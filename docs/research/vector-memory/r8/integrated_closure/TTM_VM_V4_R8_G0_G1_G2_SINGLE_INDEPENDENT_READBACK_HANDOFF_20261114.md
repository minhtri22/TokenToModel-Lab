# HANDOFF — TTM VM V4 R8: G0–G2 Integrated Independent Readback / Single Gate

**Operation:** `TTM_VM_V4_R8_G0_G1_G2_SINGLE_INDEPENDENT_READBACK_AND_OWNER_CUSTODY_ADJUDICATION_NO_GENERATION`  
**Date:** 2026-11-14  
**Role:** NEW independent AI protocol/source reviewer and evidence adjudicator, distinct from author/implementation agent. The reviewer is **not** the owner, not a private custodian by assertion and not a blind rater.
**Mode:** READ-ONLY scientific corpus; source/protocol review and private-storage readiness attestation ONLY if authorized. **DO NOT GENERATE R8**, alter R5/R6/R7, run Reader/GPU/TEST/PROBE256, release blind packets or create new rater chats.
**Task:** Reuse the already-PASS 29/29 source QA. Resolve the **three remaining evidence groups** in one packet; one final decision `GO_R8_D_CANDIDATE_AUTHORING_ONLY` or `HOLD_INTEGRATED`. No V5/V6, micro-permits, repeated QA, or new design iteration unless an actual material defect is identified.

## Exact immutable inputs — GitHub source of truth
Repository `minhtri22/TokenToModel-Lab`.
- **V4 scientific design commit** `b8410d9c1f77a733036e980b567de73c316f8725`.
- **Integrated source/evidence commit** `3a12aede5d738aa0a91d6a0d5f68869000efc097`.
- Source branch (mutable navigation ONLY): `evidence/ttm-vm-v4-r8-v4-integrated-closure-20261114`. All review references MUST use the pinned commit above, not branch HEAD.
- Main integrated report: `docs/research/vector-memory/r8/integrated_closure/TTM_VM_V4_R8_V4_INTEGRATED_SINGLE_GATE_REPORT.md`.
- Owner+custody PENDING packet: `docs/research/vector-memory/r8/integrated_closure/OWNER_RIGHTS_CUSTODY_DECISION_PACKET_PENDING.json`.
- Required executable source: `docs/research/vector-memory/r8/integrated_closure/gold_contract.py`, `folds_raters.py`, `restricted_oracles.py`, `test_integrated_source_only.py`.
- Design contracts at scientific commit: `docs/research/vector-memory/r8/TTM_VM_V4_R8_V4_GOLD_FOLD_ORACLE_RATER_OWNER_SCOPE_SINGLE_PACKET_DESIGN_ONLY_20261114.md`, `R8_V4_RESTRICTED_ORACLE_AND_RATER_CONTRACT_DESIGN_ONLY.json`, `R8_V4_OWNER_SCOPE_AND_RATER_SELECTION_PENDING.json`.
- Original V3 independent AI review at the pinned V4 scientific commit: `docs/research/vector-memory/r8/reviews/TTM_VM_V4_R8_V3_INDEPENDENT_PROTOCOL_REVIEW_20261114.md`. This is NOT a V4 independent review.

**Previously completed CI — preserve, do NOT rerun unless actual source/hash drift:** GitHub Actions [run 43570722316](https://github.com/minhtri22/TokenToModel-Lab/actions/runs/43570722316), `SUCCESS`, head SHA = integrated source/evidence commit, CPython 3.12.16, scikit-learn 1.8.0, NumPy 2.3.5, SciPy 1.17.0, 29/29 non-R8 symbolic tests PASS. Classification `SAME_AGENT_SEPARATE_CHECKER` (not independent external review). CI SHA-256 source readbacks:
| Source | SHA-256 |
|---|---|
| gold_contract.py | `a359758b97f6426629cc30293e74882f27a65ca13b887f65bd5ae7ab2cdaadde` |
| folds_raters.py | `04171d35704b9e48a59a5f64175703ed9acaf88eedbf64f3752ef350070d9d86` |
| restricted_oracles.py | `57f94f323b954e60659abea552d91795c5b8b07a060565b6ca096198156c45f8` |
| test_integrated_source_only.py | `5b914840bbd76565516d798c9cbcb06a0a2374f8879c7ba1f4f0fb4ff7c871ee` |
| regex pattern literal | `ffdfc06eb76bebd35e1f6185fafd4525d244149d7f64838bbe1f688ddf406d2e` |

## G0 — Distinct independent protocol + exact-source QA (agent's assigned responsibility)
Read actual source, V4 design, original reviewer findings and source QA report at pins. This is **independent readback**, not blind scoring. Do NOT merely repeat assertions of the implementing agent.
- **B01 Gold/F07:** inspect one-key answer-hypothesis ontology, minimal sufficient proof, authority precedence/defeaters, equal-authority conflicts, circular support, multiple hypotheses for same record but different location, duplicate target keys, negative evidence and abstention. Verify the toy P-REC-V1 symbolic F07 SELECT/ABSTAIN pair differs by authorized relation rather than a label-predictive status word. Owner domain-policy approval remains G1. Distinguish logical source validation from attestation of private real gold; latter not possible before R8 exists.
- **B03 Fold/rater:** inspect G_pre blueprint-only connected components, G_post Jaccard 5-gram >=0.80 plus exact-duplicate handling and cross-fold invalidation with NO post hoc re-split. Verify component IDs, HMAC assignment and a four-rater **proposal** with 64 cases, 128 future ratings, 32 cases/each, 16 SELECT/16 ABSTAIN/each and no twin exposure. No actual allocation key, rater or packet yet. Report leakage/independence limits accurately.
- **B04 O1–O8/O5:** inspect actual restricted_oracles.py code against design contract, TRAIN/test component isolation, O5 positive weight .5 and each negative .5/31, 1/32 SELECT key-null, O6 action+key/joint, O8 known R7 marker *fixture regression* only, Holm O2/O3/O4/O5/O6 at FWER .05 first .01, invalid permutation => NOT_ESTIMABLE. Verify no answer leakage through test action, TRAIN-only vocabulary where required and single-class/error behavior. Check that O7 semantic lexical baseline is not declared forbidden leakage by accuracy alone. **No full 29/29 rerun without source drift.** Optional bounded, targeted independent negative source/proof tests ONLY if a concrete coverage gap is documented; do not tune or regenerate R8.
- **B02, B05, B06 continuity:** question-only twin 50% is tautology, not anti-shortcut PASS; R8-D descriptive only cannot claim leakage absent, R8-C confirmatory remains NO-GO; synthetic source rights/PII policy is not an owner attestation.
- Return G0 `PASS_INDEPENDENT_DESIGN_SOURCE_SCOPED` or `HOLD` with exact lines/code symbols and evidence. **Review independence classification must be truthful** (new AI reviewer distinct from the implementing agent, but not an external human reviewer). If a source defect is discovered, do not hotfix and relabel independent review PASS in the same trace; report HOLD and precise defect.

## G1 — Owner decision & source rights (must be owner-attested, NEVER agent-autosigned)
Obtain or examine an **explicit authenticated owner decision** for all in ONE response/record; if absent leave every field pending:
1. Scientific objective: `ADOPT_R8_D_DESCRIPTIVE_ONLY` OR `RETAIN_CONFIRMATORY_OBJECTIVE_NO_GO`.
2. Proposed blind rater design: `FOUR_RATERS_TWO_PER_CASE` OR `TWO_RATERS_DISJOINT` (if R8-D approved). Former is recommended but NOT silently adopted.
3. Approval/rejection of synthetic toy authority policy `P-REC-V1` and one-key SELECT/ABSTAIN scoring semantics.
4. Authorization for source class `AI_AUTHORED_SYNTHETIC_EXPLORATORY_ONLY`, rights/license provenance and PII/privacy handling as applicable, including permitted future one-shot source generation. **Owner adoption does not automatically authorize real-science/threshold/TEST.**
Evidence must include scope, version, date, authority, source URI/record, PASS/HOLD and any caveats. A chatbot's speculation about owner preference is NOT approval. The implementing agent is not the owner. If owner cannot be reached, **G1=HOLD_OWNER_DECISION_RIGHTS_NOT_ATTESTED**, with one bundled owner decision request at closeout, not serial micro-permits.

## G2 — Private storage / source-lock readiness (avoid impossible pre-generation gold gate)
**R8 does not yet exist. Do NOT demand an R8 gold-byte SHA/readback before G3.** G2 is for **pre-generation infrastructure/source/private-custody readiness**, not post-generation real gold validation:
- Distinct authorized private custodian verifies actual private storage location, ACL/permissions, read/write/readback *on a non-R8 sentinel* or preexisting approved private fixture, canonical byte SHA-256 and controlled deletion/retention; use only approved scope. No arbitrary local filesystem write without authorization.
- Record secure handling of future R8 private proof/gold, sealed HMAC allocation key policy and independent access readback without publishing private paths, secret values, gold, paired mapping, or label-coded commitments. If a private key is generated for a permitted preflight, it must be stored and attested by custodian; don't send it in chat or public GitHub.
- Verify executable source / environment exactly against CI SHA-256 and the V4 schema, independent one-key validator source/readback, fixed seed, regex, 4-fold algorithm, scorer and branch frozen at verified commit. A source SHA pin alone is NOT a proof of private storage.
- After future authorized G3 generation, a **new actual R8 private candidate receipt** must hash and verify real candidate, private gold, proof manifest, allocation mapping and public packet redaction **before** G4/G5. Do not mark real-gold custody PASS from sentinel.
- If custodian is not connected/authorized, output `G2=HOLD_PRIVATE_CUSTODIAN_READBACK_NOT_VERIFIED`; do not fabricate a receipt or claim the public GitHub repo holds private gold.
- Even if source QA passes, G2 needs genuinely independent/private authorized custody, not a self-issued assertion.

## Exactly one integrated adjudication
Source QA is already `PASS_29/29_SCOPED_NON_R8`. No new generation, no repeat of unchanged test/CI.
Final gate matrix:
- `G0`: independent design/source PASS or HOLD with B01/B03/B04 specific readback.
- `G1`: owner decision, rater mode, P-REC-V1 and rights/PII PASS or HOLD.
- `G2`: private storage preflight, ACL/readback, source-lock PASS or HOLD.
- `G3`: `NOT_EXECUTED`; `G4=NOT_EXECUTED`; `G5/G6=SEALED`; `R7=FROZEN_FAIL`; `R8=NOT_GENERATED`; `READER=0`; `GPU=NO`; `PROBE256=SEALED`.
**Single overall decision**:
- `GO_R8_D_CANDIDATE_AUTHORING_ONLY` **iff** G0=PASS, G1=PASS with `ADOPT_R8_D_DESCRIPTIVE_ONLY` and authorized one-shot, G2=PASS readiness with independently verifiable custody and no unresolved hard blocker. **GO is scoped only to future one-shot exploratory R8 candidate authoring**, never automatic R8 generation, gold validity, blind scoring, Reader, CAL threshold or PROBE.
- Otherwise `HOLD_INTEGRATED` and return the smallest **ONE-PACKET** list of missing evidence, with roles owner/reviewer/custodian and direct sources. If owner chooses confirmatory R8-C => `NO_GO` for current 32-pair candidate and global `HOLD_INTEGRATED`.
- No "GO because GitHub Actions passed"; 29/29 source QA cannot substitute G0/G1/G2.

## Outputs — one report, one GitHub evidence write at most
Prepare **one** `TTM_VM_V4_R8_G0_G1_G2_INTEGRATED_READBACK_AND_ADJUDICATION.md` containing pinned source checks, independent findings with status, owner and private custodian receipt references (or explicit missing), G0/G1/G2 verdict and global GO/HOLD. If permitted, commit only public-safe report to a **new path** on the existing evidence branch (not altering frozen pinned inputs), read back the resulting commit. Keep owner PII/signature, private path, allocation secret and raw gold in private storage. If GitHub unavailable, supply public-safe report as prose and say persistence failed. No extra handoffs, branches, review cycles or test reruns.
**Response to owner:** concise GO/HOLD, exact GitHub evidence link, and *one* consolidated next action. Do NOT give the four blind raters a packet. They were previously closed; do not reopen.
