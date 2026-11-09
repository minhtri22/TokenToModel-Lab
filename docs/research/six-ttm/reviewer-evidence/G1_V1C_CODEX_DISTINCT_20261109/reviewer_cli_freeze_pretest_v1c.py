"""Independent pre-TEST CLI replay with in-memory synthetic security adapters.

Only TRAIN/DEV synthetic arrays are supplied. No owner credential, model,
private dataset or TEST pack is created, opened or passed to the functions.
"""

import hashlib
import json
import sys
from pathlib import Path
from unittest.mock import patch

import numpy as np

import g1_science_core_v1b as old
import g1_science_core_v1c as new


ROOT = Path(__file__).resolve().parent
FIXTURES = ROOT / "reviewer_cli_fixture_20261109"
RUN_ID = "SYNTHETIC_CLI_PRETEST_ONLY"
rng = np.random.default_rng(91365)
weight = rng.normal(size=(12, 20))
probe = rng.normal(size=(20, 8))


def make_split(label, count):
    source = rng.normal(size=(count, 12))
    target = source @ weight + 0.02 * rng.normal(size=(count, 20))
    response = target @ probe + 0.01 * rng.normal(size=(count, 8))
    ids = np.array([
        hashlib.sha256(f"SYNTHETIC_CLI_{label}_{i}".encode()).hexdigest()
        for i in range(count)
    ])
    return {"ids": ids, "s": source, "t": target, "r": response}


train = make_split("TRAIN", 128)
dev = make_split("DEV", 64)


def exercise(module, version):
    work = FIXTURES / version / "ttm_six_g1_science_private"
    work.mkdir(parents=True, exist_ok=False)
    freeze = work / "G1_FIT_DEV_FROZEN.json"
    marker = work / "G1_TEST_READ_ONE_SHOT_CONSUMED.marker"
    counts = {"TRAIN": 0, "DEV": 0, "TEST": 0}
    admission = {"pack_sha_by_split": {"TRAIN": "a" * 64, "DEV": "b" * 64}}

    def fake_load(path, split, manifest, **kwargs):
        if split not in ("TRAIN", "DEV"):
            raise AssertionError("UNAUTHORIZED_TEST_LOADER_REACHED")
        counts[split] += 1
        return train if split == "TRAIN" else dev

    def synthetic_commit(path, content, root):
        assert path == freeze and root == work
        path.write_bytes(content)
        return hashlib.sha256(content).hexdigest()

    def synthetic_read(path, root, **kwargs):
        assert path == freeze and root == work
        return freeze.read_bytes()

    def invoke(mode):
        argv = ["reviewer-cli", "--mode", mode, "--work", str(work),
                "--permit", str(work / "NOT_A_CREDENTIAL"), "--run-id", RUN_ID]
        # The entry point executes normally. Security boundary and file IO
        # inputs are replaced only for this isolated fixture test.
        with patch.object(module, "permit_check", return_value=admission), \
             patch.object(module, "manifest_check", return_value={"synthetic": True}), \
             patch.object(module, "load_pack", side_effect=fake_load), \
             patch.object(module.guard, "commit_immutable_bytes", side_effect=synthetic_commit), \
             patch.object(module.guard, "read_private_bytes", side_effect=synthetic_read), \
             patch.object(Path, "read_text", return_value="{}"), \
             patch.object(sys, "argv", argv):
            module.main()

    invoke("prepare")
    assert freeze.is_file() and not marker.exists()
    admission["fit_sha256"] = hashlib.sha256(freeze.read_bytes()).hexdigest()
    try:
        invoke("finalize")
    except RuntimeError as exc:
        code = str(exc)
    else:
        raise AssertionError(f"{version} SHOULD_STOP_BEFORE_TEST")
    expected = "STOP_G1_FIT_DEV_SELECTION_CHANGED" if version == "v1b" else "STOP_G1_TEST_PACK_SHA_MISSING"
    assert code == expected, (version, code, expected)
    assert counts["TEST"] == 0 and not marker.exists()
    return {"version": version, "prepare": "PASS", "finalize_pretest_stop": code,
            "test_pack_open_attempts": counts["TEST"], "test_marker_consumed": marker.exists(),
            "fixture_only": True, "freeze_sha256": admission["fit_sha256"]}


if __name__ == "__main__":
    results = [exercise(old, "v1b"), exercise(new, "v1c")]
    print("REVIEWER_CLI_SUMMARY=" + json.dumps(results, sort_keys=True))
