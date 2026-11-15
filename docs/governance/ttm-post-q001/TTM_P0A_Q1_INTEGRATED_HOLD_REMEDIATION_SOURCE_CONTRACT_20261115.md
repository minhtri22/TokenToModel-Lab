# TTM P0-A — Integrated design remediation of independent Q1 HOLD

**Operation:** `TTM_P0A_Q1_CONSTRUCT_EFFECTIVE_PARITY_DECISION_INTEGRATED_REMEDIATION_SINGLE_GATE`  
**Original independent reviewed HEAD:** `f3225f4f2cbc48ef15cdbc92cf5c050c78f4fa1a` · **main:** `3e6db6056dbc79747766bcdfa7cf2ce634ff6cf7`.  
**Original independent verdict:** `HOLD_Q1_SOURCE_DESIGN`. All 3 blockers are **AUTHOR_REMEDIATED_PENDING_DISTINCT_REREVIEW**, not independent PASS.  
**Source status:** reviewer summary provided by owner in chat. Original reviewer Markdown/JSON exist at local `D:/WORK/RESEARCH/_tmp/TTM_P0A_PROSPECTIVE_Q1_DISTINCT_REVIEW_20261115/`, **NOT READ BYTE-EXACT from GitHub; SHA-256 NOT_VERIFIED**. Do not impersonate original receipt.  
**Target:** exact source/design readiness for a *future* P0-A measurement Question Gate; **not benchmark validation**, not Q1 registration, not science permit.  

## F-CONSTRUCT — one assertion family and two independent axes

**One prospective assertion family only:** `LOCATED_AT(entity_id, location_id, reference_time_id)`. The three identifiers must be **explicit and unambiguous** in the authorized model/rater-visible evidence; `reference_time_id` is mandatory. Allowed: one atomic location-at-time proposition, with direct source witness. Excluded: nested coreference, inferred time, goals, causal events, multi-hop, CoT, multi-assertion stories, unstated exclusivity, implicit negatives. Whether the existing TinyStories source actually supports this family remains **UNVERIFIED**; the scope choice is not a dataset or gold authoring decision.

**Axis 1: item admission.** `ELIGIBLE`, `REJECT_RIGHTS`, `REJECT_INVALID_SCHEMA_OR_REFERENT`, `REJECT_CONFLICTING_AUTHORITY`, `REJECT_MISSING_WITNESS`, `REJECT_PARITY`, `REJECT_SHORTCUT`. A rejected item does not enter the future fact-label denominator.

**Axis 2: truth label, only for admitted items.**
- `TRUE`: exact entity/location/time triple is positively entailed by the *effective* visible source.
- `FALSE`: an explicit source-visible negation of that triple, or an incompatible location at the *same time* with an **explicitly visible exclusivity/functional-location axiom**. Do not assume a closed-world rule.
- `UNKNOWN_VALID`: well-formed triple, a **bounded and complete** declared effective visible source domain, neither entailment nor refutation, and no pre-existing claim of TRUE/FALSE with missing witness. An unknown label is a *truth outcome*, not an excuse for missing records.
- `INVALID`: ineligible item/ontology failure, not a measured fact label; missing time, ambiguous referent, conflicting authority, or malformed proposition.

**Hard boundary:** an author-assigned `TRUE` or `FALSE` whose witness disappears is `REJECT_MISSING_WITNESS`, NEVER `UNKNOWN_VALID`. If truncation/packet loss prevents verifying completeness it is `REJECT_PARITY`, NEVER `UNKNOWN_VALID`. Conflicting authoritative visible sources yield `REJECT_CONFLICTING_AUTHORITY`, not arbitrary TRUE/FALSE.

## F-PARITY — effective model/rater-visible evidence, after truncation

The required future custody trace is:
`permitted source + rights` → `witness span W` → `prompt builder and wrappers` → `tokenizer/config` → `context-window truncation` → **`MODEL_EFFECTIVE_VISIBLE_PREFIX`**;
separately `rater packet builder + disclosed rubric` → **`RATER_EFFECTIVE_VISIBLE_EVIDENCE`**. Both views must preserve the same **decisive fact witness** and semantic information budget. The full prompts need not have identical wrapper bytes. A rater may see the candidate answer but **must not receive extra hidden gold/evidence**.

Planned per-item receipt fields (all currently `NOT_CAPTURED`): `source_sha256`, `rights_ref`, `assertion_id`, `witness_span_id`, `prompt_builder_git_blob`, `rendered_prefix_sha256`, `tokenizer_id_sha256`, `context_window`, `truncation_policy/side`, `effective_token_range`, `model_effective_prefix_sha256`, `witness_token_span_after_truncation`, `witness_survives_model_window`, `rater_payload_sha256`, `rater_visible_witness_span`, `hidden_gold_absent_from_rater`, `information_parity_verdict`.

**Veto before freeze:** stored packet contains W but the effective model prefix **does not**, while rater does ⇒ `HOLD_PARITY_LOST_AFTER_TRUNCATION`. If model has W and rater not, `HOLD_PARITY`. If neither has the witness for author-assigned TRUE/FALSE ⇒ `REJECT_MISSING_WITNESS`. Treat `context=256` as the T4 target configuration only; this gate does **not** tokenize, build prompts, read private checkpoints or execute the model.

Phase order: `AD-01R` rights before source access; `AD-02/03/05` feasibility before production authoring; `AD-06` only if causal matched contrasts are proposed, before authoring/freeze; `AD-01T` exact tokenizer before token-sensitive freeze; **per-item effective view + witness parity before freeze**; `AD-01C/AD-08` before actual model run; `AD-04` independent same-task adjudication before scoring, plus a parity **recheck**. Private checkpoint custody **does not block** abstract paper-only review.

## F-DECISION — evidence required for each alternative

**Different questions:** Q1 *design eligibility* is determined by whether this grammar, two-axis label contract, effective-view trace, competing mechanisms, negatives and hard veto are logically coherent. It does **not** establish benchmark validity. Actual `KEEP` requires a later separately authorized prospective measurement study with frozen thresholds, rights, matched witness, independent gold, calibrated raters and no shortcuts.

| Decision | Minimum differentiating evidence **after** lawful future work | Current status |
|---|---|---|
| `KEEP` | Eligible scoped items with validated post-truncation witness parity, rights, independent labels, matched controls, frozen endpoint/threshold and successful prospective checks | `NOT_DEMONSTRATED` |
| `SIMPLIFY` | A localized ontology subfamily shown **before outcomes** to be the sole fixable blocker, with source/parity preserved for the narrower family | `NOT_DEMONSTRATED` |
| `PIVOT` | Original family shown structurally infeasible, plus a specific lawful alternate oracle/task with equal information access; needs a separate owner Q | `NOT_DEMONSTRATED` |
| `STOP` | Documented permanent rights/construct/oracle impossibility with no lawful feasible alternative, NOT simply a missing rights record | `NOT_DEMONSTRATED` |
| `HOLD_EVIDENCE_INSUFFICIENT` | Any missing authorization, witness/parity, unresolved label conflict, rights, rater competence, prereg threshold or proof | **`CURRENT_DEFAULT`** |

**Precedence:** unresolved evidence/hard veto ⇒ HOLD, regardless of promise; demonstrated irreversible barrier with no alternative ⇒ STOP; justified pre-outcome fixable restriction ⇒ SIMPLIFY proposal; proven inability plus lawful replacement ⇒ PIVOT proposal; only all prospective gates met ⇒ KEEP. If more than one applies, **fail closed** until reviewer and owner determine an unambiguous disposition. Never use a weighted MCDA score to bypass a hard veto. `SAMPLE_SIZE/CI/PASS_THRESHOLD/RESOURCE_BUDGET=NOT_FROZEN` now; do not invent numbers.

**Separate Q1 threshold (DESIGN):** exact question must change KEEP/SIMPLIFY/PIVOT/STOP/HOLD, one scoped assertion family, explicit source-visible label/admission split, after-truncation model/rater witness parity required, rights staged correctly, M0–M4 potentially falsifiable, negative-case rejects defined, and no HIGH finding after **distinct** reviewer re-review. This can lead only to owner consideration of Q1 registration on main; no source item/gold validity is certified.

## Negative logical controls — NO datasets created

| Case | Expected contract result |
|---|---|
| Stored W intact, but model 256-token effective view truncates W and rater sees W | `HOLD_PARITY_LOST_AFTER_TRUNCATION` |
| Model sees W but rater cannot see decisive W | `HOLD_PARITY` |
| Author's TRUE/FALSE lacks a visible witness after prompt rendering | `REJECT_MISSING_WITNESS_NOT_UNKNOWN` |
| Well-formed assertion; complete bounded effective packet does not entail/refute | `UNKNOWN_VALID` |
| Missing explicit reference time, unresolved entity, or malformed triple | `REJECT_INVALID_SCHEMA_OR_REFERENT` |
| Other location mentioned, but no visible exclusivity/negation axiom | `UNKNOWN_VALID_IF_COMPLETE`, not FALSE |
| Two authoritative conflicting locations at identical time | `REJECT_CONFLICTING_AUTHORITY` |
| Matched contrast changes location **and** time | `HOLD_AD06_IF_CAUSAL_CONTRAST` |
| Source rights not verified | `HOLD_RIGHTS` before source access |
| Independent same-task raters disagree unresolved | `HOLD_RATER_COMPETENCE` before scoring |
| Gold only in hidden `E_core` | `REJECT_MISSING_WITNESS` |
| New model run without Q1/owner science permission | `NO_MODEL_RUN` |

**Known independent verdict remains:** `HOLD_Q1_SOURCE_DESIGN`. All three author fixes remain `PENDING_DISTINCT_REREVIEW`; `BENCHMARK_GOLD=NOT_VALIDATED`; `NEW_QUESTION_REGISTERED=false`; `SCIENCE_EXECUTED=false`; `PR22=STILL_DRAFT`. No change to Q001 Q4 closure, original seven files, lineage.md or active gate.

## Bước thực hiện tiếp theo — duy nhất

`TTM_P0A_MEASUREMENT_GOLD_INTEGRATED_REMEDIATION_EXACT_CANDIDATE_DISTINCT_REREVIEW_SINGLE_GATE`

An independent reviewer audits the exact amended PR #22 candidate, checks the three HIGH blockers, schema/labels/phase timing, 12 logical negatives and source integrity, and gives **one** scoped `PASS_Q1_DESIGN_SCOPE` or `HOLD_Q1_SOURCE_DESIGN`. Neither outcome authorizes gold creation, science execution, Q1 registration, or merging.
