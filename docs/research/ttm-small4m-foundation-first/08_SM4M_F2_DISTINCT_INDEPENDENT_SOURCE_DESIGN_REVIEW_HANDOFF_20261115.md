# HANDOFF — SM4M-F2 Distinct Independent Prospective Measurement Design Audit

**Ngày:** 2026-11-15  
**Operation thiết kế do tác giả thực hiện:** `TTM_SMALL4M_F2_PROSPECTIVE_MEASUREMENT_PREEXEC_INTEGRATED_DESIGN_SINGLE_GATE`  
**Operation kiểm toán kế tiếp (đề xuất):** `TTM_SMALL4M_F2_PROSPECTIVE_MEASUREMENT_PREEXEC_DISTINCT_SOURCE_DESIGN_REVIEW_SINGLE_GATE`  
**Vai trò reviewer:** Independent AI Scientific/Source/Measurement Reviewer; không phải human gold attestor.  
**Chế độ:** `READ_ONLY · SOURCE_ONLY · DESIGN_ONLY · NO_SCIENCE_EXECUTION · NO_REPOSITORY_WRITES`.  
**Base pin của thiết kế:** `c233dff20b9b020aefd732ce62bfa2e7aebd3985`. **Exact candidate SHA:** đọc từ nhánh ở lượt review; reviewer phải khóa SHA commit duy nhất có 06/07/08/receipt trước khi nhận. Đừng kiểm HEAD động.

## 1. Mục tiêu

Thực hiện đúng một kiểm toán tích hợp hai tài liệu mới:
- `06_SM4M_F2_PROSPECTIVE_MEASUREMENT_PREEXEC_INTEGRATED_PROTOCOL_20261115.md` — M0 original frozen, M0X per-axis proposed, M0U unknown proposed, sample/threshold/interpretation.
- `07_SM4M_F2_PREEXEC_ADMISSION_SCORING_AND_CUSTODY_MATRIX_20261115.md` — G00–G12 source/rights/gold/anti-shortcut/score/custody/owner preexec gates.

Đối chiếu với:
- [MD1 original at 33021a...](https://github.com/minhtri22/TokenToModel-Lab/blob/33021a421f05bb3bfa0999ad12bc3bd144366da9/docs/research/ttm-hdata-fail4-md1/TTM_HDATA_FAIL4_MD1_PROSPECTIVE_PREREG_AND_FOUR_FAIL_MECHANISM_PLAN_20261114.md) Git blob `384d077600ed864a917fdd5e74b5a5bca0ed8766`.
- [F2 roadmap at c233dff...](https://github.com/minhtri22/TokenToModel-Lab/blob/c233dff20b9b020aefd732ce62bfa2e7aebd3985/docs/research/ttm-small4m-foundation-first/03_SMALL4M_ROOT_CAUSE_RESEARCH_ROADMAP_F0_F4_20261115.md) Git blob `d87309aea043b845fafcc805ed13b2b4466f5e46`.
- [Owner accepted design closure](https://github.com/minhtri22/TokenToModel-Lab/blob/c233dff20b9b020aefd732ce62bfa2e7aebd3985/docs/research/ttm-small4m-foundation-first/05_SMALL4M_F01_F05_OWNER_INTEGRATED_DESIGN_ADJUDICATION_20261115.md); old HOLD and independent GO documents in same branch.
- Original A/C FINAL24 and H-DATA-S1 adjudication as source facts, no re-score, no test re-run.

## 2. Reviewer checklist — bắt buộc phản biện thiết kế, không tick-box theo số

1. **Source identity:** MD1 original 32×2=64, 4×8, `111/000`, 28/32 and agreement 0.85 **không đổi**; có vô tình sửa sample/loss/prereg MD1 không?
2. **Per-axis construct:** 16 new cores ×8 patterns cân bằng có đủ phương diện logic không? Single-axis edge giữa các nhãn có duy trì ngữ nghĩa của hai trục bất biến không? Có semantic coupling vì goal phụ thuộc object/actor không? Dấu hiệu kiểu câu có lộ nhãn không? Nếu không thể kiểm được, HOLD chứ không tạo thí nghiệm không phân biệt.
3. **Actual statistical unit:** 16 independent M0X cores, không phải 128 item iid; 64 matched edges mỗi axis có correlated endpoints. M0 32 cores. Có mô tả thử nghiệm không đủ power và không khẳng định nhân quả quá mức không?
4. **Threshold governance:** M0X `56/64` sensitivity/spec and paired edges, `109/128` agreement; M0U `7/8` targeted unknown chỉ là **candidate thresholds**. Chúng có được biện minh đầy đủ và có phải khóa trước tạo item không? Không đánh đồng với MD1 frozen 28/32,0.85.
5. **Unknown/missing:** 24 targeted unknown cases, hai axes còn lại chấm binary; `UNKNOWN` không bị ép thành 0 hoặc null. Định nghĩa gold nhận diện thông tin thiếu có đo được không, denominator và error policy có thiếu không?
6. **Measurement vs model:** M0/M0X/M0U PASS không chứng minh zero scores trên outputs của T4 là đúng; không chứng minh root cause hoặc AI==human; future realistic model-distribution bridge chưa được admission.
7. **Negative controls:** cue-only style/lexical/length proxies, paired-edge invariants, blind order/IDs, sample/stratum balance, invalid source/gold leakage. Có còn shortcut qua cách sinh các pattern không?
8. **Rights/custody:** gold human vs AI-only, per-core provenance, privacy/PII, TRAIN/VAL/TEST/FINAL and M1 nonoverlap, tokenizer pin, private SHA/HMAC commitments, no public raw texts. Những gì chưa được thực hiện phải là `NOT_VERIFIED`.
9. **Scoring:** per-rater/axis confusion matrices, exact denominators, paired-edge correctness, agreement, missing/invalid/duplicate IDs fail-closed, cluster-based interpretation.
10. **Scope & diff:** đúng 3 Markdown +1 author JSON trên nhánh Foundation First; không sửa `lineage.md`, main, MD1, source, model or archived science; no F3/F4, no PR20 interference.

## 3. Chặn thực thi

Một phán quyết `GO_DESIGN_SCOPED` từ reviewer **chỉ** chứng nhận khả năng tiếp tục chuẩn bị admission, không phải reviewer tạo quyền owner. Runtime vẫn chặn hoàn toàn:
`M0_EXECUTION=NOT_AUTHORIZED; M0X_NOT_CREATED; M0U_NOT_CREATED; RIGHTS_NOT_ATTESTED; GOLD_NOT_FROZEN; BLIND_MAP_NOT_CREATED; SOURCE_QA_NOT_RUN; OWNER_SCIENCE_GO=NOT_GRANTED; F3=NOT_OPENED; F4=NOT_OPENED; NO_MERGE.`

Nếu reviewer phát hiện lỗ hổng làm lỏng gate/overclaim, verdict `HOLD_REVISE_DESIGN`, một remediation list tích hợp, không micro-permits. Nên ưu tiên kiểm các điểm khó: tính khả thi 8 pattern độc lập ngữ nghĩa, quyền tác giả/gold, thống kê cluster cỡ nhỏ và ngưỡng/shortcut pre-freeze. Không cần kiểm lại toàn bộ T4 hay các finding F01–F05 đã CLOSED_DESIGN.

## 4. Đầu ra một gói

- `TTM_SMALL4M_F2_PREEXEC_DISTINCT_SOURCE_DESIGN_REVIEW_20261115.md`
- `TTM_SMALL4M_F2_PREEXEC_DISTINCT_SOURCE_DESIGN_REVIEW_RECEIPT_20261115.json`

Phải ghi exact candidate, Git blob checks, checked sections, source exactness, high/medium findings, future conditions not fulfilled, khoa học = NO và **một verdict** `GO_DESIGN_SCOPED` hoặc `HOLD_REVISE_DESIGN`. Không tự commit/push, không tạo gold hay dùng GPU. Giao owner xem xét một quyết định tích hợp sau kiểm toán.

**Handoff terminal:** `AUTHOR_DESIGN_READY_FOR_DISTINCT_QA · RUNTIME_PREEXEC_BLOCK · OWNER_NOT_PERMITTED_EXECUTION`.
