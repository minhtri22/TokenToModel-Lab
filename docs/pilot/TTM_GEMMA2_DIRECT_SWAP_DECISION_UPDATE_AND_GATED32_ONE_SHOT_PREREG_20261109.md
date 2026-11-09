# TTM-Small-4M × EmbeddingGemma 2 — Đính chính STOP và tiền đăng ký phép thử cơ chế G/R 32 bước

**Ngày:** 09/11/2026. **Nhánh:** `research/ttm-small4m-embeddinggemma2-token-swap-minimal-proof-20261109`.

## 1. Đính chính khoa học — không sửa lịch sử

STOP direct-swap trong báo cáo cơ chế commit `79355701e56ca6e7f34bd4f0585f4935184f2a00` dựa trên kết quả **64 bước** của L0014. Khi ấy, C chưa vượt A/B trên VALIDATION; đó là kết luận đúng tại mốc đó, **không phải chứng minh cơ chế direct-swap bất khả thi**.

Bằng chứng cập nhật: L0015 (1.024 bước: chưa thiết lập lợi thế), L0016 (2.048 bước: tín hiệu thăm dò dương), và **L0017** (đánh giá một lượt trên 320 truyện mới: `PASS_FIXED_CHECKPOINT_NEW_HOLDOUT_ALL_THREE_CONTRASTS`). NLL A=`3.3414141969769373`, B=`3.358166448820946`, C=`3.3086025043275265`, D=`3.4265771698754617`; cả ba cận dưới CI95 cho A−C/B−C/D−C >0. Kết luận **phạm vi checkpoint cố định**: direct-swap sau 2.048 bước có lợi ích dự đoán so với ba đối chứng. Không còn áp dụng STOP bao trùm toàn bộ direct-swap.

**Quyết định đang có hiệu lực:** `DIRECT_SWAP=POSITIVE_CONFIRMED_FIXED_CHECKPOINT_SCOPE` và `GATED_RESIDUAL=SEPARATE_CAUSAL_MECHANISM_EXPLORATION`. Bằng chứng L0017 không cho biết ưu thế do riêng ngữ nghĩa donor, hay do năng lực tham số, tối ưu và phép chiếu; một seed không phải lặp training độc lập. Phép thử G/R dưới đây từ checkpoint 1.024 riêng biệt **không giải thích trực tiếp** tác dụng của C2048. Không sửa L0014–L0017 hay nguyên văn quyết định lịch sử.

## 2. Tiền đăng ký một lượt B/G/R — đã cố định trước khoa học

**Operation:** `TTM_SMALL4M_EMBEDDINGGEMMA2_ZERO_GATE_RESIDUAL_32_STEP_CPU_PROBE`. **RUN_ID mới, chưa tiêu thụ:** `ttm_small4m_gemma2_zero_gate_residual_32_cpu_probe_20261109_v1`. Thiết kế kế thừa tài liệu gốc và amendment sau L0017 commit `f65b0f84f7ffd6a51e82e16d3718b25a0044c970`.

- **B**: TTM checkpoint 1.024, output head untied nhưng trọng số số học gốc bảo toàn, toàn bộ backbone đóng băng, không optimizer.
- **G (donor thật)**: `E0(t) + tanh(a_G)⊙Δ_G(t)`, trong đó `Δ_G(t)=P_real Z_real(t) − E0(t)` cho token hợp lệ; fallback Δ=0 với token không map/EOS. P_real là ridge 512→256 đã khóa tại candidate initialization; chỉ tham số gate `a_G ∈ R^256` được học.
- **R (donor hoán vị)**: hoán vị 1.917 valid token donor với `NumPy.default_rng(20261109)`, refit ridge 0.01 trên cùng embedding TTM gốc, mask và EOS bất biến; chỉ `a_R ∈ R^256` được học. Đối chứng kiểm tra gán donor-token, **không cô lập đầy đủ ngữ nghĩa pretrained**. Trước khi claim chỉ phép so sánh logits trên token tổng hợp: step0 B=G=R chính xác; G và R không dùng output head nối vào embedding.
- **Nguồn bất biến:** TTM T4 step1024 SHA256 `cb985751795c8328ad65acf7ca4c1033ce35182c1bfbdb8c38550de629cb271b`; donor candidate SHA256 `c9fc798d8880c7e76636258052e9885dbb086d7b462a5b6bee5cff8b582973c3`; pack TRAIN+VAL T4 SHA256 `184f68b4c0c800ef3e98362c2e20e1cd35baa269e926489a475664526ecd9913`; pack manifest SHA256 `ef2e6e67d49b1d5a921b1051df329f15574f1c10cece0ce49468acb53322d650`; P02 nguồn SHA256 `e0fcac285918b66b13c8f694e6d625a0691c9b59221b43043e63f46b25ddcc07`; adapter nguồn SHA256 `d11da61e9d7bb040f3263e680f026817a513553c186ab243e184ffaf6e68cd39`.
- **Huấn luyện:** hai nhánh G/R, mỗi nhánh `32 AdamW steps × 512 nhãn TRAIN hữu hiệu mỗi bước = 16.384` exposures; sử dụng cùng 32 danh sách cửa sổ chọn với replacement theo `numpy.default_rng(2026110902)` và giới hạn nhãn bằng `-100`. CPU FP32, `lr=0.003`, `betas=(0.9,0.95)`, `eps=1e-8`, `weight_decay=0`, global gradient clipping 1.0. Mọi tham số ngoại trừ 256 chiều gate đóng băng; không quét LR, không thay schedule, không chọn checkpoint bằng VAL.
- **Đánh giá đúng một lần sau cả G/R đủ 32 bước:** 256 truyện VALIDATION đã dùng trước, 328 cửa sổ, 61.122 nhãn; metric NLL trung bình theo token, tổng NLL theo truyện riêng tư, không dùng lại 320 holdout L0017 hay 64 TEST lịch sử. Bootstrap ghép cặp **theo truyện**, 1.000 lần với `numpy.default_rng(20261109)`, CI hai phía 95% percentile. So sánh **B−G** và **R−G** (dương nghĩa G tốt hơn). Kết quả **`EXPLORATORY_GATED_DONOR_ALIGNMENT_SIGNAL`** chỉ khi cả hai cận dưới CI95 >0; nếu hợp lệ nhưng một cận không dương → **`GATED_32_STEP_SIGNAL_NOT_ESTABLISHED`**. Không tự tăng bước hoặc chạy lại để cứu kết quả.
- **CLAIM một lượt:** mã nguồn, 6 input SHA, số nhãn, mô hình, cổng step0 và lịch mẫu được kiểm **trước** tạo riêng `CLAIM.json`; ghi độc quyền trước bước optimizer đầu. Nếu có CLAIM và lỗi, không tự replay; giữ FAIL receipt, phải phân xử. `RESULT.json` sau hoàn tất có đánh dấu `PENDING_INDEPENDENT_ADJUDICATION` và biên bản per-story ở khu vực private, reviewer chỉ tái tính bootstrap **không gọi model**. Chỉ append `lineage.md` nếu kết quả thật đã được thẩm định khoa học.
- **Giới hạn:** VALIDATION đã dùng nhiều lần, nên dù kết quả dương vẫn chỉ exploratory, không phải blind confirmatory. Chênh lệch `||Δ_G||` và `||Δ_R||` không được bảo đảm cân bằng; thống kê mô tả được đo từ các bảng token trước TRAIN (`0.39382985` và `0.45858899` L2 mean tương ứng), không dùng để lựa chọn mô hình. Không khẳng định đây là kiểm định giải thích nhân quả trực tiếp kết quả direct-swap 2.048.

## 3. Đóng gói và QA nguồn — không phải thí nghiệm mới

- Runner `ttm_gemma2_gate32_cpu_once.py`: SHA256 `235816631eedbe212f7f431700024f1e4ae8e470fd5b0cabcdabd78421c815bf`.
- Independent reviewer `ttm_gemma2_gate32_independent_readback.py`: SHA256 `d25296daa0ff3185dc078195d0b239b655c0d305a031a3d0129d9b5a5d05cbca`.
- PowerShell 5.1 `RUN_GATED32_ONCE.ps1`: SHA256 `e27b7ba2419cf9dc1c7a0483abb68ff0f7ffcd53a9b585bdc8a59f3d1c407adc`.
- Gói ZIP riêng tư gồm mã, checkpoint và donor candidate: `TTM_GEMMA2_ZERO_GATE32_CPU_ONESHOT_SOURCE_20261109.zip`, SHA256 `42cae40352bb86303663a75d1e0235996ca59dc9b64470b16725706af483fdc5`, 59.864.771 byte. **Không upload ZIP/checkpoint/token pack lên GitHub**; đường chạy mặc định ghi trong `_tmp` của dự án trên máy Windows.
- QA trước science: **37/37** từ bộ kiểm tổng hợp gốc; trong đợt này tải, kiểm SHA và nạp **checkpoint thật bước 1.024** + candidate thật; kiểm bitwise step0 B=G=R trên token tổng hợp PASS; xác minh chỉ 256 tham số trainable mỗi gate, fallback PASS; một bước optimizer trên **token nhãn tổng hợp** cho G/R PASS (không phải 32-step TRAIN); baseline bất biến; không chấm VALIDATION. Mã nguồn được đóng băng trước CLAIM, không sửa sau khi dùng để tính khoa học.

## 4. Quản trị

Tại thời điểm tiền đăng ký này, **GATED32 SCIENCE = NOT_EXECUTED** và chưa phát hành CLAIM; **không sửa `main`, `lineage.md`, checkpoint cũ, TEST, L0017 hoặc nguồn P02**. RemoteMCP có thể chặn command admission; nếu vậy chạy một lần PowerShell trực tiếp trên Windows, không mở thêm vòng cấp phép kỹ thuật. Không GGUF, không triển khai sản phẩm; backlog riêng.