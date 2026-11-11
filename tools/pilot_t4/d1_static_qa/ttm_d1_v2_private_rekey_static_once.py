#!/usr/bin/env python3
"""TTM D1 single versioned private rekey+static QA. NO model load/inference/training/TEST."""
from __future__ import annotations
import collections
import hashlib
import importlib.util
import json
import pathlib
import re
import secrets
import sys

ROOT = pathlib.Path(r"D:\WORK\RESEARCH\TokenToModel-Lab")
TEMP = ROOT / "_tmp"
OLD = TEMP / "TTM_SMALL4M_D1_NEW_DEV_PRIVATE_20261111.json"
NEW = TEMP / "TTM_SMALL4M_D1_NEW_DEV_PRIVATE_V2_20261111.json"
SCORER = TEMP / "TTM_SMALL4M_D1_BLIND_RATER_TEMPLATE_V2_20261111.json"
RECEIPT = TEMP / "TTM_SMALL4M_D1_V2_VERSIONED_PRIVATE_REKEY_STATIC_RECEIPT_20261111.json"
BPE = TEMP / "ttm_t1_real_source_v1" / "T1_BPE2048_REAL_TRAIN_MANIFEST.json"
SRC = ROOT / "worktrees" / "ttm-fresh16-quality-20261111" / "tools" / "pilot_t4" / "integrated" / "source_t2" / "ttm_gpt2_bpe2048.py"
PUBLIC = (
    ROOT / "worktrees" / "ttm-fresh16-quality-20261111" / "artifacts" / "research" / "ttm-small4m-quality-gap" / "TTM_FRESH_CONTINUATION_PROMPT_SET_CANDIDATE_V1_20261111.json",
    ROOT / "worktrees" / "ttm-fresh16-quality-20261111" / "artifacts" / "research" / "ttm-small4m-quality-gap" / "TTM_FRESH16_ALLOWED_PUBLIC_HISTORICAL_PROMPTS_20261111.json"
)
OLD_RAW = "c43dde98c4fd2328ece9baba549c8bbc369964f0d19d4ecd9f8bb081d3256957"
OLD_LF = "de5c0acae9a863e255922963d9644623ff6b1cbfedc0ff9edd7d8225cbac7603"
BPE_RAW = "cba18e60cee3d08a353ee6d4a451017289e45af7b4b1179c87171b9b78d7dfdc"
BPE_INTERNAL = "6da22cf79c3a6cfd08d80a768eb1074125a753164ccf62a164e79545956e94c6"
CATEGORIES = ("entity_location", "causal_reasoning", "rule_constraint", "goal_persistence")

def sha(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()

def stop(msg: str) -> None:
    raise RuntimeError("D1_FAIL_CLOSED:" + msg)

def flatten(v: object):
    if isinstance(v, dict):
        for x in v.values():
            yield from flatten(x)
    elif isinstance(v, list):
        for x in v:
            yield from flatten(x)
    elif isinstance(v, str) and 20 < len(v) < 1500:
        yield v

def shingles(t: str):
    words = re.findall(r"[a-z0-9]+", t.casefold())
    return set(zip(*(words[i:] for i in range(5)))) if len(words) >= 5 else set()

def json_crlf(obj: object) -> bytes:
    return (json.dumps(obj, indent=2, ensure_ascii=True) + "\n").replace("\n", "\r\n").encode("ascii")

def main() -> None:
    if not ROOT.is_dir() or not TEMP.is_dir():
        stop("PROJECT_ROOT_MISSING")
    if ROOT.is_symlink() or TEMP.is_symlink() or any(p.exists() or p.is_symlink() for p in (NEW, SCORER, RECEIPT)):
        stop("SCOPED_DEST_EXISTS_OR_LINKED_NO_OVERWRITE")
    if not all(p.is_file() and not p.is_symlink() for p in (OLD, BPE, SRC)):
        stop("SOURCE_MISSING_OR_SYMLINK")
    raw = OLD.read_bytes()
    if len(raw) != 266415 or sha(raw) != OLD_RAW or sha(raw.replace(b"\r\n", b"\n")) != OLD_LF:
        stop("FROZEN_V1_RAW_OR_LF_SHA_MISMATCH")
    old = json.loads(raw.decode("utf-8"))
    if not (len(old["families"]) == 16 and len(old["prompts"]) == 128
            and len(old["neutral_prior_prompts"]) == 64 and len(old["blind_mapping_private"]) == 512):
        stop("FROZEN_V1_COUNT_MISMATCH")
    if old["quality_summary"]["issue_count"] != 0:
        stop("FROZEN_V1_GENERATOR_QA_FAILED")
    bpe_bytes = BPE.read_bytes()
    if sha(bpe_bytes) != BPE_RAW:
        stop("FROZEN_T1_BPE_RAW_SHA_MISMATCH")
    sp = importlib.util.spec_from_file_location("ttm_d1_v2_pinned_bpe", SRC)
    if sp is None or sp.loader is None:
        stop("EXACT_BPE_SOURCE_IMPORT_MISSING")
    module = importlib.util.module_from_spec(sp)
    sys.modules[sp.name] = module
    sp.loader.exec_module(module)
    tokenizer = module.BPE2048.from_manifest(json.loads(bpe_bytes.decode("utf-8")))
    if tokenizer.manifest()["manifest_sha256"] != BPE_INTERNAL:
        stop("FROZEN_T1_BPE_INTERNAL_SHA_MISMATCH")
    enc = tokenizer.encode
    # One-shot design invariant: no prompt/candidate/neutral data changes during rekey.
    original_text_obj = json.dumps({
        "families": old["families"], "prompts": old["prompts"],
        "neutral": old["neutral_prior_prompts"]}, sort_keys=True, ensure_ascii=True)
    decodes = [d for d in old["run_parameters"]["decode"] if d["method"] == "nucleus"]
    if len(decodes) != 1:
        stop("NUCLEUS_SPEC_MISMATCH")
    before = decodes[0].get("seeds")
    if type(before) is not list or len(before) != 3 or len(set(before)) != 3:
        stop("OLD_SEED_COUNT_INVALID")
    new_seeds = []
    while len(new_seeds) < 3:
        s = secrets.randbelow(2_000_000_000) + 10_000_000
        if s not in new_seeds and s not in before:
            new_seeds.append(s)
    seed_change = dict(zip(before, new_seeds))
    decodes[0]["seeds"] = new_seeds
    shuffled = list(range(1, 513))
    secrets.SystemRandom().shuffle(shuffled)
    for i, rec in enumerate(old["blind_mapping_private"]):
        old_value = rec["seed"]
        if old_value is not None:
            if old_value not in seed_change or rec["decoder"] != "NUCLEUS":
                stop("OLD_MAP_INVALID_SEED_OR_DECODER")
            rec["seed"] = seed_change[old_value]
        elif rec["decoder"] != "GREEDY":
            stop("OLD_GREEDY_SEED_INVALID")
        rec["blind_id"] = "D1V2B" + str(shuffled[i]).zfill(4)
    old["schema"] = "ttm.small4m.d1.new_dev.private_stimulus.one_packet.v2"
    old["version"] = 2
    old["supersedes_raw_sha256"] = OLD_RAW
    old["seed_rekey_reason"] = "OLD_VALUES_DISCLOSED_IN_PUBLIC_QA_SOURCE_BEFORE_SCIENCE"
    old["seed_custody"] = "V2_NEW_SECRETS_STORED_ONLY_IN_PRIVATE_PACKET"
    old["source_rights"] = "AI_AUTHORED_NEW_CONTENT_OWNER_FINAL_ATTESTATION_PENDING"
    old["historical_overlap"] = "PUBLIC_TWO_FILES_SCOPED_PRIVATE_FRESH16_AC_Q1Q2_TEST_NOT_CERTIFIED"
    old["rater_assigned"] = False
    old["execution"] = "NOT_AUTHORIZED_NO_INFERENCE_NO_TRAINING"
    if json.dumps({
        "families": old["families"], "prompts": old["prompts"],
        "neutral": old["neutral_prior_prompts"]}, sort_keys=True, ensure_ascii=True) != original_text_obj:
        stop("STIMULUS_CHANGED_DURING_REKEY")
    family = {x["id"]:x for x in old["families"]}
    if len(family) != 16 or any(sum(x["category"] == cat for x in family.values()) != 4 for cat in CATEGORIES):
        stop("FAMILY_BALANCE_FAILURE")
    for f in family.values():
        if len(enc(f["fact_A"])) != len(enc(f["fact_B"])):
            stop("FACT_BPE_BALANCE_" + f["id"])
        na,nb = len(enc(f["continuation_A"])),len(enc(f["continuation_B"]))
        if not 3 <= na == nb <= 12:
            stop("CONTINUATION_BPE_BALANCE_" + f["id"])
    prompts = {r["id"]:r for r in old["prompts"]}
    if len(prompts) != 128 or len({r["prompt_text"] for r in prompts.values()}) != 128:
        stop("PROMPT_DUPLICATE")
    per_family = collections.Counter()
    for rec in prompts.values():
        fid = rec["family_id"]
        if fid not in family:
            stop("UNKNOWN_FAMILY")
        per_family[fid] += 1
        text = rec["prompt_text"]
        n = len(enc(text))
        if n != rec["prompt_bpe"] or n + 64 > 256:
            stop("BPE_PROMPT_OR_CONTEXT")
        if rec["length"] == "short":
            low, high = 64, 96
        else:
            low, high = 160, 192
        if not low <= n <= high or text.endswith(" "):
            stop("LENGTH_OR_TRAILING_SPACE")
        fact = family[fid]["fact_A" if rec["condition"] == "A" else "fact_B"]
        if text.count(fact) != 1:
            stop("FACT_MISSING_OR_REPEATED")
        end = text.index(fact) + len(fact)
        cue_pos = len(enc(text[:end]))
        distance = n-cue_pos
        if distance != rec["cue_distance_bpe"] or cue_pos != rec["fact_end_bpe"]:
            stop("CUE_BPE_DISTANCE_MISMATCH")
        limits = (16,32) if rec["distance"] == "near" else ((48,64) if rec["length"] == "short" else (144,160))
        if not limits[0] <= distance <= limits[1]:
            stop("CUE_DISTANCE_OUTSIDE_FROZEN")
        if rec["candidate_A"] != family[fid]["continuation_A"] or rec["candidate_B"] != family[fid]["continuation_B"]:
            stop("CANDIDATE_CHANGED")
    if any(per_family[fid] != 8 for fid in family):
        stop("FAMILY_8_PROMPTS_INCOMPLETE")
    prior = {r["id"]:r for r in old["neutral_prior_prompts"]}
    if len(prior) != 64:
        stop("PRIOR_ID_DUPLICATE")
    for rec in prompts.values():
        p = prior.get(rec["neutral_prompt_id"])
        if p is None or p["family_id"] != rec["family_id"] or p["length"] != rec["length"] or p["distance"] != rec["distance"]:
            stop("PRIOR_ALIGNMENT_FAIL")
    for rec in prior.values():
        if len(enc(rec["prompt_text"])) != rec["prompt_bpe"]:
            stop("PRIOR_BPE_MISMATCH")
        f = family[rec["family_id"]]
        if f["fact_A"] in rec["prompt_text"] or f["fact_B"] in rec["prompt_text"]:
            stop("PRIOR_FACT_LEAK")
    blind = old["blind_mapping_private"]
    if len({r["blind_id"] for r in blind}) != 512:
        stop("BLIND_ID_COLLISION")
    decoded = collections.defaultdict(list)
    for r in blind:
        if r["prompt_id"] not in prompts:
            stop("UNKNOWN_BLIND_PROMPT")
        decoded[r["prompt_id"]].append((r["decoder"], r["seed"]))
    expected = {("GREEDY",None)} | {("NUCLEUS",s) for s in new_seeds}
    if any(set(decoded[pid]) != expected or len(decoded[pid]) != 4 for pid in prompts):
        stop("BLIND_4_WAY_COVERAGE_FAILURE")
    if any(sum(f["candidate_order_in_manifest"] == "A_then_B" for f in family.values() if f["category"] == cat) != 2 for cat in CATEGORIES):
        stop("CANDIDATE_ORDER_BALANCE_FAILURE")
    def public_strings(obj):
        return list(flatten(obj))
    old_public = []
    for path in PUBLIC:
        if not path.is_file():
            stop("PUBLIC_HISTORY_SOURCE_MISSING")
        old_public.extend(public_strings(json.loads(path.read_text(encoding="utf-8"))))
    overlap = []
    for f in family.values():
        a = shingles(f["scene"])
        for t in old_public:
            b = shingles(t)
            j = len(a & b) / len(a | b) if a and b else 0
            if f["scene"] in t or j >= 0.85:
                overlap.append(f["id"])
                break
    if overlap:
        stop("PUBLIC_HISTORY_SCENE_OVERLAP_" + ",".join(overlap))
    # Rater material is stripped of truth, decoder, seed, candidate and prompt IDs.
    scorer = {
        "schema":"ttm.small4m.d1.blind_rater_template.private.v2",
        "date":"2026-11-11",
        "status":"TEMPLATE_ONLY_RATER_UNASSIGNED_NO_OUTPUTS",
        "rubric":{"0":"No scorable event","1":"Event not grounded in fact",
                  "2":"First event and roles match fact","3":"Correct and goal persists"},
        "records":[{"blind_id":r["blind_id"],"prompt_text":prompts[r["prompt_id"]]["prompt_text"],
                    "generated_text":None,"adherence_0_to_3":None,"first_event_fact_match":None,
                    "goal_retention":None,"serious_contradiction":None,"notes":None} for r in blind]
    }
    # Randomize scorer-facing record order separately from private mapping order.
    secrets.SystemRandom().shuffle(scorer["records"])
    scorer_blob = json_crlf(scorer)
    forbidden = (b'"decoder"',b'"seed"',b'"truth"',b'"prompt_id"',b'"condition"',b'"candidate_A"',b'"candidate_B"')
    if any(k in scorer_blob for k in forbidden):
        stop("BLIND_SCORER_TEMPLATE_SECRET_LEAK")
    raw_v2 = json_crlf(old)
    if any(str(s).encode("ascii") in raw_v2 for s in before):
        stop("DISCLOSED_SEED_STILL_PRESENT")
    # Output all files no-overwrite, within project only. No result is evidence of science.
    with NEW.open("xb") as f:
        f.write(raw_v2);f.flush()
    with SCORER.open("xb") as f:
        f.write(scorer_blob);f.flush()
    if NEW.read_bytes() != raw_v2 or SCORER.read_bytes() != scorer_blob:
        stop("RAW_READBACK_MISMATCH")
    lines = raw_v2.replace(b"\r\n",b"\n")
    report = {
        "schema":"ttm.small4m.d1.versioned_private_seed_rekey_static_qa_receipt.v1",
        "operation":"TTM_SMALL4M_D1_VERSIONED_PRIVATE_SEED_REKEY_OVERLAP_CUSTODY_AND_SINGLE_OWNER_RELEASE_GO_HOLD_NO_SCIENCE",
        "date":"2026-11-11",
        "previous_v1_raw_sha256":OLD_RAW,
        "new_private_v2_raw_sha256":sha(raw_v2),
        "new_private_v2_raw_bytes":len(raw_v2),
        "new_private_v2_lf_sha256":sha(lines),
        "scorer_template_raw_sha256":sha(scorer_blob),
        "scorer_template_raw_bytes":len(scorer_blob),
        "families":16,"prompts":128,"neutral_prior":64,"blinded_future_outputs":512,
        "new_seed_count":3,"old_seed_reuse_count":0,"blind_id_unique_count":512,
        "content_stimuli_unchanged":True,
        "bpe_source":"ORIGINAL_T1_BPE2048_MANIFEST_PLUS_FROZEN_PYTHON_IMPLEMENTATION",
        "bpe_qa":"PASS_SCOPED",
        "public_historical_sources_checked":2,
        "public_scene_exact_or_5gram_near_matches":0,
        "private_fresh16_ac_q1q2_semantic_overlap":"NOT_VERIFIED_NO_SEALED_DATA_OPENED",
        "test_read":False,
        "rights":"SELF_AUTHORED_SCOPED_OWNER_ATTESTATION_PENDING",
        "rater_assignment":"NO","rater_acl_isolation":"NOT_ATTESTED",
        "scientific_execution":"NO",
        "training":"NO","inference":"NO",
        "decision":"HOLD_SINGLE_FULL_BATCH_NO_SCIENCE_RELEASE"
    }
    with RECEIPT.open("xb") as f:
        f.write(json_crlf(report));f.flush()
    print("TTM_D1_V2_STATIC_QA=PASS_SCOPED_VERSIONED_REKEY")
    print("D1_V2_RAW_SHA256=" + report["new_private_v2_raw_sha256"])
    print("D1_V2_RAW_BYTES=" + str(report["new_private_v2_raw_bytes"]))
    print("D1_V2_LF_SHA256=" + report["new_private_v2_lf_sha256"])
    print("D1_V2_SCORER_TEMPLATE_SHA256=" + report["scorer_template_raw_sha256"])
    print("D1_V2_SCORER_TEMPLATE_BYTES=" + str(report["scorer_template_raw_bytes"]))
    print("D1_V2_FAMILIES=16 PROMPTS=128 PRIOR=64 BLIND=512")
    print("D1_V2_PUBLIC_OVERLAP=0_OF_2_SCOPED")
    print("D1_V2_PRIVATE_OVERLAP=NOT_VERIFIED")
    print("D1_V2_RATER=UNASSIGNED")
    print("D1_V2_SCIENCE=NO")
    print("D1_V2_SINGLE_DECISION=HOLD")

if __name__ == "__main__":
    main()