"""Evidence manifest *schema preview*; cannot issue a PASS receipt in I0A-S."""
from __future__ import annotations
import hashlib
import json


class EvidenceNotReady(ValueError):
    pass


def canonical_design_json(value: dict[str, object]) -> bytes:
    """ASCII-key/no-float limited fixture serializer; NOT full RFC8785 JCS."""
    if not isinstance(value, dict):
        raise EvidenceNotReady("OBJECT_REQUIRED")
    # NOTE: This restricted serializer is insufficient for production JCS.
    if any(not isinstance(key, str) or not key.isascii() for key in value):
        raise EvidenceNotReady("ASCII_KEYS_ONLY_IN_DESIGN")
    return json.dumps(value, ensure_ascii=False, sort_keys=True, separators=(",", ":"),
                      allow_nan=False).encode("utf-8")


def design_hash(value: dict[str, object]) -> str:
    return hashlib.sha256(canonical_design_json(value)).hexdigest()


def issue_runtime_receipt(*_args: object, **_kwargs: object) -> None:
    raise EvidenceNotReady("QA0_RECEIPT_ISSUANCE_NOT_IMPLEMENTED")
