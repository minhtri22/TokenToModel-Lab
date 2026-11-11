# TTM-Small-4M O0 — Rà soát gộp độ bao phủ dữ liệu, mục tiêu học và năng lực biểu diễn

**Ngày:** 2026-11-11 · **Operation:** `TTM_SMALL4M_ORIGINAL_O0_DATA_COVERAGE_OBJECTIVE_AND_CAPACITY_CAUSAL_GAP_RESEARCH_DESIGN_ONLY`  
**Phạm vi ghi duy nhất:** `research/ttm-small4m-post-cf1-language-fresh-gap-reconcile-20261111`.  
**Chế độ:** `SOURCE_AND_HISTORICAL_EVIDENCE_RECONCILIATION_ONLY`, không đọc private TRAIN/VAL/TEST, không chạy lại kiểm thử nguồn đã PASS, không tạo toy, không huấn luyện hoặc suy luận; không can thiệp agent FRESH16 hoặc agent AC.  
**Phán quyết:** `GO_DESIGN_ONLY_ONE_O0_DEVELOPMENT_DIRECTION=OBJECTIVE_SIGNAL_ALLOCATION_C_MINUS_A` · `SCIENCE_EXECUTION=HOLD`.

## 1. Nhận diện chính xác mô hình nghiên cứu O0

Mô hình đã huấn luyện T4 là P02 decoder-only Transformer, **3.749.376 tham số duy nhất**, BPE vocab **2.048**, ngữ cảnh **256**, embedding ẩn **256**, **4 block Transformer**, **4 attention head**, LayerNorm, embeddings token/output-head dùng chung trọng số (tied embeddings), learned absolute position embeddings. Mã P02 là `src/p02/transformer_core.py`, Git blob `9762343e06cf800b50574c2871ae1ed58537fb18`. Cấu hình `configs/p02_transformer_core_bpe2048.json` (max_len64, emb64, layer2) là **cấu hình ứng viên correctness P02 cũ**, không phải cấu hình checkpoint T4 thật. Cấu hình khoa học T4 tại `tools/pilot_t4/integrated/T4_PREREG_INTEGRATED_CANDIDATE_20261108.json`, Git blob `3ab7a439f79594e02c7598b1e5dca7168b923bcc`.

Mô hình **không có** bộ nhớ qua các cửa sổ độc lập hoặc head chuyên giám sát thực thể/trạng thái/mục tiêu. Tuy vậy không có đối chứng công bằng nào chứng minh chính 3,75M tham số hay bốn lớp gây thất bại chất lượng. Vì những prompt đánh giá ngắn vẫn nằm trong 256 token, không được viện cớ độ dài ngữ cảnh tại **lúc suy luận** làm nguyên nhân duy nhất.

## 2. Độ bao phủ TRAIN — quan sát thực, suy luận có điều kiện

Nguồn kỹ thuật đã QA độc lập: `evidence/pilot/t4-privatepack/T4_PRIVATE_PACK_AND_CAPACITY_INDEPENDENT_QA.json`, blob `2c8cf014260d7ef75e68b1c3223d9c54536fec71`. T1 lấy 2.048 truyện TRAIN được chọn theo hash từ TinyStories, 256 truyện VAL và 64 TEST niêm phong; BPE-2048 fit trên **768 truyện TRAIN**, không phải toàn 2.048 truyện.

| Đại lượng | Đã xác minh | Ý nghĩa và giới hạn |
|---|---:|---|
| TRAIN stories | 2.048 | Một tiểu tập TinyStories, không phải đầy đủ corpus; chưa đo tính đa dạng nhân quả |
| TRAIN windows | 2.691 | Trung bình 1,314 cửa sổ/truyện; cửa sổ có độ dài không đều |
| Valid next-token target positions | 498.287 | Số **vị trí nhãn riêng** trong pack, không phải từ vựng duy nhất |
| Full windows | 652/2.691 = 24,23% | 2.039 cửa sổ còn lại ngắn hơn 256 nhãn |
| Mean valid labels/window | 185,168 | Chính sách lấy mẫu cửa sổ có độ dài không đồng nhất |
| T4 training label presentations | 1.024 × 4.096 = 4.194.304 | Đúng ngân sách, lặp **trung bình 8,417×** theo số vị trí nhãn |
| VAL | 256 truyện, 328 cửa sổ, 61.122 nhãn | Đã dùng cho NLL; không mở hoặc chọn model bằng TEST |

Mã pack `tools/pilot_t4/integrated/t4_data_pack.py`, blob `cdce219f2a2df27e25579f069238d4327c1d7d91`: `windows_for_ids` dùng bước nhảy đúng 256 nhãn, tạo cửa sổ **không chồng lấn**; tổng nhãn được chấm mỗi truyện được giữ nguyên. Ngữ cảnh sớm hơn ranh giới cửa sổ không được đưa sang cửa sổ tiếp theo; embedding vị trí bắt đầu từ 0 cho mỗi đoạn. Với truyện dài, đây là một **cơ chế khả dĩ** làm giảm tín hiệu liên kết sự kiện cách xa hơn một đoạn, không phải bằng chứng trực tiếp rằng chính nó gây điểm tiếp nối thấp.

Mã training khoa học `tools/pilot_t4/a2_continuous1024/t4_train_science_a2.py`, blob `76c4d0155cd0736919f41682f240b47ad3d7c428`: chọn một index cửa sổ bằng `torch.randint(len(x))` với thay thế cho đến đủ 4.096 nhãn hợp lệ/bước, cắt phần nhãn cuối cùng ở bước draw cuối để khớp budget. **Không có histogram truy vết từng cửa sổ/truyện đã thực sự được lấy**, cũng không có chỉ số bao phủ vai trò, goal, chuyển trạng thái theo nội dung. Không được suy từ 8,417× trung bình rằng mọi token, mọi truyện và mọi quan hệ đã xuất hiện đúng 8,417 lần hoặc mô hình đã học đủ.

**Điểm không thể đồng nhất:** `exposure` của token khác `coverage` ngữ cảnh và `learning` ngữ nghĩa. 2.691 cửa sổ có thể lặp mạnh nhưng vẫn thiếu các chuyển trạng thái quan trọng xuyên đoạn; ngược lại, với nhiều truyện ngắn, cửa sổ không chồng lấn có thể đã chứa đủ câu chuyện. Cả hai khả năng còn mở.

## 3. Bằng chứng hiệu quả học O0 — các mục tiêu khác nhau

- T4 bước 1.024: VAL NLL model **3,522338851682218**, TRAIN-only bigram **3,9972314169551506**, giảm tương đối **11,880537%**, story-bootstrap 95% lợi thế tuyệt đối **[0,45818675, 0,49406158]**. Biên bản khoa học độc lập `evidence/pilot/t4-science/T4_A2_FINAL_INDEPENDENT_SCIENCE_ADJUDICATION.json`, blob `84cb94647c403ea358d8c991090bf56adc11f128`; `PASS_H1_CONFIRMATORY_VAL_SCOPE`.
- Bước 1.024→1.280 lịch sử: VAL NLL 3,522339→3,498089 nhưng điểm bám prompt ở đánh giá nhỏ 0,375→0,375 (0–3), **không đạt** cổng cải thiện chất lượng. Đây là dấu hiệu các mục tiêu có thể lệch, **không** chứng minh huấn luyện thêm luôn vô ích.
- Kết quả FRESH12/CF1 lịch sử có giới hạn cấu trúc, người chấm và confound riêng. Không đối chiếu raw output, không chấm lại, và **không thao tác công việc của agent FRESH16**.
- Loss TRAIN một minibatch (ngay cả bước 1.024) và NLL VAL toàn tập là những thống kê khác nhau; không được dùng hiệu số của chúng làm định lượng overfitting chuẩn khi chưa có Train-NLL trên phân phối đánh giá khớp. Một seed và pilot nhỏ không cho phép xác định trần năng lực mô hình.

**Phán xử:** `LEARNED_TOKEN_DISTRIBUTION=SUPPORTED_VAL_SCOPE`; `NARRATIVE_CONDITIONING_CAUSAL_MECHANISM=NOT_IDENTIFIED`; `OVERFITTING=NOT_ESTABLISHED`; `ARCHITECTURAL_CAPACITY_CEILING=NOT_ESTABLISHED`.

## 4. Cross-Entropy và phạm vi can thiệp thật sự

T4 tối ưu `sum CE(valid target tokens) / 4096` trên mỗi bước, không có nhãn hành động/trạng thái/goal tách biệt. **Không có gì trong CE ngăn mô hình học ngữ nghĩa**, nhưng CE không cấp trọng số trực tiếp cho việc hoàn thành mục tiêu câu chuyện; các lỗi semantic không được phạt bổ sung ngoài negative log-likelihood token tham chiếu. Mệnh đề “CE không thể học reasoning” là sai về mặt suy diễn; mệnh đề đúng là *chưa chứng minh CE + dữ liệu/budget O0 đủ cho yêu cầu bám ngữ cảnh*.

Nguồn can thiệp hiện hữu trong AC: `tools/pilot_t4/prompt_conditioning_2x2/ttm_2x2_colab_runner_candidate.py`, blob `6c87e388da4d4a2b94dffba655861a390dfad73c`, hàm `loss_step`. Arm A loss đều; arm C trọng số 1 cho vị trí 0–31 và 3 cho vị trí ≥32. C **chuẩn hóa theo tổng trọng số hợp lệ**, nên không đơn thuần nhân ba toàn loss; can thiệp thực chất là tái phân bổ đóng góp gradient theo vị trí. A/C dùng cùng lịch lấy mẫu gốc, checkpoint/optimizer khởi tạo từ cùng parent và 128 bước × 4.096 nhãn/arm trong thiết kế; chưa có huấn luyện khoa học mới.

Vì vậy `C−A` có tính phân biệt khá tốt cho **lợi ích của suffix-position weighting trong phạm vi O0**. Nó **không** nhận dạng được: tác động thay corpus, sự có mặt của tín hiệu riêng về thực thể, kỹ năng reasoning, hay việc tăng độ dài context. Ngay cả nếu C cải thiện, không được suy rằng vị trí token ≥32 luôn tương ứng sự kiện quan trọng; đó là proxy, không phải nhãn semantic. FINAL24 của AC là phép đo riêng với so sánh mù, không phải FRESH16/TEST/Q1Q2.

Thiết kế 2×2 hiện hữu (`TTM_SMALL4M_EQUAL_BUDGET_2X2_DESIGN_CANDIDATE_20261110.json`, blob `6f8553e7054078d449bad6b2979c3b07d392eb48`): `B−A` đo **chính sách thay cửa sổ bằng cửa sổ đầu truyện**; `D−C` đo tương tự khi đã đổi loss; `(D−B)−(C−A)` là tương tác. B/D chưa được phép huấn luyện. Đặc biệt **B−A không kiểm tra trực tiếp chữa đứt ngữ cảnh xuyên cửa sổ**, không tăng kích thước corpus và có thể đồng thời đổi phân phối nội dung/vị trí; không gọi đó là một phép thử cô lập “data quality” tổng quát.

## 5. Xếp hạng giả thuyết — thứ hạng ưu tiên kiểm chứng, không phải xác suất đúng

| Thứ hạng kiểm chứng | Giả thuyết | Bằng chứng hiện tại | Độ phân biệt bằng thiết kế đã có | Kết luận |
|---|---|---|---|---|
| **1** | **H_OBJECTIVE_SIGNAL:** phân bổ trọng số loss chưa phù hợp cho tiếp nối sự kiện/goal | CE đều là sự thật nguồn; chất lượng sinh yếu dù NLL VAL PASS, nhưng chỉ tương quan | **C−A**: so sánh có kiểm soát, A/C đã có mã và FINAL24 | **Ưu tiên phát triển/đánh giá cao nhất**; giả thuyết chưa xác nhận |
| **2** | **H_DATA_WINDOW:** lựa chọn/cắt cửa sổ làm tín hiệu diễn biến thiếu hoặc không cân đối | Không chồng lấn 256, 2.691 windows, 24,23% full được kiểm trực tiếp | B−A chỉ đo first-window selection, **không tách riêng vấn đề mất ngữ cảnh** | Rủi ro cấu trúc nổi bật; thiếu phép đo hiệu ứng trực tiếp |
| **3** | **H_DATA_DIVERSITY:** 2.048 truyện và BPE fit 768 truyện không đủ đa dạng semantic | Quy mô và số lượt lặp 8,417× được kiểm; không có thống kê semantic coverage | 2×2 hiện hữu **không** so corpus lớn/nhỏ với budget tương đương | Chưa được phép kết luận thiếu dữ liệu là nguyên nhân |
| **4** | **H_CAPACITY_CONTEXT:** 3,75M/4 lớp/ctx256 giới hạn biểu diễn | Cấu hình được kiểm; prompt ngắn vẫn nằm trong context | Không có so sánh tham số/context giữ data, objective, budget | Hợp lý nhưng không có nhận dạng nhân quả |
| **5** | **H_OPTIMIZATION_TOKENIZER:** số bước hoặc BPE2048/giao thức prompt gây giới hạn | VAL NLL tiếp tục giảm ở bước 1.280; đã có tín hiệu format ảnh hưởng token đầu | Không có đối chứng cô lập cùng đánh giá chất lượng | Không chọn huấn luyện thêm, thay BPE hoặc đổi inference để quy nguyên nhân |

Xếp hạng dựa trên **giá trị thông tin của đối chứng và mức sẵn sàng nguồn**, không phải phỏng đoán phần trăm trách nhiệm của từng nguyên nhân. Lỗi cấu trúc có thể quan trọng hơn H1 nhưng chưa thể xác nhận bằng đúng thiết kế A/C.

## 6. Một hướng phát triển O0 được chọn

**Chọn duy nhất:** `O0_SAME_ARCH_OBJECTIVE_SIGNAL_ALLOCATION_AS_AC_C_MINUS_A` — **giữ nguyên kiến trúc gốc, tokenizer, checkpoint nguồn và dữ liệu; kiểm tra ảnh hưởng tái phân bổ tín hiệu loss theo vị trí thông qua đối chứng A/C đã có.**

**Vì sao chọn hướng này thay cho tăng model hoặc thêm dữ liệu ngay:**
1. `C−A` là một can thiệp nhỏ, hiện thực hóa sẵn và có đối chứng cùng lịch draw; kết quả có giá trị phân biệt nhân quả về **vị trí loss** hơn việc nhìn checkpoint 1.024/1.280 hoặc so bộ prompt khác nhau.
2. Nó không biến đổi corpus, số tham số, tokenizer/context, nên không nhân thêm confound; không cần đề xuất toy/bộ prompt/mô hình hay nhánh mới.
3. Nếu loss-position weighting không cải thiện adherence theo **cổng AC riêng đã khóa**, đó là kết quả âm tính về can thiệp **này**, không bác bỏ tất cả mục tiêu học khác và không chứng minh thiếu dữ liệu. Nếu C có lợi tương đối nhưng absolute score còn thấp, chỉ ghi hiệu ứng tương đối, **không** tuyên bố O0 đã đáp ứng nhu cầu sinh truyện.
4. Các vấn đề data-window/semantic coverage cần được giữ trong mục giả thuyết hậu nghiệm, không đổi can thiệp đồng thời trong A/C. Đối chứng B−A chỉ xét sau quyết định chủ dự án riêng, không nằm trong đường thực thi này.

**Phân định trách nhiệm:** Agent AC sở hữu triển khai A/C và tiền kiểm; nhánh hậu CF1 chỉ giám sát lập luận khoa học và nhận **số liệu tổng hợp đã phân xử** (khi có). Không thay agent FRESH16; không tự đăng kết quả AC hoặc cấp science GO từ nhánh hậu CF1.

**Quyết định:** `GO_OBJECTIVE_SIGNAL_DESIGN_DIRECTION`; `HOLD_NEW_TRAINING`, bởi AC vẫn `NO_GO_PREEXEC` (owner rights, private key custody, independent rater, Windows Py312 native V2, T4 zero-step + actual interrupted resume parity chưa đầy đủ). Không tái chạy các kiểm nguồn đã PASS.

## 7. Quy tắc đánh giá sau này, không tạo permit mới

Khi và chỉ khi AC đã có phân xử khoa học riêng: đối chiếu `C−A` bằng FINAL24 và VAL guard của AC theo ngưỡng đã khóa, kiểm số liệu tuyệt đối và tương đối, kiểm giảm chất lượng ngôn ngữ. Giữ phân biệt ba kết quả:
- `C−A > 0` và đạt các cổng đã khóa: có bằng chứng hiệu ứng **can thiệp loss này**, không kết luận dữ liệu hoặc năng lực reasoning phổ quát;
- `C−A ≈ 0` hoặc FAIL: không chứng minh mọi dạng thay objective đều vô hiệu;
- `AC=NOT_EXECUTED/HOLD`: không được ghi là kết quả âm tính khoa học.

**Không** sử dụng FRESH16, CF1, TEST, Q1Q2, FRESH12 để điều chỉnh post-hoc lịch train, ngưỡng AC hay so chéo các bộ prompt. Không tự mở B/D hoặc O1.

## 8. Chứng cứ nguồn và bảo toàn

- Nhánh hậu CF1 trước bước: `c8eb5cd847c98ccc3212a10b54d5e2bf78f94355`.
- `main` trước bước: `5d52e32f20021e36f08f284ef9864d3ba36dbead`.
- AC source HEAD: `837289fda82b41653a61b74e476f76a0b4c4137c`.
- Checkpoint nguồn bước 1.024 SHA256 `cb985751795c8328ad65acf7ca4c1033ce35182c1bfbdb8c38550de629cb271b`, private TRAIN/VAL pack SHA256 `184f68b4c0c800ef3e98362c2e20e1cd35baa269e926489a475664526ecd9913`.
- Tất cả thống kê trong báo cáo lấy từ **biên nhận nguồn đã PASS**, không đọc raw corpus/TEST, không tính lại QA, không huấn luyện/inference, không thay ngưỡng/prereg/checkpoint/source.
- Không sửa `main`, `lineage.md`, PR13 DRAFT, không merge, không dọn worktrees hoặc đọc private key.
- Đây là kết quả phân tích thiết kế, **không** là khoa học PASS/FAIL mới để ghi `lineage.md`.

## 9. Bước thực hiện tiếp theo

`TTM_SMALL4M_ORIGINAL_O0_OBJECTIVE_SIGNAL_AC_RESULT_ONLY_CAUSAL_DECISION_READBACK`

Khi agent AC có biên bản kết quả **đã phân xử** hoặc có quyết định HOLD cuối của gói hiện hữu, chỉ đọc lại để phân biệt tác động `C−A` (loss) với dữ liệu và giới hạn kiến trúc. Nếu AC chưa chạy, nhánh hậu CF1 giữ `HOLD` và không cần làm gì thêm; tuyệt đối không mở các vòng micro-permit hoặc xây toy để thay thế bằng chứng.

**Trạng thái cuối:** `O0_ORIGINAL_SOURCE=PINNED` · `T4_VAL_H1=PASS` · `DATA_WINDOW_MECHANISM=STRUCTURAL_RISK_NOT_PROVEN_CAUSE` · `OBJECTIVE_POSITION_WEIGHT_HYPOTHESIS=FIRST_TEST_PRIORITY` · `CAPACITY_CEILING=UNPROVEN` · `AC=NO_GO_PREEXEC` · `B/D=DEFER` · `O1=DEFER` · `NO_NEW_TRAINING` · `NO_GPU` · `TEST_Q1Q2=UNTOUCHED` · `MAIN/LINEAGE=UNMODIFIED`.
