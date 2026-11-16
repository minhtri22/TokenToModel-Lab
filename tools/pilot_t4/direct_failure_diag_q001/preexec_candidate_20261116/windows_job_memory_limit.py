"""Windows 11 Job Object *commit* memory limit, source-only I1 candidate.

NO I2 DISPATCH HERE. Must be independently tested on Windows Python 3.12.
Purpose: launch a child in CREATE_SUSPENDED state; set a job-wide OS committed
memory ceiling; assign it BEFORE ResumeThread; ensure KILL_ON_JOB_CLOSE.
The job-wide *committed* memory is NOT resident RSS. Retain existing 12-GiB
sampled process-tree RSS monitor and never claim that one equals the other.

This is a proposed I2 hard-commit guard. Native Win32 testing and distinct
adjudication are required before the guarded launcher is eligible for I1 PASS.
"""
from __future__ import annotations

import argparse
import ctypes
from ctypes import wintypes
import subprocess
import sys

JOB_OBJECT_LIMIT_JOB_MEMORY = 0x00000200
JOB_OBJECT_LIMIT_KILL_ON_JOB_CLOSE = 0x00002000
JobObjectExtendedLimitInformation = 9
CREATE_SUSPENDED = 0x00000004
CREATE_NO_WINDOW = 0x08000000
STARTF_USESTDHANDLES = 0x00000100
WAIT_OBJECT_0 = 0x00000000
WAIT_TIMEOUT = 0x00000102
WAIT_FAILED = 0xFFFFFFFF
STILL_ACTIVE = 259

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

# JobObjectBasicAccountingInformation = 1. A terminated parent must not
# mask a still-running descendant; KILL_ON_JOB_CLOSE is only cleanup, not PASS.
JobObjectBasicAccountingInformation = 1
JobObjectBasicProcessIdList = 3
MAX_JOB_PIDS_FOR_QA = 4096

class JOBOBJECT_BASIC_PROCESS_ID_LIST(ctypes.Structure):
    _fields_ = [
        ("NumberOfAssignedProcesses", wintypes.DWORD),
        ("NumberOfProcessIdsInList", wintypes.DWORD),
        ("ProcessIdList", ctypes.c_size_t * MAX_JOB_PIDS_FOR_QA),
    ]

class JOBOBJECT_BASIC_ACCOUNTING_INFORMATION(ctypes.Structure):
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
        ("JOBOBJECT_BASIC_ACCOUNTING_INFORMATION", JOBOBJECT_BASIC_ACCOUNTING_INFORMATION),
        ("JOBOBJECT_BASIC_PROCESS_ID_LIST", JOBOBJECT_BASIC_PROCESS_ID_LIST),
        ("STARTUPINFOW", STARTUPINFOW),
        ("PROCESS_INFORMATION", PROCESS_INFORMATION),
    ]}

def run_job_guarded(
    argv: list[str], *, cwd: str, max_job_commit_bytes: int,
    timeout_seconds: int
) -> tuple[int, int]:
    """Run child+descendants with OS committed-memory ceiling from birth.

    Returns (child exit code, peak job committed bytes). Fail-closed on any
    setup or query error. Does not attest absolute RSS or external rights.
    """
    if sys.platform != "win32" or ctypes.sizeof(ctypes.c_void_p) != 8:
        raise RuntimeError("HOLD_WIN32_X64_REQUIRED")
    if not argv or max_job_commit_bytes <= 0 or not 0 < timeout_seconds <= 900:
        raise ValueError("HOLD_JOB_GUARD_ARGS")
    if max_job_commit_bytes > 12 * (1024**3):
        raise ValueError("HOLD_JOB_COMMIT_LIMIT_EXCEEDS_12GIB")
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
        wintypes.LPCWSTR, ctypes.POINTER(STARTUPINFOW),
        ctypes.POINTER(PROCESS_INFORMATION)
    ]
    k32.CreateProcessW.restype = wintypes.BOOL
    k32.AssignProcessToJobObject.argtypes = [wintypes.HANDLE, wintypes.HANDLE]
    k32.AssignProcessToJobObject.restype = wintypes.BOOL
    k32.ResumeThread.argtypes = [wintypes.HANDLE]
    k32.ResumeThread.restype = wintypes.DWORD
    k32.GetStdHandle.argtypes = [wintypes.DWORD]
    k32.GetStdHandle.restype = wintypes.HANDLE
    k32.WaitForSingleObject.argtypes = [wintypes.HANDLE, wintypes.DWORD]
    k32.WaitForSingleObject.restype = wintypes.DWORD
    k32.GetExitCodeProcess.argtypes = [wintypes.HANDLE, ctypes.POINTER(wintypes.DWORD)]
    k32.GetExitCodeProcess.restype = wintypes.BOOL
    k32.TerminateJobObject.argtypes = [wintypes.HANDLE, wintypes.UINT]
    k32.TerminateJobObject.restype = wintypes.BOOL
    k32.CloseHandle.argtypes = [wintypes.HANDLE]
    k32.CloseHandle.restype = wintypes.BOOL

    def require(ok, what: str) -> None:
        if not ok:
            raise OSError(ctypes.get_last_error(), "HOLD_WINJOB_" + what)

    job = k32.CreateJobObjectW(None, None)
    require(job, "CREATE")
    pi = PROCESS_INFORMATION()
    created = False
    assigned = False
    try:
        limit = JOBOBJECT_EXTENDED_LIMIT_INFORMATION()
        limit.BasicLimitInformation.LimitFlags = (
            JOB_OBJECT_LIMIT_JOB_MEMORY | JOB_OBJECT_LIMIT_KILL_ON_JOB_CLOSE
        )
        limit.JobMemoryLimit = max_job_commit_bytes
        require(k32.SetInformationJobObject(job, JobObjectExtendedLimitInformation,
            ctypes.byref(limit), ctypes.sizeof(limit)), "SET_COMMIT_LIMIT")
        si = STARTUPINFOW()
        si.cb = ctypes.sizeof(si)
        si.dwFlags = STARTF_USESTDHANDLES
        # 0xFFFFFFF6=STD_INPUT, F5=STD_OUTPUT, F4=STD_ERROR.
        si.hStdInput = k32.GetStdHandle(0xFFFFFFF6)
        si.hStdOutput = k32.GetStdHandle(0xFFFFFFF5)
        si.hStdError = k32.GetStdHandle(0xFFFFFFF4)
        if not si.hStdOutput or not si.hStdError or \
                int(si.hStdOutput) == ctypes.c_void_p(-1).value or \
                int(si.hStdError) == ctypes.c_void_p(-1).value:
            raise RuntimeError("HOLD_WINJOB_STD_HANDLES_UNAVAILABLE")
        cmd = ctypes.create_unicode_buffer(subprocess.list2cmdline(argv))
        require(k32.CreateProcessW(
            argv[0], cmd, None, None, True,
            CREATE_SUSPENDED | CREATE_NO_WINDOW, None, cwd,
            ctypes.byref(si), ctypes.byref(pi)), "CREATE_SUSPENDED")
        created = True
        require(k32.AssignProcessToJobObject(job, pi.hProcess),
                "ASSIGN_BEFORE_RESUME")
        assigned = True
        if k32.ResumeThread(pi.hThread) == WAIT_FAILED:
            raise OSError(ctypes.get_last_error(), "HOLD_WINJOB_RESUME")
        waited = k32.WaitForSingleObject(pi.hProcess, timeout_seconds * 1000)
        if waited == WAIT_TIMEOUT:
            raise TimeoutError("HOLD_WINJOB_WALL_TIME")
        if waited != WAIT_OBJECT_0:
            raise OSError(ctypes.get_last_error(), "HOLD_WINJOB_WAIT")
        code = wintypes.DWORD()
        require(k32.GetExitCodeProcess(pi.hProcess, ctypes.byref(code)),
                "EXIT_CODE")
        if code.value == STILL_ACTIVE:
            raise RuntimeError("HOLD_WINJOB_EXIT_STATUS_STILL_ACTIVE")
        info = JOBOBJECT_EXTENDED_LIMIT_INFORMATION()
        require(k32.QueryInformationJobObject(
            job, JobObjectExtendedLimitInformation, ctypes.byref(info),
            ctypes.sizeof(info), None), "QUERY_LIMITS")
        if info.BasicLimitInformation.LimitFlags & JOB_OBJECT_LIMIT_JOB_MEMORY == 0:
            raise RuntimeError("HOLD_WINJOB_LIMIT_NOT_ACTIVE")
        if int(info.JobMemoryLimit) != max_job_commit_bytes:
            raise RuntimeError("HOLD_WINJOB_LIMIT_VALUE_MISMATCH")
        # If a tracked descendant survives its parent, return HOLD rather than
        # wrongly reporting success. The finally block will kill the full job.
        accounting = JOBOBJECT_BASIC_ACCOUNTING_INFORMATION()
        require(k32.QueryInformationJobObject(
            job, JobObjectBasicAccountingInformation, ctypes.byref(accounting),
            ctypes.sizeof(accounting), None), "QUERY_ACCOUNTING")
        # Windows accounting may transiently include the already-signaled
        # root process. Enumerate actual job PIDs, exclude that exact root PID
        # ONLY after WaitForSingleObject and GetExitCodeProcess succeeded.
        # Remaining PIDs mean live descendants; a happy child alone is PASS.
        pid_list = JOBOBJECT_BASIC_PROCESS_ID_LIST()
        require(k32.QueryInformationJobObject(
            job, JobObjectBasicProcessIdList, ctypes.byref(pid_list),
            ctypes.sizeof(pid_list), None), "QUERY_ACTIVE_PID_LIST")
        listed = int(pid_list.NumberOfProcessIdsInList)
        if listed > MAX_JOB_PIDS_FOR_QA or listed < 0:
            raise RuntimeError("HOLD_WINJOB_PID_LIST_OVERFLOW")
        remaining = {
            int(pid_list.ProcessIdList[i]) for i in range(listed)
        } - {int(pi.dwProcessId)}
        if remaining:
            raise RuntimeError("HOLD_WINJOB_LIVE_DESCENDANTS_AFTER_PARENT_EXIT")
        return int(code.value), int(info.PeakJobMemoryUsed)
    finally:
        # KILL_ON_JOB_CLOSE guarantees fail-closed descendant cleanup.
        if assigned:
            k32.TerminateJobObject(job, 1)
        if created:
            k32.CloseHandle(pi.hThread)
            k32.CloseHandle(pi.hProcess)
        k32.CloseHandle(job)

def main(argv: list[str] | None = None) -> int:
    """One executable may be used in 3 non-science modes.

    --guard is the *only* supported path for production I2 and must be
    launched by the pinned PowerShell launcher. Native QA modes run dummy
    Python subprocesses and NEVER inspect a private checkpoint/tokenizer.
    """
    import json
    from pathlib import Path
    p = argparse.ArgumentParser()
    modes = p.add_mutually_exclusive_group(required=True)
    modes.add_argument("--struct-shape", action="store_true")
    modes.add_argument("--native-smoke", action="store_true")
    modes.add_argument("--native-negative", action="store_true")
    modes.add_argument("--guard", action="store_true")
    p.add_argument("--cwd", default=".")
    p.add_argument("--max-job-commit-bytes", type=int, default=12 * (1024**3))
    p.add_argument("--wall-seconds", type=int, default=900)
    p.add_argument("command", nargs=argparse.REMAINDER)
    a = p.parse_args(argv)
    if a.struct_shape:
        print(json.dumps(struct_sizes(), sort_keys=True))
        return 0
    if a.native_smoke:
        code, peak = run_job_guarded(
            [sys.executable, "-c", "print('WINJOB_NO_MODEL_SMOKE')"],
            cwd=".", max_job_commit_bytes=256 * (1024**2),
            timeout_seconds=10
        )
        print(json.dumps({"mode":"NO_MODEL_SMOKE", "exit":code,
             "peak_job_commit_bytes":peak,"model_execution":False,
             "rss_hard_cap_proven":False}, sort_keys=True))
        return 0 if code == 0 else 2
    if a.native_negative:
        # Require *all* three cases: timeout, hard-commit pressure and an
        # orphan descendant. These are not substitute for independent QA.
        checks = {}
        def negative(name: str, command: list[str], cap: int, seconds: int):
            try:
                code, peak = run_job_guarded(command, cwd=".",
                    max_job_commit_bytes=cap, timeout_seconds=seconds)
                checks[name] = {"rejected":code != 0, "code":code,
                                "peak_job_commit_bytes":peak}
            except (TimeoutError, RuntimeError, OSError) as exc:
                checks[name] = {"rejected":True, "reason":str(exc)}
        negative("hard_commit_pressure", [sys.executable, "-c",
                "x=bytearray(512*1024*1024); print(len(x))"],
                128 * (1024**2), 10)
        negative("wall_timeout", [sys.executable, "-c",
                "import time; time.sleep(5)"], 256 * (1024**2), 1)
        negative("orphan_descendant", [sys.executable, "-c",
                "import subprocess,sys; subprocess.Popen([sys.executable,'-c','import time;time.sleep(5)'])"],
                256 * (1024**2), 3)
        ok = len(checks) == 3 and all(v["rejected"] for v in checks.values())
        print(json.dumps({"mode":"NATIVE_NEGATIVE_NO_MODEL","pass":ok,
             "checks":checks,"model_execution":False}, sort_keys=True))
        return 0 if ok else 2
    command = a.command[1:] if a.command and a.command[0] == "--" else a.command
    if not command or not Path(command[0]).is_absolute() or not Path(command[0]).is_file():
        raise RuntimeError("HOLD_WINJOB_EXACT_EXECUTABLE_REQUIRED")
    if not Path(a.cwd).resolve().is_dir():
        raise RuntimeError("HOLD_WINJOB_CWD_MISSING")
    code, peak = run_job_guarded(command, cwd=a.cwd,
         max_job_commit_bytes=a.max_job_commit_bytes,
         timeout_seconds=a.wall_seconds)
    print(json.dumps({"mode":"GUARDED_PROCESS_TREE", "child_exit":code,
         "job_commit_limit_bytes":a.max_job_commit_bytes,
         "peak_job_commit_bytes":peak, "rss_sampling_separate":True,
         "private_bytes_not_logged":True}, sort_keys=True))
    return 0 if code == 0 else 2

if __name__ == "__main__":
    raise SystemExit(main())
