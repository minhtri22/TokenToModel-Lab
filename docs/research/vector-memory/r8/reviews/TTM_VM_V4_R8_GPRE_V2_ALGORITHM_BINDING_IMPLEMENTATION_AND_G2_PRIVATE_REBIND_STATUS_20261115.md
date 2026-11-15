# TTM Vector Memory V4 R8 — G_pre V2 Algorithm Binding and G2 Private Rebind Status

**Date:** 2026-11-15 (Asia/Bangkok)  
**Operation:** `TTM_VM_V4_R8_GPRE_V2_ALGORITHM_VERSION_AND_G2_PROTECTED_SOURCE_REBIND_SINGLE_GATE`  
**Repository:** `minhtri22/TokenToModel-Lab`  
**Mode:** `IMPLEMENTATION_AGENT_SOURCE_ONLY_TARGETED_QA + REMOTEMCP_READ_ONLY_PREFLIGHT`  
**Adjudication:** **`HOLD_INTEGRATED`**. Independent G0 approval and protected G2 custody remain unverified; `GO_R8_D_CANDIDATE_AUTHORING_ONLY=NOT_AUTHORIZED`.

## 1. Exact independent finding to remediate

The independent report at `2eecf748e5e8a2ec1698d237ccb4d53fc82f4e18`:  
[TTM_VM_V4_R8_B03_C_FINAL_INDEPENDENT_G0_G2_ADJUDICATION.md](https://github.com/minhtri22/TokenToModel-Lab/blob/2eecf748e5e8a2ec1698d237ccb4d53fc82f4e18/docs/research/vector-memory/r8/reviews/TTM_VM_V4_R8_B03_C_FINAL_INDEPENDENT_G0_G2_ADJUDICATION.md) established `B03-C=PASS_SCOPED_INDEPENDENT` for injective component serialization; `B03-A/B=PASS_SCOPED`; `PRODUCTION_GATEWAY=PASS_SCOPED_SOURCE`. It discovered **`G0-VERSION-01`**: the component HMAC-ranking algorithm changed from ambiguous delimiter joins to canonical tagged JSON, while the existing `TTM_VM_R8_GPRE_HMAC_V1` lock schema, `R8_GPRE_FOLDS_V1` MAC domain and encoded lock fields did not mark the new ranking algorithm. For a synthetic 32-blueprint, four-component witness, source-version V1 and the new source could emit identical fold/map/status records and a legacy lock was accepted by the new postcheck. This is **not** HMAC forgery; it is missing version/provenance discrimination. Reviewer source pin was `8d14cc2c89bfb178e6c415c5edeba8cc58b2558b`.

The same independent report classified `G2=HOLD_SOURCE_LOCK_REBIND_NOT_VERIFIED`: public Git/checkout SHA readback does not prove private protected-runtime source bytes, ACL, authorized custodian, HMAC-key provenance or durable pre-G3 receipt.

## 2. Focused G0 source implementation — exact immutable pin

**New implementation commit:** `84d9d5c95e9962ccfe294852570e261b145fe403`  
[GitHub commit](https://github.com/minhtri22/TokenToModel-Lab/commit/84d9d5c95e9962ccfe294852570e261b145fe403)

In `integrated_closure/folds_raters.py`, without changing the independently reviewed injective `_component_signature` byte representation:
- `R8_PREASSIGN_LOCK_SCHEMA` changed to `TTM_VM_R8_GPRE_HMAC_V2`.
- Added explicit `R8_GPRE_ALGORITHM_ID=R8_GPRE_CANONICAL_JSON_COMPONENT_RANKING_V2`. Distinguish the component signature format's independent `R8_GPRE_COMPONENT_V1` domain tag from the **overall G_pre preassignment algorithm V2**.
- Added preassignment HMAC domain `R8_GPRE_FOLDS_V2`.
- `preassign_r8()` serializes `algorithm_id` with `lock_schema` and the preassigned fold/blueprint/component data; includes it in the exact authenticated HMAC document.
- `postcheck_r8()` rejects old/unknown `lock_schema` or `algorithm_id` BEFORE recomputing/accepting, then verifies the complete V2 HMAC/fold fields. A legacy V1 envelope cannot be silently reinterpreted even when its numeric fold mapping is identical.
- Existing `r8_production_caller.py` remains unchanged and delegates to the corrected strict gateways. Future G_pre private custody/source-lock and actual real authoring integration are **separate gates not proved by these source changes**.

**Code links:**
- [folds_raters.py @ exact commit](https://github.com/minhtri22/TokenToModel-Lab/blob/84d9d5c95e9962ccfe294852570e261b145fe403/docs/research/vector-memory/r8/integrated_closure/folds_raters.py)
- [r8_production_caller.py @ exact commit](https://github.com/minhtri22/TokenToModel-Lab/blob/84d9d5c95e9962ccfe294852570e261b145fe403/docs/research/vector-memory/r8/integrated_closure/r8_production_caller.py)
- [new ten-test source-only fixture](https://github.com/minhtri22/TokenToModel-Lab/blob/84d9d5c95e9962ccfe294852570e261b145fe403/docs/research/vector-memory/r8/integrated_closure/test_g0_algorithm_version_binding.py)

Source implementation diff touched only `folds_raters.py`, added `test_g0_algorithm_version_binding.py`, and updated the existing scoped GitHub workflow to select that new test. **No V4 frozen science contract, prior source reports, G1 owner decision, or real R8 data changed.**

## 3. Focused QA and immutable public hashes

[GitHub Actions 43677926880](https://github.com/minhtri22/TokenToModel-Lab/actions/runs/43677926880): `completed/success`, `head_sha=84d9d5c95e9962ccfe294852570e261b145fe403`. CPython 3.12, Ubuntu runner. **10/10 targeted tests PASS**. Targeted negative cases reject legacy V1 with identical fold/component/status/HMAC envelope, legacy version grafted to V2 schema without algorithm ID, null/unknown algorithm ID, V1 MAC domain under V2 metadata; valid V2 strict production caller still accepts exact-size synthetic non-R8 symbolic cases, and reordering is stable. The reconstructed legacy V1 envelope uses a public non-secret fixture key; this is a source-level witness, not an actual G2 key, private precommit or scientific proof.

**SHA-256 from exact CI raw source readback:**
- `integrated_closure/folds_raters.py` = `02626f9f0def5af90b57c2930898e96dbc8f6206c441bb4aaa4c4278ce0dddae`
- `integrated_closure/r8_production_caller.py` = `3a9b249bced1b4ceaa5746d63367c017410ef82ded21ef386c3be2b1ee76b206`
- `integrated_closure/test_g0_algorithm_version_binding.py` = `2ce86fe549e1625790fcab72c076df2f12d648b048a350570d5c97a026431ae2`
- Previously unchanged `gold_contract.py` = `8e8b81ce2d0bc47cc60c29abc7156fe9d97613e67983e43b7f587615d68015a5`.
- Previously unchanged `restricted_oracles.py` = `34ab74d36b822703e4d8cbdf281e142273d55d181243d904b55fd31a0e6382a1`.

CI metadata: `QA_SCOPE=G0_GPRE_ALGORITHM_VERSION_BINDING_ONLY`, `HISTORIC_37_25_15_15_7_NOT_RERUN=TRUE`, `R8_GENERATED=FALSE`, `PRIVATE_GOLD=NOT_ACCESSED`, `GPU=NO`, `READER=0`, `PROBE256=SEALED`.

**Do not classify this as independent G0 review:** author and test runner are the implementation agent. A distinct reviewer must analyze whether explicit V2 schema, authenticated algorithm ID and MAC domain actually block the independent legacy witness and any alternative downgrade paths. The frozen V4 scientific contract at `b8410d9c1f77a733036e980b567de73c316f8725` remains authoritative.

## 4. G2 — actual RemoteMCP preflight, source-lock still HOLD

Using the linked `Primary` RemoteDesktop/RemoteMCP access, read-only `device_status` confirmed:
- `machine-1`, `ONLINE`, device ID `dev_dd73ebfa742f468f2d212bade88c175b`, fresh signed heartbeat, same previously pinned key fingerprint `b657d5395e393e0957a9ed358bb5a1fe1588fde5d3a44be71295a68d1e73def9`.
- Approved node execution root reported as `D:\WORK\RESEARCH`.
- Previously reported active managed GIT binding `prj_1544c3e94ebd4b2947bc84e9` was read with `project_status`: `ACTIVE`, bound to the same device, 0 active tasks. It exposes a managed workspace root; **neither that binding nor device-online status identifies a protected persistent R8 custody store or a custodian authorization record**.
- No newly authorized R8 private source path, access-control record, verified executor custodian identity, HMAC secret/key provenance or protected-runtime SHA readback was supplied. No managed task/job was created, no maintenance/pairing/restart, no arbitrary directory declared to be protected.
- Existing 54-byte non-R8 sentinel preflight from the earlier [independent G0/G2 source report](https://github.com/minhtri22/TokenToModel-Lab/blob/62542b6db216a021f84aa8495f40794fb82097d4/docs/research/vector-memory/r8/reviews/G0_G2_FINAL_INDEPENDENT_READBACK_AND_ADJUDICATION.md) retains `PASS_SCOPED_STORAGE_PREFLIGHT_REPORTED`, not current G2 source-lock PASS.

**Decision:** `G2=HOLD_SOURCE_LOCK_REBIND_NOT_VERIFIED`. An authorized custodian must positively bind actual protected storage and runtime identity, read back the five newly pinned source SHA-256 values under that identity, verify persistence/ACL and separately record prospective private-key policy and a durable **pre-G3** attestation method. Public GitHub Actions hashes are not private-runtime evidence. Do not print secrets or private ACL contents.

## 5. Formal scope, integrated decision and one necessary verification

- `G0_GPRE_V2_SOURCE_IMPLEMENTATION_QA=PASS_10_OF_10_SCOPED`
- `G0_DISTINCT_INDEPENDENT_FINAL_REVIEW=NOT_EXECUTED`
- `G1=OWNER_STANDING_RESEARCH_DIRECTION_RECORDED` at `097e046bb0f6525665dde03ec5fcdf8134a8e762`; exploratory R8-D synthetic only. Do not ask owner repeated GO.
- `G2=HOLD_CURRENT_PROTECTED_SOURCE_LOCK`; previously scoped storage smoke evidence preserved.
- `GO_R8_D_CANDIDATE_AUTHORING_ONLY=NOT_AUTHORIZED`, `FINAL_DECISION=HOLD_INTEGRATED`.
- `R7=FROZEN_FAIL`, `R8=NOT_GENERATED`, `G3/G4=NOT_EXECUTED`, `G5/G6=SEALED`, `READER=0`, `GPU=NO`, `PROBE256=SEALED`.

**Only remaining integrated verification:** a reviewer **distinct from this implementation agent** checks the V2 version-binding delta and original legacy witness at exact source commit `84d9d5...`; an actual authorized private custodian performs an exact SHA-256 protected-runtime readback and ACL/identity/source-lock confirmation for current bytes. Then one GO/HOLD adjudication. No historical reruns, new science, new handoff, V5/V6 or repeated owner GO.
