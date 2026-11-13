# FC01 — BLIND96 AI scorer, freeze trước unblind, và phân xử hậu nghiệm duy nhất

**Operation:** `TTM_SMALL4M_FC01_BLIND96_INDEPENDENT_AI_RATER_SCORING_FREEZE_AND_SINGLE_POSTHOC_ADJUDICATION_NO_GPU`  
**Ngày:** 13/11/2026  
**Kết luận:** **`PASS_SCOPED_FC01_BLIND96_COMPLETE_NO_D1_RELEASE`**.  
**Giới hạn reviewer:** AI mù về danh tính từng đoạn, **không** phải fresh-chat rater hoàn toàn độc lập: phiên này từng xem kết quả primary tổng hợp, không xem mapping 96 bản ghi trước khi đóng băng điểm. Không có external human reviewer.

## 1. Đường chứng cứ và chronology khóa điểm

1. Truy xuất đúng `FC01_SECONDARY_BLIND96_PRIVATE.json` bằng locator tệp trực tiếp, **không truy xuất bảng mapping**. SHA-256 byte mù từ Drive = `e032e55c8f0e1e9efe87948c7fb67af5c4e648df89a32483e91a5e9d5588620f`; 96 bản ghi, 96 opaque ID riêng.
2. Không có rubric chấm đầu ra thứ cấp đã đăng ký trong các tài liệu FC01 hiện tại. Vì vậy đóng khung **posthoc exploratory** hai trục 0–3 trước khi chấm đủ 96: *bám dữ kiện/hành động* (0 sai/lạc đề; 1 nhắc đúng chủ đề nhưng chưa làm đúng; 2 đích đúng từng phần, thiếu hành động; 3 hành động đúng đầy đủ) và *tính mạch lạc* (0 gibberish; 1 câu sai cấu trúc/nửa chừng; 2 câu hiểu được nhưng vụng; 3 câu hoàn chỉnh/đúng ngữ pháp dù có thể sai dữ kiện). Cần phân biệt câu viết trôi chảy với câu làm đúng yêu cầu.
3. Chấm đúng **96/96** từ cặp `prompt_text` và `generated_text_only`, không dùng arm/model ID, không mở đáp án vàng hay primary EVAL64 để quyết định điểm; file gốc điểm SHA-256 **`a5694690a7df8743009987bc0413c49d9951309bc00df0e670fde0cac54dae09`**.
4. **Trước khi đọc mapping**, ghi biên nhận score-commit vào GitHub commit **`1a78ca28b64149518d61b86a55150278e2283279`**; đọc lại biên nhận từ đúng commit và xác minh SHA đã khóa. Đã lưu thêm bảng điểm số *mù* đầy đủ theo 96 opaque ID (không prompt, văn bản hoặc arm): `artifacts/research/ttm-small4m-fact-conditioning/TTM_FC01_BLIND96_FROZEN_NUMERIC_SCORES_BY_OPAQUE_ID_20261113.json`.
5. **Sau freeze**, mới mở mapping riêng tư, băm SHA-256 `3e8f8593388104782eba768474f7b009a57e2ef4a4891a4fd9fe327c61373e52`, đối chiếu join 96/96 opaque IDs, 32 outputs/arm, 16 family/arm × 2 condition. **Không phát hành mapping, raw prompt, raw generated text** trên GitHub.

## 2. Kết quả sau giải mù theo nhánh

| Nhánh | Đầu ra | Đúng đầy đủ (adherence=3) | Điểm bám dữ kiện TB (0–3) | Mạch lạc TB (0–3) |
|---|---:|---:|---:|---:|
| A_BASE_MLE | 32 | 4/32 (12,5%) | 0,90625 | 2,03125 |
| B_CF_MLE | 32 | 4/32 (12,5%) | 0,8125 | 2,00000 |
| C_CF_CONTRAST | 32 | **8/32 (25%)** | **1,28125** | 2,00000 |

`C-B` điểm bám dữ kiện trung bình = **+0,46875 điểm (trên thang 0–3)**. Bootstrap theo block lexical family với seed 20261113, 10.000 mẫu, phân tầng bốn category: CI percentile khám phá 95% **[+0,34375,+0,5625]**. **Không phải CI confirmatory** vì rubric hậu nghiệm và chỉ có 4 template semantics. `C-B` điểm mạch lạc = **0**, CI khám phá [-0,375,+0,25]. C có thêm 4/32 đầu ra hoàn thành chính xác (+12,5 điểm phần trăm); `B-A` không khác về tỉ lệ hoàn thành chính xác (4/32 so với 4/32). Không công bố p-value thăm dò như bằng chứng xác nhận.

## 3. Heterogeneity: toàn bộ 16 đầu ra đúng đều nằm ở rule_constraint

| Category (8 đoạn mỗi arm) | A đúng | B đúng | C đúng |
|---|---:|---:|---:|
| entity_location | 0 | 0 | 0 |
| causal_reasoning | 0 | 0 | 0 |
| rule_constraint | 4 | 4 | **8** |
| goal_persistence | 0 | 0 | 0 |

Trong 96 output chỉ có 17 chuỗi văn bản sinh khác nhau. Các lỗi điển hình về **loại**, không trích nguyên raw corpus: câu lặp token vô nghĩa, quên vị trí/đích, nêu meter nhưng không chọn hướng dial, chọn sai màu crate. Điều này thể hiện khác biệt lớn giữa *teacher-forced candidate likelihood* và *greedy decoding completion*.

Đối chiếu primary đã khóa ở lượt trước vẫn là **A=4/64, B=3/64, C=38/64**; `C−B=+54,6875` điểm phần trăm trên EVAL64. **Không sửa hoặc ghép tiêu chí primary với bảng chấm mù thứ cấp**. Dù C tăng hiệu ứng trên primary, greedy output chỉ hoàn thành đúng 8/32 và không chứng minh suy luận hay tuân thủ yêu cầu tổng quát ngoài template có sẵn.

## 4. Phân xử và bảo vệ khoa học

- `BLIND_SOURCE_BYTES=PASS_EXACT_SHA256`
- `SCORES=FROZEN_96_OF_96_BEFORE_UNBLIND`
- `MAPPING_SHA=PASS_AFTER_FREEZE_PRIVATE`
- `SCORING_RUBRIC=EXPLORATORY_POSTHOC_NOT_PREREGISTERED`
- `GREEDY_SECONDARY_C_MINUS_B=POSITIVE_ADHERENCE_SCOPED_RULE_CONSTRAINT_CONCENTRATED`
- `GREEDY_SECONDARY_FLUENCY=NO_OBSERVED_MEAN_GAIN`
- **`FC01_SCIENCE=PASS_SCOPED_EXPLORATORY_SECONDARY_COMPLETE_NO_CONFIRMATORY_RELEASE`**
- **`D1_CONFIRMATORY=HOLD`**, `TEST_Q1Q2=SEALED`, `DEV32=CLOSED`, `FC02=NOT_OPENED`
- `GPU=NO`, `TRAINING_RERUN=NO`, `LINEAGE=UNCHANGED_PENDING_OWNER_ARCHIVE`.

**Kết luận khoa học có thể bảo vệ:** FC01 cải thiện primary margin dưới contrastive objective trên shared-template EVAL64, và secondary AI score hậu nghiệm cho thấy sự cải thiện cục bộ ở rule_constraint, **không** chứng minh chuyển giao sinh văn bản chính xác sang cả bốn loại suy luận. D1 confirmatory chưa được mở. Cần ít nhất một reviewer thực sự tách phiên/human reviewer và phương án template mới/đánh giá nhiều seed được tiền đăng ký trước khi tuyên bố hiệu quả khái quát.

**Bước thực hiện tiếp theo:** `TTM_SMALL4M_FC01_POSTHOC_EVIDENCE_ARCHIVE_AND_D1_BRIDGE_PREREG_DESIGN_ONLY_NO_GPU`: không chấm lại/training; đóng hồ sơ exploratory, xác định điều kiện kiểm định confirmatory mới (template độc lập, free-generation accuracy và độ bền nhiều seed) như một đề cương riêng, chưa cấp quyền chạy.

**Biên nhận machine-readable:** `artifacts/research/ttm-small4m-fact-conditioning/TTM_FC01_BLIND96_FROZEN_SCORES_UNBLIND_SAFE_POSTHOC_SINGLE_ADJUDICATION_20261113.json`.
