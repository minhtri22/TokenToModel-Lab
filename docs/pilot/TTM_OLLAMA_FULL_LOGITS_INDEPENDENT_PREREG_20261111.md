# TTM — OLLAMA FULL LOGITS: tiền đăng ký độc lập (2026-11-11)

**Trạng thái khi khóa:** `PREREGISTERED / NEW_OLLAMA_INFERENCE_NOT_EXECUTED`.
**Nhánh:** `research/ttm-t5-ollama-full-logits-20261111`; **base:** `5d52e32f20021e36f08f284ef9864d3ba36dbead` (main).
**Không thay đổi T5 v5:** `T5_WINDOWS_F32=PASS_SCOPED`, `OLLAMA_FULL_LOGITS=NOT_EXECUTED` cho T5, biên bản v5 SHA-256 `d63ba32e85c8472cc432b97eec2c9d98ee77224baed9eb7447c34bf5fe83a0b8`.
Tiền đăng ký máy đọc được: `artifacts/qa/ttm-ollama-full-logits/TTM_OLLAMA_FULL_LOGITS_F32_PREREG_20261111.json`.

## Mục tiêu và phép phân biệt bắt buộc

Kiểm tra **toàn bộ vector 2.048 raw logits trước sampler**, tại vị trí dự đoán token tiếp theo sau prompt, **do runner thực sự được tiến trình Ollama sinh ra**. So sánh cùng vị trí và ID với PyTorch P02 checkpoint bước 1.024 trên CPU F32. Đầu ra API `/api/generate`, `logprobs`, `top_logprobs` hoặc khớp văn bản **không chứng minh full logits**. Ollama 0.40.14 chỉ công bố tối đa 20 token ứng viên qua top-logprobs; cần hook có giới hạn trong runner. Không so sánh với một `llama.cpp` độc lập rồi gọi đó là kết quả trên Ollama.

## Khóa nguồn (source pin)

- GGUF F32: `5bdc904e6c51af04a4223219f36e6bc2e687f60fd6e17dc24508f3eb7489e4e5`; checkpoint P02 step1024: `cb985751795c8328ad65acf7ca4c1033ce35182c1bfbdb8c38550de629cb271b`.
- Ollama `9a3e8177767245acc62b735eba7d5d8a553606d0` (0.40.14), llama.cpp `39febd2adb947b70da35e95f9351b3bf58ad170a`, server-context.cpp Git blob gốc `2bd1ab9ec00ca581c70bac014f7ca6d3d2bae0ae`.
- Giữ GELU_ERF patch SHA-256 `47ef4854094d6b9db648cde7067a3d243b10ce632f0b58397e986110a7f62de2` và toàn bộ compatibility patches của v5. **Binary có thêm hook sẽ là ứng viên mới**, phải khóa hash mới; **không được nhận nó là binary v5 bất biến**.
- Hook tối thiểu ở `tools/server/server-context.cpp`, ngay trước `common_sampler_sample(..., tok_idx)`: `llama_get_logits_ith(slot.ctx_tgt, tok_idx)`. Chỉ chạy khi opt-in bằng biến môi trường trên server cách ly; ghi ID prompt thực tế và 2048 F32 nguyên gốc.

## Các fixture và vị trí đo đã khóa

| ID | Prompt raw | Token IDs đã biết từ tokenizer 9/9 | Logits đo |
|---|---|---|---|
| FL01 | `abc` | `[97,98,99]` | 2.048 sau token thứ 3 |
| FL02 | `hello` | `[257,304,111]` | 2.048 sau token thứ 3 |
| FL03 | `a\\nb` (newline thật) | `[97,10,98]` | 2.048 sau token thứ 3 |
| FL04 | `Xin chào` | `[88,267,628,195,160,111]` | 2.048 sau token thứ 6 |

Các prompt này từng xuất hiện trong kiểm tra **tokenizer**, không phải bộ held-out khoa học mới; đây là **kiểm thử kỹ thuật độc lập**, không phải ước lượng tổng quát hóa. Không dùng TEST/Q1Q2. Không tự ý thay prompt sau khi xem raw logits.

## Thứ tự thực thi hữu hạn

1. **Source preflight (không suy luận):** pin commit/file/blob; QA patch chỉ thay điểm dump trước sampling và include; kiểm tra không sửa logits/sampling, không mở kết nối ngoài loopback; kiểm tra chống ghi đè và chỉ tạo đầu ra trong TTM.
2. **True P02 reference:** chạy CPU PyTorch F32 từ đúng checkpoint đã pin, tính đúng bốn cặp token IDs; khóa SHA-256 JSONL reference **trước** khi chạy Ollama mới. Không thay checkpoint hoặc huấn luyện.
3. **Ollama candidate isolated:** build nguồn Ollama đã pin + compatibility + GELU_ERF + hook. Chạy riêng với `num_gpu=0`, `num_thread=1`, `num_ctx=256`, `num_parallel=1`, `KV K/V=F32`, Flash OFF, raw, temp0, seed42, max1, speculation OFF. Xác minh tiến trình con đúng binary và GGUF, process parent/pid/ports, các token IDs quan sát trong runner. **Không dùng hoặc chiếm cổng 11434 đang chạy của người dùng**.
4. **Independent QA:** exact 4 JSONL rows từ P02 và Ollama, mỗi row 2048 số hữu hạn. So trực tiếp `logits_ollama[i]-logits_P02[i]` đủ 8192 phần tử, ngưỡng max-abs `<= 0.001` và top1 trùng 4/4. Lưu max-abs, mean-abs, signed peak, index, top1 từng row, SHA các đầu vào và báo cáo. Không lọc top-K/softmax/shift logits.
5. **Independent provenance adjudication:** audit SHA binary/dll/GGUF/hook, parent-child process và cấu hình thật; chỉ sau đó mới gắn nhãn end-to-end `PASS`. Nếu thiếu bằng chứng thì `TECHNICAL_HOLD`, không gọi số học PASS là Ollama parity PASS.

## Phán quyết tách biệt

- `NUMERIC_PASS`: 4/4 full-vector direct raw comparisons PASS và top1 bằng nhau; **chưa** đủ cho `OLLAMA_FULL_LOGITS_PASS` nếu thiếu provenance.
- `NUMERIC_FAIL`: dữ liệu nguồn hợp lệ nhưng một vector vượt `0.001` hoặc top1 khác; giữ nguyên kết quả âm tính, không nới ngưỡng.
- `TECHNICAL_HOLD`: không lấy được tensor từ runner do Ollama spawn, nguồn/ID/cấu hình không đúng, output thiếu/trùng hoặc không hữu hạn.
- `END_TO_END_PASS`: chỉ khi cả numeric pass và attestation nguồn độc lập PASS.

Chỉ lưu biên bản nghiên cứu của nhánh mới. `lineage.md` chỉ append sau khi phân xử kết quả khoa học (nếu có); không tạo PR/merge tự động và **không mở lại hoặc sửa T5 F32 v5**.

**Bước thực hiện tiếp theo:** `TTM_OLLAMA_FULL_LOGITS_SOURCE_HOOK_REFERENCE_F32_AND_ONE_INTEGRATED_QA`: kiểm tra áp dụng patch và build offline, tạo reference P02 bốn fixture và khóa hash trước khi cho phép bốn phép infer Ollama cách ly; sau đó mới đo trên máy Windows.
