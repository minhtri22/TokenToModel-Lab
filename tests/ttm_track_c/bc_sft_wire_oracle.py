"""Track C B/C SFT v1 *candidate* oracle. Stdlib-only DESIGN QA, not B adapter.

Important: this codec and tests live in C's review scope; Track B has NOT
accepted, imported, or executed them. Caller roles are not authenticated.
"""
from __future__ import annotations
import hashlib
import json
import math

VOCAB = 2048
BYTE_MAX = 255
SPECIAL = {"EOS": 256, "PAD": 257, "BOS": 258, "SYS": 259,
           "USER": 260, "ASSIST": 261, "EOT": 262}
IGNORE = -100
SCHEMA = "ttm.bc.synthetic.sft_pack.v1"
CHECKPOINT_SCHEMA = "ttm.bc.synthetic.sft_checkpoint.v1"
OLD_B_SCHEMA = "ttm.track_b.synthetic.byte_windows.v1"


def canonical(obj):
    return (json.dumps(obj, sort_keys=True, ensure_ascii=False,
                       separators=(",", ":")) + "\n").encode("utf-8")


def sha(data):
    return hashlib.sha256(data).hexdigest()


def validate_codec():
    vals = list(SPECIAL.values())
    if len(vals) != len(set(vals)) or any(not BYTE_MAX < v < VOCAB for v in vals):
        raise ValueError("BC_CODEC_ID_COLLISION")
    if SPECIAL["EOS"] != 256 or VOCAB != 2048:
        raise ValueError("BC_CODEC_BASELINE_MISMATCH")
    return True


def encode_bytes(raw: bytes) -> list[int]:
    if type(raw) is not bytes:
        raise ValueError("BYTES_REQUIRED")
    return list(raw)


def decode_bytes(ids: list[int]) -> bytes:
    if not isinstance(ids, list) or any(type(x) is not int or not 0 <= x <= BYTE_MAX for x in ids):
        raise ValueError("BYTE_ID_RANGE")
    return bytes(ids)


def serialize(messages: list[dict], max_len: int) -> tuple[list[int], list[int]]:
    """Strictly role-derived targets; max_len is B model context+1."""
    validate_codec()
    if type(max_len) is not int or not 8 <= max_len <= 257:
        raise ValueError("MAX_LEN_OUTSIDE_SYNTHETIC_BOUND")
    if not isinstance(messages, list) or not messages:
        raise ValueError("BAD_CONVERSATION")
    ids, mask, expect = [SPECIAL["BOS"]], [0], "user"
    markers = {"system": SPECIAL["SYS"], "user": SPECIAL["USER"],
               "assistant": SPECIAL["ASSIST"]}
    for j, msg in enumerate(messages):
        if not isinstance(msg, dict) or set(msg) != {"role", "content"}:
            raise ValueError("BAD_MESSAGE_SHAPE")
        role, content = msg["role"], msg["content"]
        if role == "system" and j == 0:
            pass
        elif role != expect:
            raise ValueError("ROLE_ORDER_INVALID")
        else:
            expect = "assistant" if role == "user" else "user"
        if type(content) is not str or not content:
            raise ValueError("CONTENT_STRING_REQUIRED")
        raw = content.encode("utf-8", errors="strict")
        if not raw:
            raise ValueError("EMPTY_CONTENT")
        supervised = int(role == "assistant")
        ids.extend([markers[role], *encode_bytes(raw), SPECIAL["EOT"]])
        mask.extend([0] + [supervised] * len(raw) + [supervised])
    if messages[-1]["role"] != "assistant":
        raise ValueError("FINAL_ASSISTANT_REQUIRED")
    ids.append(SPECIAL["EOS"])
    mask.append(1)
    if len(ids) > max_len:
        raise ValueError("NO_SILENT_TRUNCATION")
    assert derive_mask(ids) == mask
    return ids, mask


def derive_mask(ids: list[int]) -> list[int]:
    """Structural role-parsing only; this is NOT an authenticated source record."""
    s = SPECIAL
    if not isinstance(ids, list) or len(ids) < 8 or ids[0] != s["BOS"] or ids[-1] != s["EOS"]:
        raise ValueError("BOUNDARY_INVALID")
    if any(type(x) is not int or not 0 <= x < VOCAB for x in ids):
        raise ValueError("TOKEN_RANGE_INVALID")
    i, limit, result = 1, len(ids) - 1, [0] * len(ids)
    if ids[i] == s["SYS"]:
        i += 1
        start = i
        while i < limit and ids[i] <= BYTE_MAX:
            i += 1
        if i == start or i >= limit or ids[i] != s["EOT"]:
            raise ValueError("SYSTEM_BOUNDARY")
        i += 1
    role = s["USER"]
    turns = 0
    while i < limit:
        if ids[i] != role:
            raise ValueError("ROLE_BOUNDARY_INVALID")
        i += 1
        start = i
        while i < limit and ids[i] <= BYTE_MAX:
            result[i] = int(role == s["ASSIST"])
            i += 1
        if i == start or i >= limit or ids[i] != s["EOT"]:
            raise ValueError("EOT_BOUNDARY_INVALID")
        result[i] = int(role == s["ASSIST"])
        i += 1
        turns += 1
        role = s["ASSIST"] if role == s["USER"] else s["USER"]
    if turns < 2 or role != s["USER"]:
        raise ValueError("FINAL_ASSISTANT_REQUIRED")
    result[-1] = 1
    return result


def targets(ids: list[int], flags: list[int], max_len: int):
    if type(max_len) is not int or not 8 <= max_len <= 257 or len(ids) > max_len:
        raise ValueError("MAX_LEN_INVALID")
    if not isinstance(flags, list) or len(flags) != len(ids) or any(type(v) is not int or v not in (0, 1) for v in flags):
        raise ValueError("FLAGS_INVALID")
    if flags != derive_mask(ids):
        raise ValueError("ROLE_MASK_PROVENANCE_MISMATCH")
    right_padded = ids + [SPECIAL["PAD"]] * (max_len - len(ids))
    m = flags + [0] * (max_len - len(flags))
    x = right_padded[:-1]
    y = [right_padded[j] if m[j] else IGNORE for j in range(1, max_len)]
    if not any(k != IGNORE for k in y):
        raise ValueError("ALL_IGNORE")
    return x, y


def build(messages: list[dict], max_len: int):
    ids, mask = serialize(messages, max_len)
    return targets(ids, mask, max_len)


def independent_valid_ce(logits: list[list[float]], targets_: list[int]) -> float:
    """Unreduced cross-entropy SUM(valid) / N_valid; no torch/model used."""
    if len(logits) != len(targets_) or not logits:
        raise ValueError("SHAPE")
    total, valid = 0.0, 0
    for row, y in zip(logits, targets_):
        if not row or any(not math.isfinite(x) for x in row):
            raise ValueError("LOGITS_INVALID")
        if y == IGNORE:
            continue
        if type(y) is not int or not 0 <= y < len(row):
            raise ValueError("TARGET_RANGE")
        m = max(row)
        total += m + math.log(sum(math.exp(z - m) for z in row)) - row[y]
        valid += 1
    if not valid:
        raise ValueError("ALL_IGNORE")
    return total / valid


def verify_manifest(manifest: dict, pins: dict):
    """Exact candidate schema/hash guard. No checkpoint IO, no B adapter."""
    required = {"tokenizer_sha256", "chat_template_sha256", "serialized_inputs_sha256",
                "target_labels_sha256", "target_masks_sha256", "config_sha256",
                "checkpoint_schema_sha256"}
    if not isinstance(manifest, dict) or manifest.get("schema") != SCHEMA:
        raise ValueError("NOT_BC_SFT_PACK_V1")
    if manifest.get("checkpoint_schema") != CHECKPOINT_SCHEMA:
        raise ValueError("CHECKPOINT_SCHEMA_VERSION")
    if not isinstance(pins, dict) or set(pins) != required:
        raise ValueError("PIN_FIELDS")
    for key in required:
        v = pins[key]
        if not isinstance(v, str) or len(v) != 64 or any(x not in "0123456789abcdef" for x in v):
            raise ValueError("BAD_PIN")
        if manifest.get(key) != v:
            raise ValueError("SHA_PIN_MISMATCH:" + key)
    return True
