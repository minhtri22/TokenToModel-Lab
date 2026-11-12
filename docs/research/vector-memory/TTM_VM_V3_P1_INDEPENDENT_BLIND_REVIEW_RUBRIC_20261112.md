# TTM Vector Memory V3 — Quy trình hai người thẩm định mù cho P1 Unseen Paraphrase

**Operation:** `TTM_VM_V3_FRESH256_NEGATIVE_GROUND_TRUTH_AND_NONORACLE_SOURCE_ONEPACKET_QA_FREEZE`  
**Loại:** Annotation custody (quản trị nhãn), **chưa phải kết quả science**.  
**Tình trạng:** `PENDING_TWO_INDEPENDENT_HUMAN_REVIEWS`; không có phiếu chấm thật nào được giả định PASS.

## 1. Phạm vi đã khóa trước khi chấm

P1 có chính xác **32** câu hỏi. Mỗi câu hỏi có 32 card với `key`, `source_id`, `retrieval_text`. Các cụm từ mới nằm ngoài từ điển và surface template V2; bảng ánh xạ đề xuất `PROPOSED_P1` nằm trong generator đã đóng băng, **chưa phải bằng chứng ngữ nghĩa độc lập**. Yêu cầu hai người khác nhau, ở hai phiên/không gian tách biệt, đánh giá mà **không xem source, answer, target_key, truth_constraints, đáp án hoặc nhận xét của người còn lại**.

Fixture riêng tư owner: `_evidence/vector-memory/TTM_VM_V3_FRESH256_NONTEST_PRIVATE_20261112.json` · SHA256 `d473292d40dfb475d0b44f7d393341e19d846308820dcb4f5cbac6acb2c0e543`. Các reviewer chỉ được nhận packet blinded, **không** được nhận fixture đầy đủ.

## 2. Một gói tạo hai packet riêng biệt

Script đã khóa `tools/research/vector-memory/v3_p1_reviewer_custody.py` chỉ tạo hai file riêng khi chủ máy chạy source QA packet:

- `.../TTM_VM_V3_P1_BLIND_HUMAN_REVIEWS_20261112/P1_REVIEW_A_TEMPLATE.json`
- `.../TTM_VM_V3_P1_BLIND_HUMAN_REVIEWS_20261112/P1_REVIEW_B_TEMPLATE.json`

Mỗi packet chứa đúng 32 câu hỏi + index public. Không chứa `gold_action`, `answer`, `target_key`, `stratum`, `correct_memory`, `wrong_memory` hoặc `truth_constraints`. Mỗi reviewer chỉ được xem **packet của mình**, và bản chấm B không được xem ý kiến A.

## 3. Phải điền gì, không được suy luận gì

Reviewer xác định một card duy nhất theo ý nghĩa câu hỏi và thông tin công khai, không dùng luật nguồn dự kiến hoặc bảng giải mã từ generator. Điền cho cả 32 hàng:

- `selected_key`: key của card được chọn; **null** nếu không đủ căn cứ hoặc nhiều card hợp lý.
- `reason`: giải thích ngắn bằng ngôn ngữ tự nhiên, ít nhất 8 ký tự; không chỉ copy mã key.
- `confidence`: số nguyên 0–3, ghi mức tin cậy.

Điền metadata `rater_id` khác nhau, `reviewed_at_iso8601`, và xác nhận trung thực hai trường `attest_no_gold_or_other_review_access=true` và `attest_independent_semantic_mapping=true` **chỉ khi đúng sự thật**. Hai bản hoàn thành phải lưu thành `P1_REVIEW_A_SIGNED.json` và `P1_REVIEW_B_SIGNED.json` trên cùng thư mục D:, không sửa templates.

Phần mềm không tự thay mặt hai người chấm, không điền đáp án từ generator, không gọi một bài kiểm tra tự động là “two independent human reviewers”. `rater_id` và hai khai báo này là **attestation**, không phải chữ ký số hay bằng chứng mật mã chống thông đồng.

## 4. Cổng phân xử duy nhất, không chọn lại seed/câu hỏi

`v3_p1_reviewer_custody.py` sẽ đối chiếu rằng cả hai packet có cùng SHA fixture, 32 case không đổi, hai `rater_id` khác nhau, attestation hợp lệ, và **cả hai độc lập chọn cùng key đúng theo private ground truth ở 32/32 case**.

- Nếu cả hai biên nhận có thực và hoàn toàn khớp: `PASS_TWO_DISTINCT_BLIND_HUMAN_ATTESTATIONS`, tạo receipt riêng tại D:, không upload private per-story hoặc danh tính reviewer.
- Nếu thiếu reviewer, khác ý kiến, thiếu thông tin, còn null hoặc nhầm semantic mapping: **`HOLD_DATA_ADJUDICATION`**. Không loại câu khó, không thay synonym, không chỉnh generator/retriever đã khóa hoặc chạy khoa học để “cứu” kết quả.
- Trường hợp thông tin bị lộ/trùng người review: `HOLD_INDEPENDENCE_NOT_ESTABLISHED`; cần nguồn dữ liệu mới và amendment riêng nếu tiếp tục.

## 5. Giới hạn minh bạch

Các paraphrase P1 mới chỉ **không xuất hiện trong dictionary/surface template V2**. Retriever V3 đã chứa ánh xạ `PROPOSED_P1` từ trước. Ngay cả khi P1 sau này PASS, đó không chứng minh khả năng tổng quát hóa cho cụm từ hoàn toàn chưa từng được cấu hình trong Retriever. Kết quả là bài kiểm tra **định danh mô tả kiểm soát với từ điển V3 mở rộng**, không phải semantic retrieval mở.

**Cho đến khi có biên nhận:** `SOURCE_CODE_QA=PASS_99/99`, `P1_HUMAN_SEMANTIC_CUSTODY=HOLD`, `OWNER_SOURCE_RELEASE=HOLD`, `CPU_SCIENCE=NOT_AUTHORIZED`, `TEST=SEALED`.
