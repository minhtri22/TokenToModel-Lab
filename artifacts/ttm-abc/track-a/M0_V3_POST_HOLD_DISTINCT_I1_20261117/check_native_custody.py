"""Native independent Q001 custody audit. Real files are opened for reading only."""
import argparse
from collections import Counter
import hashlib
import json
from pathlib import Path
import stat
import subprocess
import sys
import tempfile
from unittest.mock import patch

HEAD = "ec197b5f00d3a037420390edd11ee55047e1d37f"
BASE = "ebdc54575eed1ff60c402eecf60289f408bb38ca"
PRIOR = "05041501bfe84822feffd39290c6800b2152055a"
CI = "8cc069095724e96fd051561a3037f579d01d9222"
PRIOR_PATH = "artifacts/ttm-abc/track-a/M0_V3_DISTINCT_I1_20261116"
RECORDS = "FIXTURE_RECORDS.json"
MANIFEST = "FIXTURE_MANIFEST.json"
PREFIX = "tools/pilot_t4/direct_failure_diag_q001"
RUNNER = PREFIX + "/preexec_candidate_20261116/ttm_sm4m_diag_q001.py"
SCORER = PREFIX + "/track_a_m0_v3/q001_m0_goldblind.py"
ONEPACK = PREFIX + "/track_a_m0_v3/Invoke-TrackA-M0V3-RealTokenizer-Freeze-PS51.ps1"
PINS = {
    RUNNER: ("20c147f9f2629c494c157da5bab3519e01d755096638adfd10e07bb5dda3c4b8",
             "9a6a6bbcdd1ce80d40cc40b2b6dce1b46ca2932806fc0f77b036681a401eee0e"),
    SCORER: ("2d0b980768a0ac3079f361d94244cd694c97ed90e978fc83fb7991dc82b5c2ac",
             "d76936db04caec358ddfb6947656d60023dee7de5c3388f810c7ecbf08288b63"),
    ONEPACK: ("6506ddf1e5b98793a4b2a3ba3b7aaf089f8692b64f4e0f6b53899b3c28d1a76d",
              "40b3bfc6c235e272f70b033d4cf75ed8baca38c84c01ee20aacd701e30b670e5"),
}
GROUPS = {"TRAIN": 24, "HELDOUT_RECOMBINED": 16, "HELDOUT_NOVEL_IDS": 16,
          "PAIRED_COUNTERFACTUAL": 16, "HELDOUT_ABSENT": 8}


def sha(data):
    return hashlib.sha256(data).hexdigest()


def canonical(value):
    return (json.dumps(value, sort_keys=True, ensure_ascii=False, separators=(",", ":")) + "\n").encode("utf-8")


def audit(args):
    def git(*argv):
        return subprocess.check_output(["git", "-C", str(args.tree), *argv], stderr=subprocess.PIPE)

    checks = {}

    def check(name, condition):
        if not condition:
            raise RuntimeError(name)
        checks[name] = True

    check("python_312", sys.version_info[:2] == (3, 12))
    check("exact_source_head", git("rev-parse", "HEAD").decode().strip() == HEAD)
    check("author_ci_code_equals_final_head",
          not git("diff", "--name-only", CI, HEAD, "--", "tools", ".github"))
    check("historical_review_and_lineage_unchanged", not git(
        "diff", "--name-only", PRIOR, HEAD, "--", PRIOR_PATH, ":(icase,glob)**/lineage.md"))
    scope = git("diff", "--name-only", "-z", BASE, HEAD).decode().rstrip("\0").split("\0")
    check("pr_scope_track_a", all(name.startswith((
        "artifacts/ttm-abc/track-a/", "docs/coordination/ttm-abc/track-a/",
        "docs/research/ttm-abc/track-a/", PREFIX + "/")) or name in (
        "docs/coordination/ttm-abc/TTM_TRACK_A_SMALL4M_DIAG_AGENT_HANDOFF_20261116.md",
        "docs/coordination/ttm-abc/status/TTM_TRACK_A_STATUS.json",
        ".github/workflows/ttm_track_a_m0_source_qa.yml") for name in scope))
    changed = {}
    for name in git("diff", "--name-only", "-z", PRIOR, HEAD).decode().rstrip("\0").split("\0"):
        blob = git("show", f"{HEAD}:{name}")
        disk = (args.tree / name).read_bytes()
        win = blob.replace(b"\n", b"\r\n")
        check("exact_checkout_" + Path(name).name, disk in (blob, win) and b"\r" not in blob)
        changed[name] = {"git_lf_sha256": sha(blob), "crlf_sha256": sha(win), "physical_sha256": sha(disk)}
        if name in PINS:
            check("pins_" + Path(name).name, (sha(blob), sha(win)) == PINS[name])

    old_receipt = json.loads(git("show", f"{PRIOR}:{PRIOR_PATH}/receipt.json"))
    native_raw = args.onepack_receipt.read_bytes()
    native = json.loads(native_raw)
    records_path = args.fixture / RECORDS
    manifest_path = args.fixture / MANIFEST
    freeze_path = args.fixture / "FIXTURE_FREEZE_RECEIPT.json"
    private_paths = (records_path, manifest_path, freeze_path, args.bpe, args.historical)
    for p in private_paths:
        check("ordinary_file_" + p.name, p.is_relative_to(args.root) and all(
            not part.lstat().st_file_attributes & stat.FILE_ATTRIBUTE_REPARSE_POINT
            for part in [p, *[parent for parent in p.parents if parent.is_relative_to(args.root)]]))
    before = {p: (p.read_bytes(), p.stat().st_mtime_ns) for p in private_paths}
    raw_rows, raw_manifest, raw_freeze, raw_bpe, raw_historical = [before[p][0] for p in private_paths]
    records_sha, manifest_sha = sha(raw_rows), sha(raw_manifest)
    check("onepack_receipt_exact_inputs", native["source_commit"] == HEAD
          and native["readback_only"] is True and native["fixture_case_count"] == 80
          and native["fixture_group_count"] == 5 and native["fixture_records_sha256"] == records_sha
          and native["fixture_manifest_sha256"] == manifest_sha
          and native["fixture_receipt_sha256"] == sha(raw_freeze) and native["tokenizer_sha256"] == sha(raw_bpe))
    old = old_receipt["custody"]
    check("bytes_match_prior_freeze_hashes", [records_sha, manifest_sha, sha(raw_freeze),
          sha(raw_bpe), sha(raw_historical)] == [
          old[key] for key in ("fixture_sha256", "fixture_manifest_sha256",
              "private_freeze_receipt_sha256", "private_t1_sha256", "historical_fixture_sha256")])
    bpe = json.loads(raw_bpe)
    check("pinned_train_only_taxonomy", bpe["source_kind"] == "PINNED_TINYSTORIES_TRAIN"
          and len(set(bpe["tokens"])) == len(bpe["tokens"]) == bpe["vocab_size"] == 2048
          and bpe["eos_id"] == 256 and bpe["tokens"][256] == "<|endoftext|>"
          and len(bpe["pair_ids"]) == 1791)
    rows, manifest = json.loads(raw_rows), json.loads(raw_manifest)
    cases = {r["id"]: sha(canonical(r)) for r in rows}
    groups = {g: [r for r in rows if r["group"] == g] for g in GROUPS}
    group_digests = {g: sha(canonical(group)) for g, group in groups.items()}
    check("all_80_case_and_5_group_digests", len(rows) == len(cases) == 80
          and len({tuple(r["context"]) for r in rows}) == 80 and canonical(rows) == raw_rows
          and cases == manifest["case_sha256"] == old["case_sha256"]
          and group_digests == manifest["group_sha256"] == old["group_sha256"]
          and Counter(r["group"] for r in rows) == GROUPS == manifest["counts"])

    def bindings(row):
        c = row["context"]
        return {(c[1], c[2]), (c[4], c[5])}

    training = {r["id"]: r for r in groups["TRAIN"]}
    train_pairs = set().union(*(bindings(r) for r in training.values()))
    train_ids = {token for row in training.values() for token in row["context"] + [row["gold"]]}
    holdouts = groups["HELDOUT_RECOMBINED"] + groups["HELDOUT_ABSENT"]
    pairs = groups["PAIRED_COUNTERFACTUAL"]
    check("split_and_parent_links", not any(bindings(row) & train_pairs for row in holdouts)
          and not any(row["context"][i] in train_ids
                      for row in groups["HELDOUT_NOVEL_IDS"] for i in (1, 2, 4, 5, 7))
          and len({row["parent"] for row in pairs}) == 16
          and all(row["parent"] is None for row in rows if row["group"] != "PAIRED_COUNTERFACTUAL"))
    for i, row in enumerate(pairs):
        parent = training[row["parent"]]
        ctx = list(parent["context"])
        ctx[2], ctx[5] = ctx[5], ctx[2]
        if row["context"] != ctx or row["gold"] == parent["gold"]:
            raise RuntimeError("parent_swap")
    checks["paired_value_swap"] = True

    runner_path = args.tree / RUNNER
    runner_raw = runner_path.read_bytes()
    check("runner_executes_verified_bytes", sha(runner_raw) in PINS[RUNNER])
    runner = {"__file__": str(runner_path), "__name__": "track_a_custody_review"}
    exec(compile(runner_raw, str(runner_path), "exec", dont_inherit=True), runner)
    check("legacy_pin_constants_match_private_pair",
          (runner["TRACK_A_V3_FROZEN_RECORDS_SHA256"], runner["TRACK_A_V3_FROZEN_MANIFEST_SHA256"],
           runner["TRACK_A_V3_PRE_REPAIR_SCORER_SHA256"]) == (records_sha, manifest_sha, manifest["scorer_sha256"]))
    check("real_manifest_delta_only_scorer_pin",
          dict(manifest, scorer_sha256=runner["TRACK_A_V3_SOURCE_SHA256"])
          == runner["case_and_group_manifest"](rows))
    runner["validate_fixture"](rows, groups["HELDOUT_ABSENT"][0]["no_answer"])
    checks["runner_validates_existing_rows_only"] = True
    # All actual read_frozen_fixture() calls below use synthetic rows and paths.
    allowed = list(range(300, 500))
    mock = runner["fixture_generator"](allowed)
    mock_records = canonical(mock)
    mock_digest = sha(mock_records)
    old_mock = dict(runner["case_and_group_manifest"](mock),
                    scorer_sha256=runner["TRACK_A_V3_PRE_REPAIR_SCORER_SHA256"])
    mock_manifest = canonical(old_mock)
    with tempfile.TemporaryDirectory(prefix="ttm_track_a_postfix_mock_") as td:
        d = Path(td).resolve()
        rp, mp = d / RECORDS, d / MANIFEST
        rp.write_bytes(mock_records)
        mp.write_bytes(mock_manifest)

        def read():
            return runner["read_frozen_fixture"](d, mock_digest, allowed=allowed)

        def denies(message):
            try:
                read()
            except RuntimeError as exc:
                return message in str(exc)
            return False

        check("unscoped_legacy_manifest_denied", denies("FROZEN_CASE_OR_GROUP_MANIFEST_MISMATCH"))
        with patch.dict(runner, {"TRACK_A_V3_FROZEN_RECORDS_SHA256": mock_digest,
                                "TRACK_A_V3_FROZEN_MANIFEST_SHA256": sha(mock_manifest)}):
            check("precise_legacy_pair_mock_accepted", read() == mock)
            rp.write_bytes(mock_records + b" ")
            check("record_byte_tamper_denied", denies("FROZEN_FIXTURE_BYTES_CHANGED"))
            rp.write_bytes(mock_records)
            mp.write_bytes(mock_manifest + b" ")
            check("semantic_equal_manifest_byte_tamper_denied",
                  denies("FROZEN_CASE_OR_GROUP_MANIFEST_MISMATCH"))
            changed_mock = dict(old_mock)
            changed_mock["group_sha256"] = dict(old_mock["group_sha256"], TRAIN="0" * 64)
            bad = canonical(changed_mock)
            mp.write_bytes(bad)
            with patch.dict(runner, {"TRACK_A_V3_FROZEN_MANIFEST_SHA256": sha(bad)}):
                check("pinned_but_inconsistent_manifest_denied",
                      denies("FROZEN_CASE_OR_GROUP_MANIFEST_MISMATCH"))
    check("private_hash_and_mtime_unchanged", all(
        p.read_bytes() == raw and p.stat().st_mtime_ns == mtime for p, (raw, mtime) in before.items()))
    return {"source_commit": HEAD, "base_commit": BASE, "author_ci_source_commit": CI,
            "prior_review_commit": PRIOR, "source_scope_paths": scope, "changed_files": changed,
            "onepack_native_receipt_sha256": sha(native_raw), "case_sha256": cases,
            "group_sha256": group_digests, "custody_sha256": {
                "tokenizer": sha(raw_bpe), "fixture_records": records_sha, "fixture_manifest": manifest_sha,
                "freeze_receipt": sha(raw_freeze), "historical_fixture": sha(raw_historical)},
            "python_version": sys.version.split()[0], "checks": checks,
            "real_case_count": len(cases), "real_group_count": len(group_digests),
            "real_regeneration": False, "real_fixture_written": False,
            "scope": {"I2": "NOT_EXECUTED", "checkpoint_access": False, "optimizer_steps": 0,
                      "model_forwards": 0, "nonce_claimed": False}}


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    for name in ("root", "tree", "fixture", "bpe", "historical", "onepack-receipt"):
        parser.add_argument("--" + name, required=True, type=Path)
    try:
        print(json.dumps(audit(parser.parse_args()), ensure_ascii=True, indent=2, sort_keys=True))
    except Exception as exc:
        label = str(exc) if type(exc) is RuntimeError and str(exc).replace("_", "").replace(".", "").replace("-", "").isalnum() else type(exc).__name__
        raise SystemExit("QA_HOLD_" + label) from None
