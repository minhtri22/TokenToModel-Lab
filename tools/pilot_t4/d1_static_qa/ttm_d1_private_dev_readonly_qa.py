#!/usr/bin/env python3
"""TTM-Small-4M D1 private DEV static QA. No inference/training. No write.
Reads only D1 private candidate, frozen T1 TRAIN-only BPE manifest, and optionally
the two published historical prompt documents. Does not read TEST, Q1Q2 or raw
FRESH16 mapping/outputs. Run with Python 3.12 on owner's Windows workspace.
"""
from __future__ import annotations
import collections
import hashlib
import importlib.util
import json
import pathlib
import re
import sys

ROOT = pathlib.Path(r"D:\\WORK\\RESEARCH\\TokenToModel-Lab")
WORKTREE = ROOT / "worktrees" / "ttm-fresh16-quality-20261111"
PACK = ROOT / "_tmp" / "TTM_SMALL4M_D1_NEW_DEV_PRIVATE_20261111.json"
BPE = ROOT / "_tmp" / "ttm_t1_real_source_v1" / "T1_BPE2048_REAL_TRAIN_MANIFEST.json"
SOURCE = WORKTREE / "tools" / "pilot_t4" / "integrated" / "source_t2" / "ttm_gpt2_bpe2048.py"
EXPECTED_LF_SHA256 = "de5c0acae9a863e255922963d9644623ff6b1cbfedc0ff9edd7d8225cbac7603"
EXPECTED_BPE_BYTES_SHA256 = "cba18e60cee3d08a353ee6d4a451017289e45af7b4b1179c87171b9b78d7dfdc"
EXPECTED_BPE_MANIFEST_SHA256 = "6da22cf79c3a6cfd08d80a768eb1074125a753164ccf62a164e79545956e94c6"
PUBLIC_HISTORY = (
    WORKTREE / "artifacts" / "research" / "ttm-small4m-quality-gap"
    / "TTM_FRESH_CONTINUATION_PROMPT_SET_CANDIDATE_V1_20261111.json",
    WORKTREE / "artifacts" / "research" / "ttm-small4m-quality-gap"
    / "TTM_FRESH16_ALLOWED_PUBLIC_HISTORICAL_PROMPTS_20261111.json",
)
SEEDS = (2026111201, 2026111202, 2026111203)
CATEGORIES = ("entity_location", "causal_reasoning", "rule_constraint", "goal_persistence")

def digest(b: bytes) -> str:
    return hashlib.sha256(b).hexdigest()

def die(message: str) -> None:
    print("TTM_D1_QA_FAIL=" + message)
    raise SystemExit(2)

def all_text(v: object):
    if isinstance(v, dict):
        for z in v.values():
            yield from all_text(z)
    elif isinstance(v, list):
        for z in v:
            yield from all_text(z)
    elif isinstance(v, str) and 20 < len(v) < 1500:
        yield v

def shingles(s: str):
    w = re.findall(r"[a-z0-9]+", s.casefold())
    return {tuple(w[i:i+5]) for i in range(max(0, len(w)-4))}

def main() -> None:
    if not (ROOT.is_dir() and WORKTREE.is_dir() and PACK.is_file() and BPE.is_file() and SOURCE.is_file()):
        die("REQUIRED_SOURCE_MISSING")
    raw = PACK.read_bytes()
    normalized = raw.replace(b"\r\n", b"\n")
    if b"\r" in normalized:
        die("UNEXPECTED_BARE_CR")
    if digest(normalized) != EXPECTED_LF_SHA256:
        die("D1_LF_READBACK_SHA256_MISMATCH")
    obj = json.loads(raw.decode("utf-8", "strict"))
    if obj.get("schema") != "ttm.small4m.d1.new_dev.private_stimulus.one_packet.v1":
        die("PACK_SCHEMA_MISMATCH")
    bpe_bytes = BPE.read_bytes()
    if digest(bpe_bytes) != EXPECTED_BPE_BYTES_SHA256:
        die("T1_BPE_MANIFEST_RAW_SHA256_MISMATCH")
    spec = importlib.util.spec_from_file_location("ttm_d1_exact_bpe", SOURCE)
    if spec is None or spec.loader is None:
        die("BPE_SOURCE_IMPORT_FAILED")
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    bpe = module.BPE2048.from_manifest(json.loads(bpe_bytes.decode("utf-8")))
    if bpe.manifest()["manifest_sha256"] != EXPECTED_BPE_MANIFEST_SHA256:
        die("BPE_INTERNAL_MANIFEST_SHA_MISMATCH")
    if len(obj["families"]) != 16 or len(obj["prompts"]) != 128 or len(obj["neutral_prior_prompts"]) != 64 or len(obj["blind_mapping_private"]) != 512:
        die("CARDINALITY_MISMATCH")
    fam = {f["id"]: f for f in obj["families"]}
    if len(fam) != 16:
        die("FAMILY_DUPLICATE")
    if set(x["category"] for x in obj["families"]) != set(CATEGORIES):
        die("CATEGORY_MISMATCH")
    if any(sum(f["category"] == c for f in fam.values()) != 4 for c in CATEGORIES):
        die("CATEGORY_4_EACH_MISMATCH")
    if obj["quality_summary"].get("issue_count") != 0:
        die("PACK_GENERATION_REPORTED_ISSUES")
    for f in fam.values():
        if len(bpe.encode(f["fact_A"])) != len(bpe.encode(f["fact_B"])):
            die("FACT_TOKEN_MISMATCH:" + f["id"])
        ca = len(bpe.encode(f["continuation_A"]))
        cb = len(bpe.encode(f["continuation_B"]))
        if not (3 <= ca == cb <= 12):
            die("CANDIDATE_TOKEN_MISMATCH:" + f["id"])
    samples = obj["prompts"]
    seen_text = set()
    seen_id = set()
    by_family = collections.Counter()
    for row in samples:
        fid = row["family_id"]
        if fid not in fam or row["id"] in seen_id:
            die("PROMPT_ID_INVALID")
        seen_id.add(row["id"])
        if row["prompt_text"] in seen_text:
            die("EXACT_PROMPT_DUPLICATE")
        seen_text.add(row["prompt_text"])
        if not row["prompt_text"].isascii() or row["prompt_text"].endswith(" "):
            die("PROMPT_NON_ASCII_OR_TRAILING_SPACE")
        count = len(bpe.encode(row["prompt_text"]))
        if count != row["prompt_bpe"]:
            die("PROMPT_BPE_MISMATCH:" + row["id"])
        if count + 64 > 256:
            die("CONTEXT_OVERFLOW:" + row["id"])
        short = row["length"] == "short"
        if not ((64 <= count <= 96) if short else (160 <= count <= 192)):
            die("LENGTH_WINDOW_MISMATCH:" + row["id"])
        correct_fact = fam[fid]["fact_A" if row["condition"] == "A" else "fact_B"]
        if row["prompt_text"].count(correct_fact) != 1:
            die("FACT_INCORRECT_OR_REPEATED:" + row["id"])
        end = row["prompt_text"].index(correct_fact) + len(correct_fact)
        cue_end = len(bpe.encode(row["prompt_text"][:end]))
        dist = count - cue_end
        lo, hi = (16, 32) if row["distance"] == "near" else ((48,64) if short else (144,160))
        if not lo <= dist <= hi or dist != row["cue_distance_bpe"] or cue_end != row["fact_end_bpe"]:
            die("CUE_DISTANCE_MISMATCH:" + row["id"])
        if row["candidate_A"] != fam[fid]["continuation_A"] or row["candidate_B"] != fam[fid]["continuation_B"]:
            die("CANDIDATE_CHANGED_AFTER_FAMILY:" + row["id"])
        by_family[fid] += 1
    if any(by_family[fid] != 8 for fid in fam):
        die("INCOMPLETE_2X2_BY_FACT")
    prior = {r["id"]:r for r in obj["neutral_prior_prompts"]}
    if len(prior) != 64:
        die("PRIOR_DUPLICATE_ID")
    for row in samples:
        p = prior.get(row["neutral_prompt_id"])
        if p is None or p["family_id"] != row["family_id"] or p["length"] != row["length"] or p["distance"] != row["distance"]:
            die("PRIOR_ALIGNMENT_MISMATCH:" + row["id"])
    for r in prior.values():
        if len(bpe.encode(r["prompt_text"])) != r["prompt_bpe"]:
            die("PRIOR_BPE_MISMATCH:" + r["id"])
        f=fam[r["family_id"]]
        if f["fact_A"] in r["prompt_text"] or f["fact_B"] in r["prompt_text"]:
            die("PRIOR_FACT_LEAKAGE:" + r["id"])
    maps = obj["blind_mapping_private"]
    if len({r["blind_id"] for r in maps}) != 512:
        die("BLIND_ID_COLLISION")
    coverage = collections.defaultdict(list)
    for r in maps:
        if r["prompt_id"] not in seen_id:
            die("BLIND_PROMPT_ID_UNKNOWN")
        coverage[r["prompt_id"]].append((r["decoder"], r["seed"]))
    for pid in seen_id:
        pairs = coverage[pid]
        if sorted(pairs, key=lambda q: (q[0], q[1] or 0)) != sorted([("GREEDY",None)]+[("NUCLEUS",s) for s in SEEDS], key=lambda q:(q[0], q[1] or 0)):
            die("BLIND_DECODER_SEED_MISMATCH:" + pid)
    if any(sum(f["candidate_order_in_manifest"] == "A_then_B" for f in fam.values() if f["category"] == c) != 2 for c in CATEGORIES):
        die("COUNTERBALANCE_MISMATCH")
    public_paths_found = 0
    public_strings = []
    for file in PUBLIC_HISTORY:
        if file.is_file():
            public_paths_found += 1
            public_strings.extend(all_text(json.loads(file.read_text(encoding="utf-8"))))
    matches=[]
    for f in fam.values():
        scene=f["scene"]
        g=shingles(scene)
        for s in public_strings:
            h=shingles(s)
            sim=len(g & h)/len(g | h) if g and h else 0
            if scene in s or s == scene or sim >= 0.85:
                matches.append(f["id"])
                break
    if matches:
        die("PUBLIC_HISTORICAL_EXACT_OR_NEAR_SCENE_OVERLAP:" + ",".join(matches))
    print("TTM_D1_STATIC_QA=PASS_SCOPED_PRIVATE_PACKET")
    print("D1_RAW_SHA256="+digest(raw))
    print("D1_RAW_BYTES="+str(len(raw)))
    print("D1_LF_NORMALIZED_SHA256="+digest(normalized))
    print("D1_BPE_EXACT_PYTHON_SOURCE_SHA_VERIFIED=PASS")
    print("D1_PROMPTS=128 D1_PRIOR=64 D1_BLIND=512 D1_FAMILIES=16")
    print("D1_PUBLIC_HISTORICAL_FILES_PRESENT="+str(public_paths_found))
    print("D1_PRIVATE_FRESH16_AC_TEST_Q1Q2_SEMANTIC_OVERLAP=NOT_VERIFIED")
    print("D1_RATER_ASSIGNED=NO")
    print("D1_SCIENCE_EXECUTED=NO")

if __name__ == "__main__":
    main()
