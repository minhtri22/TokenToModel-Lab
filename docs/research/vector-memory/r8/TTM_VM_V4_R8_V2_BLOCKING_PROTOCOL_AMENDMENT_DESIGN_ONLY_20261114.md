# TTM VM V4 R8 — PROSPECTIVE PROTOCOL AMENDMENT V2 (DESIGN_ONLY)
**Operation:** `TTM_VM_V4_R8_V2_BLOCKING_PROTOCOL_AMENDMENT_AND_FROZEN_INDEPENDENT_REVIEW_READBACK_NO_GENERATION`
**As of:** 2026-11-14  
**Classification:** `PROPOSED_NOT_OWNER_ADOPTED` · `NO_GENERATION` · `NO_SCIENCE`  
**Parent protocol:** `c62d0d5fa9d8b87c2d508b36f0942a3fff3fce69`  
**Independent AI review:** uploaded 2026-11-14, original SHA256 `cad0409a5d7e98c5e661ec2e2e3c83f0cee7ff617f7d282b89132ae853d0fbf0`, self-attested separate AI review, decision `HOLD_R8_PROTOCOL_AMENDMENT_REQUIRED_NO_GENERATION`. Six HIGH findings B01–B06. Reviewer NOT asked to review V2 yet.

## Scope, estimand and hypothesis
R7 exposed deterministic lexical leakage (`applicable signed record`: action 64/64, target 32/32). The original V4 P0–P3 vs N0–N3 strata encode the action class. R8 is NOT an in-place fix or direct replication of those strata. **New exploratory estimand:** conditional target-selection / abstention accuracy under balanced evidence-relation families with matched truth-conditional counterfactuals, at specified 32-card index and blind delivery. Report action, conditional target choice, joint accuracy, and per-family results separately. Do not make generalization or naturalistic claims. Preserve historic estimand and R5/R6/R7 artifacts unchanged.
R8 remains non-executed until independent V2 design review PASS (G0), owner adoption and source rights PASS (G1), private custody and validator PASS (G2).

## B01 — Formal gold/proof/abstain ontology
**Private case schema** (proposal to be versioned by owner):
```json
{
  "case_id":"opaque", "relation_family":"F01..F08", "pair_id":"private",
  "event_graph_cluster":"private", "template_cluster":"private",
  "fold_id":"private", "question_text":"string",
  "cards":[{"key":"opaque","text":"string","source_id":"opaque"}],
  "gold_action":"SELECT|ABSTAIN", "target_card_id":"opaque|null",
  "supported_target_ids":["opaque"], "proof_card_ids":["opaque"],
  "premises":[{"id":"p1","claim":"...","support_card_ids":["opaque"]}],
  "authority_order":[{"higher":"authority_A","lower":"authority_B","evidence_card_ids":[]}],
  "temporal_order":[{"earlier":"event_A","later":"event_B","evidence_card_ids":[]}],
  "abstain_reason":"NONE|NO_SUPPORTED_TARGET|MULTIPLE_SUPPORTED_TARGETS|UNRESOLVED_AUTHORITY|MISSING_PREMISE",
  "truth_conditional_edit":{"premise_id":"...","before":"...","after":"..."}
}
```
A **target card** is the card identifying the answer entity/record demanded by the question; a **proof card** is any card necessary to establish its validity, possibly distinct from target. Evaluate a candidate target by conjunction of source scope, identity, event relation, effective time, and authoritative provenance. A card's self-asserted status is insufficient without corroborating needed premises. `SELECT` iff the resulting set of **uniquely proven targets has cardinality 1**; otherwise `ABSTAIN`. No target => `NO_SUPPORTED_TARGET`; two or more tied supported => `MULTIPLE_SUPPORTED_TARGETS`; unresolved policy precedence => `UNRESOLVED_AUTHORITY`; a specified necessary premise absent => `MISSING_PREMISE`. Distinguish conflicting authority vs absent evidence. Validate every reason by proof review; unsupported target keys are never guessed.
**Important conflict:** one-key selection cannot honestly score cases where proof necessarily spans multiple cards unless evaluator supports the target-vs-proof distinction. G2 validator adaptation required before generation, not just documentation.
**F07 feasibility:** construct one paired hypothesis at design level: an accession receipt lacks requisite receiving signature (ABSTAIN), contrasted with evidence of completed authorized receipt from an independently verified ledger (SELECT). Same question text; proof changes, not an arbitrary `signed` token. If valid controls cannot be constructed without lexical oracle, F07 remains HOLD and matrix must be respecified *prospectively*, before G3.
**No case data authored by this amendment.**

## B02 — Paired question-only tautology
For identical question text across exactly one SELECT and one ABSTAIN, any deterministic question-only model that predicts the same action for both achieves exactly 32/64. Therefore this **MUST NOT** be a PASS criterion. Keep it as a schema sanity check only. Test **question+metadata**, wording-variant question-only (non-identical paraphrases precommitted at design time), and template/cluster-held-out generalization; inspect label dependence from question length, punctuation, entity roles and lexical signatures. Control variants must not become post-outcome edits. No inference of no-leakage from near chance.

## B03 — Units, folds, and blinding
64 cases = 32 counterfactual pairs, **not** 64 independent observations. Eight relation families may be fewer independent superclusters. Freeze private table before generation:
`pair_id,event_graph_cluster,template_cluster,relation_family,fold_id,blind_delivery_group`.
- Each counterfactual pair and all records sharing an event-graph or template cluster must be in **one fold**. Compute connected components of a graph connecting shared pair/graph/template before fold allocation. Reject any component that crosses specified folds.
- At design lock choose deterministic cluster-fold algorithm using seed `20261114` for *future protocol bookkeeping only*; fold count is conditional on component count. If <4 independent components, no CV inference; HOLD and report raw diagnostics. Do not assign twins separately to reach desired folds.
- Primary diagnostic: leave-template-cluster-out with group-held-out model fits; secondary: leave-family-out, testing cross-family transfer and not the primary within-family estimand. They estimate different properties.
- Cross-validation units/CI: pair or graph/template component, never cases as iid. Give per-family denominators, cluster bootstrap or randomization CI with cluster as resampling unit, conditional on adequate independent components. With eight clusters report descriptive results and uncertainty; lack of power => HOLD.
- Blind delivery: `pair_id`, family/stratum, alternate twin and gold are private; separate twins in presentation and allocation without revealing pair structure, avoid giving same human/AI rater both twins when possible. A/B routing, order, hash/pins must be independently frozen before scoring; no unblinding until A/B scores frozen.

## B04 — Frozen anti-shortcut adversary suite
**Restricted, predeclared negative-control classes**, not all possible algorithms:
1. case-order only; public key and ID lexical ordering;
2. ID/source_id/token length/line length and card-count metadata only;
3. status-marker, signature/authority keywords, source-format regex and n-gram presence only;
4. question-only (incl paraphrase and template fingerprint), and question+metadata;
5. card-level marker selector **target-key** independent of question semantics;
6. joint action + key choice from these features;
7. TF-IDF and BM25 lexical retrieval as descriptive comparators;
8. combinations of metadata, marker and basic lexical features fit **only within training clusters**, judged on held-out clusters.
Freeze feature allowlist, transforms, estimator/hyperparameters, maximum search budget and training procedure before generating data; not claiming global absence of memorization. A deterministic rule explaining all held-out actions or targets => hard FAIL. Action null for balanced random guessing `p=0.5`; target-key uniform null on SELECT `p=1/32`; joint correct SELECT+key and ABSTAIN null requires an explicitly specified strategy, not wrongly assumed 1/64. Report action sensitivity, specificity, gold top-1 and joint exact match independently. A card's presence of a status token is permitted only if not a direct oracle to target/action; correctness must require intended relation.
The historic `applicable signed record` exact-marker test is a **must-run known-failure regression**, but passing it alone never means anti-shortcut PASS.

## B05 — Proposed statistical and acceptance contract
Primary **hard technical** gates (not statistics): source lineage/rights, 64x32 counts, gold semantics, no gold/paired metadata in public schema, consistent pair/cluster folds, no deterministic shortcut from **predeclared oracle suite** on held-out clusters. Any hard violation => FAIL.
Secondary statistical diagnostics (cannot certify no leakage): raw and balanced accuracy for action; SELECT top-1 key vs 1/32; joint exact match; per-family outcomes; null-permutation reference distributions **at pair/cluster level**. For paired action sign-flip tests, swap labels of the two members together preserving pair structure only when exchangeability assumptions hold. For target-key randomization, permute candidate keys within each case under the null while maintaining clusters. Precommit a two-sided 0.05 familywise error budget using Holm on the four primary shortcut statistical families: (a) question+metadata (b) marker-only (c) metadata-only (d) combined cheap-feature selector; use exact/randomization p values if feasible, report actual permutation count/seed and Monte Carlo resolution. 95% interval from cluster bootstrap where valid; if insufficient clusters, mark CI as inconclusive and HOLD. **Exploratory signal** `abs(accuracy-0.5) >= 0.125` is NOT an acceptance threshold or proof of integrity.
**Tri-state adjudication**:
- `FAIL`: deterministic held-out oracle in fixed suite or hard schema/semantics/custody error; or statistically significant shortcut after Holm when test is valid;
- `HOLD`: insufficient independent clusters, invalid null/exchangeability, wide uncertainty, incomplete tests or unresolved semantic review;
- `PASS_SCOPED_DIAGNOSTICS`: all hard checks passed and negative controls completed, none show predeclared evidence of leakage and tests have adequate sensitivity according to a **precommitted power/sensitivity plan reviewed before G3**. Even this is not proof of no leakage and not science release. The reviewer must approve power/sensitivity definition; current V2 does not assert it has been calibrated. If no achievable power/sensitivity specification with N=32 pairs, G0 must HOLD or scope be explicitly downgraded to descriptive.
Tests are frozen once, with no adaptive threshold, seed shopping, repeated candidate generation, or flipped outcomes to improve apparent PASS. Mock/no-R8 sanity checks may be performed before G3 and recorded separately.

## B06 — Prospective AI source rights & private custody
Only class proposed: `AI_AUTHORED_SYNTHETIC_EXPLORATORY_ONLY`. Not naturalistic and not a substitute for `OWNER_AUTHORED_NATURALISTIC`. No claim license/rights or PII certificate has been signed.
**Owner decision form (blank, NEVER auto-sign):**
```
{
 "protocol_version":"ttm.vm.v4.r8.proposed.v2",
 "owner_decision":"PENDING",
 "owner_identity_attested":false,
 "owner_approval_record_uri":null,
 "allowed_source_kind":"AI_AUTHORED_SYNTHETIC_EXPLORATORY_ONLY",
 "purpose":"EXPLORATORY_ONLY",
 "pii_review_attested":false,
 "rights_review_attested":false,
 "private_custodian":null,
 "private_storage_uri":null,
 "private_access_policy":null,
 "custody_readback_receipt_uri":null,
 "validator_support_receipt_uri":null
}
```
**Custody rule:** private dataset/gold never pushed into public GitHub. Custodian stores exact encrypted/private bytes in a controlled location, records SHA256, ownership, access restrictions, readback and hash; owner must approve scope and retention. Public GitHub may carry only non-sensitive evidence, manifests and SHA commitments that do not expose answer patterns. For low-entropy candidate content, use e.g. SHA256(`nonce || full_package_bytes`) with a random secret ≥128-bit nonce held in private custodian, recorded with the full packet. A bare hash in public GitHub is not storage proof.
**Immutable source-lock** before G3: commit SHA protocol, exact validator code SHA, generator code SHA, schema, fixed folds and allocation, source-rights receipts and private-store policy, one-shot seed/PRNG version. Source-lock verification must be reproducible and independent of generator. No silent copy of R7 known-failed fixtures.

## Formal gates (NOT approved by this draft)
| Gate | Required artifact / authority | Current |
|---|---|---|
| G0 | Independent review V2 resolves B01–B06, including feasible semantics and power/QA rule | `HOLD_REVIEW_NOT_EXECUTED` |
| G1 | Owner-approved prospective amendment and source rights+PII receipt | `HOLD_NOT_ATTESTED` |
| G2 | Private custodian byte readback, access-control and locked validator/source inputs | `HOLD_NOT_EXECUTED` |
| G3 | One-shot R8 generation only after G0–G2 | `NOT_AUTHORIZED_NOT_GENERATED` |
| G4 | Distinct independent semantic/shortcut QA on R8 candidate | `NOT_EXECUTED` |
| G5 | A/B blind CAL | `SEALED` |
| G6 | CAL threshold freeze, PROBE256 etc | `SEALED` |

**One-packet adjudication:** `HOLD_R8_V2_UNREVIEWED_OWNER_RIGHTS_CUSTODY_NO_GENERATION`. No R8 source, no mock presented as science, no blind packet, no TEST, Reader, GPU, PROBE. G0 design review completion does not substitute for G1 or G2.

## Reviewer handoff after freeze
Reviewer must judge: schema ontology supports independent proof validation; F07 SELECT feasible; paired-family estimand correctly delimited; fold clusters and blinded delivery prevent twin leakage; frozen restricted oracle suite and nulls are statistically coherent; source rights and custody assertions do not exceed evidence; whether power/sensitivity plan is sufficient at 32 pairs. Return B01–B06 PASS/HOLD/FAIL, global verdict, no data generation. No revision of prior frozen review.
