"""Standard-library Win32 RSS probe: replaces optional psutil at I2.

This samples the current process WorkingSetSize (resident bytes), NOT the
entire child process tree, NOT a hard memory ceiling, and NOT an authorization.
The independent PowerShell process-tree watcher remains required. Native
Windows source/runtime QA is required before use. No checkpoint is accessed.
"""
from __future__ import annotations
import ctypes
from ctypes import wintypes
import sys

class PROCESS_MEMORY_COUNTERS(ctypes.Structure):
    _fields_ = [
        ("cb", wintypes.DWORD),
        ("PageFaultCount", wintypes.DWORD),
        ("PeakWorkingSetSize", ctypes.c_size_t),
        ("WorkingSetSize", ctypes.c_size_t),
        ("QuotaPeakPagedPoolUsage", ctypes.c_size_t),
        ("QuotaPagedPoolUsage", ctypes.c_size_t),
        ("QuotaPeakNonPagedPoolUsage", ctypes.c_size_t),
        ("QuotaNonPagedPoolUsage", ctypes.c_size_t),
        ("PagefileUsage", ctypes.c_size_t),
        ("PeakPagefileUsage", ctypes.c_size_t),
    ]

def current_process_rss_bytes() -> int:
    """Return resident working-set bytes for the *calling* Windows process."""
    if sys.platform != "win32":
        raise RuntimeError("HOLD_NATIVE_WINDOWS_REQUIRED")
    kernel32 = ctypes.WinDLL("kernel32", use_last_error=True)
    psapi = ctypes.WinDLL("psapi", use_last_error=True)
    kernel32.GetCurrentProcess.argtypes = []
    kernel32.GetCurrentProcess.restype = wintypes.HANDLE
    psapi.GetProcessMemoryInfo.argtypes = [
        wintypes.HANDLE, ctypes.POINTER(PROCESS_MEMORY_COUNTERS), wintypes.DWORD
    ]
    psapi.GetProcessMemoryInfo.restype = wintypes.BOOL
    pmc = PROCESS_MEMORY_COUNTERS()
    pmc.cb = ctypes.sizeof(PROCESS_MEMORY_COUNTERS)
    handle = kernel32.GetCurrentProcess()
    if not psapi.GetProcessMemoryInfo(handle, ctypes.byref(pmc), pmc.cb):
        raise OSError(ctypes.get_last_error(), "HOLD_NATIVE_GET_PROCESS_MEMORY_INFO")
    value = int(pmc.WorkingSetSize)
    if value <= 0:
        raise RuntimeError("HOLD_NATIVE_RSS_EMPTY_OR_INVALID")
    return value

def source_shape_qa() -> dict:
    """Pure structural check, not Windows native QA."""
    fields = [k for k, _ in PROCESS_MEMORY_COUNTERS._fields_]
    return {
        "struct_field_count": len(fields),
        "struct_fields": fields,
        "cb_size": ctypes.sizeof(PROCESS_MEMORY_COUNTERS),
        "os_requires_win32": True,
        "model_executed": False,
    }

if __name__ == "__main__":
    import json
    print(json.dumps(source_shape_qa(), sort_keys=True))
