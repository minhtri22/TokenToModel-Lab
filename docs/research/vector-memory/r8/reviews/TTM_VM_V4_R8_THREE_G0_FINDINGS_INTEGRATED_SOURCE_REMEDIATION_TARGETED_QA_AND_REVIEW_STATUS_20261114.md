# TTM Vector Memory V4 R8 — Three G0 Findings: Integrated Source Remediation and Targeted QA

**Date:** 2026-11-14  
**Operation:** `TTM_VM_V4_R8_FINAL_G0_THREE_FINDINGS_INTEGRATED_SOURCE_REMEDIATION_AND_TARGETED_NEGATIVE_QA`  
**Repository:** `minhtri22/TokenToModel-Lab`  
**Classification:** `IMPLEMENTATION_AGENT_TARGETED_SOURCE_QA` — **NOT** `DISTINCT_INDEPENDENT_G0_REVIEW`.  
**Global adjudication:** `HOLD_INTEGRATED`. No R8 candidate release authorized.

## Frozen input and retained evidence

- V4 scientific design `b8410d9c1f77a733036e980b567de73c316f8725`; do not modify.
- Previous targeted source commit `57a80009428c0974c2d262a06f2b028908960ac1`, focused CI [43585885329](https://github.com/minhtri22/TokenToModel-Lab/actions/runs/43585885329) `25/25 PASS`. Prior historical `37/37 PASS` at `cf38f8792253fe106cbb6a641f189882fb96e9d5`, CI [43573016701](https://github.com/minhtri22/TokenToModel-Lab/actions/runs/43573016701). **Neither prior suite was rerun or claimed to certify the new source SHA.**
- Independent AI G0/G2 review `62542b6db216a021f84aa8495f40794fb82097d4`: `docs/research/vector-memory/r8/reviews/G0_G2_FINAL_INDEPENDENT_READBACK_AND_ADJUDICATION.md`. It reported three blockers: (i) unused unverified claim dependencies could enlarge a supposedly minimal proof, (ii) F07 unrelated-event negative receipt could defeat a valid target event, (iii) non-R8 small manifest could pass fold primitives without an executable R8 size guard. G2 private sentinel/ACL/runtime preflight `PASS_SCOPED` in that independent report; the same reviewer made no claim of actual R8 gold custody.
- Standing owner research direction `097e046bb0f6525665dde03ec5fcdf8134a8e762`; R8-D exploratory synthetic only. No repeat owner GO.

## One batch of source changes

**Remediation source commit:** `98fec8442f38819731405c3f938ffbdf42cee311`. 
**CI YAML-only correction commit:** `5334833179895048bb19eab645fe8c06b9ca4fd0`. It changed only the workflow step-name quoting; Python source bytes are identical to remediation commit. Both commits are on `evidence/ttm-vm-v4-r8-g0-f01-f03-single-closure-20261114`.

1. **G0-PROOF-MINIMALITY:** In `integrated_closure/gold_contract.py` the CORE proof enumeration now selects actual verified **claim objects**, not only source-card keys. The dependency closure starts with the dependencies of selected claims and expands alternative verified support on dependent cards, then retains minimal card sets. Unverified or unrelated claims on the same card no longer add irrelevant dependency cards to a sufficient proof. Global circular/missing-dependency validation, equal-authority conflict rejection and one-key SELECT contract remain implemented. New tests cover irrelevant unverified dependency, needed verified dependency, alternate verified support and transitive verified dependency.
2. **G0-F07-EVENT-SCOPE:** In `gold_contract.receipt_f07`, an authorized negative receipt requires `negates_accession` **and** `link_event` to equal the hypothesis accession/event. Unrelated or absent event links do not defeat it. New tests check same-event defeat, unrelated-event non-defeat and missing-event non-defeat.
3. **G0-B03-PRODUCTION-MANIFEST:** In `integrated_closure/folds_raters.py`, added strict public-callable gateways `validate_r8_blueprint_manifest`, `validate_r8_case_manifest`, `preassign_r8`, `postcheck_r8`. They enforce **32 unique pair blueprints / eight relation families × four pairs, 64 distinct cases / one SELECT and one ABSTAIN twin for each blueprint, 32 unique-key cards per case, legal target-key semantics, and an existing complete four-fold preassignment**. Invalid/truncated data fail closed before CV or HMAC allocation, with no re-partition rescue. Original `preassign` and `postcheck` remain low-level source-fixture primitives; **future actual R8 generation/checking integration must route through the new strict gateways**, not primitive APIs. New tests exercise short blueprints, bad family balance, short cases, twin/action mismatch, bad card count, duplicate IDs, missing locked folds and an exact-size **synthetic non-R8** positive witness. No R8 data or HMAC secret was generated.

## Focused CI / actual byte provenance

- First workflow attempt [43590245642](https://github.com/minhtri22/TokenToModel-Lab/actions/runs/43590245642) failed validation before creating jobs because a YAML step name contained an unquoted colon. **Not a test failure.** The next workflow-only commit quoted the name. The failure remains visible in history, not suppressed.
- Final [GitHub Actions run 43590325992](https://github.com/minhtri22/TokenToModel-Lab/actions/runs/43590325992): `completed/success`, **exact head SHA = `5334833179895048bb19eab645fe8c06b9ca4fd0`**; job `changed-contract-only` SUCCESS, CPython 3.12.16 Linux. `15/15` new symbolic negative/positive-guard tests PASS (`test_g0_final_three_findings.py`), 0 historical tests rerun, no R8/TEST/Reader/GPU/PROBE256. Symbolic test-count is not a scientific sample size.
- CI raw source SHA-256 lock:
  - `integrated_closure/gold_contract.py` = `8e8b81ce2d0bc47cc60c29abc7156fe9d97613e67983e43b7f587615d68015a5`
  - `integrated_closure/folds_raters.py` = `fa48364561fd19a2caa2095ce3ac4cb5f711817b8dac2db1b929fd193196dc91`
  - `integrated_closure/test_g0_final_three_findings.py` = `e66ca4694625d597528e6b6f018e3be71ffbd0b1ab3439e27b95a442368c7bc9`
- `integrated_closure/restricted_oracles.py` remains unchanged at SHA-256 `34ab74d36b822703e4d8cbdf281e142273d55d181243d904b55fd31a0e6382a1` from [43585885329](https://github.com/minhtri22/TokenToModel-Lab/actions/runs/43585885329).
- All source SHA values above are **public CI source readbacks**, not independently re-attested private Windows file SHA values.

## G0 independent ratification — STILL OUTSTANDING

The same source-writing agent authored the changes and targeted tests. Therefore `G0=HOLD_PENDING_DISTINCT_INDEPENDENT_READBACK`, not `PASS`. The distinct reviewer must read actual source at **`5334833179895048bb19eab645fe8c06b9ca4fd0`** and compare with the three counterexamples in independent report `62542b6...`, inspect proof minimality/negative event scoping and ensure the **production API is actually enforced** by future R8 caller; mere presence of strict wrappers does not demonstrate that the caller uses them. The reviewer can reject claims or HOLD with specific new witnesses; no auto-V5/V6, no self-signing or rerunning unchanged historical suites.

## G2 scoped custody reuse and source-lock rebind

The separate independent report `62542b6...` describes **actual Windows sentinel** (54 harmless bytes, two processes, SHA-256 `0d880e2bed5f88f3578728fcde67b9dde341419244ba7006cf94146667cf1652`, ACL/DACL check and isolated Python 3.12.10 / NumPy 2.3.5 / SciPy 1.17.0 / scikit-learn 1.8.0). This is a scoped private preflight receipt and **need not be repeated solely due to a new GitHub source commit**, provided the same storage identity, access controls and retention boundaries remain valid.

**BUT** the previous G2 readback locked older source SHA values. The updated `gold_contract.py` and `folds_raters.py` SHA-256 in this report must be independently read back on the actual private runtime/source mount by an authorized custodian (exact source-lock rebind). Source hashes from CI alone do not prove private custodian source identity. Future HMAC key procedure is prospective; no HMAC secret, actual R8 gold, candidate or blind key map has been materialized or verified. Until rebind completes, `G2=PASS_SCOPED_STORAGE_PREFLIGHT_REPORTED; SOURCE_LOCK_REBIND_NOT_VERIFIED`.

## Overall state and one remaining independent verification

- `SOURCE_IMPLEMENTATION_TARGETED_QA=PASS_15_OF_15`; `G0=HOLD_DISTINCT_REVIEW_REQUIRED`; `G1=OWNER_STANDING_RESEARCH_DIRECTION_RECORDED`; `G2=STORAGE_PREFLIGHT_PASS_REPORTED_SOURCE_LOCK_REBIND_PENDING`; `DECISION=HOLD_INTEGRATED`.
- `R7=FROZEN_FAIL`, `R8=NOT_GENERATED`, `G3/G4=NOT_EXECUTED`, `G5/G6=SEALED`, `READER=0`, `GPU=NO`, `PROBE256=SEALED`.
- **One final independent check, no new handoff:** a reviewer **different from the implementation agent** verifies the three source corrections and their exact SHA, and the authorized custodian rebonds the two changed source files under the existing protected G2 scope. One integrated GO/HOLD verdict is rendered only after this evidence. No further owner GO request for the same synthetic exploratory scope, no historical QA reruns, no new blind-rater session.
