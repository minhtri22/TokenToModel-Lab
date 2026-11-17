"""Distinct test *code* for TTM matched TinyStories candidate.
Author-side, NOT an independent human/organizational reviewer.
Stdlib only; neither imports Torch nor accesses user corpus/checkpoints.
"""
import ast
import importlib.util
import json
from pathlib import Path
import re
import subprocess
import sys
import tempfile
import unittest

ROOT = Path(__file__).resolve().parents[2]
RUNNER = ROOT / "src/ttm_new_gpt_baseline/runner.py"
NOTEBOOK = ROOT / "notebooks/TTM_NEW_GPT_BASELINE_T4_ONEPACK_20261117.ipynb"
OLD_P02 = ROOT / "src/p02/transformer_core.py"
OLD_TRAIN = ROOT / "tools/pilot_t4/a2_continuous1024/t4_train_science_a2.py"
OLD_CAP = ROOT / "tools/pilot_t4/integrated/t4_capacity_smoke.py"
OLD_EVAL = ROOT / "tools/pilot_t4/integrated/t4_eval.py"
spec = importlib.util.spec_from_file_location("ttm_matched_source_under_test", RUNNER)
r = importlib.util.module_from_spec(spec)
sys.modules[spec.name] = r
spec.loader.exec_module(r)

def git_blob(path):
    relative = path.relative_to(ROOT).as_posix()
    return subprocess.check_output(["git", "rev-parse", "HEAD:" + relative],
                                   cwd=ROOT, text=True).strip()

def cells():
    nb = json.loads(NOTEBOOK.read_text("utf-8"))
    return nb, ["".join(c["source"]) for c in nb["cells"] if c["cell_type"] == "code"]

class MatchedIndependentStyleSourceQA(unittest.TestCase):
    def test_pinned_original_git_objects(self):
        objects = {
            OLD_P02: "9762343e06cf800b50574c2871ae1ed58537fb18",
            OLD_TRAIN: "76c4d0155cd0736919f41682f240b47ad3d7c428",
            OLD_CAP: "c9a6f256ba975228683ee7de2a1090e649110e97",
            OLD_EVAL: "bef006bdff173fba6d8ba4aa0ef687a1732fd7c4",
        }
        for p, expected in objects.items():
            self.assertEqual(git_blob(p), expected)
            self.assertEqual(r.PIN[p.relative_to(ROOT).as_posix()], expected)

    def test_python_cli_pure_qa(self):
        p = subprocess.run([sys.executable, str(RUNNER), "qa"],
                           text=True, capture_output=True, timeout=40)
        self.assertEqual(p.returncode, 0, p.stderr)
        self.assertIn("PASS_SOURCE_ONLY_13_OF_13", p.stdout)

    def test_notebook_json_and_compile(self):
        nb, chunks = cells()
        self.assertEqual(nb["nbformat"], 4)
        self.assertGreaterEqual(len(chunks), 3)
        for i, code in enumerate(chunks):
            compile(code, "notebook-cell-" + str(i), "exec")

    def test_notebook_defaults_fail_closed(self):
        _, chunks = cells()
        code = "\n".join(chunks)
        self.assertIn('MODE = "SOURCE_QA"', code)
        self.assertIn('RUN_ID = "UNSET_NO_Q4_GO"', code)
        self.assertIn('SOURCE_QA | NATIVE_QA | CAPACITY | PREFLIGHT | TRAIN | RESUME | COMPARE', code)
        self.assertIn("EXPLICIT_Q4_GO_FILE_MISSING", code)
        self.assertNotIn("google.colab.drive.mount(", code)

    def test_notebook_pins_actual_runner_git_blob(self):
        _, chunks = cells()
        code = "\n".join(chunks)
        self.assertIn(git_blob(RUNNER), code)
        self.assertIn("EXACT_SOURCE_BLOB_MISMATCH", code)
        self.assertIn('SOURCE_COMMIT = "59ee3f30b996405fddc087ab60102b59a021f8ea"', code)

    def test_40_step_mode_not_allowed(self):
        text = RUNNER.read_text("utf-8")
        self.assertNotIn('"steps": 40', text)
        self.assertNotIn('"vocab": 258', text)
        self.assertEqual(r.PARAMETERS, 3749376)
        self.assertEqual(r.P02_CONFIG["n_embd"], 256)

    def test_stored_budgets_and_schedules(self):
        self.assertEqual(r.TOKENS_PER_STEP, 4096)
        self.assertEqual(r.PLANS["replica_1024"]["steps"], 1024)
        self.assertEqual(r.PLANS["control_2048"]["steps"], 2048)
        self.assertEqual(r.PLANS["replica_2048"]["steps"], 2048)
        self.assertEqual(r.recipe_hash("control_2048"), r.recipe_hash("replica_2048"))
        self.assertNotEqual(r.recipe_hash("control_2048"), r.recipe_hash("replica_1024"))

    def test_old_t4_training_semantics_present(self):
        source = OLD_TRAIN.read_text("utf-8")
        self.assertIn("sample_exact_step", source)
        self.assertIn("TOKENS_PER_STEP-total", source)
        self.assertIn("loss=F.cross_entropy", source)
        self.assertIn("ignore_index=-100", source)
        self.assertIn("checkpoint_load(", source)
        self.assertIn("scaler.state_dict()", source)

    def test_no_sealed_test_access_path(self):
        source = RUNNER.read_text("utf-8")
        self.assertNotIn("TEST_64", source)
        self.assertNotIn("TinyStories-test", source)
        self.assertNotIn("torch.load(cp, map_location='cpu', weights_only=False)", source)
        self.assertIn('weights_only=True', source)

    def test_owner_q4_is_required_even_when_metadata_passes(self):
        with self.assertRaises(ValueError):
            r.assert_owner_go(None, "TRAIN_OR_RESUME", "replica_1024", "abcdefghij")
        with tempfile.TemporaryDirectory() as d:
            p = Path(d) / "go.json"
            p.write_text('{"decision":"GO_EXACT_ONE_SHOT"}')
            with self.assertRaisesRegex(ValueError, "EXACT_Q4_OWNER_DECISION"):
                r.assert_owner_go(p, "TRAIN_OR_RESUME", "replica_1024", "abcdefghij")

    def test_historic_pack_bytes_are_strict(self):
        self.assertEqual(r.DATA_SHA, "184f68b4c0c800ef3e98362c2e20e1cd35baa269e926489a475664526ecd9913")
        self.assertEqual(r.MANIFEST_SHA, "ef2e6e67d49b1d5a921b1051df329f15574f1c10cece49468acb53322d650")
        self.assertNotEqual(r.DATA_SHA, r.BPE_SHA)

    def test_wrong_step_and_wrong_recipe_fail(self):
        for step in [0, 40, 2048, 4096]:
            with self.assertRaises(ValueError):
                r.provenance_check("replica_1024", step, r.recipe_hash("replica_1024"), r.DATA_SHA)
        with self.assertRaises(ValueError):
            r.provenance_check("control_2048", 2048, r.recipe_hash("replica_1024"), r.DATA_SHA)

    def test_native_checkpoint_resume_integrity_interfaces(self):
        source = RUNNER.read_text("utf-8")
        for needle in ["durable_checkpoint(", "checked_ready(", "resume_state(",
                       'legacy.checkpoint_payload(', 'legacy.checkpoint_load(',
                       'RUN_LOCK.json', 'progress_sha256', 'checkpoint.partial']:
            self.assertIn(needle, source)

    def test_paired_bootstrap_requires_actual_two_checkpoints(self):
        source = RUNNER.read_text("utf-8")
        for needle in ["paired_bootstrap(", "np.random.default_rng", "reps=2000",
                       "PAIR_STEP_MISMATCH", "HISTORICAL_1024_CANNOT_COMPARE_TO_2048",
                       "CHECKPOINT_MODEL_OR_DATA_MISMATCH"]:
            self.assertIn(needle, source)
        self.assertNotIn("TEST", str(r.CHECKPOINTS))

    def test_checkpoint_fork_no_overwrite(self):
        with tempfile.TemporaryDirectory() as d:
            p = Path(d) / "READY.json"
            r.write_new(p, b"first")
            with self.assertRaises(FileExistsError):
                r.write_new(p, b"second")

if __name__ == "__main__":
    unittest.main()
