#!/usr/bin/env python3
"""TTM T5 minimal Ollama F32 compatibility one-shot V5 — Windows/Python 3.12, stdlib.

Never rerun with an existing CLAIM. Never touches the usual Ollama service.
All intended writes are confined to the TTM project-local evidence root.
"""
from __future__ import annotations

import argparse
import base64
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

import t5_native_tcp

ROOT = Path(r"D:\WORK\RESEARCH\TokenToModel-Lab")
SOURCE_DIR = ROOT / "_tmp" / "ttm_t5_trained_f32_v1"
GGUF = SOURCE_DIR / "TTM-Small4M-T4-step1024-F32.gguf"
ORIGINAL = SOURCE_DIR / "T5_TRAINED_LLAMA_CPP_PARITY.json"
V5B = SOURCE_DIR / "T5_LLAMA_UTF8_V5B_ROOTCAUSE_DIAGNOSTIC_V1.json"
OUT = ROOT / "_tmp" / "ttm_t5_ollama_compat_only_single_v5final"
EXE = Path(r"C:\Users\minht\AppData\Local\Programs\Ollama\ollama.exe")
GGUF_SHA = "5bdc904e6c51af04a4223219f36e6bc2e687f60fd6e17dc24508f3eb7489e4e5"
ORIGINAL_SHA = "c61f73216764b8582a5c996e85c59feb55b13496ec0117deb713d9b1843ec8e8"
V5B_SHA = "ac699d4e750037f88bbab776bb42a38079cd82b0a1c2f72385127ac5a36d9375"
GGUF_BYTES = 15061376
VERSION = "0.40.14"
PORT = 12648
HOST = f"127.0.0.1:{PORT}"
API = f"http://{HOST}"
MODEL = "ttm-t5-f32-compat-only-v5final:latest"
PROMPT = "Once upon a time, a small robot"
MAX_TOKENS = 32
CONTEXT = 256
MIN_DISK_BYTES = 1024 * 1024 * 1024
EXE_SHA = "14e0fff0449ce3c3a7fe9db8b8b32089274db5f835d4c99f5af7c32dcbf08981"
V1_OUT = ROOT / "_tmp" / "ttm_t5_ollama_compat_only_single_v1"
V2_OUT = ROOT / "_tmp" / "ttm_t5_ollama_compat_only_single_v2"
READINESS_MAX_SAMPLES = 40
READINESS_SLEEP_SECONDS = 0.5
SCHEMA = "ttm.t5.ollama.compatibility.project-local.one-shot.v5final"
RUNTIME_RELEASE_ENABLED = True
RC1_OUT = ROOT / "_tmp" / "ttm_t5_ollama_compat_only_single_v3rc1"
V4_OUT = ROOT / "_tmp" / "ttm_t5_ollama_compat_only_single_v4final"


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



# No netstat or NetTCPIP State field: the observed Windows kernel surface returns 0.
# Source-only successor; native IPv4 + IPv6 via bounded IP Helper snapshots.
IDENTITY_PS = r"""$ErrorActionPreference='Stop'
$pidToCheck=__PID__
$p=Get-CimInstance Win32_Process -Filter ("ProcessId = {0}" -f [uint32]$pidToCheck) -ErrorAction Stop
if ($null -eq $p) { throw 'PROCESS_IDENTITY_NOT_FOUND' }
[pscustomobject]@{pid=[int]$p.ProcessId;name=[string]$p.Name;executable_path=[string]$p.ExecutablePath;creation_date=[string]$p.CreationDate} | ConvertTo-Json -Compress -Depth 3
"""

def process_identity(pid: int) -> dict:
    """Only reads one exact PID via Win32_Process CIM, never TCP State."""
    if type(pid) is not int or not 1 <= pid <= 0xFFFFFFFF:
        raise RuntimeError('PID_INVALID')
    encoded=base64.b64encode(IDENTITY_PS.replace('__PID__',str(pid)).encode('utf-16le')).decode('ascii')
    p=subprocess.run([r'C:\Windows\System32\WindowsPowerShell\v1.0\powershell.exe',
                      '-NoProfile','-NonInteractive','-EncodedCommand',encoded],
                     capture_output=True,text=True,encoding='utf-8-sig',errors='replace',timeout=12)
    if p.returncode != 0 or len(p.stdout)>4096:
        raise RuntimeError('PROCESS_IDENTITY_QUERY_FAILED')
    try:
        obj=json.loads(p.stdout.strip())
    except (ValueError,TypeError) as exc:
        raise RuntimeError('PROCESS_IDENTITY_INVALID_JSON') from exc
    if not isinstance(obj,dict) or obj.get('pid')!=pid:
        raise RuntimeError('PROCESS_IDENTITY_MISMATCH')
    return obj

def tcp_table_observation(port: int, *, native_fn=None, identity_fn=None) -> dict:
    if type(port) is not int or port!=PORT:
        raise RuntimeError('ONLY_PINNED_V5FINAL_PORT_ALLOWED')
    raw=t5_native_tcp.capture(port,native_fn=native_fn)
    if raw.get('families_queried')!=['IPv4','IPv6']:
        raise RuntimeError('MISSING_TCP_FAMILY')
    rows=raw['rows']
    # Any matching port row must be accounted for. Never query a process for an
    # unknown PID unless exactly one PID is observed and there is a candidate.
    # Resolve only potential listener PIDs, never incidental completed TCP rows.
    # In Win11, a finished loopback HTTP exchange may appear as PID=0/state=11
    # (TIME_WAIT); that row does not own the listening socket.
    candidate_pids={r['pid'] for r in rows if r['state_code'] in (0,2)
                    and r['pid']>0 and r['remote_port']==0
                    and r['remote_address']==('0.0.0.0' if r['address_family']=='IPv4' else '::')}
    raw['processes']=[]
    if len(candidate_pids)==1:
        if identity_fn is None: identity_fn=process_identity
        raw['processes']=[identity_fn(next(iter(candidate_pids)))]
    return raw

def normalize_win_path(value: str) -> str:
    return ntpath.normcase(ntpath.normpath(value))

def ownership_status(snapshot: dict, expected_pid: int, *, expected_creation: str | None = None) -> dict:
    """Pure fail-closed classification. State 0 is UNKNOWN, NEVER 'Listen'.

    UNKNOWN may be an *ownership candidate* only with remote endpoint zero.
    It is not considered ready until independent HTTP 200/version plus both
    pre/post identity snapshots pass.
    """
    result={'decision':'HOLD_TCP_TABLE_MALFORMED','listener_candidates':[],
            'owner_pids':[], 'identity':None,'unknown_state_count':0,
            'confirmed_listen_count':0}
    if not isinstance(snapshot,dict) or snapshot.get('schema')!='ttm.t5.native.tcptable.dual.v1' or snapshot.get('port')!=PORT or snapshot.get('families_queried')!=['IPv4','IPv6']:
        return result
    rows=snapshot.get('rows');procs=snapshot.get('processes')
    if not isinstance(rows,list) or not isinstance(procs,list) or len(rows)>64 or len(procs)>1 or type(expected_pid) is not int or expected_pid<1:
        return result
    candidates=[]
    unique=set()
    for row in rows:
        if not isinstance(row,dict): return result
        af=row.get('address_family');la=row.get('local_address');ra=row.get('remote_address')
        state=row.get('state_code'); pid=row.get('pid');lp=row.get('local_port');rp=row.get('remote_port')
        if af not in ('IPv4','IPv6') or not isinstance(la,str) or not isinstance(ra,str) or type(state) is not int or type(pid) is not int or type(lp) is not int or type(rp) is not int or pid<0 or lp!=PORT or not 0<=rp<=65535:
            result['decision']='HOLD_TCP_ROW_MALFORMED';return result
        local_loopback='127.0.0.1' if af=='IPv4' else '::1'
        if la!=local_loopback:
            result['decision']='HOLD_NON_LOOPBACK_OR_WILDCARD';return result
        if state not in t5_native_tcp.VALID_STATES and state!=0:
            result['decision']='HOLD_INVALID_TCP_STATE_CODE';return result
        # Windows can retain TCP TIME_WAIT rows with PID=0 after the HTTP probe.
        # This is NOT a listener and NEVER confers ownership; only ignore a
        # strictly-shaped already-completed local TCP connection.
        if pid==0 and state==11 and ra==local_loopback and rp>0:
            continue
        if pid!=expected_pid:
            result['decision']='HOLD_UNTRUSTED_PID';return result
        if state in (0,2):
            # LISTEN or unknown-listener candidate must have a null remote endpoint.
            if ra!=('0.0.0.0' if af=='IPv4' else '::') or rp!=0:
                result['decision']='HOLD_STATE_ZERO_WITH_NONZERO_REMOTE' if state==0 else 'HOLD_LISTEN_WITH_REMOTE_ENDPOINT';return result
        if state in (0,2):
            key=(af,la,lp)
            if key in unique:
                result['decision']='HOLD_DUPLICATE_CANDIDATE';return result
            unique.add(key)
            candidates.append({'address_family':af,'local_address':la,'local_port':lp,
                               'pid':pid,'state_code':state,'state_semantics':'UNKNOWN' if state==0 else 'LISTEN_VERIFIED',
                               'remote_address':ra,'remote_port':rp})
    result['listener_candidates']=sorted(candidates,key=lambda x:(x['address_family'],x['local_address']))
    result['unknown_state_count']=sum(r['state_code']==0 for r in candidates)
    result['confirmed_listen_count']=sum(r['state_code']==2 for r in candidates)
    result['owner_pids']=sorted({r['pid'] for r in candidates})
    if not candidates:
        result['decision']='WAIT_NO_CANDIDATE_SOCKET';return result
    if len(procs)!=1 or not isinstance(procs[0],dict):
        result['decision']='HOLD_OWNER_IDENTITY_MISSING';return result
    proc=procs[0]
    if type(proc.get('pid')) is not int or proc.get('pid')!=expected_pid or not isinstance(proc.get('name'),str) or proc['name'].casefold()!='ollama.exe' or not isinstance(proc.get('executable_path'),str) or normalize_win_path(proc['executable_path'])!=normalize_win_path(str(EXE)):
        result['decision']='HOLD_OWNER_EXECUTABLE_MISMATCH';return result
    creation=proc.get('creation_date')
    if not isinstance(creation,str) or not creation.strip():
        result['decision']='HOLD_PROCESS_CREATION_MISSING';return result
    if expected_creation is not None and creation!=expected_creation:
        result['decision']='HOLD_PROCESS_REPLACED';return result
    result['identity']={'pid':expected_pid,'exe_path_match':True,'creation_date':creation}
    result['decision']='OWNED_LOOPBACK_CANDIDATE_ONLY'
    return result

def classify_shutdown_port_rows(rows: list, port: int) -> dict:
    """TIME_WAIT/0 is a kernel remnant, not proof the server is still running.

    Any remaining bound listener, foreign PID, malformed or non-loopback
    connection is a HOLD. This function cannot make readiness pass.
    """
    if type(port) is not int or port!=PORT or not isinstance(rows,list):
        return {'decision':'HOLD_INVALID_SHUTDOWN_SNAPSHOT','benign_timewait_count':0}
    benign=0
    for row in rows:
        if not isinstance(row,dict):return {'decision':'HOLD_INVALID_SHUTDOWN_ROW','benign_timewait_count':benign}
        af=row.get('address_family')
        local='127.0.0.1' if af=='IPv4' else '::1' if af=='IPv6' else None
        if (local is not None and row.get('local_address')==local and
            row.get('remote_address')==local and row.get('local_port')==port and
            type(row.get('remote_port')) is int and row['remote_port']>0 and
            type(row.get('pid')) is int and row['pid']==0 and
            type(row.get('state_code')) is int and row['state_code']==11):
            benign+=1
            continue
        return {'decision':'HOLD_UNSAFE_PORT_ROW_AFTER_SHUTDOWN','benign_timewait_count':benign}
    return {'decision':'PASS_NO_ACTIVE_SOCKET_AFTER_SHUTDOWN','benign_timewait_count':benign}


def assert_owned_listener(proc, expected_creation: str) -> dict:
    """Every pre-create and post-create check must include direct HTTP again."""
    sample=readiness_sample(proc,0,expected_creation=expected_creation)
    if not sample['decision'].startswith('READY_DUAL_ATTESTED_'):
        raise RuntimeError('OWNERSHIP_RECHECK_'+sample['decision'])
    return sample

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



def readiness_sample(proc, attempt: int, *, tcp_fn=None, http_fn=None, expected_creation=None) -> dict:
    """Two independent owner snapshots around HTTP; fail closed, no model call."""
    if tcp_fn is None: tcp_fn=tcp_table_observation
    if http_fn is None: http_fn=http_version_probe_direct
    sample={'attempt':attempt,'observed_utc':now(),'expected_pid':proc.pid,
            'process_exit_code':proc.poll(),'tcp_before':None,'tcp_after':None,
            'ownership_before':None,'ownership_after':None,
            'http':{'attempted':False,'http_status':None,'api_version':None,
                    'error_code':'SKIPPED_UNVERIFIED_OWNER','error_type':None},'decision':'PENDING'}
    if sample['process_exit_code'] is not None:
        sample['decision']='FAIL_SERVER_EXITED';return sample
    try:
        before=tcp_fn(PORT)
        sample['tcp_before']=before
        first=ownership_status(before,proc.pid,expected_creation=expected_creation)
        sample['ownership_before']=first
        if first['decision']!='OWNED_LOOPBACK_CANDIDATE_ONLY':
            sample['decision']=first['decision'];return sample
    except Exception as exc:
        sample['tcp_error_type']=type(exc).__name__
        sample['decision']='HOLD_NATIVE_TCP_OR_IDENTITY_UNAVAILABLE';return sample
    try:
        sample['http']=http_fn(API+'/api/version')
    except Exception as exc:
        sample['http']={'attempted':True,'http_status':None,'api_version':None,
                        'error_type':type(exc).__name__,'error_code':'HTTP_PROBE_EXCEPTION'}
        sample['decision']='WAIT_HTTP_EXCEPTION';return sample
    http=sample['http']
    if not isinstance(http,dict) or http.get('attempted') is not True:
        sample['decision']='HOLD_HTTP_PROBE_INVALID';return sample
    if http.get('http_status')!=200:
        sample['decision']='WAIT_HTTP_NO_200';return sample
    if http.get('error_code') is not None or http.get('api_version')!=VERSION:
        sample['decision']='WAIT_HTTP_INVALID_OR_WRONG_VERSION';return sample
    if proc.poll() is not None:
        sample['decision']='FAIL_SERVER_EXITED_AFTER_HTTP';return sample
    try:
        after=tcp_fn(PORT)
        sample['tcp_after']=after
        second=ownership_status(after,proc.pid,expected_creation=first['identity']['creation_date'])
        sample['ownership_after']=second
        if second['decision']!='OWNED_LOOPBACK_CANDIDATE_ONLY':
            sample['decision']='HOLD_OWNER_CHANGED_AFTER_HTTP';return sample
    except Exception as exc:
        sample['tcp_error_type']=type(exc).__name__
        sample['decision']='HOLD_NATIVE_RECHECK_UNAVAILABLE';return sample
    signature=lambda x:sorted((r['address_family'],r['local_address'],r['local_port'],r['pid'],
                               r['state_code'],r['remote_address'],r['remote_port']) for r in x['listener_candidates'])
    if signature(first)!=signature(second):
        sample['decision']='HOLD_CANDIDATE_CHANGED_AFTER_HTTP';return sample
    sample['attestation']={
        'owner_pid_path_creation':True,'port_loopback_only':True,
        'native_snapshot_before_after':True,'http_exact_version':True,
        'state_zero_was_not_claimed_listen':True,
        'native_listen_confirmed':first['unknown_state_count']==0,
        'compatibility_only':True}
    sample['decision']='READY_DUAL_ATTESTED_STATE_ZERO_UNKNOWN' if first['unknown_state_count'] else 'READY_DUAL_ATTESTED_VERIFIED_LISTEN'
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
            if sample["decision"].startswith("READY_DUAL_ATTESTED_"):
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
    require(pins["ollama_exe"]["sha256"] == EXE_SHA, "OLLAMA_EXE_SHA256_MISMATCH")
    for prior in (V1_OUT, V2_OUT, RC1_OUT, V4_OUT):
        forbid_reparse(prior)
        require((prior / "CLAIM.json").is_file() and (prior / "RESULT.json").is_file(), "PRIOR_ONESHOT_EVIDENCE_MISSING:"+prior.name)
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
    # Child-only environment hardening: omit the known research GGML DLL directory.
    # Never mutate os.environ, user PATH, or system PATH. Preserve a risk receipt.
    known = r"D:\WORK\RESEARCH\TokenToModel-Lab\_tmp\ttm_t2\build\bin\Release"
    inherited = [entry for entry in env.get("PATH", "").split(";") if entry.strip()]
    clean = [entry for entry in inherited if ntpath.normcase(ntpath.normpath(entry.strip().strip('"'))) != ntpath.normcase(known)]
    env["PATH"] = ";".join(clean)
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
    require(RUNTIME_RELEASE_ENABLED, "RUNTIME_RELEASE_DISABLED")
    # The one-shot directory is the immutable admission marker. No automatic re-run.
    new_dir(OUT)
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
        # After CLAIM, even an incomplete environment setup produces RESULT.json.
        dirs = [OUT / "models", OUT / "tmp", OUT / "home", OUT / "home" / "LocalAppData",
                OUT / "home" / "AppData", OUT / "home" / "cache"]
        for folder in dirs:
            new_dir(folder)
        env = isolated_env(OUT)
        for k in ("OLLAMA_HOST", "OLLAMA_MODELS", "OLLAMA_TMPDIR", "TEMP", "TMP", "HOME", "USERPROFILE", "APPDATA", "LOCALAPPDATA"):
            v = Path(env[k]) if k not in ("OLLAMA_HOST",) else None
            if v is not None:
                require(v.is_relative_to(ROOT) and v.is_relative_to(OUT), f"CHILD_ENV_OUT_OF_PROJECT:{k}")
                forbid_reparse(v)
        write_json_x(OUT / "PATH_DLL_RISK.json", {
            "parent":path_dll_risk_snapshot(os.environ),
            "child":path_dll_risk_snapshot(env),
            "path_mutated_globally":False,
            "path_filtered_only_in_child":True,
        })
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
        # Check owned listener immediately before writing model into the local store.
        assert_owned_listener(proc, report["readiness"]["identity_creation_date"])
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
            report["shutdown_port_adjudication"] = classify_shutdown_port_rows(post_tcp["rows"], PORT)
            if report["shutdown_port_adjudication"]["decision"] != "PASS_NO_ACTIVE_SOCKET_AFTER_SHUTDOWN":
                report["status"] = "HOLD_UNSAFE_PORT_ROW_AFTER_SHUTDOWN"
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
    parser=argparse.ArgumentParser(description="TTM T5 Ollama F32 V5 one-shot compatibility check")
    parser.add_argument('--mode',choices=['contract','preview','execute'],required=True)
    args=parser.parse_args()
    if args.mode == 'contract':
        print('T5_V5_RELEASE=ONE_SHOT_COMPATIBILITY_ONLY')
        print('T5_V5_PORT=12648')
        print('T5_V5_MAX_NEW_TOKENS=32')
        print('T5_V5_FULL_LOGITS=FAIL_7_OF_8_PRESERVED')
        return 0
    try:
        pins=source_pins()
    except Exception as exc:
        print('T5_V5_PRECLAIM=HOLD:'+type(exc).__name__+':'+str(exc),flush=True)
        return 3
    print('T5_V5_GGUF_SHA256='+pins['gguf']['sha256'],flush=True)
    print('T5_V5_OLLAMA_EXE_SHA256='+pins['ollama_exe']['sha256'],flush=True)
    print('T5_V5_OLLAMA_VERSION='+pins['ollama_exe']['version'],flush=True)
    print('T5_V5_DEDICATED_PORT=12648',flush=True)
    if args.mode == 'preview':
        print('T5_V5_PREVIEW=PASS_READONLY_NO_CLAIM',flush=True)
        return 0
    print('T5_V5_ONE_SHOT=CLAIM_AND_EXECUTE_EXACT_ONCE',flush=True)
    result=execute(pins)
    print('T5_V5_COMPAT_STATUS='+result['status'],flush=True)
    print('T5_V5_RESULT_PATH='+str(OUT / 'RESULT.json'),flush=True)
    print('T5_V5_NO_AUTOMATIC_RERUN=TRUE',flush=True)
    print('T5_V5_STRICT_LOGITS=FAIL_7_OF_8_PRESERVED',flush=True)
    return 0 if result['status']=='PASS_COMPATIBILITY_ONLY_OLLAMA_IMPORT_AND_INFERENCE' else 4

if __name__=='__main__':
    sys.exit(main())
