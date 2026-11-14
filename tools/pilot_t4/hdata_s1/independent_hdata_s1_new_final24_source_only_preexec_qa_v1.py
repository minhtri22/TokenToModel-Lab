#!/usr/bin/env python3
"""Independent H-DATA-S1 source-only PREEXEC QA for NEW FINAL24 generation.
No Torch import, GPU, model forward, FINAL/private reads, scoring or unblind.
"""
import ast
import hashlib
import json
from pathlib import Path
import subprocess
import sys

ROOT = Path(__file__).resolve().parents[3]
HERE = Path(__file__).resolve().parent
SOURCE = HERE / "ttm_hdata_s1_new_final24_blind_generation_candidate_source_only_v1.py"
RUBRIC = ROOT / "docs/research/ttm-small4m-h-data-s1/TTM_HDATA_S1_BLIND_SCORING_AND_ADJUDICATION_CONTRACT_20261113.json"
COMMITMENT = ROOT / "docs/research/ttm-small4m-h-data-s1/TTM_HDATA_S1_NEW_FINAL24_PUBLIC_SHA_COMMITMENT_20261113.json"
READY = ROOT / "artifacts/qa/ttm-small4m-h-data-s1/science_postrun/TTM_HDATA_S1_INDEPENDENT_READY_LAST_VAL_FREEZE_20261114.json"
P02 = ROOT / "tools/pilot_t4/integrated/p02_source_exact.py"
BPE = ROOT / "tools/pilot_t4/integrated/source_t2/ttm_gpt2_bpe2048.py"

def need(ok, why):
    if not ok:
        raise RuntimeError("HDATA_S1_NEW_FINAL24_PREEXEC_HOLD:" + why)

def git_blob(path):
    raw = Path(path).read_bytes()
    return hashlib.sha1(b"blob " + str(len(raw)).encode() + b"\0" + raw).hexdigest()

def assert_qa():
    src = SOURCE.read_text(encoding="utf-8")
    tree = ast.parse(src)
    compile(src, str(SOURCE), "exec")
    funcs = {x.name:x for x in tree.body if isinstance(x,ast.FunctionDef)}
    needed = {"source_only","check_permit","generate_once","verify_private_prompts",
              "decrypt_private_mapping","validate_all_prompt_context","greedy64","write_new","main"}
    need(needed <= set(funcs), "GENERATOR_MISSING_FUNCTIONS")
    need("import torch" not in src[:src.index("def generate_once")], "TOPLEVEL_TORCH_IMPORT")
    main = funcs["main"]
    need("source-only" in src and 'default="source-only"' in src and
         "EXPLICIT_NEW_FINAL24_OWNER_PERMIT_NOT_SUPPLIED" in src,
         "FAIL_CLOSED_DEFAULT")
    front = src[src.index("def generate_once(args):"):src.index("    need(torch.cuda.is_available()",src.index("def generate_once(args):"))]
    need(front.index("check_permit(args, selfsha)") <
         front.index('os.environ["CUBLAS_WORKSPACE_CONFIG"] = ":4096:8"') <
         front.index("import torch"),
         "OWNER_PERMIT_BEFORE_EARLY_CUBLAS_CONFIG_BEFORE_TORCH")
    need('read_pinned(owner_path, FINAL_OWNER_SHA)' in src and
         "aes_source.validate_pairs" in src and
         "FINAL_ROOT.mkdir(exist_ok=False)" in src and
         'p.open("xb")' in src, "PRIVATE_AND_NO_OVERWRITE_GUARDS")
    need("prompt_context_gate = validate_all_prompt_context(prompts, bpe)" in src and
         "FINAL_CONTEXT_GUARD:" in src and
         src.index("prompt_context_gate = validate_all_prompt_context(prompts, bpe)") <
         src.index("FINAL_ROOT.mkdir(exist_ok=False)"),
         "ALL_FINAL_PROMPT_CONTEXT_MUST_PASS_BEFORE_FORWARD")
    need("torch.argmax(logits[0, -1, :])" in src and
         "MAX_NEW_TOKENS = 64" in src and
         "EOS_ID = 256" in src and
         "CONTEXT = 256" in src and
         "len(prefix) + MAX_NEW_TOKENS <= CONTEXT" in src and
         "bpe.decode(generated)" in src, "GREEDY64_EOS_BPE_SPEC")
    need("repetition_penalty" in src and
         "temperature" not in src.lower() and "top_k" not in src.lower(),
         "NO_ALTERNATIVE_DECODER")
    need(git_blob(P02) == "9762343e06cf800b50574c2871ae1ed58537fb18",
         "P02_SOURCE_BLOB")
    need(git_blob(BPE) == "fa5bd892941ba5aa6e6b2f0b2b0ae974efe297b6",
         "BPE_SOURCE_BLOB")

    result = subprocess.run([sys.executable, str(SOURCE), "--mode","source-only"],
                            text=True,capture_output=True,check=True,timeout=20)
    s = json.loads(result.stdout)
    need(s["status"] == "SOURCE_ONLY_FINAL_OWNER_RELEASE_NOT_GRANTED" and
         s["model_import_or_forward"] is False and s["aes_key_read"] is False and
         s["new_final_plaintext_read"] is False and s["optimizer_updates"] == 0 and
         s["generate_requires_owner_final_permit_sha256"] is True,
         "SOURCE_ONLY_EXECUTION_SCOPE")
    no_permit = subprocess.run([sys.executable,str(SOURCE),"--mode","generate"],
                               text=True,capture_output=True,check=False,timeout=20)
    need(no_permit.returncode != 0 and
         "EXPLICIT_NEW_FINAL24_OWNER_PERMIT_NOT_SUPPLIED" in no_permit.stderr,
         "GENERATE_WITHOUT_PERMIT_MUST_FAIL_BEFORE_MODEL_IMPORT")

    contract = json.loads(RUBRIC.read_text("utf8"))
    need(contract["run_id"] == s["run_id"] and
         contract["schema"] == "ttm.small4m.hdata_s1.scoring_protocol.v1" and
         contract["total_fields"] == "24 pairs x 2 sides x 5 axes = 240 integer judgments, plus 24 nonempty notes",
         "RUBRIC_LOCK")
    need([c["name"] for c in contract["primary_components"]] ==
         ["actor_retention","object_relation_retention","goal_or_rule_progress"] and
         [c["name"] for c in contract["secondary_scored_axes"]] ==
         ["coherence","consistency"],"FIVE_FIXED_AXES")
    p=contract["primary_gate"]
    need(p["H1_strict_pair_wins_at_least"] == 16 and
         p["mean_H1_minus_H0_at_least"] == .5 and
         p["bootstrap_resamples"] == 20000 and
         p["bootstrap_rng_seed"] == 20261113 and
         p["paired_bootstrap_CI95_lower_gt"] == 0, "FROZEN_SCORE_THRESHOLDS")

    c=json.loads(COMMITMENT.read_text("utf8"))
    entries=c["committed_prompt_hashes"]
    need(len(entries)==24 and [q["id"] for q in entries]==
         [f"HF{i:02d}" for i in range(1,25)] and
         len({q["prompt_utf8_sha256"] for q in entries})==24,
         "FROZEN_FINAL_PROMPT_SHA_CHAIN")
    from collections import Counter
    need(Counter(q["stratum"] for q in entries)==
         {"object_custody":6,"social_relation":6,
          "causal_obstacle":6,"temporal_rule":6}, "FINAL_STRATA")
    ready=json.loads(READY.read_text("utf8"))
    need(ready["status"].startswith("PASS_SCOPED_EXECUTION_AND_READY_LAST") and
         ready["matched_budget"]["total_updates"]==256 and
         ready["matched_budget"]["ready_count"]==8 and
         ready["custody"]["owner_receipt_sha256_verified_by_independent_local_hash"]==
         "e30a2281580b1f6ea33856577f0a244cd02e226dc8a3db00d207a8fe13cce4b5" and
         ready["val_comparison"]["val_guardrail"]=="PASS_NO_REGRESSION" and
         ready["adjudication"]["NEW_FINAL_inference"]=="NOT_EXECUTED",
         "SCIENCE_FREEZE_READBACK")
    return {
        "schema": "ttm.hdata_s1.final24_generation_source_only_independent_qa.v1",
        "status": "PASS_SOURCE_ONLY_CANDIDATE_WITHOUT_FINAL_OWNER_PERMIT",
        "candidate_git_blob_sha1": git_blob(SOURCE),
        "science_owner_readback_sha256":
            ready["custody"]["owner_receipt_sha256_verified_by_independent_local_hash"],
        "ready_count": ready["matched_budget"]["ready_count"],
        "train_updates_attested": ready["matched_budget"]["total_updates"],
        "frozen_prompt_hash_count": 24,
        "blind_axes_per_side": 5,
        "required_score_count": 240,
        "required_pair_notes": 24,
        "negative_missing_permit": "PASS_FAIL_CLOSED",
        "source_only_default": "PASS",
        "decoder_static": "PASS_GREEDY64_EOS_CONTEXT",
        "checkpoint_binary_or_private_final_read": False,
        "new_FINAL_inference_executed": False,
        "owner_FINAL_generation_permit": "NOT_GRANTED",
        "independent_dynamic_T4_FINAL_qa": "NOT_EXECUTED",
        "scientific_benefit": "PENDING",
    }

if __name__=="__main__":
    print(json.dumps(assert_qa(),ensure_ascii=False,sort_keys=True,indent=2))
