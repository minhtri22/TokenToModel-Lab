# HANDOFF — PR #20 F01–F04 distinct new-HEAD QA

**Operation:** `TTM_PR20_F01_F02_F03_F04_DISTINCT_NEW_HEAD_SOURCE_QA_SINGLE_GO_HOLD`

**Repo:** https://github.com/minhtri22/TokenToModel-Lab

**PR:** https://github.com/minhtri22/TokenToModel-Lab/pull/20

**Original reviewed HEAD:** `cc665c8264df92ddaeeb0e0af7bd2cf0793be172`; **main base pin:** `fbe4a1ed58eef66f896bbfe0471926b7cc45298e`. Read **the new PR #20 HEAD** after integrated remediation, verify it has exactly one new remediation commit on top of the original HEAD. PR must remain Draft, unmerged.

## Independent tests required

1. Rehash all PR changed artifacts including new author receipt and this handoff (Git blob SHA-1 and SHA-256); compare against source SHA. Confirm `lineage.md` blob unchanged from old PR HEAD and L0000–L0029 append-only compared with main.
2. F01 correct pin #24 `9110d101601e6ebfb64d9804f3704a90cb284420` from `0ec28d44587fde9ad4acba8cccae65648e367181:lineage.md` in both inventory and receipt; no change to FRESH16 V2 FAIL scope.
3. F02 check commit ancestry PR19 source `c6b3ec442eb7313851f05d53096d1588223a9d14` vs `fbe4a1ed58eef66f896bbfe0471926b7cc45298e` is DIVERGED and trees equal `7177eb04f806c2a51aa3d7dc3ab674928d081146`; equal-tree is not ancestor relation.
4. F03 VM R8 snapshot `12540962e96caef34c587e7a8ba59d58fd09c5c4` historical, observed remote HEAD `8dec9438bff96922e5defd64550971c309d5b32f` on 15/11. Do not rebind historical claim; new HEAD science QA NOT_EXECUTED. G0/G1/G2 HOLD.
5. F04 dedup source of the two T5 branches `archive/ttm-ollama-full-logits-scoped-20261111`, `research/ttm-t5-ollama-full-logits-20261111`: same `99ca9eee4114c8bf4b9b8521cc642bb71b054f05` and `737ae1012a343319ba0f20fd4e62cc95c9aae612`, 27 pin references and 26 unique Git blobs; do not count as independent replication.
6. Check 65 snapshot branches, 23 with missing terminal QA, priority P1/P2/P3, source gate/status, rights, branch merge metadata. No science inference from readback.
7. Diff contains docs/governance and artifacts/governance only plus original append-only `lineage.md`; no code, checkpoints, sealed TEST/gold, owner permit or main modifications.

**Output:** one independent Markdown report + JSON receipt, unique GO/HOLD decision: `GO_DOCS_ONLY_PR20_MERGE_CANDIDATE` or `HOLD_PR20_SOURCE_QA_OR_GOVERNANCE_CONTRACT`. GO only means documentation candidate, never permission to merge without owner approval. No reruns of old scientific QA.

**Preserve:** `D1_BRIDGE_SCIENCE=HOLD`, `D1_R1=CLOSED_DESIGN_HOLD`, `TEST_Q1Q2=SEALED`, `FC02=NOT_OPENED`, `GPU=TRAINING=INFERENCE=0`, `FROZEN_V6=UNCHANGED`.
