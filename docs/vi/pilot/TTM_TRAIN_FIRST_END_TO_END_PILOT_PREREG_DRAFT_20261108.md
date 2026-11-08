# TTM-Small-4M — Tiền đăng ký (Preregistration) thử nghiệm tích hợp: Google Colab → Drive → Windows

> **Bản Việt hóa có đối chiếu:** [văn bản tiền đăng ký gốc](../../pilot/TTM_TRAIN_FIRST_END_TO_END_PILOT_PREREG_DRAFT_20261108.md) không bị chỉnh sửa. Tất cả trạng thái `HOLD`, kết quả PASS/FAIL và giá trị khóa trong hồ sơ phản ánh thời điểm phát hành từng mục. Tình trạng kỹ thuật T1–T3 mới hơn xem [phán quyết đóng kỹ thuật](TTM_T1_T2_T3_TECHNICAL_CLOSURE_AND_T4_SCIENCE_LOCK_REVIEW_20261108.md). Việc dịch ngôn ngữ **không cấp quyền huấn luyện T4**.

**Ngày lập:** 2026-11-08  
**Trạng thái:** `GITHUB_DESIGN_PROPOSAL_T1_T2_REVIEWED_NOT_SCIENCE_LOCKED`  
**Kho mã nguồn (Repository):** https://github.com/minhtri22/TokenToModel-Lab  
**Mốc đối chứng quản trị (Governance Baseline):** `main` merge PR #11 `1a9d8cba56564d6d36257fe95c34f2fd52c4f48a`; máy Windows cục bộ (Local) `main` và `origin/main` đã được đọc lại qua tham chiếu Git (Git Refs) đúng SHA này sau đồng bộ V2.  
**Phạm vi:** Nhánh đề xuất riêng; không thay P00–P12, không mở P08/P09/P10, không sửa lịch sử `lineage.md`, không huấn luyện hoặc tải tập ngữ liệu (Corpus) trong bước thiết kế.

**Phụ lục thẩm định tổng hợp được ưu tiên diễn giải:** [TTM_SMALL4M_T1_T2_INTEGRATED_SOURCE_TOKENIZER_EXPORT_REVIEW_20261108.md](TTM_SMALL4M_T1_T2_INTEGRATED_SOURCE_TOKENIZER_EXPORT_REVIEW_20261108.md). Tệp này là bản tiền đăng ký nháp; điều kiện chưa được khóa và giá trị thiết kế T1/T2 được diễn giải bởi phụ lục trên, không xem là thực nghiệm PASS.

**Quyết định bổ sung gần nhất (08/11/2026):** [Đóng kiểm thử native F32 của T2 và điều chỉnh F16](TTM_T2_F32_NATIVE_CLOSURE_AND_F16_GATE_AMENDMENT_20261108.md) có hiệu lực diễn giải ưu tiên trong phạm vi T2: bộ xuất GGUF F32 trên TRAIN tổng hợp (Synthetic TRAIN-only) PASS tokenizer 20/20 và logits 10/10, F16 vẫn bị chặn (BLOCKED) nhưng chuyển sang tuyến tối ưu tùy chọn; T1 nguồn thật, T3 Colab/Drive và khóa khoa học (Science Lock) vẫn tạm giữ (HOLD). Không biến PASS kỹ thuật này thành PASS khoa học.

**CẬP NHẬT KIỂM ĐỊNH KỸ THUẬT 2026-11-08 (ưu tiên hơn bản ghi trạng thái lịch sử (Historical Snapshot)):** [Độc lập đóng T1–T3 và tổng hợp các cổng khoa học T4 còn mở](TTM_T1_T2_T3_TECHNICAL_CLOSURE_AND_T4_SCIENCE_LOCK_REVIEW_20261108.md). T1 nguồn, chia tập (Split) và bộ tách token (Tokenizer) thật **PASS có giới hạn trong tập thử nghiệm giới hạn (Pilot)**, T2 GGUF F32/llama.cpp **PASS**, T3 GPU Tesla T4 + Drive lưu checkpoint và phục hồi (Resume) **PASS đọc lại độc lập**; lỗi RNG của lượt Colab đầu vẫn lưu STOP, F16 vẫn bị chặn (BLOCKED) tùy chọn. Mọi dòng `T1_NOT_EXECUTED`/`T3_NOT_EXECUTED` còn xuất hiện ở các bảng bên dưới là **snapshot lúc biên soạn**, không phải trạng thái hiện tại. **`SCIENCE_LOCK=HOLD`** cho đến khi chốt quyền dữ liệu, phạm vi 2048/256/64, baseline/ngưỡng H1, ngân sách 1024×4096, microbatch/precision qua capacity smoke, T4 runner và thẩm định độc lập tổng hợp. Chưa huấn luyện T4.

## 1. Câu hỏi và giả thuyết

**Câu hỏi chính:** Transformer P02 do TTM tự xây có thể học dự đoán văn bản truyện tiếng Anh đơn giản ngoài tập TRAIN, vượt đối chứng thống kê (mốc đối chứng (Baseline)) trong cùng quy tắc token hóa, và xuất sang llama.cpp/Ollama mà không thay đổi có ý nghĩa đầu ra hay không?

- H1 (học): TTM-Small-4M có NLL (negative log likelihood) trên tập VALIDATION thấp hơn tối thiểu 5% so với đối chứng bigram làm trơn Add-α đã khóa và khoảng tin cậy bootstrap 95% cho chênh lệch NLL không vượt quá 0. Không lấy TRAIN loss làm chứng minh chính.
- H2 (resume): khôi phục (resume) tại cùng môi trường, thiết bị, phiên bản và seed cho chuỗi tham số, loss và cursor bằng thử nghiệm ngang bằng được khóa; sai số số học theo ngưỡng nêu bên dưới.
- H3 (export): checkpoint chưa train lẫn checkpoint đã train đều đi được qua PyTorch → GGUF → llama.cpp và Ollama; đối chiếu IDs, logits và output trên cùng token IDs.

**Quy tắc:** Nếu T2 export không đạt, không dùng GPU Colab để chạy train dài; ghi `EXPORT_BLOCKED` và sửa tương thích kỹ thuật (Compatibility) trong phạm vi kỹ thuật (không sửa dữ liệu khoa học). Nếu mô hình học kém sau ngân sách đã khóa, ghi FAIL khoa học chứ không tự tăng ngân sách (Budget) để đổi nhãn kết quả.

## 2. Nguồn dữ liệu và quyền

- Nguồn đã ghim: [roneneldan/TinyStories](https://huggingface.co/datasets/roneneldan/TinyStories/tree/f54c09fd23315a6f9c86f9dc80f725de7d8f9c64) ở commit **`f54c09fd23315a6f9c86f9dc80f725de7d8f9c64`**, tiếng Anh, giấy phép (License) **`cdla-sharing-1.0`** theo thẻ dữ liệu (Dataset Card) (xác minh ngày 2026-11-08). Quyền Use/Computational Use có điều kiện theo https://cdla.dev/sharing-1-0/ ; cần thực hiện nghĩa vụ khi công bố dữ liệu (Publish Data) và rà soát (Review) riêng trước phát hành mô hình (Model). Nghiên cứu gốc https://arxiv.org/abs/2305.07759.
- Ưu tiên dùng hai file gốc `TinyStories-train.txt` và `TinyStories-valid.txt`, **không mặc nhiên thay bằng TinyStoriesV2 hay 7.62 GB dữ liệu**. Metadata chủ repository đã được rà soát; SHA commit 40 ký tự của Hugging Face, SHA-256 cho từng tệp đã trích và hồ sơ phạm vi quyền sử dụng cần điền trước khi tải/huấn luyện.
- Quyền nguồn WP30 P01 chỉ dùng cho BPE E0; không mang vào corpus GPT pilot, không huấn luyện tokenizer tiếng Anh từ WP30.
- Tách theo **câu chuyện nguyên bản**, không tách theo từng cửa sổ token; xác định bộ phân đoạn truyện (Story-boundary Parser) và chuẩn hóa dạng biểu diễn (Canonicalization) trước khi đóng băng dataset. lọc trùng hoàn toàn (Exact Deduplication) bằng SHA-256 giữa TRAIN/VAL/TEST và kiểm tra trùng gần (Near-duplicate) theo cùng thuật toán được khóa; không dùng TEST để chọn mô hình, tokenizer hay siêu tham số.
- Quy tắc nguồn/split được chi tiết hóa tại [T1/T2 review](TTM_SMALL4M_T1_T2_INTEGRATED_SOURCE_TOKENIZER_EXPORT_REVIEW_20261108.md): TRAIN chỉ lấy từ tệp gốc huấn luyện (Train) theo hạt giống băm truyện (Story-hash Seed) `20261108`; VAL/TEST (~80/20) lấy từ file gốc valid sau dedup, hash theo story, không học bộ tách token (Tokenizer)/đối chứng (Baseline) từ chúng. Parser separator, raw file bytes SHA, trùng gần (Near-duplicate) audit và manifest thực tế vẫn HOLD trước science. TEST niêm phong, một lần dùng cuối.
- License card không tự động đồng nghĩa với quyền ứng dụng thương mại hoặc tuân thủ toàn bộ yêu cầu phân phối; hoàn tất rà soát ghi nguồn (Attribution), thông tin định danh cá nhân (PII), đầu ra mô hình (Model Output) và vận hành trước mọi phát hành.

## 3. Bộ tách token (Tokenizer)

- Mới hoàn toàn từ TRAIN (không dùng VAL/TEST), byte-level BPE, vốn từ **2.048 ID**, có xử lý bytes không thuộc ASCII, encode/decode round-trip và determinism.
- Dự kiến phân bổ 256 byte nền + 1 token EOS + 1.791 phép ghép BPE = 2.048 IDs (chi tiết special-token sẽ được khóa trước khi implement). Đối chiếu encode/decode với biểu diễn GGUF; các quy tắc tiền xử lý khoảng trắng, xuống dòng, byte-unicode, special IDs bắt buộc giống nhau.
- P01 tokenizer Wikipedia tiếng Việt được giữ bất biến như bằng chứng lịch sử, không tái sử dụng cho thí nghiệm tiếng Anh.
- Tokenizer chỉ được huấn luyện **một lần** từ TRAIN đã khóa; sau đó ghim từ vựng (Vocabulary), quy tắc hợp nhất (Merges), chuẩn hóa (Normalization) và SHA nguồn và giữ nguyên cho tất cả đối chứng.

## 4. Mô hình và mã nguồn

Dùng đúng lõi `src/p02/transformer_core.py` từ `main`, blob `9762343e06cf800b50574c2871ae1ed58537fb18`. Cấu hình ứng viên: `vocab_size=2048`, `max_seq_len=256`, `n_embd=256`, `n_layer=4`, `n_head=4`, `norm_type=layernorm`, positional embedding học được, weight tying. **Số tham số theo mã đã đọc: 3.749.376 (~3,75M)**, phải kiểm đếm bằng runtime trước khi khóa.

Mốc kỹ thuật P02 tham chiếu giữ nguyên: 2 lớp/64 chiều/64 context. Có thể mở 12M sau pilot, **không thuộc pilot này**.

Hợp đồng hiện hành `src/p03/train_loop.py` chỉ chạy *cùng một batch cố định* và `src/p04/eval_checkpoints.py` chỉ smoke checkpoint/đánh giá token tổng hợp. Pilot cần bổ sung bộ đọc dữ liệu đã được phép, multi-batch sampler, val inference, optimizer/scheduler state và resume. Không sửa hồi tố chứng cứ P03/P04.

## 5. Các mốc hữu hạn T1–T7

| Mốc | Thực hiện | Điều kiện kết luận |
|---|---|---|
| T1 — Nguồn và bộ tách token (Source/Tokenizer) | Ghim revision 40-char, quyền dữ liệu, snapshot, split, leakage và tokenizer TRAIN-only | PASS nguồn và no-leakage; nếu không thì HOLD không train |
| T2 — Thử xuất mô hình chưa huấn luyện (Export Dry-run) | Mô hình **chưa huấn luyện**: ánh xạ tensor và bộ tách token (Tensor/Tokenizer Mapping) P02 → GPT2/GGUF, chạy llama.cpp CPU | 100% token IDs trên bộ tình huống kiểm thử đã khóa (Frozen Fixtures), top-1 logits trùng trên bộ prompt khóa và sai số logits trong ngưỡng đã đăng ký; nếu FAIL thì STOP trước huấn luyện (Training) |
| T3 — Colab/Drive | Script/notebook versioned; làm nóng (Warmup) benchmark **synthetic**, save/restore model+optimizer+scheduler+RNG+sampler; READY-last | Interrupted/resumed parity PASS trên cùng GPU/dtype/seed và checkpoint hoàn chỉnh; không dùng corpus khoa học trong T3 |
| T4 — Huấn luyện mô hình nhỏ (Small-model Training) | Huấn luyện mô hình 4M qua nhiều lô (Batches) trên TRAIN đã khóa, VAL định kỳ, 1 seed cho pilot, baseline unigram/bigram | H1 PASS hoặc FAIL đúng ngân sách; lưu đường cong kiểm định VAL (Validation Curve) và thang chấm mẫu (Sample Rubric) đã đăng ký |
| T5 — Windows deployment | Lưu SHA trên Drive, tải checkpoint về Windows, GGUF F32 (bắt buộc), llama.cpp/Ollama; F16 tùy chọn sau kiểm thử tương thích | Cùng tokenizer/tensors, logits và seeded greedy generation vượt ngưỡng định trước |
| T6 — A/B | No-cache/Dense/Paged, PyTorch/llama.cpp, F16/Q8/Q4 (nếu đường dẫn có) | Cùng checkpoint/prompt/device, log sai số, TTFT/TPOT, tokens/s, RAM, nhiều lần lặp; không tuyên bố cải thiện khi chưa đo |
| T7 — Revisit P07 | Chỉ đánh giá kế hoạch tối ưu GPU sau pilot | P07 vẫn có cổng numerical parity và benchmark độc lập; không tự mở P08 |

## 6. Điều kiện đo và ngân sách

- T3 có thể dùng các batch tổng hợp kỹ thuật để đo tốc độ, thống kê RAM/VRAM và độ bền Drive; **không** được chọn hyperparameter hoặc kiểm thử trên TEST.
- **Ngân sách thiết kế đề nghị:** `1024` bước bộ tối ưu (Optimizer Steps) x `4096` token mục tiêu mỗi bước (Target Tokens/Step) = **4.194.304 TRAIN tokens**, `1` seed (`20261108`), AdamW tốc độ học cực đại (Peak Learning Rate) `3e-4`, làm nóng (Warmup) `32`, cosine đến `3e-5`, VAL mỗi `128` steps, điểm lưu mô hình (Checkpoint) ở bước `1024` là primary. Chọn lô nhỏ (Microbatch) và độ chính xác số (Precision) qua kiểm tra nhanh Colab không dùng dữ liệu khoa học (Zero-science Smoke) rồi khóa **trước TRAIN**; tối đa `90` phút GPU cho lượt huấn luyện khoa học (Science Run), nếu không đáp ứng thì HOLD thay vì tự giảm/tăng tokens. Các giá trị bổ sung ở [T1/T2 review](TTM_SMALL4M_T1_T2_INTEGRATED_SOURCE_TOKENIZER_EXPORT_REVIEW_20261108.md), chưa có quyền run.
- Đối chứng: uniform, unigram và smoothed bigram cùng tokenizer/partition; baseline được fit trên TRAIN, không trên VAL/TEST. Chỉ số chính (Metric) là mất mát log âm mỗi token (Negative Log-likelihood, NLL) (không so PPL giữa tokenizers khác nhau); độ bối rối mô hình (Perplexity, PPL)=exp(NLL) chỉ báo phụ. Sử dụng tái lấy mẫu (Bootstrap) theo từng **truyện** 1.000 lượt với seed khóa để tránh coi token cùng truyện độc lập; độ chênh lệch chính (Primary Gap) là bigram NLL - model NLL.
- Mẫu sinh: bộ prompt cố định từ trước và không lấy nguyên văn TEST làm prompt thử nghiệm; đầu ra được chấm ẩn nhãn (blind) theo cấu trúc truyện, mạch ý và lặp, không dùng cảm nhận đơn lẻ để thay primary metric.
- Khi chi phí/độ chính xác không đạt: kết luận `EXPERIMENT_FAIL` hoặc `INCONCLUSIVE`, không tự tăng kích thước/seed/tokens để tìm PASS.

## 7. Điểm lưu mô hình (Checkpoint) và phục hồi (Resume)

- GPU Colab làm việc trên `/content` (đĩa phiên); Google Drive chỉ nhận checkpoint hoàn chỉnh và manifest; không đọc từng batch trực tiếp từ Drive. Colab không bảo đảm GPU/phiên, nên phải có resume (theo tài liệu https://research.google.com/colaboratory/faq.html).
- Tệp checkpoint: model state, optimizer state, scheduler state, global step, token-count, train config, tokenizer manifest, DATA manifest, sampler permutation/cursor, Python/NumPy/PyTorch RNG & CUDA RNG nếu dùng, seed, env lock, Git SHA, exact tensor shape/dtype và SHA-256.
- Ghi checkpoint vào thư mục tạm trên local session → kiểm SHA → copy lên thư mục phiên bản hóa trên Drive → kiểm SHA Drive → ghi `READY.json` **cuối cùng**. Không giả định thao tác rename trên Drive mounted là atomic. Checkpoint READY chỉ hợp lệ nếu tất cả thành phần đọc lại và hash khớp. Không sửa checkpoint đã READY; bỏ qua phần chưa READY khi resume.
- Test resume parity kỹ thuật: 20 bước bộ tối ưu (Optimizer Steps) liên tục so với 10 + save/reload + 10 cùng environment/GPU/dtype/seed, so final weights/loss/sampler cursor; dự kiến `FP32 CPU max |Δweight|<=1e-6`, cùng-GPU precision phù hợp chỉ khóa ngưỡng sau khi thử zero-science fixtures. Không cam kết bit-identical giữa GPU loại khác nhau.
- Đường Drive ứng viên: `MyDrive/TTM/ttm-small-pilot/<run-id>/` (chưa tạo); xác thực tài khoản Drive sẽ do người dùng cấp khi chạy notebook.

## 8. Định dạng mô hình GGUF và suy luận bằng llama.cpp/Ollama

- P02 là GPT-2-like nhưng không giống checkpoint GPT-2 Hugging Face: tên tensor tự tạo (`tok`, `pos`, `blocks.*`, `attn.qkv`, `mlp`, ...), QKV projection là `nn.Linear`, LayerNorm eps=1e-5, GELU, embedding/head tied. Cần mapping có kiểm tra chiều và thứ tự transpose, special token, pretokenization. Không đổi `.pt` thành `.gguf` để coi là conversion.
- Mã `ggml-org/llama.cpp` đã ghim tại commit `372dc5ca157276beb6c67b2e92477e8d662e964a` (GPT2 bộ thực thi (Backend)/bộ chuyển đổi (Converter) được thấy trong mã nguồn (Source)); bộ xuất mô hình (Exporter) còn phải chứng minh số học T2, không lấy existence làm PASS. T2 CPU F32 là cổng kỹ thuật bắt buộc: 20/20 mã token (Token IDs) và 10/10 vectơ giá trị dự đoán trước chuẩn hóa (Logits) trên bộ fixture mới đã khóa (ngưỡng F32 `max_abs_logit_diff <= 1e-3`, 0 top1 mismatch) đã PASS khi dùng dữ liệu tổng hợp. F16 `<= 2e-2` là tuyến tối ưu *tùy chọn*, hiện BLOCKED theo V4/V5B; không bắt buộc để bắt đầu khoa học nếu các cổng T1/T3 độc lập PASS. Chỉ checkpoint **đã huấn luyện** mới được đánh giá thật ở T5.
- Sau khi export đạt mới so sánh Ollama `Modelfile FROM ./model.gguf`; Ollama không phải bằng chứng đúng nếu llama.cpp parity chưa PASS. Đối chiếu trên cùng dtype và quan sát số học thay vì kỳ vọng chuỗi sinh luôn trùng ở điểm near-tie.
- Nếu GPT-2/GGUF bộ thực thi (Backend) hiện tại không hỗ trợ byte-BPE mới hoặc một phép tính nào đó, ghi `EXPORT_COMPATIBILITY_GAP`, không thay kiến trúc khoa học đã duyệt hoặc train lại để khắc phục.

## 9. Ma trận so sánh bật/tắt cấu hình (A/B)

| Phép đối chiếu | Bất biến | Báo cáo |
|---|---|---|
| No KV / Dense KV / Paged KV | checkpoint, tokens, dtype, bộ thực thi (Backend), device | logits parity, TTFT, TPOT, throughput, RAM/VRAM |
| PyTorch vs llama.cpp | weights, tokenizer, prompts | logit error, token ID parity, timing |
| GGUF F16 vs Q8/Q4 (tùy chọn, khi bộ thực thi (Backend) hỗ trợ) | checkpoint đã huấn luyện, tokenizer đã khóa | VAL NLL degradation, size, timing, memory; BLOCKED không cản đánh giá primary bằng F32 |
| LayerNorm vs RMSNorm | cùng TRAIN, seed, budget và model size | cần **train riêng**; để ngoài critical path 4M |
| FP32 vs mixed precision | cùng dữ liệu/schedule/seed và budget, 2 lần train | sau pilot; stability, accuracy, speed |

## 10. Hiện vật bàn giao và điều kiện đóng

- `config/pilot_small_4m.yaml`, `data_manifest.json`, `tokenizer_manifest.json`, `eval_protocol.md`, `export_mapping.md`, `colab_train.ipynb`, `checkpoint_schema.json`, `resume_parity_report.json`, `model_card.md` là **đầu ra dự kiến**, hiện chưa tồn tại/chưa được tạo trong bước design.
- Bước design chỉ được đóng khi: nguồn và quyền được kiểm tra, nguồn sha/revision/splits khóa được, format tokenizer và export contract đạt thiết kế, các ngưỡng và budget quyết định trước TRAIN, đường Colab/Drive ổn định. Mọi kết quả thí nghiệm sau này ghi cả PASS và FAIL khoa học vào `lineage.md` append-only; sửa hạ tầng/QA kỹ thuật vào log khác.
- **Không yêu cầu một permit riêng cho mỗi phép kiểm nhỏ.** Chỉ có cổng quyền nguồn/dữ liệu, tiền đăng ký khoa học, tài nguyên và one-shot science thực sự.

## 11. Trạng thái theo thời điểm lập tài liệu

`LOCAL_MAIN_SYNC=PASS_INDEPENDENT_READBACK` · `PILOT_PREREG_DRAFT=SCIENCE_NOT_LOCKED` · `T2_F32_SYNTHETIC_GGUF=PASS_TECHNICAL` · `T2_F16=BLOCKED_OPTIONAL` · `T1_REAL_DATA=NOT_EXECUTED` · `T3_COLAB_RESUME=NOT_EXECUTED` · `T4_T7=NOT_EXECUTED` · `COLAB_GPU=NOT_USED` · `P07=PAUSED_PRESERVE`.

**Bước thực hiện tiếp theo:** `TTM_SMALL4M_T1_T3_TINYSTORIES_SOURCE_SPLIT_AND_COLAB_DRIVE_RESUME_INTEGRATED_PREFLIGHT`. Chỉ sau khi kiểm định dữ liệu TinyStories thực, tokenizer TRAIN-only thật và T3 Colab/Drive synthetic resume PASS mới đánh giá science lock và T4; không huấn luyện trong nhánh tài liệu này.

## 12. Những trường tiền đăng ký phải khóa trước TRAIN

Những thông tin sau **chưa có bằng chứng khóa**, nên tài liệu này là bản nháp thiết kế chứ không phải quyền chạy khoa học:

| Cổng | Bằng chứng phải khóa | Trạng thái |
|---|---|---|
| SRC | Phiên bản bộ dữ liệu (Dataset Revision) 40-char SHA, SHA-256 byte nguồn huấn luyện/kiểm định (Train/Valid), giấy phép CDLA Sharing 1.0 và phạm vi huấn luyện (Training), phân phối lại (Redistribution) và ghi nguồn (Attribution), PII | `HOLD_SOURCE_PIN_AND_RIGHTS` |
| SPLIT | Story-boundary, dedup exact/trùng gần (Near-duplicate), số mẫu và SHA manifest TRAIN/VAL/TEST; niêm phong TEST | `HOLD_NOT_MATERIALIZED` |
| TOK | Byte BPE 2048, merges, EOS/special IDs, round-trip; tokenizer chỉ học TRAIN | `DESIGN_PROPOSED` |
| TRAIN | Ngân sách tokens, effective batch, LR/optimizer/scheduler, seeds, mixed-precision/hardware | `HOLD_SYNTHETIC_CAPACITY_TEST` |
| BASE | Uniform/unigram/Add-alpha bigram và công thức NLL; bootstrap theo truyện; chênh NLL tối thiểu 5% | `DESIGN_PROPOSED` |
| RESUME | Schema + SHA READY, optimizer/scheduler/cursor/RNG; parity 20 vs 10+10 cùng runtime | `DESIGN_PROPOSED` |
| EXPORT | T2 F32 synthetic đã PASS native; sau khi khóa TRAIN-only tokenizer dữ liệu thật phải kiểm parity lại trước T4 | `F32_SYNTHETIC_PASS_REAL_TOKENIZER_PENDING` |
| RESULTS | VAL dùng chọn model trước TEST; TEST một lượt, kết luận PASS/FAIL theo tiêu chí gốc | `DESIGN_PROPOSED` |

Thứ tự: SRC/SPLIT/TOK kiểm định trước TRAIN; GGUF dry-run T2 và resume synthetic T3 phải PASS trước train dài. Không mặc định máy Colab cấp loại GPU cố định. Mọi QA kỹ thuật không cần permit riêng, nhưng cổng nguồn/tiền đăng ký khoa học vẫn bắt buộc.

**Quản trị Git (Git Governance):** Mốc đối chứng (Baseline) `main` đã đồng bộ local đến `1a9d8cba56564d6d36257fe95c34f2fd52c4f48a`; `lineage.md` bất biến, P07 giữ PAUSED, không dùng tập ngữ liệu (Corpus) WP30 để huấn luyện GPT. Không thực hiện tải xuống (Download), huấn luyện (Train), Colab, TEST hoặc xuất GGUF (GGUF Export) trong PR nháp.
