#!/usr/bin/env python3
"""TTM T5: one integrated owner-local first-op discovery batch on Windows.

- Accepts only true D01/D02 P02 reference zip (created earlier, SHA locked).
- Fast-forward clean project-local worktree only, no merges to main.
- Builds isolated pinned llama copies: trace-only and trace+GELU_ERF.
- Builds a new 2-fixture, F32 KV, Flash OFF probe for each variant.
- Runs exactly 2 new native fixtures per variant ONCE, then separate signed
  tensor auditors; never accesses C01..C04 confirmatory or old fixtures.
- Preserves partial evidence and never retries automatically.
"""
from __future__ import annotations
import argparse
import hashlib
import json
import os
from pathlib import Path
import subprocess
import sys
import zipfile

BASE_ROOT=Path("D:/WORK/RESEARCH/TokenToModel-Lab")
BRANCH="research/ttm-t5-f32-strict-logit-parity-diagnostic-20261109"
WORK_REL="worktrees/ttm-t5-kvflash-preview-20261109"
STAGE_REL="_tmp/ttm_t5_exact_root_discovery_run_v1_20261110"
ISOLATION_REL="_tmp/ttm_t5_exact_root_v1_20261110"
GGUF_REL="_tmp/ttm_t5_trained_f32_v1/TTM-Small4M-T4-step1024-F32.gguf"
GGUF_SHA="5bdc904e6c51af04a4223219f36e6bc2e687f60fd6e17dc24508f3eb7489e4e5"
REF_ZIP_SHA="8e289485e9af2ae3de3aa8d8e19150b4d062dad395189540483ecb424be4bc10"
REF_SHA="9cc5fc2db1f95e7e863a285eb279b28b7a383b81a4f890d7ec0f79b788b995e0"
REF_NAME="TTM_T5_D01D02_P02_TRUE_SIGNED_TRACE_20261110.jsonl"
PREREG_BLOB="82fdd9fe716579181db648caa69170fb63d115a6"
LLAMA_COMMIT="372dc5ca157276beb6c67b2e92477e8d662e964a"
DLL_NAMES=("llama.dll","ggml.dll","ggml-base.dll","ggml-cpu.dll")
OWNER_LITERAL="I_APPROVE_TTM_T5_FIRSTOP_NEW_D01_D02_DISCOVERY_ONLY"

def sha(p):
    h=hashlib.sha256()
    with p.open("rb") as f:
        for c in iter(lambda:f.read(1<<20),b""):h.update(c)
    return h.hexdigest()

def gitblob(p):
    b=p.read_bytes()
    return hashlib.sha1(b"blob "+str(len(b)).encode()+b"\0"+b).hexdigest()

def root_member(root,p,regular=False):
    x=p.resolve(strict=True)
    if not x.is_relative_to(root) or (regular and not x.is_file()):
        raise ValueError("PROJECT_BOUNDED_EXISTING_FILE_REQUIRED:"+str(p))
    return x

def call(label,argv,cwd,log,timeout,env=None):
    if log.exists():raise FileExistsError("STAGE_LOG_EXISTS:"+label)
    try:
        p=subprocess.run([str(x) for x in argv],cwd=str(cwd),env=env,
             capture_output=True,text=True,errors="replace",
             check=False,timeout=timeout)
    except subprocess.TimeoutExpired as e:
        log.write_text("TIMED_OUT_NO_RETRY:"+repr(e)+"\n",encoding="utf-8")
        raise RuntimeError(label+"_TIMEOUT_DO_NOT_RERUN") from e
    log.write_text("ARGS="+json.dumps([str(x) for x in argv])+
         "\nEXIT_CODE="+str(p.returncode)+"\nSTDOUT:\n"+p.stdout+
         "\nSTDERR:\n"+p.stderr+"\n",encoding="utf-8")
    if p.returncode:
        raise RuntimeError(label+"_FAILED_EXIT_"+str(p.returncode)+"_READ_LOG")
    print("T5_STAGE="+label,flush=True)
    return p.stdout

def main():
    ap=argparse.ArgumentParser()
    ap.add_argument("--project-root",type=Path,required=True)
    ap.add_argument("--reference-zip",type=Path,required=True)
    ap.add_argument("--expected-head",required=True)
    ap.add_argument("--approve-exact-discovery",required=True)
    args=ap.parse_args()
    if (os.name!="nt" or sys.version_info[:2]!=(3,12)
        or args.approve_exact_discovery!=OWNER_LITERAL):
        raise ValueError("WINDOWS_PYTHON312_EXACT_OWNER_SCOPE_REQUIRED")
    root=args.project_root.resolve(strict=True)
    if os.path.normcase(str(root))!=os.path.normcase(str(BASE_ROOT)):
        raise ValueError("ROOT_IS_NOT_TTM")
    source_work=root_member(root,root/WORK_REL)
    zipfile_path=root_member(root,args.reference_zip,regular=True)
    gguf=root_member(root,root/GGUF_REL,regular=True)
    if sha(zipfile_path)!=REF_ZIP_SHA or sha(gguf)!=GGUF_SHA:
        raise ValueError("REFERENCE_ZIP_OR_GGUF_SHA_MISMATCH")
    stage=root/STAGE_REL
    isolation=root/ISOLATION_REL
    if stage.exists() or isolation.exists():
        raise FileExistsError("DISCOVERY_OR_ISOLATION_ALREADY_EXISTS_NO_RETRY")
    # Validate PR16 is still on the T5 branch: no main update.
    if "TokenToModel-Lab" not in str(source_work):
        raise ValueError("WORKTREE_IDENTITY_MISMATCH")
    status=subprocess.run(["git.exe","-C",str(source_work),"status","--porcelain"],
        capture_output=True,text=True,timeout=20)
    if status.returncode!=0 or status.stdout.strip():
        raise ValueError("ORIGINAL_WORKTREE_NOT_CLEAN")
    origin=subprocess.run(["git.exe","-C",str(root),"remote","get-url","origin"],
        capture_output=True,text=True,timeout=20)
    if origin.returncode or "minhtri22/TokenToModel-Lab" not in origin.stdout.replace(".git",""):
        raise ValueError("GITHUB_PROJECT_ORIGIN_MISMATCH")
    stage.mkdir(parents=True,exist_ok=False)
    receipt={"schema":"ttm.t5.firstop.d01d02.two_native_variants.v1",
        "status":"STARTED_PINNED_DISCOVERY_NO_CONFIRMATORY",
        "expected_head":args.expected_head,
        "GGUF_SHA256":GGUF_SHA,"reference_zip_SHA256":REF_ZIP_SHA,
        "source_isolation":"NOT_EXECUTED","reference":"NOT_IMPORTED",
        "variants":{},"confirmatory":"NOT_EXECUTED",
        "historical_8_32":"NOT_RERUN","strict_threshold":0.001,
        "training":False,"TEST":False,"main":"UNCHANGED","lineage":"UNCHANGED"}
    try:
        # Fast-forward ONLY, on dedicated project-local T5 worktree.
        call("01_fetch_branch",
             ["git.exe","-C",str(source_work),"fetch","--no-tags","origin",
               "refs/heads/"+BRANCH],
             stage,stage/"01_fetch_branch.log",90)
        fetched=call("02_verify_fetched_HEAD",
             ["git.exe","-C",str(source_work),"rev-parse","FETCH_HEAD"],
             stage,stage/"02_verify_fetched_HEAD.log",20).strip()
        if fetched!=args.expected_head:raise ValueError("REMOTE_BRANCH_HEAD_CHANGED")
        call("03_ff_only",
             ["git.exe","-C",str(source_work),"merge","--ff-only","FETCH_HEAD"],
             stage,stage/"03_ff_only.log",30)
        actual=call("04_worktree_head",
             ["git.exe","-C",str(source_work),"rev-parse","HEAD"],
             stage,stage/"04_worktree_head.log",15).strip()
        if actual!=args.expected_head:raise ValueError("WORKTREE_HEAD_NOT_EXACT")
        rel="tools/pilot_t5/exact_root_v1"
        prereg=root_member(root,source_work/"artifacts/qa/ttm-t5-parity/TTM_T5_EXACT_FIRST_OP_NEW_FIXTURES_INTEGRATED_PREREG_20261110.json",True)
        if gitblob(prereg)!=PREREG_BLOB:raise ValueError("PREREG_GIT_BLOB_MISMATCH")
        qa_script=root_member(root,source_work/rel/"test_integrated_static_protocol.py",True)
        call("04b_static_16_readonly_QA",
            [sys.executable,qa_script],stage,stage/"04b_static_16_readonly_QA.log",40)
        receipt["static_qa"]="PASS_16_OF_16_PROTOCOL_TESTS"
        plan=json.loads(prereg.read_text("utf-8"))
        if [x["fixture_id"] for x in plan["fixtures"] if x["partition"]=="discovery"]!=["D01","D02"]:
            raise ValueError("DISCOVERY_NOT_EXACT")
        ref=stage/REF_NAME
        with zipfile.ZipFile(zipfile_path,"r") as z:
            if z.namelist()!=[REF_NAME]:raise ValueError("ZIP_ENTRIES_NOT_CANONICAL")
            ref.write_bytes(z.read(REF_NAME))
        if sha(ref)!=REF_SHA:raise ValueError("EXTRACTED_P02_SIGNED_TRACE_SHA_MISMATCH")
        receipt["reference"]="PASS_IMPORTED_TRUE_P02_42_TENSOR_ROWS"
        # All real llama code edits confined to two new sub-worktrees in TTM.
        prep=root_member(root,source_work/rel/"prepare_isolated_llama_trace_gelu_sources.py",True)
        call("05_isolate_sources",
             [sys.executable,prep,"--project-root",root],
             stage,stage/"05_isolate_sources.log",150)
        isolation_receipt=root_member(root,isolation/"SOURCE_ISOLATION_RECEIPT.json",True)
        isolated=json.loads(isolation_receipt.read_text("utf-8"))
        if isolated["status"]!="PASS_TWO_ISOLATED_SOURCE_VARIANTS_READY_FOR_BUILD":
            raise ValueError("SOURCE_ISOLATION_NOT_PASS")
        receipt["source_isolation"]=sha(isolation_receipt)
        for label in ("trace_only","trace_gelu_erf"):
            source=root_member(root,isolation/label)
            out=stage/label
            out.mkdir(parents=True,exist_ok=False)
            llama_build=out/"llama_build"
            probe_build=out/"probe_build"
            opts=["-G","Visual Studio 17 2022","-A","x64",
              "-DBUILD_SHARED_LIBS=ON","-DLLAMA_BUILD_TESTS=OFF",
              "-DLLAMA_BUILD_EXAMPLES=OFF","-DLLAMA_CURL=OFF","-DGGML_NATIVE=ON"]
            call(label+"_06_config_llama",
                ["cmake.exe","-S",source,"-B",llama_build,*opts],
                out,out/"06_config_llama.log",180)
            call(label+"_07_build_llama",
                ["cmake.exe","--build",llama_build,"--config","Release",
                 "--target","llama","--parallel","4"],
                out,out/"07_build_llama.log",900)
            call(label+"_08_config_probe",
                ["cmake.exe","-S",source_work/rel,"-B",probe_build,
                 "-G","Visual Studio 17 2022","-A","x64",
                 "-DLLAMA_SOURCE_ROOT="+str(source),
                 "-DLLAMA_BUILD_ROOT="+str(llama_build)],
                out,out/"08_config_probe.log",180)
            call(label+"_09_build_probe",
                ["cmake.exe","--build",probe_build,"--config","Release",
                 "--target","ttm_t5_firstop_trace_probe","--parallel","4"],
                out,out/"09_build_probe.log",600)
            dll_dir=root_member(root,llama_build/"bin/Release")
            dll_paths={name:root_member(root,dll_dir/name,True) for name in DLL_NAMES}
            exe=root_member(root,probe_build/"Release/ttm_t5_firstop_trace_probe.exe",True)
            env=dict(os.environ)
            env["PATH"]=str(dll_dir)+os.pathsep+env.get("PATH","")
            self_stdout=call(label+"_10_no_model_constants",
                [exe,"--self-check"],
                out,out/"10_self_check.log",40,env)
            parsed=json.loads(self_stdout)
            if parsed.get("schema")!="ttm.t5.firstop.discover_two.compiled_constants.v1":
                raise ValueError("COMPILED_CONSTANTS_SCHEMA")
            if parsed.get("model_loaded") is not False or parsed.get("native_inference") is not False:
                raise ValueError("SELF_CHECK_MODEL_ACCESS")
            if [(x["fixture_id"],x["token_ids"]) for x in parsed["fixtures"]]!=[
                ("D01",[1281]),("D02",[1406,971,566,1092,1587])]:
                raise ValueError("COMPILED_INPUTS_CHANGED")
            if parsed["arms"]!=[{"id":"S1_F32_NO_FLASH","kv":"F32","flash":"DISABLED"}]:
                raise ValueError("COMPILED_ARM_CHANGED")
            output=out/"D01_D02_F32_OFF_NATIVE.jsonl"
            print("T5_NATIVE_ONE_SHOT="+label+" D01_D02",flush=True)
            stdout=call(label+"_11_native_two",
                [exe,root,gguf,output],out,out/"11_native.log",300,env)
            if "T5_FIRST_OP_DISCOVERY_COMPLETE_ROWS_2" not in stdout:
                raise ValueError("NATIVE_TWO_COMPLETE_MARKER_MISSING")
            trace=out/"D01_D02_F32_OFF_NATIVE.jsonl.trace.jsonl"
            if not output.is_file() or not trace.is_file():
                raise ValueError("NATIVE_DISCOVERY_OUTPUT_MISSING")
            auditor=root_member(root,source_work/rel/"independent_firstop_signed_tensor_audit.py",True)
            report=out/"INDEPENDENT_SIGNED_STAGE_AUDIT.json"
            call(label+"_12_independent_signed_audit",
                 [sys.executable,auditor,
                  "--prereg",prereg,"--reference",ref,
                  "--native-trace",trace,"--native-logits",output,
                  "--output",report],out,out/"12_independent_audit.log",90)
            evidence=json.loads(report.read_text("utf-8"))
            if evidence.get("status")!="PASS_TRACE_PROTOCOL_MEASURED_CAUSE_NOT_PROVEN":
                raise ValueError("SIGNED_AUDIT_STATUS_FAIL")
            receipt["variants"][label]={
                "source_git_blobs":isolated[label],
                "compiled_exe_sha256":sha(exe),
                "runtime_dll_sha256":{name:sha(p) for name,p in dll_paths.items()},
                "native_sha256":sha(output),"trace_sha256":sha(trace),
                "audit_sha256":sha(report),"status":"PASS_TWO_NATIVE_ROWS_SCOPED"}
        receipt["status"]="DISCOVERY_TWO_VARIANTS_COMPLETED_UNADJUDICATED_CONFIRMATORY_HOLD"
    except Exception as e:
        receipt["status"]="HOLD_DISCOVERY_FAILED_OR_PARTIAL_NO_RERUN"
        receipt["failure"]=type(e).__name__+":"+str(e)
    finally:
        output=stage/"DISCOVERY_RUN_RECEIPT.json"
        with output.open("x",encoding="utf-8",newline="\n") as fp:
            json.dump(receipt,fp,sort_keys=True,indent=2,ensure_ascii=False)
            fp.write("\n")
        print("DISCOVERY_STATUS="+receipt["status"],flush=True)
        print("DISCOVERY_RECEIPT="+str(output),flush=True)
        print("DISCOVERY_RECEIPT_SHA256="+sha(output),flush=True)
        print("NATIVE_32_REPLAY=NO; CONFIRMATORY=NOT_EXECUTED; MERGE=HOLD",flush=True)
    if receipt["status"]!="DISCOVERY_TWO_VARIANTS_COMPLETED_UNADJUDICATED_CONFIRMATORY_HOLD":
        raise SystemExit(2)

if __name__=="__main__":
    try:main()
    except Exception as e:
        print("TTM_T5_DISCOVERY_DENIED_BEFORE_OR_AFTER_PRECHECK:"
              +type(e).__name__+":"+str(e),file=sys.stderr)
        raise SystemExit(3)
