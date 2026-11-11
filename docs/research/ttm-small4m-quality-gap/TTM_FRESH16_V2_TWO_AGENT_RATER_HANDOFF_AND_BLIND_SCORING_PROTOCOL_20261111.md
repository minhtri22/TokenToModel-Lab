# TTM FRESH16 — Hai vai trò chấm điểm và quy trình giao việc một lần

**Dành cho owner/executor tổ chức phần đánh giá, không đưa nguyên văn tài liệu này vào packet chấm cá thể vì nó tiết lộ H1/H2/điều kiện cặp.**  
**Source:** original prompt blob `6299a073f0b7c7f8ea890ba9d9b29eaed9442f1f`; original rubric blob `69668664df23d2246cd65935ab049054aea43e7a`; adopted V2 blob `27b994b3b3283b2611af21d63acc5d37abf45013`.

**Phân tách vai trò:** executor chuẩn bị/sinh dữ liệu khi **được owner cấp GO riêng**; `FRESH16_S1_OUTPUT_RATER` chỉ chấm từng output; `FRESH16_S2_PAIR_ADJUDICATOR` chỉ so sánh cặp sau khi S1 đã khóa. Hai phiên mới có danh tính/phiên bản rõ ràng là đủ cho pilot; không tạo micro-permit cho từng bước. Protocol Reviewer trước đó không làm S1 hoặc S2.

## Stage 1 — Output Rater (new independent session)

**Giao cho rater cùng với packet gồm 32 bản ghi được shuffle, chỉ chứa `opaque_id`, `prompt_text`, `generated_text_only`, không kèm pair_id/A-B/step/score lịch sử.**

> Bạn được giao chấm các đoạn tiếp nối truyện. Chỉ đánh giá **văn bản mới được sinh**, dựa trên prompt đầy đủ để xác định actor, goal và thay đổi dữ kiện. Không thưởng cho prompt copy, từ/cụm từ chỉ điền slot hoặc nhắc lại ý định có sẵn. Adherence 0=trống/không hiểu được hoặc mâu thuẫn chính; 1=chỉ điền từ/lặp/dang dở chưa có sự kiện mới; 2=có một sự kiện/hậu quả mới quan sát được dùng đúng vai trò/dữ kiện/mục tiêu, không mâu thuẫn chính; 3=sự kiện mới và diễn biến tiến triển nhất quán. Với điểm≥2 hãy trích span **từ generated_text_only** chứng minh sự kiện thực sự mới. EOS sớm chấm theo phần đã sinh, không yêu cầu độ dài cố định hay câu hoàn chỉnh. Chấm cả coherence, entity consistency, causal continuation theo rubric 0..3. Không suy đoán checkpoint, ghép cặp hay xem đánh giá cũ. Xuất đầy đủ 32 bản ghi điểm và tên/phiên bản/session của bạn; không tự giải mù. Không thay input, không chạy mô hình.

**S1 lock:** tạo JSON điểm/nhận xét và SHA256; owner commit receipt chứa SHA trước khi gửi cặp cho S2. Không sửa điểm S1 sau khóa.

## Stage 2 — Pair Adjudicator (another independent session)

**Giao cho adjudicator packet 16 opaque pairs, mỗi cặp 2 prompt + generated text + adherence cá thể đã khóa; không có checkpoint labels, H1/H2 counts hay mapping giải mù.**

> Bạn phân xử tương phản theo dữ kiện giữa hai đầu ra **không biết checkpoint**. H2 pair=1 chỉ khi: cả hai adherence S1≥2; có **sự kiện mới** trong cả hai; vai trò/đối tượng/địa điểm, hành động hoặc kết quả gắn đúng can thiệp khác nhau một cách có ý nghĩa; không mâu thuẫn; và đổi dữ kiện trong prompt sẽ làm tương phản trở nên kém phù hợp/ngữ nghĩa không còn được giải thích đúng. **Không yêu cầu khác động từ**, nhưng cũng **không thưởng chỉ vì thay một danh từ**. Nhãn bắt buộc: `LEXICAL_SWAP_ONLY`, `SEMANTIC_ROLE_BINDING`, `FACT_CONDITIONED_ACTION`, `GENERIC_COMMON_VALID`, `UNRELATED_DIVERGENCE`, `CONTRADICTORY_OR_UNINTERPRETABLE` hoặc `AMBIGUOUS_NON_DIAGNOSTIC`. Giải pháp chung phù hợp ở cả hai điều kiện là H2=0 mà **không xem là lỗi mô hình**. Ghi event tuple, bằng chứng từ text mới sinh và swap countercheck. Không sửa S1, không yêu cầu checkpoint hay TEST, không đổi tiêu chí. Xuất đủ 16 cặp và tên/phiên bản/session.

**S2 lock:** tạo JSON quyết định cặp và SHA256; owner commit receipt SHA trước khi mở checkpoint và tính H1/H2. Nếu còn tranh chấp không thể giải quyết mà không thay quy tắc, giữ output gốc và kết luận HOLD, không chạy lại.

## Stage 3 — Final scoring

Chỉ sau **S1 SHA và S2 SHA** đã được ghi nhận trên GitHub, executor giải mù mapping, tính H1/H2 đúng frozen denominator và ngưỡng. Giữ toàn bộ điểm bất lợi/cặp không phân biệt được; không dùng kết quả để đổi prompt/checkpoint/threshold. Mọi claim `QUALITY_CANDIDATE_SCOPED_STEP1024_ONLY` đều phải ghi `LOCAL_CONTEXT_FACT_CONDITIONED_CONTINUATION_EXPLORATORY`, chỉ một AI rater không phải đồng thuận giữa nhiều người.

**Hiện trạng:** file này là `ROLE_ASSIGNMENT_PLAN`, chưa có rater session thật, S1/S2 scores hoặc CPU outputs. Owner đã `ADOPT_V2`, **chưa cấp GO inference**.

**Bước thực hiện tiếp theo:** owner/executor tạo hai phiên độc lập lúc triển khai, giữ khóa nguồn/score và chỉ sinh 32 outputs sau một quyết định GO duy nhất.
