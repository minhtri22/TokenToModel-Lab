"""P01 Windows Job Object kernel adapter; NO worker execution admission.

Native job creation and membership checking are implemented for later controlled
QA. The user-facing start_worker() remains fail-closed until a separate Windows
restricted-token/filesystem broker and supervisor have passed independent QA.
Do not interpret a Job Object as filesystem or network isolation.
"""
from __future__ import annotations

from dataclasses import dataclass
import ctypes
from ctypes import wintypes
import os

JOB_OBJECT_LIMIT_JOB_MEMORY = 0x00000200
JOB_OBJECT_LIMIT_KILL_ON_JOB_CLOSE = 0x00002000
JOB_OBJECT_LIMIT_BREAKAWAY_OK = 0x00000800
JOB_OBJECT_LIMIT_SILENT_BREAKAWAY_OK = 0x00001000
JOB_OBJECT_EXTENDED_LIMIT_INFORMATION_CLASS = 9
MAX_JOB_COMMIT_BYTES = 4 * 1024**3
MAX_WALL_SECONDS = 1800


class GuardNotEstablished(RuntimeError):
    pass


@dataclass(frozen=True)
class GuardPlan:
    max_job_commit_bytes: int = MAX_JOB_COMMIT_BYTES
    wall_clock_seconds: int = MAX_WALL_SECONDS
    kill_on_job_close: bool = True
    prohibit_breakaway: bool = True
    suspended_assign_verify_before_resume: bool = True

    def validate(self) -> None:
        if (type(self.max_job_commit_bytes) is not int
                or self.max_job_commit_bytes != MAX_JOB_COMMIT_BYTES
                or type(self.wall_clock_seconds) is not int
                or not (1 <= self.wall_clock_seconds <= MAX_WALL_SECONDS)
                or self.kill_on_job_close is not True
                or self.prohibit_breakaway is not True
                or self.suspended_assign_verify_before_resume is not True):
            raise GuardNotEstablished("JOB_GUARD_PLAN_WEAKENED")


class _BasicLimits(ctypes.Structure):
    _fields_ = [
        ("PerProcessUserTimeLimit", ctypes.c_int64),
        ("PerJobUserTimeLimit", ctypes.c_int64),
        ("LimitFlags", wintypes.DWORD),
        ("MinimumWorkingSetSize", ctypes.c_size_t),
        ("MaximumWorkingSetSize", ctypes.c_size_t),
        ("ActiveProcessLimit", wintypes.DWORD),
        ("Affinity", ctypes.c_size_t),
        ("PriorityClass", wintypes.DWORD),
        ("SchedulingClass", wintypes.DWORD),
    ]


class _IOCounters(ctypes.Structure):
    _fields_ = [
        ("ReadOperationCount", ctypes.c_uint64),
        ("WriteOperationCount", ctypes.c_uint64),
        ("OtherOperationCount", ctypes.c_uint64),
        ("ReadTransferCount", ctypes.c_uint64),
        ("WriteTransferCount", ctypes.c_uint64),
        ("OtherTransferCount", ctypes.c_uint64),
    ]


class _ExtendedLimits(ctypes.Structure):
    _fields_ = [
        ("BasicLimitInformation", _BasicLimits),
        ("IoInfo", _IOCounters),
        ("ProcessMemoryLimit", ctypes.c_size_t),
        ("JobMemoryLimit", ctypes.c_size_t),
        ("PeakProcessMemoryUsed", ctypes.c_size_t),
        ("PeakJobMemoryUsed", ctypes.c_size_t),
    ]


class NativeJob:
    """Own a configured job handle; NEVER resumes or creates a worker.

    An external supervisor must independently create a suspended restricted
    worker, attach it, verify membership, then decide on resume. This module
    intentionally exposes no resume capability before independent Windows QA.
    """

    def __init__(self, handle: int, api: object, plan: GuardPlan):
        self._handle = handle
        self._api = api
        self.plan = plan
        self._closed = False

    def _require_open(self) -> int:
        if self._closed or not self._handle:
            raise GuardNotEstablished("JOB_HANDLE_CLOSED")
        return self._handle

    def query_limits(self) -> dict[str, int]:
        handle = self._require_open()
        details = _ExtendedLimits()
        ok = self._api.QueryInformationJobObject(
            handle, JOB_OBJECT_EXTENDED_LIMIT_INFORMATION_CLASS,
            ctypes.byref(details), ctypes.sizeof(details), None
        )
        if not ok:
            raise GuardNotEstablished("QUERY_JOB_LIMITS_FAILED")
        flags = details.BasicLimitInformation.LimitFlags
        required = JOB_OBJECT_LIMIT_JOB_MEMORY | JOB_OBJECT_LIMIT_KILL_ON_JOB_CLOSE
        if ((flags & required) != required
                or flags & (JOB_OBJECT_LIMIT_BREAKAWAY_OK
                            | JOB_OBJECT_LIMIT_SILENT_BREAKAWAY_OK)
                or details.JobMemoryLimit != self.plan.max_job_commit_bytes):
            raise GuardNotEstablished("JOB_LIMIT_READBACK_MISMATCH")
        return {
            "limit_flags": flags,
            "job_memory_limit": details.JobMemoryLimit,
            "peak_job_memory_used": details.PeakJobMemoryUsed,
        }

    def attach_suspended(self, process_handle: int, *, suspended: bool) -> None:
        """Fail-closed membership check; caller must prove suspended status."""
        self._require_open()
        if suspended is not True or type(process_handle) is not int or process_handle <= 0:
            raise GuardNotEstablished("SUSPENDED_PROCESS_NOT_VERIFIED")
        try:
            self.query_limits()
            if not self._api.AssignProcessToJobObject(self._handle, process_handle):
                raise GuardNotEstablished("ASSIGN_PROCESS_TO_JOB_FAILED")
            member = wintypes.BOOL()
            if not self._api.IsProcessInJob(process_handle, self._handle, ctypes.byref(member)):
                raise GuardNotEstablished("JOB_MEMBERSHIP_QUERY_FAILED")
            if member.value != 1:
                raise GuardNotEstablished("JOB_MEMBERSHIP_NOT_CONFIRMED")
            self.query_limits()
        except Exception as exc:
            # A failure MUST NOT leave a candidate suspended process orphaned.
            # Win32 assignment can itself terminate the process; regardless,
            # a signaled process handle is required before classifying cleanup.
            self._api.TerminateProcess(process_handle, 1)
            if self._api.WaitForSingleObject(process_handle, 5000) != 0:
                raise GuardNotEstablished("FAILED_WORKER_TERMINATION_UNVERIFIED") from exc
            raise

    def terminate(self, exit_code: int = 1) -> None:
        self._require_open()
        if not self._api.TerminateJobObject(self._handle, exit_code):
            raise GuardNotEstablished("TERMINATE_JOB_FAILED")

    def close(self) -> None:
        if not self._closed:
            self._closed = True
            if self._handle:
                self._api.CloseHandle(self._handle)
                self._handle = 0

    def __enter__(self) -> NativeJob:
        self._require_open()
        return self

    def __exit__(self, *_exc: object) -> None:
        self.close()


def prepare_limited_job(plan: GuardPlan | None = None) -> NativeJob:
    """Create/round-trip a 4-GiB job, but do not create or run a worker.

    Not a complete secure launcher; invoking this on Windows itself needs
    a later, separately approved technical QA operation.
    """
    selected = plan if plan is not None else GuardPlan()
    if type(selected) is not GuardPlan:
        raise GuardNotEstablished("INVALID_GUARD_PLAN")
    selected.validate()
    if os.name != "nt":
        raise GuardNotEstablished("WINDOWS_ONLY")
    try:
        kernel = ctypes.WinDLL("kernel32", use_last_error=True)
    except (AttributeError, OSError) as exc:
        raise GuardNotEstablished("KERNEL32_UNAVAILABLE") from exc

    kernel.CreateJobObjectW.argtypes = [ctypes.c_void_p, wintypes.LPCWSTR]
    kernel.CreateJobObjectW.restype = wintypes.HANDLE
    kernel.SetInformationJobObject.argtypes = [
        wintypes.HANDLE, ctypes.c_int, ctypes.c_void_p, wintypes.DWORD
    ]
    kernel.SetInformationJobObject.restype = wintypes.BOOL
    kernel.QueryInformationJobObject.argtypes = [
        wintypes.HANDLE, ctypes.c_int, ctypes.c_void_p,
        wintypes.DWORD, ctypes.c_void_p
    ]
    kernel.QueryInformationJobObject.restype = wintypes.BOOL
    kernel.AssignProcessToJobObject.argtypes = [wintypes.HANDLE, wintypes.HANDLE]
    kernel.AssignProcessToJobObject.restype = wintypes.BOOL
    kernel.IsProcessInJob.argtypes = [
        wintypes.HANDLE, wintypes.HANDLE, ctypes.POINTER(wintypes.BOOL)
    ]
    kernel.IsProcessInJob.restype = wintypes.BOOL
    kernel.TerminateJobObject.argtypes = [wintypes.HANDLE, wintypes.UINT]
    kernel.TerminateJobObject.restype = wintypes.BOOL
    kernel.TerminateProcess.argtypes = [wintypes.HANDLE, wintypes.UINT]
    kernel.TerminateProcess.restype = wintypes.BOOL
    kernel.WaitForSingleObject.argtypes = [wintypes.HANDLE, wintypes.DWORD]
    kernel.WaitForSingleObject.restype = wintypes.DWORD
    kernel.CloseHandle.argtypes = [wintypes.HANDLE]
    kernel.CloseHandle.restype = wintypes.BOOL

    handle = kernel.CreateJobObjectW(None, None)
    if not handle:
        raise GuardNotEstablished("CREATE_JOB_FAILED")
    job = NativeJob(handle, kernel, selected)
    try:
        limits = _ExtendedLimits()
        limits.BasicLimitInformation.LimitFlags = (
            JOB_OBJECT_LIMIT_JOB_MEMORY | JOB_OBJECT_LIMIT_KILL_ON_JOB_CLOSE
        )
        limits.JobMemoryLimit = selected.max_job_commit_bytes
        if not kernel.SetInformationJobObject(
            handle, JOB_OBJECT_EXTENDED_LIMIT_INFORMATION_CLASS,
            ctypes.byref(limits), ctypes.sizeof(limits)
        ):
            raise GuardNotEstablished("SET_JOB_LIMIT_FAILED")
        job.query_limits()
        return job
    except BaseException:
        job.close()
        raise


def start_worker(*_args: object, **_kwargs: object) -> None:
    # This remains denied even if a caller claims "approved" in a string.
    # Restricted worker identity, no direct filesystem writes, pre-resume
    # attestation, monotonic watchdog and independent Windows QA are required.
    raise GuardNotEstablished("QA0_RESTRICTED_WORKER_AND_BROKER_NOT_QUALIFIED")
