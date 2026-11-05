"""Independent P01 F0 contracts reader; does NOT import tokenizer or generator."""
from __future__ import annotations
import hashlib
import struct

EXPECTED_M01_SHA256 = "11c72190c6f3b757d260c426c357a4de8ff36313495f2299da81638386289e8d"
EXPECTED_M01_RULES = ((97, 98, 256), (256, 256, 257))
MAGIC = b"TTM_BPE_V1\x00"


class IndependentCheckError(ValueError):
    pass


def inspect_merges_blob(blob: bytes) -> dict[str, object]:
    if not isinstance(blob, bytes) or len(blob) < 23 or blob[:11] != MAGIC:
        raise IndependentCheckError("MAGIC_OR_HEADER")
    target, actual, count = struct.unpack_from("<III", blob, 11)
    if target < 256 or count > target - 256 or actual != 256 + count:
        raise IndependentCheckError("COUNT")
    if len(blob) != 23 + count * 12:
        raise IndependentCheckError("TRAILING_OR_TRUNCATED")
    seen: set[tuple[int, int]] = set()
    entries = []
    for i in range(count):
        a, b, new_id = struct.unpack_from("<III", blob, 23 + i * 12)
        if new_id != 256 + i or a >= new_id or b >= new_id or (a, b) in seen:
            raise IndependentCheckError("INVALID_RULE")
        seen.add((a, b))
        entries.append((a, b, new_id))
    return {"target": target, "actual": actual, "merges": tuple(entries),
            "sha256": hashlib.sha256(blob).hexdigest()}


def inspect_m01_design_bytes(blob: bytes) -> dict[str, object]:
    result = inspect_merges_blob(blob)
    if (len(blob) != 47 or result["target"] != 258 or result["actual"] != 258
            or result["merges"] != EXPECTED_M01_RULES
            or result["sha256"] != EXPECTED_M01_SHA256):
        raise IndependentCheckError("M01_GOLDEN_MISMATCH")
    return result


def validate_receipt_admission(manifest: dict[str, object]) -> None:
    """Fail closed: F0 golden manifests must never be accepted as runtime receipts."""
    if not isinstance(manifest, dict) or manifest.get("operation_id") == "DESIGN_ONLY_NO_RUN":
        raise IndependentCheckError("DESIGN_IS_NOT_EXECUTION_EVIDENCE")
    if manifest.get("final_status") == "PASS":
        raise IndependentCheckError("DYNAMIC_QA_NOT_AUTHORIZED_IN_I0A_S")
    raise IndependentCheckError("RUNTIME_RECEIPT_VALIDATION_NOT_IMPLEMENTED")
