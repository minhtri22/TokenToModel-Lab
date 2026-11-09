# TTM-Small-4M — Rà soát TRAIN/VAL 1.024 bước, Q1 partial-5 và phương án REVISE chi phí thấp

**Ngày:** 2026-11-09 · **PR #13** · **Phân loại:** phân tích hậu nghiệm, **không mở huấn luyện hoặc Q1/Q2 V3**. Giá trị khoa học H1 gốc được giữ nguyên.

## 1. Bằng chứng nguyên bản và tính toàn vẹn

- Drive [checkpoint step1024](https://drive.google.com/drive/folders/1pLmIEB595x_cEkez0299C7mI_mV4bMfO) chứa `progress.json` **142.438 byte** có SHA-256 **`5517cc691fc803eaa69db4078f1f3b3ed78f99fa3c012cb17fd8655123c606ec`**, khớp READY và bản kiểm toán khoa học trên GitHub. Đã đọc đủ 1.024 bản ghi liên tiếp: `step=1..1024`, mỗi bản ghi có `exact_scored_targets=4096`.
- Checkpoint **`cb985751795c8328ad65acf7ca4c1033ce35182c1bfbdb8c38550de629cb271b`** cùng READY 4/4 checkpoint được đối chiếu trước đó; không tải lại hoặc thay đổi tệp checkpoint 45 MB. Nguồn dữ liệu TRAIN/VAL riêng tư chỉ xem qua số liệu aggregate đã lưu, không công bố raw stories/tokenized NPZ.
- Cấu hình thực nghiệm gốc: P02 3.749.376 tham số, BPE 2048, context 256, 2.048 TRAIN / 256 VAL / 64 TEST sealed, 1 seed, FP16, AdamW `lr=3e-4`, 32 bước warmup → cosine xuống `3e-5` ở step1024, clipping 1.0, 1.024×4.096 = **4.194.304 target exposures**.
- TRAIN chứa 498.287 vị trí nhãn trong 2.691 cửa sổ; mức reuse trung bình **8,417 lần**. Mẫu TRAIN loss và full VAL NLL có khác biệt thống kê, **không** lấy phép trừ trực tiếp để chứng minh overfitting.

## 2. Dữ liệu đường học gốc — đối chiếu 8 mốc VAL

| Step | TRAIN loss trung bình 64 bước trước đó | VAL NLL | Mức giảm VAL so với mốc trước |
|---:|---:|---:|---:|
| 128 | 4.8910 | 4.582942 | — |
| 256 | 4.1280 | 4.091828 | 0.491114 |
| 384 | 3.8022 | 3.869640 | 0.222187 |
| 512 | 3.6059 | 3.729338 | 0.140302 |
| 640 | 3.4752 | 3.631370 | 0.097968 |
| 768 | 3.3738 | 3.579511 | 0.051859 |
| 896 | 3.3242 | 3.540885 | 0.038626 |
| 1024 | 3.3070 | 3.522339 | 0.018546 |

VAL NLL giảm ở **8/8 điểm đo liên tiếp**. Độ giảm **896→1024 = 0.018546**, bằng khoảng một nửa **768→896 = 0.038626**. Tín hiệu: có cải thiện đến cuối ngân sách, nhưng lợi ích biên đang yếu dần; **không chứng minh** hội tụ hoàn toàn hay overfitting. TRAIN step1 loss 7,677356 → step1024 3,282975; rolling64 cuối 3,306959.

H1 gốc độc lập: VAL model NLL **3,522338851682218**, TRAIN-only bigram **3,9972314169551506**, lợi thế **11,880537%**, story-bootstrap95% của `bigram-model` **[0,45818675; 0,49406158]**. `PASS_H1_CONFIRMATORY_VAL_SCOPE` vẫn đúng. TEST 64 chỉ được phép **trích dẫn** one-shot 2026-11-08: model NLL 3,4835910733, bigram 3,9736037453, +12,3317% mô tả; không đọc/chấm/chọn theo TEST lần nữa.

## 3. Vị trí vấn đề sinh văn bản — không đánh đồng với học token

Q1 V2: 5/48 sinh từ E01/E02, 283 token; Q2 **0/24**. Greedy lặp từ/cụm `big tree`, sampling đa dạng cao nhưng đi lệch Mara/cốc đỏ/cửa sổ hoặc Leo/chiếc tất. Chưa có C01–C04 và K01–K04, chưa có rubric 0–3. Đánh giá đúng là **`WEAK_PROMPT_ADHERENCE_IN_PARTIAL5`**, `QUALITY_NOT_ADJUDICATED`. Kết quả Ollama tương thích PASS không có nghĩa model tốt. T5 strict logits parity F32 đã FAIL 7/8 với max abs ~0,00336, top1 cùng 8/8; giữ lại như **yếu tố nhiễu kỹ thuật chưa định vị**, không khẳng định nó gây ra chất lượng kém.

Cần phân biệt bốn giả thuyết chưa chứng minh: **(a)** cần thêm optimization, **(b)** tập TRAIN 2.048 truyện bị lặp/dữ liệu đa dạng thấp, **(c)** mục tiêu next-token trong TinyStories không đủ để theo dõi thực thể/nguyên nhân khi Q1, **(d)** giới hạn kích thước 3,75M / context256. Không chọn (d) chỉ từ năm đoạn văn.

## 4. Phương án thăm dò REVISE — chi phí thấp, không chạy trong PR này

**Bước A — không GPU, đã hoàn thành:** 1.024 log & 8 mốc VAL có checksum; chưa thấy VAL tăng, nhưng diminishing returns; năm output đã xem, không dùng TEST. Checkpoint 1024 vẫn là đối chứng frozen.

**Bước B — chỉ sau một phê duyệt khoa học riêng (candidate):** một lần **256 optimizer steps** từ **checkpoint step1024 nguyên vẹn**, tổng **1.048.576 target exposures**; new run identifier `ttm_small4m_step1024_to1280_exploratory_v1`, work folder mới trên Drive, không sửa RUN T4 và không viết đè checkpoint. Bắt buộc khôi phục chính xác weights, AdamW, scheduler, sampler, Python/NumPy/torch CPU/CUDA RNG, GradScaler từ READY; SHA check toàn bộ. Giữ nguyên dữ liệu TRAIN/VAL, tokenizer, P02, one seed, FP16, microbatch8, 4.096 target/bước, clip1.0. **LR tiếp tục từ mức sàn 3e-5**: vì `lambda_schedule()` gốc kẹp `t<=1.0` khi step≥1024, có thể dùng scheduler tiếp nối được kiểm tra trạng thái/đếm bước, nhưng trainer A2 gốc có stop ở 1024 và science lock nguyên bản không cho chạy >1024: **phải viết runner successor và science lock mới, không bypass/patch logic chạy cũ**.
- Mốc **1152** chỉ diagnostic, **1280** là primary exploratory preselected; không chọn mốc nào hậu nghiệm theo VAL. Tối đa **256 bước**, một batch duy nhất trên Colab Free T4; không dùng GPU dev, không tự động cấp lại lượt huấn luyện nếu preempt/FAIL; hồi phục chỉ theo READY mới được phê duyệt và cùng RunID.
- Chỉ đánh giá VAL từ 256 truyện cũ; tính `DeltaVAL=NLL_1024-NLL_1280`, bootstrap **paired by story** (1.000 lượt seed20261109) trên cùng tập VAL; báo cáo hiệu ứng và CI, không mang nhãn H1 confirmatory mới. Nếu không có dữ liệu per-story của baseline, cho phép **read-only VAL baseline re-score** từ checkpoint frozen sau khi được phê duyệt, nhưng không sinh Q1/Q2 và không đọc TEST. Không công bố checkpoint/NPZ lên GitHub.
- **Quy tắc phân xử thăm dò đã ghi trước**: (i) `TRAINING_HELPFUL_SIGNAL` khi `DeltaVAL>0` và cận dưới bootstrap paired 95% **>0**, không có lỗi tái lập; (ii) `TRAINING_NOT_CLEARED` nếu NLL không giảm hoặc CI bao gồm 0; (iii) `HOLD` khi không đủ nguồn/QA/kết quả. **Ngay cả (i) cũng không chứng minh cải thiện chất lượng sinh**. Một panel ngắn mới, tự biên soạn, cân bằng nhân vật/nguyên nhân, cần khóa trước khi so chất lượng và **không biến thành Q1/Q2 V3**.
- **Bước C — tùy kết quả, chưa mở:** nếu train loss tiếp tục giảm nhưng VAL không cải thiện, ưu tiên thiết kế dataset diversity/repacking cùng quyền dữ liệu trước khi tăng model size. Nếu VAL cải thiện nhưng sinh chưa mạch lạc, ưu tiên phân tích cách đặt prompt, causal entity tracking và tokenizer/runtime parity; chỉ xem xét thay architecture sau đối chứng data/budget. Tất cả là giả thuyết, không tự động huấn luyện thêm/đổi dataset.

## 5. Quyền thực thi & merge

Không có mã TRAIN successor, science lock mới, CLAIM hay checkpoint 1280 nào được tạo trong bước này. Bộ chạy Q1/Q2 V1/V2 đã HOLD và consumed, **không có V3**. PR #13 là workstream gốc; chỉ thêm biên bản và dữ liệu tổng hợp, `main` và `lineage.md` bất biến. Không dọn model store/Drive hoặc worktree. Không merge PR #13 khi đang HOLD; không tự dùng TEST để quyết định tiếp tục.

**Trạng thái:** `T4_H1=PASS_PRESERVED`; `Q1Q2_V2=HOLD_CONSUMED`; `QUALITY=REVISE_CANDIDATE`; `NEXT_256_STEPS=DESIGN_ONLY_NOT_AUTHORIZED`; `PR13=HOLD`; `MAIN=UNCHANGED`.

**Bước thực hiện tiếp theo:** `TTM_SMALL4M_1024_TO_1280_EXPLORATORY_CONTINUATION_PREREG_SOURCE_READY_REVIEW` — một lượt thiết kế/QA gộp, không khởi động Colab trước khi phê duyệt và đối chiếu HEAD.
