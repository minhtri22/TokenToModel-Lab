#!/usr/bin/env python3
"""Independent source-only design QA for H-DATA FAIL4 MD1.

Reads public frozen aggregate and NEW design contract ONLY. No model/Torch,
private prompts, score files, AES mapping, TRAIN/TEST or data generation.
"""
from __future__ import annotations
import copy
import hashlib
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[4]
OLD = (ROOT / "artifacts/qa/ttm-small4m-h-data-s1/blind240/"
       "TTM_HDATA_S1_FINAL24_READONLY_UNBLIND_PUBLIC_AGGREGATE_20261114.json")
NEW = (ROOT / "docs/research/ttm-hdata-fail4-md1/"
       "TTM_HDATA_FAIL4_MD1_FROZEN_PROSPECTIVE_DESIGN_CONTRACT_20261114.json")
DOC = (ROOT / "docs/research/ttm-hdata-fail4-md1/"
       "TTM_HDATA_FAIL4_MD1_PROSPECTIVE_PREREG_AND_FOUR_FAIL_MECHANISM_PLAN_20261114.md")
BLUEPRINT = (ROOT / "docs/research/ttm-hdata-fail4-md1/"
             "TTM_HDATA_FAIL4_MD1_FRESH_CORE_2X2_DATA_BLUEPRINT_DESIGN_ONLY_20261114.json")
OLD_SHA256 = "23df562a73c7f83096ba4ec683da81823d0104a80fbf689b01b4310348e3a7e2"

def need(value: bool, code: str) -> None:
    if not value:
        raise RuntimeError("H_DATA_FAIL4_MD1_SOURCE_HOLD:" + code)

def load_json(path: Path) -> tuple[dict, bytes]:
    need(path.is_file() and not path.is_symlink(), "INPUT_NOT_REGULAR:" + path.name)
    raw = path.read_bytes()
    return json.loads(raw), raw

def verify(old: dict, new: dict) -> dict:
    need(new.get("schema") == "ttm.hdata_s1.fail4.prospective_mechanism_design.v1",
         "NEW_CONTRACT_SCHEMA")
    need(new["state"] == "DESIGN_ONLY_NO_DATA_RELEASE_NO_INFERENCE_NO_TRAINING",
         "DESIGN_ONLY_STATE")
    prev = new["source_hdata_closed"]
    need(prev["formal_outcome"] == old["formal_adjudication"] ==
         "H_DATA_S1_NO_DEMONSTRATED_SCOPED_SEMANTIC_BENEFIT",
         "ORIGINAL_FINAL_SCIENCE_NOT_PRESERVED")
    need(prev["original_FINAL24_consumed"] is True and
         prev["original_AES_unblind_consumed"] is True and
         prev["freeze_immutable"] is True and
         prev["source_TEST_Q1_Q2_OOD_sealed"] is True,
         "ORIGINAL_CONSUMED_SCOPE")
    need(old["status"] == "COMPLETE_READONLY_UNBLIND_NO_REDO" and
         old["unblind"] == "EXECUTED_ONCE_READ_ONLY", "OLD_UNBLIND_COMPLETE")
    need(old["primary_paired_H1_minus_H0_mean_delta"] == 0 and
         old["primary_paired_strict_wins_H1"] == 0 and
         old["paired_bootstrap_20k_seed_20261113"]["CI95"] == [0, 0] and
         old["component_secondary_H1_minus_H0_deltas"]["goal_or_rule_progress"] == 0,
         "SOURCE_FOUR_FAIL_VALUES")
    observed = new["four_failed_gates"]
    need([x["id"] for x in observed] == ["F1", "F2", "F3", "F4"],
         "FOUR_FAIL_ORDER")
    tests = [
        ("primary_mean_H1_minus_H0", 0, ">=", 0.5),
        ("primary_strict_pair_wins_H1", 0, ">=", 16),
        ("paired_20000_bootstrap_CI95_lower", 0, ">", 0),
        ("goal_rule_progress_mean_H1_minus_H0", 0, ">", 0),
    ]
    for row, (metric, value, op, threshold) in zip(observed, tests):
        need(row["metric"] == metric and row["observed"] == value and
             row["operator"] == op and row["threshold"] == threshold and
             row["cause_independent"] is False, "FAIL_GATES_NOT_EXACT")
    need(new["known_associated_observations"]
         ["all_48_primary_actor_object_goal_ratings_zero"] is True,
         "SCORE_FLOOR_NOT_RECORDED")

    measurement = new["M0_measurement_calibration"]
    need(measurement["control_core_count"] == 32 and
         measurement["control_text_count"] == 64 and
         measurement["positive_count"] == measurement["negative_count"] == 32 and
         measurement["reviewers"] == 2 and
         measurement["sensitivity_min_per_rater_per_axis"] == 0.875 and
         measurement["specificity_min_per_rater_per_axis"] == 0.875 and
         measurement["interrater_agreement_min_per_axis"] == 0.85,
         "CALIBRATION_CONTROL_GATES")

    d = new["M1_fresh_dataset"]
    f = d["factorial"]
    need(d["strata"] ==
         ["object_custody", "social_relation", "causal_obstacle", "temporal_rule"] and
         d["cores_per_stratum"] == 4 and
         d["fresh_core_count"] == 16 and
         d["conditions_per_core"] == 4 and
         d["DEV_prompt_count"] == 16 and
         d["LOCKED_FINAL_prompt_count"] == 48 and
         d["FINAL_core_index_per_stratum"] == [2,3,4] and
         d["DEV_core_index_per_stratum"] == [1],
         "CORE_LEVEL_DEV_FINAL_SPLIT")
    need(f["context_load"] == ["SHORT","DISTRACTOR"] and
         f["goal_signal"] == ["EXPLICIT","IMPLICIT"] and
         f["core_matched_2x2"] is True and
         f["short_target_BPE_prefix_range"] == [64,96] and
         f["distractor_target_BPE_prefix_range"] == [144,176] and
         f["max_new_tokens"] == 64 and
         f["context_limit"] == 256 and
         max(f["distractor_target_BPE_prefix_range"]) + f["max_new_tokens"] <= f["context_limit"],
         "FACTORS_CONTEXT")
    need(f["new_prompt_private_status"] == "NOT_CREATED_DESIGN_ONLY" and
         d["public_prompts"] is False and
         d["freeze_before_first_new_model_forward"] is True,
         "FRESH_FINAL_NOT_YET_GENERATED_OR_EXPOSED")

    arm = new["allowed_model"]
    need(arm["further_optimizer_updates"] == 0 and
         arm["forbid_finetuning"] is True and
         arm["context_tokens"] == 256 and arm["decode_max_new_tokens"] == 64 and
         arm["H0_checkpoint_step1152_sha256"] ==
         "a7cdade3b70cb2ceed258edd1e3edd494ce9745633d2e528ee90232f3c95c2fe" and
         arm["H1_checkpoint_step1152_sha256"] ==
         "31d9365a470e638f77e6661252ed8d0605e9f9095da145d9f48751adcdcfcb64",
         "NO_MODEL_TUNING_AND_EXACT_EXISTING_WEIGHTS")

    evaluation = new["M2_forward_and_blind"]
    need(evaluation["mode"] == "NOT_EXECUTED_IN_THIS_DESIGN_TURN" and
         evaluation["new_separate_owner_GO_required"] is True and
         evaluation["new_random_balanced_AES_mapping_required"] is True and
         evaluation["balanced_total_LEFT_H0_H1_each"] == 24 and
         evaluation["within_core_4_conditions_LEFT_H0_H1_each"] == 2 and
         evaluation["six_per_stratum_each_arm"] == 6 and
         evaluation["per_condition_LEFT_H0_H1_each"] == 6 and
         evaluation["bootstrap_unit"] ==
         "12 independent FINAL story cores, not 48 variants and not 96 continuations" and
         evaluation["bootstrap_resamples"] == 20000 and
         evaluation["bootstrap_rng_seed"] == 20261114 and
         evaluation["frozen_reviewers_per_review"] ==
         {"number_of_pairs":48,"sides":2,"axes":5,"integer_scores":480,"pair_notes":48},
         "EVAL_SPLIT_BLIND_AND_CLUSTER_BOOTSTRAP")
    mech = new["M3_mechanism_diagnostics"]
    need(mech["context_interference"]["minimum_delta"] == 0.25 and
         mech["goal_explicitness"]["minimum_delta"] == 0.25 and
         mech["teacher_forced_oracle_foil"]["candidate_core_count"] == 12 and
         mech["teacher_forced_oracle_foil"]["length_match_requirement"].startswith(
             "Absolute BPE token length difference <=2 AND <=5%"),
         "MECHANISM_GATES_FROZEN")
    p = new["permissions"]
    need(all(p[k] is False for k in
             ("generation_authorized", "inference_authorized",
              "training_authorized", "TEST_Q1_Q2_OOD_authorized",
              "unblind_authorized")), "WRONG_CURRENT_OWNER_PERMISSIONS")
    need(new["decision"] ==
         "GO_PROSPECTIVE_DESIGN_ONLY__HOLD_NEW_DATA_CUSTODY_AND_ALL_SCIENCE_UNTIL_INDEPENDENT_PREEXEC_AND_OWNER_GO",
         "WRONG_OWNER_DESIGN_DECISION")
    return {
        "schema":"ttm.hdata_s1.fail4.md1.source_only_static_qa.v1",
        "status":"PASS_SOURCE_ONLY_PROTOCOL_AND_SOURCE_FOUR_FAIL_LOCK",
        "source_old_final_four_failed_gates":"PASS_4_OF_4",
        "new_dataset_cores":16,
        "new_DEV_prompts_planned":16,
        "new_FINAL_prompts_planned":48,
        "calibration_controls_planned":64,
        "rater_requirement":2,
        "measurement_floor_gate":"SOURCE_LOCKED_NOT_EXECUTED",
        "new_prompt_materialized":False,
        "model_forward_or_training":False,
        "old_FINAL_or_score_reopened":False,
        "old_TEST_Q1_Q2_OOD":False,
        "new_OWNER_GO_for_science":False,
        "formal_decision":new["decision"]
    }

def main() -> None:
    old, raw = load_json(OLD)
    need(hashlib.sha256(raw).hexdigest() == OLD_SHA256, "OLD_REPORT_SHA_DRIFT")
    new, _ = load_json(NEW)
    need(DOC.is_file() and DOC.stat().st_size >= 5000,
         "READABLE_PREREG_MISSING")
    result = verify(old,new)
    bp,_ = load_json(BLUEPRINT)
    need(bp["schema"] == "ttm.hdata_s1.fail4.md1.fresh_data_preproduction_blueprint.v1"
         and bp["status"] == "BLUEPRINT_ONLY_NO_NEW_PROMPT_TEXT_CREATED_OR_REVEALED",
         "BLUEPRINT_IS_NOT_DATA")
    cores, prompts, controls = bp["story_cores"], bp["prompt_variants"], bp["measurement_controls"]
    need(len(cores)==16 and len(prompts)==64 and len(controls)==32 and
         len({c["core_id"] for c in cores})==16 and
         len({p["id"] for p in prompts})==64 and
         len({p["core_id"] for p in prompts})==16,
         "BLUEPRINT_CORE_OR_PROMPT_COUNTS")
    need(sum(c["split"]=="DEV" for c in cores)==4 and
         sum(c["split"]=="LOCKED_FINAL" for c in cores)==12 and
         sum(p["split"]=="DEV" for p in prompts)==16 and
         sum(p["split"]=="LOCKED_FINAL" for p in prompts)==48,
         "BLUEPRINT_SPLIT_COUNTS")
    need(all(p["sha256_utf8_prompt"] is None and
             p["exact_BPE_prefix_count"] is None and
             p["owner_private_source_ref"] is None for p in prompts) and
         all(c["core_sha256"] is None and
             c["owner_private_gold_record_sha256"] is None for c in cores),
         "BLUEPRINT_CANNOT_CONTAIN_PRIVATE_OR_GENERATED_TEXT")
    for core in cores:
        siblings=[p for p in prompts if p["core_id"]==core["core_id"]]
        need(len(siblings)==4 and all(p["split"]==core["split"] and
             p["stratum"]==core["stratum"] for p in siblings) and
             {(p["context_load"],p["goal_signal"]) for p in siblings} ==
             {("SHORT","EXPLICIT"),("SHORT","IMPLICIT"),
              ("DISTRACTOR","EXPLICIT"),("DISTRACTOR","IMPLICIT")},
             "ONE_FOUR_CELL_GROUP_PER_CORE")
    need(all(c["positive_text_sha256"] is None and
             c["negative_text_sha256"] is None and
             c["gold_owner_private_sha256"] is None for c in controls),
         "NO_CALIBRATION_GOLD_IN_BLUEPRINT")
    result["blueprint_structural_slots"] = "PASS_16_CORES_64_VARIANTS_32_CONTROLS_NO_TEXT"
    # Negative unit tests ensure that the verifier fails if someone quietly
    # changes a prior FAIL, gives an unauthorized GO or retunes the dataset.
    for mutate in (
        lambda n: n["four_failed_gates"][0].update({"threshold":0}),
        lambda n: n["permissions"].update({"inference_authorized":True}),
        lambda n: n["M1_fresh_dataset"].update({"LOCKED_FINAL_prompt_count":24}),
    ):
        changed = copy.deepcopy(new)
        mutate(changed)
        try:
            verify(old, changed)
        except RuntimeError:
            pass
        else:
            raise RuntimeError("H_DATA_FAIL4_MD1_SOURCE_HOLD:NEGATIVE_MUTATION_ACCEPTED")
    result["negative_mutation_tests"] = "PASS_3_OF_3"
    print(json.dumps(result, sort_keys=True, ensure_ascii=False, indent=2))

if __name__ == "__main__":
    main()
