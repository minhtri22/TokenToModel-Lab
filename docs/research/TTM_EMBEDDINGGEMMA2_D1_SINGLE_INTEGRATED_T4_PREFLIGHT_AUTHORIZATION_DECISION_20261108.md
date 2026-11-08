# TTM — D1 EmbeddingGemma 2: Quyết định cấp quyền tài nguyên cho một lượt tiền kiểm T4

**Mã công việc:** `TTM_EMBEDDINGGEMMA2_D1_SINGLE_INTEGRATED_T4_PREFLIGHT_AUTHORIZATION_DECISION`  
**Ngày:** 2026-11-08  
**Phán quyết duy nhất:** **`HOLD_RESOURCE_AUTHORIZATION_PENDING_OWNER_APPROVAL`**  
**Trạng thái kỹ thuật:** `SCOPED_PREREG_LOCK_READY` · `INTEGRATED_PREFLIGHT_PLAN_READY` · `PREFLIGHT_NOT_EXECUTED`  
**Tuyệt đối không suy diễn:** `OWNER_DOWNLOAD_PERMISSION=NOT_GRANTED`; `OWNER_COLAB_COMPUTE_PERMISSION=NOT_GRANTED`; `D1_D4=NOT_AUTHORIZED`; `SCIENCE_RUNS=0`.  
**Repository:** https://github.com/minhtri22/TokenToModel-Lab  
**Nhánh nghiên cứu:** `research/ttm-gemini-embedding2-gqa-pagedattention-feasibility-design-20261108` (chỉ là tên lịch sử; **đối tượng đúng** `google/embeddinggemma-2`).  
**Nguồn G1–G4 giữ nguyên:** `docs/research/TTM_EMBEDDINGGEMMA2_D1_FOUR_REAL_RECEIPTS_SINGLE_LOCK_DECISION_20261108.md` Git blob `26859d8143aa55da227be5abe3fa3cd83ae16744`.  
**HEAD nghiên cứu trước quyết định:** `17134767edea9fd075fe54985be2c847492739ab`. **Main HEAD khi đối chiếu:** `1a9d8cba56564d6d36257fe95c34f2fd52c4f48a`.

> **Ý nghĩa:** Chủ dự án yêu cầu *ra quyết định cấp quyền tài nguyên*, nêu rõ "chỉ khi được cho phép" mới tải mô hình/dataset và dùng GPU. Đây **không phải** sự chấp thuận chi trả, tải trọng số, mount Drive, nạp dữ liệu lên Colab hoặc chạy GPU. Bản thân một biên bản do trợ lý tạo không thay thế quyết định của chủ tài nguyên. Do đó chỉ được ghi một `HOLD` về quyền **thực thi**, không mở lại thiết kế khoa học đã khóa, không thêm các micro-permit riêng.

## 1. Đối chiếu trạng thái TTM-Small: bằng chứng mới và thứ tự ưu tiên

**Đọc GitHub pilot `research/ttm-small-4m-colab-pilot-prereg-20261108` ngày 2026-11-08:**
- T4 khoa học **ĐÃ THỰC HIỆN THẬT**: 1.024 optimizer steps trên Colab Tesla T4, H1 VAL independently reproduced `PASS_H1_CONFIRMATORY_VAL_SCOPE`. Model 3.749.376 tham số và bigram VAL NLL lần lượt 3.52233885 và 3.99723142, lợi thế 11,880537%.
- T4 TEST 64 truyện đã tiêu thụ **một lượt**: `PASS_TEST_HOLDOUT_DESCRIPTIVE_SCOPED`. Không chạy lại TEST.
- T5 GGUF F32 exporter tự kiểm tra 52/52 tensors đúng, nhưng **trained llama.cpp full-logits parity FAIL ngưỡng frozen 0.001**, 7/8 fixtures có worst abs > threshold, worst 0.003362179; tokenizer V5B 9/9 PASS; Ollama chưa hoàn tất. Đường xử lý chính hiện tại là chẩn đoán sai lệch số học T5, **không** yêu cầu huấn luyện lại T4.
- Bằng chứng: `docs/pilot/TTM_T4_A2_REAL_SCIENCE_H1_FORMAL_ADJUDICATION_20261108.md`, `docs/pilot/TTM_T4_TEST_64_SCIENCE_ADJUDICATION_AND_T5_TRAINED_F32_EXPORT_20261108.md`, `docs/pilot/TTM_T5_V5B_UTF8_NUMERIC_FAILURE_ADJUDICATION_20261108.md` trên PR #12.
- PR #12 vẫn **OPEN / DRAFT**; `main` unchanged. Tài liệu/commit pilot có thể tiếp tục thay đổi bởi công việc khác; kiểm lại đúng lúc dùng tài nguyên.

**Giới hạn quan sát:** Github xác minh trạng thái tài liệu, **không** xác minh Colab hiện đang rảnh, GPU nào sẵn có, dư quota, RAM/VRAM thực, hoặc chủ dự án có đang chạy phiên T5 song song. Không claim `COLAB_FREE=PASS`. TTM-Small T5 tiếp tục được ưu tiên về thiết bị, Drive, quota, đường dẫn và thời gian.

## 2. Điều kiện được chấp nhận về mặt kỹ thuật — không phải giấy phép chạy

`SOURCE_AND_PREREG_LOCK_READY_SCOPED=YES` đã ghi ở hồ sơ G1–G4. **Không** cần phát hành lại, làm mới hoặc mở rộng G1–G4 trong bước này.

Các nguồn đã ghim:
| Nguồn | Repository / revision | Dùng ở preflight |
|---|---|---|
| Encoder | `google/embeddinggemma-2@f9972ac22e696a105c482202646979e33e4b5a1e` | **Text-only, FP32**, không dùng float16 |
| Frozen Qwen | `Qwen/Qwen2.5-0.5B-Instruct@7ae557604adf67be50417f59c2c2f167def9a775` | Chỉ kiểm nạp, tokenizer/template/teacher-forcing trên fixture giả lập |
| Corpus | `rajpurkar/squad@7b6d24c440a36b6815f21b70d25016731768db1f` | **Chỉ validation**; file `plain_text/validation-00000-of-00001.parquet` |
| Corpus remote hash | `8c6646d36bd5a95061e076788cf3161d11f6f3e7d625dac7a83bbed0a49f69f7` | Dùng để so downloaded-file SHA256; metadata nguồn, chưa tự kiểm byte |
| R_gold frozen fixture | `docs/research/fixtures/TTM_EMBEDDINGGEMMA2_D1_R_GOLD_60_GROUPS_LOCK_CANDIDATE_20261108.jsonl` | **Chỉ xác minh tồn tại/hash, không sử dụng câu hỏi khoa học** |
| R_gold SHA256 | `0215719de94f86a4f2b7a48959ca81343014c127e74799f737901a57b33f341a` | Đảm bảo namespace/fixture không thay đổi |
| R1–R3 contract | `docs/research/fixtures/TTM_EMBEDDINGGEMMA2_D1_SQUAD_RETRIEVAL_AND_R_GOLD_SOURCE_LOCK_CANDIDATE_20261108.json` blob `52d92e1c054afcf85ec5334e275f9b75ec084e83` | Dẫn thuật toán tạo index/group và scoring; **không chấm dữ liệu khoa học** |

Nguồn được mô tả bằng model card Apache-2.0 cho hai model; SQuAD CC BY-SA 4.0; giữ license/attribution/source snapshots và tuyệt đối không ghi nội dung SQuAD hoặc dữ liệu riêng vào repo công khai. EmbeddingGemma2 model card: https://ai.google.dev/gemma/docs/embeddinggemma/model_card_2 . Colab FAQ: https://research.google.com/colaboratory/faq.html . Free Colab có GPU nhưng loại GPU/giới hạn tài nguyên không được bảo đảm; không tự giả định T4 hoặc free quota sẵn.

## 3. Đề xuất một phong bì tài nguyên duy nhất để chủ dự án duyệt (không phải budget đã được cấp)

**Phạm vi `ONE_TECHNICAL_PREFLIGHT_ONLY`:**
1. Một lần quan sát tài nguyên Colab trước download: GPU identity, RAM/VRAM/disk available, Torch/CUDA/dtype support, status TTM-Small resource, free/premium mode. Nếu không có T4 hoặc ảnh hưởng pilot đang chạy thì **STOP_NO_SIDE_EFFECT**.
2. Chỉ sau owner approval: tải **đúng** Google embedding+Qwen pinned revisions và **chỉ SQuAD validation Parquet**, kiểm SHA-256 và phạm vi license. Tải và cache model có thể cần > trọng số text-only; phải đo dung lượng trước khi download. **Không tải Pythia, SQuAD train, TinyStories, Gemini API, paid endpoints, hay multimodal data nếu không cần.**
3. Dùng text-only `config_kwargs={"vision_config":null,"audio_config":null}` và `torch.float32`. FP16 **cấm** cho EmbeddingGemma 2 (có nguy cơ NaN/sai âm thầm); BF16 không mặc định trên T4. Kiểm finite `[B,768]`, L2 norm, idempotent encoding, task prefix và truncation trên **zero-science synthetic fixtures**.
4. Nạp frozen Qwen riêng hoặc tuần tự sau khi encoder được giải phóng; kiểm template role/special tokens, causal logit shift/mask, tokenizer answer-boundary, empty-document behavior trên **synthetic dummy tokens** không có R_gold hoặc nhãn SQuAD.
5. Chỉ dùng dữ liệu SQuAD để xác minh định dạng/schema, byte digest, tạo **manifest group/index/query IDs bằng thuật toán nguồn đã khóa**; không chấm Hit@k, MRR, NLL, Exact Match, hoặc nhìn TEST/answer để điều chỉnh selection. No adapter training.
6. Đo peak GPU VRAM, RAM, disk/Drive size, latency/load; log full software versions (Python, Torch, CUDA, Transformers, SentenceTransformers, tokenizers, safetensors), model weight/tokenizer/config SHA256, decision STOP reason nếu lỗi. Không tự chạy lại khoa học nếu một bước FAIL; không gia hạn tự động.

**Phương án bảo toàn tài nguyên:** mọi file/cache/receipt trong namespace riêng EmbeddingGemma 2, không dùng đường dẫn TTM-Small checkpoint/Drive/progress; mức chi tiêu API/compute trả phí: **$0** và **không được tự kích hoạt gói trả phí**. Ưu tiên lấy snapshot/size thông tin trước khi tiêu thụ GPU. Bắt buộc kiểm free memory trước mỗi model load, serial encoder/Qwen. Nếu thiếu quota/disk/GPU cần thiết, STOP, không mượn tài nguyên của TTM-Small.

**Budget proposal only (not authorized):** `max GPU session 30 minutes`, `max new model/dataset download 5 GiB`, `max persistent storage 8 GiB`, `Colab GPU requirement Tesla T4 only`, `API paid spend $0`. Đây là **giới hạn đề xuất** để owner có thể chấp nhận/chỉnh một lần; chưa thể khẳng định preflight thực tế nằm trong giới hạn, và phải dừng nếu ước tính không đủ. Không ấn định lại sau failure nếu không có quyết định mới của owner.

**An toàn/công bằng:** preflight KHÔNG chạy R_gold, R1/R2/R3, Adapter, TRAIN/VAL/TEST mô hình khoa học. `lineage.md` không ghi QA kỹ thuật. Nếu chưa có owner approval về dữ liệu trên Colab, chỉ giữ read-only documentation. Khi owner cho phép, uploading/processing SQuAD trên Google Colab là xử lý dữ liệu bằng môi trường bên thứ ba, phải phù hợp điều kiện quyền dữ liệu đã đọc.

## 4. Một phán quyết tài nguyên (không mở lại G1–G4)

**Decision `HOLD_RESOURCE_AUTHORIZATION_PENDING_OWNER_APPROVAL`:**
- **Source/prereg:** `LOCK_READY=YES_SCOPED_PREREG_ONLY`.
- **Technical scope:** `PREFLIGHT_SCOPE_READY=YES`.
- **Live GPU availability:** `NOT_VERIFIED`.
- **Owner permission to download and use Colab/Drive on EmbeddingGemma branch:** `NOT_PRESENT_IN_USER_REQUEST`.
- **Authorization granted:** `NO`. No load/download/Colab run.
- **Scientific D1:** `NOT_AUTHORIZED` independently of any technical success.

**Single subsequent owner action:** Approve **one** integrated preflight, including pinned model+SQuAD validation downloads and bounded Colab T4 resources in the above envelope, with priority to TTM-Small and $0 paid spend. Without explicit approval, remain HOLD; **no new micro-review, micro-permits, or prereg rewrite**.

**Next step:** `TTM_EMBEDDINGGEMMA2_D1_T4_PREFLIGHT_SINGLE_OWNER_APPROVAL_THEN_RUN_ONCE`. Before any execution, check actual resource and TTM-Small priority; if blocked, stop and preserve receipts. Only after technical PASS does a **separate science decision** become eligible. This document is a *single decision* on resources, not authorization from the user's account or a new research protocol.

**Final states:** `SCOPED_PREREG_LOCK_READY=YES` · `RESOURCE_AUTHORIZATION=HOLD_OWNER_APPROVAL` · `PREFLIGHT=NOT_EXECUTED` · `R_GOLD=NOT_EXECUTED` · `D1_D4=NOT_AUTHORIZED` · `TTM_SMALL_T5=PRIORITY_FIRST` · `MAIN/PR12/LINEAGE=UNTOUCHED_BY_THIS_DECISION`.
