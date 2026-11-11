# TTM FRESH16 — Owner Adoption, Rater Custody & Single CPU GO/NO-GO Gate

**Operation:** `TTM_FRESH16_V2_OWNER_ADOPTION_RATER_CUSTODY_AND_SINGLE_CPU_GO_NO_GO_GATE`  
**Date:** 2026-11-11  
**Scope:** DESIGN / OWNER DECISION PREPARATION ONLY — NO SCIENCE EXECUTION  
**Research branch:** `research/ttm-small4m-prompt-adherence-continuation-design-20261111`  
**Last source HEAD validated before this intake:** `202477787a14cd2c30649bb9dab8f630573479f0`  
**Frozen original scientific HEAD:** `1583c5b475407799bfca75b503ddf359de7fda69`  
**Original prompt Git blob:** `6299a073f0b7c7f8ea890ba9d9b29eaed9442f1f`  
**Original rubric/H1/H2 Git blob:** `69668664df23d2246cd65935ab049054aea43e7a`  
**V2 scoring amendment Git blob:** `27b994b3b3283b2611af21d63acc5d37abf45013`

## 1. Outcome of final independent protocol review

Owner supplied the full review report in chat as `Pasted text(20261111-114748).txt`. Local uploaded file has **SHA-256 `f7b3138846d74bc2389c7a819ee6197af12e6417763aca41f96caa7ad7506f28`**, **12,418 bytes**. These are the bytes of the supplied report, NOT a signature of reviewer identity. Review provenance: reviewer self-described `ChatGPT/GPT-6`, role `INDEPENDENT_PROTOCOL_REVIEWER`, expressly not Output Rater or H2 Pair Adjudicator. Agent involved in this owner intake does not impersonate that independent reviewer.

**Review outcome as supplied:**
- P1 `PASS`: prospective outcome redefinition, cloze-only, generated new event and EOS handled.
- P2 `PASS`: semantic role-binding / fact-conditioned action distinction; CP04/CP08 limitations retained.
- P3 `PASS`: scientific claims bounded to exploratory local context/fact-conditioned continuation only.
- P4 `HOLD_IMPLEMENTATION` while `PASS_DESIGN`: output rater, H2 adjudicator, no-prior-outcome exposure attestations, sealed mapping, SHA custody and CPU runner missing.

**Amendment verdict:** `ACCEPT_CANDIDATE_FOR_OWNER_APPROVAL`. **Overall:** `PASS_PROTOCOL_REVIEW_FOR_OWNER_DECISION`. **Science execution:** `NO_GO_HOLD`.

This does **not** mean V2 is owner-adopted, that all independent raw checkpoint/BPE bytes were rehashed in the reviewer session, or that 32 outputs have been authorized.

## 2. Clarifications recognized by the reviewer without changing V2

1. `swap countercheck` compares **fact-conditioned appropriateness** of a generated event and its semantic role(s), **not** the absolute impossibility of the event after swapping conditions.
2. Fix an opaque permutation and sealed mapping **before inference**; do not reveal primary checkpoint identity in individual or pair scoring.
3. The actual `S1_SCORES_SHA` and `S2_PAIRS_SHA` are generated **after outputs are scored**, then **anchored with an independent evidence custodian or immutable Git commit** before checkpoint unblinding. Hashes beside mutable files alone are insufficient. Do NOT upload the private unblinding map to the public repository; if only a hash is shared, include a high-entropy secret salt/nonce inside the sealed map to mitigate guessing.
4. These are owner adoption/implementation conditions, **not** new changes to H1/H2, V2 scoring criteria, 16 prompts or checkpoint pins. Protocol reviewer did not require V3.

## 3. Owner's distinct, explicit decisions (none taken at intake)

**Owner must choose one:** `ADOPT_V2`, `REJECT_V2`, `DEFER_V2`. The default is `DEFER_V2`.

An `ADOPT_V2` requires explicit owner identity/time, reference to exact V2 blob, and separate **truthful** statements from owner and executor concerning whether *any* FRESH16 outputs were generated, viewed or used before adoption. Do not infer no-exposure merely from source QA receipt, lack of a directory, or lack of output in the current session. Owner/executor may be the same person, but role attestations must still be recorded distinctly. If prior outputs were seen or exposure is unknown, **cannot honestly classify V2 as prospective**; stop `NO_GO_HOLD` and decide on a fresh future protocol rather than changing scoring post-exposure.

Approval to **adopt V2** is **not** approval to **execute**: the 32-output CPU execution requires a second explicit decision after custody and source locking are complete. The template is in `docs/research/ttm-small4m-quality-gap/TTM_FRESH16_V2_OWNER_DECISION_DECLARATION_TEMPLATE_20261111.md`. No blank field or placeholder counts as an attestation.

## 4. One integrated readiness gate; no micro-permits

| Condition | Evidenced now | Requirement before GO |
|---|---|---|
| Frozen public source, BPE, checkpoint source QA | `PASS_RECORDED_SCOPED` from native Windows; reviewer raw-byte rehash separately NOT_VERIFIED | Preserve pinned bytes; no source QA replay unless actual drift |
| Independent protocol V2 review | `ACCEPT_CANDIDATE_FOR_OWNER_APPROVAL` reported | Attach reviewer report and blob pins to adoption record |
| Owner adopts V2 | **NO** | Explicit, version-pinned `ADOPT_V2` with date and intent |
| Owner + executor no-prior-outcome attestations | **NOT_ATTESTED** | Both facts declared/recorded; if unsure, HOLD |
| Output Rater | **UNASSIGNED** | Human name or AI model/version/new clean session, independent of executor, no early access to outcomes |
| H2 Pair Adjudicator | **UNASSIGNED** | Distinct predesignated person/agent/version/session; reserve alternate for disputes |
| Sealed blind permutation and map | **NOT_CREATED** | Opaque IDs for 32 outputs; 16 pairs hidden by checkpoint; map SHA anchored before inference without exposing map |
| CPU runner and executable source lock | **NOT_PINNED** | Exact P02 source blob `9762343e06cf800b50574c2871ae1ed58537fb18`, BPE manifest SHA `cba18e60cee3d08a353ee6d4a451017289e45af7b4b1179c87171b9b78d7dfdc`, checkpoint SHA1024 `cb985751795c8328ad65acf7ca4c1033ce35182c1bfbdb8c38550de629cb271b` / SHA1280 `ee723407b2c25a18be20e26387a3dd8e4a18e2942d469279b6f0748ff86af0dc`, exact runner Git blob and no TEST |
| Owner single-science CPU permit | **NOT_ISSUED** | Distinct explicit `GO_32_CPU_ONE_SHOT` after all conditions passed |

**Prelocked contract** (unchanged): original 16 prompts, 8 A/B pairs, checkpoint step1024 primary/step1280 secondary, 32 outputs, greedy argmax, context256, max64 new tokens/output, EOS256, 900 s and 8 GiB planned cap, no retry, no training and no consumed TEST/Q1/FRESH12 science replay. H1 ≥12/16 scores≥2; H2 ≥6/8 with ≥1 pass per each of 4 categories. No blind label leaks.

## 5. Evidence flow to avoid outcome leakage / mutable-score attacks

Before inference: appoint executor, independent rater, H2 adjudicator and evidence custodian; adopt V2 explicitly; generate and seal opaque map, anchor checksum with independent custodian; lock CPU runner and science permit; keep prompt/rubric/previous results unchanged.

Only after authorized single run: freeze 32 original outputs and their hashes without allowing a retry. Deliver randomized **individual** prompts plus generated text to Output Rater without checkpoint, A/B or pair labels; SHA-lock all **32 scores (S1)** in independent custody. Reveal only opaque pair membership with checkpoint still masked; H2 adjudicator freezes **16 pair decisions (S2)**, retaining generated-event and action/role evidence; anchor S2 SHA independently. After both independent locks are acknowledged, unblind checkpoint mapping and deterministically tally H1/H2. Preserve failures/inconclusive verdicts; do not invent inter-rater reliability from a single rater.

An independent Output Rater is **not** the earlier reviewer who saw CP01–CP08 and FRESH12. A single AI rater is exploratory only; explicitly disclose limits. If a substantive disagreement cannot be resolved without bias or score edits, `HOLD_SCORING_DISPUTE` and preserve all originals without rerun.

## 6. Current adjudication and required action

`V2_PROTOCOL_REVIEW=PASS_FOR_OWNER_DECISION`  
`OWNER_V2_ADOPTION=NOT_APPROVED`  
`NO_PRIOR_OUTPUT_ATTESTATION=NOT_ATTESTED`  
`OUTPUT_RATER=UNASSIGNED`  
`PAIR_ADJUDICATOR=UNASSIGNED`  
`SEALED_BLIND_MAP=NOT_CREATED`  
`RUNNER_SOURCE_SHA=NOT_PINNED`  
`SCIENCE_ONE_SHOT_PERMISSION=NOT_ISSUED`  
`EXECUTION=NO_GO_HOLD`

**This is a protocol acceptance intake and owner decision preparation, not a statement that science was executed, V2 was adopted or custody is complete.** If owner explicitly defers/rejects, remain NO-GO. If owner adopts V2 with exposure attested, carry out the remaining custody/source-locking as a **single integrated future gate**, and issue a separate execution decision only when actually ready.

Do not modify `main`, `lineage.md` or frozen science files. Do not rerun QA or inference merely to advance this paperwork.

**Bước thực hiện tiếp theo:** `TTM_FRESH16_V2_OWNER_EXPLICIT_ADOPTION_AND_RATER_CUSTODY_BINDING` — record the owner's real ADOPT/DEFER/REJECT decision and exposure attestations; if adopted, name separate rater/adjudicator and lock mapping/runner in one integrated follow-up.
