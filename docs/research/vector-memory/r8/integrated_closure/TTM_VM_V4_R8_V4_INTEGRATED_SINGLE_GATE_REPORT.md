# TTM VM V4 R8 V4 — Integrated Single-Gate Source / Evidence Closeout

**Operation:** `TTM_VM_V4_R8_V4_INTEGRATED_BLOCKER_CLOSURE_SOURCE_QA_OWNER_CUSTODY_SINGLE_GATE_NO_GENERATION`  
**Date:** 2026-11-14  
**Role:** Same-agent implementation and source QA; **NOT OWNER, NOT INDEPENDENT EXTERNAL REVIEWER, NOT BLIND RATER**  
**Mode:** SOURCE IMPLEMENTATION + CPU NON-R8 SYMBOLIC QA; NO_R8_GENERATION, NO_TEST, NO_READER, NO_GPU, NO_PROBE256.  
**Verdict:** `DECISION=HOLD_INTEGRATED`.

## 1. Immutable input readback

Scientific design source commit **`b8410d9c1f77a733036e980b567de73c316f8725`**. GitHub connector reported the following original Git blob SHA-1 (not misrepresented as SHA-256):

| Input | Git blob SHA-1 |
|---|---|
| `TTM_VM_V4_R8_V4_GOLD_FOLD_ORACLE_RATER_OWNER_SCOPE_SINGLE_PACKET_DESIGN_ONLY_20261114.md` | `353d86307b93cca4c6a183edf297e9ec552a6ed9` |
| `R8_V4_RESTRICTED_ORACLE_AND_RATER_CONTRACT_DESIGN_ONLY.json` | `68d7e105a1e14c71c599434e7bf19ec1273b967a` |
| `R8_V4_DESIGN_CONTRACT_STATIC_CHECK.py` | `3c5280895f78361c3e33b2c1b4503ae2ebf78094` |
| `R8_V4_OWNER_SCOPE_AND_RATER_SELECTION_PENDING.json` | `e9b6a3942b3de60d041ea240d43f5d61f6836cff` |
| `TTM_VM_V4_R8_V4_SINGLE_PACKET_DESIGN_ONLY_ADJUDICATION_20261114.json` | `3e31d31facbdcbc1e9b48166736d44263ea89f0c` |
| Independent V3 review `reviews/TTM_VM_V4_R8_V3_INDEPENDENT_PROTOCOL_REVIEW_20261114.md` | `0a6287dfd6dac9a83438bf5043b8733527eed69c` |

Handoff input Git commit **`aa529e207409da8ea32dba22583b16718deb8954`**, blob SHA-1 **`3910bd28847630ff553781c99139ce688d40c5ae`**. Independent V3 findings B01/B03/B04 HOLD and B05 descriptive-scoped PASS are **historical findings, not independent V4 approval**.

## 2. Actual new files and implemented scope

All new artifacts reside on branch `evidence/ttm-vm-v4-r8-v4-integrated-closure-20261114`, based on handoff commit; no historical frozen source/receipt overwritten:

1. `docs/research/vector-memory/r8/integrated_closure/gold_contract.py`: B01 six-field answer hypothesis; typed evidence for IDENTITY/SCOPE/EVENT/LOCATION/TIME_VALID/AUTHORIZED with computed NOT_DEFEATED; minimal support sets; authority rank/time conflict, negative-record ABSTAIN, duplicate keys and one-key rejection, transitive dependency/cycle rejection, multiple hypotheses, reason precedence. P-REC-V1 **toy-only** F07 symbolic twin reconstructs SELECT vs ABSTAIN from authoritative accession-event edge; keyword-only false positive checked. Typed `verified` upstream claims still require **independent authorized private data provenance**, so this is not an attested real gold validator.
2. `.../folds_raters.py`: B03 deterministic G_pre by pair/event/template BLUEPRINT edges; HMAC-SHA256 keyed component ordering and greedy four-fold preassignment; G_post NFKC/lowercase Unicode word-5-gram overlap, Jaccard >=0.80, duplicate event/card edges, **no repartition** on cross-fold leak. Component IDs distinct from authored `event_graph_id`. Four-rater **abstract proposed** 8 families × 4 pairs, 64 cases, 128 ratings, each rater 32 = 16 SELECT + 16 ABSTAIN, no twin overlap. No actual private allocation or HMAC key created/published.
3. `.../restricted_oracles.py`: B04 executable CPU O1 order, O2 metadata, O3 marker, O4 question and question+metadata, O5 card-key TRAIN SELECT-only logistic with +0.5 and 31×0.5/31 weighting, O6 combined action/key/joint with ABSTAIN, O7 train-vocabulary TF-IDF and BM25 lexical comparator, O8 R7 known marker/ID/position/date-location **rule-trigger regression only**, not actual R7 rerun. O5 inference covers **all** held-out cases, never uses held-out action to decide whether to predict a key. Input schema fixed 32 cards, component-disjoint TRAIN/test guard. Holm for O2/O3/O4/O5/O6 (FWER .05, first .01); without justified blocked null, statistical outcome `NOT_ESTIMABLE`.
4. `.../test_integrated_source_only.py`: **29** actual source/symbolic QA cases including counterfactual edge flip, keyword false-positive, different locations for same record, duplicated target/key, equal competing authority, negative record, circular proof, fold cross-edge invalidation, rater balance, O1–O8 execution, training isolation, O5 test-action isolation and frozen R7 phrase regression trigger.
5. `.../OWNER_RIGHTS_CUSTODY_DECISION_PACKET_PENDING.json`: one public-safe **decision-ready** owner/rights/PII/P-REC-V1/rater choice/private custody readback packet, all approvals explicitly PENDING or NOT_ATTESTED; no forged signature, private URI, gold or allocation secrets.
6. `.github/workflows/ttm-vm-r8-integrated-closure-qa.yml`: bounded scoped CPU QA on this evidence branch only; exact package version install, frozen design static checker, compilation, 29-case unittest, SHA256 and regex readbacks.
7. This `TTM_VM_V4_R8_V4_INTEGRATED_SINGLE_GATE_REPORT.md` — single final report. No historical lineage entry silently rewritten.

## 3. Readback of actual CPU run and source locks

**Successful integrated QA:** GitHub Actions run [43570573752](https://github.com/minhtri22/TokenToModel-Lab/actions/runs/43570573752); runner source commit `197920ecb9f788cd4af594fa12811578272ef455`; job `132373854586`; **SUCCESS**, 2026-11-14 UTC; `Ran 29 tests in 1.065s: OK`. Original initial QA at run 43570282115 failed 1 of 28 on circular dependency; the source bug was fixed; the final run passed. Intermediate 28/28 at run 43570383863 also succeeded before adding O5 held-out action isolation check.

Actual runner versions: **CPython 3.12.16**, Ubuntu Linux Azure runner, **scikit-learn 1.8.0, NumPy 2.3.5, SciPy 1.17.0**. The user Windows 11 / Python 3.12 machine was **NOT EXECUTED** in this operation; do not infer Windows reproducibility from Linux QA.

GitHub Actions `sha256sum` readbacks from the final successful run:

| UTF-8 source | SHA-256 |
|---|---|
| `gold_contract.py` | `a359758b97f6426629cc30293e74882f27a65ca13b887f65bd5ae7ab2cdaadde` |
| `folds_raters.py` | `04171d35704b9e48a59a5f64175703ed9acaf88eedbf64f3752ef350070d9d86` |
| `restricted_oracles.py` | `57f94f323b954e60659abea552d91795c5b8b07a060565b6ca096198156c45f8` |
| `test_integrated_source_only.py` | `5b914840bbd76565516d798c9cbcb06a0a2374f8879c7ba1f4f0fb4ff7c871ee` |
| `restricted_oracles.PATTERN` UTF-8 literal `(?u)\\b\\w+\\b` | `ffdfc06eb76bebd35e1f6185fafd4525d244149d7f64838bbe1f688ddf406d2e` |

Frozen design static checker on original V4 contract: `PASS_SCOPED`. Source compile: PASS. Source-only synthetic unittest: **29/29 PASS**. O1–O8 CPU runs: **EXECUTED_NON_R8_SYNTHETIC_ONLY**. O8 actual R7 real data regression: **NOT_EXECUTED**; static symbolic trigger test PASS. No real R8 prediction, significance p-value, TEST, independent reviewer or gold authority claim.

**QA independence classification:** `SAME_AGENT_SEPARATE_CHECKER`. Running GitHub Actions does not by itself create a distinct human/AI protocol reviewer; `EXTERNAL_INDEPENDENT_REVIEW=NOT_EXECUTED`.

## 4. Integrated blocker adjudication

| Blocker | Source/QA work | Residual |
|---|---|---|
| **B01** gold/F07 | Implemented; symbolic SELECT/ABSTAIN edge flip and negative fixtures PASS | P-REC-V1 owner acceptance and independently validated private proof provenance PENDING |
| **B02** matched question | Preserved; paired 50% is mathematical tautology, not anti-shortcut PASS | No release claim |
| **B03** graph/folds/raters | Pre/post graph, crossfold invalidation and 128-score abstract proposal validated | No real G2 key, blueprint private custody or owner rater choice |
| **B04** O1–O8 incl O5 | Executable scoped CPU source tests PASS; source & regex hashes read back | No independently approved source lock, actual R7 readback or R8 grouped inference |
| **B05** inference | `PASS_SCOPED_DESCRIPTIVE_ONLY` retained, no significance implies no leakage | `HOLD_INCONCLUSIVE` for no-leakage inference; R8-C `NO_GO` |
| **B06** rights/custody | Consolidated public-safe owner/custody packet created | Owner rights/PII `NOT_ATTESTED`, private custody `NOT_VERIFIED` |

### One gate decision

| Gate | Status |
|---|---|
| **G0** distinct independent V4 protocol/source review | **HOLD** — independent V3 review exists, but no distinct V4 pass |
| **G1** authentic owner scientific scope + rater choice + rights/PII | **HOLD** — `PENDING / NOT_ATTESTED` |
| **G2** private source/gold custody, validated one-key proof, protected HMAC key & approved exact source-lock | **HOLD** — source hashes + scoped synthetic QA exist, private readback and independent full-source review absent |
| **G3** R8 generation | `NOT_AUTHORIZED / NOT_EXECUTED` |
| **G4** R8 candidate QA | `NOT_EXECUTED` |
| **G5** blind CAL / rater exposure | `SEALED` |
| **G6** threshold / PROBE256 / TEST | `SEALED` |

**R7:** `FROZEN_FAIL`, unchanged. **R8:** `NOT_GENERATED`. **Reader:** 0. **GPU:** NO. **Private gold:** NOT_ACCESSED. **R8 blind packets:** NOT_CREATED. **Source class:** `AI_AUTHORED_SYNTHETIC_EXPLORATORY_ONLY_PROPOSED`, not authorized.

### Smallest consolidated recovery evidence (no follow-on micro-permits)

At most **one** owner/rights/custody + distinct independent-review readback packet can satisfy the remaining gates: (1) a truly separate reviewer adjudicates B01/F07, B03 graph/rater and B04 O1–O8 exact source and B05 scope; (2) authenticated owner explicitly chooses R8-D vs R8-C and four vs two raters, accepts/rejects P-REC-V1 and rights/PII/source class; (3) authorized custodian privately attests storage/readback SHA-256, validator/one-key proof and protected allocation key and pins accepted exact source/runtime, without publishing secrets. **These are missing evidence, not reasons to spawn V5/V6.** No permission implied. If owner chooses confirmatory R8-C, retain NO_GO for the current 32-pair proposal.

**DECISION=HOLD_INTEGRATED**
