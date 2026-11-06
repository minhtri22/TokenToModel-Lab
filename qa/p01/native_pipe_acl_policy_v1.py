"""TTM P01 L1 — reviewable Win32 pipe security policy (SOURCE ONLY).

This module creates a *proposed* protected SDDL. It does not install a service,
create a pipe, set ACLs, launch workers, or qualify W01-W12.

Important: this policy must be applied as SECURITY_ATTRIBUTES when
CreateNamedPipeW creates the pipe; validating the string in Python is not
equivalent to a native DACL readback or client identity attestation.
"""
from __future__ import annotations
import re

# Client permissions: SYNCHRONIZE | READ_CONTROL | READ_DATA | WRITE_DATA |
# READ_EA | WRITE_EA | READ_ATTRIBUTES | WRITE_ATTRIBUTES.
# Explicitly exclude FILE_CREATE_PIPE_INSTANCE (0x4).
CLIENT_ACCESS_MASK = 0x0012019B
FILE_CREATE_PIPE_INSTANCE = 0x0004
SERVICE_SID_PREFIX = "S-1-5-80-"
SID_PATTERN = re.compile(r"^S-1-(?:[0-9]{1,10}-)+[0-9]{1,10}$", re.ASCII)

class PipePolicyRefusal(PermissionError):
    pass

def validate_sid(sid: object, *, service: bool = False) -> str:
    if type(sid) is not str or len(sid) > 184 or not SID_PATTERN.fullmatch(sid):
        raise PipePolicyRefusal("INVALID_SID")
    if service and not sid.startswith(SERVICE_SID_PREFIX):
        raise PipePolicyRefusal("SERVICE_SID_REQUIRED")
    return sid

def propose_pipe_sddl(*, service_sid: str, worker_sid: str) -> str:
    service_sid = validate_sid(service_sid, service=True)
    worker_sid = validate_sid(worker_sid)
    if service_sid == worker_sid or worker_sid in (
        "S-1-1-0", "S-1-5-7", "S-1-5-11", "S-1-5-32-545",
        "S-1-5-18", "S-1-5-32-544"
    ):
        raise PipePolicyRefusal("DISTINCT_NONBUILTIN_WORKER_SID_REQUIRED")
    if CLIENT_ACCESS_MASK & FILE_CREATE_PIPE_INSTANCE:
        raise PipePolicyRefusal("CLIENT_PIPE_INSTANCE_CREATE_PERMISSION_FORBIDDEN")
    return ("D:P"
            "(A;;GA;;;SY)"
            "(A;;GA;;;BA)"
            "(A;;GA;;;" + service_sid + ")"
            "(A;;0x%08x;;;" % CLIENT_ACCESS_MASK + worker_sid + ")")

def forbid_default_pipe_acl(*, security_attributes_explicit: bool,
                            native_dacl_readback: bool,
                            client_sid_attested: bool) -> None:
    if not security_attributes_explicit:
        raise PipePolicyRefusal("DEFAULT_PIPE_DACL_BLOCKED")
    if not native_dacl_readback:
        raise PipePolicyRefusal("NATIVE_DACL_READBACK_REQUIRED")
    if not client_sid_attested:
        raise PipePolicyRefusal("CLIENT_TOKEN_SID_ATTESTATION_REQUIRED")
