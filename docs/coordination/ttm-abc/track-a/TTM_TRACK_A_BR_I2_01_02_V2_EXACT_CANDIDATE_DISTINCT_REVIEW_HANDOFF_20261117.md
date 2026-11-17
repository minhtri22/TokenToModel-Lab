# HANDOFF — Track A BR-I2-01/02 V2 exact-SHA F01–F06 distinct re-review

**Operation:** `TTM_TRACK_A_BR_I2_01_02_F01_F06_INTEGRATED_DESIGN_AMENDMENT_AND_EXACT_SHA_DISTINCT_REREVIEW_SINGLE_GATE`  
**Reviewer:** một phiên **khác người soạn Agent A**; đánh giá `SOURCE_ONLY · DESIGN_ONLY · NO_SCIENCE`.  
**PM authority:** [Issue #32 reviewer HOLD](https://github.com/minhtri22/TokenToModel-Lab/issues/32#issuecomment-6928014536) và [PM one-pack instruction](https://github.com/minhtri22/TokenToModel-Lab/issues/32#issuecomment-6927554428).  
**V1 exact design commit:** `20385e71cb5d2b8f3d7725229ab7a823e1044990` · **V1 independent decision:** `HOLD_DESIGN_AMENDMENT` (F01–F06).  
**I1 source:** `ec197b5f00d3a037420390edd11ee55047e1d37f`, independent review `e3e1c802815f4db1534e92d9848d6015eb9203cc`; `I1_MEASUREMENT_CLOSED_PASS_SCOPED`.

## Artifact set và custody

V2 is a **new** normative candidate; V1 historical files are unchanged. Review **current exact PR #33 HEAD** obtained from GitHub, not mutable branch alias. New files:
- `docs/coordination/ttm-abc/track-a/TTM_TRACK_A_BR_I2_01_02_V2_F01_F06_INTEGRATED_DESIGN_CONTRACT_20261117.md`
- `artifacts/ttm-abc/track-a/BR_I2_01_02_V2_F01_F06_NEGATIVE_QA_MATRIX_20261117.json`
- this handoff `docs/coordination/ttm-abc/track-a/TTM_TRACK_A_BR_I2_01_02_V2_EXACT_CANDIDATE_DISTINCT_REVIEW_HANDOFF_20261117.md`
- `docs/coordination/ttm-abc/status/TTM_TRACK_A_STATUS.json` (status update)

Pin and hash all Git blob IDs, compare V1 `20385e71cb5d2b8f3d7725229ab7a823e1044990` against new exact candidate, and compare I1 reviewed executable SHA `ec197b5f00d3a037420390edd11ee55047e1d37f` against new candidate. Require **no diff** to executable, workflows, historical verdicts, fixture, main, PR28, BC artifacts or `lineage.md`.

## F01–F06 distinct acceptance checklist

| Finding | Required falsification checks | Intended design delta |
|---|---|---|
| F01 self-hash | Whole-file payload cannot hash itself; envelope has payload SHA but not its own SHA | exact canonical byte domain + ordered external completion envelope |
| F02 parent-swap | Verify Win32 `SetFileInformationByHandle(FileRenameInfo, RootDirectory=hParent, relative leaf, ReplaceIfExists=FALSE)` semantics; attack ancestor swap and handle/ACL ambiguity | no path-based MoveFileExW fallback; native proof later |
| F03 deterministic final | Two writers to same scoped final, retry exact same journal transaction vs competitor | final scope_key stable, random only stage, no replace |
| F04 crash/replay | Crash before stage/after flush/after rename, stale journal, ledger consumed but result unknown | dual FSM (receipt vs science), at-most-once dispatch and fail-closed |
| F05 signer authority | Distinct keys but same principal; revoked policy; unsigned PM GitHub comment; old vs new phase mismatch | issuer + attestations, separate signed permit, `I2_RUN -> run` only future adapter |
| F06 QA | Positive schema parity, duplicate JSON keys, mutated final, signer key custody substitution | machine-readable oracles with 0/0 executed |

## Matrix and burden

**50 prospective negative cases**: authority 21, atomicity 23, integrated 6; tiers 27 future source, 23 future native. **3 positive controls** with the same `setup/stimulus/expected/oracle/evidence/tier/execution` fields. Author schema self-check **is not** native QA or independent review. Actual executions: `0/50` and `0/3`.

**Distinct reviewer outcome must be exactly:** `DESIGN_ACCEPT_SCOPED` **or** `HOLD_DESIGN_AMENDMENT`, with exact new Git SHA, per-F01–F06 findings, noted unresolved native-proof caveats. Do not issue `I2_GO` or bypass historical guard. Independent AI review must be identified as AI, not misrepresented as a human signature or Windows native execution.

## PM handback

Send result and exact evidence to PM Issue #32 under `TTM_PM_ABC_OWNER_PROSPECTIVE_RELEASE_READINESS_AND_EXACT_MERGE_DEPENDENCY_REVIEW_SINGLE_GATE` for **one** R0–R8 owner decision packet, not a Track A micro-permit. Preserve `I1_CLOSED`, `I2_NOT_EXECUTED`, `OWNER_RELEASE_HOLD`, `PR33_DRAFT`, `NO_MERGE`.

**Bước thực hiện tiếp theo — duy nhất:** distinct V2 design re-review at the new exact Git commit, then PM one integrated A/B/C decision. No owner/native/science dispatch.
