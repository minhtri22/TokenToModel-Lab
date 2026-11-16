"""Track A M0 v3 independent Windows fixture and scorer audit. Stdlib only."""
import argparse
from collections import Counter
from copy import deepcopy
import hashlib
import importlib.util
import json
import math
import os
from pathlib import Path
import py_compile
import random
import shutil
import stat
import struct
import subprocess
import sys
import tempfile
from types import SimpleNamespace
from unittest.mock import patch

PIN = "6ccd00ec3faef0e87b095662fdb099ac01f4709a"
BASE = "ebdc54575eed1ff60c402eecf60289f408bb38ca"
CI = "639a662ef52d028d0b3f07234bdc6d0a5ed5be62"
PREFIX = Path("tools/pilot_t4/direct_failure_diag_q001")
RUNNER = PREFIX / "preexec_candidate_20261116/ttm_sm4m_diag_q001.py"
SCORER = PREFIX / "track_a_m0_v3/q001_m0_goldblind.py"
RUNNER_SHA = "ccc4f496edbda23517c8efa6110b447eeab807d84a087b0284277670e78cc73d"
SCORER_SHA = "98101e871410e7255cd25f611e5eb9d7068ab264ac162e0af89ef1f1863f6587"
T1 = "cba18e60cee3d08a353ee6d4a451017289e45af7b4b1179c87171b9b78d7dfdc"
OLD = "5f1234f583ccf719ca9f0e68de4f47d8b653af777271b8115c5f02307f764e5a"
MOCK = "f696d20af567ba52dbb9187aba87092829b4da7f3974fbe062608659bd99e726"
GROUPS = dict(TRAIN=24, HELDOUT_RECOMBINED=16, HELDOUT_NOVEL_IDS=16,
              PAIRED_COUNTERFACTUAL=16, HELDOUT_ABSENT=8)
N = 2048


def sha(raw):
    return hashlib.sha256(raw).hexdigest()


def encode(obj):
    return (json.dumps(obj, sort_keys=True, separators=(",", ":"), ensure_ascii=False)
            + "\n").encode("utf-8")


def import_file(name, path):
    spec = importlib.util.spec_from_file_location(name, path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def git_bytes(tree, *args):
    return subprocess.check_output(["git", "-C", str(tree), *args])


def rejected(fn, fragment):
    try:
        fn()
    except (ValueError, RuntimeError) as exc:
        return fragment in str(exc)
    return False


def choices_for(row):
    context = row["context"]
    base = set([context[2], context[5], row["no_answer"]])
    filler = sorted(set(row["value_pool"]) - base,
                    key=lambda token: sha(encode(["filler", context, token])))[0]
    return sorted(base | {filler},
                  key=lambda token: sha(encode(["order", context, token])))


def unique_max(scores, ids):
    ranked = sorted((scores[token], token) for token in ids)
    return ranked[-1][1] if ranked[-1][0] > ranked[-2][0] else None


def f32(x):
    return struct.unpack("f", struct.pack("f", x))[0]


def audit(args):
    sys.dont_write_bytecode = True
    tree, root = args.tree.resolve(), args.root.resolve()
    fixture = args.fixture
    records = fixture / "FIXTURE_RECORDS.json"
    manifest = fixture / "FIXTURE_MANIFEST.json"
    receipt = fixture / "FIXTURE_FREEZE_RECEIPT.json"
    checks = {}

    def must(name, condition):
        checks[name] = bool(condition)
        if not condition:
            raise RuntimeError(name)

    must("python312", sys.version_info[:2] == (3, 12))
    must("pinned_head_and_base", git_bytes(tree, "rev-parse", "HEAD").strip().decode() == PIN
         and not git_bytes(tree, "diff", "--name-only", CI, PIN, "--", "tools", ".github"))
    expected_materializations = {RUNNER: RUNNER_SHA, SCORER: SCORER_SHA}
    changed = {}
    for name in git_bytes(tree, "diff", "--name-only", "-z", BASE, PIN).decode().split("\0"):
        if not name:
            continue
        rel = Path(name)
        blob = git_bytes(tree, "show", f"{PIN}:{rel.as_posix()}")
        disk = (tree / rel).read_bytes()
        if rel in expected_materializations:
            must(f"lf_git_and_crlf_execution_{rel.name}",
                 blob.replace(b"\n", b"\r\n") == disk
                 and sha(disk) == expected_materializations[rel])
        else:
            must(f"exact_git_and_worktree_{rel.name}", disk == blob)
        changed[name] = {"git_blob_sha256": sha(blob), "windows_worktree_sha256": sha(disk)}

    for name, path in {"fixture_records": records, "fixture_manifest": manifest,
                       "freeze_receipt": receipt, "t1": args.tokenizer,
                       "historical": args.historical}.items():
        must(f"{name}_inside_root_no_reparse", path.is_relative_to(root)
             and all(not node.lstat().st_file_attributes & stat.FILE_ATTRIBUTE_REPARSE_POINT
                     for node in [path, *[p for p in path.parents if p.is_relative_to(root)]]))
    raw_t1 = args.tokenizer.read_bytes()
    t1 = json.loads(raw_t1)
    must("exact_original_train_bpe", sha(raw_t1) == T1
         and t1["manifest_sha256"] == "6da22cf79c3a6cfd08d80a768eb1074125a753164ccf62a164e79545956e94c6"
         and t1["source_kind"] == "PINNED_TINYSTORIES_TRAIN")
    must("tokenizer_taxonomy", t1["vocab_size"] == N and t1["eos_id"] == 256
         and len(t1["tokens"]) == len(set(t1["tokens"])) == N
         and t1["tokens"][256] == "<|endoftext|>" and len(t1["pair_ids"]) == 1791)
    must("historical_fixture_hash", sha(args.historical.read_bytes()) == OLD)
    raw_records = records.read_bytes()
    fixture_hash = sha(raw_records)
    rows = json.loads(raw_records)
    mf = json.loads(manifest.read_bytes())
    receipt_data = json.loads(receipt.read_bytes())
    must("canonical_real_bytes", encode(rows) == raw_records and fixture_hash not in {OLD, MOCK})
    must("fixture_receipt_custody", receipt_data["source_sha256"] == RUNNER_SHA
         and receipt_data["scorer_sha256"] == SCORER_SHA
         and receipt_data["underlying_inventory_sha256"] == T1
         and receipt_data["frozen_fixture_sha256"] == fixture_hash
         and receipt_data["per_case_manifest_sha256"] == sha(manifest.read_bytes())
         and receipt_data["actual_model_access"] is receipt_data["model_run"] is False)
    ids = set(range(N)) - {t1["eos_id"]}
    groups = {g: [row for row in rows if row["group"] == g] for g in GROUPS}
    pair_rows = groups["PAIRED_COUNTERFACTUAL"]
    train_by_id = {row["id"]: row for row in groups["TRAIN"]}
    must("counts_unique_context_and_ids", len(rows) == len({r["id"] for r in rows})
         == len({tuple(r["context"]) for r in rows}) == 80
         and Counter(r["group"] for r in rows) == GROUPS)
    must("case_group_sha_recomputed", mf["fixture_sha256"] == fixture_hash
         and mf["counts"] == GROUPS and mf["scorer_sha256"] == SCORER_SHA
         and mf["protocol_schema"] == "ttm.sm4m.q001.track_a.measurement.v3.integrated"
         and mf["case_sha256"] == {r["id"]: sha(encode(r)) for r in rows}
         and mf["group_sha256"] == {g: sha(encode(rs)) for g, rs in groups.items()})
    must("real_ids_candidates_and_oracle", all(
        len(r["context"]) == 9 and set(r["context"] + r["value_pool"]
        + r["choices"] + [r["no_answer"], r["gold"]]) <= ids
        and r["choices"] == choices_for(r)
        and r["gold"] == {r["context"][1]: r["context"][2],
                          r["context"][4]: r["context"][5]}.get(r["context"][7], r["no_answer"])
        for r in rows))
    def bindings(row):
        c = row["context"]
        return {(c[1], c[2]), (c[4], c[5])}

    train_bindings = set().union(*(bindings(row) for row in groups["TRAIN"]))
    clean_holdouts = groups["HELDOUT_RECOMBINED"] + groups["HELDOUT_ABSENT"]
    train_tokens = set().union(*(set(r["context"] + [r["gold"]]) for r in groups["TRAIN"]))
    novel_overlap = sum(any(r["context"][i] in train_tokens for i in (1, 2, 4, 5, 7))
                        for r in groups["HELDOUT_NOVEL_IDS"])
    leak_count = sum(bool(bindings(row) & train_bindings) for row in clean_holdouts)
    must("split_and_paired", leak_count == novel_overlap == 0
         and len({r["parent"] for r in pair_rows}) == 16
         and all(r["parent"] is None for r in rows if r["group"] != "PAIRED_COUNTERFACTUAL"))
    for row in pair_rows:
        parent = train_by_id[row["parent"]]
        swapped = list(parent["context"])
        swapped[2], swapped[5] = swapped[5], swapped[2]
        if row["context"] != swapped or row["gold"] == parent["gold"]:
            raise RuntimeError("pair_swap")
    checks["literal_parent_value_swap"] = True

    runner = import_file("review_target", tree / RUNNER)
    scorer = runner.track_a_v3()
    must("runner_readback_and_regeneration", runner.read_frozen_fixture(
        fixture, fixture_hash, allowed=sorted(ids)) == rows
         and encode(runner.fixture_generator(sorted(ids))) == raw_records)
    guard = import_file("review_release", tree / RUNNER.parent / "owner_internal_admission.py")
    must("owner_scope_pinned", guard.require_scope(root) is None)
    must("t1_guard_agrees", guard.original_token_ids(raw_t1) == sorted(ids)
         and rejected(lambda: guard.original_token_ids(raw_t1 + b" "), "ORIGINAL_BPE_SHA256"))
    verdict = json.loads(git_bytes(tree, "show", f"{BASE}:{guard.VERDICT_PATH}"))
    must("historical_i1_fails_release_validation", verdict["I1"] == "HOLD_I1"
         and rejected(lambda: guard.validate_verdict(verdict, runtime_sha256={}),
                      "OWNER_INTERNAL_I1_NOT_PASS"))

    rng = random.Random(16202611)
    shuffled_scores = list(range(N))
    rng.shuffle(shuffled_scores)
    control_fns = {
        "uniform": lambda r: [0.0] * N,
        "fixed_id_ascending": lambda r: list(range(N)),
        "fixed_id_descending": lambda r: list(range(N, 0, -1)),
        "fixed_seeded_random": lambda r: shuffled_scores,
        "constant_no_answer": lambda r: [int(i == rows[0]["no_answer"]) for i in range(N)],
        "first_value_without_query": lambda r: [int(i == r["context"][2]) for i in range(N)],
        "last_value_without_query": lambda r: [int(i == r["context"][5]) for i in range(N)],
        "explicit_oracle": lambda r: [int(i == {r["context"][1]: r["context"][2],
                              r["context"][4]: r["context"][5]}.get(r["context"][7], r["no_answer"]))
                               for i in range(N)],
    }
    control_results = {}
    permutation_trials = 0
    for name, produce in control_fns.items():
        counts = {}
        per_row = {}
        for group, members in groups.items():
            count = Counter(full_vocab=0, candidate_secondary=0,
                            full_vocab_abstain=0, candidate_abstain=0)
            for row in members:
                scores = produce(row)
                choices = list(row["choices"])
                gold = row["gold"]
                full = unique_max(scores, range(N))
                restricted = unique_max(scores, choices)
                rng.shuffle(choices)
                permutation_trials += 1
                if scorer.unique_top1((token, scores[token]) for token in choices) != restricted:
                    raise RuntimeError("choice_permutation")
                result = runner.evaluate_goldblind_logits(scores, row)
                peak = max(scores)
                expected_nll = (peak - scores[gold]) + math.log(
                    math.fsum(math.exp(s - peak) for s in scores))
                if (not math.isclose(result["gold_nll"], expected_nll, abs_tol=1e-12)
                        or result["gold_rank"] != 1 + sum(s > scores[gold] for s in scores)
                        or result["greedy_correct"] != (full == gold)
                        or result["candidate_correct"] != (restricted == gold)
                        or result["full_vocab_tie_abstained"] != (full is None)
                        or result["candidate_tie_abstained"] != (restricted is None)):
                    raise RuntimeError("independent_metric_crosscheck")
                count.update(full_vocab=int(full == gold), candidate_secondary=int(restricted == gold),
                             full_vocab_abstain=int(full is None), candidate_abstain=int(restricted is None))
                per_row[row["id"]] = full == gold
            counts[group] = dict(count)
        control_results[name] = {
            "groups": counts,
            "paired_both_full_vocab_correct": sum(
                per_row[r["id"]] and per_row[r["parent"]] for r in pair_rows),
        }
    checks["reference_metrics_and_rank_choice_permutations"] = True

    diverged = 0
    for row in groups["HELDOUT_NOVEL_IDS"]:
        outside = next(i for i in ids if i not in row["choices"])
        scores = [0] * N
        scores[row["gold"]], scores[outside] = 1, 2
        metrics = runner.evaluate_goldblind_logits(scores, row)
        diverged += metrics["candidate_correct"] and not metrics["greedy_correct"] and metrics["gold_rank"] == 2
    must("novel_candidate_full_vocab_divergence", diverged == 16)
    gold_mutations = matched_query_swaps = shuffled_rows_rejected = 0
    for row in rows:
        mutated = deepcopy(row)
        mutated["gold"] = next(c for c in row["choices"] if c != row["gold"])
        # A scorer given a different gold reads it only for endpoint calculations.
        scores = [int(i == row["gold"]) for i in range(N)]
        a = runner.evaluate_goldblind_logits(scores, row)
        b = runner.evaluate_goldblind_logits(scores, mutated)
        gold_mutations += (choices_for(mutated) == row["choices"]
                           and a["greedy_correct"] and not b["greedy_correct"])
        alternate = deepcopy(row)
        alternate["choices"].reverse()
        shuffled_rows_rejected += rejected(
            lambda: runner.evaluate_goldblind_logits(scores, alternate), "CHOICE_INTEGRITY")
        c = alternate["context"]
        if c[7] in (c[1], c[4]):
            c[7] = c[4] if c[7] == c[1] else c[1]
            alt_gold = c[2] if c[7] == c[1] else c[5]
            alternate["gold"] = alt_gold
            alternate["choices"] = choices_for(alternate)
            correct_scores = [int(i == alt_gold) for i in range(N)]
            matched_query_swaps += (not runner.evaluate_goldblind_logits(scores, alternate)["greedy_correct"]
                                    and runner.evaluate_goldblind_logits(correct_scores, alternate)["greedy_correct"])
    must("gold_only_metric_and_matched_query_swap",
         gold_mutations == shuffled_rows_rejected == 80 and matched_query_swaps == 64)

    import release_auth_v2 as release
    must("unsigned_or_forged_admission_fails_closed", rejected(
        lambda: release.authenticate_release(root / "never_opened.json", phase="run",
              runner_sha256=RUNNER_SHA, tokenizer_sha256=T1, underlying_sha256=T1,
              frozen_fixture_sha256=fixture_hash, project_root=root),
        "AUTHENTICATED_TRUST_ANCHORS_UNAVAILABLE"))
    must("live_historical_release_guard_holds", rejected(
        lambda: guard.published_fixture_sha256(root), "OWNER_INTERNAL_I1_NOT_PASS"))
    with tempfile.TemporaryDirectory(prefix="track_a_m0v3_independent_") as tmp:
        outside = Path(tmp).resolve()
        must("outside_trusted_root_denied", rejected(
            lambda: runner.exact_scoped_path(root, outside / "never_opened.json"),
            "DIRECT_CLI_PATH_ESCAPES_SIGNED_PROJECT"))
        with tempfile.TemporaryDirectory(prefix="track_a_m0v3_pathqa_", dir=fixture.parent) as probe:
            test_dir = Path(probe)
            junction = test_dir / "redirect"
            ps = "$ErrorActionPreference='Stop'; New-Item -ItemType Junction -Path $env:TRACK_A_JUNCTION -Target $env:TRACK_A_OUTSIDE | Out-Null"
            env = {k: v for k, v in os.environ.items() if k.casefold() != "psmodulepath"}
            env.update(TRACK_A_JUNCTION=str(junction), TRACK_A_OUTSIDE=str(outside))
            run = subprocess.run(["powershell.exe", "-NoProfile", "-NonInteractive",
                                  "-Command", ps], env=env, capture_output=True)
            must("native_junction_created_for_mock", run.returncode == 0 and junction.is_dir())
            try:
                must("junction_escape_rejected", rejected(
                    lambda: runner.exact_scoped_path(root, junction / "never_opened.json"),
                    "DIRECT_CLI_PATH_ESCAPES_SIGNED_PROJECT"))
                must("readback_rejects_reparse_path", rejected(
                    lambda: runner.read_frozen_fixture(junction, fixture_hash, allowed=sorted(ids)),
                    "FROZEN_FIXTURE_RECORDS_REPARSE"))
            finally:
                junction.rmdir()
            marker = test_dir / "DO_NOT_OVERWRITE"
            marker.write_bytes(b"qa")
            cfg = SimpleNamespace(root=str(root), token_inventory="", tokenizer_source="",
                                  owner_internal=True, out=str(test_dir))
            # Only the source admission is replaced by a synthetic allowed-ID pool.
            # The production path and overwrite checks still run.
            with patch.object(runner, "owner_admission", return_value=(list(range(300, 500)), None, None)):
                must("existing_output_refused_on_mock", rejected(
                    lambda: runner.fixture_freeze(cfg), "FIXTURE_FREEZE_OUTPUT_LOCATION")
                     and marker.read_bytes() == b"qa"
                     and not (test_dir / records.name).exists())

        scratch = Path(tmp)
        mock_meta, mock_raw = runner.mock_token_inventory()
        mock_rows = runner.fixture_generator(runner.permitted_ids(mock_meta, mock_raw))
        mock_mf = runner.case_and_group_manifest(mock_rows)
        scratch_records = scratch / records.name
        scratch_manifest = scratch / manifest.name
        mock_fixture_bytes = encode(mock_rows)
        scratch_records.write_bytes(mock_fixture_bytes + b" ")
        scratch_manifest.write_bytes(encode(mock_mf))
        load_mock = lambda: runner.read_frozen_fixture(scratch, mock_mf["fixture_sha256"],
                                                       mock_meta, mock_raw)
        must("fixture_byte_tamper_rejected", rejected(load_mock, "FROZEN_FIXTURE_BYTES_CHANGED"))
        scratch_records.write_bytes(mock_fixture_bytes)
        mock_mf_copy = deepcopy(mock_mf)
        mock_mf_copy["group_sha256"]["TRAIN"] = "0" * 64
        scratch_manifest.write_bytes(encode(mock_mf_copy))
        must("manifest_digest_tamper_rejected", rejected(load_mock, "MANIFEST_MISMATCH"))
        scratch_manifest.write_bytes(encode(mock_mf))
        must("mock_fixture_readback", load_mock() == mock_rows)

        scratch_runner, scratch_scorer = scratch / RUNNER, scratch / SCORER
        for dest, source in ((scratch_runner, tree / RUNNER), (scratch_scorer, tree / SCORER)):
            dest.parent.mkdir(parents=True, exist_ok=True)
            shutil.copyfile(source, dest)
        scratch_module = import_file("review_copy", scratch_runner)
        original = scratch_scorer.read_bytes()
        scratch_scorer.write_bytes(original + b"\n")
        must("scorer_text_tamper_rejected", rejected(scratch_module.track_a_v3, "SOURCE_SHA_MISMATCH"))

        # Compile a harmless marker against a timestamp/size of our scratch copy,
        # then restore the authentic source bytes and preserve its mtime.
        marker = b"INDEPENDENT_UNPINNED_BYTECODE_MARKER = True\n"
        scratch_scorer.write_bytes(marker + b" " * (len(original) - len(marker)))
        ts = scratch_scorer.stat()
        py_compile.compile(str(scratch_scorer), doraise=True,
                           invalidation_mode=py_compile.PycInvalidationMode.TIMESTAMP)
        scratch_scorer.write_bytes(original)
        os.utime(scratch_scorer, ns=(ts.st_atime_ns, ts.st_mtime_ns))
        must("scratch_python_text_hash_is_pinned", sha(scratch_scorer.read_bytes()) == SCORER_SHA)
        checks["scorer_sha_binds_executed_bytecode"] = not getattr(
            scratch_module.track_a_v3(), "INDEPENDENT_UNPINNED_BYTECODE_MARKER", False)

    shifted = [runner.evaluate_goldblind_logits([f32(1e20)] * N, r) for r in rows]
    shifted_nll = sorted({m["gold_nll"] for m in shifted})
    checks["primary_nll_additive_shift_invariance"] = all(
        math.isclose(m["gold_nll"], math.log(N), abs_tol=1e-12) for m in shifted)
    must("shifted_uniform_still_abstains", all(
         m["full_vocab_tie_abstained"] and m["candidate_tie_abstained"] for m in shifted))

    return {
        "source": {"git_head": PIN, "base_pr28_head": BASE, "ci_head": CI, "files": changed},
        "custody": {
            "fixture_sha256": fixture_hash,
            "fixture_manifest_sha256": sha(manifest.read_bytes()),
            "private_freeze_receipt_sha256": sha(receipt.read_bytes()),
            "private_t1_sha256": sha(raw_t1),
            "historical_fixture_sha256": sha(args.historical.read_bytes()),
            "case_sha256": mf["case_sha256"],
            "group_sha256": mf["group_sha256"],
            "group_counts": GROUPS, "train_binding_leak_rows": leak_count,
            "novel_id_overlap_rows": novel_overlap, "linked_parent_rows": len(pair_rows),
        },
        "controls": control_results,
        "permutation_trials": permutation_trials, "gold_mutations": gold_mutations,
        "negative_reordered_frozen_rows_rejected": shuffled_rows_rejected,
        "bound_query_swaps": matched_query_swaps,
        "novel_control_candidate_full_vocab_divergence": diverged,
        "uniform_shift": {"finite_float32_input": 1e20, "expected_full_vocab_nll": math.log(N),
                          "actual_full_vocab_nll_values": shifted_nll, "fixture_rows": len(rows)},
        "checks": checks,
        "scope": {"I2": "NOT_EXECUTED", "model_forwards": 0, "optimizer_steps": 0,
                  "checkpoint_access": False, "nonce_claimed": False},
    }


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    for option in ("tree", "root", "fixture", "tokenizer", "historical"):
        parser.add_argument(f"--{option}", type=Path, required=True)
    try:
        result = audit(parser.parse_args())
    except Exception as exc:
        # Never print exceptions that may interpolate private fixture data or paths.
        if type(exc) is RuntimeError and str(exc).replace("_", "").replace(".", "").isalnum():
            raise SystemExit("Independent check failed: " + str(exc)) from None
        raise SystemExit("Independent check failed: " + type(exc).__name__) from None
    print(json.dumps(result, indent=2, sort_keys=True))
