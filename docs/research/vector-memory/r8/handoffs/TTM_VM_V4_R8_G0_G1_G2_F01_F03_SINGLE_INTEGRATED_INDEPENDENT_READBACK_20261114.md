# HANDOFF — TTM Vector Memory V4 R8 · G0–G2 One-Packet Independent Readback

**Operation:** `TTM_VM_V4_R8_G0_G1_G2_F01_F03_SINGLE_INTEGRATED_INDEPENDENT_READBACK_NO_GENERATION`  
**Date:** 2026-11-14  
**Mode:** `READ_ONLY_SCIENCE` · `NO_R8_GENERATION` · `NO_TEST` · `NO_READER` · `NO_GPU` · `NO_PROBE256`  
**Role:** Distinct independent AI source reviewer, collaborating with a REAL authorized owner and private custodian **only for their own attestations**. Reviewer is **not** owner or custodian by declaration.
**Required outcome:** ONE `GO_R8_D_CANDIDATE_AUTHORING_ONLY` or `HOLD_INTEGRATED` decision, with evidence for G0/G1/G2. **No V5/V6, micro-permits or additional handoff loops.**

## 1. Source-of-truth pins; no repeated historical QA
Repository: `minhtri22/TokenToModel-Lab`.
- Scientific V4 prereg draft: `b8410d9c1f77a733036e980b567de73c316f8725`.
- Initial integrated source+QA report: `3a12aede5d738aa0a91d6a0d5f68869000efc097`, 29/29 symbolic PASS.
- First remediation source: `cf38f8792253fe106cbb6a641f189882fb96e9d5`, GitHub Actions [43573016701](https://github.com/minhtri22/TokenToModel-Lab/actions/runs/43573016701) 37/37 PASS, `SAME_AGENT_SEPARATE_CHECKER`, Ubuntu Python 3.12.16 and sklearn 1.8.0. **Historical receipt stays pinned to that SHA**, not transferred by assumption to later edits.
- Independent AI G0-G2 reviewer HOLD report (source not modified): `53c987be529fc6342006d678116180fc6be72a62`, file `docs/research/vector-memory/r8/reviews/TTM_VM_V4_R8_G0_G1_G2_INTEGRATED_READBACK_AND_ADJUDICATION.md`; reviewer found G0-F01 O1 metadata boundary, G0-F02 proof INVALID vs ABSTAIN, G0-F03 unbounded marker-adjacent ngrams.
- **Second, focused source correction:** commit **`1495c42f589b5150e0f941d662846b2dde6b3a31`** on branch `evidence/ttm-vm-v4-r8-g0-f01-f03-single-closure-20261114`.
- **Focused GitHub Actions:** [43574946922](https://github.com/minhtri22/TokenToModel-Lab/actions/runs/43574946922), `SUCCESS` with head SHA = correction commit, Python 3.12.16, **12 new focused regressions + two updated historical affected assertions = 14/14 PASS**. This did **not** rerun the original 37 tests. Current scope `SAME_AGENT_SEPARATE_CHECKER_NON_R8`, NOT independent G0 or R8 scientific QA; no Windows execution.
- Corrected SHA-256 from focused CI:
  - `integrated_closure/gold_contract.py`: `17fc44ce356e6b8bf70bf350a0082774613b53a40261bf817d17cdbe98facef5`
  - `integrated_closure/restricted_oracles.py`: `afde600811a27755dc7003f6eb317716def2446f8d746125e92826d8bded251f`
  - `integrated_closure/test_integrated_source_only.py`: `e4402b825eba932c6ae5a0e3054a1cafe85d835c645be7d80df2a6b10c3f811f`
  - `integrated_closure/test_g0_f01_f03_targeted.py`: `dd484860ef940225cb18c21cc68af654d6ca85d62b7f565c793f85f453956f7b`
  - `folds_raters.py` unchanged from first remediation CI: `7f2cfd23252a86354b91383351cea7ccede987c2daba80d6b6649f6bdcb9e853`.

## 2. Specific remediation completed — reviewer MUST inspect actual source
At fixed correction commit, inspect the exact Python source, V4 scientific contract and test source:
- **G0-F01 / O1 order-only:** `restricted_oracles._o1_features` now reports `row_position_decile`, `card_count`, `first_card_position`, `last_card_position`, **not** key lengths or source text. O2 still tests key/source/ordering metadata separately. New targeted tests assert exact O1 feature allowlist and invariance when first/last card keys change.
- **G0-F02 / B01 proof invalidity:** `gold_contract._validate_claim_dependencies` checks declared proof graph for cycles and missing references, raises `INVALID_FIXTURE_CIRCULAR_PROOF` or `INVALID_FIXTURE_MISSING_PROOF_DEPENDENCY`. `gold_contract.resolve` raises `INVALID_FIXTURE_EQUAL_AUTHORITY_CONFLICT` when a verified, time-valid conflicting proof has equal rank. These **are no longer ABSTAIN**. Valid ordinary missing `AUTHORIZED` remains `ABSTAIN/MISSING_PREMISE`; superior negative evidence remains ABSTAIN. Historical `test_08` and `test_10` updated to validate new semantics, and selectively retested. Any further source/contract contradictions must be reported precisely, not fixed post hoc during purported independent review.
- **G0-F03 / O3 restricted marker-only:** `restricted_oracles._o3_features` only emits markergram 1/2-grams whose constituent lexemes belong to the frozen `MARKERS` lexicon, so `signed accession_x` and `authorized proof_42` do not become arbitrary vocabulary features. Known marker bigrams (`applicable signed`, `signed record`) remain. Independent reviewer should check whether all status/authority/source-format fields are still within intended O3 boundary. No observed R8 leakage claim: R8 data do not exist.
- **B03 prior fix:** `folds_raters.postcheck` uses actual `case_id` for 64-case G_post; preserves two twins to each G_pre blueprint, no repartition. Unchanged from 37/37 receipt.
- **B04 other controls:** O2–O8 incl TRAIN-only O5, group holdout and Holm retain prior behavior except explicitly listed O3 adjustment. Only **changed behaviors** were retested. A targeted PASS is not blanket 37/37 on the new commit.
- **B05:** R8-D `EXPLORATORY_DESCRIPTIVE_ONLY`; no "lack of leakage proven"; R8-C confirmatory 32-pair route NO-GO.

## 3. G0 exact distinct independent source/protocol decision
A different agent must verify, using source and code-level arguments, **all three F01/F02/F03** plus no regression against B01/B03/B04/B05. Cite precise functions and test names/lines. Optionally run **only** a bounded independent negative test for a newly identified substantive issue; do not repeat old 37 or regenerate data. Distinguish this new review from prior 14/14 same-agent QA. Return either `G0=PASS_INDEPENDENT_SOURCE_PROTOCOL_SCOPED` or `G0=HOLD`. A G0 PASS is only a design/source readback, not owner authorization or actual R8 QA.

## 4. G1 — ONE owner decision (not the reviewer)
The owner must provide **one authenticated approval or rejection covering all four dimensions**:
1. Scientific scope: `ADOPT_R8_D_DESCRIPTIVE_ONLY` or `RETAIN_CONFIRMATORY_OBJECTIVE_NO_GO`.
2. Proposed rater setup: `FOUR_RATERS_TWO_PER_CASE` (2 ratings per 64 cases, 128 total; no reviewer sees both twins) OR `TWO_RATERS_DISJOINT`.
3. Approve/reject toy synthetic policy `P-REC-V1` and one-key target SELECT/ABSTAIN contract.
4. Approve/reject `AI_AUTHORED_SYNTHETIC_EXPLORATORY_ONLY` source rights and PII/privacy controls for future one-shot candidate authoring, including version/scope/authority/date/provenance.
The packet `integrated_closure/OWNER_RIGHTS_CUSTODY_DECISION_PACKET_PENDING.json` is a template, not approval. **No AI can claim to sign for the owner.** Owner may reply in one consolidated decision; reviewer can only verify actual attributable receipt. Without it `G1=HOLD_OWNER_NOT_ATTESTED`.

## 5. G2 — ONE real private custodian readiness attestation
Authorized custodian must attest actual private location (kept PRIVATE), ACL/access controls, permitted read/write/readback of an explicitly authorized **non-R8 sentinel**, SHA-256 readback, retention/access/HMAC secret policy, independent protected source-lock with exact corrected SHA-256/runtime/validator. Nothing secret/raw private is committed or pasted into public GitHub.
**R8=NOT_GENERATED**: do NOT demand or fabricate an actual R8 gold-byte SHA at G2. Real R8 gold/proof/packet byte custody is **post-generation**, needed later before G4/G5. If custodian lacks authorized access or real receipts are absent, `G2=HOLD_PRIVATE_CUSTODY_NOT_VERIFIED`. A source SHA alone is not private-storage proof.

## 6. One final adjudication, not another chain
Report ONLY after evaluating available G0/G1/G2 evidence. One overall verdict:
- `GO_R8_D_CANDIDATE_AUTHORING_ONLY` iff `G0=PASS`, `G1=PASS` (R8-D explicit owner adoption and rights/PII), and `G2=PASS` (real authorized private preflight/source-lock), no new substantive defect. GO scopes **a separately authorized future one-shot exploratory R8 authoring**, not automatic generation or science release.
- `HOLD_INTEGRATED` otherwise, with a consolidated final missing-evidence set; no micro-permit or V5/V6 cycle. If owner wants R8-C confirmatory, current 32-pair plan remains NO-GO.
- Always `R7=FROZEN_FAIL`, `R8=NOT_GENERATED`, `G3/G4=NOT_EXECUTED`, `G5/G6=SEALED`, `Reader=0`, `GPU=NO`, `PROBE256=SEALED`.

**Output expectation:** one compact public-safe independent readback/adjudication report with fixed commit/CI/SHA references and one final GO/HOLD. If reviewer can write GitHub, create **one** new evidence file at a non-secret path and pin its resulting commit; no extra handoff or empty interim receipts. If G1/G2 absent, explicitly record HOLD, do not purport to manufacture them. No new blind rater chats: prior chats are closed.
