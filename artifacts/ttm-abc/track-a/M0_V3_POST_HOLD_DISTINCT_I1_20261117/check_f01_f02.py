"""Distinct Windows review of public source with synthetic inputs only."""

from collections import Counter
from decimal import Decimal, localcontext
import hashlib
import importlib.util
import json
import math
import os
from pathlib import Path
import py_compile
import struct
import subprocess
import sys
import types
from unittest.mock import patch


PIN = "ec197b5f00d3a037420390edd11ee55047e1d37f"
PRIOR = "05041501bfe84822feffd39290c6800b2152055a"
REVIEWER = "01a1e558-969b-7e43-85c2-6aaa8d4df3e5"
PREFIX = Path("tools/pilot_t4/direct_failure_diag_q001")
RUNNER = PREFIX / "preexec_candidate_20261116/ttm_sm4m_diag_q001.py"
SCORER = PREFIX / "track_a_m0_v3/q001_m0_goldblind.py"
WRAPPER = PREFIX / "track_a_m0_v3/Invoke-TrackA-M0V3-RealTokenizer-Freeze-PS51.ps1"
PINS = {
    RUNNER: ("20c147f9f2629c494c157da5bab3519e01d755096638adfd10e07bb5dda3c4b8",
             "9a6a6bbcdd1ce80d40cc40b2b6dce1b46ca2932806fc0f77b036681a401eee0e"),
    SCORER: ("2d0b980768a0ac3079f361d94244cd694c97ed90e978fc83fb7991dc82b5c2ac",
             "d76936db04caec358ddfb6947656d60023dee7de5c3388f810c7ecbf08288b63"),
    WRAPPER: ("6506ddf1e5b98793a4b2a3ba3b7aaf089f8692b64f4e0f6b53899b3c28d1a76d",
              "40b3bfc6c235e272f70b033d4cf75ed8baca38c84c01ee20aacd701e30b670e5"),
}
GROUPS = {
    "TRAIN": 24, "HELDOUT_RECOMBINED": 16, "HELDOUT_NOVEL_IDS": 16,
    "PAIRED_COUNTERFACTUAL": 16, "HELDOUT_ABSENT": 8,
}
RESULT = {"reviewer_thread": REVIEWER, "source_commit": PIN,
          "python": sys.version.split()[0], "checks": {}}


def sha(raw):
    return hashlib.sha256(raw).hexdigest()


def git_blob(root, rev, path):
    spec = f"{rev}:{path.as_posix()}"
    raw = subprocess.check_output(["git", "-C", str(root), "cat-file", "blob", spec])
    object_id = subprocess.check_output(["git", "-C", str(root), "rev-parse", spec]).strip()
    calculated = hashlib.sha1(f"blob {len(raw)}\0".encode("ascii") + raw).hexdigest()
    assert calculated.encode("ascii") == object_id
    return raw, calculated


def crlf(raw):
    assert b"\r" not in raw and raw.endswith(b"\n")
    return raw.replace(b"\n", b"\r\n")


def materialize(root, tree, rev, mode, paths):
    source_pins = {}
    for relative in paths:
        raw, object_id = git_blob(root, rev, relative)
        native = crlf(raw)
        if rev == PIN:
            assert (sha(raw), sha(native)) == PINS[relative]
        target = tree / relative
        target.parent.mkdir(parents=True, exist_ok=True)
        with target.open("xb") as handle:
            handle.write(raw if mode == "LF" else native)
        source_pins[target.name] = {"git_blob": object_id, "lf_sha": sha(raw),
                                    "crlf_sha": sha(native)}
    return source_pins


def run_buffer(path, name):
    module = types.ModuleType(name)
    module.__file__ = str(path)
    exec(compile(path.read_bytes(), str(path), "exec", dont_inherit=True), module.__dict__)
    return module


def f32(value):
    return struct.unpack("<f", struct.pack("<f", value))[0]


def nll_oracle(values, gold):
    with localcontext() as ctx:
        ctx.prec = 75
        target = Decimal.from_float(values[gold])
        counts = Counter(values)
        return float(sum(Decimal(count) * (Decimal.from_float(value) - target).exp()
                         for value, count in counts.items()).ln())


def held(label, expected, action):
    try:
        action()
    except (RuntimeError, ValueError) as exc:
        assert str(exc) == expected, (label, str(exc))
    else:
        raise AssertionError(f"{label}: unexpectedly accepted")
    RESULT["checks"][label] = expected


def numeric_replay(patched, previous):
    allowed = list(range(763, 939))
    rows = patched.fixture_generator(allowed)
    assert previous.fixture_generator(allowed) == rows
    assert Counter(row["group"] for row in rows) == GROUPS
    assert len(rows) == 80
    uniform_series = []
    for value in (f32(1e20), f32(-1e20), f32(3.4028235e38)):
        values = [value] * 2048
        observed_old = set()
        for row in rows:
            old_score = previous.evaluate_goldblind_logits(values, row)
            new_score = patched.evaluate_goldblind_logits(values, row)
            assert old_score["gold_nll"] == 0.0
            observed_old.add(old_score["gold_nll"])
            assert new_score["gold_nll"] == math.log(2048)
            assert new_score["gold_rank"] == 1
            assert new_score["full_vocab_tie_abstained"] is True
            assert new_score["candidate_tie_abstained"] is True
            assert new_score["greedy_correct"] is False
            assert new_score["candidate_correct"] is False
        uniform_series.append({"uniform_float32": value, "cases": len(rows),
                               "prior_nll": observed_old.pop(), "candidate_nll": math.log(2048),
                               "full_and_restricted_abstentions": len(rows)})
    RESULT["checks"]["uniform_full_vocab"] = uniform_series

    row = rows[57]
    gold = row["gold"]
    outside = next(token for token in range(2048) if token not in row["choices"])
    values = [-12.0] * 2048
    for index, token in enumerate(row["choices"]):
        values[token] = -2.0 - index * 0.25
    values[gold] = -0.75
    values[outside] = 0.125
    expected = nll_oracle(values, gold)
    shifted_nlls = []
    for shift in (0, 2**46, -(2**46)):
        shifted = [value + shift for value in values]
        assert [value - shift for value in shifted] == values
        score = patched.evaluate_goldblind_logits(shifted, row)
        assert math.isclose(score["gold_nll"], expected, rel_tol=0, abs_tol=3e-16)
        assert score["candidate_correct"] and not score["greedy_correct"]
        assert score["gold_rank"] == 2
        shifted_nlls.append({"shift": shift, "candidate_nll": score["gold_nll"],
                             "prior_nll": previous.evaluate_goldblind_logits(shifted, row)["gold_nll"]})
    RESULT["checks"]["nonuniform_oracle_and_translation"] = {
        "decimal_oracle": expected, "results": shifted_nlls,
        "full_rank": 2, "restricted_top1_correct": True, "full_top1_correct": False}
    held("reject_2047_logits", "HOLD_M0_LOGIT_SHAPE_OR_FINITE",
         lambda: patched.evaluate_goldblind_logits(values[:-1], row))
    held("reject_2049_logits", "HOLD_M0_LOGIT_SHAPE_OR_FINITE",
         lambda: patched.evaluate_goldblind_logits(values + [0.0], row))
    for name, invalid in (("inf", math.inf), ("nan", math.nan)):
        held(f"reject_{name}", "HOLD_M0_LOGIT_SHAPE_OR_FINITE",
             lambda: patched.evaluate_goldblind_logits(values[:-1] + [invalid], row))
    return allowed, rows


def forge_cache(scorer):
    raw = scorer.read_bytes()
    stat_before = scorer.stat()
    marker = b"DISTINCT_FORGED_TIMESTAMP_CACHE = True\n"
    scorer.write_bytes(marker + b"#" * (len(raw) - len(marker)))
    os.utime(scorer, ns=(stat_before.st_atime_ns, stat_before.st_mtime_ns))
    bytecode = Path(py_compile.compile(
        str(scorer), doraise=True,
        invalidation_mode=py_compile.PycInvalidationMode.TIMESTAMP))
    scorer.write_bytes(raw)
    os.utime(scorer, ns=(stat_before.st_atime_ns, stat_before.st_mtime_ns))
    restored = scorer.stat()
    header = bytecode.read_bytes()[:16]
    assert header[:4] == importlib.util.MAGIC_NUMBER
    assert unpack_pyc(header) == (0, int(restored.st_mtime), restored.st_size)
    assert scorer.read_bytes() == raw
    return bytecode


def unpack_pyc(header):
    return struct.unpack("<III", header[4:])


def symlink(path, target):
    try:
        path.symlink_to(target)
    except OSError as exc:
        if getattr(exc, "winerror", None) == 1314:
            return False
        raise
    return True


def cache_and_source(runner, old, candidate_path, old_path, scratch, mode):
    raw = candidate_path.read_bytes()
    compiled = forge_cache(candidate_path)
    before = sha(compiled.read_bytes())
    if old is not None:
        old_compiled = forge_cache(old_path)
        assert getattr(old.track_a_v3(), "DISTINCT_FORGED_TIMESTAMP_CACHE", False)
        assert old_compiled.is_file()
        RESULT["checks"]["historical_loader_cache_positive_control"] = True
    standard = importlib.util.spec_from_file_location("reviewer_standard_positive", candidate_path)
    positive = importlib.util.module_from_spec(standard)
    standard.loader.exec_module(positive)
    assert positive.DISTINCT_FORGED_TIMESTAMP_CACHE is True
    scorer = runner.track_a_v3()
    assert not hasattr(scorer, "DISTINCT_FORGED_TIMESTAMP_CACHE") and scorer.VOCAB == 2048
    assert sha(compiled.read_bytes()) == before
    RESULT["checks"][f"forged_{mode}_cache"] = {
        "timestamp_mode_accepted_standard_loader": True, "sentinel_executed_exact_runner": False,
        "cache_untouched": True, "scorer_sha256": sha(raw)}

    tamper = raw.replace(b"VOCAB = 2048", b"VOCAB = 2047", 1)
    assert len(tamper) == len(raw) and tamper != raw
    mixed = (crlf(raw).replace(b"\r\n", b"\n", 1) if mode == "LF"
             else raw.replace(b"\r\n", b"\n", 1))
    for label, changed in (("content_tamper", tamper), ("mixed_eol", mixed),
                           ("lone_cr", raw.replace(b"\n", b"\r", 1)),
                           ("utf8_bom", b"\xef\xbb\xbf" + raw)):
        candidate_path.write_bytes(changed)
        held(f"{mode}_{label}", "HOLD_TRACK_A_V3_SOURCE_SHA_MISMATCH", runner.track_a_v3)
    candidate_path.unlink()
    held(f"{mode}_cached_source_missing", "HOLD_TRACK_A_V3_SOURCE_MISSING", runner.track_a_v3)
    candidate_path.write_bytes(raw)
    external = scratch / f"linked_scorer_{mode}.py"
    external.write_bytes(tamper)
    candidate_path.unlink()
    if symlink(candidate_path, external):
        held(f"{mode}_linked_tampered_source", "HOLD_TRACK_A_V3_SOURCE_SHA_MISMATCH", runner.track_a_v3)
        external.write_bytes(raw)
        assert runner.track_a_v3().VOCAB == 2048
        RESULT["checks"][f"{mode}_linked_exact_source"] = "ACCEPTED_ONLY_PINNED_CODE_BUFFER"
        candidate_path.unlink()
    else:
        RESULT["checks"][f"{mode}_symlink"] = "SKIP_WINERROR_1314"
    candidate_path.write_bytes(raw)

    read = Path.read_bytes
    calls = 0

    def replace_after_read(path):
        nonlocal calls
        verified = read(path)
        if path == candidate_path:
            calls += 1
            candidate_path.write_bytes(tamper)
        return verified

    with patch.object(Path, "read_bytes", replace_after_read):
        assert runner.track_a_v3().VOCAB == 2048
    assert calls == 1 and candidate_path.read_bytes() == tamper
    RESULT["checks"][f"{mode}_source_changed_after_read"] = {"scorer_reads": calls,
                                                              "pinned_buffer_executed": True}
    candidate_path.write_bytes(raw)


def canonical(value):
    return (json.dumps(value, ensure_ascii=False, sort_keys=True, separators=(",", ":")) + "\n").encode()


def frozen_reader(runner, scratch, allowed, rows):
    fixture = scratch / "synthetic_reader_inputs"
    fixture.mkdir()
    records = fixture / "FIXTURE_RECORDS.json"
    manifest = fixture / "FIXTURE_MANIFEST.json"
    record_bytes = canonical(rows)
    records.write_bytes(record_bytes)
    record_sha = sha(record_bytes)
    real_pins = (runner.TRACK_A_V3_FROZEN_RECORDS_SHA256, runner.TRACK_A_V3_FROZEN_MANIFEST_SHA256)
    assert real_pins == ("823a08dd4be0da7748cb258b9bf5b2841dd1fdbac84956eb204be7ba57f8c55d",
                         "0b80368a6747994df5f5b8d0e7b35137266ac82f6c9b83d26af5b61f79b3cb04")
    current = {
        "protocol_schema": "ttm.sm4m.q001.track_a.measurement.v3.integrated",
        "scorer_sha256": PINS[SCORER][0], "fixture_sha256": record_sha,
        "case_sha256": {row["id"]: sha(canonical(row)) for row in rows},
        "group_sha256": {group: sha(canonical([row for row in rows if row["group"] == group]))
                         for group in GROUPS},
        "counts": GROUPS,
    }
    assert runner.case_and_group_manifest(rows) == current
    manifest.write_bytes(canonical(current))
    read = lambda: runner.read_frozen_fixture(fixture, record_sha, allowed=allowed)
    assert read() == rows
    RESULT["checks"]["mock_current_manifest"] = {"cases": 80, "groups": 5}

    legacy = dict(current, scorer_sha256=runner.TRACK_A_V3_PRE_REPAIR_SCORER_SHA256)
    legacy_bytes = canonical(legacy)
    manifest.write_bytes(legacy_bytes)
    hold_manifest = "HOLD_FROZEN_CASE_OR_GROUP_MANIFEST_MISMATCH"
    held("real_pins_reject_synthetic_legacy", hold_manifest, read)
    with patch.object(runner, "TRACK_A_V3_FROZEN_RECORDS_SHA256", record_sha), patch.object(
            runner, "TRACK_A_V3_FROZEN_MANIFEST_SHA256", sha(legacy_bytes)):
        assert read() == rows
        RESULT["checks"]["mock_legacy_manifest_exact_match"] = True
        manifest.write_bytes(legacy_bytes + b"\n")
        held("mock_legacy_reject_semantically_equal_byte_tamper", hold_manifest, read)
        changed = dict(legacy, counts=dict(GROUPS, TRAIN=25))
        tampered = canonical(changed)
        manifest.write_bytes(tampered)
        with patch.object(runner, "TRACK_A_V3_FROZEN_MANIFEST_SHA256", sha(tampered)):
            held("mock_legacy_reject_extra_semantic_delta_even_with_byte_pin", hold_manifest, read)
        wrong_scorer = canonical(dict(legacy, scorer_sha256="c" * 64))
        manifest.write_bytes(wrong_scorer)
        with patch.object(runner, "TRACK_A_V3_FROZEN_MANIFEST_SHA256", sha(wrong_scorer)):
            held("mock_legacy_reject_wrong_historical_scorer_even_with_byte_pin", hold_manifest, read)
        manifest.write_bytes(legacy_bytes)
        records.write_bytes(record_bytes + b"\n")
        held("mock_legacy_reject_semantically_equal_record_byte_tamper",
             "HOLD_FROZEN_FIXTURE_BYTES_CHANGED", read)
        records.write_bytes(record_bytes)
        held("mock_legacy_reject_wrong_signed_records_digest", "HOLD_FROZEN_FIXTURE_BYTES_CHANGED",
             lambda: runner.read_frozen_fixture(fixture, "f" * 64, allowed=allowed))
        for file, country in ((records, "RECORDS"), (manifest, "MANIFEST")):
            external = scratch / (file.name + ".linked")
            data = file.read_bytes()
            external.write_bytes(data)
            file.unlink()
            if symlink(file, external):
                held(f"mock_legacy_{country.lower()}_symlink",
                     f"HOLD_FROZEN_FIXTURE_{country}_REPARSE", read)
                file.unlink()
            else:
                RESULT["checks"][f"mock_legacy_{country.lower()}_symlink"] = "SKIP_WINERROR_1314"
            file.write_bytes(data)
    assert (runner.TRACK_A_V3_FROZEN_RECORDS_SHA256,
            runner.TRACK_A_V3_FROZEN_MANIFEST_SHA256) == real_pins


def main(root, scratch):
    targets = {name: scratch / name for name in ("candidate_lf", "candidate_crlf", "historical_crlf")}
    for tree in targets.values():
        tree.mkdir()
    RESULT["source_pins"] = materialize(root, targets["candidate_lf"], PIN, "LF", PINS)
    assert materialize(root, targets["candidate_crlf"], PIN, "CRLF", PINS) == RESULT["source_pins"]
    materialize(root, targets["historical_crlf"], PRIOR, "CRLF", (RUNNER, SCORER))
    lf = run_buffer(targets["candidate_lf"] / RUNNER, "review_lf")
    native = run_buffer(targets["candidate_crlf"] / RUNNER, "review_crlf")
    old = run_buffer(targets["historical_crlf"] / RUNNER, "review_before_fix")
    allowed, rows = numeric_replay(lf, old)
    for mode, runner, tree in (("LF", lf, targets["candidate_lf"]),
                                ("CRLF", native, targets["candidate_crlf"])):
        cache_and_source(runner, old if mode == "CRLF" else None,
                         tree / SCORER, targets["historical_crlf"] / SCORER, scratch, mode)
    frozen_reader(native, scratch, allowed, rows)
    RESULT["checker_sha256"] = sha(Path(__file__).read_bytes())
    skipped = sum(str(value).startswith("SKIP_") for value in RESULT["checks"].values())
    RESULT["counts"] = {"checks_passed": len(RESULT["checks"]) - skipped, "checks_skipped": skipped}
    output = json.dumps(RESULT, sort_keys=True, indent=2) + "\n"
    with (scratch / "independent_posthold_result.json").open("x", encoding="utf-8", newline="\n") as f:
        f.write(output)
    print(output, end="")


if __name__ == "__main__":
    assert sys.dont_write_bytecode and sys.flags.isolated
    main(Path(sys.argv[1]), Path(sys.argv[2]))
