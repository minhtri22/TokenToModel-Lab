#!/usr/bin/env python3
"""TTM-Small-4M D1: distinct exploratory DEV32 CPU-only one-shot.

No TEST/Q1Q2, no optimizer, no GPU, no new scientific seed, no unblinding.
Owner output and 64-text blind packet stay private in project _tmp.
All important source and checkpoint hashes are checked before model work.
"""
from __future__ import annotations

import hashlib
import json
import math
import os
import sys
from collections import defaultdict
from pathlib import Path

ROOT = Path(r"D:\WORK\RESEARCH\TokenToModel-Lab")
TMP = ROOT / "_tmp"
SOURCE = TMP / "TTM_SMALL4M_D1_NEW_DEV_PRIVATE_V2_20261111.json"
CHECKPOINT = TMP / "CF1_STEP1024_PINNED.pt"
BPE = TMP / "ttm_t1_real_source_v1" / "T1_BPE2048_REAL_TRAIN_MANIFEST.json"
CF1 = TMP / "TTM_CF1_STEP1024_DEV36_ONE_SHOT_20261111"
P02 = CF1 / "transformer_core.py"
OUTPUT = TMP / "TTM_D1_EXPLORATORY_DEV32_ONE_SHOT_20261112"
D1_SHA = "f381ae8ab9c67c8590092f85445ab2fbe95a3b1c6a646ec18ee26b6b13ac92b8"
CHECKPOINT_SHA = "cb985751795c8328ad65acf7ca4c1033ce35182c1bfbdb8c38550de629cb271b"
BPE_SHA = "cba18e60cee3d08a353ee6d4a451017289e45af7b4b1179c87171b9b78d7dfdc"
FINGERPRINT_SHA = "66a987550fdeb5b6ff3711d49ab673578be68418a1978b33126f6127deed763c"
EXP_OPERATION = "TTM_SMALL4M_D1_POST_FINGERPRINT_EXPLORATORY_DEV32_ONE_SHOT"
CATEGORIES = ("entity_location", "causal_reasoning", "rule_constraint", "goal_persistence")
MAX_NEW = 32
EOS = 256

def fatal(why: str) -> None:
    print("D1_EXPLORATORY_DEV32=HOLD_" + why)
    raise SystemExit(2)

def sha(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()

def sha_file(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as f:
        for piece in iter(lambda: f.read(1 << 20), b""):
            h.update(piece)
    return h.hexdigest()

def canonical_json(obj: object) -> bytes:
    return (json.dumps(obj, sort_keys=True, ensure_ascii=True,
                       separators=(",", ":"), allow_nan=False) + "\n").encode("ascii")

def read_frozen(path: Path, expected: str) -> dict:
    if not path.is_file() or path.is_symlink() or not path.resolve().is_relative_to(ROOT.resolve()):
        fatal("FROZEN_SOURCE_MISSING_OR_LINK_" + path.name)
    if sha_file(path) != expected:
        fatal("FROZEN_INPUT_SHA_MISMATCH_" + path.name)
    obj = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(obj, dict):
        fatal("BAD_ROOT_JSON_" + path.name)
    return obj

def encode_decoding_table(bpe_manifest: dict) -> tuple[bytes, ...]:
    pairs = bpe_manifest.get("pair_ids")
    if not isinstance(pairs, list) or len(pairs) != 1791:
        fatal("BAD_BPE_PAIR_COUNT")
    tokens = [bytes([i]) for i in range(256)] + [b""]
    for j, pair in enumerate(pairs):
        if (not isinstance(pair, list) or len(pair) != 2 or
                any(type(i) is not int or i < 0 or i >= 257 + j for i in pair)):
            fatal("BAD_BPE_PAIR_" + str(j))
        tokens.append(tokens[pair[0]] + tokens[pair[1]])
    if len(tokens) != 2048:
        fatal("BAD_BPE_VOCAB_LENGTH")
    return tuple(tokens)

def select_records(d1: dict) -> tuple[list[dict], list[dict], dict]:
    if d1.get("schema") != "ttm.small4m.d1.new_dev.private_stimulus.one_packet.v2":
        fatal("D1_V2_SCHEMA_MISMATCH")
    if tuple(len(d1.get(k, [])) for k in
             ("families", "prompts", "neutral_prior_prompts", "blind_mapping_private")) != (16, 128, 64, 512):
        fatal("D1_SOURCE_COUNTS_MISMATCH")
    fam = {r["id"]: r for r in d1["families"]}
    if len(fam) != 16:
        fatal("D1_FAMILY_IDS_INVALID")
    chosen = [p for p in d1["prompts"]
              if p.get("length") == "short" and p.get("distance") == "near"]
    chosen.sort(key=lambda r: (r["family_id"], r["condition"]))
    if len(chosen) != 32:
        fatal("DEV32_SELECTION_SIZE")
    if any(p["condition"] not in ("A", "B") for p in chosen):
        fatal("UNKNOWN_CONDITION")
    for fid in fam:
        if [(r["condition"]) for r in chosen if r["family_id"] == fid] != ["A", "B"]:
            fatal("DEV_PAIR_MISSING_" + fid)
    neutral = [p for p in d1["neutral_prior_prompts"]
               if p.get("length") == "short" and p.get("distance") == "near"]
    if len(neutral) != 16 or len({p["family_id"] for p in neutral}) != 16:
        fatal("NEUTRAL16_SELECTION_INVALID")
    neutral.sort(key=lambda r: r["family_id"])
    options = [x for x in d1["run_parameters"]["decode"]
               if x.get("method") == "nucleus"]
    if len(options) != 1 or options[0].get("top_p") != 0.9 or options[0].get("temperature") != 0.8:
        fatal("FROZEN_NUCLEUS_SPEC_MISMATCH")
    frozen_seeds = options[0].get("seeds", [])
    if len(frozen_seeds) != 3 or any(type(x) is not int for x in frozen_seeds):
        fatal("FROZEN_SEED_SET_INVALID")
    return chosen, neutral, {"families": fam, "frozen_nucleus_seed": frozen_seeds[0]}

def logits_step(model, ids: list[int]):
    import torch
    if not 1 <= len(ids) <= 256:
        fatal("CONTEXT_OVERFLOW_IN_GENERATION")
    inp = torch.tensor([ids], dtype=torch.long, device="cpu")
    result = model(inp)
    value = result[0] if isinstance(result, (tuple, list)) else result
    if value.ndim != 3 or value.shape != (1, len(ids), 2048):
        fatal("UNEXPECTED_MODEL_LOGITS_SHAPE")
    last = value[0, -1].float()
    if not torch.isfinite(last).all():
        fatal("NONFINITE_OUTPUT_LOGITS")
    return last

def generate(model, prompt_ids: list[int], method: str, rng, table: tuple[bytes, ...]) -> dict:
    import torch
    new: list[int] = []
    stopped = False
    with torch.inference_mode():
        for _ in range(MAX_NEW):
            logits = logits_step(model, prompt_ids + new)
            if method == "GREEDY":
                token = int(torch.argmax(logits).item())
            elif method == "NUCLEUS":
                probs = torch.softmax(logits / 0.8, dim=-1)
                p, idx = torch.sort(probs, descending=True)
                # Keep the probability mass up to and including the p=0.9 crossing item.
                keep = (torch.cumsum(p, 0) - p) < 0.9
                p = p * keep
                p = p / p.sum()
                selected = int(torch.multinomial(p, 1, generator=rng).item())
                token = int(idx[selected].item())
            else:
                fatal("BAD_DECODER_NAME")
            if token == EOS:
                stopped = True
                break
            if not 0 <= token < 2048:
                fatal("TOKEN_OUT_OF_VOCAB")
            new.append(token)
    raw_text = b"".join(table[i] for i in new).decode("utf-8", errors="replace")
    triples = [tuple(new[i:i+3]) for i in range(len(new)-2)]
    return {
        "generated_text_only": raw_text, "generated_tokens": len(new),
        "eos_early": stopped,
        "repeated_trigram_windows": len(triples) - len(set(triples)),
        "token_ids_sha256": sha(json.dumps(new, separators=(",", ":")).encode("ascii"))
    }

def write_new(directory: Path, name: str, content: bytes) -> None:
    if not directory.is_dir() or directory.is_symlink():
        fatal("UNEXPECTED_OUTPUT_DIRECTORY")
    with (directory / name).open("xb") as output:
        output.write(content)
        output.flush()
        os.fsync(output.fileno())

def main() -> None:
    if sys.version_info[:2] != (3, 12):
        fatal("PYTHON312_REQUIRED")
    if OUTPUT.exists():
        fatal("OUTPUT_EXISTS_NO_REEXECUTION")
    if any(p.is_symlink() for p in (ROOT, TMP, CF1, SOURCE, CHECKPOINT, BPE)):
        fatal("SYMLINK_SOURCE_NOT_ALLOWED")
    if not ROOT.is_dir() or not TMP.is_dir() or not CF1.is_dir():
        fatal("EXPECTED_TTM_RUNTIME_MISSING")
    # Fail before inference if source custody and machine environment differ.
    d1 = read_frozen(SOURCE, D1_SHA)
    read_frozen(BPE, BPE_SHA)
    if sha_file(CHECKPOINT) != CHECKPOINT_SHA:
        fatal("FROZEN_CHECKPOINT_SHA_MISMATCH")
    if not (TMP / "TTM_D1_ONEPACKET_FINGERPRINT_20261112" / "D1_PRIVATE_FINGERPRINT_INDEX.json").is_file():
        fatal("PRIOR_FINGERPRINT_INDEX_MISSING")
    if sha_file(TMP / "TTM_D1_ONEPACKET_FINGERPRINT_20261112" /
                "D1_PRIVATE_FINGERPRINT_INDEX.json") != FINGERPRINT_SHA:
        fatal("PRIOR_FINGERPRINT_INDEX_SHA_MISMATCH")
    # Do not inspect protected TEST/Q1Q2, raw previous generations or private mappings.
    selected, neutral, scope = select_records(d1)
    import torch
    if torch.cuda.is_available():
        # CPU is enforced regardless of availability; never call .cuda().
        pass
    torch.set_num_threads(2)
    sys.path.insert(0, str(CF1))
    from cf1_exact_t1_bpe import PinnedT1BPE
    from cf1_teacher_forced_scorer import (
        length_and_prefix_check, load_frozen_p02, mean_teacher_forced_logprob)
    tok = PinnedT1BPE(BPE)
    # Every teacher-forced candidate must have the exact prefix continuation boundary.
    fam = scope["families"]
    by_family = {}
    neu = {r["family_id"]: r for r in neutral}
    for p in selected:
        by_family.setdefault(p["family_id"], {})[p["condition"]] = p
    for fid in sorted(fam):
        f = fam[fid]
        for context in (by_family[fid]["A"]["prompt_text"],
                        by_family[fid]["B"]["prompt_text"], neu[fid]["prompt_text"]):
            for answer in (f["continuation_A"], f["continuation_B"]):
                length_and_prefix_check(tok.encode, context, answer)
        for cond in ("A", "B"):
            ids = list(tok.encode(by_family[fid][cond]["prompt_text"]))
            if not 1 <= len(ids) <= 192 or len(ids) + MAX_NEW > 256:
                fatal("PROMPT_BPE_OR_GENERATION_CONTEXT_OVERFLOW")
    manifest = json.loads(BPE.read_text(encoding="utf-8"))
    table = encode_decoding_table(manifest)
    model = load_frozen_p02(P02, CHECKPOINT)
    if model.training or any(p.requires_grad for p in model.parameters()):
        fatal("MODEL_NOT_FROZEN_EVAL")
    # 96 answer-only candidate log-probability calls.
    preference = []
    for fid in sorted(fam):
        f = fam[fid]
        a, b = by_family[fid]["A"]["prompt_text"], by_family[fid]["B"]["prompt_text"]
        x0 = neu[fid]["prompt_text"]
        ya, yb = f["continuation_A"], f["continuation_B"]
        def lp(x, y):
            value, length = mean_teacher_forced_logprob(model, tok.encode, x, y)
            return value
        laa, lab = lp(a, ya), lp(a, yb)
        lba, lbb = lp(b, ya), lp(b, yb)
        l0a, l0b = lp(x0, ya), lp(x0, yb)
        ma, mb, d0 = laa-lab, lbb-lba, l0a-l0b
        preference.append({
            "family_id": fid, "category": f["category"],
            "mA": ma, "mB": mb, "prior_d0": d0,
            "mA_prior_adjusted": ma-d0, "mB_prior_adjusted": mb+d0,
            "switch": bool(ma > 0 and mb > 0),
            "switch_prior_adjusted": bool(ma-d0 > 0 and mb+d0 > 0),
        })
    if len(preference) != 16:
        fatal("PREFERENCE_FAMILY_COUNT_MISMATCH")
    # Frozen seed: first of the 3 in private V2; use it once, no new seeds.
    rng = torch.Generator(device="cpu")
    rng.manual_seed(scope["frozen_nucleus_seed"])
    rollouts = []
    for cond in selected:
        ids = list(tok.encode(cond["prompt_text"]))
        for mode in ("GREEDY", "NUCLEUS"):
            result = generate(model, ids, mode, rng, table)
            rollouts.append({
                "family_id": cond["family_id"],
                "condition": cond["condition"],
                "prompt_id": cond["id"],
                "decoder": mode,
                "prompt_text": cond["prompt_text"],
                **result
            })
    if len(rollouts) != 64:
        fatal("EXPECTED_64_GENERATED_TEXTS")
    blinded = []
    for seq, row in enumerate(rollouts):
        opaque_id = sha((D1_SHA + ":" + str(seq) + ":EXP32").encode("ascii"))[:20]
        blinded.append({
            "opaque_id": opaque_id,
            "prompt_text": row["prompt_text"],
            "generated_text_only": row["generated_text_only"]
        })
    blinded.sort(key=lambda q: sha(("BLIND_ORDER_" + q["opaque_id"]).encode("ascii")))
    if len({p["opaque_id"] for p in blinded}) != 64:
        fatal("BLIND_ID_COLLISION")
    by_category = defaultdict(list)
    for p in preference:
        by_category[p["category"]].append(p)
    if set(by_category) != set(CATEGORIES):
        fatal("CATEGORY_COVERAGE_MISMATCH")
    tf_aggregate = {
        "teacher_forced_candidate_calls": 96,
        "both_positive_family_count": sum(p["switch"] for p in preference),
        "both_positive_prior_adjusted_family_count": sum(p["switch_prior_adjusted"] for p in preference),
        "mean_margin_A": sum(p["mA"] for p in preference) / 16,
        "mean_margin_B": sum(p["mB"] for p in preference) / 16,
        "mean_margin_prior_adjusted_A": sum(p["mA_prior_adjusted"] for p in preference) / 16,
        "mean_margin_prior_adjusted_B": sum(p["mB_prior_adjusted"] for p in preference) / 16,
        "by_category": {
            k: {
                "families": len(v),
                "both_positive": sum(z["switch"] for z in v),
                "both_positive_adjusted": sum(z["switch_prior_adjusted"] for z in v)
            } for k,v in sorted(by_category.items())
        }
    }
    roll_aggregate = {}
    for mode in ("GREEDY", "NUCLEUS"):
        x = [r for r in rollouts if r["decoder"] == mode]
        roll_aggregate[mode] = {
            "count": len(x),
            "eos_early_count": sum(r["eos_early"] for r in x),
            "empty_text_count": sum(not r["generated_text_only"].strip() for r in x),
            "mean_new_tokens": sum(r["generated_tokens"] for r in x) / len(x),
            "total_repeated_trigram_windows": sum(r["repeated_trigram_windows"] for r in x),
            "max_new_tokens": MAX_NEW
        }
    owner = {
        "schema": "ttm.d1.exploratory_dev32.owner_private_raw.v1",
        "operation": EXP_OPERATION,
        "source_dev_sha256": D1_SHA,
        "source_fingerprint_private_index_sha256": FINGERPRINT_SHA,
        "checkpoint_sha256": CHECKPOINT_SHA,
        "bpe_sha256": BPE_SHA,
        "preference": preference,
        "outputs": rollouts,
        "seed_policy": "FIRST_FROZEN_NUCLEUS_SEED_FROM_V2_ONLY",
        "frozen_seed_used_owner_private": scope["frozen_nucleus_seed"],
        "optimizer_updates": 0,
        "gpu_calls": 0,
        "test_q1q2_read": False,
        "confirmatory_512_science": "NOT_EXECUTED"
    }
    blind = {
        "schema": "ttm.d1.exploratory_dev32.blind64.v1",
        "operation": EXP_OPERATION,
        "records": blinded,
        "rubric": ["adherence_0_to_3", "first_event_fact_match",
                   "goal_retention", "serious_contradiction", "notes"],
        "independence": "INDEPENDENT_NEW_CHAT_NOT_YET_SCORED"
    }
    private_bytes = canonical_json(owner)
    blind_bytes = canonical_json(blind)
    safe = {
        "schema": "ttm.d1.exploratory_dev32.safe_summary.v1",
        "operation": EXP_OPERATION, "status": "EXECUTED_EXPLORATORY_DEV_ONLY_NOT_ADJUDICATED",
        "source_dev_sha256": D1_SHA,
        "source_fingerprint_index_sha256": FINGERPRINT_SHA,
        "checkpoint_sha256": CHECKPOINT_SHA, "bpe_manifest_sha256": BPE_SHA,
        "selected_prompt_count": 32, "selected_family_count": 16,
        "neutral_prompt_count": 16, "teacher_forced": tf_aggregate,
        "rollout": roll_aggregate, "blind_texts_expected": 64,
        "blind_texts_generated": len(blinded),
        "raw_owner_sha256": sha(private_bytes), "blind_packet_sha256": sha(blind_bytes),
        "blind_rater_scored": 0,
        "no_new_train_steps": True, "GPU_calls": 0,
        "TEST_Q1Q2_access": "NONE", "seed_source": "FIRST_PREEXISTING_FROZEN_V2_SEED",
        "confirmatory_D1_512": "NOT_AUTHORIZED_NO_EXECUTION",
        "scientific_scope": "EXPLORATORY_SCOPED_SHORT_NEAR_ONE_NUCLEUS_SEED",
        "scientific_verdict": "PENDING_INDEPENDENT_BLIND64_SCORES",
    }
    safe_bytes = canonical_json(safe)
    # Only create files after all checks and the real evaluation have succeeded.
    OUTPUT.mkdir(parents=False, exist_ok=False)
    write_new(OUTPUT, "D1_EXP32_OWNER_PRIVATE_RAW.json", private_bytes)
    write_new(OUTPUT, "D1_EXP32_BLIND64_PRIVATE.json", blind_bytes)
    write_new(OUTPUT, "D1_EXP32_SAFE_SUMMARY.json", safe_bytes)
    print("TTM_D1_EXP32_CPU_SCIENCE=EXECUTED_EXPLORATORY_ONLY")
    print("D1_EXP32_TEACHER_FORCED=96")
    print("D1_EXP32_OUTPUTS=64")
    print("D1_EXP32_BLIND64_SHA256=" + sha(blind_bytes))
    print("D1_EXP32_OWNER_RAW_SHA256=" + sha(private_bytes))
    print("D1_EXP32_SAFE_SHA256=" + sha(safe_bytes))
    print("D1_EXP32_BOTH_POSITIVE=" + str(tf_aggregate["both_positive_family_count"]))
    print("D1_EXP32_BOTH_POSITIVE_ADJUSTED=" + str(tf_aggregate["both_positive_prior_adjusted_family_count"]))
    print("D1_EXP32_TEST_Q1Q2=SEALED")
    print("D1_EXP32_INDEPENDENT_RATER=PENDING")
    print("D1_EXP32_CONFIRMATORY_512=HOLD")

if __name__ == "__main__":
    try:
        main()
    except SystemExit:
        raise
    except Exception as exc:
        fatal("EXECUTION_OR_PREFLIGHT_" + type(exc).__name__ + "_" + str(exc)[:130])
