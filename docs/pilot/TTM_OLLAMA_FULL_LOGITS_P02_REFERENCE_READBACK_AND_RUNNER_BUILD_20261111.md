# TTM — Tiếp nhận reference FL01–FL04 và stage runner Ollama full logits (2026-11-11)

## Kết quả owner-local

Bộ reference mới **4×2.048 logits** từ P02 F32 step1024 đã chạy trên Windows, checkpoint SHA256 `cb985751795c8328ad65acf7ca4c1033ce35182c1bfbdb8c38550de629cb271b`. Python 3.12 / torch `2.11.0+cpu`; offline tests 7/7 PASS; reference auditor local ghi `PASS_REFERENCE_4_OF_4_X_2048`.

- Reference raw SHA256: `1e098a643c9bce66431adf3dc0296ce6b628731d33c4532753d2f2acd664d082`.
- Seal SHA256 do owner đọc lại: `571a1a654bad1b97de066d6fb3b690e910ecc71777deb4b16b7b15968f444939`.
- Kết nối RemoteDesktop chỉ đọc xác nhận hai file tồn tại và seal metadata khớp, nhưng giới hạn ~20.000 ký tự đọc file khiến việc kiểm tra độc lập toàn bộ logits raw bằng kết nối **chưa thực hiện**. Không giả nhận đây là phép tính lại raw 8192 chiều.
- Bằng chứng máy đọc: `artifacts/qa/ttm-ollama-full-logits/TTM_OLLAMA_FULL_LOGITS_P02_REFERENCE_OWNER_REMOTE_READBACK_20261111.json`.

## Source & build step tiếp theo

`tools/ollama_full_logits_v1/stage_and_build_ollama_full_logits.py` chuẩn bị cây ứng viên riêng trong TTM, từ nguồn v5 đã pin:
- Ollama `5d52e32f20021e36f08f284ef9864d3ba36dbead` chỉ là mốc main TTM; Ollama thực sự pin `9a3e8177767245acc62b735eba7d5d8a553606d0`, llama.cpp `39febd2adb947b70da35e95f9351b3bf58ad170a`.
- Từ `_tmp/t5-ollama-custom-v4/ollama` và `_tmp/t5-ollama-custom-v4/llama`, chỉ đọc nguồn cũ, kiểm 4 Git blobs postpatch v5, tạo **git worktree mới bên trong TTM** cho llama, copy đúng 4 file postpatch, áp dụng hook vào file `tools/server/server-context.cpp`, chặn nếu thay đổi ngoài 5 file.
- Trước mọi build, script đọc lại raw reference 4×2048 trên Windows, kiểm SHA256 raw và seal tuyệt đối. Chế độ `--build` chạy CMake VS2022 trong stage riêng, sao chép gói v5 sang package riêng rồi install ứng viên native. Gói v5 cũ không bị sửa, Ollama không chạy.
- Nơi lưu output: `_tmp/ttm_ollama_full_logits_candidate_build_20261111/STAGE_RECEIPT.json`. Không xóa/retry khi stage đã tồn tại. Lần chạy thành công mới dùng SHA binary candidate làm đầu vào cho bước thử nghiệm Ollama cách ly.
- Script tự khóa source Git HEAD được truyền bởi owner, không merge main, không sửa GGUF, không TEST, không train và không thay `lineage.md`.
- **Cảnh báo:** vì chưa chạy build trên Windows tại thời điểm commit, cấu hình/biên dịch native vẫn là `NOT_EXECUTED`. PASS source patch của lượt trước chỉ là `git apply --check`, không chứng minh build.

**Bước thực hiện tiếp theo** `TTM_OLLAMA_FULL_LOGITS_ISOLATED_RUNNER_STAGE_BUILD_AND_INDEPENDENT_QA`. Chạy một lượt chỉ build/QA từ source đã pin, đọc receipt và log. Nếu PASS, sau đó mở đợt lấy 4 raw logits qua chính Ollama child-process, gắn provenance và so sánh với reference đã khóa. T5 F32 v5 bất biến.
