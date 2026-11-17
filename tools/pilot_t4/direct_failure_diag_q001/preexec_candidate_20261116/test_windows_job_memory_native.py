"""Windows-only resource probes using stdlib Python, with no model or input data."""
import ctypes
from ctypes import wintypes
import json
import os
from pathlib import Path
import subprocess
import sys
import tempfile
import time
import unittest

import windows_job_memory_limit as job
from windows_rss_native import current_process_rss_bytes

MIB = 1024**2
CAP = 96 * MIB

ALLOC = """
import ctypes
from ctypes import wintypes
import json
import sys
k = ctypes.WinDLL('kernel32', use_last_error=True)
k.VirtualAlloc.argtypes = [ctypes.c_void_p, ctypes.c_size_t, wintypes.DWORD, wintypes.DWORD]
k.VirtualAlloc.restype = ctypes.c_void_p
size = int(sys.argv[1])
p = k.VirtualAlloc(None, size, 0x3000, 4)
error = ctypes.get_last_error() if not p else 0
print(json.dumps({'committed': bool(p), 'request_bytes': size, 'winerror': error}), flush=True)
"""


def py(code, *args):
    return [sys.executable, "-I", "-B", "-c", code, *map(str, args)]


def execute(code, *args, cap=CAP, timeout=10, cwd=None):
    return job.run_job_guarded(py(code, *args), cwd=cwd or os.getcwd(),
                               max_job_commit_bytes=cap, timeout_seconds=timeout)


def log(value):
    print(json.dumps(value, sort_keys=True), flush=True)


def process_handle(pid):
    k = job._kernel()
    k.OpenProcess.argtypes = [wintypes.DWORD, wintypes.BOOL, wintypes.DWORD]
    k.OpenProcess.restype = wintypes.HANDLE
    handle = k.OpenProcess(0x00100000, False, pid)
    job.require(handle, "TEST_OPEN_CHILD")
    return k, handle


class Win32QA(unittest.TestCase):
    def test_rss_vs_psapi_and_working_set_growth(self):
        ps = Path(os.environ["SystemRoot"]) / "System32/WindowsPowerShell/v1.0/powershell.exe"
        before = current_process_rss_bytes()
        data = bytearray(48 * MIB)
        for offset in range(0, len(data), 4096):
            data[offset] = 1
        touched = current_process_rss_bytes()
        independent = int(subprocess.check_output(
            [str(ps), "-NoProfile", "-Command", f"(Get-Process -Id {os.getpid()}).WorkingSet64"],
            text=True).strip())
        self.assertGreater(touched - before, 40 * MIB)
        self.assertLess(abs(independent - touched), 8 * MIB)
        log({"rss_before": before, "rss_after_touch": touched, "ps51_working_set": independent})

    def test_commit_ceiling_and_aggregate_descendant(self):
        code, single_peak = execute(ALLOC + "\nsys.exit(0 if p else 86)", 52 * MIB)
        self.assertEqual(code, 0)
        self.assertGreaterEqual(single_peak, 52 * MIB)
        self.assertLessEqual(single_peak, CAP)
        code, above_peak = execute(ALLOC + "\nsys.exit(86 if not p and error in (8, 14, 1455, 1816) else 92)",
                                   CAP + MIB)
        self.assertEqual(code, 86)
        # Windows can include a rejected allocation's transient charge in the
        # peak counter. The native VirtualAlloc outcome establishes enforcement.
        self.assertGreater(above_peak, 0)
        aggregate = ALLOC + """
import subprocess
if not p:
    sys.exit(91)
probe = subprocess.run([sys.executable, '-I', '-B', '-c', sys.argv[2], sys.argv[1]])
sys.exit(probe.returncode)
"""
        child = ALLOC + "\nsys.exit(86 if not p and error in (8, 14, 1455, 1816) else 92)"
        code, peak = execute(aggregate, 52 * MIB, child)
        self.assertEqual(code, 86)
        self.assertGreaterEqual(peak, 52 * MIB)
        log({"commit_cap": CAP, "single_peak_commit": single_peak, "above_cap_peak_commit": above_peak,
             "aggregate_peak_commit": peak, "resource_exit": code})

    def test_nested_membership(self):
        folder = str(Path(job.__file__).parent)
        code, _ = execute("""
import os, sys
sys.path.insert(0, sys.argv[1])
import windows_job_memory_limit as j
k = j._kernel()
j.read_limits(k, None, int(sys.argv[2]))
child = "import sys; sys.path.insert(0,sys.argv[1]); import windows_job_memory_limit as j; j.read_limits(j._kernel(), None, int(sys.argv[2])); sys.exit(31)"
code, peak = j.run_job_guarded([sys.executable, '-I', '-c', child, sys.argv[1], str(64*1024**2)],
    cwd=os.getcwd(), max_job_commit_bytes=64*1024**2, timeout_seconds=5)
sys.exit(code)
""", folder, 192 * MIB, cap=192 * MIB)
        self.assertEqual(code, 31)

    def test_exit_and_late_failure(self):
        self.assertEqual(execute("raise SystemExit(37)")[0], 37)
        with self.assertRaisesRegex(TimeoutError, "WINJOB_WALL_TIME"):
            execute("import time; time.sleep(60)", timeout=1)
        with self.assertRaisesRegex(OSError, "CREATE_ASSIGNED_SUSPENDED"):
            job.run_job_guarded([str(Path(sys.executable).with_name("missing-q001-probe.exe"))],
                                cwd=os.getcwd(), max_job_commit_bytes=CAP, timeout_seconds=1)
        stray = """
import subprocess, sys
subprocess.Popen([sys.executable, '-c', 'import time; time.sleep(60)'], close_fds=True)
"""
        with self.assertRaisesRegex(RuntimeError, "DESCENDANT_ACTIVE"):
            execute(stray)

    def test_inherited_std_handles_only_and_kill_on_last_close(self):
        folder = str(Path(job.__file__).parent)
        supervisor_code = """
import os, sys
sys.path.insert(0, sys.argv[1])
import msvcrt
import windows_job_memory_limit as j
fd = os.open(sys.argv[2] + '.secret', os.O_CREAT | os.O_WRONLY | os.O_EXCL)
os.set_inheritable(fd, True)
j.run_job_guarded([sys.executable, '-I', '-c', sys.argv[3], sys.argv[2],
                   str(msvcrt.get_osfhandle(fd))],
    cwd=os.getcwd(), max_job_commit_bytes=96 * 1024**2, timeout_seconds=25)
"""
        child = """
import ctypes, json, os, pathlib, subprocess, sys, time
from ctypes import wintypes
k = ctypes.WinDLL('kernel32', use_last_error=True)
k.GetFinalPathNameByHandleW.argtypes = [wintypes.HANDLE, wintypes.LPWSTR, wintypes.DWORD, wintypes.DWORD]
k.GetFinalPathNameByHandleW.restype = wintypes.DWORD
path = ctypes.create_unicode_buffer(1024)
actual = k.GetFinalPathNameByHandleW(int(sys.argv[2]), path, len(path), 0)
# Handle numbers may be reused by CPython. Compare the actual object identity.
secret_inherited = bool(actual and path.value.casefold().endswith((sys.argv[1] + '.secret').casefold()))
print('CHILD_STDOUT', flush=True)
print('CHILD_STDERR', file=sys.stderr, flush=True)
descendant = subprocess.Popen([sys.executable, '-c', 'import time; time.sleep(60)'], close_fds=True)
p = pathlib.Path(sys.argv[1])
tmp = p.with_suffix('.tmp')
tmp.write_text(json.dumps({'child': os.getpid(), 'descendant': descendant.pid,
                          'stdin_eof': not sys.stdin.read(1), 'secret_inherited': secret_inherited}))
tmp.replace(p)
time.sleep(60)
"""
        with tempfile.TemporaryDirectory() as temp:
            target = Path(temp) / "probe.json"
            proc = subprocess.Popen(py(supervisor_code, folder, target, child),
                                    stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
            handles = []
            try:
                deadline = time.monotonic() + 10
                while not target.is_file() and proc.poll() is None and time.monotonic() < deadline:
                    time.sleep(0.02)
                self.assertTrue(target.is_file(), "child did not reach the readiness marker")
                marker = json.loads(target.read_text())
                for name in ("child", "descendant"):
                    handles.append(process_handle(marker[name]))
                proc.kill()
                proc.wait(timeout=6)
                for k, handle in handles:
                    self.assertEqual(k.WaitForSingleObject(handle, 5000), job.WAIT_OBJECT_0)
                self.assertTrue(marker["stdin_eof"])
                self.assertFalse(marker["secret_inherited"])
                out, err = proc.communicate(timeout=6)
                self.assertIn("CHILD_STDOUT", out)
                self.assertIn("CHILD_STDERR", err)
                log({"stdio_allowlist": True, "kill_last_close_root": True, "kill_last_close_descendant": True})
            finally:
                if proc.poll() is None:
                    proc.kill()
                proc.communicate(timeout=6)
                for k, handle in handles:
                    k.CloseHandle(handle)


if __name__ == "__main__":
    unittest.main()
