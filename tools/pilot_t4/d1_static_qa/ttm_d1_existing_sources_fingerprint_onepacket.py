#!/usr/bin/env python3
"""TTM D1 V2: one-shot, owner-local, source-only fingerprint index and overlap screen.

Reads pinned DEV V2 and permitted consumed/public *prompts only*. No science,
training, inference, TEST/Q1Q2 sealed reads, unblinding, seed use, or mapping use.
Writes PRIVATE per-record digest index under project/_tmp; prints only aggregates.
"""
from __future__ import annotations

import hashlib
import json
import os
import re
import sys
from pathlib import Path

ROOT = Path(r"D:\WORK\RESEARCH\TokenToModel-Lab")
TEMP = ROOT / "_tmp"
OUTPUT = TEMP / "TTM_D1_ONEPACKET_FINGERPRINT_20261112"
DEV = TEMP / "TTM_SMALL4M_D1_NEW_DEV_PRIVATE_V2_20261111.json"
S1 = TEMP / "ttm_fresh16_v2_e0_20261111" / "S1_BLIND_PACKET_PRIVATE.json"
CF1 = TEMP / "TTM_CF1_STEP1024_DEV36_ONE_SHOT_20261111" / "CF1_DEV_MODEL_INPUT_ONLY.json"
HISTORY = ROOT / "worktrees" / "ttm-fresh16-quality-20261111" / "artifacts" / "research" / "ttm-small4m-quality-gap" / "TTM_FRESH16_ALLOWED_PUBLIC_HISTORICAL_PROMPTS_20261111.json"
AC = TEMP / "TTM_D1_FINGERPRINT_AC_FINAL24_PUBLIC_PINNED_20261112.json"

D1_SHA = "f381ae8ab9c67c8590092f85445ab2fbe95a3b1c6a646ec18ee26b6b13ac92b8"
S1_SHA = "2dc1fd7cda1262168cbdca4ca0773327e4153642c39a9981f3462dddad9aaccb"
CF1_SHA = "81e9849226029a1cb017c87da4202347be42dc92039db8c0d430d7115b68b4ed"
AC_GIT_BLOB = "f08f15c5049baf77771bed463a5119136566373b"
HISTORY_GIT_BLOB = "6b35ec8ae377a9dbdb778766756a32e8ad4bcbc8"
STOP = set(("the a an this that with into onto in on at to for and or from was were "
            "is are did does had have has her his their its she he they it there here "
            "after before then but as each every some now so could would should not no "
            "still again near over under because about toward while them").split())

def fail(reason: str) -> None:
    print("D1_FINGERPRINT_ONEPACKET=HOLD_" + reason)
    raise SystemExit(2)

def sha(raw: bytes) -> str:
    return hashlib.sha256(raw).hexdigest()

def git_blob(raw: bytes) -> str:
    header = ("blob " + str(len(raw)) + "\0").encode("ascii")
    return hashlib.sha1(header + raw).hexdigest()

def read_pinned(path: Path, sha256: str = "", git_sha1: str = "") -> tuple[dict, str]:
    if not path.is_file() or not path.resolve().is_relative_to(ROOT.resolve()):
        fail("SOURCE_NOT_FOUND_OR_OUTSIDE_PROJECT_" + path.name)
    raw = path.read_bytes()
    if sha256 and sha(raw) != sha256:
        fail("PINNED_SOURCE_SHA_MISMATCH_" + path.name)
    canonical = raw.replace(b"\r\n", b"\n")
    if git_sha1 and git_blob(raw) != git_sha1 and git_blob(canonical) != git_sha1:
        fail("GIT_BLOB_MISMATCH_" + path.name)
    try:
        obj = json.loads(raw.decode("utf-8-sig"))
    except (UnicodeDecodeError, ValueError):
        fail("SOURCE_JSON_INVALID_" + path.name)
    if not isinstance(obj, dict):
        fail("SOURCE_ROOT_INVALID_" + path.name)
    return obj, sha(raw)

def strict_text(value: object) -> str:
    if not isinstance(value, str) or not value.strip():
        fail("EMPTY_OR_NONSTRING_PROMPT")
    return value

def norm(value: str) -> str:
    return " ".join(value.split()).casefold()

def words(value: str) -> list[str]:
    return re.findall(r"[a-z]+", value.casefold())

def content_words(value: str) -> set[str]:
    return {w for w in words(value) if len(w) > 2 and w not in STOP}

def grams(value: str, n: int = 5) -> set[tuple[str,...]]:
    w = words(value)
    return {tuple(w[i:i + n]) for i in range(len(w) - n + 1)}

def add(records: list, label: str, rid: str, prompt: object) -> None:
    text = strict_text(prompt)
    records.append({"source": label, "id": str(rid), "text": text})

def source_records() -> tuple[list, list, dict]:
    d1, d1sha = read_pinned(DEV, sha256=D1_SHA)
    if d1.get("schema") != "ttm.small4m.d1.new_dev.private_stimulus.one_packet.v2":
        fail("D1_SCHEMA_MISMATCH")
    if any(len(d1.get(k, [])) != n for k, n in (
       ("families", 16), ("prompts", 128), ("neutral_prior_prompts", 64),
       ("blind_mapping_private", 512))):
        fail("D1_FROZEN_COUNTS_MISMATCH")

    prior, priorsha = read_pinned(S1, sha256=S1_SHA)
    cf, cfsha = read_pinned(CF1, sha256=CF1_SHA)
    history, historysha = read_pinned(HISTORY, git_sha1=HISTORY_GIT_BLOB)
    ac, acsha = read_pinned(AC, git_sha1=AC_GIT_BLOB)

    d1_records, source = [], []
    for row in d1["prompts"]:
        add(d1_records, "D1_DEV", row["id"], row["prompt_text"])
    for row in d1["neutral_prior_prompts"]:
        add(d1_records, "D1_NEUTRAL_PRIOR", row["id"], row["prompt_text"])

    if len(prior.get("records", [])) != 32:
        fail("FRESH16_S1_RECORD_COUNT")
    previous = sorted({strict_text(row["prompt_text"]) for row in prior["records"]})
    if len(previous) != 16:
        fail("FRESH16_UNIQUE_PROMPT_COUNT")
    for i, prompt in enumerate(previous):
        add(source, "FRESH16_USED", f"S1_{i:03d}", prompt)

    if len(cf.get("records", [])) != 36:
        fail("CF1_RECORD_COUNT")
    for i, row in enumerate(cf["records"]):
        for field in ("context_a", "context_b"):
            add(source, "CF1_DEV36", f"ROW_{i:03d}_{field}", row[field])

    if len(history.get("history", [])) != 28:
        fail("PUBLIC_HISTORY_RECORD_COUNT")
    for row in history["history"]:
        add(source, "Q1_FRESH12_PUBLIC", row["id"], row["text"])

    if len(ac.get("prompts", [])) != 36:
        fail("AC_SOURCE_RECORD_COUNT")
    ac_final, ac_dev = 0, 0
    for row in ac["prompts"]:
        if row.get("split") not in ("DEV", "BLIND_FINAL"):
            fail("AC_SPLIT_UNKNOWN")
        ac_final += row["split"] == "BLIND_FINAL"
        ac_dev += row["split"] == "DEV"
        # Exact UTF-8 source fingerprint is part of the frozen public manifest.
        if sha(strict_text(row["prompt"]).encode("utf-8")) != row["utf8_sha256"]:
            fail("AC_PER_PROMPT_SHA_MISMATCH")
        add(source, "AC_FINAL24" if row["split"] == "BLIND_FINAL" else "AC_DEV12",
            row["id"], row["prompt"])
    if (ac_final, ac_dev) != (24, 12):
        fail("AC_SPLIT_COUNT_MISMATCH")
    if len(d1_records) != 192 or len(source) != 152:
        fail("SOURCE_COLLECTION_COUNT_MISMATCH")
    pins = {
        "D1_DEV_V2_RAW_SHA256": d1sha,
        "FRESH16_S1_RAW_SHA256": priorsha,
        "CF1_MODEL_INPUT_RAW_SHA256": cfsha,
        "Q1_FRESH12_PUBLIC_RAW_SHA256": historysha,
        "AC_FROZEN_PUBLIC_RAW_SHA256": acsha
    }
    # Never touch d1["run_parameters"] or d1["blind_mapping_private"] values.
    return d1_records, source, pins

def main() -> None:
    if OUTPUT.exists():
        fail("ALREADY_EXISTS_NO_RECOMPUTE")
    if not TEMP.is_dir() or not ROOT.is_dir():
        fail("PROJECT_ROOT_NOT_FOUND")
    d1, prior, pins = source_records()
    normalized_d1 = {norm(q["text"]) for q in d1}
    # D1's frozen QA guarantees unique DEV strings, not unique neutral priors.
    # Record any cross-record equality, but do not invent a new admission gate.
    duplicate_normalized_in_d1 = len(d1) - len(normalized_d1)
    # Private hashes are held only locally. Never print texts, IDs or digests.
    index = {
        "schema": "ttm.d1.owner_private_fingerprint_index.v1",
        "source_sha256": pins,
        "records": [{
            "source": q["source"], "id": q["id"],
            "raw_utf8_sha256": sha(q["text"].encode("utf-8")),
            "normalized_sha256": sha(norm(q["text"]).encode("utf-8"))
        } for q in d1 + prior]
    }
    d1_structs = [(q, norm(q["text"]), content_words(q["text"]), grams(q["text"])) for q in d1]
    prior_structs = [(q, norm(q["text"]), content_words(q["text"]), grams(q["text"])) for q in prior]
    metrics = {}
    private_flags = []
    for group in sorted({q["source"] for q in prior}):
        group_inputs = [p for p in prior_structs if p[0]["source"] == group]
        counters = {
            "d1_records": len(d1), "historical_prompt_records": len(group_inputs),
            "comparisons": 0, "exact_normalized_matches": 0,
            "pairs_with_common_5gram": 0, "pairs_content_jaccard_ge_0_18": 0,
            "max_content_jaccard": 0.0
        }
        for dr, dn, dw, dg in d1_structs:
            for sr, sn, sw, sg in group_inputs:
                counters["comparisons"] += 1
                equal = dn == sn
                overlap5 = bool(dg & sg)
                inter = len(dw & sw)
                union = len(dw | sw)
                jacc = inter / union if union else 0.0
                counters["exact_normalized_matches"] += int(equal)
                counters["pairs_with_common_5gram"] += int(overlap5)
                counters["pairs_content_jaccard_ge_0_18"] += int(jacc >= 0.18)
                counters["max_content_jaccard"] = max(counters["max_content_jaccard"], jacc)
                if equal or overlap5 or jacc >= 0.18:
                    private_flags.append({
                        "d1_id": dr["id"], "historical_id": sr["id"],
                        "historical_source": group,
                        "exact": equal, "common_5gram": overlap5,
                        "jaccard": round(jacc, 6)
                    })
        counters["max_content_jaccard"] = round(counters["max_content_jaccard"], 6)
        metrics[group] = counters

    index["screening_flags"] = private_flags
    index["protected_sealed_sources"] = {
        "TEST": "NOT_READ_NO_ACCESS_IN_THIS_OPERATION",
        "Q1Q2_OTHER_THAN_APPROVED_PUBLIC_HISTORY": "NOT_READ_NO_ACCESS_IN_THIS_OPERATION"
    }
    private_blob = (json.dumps(index, sort_keys=True, ensure_ascii=True,
                separators=(",", ":")) + "\n").encode("ascii")
    safe = {
        "schema": "ttm.d1.fingerprint_static_onepacket_receipt.v1",
        "operation": "TTM_SMALL4M_D1_GENERATE_NEW_CANONICAL_FINGERPRINTS_OWNER_LOCAL_ONE_SHOT",
        "status": "PASS_SCOPED_SOURCE_FINGERPRINTS_ONLY",
        "source_sha256": pins,
        "private_fingerprint_index_sha256": sha(private_blob),
        "private_fingerprint_record_count": len(index["records"]),
        "d1_normalized_duplicate_record_count": duplicate_normalized_in_d1,
        "source_counts": {
            "D1_DEV": 128, "D1_NEUTRAL_PRIOR": 64,
            "FRESH16_USED": 16, "CF1_DEV36": 72, "Q1_FRESH12_PUBLIC": 28,
            "AC_FINAL24": 24, "AC_DEV12": 12
        },
        "comparisons": metrics,
        "private_flag_count": len(private_flags),
        "protected_TEST_Q1Q2": "NOT_READ_NOT_CERTIFIED",
        "full_semantic_nonoverlap": "NOT_CERTIFIED_BY_LEXICAL_HASH_SCREEN",
        "only_local_private_sha_and_counts_for_publication": True,
        "model_training_executed": False, "model_inference_executed": False,
        "blind_mapping_or_seeds_published": False,
        "science_release": "HOLD_PENDING_FROZEN_PREREG_NONOVERLAP_GOVERNANCE"
    }
    safe_blob = (json.dumps(safe, sort_keys=True, ensure_ascii=True,
                indent=2) + "\n").encode("ascii")
    OUTPUT.mkdir(parents=False, exist_ok=False)
    for name, body in (("D1_PRIVATE_FINGERPRINT_INDEX.json", private_blob),
                       ("D1_PUBLIC_SAFE_SUMMARY.json", safe_blob)):
        with (OUTPUT / name).open("xb") as file:
            file.write(body)
    print("D1_FINGERPRINT_ONEPACKET=PASS_SCOPED")
    print("D1_D1_RECORDS=192")
    print("D1_HISTORICAL_RECORDS=152")
    print("D1_PRIVATE_INDEX_SHA256=" + sha(private_blob))
    print("D1_SAFE_SUMMARY_SHA256=" + sha(safe_blob))
    print("D1_FULL_SEALED_NONOVERLAP=NOT_CERTIFIED")
    print("D1_SCIENCE_RELEASE=HOLD")

if __name__ == "__main__":
    main()
