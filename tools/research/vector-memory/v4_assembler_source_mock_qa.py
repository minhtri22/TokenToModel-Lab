#!/usr/bin/env python3
"""20 independent packet-assembler source/mock checks. NO ACTUAL CAL OR PROBE."""
from __future__ import annotations
import argparse
import ast
import json
from pathlib import Path
import v4_cal_probe_private_packet_assembler as pack
from v4_source_rights_annotation_custody import MODEL_REVISION,MODEL_WEIGHT_SHA256

def mock_lock():
    return {
       "model_revision":MODEL_REVISION,"weights_sha256":MODEL_WEIGHT_SHA256,
       "source_commit_sha":"a"*40,"baseline_source_git_blob":"b"*40,
       "tokenizer_sha256":"c"*64,
       "owner_model_weight_sha256":MODEL_WEIGHT_SHA256,
       "model_config_sha256":"d"*64,"rights_manifest_sha256":"e"*64,
       "owner_model_snapshot_verified":True,"source_rights_reviewed":True
    }

def refused(fn):
    try: fn()
    except (ValueError,FileNotFoundError): return True
    return False

def audit():
    src=Path(pack.__file__).read_text(encoding="utf-8")
    result={}
    def one(label,ok):result[label]=bool(ok)
    good=mock_lock()
    one("01_source_compiles_AST",isinstance(ast.parse(src),ast.Module))
    one("02_CAL_4_exact_expected_names",len(pack.OUT_NAMES["CAL"])==4)
    one("03_PROBE_4_exact_expected_names",len(pack.OUT_NAMES["PROBE"])==4)
    one("04_both_splits_distinct_names",not set(pack.OUT_NAMES["CAL"])&set(pack.OUT_NAMES["PROBE"]))
    one("05_upstream_revision_pinned",pack.MODEL_REVISION==MODEL_REVISION)
    one("06_upstream_weight_SHA_pinned",pack.MODEL_WEIGHT_SHA256==MODEL_WEIGHT_SHA256)
    one("07_mock_source_lock_structural_pass",pack.source_frozen(good)["status"]=="PASS_DECLARED_SOURCE_SNAPSHOT_PINS")
    one("08_wrong_revision_HOLD",refused(lambda:pack.source_frozen({**good,"model_revision":"main"})))
    one("09_wrong_weight_SHA_HOLD",refused(lambda:pack.source_frozen({**good,"weights_sha256":"f"*64})))
    one("10_missing_tokenizer_SHA_HOLD",refused(lambda:pack.source_frozen({**good,"tokenizer_sha256":None})))
    one("11_owner_rights_false_HOLD",refused(lambda:pack.source_frozen({**good,"source_rights_reviewed":False})))
    one("12_model_owner_verified_false_HOLD",refused(lambda:pack.source_frozen({**good,"owner_model_snapshot_verified":False})))
    one("13_wrong_local_weight_SHA_HOLD",refused(lambda:pack.source_frozen({**good,"owner_model_weight_sha256":"f"*64})))
    one("14_PROBE_requires_prior_CAL_and_threshold", "HOLD_THRESHOLD_AND_CAL_REQUIRED_BEFORE_PROBE" in src)
    one("15_PROBE_verifies_CAL_sha", "HOLD_CAL_PRIVATE_BYTES_NOT_FROZEN_THRESHOLD_RECEIPT" in src)
    one("16_PROBE_verifies_rights_hash", "HOLD_CAL_RIGHTS_CUSTODY_HASH_MISMATCH" in src)
    one("17_split_four_family_disjoint_check", "check_disjoint(cal[\\"cases\\"],cases)" in src or "check_disjoint(cal[\"cases\"],cases)" in src)
    one("18_source_output_confined_to_project", "is_relative_to(root)" in src)
    one("19_private_no_overwrite", "FileExistsError" in src and "open(\"xb\")" in src)
    one("20_no_model_or_science_execution", "model.forward(" not in src and
        "Reader(" not in src and "ONE_SHOT_STARTED" not in src and "torch.load" not in src)
    return result

def main():
    p=argparse.ArgumentParser()
    p.add_argument("--out",type=Path,required=True)
    args=p.parse_args()
    if args.out.exists():raise FileExistsError("REFUSE_QA_OVERWRITE")
    checks=audit();passed=sum(bool(x) for x in checks.values())
    obj={"schema":"ttm.vm.v4.packet_assembler.source_mock_qa.v1",
         "status":"PASS_ASSEMBLER_SOURCE_MOCK_QA" if passed==len(checks) else "HOLD_ASSEMBLER_SOURCE_MOCK_QA",
         "checks":checks,"qa_passed":passed,"qa_total":len(checks),
         "data":"ONLY_DUMMY_SOURCE_LOCK_IN_MEMORY_NOT_REAL_RIGHTS",
         "cal_generated":False,"probe_generated":False,
         "Reader_forward_calls":0,"test_opened":False,"gpu_used":False}
    args.out.parent.mkdir(parents=True,exist_ok=True)
    args.out.write_text(json.dumps(obj,indent=2,sort_keys=True)+"\n",encoding="utf8")
    print(json.dumps({"status":obj["status"],"qa":f"{passed}/{len(checks)}","science":False}))
    if passed!=len(checks):raise SystemExit("ASSEMBLER_SOURCE_MOCK_QA_FAIL")
if __name__=="__main__":
    main()
