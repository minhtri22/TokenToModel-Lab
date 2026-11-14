# TTM Vector Memory V4 R8 — B03 Family/HMAC/Production-Caller Integrated Closure

**Operation:** `TTM_VM_V4_R8_B03_FAMILY_ENUM_HMAC_GPRE_PRODUCTION_CALLER_AND_G2_SOURCE_LOCK_SINGLE_GATE`  
**Date:** 2026-11-14 (Asia/Bangkok)  
**Repository:** `minhtri22/TokenToModel-Lab`  
**Evidence type:** `IMPLEMENTATION_AGENT_SOURCE_QA_WITH_CUSTODY_ACCESS_ATTEMPT`, NOT an independent source review and NOT a private custodian attestation.  
**Formal integrated decision:** `HOLD_INTEGRATED`. `GO_R8_D_CANDIDATE_AUTHORING_ONLY=NOT_AUTHORIZED`.

## Reviewed evidence and immutable references

- Prior independent G0/G2 adjudication at **`12540962e96caef34c587e7a8ba59d58fd09c5c4`**: [read exact report](https://github.com/minhtri22/TokenToModel-Lab/blob/12540962e96caef34c587e7a8ba59d58fd09c5c4/docs/research/vector-memory/r8/reviews/TTM_VM_V4_R8_FINAL_INDEPENDENT_G0_G2_ADJUDICATION.md). Reviewed scope: F01 minimal proof PASS_SCOPED; F02 F07 event scoping PASS_SCOPED; F03/B03 HOLD because eight unrelated family names were accepted, forged fold assignment bypassed HMAC provenance, and no production caller used strict gateways. G2 source-lock rebind HOLD.
- Frozen V4 scientific design **`b8410d9c1f77a733036e980b567de73c316f8725`**: [contract](https://github.com/minhtri22/TokenToModel-Lab/blob/b8410d9c1f77a733036e980b567de73c316f8725/docs/research/vector-memory/r8/TTM_VM_V4_R8_V4_GOLD_FOLD_ORACLE_RATER_OWNER_SCOPE_SINGLE_PACKET_DESIGN_ONLY_20261114.md). Its B03 Stage 1 requires exactly eight **F01–F08** families and 32 precommitted blueprints/64 later cases.
- G1 owner standing direction is recorded at `097e046bb0f6525665dde03ec5fcdf8134a8e762`: synthetic exploratory R8-D, four AI raters, no real PII; do not ask for repeat owner GO.
- Original independent Windows G2 temporary non-R8 preflight: [commit `62542b6...` report](https://github.com/minhtri22/TokenToModel-Lab/blob/62542b6db216a021f84aa8495f40794fb82097d4/docs/research/vector-memory/r8/reviews/G0_G2_FINAL_INDEPENDENT_READBACK_AND_ADJUDICATION.md); `PASS_SCOPED` for temporary DACL/sentinel/runtime only, not a persistent R8 storage source lock.
- Historic 37/37, 25/25, 15/15 receipts remain pinned to original commits; they were **NOT rerun**. No R8 candidate/gold/CAL/TEST/GPU/Reader/PROBE256.

## One integrated B03 source change

**Source implementation commit:** `5a51e1e6ca0938b0f77d1db553da45cd294a97c3`  
[GitHub commit](https://github.com/minhtri22/TokenToModel-Lab/commit/5a51e1e6ca0938b0f77d1db553da45cd294a97c3)

1. **Exact family enum:** `folds_raters.validate_r8_blueprint_manifest` now enforces the closed set `F01` through `F08` by equality of sets, plus four blueprints per family. Eight arbitrary family names are INVALID even when 32 rows and 8×4 counts otherwise match.
2. **Authenticated preassignment:** `preassign_r8` requires bytes key length ≥32 supplied by a real custodian when used in production; it binds *all JSON blueprint metadata* in a canonical sorted HMAC-SHA256 blueprint commitment. It also binds the actual fold map, component memberships/counts and CV status in a second domain-separated HMAC. `postcheck_r8` requires the same custodian-supplied key, verifies both HMAC values with constant-time comparison, recomputes the deterministic preassignment, compares locked fold/component/status values, and only then invokes `postcheck`. A forged status/fold/blueprint/key is rejected before CV. These checks validate integrity under the supplied key; **they do not themselves prove that the key came from G2 custody or that preassignment was timestamped BEFORE any real R8 case**.
3. **Source-level production caller:** new `integrated_closure/r8_production_caller.py` has two mandatory entrypoints, `precommit_before_G3` and `verify_after_G3_before_CV`. They invoke `preassign_r8` and `postcheck_r8` respectively, and fail closed if no CV readiness or any post-fold leakage. They return only a summary on postcheck. A direct production R8 candidate generator does **not** exist in this repository snapshot; this caller is a runnable mandatory preflight API, **not proof of integration into future real authoring runtime**. An actual candidate producer must be integrated with this API and yield a G2 precommit timing receipt before production authoring GO.
4. **Test compatibility:** `test_g0_final_three_findings.py` had a source-fixture call updated to supply an obviously synthetic 32+-byte test key to the new required `postcheck_r8` signature; the old 15/15 historical run was not executed again and continues to apply solely to its original code pin.
5. Source QA work added `test_g0_b03_production_negative.py` (15 targeted non-R8 cases) and updated only the targeted workflow to run **this new file**. No historical suites executed.

Exact source links:
- [folds_raters.py](https://github.com/minhtri22/TokenToModel-Lab/blob/5a51e1e6ca0938b0f77d1db553da45cd294a97c3/docs/research/vector-memory/r8/integrated_closure/folds_raters.py)
- [r8_production_caller.py](https://github.com/minhtri22/TokenToModel-Lab/blob/5a51e1e6ca0938b0f77d1db553da45cd294a97c3/docs/research/vector-memory/r8/integrated_closure/r8_production_caller.py)
- [targeted QA](https://github.com/minhtri22/TokenToModel-Lab/blob/5a51e1e6ca0938b0f77d1db553da45cd294a97c3/docs/research/vector-memory/r8/integrated_closure/test_g0_b03_production_negative.py)

## Focused QA, not science and not independent review

[GitHub Actions run 43602350914](https://github.com/minhtri22/TokenToModel-Lab/actions/runs/43602350914) `completed/success`, exact head `5a51e1e6ca0938b0f77d1db553da45cd294a97c3`, Ubuntu CPython 3.12.16. The job ran **15/15 PASS** new B03 source-only negative/positive-control tests. Cases include exact closed enum, wrong family capitalization, forged fold/status without lock, altered HMAC, altered blueprint, wrong key, insufficient key length, a reproducible synthetic happy path, actual caller monkeypatch instrumentation verifying both strict gateways, and fail-closed cross-fold leakage. All source-only, non-R8.

CI SHA-256 (raw bytes):
- `integrated_closure/folds_raters.py`: `a9fbf9dd81994822ced7dabc50b7fedc2f5fc608ed1f6da9ec9aadfb22eb7edb`
- `integrated_closure/r8_production_caller.py`: `3a9b249bced1b4ceaa5746d63367c017410ef82ded21ef386c3be2b1ee76b206`
- `integrated_closure/test_g0_b03_production_negative.py`: `8c7cce710964455db2a1ca66904d74050b2a84f6c8f2a1998534719d4954aeb6`
- `integrated_closure/test_g0_final_three_findings.py`: `750d90cf069b31418bdc852d9aa276295b06162ef454629835b5086aa872a4a2`
- `integrated_closure/gold_contract.py`: still `8e8b81ce2d0bc47cc60c29abc7156fe9d97613e67983e43b7f587615d68015a5`
- `integrated_closure/restricted_oracles.py`: still `34ab74d36b822703e4d8cbdf281e142273d55d181243d904b55fd31a0e6382a1`

## G2 — attempted private source-lock readback; **NOT COMPLETE**

- Previously reported Windows temporary preflight remains `PASS_SCOPED_STORAGE_PREFLIGHT_REPORTED`. Do not rerun sentinel without a material scope change.
- During this operation the connected RemoteDesktop device/workspace inspection returned an internal tool error; no actual protected-runtime readback took place. CMH Remote Web reported `online=true` on the canary but `mode=RC3_I_OFFLINE`; this is NOT evidence that arbitrary commands or private-custody source-lock operations are accessible.
- Hence **`G2=HOLD_SOURCE_LOCK_REBIND_NOT_VERIFIED`**. A real authorized custodian must compare exact SHA-256 of the new `folds_raters.py` and `r8_production_caller.py` (as well as the unchanged `gold_contract.py`, `restricted_oracles.py` and relevant runtime/contract) against bytes available under its current protected private execution identity, and attest source-lock/ACL scope/timestamp. It must bind a future private HMAC key and pre-G3 assignment receipt under that scope; no key is created/published here.
- The public CI hashes above **cannot substitute** for an actual private G2 readback or a production precommit timestamp receipt. Do not claim G2 PASS from this same-agent implementation.

## Gate adjudication and next single action

- `G0_B03_IMPLEMENTATION_SOURCE_QA=PASS_SCOPED_15_OF_15`; exact source pin `5a51e1e6ca0938b0f77d1db553da45cd294a97c3`. Independent G0 reviewer of this latest delta **NOT YET PERFORMED**.
- `PRODUCTION_CALLER_SOURCE_GATE=IMPLEMENTED_AND_QA_PASS`; real R8 authoring integration / pre-G3 chronological custody still `NOT_EXECUTED`.
- `G1=OWNER_STANDING_RESEARCH_DIRECTION_RECORDED`; no repeat owner GO.
- `G2=PASS_SCOPED_STORAGE_PREFLIGHT_REPORTED; HOLD_SOURCE_LOCK_REBIND_NOT_VERIFIED`.
- **`DECISION=HOLD_INTEGRATED`**, `GO_R8_D_CANDIDATE_AUTHORING_ONLY=NOT_AUTHORIZED`.
- Preserve `R7=FROZEN_FAIL`, `R8=NOT_GENERATED`, `G3/G4=NOT_EXECUTED`, `G5/G6=SEALED`, `READER=0`, `GPU=NO`, `PROBE256=SEALED`.

**Single next action (NOT a handoff or micro-permit):** Another independent AI reviewer validates the corrected B03 family/HMAC/caller source delta and its exact pinned SHA; a genuine authorized Windows custodian performs one protected source-lock readback and confirms persistence/ACL and future precommit binding. Then issue one GO/HOLD verdict on combined evidence. Do not rerun historic QA, fabricate private attestation, open V5/V6 or produce R8 candidate.
