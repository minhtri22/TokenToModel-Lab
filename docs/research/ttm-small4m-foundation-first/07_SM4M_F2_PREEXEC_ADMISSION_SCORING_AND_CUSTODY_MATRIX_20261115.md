# TTM-Small-4M — F2 Pre-execution Admission, Deterministic Scoring & Custody · IR01–IR07

**Operation:** `TTM_SMALL4M_F2_IR01_IR02_IR07_AND_NF01_NF03_INTEGRATED_CONTRACT_REMEDIATION_SINGLE_GATE`  
**Source:** 06 F2 protocol of same remediation candidate; MD1 original `33021a421f05bb3bfa0999ad12bc3bd144366da9`; owner design closure `c233dff20b9b020aefd732ce62bfa2e7aebd3985`.  
**State:** `AUTHOR_CONTRACT_ONLY · EXECUTION_PREEXEC_BLOCK=TRUE · NO_GOLD · NO_SCORE · NO_MODEL`. Requirements for post-data evidence are **not prerequisites to authorizing data creation**.

## 1. Non-circular G00–G12 matrix: separate PREAUTHOR `P` and POSTAUTHOR `E`

| Gate | P / prerequisites **before owner permits private authoring S2** | E / evidence **after authorized authoring, before scoring release S4** | Responsible independent check | Current |
|---|---|---|---|---|
| `G00_SOURCE` | Exact candidate/source pins, frozen protocol/reviewer report | Recheck data/scorer/packet exact pins | Independent source reviewer | `DESIGN_SOURCE_ONLY` |
| `G01_RIGHTS` | `G01P` approved source/rights/PII policy and private handling; **not per-item rights attestations** | `G01E` per-core provenance/license/PII reviewed & attested | Rights custodian + independent audit | `P_NOT_FROZEN · E_NOT_AUTHORED` |
| `G02_NONOVERLAP` | `G02P` scope/algorithm for exact & semantic overlap and declarations of accessible historical collections | `G02E` 72 private cores exact/semantic checked against admissible history, with limitations | Distinct source QA | `P_DRAFT · E_NOT_VERIFIED` |
| `G03_MD1` | Original 32×2=64, patterns 111/000, thresholds 28/32 and0.85 unchanged | Source gold count/strata identity and sealed M0 items | MD1 source reviewer + custodian | `P_SOURCE_PINNED · E_NO_ITEMS` |
| `G04_M0X` | `G04P` **abstract-only** truth constraints, per-stratum dependency/witness feasibility, 12 Hamming-1 *symbolic* edges, no authored real text/gold; distinct source-only review | `G04E` **after G12A**: 16×8 authorized actual story/continuation envelopes, all 12 edges/core, 4 strata; gold reviewers prove parity from evidence visible to blind rater and independent source ledger | Gold QA independent of item author | `P_CANDIDATE · E_NOT_AUTHORED` |
| `G05_M0U` | `G05P` 3-valued evidence rubric, 3×3 confusion, class counts, false-abstention limits | `G05E` 24 cores, balanced 8/8/8 per measured axis, adjudicated truth and source evidence | Independent epistemic-gold QA | `P_CANDIDATE · E_NOT_AUTHORED` |
| `G06_SHORTCUT` | `G06P` **all NC1–NC6**, frozen features, split, nuisance models, training budgets, thresholds & hard leakage policy | `G06E` complete negative-control and source-coupling results, group-heldout, no omissions | Independent anti-shortcut QA | `P_CANDIDATE · E_NOT_EXECUTED` |
| `G07_THRESHOLDS` | `G07P` owner-frozen **extension** thresholds, endpoints, sample size rationale and stop rules; M0 MD1 unchanged | Check no thresholds changed after item authoring | Independent prereg QA | `NOT_FROZEN` |
| `G08_BLIND` | `G08P` single-item isolation and cross-variant exposure plan, independent rater/custodian roles | `G08E` same underlying IDs, opaque mapping, sealed score packet, actual isolation/identity checks | Independent rater-custody QA | `P_DRAFT · E_NOT_ASSIGNED` |
| `G09_SCORER` | `G09P` versioned typed JSON Schema 11, exact foreign keys/counts/canonicalization, total first-error precedence and compound-fault oracles | `G09E` authorized implemented checker, independent static QA and full N01–N28 + C01–C12 negative fixture PASS before any actual rater scoring | Distinct checker QA | `P_SPEC_CANDIDATE · E_NOT_IMPLEMENTED` |
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

**`rater_visible_request` NEW strict request:** schema version, presentation ID, task/version, **source-bearing story prefix, one candidate continuation, three canonical axis questions, rubric reference and isolated session ID**. The task/source evidence must suffice for independent rater to reach every binary gold value, without E_core/private answer key. Gold reviewers first rate the *same visible payload*, cite exact visible source UTF-8 spans, and only then reconcile ledger, independent of intended bit pattern. If hidden evidence is necessary: `HOLD_EVIDENCE_PARITY` whole packet, never score.

**`packet_binding` private:** joins item ID to presentation ID, approved set, exact canonical visible-payload hash, custodian mapping, all never shown to rater. Previous untyped `rater_packet` field list is deprecated; strict public-on-wire request and separate private binding are in schema 11. Rater receives only visible request fields; no core, stratum, condition, gold, witness answer key, other variants or metadata signals.

**`score_row`:** `rater_id,opaque_id,set_id,actor,object,goal,model_prompt_sha,session_attestation,receipt_commitment,invalid_reason`. Scores M0/M0X are exact typed integer 0 or1 (booleans/strings/null INVALID). Scores M0U exact typed integer 0/1 or exact string `UNKNOWN`. No implicit conversion. Total expected **2 raters×(64+128+24)=432 rows** and **1296 axis decisions** if eventually run. Missing/duplicate rows invalidate packet; never drop or impute.

**`custody_receipt`:** `frozen_protocol_sha256,owner_conditional_go_ref,private_gold_commitment,private_item_commitment,negative_proxy_receipt,rights_attestation,blind_map_commitment,rater_output_commitment,checker_pin,independent_qa_attestation,release_event`. Use private keyed/HMAC or encrypted commitments for guessable texts where approved; do NOT publish raw texts/gold/keys or claim SHA values for uncreated bytes.


## 2A. Strict machine-readable record contract (IR-07 / NF-03)

**Normative** source-only candidate: [11_SM4M_F2_TYPED_PRIVATE_RECORD_SCHEMA_20261115.json](11_SM4M_F2_TYPED_PRIVATE_RECORD_SCHEMA_20261115.json), JSON Schema Draft 2020-12 with ID `urn:ttm:sm4m:f2:contract:20261115:v1`. It defines 10 exact discriminated record types: `core_manifest,item_manifest,edge_manifest,unknown_manifest,rater_visible_request,packet_binding,gold_adjudication,score_row,stage_event,custody_receipt`. Every record has strict required fields, types/enums and `additionalProperties=false`; null/booleans/string score coercion are forbidden. A record's envelope is `{schema_version:"sm4m-f2-v1",record:...}`. Private records never go to public GitHub and the existing state has **zero real data records**.

**Mandatory deterministic cross-record checks (not expressible by JSON Schema alone):**

| Check | Exact invariant |
|---|---|
| ID scopes and FK | `study_id` exact; unique `(study_id,set_id,core_id)` and `(study_id,set_id,item_id)`; unique presentation ID per study. Every item joins exactly one parent core; every edge joins two distinct items in the **same M0X core**; each UNKNOWN case joins one M0U item; each visible packet joins exactly one private item through `packet_binding`; every score row joins one registered rater and one visible packet. Orphans, duplicate keys or ambiguous joins HOLD |
| Counts | M0 32 cores/64 items, 4×8 strata, each core one 111 and one 000. M0X 16 cores/128 items, 4×4 strata, each core one of each 8 patterns. M0U 24 cores/24 items, 4×6 strata, exactly two UNKNOWN target cases per axis per stratum; per measured axis gold 0/1/UNKNOWN =8/8/8. All 72 cores across sets must be independent and nonoverlapping |
| Graph | M0X each core: exactly 8 unique nodes, 12 unique undirected Hamming-1 edges, degree3/node, four edges/axis, no cross-core links. Edge source witnesses of the two **unchanged** axes must be identical and visible to blinded rater. Each pattern bit must match `item_manifest.gold_vector`; the numeric condition index is frozen as 0–7 in lexicographic bit order |
| Gold adjudicator | Each `gold_adjudication.axis_witnesses` must contain **exactly one actor, one object and one goal** in this fixed order, each `verdict` equals the same position in `gold_vector`; two **distinct** independent adjudicators for each item, with each `visible_packet_sha256` matching the binding; disagreement → HOLD without majority vote |
| Evidence parity | `rater_visible_request` contains frozen identical prefix, one continuation, canonical actor/object/goal questions and source/rules sufficient to judge each axis. Private `gold_adjudication` must cite those very visible bytes; it may read E_core only after blinded first pass and cannot use ledger-only facts to score. Inadequate visible evidence → `HOLD_EVIDENCE_PARITY` before any rating. Never send `packet_binding`, core ID, gold bit, ledger, stratum or adjacent variants to rater |
| Source spans | `start_utf8 < end_utf8 ≤ len(UTF8(segment))` where segment is exact visible story prefix or continuation. Offsets are bytes, not JS UTF-16 code units. No parser silently normalizes Unicode, changes case or rewrites story. UNKNOWN must have independent non-entailment rationale, INVALID_SOURCE is a HOLD class, not a scored prediction |
| Score integrity | Two independent raters on exactly the same (opaque-mapped) item set. Unique `(rater_id,presentation_id)`, no missing/extra rows; M0/M0X exactly typed 0/1, M0U 0/1/exact `UNKNOWN`, all in actor-object-goal order. No score rows before actual S4, no impute/drop. Full 3×3 UNKNOWN confusion and per-core dependent edges remain unchanged |
| Stage and release | Only forward `S0→S1→S2→S3→S4→S5`; S2 needs actual G12A owner decision, S4 needs explicit conditional scoring scope + all E gates independently verified + immutable G12B. **Early S0/S1 stage events must not require future release receipts or post-data hashes**. No permission inferred from design review or synthetic checker QA |
| Canonical byte / digest | Use RFC8785 JCS JSON canonicalization (UTF-8, **no Unicode normalization**) for complete private record; lengths/bindings computed over exact content; canonical record sort order: `(record_type,study_id,set_id,core_id,item_id,presentation_id,rater_id)` (missing keys sort as empty only for ordering). For future committed bundles, hash length-prefixed serialized canonical records. Use private keyed/encrypted commitments when plaintext is guessable; never publish source text/gold/key or invent digest for bytes not yet created |
| Stage-specific snapshot | Dataset records required only after owner-authorized S2; frozen gold/rights/proxy evidence required for G12B, not G12A. Score records required only after S4; checker source may be separately implemented and negative-tested **only** within future owner-authorized S2 QA scope |

**Schema versioning:** any change in field types, gold grammar, question payload, digest or error priority requires a new exact schema pin and owner prospective approval before data authoring. The JSON schema describes *per-record syntax*; the cross-record invariants above are normative and must be implemented/tested at G09E after authorization. A JSON Schema check alone does **not** certify semantic validity.

## 2B. Deterministic total first-error priority and compound-fault oracle

Runtime permission is checked **before reading a candidate scoring packet**: absent G12A/G12B or an illegal stage means terminal `HOLD_OWNER_OR_RELEASE`, even if the data might have other faults. A pure structural source QA may simulate guards in a **separate offline harness only**; synthetic test switches are not allowed in any real packet and imply no owner permit.

For a hypothetically authorized stage, collect detected errors without mutating the packet and choose the **lowest rank** below. At equal rank, choose lexical UTF-8 order of `(study_id,set_id,core_id,item_id,presentation_id,rater_id)` then lexical UTF-8 JSON-pointer path; this produces exactly one terminal code and a stable sorted diagnostic list.

| Rank | Code | Scope |
|---:|---|---|
| 01 | `HOLD_SCHEMA` | Malformed JSON, version/class, forbidden/missing keys, wrong non-score types |
| 02 | `HOLD_DUPLICATE_OR_MISSING_ID` | Key uniqueness, FK, missing IDs and rater-set mismatch |
| 03 | `HOLD_COUNT_STRATUM` | Wrong core/item/stratum/pattern counts |
| 04 | `HOLD_GRAPH` | Invalid 8-node/12-edge structure or cross-core edges |
| 05 | `HOLD_SEMANTIC_COUPLING` | Causally dependent axis or broken invariant witness |
| 06 | `HOLD_EVIDENCE_PARITY` | Gold cannot be decided from rater-visible evidence or visible hash differs |
| 07 | `HOLD_INVALID_UNKNOWN_GOLD` | Wrong UNKNOWN/decidable distinction |
| 08 | `HOLD_RIGHTS_NONOVERLAP` | Source rights/PII/nonoverlap failure |
| 09 | `HOLD_LEAKAGE` | Rater label leak or invalid heldout group split |
| 10 | `HOLD_SHORTCUT` | Any missing/failing NC1–NC6 nuisance control |
| 11 | `HOLD_THRESHOLD_NOT_FROZEN` | Unfrozen or modified prospective cutoff |
| 12 | `HOLD_RATER_EXPOSURE` | Shared context/memory or same-core comparison |
| 13 | `HOLD_SCORE_TYPE` | Invalid typed score, including UNKNOWN in M0/M0X |
| 14 | `HOLD_CUSTODY` | Missing commitment, score freeze/unblind order |
| 15 | `HOLD_SOURCE_CLAIM` | False historic source/denominator/inference claim |
| 16 | `HOLD_INPUT_INTEGRITY` | Any other deterministic summary defect |

**Score type vs generic schema:** if the **only** schema defect is a score-vector value/type in an otherwise valid score row, classify `HOLD_SCORE_TYPE`; otherwise `HOLD_SCHEMA` takes rank 01. This specialized classification is deterministic. Valid but below-threshold results are `FAIL_M0_SCOPED` / `FAIL_M0X_SCOPED` / `FAIL_M0U_SCOPED`, never input HOLD.

**Compound negative-fixture oracles — all are plans, NOT_EXECUTED against real checker:**

| ID | Hypothetical defects | First terminal code |
|---|---|---|
| `C01` | Owner G12A absent AND invalid graph | `HOLD_OWNER_OR_RELEASE` (runtime) |
| `C02` | Duplicate item ID AND bad stratum count | `HOLD_DUPLICATE_OR_MISSING_ID` |
| `C03` | Missing pattern AND semantic coupling | `HOLD_COUNT_STRATUM` |
| `C04` | Cross-core edge AND missing gold evidence in visible prefix | `HOLD_GRAPH` |
| `C05` | Broken axis invariance AND insufficient visible context | `HOLD_SEMANTIC_COUPLING` |
| `C06` | Gold only in hidden E_core AND proxy lexical leak | `HOLD_EVIDENCE_PARITY` |
| `C07` | Wrong UNKNOWN rationale AND rater exposure | `HOLD_INVALID_UNKNOWN_GOLD` |
| `C08` | Unknown schema key AND bad score | `HOLD_SCHEMA` |
| `C09` | Only UNKNOWN score in M0X, no other faults | `HOLD_SCORE_TYPE` |
| `C10` | Owner authorization lacks conditional score release AND score invalid | `HOLD_OWNER_OR_RELEASE` (runtime) |
| `C11` | Valid early S1 event with no future S4 release receipt | **ACCEPT_STAGE_EVENT_SCHEMA**, no HOLD |
| `C12` | G04P symbolic PASS, G04E texts absent, S4 requested | `HOLD_OWNER_OR_RELEASE` (no release) |

Original N01–N28 remain future tests, **NOT_EXECUTED**, and cross-record/post-data negative QA is not authorized here. Precedence above supersedes inconsistent informal first-error descriptions when several faults occur.

## 3. Deterministic checker decision order, full denominators and reject code taxonomy

**Ordering (first FAIL is terminal HOLD):** parse strict JSON/schema/version → set IDs and unique keys → exact item/core/stratum/pattern counts → gold evidence and 12-edge graph → rights/nonoverlap → anti-shortcut full NC1–NC6 → pre-score frozen source and owner release → two raters and isolated sessions → exact score types/counts → unblind by independent custodian → compute and report every endpoint → archive independent readback. Do **not** run scorer in source-only design gate.

| Reject code | Deterministic trigger | Verdict |
|---|---|---|
| `HOLD_SCHEMA` | Missing/extra mandatory keys, incompatible version, wrong types/null/NaN | HOLD |
| `HOLD_DUPLICATE_OR_MISSING_ID` | Unknown, duplicate, missing item/core/opaque/rater; differing rater item sets | HOLD |
| `HOLD_COUNT_STRATUM` | M0≠32/64, M0X≠16/128, M0U≠24/24, invalid pattern/stratum/UNKNOWN class balance | HOLD |
| `HOLD_GRAPH` | M0X not exactly 8 nodes+12 valid edges/core, wrong Hamming axis, mismatched unchanged witness, orphan edge | HOLD |
| `HOLD_SEMANTIC_COUPLING` | Source-supported axes not independent, missing predicate, unresolvable referent, adjudicator disagreement | HOLD |
| `HOLD_EVIDENCE_PARITY` | Necessary gold evidence only in hidden ledger or absent from rater-visible request; frozen visible payload mismatch | HOLD |
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
| `SM4M-F2-IR-07` MEDIUM | Typed schemas, graph invariants, strict reject codes, N01–N28 plus C01–C12 compound oracle plan | Actual checker implementation/source QA/negative execution |

**Current gate state:** `ALL_RUNTIME_GATES_UNVERIFIED · G12A_NOT_GRANTED · G12B_BLOCKED · PREEXEC_BLOCK=TRUE · SCIENCE_HOLD · F3/F4_NOT_OPENED · MERGE_NOT_AUTHORIZED`. Previous distinct reviewers retained `HOLD_REVISE_DESIGN` at both 07adab… and cf0f… candidates; neither original finding history is overwritten. This document is an **author remediation candidate**, not an independent PASS or a science execution permit.

## 6. Integrated remediation traceability (design only)

IR-01/NF-02: G04P abstract-only before G12A and G04E real text after. IR-02/NF-01: visible prefix+continuation+axis questions parity and hidden ledger prohibited as sole gold evidence. IR-07/NF-03: typed schema 11, full join/graph/canonicalization/reject priority and C01–C12 compound cases. IR-03/04/05/06 remain CLOSED_DESIGN with E gates NOT_VERIFIED. **PREEXEC_BLOCK=TRUE; G12A_NOT_GRANTED; G12B_BLOCKED; NO_SCIENCE; F3/F4_NOT_OPENED; NO_MERGE.**
