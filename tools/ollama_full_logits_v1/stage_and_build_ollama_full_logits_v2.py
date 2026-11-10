#!/usr/bin/env python3
"""Short-path V2 recovery after Windows Git checkout MAX_PATH failure.
Never starts Ollama/inference; preserves failed V1 stage and frozen T5 v5.
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

ROOT = Path("D:/WORK/RESEARCH/TokenToModel-Lab")
BRANCH = "research/ttm-t5-ollama-full-logits-20261111"
BASE_MAIN = "5d52e32f20021e36f08f284ef9864d3ba36dbead"
OLLAMA_COMMIT = "9a3e8177767245acc62b735eba7d5d8a553606d0"
LLAMA_COMMIT = "39febd2adb947b70da35e95f9351b3bf58ad170a"
ORIGINAL_CONTEXT_BLOB = "2bd1ab9ec00ca581c70bac014f7ca6d3d2bae0ae"
PATCHED_SOURCE_BLOBS = {
    "src/llama-model-loader.cpp": "30a5bbf403ab9bc81d9c307ca402b7510c1cdf5c",
    "tools/mtmd/clip.cpp": "b7d13fbbe2ec8cd4f8aa2e9c93a96dbfdb4f8c10",
    "ggml/src/ggml-metal/kernels/unary.metal": "873b59e089857460c56377055465c8e1e160916d",
    "src/models/gpt2.cpp": "430eed46a557f5004fb8a72e86f3152b06d95b6a",
}
REFERENCE_SHA = "1e098a643c9bce66431adf3dc0296ce6b628731d33c4532753d2f2acd664d082"
SEAL_SHA = "571a1a654bad1b97de066d6fb3b690e910ecc71777deb4b16b7b15968f444939"
GGUF_SHA = "5bdc904e6c51af04a4223219f36e6bc2e687f60fd6e17dc24508f3eb7489e4e5"
V5_OLLAMA_EXE_SHA = "7544d36e5bb4c9cfddbd48a400ea4f1919de8fcea80510e1847627ec92909e43"
V5_LLAMA_SERVER_SHA = "13ea04b48551a5476920197fee4ff98b5b17b6277f84306fcc4f2422de046879"
V1_FAILURE_STAGE = "_tmp/ttm_ollama_full_logits_candidate_build_20261111"
V1_FAILURE_RECEIPT_SHA = "b7f0750541b872f0806ff5a4ab9a5cc9952f08830607fc6fa90bb29e4a944cb4"
V2_STAGE = "_tmp/fl2"
V2_HOOK_FILENAME = "ttm_ollama_full_logits_b11963_hook_v2.patch"

def sha(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()

def contained(root: Path, path: Path, *, exist: bool = True) -> Path:
    value = path.resolve(strict=exist)
    if value == root or not value.is_relative_to(root):
        raise ValueError("PATH_OUTSIDE_TTM_ROOT")
    return value

def existing_file(root: Path, p: Path) -> Path:
    q = contained(root,p)
    if not q.is_file():
        raise ValueError("REQUIRED_FILE_MISSING:" + str(q))
    return q

def command(argv, cwd: Path, *, timeout: int = 45, log: Path | None = None, env=None):
    args = [str(x) for x in argv]
    if log is None:
        done = subprocess.run(args, cwd=str(cwd), check=False, capture_output=True,
                              text=True, errors="replace", timeout=timeout, env=env)
        if done.returncode:
            raise RuntimeError("COMMAND_FAILED:" + args[0] + ":" + str(done.returncode)
                               + ":" + (done.stderr or done.stdout)[-900:])
        return done.stdout.strip()
    with log.open("x", encoding="utf-8", newline="\n") as handle:
        handle.write("ARGV=" + json.dumps(args,ensure_ascii=False) + "\n")
        handle.flush()
        try:
            p = subprocess.run(args, cwd=str(cwd), stdout=handle,
                               stderr=subprocess.STDOUT, check=False,
                               timeout=timeout, env=env)
        except subprocess.TimeoutExpired as ex:
            handle.write("\nTIMEOUT_NO_AUTOMATIC_RETRY\n")
            raise RuntimeError("COMMAND_TIMEOUT:" + log.name) from ex
        handle.write("\nEXIT_CODE=" + str(p.returncode) + "\n")
        handle.flush()
    if p.returncode:
        raise RuntimeError("COMMAND_FAILURE_LOG:" + log.name + ":" + str(p.returncode))
    return sha(log)

def git_hash(git: str, repo: Path, f: Path, *, raw: bool = False) -> str:
    # Git blob IDs of tracked source normalize line endings. The four frozen
    # materialized v5 source pins were recorded with --no-filters (raw bytes).
    args=[git,"-C",repo,"hash-object"]
    if raw:
        args.append("--no-filters")
    args.append(str(f))
    return command(args,cwd=repo,timeout=30)

def verify_reference(root: Path):
    base = contained(root,root/"_tmp/ttm_ollama_full_logits_reference_fl01_fl04_20261111")
    ref = existing_file(root,base/"REFERENCE_P02_F32_FL01_FL04.jsonl")
    seal = existing_file(root,base/"REFERENCE_INDEPENDENT_SEAL.json")
    if sha(ref) != REFERENCE_SHA or sha(seal) != SEAL_SHA:
        raise ValueError("REFERENCE_OR_SEAL_SHA_CHANGED")
    report = json.loads(seal.read_text("utf-8"))
    if (report.get("status")!="PASS_REFERENCE_4_OF_4_X_2048"
        or report.get("reference_sha256")!=REFERENCE_SHA
        or report.get("rows")!=4 or report.get("logits_evaluated")!=8192):
        raise ValueError("FROZEN_REFERENCE_SEAL_INVALID")
    # Direct full-vector readback here, not merely trusting the previous audit receipt.
    values=ref.read_text("utf-8")
    if not values.endswith("\n") or values.count("\n") != 4:
        raise ValueError("REFERENCE_NOT_EXACT_FOUR_ROWS")
    ids={"FL01":[97,98,99],"FL02":[257,304,111],"FL03":[97,10,98],
         "FL04":[88,267,628,195,160,111]}
    seen=[]
    for line in values.splitlines():
        row=json.loads(line)
        k=row.get("fixture_id")
        if (k not in ids or k in seen or row.get("token_ids")!=ids[k]
            or row.get("source")!="P02_F32_STEP1024_GELU_ERF"
            or not isinstance(row.get("logits"),list)
            or len(row["logits"])!=2048):
            raise ValueError("REFERENCE_ROW_SCHEMA_MISMATCH")
        import math
        if any(type(x) not in (float,int) or not math.isfinite(x) for x in row["logits"]):
            raise ValueError("REFERENCE_LOGITS_NOT_FINITE")
        seen.append(k)
    if seen != list(ids):
        raise ValueError("REFERENCE_ROW_ORDER_CHANGED")
    return {"sha256":REFERENCE_SHA,"seal_sha256":SEAL_SHA,"rows":4,"logits":8192}

def main() -> None:
    parser=argparse.ArgumentParser()
    parser.add_argument("--project-root",type=Path,required=True)
    parser.add_argument("--worktree",type=Path,required=True)
    parser.add_argument("--expected-head",required=True)
    parser.add_argument("--build",action="store_true",
                        help="Actually compile/install isolated native runner. Without this, source-only staging.")
    a=parser.parse_args()
    if os.name != "nt" or sys.version_info[:2] != (3,12):
        raise ValueError("WINDOWS_PYTHON312_REQUIRED")
    root=a.project_root.resolve(strict=True)
    if root != ROOT.resolve(strict=True):
        raise ValueError("WRONG_TTM_PROJECT")
    work=contained(root,a.worktree)
    if not (work/".git").exists():
        raise ValueError("MISSING_TTM_GIT_WORKTREE")
    if len(a.expected_head)!=40 or any(x not in "0123456789abcdef" for x in a.expected_head):
        raise ValueError("INVALID_EXPECTED_HEAD")
    git=shutil.which("git.exe")
    cmake=shutil.which("cmake.exe")
    if not git or (a.build and not cmake):
        raise ValueError("GIT_OR_CMAKE_NOT_AVAILABLE")
    if command([git,"-C",work,"branch","--show-current"],work) != BRANCH:
        raise ValueError("WRONG_RESEARCH_BRANCH")
    if command([git,"-C",work,"rev-parse","HEAD"],work) != a.expected_head:
        raise ValueError("WORKTREE_HEAD_NOT_EXACT")
    if command([git,"-C",work,"status","--porcelain","--untracked-files=all"],work):
        raise ValueError("RESEARCH_WORKTREE_DIRTY")
    ref=verify_reference(root)
    original_root=contained(root,root/"_tmp/t5-ollama-custom-v4")
    original_ollama=contained(root,original_root/"ollama")
    original_llama=contained(root,original_root/"llama")
    if command([git,"-C",original_ollama,"rev-parse","HEAD"],work)!=OLLAMA_COMMIT:
        raise ValueError("V5_OLLAMA_SOURCE_REVISION_CHANGED")
    if command([git,"-C",original_llama,"rev-parse","HEAD"],work)!=LLAMA_COMMIT:
        raise ValueError("V5_LLAMA_SOURCE_REVISION_CHANGED")
    for name,digest in PATCHED_SOURCE_BLOBS.items():
        src=existing_file(root,original_llama/name)
        if git_hash(git,original_llama,src,raw=True)!=digest:
            raise ValueError("V5_MATERIALIZED_SOURCE_BLOB_MISMATCH:"+name)
    # Only continue the exact Windows failure already preserved by the owner.
    old_stage=contained(root,root/V1_FAILURE_STAGE)
    old_receipt=existing_file(root,old_stage/"STAGE_RECEIPT.json")
    old_log=existing_file(root,old_stage/"01_git_worktree_add.log")
    if sha(old_receipt) != V1_FAILURE_RECEIPT_SHA:
        raise ValueError("FROZEN_FAILED_V1_RECEIPT_SHA_CHANGED")
    failed=json.loads(old_receipt.read_text("utf-8"))
    log=old_log.read_text("utf-8",errors="replace")
    if (failed.get("status")!="HOLD_PARTIAL_STAGE_NO_AUTO_REPLAY"
        or failed.get("failure")!="RuntimeError:COMMAND_FAILURE_LOG:01_git_worktree_add.log:128"
        or failed.get("research_head")!="196b01009130a1b6771f9bcfa537e2e6d38df96a"
        or "Filename too long" not in log
        or "EXIT_CODE=128" not in log):
        raise ValueError("FAILURE_NOT_EXACT_WINDOWS_LONG_PATH")
    if (old_stage/"llama").exists():
        raise ValueError("V1_PARTIAL_LLAMA_DIR_EXISTS_DO_NOT_CLEAN")
    patch=existing_file(root,work/("tools/ollama_full_logits_v1/" + V2_HOOK_FILENAME))
    v5_package=contained(root,root/"_tmp/t5-ollama-custom-v5/package")
    orig_exe=existing_file(root,v5_package/"ollama.exe")
    orig_runner=existing_file(root,v5_package/"lib/ollama/llama-server.exe")
    if sha(orig_exe)!=V5_OLLAMA_EXE_SHA or sha(orig_runner)!=V5_LLAMA_SERVER_SHA:
        raise ValueError("V5_PACKAGE_HASH_NOT_PINNED")
    # Only reserve stage once after all source/reference checks have passed.
    stage=contained(root,root/V2_STAGE,exist=False)
    # The exact path that failed V1 was 262 characters; the corresponding V2
    # path must remain below 240 to allow legacy Windows toolchain headroom.
    longest="tools/ui/src/lib/components/app/models/discover/ModelsDiscoverDetails/ModelsDiscoverDetailsDownloadOptions/ModelsDiscoverDetailsDownloadOptionsDraftDownloadButton.svelte"
    if len(str(stage/"llama"/longest)) >= 240:
        raise ValueError("RECOVERY_PATH_STILL_TOO_LONG")
    if stage.exists() or stage.is_symlink():
        raise FileExistsError("STAGE_EXISTS_NO_OVERWRITE")
    stage.mkdir(parents=True,exist_ok=False)
    snap={
      "schema":"ttm.ollama.full_logits.isolated_candidate_stage.v1",
      "status":"STAGE_STARTED_UNADJUDICATED",
      "phase":"SOURCE_AND_NATIVE_BUILD" if a.build else "SOURCE_ONLY",
      "base_main":BASE_MAIN,"research_head":a.expected_head,
      "original_ollama_commit":OLLAMA_COMMIT,"original_llama_commit":LLAMA_COMMIT,
      "original_v5_package_read_only":True,"v5_reference_unchanged":True,
      "reference":ref,"source_blobs":PATCHED_SOURCE_BLOBS,
      "runner_inference":"NOT_EXECUTED","test_access":False,"training":False,
      "git_merge_main":False,
      "recovery_from":"HOLD_WINDOWS_LONG_PATH_V1",
      "original_failure_receipt_sha256":V1_FAILURE_RECEIPT_SHA,
      "stage_short_path":str(stage),
      "candidate_patch_path":str(patch)
    }
    try:
        cand_llama=stage/"llama"
        snap["git_worktree_add_log_sha256"]=command(
            [git,"-c","core.longpaths=true","-C",original_llama,
             "worktree","add","--detach",cand_llama,LLAMA_COMMIT],
            original_llama,timeout=120,log=stage/"01_git_worktree_add.log")
        for name,blob in PATCHED_SOURCE_BLOBS.items():
            dst=cand_llama/name
            shutil.copyfile(original_llama/name,dst)
            if git_hash(git,cand_llama,dst,raw=True)!=blob:
                raise ValueError("NEW_COPY_HASH_MISMATCH:"+name)
        ctx=cand_llama/"tools/server/server-context.cpp"
        if git_hash(git,cand_llama,ctx)!=ORIGINAL_CONTEXT_BLOB:
            raise ValueError("CANDIDATE_UNMODIFIED_CONTEXT_HASH_MISMATCH")
        snap["git_apply_check_log_sha256"]=command(
            [git,"-C",cand_llama,"apply","--check",patch],cand_llama,
            timeout=45,log=stage/"02_hook_patch_check.log")
        snap["git_apply_log_sha256"]=command(
            [git,"-C",cand_llama,"apply",patch],cand_llama,
            timeout=45,log=stage/"03_hook_patch_apply.log")
        modified=set(command([git,"-C",cand_llama,"diff","--name-only"],cand_llama).splitlines())
        expected=set(PATCHED_SOURCE_BLOBS)|{"tools/server/server-context.cpp"}
        if modified != expected:
            raise ValueError("UNEXPECTED_CANDIDATE_SOURCE_FILES:"+repr(sorted(modified)))
        if "llama_get_logits_ith(slot.ctx_tgt, tok_idx)" not in ctx.read_text("utf-8"):
            raise ValueError("PRE_SAMPLER_RAW_LOGITS_HOOK_MISSING")
        snap["modified_source_paths"]=sorted(modified)
        snap["candidate_hook_server_context_git_blob"]=git_hash(git,cand_llama,ctx)
        snap["status"]="SOURCE_STAGE_PASS_NATIVE_NOT_EXECUTED"
        print("OLLAMA_FULL_LOGITS_ISOLATED_SOURCE=PASS_EXACT_FIVE_FILES",flush=True)
        if a.build:
            pkg=stage/"package"
            shutil.copytree(v5_package,pkg)
            env=dict(os.environ)
            # These environment overrides can silently redirect CMake to a
            # different llama.cpp tree or skip the Ollama compatibility shim.
            env.pop("OLLAMA_LLAMA_CPP_SOURCE",None)
            env.pop("FETCHCONTENT_SOURCE_DIR_LLAMA_CPP",None)
            temp=stage/"scratch"
            temp.mkdir()
            env.update({"TMP":str(temp),"TEMP":str(temp),"TMPDIR":str(temp)})
            build=stage/"native-build"
            argv=[cmake,"-G","Visual Studio 17 2022","-A","x64",
                  "-S",original_ollama/"llama/server","-B",build,
                  "-DCMAKE_CONFIGURATION_TYPES=Release",
                  "-DCMAKE_INSTALL_PREFIX="+str(pkg),
                  "-DOLLAMA_LIB_DIR=lib/ollama","-DOLLAMA_RUNNER_DIR=",
                  "-DFETCHCONTENT_SOURCE_DIR_LLAMA_CPP="+str(cand_llama),
                  "-DOLLAMA_LLAMA_CPP_SKIP_COMPAT_PATCH=ON",
                  "-DBUILD_SHARED_LIBS=ON","-DGGML_BACKEND_DL=ON",
                  "-DGGML_NATIVE=OFF","-DGGML_CPU_ALL_VARIANTS=OFF",
                  "-DGGML_OPENMP=OFF","-DGGML_CUDA=OFF",
                  "-DGGML_VULKAN=OFF","-DGGML_HIP=OFF","-DGGML_SYCL=OFF"]
            snap["cmake_configure_log_sha256"]=command(
                 argv,stage,timeout=240,log=stage/"04_cmake_configure.log",env=env)
            cache=(build/"CMakeCache.txt").read_text("utf-8",errors="replace")
            found = {}
            for ln in cache.splitlines():
                if ln.startswith(("FETCHCONTENT_SOURCE_DIR_LLAMA_CPP:", "OLLAMA_LLAMA_CPP_SKIP_COMPAT_PATCH:")):
                    k,_,v=ln.partition("=")
                    found[k.split(":")[0]]=v
            effective=found.get("FETCHCONTENT_SOURCE_DIR_LLAMA_CPP","")
            if os.path.normcase(os.path.normpath(effective)) != os.path.normcase(os.path.normpath(str(cand_llama))):
                raise ValueError("CMAKE_SOURCE_TREE_NOT_FROZEN_CANDIDATE")
            if found.get("OLLAMA_LLAMA_CPP_SKIP_COMPAT_PATCH") != "ON":
                raise ValueError("CMAKE_COMPAT_HOOK_LINKAGE_NOT_PINNED")
            snap["cmake_effective_llama_source"]=effective
            snap["cmake_build_log_sha256"]=command(
                [cmake,"--build",build,"--config","Release","--parallel","4"],
                stage,timeout=1800,log=stage/"05_cmake_build.log",env=env)
            snap["cmake_install_log_sha256"]=command(
                [cmake,"--install",build,"--config","Release"],
                stage,timeout=300,log=stage/"06_cmake_install.log",env=env)
            newly_built=existing_file(root,pkg/"lib/ollama/llama-server.exe")
            snap["candidate_native_runner_sha256"]=sha(newly_built)
            snap["candidate_ollama_exe_sha256"]=sha(pkg/"ollama.exe")
            if (snap["candidate_native_runner_sha256"]==V5_LLAMA_SERVER_SHA
                or snap["candidate_ollama_exe_sha256"]!=V5_OLLAMA_EXE_SHA):
                raise ValueError("RUNNER_NOT_CHANGED_OR_GO_CLI_NOT_PINNED")
            snap["status"]="BUILD_PASS_ISOLATED_NO_OLLAMA_INFERENCE"
            print("OLLAMA_FULL_LOGITS_BUILD=PASS_ISOLATED",flush=True)
            print("CANDIDATE_NATIVE_SHA256="+snap["candidate_native_runner_sha256"],flush=True)
    except Exception as ex:
        snap["status"]="HOLD_PARTIAL_STAGE_NO_AUTO_REPLAY"
        snap["failure"]=type(ex).__name__+":"+str(ex)
        print("OLLAMA_FULL_LOGITS_STAGE_HOLD="+snap["failure"],file=sys.stderr,flush=True)
    finally:
        path=stage/"STAGE_RECEIPT.json"
        with path.open("x",encoding="utf-8",newline="\n") as stream:
            json.dump(snap,stream,indent=2,sort_keys=True,ensure_ascii=False)
            stream.write("\n")
        print("REFERENCE_F32_PIN=PASS_4_X_2048_SHA_EXACT",flush=True)
        print("STAGE_STATUS="+snap["status"],flush=True)
        print("STAGE_RECEIPT="+str(path),flush=True)
        print("STAGE_RECEIPT_SHA256="+sha(path),flush=True)
        print("OLLAMA_FULL_LOGITS_INFERENCE=NOT_EXECUTED",flush=True)
        print("T5_WINDOWS_F32=PASS_SCOPED_UNCHANGED",flush=True)
    if snap["status"] not in (
        "SOURCE_STAGE_PASS_NATIVE_NOT_EXECUTED",
        "BUILD_PASS_ISOLATED_NO_OLLAMA_INFERENCE",
    ):
        raise SystemExit(2)

if __name__=="__main__":
    try:
        main()
    except (ValueError,OSError,RuntimeError,subprocess.TimeoutExpired,
            KeyError,TypeError,json.JSONDecodeError) as error:
        print("TTM_OLLAMA_FULL_LOGITS_PRESTAGE_HOLD:"+
              type(error).__name__+":"+str(error),file=sys.stderr)
        raise SystemExit(3)
