# Agent C handback — M4 Data/Measurement/SFT design onepack

**Operation:** C_M4_DATA_AUDIT_MEASUREMENT_CONSTRUCT_AND_SFT_MASK_DESIGN_ONLY_ONEPACK
**Repository:** minhtri22/TokenToModel-Lab · **Working branch:** research/ttm-track-c-research-scaling-20261116 · **PR:** #35 (Draft)
**Start HEAD:** 666bc2c95ba21eaddcf8a0e3f8ed7cd906629de2 · **main baseline:** f7a0a5874e8fd895c8ea8d17ceff393a4d4917a3.
**Scope:** design-only docs, deterministic synthetic fixture code/tests, source-only metadata checks. No real corpus, no private checkpoint/tokenizer, no model, no GPU, no science, no merge, no A/B edits, no lineage modification.

## Deliverable map

1. \`docs/research/ttm-abc/track-c/C_EVAL_CONSTRUCT_AND_DATA_AUDIT.md\` — traced historical numbers vs missing real histogram/dedup/license/splits; endpoint/rubric/positive-negative controls, floor policy.
2. \`docs/research/ttm-abc/track-c/C_DATA_OBJECTIVE_CAPACITY_MATRIX.md\` — D0/D1/D2 and prospective O/P arms, exposure arithmetic vs FLOPs, seed/power/resource gates, checkpoint compatibility.
3. \`docs/research/ttm-abc/track-c/C_SFT_PROTOCOL.md\` — nanochat-at-pin interpretation, B-facing serialization, shift/assistant-answer mask and no cross-document packing.
4. \`tests/ttm_track_c/synthetic_contract.py\` / \`test_synthetic_contract.py\` — pure-stdlib toy audit/serialize/slot scoring and negative QA, no model or sensitive material.
5. \`configs/ttm_track_c_design_only_v1.json\` — machine-readable proposal, not locked runtime config.
6. \`artifacts/ttm-abc/track-c/\` — QA receipt to be added after test evidence, distinguishing native vs author-only verification.

## Gates (do not promote via paper checks)

| Gate | Latest honest category |
|---|---|
| C-G0 | Source inventory AUTHOR_PASS_SCOPED, independent PENDING |
| C-G1 | REAL_DATA_HOLD (no private corpus; only toy corpus QA) |
| C-G2 | PROPOSED_CONSTRUCT / toy controls, independent PENDING |
| C-G3 | DESIGN_ONLY |
| C-G4 | WAIT_A_B |
| C-G5 | DESIGN_ONLY / toy mask verification, not B trainer |
| C-G6 | DESIGN_ONLY (architecture options, no artifacts validated) |
| C-G7 | NOT_AUTHORIZED |
| C-G8 | NOT_EXECUTED |

**Rights:** internal noncommercial owner declaration in handoff, but no blanket rights for new source, release or third-party scoring. No real rights attestation executed by Track C.
**Reviewer:** distinct reviewer NOT_PERFORMED; author smoke must not be relabeled independent.
**Compute estimate:** only 4,194,304 labels/seed/arm and planning multipliers are known, no actual measured GPU-s/FLOPs/VRAM. **Histogram / dedup:** actual unavailable; toy only. No scientific inference.

**Single blocker:** rights-scoped, source/hashed, fresh nonleaking dataset and A-qualified measurement endpoint (or independently qualified replacement) are missing; B pipeline required for training.
**Bước thực hiện tiếp theo — duy nhất:** \`C_M4_INDEPENDENT_DESIGN_AND_SYNTHETIC_CONTRACT_REVIEW_SINGLE_GATE\` — distinct reviewer challenges gold/negative controls, leakage policy, mask/shift/stop and arm budgets on the exact PR #35 HEAD; report PASS_DESIGN or HOLD_DESIGN without training or micro-permit.
