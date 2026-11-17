# HANDOFF — TTM Track A BR-I2-01/02 V3 exact-candidate DISTINCT design review

**Operation:** `TTM_TRACK_A_BR_I2_01_02_V3_F01_F04_F05_F06_EXACT_SCHEMA_SCOPE_SIGNATURE_FALSIFIER_AMENDMENT_AND_DISTINCT_REREVIEW_ONEPACK`  
**Mode:** `DISTINCT AI REVIEW · SOURCE_ONLY · DESIGN_ONLY · NO_SCIENCE`  
**Repo:** `minhtri22/TokenToModel-Lab` · **PR #33:** Draft/open/unmerged · stacked PR #28 unchanged.  
**Reviewed source I1:** `ec197b5f00d3a037420390edd11ee55047e1d37f` · **I1 independent receipt:** `e3e1c802815f4db1534e92d9848d6015eb9203cc` · `I1_PASS_SCOPED_MEASUREMENT` still CLOSED.  
**Previous V2 exact source:** `7438e0c16860e69f063307fed5886a5f6bee211b` · [independent V2 `HOLD_DESIGN_AMENDMENT`](https://github.com/minhtri22/TokenToModel-Lab/issues/32#issuecomment-6936401307).  
**V3 SHA:** resolve actual GitHub PR #33 HEAD after amendment and PIN full 40 hex, not the mutable branch alias. The reviewer must not be the V3 author session. No native re-run or signer operation implied.

## Exact new V3 artifacts

- `docs/coordination/ttm-abc/track-a/TTM_TRACK_A_BR_I2_01_02_V3_CLOSED_SCHEMA_SCOPE_TBS_INTEGRATED_CONTRACT_20261117.md`: closed required-field typed wire schemas, NUL-separated digest domains, global Q001 one-shot identity, detached TBS signature domains, retained F02/F03.
- `artifacts/ttm-abc/track-a/BR_I2_01_02_V3_BYTE_EXACT_TEST_VECTORS_20261117.json`: 8 exact ASCII valid synthetic vectors with expected SHA256, 12 invalid vector attacks. **No real owner signatures or permits.**
- `artifacts/ttm-abc/track-a/BR_I2_01_02_V3_NEGATIVE_POSITIVE_QA_MATRIX_20261117.json`: all 50 historical V2 negative cases + 10 direct new F01/F04/F05/F06 cases, 3 positive controls; `POS-02` explicitly sets two competing publishers.
- `artifacts/ttm-abc/track-a/BR_I2_01_02_V3_AUTHOR_SCHEMA_SOURCE_QA_RECEIPT_20261117.json`: author-only static schema/source integrity checks; not distinct review. `docs/coordination/ttm-abc/status/TTM_TRACK_A_STATUS.json`: Track A DESIGN_ONLY/HOLD.
- Historical V1/V2 documents and reviewer HOLD comments remain unchanged.

## Mandatory distinct design probes

| Finding | Independent acceptance checks | Scope |
|---|---|---|
| **F01** | All closed field sets/typed hashes, checkpoint absent-vs-null, raw ASCII wire exact sorted keys & one LF, no self-hash; independently recompute 8 SHA-256 prefix+NUL vectors | Need full schema and byte oracle, not prose only |
| **F02** | `SetFileInformationByHandle` handle-root/relative name, ancestor FileId+ACL and share lock; reject parent moved outside root unchanged FileId | DESIGN_ONLY acceptance ≠ native proof |
| **F03** | Stable final scope key excludes random tx/permit revision; POS-02 **two concurrent writers** same deterministic final, one winner/one HOLD | No overwrite/idempotence |
| **F04** | Scientific intent equivalence: Q001 I2 family policy-owned registry, not permit ID; same science with *two different applicant scope IDs* must reject before ledger; global ledger and crash ambiguity HOLD | Must not mint extra one-shot |
| **F05** | No signature/self-reference in any TBS; role/kind domain-separated raw preimage, detached envelopes; key/principal/epoch binding and `I2_RUN→run` only future trusted adapter | No fabricated signatures |
| **F06** | Verify 60/60 negative + 3/3 positive **SCHEMA**, 0/63 actual QA executions; direct SELF_HASH/TBS mutation/different scope ID cases and POS-02 stimulus match oracle | No schema PASS⇒science PASS |

**Exact-candidate custody:** compare V2 `7438e0c16860e69f063307fed5886a5f6bee211b` → V3 HEAD for only the six design artifacts, and accepted I1 executable `ec197b5f00d3a037420390edd11ee55047e1d37f` → V3 for no code/CI/workflow/lineage diff. Independently hash all new Git blobs, recompute vector-domain SHA-256. Flag any unexpected source/branch mutations. Do not claim re-running private fixture, Windows native tests, signers or science.

**Review verdict requested:** exactly `DESIGN_ACCEPT_SCOPED` or `HOLD_DESIGN_AMENDMENT` against **new V3 exact SHA**, separate F01–F06 disposition and blocking falsifiers. Send to [PM Issue #32](https://github.com/minhtri22/TokenToModel-Lab/issues/32) for **one** `TTM_PM_ABC_OWNER_PROSPECTIVE_RELEASE_READINESS_AND_EXACT_MERGE_DEPENDENCY_REVIEW_SINGLE_GATE` adjudication. Design PASS is not implementation/owner release GO.

**Bước thực hiện tiếp theo — duy nhất:** distinct V3 exact-candidate review, then one PM A/B/C R0–R8 decision; no Track A micro-permit.
