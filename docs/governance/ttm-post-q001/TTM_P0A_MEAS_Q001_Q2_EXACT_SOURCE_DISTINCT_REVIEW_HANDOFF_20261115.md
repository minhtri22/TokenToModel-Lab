# HANDOFF — TTM-P0A-MEAS-Q001 Q2 Independent Framework & Alternatives Review

**Operation:** `TTM_P0A_MEAS_Q2_EXACT_SOURCE_DISTINCT_REVIEW_AND_OWNER_ADMISSION_SINGLE_GATE`  
**Parent operation (author packet):** `TTM_P0A_MEAS_Q2_FRAMEWORK_ALTERNATIVES_SOURCE_ONLY_SINGLE_GATE`.  
**QuestionID:** `TTM-P0A-MEAS-Q001` (`MEASUREMENT`, Q1 registered).  
**Source-of-truth baseline `main`:** `f31754c21b4e26f7d7a15e53096090f2fa9b5d87`. `lineage.md` Git blob `3409e036241deb1da6674619a2abc834bea8a2d6`.  
**Review mode:** `READ_ONLY · SOURCE_ONLY · DESIGN_ONLY · INDEPENDENT_FROM_AUTHOR`. No dataset/gold/scorer/model run.  
**Draft governance PR:** retrieve PR number and **40-character exact head after author publishes the governance-only PR**; it is not known while this handoff blob is authored. Check candidate **is a one-commit descendant** of pinned main above, compare exact blobs (not dynamic branch ref), and if branch/head shifts record HOLD for the old review rather than reuse its verdict.

## 1. Source files under candidate HEAD

- `docs/governance/ttm-post-q001/TTM_P0A_MEAS_Q001_Q2_FRAMEWORK_ALTERNATIVES_SOURCE_ONLY_REVIEW_20261115.md` — authored report Git blob `f05223a3aa8724054fcd7e4e0b2a87392a2cf789`.
- `artifacts/governance/ttm-post-q001/TTM_P0A_MEAS_Q001_Q2_MECHANISM_DISCRIMINATION_AND_ADMISSION_MATRIX_20261115.json` — machine matrix Git blob `3591c22c0ae552a5a1e054fa29c2254a19701103`.
- `artifacts/governance/ttm-post-q001/TTM_P0A_MEAS_Q001_Q2_AUTHOR_SOURCE_ONLY_QA_RECEIPT_20261115.json` — author QA 98/98, **not independent**.
- This handoff; verify that only four new governance/evidence files are added and no `ACTIVE_RESEARCH_GATE.md`, `lineage.md`, policy, implementation or Q1 source changes.

**Normative sources pinned to `main`:**
- [Registered Q1](https://github.com/minhtri22/TokenToModel-Lab/blob/f31754c21b4e26f7d7a15e53096090f2fa9b5d87/docs/governance/ttm-post-q001/TTM_P0A_MEAS_Q001_REGISTERED_QUESTION_GATE_20261115.md): blob `6b29c962b48c4134c925935409433d4ae2804110`.
- [Active Gate](https://github.com/minhtri22/TokenToModel-Lab/blob/f31754c21b4e26f7d7a15e53096090f2fa9b5d87/docs/governance/ACTIVE_RESEARCH_GATE.md): blob `288d4cd2c84315705e7ea06e45c246b6f3d67496`; Q2 pending.
- [Question-First Policy](https://github.com/minhtri22/TokenToModel-Lab/blob/f31754c21b4e26f7d7a15e53096090f2fa9b5d87/docs/governance/TTM_QUESTION_FIRST_RESEARCH_ARCHITECTURE_LINEAGE_AND_MAIN_POLICY_20261115.md): blob `af1a879a2552f100c6669cb9ab6dc98c930d2e19`.
- [Independent Q1 design review](https://github.com/minhtri22/TokenToModel-Lab/blob/f31754c21b4e26f7d7a15e53096090f2fa9b5d87/docs/governance/ttm-post-q001/TTM_P0A_Q1_AMENDED_DISTINCT_REVIEW_20261115.md): blob `38d009fa3cdc36db847565520307a8ff05d4c8c3`, `PASS_Q1_DESIGN_SCOPE` on old Q1 reviewed exact HEAD `a8fd21f35d56a87f869df673b318d437ed0c8b31`, **not** Q2 independent PASS.

## 2. Adversarial review requirements — do not accept author QA at face value

**A. Q1 scope and framework selection.** Confirm only one `LOCATED_AT(entity,location,reference_time)` family; true/false/unknown versus item REJECT must not be mixed. Audit 5W1H source/access/WHOM, construct validity, falsification, failure modes, no arbitrary MCDA numeric weighting. Challenge whether this source-only Q2 can materially change future owner decision; do not replace it with general ML hypotheses.

**B. M0–M4 independent disconfirmation.** For each, find an alternative explanation and a minimal *independently observable* prospective fact that could falsify the mechanism. Explicitly test nonexclusive causal explanations, role of M0 as measurement prerequisite, M1 hidden gold versus truncation, M2 ambiguity versus valid UNKNOWN, M3 shortcut versus material fact switch with nuisance constant, M4 same-task rater bias versus ontology disagreement. Historical FC01/FRESH16 are scoped, not a direct Q2 empirical contrast.

**C. KEEP/SIMPLIFY/PIVOT/STOP/HOLD.** Demand separate evidence criteria, discriminating capacity, rights/implementation feasibility, qualitative costs and hard-veto precedence. STOP only after proven irreversible illegality/impossibility and no lawful alternative, not missing rights. KEEP requires validated prospective rights/gold/rater/full parity/metrics. SIMPLIFY is pre-outcome only; PIVOT requires a new Question Gate. HOLD default on unknown critical facts, not Q4 model FAIL.

**D. Minimum distinguishing evidence.** Inspect `E0_RIGHTS` to `E5_PREREG`. Is each necessary? Is any mandatory category missing (e.g. source completeness, exact effective model/rater material facts, negative cue control, same-task independent rater, denominator/abstention metric, budget)? Does the packet wrongly presume legal access, checkpoint/rater bytes, a real corpus or an adequate sample? Mark NOT_VERIFIED where applicable. Do not author actual gold, prompt or scorer fixtures.

**E. X13–X16 and N01–N12 adversarial negatives.**
- X13 material-fact parity, including rater-only refutation despite shared positive W;
- X14 different locations do not imply exclusive contradiction without visible axiom;
- X15 gate-level HOLD vs item-level REJECT primary reason precedence when truncation removes evidence, never UNKNOWN;
- X16 Q1 design PASS is compatible with source/gold/rater/rights runtime HOLD.
Check stage timing before authoring/freeze/model/scoring, and whether multi-reason rejects need deterministic canonical priority. The author packet says precedence is **pending implementation**; do not pretend it is tested.

**F. Rights and governance.** Confirm `AD-01R` rights/PII before source access and third-party rater; `AD-01T` if token-sensitive before fixture freeze; `AD-01C` model rights/custody before inference. `AD-02/03/05` before authoring, `AD-06` only if paired causal contrasts. `AD-07` prereg before freeze, `AD-04` independent gold/rater before scoring. The Q1 old independent PASS cannot be called new Q2/Q3 science PASS. No new science branch, dataset, gold, runner or phase permit.

## 3. Output in one integrated, read-only review packet

1. `TTM_P0A_MEAS_Q001_Q2_DISTINCT_SOURCE_REVIEW_20261115.md`.
2. `TTM_P0A_MEAS_Q001_Q2_DISTINCT_SOURCE_REVIEW_RECEIPT_20261115.json`.

Each must include exact 40-char reviewed candidate HEAD, main baseline, source Git blobs and raw SHA-256 verification level, reviewer independence statement, five mechanism dispositions, 5-option decision matrix, minima E0–E5, negative challenges with new adversarial counterexamples if needed, rights/science hold status, HIGH/MEDIUM/LOW findings with file+line anchors, and one overall verdict:

- `PASS_Q2_SOURCE_DESIGN_SCOPED` means paper framework/alternative source analysis is sufficient for **owner Q2 admission deliberation**, NOT benchmark/gold/science PASS or permission to start Q3 automatically.
- `HOLD_Q2_SOURCE_DESIGN` means registration-level Q2 framework/alternative criteria or sources are missing/contradictory; list a **single integrated remediation packet on this same governance PR**. Do not merge.
  
Reviewer is **read-only**; do not commit to GitHub. The owner separately decides `GO_ACCEPT_Q2_SOURCE_ONLY` or `HOLD_Q2_ADMISSION` after receipt. Do not silently merge this draft, update main's active gate, or claim that Q2 is closed from author's 98/98 symbolic QA.

## 4. Boundaries and single next step

`Q1_REGISTERED_ON_MAIN · Q2_AUTHOR_PACKET_READY_INDEPENDENT_QA_PENDING · Q3_NOT_EXECUTED · Q4_NOT_DECIDED · BENCHMARK_GOLD_NOT_VALIDATED · RIGHTS_NOT_VERIFIED · SCIENCE_HOLD · F0_F2_PAUSED`.

**Bước thực hiện tiếp theo — duy nhất:** `TTM_P0A_MEAS_Q2_EXACT_SOURCE_DISTINCT_REVIEW_AND_OWNER_ADMISSION_SINGLE_GATE`.

One distinct source-only review and one eventual owner GO/HOLD evaluation. No micro-permits, no model run, source/gold/scorer authoring, Q3 auto-admission, implementation merge or `lineage.md` edit.
