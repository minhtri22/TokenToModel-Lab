"""Compatibility adapter for executing C's exact Part A tests on B's new v2 wire.

All role/serializer/target/byte functions are B v2, not C's implementation.
The metadata-only fixture tester is separated from required verify_bundle() IO:
a matching hex string by itself is NOT artifact custody.
"""
from __future__ import annotations
from src.ttm_track_b import bc_sft_bridge_v2 as b
import math

SPECIAL=b.SPECIAL
BYTE_MAX=b.BYTE_MAX
VOCAB=b.VOCAB
IGNORE=b.IGNORE
SCHEMA=b.SCHEMA
CHECKPOINT_SCHEMA=b.CHECKPOINT_SCHEMA
OLD_B_SCHEMA=b.OLD_B_SCHEMA
validate_codec=b.validate_codec
encode_bytes=b.encode_bytes
decode_bytes=b.decode_bytes
serialize=b.serialize
derive_mask=b.derive_mask
targets=b.targets
build=b.build
canonical=b.canonical
sha=b.sha

def independent_valid_ce(logits: list[list[float]], labels: list[int]) -> float:
    """Math-only oracle matching C Part A arithmetic, not a model training loss."""
    if not logits or len(logits)!=len(labels):
        raise ValueError("SHAPE")
    total=0.0
    n=0
    for row,y in zip(logits,labels):
        if not row or any(not math.isfinite(z) for z in row):
            raise ValueError("LOGITS_INVALID")
        if y==IGNORE:
            continue
        if type(y) is not int or not 0<=y<len(row):
            raise ValueError("TARGET_RANGE")
        maximum=max(row)
        total+=maximum+math.log(sum(math.exp(z-maximum) for z in row))-row[y]
        n+=1
    if not n:
        raise ValueError("ALL_IGNORE")
    return total/n

def verify_manifest(manifest: dict, pins:dict) -> bool:
    """Only C legacy test metadata shape; NOT production artifact-byte verification.

    The required gate for F04 is b.verify_bundle(root) which opens actual files.
    """
    if not isinstance(manifest,dict) or manifest.get("schema")!=SCHEMA:
        raise ValueError("NOT_BC_SFT_PACK_V2")
    if manifest.get("checkpoint_schema")!=CHECKPOINT_SCHEMA:
        raise ValueError("CHECKPOINT_SCHEMA_VERSION")
    if not isinstance(pins,dict) or set(pins)!=b.REQUIRED:
        raise ValueError("PIN_FIELDS")
    for key in b.REQUIRED:
        v=pins[key]
        if type(v) is not str or len(v)!=64 or any(c not in "0123456789abcdef" for c in v):
            raise ValueError("BAD_PIN")
        if manifest.get(key)!=v:
            raise ValueError("SHA_PIN_MISMATCH:"+key)
    return True
