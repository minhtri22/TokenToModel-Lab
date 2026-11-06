"""TTM P01 L1: fail-closed lifecycle logic for independent injection QA.

IMPORTANT: this module does not qualify a Windows security boundary and DOES NOT
expose a live-spawn entrypoint. It accepts an injected fake backend ONLY when
called by isolated tests. No ordinary caller can obtain a native run permit.
"""
from __future__ import annotations
from dataclasses import dataclass

class GuardFailure(RuntimeError):
    pass

@dataclass(frozen=True)
class CleanupReceipt:
    reason: str
    confirmed_terminated: bool
    close_failures: tuple[str, ...]

def abort_and_verify(backend, *, job=None, process=None, thread=None, reason='UNKNOWN'):
    """Always raise, including when cleanup verified; never return success."""
    errors = []
    if job is not None:
        try:
            if not backend.terminate_job(job):
                errors.append('JOB_TERMINATION_FAILED')
        except Exception:
            errors.append('JOB_TERMINATION_EXCEPTION')
    terminated = process is None
    if process is not None:
        try:
            terminated = bool(backend.wait(process, 5000))
            if not terminated:
                if not backend.terminate_process(process):
                    errors.append('PROCESS_TERMINATION_FAILED')
                terminated = bool(backend.wait(process, 5000))
        except Exception:
            errors.append('PROCESS_TERMINATION_EXCEPTION')
        if not terminated:
            errors.append('PROCESS_TERMINATION_UNVERIFIED')
    for name, handle in (('thread', thread), ('process', process), ('job', job)):
        if handle is not None:
            try:
                backend.close(handle)
            except Exception:
                errors.append('CLOSE_'+name.upper()+'_FAILED')
    raise GuardFailure(reason + (':' + ','.join(errors) if errors else ':TERMINATED_CONFIRMED'))

def inspect_mock_only(backend, *, fake_authority):
    """Exercise strict ordering in test with an explicit non-native fake marker.

    Any native backend is refused. This entrypoint must NOT be used to launch
    a Windows worker or count as evidence for W01-W12.
    """
    if type(fake_authority) is not str or fake_authority != 'MOCK_ONLY_NO_WIN32':
        raise GuardFailure('NO_NATIVE_EXECUTION_AUTHORITY')
    if type(backend).__module__ != 'test_native_guard_lifecycle_v2':
        raise GuardFailure('TEST_BACKEND_REQUIRED')
    job=process=thread=None
    try:
        job=backend.make_job()
        if not backend.job_limits_confirmed(job):
            raise GuardFailure('JOB_LIMIT_MISMATCH')
        process,thread=backend.create_suspended()
        if not backend.is_suspended(process,thread):
            raise GuardFailure('SUSPENDED_STATE_UNVERIFIED')
        if not backend.assign(job,process):
            raise GuardFailure('JOB_ASSIGN_FAILED')
        if not backend.is_member(job,process):
            raise GuardFailure('JOB_MEMBERSHIP_FAILED')
        if not backend.job_limits_confirmed(job):
            raise GuardFailure('JOB_LIMIT_CHANGED')
        if not backend.resume(thread):
            raise GuardFailure('RESUME_FAILED')
        # This is a *mock* only. Terminate even on simulated success, no live run.
        abort_and_verify(backend, job=job, process=process, thread=thread,
                         reason='MOCK_ONLY_SIMULATION_COMPLETE')
    except GuardFailure as exc:
        if str(exc).startswith('MOCK_ONLY_SIMULATION_COMPLETE') or 'TERMINATED_CONFIRMED' in str(exc) and 'MOCK_ONLY_SIMULATION_COMPLETE' in str(exc):
            raise
        abort_and_verify(backend, job=job, process=process, thread=thread,
                         reason=str(exc))
    except Exception as exc:
        abort_and_verify(backend, job=job, process=process, thread=thread,
                         reason='BACKEND_EXCEPTION_'+type(exc).__name__)
