#!/usr/bin/env python3
"""TTM T5 once-only heldout C01-C04 native GELU_ERF confirmatory runner.

Reuses pinned B llama.cpp source/built libs; compiles NEW C01-C04-only
probe and executes only four previously sealed fixtures. No inference for
D01/D02, original 8 or original 32; no training or TEST.
"""
from __future__ import annotations
import argparse,hashlib,json,os,subprocess,sys
from pathlib import Path

ROOT=Path("D:/WORK/RESEARCH/TokenToModel-Lab")
STAGE="_tmp/ttm_t5_c01c04_gelu_erf_confirmatory_one_shot_20261110"
RECOVERY="_tmp/ttm_t5_exact_root_discovery_recovery_v2_20261110"
ISOLATION="_tmp/ttm_t5_exact_root_v1_20261110/trace_gelu_erf"
WORK="worktrees/ttm-t5-kvflash-preview-20261109"
GGUF="_tmp/ttm_t5_trained_f32_v1/TTM-Small4M-T4-step1024-F32.gguf"
GGUF_SHA="5bdc904e6c51af04a4223219f36e6bc2e687f60fd6e17dc24508f3eb7489e4e5"
PREREG="82fdd9fe716579181db648caa69170fb63d115a6"
RECOVERY_RECEIPT_SHA="1f01b2991d0faae4e93c7faff8ab59cf53268f68c36085460949ff3402669bf1"
REF_ZIP_SHA="e5d522bd5234c46af77dbb85990779bd09e25d35be587538cec577ee486c5996"
C_CPP_BLOB="f14f4e8eaecba273a5fe314d04e8498c40c76655"
C_CMAKE_BLOB="9e829fbdc0415582a81e9d64c2b3da689cfd6b12"
CHECKER_BLOB="b38c09278588c3e8bf40208cbbacf8448bfdd97e"
PIN_B_SOURCE={
    "src/llama-graph.cpp":"df553f77f4d481877455dde37a96b19e77e4aefd674879e14bcf55b9e2a2dd2c",
    "src/models/gpt2.cpp":"59d1685da8f44ed420af8852c987a6c72e0d028c8304931f05a9e90a5c03f06e"}
PIN_B_DLLS={
    "llama.dll":"93c6f488acc4e3a8ac9ad656cc3c462f1cc53ccb6bdac07ea48b2f64e917253d",
    "ggml.dll":"2b0c7354fd1036a12d1c495aeff1c435e44273280b254e5800d12dcfafd073ca",
    "ggml-base.dll":"edc32ece78986aec6859d276744a65f89c6eec46e68fffeb266d015463c029ac",
    "ggml-cpu.dll":"86c9b9becd030f372c68bb02fdbf4ffa26794bdabec5f4b88172e50f22b3adca"}
FIX=[
    ("C01",[1531,1448]),
    ("C02",[1656,1282,646,1827]),
    ("C03",[1781,1116,686,656,1421,1258,1286,2029,1493,1645,485]),
    ("C04",[1906,950,726,1919,386,2019,849,482,889,1037,1758,785,1969,754,1900,1892,727])]
APPROVAL="I_APPROVE_ONE_TTM_T5_C01_C04_GELU_ERF_STRICT_CONFIRMATORY"

def sha(p:Path)->str:
    h=hashlib.sha256()
    with p.open("rb") as stream:
        for b in iter(lambda:stream.read(1<<20),b""):h.update(b)
    return h.hexdigest()

def blob(p:Path)->str:
    d=p.read_bytes()
    return hashlib.sha1(b"blob "+str(len(d)).encode()+b"\0"+d).hexdigest()

def member(root:Path,p:Path,file=True):
    q=p.resolve(strict=True)
    if not q.is_relative_to(root) or (file and not q.is_file()):
        raise ValueError("NOT_EXACT_PROJECT_LOCAL_FILE")
    return q

def command(label,argv,work,env=None,timeout=180):
    log=work/(label+".log")
    if log.exists():raise FileExistsError("LOG_EXISTS_NO_OVERWRITE:"+label)
    e=dict(os.environ)
    e.update(env or {})
    e.update({"TMP":str(work),"TEMP":str(work),"PYTHONDONTWRITEBYTECODE":"1"})
    try:
        p=subprocess.run([str(x) for x in argv],cwd=str(work),env=e,
            capture_output=True,text=True,errors="replace",timeout=timeout)
    except subprocess.TimeoutExpired as exc:
        log.write_text("TIMEOUT_FAILED_CLOSED_NO_RETRY\n",encoding="utf-8")
        raise RuntimeError(label+"_TIMEOUT_NO_RETRY") from exc
    log.write_text("ARGV="+json.dumps([str(x) for x in argv])+
      "\nRETURN_CODE="+str(p.returncode)+"\nSTDOUT:\n"+p.stdout+
      "\nSTDERR:\n"+p.stderr+"\n",encoding="utf-8")
    if p.returncode:raise RuntimeError(label+"_EXIT_"+str(p.returncode)+"_SEE_LOG")
    print("C_CONFIRMATORY_STEP="+label,flush=True)
    return p.stdout

def main():
    p=argparse.ArgumentParser()
    p.add_argument("--project-root",type=Path,required=True)
    p.add_argument("--source-dir",type=Path,required=True)
    p.add_argument("--reference-zip",type=Path,required=True)
    p.add_argument("--approve-exact-once",required=True)
    opts=p.parse_args()
    if (os.name!="nt" or sys.version_info[:2]!=(3,12)
        or opts.approve_exact_once!=APPROVAL):
        raise ValueError("OWNER_WINDOWSPY312_SCOPE_REQUIRED")
    root=opts.project_root.resolve(strict=True)
    if os.path.normcase(str(root))!=os.path.normcase(str(ROOT)):
        raise ValueError("WRONG_TTM_PROJECT")
    source=member(root,opts.source_dir,file=False)
    cpp=member(root,source/"ttm_t5_c01c04_gelu_erf_confirmatory_probe.cpp")
    cm=member(root,source/"CMakeLists.txt")
    chk=member(root,source/"independent_strict_c01c04_checker.py")
    if (blob(cpp)!=C_CPP_BLOB or blob(cm)!=C_CMAKE_BLOB or
        blob(chk)!=CHECKER_BLOB):
        raise ValueError("CANDIDATE_CPP_CMAKE_AUDITOR_SOURCE_SHA_CHANGED")
    zip_path=member(root,opts.reference_zip)
    gguf=member(root,root/GGUF)
    pre=member(root,root/WORK/"artifacts/qa/ttm-t5-parity/TTM_T5_EXACT_FIRST_OP_NEW_FIXTURES_INTEGRATED_PREREG_20261110.json")
    if sha(zip_path)!=REF_ZIP_SHA or sha(gguf)!=GGUF_SHA or blob(pre)!=PREREG:
        raise ValueError("PINNED_REFERENCE_GGUF_PREREG_MISMATCH")
    original=member(root,root/RECOVERY/"RECOVERY_V2_RECEIPT.json")
    if sha(original)!=RECOVERY_RECEIPT_SHA:
        raise ValueError("DISCOVERY_RECEIPT_SHA_CHANGED")
    previous=json.loads(original.read_text("utf-8"))
    if (previous.get("status")!="RECOVERY_TWO_VARIANTS_AUDITED_DISCOVERY_UNADJUDICATED"
        or previous.get("actual_B_ERF_node_captures")!=2
        or previous.get("new_native_gelu_erf_executions")!=2
        or previous.get("confirmatory_C01_C04")!="NOT_EXECUTED"
        or previous.get("old_trace_only_native_reexecuted") is not False):
        raise ValueError("GELU_ERF_DISCOVERY_GATE_NOT_MET")
    for f in ("D01","D02"):
        if previous["variants"]["trace_gelu_erf"]["strict_max_abs"][f]>0.001:
            raise ValueError("DISCOVERY_B_GELU_ERF_NOT_STRICT_PASS")
    b_source=member(root,root/ISOLATION,file=False)
    b_build=member(root,root/RECOVERY/"trace_gelu_erf/llama_build",file=False)
    for relative,digest in PIN_B_SOURCE.items():
        if sha(member(root,b_source/relative))!=digest:
            raise ValueError("ORIGINAL_B_GELU_ERF_SOURCE_MUTATED:"+relative)
    dll_dir=member(root,b_build/"bin/Release",file=False)
    dlls={}
    for name,digest in PIN_B_DLLS.items():
        file=member(root,dll_dir/name)
        if sha(file)!=digest:raise ValueError("PINNED_ERF_RUNTIME_DLL_MISMATCH:"+name)
        dlls[name]=digest
    pre_json=json.loads(pre.read_text("utf-8"))
    if ([(a["fixture_id"],a["token_ids"]) for a in pre_json["fixtures"]
            if a["partition"]=="confirmatory"]!=FIX):
        raise ValueError("FOUR_HELDOUT_FIXTURES_CHANGED")
    out=root/STAGE
    if out.exists():raise FileExistsError("CONFIRMATORY_ALREADY_STARTED_NO_REPEAT")
    out.mkdir(parents=True,exist_ok=False)
    receipt={
      "schema":"ttm.t5.GELU_ERF.C01_C04.once_only_confirmatory_receipt.v1",
      "status":"CONFIRMATORY_STAGE_STARTED_UNADJUDICATED",
      "inputs_sha256":{"P02_true_reference_zip":REF_ZIP_SHA,
        "GGUF_F32":GGUF_SHA,"discovery_receipt":RECOVERY_RECEIPT_SHA},
      "candidate_source_blobs":{"cpp":C_CPP_BLOB,"cmake":C_CMAKE_BLOB,
        "checker":CHECKER_BLOB},
      "llama_src_sha256":PIN_B_SOURCE,
      "DLLs_sha256":dlls,
      "old_D_8_32_reexecuted":False,"TEST_or_Q1Q2":False,
      "training":False,"main":"UNCHANGED","lineage":"UNCHANGED",
      "PR16":"DRAFT_HOLD","threshold":0.001,
      "confirmatory_attempted_once":False}
    try:
        build=out/"probe_build"
        command("01_configure_C_candidate",
            ["cmake.exe","-S",source,"-B",build,"-G","Visual Studio 17 2022","-A","x64",
              "-DLLAMA_SOURCE_ROOT="+str(b_source),
              "-DLLAMA_BUILD_ROOT="+str(b_build)],out,timeout=180)
        command("02_build_C_candidate",
            ["cmake.exe","--build",build,"--config","Release","--target",
             "ttm_t5_firstop_trace_probe","--parallel","4"],out,timeout=600)
        exe=member(root,build/"Release/ttm_t5_firstop_trace_probe.exe")
        env={"PATH":str(dll_dir)+os.pathsep+os.environ.get("PATH","")}
        c=command("03_compiled_no_model_selfcheck",[exe,"--self-check"],out,env,60)
        j=json.loads(c)
        if (j.get("schema")!="ttm.t5.confirmatory_four.GELU_ERF.compiled_constants.v1"
            or j.get("model_loaded") is not False
            or j.get("native_inference") is not False
            or [(q["fixture_id"],q["token_ids"]) for q in j.get("fixtures",[])]!=FIX
            or j.get("arms")!=[{"id":"S1_F32_NO_FLASH","kv":"F32","flash":"DISABLED"}]):
            raise ValueError("COMPILED_CANDIDATE_NOT_EXACT_FROZEN_C01_C04")
        receipt["exe_sha256"]=sha(exe)
        native=out/"C01_C04_NATIVE_F32_GELU_ERF.jsonl"
        print("C_CONF_NATIVE=STARTED_ONCE_FOUR_HELDOUT_FIXTURES",flush=True)
        receipt["confirmatory_attempted_once"]=True
        done=command("04_confirmatory_four_native_once",
            [exe,root,gguf,native],out,env,timeout=300)
        if "T5_GELU_ERF_CONFIRMATORY_COMPLETE_ROWS_4" not in done:
            raise ValueError("NO_FOUR_NATIVE_COMPLETION_MARKER")
        rawtrace=member(root,Path(str(native)+".trace.jsonl"))
        native=member(root,native)
        report=out/"C01_C04_INDEPENDENT_STRICT_AUDIT.json"
        command("05_independent_strict_2048_audit",
            [sys.executable,"-B",chk,
             "--prereg",pre,"--reference-zip",zip_path,
             "--native-logits",native,"--native-trace",rawtrace,
             "--output",report],out,timeout=120)
        check=json.loads(report.read_text("utf-8"))
        if check.get("status") not in ("STRICT_PASS_4_OF_4",
              "STRICT_FAIL_1_OF_4","STRICT_FAIL_2_OF_4",
              "STRICT_FAIL_3_OF_4","STRICT_FAIL_4_OF_4"):
            raise ValueError("INDEPENDENT_AUDITOR_INVALID_STATUS")
        receipt["native_sha256"]=sha(native)
        receipt["trace_sha256"]=sha(rawtrace)
        receipt["independent_audit_sha256"]=sha(report)
        receipt["science_status"]=check["status"]
        receipt["status"]="CONFIRMATORY_COMPLETED_UNADJUDICATED"
    except Exception as e:
        receipt["status"]="HOLD_CONFIRMATORY_TECHNICAL_FAILURE_OR_PARTIAL_NO_RETRY"
        receipt["failure"]=type(e).__name__+":"+str(e)
    finally:
        final=out/"CONFIRMATORY_ONCE_RECEIPT.json"
        with final.open("x",encoding="utf-8",newline="\n") as stream:
            json.dump(receipt,stream,indent=2,sort_keys=True)
            stream.write("\n")
        print("CONFIRMATORY_RECEIPT="+str(final),flush=True)
        print("CONFIRMATORY_RECEIPT_SHA256="+sha(final),flush=True)
        print("CONFIRMATORY_RUN_STATUS="+receipt["status"],flush=True)
        print("MERGE=HOLD_PENDING_INDEPENDENT_REVIEW_AND_OWNER",flush=True)
    if receipt["status"]!="CONFIRMATORY_COMPLETED_UNADJUDICATED":
        raise SystemExit(2)

if __name__=="__main__":
    try:main()
    except (RuntimeError,ValueError,KeyError,TypeError,OSError,FileNotFoundError) as e:
        print("TTM_T5_CONFIRMATORY_PRECHECK_HOLD:"+type(e).__name__+":"+str(e),file=sys.stderr)
        raise SystemExit(3)
