# TTM-Small-4M × EmbeddingGemma 2 — Kiểm toán gần trùng VALIDATION-only 320 × 256 và quyết định CPU one-shot

**Ngày:** 09/11/2026. **Bước:** `TTM_SMALL4M_EMBEDDINGGEMMA2_VALIDATION_ONLY_NEAR_DUPLICATE_AUDIT_AND_FINAL_GO_DECISION`.

## 1. Phạm vi do chủ dự án xác định và sửa đổi tiền đăng ký trước khi chấm

Chủ dự án xác định đây là **lần đầu thực hiện so sánh 320 truyện mới với 256 truyện VALIDATION đã dùng trong nghiên cứu TTM**. Bộ kiểm toán được giới hạn ở **320 × 256 = 81.920** cặp và ngưỡng gốc **Jaccard 5-gram theo từ ≥ 0,85**. Giữ nguyên SHA manifest mới và mọi 320 định danh; **không mở lại nội dung 64 truyện TEST lịch sử**; không dùng GPU, không huấn luyện hoặc chấm mô hình.

**Đính chính lịch sử:** `lineage.md` mốc **L0012** chứng minh 64 truyện TEST cũ đã được sử dụng một lần vào **08/11/2026** để đánh giá TTM bước 1.024 so với bigram. Không được gọi nhóm TEST này là “chưa từng được chấm”. Lượt này không dùng TEST để chọn checkpoint A/B/C/D trực tiếp, nhưng đây vẫn là rủi ro phụ thuộc lịch sử nghiên cứu cần minh bạch.

Vì vậy, hợp đồng phương pháp **chỉ áp dụng để xác nhận dự đoán của bốn checkpoint A/B/C/D cố định trên một tập truyện mới trong cùng miền TinyStories**, chứ không chứng minh độc lập tuyệt đối với TEST lịch sử, không chứng minh donor chưa từng thấy TinyStories và không phải lặp huấn luyện độc lập. Đây là **sửa đổi phạm vi có công bố, trước khi chạy**, không phải tuyên bố đã kiểm đủ gần trùng TEST.

## 2. Chuỗi nguồn và các cổng đã sẵn sàng

- Manifest private 320 truyện: SHA-256 `bedc3671256a66f605fbeb9f98bbd27149b456019d3d8bc5bbc89ebca6d09b47`; đã readback độc lập 320 truyện, 75.798 nhãn.
- T1 split manifest: `9f2ebaca821bddf0a9d7ae30ccfcef34561b968b21159aa913794298235a2fa9`. Chỉ đọc khóa `VAL` cho 256 định danh dùng so sánh; không truy cập `TEST` để lấy nội dung.
- BPE 2.048 TRAIN-only: `cba18e60cee3d08a353ee6d4a451017289e45af7b4b1179c87171b9b78d7dfdc`.
- Raw `TinyStories-valid.txt`: `94e431816c4cce81ff71e4408ff8d3bda9a42e8d2663986697c3954288cb38b4`. Tệp raw chứa cả truyện thuộc nhóm lịch sử TEST, vì thế việc phát hiện ranh giới phải đọc tuần tự các byte nguồn; **chỉ giải mã/lưu vào bộ nhớ văn bản khớp 320 ID mới hoặc 256 VAL**, không giải mã, in, hoặc chấm truyện TEST cũ. Không giả nhận không đọc byte nguồn có chứa TEST.
- Các nguồn mã T1/T4 được ghim Git blob, mã checkpoint vẫn đóng băng.

## 3. Kiểm thử đạt được trong bước này

Đã tạo bộ chạy Python chuẩn thư viện `ttm_gemma2_validation_only_near_audit_final_gate_20261109.py`, SHA-256 **`80361cdfa16dd6c37ced6809adbbbd2ea778f9ef9ba7ebc578a7a9d9f7ed1f85`**, và kiểm thử:
- `--mode fixture-qa`: **24/24 PASS**. Có cả trường hợp cùng nội dung gần giống nhưng khác SHA, một cặp gần trùng xuất hiện trong đúng 81.920 cặp và các biên độ dài context=256.
- Đối chiếu phát hiện Jaccard≥0,85 với hàm `near` của mã niêm phong gốc trên **1.000/1.000** cặp chuỗi tổng hợp: PASS.
- Bộ chạy kiểm SHA trước khi truy cập dữ liệu thật; chỉ chọn 320 + 256 bản ghi theo SHA; trên 320 truyện xác minh số token BPE và cửa sổ, tổng 75.798 mục tiêu, không tính logits hay NLL; báo cáo chỉ chứa tổng thống kê, không có ID hoặc raw story.
- Máy Windows đã được xác nhận có raw VALID, T1 split và manifest private. Tuy nhiên đầu chạy từ xa RemoteMCP hiện không có trực tiếp `run_command` vì yêu cầu tác vụ quản lý. **Chưa gọi lượt kiểm toán dữ liệu thật trong bước viết báo cáo này**. Không khẳng định kết quả 81.920 cặp đã PASS.

## 4. Phán quyết hữu hạn, không thêm quy trình nhỏ

**Trạng thái hiện tại: `HOLD_PENDING_SINGLE_REAL_VALIDATION_ONLY_AUDIT_RESULT`**, là HOLD vì **chưa thực thi 81.920 phép so sánh trên dữ liệu thật**, không phải HOLD vì cần thêm tài liệu/phê duyệt mới.

Chỉ cần đúng **một lần chạy** bộ kiểm toán trên máy sở hữu. Logic cuối đã được khóa:
- Nếu nguồn/cửa sổ/BPE khớp, và **0/81.920 cặp gần trùng**, trả `GO_SCOPED_CPU_ONE_SHOT_READY_SEPARATE_EXECUTION`. GO này chỉ mở **một lần CPU scoring riêng** và phải giữ giới hạn lịch sử TEST/donor nêu trên.
- Nếu có **≥1 cặp gần trùng**, trả `HOLD_NEAR_DUPLICATE_WITH_USED_VALIDATION`; **không** tự đổi 320 truyện hoặc nới ngưỡng.
- Nếu sai SHA, thiếu bản ghi, sai BPE nhãn hoặc cửa sổ, trả `HOLD_AUDIT_TECHNICAL_OR_MISSING_DATA`; không tự tính science.

Không mở thủ tục khác. `lineage.md` chỉ có kết quả khoa học PASS/FAIL, hiện không thay đổi. Không có claim, NLL, logits, GPU hay huấn luyện mới.

## 5. Cách chạy gọn trên Windows (PowerShell 5.1, Python 3.12)

Tải tệp Python từ hội thoại, đặt trong `D:\WORK\RESEARCH\TokenToModel-Lab\_tmp\ttm_gemma2_validation_only_near_audit_20261109\` và xác thực SHA-256 `80361cdfa16dd6c37ced6809adbbbd2ea778f9ef9ba7ebc578a7a9d9f7ed1f85`. Sau đó:

```powershell
$ErrorActionPreference='Stop'
$root='D:\WORK\RESEARCH\TokenToModel-Lab'
$py='C:\Users\minht\AppData\Local\Programs\Python\Python312\python.exe'
$script=Join-Path $root '_tmp\ttm_gemma2_validation_only_near_audit_20261109\ttm_gemma2_validation_only_near_audit_final_gate_20261109.py'
$expected='80361cdfa16dd6c37ced6809adbbbd2ea778f9ef9ba7ebc578a7a9d9f7ed1f85'
if (-not (Test-Path -LiteralPath $script)) {throw 'SOURCE_NOT_STAGED'}
if ((Get-FileHash -LiteralPath $script -Algorithm SHA256).Hash -ine $expected) {throw 'SOURCE_SHA256_MISMATCH'}
& $py -B $script --mode fixture-qa
if ($LASTEXITCODE -ne 0) {throw 'FIXTURE_FAIL'}
& $py -B $script --mode audit --repo $root
$code=$LASTEXITCODE
$receipt=Join-Path $root '_tmp\ttm_gemma2_validation_only_near_audit_20261109\VALIDATION_ONLY_NEAR_AUDIT_PUBLIC_RECEIPT.json'
if (Test-Path -LiteralPath $receipt) {Get-Content -LiteralPath $receipt -Raw}
Write-Host ('AUDIT_EXIT_CODE=' + $code)
```

Nội dung biên bản thật chỉ ghi `GO/HOLD`, số cặp trùng, mức tương đồng cao nhất, tổng số nhãn và SHA; không ghi thành viên, nguyên văn hay mô hình.

**Bước thực hiện tiếp theo:** chạy duy nhất lệnh kiểm toán trên máy sở hữu, đọc biên bản, và nếu GO thì mở **một** lượt CPU-scoring riêng của A/B/C/D; không tạo thêm thiết kế hoặc cổng QA mới.
