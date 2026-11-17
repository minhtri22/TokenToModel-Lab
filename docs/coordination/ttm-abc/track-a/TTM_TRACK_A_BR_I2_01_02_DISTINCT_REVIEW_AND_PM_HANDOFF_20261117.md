# HANDOFF — Track A BR-I2-01/02 · Independent design acceptance / PM integration

**Ngày:** 2026-11-17 · **Vai trò nhận:** reviewer khác Agent A / PM integrated-release reviewer.  
**Authority:** [PM Issue #32 — decision comment #6927554428](https://github.com/minhtri22/TokenToModel-Lab/issues/32#issuecomment-6927554428), **không phải cấp quyền I2**.  
**Operation:** `TTM_TRACK_A_I2_RELEASE_BARRIER_TOCTOU_ATOMICITY_AND_OWNER_AUTHORITY_DESIGN_SINGLE_GATE`  
**Parent PM one-packet:** `TTM_PM_ABC_OWNER_PROSPECTIVE_RELEASE_READINESS_AND_EXACT_MERGE_DEPENDENCY_REVIEW_SINGLE_GATE`.

## Handoff bytes and review scope

Exact-reviewed measurement source SHA `ec197b5f00d3a037420390edd11ee55047e1d37f`. I1 independent adjudication evidence SHA `e3e1c802815f4db1534e92d9848d6015eb9203cc`. Design base branch SHA `f7d6153fdae526b12303d324ccb7a271adee376b`. Current design HEAD: use exact Git HEAD and independently hash **design contract**, **negative matrix**, **handoff** and **status** at the reviewed source commit; never approve against a mutable branch name alone.

Artifacts:
1. `docs/coordination/ttm-abc/track-a/TTM_TRACK_A_BR_I2_01_02_INTEGRATED_DESIGN_CONTRACT_20261117.md`: authority bridge, non-overwriting historical I1, versioned certificates vs release permits, proposed Windows atomic receipt protocol.
2. `artifacts/ttm-abc/track-a/BR_I2_01_02_NEGATIVE_QA_MATRIX_20261117.json`: **43 design-only negative cases + 3 positive controls**, every case explicitly `NOT_EXECUTED_DESIGN_ONLY`.
3. This handoff and PM Issue #32. **Do not request another independent Track A-specific release permit.**

## Exact obligations for distinct design reviewer

- Verify genuine historic I1 closure: **35/35 F01/F02, 38/38 custody, 80/80 cases, 5/5 groups**, frozen records SHA `823a08dd4be0da7748cb258b9bf5b2841dd1fdbac84956eb204be7ba57f8c55d`, manifest `0b80368a6747994df5f5b8d0e7b35137266ac82f6c9b83d26af5b61f79b3cb04`, no source modification.
- Inspect actual `owner_internal_admission.py` (`VERDICT_URL`, legacy `validate_verdict`, exact runtime SHA and expiry), `release_auth_v2.py` (3 signatures, empty trust anchor map, fail closed) and Windows OnePack. Reject design if it treats unsigned PM issue text, owner status JSON, or measurement certificate as I2 permit.
- Threat-model each negative and positive case: signer/key substitution, old/new verdict confusion, expiry/replay, wrong phase/source SHA, reparse/junction/ancestor substitutions, ACL/hardlink, temp vs final race, crash windows, duplicate publishers, unsupported filesystem and post-publish byte drift. Mark not applicable only with a rigorous frozen trust-boundary proof. No skips in required future QA.
- Check native-API semantics for `CREATE_NEW`, same-volume **rename no replace**, FlushFileBuffers, opened-handle identity, parent directory races, final-file rehash, retry behavior. Do not accept `Test-Path` + `WriteAllText` as atomic. Distinguish namespace atomicity from power-loss durability, and local NTFS from remote/unsupported filesystem.
- Review no checkpoint/model forward/optimizer/nonce, no generated private fixture, no release guard edits, no PR merge/main/lineage and no new program-level micro-permits. Confirm PR #33 remains Draft and stacked on PR #28.
- Issue a source-only conclusion **`DESIGN_ACCEPT_SCOPED`** or **`HOLD_DESIGN_AMENDMENT`**, with exact SHA and falsifier-specific analysis. Record reviewer independence and send verdict to **PM Issue #32**, not an alternate owner authority path. Do **not** label prospective negatives PASS as executed.

## Proposed independent acceptance matrix

| Gate | Acceptance predicate | Current |
|---|---|---|
| D0 Immutable scope | I1 source/evidence pins, no changed code | Source pinned; independent design check PENDING |
| D1 Authority | Measurement certificate ≠ signed release permit; old HOLD preserved | DESIGN_SPECIFIED_ONLY |
| D2 Signing | Three distinct approved trust anchors, explicit owner decision and environment | **HOLD_IMPLEMENTATION_UNAUTHORIZED** |
| D3 Atomic receipt | native no-replace + handle-bound custody + concurrent/crash proof | **HOLD_NATIVE_QA_NOT_EXECUTED** |
| D4 Negative tests | 43/43 required prospective negatives + 3 positive controls (no skips) | **NOT_EXECUTED** |
| D5 PM R0–R8 | one consolidated program GO/HOLD, not independent Track A permit | **HOLD_ALL_PROSPECTIVE_RELEASES** |
| D6 Science | I2 not launched, no checkpoint/nonce; keep frozen fixture | **NOT_EXECUTED** |

**Bước tiếp theo — duy nhất:** `TTM_PM_ABC_OWNER_PROSPECTIVE_RELEASE_READINESS_AND_EXACT_MERGE_DEPENDENCY_REVIEW_SINGLE_GATE`: PM incorporates the reviewed Track A design and all other program R0–R8 evidence into one owner GO/HOLD decision. No separate Track A permit and no science dispatch.

**Closure expectation:** `DESIGN_ONLY_SUBMITTED_FOR_DISTINCT_QA · I1_MEASUREMENT_CLOSED · I2_RELEASE_HOLD · NO_IMPLEMENTATION · NO_MERGE`.
