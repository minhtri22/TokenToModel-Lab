# TTM P01 F1 Snapshot V1 — pre-marker failure và kỹ thuật khôi phục V2

Ngày 07/11/2026. Phạm vi `F1-VI-GENERAL-01`, **không dùng CQG-J3**.

## Kết luận về lỗi thực tế

Người dùng chạy script V1 với SHA-256 `50EE540EEC7A946792FC1C291FEB4ADB21A8F2FFC7A88B68E2A8C20F38CA2B75` và nhận `TTM_P01_SOURCE_SNAPSHOT=FAIL_OR_HOLD: GIT_READ_FAILED:` tại dòng hàm `ReadGit`. Mã V1 định nghĩa `function ReadGit([string[]]$Args)` và gọi `& $GitExe -C $Repo @Args`. Trong PowerShell, `$args` là biến tự động; tên hàm dùng đã làm mất truyền đối số, nên tên Git command rỗng.

Bằng chứng đọc lại từ máy Windows: không có marker/receipt V1 ở `evidence/p01`; thư mục `datasets` chưa tồn tại; thư mục tạm F1 chưa tồn tại. Lỗi xảy ra ở bước **read-only Git preflight trước CreateNew marker, tạo quarantine và truy cập mạng**. Kết luận `PREFLIGHT_FAIL_BEFORE_ONE_SHOT`, không coi là lượt source acquisition đã chạy.

## Sửa tối thiểu V2

- Hàm sửa: `ReadGit([Parameter(Mandatory=$true)][string[]]$GitArgs)`; tất cả sáu lần gọi được truyền tham số tên `-GitArgs`. Không sửa mô-đun Python tải dữ liệu và không sửa danh sách 100 URL.
- Script V2: `TTM_P01_F1_VI_GENERAL_01_SOURCE_SNAPSHOT_ARGV_RECOVERY_V2_PS51.ps1`; SHA-256: `B453A1228ADBE90B9E3EAAB79D6C640E57B60F21437BBD6473C0A436A3A8205A`.
- Embedded Python SHA-256 giữ `9da5b25f2b8b45a62f1f88d7e6142e4cfa9d9b3b69caa513f16361c0b35bdb5b`. Candidate list SHA-256 giữ `d4f3210c229f2c1d9808bd615ec8b605a86f3312880b7e422b80f1c3f7e732bd`. Đã giải mã, đối chiếu **đúng byte** với hai tệp V1 trên môi trường tác giả; Python AST PASS. **Chưa thực thi parser PowerShell 5.1 hay script V2 trên Windows**.
- V2 tạo marker riêng `TTM_P01_F1_VI_GENERAL_01_SOURCE_SNAPSHOT_ARGV_RECOVERY_V2_20261107.once` và thư mục temp riêng; giữ nguyên đường dẫn receipt snapshot V1 vì trước đó không có receipt. Nếu marker/receipt/fail V1 hoặc V2 đã xuất hiện, script fail-closed không ghi đè.
- Không chạy lại F0/K1/K2 hoặc S1; không khởi động E0; dữ liệu vẫn ở `HOLD_RIGHTS_PII` kể cả khi quá trình thu thập hoàn thành.

## Bước tiếp theo

Chạy kiểm tra SHA script và parser PS5.1 trong PowerShell Windows; chỉ khi hai cổng này PASS mới chạy V2 một lượt. Đọc lại receipt, phân loại quyền/PII, kiểm số nhóm H03. Nếu đủ từ 30 nhóm được chấp thuận và tuyến Docker đạt QA an toàn thì mở đúng một lượt E0 TRAIN-only theo khóa khoa học đã duyệt; nếu chưa đủ thì giữ HOLD.

`F1_SNAPSHOT=NOT_EXECUTED` · `E0=NOT_EXECUTED` · `P01=OPEN` · `P02=NOT_OPENED` · `lineage.md=UNCHANGED`.
