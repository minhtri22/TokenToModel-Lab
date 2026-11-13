#!/usr/bin/env python3
"""V4 CAL/PROBE provenance, authoring, blind AI review and raw-action custody.

Source-only library: no model/Reader forward, no downloading, no TEST access.
Author/reviewer consent and source rights are NEVER inferred by this code.
"""
from __future__ import annotations
from collections import Counter
from hashlib import sha256
from pathlib import Path
from typing import Mapping, Sequence
import json
import re
from v4_fixed_retrieval_calibration import (CAL_STRATA, CAL_NEGATIVE, CAL_PRIMARY,
                                             public_input, sha256_file)

ALLOWED_SOURCE_KINDS = ("OWNER_AUTHORED_NATURALISTIC","DOCUMENTS_WITH_EXPLICIT_PERMISSION")
SOURCE_CLUSTER_AXES = ("source_document_cluster","entity_family",
                       "author_style","paraphrase_family")
SPLIT_CASE_COUNTS = {"CAL":64,"PROBE":256}
SPLIT_PER_STRATUM = {"CAL":8,"PROBE":32}
MODEL_WEIGHT_SHA256 = "3c9f31665447c8911517620762200d2245a2518d6e7208acc78cd9db317e21ad"
MODEL_REVISION = "5c38ec7c405ec4b44b94cc5a9bb96e735b38267a"
MODEL_ID = "BAAI/bge-small-en-v1.5"
SCHEMA_V4_CASE = "ttm.vm.v4.authored_source_case.v1"
SCHEMA_V4_RIGHTS = "ttm.vm.v4.source_rights.v1"
SCHEMA_V4_AI = "ttm.vm.v4.ai_blind_review.v1"


def stable_json(o: object) -> bytes:
    return (json.dumps(o,sort_keys=True,separators=(",",":"),
                       ensure_ascii=False)+"\n").encode("utf-8")


def hash_obj(o: object) -> str:
    return sha256(stable_json(o)).hexdigest()


def validate_rights(source_manifest: Mapping) -> dict:
    """Fail-closed rights review; zero receipts means HOLD, not presumed permission."""
    if source_manifest.get("schema") != SCHEMA_V4_RIGHTS:
        raise ValueError("RIGHTS_SCHEMA_INVALID")
    rows = source_manifest.get("sources",[])
    if not isinstance(rows,list) or not rows:
        raise ValueError("HOLD_SOURCE_RIGHTS_MISSING")
    if len({r.get("source_id") for r in rows}) != len(rows):
        raise ValueError("DUPLICATE_SOURCE_ID")
    for r in rows:
        if r.get("kind") not in ALLOWED_SOURCE_KINDS:
            raise ValueError("SOURCE_KIND_NOT_ALLOWED")
        if not isinstance(r.get("source_id"),str) or not r["source_id"]:
            raise ValueError("INVALID_SOURCE_ID")
        if r.get("contains_sensitive_PII") is not False:
            raise ValueError("HOLD_PII_SCREEN_NOT_PASSED")
        if r.get("owner_rights_attestation") is not True:
            raise ValueError("HOLD_OWNER_RIGHTS_ATTESTATION_REQUIRED")
        if not isinstance(r.get("attestation_receipt_sha256"),str) or len(r["attestation_receipt_sha256"])!=64:
            raise ValueError("HOLD_NO_ATTESTATION_RECEIPT_SHA")
        if r["kind"]=="DOCUMENTS_WITH_EXPLICIT_PERMISSION":
            if not all(isinstance(r.get(k),str) and r.get(k)
                       for k in ("source_url","author","license_or_permission",
                                 "permission_receipt_sha256","retrieval_date_utc")):
                raise ValueError("HOLD_EXTERNAL_SOURCE_LICENSE_PROVENANCE")
        elif not isinstance(r.get("authoring_statement"),str) or not r["authoring_statement"]:
            raise ValueError("HOLD_OWNER_AUTHORING_STATEMENT")
    return {"status":"PASS_RIGHTS_STRUCTURE_ATTESTED_BY_OWNER_NOT_EXTERNAL_LEGAL_AUDIT",
            "source_count":len(rows),"source_ids":[r["source_id"] for r in rows]}


def validate_case(case: Mapping, split: str) -> None:
    if split not in SPLIT_CASE_COUNTS:
        raise ValueError("BAD_SPLIT")
    if not isinstance(case,Mapping) or case.get("schema") != SCHEMA_V4_CASE:
        raise ValueError("CASE_SCHEMA_INVALID")
    if case.get("split") != split:
        raise ValueError("CASE_SPLIT_DRIFT")
    if case.get("stratum") not in CAL_STRATA:
        raise ValueError("CASE_STRATUM_INVALID")
    if not isinstance(case.get("case_id"),str) or not case["case_id"].startswith("vm4-"+split.lower()+"-"):
        raise ValueError("CASE_ID_NAMESPACE_INVALID")
    for axis in SOURCE_CLUSTER_AXES:
        if not isinstance(case.get(axis),str) or not case[axis]:
            raise ValueError("MISSING_SOURCE_SPLIT_FAMILY_"+axis)
    question,cards = public_input(case.get("question"),case.get("public_index"))
    if len(question)>1024:
        raise ValueError("QUESTION_TOO_LONG")
    if not isinstance(case.get("source_manifest_ids"),list) or not case["source_manifest_ids"]:
        raise ValueError("CASE_SOURCE_PROVENANCE_MISSING")
    if len(case["source_manifest_ids"])!=len(set(case["source_manifest_ids"])):
        raise ValueError("DUPLICATE_SOURCE_MANIFEST_REF")
    keys={c["key"] for c in cards}
    evidence=case.get("evidence_support_set")
    if not isinstance(evidence,list) or len(evidence)!=len(set(evidence)) or not set(evidence).issubset(keys):
        raise ValueError("INVALID_GOLD_EVIDENCE_SUPPORT_KEYS")
    positive=case["stratum"] not in CAL_NEGATIVE
    if positive:
        if case.get("gold_action")!="SELECT" or case.get("gold_target_key") not in keys:
            raise ValueError("POSITIVE_GOLD_ACTION_TARGET_MISSING")
        if len(evidence)!=1 or evidence[0]!=case["gold_target_key"]:
            raise ValueError("POSITIVE_NOT_UNIQUE_SUPPORTED")
        if not isinstance(case.get("answer"),str) or not case["answer"]:
            raise ValueError("POSITIVE_ANSWER_MISSING")
    else:
        if case.get("gold_action")!="ABSTAIN":
            raise ValueError("NEGATIVE_NOT_ABSTAIN")
        if case.get("gold_target_key") is not None or case.get("answer") is not None:
            raise ValueError("NEGATIVE_HAS_HIDDEN_TARGET_OR_ANSWER")
        if case.get("correct_memory") is not None or case.get("wrong_memory") is not None:
            raise ValueError("NEGATIVE_READER_MEMORY_INVALID")
        if case["stratum"]=="N2_FALSE_PREMISE_NO_SUPPORT" and evidence:
            raise ValueError("NO_SUPPORT_NEGATIVE_HAS_SUPPORT")
        if case["stratum"]!="N2_FALSE_PREMISE_NO_SUPPORT" and len(evidence)<2:
            raise ValueError("AMBIGUOUS_OR_CONFLICTING_NEGATIVE_NEEDS_2_EVIDENCE")
    # Explicitly prevent answer/target from appearing in the PUBLIC card schema.
    if any("answer" in c or "target_key" in c or "value" in c for c in cards):
        raise ValueError("PRIVATE_FIELD_LEAKED_IN_PUBLIC_CARDS")


def validate_partition(cases: Sequence[Mapping], split: str, rights_manifest: Mapping) -> dict:
    if split not in SPLIT_CASE_COUNTS or len(cases)!=SPLIT_CASE_COUNTS[split]:
        raise ValueError("PARTITION_TOTAL_MISMATCH")
    expected=Counter({s:SPLIT_PER_STRATUM[split] for s in CAL_STRATA})
    if Counter(x.get("stratum") for x in cases)!=expected:
        raise ValueError("PARTITION_STRATA_MISMATCH")
    ids=[x.get("case_id") for x in cases]
    if len(set(ids))!=len(ids):
        raise ValueError("DUPLICATE_CASE_IDS")
    right=validate_rights(rights_manifest)
    valid_sources=set(right["source_ids"])
    for x in cases:
        validate_case(x,split)
        if not set(x["source_manifest_ids"]).issubset(valid_sources):
            raise ValueError("CASE_SOURCE_NOT_IN_SIGNED_RIGHTS_MANIFEST")
    return {"split":split,"cases":len(cases),"case_ids_sha256":hash_obj(ids),
            "rights_manifest_sha256":hash_obj(rights_manifest),
            "status":"PASS_STRUCTURE_RIGHTS_CUSTODY_SOURCE_ONLY"}


def check_disjoint(cal: Sequence[Mapping], probe: Sequence[Mapping]) -> dict:
    """Does not read TEST. All four source-family axes must be disjoint."""
    if len(cal)!=64 or len(probe)!=256:
        raise ValueError("BAD_SPLIT_SIZE")
    if {x["case_id"] for x in cal} & {x["case_id"] for x in probe}:
        raise ValueError("CROSS_SPLIT_DUPLICATE_IDS")
    intersection={}
    for axis in SOURCE_CLUSTER_AXES:
        a={x[axis] for x in cal}
        b={x[axis] for x in probe}
        intersection[axis]=sorted(a & b)
        if intersection[axis]:
            raise ValueError("HOLD_CROSS_SPLIT_CONTAMINATION_"+axis)
    return {"status":"PASS_FOUR_FAMILY_DISJOINT","axis_intersections":intersection}


def pre_probe_authorization(freeze_receipt: Mapping) -> dict:
    """Only permit later PROBE authoring after CAL thresholds are committed."""
    r=freeze_receipt
    required=["candidate_source_git_blob","retriever_baselines_source_git_blob",
              "model_revision","weights_sha256","tokenizer_sha256",
              "CAL64_sha256","CAL_rater_A_sha256","CAL_rater_B_sha256",
              "CAL_thresholds_sha256","source_rights_receipt_sha256",
              "thresholds_frozen_commit_sha","source_freeze_commit_sha"]
    for key in required:
        if not isinstance(r.get(key),str) or not r[key]:
            raise ValueError("HOLD_PRE_PROBE_FREEZE_MISSING_"+key)
    if r["model_revision"]!=MODEL_REVISION or r["weights_sha256"]!=MODEL_WEIGHT_SHA256:
        raise ValueError("HOLD_SEMANTIC_MODEL_PIN_DRIFT")
    if not all(re.fullmatch(r"[0-9a-f]{40}",r[k]) for k in (
        "candidate_source_git_blob","retriever_baselines_source_git_blob",
        "thresholds_frozen_commit_sha","source_freeze_commit_sha")):
        raise ValueError("HOLD_SOURCE_COMMIT_OR_BLOB_SHA_INVALID")
    if not all(re.fullmatch(r"[0-9a-f]{64}",r[k]) for k in (
        "weights_sha256","tokenizer_sha256","CAL64_sha256","CAL_rater_A_sha256",
        "CAL_rater_B_sha256","CAL_thresholds_sha256","source_rights_receipt_sha256")):
        raise ValueError("HOLD_PRIVATE_CUSTODY_SHA_INVALID")
    if r["source_freeze_commit_sha"]==r["thresholds_frozen_commit_sha"]:
        raise ValueError("HOLD_THRESHOLD_FREEZE_MUST_FOLLOW_SOURCE_FREEZE")
    if r.get("CAL_negative_false_select_max")!=1:
        raise ValueError("HOLD_CAL_NEGATIVE_SAFETY_POLICY_DRIFT")
    if r.get("CAL_cases")!=64 or r.get("calibration_complete") is not True:
        raise ValueError("HOLD_CAL_NOT_COMPLETE")
    return {"status":"GO_PROBE_AUTHORING_ONLY_NOT_SCIENCE",
            "receipt_sha256":hash_obj(r)}


def public_view(case: Mapping) -> dict:
    """Only this projection may be given to rater/retriever."""
    return {"case_id":case["case_id"],"question":case["question"],
            "public_index":case["public_index"]}


def validate_two_blind_AI(reviews: Mapping[str,Mapping], cases: Sequence[Mapping]) -> dict:
    if set(reviews)!={"A","B"}:
        raise ValueError("TWO_DISTINCT_AI_SLOTS_REQUIRED")
    originals={c["case_id"]:c for c in cases}
    if len(originals)!=len(cases):
        raise ValueError("DUPLICATE_CASES_FOR_REVIEW")
    ids=[]
    answers={}
    for slot in ("A","B"):
        r=reviews[slot]
        if r.get("schema")!=SCHEMA_V4_AI or r.get("slot")!=slot or r.get("rater_type")!="AI":
            raise ValueError("AI_RATER_SCHEMA_SLOT_CLASS_INVALID")
        if r.get("human_attestation") is not False:
            raise ValueError("AI_MUST_NOT_CLAIM_HUMAN")
        if r.get("self_report_no_source_or_other_rater_access") is not True:
            raise ValueError("AI_BLINDNESS_SELF_REPORT_NOT_CLEAN")
        if not isinstance(r.get("rater_id"),str) or not r["rater_id"]:
            raise ValueError("AI_ID_MISSING")
        ids.append(r["rater_id"])
        rows=r.get("cases")
        if not isinstance(rows,list) or len(rows)!=len(cases):
            raise ValueError("AI_REVIEW_COUNT_MISMATCH")
        if {row.get("case_id") for row in rows}!=set(originals):
            raise ValueError("AI_REVIEW_CASE_SET_MISMATCH")
        answers[slot]={}
        for row in rows:
            original=originals[row["case_id"]]
            if set(row)!={"case_id","question","public_index","selected_key","reason","confidence"}:
                raise ValueError("AI_REVIEW_ROW_SCHEMA_MISMATCH")
            if row["question"]!=original["question"] or row["public_index"]!=original["public_index"]:
                raise ValueError("AI_BLIND_PACKET_MODIFIED")
            if not isinstance(row["reason"],str) or len(row["reason"].strip())<8:
                raise ValueError("AI_REASON_TOO_SHORT")
            if type(row["confidence"])!=int or not 0<=row["confidence"]<=3:
                raise ValueError("AI_CONFIDENCE_INVALID")
            if row["selected_key"] is not None and row["selected_key"] not in {
                    x["key"] for x in original["public_index"]}:
                raise ValueError("AI_SELECTED_KEY_NOT_PUBLIC")
            answers[slot][row["case_id"]]=row["selected_key"]
    if ids[0]==ids[1]:
        raise ValueError("AI_RATER_ID_NOT_DISTINCT")
    agreement=sum(answers["A"][i]==answers["B"][i] for i in originals)
    if agreement!=len(cases):
        raise ValueError("HOLD_TWO_AI_DISAGREE_REQUIRE_ADJUDICATION")
    matched=sum(answers["A"][i]==originals[i].get("gold_target_key") for i in originals)
    if matched!=len(cases):
        raise ValueError("HOLD_AI_GOLD_NOT_AGREED")
    return {"status":"PASS_AI_AGREEMENT_AND_PRIVATE_GOLD_SCOPED",
            "cases":len(cases),"agree":agreement,"match_gold":matched,
            "human_reviewer_count":0,
            "AI_independence":"SELF_REPORTED_NOT_CRYPTOGRAPHICALLY_ATTESTED"}


def private_action_trace(case: Mapping, method: str, selected_key: str|None,
                         selected_index: int|None, status: str, score: float,
                         threshold: float, reason_code: str) -> dict:
    """For future native post-science readback, with selected_key visible privately."""
    validate_case(case,case["split"])
    if status not in ("SELECT","ABSTAIN") or not isinstance(reason_code,str):
        raise ValueError("BAD_RETRIEVER_OUTCOME")
    if status=="SELECT":
        if type(selected_index)!=int or not 0<=selected_index<32:
            raise ValueError("BAD_SELECTED_INDEX")
        if case["public_index"][selected_index]["key"]!=selected_key:
            raise ValueError("SELECTED_INDEX_KEY_INCONSISTENT")
    elif selected_key is not None or selected_index is not None:
        raise ValueError("ABSTAIN_HAS_SELECTED_KEY")
    trace={"case_id":case["case_id"],"stratum":case["stratum"],
           "public_index_sha256":hash_obj(case["public_index"]),
           "gold_action":case["gold_action"],
           "gold_target_key":case["gold_target_key"],
           "selected_key":selected_key,"selected_index":selected_index,
           "status":status,"reason_code":reason_code,"score":score,
           "threshold":threshold,"method":method,
           "evidence_support_key_hashes":[sha256(k.encode()).hexdigest()
                                          for k in case["evidence_support_set"]]}
    trace["correct_select"]=(status=="SELECT" and
                             selected_key==case["gold_target_key"] and
                             case["gold_action"]=="SELECT")
    trace["correct_abstain"]=(status=="ABSTAIN" and case["gold_action"]=="ABSTAIN")
    trace["Reader_forward_count"]=0
    trace["arm_nll"]=None
    trace["answer_tokens"]=0
    trace["decision_trace_sha256"]=hash_obj(trace)
    return trace
