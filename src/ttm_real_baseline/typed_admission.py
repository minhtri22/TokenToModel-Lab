"""T4 GPT vertical-slice *source-contract* admission. Pure Python 3.12 stdlib.

This module NEVER opens private files, imports Torch, deserializes checkpoints,
runs inference, grants Q4/I2 or claims evidence of real weights or data rights.
Inputs are UNTRUSTED DECLARATIONS for a future independently verified witness.

Do not use a structurally valid packet as a release token. The only successful
status is SOURCE_RELATIONSHIPS_VALIDATED_DESIGN_ONLY; Q4 stays HOLD.
"""
from __future__ import annotations

import re
from collections.abc import Mapping

SCHEMA = "ttm.pm.real_gpt.t4_typed_identity_plan.v1"
BASE_MAIN_SHA = "b2e97dd3b773fc22a91618c8f034d22fda1f5908"
BPE_SCHEMA = "ttm.gpt2.pretokenized.byte-bpe.2048.v1"
PACK_SCHEMA = "ttm.t4.private.train_val.windowpack.v1"
CHECKPOINT_SCHEMA = "ttm.t4.science.checkpoint.v1"
READY_SCHEMA = "ttm.t4.ready.last.v1"

EXACT_SOURCE_BLOBS = {
    "P02": "9762343e06cf800b50574c2871ae1ed58537fb18",
    "T4_CAPACITY": "c9a6f256ba975228683ee7de2a1090e649110e97",
    "T4_TRAIN": "76c4d0155cd0736919f41682f240b47ad3d7c428",
    "T4_PACK": "cdce219f2a2df27e25579f069238d4327c1d7d91",
    "T4_BPE": "fa5bd892941ba5aa6e6b2f0b2b0ae974efe297b6",
    "B_SYNTHETIC_LOADER": "0d76d764097cd838f3fef9cb16c9da11ff778bb9",
    "C_REGISTRY": "364a15d305b71e0c236a27409430f1e27e14aa70",
}
T4_CONFIG = {
    "vocab_size": 2048,
    "max_seq_len": 256,
    "n_embd": 256,
    "n_layer": 4,
    "n_head": 4,
    "norm_type": "layernorm",
}
HEX64 = re.compile(r"[0-9a-f]{64}\Z")
HEX40 = re.compile(r"[0-9a-f]{40}\Z")

class ContractHold(ValueError):
    """Fail closed before any private byte/model read."""


def _dict(value: object, keys: set[str], where: str) -> Mapping:
    if not isinstance(value, dict) or set(value) != keys:
        raise ContractHold("SCHEMA_KEYS_MISMATCH:" + where)
    return value


def _sha(value: object, label: str, length: int = 64) -> str:
    pat = HEX64 if length == 64 else HEX40
    if not isinstance(value, str) or pat.fullmatch(value) is None:
        raise ContractHold("INVALID_SHA_DOMAIN:" + label)
    return value


def _positive(value: object, name: str) -> int:
    if type(value) is not int or value <= 0:
        raise ContractHold("INVALID_POSITIVE_INTEGER:" + name)
    return value


def _equal(x: object, y: object, code: str) -> None:
    if x != y:
        raise ContractHold(code)


def inspect_declarations(packet: object) -> dict:
    """Validate declared T4 relationships, NOT authenticity of physical bytes.

    A caller must separately provide owner-authorized readback of actual bytes,
    handle ancestry, rights, resources, fresh VAL/gold, independent QA and Q4 GO.
    This function *cannot* produce executable authorization, even for all-valid
    declarations, and does not touch the filesystem or model runtime.
    """
    p = _dict(packet, {"schema", "source", "tokenizer", "pack",
                       "checkpoint", "evaluation", "authority", "codec"}, "ROOT")
    _equal(p["schema"], SCHEMA, "PACKET_SCHEMA_MISMATCH")
    src = _dict(p["source"], {"main_commit", "git_blobs"}, "SOURCE")
    _equal(src["main_commit"], BASE_MAIN_SHA, "BASE_SOURCE_DRIFT")
    _dict(src["git_blobs"], set(EXACT_SOURCE_BLOBS), "SOURCE_BLOBS")
    for role, expected in EXACT_SOURCE_BLOBS.items():
        _sha(src["git_blobs"][role], "GIT_BLOB_" + role, 40)
        _equal(src["git_blobs"][role], expected, "PINNED_GIT_SOURCE_MISMATCH:" + role)

    tok = _dict(p["tokenizer"], {
        "schema", "file_sha256", "manifest_sha256", "token_merges_sha256",
        "vocab_size", "eos_id", "merges", "trained_on",
    }, "TOKENIZER")
    _equal(tok["schema"], BPE_SCHEMA, "T4_TOKENIZER_SCHEMA_MISMATCH")
    _equal(tok["trained_on"], "TRAIN_ONLY", "TOKENIZER_TRAIN_LEAK_OR_UNVERIFIED")
    for name in ("file_sha256", "manifest_sha256", "token_merges_sha256"):
        _sha(tok[name], "T4_BPE_" + name)
    for name, expected in (("vocab_size", 2048), ("eos_id", 256), ("merges", 1791)):
        _equal(tok[name], expected, "T4_BPE_CONFIG_MISMATCH:" + name)

    pack = _dict(p["pack"], {
        "schema", "npz_sha256", "npz_bytes", "t1_bpe_file_sha256",
        "t1_bpe_internal_sha256", "source_sha256", "t1_split_sha256",
        "contains_test", "contains_raw_text", "context",
    }, "PACK")
    _equal(pack["schema"], PACK_SCHEMA, "T4_PACK_SCHEMA_MISMATCH")
    for name in ("npz_sha256", "t1_bpe_file_sha256",
                 "t1_bpe_internal_sha256", "source_sha256", "t1_split_sha256"):
        _sha(pack[name], "PACK_" + name)
    _positive(pack["npz_bytes"], "PACK_BYTES")
    if pack["contains_test"] is not False or pack["contains_raw_text"] is not False:
        raise ContractHold("T4_PACK_TEST_OR_RAW_TEXT_FORBIDDEN")
    _equal(pack["context"], 256, "T4_PACK_CONTEXT_MISMATCH")
    _equal(pack["t1_bpe_file_sha256"], tok["file_sha256"], "BPE_FILE_SHA_DOMAIN_MISMATCH")
    _equal(pack["t1_bpe_internal_sha256"], tok["manifest_sha256"],
           "BPE_INTERNAL_MANIFEST_SHA_DOMAIN_MISMATCH")

    ckpt = _dict(p["checkpoint"], {"file_sha256", "ready", "declared_header"}, "CHECKPOINT")
    _sha(ckpt["file_sha256"], "CHECKPOINT_FILE")
    ready = _dict(ckpt["ready"], {"schema", "sha256", "bytes", "step",
                                  "checkpoint", "train_pack_sha256",
                                  "science_lock_sha256", "progress_sha256"}, "READY")
    _equal(ready["schema"], READY_SCHEMA, "T4_READY_SCHEMA_MISMATCH")
    _equal(ready["checkpoint"], "checkpoint.pt", "UNTRUSTED_CHECKPOINT_FILENAME")
    for name in ("sha256", "train_pack_sha256", "science_lock_sha256",
                 "progress_sha256"):
        _sha(ready[name], "READY_" + name)
    _positive(ready["bytes"], "CHECKPOINT_BYTES")
    _positive(ready["step"], "CHECKPOINT_STEP")
    _equal(ready["sha256"], ckpt["file_sha256"], "READY_CHECKPOINT_FILE_SHA_MISMATCH")
    _equal(ready["train_pack_sha256"], pack["npz_sha256"], "READY_TRAIN_PACK_SHA_MISMATCH")

    h = _dict(ckpt["declared_header"], {
        "schema", "step", "p02_git_blob", "config",
        "science_lock_sha256", "train_pack_sha256",
    }, "DECLARED_CHECKPOINT_HEADER")
    _equal(h["schema"], CHECKPOINT_SCHEMA, "T4_CHECKPOINT_SCHEMA_MISMATCH")
    _equal(h["config"], T4_CONFIG, "T4_MODEL_CONFIG_MISMATCH")
    _equal(h["step"], ready["step"], "T4_CHECKPOINT_STEP_MISMATCH")
    _equal(_sha(h["p02_git_blob"], "P02_BLOB", 40),
           EXACT_SOURCE_BLOBS["P02"], "T4_P02_PIN_MISMATCH")
    _equal(_sha(h["science_lock_sha256"], "SCIENCE_LOCK"),
           ready["science_lock_sha256"], "T4_LOCK_PIN_MISMATCH")
    _equal(_sha(h["train_pack_sha256"], "TRAIN_PACK"),
           pack["npz_sha256"], "T4_CHECKPOINT_TRAIN_PACK_SHA_MISMATCH")

    codec = _dict(p["codec"], {
        "kind", "direct_bc_v2_alias", "external_role_byte_sidecar",
    }, "CODEC")
    _equal(codec["kind"], "T4_TRAIN_ONLY_BPE2048", "CODEC_KIND_UNSUPPORTED")
    if codec["direct_bc_v2_alias"] is not False:
        raise ContractHold("T4_BPE_BC_V2_IDS_257_TO_262_COLLIDE")
    _equal(codec["external_role_byte_sidecar"], "DESIGN_ONLY_NOT_IMPLEMENTED",
           "PROSPECTIVE_CODEC_UNVERIFIED")

    ev = _dict(p["evaluation"], {
        "primary", "a_i1", "gold_source", "fresh_val", "byte_spans",
    }, "EVALUATION")
    _equal(ev["primary"], "C_VALID_UTF8_BYTE_BPB", "EVAL_PRIMARY_MISMATCH")
    _equal(ev["a_i1"], "PASS_SCOPED_MEASUREMENT_ONLY", "A_I1_SCOPE_PROMOTION")
    for key in ("gold_source", "fresh_val", "byte_spans"):
        _equal(ev[key], "HOLD_REAL_EVIDENCE_MISSING", "EVAL_REAL_CUSTODY_NOT_VERIFIED:" + key)

    authority = _dict(p["authority"], {
        "q4", "i2", "checkpoint_read", "real_data_read", "gpu", "science",
        "new_test", "rights", "native_resource", "independent_real_qa",
    }, "AUTHORITY")
    _equal(authority["q4"], "HOLD", "UNAUTHORIZED_Q4_GO")
    _equal(authority["i2"], "HOLD", "UNAUTHORIZED_I2_GO")
    for key in ("checkpoint_read", "real_data_read", "gpu", "science", "new_test"):
        if authority[key] is not False:
            raise ContractHold("UNAUTHORIZED_EXECUTION:" + key)
    for key in ("rights", "native_resource", "independent_real_qa"):
        _equal(authority[key], "UNVERIFIED", "FALSE_ATTESTATION:" + key)

    return {
        "schema": "ttm.pm.real_gpt.t4_structural_readback.v1",
        "status": "PASS_DECLARED_SOURCE_RELATIONSHIPS_ONLY",
        "source_main_commit": BASE_MAIN_SHA,
        "checkpoint_sha256_declared": ckpt["file_sha256"],
        "train_pack_sha256_declared": pack["npz_sha256"],
        "tokenizer_file_sha256_declared": tok["file_sha256"],
        "tokenizer_manifest_sha256_declared": tok["manifest_sha256"],
        "distinct_sha_domains": True,
        "physical_byte_custody": "UNVERIFIED",
        "rights": "UNVERIFIED",
        "gold": "HOLD",
        "real_model_run": False,
        "authorizes_q4": False,
        "authorizes_i2": False,
        "authorizes_checkpoint_or_data_read": False,
    }
