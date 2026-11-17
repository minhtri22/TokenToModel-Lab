"""TTM NEW_GPT_BASELINE v1. Python 3.12; source QA is stdlib-only.
Fresh byte-identity UTF-8 tokenizer, separate from historic T4 BPE and BC-v2.
Real training is inert unless an externally reviewed Q4 owner GO file is supplied.
"""
from __future__ import annotations
import argparse
import hashlib
import importlib.util
import json
import math
import os
from pathlib import Path, PurePosixPath
import re
import subprocess
import sys
import tempfile
import time
import unittest
import urllib.request

P02_BLOB = "9762343e06cf800b50574c2871ae1ed58537fb18"
P02_URL = ("https://raw.githubusercontent.com/minhtri22/TokenToModel-Lab/"
           "59ee3f30b996405fddc087ab60102b59a021f8ea/src/p02/transformer_core.py")
SCHEMA = "ttm.newgpt.data.v1"
BOS, EOS, VOCAB = 257, 256, 258
CFG = {"schema": "ttm.newgpt.config.v1", "seed": 20261117, "context": 128,
       "n_embd": 128, "n_layer": 2, "n_head": 4, "batch_windows": 4,
       "steps": 40, "lr": 0.0003, "max_wall_seconds": 900,
       "max_gpu_reserved_mib": 8192, "min_gpu_free_mib": 10240}
RIGHTS = {"OWNER_AUTHORED", "LICENSED_TRAINING", "PUBLIC_DOMAIN"}
FIELDS = {"path", "split", "family", "sha256", "rights_basis",
          "rights_reference", "pii_reviewed"}

def canonical(obj):
    return (json.dumps(obj, sort_keys=True, ensure_ascii=False,
                       separators=(",", ":")) + "\n").encode("utf-8")

def sha(raw):
    return hashlib.sha256(raw).hexdigest()

def sha_file(path):
    h = hashlib.sha256()
    with Path(path).open("rb") as f:
        for block in iter(lambda: f.read(1024 * 1024), b""):
            h.update(block)
    return h.hexdigest()

def git_blob(data):
    return hashlib.sha1(b"blob " + str(len(data)).encode() + b"\0" + data).hexdigest()

def check_sha(s):
    if not isinstance(s, str) or re.fullmatch("[0-9a-f]{64}", s) is None:
        raise ValueError("INVALID_SHA256")
    return s

def own_blob():
    return git_blob(Path(__file__).read_bytes())

def tokenizer_info():
    return {"schema": "ttm.newgpt.utf8_byte_identity.v1", "vocab": VOCAB,
            "byte_range": [0, 255], "eos": EOS, "bos": BOS,
            "training": "NOT_REQUIRED_DETERMINISTIC_BYTE_MAPPING",
            "old_t4_bpe_compatible": False, "bc_v2_direct_alias": False}

def validate_data(root, manifest, read_bytes=True):
    root = Path(root).resolve(strict=True)
    mf = Path(manifest).resolve(strict=True)
    if not root.is_dir() or not mf.is_file() or mf.is_symlink():
        raise ValueError("INVALID_DATA_ROOT_OR_MANIFEST")
    raw_manifest = mf.read_bytes()
    spec = json.loads(raw_manifest.decode("utf-8", "strict"))
    if not isinstance(spec, dict) or set(spec) != {"schema", "records"} or spec["schema"] != SCHEMA:
        raise ValueError("MANIFEST_SCHEMA")
    if not isinstance(spec["records"], list) or len(spec["records"]) < 2 or len(spec["records"]) > 10000:
        raise ValueError("MANIFEST_RECORD_COUNT")
    seen_paths, seen_sha, families, splits = set(), {}, {}, {"TRAIN": [], "VAL": []}
    total = 0
    for r in spec["records"]:
        if not isinstance(r, dict) or set(r) != FIELDS:
            raise ValueError("RECORD_SCHEMA")
        name, split, fam = r["path"], r["split"], r["family"]
        if split not in splits or "TEST" in str(name).upper().split("/"):
            raise ValueError("TEST_FORBIDDEN")
        if not isinstance(name, str) or "\\" in name:
            raise ValueError("UNSAFE_PATH")
        pure = PurePosixPath(name)
        if pure.is_absolute() or not pure.parts or any(x in ("..", ".") for x in name.split("/")):
            raise ValueError("UNSAFE_PATH")
        if not isinstance(fam, str) or re.fullmatch("[A-Za-z0-9_-]{1,80}", fam) is None:
            raise ValueError("FAMILY_ID")
        if name in seen_paths:
            raise ValueError("DUPLICATE_PATH")
        seen_paths.add(name)
        if fam in families and families[fam] != split:
            raise ValueError("FAMILY_SPLIT_LEAK")
        families[fam] = split
        check_sha(r["sha256"])
        if r["sha256"] in seen_sha and seen_sha[r["sha256"]] != split:
            raise ValueError("BYTE_HASH_SPLIT_LEAK")
        seen_sha[r["sha256"]] = split
        if r["rights_basis"] not in RIGHTS or r["pii_reviewed"] is not True:
            raise ValueError("RIGHTS_OR_PII_ATTESTATION_MISSING")
        if not isinstance(r["rights_reference"], str) or len(r["rights_reference"].strip()) < 5:
            raise ValueError("RIGHTS_REFERENCE_MISSING")
        p = root.joinpath(*pure.parts)
        if p.is_symlink() or any(z.is_symlink() for z in p.parents if z != root and root in z.parents):
            raise ValueError("SYMLINK_FORBIDDEN")
        p = p.resolve(strict=True)
        if not p.is_file() or not p.is_relative_to(root) or p.stat().st_size == 0 or p.stat().st_size > 2_000_000:
            raise ValueError("FILE_SCOPE_OR_SIZE")
        total += p.stat().st_size
        if total > 16_000_000:
            raise ValueError("TOTAL_BYTES_CAP")
        if sha_file(p) != r["sha256"]:
            raise ValueError("SOURCE_BYTE_SHA_MISMATCH")
        raw = p.read_bytes() if read_bytes else b""
        if read_bytes:
            raw.decode("utf-8", "strict")
            splits[split].append((fam, raw))
        else:
            splits[split].append((fam, None))
    if any(not v for v in splits.values()):
        raise ValueError("TRAIN_VAL_REQUIRED")
    return {"manifest_sha256": sha(raw_manifest), "data_bytes": total,
            "records": len(seen_paths), "families": len(families),
            "owner_rights_attested_only": True, "distinct_rights_qa": "UNVERIFIED"}, splits

def windows(splits, context):
    out = {}
    for split, docs in splits.items():
        ws = []
        for _, raw in docs:
            ids = [BOS, *raw, EOS]
            for i in range(0, len(ids) - 1, context):
                n = min(context, len(ids) - 1 - i)
                x, y = ids[i:i+n], ids[i+1:i+1+n]
                if len(x) != n or len(y) != n:
                    raise AssertionError("MISALIGNED")
                ws.append((x + [BOS] * (context - n),
                           y + [-100] * (context - n)))
        out[split] = ws
    return out

def score_math(nll_nats, utf8_bytes):
    if (type(nll_nats) not in (int, float) or not math.isfinite(nll_nats)
            or nll_nats < 0 or type(utf8_bytes) is not int or utf8_bytes <= 0):
        raise ValueError("INVALID_BYTE_METRIC")
    return nll_nats / (math.log(2) * utf8_bytes)

def load_p02():
    # Import only after explicit PROBE or owner-authorized TRAIN; no old checkpoints.
    with urllib.request.urlopen(P02_URL, timeout=25) as response:
        source = response.read(500_000)
    if git_blob(source) != P02_BLOB:
        raise ValueError("P02_GIT_BLOB_MISMATCH")
    folder = Path(tempfile.mkdtemp(prefix="ttm-newgpt-p02-"))
    path = folder / "transformer_core.py"
    path.write_bytes(source)
    spec = importlib.util.spec_from_file_location("ttm_p02_pinned_newgpt", path)
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module

def runtime():
    if sys.version_info[:2] != (3, 12):
        raise RuntimeError("PYTHON312_REQUIRED")
    os.environ.setdefault("CUBLAS_WORKSPACE_CONFIG", ":4096:8")
    import torch
    if not torch.cuda.is_available() or "T4" not in torch.cuda.get_device_name(0):
        raise RuntimeError("ACTUAL_TESLA_T4_REQUIRED")
    free, total = torch.cuda.mem_get_info()
    if free < CFG["min_gpu_free_mib"] * 1024 ** 2:
        raise RuntimeError("GPU_FREE_MEMORY_TOO_LOW")
    torch.manual_seed(CFG["seed"])
    torch.cuda.manual_seed_all(CFG["seed"])
    torch.use_deterministic_algorithms(True)
    return torch, {"gpu": torch.cuda.get_device_name(0),
                   "free_mib_pre": int(free / 1048576),
                   "total_mib": int(total / 1048576),
                   "torch": str(torch.__version__), "python": sys.version.split()[0]}

def model_and_optimizer(torch, module):
    c = module.P02Config(vocab_size=VOCAB, max_seq_len=CFG["context"],
                         n_embd=CFG["n_embd"], n_layer=CFG["n_layer"],
                         n_head=CFG["n_head"], norm_type="layernorm")
    m = module.GPT(c).to("cuda")
    opt = torch.optim.AdamW(m.parameters(), lr=CFG["lr"], betas=(0.9, 0.95), weight_decay=0.1)
    return m, opt

def batch(torch, samples, indexes):
    xs = torch.tensor([samples[i][0] for i in indexes], dtype=torch.long, device="cuda")
    ys = torch.tensor([samples[i][1] for i in indexes], dtype=torch.long, device="cuda")
    return xs, ys

def one_step(torch, m, opt, x, y):
    import torch.nn.functional as F
    m.train()
    opt.zero_grad(set_to_none=True)
    logits, _ = m(x)
    loss = F.cross_entropy(logits.float().reshape(-1, VOCAB), y.reshape(-1),
                           ignore_index=-100, reduction="sum")
    count = (y != -100).sum()
    if int(count.item()) == 0:
        raise ValueError("NO_VALID_TARGETS")
    (loss / count).backward()
    torch.nn.utils.clip_grad_norm_(m.parameters(), max_norm=1.0)
    opt.step()
    return float((loss / count).detach().item())

def resource_probe(out):
    torch, env = runtime()
    module = load_p02()
    m, opt = model_and_optimizer(torch, module)
    torch.cuda.reset_peak_memory_stats()
    sampler = torch.Generator(device="cpu").manual_seed(CFG["seed"])
    start = time.monotonic()
    losses = []
    for i in range(3):
        ids = torch.randint(0, 256, (CFG["batch_windows"], CFG["context"] + 1),
                            generator=sampler, dtype=torch.long)
        x, y = ids[:, :-1].to("cuda"), ids[:, 1:].to("cuda")
        losses.append(one_step(torch, m, opt, x, y))
    torch.cuda.synchronize()
    elapsed = time.monotonic() - start
    reserved = torch.cuda.max_memory_reserved() // 1048576
    if elapsed > 90 or reserved > CFG["max_gpu_reserved_mib"] or not all(math.isfinite(v) for v in losses):
        raise RuntimeError("RESOURCE_PROBE_GUARD_FAIL")
    receipt = {"schema": "ttm.newgpt.t4_probe.v1",
               "status": "PASS_SYNTHETIC_RESOURCE_PROBE_SCOPED",
               "source_blob": own_blob(), "p02_blob": P02_BLOB,
               "config_sha256": sha(canonical(CFG)), "env": env,
               "steps": 3, "elapsed_s": elapsed, "peak_reserved_mib": reserved,
               "max_gpu_reserved_mib": CFG["max_gpu_reserved_mib"],
               "science_executed": False, "real_training_executed": False,
               "owner_q4": "HOLD"}
    Path(out).write_bytes(canonical(receipt))
    print(json.dumps(receipt, ensure_ascii=False))

def evaluate(torch, m, val_windows, raw_byte_count):
    import torch.nn.functional as F
    m.eval()
    nll = 0.0
    observed = 0
    with torch.no_grad():
        for x_raw, y_raw in val_windows:
            x = torch.tensor([x_raw], dtype=torch.long, device="cuda")
            y = torch.tensor([y_raw], dtype=torch.long, device="cuda")
            logits, _ = m(x)
            row = F.cross_entropy(logits.float().reshape(-1, VOCAB), y.reshape(-1),
                                  ignore_index=-100, reduction="none")
            mask = (y.reshape(-1) >= 0) & (y.reshape(-1) < 256)
            nll += float(row[mask].sum().item())
            observed += int(mask.sum().item())
    if observed != raw_byte_count:
        raise ValueError("VAL_BYTE_TARGET_COVERAGE_MISMATCH")
    return {"text_nll_nats": nll, "val_text_bytes": observed,
            "val_bpb": score_math(nll, observed),
            "stop_eos_excluded_from_primary": True,
            "a_c_independent_gold": "NOT_VERIFIED"}

def unique_new_dir(path):
    p = Path(path)
    if p.is_symlink() or p.exists() or p.parent.is_symlink():
        raise FileExistsError("ONE_SHOT_OUTPUT_MUST_NOT_EXIST")
    p.parent.mkdir(parents=True, exist_ok=True)
    p.mkdir(exist_ok=False)
    return p

def train_real(args):
    if not args.manifest or not args.data_root or not args.probe_receipt or not args.owner_go or not args.run_id:
        raise ValueError("REAL_TRAIN_REQUIRES_EXACT_ONEPACK_INPUTS")
    if not re.fullmatch("[A-Za-z0-9_-]{4,80}", args.run_id):
        raise ValueError("BAD_RUN_ID")
    meta, corpus = validate_data(args.data_root, args.manifest)
    probe_raw = Path(args.probe_receipt).read_bytes()
    probe = json.loads(probe_raw)
    decision = json.loads(Path(args.owner_go).read_text("utf-8"))
    expected_decision = {"schema": "ttm.newgpt.owner_q4.v1",
       "decision": "Q4_GO_NEW_GPT_SINGLE_RUN", "run_id": args.run_id,
       "runner_git_blob": own_blob(), "p02_git_blob": P02_BLOB,
       "config_sha256": sha(canonical(CFG)), "manifest_sha256": meta["manifest_sha256"],
       "probe_sha256": sha(probe_raw)}
    if decision != expected_decision:
        raise ValueError("OWNER_Q4_GO_EXACT_PACKET_REQUIRED")
    if (probe.get("schema") != "ttm.newgpt.t4_probe.v1"
            or probe.get("status") != "PASS_SYNTHETIC_RESOURCE_PROBE_SCOPED"
            or probe.get("source_blob") != own_blob()
            or probe.get("config_sha256") != expected_decision["config_sha256"]
            or probe.get("p02_blob") != P02_BLOB
            or probe.get("peak_reserved_mib", 999999) > CFG["max_gpu_reserved_mib"]):
        raise ValueError("RESOURCE_PROBE_NOT_MATCHED")
    torch, env = runtime()
    module = load_p02()
    data = windows(corpus, CFG["context"])
    expected_val_bytes = sum(len(raw) for _, raw in corpus["VAL"])
    generator = torch.Generator(device="cpu").manual_seed(CFG["seed"])
    model, optimizer = model_and_optimizer(torch, module)
    # This is an operator-supplied GO interlock, not cryptographic proof of owner authority.
    out = unique_new_dir(args.out)
    (out / "INPUT_PINS.json").write_bytes(canonical({
        "schema": "ttm.newgpt.run_inputs.v1", "run_id": args.run_id,
        "config_sha256": expected_decision["config_sha256"],
        "manifest_sha256": meta["manifest_sha256"],
        "probe_sha256": expected_decision["probe_sha256"],
        "source_blob": own_blob(), "p02_blob": P02_BLOB,
        "tokenizer_sha256": sha(canonical(tokenizer_info())),
        "rights": "OWNER_ATTESTED_ONLY_DISTINCT_QA_PENDING",
        "go": "OPERATOR_INPUT_NOT_INDEPENDENTLY_AUTHENTICATED"}))
    start = time.monotonic()
    losses = []
    torch.cuda.reset_peak_memory_stats()
    for step in range(1, CFG["steps"] + 1):
        if time.monotonic() - start > CFG["max_wall_seconds"]:
            raise TimeoutError("REAL_TRAIN_TIME_CAP")
        ids = torch.randint(len(data["TRAIN"]), (CFG["batch_windows"],), generator=generator).tolist()
        x, y = batch(torch, data["TRAIN"], ids)
        loss = one_step(torch, model, optimizer, x, y)
        if not math.isfinite(loss):
            raise ValueError("NONFINITE_TRAIN_LOSS")
        losses.append(loss)
        if torch.cuda.max_memory_reserved() // 1048576 > CFG["max_gpu_reserved_mib"]:
            raise MemoryError("GPU_RESERVED_CAP")
    ev = evaluate(torch, model, data["VAL"], expected_val_bytes)
    # Checkpoint contains fresh model + optimizer + sampler; never imports historical T4.
    checkpoint = {"schema": "ttm.newgpt.train_checkpoint.v1", "step": CFG["steps"],
        "config": CFG, "runner_git_blob": own_blob(),
        "data_manifest_sha256": meta["manifest_sha256"],
        "tokenizer_sha256": sha(canonical(tokenizer_info())),
        "model": model.state_dict(), "optimizer": optimizer.state_dict(),
        "sampler_state": generator.get_state(), "torch_rng": torch.get_rng_state(),
        "cuda_rng": torch.cuda.get_rng_state_all()}
    tmp = out / "checkpoint.pt.partial"
    torch.save(checkpoint, tmp)
    ck = out / "checkpoint.pt"
    os.replace(tmp, ck)
    digest = sha_file(ck)
    (out / "READY.json").write_bytes(canonical({
        "schema": "ttm.newgpt.ready.v1", "checkpoint": "checkpoint.pt",
        "checkpoint_sha256": digest, "checkpoint_bytes": ck.stat().st_size,
        "step": CFG["steps"], "manifest_sha256": meta["manifest_sha256"],
        "config_sha256": expected_decision["config_sha256"]}))
    model.eval()
    samples = [BOS]
    with torch.no_grad():
        for _ in range(24):
            t = torch.tensor([samples[-CFG["context"] :]], dtype=torch.long, device="cuda")
            logits, _ = model(t)
            nxt = int(logits[0, -1].argmax().item())
            samples.append(nxt)
            if nxt == EOS:
                break
    report = {"schema": "ttm.newgpt.run_result.v1", "status": "TRAIN_EXECUTED_OPERATOR_GO",
              "run_id": args.run_id, "checkpoint_sha256": digest,
              "checkpoint_bytes": ck.stat().st_size,
              "config_sha256": expected_decision["config_sha256"],
              "manifest_sha256": meta["manifest_sha256"],
              "source_blob": own_blob(), "env": env,
              "train_steps": CFG["steps"], "train_first_loss": losses[0],
              "train_last_loss": losses[-1], "val": ev,
              "sample_token_ids": samples, "sample_interpretation": "UNVERIFIED",
              "max_reserved_mib": torch.cuda.max_memory_reserved() // 1048576,
              "wall_s": time.monotonic()-start,
              "independent_qa": "NOT_EXECUTED",
              "science_claim": "NONE_UNTIL_DISTINCT_QA"}
    (out / "RUN_RESULT.json").write_bytes(canonical(report))
    print(json.dumps(report, ensure_ascii=False))

class SourceQA(unittest.TestCase):
    def fixture(self):
        tmp = tempfile.TemporaryDirectory()
        root = Path(tmp.name)
        (root / "train").mkdir()
        (root / "val").mkdir()
        docs = [("train/one.txt", "TRAIN", "family_a", "Hà Nội\n".encode()),
                ("val/one.txt", "VAL", "family_b", "Đà Nẵng\n".encode())]
        records = []
        for name, split, family, raw in docs:
            (root / name).write_bytes(raw)
            records.append({"path": name, "split": split, "family": family,
                "sha256": sha(raw), "rights_basis": "OWNER_AUTHORED",
                "rights_reference": "qa-original-fixture", "pii_reviewed": True})
        path = root / "manifest.json"
        path.write_bytes(canonical({"schema": SCHEMA, "records": records}))
        return tmp, root, path, records
    def test_fixture_and_byte_coverage(self):
        temp, root, path, _ = self.fixture()
        with temp:
            meta, docs = validate_data(root, path)
            w = windows(docs, 8)
            self.assertEqual(sum(sum(0 <= z < 256 for z in ys) for _, ys in w["VAL"]), len("Đà Nẵng\n".encode()))
            self.assertEqual(meta["records"], 2)
    def test_family_leak(self):
        tmp, root, path, r = self.fixture()
        with tmp:
            r[1]["family"] = r[0]["family"]
            path.write_bytes(canonical({"schema": SCHEMA, "records": r}))
            with self.assertRaisesRegex(ValueError, "FAMILY_SPLIT_LEAK"):
                validate_data(root, path)
    def test_duplicate_byte_leak(self):
        tmp, root, path, r = self.fixture()
        with tmp:
            raw = (root / r[0]["path"]).read_bytes()
            (root / r[1]["path"]).write_bytes(raw)
            r[1]["sha256"] = sha(raw)
            path.write_bytes(canonical({"schema": SCHEMA, "records": r}))
            with self.assertRaisesRegex(ValueError, "BYTE_HASH_SPLIT_LEAK"):
                validate_data(root, path)
    def test_rights(self):
        tmp, root, path, r = self.fixture()
        with tmp:
            r[0]["pii_reviewed"] = False
            path.write_bytes(canonical({"schema": SCHEMA, "records": r}))
            with self.assertRaisesRegex(ValueError, "RIGHTS_OR_PII"):
                validate_data(root, path)
    def test_sha_tampering(self):
        tmp, root, path, _ = self.fixture()
        with tmp:
            (root / "val/one.txt").write_text("changed", encoding="utf-8")
            with self.assertRaisesRegex(ValueError, "SOURCE_BYTE_SHA"):
                validate_data(root, path)
    def test_test_forbidden(self):
        tmp, root, path, r = self.fixture()
        with tmp:
            r[1]["split"] = "TEST"
            path.write_bytes(canonical({"schema": SCHEMA, "records": r}))
            with self.assertRaisesRegex(ValueError, "TEST_FORBIDDEN"):
                validate_data(root, path)
    def test_path_traversal(self):
        tmp, root, path, r = self.fixture()
        with tmp:
            r[0]["path"] = "../outside.txt"
            path.write_bytes(canonical({"schema": SCHEMA, "records": r}))
            with self.assertRaisesRegex(ValueError, "UNSAFE_PATH"):
                validate_data(root, path)
    def test_utf8(self):
        tmp, root, path, r = self.fixture()
        with tmp:
            bad = b"\xff"
            (root / r[0]["path"]).write_bytes(bad)
            r[0]["sha256"] = sha(bad)
            path.write_bytes(canonical({"schema": SCHEMA, "records": r}))
            with self.assertRaises(UnicodeDecodeError):
                validate_data(root, path)
    def test_byte_metric(self):
        self.assertAlmostEqual(score_math(math.log(2)*7, 7), 1)
        for a, b in [(float("nan"), 2), (2, 0), (-1, 4)]:
            with self.assertRaises(ValueError):
                score_math(a, b)
    def test_bos_eos_domain(self):
        self.assertEqual((BOS, EOS, VOCAB), (257, 256, 258))
        self.assertFalse(tokenizer_info()["old_t4_bpe_compatible"])
        self.assertFalse(tokenizer_info()["bc_v2_direct_alias"])

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("action", choices=["qa", "preflight", "probe", "train"])
    ap.add_argument("--data-root")
    ap.add_argument("--manifest")
    ap.add_argument("--out")
    ap.add_argument("--owner-go")
    ap.add_argument("--probe-receipt")
    ap.add_argument("--run-id")
    a = ap.parse_args()
    if a.action == "qa":
        suite = unittest.defaultTestLoader.loadTestsFromTestCase(SourceQA)
        result = unittest.TextTestRunner(verbosity=2).run(suite)
        if not result.wasSuccessful():
            sys.exit(1)
        print("PASS_SOURCE_ONLY_10_OF_10")
    elif a.action == "preflight":
        m, _ = validate_data(a.data_root, a.manifest, read_bytes=False)
        print(json.dumps({"schema": "ttm.newgpt.preflight.v1",
                          "status": "OWNER_RIGHTS_ATTESTATION_SOURCE_SCAN_ONLY",
                          "data": m, "config_sha256": sha(canonical(CFG)),
                          "runner_git_blob": own_blob(), "q4": "HOLD"}, ensure_ascii=False))
    elif a.action == "probe":
        if not a.out:
            raise ValueError("OUT_REQUIRED")
        p = Path(a.out)
        if p.exists() or p.is_symlink():
            raise FileExistsError("ONE_SHOT_PROBE_RECEIPT")
        resource_probe(p)
    else:
        train_real(a)

if __name__ == "__main__":
    main()
