"""PM distinct source-only integrated E2E ABC contract QA.

Does NOT import Torch/model code, execute trainer or load any checkpoint/corpus.
Uses Git object bytes (not Windows-smudged checkout text) for exact source pins.
Scope: existing source graph, negative source drift, contract boundaries only.
"""
from __future__ import annotations

import ast
from copy import deepcopy
import hashlib
import json
from pathlib import Path
import subprocess
import unittest


ROOT = Path(__file__).resolve().parents[2]
MANIFEST = "artifacts/ttm-gpt-e2e/TTM_PM_GPT_E2E_ABC_EXACT_SOURCE_INTEGRATION_MANIFEST_20261117.json"


def git_bytes(path: str) -> bytes:
    if not isinstance(path, str) or not path or path.startswith(("/", "../")) or "\\" in path:
        raise ValueError("INVALID_GIT_SOURCE_PATH")
    if ".." in Path(path).parts:
        raise ValueError("SOURCE_PATH_TRAVERSAL")
    return subprocess.run(["git", "cat-file", "blob", "HEAD:" + path], cwd=ROOT,
                          capture_output=True, check=True).stdout


def blob_sha(data: bytes) -> str:
    return hashlib.sha1(b"blob " + str(len(data)).encode("ascii") + b"\0" + data).hexdigest()


def verified_nodes(m: dict) -> dict[str, bytes]:
    if m.get("schema") != "ttm.pm.gpt_e2e.abc_exact_source_graph.v1":
        raise ValueError("SCHEMA_MISMATCH")
    nodes = m.get("nodes")
    if not isinstance(nodes, list) or len(nodes) != 18:
        raise ValueError("NODE_SET_MISMATCH")
    if len({n["id"] for n in nodes}) != len(nodes) or len({n["path"] for n in nodes}) != len(nodes):
        raise ValueError("DUPLICATE_NODE_ID_OR_PATH")
    found = {}
    for node in nodes:
        raw = git_bytes(node["path"])
        if blob_sha(raw) != node["blob"]:
            raise ValueError("GIT_BLOB_PIN_MISMATCH:" + node["id"])
        found[node["id"]] = raw
    return found


class TestABCSourceIntegratedBaseline(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.m = json.loads(git_bytes(MANIFEST))
        cls.raw = verified_nodes(cls.m)
        cls.txt = {k: v.decode("utf-8") for k, v in cls.raw.items() if k not in ("C_SCIENCE_REGISTRY", "B_C_REMAP")}

    def test_01_exact_source_graph_18_blobs(self) -> None:
        self.assertEqual(len(self.raw), 18)
        self.assertEqual(self.m["base_main_sha"],
                         "e102d2ed3c885756b6e4354189ccbece36b75eb8")
        self.assertTrue(self.m["source_snapshot_frozen"])

    def test_02_negative_blob_tamper_rejected(self) -> None:
        changed = deepcopy(self.m)
        changed["nodes"][0]["blob"] = "0" * 40
        with self.assertRaisesRegex(ValueError, "GIT_BLOB_PIN_MISMATCH"):
            verified_nodes(changed)

    def test_03_negative_schema_or_duplicates_rejected(self) -> None:
        bad = deepcopy(self.m)
        bad["schema"] = "ttm.fake"
        with self.assertRaisesRegex(ValueError, "SCHEMA_MISMATCH"):
            verified_nodes(bad)
        bad = deepcopy(self.m)
        bad["nodes"][1]["id"] = bad["nodes"][0]["id"]
        with self.assertRaisesRegex(ValueError, "DUPLICATE_NODE"):
            verified_nodes(bad)

    def test_04_path_traversal_and_missing_sources_rejected(self) -> None:
        for p in ("../secret", "/etc/passwd", "a/../../test", r"a\\b"):
            with self.subTest(path=p), self.assertRaises(ValueError):
                git_bytes(p)

    def test_05_python_AST_compiles_without_importing_model(self) -> None:
        python_ids = ("P01_T4_BPE", "P01_T4_DATA", "P02_TRANSFORMER", "P03_TRAIN",
                      "P04_CHECKPOINT_EVAL", "B_SYNTHETIC_RUNNER", "B_SYNTHETIC_CLI",
                      "B_C_SYNTHETIC_INTERFACE", "B_C_SYNTHETIC_BRIDGE",
                      "T4_TRAIN_HISTORIC", "T4_EVAL_HISTORIC")
        for node in python_ids:
            with self.subTest(node=node):
                ast.parse(self.txt[node], filename=node)

    def test_06_P02_P03_P04_are_real_source_interfaces_not_one_trainer(self) -> None:
        p02 = self.txt["P02_TRANSFORMER"]
        p03 = self.txt["P03_TRAIN"]
        p04 = self.txt["P04_CHECKPOINT_EVAL"]
        for s in ("class GPT", "class P02Config", "def forward(", "F.cross_entropy("):
            self.assertIn(s, p02)
        for s in ("def train_fixed_batch(", "class TrainConfig", "def scheduled_lr(",
                  '"checkpoint": "NOT_SAVED_P04_NOT_OPENED"'):
            self.assertIn(s, p03)
        for s in ("def save_checkpoint_new(", "def load_checkpoint_verified(",
                  "def generate_tokens(", "def evaluate_synthetic_heldout(",
                  '"state_dict":'):
            self.assertIn(s, p04)
        # F01: source AST proves P02 uses PyTorch's default ignore_index=-100.
        # The validation blocker is P03 rejecting target y < 0, not P02 CE.
        ce_calls = [n for n in ast.walk(ast.parse(p02))
                    if isinstance(n, ast.Call) and isinstance(n.func, ast.Attribute)
                    and n.func.attr == "cross_entropy"]
        self.assertEqual(len(ce_calls), 1)
        self.assertFalse(any(k.arg == "ignore_index" for k in ce_calls[0].keywords))
        self.assertIn("torch.any(y < 0).item()", p03)
        self.assertIn("target token outside 2048 vocabulary", p03)
        self.assertIn("ignore_index=-100", self.txt["B_SYNTHETIC_RUNNER"])
        s03 = next(edge for edge in self.m["seams"] if edge["id"] == "S03")
        self.assertEqual(s03["status"], "P02_MASK_DEFAULT_VALID_P03_INPUT_ADMISSION_GAP")
        self.assertIn("P03_VALIDATE_REJECTS_NEGATIVE_TARGETS", s03["blocker"])
        self.assertIn("P02_TORCH_F_CROSS_ENTROPY_DEFAULT_IGNORE_INDEX_MINUS100",
                      s03["blocker"])
        self.assertNotIn('"optimizer":', p04)
        self.assertNotIn('"scheduler":', p04)
        self.assertNotIn('"sampler_state":', p04)

    def test_07_B_synthetic_vertical_slice_all_five_stages(self) -> None:
        cli = self.txt["B_SYNTHETIC_CLI"]
        runner = self.txt["B_SYNTHETIC_RUNNER"]
        for stage in ("def prepare(", "def run_train(", "def new_model_from_step(",
                      "def finished_model(", "def ready_checkpoint("):
            self.assertIn(stage, cli)
        self.assertIn("choices=['prepare','train','evaluate','sample']", cli)
        self.assertIn("b.load_training_checkpoint(", cli)
        self.assertIn("b.save_training_checkpoint(", cli)
        self.assertIn("b.evaluate(", cli)
        self.assertIn("b.sample(", cli)
        for s in ("def checkpoint_payload(", "def train_state(", "def train_step(",
                  "def evaluate(", "def sample(", "def read_historical_checkpoint("):
            self.assertIn(s, runner)
        self.assertIn("test_19_cli_end_to_end_and_no_overwrite",
                      self.txt["B_SYNTHETIC_TESTS"])

    def test_08_existing_CI_has_win_linux_and_synthetic_only(self) -> None:
        wf = self.txt["B_WIN_LINUX_CI"]
        self.assertIn("ubuntu-latest", wf)
        self.assertIn("windows-latest", wf)
        self.assertIn('python-version: "3.12"', wf)
        self.assertIn("python -m src.ttm_track_b.cli prepare", wf)
        self.assertIn("python -m src.ttm_track_b.cli train", wf)
        self.assertIn("python -m src.ttm_track_b.cli evaluate", wf)
        self.assertIn("python -m src.ttm_track_b.cli sample", wf)
        self.assertIn("--resume-from-step", wf)
        self.assertIn("Synthetic-only end-to-end", wf)
        self.assertIn("SYNTHETIC", self.txt["B_SYNTHETIC_CLI"])

    def test_09_synthetic_byte_identity_is_not_T4_BPE(self) -> None:
        b = self.txt["B_SYNTHETIC_RUNNER"]
        t4 = self.txt["P01_T4_BPE"]
        self.assertIn("SYNTHETIC_BYTE_IDENTITY_V1_NOT_T4_BPE", b)
        self.assertIn("EOS_ID = 256", t4)
        self.assertIn("N_MERGES = 1791", t4)
        self.assertIn("new_id=257+rank", t4)
        bc = self.txt["B_C_SYNTHETIC_INTERFACE"]
        self.assertIn("PAD, BOS, SYS, USER, ASSIST, EOT, EOS = 257, 258, 259, 260, 261, 262, 256", bc)
        self.assertIn("INCOMPATIBLE_DIRECT", json.dumps(self.m["seams"]))

    def test_10_B_bpb_not_token_to_byte_T4_mapper(self) -> None:
        b = self.txt["B_SYNTHETIC_RUNNER"]
        self.assertIn('totals["utf8_bytes"] += int(non_eos.sum().item())', b)
        self.assertIn('totals["non_eos_nll_sum"]/(totals["utf8_bytes"]*math.log(2))', b)
        self.assertIn('"SYNTHETIC_BYTE_IDENTITY_V1_NOT_T4_BPE"', b)
        self.assertEqual(next(x for x in self.m["seams"] if x["id"] == "S09")["status"],
                         "DESIGN_ACK_ONLY")

    def test_11_T4_historic_checkpoint_is_other_schema(self) -> None:
        train = self.txt["T4_TRAIN_HISTORIC"]
        self.assertIn("ttm.t4.science.checkpoint.v1", train)
        self.assertIn("def checkpoint_load(", train)
        self.assertIn("def checkpoint_write(", train)
        self.assertIn("ttm.p04.model_checkpoint.v1", self.txt["P04_CHECKPOINT_EVAL"])
        self.assertIn("ttm.track_b.synthetic.train_checkpoint.v1", self.txt["B_SYNTHETIC_RUNNER"])
        self.assertIn("PACK_SHA_VS_TOKENIZER_SHA_DOMAIN_CONFUSION",
                      json.dumps(self.m["seams"]))

    def test_12_ABC_63_fields_and_correct_A_pointer(self) -> None:
        c = json.loads(self.raw["C_SCIENCE_REGISTRY"])
        b = json.loads(self.raw["B_C_REMAP"])
        self.assertEqual(len(c["original_A_37_field_crosswalk"]), 37)
        self.assertEqual(len(c["C_B_additional_logical_requirements"]), 26)
        self.assertEqual(len(c["ASSUMPTIONS_REQUIRING_B"]), 14)
        self.assertEqual(len({r["field"] for r in b["A37"] + b["C26"]}), 63)
        self.assertEqual(len(b["B14"]), 14)
        self.assertTrue({r["field"] for r in b["B14"]}.issubset(
            {r["field"] for r in b["C26"]}))
        self.assertEqual(c["sources"]["a_requirements_git_blob"],
                         "3de320f1e734c7610fb750477803b082fefff753")
        self.assertEqual(b["input_pins"]["C_registry_blob"],
                         "364a15d305b71e0c236a27409430f1e27e14aa70")

    def test_13_A_is_external_and_owner_execution_denied(self) -> None:
        m = self.m
        self.assertEqual(len(m["external_branch_only"]), 2)
        self.assertTrue(all(ref["runtime"] for ref in m["external_branch_only"]))
        self.assertFalse(any(m["owner_GO"].values()))
        for key in ("real_source_access", "model_or_checkpoint_execution"):
            self.assertIs(m[key], False)
        self.assertEqual(m["gate_matrix"]["E1_SYNTHETIC_VERTICAL_SLICE"],
                         "PASS_PREEXISTING_B_SYNTHETIC_ONLY")
        self.assertTrue(m["gate_matrix"]["E2_REAL_T4_SOURCE_DATA_CHECKPOINT"].startswith("HOLD"))

    def test_14_edges_are_exact_and_no_silent_go(self) -> None:
        m = self.m
        ids = {r["id"] for r in m["nodes"]} | {r["id"] for r in m["external_branch_only"]}
        edges = m["seams"]
        self.assertEqual(len(edges), 12)
        self.assertEqual(len({edge["id"] for edge in edges}), 12)
        self.assertTrue(all(edge["from"] in ids and edge["to"] in ids for edge in edges))
        self.assertFalse(any(edge["status"] in ("GO", "PASS_REAL_SCIENCE") for edge in edges))
        self.assertTrue(any(e["status"] == "INCOMPATIBLE_DIRECT" for e in edges))


    def test_15_external_A_refs_bound_to_exact_authoritative_git_pins(self) -> None:
        # External branches are not checked out by CI. Verify declared exact
        # source/evidence pointer values and C registry linkage in main; the
        # independent PM reviewer separately reads external GitHub Git blobs.
        a = {e["id"]: e for e in self.m["external_branch_only"]}
        self.assertEqual(set(a), {"A_I1_MEASUREMENT", "A_V4_RELEASE_DESIGN"})
        i1, v4 = a["A_I1_MEASUREMENT"], a["A_V4_RELEASE_DESIGN"]
        self.assertEqual(i1["branch_commit"],
                         "ec197b5f00d3a037420390edd11ee55047e1d37f")
        self.assertEqual(i1["source_path"],
                         "tools/pilot_t4/direct_failure_diag_q001/track_a_m0_v3/q001_m0_goldblind.py")
        self.assertEqual(i1["source_git_blob"],
                         "46009c78b52a7bcf4c996e0bc866297d4d5ba161")
        self.assertEqual(i1["evidence_commit"],
                         "e3e1c802815f4db1534e92d9848d6015eb9203cc")
        self.assertEqual(i1["evidence_git_blob"],
                         "7d0ea908d3f52169fc6710ad06115316e84ae343")
        self.assertTrue(i1["evidence_path"].endswith("/REVIEW.md"))
        self.assertEqual(v4["branch_commit"],
                         "7639a53b9d76e16abfa4211cf239c5c3e9d6c940")
        self.assertEqual(v4["accepted_design_source_commit"],
                         "e6746184603f038b49d1e7d472367b6354474ba2")
        self.assertEqual(v4["requirements_path"],
                         "docs/coordination/ttm-abc/track-a/A_TO_BC_REQUIREMENTS.md")
        self.assertEqual(v4["requirements_git_blob"],
                         "3de320f1e734c7610fb750477803b082fefff753")
        c_registry = json.loads(self.raw["C_SCIENCE_REGISTRY"])
        self.assertEqual(c_registry["sources"]["a_requirements_git_blob"],
                         v4["requirements_git_blob"])
        self.assertIn("does not fetch external A objects",
                      self.m["external_verification_scope"])

    def test_16_report_manifest_receipt_scope_consistency(self) -> None:
        report_path = ("docs/architecture/"
                       "TTM_PM_GPT_END_TO_END_BASELINE_ABC_INTEGRATION_ONEPACK_20261117.md")
        receipt_path = ("artifacts/ttm-gpt-e2e/"
                        "TTM_PM_GPT_E2E_ABC_SOURCE_INTEGRATION_QA_RECEIPT_20261117.json")
        report = git_bytes(report_path).decode("utf-8")
        receipt = json.loads(git_bytes(receipt_path))
        self.assertIn("P02 gọi `F.cross_entropy` không override `ignore_index`", report)
        self.assertIn("P03 `_validate` từ chối mọi target âm", report)
        self.assertNotIn("P02 `forward(tokens,targets)` dùng CE mặc định **không ignore -100**", report)
        self.assertIn("`PRE_QA_CANDIDATE`", report)
        self.assertIn("PRE_QA_SOURCE_SNAPSHOT_READY", self.m["gate_matrix"]["E0_SOURCE_GRAPH"])
        self.assertEqual(receipt["base_main"], self.m["base_main_sha"])
        self.assertEqual(receipt["source_scope"]["report_path"], report_path)
        self.assertEqual(receipt["source_scope"]["manifest_path"], MANIFEST)
        self.assertEqual(receipt["source_scope"]["source_nodes"], len(self.m["nodes"]))
        self.assertEqual(receipt["source_scope"]["seam_count"], len(self.m["seams"]))
        self.assertTrue(receipt["source_scope"]["snapshot_only_no_real_execution"])
        self.assertEqual(receipt["QA"]["latest_prior_exact_head_run"], 44060530115)
        self.assertEqual(receipt["QA"]["latest_prior_exact_head_sha"],
                         "383e2a4a858069e05a290d7448e607a01853ae04")
        self.assertIn("current PR HEAD workflow result", receipt["QA"]["CI_authority_note"])
        self.assertTrue(receipt["PM_decision"]["no_new_QuestionGate"])
        self.assertTrue(receipt["PM_decision"]["A_I2"].startswith("HOLD"))

    def test_17_workflow_follows_report_and_excludes_model_execution(self) -> None:
        path = ".github/workflows/ttm-pm-gpt-e2e-abc-source-qa-py312.yml"
        wf = git_bytes(path).decode("utf-8")
        self.assertIn("docs/architecture/TTM_PM_GPT_END_TO_END_BASELINE_ABC_INTEGRATION_ONEPACK_20261117.md", wf)
        self.assertIn("artifacts/ttm-gpt-e2e/**", wf)
        self.assertIn("tests/ttm_pm_gpt_e2e_source/**", wf)
        self.assertIn("windows-latest", wf)
        self.assertIn("ubuntu-latest", wf)
        self.assertIn("python -S -B -m unittest discover", wf)
        self.assertNotIn("pip install", wf)
        self.assertNotIn("python -m src.ttm_track_b.cli train", wf)


if __name__ == "__main__":
    unittest.main()
