# TTM Vector Memory V4 R8 — Final Independent G_pre V2 / G2 Adjudication

**Date:** 2026-11-15 (Asia/Bangkok)  
**Operation:** `TTM_VM_V4_R8_GPRE_V2_FINAL_DISTINCT_REVIEW_AND_G2_PROTECTED_REBIND_SINGLE_GATE`  
**Reviewer role:** Independent AI Scientific & Source Reviewer (distinct from the implementation-agent report).  
**Mode:** `READ_ONLY_SOURCE_REVIEW · REMOTEMCP_PROTECTED_PREFLIGHT_ONLY · NO_SCIENCE_EXECUTION`  
**One integrated adjudication:** **`HOLD_INTEGRATED`**.  
**G0-VERSION-01:** `PASS_SCOPED_INDEPENDENT_SOURCE_REVIEW`.  
**G2:** `G2_HOLD_SOURCE_LOCK_REBIND_NOT_VERIFIED`.  
**GO_R8_D_CANDIDATE_AUTHORING_ONLY:** `NOT_AUTHORIZED`.

## 1. Immutable inputs and source-chain custody

- Repository: [minhtri22/TokenToModel-Lab](https://github.com/minhtri22/TokenToModel-Lab).
- Original implementation code reviewed **only at** `84d9d5c95e9962ccfe294852570e261b145fe403`: [exact commit](https://github.com/minhtri22/TokenToModel-Lab/commit/84d9d5c95e9962ccfe294852570e261b145fe403).
- Implementation-agent report: [`b05883ea79ae6228ef59c70c1704d42e7879c49e`](https://github.com/minhtri22/TokenToModel-Lab/blob/b05883ea79ae6228ef59c70c1704d42e7879c49e/docs/research/vector-memory/r8/reviews/TTM_VM_V4_R8_GPRE_V2_ALGORITHM_BINDING_IMPLEMENTATION_AND_G2_PRIVATE_REBIND_STATUS_20261115.md). This is **not** an independent approval.
- Prior independent counterexample and B03-A/B/C adjudication: [`2eecf748e5e8a2ec1698d237ccb4d53fc82f4e18`](https://github.com/minhtri22/TokenToModel-Lab/blob/2eecf748e5e8a2ec1698d237ccb4d53fc82f4e18/docs/research/vector-memory/r8/reviews/TTM_VM_V4_R8_B03_C_FINAL_INDEPENDENT_G0_G2_ADJUDICATION.md).
- Prior source for comparison: `8d14cc2c89bfb178e6c415c5edeba8cc58b2558b`.
- Frozen V4 scientific design: [`b8410d9c1f77a733036e980b567de73c316f8725`](https://github.com/minhtri22/TokenToModel-Lab/blob/b8410d9c1f77a733036e980b567de73c316f8725/docs/research/vector-memory/r8/TTM_VM_V4_R8_V4_GOLD_FOLD_ORACLE_RATER_OWNER_SCOPE_SINGLE_PACKET_DESIGN_ONLY_20261114.md).
- G1 owner standing research direction: [`097e046bb0f6525665dde03ec5fcdf8134a8e762`](https://github.com/minhtri22/TokenToModel-Lab/blob/097e046bb0f6525665dde03ec5fcdf8134a8e762/docs/research/vector-memory/r8/decisions/TTM_VM_V4_R8_OWNER_STANDING_RESEARCH_DIRECTION_20261114.md).

A separate SHA-256 digest was computed from each exact GitHub source file's fetched UTF-8 contents, not inferred from the Git blob SHA-1. All digests independently matched the CI-reported raw-source SHA-256 values:

| File in `docs/research/vector-memory/r8/integrated_closure/` | Independently computed SHA-256 | Match |
|---|---|---|
| `folds_raters.py` | `02626f9f0def5af90b57c2930898e96dbc8f6206c441bb4aaa4c4278ce0dddae` | PASS |
| `r8_production_caller.py` | `3a9b249bced1b4ceaa5746d63367c017410ef82ded21ef386c3be2b1ee76b206` | PASS |
| `test_g0_algorithm_version_binding.py` | `2ce86fe549e1625790fcab72c076df2f12d648b048a350570d5c97a026431ae2` | PASS |
| `gold_contract.py` | `8e8b81ce2d0bc47cc60c29abc7156fe9d97613e67983e43b7f587615d68015a5` | PASS |
| `restricted_oracles.py` | `34ab74d36b822703e4d8cbdf281e142273d55d181243d904b55fd31a0e6382a1` | PASS |

**Evidence classification:** `GITHUB_EXACT_SOURCE_SHA_MATCH_5_OF_5`, **not** `G2_PROTECTED_SOURCE_LOCK_PASS_SCOPED`. The code/content readbacks came from GitHub, not from verified private execution storage.

## 2. Distinct independent source analysis: G0-VERSION-01

Original counterexample: for a public synthetic fixture of 32 blueprints in four components, V1 and post-B03-C component ranking could produce identical fold/component/status maps. The legacy `TTM_VM_R8_GPRE_HMAC_V1` lock and `R8_GPRE_FOLDS_V1` MAC domain lacked an authenticated new-ranking identity; the new postcheck previously accepted a lock made by the old algorithm. This was **algorithm-version provenance ambiguity**, not SHA-256/HMAC forgery.

The exact V2 implementation introduces three distinct bindings in `folds_raters.py` (lines 168–173):
- `R8_PREASSIGN_LOCK_SCHEMA="TTM_VM_R8_GPRE_HMAC_V2"`
- `R8_GPRE_ALGORITHM_ID="R8_GPRE_CANONICAL_JSON_COMPONENT_RANKING_V2"`
- `R8_GPRE_PREASSIGNMENT_MAC_DOMAIN="R8_GPRE_FOLDS_V2"`

In `preassign_r8()` (lines 267–285), the returned lock contains both `lock_schema` and `algorithm_id`, and the canonical-json preassignment HMAC authenticates these fields together with blueprint HMAC, folds, component membership IDs/count, fold sizes and status. The HMAC calculation applies explicit domain separation `purpose.encode("ascii")+b"\0"+canonical_json` in `_r8_hmac()` (lines 251–255).

In `postcheck_r8()` (lines 288–318), schema and algorithm ID are checked **before** the expected V2 allocation is recomputed; both HMAC fields are checked with `hmac.compare_digest`, and fold/component/count/status fields are compared to recomputed expected values. The function rejects a legacy V1 envelope even if its numeric fold map is the same. A hand-edited V2 schema without an authenticated V2 algorithm ID fails, and a V1 MAC-domain digest does not match V2.

### Independent condition-by-condition disposition

| Requirement from handoff | Distinct source review |
|---|---|
| 1. Reject legacy V1 lock with matching fold | PASS — schema mismatch in `postcheck_r8` |
| 2. Reject mere schema-graft from V1 | PASS — missing `algorithm_id` check; V1 MAC still incompatible |
| 3. Reject missing/null/unknown/modified algorithm ID | PASS — equality check and authenticated MAC |
| 4. Detect V1 HMAC domain graft | PASS — recomputed `R8_GPRE_FOLDS_V2` MAC compared to supplied |
| 5. Algorithm ID authenticated, not mere metadata | PASS — `algorithm_id` explicitly in MAC document |
| 6. Detect fold/component/blueprint tampering | PASS_SCOPED_SOURCE — full blueprint HMAC + recomputed assignment + authenticated fields |
| 7. Strict production caller does not skip version verification | PASS_SCOPED_SOURCE — `verify_after_G3_before_CV` delegates to `postcheck_r8` |
| 8. Valid V2 synthetic source-only fixture | PASS_REPORTED_IMPLEMENTATION_QA + source path inspected; **not counted as distinct runtime probe** |
| 9. Preserve prior B03-C `_component_signature` | PASS — compared old and new exact function text; unchanged, including its literal `\\x00` component tag |
| 10. No silent V1→V2 reinterpretation in reviewed production APIs | PASS_SCOPED_SOURCE — no bypass observed in the two pinned production entrypoints |

The `R8_GPRE_COMPONENT_V1` signature-format label is different in purpose from the preassignment `R8_GPRE_HMAC_V2` algorithm version. This difference is **not** itself a downgrade or source inconsistency. There is no basis to reclassify B03-C as failed.

### QA provenance and independent-review limitation

[GitHub Actions run `43677926880`](https://github.com/minhtri22/TokenToModel-Lab/actions/runs/43677926880) was read directly: `completed/success`, run head `84d9d5c95e9962ccfe294852570e261b145fe403`, targeted G0 version-binding QA `10/10 PASS` per implementation report. This is **implementation-agent QA**, not independently authored dynamic QA. This review performed an independent line-by-line source analysis, exact source SHA-256 readback and old/new helper comparison; **no additional independent executable Python probes were run**. No historical 37/25/15/15/7 suites were rerun.

**Narrow disposition:** `G0_VERSION_BINDING_PASS_SCOPED_INDEPENDENT_SOURCE_REVIEW`. The original `G0-VERSION-01` acceptance path is closed **within the exact source and production entrypoints reviewed**. This is not a statement that a future protected deployment, arbitrary external callers, real R8 data, or G2 source custody has passed. Retain prior `B03-A=PASS_SCOPED`, `B03-B=PASS_SCOPED`, `B03-C=PASS_SCOPED_INDEPENDENT`, `PRODUCTION_GATEWAY=PASS_SCOPED_SOURCE`.

## 3. RemoteMCP V2 read-only preflight — actual current G2 observation

Used the installed canonical `remote-mcp-v2-web-clean` skill and its tool-surface-integrity instructions. The attached RemoteDesktop App has the current managed task/device surfaces, including `task_job_submit_with_evidence`; no retired `task_job_submit_once` was selected or invoked. The linked **`Primary`** account was used for read-only `device_list`, `device_status` and `project_status`. No legacy or arbitrary gateway shell execution was used.

| Observed property | Readback |
|---|---|
| Device | `machine-1`, `ONLINE` |
| Device ID | `dev_dd73ebfa742f468f2d212bade88c175b` |
| Hostname | `DESKTOP-4PSD0G2` |
| Route generation | `1` |
| Pinned node fingerprint SHA-256 | `b657d5395e393e0957a9ed358bb5a1fe1588fde5d3a44be71295a68d1e73def9` — matched |
| Node execution root | `D:\WORK\RESEARCH` |
| Signed heartbeat | Fresh at device query, node local snapshot around `2026-11-15T04:50:33Z` |
| Authoritative active node jobs | `0`; reconciliation complete; unresolved `0` |
| Research dispatch | `RESEARCH_ADAPTER_DISABLED`; new job admission not allowed |
| Existing managed project | `prj_1544c3e94ebd4b2947bc84e9`, `ACTIVE`, bound to `machine-1`, active tasks `0` |
| Authorized R8 private custodian | `NOT_VERIFIED` |
| R8 protected persistent source store/path | `NOT_VERIFIED` |
| Effective R8 ACL/DACL and executor authorization | `NOT_VERIFIED` |
| Protected source provenance and current five source hashes | `NOT_EXECUTED` |
| Private HMAC-key custody policy, receipt persistence before G3 | `NOT_VERIFIED` |

**Classification:** `G2_HOLD_SOURCE_LOCK_REBIND_NOT_VERIFIED`.

Device and project metadata prove a reachable, correctly identified executor and a managed project binding, **not** an authorized protected R8 store. No scoped private path or custodian identity was furnished. Consequently, no `Get-FileHash` was routed to an assumed directory. The current GitHub source hash matches cannot be relabeled private-runtime hashes. No custodian attestation is fabricated. The history of a non-R8 sentinel/storage preflight remains only `PASS_SCOPED_STORAGE_PREFLIGHT_REPORTED`.

To close this exact G2 condition, the already-authorized custodian must bind a specific protected source checkout and runtime identity; verify the effective access control, durable storage, actual five file hashes and source provenance, and attest to key governance plus the mechanism ensuring an immutable timestamped G_pre commitment before G3. The public receipt must disclose only nonsensitive status, hashes, device/route/source pins and UTC audit time — **never** private keys, private gold, secret paths or ACL details. No real key or gold is to be generated just for preflight.

## 4. G1 standing owner decision, scientific state, integrated gate

G1 is `OWNER_STANDING_RESEARCH_DIRECTION_RECORDED` at `097e046bb0f6525665dde03ec5fcdf8134a8e762`: `ADOPT_R8_D_DESCRIPTIVE_ONLY`, exploratory 32 pairs/64 cases, four AI raters/two scores per case, P-REC-V1 synthetic toy domain and exclusively new AI-authored non-PII/non-unlicensed data. The record is classified `OWNER_CHAT_DECLARATION_RECORDED_BY_ASSISTANT`, **not** a cryptographically signed owner or private custodian attestation. No repeated owner GO question is necessary for this same scoped direction. Future data-specific rights and PII proof remain untested because no R8 data exist.

| Gate | Status |
|---|---|
| B03-A/B/C source findings | Preserve prior scoped PASS |
| G0-VERSION-01 V2 independent source review | `PASS_SCOPED_INDEPENDENT_SOURCE_REVIEW` |
| G0 historic QA | Preserved; not rerun |
| G1 standing exploratory research direction | `OWNER_STANDING_RESEARCH_DIRECTION_RECORDED` |
| G2 protected runtime source-lock and custodian | **`G2_HOLD_SOURCE_LOCK_REBIND_NOT_VERIFIED`** |
| GO R8-D candidate authoring | **`NOT_AUTHORIZED`** |
| **Single integrated decision** | **`HOLD_INTEGRATED`** |

Scientific invariants: `R7=FROZEN_FAIL`; `R8=NOT_GENERATED`; `G3/G4=NOT_EXECUTED`; `G5/G6=SEALED`; `READER=0`; `GPU=NO`; `PROBE256=SEALED`. No R8 cases/gold, blind ratings, CAL/TEST, model training, GPU use or scientific dispatch occurred. No source modifications, task/job creation, pairing, node restart, repository main merge, historical QA reruns or phase/permit openings occurred.

**Final adjudication: `HOLD_INTEGRATED`.** G0-VERSION-01 is closed at the reviewed exact source pin; **G2 remains the single decisive unresolved blocker**. The sole next verification is the authenticated protected-runtime SHA-256 and custody readback by the authorized private custodian within the existing G2 gate; retain the standing G1 decision and do not create micro-permits, V5/V6, or another handoff.
