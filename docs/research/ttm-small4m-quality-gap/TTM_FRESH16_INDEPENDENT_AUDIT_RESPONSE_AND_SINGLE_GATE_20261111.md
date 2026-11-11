# TTM FRESH16 — Tiếp nhận phán quyết reviewer độc lập và cổng đóng duy nhất

**Ngày tiếp nhận:** 2026-11-11  
**Operation:** `TTM_FRESH16_RATER_CUSTODY_AND_SCORING_INTERPRETATION_FINAL_GATE`  
**Nguồn báo cáo:** Văn bản kiểm toán độc lập do owner chuyển vào hội thoại, nhãn `TTM_FRESH16_INDEPENDENT_PREREG_SOURCE_RUBRIC_AND_REVIEWER_CUSTODY_AUDIT`; reviewer tự khai `ChatGPT / GPT-6`, vai trò `INDEPENDENT_PROTOCOL_SOURCE_REVIEWER`, **không phải output rater**.  
**Frozen source HEAD reviewed:** `1583c5b475407799bfca75b503ddf359de7fda69`.  
**Phán quyết nguyên văn về trạng thái:** `HOLD` · `NO_GO_HOLD` · 3 PASS, 5 HOLD, 0 FAIL.  
**Phân loại tài liệu:** intake / owner review of an external report; **không** là kết quả thực nghiệm, không thay cho reviewer độc lập, không tái chạy phép thử.

## 1. Phản hồi theo 8 cổng

| Gate | Kết quả independent reviewer | Phân xử khi tiếp nhận | Bằng chứng / giới hạn |
|---|---|---|---|
| R1 Source Integrity | HOLD | **Giữ HOLD independent raw bytes** | Git/receipt đối chiếu; reviewer chưa trực tiếp băm byte checkpoint/BPE trên Windows. QA gốc trước đó PASS về source; hai phạm vi không được đồng nhất |
| R2 Data Leakage | PASS_SCOPED | **Công nhận PASS trong 28 prompt công khai** | 16 Q1 + 12 FRESH12, 0 exact duplicate, Jaccard 3-gram 0.01754386; không tuyên bố mới so với toàn TRAIN/TEST |
| R3 Tokenization | HOLD | **Giữ HOLD reviewer direct re-execution** | Receipt nguồn ghi 16 roundtrip, 28–47 token, BPE manifest pinned; reviewer không chạy lại private manifest |
| R4 Counterfactual Design | HOLD | **Chấp nhận rủi ro cấu trúc** | CP04 locked/open door và CP08 wet/dry blanket có common valid response; một số prompt thiên cloze |
| R5 Scientific Rubric | HOLD | **Phải khóa quy tắc giải thích trước đầu ra** | Đầu ra chỉ điền đúng slot không được xem là truyện tiếp nối, trong khi rubric cũ có khả năng diễn giải khác nhau |
| R6 Reviewer Independence | HOLD | **Giữ HOLD** | Output rater chưa có danh tính/custody, chưa có scoring packet mù/niêm phong |
| R7 Execution Contract | PASS_DESIGN_ONLY | **Giữ PASS_DESIGN_ONLY** | 16 prompts × 2 checkpoints, greedy, 64 new tokens, context256, CPU cap; không phải execution permit |
| R8 Scientific Governance | PASS_SCOPED | **Giữ PASS_SCOPED** | FRESH12 lịch sử `NO_DEMONSTRATED_SEMANTIC_GAIN_SCOPED`; main và lineage giữ nguyên; không mở TEST |

## 2. Bốn phát hiện reviewer và quyết định

**F01 (HIGH) — Cloze false positive:** CP01/02/05/06/07 gợi sẵn một từ/vật/hành động ở cuối prompt. Một từ chỉ điền slot **không chứng minh tạo diễn biến mới**, dù cho biết mô hình dựa vào ngữ cảnh cục bộ. **Phản hồi:** tạo phụ lục chấm điểm *candidate*, yêu cầu sự kiện/hành động mới để nhận điểm adherence ≥2; không giả mạo là rubric gốc đã được reviewer chấp thuận.

**F02 (HIGH) — CP04/08 common-valid response:** cả A và B có thể hợp lý với cùng hành động. **Phản hồi:** không sửa prompt hay giảm mẫu H2; nếu cùng một diễn biến chung hợp lý, chấm adherence từng đầu ra theo thực tế, nhưng H2 pair=0 nếu không có phản ứng khác nhau gắn với fact. Gắn nhãn `NON_DIAGNOSTIC_COMMON_VALID_ACTION` và nêu đây là giới hạn của test, *không* gọi mô hình sai ở câu đó.

**F03 (MEDIUM) — Scope of inference:** H1/H2 chỉ là ngưỡng sàng lọc nội bộ cho local context/fact-conditioned continuation; không chứng minh causal reasoning, semantic comprehension tổng quát hoặc truyện dài. Giữ checkpoint step1024 primary, step1280 descriptive; không chọn post-hoc.

**F04 (HIGH) — Rater custody missing:** reviewer thiết kế từ chối vai trò Output Rater, điều đó được tôn trọng. Cần output rater mới **tách khỏi** người thiết kế/generator/reviewer protocol; chuẩn bị tập phiếu 32 trường hợp có mã ẩn danh, rater nhìn prompt/continuation nhưng không nhìn checkpoint, A/B label, pair IDs, thresholds, predicted verdict, mẫu kết quả FRESH12. Lock scores SHA trước giải mù. Chưa gán identity/phiên bản nên giữ HOLD.

## 3. Không hồi tố nguồn khóa

Nguồn FRESH16 bất biến: Git prompt blob `6299a073f0b7c7f8ea890ba9d9b29eaed9442f1f`, rubric blob `69668664df23d2246cd65935ab049054aea43e7a`, H1 ≥12/16 adherence≥2 và H2 ≥6/8 paired fact-sensitive (≥1 pair mỗi category), 16 prompt, 8 cặp, hai checkpoint frozen (step1024 primary, step1280 descriptive).

Phụ lục ứng viên `docs/research/ttm-small4m-quality-gap/TTM_FRESH16_PROSPECTIVE_SCORING_INTERPRETATION_CANDIDATE_20261111.md` được tạo **trước khi có bất kỳ đầu ra FRESH16 nào**, nhưng là bản diễn giải bổ sung **có thể ảnh hưởng tới điểm**. Trạng thái `PROSPECTIVE_AMENDMENT_CANDIDATE_NOT_ADOPTED`. Để dùng nó, owner phải phê chuẩn rõ và một protocol reviewer xác nhận trước inference, tạo revision receipt/sha mới. Nếu không phê chuẩn, vẫn NO-GO; tuyệt đối không nói phụ lục này là nội dung đã khóa từ đầu.

Không tái chấm TEST, FRESH12 hay Q1, không chạy inference/training, không ghi `lineage.md`.

## 4. Quyết định duy nhất

`EXECUTION_DECISION=NO_GO_HOLD`. Nguồn kỹ thuật phía owner vẫn `PASS_SOURCE_BYTES_NATIVE_16_OF_16`; reviewer audit R1/R3 HOLD theo **phạm vi xác minh độc lập**, không biến thành source FAIL.

**Để đủ điều kiện trình một quyết định duy nhất cho 32 output CPU:** (a) owner chấp thuận/bác bỏ phụ lục scoring với lịch sử thay đổi minh bạch; (b) protocol reviewer chấp nhận/không chấp nhận construct validity scope; (c) output rater độc lập được nhận diện, chốt blind packet + adjudication; (d) runner CPU source-only đã khóa, không model forward, không chọn outcome. Nếu một điều kiện HOLD, phán quyết vẫn NO-GO. Không tạo thêm các micro-gate riêng lẻ.

**Bước thực hiện tiếp theo:** `TTM_FRESH16_SCORING_AMENDMENT_OWNER_PROTOCOL_REVIEW_AND_RATER_CUSTODY_SINGLE_GATE` — quyết định chấp nhận phụ lục, gắn output rater, đóng gói blind scoring, rồi trình owner GO/NO-GO; vẫn zero science.
