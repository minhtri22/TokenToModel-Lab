# G1 — Thẩm định đối kháng thiết kế và gói dành cho người kiểm định độc lập

**Ngày:** 2026-11-09  
**Mục tiêu:** `TTM_SIX_XMODEL_G1_SINGLE_INTEGRATED_SCIENCE_PREREG_FINALIZATION_AND_INDEPENDENT_REVIEW`  
**Kết luận:** `INTEGRATED_PREREG_DESIGN_QA_PASS_25_OF_25 / DISTINCT_SCIENTIFIC_REVIEW_NOT_COMPLETED / G1_SCIENCE_LOCK_HOLD`.

Đây là **rà soát đối kháng cấu trúc + phương pháp do cùng phiên trợ lý thực hiện**, **không phải** phản biện khoa học từ một chủ thể độc lập tách khỏi tác giả. Không tự nhận `INDEPENDENT_REVIEW_PASS`, không ký giả reviewer, không cấp science permit. Để có phản biện độc lập đúng nghĩa, người/agent khác phải đọc các tệp bất biến dưới đây và đưa phán quyết riêng trước khi chạy.

## I. Gói nguồn dùng để kiểm định

1. Hợp đồng định lượng machine-readable: `G1_SCIENCE_PREREG_V1_CONTRACT_CANDIDATE_20261109.json`; Git blob `de049ba00331d90f3c7ae72ab3daf943c766ec82`.
2. Tài liệu diễn giải: `G1_SCIENCE_PREREG_V1_METHODS_AND_THRESHOLDS_20261109.md`; Git blob `9dcbf31b2835e07922b2aaf66e5895c7d2f8b03b`.
3. Technical Qwen0.6 PASS, receipt consistency: `G1_V3_COLAB_TECHNICAL_SMOKE_PASS_OWNER_RECEIPT_QA_AND_G1_GATE_20261109.md`, Git blob `b3ee99f44d96de34bf81e031ff24e4345d83f88c`.
4. G0 source SIX provenance, including OW1 FAIL; `G0_PIN_AUDIT_AND_QWEN_FEASIBILITY_20261109.md`.
5. TTM pilot T1 data manifest and source rights technical review, read-only from merged TTM `main`; tránh nhầm TEST của TTM với TEST G1.

## II. Đối chiếu cơ học tách khỏi nội dung narrative

Một thuật toán kiểm toán đọc lại trực tiếp **JSON** và **Markdown** từ GitHub bằng công cụ riêng, đối chiếu **25/25** tiêu chí sau cập nhật numeric stability: schema, no-science, model revision/source SHA, 1.7B 2 shard/target SHA HOLD, source license/rights HOLD, TRAIN-only rule, split 128/64/64, cùng prefix theo SHA, 8 probes, không generation, lớp 28, baselines và null, alpha grid cùng DEV selection, 1.000 permutation, 2.000 bootstrap paired cho ΔR² vs TRAIN-mean, threshold/p-value, positive control, power limitation, VRAM guard, không chạm TTM và science permit HOLD. **25/25 PASS về cấu trúc** tức là tình trạng HOLD được khai báo đúng và thiết kế có đủ trường, *không* chứng minh thiếu sót đã được giải quyết.

## III. Kiểm tra phương pháp đối kháng và kết luận

| Mã | Nguy cơ phản biện | Kết luận / sửa |
|---|---|---|
| R1 | Trộn G1 TEST với TTM TEST gây rò rỉ và ảnh hưởng TTM | Đã tách: G1 chỉ dùng TTM TRAIN, độc lập 128/64/64. Nhưng chưa có readback bytes manifest hoặc quyền truy cập G1 → **HOLD_DATA** |
| R2 | Giấy phép Qwen được dùng để biện minh sai cho TinyStories | Tách Apache-2.0 (model) và CDLA-Sharing-1.0 (dataset); owner rights mới chưa phê duyệt → **HOLD_RIGHTS** |
| R3 | Qwen3-1.7B 2 shards chưa pin actual SHA và chưa load runtime | **HOLD_TARGET_MODEL**. 0.6B smoke PASS không thay được |
| R4 | Tương tự vector/CKA bị gọi là function transfer | Có r_T từ **8 cặp continuation** theo exact conditional likelihood, primary metric riêng; CKA chỉ là cổng bổ trợ. Tuy nhiên các phản ứng này là **sở thích câu tiếp nối có điều kiện**, không kiểm định năng lực giải nhiệm vụ/nhân quả/semantic correctness. Chỉ được gọi `G1_SCOPED_CONTINUATION_PREFERENCE_TRANSFER`, không gọi SIX law validated |
| R5 | Linear ridge căn chỉnh học trực tiếp target, không có đóng góp SIX riêng | Phải báo cáo direct source→target response baseline và random/shuffle; nếu mapping PASS nhưng không hơn direct, chỉ kết luận feasibility của thông tin cross-model, không quy công cho SIX. G3 mới phân biệt functional vs generic distillation |
| R6 | Tokenizers khác nhau, nối x+c rồi tokenize lại làm sai conditional score do BPE merge | Đã xác định rõ prompt tokens và continuation tokens riêng rồi nối token IDs, không index-align, không retokenize raw concat |
| R7 | Giấu lựa chọn layer/probe/alpha/seed bằng TEST | Layer28 chính, layer14 phụ, 8 probes nguyên văn, alpha {1,10,100} chọn trên DEV, TEST chỉ mở một lần. **HOLD_IMPLEMENTATION** vì chưa có runner khoa học độc lập kiểm leakage |
| R8 | Null tráo cặp chịu ít tuning hơn pipeline chính → p-value không công bằng | Đã làm rõ null fit cũng dùng cùng alpha-grid và DEV selection; permutation seed cố định, 1.000 null. Cần khóa source code permutation và chứng minh không nhìn TEST khi tune |
| R9 | Bootstrap 2.000 × permutation 1.000 gây thay đổi estimand/budget quá mức | Đã chỉnh: bootstrap paired ΔR² vs mean, permutation null p95 tính một lần; không nhầm CI đối mean với shuffle |
| R10 | Độ lệch 8 probe/đầu vào nhỏ, n_TEST=64 có thể không đủ power | **CONFIRMATORY_POWER_NOT_ESTABLISHED**. Có thể làm feasibility scoped, không được suy rộng hoặc gọi không đạt p là chứng minh H0. Nếu muốn confirmatory về khoa học rộng hơn phải khóa power theo effect độc lập |
| R11 | Positive control target hidden→target response không đủ tín hiệu | Ngưỡng định trước `R²_target_oracle≥0.20`. Nếu không đạt, verdict bắt buộc `INCONCLUSIVE_CONTROL_UNQUALIFIED`, không FAIL SIX |
| R12 | Teacher pretraining có thể đã gặp TinyStories | Không có chứng cứ loại trừ overlap với pretraining Qwen; TEST là held-out **so với các bộ fit G1**, không phải held-out bảo đảm với pretraining của teacher. Phải ghi limitation |
| R13 | Trọng số teacher, tensor và văn bản được công khai trên GitHub | Khóa không công khai corpus hoặc tensor khối lượng lớn, chỉ manifest/checksum/metrics + rights notices |
| R14 | G1 làm thay đổi science TTM-Small-4M | Không đọc TTM VAL/TEST, không sửa main, không sửa PR #12, không train TTM, không merge. PR #12 đã merged bởi tuyến riêng; G1 chỉ đọc trạng thái |
| R15 | 1.7B hoặc phép chấm 8 cặp vượt T4 Free | Định mức 60 phút/teacher, 120 phút tổng, tải tuần tự, free VRAM≥11GiB, peak≤12GiB, disk≥12GiB. **Chưa có capacity smoke/model 1.7B**, STOP nếu không đạt, không âm thầm giảm workload |

### Vấn đề cần kiểm định trước khi mở TEST

**Finding numeric stability đã được sửa trước chạy khoa học:** JSON và Markdown cuối đã định nghĩa `macro_R2=(1/8)*Σ_j R2_j` (đủ cả 8 chiều), TRAIN population std của bất kỳ probe `<1e-5` ⇒ `INCONCLUSIVE_CONTROL_DEGENERATE_PRETEST` trước khi mở TEST; nếu TEST SST một chiều `<1e-8` ⇒ `INCONCLUSIVE_DEGENERATE_TEST`, không bỏ chiều/rerun. **Implementation runner vẫn chưa có**, nên independent source QA của policy này còn HOLD trước science.

### Quyết định thẩm định khoa học

- `PROTOCOL_CANDIDATE_DESIGN=SPECIFIED`; `STRUCTURAL_25_OF_25=PASS`.
- `INDEPENDENT_DISTINCT_REVIEWER=NOT_PERFORMED`; cần một reviewer tách khỏi người soạn và phán quyết signed/source-pinned.
- `RIGHTS=HOLD`, `TRAIN_MANIFEST_ACTUAL_BYTES=HOLD`, `QWEN17_SHA_SMOKE=HOLD`, `SCIENCE_EXECUTION_RUNNER=NOT_FROZEN`.
- `POWER_FOR_CONFIRMATORY=NOT_QUALIFIED`; G1 scoped feasibility nhỏ chỉ được chấp nhận nếu owner/reviewer đồng ý giới hạn câu kết luận.
- `G1_SCIENCE_LOCK=HOLD`, `SCIENCE_PERMIT=NOT_ISSUED`, `G1_SCIENCE_RUN=NOT_STARTED`.

Không ghi `lineage.md`: đây là thiết kế và kiểm toán kỹ thuật, **không phải** kết quả G1 khoa học. Giữ tất cả FAIL/INCONCLUSIVE cũ của SIX và TTM.

## IV. Hợp đồng yêu cầu đối với phản biện khoa học thực sự độc lập

Người/agent được phân công cần đọc trực tiếp **exact Git blobs** ở Mục I, không chỉ bản tóm tắt. Kiểm lại khả năng biểu diễn vs phép chấm functional, quyền nguồn, chống rò rỉ TTM TEST, tính thống kê R²/CKA/perm/bootstrap, đối chứng âm, positive control, power và T4 resource. Xuất một tài liệu độc lập ghi reviewer identity/role, timestamp, source SHA và verdict `PASS / HOLD / FAIL`, từng finding severity/blocker, bằng chứng cụ thể; nghiêm cấm tự kết luận khoa học nếu không chạy.

**Bước thực hiện tiếp theo:** `TTM_SIX_XMODEL_G1_INTEGRATED_ADMISSION_READINESS_DATA_RIGHTS_QWEN17_AND_INDEPENDENT_ADJUDICATION`. Gộp điều kiện vật chất còn thiếu trong **một** lượt, không lặp Qwen0.6B smoke hoặc mở các giấy phép con không cần thiết.
