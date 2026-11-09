# TTM-Small-4M — Kế hoạch đánh giá chất lượng và thử nghiệm bật/tắt sau tương thích Ollama

**Ngày:** 2026-11-09 · **Trạng thái:** `DESIGN_ONLY_NO_NEW_EXPERIMENT` · **Nhánh:** `research/ttm-small-4m-colab-pilot-prereg-20261108`

**Mục tiêu:** trả lời ba câu hỏi riêng: (1) mô hình nhỏ *học* phân bố token có tốt hơn đối chứng không; (2) *sinh văn bản* có nhất quán, ít lặp và hữu ích ở phạm vi TinyStories không; (3) *suy luận* có ổn định, nhanh và khác nhau ra sao theo cấu hình mà không nhầm với thay đổi kiến trúc. Chỉ lập kế hoạch; không tải TEST/huấn luyện/checkpoint mới, không thực thi Ollama và không mở P07–P12.

## 1. Mốc gốc không thay thế

| Mốc | Dữ liệu đã khóa | Kết luận |
|---|---|---|
| Mô hình | P02 decoder-only, **3.749.376** tham số, 4 block, 4 heads, embedding 256, BPE 2048, context 256; checkpoint T4 step 1024 SHA256 `cb985751795c8328ad65acf7ca4c1033ce35182c1bfbdb8c38550de629cb271b` | Một seed huấn luyện thật 1.024/1.024 bước |
| VAL | NLL mô hình **3.5223388517**; bigram **3.9972314170**; cải thiện **11.880537%**, story-bootstrap 95% lợi thế [0.4581867476, 0.4940615819] | `PASS_H1_CONFIRMATORY_VAL_SCOPE` từ CPU tái tính độc lập |
| TEST | 64 truyện, NLL model **3.48359107334**, bigram **3.97360374532**, cải thiện **12.3316944%** | `PASS_TEST_HOLDOUT_DESCRIPTIVE_SCOPED`. **Không đọc/chấm TEST thêm** |
| GGUF/Ollama | GGUF F32 SHA256 `5bdc904e6c51af04a4223219f36e6bc2e687f60fd6e17dc24508f3eb7489e4e5`; Ollama 0.40.14 import PASS, 32-token generate PASS | `COMPATIBILITY_PASS`, chưa là chất lượng PASS |
| Parity số học | 8 fixture logits F32, ngưỡng max abs `0.001`; 1 PASS / **7 FAIL** | `FAIL_7_OF_8_PRESERVED` |

Điểm hiện có: một mẫu 32 token có lặp cấu trúc “The bird was very happy…”; **không đủ** thống kê để đánh giá chất lượng. Không sử dụng mẫu đó như tập prompt khóa mới để tránh chọn theo kết quả.

## 2. Đơn vị đánh giá và khóa trước khi chạy (Q0: static plan)

- Dùng **checkpoint, GGUF, tokenizer, executable, driver và mã nguồn đã xác minh**, không huấn luyện lại. Lưu `config_id`, SHA256 của checkpoint/GGUF/tokenizer, commit, seed, runtime, CPU/GPU, phiên bản và prompt SHA. Không ghi mô hình hoặc corpus thô vào Git công khai.
- Tạo **16 lời dẫn tiếng Anh mới do dự án tự viết** và ghim SHA trước lần sinh đầu: 8 bắt đầu truyện đời thường có hai nhân vật/sự vật, 4 đoạn chứa nguyên nhân–kết quả, 4 trường hợp giữ nhất quán nhân vật/đồ vật. Đây là kiểm tra *nối tiếp truyện*, không đánh giá như mô hình chat instruction-tuned. Kiểm tra trùng với câu đã dùng ở lần smoke; không dùng câu trích từ TEST hoặc chọn lại prompt sau khi xem kết quả.
- Tập TEST 64 truyện đã niêm phong và dùng một lần: **không dùng lại** cho chất lượng hay điều chỉnh tham số. Có thể trích dẫn NLL TEST gốc bất biến; một đánh giá chất lượng prompt tự viết mới mang nhãn `EXPLORATORY_QUALITY`, không biến thành TEST xác nhận mới.
- Tiền đăng ký trước phép đo: bộ prompt, mã scorer, chỉ số, các seed, quyết định giữ/bỏ, môi trường và quyền chạy một batch; QA tĩnh/độc lập *gộp vào một bước*, không tách permit cho các kiểm tra nhỏ.

## 3. Thử nghiệm chất lượng quy mô nhỏ (Q1)

| Nhóm | Cấu hình | Số đầu ra | Tác dụng |
|---|---|---:|---|
| G0 — tham chiếu | Ollama F32, greedy `temperature=0`, `num_ctx=256`, `num_predict=64` | 16 | Độ lặp/tính ổn định cơ sở |
| G1 — lấy mẫu | Giữ **cùng weights/tokenizer/prompt**, `temperature=0.8`, `top_p=0.9`, seed 101 và 102, tối đa 64 token | 32 | Độ đa dạng và mức lặp khi thay bộ lấy mẫu (sampler) |
| Tổng Q1 | 16 prompt × (1 greedy + 2 sampling) | **48** | Tối đa **3.072 token sinh**; CPU nhỏ, có cap/stop |

**Không gọi G0 vs G1 là loại trừ kiến trúc (architecture ablation):** nó là phép so sánh bộ lấy mẫu, không thay Attention/GELU/weights. Lưu raw output + options + timestamp + token count + `done_reason` trước khi chấm.

Chỉ số tính từ token **theo cùng tokenizer BPE 2048**: `distinct-2`, `distinct-3`, tỷ lệ các 3-gram lặp, tỷ lệ cùng câu/cụm lặp, số output trống, tỷ lệ truncated `done_reason=length`. Có bảng chấm thủ công **0–3** trên rubric cố định cho (a) ngữ pháp/đọc hiểu, (b) liên tục nhân vật/sự kiện, (c) quan hệ nhân quả, (d) mức lặp; ghi nguyên điểm và lý do, **không gọi một người chấm là hai giám khảo độc lập**. Báo cáo theo nhóm prompt, trung vị và khoảng biến thiên; 48 mẫu nhỏ chỉ phục vụ phân loại sơ bộ, không đủ tuyên bố chất lượng rộng.

Nếu có bộ bigram TRAIN-only để phát sinh văn bản tương đương **đã được xác minh**, có thể bổ sung đối chứng cùng tokenizer/chiều dài vào batch sau khi khóa; nếu không, báo cáo Q1 không có đối chứng sinh văn bản, không tự tạo hoặc chấm lại TEST.

## 4. Tốc độ, tài nguyên và A/B hợp lệ (Q2)

- Giữ weights, backend `CPU`, kiểu số F32, cổng riêng, cùng prompt/token-ID, `num_predict=32`, concurrency=1. Một warm-up riêng được ghi dấu (không tính vào số đo); **4 prompt cố định × 3 lượt** cho mỗi cấu hình đủ để mô tả, không phải benchmark công nghiệp.
- Dùng số đo gốc từ Ollama: `load_duration`, `prompt_eval_duration`, `eval_duration`, `prompt_eval_count`, `eval_count`, `total_duration`, `done_reason`; suy ra `eval_tokens_per_s = eval_count / (eval_duration_ns / 1e9)`. Báo cáo median/range và có/không nóng cache; không suy ra **TTFT** từ phản hồi HTTP không streaming. Nếu cần TTFT thì đo bằng streaming có định nghĩa và clock/host phù hợp.
- **A0** baseline CPU F32 cố định. **A1** KV cache bật/tắt chỉ hợp lệ nếu API PyTorch/llama.cpp đã xác minh có kiểm soát này trên **chính** checkpoint và input IDs, dùng greedy và đối chiếu logits/đầu ra; nếu chưa có toggle, ghi `NOT_FEASIBLE`, **không giả làm** tùy chọn Ollama.
- **A2** thay sampling như Q1 (mô tả đa dạng, không đo tốc độ để quy cho kiến trúc). **A3** `num_ctx=128 vs 256` chỉ trên prompt không bị cắt để so hiệu năng; test cắt prompt dài là mục riêng, không tuyên bố hiệu quả mô hình tốt hơn. **Không** tự mở quantization/backend Intel Arc/GQA/EmbeddingGemma2 hoặc sửa kiến trúc trong batch này.
- Giới hạn tài nguyên: CPU, không mở lại SYCL/P07; giữ nhật ký RAM, thời gian, không chạm dịch vụ Ollama 11434 và không chạy lại lượt V1–V5/inference-only đã tiêu thụ.

## 5. Nhánh định vị số học riêng, hữu hạn (Q3)

Kết quả đã khóa: `ffn_inp-0` là stage đầu tiên có sai khác đáng chú ý sau attention+residual; LayerNorm khuếch đại, GELU là đóng góp **có thể có**, chưa xác định toán tử gây lỗi. Không cho phép đổi ngưỡng `max_abs=0.001` để biến FAIL thành PASS.

Nếu nghiên cứu parity tiếp: đúng 8 fixture synthetic đã khóa, không TRAIN/TEST; instrument **một lần** bên trong attention: logits `QK^T`, scale/mask/softmax, `attention@V`, output projection, residual, LayerNorm và GELU; so sánh PyTorch/llama.cpp trên **cùng IDs/weights/dtype**, báo điểm bắt đầu divergence. Đây là nghiên cứu kỹ thuật tách biệt, không chặn Q1, không sửa backend trong bước lập kế hoạch. Kết quả cũ `FAIL_7_OF_8` giữ nguyên dù có chẩn đoán mới.

## 6. Tiêu chí phân xử sau một batch

- `Q1_EXECUTED=PASS` nghĩa là hoàn thành đủ 48 đầu ra, raw+SHA và scorer hợp lệ; **không** đồng nghĩa `QUALITY_PASS`. Thiếu đầu ra / sai hash / lỗi ID => `HOLD`.
- `QUALITY_DESCRIPTIVE`: báo cụ thể độ lặp, tính nhất quán, phân bố điểm 0–3; ngưỡng chất lượng nếu muốn dùng làm cổng phải được chốt **trước** khi chạy (không chọn sau khi nhìn mẫu). Không khẳng định khả năng làm theo chỉ dẫn hay ứng dụng rộng với chỉ 16 prompt.
- `GO_SMALL_NEXT_SCIENCE`: chỉ xem xét nếu có bằng chứng chất lượng tương đối rõ và bài toán giá trị; huấn luyện tiếp hoặc thay kiến trúc cần **prereg khoa học mới**, nguồn và ngân sách ngang bằng, không dựa TEST đã tiêu thụ.
- `REVISE_DATA_OR_TRAIN`: nếu NLL vẫn tốt nhưng output lặp/không liên tục, ưu tiên phân tích giới hạn vocab, độ dài context 256, dữ liệu TRAIN 2.048 truyện lặp nhiều (~8,417×) và số steps; không kết luận nguyên nhân từ sample đơn.
- `NO_BROAD_CLAIM`: hiện tại chỉ được nói mô hình học tốt hơn bigram trong pilot, nhập/suy luận Ollama PASS; logits parity FAIL và chất lượng sản phẩm chưa đủ.

## 7. Thực thi gộp, không tạo nhánh con

**Một batch sau phê duyệt kế hoạch**: đóng prompt+config+QA, chạy 48 đầu ra Q1 và bảng tốc độ CPU Q2 trong cùng workstream, lưu raw receipt bất biến và tính metrics, review. Nếu A1 không khả thi thì bỏ qua có lý do; không mở thêm một nhánh cho từng toggle. Q3 có thể hoãn nếu mục tiêu trước mắt là quyết định mô hình có đáng huấn luyện thêm. Không mở lại TEST/Colab.

**Bước tiếp theo:** `TTM_SMALL_Q1_Q2_SINGLE_BATCH_FROZEN_PROMPTS_AND_INDEPENDENT_SCORER` — chỉ khi nguồn, ngân sách và cấu hình được khóa; trong lượt này mới lập kế hoạch, không cấp runtime permit.
