# TTM — Final adjudication: Ollama child raw logits (FL01–FL04)

Ngày 2026-11-11. Nhánh: `research/ttm-t5-ollama-full-logits-20261111`. **Phán quyết độc lập: `PASS_SCOPED_OLLAMA_CHILD_FULL_RAW_LOGITS_4_OF_4`**. Không liên quan đến đóng/merge T5 v5 trên main.

## Phát hiện khoa học

Bốn prompt cố định FL01–FL04 chạy một lần trong child runner do Ollama v0.40.14 khởi chạy, F32 trước sampler; tham chiếu trực tiếp PyTorch P02 checkpoint bước 1.024. Bộ kiểm toán thứ hai (không inference, 8/8 QA offline) đọc lại toàn bộ 8.192 logits và tính lại sai số, đối chiếu ngưỡng đăng ký `max_abs≤0.001` và Top-1, PASS 4/4.

| Prompt | max_abs | Top-1 (P02/Ollama) |
|---|---:|---:|
| FL01 | 0.000005245208740234375 | 99/99 |
| FL02 | 0.00000476837158203125 | 282/282 |
| FL03 | 0.00000476837158203125 | 282/282 |
| FL04 | 0.0000095367431640625 | 46/46 |

Max toàn cục `0.0000095367431640625` (ngưỡng `0.001`). Không bằng nhau bitwise tuyệt đối.

## Kiểm tra nguồn gốc

Ghi nhận lúc chạy: parent PID 580, child PID 27488, API 12651, native 50871, 4 CIM snapshots cùng PID; native log 4 HTTP generate, CPU/KV F32, Flash OFF, 1 child launch, dọn cây tiến trình thuộc sở hữu. Kiểm toán độc lập **đối chiếu bản ghi đã khóa**, không tái chứng kiến tiến trình sau khi kết thúc.

## Bằng chứng

- Run receipt SHA256: `18f2fea2d986449eda098a949103e9614ab3c8a1a2368a3647c0c7729dbda269`.
- Ollama raw JSONL SHA256: `af289d6cbe52931581b6b0419d0239d80bbdd95d19357abbeb586ae53d1dd9e1`.
- Independent final original (Windows owner báo) SHA256: `1c0d48e8072de3a33849eb490a4118493e4479b6c3488fbc263b86cf237e8066`.
- GGUF SHA256: `5bdc904e6c51af04a4223219f36e6bc2e687f60fd6e17dc24508f3eb7489e4e5`; P02 reference SHA256: `1e098a643c9bce66431adf3dc0296ce6b628731d33c4532753d2f2acd664d082`; custom runner SHA256: `818fec27008b0a8555ecbae09c8c95e6a076d2b2fa4c26377b8bdb248232210a`.
- Bản báo cáo khoa học metadata: `artifacts/qa/ttm-ollama-full-logits/TTM_OLLAMA_FULL_LOGITS_FL01_FL04_FINAL_SCIENCE_ADJUDICATION_20261111.json`; tệp gốc nằm trong `_tmp/fl3/`.

Giới hạn: bốn prompt, một mô hình, Windows CPU, KV F32/Flash OFF và bản Ollama **tùy chỉnh**. Không kết luận về stock Ollama, Flash ON, F16, GPU hoặc khả năng khái quát. Các kết quả khoa học L0013 âm tính và L0014 dương tính vẫn không đổi. Không run TEST, không train lại, không rerun inference. Chỉ nối thêm L0015 trên nhánh này; **main bất biến, nhánh đóng khoa học nhưng chưa merge**.

**Bước thực hiện tiếp theo:** cập nhật báo cáo danh mục TTM với nhãn `SCOPED_PASS_CLOSED_UNMERGED`; nếu thử cấu hình mới, lập tiền đăng ký độc lập thay vì chạy lại một lượt đã khóa.
