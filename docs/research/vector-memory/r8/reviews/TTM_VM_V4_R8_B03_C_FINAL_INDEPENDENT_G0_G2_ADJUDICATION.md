# TTM Vector Memory V4 R8 — B03-C Final Independent G0/G2 Adjudication

**Operation:** `TTM_VM_V4_R8_B03_C_FINAL_INDEPENDENT_REVIEW_AND_G2_PRIVATE_SOURCE_REBIND_SINGLE_GATE`

**Date:** 2026-11-15 (Asia/Ho_Chi_Minh)

**Role:** Independent AI Evidence Reviewer

**Scope:** exact Git-source review, independent in-memory synthetic negative probes, RemoteMCP V2 read-only preflight

**One integrated decision:** **`HOLD_INTEGRATED`**

## 1. Immutable source and provenance

- Repository: `minhtri22/TokenToModel-Lab`.
- Evidence branch: `evidence/ttm-vm-v4-r8-g0-f01-f03-single-closure-20261114`.
- **Implementation source commit:** `8d14cc2c89bfb178e6c415c5edeba8cc58b2558b`.
- Implementation-agent report: `8dec9438bff96922e5defd64550971c309d5b32f`.
- Previous independent B03 review: `b21a6bb6576d3b7ecc7f63fba8ff67fab5e102bb`.
- Frozen V4 science contract: `b8410d9c1f77a733036e980b567de73c316f8725`.
- Owner standing research decision: `097e046bb0f6525665dde03ec5fcdf8134a8e762`.

The reviewer read exact Git objects using `git show <commit>:<path>` and calculated SHA-256 over the **raw Git blob bytes**, using Python `subprocess.check_output` and `hashlib.sha256`. All five source hashes match the implementation report:

| Source under `docs/research/vector-memory/r8/integrated_closure/` | Independent Git blob SHA-256 | Match |
|---|---|---|
| `folds_raters.py` | `db0879f6f2c5557d46e48207e84b8071cf85a772f9b83c22bb777c4fe0fd5f8b` | PASS |
| `r8_production_caller.py` | `3a9b249bced1b4ceaa5746d63367c017410ef82ded21ef386c3be2b1ee76b206` | PASS |
| `test_g0_b03_component_signature.py` | `2f6caa38664e7b735da053605799a7ac719b9d800050bec0a9a7a6364acd7cc3` | PASS |
| `gold_contract.py` | `8e8b81ce2d0bc47cc60c29abc7156fe9d97613e67983e43b7f587615d68015a5` | PASS |
| `restricted_oracles.py` | `34ab74d36b822703e4d8cbdf281e142273d55d181243d904b55fd31a0e6382a1` | PASS |

The complete code delta from previous independent report `b21a6bb` to implementation `8d14cc2` consists of `folds_raters.py`, the new `test_g0_b03_component_signature.py`, and the targeted QA workflow. The protected private runtime is a separate evidence domain.

## 2. G0 B03-C — Independent membership-encoding analysis

The previous `"|".join(comp)` ranking message was non-injective. Two distinct member lists `["a","b|c"]` and `["a|b","c"]` both encoded as `a|b|c`.

The new `_component_signature()` enforces a list/tuple of strings, sorts its members, rejects duplicates, serializes them as a canonical JSON array with `ensure_ascii=False` and fixed separators, UTF-8 encodes that array and prepends the component-specific domain tag. `preassign()` passes this result into the HMAC-SHA256 component-ranking path. The actual source prefix is the bytes for `R8_GPRE_COMPONENT_V1\x00` with a **literal backslash-x sequence**, rather than a NUL byte. It is nevertheless a fixed, distinct component domain prefix at the reviewed source pin.

For finite lists of distinct UTF-8-encodable strings, the JSON array parser reconstructs the sorted member list, including boundaries and special characters. Therefore equal canonical messages imply equal sorted lists and equal component membership. The source rejects duplicate and non-string members. Unicode values that cannot be UTF-8 encoded raise an exception before an HMAC ranking result can be returned.

**Independent CPU probes** directly loaded the old and new pinned source modules from Git blobs. They did not use the implementation agent's test suite:

| Probe | Result |
|---|---|
| Twelve independent pairs containing delimiter, comma, quote, bracket, backslash, control characters and Unicode | **12/12 PASS**, signatures distinct |
| JSON parse round-trip and order invariance across both sides of each pair | **24/24 PASS** |
| Non-string and duplicate members rejected | **4/4 PASS** |
| Old reviewer witness `["a","b|c"]` vs `["a|b","c"]` | **PASS**, former collision closed |
| Component-specific HMAC input and strict production caller wiring | **PASS_SCOPED_SOURCE** |

The implementation-agent GitHub Actions run `43671809208` reports **7/7 PASS** at `8d14cc2`; it remains **implementation QA**, distinct from the independent probes above. Historical suites `37/37`, `25/25`, and `15/15` were retained without rerun. Unchanged B03-A family validation and B03-B HMAC tamper checks retain prior `PASS_SCOPED` conclusions.

## 3. G0 blocker — unversioned G_pre algorithm and legacy-lock acceptance

**Finding G0-VERSION-01 — `HOLD_G0_ALGORITHM_VERSION_BINDING`.**

The HMAC ranking message changed from delimiter-joined bytes to the canonical tagged JSON representation, but `R8_PREASSIGN_LOCK_SCHEMA` remains `TTM_VM_R8_GPRE_HMAC_V1`. The `preassignment_hmac` binds schema, blueprint MAC, fold mapping, component IDs/counts, fold counts and status. **It does not bind the ranking algorithm version, exact source hash, or source-lock receipt.** `postcheck_r8()` recomputes and compares these fields. When the old and new algorithms happen to generate the same fold mapping, their entire locked preassignments can be byte-for-byte equivalent under one key.

An independent, in-memory counterexample was reproduced with two Git modules (old `b21a6bb`, new `8d14cc2`) and public synthetic inputs:

1. Build 32 blueprints `BP00` through `BP31`; use unique `pair_id=PAIRxx` and `template_cluster_id=TEMPxx`, families `F01`–`F08` (four each), and `event_graph_id=EG(i//8)` for four components of eight members.
2. Set the **public/non-secret fixture key** to `SHA256(UTF8("nonsecret-scoped-source-fixture-59"))`. This is deliberately unrelated to G2 private custody.
3. Call `preassign_r8(blueprints,key)` against both immutable versions. The entire returned dictionaries are **equal**. The component count is `4` and fold sizes are `[8,8,8,8]`.
4. Construct 64 strictly valid synthetic SELECT/ABSTAIN cases with 32 unique keyed cards each, unique per-case text and only within-blueprint shared event signatures. Call **new** `postcheck_r8(cases,blueprints,old_lock,key)`. It **accepts** the old-version lock, returns `POST_GRAPH_NO_CROSSFOLD_EDGE`, and reports `crossfold_post_edges=0`.

Observed output: `SCHEMA_SAME=True`, `FOUND_PUBLIC_SEED=59`, `OLD_LOCK_EQUALS_NEW_LOCK=True`, `OLD_LOCK_ACCEPTED_BY_NEW_POSTCHECK=True`. This is a compatibility/provenance witness, **not** a cryptographic HMAC forgery and **not** evidence of affected real R8 data. It proves the source does not satisfy the handoff's condition that a G_pre commitment made by the old algorithm be recognizable and rejectable after the algorithm change. G2 attestation might establish which executable was used in a separate protected process, but the reviewed `postcheck_r8()` by itself does not enforce that identity.

**Disposition:** The injective-encoding component is `PASS_SCOPED`; integrated G0 remains **`HOLD_G0_ALGORITHM_VERSION_BINDING`**. A new, unambiguous algorithm/source-version binding must be independently reviewed at a future exact source pin before G0 closure. Reviewer made **no** source amendment.

## 4. Production gateway and cross-fold policy

At the exact source pin, `r8_production_caller.precommit_before_G3()` calls strict `preassign_r8()` and rejects non-estimable pre-fold status. `verify_after_G3_before_CV()` calls `postcheck_r8()` and rejects any `FOLD_LEAK_CV_INVALID`. `postcheck()` calculates similarity/event/card edges and sets `no_repartition=True`. This source inspection retains the earlier production-gateway **`PASS_SCOPED_SOURCE`** finding. Real G3 caller integration and durable timestamped pre-G3 source/commit binding remain **NOT_EXECUTED/NOT_VERIFIED**.

## 5. G2 — RemoteMCP V2 protected-runtime custody

Read-only RemoteDesktop App calls, reached through the canonical RemoteMCP V2 surface, returned current signed node information on 2026-11-15. The linked `Primary` connection was used. Required registered tool names `device_maintenance_recipe_catalog`, `device_maintenance_recipe_run`, and `task_job_submit_with_evidence` were discoverable; no job or maintenance call was made.

| Observation | Current evidence |
|---|---|
| Device | `machine-1`; ID `dev_dd73ebfa742f468f2d212bade88c175b`; `ONLINE` |
| Host | `DESKTOP-4PSD0G2`; Windows 11 |
| Node fingerprint SHA-256 | `b657d5395e393e0957a9ed358bb5a1fe1588fde5d3a44be71295a68d1e73def9` |
| Route generation / execution root | `1`; `D:\WORK\RESEARCH` |
| Capacity | Signed/reconciled, `authoritative_active_node_jobs=0`; `unresolved=0` |
| Managed binding inspected | `prj_1544c3e94ebd4b2947bc84e9`; bound to this device, ACTIVE, `active_tasks=0` |
| Research dispatch | `RESEARCH_ADAPTER_DISABLED`, `new_job_admission_allowed=false` |
| Verified authorized R8 private custodian and store | **NOT_VERIFIED** |
| Effective persistent ACL/DACL, storage identity and source-lock binding | **NOT_VERIFIED** |
| Protected-runtime hashes for current five pinned files | **NOT_EXECUTED**; no authenticated protected source paths |
| Private HMAC-key provenance and durable pre-G3 UTC receipt | **NOT_VERIFIED** |

The current binding and signed node heartbeat establish a reachable routed Windows executor. They do not identify an approved persistent R8 store, authenticated custodian permission or protected source-checkout location. Neither the public checkout SHA-256 results in §1 nor historical non-R8 sandbox/sentinel receipts establish current G2 custody. The readback prerequisite could not be satisfied from the available managed binding, so `Get-FileHash` was **not** dispatched against guessed paths and no private source bytes, secrets or ACL contents were accessed.

**G2 status: `G2_HOLD_SOURCE_LOCK_REBIND_NOT_VERIFIED`.** No claim of a protected-runtime SHA match is made. The future single custodian receipt must bind protected executor/source paths, authorized access scope, five actual file hashes, persistent storage/ACL evidence, key provenance and externally durable pre-G3 timestamp.

## 6. G1 and scientific scope

The owner standing direction at `097e046bb0f6525665dde03ec5fcdf8134a8e762` records `ADOPT_R8_D_DESCRIPTIVE_ONLY`, four AI raters/two ratings per case, P-REC-V1 toy-world policy and exclusively new AI-authored synthetic data. Its own classification is `OWNER_CHAT_DECLARATION_RECORDED_BY_ASSISTANT`; it is not a cryptographic owner signature, independent science acceptance or private custody attestation. **G1 remains `OWNER_STANDING_RESEARCH_DIRECTION_RECORDED`** for the already specified exploratory scope.

No new owner GO question was issued. Source-specific rights/PII screening remains tied to any future authorized generation.

## 7. Integrated adjudication and preservation

| Gate / condition | Result |
|---|---|
| G0 B03-A family identity | `PASS_SCOPED` (unchanged) |
| G0 B03-B tamper HMAC | `PASS_SCOPED_SOURCE` (unchanged) |
| G0 B03-C injective membership serialization | `PASS_SCOPED_INDEPENDENT` |
| **G0 algorithm/source-version binding of locked preassignment** | **`HOLD_G0_ALGORITHM_VERSION_BINDING`** |
| Production caller and G_post leakage handling | `PASS_SCOPED_SOURCE`; actual authoring execution pending |
| G1 standing research direction | `OWNER_STANDING_RESEARCH_DIRECTION_RECORDED` |
| **G2 protected source readback/custody** | **`G2_HOLD_SOURCE_LOCK_REBIND_NOT_VERIFIED`** |
| Final | **`HOLD_INTEGRATED`** |

**`GO_R8_D_CANDIDATE_AUTHORING_ONLY=NOT_AUTHORIZED`.** The integrated decision follows the existing G0/G2 gates with two independently identifiable blockers and no new science permit.

Recorded scientific state preserved: `R7=FROZEN_FAIL`; `R8=NOT_GENERATED`; `G3/G4=NOT_EXECUTED`; `G5/G6=SEALED`; `READER=0`; `GPU=NO`; `PROBE256=SEALED`. This review performed source-only CPU checks and control-plane reads, with no candidate/gold/rater creation, science dispatch, private TEST access, main merge, or historical QA rerun.
