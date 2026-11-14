# HANDOFF — TTM Vector Memory V4 R8-D · Four Blind Raters / Custodian
**Operation:** `TTM_VM_V4_R8_FOUR_BLIND_RATERS_PREPARED_HANDOFF_NO_SCORING_NO_GENERATION`  
**Date:** 2026-11-14 · **Status:** `DESIGN_ONLY_HANDOFF_PREPARED` · `SCORING_NOT_AUTHORIZED`  
**Parent scientific design:** `b8410d9c1f77a733036e980b567de73c316f8725`; `TTM_VM_V4_R8_V4_GOLD_FOLD_ORACLE_RATER_OWNER_SCOPE_SINGLE_PACKET_DESIGN_ONLY_20261114.md`.
**Warning:** This is a FUTURE execution template, NOT authorization. R8 does not yet exist; no calibration packet or SHA-256 is available. G0 independent protocol review HOLD, G1 owner rights and scope HOLD, G2 private custodian/source and validator HOLD, G3 generation NOT_AUTHORIZED, G4 independent QA NOT_EXECUTED, G5 blind rating SEALED; G6 threshold and PROBE256 SEALED. R7 stays FROZEN_FAIL.

## Coordinator-only preconditions, before sending ANY packet to raters
1. **G0**: distinct independent review of R8 V4 passes B01 (answer hypothesis/F07), B03 (graph/folds and rater isolation), B04 (O1–O8 including O5) and validates B05 descriptive-only scope. A G0 design PASS does not confer generation permission.
2. **G1**: verifiable owner adoption of `ADOPT_R8_D_DESCRIPTIVE_ONLY` and `FOUR_RATERS_TWO_PER_CASE`, with rights and PII/source attestations; no AI self-signature. The alternative `RETAIN_CONFIRMATORY_OBJECTIVE_NO_GO` means this four-rater flow must not run.
3. **G2**: custodian byte readback and access control of private gold; versioned validator, source lock, exact code hashes, pre-frozen HMAC allocation and blind redaction.
4. **G3**: one-shot R8 generation, candidate SHA pinned; preserve source exactly, no fixing after QA reveal.
5. **G4**: distinct independent semantic/content QA and anti-shortcut diagnostics. Any FAIL, unresolved material leakage, invalid folds, ambiguous gold, missing custody or source-rights release => do not export rater packets.
6. **G5 release**: protocol owner/custodian issues a single release receipt authorizing ONLY blind R8-D descriptive scoring. No threshold freeze or PROBE unsealing.

## Internal design; DO NOT send this coordinator document to raters
If four-rater allocation is approved, 8 relation families × 4 counterfactual pairs each => 32 pairs/64 cases. Per pair, send each twin to two different raters and never both twins to any rater. Proposed per-family pair-slot matrix (0..3):
| Pair slot | SELECT twin | ABSTAIN twin |
|---|---|---|
| 0 | A,B | C,D |
| 1 | A,C | B,D |
| 2 | C,D | A,B |
| 3 | B,D | A,C |
Before release, use secret G2 HMAC to map anonymous pair IDs into those slots, lock assignment+delivery order; independent check no rater sees both twins, every case has exactly two raters, every rater gets 32 cases. Distribution is 16 SELECT / 16 ABSTAIN per rater and 2/2 per relation family **coordinator-only**, never print it in rater instructions or public packet. Total 128 ratings does not mean 128 independent samples. Four GPT-6 sessions may share systematic biases.
**Blind exposure guard:** Four ChatGPT chats should not be able to browse the shared source repository, this coordinator file, gold, generator, QA, review or other rater packets. Rater is only given their own sanitized 32-case packet plus their role handoff. Do not leak gold in filenames, IDs, order, comments, metadata, source_id, messages or code.

## Packet construction (NONE EXISTS TODAY)
Produce four **distinct** protected files `R8_D_BLIND_PACKET_A.json`, ... `_D.json` and four release-specific SHA256 values; names are planned only. Each consists of 32 case records, each with `opaque_id`, exact `question_text`, `public_index` of 32 cards `{key,text,source_id}`, and a packet-level `schema`, `role` and source-release revision. **Do not include** `gold_action`, `target_card_key`, `answer_key_set`, `proof_sets`, `supported_hypotheses`, `relation_family`, `stratum`, `pair_id`, `twin_id`, `fold_id`, `event_graph_id`, `template_cluster_id`, `allocation`, `notes` or `generator provenance` that encodes answers. Redaction is necessary but insufficient: run independent byte/content scan against private gold and packet overlap.
Four packet sets collectively contain exactly 128 assignments for 64 case IDs; each case twice and each twin delivered to distinct raters. Never publish protected per-rater packets on a public GitHub repository or attach the coordinator allocation table to a blind chat. Do not reconstruct a missing packet from memory or R5/R6/R7.

## Send to four new chats — only when G5 release exists
- Chat A: give only `TTM_VM_V4_R8_BLIND_RATER_A_HANDOFF.md`, approved `R8_D_BLIND_PACKET_A.json`, its actual SHA, and release receipt.
- Chat B: analogous B.
- Chat C: analogous C.
- Chat D: analogous D.
**Today:** Without packet+release, each chat may acknowledge `HOLD_INPUT_NOT_RELEASED` and must NOT output decisions or fabricated scoring hashes.

## Frozen scoring contract (future)
Rater must use only the question and 32 public cards. For each case: `action=SELECT` with exactly ONE `selected_key` from index if precisely one answer record/location is established by visible, applicable, authoritative, temporally valid evidence; otherwise `action=ABSTAIN` and `selected_key=null`. Multiple cards can support one hypothesis; proof card keys can be noted but are not substitutes for target key. An absent premise, competing valid hypotheses, unresolved authority, or ambiguous canonical key => ABSTAIN, no educated guess.
No outside retrieval, cross-chat consultation, access to GitHub source/reviews/other packet, model/generator inspection or unblind. No knowledge of class balance/paired twins should be supplied to rater.

## Output and readback
Each rater independently emits `R8_D_BLIND_SCORES_<ROLE>.json` with:
```json
{
  "schema":"ttm.vm.v4.r8.d.blind_rater_scores.v1",
  "role":"A",
  "reviewer_type":"AI_SELF_ATTESTED_NEW_CHAT",
  "release_receipt_sha256":"ACTUAL_RELEASE_RECEIPT_SHA",
  "input_packet_sha256":"ACTUAL_PACKET_SHA",
  "review_mode":"BLIND_NO_GOLD_NO_CROSS_RATER",
  "records":[
    {"opaque_id":"opaque","action":"SELECT","selected_key":"key_in_public_index","evidence_keys":["other_public_key"],"reason":"one short evidence-grounded note"}
  ],
  "completed_cases":32,
  "unblinded":false
}
```
ABSTAIN uses `selected_key: null`. Use exact 32 unique IDs, not placeholders in final output; record SHA256 of actual UTF-8 bytes and size. Mark `NOT_STARTED`, `HOLD_INPUT_HASH_MISMATCH`, `HOLD_PACKET_LEAKAGE` or `HOLD_INCOMPLETE` honestly if conditions fail. Freeze signed/hashed outputs **before** any gold or mapping reveal. No post-unblind score edits.
Coordinator validates every packet hash, role, 32 IDs, key membership, 128 assignments, no twin exposure, four score SHA and completeness. Compare scores with private gold and compute agreement **only after all four outputs sealed**, under owner-approved unblind rule. Report action agreement; conditional key agreement for both-SELECT decisions with selection caveat; joint exact match; uncertainty clustered by pair/event component, not by 128 ratings. A/B/C/D same-model opinions are not independent human raters.

## Final current status
`HANDOFF_PREPARED_ONLY` · `R8_NOT_GENERATED` · `G0=HOLD` · `G1=HOLD` · `G2=HOLD` · `G3=NOT_AUTHORIZED` · `G4=NOT_EXECUTED` · `G5=SEALED` · `G6=SEALED` · `R7=FROZEN_FAIL` · `THRESHOLD=NOT_FROZEN` · `PROBE256=SEALED` · `READER=0` · `GPU=NO`.
**Next action today:** independent V4 protocol G0 review + owner scope decision; not blind rating.
