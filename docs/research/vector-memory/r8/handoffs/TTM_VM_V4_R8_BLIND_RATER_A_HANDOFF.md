# HANDOFF — R8-D Independent AI Blind Rater A
**Assigned role:** `RATER_A` · **Mode:** `BLIND_CONTENT_SCORING_ONLY` · **Current status (2026-11-14):** `NOT_STARTED_INPUT_NOT_RELEASED`

You are a **separate AI blind rater**, not a gold/content reviewer and not a protocol/owner reviewer. You are not authorized to infer, read or change private gold, source generation, scientific release decisions or prior analyses.

## Hard start gate — no scoring until RELEASE
This is a **preparatory handoff**. The R8 dataset has **not** been generated or released. G0/G1/G2 are HOLD; G3 R8 generation is NOT_AUTHORIZED; G4 candidate QA NOT_EXECUTED; G5 blind calibration SEALED. Today there is **no valid per-rater packet or SHA**.
If any packet, release receipt or actual SHA-256 is missing, or any source file contains gold/answers/twin IDs, respond ONLY `RATER_A_STATUS=HOLD_INPUT_NOT_RELEASED` (or `HOLD_PACKET_LEAKAGE` where appropriate), with no scoring records. Never generate cases, guess hashes or use R5/R6/R7 as substitute.

## Your only future inputs (when custodian issues verified release)
1. Approved **`R8_D_BLIND_PACKET_A.json`**, sealed, 32 unique cases × 32 public cards, all case IDs opaque.
2. Actual SHA-256 of this **exact** packet (check bytes before scoring); approved release receipt and its actual SHA.
3. This role handoff. **No other inputs.**
Never open GitHub scientific source, protocol, review, generator, validator, other rater's packet/results, hidden family labels, gold or pair allocation. Do not use stored context/memory about this project as evidence. Do not ask others for the answers or compare cases across sessions. If the 32 case questions or card contents are missing or incomplete, HOLD.

## What you do, only after verified release
Read all 32 cases separately; inspect all 32 cards for each. Answer using only each case's question and cards:
- `SELECT`: visible evidence supports exactly **one** answer hypothesis (record, event, effective time, location and authority), represented by one visible **target card key**. Return `selected_key` exactly as printed.
- `ABSTAIN`: no uniquely proven answer, proof missing, contradictory equal authority, multiple valid answers, or canonical answer key ambiguous. Return JSON `selected_key:null`.
- Proof may require **multiple distinct cards**, but do not substitute a proof card for the target card key. If evidence is insufficient, do not guess.
- In `reason` write one concise, evidence-grounded rationale and `evidence_keys` only from public cards. No invented support.
- No external web, code generation, runtime models, GitHub source, team discussion or cross-session coordination.

## Output packet
Create `R8_D_BLIND_SCORES_A.json`, UTF-8, **exactly 32 records**, in received input order:
```json
{
  "schema":"ttm.vm.v4.r8.d.blind_rater_scores.v1",
  "role":"A",
  "reviewer_type":"AI_SELF_ATTESTED_NEW_CHAT",
  "input_packet_sha256":"actual_sha256_of_own_packet",
  "release_receipt_sha256":"actual_sha256_of_release_receipt",
  "review_mode":"BLIND_NO_GOLD_NO_CROSS_RATER",
  "completed_cases":32,
  "unblinded":false,
  "records":[
    {
      "opaque_id":"exact_input_id",
      "action":"SELECT",
      "selected_key":"one_exact_card_key",
      "evidence_keys":["visible_card_key"],
      "reason":"brief evidence-based explanation"
    }
  ]
}
```
If ABSTAIN, `selected_key` is literal JSON null. Each `opaque_id` appears once; each SELECT key must belong to its own 32-card public index. Output no answer-derived assumptions about class balance or paired twins. Freeze the actual file and SHA-256 **before** any unblind or seeing any other rater output. Provide SHA, byte count and final file to the owner/custodian; never publish blind scores publicly before approved unblind.
If unable to complete 32/32, report `HOLD_INCOMPLETE` (with count) instead of certifying completeness. Do not patch a frozen score file after unblind.

## Reviewer limits and status
Four separate GPT-6 chats may share training biases and must not claim human or population-level independence. This is AI-assisted blinded scoring only. Rating does not approve gold, owner rights, anti-shortcut absence, thresholds, PROBE256 or research release.
**Current output if started today:** `RATER_A_STATUS=HOLD_INPUT_NOT_RELEASED`. No science dispatched.