# TTM-GEMMA2 — đóng OOD256 và rà soát giả thuyết ngữ nghĩa vs hình học

**Ngày:** 2026-11-11  
**Operation:** `TTM_GEMMA2_OOD256_SCIENCE_CLOSURE_AND_NEXT_HYPOTHESIS_REVIEW`  
**Trạng thái:** `OOD256=SCIENCE_CLOSED_PASS_SCOPED` · `NEXT_HYPOTHESIS=PRIORITY_HIGH_CONDITIONAL_DESIGN_ONLY` · `NEW_TRAINING=NOT_AUTHORIZED` · `NEW_SCIENCE=NOT_EXECUTED`.

## 1. Đóng băng OOD256 — những gì đã được chứng minh

Nguồn khoa học L0020: `PASS_SCOPED_DONOR_RESIDUAL_STRUCTURE` trên H768 TinyStories. Nguồn khoa học L0021: `PASS_SCOPED_OOD_RESIDUAL_TRANSPORT` trên WikiText-2 raw OOD256 đúng một lần, khác miền TinyStories. Không hồi tố hoặc sửa L0020/L0021, không reset CLAIM và không dùng OOD256 làm tập xác nhận của giả thuyết tiếp theo.

**Hai đại lượng chính trên OOD256 (đã tiền đăng ký):**

| Estimand | Mean ΔNLL nats/target | CI 95% bootstrap theo 256 bài | Dấu qua 3 seed |
|---|---:|---|---|
| `tau_residual` | +0.06836278721978761 | [0.06235342572949934, 0.07423878749033531] | 3/3 dương |
| `gamma_real` | +0.0479801420718878 | [0.04355893220445865, 0.052225954797402115] | 3/3 dương |

2.000 bootstrap draw, seed `2026111198`, đúng 12 checkpoint step-2048, 256 bài×512 nhãn, 131.072 nhãn. Independent readback khớp 12/12 per-arm private receipt, 12 NLL, paired-document CI; cả ba OOD private/public SHA đúng; không huấn luyện thêm, không chọn checkpoint. Đọc lại Drive hiện hành xác nhận CLAIM owner scope một lượt, RESULT cùng estimands và 12 independent receipts.

**Pin bất biến (content-addressed)** của bằng chứng ở:
`artifacts/qa/ttm-embeddinggemma2/TTM_GEMMA2_OOD256_SCIENCE_CLOSURE_FROZEN_EVIDENCE_MANIFEST_20261111.json` trên nhánh nghiên cứu. Freeze commit khoa học `6f3c73401b1724b6040dd1f877bc4c0c514f60f2`; `lineage.md` Git blob `02835041fbd90f8dec61e8a6e1478e6d2fb5eec2` có L0020 và L0021. Google Drive folder ID `1cQ4kUtqqnII_xs6Q1qqM0R0JJT9owA7B` tiếp tục là kho riêng tư, không đổi file; content hash là cơ chế phát hiện thay đổi, **không phải khóa chống sửa cấp Google Drive**.

Không phát hành per-document loss, raw token window, private membership hay checkpoint ra GitHub. Không mở lại OOD256 hoặc tuyên bố một CI theo population of training seeds.

## 2. Vấn đề nhân quả chưa được giải đáp

Các kiểm soát của SEMANTIC4X3 không đo trực tiếp *pure semantic pretraining*. Mã `projection_and_permutations` từ frozen runner dựng `X_real`, `X_null`, `X_perm`, `X_null_perm`. `X_null` được dựng sao cho:

1. `X_real P^T = X_null P^T` (với `P` Ridge frozen, shape 256×512): **giữ nguyên giá trị input đã chiếu cho từng token tại khởi tạo**.
2. Trung bình từng chiều và ma trận hiệp phương sai toàn cục của 1.917 donor-token vectors khớp tới sai số số học.
3. Nhưng **không bảo toàn norm cho từng hàng**, pairwise local topology, higher-order moments, quan hệ ngữ nghĩa với token, hoặc khả năng model học `P` sau khởi tạo.

Vì vậy `tau_residual>0` chứng minh phần dư donor có tác dụng thêm ngoài các thống kê được giữ; `gamma_real>0` củng cố so sánh real/null. **Không thể quy toàn bộ chênh lệch thành tri thức ngữ nghĩa tiền huấn luyện.**

Rào cản định danh (identifiability): không thể vừa bảo toàn *toàn bộ* khoảng cách và quan hệ giữa tất cả token-vectors (full Gram matrix kèm ánh xạ token) vừa xóa sạch mọi cấu trúc ngữ nghĩa được mã hóa bởi chính quan hệ đó. Mục tiêu khả thi hơn là ước lượng **lợi ích của phép gắn đúng token vào phần dư (token–residual semantic alignment), với một tập hữu hạn thống kê hình học/lexical được đối sánh**, không tuyên bố causal isolation tuyệt đối.

Nguồn phương pháp học đối chứng bổ trợ: John Hewitt & Percy Liang (EMNLP 2019), *Designing and Interpreting Probes with Control Tasks*, https://aclanthology.org/D19-1275/; Zining Zhu & Frank Rudzicz (EMNLP 2020), *An information theoretic view on selecting linguistic probes*, https://aclanthology.org/2020.emnlp-main.744/. Đây là tham chiếu phương pháp cho kiểm tra lựa chọn thông tin và đối chứng ngẫu nhiên, **không phải bằng chứng thực nghiệm của TTM**.

## 3. Ma trận giả thuyết kế tiếp

| Lựa chọn | Câu hỏi đo được | Điều kiện kiểm soát | Khả năng | Khuyến nghị |
|---|---|---|---|---|
| **A. Geometry-aware token residual reassignment** | Gán đúng phần dư cho token có lợi hơn phân công lại đã ghép cặp không? | Giữ đúng `XP^T`, per-token norm, ngân sách/seed/schedule, cố gắng khớp hiệp phương sai, hình thái và tần suất | Kỹ thuật không tầm thường nhưng trực tiếp nhất | **Ưu tiên 1, CPU feasibility trước** |
| B. Whole-vector token shuffle | Real token mapping có lợi không? | Giữ multiset vector và covariance, nhưng phá luôn projected input | Đã có PT-PERM/NULL-PERM; gây nhiễu lớn | Không ưu tiên |
| C. Global orthogonal rotation trong nullspace(P) | Model nhạy hướng tọa độ phần dư không? | Giữ per-row norms, pairwise distances, spectrum | Giữ lại quan hệ ngữ nghĩa tương đối; chỉ kiểm *basis sensitivity* | Đối chứng phụ, không thay A |
| D. Lexical semantic probe trên donor frozen | Độ tương đồng ngữ nghĩa vượt control task không? | Tập cặp từ/synonym ngoài TRAIN, đối chứng chữ/tần suất, probe rất nhỏ | Rẻ, không đòi forward LM; không chứng minh tác dụng NLL | Hỗ trợ A ở giai đoạn CPU |
| E. Donor hoàn toàn khác hoặc untrained donor | Lợi ích đến từ pretrained weights hay nguồn hình học cụ thể? | Cùng tokenizer mapping/Ridge/norm, nguồn và training budget matched | Có thể confound giữa các pretrained corpus, phân phối và norm | Để nghiên cứu riêng sau |

**Ưu tiên khoa học:** Chọn A kèm kiểm tra D bằng CPU. Không chọn B như một lần khẳng định mới vì chính nó đã xuất hiện trong SEMANTIC4X3. C là negative/control về hướng basis (không phá semantic topology) và có thể bổ sung nếu thiết kế A thiếu khả năng định danh.

## 4. Dự thảo thao tác kỹ thuật A: giữ projected input và norm của từng token

Cho `X ∈ R^(n×512)`, `P ∈ R^(256×512)`, `n=1917`, assume `rank(P)=256`. Tách trực giao:
`X_parallel = X P^T (P P^T)^(-1) P`, `R = X-X_parallel`, kiểm `R P^T≈0`.

Đề xuất dựng đối chứng `X_mix,i = X_parallel,i + ||R_i|| · R_{π(i)}/||R_{π(i)}||`, với `π` là hoán vị xác định seed trong các strata ghép cặp **chỉ bằng thông tin TRAIN**: frequency bin, số byte/mảnh BPE, độ dài/case/nhóm hình thái, residual-norm bin; nếu có nhãn semantic đáng tin, áp dụng semantic-disjoint pair trên tập eligible được đóng băng trước đo NLL.

Hệ quả toán học nếu `R_{π(i)}` thuộc đúng nullspace:
- `X_mix P^T = X_real P^T` tới tolerance số học;
- `||X_mix,i|| = ||X_real,i||` cho **mỗi token**, không chỉ quantile;
- Nhưng covariance, mean, pairwise distances và higher-order moments **không được bảo đảm bằng phép dựng này**: phải đo và khóa ngưỡng sai khác sau **CPU feasibility** trước khi dùng loss/dữ liệu đánh giá. Nếu không thể khớp đồng thời, kết luận là `HOLD_GEOMETRY_MATCH_INFEASIBLE`, **không** gán nhãn cô lập ngữ nghĩa.

Những token rỗng, residual norm bằng 0, fallback 131 token không mapped, token nhiều nghĩa hoặc không có lexical anchor phải được xác định và xử lý theo quy tắc trước NLL; không được lựa chọn thủ công sau xem loss. Semantic corruption phải có kiểm chứng thực tế (ví dụ semantic probe/control task) và kiểm tra `π` derangement; không chỉ đổi tên một phép hoán vị tùy ý.

**Phương án có giá trị nhưng không đủ để nhận causal semantic:** nếu hai arm khác nhau và norm/projection matched nhưng covariance chênh lớn, chỉ có evidence về *token residual reassignment under partially matched geometry*, không có evidence tách semantics khỏi geometry. Phải giữ đúng giới hạn claim.

## 5. Lộ trình nghiên cứu mới, chi phí thấp

**A0 — CPU chỉ đọc và feasibility, chưa model forward, chưa claim** (đề xuất bước tiếp theo):

- Kiểm nguyên vẹn nguồn donor 1.917 valid rows, T1 token strings, Ridge `P`, checkpoint L0020; phân loại token lexical vs subword, nguồn lexical labels, rights, mức độ phủ từ vựng; không đọc lại OOD256 per-document loss cho thiết kế.
- Đo rank, numerical nullspace, residual norm, tần suất TRAIN, covariance và khả năng tạo hoán vị có ý nghĩa; thử **synthetic CPU fixture** trước khi xử lý donor thật; source READONLY, chỉ tạo bản kê thống kê trong nhánh nghiên cứu **mới**, không làm thay đổi checkpoint/donor frozen.
- Predeclare ngưỡng feasibility hoàn toàn dựa trên hình học/lexical TRAIN-only. Nếu không đạt ghép cặp tin cậy hay không đủ semantic anchors, `HOLD`; không tự thay đổi ngưỡng sau khi nhìn OOD NLL.
- Trình quyết định cuối `A0_FEASIBILITY_PASS/HOLD` và bản prereg mới. Đây không phải micro-permit khoa học, chỉ một cổng nghiên cứu kỹ thuật tích hợp.

**A1 — Mini pilot nếu A0 đủ điều kiện và owner phê duyệt nghiên cứu mới:**

- Dùng **ba arm**: `PT-REAL` (donor đúng token), `PT-RESIDUAL-MATCHED-SHUFFLE` (đối chứng A), `NULL-REAL` (negative baseline frozen logic). Giữ input coverage, tokenizer T1, base checkpoint, optimizer, schedule, seeds, số bước và ngân sách token bằng nhau.
- **Thiết kế dự kiến (chưa đóng băng):** 3 seed × 3 arm × 512 bước × 4.096 labels = **18.874.368 target-token presentations**, khoảng 18,75% ngân sách `12×2048×4096` của SEMANTIC4X3; Colab T4, lưu checkpoints/receipts vào Drive, không train trên máy dev Windows.
- A1 chỉ **khả thi/thăm dò (feasibility/pilot)**. Nếu muốn kết luận confirmatory, khóa một thiết kế A2 riêng có dữ liệu đánh giá mới và độc lập, không tái sử dụng OOD256 và không lựa chọn giả thuyết theo test đã tiêu thụ.
- OOD256 và H768 cũ đã được nhìn thấy và không thể biến thành xác nhận mới cho A1/A2. Cần nguồn DEV/TEST mới và kiểm tra overlap độc lập trước CLAIM; việc donor đã pretrain trên nguồn nào vẫn phải ghi `UNKNOWN` nếu không chứng minh được.

**A2 — Confirmatory mới:** chỉ mở khi A1 cho thấy tính khả thi và khả năng định danh, có prereg trước scoring mới, kiểm soát nhiều seed và bootstrap theo đơn vị bài, phân xử độc lập PASS/FAIL trên **bộ dữ liệu mới**, không đổi L0020/L0021. Không mặc định 3 seed đủ cho suy rộng seed-population.

## 6. Ma trận quyết định — không trộn QA với science

| Cổng | Ngưỡng quyết định | Trạng thái |
|---|---|---|
| OOD256 khoa học | Co-primary 2/2 và 3/3 seed dương, independent receipts | **CLOSED_PASS_SCOPED** |
| Source/Drive/lineage | SHA 12 checkpoint, 3 seal, 4 receipts, báo cáo phân xử, L0021 append-only | **PINNED_CONTENT_ADDRESSED** |
| Câu hỏi causal semantics đã được chứng minh? | Tách token semantics khỏi geometry matched | **NO** |
| Câu hỏi mới có đáng làm? | OOD transport PASS nhưng row-norm & morphology confound chưa loại trừ | **HIGH_PRIORITY_CONDITIONAL** |
| A0 CPU feasibility | Đối chứng token remap bảo toàn phép chiếu, norm, độ phủ lexical và kiểm geometry mismatch | **NOT_EXECUTED** |
| A1/A2 GPU training | Owner permit mới, prereg riêng, dataset mới, source QA | **NOT_AUTHORIZED** |
| GGUF/application | Không mở trong nhánh khoa học này | **NOT_OPENED** |

## 7. Quyết định

**Đóng** OOD256 ở `PASS_SCOPED_OOD_RESIDUAL_TRANSPORT`, chỉ dùng làm **lý do ưu tiên** nghiên cứu mới; không lấy các giá trị OOD làm ngưỡng đích huấn luyện. **Ưu tiên A0 CPU feasibility** cho thiết kế geometry-aware matched residual assignment. Không nên chi ngân sách T4 trước khi chứng minh được đối chứng có thể giữ đúng phép chiếu, norm, đủ lexical coverage và không gây chênh hình học lớn. Nếu A0 không khả thi, chuyển về `HOLD` và xét alternative (C hoặc control-task D), không tuyên bố semantic causality.

**Bước thực hiện tiếp theo:** `TTM_GEMMA2_SEMANTICS_VS_GEOMETRY_A0_CPU_MATCHED_RESIDUAL_FEASIBILITY_SOURCE_AUDIT_AND_DRAFT_PREREG`. Một lượt CPU QA tích hợp **design/feasibility only**, trên nhánh nghiên cứu riêng, không động bất kỳ science result đã khóa; chỉ sau đó trình đúng một quyết định về pilot T4.
