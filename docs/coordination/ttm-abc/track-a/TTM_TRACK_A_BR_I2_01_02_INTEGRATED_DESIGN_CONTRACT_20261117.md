# Track A — Hợp đồng thiết kế tích hợp BR-I2-01 / BR-I2-02

**Ngày:** 2026-11-17 · **Chế độ:** `DESIGN_ONLY · SOURCE_REVIEW_ONLY · NO_IMPLEMENTATION · NO_I2`  
**Operation:** `TTM_TRACK_A_I2_RELEASE_BARRIER_TOCTOU_ATOMICITY_AND_OWNER_AUTHORITY_DESIGN_SINGLE_GATE`  
**Repository/branch:** `minhtri22/TokenToModel-Lab` / `research/ttm-track-a-small4m-diagnosis-20261116`  
**Gói điều phối:** [PM Issue #32 / quyết định thiết kế](https://github.com/minhtri22/TokenToModel-Lab/issues/32#issuecomment-6927554428) — tiểu mục của `TTM_PM_ABC_OWNER_PROSPECTIVE_RELEASE_READINESS_AND_EXACT_MERGE_DEPENDENCY_REVIEW_SINGLE_GATE` và R0–R8. **Không có tiểu permit.**

## A. Tình trạng và những gì KHÔNG được sửa

- PM đã đóng `I1_PASS_SCOPED_MEASUREMENT` cho M0 v3 tại **exact executable source** `ec197b5f00d3a037420390edd11ee55047e1d37f`; 35/35 F01/F02 + 38/38 native custody + 80/80 case và 5/5 nhóm tại [review evidence `e3e1c802815f4db1534e92d9848d6015eb9203cc`](https://github.com/minhtri22/TokenToModel-Lab/blob/e3e1c802815f4db1534e92d9848d6015eb9203cc/artifacts/ttm-abc/track-a/M0_V3_POST_HOLD_DISTINCT_I1_20261117/REVIEW.md).
- Tokenizer TRAIN-only BPE: `cba18e60cee3d08a353ee6d4a451017289e45af7b4b1179c87171b9b78d7dfdc`; fixture records `823a08dd4be0da7748cb258b9bf5b2841dd1fdbac84956eb204be7ba57f8c55d`; manifest `0b80368a6747994df5f5b8d0e7b35137266ac82f6c9b83d26af5b61f79b3cb04`; original freeze receipt `b82a7ebc29930563db581f7724d0847a725d893860b776b7cc682ec875af4c3a`.
- **Không thay đổi** old HOLD verdict, I1 scorer/runner, `owner_internal_admission.py`, `release_auth_v2.py`, `Invoke-TrackA-M0V3-RealTokenizer-Freeze-PS51.ps1`, QA scripts, private fixture hoặc `lineage.md`. Không mở checkpoint, không thực hiện model forward, không nonce, không merge.
- [Draft PR #33](https://github.com/minhtri22/TokenToModel-Lab/pull/33) stacked on PR #28 `ebdc54575eed1ff60c402eecf60289f408bb38ca`. Owner release preflight **HOLD exit 2** / `HOLD_OWNER_INTERNAL_I1_NOT_PASS`. `I2=NOT_EXECUTED`.

## B. Kiểm kê đường kiểm soát đang có (không suy diễn là đã PASS)

| Bộ phận | Quan sát source thực | Ý nghĩa thiết kế |
|---|---|---|
| `owner_internal_admission.py` | `VERDICT_URL` trỏ tới historical Q001 verdict; `validate_verdict` yêu cầu literal `I1_PASS_SCOPED_INTERNAL_RESEARCH`, so exact `SCOPE`, `RUNTIME_FILES` SHA, UTC expiry và fixture digest | I1 M0 v3 PASS là **protocol khác**; không được tráo đổi literal hay repoint URL mù để PASS |
| `release_auth_v2.py` | `TRUSTED_ED25519_PUBLIC_KEYS={}` (fail closed), cần ba vai trò owner, distinct reviewer, rights custodian; permit pin phase/root/host/checkpoint/runner/tokenizer và nonce | Một báo cáo đo lường PASS **không phải** chữ ký GO; trust anchors/owner authority vẫn thiếu |
| `Track A readback OnePack` | Kiểm SHA của records, manifest, BPE; đọc metadata, tạo receipt; `Test-Path` rồi `WriteAllText` | Có check/write race, thiếu chứng cứ publish nguyên tử, reparse/ACL/handle-trust; I1 independent checker bù custody, **không phát hành** |
| PM R0–R8 | Program-level `HOLD_ALL_PROSPECTIVE_RELEASES` gồm source, gold, rights, checkpoint, resource, filesystem, prereg, distinct QA và owner | Hai BR là **đầu vào** của duy nhất một quyết định owner A/B/C, không phải hai cổng cho phép chạy riêng |

## C. BR-I2-01 — Owner authority bridge, không làm sai lệch lịch sử

**Nguyên tắc:** `MeasurementCertificate != ReleasePermit`. Chứng nhận M0 v3 có thể được **tham chiếu**, không thể tự tạo hoặc sửa quyền phát hành.

### C1. Proposed immutable `MeasurementCertificateV1` (không phải permit)

Trường bắt buộc: `schema_version`, `question_id`, `measurement_scope=M0_V3_ONLY`, `source_commit=ec197b5f00d3a037420390edd11ee55047e1d37f`, `scorer_sha256_lf=2d0b980768a0ac3079f361d94244cd694c97ed90e978fc83fb7991dc82b5c2ac`, `runner_sha256_lf=20c147f9f2629c494c157da5bab3519e01d755096638adfd10e07bb5dda3c4b8`, `fixture_records_sha256=823a08dd4be0da7748cb258b9bf5b2841dd1fdbac84956eb204be7ba57f8c55d`, `fixture_manifest_sha256=0b80368a6747994df5f5b8d0e7b35137266ac82f6c9b83d26af5b61f79b3cb04`, `tokenizer_bpe_sha256=cba18e60cee3d08a353ee6d4a451017289e45af7b4b1179c87171b9b78d7dfdc`, `independent_evidence_commit=e3e1c802815f4db1534e92d9848d6015eb9203cc`, frozen reviewer/report/receipt *Git blob IDs* and sha256, `distinct_35_of_35`, `native_custody_38_of_38`, `owner_pm_closure_record_blob`, `decision=I1_PASS_SCOPED_MEASUREMENT`, `release_authorization=false`. Keep historical HOLD and old runtime pins as append-only references.

**Custody chain:** compare every public Git blob to its pinned ref and digest; require reviewer/PM identities and approved signing provenance (GitHub account alone is insufficient); no mutable branch HEAD as sole authority; fail closed if document missing, unsigned, malformed, reused or unexpectedly changed. A reviewer session ID is provenance, **not** a cryptographic signature.

### C2. Proposed independent `ReleaseAuthorizationV1` / admission overlay

A **separate** prospectively signed object, valid for a single phase and environment only, with: pinned measurement-certificate SHA, reviewed policy/validator source SHA and trust-anchor revision, explicit `phase=I2_RUN`, QID, source/runtime-file exact SHA map, trusted root+host, pinned checkpoint/tokenizer/fixture/manifest, rights source, independent QA digest, resource and filesystem custody receipts, prereg scope, expiry UTC, revocation reference, one-shot nonce/ledger commitment, and explicit **fresh owner decision**. Required signer roles and independence must be defined by the integrated program authority, not supplied by the permit itself. `release_auth_v2` currently requires **three distinct Ed25519 roles**; no keys are configured. Correct this only under separately reviewed implementation source and one consolidated PM decision; **do not seed arbitrary keys**.

**Admission sequence (proposed, not executed):** resolve *exact* immutable source and owner/PM record → validate authentic `MeasurementCertificateV1` → validate policy/trust anchors and independent signatures on prospective release object → evaluate R0–R8 prerequisites → verify expiry/revocation and one-shot resource constraints → evaluate native filesystem custody under trusted root → **only then** permit one-shot nonce claim and checkpoint access. Any unknown condition = HOLD. No permissive fallback, no implicit I2 GO derived from a status file or unsigned issue comment.

**Compatibility contract:** old `VERDICT_URL`, `VERDICT_PATH`, old `SCOPE`/runtime map/expiry and historical `HOLD_I1` remain immutable. Versioned bridge explicitly distinguishes `I1_PASS_SCOPED_MEASUREMENT` from legacy `I1_PASS_SCOPED_INTERNAL_RESEARCH` and records a new signed decision rather than editing the old verdict. The policy/protocol transition needs its own exact-source implementation review, but not a new PM micro-permit.

## D. BR-I2-02 — Atomic receipt, no overwrite, custody

### D1. Transactional design (Windows 11/PS5.1, prospective)

1. **Admission precondition**: exact root and host, pinned source LF/CRLF bytes, physical filesystem and volume. Confirm supported **local NTFS** semantics and same-volume staging/final; unknown FS or SMB = HOLD. Do not use path string checks alone.
2. **Handle-based input custody:** open root/parents/fixture/manifest/BPE/freeze receipt with Win32 handles and explicit no-reparse policy (`FILE_FLAG_OPEN_REPARSE_POINT` plus tag/identity inspection, not assumed sufficient alone). Verify canonical volume+file identities, expected ACL and no untrusted writer, SHA of each *opened* byte stream and 80 case/5 group digests. Reject junction, symlink, ADS, unexpected hardlink, redirected ancestor or concurrent replacement. Keep verified identities/handles pinned until commit. Existing I1 fixture stays read-only.
3. **Stage** a new receipt file **inside a verified same-volume directory** with unpredictable transaction suffix and create-new exclusive semantics (`CREATE_NEW`; never `OPEN_ALWAYS` / overwrite). Serialize a canonical UTF-8 schema version, one terminal LF, no private context/tokens. Include all input SHA, I1 exact source/evidence, file identity snapshot, transaction nonce distinct from *science* one-shot nonce, and `science_executed=false`.
4. Flush the **staging file** via `FlushFileBuffers` and independently hash the bytes from the opened handle. Verify source identities+digests again before publication. Abort on source mutations; leave staging as quarantined evidence, do not delete automatically.
5. **Atomic publication**: one native same-volume **rename without replace** to previously unused final receipt name, using a Windows primitive with independently verified failure semantics for existing target (e.g. `MoveFileExW` without `MOVEFILE_REPLACE_EXISTING`; exact primitive is an implementation choice requiring native proof). Do not treat `Test-Path` as a lock. Simultaneous publishers: at most one succeeds, loser must HOLD with unchanged final bytes.
6. Open final file through verified directory handle, rehash bytes and compare with staged hash, verify file identity/mount and no reparse. Write a separate immutable sanitized completion record if needed, also atomically. Crash after publish but before stdout: return **idempotent exact-hash acknowledgement**, not rewrite. Power-loss durability of directory-entry rename must be **tested separately**; atomic namespace publish is not a claim of complete durable storage.
7. STOP on any ambiguous Windows API outcome, unsupported FS, ACL provenance, reparse tag, post-write digest drift, partial crash or inconsistent local/remote evidence. No recovery via truncation/replace/delete of frozen assets.

**Critical:** input-handle locking and authorization of directory mutations are not interchangeable with an early `Path.resolve()`/PowerShell `Test-Path`. NTFS behavior, share modes, ACL and reparse-point race safety must be demonstrated on owner Windows host with a concurrent adversary harness. Any primitive without proven atomic **no-replace** semantics => HOLD.

### D2. Receipt schema (proposal)

`ttm.track_a.br_i2.receipt.v1`: `source_commit`, `release_policy_sha256`, `measurement_cert_sha256`, `i1_result=PASS_SCOPED`, `fixture_records_sha256`, `fixture_manifest_sha256`, `freeze_receipt_sha256`, `tokenizer_sha256`, `source_blob_lf_sha256`, `source_checkout_sha256`, `volume_id`, `file_ids`, `parent_handle_chain`, `writer_identity`, `transaction_id`, `staging_sha256`, `published_sha256`, `publication_outcome`, `science_executed=false`, `I2=NOT_EXECUTED`. Sensitive internal host paths and full raw IDs remain private; public receipt stores hashes and scoped identifiers only. The receipt **does not grant I2**.

## E. Gates, matrix và nghiệm thu

- [Ma trận negative QA máy đọc được](../../../../artifacts/ttm-abc/track-a/BR_I2_01_02_NEGATIVE_QA_MATRIX_20261117.json): **43 prospective negative cases** (18 authority, 20 atomicity, 5 cross-gate), **3 positive controls**. **ALL NOT_EXECUTED_DESIGN_ONLY**, not QA PASS.
- Distinct reviewer must audit the **exact design commit** and every negative's falsifier/expected fail-close, identify weak primitives or omitted attacks, and return **DESIGN_ACCEPT_SCOPED** or **DESIGN_HOLD**; a design PASS does not confer runtime QA PASS.
- Future implementation (if and only if PM admits it in the **single integrated program packet**) must run full synthetic source QA plus **owner-native Windows PS5.1 / Python3.12, NTFS concurrent process race, crash, junction/reparse/ACL, File ID and signer/auth source QA**, all SHA-pinned. Independent actor re-runs no-skip negatives; release preflight must remain HOLD until owner independently authorizes an exact I2 prospective decision and all R0–R8 are proven.
- Cross-check no changes to I1 code at `ec197b5f00d3a037420390edd11ee55047e1d37f`, historical FAIL/HOLD, private fixture bytes, `main`, `lineage.md`, PR #28, Track B/C, and no real science. Distinguish technical feasibility, science evidence and owner release authority.

**PM disposition requested:** `ACCEPT_DESIGN_SCOPED` or `HOLD_DESIGN_AMENDMENT`. In both cases `HOLD_ALL_PROSPECTIVE_RELEASES` remains unless a later explicit integrated PM owner release is separately issued after native independent proofs.

**Operation complete only as documentation:** `DESIGN_PACKET_SOURCE_ONLY · NEGATIVE_QA_PLANNED_NOT_EXECUTED · DISTINCT_QA_NOT_EXECUTED · I1_CLOSED · I2_HOLD · NO_MERGE`.
