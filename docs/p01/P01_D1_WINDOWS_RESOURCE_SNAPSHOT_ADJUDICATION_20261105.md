# P01 D1 — Thẩm định kết quả tiền kiểm tài nguyên Windows

**Mã công việc:** `TTM_P01_D1_WINDOWS_RESOURCE_READONLY_RESULT_ADJUDICATION`  
**Nguồn:** console PowerShell 5.1 do người dùng cung cấp; đọc lại và đối chiếu với chương trình đã ghim trong phiên ChatGPT.  
**Thời điểm đo theo console:** `2026-11-05T11:01:18.0864528Z` (18:01:18 ngày 05/11/2026, giờ Việt Nam).  
**Máy:** `DESKTOP-4PSD0G2`. **Workspace:** `D:\WORK\RESEARCH\TokenToModel-Lab`.  
**Trạng thái:** `H05_RESOURCE_SNAPSHOT_PASS_CANDIDATE_THRESHOLDS`; `H05_RUNTIME_GUARD_QA=HOLD`.

## 1. Nguồn gốc và giới hạn chứng cứ

- Tệp biên bản GitHub: `artifacts/qa/p01/TTM_P01_D1_RESOURCE_READONLY_USER_CONSOLE_20261105T110118Z.txt`, nhãn `USER_SUPPLIED_CHAT_CONSOLE_TRANSCRIPTION`. Đây là bản chép của console, **không phải biên bản có chữ ký/mã băm do Windows tự sinh**.
- Chương trình PowerShell đã chuẩn bị: `TTM_P01_D1_RESOURCE_READONLY_PREFLIGHT.ps1`, SHA-256 `e48e6a101e640a483f727786e50032f04e1b39bdbc6c6b97b75d9c437c606606`. Đã đối chiếu tệp chương trình tại môi trường chuẩn bị với SHA-256 đã ghim và kiểm tra rằng các thao tác chính là đọc Git và `Get-CimInstance`.
- Console ghi `WRITES_BY_THIS_SCRIPT=NONE`, `CLEANUP=NONE`, `P01_TRAINING=NOT_PERFORMED`. Các dòng này là tuyên bố của chương trình, không phải chứng thư giám sát toàn hệ điều hành.
- Kiểm tra `WORKTREES_WITHIN_ROOT=2` xác minh vị trí cây làm việc theo chương trình; **chưa chứng minh SHA HEAD của từng worktree ở thời điểm này**.
- Bản chép không cho phép kiểm chứng độc lập trực tiếp số đo RAM/đĩa theo thời gian thực; RAM và ổ D: thay đổi theo ứng dụng khác.

## 2. Bảng đo và ý nghĩa

| Đại lượng | Giá trị console | Ngưỡng ứng viên | Chênh lệch so với ngưỡng | Đánh giá |
|---|---:|---:|---:|---|
| Tổng RAM nhìn thấy (Visible RAM) | 31,587 GiB | Không có ngưỡng | Không áp dụng | Số tham khảo, không thay cho RAM khả dụng |
| RAM khả dụng (Available RAM) | **10,959 GiB** | **≥8 GiB** | **+2,959 GiB** | `CANDIDATE_PASS` |
| Tổng dung lượng ổ D: | 500,863 GiB | Không có ngưỡng | Không áp dụng | Dung lượng logic, không phải dung lượng trống |
| D: khả dụng (Free Disk) | **34,869 GiB** | **≥16 GiB** | **+18,869 GiB** | `CANDIDATE_PASS` |
| D: sau dự phòng nguồn + tạm | **32,807 GiB** | **≥12 GiB** | **+20,807 GiB** | `CANDIDATE_PASS` |
| Dung lượng dự phòng tính theo chương trình | 2,0625 GiB (64 MiB + 2 GiB) | Dự phòng kế hoạch | Không áp dụng | Là phép trừ ước tính, **chưa** cấp phát hoặc đo sử dụng thật |
| Số worktree trong phạm vi | 2 | Không có worktree ngoài root | Theo console đạt | Không khẳng định P00 SHA được re-pin |
| Cơ chế chặn RAM/thời gian trong khi chạy (Runtime Guard) | `NOT_PERFORMED` | Phải có kiểm thử âm tính đạt | Không áp dụng | `HOLD` |

**Giải thích:** RAM khả dụng lớn hơn ngưỡng không chứng minh quá trình BPE luôn dùng dưới 4 GiB RAM. Dung lượng D: đủ ở thời điểm đo không chứng minh gói dữ liệu/corpus đã hợp pháp hay có thể tải. Ở các lần thực thi trong tương lai, phải đo lại tài nguyên ngay trước khi chạy và kiểm tra giới hạn liên tục trong quá trình chạy.

## 3. Quyết định H05

- `H05_WINDOWS_RAM_CANDIDATE_THRESHOLD=PASS_USER_CONSOLE_SNAPSHOT`
- `H05_WINDOWS_DISK_CANDIDATE_THRESHOLD=PASS_USER_CONSOLE_SNAPSHOT`
- `H05_RUNTIME_RESOURCE_GUARD=NOT_IMPLEMENTED_OR_NOT_VERIFIED`
- `H05_DYNAMIC_NEGATIVE_QA=NOT_PERFORMED`
- `H05_EXECUTION_PERMIT=NOT_GRANTED`

H05 **được đóng ở tiểu cổng đo tài nguyên (Resource Snapshot), chưa đóng tiểu cổng an toàn thực thi**.

## 4. Phạm vi nguồn dữ liệu tại thời điểm quyết định

- Không có bản kê nguồn F1/F2 với `admission_decision=ALLOW`, giấy phép và SHA-256 được thẩm định trong hồ sơ P01.
- Quyết định thận trọng phù hợp phạm vi hiện có: `P01_SOURCE_SCOPE=F0_ONLY_DESIGN_AND_ORACLE_REVIEW`, **không** nhận corpus thật, không huấn luyện BPE.
- Các mẫu F0 giả lập dùng cho mô tả và kiểm tra oracle tĩnh, không được xem là corpus TRAIN, VALIDATION hoặc TEST khoa học.
- Muốn mở nghiên cứu BPE trên corpus thật phải có đề xuất nguồn F1/F2 cụ thể và quyết định chấp thuận quyền dữ liệu **riêng**.

## 5. Giới hạn thẩm định bộ kiểm tra độc lập H04

- 12 byte fixture có mã SHA-256 trong đặc tả là **oracle**, không phải chứng nhận đã chạy bộ kiểm tra riêng.
- Trước khi triển khai checker phải khóa các trường hợp lỗi, tính độc lập với mã tokenizer, luật kiểm tra BPE và nội dung byte kỳ vọng. Bộ kiểm tra chỉ được hiện thực sau cổng I0 riêng; không viết mã trong bước D1 này.
- Nếu H04 hoặc H02 chưa đủ bằng chứng, **không được** cấp khóa tiền đăng ký D1 dù hai ngưỡng tài nguyên đạt.

## 6. Kết luận cuối

`TTM_P01_D1_RESOURCE_SNAPSHOT_ADJUDICATION=PASS_SCOPED_USER_CONSOLE`  
`TTM_P01_D1_SOURCE_SCOPE=F0_ONLY_DESIGN`  
`TTM_P01_D1_SOURCE_RIGHTS=HOLD_NO_APPROVED_CORPUS`  
`TTM_P01_D1_CHECKER_DYNAMIC_QA=HOLD`  
`TTM_P01_D1_RESOURCE_GUARD=HOLD`  
`TTM_P01_D1_SCIENTIFIC_PREREG_LOCK=NOT_GRANTED`  
`P01_IMPLEMENTATION_AUTHORIZED=false`  
`P01_DATA_DOWNLOAD_AUTHORIZED=false`  
`P01_WORKTREE_CREATION_AUTHORIZED=false`  
`P01_TOKENIZER_TRAINING_AUTHORIZED=false`  
`P00_CLEANUP_AUTHORIZED=false`

**Bước tiếp theo:** rà soát độc lập hợp đồng checker F0 (chỉ tài liệu), chuẩn bị một nguồn F1 cụ thể kèm quyền sử dụng nếu muốn nghiên cứu corpus, và chuẩn bị quyết định thiết kế cơ chế giới hạn tài nguyên ở một cổng riêng.
