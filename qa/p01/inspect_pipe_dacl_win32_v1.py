"""Native Windows read-only pipe security-descriptor inspector.

GetFileSecurityW reads existing pipe object security by name. No CreateFileW,
no pipe connection, no service creation, no worker launch, no ACL mutation.
Returns a redacted PASS/BLOCK receipt. This cannot attest the peer SID/job or
replace W01-W12.
"""
from __future__ import annotations
import argparse
import ctypes
from ctypes import wintypes
import hashlib
import json
import os
import re
import sys

DACL_SECURITY_INFORMATION = 0x4
SDDL_REVISION_1 = 1
ERROR_INSUFFICIENT_BUFFER = 122
FORBIDDEN = {"WD", "AU", "AN", "BU", "S-1-1-0", "S-1-5-11", "S-1-5-7", "S-1-5-32-545"}
SERVICE = re.compile(r"^S-1-5-80-(?:[0-9]{1,10}-){4}[0-9]{1,10}$")
SID = re.compile(r"^S-1-(?:[0-9]{1,10}-)+[0-9]{1,10}$")

def inspect(*, pipe_name, service_sid, worker_sid):
    if os.name != "nt":
        return {"verdict": "BLOCK", "reason": "WINDOWS_REQUIRED"}
    if type(pipe_name) is not str or not pipe_name.startswith("\\\\.\\pipe\\TTM_P01_L1_") or len(pipe_name)>200:
        return {"verdict": "BLOCK", "reason": "INVALID_PINNED_PIPE_NAME"}
    if not SERVICE.fullmatch(service_sid) or not SID.fullmatch(worker_sid) or worker_sid == service_sid:
        return {"verdict": "BLOCK", "reason": "INVALID_SID_BINDING"}
    a=ctypes.WinDLL("advapi32",use_last_error=True)
    k=ctypes.WinDLL("kernel32",use_last_error=True)
    get=a.GetFileSecurityW
    get.argtypes=[wintypes.LPCWSTR,wintypes.DWORD,ctypes.c_void_p,wintypes.DWORD,ctypes.POINTER(wintypes.DWORD)]
    get.restype=wintypes.BOOL
    convert=a.ConvertSecurityDescriptorToStringSecurityDescriptorW
    convert.argtypes=[ctypes.c_void_p,wintypes.DWORD,wintypes.DWORD,ctypes.POINTER(wintypes.LPWSTR),ctypes.POINTER(wintypes.DWORD)]
    convert.restype=wintypes.BOOL
    local_free=k.LocalFree
    local_free.argtypes=[ctypes.c_void_p]
    local_free.restype=ctypes.c_void_p
    size=wintypes.DWORD(0)
    ok=get(pipe_name,DACL_SECURITY_INFORMATION,None,0,ctypes.byref(size))
    err=ctypes.get_last_error()
    if ok or err != ERROR_INSUFFICIENT_BUFFER or size.value < 20 or size.value > 65536:
        return {"verdict":"BLOCK","reason":"PIPE_GETFILESECURITY_QUERY_FAILED","winerror":err}
    sd=ctypes.create_string_buffer(size.value)
    if not get(pipe_name,DACL_SECURITY_INFORMATION,sd,size,ctypes.byref(size)):
        return {"verdict":"BLOCK","reason":"PIPE_DACL_READBACK_FAILED","winerror":ctypes.get_last_error()}
    out=wintypes.LPWSTR()
    n=wintypes.DWORD()
    if not convert(sd,SDDL_REVISION_1,DACL_SECURITY_INFORMATION,ctypes.byref(out),ctypes.byref(n)):
        return {"verdict":"BLOCK","reason":"PIPE_SDDL_CONVERSION_FAILED","winerror":ctypes.get_last_error()}
    try:
        sddl=out.value or ""
    finally:
        local_free(ctypes.cast(out,ctypes.c_void_p))
    aces=[a.split(";") for a in re.findall(r"\\(([^()]*)\\)",sddl)]
    allow=[parts for parts in aces if len(parts)>=6 and parts[0]=="A"]
    bad=[parts[5] for parts in allow if parts[5] in FORBIDDEN]
    sidset={parts[5] for parts in allow}
    # Readback is necessary, but can never alone attest effective OS access.
    good = (sddl.startswith("D:P") and not bad and service_sid in sidset and worker_sid in sidset)
    return {"verdict":"PASS_DACL_READBACK_ONLY" if good else "BLOCK",
            "reason":"DACL_REQUIRED_ENTRIES" if good else "DACL_MISSING_OR_OVERBROAD",
            "sddl_sha256":hashlib.sha256(sddl.encode("utf-8")).hexdigest(),
            "ace_count":len(aces),"forbidden_allow_ace_count":len(bad),
            "service_sid_ace":service_sid in sidset,"worker_sid_ace":worker_sid in sidset,
            "client_process_sid_attested":False,"job_membership_attested":False}

def main():
    p=argparse.ArgumentParser()
    p.add_argument("--pipe",required=True)
    p.add_argument("--service-sid",required=True)
    p.add_argument("--worker-sid",required=True)
    args=p.parse_args()
    try:r=inspect(pipe_name=args.pipe,service_sid=args.service_sid,worker_sid=args.worker_sid)
    except Exception as exc:r={"verdict":"BLOCK","reason":"NATIVE_PROBE_EXCEPTION","exception_type":type(exc).__name__}
    print(json.dumps(r,sort_keys=True))
    return 0 if r["verdict"]=="PASS_DACL_READBACK_ONLY" else 3

if __name__=="__main__":
    raise SystemExit(main())
