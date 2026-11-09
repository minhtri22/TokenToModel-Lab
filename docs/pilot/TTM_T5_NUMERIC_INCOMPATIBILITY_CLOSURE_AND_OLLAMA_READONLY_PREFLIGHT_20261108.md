# TTM T5 — Đóng sai khác số học F32 và tiền kiểm Ollama chỉ đọc

**Ngày:** 2026-11-08  
**Mã công việc:** `TTM_T5_SCOPED_BACKEND_NUMERIC_INCOMPATIBILITY_CLOSURE_AND_OLLAMA_COMPATIBILITY_PREFLIGHT_READONLY`  
**Phạm vi:** TTM-Small4M T4 step 1024, T5 checkpoint → GGUF → llama.cpp / Ollama. Kiểm tra kỹ thuật, không nghiên cứu khoa học mới.  
**Giới hạn thao tác:** Không TRAIN/TEST, không sửa checkpoint/GGUF, không `ollama create/run/serve/pull`, không sửa `main` hay `lineage.md`, không thay ngưỡng logits.

## 1. Bằng chứng khóa và kết luận đóng backend F32

| Khóa/bằng chứng | Giá trị | Trạng thái |
|---|---|---|
| Checkpoint T4 step1024 SHA256 | `cb985751795c8328ad65acf7ca4c1033ce35182c1bfbdb8c38550de629cb271b` | Gốc, giữ nguyên |
| GGUF F32 SHA256 | `5bdc904e6c51af04a4223219f36e6bc2e687f60fd6e17dc24508f3eb7489e4e5` | 15.061.376 byte, 52 tensor F32, weight readback PASS |
| llama.cpp source commit | `372dc5ca157276beb6c67b2e92477e8d662e964a` | Pinned, không cập nhật |
| Original FAIL receipt SHA256 | `c61f73216764b8582a5c996e85c59feb55b13496ec0117deb713d9b1843ec8e8` | Giữ nguyên |
| V5B JSON SHA256 | `ac699d4e750037f88bbab776bb42a38079cd82b0a1c2f72385127ac5a36d9375` | Tokenizer 9/9, logits FAIL 7/8 |
| Single native intermediate JSON SHA256 | `8f1ed4f8ec5846084226807cccc1455638d4d2e08957827ffa15ed765d5220ae` | 8 fixture × 35 stage, independent QA scoped PASS |

### Phán quyết chính thức

- `T5_SCOPED_BACKEND_NUMERICAL_INCOMPATIBILITY=DOCUMENTED_CLOSED`: sai khác số học là có thật dưới backend llama.cpp đã pin; max |Δlogit| cuối `0.003362178805176086` lớn hơn ngưỡng đã khóa `0.001`; 7/8 bộ không đạt; 8/8 top-1 trùng trong V5B. **Không phải T5 parity PASS**.
- `FIRST_SENSITIVE_STAGE=ffn_inp-0` ở 8/8 bộ theo ngưỡng định vị `1e-5` (không phải ngưỡng chấp nhận). `inpL` bitwise-trùng tại điểm đo; các sai khác trước `ffn_inp-0` nhỏ. Vùng phát sinh sớm nhất quan sát được là **attention output + residual sau QKV**, không đủ dữ liệu để định danh kernel duy nhất. Các LayerNorm tiếp theo có thể khuếch đại sai khác.
- Thử PyTorch GELU-tanh (diagnostic-only) cải thiện max logits 6/8 fixture nhưng vẫn 7/8 FAIL: `GELU_CONTRIBUTION=POSSIBLE`, `EXACT_ROOT_CAUSE=NOT_ISOLATED`. Không sửa backend trên suy đoán, không nâng ngưỡng, không xóa FAIL cũ, không mở lần chạy parity mới.
- T4 khoa học/TEST vẫn PASS theo phạm vi riêng đã được phân xử, hoàn toàn không được diễn giải thành parity với llama.cpp.

Nguồn GitHub: `evidence/pilot/t5-trained/T5_F32_NUMERIC_LOCALIZATION_UNADJUDICATED.json` và `docs/pilot/TTM_T5_F32_NUMERIC_LOCALIZATION_INDEPENDENT_ADJUDICATION_20261108.md` trên nhánh PR #12; hai tài liệu giữ nguyên.

## 2. Ollama: tài liệu, nguồn công khai và giới hạn chứng minh

Đã đối chiếu tài liệu Ollama hiện hành:

- https://docs.ollama.com/import : `Modelfile` có thể khai báo `FROM /path/to/file.gguf` để chuẩn bị một lệnh `ollama create`; Ollama không lượng tử hóa GGUF khi nhập.
- https://docs.ollama.com/modelfile : `FROM` tham chiếu GGUF, `PARAMETER num_ctx`, `TEMPLATE` (có thể dùng prompt đơn thay vì cấu trúc chat). **Không tạo Modelfile trong bước này.**
- https://docs.ollama.com/cli : lệnh `ollama run/create/serve` có tác dụng chạy hoặc khởi tạo, **không gọi** trong tiền kiểm chỉ đọc.
- https://registry.ollama.com/treyleo16/gpt-2 : mô hình kiến trúc `gpt2` được phân phối cho Ollama; đây là ví dụ công khai, không phải bài kiểm thử Ollama đã cài trên Windows đích, không chứng minh GGUF riêng của TTM tương thích.

**Đánh giá:** `GGUF_IMPORT_MECHANISM=DOCUMENTED`; `GPT2_FAMILY_PLAUSIBILITY=SUPPORTED_BY_PUBLIC_EXAMPLE`; `TTM_EXACT_GGUF_OLLAMA_IMPORT=NOT_TESTED`; `TTM_EXACT_GGUF_OLLAMA_INFERENCE=NOT_TESTED`. Không suy ra rằng bản Ollama đang cài trên Windows có cùng backend hoặc nhận đúng GGUF này.

## 3. Những gì đã xác minh trên Windows đích (chỉ đọc)

- RemoteDesktop liệt kê thấy `D:\WORK\RESEARCH\TokenToModel-Lab\_tmp\ttm_t5_trained_f32_v1\TTM-Small4M-T4-step1024-F32.gguf`, các receipt T5 gốc và thư mục chẩn đoán đơn có `CLAIM.json`, 8 thư mục fixture, cùng JSON kết quả.
- Đường điều khiển từ xa quản lý bằng tác vụ không cung cấp general shell; catalog bảo trì chỉ expose targeted pytest, không expose lệnh Ollama/version. **Chưa trực tiếp thực thi `ollama --version`, kiểm tra phiên bản backend, GET `/api/version` hoặc đọc lại GGUF trên máy ở lượt này.**
- Python thư viện chuẩn trên môi trường kiểm thử của trợ lý: bộ đọc GGUF cấu trúc `PASS_UNIT_SYNTHETIC_POSITIVE_AND_NEGATIVE`; PowerShell kiểm tra bề mặt thao tác tĩnh `PASS_NO_MODEL_MUTATION`. **PowerShell 5.1 trên Windows đích chưa chạy bộ tiền kiểm mới**.

## 4. Bộ tiền kiểm độc lập chỉ đọc đã chuẩn bị

Gói `TTM_T5_OLLAMA_READONLY_PREFLIGHT_V1.zip` gồm:

1. `Inspect-TTM-GGUF-ReadOnly.py`: SHA256 chính xác của GGUF, đọc metadata GGUF v3, kiểm tra gpt2/4 lớp/256 embedding/4 head/context 256/2048 token/1791 merge/52 tensor F32 và mọi descriptor nằm trong giới hạn tệp. Không đọc weights thành torch, không chạm TEST.
2. `Inspect-TTM-Ollama-ReadOnly-PS51.ps1`: xác nhận project root, chỉ đọc GGUF và thông tin Ollama CLI, phiên bản, process, cổng localhost 11434, GET `/api/version`. Không lệnh model-create, inference hoặc download. Chỉ in console, không tự ghi file.
3. README tiếng Việt có câu lệnh PowerShell 5.1.

**Điều kiện kết quả:** Nếu GGUF SHA hoặc metadata không khớp thì `FAIL_CLOSED`; nếu môi trường Ollama không có/không truy cập được, ghi `HOLD_LOCAL_ENV`; ngay cả khi tiền kiểm đạt, nhãn kết luận vẫn chỉ là `READONLY_PREFLIGHT_COMPLETED_COMPATIBILITY_NOT_TESTED`.

## 5. Điều kiện cho quyết định tương lai (không thực thi trong bước này)

Nếu chủ dự án muốn xác minh khả năng chạy thực tế sau tiền kiểm: tách một lần `COMPATIBILITY_ONLY` trong project workspace, chỉ nhập GGUF gốc bằng Modelfile đơn giản, không template chat làm lệch GPT-2 base; giới hạn context đúng 256; ghi phiên bản Ollama và SHA trước/sau, ghi cả lỗi nếu bị từ chối, rồi chạy prompt tổng hợp ngắn. Đó là **lượt thử khác** và không thể biến FAIL số học thành PASS khoa học. Không triển khai việc này trong tài liệu hiện tại.

**Kết luận / tiêu chí đóng:** `T5_BACKEND_NUMERIC_LIMITATION=DOCUMENTED_CLOSED` · `T5_GGUF_EXPORT=PASS_PRESERVED` · `T5_TOKENIZER=PASS_9_OF_9_PRESERVED` · `T5_STRICT_LOGITS=FAIL_7_OF_8_PRESERVED` · `OLLAMA_PREFLIGHT=PARTIAL_READONLY_PENDING_WINDOWS_EVIDENCE` · `OLLAMA_IMPORT_AND_INFERENCE=NOT_TESTED` · `T4_SCIENCE=UNCHANGED`.

**Không chỉnh `lineage.md`:** biên bản này là kiểm định kỹ thuật, không phải một kết luận khoa học thay thế. PR #12 tiếp tục DRAFT.

**Bước thực hiện tiếp theo:** `TTM_T5_OLLAMA_LOCAL_READONLY_PREFLIGHT_EVIDENCE_READBACK` — chỉ nhận output của bộ tiền kiểm trên Windows, xác minh SHA/metadata/phiên bản và phân xử có đủ điều kiện cho một lượt compatibility-only riêng hay không.
