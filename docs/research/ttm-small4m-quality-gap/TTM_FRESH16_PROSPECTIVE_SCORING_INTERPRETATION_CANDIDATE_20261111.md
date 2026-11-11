# TTM FRESH16 — Phụ lục diễn giải rubric tiền thực nghiệm (CANDIDATE)

**Status:** `PROSPECTIVE_AMENDMENT_CANDIDATE_NOT_ADOPTED`  
**Why:** Reviewer phát hiện F01 `CLOZE_FALSE_POSITIVE` và F02 `COMMON_VALID_RESPONSE_CP04_CP08` trong kiểm toán ngày 2026-11-11.  
**Reference:** frozen prompt Git blob `6299a073f0b7c7f8ea890ba9d9b29eaed9442f1f`; frozen rubric Git blob `69668664df23d2246cd65935ab049054aea43e7a`.  
**Scientific exposure:** `NO_FRESH16_OUTPUTS_EXIST` theo phạm vi biên bản hiện có; phải xác minh lại ở quyết định thực thi. Phụ lục này có thể thay đổi điểm → phải được protocol reviewer + owner chấp thuận trước khi xem bất kỳ output.

## 1. Thang điểm gốc giữ nguyên 0..3, nhưng cần định nghĩa hành vi chấm

Dự kiến áp dụng **chỉ cho văn bản model vừa sinh**, không cộng điểm từ chính prompt:

- **Điểm adherence=0**: trống/EOS ngay; continuation vô nghĩa; hoặc phản bác trực tiếp dữ kiện chủ đạo đã khóa.
- **Điểm adherence≤1 (cloze-only)**: chỉ sinh từ/cụm từ hoàn thành slot đang dang dở (`box`, `Mom`, `red bag`, `cat`, `feed the dog`, v.v.), kể cả đúng fact; chỉ echo dữ kiện, hoặc dừng mà không có **hành động/sự kiện mới quan sát được**. Khác biệt A/B ở vài từ không đủ H2.
- **Điểm adherence=2**: sau khi hoàn thành slot (nếu có), thêm ít nhất **một hành động/sự kiện mới** liên quan đến actor, fact và mục tiêu đã nêu; không trái điều kiện chính; được phép sai sót nhỏ.
- **Điểm adherence=3**: hành động/sự kiện mới tiến triển hợp lý, giữ các actor/object/fact/goal xuyên suốt và không mâu thuẫn.

**Lưu ý khoa học:** Quy tắc `cloze-only <=1` là **một diễn giải mới cần đồng thuận**; không tự nhận là rubric frozen đã rõ như vậy. Giữ nguyên điểm 0..3 và ngưỡng H1/H2, nhưng version scoring interpretation phải thay đổi được theo dõi minh bạch.

**Ví dụ minh họa TRƯỚC THỰC NGHIỆM — không phải đầu ra model:**

| Prompt | Mẫu mới sinh giả định | Adherence theo phụ lục | Lý do |
|---|---|---|---|
| CP01-A | `box.` | ≤1 | Chỉ hoàn thành slot |
| CP01-A | `box and found her hat there.` | có thể ≥2 | Có sự kiện tìm thấy mũ; phải xem tính mạch lạc |
| CP02-B | `Dad.` | ≤1 | Chỉ điền holder |
| CP02-B | `Dad to return the drum, and Dad handed it back.` | có thể ≥2 | Thêm diễn biến đáp ứng mục tiêu |
| CP05-A | `red bag.` | ≤1 | Chỉ điền tên túi |
| CP05-A | `red bag and carried them safely outside.` | có thể ≥2 | Có diễn biến mới đúng ràng buộc |
| CP07-A | `feed the dog.` | ≤1 | Chỉ hoàn thành việc đã được nêu |
| CP07-A | `the kitchen and filled the dog's bowl before playing.` | có thể ≥2 | Hoàn thành lời hứa bằng hành động |

Các ví dụ này là **gold guidance về cách diễn giải**, không phải prompt điều chỉnh hoặc chọn output. Output rater không được cung cấp kết quả FRESH12/đánh giá reviewer trước để tránh định hướng điểm; có thể cung cấp ví dụ trung tính từ một fixture tách biệt do protocol reviewer phê chuẩn, không phải từ chính 16 prompt nếu muốn giảm rater anchoring.

## 2. H2 và các cặp CP04/CP08

Giữ nguyên định nghĩa H2 cũ **cả hai** adherence≥2 **và** diễn biến khác nhau một cách phù hợp với fact; ≥6/8 pairs, ≥1 thành công/category.

- Trường hợp cả A và B có cùng giải pháp hợp lệ chung: adherence từng output có thể ≥2, nhưng H2 pair=0 vì không thể hiện **distinct fact-sensitive action**. Gắn nhãn giải thích `NON_DIAGNOSTIC_COMMON_VALID_ACTION`, **không** xem đó là lỗi logic của model.
- Trường hợp A/B khác vài từ nhưng cùng hành động generic: H2=0, `LEXICAL_SWAP_NOT_SEMANTIC_CONTRAST`.
- Trường hợp cả hai output sử dụng dữ kiện riêng, thêm hành động phân biệt đúng nghĩa và adherence≥2: H2=1.
- Đặc biệt CP04 locked/open và CP08 wet/dry: rater không được ép bản A/B phải chọn hành động duy nhất nếu có nhiều cách đúng; chỉ đánh dấu H2 thành công khi có sự tương phản tích cực quan sát được. **Không loại cặp/đổi denominator** sau khi biết model output.

Nếu việc chấm H2 cho CP04/CP08 có ý nghĩa không xác định, ghi thêm cờ `PAIR_NON_DIAGNOSTIC` (secondary descriptive). Không biến flag đó thành phép sửa ngưỡng H2.

## 3. Template trường score và vai trò

Mỗi phiếu ẩn danh cần:
`opaque_id`, `prompt_text`, `generated_text_only`, `is_empty_or_eos`, `adherence_0_3`, `coherence_0_3`, `entity_consistency_0_3`, `causal_continuation_0_3`, `has_new_event_after_slot`, `cloze_only`, `fact_contradiction`, `evidence_new_text_span`, `rater_id_or_model_version`, `rubric_version`, `scored_at`.

Rater phải chấm 32 output **mù nhãn checkpoint và pair**; rater nhìn prompt đầy đủ nên không thể mù với fact. Mapping từ opaque IDs tới checkpoint/pair/variant phải đóng riêng trước giải mù, chỉ mở sau SHA lock cả 32 phiếu. H2 nên được phân xử bởi adjudicator theo mapping sau giai đoạn chấm cá thể; adjudicator phải công bố quy tắc và xử lý bất đồng trước model output. Đánh giá đồng thuận (inter-rater) chỉ báo nếu thực sự có ≥2 người chấm độc lập.

**Tư cách rater:** external protocol reviewer đã tự từ chối output-rater role, không được tự động gán họ. Output rater mới cần được owner chỉ định rõ tên hoặc model+version, thời điểm, quyền đọc, phương thức lock score, tách khỏi executor. Một AI rater duy nhất chỉ đủ kết luận `SINGLE_RATER_EXPLORATORY_ONLY`.

## 4. Không mở rộng claim

Ngay cả nếu H1+H2 PASS, claim cao nhất: `QUALITY_CANDIDATE_SCOPED_STEP1024_ONLY` với chú thích `LOCAL_CONTEXT_FACT_CONDITIONED_CONTINUATION_EXPLORATORY`, không gọi `CAUSAL_REASONING_PASS`, `LONG_STORY_COHERENCE_PASS` hoặc `PRODUCT_READY`.

Ngược lại, nếu H1/H2 không đạt, chỉ nói chưa chứng minh được theo bộ kiểm tra nhỏ có cấu trúc cloze/confounding này; không kết luận mô hình nói chung thất bại.

## 5. Quyết định chấp thuận

**Owner:** `NOT_APPROVED`. **Protocol Reviewer:** `NOT_REVIEWED_NEW_AMENDMENT`. **Output Rater Custody:** `UNASSIGNED`.

Phụ lục này là ứng viên, chưa có hiệu lực với khoa học. Nếu owner không chấp thuận, không dùng phụ lục để chấm. Nếu owner chấp thuận và protocol reviewer thẩm định, ghi exact SHA của phụ lục và receipt accepted-before-inference; tiếp tục giữ nguyên các nguồn cũ với công khai revision/interpretation delta. Không cần huấn luyện, inference, rerun TEST hay source QA.

**Bước thực hiện tiếp theo:** review phụ lục này độc lập và phê duyệt/bác bỏ phiên bản scoring trước khi khóa rater; vẫn `NO_GO_HOLD`.
