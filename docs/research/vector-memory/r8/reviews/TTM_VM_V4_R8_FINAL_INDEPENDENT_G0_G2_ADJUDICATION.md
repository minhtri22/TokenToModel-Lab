# TTM_VM_V4_R8_FINAL_INDEPENDENT_G0_G2_ADJUDICATION

**Ngày:** 2026-11-14 (Asia/Saigon)
**Operation:** `TTM_VM_V4_R8_FINAL_INDEPENDENT_SOURCE_DELTA_AND_G2_SHA_REBIND_SINGLE_GATE`
**Vai trò:** Independent AI Evidence Reviewer (người kiểm toán chứng cứ AI độc lập)
**Nguồn kiểm toán được khóa:** `5334833179895048bb19eab645fe8c06b9ca4fd0`
**Nhánh ghi chứng cứ:** `evidence/ttm-vm-v4-r8-g0-f01-f03-single-closure-20261114`
**Phán quyết duy nhất:** **`HOLD_INTEGRATED`**

## 1. Phạm vi và nguồn chứng cứ

Reviewer mới đọc lại mã Python từ các Git object của commit khóa `5334833...`, so sánh với báo cáo độc lập trước `62542b6...`, bản sửa `98fec84...` và báo cáo triển khai `8e8574...`. Commit `5334833...` là tổ tiên của HEAD nhánh chứng cứ `8e8574...`; diff của thư mục `integrated_closure/` giữa hai commit trống. Không sử dụng `main` làm source pin.

- [Thiết kế V4 đóng băng (`b8410d9...`)](https://github.com/minhtri22/TokenToModel-Lab/blob/b8410d9c1f77a733036e980b567de73c316f8725/docs/research/vector-memory/r8/TTM_VM_V4_R8_V4_GOLD_FOLD_ORACLE_RATER_OWNER_SCOPE_SINGLE_PACKET_DESIGN_ONLY_20261114.md)
- [Kiểm toán độc lập trước (`62542b6...`)](https://github.com/minhtri22/TokenToModel-Lab/blob/62542b6db216a021f84aa8495f40794fb82097d4/docs/research/vector-memory/r8/reviews/G0_G2_FINAL_INDEPENDENT_READBACK_AND_ADJUDICATION.md)
- [Remediation source (`98fec84...`)](https://github.com/minhtri22/TokenToModel-Lab/commit/98fec8442f38819731405c3f938ffbdf42cee311)
- [Source pin sau sửa workflow (`5334833...`)](https://github.com/minhtri22/TokenToModel-Lab/commit/5334833179895048bb19eab645fe8c06b9ca4fd0)
- [Báo cáo agent triển khai (`8e8574...`)](https://github.com/minhtri22/TokenToModel-Lab/blob/8e857415c2ac0c1c09afdaf361f6eed1f727a0ab/docs/research/vector-memory/r8/reviews/TTM_VM_V4_R8_THREE_G0_FINDINGS_INTEGRATED_SOURCE_REMEDIATION_TARGETED_QA_AND_REVIEW_STATUS_20261114.md)

SHA-256 tính lại độc lập bằng `Get-FileHash -Algorithm SHA256` trên byte của checkout GitHub từ nhánh chứng cứ đã fetch. Các giá trị trùng danh sách CI tại source pin, đồng thời `integrated_closure/` không đổi giữa source pin và evidence HEAD.

| Tệp trong `integrated_closure/` | SHA-256 độc lập |
| --- | --- |
| `gold_contract.py` | `8e8b81ce2d0bc47cc60c29abc7156fe9d97613e67983e43b7f587615d68015a5` |
| `folds_raters.py` | `fa48364561fd19a2caa2095ce3ac4cb5f711817b8dac2db1b929fd193196dc91` |
| `test_g0_final_three_findings.py` | `e66ca4694625d597528e6b6f018e3be71ffbd0b1ab3439e27b95a442368c7bc9` |
| `restricted_oracles.py` | `34ab74d36b822703e4d8cbdf281e142273d55d181243d904b55fd31a0e6382a1` |

Đây là **GitHub/local checkout byte readback**. Chưa có biên nhận băm hai tệp sửa đổi tại môi trường private được bảo vệ.

## 2. G0 — Independent source-delta review

### G0-F01 — `PASS_SCOPED_SOURCE_REVIEW`

`gold_contract.py` dòng 20–57 lấy `pending` từ các **verified claim objects đã chọn** trong tổ hợp CORE. Các claim `verified=False` không tham gia `grouped` hay `verified_by_card` (dòng 114–118). `resolve()` liệt kê phương án theo từng CORE predicate (dòng 137–149) và loại mọi tập có tập con đủ chứng cứ. `_validate_claim_dependencies()` vẫn kiểm tra dependency thiếu/cyclic trước khi chọn (dòng 59–109). Target chỉ được SELECT nếu đúng một hypothesis và đúng một target key (dòng 150–167).

Đối chiếu phản ví dụ lịch sử: S chứa sáu CORE verified; U không cần thiết; claim khác trên S có `verified=False, depends_on=["U"]`. Resolver mới lấy root dependency từ sáu claim được chọn, cho proof tối thiểu `["S"]`. Nếu chính CORE verified cần U, dependency U vẫn được thêm; nếu U có verified chain đến V thì closure duyệt tiếp. Những kết luận này được xác nhận bằng đường mã và đối chiếu các fixture triển khai, **không nhận QA của agent sửa mã là độc lập**. Không phát hiện blocker mới cho phạm vi ba lỗi G0 được giao trong F01.

[Nguồn F01 tại source pin](https://github.com/minhtri22/TokenToModel-Lab/blob/5334833179895048bb19eab645fe8c06b9ca4fd0/docs/research/vector-memory/r8/integrated_closure/gold_contract.py)

### G0-F02 — `PASS_SCOPED_SOURCE_REVIEW`

`receipt_f07()` (dòng 185–197) chỉ tạo negative claim khi đồng thời có `negates_accession == target accession`, `link_event == target event`, `authorized is True`. `time_valid` và authority rank sau đó được xử lý ở `resolve()` (dòng 119–135). Receipt sai event hoặc thiếu `link_event` không thể phủ định hypothesis. Receipt cùng accession/event, có thẩm quyền và còn hiệu lực tạo defeater, giữ semantics P-REC-V1.

Trong cặp F07 symbolic gốc, nhánh audit authorized khớp X/E sinh `SELECT`, nhánh audit authorized chỉ khớp Y/E sinh `ABSTAIN`; mã không đổi hành vi đó. Không phát hiện blocker mới cho F02 trong phạm vi reviewer được giao.

[Nguồn F02 và cặp symbolic](https://github.com/minhtri22/TokenToModel-Lab/blob/5334833179895048bb19eab645fe8c06b9ca4fd0/docs/research/vector-memory/r8/integrated_closure/gold_contract.py)

### G0-F03 — `HOLD_SOURCE_CONTRACT_AND_CALLER_INTEGRATION`

**Gateway đã có ở mã nguồn.** `preassign_r8()` gọi `validate_r8_blueprint_manifest()` để từ chối số blueprint khác 32. `postcheck_r8()` gọi `validate_r8_case_manifest()` cho 64 case, hai twins SELECT/ABSTAIN, 32 card/key mỗi case, target hợp lệ, và kiểm tra bốn fold có đủ membership. `postcheck()` giữ phát hiện cross-fold edge và trạng thái `FOLD_LEAK_CV_INVALID`. Các primitive `preassign()` và `postcheck()` vẫn chấp nhận fixture nhỏ, đúng mục đích source-only của chúng.

**Phản ví dụ độc lập mới F03-A, family enum.** Thiết kế V4 đóng băng yêu cầu chính xác `F01…F08`, mỗi family bốn cặp (B03 Stage 1). Reviewer dựng **32 blueprint synthetic QA** với tám family tên `UNREGISTERED_0` đến `UNREGISTERED_7`, mỗi family bốn cặp, IDs hợp lệ và duy nhất. `validate_r8_blueprint_manifest()` **chấp nhận**. Dòng 167–175 chỉ kiểm tra tám tên bất kỳ và mỗi tên có bốn bản ghi; không kiểm tra tập tên định trước. Kết quả `PROBE_FAMILY_ENUM=ACCEPTED_UNREGISTERED_NAMES`. Vì vậy production manifest chưa enforce đúng tám family đã preregister.

**Phản ví dụ độc lập mới F03-B, nguồn locked fold.** Reviewer dựng 32 blueprint/64 case giả lập chỉ để QA, hai action twins mỗi blueprint, 32 unique card keys, text và event signature phân biệt, cùng một dict fold tùy ý `{bp_i: i % 4}` và chuỗi `cv_status="PREFOLD_READY_NOT_VALIDATED"` tự điền, **không gọi `preassign_r8()`**. `postcheck_r8(cases, blueprints, forged_preassignment)` **chấp nhận**, trả `POST_GRAPH_NO_CROSSFOLD_EDGE`, `crossfold_post_edges=0`. Dòng 221–234 kiểm membership, range và status nhưng không kiểm nguồn bản ghi, HMAC allocation hoặc gắn immutable blueprint signature. Phản ví dụ không chứng minh có leakage trong fixture; nó chứng minh một bản phân fold tự tạo có thể đi qua cổng mang tên `locked_preassignment`. Cần binding/custody thực sự trước khi xem đó là phân fold precommitted hợp lệ.

**Production caller.** `git grep` tại đúng `5334833...` không tìm thấy lời gọi `preassign_r8`, `postcheck_r8` hay hai validator bên ngoài chính `folds_raters.py` và `test_g0_final_three_findings.py`. Vì chưa có caller production được khóa, trạng thái là `SOURCE_GATEWAY_IMPLEMENTED` cùng `PRODUCTION_CALLER_INTEGRATION_NOT_VERIFIED`. Không thể cấp readiness PASS từ sự tồn tại của wrapper.

Hai probe trên chạy một lượt độc lập bằng Python 3.12 với fixture non-R8 trong bộ nhớ, không lưu đầu vào, không sinh gold, không ghi private, không dùng HMAC secret. Các bộ test 37/37, 25/25 và 15/15 lịch sử không chạy lại. Kết quả triển khai 15/15 tại [CI 43590325992](https://github.com/minhtri22/TokenToModel-Lab/actions/runs/43590325992) được ghi nhận là `IMPLEMENTATION_AGENT_QA` theo báo cáo hiện có, chưa bao phủ hai witness này.

[Nguồn F03 tại source pin](https://github.com/minhtri22/TokenToModel-Lab/blob/5334833179895048bb19eab645fe8c06b9ca4fd0/docs/research/vector-memory/r8/integrated_closure/folds_raters.py)

**G0 tích hợp:** `HOLD` do F03-A, F03-B và thiếu chứng cứ caller production. F01/F02 chỉ PASS trong phạm vi source review đã mô tả.

## 3. G2 — private custody và source-lock rebind

**Chứng cứ cũ được giữ đúng phạm vi:** báo cáo độc lập `62542b6...` ghi `G2_PRIVATE_PREFLIGHT=PASS` cho sentinel non-R8 54 bytes, hai tiến trình Windows PowerShell 5.1, DACL/ACL đã giới hạn, Python 3.12.10 và môi trường dependency cô lập. Sentinel SHA-256 `0d880e2bed5f88f3578728fcde67b9dde341419244ba7006cf94146667cf1652`. Sandbox và runtime tạm đã bị xóa sau kiểm tra. Đây là `PASS_SCOPED_STORAGE_PREFLIGHT_REPORTED`.

**Source-lock mới:** `G2=HOLD_SOURCE_LOCK_REBIND_NOT_VERIFIED`. Bốn SHA ở mục 1 được đọc từ checkout public trên máy reviewer. Không có chứng cứ phiên này cho thấy custodian có quyền trên private store bền vững đã đọc lại byte `gold_contract.py`/`folds_raters.py` đúng SHA mới trong protected runtime. Biên nhận trước vẫn khóa SHA cũ. Chưa chứng minh identity/account, private-store persistence và quyền truy cập hiện tại, HMAC-key custody/source pin tại G2. Reviewer không giả nhận vai trò custodian hoặc tạo khóa để điền khoảng trống chứng cứ này.

Không lặp lại sentinel chỉ do đổi source. Không đưa tên tài khoản, private path, key hay ACL nhạy cảm vào GitHub. Trạng thái G2 được giới hạn đúng bằng chứng đã đọc.

## 4. G1 — standing research direction

`OWNER_STANDING_RESEARCH_DIRECTION_RECORDED` đã tồn tại tại commit `097e046...`. Phạm vi được ghi nhận gồm `R8-D_EXPLORATORY_DESCRIPTIVE_ONLY`, `FOUR_RATERS_TWO_PER_CASE`, `P-REC-V1_SYNTHETIC_TOY_DOMAIN`, synthetic mới do AI tạo và loại trừ real PII, third-party private hoặc material chưa rõ quyền. Đây là owner declaration được ghi lại, **không phải signed attestation** hay bằng chứng rights/PII của candidate tương lai. Không yêu cầu owner xác nhận GO lại cho phạm vi này.

[Owner standing direction](https://github.com/minhtri22/TokenToModel-Lab/blob/097e046bb0f6525665dde03ec5fcdf8134a8e762/docs/research/vector-memory/r8/decisions/TTM_VM_V4_R8_OWNER_STANDING_RESEARCH_DIRECTION_20261114.md)

## 5. Formal adjudication — `HOLD_INTEGRATED`

Các blocker đang mở có chứng cứ cụ thể là (1) B03 không khóa được exact family enum `F01…F08` dù manifest đủ 32 bản ghi, (2) `postcheck_r8` nhận fold/status tự điền không có xác minh nguồn locked assignment, (3) chưa chứng minh production caller buộc đi qua strict gateways trước CV, và (4) chưa có custodian private SHA-256/source-lock rebind mới trên hai source đã sửa. Không có căn cứ để tuyên `GO_R8_D_CANDIDATE_AUTHORING_ONLY`.

Giữ nguyên `R7=FROZEN_FAIL`, `R8=NOT_GENERATED`, `G3/G4=NOT_EXECUTED`, `G5/G6=SEALED`, `Reader=0`, `GPU=NO`, `PROBE256=SEALED`. Không thực thi khoa học, sinh gold/candidate R8, blind raters, CAL/TEST hay HMAC private; không mở V5/V6. Báo cáo này là **một closure evidence cuối** cho lượt kiểm toán được giao.
