"""P01 C09 Windows guard/broker negative matrix: design and pure policy QA.

This is NOT the Windows W01-W12 execution suite; no file/process/JobObject
mutations occur. Run only after the independent static-test admission.
"""
from __future__ import annotations

import unittest
from runtime.p01.windows_job_guard import GuardNotEstablished, GuardPlan, start_worker
from runtime.p01.write_quota_broker import (
    BrokerUnavailable, BrokerPolicy, QuotaLedger, relative_output_path, write_file
)

ROOT = r"D:\WORK\RESEARCH\TokenToModel-Lab\worktrees\p01-f0-static-i0a-20261105"


class IndependentGuardPolicyNegativeQA(unittest.TestCase):
    def test_job_memory_is_commit_not_rss(self):
        plan = GuardPlan()
        plan.validate()
        self.assertEqual(plan.max_job_commit_bytes, 4 * 1024**3)
        self.assertEqual(plan.wall_clock_seconds, 1800)

    def test_reject_weakened_job_limits(self):
        for plan in (
            GuardPlan(max_job_commit_bytes=0),
            GuardPlan(max_job_commit_bytes=5 * 1024**3),
            GuardPlan(wall_clock_seconds=1801),
            GuardPlan(kill_on_job_close=False),
            GuardPlan(prohibit_breakaway=False),
            GuardPlan(suspended_assign_verify_before_resume=False),
        ):
            with self.subTest(plan=plan):
                with self.assertRaises(GuardNotEstablished):
                    plan.validate()

    def test_no_worker_launch_from_unqualified_api(self):
        for args in ((), ("python.exe",), ({"approval": True},)):
            with self.subTest(args=args):
                with self.assertRaises(GuardNotEstablished):
                    start_worker(*args)

    def test_broker_policy_hard_requirements(self):
        BrokerPolicy(ROOT).validate()
        for policy in (
            BrokerPolicy("C:relative"),
            BrokerPolicy(""),
            BrokerPolicy(ROOT, quota_bytes=MAX_PLUS_ONE),
            BrokerPolicy(ROOT, create_new_only=False),
            BrokerPolicy(ROOT, prohibit_reparse=False),
            BrokerPolicy(ROOT, require_restricted_worker=False),
        ):
            with self.subTest(policy=policy):
                with self.assertRaises(BrokerUnavailable):
                    policy.validate()

    def test_path_traversal_and_win32_aliases_denied(self):
        bad = [
            "", "../outside", "folder/../escape", "./abc", "folder//foo",
            r"D:\other\out", r"\\server\share\out", r"..\escape",
            "/root", "C:relative", "file:stream", "con.txt",
            "nul", "AUX", "COM1.txt", "folder/name.", "folder/name ",
            "folder\\name", "x//y", "file?bad", "file|bad",
        ]
        for name in bad:
            with self.subTest(name=name):
                with self.assertRaises(BrokerUnavailable):
                    relative_output_path(name)

    def test_path_rejects_case_insensitive_collision(self):
        ledger = QuotaLedger(BrokerPolicy(ROOT))
        self.assertEqual(ledger.reserve("qa/evidence.json", 10), "qa/evidence.json")
        with self.assertRaises(BrokerUnavailable):
            ledger.reserve("QA/EVIDENCE.JSON", 1)

    def test_quota_is_prewrite_and_no_partial_accept(self):
        ledger = QuotaLedger(BrokerPolicy(ROOT, quota_bytes=12))
        ledger.reserve("a.dat", 10)
        with self.assertRaises(BrokerUnavailable):
            ledger.reserve("b.dat", 3)
        self.assertEqual(ledger.reserved_bytes, 10)
        self.assertNotIn("b.dat", ledger.reserved_paths)

    def test_bool_and_negative_sizes_denied(self):
        ledger = QuotaLedger(BrokerPolicy(ROOT))
        for bad in (True, -1, 1.0, "2", None):
            with self.subTest(size=bad):
                with self.assertRaises(BrokerUnavailable):
                    ledger.reserve("a.dat", bad)

    def test_broker_write_never_falls_through(self):
        for args in ((), ("a.dat", b"abc"), ({"approved": True},)):
            with self.subTest(args=args):
                with self.assertRaises(BrokerUnavailable):
                    write_file(*args)


MAX_PLUS_ONE = 2 * 1024**3 + 1
