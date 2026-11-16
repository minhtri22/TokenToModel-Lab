# Chương 04 — Suy luận toán học

Nguồn gốc: `documents/chapter4/math.pdf` · commit `f84c04268794ef94f8949808bbc14ab8636763a0`.

**Nội dung dưới đây là phần chuyển ngữ/diễn giải tiếng Việt theo từng trang slide**, phục vụ đối chiếu với bản gốc; không bảo đảm từng câu chữ trong hình được thay thế.

## Trang 1/17

SUY LUẬN TOÁN HỌC VỚI MÔ HÌNH NGÔN NGỮ LỚN (LLM)
Tác giả: Chen Xingyu (陈星宇).

## Trang 2/17

MỤC LỤC
1. Giới thiệu suy luận toán học.
2. Mô hình ngôn ngữ lớn chuyên toán.
3. Chưng cất tri thức (distillation).
4. Mô hình suy luận dài (long-reasoning models).
5. Đánh giá năng lực toán học.

## Trang 3/17

GIỚI THIỆU SUY LUẬN TOÁN HỌC
Suy luận toán học là năng lực LLM giải các bài toán bằng phân tích logic, thao tác ký hiệu và suy diễn nhiều bước. Mô hình cần hiểu khái niệm toán học như đại số, hình học và tạo ra đáp án đúng.
Các năng lực trọng tâm:
• Suy luận nhiều bước: chia bài toán phức tạp thành các bài toán con.
• Hiểu ký hiệu: xử lý ký hiệu và công thức trừu tượng.
• Tính toán: thực hiện phép toán chính xác.
Ứng dụng: giải toán thi đấu, hỗ trợ giáo dục, suy diễn công thức trong nghiên cứu khoa học.

## Trang 4/17

LÀM THẾ NÀO ĐỂ LLM SUY LUẬN TOÁN HỌC?
• Chuỗi suy luận (Chain-of-Thought, CoT): sinh tường minh các bước lập luận.
• Tìm kiếm trên cây: dùng Monte Carlo Tree Search (MCTS) phối hợp mô hình phần thưởng theo quá trình (Process Reward Model, PRM) để thử nhiều hướng giải.
• Tự nhất quán (Self-Consistency): lấy mẫu nhiều đường suy luận, bỏ phiếu chọn đáp án xuất hiện nhiều nhằm giảm sai sót.
• Hỗ trợ bằng công cụ: gọi máy tính để tránh lỗi tính số; hoặc tạo và chạy chương trình Python để tính toán.
Các tài liệu tham khảo [1]–[3] được giữ ở trang gốc.

## Trang 5/17

MÔ HÌNH SUY LUẬN DÀI
Là loại mô hình tạo chuỗi suy luận dài trong giai đoạn trả lời. Các ví dụ được bài giảng giới thiệu: OpenAI-o1 và DeepSeek-R1.
Các đặc trưng của chuỗi suy luận:
• Tự phản tư, xem lại giả định.
• Chuyển hướng giải khi cần.
• Kiểm tra đáp án và sửa lỗi.
Khi tăng độ dài nội dung sinh trong quá trình suy luận, mô hình có thể khảo sát nhiều hướng giải hơn, qua đó cải thiện hiệu quả trên một số bài toán. Chuỗi suy luận cũng có thể chứa các chiến lược tương tự cách con người giải toán. Đây là cách diễn giải của tác giả; không phải bảo đảm cho mọi nhiệm vụ.

## Trang 6/17

MINH HỌA ĐẶC TRƯNG CỦA CHUỖI SUY LUẬN DÀI
• Tự phản tư: xem lại lời giải hoặc lý do đưa ra đáp án.
• Chuyển hướng giải: thử cách tiếp cận khác.
• Kiểm tra và sửa lỗi: đánh giá bước trung gian hoặc kết quả cuối.
Ví dụ minh họa trong bài giảng: OpenAI-o1. Hình gốc chỉ ra các đoạn tương ứng với chuyển hướng, tự sửa lỗi và tự phản tư.

## Trang 7/17

MÔ HÌNH LỚN CHUYÊN TOÁN
Định nghĩa: mô hình lớn được tối ưu riêng cho nhiệm vụ suy luận toán. Ví dụ: DeepSeek-Math và Qwen2.5-Math.
Bộ dữ liệu huấn luyện được giới thiệu: DeepMath-103K.
Các bộ đánh giá:
• GSM8K: khoảng 8,5 nghìn mẫu toán lời văn ở cấp tiểu học.
• MATH: 12.500 bài toán có mức khó như toán thi trung học.
• AIME: American Invitational Mathematics Examination, tổ chức hằng năm với 30 câu, độ khó thi toán.
Các trích dẫn học thuật [1]–[5] nằm trên slide gốc.

## Trang 8/17

MÔ HÌNH DEEPSEEK-MATH
• Làm sạch khoảng 120 tỷ token văn bản web về toán bằng lọc lặp dữ liệu Common Crawl, đồng thời giảm ô nhiễm benchmark.
• Khởi tạo từ mô hình mã nguồn DeepSeek-Coder-v1.5 thay vì LLM tổng quát, nhằm tăng khả năng thao tác ký hiệu.
• Dùng Group Relative Policy Optimization (GRPO) trong học tăng cường để giảm nhu cầu bộ nhớ và cải thiện khái quát hóa; sau đó trở thành một thành phần quan trọng của DeepSeek-R1.
• Theo bài giảng, mô hình 7B đạt hiệu năng dẫn đầu tại thời điểm được giới thiệu.

## Trang 9/17

MÔ HÌNH QWEN2.5-MATH
• Ngữ liệu tiền huấn luyện: Qwen Math Corpus v2 với khoảng 1 nghìn tỷ token, bao gồm dữ liệu tổng hợp và bài toán tiếng Trung.
• Sinh dữ liệu: dùng Qwen2-72B-Instruct tạo các cặp câu hỏi–trả lời chất lượng cao nhằm tăng độ đa dạng.
• Kết hợp CoT và Tool-Integrated Reasoning (TIR): lập luận nhiều bước và sử dụng công cụ như trình thông dịch Python; hỗ trợ phân tích song ngữ.
• Cải tiến mô hình phần thưởng: Qwen2.5-Math-RM hỗ trợ phát triển dữ liệu SFT; GRPO được dùng trong giai đoạn học tăng cường.
Theo kết quả được bài giảng dẫn, bản 7B vượt một số mô hình nguồn mở 30B–70B trên benchmark MATH và tiếp cận GPT-4 trong phép đo đó.

## Trang 10/17

BỘ DỮ LIỆU DEEPMATH-103K
• Được thiết kế cho các bài toán có độ khó cao.
• Thu thập từ những tập huấn luyện toán phổ biến rồi thực hiện nhiều bước làm sạch và loại trùng, nhằm không chồng lấn với các bộ đánh giá toán thường dùng.
• Có chú thích độ khó và các phản hồi/lời giải do DeepSeek-R1 tạo.
Theo nội dung bài giảng, việc dùng DeepMath-103K để huấn luyện có thể nâng cao năng lực toán. Đây là mô tả về kết quả được tác giả trình bày, chưa được tái lập trong bản dịch.

## Trang 11/17

CHƯNG CẤT TRI THỨC ĐỂ HỌC SUY LUẬN DÀI
Câu hỏi: làm thế nào để mô hình nhỏ học nhanh hơn các cách giải toán của mô hình suy luận dài?
• Tinh chỉnh có giám sát (SFT): cho mô hình học cách trình bày lời giải và các bước chuẩn; cần dữ liệu CoT được gán nhãn chất lượng cao.
• Chưng cất tri thức (Knowledge Distillation): mô hình lớn (teacher) sinh dữ liệu CoT, mô hình nhỏ (student) học từ các ví dụ đó qua SFT.
Ví dụ tài liệu nêu: mô hình Qwen-7B chưng cất từ DeepSeek-R1 có kết quả tốt hơn một baseline 32B trong phép đánh giá được dẫn.

## Trang 12/17

QUY TRÌNH CHƯNG CẤT BA BƯỚC
1. Sinh dữ liệu: mô hình giáo viên tạo các lời giải CoT chất lượng cao.
2. Lấy mẫu có từ chối (rejection sampling): bỏ đáp án sai, giữ chuỗi giải rõ ràng, đúng chuẩn định dạng.
3. Tinh chỉnh SFT: mô hình nhỏ học trực tiếp đầu ra giáo viên mà không bắt buộc thêm một giai đoạn học tăng cường.
Ưu điểm: tận dụng dữ liệu hiệu quả, rào cản triển khai thấp hơn, học được một số hành vi giải toán phức tạp.
Giới hạn: hiệu năng mô hình nhỏ phụ thuộc chất lượng giáo viên; bài toán quá khó vẫn có thể cần mô hình lớn.

## Trang 13/17

ĐÁNH GIÁ NĂNG LỰC TOÁN HỌC
Benchmark truyền thống:
• GSM8K (toán cấp tiểu học); MATH (toán trung học); AIME (toán thi đấu).
Chỉ số: độ chính xác và Pass@k (tỷ lệ thành công khi được lấy mẫu k lượt).
Đặc điểm: nhiều nghiên cứu hiện nay tập trung vào bài toán có đáp án dạng số/ký hiệu rõ ràng.
Hướng phát triển: đánh giá tính đúng đắn của các bài chứng minh.
Khó khăn:
• Trích xuất đáp án cuối từ câu trả lời ngôn ngữ tự nhiên.
• Xác định tính tương đương giữa các biểu thức toán.

## Trang 14/17

TRÍCH XUẤT ĐÁP ÁN ĐỂ ĐÁNH GIÁ TOÁN HỌC
• Với GSM8K, đáp án thường được đánh dấu bằng bốn dấu thăng liên tiếp: ####.
• Với MATH, đáp án thường được đặt trong lệnh LaTeX \boxed{}; tài liệu xem đây là cách làm phổ biến.
Ưu điểm: thống nhất quy tắc tách đáp án, thuận tiện cho việc đánh giá tự động.
Hạn chế: mô hình cần được huấn luyện hoặc hướng dẫn sử dụng định dạng đầu ra này; định dạng cố định không bao phủ được mọi trường hợp.
Hai hình minh họa trên slide nguồn đối chiếu phương án GSM8K và MATH.

## Trang 15/17

ĐÁNH GIÁ TÍNH ĐÚNG ĐẮN CỦA ĐÁP ÁN
Đánh giá theo quy tắc (rule-based): vì đáp án toán thường theo LaTeX, có thể trích biểu thức và kiểm tra tính tương đương bằng các quy tắc. Ví dụ: công cụ Hugging Face Math-Verify.
Đánh giá bằng LLM (LLM-as-a-Judge): quy tắc có thể bỏ sót cách diễn đạt bằng văn bản hoặc trích đáp án sai; mô hình chuyên dụng sẽ so sánh đáp án sinh với đáp án chuẩn để quyết định tương đương.
Ví dụ: Omni-Judge cho bộ đánh giá Omni. Link đến Math-Verify và Omni-Judge nằm trên slide gốc.

## Trang 16/17

TỔNG KẾT
• Suy luận toán học: dùng logic, biến đổi ký hiệu, suy diễn nhiều bước để giải toán và tạo đáp án đúng.
• Mô hình suy luận dài: sinh chuỗi CoT dài khi trả lời.
• Mô hình chuyên toán: được tối ưu bằng dữ liệu và quy trình huấn luyện cho nhiệm vụ toán.
• Chưng cất: mô hình lớn sinh dữ liệu; mô hình nhỏ học trực tiếp từ các mẫu được sinh.
• Đánh giá: GSM8K, MATH500, AIME; sinh đáp án, chuẩn hóa và trích xuất theo định dạng chung, kiểm tra tính nhất quán bằng quy tắc hoặc LLM.

## Trang 17/17

CẢM ƠN!
Slide kết thúc bài giảng về suy luận toán học. Trang gốc ghi thông tin Đại học Giao thông Thượng Hải (Shanghai Jiao Tong University).
