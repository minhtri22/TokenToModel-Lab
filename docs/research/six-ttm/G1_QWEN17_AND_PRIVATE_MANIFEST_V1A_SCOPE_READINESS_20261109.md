# TTM × SIX — G1 private TRAIN-only manifest v1a: scope, source, validation, execution handoff

**Date:** 2026-11-09  
**Task:** `TTM_SIX_XMODEL_G1_QWEN17_TECHNICAL_READBACK_AND_PRIVATE_MANIFEST_SEAL`  
**State:** `T1_ORIGINAL_MANIFEST=PASS_OWNER_ATTESTED` · `G1_PRIVATE_MANIFEST_PRODUCER=SOURCE_COMMITTED_STATIC_REVIEW` · `G1_PRIVATE_MANIFEST_SEAL=NOT_EXECUTED` · `QWEN17_COLAB=RECEIPTS_NOT_OBSERVED` · `G1_SCIENCE_LOCK=HOLD`.

## 1. G1 private computational scope for owner opt-in

The source is `roneneldan/TinyStories@f54c09fd23315a6f9c86f9dc80f725de7d8f9c64`, declared `CDLA-Sharing-1.0`. This plan restricts G1 to **private, local computational research** and its results; it does **not** authorize publishing raw stories, any continuous prefixes, copies of the dataset or bulk extracted tensors. Keep attribution, source revision, license notices, transformation logs and SHA-256 receipts. Source and derived-content publication requires an additional rights classification if ever proposed.

**Owner acceptance is not assumed** from an instruction to prepare the workflow. Running `-Mode Seal -OwnerAcceptPrivateScope` is the **one explicit owner opt-in** to this narrowly stated private data-use scope. The program refuses to scan any TRAIN story bytes without this exact opt-in. This opt-in does **not** constitute a permit to run scientific G1, release any TEST values, train Qwen/TTM, or publish content.

All new artifacts, HF metadata and temporary caches stay under the project root:
`D:\WORK\RESEARCH\TokenToModel-Lab\_tmp\ttm_six_g1_private_manifest_v1`.

Raw `TinyStories-valid.txt`, TTM original VAL/TEST story text, other research projects, `main`, PR#12 and `lineage.md` stay untouched.

## 2. Preserved evidence — no reruns

Owner reported, from the frozen PowerShell source blob `b15a58b9aaa4d8cc6c7813bdbf4e1d825554c24d`:

```
status=PASS_T1_ORIGINAL_MANIFEST_BYTES_AND_2368_IDS
manifest_sha256=9f2ebaca821bddf0a9d7ae30ccfcef34561b968b21159aa913794298235a2fa9
manifest_size_bytes=159689
train=2048, val=256, test=64, unique_ids=2368
source_raw_story_bytes_read=false, writes_performed=false, science_executed=false
```

The receipt is archived in `docs/research/six-ttm/G1_T1_ORIGINAL_MANIFEST_2368_IDS_OWNER_READBACK_PASS_20261109.json`, Git blob `38bf17442afe0978182ebf4e0802b6f95919cf9a`. Do **not** rerun this T1 QA; reading its 159KB manifest as an input integrity pin is not an independent replay. Qwen3-0.6B Colab technical PASS is also preserved, not rerun.

## 3. Technical implementation — two stages, one evidence package

**Producer:** `scripts/research/six_ttm/g1_private_manifest_train_only_v1a.py`, Git blob `aee230060f8202907953e0eeab0ae5b1099a584e`.

**PS5.1 wrapper:** `scripts/research/six_ttm/Run-G1-PrivateManifest-PS51.ps1`, Git blob `396c7dd53cf002dcfebca91d7e1cce89a46b9d0f`.

**Separate metadata-only verifier:** `scripts/research/six_ttm/g1_private_manifest_independent_readonly_qa_v1.py`, Git blob `7dfc6bea2cee1773c20fee655691fc366a6a9ecd`. Separate source implementation checks 29 invariants; it is **not** an independent scientific reviewer or an independent GPU replay.

### Modes

- `SelfTest`: standard-library synthetic QA; no files or project reads in Python, no GPU.
- `Preflight`: T1 metadata SHA, origin, boundary and tokenizer readiness only; does not read raw TRAIN text.
- `Tokenizers`: download **only** pinned tokenizer/config files from Qwen3-0.6B and Qwen3-1.7B to project-local metadata dirs, no weight shards, no raw dataset read; writes a hash-pin receipt. Requires Python 3.12 and Hugging Face tokenization dependencies available on host; do **not** install into global Python automatically.
- `Seal`: requires explicit `-OwnerAcceptPrivateScope`; the only mode that streams original `TinyStories-train.txt` (about 1.92GB) to match **only** the 2,048 T1 TRAIN content IDs and recompute the original pinned full-file SHA in the same pass. Never opens `TinyStories-valid.txt`. Selects deterministic eligible prefixes using both frozen tokenizers and 8–96 token length guards, then writes exactly 128 TRAIN / 64 DEV / 64 TEST metadata rows with no story/prefix text, exclusive create/no overwrite.
- `QA`: independent read-only schema, SHA, T1 membership, three-way non-overlap, prefix/story uniqueness, deterministic ordering, both token lengths, offsets, scope and no-payload checks. Prints sanitized JSON to console. If QA fails, do not claim `SEALED_PASS`.

### Necessary prereg amendment (not a covert edit of frozen v1)

The original T1 manifest maps a story by SHA-256 of **stripped original UTF-8 story bytes**, not by `source_row_index`. Because the original corpus contains duplicates, the v1a materialization uses **the first occurrence, zero-based row index** for a matched content SHA. It preserves the count of repeated occurrences as metadata without exposing text.

To prevent identical prefixes between G1 TRAIN/DEV/TEST, v1a excludes duplicate normalized-story SHA and duplicate normalized-prefix SHA **before the 128/64/64 cut**, keeping the first row in deterministic selection-key order. These implementation choices are **v1a protocol amendments**, not present in the frozen v1 candidate at its original SHA. Before any G1 science, the independent reviewer must adjudicate and freeze this amendment, or request a new immutable protocol version; do not silently rewrite v1.

The JSON is stored at `_tmp/ttm_six_g1_private_manifest_v1/G1_PREFIX_IDS_128_64_64_PRIVATE_METADATA.json`, with `G1_PREFIX_MANIFEST_READY.json`. Neither should be committed to public GitHub. They contain hashes and row IDs only; original text stays in original pinned local source. The final QA prints a hash of the output and asserts no raw source text persisted. This manifest is a private **pre-science identity pack**, not functional teacher outputs.

### QA status now

Producer static invariants: **14/14 before fixture correction**, then **12/12 post-fix code checks**; PS wrapper QA mode source pinned. Standalone QA static invariants: 9/9. **Python AST, selftest, Windows dependency/runtime and real manifest generation have NOT been executed** by the assistant; do not upgrade these static checks to runtime PASS. The synthetic fixture was corrected to include 300 distinct prefixes; dynamic selftest still requires execution.

## 4. Qwen3-1.7B on Colab

Existing pinned notebook `notebooks/six_ttm/TTM_SIX_G1_QWEN17_INTEGRATED_READINESS_PREFLIGHT_ONESHOT_SMOKE_20261109.ipynb`, Git blob `3c807149ac16b1d08be3ba70ef57ff5ccf62c679`.

Current connected Drive search for `G1_TARGET17_PREFLIGHT_RECEIPT` and `G1_TARGET17_SMOKE_RECEIPT` produced **no accessible match**. There is no Colab execution facility connected in this turn; **no cell was run**. The owner should run cell 1 first, then cell 2 **only on PASS**, once, with a fresh Colab Free T4 session, and provide both receipts. Qwen3-0.6B must not be rerun. A model-weight hash mismatch or fail-closed STOP is not a science FAIL.

## 5. Single final science gate

Even after private manifest QA and Qwen17 synthetic smoke PASS, **science remains HOLD** until the full runner (TRAIN fit / DEV select / TEST once, 8 fixed functional probes, null + positive controls), prereg v1a amendment and a **distinct external scientific reviewer** all PASS and the owner grants one scientific execution. Do not append engineering QA to `lineage.md`; scientific FAIL/PASS only.

**Next:** `TTM_SIX_XMODEL_G1_PRIVATE_MANIFEST_SOURCE_SELFTEST_AND_QWEN17_COLAB_RECEIPTS_READBACK`. Collect in one batch: local PS selftest/preflight/tokenizer pin/owner-opt-in seal/QA plus the two Qwen17 Colab receipts. Any missing item remains HOLD; do not invent results or create replacement one-shot attempts.
