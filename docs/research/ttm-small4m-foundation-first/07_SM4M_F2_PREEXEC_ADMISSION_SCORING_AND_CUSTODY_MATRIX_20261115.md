# TTM-Small-4M — F2 Pre-execution Admission, Deterministic Scoring & Custody · IR01–IR07

**Operation:** `TTM_SMALL4M_F2_PREEXEC_INTEGRATED_DESIGN_REMEDIATION_IR01_IR07_SINGLE_GATE`  
**Source:** 06 F2 protocol of same remediation candidate; MD1 original `33021a421f05bb3bfa0999ad12bc3bd144366da9`; owner design closure `c233dff20b9b020aefd732ce62bfa2e7aebd3985`.  
**State:** `AUTHOR_CONTRACT_ONLY · EXECUTION_PREEXEC_BLOCK=TRUE · NO_GOLD · NO_SCORE · NO_MODEL`. Requirements for post-data evidence are **not prerequisites to authorizing data creation**.

## 1. Non-circular G00–G12 matrix: separate PREAUTHOR `P` and POSTAUTHOR `E`

| Gate | P / prerequisites **before owner permits private authoring S2** | E / evidence **after authorized authoring, before scoring release S4** | Responsible independent check | Current |
|---|---|---|---|---|
| `G00_SOURCE` | Exact candidate/source pins, frozen protocol/reviewer report | Recheck data/scorer/packet exact pins | Independent source reviewer | `DESIGN_SOURCE_ONLY` |
| `G01_RIGHTS` | `G01P` approved source/rights/PII policy and private handling; **not per-item rights attestations** | `G01E` per-core provenance/license/PII reviewed & attested | Rights custodian + independent audit | `P_NOT_FROZEN · E_NOT_AUTHORED` |
| `G02_NONOVERLAP` | `G02P` scope/algorithm for exact & semantic overlap and declarations of accessible historical collections | `G02E` 72 private cores exact/semantic checked against admissible history, with limitations | Distinct source QA | `P_DRAFT · E_NOT_VERIFIED` |
| `G03_MD1` | Original 32×2=64, patterns 111/000, thresholds 28/32 and0.85 unchanged | Source gold count/strata identity and sealed M0 items | MD1 source reviewer + custodian | `P_SOURCE_PINNED · E_NO_ITEMS` |
| `G04_M0X` | `G04P` 2³ rubric, truth-predicate/witness, full 12-edge rules, feasibility, no-reserve policy, independent gold plan | `G04E` 16×8 verified standalone variants, all 12 edges/core, 4 strata, two blind gold adjudicators agree on witness/evidence | Gold QA independent of item author | `P_CANDIDATE · E_NOT_AUTHORED` |
| `G05_M0U` | `G05P` 3-valued evidence rubric, 3×3 confusion, class counts, false-abstention limits | `G05E` 24 cores, balanced 8/8/8 per measured axis, adjudicated truth and source evidence | Independent epistemic-gold QA | `P_CANDIDATE · E_NOT_AUTHORED` |
| `G06_SHORTCUT` | `G06P` **all NC1–NC6**, frozen features, split, nuisance models, training budgets, thresholds & hard leakage policy | `G06E` complete negative-control and source-coupling results, group-heldout, no omissions | Independent anti-shortcut QA | `P_CANDIDATE · E_NOT_EXECUTED` |
| `G07_THRESHOLDS` | `G07P` owner-frozen **extension** thresholds, endpoints, sample size rationale and stop rules; M0 MD1 unchanged | Check no thresholds changed after item authoring | Independent prereg QA | `NOT_FROZEN` |
| `G08_BLIND` | `G08P` single-item isolation and cross-variant exposure plan, independent rater/custodian roles | `G08E` same underlying IDs, opaque mapping, sealed score packet, actual isolation/identity checks | Independent rater-custody QA | `P_DRAFT · E_NOT_ASSIGNED` |
| `G09_SCORER` | `G09P` frozen deterministic checker **spec** and negative test catalogue | `G09E` exact implemented checker pin, independent static QA and full negative fixture PASS before any rater scores | Distinct checker QA | `P_SPEC_CANDIDATE · E_NOT_IMPLEMENTED` |
| `G10_CUSTODY` | `G10P` secret storage, retention, access, commitment/attestation policy | `G10E` immutable private manifest/gold/packet commitments and authorized custodian attestations after bytes exist | Independent evidence custodian | `P_DRAFT · E_NOT_CREATED` |
| `G11_RESOURCE` | `G11P` provider/reviewer rights, isolation and cost policy; no GPU/model Small-4M needed | `G11E` approved current provider/version, no cross-chat memory, retention/access compliance | Rater/provider reviewer | `NOT_AUTHORIZED` |
| `G12_OWNER` | `G12A` **one explicit** conditional owner GO for private authoring, frozen nuisance-only proxy QA, checker implementation/synthetic negative QA, and preregistered score-release scope; **no E gates required yet** | `G12B` distinct readback of **all E gates** and immutable release event under exact G12A scope. If conditional scoring not in G12A, HOLD for a new substantive owner decision | Owner decision registry + distinct pre-score QA, not author | `G12A_NOT_GRANTED · G12B_BLOCKED` |

**Critical logical invariant (IR01):** S2 includes only the previously scoped proxy/checker pre-score work needed to produce G06E/G09E; it excludes any blind rater/Small-4M model scoring. G12A can occur when all required **P** contracts are independently reviewed and owner approves, with **zero post-data items created**. S2 then creates items privately. G12B must verify all required **E** outputs *after* S2 and only under the explicit G12A conditional scope. `PREEXEC_BLOCK=TRUE` until G12B; no self-certification, implicit permit, automatic scoring on design QA, or owner micro-permit sequence. Any missing, invalid or adverse P/E evidence → `HOLD_PRE_SCORE` with original negative receipt. Currently **neither G12A nor G12B exists**.

## 2. Canonical private schemas and validation before scoring (IR02/04/07)

The following is a *future schema contract*, not existing private files.

**`core_manifest`:** `study_id,set_id,stratum,core_id,author_id,template_id,source_license_rights_id,privacy_clearance_id,source_commitment,explicit_core_facts,actor_predicate,object_predicate,goal_predicate,actor_witness,object_witness,goal_witness,ontology_and_time,owner_custodian_id`.

**`item_manifest`:** `item_id,core_id,set_id,opaque_id,condition_pattern,actor_gold,object_gold,goal_gold,axis_evidence_witnesses,axis_invalid_flag,referent_constraints,text_commitment,gold_adjudicator1,gold_adjudicator2,gold_resolution,rights_and_nonoverlap_receipt,checksum_scheme`. Pattern ID and gold NEVER go to rater.

**`edge_manifest`** M0X: `core_id,axis,endpoint_id_0,endpoint_id_1,expected_hamming_distance=1,changed_axis_witness,unchanged_axis_witnesses_2,reviewer1_verdict,reviewer2_verdict,independent_adjudication`. EXACT graph: every M0X core has 8 nodes with 8 unique 3-bit patterns, exactly 12 unordered Hamming-1 edges (4/axis); every node degree 3, each edge references existing same-core IDs and unchanged witnesses, all edges PASS source gold. No extra/missing/duplicate edges, no edge across cores.

**`unknown_manifest`** M0U: `item_id,target_unknown_axis,source_evidence_absent_or_alternatives,explicit_no_entailment_rationale,other_axes_evidence,adjudicator_attestations`. Target axis gold `UNKNOWN` exactly, other 2 axis gold 0 or1, and across each unknown-target group of 8, each non-target 2-bit combination appears **twice**. Across 24 items each measured axis gold count 0=8,1=8,UNKNOWN=8. Gold `INVALID_SOURCE` is a **HOLD** event, not a score.

**`rater_packet`:** `packet_id,opaque_id,isolated_session_id,scorer_prompt_pin,provider_model_version,randomized_order_commitment,rater_identity,context_isolation_attestation,submission_receipt`. Rater never sees source ledger, other variants or other rater scores. Custodian privately binds opaque IDs to `item_id`; freeze map before scoring, unblind only after all score receipts frozen.

**`score_row`:** `rater_id,opaque_id,set_id,actor,object,goal,model_prompt_sha,session_attestation,receipt_commitment,invalid_reason`. Scores M0/M0X are exact typed integer 0 or1 (booleans/strings/null INVALID). Scores M0U exact typed integer 0/1 or exact string `UNKNOWN`. No implicit conversion. Total expected **2 raters×(64+128+24)=432 rows** and **1296 axis decisions** if eventually run. Missing/duplicate rows invalidate packet; never drop or impute.

**`custody_receipt`:** `frozen_protocol_sha256,owner_conditional_go_ref,private_gold_commitment,private_item_commitment,negative_proxy_receipt,rights_attestation,blind_map_commitment,rater_output_commitment,checker_pin,independent_qa_attestation,release_event`. Use private keyed/HMAC or encrypted commitments for guessable texts where approved; do NOT publish raw texts/gold/keys or claim SHA values for uncreated bytes.

## 3. Deterministic checker decision order, full denominators and reject code taxonomy

**Ordering (first FAIL is terminal HOLD):** parse strict JSON/schema/version → set IDs and unique keys → exact item/core/stratum/pattern counts → gold evidence and 12-edge graph → rights/nonoverlap → anti-shortcut full NC1–NC6 → pre-score frozen source and owner release → two raters and isolated sessions → exact score types/counts → unblind by independent custodian → compute and report every endpoint → archive independent readback. Do **not** run scorer in source-only design gate.

| Reject code | Deterministic trigger | Verdict |
|---|---|---|
| `HOLD_SCHEMA` | Missing/extra mandatory keys, incompatible version, wrong types/null/NaN | HOLD |
| `HOLD_DUPLICATE_OR_MISSING_ID` | Unknown, duplicate, missing item/core/opaque/rater; differing rater item sets | HOLD |
| `HOLD_COUNT_STRATUM` | M0≠32/64, M0X≠16/128, M0U≠24/24, invalid pattern/stratum/UNKNOWN class balance | HOLD |
| `HOLD_GRAPH` | M0X not exactly 8 nodes+12 valid edges/core, wrong Hamming axis, mismatched unchanged witness, orphan edge | HOLD |
| `HOLD_SEMANTIC_COUPLING` | Source-supported axes not independent, missing predicate, unresolvable referent, adjudicator disagreement | HOLD |
| `HOLD_INVALID_UNKNOWN_GOLD` | Target inferable, source contradictory, non-target axis not decidable or wrong gold distributions | HOLD |
| `HOLD_SHORTCUT` | Any registered nuisance proxy above limit, missing receipt, or NC1/NC6 defect | HOLD |
| `HOLD_LEAKAGE` | Label/pattern/gold exposed, core/template/author leakage, non-disjoint proxy fold | HOLD |
| `HOLD_RATER_EXPOSURE` | Shared context, same-core variant comparison, version mismatch, leaked blind mapping | HOLD |
| `HOLD_RIGHTS_NONOVERLAP` | Unattested license/PII; collision with prior approved corpus or source scope mismatch | HOLD |
| `HOLD_THRESHOLD_NOT_FROZEN` | Proposed rather than owner-frozen extensions/scorer/rubric at S2; post-hoc edits | HOLD |
| `HOLD_CUSTODY` | Missing exact commitments, score freeze/unblind order, signed/attested custodian evidence | HOLD |
| `HOLD_OWNER_OR_RELEASE` | Missing G12A, missing G12B or stage transition without guard | HOLD |
| `HOLD_SCORE_TYPE` | UNKNOWN in binary M0/M0X; invalid numeric/string/NULL/missing/duplicate in any set | HOLD |
| `HOLD_INPUT_INTEGRITY` | Any other schema/split/denominator mismatch, scorer cannot uniquely determine input | HOLD |
| `HOLD_SOURCE_CLAIM` | Historical claim falsely equates delta with absolute score, or treats nested axis ratings as independent cases | HOLD |

**Metrics only after all structural gates pass:**
- M0 per rater/axis TP+FN=32, TN+FP=32; MD1 TP,TN≥28; raw agreement proposal matches≥55/64.
- M0X per rater/axis TP+FN=64, TN+FP=64; candidate TP,TN≥56; full-vector edge correctness≥56/64/axis, stratum floor≥12/16 edges/axis/stratum; inter-rater exact matches≥109/128/axis. All 12 graph edges/core required, do not double-count as IID.
- M0U per rater/axis full **3×3 gold×prediction** with gold row sums (8,8,8), score total24; candidate targeted UNKNOWN≥7/8; non-target binary correct≥14/16; false-UNKNOWN≤1/16; true0/true1 correctly classified≥7/8 each; false certainty on true-UNKNOWN≤1/8. Always UNKNOWN predicted must FAIL non-target. Scores cannot turn invalid source into UNKNOWN.
- No score may be marked PASS unless **every** applicable endpoint and negative control passes. Any measured score below valid, prospectively frozen threshold is `FAIL_M0_SCOPED` / `FAIL_M0X_SCOPED` / `FAIL_M0U_SCOPED` (valid science assessment only after authorization), **not** HOLD for bad inputs. No change to historic frozen scores.

**Statistical evidence unit:** 32 core M0, 16 core M0X, 24 core M0U. Paired variants/edges clustered; report each stratum/core/pattern, count of failed cores and descriptive cluster uncertainty. New thresholds screen construct validity *exploratorily*, not power-confirmatory or T4-generalization proof.

## 4. Prespecified negative-fixture source QA plan (no authored science text)

| ID | Pure structural/scorer contract mutation | Required expected rejection |
|---|---|---|
| `N01` | M0X contains only 111/000 patterns yet claims per-axis validity | `HOLD_COUNT_STRATUM` (pattern-balance check precedes semantic inference) |
| `N02` | Changed actor also changes goal witness on an edge | `HOLD_SEMANTIC_COUPLING` |
| `N03` | 8 nodes but only 11/12 edges | `HOLD_GRAPH` |
| `N04` | Any matched edge connects nodes from different cores | `HOLD_GRAPH` |
| `N05` | 128 item rows but 15 unique M0X cores | `HOLD_COUNT_STRATUM` |
| `N06` | One stratum has 3 cores, another 5 | `HOLD_COUNT_STRATUM` |
| `N07` | Any nuisance model uses item-level train/test split | `HOLD_LEAKAGE` |
| `N08` | NC2–NC5 incomplete / only one weak proxy run | `HOLD_SHORTCUT` |
| `N09` | Cue-only heldout balanced accuracy >0.625 | `HOLD_SHORTCUT` |
| `N10` | Intended bit/pattern exposed as rater metadata | `HOLD_LEAKAGE` |
| `N11` | UNKNOWN gold when source explicitly negates proposition | `HOLD_INVALID_UNKNOWN_GOLD` |
| `N12` | Contradictory source mislabeled UNKNOWN | `HOLD_INVALID_UNKNOWN_GOLD` |
| `N13` | Always-UNKNOWN rater predicted across all M0U axes | `FAIL_M0U_SCOPED` under valid input |
| `N14` | TRUE UNKNOWN item scored numeric0 and false-certainty >1/8 | `FAIL_M0U_SCOPED` under valid input |
| `N15` | One non-target M0U axis also UNKNOWN in gold | `HOLD_INVALID_UNKNOWN_GOLD` |
| `N16` | Missing/duplicate opaque ID or different rater sets | `HOLD_DUPLICATE_OR_MISSING_ID` |
| `N17` | Unknown string in binary M0X, numeric 2 or bool True | `HOLD_SCORE_TYPE` |
| `N18` | Invalid 63/64 or 127/128 denominator after dropping a score row | `HOLD_DUPLICATE_OR_MISSING_ID` (row integrity check first) |
| `N19` | Same-core variants side by side in one rater context | `HOLD_RATER_EXPOSURE` |
| `N20` | No private rights/PII or Gold provenance | `HOLD_RIGHTS_NONOVERLAP` |
| `N21` | Stage S4 requested from S1 without G12A/S3 evidence | `HOLD_OWNER_OR_RELEASE` |
| `N22` | Stage S2 requested before G12A owner GO | `HOLD_OWNER_OR_RELEASE` |
| `N23` | Stage S4 with G12A authoring-only, no conditional scoring | `HOLD_OWNER_OR_RELEASE` |
| `N24` | Protocol threshold changed after item SHA freeze | `HOLD_THRESHOLD_NOT_FROZEN` |
| `N25` | Score viewed/unblinded before immutable score receipt | `HOLD_CUSTODY` |
| `N26` | A/C delta0 misreported as A=C absolute0 | `HOLD_SOURCE_CLAIM` (source claim QA) |
| `N27` | H-DATA 144 axis scores treated as 144 independent cases | `HOLD_SOURCE_CLAIM` (inference QA) |
| `N28` | Every row exists but scorer reports denominator 63/64, 127/128 or ignores one core in summary | `HOLD_INPUT_INTEGRITY` (post-parse summary consistency) |

These are **future checker QA fixtures**, not executed model/scorer tests. Author may perform separate pure graph/logic self-tests without producing items or science; distinguish such tests in a source-only receipt.

## 5. IR01–IR07 remediation traceability and unresolved execution gates

| Independent finding | Remediated design contract | Still NOT proven/executed |
|---|---|---|
| `SM4M-F2-IR-01` HIGH | G12A vs G12B, S0–S5 acyclic state machine | Owner conditional authorization, private evidence, score-release |
| `SM4M-F2-IR-02` HIGH | Ledger predicates/witnesses, exact 12 edges/core, stratum feasibility and whole-packet HOLD | Semantic existence of 8 natural variants per stratum |
| `SM4M-F2-IR-03` HIGH | Mandatory NC1–NC6, disjoint fold, feature/budget/threshold, all-proxy decision | Actual proxy performance, absence of unintended shortcuts |
| `SM4M-F2-IR-04` HIGH | UNKNOWN three-valued source rubric, 8/8/8 gold balance, 3×3 scorer, always-UNKNOWN fails | Independent UNKNOWN gold and rater data |
| `SM4M-F2-IR-05` MEDIUM | Screening-only hierarchy, cluster n, stratum floor, uncertainty limits and threshold rationale | Statistical power or external natural-output validity |
| `SM4M-F2-IR-06` MEDIUM | Per-item isolated rater, interleaved cores, no memory, exposure HOLD | Provider/human isolation verified |
| `SM4M-F2-IR-07` MEDIUM | Typed schemas, graph invariants, strict reject codes, N01–N27 plan | Actual checker implementation/source QA/negative execution |

**Current gate state:** `ALL_RUNTIME_GATES_UNVERIFIED · G12A_NOT_GRANTED · G12B_BLOCKED · PREEXEC_BLOCK=TRUE · SCIENCE_HOLD · F3/F4_NOT_OPENED · MERGE_NOT_AUTHORIZED`. Original independent reviewer `HOLD_REVISE_DESIGN` applies to old commit, not overwritten. This document is an **author remediation candidate**, not an independent PASS or a science execution permit.
