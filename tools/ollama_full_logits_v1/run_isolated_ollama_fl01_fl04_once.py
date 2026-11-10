#!/usr/bin/env python3
"""TTM Ollama FL01-FL04 exact one-shot raw pre-sampling capture; Windows CPU only.
No TEST, training, network download, automatic retry, changes to frozen v5/main.
"""
from __future__ import annotations
import argparse, hashlib, json, math, os, re, shutil, socket, subprocess, sys, time
from http.client import HTTPConnection
from pathlib import Path

ROOT=Path("D:/WORK/RESEARCH/TokenToModel-Lab")
BRANCH="research/ttm-t5-ollama-full-logits-20261111"
PORT=12651
MODEL="ttm-t5-gelu-erf-f32"
BUILD_RECEIPT_SHA="86f2aa3ffc5dbedfc67de009721009577d11645d8aad0f025bda32ef8460b122"
RUNNER_SHA="818fec27008b0a8555ecbae09c8c95e6a076d2b2fa4c26377b8bdb248232210a"
OLLAMA_SHA="7544d36e5bb4c9cfddbd48a400ea4f1919de8fcea80510e1847627ec92909e43"
GGUF_SHA="5bdc904e6c51af04a4223219f36e6bc2e687f60fd6e17dc24508f3eb7489e4e5"
REF_SHA="1e098a643c9bce66431adf3dc0296ce6b628731d33c4532753d2f2acd664d082"
SEAL_SHA="571a1a654bad1b97de066d6fb3b690e910ecc71777deb4b16b7b15968f444939"
FIX=[("FL01","abc",[97,98,99]),("FL02","hello",[257,304,111]),
     ("FL03","a\nb",[97,10,98]),("FL04","Xin chào",[88,267,628,195,160,111])]

def sha(path):
    h=hashlib.sha256()
    with path.open("rb") as f:
        for b in iter(lambda:f.read(1<<20),b""):h.update(b)
    return h.hexdigest()

def within(root,path,exists=True):
    p=path.resolve(strict=exists)
    if p==root or not p.is_relative_to(root):raise ValueError("PATH_OUTSIDE_TTM")
    return p

def exact(root,path,digest):
    p=within(root,path)
    if not p.is_file() or sha(p)!=digest:raise ValueError("FILE_SHA_MISMATCH:"+str(path))
    return p

def gitcheck(git,work,*args):
    q=subprocess.run([git,"-C",str(work),*args],capture_output=True,text=True,timeout=25,check=False)
    if q.returncode:raise RuntimeError("GIT_CHECK_FAILED:"+q.stderr[-500:])
    return q.stdout.strip()

def request(route,payload=None,timeout=15):
    c=HTTPConnection("127.0.0.1",PORT,timeout=timeout)
    try:
        body=None if payload is None else json.dumps(payload,ensure_ascii=False).encode("utf-8")
        c.request("GET" if payload is None else "POST",route,body,
                  {"Content-Type":"application/json; charset=utf-8"})
        r=c.getresponse(); data=r.read()
        if r.status!=200:
            raise RuntimeError("OLLAMA_HTTP_"+str(r.status)+":"+data[:400].decode("utf-8","replace"))
        return json.loads(data)
    finally:c.close()

def wait_ready(proc):
    deadline=time.monotonic()+90
    while time.monotonic()<deadline:
        if proc.poll() is not None:raise RuntimeError("OLLAMA_PARENT_EXITED:"+str(proc.returncode))
        try:
            ver=request("/api/version",timeout=2).get("version")
            if ver=="0.40.14":return
            raise ValueError("WRONG_OLLAMA_VERSION:"+str(ver))
        except (OSError,TimeoutError):time.sleep(.25)
    raise RuntimeError("OLLAMA_READINESS_TIMEOUT")

def check_rows(path,n):
    if not path.is_file():raise ValueError("NO_RAW_LOGITS_OUTPUT")
    raw=path.read_bytes().decode("utf-8")
    if not raw.endswith("\n") or raw.count("\n")!=n:
        raise ValueError("RAW_ROWS_MISMATCH_EXPECTED_"+str(n))
    rows=[json.loads(s) for s in raw.splitlines()]
    for i,row in enumerate(rows):
        fid,_,ids=FIX[i]
        if (row.get("fixture_id")!=fid or row.get("token_ids")!=ids
            or row.get("phase")!="PRE_SAMPLING_RAW_F32"
            or row.get("schema")!="ttm.ollama.full_logits.runner_pre_sample.v1"
            or row.get("n_vocab")!=2048):
            raise ValueError("RAW_TOKEN_OR_SOURCE_MISMATCH:"+fid)
        vals=row.get("logits")
        if (not isinstance(vals,list) or len(vals)!=2048
            or any(type(x) not in (float,int) or not math.isfinite(x) for x in vals)):
            raise ValueError("RAW_LOGITS_WRONG_SIZE_OR_NONFINITE:"+fid)
    return rows

def live_provenance(parent,runner,blob,log,prior_pid):
    ps=Path(os.environ["SystemRoot"])/"System32/WindowsPowerShell/v1.0/powershell.exe"
    query=("$p=@(Get-CimInstance Win32_Process -Filter 'ParentProcessId="+str(parent)+
        "' | Where-Object Name -eq 'llama-server.exe');"+
        "if($p.Count -ne 1){exit 4};"+
        "$p[0] | Select-Object ProcessId,ParentProcessId,ExecutablePath,CommandLine | ConvertTo-Json -Compress")
    p=subprocess.run([str(ps),"-NoProfile","-NonInteractive","-Command",query],
                     capture_output=True,timeout=30,check=False)
    if p.returncode:raise ValueError("NO_EXACT_OWNED_CHILD:"+p.stderr.decode("utf-8","replace")[-300:])
    child=json.loads(p.stdout.decode("utf-8-sig"))
    pid=int(child["ProcessId"])
    if (int(child["ParentProcessId"])!=parent
        or Path(child["ExecutablePath"]).resolve(strict=True)!=runner
        or (prior_pid is not None and pid!=prior_pid)):
        raise ValueError("PARENT_OR_CHILD_PATH_CHANGED")
    command=str(child["CommandLine"]).replace("\\\\","\\")
    required=[str(runner),str(blob),"--cache-type-k f32","--cache-type-v f32",
              "--flash-attn off","-ngl 0","-t 1","-np 1","-c 256","--host 127.0.0.1"]
    if not all(item in command for item in required):
        raise ValueError("ACTUAL_CHILD_ARGS_MISMATCH")
    data=log.read_text("utf-8",errors="replace")
    launches=[s for s in data.splitlines() if 'msg="starting llama-server"' in s]
    if (len(launches)!=1 or "K (f32)" not in data or "V (f32)" not in data
        or re.search(r"flash_attn\s*=\s*disabled",data) is None):
        raise ValueError("NATIVE_LOG_PROVENANCE_MISSING")
    return {"parent_pid":parent,"child_pid":pid,"child_path":str(runner),
            "child_command_line":command,"kv_f32":True,"flash_off":True,
            "ollama_child_launch_lines":len(launches)}

def main():
    pa=argparse.ArgumentParser()
    pa.add_argument("--project-root",required=True,type=Path)
    pa.add_argument("--worktree",required=True,type=Path)
    pa.add_argument("--expected-head",required=True)
    a=pa.parse_args()
    if os.name!="nt" or sys.version_info[:2]!=(3,12):
        raise ValueError("WINDOWS_PYTHON312_REQUIRED")
    root=a.project_root.resolve(strict=True)
    if root!=ROOT.resolve(strict=True):raise ValueError("EXACT_TTM_ROOT")
    work=within(root,a.worktree)
    if not (work/".git").exists():raise ValueError("MISSING_GIT_WORKTREE")
    git=shutil.which("git.exe")
    if not git or gitcheck(git,work,"branch","--show-current")!=BRANCH:
        raise ValueError("WRONG_BRANCH")
    if len(a.expected_head)!=40 or gitcheck(git,work,"rev-parse","HEAD")!=a.expected_head:
        raise ValueError("SOURCE_COMMIT_NOT_EXACT")
    if gitcheck(git,work,"status","--porcelain","--untracked-files=all"):
        raise ValueError("WORKTREE_DIRTY")
    build=within(root,root/"_tmp/fl2")
    receipt=exact(root,build/"STAGE_RECEIPT.json",BUILD_RECEIPT_SHA)
    b=json.loads(receipt.read_text("utf-8"))
    if (b.get("status")!="BUILD_PASS_ISOLATED_NO_OLLAMA_INFERENCE"
        or b.get("candidate_native_runner_sha256")!=RUNNER_SHA
        or b.get("runner_inference")!="NOT_EXECUTED"):
        raise ValueError("FROZEN_BUILD_RECEIPT_WRONG")
    package=within(root,build/"package")
    ollama=exact(root,package/"ollama.exe",OLLAMA_SHA)
    runner=exact(root,package/"lib/ollama/llama-server.exe",RUNNER_SHA)
    gguf=exact(root,root/"_tmp/ttm_t5_trained_f32_v1/TTM-Small4M-T4-step1024-F32.gguf",GGUF_SHA)
    model_src=within(root,root/"_tmp/t5-ollama-custom-v5/models")
    exact(root,model_src/"blobs"/("sha256-"+GGUF_SHA),GGUF_SHA)
    refs=within(root,root/"_tmp/ttm_ollama_full_logits_reference_fl01_fl04_20261111")
    exact(root,refs/"REFERENCE_P02_F32_FL01_FL04.jsonl",REF_SHA)
    exact(root,refs/"REFERENCE_INDEPENDENT_SEAL.json",SEAL_SHA)
    prereg=within(root,work/"artifacts/qa/ttm-ollama-full-logits/TTM_OLLAMA_FULL_LOGITS_F32_PREREG_20261111.json")
    auditor=within(root,work/"tools/ollama_full_logits_v1/independent_full_logits_audit.py")
    # Never take an active local service's port, and never stop non-owned processes.
    with socket.socket(socket.AF_INET,socket.SOCK_STREAM) as probe:
        probe.setsockopt(socket.SOL_SOCKET,socket.SO_EXCLUSIVEADDRUSE,1)
        probe.bind(("127.0.0.1",PORT))
    stage=within(root,root/"_tmp/fl3",exists=False)
    if stage.exists() or stage.is_symlink():raise FileExistsError("STAGE_ALREADY_EXISTS_NO_REPLAY")
    stage.mkdir(parents=True,exist_ok=False)
    evidence={"schema":"ttm.ollama.full_logits.one_shot.v1","status":"HOLD_STAGE_STARTED",
              "source_head":a.expected_head,"runner_sha256":RUNNER_SHA,
              "ollama_sha256":OLLAMA_SHA,"model_sha256":GGUF_SHA,
              "reference_sha256":REF_SHA,"reference_seal_sha256":SEAL_SHA,
              "api_port":PORT,"fixture_ids_completed":[],"child_provenance":[],
              "inference_started":False,"training":False,"TEST":False,
              "T5_WINDOWS_F32":"PASS_SCOPED_UNCHANGED","main_changed":False}
    proc=None
    raw=stage/"OLLAMA_RAW_FL01_FL04.jsonl"
    log=stage/"OLLAMA_SERVE.log"
    try:
        for item in model_src.rglob("*"):
            if item.is_symlink():raise ValueError("MODEL_REGISTRY_SYMLINK")
        shutil.copytree(model_src,stage/"models")
        blob=exact(root,stage/"models"/"blobs"/("sha256-"+GGUF_SHA),GGUF_SHA)
        for d in ("home","temp"):(stage/d).mkdir()
        env={k:v for k,v in os.environ.items()
             if not k.upper().startswith(("OLLAMA_","LLAMA_","GGML_","CUDA_","HIP_","ROCR_"))}
        env.update({"TEMP":str(stage/"temp"),"TMP":str(stage/"temp"),"TMPDIR":str(stage/"temp"),
                    "USERPROFILE":str(stage/"home"),"HOME":str(stage/"home"),
                    "OLLAMA_MODELS":str(stage/"models"),"OLLAMA_HOST":f"127.0.0.1:{PORT}",
                    "OLLAMA_NO_CLOUD":"true","OLLAMA_CREATE_REMOTE":"false","OLLAMA_NOHISTORY":"true",
                    "OLLAMA_VULKAN":"false","OLLAMA_KV_CACHE_TYPE":"f32",
                    "OLLAMA_FLASH_ATTENTION":"false","OLLAMA_NUM_PARALLEL":"1",
                    "OLLAMA_MAX_LOADED_MODELS":"1",
                    "TTM_OLLAMA_FULL_LOGITS_OUTPUT":str(raw)})
        with log.open("xb") as fh:
            proc=subprocess.Popen([str(ollama),"serve"],cwd=str(package),env=env,
                                  stdout=fh,stderr=subprocess.STDOUT)
            evidence["parent_pid"]=proc.pid
            try:
                wait_ready(proc)
                tags=request("/api/tags")
                if not any(str(x.get("name","")).startswith(MODEL+":")
                           for x in tags.get("models",[])):
                    raise ValueError("FROZEN_MODEL_TAG_NOT_FOUND_IN_ISOLATED_REGISTRY")
                options={"num_gpu":0,"num_thread":1,"num_ctx":256,
                         "num_predict":1,"temperature":0,"seed":42}
                pid=None
                evidence["inference_started"]=True
                for n,(fid,prompt,ids) in enumerate(FIX,start=1):
                    if proc.poll() is not None:raise RuntimeError("PARENT_EXITED_DURING_FIXTURES")
                    response=request("/api/generate",
                        {"model":MODEL,"prompt":prompt,"raw":True,"stream":False,
                         "keep_alive":"5m","options":options},timeout=120)
                    if response.get("done") is not True:
                        raise ValueError("INCOMPLETE_OLLAMA_GENERATE:"+fid)
                    check_rows(raw,n)
                    child=live_provenance(proc.pid,runner,blob,log,pid)
                    pid=child["child_pid"]
                    evidence["child_provenance"].append({"fixture":fid,**child})
                    evidence["fixture_ids_completed"].append(fid)
                    print("OLLAMA_FULL_LOGITS_CAPTURE="+fid+"_PASS_2048",flush=True)
                evidence["raw_sha256"]=sha(raw)
                num=stage/"NUMERIC_AUDIT.json"
                audit=subprocess.run([sys.executable,"-B",str(auditor),
                    "--project-root",str(root),"--prereg",str(prereg),
                    "--reference",str(refs/"REFERENCE_P02_F32_FL01_FL04.jsonl"),
                    "--ollama",str(raw),"--output",str(num)],
                    capture_output=True,text=True,timeout=50,check=False)
                (stage/"NUMERIC_AUDIT_RUN.log").write_text(
                    audit.stdout+"\n"+audit.stderr+"\nEXIT_CODE="+str(audit.returncode)+"\n",
                    encoding="utf-8")
                if audit.returncode:raise ValueError("NUMERIC_AUDITOR_TECHNICAL_FAILURE")
                result=json.loads(num.read_text("utf-8"))
                evidence["numeric_audit_sha256"]=sha(num)
                evidence["numeric_status"]=result["status"]
                evidence["strict_pass_count"]=result["strict_pass_count"]
                evidence["max_abs_by_fixture"]={x["fixture_id"]:x["max_abs"] for x in result["rows"]}
                evidence["child_final"]=live_provenance(proc.pid,runner,blob,log,pid)
                evidence["status"]=("NUMERIC_PASS_PROVENANCE_REVIEW_PENDING"
                    if result["status"]=="NUMERIC_PASS_PROVENANCE_PENDING"
                    else "NUMERIC_FAIL_PROVENANCE_REVIEW_PENDING")
            finally:
                if proc.poll() is None:
                    killer=Path(os.environ["SystemRoot"])/"System32/taskkill.exe"
                    with (stage/"OWNED_PROCESS_CLEANUP.log").open("xb") as f:
                        stopped=subprocess.run([str(killer),"/PID",str(proc.pid),"/T","/F"],
                                               stdout=f,stderr=subprocess.STDOUT,timeout=25)
                    evidence["owned_cleanup_returncode"]=stopped.returncode
                try:proc.wait(timeout=25)
                except subprocess.TimeoutExpired:evidence["cleanup_hold"]="PARENT_NOT_REAPED"
                evidence["parent_exitcode"]=proc.poll()
                if evidence["parent_exitcode"] is None:
                    raise RuntimeError("OWNED_OLLAMA_PARENT_STILL_RUNNING")
                if ("owned_cleanup_returncode" in evidence
                    and evidence["owned_cleanup_returncode"]!=0):
                    raise RuntimeError("OWNED_PROCESS_TREE_CLEANUP_COMMAND_FAILED")
    except Exception as exc:
        evidence["status"]="HOLD_PARTIAL_CAPTURE_NO_REPLAY"
        evidence["failure"]=type(exc).__name__+":"+str(exc)
        print("OLLAMA_FULL_LOGITS_RUN_HOLD="+evidence["failure"],file=sys.stderr,flush=True)
    finally:
        evidence["artifact_sha256"]={}
        for f in sorted(stage.iterdir()):
            if f.is_file():evidence["artifact_sha256"][f.name]=sha(f)
        output=stage/"RUN_RECEIPT.json"
        with output.open("x",encoding="utf-8",newline="\n") as stream:
            json.dump(evidence,stream,indent=2,sort_keys=True,ensure_ascii=False)
            stream.write("\n")
        print("OLLAMA_FULL_LOGITS_RUN_STATUS="+evidence["status"],flush=True)
        print("OLLAMA_FULL_LOGITS_RUN_RECEIPT_SHA256="+sha(output),flush=True)
        print("T5_WINDOWS_F32=PASS_SCOPED_UNCHANGED",flush=True)
    if evidence["status"] not in ("NUMERIC_PASS_PROVENANCE_REVIEW_PENDING",
                                   "NUMERIC_FAIL_PROVENANCE_REVIEW_PENDING"):
        raise SystemExit(2)

if __name__=="__main__":
    try:main()
    except (OSError,ValueError,RuntimeError,TypeError,KeyError) as exc:
        print("OLLAMA_FULL_LOGITS_PREFLIGHT_HOLD="+type(exc).__name__+":"+str(exc),file=sys.stderr)
        raise SystemExit(3)
