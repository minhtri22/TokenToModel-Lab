#!/usr/bin/env python3
"""G1 private TRAIN-only hash-ID prefix manifest, no science, no GPU.

Modes: selftest (stdlib, no writes), preflight (read-only), tokenizers (download
ONLY tokenizer/config metadata into project), seal (requires explicit owner
CDLA/private-scope acknowledgment, reads original TRAIN text once, writes
hash-only G1 manifest+receipt within project). No original TTM VAL/TEST text.
This is a pre-science manifest producer; does not authorize G1 science.
"""
from __future__ import annotations
import argparse
import hashlib
import io
import json
import os
from pathlib import Path
import re
import subprocess
import sys
import unicodedata

ROOT = Path(r"D:\WORK\RESEARCH\TokenToModel-Lab")
SRC = Path("datasets/tinystories_v1_original_pinned/TinyStories-train.txt")
T1 = Path("_tmp/ttm_t1_real_source_v1/T1_STORY_SPLIT_IDS_NO_RAW_TEXT.json")
T1_SHA = "9f2ebaca821bddf0a9d7ae30ccfcef34561b968b21159aa913794298235a2fa9"
TRAIN_SHA = "c5cf5e22ff13614e830afbe61a99fbcbe8bcb7dd72252b989fa1117a368d401f"
T1_REV = "f54c09fd23315a6f9c86f9dc80f725de7d8f9c64"
SOURCE_CODE_COMMIT = "b57b44e7287f842e81050c1faee337f636333dd0"
SOURCE_CODE_BLOB = "3ef500ddd8259153e7e3d4602915a51b7060a40f"
MODEL_REVS = {
    "qwen06": ("Qwen/Qwen3-0.6B", "c1899de289a04d12100db370d81485cdf75e47ca"),
    "qwen17": ("Qwen/Qwen3-1.7B", "70d244cc86ccca08cf5af4e1e306ecf908b1ad5e"),
}
TOK_FILES = ("tokenizer.json", "tokenizer_config.json", "vocab.json",
             "merges.txt", "config.json", "special_tokens_map.json")
WORK = Path("_tmp/ttm_six_g1_private_manifest_v1")
TOKEN_SUBDIR = "tokenizers"
OUT = "G1_PREFIX_IDS_128_64_64_PRIVATE_METADATA.json"
READY = "G1_PREFIX_MANIFEST_READY.json"
ACK = "YES_PRIVATE_COMPUTATIONAL_G1_NO_RAW_PUBLICATION"
EOS = b"<|endoftext|>"
EXPECTED_COUNTS = {"TRAIN": 2048, "VAL": 256, "TEST": 64}
G1_COUNTS = {"TRAIN": 128, "DEV": 64, "TEST": 64}
PREFIX_SEED = "TTM_SIX_G1_V1|"
CHUNK = 1 << 20

def ensure(ok: bool, message: str) -> None:
    if not ok:
        raise RuntimeError(message)

def sha_bytes(b: bytes) -> str:
    return hashlib.sha256(b).hexdigest()

def canonical(obj: object) -> bytes:
    return (json.dumps(obj, ensure_ascii=False, sort_keys=True,
                       separators=(",", ":")) + "\n").encode("utf-8")

def sha_file(p: Path) -> str:
    h = hashlib.sha256()
    with p.open("rb") as f:
        for block in iter(lambda: f.read(8*CHUNK), b""):
            h.update(block)
    return h.hexdigest()

def assert_non_link(p: Path) -> None:
    ensure(p.exists(), "REQUIRED_PATH_MISSING:" + str(p))
    ensure(not p.is_symlink() and not p.is_junction(), "REPARSE_POINT_REFUSED:" + str(p))

def check_root() -> Path:
    ensure(os.name == "nt", "WINDOWS_ONLY_PROJECT_LOCAL_EXECUTION")
    assert_non_link(ROOT)
    root = ROOT.resolve(strict=True)
    ensure(str(root).casefold() == str(ROOT).casefold(), "PROJECT_ROOT_MISMATCH")
    for path in (root / ".git", root / "_tmp", root / "datasets",
                 root / "datasets/tinystories_v1_original_pinned",
                 root / SRC, root / T1):
        assert_non_link(path)
        ensure(path.resolve(strict=True).is_relative_to(root), "PATH_ESCAPES_PROJECT")
    result = subprocess.run(["git", "-C", str(root), "remote", "get-url", "origin"],
                            check=False, capture_output=True, text=True, timeout=12)
    ensure(result.returncode == 0, "GIT_ORIGIN_LOOKUP_FAIL")
    origin = result.stdout.strip().lower()
    ensure(origin in {
        "https://github.com/minhtri22/tokentomodel-lab",
        "https://github.com/minhtri22/tokentomodel-lab.git",
        "git@github.com:minhtri22/tokentomodel-lab",
        "git@github.com:minhtri22/tokentomodel-lab.git",
    }, "WRONG_GIT_ORIGIN")
    return root

def read_t1(root: Path) -> dict:
    data = (root / T1).read_bytes()  # tiny metadata only; not TTM TEST text
    ensure(sha_bytes(data) == T1_SHA, "T1_MANIFEST_PIN_MISMATCH")
    m = json.loads(data.decode("utf-8"))
    ensure(m.get("schema") == "ttm.t1.real.stories.split.v1", "T1_SCHEMA")
    ensure(m.get("revision") == T1_REV, "T1_REVISION")
    ensure(m.get("repo") == "roneneldan/TinyStories", "T1_REPO")
    ensure(m.get("license") == "CDLA-Sharing-1.0", "T1_LICENSE")
    ensure(m.get("source_sha256", {}).get("TinyStories-train.txt") == TRAIN_SHA,
           "T1_TRAIN_SOURCE_PIN")
    ids = m["splits"]
    seen: set[str] = set()
    for group, count in EXPECTED_COUNTS.items():
        entries = ids[group]
        ensure(len(entries) == count, "T1_SPLIT_COUNT:" + group)
        for digest in entries:
            ensure(isinstance(digest, str) and
                   re.fullmatch(r"[0-9a-f]{64}", digest) is not None,
                   "T1_INVALID_STORY_ID")
            ensure(digest not in seen, "T1_SPLIT_COLLISION")
            seen.add(digest)
    ensure(len(seen) == 2368, "T1_UNIQUE_COUNT")
    return m

def iter_story_bytes(fd, h=None):
    # Exact T1 parser: chunked b'<|endoftext|>' separator, .strip(b' \t\r\n').
    buffer = b""
    while True:
        data = fd.read(CHUNK)
        if not data:
            break
        if h is not None:
            h.update(data)
        buffer += data
        while True:
            k = buffer.find(EOS)
            if k < 0:
                break
            part = buffer[:k].strip(b" \t\r\n")
            buffer = buffer[k + len(EOS):]
            if part:
                yield part
        ensure(len(buffer) <= (1 << 23), "STORY_OVER_8MIB")
    tail = buffer.strip(b" \t\r\n")
    if tail:
        yield tail

def normalize_story(raw: str) -> str:
    return unicodedata.normalize("NFC", raw).replace("\r\n", "\n").replace("\r", "\n").strip().replace("\n", " ")

def prefix_candidate(text: str):
    # End offsets count Unicode codepoints, not bytes or token positions.
    end = next((i+1 for i,c in enumerate(text) if c in ".!?" and
                80 <= i+1 <= 192), None)
    if end is None:
        end = next((i for i,c in enumerate(text) if c.isspace() and
                    128 <= i <= 192), None)
    if end is None:
        return None, "NO_APPROVED_BOUNDARY"
    prefix = text[:end]
    if sum(not c.isspace() for c in prefix) < 12:
        return None, "PREFIX_TOO_SHORT"
    return (prefix, end), None

def source_key(original_row: int, norm_sha: str) -> str:
    return sha_bytes((PREFIX_SEED + str(original_row) + "|" + norm_sha).encode("utf-8"))

def scan_source(root: Path, idset: set[str]):
    selected = {}
    occurrences = {}
    n_rows = 0
    h = hashlib.sha256()
    # Read only TinyStories-train.txt. VALID source is never opened.
    with (root / SRC).open("rb") as fd:
        for n_rows, raw in enumerate(iter_story_bytes(fd, h), start=1):
            ensure(b"\x00" not in raw and EOS not in raw, "BAD_RAW_STORY_BYTES")
            story_id = sha_bytes(raw)  # exact T1: sha(text.encode('utf8'))
            if story_id not in idset:
                continue
            occurrences[story_id] = occurrences.get(story_id, 0) + 1
            if story_id not in selected:
                text = raw.decode("utf-8", "strict")
                selected[story_id] = (n_rows - 1, text)  # first occurrence, zero-based
    ensure(h.hexdigest() == TRAIN_SHA, "ORIGINAL_TRAIN_FILE_SHA_MISMATCH")
    ensure(set(selected) == idset, "T1_TRAIN_IDS_NOT_RESOLVED")
    return selected, occurrences, n_rows

def file_hashes(path: Path) -> dict:
    result = {}
    for file in TOK_FILES:
        p = path / file
        if p.is_file():
            assert_non_link(p)
            result[file] = sha_file(p)
    ensure("tokenizer.json" in result and "tokenizer_config.json" in result
           and "config.json" in result, "TOKENIZER_REQUIRED_FILE_MISSING")
    return result

def prepare_environment(root: Path) -> Path:
    work = root / WORK
    ensure(work.is_relative_to(root), "OUTPUT_OUTSIDE_PROJECT")
    if work.exists():
        assert_non_link(work)
    else:
        work.mkdir(parents=True, exist_ok=False)
    # Prevent HF/Transformers/temp/cache writes outside TTM project.
    for key, sub in (("HF_HOME", "hf_home"),
                     ("HF_HUB_CACHE", "hf_home/hub"),
                     ("HF_DATASETS_CACHE", "hf_home/datasets"),
                     ("XDG_CACHE_HOME", "xdg_cache"),
                     ("TMP", "tmp"), ("TEMP", "tmp"), ("TMPDIR", "tmp")):
        p = work / sub
        p.mkdir(parents=True, exist_ok=True)
        os.environ[key] = str(p)
    os.environ["PYTHONDONTWRITEBYTECODE"] = "1"
    os.environ["HF_HUB_DISABLE_TELEMETRY"] = "1"
    sys.dont_write_bytecode = True
    return work

def fetch_tokenizers(work: Path):
    from huggingface_hub import snapshot_download
    target = work / TOKEN_SUBDIR
    target.mkdir(parents=True, exist_ok=True)
    results = {}
    for short, (repo, revision) in MODEL_REVS.items():
        path = target / short
        ensure(not path.exists(), "TOKENIZER_DIR_EXISTS_NO_OVERWRITE:" + short)
        snapshot_download(repo_id=repo, revision=revision, local_dir=str(path),
                          allow_patterns=list(TOK_FILES), max_workers=1)
        hashes = file_hashes(path)
        results[short] = {"repo": repo, "revision": revision, "file_sha256": hashes}
    payload = {"schema": "ttm.six.g1.tokenizers.metadata.v1",
               "weights_downloaded": False, "science_executed": False,
               "tokenizers": results}
    dest = work / "G1_TOKENIZER_METADATA_PIN.json"
    with dest.open("xb") as f:
        f.write(canonical(payload))
    return dest

def load_pinned_tokenizers(work: Path):
    from transformers import AutoTokenizer
    pin_path = work / "G1_TOKENIZER_METADATA_PIN.json"
    ensure(pin_path.is_file(), "TOKENIZER_METADATA_PIN_MISSING")
    pin = json.loads(pin_path.read_text(encoding="utf-8"))
    ensure(pin.get("schema") == "ttm.six.g1.tokenizers.metadata.v1",
           "TOKENIZER_PIN_SCHEMA_MISMATCH")
    tok = {}
    for short, (repo, rev) in MODEL_REVS.items():
        meta = pin["tokenizers"][short]
        ensure(meta["repo"] == repo and meta["revision"] == rev,
               "TOKENIZER_REVISION_PIN_MISMATCH")
        path = work / TOKEN_SUBDIR / short
        hashes = file_hashes(path)
        ensure(hashes == meta["file_sha256"], "TOKENIZER_BYTES_CHANGED:" + short)
        tokenizer = AutoTokenizer.from_pretrained(str(path), local_files_only=True,
                      trust_remote_code=False, use_fast=True)
        ensure(tokenizer.is_fast, "FAST_TOKENIZER_REQUIRED")
        tok[short] = tokenizer
    return tok, sha_file(pin_path)

def collect_candidates(selected: dict, tokenizers: dict):
    items = []
    exclusions = {"NO_APPROVED_BOUNDARY": 0, "PREFIX_TOO_SHORT": 0,
                  "TOKEN_COUNT_OUTSIDE_8_96": 0}
    for story_id, (row_index, text) in selected.items():
        norm = normalize_story(text)
        suggestion, reason = prefix_candidate(norm)
        if suggestion is None:
            exclusions[reason] += 1
            continue
        prefix, offset = suggestion
        counts = {key: len(t.encode(prefix, add_special_tokens=False))
                  for key, t in tokenizers.items()}
        if not all(8 <= n <= 96 for n in counts.values()):
            exclusions["TOKEN_COUNT_OUTSIDE_8_96"] += 1
            continue
        norm_sha = sha_bytes(norm.encode("utf-8"))
        prefix_sha = sha_bytes(prefix.encode("utf-8"))
        items.append({
            "source_row_index": row_index,
            "source_story_sha256": story_id,
            "normalized_story_utf8_sha256": norm_sha,
            "normalized_prefix_utf8_sha256": prefix_sha,
            "prefix_end_unicode_codepoint_offset": offset,
            "qwen06_token_count": counts["qwen06"],
            "qwen17_token_count": counts["qwen17"],
            "selection_key_sha256": source_key(row_index, norm_sha),
        })
    items.sort(key=lambda z: (z["selection_key_sha256"], z["source_story_sha256"]))
    unique = []
    seen_norm, seen_prefix = set(), set()
    exclusions["DUPLICATE_NORMALIZED_STORY"] = 0
    exclusions["DUPLICATE_PREFIX"] = 0
    for entry in items:
        if entry["normalized_story_utf8_sha256"] in seen_norm:
            exclusions["DUPLICATE_NORMALIZED_STORY"] += 1
            continue
        if entry["normalized_prefix_utf8_sha256"] in seen_prefix:
            exclusions["DUPLICATE_PREFIX"] += 1
            continue
        seen_norm.add(entry["normalized_story_utf8_sha256"])
        seen_prefix.add(entry["normalized_prefix_utf8_sha256"])
        unique.append(entry)
    ensure(len(unique) >= 256, "ELIGIBLE_UNIQUE_PREFIX_COUNT_BELOW_256")
    sliced = unique[:256]
    result = {"TRAIN": [], "DEV": [], "TEST": []}
    for i, entry in enumerate(sliced):
        split = "TRAIN" if i < 128 else "DEV" if i < 192 else "TEST"
        entry["g1_split"] = split
        result[split].append(entry)
    ensure({k: len(v) for k,v in result.items()} == G1_COUNTS, "G1_SPLIT_COUNTS")
    all_ids = [r["source_story_sha256"] for a in result.values() for r in a]
    all_prefixes = [r["normalized_prefix_utf8_sha256"] for a in result.values() for r in a]
    ensure(len(set(all_ids)) == 256 and len(set(all_prefixes)) == 256, "G1_EXACT_LEAKAGE")
    return result, exclusions, len(items), len(unique)

def seal(root: Path, work: Path, ack: str):
    ensure(ack == ACK, "OWNER_PRIVATE_G1_CDLASHARING_SCOPE_NOT_ACCEPTED")
    dest = work / OUT
    ready = work / READY
    ensure(not dest.exists() and not ready.exists(), "G1_SEAL_ALREADY_EXISTS_DO_NOT_OVERWRITE")
    t1 = read_t1(root)
    tokenizers, token_pin_sha = load_pinned_tokenizers(work)
    ids = set(t1["splits"]["TRAIN"])
    selected, occur, scanned = scan_source(root, ids)
    splits, exclusions, eligible, unique_count = collect_candidates(selected, tokenizers)
    manifest = {
        "schema": "ttm.six.g1.private.prefix.ids.v1",
        "status": "SEALED_METADATA_ONLY_ZERO_SCIENCE",
        "source": "roneneldan/TinyStories",
        "source_revision": T1_REV,
        "source_original_train_sha256": TRAIN_SHA,
        "t1_source_commit": SOURCE_CODE_COMMIT,
        "t1_source_blob": SOURCE_CODE_BLOB,
        "t1_split_manifest_sha256": T1_SHA,
        "scope": "OWNER_OPT_IN_PRIVATE_COMPUTATIONAL_G1_CDLASHARING_1_0",
        "original_ttm_VAL_TEST_story_text_accessed": False,
        "source_mapping": "FIRST_OCCURRENCE_ZERO_BASED_FOR_DUPLICATE_RAW_SHA",
        "g1_prefix_dedup_rule": "KEEP_FIRST_SELECTION_KEY_PER_NORMALIZED_STORY_AND_PREFIX_SHA",
        "tokenizer_pin_sha256": token_pin_sha,
        "selection_protocol": "TTM_SIX_G1_V1_FIXED_PREFIX_LENGTH_AND_G1_V1A_DEDUP_AMENDMENT",
        "story_hashes_only_no_raw_text": True,
        "science_executed": False,
        "counts": G1_COUNTS,
        "splits": splits,
    }
    bytes_manifest = canonical(manifest)
    digest = sha_bytes(bytes_manifest)
    r = {
        "schema": "ttm.six.g1.private.prefix.ready.v1",
        "status": "PASS_G1_128_64_64_METADATA_SEALED",
        "manifest_filename": OUT,
        "manifest_sha256": digest,
        "manifest_size_bytes": len(bytes_manifest),
        "t1_split_manifest_sha256": T1_SHA,
        "source_original_train_sha256": TRAIN_SHA,
        "source_rows_scanned": scanned,
        "train_t1_id_count": len(ids),
        "train_id_multi_occurrence_count": sum(v > 1 for v in occur.values()),
        "total_extra_occurrences_of_selected_sha": sum(v - 1 for v in occur.values()),
        "eligible_story_count_before_dedup": eligible,
        "eligible_unique_prefix_count": unique_count,
        "excluded_reasons": exclusions,
        "split_counts": G1_COUNTS,
        "raw_story_text_persisted": False,
        "original_ttm_VAL_TEST_story_text_accessed": False,
        "qwen_model_weights_downloaded": False,
        "science_executed": False,
        "g1_science_permit": "NOT_GRANTED",
    }
    # Exclusive creation. Metadata only and no overwrite. Keep failure receipts if seal aborts.
    with dest.open("xb") as f:
        f.write(bytes_manifest)
    with ready.open("xb") as f:
        f.write(canonical(r))
    ensure(sha_file(dest) == digest, "POST_SEAL_MANIFEST_SHA_MISMATCH")
    return r

class FakeTokenizer:
    is_fast = True
    def encode(self, text: str, add_special_tokens=False):
        ensure(add_special_tokens is False, "TEST_TOKENIZER_SPECIALS")
        return list(range(max(1, len(text)//8)))

def selftest():
    original = b"A tiny first story.   \n" + EOS + b"\nAnother tiny story!\r\n"
    s = list(iter_story_bytes(io.BytesIO(original)))
    ensure(s == [b"A tiny first story.", b"Another tiny story!"], "T1_PARSER_FIXTURE_FAIL")
    text = "a"*92 + ". " + "b"*100
    normal = normalize_story(text)
    value, err = prefix_candidate(normal)
    ensure(err is None and value[1] == 93, "PUNCTUATION_PREFIX_FIXTURE_FAIL")
    fallback = "a"*134 + " " + "b"*100
    value, err = prefix_candidate(fallback)
    ensure(err is None and value[1] == 134, "WHITESPACE_PREFIX_FIXTURE_FAIL")
    source = {}
    for i in range(300):
        body = (str(i).zfill(5) + "a"*95 + ". the day continued")
        source[sha_bytes(body.encode())] = (i, body)
    result, exclusions, before, dedup = collect_candidates(source, {
        "qwen06": FakeTokenizer(), "qwen17": FakeTokenizer()})
    ensure(sum(len(x) for x in result.values()) == 256, "SPLIT_FIXTURE_COUNT")
    ensure({k:len(v) for k,v in result.items()} == G1_COUNTS, "SPLIT_FIXTURE_LAYOUT")
    ensure(len({e["normalized_prefix_utf8_sha256"] for a in result.values() for e in a})
           == 256, "PREFIX_LEAK_FIXTURE")
    ensure("a"*100 not in canonical(result).decode(), "RAW_TEXT_LEAK_FIXTURE")
    return {"status": "PASS_SYNTHETIC_SELFTEST_NO_FILES_NO_SCIENCE",
            "test_cases": 7, "no_gpu": True, "writes": False}

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--mode", choices=("selftest","preflight","tokenizers","seal"),
                        required=True)
    parser.add_argument("--owner-accept-scope", default="")
    args = parser.parse_args()
    if args.mode == "selftest":
        print(json.dumps(selftest(), sort_keys=True))
        return
    root = check_root()
    t1 = read_t1(root)  # 159KB metadata; original full hash already owner-PASS.
    if args.mode == "preflight":
        work = root / WORK
        status = {"status":"PASS_LOCAL_T1_METADATA_AND_PROJECT_BOUNDARY_ONLY",
                  "python":sys.version.split()[0],
                  "t1_manifest_sha256":T1_SHA,"train_count":len(t1["splits"]["TRAIN"]),
                  "original_TTM_VAL_TEST_text_read":False,
                  "tokenizers_prepared":(work/"G1_TOKENIZER_METADATA_PIN.json").is_file(),
                  "g1_metadata_sealed":(work/READY).is_file(),
                  "model_weights_downloaded":False,"science_executed":False}
        print(json.dumps(status, sort_keys=True))
    elif args.mode == "tokenizers":
        work = prepare_environment(root)
        r = fetch_tokenizers(work)
        print(json.dumps({"status":"PASS_TOKENIZER_METADATA_READY_TECHNICAL_ONLY",
                          "metadata_receipt_sha256":sha_file(r),
                          "model_weights_downloaded":False,"science_executed":False}))
    else:
        # Do not read source or create output before owner acceptance of limited G1 scope.
        ensure(args.owner_accept_scope == ACK, "OWNER_G1_RIGHTS_SCOPE_NOT_ACCEPTED")
        work = prepare_environment(root)
        print(json.dumps(seal(root, work, args.owner_accept_scope), sort_keys=True))

if __name__ == "__main__":
    try:
        main()
    except Exception as exc:
        print(json.dumps({"status":"STOP_FAIL_CLOSED","error":str(exc)[:700],
                          "science_executed":False}, sort_keys=True), file=sys.stderr)
        raise SystemExit(1)
