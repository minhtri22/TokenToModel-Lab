#!/usr/bin/env python3
"""TTM PR12: one source-controlled, offline-only Windows QA batch.
No Ollama serve/create/generate, no Colab, no TRAIN/TEST decoding, no merge.
Run only after retrieving this exact file from GitHub and SHA checking it.
"""
import argparse, ast, datetime, hashlib, json, os, pathlib, re, shutil, subprocess, sys, urllib.request

ROOT = pathlib.Path(r"D:\WORK\RESEARCH\TokenToModel-Lab")
REPO = "minhtri22/TokenToModel-Lab"
ORIGIN = "https://github.com/" + REPO + ".git"
BRANCH = "research/ttm-small-4m-colab-pilot-prereg-20261108"
MAIN = "1a9d8cba56564d6d36257fe95c34f2fd52c4f48a"
VALID_ORIGINS = {ORIGIN, ORIGIN[:-4], "git@github.com:minhtri22/TokenToModel-Lab.git"}
SECRET = re.compile(rb"(?:ghp_[A-Za-z0-9]{20,}|github_pat_[A-Za-z0-9_]{20,}|sk-proj-[A-Za-z0-9_-]{20,}|AKIA[0-9A-Z]{16}|-----BEGIN [A-Z ]*PRIVATE KEY-----)")

def require(ok, msg):
    if not ok:
        raise RuntimeError(msg)

def sha(data):
    return hashlib.sha256(data).hexdigest()

def cmd(args, cwd=None, timeout=100, env=None):
    return subprocess.run(args, cwd=cwd, env=env, stdout=subprocess.PIPE,
                          stderr=subprocess.PIPE, timeout=timeout, check=False)

def git(*args, cwd=ROOT, timeout=100):
    r = cmd(["git", "-C", str(cwd), *args], timeout=timeout)
    require(r.returncode == 0, "GIT_FAILED_" + "_".join(args[:2]) + ":" + r.stderr[-800:].decode("utf-8", "replace"))
    return r.stdout.decode("utf-8", "replace").strip()

def remote_head():
    rows = git("ls-remote", "origin", "refs/heads/" + BRANCH)
    require(len(rows.splitlines()) == 1, "REMOTE_BRANCH_NOT_UNIQUE")
    return rows.split()[0]

def verify_root():
    require(os.name == "nt", "WINDOWS_ONLY")
    require(ROOT.is_dir() and (ROOT / ".git").exists(), "REPO_MISSING")
    require(pathlib.Path(git("rev-parse", "--show-toplevel")).resolve() == ROOT.resolve(), "ROOT_MISMATCH")
    require(git("remote", "get-url", "origin") in VALID_ORIGINS, "ORIGIN_MISMATCH")
    require(git("ls-remote", "origin", "refs/heads/main").split()[0] == MAIN, "MAIN_MOVED")

def source_pins(checkout):
    v = checkout / "tools/pilot_t5/v5_native_source_20261109"
    i = checkout / "tools/pilot_t5/v5_inference_only_source_20261109"
    q = checkout / "tools/pilot_q1q2/frozen_inputs_20261109"
    manifest_v = json.loads((v / "SOURCE_SHA256_MANIFEST.json").read_text("utf-8"))
    manifest_i = json.loads((i / "SOURCE_SHA256_MANIFEST.json").read_text("utf-8"))
    manifest_q = json.loads((q / "Q1Q2_LOCK_MANIFEST.json").read_text("utf-8"))
    checked = 0
    for directory, pins in [(v, manifest_v["source_files"]),
                            (i, manifest_i["source_sha256"]),
                            (q, manifest_q["files_sha256"])]:
        for filename, expected in pins.items():
            require(re.fullmatch(r"[A-Za-z0-9_.-]+", filename) is not None, "UNSAFE_SOURCE_FILENAME")
            require(sha((directory / filename).read_bytes()) == expected, "SOURCE_SHA_MISMATCH:" + filename)
            checked += 1
    require(sha((v / "Invoke-TTM-T5-Timewait-V5-PS51.ps1").read_bytes()) ==
            "856a61d364f14523dce2572cde3185542733c46cfb9aeedbfaf80e1b82d46fdb", "V5_ORIGINAL_WRAPPER_CHANGED")
    require(sha((v / "Invoke-TTM-T5-Timewait-V5-PS51.patched.ps1").read_bytes()) ==
            "238570d7c98e228d351dbe9ebcd6992fb018ba482d9d0078008d4ab8a2c5c8ad", "V5_PATCHED_WRAPPER_CHANGED")
    return checked + 2

def static_inspection(checkout):
    compiled = parsed = notebooks = 0
    for folder in ("tools/pilot_t1t3", "tools/pilot_t4", "tools/pilot_t5", "tools/pilot_q1q2"):
        for p in (checkout / folder).rglob("*"):
            if not p.is_file() or p.is_symlink():
                continue
            if p.suffix == ".py":
                ast.parse(p.read_text(encoding="utf-8-sig"), filename=str(p)); compiled += 1
            elif p.suffix in (".json", ".ipynb"):
                obj = json.loads(p.read_text("utf-8")); parsed += 1
                if p.suffix == ".ipynb":
                    for cell in obj.get("cells", []):
                        if cell.get("cell_type") == "code":
                            require(not cell.get("outputs") and cell.get("execution_count") is None, "NOTEBOOK_OUTPUT_PRESENT")
                    notebooks += 1
    return dict(python_ast=compiled, json_parsed=parsed, notebooks_without_outputs=notebooks)

def run_qa(checkout, name, argv, timeout, evidence_dir):
    env = os.environ.copy()
    env.update(PYTHONDONTWRITEBYTECODE="1", PYTEST_DISABLE_PLUGIN_AUTOLOAD="1",
               HF_HUB_OFFLINE="1", TRANSFORMERS_OFFLINE="1", OLLAMA_NO_CLOUD="true")
    try:
        result = cmd([sys.executable, "-B", *argv], cwd=checkout, timeout=timeout, env=env)
        stdout, stderr, exitcode = result.stdout, result.stderr, result.returncode
        outcome = "PASS" if exitcode == 0 else "FAIL"
    except subprocess.TimeoutExpired as ex:
        stdout, stderr, exitcode, outcome = ex.stdout or b"", ex.stderr or b"", 124, "TIMEOUT"
    require(not SECRET.search(stdout + stderr), "POSSIBLE_SECRET_IN_QA_LOG_" + name)
    first = evidence_dir / (name + ".stdout.txt")
    second = evidence_dir / (name + ".stderr.txt")
    first.write_bytes(stdout); second.write_bytes(stderr)
    return dict(name=name, outcome=outcome, exit_code=exitcode, stdout_sha256=sha(stdout),
                stderr_sha256=sha(stderr), timeout_seconds=timeout)

def safe_cleanup(path, parent):
    require(path.parent.resolve() == parent.resolve(), "CLEANUP_PARENT_NOT_EXACT")
    require(path.name.startswith("TTM_PR12_QA_"), "CLEANUP_NAME_NOT_EXACT")
    for base, directories, files in os.walk(path, followlinks=False):
        for entry in directories + files:
            item = pathlib.Path(base) / entry
            require(not item.is_symlink(), "CLEANUP_REPARSE_POINT")
            if hasattr(os.path, "isjunction"):
                require(not os.path.isjunction(item), "CLEANUP_JUNCTION")
    shutil.rmtree(path)

def run(expected, cleanup):
    verify_root()
    require(remote_head() == expected, "REMOTE_HEAD_CHANGED")
    parent = ROOT / "_tmp"
    require(parent.is_dir() and not parent.is_symlink(), "PROJECT_TMP_MISSING_OR_LINK")
    run_dir = parent / ("TTM_PR12_QA_" + expected[:12])
    run_dir.mkdir(exist_ok=False)
    checkout = run_dir / "checkout"
    print("TTM_PR12_QA_CLAIMED=" + str(run_dir), flush=True)
    clone = cmd(["git", "clone", "--single-branch", "--branch", BRANCH, ORIGIN, str(checkout)], timeout=180)
    require(clone.returncode == 0, "GIT_CLONE_FAILED:" + clone.stderr[-800:].decode("utf-8", "replace"))
    require(git("rev-parse", "HEAD", cwd=checkout) == expected, "CLONED_HEAD_NOT_EXACT")
    original_main = cmd(["git", "-C", str(checkout), "show", MAIN + ":lineage.md"], timeout=30)
    require(original_main.returncode == 0, "MAIN_LINEAGE_NOT_IN_HISTORY")
    current_lineage = (checkout / "lineage.md").read_bytes()
    require(current_lineage.startswith(original_main.stdout), "LINEAGE_NOT_APPEND_ONLY")
    require(b"L0011" in current_lineage[len(original_main.stdout):] and
            b"L0012" in current_lineage[len(original_main.stdout):], "LINEAGE_SCIENCE_ENTRIES_MISSING")
    source_count = source_pins(checkout)
    static = static_inspection(checkout)
    evidence_dir = checkout / "artifacts" / "qa" / "pr12" / ("TTM_PR12_QA_" + expected[:12])
    evidence_dir.mkdir(parents=True, exist_ok=False)
    commands = [
       ("T1T3_SYNTHETIC", ["-m", "pytest", "-q", "-p", "no:cacheprovider", "tools/pilot_t1t3/tests/test_t1_t3_contract.py"], 120),
       ("T2_SYNTHETIC", ["-m", "pytest", "-q", "-p", "no:cacheprovider", "tools/pilot_t1t3/source_t2/test_ttm_t2_f32_contract.py"], 150),
       ("T4_SYNTHETIC", ["-m", "pytest", "-q", "-p", "no:cacheprovider", "tools/pilot_t4/integrated/tests/test_t4_integrated.py"], 180),
       ("T5_V5_OFFLINE", ["tools/pilot_t5/v5_native_source_20261109/test_final_minimal_smoke_v5.py"], 50),
       ("T5_INFERENCE_OFFLINE", ["tools/pilot_t5/v5_inference_only_source_20261109/test_resume_inference_offline.py"], 50),
       ("Q1Q2_FROZEN", ["tools/pilot_q1q2/frozen_inputs_20261109/QA_FROZEN_INPUTS.py"], 40)
    ]
    results = [run_qa(checkout, n, args, sec, evidence_dir) for n, args, sec in commands]
    receipt = dict(schema="ttm.pr12.github_truth.integrated_windows_qa.v1",
                   date_utc=datetime.datetime.now(datetime.timezone.utc).isoformat(),
                   exact_head=expected, main=MAIN, branch=BRANCH, source_pins_verified=source_count,
                   static=static, suites=results, science_train_or_test_executed=False,
                   ollama_or_network_smoke_executed=False, prior_one_shots_replayed=False,
                   parity="FAIL_7_OF_8_PRESERVED",
                   status="PASS_SCOPED" if all(x["outcome"] == "PASS" for x in results) else "HOLD_QA_FAILURE",
                   merge_decision="HOLD_OWNER_RIGHTS_AND_FINAL_REVIEW")
    out = evidence_dir / "QA_RESULT.json"
    out.write_text(json.dumps(receipt, indent=2, ensure_ascii=False, sort_keys=True) + "\n", encoding="utf-8")
    for f in evidence_dir.iterdir():
        require(not SECRET.search(f.read_bytes()), "POSSIBLE_SECRET_IN_EVIDENCE_" + f.name)
    require(remote_head() == expected, "REMOTE_HEAD_MOVED_BEFORE_PUBLISH")
    rel = evidence_dir.relative_to(checkout).as_posix()
    git("add", "--", rel, cwd=checkout)
    changed = git("diff", "--cached", "--name-only", cwd=checkout).splitlines()
    require(len(changed) == 13 and all(x.startswith(rel + "/") for x in changed), "GIT_STAGE_SCOPE_INVALID")
    author = git("config", "--get", "user.name", cwd=ROOT)
    email = git("config", "--get", "user.email", cwd=ROOT)
    require(bool(author and email), "GIT_USER_IDENTITY_MISSING")
    git("-c", "user.name=" + author, "-c", "user.email=" + email,
        "commit", "-m", "qa(ttm): archived exact-head Windows offline integrated source receipts", cwd=checkout)
    published = git("rev-parse", "HEAD", cwd=checkout)
    push = cmd(["git", "-C", str(checkout), "push", "origin", "HEAD:refs/heads/" + BRANCH], timeout=120)
    require(push.returncode == 0, "GIT_NONFORCE_PUSH_FAILED:" + push.stderr[-800:].decode("utf-8", "replace"))
    require(remote_head() == published, "PUSH_READBACK_SHA_MISMATCH")
    # Each uploaded file is independently read back over immutable commit URL before cleanup.
    for f in evidence_dir.iterdir():
        path = rel + "/" + f.name
        url = "https://raw.githubusercontent.com/" + REPO + "/" + published + "/" + path
        req = urllib.request.Request(url, headers={"User-Agent": "TTM-PR12-QA-GitHub-Readback/1.0"})
        with urllib.request.urlopen(req, timeout=25) as response:
            require(response.status == 200 and sha(response.read()) == sha(f.read_bytes()), "GITHUB_READBACK_MISMATCH_" + f.name)
    print("TTM_PR12_EVIDENCE_COMMIT=" + published)
    print("TTM_PR12_QA_RESULT=" + receipt["status"])
    print("TTM_PR12_MERGE_DECISION=" + receipt["merge_decision"])
    print("TTM_PR12_EVIDENCE_GITHUB_READBACK=PASS_ALL_13_FILES")
    if cleanup:
        safe_cleanup(run_dir, parent)
        print("TTM_PR12_EPHEMERAL_CLEANUP=PASS_SCOPED_ONLY")
    else:
        print("TTM_PR12_EPHEMERAL_CLEANUP=NOT_REQUESTED")
    return 0 if receipt["status"] == "PASS_SCOPED" else 4

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--head", required=True)
    ap.add_argument("--mode", choices=["preview", "qa"], default="preview")
    ap.add_argument("--cleanup-if-published", action="store_true")
    opts = ap.parse_args()
    require(re.fullmatch(r"[0-9a-f]{40}", opts.head) is not None, "INVALID_EXPECTED_HEAD")
    verify_root()
    require(remote_head() == opts.head, "REMOTE_HEAD_CHANGED")
    if opts.mode == "preview":
        print("TTM_PR12_SOURCE_OF_TRUTH=GITHUB_EXACT_HEAD")
        print("TTM_PR12_PREVIEW=PASS_READONLY_NO_QA_CLAIM")
        return 0
    return run(opts.head, opts.cleanup_if_published)

if __name__ == "__main__":
    try:
        sys.exit(main())
    except Exception as exc:
        print("TTM_PR12_QA=HOLD:" + type(exc).__name__ + ":" + str(exc)[:800], file=sys.stderr)
        print("TTM_PR12_NO_AUTOMATIC_RERUN=TRUE", file=sys.stderr)
        sys.exit(4)
