# TTM-Small-4M — Thiết kế kiểm tra bám prompt và chất lượng tiếp nối truyện

**Operation:** `TTM_SMALL4M_FRESH_CONTINUATION_QUALITY_GAP_REVIEW_DESIGN_ONLY`  
**Ngày:** 2026-11-11  
**Trạng thái:** `DESIGN_ONLY_CANDIDATE_NOT_SCIENCE_LOCKED`  
**Nhánh nghiên cứu độc lập:** `research/ttm-small4m-prompt-adherence-continuation-design-20261111`; **main nguồn:** `5d52e32f20021e36f08f284ef9864d3ba36dbead`.

## 1. Điều đã biết và câu hỏi mới

1. T4 gốc: P02 3.749.376 tham số, BPE 2.048, context 256; checkpoint step1024 đã có NLL VAL tốt hơn bigram, TEST 64 truyện đã sử dụng và **cấm tái chấm**. Checkpoint step1280 đã được tạo trong nghiên cứu riêng; không huấn luyện tiếp ở đây.
2. T5 Ollama tùy chỉnh: full raw logits đạt 4/4 ở CPU F32 nhưng **không** nói mô hình có chất lượng ngôn ngữ cao; nhánh `research/ttm-t5-ollama-full-logits-20261111` còn tồn tại do owner chưa chạy lệnh retire, archive đã xác minh tồn tại. Nghiên cứu này **không** đụng hai ref đó.
3. FRESH12: 48 output và 144 điểm reviewer AI; 35/48 output có điểm bám prompt bằng 0, và trimming vs trailing-space không chứng minh semantic gain. Đã tìm ra **trailing ASCII space** là nhiễu serialization đối với token đầu. Không dùng FRESH12 để lựa chọn prompt/checkpoint sau khi thấy điểm; không sửa đánh giá đó.
4. Khoảng trống riêng cần trả lời: **mô hình có sử dụng dữ kiện và mục tiêu của truyện trong prompt để tạo tiếp nối phù hợp không**, hay chỉ tạo các câu có vẻ trôi chảy nhưng chuyển sang chuyện chung?

## 2. Giả thuyết và đối chứng

- **H1 — bám nội dung (prompt adherence):** ở checkpoint T4 gốc bước 1.024, ít nhất 12/16 tiếp nối mới được chấm từ 2/3 trở lên trên thang bám sự kiện/đối tượng/mục tiêu.
- **H2 — nhạy với thay đổi sự kiện (counterfactual fact sensitivity):** ít nhất 6/8 cặp đối chứng thay đổi một cụm dữ kiện có hai tiếp nối khác biệt **đúng ngữ nghĩa tương ứng**, không chỉ khác chuỗi ký tự; tối thiểu 1 cặp đạt trong mỗi nhóm.
- **H0 (đối lập):** không đủ bằng chứng cho một hoặc cả hai ngưỡng trong phạm vi nhỏ. Đây là ngưỡng sàng lọc ứng viên (candidate screening), **không** phải kiểm định ý nghĩa thống kê/khả năng khái quát cho mọi đầu vào.
- **Đối chứng 1 — cặp tối thiểu (minimal pair):** mỗi tình huống có bản A/B, cùng chuỗi tiền tố/hậu tố, chỉ thay một cụm sự kiện. Kiểm tra mô hình *đổi hành động hoặc diễn biến đúng theo sự kiện* (ví dụ súp quá nóng vs quá lạnh, cửa khóa vs mở), chứ không thưởng vì nhắc lại một từ.
- **Đối chứng 2 — checkpoint giữ cố định cách đánh giá:** cùng 16 prompt, cùng tokenizer, cùng greedy và ngân sách cho bước 1.024 (chính) và 1.280 (phụ, chỉ mô tả). Không chọn checkpoint thắng rồi thay phán quyết H1/H2.
- **Không dùng:** TRAIN/VAL/TEST cho prompt, FRESH12 12 prompt cũ, Q1 16 prompt cũ, Ollama FL01–FL04, dữ liệu TinyStories có thể nhận dạng; không lấy TEST đã niêm phong làm kiểm định mới.

## 3. Bộ 8 cặp = 16 prompt mới được tác giả dự án tạo

**Nguồn dữ liệu:** `artifacts/research/ttm-small4m-quality-gap/TTM_FRESH_CONTINUATION_PROMPT_SET_CANDIDATE_V1_20261111.json`, trường `new_prompts[].prompt_text` là **toàn bộ văn bản sẽ đưa vào tokenizer trong một nghiên cứu tương lai**. Nội dung này chưa chạy inference. Hash nội dung được cố định bằng Git blob của chính file ở commit tạo. Trước khi run thật, phải xác minh tokenizer, chiều dài BPE, so trùng bổ sung với những prompt lịch sử khác *chỉ từ nguồn được phép*, xác minh source/checkpoint hash, sau đó khóa chính thức; không sửa prompt theo đầu ra.

| Cặp | Nhóm | Dữ kiện A ↔ B | Điều phải quan sát trong tiếp nối |
|---|---|---|---|
| CP01 | Vị trí | hat trong **box / bag** | tìm đúng vật chứa, không nhầm vị trí |
| CP02 | Chủ sở hữu | drum ở **Mom / Dad** | hỏi đúng người |
| CP03 | Nhân quả | soup **too hot / too cold** | làm nguội / hâm nóng, không gây phản tác dụng |
| CP04 | Nhân quả | door **locked / open** | ứng xử phù hợp với cửa khóa / cửa mở |
| CP05 | Quy tắc | túi dùng được **red / blue** | dùng túi nguyên, không đặt sách vào túi thủng |
| CP06 | Quy tắc | con vật cần nghỉ **cat / dog** | giữ đúng con vật bị ốm ở trong nhà |
| CP07 | Mục tiêu | **feed dog / water flowers** | làm đúng việc đã hứa trước khi chơi |
| CP08 | Mục tiêu | blanket **wet / dry** | phản ứng phù hợp để giữ em gái ấm |

**Kiểm tra nguồn đã thực hiện (chỉ dùng tài liệu GitHub công khai của TTM):** 16/16 ID và chuỗi prompt mới phân biệt; 0 trường hợp trùng nguyên văn sau chuẩn hóa với **12 FRESH12 + 16 Q1** đã công bố; không prompt nào có dấu cách cuối; cùng suffix cho cả hai biến thể của một cặp. **Chưa** chạy tokenizer/BPE, không quét dữ liệu TEST hay toàn TRAIN, không khẳng định hoàn toàn độc lập khỏi mọi lịch sử.

## 4. Chấm điểm (Scoring) và cách tránh đo sai khả năng bám prompt

Mỗi tiếp nối được chấm **chỉ dựa vào văn bản mới sinh** và prompt gốc được cung cấp cho reviewer. Tuyệt đối không cộng điểm vì các sự kiện vốn đã nằm trong phần prompt, hoặc vì echo/copy nguyên prompt. Nếu có EOS sớm, giữ nguyên đầu ra trống/ngắn để chấm, không retry.

| Chỉ số | 0 | 1 | 2 | 3 |
|---|---|---|---|---|
| **Bám prompt — PRIMARY** | chuyển sang truyện khác hoặc mâu thuẫn dữ kiện chính | nhắc 1 chi tiết nhưng lệch mục tiêu | giữ người/vật và có hành động liên quan, sai sót nhỏ | giữ đúng điều kiện A/B, mục tiêu và hành động/diễn biến hợp lý |
| Mạch lạc (Coherence) | rời rạc, khó hiểu | hiểu được vài câu nhưng thiếu tiến triển | phần lớn sự kiện có liên kết | diễn tiến tự nhiên, có quan hệ rõ |
| Nhất quán thực thể (Entity Consistency) | tự mâu thuẫn ai giữ vật/ai làm gì | lẫn nhân vật/đối tượng đáng kể | phần lớn nhất quán | nhất quán cả nhân vật, vật, tình trạng |
| Nhân quả (Causal Continuation) | hành động trái nguyên nhân hoặc không liên quan | quan hệ yếu hoặc vô lý | giải pháp có liên quan và đúng phần lớn | diễn tiến/giải pháp phù hợp rõ với điều kiện |

**Cổng H1:** ≥12/16 output **step1024** có điểm bám prompt ≥2.  
**Cổng H2:** ≥6/8 cặp **step1024** mà cả hai output đạt điểm ≥2 và **hành động/sự kiện ứng với fact A khác B một cách phù hợp**; có ít nhất 1 cặp H2 trong từng nhóm của bốn nhóm.  
Chỉ khi **H1 và H2** đạt, kèm đầy đủ nguồn/score QA và không có vấn đề provenance, mới được gọi `QUALITY_CANDIDATE_SCOPED_STEP1024`. Nếu không, báo `NO_DEMONSTRATED_PROMPT_ADHERENCE_SCOPED` hoặc `HOLD_INCONCLUSIVE`, không gọi FAIL toàn bộ mô hình. Các thang phụ và repetition chỉ mô tả, không chuyển thành cổng mới sau khi nhìn kết quả.

**Quy trình người chấm:** trước khi đánh giá cần mã hóa ẩn checkpoint/variant thứ tự (blinding of source label), giữ nguyên prompt cho người chấm nhìn để kiểm bám nội dung; thang chấm, phiếu điểm và SHA được khóa trước giải mù. Có thể chấm bởi 1 người giữ vai trò owner và 1 AI reviewer với vai trò tách biệt; cần ghi rõ AI không phải đánh giá con người độc lập. Nếu chỉ một reviewer, kết luận `SINGLE_RATER_EXPLORATORY_ONLY`, chưa được tuyên bố độ đồng thuận (inter-rater reliability). Nếu hai reviewer, ghi tỷ lệ đồng thuận, những bất đồng và quy tắc phân xử trước run. Không dùng tên model/condition trong packet chấm.

## 5. Ngân sách tối đa cho nghiên cứu tương lai (chưa cấp phép)

| Hạng mục | Giới hạn đề xuất |
|---|---|
| Checkpoint | T4 gốc step1024 (primary) và original step1280 (descriptive secondary) |
| Số prompt | 8 cặp × 2 biến thể = **16** |
| Số đầu ra | 16 × 2 checkpoint = **32**; không retry, không thêm nhiều seed hoặc chọn output đẹp |
| Phương thức | Python/PyTorch P02 chính gốc, BPE2048, greedy, **64 token mới tối đa/đầu ra**, context 256; không cần Ollama |
| Ngân sách token | Tối đa **2.048 generated tokens** (32×64), EOS có thể dừng sớm |
| Máy | Windows CPU, không GPU, không Colab; giới hạn wall-clock **900 giây**, RAM tối đa kế hoạch **8 GiB**, không vượt ngân sách vì lỗi timeout |
| Nguồn | Chỉ checkpoint và tokenizer đã khóa; không TRAIN, VAL, TEST, không gọi API bên ngoài |
| Khóa khoa học | Một lệnh tiền kiểm tích hợp nguồn + BPE length (≤192 token đầu vào) + phép chấm/score packet + QA; rồi **một owner approval duy nhất** nếu có thực thi sau |
| Khi lỗi | Lưu HOLD/FAIL, không tự chạy lại, không đổi dữ liệu sau xem output |

**Ngân sách là cap thiết kế**, không phải đo thực tế, ước tính thời gian hoàn thành hay giấy phép chạy. Chỉ khi nghiên cứu mới được duyệt mới tạo runner, khóa SHA, kiểm dừng đúng một lượt.

## 6. Kết quả của lượt thiết kế hôm nay

- `PROMPTS=AUTHORED_CANDIDATE_16`, `SOURCE_EXACT_PUBLIC_DEDUP=PASS_0_OF_28_COLLISIONS`, `PROMPT_END_SERIALIZATION=NO_TRAILING_SPACE`.
- `H1/H2=PROPOSED_NOT_SCIENCE_LOCKED`, `CHECKPOINT_SOURCE=PINNED_REFERENCES_NOT_REHASHED`, `FULL_HISTORICAL_DEDUP=NOT_EXECUTED`, `BPE_LENGTH_CHECK=NOT_EXECUTED`.
- `TRAIN=NOT_EXECUTED`, `INFERENCE=NOT_EXECUTED`, `TEST=NOT_READ`; `lineage.md` và `main` không sửa.
- Nhánh Ollama cũ `research/ttm-t5-ollama-full-logits-20261111` **chưa xóa** vì owner chưa chạy PowerShell, ref lưu trữ đã được giữ nguyên. Không đụng dữ liệu `_tmp/fl3`.

**Bước thực hiện tiếp theo:** `TTM_SMALL4M_PROMPT_ADHERENCE_FRESH16_PREREG_SOURCE_AND_RUBRIC_INTEGRATED_OFFLINE_REVIEW` — một bước thiết kế/QA tích hợp để kiểm nguồn BPE và trùng lịch sử, chốt reviewer và frozen source/gates; chưa inference, huấn luyện hoặc mở TEST.
