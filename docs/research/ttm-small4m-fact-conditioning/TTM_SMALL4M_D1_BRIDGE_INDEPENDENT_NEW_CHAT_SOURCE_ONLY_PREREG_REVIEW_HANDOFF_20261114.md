# HANDOFF — D1 Bridge V1 / Independent Scientific Preregistration Review

**Operation:** `TTM_SMALL4M_D1_BRIDGE_SOURCE_ONLY_INDEPENDENT_PREREG_REVIEW_AND_GO_HOLD_NO_GPU`  
**Ngày bàn giao:** 14/11/2026  
**Dự án:** `minhtri22/TokenToModel-Lab`  
**Nhánh:** `research/ttm-small4m-fact-conditioning-data-objective-capacity-design-20261112`  
**Frozen scientific input HEAD:** `25a19daea9f664e14f83d7df2cf8265ffaea4ecd`  
**Vai trò agent:** **Independent AI Scientific Protocol Reviewer** (người phản biện AI độc lập về thiết kế khoa học), **không phải** người thiết kế, chạy mô hình, chấm mù hoặc giữ gold.  
**Chế độ:** `READ_ONLY / DESIGN_ONLY / SOURCE_ONLY / NO_GPU / NO_TRAIN / NO_TEST_ACCESS`.  
**Trạng thái đầu vào:** `D1_BRIDGE_DESIGN=FROZEN_CANDIDATE_FOR_REVIEW` · `D1_BRIDGE_SCIENCE=HOLD`.

## 1. Nhiệm vụ — bắt đầu ngay khi nhận handoff

Đọc tài liệu nguồn đúng **frozen commit**, thực hiện **một lượt phản biện khoa học độc lập** và trả **một quyết định cuối** `GO_DESIGN_ONLY`, `HOLD_REVISE_BEFORE_PREREG` hoặc `FAIL_INVALID_DESIGN`. Quyết định chỉ về **chất lượng thiết kế và khả năng đóng băng giao thức**, tuyệt đối **không phải GO training/GPU/D1**.

Không phải hỏi owner ký thêm micro-permit để *đọc và review*. Nếu không đọc được nguồn, phải ghi `HOLD_SOURCE_UNAVAILABLE`, không dựa vào tóm tắt của agent cũ để đoán phần thiếu.

**Reviewer phải tìm lỗ hổng, không xác nhận thành tích.** Kết quả FC01 exploratory là bối cảnh tạo giả thuyết, không được dùng làm dữ liệu để biện hộ power, chọn threshold hoặc điều chỉnh luật chấm mới.

## 2. Tài liệu bắt buộc — đọc nguyên bản, đúng commit

| Nguồn | Git blob SHA-1 GitHub | Mục đích |
|---|---|---|
| [D1 Bridge V1 — Markdown](https://github.com/minhtri22/TokenToModel-Lab/blob/25a19daea9f664e14f83d7df2cf8265ffaea4ecd/docs/research/ttm-small4m-fact-conditioning/TTM_FC01_D1_BRIDGE_STRUCTURAL_OOD_FREEGEN_MULTISEED_PREREG_DESIGN_V1_20261113.md) | `a5cd0dbd4167bdc53454847a25afcf317c94226b` | Hợp đồng khoa học, ngưỡng, thiết kế |
| [D1 Bridge V1 — machine-readable JSON](https://github.com/minhtri22/TokenToModel-Lab/blob/25a19daea9f664e14f83d7df2cf8265ffaea4ecd/artifacts/research/ttm-small4m-fact-conditioning/TTM_FC01_D1_BRIDGE_PREREG_V1_MACHINE_READABLE_DESIGN_HOLD_20261113.json) | `8bc9cf0fa45ada52150094a24259514f51ee2a28` | Kiểm nhất quán từng trường |
| [Source-only consistency QA 26/26](https://github.com/minhtri22/TokenToModel-Lab/blob/25a19daea9f664e14f83d7df2cf8265ffaea4ecd/artifacts/research/ttm-small4m-fact-conditioning/TTM_FC01_ARCHIVE_D1_BRIDGE_V1_SOURCE_ONLY_INTEGRATED_QA_20261113.json) | `e29a994a9d3d9bf368380aeb858f0626ec6558ed` | **Chỉ self-authored QA**, không coi là independent review |
| [FC01 terminal archive manifest](https://github.com/minhtri22/TokenToModel-Lab/blob/25a19daea9f664e14f83d7df2cf8265ffaea4ecd/artifacts/research/ttm-small4m-fact-conditioning/TTM_FC01_EXPLORATORY_FINAL_ARCHIVE_MANIFEST_AND_D1_BRIDGE_DESIGN_HOLD_20261113.json) | `dab622ba088ee3def4c0994dd2f068938fd47bc2` | Bằng chứng động cơ & giới hạn exploratory |
| [D1 hiện hữu — handoff 512 outputs](https://github.com/minhtri22/TokenToModel-Lab/blob/25a19daea9f664e14f83d7df2cf8265ffaea4ecd/docs/research/ttm-small4m-quality-gap/TTM_SMALL4M_D1_INDEPENDENT_CHATGPT_BLIND_RATER_HANDOFF_20261112.md) | `b6abdab37b5220fc7a861de940e28313ebe1c316` | Bảo đảm D1 Bridge **không sửa/lẫn** D1 đã khóa |
| [lineage.md — L0016](https://github.com/minhtri22/TokenToModel-Lab/blob/25a19daea9f664e14f83d7df2cf8265ffaea4ecd/lineage.md) | `dc97f833dfd764bce29675919604f3ebb97bf8e8` | Nguồn gốc append-only; không sửa lịch sử |

Nếu chưa đọc đủ 6 nguồn thì không tuyên bố `FULL_REVIEW_PASS`. Các SHA trên là **Git blob SHA-1** (không phải SHA-256 nội dung) và có thể đối chiếu bằng GitHub API hoặc `git rev-parse <commit>:<path>`. Không đọc branch HEAD động để thay thế frozen commit.

## 3. Hợp đồng đang được review (không được tự thay)

- Ba arm: `A_BASE_MLE`, `B_CF_MLE`, `C_CF_CONTRAST`; B/C dùng **dữ liệu và thứ tự episode giống byte**, khác mục tiêu; A là singleton cân bằng.
- P02 parent step1024; T1 BPE2048; FP32; STEP256 mỗi arm/seed; **5 seed** `20261120`–`20261124`. Không dùng best checkpoint theo EVAL.
- Bốn nhóm `entity_location`, `causal_reasoning`, `rule_constraint`, `goal_persistence`; mỗi nhóm 4 skeleton TRAIN và 4 skeleton OOD cấu trúc.
- TRAIN = **512 paired families**; VAL = **128**; OOD EVAL = **256** paired families; **512 prompt/arm/seed**; dự kiến 15 arm-runs / 3.840 optimizer updates / 7.680 generations **nếu** khoa học được phép về sau.
- Greedy decoding, output một hành động ngắn, `prompt≤224` tokens + `new≤32` tokens trong context 256; deterministic parser khóa trước EVAL.
- Primary theo *family*: **đúng cả hai điều kiện A và B**. `d_s = mean_f(success_C − success_B)` theo 5 seed, cân bằng 4 category. Exact one-sided paired sign-flip `alpha=0.05`, minimum p 1/32; gate thêm `mean(d_s)≥+0.10`, không có category âm, ít nhất 3/4 category ≥+0.05, accuracy tuyệt đối C ≥25% ở cả 4 category.
- Không tạo data/gold, không train, không dùng GPU, không mở TEST/Q1Q2, không sử dụng D1 hiện hữu.

## 4. Sáu trục phản biện bắt buộc (đưa PASS/HOLD/FAIL từng trục)

**R1 — Độ mới OOD cấu trúc (structural OOD):** Kiểm tra định nghĩa `semantic_skeleton_id`, phép so cấu trúc AST/graph, graph isomorphism đổi tên, biến ngữ nghĩa và thứ tự logic, chỉ khác lexical vs khác thao tác suy luận. Có cách nào chứng minh TRAIN không chứa cấu trúc tương đương EVAL? Tập 4 skeleton/category có đủ đa dạng để kết luận structural generalization? Nêu negative controls và tiêu chuẩn loại trùng **trước khi sinh EVAL**. Nếu chưa có AST thực, ghi `NOT_EXECUTED`, không kết luận non-overlap PASS.

**R2 — Scorer, decoder, và primary validity:** Kiểm tính đúng/sai của *hành động có điều kiện*, đáp án tham chiếu riêng A/B, trường hợp thiếu/đa nghĩa/mâu thuẫn, parser false-positive/false-negative, synonym, tokenization và max-length. Kiểm bất biến `both-conditions-correct`, mẫu số family cố định, EOS/truncation, greedy fairness và tính công bằng giữa arm. Đề xuất test fixture âm/dương được phép **ở mức đặc tả**, không viết gold hay chấm dữ liệu OOD thật. Parser hiện **chưa có mã thực**: đánh giá contract, không giả nhận parser QA.

**R3 — Thống kê, 5 seed, power và false positives:** Xác định *đúng đơn vị độc lập* (seed, skeleton, family) và điều kiện exchangeability của exact sign-flip; rủi ro cùng parent/data/EVAL qua seed, skeleton cố định, tương quan giữa family và trần p-value với n=5. Kiểm phép thử một phía, lựa chọn `alpha=.05`, cách xử lý zero effects/ties, missing seed, p-value discrete, và liệu 5 seed đủ power cho `+10pp` thực chất hay không. Phân biệt **kiểm định H0: Δ=0** với **yêu cầu ngưỡng hiệu ứng ≥0.10**: nếu đây là gate ghép chứ không phải test cho Δ≥0.10, bắt buộc ghi rõ và cân nhắc liệu nên giữ. Xem tính hợp lý của bootstrap phân cấp seed→skeleton→family, có double counting/correlation không; yêu cầu reviewer tự làm bảng ví dụ tính toán bằng số giả lập *trong suy luận*, **không sinh data science**.

**R4 — Ngưỡng bảo vệ theo nhóm và diễn giải:** Kiểm logic đồng thời của `mean Δ≥10pp`, `p≤.05`, `4/4 Δ≥0`, `3/4 Δ≥5pp`, `C absolute≥25%` theo 4 category. Đánh giá false success, false failure, low base rate, overconservatism, posthoc anchoring do FC01 chỉ thành công rule_constraint. Đề xuất cách phân biệt `CONFIRM_PRIMARY_GO` với `POSITIVE_AGGREGATE_SCOPED`, `NO_CONFIRMED_GAIN`, `HOLD_INVALID_PROTOCOL`; không được tự thay ngưỡng và coi như đã phê duyệt.

**R5 — Data leakage / rights / blind custody:** Chỉ rõ các đường rò từ template/AST/generator, pretrained parent TinyStories, shared lexical worlds, prompt/answer leakage, parser/teacher-forced tuning, seed selection, VAL/TEST selection. Đánh giá sơ đồ custody: owner TRAIN/VAL, custodian EVAL gold, reviewer scores, mapping SHA trước giải mù. Có độc lập quyền truy cập thực hay chỉ tách vai trò trên giấy? Gợi ý ít nhất một kiểm tra âm để phát hiện leakage và điều kiện quyền dữ liệu. Không tìm hay đọc tệp private/sealed.

**R6 — Khả thi và tính tái lập (reproducibility/resources):** Đánh giá 5×3 runs, đúng checkpoint/seed, budget token/microbatch, GPU Free T4 + phí $0, storage/timeout, determinism, resume sau AdamW đã có moment state (không nhầm với snapshot zero-step), one-shot fail-closed, nguyên tắc giữ kết quả lỗi; có khả thi để `GO_DESIGN_ONLY` không? Không giả đo thời gian hay cấp phép GPU.

## 5. Quy tắc độc lập và xử lý lỗi

- Reviewer là **AI ở phiên/chat mới**; chỉ nhận handoff và 6 tệp frozen; không đọc transcript của agent thiết kế. Có thể dùng tính toán nội bộ để kiểm thống kê; **không chạy training/inference hoặc sinh gold/test**.
- Không chỉnh sửa source, hyperparameter, schema, seed, scorer, `lineage.md`, `main`, không merge, không cấp science GO. Nếu đề xuất sửa, đưa **amendment có version mới**, nêu chính xác dòng/trường cần sửa, vấn đề khoa học, tác động tới prereg; **không thay V1 tại chỗ**.
- Không đưa bất kỳ private raw data/checkpoint/EVAL gold hoặc mapping lên GitHub hay vào phản hồi.
- Reviewer cần nói rõ limitation `AI_SELF_ATTESTED_NEW_CHAT`; nếu không thể xác minh tính độc lập, ghi `INDEPENDENCE_NOT_VERIFIED`.
- Không để lời công bố `QA_26/26` của author thay cho việc reviewer tự chỉ ra lỗi và kiểm tra logic. Không vì FC01 exploratory dương mà tự cho D1 bridge GO.

## 6. Định dạng bàn giao lại cho chủ dự án

**Xuất hai file hoàn chỉnh**, lưu file để owner tải hoặc commit **chỉ vào nhánh chứng cứ review riêng** nếu có quyền được ủy nhiệm (không ghi đè frozen scientific branch):

1. `TTM_D1_BRIDGE_V1_INDEPENDENT_PREREG_REVIEW_20261114.md`: tóm tắt câu hỏi khoa học, 6 mục R1–R6 mỗi mục có **PASS/HOLD/FAIL**, lý do cụ thể + dẫn chiếu đoạn/đường dẫn frozen source, risk level `CRITICAL/HIGH/MEDIUM/LOW`, điều kiện khắc phục, phân loại amendment (must-fix trước source QA hay optional); phân biệt `NOT_EXECUTED` với FAIL.
2. `TTM_D1_BRIDGE_V1_INDEPENDENT_REVIEW_RECEIPT_20261114.json`: tối thiểu:
```json
{
  "operation": "TTM_SMALL4M_D1_BRIDGE_SOURCE_ONLY_INDEPENDENT_PREREG_REVIEW_AND_GO_HOLD_NO_GPU",
  "reviewer_type": "INDEPENDENT_NEW_CHAT_AI_SELF_ATTESTED",
  "frozen_input_commit": "25a19daea9f664e14f83d7df2cf8265ffaea4ecd",
  "source_files_verified": [],
  "review_sections": {
    "R1_structural_ood": "HOLD",
    "R2_parser_primary": "HOLD",
    "R3_statistical_power": "HOLD",
    "R4_category_gates": "HOLD",
    "R5_leakage_rights_custody": "HOLD",
    "R6_repro_resources": "HOLD"
  },
  "critical_findings": [],
  "required_amendments": [],
  "source_only_review_complete": false,
  "science_executed": false,
  "gpu_calls": 0,
  "private_gold_accessed": false,
  "independence_scope": "SELF_ATTESTED_NEW_CHAT_NOT_HUMAN",
  "single_design_decision": "HOLD_REVISE_BEFORE_PREREG",
  "d1_science_release": "HOLD",
  "test_q1q2": "SEALED"
}
```
Các giá trị HOLD trong JSON trên **chỉ là placeholders**, không phải đáp án định hướng: reviewer phải thay bằng nhận xét thực, không sao chép mặc định. Tệp không được khai báo PASS khi còn `source_files_verified` thiếu hoặc lỗi CRITICAL chưa đóng. Nếu SHA-256 receipt có thể tính được, báo hash thực; không bịa.

**Single design decision semantics:**
- `GO_DESIGN_ONLY`: hợp đồng nhất quán, các giả định chấp nhận được cho **bước triển khai source+independent QA tiếp theo**; vẫn `D1_SCIENCE=HOLD`.
- `HOLD_REVISE_BEFORE_PREREG`: bất kỳ lỗi/thiếu bằng chứng trọng yếu có thể khắc phục; đề xuất một gói amendment tập trung, **không micro-permits**.
- `FAIL_INVALID_DESIGN`: giả định/hypothesis vô hiệu hoặc nhiễm leakage không thể cứu bằng sửa đổi nhỏ; đề xuất tái thiết kế lớn, không chôn kết quả âm.
- `HOLD_SOURCE_UNAVAILABLE`: chưa đọc/kiểm được nguồn chính, không tự phân xử nội dung.

## 7. Quyết định và ranh giới sau review

Trả một câu chốt `D1_BRIDGE_DESIGN=GO_DESIGN_ONLY|HOLD_REVISE_BEFORE_PREREG|FAIL_INVALID_DESIGN|HOLD_SOURCE_UNAVAILABLE`, một danh sách các sửa đổi ưu tiên, và **Bước thực hiện tiếp theo** duy nhất.

**Bất biến không được thay đổi:** `FC01_EXPLORATORY=CLOSED_PASS_SCOPED` · `D1_EXISTING=HOLD_UNMODIFIED` · `D1_BRIDGE_SCIENCE=HOLD` · `TEST_Q1Q2=SEALED` · `FC02=NOT_OPENED` · `NEW_TRAINING=0` · `GPU=0` · `MAIN=UNCHANGED`. Review không được tự mở bất kỳ nhánh khoa học hay chấm mù nào.

**BẮT ĐẦU REVIEW NGAY** khi nhận handoff, không hỏi lại điều kiện đã có; nếu GitHub không đọc được thì nêu blocker và HOLD có chứng cứ.
