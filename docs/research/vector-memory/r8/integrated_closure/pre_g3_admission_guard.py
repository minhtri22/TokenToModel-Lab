"""R8-D pre-G3 guarded dispatcher candidate; fixture-only until independently admitted.

No case generator or GitHub attestation verifier is registered in this module.
A caller must not treat a forged verification result as a production attestation.
Exact frozen scientific source remains untouched.
"""
from __future__ import annotations

from contextlib import closing
from dataclasses import dataclass
from datetime import datetime, timezone
import hashlib
import json
import re
import sqlite3
from pathlib import Path
from typing import Callable, Protocol, TypeVar

SCHEMA = "TTM_VM_R8_GPRE_HMAC_V2"
ALGORITHM = "R8_GPRE_CANONICAL_JSON_COMPONENT_RANKING_V2"
SOURCE_COMMIT = "84d9d5c95e9962ccfe294852570e261b145fe403"
HEX64 = re.compile(r"[0-9a-f]{64}\Z")
SESSION = re.compile(r"[A-Za-z0-9_-]{12,128}\Z")
T = TypeVar("T")


class AdmissionDenied(RuntimeError):
    """No downstream generator may be invoked after this exception."""


def _digest(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def _reject_duplicate_keys(pairs: list[tuple[str, object]]) -> dict:
    result: dict = {}
    for key, value in pairs:
        if key in result:
            raise ValueError("DUPLICATE_JSON_FIELD")
        result[key] = value
    return result


def _utc(value: str) -> datetime:
    if not isinstance(value, str):
        raise AdmissionDenied("TIMESTAMP_INVALID")
    try:
        parsed = datetime.fromisoformat(value.replace("Z", "+00:00"))
    except ValueError as exc:
        raise AdmissionDenied("TIMESTAMP_INVALID") from exc
    if parsed.tzinfo is None or parsed.utcoffset() != timezone.utc.utcoffset(parsed):
        raise AdmissionDenied("TIMESTAMP_NOT_UTC")
    return parsed.astimezone(timezone.utc)


def _hex64(value: object) -> bool:
    return isinstance(value, str) and HEX64.fullmatch(value) is not None


@dataclass(frozen=True)
class PrivateEnvelope:
    """Private exact bytes and nonce remain within protected custody."""

    exact_bytes: bytes
    nonce: bytes
    blueprint_bytes: bytes
    lock_bytes: bytes

    def parse_and_validate(self) -> dict:
        if not isinstance(self.nonce, bytes) or len(self.nonce) != 16:
            raise AdmissionDenied("NONCE_LENGTH_INVALID")
        if any(not isinstance(x, bytes) for x in (self.exact_bytes, self.blueprint_bytes, self.lock_bytes)):
            raise AdmissionDenied("PRIVATE_BYTES_INVALID")
        try:
            value = json.loads(self.exact_bytes.decode("utf-8", "strict"),
                               object_pairs_hook=_reject_duplicate_keys,
                               parse_constant=lambda _: (_ for _ in ()).throw(ValueError("NONFINITE_JSON")))
            if not isinstance(value, dict):
                raise ValueError("NON_OBJECT_ENVELOPE")
            canonical = json.dumps(value, ensure_ascii=False, sort_keys=True,
                                   separators=(",", ":"), allow_nan=False).encode("utf-8")
        except (UnicodeError, ValueError, OverflowError, TypeError) as exc:
            raise AdmissionDenied("PRIVATE_ENVELOPE_INVALID") from exc
        if canonical != self.exact_bytes:
            raise AdmissionDenied("NONCANONICAL_ENVELOPE")
        required = {"schema", "algorithm_id", "session_id", "source_commit",
                    "source_manifest_sha256", "runtime_manifest_sha256",
                    "blueprint_sha256", "lock_sha256"}
        if set(value) != required:
            raise AdmissionDenied("ENVELOPE_FIELDS_INVALID")
        if value["schema"] != SCHEMA or value["algorithm_id"] != ALGORITHM:
            raise AdmissionDenied("ALGORITHM_SCHEMA_MISMATCH")
        if not isinstance(value["session_id"], str) or not SESSION.fullmatch(value["session_id"]):
            raise AdmissionDenied("SESSION_ID_INVALID")
        if not all(_hex64(value[x]) for x in required if x.endswith("sha256")):
            raise AdmissionDenied("MANIFEST_SHA_INVALID")
        if value["blueprint_sha256"] != _digest(self.blueprint_bytes):
            raise AdmissionDenied("BLUEPRINT_DIGEST_MISMATCH")
        if value["lock_sha256"] != _digest(self.lock_bytes):
            raise AdmissionDenied("LOCK_DIGEST_MISMATCH")
        if value["source_commit"] != SOURCE_COMMIT:
            raise AdmissionDenied("SOURCE_COMMIT_PIN_MISMATCH")
        try:
            lock = json.loads(self.lock_bytes.decode("utf-8", "strict"),
                              object_pairs_hook=_reject_duplicate_keys)
        except (UnicodeError, ValueError, TypeError) as exc:
            raise AdmissionDenied("PRIVATE_LOCK_INVALID") from exc
        if (not isinstance(lock, dict) or lock.get("algorithm_id") != ALGORITHM or
            lock.get("lock_schema") != SCHEMA):
            raise AdmissionDenied("PRIVATE_LOCK_ALGORITHM_MISMATCH")
        if not _hex64(lock.get("preassignment_hmac")) or not _hex64(lock.get("blueprint_hmac")):
            raise AdmissionDenied("PRIVATE_LOCK_HMAC_MISSING")
        return value

    @property
    def public_digest(self) -> str:
        return _digest(self.nonce + self.exact_bytes)


@dataclass(frozen=True)
class AnchorProof:
    """Only a trusted verifier may claim these attestations; not raw API data."""

    public_digest: str
    source_commit: str
    source_manifest_sha256: str
    runtime_manifest_sha256: str
    session_id: str
    schema: str
    algorithm_id: str
    release_tag: str
    release_asset_sha256: str
    signed_timestamp_utc: str
    published_timestamp_utc: str
    verified_at_utc: str
    immutable: bool
    signature_verified: bool
    verification_bundle_sha256: str


@dataclass(frozen=True)
class AcceptedReceipt:
    """Fixture proof of an independently accepted, source-bound admission."""

    session_id: str
    public_digest: str
    release_asset_sha256: str
    source_commit: str
    acceptance_timestamp_utc: str
    amendment_review_commit: str
    accepted: bool


class TrustedReceiptVerifier(Protocol):
    def verify_accepted(self, *, session_id: str, public_digest: str) -> AcceptedReceipt:
        """Must verify independent amendment acceptance and G_pre receipt."""


class TrustedAnchorVerifier(Protocol):
    def verify(self, *, release_tag: str, public_digest: str) -> AnchorProof:
        """Must independently check remote release bytes, signature and timestamp."""


class PreG3AdmissionGuard:
    """Durable atomic one-shot fixture admission, never a production permit.

    The production verifier/retention amendment and real G3 generator have NOT
    been accepted. production=True always denies until a separate reviewed
    integration supplies a verified production trust boundary.
    """

    def __init__(self, ledger_path: Path, verifier: TrustedAnchorVerifier,
                 receipt_verifier: TrustedReceiptVerifier, *,
                 fixture_mode: bool = False):
        self._path = Path(ledger_path)
        self._verifier = verifier
        self._receipt_verifier = receipt_verifier
        self._fixture_mode = fixture_mode

    def dispatch(self, envelope: PrivateEnvelope, release_tag: str,
                 generator: Callable[[], T]) -> T:
        if self._fixture_mode is not True:
            raise AdmissionDenied("PRODUCTION_VERIFIER_AND_AMENDMENT_NOT_ADMITTED")
        if not callable(generator):
            raise AdmissionDenied("GENERATOR_NOT_CALLABLE")
        value = envelope.parse_and_validate()
        if not isinstance(release_tag, str) or not re.fullmatch(r"[A-Za-z0-9_.-]{8,150}", release_tag):
            raise AdmissionDenied("RELEASE_TAG_INVALID")
        proof = self._verifier.verify(release_tag=release_tag,
                                      public_digest=envelope.public_digest)
        if not isinstance(proof, AnchorProof):
            raise AdmissionDenied("TRUSTED_PROOF_ABSENT")
        expected = {
            "public_digest": envelope.public_digest,
            "source_commit": value["source_commit"],
            "source_manifest_sha256": value["source_manifest_sha256"],
            "runtime_manifest_sha256": value["runtime_manifest_sha256"],
            "session_id": value["session_id"],
            "schema": SCHEMA, "algorithm_id": ALGORITHM,
            "release_tag": release_tag,
        }
        if any(getattr(proof, k) != v for k, v in expected.items()):
            raise AdmissionDenied("REMOTE_PROOF_BINDING_MISMATCH")
        if proof.immutable is not True or proof.signature_verified is not True:
            raise AdmissionDenied("REMOTE_ATTESTATION_NOT_VERIFIED")
        if not _hex64(proof.release_asset_sha256) or not _hex64(proof.verification_bundle_sha256):
            raise AdmissionDenied("REMOTE_ASSET_OR_BUNDLE_HASH_INVALID")
        published = _utc(proof.published_timestamp_utc)
        signed = _utc(proof.signed_timestamp_utc)
        verified = _utc(proof.verified_at_utc)
        now = datetime.now(timezone.utc)
        if not published < signed < verified <= now:
            raise AdmissionDenied("PRE_G3_TIMESTAMP_ORDER_INVALID")
        receipt = self._receipt_verifier.verify_accepted(
            session_id=value["session_id"], public_digest=envelope.public_digest)
        if not isinstance(receipt, AcceptedReceipt) or receipt.accepted is not True:
            raise AdmissionDenied("INDEPENDENT_ADMISSION_RECEIPT_MISSING")
        if (receipt.session_id != value["session_id"] or
            receipt.public_digest != envelope.public_digest or
            receipt.source_commit != value["source_commit"] or
            receipt.release_asset_sha256 != proof.release_asset_sha256 or
            not isinstance(receipt.amendment_review_commit, str) or
            not re.fullmatch(r"[0-9a-f]{40}", receipt.amendment_review_commit) or
            receipt.amendment_review_commit == "0" * 40):
            raise AdmissionDenied("ACCEPTED_RECEIPT_BINDING_MISMATCH")
        accepted_at = _utc(receipt.acceptance_timestamp_utc)
        if not verified < accepted_at <= now:
            raise AdmissionDenied("PRE_G3_ACCEPTANCE_ORDER_INVALID")
        # Re-check the same exact proof after independent acceptance; stale or
        # revoked fixture anchors must fail before any callback is invoked.
        refreshed = self._verifier.verify(release_tag=release_tag,
                                         public_digest=envelope.public_digest)
        if not isinstance(refreshed, AnchorProof) or refreshed != proof:
            raise AdmissionDenied("REMOTE_ANCHOR_CHANGED_OR_UNAVAILABLE")
        if not self._path.parent.is_dir() or self._path.is_symlink():
            raise AdmissionDenied("PRIVATE_LEDGER_LOCATION_INVALID")
        if self._path.exists() and self._path.stat().st_nlink != 1:
            raise AdmissionDenied("PRIVATE_LEDGER_MULTIPLE_HARDLINKS")
        # UNIQUE constraints + BEGIN IMMEDIATE serialize cross-process admissions.
        # A transaction commits before dispatch; even a failed callback consumes it.
        try:
            with closing(sqlite3.connect(self._path, timeout=10, isolation_level=None)) as db:
                db.execute("PRAGMA synchronous=FULL")
                db.execute("PRAGMA journal_mode=DELETE")
                db.execute("BEGIN IMMEDIATE")
                expected_ddl = ("CREATE TABLE consumed (session_id TEXT PRIMARY KEY, "
                                "commitment_digest TEXT NOT NULL UNIQUE, "
                                "consumed_utc TEXT NOT NULL)")
                db.execute(expected_ddl.replace("CREATE TABLE consumed", "CREATE TABLE IF NOT EXISTS consumed"))
                installed = db.execute("SELECT sql FROM sqlite_master WHERE type='table' "
                                       "AND name='consumed'").fetchone()
                def normalize_ddl(value):
                    return " ".join(value.replace("IF NOT EXISTS", "").split()).lower()
                if not installed or normalize_ddl(installed[0]) != normalize_ddl(expected_ddl):
                    raise AdmissionDenied("PRIVATE_LEDGER_SCHEMA_UNTRUSTED")
                if db.execute("PRAGMA integrity_check").fetchone()[0] != 'ok':
                    raise AdmissionDenied("PRIVATE_LEDGER_INTEGRITY_FAILED")
                db.execute("INSERT INTO consumed VALUES(?,?,?)", (
                    value["session_id"], envelope.public_digest,
                    datetime.now(timezone.utc).isoformat()))
                db.execute("COMMIT")
        except sqlite3.IntegrityError as exc:
            raise AdmissionDenied("G3_ONE_SHOT_REPLAY_REJECTED") from exc
        except sqlite3.Error as exc:
            raise AdmissionDenied("G3_LEDGER_NOT_DURABLE") from exc
        return generator()
