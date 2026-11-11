#!/usr/bin/env python3
"""Read-only independent adjudication of existing TTM FL01-FL04 Ollama run.
No model import, no Ollama HTTP, no inference, no cleanup, no replay.
Only creates a new independent QA receipt in the existing TTM _tmp/fl3 stage.
"""
from __future__ import annotations
import argparse
import hashlib
import json
import math
from pathlib import Path
import re
import shutil
import subprocess
import sys

ROOT = Path("D:/WORK/RESEARCH/TokenToModel-Lab")
BRANCH = "research/ttm-t5-ollama-full-logits-20261111"
SOURCE_HEAD = "194fb946cc3283d65bd54c64bb965db2343e0c71"
PREREG_BLOB = "fdcb81064a6c55b3dca5f71e18defff0895c0568"
P02_BLOB = "9762343e06cf800b50574c2871ae1ed58537fb18"
CKPT_SHA = "cb985751795c8328ad65acf7ca4c1033ce35182c1bfbdb8c38550de629cb271b"
GGUF_SHA = "5bdc904e6c51af04a4223219f36e6bc2e687f60fd6e17dc24508f3eb7489e4e5"
RUNNER_SHA = "818fec27008b0a8555ecbae09c8c95e6a076d2b2fa4c26377b8bdb248232210a"
OLLAMA_SHA = "7544d36e5bb4c9cfddbd48a400ea4f1919de8fcea80510e1847627ec92909e43"
REFERENCE_SHA = "1e098a643c9bce66431adf3dc0296ce6b628731d33c4532753d2f2acd664d082"
REFERENCE_SEAL_SHA = "571a1a654bad1b97de066d6fb3b690e910ecc71777deb4b16b7b15968f444939"
RUN_SHA = "18f2fea2d986449eda098a949103e9614ab3c8a1a2368a3647c0c7729dbda269"
FILES = {
    "OLLAMA_RAW_FL01_FL04.jsonl": "af289d6cbe52931581b6b0419d0239d80bbdd95d19357abbeb586ae53d1dd9e1",
    "NUMERIC_AUDIT.json": "1710564a877e02cb2c96b00edfebccf94e2e31473c8d11f0ef6a05315eb7b77d",
    "NUMERIC_AUDIT_RUN.log": "c22d7eeb4c68021a2ad31512b5a9a269492806ad5a3c95910579fe824f0998d0",
    "OLLAMA_SERVE.log": "d43954db7a1078dd999086b64a6683e7fada38278fe9cf2a434132e059b44964",
    "OWNED_PROCESS_CLEANUP.log": "e0caa327def0f07ebd6f71f1220b1b538bfa6e3689050c7349305cc19bbc662a",
}
FIXTURES = {
    "FL01": [97, 98, 99],
    "FL02": [257, 304, 111],
    "FL03": [97, 10, 98],
    "FL04": [88, 267, 628, 195, 160, 111],
}
THRESHOLD = 0.001

def digest(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as file:
        for block in iter(lambda: file.read(1 << 20), b""):
            h.update(block)
    return h.hexdigest()

def blob_sha(path: Path) -> str:
    data = path.read_bytes()
    return hashlib.sha1(b"blob " + str(len(data)).encode() + b"\0" + data).hexdigest()

def check(ok: bool, message: str) -> None:
    if not ok:
        raise ValueError(message)

def is_child(root: Path, p: Path) -> Path:
    q = p.resolve(strict=True)
    check(q != root and q.is_relative_to(root), "PATH_OUTSIDE_TTM_PROJECT")
    return q

def exact(root: Path, path: Path, expected: str) -> Path:
    p = is_child(root, path)
    check(p.is_file() and digest(p) == expected, "FROZEN_SHA256_MISMATCH:" + str(path))
    return p

def read_vectors(path: Path, origin: str):
    data = path.read_bytes().decode("utf-8", "strict")
    check(data.endswith("\n") and data.count("\n") == 4, "EXACT_FOUR_JSONL_LINES:" + origin)
    rows = [json.loads(line) for line in data.splitlines()]
    check([r.get("fixture_id") for r in rows] == list(FIXTURES), "FIXTURE_ORDER_OR_DUPLICATE")
    for row in rows:
        ids = FIXTURES[row["fixture_id"]]
        check(row.get("token_ids") == ids, "TOKEN_IDS_MISMATCH")
        if origin == "ollama":
            check(row.get("schema") == "ttm.ollama.full_logits.runner_pre_sample.v1"
                and row.get("phase") == "PRE_SAMPLING_RAW_F32"
                and row.get("n_vocab") == 2048, "NOT_RAW_PRESAMPLER_F32")
        else:
            check(row.get("source") == "P02_F32_STEP1024_GELU_ERF"
                and row.get("checkpoint_sha256") == CKPT_SHA
                and row.get("p02_git_blob") == P02_BLOB
                and row.get("prereg_git_blob") == PREREG_BLOB,
                "REFERENCE_PROVENANCE_MISMATCH")
        vals = row.get("logits")
        check(isinstance(vals, list) and len(vals) == 2048
              and all(type(v) in (int, float) and math.isfinite(v) for v in vals),
              "LOGITS_NOT_FINITE_2048")
    return rows

def comparison(ref, ollama):
    results = []
    for a,b in zip(ref, ollama):
        fid = a["fixture_id"]
        diffs = [float(y)-float(x) for x,y in zip(a["logits"],b["logits"])]
        idx = max(range(2048),key=lambda i:abs(diffs[i]))
        top_a = max(range(2048),key=lambda i:a["logits"][i])
        top_b = max(range(2048),key=lambda i:b["logits"][i])
        results.append({
            "fixture_id": fid,
            "n_logits": 2048,
            "max_abs": abs(diffs[idx]),
            "mean_abs": sum(abs(v) for v in diffs) / 2048,
            "peak_index": idx,
            "signed_peak_ollama_minus_p02": diffs[idx],
            "top1_reference": top_a,
            "top1_ollama": top_b,
            "top1_equal": top_a == top_b,
            "strict_pass": abs(diffs[idx]) <= THRESHOLD and top_a == top_b,
        })
    return results

def verify_comparison(recomputed, owner_audit):
    check(len(owner_audit.get("rows",[])) == 4, "ORIGINAL_NUMERIC_AUDIT_ROWS")
    check(owner_audit.get("status") == "NUMERIC_PASS_PROVENANCE_PENDING"
          and owner_audit.get("strict_pass_count") == 4
          and owner_audit.get("threshold") == THRESHOLD
          and owner_audit.get("full_logits_evaluated") == 8192,
          "ORIGINAL_NUMERIC_AUDIT_STATUS_MISMATCH")
    for ours, original in zip(recomputed, owner_audit["rows"]):
        for k in ("fixture_id", "n_logits", "peak_index", "top1_reference",
                  "top1_ollama", "top1_equal", "strict_pass"):
            check(ours[k] == original[k],"INDEPENDENT_NUMERIC_DISAGREEMENT:"+k)
        for k in ("max_abs", "mean_abs", "signed_peak_ollama_minus_p02"):
            check(math.isclose(ours[k], original[k],abs_tol=1e-12,rel_tol=0),
                  "INDEPENDENT_FLOAT_DISAGREEMENT:"+k)
    check(all(r["strict_pass"] for r in recomputed), "STRICT_PARITY_FAIL")
    return {"pass": True,"rows":4,"logits_compared":8192,
            "max_abs_global":max(x["max_abs"] for x in recomputed),
            "top1_equal":4, "per_fixture":recomputed}

def verify_provenance(stage: Path, receipt: dict, log: str, cleanup: str,
                      runner: Path, blob: Path):
    check(receipt.get("source_head") == SOURCE_HEAD
          and receipt.get("status") == "NUMERIC_PASS_PROVENANCE_REVIEW_PENDING"
          and receipt.get("inference_started") is True
          and receipt.get("fixture_ids_completed") == list(FIXTURES)
          and receipt.get("strict_pass_count") == 4
          and receipt.get("main_changed") is False
          and receipt.get("TEST") is False
          and receipt.get("training") is False
          and receipt.get("T5_WINDOWS_F32") == "PASS_SCOPED_UNCHANGED",
          "OWNER_RECEIPT_SCOPE_OR_STATUS_MISMATCH")
    check(receipt.get("api_port") == 12651
          and receipt.get("runner_sha256") == RUNNER_SHA
          and receipt.get("reference_sha256") == REFERENCE_SHA
          and receipt.get("reference_seal_sha256") == REFERENCE_SEAL_SHA
          and receipt.get("model_sha256") == GGUF_SHA
          and receipt.get("ollama_sha256") == OLLAMA_SHA,
          "OWNER_RECEIPT_INPUT_PROVENANCE_MISMATCH")
    parent = receipt.get("parent_pid")
    childrows=receipt.get("child_provenance")
    check(type(parent) is int and parent > 0 and isinstance(childrows,list)
          and len(childrows) == 4, "MISSING_PARENTPID_OR_CHILD_SNAPSHOTS")
    ids={x.get("child_pid") for x in childrows}
    check(len(ids)==1,"MULTIPLE_CHILD_PIDS")
    pid=next(iter(ids))
    check(type(pid) is int and pid > 0 and pid!=parent,"INVALID_CHILD_PID")
    check(re.search(r"Listening on 127[.]0[.]0[.]1:12651",log) is not None
          and len(re.findall(r'POST\s+"/api/generate"',log)) == 4
          and len(re.findall('msg="starting llama-server"',log)) == 1,
          "OLLAMA_LOG_NOT_ONE_CHILD_AND_FOUR_REQUESTS")
    check("K (f32)" in log and "V (f32)" in log
          and re.search(r"flash_attn\s*=\s*disabled",log) is not None
          and "no implementations specified for speculative decoding" in log,
          "NATIVE_RUNTIME_KV_FLASH_SPEC_MISMATCH")
    for n in (3,6):
        expected = 3 if n==3 else 1
        check(len(re.findall(r"task[.]n_tokens = "+str(n)+r"\b",log)) == expected,
              "RUNTIME_PROMPT_LENGTH_MISMATCH")
    ports=set()
    for i,row in enumerate(childrows):
        check(row.get("fixture")==list(FIXTURES)[i]
              and row.get("child_pid")==pid
              and row.get("parent_pid")==parent
              and row.get("kv_f32") is True and row.get("flash_off") is True
              and row.get("ollama_child_launch_lines")==1
              and Path(row["child_path"]).resolve(strict=True) == runner,
              "CIM_SNAPSHOT_PATH_OR_PID_MISMATCH")
        command=row["child_command_line"]
        needed=[str(runner), str(blob),"--host 127.0.0.1","-ngl 0",
                "-t 1","-np 1","-c 256","--cache-type-k f32",
                "--cache-type-v f32","--flash-attn off"]
        check(all(s in command for s in needed),"CHILD_COMMAND_FLAGS_MISMATCH")
        m=re.search(r"--port\s+(\d+)",command)
        check(m is not None and int(m.group(1))>0,"CHILD_LISTEN_PORT_UNKNOWN")
        ports.add(int(m.group(1)))
    check(len(ports)==1 and ports!={12651},"CHILD_NATIVE_PORT_MISMATCH")
    nativeport=next(iter(ports))
    check("listening on http://127.0.0.1:"+str(nativeport) in log,
          "NATIVE_PORT_NOT_IN_SERVER_LOG")
    check(receipt.get("child_final",{}).get("child_pid")==pid
          and receipt.get("owned_cleanup_returncode")==0
          and type(receipt.get("parent_exitcode")) is int,
          "OWNED_PROCESS_COMPLETION_NOT_RECORDED")
    check("PID "+str(pid) in cleanup and "PID "+str(parent) in cleanup
          and cleanup.count("SUCCESS:") >= 2,
          "OWNED_PROCESS_CLEANUP_LOG_NOT_CORROBORATED")
    return {
        "status":"PASS_RECORDED_CIM_CHILD_AND_OLLAMA_LOG_CORROBORATED",
        "parent_pid":parent,"child_pid":pid,
        "native_port":nativeport,"ollama_api_port":12651,
        "snapshots":4,"one_child_launch":True,"api_requests":4,
        "cpu_only":True,"kv_cache":"F32","flash_attention":"OFF",
        "live_pid_rewitness_after_shutdown":False,
        "note":"Original owner runner collected CIM observations while running; independent reviewer verified immutable snapshots and matching server log after shutdown."
    }

def main():
    p=argparse.ArgumentParser()
    p.add_argument("--project-root",required=True,type=Path)
    p.add_argument("--worktree",required=True,type=Path)
    p.add_argument("--expected-head",required=True)
    a=p.parse_args()
    if sys.version_info[:2] != (3,12):
        raise ValueError("PYTHON312_REQUIRED")
    root=a.project_root.resolve(strict=True)
    check(root == ROOT.resolve(strict=True), "EXACT_PROJECT_ROOT_MISMATCH")
    work=is_child(root,a.worktree)
    git=shutil.which("git.exe")
    check(bool(git),"GIT_NOT_INSTALLED")
    def g(*args):
        out=subprocess.run([git,"-C",str(work),*args],capture_output=True,
                           text=True,check=False,timeout=20)
        check(out.returncode==0,"GIT_CHECK_FAILED")
        return out.stdout.strip()
    check(g("branch","--show-current")==BRANCH
          and g("rev-parse","HEAD")==a.expected_head
          and not g("status","--porcelain","--untracked-files=all"),
          "EXACT_CLEAN_RESEARCH_HEAD_REQUIRED")
    stage=is_child(root,root/"_tmp/fl3")
    destination=stage/"INDEPENDENT_FINAL_ADJUDICATION.json"
    check(not destination.exists() and not destination.is_symlink(),
          "INDEPENDENT_ADJUDICATION_ALREADY_EXISTS")
    inputs={name:exact(root,stage/name,d) for name,d in FILES.items()}
    rfile=exact(root,stage/"RUN_RECEIPT.json",RUN_SHA)
    receipt=json.loads(rfile.read_text("utf-8"))
    check(receipt.get("artifact_sha256")==FILES,
          "RUN_RECEIPT_ALL_OUTPUT_HASHES_MISMATCH")
    reference_dir=is_child(root,root/"_tmp/ttm_ollama_full_logits_reference_fl01_fl04_20261111")
    ref=exact(root,reference_dir/"REFERENCE_P02_F32_FL01_FL04.jsonl",REFERENCE_SHA)
    seal=exact(root,reference_dir/"REFERENCE_INDEPENDENT_SEAL.json",REFERENCE_SEAL_SHA)
    seal_json=json.loads(seal.read_text("utf-8"))
    check(seal_json.get("status")=="PASS_REFERENCE_4_OF_4_X_2048"
          and seal_json.get("reference_sha256")==REFERENCE_SHA,
          "REFERENCE_SEAL_STATUS_CHANGED")
    prereg=is_child(root,work/"artifacts/qa/ttm-ollama-full-logits/TTM_OLLAMA_FULL_LOGITS_F32_PREREG_20261111.json")
    check(blob_sha(prereg)==PREREG_BLOB,"PREREG_BLOB_CHANGED")
    frozen=json.loads(prereg.read_text("utf-8"))
    check(frozen["measurement"]["absolute_error_threshold"]==THRESHOLD
          and frozen["measurement"]["logits_per_row"]==2048
          and [(x["fixture_id"],x["token_ids"]) for x in frozen["fixtures"]]==list(FIXTURES.items()),
          "PREREG_CHANGED_AFTER_RUN")
    package=is_child(root,root/"_tmp/fl2/package")
    runner=exact(root,package/"lib/ollama/llama-server.exe",RUNNER_SHA)
    exact(root,package/"ollama.exe",OLLAMA_SHA)
    exact(root,root/"_tmp/ttm_t5_trained_f32_v1/TTM-Small4M-T4-step1024-F32.gguf",GGUF_SHA)
    blob=exact(root,stage/"models/blobs"/("sha256-"+GGUF_SHA),GGUF_SHA)
    check(receipt.get("raw_sha256")==FILES["OLLAMA_RAW_FL01_FL04.jsonl"]
          and receipt.get("numeric_audit_sha256")==FILES["NUMERIC_AUDIT.json"],
          "RECEIPT_RAW_OR_AUDIT_PIN_CHANGED")
    refs=read_vectors(ref,"reference")
    vectors=read_vectors(inputs["OLLAMA_RAW_FL01_FL04.jsonl"],"ollama")
    calculated=comparison(refs,vectors)
    original=json.loads(inputs["NUMERIC_AUDIT.json"].read_text("utf-8"))
    check(original.get("ollama_dump_sha256")==FILES["OLLAMA_RAW_FL01_FL04.jsonl"]
          and original.get("reference_sha256")==REFERENCE_SHA,
          "ORIGINAL_NUMERIC_AUDIT_SHA_MISMATCH")
    numbers=verify_comparison(calculated,original)
    serve_log=inputs["OLLAMA_SERVE.log"].read_text("utf-8",errors="replace")
    cleanup_log=inputs["OWNED_PROCESS_CLEANUP.log"].read_text("utf-8",errors="replace")
    provenance=verify_provenance(stage,receipt,serve_log,cleanup_log,runner,blob)
    report={
       "schema":"ttm.ollama.full_logits.final_independent_readback_adjudication.v1",
       "date":"2026-11-11",
       "status":"PASS_SCOPED_OLLAMA_CHILD_FULL_RAW_LOGITS_4_OF_4",
       "scientific_scope":"Fixed P02 checkpoint and trained GELU_ERF F32 GGUF on Windows CPU, four preregistered prompt token sequences.",
       "numeric":numbers,"provenance":provenance,
       "input_sha256":{"run_receipt":RUN_SHA,**FILES,
          "reference":REFERENCE_SHA,"reference_seal":REFERENCE_SEAL_SHA,
          "GGUF":GGUF_SHA,"runner":RUNNER_SHA,"ollama_cli":OLLAMA_SHA},
       "prereg_git_blob":PREREG_BLOB,
       "underlying_run_source_head":SOURCE_HEAD,
       "independent_readback_worktree_head":a.expected_head,
       "independent_method":"Fresh source re-reads and hashes entire raw+reference JSONL, independently calculates 8192 differences and cross checks source numeric audit, CIM snapshots, native runtime log, cleanup evidence. No model inference or TEST access.",
       "limitations":["The full original JSONL files and checkpoint remain local, not uploaded to GitHub.",
          "Raw-file SHA rehash and re-comparison on owner machine, not a second native execution.",
          "Runtime PIDs were witnessed by original runner during execution and are no longer live.",
          "Pass applies only to four prompts, CPU, KV F32, Flash OFF, fixed trained model and custom build; does not prove universal equivalence, bitwise equality, or stock Ollama support.",
          "The original NUMERIC_AUDIT.json contains inherited field T5_OLLAMA_FULL_LOGITS=NOT_EXECUTED_UNCHANGED; preserve original bytes and interpret numeric status and run receipt as the scope of this separate experiment."],
       "main_modified":False,"existing_T5_WINDOWS_F32":"PASS_SCOPED_UNCHANGED",
       "training":False,"TEST":False,"inference_reexecuted":False,
       "lineage_write":False
    }
    with destination.open("x",encoding="utf-8",newline="\n") as out:
        json.dump(report,out,ensure_ascii=False,indent=2,sort_keys=True)
        out.write("\n")
    print("INDEPENDENT_FULL_LOGITS_REHASH=PASS_4X2048",flush=True)
    print("INDEPENDENT_OLLAMA_CHILD_PROVENANCE=PASS_RECORDED_CIM_AND_LOG",flush=True)
    print("INDEPENDENT_FINAL_VERDICT="+report["status"],flush=True)
    print("INDEPENDENT_FINAL_SHA256="+digest(destination),flush=True)
    print("OLLAMA_INFERENCE_REEXECUTED=FALSE",flush=True)

if __name__=="__main__":
    try:main()
    except (OSError,ValueError,KeyError,TypeError,RuntimeError,UnicodeError) as ex:
        print("TTM_FULL_LOGITS_INDEPENDENT_ADJUDICATION_HOLD:"+type(ex).__name__+":"+str(ex),
              file=sys.stderr)
        raise SystemExit(2)
