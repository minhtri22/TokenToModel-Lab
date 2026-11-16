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

## 3. Evidence-gap matrix: what proof can reverse decisions?

| Gate / priority | Current evidence | Smallest decision-relevant prospective proof (not authorized here) | What changes if proven / refuted |
|---|---|---|---|
| **P0_PREREQUISITE_NOT_SCIENCE: G0_RIGHTS** | `NOT_VERIFIED` | Written rights/PII/copyright/transform/annotation/third-party rater scope and owner legal authorization; `AD-01R X20 before source access` | If unattainable, keep empirical HOLD or consider a lawfully distinct source; if attested, enable only separately approved scoped feasibility inspection |
| **P1_HIGH: G1_SOURCE_CONSTRUCT** | `NOT_VALIDATED` | Candidate sampling frame fixed prospectively; typed entity/location/time, authority, bounded time closure, witness/negation/exclusivity; all candidate/eligible/reject/abstain denominators and reasons, nonzero coverage with prereg threshold; `E1 F-H01 X14 X17 X19` | Construct feasible with honest coverage -> measurement remains candidate; systemic insufficiency -> HOLD/SIMPLIFY/PIVOT under new Q4, not post-hoc filtering |
| **P1_HIGH: G2_FULL_EFFECTIVE_PARITY** | `NOT_CAPTURED` | All label-changing material support/refutation/exclusivity facts preserved in both model-effective and rater-effective payloads after renderer/tokenizer/window/truncation; separate hidden key/oracle custody; exact byte provenance; `E2 X13 X15` | Parity established -> model-vs-rater agreement interpretable; parity violation -> item REJECT and measurement admission HOLD, not UNKNOWN |
| **P1_HIGH: G3_GOLD_RATER** | `NOT_CALIBRATED` | Independent source-grounded hidden gold derivation, blind same-task calibration and disagreements/adjudication, no shared ontology error, correct custody and permitted rater use; `E4 M1 M4 X18` | Validated gold -> semantic adherence distinguishable from evaluator failure; shared error -> benchmark HOLD |
| **P1_INTEGRATED_FREEZE: G4_PROSPECTIVE_PREREG_COST** | `NOT_FROZEN` | Question/endpoint, unit and n with uncertainty/power; candidate/eligible/reject/abstain coverage; exact REJECT precedence preserving all reasons; threshold, STOP, budget and owner role frozen before outcomes; `E5 AD-07 F-H01 X21` | GO/HOLD/STOP becomes auditable under frozen decision threshold; unknown costs cannot justify quantitative promise |
| **P2_CONDITIONAL_ONLY: G5_CAUSAL_CONTRASTS** | `NOT_EXECUTED` | Prospectively matched/group-disjoint fact-only vs cue-only contrasts with balanced lexical/position/length and prereg AD-06, only if causal shortcut attribution is desired; `E3 M3 F-M04 for causal claims ONLY` | Distinguish genuine fact sensitivity from cue shortcut; without contrast avoid causal claim |

**G0 rights before every inspection.** Rights attestation itself is not scientific evidence. It allows only what the owner and rights scope explicitly authorize. If G0 fails, do not try to 'fix' rights by synthetic/pseudo-licenses, or infer that the measurement itself is mathematically impossible.

**G1/F-H01:** report candidate denominator **and** eligible/reject/abstain counts, all reasons, coverage and confidence under prereg. Score only eligible items but never conceal rejected populations. `FALSE` requires visible negation or applicable exclusivity; `UNKNOWN_VALID` requires bounded/temporally complete source. `X21`: freeze deterministic primary REJECT reason priority while preserving every reason.

**G2/X13/X15:** source oracle facts hidden from model/rater must not silently change label; compare whole label-changing material-fact sets after tokenizer/context trimming, not merely 'shared positive witness'. Missing decisive fact → HOLD gate/item REJECT, not an epistemic UNKNOWN.

**G3/X18:** two raters agreeing can both be wrong. Use blind same-task independently source-grounded truth and rights-compliant roles.

**G4:** freeze eligibility rules, sample unit, endpoint/threshold/uncertainty, STOP and real budget before any outcomes. No retrospective tailoring of N, coverage denominator or cost assumptions.

**G5/E3:** shortcut contrast is necessary for **causal attribution** only; it is not a reason to block a paper-only evidence matrix. E6 checkpoint/runner custody is a distinct **execution** veto.

## 4. Candidate next directions — separate evidence prerequisites from research options

| Rank | Direction | Lineage and what is already known | Decision-changing evidence / dependencies | Disposition |
|---|---|---|---|---|
| **1 · P1_CONDITIONAL_OWNER_CHOICE** | **ONE_INTEGRATED_RIGHTS_FIRST_MEASUREMENT_FEASIBILITY_QUESTION** | L0011, L0012, L0015, L0022, L0026; `DESIGN_Q1_TO_Q4_CLOSED_HOLD_NEW_ACCESS_NOT_AUTHORIZED` | Establishes whether a valid score can ever support comparing model/data/objective/decoder; needs G0_RIGHTS, G1_SOURCE_CONSTRUCT, G2_FULL_EFFECTIVE_PARITY, G3_GOLD_RATER, G4_PROSPECTIVE_PREREG_COST | `PROPOSED_NOT_REGISTERED` |
| **2 · P2_AFTER_VALID_MEASUREMENT** | **DATA_VS_OBJECTIVE_EQUAL_INFORMATION_AND_COMPUTE_BUDGET** | L0011, L0015, L0016, L0025, L0026; `H_DATA_S1_NO_DEMONSTRATED_SCOPED_SEMANTIC_BENEFIT_NO_FRESH_PERMISSION` | GO data-focused or objective-focused revision, or HOLD causal attribution; needs G0_RIGHTS, G1_SOURCE_CONSTRUCT, G2_FULL_EFFECTIVE_PARITY, G3_GOLD_RATER, G4_PROSPECTIVE_PREREG_COST | `NOT_OPENED` |
| **3 · P2_AFTER_VALID_MEASUREMENT** | **DECODER_CONTEXT_CAPACITY_CONTROLLED_CAUSAL_DIAGNOSTIC** | L0011, L0012, L0015, L0026; `NO_CAUSAL_LOCALIZATION_NOT_AUTHORIZED` | Evidence for simpler decoder/context interventions before architecture scaling; needs G1_SOURCE_CONSTRUCT, G2_FULL_EFFECTIVE_PARITY, G3_GOLD_RATER, G4_PROSPECTIVE_PREREG_COST | `NOT_OPENED` |
| **4 · P3_INDEPENDENT_ENGINEERING** | **T5_T6_CPU_PARITY_AND_INFERENCE_BASELINE** | L0013, L0014, L0027, L0029; `L0013_FAIL_32_OF_32_L0014_PASS_4_OF_4_SCOPED_T6_TECH_MERGED` | GO/HOLD deployment or runtime baseline only, not Q001 measurement; needs independent technical QA and owner scope | `NOT_OPENED` |
| **5 · P3_SEPARATE_QUESTION_ONLY** | **EMBEDDINGGEMMA_VECTOR_MEMORY_INFORMATION_PATH** | L0023, L0024, L0029; `OOD256_PASS_SCOPED_TRANSPORT_VM_MARKER_SHORTCUT_FAIL_R8_HOLD` | Whether memory/vector pathway adds task semantics rather than geometric transport; needs G0_RIGHTS, G1_SOURCE_CONSTRUCT, G2_FULL_EFFECTIVE_PARITY, G3_GOLD_RATER | `NOT_OPENED` |
| **6 · P3_ARCHIVE_AND_REASSESS_ONLY** | **D1_BRIDGE_ACTION_CAUSAL_TASK_ONTOLOGY_REDESIGN** | L0016, L0017, L0018, L0019, L0020, L0021, L0022; `R1_DESIGN_CLOSED_HOLD_ONTOLOGY_FEASIBILITY` | Potential separately registered action-causal research question if construct can be shown valid; needs G0_RIGHTS, G1_SOURCE_CONSTRUCT, G3_GOLD_RATER | `NOT_OPENED` |

**Not a declaration that all six directions should execute:** after the Q4 CLOSED_HOLD, exactly zero active Question Gate and zero authorized research branch remain. Alternatives rank by **decision relevance to Small4M semantics**; T5/T6 has potentially better engineering readiness but answers a *different*, narrower question. The 2026-11-14 old priority matrix ranked T5/Embedding P1 for branch review/engineering; no contradiction with putting them P3 here for **semantic science cause attribution**. The two taxonomies use different decision objectives.

## 5. Single integrated successor candidate (not registered)

**Suggested candidate QuestionID (placeholder only, not reserved):** `TTM-P0B-MEAS-FEASIBILITY-PROPOSED` · `TYPE=MEASUREMENT`.

**One falsifiable question:** *Does at least one lawfully accessible, prospectively sampled family of typed and temporally bounded `LOCATED_AT` assertions permit a defensible eligible/reject denominator, valid source-grounded independent gold, and full label-changing material-fact parity between effective model and rater views, under a previously frozen cost/uncertainty ceiling?*

This is **feasibility of a valid measurement** — not 'Does Small4M understand locations?' or a permit to generate data/run model. Relevance: `YES` would justify owner consideration of a later **separate** model-scoring science Question Gate; `NO` with lawful source evidence would support scoped SIMPLIFY/PIVOT/HOLD/STOP adjudication. `NO_ACCESS` or `UNVERIFIED` remains evidence HOLD, not scientific impossibility. Declare scope, sampled population, threshold, temporal domain, units, STOP, rights and budget before any prospective source manipulation; do **not** invent numeric criteria now.

**Single-packet dependency ordering — no micro-permits:** (i) owner first approves/records one Q1 Question Gate, then lawful AD-01R rights attested *before data access*, with immediate stop if absent; (ii) only if explicitly authorized, perform one bounded prospective source/ontology/candidate-denominator feasibility check; (iii) within that authorized packet, check material-fact effective parity and independent blind gold/rater; (iv) independent evidence/admission review and owner Q4 disposition. No current step performs (i)–(iv). An alternative **ENGINEERING** Question Gate for T5/T6 is possible only by distinct owner selection, not automatically layered on top.

## 6. Recommended next owner decision (proposal, not action)

`RECOMMEND_OWNER_SELECT_ONE_NEXT_MEASUREMENT_FEASIBILITY_QUESTION_DESIGN_ONLY`; avoid `GO_SCIENCE`, generic architecture pivot, or reopening CLOSED Q001.

**Decision boundary:** owner must explicitly choose either (a) register one new proposed measurement Question Gate later with lawful rights/feasibility STOP design, (b) choose a different specific evidence-backed engineering question (e.g. T5/T6 parity), or (c) maintain `NO_ACTIVE_QUESTION`. This priority matrix grants **none** of those.

**Falsifier for this ranking:** If credible rights and ontology/parity/gold source evidence for a different candidate question is shown to be more ready and more causally discriminating than current Q001 descendants, re-evaluate ranking with pinned new inputs, not by silently promoting old branch PASS. If access rights can never be attested within the owner's constraints, a lawful alternate construct becomes higher-value than endlessly restating HOLD.

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

No model run, no source access, no checkpoint/scorer/rights assertion, no new science eligibility, no new QuestionID, no change to `ACTIVE_RESEARCH_GATE.md`. **Author source QA does not equal independent review**. Any reviewer must assess the exact immutable governance proposal HEAD, cross-check scientific lineage and challenge the priority ordering and successor feasibility question.

**Proposed next single action:** `TTM_POST_P0A_Q001_DISTINCT_PRIORITY_MATRIX_SOURCE_REVIEW_AND_OWNER_ONE_NEXT_QUESTION_SELECTION_SINGLE_GATE` — one independent read-only adversarial priority review, then owner selects a **single** next Question Gate design/HOLD direction (no automatic new branch, permit or implementation). Governance merge only after distinct source QA and explicit owner approval.
