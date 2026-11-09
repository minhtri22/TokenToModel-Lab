# TTM T5 — Quyết định tích hợp lượt Ollama V4 tối giản (2026-11-09)

## Mục tiêu
Thử thực sự nhập GGUF F32 của checkpoint TTM-Small-4M vào Ollama 0.40.14 và sinh **tối đa 32 token**. Đây là kiểm tra tương thích kỹ thuật (compatibility-only), không đổi kết quả khoa học `T5_STRICT_FULL_LOGITS=FAIL_7_OF_8_PRESERVED`.

## Tình trạng đầu vào
- V1, V2, V3 RC1: `CONSUMED_NO_RERUN`, đều dừng trước `ollama create`; RC2 source-only 114/114 PASS trên Windows, không chạy Ollama.
- `State=0` được nhận thấy từ IP Helper Windows ngay khi Ollama đang phục vụ HTTP. Không tự suy diễn `LISTEN=2`.
- GGUF SHA256: `5bdc904e6c51af04a4223219f36e6bc2e687f60fd6e17dc24508f3eb7489e4e5`; Ollama executable SHA256: `14e0fff0449ce3c3a7fe9db8b8b32089274db5f835d4c99f5af7c32dcbf08981`.
- Đối chiếu tài liệu chính thức Ollama: `FROM <absolute .gguf path>` trong `Modelfile`, sau đó `ollama create`; xem https://github.com/ollama/ollama/blob/main/docs/import.mdx và https://github.com/ollama/ollama/blob/main/docs/modelfile.mdx.

## Gói bản chạy V4 mới và nguồn gốc
- Gói `TTM_T5_FINAL_MINIMAL_OLLAMA_COMPATIBILITY_SMOKE_20261109.zip`, SHA256 `9fde19c7f9a47d5d9548afb27f694e230116b5db5b34b5c227664c7cb81c8c34`, 24.309 byte, được tạo và kiểm tra byte trên assistant container. File ZIP được bàn giao trực tiếp trong cuộc trò chuyện; **chưa upload ZIP vào GitHub**. Manifest trong repository lưu SHA mọi nguồn để kiểm tra chéo.
- 35/35 bài kiểm định giả lập đạt PASS, cả mock pipeline và trường hợp từ chối. **Chưa có kiểm tra native Windows / Ollama trong lượt V4**.
- Cổng riêng `127.0.0.1:12647`; model tag `ttm-t5-f32-compat-only-v4final:latest`; output `D:\WORK\RESEARCH\TokenToModel-Lab\_tmp\ttm_t5_ollama_compat_only_single_v4final`, khác V1/V2/RC1/RC2.
- PowerShell wrapper `Invoke-TTM-T5-Final-Minimal-PS51.ps1 -Mode Smoke` kiểm tra repo/origin, SHA nguồn, chạy **35 bài kiểm định QA** và preview chỉ đọc; **nếu PASS mới chạy đúng một lần**. Không chạy lại 114 bài RC2.
- Trước import yêu cầu đúng pid, executable path, creation time, loopback-only, cùng socket state 0 chỉ là ứng viên UNKNOWN với đầu xa bằng 0; HTTP 200/version exact, kiểm lại TCP/identity. Giữ đầy đủ dấu vết, fail-closed với PID lạ, wildcard, HTTP mismatch hoặc thay đổi ownership.
- Store model trong project, không sửa dịch vụ 11434, không chạm hệ thống, TRAIN/TEST, checkpoint, main, lineage hoặc FAIL receipts. Lọc DLL xung đột khỏi PATH chỉ trong tiến trình con.

## Phán quyết
`RELEASE_DESIGN_AND_OFFLINE_QA=PASS_SCOPED_35_OF_35`.
`SINGLE_NATIVE_COMPATIBILITY_SMOKE=CONDITIONALLY_AUTHORIZED_BY_USER`: một lượt chỉ khi SHA ZIP/manifest, Windows QA, preclaim và cổng riêng PASS. **Chưa thực thi**. Nếu output root xuất hiện thì dù PASS/FAIL/HOLD đều `ONE_SHOT_CONSUMED_NO_RERUN`.

**Phán quyết PASS kỹ thuật** chỉ khi `ollama create` thành công, manifest nằm trong store dự án, tag đúng và `/api/generate` trả `done=true`, `eval_count` 1..32 cho đúng model. Suy luận thành công không đồng nghĩa parity hay chất lượng câu trả lời tốt.

## Bước tiếp theo
`TTM_T5_FINAL_MINIMAL_OLLAMA_COMPATIBILITY_SMOKE_EVIDENCE_READBACK_AND_ADJUDICATION`: nhận `RESULT.json`, dấu vết readiness và console từ Windows, phân xử theo giai đoạn, không tự chạy lại lượt thất bại.
