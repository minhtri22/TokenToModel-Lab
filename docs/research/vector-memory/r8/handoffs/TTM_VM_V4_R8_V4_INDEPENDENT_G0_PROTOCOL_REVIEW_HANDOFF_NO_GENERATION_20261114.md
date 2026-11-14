# HANDOFF — Independent AI G0 Protocol Reviewer · TTM VM V4 R8 V4
**Operation:** `TTM_VM_V4_R8_V4_DISTINCT_G0_REVIEW_OWNER_SCOPE_AND_SOURCE_QA_SINGLE_GATE_NO_GENERATION`
**Ngày:** 2026-11-14
**Vai trò:** NEW independent AI G0 protocol reviewer — **NOT** any of blind raters A/B/C/D
**Scope:** READ-ONLY · DESIGN-ONLY · NO R8 DATA GENERATION · NO BLIND SCORING
**Pinned scientific design commit:** `b8410d9c1f77a733036e980b567de73c316f8725`
**Sole scientific decision currently valid:** `HOLD_R8_V4_UNREVIEWED_OWNER_SCOPE_RIGHTS_CUSTODY_NO_GENERATION`.

## Mandatory reads (pinned)
1. V4 proposal: https://github.com/minhtri22/TokenToModel-Lab/blob/b8410d9c1f77a733036e980b567de73c316f8725/docs/research/vector-memory/r8/TTM_VM_V4_R8_V4_GOLD_FOLD_ORACLE_RATER_OWNER_SCOPE_SINGLE_PACKET_DESIGN_ONLY_20261114.md
2. O1–O8 / 4-rater machine-readable contract: https://github.com/minhtri22/TokenToModel-Lab/blob/b8410d9c1f77a733036e980b567de73c316f8725/docs/research/vector-memory/r8/R8_V4_RESTRICTED_ORACLE_AND_RATER_CONTRACT_DESIGN_ONLY.json
3. Read-only schema checker (source only; not an executed oracle suite): https://github.com/minhtri22/TokenToModel-Lab/blob/b8410d9c1f77a733036e980b567de73c316f8725/docs/research/vector-memory/r8/R8_V4_DESIGN_CONTRACT_STATIC_CHECK.py
4. Owner choice is blank: https://github.com/minhtri22/TokenToModel-Lab/blob/b8410d9c1f77a733036e980b567de73c316f8725/docs/research/vector-memory/r8/R8_V4_OWNER_SCOPE_AND_RATER_SELECTION_PENDING.json
5. Formal V4 HOLD: https://github.com/minhtri22/TokenToModel-Lab/blob/b8410d9c1f77a733036e980b567de73c316f8725/docs/research/vector-memory/r8/TTM_VM_V4_R8_V4_SINGLE_PACKET_DESIGN_ONLY_ADJUDICATION_20261114.json
6. Independent V3 review (background; do not mutate): https://github.com/minhtri22/TokenToModel-Lab/blob/b8410d9c1f77a733036e980b567de73c316f8725/docs/research/vector-memory/r8/reviews/TTM_VM_V4_R8_V3_INDEPENDENT_PROTOCOL_REVIEW_20261114.md

## Explicit distinction from blind rating
Four blind raters A/B/C/D have already acknowledged `HOLD_INPUT_NOT_RELEASED` per owner relay; there are **NO approved R8 packets, SHA pins, or release receipts**. They are not the correct agents to perform this source protocol review. Do not send any of the six above links, especially gold-related schema / allocation, to those chats. Reviewer for this handoff is allowed to see design docs, but not private gold and is NOT an authorized custodian or owner.

## Questions to adjudicate separately with PASS/HOLD/FAIL, reasons & exact source references
### B01 — answer hypothesis / F07
- Does the tuple (record, accession, event, location, effective time, authority policy) eliminate the mistaken inference that one entity means a unique answer?
- Does a minimal sufficient proof set establish all necessary premises, and are defeaters, duplicate answer keys, explicit negative evidence and ABSTAIN taxonomy fully deterministic?
- Under proposed synthetic policy P-REC-V1, does the symbolic F07 SELECT/ABSTAIN pair truly change *only* the decisive authoritative graph relation without a new lexical oracle? Is domain policy owner adoption clearly left pending?
- Can the proposed one-key scorer represent the gold without ambiguity? State missing formal or validator contracts.

### B03 — fold graph and four raters
- Are pre-G3 blueprint edges frozen without using future generated texts, and is post-G3 similarity checking logically sound? Is a new post edge across folds treated as CV invalid, with no reselection?
- Are event_graph_id, component_id_pre, component_id_post unambiguous? Are component count, held-out class availability and pair/twin isolation handled?
- Verify four-rater assignment (32 pairs across 8 families, 64 cases, 128 ratings). Check that every case has two raters, none sees both twins, each A/B/C/D receives 32 cases with 16 SELECT and 16 ABSTAIN. Flag any overlooked selection/overlap leak or impossible blinding requirement.
- Explicitly distinguish 128 ratings from independent sample size, and whether GPT-6 sessions count as truly distinct human raters (they do not).

### B04 — restricted O1–O8
- Assess O1–O8 contract completeness against the executable-source requirement. A JSON parameter register plus a structural checker is NOT a full implemented oracle suite, and must not be marked executed.
- Check key-selection O5: TRAIN-only cases, per-card weighting (positive 1/2 and each negative 1/62), tie rule, held-out component constraint; chance baseline 1/32; combined O6 scoring semantics and Holm family (O2/O3/O4/O5/O6) with first cutoff 0.01.
- Identify ambiguity/invalid assumptions in feature vectors, source metadata, preprocessing, group splits, null exchangeability, Python/scikit-learn versions, regex assets and exact reproducibility. G2 cannot be declared PASS until code/versions/receipts are pinned and separately verified.

### B05 — scope and inferential validity
- Is `R8-D EXPLORATORY_DESCRIPTIVE_ONLY` clearly distinct from a confirmatory R8-C objective?
- Does `PASS_SCOPED_DESCRIPTIVE_QA` mean QA-complete only, never absence-of-shortcut proof or authorization of scientific threshold?
- Does `NOT_ESTIMABLE` prevent invalid significance/power inferences when there are <=32 pair units and possibly fewer independent components?
- Do not claim confidence intervals/p-values or independent scientific outcomes from **unexecuted** R8 data.

### B02 and B06 (inherited scoped findings)
Confirm V4 does not regress paired-question 50% tautology treatment (B02) or prospective AI-authored source / private custody policy (B06). A scoped PASS on policy is NOT G1 owner/rights attestation or G2 byte custody.

## Output — independent frozen source review
Create an evidence file `TTM_VM_V4_R8_V4_INDEPENDENT_G0_REVIEW.json`, with reviewer type `AI_SELF_ATTESTED_DISTINCT_CHAT`, source commit, each B01/B03/B04/B05 verdict and supporting reason, B02/B06 continuity checks, overall `PASS_G0_DESIGN_ONLY` or `HOLD_G0` or `FAIL_G0`, explicit reasons. The reviewer must include unresolved issues, limits and a verifiable SHA-256 of the final saved bytes. The reviewer may create its own file but must NOT sign owner adoption, change protocol, generate R8, or give blind raters any input.

**Global gate rule:** G0 PASS for *design* only if there are no blocking design findings; even if PASS, G1 owner decision + rights, G2 private custodian/validator/source-code lock, G3 actual generation, G4 independent content/anti-shortcut QA and G5 explicit release remain separate. In current facts **R8=NOT_GENERATED**, G0=HOLD, G1/G2=HOLD, G5=SEALED, PROBE256=SEALED, Reader=0, GPU=NO.

## Next action
Owner sends THIS handoff only to a **new source-review chat**; not to existing four blind rater chats. Return completed G0 review and file SHA for integrated adjudication. Do not ask four blind raters to score while waiting.