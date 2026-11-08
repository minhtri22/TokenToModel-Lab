#!/usr/bin/env python3
"""TTM T5 Ollama F32 successor V3 TCP table ownership gate — source-only, Windows/Python 3.12, stdlib.

Never rerun with an existing CLAIM. Never touches the usual Ollama service.
All intended writes are confined to the TTM project-local evidence root.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import ntpath
import os
from pathlib import Path
import re
import shutil
import socket
import stat
import subprocess
import sys
import time
import traceback
import urllib.error
import urllib.request
from datetime import datetime, timezone

ROOT = Path(r"D:\WORK\RESEARCH\TokenToModel-Lab")
SOURCE_DIR = ROOT / "_tmp" / "ttm_t5_trained_f32_v1"
GGUF = SOURCE_DIR / "TTM-Small4M-T4-step1024-F32.gguf"
ORIGINAL = SOURCE_DIR / "T5_TRAINED_LLAMA_CPP_PARITY.json"
V5B = SOURCE_DIR / "T5_LLAMA_UTF8_V5B_ROOTCAUSE_DIAGNOSTIC_V1.json"
OUT = ROOT / "_tmp" / "ttm_t5_ollama_compat_only_single_v3"
EXE = Path(r"C:\Users\minht\AppData\Local\Programs\Ollama\ollama.exe")
GGUF_SHA = "5bdc904e6c51af04a4223219f36e6bc2e687f60fd6e17dc24508f3eb7489e4e5"
ORIGINAL_SHA = "c61f73216764b8582a5c996e85c59feb55b13496ec0117deb713d9b1843ec8e8"
V5B_SHA = "ac699d4e750037f88bbab776bb42a38079cd82b0a1c2f72385127ac5a36d9375"
GGUF_BYTES = 15061376
VERSION = "0.40.14"
PORT = 12645
HOST = f"127.0.0.1:{PORT}"
API = f"http://{HOST}"
MODEL = "ttm-t5-f32-compat-only-v3:latest"
PROMPT = "Once upon a time, a small robot"
MAX_TOKENS = 32
CONTEXT = 256
MIN_DISK_BYTES = 1024 * 1024 * 1024
READINESS_MAX_SAMPLES = 40
READINESS_SLEEP_SECONDS = 0.5
SCHEMA = "ttm.t5.ollama.compatibility.project-local.one-shot.v3-candidate"


def now() -> str:
    return datetime.now(timezone.utc).isoformat()


def sha256(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as f:
        while True:
            block = f.read(1024 * 1024)
            if not block:
                break
            h.update(block)
    return h.hexdigest()


def forbid_reparse(path: Path) -> None:
    """Reject symlink/junction/reparse in existing components of a selected path."""
    p = path.absolute()
    chain = [p, *p.parents]
    for item in reversed(chain):
        if not item.exists() and not item.is_symlink():
            continue
        attrs = getattr(item.lstat(), "st_file_attributes", 0)
        reparse = bool(attrs & getattr(stat, "FILE_ATTRIBUTE_REPARSE_POINT", 0x400))
        if item.is_symlink() or reparse or (hasattr(item, "is_junction") and item.is_junction()):
            raise RuntimeError(f"REPARSE_PATH_DENIED:{item}")


def require(cond: bool, message: str) -> None:
    if not cond:
        raise RuntimeError(message)



PS_TCP_TABLE_QUERY = '$ErrorActionPreference = \'Stop\'\n$port = __PORT__\n$rows = @(\n    Get-NetTCPConnection -ErrorAction Stop |\n      Where-Object { [int]$_.LocalPort -eq $port } |\n      ForEach-Object {\n          [pscustomobject]@{\n              local_address = [string]$_.LocalAddress\n              local_port = [int]$_.LocalPort\n              state = [string]$_.State\n              pid = [int]$_.OwningProcess\n          }\n      }\n)\n$listenPids = @($rows | Where-Object { $_.state -eq \'Listen\' } | Select-Object -ExpandProperty pid -Unique)\n$processes = @(\n    foreach ($ownerPid in $listenPids) {\n        if ($ownerPid -le 0) { throw \'INVALID_LISTEN_PID\' }\n        $proc = Get-CimInstance Win32_Process -Filter ("ProcessId = {0}" -f [uint32]$ownerPid) -ErrorAction Stop\n        if ($null -ne $proc) {\n            [pscustomobject]@{\n                pid = [int]$proc.ProcessId\n                name = [string]$proc.Name\n                executable_path = [string]$proc.ExecutablePath\n                creation_date = [string]$proc.CreationDate\n            }\n        }\n    }\n)\n[pscustomobject]@{\n    schema = \'ttm.t5.windows.tcptable.snapshot.v1\'\n    port = $port\n    rows = @($rows)\n    processes = @($processes)\n} | ConvertTo-Json -Compress -Depth 6\n'

# Windows 5.1 output encoded as UTF-16LE base64 for -EncodedCommand.
def tcp_table_observation(port: int) -> dict:
    """Read TCP connections and process identity via NetTCPIP+CIM; no mutation."""
    if type(port) is not int or not (1 <= port <= 65535):
        raise RuntimeError("INVALID_TCP_PORT")
    command = PS_TCP_TABLE_QUERY.replace("__PORT__", str(port))
    encoded = __import__("base64").b64encode(command.encode("utf-16le")).decode("ascii")
    executable = r"C:\Windows\System32\WindowsPowerShell\v1.0\powershell.exe"
    p = subprocess.run([executable,"-NoProfile","-NonInteractive","-EncodedCommand",encoded],
        capture_output=True,text=True,encoding="utf-8-sig",errors="replace",timeout=12)
    if p.returncode != 0:
        raise RuntimeError("TCP_TABLE_POWERSHELL_FAILED_RC_" + str(p.returncode))
    if len(p.stdout) > 64*1024:
        raise RuntimeError("TCP_TABLE_OUTPUT_TOO_LARGE")
    try:
        result = json.loads(p.stdout.strip())
    except (ValueError,TypeError) as exc:
        raise RuntimeError("TCP_TABLE_INVALID_JSON") from exc
    if not isinstance(result,dict) or result.get("schema")!="ttm.t5.windows.tcptable.snapshot.v1" or result.get("port") != port:
        raise RuntimeError("TCP_TABLE_SCHEMA_OR_PORT_MISMATCH")
    if not isinstance(result.get("rows"),list) or not isinstance(result.get("processes"),list):
        raise RuntimeError("TCP_TABLE_ARRAYS_INVALID")
    if len(result["rows"]) > 256 or len(result["processes"]) > 16:
        raise RuntimeError("TCP_TABLE_TOO_MANY_ROWS")
    return result


def normalize_win_path(value: str) -> str:
    return ntpath.normcase(ntpath.normpath(value))


def ownership_status(snapshot: dict, expected_pid: int, *, expected_creation: str | None = None) -> dict:
    """Pure decision: reject unsafe listeners, PID mismatch, missing State or identity."""
    result={"decision":"HOLD_TCP_TABLE_MALFORMED", "listener_rows":[],
            "owner_pids":[],"identity":None}
    if not isinstance(snapshot,dict) or snapshot.get("port") != PORT:
        return result
    rows=snapshot.get("rows")
    processes=snapshot.get("processes")
    if not isinstance(rows,list) or not isinstance(processes,list):
        return result
    if type(expected_pid) is not int or expected_pid < 1:
        return result
    listens=[]
    for row in rows:
        if not isinstance(row,dict):
            return result
        addr=row.get("local_address"); state=row.get("state");pid=row.get("pid");localport=row.get("local_port")
        if not isinstance(addr,str) or not addr or not isinstance(state,str) or not state.strip() or type(pid) is not int or pid < 1 or type(localport) is not int or localport!=PORT:
            result["decision"]="HOLD_TCP_ROW_INVALID_OR_MISSING_STATE"
            return result
        if state == "Listen":
            listens.append({"local_address":addr,"local_port":localport,"state":state,"pid":pid})
    result["listener_rows"] = listens
    owners=sorted({row["pid"] for row in listens})
    result["owner_pids"]=owners
    if any(row["local_address"] not in ("127.0.0.1","::1") for row in listens):
        result["decision"]="HOLD_NON_LOOPBACK_OR_WILDCARD_LISTENER"
        return result
    if owners and owners != [expected_pid]:
        result["decision"]="HOLD_UNTRUSTED_OR_MULTIPLE_PID"
        return result
    if not listens:
        result["decision"]="WAIT_NO_LISTEN_ROW"
        return result
    ident=[p for p in processes if isinstance(p,dict) and p.get("pid")==expected_pid]
    if len(ident) != 1 or len(processes) != 1:
        result["decision"]="HOLD_PROCESS_IDENTITY_MISSING_OR_MULTIPLE"
        return result
    p=ident[0]
    executable=p.get("executable_path");name=p.get("name");creation=p.get("creation_date")
    if not all(isinstance(x,str) and bool(x.strip()) for x in (executable,name,creation)):
        result["decision"]="HOLD_PROCESS_IDENTITY_INCOMPLETE"
        return result
    if name.casefold()!="ollama.exe" or normalize_win_path(executable)!=normalize_win_path(str(EXE)):
        result["decision"]="HOLD_UNEXPECTED_EXECUTABLE_IDENTITY"
        return result
    if expected_creation is not None and creation != expected_creation:
        result["decision"]="HOLD_PROCESS_CREATION_CHANGED"
        return result
    result["identity"]={"pid":expected_pid,"name":name,"exe_path_match":True,"creation_date":creation}
    result["decision"]="OWNED_LOOPBACK_LISTEN"
    return result


def assert_owned_listener(proc, expected_creation: str) -> dict:
    """Read-only recheck for after create/generation; fail closed."""
    if proc.poll() is not None:
        raise RuntimeError("OWNED_PROCESS_EXITED")
    check=ownership_status(tcp_table_observation(PORT),proc.pid,expected_creation=expected_creation)
    if check["decision"]!="OWNED_LOOPBACK_LISTEN":
        raise RuntimeError("TCP_OWNER_RECHECK_"+check["decision"])
    return check

def http_version_probe_direct(url: str, timeout: float = 2.0) -> dict:
    """Loopback-only HTTP probe; explicitly bypass inherited/system proxies.

    Does not send any model data, and does not call create/generate endpoints.
    """
    if url != API + "/api/version":
        raise RuntimeError("HTTP_PROBE_URL_NOT_PINNED_LOOPBACK")
    # urllib.request.urlopen() can pick up Windows registry or env proxies.
    # build_opener(ProxyHandler({})) disables proxy routing for this probe.
    opener = urllib.request.build_opener(urllib.request.ProxyHandler({}))
    request = urllib.request.Request(url, method="GET")
    outcome = {"attempted":True,"http_status":None,"api_version":None,
               "error_type":None,"error_code":None}
    try:
        with opener.open(request, timeout=timeout) as resp:
            outcome["http_status"] = int(resp.status)
            payload = resp.read(4097)
            if len(payload) > 4096:
                outcome["error_code"]="BODY_TOO_LONG"
                return outcome
            try:
                obj=json.loads(payload.decode("utf-8"))
                outcome["api_version"] = obj.get("version") if isinstance(obj,dict) else None
                if not isinstance(outcome["api_version"],str):
                    outcome["error_code"]="VERSION_FIELD_INVALID"
            except (ValueError,UnicodeDecodeError) as exc:
                outcome["error_type"] = type(exc).__name__
                outcome["error_code"] = "INVALID_JSON"
    except urllib.error.HTTPError as exc:
        outcome["http_status"] = exc.code
        outcome["error_type"] = "HTTPError"
        outcome["error_code"] = "HTTP_NON_200"
    except (urllib.error.URLError,TimeoutError,OSError) as exc:
        outcome["error_type"] = type(exc).__name__
        outcome["error_code"] = "HTTP_CONNECT_OR_TIMEOUT"
    return outcome


def path_dll_risk_snapshot(env: dict) -> dict:
    """Report only. Does not modify PATH or load any DLLs."""
    needle = r"D:\WORK\RESEARCH\TokenToModel-Lab\_tmp\ttm_t2\build\bin\Release"
    elements = [p.strip().strip('"') for p in env.get("PATH","").split(";") if p.strip()]
    suspicious = [p for p in elements if p.rstrip("\\/").casefold()==needle.casefold()]
    return {"known_ggml_dll_dir_in_path":bool(suspicious),
            "known_ggml_dll_dir":needle if suspicious else None,
            "status":"WARN_ENVIRONMENT_RISK_NOT_CAUSAL_PROOF" if suspicious else "NO_KNOWN_MATCH",
            "path_mutated":False,
            "proxy_env_variable_names_present":[k for k in ("HTTP_PROXY","HTTPS_PROXY","ALL_PROXY","NO_PROXY") if env.get(k)]}



def readiness_sample(proc, attempt: int, *, tcp_fn=None, http_fn=None) -> dict:
    """Two TCP-table identity snapshots bracketing direct HTTP version probe."""
    if tcp_fn is None: tcp_fn=tcp_table_observation
    if http_fn is None: http_fn=http_version_probe_direct
    sample={"attempt":attempt,"observed_utc":now(),"expected_pid":proc.pid,
       "process_exit_code":proc.poll(),"tcp_before":None,"tcp_after":None,
       "ownership_before":None,"ownership_after":None,
       "http":{"attempted":False,"http_status":None,"api_version":None,
               "error_type":None,"error_code":"SKIPPED_UNVERIFIED_OWNER"},
       "decision":"PENDING"}
    if sample["process_exit_code"] is not None:
        sample["decision"]="FAIL_SERVER_EXITED"
        sample["http"]["error_code"]="SKIPPED_PROCESS_EXITED"
        return sample
    try:
        before=tcp_fn(PORT)
        sample["tcp_before"]=before
        first=ownership_status(before,proc.pid)
        sample["ownership_before"]=first
        if first["decision"] != "OWNED_LOOPBACK_LISTEN":
            sample["decision"]=first["decision"]
            return sample
    except Exception as exc:
        sample["tcp_error_type"]=type(exc).__name__
        sample["tcp_error_code"]="TCP_TABLE_QUERY_FAILED"
        sample["decision"]="HOLD_TCP_TABLE_UNAVAILABLE"
        return sample
    try:
        sample["http"]=http_fn(API + "/api/version")
    except Exception as exc:
        sample["http"]={"attempted":True,"http_status":None,"api_version":None,
           "error_type":type(exc).__name__,"error_code":"HTTP_PROBE_EXCEPTION"}
        sample["decision"]="WAIT_HTTP_PROBE_EXCEPTION"
        return sample
    http=sample["http"]
    if not isinstance(http,dict) or http.get("attempted") is not True:
        sample["http"]={"attempted":True,"http_status":None,"api_version":None,
           "error_type":"InvalidProbeReturn","error_code":"HTTP_PROBE_INVALID_RESULT"}
        sample["decision"]="WAIT_HTTP_INVALID_RESULT"
        return sample
    if http.get("http_status") != 200:
        sample["decision"]="WAIT_HTTP_NON_200_OR_UNREACHABLE"
        return sample
    if http.get("error_code") is not None:
        sample["decision"]="WAIT_HTTP_MALFORMED_PAYLOAD"
        return sample
    if http.get("api_version") != VERSION:
        sample["decision"]="WAIT_HTTP_VERSION_MISMATCH"
        return sample
    if proc.poll() is not None:
        sample["process_exit_code_after_http"]=proc.returncode
        sample["decision"]="FAIL_SERVER_EXITED_AFTER_HTTP"
        return sample
    try:
        after=tcp_fn(PORT)
        sample["tcp_after"]=after
        second=ownership_status(after,proc.pid,
             expected_creation=first["identity"]["creation_date"])
        sample["ownership_after"]=second
    except Exception as exc:
        sample["tcp_error_type"]=type(exc).__name__
        sample["tcp_error_code"]="TCP_TABLE_RECHECK_FAILED"
        sample["decision"]="HOLD_TCP_TABLE_RECHECK_UNAVAILABLE"
        return sample
    if second["decision"]!="OWNED_LOOPBACK_LISTEN":
        sample["decision"]="HOLD_OWNERSHIP_CHANGED_AFTER_HTTP"
        return sample
    signature=lambda obs: sorted((r["local_address"],r["local_port"],r["state"],r["pid"])
                               for r in obs["listener_rows"])
    if signature(first) != signature(second):
        sample["decision"]="HOLD_LISTENER_SET_CHANGED_AFTER_HTTP"
        return sample
    sample["decision"]="READY_TCP_TABLE_PID_PATH_AND_EXACT_API_VERSION"
    return sample


def observe_readiness_with_trace(proc, dest: Path, *, max_samples: int = READINESS_MAX_SAMPLES,
                                   sleep_fn=None, tcp_fn=None, http_fn=None) -> dict:
    """Persist each decision as exclusive JSONL with fsync. No model operations."""
    if sleep_fn is None: sleep_fn=time.sleep
    trace=dest / "READINESS_ATTEMPTS.jsonl"
    with trace.open("x",encoding="utf-8",newline="\n") as fh:
        last=None
        for attempt in range(1,max_samples+1):
            sample=readiness_sample(proc,attempt,tcp_fn=tcp_fn,http_fn=http_fn)
            fh.write(json.dumps(sample,sort_keys=True,ensure_ascii=False)+"\n")
            fh.flush();os.fsync(fh.fileno())
            last=sample
            if sample["decision"]=="READY_TCP_TABLE_PID_PATH_AND_EXACT_API_VERSION":
                return {"ready":True,"samples":attempt,"last_decision":sample["decision"],
                        "identity_creation_date":sample["ownership_after"]["identity"]["creation_date"],
                        "trace_file":trace.name}
            if sample["decision"].startswith("HOLD_") or sample["decision"].startswith("FAIL_"):
                raise RuntimeError("READINESS_"+sample["decision"])
            if attempt<max_samples:
                sleep_fn(READINESS_SLEEP_SECONDS)
    raise RuntimeError("READINESS_TIMEOUT_"+(last["decision"] if last else "NO_SAMPLES"))

def api_json(url: str, body: dict | None = None, timeout: int = 4) -> dict:
    data = None if body is None else json.dumps(body, ensure_ascii=False).encode("utf-8")
    req = urllib.request.Request(url, data=data, headers={"Content-Type": "application/json"},
                                 method="POST" if data is not None else "GET")
    # Direct-only loopback transport; avoids inherited Windows/system proxy.
    require(url.startswith(API + "/"), "NON_LOCAL_API_CALL_DENIED")
    opener = urllib.request.build_opener(urllib.request.ProxyHandler({}))
    with opener.open(req, timeout=timeout) as resp:
        require(resp.status == 200, f"HTTP_STATUS_{resp.status}")
        raw = resp.read(1024 * 1024 + 1)
        require(len(raw) <= 1024 * 1024, "HTTP_RESPONSE_TOO_LONG")
        return json.loads(raw.decode("utf-8"))


def source_pins() -> dict:
    require(sys.platform == "win32" and sys.version_info[:2] == (3, 12), "PYTHON312_WINDOWS_REQUIRED")
    require(str(ROOT) == r"D:\WORK\RESEARCH\TokenToModel-Lab", "ROOT_UNEXPECTED")
    require(ROOT.is_dir() and (ROOT / ".git").exists(), "EXACT_REPO_ROOT_MISSING")
    require((ROOT / "_tmp").is_dir(), "PROJECT_TMP_MISSING")
    require(SOURCE_DIR.is_dir(), "SOURCE_GGUF_DIR_MISSING")
    for item in (ROOT, ROOT / "_tmp", SOURCE_DIR, GGUF, ORIGINAL, V5B, OUT, EXE):
        forbid_reparse(item)
    for p in (GGUF, ORIGINAL, V5B, EXE):
        require(p.is_file(), f"PINNED_INPUT_MISSING:{p.name}")
    require(GGUF.stat().st_size == GGUF_BYTES, "GGUF_SIZE_MISMATCH")
    pins = {
        "gguf":{"path":str(GGUF),"size":GGUF.stat().st_size,"sha256":sha256(GGUF)},
        "original_fail":{"path":str(ORIGINAL),"sha256":sha256(ORIGINAL)},
        "v5b_fail":{"path":str(V5B),"sha256":sha256(V5B)},
        "ollama_exe":{"path":str(EXE),"sha256":sha256(EXE)},
    }
    require(pins["gguf"]["sha256"] == GGUF_SHA, "GGUF_PIN_MISMATCH")
    require(pins["original_fail"]["sha256"] == ORIGINAL_SHA, "ORIGINAL_FAIL_PIN_MISMATCH")
    require(pins["v5b_fail"]["sha256"] == V5B_SHA, "V5B_FAIL_PIN_MISMATCH")
    version = subprocess.run([str(EXE), "--version"], capture_output=True,
                             text=True, encoding="utf-8", errors="replace", timeout=12)
    require(version.returncode == 0, "OLLAMA_CLI_VERSION_COMMAND_FAILED")
    actual = (version.stdout + " " + version.stderr).strip()
    require(bool(re.search(r"\b" + re.escape(VERSION) + r"\b", actual)), "OLLAMA_VERSION_UNEXPECTED:"+actual[:200])
    pins["ollama_exe"]["version"] = actual
    # Prevent any accidental interaction with an existing service on dedicated port.
    require(not tcp_table_observation(PORT)["rows"], "DEDICATED_PORT_ALREADY_HAS_TCP_ROWS")
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.settimeout(0.75)
        require(s.connect_ex(("127.0.0.1", PORT)) != 0, "DEDICATED_PORT_CONNECTABLE")
    with socket.socket(socket.AF_INET6, socket.SOCK_STREAM) as s6:
        s6.settimeout(0.75)
        require(s6.connect_ex(("::1", PORT)) != 0, "DEDICATED_IPV6_PORT_CONNECTABLE")
    require(not OUT.exists() and not OUT.is_symlink(), "ONE_SHOT_EVIDENCE_DIR_ALREADY_EXISTS_NO_RERUN")
    require(shutil.disk_usage(ROOT).free >= MIN_DISK_BYTES, "DISK_FREE_LT_1_GIB")
    return pins


def new_dir(p: Path) -> None:
    forbid_reparse(p)
    p.mkdir(exist_ok=False)
    forbid_reparse(p)


def write_json_x(path: Path, obj: dict) -> None:
    require(not path.exists(), f"EVIDENCE_ALREADY_EXISTS:{path.name}")
    with path.open("x", encoding="utf-8", newline="\n") as f:
        json.dump(obj, f, indent=2, ensure_ascii=False, sort_keys=True)
        f.write("\n")


def folder_snapshot(path: Path) -> dict:
    out = {}
    if not path.is_dir():
        return out
    for dirpath, dirs, files in os.walk(path, followlinks=False):
        base = Path(dirpath)
        forbid_reparse(base)
        for dn in dirs:
            forbid_reparse(base / dn)
        for fn in files:
            f = base / fn
            forbid_reparse(f)
            out[str(f.relative_to(path)).replace("\\", "/")] = {
                "size": f.stat().st_size,
                "sha256": sha256(f),
            }
            require(len(out) <= 1000, "LOCAL_MODEL_STORE_TOO_MANY_FILES")
    return out


def isolated_env(root: Path) -> dict:
    env = os.environ.copy()
    kv = {
        "OLLAMA_HOST": HOST,
        "OLLAMA_MODELS": str(root / "models"),
        "OLLAMA_TMPDIR": str(root / "tmp"),
        "OLLAMA_NO_CLOUD": "1",
        "OLLAMA_KEEP_ALIVE": "0",
        "OLLAMA_NUM_PARALLEL": "1",
        "OLLAMA_MAX_LOADED_MODELS": "1",
        "OLLAMA_MAX_QUEUE": "1",
        "OLLAMA_CONTEXT_LENGTH": str(CONTEXT),
        "TEMP": str(root / "tmp"),
        "TMP": str(root / "tmp"),
        "TMPDIR": str(root / "tmp"),
        "HOME": str(root / "home"),
        "USERPROFILE": str(root / "home"),
        "HOMEDRIVE": "D:",
        "HOMEPATH": str(root / "home")[2:],
        "LOCALAPPDATA": str(root / "home" / "LocalAppData"),
        "APPDATA": str(root / "home" / "AppData"),
        "XDG_CACHE_HOME": str(root / "home" / "cache"),
    }
    env.update(kv)
    return env


def stop_owned_server(proc: subprocess.Popen) -> dict:
    if proc.poll() is None:
        # Only this subprocess PID; /T also stops any subprocess runners it owns.
        killed = subprocess.run(["taskkill.exe", "/PID", str(proc.pid), "/T", "/F"],
                                capture_output=True, text=True, errors="replace", timeout=20)
        try:
            proc.wait(timeout=10)
        except subprocess.TimeoutExpired:
            return {"stop_status":"FAILED_PROCESS_STILL_RUNNING", "pid":proc.pid,
                    "taskkill_exit_code":killed.returncode}
        return {"stop_status":"STOPPED_OWNED_TREE", "pid":proc.pid,
                "taskkill_exit_code":killed.returncode}
    return {"stop_status":"SERVER_ALREADY_EXITED", "pid":proc.pid, "exit_code":proc.returncode}


def execute(pins: dict) -> dict:
    raise RuntimeError("V3_SOURCE_ONLY_EXECUTION_LOCK_NO_RUNTIME_PERMIT")
    # The one-shot directory is the immutable admission marker. No automatic re-run.
    new_dir(OUT)
    dirs = [OUT / "models", OUT / "tmp", OUT / "home", OUT / "home" / "LocalAppData",
            OUT / "home" / "AppData", OUT / "home" / "cache"]
    for p in dirs:
        new_dir(p)
    claim = {"schema":SCHEMA,"status":"ONE_SHOT_CLAIMED", "start_utc":now(),
             "model":MODEL,"host":HOST,"source_pins":pins,
             "no_science_train_or_test":True,"no_global_ollama_service_mutation":True}
    write_json_x(OUT / "CLAIM.json", claim)
    report: dict = {"schema": SCHEMA,"start_utc":now(),"status":"IN_PROGRESS",
                    "model":MODEL,"host":HOST,"source_before":pins,
                    "max_new_tokens":MAX_TOKENS,"num_ctx":CONTEXT,
                    "store":str(OUT / "models"),"stages":{}}
    proc = None
    stderr = OUT / "serve.log"
    log_handle = None
    try:
        env = isolated_env(OUT)
        for k in ("OLLAMA_HOST", "OLLAMA_MODELS", "OLLAMA_TMPDIR", "TEMP", "TMP", "HOME", "USERPROFILE", "APPDATA", "LOCALAPPDATA"):
            v = Path(env[k]) if k not in ("OLLAMA_HOST",) else None
            if v is not None:
                require(v.is_relative_to(ROOT) and v.is_relative_to(OUT), f"CHILD_ENV_OUT_OF_PROJECT:{k}")
                forbid_reparse(v)
        write_json_x(OUT / "PATH_DLL_RISK.json", path_dll_risk_snapshot(env))
        write_json_x(OUT / "ENV_SCOPE.json", {"host":HOST,"ollama_models":env["OLLAMA_MODELS"],
                                                "ollama_tmpdir":env["OLLAMA_TMPDIR"],
                                                "userprofile":env["USERPROFILE"],
                                                "appdata":env["APPDATA"],"localappdata":env["LOCALAPPDATA"],
                                                "homedrive":env["HOMEDRIVE"],"homepath":env["HOMEPATH"],
                                                "no_cloud":env["OLLAMA_NO_CLOUD"]})
        write_json_x(OUT / "MODELS_BEFORE.json", folder_snapshot(OUT / "models"))
        with (OUT / "Modelfile").open("x", encoding="utf-8", newline="\n") as f:
            f.write(f"FROM {GGUF}\nPARAMETER num_ctx {CONTEXT}\nPARAMETER num_predict {MAX_TOKENS}\n")
        require(sha256(GGUF)==GGUF_SHA, "GGUF_CHANGED_BEFORE_IMPORT")
        log_handle = stderr.open("x", encoding="utf-8", errors="replace")
        proc = subprocess.Popen([str(EXE), "serve"], cwd=str(OUT), env=env,
                                stdout=log_handle, stderr=subprocess.STDOUT,
                                creationflags=subprocess.CREATE_NEW_PROCESS_GROUP)
        report["server_pid"] = proc.pid
        report["stages"]["server_started"] = now()
        # Never swallow the sub-condition that caused the previous V1 HOLD.
        # Every readiness decision is flushed to a durable JSONL before proceeding.
        report["readiness"] = observe_readiness_with_trace(proc, OUT)
        report["stages"]["owned_server_ready"] = now()
        # Command is routed only to this host and fresh isolated store.
        created = subprocess.run([str(EXE), "create", MODEL, "-f", str(OUT / "Modelfile")],
                                 cwd=str(OUT), env=env, text=True,
                                 encoding="utf-8", errors="replace", capture_output=True, timeout=180)
        with (OUT / "create.stdout.log").open("x",encoding="utf-8") as f: f.write(created.stdout)
        with (OUT / "create.stderr.log").open("x",encoding="utf-8") as f: f.write(created.stderr)
        report["create_return_code"] = created.returncode
        report["stages"]["create_completed"] = now()
        require(created.returncode == 0, "OLLAMA_CREATE_FAILED_KEPT_LOGS")
        assert_owned_listener(proc, report["readiness"]["identity_creation_date"])
        model_snapshot = folder_snapshot(OUT / "models")
        write_json_x(OUT / "MODELS_AFTER_CREATE.json", model_snapshot)
        # At least one actual model manifest MUST be written under the project store.
        manifests = [p for p in model_snapshot if p.startswith("manifests/")]
        require(bool(manifests), "CREATE_WITHOUT_PROJECT_LOCAL_MANIFEST_HOLD_NO_GENERATE")
        manifest_json = api_json(API + "/api/tags", timeout=8)
        found = any(it.get("name","").lower() == MODEL.lower() for it in manifest_json.get("models",[]))
        require(found, "PROJECT_LOCAL_SERVER_MODEL_TAG_NOT_VISIBLE")
        report["stages"]["local_store_confirmed"] = now()
        response = api_json(API + "/api/generate", body={
            "model":MODEL,"prompt":PROMPT,"raw":True,"stream":False,
            "keep_alive":0,"options":{"num_ctx":CONTEXT,"num_predict":MAX_TOKENS,
                                      "temperature":0,"seed":20261108}
        }, timeout=180)
        write_json_x(OUT / "GENERATION_RAW_RESPONSE.json", response)
        assert_owned_listener(proc, report["readiness"]["identity_creation_date"])
        report["stages"]["generate_completed"] = now()
        ev = response.get("eval_count")
        require(response.get("done") is True and isinstance(ev,int) and 0 < ev <= MAX_TOKENS,
                "GENERATION_NOT_CONFIRMED_OR_EXCEEDED_32_TOKENS")
        require(response.get("model","").lower() == MODEL.lower(),"WRONG_RESPONSE_MODEL")
        report["evaluation"] = {"generated_tokens":ev,"done":True,
                                 "done_reason":response.get("done_reason"),
                                 "prompt_eval_count":response.get("prompt_eval_count"),
                                 "generated_text":response.get("response",""),
                                 "compatibility_only":True,"science_parity_not_retested":True}
        report["status"] = "PASS_COMPATIBILITY_ONLY_OLLAMA_IMPORT_AND_INFERENCE"
    except Exception as exc:
        report["status"] = "FAIL_OR_HOLD_COMPATIBILITY_ONLY_NO_RERUN"
        report["failure"] = {"type":type(exc).__name__,"message":str(exc),
                             "traceback":traceback.format_exc(limit=5)}
    finally:
        if proc is not None:
            try: report["shutdown"] = stop_owned_server(proc)
            except Exception as exc: report["shutdown"]={"stop_status":"STOP_FAILED", "error":str(exc)}
        if log_handle is not None:
            log_handle.close()
        if report.get("shutdown",{}).get("stop_status") not in ("STOPPED_OWNED_TREE", "SERVER_ALREADY_EXITED"):
            report["status"] = "HOLD_OWNED_SERVER_SHUTDOWN_UNVERIFIED"
        try:
            post_tcp = tcp_table_observation(PORT)
            report["shutdown_tcp_table"] = post_tcp
            if any(r.get("state") == "Listen" for r in post_tcp["rows"]):
                report["status"] = "HOLD_SERVER_STILL_ON_DEDICATED_PORT"
        except Exception as exc:
            report["shutdown_port_check_error"] = str(exc)
            report["status"] = "HOLD_SHUTDOWN_PORT_UNVERIFIED"
        try:
            report["source_after"] = {
                "gguf_sha256":sha256(GGUF),"original_fail_sha256":sha256(ORIGINAL),
                "v5b_fail_sha256":sha256(V5B),"ollama_exe_sha256":sha256(EXE)}
            if (report["source_after"]["gguf_sha256"] != pins["gguf"]["sha256"] or
                report["source_after"]["original_fail_sha256"] != pins["original_fail"]["sha256"] or
                report["source_after"]["v5b_fail_sha256"] != pins["v5b_fail"]["sha256"] or
                report["source_after"]["ollama_exe_sha256"] != pins["ollama_exe"]["sha256"]):
                report["status"]="HOLD_SOURCE_OR_EXECUTABLE_CHANGED"
        except Exception as exc:
            report["status"]="HOLD_POST_SHA_UNVERIFIED"
            report["source_post_error"] = str(exc)
        try:
            report["models_after_run"] = folder_snapshot(OUT / "models")
        except Exception as exc:
            report["status"] = "HOLD_LOCAL_STORE_POSTCHECK_FAILED"
            report["model_store_error"] = str(exc)
        report["finished_utc"] = now()
        report["frozen_parity"] = "FAIL_7_OF_8_PRESERVED"
        report["science_train_or_test_executed"] = False
        write_json_x(OUT / "RESULT.json", report)
    return report



def main() -> int:
    parser=argparse.ArgumentParser()
    parser.add_argument("--mode",choices=["contract"],required=True)
    parser.parse_args()
    print("TTM_T5_V3_SOURCE_ONLY=TRUE")
    print("TTM_T5_V3_EXECUTION_LOCK=ACTIVE_NO_RUNTIME_PERMIT")
    print("TTM_T5_V3_PORT=12645")
    print("TTM_T5_V3_GGUF_COMPATIBILITY=NOT_TESTED")
    return 0

if __name__ == "__main__":
    sys.exit(main())
