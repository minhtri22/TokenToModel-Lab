#!/usr/bin/env python3
"""V1e failure-path closure candidate. Harmless CPU child ONLY.

On Windows, starts an exact Python self-test command SUSPENDED, attaches to a
kill-on-job-close Job Object BEFORE resuming and enforces a wall timeout.
This is NOT an approved Qwen launcher, T4 budget guard or production principal.
It must be tested independently on the target Windows 11 machine.
"""
import ctypes
from ctypes import wintypes
import json
import os
import subprocess
import sys


def status():
    return {"schema": "ttm.six.g1.win32_failure_path_candidate.v1e",
            "platform": os.name, "production_qualified": False,
            "real_gpu_used": False, "science_executed": False}


def run_harmless_qa(*, sleep_seconds: int, wall_timeout_ms: int, fault_injection=None):
    if os.name != "nt":
        raise RuntimeError("STOP_G1_WINDOWS_HOST_REQUIRED")
    if type(sleep_seconds) is not int or not (0 <= sleep_seconds <= 8):
        raise RuntimeError("STOP_G1_HARMLESS_CHILD_ONLY")
    if type(wall_timeout_ms) is not int or not (50 <= wall_timeout_ms <= 5000):
        raise RuntimeError("STOP_G1_QA_TIMEOUT_INVALID")
    # Faults are injected ONLY into an owned, fixed Python sleep child.
    # Never allow user-provided executable paths or arbitrary command input.
    if fault_injection not in (None, "post_create_pre_assign", "post_assign_pre_resume"):
        raise RuntimeError("STOP_G1_QA_FAULT_MODE_INVALID")

    kernel = ctypes.WinDLL("kernel32", use_last_error=True)
    HANDLE = wintypes.HANDLE
    DWORD = wintypes.DWORD
    LPWSTR = wintypes.LPWSTR
    LPVOID = wintypes.LPVOID
    SIZE_T = ctypes.c_size_t

    class STARTUPINFOW(ctypes.Structure):
        _fields_ = [("cb", DWORD), ("lpReserved", LPWSTR), ("lpDesktop", LPWSTR),
                    ("lpTitle", LPWSTR), ("dwX", DWORD), ("dwY", DWORD),
                    ("dwXSize", DWORD), ("dwYSize", DWORD),
                    ("dwXCountChars", DWORD), ("dwYCountChars", DWORD),
                    ("dwFillAttribute", DWORD), ("dwFlags", DWORD),
                    ("wShowWindow", wintypes.WORD), ("cbReserved2", wintypes.WORD),
                    ("lpReserved2", ctypes.c_void_p), ("hStdInput", HANDLE),
                    ("hStdOutput", HANDLE), ("hStdError", HANDLE)]

    class PROCESS_INFORMATION(ctypes.Structure):
        _fields_ = [("hProcess", HANDLE), ("hThread", HANDLE),
                    ("dwProcessId", DWORD), ("dwThreadId", DWORD)]

    class BASIC_LIMIT(ctypes.Structure):
        _fields_ = [("PerProcessUserTimeLimit", ctypes.c_int64),
                    ("PerJobUserTimeLimit", ctypes.c_int64),
                    ("LimitFlags", DWORD),
                    ("MinimumWorkingSetSize", SIZE_T),
                    ("MaximumWorkingSetSize", SIZE_T),
                    ("ActiveProcessLimit", DWORD),
                    ("Affinity", SIZE_T),
                    ("PriorityClass", DWORD),
                    ("SchedulingClass", DWORD)]

    class IO_COUNTERS(ctypes.Structure):
        _fields_ = [("ReadOperationCount", ctypes.c_uint64),
                    ("WriteOperationCount", ctypes.c_uint64),
                    ("OtherOperationCount", ctypes.c_uint64),
                    ("ReadTransferCount", ctypes.c_uint64),
                    ("WriteTransferCount", ctypes.c_uint64),
                    ("OtherTransferCount", ctypes.c_uint64)]

    class EXTENDED_LIMIT(ctypes.Structure):
        _fields_ = [("BasicLimitInformation", BASIC_LIMIT),
                    ("IoInfo", IO_COUNTERS),
                    ("ProcessMemoryLimit", SIZE_T),
                    ("JobMemoryLimit", SIZE_T),
                    ("PeakProcessMemoryUsed", SIZE_T),
                    ("PeakJobMemoryUsed", SIZE_T)]

    kernel.CreateJobObjectW.argtypes = [LPVOID, LPWSTR]
    kernel.CreateJobObjectW.restype = HANDLE
    kernel.SetInformationJobObject.argtypes = [HANDLE, ctypes.c_int,
                                                LPVOID, DWORD]
    kernel.SetInformationJobObject.restype = wintypes.BOOL
    kernel.CreateProcessW.argtypes = [LPWSTR, LPWSTR, LPVOID, LPVOID,
                                       wintypes.BOOL, DWORD, LPVOID,
                                       LPWSTR, ctypes.POINTER(STARTUPINFOW),
                                       ctypes.POINTER(PROCESS_INFORMATION)]
    kernel.CreateProcessW.restype = wintypes.BOOL
    kernel.AssignProcessToJobObject.argtypes = [HANDLE, HANDLE]
    kernel.AssignProcessToJobObject.restype = wintypes.BOOL
    kernel.ResumeThread.argtypes = [HANDLE]
    kernel.ResumeThread.restype = DWORD
    kernel.WaitForSingleObject.argtypes = [HANDLE, DWORD]
    kernel.WaitForSingleObject.restype = DWORD
    kernel.TerminateJobObject.argtypes = [HANDLE, ctypes.c_uint]
    kernel.TerminateJobObject.restype = wintypes.BOOL
    kernel.TerminateProcess.argtypes = [HANDLE, ctypes.c_uint]
    kernel.TerminateProcess.restype = wintypes.BOOL
    kernel.CloseHandle.argtypes = [HANDLE]
    kernel.CloseHandle.restype = wintypes.BOOL
    kernel.GetExitCodeProcess.argtypes = [HANDLE, ctypes.POINTER(DWORD)]
    kernel.GetExitCodeProcess.restype = wintypes.BOOL

    def check(ok, tag):
        if not ok:
            raise OSError("STOP_G1_" + tag + "_WINERROR_" + str(ctypes.get_last_error()))

    # Fixed allowlist, no argv passed through from users or source/TEST.
    child_code = "import time;time.sleep(%d)" % sleep_seconds
    args = [sys.executable, "-B", "-c", child_code]
    cmdline = ctypes.create_unicode_buffer(subprocess.list2cmdline(args))
    job = kernel.CreateJobObjectW(None, None)
    check(job, "CREATE_JOB")
    pi = PROCESS_INFORMATION()
    spawned = False
    assigned = False
    completed = False
    cleanup_verified = False
    caught_expected_fault = False
    result = None
    try:
        limits = EXTENDED_LIMIT()
        limits.BasicLimitInformation.LimitFlags = 0x00002000  # KILL_ON_JOB_CLOSE
        check(kernel.SetInformationJobObject(job, 9, ctypes.byref(limits),
                                             ctypes.sizeof(limits)), "JOB_LIMITS")
        si = STARTUPINFOW()
        si.cb = ctypes.sizeof(STARTUPINFOW)
        flags = 0x00000004 | 0x08000000  # suspended, no window
        check(kernel.CreateProcessW(sys.executable, cmdline, None, None, False,
                                     flags, None, None, ctypes.byref(si),
                                     ctypes.byref(pi)), "SUSPENDED_CREATE")
        spawned = True
        if fault_injection == "post_create_pre_assign":
            raise RuntimeError("STOP_G1_QA_INJECTED_POST_CREATE_PRE_ASSIGN")
        check(kernel.AssignProcessToJobObject(job, pi.hProcess), "JOB_ASSIGN")
        assigned = True
        if fault_injection == "post_assign_pre_resume":
            raise RuntimeError("STOP_G1_QA_INJECTED_POST_ASSIGN_PRE_RESUME")
        check(kernel.ResumeThread(pi.hThread) != 0xffffffff, "THREAD_RESUME")
        outcome = kernel.WaitForSingleObject(pi.hProcess, wall_timeout_ms)
        if outcome == 258:  # WAIT_TIMEOUT
            check(kernel.TerminateJobObject(job, 0xEE), "JOB_FORCED_KILL")
            check(kernel.WaitForSingleObject(pi.hProcess, 2000) == 0,
                  "JOB_KILL_NOT_OBSERVED")
            completed = True
            result = {**status(), "test": "HARMLESS_SLEEP",
                      "forced_kill_verified": True, "timed_out": True,
                      "child_exited": True}
        else:
            check(outcome == 0, "WAIT_FAILED")
            exit_code = DWORD()
            check(kernel.GetExitCodeProcess(pi.hProcess, ctypes.byref(exit_code)),
                  "GET_EXIT_CODE")
            completed = True
            result = {**status(), "test": "HARMLESS_SLEEP",
                      "forced_kill_verified": False, "timed_out": False,
                      "child_exited": True, "exit_code": exit_code.value}
    except RuntimeError as err:
        # An expected synthetic fault is a PASS only when `finally` proves
        # that the owned suspended child was really reaped. Other failures STOP.
        expected = (fault_injection is not None and
                    str(err) == "STOP_G1_QA_INJECTED_" +
                    ("POST_CREATE_PRE_ASSIGN" if fault_injection ==
                     "post_create_pre_assign" else "POST_ASSIGN_PRE_RESUME"))
        if not expected:
            raise
        caught_expected_fault = True
        result = {**status(), "test": "HARMLESS_FAULT_INJECTION",
                  "fault_mode": fault_injection, "child_exited": False,
                  "cleanup_verified": False}
    finally:
        if spawned and not completed:
            # CreateProcess succeeded. Even if job ASSIGN failed, this exact
            # owned HANDLE can be terminated. Closing an unassigned job alone
            # is insufficient to kill a suspended process.
            kernel.TerminateProcess(pi.hProcess, 0xEF)
            cleanup_verified = (kernel.WaitForSingleObject(pi.hProcess, 2000) == 0)
            if result is not None and caught_expected_fault:
                result["cleanup_verified"] = cleanup_verified
                result["child_exited"] = cleanup_verified
            # On ANY abnormal path, a failure to reap the created child is a
            # hard failure; do not return PASS on an orphan.
            if not cleanup_verified:
                kernel.CloseHandle(job)
                kernel.CloseHandle(pi.hThread)
                kernel.CloseHandle(pi.hProcess)
                raise RuntimeError("STOP_G1_OWNED_CHILD_CLEANUP_UNVERIFIED")
        kernel.CloseHandle(job)  # kill-on-close for attached descendants
        if spawned:
            kernel.CloseHandle(pi.hThread)
            kernel.CloseHandle(pi.hProcess)
    assert result is not None
    return result

if __name__ == "__main__":
    import argparse
    p=argparse.ArgumentParser()
    p.add_argument("--mode", required=True, choices=("status", "harmless-sleep-qa", "harmless-assign-fault-qa", "harmless-resume-fault-qa"))
    p.add_argument("--sleep-seconds", type=int, default=2)
    p.add_argument("--timeout-ms", type=int, default=200)
    a=p.parse_args()
    if a.mode == "status":
        print(json.dumps(status(), sort_keys=True))
    else:
        fault = {"harmless-assign-fault-qa": "post_create_pre_assign",
                 "harmless-resume-fault-qa": "post_assign_pre_resume"}.get(a.mode)
        print(json.dumps(run_harmless_qa(sleep_seconds=a.sleep_seconds,
                      wall_timeout_ms=a.timeout_ms, fault_injection=fault), sort_keys=True))
