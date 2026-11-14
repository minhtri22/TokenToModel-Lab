# HANDOFF — TTM VM V4 R8 V4 · Integrated Blocker Closure / One-Shot
**Operation:** `TTM_VM_V4_R8_V4_INTEGRATED_BLOCKER_CLOSURE_SOURCE_QA_OWNER_CUSTODY_SINGLE_GATE_NO_GENERATION`  
**Date:** 2026-11-14  
**Role:** Implementation + source QA integration agent (NOT blind rater; NOT owner; NOT automatically an independent external reviewer).  
**Mode:** `DESIGN/SOURCE IMPLEMENTATION + CPU STATIC/SYNTHETIC CONTRACT QA ONLY`, `NO_R8_GENERATION`, `NO_TEST`, `NO_READER`, `NO_GPU`, `NO_PROBE256`.  
**Goal:** DO REAL WORK IN ONE PASS, then render exactly one overall `GO` or `HOLD` with verifiable evidence. **No V5/V6 iterative review loop, no micro-permits, no placeholder-only writeup.**

## Inputs — must read all at fixed commit
Repository `minhtri22/TokenToModel-Lab`; scientific design source commit **`b8410d9c1f77a733036e980b567de73c316f8725`**:
1. `docs/research/vector-memory/r8/TTM_VM_V4_R8_V4_GOLD_FOLD_ORACLE_RATER_OWNER_SCOPE_SINGLE_PACKET_DESIGN_ONLY_20261114.md`
2. `docs/research/vector-memory/r8/R8_V4_RESTRICTED_ORACLE_AND_RATER_CONTRACT_DESIGN_ONLY.json`
3. `docs/research/vector-memory/r8/R8_V4_DESIGN_CONTRACT_STATIC_CHECK.py`
4. `docs/research/vector-memory/r8/R8_V4_OWNER_SCOPE_AND_RATER_SELECTION_PENDING.json`
5. `docs/research/vector-memory/r8/TTM_VM_V4_R8_V4_SINGLE_PACKET_DESIGN_ONLY_ADJUDICATION_20261114.json`
Read the independently authored R8 V3 review at `docs/research/vector-memory/r8/reviews/TTM_VM_V4_R8_V3_INDEPENDENT_PROTOCOL_REVIEW_20261114.md` for findings B01, B03, B04 and scoped B05. R5/R6/R7 and their reviews are **FROZEN**, R7 known marker-shortcut FAIL. Do not overwrite frozen protocol/QA or invent prior receipts.

**Repository workspace:** When executing on user's Windows device, operate only within `D:\WORK\RESEARCH\TokenToModel-Lab`, use PowerShell 5.1 and stable Python 3.12 when available, with scoped worktree/tmp/evidence paths under the repo; record actual tool/version/hash readbacks. Do not depend on a remote execution tool if unreliable; use an equivalent documented local PowerShell fallback. **Do not modify external project roots.**

## One integrated execution packet — all actions in this handoff
**B01 — gold validator and F07 proof closure**
- Implement the **answer-hypothesis** unit: `(record, accession, event, location, effective interval, authority policy)`; cardinality over fully supported, nondefeated answer hypotheses, not over entities or card IDs.
- Encode private proof schema separately from public packet; minimal sufficient proof sets may have alternatives, each requiring typed `IDENTITY/SCOPE/EVENT/LOCATION/TIME_VALID/AUTHORIZED/NOT_DEFEATED` claims. Multiple keys for the same answer must be rejected under this one-key contract, not arbitrarily resolved.
- Implement deterministic ABSTAIN diagnosis precedence and retain all applicable reasons. Handle zero proof, two distinct answer hypotheses (including same entity but different location), competing equal authority, stale records, explicit negative evidence under a *record-selection* question, duplicate answer cards and circular proofs. No arbitrary "first key" gold.
- **Without generating R8**, create a small, clearly segregated **non-R8 symbolic contract fixture** to test F07 under proposed synthetic policy `P-REC-V1`: the two variants contain same document categories/status tokens; only the *authoritative link* to accession X vs Y changes. Demonstrate SELECT vs ABSTAIN by reconstructing proof, not by matching `signed` or presence of an audit ledger. Add tests for false positives when the same keywords appear in negative cases. Mark owner acceptance of P-REC-V1 as `PENDING` unless authentically approved.
- Require independent content/source QA proof readback where feasible; own checker written by same agent must explicitly be `SAME_AGENT_SEPARATE_CHECKER`, never misleadingly `EXTERNAL_INDEPENDENT_REVIEW`.

**B03 — cluster/fold and rater isolation**
- Implement deterministic G_pre connected components from frozen pair/event/template **blueprints** BEFORE any candidate; do not claim observed post-generation fingerprints exist.
- Implement G_post text overlap checker **as code only**: NFKC/lowercase, Unicode word 5-grams over question+cards, Jaccard `>= 0.80`, exact duplicate event/card signals. Cross-fold post-edge => `FOLD_LEAK_CV_INVALID` and NO repartition; fewer than four usable components/one-class training => `NOT_ESTIMABLE`. Record `event_graph_id` distinct from derived `component_id_pre/post`. Validate via non-R8 synthetic negative fixtures.
- Verify proposed **four-rater** allocation for 8 relation families × 4 pairs, 64 cases ×2 ratings = 128 scores; each A/B/C/D would see 32 cases, with 16 SELECT/16 ABSTAIN, no rater viewing both twins, two scorers/case. Preserve hidden allocation; source-only QA allowed. **No actual packets**. Four separate GPT-6 chats do not imply four human-independent reviewers.
- Owner's choice between `FOUR_RATERS_2_PER_CASE` and `TWO_RATERS_DISJOINT` remains pending unless supported by an actual owner approval record; the four-rater route is a PROPOSAL, not self-authorized.

**B04 — executable restricted O1–O8 including O5**
- Do not treat the existing JSON parameter register or `R8_V4_DESIGN_CONTRACT_STATIC_CHECK.py` as the complete executable suite. Implement deterministic **source-only** restricted controls O1 order, O2 metadata, O3 status/source marker, O4 question and question+metadata, O5 target-key selector, O6 combined action+key, O7 TF-IDF/BM25 comparator, O8 R7 known-leak regression. Keep data input schema and feature boundaries explicit.
- For O5 use TRAIN-only positive-key vs 31 negatives, per-SELECT case weights `0.5` (positive) and `0.5/31` each negative, no test leakage; held-out component accuracy null `1/32`; O6 must report action, conditional key and joint, including abstentions. Cheap metadata/marker success cannot be hand-waved away merely because it is below 32/32.
- Record exact runtime and pinned requirements or `NOT_AVAILABLE`; regex source hash, Python/scikit-learn/NumPy/SciPy versions, seed, feature transforms, fixed group splits, Holm primary O2/O3/O4/O5/O6 with `FWER=0.05` (first cutoff `0.01`). Avoid any after-results hyperparameter selection, label flipping or seed-shopping. Grouped null/permutation only when exchangeability is valid; otherwise `NOT_ESTIMABLE`.
- Run bounded CPU tests **ONLY on non-R8 symbolic synthetic fixtures and known frozen R7 regression contracts if appropriately accessible**, recording a compact table `PASS/FAIL/NOT_EXECUTED` for every oracle and proof-related test. Separate static source checks from actual oracle dynamic QA; do not claim independent QA unless truly done by a distinct agent.

**B02/B05/B06 — no unnecessary reopening**
- B02: identical-question matched SELECT/ABSTAIN 50% accuracy is a mathematical tautology, never a PASS anti-shortcut claim.
- B05: R8-D remains `EXPLORATORY_DESCRIPTIVE_ONLY`; `NO SIGNIFICANT LEAKAGE ≠ NO LEAKAGE`. With 32 pairs and potentially fewer independent clusters, do not claim to certify absence of shortcuts, scientific threshold, or confirmatory release. `PASS_SCOPED_DESCRIPTIVE_QA` describes completeness of QA only; insufficient sensitivity => `HOLD_INCONCLUSIVE`. R8-C remains `NO_GO` without a separate powered prereg.
- B06: source class `AI_AUTHORED_SYNTHETIC_EXPLORATORY_ONLY` is **proposed** until approved; do not infer copyright/rights/PII authority from code review, or private custody from a bare SHA. Prepare a single decision-ready owner/rights/custody packet (not fabricated signature) and a private storage readback plan. If connected custodian evidence exists and is authorized, verify it; otherwise `NOT_ATTESTED/NOT_VERIFIED`, overall HOLD.

## Single adjudication — no micro-gates
Agent must close as much real source/QA work as possible, **in this same operation**, before final decision. After one bounded integration batch and readback, decide:
- **`GO_NEXT_AUTHORIZED_STEP`** only if **G0 independent protocol/source review PASS**, **G1 explicit authentic owner scope+rater choice + rights/PII PASS**, **G2 private custody, validator and exact executable source-lock PASS**, and no hard defect remains. **GO does NOT authorize PROBE, CAL scoring or science;** it only allows the separately preregistered next step explicitly permitted by the owner. Do not generate R8 in this operation regardless of verdict.
- **`HOLD_INTEGRATED`** if any G0/G1/G2 gate lacks required independent evidence, or a true implementation defect is found. Still present actual completed work and the *smallest consolidated* outstanding evidence set. Do not write multiple follow-on operations, ask micro-permits, or label same-agent QA as independent.
- Internal tests may each be PASS/FAIL/NOT_EXECUTED, but **global verdict must be one of GO or HOLD** with a precise scope. A failure of scientific design is reported `HOLD` with root cause and NO-GO for any unauthorized phase, not disguised as GO.

## Artifacts — compact, GitHub-first, one closeout
Create bounded new source/checker/fixture files under `docs/research/vector-memory/r8/integrated_closure/` or a clearly scoped implementation path under R8; never edit prior pinned historical receipts. Produce **one** `TTM_VM_V4_R8_V4_INTEGRATED_SINGLE_GATE_REPORT.md` with:
- pinned input commit/blob hashes, exact files modified and tool/version/hash readback;
- B01/B03/B04 source implementations and test results, B02/B05/B06 continuity;
- G0 independent classification and check evidence (never claim distinct reviewer absent);
- owner decisions/custody receipts if real, else `PENDING`; no private gold, allocation secrets, PII or synthetic key maps in a public repo;
- G0/G1/G2/G3/G4/G5/G6, R7 frozen, R8 not generated, PROBE sealed, Reader=0, GPU=NO;
- formal one-line `DECISION=GO_NEXT_AUTHORIZED_STEP` or `DECISION=HOLD_INTEGRATED`.
Hash source/QA artifacts using real bytes and **commit public-safe evidence to GitHub** after validating contents; return permanent commit URLs, not download links. If GitHub write fails, report `GITHUB_PERSISTENCE_FAILED` and do not claim success. Append lineage only according to existing append-only policy, never retroactively modify scientific record.
No R8 candidate, blind packets, new rater chats, TEST, PROBE256, Reader or GPU. Do **not** request human signature if not supplied; just report G1 HOLD.

## Direct user-facing response
Return **one compact integrated report**, not a status-message chain: `B01/B03/B04/B05` readiness, independent QA classification, `G0/G1/G2`, real GitHub commit, and final `GO` or `HOLD`. If HOLD, give one exact consolidated blocker/recovery plan, not another V5/V6 cycle.
