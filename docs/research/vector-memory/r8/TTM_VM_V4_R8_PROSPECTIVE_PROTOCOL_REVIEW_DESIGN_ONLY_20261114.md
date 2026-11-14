# TTM VM V4 — R7 failure adjudication and R8 prospective protocol review (DESIGN ONLY)
Operation: `TTM_VM_V4_R7_MARKER_SHORTCUT_FAILURE_ADJUDICATION_AND_PROSPECTIVE_R8_PROTOCOL_REVIEW_NO_GENERATION`
Date: 2026-11-14
Status: `R7_FAIL_CONFIRMED` · `R8_PROTOCOL_PROPOSED_NOT_ADOPTED` · `R8_NOT_GENERATED` · `SCIENCE_HOLD`
Repository: minhtri22/TokenToModel-Lab. Append-only research evidence; never rewrite R5/R6/R7.

## 1. Inputs and custody
- R7 protocol before generation: commit `74ef335fb1418515a21591c598d9109ce68070c4`.
- R7 one-shot FAIL adjudication: commit `4eccc4a7549c1956b60ddd5a346300f835377a62`.
- R7 public QA readback: commit `cac10a2f3a6609379a7b976f520e084c483c4921`.
- R7 private SHA-256 `d9e9d6534eae4dbe1169edf2eaa7b6cc2da04eee94296b791b839f6531522db4` (bytes not held in this public repo).
- R7 sealed preview SHA-256 `78de11f46ea0d64b21f78fc325e4120c707d38bf9efec295628bfbf52a644564` (not published).
- R7 QA `7/9 PASS`, FAIL marker-only action `64/64`, target `32/32`. Question-only full CV, lexical baseline, external reviewer `NOT_EXECUTED`. Do NOT infer they passed.
- No owner or human rights attestation; AI-authored source amendment remains PROPOSED.

## 2. Causal diagnosis
**Confirmed deterministic leakage:** phrase `applicable signed record` is uniquely associated with SELECT target, so a card-text substring rule solves action and gold key without semantic retrieval.
**Confirmed design confound:** historical P0–P3 encode SELECT and N0–N3 encode ABSTAIN. Balanced 4/4 *within a separate family* does not make P/N strata independent of action.
**Not established:** generalized question-only, marker-only across novel unseen paraphrases, semantic gold correctness, overlap of purported independent families, rights attestation.

## 3. Non-negotiable R8 amendment requirement
Historical eight strata cannot be kept **as mutually exclusive label-defining strata** and simultaneously be balanced SELECT/ABSTAIN within every stratum. Any plan claiming both is invalid.
**Proposal:** define 8 `relation_family` dimensions with counterfactual paired examples in each; keep legacy P0/P1/P2/P3/N0/N1/N2/N3 as historical mappings only (not eight balanced strata). This changes the estimand and must be prospective owner-adopted *before any new candidate generation*. A separate versioned V4 CAL protocol is required; do not report R8 directly comparable to original P/N CAL without qualification.

### 3.1 Proposed R8 matrix (not data)
For each of eight relation families, author 8 cases: 4 SELECT / 4 ABSTAIN = 64 total; each case 32 public cards; 2048 total.
F01 authorized final placement; F02 actual physical receipt; F03 cross-record assignment; F04 effective-time and supersession; F05 identity disambiguation; F06 conflicting evidence and authority; F07 missing premises/insufficient support; F08 provenance and scope.
These families are semantic task requirements, not IDs. They MUST have disjoint event graphs/templates for held-out tests, no cyclical code-date-location mapping.
For each family: 4 matched SELECT/ABSTAIN pairs with the same question surface, topic, names, metadata distribution and vocabulary budget. Change *only* one logically decisive relation in evidence; preserve plausible supporting and distractor cards. If a family does not admit a meaningful SELECT counterpart (e.g., intrinsically underspecified), redesign family rather than lie about balanced status.
Counterfactual changes must be nontrivial, verified by separate evidence reasoning; no mere word swap like signed/unsigned, final/pending, exists/missing that deterministically identifies gold.

### 3.2 Evidence and source authoring
- Different correct/incorrect cards must share the same style, length, signature vocabulary, provenance markers, source formatting, and status words across conditions. Do not require literal identical text if it changes truth conditions; require balanced conditional distributions.
- Final/pending/signed/approved/countersigned variants must occur in both SELECT and ABSTAIN candidate sets. A word may indicate local card status but must not globally predict action or which card is gold.
- Gold should be established from composed facts, identity, temporal order, and authority; a case with no unique support must abstain. Distinct independent adjudication needed for semantic entailment.
- Inject hard distractors that match entity names, dates, locations, relation keywords and provenance, but contradict one necessary relation. Use variable lexical realization per fact; no fixed phrase unique to selected targets.
- Context and identifiers sampled without fixed one-to-one maps; shuffle cases/cards and use opaque IDs. Keep `gold`, `relation_family`, `paired_id`, `stratum`, labels, rationale and source-lock private. Public-only fields must be allowlisted and searched for hidden encoding.
- Do not publish private case-level gold or any public packet before release gate. No generator output generated in this operation.

## 4. Proposed frozen QA protocol (design not pre-adopted)
- Lock seed, generator code hash, data schema, paired balancing, fixed fold assignments, anti-shortcut implementation and all cutoff choices BEFORE generating.
- Structural (hard): 64 cases, 32 unique cards/case, 8x8 relation-family matrix, 4 SELECT/4 ABSTAIN each family, 32/32 actions, opaque IDs, shuffled ordering, 32 matched-pair comparisons, every SELECT has exactly one supported gold, every ABSTAIN has zero unique support.
- Semantic QA (hard): cross-evidence entailment validated by independent reviewer; no unsupported gold or gold duplicates; matched pair differs in truth-conditional evidence, not surface cue alone.
- Metadata (hard): serialized row/order, case_id, source_id, provenance, string length, URL, numbering, hashes or subfields cannot deterministically recover labels or target. Include case-order-only, identifiers-only, length-only, source-marker-only negative controls. Any deterministic label or gold-key oracle is FAIL regardless of aggregate score.
- Question-only: evaluate fixed explicit baselines on fixed folds, holding out paired counterfactuals and entire latent template clusters. Stratified random CV alone is insufficient. Check both raw and reversed directions *as a two-sided diagnostic*; do not select direction post hoc to claim accuracy. Report exact accuracy, balanced accuracy, confidence interval and by-family confusion.
- Marker-only: use frozen n-gram/regex markers, credential/status token counts and role-presence indicator, and a selector finding gold by marker alone. Any deterministic 64/64 action or 32/32 gold => FAIL. All other high or low scores require calibrated uncertainty; absence of leakage NOT PROVEN by near-chance point estimate.
- Lexical: BM25/TF-IDF top-1 on SELECT cases plus abstention proxy on negatives, family-wise; report both correct and error cases. No fixed desired success rate: a near-zero lexical baseline is not automatically scientific success.
- Family overlap: compare n-gram, prompt frame, event graph, code/date/location, source template fingerprints; leave-entire-family and leave-template-group-out (without train/test related twins). If identity of family is only a changed ID => FAIL.
- Proposed screening flag: absolute distance from chance >= 0.125 for N=64, but this is exploratory *not a statistical acceptance test*. Apply pre-specified two-sided exact-binomial or permutation uncertainty and multiple-check handling after owner adopts; default inconclusive = HOLD, never auto-PASS.
- Strict one-shot: after QA reveal, immutable candidate + receipt; no in-loop edits or repeated seeds. Failure transitions to a new prospective protocol amendment, never cherry-picking.
- Independent validation: reviewer separate chat/environment; knows truth for content QA, no previous R8 result; then A/B blind raters only after source/rights/protocol/content gates PASS; no privilege to approve owner rights or declare scientific release.

## 5. Rights and governance
`AI_AUTHORED_SYNTHETIC_EXPLORATORY_ONLY` is PROPOSED_NOT_ADOPTED, no claim of OWNER_AUTHORED_NATURALISTIC, no fabricated authorship, permission or PII attestation. Require versioned amendment, signed/approved owner decision with verifiable evidence, license/PII provenance, and actual validator support before generation admission; historical R5/R6/R7 unchanged.
Owner must distinguish permission to *create candidate* from scientific permission to *use CAL*. AI preparation does not constitute the owner's decision.
The source and publication policy must specify protected private gold/receipt custody separate from public evidence GitHub.

## 6. Formal gates, fixed before further work
G0 design review: PASS_SCOPED_DESIGN if all contradictions and QA controls documented; independent reviewer of protocol NOT_EXECUTED.
G1 owner adoption / source rights: HOLD_NOT_ATTESTED.
G2 source validator & verified private custody: HOLD_NOT_EXECUTED.
G3 R8 one-shot authoring: NOT_AUTHORIZED / NOT_GENERATED.
G4 independent semantic & anti-shortcut QA: NOT_EXECUTED.
G5 A/B blind calibration: SEALED.
G6 threshold and PROBE256: NOT_FROZEN / SEALED.
Final adjudication: `HOLD_R8_PROTOCOL_OWNER_RIGHTS_AND_INDEPENDENT_REVIEW_NO_GENERATION`.

## 7. Required independent protocol reviewer questions
1. Is label balancing over new relation_family compatible with the task and historical P/N scientific question, or does it demand a new estimand?
2. Could matched counterfactual pairs create their own shortcuts or correlated folds?
3. Can public metadata (case order, keys, IDs, source language) recover action/gold?
4. Are oracle-like fixed-marker negative controls adequate without access to private QA inputs?
5. Are source rights and private custody release rules sufficient for an exploratory-only study?
6. Is the threshold rule preregistered, calibrated and not post-hoc? No reviewer may change numerical gates based on R8 outcomes.

## Next operation
`TTM_VM_V4_R8_PROSPECTIVE_PROTOCOL_DISTINCT_SOURCE_REVIEW_AND_OWNER_AMENDMENT_DECISION_NO_GENERATION`.
No R8 candidate, no blind packet, no TEST, no Reader, no GPU, no PROBE.
