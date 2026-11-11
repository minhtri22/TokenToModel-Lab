#!/usr/bin/env python3
"""FRESH16 V2: exact-source CPU PREPARE/one-shot RUN. Never runs on import.

PREPARE performs no model forward, sampling, or training. RUN requires a separate,
SHA-pinned owner permit, an anchored blind map, and a preexisting PREPARED receipt.
Private mapping, raw outputs, and blind packet never leave the project root.
"""
from __future__ import annotations

import argparse
import ctypes
import hashlib
import importlib.util
import json
import os
from pathlib import Path
import random
import secrets
import subprocess
import sys
import time

ROOT = Path(r"D:\WORK\RESEARCH\TokenToModel-Lab")
BRANCH = "research/ttm-small4m-prompt-adherence-continuation-design-20261111"
REL = "tools/research/ttm_small4m_quality_gap/ttm_fresh16_v2_e0.py"
PROMPTS = "artifacts/research/ttm-small4m-quality-gap/TTM_FRESH_CONTINUATION_PROMPT_SET_CANDIDATE_V1_20261111.json"
RUBRIC = "artifacts/research/ttm-small4m-quality-gap/TTM_FRESH16_FROZEN_RUBRIC_AND_PREREG_CANDIDATE_20261111.json"
V2 = "docs/research/ttm-small4m-quality-gap/TTM_FRESH16_SCORING_AMENDMENT_V2_ACTION_ROLE_BINDING_TWO_LOCKS_CANDIDATE_20261111.md"
P02 = "src/p02/transformer_core.py"
BPE = "tools/pilot_t1t3/source_t2/ttm_gpt2_bpe2048.py"
BPE_MANIFEST = "_tmp/ttm_t1_real_source_v1/T1_BPE2048_REAL_TRAIN_MANIFEST.json"
CHECKPOINTS = {
    1024: ("_tmp/ttm_causal6_source_h512_stage_20261109/input/checkpoint.pt", "cb985751795c8328ad65acf7ca4c1033ce35182c1bfbdb8c38550de629cb271b", 45074891),
    1280: ("_tmp/ttm_fresh16_inputs_20261111/checkpoint_step1280.pt", "ee723407b2c25a18be20e26387a3dd8e4a18e2942d469279b6f0748ff86af0dc", 45075275),
}
BLOBS = {
    PROMPTS: "6299a073f0b7c7f8ea890ba9d9b29eaed9442f1f",
    RUBRIC: "69668664df23d2246cd65935ab049054aea43e7a",
    V2: "27b994b3b3283b2611af21d63acc5d37abf45013",
    P02: "9762343e06cf800b50574c2871ae1ed58537fb18",
    BPE: "fa5bd892941ba5aa6e6b2f0b2b0ae974efe297b6",
}
BPE_SHA = "cba18e60cee3d08a353ee6d4a451017289e45af7b4b1179c87171b9b78d7dfdc"
MERGES_SHA = "aea0e2a1a1bc1943f20b767ba2f879e3a47f0cb43b8b66026b1a34a038e014af"
CONFIG = dict(vocab_size=2048, max_seq_len=256, n_embd=256, n_layer=4, n_head=4, norm_type="layernorm")
EXPECTED_PARAMS = 3749376
MAX_SECONDS = 900
MAX_PROCESS_BYTES = 8 * 1024 ** 3
MAP_ANCHOR_REL = "artifacts/research/ttm-small4m-quality-gap/TTM_FRESH16_V2_PRIVATE_MAP_SHA_ANCHOR.json"


def need(test, label):
    if not test:
        raise RuntimeError(label)


def sha(path):
    h = hashlib.sha256()
    with Path(path).open("rb") as f:
        for chunk in iter(lambda: f.read(1024 * 1024), b""):
            h.update(chunk)
    return h.hexdigest()


def git_blob(path):
    raw = Path(path).read_bytes()
    return hashlib.sha1(b"blob " + str(len(raw)).encode() + b"\0" + raw).hexdigest()


def project_file(root, value):
    path = Path(value)
    if not path.is_absolute():
        path = root / path
    path = path.resolve(strict=True)
    need(path.is_relative_to(root) and path != root, "ESCAPE_PROJECT_ROOT")
    need(path.is_file() and not path.is_symlink(), "MISSING_OR_LINKED_FILE")
    return path


def project_dir_target(root, value):
    path = Path(value)
    if not path.is_absolute():
        path = root / path
    need(not path.exists() and not path.is_symlink(), "RUN_DIR_EXISTS_NO_RETRY")
    parent = path.parent.resolve(strict=True)
    need(parent.is_relative_to(root) and parent != root and parent.is_dir(), "OUTPUT_PARENT_OUTSIDE_ROOT")
    need(path.name not in ("", ".", ".."), "BAD_RUN_DIRECTORY")
    return parent / path.name


def git(work, *args):
    p = subprocess.run(["git", "-C", str(work), *args], capture_output=True, text=True, timeout=30, check=False)
    need(p.returncode == 0, "GIT_READ_FAILED:" + p.stderr[-250:])
    return p.stdout.strip()


def load_json(path):
    return json.loads(Path(path).read_text(encoding="utf-8"))


def new_json(path, object_):
    with Path(path).open("x", encoding="utf-8", newline="\n") as f:
        json.dump(object_, f, ensure_ascii=False, indent=2, sort_keys=True)
        f.write("\n")
        f.flush()
        os.fsync(f.fileno())


def module(path, name):
    spec = importlib.util.spec_from_file_location(name, path)
    need(spec is not None and spec.loader is not None, "MODULE_IMPORT_SPEC_MISSING")
    mod = importlib.util.module_from_spec(spec)
    sys.modules[name] = mod
    spec.loader.exec_module(mod)
    return mod


def fixed_source(root, work, expected_head):
    need(os.name == "nt" and sys.version_info[:2] == (3, 12), "WIN_PYTHON312_REQUIRED")
    need(root == ROOT.resolve(strict=True), "WRONG_TTM_ROOT")
    need(work.is_relative_to(root) and work != root, "INVALID_WORKTREE")
    need(git(work, "branch", "--show-current") == BRANCH, "WRONG_RESEARCH_BRANCH")
    need(git(work, "rev-parse", "HEAD") == expected_head, "UNEXPECTED_HEAD")
    need(not git(work, "status", "--porcelain", "--untracked-files=all"), "DIRTY_WORKTREE")
    for rel, wanted in BLOBS.items():
        path = project_file(root, work / rel)
        need(git_blob(path) == wanted and git(work, "rev-parse", "HEAD:" + rel) == wanted,
             "FROZEN_SOURCE_MISMATCH:" + rel)
    runner = project_file(root, work / REL)
    need(git_blob(runner) == git(work, "rev-parse", "HEAD:" + REL), "RUNNER_SOURCE_NOT_COMMITTED")
    return git_blob(runner)


def validate_inputs(root, work):
    import torch
    need(torch.device("cpu").type == "cpu", "CPU_NOT_AVAILABLE")
    prompt = load_json(work / PROMPTS)["new_prompts"]
    rub = load_json(work / RUBRIC)
    need(len(prompt) == 16 and [p["id"] for p in prompt] ==
         [f"CP{i:02d}-{v}" for i in range(1, 9) for v in "AB"], "PROMPT_SHAPE_CHANGED")
    need(rub["fixture_contract"]["primary"]["H1"]["required_min"] == 12 and
         rub["fixture_contract"]["primary"]["H2"]["required_min"] == 6, "H1_H2_CHANGED")
    manifest = project_file(root, BPE_MANIFEST)
    need(sha(manifest) == BPE_SHA, "BPE_MANIFEST_SHA_MISMATCH")
    obj = load_json(manifest)
    need(obj.get("source_kind") == "PINNED_TINYSTORIES_TRAIN" and
         obj.get("token_merges_sha256") == MERGES_SHA, "BPE_PROVENANCE_CHANGED")
    bpe_module = module(work / BPE, "ttm_fresh16_v2_bpe")
    bpe = bpe_module.BPE2048.from_manifest(obj)
    encoded = {}
    for row in prompt:
        ids = bpe.encode(row["prompt_text"])
        need(0 < len(ids) <= 192 and 256 not in ids and bpe.decode(ids) == row["prompt_text"],
             "BPE_ENCODING_INVALID:" + row["id"])
        encoded[row["id"]] = ids
    p02 = module(work / P02, "ttm_fresh16_v2_p02")
    need(p02.P02Config(**CONFIG).max_seq_len == 256, "P02_CONFIG_INCOMPATIBLE")
    model = p02.GPT(p02.P02Config(**CONFIG)).cpu()
    need(sum(p.numel() for p in model.parameters()) == EXPECTED_PARAMS, "TRAINED_ARCH_PARAM_COUNT_MISMATCH")
    cp_readback = {}
    for step, (rel, expected_sha, n) in CHECKPOINTS.items():
        checkpoint = project_file(root, rel)
        need(checkpoint.stat().st_size == n and sha(checkpoint) == expected_sha,
             "CHECKPOINT_SOURCE_SHA_MISMATCH:" + str(step))
        record = torch.load(checkpoint, map_location="cpu", weights_only=True)
        need(isinstance(record, dict) and record.get("schema") == "ttm.t4.science.checkpoint.v1" and
             record.get("step") == step and record.get("config") == CONFIG and
             record.get("p02_git_blob") == BLOBS[P02] and isinstance(record.get("model"), dict),
             "CHECKPOINT_ARCH_METADATA_INVALID:" + str(step))
        model.load_state_dict(record["model"], strict=True)   # NO FORWARD; shape-only model compatibility
        need(all(t.isfinite().all().item() for t in record["model"].values()),
             "CHECKPOINT_NONFINITE_WEIGHTS:" + str(step))
        cp_readback[str(step)] = {"sha256": expected_sha, "bytes": n, "step": step,
                                  "schema": record["schema"], "config": CONFIG,
                                  "state_dict_keys": len(record["model"])}
        del record
    del model
    return bpe, encoded, cp_readback


def make_map(prompts):
    rng = random.SystemRandom()
    entries = []
    for step in (1024, 1280):
        for i in range(1, 9):
            pair = "CP%02d" % i
            opaque_pair = secrets.token_hex(16)
            for v in ("A", "B"):
                entries.append({"opaque_id": secrets.token_hex(16), "opaque_pair_id": opaque_pair,
                                "checkpoint_step": step, "prompt_id": pair + "-" + v,
                                "pair_id": pair, "variant": v})
    rng.shuffle(entries)
    need(len(entries) == 32 and len({x["opaque_id"] for x in entries}) == 32 and
         len({x["opaque_pair_id"] for x in entries}) == 16 and
         set(x["prompt_id"] for x in entries) == set(p["id"] for p in prompts), "MAP_CARDINALITY_FAILED")
    return {"schema": "ttm.fresh16.v2.sealed_map.v1", "secret_nonce": secrets.token_hex(32),
            "mapping": entries, "private_do_not_publish": True}


def map_validate(data):
    entries = data["mapping"]
    need(data.get("schema") == "ttm.fresh16.v2.sealed_map.v1" and len(entries) == 32,
         "SEALED_MAP_SCHEMA_INVALID")
    need(len({x["opaque_id"] for x in entries}) == 32 and
         len({x["opaque_pair_id"] for x in entries}) == 16, "SEALED_MAP_DUPLICATE_IDS")
    pairs = {}
    for e in entries:
        pairs.setdefault(e["opaque_pair_id"], []).append(e)
    need(all(len(two) == 2 and two[0]["checkpoint_step"] == two[1]["checkpoint_step"] and
             two[0]["pair_id"] == two[1]["pair_id"] and
             {two[0]["variant"], two[1]["variant"]} == {"A", "B"} for two in pairs.values()),
         "MAP_PAIR_INVALID")
    return entries


def prepare(root, work, head, run_dir):
    script_blob = fixed_source(root, work, head)
    _, encoded, readback = validate_inputs(root, work)  # NO MODEL FORWARD
    prompts = load_json(work / PROMPTS)["new_prompts"]
    sealed = make_map(prompts)
    target = project_dir_target(root, run_dir)
    target.mkdir(parents=False, exist_ok=False)
    map_path = target / "BLIND_MAP_PRIVATE.json"
    new_json(map_path, sealed)
    mp_sha = sha(map_path)
    receipt = {"schema": "ttm.fresh16.v2.e0.prepared.v1", "source_head": head,
               "runner_git_blob": script_blob, "runner_sha256": sha(work / REL),
               "original_prompt_blob": BLOBS[PROMPTS], "rubric_blob": BLOBS[RUBRIC],
               "adopted_v2_blob": BLOBS[V2], "bpe_manifest_sha256": BPE_SHA,
               "checkpoint_readback": readback, "sealed_map_sha256": mp_sha,
               "encoded_prompt_token_lengths": {k: len(v) for k, v in encoded.items()},
               "outputs_expected": 32, "pairings_expected": 16,
               "inference_executed": False, "training_executed": False,
               "TEST_read": False, "S1_actual_identity": "UNASSIGNED",
               "S2_actual_identity": "UNASSIGNED", "map_anchor_commit": "NOT_ANCHORED",
               "owner_science_GO": "NOT_ISSUED", "decision": "NO_GO_HOLD"}
    new_json(target / "PREPARED.json", receipt)
    print("FRESH16_E0_PREPARE=PASS_SOURCE_ONLY_NO_FORWARD", flush=True)
    print("FRESH16_E0_MAP_SHA256=" + mp_sha, flush=True)
    print("FRESH16_E0_RUNNER_GIT_BLOB=" + script_blob, flush=True)
    print("FRESH16_E0_PREPARED_SHA256=" + sha(target / "PREPARED.json"), flush=True)
    print("FRESH16_E0_EXECUTION=NO_GO_HOLD", flush=True)


def memory_bytes():
    # Windows process working-set hard cap, with no third-party process module.
    class PMC(ctypes.Structure):
        _fields_ = [("cb", ctypes.c_ulong), ("PageFaultCount", ctypes.c_ulong),
                    ("PeakWorkingSetSize", ctypes.c_size_t), ("WorkingSetSize", ctypes.c_size_t),
                    ("QuotaPeakPagedPoolUsage", ctypes.c_size_t), ("QuotaPagedPoolUsage", ctypes.c_size_t),
                    ("QuotaPeakNonPagedPoolUsage", ctypes.c_size_t), ("QuotaNonPagedPoolUsage", ctypes.c_size_t),
                    ("PagefileUsage", ctypes.c_size_t), ("PeakPagefileUsage", ctypes.c_size_t)]
    pmc = PMC()
    pmc.cb = ctypes.sizeof(PMC)
    ok = ctypes.windll.psapi.GetProcessMemoryInfo(ctypes.windll.kernel32.GetCurrentProcess(),
                                                   ctypes.byref(pmc), pmc.cb)
    need(bool(ok), "MEMORY_CAP_MEASUREMENT_FAILED")
    return pmc.WorkingSetSize


def execute(root, work, head, run_dir, permit_path, permit_sha, map_anchor_commit):
    import torch
    need(permit_path is not None and len(permit_sha) == 64 and len(map_anchor_commit) == 40,
         "SCIENCE_GO_PERMIT_NOT_PROVIDED")
    script_blob = fixed_source(root, work, head)
    directory = project_file(root, run_dir / "PREPARED.json").parent
    sealed_path = project_file(root, directory / "BLIND_MAP_PRIVATE.json")
    prepared = load_json(directory / "PREPARED.json")
    need(prepared["source_head"] == head and prepared["runner_git_blob"] == script_blob and
         prepared["runner_sha256"] == sha(work / REL) and
         prepared["sealed_map_sha256"] == sha(sealed_path), "PREPARED_SOURCE_OR_MAP_DRIFT")
    entry = map_validate(load_json(sealed_path))
    permit = project_file(root, permit_path)
    need(sha(permit) == permit_sha, "PERMIT_FILE_SHA_INVALID")
    auth = load_json(permit)
    need(auth.get("decision") == "GO_32_CPU_ONE_SHOT" and
         auth.get("source_head") == head and auth.get("runner_git_blob") == script_blob and
         auth.get("sealed_map_sha256") == sha(sealed_path) and
         auth.get("map_anchor_commit") == map_anchor_commit and
         auth.get("S1_rater_session") and auth.get("S2_adjudicator_session") and
         auth["S1_rater_session"] != auth["S2_adjudicator_session"], "GO_CONTRACT_NOT_SATISFIED")
    anchor = load_json_from_git(work, map_anchor_commit, MAP_ANCHOR_REL)
    need(anchor.get("sealed_map_sha256") == sha(sealed_path) and
         anchor.get("source_head") == head, "MAP_SHA_NOT_GIT_ANCHORED")
    need(not (directory / "RUN_STARTED.json").exists(), "ONE_SHOT_ALREADY_STARTED_NO_RETRY")
    bpe, encoded, _ = validate_inputs(root, work)  # static loader compatibility; no forward until marker
    started = {"schema": "ttm.fresh16.v2.run_started.v1", "time_unix": time.time(),
               "permit_sha256": permit_sha, "map_sha256": sha(sealed_path),
               "source_head": head, "runner_git_blob": script_blob,
               "no_retry": True, "outcome": "IN_PROGRESS_OR_STOP_PRESERVE"}
    new_json(directory / "RUN_STARTED.json", started)  # one-way science entry, before first forward
    t0 = time.monotonic()
    prompts = {p["id"]: p["prompt_text"] for p in load_json(work / PROMPTS)["new_prompts"]}
    p02 = module(work / P02, "ttm_fresh16_v2_p02_live")
    results = []
    # No test/validation/train data are read; only 2 immutable checkpoint state_dicts.
    with (directory / "RAW_OUTPUTS_PRIVATE.jsonl").open("x", encoding="utf-8", newline="\n") as out:
        for step in (1024, 1280):
            cp = project_file(root, CHECKPOINTS[step][0])
            payload = torch.load(cp, map_location="cpu", weights_only=True)
            need(payload["config"] == CONFIG and payload["step"] == step, "RUN_CHECKPOINT_CONFIG_CHANGED")
            model = p02.GPT(p02.P02Config(**CONFIG)).cpu()
            model.load_state_dict(payload["model"], strict=True)
            model.eval()
            del payload
            for e in entry:
                if e["checkpoint_step"] != step:
                    continue
                ids = list(encoded[e["prompt_id"]])
                generated = []
                why = "MAX_64_NEW_TOKENS"
                with torch.inference_mode():
                    for _ in range(64):
                        need(time.monotonic() - t0 < MAX_SECONDS, "CPU_WALL_CAP_EXCEEDED_NO_RETRY")
                        need(memory_bytes() < MAX_PROCESS_BYTES, "CPU_PROCESS_MEMORY_CAP_EXCEEDED_NO_RETRY")
                        seq = torch.tensor([ids + generated], dtype=torch.long, device="cpu")
                        logits, _ = model(seq)
                        token = int(torch.argmax(logits[0, -1, :]).item())
                        if token == 256:
                            why = "EOS_256"
                            break
                        generated.append(token)
                # Do not 'repair' broken UTF-8 output; preserve raw token IDs and stop.
                generated_text = bpe.decode(generated)
                row = {"opaque_id": e["opaque_id"], "generated_token_ids": generated,
                       "generated_text_only": generated_text, "stop_reason": why,
                       "n_new_tokens": len(generated)}
                out.write(json.dumps(row, ensure_ascii=False, sort_keys=True) + "\n")
                out.flush()
                os.fsync(out.fileno())
                results.append(row)
            del model
    need(len(results) == 32 and len({r["opaque_id"] for r in results}) == 32,
         "INCOMPLETE_OUTPUTS_NO_SUBSTITUTION")
    result_by = {r["opaque_id"]: r for r in results}
    s1 = [{"opaque_id": e["opaque_id"], "prompt_text": prompts[e["prompt_id"]],
           "generated_text_only": result_by[e["opaque_id"]]["generated_text_only"]} for e in entry]
    new_json(directory / "S1_BLIND_PACKET_PRIVATE.json", {"schema": "ttm.fresh16.v2.s1_packet.v1", "records": s1})
    new_json(directory / "RUN_FINISHED.json", {"schema": "ttm.fresh16.v2.run_finished.v1",
             "original_outputs": 32, "raw_outputs_sha256": sha(directory / "RAW_OUTPUTS_PRIVATE.jsonl"),
             "S1_packet_sha256": sha(directory / "S1_BLIND_PACKET_PRIVATE.json"),
             "seconds": time.monotonic() - t0, "inference_executed": True, "training_executed": False})
    print("FRESH16_E0_RUN=ONE_SHOT_32_OUTPUTS_COMPLETE", flush=True)
    print("FRESH16_E0_S1_PACKET_SHA256=" + sha(directory / "S1_BLIND_PACKET_PRIVATE.json"), flush=True)


def load_json_from_git(work, commit, rel):
    need(len(commit) == 40 and all(c in "0123456789abcdef" for c in commit), "ANCHOR_BAD_SHA")
    p = subprocess.run(["git", "-C", str(work), "show", commit + ":" + rel],
                       capture_output=True, timeout=30, check=False)
    need(p.returncode == 0, "COMMITTED_MAP_ANCHOR_MISSING_FETCH_THE_COMMIT")
    return json.loads(p.stdout.decode("utf-8"))


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--mode", required=True, choices=("prepare", "run"))
    ap.add_argument("--project-root", required=True, type=Path)
    ap.add_argument("--worktree", required=True, type=Path)
    ap.add_argument("--expected-head", required=True)
    ap.add_argument("--run-dir", required=True, type=Path)
    ap.add_argument("--permit", type=Path)
    ap.add_argument("--permit-sha256", default="")
    ap.add_argument("--map-anchor-commit", default="")
    a = ap.parse_args()
    root = a.project_root.resolve(strict=True)
    work = a.worktree.resolve(strict=True)
    if a.mode == "prepare":
        need(a.permit is None, "PREPARE_MUST_NOT_HAVE_GO_PERMIT")
        prepare(root, work, a.expected_head, a.run_dir)
    else:
        execute(root, work, a.expected_head, a.run_dir, a.permit, a.permit_sha256, a.map_anchor_commit)


if __name__ == "__main__":
    try:
        main()
    except (OSError, ValueError, KeyError, TypeError, RuntimeError, ImportError) as e:
        print("FRESH16_E0_HOLD=" + type(e).__name__ + ":" + str(e), file=sys.stderr, flush=True)
        raise SystemExit(2)
