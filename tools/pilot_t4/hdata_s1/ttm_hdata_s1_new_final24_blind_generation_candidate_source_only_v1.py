#!/usr/bin/env python3
"""H-DATA-S1 NEW FINAL24 owner-only generation candidate.

DEFAULT: --mode source-only prints only code/intended contract, no FINAL,
no checkpoint load, model forward, scoring, key or secret mapping read.
--mode generate is NOT authorized by this source commit. A *separate* explicit
owner FINAL24 permit, pinned by its exact SHA-256, is mandatory. Never rerun
a partially consumed FINAL or modify an existing output directory.
"""
from __future__ import annotations

import argparse
import base64
import collections
import hashlib
import importlib.util
import json
import os
from pathlib import Path
import sys
import zipfile

RUN_ID = "TTM_SMALL4M_HDATA_S1_MATCHED_BUDGET_FRESH_FINAL_V1"
CHECKOUT_SHA = "7aec0d551c930936412b93eb49951bd1597d71b9"
SCIENCE_LOCK_SHA = "85e744a3da8d0e417079f726d95f059ad569a5f13e592ee56c1982dbce0aa540"
PARENT_SHA = "cb985751795c8328ad65acf7ca4c1033ce35182c1bfbdb8c38550de629cb271b"
BPE_SHA = "cba18e60cee3d08a353ee6d4a451017289e45af7b4b1179c87171b9b78d7dfdc"
FINAL_OWNER_SHA = "b129a5c52520a25f1c40de950471622320abfa6b5414d0b16e0111ed96adc680"
FINAL_COMMITMENT_SHA = "6c8c21c406b4bc30171244142c4226460a6735164f88fd425db7afa070a6f4f3"
ESCROW_CIPHERTEXT_SHA = "de0562cd4a9584ca8128e505b14e3d04ae35793b72f7d8a2b4d4f6eb0176cc7d"
ESCROW_ZIP_SHA = "c5c5d6eae6ce38d892348878ae200d5bbcd42406b53f7b0c43e8876a145d48d4"
H0_SHA = "a7cdade3b70cb2ceed258edd1e3edd494ce9745633d2e528ee90232f3c95c2fe"
H1_SHA = "31d9365a470e638f77e6661252ed8d0605e9f9095da145d9f48751adcdcfcb64"
P02_GIT_BLOB = "9762343e06cf800b50574c2871ae1ed58537fb18"
BPE_GIT_BLOB = "fa5bd892941ba5aa6e6b2f0b2b0ae974efe297b6"
AES_GIT_BLOB = "c85b8c63a008abcad65ee546b06db44d19ae26be"
EXPECTED_TORCH = "2.14.1+cu130"
DRIVE_OWNER = Path("/content/drive/MyDrive/TTM/ttm-small-pilot/ttm_small4m_h_data_s1_20261113")
SCIENCE_ROOT = DRIVE_OWNER / "science_one_shot_v1"
FINAL_ROOT = DRIVE_OWNER / "new_final24_blind_generation_once_v1"
MAX_NEW_TOKENS = 64
CONTEXT = 256
EOS_ID = 256


def need(ok, code):
    if not ok:
        raise RuntimeError("HDATA_S1_FINAL24_GENERATION_HOLD:" + code)


def sha(path):
    h = hashlib.sha256()
    with Path(path).open("rb") as f:
        for block in iter(lambda: f.read(1024 * 1024), b""):
            h.update(block)
    return h.hexdigest()


def blob(path):
    b = Path(path).read_bytes()
    return hashlib.sha1(b"blob " + str(len(b)).encode() + b"\0" + b).hexdigest()


def read_pinned(path, digest):
    p = Path(path)
    need(p.is_file() and not p.is_symlink(), "REQUIRED_FILE:" + p.name)
    need(sha(p) == digest, "SHA_DRIFT:" + p.name)
    return json.loads(p.read_bytes())


def import_blob(path, name, digest):
    p = Path(path)
    need(p.is_file() and not p.is_symlink() and blob(p) == digest, "SOURCE_BLOB:" + name)
    spec = importlib.util.spec_from_file_location(name, p)
    need(spec is not None and spec.loader is not None, "SOURCE_IMPORT:" + name)
    module = importlib.util.module_from_spec(spec)
    sys.modules[name] = module
    spec.loader.exec_module(module)
    return module


def write_new(path, data):
    p = Path(path)
    with p.open("xb") as f:
        f.write(data)
        f.flush()
        os.fsync(f.fileno())


def canonical(obj):
    return json.dumps(obj, sort_keys=True, ensure_ascii=False,
                      separators=(",", ":")).encode("utf-8")


def source_only():
    return {
        "schema": "ttm.hdata_s1.final24_generation_candidate.source_only.v1",
        "status": "SOURCE_ONLY_FINAL_OWNER_RELEASE_NOT_GRANTED",
        "run_id": RUN_ID,
        "science_lock_sha256": SCIENCE_LOCK_SHA,
        "h0_step1152_sha256": H0_SHA,
        "h1_step1152_sha256": H1_SHA,
        "final24_owner_prompt_sha256": FINAL_OWNER_SHA,
        "public_final24_commitment_sha256": FINAL_COMMITMENT_SHA,
        "encrypted_mapping_sha256": ESCROW_CIPHERTEXT_SHA,
        "decoding": {"policy": "plain_greedy_argmax", "new_tokens_cap": MAX_NEW_TOKENS,
                     "eos_id": EOS_ID, "context": CONTEXT, "no_repetition_penalty": True},
        "rater_packet": "24 neutral LEFT/RIGHT pairs; 48 continuations; no model/anchor/map identifiers",
        "scoring": "NO_SCORING; 240 judgments+24 notes only after independent blind rater",
        "generate_requires_owner_final_permit_sha256": True,
        "new_final_plaintext_read": False,
        "aes_key_read": False,
        "model_import_or_forward": False,
        "optimizer_updates": 0,
        "TEST_Q1_Q2_OOD_access": False,
    }


def check_permit(args, selfsha):
    # First gate before ANY FINAL/model/secret access; only a separate future
    # file explicitly authorized by the owner can release this source.
    need(args.permit is not None and args.permit_sha is not None,
         "EXPLICIT_NEW_FINAL24_OWNER_PERMIT_NOT_SUPPLIED")
    permit = read_pinned(args.permit, args.permit_sha)
    need(permit.get("schema") == "ttm.hdata_s1.owner_final24_generation_permit.v1" and
         permit.get("authorization") == "GO_HDATA_S1_NEW_FINAL24_ONE_SHOT_OWNER_INFERENCE" and
         permit.get("explicit_owner_decision") is True and
         permit.get("run_id") == RUN_ID and
         permit.get("generator_source_sha256") == selfsha and
         permit.get("science_lock_sha256") == SCIENCE_LOCK_SHA and
         permit.get("h0_checkpoint_sha256") == H0_SHA and
         permit.get("h1_checkpoint_sha256") == H1_SHA and
         permit.get("final_owner_prompt_sha256") == FINAL_OWNER_SHA and
         permit.get("AES_escrow_sha256") == ESCROW_CIPHERTEXT_SHA and
         permit.get("single_run_root") == str(FINAL_ROOT) and
         permit.get("unblind_authorized") is False and
         permit.get("scoring_authorized") is False and
         permit.get("no_training") is True,
         "INVALID_OR_DRIFTED_FINAL24_OWNER_PERMIT")
    return permit


def verify_private_prompts(owner_path, commitment_path):
    # Only in separately authorized --mode generate.
    owner = read_pinned(owner_path, FINAL_OWNER_SHA)
    commitment = read_pinned(commitment_path, FINAL_COMMITMENT_SHA)
    prompts = owner.get("prompts")
    need(isinstance(prompts, list) and len(prompts) == 36, "OWNER_PROMPT_COUNT")
    finals = prompts[12:]
    locked = commitment.get("committed_prompt_hashes")
    need(isinstance(locked, list) and len(locked) == 24, "FINAL_COMMITMENT_COUNT")
    seen = set()
    out = []
    for i, (item, frozen) in enumerate(zip(finals, locked), 1):
        pid = f"HF{i:02d}"
        need(item.get("id") == pid and frozen.get("id") == pid and
             item.get("stratum") == frozen.get("stratum") and
             item.get("cohort") == frozen.get("cohort") == "BLIND_FINAL",
             "PROMPT_SEQUENCE_OR_STRATUM_DRIFT")
        text = item.get("prompt")
        need(isinstance(text, str) and bool(text) and text == text.strip() and
             "\n" not in text, "FINAL_PROMPT_TEXT_SCOPE")
        digest = hashlib.sha256(text.encode("utf-8")).hexdigest()
        need(digest == item.get("prompt_utf8_sha256") ==
             frozen.get("prompt_utf8_sha256"), "PROMPT_SHA:" + pid)
        need(digest not in seen, "PROMPT_DUPLICATE")
        seen.add(digest)
        out.append((pid, text))
    need(len(out) == 24, "FINAL_PAIRS_COUNT")
    return out, locked


def decrypt_private_mapping(escrow_zip_path, locked_commitment, aes_source):
    # Never writes owner key or plaintext mapping to disk.
    zpath = Path(escrow_zip_path)
    need(zpath.is_file() and not zpath.is_symlink() and sha(zpath) == ESCROW_ZIP_SHA,
         "OWNER_PRIVATE_ZIP_SHA")
    from cryptography.hazmat.primitives.ciphers.aead import AESGCM
    with zipfile.ZipFile(zpath) as z:
        names = z.namelist()
        e_name = aes_source.ESCROW_NAME
        k_name = aes_source.KEY_NAME
        need(e_name in names and k_name in names, "PRIVATE_AES_FILES_MISSING")
        e_bytes, k_bytes = z.read(e_name), z.read(k_name)
    need(hashlib.sha256(e_bytes).hexdigest() == ESCROW_CIPHERTEXT_SHA,
         "ESCROW_CIPHERTEXT_SHA")
    e = json.loads(e_bytes)
    k = json.loads(k_bytes)
    need(e.get("schema") == "ttm.hdata_s1.encrypted_blind_escrow.v1" and
         e.get("run_id") == k.get("run_id") == RUN_ID and
         e.get("commitment_sha256") == FINAL_COMMITMENT_SHA and
         k.get("public_escrow_sha256") == ESCROW_CIPHERTEXT_SHA,
         "AES_ESCROW_METADATA")
    aad = aes_source.AAD
    need(base64.b64decode(e["aad_b64"]) == aad, "AES_AAD_DRIFT")
    plain = AESGCM(base64.b64decode(k["key_b64"])).decrypt(
        base64.b64decode(e["nonce_b64"]),
        base64.b64decode(e["ciphertext_b64"]), aad)
    need(hashlib.sha256(plain).hexdigest() ==
         e["plaintext_mapping_sha256"] == k["mapping_sha256"], "AES_MAP_SHA")
    obj = json.loads(plain)
    aes_source.validate_pairs(obj["pairs"], locked_commitment)
    return obj["pairs"]


def greedy64(model, bpe, text, torch, device):
    prefix = bpe.encode(text)
    need(prefix and EOS_ID not in prefix and len(prefix) + MAX_NEW_TOKENS <= CONTEXT,
         "FINAL_CONTEXT_OR_EOS")
    need(bpe.decode(prefix) == text, "FINAL_BPE_ROUNDTRIP")
    sequence = list(prefix)
    generated = []
    stopped_eos = False
    model.eval()
    with torch.inference_mode():
        for _ in range(MAX_NEW_TOKENS):
            tokens = torch.tensor([sequence], dtype=torch.long, device=device)
            logits, _ = model(tokens)
            next_id = int(torch.argmax(logits[0, -1, :]).item())
            if next_id == EOS_ID:
                stopped_eos = True
                break
            generated.append(next_id)
            sequence.append(next_id)
    continuation = bpe.decode(generated)  # strict UTF-8, no invisible repair
    return continuation, {"generated_tokens": len(generated),
                          "ended_eos": stopped_eos,
                          "ended_cap64": not stopped_eos and len(generated) == MAX_NEW_TOKENS,
                          "word_count": len(continuation.split())}


def generate_once(args):
    selfsha = sha(__file__)
    check_permit(args, selfsha)  # BEFORE torch import, NEW FINAL, AES key, checkpoint
    import torch
    need(torch.cuda.is_available() and torch.cuda.device_count() == 1 and
         "T4" in torch.cuda.get_device_name(0) and
         str(torch.__version__) == EXPECTED_TORCH, "EXACT_T4_RUNTIME")
    need(args.frozen_repo is not None and args.bpe is not None and
         args.owner_final is not None and args.owner_escrow_zip is not None and
         args.parent is not None, "REQUIRED_PINNED_INPUTS")
    repo = Path(args.frozen_repo)
    src = repo / "tools" / "pilot_t4"
    p02_path = src / "integrated" / "p02_source_exact.py"
    bpe_source = src / "integrated" / "source_t2" / "ttm_gpt2_bpe2048.py"
    aes_source = src / "hdata_s1" / "ttm_hdata_s1_owner_blind_escrow_v1.py"
    commitment_path = (repo / "docs" / "research" / "ttm-small4m-h-data-s1" /
                       "TTM_HDATA_S1_NEW_FINAL24_PUBLIC_SHA_COMMITMENT_20261113.json")
    need(repo.is_dir() and not repo.is_symlink(), "FROZEN_SOURCE_REPO")
    need(SCIENCE_ROOT.is_dir() and not SCIENCE_ROOT.is_symlink() and
         DRIVE_OWNER.is_dir() and not FINAL_ROOT.exists() and
         not FINAL_ROOT.is_symlink(), "ONE_SHOT_EXISTING_OR_MISSING_SCIENCE_ROOT")
    parent_path = Path(args.parent)
    need(parent_path.is_file() and not parent_path.is_symlink() and
         sha(parent_path) == PARENT_SHA, "FROZEN_PARENT_SHA")
    p02 = import_blob(p02_path, "hdata_final24_p02_pinned", P02_GIT_BLOB)
    bpe_module = import_blob(bpe_source, "hdata_final24_bpe_pinned", BPE_GIT_BLOB)
    aes_module = import_blob(aes_source, "hdata_final24_aes_pinned", AES_GIT_BLOB)
    bpe_manifest = read_pinned(args.bpe, BPE_SHA)
    bpe = bpe_module.BPE2048.from_manifest(bpe_manifest)
    prompts, locked = verify_private_prompts(args.owner_final, commitment_path)
    pairs = decrypt_private_mapping(args.owner_escrow_zip, locked, aes_module)
    parent = torch.load(args.parent, map_location="cpu", weights_only=True)
    need(parent.get("step") == 1024 and
         parent.get("schema") == "ttm.t4.science.checkpoint.v1", "PARENT_SOURCE_SCHEMA")
    need(parent["config"].get("max_seq_len") == CONTEXT, "MODEL_CONTEXT_256")
    checkpoint_paths = {"H0": args.h0_checkpoint, "H1": args.h1_checkpoint}
    state = {}
    for arm, expected in (("H0", H0_SHA), ("H1", H1_SHA)):
        path = checkpoint_paths[arm]
        need(path is not None, "FINAL_CHECKPOINT_PATH:" + arm)
        p = Path(path)
        need(p.is_file() and not p.is_symlink() and sha(p) == expected,
             "FINAL_CHECKPOINT_SHA:" + arm)
        snap = torch.load(p, map_location="cpu", weights_only=True)
        need(snap.get("run_id") == RUN_ID and
             snap.get("arm") == arm and snap.get("step") == 1152,
             "FINAL_CHECKPOINT_CUSTODY:" + arm)
        need(set(("model", "optimizer", "scheduler", "sampler_state",
                  "grad_scaler_state", "h1_exposure", "torch_cpu_rng",
                  "torch_cuda_rng", "python_rng", "numpy_rng")) <= set(snap),
             "FULL_RESUMABLE_STATE:" + arm)
        state[arm] = snap["model"]

    # Create immutable destination only after every input has been checked.
    FINAL_ROOT.mkdir(exist_ok=False)
    write_new(FINAL_ROOT / "STARTED_NO_REPLAY.json",
              canonical({"schema": "ttm.hdata_s1.final24_consumption_sentinel.v1",
                         "run_id": RUN_ID, "final_owner_sha256": FINAL_OWNER_SHA,
                         "generator_source_sha256": selfsha,
                         "permit_sha256": args.permit_sha,
                         "unblind": False}) + b"\n")

    os.environ["CUBLAS_WORKSPACE_CONFIG"] = ":4096:8"
    torch.backends.cuda.matmul.allow_tf32 = False
    torch.backends.cudnn.allow_tf32 = False
    torch.backends.cudnn.deterministic = True
    torch.backends.cudnn.benchmark = False
    torch.use_deterministic_algorithms(True)

    outputs = {}
    counts = {}
    for arm in ("H0", "H1"):
        model = p02.GPT(p02.P02Config(**parent["config"])).to("cuda")
        model.load_state_dict(state[arm], strict=True)
        model.eval()
        per = []
        metrics = []
        for pid, prompt in prompts:
            text, metric = greedy64(model, bpe, prompt, torch, "cuda")
            per.append((pid, text))
            metrics.append(metric)
        outputs[arm] = dict(per)
        counts[arm] = {"eos": sum(x["ended_eos"] for x in metrics),
                       "cap64": sum(x["ended_cap64"] for x in metrics),
                       "under8_word": sum(x["word_count"] < 8 for x in metrics)}
        del model
        torch.cuda.empty_cache()

    lefts = {p["prompt_id"]: p["left_arm"] for p in pairs}
    need(set(lefts) == {pid for pid, _ in prompts}, "PAIR_COVERAGE")
    packet = {"schema": "ttm.hdata_s1.neutral_blind_final24.rater_packet.v1",
              "rater_classification": "EXPLORATORY_SCOPED_AI_REVIEW_IF_AI",
              "run_id": RUN_ID, "blind": True,
              "instructions": "Score all five frozen rubric axes per side (240 integer scores), 24 nonempty notes; freeze SHA before owner unblind. No anchor metadata.",
              "records": []}
    for i, (pid, prompt) in enumerate(prompts, 1):
        left = lefts[pid]
        right = "H1" if left == "H0" else "H0"
        packet["records"].append({
            "pair_id": f"R{i:02d}", "prompt_text": prompt,
            "LEFT": outputs[left][pid], "RIGHT": outputs[right][pid]
        })
    need(len(packet["records"]) == 24 and
         all(not any(k in p for k in ("left_arm", "right_arm", "actor_anchor",
                                      "object_anchor", "goal_anchor")) for p in packet["records"]),
         "RATER_PACKET_LEAK")
    packet_data = canonical(packet) + b"\n"
    write_new(FINAL_ROOT / "BLIND_FINAL24_RATER_PACKET.json", packet_data)
    receipt = {"schema": "ttm.hdata_s1.final24_owner_generation_receipt.v1",
               "run_id": RUN_ID, "status": "GENERATED_PENDING_BLIND_RATER",
               "rater_packet_sha256": hashlib.sha256(packet_data).hexdigest(),
               "generator_source_sha256": selfsha,
               "permit_sha256": args.permit_sha,
               "prompt_count": 24, "continuation_count": 48,
               "decoding": "plain_greedy64_or_EOS",
               "arm_counts_OWNER_ONLY_NOT_FOR_RATER": counts,
               "NEW_FINAL_generation": "EXECUTED_ONCE",
               "blind_scoring": "NOT_EXECUTED",
               "unblind": "NOT_EXECUTED"}
    write_new(FINAL_ROOT / "OWNER_PRIVATE_GENERATION_RECEIPT.json",
              canonical(receipt) + b"\n")
    print("H_DATA_S1_FINAL24_GENERATION=ONE_SHOT_COMPLETE_PENDING_BLIND_RATING")
    print("H_DATA_S1_BLIND_PACKET_SHA256=" + receipt["rater_packet_sha256"])
    print("H_DATA_S1_UNBLIND=NOT_EXECUTED")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--mode", choices=("source-only", "generate"), default="source-only")
    for key in ("permit", "permit_sha", "frozen_repo", "parent", "bpe",
                "owner_final", "owner_escrow_zip", "h0_checkpoint", "h1_checkpoint"):
        ap.add_argument("--" + key.replace("_", "-"))
    a = ap.parse_args()
    if a.mode == "source-only":
        print(json.dumps(source_only(), sort_keys=True))
        return
    generate_once(a)


if __name__ == "__main__":
    main()
