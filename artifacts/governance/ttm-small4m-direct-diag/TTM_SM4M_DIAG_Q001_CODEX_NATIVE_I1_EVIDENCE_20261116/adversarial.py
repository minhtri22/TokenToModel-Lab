import importlib.util
import json
import os
from pathlib import Path
import re
import shutil
import subprocess
import sys
import tempfile
from unittest.mock import patch

root = Path.cwd()
src = root / "tools/pilot_t4/direct_failure_diag_q001/preexec_candidate_20261116"
sys.path.insert(0, str(src))
import release_auth_v2 as auth
import ttm_sm4m_diag_q001 as diag

def denial(fn, expected):
    try:
        fn()
    except RuntimeError as error:
        return {"expected": expected, "actual": str(error), "passed": str(error) == expected}
    return {"expected": expected, "actual": "UNEXPECTED_ACCEPT", "passed": False}

def check(result):
    return {"passed": bool(result)}

def junction(link, target):
    shell = Path(os.environ["SystemRoot"]) / "System32/cmd.exe"
    return subprocess.run([str(shell), "/d", "/c", "mklink", "/J", str(link), str(target)],
                          text=True, capture_output=True, check=True)

checks = {}
real_root = root.parents[1]
checks["real_pinned_root_and_hostname"] = check(auth.trusted_execution_root(real_root) == real_root)
checks["worktree_is_not_an_execution_root"] = denial(
    lambda: auth.trusted_execution_root(root), "HOLD_PROJECT_ROOT_NOT_SIGNED_TRUST_ROOT")
with patch.object(auth.platform, "node", return_value="synthetic-foreign-host"):
    checks["foreign_hostname"] = denial(
        lambda: auth.trusted_execution_root(real_root), "HOLD_HOSTNAME_NOT_SIGNED_TRUST_HOST")

with tempfile.TemporaryDirectory(prefix="security_", dir=root / "_tmp") as tmp:
    space = Path(tmp)
    scoped_root = space / "synthetic_trust_root"
    foreign = space / "foreign"
    scoped_root.mkdir()
    foreign.mkdir()
    first_worktree = scoped_root / "worktree_a"
    second_worktree = scoped_root / "worktree_b"
    first_worktree.mkdir()
    second_worktree.mkdir()

    def from_worktree(directory, name):
        runner = directory / "runner.py"
        shutil.copyfile(src / "ttm_sm4m_diag_q001.py", runner)
        spec = importlib.util.spec_from_file_location(name, runner)
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)
        return module

    a = from_worktree(first_worktree, "synthetic_scope_a")
    b = from_worktree(second_worktree, "synthetic_scope_b")
    alias = space / "root_alias"
    escape = scoped_root / "junction_escape"
    junction(alias, scoped_root)
    junction(escape, foreign)
    symbolic = scoped_root / "symlink_escape"
    try:
        symbolic.symlink_to(foreign, target_is_directory=True)
        symbolic_error = None
    except OSError as error:
        symbolic_error = {"winerror": error.winerror}

    try:
        with patch.object(auth, "TRUSTED_PROJECT_ROOT", str(scoped_root)):
            checks["canonical_alias_resolves_to_pinned_root"] = check(auth.trusted_execution_root(alias) == scoped_root)
            checks["junction_escape"] = denial(lambda: diag.exact_scoped_path(scoped_root, escape / "synthetic"),
                                               "HOLD_DIRECT_CLI_PATH_ESCAPES_SIGNED_PROJECT")
            if symbolic_error is None:
                checks["symlink_escape"] = denial(lambda: diag.exact_scoped_path(scoped_root, symbolic / "synthetic"),
                                                  "HOLD_DIRECT_CLI_PATH_ESCAPES_SIGNED_PROJECT")
            else:
                checks["symlink_escape"] = {"passed": None, "status": "NOT_EXECUTED", **symbolic_error}
            # A synthetic nonce in a disposable ledger. No permit or trust key is generated.
            nonce = "8" * 64
            first = a.claim_one_shot(scoped_root, nonce)
            checks["first_mock_nonce_claim"] = check(first.is_file())
            checks["same_nonce_two_worktree_sources"] = denial(
                lambda: b.claim_one_shot(scoped_root, nonce), "HOLD_ONESHOT_NONCE_ALREADY_CONSUMED_NO_RETRY")
            checks["same_nonce_root_junction_alias"] = denial(
                lambda: b.claim_one_shot(alias, nonce), "HOLD_ONESHOT_NONCE_ALREADY_CONSUMED_NO_RETRY")

        reparse_root = space / "reparse_ledger_root"
        reparse_root.mkdir()
        ledger_link = reparse_root / "_evidence"
        junction(ledger_link, foreign)
        try:
            with patch.object(auth, "TRUSTED_PROJECT_ROOT", str(reparse_root)):
                checks["ledger_reparse_denied_before_mkdir"] = denial(
                    lambda: diag.claim_one_shot(reparse_root, "9" * 64),
                    "HOLD_ONESHOT_LEDGER_REPARSE_OR_SYMLINK")
                checks["no_foreign_ledger_write"] = check(not any(foreign.iterdir()))
        finally:
            ledger_link.rmdir()
    finally:
        for link in (symbolic, escape, alias):
            if link.is_junction() or link.is_symlink():
                link.rmdir()

    read_names = []
    real_open = Path.open
    restricted = {"sentinel_checkpoint", "sentinel_tokenizer", "sentinel_inventory"}
    def trace_open(path, *args, **kwargs):
        read_names.append(path.name)
        if path.name in restricted:
            raise AssertionError("private-input sentinel was accessed")
        return real_open(path, *args, **kwargs)

    for name, packet in {
        "unsigned": {"payload": {"frozen_fixture_sha256": "d" * 64}},
        "forged": {"payload": {"frozen_fixture_sha256": "d" * 64}, "signatures": {"owner": "invalid"}},
        "expired": {"payload": {"frozen_fixture_sha256": "d" * 64, "expires_utc": "2000-01-01T00:00:00Z"}},
    }.items():
        negative = space / ("synthetic-invalid-" + name + ".json")
        negative.write_text(json.dumps(packet), encoding="ascii")
        with patch.object(Path, "open", trace_open):
            checks["real_empty_trust_denies_" + name] = denial(
                lambda: diag.signed_admission(negative, src / "ttm_sm4m_diag_q001.py",
                                               space / "sentinel_inventory", space / "sentinel_tokenizer",
                                               "run", "d" * 64, real_root),
                "HOLD_AUTHENTICATED_TRUST_ANCHORS_UNAVAILABLE")
    checks["trust_empty_no_private_open"] = {**check(not restricted.intersection(read_names)),
                                             "observed_basenames": sorted(set(read_names))}
    # Watch only pre-model admission by replacing every possible model entry with
    # sentinels that fail the test if reached. No checkpoint or fixture is created.
    class SyntheticArgs:
        root = str(real_root)
        permit = str(negative)
        checkpoint = str(space / "sentinel_checkpoint")
        token_inventory = str(space / "sentinel_inventory")
        tokenizer_source = str(space / "sentinel_tokenizer")
        fixture_dir = str(space / "sentinel_fixture")
        out = str(space / "sentinel_output")

    with patch.object(Path, "open", trace_open), \
         patch.object(diag, "load_model", side_effect=AssertionError("model entry reached")) as model, \
         patch.object(diag, "claim_one_shot", side_effect=AssertionError("nonce claim reached")) as claim:
        checks["direct_function_denies_before_model_or_nonce"] = denial(
            lambda: diag.run(SyntheticArgs()), "HOLD_AUTHENTICATED_TRUST_ANCHORS_UNAVAILABLE")
        checks["no_private_checkpoint_open_or_model_call"] = check(
            not restricted.intersection(read_names) and not model.called and not claim.called
            and not Path(SyntheticArgs.out).exists())

for label, data, reason in (
    ("missing", {}, "HOLD_SIGNED_PERMIT_EXPIRY_REQUIRED"),
    ("malformed", {"expires_utc": "2000-01-01 00:00:00"}, "HOLD_SIGNED_PERMIT_EXPIRY_INVALID"),
    ("past", {"expires_utc": "2000-01-01T00:00:00Z"}, "HOLD_SIGNED_PERMIT_EXPIRED"),
):
    checks["expiration_validator_" + label] = denial(lambda: auth.require_unexpired(data), reason)
auth.require_unexpired({"expires_utc": "2099-01-01T00:00:00Z"})
checks["expiration_validator_future"] = check(True)
launcher = (src / "Run-Approved-OneShot-PS51.ps1").read_text()
checks["frozen_resource_constants"] = check(
    (diag.WALL_SECONDS, diag.MEMORY_BYTES, diag.OUTPUT_BYTES, diag.MAX_STEPS) ==
    (900, 12884901888, 1073741824, 256) and all(re.search(p, launcher) for p in
    (r"-WallSeconds 900\b", r"-MaxTreeRssBytes 12884901888\b", r"-MaxTotalOutputBytes 1073741824\b")))

print(json.dumps({"scope": "CODEX_ADVERSARIAL_NATIVE_WINDOWS_SOURCE_AND_MOCK",
                  "trust_store_modified_on_disk": False, "model_execution": False,
                  "private_inputs_read": False, "checks": checks,
                  "crypto_with_external_keys": "NOT_EXERCISED_EMPTY_PRODUCTION_STORE",
                  "organizational_signoff": "NOT_INCLUDED",
                  "passed": sum(item["passed"] is True for item in checks.values()),
                  "total": len(checks)}, indent=2))
sys.exit(2 if any(item["passed"] is False for item in checks.values()) else 0)
