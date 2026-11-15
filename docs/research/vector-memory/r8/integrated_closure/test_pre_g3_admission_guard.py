"""Source-only G2 negative QA. Synthetic fixtures; no real R8 key/cases/G3."""
from concurrent.futures import ThreadPoolExecutor
from dataclasses import replace
from datetime import datetime, timedelta, timezone
import hashlib
import json
from pathlib import Path
import multiprocessing
import tempfile
import threading
import unittest

from pre_g3_admission_guard import (
    ALGORITHM, SCHEMA, AcceptedReceipt, AdmissionDenied, AnchorProof,
    PreG3AdmissionGuard, PrivateEnvelope,
)

SOURCE_COMMIT = "84d9d5c95e9962ccfe294852570e261b145fe403"
REVIEW_COMMIT = "a" * 40  # synthetic fixture, NOT an approved reviewer
TAG = "ttm-r8-fixture-sentinel-20261115"


def sha(v):
    return hashlib.sha256(v).hexdigest()


def canonical(x):
    return json.dumps(x, sort_keys=True, ensure_ascii=False,
                      separators=(",", ":"), allow_nan=False).encode()


class Proofs:
    def __init__(self, anchor, receipt):
        self.anchor = anchor
        self.receipt = receipt

    def verify(self, *, release_tag, public_digest):
        return self.anchor

    def verify_accepted(self, *, session_id, public_digest):
        return self.receipt


def cross_process_worker(ledger, envelope, anchor, receipt, start, output):
    proofs = Proofs(anchor, receipt)
    guard = PreG3AdmissionGuard(Path(ledger), proofs, proofs, fixture_mode=True)
    start.wait(10)
    try:
        result = guard.dispatch(envelope, TAG, lambda: "CROSS_PROCESS_DISPATCHED")
    except AdmissionDenied as exc:
        result = str(exc)
    output.put(result)


class AdmissionQA(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.ledger = Path(self.tmp.name) / "one_shot.sqlite3"
        self.blueprint = b'{"fixture_blueprints":"no-real-data"}'
        self.lock = canonical({"algorithm_id": ALGORITHM,
                               "lock_schema": SCHEMA, "preassignment_hmac": "a" * 64,
                               "blueprint_hmac": "b" * 64})
        self.obj = {
            "schema": SCHEMA, "algorithm_id": ALGORITHM,
            "session_id": "fixture-session-000001",
            "source_commit": SOURCE_COMMIT,
            "source_manifest_sha256": "c" * 64,
            "runtime_manifest_sha256": "d" * 64,
            "blueprint_sha256": sha(self.blueprint),
            "lock_sha256": sha(self.lock),
        }
        self.envelope = self.make_envelope()
        now = datetime.now(timezone.utc)
        def at(seconds):
            return (now + timedelta(seconds=seconds)).isoformat()
        self.anchor = AnchorProof(
            public_digest=self.envelope.public_digest,
            source_commit=SOURCE_COMMIT,
            source_manifest_sha256="c" * 64,
            runtime_manifest_sha256="d" * 64,
            session_id=self.obj["session_id"],
            schema=SCHEMA, algorithm_id=ALGORITHM, release_tag=TAG,
            release_asset_sha256="e" * 64,
            signed_timestamp_utc=at(-50),
            published_timestamp_utc=at(-60),
            verified_at_utc=at(-30),
            immutable=True, signature_verified=True,
            verification_bundle_sha256="f" * 64,
        )
        self.receipt = AcceptedReceipt(
            session_id=self.obj["session_id"],
            public_digest=self.envelope.public_digest,
            release_asset_sha256="e" * 64,
            source_commit=SOURCE_COMMIT,
            acceptance_timestamp_utc=at(-20),
            amendment_review_commit=REVIEW_COMMIT,
            accepted=True,
        )
        self.proofs = Proofs(self.anchor, self.receipt)
        self.guard = PreG3AdmissionGuard(
            self.ledger, self.proofs, self.proofs, fixture_mode=True)
        self.called = 0

    def make_envelope(self, **changes):
        payload = dict(self.obj, **changes)
        return PrivateEnvelope(canonical(payload), b"\x17" * 16,
                               self.blueprint, self.lock)

    def generator(self):
        self.called += 1
        return "FIXTURE_DISPATCHED"

    def deny(self, reason, envelope=None, tag=TAG, guard=None):
        with self.assertRaises(AdmissionDenied) as c:
            (guard or self.guard).dispatch(envelope or self.envelope, tag, self.generator)
        self.assertEqual(str(c.exception), reason)
        self.assertEqual(self.called, 0, "Generator must NOT run after denial")

    def test_01_valid_fixture_dispatch_once(self):
        self.assertEqual(self.guard.dispatch(self.envelope, TAG, self.generator),
                         "FIXTURE_DISPATCHED")
        self.assertEqual(self.called, 1)
        with self.assertRaisesRegex(AdmissionDenied, "ONE_SHOT_REPLAY"):
            self.guard.dispatch(self.envelope, TAG, self.generator)
        self.assertEqual(self.called, 1)

    def test_02_production_default_denies(self):
        guard = PreG3AdmissionGuard(self.ledger, self.proofs, self.proofs)
        self.deny("PRODUCTION_VERIFIER_AND_AMENDMENT_NOT_ADMITTED", guard=guard)

    def test_03_anchor_missing_denies(self):
        self.proofs.anchor = None
        self.deny("TRUSTED_PROOF_ABSENT")

    def test_04_unsigned_denies(self):
        self.proofs.anchor = replace(self.anchor, signature_verified=False)
        self.deny("REMOTE_ATTESTATION_NOT_VERIFIED")

    def test_05_mutable_release_denies(self):
        self.proofs.anchor = replace(self.anchor, immutable=False)
        self.deny("REMOTE_ATTESTATION_NOT_VERIFIED")

    def test_06_wrong_anchor_digest_denies(self):
        self.proofs.anchor = replace(self.anchor, public_digest="0" * 64)
        self.deny("REMOTE_PROOF_BINDING_MISMATCH")

    def test_07_wrong_source_or_runtime_manifest_denies(self):
        for field in ("source_commit", "source_manifest_sha256", "runtime_manifest_sha256",
                      "session_id", "schema", "algorithm_id", "release_tag"):
            with self.subTest(field=field):
                self.proofs.anchor = replace(self.anchor, **{field: "WRONG"})
                self.deny("REMOTE_PROOF_BINDING_MISMATCH")

    def test_08_bad_time_order_denies(self):
        self.proofs.anchor = replace(self.anchor, signed_timestamp_utc="2099-01-01T00:00:00Z")
        self.deny("PRE_G3_TIMESTAMP_ORDER_INVALID")

    def test_09_missing_independent_acceptance_denies(self):
        self.proofs.receipt = replace(self.receipt, accepted=False)
        self.deny("INDEPENDENT_ADMISSION_RECEIPT_MISSING")

    def test_10_receipt_tamper_denies(self):
        for field in ("session_id", "public_digest", "release_asset_sha256",
                      "source_commit", "amendment_review_commit"):
            with self.subTest(field=field):
                self.proofs.receipt = replace(self.receipt, **{field: "WRONG"})
                self.deny("ACCEPTED_RECEIPT_BINDING_MISMATCH")

    def test_11_receipt_timestamp_early_denies(self):
        self.proofs.receipt = replace(self.receipt, acceptance_timestamp_utc="2020-01-01T00:00:00Z")
        self.deny("PRE_G3_ACCEPTANCE_ORDER_INVALID")

    def test_12_tampered_private_payload_denies(self):
        self.deny("BLUEPRINT_DIGEST_MISMATCH", self.make_envelope(blueprint_sha256="0" * 64))
        self.deny("ALGORITHM_SCHEMA_MISMATCH", self.make_envelope(algorithm_id="V1"))
        self.deny("LOCK_DIGEST_MISMATCH", self.make_envelope(lock_sha256="1" * 64))

    def test_13_noncanonical_or_duplicate_json_denies(self):
        e = replace(self.envelope, exact_bytes=json.dumps(self.obj).encode())
        self.deny("NONCANONICAL_ENVELOPE", e)
        dupe = b'{"schema":"a","schema":"b"}'
        self.deny("PRIVATE_ENVELOPE_INVALID", replace(self.envelope, exact_bytes=dupe))

    def test_14_nonce_invalid_denies(self):
        self.deny("NONCE_LENGTH_INVALID", replace(self.envelope, nonce=b"short"))

    def test_15_generator_exception_is_consumed(self):
        def failure():
            raise RuntimeError("FIxTURE_ABORT")
        with self.assertRaises(RuntimeError):
            self.guard.dispatch(self.envelope, TAG, failure)
        self.deny("G3_ONE_SHOT_REPLAY_REJECTED")

    def test_16_simultaneous_calls_one_winner(self):
        barrier = threading.Barrier(8)
        successes = []
        def job(_):
            barrier.wait()
            try:
                return self.guard.dispatch(self.envelope, TAG, self.generator)
            except AdmissionDenied as e:
                return str(e)
        with ThreadPoolExecutor(max_workers=8) as pool:
            results = list(pool.map(job, range(8)))
        self.assertEqual(results.count("FIXTURE_DISPATCHED"), 1)
        self.assertEqual(results.count("G3_ONE_SHOT_REPLAY_REJECTED"), 7)
        self.assertEqual(self.called, 1)

    def test_17_missing_ledger_directory_denies(self):
        guard = PreG3AdmissionGuard(Path(self.tmp.name) / "missing" / "ledger.db",
                                    self.proofs, self.proofs, fixture_mode=True)
        self.deny("PRIVATE_LEDGER_LOCATION_INVALID", guard=guard)

    def test_18_no_receipt_type_denies(self):
        self.proofs.receipt = None
        self.deny("INDEPENDENT_ADMISSION_RECEIPT_MISSING")

    def test_19_cross_session_same_commitment_rejected(self):
        self.guard.dispatch(self.envelope, TAG, self.generator)
        self.called = 0
        # A replay via a newly constructed guard still sees durable ledger state.
        fresh = PreG3AdmissionGuard(self.ledger, self.proofs, self.proofs, fixture_mode=True)
        self.deny("G3_ONE_SHOT_REPLAY_REJECTED", guard=fresh)


    def test_20_wrong_private_source_commit_denies(self):
        self.deny("SOURCE_COMMIT_PIN_MISMATCH",
                  self.make_envelope(source_commit="e" * 40))

    def test_21_invalid_private_lock_schema_or_hmac_denies(self):
        bad_lock = canonical({"algorithm_id": ALGORITHM, "lock_schema": "V1",
                              "preassignment_hmac": "a" * 64,
                              "blueprint_hmac": "b" * 64})
        self.deny("PRIVATE_LOCK_ALGORITHM_MISMATCH",
                  replace(self.envelope, lock_bytes=bad_lock,
                          exact_bytes=canonical(dict(self.obj, lock_sha256=sha(bad_lock)))))
        bad_hmac = canonical({"algorithm_id": ALGORITHM, "lock_schema": SCHEMA,
                              "preassignment_hmac": "invalid",
                              "blueprint_hmac": "b" * 64})
        self.deny("PRIVATE_LOCK_HMAC_MISSING",
                  replace(self.envelope, lock_bytes=bad_hmac,
                          exact_bytes=canonical(dict(self.obj, lock_sha256=sha(bad_hmac)))))

    def test_22_two_spawned_processes_one_winner(self):
        ctx = multiprocessing.get_context("spawn")
        event = ctx.Event()
        queue = ctx.Queue()
        processes = [ctx.Process(target=cross_process_worker,
                     args=(str(self.ledger), self.envelope, self.anchor,
                           self.receipt, event, queue)) for _ in range(2)]
        for process in processes:
            process.start()
        event.set()
        results = [queue.get(timeout=20) for _ in processes]
        for process in processes:
            process.join(timeout=20)
            self.assertEqual(process.exitcode, 0)
        self.assertEqual(results.count("CROSS_PROCESS_DISPATCHED"), 1)
        self.assertEqual(results.count("G3_ONE_SHOT_REPLAY_REJECTED"), 1)


if __name__ == "__main__":
    unittest.main(verbosity=2)
