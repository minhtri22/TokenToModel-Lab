# HANDOFF C — TTM Research, Post-Training & Scaling (M4–M8)

**Operation:** `TTM_TRACK_C_DATA_OBJECTIVE_SFT_ARCHITECTURE_SCALING_RESEARCH`  
**Date:** 2026-11-16 (Asia/Bangkok) · **Agent C:** independent executor (unassigned) · **PM:** ChatGPT on submitted review/evidence  
**Branch:** `research/ttm-track-c-research-scaling-20261116` · **Exact starting main:** `f7a0a5874e8fd895c8ea8d17ceff393a4d4917a3`  
**Schedule target:** M4 weeks 4–7; M5 weeks 7–9; M6 weeks 8–10; M7–M8 week 10 onward. These are estimates, **not authorized runs or validated outcomes**.  
**State:** `C_DESIGN_OPEN · DATA_SCIENCE_NOT_EXECUTED · SFT_NOT_EXECUTED · ARCHITECTURE_NOT_EXECUTED · SCALING_NOT_EXECUTED`.

## 0. Mission / exclusions

The Track C goal is **to identify which changes actually improve new-data generalization and instruction behavior per unit compute**, then prepare evidence-based scaling beyond Small-4M. Do NOT reimplement GPT Core (belongs to B), modify Q001 or its scorer (belongs to A), auto-open GPU/training runs, repurpose historical frozen checkpoints under different math, tune on consumed TEST64/FRESH16/FINAL24, publish source stories/weights, or merge to main.

Design documents, source-only QA, synthetic evaluator/fixture engineering and resource estimates can start **immediately**, independently of A and B. Real new scientific comparisons require (a) validated measurement from A or an independently qualified endpoint, (b) reproducible trainer/data contracts from B, (c) source/rights/custody and compute budget, (d) one scoped protocol/owner decision. A and B need NOT finish every milestone to allow this planning. No sequential micro-permits for parser fixes or routine CI.

Reference anchors:
- [Global roadmap PR #30](https://github.com/minhtri22/TokenToModel-Lab/pull/30) HEAD `229f9dedfd82c0544cd637f8180d50017fc16777`, backlog RF-10, RF-11, RF-13..RF-17, RF-21..RF-31.
- [Small4M in-context probe design](https://github.com/minhtri22/TokenToModel-Lab/tree/research/ttm-small4m-incontext-probe-roadmap-design-20261116), particularly Step 3 rubric negative controls, Step 4 data/objective/capacity separation, Step 5 rights/custody. These are **unreviewed design proposals**, not frozen protocol.
- [nanochat pinned inspiration](https://github.com/karpathy/nanochat/tree/92d63d4e8bb4df75c3b71618f31ddde2378b2bcd): `scripts/base_train.py`, `scripts/chat_sft.py`, `nanochat/gpt.py`, `nanochat/optim.py`, `nanochat/loss_eval.py`, `runs/miniseries.sh`; track the reference SHA separately if updated.
- Historical T4 **3,749,376 parameters**, 1024 updates, 4096 target-label exposures/update = 4,194,304 exposures, about 498,287 unique TRAIN target labels reused ~8.4×. VAL NLL ~11.88% better than TRAIN-only bigram while prompt adherence FRESH16 0/16. **No demonstrated causal root cause yet.**
- **Rights:** owner has declared internal, noncommercial research for scoped assets; TinyStories source license has CDLA-Sharing-1.0 label. Recording the label is NOT external legal clearance for redistribution, derivative weights release or a new private-data study.

## 1. M4 — Data quality and valid measurement (week 4–7)

Build a `C_EVAL_CONSTRUCT_AND_DATA_AUDIT.md` and synthetic evaluator QA before proposing training arms.

**Data diagnostics:** canonical source revision/hash, tokenizer/version/fertility, UTF-8 bytes/token, dataset sample hash and near-duplicate groups, train-only tokenizer provenance, train/val/test isolation, repeated-target factor, length/domain balance, entities/attributes, copyright/PII flags and allowed use/action (internal forward, train, redistribute = separate decisions).

**Measurement construct:** distinguish pretraining next-token learning vs induction/copy, entity binding, counterfactual change, instruction adherence, formatting, repetitive degeneration and decoding. Give each capability its own endpoint; do not conflate with low NLL. Prior FRESH16, FINAL24 and D1 suffered floor effects/provenance gaps, so require negative and positive controls with known answers, label-blind candidate rule, multi-level reference rubric, exact rater-visible byte hashes and held-out samples. Prefer programmatically checked slot correctness before AI rater. For language judgment requiring humans/AI, blinded independent rater sessions and inter-rater agreement are **additional**, not substitutes for valid gold. If metrics floor at zero, mark `FLOOR_HOLD` and change measurement before comparing models.

**M4 evidence:** source-only data audit, split SHA, metric specification, positive/negative controls on entirely synthetic cases, independent validity assessment. No historical FINAL24 rescoring as a new confirmatory result.

## 2. M5 — Data → objective → capacity (week 7–9; prospective science only)

A *proposed* causal ablation sequence, not permission to execute:

**Diversity first, equal target exposure:** retain T4 tokenizer/architecture and 1024×4096 target exposures. Compare approximately 0.5M, 2.1M, 4.2M independent TRAIN target-token budgets (D0/D1/D2), with controlled source and revision, equivalent distribution and sequence lengths as far as possible, no overlap with VAL/historical TEST/new probe, seed-matched order, exact actual counts. Expected repeat factors ~8.4, ~2, ~1, to be recomputed from real source hashes. Treat the current T4 D0 as a historical anchor, not automatically a matched contemporary control: re-runs for comparability require a new authorized study.

**Then objective:** compare pure next-token prediction with a precisely specified alternative (e.g., contrastive C package) on **the same data and total measured FLOPs**, if technically feasible; otherwise disclose cost difference and avoid causal claim about objective alone. Do not use historical FC01 as clean objective-only evidence.

**Then capacity:** only if previous studies leave a gap, compare different parameter counts with identical data/objective/compute rules and explicit training budgets. Precompute real parameter counts from code rather than assuming labels 16M/32M/64M are exact. Multiple independent seeds (pilot e.g., 5, confirmatory e.g., 12) with predeclared endpoints, effect sizes and confidence intervals; these counts are proposals requiring power/feasibility review, not frozen obligations.

**Primary endpoints:** validated teacher-forced copy/induction + binding, gold NLL/rank, appropriately fresh VAL; secondary valid format and generation scores. Track tokens/parameter, unique tokens, seen tokens, FLOPs, GPU-s, total time, peak VRAM, `bpb` only with correct byte accounting. A null effect with wide CI is `INCONCLUSIVE`, not equivalence; failure to separate at a floor is `FLOOR_HOLD`.

**Run boundaries:** source rights/custody verified for exact files, model schema pin, frozen seeds/splits/thresholds, resource preflight of actual T4 or other granted hardware, explicit stop/retry policy, independent review *before observing results*, bounded one-shot execution and GitHub receipt with private data excluded. No automatic permit proliferation; one integrated science admission per coherent experiment.

## 3. M6 — Base GPT → instruction-following SFT (week 8–10)

Start with **design and synthetic smoke** on B's stable baseline:
- Define ChatML-like or other versioned conversation serialization (system/user/assistant turns), explicit BOS/EOS, stop sequences, loss mask **only on assistant answer tokens**, padding `ignore_index`, training target shift, multi-turn packing rules, and data-hash/split separation.
- Tiny rights-safe structured instruction set: factual slot binding, formatting, refusal/unknown when context insufficient, simple Vietnamese and English instructions (track language separately), counterfactual edits; avoid using personal/private prompts as training material.
- Controls: same base checkpoint, same data and information budget where possible, SFT vs no-SFT (or NTP-only), greedy and matched sampling, same fresh heldout, multiple seeds if science is approved. Single overfit or lower SFT TRAIN loss **does not** prove instruction ability.
- Evaluate exact slot correctness, schema/format compliance, repetitive loops, fact conditioning, hallucinated entities and stop behavior; maintain blind, positive/negative rubrics.
- Do not market Small-4M as a capable chat assistant. SFT at 4M may simply expose a capacity ceiling; if so, record measured boundary.

Deliver `C_SFT_PROTOCOL.md`, synthetic data example + mask tests, proposed evaluation items, run configs/estimate (not hidden model run), standalone independent review; eventual real results only after owner-scoped admission.

## 4. M7–M8 — Architecture, scale and serving, conditioned on evidence (week 10+)

**One architecture arm at a time**, with checkpoint schema/version change and no silent math substitution:
1. RMSNorm vs LayerNorm (baseline already has an RMSNorm option but T4 uses LayerNorm).
2. RoPE vs learned absolute positional embeddings; no old positional checkpoint direct load.
3. ReLU² or SwiGLU vs GELU (separate arms, test GGUF/llama.cpp compatibility); preserve historic strict-logit FAIL32/32 and scoped GELU_ERF PASS4/4.
4. QK-Norm / GQA (separate from RoPE unless factorial pre-registration); measure actual KV memory, long-context quality, trained from scratch or defensible transform.
5. MuonAdamW vs AdamW after optimizer correctness; compare total compute and actual implementation throughput, do not assume H100 speedups on T4.

**Scale series:** target approximate 4M → 16M → 32M/64M **only if data/compute evidence supports it**; preflight parameter counts, throughput, VRAM, context, optimizer state, batch/accumulation, checkpoint sizes and interruption/resume. T4 16 GiB does **not** imply every arm fits, and nanochat's 8×H100 performance is not a TTM budget. Use a pilot feasibility gate before any expensive run. Quantify heldout quality **per compute**, not just model-size growth. If 16M cannot fit budget or quality stagnates, HOLD rather than claiming roadmap failure.

**Serve:** after a stable quality checkpoint, B/C interface for T5 GGUF parity and CPU P05/P06 dense/paged KV (historically scoped), model-specific logits parity, streaming/stop tokens, latency TTFT/TPOT, concurrency and safe shutdown. Do not characterize CPU synthetic Paged KV as GPU paged-attention deployment or show false throughput gains.

## 5. Gates and role-specific deliverables

| Gate | Requirement | State at handoff |
|---|---|---|
| C-G0 | Exact source/backlog/lineage inventory, separate repository research branch | OPEN |
| C-G1 | Data/license/action rights and split/duplication audit (synthetic + source-only) | NOT_EXECUTED |
| C-G2 | Valid independent-tested metrics and known-answer controls, floor checked | NOT_EXECUTED |
| C-G3 | Equal-budget data/objective protocol + resource estimate, effects/seed/power design | DESIGN_ONLY |
| C-G4 | B trainer readiness + A endpoint or independent replacement qualified | DEPENDENCY |
| C-G5 | SFT mask/template synthetic QA + blinded instruction assessment design | DESIGN_ONLY |
| C-G6 | Individual architecture/checkpoint version/compatibility specs | DESIGN_ONLY |
| C-G7 | Scale resource feasibility and owner-scoped prospective decision | NOT_AUTHORIZED |
| C-G8 | Any real science run exact evidence and independent adjudication | NOT_EXECUTED |

**Important:** `C_DESIGN_PASS` may be reached while `C_SCIENCE_HOLD`; do not collapse these into one PASS. No claims of scaling gains, SFT gains or science until real independently assessed receipts exist.

**Owned paths:** `docs/coordination/ttm-abc/TTM_TRACK_C_*.md`, `docs/research/ttm-abc/track-c/`, `tests/` for synthetic measurement/SFT controls, `configs/` C proposals, `artifacts/ttm-abc/track-c/` source QA. Never edit A/B files or historical checkpoint/evidence. Publish unmerged **draft PR C → main** for reviewed source/design; future science patches must be scoped and prospective.

**Agent C handback:** exact commit/base, files/manifest SHA, source-only vs native QA, decision on scientific construct, independent reviewer record, dataset token histogram+dedup, arm matrix, compute estimate vs budget, checkpoint compatibility, permission scope, `NOT_EXECUTED` list, one blocker and **one** next action. GitHub stores summaries, hashes and receipts; no private corpus, tokenizer reversible packs, raw logits, weights or credentials.

**Interface:** receive A's validated endpoints/contamination controls and B's working CLI/benchmark; provide B a versioned chat serialization and SFT loss mask; provide PM a prioritized evidence-backed decision whether to improve data, objective, capacity or stop. **Do not block B engineering on C research.**

**Bước thực hiện tiếp theo — duy nhất:** `C_M4_DATA_AUDIT_MEASUREMENT_CONSTRUCT_AND_SFT_MASK_DESIGN_ONLY_ONEPACK`.