# TTM — Evidence-gap priority matrix after P0-A MEAS Q001 CLOSED_HOLD

**Operation:** `TTM_POST_P0A_Q001_CLOSED_HOLD_EVIDENCE_GAPS_AND_NEXT_QUESTION_PRIORITY_MATRIX_SOURCE_ONLY_SINGLE_GATE`  
**Date:** 2026-11-16 · **Repository:** `minhtri22/TokenToModel-Lab` · **Source-of-truth exact main:** `f6d7d304ef79f889dc24f7282ef6e2aceebf44af`.  
**Scope:** `READ_ONLY_SOURCE_ANALYSIS · GOVERNANCE_EVIDENCE_PROPOSAL_ONLY · NO_SCIENCE · NO_SOURCE_ACCESS · NO_NEW_GOLD_SCORER_RATER · NO_MODEL_GPU · NO_NEW_RESEARCH_BRANCH · NO_NEW_QUESTION_ID_REGISTERED`. Historical `lineage.md` **must stay unchanged**.

## 1. Baseline: question closed, no science GO

Q1 `TTM-P0A-MEAS-Q001` registered, Q2/Q3 source-only accepted; owner Q4 `GO_Q4_CLOSE_HOLD_EVIDENCE_INSUFFICIENT` and [PR #25](https://github.com/minhtri22/TokenToModel-Lab/pull/25) merged. `Q4_CLOSED_HOLD_EVIDENCE_INSUFFICIENT · NO_ACTIVE_QUESTION · EMPIRICAL_HOLD · SCIENCE_NOT_AUTHORIZED · F0_F2_PAUSED`. Q4 closed one **evidence-review Question Gate**, not permanent STOP or science FAIL. This roadmap **does not reopen Q001**.

Lineage observations, distinguished by scope:
- **L0010** F1/WP30 E0 byte-BPE actual tokenizer training PASS scoped; does not establish semantic evaluation rights or quality.
- **L0011** T4 VAL H1 `PASS_H1_CONFIRMATORY_VAL_SCOPE`, model NLL 3.5223388517 vs bigram 3.9972314170 (11.880537% relative improvement), exactly one pilot seed, **not** semantic adherence.
- **L0012** T4 TEST `PASS_TEST_HOLDOUT_DESCRIPTIVE_SCOPED` with NLL 3.48359107334 vs 3.97360374532 (12.3316944% relative improvement) based on original single-use TEST; not independent token-level recompute. TEST is **CONSUMED/SEALED**; never rerun.
- **L0013** strict logits `FAIL_STRICT_LOGITS_32_OF_32_SCOPED_SYNTHETIC`; **L0014** GELU_ERF change `PASS_HELDOUT_STRICT_LOGITS_4_OF_4_SCOPED_GELU_ERF`. Do not generalize one configuration to all KV/Flash/lengths or call an inference transport fix a semantic finding.
- **L0015** FRESH16 V2 `FAIL_PRE_REGISTERED_FRESH16_V2_SCOPED` with H1=0/16 H2=0/8; this does not refute valid NLL observations nor identify unique failure mechanism.
- **L0016 + L0022** FC01 exploratory scoped closure and D1 R1 `HOLD_ONTOLOGY_FEASIBILITY`; 32 pair witnesses are bounded constructive evidence, not a validated 16-item action-causal OOD benchmark.
- **L0023–L0024** VM retrieval/cosine/marker failures and structured selector scoped success, R8 HOLD; EmbeddingGemma OOD256 residual-transport PASS scoped, **not** generalized language/semantic causality.
- **L0025–L0026** H-DATA-S1 no demonstrated scoped semantic benefit, FINAL24 adherence negative while H-DEC repetition candidate only; preserve all historical blind/FINAL closure and do not replay.
- **L0027–L0029** T6 technical merge, P07 PAUSED and historical global branch V2 inventory/priorities are **dated 2026-11-14 snapshots**, not current branch-wide new science certification.

**Central scientific ambiguity:** reliable language-model NLL versus poor scoped prompt adherence is a gap, not evidence that architecture, objective, data, decoding, or rater is the unique cause. The hardest next decision is whether **a valid measurement construct can even identify this causal comparison** on lawful prospective items.

## 2. How priority was assigned (qualitative, no fabricated utility)

**Lexicographic noncompensatory screening:** (1) rights/PII/access hard veto; (2) whether proposed evidence can change a real scientific/engineering decision; (3) whether item/ontology/gold/parity is valid; (4) provenance and independence, fresh vs consumed TEST; (5) reuse across candidate hypothesis families; (6) expected burden and reversibility **only when grounded**. `P0` is a **legal dependency**, not a ranking of model performance. Within `P1`, no false absolute sequence: ontology/frame, parity, independent gold, prereg must form **one integrated admissible measurement packet** with correct internal order, not an endless sequence of micro-permits. Exact costs, N, coverage, uncertainty, probabilities, and quantitative expected value **UNKNOWN**.

**Why no weighted MCDA:** source availability/rights, sampling N, rater correctness, budget and performance have no verified cardinal estimates; safety/construct veto cannot be outscored. Rank reflects a *conditional decision-value argument*, not numeric expected ROI or a frozen experiment selection.

## 3. Evidence-gap matrix: what proof can reverse decisions? (evidence gaps, NOT Q2/Q3 data-creation tasks)

| Gate / priority | Current evidence | Smallest decision-relevant prospective proof (not authorized here) | What changes if proven / refuted |
|---|---|---|---|
| **P0_PREREQUISITE_NOT_SCIENCE: G0_RIGHTS** | `NOT_VERIFIED` | Written rights/PII/copyright/transform/annotation/third-party rater scope and owner legal authorization; `AD-01R X20 before source access` | If unattainable, keep empirical HOLD or consider a lawfully distinct source; if attested, enable only separately approved scoped feasibility inspection |
| **P1_HIGH: G1_SOURCE_CONSTRUCT** | `NOT_VALIDATED` | Candidate sampling frame fixed prospectively; typed entity/location/time, authority, bounded time closure, witness/negation/exclusivity; all candidate/eligible/reject/abstain denominators and reasons, nonzero coverage with prereg threshold; `E1 F-H01 X14 X17 X19` | Construct feasible with honest coverage -> measurement remains candidate; systemic insufficiency -> HOLD/SIMPLIFY/PIVOT under new Q4, not post-hoc filtering |
| **P1_HIGH: G2_FULL_EFFECTIVE_PARITY** | `NOT_CAPTURED` | All label-changing material support/refutation/exclusivity facts preserved in both model-effective and rater-effective payloads after renderer/tokenizer/window/truncation; separate hidden key/oracle custody; exact byte provenance; `E2 X13 X15` | Parity established -> model-vs-rater agreement interpretable; parity violation -> item REJECT and measurement admission HOLD, not UNKNOWN |
| **P1_HIGH: G3_GOLD_RATER** | `NOT_CALIBRATED` | Independent source-grounded hidden gold derivation, blind same-task calibration and disagreements/adjudication, no shared ontology error, correct custody and permitted rater use; `E4 M1 M4 X18` | Validated gold -> semantic adherence distinguishable from evaluator failure; shared error -> benchmark HOLD |
| **P1_INTEGRATED_FREEZE: G4_PROSPECTIVE_PREREG_COST** | `NOT_FROZEN` | Question/endpoint, unit and n with uncertainty/power; candidate/eligible/reject/abstain coverage; exact REJECT precedence preserving all reasons; threshold, STOP, budget and owner role frozen before outcomes; `E5 AD-07 F-H01 X21` | GO/HOLD/STOP becomes auditable under frozen decision threshold; unknown costs cannot justify quantitative promise |
| **P2_CONDITIONAL_ONLY: G5_CAUSAL_CONTRASTS** | `NOT_EXECUTED` | Prospectively matched/group-disjoint fact-only vs cue-only contrasts with balanced lexical/position/length and prereg AD-06, only if causal shortcut attribution is desired; `E3 M3 F-M04 for causal claims ONLY` | Distinguish genuine fact sensitivity from cue shortcut; without contrast avoid causal claim |

**G0 rights before every inspection.** Rights attestation itself is not scientific evidence. It allows only what the owner and rights scope explicitly authorize. If G0 fails, do not try to 'fix' rights by synthetic/pseudo-licenses, or infer that the measurement itself is mathematically impossible.

**G1/F-H01/X17 + F04 correction:** Family discovery and feasibility cannot select a convenient 'at least one' family after observing outcomes. Future protocol **must** prospectively enumerate the eligible family/source search universe and sampling unit, candidate-family counts, search/inspection order or randomization/selection rule, screened/inspected/rejected family counts with ALL exclusion reasons, and a candidate-item frame within every assessed family. Keep exploratory family discovery separate from a **fresh, disjoint confirmatory family/sample** untouched by discovery-based tuning; if independence cannot be achieved, report exploratory-only and never call it prospective confirmatory PASS. Freeze family and item denominators, eligible/reject/abstain rules, all reason codes, deterministic primary rejection precedence, family/item coverage threshold, sample size, uncertainty/power, cost/STOP **before decision-relevant outcome inspection**, under separately approved owner scope. Never hide rejected families or include only easy items. Source rights attestations can be collected as documents before access but **are not model/measurement outcomes**. `FALSE` needs visible negation or applicable exclusivity; `UNKNOWN_VALID` needs bounded and temporally complete source.

**G2/X13/X15:** source oracle facts hidden from model/rater must not silently change label; compare whole label-changing material-fact sets after tokenizer/context trimming, not merely 'shared positive witness'. Missing decisive fact → HOLD gate/item REJECT, not an epistemic UNKNOWN.

**G3/X18:** two raters agreeing can both be wrong. Use blind same-task independently source-grounded truth and rights-compliant roles.

**G4:** freeze eligibility rules, sample unit, endpoint/threshold/uncertainty, STOP and real budget before any outcomes. No retrospective tailoring of N, coverage denominator or cost assumptions.

**G5/E3:** shortcut contrast is necessary for **causal attribution** only; it is not a reason to block a paper-only evidence matrix. E6 checkpoint/runner custody is a distinct **execution** veto.

## 4. Candidate directions — priorities are conditional, not automatic question gates

| Rank | Direction / nature | Existing decision evidence | Required gates (non-interchangeable) | Admission |
|---|---|---|---|---|
| **1 — P1 capability gap** | **Measurement validity / construct evidence**, NOT an approved new `LOCATED_AT` QuestionID | L0011/L0012 NLL PASS versus L0015/FRESH16 semantic FAIL; Q001 Q4 already `CLOSED_HOLD` | Rights G0 then future distinct question/delta evidence; G1 family ontology/denominator, G2 full parity, G3 gold/rater, G4 prereg only *after* Q4 scoped GO in I1/I2 | `BLOCK_NEW_MEASUREMENT_Q_REPETITION_F01` |
| **2 — P2 science later** | Data vs Objective | L0016, L0025, L0026 scoped findings | Rights/source G0; measurement G1–G4; E6 model/checkpoint rights, provenance and owner-scoped run permit | `NOT_OPENED` |
| **3 — P2 science later** | Decoder/Context/Capacity | L0011/L0012/L0015/L0026 do not localize root cause | Source G0 when external data are involved; G1–G4 for semantic scoring; E6 checkpoint/executable rights, custody and execution permit | `NOT_OPENED` |
| **4 — P3 semantic value, potentially P1 engineering value** | **T5/T6 CPU strict-logit parity**, distinct `ENGINEERING` candidate only | L0013 strict FAIL 32/32, L0014 GELU_ERF PASS 4/4 in bounded config; T6 merged scoped | No semantic gold requirement if strictly synthetic numerical parity; nevertheless exact P02/GGUF/executable/custody hashes, checkpoint/fixture permissions, E6/AD-00/AD-01C, technical negative/regression QA, independent reviewer and explicit Q4 owner scoped GO BEFORE running | `NOT_OPENED` |
| **5 — P3 separate science** | EmbeddingGemma / Vector Memory | L0023 VM mixed + HOLD; L0024 OOD residual transport PASS scoped | External-source G0, semantic validity G1–G4, E6 model/data permission and execution, shortcut contrasts if causal claim | `NOT_OPENED` |
| **6 — P3 design-only** | D1 Bridge action-causal oracle redesign | L0016–L0022 ontology feasibility HOLD | G0 for any outside source, G1 true action oracle/temporal closure, G3 independent source-rights-valid gold; prospective prereg G4 before outcomes; E6 only if implementation/model execution later | `NOT_OPENED` |

**Dependency taxonomy (F03):** `source_access_prerequisites` mean AD-01R/PII/rights before external source access (or explicit lawful synthetic provenance when no external source); `measurement_validity_prerequisites` mean G1/G2/G3/G4 for semantic-scored decisions; `execution_prerequisites` mean E6/AD-00/AD-01C checkpoint/runner/fixture rights and hashes, technical QA and a separate, scoped owner execution decision. An empty semantic-measurement dependency **never means** the model may execute without permissions. No fixture is produced in this document.

**Difference between objectives:** A missing measurement construct is highest-value **scientific information** for Small4M semantics; a lawful synthetic CPU parity audit may be more **practically executable** if the owner prioritizes engineering. The 2026-11-14 old branch-review ranking is historical. The prioritization table does not assert verified rights or readiness for either path.

## 5. F01/F02 closure — NO new P0B QuestionID; Question-First policy order

**RETRACTED, NOT REGISTERED:** previous proposed placeholder `TTM-P0B-MEAS-FEASIBILITY-PROPOSED` was materially overlapping with registered and CLOSED_HOLD `TTM-P0A-MEAS-Q001`. It is hereby **withdrawn as a selectable Question Gate proposal**; retained only as immutable historical evidence at pre-remediation candidate `cef770d386c2e6862dc33e0f6e7d4e1866f7c00b`. Changing the label from source-only design to 'lawful prospective feasibility' alone adds evidence requirements but **does not add a new falsifiable scientific decision**. No new lawful source attestation or distinct oracle was verified here. The predecessor stays `Q4_CLOSED_HOLD_EVIDENCE_INSUFFICIENT`, `ACTIVE_QUESTION=NONE`.

**Distinctness hard veto:** a future *measurement* Question Gate can be entertained only if (a) exact-custodied genuinely new, rights-attested evidence or a distinct verified source family, or (b) a separately falsifiable construct/decision demonstrably outside original `LOCATED_AT` Q1, is identified and explained before Q1 owner registration. State a counterfactual: *would Q001's already-closed Q1–Q4 have answered the same proposed question?* If YES without distinct new fact or decision, reject as `DUPLICATE_CLOSED_Q001` and keep `NO_ACTIVE_QUESTION`. Rights attestations alone do not establish empirical construct validity.

**F02 exact stage machine** (no prospective packet performed now):
1. `Q0_CLOSED_OR_NO_ACTIVE` → new owner-selected `Q1_QUESTION_REGISTERED` **only after distinctness and a valid decision delta**. Q1 is paper/question registration.
2. `Q2_FRAMEWORK_AND_ALTERNATIVES_EVALUATED` → `Q3_ANSWER_REVIEWED`: **source/design-only** from already lawfully available pinned materials; no actual source inspection, dataset, fixture creation, gold, model run, hidden TEST/FINAL or rater score. Rights documentation may be checked without accessing underlying restricted source bytes.
3. `Q4_OWNER_DECIDED_AND_CLOSED`: owner chooses KEEP/SIMPLIFY/PIVOT/STOP/HOLD; only `GO_SCOPED_IMPLEMENT` with lawful provenance allows later I1. Q4 cannot rely on I1/I2 outcomes it has not yet authorized.
4. `I1_ONE_IMPLEMENTATION_BRANCH` then `I2_EXECUTION_AND_EVIDENCE` **only if separately authorized and AD-01R already verified before source access**: freeze prereg design, family/sample selection and cost/STOP **before seeing decision-relevant outcomes**; create/run only explicitly scoped lawful fixtures, parity checks and independent gold/rater. Model inference requires distinct E6 checkpoint/right/custody and owner run permit; none is granted here.
5. `I3_INDEPENDENT_ADJUDICATION` → `I4_MERGE_OR_EVIDENCE_ONLY_CLOSURE`: distinct review of actual evidence and owner terminal decision; no Q4 reused retroactively as an I3 empirical adjudication. Preserve scientific lineage rules and original TEST/FINAL custody.

**No micro-permits:** Future I1–I4 is a *single prospective scoped authorized packet with conditional internal stops*, not a bundle of auto-created QuestionIDs, authority grants or research branches. Where exact n, family universe, coverage threshold and cost ceiling are UNKNOWN, they are design unknowns — not invented freezes or PASS.

## 6. Owner choice after independent remediation review (proposal, not action)

**Recommendation:** `HOLD_NEXT_MEASUREMENT_Q_UNTIL_DISTINCTNESS_AND_NEW_RIGHTS_EVIDENCE`; preserve measurement-validity gap as top scientific bottleneck, **not** as an already-proposed/registerable P0B question. At present `NO_ACTIVE_QUESTION` remains the canonical state.

The owner will select **one** option only after exact candidate independent readback:
- **A — Measurement question, only with material new evidence or a genuinely distinct falsifiable decision:** do not reuse the withdrawn `P0B` placeholder, and do not reopen CLOSED Q001 by renaming. Q1–Q4 remain source-only until separately authorized I1.
- **B — Distinct technical ENGINEERING Question Gate candidate:** Does an exactly pinned P02 reference vs CPU GGUF with GELU_ERF (under a prospectively specified distinct context/KV configuration and fresh legal synthetic token-ID fixtures) achieve a preregistered strict-logits parity criterion, while preserving all historical negative/positive results? This is **only** a candidate wording; no new source/code/fixtures and no new unverified numerical threshold. Even synthetic runs need checkpoint, binary and fixture provenance/rights, QA, owner Q4 `GO_SCOPED_IMPLEMENT` and later scoped execution approval.
- **C — `NO_ACTIVE_QUESTION`:** no new QuestionID or research/implementation branch; preserve existing proof archive.

**Sensitivity:** Verified new rights/source lineage plus a separately bounded construct and gold could elevate a truly distinct measurement question. If those are unavailable, engineering can outrank measurement on immediate executability, without claiming a semantic root cause. New disjoint semantic evaluation could motivate data/objective or decoder controls; once-consumed TEST/FINAL24 never reused. No fabricated sample sizes, rights, predicted utility, ROI or costs.

`REVIEW_STATUS=HOLD_POST_P0A_EVIDENCE_PRIORITY` at reviewed candidate `cef770d386c2e6862dc33e0f6e7d4e1866f7c00b`; this amendment is a response, **not** an independent reviewer reversal. `GOVERNANCE_MERGE=NOT_AUTHORIZED` pending new distinct QA and explicit owner decision.

## 7. Exact source manifest and source QA boundary

| GitHub source | Git blob SHA-1 (at `f6d7d304ef79f889dc24f7282ef6e2aceebf44af`) |
|---|---|
| [lineage.md](https://github.com/minhtri22/TokenToModel-Lab/blob/f6d7d304ef79f889dc24f7282ef6e2aceebf44af/lineage.md) | `3409e036241deb1da6674619a2abc834bea8a2d6` |
| [docs/governance/ACTIVE_RESEARCH_GATE.md](https://github.com/minhtri22/TokenToModel-Lab/blob/f6d7d304ef79f889dc24f7282ef6e2aceebf44af/docs/governance/ACTIVE_RESEARCH_GATE.md) | `3d66a78fee3fa2ad5f8cdd3ca3117f67bf72dd01` |
| [docs/governance/ttm-post-q001/TTM_P0A_MEAS_Q001_Q4_OWNER_CLOSED_HOLD_GOVERNANCE_CLOSURE_20261116.md](https://github.com/minhtri22/TokenToModel-Lab/blob/f6d7d304ef79f889dc24f7282ef6e2aceebf44af/docs/governance/ttm-post-q001/TTM_P0A_MEAS_Q001_Q4_OWNER_CLOSED_HOLD_GOVERNANCE_CLOSURE_20261116.md) | `bb21cf560c91a083680e072adb7d5ce5a5508d11` |
| [docs/governance/TTM_QUESTION_FIRST_RESEARCH_ARCHITECTURE_LINEAGE_AND_MAIN_POLICY_20261115.md](https://github.com/minhtri22/TokenToModel-Lab/blob/f6d7d304ef79f889dc24f7282ef6e2aceebf44af/docs/governance/TTM_QUESTION_FIRST_RESEARCH_ARCHITECTURE_LINEAGE_AND_MAIN_POLICY_20261115.md) | `af1a879a2552f100c6669cb9ab6dc98c930d2e19` |
| [docs/governance/TTM_GLOBAL_BRANCH_EVIDENCE_QA_AND_RESEARCH_PRIORITY_20261114.md](https://github.com/minhtri22/TokenToModel-Lab/blob/f6d7d304ef79f889dc24f7282ef6e2aceebf44af/docs/governance/TTM_GLOBAL_BRANCH_EVIDENCE_QA_AND_RESEARCH_PRIORITY_20261114.md) | `09a9f9c5003d0e8d899151f7f426707eb1505d44` |
| [artifacts/governance/ttm-post-q001/TTM_P0A_MEAS_Q001_Q3_EVIDENCE_SUFFICIENCY_MATRIX_20261116.json](https://github.com/minhtri22/TokenToModel-Lab/blob/f6d7d304ef79f889dc24f7282ef6e2aceebf44af/artifacts/governance/ttm-post-q001/TTM_P0A_MEAS_Q001_Q3_EVIDENCE_SUFFICIENCY_MATRIX_20261116.json) | `674ef299cc4b6fb8dea6e35d47a96cea49e3cdbe` |
| [artifacts/governance/ttm-post-q001/TTM_P0A_MEAS_Q001_Q4_ALTERNATIVES_DECISION_MATRIX_20261116.json](https://github.com/minhtri22/TokenToModel-Lab/blob/f6d7d304ef79f889dc24f7282ef6e2aceebf44af/artifacts/governance/ttm-post-q001/TTM_P0A_MEAS_Q001_Q4_ALTERNATIVES_DECISION_MATRIX_20261116.json) | `2a4f9acd511b21ce22e922ff1fa3c370928a03a9` |

Historical `lineage.md` contains mixed technical and science entries because it is an append-only historical log; **current Question-First policy** only permits new scientific PASS/FAIL lineage appends with complete adjudication. This source-only priority report does **not** append to `lineage.md` or reclassify historical entries.

No model run, no source access, no checkpoint/scorer/rights assertion, no new science eligibility, no new QuestionID, no change to `ACTIVE_RESEARCH_GATE.md`. **Old author static QA 35/35 covers ONLY the original reviewed HEAD `cef770d386c2e6862dc33e0f6e7d4e1866f7c00b`, not this amendment.** Original distinct AI review verdict `HOLD_POST_P0A_EVIDENCE_PRIORITY` is preserved verbatim; this proposed remediation requires a NEW exact-HEAD distinct source review, never a self-claimed PASS. Reviewer should check F01–F05 and challenge the actual alternative technical question.

**Proposed next single action:** `TTM_POST_P0A_Q001_PRIORITY_F01_F05_EXACT_REMEDIATION_DISTINCT_SOURCE_READBACK_AND_OWNER_ONE_NEXT_QUESTION_SELECTION_SINGLE_GATE` — one exact remediation HEAD distinct review, then owner may choose exactly ONE genuinely new direction or `NO_ACTIVE_QUESTION`. Governance merge still needs explicit owner approval; no science or implementation.
