# TTM T2 V4 — Định danh lỗi và V5 chẩn đoán đúng phạm vi (2026-11-08)

**Nguồn chứng cứ:** Windows PowerShell 5.1 console do chủ dự án cung cấp, cộng với **biên bản đã đọc trực tiếp** bằng kết nối đọc tệp trên Windows:

`D:\WORK\RESEARCH\TokenToModel-Lab\_tmp\ttm_t2\v4_recovery\TTM_T2_V4_CPU_DLL_LOGITS_TOKENIZER_REPORT.json`

- SHA-256 **theo console chủ dự án**: `b1f064e5626db5b4034b9bf17e424257db767616bc2eae4a420f2be88dca7a34` (V5 sẽ bắt buộc xác minh lại byte hash).
- P02 source blob `9762343e06cf800b50574c2871ae1ed58537fb18`; pinned llama.cpp `372dc5ca157276beb6c67b2e92477e8d662e964a`.
- F32 source GGUF SHA `66ac11327904d010b326a281998ccd6efec25ff54f12cbcacd9257b5de00b2ac`; F16 SHA `cb5a3c9fa2ee1e08489e0fcf400bbab7e9e6349eebf49cd6906bde29f19a8890`.
- V4 source runner/script and DLL checks PASS; no new data, train, GPU, or Colab.

## Kết quả kiểm toán theo biên bản gốc

| Hạng mục | Kết luận |
|---|---|
| Model/GGUF structural 52 tensors | `PASS` (V3) |
| V4 loader / DLL PATH | `PASS` (F32 probe runs) |
| F32 8/8 numerical logits | `PASS` — max absolute `0.0008664131268951158` vs threshold `0.001`; top-1 mismatch `0` |
| F32 tokenizer 9 fixtures | `FAIL_PARITY` — 5/9 match, 4/9 differ |
| F16 native CPU decode | `STOP_RUNTIME` — subprocess `3221226505` = `0xC0000409`, no valid logits |
| F16 stderr | `binary_op: unsupported types: dst: f32, src0: f32, src1: f16` at pinned ggml-cpu binary-ops.cpp:136 |
| V4 summary | `T2_FULL=STOP_RUNTIME_OR_ARTIFACT`, not `T2_FULL_PASS` |

### F32 tokenizer mismatch details

- `café`: expected `[99,359,195,169]`, actual `[99,359,239,191,189]`.
- `a b`: expected `[289,98]`, actual `[97,32,98]`.
- `a\nb`: expected `[267,98]`, actual `[97,10,98]`.
- `Xin chào`: expected `[88,105,110,32,873,195,160,111]`, actual `[88,105,110,32,873,239,191,189,111]`.

**Phân loại không vượt bằng chứng:** khoảng trắng/newline là bất tương thích giữa BPE oracle **whole-string** và regex pretokenization `tokenizer.ggml.pre=gpt-2`. Hai trường hợp Unicode có thể do `ttm_t2_probe.cpp` truyền Unicode qua `std::string s(argv[3])` với narrow/ANSI Windows argv, khiến UTF-8 không được bảo toàn; phải kiểm chứng UTF-8 bytes qua ASCII-hex trước khi kết luận chính tokenizer sai. Không sửa oracle âm thầm để lấy PASS.

**F16:** đây là CPU graph data type conflict, không phải thiếu DLL. Lỗi `0xC0000409` phát sinh do native backend abort sau báo unsupported mixed F32/F16 operation. Giả thuyết có thể kiểm chứng: token embeddings/activations F32 nhưng learned-position embeddings ở F16 gây `ggml_add` khác kiểu. Không sửa/tấn công baseline P02, không biến F16 mixed candidate thành tuyên bố F16 thuần.

## V5 successor — chỉ chẩn đoán kỹ thuật

- **V4/ V3 frozen, không chạy lại.** Trên Windows đã kiểm tra thư mục `build\upstream_llama\src\Release\llama.lib` và bốn DLL `build\bin\Release` có mặt.
- Offline artifact: `TTM_SMALL4M_T2_V5_UTF8_AND_F16_MIXED_DIAGNOSTIC_20261108.zip`, SHA256 `93A08884FF2DEB0DE61F4A2105E8B4F7C7E24BD601363D83F6568D3C20F35440`.
- Python + CMake + native C++ helper mới: `--tokenize-hex UTF8_BYTES` để tránh môi trường Windows ANSI. CMake chỉ build **probe** mới từ prebuilt `llama.lib`, không build/upstream/re-fetch. Reuse existing F32 GGUF; tạo **artifact riêng** với 51 F16 tensors + `position_embd.weight` F32 trong `_tmp\ttm_t2\v5_technical`, không ghi đè.
- Offline static QA `6/6 PASS` và mixed F16/F32 GGUF readback: 52 tensors, đúng một F32 positional tensor; max abs weight roundtrip `3.0517578125e-5` PASS. **Windows runtime + actual UTF-8/tokenizer/numerical V5 NOT EXECUTED**.
- Windows V5 phải verify SHA file và PS5.1 parser trước `Preview`; chạy `Execute` đúng một lần nếu Preview PASS; receipt riêng `TTM_T2_V5_UTF8_AND_F16_MIXED_DIAGNOSTIC.json`. Không thử chạy lại V4, không sửa dữ liệu TinyStories, không dùng GPU, không sửa P07 hay `lineage.md`.

**Verdict:** `T2_F32_BACKEND_NUMERIC=PASS`, `T2_SYNTHETIC_TOKENIZER=FAIL_4_OF_9`, `T2_F16_NATIVE_CPU=STOP_MIXED_DTYPE`, `T2_FULL=HOLD`, `SCIENCE_LOCK=NOT_GRANTED`. T2 V5 chỉ chẩn đoán giả thuyết trước khi quyết định sửa tokenizer/adapter và khóa science. Không coi một kết quả V5 mixed pass là quyền huấn luyện.
