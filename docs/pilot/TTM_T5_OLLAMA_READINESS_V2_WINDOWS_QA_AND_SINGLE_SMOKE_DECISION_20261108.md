# TTM T5 — Tiếp nhận QA tĩnh Windows V2 và quyết định một lượt thử tương thích (2026-11-08)

## 1. Bằng chứng được tiếp nhận

- Người dùng đã thực hiện `test_independent_readiness_v2.py` với Python 3.12 trên Windows; console công bố **Ran 23 tests in 0.132s / OK**, `T5_V2_ZIP_SHA256=PASS`, `T5_V2_SOURCE_SHA256=PASS`, `T5_V2_WINDOWS_STATIC_QA=PASS`, `T5_V2_OLLAMA_EXECUTION=NOT_EXECUTED`, `T5_V1_ONE_SHOT=UNCHANGED`, `T5_STRICT_LOGITS=FAIL_PRESERVED`.
- Chi tiết 23 tên bài thử và cờ PASS đã được chuyển vào tệp JSON tiếp nhận trên nhánh. Đây là **bằng chứng console người dùng cung cấp**, không phải phiên Python native do agent chạy từ xa.
- Kiểm tra chéo gói ZIP nguồn: `SHA256=9da06fad41cd45a03f9221aade5de1fd6ef8446879276eebeebbebcbd9f71bbf`; 4/4 SHA nguồn trong manifest đúng; 23/23 mock test chạy ngoại tuyến độc lập trong môi trường assistant.
- File successor: `t5_ollama_smoke_v2.py`, SHA256 `de80194c4576ea8749fce0ec1367ee65a9d520f563ab70063006d5a6506def6f`.
- Checker: `test_independent_readiness_v2.py`, SHA256 `1d5da70808a9d63844b1a9ce66ba25864f27bee47b5c040d93795cebe4a7acae`.

## 2. Phán quyết

**`PASS_SCOPED_WINDOWS_STATIC_QA_23_OF_23`.** Có đủ bằng chứng để cho phép một lượt thử duy nhất về tương thích kỹ thuật (compatibility-only) mới mang danh tính V2. Đây **không** phải PASS về tương đương logits hay hiệu quả khoa học.

**`TTM_T5_V2_SINGLE_SMOKE=AUTHORIZED_ON_PRECLAIM_GUARDS`**:
- Chỉ dùng GGUF gốc SHA256 `5bdc904e6c51af04a4223219f36e6bc2e687f60fd6e17dc24508f3eb7489e4e5`, Ollama 0.40.14 và nguồn V2 đúng SHA ghim.
- V2 chỉ sử dụng cổng loopback `127.0.0.1:12644`, tag `ttm-t5-f32-compat-only-v2:latest`, `num_ctx=256`, `num_predict<=32`; prompt tổng hợp; không TRAIN/TEST.
- Chỉ được gọi `--mode preview` (đọc) và **nếu PASS** thì **một** lần `--mode execute` dưới `D:\WORK\RESEARCH\TokenToModel-Lab\_tmp\TTM_T5_OLLAMA_READINESS_V2_SOURCE_ONLY_20261108\t5_ollama_smoke_v2.py` bằng Python 3.12 Windows.
- Bắt buộc preclaim: không có evidence dir V2, cổng trống, SHA nguồn/GGUF/FAIL receipts đúng, Ollama executable đúng phiên bản, đủ disk; nếu bất kỳ điều kiện nào FAIL/HOLD thì **không** mở lượt.
- Khi execute đã tạo `_tmp\ttm_t5_ollama_compat_only_single_v2\CLAIM.json`, **một lượt được tính là đã tiêu thụ kể cả FAIL**. Tuyệt đối không dọn, ghi đè hoặc chạy lại; lưu `RESULT.json`, `READINESS_ATTEMPTS.jsonl`, `serve.log`, output create/generate nếu có.
- Không dùng/khởi động lại Ollama 11434; vùng ghi model riêng trong dự án; không sửa service toàn hệ thống. Cảnh báo `PATH` về `ggml-base.dll` chỉ quan sát, không quy nguyên nhân.
- Không truy cập hoặc sửa V1 `_tmp\ttm_t5_ollama_compat_only_single_v1`, `lineage.md`, `main`, checkpoint, GGUF.
- Nếu V2 chưa được chạy, trạng thái là `AUTHORIZED_NOT_EXECUTED`; không mô tả thành PASS runtime.

## 3. Nhận kết quả

Đọc lại `RESULT.json` và `READINESS_ATTEMPTS.jsonl` của V2, đối chiếu SHA gốc và log theo từng stage. Chỉ `PASS_COMPATIBILITY_ONLY_OLLAMA_IMPORT_AND_INFERENCE` khi có import, model-store manifest trong project, và HTTP generation hoàn tất tối đa 32 token; nếu không, FAIL/HOLD đúng giai đoạn. `T5_FULL_LOGITS=FAIL_7/8_PRESERVED` luôn giữ nguyên.

**Bước tiếp theo:** `TTM_T5_OLLAMA_V2_SINGLE_SMOKE_EXACT_ONCE_AND_EVIDENCE_READBACK`.
