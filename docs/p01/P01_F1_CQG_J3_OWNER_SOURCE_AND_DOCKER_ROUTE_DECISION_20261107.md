# TTM P01 — Chọn F1-CQG-J3 và phân định tuyến E0 (07/11/2026)

**Phạm vi:** tài liệu và kiểm toán kỹ thuật. Không phát hành quyền chạy E0 hay đóng P01.

## 1. Quyền chủ dự án đã cấp

Chủ dự án cho phép sử dụng tự do các văn bản *phù hợp* từ những dự án nghiên cứu do mình sở hữu. Đây là phạm vi đồng ý **dùng nội bộ cho nghiên cứu tokenizer**, không suy ra mọi đoạn trích bên thứ ba đã được cấp phép hoặc corpus được phát hành công khai, và không mặc định quyền thương mại.

## 2. Ứng viên F1 được chọn

- `source_id=F1_CQG_J3_PREREG_OWNER_SCOPE_20261107`
- Đường dẫn chỉ đọc: `D:\WORK\RESEARCH\2.CQG\studies\j3_*`
- Đã kiểm kê **37 thư mục J3**; trong các thư mục đã rà, có tệp tiền đăng ký (`*PREREGISTRATION.md`). Việc có thư mục hoặc tệp không chứng minh đủ 30 nhóm không trùng.
- Chọn đúng một tệp mỗi thư mục, ưu tiên `HYPOTHESES_AND_PREREGISTRATION.md`, nếu không có thì chỉ chọn duy nhất một `*PREREGISTRATION.md`. Nhiều tệp cùng phù hợp mà không có thứ tự rõ ⇒ HOLD, không tùy chọn theo số liệu thực nghiệm.
- Loại bỏ log, kết quả TEST, mã nguồn, chứng cứ khoa học, binary, `lineage.md`, thư viện bên thứ ba và dữ liệu cá nhân. Không đọc các dự án không nằm trong phạm vi định trước.
- **Chưa** có số nhóm đã chống trùng, SHA snapshot, PII/Copyright per-file; `F1_ADMISSION=HOLD`.

## 3. Một lượt kiểm kê nội dung chỉ đọc

Script cung cấp riêng qua cuộc trò chuyện:

- `TTM_P01_F1_CQG_J3_READONLY_CENSUS_PS51_V1.ps1`, SHA-256 `6b38206445f633132953449b5f9605bdba48c3d577727bae048500a51307d12e`.
- Embedded Python `TTM_P01_F1_CQG_J3_READONLY_CENSUS_V1.py`, SHA-256 `928c065a3daf42d3d2d5b2d0367bdcae4426337ad369ec959be8c5891af86efb`.
- Chỉ đọc tệp CQG/J3; áp dụng `canonical_key` và `near_duplicate` từ đúng mã TTM đã pin; lập thành phần liên thông, thống kê số nhóm, băm SHA-256 từng tệp và băm danh sách nguồn. Bộ đếm không gọi `classify_f0_documents` vì F0 source guard cấm corpus thật. Không tạo split, không xem TEST, không học BPE.
- Kiểm tra tự động một số dấu hiệu PII/secrets không thay thế việc duyệt PII của người chịu trách nhiệm. Mã băm danh sách nguồn **không phải** SHA của snapshot corpus đã vật chất hóa.
- Đọc nguồn từ CQG; mọi tệp tạm và bằng chứng chỉ ở `D:\WORK\RESEARCH\TokenToModel-Lab`. Không đẩy nội dung các tài liệu sang GitHub.
- QA tĩnh Python AST/Base64/scope: PASS ngoài máy. Parser PowerShell 5.1/native content census: **chưa thực hiện**.

## 4. Quyết định tuyến E0: Docker Linux CPU-only

Chọn **ứng viên tuyến E0** `LINUX_DOCKER_CPU_ONLY_PROJECT_SCOPED` để không phụ thuộc kết quả S1 Windows/SCM trước đó. **Chưa tuyên bố K4 PASS.** Trước E0 phải xác nhận Docker thực sự sẵn sàng, CPU-only, không mạng, nguồn chỉ đọc, ghi chỉ vào workspace TTM, không gắn tập TEST vào máy học, cưỡng chế RAM/CPU/PID/wall/disk, kiểm tra âm tính fail-closed.

Phát hiện từ HEAD TTM đã pin: `source_scope_guard.py` từ chối F1; `learn_merges_f0_qa0_only` chỉ cho phép F0; `runtime/p01/windows_job_guard.py:start_worker` chưa được thiết lập. Vì vậy **bắt buộc** tạo bộ tiếp nhận F1 thực có khóa SHA và tuyến BPE TRAIN-only đúng hợp đồng; không patch/mock guard F0 để chạy thật.

Nếu Docker không khả dụng hoặc QA bảo vệ không đạt, `K4=HOLD`. Không tự chuyển sang Python Windows không giới hạn.

## 5. Đường hoàn tất P01 hữu hạn

1. Một lượt kiểm kê F1, chốt SHA/nhóm và rà soát ngoại lệ PII/quyền. Chỉ khi đủ 30 nhóm thực, mới xét `SOURCE_ADMISSION=ALLOW` và khóa TRAIN/VALIDATION/TEST.
2. Một gói triển khai + QA tích hợp F1 adapter và Docker E0 guard. Không lập permit nhỏ cho từng lệnh băm.
3. Một E0 TRAIN-only BPE (hai tiến trình sạch/đúng SHA), checker độc lập và quyết định P01. Chỉ sau đó xét mở P02.

**Trạng thái:** `K1=PASS_SCOPED_WINDOWS`, `K2=PASS_SCOPED_FIXTURE`, `K3=HOLD`, `K4=HOLD_ROUTE_QA`, `E0=NOT_EXECUTED`, `P01=OPEN`, `P02=NOT_OPENED`. Giữ nguyên P00, 10 F0 PASS, S1 FAIL/markers, `lineage.md`, PR/HEAD gốc và P00–P12.
