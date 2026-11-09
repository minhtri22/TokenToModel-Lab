# HANDOFF — TTM × SIX G1 v1e: hai lỗi Win32, phản biện độc lập và một quyết định owner

**Nhiệm vụ:** `TTM_SIX_G1_V1E_INTEGRATED_GATE_PRODUCTION_REVIEW_AND_MINIMAL_OWNER_DECISION`  
**Ngày hồ sơ:** 10/11/2026  
**Tình trạng tại lúc giao:** `V1E_SOURCE=COMMITTED` · `AUTHOR_CPU_QA=PASS_61/61` (lịch sử) · `WINDOWS_V1E_QA=PENDING_OWNER` · `DISTINCT_REVIEW=PENDING` · `G1_SCIENCE_LOCK=HOLD`.

## A. Giới hạn công việc và mốc chính xác

- Repository: https://github.com/minhtri22/TokenToModel-Lab
- **Mã v1e phải review ở commit bất biến:** `1efca4ca080572dcd22bbe658701b221ca46f7dd` trên `implementation/ttm-six-g1-production-gates-methods-v1e-20261110`. Luôn checkout/fetch theo SHA bất biến, không đọc HEAD di động để làm mốc nguồn.
- `main`: `b57b44e7287f842e81050c1faee337f636333dd0`.
- Nghiên cứu v1c đã khóa: `d5d0c5346a595557a76349f900d09be50bce289c`.
- Codex review Windows trước đó: `efbbc1fddfd61e775d30a0481622312f8fb93c51`, overall `HOLD`.
- Nghiên cứu G1 / TEST thật / Qwen / Colab / TTM-Small-4M không nằm trong phạm vi chạy này. Không cấp owner science permit, không thay đổi `main`, PR #12, `lineage.md`, manifest, checkpoint hoặc consumed Qwen technical one-shots.
- Mọi tệp tạm, worktree và thao tác dọn dẹp phải ở bên trong `D:\WORK\RESEARCH\TokenToModel-Lab`. Không xóa tự động tệp bằng chứng.

## B. Tệp nguồn cần đối chiếu SHA / Git blob

| Tệp ở commit v1e | Git blob SHA-1 | SHA-256 của byte trong ZIP |
|---|---|---|
| `scripts/research/six_ttm/g1_signed_boundary_contract_v1e_candidate.py` | `e91fe583db1aa5b112aecd5b8d2830a5da17dd3e` | `19714d8ff8dea1ffe0842018e04fc977d96f746d5732a890656c0d04b4d7c411` |
| `scripts/research/six_ttm/test_g1_signed_boundary_v1e_negative.py` | `eb29fc00d1ac43db867492c2be07ff29bab003ff` | `02795fd784024cb08d0743fd8d404f8448026605fae2533d8627b31b756418bf` |
| `scripts/research/six_ttm/g1_win32_job_failure_path_v1e_candidate.py` | `ec5f3b5d633b8b0feb5ae98c2d8c8c9f45896eb7` | `eb5d1b71a991eb4ca46d801057806e2a580c6bcd2487080bfe3e2c15a6008309` |
| `scripts/research/six_ttm/test_g1_win32_job_failure_path_v1e_static.py` | `961c738534ad0675af69b4ada0d7d781abe074b8` | `111d34ef7f0e4eb4b608ca97760ae05442434e33368676072a40f057c214d2b3` |
| `scripts/research/six_ttm/Run-G1-Win32FailureModes-PS51-V1E.ps1` | `348205f54acd0134e233d0f79563f099a121bc1d` | `3cc1ee9f9991a17b6c890853f1f0c5d0f8f132400b5ca2a41adc40f89355ebd6` |
| `docs/research/six-ttm/G1_METHODS_V1E_PRETEST_FROZEN_AMENDMENT_CANDIDATE_20261110.md` | `d2737a9c2fb31d8398119622fe1ff78c295c8fa8` | `2748adbb6a5bd18da4866846ea21e761dc8cfef318eb422e08c832174836db2f` |
| `docs/research/six-ttm/G1_V1E_INTEGRATED_PRODUCTION_GATE_STATUS_AND_CODEX_HANDOFF_20261110.md` | `24cf0a66994ebb2b9364c2b7974ebde57b0430e8` | `749a10312938872f5643dfcd65ed9dabdb62fa433c14946189a9b19cbec74b87` |
| `docs/research/six-ttm/G1_V1E_AUTHOR_CPU_QA_RECEIPT_20261110.json` | `1fd2be1c3bb39a784f7cda4d0f988b7619b136d5` | `24a71820bccff9fa42ffe3e5846877470e4d62fa0a99489af8a55db96d366c89` |

**ZIP gốc** `TTM_SIX_G1_V1E_INTEGRATED_PRODUCTION_GATES_AND_METHODS_20261110.zip`, SHA-256 `fad5992bac357367c67ee7448209e02247f9566fe6c01a09d69efae2a2b1d55f`. Tám Git blob và hash trong ZIP đã được bên triển khai đối chiếu; reviewer vẫn phải xác minh độc lập.

**Wrapper chỉ để owner chạy:** `Run-TTM-G1-V1E-Two-Win32-FailureModes-VerifiedStage-PS51-20261110.ps1`, SHA-256 `9dbfa1eab3242f3d4bb5ef4254eea9b072007b0c5ca4ab628a13b358f8b4a1bc`. Wrapper này **không** thuộc tám tệp v1e đã khóa. Nó chỉ kiểm tra ZIP/hashes, tạo thư mục mới ở `_tmp`, và gọi nguyên xi runner v1e. Kiểm tra source wrapper độc lập trước khi chấp nhận receipt.

## C. Đúng hai ca Windows cần thực hiện trước phản biện

Máy Windows: `DESKTOP-4PSD0G2`, PowerShell 5.1, Python 3.12 được pin dưới user profile. Chỉ dùng fixed Python child `import time;time.sleep(8)` do test harness sở hữu; không truyền executable/argv tùy ý.

1. `harmless-assign-fault-qa`: fault sau `CreateProcessW(CREATE_SUSPENDED)`, **trước** `AssignProcessToJobObject`. Yêu cầu `TerminateProcess` trên handle đã sở hữu, `WaitForSingleObject` xác nhận child exited; không có orphan.
2. `harmless-resume-fault-qa`: fault sau `AssignProcessToJobObject`, **trước** `ResumeThread`. Yêu cầu cleanup tương tự, Job Object đóng đúng; không có orphan.

Runner nguyên gốc nhận source ở `_tmp`, kiểm SHA-256 source, dùng Python 3.12, tạo thư mục `_tmp\G1_WIN32_FAILURE_MODES_<timestamp>_<id>`, xuất `G1_WIN32_V1E_PRIVATE_RECEIPT.json`, `SHA256_RECEIPT.txt` và 4 log (stdout/stderr cho mỗi ca). Trong mỗi stdout cần `test=HARMLESS_FAULT_INJECTION`, `cleanup_verified=true`, `child_exited=true`, `production_qualified=false`, `real_gpu_used=false`, `science_executed=false`.

**Tình trạng chưa xác minh:** RemoteMCP `machine-1` thấy online nhưng `task_job_submit` của ngay cả PowerShell preflight chỉ đọc bị từ chối: `scientific job admission held until exact command evidence qualifies`. Không dùng các đường vòng để né admission; chưa có receipt thực tế của **hai ca mới**. Owner cần chạy wrapper cục bộ một lần; reviewer không được suy diễn PASS từ file bản thiết kế hay 45 ca cũ.

**Vị trí receipt:** lấy **chính xác** đường dẫn in bởi `G1_WIN32_V1E_QA_DIR=...`, không đoán tên thư mục. Review raw receipt và log ở local; tránh public SID/đường dẫn nhạy cảm. Xác minh hash raw bytes độc lập, exit code, PID/process liveness nếu có; đừng tuyên bố process-tree absence nếu log chỉ xác nhận handle child. Nếu lỗi, giữ nguyên receipt và báo STOP/FAIL với lệnh đã thực thi; không chạy lại một cách tự động.

## D. Các bằng chứng v1e được xem xét nhưng không cần chạy lại

- `AUTHOR_CPU_QA=PASS_61/61` gồm 53 ca signed boundary/ledger candidate và 8 ca Win32 static; đây là QA tác giả, không phải PASS production.
- `WINDOWS_PREVIOUS_SYNTHETIC_QA=PASS_45/45`, `WIN32_HARMLESS_CHILD_KILL=PASS` thuộc gói trước, đã kiểm độc lập bằng log/hash tại `efbbc1...`; **không chạy lại**.
- Hai lỗi CRITICAL lịch sử của v1b (freeze DEV và CKA false-significance) được Codex xác minh đã sửa trong v1c; **không mở lại** nếu không có phản ví dụ mới.
- Owner-controlled Ed25519 signer/writer/witness keys thực, principal worker riêng, ACL/DACL deny TEST, trusted writer và witness external chưa có bằng chứng provision. Bằng chứng synthetic key **không** thay thế nguồn tin cậy production.

## E. Sáu gate: một ma trận PASS/FAIL/NOT_TESTED

1. **Owner Authority / Trusted launcher:** kiểm chữ ký theo exact code/head/amendment/run/data rights/expiry; không accept permit tự phát từ worker, no production signing key assumed.
2. **Split broker / Windows worker SID:** yêu cầu principal riêng và negative `AccessDenied` thật đối với TEST giả qua path/hardlink/junction *trước* freeze; current-user sentinel không chứng minh cách ly.
3. **Pack writer / atomic ledger:** writer được định danh riêng, receipt xác thực exact bytes đã parse, crash consistency và concurrency; chỉ ghi hai tệp trong cùng directory không có nghĩa là atomic transaction.
4. **External monotonic witness:** chứng cứ nằm ngoài cùng miền rollback controller/worker, xác thực monotonic sequence/ACK, thử rollback đồng thời và replay xuyên workspace deletion. Hai file SQLite/text ở cùng owner chỉ là simulation.
5. **GPU/OS watchdog:** hai ca lỗi Win32 này chỉ đóng **nhánh cleanup của một tiến trình con vô hại**; phải phân biệt với group/process tree/3.600s per model + 7.200s cumulative + peak VRAM T4 thực tế; không thực thi Qwen/GPU trong review này.
6. **Scientific methods v1e:** xem `G1_METHODS_V1E_PRETEST_FROZEN_AMENDMENT_CANDIDATE_20261110.md`, đánh giá v1a first-occurrence/dedup; near-duplicate/group-dependence; null exchangeability, 1.000 permutation, 2.000 paired bootstrap fixed full TEST SST; CKA 64 eps tie (type-I/power); TEST=64 feasibility/INCONCLUSIVE và B-direct comparison. Quyết định amendment phải có trước TEST.

**Một quyết định chủ sở hữu tối thiểu:** reviewer ghi chính xác các dữ kiện cần owner cấp cho việc **provision kỹ thuật** (SID/service identities, ACL scope, trusted store/witness location, signer public anchor, runner host và limits). Không tự tạo key, tài khoản hoặc điều chỉnh DACL khi chưa phê duyệt. `APPROVE_TECHNICAL_PROVISIONING` (nếu chủ sở hữu sau đó cho phép) **không** tương đương `AUTHORIZE_G1_SCIENCE`.

## F. Khuôn kết luận bắt buộc của Codex

Một báo cáo `.md` và receipt `.json` gồm: origin/HEAD/Git blob; SHA256 của ZIP, raw receipt và log; hai ca Win32 `PASS/FAIL/NOT_TESTED`; phân biệt sửa mã với runtime production; bảng sáu gate `PASS/FAIL/NOT_TESTED` cùng chứng cứ; phán quyết phương pháp v1e; danh mục blocker tích hợp nhỏ nhất; nguyên trạng các cổng khoa học.

**Phán quyết tổng thể duy nhất:** `PASS_DISTINCT_REVIEWER` hoặc `HOLD` hoặc `FAIL`. Giữ `G1_SCIENCE_LOCK=HOLD`, ngay cả nếu reviewer đạt PASS, cho đến owner admission science riêng. Được tạo branch review riêng để lưu kết luận khử thông tin nhạy cảm; không merge vào nhánh đã khóa hoặc `main`.

**Bước thực hiện tiếp theo:** `TTM_SIX_G1_V1E_OWNER_WINDOWS_TWO_FAULT_RECEIPT_THEN_DISTINCT_ADJUDICATION` — owner chạy hai ca Windows một lần; Codex đọc receipt và phân xử độc lập một gói. Nếu phản biện còn HOLD, xác định **một lô provision kỹ thuật** thực sự cần owner phê duyệt, không chia thành các micro-permit.
