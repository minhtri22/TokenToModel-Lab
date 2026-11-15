# TTM-Small-4M — F2 IR01–IR07 Integrated Author Adversarial QA

**Date:** 2026-11-15  
**Operation:** `TTM_SMALL4M_F2_PREEXEC_INTEGRATED_DESIGN_REMEDIATION_IR01_IR07_SINGLE_GATE`  
**Reviewer type:** **AUTHOR / SAME AGENT**. This is **NOT** an independent reviewer, not a science experiment, and not a release permit.  
**Mode:** `SOURCE_ONLY · DESIGN_ONLY · SYMBOLIC_STRUCTURAL_QA · NO_SCIENCE_EXECUTION`.  
**Prior independent exact candidate:** `07adab6262e50b5e17c6ea816bb133866e0a11d2`, verdict `HOLD_REVISE_DESIGN` (4 HIGH, 3 MEDIUM).  
**Corrected draft exact Git blob pins:** protocol 06 `a5cc0c51363de9772c27418ea667475c25c791b0`; admission 07 `d0ca205935c01a815aaebe86c90f4e3daf1a1291`.  
**Author QA receipt:** `artifacts/research/ttm-small4m-foundation-first/TTM_SMALL4M_F2_IR01_IR07_AUTHOR_ADVERSARIAL_SOURCE_QA_RECEIPT_20261115.json`, blob `01e589c62fded5e733bb50a24bbe73d83fe36ee0`.

## 1. Điều đã rà soát

Tự đọc lại độc lập cả **báo cáo và JSON reviewer** của lượt F2 trước, xác minh original report SHA-256 `c4a43c9236debc967a9a4c088c158074f5fbf0201648677c53e6ea49cffd5376`; original JSON SHA-256 `70685237d07b20bb7b40b3028195e835b88b544e60151d7f0eb150f60a7357d2`. Giữ nguyên verdict `HOLD_REVISE_DESIGN` của reviewer trên commit cũ.

Thiết kế source 06/07 đã sửa tích hợp:
- **IR-01 HIGH:** `S0–S5` và `G12A` (owner authoring permission) khác `G12B` (pre-score conditional release) không vòng tròn; các gate cần dữ liệu chỉ được xét sau khi owner cho phép tác giả tạo riêng tư. Không có owner execution GO hiện tại.
- **IR-02 HIGH:** per-axis fact predicates, independent evidence witnesses, 8 variants và **12 Hamming-1 edges/core** cùng guard semantic coupling; không suy semantic isolation từ bit pattern.
- **IR-03 HIGH:** bắt buộc **NC1–NC6** (global valence, length/format, style/lexical, metadata/order, strong nuisance ensemble và gold-coupling); core-disjoint proxy split, fail-closed nếu một proxy leak.
- **IR-04 HIGH:** gold 0/1/UNKNOWN/INVALID_SOURCE được phân biệt; **3×3 confusion**, 8/8/8 mỗi axis, false-UNKNOWN và non-target thresholds; rater always-UNKNOWN phải FAIL.
- **IR-05 MEDIUM:** screening-only, n=16 independent M0X cores, n=8 target UNKNOWN/axis, per-stratum edge floor12/16, 7/8 uncertainty note.
- **IR-06 MEDIUM:** one-item-per-isolated-session, opaque map, no memory/side-by-side or core variant exposure, `HOLD_RATER_EXPOSURE`.
- **IR-07 MEDIUM:** strict typed source/score schema, reject reason priority, graph validation, **N01–N28** negative-fixture plan and mandatory future checker QA.

## 2. Thực hiện author QA — không tạo science records

Vòng 1 trước bản chỉnh cuối: **28/28** static/math/source assertions PASS (revision candidate). Vòng rà soát thủ công **không dừng tại số PASS** và đã phát hiện:
1. Từ S2 đến S3 cần cho phép các kiểm tra proxy nuisance và source/negative QA của checker **nếu** owner conditional permit bao gồm đúng các công việc này, nhưng tuyệt đối không cho phép AI rater hoặc Small-4M inference.
2. Một số negative fixtures có expected reject code không khớp thứ tự kiểm tra đầu vào: N01 phải fail ở pattern/count trước semantic, N18 missing ID trước summary count; bổ sung `HOLD_SOURCE_CLAIM` cho N26/N27 và N28 cho denominator sai dù rows đầy đủ.

Sau khi sửa, vòng 2 chạy **44/44** assertions PASS, **0 FAIL** trên exact source blobs 06/07 phía trên. 44 checks bao gồm:
- Reachability giả định `S0→S1→S2→S3→S4` dưới full guards và các **tình huống bắt buộc HOLD** nếu thiếu owner G12A, conditional scoring, independent post-data QA hoặc release receipt.
- Enumeration **8 label patterns**, **12 Hamming-1 edges/core**, 4 cạnh mỗi trục, 16×8=128, marginals 64/64; negative graph missing-edge / duplicate-pattern rejection (symbolic, **không có story text**).
- Negative polarity shortcuts: classifier majority-valence chỉ đạt 3/4 sensitivity và specificity theo mỗi axis, không thể qua đề xuất 56/64; always-000/111 thiếu một phía confusion.
- Nuisance catalogue 6 controls, group disjoint, cue-only balance 0.75 vượt đề xuất ceiling0.625 ⇒ HOLD trong logic giả định.
- M0U: tạo **chỉ bảng ký hiệu các nhãn**, không có câu truyện/continuation: 24 nhãn với mỗi measured axis 8 true 0/8 true1/8 UNKNOWN; giả lập rater luôn UNKNOWN có targeted recall8/8 nhưng non-target correct0/16, false-UNKNOWN16/16 ⇒ không qua.
- Parser type restrictions: UNKNOWN bị từ chối trong M0/M0X, boolean/null/string score bị chặn; completeness of reject taxonomy and N01–N28 future fixture specifications.
- Bảo toàn M0 thresholds gốc và admission block, F3/F4 unopened.

**Không chạy** rater, AI scoring, trained model, actual proxy fit, scientific simulation, source-rights review, actual gold, scorer implementation hay GPU. Các symbolic fixtures không phải tập calibration/human truth; mọi vận hành chỉ là tự kiểm cấu trúc của hợp đồng.

## 3. Chứng cứ self-QA và giới hạn

**Author QA verdict:** `PASS_AUTHOR_SYMBOLIC_SOURCE_QA_ONLY__NO_INDEPENDENT_DESIGN_GO`.

Các điều **không được đánh PASS**: (i) 2³ semantic feasibility trong từng stratum; (ii) gold độc lập đúng nghĩa / quyền dữ liệu / PII; (iii) proxy nuisance thực nghiệm không học được style shortcut; (iv) isolation real AI/human raters; (v) scorer thật/negative fixtures thật, security custody; (vi) confidence/power đủ cho confirmatory; (vii) owner freezing candidate thresholds; (viii) T4 model-output measurement validity.

Original MD1 32 cores/64 items, thresholds 28/32 và agreement0.85 bất biến. M0X 16 cores/128 và M0U 24 cores/24, các ngưỡng mới **chỉ là ứng viên**, chưa được owner/independent reviewer khóa. Không đánh `GO_DESIGN_SCOPED` cho tác giả. 

## 4. Trạng thái và bước tiếp theo duy nhất

`F2_AUTHOR_QA_PASS_SCOPED · DISTINCT_INDEPENDENT_QA_NOT_EXECUTED_ON_REMEDIATION · PREEXEC_BLOCK=TRUE · GOLD_NOT_CREATED · OWNER_AUTHORING_GO=FALSE · OWNER_SCORE_GO=FALSE · SCIENCE_HOLD · GPU_NO · F3/F4_NOT_OPENED · MERGE_NO`.

**Bước thực hiện tiếp theo — duy nhất:** reviewer **khác** đọc exact remediation commit, audit substantive truth-condition feasibility, admission DAG, all negative controls and three-class UNKNOWN with candidate statistical thresholds; trả **một verdict** `GO_DESIGN_SCOPED` / `HOLD_REVISE_DESIGN`. Reviewer **không** chạy science và không được nâng author QA thành independent QA.
