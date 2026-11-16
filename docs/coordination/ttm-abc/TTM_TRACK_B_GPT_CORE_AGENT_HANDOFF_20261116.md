# HANDOFF B — GPT Core End-to-End Baseline (M3)

**Operation:** `TTM_TRACK_B_P01_P04_T4_UNIFIED_GPT_PIPELINE_AND_INDEPENDENT_QA`  
**Date:** 2026-11-16 (Asia/Bangkok) · **Agent B:** executor (unassigned) · **PM:** ChatGPT on submitted evidence  
**Branch:** `research/ttm-track-b-gpt-core-20261116`  
**Frozen base main:** `f7a0a5874e8fd895c8ea8d17ceff393a4d4917a3`  
**Window:** weeks 2–6, can start independently of A  
**Status:** `B_M3_OPEN_SOURCE_ENGINEERING · NEW_SCIENCE_NOT_AUTHORIZED · MAIN_UNCHANGED`

## 0. Mission and boundaries

Build a small, readable, reproducible GPT pipeline using existing TTM code: **tokenizer/data → P02 model → P03/T4 trainer → P04 checkpoint → evaluator → sampling**. Deliver one command (or one well-defined sequence) for end-to-end **synthetic engineering smoke** on Windows 11, Python 3.12, PowerShell 5.1. No rewrite of P02, no upgrade to RoPE/GQA/Muon, no new TinyStories science, no TEST64/FINAL24/FRESH16 reuse, no trained-weight publication, no source changes to A/C branches, no merge to main.

Read exact main `docs/PHASE_PLAN.md`, `lineage.md` (read-only), `src/p02/transformer_core.py`, `src/p03/train_loop.py`, `src/p04/eval_checkpoints.py`, `tools/pilot_t4/a2_continuous1024/t4_train_science_a2.py`, `tools/pilot_t4/integrated/t4_data_pack.py`. Read [PR #30](https://github.com/minhtri22/TokenToModel-Lab/pull/30) at `229f9dedfd82c0544cd637f8180d50017fc16777`, backlog RF-04..RF-08, RF-12/13/21. Read [nanochat pinned reference](https://github.com/karpathy/nanochat/tree/92d63d4e8bb4df75c3b71618f31ddde2378b2bcd) as *design comparison*, particularly dataloader, checkpoint_manager, loss_eval, base_train and chat_sft. Nanochat's advanced architecture and H100 configuration are not automatically compatible with TTM.

**Historical config:** T4 actual GPT = 2048 vocab, context 256, dim 256, four layers, four attention heads, LayerNorm/GELU, learned absolute position, tied embedding/head, **3,749,376** unique parameters. P02 defaults are NOT T4. T4's source pack uses `ids=bpe.encode(text)+[EOS_ID]`; next-token training windows use targets `segment[1:]`. P01 WP30 BPE and T4 T1 TRAIN-only BPE may share vocab size but are **different artifacts**.

## 1. M3 packages and exact acceptance

**B0 — Contract inventory (week 2).** Write contracts for tokenizer hash/version, special tokens and byte-level roundtrip, split membership and overlap, context length, strict model config, target alignment/mask, sampler and optimizer state, checkpoint provenance, output/receipt schemas. Distinguish P04 `ttm.p04.model_checkpoint.v1` versus T4 `ttm.t4.science.checkpoint.v1`; implement read-only strict adapter with `torch.load(weights_only=True)`, `strict=True`, expected config, key shapes, hash and fail-closed input path. Do not reserialize historical checkpoint.

**B1 — Real dataset/trainer adapter (weeks 2–4).** Reuse P02 and existing P03/T4 optimizer/scheduler routines, avoid a second divergent trainer. Add a deterministic, rights-safe synthetic dataset and window loader. Unit tests MUST cover:
- causal mask (future tokens never affect past logits), shifted next-token targets, padding `ignore_index=-100`, exact valid-target normalization;
- accumulation vs reference batch within predeclared FP32 tolerance, LR warmup/cosine, gradient finiteness, clipping and real parameter delta;
- negative injected off-by-one target/mask/label leak, incorrect tokenizer or split manifest rejection;
- tiny synthetic single-batch overfit with train loss decreasing **without scientific interpretation**;
- train N steps uninterrupted versus K + resume N-K: exact sampler/scheduler/optimizer/RNG restoration, no-overwrite, byte/hash custody. If bitwise equality cannot be justified, freeze numeric tolerance before checking output.

**B2 — Evaluation/inference (weeks 3–5).** Implement full-vocabulary token NLL, rank/top-1 and reliable bpb computed from real UTF-8 byte counts and explicit exclusions (not arbitrary mean over story means). Separate TRAIN, fresh VAL and groups; include denominators, processed vs independent target tokens, reuse factor, throughput, timing, peak RSS/memory. Greedy and seeded sampling with EOS/context boundaries and deterministic smoke. Do **not** reuse the invalid Q001 restricted scorer (gold-first candidate leak). Capability/rater metrics are `NOT_VALIDATED` until Track A provides an independent validated endpoint.

**B3 — CLI / CI / evidence (weeks 4–6).** Proposed minimal invocations:
```powershell
# DESIGN TARGETS — not real commands until Agent B implements them
python -m ttm.cli prepare --config configs/ttm/synthetic_smoke.json
python -m ttm.cli train --config configs/ttm/synthetic_smoke.json
python -m ttm.cli evaluate --config configs/ttm/synthetic_smoke.json
python -m ttm.cli sample --config configs/ttm/synthetic_smoke.json
```
Include a concise Vietnamese runbook (English terms in parentheses), code tests and optional Actions Python3.12 CI that downloads **no private data**. A separate Windows PS5.1 path/parser check is required if PowerShell launcher is introduced. Run resource-bounded smoke with exact input/output SHAs, exit codes, no uncontrolled children, no silent retries. Smoke QA is engineering, not proof of prompt-following or model quality.

## 2. QA and decision gates

| Gate | PASS requires | HOLD label |
|---|---|---|
| B-G0 | Exact source inventory; scope only B; PR30 pinned read-only | HOLD_SOURCE |
| B-G1 | Tokenizer/split/EOS/target mask contracts + negatives PASS | HOLD_DATA_CONTRACT |
| B-G2 | Real P02/P03/T4 integrated adapter, synthetic overfit and negative controls | HOLD_TRAINER |
| B-G3 | Two checkpoint schema adapters; strict/no-overwrite; resume parity | HOLD_CHECKPOINT |
| B-G4 | Full-vocab NLL/bpb correct against independent reference; seed-controlled sample | HOLD_EVAL |
| B-G5 | One-command/one-run synthetic CPU E2E with measured resource caps | HOLD_E2E |
| B-G6 | Distinct exact-HEAD independent QA, evidence GitHub readback, no science | HOLD_REVIEW |

Only `B_M3_PASS_ENGINEERING_BASELINE` when B-G0..B-G6 pass. `NOT_EXECUTED` is not PASS. Never convert a CI success into a claim of semantic improvement. Retain historical T5 strict-logits FAIL32/32 and scoped GELU_ERF PASS4/4; this B work does not certify stock Ollama or all precisions.

## 3. Deliverable files and handback

Suggested owned paths: `docs/coordination/ttm-abc/TTM_TRACK_B_*.md`, `docs/research/ttm-abc/track-b/`, new B-scoped adapters in `tools/` or `src/`, `tests/`, `configs/`, `artifacts/ttm-abc/track-b/`. Preserve all prior archive/lineage. Make branch-local commits and an unmerged **draft PR B → main**. PM reviews before any integration.

Mandatory evidence: exact branch HEAD/base, source blob pins, `RUN_MANIFEST.json`, synthetic fixture SHA256, test counts with author/distinct provenance, Windows/Python/torch versions, train/val metrics, resource/time, resume comparison, negatives, executed/not-executed matrix and ONE next step. No checkpoint weights, TinyStories raw contents, reversible token packs, credentials or sensitive private logs on GitHub.

**Interface:** Track B accepts A's validated score contract when available but **must not wait** to build B0/B1. B supplies C with frozen CLI, manifest, tokenizer/data contract, bpb/NLL, throughput and a clean SFT extension point. B does not authorize C's experiments.

**Bước thực hiện tiếp theo — duy nhất:** `B_B0_B1_CONTRACTS_T4_ADAPTER_AND_SYNTHETIC_E2E_SCAFFOLD`.