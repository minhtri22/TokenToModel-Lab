# HANDOFF — Track A BR-I2-01/02 V4 exact-SHA distinct design review

**Operation:** `TTM_TRACK_A_BR_I2_01_02_V4_PAYLOAD_HASH_DOMAIN_AND_RELEASE_POLICY_EPOCH_INTEGRATED_AMENDMENT_ONEPACK` · **Mode:** `DISTINCT AI REVIEW · SOURCE_ONLY · DESIGN_ONLY · NO_SCIENCE`  
**Repo:** `minhtri22/TokenToModel-Lab` · PR #33 Draft/unmerged stacked on PR #28 `ebdc54575eed1ff60c402eecf60289f408bb38ca`.  
**V3 independently reviewed exact SHA:** `f97298098c12c55a3abb00cddd757dfde7b364ac` · [V3 HOLD / F01 & F05](https://github.com/minhtri22/TokenToModel-Lab/issues/32#issuecomment-6936941604).  
**I1 source accepted:** `ec197b5f00d3a037420390edd11ee55047e1d37f` — `I1_PASS_SCOPED_MEASUREMENT` preserved; I2 `NOT_EXECUTED`.

## Input to reviewer — fetch fresh exact PR HEAD, never accept mutable branch alias

- `docs/coordination/ttm-abc/track-a/TTM_TRACK_A_BR_I2_01_02_V4_PAYLOAD_DUAL_HASH_RELEASE_EPOCH_CONTRACT_20261117.md`: V4 two-digest receipt envelope + signed release epoch, archived V3 slot/final/scoped pass.
- `artifacts/ttm-abc/track-a/BR_I2_01_02_V4_EXACT_DOMAIN_TEST_VECTORS_20261117.json`: 8 tagged SHA-256 synthetic vectors (6 byte-identical V3, 2 redefined V4), V3 PAYLOAD `RAW=a4bca0d2d9d64b2c3b1882764abf421fe872e671e42fa1a62a8147d2675c55b4`, `TAG=e27ae8e39fbd669e152339b271ef69034f69564063d57f286dbc878bc433ce55`, V4 release `c3cf68c0ad731a127857dc20248b419ca21f0247475304426f3803c9a78dbac3`, V4 completion `7151df6bbca3b7e8ff8f2bff520795ce4431efc620438958448a97f4f5f6f5df`.
- `artifacts/ttm-abc/track-a/BR_I2_01_02_V4_NEGATIVE_POSITIVE_QA_MATRIX_20261117.json`: **65 negative** (from 60 V3 IDs + 5 new direct F01/F05 probes), **3 positive**; all 68 `NOT_EXECUTED_DESIGN_ONLY`.
- `artifacts/ttm-abc/track-a/BR_I2_01_02_V4_AUTHOR_STATIC_READBACK_20261117.json`: author-only static readback, **not** independent/native.
- `docs/coordination/ttm-abc/status/TTM_TRACK_A_STATUS.json`: keeps release and implementation HOLD.
- Historic V1/V2/V3 files and review comments must stay unchanged.

## Exact distinct review obligations

1. Verify V3 SHA `f97298098c12c55a3abb00cddd757dfde7b364ac` → V4 has only new scoped design/artifact/status files, one commit. Compare reviewed I1 source `ec197b5f...` → V4; no executable/workflow/lineage changes. Independently recompute SHA1 of new Git blobs.
2. Recompute `SHA256(canonical_payload_ascii)` **RAW** and `SHA256(V3/PAYLOAD||00||canonical_payload_ascii)` **TAG**. Confirm distinct values, both present in closed `CompletionEnvelopeV4` and independently enforced by its verification order. Recompute V4 envelope `H_ENVELOPE` and unchanged six V3 tagged vectors.
3. Parse `ReleaseTBSV4` and confirm mandatory `policy_epoch:uint53_positive` is *within exact canonical signed preimage*, with `TBS.epoch=detached.epoch=trusted_policy.epoch>=antirollback_floor`; compare policy raw digest and reviewed trust anchor. Recompute tagged V4 release digest and inspect domain-separated role-specific signature preimage (no actual signing).
4. Check new `ATOMIC-28/29` swap/lone field, `AUTH-26/27` epoch mutation/rollback, `INTEG-09` mixed-version downgrade. Check 65 unique negative + 3 positive schema and POS-02 two-writer setup. **No runtime tests have been executed.**
5. Preserve F02/F03/F04 scoped design assessment and **HOLD native proof**. Ensure **frozen V3 global SLOT digest unchanged** across V4; no extra one-shot by schema versioning.
6. Return exactly **`DESIGN_ACCEPT_SCOPED`** or **`HOLD_DESIGN_AMENDMENT`** with exact V4 commit and per-F01–F06 reasons. This is AI source/design review, not owner, real signatures, Windows native QA or I2 execution.

## PM handback and next step — single gate

Post result to [PM Issue #32](https://github.com/minhtri22/TokenToModel-Lab/issues/32), for **one** A/B/C integrated `TTM_PM_ABC_OWNER_PROSPECTIVE_RELEASE_READINESS_AND_EXACT_MERGE_DEPENDENCY_REVIEW_SINGLE_GATE` R0–R8 decision. Do not issue Track A micro-permits; no historical release guard edits, real fixture modifications, GPU, checkpoint/model forward, nonce claim, owner GO, PR merge or `lineage.md` edit.

**Expected after author amendment:** `V4_DESIGN_CANDIDATE · INDEPENDENT_V4_REVIEW_PENDING · I1_CLOSED · I2_HOLD · NO_MERGE`.
