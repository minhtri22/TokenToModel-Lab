# TTM × SIX G1 — Sửa đổi tiền đăng ký (preregistration amendment) v1e, chưa phê duyệt

**Ngày:** 2026-11-10. **Trạng thái:** `METHODS_CANDIDATE_ONLY / DISTINCT_METHODS_REVIEW=PENDING / SCIENCE_LOCK=HOLD`.

## 1. Câu hỏi khoa học và nguồn kế thừa

Giữ nguyên câu hỏi RQ1 G1: có tồn tại tín hiệu căn chỉnh biểu diễn liên mô hình từ Qwen3-0.6B sang Qwen3-1.7B, đo được trên tiền tố truyện giữ riêng, vượt đối chứng tráo cặp trong phạm vi được định nghĩa không? Đây là *scoped feasibility* chứ không phải chứng minh SIX gây ra cơ chế nhân quả hoặc làm TTM-Small-4M tốt hơn; khẳng định huấn luyện TTM thuộc G3.

Nguồn bất biến: research commit `d5d0c5346a595557a76349f900d09be50bce289c`; G1 manifest SHA-256 `6451be0cd09a54378eda9e815b5c89ce8ce8301ddefef556476d94e3e31e42b6`; T1 metadata SHA-256 `9f2ebaca821bddf0a9d7ae30ccfcef34561b968b21159aa913794298235a2fa9`. Không sửa lại 128 TRAIN / 64 DEV / 64 TEST và không mở TEST từ runner khi chưa có owner admission.

## 2. Bộ thông số kế thừa *không được đổi sau khi nhìn TEST*

- Teacher A `Qwen/Qwen3-0.6B@c1899de289a04d12100db370d81485cdf75e47ca` và B `Qwen/Qwen3-1.7B@70d244cc86ccca08cf5af4e1e306ecf908b1ad5e`.
- `hidden_states[28]`; tám phép dò (8 continuation response probes) đã được pin trong v1c; alpha ridge grid `[1, 10, 100]`; DEV-only selection.
- `N_shuffle=1000` tráo cặp TRAIN rồi chọn alpha bằng DEV; `N_CKA=1000` hoán vị; `N_bootstrap=2000` paired; seed cố định trong chính frozen code; không xoay seed để tìm kết quả tốt.
- Các đối chứng: direct target probe (B-direct), target oracle, TRAIN mean, shuffle-null và CKA phải được báo cáo đồng thời. Chênh lệch A→P với B-direct là mô tả, **không** được khẳng định công bằng về ngân sách thông tin nếu không chứng thực được cùng mức lựa chọn/đặc trưng.
- Giới hạn compute T4 dự kiến 3.600 giây/model, 7.200 giây tổng, 12GiB peak VRAM chỉ là **giới hạn an toàn**; chưa có chứng cứ watchdog GPU thực.

## 3. Sửa đổi v1a: first-occurrence và rò rỉ near-duplicate

- Bộ chọn mẫu theo first occurrence của T1 là nguồn đã có; không đổi hoặc tạo lại manifest trong bước này. `first_occurrence` phải có hash và phiên bản normalization nguồn, cùng bằng chứng mapping row→source SHA trước chia split.
- Các hash SHA-256 exact story/prefix **không phát hiện near-duplicate**. Trước khoa học phải có **kiểm toán nhóm tương đương (group/near-duplicate lineage)** do một broker có quyền dữ liệu thực hiện trên T1 TRAIN gốc đã được owner chấp thuận, *không dùng outcome TEST*, và chỉ phát hành group-commitment/digest + số lượng kiểm toán không tiết lộ văn bản truyện.
- Cố định quy tắc gần trùng *trước* kiểm toán, kèm mã/hash thuật toán và tham số/normalization. Không được chọn ngưỡng similarity sau khi biết outcome, không được dùng TEST để tune.
- Nếu có thành viên một nhóm near-duplicate nằm ở hai split, đánh dấu `SPLIT_GROUP_LEAKAGE_HOLD`. **Không** tự sửa split, tự bỏ điểm TEST, hoán chuyển dòng hoặc dùng lại one-shot. Muốn đổi split cần amendment/owner decision mới, nguồn và manifest mới, không gắn kết quả với G1 ban đầu.
- Nếu không có quyền kiểm toán lineage, trả `INCONCLUSIVE_DATA_DEPENDENCE` hoặc `METHODS_HOLD` trước science, không tự cho phép truy cập TEST.

## 4. Sửa đổi v1b: paired bootstrap với `SST_TEST` cố định

- Estimand được báo cáo là độ cải thiện có điều kiện trên tập TEST 64 đã khóa, so với train-mean predictor (hoặc metric được khóa trong v1c). Giữ denominator `SST_TEST` *từ toàn bộ TEST* bất biến cho mọi mẫu paired bootstrap, tránh singleton / 63+1 degenerate denominator.
- `CI95` của 2.000 paired replicates nói về biến động lấy mẫu theo hàng/nhóm dưới giả định exchangeability. Nó **không** là bằng chứng rằng G1 có power 80%, và không thay thế p-value shuffle-null.
- Nếu nhóm near-duplicate gây phụ thuộc, resample theo nhóm độc lập hoặc phân tích độ nhạy đã tiền đăng ký. Vì đổi cách bootstrap có thể làm thay đổi phân phối thống kê, **không âm thầm triển khai trên run đã khóa**; nếu chưa có code/hash/group evidence và độc lập review thì `METHODS_HOLD`.
- Trường hợp `SST_TEST<=epsilon` hoặc hình học suy biến: `INCONCLUSIVE`, không ép PASS/FAIL.

## 5. Sửa đổi v1c: CKA và tolerance số học

- Dùng **cùng** centered Gram `G_source`, `G_target`, cùng denominator và cùng phép giảm (reduction) cho observed và toàn bộ 1.000 permutation nulls.
- Tie bảo thủ đã ghim: `null >= observed - 64 * epsilon(float64) * max(1, abs(observed))`. Khi tất cả hoán vị là tie, p=1; không được thay `64` dựa trên TEST hoặc chọn scale sau khi biết kết quả.
- Công thức p-value cộng một: `(1 + #null_at_or_above_observed) / (1000+1)`.
- Reviewer cần xác nhận Type-I/power qua mô phỏng độc lập *trước* TEST trên nhiều cấu trúc covariance, near-degenerate và thang đo. Fixture synthetic PASS hiện có chỉ chứng minh sửa false positive số học cụ thể, không đủ chứng minh mọi null exchangeable.

## 6. Null exchangeability, cỡ mẫu và nghĩa của phán quyết

- Mọi permutation/bootstrap yêu cầu đơn vị độc lập hợp lệ. Thẩm định tính trao đổi được (exchangeability) theo nhóm nguồn/tiền tố; không được coi 64 hàng độc lập nếu có lineage phụ thuộc.
- `TEST=64` **chưa có chứng minh công suất kiểm định 80%**. Phép tính power prospective phải chỉ rõ effect size mục tiêu, variance, clustering, alpha và criterion. Nếu power không đủ, verdict phải ghi `INCONCLUSIVE_LOW_POWER`, không sửa threshold hay tăng TEST sau khi đã mở.
- Ngưỡng G1 đã prereg (macro R², đối chứng tráo cặp, CKA p, bootstrap, oracle) không được điều chỉnh sau khi nhìn TEST. Mọi điều kiện bắt buộc không rõ hoặc không đạt điều kiện dữ liệu/nguồn là **HOLD trước science**; nếu đã chạy khoa học hợp lệ nhưng metric chứng cứ thiếu lực thì `INCONCLUSIVE`, không tự chọn nhánh PASS.
- Báo cáo G1 nêu cả kết quả âm, CI, số mẫu/nhóm và limitations; không suy ra lợi ích huấn luyện TTM hoặc generalization ngoài 64 TEST.

## 7. Phán quyết phương pháp cần reviewer/owner, chưa tự phê duyệt

| Điều kiện | Evidence cần | Trạng thái hiện tại |
|---|---|---|
| Exact normalization, first-occurrence, lineage | Hash/mã nguồn và broker audit, không dùng TEST outcome | `NOT_TESTED` |
| Near-duplicate grouping và exchangeability | Precommitted group rule, split-group proof, sensitivity | `NOT_TESTED` |
| Bootstrap conditional estimand / grouped variation | QA độc lập đúng metric/giả định | `REVIEW_HOLD` |
| CKA 64ε Type-I/power | Simulation và QA độc lập, không TEST | `REVIEW_HOLD` |
| Power TEST64 và terminal inconclusive | Prospective calculation và decision table | `REVIEW_HOLD` |
| Owner admission/data rights | Chữ ký owner và phạm vi T1 TRAIN riêng | `NOT_ISSUED` |

**Quyết định tài liệu:** `METHODS_AMENDMENT_V1E=DESIGN_CANDIDATE`; `DISTINCT_ADJUDICATION=PENDING`; `OWNER_SCIENCE_PERMIT=NOT_ISSUED`; `G1_SCIENCE_LOCK=HOLD`.

**Bước thực hiện tiếp theo:** đưa bản v1e cùng production boundary source pins sang Codex phản biện độc lập; sau khi đủ bằng chứng, một owner admission riêng, không gộp vào tự phê duyệt của tác giả.
