# HANDOFF AGENT E0 — TTM FRESH16 V2 CPU Executor & Blind Map

**Operation:** TTM_FRESH16_V2_E0_PREPARE_RUNNER_SEALED_MAP_SINGLE_READINESS_GATE
**Role:** EXECUTOR / IMPLEMENTER, not output rater or H2 adjudicator
**Repository:** minhtri22/TokenToModel-Lab
**Research branch:** research/ttm-small4m-prompt-adherence-continuation-design-20261111
**Source baseline HEAD:** 39c1cbfb8734911a3d9fba0e7249e1c3985f94a0
**Original frozen scientific HEAD:** 1583c5b475407799bfca75b503ddf359de7fda69
**Date:** 2026-11-11
**Mode authorized now:** SOURCE/CODE PREPARATION ONLY; NO MODEL FORWARD / INFERENCE, NO TRAINING.
**Owner:** Explicitly ADOPTED V2 on 2026-11-11; did NOT authorize 32-output science execution.
**V2 scoring Git blob:** 27b994b3b3283b2611af21d63acc5d37abf45013
**Prompt Git blob:** 6299a073f0b7c7f8ea890ba9d9b29eaed9442f1f
**Rubric Git blob:** 69668664df23d2246cd65935ab049054aea43e7a

## 1. Immediate assignment

Build a **usable, fail-closed Windows CPU one-shot runner** plus blinded packet/mapping producer, using the original trained TTM-Small-4M model sources. Deliver version-pinned code, single integrated offline source-only readiness report, sealed mapping plan and exactly one GO/NO-GO recommendation to owner. DO NOT execute model forward, generate one sample, fabricate a model output, or consume the one-shot during preparation.

Implement and commit only to the **research branch above**, after checking its current HEAD and working-tree status; never edit main, lineage.md, frozen prompts/rubric, original checkpoints, TEST or prior one-shots. If other agent commits have moved HEAD, reconcile rather than force push or reset. The other two agents (S1/S2) should be read-only; you own the runner implementation.

## 2. Verified existing evidence — use, do not repeat

- Original 16 prompt source: artifacts/research/ttm-small4m-quality-gap/TTM_FRESH_CONTINUATION_PROMPT_SET_CANDIDATE_V1_20261111.json; exact Git blob 6299a073f0b7c7f8ea890ba9d9b29eaed9442f1f.
- Frozen scoring/H1/H2: artifacts/research/ttm-small4m-quality-gap/TTM_FRESH16_FROZEN_RUBRIC_AND_PREREG_CANDIDATE_20261111.json; Git blob 69668664df23d2246cd65935ab049054aea43e7a.
- Adopted V2: docs/research/ttm-small4m-quality-gap/TTM_FRESH16_SCORING_AMENDMENT_V2_ACTION_ROLE_BINDING_TWO_LOCKS_CANDIDATE_20261111.md; Git blob 27b994b3b3283b2611af21d63acc5d37abf45013.
- Source-only QA: 11/11 PASS, native real TRAIN-only BPE2048 roundtrip 16/16, prompt length 28–47 tokens, original Windows checkpoint SHA checks PASS 2/2. Receipt: D:\WORK\RESEARCH\TokenToModel-Lab\_tmp\ttm_fresh16_integrated_offline_review_20261111\INTEGRATED_OFFLINE_REVIEW_RECEIPT.json; SHA256 owner-reported 41407fa954f322879759a04562fdf8ac7b2cc05545a9bcbb734ee5404603c017.
- P02 core: src/p02/transformer_core.py Git blob 9762343e06cf800b50574c2871ae1ed58537fb18.
- BPE source: tools/pilot_t1t3/source_t2/ttm_gpt2_bpe2048.py Git blob fa5bd892941ba5aa6e6b2f0b2b0ae974efe297b6.
- Private manifest: _tmp/ttm_t1_real_source_v1/T1_BPE2048_REAL_TRAIN_MANIFEST.json SHA256 cba18e60cee3d08a353ee6d4a451017289e45af7b4b1179c87171b9b78d7dfdc.
- Checkpoint step1024: _tmp/ttm_causal6_source_h512_stage_20261109/input/checkpoint.pt; SHA256 cb985751795c8328ad65acf7ca4c1033ce35182c1bfbdb8c38550de629cb271b; expected 45,074,891 bytes.
- Checkpoint step1280: _tmp/ttm_fresh16_inputs_20261111/checkpoint_step1280.pt; SHA256 ee723407b2c25a18be20e26387a3dd8e4a18e2942d469279b6f0748ff86af0dc; expected 45,075,275 bytes.

**Important source trap:** P02Config has small engineering defaults (e.g., max_seq_len=64, n_embd=64), **not** the trained 4M science config. Derive exact trained model dimensions and key names from trusted checkpoint metadata/state_dict, validate them against the original T4 model/config source, then strict-load state_dict into the exact 4M architecture. Never silently use P02Config defaults, arbitrary key renames, a fresh random model or an unpinned alternate checkpoint. Use torch.load CPU with weights_only=True where compatible; if legacy trusted archive cannot be loaded safely, report HOLD and the exact compatibility issue rather than silently disabling protections.

## 3. Exact future science contract, NOT permission for today

- 16 frozen prompts × 2 frozen checkpoints = **32 original outputs**, 8 A/B pairs per checkpoint.
- Primary step1024; step1280 strictly descriptive (do not select by outcome).
- Windows 11 CPU FP32, PyTorch/P02 exact source; no GPU/Colab/Ollama.
- GREEDY / argmax next token, max **64 newly generated tokens per output**, original EOS=256, context max256; prompt token length <192; use exact UTF-8 prompt_text with no wrappers, no insertion or stripping of whitespace.
- Decode **generated token IDs only** into generated_text_only; retain exact IDs, EOS, stop reason, any partial/non-UTF-8 decode status. Never count prompt as generation. Model.eval(), torch.inference_mode(), no gradients; no TRAIN/VAL/TEST access, no retraining.
- Planned hard limits: max 900 seconds, max 8 GiB RAM. No retry, no missing-output substitution, no checkpoint cherry-picking. Any preflight failure occurs **before** forward; any science failure after GO is recorded with partial outputs, not rerun.
- One owner science approval after the integrated readiness review; require the explicit permission and locked runner SHA before any model forward.

## 4. Blind mapping / packet preparation

Prepare a local-only, cryptographically shuffled **32-row** mapping from opaque IDs to (checkpoint step, prompt ID, pair ID, variant). Use os.urandom/secrets.SystemRandom, unique random opaque IDs of ≥128 random bits, randomized output order, plus a private random secret in the sealed file. Source pins and two-checkpoint/pair shape must validate before sealing. Create an immutable/exclusive private map under D:\WORK\RESEARCH\TokenToModel-Lab\_tmp\ttm_fresh16_v2_... (all artifacts **inside TTM root only**); do not publish map, mapping key or generated full outputs on public GitHub.

Produce a mapping **hash only** (never the key) in a source-only receipt and propose its anchoring as a content-addressed Git commit before inference. Do not create a public unblinding file. If runner reordering and mapping cannot be made byte-stable before any outcome, HOLD.

When owner later grants GO and outputs actually exist:
- Stage S1 packet: 32 shuffled records containing **only** opaque_id, original prompt_text and generated_text_only. No step, pair ID, variant A/B, rank, H1/H2 aggregate, target/failure cues, prior FRESH12 outputs or unblinding data.
- Stage S2 packet: only **after S1 scores SHA anchored**, 16 opaque pairs of two outputs each, their exact prompts, generated-only text and **locked** S1 adherence scores. Pair checkpoint identity remains hidden.
- Final unblinding only **after S1 and S2 hashes independently anchored in Git commits** (branch refs alone are mutable). No score rewrites.

Prepare schema checkers for cardinalities/IDs/no-label-leak before GO; do not create fake output packets to simulate science. Source-only syntax/tests are acceptable if truly necessary and consolidated, not a new micro-permit. Verify version/code, not experiment outcomes.

## 5. Required deliverables

1. Project-local Python 3.12 + PowerShell 5.1 source-only preparation and future guarded CPU one-shot runner; frozen exact source file Git blob reported.
2. Mapping generator plus sealed-map **plan or actual private map (if feasible without model forward)** and only hash/commit evidence in public repo; no secret leakage.
3. Output-packet schema for S1/S2 and deterministic post-lock tally plan (H1 ≥12/16 with adherence≥2; H2 ≥6/8 with ≥1 passed pair per four categories). No model output scores now.
4. **ONE integrated readiness receipt** detailing source match, trained-config reconstruction, CPU loader compatibility, runner guard, map custody, rater sessions pending/assigned, CPU limits and ONE proposed GO/NO-GO. No repeated QA already PASS.
5. Exact owner launch command for a **future** one-shot, but **do not execute** it or print GO as though already approved.

**Decision today:** NO_GO_HOLD until code/config, map locking, agent identities and one distinct owner execution GO. No other agent should claim the 32 outputs already exist.

**Bước thực hiện tiếp theo:** implement the source-only bundle on the research branch; return commit SHA, gated receipt and concise single-run decision to owner. Do not run inference.
