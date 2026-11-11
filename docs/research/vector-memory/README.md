# TTM — Nghiên cứu độc lập về bộ nhớ vector ngoài (External Vector Memory)

**Nhánh:** `research/ttm-vector-memory-architecture-20261111` · **Ngày:** 2026-11-11.

Đây là nhánh **nghiên cứu khám phá** phục vụ tối ưu hóa hoặc thay đổi kiến trúc về sau; không thay đổi lộ trình P00–P12, không phải tính năng đã được chấp nhận cho `main`, không merge. Mọi thay đổi đều nằm trên nhánh này. `lineage.md` append-only: chỉ thêm kết quả khoa học thực nghiệm PASS/FAIL; bằng chứng kỹ thuật và thiết kế nằm trong thư mục riêng.

## Câu hỏi và đối chứng

Liệu kết quả tìm kiếm vector dựa vào nội dung ngữ cảnh (không dựa vào token ID của đối tượng cần tìm), khi được truyền **vào cùng Weights + Attention + MLP** của checkpoint đã huấn luyện, có giảm NLL trên văn bản kiểm tra thật hay không?

Nguồn: checkpoint TTM-Small-4M 1.280 bước SHA-256 `ee723407b2c25a18be20e26387a3dd8e4a18e2942d469279b6f0748ff86af0dc`; nguồn P02 Git blob `9762343e06cf800b50574c2871ae1ed58537fb18`. Bộ TRAIN/VAL TinyStories riêng đã token hóa có SHA-256 `184f68b4c0c800ef3e98362c2e20e1cd35baa269e926489a475664526ecd9913`. Không đọc hoặc đánh giá TEST. **Không commit checkpoint, dữ liệu thô hoặc cửa sổ token có thể giải mã** lên GitHub.

### Thử nghiệm thứ nhất — ID-keyed exact externalization (đã chạy trước khi mở nhánh)

Chuyển ma trận `tok.weight == head.weight` 524.288 phần tử sang kho vector ngoài; giữ cùng P02 Attention/MLP/LayerNorm/vị trí và phép chiếu đầu ra.

Trên 64 chuỗi × 32 token **tổng hợp**, truy xuất FP32 chính xác cho logits bit-exact (`max_abs=0`); FP16 `max_abs=0.003446`, Top-1 100%; INT8 `max_abs=0.077984`, Top-1 99,56%. Đây là **PASS trong phạm vi exact lookup**, không phải xác minh truy xuất theo nội dung hoặc năng lực ngôn ngữ. Unique learned weights trước: 3.749.376; lõi sau khi tách bảng: 3.225.088; toàn hệ thống vẫn lưu bảng đó bên ngoài, không xóa tri thức khỏi hệ thống.

### Thử nghiệm thứ hai — Contextual vector retrieval, TRAIN → VAL (đã chạy 2026-11-11)

- Cố định toàn bộ tham số đã học và head buộc chung; **không huấn luyện** thêm.
- Chọn 512 truyện TRAIN và 128 truyện VAL độc lập, một cửa sổ ngữ cảnh 64 token và một target/truyện. Không lấy target VAL để làm khóa/giá trị truy xuất.
- Khóa bộ nhớ: hidden state theo ngữ cảnh từ frozen P02 trên TRAIN. Giá trị: embedding của **token tiếp theo thực có trong TRAIN**. Truy vấn: hidden state của tiền tố VAL đang quan sát; cosine top-4, nhiệt độ 0,05.
- A: checkpoint chuẩn; B: tách bảng vector FP32 nhưng truy xuất chính xác; C: thay 25% embedding tại vị trí dự đoán bằng tổ hợp vector lấy qua nội dung; D: cùng truy xuất nhưng xáo giá trị TRAIN (đối chứng âm). Mọi dự đoán chạy cùng Transformer.
- Tiêu chí thăm dò cố định: **C NLL phải thấp hơn cả A và D**. Không tối ưu hyperparameter theo VAL.

| Nhánh | NLL (nats/target) | Perplexity | Top-1 accuracy |
|---|---:|---:|---:|
| A — GPT đã huấn luyện | 3.408361 | 30.21569 | 34,38% |
| B — External exact FP32 | 3.408361 | 30.21569 | 34,38% |
| C — Contextual kNN vector | 3.607639 | 36.87889 | 28,91% |
| D — Shuffled retrieved values | 3.586965 | 36.12428 | 27,34% |

**Kết quả: `FAIL_EXPLORATORY`** đối với cấu hình cố định này. C kém A `+0.199278` nats/target; C cũng kém D `+0.020674` nats/target. Đường B vẫn bit-exact, chứng tỏ đối chứng chung Backbone chính xác. Truy xuất next-token đúng ngay top-1 TRAIN context đạt 14,06% và đúng trong top-4 là 32,81% trong lượt chạy chi tiết.

Không suy ra mọi phương pháp bộ nhớ ngữ nghĩa đều thất bại; chưa thử learned adapter/cross-attention, nhiều giá trị alpha, bộ nhớ từ nguồn ngoài TRAIN, đánh giá OOD và kiểm định thống kê. Hidden state theo ngữ cảnh không đương nhiên có ngữ nghĩa tối ưu cho tìm kiếm.

## Bằng chứng và tái lập

- `artifacts/research/vector-memory/TTM_ID_EXACT_20261111.json`: bản ghi chứng cứ thí nghiệm đầu tiên.
- `artifacts/research/vector-memory/TTM_CONTEXTUAL_VAL_20261111.json`: NLL và đối chứng trên dữ liệu VAL thật.
- `tools/research/vector-memory/mini_test.py`: CPU runner tự chứa logic, import chính P02 source của repo, pin SHA checkpoint/pack; chỉ ghi metric tổng hợp.

Chạy (PowerShell) từ repo TTM, các tệp nhị phân **nằm trong project root và chỉ đọc**:

```powershell
$root = 'D:\WORK\RESEARCH\TokenToModel-Lab'
$python = 'C:\Users\minht\AppData\Local\Programs\Python\Python312\python.exe'
& $python (Join-Path $root 'tools\research\vector-memory\mini_test.py') `
  --repo-root $root `
  --checkpoint (Join-Path $root '_tmp\vector-memory\checkpoint.pt') `
  --private-pack (Join-Path $root '_tmp\vector-memory\T4_PRIVATE_TRAIN_VAL_WINDOWS.npz') `
  --output (Join-Path $root '_evidence\vector-memory\contextual_val_result.json')
```

Không sao chép bộ TRAIN/VAL có thể giải mã vào repo Git; chỉ đưa SHA, chỉ số tổng hợp và mã chạy lên nhánh nghiên cứu. Việc xuất bản hoặc ứng dụng về sau cần đánh giá mới, không suy từ thử nghiệm này.

## Pilot TRAIN-only Adapter vs Exact Lookup (2026-11-11)

- Phán quyết: **NO_SCOPED_EXPLORATORY**, adapter có memory không cải thiện NLL so với checkpoint gốc hoặc memory đảo trên subset 128 VAL targets.
- [Báo cáo và giới hạn](ADAPTER_TRAIN_ONLY_PILOT_20261111.md); JSON aggregate tại `artifacts/research/vector-memory/TTM_ADAPTER_TRAIN_ONLY_PILOT_20261111.json` và entry `lineage.md` L0017.
- Chỉ nghiên cứu; không merge vào main.

## Retrieval signal diagnostic (2026-11-11)

- Kết luận: `KEY_LABEL_ASSOCIATION=YES_SCOPED`, `INCREMENTAL_NLL_GAIN=NO_SCOPED`, `VECTOR_MEMORY_TRAINING=PAUSED`.
- Chứng cứ: [báo cáo](RETRIEVAL_SIGNAL_DIAGNOSTIC_20261111.md), JSON aggregate, runner CPU và kiểm toán 22/22 tại `artifacts/research/vector-memory/` / `tools/research/vector-memory/`; `lineage.md` nối thêm L0018.
- Không huấn luyện, không GPU, không dùng TEST, không merge vào main. Không dùng VAL đã xem để tune.

## External knowledge evaluation — thiết kế mới 2026-11-11

- **Trạng thái:** `DESIGN_ONLY_STATIC_QA_PASS_22_OF_22`; `SCIENCE_NOT_EXECUTED`; `TEST_NOT_MATERIALIZED_NOT_SEALED`.
- [Hợp đồng câu hỏi tri thức ngoại sinh theo từng truyện](EXTERNAL_KNOWLEDGE_EVALUATION_DESIGN_20261111.md): 256 TRAIN + 64 DEV synthetic mới; 64 TEST dự kiến dùng secret riêng, chưa tạo/chưa xem.
- Ba đối chứng giữ cùng backbone: không bộ nhớ, bộ nhớ đúng, bộ nhớ sai (chỉ đổi target value); tách `ORACLE_LOOKUP` với `RETRIEVED_TOPK`, phán quyết qua answer-only NLL và paired story bootstrap.
- Bộ sinh, QA, TRAIN/DEV fixtures, manifest và QA JSON lưu trong `tools/research/vector-memory/` và `artifacts/research/vector-memory/`. Không dùng lại TinyStories VAL cũ, không huấn luyện, không inference, không GPU.
- Không ghi `lineage.md` vì hiện mới có kết quả kiểm tra tĩnh, chưa có kết quả khoa học PASS/FAIL. Nhánh tiếp tục không merge vào `main`.
