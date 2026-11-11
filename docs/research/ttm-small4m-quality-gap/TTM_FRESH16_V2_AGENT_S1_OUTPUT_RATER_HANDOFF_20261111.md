# HANDOFF AGENT S1 — Blind Individual Continuation Rater

**Operation:** TTM_FRESH16_V2_S1_INDEPENDENT_OUTPUT_SCORING
**Role:** FRESH16_S1_OUTPUT_RATER (independent session; not executor, protocol reviewer or H2 pair adjudicator)
**Repository reference:** minhtri22/TokenToModel-Lab
**This handoff is intentionally self-contained.** Do NOT browse other FRESH16 research files, previous audit reports, model checkpoint metadata, H1/H2 pass thresholds, hidden mapping, competing rater work or training/TEST data. Do not ask owner to disclose model variants or paired relationships.

## 1. Receive and declare role

In a **fresh chat/session**, record exact rater identity (human or AI model/provider/version/session ID as available) and that you have not seen any model outputs for this assignment before the packet. You receive only one private packet with **32 individually shuffled cases**, each containing:

- opaque_id (anonymous identifier)
- prompt_text (original English story fragment)
- generated_text_only (exact continuation tokens decoded from model; empty string allowed)

The packet must contain **no checkpoint labels**, no A/B, no pair identity and no aggregate score targets. This GitHub file contains no test answers. If no real output packet has been supplied, respond **READY_FOR_S1_PACKET — NO_SCORING_PERFORMED**. Do not invent 32 continuations.

## 2. What to score

Read prompt for actor, object, changed fact and stated goal. Award points **only for newly generated text**; content inside prompt never earns points. The adopted *prospective* operational definition requires **a new observable event** for adherence≥2. A new event has actor (possibly implicit), action/outcome/state transition **not already completed in the prompt**, and a concrete fact-dependent participant/role/result. Finishing a dangling prompt slot or echoing a previous intention is not a new event; a grammatically complete sentence is not required.

**Adherence (0–3):**
- **0:** Empty/EOS immediately, uninterpretable continuation, or clear central contradiction.
- **1:** Interpretable but only a word/phrase cloze completion, actor/object echo, recycled intended action or fragment **without newly realized event**, even if the entity word is right.
- **2:** At least one evidence-supported new event relevant to actor, changed fact and goal, with no direct contradiction (small lapse acceptable).
- **3:** Fact-grounded new event advances events coherently and preserves people, roles, objects and goal.

For every adherence≥2, quote an **exact generated-only substring** witnessing the new event, state the predicate and who/what it applies to. If a verb starts in prompt, require generated text to assert something beyond merely supplying that verb's already cued object. EOS after a real event is permitted; EOS before any event does not earn 2. Pure fluent text does not substitute for correct fact binding. Do not give points for copying prompt text. If boundaries/Unicode are ambiguous, flag with exact evidence instead of guessing.

**Secondary scores 0–3 (descriptive only):**
- coherence: 0 incoherent, 1 understandable scraps, 2 mostly linked events, 3 coherent progression.
- entity_consistency: 0 contradiction, 1 major confusion, 2 minor lapse, 3 fully consistent entities/object state.
- causal_continuation: 0 contradiction/irrelevance, 1 weak cause response, 2 mostly relevant response, 3 clear goal/cause-linked progress.

Scoring decisions are independent for all 32 cases. Do not identify duplicate prompts across cases, try to pair them or infer model checkpoint. Do not calculate pass/fail of model quality; your role ends after immutable individual scoring.

## 3. Exact deliverable (after real packet arrives)

Return a **single** machine-readable UTF-8 JSON file with exactly 32 unique opaque IDs, same case IDs as input and no new output text authored by you; recommended shape:

~~~json
{
  "schema": "ttm.fresh16.v2.s1_individual_scores.v1",
  "rater_identity_and_version": "REAL_SESSION_IDENTITY",
  "records": [
    {
      "opaque_id": "COPY_ID_FROM_INPUT",
      "adherence_0_3": 0,
      "coherence_0_3": 0,
      "entity_consistency_0_3": 0,
      "causal_continuation_0_3": 0,
      "cloze_only": false,
      "has_new_event_after_slot": false,
      "generated_event_text_span": "",
      "new_event_predicate": "",
      "new_event_arguments": "",
      "hard_fact_contradiction": false,
      "reason_for_score": "CITE_GENERATED_ONLY_TEXT_OR_EXPLAIN_EMPTY"
    }
  ]
}
~~~

The zero values above are **schema placeholders, not real scores**. A row with adherence≥2 must have true has_new_event_after_slot and a nonempty exact span from generated_text_only. Do not add step, variant, pair ID, threshold-derived pass labels or inferred hidden metadata. Report missing/corrupt rows as HOLD; never generate replacement outputs. Do not modify original packet.

Owner/Executor verifies cardinality and referential IDs, locks the completed S1 file's SHA-256, and anchors the SHA receipt in a **Git commit** before releasing pair information to S2. No score edits once locked; if impossible to assess, report a scoped scoring disagreement/hold with evidence, not invented certainty.

**Now:** No output packet was provided, so this is a role handoff/readiness request only. Do not ask to run the model or access TEST.

**Bước thực hiện tiếp theo:** state READY_FOR_S1_PACKET and your actual rater identity/version/session; once supplied a real 32-item blinded packet, produce all individual scores and the evidence fields, then hand off to owner for S1 SHA lock.
