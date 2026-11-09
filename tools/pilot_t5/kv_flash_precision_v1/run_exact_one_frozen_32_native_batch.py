#!/usr/bin/env python3
"""Owner-approved one shot: EXACT frozen SYN01..SYN08 x S0..S3 TTM native.

No training, no TEST/Q1Q2, no checkpoint modification, no historical fixture
replay, no git modification. A single llama.cpp binary invocation produces
32 paired rows, audited against a separately generated genuine P02 reference.
Never re-run if evidence exists; preserve partial results on failure.
"""
from __future__ import annotations
import argparse
import hashlib
import json
import os
from pathlib import Path
import subprocess
import sys

ROOT=Path("D:/WORK/RESEARCH/TokenToModel-Lab")
RUN_REL="_tmp/ttm_t5_kvflash_frozen_new_32_native_one_shot_v1_20261110"
WORK_REL="worktrees/ttm-t5-kvflash-preview-20261109"
BINARY_REL="_tmp/ttm_t5_kvflash_binary_reference_stage_v1_20261110/build/Release/ttm_t5_kvflash_probe.exe"
GGUF_REL="_tmp/ttm_t5_trained_f32_v1/TTM-Small4M-T4-step1024-F32.gguf"
REF_REL="_tmp/ttm_t5_kvflash_reference_input_v1_20261110/REFERENCE_F32_SYN01_SYN08.jsonl"
RECOVERY_REL="_tmp/ttm_t5_kvflash_loader_recovery_v1_20261110/RECOVERY_RECEIPT.json"
DLL_REL="_tmp/ttm_t2/build/bin/Release"
PIN_BINARY="0da91785a0882dd1b5a04cce4dc050886b54e0fe0f17e66f66802638b3760537"
PIN_GGUF="5bdc904e6c51af04a4223219f36e6bc2e687f60fd6e17dc24508f3eb7489e4e5"
PIN_REFERENCE="d6f367269df610a4e1c93edbff9a4dcffb7f0e0b6bd5f77247c5c90394de176c"
PIN_RECOVERY="2648b84558a503de66a2e2a0e09094561123d64578eefa82b26bf85fcfdc1be2"
PIN_PREREG_BLOB="3b12cc1883ab20e2d9e3a92e6907586c1b4cad36"
PIN_WORKTREE_HEAD="888adde84e0e4fbe8cbaae801ed4d9687e6b4bb8"
PIN_AUDITOR_BLOB="18dc82d845f228ea4e5b349ac5cabf9f1110a252"
DLL_SHA={
"llama.dll":"fff1f9ef4fc40c0946bf9be229d9eddeb06060b05496527272b64cd9ec0f9859",
"ggml.dll":"a47e350ea98666a781208d11d2d820e14c6ae82b9bb7c5c15193342030528f9f",
"ggml-base.dll":"d8c7b4c509748292670e9720c2676c918262a1ce4782cbb34627c595298541f3",
"ggml-cpu.dll":"fae303eda4b1a8c93aaf61be330696662752a817204be88944454d0255e2c434"
}
OWNER_APPROVAL_LITERAL="I_APPROVE_ONE_TTM_T5_FROZEN_NEW_32_NATIVE_BATCH"

def sha(path):
    h=hashlib.sha256()
    with path.open("rb") as f:
        for c in iter(lambda:f.read(1<<20),b""):
            h.update(c)
    return h.hexdigest()

def blob(path):
    data=path.read_bytes()
    return hashlib.sha1(b"blob "+str(len(data)).encode()+b"\0"+data).hexdigest()

def project_file(root,path):
    p=Path(path).resolve(strict=True)
    if not p.is_relative_to(root) or not p.is_file():
        raise ValueError("NOT_EXISTING_REGULAR_FILE_INSIDE_PROJECT:"+str(path))
    return p

def exe(argv,cwd,env,log,timeout):
    if log.exists():raise FileExistsError("ONE_SHOT_LOG_ALREADY_EXISTS")
    try:
        p=subprocess.run([str(x) for x in argv],cwd=str(cwd),env=env,
             capture_output=True,text=True,errors="replace",
             timeout=timeout,check=False)
        content="ARGV="+json.dumps([str(x) for x in argv])+"\n"
        content+="RETURN_CODE="+str(p.returncode)+"\nSTDOUT:\n"+p.stdout+"\nSTDERR:\n"+p.stderr+"\n"
        log.write_text(content,encoding="utf-8")
        if p.returncode!=0:raise RuntimeError("NATIVE_OR_AUDIT_FAILED_CODE_"+str(p.returncode))
        return p.stdout
    except subprocess.TimeoutExpired as err:
        log.write_text("TIMED_OUT_NO_AUTOMATIC_RETRY\n"+str(err)+"\n",encoding="utf-8")
        raise RuntimeError("ONE_SHOT_TIMEOUT_NO_RETRY") from err

def main():
    ap=argparse.ArgumentParser()
    ap.add_argument("--approve-one-frozen-batch",required=True)
    args=ap.parse_args()
    if args.approve_one_frozen_batch!=OWNER_APPROVAL_LITERAL:
        raise ValueError("OWNER_BATCH_APPROVAL_LITERAL_NOT_PRESENT")
    if os.name!="nt" or sys.version_info[:2]!=(3,12):
        raise ValueError("WINDOWS_PY312_REQUIRED")
    root=ROOT.resolve(strict=True)
    if os.path.normcase(str(root))!=os.path.normcase(str(ROOT)):
        raise ValueError("EXACT_PROJECT_ROOT_MISMATCH")
    run=root/RUN_REL
    if run.exists():
        raise FileExistsError("ONE_SHOT_ALREADY_EXISTS_OR_PARTIAL_NO_REPEAT")
    work=root/WORK_REL
    binary=project_file(root,root/BINARY_REL)
    gguf=project_file(root,root/GGUF_REL)
    reference=project_file(root,root/REF_REL)
    recovery=project_file(root,root/RECOVERY_REL)
    prereg=project_file(root,work/"artifacts/qa/ttm-t5-parity/TTM_T5_KV_FLASH_2X2_FRESH_SYNTHETIC_PREREG_20261109.json")
    auditor=project_file(root,work/"tools/pilot_t5/kv_flash_precision_v1/audit_new_native_results.py")
    if (sha(binary)!=PIN_BINARY or sha(gguf)!=PIN_GGUF
        or sha(reference)!=PIN_REFERENCE or sha(recovery)!=PIN_RECOVERY
        or blob(prereg)!=PIN_PREREG_BLOB or blob(auditor)!=PIN_AUDITOR_BLOB):
        raise ValueError("FROZEN_INPUT_SHA_OR_GIT_BLOB_MISMATCH")
    dlls={key:project_file(root,root/DLL_REL/key) for key in DLL_SHA}
    if any(sha(p)!=DLL_SHA[name] for name,p in dlls.items()):
        raise ValueError("PINNED_RUNTIME_DLL_CHANGED")
    rec=json.loads(recovery.read_text(encoding="utf-8"))
    if (rec.get("status")!="PASS_BINARY_SELF_CHECK_AND_REAL_REFERENCE_QA_NATIVE_32_HOLD"
        or rec.get("native_2x2")!="0_OF_32_NOT_EXECUTED"
        or rec.get("compiled_existing_binary_sha256")!=PIN_BINARY
        or rec.get("reference_f32_8x2048_sha256")!=PIN_REFERENCE):
        raise ValueError("RECOVERY_GATE_NOT_PASS")
    plan=json.loads(prereg.read_text("utf-8"))
    if (plan["original_pins"]["final_logits_acceptance_max_abs"]!=0.001
        or plan["control_design"]["expected_runs"]!=32
        or len(plan["control_design"]["new_fixtures"])!=8):
        raise ValueError("FROZEN_PREREG_CHANGED")
    git=subprocess.run(["git.exe","-C",str(work),"rev-parse","HEAD"],
        capture_output=True,text=True,timeout=12)
    if git.returncode!=0 or git.stdout.strip()!=PIN_WORKTREE_HEAD:
        raise ValueError("WORKTREE_HEAD_NO_LONGER_EXACT")
    status=subprocess.run(["git.exe","-C",str(work),"status","--porcelain","--untracked-files=all"],
        capture_output=True,text=True,timeout=12)
    if status.returncode or status.stdout.strip():
        raise ValueError("WORKTREE_NOT_CLEAN")
    run.mkdir(parents=True,exist_ok=False)
    result={
        "schema":"ttm.t5.kvflash.new_synthetic_one_shot_native.run.v1",
        "owner_approved_exact_scope":True,
        "status":"STARTED_ONE_SHOT",
        "old_strict_fail_7_of_8":"PRESERVED",
        "strict_abs_threshold":0.001,
        "checkpoint_trained":False,"test_accessed":False,"q1q2_accessed":False,
        "native_output":"NOT_EXECUTED","audit":"NOT_EXECUTED",
        "inputs_sha256":{"exe":PIN_BINARY,"gguf":PIN_GGUF,
           "reference":PIN_REFERENCE,"recovery":PIN_RECOVERY,"dll":DLL_SHA},
    }
    try:
        output=run/"NATIVE_F32_KVFLASH_SYN01_SYN08_X_S0_S3.jsonl"
        runlog=run/"01_native_one_shot.log"
        env=dict(os.environ)
        env["PATH"]=str(root/DLL_REL)+os.pathsep+env.get("PATH","")
        print("NATIVE_2X2_ONE_SHOT=STARTED_EXACT_32",flush=True)
        stdout=exe([binary,root,gguf,output],run,env,runlog,timeout=600)
        if "T5_NEW_SYNTHETIC_2X2_NATIVE_RUN=COMPLETE_ROWS_32" not in stdout:
            raise ValueError("NATIVE_32_COMPLETE_MARKER_NOT_PRESENT")
        result["native_output"]="GENERATED_CLAIMED_32_ROWS"
        result["native_output_sha256"]=sha(output)
        # Independent evaluator uses fixed 0.001 and original reference.
        audit_file=run/"AUDIT_FROZEN_NEW_32.json"
        print("NATIVE_2X2_INDEPENDENT_AUDIT=STARTED",flush=True)
        audit_out=exe([sys.executable,auditor,"--prereg",prereg,
             "--reference",reference,"--native",output,"--out",audit_file],
             run,env,run/"02_independent_native_32_audit.log",timeout=120)
        summary=json.loads(audit_out)
        if summary.get("status")!="NEW_SYNTHETIC_AUDIT_COMPLETE":
            raise ValueError("NATIVE_32_INDEPENDENT_AUDIT_NOT_COMPLETED")
        result["audit"]="PASS_32_ROW_PROTOCOL_AND_MEASUREMENT_COMPLETE"
        result["audit_sha256"]=sha(audit_file)
        result["arm_strict_pass_counts"]=summary["arm_pass_counts"]
        result["status"]="ONE_FROZEN_32_NATIVE_BATCH_COMPLETED_UNADJUDICATED"
    except Exception as err:
        result["failure"]=type(err).__name__+": "+str(err)
        result["status"]="HOLD_ONE_SHOT_FAILED_OR_PARTIAL_DO_NOT_RERUN"
    finally:
        receipt=run/"RUN_RECEIPT.json"
        with receipt.open("x",encoding="utf-8") as f:
            json.dump(result,f,ensure_ascii=False,indent=2,sort_keys=True)
            f.write("\n")
        print("NATIVE_RUN_STATUS="+result["status"],flush=True)
        print("NATIVE_RUN_RECEIPT="+str(receipt),flush=True)
        print("NATIVE_RUN_RECEIPT_SHA256="+sha(receipt),flush=True)
        print("ORIGINAL_STRICT=FAIL_7_OF_8_PRESERVED",flush=True)
    if result["status"]!="ONE_FROZEN_32_NATIVE_BATCH_COMPLETED_UNADJUDICATED":
        raise SystemExit(2)

if __name__=="__main__":
    try:
        main()
    except Exception as exc:
        print("T5_NATIVE_BATCH_BLOCKED_BEFORE_EXECUTION:"
              +type(exc).__name__+":"+str(exc),file=sys.stderr)
        raise SystemExit(3)
