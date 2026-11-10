#!/usr/bin/env python3
"""Offline only: import runner, assert pins and reject malformed logits."""
import ast,importlib.util,json,tempfile,unittest
from pathlib import Path
PATH=Path(__file__).resolve().parent
SOURCE=(PATH/"run_isolated_ollama_fl01_fl04_once.py").read_text("utf-8")
spec=importlib.util.spec_from_file_location("ttm_full_logits_local_qa",PATH/"run_isolated_ollama_fl01_fl04_once.py")
m=importlib.util.module_from_spec(spec);spec.loader.exec_module(m)
class FrozenCaptureQA(unittest.TestCase):
    def test_python_syntax(self):ast.parse(SOURCE)
    def test_fixtures(self):
        self.assertEqual([(x[0],len(x[2])) for x in m.FIX],[("FL01",3),("FL02",3),("FL03",3),("FL04",6)])
    def test_pinned_artifacts(self):
        self.assertEqual(m.RUNNER_SHA,"818fec27008b0a8555ecbae09c8c95e6a076d2b2fa4c26377b8bdb248232210a")
        self.assertEqual(m.REF_SHA,"1e098a643c9bce66431adf3dc0296ce6b628731d33c4532753d2f2acd664d082")
    def test_isolated_port(self):self.assertEqual(m.PORT,12651)
    def test_missing_rows_rejected(self):
        with tempfile.TemporaryDirectory() as d:
            with self.assertRaisesRegex(ValueError,"NO_RAW"):m.check_rows(Path(d)/"missing",1)
    def test_bad_ids_rejected(self):
        with tempfile.TemporaryDirectory() as d:
            f=Path(d)/"test.jsonl"
            row={"schema":"ttm.ollama.full_logits.runner_pre_sample.v1","phase":"PRE_SAMPLING_RAW_F32",
                 "fixture_id":"FL01","token_ids":[-1],"n_vocab":2048,"logits":[0.0]*2048}
            f.write_text(json.dumps(row)+"\n")
            with self.assertRaisesRegex(ValueError,"RAW_TOKEN"):m.check_rows(f,1)
    def test_wrong_vector_dim_rejected(self):
        with tempfile.TemporaryDirectory() as d:
            f=Path(d)/"test.jsonl"
            row={"schema":"ttm.ollama.full_logits.runner_pre_sample.v1","phase":"PRE_SAMPLING_RAW_F32",
                 "fixture_id":"FL01","token_ids":[97,98,99],"n_vocab":2048,"logits":[0.0]*2047}
            f.write_text(json.dumps(row)+"\n")
            with self.assertRaisesRegex(ValueError,"WRONG_SIZE"):m.check_rows(f,1)
    def test_cleanup_required_for_success(self):
        self.assertIn("OWNED_OLLAMA_PARENT_STILL_RUNNING",SOURCE)
        self.assertIn("OWNED_PROCESS_TREE_CLEANUP_COMMAND_FAILED",SOURCE)
    def test_no_replay_or_delete(self):
        self.assertNotIn("shutil.rmtree",SOURCE)
        self.assertIn("STAGE_ALREADY_EXISTS_NO_REPLAY",SOURCE)
        self.assertIn("main_changed",SOURCE)
if __name__=="__main__":unittest.main(verbosity=2)
