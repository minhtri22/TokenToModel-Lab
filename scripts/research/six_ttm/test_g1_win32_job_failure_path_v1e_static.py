#!/usr/bin/env python3
"""Static safety review; target Windows execution is deliberately NOT claimed."""
from pathlib import Path
import ast
import subprocess
import sys

import pytest
import g1_win32_job_failure_path_v1e_candidate as win

SOURCE = Path(win.__file__).read_text(encoding='utf8')
TREE = ast.parse(SOURCE)

def test_safe_cpu_status_reports_not_production():
    s=win.status()
    assert s['production_qualified'] is False
    assert s['real_gpu_used'] is False
    assert s['science_executed'] is False

def test_win32_target_required_before_launch_on_linux():
    if win.os.name=='nt':pytest.skip('Direct Win32 test reserved for separate target')
    with pytest.raises(RuntimeError,match='STOP_G1_WINDOWS_HOST_REQUIRED'):
        win.run_harmless_qa(sleep_seconds=5,wall_timeout_ms=100)

def test_injected_cleanup_has_finally():
    f=next(x for x in TREE.body if isinstance(x,ast.FunctionDef) and x.name=='run_harmless_qa')
    ts=[n for n in ast.walk(f) if isinstance(n,ast.Try)]
    assert any(n.finalbody and 'TerminateProcess' in ast.unparse(n.finalbody)
               and 'WaitForSingleObject' in ast.unparse(n.finalbody) for n in ts)

def test_exact_owned_process_handle_cleanup_and_hard_failure():
    assert 'kernel.TerminateProcess(pi.hProcess' in SOURCE
    assert 'kernel.WaitForSingleObject(pi.hProcess, 2000)' in SOURCE
    assert 'STOP_G1_OWNED_CHILD_CLEANUP_UNVERIFIED' in SOURCE

def test_both_failure_injection_stages_present():
    assert 'post_create_pre_assign' in SOURCE
    assert 'post_assign_pre_resume' in SOURCE
    assert 'harmless-assign-fault-qa' in SOURCE
    assert 'harmless-resume-fault-qa' in SOURCE

def test_job_assigned_before_resume_and_kill_on_close():
    p=SOURCE.index('check(kernel.AssignProcessToJobObject(job, pi.hProcess)')
    q=SOURCE.index('check(kernel.ResumeThread(pi.hThread)')
    assert p<q
    assert '0x00002000  # KILL_ON_JOB_CLOSE' in SOURCE

def test_no_unrestricted_exec_argv():
    assert 'child_code = "import time;time.sleep(%d)" % sleep_seconds' in SOURCE
    assert 'args = [sys.executable, "-B", "-c", child_code]' in SOURCE
    assert 'subprocess.list2cmdline(args)' in SOURCE

def test_invalid_fault_mode_fails_before_kernel():
    # Source order check; actual Win32 negative QA must be on target machine.
    assert SOURCE.index('STOP_G1_QA_FAULT_MODE_INVALID') < SOURCE.index('ctypes.WinDLL')
