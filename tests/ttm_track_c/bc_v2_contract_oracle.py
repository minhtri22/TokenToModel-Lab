"""Agent C v2 *candidate* acceptance oracle; NOT the B implementation.

This is a source/design validation helper only, with no model, training, real
checkpoint, real data or network IO.  No authority to migrate B v1 receipts.
"""
from __future__ import annotations

import hashlib
import json
import os
from pathlib import Path
import re

WIRE_SCHEMA = "ttm.bc.synthetic.sft.wire.v2"
PACK_SCHEMA = "ttm.bc.synthetic.sft.pack.v2"
RESUME_METADATA_SCHEMA = "ttm.bc.synthetic.sft.resume_metadata.v2"
CODEC_SCHEMA = "ttm.bc.synthetic.byte_chat_codec.v2"
TEMPLATE_SCHEMA = "ttm.bc.synthetic.role_bound_template.v2"
CANON_SCHEMA = "ttm.bc.canonical_json_utf8_lf.v2"
SPECIAL = {"EOS": 256, "PAD": 257, "BOS": 258, "SYS": 259,
           "USER": 260, "ASSIST": 261, "EOT": 262}
IGNORE = -100
MAX_LEN = 33  # 32 positions after shift; B synthetic model only
ARTIFACT_NAMES = {
    "tokenizer_sha256": "tokenizer.json",
    "chat_template_sha256": "chat_template.json",
    "serialized_inputs_sha256": "serialized_inputs.json",
    "target_masks_sha256": "target_masks.json",
    "target_labels_sha256": "target_labels.json",
    "config_sha256": "config.json",
    "checkpoint_schema_sha256": "checkpoint_schema.json",
}
LEGACY_SCHEMAS = frozenset({
    "ttm.track_b.synthetic.byte_windows.v1",
    "ttm.bc.synthetic.sft.pack.v1",
    "ttm.bc.synthetic.sft_pack.v1",
    "ttm.bc.synthetic.sft.resume.v1",
    "ttm.bc.synthetic.sft_checkpoint.v1",
    "ttm.p04.model_checkpoint.v1",
    "ttm.t4.science.checkpoint.v1",
    "ttm.track_b.synthetic.train_checkpoint.v1",
})
HEX64 = re.compile(r"[0-9a-f]{64}\Z")


def canonical_v2(value: object) -> bytes:
    """Actual exact v2 JSON artifact bytes: UTF-8, sorted, compact, final LF.

    No Unicode normalization or newline rewriting within JSON strings;
    surrogate Unicode and nonfinite floats are rejected instead of coerced.
    """
    raw = json.dumps(value, sort_keys=True, separators=(",", ":"),
                     ensure_ascii=False, allow_nan=False)
    return (raw + "\n").encode("utf-8", errors="strict")


def sha256_bytes(data: bytes) -> str:
    if type(data) is not bytes:
        raise TypeError("RAW_BYTES_REQUIRED")
    return hashlib.sha256(data).hexdigest()


def strict_typed_bridge(messages: list[dict], *, max_len: int = MAX_LEN) -> list[dict]:
    """C str → B list[int] with exact UTF-8 identity, not provenance/auth."""
    if type(max_len) is not int or not 8 <= max_len <= MAX_LEN:
        raise ValueError("SFT_CONTEXT_BOUND")
    if not isinstance(messages, list) or not messages:
        raise ValueError("MESSAGES_REQUIRED")
    result, expected = [], "user"
    for i, message in enumerate(messages):
        if not isinstance(message, dict) or set(message) != {"role", "content"}:
            raise ValueError("STRUCTURED_ROLE_PROVENANCE")
        role, text = message["role"], message["content"]
        if role == "system" and i == 0:
            pass
        elif role != expected:
            raise ValueError("ROLE_ORDER")
        else:
            expected = "assistant" if role == "user" else "user"
        if type(text) is not str or not text:
            raise ValueError("C_TEXT_CONTENT_REQUIRED")
        raw = text.encode("utf-8", "strict")  # Unicode surrogate raises
        if raw.decode("utf-8", "strict") != text:
            raise ValueError("UTF8_IDENTITY_ROUNDTRIP")
        result.append({"role": role, "content": list(raw)})
    if result[-1]["role"] != "assistant":
        raise ValueError("FINAL_ASSISTANT_REQUIRED")
    # BOS + each header/content/EOT + terminal EOS
    n = 2 + sum(2 + len(m["content"]) for m in result)
    if n > max_len:
        raise ValueError("NO_SILENT_TRUNCATION")
    return result


def strict_b_bytes_to_text(messages: list[dict]) -> list[dict]:
    """Only valid UTF-8 B byte records may be mapped back into C text."""
    result = []
    if not isinstance(messages, list):
        raise ValueError("MESSAGES_REQUIRED")
    for message in messages:
        if not isinstance(message, dict) or set(message) != {"role", "content"}:
            raise ValueError("STRUCTURED_ROLE_PROVENANCE")
        data = message["content"]
        if not isinstance(data, list) or not data or any(
            type(x) is not int or not 0 <= x <= 255 for x in data
        ):
            raise ValueError("BYTE_CONTENT_RANGE")
        text = bytes(data).decode("utf-8", "strict")
        result.append({"role": message["role"], "content": text})
    return result


def validate_new_schema(schema: str, *, role: str) -> None:
    if role not in ("pack", "resume_metadata"):
        raise ValueError("SCHEMA_ROLE")
    required = PACK_SCHEMA if role == "pack" else RESUME_METADATA_SCHEMA
    if schema in LEGACY_SCHEMAS or schema != required:
        raise ValueError("SCHEMA_VERSION_MISMATCH")
    # Resume metadata is not a checkpoint weight artifact.


def _safe_path(root: Path, name: str) -> Path:
    if name not in set(ARTIFACT_NAMES.values()):
        raise ValueError("UNEXPECTED_ARTIFACT_PATH")
    if root.is_symlink() or not root.is_dir():
        raise ValueError("UNSAFE_ROOT")
    p = root / name
    if p.is_symlink():
        raise ValueError("ARTIFACT_SYMLINK")
    return p


def freeze_seven_artifacts(root: Path, objects: dict) -> dict:
    """Save once and independently read back actual seven artifact bytes."""
    root = Path(root)
    if set(objects) != set(ARTIFACT_NAMES):
        raise ValueError("SEVEN_ARTIFACT_FIELDS_REQUIRED")
    report = {"wire_schema": WIRE_SCHEMA, "pack_schema": PACK_SCHEMA,
              "resume_metadata_schema": RESUME_METADATA_SCHEMA,
              "canonical_schema": CANON_SCHEMA, "artifacts": {}}
    for key, name in ARTIFACT_NAMES.items():
        raw = canonical_v2(objects[key])
        path = _safe_path(root, name)
        with path.open("xb") as out:
            out.write(raw)
            out.flush()
            os.fsync(out.fileno())
        reread = path.read_bytes()
        if reread != raw:
            raise IOError("ARTIFACT_READBACK_BYTES_MISMATCH")
        report["artifacts"][key] = {"file": name, "size": len(reread),
                                   "sha256": sha256_bytes(reread)}
    verify_seven_artifacts(root, report)
    return report


def verify_seven_artifacts(root: Path, report: dict) -> bool:
    """Reject all 7 byte changes, LF changes, schema aliases and missing files."""
    root = Path(root)
    if not isinstance(report, dict) or set(report) != {
        "wire_schema", "pack_schema", "resume_metadata_schema",
        "canonical_schema", "artifacts"
    }:
        raise ValueError("MANIFEST_SCHEMA_FIELDS")
    if (report["wire_schema"], report["pack_schema"],
        report["resume_metadata_schema"], report["canonical_schema"]) != (
        WIRE_SCHEMA, PACK_SCHEMA, RESUME_METADATA_SCHEMA, CANON_SCHEMA
    ):
        raise ValueError("V2_SCHEMA_MISMATCH")
    items = report["artifacts"]
    if not isinstance(items, dict) or set(items) != set(ARTIFACT_NAMES):
        raise ValueError("SEVEN_ARTIFACT_FIELDS_REQUIRED")
    for key, name in ARTIFACT_NAMES.items():
        info = items[key]
        if not isinstance(info, dict) or set(info) != {"file", "size", "sha256"}:
            raise ValueError("ARTIFACT_RECORD_FIELDS")
        if info["file"] != name or type(info["size"]) is not int:
            raise ValueError("ARTIFACT_FILE_ALIAS_OR_SIZE")
        h = info["sha256"]
        if type(h) is not str or HEX64.fullmatch(h) is None:
            raise ValueError("BAD_SHA256")
        path = _safe_path(root, name)
        data = path.read_bytes()
        if len(data) != info["size"] or sha256_bytes(data) != h:
            raise ValueError("ACTUAL_BYTE_READBACK_SHA_MISMATCH")
        try:
            obj = json.loads(data.decode("utf-8", "strict"))
        except (UnicodeError, ValueError) as exc:
            raise ValueError("ARTIFACT_UTF8_JSON_INVALID") from exc
        if canonical_v2(obj) != data:
            raise ValueError("CANONICAL_V2_BYTE_MISMATCH")
    return True
