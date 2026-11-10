# TTM-Small-4M — 2×2 Real Metadata, Colab Runner và quyết định khoa học tổng hợp

**Ngày:** 2026-11-10 · **Nhiệm vụ:** `TTM_SMALL4M_2X2_REAL_TRAIN_METADATA_MATCHED_DRAWS_AND_COLAB_RUNNER_QA_PLUS_EVAL_RIGHTS_SINGLE_OWNER_DECISION`  
**Phân xử:** `HOLD_FREE_T4_NOT_AUTHORIZED` · `SCIENCE_NOT_EXECUTED`  
**Nguồn sự thật:** GitHub `minhtri22/TokenToModel-Lab`, nhánh `research/ttm-small4m-prompt-conditioning-objective-design-20261110`.  
**Điểm xuất phát:** `main` `b57b44e7287f842e81050c1faee337f636333dd0`, PR #13 `8399406cfca7855626a20e031d1cfb3c767d606f` — hai refs không ghi thay đổi.  
**Lineage:** main L0012, Git blob `971fbd8eccdf4719fee6b83a3c0f4c44b13ebaa9`; PR #13 L0017, Git blob `15c67ada3b11c46e2d947bef8818599c7408733c`. Không merge lineage hay ghi thêm.

## 1. Kiểm tra metadata TRAIN thật (PASS, chỉ đọc)

Đã kiểm SHA-256 chính xác của private TRAIN/VAL pack `184f68b4c0c800ef3e98362c2e20e1cd35baa269e926489a475664526ecd9913`, manifest `ef2e6e67d49b1d5a921b1051df329f15574f1c10cece0ce49468acb53322d650`, checkpoint `step1024` `cb985751795c8328ad65acf7ca4c1033ce35182c1bfbdb8c38550de629cb271b`. Chỉ dữ liệu tổng hợp và digest mới được đưa lên GitHub; **không công bố token ID, index từng cửa sổ hay nội dung TRAIN**. Pack không chứa TEST, có 2.048 truyện TRAIN/2.691 cửa sổ/498.287 nhãn và 256 truyện VAL/328 cửa sổ/61.122 nhãn.

| Hạng mục | A và C (lấy mẫu gốc) | B và D (first-window) |
|---|---:|---:|
| Bước giả lập metadata | 128 | 128 |
| Nhãn hợp lệ/arm | 524.288 | 524.288 |
| Cửa sổ forward/arm | 2,928 | 2,928 |
| Forward token slots/arm | 749,568 | 749,568 |
| Cửa sổ đầu truyện chọn được | 2,225 | 2,928 |
| Truyện TRAIN khác nhau được chọn | 1,493 | 1,363 |

Mọi `n` từ lịch mẫu lấy **sampler RNG đúng của checkpoint 1024**, phù hợp quy tắc draw 4.096 target/step. Đã tìm đủ ứng viên `first-story window count>=n` cho **tất cả 128 bước**, có 560 cửa sổ đầu truyện đủ 256 nhãn. Lịch A=C và B=D khớp theo các digest: A/C `b4082178bac4c7830645661f31b2ba16a5743d324ac46000b5f9dffc289f4fe3`, B/D `162688091ea4f2331d86205761109216a16991b00f6b0849576524c81b18692a`. Chỉ giống ngân sách token/forward; **đa dạng câu chuyện, gradient weighting và thời gian GPU khác nhau theo thiết kế**. Phân phối B/D chỉ chạm 1.363 truyện khác nhau, so với 1.493 ở A/C; cần báo cáo như một tác động/caveat thực nghiệm.

## 2. Runner 4 arm, CPU QA (PASS có giới hạn)

- Mã `ttm_2x2_colab_runner_candidate.py` xây bốn nhánh A/B/C/D riêng, dùng cùng checkpoint 1024, full AdamW/scheduler/sampler/RNG/GradScaler; baseline CE đồng đều vs C/D CE suffix weight 1:3, chuẩn hóa theo **toàn optimizer step**, không cộng loss microbatch lệch ngân sách; A/C cùng source schedule, B/D cùng replacement schedule.
- Đã kiểm **nạp chính xác model P02 3.749.376 tham số**, AdamW 52 state tensors, scheduler step 1.024, GradScaler 65.536, finite CPU forward logits. `CPU_PARENT_RESTORE=PASS`.
- **42/42 kiểm thử CPU PASS**, gồm trường hợp nguồn/checkpoint SHA sai, khởi động science không có khóa, label sai, loss NaN, mask -100, ngân sách, source pins. Kiểm toán số học chỉ đọc riêng **34/34 PASS**.
- `--mode science` **bị chặn trước khi dùng GPU** nếu thiếu new owner lock có chính runner SHA, rights/eval/reviewer receipts. Đã kiểm negative thực tế. Không dùng khóa của 1024→1280 cho lượt 2×2 này.
- **Giới hạn quan trọng:** chưa chạy trên Tesla T4 FP16; chưa kiểm chứng khả năng khôi phục sau ngắt phiên (runner candidate hiện mới ghi checkpoint cuối arm, chưa có intermediate READY-last/resume test). Do đó `COLAB_RUNNER=SOURCE_CANDIDATE_CPU_ONLY`, không được gọi `T4_RUNNER_PRODUCTION_READY`.

## 3. 36 prompt DEV/FINAL và reviewer

Đã tạo, khóa source JSON 12 **DEV** + 24 **BLIND_FINAL** hoàn toàn mới, Unicode/UTF-8 SHA256 từng prompt, 36/36 BPE2048 roundtrip PASS, dài 23–35 BPE token. Không trùng nguyên văn F01–F12. Không đụng lại Q1/Q2 hoặc TEST gốc để dò trùng, nên **không khẳng định novelty tuyệt đối**. Prompt đã viết theo tình huống nhân vật/đồ vật/mục tiêu; đây là fixture đánh giá, chưa phải dữ liệu train.

Rubric 0–3 bám prompt/mạch lạc/nhất quán, 4-arm Latin square (mỗi arm xuất hiện 6 lần ở mỗi vị trí trong 24 FINAL prompt) và ngưỡng chất lượng kế thừa bản thiết kế, **chưa có reviewer độc lập nào tiếp nhận nhiệm vụ 2×2**, không dùng lại tự động Codex reviewer đã chấm FRESH12. Chưa có key mapping A/B của lượt này hay packet sau sinh, vì chưa chạy science.

## 4. Quyền nguồn (reviewed, owner attestation HOLD)

Nguồn `roneneldan/TinyStories` revision `f54c09fd23315a6f9c86f9dc80f725de7d8f9c64` có license card `cdla-sharing-1.0`. Văn bản chính thức [CDLA-Sharing 1.0](https://cdla.dev/sharing-1-0/) cấp quyền Use/Computational Use tại Section 2, kèm nghĩa vụ nếu Publish Data/Enhanced Data tại Section 3. Khi công bố dữ liệu cần xem attribution/license text và notices thay đổi. Bản này không công khai raw TRAIN/VAL hoặc bản enhanced dataset; training nội bộ theo giấy phép là khả thi về mặt văn bản license, **không phải ý kiến pháp lý**. Tuy nhiên: chủ dự án chưa ký attestation phạm vi dùng bộ private pack cho đợt huấn luyện kế nhiệm và nghĩa vụ không phát hành dữ liệu. Vì vậy `OWNER_RIGHTS_ATTESTATION=HOLD`.

Nguồn kiểm tra: [TinyStories dataset card](https://huggingface.co/datasets/roneneldan/TinyStories), [CDLA Sharing 1.0](https://cdla.dev/sharing-1-0/).

## 5. Một quyết định GO/HOLD tổng hợp

| Cổng | Trạng thái |
|---|---|
| SHA original TRAIN/VAL+checkpoint, 128-step matched draw | **PASS** |
| CPU full-parent model/optimizer/scaler restore | **PASS** |
| CPU tests và số học lần hai | **PASS 42/42 + 34/34** |
| 12 DEV + 24 BLIND_FINAL, BPE checks | **PASS source-only** |
| CDLA license clause review | **PASS scoped license-text; owner attestation HOLD** |
| Colab T4 FP16 và interrupted READY/resume | **NOT_EXECUTED/HOLD** |
| Reviewer độc lập cho nghiên cứu mới | **NOT_ASSIGNED** |
| New exact owner science lock | **NOT_GRANTED** |

**Tuyên bố duy nhất:** `HOLD_FREE_T4_NOT_AUTHORIZED`. Chưa có chứng cứ đầy đủ cho 4-arm one-shot trên Colab Free T4. Không huấn luyện thật, không thay TRAIN, checkpoint, kiến trúc, PR13, main hoặc lineage. Khi hoàn thiện runner READY/resume, đối chứng GPU smoke scoped, reviewer attestation và rights owner, trình một quyết định GO duy nhất; không chia ra hàng loạt micro-permits.

**Bước thực hiện tiếp theo:** `TTM_SMALL4M_2X2_COLAB_RESUME_GPU_SMOKE_REVIEWER_RIGHTS_OWNER_SINGLE_GO_NO_GO`.
