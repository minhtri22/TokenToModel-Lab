"""RF-00 no-model Win32 Job Object regression and exact CLI tests.

CPU fixture only. Do not read checkpoints, tokenizers or TEST/FINAL24.
CI on Windows 11/Server and owner Windows PS5.1 must independently retain
the raw output as evidence; Linux source tests are NOT native certification.
"""
from __future__ import annotations
import contextlib
import io
from pathlib import Path
import sys
import unittest
from unittest import mock

import windows_job_memory_limit as winjob


class SourceContract(unittest.TestCase):
    def test_struct_metadata(self):
        d = winjob.struct_sizes()
        self.assertIn("JOBOBJECT_BASIC_ACCOUNTING_INFORMATION", d)
        self.assertIn("JOBOBJECT_EXTENDED_LIMIT_INFORMATION", d)
        self.assertGreater(d["PROCESS_INFORMATION"], 0)

    def test_max_commit_cap_precondition(self):
        # Non-Windows fails before argument checks; native Windows rejects >12GiB.
        if sys.platform == "win32":
            with self.assertRaises(ValueError):
                winjob.run_job_guarded([sys.executable], cwd=".",
                    max_job_commit_bytes=13 * 1024**3, timeout_seconds=5)
        else:
            with self.assertRaises(RuntimeError):
                winjob.run_job_guarded([sys.executable], cwd=".",
                    max_job_commit_bytes=13 * 1024**3, timeout_seconds=5)

    def test_cli_no_arbitrary_executable(self):
        with self.assertRaisesRegex(RuntimeError, "EXACT_EXECUTABLE"):
            winjob.main(["--guard", "--", "python", "-c", "print(1)"])

    def test_cli_mock_accepts_zero_exit(self):
        with mock.patch.object(winjob, "run_job_guarded", return_value=(0, 9876)) as fn:
            with contextlib.redirect_stdout(io.StringIO()) as out:
                code = winjob.main(["--guard", "--cwd", str(Path.cwd()),
                    "--max-job-commit-bytes", "134217728", "--wall-seconds", "4",
                    "--", str(Path(sys.executable).resolve()), "-c", "pass"])
        self.assertEqual(code, 0)
        self.assertIn("GUARDED_PROCESS_TREE", out.getvalue())
        self.assertIn("peak_job_commit_bytes", out.getvalue())
        self.assertEqual(fn.call_args.kwargs["max_job_commit_bytes"], 134217728)

    def test_cli_mock_denies_nonzero(self):
        with mock.patch.object(winjob, "run_job_guarded", return_value=(5, 9000)):
            with contextlib.redirect_stdout(io.StringIO()):
                code = winjob.main(["--guard", "--", str(Path(sys.executable).resolve()), "-c", "pass"])
        self.assertEqual(code, 2)


@unittest.skipUnless(sys.platform == "win32" and sys.maxsize > 2**32,
                     "Requires actual native Windows x64 (NOT Linux simulation)")
class NativeNoModel(unittest.TestCase):
    def test_native_smoke(self):
        with contextlib.redirect_stdout(io.StringIO()) as out:
            code = winjob.main(["--native-smoke"])
        self.assertEqual(code, 0, out.getvalue())
        self.assertIn("NO_MODEL_SMOKE", out.getvalue())

    def test_native_negative_memory_timeout_orphan(self):
        with contextlib.redirect_stdout(io.StringIO()) as out:
            code = winjob.main(["--native-negative"])
        self.assertEqual(code, 0, out.getvalue())
        self.assertIn('"pass": true', out.getvalue())
        self.assertIn("orphan_descendant", out.getvalue())


if __name__ == "__main__":
    unittest.main(verbosity=2)
