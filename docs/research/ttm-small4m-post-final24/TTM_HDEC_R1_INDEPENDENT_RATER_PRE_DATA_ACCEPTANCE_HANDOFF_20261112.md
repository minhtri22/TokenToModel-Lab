# HANDOFF — TTM-Small4M H-DEC-R1 Independent Blind Rater: PRE-DATA ACCEPTANCE

**Operation:** `TTM_H_DEC_R1_INDEPENDENT_BLIND_RATER_PRE_DATA_ACCEPTANCE`  
**Run ID:** `TTM_SMALL4M_POST_FINAL24_DECODING_REPETITION_DIAGNOSTIC_V1`  
**Review classification:** `EXPLORATORY_SCOPED_AI_REVIEW` if the reviewer is AI.  
**Status at handoff:** `NO_MODEL_OUTPUTS_REVIEWED`, `RATER_ACCEPTANCE_PENDING`, `SCORING_NOT_STARTED`.

## Scope

You are invited to independently score **24 paired prompts, 48 anonymous text continuations** in a *future*, separately provided blind packet. Each text will receive integer scores `0..3` for **prompt adherence**, **coherence**, and **consistency**, yielding **144 scores**, plus **24 concise pair notes**. Tied scores are permitted. Scoring must be frozen with SHA-256 **before any unblinding**.

**For this turn, do not score anything.** No packet, text, model identities, research results, checkpoint, or arm mapping is provided. Only acknowledge or decline the prospective reviewer role in a new ChatGPT conversation.

## Blindness and independence requirements

1. Work solely in this new conversation. Do **not** consult prior user conversations, saved memories, connected apps, GitHub, Google Drive, earlier outputs, or owner-only analysis of this research.
2. Do **not** attempt to identify or infer the systems behind `LEFT` and `RIGHT`, or ask for any encryption key, per-pair mapping, training text or original evaluation outcomes.
3. Accurately identify yourself as an AI reviewer if applicable. Do not claim human or institutional independence. A reviewer session reference you invent is **not** a platform-issued conversation ID.
4. You may decline if you have already seen the arm-to-position mapping, the outputs to be scored, or the owner-only results, or if you cannot honor the 24-pair, 144-score contract.
5. Do **not** accept scientific inference execution privileges. Reviewer acceptance is *not* owner science GO.

## Required pre-data response

Return exactly one JSON object with these fields:

```json
{
  "schema": "ttm.hdec_r1.independent_rater.pre_data_acceptance.v1",
  "run_id": "TTM_SMALL4M_POST_FINAL24_DECODING_REPETITION_DIAGNOSTIC_V1",
  "reviewer_identity": "<actual model or reviewer identity>",
  "reviewer_kind": "AI",
  "reviewer_session_reference": "<new self-generated label; declare this is not a provider conversation ID>",
  "acceptance": "ACCEPTED_PRE_DATA",
  "prior_arm_mapping_seen": false,
  "prior_owner_private_results_seen": false,
  "blind_packet_received": false,
  "scoring_started": false,
  "commitment": "24 pairs, 48 texts, 144 integer scores 0-3, 24 notes, exact input/output SHA-256, freeze before unblind",
  "scope": "EXPLORATORY_SCOPED_AI_REVIEW",
  "unblind": "NOT_EXECUTED",
  "independence_limitation": "self-attested new session, not provider-verified organizational independence"
}
```

If any requirement cannot be met, change `acceptance` to `DECLINED_HOLD` and state why. Never invent that a future packet has already been received or scored.

**Handoff complete when** the owner receives and independently verifies this pre-data acceptance receipt. The owner will deliver a neutral blinded packet *only after* science release, exact source pinning and one-shot inference; no future reviewer action is authorized by this handoff itself.
