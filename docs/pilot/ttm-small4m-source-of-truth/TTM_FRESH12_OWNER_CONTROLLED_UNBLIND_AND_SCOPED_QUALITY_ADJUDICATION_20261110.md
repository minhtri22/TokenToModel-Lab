# TTM-Small-4M — FRESH12 Owner-Controlled Unblind & scoped quality adjudication

**Ngày 2026-11-10.** Nhiệm vụ: `TTM_SMALL4M_FRESH12_OWNER_CONTROLLED_UNBLIND_HANDOFF`.  
**Nguồn sự thật:** GitHub PR [#13](https://github.com/minhtri22/TokenToModel-Lab/pull/13), nhánh `research/ttm-small4m-q1q2-quality-single-batch-20261109`. **Phân xử phạm vi pilot, không phải kết quả khoa học được xác nhận bởi người chấm con người.**

## 1. Tình trạng niêm phong *trước* giải mù

- Codex AI (GPT-6), **REVIEWER_ONLY**, đã ghi [biên nhận hoàn tất](https://github.com/minhtri22/TokenToModel-Lab/pull/13#issuecomment-6758016818). Không tự diễn giải là reviewer con người hoặc tổ chức độc lập.
- [Phiếu 144/144 điểm](../../../artifacts/qa/ttm-original1280/fresh12/reviewer/TTM_FRESH12_CODEX_AI_SCORES_R01_R24_20261110.csv) có SHA-256 `d56f8f062d1a7ef2addd391b524cf555dc81d8eca5406a78daee3a7935c6a29c`, Git blob `39de8ec0ee46560c99d75533d4b62baeb844eea0`. Commit khóa trước giải mù `20163b753b56f8645b78731224538816569a3222`.
- [Biên nhận khóa điểm](../../../artifacts/qa/ttm-original1280/fresh12/reviewer/TTM_FRESH12_CODEX_AI_SCORE_LOCK_RECEIPT_20261110.md) có SHA-256 `081fbb773f545aef2921557fbf9a313ff6bd7dfdbbe036d250a0ae161f65e73e`, Git blob `e4b0b46cf182af3551a2b8aa4e43bab159cf61e7`. Cả CSV và receipt **đã đọc lại exact từ GitHub trước khi giải mù**, sau đó copy vào PR #13 với **đúng cùng Git blob** (không sửa phiếu).
- 24 cặp, 48 đoạn sinh, 144 điểm nguyên 0–3, 24/24 nhận xét, tổng điểm thô **114/432**; **35/48** đầu ra bám prompt = 0.
- Nguồn bản A/B [packet reviewer](../../../artifacts/qa/ttm-original1280/fresh12/reviewer/TTM_FRESH12_BLINDED_REVIEWER_PACKET_R01_R24_20261110.md) SHA-256 `85fec5d290d6639809ca6ba437982fa8bb11cd5e7e0fbcf412d40f7bc9c3a037`. Nhãn trung tính R01–R24 được khóa trước khi sinh theo amendment A01.
- [Giao thức tiền đăng ký](../../../artifacts/qa/ttm-original1280/fresh12/TTM_SMALL4M_FRESH12_PUBLIC_PREREG_GITHUB_CANONICAL_20261109.json) Git blob `919c43f2c919fa733b20a9be5d6b965e9649339c`: 12 prompt × 2 checkpoint (1024,1280) × 2 cách đưa dấu cách cuối, decoder greedy, max 64 token, 24 cặp hoán vị A/B.

## 2. Kiểm soát giải mù và tính toàn vẹn

- Khóa AES-256-GCM chỉ được đọc tại vùng riêng tư của chủ dự án **sau** khi thấy các SHA chính thức trên GitHub. Không xuất/commit khóa, seed, bảng liên kết R-ID ↔ checkpoint/điều kiện, hoặc 48 raw outputs có nhãn dưới dạng rõ vào repository công khai.
- Bản raw48+mapping mã hóa AES-256-GCM trên PR #13: [sealed ciphertext](../../../artifacts/qa/ttm-original1280/fresh12/escrow/TTM_FRESH12_ENCRYPTED_RAW48_AND_PRIVATE_MAPPING_20261110.json), Git blob `e364ea7309c9d4b8b4288ec81acef47208db4375`, SHA-256 file `3097d66900b0027edcc1c0f81c8467f31e0dbbc8b2d80365fb7c798b2ee64435`.
- Xác minh SHA256 dữ liệu giải mã so với cam kết trên ciphertext, so văn bản 48/48 với raw đã niêm phong, tái dựng đầy đủ 24 cặp bằng HMAC-SHA256 từ seed escrow, kiểm tra đúng hai điều kiện và 12/12 cân bằng (6/6 tại mỗi checkpoint). Dùng đúng score CSV **bất biến**, không chấm lại.
- **108/108** kiểm tra nguồn, SHA/byte, gói A/B và phép ghép điểm PASS. Bộ tính số học thứ hai **66/66 PASS**; đây là QA kỹ thuật và số học của hai chương trình, **không** phải chấm ngữ nghĩa độc lập lần hai.
- Giới hạn custody: SHA-256 của file mapping trước đây được ghi trong prereg là `ed22d6fc6d2075a7d7aedb1512aba9ae4034b95dd39fbe9c5c4a5c86a4aad9ed`, nhưng **không tái kiểm được chính file nguyên byte đó** từ môi trường hiện hành. Thay vào đó đã xác thực cam kết **seed SHA-256** và tái dựng đúng toàn bộ mapping 24 cặp theo HMAC, đối chiếu raw/packet. Không nhận `ORIGINAL_MAPPING_FILE_SHA=PASS_EXACT` khi chưa có file.

## 3. Kết quả sau giải mù

Chỉ số chính đã tiền đăng ký là **chênh lệch điểm bám prompt `TRIMMED − BASELINE`**. Trung bình mỗi điều kiện trên 24 đoạn, ba trục 0–3.

| Trục đánh giá | Giữ dấu cách cuối (baseline) | Bỏ dấu cách cuối (trimmed) | Δ |
|---|---:|---:|---:|
| Bám prompt (prompt adherence) | 0.291667 | 0.291667 | **0.000000** |
| Mạch lạc (coherence) | 1.000000 | 1.000000 | 0.000000 |
| Nhất quán (consistency) | 1.166667 | 1.000000 | −0.166667 |
| **Tổng /9** | **2.458333** | **2.291667** | **−0.166667** |

- **Bám prompt:** trimmed thắng rõ 4/24; baseline thắng 4/24; hòa **16/24**.
- **Tổng /9:** trimmed thắng 4/24; baseline thắng 6/24; hòa 14/24.
- **Checkpoint 1024:** Δ adherence **−0.166667/3**; 1280: **+0.166667/3**. Chưa đủ bằng chứng step1280 có chất lượng tổng quát hơn step1024.
- **Bootstrap theo 12 cụm prompt**, mỗi cụm gồm hai checkpoint, 10.000 resamples (seed 20261110), percentile CI95 **[−0.208333, +0.166667]**, gồm 0. Khoảng này **chỉ mang tính mô tả** khi có duy nhất một reviewer AI.
- Codex chấm **mạch lạc = 1 cho toàn bộ 48 đoạn**; thang điểm riêng trục này không phân biệt giữa hai điều kiện trong lượt đánh giá này. Không diễn giải `Δ coherence=0` là chứng minh mô hình thực tế tương đương trên mọi nội dung.

## 4. Kiểm tra đúng các ngưỡng đã tiền đăng ký

| Cổng đã khóa trước chạy | Kết quả |
|---|---|
| Mean Δ adherence ≥ +0.5/3 | **FAIL** — 0 |
| Trimmed thắng rõ adherence ≥16/24 | **FAIL** — 4/24 |
| Δ adherence không âm tại từng checkpoint | **FAIL** — step1024 = −0.167 |
| Mean Δ coherence ≥−0.25 | PASS — 0 |
| Mean Δ consistency ≥−0.25 | PASS — −0.167 |
| CI95 bootstrap prompt-cluster lower >0 | **FAIL** — −0.208 |
| A/B cân bằng 12/12 và 6/6 mỗi checkpoint | PASS |
| Điểm Codex AI khóa trước giải mù | PASS (scoped AI) |

**`REGISTERED_CANDIDATE_GATES=PASS_4_FAIL_4`.** Vì các cổng cần đồng thời đạt PASS, **`SEMANTIC_GAIN=NO_DEMONSTRATED_SEMANTIC_GAIN_SCOPED`**. Đây là FAIL theo **ngưỡng ứng viên cải thiện của pilot**; không phải FAIL toàn bộ Transformer/P02 hay kết luận thống kê rằng hai điều kiện giống nhau.

Tác động **lên token mở đầu** từ nghiên cứu hậu nghiệm cũ vẫn đúng trong phạm vi đã đo, nhưng không được thay thế phép kiểm định **tiếp nối nội dung** của FRESH12 bằng chỉ số lexical/newline.

## 5. Giới hạn và quyết định nghiên cứu

- 12 prompt mới **chỉ được kiểm tra khác 8 prompt pilot trước**, không tái mở TEST/Q1Q2 đã khóa để thử độ trùng đầy đủ. Hai mẫu/checkpoint trong cùng prompt là tương quan; 24 cặp không phải 24 prompt độc lập.
- Reviewer là **Codex AI** có phạm vi được tách khỏi executor, **không có xác minh tính độc lập tổ chức hoặc đánh giá con người**; có rủi ro thiên lệch còn lại vì nguồn GitHub công khai chứa mô tả lịch sử và phong cách sinh có thể tiết lộ định dạng.
- Điểm tuyệt đối bám prompt rất thấp: 35/48 đoạn đạt 0. Dữ liệu hướng dẫn/tiếp nối, năng lực mô hình nhỏ, coverage và training objective cần nghiên cứu, nhưng kết quả này **không đủ cơ sở để tự động thêm bước huấn luyện** trên corpus hiện tại.
- **HOLD** thay TRAIN/tokenizer, GPU, scale, và step1280+ training. Tiếp theo phù hợp là **thiết kế sửa đổi mục tiêu học/đối chứng dữ liệu (DESIGN ONLY)**, yêu cầu một giả thuyết tiền đăng ký và so sánh ngang ngân sách mới nếu sau này thực thi.
- Không cập nhật `lineage.md` vì đây là kết quả kỹ thuật/đánh giá pilot scoped với người chấm AI duy nhất, không phải quyết định PASS/FAIL khoa học confirmatory đã được xét duyệt.

## 6. Source of Truth / trạng thái cuối

Tài liệu cùng hai biên bản QA và kết quả dạng JSON được lưu trên **PR #13**. Các dữ liệu phân cặp riêng tư lưu ngoài GitHub **ở dạng rõ**, chỉ được tham chiếu bằng SHA. Không merge, không sửa `main` hoặc `lineage.md`.

`REVIEW_LOCK=VERIFIED_BEFORE_UNBLIND` · `UNBLIND=COMPLETED_OWNER_CONTROLLED` · `SOURCE_INTEGRITY=PASS_108_108` · `SECOND_PASS_ARITHMETIC=PASS_66_66` · `SEMANTIC_GAIN=NO_DEMONSTRATED_SCOPED` · `NEW_INFERENCE=NO` · `NEW_TRAINING=NO` · `TEST_Q1Q2=UNTOUCHED` · `PR13=HOLD_DRAFT` · `MAIN=UNCHANGED` · `LINEAGE=L0017_UNCHANGED`.

**Bước thực hiện tiếp theo:** `TTM_SMALL4M_PROMPT_CONDITIONING_TRAIN_OBJECTIVE_ROOT_CAUSE_AND_EQUAL_BUDGET_ABLATION_DESIGN` — nghiên cứu dạng dữ liệu và mục tiêu học next-token so với giữ nhiệm vụ/tình huống; chỉ lập kế hoạch đối chứng không đụng checkpoint hay TRAIN trước khi phê duyệt giả thuyết.
