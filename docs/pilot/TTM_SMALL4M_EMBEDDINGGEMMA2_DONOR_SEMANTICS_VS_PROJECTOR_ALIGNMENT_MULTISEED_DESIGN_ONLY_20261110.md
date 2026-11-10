# TTM-Small-4M × EmbeddingGemma 2 — Thiết kế phân biệt donor semantics và projector alignment, xác nhận đa seed

**Ngày:** 10/11/2026 · **Operation:** `TTM_SMALL4M_EMBEDDINGGEMMA2_DONOR_SEMANTICS_VS_PROJECTOR_ALIGNMENT_REPLICATION_DESIGN_ONLY`.
**Quyết định:** `GO_TO_INTEGRATED_CONTRACT_REVIEW_DESIGN_ONLY` — **chưa tiền đăng ký hợp đồng thực thi, chưa cấp GPU, chưa CLAIM, chưa huấn luyện, chưa chọn H768, chưa sửa `lineage.md`**.

## 1. Vấn đề khoa học và ranh giới bằng chứng

L0017: direct-swap C2048 vượt A/B/D trên 320 truyện mới; L0018: zero-gate residual 32 bước không vượt donor hoán vị, scoped FAIL; L0019: trên H512 mới (512 truyện, 651 cửa sổ, 119.856 nhãn), sáu nhánh CAUSAL6 đã phân xử `PASS_SCOPED_DONOR_MAPPING_ALIGNMENT`. PRIMARY `tau_D=NLL(RP-F)-NLL(RR-F)=+0.0785658100`, paired story bootstrap CI95 `[+0.0709965265,+0.0863988495]` (2.000 mẫu). Các mốc đã khóa giữ nguyên, không STOP direct-swap vì kết quả 64 bước cũ.

**Lỗ hổng nhận dạng:** trong CAUSAL6, projector Ridge được fit từ **1.917 cặp token donor-embedding TTM chính xác** rồi dùng chung ma trận cho real và permuted. Kiểm soát multiset/optimizer tốt, nhưng fit real đã đưa tri thức token correspondence của TTM vào projector; vì vậy không quy toàn bộ `tau_D` cho riêng nội dung ngữ nghĩa donor tiền huấn luyện. Hơn nữa 1 training seed, same-family TinyStories-valid và chưa có no-donor train-matched baseline.

**Câu hỏi tiếp theo có thể bác bỏ:** nếu cho donor đã tiền huấn luyện và một donor giả lập không có quan hệ ngữ nghĩa đã học **cùng quyền fit projector vào TTM theo token neo**, liệu lợi thế của gán đúng token trong donor thật có vượt phần tương tự của donor giả lập, và có lặp lại ở ba seed cố định không?

## 2. Ma trận đối chứng 2×2 — đề xuất duy nhất

| Mã nhánh | Donor frozen | Gán hàng token | Projector Ridge 512→256 | Transformer/Head |
|---|---|---|---|---|
| **PT-REAL** | EmbeddingGemma 2 pretrained thật | Đúng token | **Fit độc lập** trên 1.438 anchors đúng token | Huấn luyện toàn phần như F |
| **PT-PERM** | Cùng donor thật | Hoán vị trước phép fit | **Fit độc lập** trên cùng 1.438 anchors sau hoán vị | Như PT-REAL |
| **NULL-REAL** | Donor giả lập khớp phổ hình học, không học ngữ nghĩa | Đúng chỉ số token của bảng giả lập | **Fit độc lập** trên cùng 1.438 anchors | Như PT-REAL |
| **NULL-PERM** | Cùng donor giả lập ở cùng seed | Cùng phép hoán vị PT-PERM | **Fit độc lập** trên cùng 1.438 anchors sau hoán vị | Như PT-REAL |

Điểm khác so với CAUSAL6: **không dùng chung projector Ridge fit trên donor thật cho nhánh permuted**. Mỗi nhánh nhận chính xác cùng **quyền truy cập nhãn fit** `E0[token_id]`, cùng số anchor, cùng Ridge λ=0,01 và số chiều, nhưng phép fit chỉ dùng đầu vào donor tương ứng của nhánh. Như vậy thay đổi thực nghiệm là **căn chỉnh có giám sát bằng E0 được cân bằng về quy trình**. Bốn nhánh vẫn là direct-swap; không quay lại GATED32, không resize 512-hidden.

### 2.1 Nguồn donor và giả lập phổ (spectral null)

Donor thật `X_real ∈ R^(1917×512)` là các row đã ánh xạ hợp lệ từ candidate SHA256 `c9fc798d8880c7e76636258052e9885dbb086d7b462a5b6bee5cff8b582973c3`; 130 fragment không đầy đủ + 1 EOS giữ fallback `E0` y hệt mọi arm. Không thay donor tokenizer và không sử dụng contextual embedding hoặc API dịch vụ.

Với `X_c = X_real - mean_row(X_real) = U Σ Vᵀ`, tạo ma trận `U_null` seed-fixed có cột trực chuẩn trong không gian vuông góc vector hằng, rồi lấy `X_null = mean_row(X_real) + U_null Σ Vᵀ`. Điều này khớp **trung bình cột, phổ giá trị kỳ dị, ma trận hiệp phương sai theo cột và tổng năng lượng centered** của nguồn thật, nhưng **không giữ quan hệ token–nghĩa**. Null **không phải checkpoint EmbeddingGemma 2 chưa huấn luyện**, và không đảm bảo phân phối chuẩn từng hàng, hàng xóm ngữ nghĩa hoặc đặc trưng hình thái tương đương. Ghi báo cáo các sai khác này; không đặt nhãn `GEOMETRY_EXACT_MATCH` tùy tiện.

Chọn một phép hoán vị không tầm thường trên 1.917 token mapped theo seed cố định, phân tầng tần suất token từ **T1 TRAIN** và số donor subtokens; token fallback tuyệt đối không bị hoán vị. Nhóm singleton phải được gộp/định nghĩa trước; nếu không đủ khả năng thực thi hoán vị theo hợp đồng thì HOLD trước science, không chọn lại theo kết quả.

### 2.2 Fit Ridge không tiêu thụ dữ liệu chấm

Cố định **1.438 token neo (anchor fit, xấp xỉ 75%)** và **479 token audit holdout** bằng SHA chọn trước theo token ID, frequency band T1 TRAIN, donor-subtoken-count, valid mask; không dùng loss/NLL trên VAL, H320, H512 hoặc H768. Cùng tập anchors trên cả bốn arms và mọi seed. Với mỗi arm, fit:

\[P_a = (X_{a,A}^{\top}X_{a,A}+0.01I)^{-1}X_{a,A}^{\top}E_{0,A},\quad E^{\mathrm{init}}_a(t)=X_a(t)P_a.\]

Không fit Ridge riêng cho các truyện H768. Không thêm bias/cổng/alpha mới. Sau fit, kiểm chuẩn, cosine, Gram-spectrum, RMSE/cosine trên anchor và 479 token chưa fit; kiểm cả unigram frequency và mapped coverage. **Phải báo cáo chênh lệch độ fit giữa 4 arms** trước khi diễn giải hậu nghiệm. Quy trình có cùng giám sát, nhưng không giả định có **chất lượng fit bằng nhau**; nếu mất cân bằng hình học lớn, điều kiện suy luận nhân quả phải giới hạn, không đổi seed hoặc hạ tiêu chí sau khi thấy NLL.

## 3. Ước lượng nhân quả và điều kiện bác bỏ

Với `L(a,s)` là NLL theo nhãn trên cùng holdout mới của nhánh `a` tại seed `s`, định nghĩa:

\[\Delta_{\mathrm{pre},s}=L(\mathrm{PT\text{-}PERM},s)-L(\mathrm{PT\text{-}REAL},s)\]
\[\Delta_{\mathrm{null},s}=L(\mathrm{NULL\text{-}PERM},s)-L(\mathrm{NULL\text{-}REAL},s)\]
\[\boxed{\tau_{\mathrm{specific},s}=\Delta_{\mathrm{pre},s}-\Delta_{\mathrm{null},s}}\]

**Đơn vị kết luận đề xuất:** hiệu ứng gán token **đặc hiệu cho cấu trúc donor tiền huấn luyện** so với một donor null khớp phổ, *dưới chính quy trình projector-fit*, không phải `PURE_SEMANTIC_CAUSALITY_PROVED`. `tau_specific>0` cho thấy lợi thế real–perm của donor thật lớn hơn lợi thế tương ứng của null. Đây là difference-in-differences, không dùng chênh lệch một cặp đơn lẻ làm primary.

**Tiêu chí PASS ứng viên cần tiền đăng ký trước run:** tất cả 12 arm chạy đúng nguồn và đủ ngân sách; thẩm định độc lập PASS; **cả ba seed đều có `tau_specific,s > 0`** và **cận dưới CI95 của trung bình ba `tau_specific` >0** trên bootstrap story-paired; chênh lệch hình học/fit được ghi nhận và không vượt giới hạn giải thích đã chốt. Nếu hoàn tất khoa học nhưng không thỏa toàn bộ điều kiện, `PRETRAINING_SPECIFIC_MAPPING_EFFECT_NOT_ESTABLISHED` (scientific scoped FAIL). Nếu dữ liệu, tài nguyên, nguồn, READY hoặc one-shot chưa đủ: HOLD, không gọi FAIL.

**Lưu ý thống kê bắt buộc:** bootstrap lại **cùng 768 story IDs** giữa 12 arm, 2.000 lượt, cùng các chỉ số story; với mỗi lần lấy mẫu, tính `ratio(sum(loss))/sum(target_count)` theo từng arm/seed rồi tính difference-in-differences và trung bình ba seed. Khoảng tin cậy này **có điều kiện trên đúng ba seed đã chọn**; không phải CI95 đại diện cho quần thể seed vô hạn. Đồng nhất giả thuyết chính/chiều dấu và điều kiện PASS trước run; không kiểm định confirmatory ba contrast phụ.

Secondary (không dùng để chuyển FAIL thành PASS): `Δ_pre`, `Δ_null`, NLL từng arm, cosine/RMSE projector trên 479 token chưa fit, spectral/row-norm residual, lớp token 1 donor subtoken so với nhiều donor subtokens, lỗi theo tần suất TRAIN. Đề nghị bổ sung thước đo lexical semantic-neighbor từ một nguồn có quyền và pin trước run như một kiểm tra cơ chế độc lập với NLL, nhưng chưa chọn/tiêu thụ nguồn đó trong design-only.

## 4. Nhiều seed, ngân sách ứng viên, dữ liệu mới

| Quy định | Thiết kế đề xuất (chưa được phép chạy) |
|---|---|
| Seeds adaptation | 3 seed cố định **ứng viên**: `2026111101`, `2026111102`, `2026111103` |
| Các arms | 4 arms mỗi seed; 12 lượt training tất cả |
| Base | Cùng TTM checkpoint T4 step1024, hidden256, vocab2048, context256, 4 blocks/heads, untied head |
| Train | Mỗi arm **2048 steps × 4096 nhãn**; tổng **100.663.296 lượt nhãn**, gấp 2 CAUSAL6 |
| Dữ liệu TRAIN | T4 TRAIN 2048 truyện / 2691 windows; cùng packet schedule *trong một seed* cho 4 arms; seeds khác nhau sử dụng schedule khác cố định trước run |
| Optimizer | AdamW mới mỗi arm, lr `1e-4`, betas `(0.9,0.95)`, eps `1e-8`, wd `0.1`, clip `1.0`; FP32, micro ≤8 như CAUSAL6 |
| Donor / masks | 1917 mapped frozen donor rows; 131 fallback như nguồn; projector+Transformer/head trainable cùng mặt nạ trên bốn arms |
| Null + permutation | Cùng một `X_null` và π trong cặp seed; donor null khác theo seed, seed khởi tạo/projector/schedule ghim trước run |
| Holdout **H768_NEW** | **768 truyện chưa tiêu thụ** từ nguồn TinyStories-valid đã pin, cùng cửa sổ/nhãn và story bootstrap cho 12 arms |
| QA | Independent per-story NLL/bootstrap without model rerun; exact source/model/READY SHA and one-shot claim guards |
| Execution (tương lai) | Google Colab Free T4 một arm tại một thời điểm; checkpoint đầy đủ model/optimizer/RNG/cursor/READY mỗi 256 bước; 3 RunID khoa học phân biệt theo seed |

**H768_NEW chỉ là quy tắc thiết kế:** trước CLAIM tương lai phải chọn bằng SHA cố định đã tiền đăng ký, loại khỏi T1 TRAIN/VAL/TEST, L0017 H320 và L0019 H512 theo membership, chống trùng exact; audit shingle 5-gram Jaccard ngưỡng 0,85 giữa H768 và TRAIN/VAL/H768 nội bộ. Không mở lại nội dung L0017/L0019 hoặc TEST; near duplicate với các tập đó chưa được loại bằng text thì phải công bố giới hạn. Không chấm NLL trên H768 trước khi cả 12 arms FINAL READY; không dùng H768 để chỉnh LR, seed, checkpoint, hyperparameter hoặc chọn donor surrogate. Đây vẫn là TinyStories-valid **in-domain**, không thay cho kiểm định miền độc lập/đối chiếu donor pretraining.

**Tài nguyên:** ngân sách gấp đôi CAUSAL6 và Free T4 không được đảm bảo; không tự giảm số bước, thay GPU trả phí hoặc đổi số seed để cứu run. Một hợp đồng thực thi tích hợp tiếp theo phải khóa các seed cụ thể, metadata khóa nguồn dữ liệu, quota Drive trước claim, quyền dữ liệu, lỗi/gián đoạn, nguồn runner, các chẩn đoán hình học và điểm STOP. Không mở nhiều cổng cấp phép kỹ thuật nhỏ. Mỗi seed phải có CLAIM riêng và READY phục hồi đúng cùng RunID; tuyệt đối không auto-replay nếu đã CLAIM.

## 5. Bất định cơ chế còn lại — không được tuyên bố quá mức

1. **Không đồng nhất ngữ nghĩa và tiền huấn luyện:** lợi ích sau `PT-REAL vs spectral null` có thể bắt nguồn từ tần suất, hình thái, cấu trúc tokenization hoặc phép fit E0, chưa riêng semantic knowledge. Full causal identification của semantically pretrained features cần thêm can thiệp mức pretraining donor hoặc tiêu chí semantic-source độc lập.
2. **Projector fit geometry unequal:** cùng thuật toán/training labels không đảm bảo cùng cosine, RMS, spread logits ở step0. Phải báo cáo và khóa biên độ chênh trước khi nâng luận cứ, không dùng hậu nghiệm để giải thích tùy ý.
3. **Seed hạn chế:** ba lần fine-tuning từ cùng checkpoint/donor chỉ kiểm tính ổn định theo lịch/optimizer và random null, không phải ba donor pretraining độc lập. Một khối ngẫu nhiên cố định theo seed còn làm biến thiên null và train schedule đồng thời; không suy luận population-level significance.
4. **Nguồn H768 cùng miền:** donor pretraining overlap chưa xác minh, cùng TinyStories-valid; phải có OOD holdout có quyền độc lập nếu sau này muốn khẳng định khái quát rộng.
5. **Không có no-donor train-matched baseline trên H768:** không suy đoán absolute improvement so với TTM origin từ phép thử này. L0017 là bằng chứng lịch sử riêng và giữ nguyên.

## 6. Trạng thái quản trị và điều kiện chuyển bước

**Hiện tại:** `DESIGN_ONLY=COMPLETED` · `FACTORIAL_4x3=PROPOSAL` · `PROJECTOR_ANCHOR_SPLIT=NOT_CREATED` · `NULL_GENERATOR=NOT_IMPLEMENTED` · `H768=NOT_SEALED` · `SCIENTIFIC_CLAIM=NOT_CREATED` · `TRAINING=NOT_EXECUTED` · `LINEAGE=L0019_UNCHANGED` · `GGUF=DEFERRED` · `APPLICATION=DEFERRED`.

**Đề xuất quyết định:** `GO` sang **một lượt review hợp đồng tích hợp khoa học và khả thi tài nguyên**, không phải `GO` cho huấn luyện. Phải xác nhận khả năng khớp giả lập spectral null và projector-fit quality, tính nguồn H768, thống kê seed và quyền tài nguyên trước khi phát hành one-shot; nếu không bảo đảm khả năng phân biệt cơ chế thì HOLD và sửa hợp đồng **trước** science.

**Bước thực hiện tiếp theo:** `TTM_SMALL4M_EMBEDDINGGEMMA2_SEMANTIC_FACTORIAL_4X3_INTEGRATED_PREREG_SOURCE_AND_RESOURCE_DECISION` (chỉ khi chủ dự án phê duyệt thiết kế).

### Nguồn khoa học tham khảo (không phải chứng cứ riêng cho TTM)

- Dodge et al. (2020), *Fine-Tuning Pretrained Language Models: Weight Initializations, Data Orders, and Early Stopping* — quan sát độ nhạy seed: https://schwartz-lab-huji.github.io/publication/finetune/
- Grave, Joulin & Berthet (2019), *Unsupervised Alignment of Embeddings with Wasserstein Procrustes* — alignment/hoán vị và điều kiện hình học: https://proceedings.mlr.press/v89/grave19a.html
- Bằng chứng nguồn TTM: `docs/pilot/TTM_GEMMA2_CAUSAL6_SIX_ARM_H512_SCIENTIFIC_ADJUDICATION_20261110.md`, phán quyết L0019 commit `83dac7fc774b93025b5ddc64b5ece18aebdb48c8`.
