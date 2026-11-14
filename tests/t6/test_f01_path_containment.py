"""F-01 negative QA for Python entry points; no training or benchmarking.

All temporary nodes are created inside the TTM project artifact subtree.
On Windows, a real MKLINK /J junction probe is attempted without admin rights.
"""
from __future__ import annotations

import os
import subprocess
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

from tools.t6.path_containment import resolve_t6_artifact
from tools.t6.cache_ab_benchmark_fixture import ROOT, _ensure_safe_output
from tools.t6 import independent_scoped_qa as qa

BASE = ROOT / "artifacts" / "qa" / "t6"


class T6F01PathContainmentTests(unittest.TestCase):
    def setUp(self):
        self.assertTrue(BASE.is_dir(), "canonical T6 QA subtree must exist")
        self.tmp = tempfile.TemporaryDirectory(dir=BASE, prefix="t6_f01_")
        self.addCleanup(self.tmp.cleanup)
        self.parent = Path(self.tmp.name)
        self.rel = self.parent.relative_to(ROOT).as_posix()

    def target(self, filename="new.json"):
        return self.rel + "/" + filename

    def test_valid_output_stays_inside_existing_subtree(self):
        p = resolve_t6_artifact(ROOT, self.target(), for_write=True, suffix=".json")
        self.assertEqual(p, self.parent / "new.json")
        self.assertFalse(p.exists())

    def test_existing_output_rejected_without_overwrite(self):
        target = self.parent / "evidence.json"
        target.write_text("original", encoding="utf-8")
        with self.assertRaises(FileExistsError):
            resolve_t6_artifact(ROOT, self.target("evidence.json"), for_write=True, suffix=".json")
        self.assertEqual(target.read_text(encoding="utf-8"), "original")

    def test_malicious_lexical_paths_rejected(self):
        bad = (
            "../foo.json", "/tmp/f.json", "C:/Windows/Temp/out.json",
            r"C:\Windows\Temp\out.json", "//server/share/a.json",
            "artifacts/qa/t6/../../outside.json",
            "artifacts/qa/t6//double.json", "artifacts/qa/t6/./dot.json",
            "artifacts/qa/t6/bad.txt", "artifacts/qa/t6/bad.json:evil",
            "artifacts/qa/t6/NUL.json", "artifacts/qa/not_t6/a.json",
        )
        for candidate in bad:
            with self.subTest(candidate=candidate):
                with self.assertRaises(ValueError):
                    resolve_t6_artifact(ROOT, candidate, for_write=True, suffix=".json")

    def test_missing_parent_fails_without_creation(self):
        p = self.target("missing/sub/out.json")
        with self.assertRaises(ValueError):
            resolve_t6_artifact(ROOT, p, for_write=True, suffix=".json")
        self.assertFalse((self.parent / "missing").exists())

    def test_qa_input_must_be_existing_regular_file(self):
        with self.assertRaises(ValueError):
            resolve_t6_artifact(ROOT, self.target("nope.json"), for_write=False, suffix=".json")
        good = self.parent / "exists.json"
        good.write_text("{}", encoding="utf-8")
        self.assertEqual(resolve_t6_artifact(ROOT, self.target("exists.json"), for_write=False, suffix=".json"), good)

    def test_mocked_windows_junction_denied_in_both_python_tools(self):
        component = self.parent / "junction_parent"
        component.mkdir()
        relative = self.rel + "/junction_parent/new.json"
        old = getattr(Path, "is_junction", lambda path: False)

        def flagged(path):
            return path == component or old(path)

        with patch.object(Path, "is_junction", flagged, create=True):
            with self.assertRaisesRegex(ValueError, "REPARSE"):
                resolve_t6_artifact(ROOT, relative, for_write=True, suffix=".json")
            with self.assertRaisesRegex(ValueError, "REPARSE"):
                _ensure_safe_output(relative)
            # No input reads, output directory creation, or report changes.
            with self.assertRaisesRegex(ValueError, "REPARSE"):
                qa.main(["--report", relative, "--unittest-log",
                         self.target("missing.log"), "--output", self.target("qa.json")])
        self.assertFalse((component / "new.json").exists())

    def test_mocked_symlink_denied_before_write(self):
        component = self.parent / "symlink_parent"
        component.mkdir()
        old = Path.is_symlink

        def flagged(path):
            return path == component or old(path)

        with patch.object(Path, "is_symlink", flagged):
            with self.assertRaisesRegex(ValueError, "REPARSE"):
                resolve_t6_artifact(ROOT, self.rel + "/symlink_parent/out.json",
                                    for_write=True, suffix=".json")
        self.assertFalse((component / "out.json").exists())

    def test_qa_rejects_unsafe_output_even_with_valid_inputs(self):
        report = self.parent / "source.json"
        log = self.parent / "unittest.log"
        report.write_text("{}", encoding="utf-8")
        log.write_text("OK", encoding="utf-8")
        with self.assertRaises(ValueError):
            qa.main(["--report", self.target("source.json"),
                     "--unittest-log", self.target("unittest.log"),
                     "--output", "artifacts/qa/t6/../escaped.json"])

    @unittest.skipUnless(os.name == "nt", "native Windows junction probe")
    def test_real_windows_junction_rejected_before_file_creation(self):
        link = self.parent / "real_junction"
        # Link to an existing project directory outside the allowed evidence subtree.
        # Never create or modify anything at the junction target.
        target = ROOT / "src"
        proc = subprocess.run(["cmd.exe", "/d", "/c", "mklink", "/J", str(link), str(target)],
                              capture_output=True, text=True, check=False)
        if proc.returncode != 0:
            self.skipTest("mklink /J not available in this Windows session")
        try:
            self.assertTrue(link.is_junction(), "Windows Python 3.12 must detect actual junction")
            escaped = self.rel + "/real_junction/t6_guard_out.json"
            with self.assertRaisesRegex(ValueError, "REPARSE"):
                resolve_t6_artifact(ROOT, escaped, for_write=True, suffix=".json")
            with self.assertRaisesRegex(ValueError, "REPARSE"):
                _ensure_safe_output(escaped)
            with self.assertRaisesRegex(ValueError, "REPARSE"):
                qa.main(["--report", escaped, "--unittest-log",
                         self.target("no.log"), "--output", self.target("qa.json")])
            self.assertFalse((target / "t6_guard_out.json").exists())
        finally:
            # os.rmdir removes the junction itself, NOT any target directory contents.
            if link.is_junction() or link.exists():
                os.rmdir(link)


if __name__ == "__main__":
    unittest.main()
