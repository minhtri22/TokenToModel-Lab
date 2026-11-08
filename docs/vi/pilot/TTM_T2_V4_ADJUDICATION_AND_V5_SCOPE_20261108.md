# TTM T2 V4 — Phán quyết lỗi và giới hạn chẩn đoán V5 (08/11/2026)

> Bản diễn giải tiếng Việt của [biên bản V4 gốc](../../pilot/TTM_T2_V4_ADJUDICATION_AND_V5_SCOPE_20261108.md). Trạng thái kỹ thuật FAIL/STOP được bảo toàn, không đổi thành PASS vì các kết quả phục hồi về sau.

**Nguồn chứng cứ:** nhật ký PowerShell 5.1 do người dùng cung cấp, kết hợp biên bản JSON đọc trực tiếp trên Windows:

`D:\WORK\RESEARCH\TokenToModel-Lab\_tmp\ttm_t2\v4_recovery\TTM_T2_V4_CPU_DLL_LOGITS_TOKENIZER_REPORT.json`

- SHA-256 báo trên cửa sổ lệnh (Console) chủ dự án: `b1f064e5626db5b4034b9bf17e424257db767616bc2eae4a420f2be88dca7a34`; V5 phải kiểm tra lại byte nguồn.
- Mã đối tượng Git (Source Git Blob) P02 `9762343e06cf800b50574c2871ae1ed58537fb18`; phiên bản `llama.cpp` được ghim (Pinned) `372dc5ca157276beb6c67b2e92477e8d662e964a`.
- SHA-256 GGUF nguồn F32: `66ac11327904d010b326a281998ccd6efec25ff54f12cbcacd9257b5de00b2ac`; F16: `cb5a3c9fa2ee1e08489e0fcf400bbab7e9e6349eebf49cd6906bde29f19a8890`.
- Bộ chạy nguồn V4 cùng các kiểm tra thư viện động (DLL) PASS; không tải dữ liệu mới, không huấn luyện, không GPU hoặc Colab.

## Kết quả kiểm toán theo biên bản V4

| Hạng mục | Kết luận |
|---|---|
| Kiểm tra cấu trúc mô hình/GGUF có **52 tensor** | `PASS` (V3) |
| Trình nạp V4 và biến đường dẫn thư viện động (DLL PATH) | `PASS` — bộ thăm dò F32 chạy |
| Logits F32, **8/8** trường hợp số học | `PASS` — sai lệch tuyệt đối lớn nhất `0.0008664131268951158` với ngưỡng `0.001`, số ca sai Top-1 bằng `0` |
| Bộ tách token (Tokenizer) F32, **9** tình huống | `FAIL_PARITY` — **5/9** khớp, **4/9** khác |
| Giải mã F16 trên CPU bằng chương trình gốc (Native Decode) | `STOP_RUNTIME` — tiến trình con trả mã `3221226505` = `0xC0000409`, không có logits hợp lệ |
| Lỗi chuẩn (Standard Error) F16 | `binary_op: unsupported types: dst: f32, src0: f32, src1: f16`, tại `ggml-cpu/binary-ops.cpp:136` đã ghim |
| Phán quyết tổng hợp V4 | `T2_FULL=STOP_RUNTIME_OR_ARTIFACT`, **không phải** `T2_FULL_PASS` |

### Chi tiết chênh lệch bộ tách token F32 (Tokenizer Mismatch)

- `café`: mong đợi `[99,359,195,169]`, thực tế `[99,359,239,191,189]`.
- `a b`: mong đợi `[289,98]`, thực tế `[97,32,98]`.
- `a\nb`: mong đợi `[267,98]`, thực tế `[97,10,98]`.
- `Xin chào`: mong đợi `[88,105,110,32,873,195,160,111]`, thực tế `[88,105,110,32,873,239,191,189,111]`.

**Phân loại theo giới hạn bằng chứng:** dấu cách và xuống dòng cho thấy bất tương thích giữa bộ BPE tham chiếu trên **toàn chuỗi (Whole-string Oracle)** và bước tiền phân đoạn bằng biểu thức chính quy (Regex Pretokenization) với `tokenizer.ggml.pre=gpt-2`. Hai sai lệch Unicode có thể đến từ việc `ttm_t2_probe.cpp` lấy tham số qua `std::string s(argv[3])` trong môi trường dòng lệnh ANSI Windows, làm mất byte UTF-8. Cần kiểm chứng các byte UTF-8 bằng biểu diễn thập lục phân ASCII (ASCII-hex) trước khi kết luận chính tokenizer sai. Không âm thầm sửa bộ tham chiếu để đạt PASS.

**Lỗi F16:** đây là xung đột kiểu số trong đồ thị tính toán CPU (CPU Graph Data-type Conflict), **không phải thiếu DLL**. Mã dừng `0xC0000409` xuất hiện khi chương trình gốc (Native Backend) bỏ dở sau lỗi cộng hai kiểu F32/F16. Giả thuyết cần kiểm chứng: nhúng token hoặc giá trị trung gian (Activations) ở F32, trong khi nhúng vị trí đã học (Learned Position Embeddings) ở F16 khiến phép `ggml_add` khác kiểu. Không sửa mô hình P02 làm mốc, không lấy ứng viên F16 hỗn hợp để khẳng định F16 thuần.

## Tuyến kế tiếp V5 — chỉ chẩn đoán kỹ thuật (Technical Diagnostic)

- Bảo toàn V3/V4 đã khóa; **không chạy lại**. Trên Windows đã tìm thấy `build\upstream_llama\src\Release\llama.lib` và bốn DLL trong `build\bin\Release`.
- Gói hiện vật ngoại tuyến `TTM_SMALL4M_T2_V5_UTF8_AND_F16_MIXED_DIAGNOSTIC_20261108.zip`, SHA-256 `93A08884FF2DEB0DE61F4A2105E8B4F7C7E24BD601363D83F6568D3C20F35440`.
- Bộ mã Python + CMake + C++ mới có tùy chọn `--tokenize-hex UTF8_BYTES` để vượt lỗi tham số ANSI Windows. CMake chỉ biên dịch bộ thăm dò mới từ `llama.lib` đã có, không tải hoặc biên dịch lại dự án nguồn.
- Dùng lại tệp GGUF F32 cũ. Tạo hiện vật riêng chứa **51 tensor F16** và `position_embd.weight` ở F32 trong `_tmp\ttm_t2\v5_technical`, không ghi đè.
- Kiểm thử tĩnh ngoại tuyến (Offline Static QA) **6/6 PASS**; đọc lại GGUF hỗn hợp: **52 tensor**, đúng **1 tensor vị trí F32**, sai lệch lớn nhất khi đọc lại trọng số `3.0517578125e-5`, PASS. **Khi ghi biên bản, các phép chạy V5 thực trên Windows về UTF-8/tokenizer/logits chưa thực hiện.**
- V5 Windows phải kiểm tra SHA, cú pháp PowerShell 5.1 rồi chạy `Preview`; chỉ `Execute` đúng một lần nếu Preview PASS. Biên bản riêng `TTM_T2_V5_UTF8_AND_F16_MIXED_DIAGNOSTIC.json`. Không chạy lại V4, không sửa TinyStories, không dùng GPU, không thay đổi P07 hoặc `lineage.md`.

**Phán quyết tại thời điểm đó:** `T2_F32_BACKEND_NUMERIC=PASS`, `T2_SYNTHETIC_TOKENIZER=FAIL_4_OF_9`, `T2_F16_NATIVE_CPU=STOP_MIXED_DTYPE`, `T2_FULL=HOLD`, `SCIENCE_LOCK=NOT_GRANTED`. V5 chỉ kiểm tra giả thuyết trước khi quyết định sửa tokenizer/bộ chuyển đổi (Adapter) và khóa khoa học. Một phép thử hỗn hợp V5 đạt không tự cấp quyền huấn luyện.
