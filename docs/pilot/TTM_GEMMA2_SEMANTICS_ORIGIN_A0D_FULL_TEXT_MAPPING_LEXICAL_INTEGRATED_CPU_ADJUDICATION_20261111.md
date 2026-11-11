# TTM-Small-4M × EmbeddingGemma 2 — A0D text-only source, donor tokenizer, lexical controls

**Ngày:** 2026-11-11  
**Operation:** `TTM_GEMMA2_SEMANTICS_ORIGIN_A0D_FULL_UNTRAINED_TEXT_CONFIG_DONOR_TOKENIZER_MAPPING_AND_BALANCED_LEXICAL_PROBE_CPU_ADMISSION`  
**Nhánh khoa học tách biệt:** `research/ttm-gemma2-token-alignment-pretraining-causality-20261111`.  
**Loại kết quả:** SOURCE/CPU FEASIBILITY, exploratory lexical signal, **KHÔNG có PASS/FAIL khoa học mới**.  
**Một quyết định T4:** **`HOLD_T4_2X2`**.

## 1. Đối chiếu nguồn và những gì không được giả định

T1 BPE2048 manifest là file thật 34.589 byte, SHA256 `cba18e60cee3d08a353ee6d4a451017289e45af7b4b1179c87171b9b78d7dfdc`; 2.048 token, 1.791 merges, 1.917 mapped donor rows đã được audit ở A0C. Donor nguồn ZIP SHA256 `2c6cb72f35eba72d6014f15914d6e9792cbf0bf6774d93e3ff5c53e5c6b9ba9a`; candidate model state `c9fc798d8880c7e76636258052e9885dbb086d7b462a5b6bee5cff8b582973c3`, TRAIN-only token counts lấy từ T4 pack SHA `184f68b4c0c800ef3e98362c2e20e1cd35baa269e926489a475664526ecd9913`. Không đọc OOD256/H768/TEST outcome.

Mã Hugging Face chính thức được đối chiếu chỉ đọc: `huggingface/transformers/src/transformers/models/embedding_gemma2/modeling_embedding_gemma2.py` Git blob `c0fedeb4228fdab6020a78f6104fe05572996e1d` (main tại thời điểm xem). Model text có 24 lớp, layer index 5/11/17/23 dùng full attention với query head_dim 512; các lớp khác head_dim 256. Text input token vocab 262144 × hidden 512; text output projection 768. Source pin lịch sử từ nghiên cứu gốc: `google/embeddinggemma-2` revision `f9972ac22e696a105c482202646979e33e4b5a1e`; `config.json` SHA256 `b8f1e9931b57fbc054acdb445c41765d55b0074c58d145fa82839941ad1b5bb3`, `tokenizer.json` `4d777ef5bdc1aa36227abdfb77c3e49e7b9c892d16e1b6bda41c393504828be4`, `tokenizer_config.json` `17bd5d6e9364ca49a534e1502076593317c298d4a663623091ed45388f004874`.

**Blocker thật:** Nguồn được kết nối trong lượt này chỉ chứa donor candidate đã ánh xạ sẵn; **không tìm được byte gốc đúng SHA của donor tokenizer/config** tại revision khóa để chạy lại `map_bpe_tokens`. Python CPU cũng không có thư viện `transformers`, và cài từ PyPI không thực hiện được vì mạng runtime không hoạt động. Do đó không được tuyên bố `HF_OFFICIAL_MODEL_CLASS=PASS`, `HF_EXACT_POST_INIT=PASS` hay `DONOR_TOKENIZER_MAPPING_RECONSTRUCTED=PASS`.

## 2. Khởi tạo và tái lập toàn bộ parameter topology text-only (khác model class chính thức)

Đã dựng và khởi tạo CPU `TextParameterMirror` có **24 lớp, 271.002.624 tham số, 413 state tensors/buffers**, đúng các nhóm trọng số tham chiếu public HF (embedding, full/sliding attention, RMSNorm, MLP, per-layer PLE, projection). Seed khóa `2026111194`, FP32, PyTorch `2.10.0+cpu`. Khởi tạo lại **độc lập hai lần** và băm danh sách tên + shape + dtype + SHA tensor theo thứ tự ổn định: **cùng Merkle SHA256 `4a460d1046e89b4311ea71e62efe5690c20dcf37fd61c1329d163d348e3864b3`**. SHA tên/shape `63126c6791db9dffe78300060eef48de1cbc5f56ec7d0e849d94b605d9873203`.

Đã ghi file riêng tư `TTM_GEMMA2_A0D_TEXT_PARAMETER_MIRROR_SEEDED_20261111.safetensors`, **1.084.055.304 byte**, SHA256 `3c84bcfef1b16e5a15b14d5ead7876f67d2fde739725d4207c0a823c55a27b0d`. Kiểm tra độc lập bằng `safe_open` trên file thật: 413 keys, layer 23 q-proj shape (2048,512), embedding projection shape (768,512), padding input row 0, và toàn tệp SHA đúng. Không public trọng số 1,08 GB trên GitHub. Source đã chạy đúng Git blob `affa63b24ba6c26f8d35efec608ebdb8fd3ade8f`, path `tools/embeddinggemma2_swap/semantics_origin_a0/ttm_a0d_text_parameter_mirror.py`.

**Giới hạn phân loại:** Đây là *reproducible parameter-topology mirror*, **không phải** instance của official `EmbeddingGemma2TextModel`, không triển khai forward, chưa kiểm tra `transformers.post_init` parity, chưa dùng tokenizer original để map donor IDs vào T1, và không phải official nonpretrained checkpoint. Cổng `OFFICIAL_SAME_ARCH_SOURCE` vẫn **HOLD**.

## 3. Lexical probe có nhãn con người và control tần suất/hình thái — thăm dò CPU

Nguồn nhãn: SimLex-999 từ `yumeng5/Spherical-Text-Embedding/datasets/SimLex-999/SimLex-999.txt`, Git blob `b642f3abe39c9ff1c9d6f942c917e47fd6c3801d`. Chỉ các token T1 thực có dạng `" " + lowercase ASCII word` và mapping hợp lệ, không suy đoán BPE fragment hay whole-word context. **76/999** cặp có đủ hai endpoint; bản ghi dẫn xuất 76 cặp được giữ riêng tư, SHA256 `4f8a87ebb0221bba213488ad2f41692dccdc449611260579d2aa783a98302839`.

Với ngưỡng khám phá *không tiền đăng ký* (điểm similarity **≥5** so với **≤3**), 22 cặp high và 38 cặp low; thuật toán Hungarian ghép theo 8 biến lexical/frequency TRAIN-only, chọn **22 high + 22 low**, tổng 44. Nguồn 512-d input embeddings thực là `tok.source.weight` từ candidate frozen, **không model inference**.

| Chỉ số trên 44 cặp | Kết quả |
|---|---:|
| High human similarity, mean donor cosine | 0.2109389609605035 |
| Low human similarity, mean donor cosine | 0.15580480367235405 |
| High−low donor cosine | **+0.05513415728814944** |
| Spearman donor cosine ↔ human scores | +0.4936392176157056 |
| Spearman string-similarity ↔ human scores | +0.01668213068851197 |
| Random-label permutations | 10.000 |
| **Naive permutation p** | **0.0051994800519948** (CHỈ exploratory, KHÔNG dùng làm science significance) |
| Unique word types / word reuse | 71 unique / 17 lượt xuất hiện bị lặp |

**Không đủ để kết luận:** (a) có shared word IDs, nên 44 cặp không phải 44 quan sát độc lập; (b) hai biến vẫn lệch (absolute standardized mean difference 0,3717 về chênh lệch độ dài và 0,2545 về chênh tần suất), ngoài ngưỡng cân bằng tư vấn 0,25; (c) ngưỡng 5/3 và chọn bộ có coverage đã dựa trên dữ liệu đánh giá từng thấy, không là prereg mới; (d) input embedding có thể mã hóa morphology/frequency và overlap tiền huấn luyện donor `UNKNOWN`; (e) chưa có nguồn official untrained có cùng donor-tokenizer mapping. Đây là **tín hiệu hỗ trợ lựa chọn nghiên cứu**, không phải kết luận H-A/H-B về LM loss.

Script đã chạy và byte-pinned trong GitHub: `tools/embeddinggemma2_swap/semantics_origin_a0/ttm_a0d_lexical_probe_cpu.py`, blob `d1ed172ebfc9c72421ff788764a8cb11597251ba`. 2 negative QA thực tế: đổi 1 byte manifest T1 → `A0D_HOLD_T1_SHA`; làm thiếu một cặp trong 76 source rows → `A0D_HOLD_SIMLEX_DERIVED_SOURCE_MATCHES`; **PASS_FAIL_CLOSED_2_OF_2**. Không đăng lên GitHub raw SimLex rows/token strings/source donor tensor.

## 4. QA tích hợp và một quyết định duy nhất

| Gate | Phán quyết |
|---|---|
| T1 file + candidate + TRAIN SHA | **PASS** |
| A0B geometry exact-source CPU (A0C trước) | **PASS_SCOPED** |
| Text parameter topology 24-layer CPU, seed/SHA repeat | **PASS_COMPONENT** |
| Full Transformers official model class và historical config bytes | **HOLD** |
| Donor tokenizer historical SHA và mapping lại T1 | **HOLD** |
| Balanced pair **counts** SimLex 22/22 | **PASS_EXPLORATORY_COUNTS** |
| Independent lexical calibration, frequency/morph balance, non-overlapping paired anchors | **HOLD** |
| H-A/H-B causal scientific gate | **NOT_EXECUTED** |

**Quyết định cuối:** **`T4_PILOT_2X2=HOLD`**. Không huấn luyện 4-arm 3-seed 512-step, không tạo claim mới hoặc chấm lại OOD256. Lợi ích không đến từ việc cứ tạo thêm mô hình parameter-matched; muốn chứng minh *pretrained origin* phải có official untrained model/tensor mapping cùng token và một tập nhãn/kiểm định độc lập đủ cân bằng, kiểm tra confounds. L0020, L0021 và `lineage.md` không chỉnh; `main` không chỉnh, không L0022.

**Bước thực hiện tiếp theo:** `TTM_GEMMA2_A0D_OWNER_LOCAL_PINNED_DONOR_TOKENIZER_AND_OFFICIAL_TRANSFORMERS_CLASS_ONE_INTEGRATED_READBACK`. Tập trung đúng một dependency có thể xử lý: tìm các file donor `config.json`, `tokenizer.json`, `tokenizer_config.json` trên Windows/Drive **theo SHA khóa** và kiểm official `EmbeddingGemma2TextModel` trong venv Python 3.12 nếu sẵn có. Không tạo mô hình/nguồn thay thế lần nữa; chỉ khi nguồn PASS mới đóng băng controlled pilot prereg và quyết định T4. Với lexical probe, cần nhãn mới (không dùng 44 cặp đã chấm làm confirmatory) và cách chia không trùng từ giữa nhóm.
