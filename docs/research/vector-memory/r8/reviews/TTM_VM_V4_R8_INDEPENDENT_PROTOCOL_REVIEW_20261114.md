# TTM VM V4 R8 — INDEPENDENT AI SOURCE/PROTOCOL REVIEW

- **Ngày:** 2026-11-14
- **Operation:** `TTM_VM_V4_R8_PROSPECTIVE_PROTOCOL_DISTINCT_SOURCE_REVIEW_AND_OWNER_AMENDMENT_DECISION_NO_GENERATION`
- **Reviewer:** GPT-6; independent AI source reviewer (không phải reviewer con người; không thay thế quyết định owner)
- **Mode:** `READ_ONLY` · `DESIGN_ONLY` · `NO_GENERATION` · `NO_SCIENCE_EXECUTION`
- **Repository:** `minhtri22/TokenToModel-Lab`
- **Source commit (pinned):** `c62d0d5fa9d8b87c2d508b36f0942a3fff3fce69`
- **Source file:** `docs/research/vector-memory/r8/TTM_VM_V4_R8_PROSPECTIVE_PROTOCOL_REVIEW_DESIGN_ONLY_20261114.md`
- **Git blob SHA-1 (không phải SHA-256):** `a13733971cd4b3b70531a9d861147bb5a9cf80ac`
- **Source URL:** https://github.com/minhtri22/TokenToModel-Lab/blob/c62d0d5fa9d8b87c2d508b36f0942a3fff3fce69/docs/research/vector-memory/r8/TTM_VM_V4_R8_PROSPECTIVE_PROTOCOL_REVIEW_DESIGN_ONLY_20261114.md
- **Decision:** `HOLD_R8_PROTOCOL_AMENDMENT_REQUIRED_NO_GENERATION`

## 1. Scope and evidentiary limitation

Đã đọc toàn bộ đặc tả R8 tại commit khóa. Review này phân tích tính nhất quán logic, khả năng nhận diện shortcut, ước lượng khoa học, luật QA, blinding, và các gate quản trị. **Không** tự xác minh byte/chạy lại bộ QA R7; các kết quả R7 7/9, marker-only 64/64 và gold 32/32 được ghi nhận *theo đặc tả*, không được tự nhận là đã tái kiểm chứng. Không kiểm toán byte private hay chứng nhận rights. Không sinh R8, không xem gold, không mở TEST/Reader/GPU/PROBE.

## 2. Positive design findings (PASS_SCOPED_SOURCE_REVIEW)

1. **P01 — Diagnosis clarity:** Nhận diện rõ marker-only leakage của R7 và P/N confounding; không suy rộng thành khẳng định đã PASS những QA chưa chạy.
2. **P02 — Changed estimand:** Thừa nhận thay P/N stratum bằng 8 `relation_family` làm đổi estimand, phải có V4 CAL protocol riêng, không đồng nhất với R5–R7.
3. **P03 — One-shot and governance separation:** Đề xuất đóng băng trước sinh, giữ các vòng trước bất biến, phân biệt quyền sinh candidate với quyền khoa học dùng CAL, không xem AI review là owner approval.

## 3. Blocking findings (HOLD)

### B01 [HIGH] — Target/key ontology và quy tắc ABSTAIN chưa được hình thức hóa

Đặc tả đồng thời yêu cầu suy luận từ nhiều chứng cứ và một `gold` card duy nhất. Cần định nghĩa chính xác target card, support cards, tập chứng cứ cần thiết, và hàm entailment. `ABSTAIN` do **không có** target được chứng minh khác với `ABSTAIN` do **nhiều** target ngang quyền hoặc xung đột bằng chứng. Câu “zero unique support” chưa phân biệt các tình huống này. F07 (missing premises) có nguy cơ trở thành loại nhãn âm cố hữu nếu không có phiên bản SELECT có ý nghĩa.

**Amend:** Khóa schema private: `target_card_id | null`, `proof_card_ids`, `premises`, `authority_order`, `temporal_order`, `abstain_reason ∈ {NO_SUPPORTED_TARGET, MULTIPLE_SUPPORTED_TARGETS, UNRESOLVED_AUTHORITY, MISSING_PREMISE}` (taxonomy cuối cùng do owner khóa). Xác định SELECT iff chính xác một target thỏa quy tắc chứng minh; ABSTAIN trong các trường hợp còn lại; giữ semantics thống nhất giữa tám họ. Kiểm riêng khả năng có đối chứng SELECT hợp lệ ở F07.

### B02 [HIGH] — Question-only 50% có thể được bảo đảm cơ học bởi cặp phản thực

Với 32 cặp có đúng cùng `question_text` nhưng nhãn ngược nhau, mọi mô hình quyết định chỉ từ `question_text` và cho cùng đầu ra cho hai thành viên đều đúng chính xác một thành viên mỗi cặp, tức **32/64 = 50%**. Vì vậy kiểm tra question-only toàn bộ 64 trường hợp không có sức phân biệt: near-chance không là bằng chứng đã khử shortcut.

**Amend:** Xem paired question-only 50% là *sanity check* bắt buộc, **không** là bằng chứng không rò rỉ. Bổ sung kiểm tra dựa trên các biến thực sự có thể bị lộ (metadata, question+metadata, template fingerprints), kiểm tra phiên bản câu hỏi thay đổi có kiểm soát và đánh giá theo nhóm chưa thấy; không cải biên R8 post hoc sau kết quả.

### B03 [HIGH] — Folds, sample independence, paired leakage chưa được định nghĩa đủ chính xác

`N=64` quan sát nhưng chỉ có **32 đơn vị phản thực ghép cặp**; nhiều trường hợp còn có thể chung event graphs/templates. Stratified CV thông thường thổi phồng hiệu quả và rò rỉ cặp twins. `leave-entire-family-out` với tám họ rất ít đơn vị độc lập và kiểm tra khả năng chuyển họ, khác với ước lượng hiệu quả trong họ. Rater nhìn thấy hai twins có thể suy luận bằng so sánh chứ không phải chấm độc lập.

**Amend:** Cố định trước sinh bảng `pair_id → event_graph_cluster → template_cluster → family → fold_id`; tất cả twins và các case dùng chung latent template/event graph phải ở cùng fold; công bố protocol leave-template-out và leave-family-out **như hai diagnostics tách biệt**, uncertainty theo cluster/pair. Thiết kế blind delivery che `paired_id`, làm mù mẫu song sinh/giảm so sánh trực tiếp, khóa order/assignment trước khi phát hành.

### B04 [HIGH] — “Any deterministic oracle” không khả kiểm theo nghĩa tuyệt đối

Với một tập hữu hạn và ID duy nhất, luôn có thể ghi nhớ ánh xạ ID→nhãn; vì thế “metadata cannot deterministically recover labels” không thể chứng minh cho *mọi* thuật toán. Cần xác định lớp oracle không dùng gold, ngân sách tìm kiếm và yêu cầu out-of-fold. Nhiều weak cues cộng lại có thể rò rỉ dù không có n-gram đơn nhất. Riêng `gold-key` classifier có baseline cơ hội **1/32** trên SELECT nếu chọn ngẫu nhiên một thẻ, khác với baseline **1/2** cho action.

**Amend:** Freeze danh sách oracle/feature allowlist trước tạo R8: order-only, id-only, length-only, source-marker-only, question+metadata, aggregate lexical/regex, card-level selector, action+gold combined; quy định train/test cluster-held-out và null baselines; FAIL hard cho các rule thuộc lớp đã đăng ký chứng minh khả năng oracle trên held-out, HOLD khi bằng chứng không đủ, không tuyên bố proof-of-no-leakage từ near chance.

### B05 [HIGH] — Acceptance/statistical thresholds chưa khóa đầy đủ

`|accuracy − chance| ≥ 0.125` được ghi là *exploratory screening flag*, không phải acceptance rule. Điều này đúng nhưng chưa đủ để G0 khóa giao thức thực thi. Action trên cặp đối nhãn không có 64 independent Bernoulli trials; gold-key chỉ có 32 SELECT cases và null khác. Nếu tùy chọn exact-binomial hoặc permutation sau khi có dữ liệu sẽ tạo researcher degrees of freedom.

**Amend:** Trước sinh khóa: tập kiểm định theo thứ tự, outcome chính/phụ, null mỗi kiểm thử, thống kê tính tại level pair/family, paired/permutation logic, confidence intervals, xử lý nhiều lần kiểm định, hard FAIL vs inconclusive HOLD vs scoped PASS, và định nghĩa QA pass không suy ra khoa học pass. Có thể thực hiện kiểm tra logic/null trên dữ liệu mô phỏng không phải R8, nhưng không dùng R8 để điều chỉnh ngưỡng.

### B06 [HIGH] — Rights/private custody và versioned source-lock chưa được thực chứng

Đặc tả phân biệt đúng AI-authored synthetic vs owner-authored naturalistic, nhưng chưa có owner approval, license/PII proof hoặc xác minh lưu giữ private input/gold/receipt. Chỉ công bố SHA không chứng minh đang sở hữu bytes gốc, quyền truy cập hoặc tính bí mật. Nếu bundle private có entropy thấp, bare hash cũng có thể là oracle brute-force về một số nhãn.

**Amend:** Owner ký duyệt rõ mục đích exploratory, nguồn và quyền dùng, trách nhiệm PII; chỉ định private custodian, nơi lưu, access control và receipt kiểm tra bytes/SHA; công bố commitment cho gói hoàn chỉnh có nonce đủ entropy nhưng không tiết lộ nội dung; freeze `source_lock`, schema, generator, code SHA, folds/seed trước G3; quy định unblind chỉ sau khi A/B scoring đóng băng và đối chiếu.

## 4. Six mandatory reviewer answers

| Question | Answer | Status |
|---|---|---|
| Q1. Cân bằng label trên `relation_family` có giữ estimand cũ? | Không. Đó là estimand mới; V4 CAL protocol/version, target và reporting riêng. | `PASS_DIRECTION / HOLD_LOCK` |
| Q2. Matched pairs tạo shortcut/correlated folds? | Có. Twins, template reuse, và exposure across A/B dẫn đến leakage; group-split và blind delivery cần freeze. | `HOLD_B03` |
| Q3. Public metadata có thể khôi phục label/gold? | Có nguy cơ. Chưa có chứng cứ thực nghiệm R8; phải test nhiều feature classes out-of-fold. | `HOLD_B04` |
| Q4. Fixed-marker controls đủ xác nhận không rò rỉ? | Không. Hữu ích để phát hiện leak đã biết, không chứng minh không có leak mới; question-only paired 50% là tầm thường. | `HOLD_B02_B04` |
| Q5. Rights/private custody đủ để mở exploratory? | Đúng hướng quy phạm, nhưng chưa có bằng chứng owner/custodian; không được mở generation. | `HOLD_B06` |
| Q6. Threshold pre-registered và calibrated? | Chưa. `0.125` chỉ là screening; phải khóa null, test, multiplicity, và quy tắc PASS/HOLD/FAIL trước data. | `HOLD_B05` |

## 5. Review adjudication and gate disposition

| Gate | Review disposition |
|---|---|
| G0 — independent design review | `COMPLETED_WITH_HOLD_FINDINGS`; **không** phê chuẩn `PASS_SCOPED_DESIGN` cuối cùng |
| G1 — owner adoption and rights | `HOLD_NOT_ATTESTED` |
| G2 — private custody/source validator | `HOLD_NOT_EXECUTED` |
| G3 — authoring R8 | `NOT_AUTHORIZED` · `NOT_GENERATED` |
| G4 — independent semantic and anti-shortcut QA | `NOT_EXECUTED` |
| G5 — A/B blinded CAL | `SEALED` |
| G6 — thresholds and PROBE256 | `NOT_FROZEN` · `SEALED` |

**Final:** `HOLD_R8_PROTOCOL_AMENDMENT_REQUIRED_NO_GENERATION`.

**Giới hạn quyền phán quyết:** Đây là nhận định của independent AI reviewer về **nguồn đặc tả**, không phải reviewer người thật, không chứng nhận license/PII/custody, không ra quyết định owner và không tuyên bố R8 có dữ liệu hay kết quả khoa học.

## 6. Next operation (proposed)

`TTM_VM_V4_R8_V2_BLOCKING_PROTOCOL_AMENDMENT_AND_FROZEN_INDEPENDENT_REVIEW_READBACK_NO_GENERATION`

Owner/agent soạn **một** amendment V2 giải quyết B01–B06, với artifact tối thiểu: (i) V4 CAL estimand + target/gold/abstain ontology; (ii) matrix 8 family với proof of paired feasibility; (iii) frozen pair/template/family folds + blinding allocation; (iv) negative controls, nulls, statistic/gates, leave-out handling; (v) private custody/source-rights decision form, không ghi nhận quyền đã được phê duyệt nếu chưa có chữ ký/receipt. Reviewer mới chỉ đọc đặc tả sau sửa; nếu đạt mới trình owner adoption G1 và custody G2. **Không sinh candidate R8 cho tới khi G0, G1, G2 đóng PASS đúng thẩm quyền.**