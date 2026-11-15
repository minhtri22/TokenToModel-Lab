# TTM VM V4 R8 — G2 Production trust-boundary & ledger antirollback implementation

**Operation:** `TTM_VM_V4_R8_G2_PRODUCTION_TRUST_BOUNDARY_AND_LEDGER_ANTIROLLBACK_INTEGRATED_IMPLEMENTATION_SINGLE_GATE`

**Ngày:** 15/11/2026 (Asia/Bangkok) · **Vai trò:** Implementation Agent (không phải reviewer độc lập)

**Phán xử:** `PASS_SCOPED_IMPLEMENTATION_SOURCE_QA_79_OF_79` · **`G2_HOLD · HOLD_INTEGRATED`**.

## 1. Exact input và nguồn sự thật

- Frozen scientific source: [`84d9d5c95e9962ccfe294852570e261b145fe403`](https://github.com/minhtri22/TokenToModel-Lab/commit/84d9d5c95e9962ccfe294852570e261b145fe403); **không chỉnh sửa**.
- Source candidate trước: `2c6aee6d9644bd2035c4624ab12f1b524a11e6e0` (35 fixture tests).
- Independent F01–F09 review: [`94b377ce…`](https://github.com/minhtri22/TokenToModel-Lab/commit/94b377ce6c0d6aa9e1d08ae4ff628c215449be1f).
- New four-file implementation source: [`5bba59b12d5b0541c717b04245c5b1862b064718`](https://github.com/minhtri22/TokenToModel-Lab/commit/5bba59b12d5b0541c717b04245c5b1862b064718).
- New public-safe source-QA ZIP committed to GitHub at [`92fce2ec8ce0359d5e696f1607beecf4a83fd6b1`](https://github.com/minhtri22/TokenToModel-Lab/commit/92fce2ec8ce0359d5e696f1607beecf4a83fd6b1).
- Owner scope: `R8_D_EXPLORATORY_DESCRIPTIVE_ONLY`. Không backup độc lập là `OWNER_ACCEPTED_RISK`, recovery `NOT_VERIFIED`. Retention amendment ở `b1231fa` vẫn `PROPOSED_NOT_EFFECTIVE`.

## 2. Những gì đã triển khai thực sự

**`g2_production_boundary.py`:**

1. Canonical JSON strict, nonce, exact blueprint/lock SHA-256 và algorithm/version/source commit binding; không chấp nhận duplicate JSON, NaN, lone surrogate.
2. `FrozenCodeVerifier` đọc lại hash **byte thật** của `folds_raters.py` và `r8_production_caller.py` trước khi import; kiểm SHA-256 manifest, Python 3.12, executable SHA đã pin và versions NumPy/SciPy/scikit-learn trong production. Code source và runtime phải khớp với byte đã khóa.
3. `validate_hmac_v2` tái tính `preassign_r8` với khóa lấy qua `CustodianPort.use_private_key` và so HMAC, fold, component, schema, CV; không dựa vào hai chuỗi hex giả để chấp nhận. Không tạo khóa hoặc tái phân bổ.
4. `GhReleaseVerifier` dùng `gh release verify` và `gh release verify-asset` có kiểm chữ ký, kèm `gh api` để xác minh repository, tag, immutable status, asset SHA-256 và server publish time. Không tin cờ signature do caller gửi.
5. `VerifiedAdmissionCore` ràng buộc cùng private digest, exact source/runtime manifest, asset public-safe, independent acceptance receipt, thứ tự timestamp; recheck release trước khi tiêu thụ quyền một lần.
6. `AntiRollbackConsumptionLedger` bắt buộc gọi **external monotonic witness trước khi ghi SQLite**; nếu không có witness, từ chối. Replay sau khi đổi DB hoặc rollback local DB bị chặn **trong mô hình witness bảo toàn trạng thái**. Lỗi ghi DB sau remote reserve vẫn tiêu thụ quyền, fail closed.
7. `ProductionG3Gateway.launch` cố ý từ chối: `PRODUCTION_G3_GENERATOR_NOT_REGISTERED_OR_AUTHORIZED`. Không chấp nhận callback G3 tùy ý; không đăng ký generator.

**`g2_github_release_witness.py`:** một backend cụ thể có thể dùng GitHub immutable release như một mốc one-shot theo **session-only tag**, kiểm lại release và asset đã ký, từ chối duplicate tag/replay trong vòng đời release. **Chưa gọi backend này trên GitHub thật.** Một admin vẫn có thể xóa release, rồi cùng session được tạo release mới: test `test_11_deleted_release_can_be_recreated_is_known_risk` ghi nhận giới hạn này. Vì vậy không tuyên bố chống rollback tuyệt đối hoặc WORM.

Tài liệu tham khảo cho các lệnh CLI: https://cli.github.com/manual/gh_release_verify và https://cli.github.com/manual/gh_release_verify-asset.

## 3. Source QA

Lệnh chạy (Linux local, Python 3.13.5):

`python -B -W error::ResourceWarning -m unittest -q test_pre_g3_admission_guard.py test_g2_production_boundary.py test_g2_github_release_witness.py`

**79/79 PASS**:

- 35 test source candidate cũ (regression, fixture-only).
- 33 test trust boundary mới: fake HMAC đúng định dạng bị từ chối; mất anchor; ký nhận độc lập thiếu; source pin sai; asset sai; chống replay với ledger khác hoặc bị xóa **với remote witness giả còn nguyên**; concurrency 8 threads.
- 11 test GitHub witness với mock GH CLI/API: duplicate tag, concurrent writer, sai SHA, mutable release, chữ ký lỗi, release mất. Test 11 **chứng minh lỗ hổng deletion/recreation nếu admin xóa release**.

Bốn tệp mới đều parse bằng AST. ZIP đã kiểm tra CRC và exact member bytes với bốn tệp đã chạy local.

**ZIP SHA-256:** `cd3a13a92853b71428f86a6b1df3f54efb54e69de79fadc94c2de714a09fda09`

**Giới hạn QA:** Kết quả là **implementation synthetic QA**, không phải Windows Python 3.12, independent QA, live GitHub signing hoặc G3 production certificate.

## 4. Điều kiện production vẫn HOLD

1. `IndependentAcceptanceVerifier` và `signed_timestamp_checker` là interface chờ trusted implementation. Mã hiện có **không** xác minh signer độc lập hoặc signed timestamp từ một nguồn trust root đã nghiệm thu; synthetic QA dùng fixture giả.
2. Chưa có chứng cứ chạy trên Windows Python 3.12 cùng protected custody, chưa có actual HMAC V2/readback runtime trong private session. **Không tạo key G_pre thật để tiền kiểm**.
3. External witness cụ thể dùng GitHub immutable releases nhưng **không chứng minh chống reset nếu admin xóa release**. Điều này phải được reviewer adjudicate trong retention/invalidation amendment, không tự nâng thành PASS.
4. Chưa có process isolation / Windows ACL chứng minh user không thể bypass guard, không có frozen production G3 generator/call graph đã khóa. `ProductionG3Gateway` tiếp tục mặc định từ chối.
5. `safe_read` kiểm leaf symlink/hash; chưa nghiệm thu tất cả Windows reparse point / hardlink và TOCTOU. Hash pin nguồn kế thừa không tự chứng minh protected runtime custody hiện tại.
6. Chưa có độc lập review cho candidate mới và retention amendment của tác giả trước.

## 5. Điều kiện review một lần, không tạo chuỗi micro-permit

**Single integrated next review:** phân xử exact new candidate, source-only QA, trusted signer/timestamp implementation requirement, GitHub witness policy và deletion/recreation risk, Windows custody readback khi được phép. Nếu không đủ trust root hoặc independent amendment acceptance, giữ HOLD và liệt kê đúng blocker. Không chạy lại G0/QA lịch sử.

`G0=PASS_SCOPED` · `G1=OWNER_STANDING_DIRECTION` · `R7=FROZEN_FAIL` · `R8=NOT_GENERATED` · `G3/G4=NOT_EXECUTED` · `G5/G6=SEALED` · `GPU=NO` · `READER=0` · `PROBE256=SEALED` · `ACTUAL_HMAC_KEY_GENERATED=FALSE` · `ACTUAL_G_PRE_COMMITMENT_CREATED=FALSE` · `GO_R8_D_CANDIDATE_AUTHORING_ONLY=NOT_AUTHORIZED`.

Không merge, không cấp GO khoa học, không tạo release tiêu thụ quyền thật, không truy cập dữ liệu/khóa private.
