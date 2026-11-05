# TTM P00 independent Windows QA (read-only on Git; evidence-only writes).
# Separate fixtures from reference/phase0/test_reference.py.
# No Git worktree creation, deletion, cleanup, commit, push or merge.
from __future__ import annotations

import hashlib
import json
import os
from pathlib import Path
import platform
import re
import stat
import subprocess
import sys
import traceback
from datetime import datetime, timezone

ROOT = Path(r"D:\WORK\RESEARCH\TokenToModel-Lab")
WORKTREE = ROOT / "worktrees" / "p00-source-docs-diagrams-20261105"
LOCAL_QA = ROOT / "evidence" / "p00" / "TTM_P00_WINDOWS_LOCAL_QA_20261105T043050Z"
BASE_MAIN = "f2ed098b033431924a3cbabdc9af89d7bbd7b378"
SOURCE_COMMIT = "382da2c52d0fb4efe1cd9de5c92e68de79a52a20"
RECEIPT_SHA = "6f30d4450199d471acd5e5a9c7b8264bc8fdc653bdc3b76ba5bfa8afa47034ee"
MODEL_SHA = "821e60a6c97536bf3a251602b31dcc6b55f1c81836cffa5223ec2f063ae578ea"
CONFIG_SHA = "ffcd83863fb9c2a8959fbaaa52ccdb7bf2977d68ea6aa869880015dc0daebcbd"
REMOTE = "https://github.com/minhtri22/TokenToModel-Lab.git"
BRANCH = "feature/p00-source-docs-diagrams-20261105"


def hash_file(p: Path) -> str:
    h = hashlib.sha256()
    with p.open("rb") as f:
        for chunk in iter(lambda: f.read(1024 * 1024), b""):
            h.update(chunk)
    return h.hexdigest()


def require(value: bool, message: str) -> None:
    if not value:
        raise AssertionError(message)


def safe_path(path: Path, root: Path = ROOT) -> Path:
    # Check lexical containment first. Verify every existing component for
    # Windows junctions/reparse points, not only normal symbolic links.
    absolute_root = Path(os.path.abspath(str(root)))
    absolute_path = Path(os.path.abspath(str(path)))
    try:
        inside = os.path.commonpath((str(absolute_root), str(absolute_path)))
    except ValueError as exc:
        raise RuntimeError("TTM_PATH_ESCAPE_DRIVE") from exc
    require(os.path.normcase(inside) == os.path.normcase(str(absolute_root)),
            "TTM_PATH_ESCAPE")
    for item in [absolute_root, *list(reversed(list(absolute_path.parents))) , absolute_path]:
        if not item.exists():
            continue
        if not (str(item) == str(absolute_root)
                or os.path.normcase(os.path.commonpath((str(absolute_root), str(item))))
                   == os.path.normcase(str(absolute_root))):
            continue
        attrs = getattr(item.lstat(), "st_file_attributes", 0)
        require(not (attrs & getattr(stat, "FILE_ATTRIBUTE_REPARSE_POINT", 0)),
                "TTM_REPARSE_POINT_REJECTED: " + str(item))
    return absolute_path


def git(*args: str, cwd: Path) -> str:
    proc = subprocess.run(["git", "-C", str(cwd), *args], text=True,
                          capture_output=True, check=False, timeout=30)
    require(proc.returncode == 0,
            "TTM_GIT_READONLY_FAILED: " + " ".join(args) + " " + proc.stderr[:350])
    return proc.stdout.strip()


def preflight() -> dict:
    require(os.name == "nt", "TTM_WINDOWS_REQUIRED")
    require(ROOT.is_dir() and WORKTREE.is_dir() and LOCAL_QA.is_dir(),
            "TTM_REQUIRED_PATH_MISSING")
    for path in (ROOT, WORKTREE, LOCAL_QA, ROOT / "tmp", ROOT / "cache"):
        safe_path(path)
    require(os.path.normcase(git("rev-parse", "--show-toplevel", cwd=ROOT).replace("/", "\\"))
            == os.path.normcase(str(ROOT)), "TTM_MAIN_ROOT_MISMATCH")
    require(git("remote", "get-url", "origin", cwd=ROOT) == REMOTE,
            "TTM_ORIGIN_MISMATCH")
    require(git("rev-parse", "HEAD", cwd=ROOT) == BASE_MAIN,
            "TTM_MAIN_HEAD_MISMATCH")
    require(git("rev-parse", "HEAD", cwd=WORKTREE) == SOURCE_COMMIT,
            "TTM_SOURCE_HEAD_MISMATCH")
    require(git("branch", "--show-current", cwd=WORKTREE) == BRANCH,
            "TTM_BRANCH_MISMATCH")
    require(not git("status", "--porcelain", "--untracked-files=no", cwd=WORKTREE),
            "TTM_TRACKED_SOURCE_DIRTY")
    for line in git("worktree", "list", "--porcelain", cwd=ROOT).splitlines():
        if line.startswith("worktree "):
            safe_path(Path(line[9:]))
    receipt_path = safe_path(LOCAL_QA / "QA_RECEIPT.json")
    require(hash_file(receipt_path) == RECEIPT_SHA, "TTM_RECEIPT_SHA_MISMATCH")
    receipt = json.loads(receipt_path.read_text(encoding="utf-8-sig"))
    require(receipt.get("source_commit") == SOURCE_COMMIT, "TTM_RECEIPT_COMMIT_MISMATCH")
    require(receipt.get("main_baseline") == BASE_MAIN, "TTM_RECEIPT_BASE_MISMATCH")
    require(receipt.get("local_tests_pass") is True, "TTM_LOCAL_QA_NOT_PASS")
    require(receipt.get("merge_authorized") is False, "TTM_MERGE_GATE_MISMATCH")
    require(receipt.get("independent_qa") == "NOT_PERFORMED", "TTM_RECEIPT_INDEPENDENCE_MISMATCH")

    hashes = {"model": (WORKTREE / "reference" / "phase0" / "model.py", MODEL_SHA),
              "config": (WORKTREE / "configs" / "phase0_reference.json", CONFIG_SHA)}
    for label, (path, expected) in hashes.items():
        require(hash_file(safe_path(path)) == expected, "TTM_" + label.upper() + "_HASH_MISMATCH")

    expected_counts = {"reference": 5, "records": 8}
    for item in receipt["tests"]:
        name = item["name"]
        require(name in expected_counts and item["exit_code"] == 0, "TTM_TEST_EXIT_OR_NAME_INVALID")
        for stream in ("stdout", "stderr"):
            log = safe_path(LOCAL_QA / (name + "." + stream + ".txt"))
            require(hash_file(log) == item[stream + "_sha256"],
                    "TTM_LOG_SHA_MISMATCH:" + name + ":" + stream)
        log_data = (LOCAL_QA / (name + ".stderr.txt")).read_text(encoding="utf-8-sig")
        require(re.search(r"Ran " + str(expected_counts[name]) + r" tests? in ", log_data) is not None,
                "TTM_TEST_COUNT_MISMATCH:" + name)
        require(re.search(r"(?m)^OK\s*$", log_data) is not None,
                "TTM_TEST_LOG_NOT_OK:" + name)
    require(len(receipt["tests"]) == 2, "TTM_TEST_SET_MISMATCH")
    return {"source_commit": SOURCE_COMMIT, "receipt_sha256": RECEIPT_SHA,
            "model_sha256": MODEL_SHA, "config_sha256": CONFIG_SHA,
            "verified_prior_tests": 13}


def independent_tests() -> tuple[list[dict], dict]:
    import torch
    torch.set_num_threads(1)
    sys.dont_write_bytecode = True
    sys.path.insert(0, str(WORKTREE / "reference" / "phase0"))
    from model import GPT, GPTConfig
    from paged_kv import PagedKVCache

    results = []
    measurements = {}

    def run_case(name, fn):
        try:
            fn()
            results.append({"name": name, "status": "PASS"})
        except Exception as exc:
            results.append({"name": name, "status": "FAIL",
                            "exception": type(exc).__name__, "message": str(exc)[:500]})

    def model_config():
        return GPTConfig(n_layer=2, n_head=4, n_embd=64, max_seq_len=64, vocab_size=256)

    def new_cache(blocks=16):
        return PagedKVCache(n_layers=2, n_blocks=blocks, block_size=4, n_heads=4, head_dim=16)

    def numerical_parity():
        torch.manual_seed(20261105)
        model = GPT(model_config()).eval()
        tokens = [3, 15, 0, 225, 17, 12, 9, 81, 7]
        cache = new_cache()
        cache.start("independent")
        with torch.no_grad():
            all_dense = model(torch.tensor([tokens], dtype=torch.long))[0][0]
            diffs = []
            for pos, token in enumerate(tokens):
                got = model.paged_forward_tokens([token], cache, "independent")
                diffs.append(float((got - all_dense[pos]).abs().max()))
        require(len(cache.tables["independent"]) == 3, "TTM_BLOCK_BOUNDARY")
        require(max(diffs) <= 2e-5, "TTM_NUMERIC_PARITY:" + str(max(diffs)))
        measurements["paged_dense_max_abs_diff"] = max(diffs)
        cache.release("independent")
        require(cache.stats()["used_blocks"] == 0, "TTM_MEMORY_RELEASE")

    def future_token_isolation():
        torch.manual_seed(55)
        model = GPT(model_config()).eval()
        with torch.no_grad():
            one = model(torch.tensor([[1, 2, 3, 4, 5]]))[0]
            two = model(torch.tensor([[1, 2, 3, 141, 212]]))[0]
        delta = float((one[:, :3] - two[:, :3]).abs().max())
        require(delta <= 1e-6, "TTM_FUTURE_LEAK:" + str(delta))
        measurements["causal_prefix_max_abs_diff"] = delta

    def interleaved_request_isolation():
        torch.manual_seed(87)
        model = GPT(model_config()).eval()
        cache = new_cache()
        cache.start("A")
        cache.start("B")
        seqs = {"A": [4, 4, 6, 9, 33], "B": [2, 10, 11, 31, 72]}
        with torch.no_grad():
            for i in range(5):
                for rid in ("A", "B"):
                    got = model.paged_forward_tokens([seqs[rid][i]], cache, rid)
                    expected = model(torch.tensor([seqs[rid][:i+1]]))[0][0, -1]
                    require(torch.allclose(got, expected, atol=2e-5, rtol=2e-5),
                            "TTM_CROSS_REQUEST_PARITY:" + rid)
        require(not (set(cache.tables["A"]) & set(cache.tables["B"])),
                "TTM_CROSS_REQUEST_BLOCK_OVERLAP")
        cache.release("A")
        cache.release("B")
        require(cache.stats()["used_blocks"] == 0, "TTM_BLOCK_LEAK")

    def clear_on_release():
        cache = PagedKVCache(n_layers=1, n_blocks=1, block_size=2, n_heads=1, head_dim=2)
        cache.start("old")
        pos = cache.allocate_token("old")
        cache.write(0, "old", pos, torch.tensor([[93., 94.]]), torch.tensor([[95., 96.]]))
        require(bool(torch.count_nonzero(cache.storage)), "TTM_FIXTURE_NOT_WRITTEN")
        cache.release("old")
        require(not bool(torch.count_nonzero(cache.storage)), "TTM_STALE_KV_AFTER_RELEASE")
        cache.start("new")
        cache.allocate_token("new")
        k, v = cache.read(0, "new")
        require(not bool(torch.count_nonzero(k)) and not bool(torch.count_nonzero(v)),
                "TTM_CROSS_REQUEST_STALE_KV")

    def capacity_guard():
        cache = PagedKVCache(n_layers=1, n_blocks=1, block_size=2, n_heads=1, head_dim=2)
        cache.start("cap")
        cache.allocate_token("cap")
        cache.allocate_token("cap")
        try:
            cache.allocate_token("cap")
        except MemoryError:
            pass
        else:
            raise AssertionError("TTM_OOM_NOT_RAISED")
        require(cache.lengths["cap"] == 2 and cache.stats()["used_blocks"] == 1,
                "TTM_OOM_MUTATED_CACHE_STATE")

    def next_token_gradient():
        torch.manual_seed(909)
        model = GPT(GPTConfig(vocab_size=256, n_embd=16, n_layer=1, n_head=2,
                              max_seq_len=16)).train()
        tok = torch.tensor([[5, 17, 19, 21, 23]], dtype=torch.long)
        x, y = tok[:, :-1], tok[:, 1:]
        _, loss = model(x, y)
        require(bool(torch.isfinite(loss)), "TTM_NONFINITE_NEXT_TOKEN_LOSS")
        loss.backward()
        grad = model.tok.weight.grad
        require(grad is not None and bool(torch.isfinite(grad).all())
                and float(grad.abs().sum()) > 0.0, "TTM_NO_VALID_TRAIN_GRADIENT")
        measurements["next_token_smoke_loss"] = float(loss.item())

    for name, fn in (("independent_numerical_parity", numerical_parity),
                     ("independent_future_isolation", future_token_isolation),
                     ("independent_request_isolation", interleaved_request_isolation),
                     ("independent_zero_on_release", clear_on_release),
                     ("independent_oom_state_integrity", capacity_guard),
                     ("independent_next_token_gradient", next_token_gradient)):
        run_case(name, fn)
    return results, {"torch": torch.__version__, **measurements}


def main() -> int:
    # Fail before any filesystem writes if the approved workspace is not present.
    audit = preflight()
    # No scientific model training or external data acquisition occurs in these fixtures.
    os.environ["PYTHONDONTWRITEBYTECODE"] = "1"
    test_results, metrics = independent_tests()
    success = all(x["status"] == "PASS" for x in test_results)
    now = datetime.now(timezone.utc)
    run_id = "TTM_P00_INDEPENDENT_QA_" + now.strftime("%Y%m%dT%H%M%S%fZ")
    evidence = safe_path(ROOT / "evidence" / "p00" / run_id)
    evidence.mkdir(parents=True, exist_ok=False)
    receipt = {
        "schema": "ttm.p00.independent_qa.v1", "run_id": run_id,
        "utc": now.isoformat(), "repository": REMOTE, "workspace": str(ROOT),
        "source_commit": SOURCE_COMMIT, "main_baseline": BASE_MAIN,
        "prior_local_qa": audit, "qa_scope": "INDEPENDENT_ZERO_SCIENCE_CPU_TESTS",
        "qa_tests": test_results, "metrics": metrics,
        "qa_result": "PASS" if success else "FAIL",
        "python": sys.executable, "python_version": platform.python_version(),
        "os": platform.platform(), "merge_authorized": False,
        "scientific_training": "NOT_PERFORMED",
        "notes": "Separate fixtures from developer unit tests; formal adjudication pending.",
    }
    dest = safe_path(evidence / "INDEPENDENT_QA_RECEIPT.json")
    with dest.open("x", encoding="utf-8") as f:
        json.dump(receipt, f, ensure_ascii=False, indent=2)
        f.write("\n")
    print("TTM_INDEPENDENT_QA=" + receipt["qa_result"])
    print("TTM_INDEPENDENT_QA_TESTS=" + str(sum(x["status"] == "PASS" for x in test_results))
          + "/" + str(len(test_results)))
    print("TTM_INDEPENDENT_QA_RECEIPT=" + str(dest))
    print("TTM_INDEPENDENT_QA_RECEIPT_SHA256=" + hash_file(dest))
    print("TTM_MERGE=NOT_AUTHORIZED")
    return 0 if success else 1


if __name__ == "__main__":
    try:
        sys.exit(main())
    except Exception as exc:
        print("TTM_INDEPENDENT_QA_PREFLIGHT=FAIL: " + repr(exc), file=sys.stderr)
        sys.exit(2)