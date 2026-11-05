"""Static regression tests for the Windows PowerShell 5.1 P00 bootstrap.

These checks prevent the original CallDepthOverflow defect from returning.
They do not substitute for running the script on a Windows host.
"""
from pathlib import Path
import re
import unittest

SCRIPT = Path(__file__).resolve().parents[1] / "scripts" / "TTM_P00_WINDOWS_QA.ps1"

class P00PowerShellStaticTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.text = SCRIPT.read_text(encoding="utf-8")

    def test_no_git_function_shadows_git_executable(self):
        self.assertIsNone(re.search(r"(?im)^\s*function\s+git\s*[\(\{]", self.text))
        self.assertIn("function Invoke-TtmGit(", self.text)

    def test_git_executable_is_resolved_explicitly(self):
        self.assertIn("Get-Command -Name 'git.exe' -CommandType Application", self.text)
        self.assertIn("& $script:GitExe -C $Root @GitArgs", self.text)
        self.assertIn("& $script:GitExe -C $Worktree @GitArgs", self.text)

    def test_git_argument_array_is_bound_by_name(self):
        self.assertIn("Invoke-TtmGit -GitArgs @('init','-b','main')", self.text)
        self.assertIn("Invoke-TtmGit -GitArgs @('fetch'", self.text)
        self.assertIn("Invoke-TtmGitWorktree -GitArgs @('rev-parse','HEAD')", self.text)
        self.assertNotIn("Git @(", self.text)

    def test_workspace_boundary_and_non_destructive_actions(self):
        self.assertIn(r"D:\WORK\RESEARCH\TokenToModel-Lab", self.text)
        self.assertIn("TTM_PATH_ESCAPE", self.text)
        self.assertIn("TTM_REPARSE_POINT_REJECTED", self.text)
        for command in ("worktree','remove", "worktree','prune", "'push'", "'merge'"):
            self.assertNotIn(command, self.text)

    def test_qa_remains_non_authorizing(self):
        self.assertIn("independent_qa='NOT_PERFORMED'", self.text)
        self.assertIn("merge_authorized=$false", self.text)

if __name__ == "__main__":
    unittest.main()
