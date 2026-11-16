# TTM POST-P0A Q001 — Distinct AI Source Review of Priority Matrix

**Date:** 2026-11-16  
**Operation:** `TTM_POST_P0A_Q001_DISTINCT_PRIORITY_MATRIX_SOURCE_REVIEW_AND_OWNER_ONE_NEXT_QUESTION_SELECTION_SINGLE_GATE`  
**Repository:** `minhtri22/TokenToModel-Lab`  
**Reviewed exact candidate HEAD:** `cef770d386c2e6862dc33e0f6e7d4e1866f7c00b`  
**Frozen main reviewed:** `f6d7d304ef79f889dc24f7282ef6e2aceebf44af`  
**PR:** https://github.com/minhtri22/TokenToModel-Lab/pull/26 (OPEN, DRAFT, UNMERGED at review)  
**Verdict:** **`HOLD_POST_P0A_EVIDENCE_PRIORITY`**  
**Scope:** source/design-only, read-only Github review. This is a distinct AI critical review of authored source, **not** human or organizational independence attestation, and not empirical or legal validation.

## 1. Source-custody checks

- Verified exact candidate commit and PR #26 head both equal `cef770d386c2e6862dc33e0f6e7d4e1866f7c00b`; PR base and observed `main` equal `f6d7d304ef79f889dc24f7282ef6e2aceebf44af`.
- `compare_commits` main...candidate: `ahead_by=4`, `behind_by=0`, four **added** governance-only files, no changed/deleted implementation files; `lineage.md` unchanged.
- Seven source manifest Git blob SHA-1 entries were checked directly at the frozen main and match:

| Source path | Verified Git blob SHA-1 |
|---|---|
| `lineage.md` | `3409e036241deb1da6674619a2abc834bea8a2d6` |
| `docs/governance/ACTIVE_RESEARCH_GATE.md` | `3d66a78fee3fa2ad5f8cdd3ca3117f67bf72dd01` |
| `docs/governance/ttm-post-q001/TTM_P0A_MEAS_Q001_Q4_OWNER_CLOSED_HOLD_GOVERNANCE_CLOSURE_20261116.md` | `bb21cf560c91a083680e072adb7d5ce5a5508d11` |
| `docs/governance/TTM_QUESTION_FIRST_RESEARCH_ARCHITECTURE_LINEAGE_AND_MAIN_POLICY_20261115.md` | `af1a879a2552f100c6669cb9ab6dc98c930d2e19` |
| `docs/governance/TTM_GLOBAL_BRANCH_EVIDENCE_QA_AND_RESEARCH_PRIORITY_20261114.md` | `09a9f9c5003d0e8d899151f7f426707eb1505d44` |
| `artifacts/governance/ttm-post-q001/TTM_P0A_MEAS_Q001_Q3_EVIDENCE_SUFFICIENCY_MATRIX_20261116.json` | `674ef299cc4b6fb8dea6e35d47a96cea49e3cdbe` |
| `artifacts/governance/ttm-post-q001/TTM_P0A_MEAS_Q001_Q4_ALTERNATIVES_DECISION_MATRIX_20261116.json` | `2a4f9acd511b21ce22e922ff1fa3c370928a03a9` |

- Proposal artifacts inspected: evidence report Git blob `effdf66ed93405524d92b55504b919dabfcf5348`; matrix JSON `a62b7c7add8071c122bdacd7b242171d20d9ebe0`; Author QA JSON `47517a14acfd2e575643762f39ea8d719ddea158`; handoff Markdown `f0c52fef5a4c8a2eb7b3cc50e9ecfd41d82407b5`.
- Author QA claims 35/35 scoped static PASS. That is an **author receipt**, not independent QA. No PR reviews were present at time of readback.

## 2. Method and what passes source-level challenge

Methods: (a) non-compensatory hard-veto / construct validity, (b) falsifiability and decision relevance, (c) qualitative FMEA, (d) comparative value-of-information / sensitivity reasoning **without invented numeric utilities or probabilities**, (e) policy state-machine consistency.

- **PASS SOURCE DESCRIPTION:** L0011 VAL T4 NLL vs bigram scoped confirmatory PASS; L0012 64-story once-consumed TEST descriptive PASS (not independent token-level recompute). Neither demonstrates semantic adherence.
- **PASS SOURCE DESCRIPTION:** L0015 FRESH16 V2 H1=0/16 H2=0/8 scoped semantic FAIL; distinct from NLL PASS. L0013 32/32 strict-logit parity FAIL is preserved; L0014 GELU_ERF 4/4 strict held-out parity PASS is narrow, not universal.
- **PASS SOURCE DESCRIPTION:** L0022 ontology HOLD, L0023 VM retrieval and marker shortcut issues/R8 HOLD, L0024 EmbeddingGemma OOD256 residual-transport scoped PASS, L0025 H-DATA no demonstrated scoped semantic benefit, L0026 FINAL24 negative, L0027 technical T6 merged with P07 paused, and L0028/29 dated branch snapshots are not generalized science authorization.
- **PASS CONCEPTUAL PRINCIPLE:** AD-01R rights/PII/source permission is non-compensatory before **any** source access; source-rights attestation is not science evidence. Construct/denominator, complete post-tokenizer material-fact parity, independent source-correct gold/rater, prospectively locked endpoints and STOP are different necessary controls. E3 applies to causal shortcut attribution; E6 to model execution.
- **PASS QUALITATIVE PRIORITIZATION PREMISE:** Measurement validity can have high cross-hypothesis value for *semantic attribution*, while engineering T5/T6 can rank higher under a *technical reproducibility/deployment* objective. Existing source does not support numeric VOI, sample N, cost, effect size or a universal total order.

## 3. Adversarial findings

### F01 — BLOCKER — proposed successor duplicates the CLOSED_HOLD Q001 decision construct

The original registered `TTM-P0A-MEAS-Q001` Q1 explicitly asks whether a valid `LOCATED_AT(entity,location,reference_time)` TRUE/FALSE/UNKNOWN measurement with ontology/witness/full effective-view parity and advance decision criteria can be established. Its Q4 has **closed** at `CLOSED_HOLD_EVIDENCE_INSUFFICIENT`; the main active registry says `NONE_ACTIVE`. Proposed `TTM-P0B-MEAS-FEASIBILITY-PROPOSED` asks whether there exists at least one lawful prospective `LOCATED_AT` family with those same requirements. The addition of "lawful prospective source" is a stronger empirical-evidence demand but has not yet established a new independently discriminating decision or new lawful source. Without a clear delta/new evidence, re-registering it is materially at risk of reopening Q001 by renaming it.

**Required resolution:** preserve Q001 CLOSED_HOLD. Before choosing a new gate, supply exact source-custodied **new external lawful evidence** (e.g., a rights attestation or a distinct verified source family not used by Q001), or reformulate the new question around a **separate falsifiable decision** that the old Q001 did not ask. Explicitly distinguish *planning/rights discovery* from *new empirical measurement*. Absent such evidence, maintain `NO_ACTIVE_QUESTION` or choose a genuinely distinct engineering question.

### F02 — BLOCKER — Q4/I1–I4 policy ordering is inverted/ambiguous

Report §5 proposes (i) owner registers Q1, (ii) source/ontology/denominator feasibility inspection, (iii) effective-view parity plus blind gold/rater, then (iv) independent admission review and **owner Q4** disposition. Main Question-First policy §3 establishes Q1→Q2→Q3→**Q4 owner decision**→I1 branch→I2 execution/evidence→I3 independent adjudication→I4 closure/merge. Its Q1–Q3 stage is source/design only, with no new data/gold creation. A conceptual rights attestation can be assessed before source access, but source inspection/fixture construction and blind gold derivation cannot silently be performed as ordinary Q2/Q3 paper work or before scoped implementation permission.

**Required resolution:** articulate the two stage boundaries explicitly: Q1–Q3 source-only design; Q4 can only decide `GO_SCOPED_IMPLEMENT` for one lawful and constrained feasibility implementation; only afterward, if expressly authorized and rights-attested, I1/I2 may inspect authorized sources and create prereg fixtures/gold; I3 distinct adjudication; I4 evidence-only closure or approved merge. Maintain separate science/inference permission and never reuse sealed TEST/FINAL. Do not label source-inspection result as Q4 evidence from the same pre-implementation Q1–Q3.

### F03 — MAJOR — executable dependency matrix has holes

In machine-readable options, D3 (`DECODER_CONTEXT_CAPACITY_CONTROLLED_CAUSAL_DIAGNOSTIC`) lists `G1..G4` but omits `G0_RIGHTS`, despite declaring G0 mandatory before any source inspection. D4 (`T5_T6_CPU_PARITY_AND_INFERENCE_BASELINE`) lists `required=[]`, whereas its own suggested proof demands executable/model/GGUF custody, rights, technical QA and a separately authorized scoped owner decision. Likewise, other model-running options need E6/AD-00/AD-01C before execution; G5 causal guards are conditional to the causal claim and appropriate contrasts.

**Required resolution:** distinguish three explicit machine-readable categories: `source_access_prerequisites`, `measurement_validity_prerequisites`, `execution_prerequisites`. Add `G0_RIGHTS` to D3 if it uses real external source; add E6/AD-00/AD-01C and owner scope for any model-involving option; distinguish technical-only synthetic fixtures that avoid private T4 checkpoint from T4-trained model claims. `required=[]` may be valid only as *no semantic measurement prerequisite*, not as no gate at all.

### F04 — MAJOR — single-family existential feasibility and sampling selection

An endpoint of "at least one lawful family" with nonzero eligible coverage risks convenience selection. The report rightly insists on candidate/eligible/reject/abstain denominators and prospective thresholds, but does not distinguish an exploratory source-discovery phase from an untouched confirmatory family/sampling frame. Inspection of multiple families followed by selection of an easy family would bias the eligibility claim unless all candidate families, inspection counts and exclusion reasons are reported.

**Required resolution:** prospectively declare the source-family search universe, sampling unit, family-selection algorithm, which stage is exploratory vs confirmation, exact candidate/eligible/reject/abstain denominator and all reasons, minimum credible coverage threshold/uncertainty and STOP/resource ceiling **before observing decision-relevant outcomes**. Rights-only external attestations may arrive first without being treated as scored outcomes. Unknown N/cost can remain `UNKNOWN` in this source-only proposal, but no feasibility PASS before they are frozen.

### F05 — MINOR — broken relative Markdown link in handoff

The first report hyperlink inside the handoff points to `docs/governance/ttm-post-q001/...` relative to an already nested `docs/governance/ttm-post-q001/` folder. Change it to `TTM_POST_P0A_Q001_EVIDENCE_GAPS_AND_NEXT_QUESTION_PRIORITY_MATRIX_20261116.md` or an immutable GitHub URL; no scientific effect.

## 4. Decision sensitivity / what can change the ranking

- **Current objective: identify why Small4M has scoped NLL PASS and semantic adherence FAIL.** Rank measurement/construct validity **first as a missing capability**, not first as an approved new research gate. No verified probability, sample size, legal rights, NLL→semantics causal bridge, or performance ROI is available.
- **If a new written rights attestation plus correctly bounded source family and independently checked full parity/gold become available:** a truly distinct, prospectively specified measurement feasibility question may take first place, conditioned on F01/F02 remediation and owner approval.
- **If rights cannot be attested within constraints:** do not repeat paper feasibility gates. Give a distinct lawfully available construct/source higher consideration, or maintain NO_ACTIVE_QUESTION for semantic science.
- **If the owner's actual immediate objective is technical deployability and legally usable synthetic fixtures/executables are available:** a distinct T5/T6 strict CPU parity technical Question Gate may rank first **for engineering**, independently of unresolved Small4M semantic questions. It requires independent technical QA and rights/checkpoint custody where applicable; does not imply semantic science GO.
- **If a valid source-independent blind semantic benchmark is presented with stronger provenance than the current one:** re-rank data/objective or decoder/context controls using fresh, disjoint evidence and equal information/compute budgets; do not resurrect once-consumed TEST/FINAL24.
- **If VM/Embedding demonstrates independently scored semantic improvements under matched information budgets, no marker leakage, lawful source access and valid gold:** it can displace lower-ranked options; OOD256 residual transport alone is insufficient.

## 5. Adjudication and owner boundary

**Single verdict:** `HOLD_POST_P0A_EVIDENCE_PRIORITY` at exact candidate `cef770d386c2e6862dc33e0f6e7d4e1866f7c00b`.

**Preserve:** 7/7 verified source pins, four-file governance-only diff, main/lineage unchanged, scientific results bounded as recorded, Q4 `CLOSED_HOLD_EVIDENCE_INSUFFICIENT`, `NO_ACTIVE_QUESTION`, `SCIENCE_HOLD`, PR #26 DRAFT and UNMERGED.

**Do not infer:** existing model rights, independent human signoff, source feasibility, validated gold, new prereg, science GO, permit to create dataset/runner or merge approval. The author's 35/35 static QA is not this review.

**One next operation:** `TTM_POST_P0A_Q001_PRIORITY_MATRIX_F01_F04_INTEGRATED_SOURCE_REMEDIATION_AND_EXACT_HEAD_DISTINCT_READBACK_SINGLE_GATE` — one governance-only integrated revision, resolving F01–F04 and link F05, then exact-head distinct review; **no micro-permits and no new Question Gate**. Only after a PASS should the owner select exactly one of (A) genuinely distinct future measurement question conditioned on *new evidence*, (B) genuinely distinct engineering question, or (C) `NO_ACTIVE_QUESTION`. Owner choice and governance merge are separate express approvals.

**This report is delivered as a local review artifact, not posted to GitHub and not an independent organization-issued certification.**

## 6. Links

- Exact candidate: https://github.com/minhtri22/TokenToModel-Lab/commit/cef770d386c2e6862dc33e0f6e7d4e1866f7c00b
- Draft PR #26: https://github.com/minhtri22/TokenToModel-Lab/pull/26
- Original registered Q001 question: https://github.com/minhtri22/TokenToModel-Lab/blob/f6d7d304ef79f889dc24f7282ef6e2aceebf44af/docs/governance/ttm-post-q001/TTM_P0A_MEAS_Q001_REGISTERED_QUESTION_GATE_20261115.md
- Current governance policy: https://github.com/minhtri22/TokenToModel-Lab/blob/f6d7d304ef79f889dc24f7282ef6e2aceebf44af/docs/governance/TTM_QUESTION_FIRST_RESEARCH_ARCHITECTURE_LINEAGE_AND_MAIN_POLICY_20261115.md
- Q4 closure: https://github.com/minhtri22/TokenToModel-Lab/blob/f6d7d304ef79f889dc24f7282ef6e2aceebf44af/docs/governance/ttm-post-q001/TTM_P0A_MEAS_Q001_Q4_OWNER_CLOSED_HOLD_GOVERNANCE_CLOSURE_20261116.md
