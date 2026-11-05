"""F0 Windows guard interface, SOURCE ONLY; NOT A FUNCTIONAL SECURITY BOUNDARY.

Fail closed until an approved QA0 implementation demonstrates suspended process,
assigned Job Object, no breakaway and resource limits BEFORE ResumeThread.
"""
from __future__ import annotations
from dataclasses import dataclass


class GuardNotEstablished(RuntimeError):
    pass


@dataclass(frozen=True)
class GuardPlan:
    max_job_commit_bytes: int = 4294967296
    wall_clock_seconds: int = 1800
    kill_on_job_close: bool = True
    prohibit_breakaway: bool = True
    suspended_assign_verify_before_resume: bool = True


def start_worker(*_args: object, **_kwargs: object) -> None:
    # Never fall back to an unguarded subprocess, including python -m/pytest.
    raise GuardNotEstablished("QA0_JOB_OBJECT_AND_BROKER_UNIMPLEMENTED")
