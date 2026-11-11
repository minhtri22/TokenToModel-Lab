# TTM-Small-4M × EmbeddingGemma 2 — A0C kiểm định T1, nguồn chưa tiền huấn luyện và A0B

**Operation:** `TTM_GEMMA2_SEMANTICS_ORIGIN_A0C_T1_LEXICAL_MANIFEST_AND_SEEDED_SAME_ARCH_UNTRAINED_SOURCE_CPU_ADMISSION`  
**Ngày:** 2026-11-11  
**Nhánh:** `research/ttm-gemma2-token-alignment-pretraining-causality-20261111`.  
**Phán quyết:** `T1=PASS` · `A0B_EXACT_PRIVATE_CPU=PASS` · `NONPRETRAINED_INPUT_ONLY=PASS_REPRODUCIBLE_COMPONENT` · `LEXICAL_COVERAGE=PASS_AUDIT_ONLY` · **`T4_2X2=HOLD`**.  
**Cấm:** huấn luyện, inference/LM forward, sửa L0020/L0021, dùng OOD256/H768/TEST để chọn đối chứng, công bố donor/token rows riêng tư.

## 1. Đã tìm được manifest T1 gốc, không thay thế

Đọc từ Drive riêng tư `TTM_Small4M_EmbeddingSwap_Input/T1_BPE2048_REAL_TRAIN_MANIFEST.json`, tệp thật **34.589 byte**, SHA256 `cba18e60cee3d08a353ee6d4a451017289e45af7b4b1179c87171b9b78d7dfdc`. Mã CPU đã xác minh lần lượt:
- `manifest_sha256` nội bộ: `6da22cf79c3a6cfd08d80a768eb1074125a753164ccf62a164e79545956e94c6`.
- T1 có `2048` token, `1791` merge pair IDs, EOS ID `256`, schema `ttm.gpt2.pretokenized.byte-bpe.2048.v1`. Phát lại từng merge và đối chiếu byte-canonical với token list thật: PASS. SHA danh sách token+merges `aea0e2a1a1bc1943f20b767ba2f879e3a47f0cb43b8b66026b1a34a038e014af`: PASS.
- Nguồn donor private ZIP SHA `2c6cb72f35eba72d6014f15914d6e9792cbf0bf6774d93e3ff5c53e5c6b9ba9a`, candidate SHA `c9fc798d8880c7e76636258052e9885dbb086d7b462a5b6bee5cff8b582973c3` và pack TRAIN-only `184f68b4c0c800ef3e98362c2e20e1cd35baa269e926489a475664526ecd9913`: 3/3 thực SHA PASS.
- Độc lập giải mã GPT-2 byte-unicode BPE của 2.048 token và đối chiếu trực tiếp mặt nạ `tok.valid` trong checkpoint: **1917 token mapped, 130 fragment UTF-8 chưa hoàn chỉnh, một EOS không mapped — PASS parity 2048/2048**. Token strings không được xuất hoặc commit.

## 2. Độ phủ kiểm tra lexical/semantic độc lập

Phân loại chỉ từ token T1, TRAIN token frequencies và valid donor mapping; **đây mới là ứng viên lexical**, không phải word-sense/semantic ground truth.

| Chỉ số | Đo thật |
|---|---:|
| Token ID chỉ gồm chữ ASCII tùy chọn 1 leading space (đã mapped) | 1822 |
| Token ID bắt đầu bằng space và tiếp theo là chữ ASCII | 1240 |
| Loại leading-space có tần suất TRAIN ≥10 | 1176 |
| Loại leading-space có tần suất TRAIN ≥50 | 926 |
| Unique lowercase ASCII word types theo quy tắc rộng | 1557 |
| Unique lowercase word types có dạng leading-space | 1175 |

Hai bộ nhãn đánh giá *ngoài nguồn huấn luyện* được tra cứu chỉ để tính coverage, **không dùng cosine donor/NLL và không train probe**:
- **SimLex-999**: source `yumeng5/Spherical-Text-Embedding/datasets/SimLex-999/SimLex-999.txt`, blob SHA-1 `b642f3abe39c9ff1c9d6f942c917e47fd6c3801d`: **80/999** cặp khớp hai endpoint trong T1 theo chữ ASCII (76/999 với yêu cầu leading-space). Trong 80 có 7 cặp human similarity ≥7, 40 cặp ≤3; 112 unique word types. `SimLex` đo *similarity*, không tự động bằng relatedness.
- **WordSim-353**: source `msavva/transphoner/data/wordsim353.csv`, blob SHA-1 `d3b41852afce0a0732b756c017fc2519fb427812`: **21/353** cặp khớp hai endpoint (20/353 theo leading-space); 5 cặp human relatedness ≥7 và 2 cặp ≤3; 31 unique word types. `WordSim` đo *relatedness*, không được gộp thang scores với SimLex thành một estimand.

**Giới hạn bắt buộc:** cả hai phép đo là token-form coverage, không dùng TRAIN-frequency threshold cho từng cặp, chưa chứng minh mỗi token là complete whole-word trong ngữ cảnh và chưa chạy human-label/random-label selectivity probe. Với SimLex chỉ có 7 cặp điểm cao, chưa đủ một bộ contrast ngữ nghĩa cân đối cho confirmatory. Kiểm cả quyền sử dụng của benchmark tại nguồn trước khi phát hành; không đưa raw label rows lên GitHub. Không được dùng các cặp đã xem làm TEST khoa học mới nếu chưa đăng ký rõ vai trò exploratory.

## 3. Đã khởi tạo và băm lại nguồn nonpretrained INPUT-ONLY, chưa phải model đầy đủ

Theo cấu hình text EmbeddingGemma 2 được khóa trong nguồn gốc (revision `f9972ac22e696a105c482202646979e33e4b5a1e`, config SHA256 `b8f1e9931b57fbc054acdb445c41765d55b0074c58d145fa82839941ad1b5bb3`): vocab `262144`, hidden size `512`, 24 tầng text, initializer scale `0.02`, padding ID 0. Nguồn chính thức `https://huggingface.co/google/embeddinggemma-2/blob/main/config.json`. **Lưu ý main có thể đổi; pin nghiên cứu vẫn là frozen revision SHA.**

CPU Python `3.13` / PyTorch `2.10.0+cpu` / NumPy `2.3.5`: khởi tạo một bảng input token embedding **262.144×512 FP32** với `torch.nn.init.trunc_normal_` (mean=0, std=0.02, a=−0.04, b=+0.04), zero padding row 0, **seed `2026111173`**. Không nạp trọng số pretrained hoặc gọi layer mô hình.
- Tệp riêng tư `TTM_GEMMA2_A0C_SEEDED_INPUT_ONLY_20261111.npy`, **536.871.040 byte**.
- SHA256 nguyên tệp .npy `9c3b4e5e5ac105c31742ae52ae648aa2c2b727a95ee01ec62d45e15331e935c7`.
- SHA256 tensor raw FP32 LE `b6bfe073898ff1f117499272e2798dc9e9d5dca80431c301fadbc951e55837a1`.
- **Tái tạo độc lập cùng seed lần hai: raw SHA khớp**, đọc lại memmap cùng tensor sha. Không ghi 512 MiB tệp này lên GitHub.

**Phán quyết riêng:** `PASS_INPUT_ONLY_REPRODUCIBLE_CONTROL_COMPONENT`. Không được gọi đây là same-architecture **FULL NONPRETRAINED CHECKPOINT**; 24-layer text backbone chưa được khởi tạo và độc lập xác minh, thuật toán initializer có thể khác `transformers.post_init`, và tokenizer donor exact revision chưa được nạp để tái tạo mapping T1→donor IDs. Vì vậy nguồn này chưa đủ admissible cho H-B 2×2.

## 4. Đã thực thi lại exact A0B trên donor thật, trong chính integrated CPU runner

Tải mã A0B từ GitHub và tính Git blob của **byte thực**: `856b07246261bd637dedb320fb2f79eeeac27a67`, khớp frozen source. Gọi đúng CLI `--mode private-audit` trên donor ZIP gốc và TRAIN-only frequency. Lượt CPU chạy thật (không dùng lại số liệu độc lập A0B cũ):

| Cổng | Đo thực |
|---|---:|
| Hội tụ | **18 iteration** / tối đa 64 |
| Covariance relative Fro drift | **2.607150712956896e-15** |
| Projection max abs FP32 | **1.1920928955078125e-7** |
| Per-token L2 norm max abs FP32 | **1.1920928955078125e-7** |
| Per-token L2 norm max abs FP64 | 3.878269483337249e-9 |
| Residual top-10-neighbor overlap | 0.034220135628586335 |
| LM forward calls / training / eval loss | **0 / 0 / 0** |

Cổng A0B `PASS_A0B_CONSTRAINED_MOMENTS_MATHEMATICAL_CPU_FEASIBILITY`; không chứng minh pure semantic causality. Đây là phép chạy **mã đúng Git blob trên donor thật**, không chỉ synthetic fixtures hoặc thuật toán viết lại.

Lượt tích hợp `tools/embeddinggemma2_swap/semantics_origin_a0/ttm_gemma2_a0c_integrated_cpu_gate.py` cũng kiểm T1, candidate, TRAIN SHA, source .npy SHA và tensor raw SHA, source Git blob A0B rồi mới gọi A0B. Blob của chính mã tích hợp: `8a29c02ff941f0e697958765fbc4f0c32d1a0035`. SHA-256 của receipt JSON CPU riêng tư `e0007da5e84c8f7681e96ccb8a9cb3659ac68ccc670074e01aa04ec2098bf19a`. Mã tạo bảng seed có Git blob `f79d8038d362e5b2f3ad135c13aee14738c5cde6`.

## 5. Một quyết định cho pilot T4

**`T4_2X2=HOLD_FULL_SAME_ARCH_AND_DONOR_TOKENIZER_MAPPING_AND_PROBE_BALANCE`.**

- `T1_SOURCE=PASS_EXACT`, `T1_DONOR_MAPPING_MASK=PASS`.
- `A0B_EXACT_CPU_REAL=PASS`, geometry-matched residual null sẵn sàng cho nghiên cứu mới.
- `UNTRAINED_INPUT_COMPONENT=PASS_REGENERATED_HASH` nhưng `FULL_UNTRAINED_TEXT_MODEL=NOT_EXECUTED` và `DONOR_TOKENIZER_MAPPING=NOT_VERIFIED`.
- `LEXICAL_COVERAGE=MEASURED`; SimLex có 80 cặp mapped nhưng rất ít cặp similarity cao, chưa chứng minh whole-word context và chưa có random-label control QA.
- Vì H-B muốn đo **pretraining-origin advantage**, không được thay một bảng random khớp shape cho một full-model counterpart đã được kiểm xuất xứ. Chạy T4 ngay sẽ chưa đủ để kết luận. HOLD không phải science FAIL.

**Giới hạn quản trị:** Không có L0022 khoa học mới; giữ `lineage.md` đúng blob `02835041fbd90f8dec61e8a6e1478e6d2fb5eec2`, L0020/L0021 và science OOD256 unchanged; không đụng TTM `main` hoặc nhánh nghiên cứu gốc. Không public private T1 tokens, train IDs, donor weights, random tensor.

**Bước thực hiện tiếp theo:** `TTM_GEMMA2_SEMANTICS_ORIGIN_A0D_FULL_UNTRAINED_TEXT_CONFIG_DONOR_TOKENIZER_MAPPING_AND_BALANCED_LEXICAL_PROBE_CPU_ADMISSION` — tải offline/verified tokenizer files đúng donor revision và config gốc trong phạm vi nguồn owner, khởi tạo cùng kiến trúc text (nếu chi phí CPU cho phép) với pin version/seed/SHA, tái dựng cùng T1 mapping; thiết kế lexical probe có đủ nhóm similarity cao/thấp và đối chứng morphology/frequency, chỉ chấm sau hợp đồng science mới. Tất cả CPU source QA được gộp một lượt; chưa mở T4 tự động.
