#!/usr/bin/env python3
"""V4 future owner-authored CAL or PROBE packet assembly, STRICT SOURCE ONLY.

Does not invent any cases. Input MUST be owner-authored and rights attested.
PROBE requires CAL-threshold receipt and split-disjoint source families.
Never scores retrieval, calls Reader, trains, reads TEST or writes GitHub.
"""
from __future__ import annotations
from pathlib import Path
import argparse
import hashlib
import json
import re
import sys
from v4_source_rights_annotation_custody import (
    SCHEMA_V4_RIGHTS, SCHEMA_V4_AI,
    validate_partition, check_disjoint, public_view, pre_probe_authorization,
    stable_json, hash_obj, MODEL_WEIGHT_SHA256, MODEL_REVISION)

BUNDLE_SCHEMA = "ttm.vm.v4.authored_bundle.v1"
OUT_NAMES = {
    "CAL": ("V4_CAL64_PRIVATE.json","V4_CAL64_AI_A_TEMPLATE.json",
            "V4_CAL64_AI_B_TEMPLATE.json","V4_CAL64_SOURCE_QA_RECEIPT.json"),
    "PROBE": ("V4_PROBE256_PRIVATE.json","V4_PROBE256_AI_A_TEMPLATE.json",
              "V4_PROBE256_AI_B_TEMPLATE.json","V4_PROBE256_SOURCE_QA_RECEIPT.json")
}

def read_json(path:Path):
    return json.loads(path.read_text(encoding="utf-8"))

def sha256_hex(v):
    return isinstance(v,str) and re.fullmatch("[0-9a-f]{64}",v) is not None

def source_frozen(receipt:dict):
    """Attestation fields must be read from actual owner-prepared frozen receipt.
    This function cannot independently verify Git ancestry or real model bytes.
    """
    if receipt.get("model_revision")!=MODEL_REVISION or        receipt.get("weights_sha256")!=MODEL_WEIGHT_SHA256:
        raise ValueError("HOLD_SOURCE_MODEL_UPSTREAM_PIN_MISMATCH")
    for key in ("source_commit_sha","baseline_source_git_blob"):
        if re.fullmatch(r"[0-9a-f]{40}",str(receipt.get(key,""))) is None:
            raise ValueError("HOLD_SOURCE_COMMIT_PIN_MISSING_"+key)
    for key in ("tokenizer_sha256","owner_model_weight_sha256",
                "model_config_sha256","rights_manifest_sha256"):
        if not sha256_hex(receipt.get(key)):
            raise ValueError("HOLD_LOCAL_SHA_RECEIPT_MISSING_"+key)
    if receipt["owner_model_weight_sha256"]!=MODEL_WEIGHT_SHA256:
        raise ValueError("HOLD_OWNER_LOCAL_WEIGHT_BYTES_UNVERIFIED")
    if receipt.get("owner_model_snapshot_verified") is not True or        receipt.get("source_rights_reviewed") is not True:
        raise ValueError("HOLD_OWNER_MODEL_RIGHTS_REVIEW_NOT_COMPLETE")
    return {"status":"PASS_DECLARED_SOURCE_SNAPSHOT_PINS",
            "receipt_sha256":hash_obj(receipt)}

def write_new(path:Path,obj):
    if path.exists():
        raise FileExistsError("REFUSE_PRIVATE_PACKET_OVERWRITE_"+path.name)
    with path.open("xb") as f:
        f.write(stable_json(obj))

def assemble(project_root:Path, authored_bundle:Path, rights_file:Path,
             source_lock_file:Path, output_dir:Path,
             threshold_freeze_file:Path|None=None,
             cal_private_file:Path|None=None):
    root=project_root.resolve(strict=True)
    # Reading/writing must remain in the research project root.
    for file in (authored_bundle,rights_file,source_lock_file):
        if not file.resolve(strict=True).is_relative_to(root):
            raise ValueError("INPUT_OUTSIDE_PROJECT_ROOT")
    out=output_dir.resolve()
    if not out.is_relative_to(root) or out.exists():
        raise ValueError("REFUSE_OUTPUT_OUTSIDE_PROJECT_OR_ALREADY_EXISTS")
    bundle=read_json(authored_bundle)
    if bundle.get("schema")!=BUNDLE_SCHEMA or bundle.get("split") not in OUT_NAMES:
        raise ValueError("BAD_AUTHORED_BUNDLE_SCHEMA_SPLIT")
    split=bundle["split"]
    rights=read_json(rights_file)
    lock=read_json(source_lock_file)
    snapshot=source_frozen(lock)
    if lock["rights_manifest_sha256"]!=hash_obj(rights):
        raise ValueError("HOLD_RIGHTS_MANIFEST_SHA_DRIFT")
    cases=bundle.get("cases")
    if not isinstance(cases,list):
        raise ValueError("MISSING_AUTHORED_CASES")
    checked=validate_partition(cases,split,rights)
    threshold=None
    if split=="PROBE":
        if not threshold_freeze_file or not cal_private_file:
            raise ValueError("HOLD_THRESHOLD_AND_CAL_REQUIRED_BEFORE_PROBE")
        for file in (threshold_freeze_file,cal_private_file):
            if not file.resolve(strict=True).is_relative_to(root):
                raise ValueError("EXTERNAL_PREPROBE_INPUT")
        threshold=read_json(threshold_freeze_file)
        pre_probe_authorization(threshold)
        cal=read_json(cal_private_file)
        if cal.get("schema")!=BUNDLE_SCHEMA or cal.get("split")!="CAL":
            raise ValueError("CAL_PRIVATE_BUNDLE_BAD_SCHEMA")
        disjoint=check_disjoint(cal["cases"],cases)
    else:
        if threshold_freeze_file or cal_private_file:
            raise ValueError("CAL_MUST_NOT_ACCESS_PROBE_THRESHOLDS")
        disjoint=None
    public=[public_view(x) for x in cases]
    raw_payload={"schema":BUNDLE_SCHEMA,"split":split,"cases":cases}
    per_slot={}
    for slot in ("A","B"):
        rows=[]
        for x in public:
            rows.append({**x,"selected_key":None,"reason":"","confidence":0})
        per_slot[slot]={"schema":SCHEMA_V4_AI,"split":split,"slot":slot,
                        "rater_type":"AI","rater_id":None,
                        "human_attestation":False,
                        "self_report_no_source_or_other_rater_access":False,
                        "cases":rows}
    receipt={
        "schema":"ttm.vm.v4.private_authoring_packet_source_QA.v1",
        "status":"PASS_AUTHORED_SOURCE_STRUCTURE_ONLY_PENDING_BLIND_REVIEWS",
        "split":split,"cases":len(cases),"bank_size":32,
        "private_bundle_sha256":hash_obj(raw_payload),
        "rights_manifest_sha256":hash_obj(rights),
        "source_lock_sha256":snapshot["receipt_sha256"],
        "public_projection_sha256":hash_obj(public),
        "source_structural_checks":checked,
        "cross_split_disjoint":disjoint,
        "threshold_receipt_sha256":(hash_obj(threshold) if threshold else None),
        "human_reviewers":0,"two_AI_blind_reviews_completed":False,
        "retriever_scored":False,"reader_forward_calls":0,
        "test_opened":False,"gpu_used":False,"science_executed":False
    }
    output_dir.mkdir(parents=True,exist_ok=False)
    names=OUT_NAMES[split]
    for name,obj in zip(names,(raw_payload,per_slot["A"],per_slot["B"],receipt)):
        write_new(output_dir/name,obj)
    return receipt

def main():
    p=argparse.ArgumentParser()
    p.add_argument("--project-root",type=Path,required=True)
    p.add_argument("--authored-bundle",type=Path,required=True)
    p.add_argument("--rights-file",type=Path,required=True)
    p.add_argument("--source-lock-file",type=Path,required=True)
    p.add_argument("--output-dir",type=Path,required=True)
    p.add_argument("--threshold-freeze",type=Path)
    p.add_argument("--cal-private-bundle",type=Path)
    a=p.parse_args()
    receipt=assemble(a.project_root,a.authored_bundle,a.rights_file,
                     a.source_lock_file,a.output_dir,
                     a.threshold_freeze,a.cal_private_bundle)
    print(json.dumps({"status":receipt["status"],"split":receipt["split"],
                      "cases":receipt["cases"],"science":False,
                      "TEST":False},sort_keys=True))
if __name__=="__main__":
    main()
