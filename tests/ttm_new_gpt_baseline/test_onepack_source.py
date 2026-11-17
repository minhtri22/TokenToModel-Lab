"""Independent-from-author-script contract checks; stdlib, no Torch or corpus."""
import importlib.util
import json
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest

ROOT = Path(__file__).resolve().parents[2]
RUNNER = ROOT / "src/ttm_new_gpt_baseline/runner.py"
NB = ROOT / "notebooks/TTM_NEW_GPT_BASELINE_T4_ONEPACK_20261117.ipynb"
spec = importlib.util.spec_from_file_location("ttm_new_gpt_baseline", RUNNER)
r = importlib.util.module_from_spec(spec)
sys.modules[spec.name] = r
spec.loader.exec_module(r)

class ExternalSourceQA(unittest.TestCase):
    def test_runner_cli_fresh_stdlib_qa(self):
        p = subprocess.run([sys.executable, str(RUNNER), "qa"],
                           capture_output=True, text=True, timeout=20)
        self.assertEqual(p.returncode, 0, p.stderr)
        self.assertIn("PASS_SOURCE_ONLY_10_OF_10", p.stdout)
    def test_colab_notebook_json_ast(self):
        note = json.loads(NB.read_text("utf-8"))
        self.assertEqual(note["nbformat"], 4)
        codes = [c for c in note["cells"] if c["cell_type"] == "code"]
        self.assertEqual(len(codes), 3)
        for i, cell in enumerate(codes):
            compile("".join(cell["source"]), "notebook-cell-"+str(i), "exec")
        self.assertIn('MODE = "QA"', "".join(codes[0]["source"]))
        self.assertIn('RUN_ID = "UNSET_NO_Q4_GO"', "".join(codes[0]["source"]))
    def test_notebook_exact_runner_git_blob(self):
        code = "\n".join("".join(c["source"]) for c in json.loads(NB.read_text("utf-8"))["cells"] if c["cell_type"] == "code")
        self.assertIn(r.git_blob(RUNNER.read_bytes()), code)
        self.assertIn("RUNNER_SOURCE_DRIFT_FAIL_CLOSED", code)
        self.assertIn("Q4_GO_MISSING", code)
    def test_no_weights_import_or_cuda_in_qa(self):
        source = RUNNER.read_text("utf-8")
        self.assertNotIn("torch.load(", source)
        self.assertNotIn("google.colab.drive", source)
        self.assertIn('if a.action == "qa":', source)
        self.assertIn('if a.action == "preflight":', source)
    def test_no_implicit_owner_go(self):
        self.assertEqual(r.CFG["steps"], 40)
        self.assertEqual(r.P02_BLOB, "9762343e06cf800b50574c2871ae1ed58537fb18")
        self.assertEqual(r.tokenizer_info()["vocab"], 258)
        with self.assertRaisesRegex(ValueError, "REAL_TRAIN_REQUIRES"):
            r.train_real(type("Args", (), {"manifest":None,"data_root":None,
                "probe_receipt":None,"owner_go":None,"run_id":None})())
    def test_training_output_one_shot(self):
        with tempfile.TemporaryDirectory() as d:
            path = Path(d) / "run"
            r.unique_new_dir(path)
            with self.assertRaises(FileExistsError):
                r.unique_new_dir(path)
    def test_val_bpb_is_byte_domain(self):
        self.assertAlmostEqual(r.score_math(2.0 * 4 * 0.6931471805599453, 4), 2.0)
        self.assertEqual(r.EOS, 256)
        self.assertEqual(r.BOS, 257)

if __name__ == "__main__":
    unittest.main()
