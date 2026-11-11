# HANDOFF AGENT S2 — Blind Counterfactual Pair Adjudicator

**Operation:** TTM_FRESH16_V2_S2_INDEPENDENT_COUNTERFACTUAL_PAIR_ADJUDICATION
**Role:** FRESH16_S2_PAIR_ADJUDICATOR, **not** executor, S1 individual rater or prior independent protocol reviewer.
**Repository reference:** minhtri22/TokenToModel-Lab
**This handoff is role-isolated.** Do not browse source files revealing checkpoint names, source map, aggregated thresholds, original A/B IDs or previous output scores beyond the locked S1 scores in your authorized packet.

## 1. Start condition and data

Create a **fresh independent session**, record actual model/human identity and version/session. **Before S1 SHA is durably locked in a Git commit, do not review pairs**. If a real 16-pair packet has not arrived, respond **READY_FOR_S2_PACKET — PAIR_SCORING_NOT_PERFORMED**.

Once unlocked by owner, receive **exactly 16 anonymized pairs**, each pair containing two anonymous outputs from the **same hidden model condition**, exact respective prompt_texts, generated_text_only and the corresponding **immutable S1 adherence_0_3**. You may see which two belong to one pair at this point; you must NOT see checkpoint step labels, which condition is primary, source map, H1/H2 pass thresholds, aggregate results, or any unused historical TEST. Do not contact S1 to change an earlier rating.

## 2. Pair scoring: fact-sensitive semantics, not string swap

For a pair to score counterfactual distinction = 1, verify ALL five:
1. Both **already locked** S1 adherence scores are ≥2. Do not regrade.
2. Both continuations contain newly generated **observable events** (not just a completed prompt slot); quote **exact span from generated-only text** of each.
3. The fact intervention changes a **meaningful event predicate, semantic role** (holder/recipient/patient/source/destination/location) or relevant outcome/state; the changed part binds correctly to the new event in both conditions.
4. Neither generated event directly contradicts its own changed fact.
5. A **swap countercheck** indicates the contrast depends on the differing prompt facts, i.e. after hypothetically swapping conditions its fit is meaningfully reduced or unsupported. It does **NOT** require the action to be absolutely impossible when swapped.

Difference classes:
- LEXICAL_SWAP_ONLY ⇒ 0: isolated different word/name but no grounded new event.
- SEMANTIC_ROLE_BINDING ⇒ possibly 1: same verb with **different correct fact-dependent role/object/holder/place**, in new events.
- FACT_CONDITIONED_ACTION ⇒ possibly 1: substantively differing action/outcome by fact.
- GENERIC_COMMON_VALID ⇒ 0: same generic behavior is plausible under both; **not automatically a model error**.
- UNRELATED_DIVERGENCE ⇒ 0: differences unrelated to intervention.
- CONTRADICTORY_OR_UNINTERPRETABLE ⇒ 0: contradiction or a locked score below 2.
- AMBIGUOUS_NON_DIAGNOSTIC ⇒ 0, explain ambiguity; if the rubric itself cannot be consistently applied, HOLD_SCORING_DISPUTE rather than arbitrary decision.

Compare **event tuples**, not verb tokens: actor, predicate, patient, recipient, source, destination/location, condition and goal outcome. A single changed noun does not suffice; a same-verb event with a fact-bound role can suffice. Common-valid replies may be individually fine yet fail this pairwise *observed contrast* test.

## 3. Deliverable after the real S2 packet

A single UTF-8 JSON with exactly 16 unique opaque_pair_id and each original pair's **two** opaque member IDs, plus locked S1 score references. Use this shape (illustrative placeholders, NOT actual findings):

~~~json
{
  "schema": "ttm.fresh16.v2.s2_pair_scores.v1",
  "adjudicator_identity_and_version": "REAL_SESSION_IDENTITY",
  "s1_score_file_sha256": "ACTUAL_LOCKED_S1_SHA256",
  "records": [
    {
      "opaque_pair_id": "COPY_PAIR_ID",
      "member_opaque_ids": ["COPY_MEMBER1_ID", "COPY_MEMBER2_ID"],
      "locked_s1_adherence": [0, 0],
      "h2_binary": 0,
      "semantic_contrast_class": "AMBIGUOUS_NON_DIAGNOSTIC",
      "member_event_text_spans": ["", ""],
      "member_event_tuples": [{}, {}],
      "swap_countercheck_result": "EXPLAIN_INTERVENTION_DEPENDENT_APPROPRIATENESS",
      "pair_evidence": "EXACT_GENERATED_TEXT_AND_CAUSAL_ROLE_JUSTIFICATION",
      "non_diagnostic_not_model_error": false
    }
  ]
}
~~~

Do not assign scores until actual pairs exist. For every H2=1, provide both generated-only spans and explicit role/action relation plus the swap-countercheck. Never supply checkpoint labels or model-quality conclusions. Preserve all 16 cases, including hard/ambiguous ones; no dropping, repairing or changing denominator.

Owner/Executor verifies S1 SHA and pair completeness, locks S2 JSON by SHA-256 and anchors a **Git commit containing only the SHA receipt**, **before** final checkpoint unblinding. If disagreement cannot be resolved within the prespecified facts and rubric, report HOLD_SCORING_DISPUTE; do not invent consensus or request a rerun.

**Now:** No real output/S1 scores are supplied. Initial response is role readiness only.

**Bước thực hiện tiếp theo:** acknowledge READY_FOR_S2_PACKET with real adjudicator identity/version/session. Only after the committed S1 lock and receipt can you produce the 16 pair judgments; hand off to owner for S2 SHA lock, then unblind.
