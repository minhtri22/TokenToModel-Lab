"""Fail-closed release admission: authorizations are NOT local JSON booleans.

Trust anchors must be hard-coded from independently reviewed external public
keys at a separately reviewed exact Git blob. No trusted key is supplied now:
this candidate therefore cannot authorize checkpoint reading or CPU execution.
The API has no ``mock`` bypass in a production call.
"""
from __future__ import annotations
import base64
import hashlib
import json
from pathlib import Path

QUESTION_ID = 'TTM-SM4M-DIAG-Q001'
Q1_MAIN = 'f7a0a5874e8fd895c8ea8d17ceff393a4d4917a3'
CHECKPOINT_SHA = 'cb985751795c8328ad65acf7ca4c1033ce35182c1bfbdb8c38550de629cb271b'
OWNER_DECISION = 'GO_SMALL4M_DIAG_SINGLE_SCOPED_IMPLEMENT_AND_RUN_CONDITIONAL'
# Deliberately NOT configured. No release until separately authenticated keys
# are reviewed and hard-pinned to this file in a later exact-HEAD source review.
TRUSTED_ED25519_PUBLIC_KEYS: dict[str, str] = {}
REQUIRED_SIGNER_ROLES = ('owner', 'distinct_reviewer', 'rights_custodian')


class AdmissionHold(RuntimeError):
    pass


def canonical_bytes(obj: dict) -> bytes:
    return json.dumps(obj, sort_keys=True, ensure_ascii=False,
                      separators=(',', ':')).encode('utf-8')


def _hold(message: str):
    raise AdmissionHold('HOLD_' + message)


def _hex(value, length=64):
    return isinstance(value, str) and len(value) == length and all(c in '0123456789abcdef' for c in value)


def authenticate_release(permit_path: Path, *, phase: str, runner_sha256: str,
                         tokenizer_sha256: str, underlying_sha256: str,
                         frozen_fixture_sha256: str | None = None) -> dict:
    """Verify 3 distinct signatures over the same complete immutable payload.

    Keys are not taken from permit or an arbitrary local path. A well-formed
    permit with all GO strings, but no externally pinned keys, ALWAYS fails.
    """
    if not TRUSTED_ED25519_PUBLIC_KEYS or any(
            role not in TRUSTED_ED25519_PUBLIC_KEYS for role in REQUIRED_SIGNER_ROLES):
        _hold('AUTHENTICATED_TRUST_ANCHORS_UNAVAILABLE')
    if not permit_path.is_file():
        _hold('SIGNED_PERMIT_MISSING')
    try:
        permit = json.loads(permit_path.read_text(encoding='utf-8'))
    except (ValueError, UnicodeError, OSError):
        _hold('SIGNED_PERMIT_INVALID')
    if not isinstance(permit, dict) or set(permit) != {'payload', 'signatures'}:
        _hold('SIGNED_PERMIT_SCHEMA')
    payload, signatures = permit['payload'], permit['signatures']
    if not isinstance(payload, dict) or not isinstance(signatures, dict):
        _hold('SIGNED_PERMIT_SCHEMA')
    required = {
        'question_id': QUESTION_ID,
        'question_gate_main_sha': Q1_MAIN,
        'owner_decision': OWNER_DECISION,
        'phase': phase,
        'runner_sha256': runner_sha256,
        'checkpoint_sha256': CHECKPOINT_SHA,
        'token_inventory_sha256': tokenizer_sha256,
        'underlying_inventory_sha256': underlying_sha256,
        'independent_source_qa': 'PASS_DIAG_Q001_REMEDIATED_SOURCE_SCOPED',
        'independent_negative_qa': 'PASS_SCOPED_NATIVE',
        'ad00_ad01c_e6_rights': 'ATTESTED_EXACT_SCOPE',
        'owner_one_shot_execution': 'GO_SINGLE_ONE_SHOT_CPU',
    }
    if any(payload.get(k) != v for k, v in required.items()):
        _hold('SIGNED_PERMIT_PAYLOAD_MISMATCH')
    if not all(_hex(payload.get(k)) for k in ('runner_sha256', 'token_inventory_sha256',
                                               'underlying_inventory_sha256')):
        _hold('SIGNED_PERMIT_SHA_FORMAT')
    if phase == 'run':
        if not _hex(payload.get('one_shot_nonce')):
            _hold('SIGNED_ONESHOT_NONCE_REQUIRED')
        if not _hex(frozen_fixture_sha256) or payload.get('frozen_fixture_sha256') != frozen_fixture_sha256:
            _hold('SIGNED_FIXTURE_PIN_MISMATCH')
    elif phase != 'fixture-freeze':
        _hold('PERMIT_PHASE_UNKNOWN')
    if set(signatures) != set(REQUIRED_SIGNER_ROLES):
        _hold('SIGNER_ROLES_MISSING_OR_EXTRA')
    if len(set(TRUSTED_ED25519_PUBLIC_KEYS[r] for r in REQUIRED_SIGNER_ROLES)) != len(REQUIRED_SIGNER_ROLES):
        _hold('REUSED_SIGNER_KEY')
    try:
        from cryptography.hazmat.primitives.asymmetric.ed25519 import Ed25519PublicKey
        from cryptography.exceptions import InvalidSignature
    except ImportError:
        _hold('CRYPTOGRAPHIC_VALIDATOR_MISSING')
    encoded = canonical_bytes(payload)
    for role in REQUIRED_SIGNER_ROLES:
        sig = signatures[role]
        try:
            if not isinstance(sig, str):
                _hold('SIGNATURE_SCHEMA_' + role)
            pub = base64.b64decode(TRUSTED_ED25519_PUBLIC_KEYS[role], validate=True)
            signed = base64.b64decode(sig, validate=True)
            if len(pub) != 32 or len(signed) != 64:
                _hold('SIGNATURE_BYTES_' + role)
            Ed25519PublicKey.from_public_bytes(pub).verify(signed, encoded)
        except (ValueError, InvalidSignature, UnicodeEncodeError):
            _hold('SIGNATURE_INVALID_' + role)
    return payload
