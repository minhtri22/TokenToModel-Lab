#!/usr/bin/env python3
"""TTM x SIX G1: pre-execution signed boundary verifier, *not* production admission.

Pure CPU cryptographic checks for independent owner/writer/witness signatures.
This file does NOT provide a trusted launcher, an external witness, a broker,
OS privilege separation, a GPU process, a source loader, or a science permit.
Real production requires separately managed principals, keys and witness service.

`authorize_real_science` is intentionally a non-bypassable STOP regardless of
synthetic evidence. Never replace its failure with a local JSON/boolean flag.
"""
from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timezone
import hashlib
import json
import math
from pathlib import Path
import re
from typing import Mapping, Any

from cryptography.hazmat.primitives.asymmetric.ed25519 import Ed25519PublicKey

# Provenance invariants. Never change the underlying frozen v1c experiment here.
FROZEN_V1C_HEAD = 'd5d0c5346a595557a76349f900d09be50bce289c'
MANIFEST_SHA256 = '6451be0cd09a54378eda9e815b5c89ce8ce8301ddefef556476d94e3e31e42b6'
T1_SHA256 = '9f2ebaca821bddf0a9d7ae30ccfcef34561b968b21159aa913794298235a2fa9'
V1C_BLOBS = {
    'guard': '4554a3e12911cbf0606a8be053660cad0c38f374',
    'core': 'f591bd617feb007c20023a313ebc5f429471d8b2',
    'extractor': '9bb28fe39999fba0bab5474e2644b11f7940c06a',
}
# UNPROVISIONED. Keys/private credentials must be created and controlled outside
# the repository/worker and must not be committed as test fixtures.
OWNER_PUB_SHA256_PIN = None
WRITER_PUB_SHA256_PIN = None
WITNESS_PUB_SHA256_PIN = None
PRODUCTION_LAUNCHER_QUALIFIED = False
SCIENCE_LOCK = 'HOLD'
_HEX40 = re.compile(r'^[0-9a-f]{40}$')
_HEX64 = re.compile(r'^[0-9a-f]{64}$')
_RUN = re.compile(r'^[A-Za-z0-9_-]{8,80}$')
_NONCE = re.compile(r'^[0-9a-f]{32,64}$')

class BoundaryStop(RuntimeError):
    """A *sanitized* terminal failure. No paths, keys or private data in error."""


def stop(reason: str):
    raise BoundaryStop('STOP_G1_' + reason)


def need(ok: bool, reason: str):
    if not ok:
        stop(reason)


def canonical(obj: Mapping[str, Any]) -> bytes:
    need(type(obj) is dict, 'SIGNED_RECORD_TYPE')
    try:
        return json.dumps(obj, sort_keys=True, ensure_ascii=True,
                          separators=(',', ':'), allow_nan=False).encode('ascii')
    except (TypeError, ValueError, OverflowError):
        stop('SIGNED_RECORD_CANONICAL')


def digest(data: bytes) -> str:
    need(type(data) is bytes, 'DIGEST_INPUT_TYPE')
    return hashlib.sha256(data).hexdigest()


def sha64(value: object, name: str):
    need(type(value) is str and _HEX64.fullmatch(value) is not None,
         'SHA_FORMAT_' + name)
    return value


def utc_seconds(now=None):
    if now is None:
        now = datetime.now(timezone.utc).timestamp()
    need(type(now) in (int, float) and math.isfinite(now) and now >= 0,
         'CLOCK_INVALID')
    return now


def verify_envelope(envelope: Mapping, trusted_pubkey_sha256: str):
    """One detached Ed25519 record against an EXTERNALLY pinned public key.

    Passing a synthetic test pin here establishes only mathematical signature
    verification; it never establishes independent owner, service or hardware.
    """
    sha64(trusted_pubkey_sha256, 'AUTHORITY_PIN')
    need(type(envelope) is dict and set(envelope) ==
         {'payload', 'public_key_hex', 'signature_hex'}, 'ENVELOPE_FIELDS')
    try:
        key = bytes.fromhex(envelope['public_key_hex'])
        sig = bytes.fromhex(envelope['signature_hex'])
    except (KeyError, ValueError, TypeError):
        stop('ENVELOPE_DECODE')
    need(len(key) == 32 and len(sig) == 64, 'KEY_SIGNATURE_SIZE')
    need(digest(key) == trusted_pubkey_sha256, 'SIGNER_NOT_TRUSTED')
    payload = envelope['payload']
    raw = canonical(payload)
    try:
        Ed25519PublicKey.from_public_bytes(key).verify(sig, raw)
    except Exception:
        stop('SIGNATURE_INVALID')
    return payload


def verify_distinct_anchor_pins(owner: str, writer: str, witness: str):
    pins = [sha64(p, 'ANCHOR') for p in (owner, writer, witness)]
    need(len(set(pins)) == 3, 'TRUST_ANCHORS_NOT_DISTINCT')
    return True  # Key distinction != OS principal/admin/rollback distinction.


def verify_owner_admission(envelope, *, externally_pinned_owner_sha256,
                           run_id, workspace, now=None):
    """Validate owner admission syntax without issuing permission to launch.

    The future trusted launcher MUST independently pin its own commit/runtime,
    verify rights and separate signer identity, and use an OS restricted token.
    This source never claims these external prerequisites exist.
    """
    p = verify_envelope(envelope, externally_pinned_owner_sha256)
    need(type(p) is dict, 'OWNER_PAYLOAD_TYPE')
    required = {
        'schema': 'ttm.six.g1.owner_admission.v1e_candidate',
        'decision': 'QUALIFY_G1_PREEXECUTION_ONLY',
        'reviewed_v1c_head': FROZEN_V1C_HEAD,
        'reviewed_v1c_blobs': V1C_BLOBS,
        'manifest_sha256': MANIFEST_SHA256,
        't1_sha256': T1_SHA256,
        'run_id': run_id,
        'workspace': workspace,
        'phase': 'PREEXECUTION_ONLY',
        'data_rights': 'T1_TRAIN_METADATA_ONLY_NO_PRIVATE_TEST',
        'allow_real_science': False,
        'allow_private_test': False,
        'allow_teacher_download': False,
    }
    for k, v in required.items():
        need(k in p and type(p[k]) is type(v) and p[k] == v,
             'OWNER_FIELD_' + k.upper())
    need(set(p) == set(required) | {'owner_id','reviewer_id','author_id',
          'issued_utc','expires_utc','launcher_commit_sha','method_amendment_sha256'},
         'OWNER_SCOPE_KEYSET')
    need(type(run_id) is str and _RUN.fullmatch(run_id), 'RUN_ID')
    need(type(workspace) is str and len(workspace) <= 1024 and workspace,
         'WORKSPACE_INVALID')
    need(type(p['owner_id']) is str and p['owner_id'] and
         type(p['reviewer_id']) is str and p['reviewer_id'] and
         type(p['author_id']) is str and p['author_id'], 'OWNER_IDENTITIES')
    need(len({p['owner_id'],p['reviewer_id'],p['author_id']}) == 3,
         'OWNER_REVIEWER_AUTHOR_NOT_DISTINCT')
    need(type(p['launcher_commit_sha']) is str and
         _HEX40.fullmatch(p['launcher_commit_sha']), 'LAUNCHER_PIN')
    sha64(p['method_amendment_sha256'], 'METHOD_AMENDMENT')
    now = utc_seconds(now)
    need(type(p['issued_utc']) is int and type(p['expires_utc']) is int and
         p['issued_utc'] <= now < p['expires_utc'] and
         0 < p['expires_utc']-p['issued_utc'] <= 3600,
         'OWNER_EXPIRY')
    return {'synthetic_contract_verified': True, 'science_authorized': False,
            'test_opened': False, 'run_id': run_id}


def verify_signed_writer_receipt(envelope, *, writer_pubkey_pin, run_id,
                                 stage, source_bytes, ids_sha256, expected_seq,
                                 expected_prior_ack):
    """Binds the *same supplied bytes* to independently signed pack provenance.

    Caller must acquire writer-produced receipt via its trusted control channel,
    not from the same untrusted worker directory. Never returns real admission.
    """
    p = verify_envelope(envelope, writer_pubkey_pin)
    need(type(p) is dict, 'WRITER_PAYLOAD_TYPE')
    required = {
        'schema': 'ttm.six.g1.external_writer_pack.v1e_candidate',
        'run_id': run_id, 'stage': stage,
        'manifest_sha256': MANIFEST_SHA256,
        'pack_sha256': digest(source_bytes),
        'ids_sha256': sha64(ids_sha256, 'IDS'),
        'witness_prev_ack': sha64(expected_prior_ack, 'PREV_ACK'),
        'seq': expected_seq,
        'status': 'PACK_COMMITTED',
    }
    need(set(p) == set(required), 'WRITER_RECEIPT_KEYS')
    need(type(run_id) is str and _RUN.fullmatch(run_id), 'WRITER_RUN')
    need(stage in ('TRAIN', 'DEV', 'TEST'), 'WRITER_STAGE')
    need(type(expected_seq) is int and expected_seq >= 0, 'WRITER_SEQ')
    for k, v in required.items():
        need(k in p and type(p[k]) is type(v) and p[k] == v,
             'WRITER_FIELD_' + k.upper())
    return {'receipt_crypto_valid': True, 'pack_sha256': digest(source_bytes),
            'stage': stage, 'production_provenance_qualified': False}


def verify_signed_witness_ack(envelope, *, witness_pubkey_pin, run_id,
                              event_sha256, previous_ack_sha256,
                              expected_seq, challenge_nonce, now=None):
    """Verifies fresh signed ACK. No HTTP service or durable backend provided.

    A production client MUST query independent external latest state on EVERY
    attempt, not accept only locally cached signed ACKs. If controller and
    witness can be rolled back together, signature verification is insufficient.
    """
    p = verify_envelope(envelope, witness_pubkey_pin)
    need(type(p) is dict, 'WITNESS_PAYLOAD_TYPE')
    need(type(run_id) is str and _RUN.fullmatch(run_id), 'WITNESS_RUN_ID')
    need(type(challenge_nonce) is str and _NONCE.fullmatch(challenge_nonce),
         'WITNESS_NONCE_FORMAT')
    need(type(expected_seq) is int and expected_seq >= 0, 'WITNESS_SEQ')
    expected = {
        'schema': 'ttm.six.g1.external_monotonic_ack.v1e_candidate',
        'run_id': run_id, 'event_sha256': sha64(event_sha256, 'EVENT'),
        'prev_ack_sha256': sha64(previous_ack_sha256, 'PREVIOUS'),
        'seq': expected_seq, 'challenge_nonce': challenge_nonce,
        'status': 'DURABLE_ACK',
    }
    need(set(p) == set(expected) | {'issued_utc','expires_utc'},
         'WITNESS_ACK_KEYS')
    for k, v in expected.items():
        need(k in p and type(p[k]) is type(v) and p[k] == v,
             'WITNESS_FIELD_' + k.upper())
    now = utc_seconds(now)
    need(type(p['issued_utc']) is int and type(p['expires_utc']) is int and
         p['issued_utc'] <= now < p['expires_utc'] and
         0 < p['expires_utc'] - p['issued_utc'] <= 60,
         'WITNESS_ACK_STALE')
    return {'signature_fresh': True, 'ack_sha256': digest(canonical(p)),
            'external_monotonicity_proven': False,
            'science_authorized': False}


def authorize_real_science(*args, **kwargs):
    """Non-bypassable until a distinct owner-reviewed production release."""
    stop('PRODUCTION_RELEASE_NOT_IMPLEMENTED_AND_OWNER_NOT_AUTHORIZED')


def status():
    return {
        'schema': 'ttm.six.g1.production_boundary_candidate.v1e',
        'owner_pin_provisioned': OWNER_PUB_SHA256_PIN is not None,
        'writer_pin_provisioned': WRITER_PUB_SHA256_PIN is not None,
        'witness_pin_provisioned': WITNESS_PUB_SHA256_PIN is not None,
        'production_launcher_qualified': PRODUCTION_LAUNCHER_QUALIFIED,
        'private_test_opened': False,
        'science_executed': False,
        'science_lock': SCIENCE_LOCK,
    }


if __name__ == '__main__':
    print(json.dumps(status(), sort_keys=True))
