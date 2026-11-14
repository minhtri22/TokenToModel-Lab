# TTM Vector Memory V4 R8 — G0/G1/G2 Integrated Independent Readback & Adjudication

- **Date:** 2026-11-14
- **Operation:** `TTM_VM_V4_R8_G0_G1_G2_INTEGRATED_REMEDIATION_AND_INDEPENDENT_READBACK_SINGLE_GATE`
- **Reviewer:** GPT-6, separate AI review session; independent **AI source/protocol** readback, **NOT** human review, authenticated owner approval or authorized private-custodian attestation.
- **Review mode:** GitHub read-only source inspection; one public-safe evidence report committed; **NO tests rerun, NO R8 generation, NO TEST, NO Reader/GPU/PROBE256, NO private files accessed.**
- **Single adjudication:** `HOLD_INTEGRATED`.
- **G0:** `HOLD_INDEPENDENT_SOURCE_PROTOCOL_CONTRACT_MISMATCH`.
- **G1:** `HOLD_OWNER_DECISION_RIGHTS_NOT_ATTESTED`.
- **G2:** `HOLD_PRIVATE_CUSTODIAN_READBACK_NOT_VERIFIED`.

## 1. Exact source and existing QA preservation

- V4 scientific design commit: `b8410d9c1f77a733036e980b567de73c316f8725`.
- Original integrated evidence: `3a12aede5d738aa0a91d6a0d5f68869000efc097`, earlier 29/29 non-R8 synthetic/source-only PASS.
- One-shot remediation source commit: `cf38f8792253fe106cbb6a641f189882fb96e9d5`.
- Handoff commit: `32ffcdd53a2b20ba43e9d2305ef4cec698e1aab7`.
- GitHub compare `cf38f879...32ffcdd5`: exactly one added handoff Markdown document, **no changes to Python source or tests**. Thus the existing remediation QA is reusable and has NOT been executed again here.
- GitHub Actions remediation run: https://github.com/minhtri22/TokenToModel-Lab/actions/runs/43573016701 ; verified `head_sha=cf38f879...`, run `success`, job `scoped-nonr8-cpu` `success`; handoff records **37/37** (29 prior + 8 additional negative regressions). `SAME_AGENT_SEPARATE_CHECKER`, Ubuntu/Python 3.12.16; Windows QA not executed. **Not independent G0**, not R8 science.
- CI-reported SHA-256 (not recomputed by this reviewer): `gold_contract.py=a359758b97f6426629cc30293e74882f27a65ca13b887f65bd5ae7ab2cdaadde`; `folds_raters.py=7f2cfd23252a86354b91383351cea7ccede987c2daba80d6b6649f6bdcb9e853`; `restricted_oracles.py=4fc20ef92d02e22a4bf33edad6da40d1bb2c13df25ea37e87229038bc060c5e9`; `test_integrated_source_only.py=7db6c1e513d0d0ee8790d17dea9dbfad6df6aa0688a7f15828b15207aac90012`; `restricted_oracles.PATTERN=ffdfc06eb76bebd35e1f6185fafd4525d244149d7f64838bbe1f688ddf406d2e`.
- This new report is placed in `r8/reviews/`, NOT `r8/integrated_closure/`; the scoped QA workflow push path filters only `integrated_closure/**` and the workflow YAML. No repeat QA is requested.

## 2. G0 source/protocol readback: observed results

Read:
- [V4 scientific contract](https://github.com/minhtri22/TokenToModel-Lab/blob/b8410d9c1f77a733036e980b567de73c316f8725/docs/research/vector-memory/r8/TTM_VM_V4_R8_V4_GOLD_FOLD_ORACLE_RATER_OWNER_SCOPE_SINGLE_PACKET_DESIGN_ONLY_20261114.md)
- [Machine-readable restricted-oracle contract](https://github.com/minhtri22/TokenToModel-Lab/blob/b8410d9c1f77a733036e980b567de73c316f8725/docs/research/vector-memory/r8/R8_V4_RESTRICTED_ORACLE_AND_RATER_CONTRACT_DESIGN_ONLY.json)
- [gold_contract.py](https://github.com/minhtri22/TokenToModel-Lab/blob/cf38f8792253fe106cbb6a641f189882fb96e9d5/docs/research/vector-memory/r8/integrated_closure/gold_contract.py)
- [folds_raters.py](https://github.com/minhtri22/TokenToModel-Lab/blob/cf38f8792253fe106cbb6a641f189882fb96e9d5/docs/research/vector-memory/r8/integrated_closure/folds_raters.py)
- [restricted_oracles.py](https://github.com/minhtri22/TokenToModel-Lab/blob/cf38f8792253fe106cbb6a641f189882fb96e9d5/docs/research/vector-memory/r8/integrated_closure/restricted_oracles.py)
- [test_integrated_source_only.py](https://github.com/minhtri22/TokenToModel-Lab/blob/cf38f8792253fe106cbb6a641f189882fb96e9d5/docs/research/vector-memory/r8/integrated_closure/test_integrated_source_only.py)

### B03 — source logic improvements, scoped positive readback

`folds_raters.postcheck()` now fingerprints by unique case ID (not blueprint ID), requires twins per blueprint (default 2), validates case identity and pre-blueprint coverage, unions twins, compares actual case pairs on identical event/card or normalized word-5gram Jaccard >=0.8 and flags cross-pre-fold edges without repartition. `preassign()` maintains blueprint-level pair/event/template graph and HMAC-based component allocation. Abstract four-rater counts remain **proposal only**: 64 cases, 128 ratings, 32 per rater, no twin exposure. **PASS_SCOPED_SOURCE_OBSERVATION**, not G0 overall PASS. Real 32-blueprint/64-case manifest, public-order freeze, and private HMAC assignment remain G2/G3 work.

### B04 O2/O5 — source logic improvements, scoped positive readback

`_o2_features()` drops invariant sum-of-positions and includes position-weighted metadata. `_o1_features()` requires explicit public row position/count. `_o5()` uses TRAIN SELECT cases and positive/negative weights 0.5 / (0.5/31), predicts candidate keys without reading held-out actions for prediction. `aggregate_o5_folds()` rejects duplicate held-out case identities, marks incomplete OOF coverage `OOF_PARTIAL_NOT_ESTIMABLE`, and retains the 20/32 raw warning **descriptive only**. Holm family O2/O3/O4/O5/O6 requires defended group exchangeability; absent this, inference `NOT_ESTIMABLE`. O7 is an allowed lexical comparator; O8 is non-R8 symbolic trigger test, not real R7 replay. **PASS_SCOPED_SOURCE_OBSERVATION**, not G0 overall PASS.

### G0-F01 [MATERIAL] O1 violates the order-only feature boundary

`restricted_oracles.py` line 19–24 declares O1 `card order/card count only`. The machine-readable contract O1 lists `row_position_decile` and `card_position_extrema`; the scientific protocol calls O1 **order-only**. Yet `_o1_features()` lines 60–71 adds `first_key_length` and `last_key_length`, which are public **key metadata**, not order/count-only. This contaminates O1/O2 feature segregation. `test_34` tests row decile variability but does not guard O1 against key-length feature contamination. **Unresolved actual code/contract inconsistency => G0 HOLD.**

### G0-F02 [MATERIAL] B01 invalid-fixture semantics disagree with gold code and regression tests

Scientific V4 B01 states: circular support chain and contradictory equally authoritative sources are **INVALID FIXTURE, not silently resolved**. `gold_contract._proof_dependency_closure()` (lines 20–36) instead returns `None` for a dependency cycle; `resolve()` (lines 87–107) treats that as missing proof and returns `ABSTAIN`. Likewise equally authoritative verified contradiction (lines 67–76) results in `ABSTAIN / UNRESOLVED_AUTHORITY`; `test_08` and `test_10` explicitly assert these behaviors. There is no separate invalid-fixture state for these documented conditions. **A valid ABSTAIN case and a malformed fixture must not be silently conflated.** The contract or implementation must be reconciled prospectively before a G0 PASS.

### G0-F03 [FEATURE-BOUNDARY REVIEW] O3 ngrams can include unregistered adjacent lexical tokens

Scientific V4 frames O3 as status/authority **marker-only**; the source `FEATURE_BOUNDARIES` names marker tokens and precommitted marker ngrams. `_o3_features()` (lines 108–124) dynamically adds all 1- and 2-grams in full card text whenever any marker substring appears in the ngram. Thus e.g. a marker-adjacent accession token may enter `markergram=signed accession_x`, not just the marker itself. The implementation should either prove these context terms are in the predeclared allowed class or restrict them. **Hold source boundary adjudication; no assertion of observed R8 leakage (R8 does not exist).**

### Remaining source-readback qualifications

B01 `receipt_f07()` exhibits a toy truth-conditional authorized accession/event edge flip, but owner adoption of P-REC-V1 is G1, and private record-derived proof/validator provenance is G2. Grouped splits guard pre-component overlap, but enforceable complete real 32-pair/64-case manifest and real public row ordering are still unverified pre-generation custody/validator prerequisites. B05 remains descriptive-only: 64 cases or 128 rater decisions are **not** 64/128 independent scientific samples. No inference may assert absence of shortcuts.

**G0 final: `HOLD_INDEPENDENT_SOURCE_PROTOCOL_CONTRACT_MISMATCH`.** Reviewer identity/classification: separate GPT-6 AI source readback; not human, not implementation-agent QA, not scientific execution. No additional tests were run.

## 3. G1 authenticated owner, rights and PII — evidence inventory

Public baseline: [OWNER_RIGHTS_CUSTODY_DECISION_PACKET_PENDING.json](https://github.com/minhtri22/TokenToModel-Lab/blob/cf38f8792253fe106cbb6a641f189882fb96e9d5/docs/research/vector-memory/r8/integrated_closure/OWNER_RIGHTS_CUSTODY_DECISION_PACKET_PENDING.json), Git blob SHA-1 `7bd1905e699db32dac479b39f480433877a33c9a` (not SHA-256). Also [R8_V4_OWNER_SCOPE_AND_RATER_SELECTION_PENDING.json](https://github.com/minhtri22/TokenToModel-Lab/blob/b8410d9c1f77a733036e980b567de73c316f8725/docs/research/vector-memory/r8/R8_V4_OWNER_SCOPE_AND_RATER_SELECTION_PENDING.json). These are **templates**, not owner approvals.

| Owner item | Public evidence state | Required one-packet authenticated decision |
|---|---|---|
| Scientific scope | `PENDING` | `ADOPT_R8_D_DESCRIPTIVE_ONLY` OR `RETAIN_CONFIRMATORY_OBJECTIVE_NO_GO` |
| Blind raters | `PENDING` | `FOUR_RATERS_TWO_PER_CASE` OR `TWO_RATERS_DISJOINT` (if R8-D) |
| P-REC-V1/one-key | `PENDING` | Explicit approval or rejection of toy-domain policy + SELECT/ABSTAIN scoring |
| Synthetic-source rights/PII | `NOT_ATTESTED` | Scoped source class, provenance/use rights, PII/privacy rule, actual authority, date, signed/linked owner record |
| Owner signature/record | `NOT_SUPPLIED` | Authenticated owner evidence; recommendation is not consent |

**G1=`HOLD_OWNER_DECISION_RIGHTS_NOT_ATTESTED`.** No owner choice, rights approval, or PII permission was manufactured by this reviewer.

## 4. G2 authorized private custodian — evidence inventory

The same pending packet reports `status=NOT_VERIFIED`, `private_material_read=NOT_EXECUTED`, `gold_access=NO`, `private_storage_uri=REDACTED_NOT_SUPPLIED`, and `rater_allocation_secrets=NOT_CREATED`. No authorized real private endpoint, ACL attestation, sentinel/approved existing fixture read/write/readback, retention/access rules, protected future HMAC allocation custody, private validator one-key source-lock receipt or independent custodian signoff was supplied/verified in this review. CI source SHA-256 and Git blob identity are **not a substitute for private byte custody**.

The G2 pre-generation check should use only an explicitly authorized **non-R8** sentinel/fixture. **Do not require SHA-256 for nonexistent R8 gold.** Actual R8 candidate/gold/proof readback would be a different post-G3 requirement before G4/G5. Never publish private storage paths, ACL specifics, keys, allocations, gold, or secret-dependent labels.

**G2=`HOLD_PRIVATE_CUSTODIAN_READBACK_NOT_VERIFIED`.** No private sentinel was written or read.

## 5. One integrated decision and minimum next action

| Gate | Disposition |
|---|---|
| G0 — independent design/source | **HOLD** (F01 O1 feature boundary; F02 B01 invalid-fixture semantics; F03 O3 boundary review) |
| G1 — owner/rights/PII | **HOLD_NOT_ATTESTED** |
| G2 — private custody/source-lock | **HOLD_NOT_VERIFIED** |
| G3/G4 | **NOT_EXECUTED** / generation **NOT_AUTHORIZED** |
| G5/G6 | **SEALED** |
| R7 | **FROZEN_FAIL** |
| R8 | **NOT_GENERATED** |
| Reader / GPU / PROBE256 | **0 / NO / SEALED** |

**GLOBAL DECISION = `HOLD_INTEGRATED`.** No automatic R8 generation. No G0 PASS from 37/37 same-agent synthetic QA.

**ONE next integrated operation:** Resolve F01–F03 at the pinned V4 feature/invalid-fixture boundary (one bounded source/contract correction only if a real change is approved), collect one owner-attested scientific-scope+rater+P-REC-V1+rights+PII decision, and obtain one authorized independent private-custodian readiness/source-lock readback. Then a distinct reviewer adjudicates exact resulting hashes and the three gates together. Reuse unchanged PASS results; any future source change requires **targeted** QA for changed behavior, not reflexive replay of all 37 tests. R8-C confirmatory with 32 pairs remains NO-GO; only a future `GO_R8_D_CANDIDATE_AUTHORING_ONLY` could permit a separately authorized exploratory authoring step.

No secret material, new rater packet, or private locator is included in this report.
