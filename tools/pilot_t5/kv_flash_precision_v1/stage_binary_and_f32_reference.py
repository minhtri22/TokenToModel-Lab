#!/usr/bin/env python3
"""One-stage build + independent F32 reference + static/synthetic QA ONLY.

Does NOT call native GGUF inference, does NOT replay old fixtures, does NOT
train or use TEST. All working files stay in TTM project _tmp and worktrees.
Windows Python 3.12, Visual Studio 2022, CMake, pinned llama.cpp required.
"""
from __future__ import annotations
import argparse
import hashlib
import json
import os
from pathlib import Path
import shutil
import subprocess
import sys
import time

PROJECT_FIXED = Path("D:/WORK/RESEARCH/TokenToModel-Lab")
BRANCH = "research/ttm-t5-f32-strict-logit-parity-diagnostic-20261109"
LLAMA_COMMIT = "372dc5ca157276beb6c67b2e92477e8d662e964a"
P02_BLOB = "9762343e06cf800b50574c2871ae1ed58537fb18"
PLAN_BLOB = "3b12cc1883ab20e2d9e3a92e6907586c1b4cad36"
CKPT_SHA = "cb985751795c8328ad65acf7ca4c1033ce35182c1bfbdb8c38550de629cb271b"
GGUF_SHA = "5bdc904e6c51af04a4223219f36e6bc2e687f60fd6e17dc24508f3eb7489e4e5"
GGUF_REL = "_tmp/ttm_t5_trained_f32_v1/TTM-Small4M-T4-step1024-F32.gguf"
WORKTREE_REL = "worktrees/ttm-t5-kvflash-preview-20261109"
LLAMA_REL = "_tmp/ttm_t2/llama.cpp"
LLAMA_BUILD_REL = "_tmp/ttm_t2/build/upstream_llama"
STAGE_REL = "_tmp/ttm_t5_kvflash_binary_reference_stage_v1_20261110"
EXE_REL = "build/Release/ttm_t5_kvflash_probe.exe"
SRC_REL = "tools/pilot_t5/kv_flash_precision_v1"

def sha(path):
    h=hashlib.sha256()
    with Path(path).open("rb") as f:
        for block in iter(lambda:f.read(1<<20), b""):h.update(block)
    return h.hexdigest()

def git_blob(path):
    b=Path(path).read_bytes()
    return hashlib.sha1(b"blob "+str(len(b)).encode()+b"\0"+b).hexdigest()

def within(root, child, *, exists=True):
    p=Path(child).resolve(strict=exists)
    if not p.is_relative_to(root):
        raise ValueError("DENIED_OUTSIDE_TTM_PROJECT")
    return p

def invoke(args, *, cwd, env, log_path, seconds):
    # No shell interpretation; bounded launch with stdout/stderr redirected to
    # project-local files (no Windows PowerShell 5.1 NativeCommandError).
    if log_path.exists():raise FileExistsError("LOG_OUTPUT_ALREADY_EXISTS:"+str(log_path))
    result=subprocess.run([str(x) for x in args],cwd=str(cwd),env=env,
                          capture_output=True,text=True,errors="replace",
                          timeout=seconds,check=False)
    log_path.write_text(
        "ARGV: "+json.dumps([str(x) for x in args],ensure_ascii=False)+"\n"
        +"RETURN_CODE="+str(result.returncode)+"\nSTDOUT:\n"+result.stdout
        +"\nSTDERR:\n"+result.stderr+"\n",encoding="utf-8")
    if result.returncode:
        raise RuntimeError("STAGE_COMMAND_FAILED:"+log_path.name+":EXIT_"+str(result.returncode))
    return result.stdout

def main():
    if os.name!="nt":
        raise RuntimeError("WINDOWS_ONLY_STAGE")
    ap=argparse.ArgumentParser()
    ap.add_argument("--project-root",type=Path,default=PROJECT_FIXED)
    ap.add_argument("--expected-head",required=True)
    ap.add_argument("--checkpoint",type=Path,default=None,
                    help="Existing ORIGINAL T4 1024 .pt inside this project; optional for binary-only stage.")
    a=ap.parse_args()
    if not (len(a.expected_head)==40 and all(x in "0123456789abcdef" for x in a.expected_head)):
        raise ValueError("EXPECTED_SHA_40_LOWERCASE_REQUIRED")
    root=a.project_root.resolve(strict=True)
    if root!=PROJECT_FIXED.resolve(strict=True):raise ValueError("PROJECT_ROOT_DIFFERENT")
    work=within(root,root/WORKTREE_REL)
    stage=within(root,root/STAGE_REL,exists=False)
    if stage.exists():raise FileExistsError("STAGE_ALREADY_EXISTS_NO_OVERWRITE")
    if not (root/".git").exists() or not (work/".git").exists():
        raise ValueError("WORKTREE_OR_GIT_MISSING")
    stage.mkdir(parents=True,exist_ok=False)
    receipts={"schema":"ttm.t5.kvflash.binary_reference.stage.v1",
       "date":"2026-11-10","expected_git_head":a.expected_head,
       "status":"HOLD_STAGE_STARTED","executed_native_2x2":False,
       "original_strict":"FAIL_7_OF_8_PRESERVED",
       "training":False,"test_read":False,"q1q2_read":False,"steps":{},
       "compile_binary":"NOT_COMPILED","reference":"NOT_EXECUTED"}
    (stage/"STAGE_STARTED.json").write_text(json.dumps(receipts,indent=2)+"\n",encoding="utf-8")
    env=dict(os.environ)
    # Compilers should use project-local temp files wherever toolchains honor TMP.
    localtemp=stage/"scratch"
    localtemp.mkdir()
    env["TMP"]=env["TEMP"]=env["TMPDIR"]=str(localtemp)
    python=Path(sys.executable)
    git=shutil.which("git.exe")
    cmake=shutil.which("cmake.exe")
    if not git or not cmake:raise RuntimeError("GIT_EXE_OR_CMAKE_EXE_NOT_FOUND")

    def run(label, cmd, *, cwd=work, timeout=100):
        print("STAGE_STEP="+label,flush=True)
        out=invoke(cmd,cwd=cwd,env=env,log_path=stage/(label+".log"),seconds=timeout)
        receipts["steps"][label]={"exit_code":0,"log_sha256":sha(stage/(label+".log"))}
        return out.strip()

    try:
        fetched=run("01_git_fetch",[git,"-C",str(root),"fetch","--no-tags","origin","refs/heads/"+BRANCH],cwd=root,timeout=60)
        actual=run("02_git_fetched_sha",[git,"-C",str(root),"rev-parse","FETCH_HEAD"],cwd=root,timeout=12)
        if actual!=a.expected_head:raise ValueError("GITHUB_BRANCH_HEAD_CHANGED")
        branchname=run("03_worktree_branch",[git,"rev-parse","--abbrev-ref","HEAD"])
        if branchname!=BRANCH:raise ValueError("WRONG_WORKTREE_BRANCH")
        clean=run("04_worktree_status",[git,"status","--porcelain","--untracked-files=all"])
        if clean:raise ValueError("DIRTY_WORKTREE_NO_RESET")
        head=run("05_worktree_sha",[git,"rev-parse","HEAD"])
        if head!=a.expected_head:
            # Verify ancestry first. This is a read-only test.
            run("06_ancestor",[git,"merge-base","--is-ancestor",head,a.expected_head],timeout=20)
            run("07_fast_forward_only",[git,"merge","--ff-only","--no-edit",a.expected_head],timeout=50)
        head2=run("08_final_worktree_sha",[git,"rev-parse","HEAD"])
        if head2!=a.expected_head:raise ValueError("GIT_HEAD_AFTER_FF_MISMATCH")
        clean2=run("09_worktree_status_after_ff",[git,"status","--porcelain","--untracked-files=all"])
        if clean2:raise ValueError("WORKTREE_DIRTY_AFTER_FF")
        receipts["steps"]["git_source"]={"head":head2,"branch":BRANCH}

        source=within(root,work/SRC_REL)
        p02=within(root,work/"src/p02/transformer_core.py")
        prereg=within(root,work/"artifacts/qa/ttm-t5-parity/TTM_T5_KV_FLASH_2X2_FRESH_SYNTHETIC_PREREG_20261109.json")
        if git_blob(p02)!=P02_BLOB or git_blob(prereg)!=PLAN_BLOB:
            raise ValueError("FROZEN_SOURCE_BLOB_CHANGED")
        gguf=within(root,root/GGUF_REL)
        if sha(gguf)!=GGUF_SHA:raise ValueError("ORIGINAL_GGUF_SHA_MISMATCH")
        llama=within(root,root/LLAMA_REL)
        llamaBuild=within(root,root/LLAMA_BUILD_REL)
        llamaHead=run("10_llama_commit",[git,"-C",str(llama),"rev-parse","HEAD"],cwd=root)
        if llamaHead!=LLAMA_COMMIT:raise ValueError("PINNED_LLAMA_SOURCE_COMMIT_CHANGED")
        libs=[llamaBuild/"src/Release/llama.lib",
              llamaBuild/"ggml/src/Release/ggml.lib",
              llamaBuild/"ggml/src/Release/ggml-base.lib"]
        libpins={}
        for file in libs:
            f=within(root,file)
            libpins[f.name]=sha(f)
        receipts["input_sha256"]={
           "gguf":GGUF_SHA,"p02_git_blob":P02_BLOB,"prereg_git_blob":PLAN_BLOB,
           "source_llama_commit":LLAMA_COMMIT,"import_libraries_sha256":libpins,
           "candidate_cpp_sha256":sha(source/"ttm_t5_kvflash_probe_candidate.cpp"),
           "candidate_cmake_sha256":sha(source/"CMakeLists.txt")}
        plan=json.loads(prereg.read_text(encoding="utf-8"))
        if plan.get("schema")!="ttm.t5.f32_kv_flash_single_synthetic_discrimination.prereg.v1":
            raise ValueError("PREREG_SCHEMA_MISMATCH")
        if plan["control_design"]["expected_runs"]!=32 or len(plan["control_design"]["new_fixtures"])!=8:
            raise ValueError("FROZEN_NEW_FIXTURES_MISMATCH")
        # No model load: synthetic unit tests (13 tests in frozen suite).
        tests=run("11_synthetic_python_qa",[python,str(source/"test_kvflash_protocol.py")],timeout=80)
        receipts["steps"]["synthetic_python_QA"]="EXECUTED_ZERO_MODEL"

        build=stage/"build"
        build.mkdir(exist_ok=False)
        run("12_cmake_configure",
            [cmake,"-S",source,"-B",build,"-G","Visual Studio 17 2022","-A","x64",
             "-DLLAMA_SOURCE_ROOT="+str(llama),"-DLLAMA_BUILD_ROOT="+str(llamaBuild)],
            timeout=120)
        run("13_cmake_build",
            [cmake,"--build",build,"--config","Release","--target","ttm_t5_kvflash_probe"],
            timeout=240)
        exe=within(root,stage/EXE_REL)
        receipts["compile_binary"]="COMPILED"
        receipts["compiled_executable_sha256"]=sha(exe)
        receipts["compiled_executable_path"]=str(exe)
        # The compiled self-check does not load a model or run GGUF decode.
        env["PATH"]=";".join([str(llamaBuild/"bin/Release"),str(llamaBuild/"src/Release"),
                              str(llamaBuild/"ggml/src/Release"),env.get("PATH","")])
        selfcheck=run("14_compiled_no_model_self_check",[exe,"--self-check"],timeout=35)
        parsed=json.loads(selfcheck)
        sc_file=stage/"SELF_CHECK.json"
        sc_file.write_text(json.dumps(parsed,sort_keys=True)+"\n",encoding="utf-8")
        run("15_check_compiled_constants",
            [python,source/"check_compiled_constants.py","--prereg",prereg,"--self-check-json",sc_file],
            timeout=45)
        receipts["steps"]["compiled_constants"]="PASS_8_FIXTURES_4_ARMS_NO_MODEL"
        receipts["compiled_constants_sha256"]=sha(sc_file)

        if a.checkpoint is None:
            receipts["reference"]="HOLD_CHECKPOINT_FILE_NOT_PROVIDED"
            receipts["status"]="HOLD_REFERENCE_MISSING_BINARY_QA_COMPLETE"
        else:
            checkpoint=within(root,a.checkpoint)
            if sha(checkpoint)!=CKPT_SHA:raise ValueError("ORIGINAL_1024_CHECKPOINT_SHA_MISMATCH")
            receipts["input_sha256"]["checkpoint"]=CKPT_SHA
            ref=stage/"REFERENCE_F32_SYN01_SYN08.jsonl"
            output=run("16_reference_P02_F32_CPU",[
                python,source/"f32_p02_reference_candidate.py",
                "--project-root",root,"--worktree-root",work,"--checkpoint",checkpoint,
                "--output",ref],timeout=180)
            metadata=json.loads(output)
            if metadata.get("status")!="REFERENCE_8_NEW_FIXTURES_COMPLETED":
                raise ValueError("REFERENCE_METADATA_NOT_COMPLETED")
            if metadata.get("reference_sha256")!=sha(ref):
                raise ValueError("REFERENCE_SHA_NOT_MATCHED")
            audit_stdout=run("17_independent_reference_schema_qa",[
                python,source/"verify_f32_reference_rows.py",
                "--prereg",prereg,"--reference",ref],timeout=45)
            if json.loads(audit_stdout).get("status")!="PASS_REFERENCE_8_OF_8_X_2048_F32_SCHEMA":
                raise ValueError("REFERENCE_INDEPENDENT_SCHEMA_NOT_PASS")
            receipts["steps"]["reference_schema"]="PASS_8_OF_8_X_2048"
            receipts["reference"]="COMPLETED_8_X_2048_F32"
            receipts["reference_sha256"]=sha(ref)
            receipts["reference_path"]=str(ref)
            receipts["reference_metadata"]=metadata
            receipts["status"]="STAGED_COMPILED_BINARY_AND_REFERENCE_QA_COMPLETE_NATIVE_HOLD"

    except Exception as err:
        receipts["status"]="HOLD_STAGE_FAILED_CLOSED"
        receipts["failure"]=type(err).__name__+": "+str(err)
        print("STAGE_FAILURE="+receipts["failure"],file=sys.stderr,flush=True)
    finally:
        outfile=stage/"STAGE_RECEIPT.json"
        outfile.write_text(json.dumps(receipts,ensure_ascii=False,sort_keys=True,indent=2)+"\n",encoding="utf-8")
        print("STAGE_STATUS="+receipts["status"],flush=True)
        print("STAGE_RECEIPT="+str(outfile),flush=True)
        print("STAGE_RECEIPT_SHA256="+sha(outfile),flush=True)
        print("NATIVE_2X2=NOT_EXECUTED",flush=True)
        print("STRICT_LOGITS=FAIL_7_OF_8_PRESERVED",flush=True)
    if receipts["status"]=="HOLD_STAGE_FAILED_CLOSED":
        raise SystemExit(2)

if __name__=="__main__":
    try:
        main()
    except Exception as err:
        print("TTM_T5_STAGE_FAIL_BEFORE_RECEIPT:"+type(err).__name__+": "+str(err),file=sys.stderr)
        raise SystemExit(3)
