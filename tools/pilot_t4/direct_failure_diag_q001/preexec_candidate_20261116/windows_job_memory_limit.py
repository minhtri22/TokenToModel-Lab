"""Win32 job-wide committed-memory containment for the Q001 CPU launcher."""
from __future__ import annotations

import argparse
import ctypes
from ctypes import wintypes
import json
import msvcrt
import os
from pathlib import Path
import subprocess
import sys
import time

JOB_OBJECT_LIMIT_JOB_MEMORY = 0x00000200
JOB_OBJECT_LIMIT_KILL_ON_JOB_CLOSE = 0x00002000
JobObjectExtendedLimitInformation = 9
CREATE_SUSPENDED = 0x00000004
CREATE_NO_WINDOW = 0x08000000
STARTF_USESTDHANDLES = 0x00000100
WAIT_OBJECT_0 = 0x00000000
WAIT_TIMEOUT = 0x00000102
WAIT_FAILED = 0xFFFFFFFF
EXTENDED_STARTUPINFO_PRESENT = 0x00080000
PROC_THREAD_ATTRIBUTE_HANDLE_LIST = 0x00020002
PROC_THREAD_ATTRIBUTE_JOB_LIST = 0x0002000D
COMMIT_CAP = 12 * 1024**3
RESOURCE_EXIT = 86

class IO_COUNTERS(ctypes.Structure):
    _fields_ = [
        ("ReadOperationCount", ctypes.c_ulonglong),
        ("WriteOperationCount", ctypes.c_ulonglong),
        ("OtherOperationCount", ctypes.c_ulonglong),
        ("ReadTransferCount", ctypes.c_ulonglong),
        ("WriteTransferCount", ctypes.c_ulonglong),
        ("OtherTransferCount", ctypes.c_ulonglong),
    ]

class JOBOBJECT_BASIC_LIMIT_INFORMATION(ctypes.Structure):
    _fields_ = [
        ("PerProcessUserTimeLimit", ctypes.c_longlong),
        ("PerJobUserTimeLimit", ctypes.c_longlong),
        ("LimitFlags", wintypes.DWORD),
        ("MinimumWorkingSetSize", ctypes.c_size_t),
        ("MaximumWorkingSetSize", ctypes.c_size_t),
        ("ActiveProcessLimit", wintypes.DWORD),
        ("Affinity", ctypes.c_size_t),
        ("PriorityClass", wintypes.DWORD),
        ("SchedulingClass", wintypes.DWORD),
    ]

class JOBOBJECT_EXTENDED_LIMIT_INFORMATION(ctypes.Structure):
    _fields_ = [
        ("BasicLimitInformation", JOBOBJECT_BASIC_LIMIT_INFORMATION),
        ("IoInfo", IO_COUNTERS),
        ("ProcessMemoryLimit", ctypes.c_size_t),
        ("JobMemoryLimit", ctypes.c_size_t),
        ("PeakProcessMemoryUsed", ctypes.c_size_t),
        ("PeakJobMemoryUsed", ctypes.c_size_t),
    ]

class STARTUPINFOW(ctypes.Structure):
    _fields_ = [
        ("cb", wintypes.DWORD),
        ("lpReserved", wintypes.LPWSTR),
        ("lpDesktop", wintypes.LPWSTR),
        ("lpTitle", wintypes.LPWSTR),
        ("dwX", wintypes.DWORD),
        ("dwY", wintypes.DWORD),
        ("dwXSize", wintypes.DWORD),
        ("dwYSize", wintypes.DWORD),
        ("dwXCountChars", wintypes.DWORD),
        ("dwYCountChars", wintypes.DWORD),
        ("dwFillAttribute", wintypes.DWORD),
        ("dwFlags", wintypes.DWORD),
        ("wShowWindow", wintypes.WORD),
        ("cbReserved2", wintypes.WORD),
        ("lpReserved2", ctypes.POINTER(ctypes.c_ubyte)),
        ("hStdInput", wintypes.HANDLE),
        ("hStdOutput", wintypes.HANDLE),
        ("hStdError", wintypes.HANDLE),
    ]

class STARTUPINFOEXW(ctypes.Structure):
    _fields_ = [("StartupInfo", STARTUPINFOW), ("lpAttributeList", ctypes.c_void_p)]


class JOB_ACCOUNTING(ctypes.Structure):
    _fields_ = [
        ("TotalUserTime", ctypes.c_longlong),
        ("TotalKernelTime", ctypes.c_longlong),
        ("ThisPeriodTotalUserTime", ctypes.c_longlong),
        ("ThisPeriodTotalKernelTime", ctypes.c_longlong),
        ("TotalPageFaultCount", wintypes.DWORD),
        ("TotalProcesses", wintypes.DWORD),
        ("ActiveProcesses", wintypes.DWORD),
        ("TotalTerminatedProcesses", wintypes.DWORD),
    ]


class PROCESS_INFORMATION(ctypes.Structure):
    _fields_ = [
        ("hProcess", wintypes.HANDLE),
        ("hThread", wintypes.HANDLE),
        ("dwProcessId", wintypes.DWORD),
        ("dwThreadId", wintypes.DWORD),
    ]

def struct_sizes() -> dict[str, int]:
    """Pure layout metadata (not proof of Win32 native correctness)."""
    return {name: ctypes.sizeof(cls) for name, cls in [
        ("IO_COUNTERS", IO_COUNTERS),
        ("JOBOBJECT_BASIC_LIMIT_INFORMATION", JOBOBJECT_BASIC_LIMIT_INFORMATION),
        ("JOBOBJECT_EXTENDED_LIMIT_INFORMATION", JOBOBJECT_EXTENDED_LIMIT_INFORMATION),
        ("STARTUPINFOW", STARTUPINFOW),
        ("PROCESS_INFORMATION", PROCESS_INFORMATION),
        ("STARTUPINFOEXW", STARTUPINFOEXW),
        ("JOB_ACCOUNTING", JOB_ACCOUNTING),
    ]}

def _kernel():
    if sys.platform != "win32" or ctypes.sizeof(ctypes.c_void_p) != 8:
        raise RuntimeError("HOLD_WIN32_X64_REQUIRED")
    k32 = ctypes.WinDLL("kernel32", use_last_error=True)
    k32.CreateJobObjectW.argtypes = [ctypes.c_void_p, wintypes.LPCWSTR]
    k32.CreateJobObjectW.restype = wintypes.HANDLE
    k32.SetInformationJobObject.argtypes = [
        wintypes.HANDLE, wintypes.INT, ctypes.c_void_p, wintypes.DWORD
    ]
    k32.SetInformationJobObject.restype = wintypes.BOOL
    k32.QueryInformationJobObject.argtypes = [
        wintypes.HANDLE, wintypes.INT, ctypes.c_void_p, wintypes.DWORD,
        ctypes.POINTER(wintypes.DWORD)
    ]
    k32.QueryInformationJobObject.restype = wintypes.BOOL
    k32.CreateProcessW.argtypes = [
        wintypes.LPCWSTR, wintypes.LPWSTR, ctypes.c_void_p,
        ctypes.c_void_p, wintypes.BOOL, wintypes.DWORD, ctypes.c_void_p,
        wintypes.LPCWSTR, ctypes.POINTER(STARTUPINFOEXW),
        ctypes.POINTER(PROCESS_INFORMATION)
    ]
    k32.CreateProcessW.restype = wintypes.BOOL
    k32.IsProcessInJob.argtypes = [wintypes.HANDLE, wintypes.HANDLE,
                                  ctypes.POINTER(wintypes.BOOL)]
    k32.IsProcessInJob.restype = wintypes.BOOL
    k32.ResumeThread.argtypes = [wintypes.HANDLE]
    k32.ResumeThread.restype = wintypes.DWORD
    k32.InitializeProcThreadAttributeList.argtypes = [
        ctypes.c_void_p, wintypes.DWORD, wintypes.DWORD, ctypes.POINTER(ctypes.c_size_t)
    ]
    k32.InitializeProcThreadAttributeList.restype = wintypes.BOOL
    k32.UpdateProcThreadAttribute.argtypes = [
        ctypes.c_void_p, wintypes.DWORD, ctypes.c_size_t, ctypes.c_void_p,
        ctypes.c_size_t, ctypes.c_void_p, ctypes.c_void_p
    ]
    k32.UpdateProcThreadAttribute.restype = wintypes.BOOL
    k32.DeleteProcThreadAttributeList.argtypes = [ctypes.c_void_p]
    k32.DeleteProcThreadAttributeList.restype = None
    k32.WaitForSingleObject.argtypes = [wintypes.HANDLE, wintypes.DWORD]
    k32.WaitForSingleObject.restype = wintypes.DWORD
    k32.GetExitCodeProcess.argtypes = [wintypes.HANDLE, ctypes.POINTER(wintypes.DWORD)]
    k32.GetExitCodeProcess.restype = wintypes.BOOL
    k32.TerminateJobObject.argtypes = [wintypes.HANDLE, wintypes.UINT]
    k32.TerminateJobObject.restype = wintypes.BOOL
    k32.CloseHandle.argtypes = [wintypes.HANDLE]
    k32.CloseHandle.restype = wintypes.BOOL

    return k32


def require(ok, what: str) -> None:
    if not ok:
        raise OSError(ctypes.get_last_error(), "HOLD_WINJOB_" + what)


def query(k32, job, kind, structure):
    info = structure()
    require(k32.QueryInformationJobObject(job, kind, ctypes.byref(info),
                                            ctypes.sizeof(info), None), "QUERY")
    return info


def read_limits(k32, job, cap):
    info = query(k32, job, JobObjectExtendedLimitInformation,
                 JOBOBJECT_EXTENDED_LIMIT_INFORMATION)
    flags = JOB_OBJECT_LIMIT_JOB_MEMORY | JOB_OBJECT_LIMIT_KILL_ON_JOB_CLOSE
    if info.BasicLimitInformation.LimitFlags != flags or info.JobMemoryLimit != cap:
        raise RuntimeError("HOLD_WINJOB_LIMIT_READBACK_MISMATCH")
    return info


def require_current_job():
    read_limits(_kernel(), None, COMMIT_CAP)


def run_job_guarded(argv: list[str], *, cwd: str, max_job_commit_bytes: int,
                    timeout_seconds: int) -> tuple[int, int]:
    """Return the actual child exit code and peak job committed bytes."""
    if not argv or not os.path.isabs(argv[0]) or not 0 < timeout_seconds <= 900:
        raise ValueError("HOLD_JOB_GUARD_ARGS")
    if not 0 < max_job_commit_bytes <= COMMIT_CAP:
        raise ValueError("HOLD_JOB_COMMIT_LIMIT_RANGE")
    k32 = _kernel()

    job = k32.CreateJobObjectW(None, None)
    require(job, "CREATE")
    pi = PROCESS_INFORMATION()
    try:
        limit = JOBOBJECT_EXTENDED_LIMIT_INFORMATION()
        limit.BasicLimitInformation.LimitFlags = (
            JOB_OBJECT_LIMIT_JOB_MEMORY | JOB_OBJECT_LIMIT_KILL_ON_JOB_CLOSE
        )
        limit.JobMemoryLimit = max_job_commit_bytes
        require(k32.SetInformationJobObject(job, JobObjectExtendedLimitInformation,
            ctypes.byref(limit), ctypes.sizeof(limit)), "SET_COMMIT_LIMIT")
        read_limits(k32, job, max_job_commit_bytes)
        size = ctypes.c_size_t()
        k32.InitializeProcThreadAttributeList(None, 2, 0, ctypes.byref(size))
        require(size.value > 0 and ctypes.get_last_error() == 122, "ATTRIBUTE_SIZE")
        attributes = ctypes.create_string_buffer(size.value)
        require(k32.InitializeProcThreadAttributeList(attributes, 2, 0,
                ctypes.byref(size)), "ATTRIBUTES_INIT")
        try:
            # Duplicate only these descriptors. Never inherit the job handle.
            from contextlib import ExitStack
            with ExitStack() as stack:
                null_input = stack.enter_context(open(os.devnull, "rb"))
                handles = []
                for fd in (null_input.fileno(), sys.stdout.fileno(), sys.stderr.fileno()):
                    dupe = os.dup(fd)
                    stack.callback(os.close, dupe)
                    os.set_inheritable(dupe, True)
                    handles.append(msvcrt.get_osfhandle(dupe))
                allowed_handles = (wintypes.HANDLE * 3)(*handles)
                jobs = (wintypes.HANDLE * 1)(job)
                for attribute, values in (
                    (PROC_THREAD_ATTRIBUTE_HANDLE_LIST, allowed_handles),
                    (PROC_THREAD_ATTRIBUTE_JOB_LIST, jobs),
                ):
                    require(k32.UpdateProcThreadAttribute(attributes, 0, attribute,
                            values, ctypes.sizeof(values), None, None), "ATTRIBUTE_SET")
                si = STARTUPINFOEXW()
                si.StartupInfo.cb = ctypes.sizeof(si)
                si.StartupInfo.dwFlags = STARTF_USESTDHANDLES
                si.StartupInfo.hStdInput, si.StartupInfo.hStdOutput, si.StartupInfo.hStdError = handles
                si.lpAttributeList = ctypes.addressof(attributes)
                cmd = ctypes.create_unicode_buffer(subprocess.list2cmdline(argv))
                # Atomic job assignment closes the gap if the supervisor dies
                # during process creation. The primary thread still starts suspended.
                require(k32.CreateProcessW(argv[0], cmd, None, None, True,
                    CREATE_SUSPENDED | CREATE_NO_WINDOW | EXTENDED_STARTUPINFO_PRESENT,
                    None, cwd, ctypes.byref(si), ctypes.byref(pi)), "CREATE_ASSIGNED_SUSPENDED")
        finally:
            k32.DeleteProcThreadAttributeList(attributes)
        member = wintypes.BOOL()
        require(k32.IsProcessInJob(pi.hProcess, job, ctypes.byref(member))
                and member.value, "MEMBERSHIP_BEFORE_RESUME")
        if k32.ResumeThread(pi.hThread) != 1:
            raise OSError(ctypes.get_last_error(), "HOLD_WINJOB_RESUME")
        waited = k32.WaitForSingleObject(pi.hProcess, timeout_seconds * 1000)
        if waited == WAIT_TIMEOUT:
            raise TimeoutError("HOLD_WINJOB_WALL_TIME")
        if waited != WAIT_OBJECT_0:
            raise OSError(ctypes.get_last_error(), "HOLD_WINJOB_WAIT")
        code = wintypes.DWORD()
        require(k32.GetExitCodeProcess(pi.hProcess, ctypes.byref(code)), "EXIT_CODE")
        info = read_limits(k32, job, max_job_commit_bytes)
        # The process wait can signal just before job accounting is updated.
        # Allow time for the exited root to be removed from the active count.
        settled = time.monotonic() + 0.25
        while query(k32, job, 1, JOB_ACCOUNTING).ActiveProcesses:
            if time.monotonic() >= settled:
                raise RuntimeError("HOLD_WINJOB_DESCENDANT_ACTIVE_AFTER_PARENT_EXIT")
            time.sleep(0.01)
        return int(code.value), int(info.PeakJobMemoryUsed)
    finally:
        if pi.hProcess:
            # Last close also kills the job if the supervisor itself is stopped.
            k32.TerminateJobObject(job, RESOURCE_EXIT)
            k32.CloseHandle(pi.hThread)
            k32.CloseHandle(pi.hProcess)
        k32.CloseHandle(job)


def main() -> int:
    p = argparse.ArgumentParser()
    mode = p.add_mutually_exclusive_group(required=True)
    mode.add_argument("--struct-shape", action="store_true")
    mode.add_argument("--native-smoke", action="store_true")
    mode.add_argument("--guard-run", nargs=argparse.REMAINDER)
    a = p.parse_args()
    if a.struct_shape:
        print(json.dumps(struct_sizes(), sort_keys=True))
        return 0
    if a.native_smoke:
        argv = [sys.executable, "-c", "print('WINJOB_NO_MODEL_SMOKE')"]
        cap, timeout = 256 * 1024**2, 10
    else:
        runner = Path(__file__).resolve().with_name("ttm_sm4m_diag_q001.py")
        argv = [sys.executable, "-I", "-B", str(runner), "run", *a.guard_run]
        cap, timeout = COMMIT_CAP, 900
    try:
        code, peak = run_job_guarded(argv, cwd=os.getcwd(),
                                     max_job_commit_bytes=cap, timeout_seconds=timeout)
    except (OSError, ValueError, RuntimeError) as exc:
        print(json.dumps({"status": "HOLD_RESOURCE_INCOMPLETE", "reason": str(exc),
                          "job_commit_limit_bytes": cap}), file=sys.stderr, flush=True)
        return RESOURCE_EXIT
    print(json.dumps({"child_exit_code": code, "job_commit_limit_bytes": cap,
                      "peak_job_commit_bytes": peak}), flush=True)
    # The peak counter can reflect a rejected commit charge. Treat a peak over
    # the hard limit conservatively even if the child retried internally.
    if peak > cap:
        print(json.dumps({"status": "HOLD_RESOURCE_INCOMPLETE",
                          "reason": "JOB_PEAK_COMMIT_CHARGE_EXCEEDED_LIMIT",
                          "child_exit_code": code}), file=sys.stderr, flush=True)
        return RESOURCE_EXIT
    # A native crash or explicit allocation failure is incomplete execution.
    if code not in (0, 2):
        print(json.dumps({"status": "HOLD_RESOURCE_INCOMPLETE",
                          "reason": "GUARDED_CHILD_ABNORMAL_EXIT",
                          "child_exit_code": code}), file=sys.stderr, flush=True)
        return RESOURCE_EXIT
    return code


if __name__ == "__main__":
    raise SystemExit(main())
