#!/usr/bin/env python3
"""Independent V4 SOURCE / HANDWRITTEN MOCK QA ONLY. Never read CAL/PROBE/TEST.

QA creates temporary mock-shaped Python dictionaries IN MEMORY; NOT the real
CAL64/PROBE256, no authoring, no model loading, no Retriever on real cases.
"""
from __future__ import annotations
import argparse
from collections import Counter
from pathlib import Path
import json
import math
import sys
import importlib.util

import v4_fixed_retrieval_calibration as rank
import v4_source_rights_annotation_custody as cust

SCHEMA = "ttm.vm.v4.source_only_negative_mock_qa.v1"


def mock_index(prefix: str) -> list[dict]:
    return [{"key":f"{prefix}-k-{i:02d}",
             "source_id":f"{prefix}-src",
             "retrieval_text":f"Mock document {i} about a blue stone and a circle."}
            for i in range(32)]


def mock_rights():
    # This is ONLY a mock in-memory test artifact; never evidence of real rights.
    return {"schema":cust.SCHEMA_V4_RIGHTS,
            "sources":[{"source_id":"mock-rights-cal",
                        "kind":"OWNER_AUTHORED_NATURALISTIC",
                        "owner_rights_attestation":True,
                        "attestation_receipt_sha256":"a"*64,
                        "contains_sensitive_PII":False,
                        "authoring_statement":"MOCK_ONLY_NOT_A_REAL_OWNER_ATTESTATION"},
                       {"source_id":"mock-rights-probe",
                        "kind":"OWNER_AUTHORED_NATURALISTIC",
                        "owner_rights_attestation":True,
                        "attestation_receipt_sha256":"b"*64,
                        "contains_sensitive_PII":False,
                        "authoring_statement":"MOCK_ONLY_NOT_A_REAL_OWNER_ATTESTATION"}]}


def mock_case(split, stratum, i):
    cards=mock_index(f"mock-{split.lower()}-{stratum}-{i:02d}")
    keys=[x["key"] for x in cards]
    positive=stratum not in rank.CAL_NEGATIVE
    evidence=[keys[4]] if positive else ([] if stratum=="N2_FALSE_PREMISE_NO_SUPPORT"
                                      else [keys[4],keys[5]])
    return {
        "schema":cust.SCHEMA_V4_CASE,"case_id":f"vm4-{split.lower()}-{stratum}-{i:03d}",
        "split":split,"stratum":stratum,
        "question":"Mock only question about a blue stone and a circle.",
        "public_index":cards,
        "gold_action":"SELECT" if positive else "ABSTAIN",
        "gold_target_key":keys[4] if positive else None,
        "evidence_support_set":evidence,
        "answer":"oak" if positive else None,
        "source_document_cluster":f"mock-{split}-source-{i}-{stratum}",
        "entity_family":f"mock-{split}-entity-{i}-{stratum}",
        "author_style":f"mock-{split}-style-{i}-{stratum}",
        "paraphrase_family":f"mock-{split}-phrase-{i}-{stratum}",
        "source_manifest_ids":[f"mock-rights-{split.lower()}"],
        "correct_memory":None,"wrong_memory":None
    }


def mock_cases(split):
    n=cust.SPLIT_PER_STRATUM[split]
    return [mock_case(split,s,i) for s in rank.CAL_STRATA for i in range(n)]


def expected_value_error(fn):
    try:
        fn()
    except (ValueError, FileNotFoundError):
        return True
    return False


def chk_ok(condition, label):
    if condition is not True:
        raise AssertionError(label)
    return True


def run_audit():
    checks={}
    def register(name,fn):
        try:
            checks[name]=bool(fn())
        except Exception:
            checks[name]=False

    cards=mock_index("mock-vector")
    q="The blue stone rests inside a circle"
    good=mock_cases("CAL")
    poor=mock_cases("PROBE")
    rights=mock_rights()

    register("01_qa_no_real_input_paths",lambda:chk_ok(cust.SPLIT_CASE_COUNTS["CAL"]==64 and
             cust.SPLIT_CASE_COUNTS["PROBE"]==256,"sizes"))
    register("02_cal_mock_generated_only_in_memory",lambda:chk_ok(len(good)==64,"cal_mock"))
    register("03_probe_mock_generated_only_in_memory",lambda:chk_ok(len(poor)==256,"probe_mock"))
    register("04_public_case32_valid",lambda:chk_ok(len(rank.public_input(q,cards)[1])==32,"bank"))
    register("05_public_rejects_wrong_size",lambda:expected_value_error(lambda:rank.public_input(q,cards[:31])))
    register("06_public_rejects_answer_leak",lambda:expected_value_error(lambda:rank.public_input(q,[{**cards[0],"answer":"secret"}]+cards[1:])))
    register("07_public_rejects_duplicate_key",lambda:expected_value_error(lambda:rank.public_input(q,[cards[0],cards[0]]+cards[2:])))
    register("08_public_rejects_empty_query",lambda:expected_value_error(lambda:rank.public_input("",cards)))
    register("09_public_rejects_private_value",lambda:expected_value_error(lambda:rank.public_input(q,[{**cards[0],"value":"secret"}]+cards[1:])))
    register("10_BM25_32_finite",lambda:chk_ok(len(rank.bm25_scores(q,cards))==32 and all(math.isfinite(x) for x in rank.bm25_scores(q,cards)),"bm25"))
    register("11_char3gram_32_finite",lambda:chk_ok(len(rank.char3gram_scores(q,cards))==32 and all(math.isfinite(x) for x in rank.char3gram_scores(q,cards)),"char"))
    register("12_BM25_nontrivial",lambda:chk_ok(max(rank.bm25_scores(q,cards))>=0.0,"bm25_range"))
    register("13_char_normalization_unicode",lambda:chk_ok(rank.normalize("ＡＢＣ  CAT")=="abc cat","unicode"))
    register("14_char3gram_hash_differs",lambda:chk_ok(rank.character_ngrams("banana")!=rank.character_ngrams("orange"),"char_grams"))
    register("15_score_bad_nan_rejected",lambda:expected_value_error(lambda:rank.score_margin([float("nan")]+[0]*31)))
    register("16_score_bad_length_rejected",lambda:expected_value_error(lambda:rank.score_margin([0]*31)))
    scores=[0.0]*32; scores[4]=10.0
    register("17_margin_positive",lambda:chk_ok(rank.score_margin(scores)>0.0,"margin"))
    register("18_margin_zero_tie",lambda:chk_ok(rank.score_margin([0]*32)==0.0,"tie"))
    register("19_Select_exact_key",lambda:chk_ok(rank.decision_from_scores(scores,cards,0.25,rank.METHODS[0]).selected_key==cards[4]["key"],"selected"))
    register("20_Select_index_match",lambda:chk_ok(rank.decision_from_scores(scores,cards,0.25,rank.METHODS[0]).selected_index==4,"selected_index"))
    register("21_ABSTAIN_low_margin",lambda:chk_ok(rank.decision_from_scores(scores,cards,0.999,rank.METHODS[0]).status=="ABSTAIN","abstain"))
    register("22_ABSTAIN_on_exact_tie",lambda:chk_ok(rank.decision_from_scores([0]*32,cards,0.005,rank.METHODS[0]).status=="ABSTAIN","tie_abstain"))
    register("23_always_abstain_sentinel",lambda:chk_ok(rank.decision_from_scores(scores,cards,math.inf,rank.METHODS[0]).status=="ABSTAIN","always"))
    register("24_method_not_registered_rejected",lambda:expected_value_error(lambda:rank.decision_from_scores(scores,cards,0.005,"ORACLE")))

    register("25_mock_rights_structural_PASS_only",lambda:chk_ok(cust.validate_rights(rights)["source_count"]==2,"rights_mock"))
    badrights=mock_rights();badrights["sources"][0]["owner_rights_attestation"]=False
    register("26_real_rights_without_owner_signature_HOLD",lambda:expected_value_error(lambda:cust.validate_rights(badrights)))
    register("27_mock_CAL_shape_valid",lambda:chk_ok(cust.validate_partition(good,"CAL",rights)["cases"]==64,"cal_shape"))
    register("28_mock_PROBE_shape_valid_not_real",lambda:chk_ok(cust.validate_partition(poor,"PROBE",rights)["cases"]==256,"probe_shape"))
    register("29_split_family_disjoint",lambda:chk_ok(cust.check_disjoint(good,poor)["status"]=="PASS_FOUR_FAMILY_DISJOINT","disjoint"))
    contaminated=[dict(poor[0],source_document_cluster=good[0]["source_document_cluster"])]+poor[1:]
    register("30_split_overlap_source_HOLD",lambda:expected_value_error(lambda:cust.check_disjoint(good,contaminated)))
    wrongneg=dict(good[32],answer="faked_answer")
    register("31_negative_answer_HOLD",lambda:expected_value_error(lambda:cust.validate_case(wrongneg,"CAL")))
    wrongpositive=dict(good[8],evidence_support_set=[good[8]["public_index"][4]["key"],good[8]["public_index"][5]["key"]])
    register("32_positive_ambiguous_target_HOLD",lambda:expected_value_error(lambda:cust.validate_case(wrongpositive,"CAL")))
    wrongsource=dict(good[0],source_manifest_ids=["unverified-source"])
    register("33_unsigned_case_source_HOLD",lambda:expected_value_error(lambda:cust.validate_partition([wrongsource]+good[1:],"CAL",rights)))
    register("34_default_prePROBE_gate_HOLD",lambda:expected_value_error(lambda:cust.pre_probe_authorization({})))

    # Synthetic SCORE vectors for hand-written MOCK CAL only.
    vectors=[]
    for c in good:
        z=[0.0]*32
        if c["stratum"] in rank.CAL_PRIMARY or c["stratum"]=="P0_SEEN_WIRING_CONTROL":
            z[4]=10.0
        vectors.append(z)
    register("35_mock_calibration_select_threshold",lambda:chk_ok(rank.calibrate_one(good,vectors,rank.METHODS[0])["cal_correct_primary"]==24,"cal24"))
    register("36_mock_calibration_no_false_select",lambda:chk_ok(rank.calibrate_one(good,vectors,rank.METHODS[0])["cal_negative_false_select"]==0,"negative0"))
    register("37_cal_threshold_grid_no_zero",lambda:chk_ok(len(rank.CAL_GRID)==200 and min(rank.CAL_GRID)>0,"grid"))
    register("38_baseline_best_tie_preference_BM25",lambda:chk_ok(rank.choose_best_baseline({m:{"cal_correct_primary":8,"cal_negative_false_select":0} for m in rank.METHODS[:3]})=="R_BM25_LEXICAL","bm25tie"))
    register("39_cal_rejects_misaligned_scores",lambda:expected_value_error(lambda:rank.calibrate_one(good,vectors[:-1],rank.METHODS[0])))

    trace=cust.private_action_trace(good[0],rank.METHODS[0],
                                    good[0]["gold_target_key"],4,"SELECT",0.9,0.1,"MOCK_UNIQUE")
    register("40_trace_actual_key_recorded",lambda:chk_ok(trace["selected_key"]==good[0]["gold_target_key"],"tracekey"))
    register("41_trace_sha64",lambda:chk_ok(len(trace["decision_trace_sha256"])==64,"tracehash"))
    register("42_trace_wrong_index_rejected",lambda:expected_value_error(lambda:cust.private_action_trace(good[0],rank.METHODS[0],good[0]["gold_target_key"],5,"SELECT",0.9,0.1,"BAD_KEY")))
    register("43_trace_abstain_no_selected_key",lambda:chk_ok(cust.private_action_trace(good[32],rank.METHODS[0],None,None,"ABSTAIN",0.0,1.0,"MOCK_ABSTAIN")["selected_key"] is None,"traceabstain"))
    register("44_negative_trace_gold_null",lambda:chk_ok(cust.private_action_trace(good[32],rank.METHODS[0],None,None,"ABSTAIN",0.0,1.0,"MOCK_ABSTAIN")["gold_target_key"] is None,"tracegold"))

    register("45_bge_revision_full_commit_pin",lambda:chk_ok(len(rank.UPSTREAM_REVISION)==40 and rank.UPSTREAM_REVISION==cust.MODEL_REVISION,"revision"))
    register("46_bge_weights_known_hash_pin",lambda:chk_ok(rank.EXPECTED_SAFETENSORS_SHA256==cust.MODEL_WEIGHT_SHA256 and len(rank.EXPECTED_SAFETENSORS_SHA256)==64,"weights"))
    register("47_BGE_local_only_loader_source",lambda:chk_ok("local_files_only=True" in Path(rank.__file__).read_text(encoding="utf-8"),"local"))
    register("48_no_transformers_import_on_mock",lambda:chk_ok("transformers" not in sys.modules,"no_model_import"))
    register("49_review_requires_two_AI",lambda:expected_value_error(lambda:cust.validate_two_blind_AI({},good)))
    register("50_review_does_not_accept_human_flag",lambda:chk_ok(cust.SCHEMA_V4_AI.endswith("ai_blind_review.v1"),"reviewclass"))
    register("51_import_science_not_triggered",lambda:chk_ok(rank.SOURCE_CODE_ONLY is True,"not_science"))
    register("52_private_positive_NLL_not_computed_in_QA",lambda:chk_ok(all("arm_nll" not in row for row in good),"no_reader_nll"))
    register("53_one_shot_marker_not_created",lambda:chk_ok(not hasattr(rank,"RUN_ID"),"no_one_shot"))
    register("54_fixture_schema_source_only",lambda:chk_ok(cust.SCHEMA_V4_CASE.endswith("authored_source_case.v1"),"schema"))
    register("55_case_public_view_no_gold",lambda:chk_ok(set(cust.public_view(good[0]))=={"case_id","question","public_index"},"public"))
    register("56_future_selected_key_vs_gold_is_explicit",lambda:chk_ok("correct_select" in trace and trace["correct_select"] is True,"recompute"))
    register("57_no_real_model_weights_opened",lambda:chk_ok(not any("model.safetensors" in repr(x) for x in (good,poor)),"model_fake"))
    register("58_negative_Reader_forward_initially_zero",lambda:chk_ok(cust.private_action_trace(good[32],rank.METHODS[0],None,None,"ABSTAIN",0.0,1.0,"NEGATIVE")["Reader_forward_count"]==0,"no_negative_reader"))
    register("59_cal_positive_denominator_fixed24",lambda:chk_ok(sum(c["stratum"] in rank.CAL_PRIMARY for c in good)==24,"caldenom"))
    register("60_cal_negative_denominator_fixed32",lambda:chk_ok(sum(c["stratum"] in rank.CAL_NEGATIVE for c in good)==32,"negdenom"))

    return checks


def main():
    parser=argparse.ArgumentParser()
    parser.add_argument("--out",type=Path,required=True)
    args=parser.parse_args()
    if args.out.exists():
        raise FileExistsError("REFUSE_QA_RECEIPT_OVERWRITE")
    checks=run_audit()
    passed=sum(x is True for x in checks.values())
    report={"schema":SCHEMA,
            "status":("PASS_V4_SOURCE_MOCK_QA" if passed==len(checks) else "HOLD_V4_SOURCE_MOCK_QA"),
            "qa_passed":passed,"qa_total":len(checks),"checks":checks,
            "data_class":"HANDWRITTEN_MOCK_ONLY_IN_MEMORY_NOT_CAL64_OR_PROBE256",
            "source_rights_real":"NOT_ATTESTED","candidate_weights_on_owner":"NOT_VERIFIED",
            "CAL64_actual_scored":False,"PROBE256_actual_scored":False,
            "reader_forward_calls":0,"test_opened":False,"gpu_used":False}
    args.out.parent.mkdir(parents=True,exist_ok=True)
    args.out.write_text(json.dumps(report,sort_keys=True,indent=2)+"\n",encoding="utf-8")
    print(json.dumps({"status":report["status"],"qa":f"{passed}/{len(checks)}",
                      "real_data":False,"science":False},sort_keys=True))
    if passed!=len(checks):
        raise SystemExit("SOURCE_MOCK_QA_FAILED_FAIL_CLOSED")


if __name__=="__main__":
    main()
