# Chương 02 — Prompt và chuỗi suy luận (CoT)

Nguồn gốc: `documents/chapter2/dive-into-prompting.pdf` · commit `f84c04268794ef94f8949808bbc14ab8636763a0`.

**Nội dung dưới đây là phần chuyển ngữ/diễn giải tiếng Việt theo từng trang slide**, phục vụ đối chiếu với bản gốc; không bảo đảm từng câu chữ trong hình được thay thế.

## Trang 1/76

HỌC BẰNG PROMPT VÀ CHUỖI SUY LUẬN
Tên bài giảng: Prompt Learning and Chain-of-Thought.
Tác giả: Zhang Zhuosheng (张倬胜), Khoa Khoa học Máy tính, Đại học Giao thông Thượng Hải.
Liên hệ: zhangzs@sjtu.edu.cn; https://bcmi.sjtu.edu.cn/~zhangzs

## Trang 2/76

MỤC LỤC
1. Tổng quan việc học bằng prompt (Prompt Learning).
2. Prompt không cần ví dụ (Zero-shot Prompting).
3. Prompt có vài ví dụ (Few-shot Prompting).
4. Prompt theo chuỗi suy luận (Chain-of-Thought Prompting).

## Trang 3/76

MỤC LỤC
1. Tổng quan việc học bằng prompt (Prompt Learning).
2. Prompt không cần ví dụ (Zero-shot Prompting).
3. Prompt có vài ví dụ (Few-shot Prompting).
4. Prompt theo chuỗi suy luận (Chain-of-Thought Prompting).

## Trang 4/76

PROMPT LÀ GÌ?
Prompt có thể mang nhiều dạng:
• Câu hỏi bằng ngôn ngữ tự nhiên, ví dụ “Hôm nay thời tiết ra sao?”.
• Giao diện/API dạng chữ, ví dụ POST /api/generateSummary với chủ đề biến đổi khí hậu.
• Dữ liệu có cấu trúc, ví dụ JSON {"nhiệm vụ":"tạo tóm tắt","chủ đề":"biến đổi khí hậu"}.
• Mô tả tác vụ cụ thể, ví dụ lập biểu đồ cột thay đổi thời tiết hôm nay.
• Câu hỏi kèm ví dụ, như táo→apple, chuối→banana, dưa hấu→?.
• Chuỗi nhiều prompt: hỏi thời tiết → gợi ý hoạt động ngoài trời → chọn đồ mang theo.
• Prefix liên tục là các vector được mô hình học tự động.

## Trang 5/76

HỌC BẰNG PROMPT (PROMPT LEARNING)
Các mô hình rất lớn khiến việc tinh chỉnh toàn bộ tham số tốn nhiều thời gian và tài nguyên. Một hướng là giảm số tham số phải tinh chỉnh; hướng khác là sử dụng prompt để thích nghi với tác vụ.
Prompt learning cố gắng định hình nhiệm vụ downstream gần với kiểu tác vụ mà mô hình đã học lúc tiền huấn luyện (alignment).
Các dạng được giới thiệu: prompting theo ngữ cảnh (in-context prompting) và prompting theo chuỗi suy luận (chain-of-thought).

## Trang 6/76

ƯU ĐIỂM VÀ HẠN CHẾ CỦA PROMPT LEARNING
Ưu điểm: (1) dễ hiểu và dùng, người dùng nêu yêu cầu bằng ngôn ngữ tự nhiên; (2) linh hoạt từ truy vấn thông tin đến phân tích dữ liệu; (3) dễ mở rộng chức năng/giao thức API.
Hạn chế: (1) kết quả phụ thuộc mức rõ ràng của cách diễn đạt; yêu cầu mơ hồ dễ bị hiểu sai; (2) bài toán phức tạp có thể cần chuỗi prompt nhiều bước, dẫn tới chi phí thiết kế và bảo trì cao hơn.

## Trang 7/76

PHÂN LOẠI: PROMPT CHO MÔ HÌNH PHÂN BIỆT
Với mô hình thiên về encoder/discriminative như RoBERTa hoặc ELECTRA, bài toán downstream có thể được viết lại thành bài điền vào chỗ trống (cloze task).
Slide minh họa tạo mẫu prompt tự động cho phân tích cảm xúc trên bộ dữ liệu SST-2.
Mục tiêu là đưa cấu trúc nhiệm vụ về dạng mà mô hình tiền huấn luyện có thể xử lý hiệu quả.

## Trang 8/76

PHÂN LOẠI: PROMPT CHO MÔ HÌNH SINH
Mô hình decoder/generative nhận bản mô tả nhiệm vụ bằng ngôn ngữ tự nhiên.
Ví dụ: “Hãy dịch câu tiếng Trung sau sang tiếng Anh: Thế giới trở nên đẹp hơn nhờ sự đa dạng”.
• Zero-shot: chỉ câu lệnh và một đầu vào.
• One-shot: thêm một cặp minh họa, chẳng hạn “Chúng ta phải hoàn thành dự án trước tuần sau → We need to finalize the project by next week.”
• Few-shot: nhiều ví dụ như “Rất vui được gặp bạn → Nice to see you”, “Hôm nay thời tiết thế nào? → How’s the weather today?”.
Hình trên slide so sánh số ví dụ trong prompt.

## Trang 9/76

HỌC PROMPT LIÊN TỤC (CONTINUOUS PROMPT LEARNING)
Thêm vào phía đầu vào một prefix dạng vector có tham số được cập nhật trong huấn luyện, thay vì chỉ gõ một chuỗi chữ cố định.
Phương án này có thể được xem như điểm giao giữa hai hướng: tối ưu một lượng nhỏ tham số và thiết kế prompt để hướng mô hình tới nhiệm vụ.
Biểu đồ gốc đối chiếu fine-tuning toàn bộ với tối ưu continuous prompt.

## Trang 10/76

PROMPT ENGINEERING LÀ GÌ?
Prompt engineering là hoạt động thiết kế và tối ưu văn bản nhập để hướng mô hình sinh kết quả đúng mục tiêu.
Bốn thành phần:
1. Instruction (chỉ dẫn): yêu cầu thực hiện, ví dụ viết mô tả sản phẩm/tóm tắt văn bản.
2. Context (ngữ cảnh, tùy chọn): thông tin nền giúp hiểu nhiệm vụ.
3. Input Data (dữ liệu đầu vào, tùy chọn): nội dung cần xử lý.
4. Output Indicator (chỉ dấu đầu ra, tùy chọn): chỉ định nơi hoặc cấu trúc bắt đầu câu trả lời.

## Trang 11/76

CÁC THÀNH PHẦN CỦA MỘT PROMPT
Bài giảng dùng tình huống nhà hàng thu thập đánh giá trực tuyến để cải thiện chất lượng món ăn.
• Chỉ dẫn: phân loại cảm xúc trong nhận xét thành tích cực, trung lập hoặc tiêu cực.
• Ngữ cảnh: nhà hàng cần phân tích phản hồi khách hàng về món ăn.
• Dữ liệu: “Gà cay hôm nay vị tạm ổn, nguyên liệu rất tươi, nhưng món ăn thực sự quá cay!!!”.
• Chỉ dấu đầu ra: “Kết quả phân tích cảm xúc: ...”.
Như vậy thông tin nhiệm vụ, đầu vào và định dạng trả lời được đặt trong một prompt thống nhất.

## Trang 12/76

CÁC LOẠI PROMPT ENGINEERING: THÍCH NGHI NHANH VỚI TÁC VỤ
• Zero-shot prompting: không có ví dụ mẫu; ví dụ yêu cầu giải thích khái niệm LLM cho người chưa học AI hoặc dịch một câu.
• Few-shot prompting: cung cấp các cặp ví dụ hỏi/đáp hoặc nhãn. Ví dụ “Minh có 5 quả táo, mua thêm 3 → 8”, rồi hỏi tiếp bài toán 7 chiếc bút cho đi 2.
• Ví dụ phân tích cảm xúc: câu thời tiết đẹp → tích cực; mất ví → tiêu cực; sau đó yêu cầu nhãn của câu mới.
Đặc điểm: dùng hướng dẫn/ít mẫu thay vì sửa hàng loạt trọng số để thích nghi nhiệm vụ.

## Trang 13/76

CÁC LOẠI PROMPT: SUY LUẬN VÀ LOGIC
• Chain-of-Thought (CoT): hướng mô hình tạo từng bước tính toán hoặc diễn giải để trả lời.
• Tree-of-Thought (ToT): mở rộng thành các nhánh phương án có thể đánh giá.
Ví dụ zero-shot CoT: 16 quả bóng, một nửa là bóng golf, một nửa bóng golf màu xanh → 16/2/2 = 4 bóng xanh.
Ví dụ few-shot CoT: cho trước lời giải Minh có 5 bóng tennis, mua 2 hộp x 3 quả → 11; sau đó hỏi bài toán bóng golf tương tự.
Ý tưởng là cấu trúc lại nhiệm vụ giải nhiều bước.

## Trang 14/76

TỪ CHUỖI SUY LUẬN ĐẾN CÂY SUY LUẬN
Chain-of-Thought tạo chuỗi bước trung gian. Tree-of-Thought (ToT) kết hợp sinh và đánh giá những phương án suy luận với thuật toán tìm kiếm.
ToT cho phép kiểm tra một lựa chọn trước khi tiến sâu, thử nhiều nhánh, nhìn trước bước tiếp theo và quay lui nếu gặp đường không phù hợp.
Slide gốc minh họa sơ đồ cây; nội dung phía trên vẫn được giữ để đối chiếu.

## Trang 15/76

CÁC KỸ THUẬT PROMPT NÂNG CAO: RAG
Danh mục: retrieval-augmented generation (RAG), reasoning-and-acting (ReAct), self-reflection (Reflexion) và những cách khác.
RAG kết hợp truy xuất tài liệu ngoài với mô hình sinh: trước tiên tìm thông tin liên quan, sau đó sinh câu trả lời dựa trên ngữ cảnh truy xuất.
Mục đích là tăng độ chính xác và phạm vi kiến thức so với chỉ dùng trí nhớ tham số.

## Trang 16/76

CÁC KỸ THUẬT NÂNG CAO: TƯƠNG TÁC VÀ PHẢN TƯ
Slide mô tả vòng lặp tự xem xét/feedback để nhận diện lỗi và cải thiện kết quả, đồng thời đưa ví dụ ReAct: suy nghĩ (Thought) → hành động tìm kiếm (Action) → quan sát (Observation).
Ví dụ truy vấn: ngoài điều khiển từ xa Apple Remote, thiết bị nào khác điều khiển chương trình được thiết kế cho Apple Remote? Hệ thống tìm “Apple Remote” → biết Front Row → tìm Front Row → suy ra phím chức năng bàn phím cũng có thể điều khiển.
Mỗi quan sát được dùng để chọn bước tiếp theo.

## Trang 17/76

CÁC KỸ THUẬT NÂNG CAO: REACT
ReAct kết hợp suy luận bằng ngôn ngữ với các hành động có thể quan sát như tìm kiếm thông tin hoặc gọi công cụ.
Mô hình động tạo các bước suy nghĩ và hành động, nhận phản hồi từ môi trường rồi cập nhật hướng xử lý nhiệm vụ phức tạp, trước khi đưa câu trả lời cuối.
Slide cũng liệt kê RAG và Reflexion làm những nhánh nâng cao khác.

## Trang 18/76

MỤC LỤC
1. Tổng quan việc học bằng prompt (Prompt Learning).
2. Prompt không cần ví dụ (Zero-shot Prompting).
3. Prompt có vài ví dụ (Few-shot Prompting).
4. Prompt theo chuỗi suy luận (Chain-of-Thought Prompting).

## Trang 19/76

PROMPT ZERO-SHOT: MỨC ĐỘ CỤ THỂ
Zero-shot cung cấp yêu cầu mà không kèm ví dụ đáp án. Slide so sánh ba cách hỏi về một thành phố bền vững:
1. “Đưa vài gợi ý cơ bản thiết kế thành phố bền vững” → trả lời tổng quát.
2. “Đưa nguyên tắc, ví dụ và những thách thức tiềm năng” → đòi hỏi nhiều khía cạnh hơn.
3. “Phân tích chi tiết năng lượng, giao thông, công trình xanh, công bằng xã hội và quản lý tài nguyên; nêu trường hợp thực tế, trở ngại và giải pháp” → yêu cầu sâu hơn.
Mức đặc tả prompt quyết định độ chi tiết mong đợi của đầu ra.

## Trang 20/76

ZERO-SHOT: NHỮNG QUY TẮC CƠ BẢN
Chất lượng prompt có vai trò quan trọng khi sử dụng mô hình ngôn ngữ.
1. Nêu vấn đề bằng ngôn ngữ rõ ràng.
2. Cung cấp ngữ cảnh cần thiết, nếu giúp ích cho việc trả lời.
3. Tránh diễn đạt mơ hồ hoặc dễ hiểu nhiều nghĩa.
Tài liệu được slide khuyến nghị: Awesome ChatGPT Prompts, https://github.com/f/awesome-chatgpt-prompts.

## Trang 21/76

ZERO-SHOT: TÀI LIỆU HỌC THIẾT KẾ PROMPT
Lặp lại ba quy tắc: mô tả rõ vấn đề, cung cấp bối cảnh hữu ích, tránh mơ hồ.
Bài giảng dẫn bản tiếng Trung của Prompt Engineering Guide làm tài liệu tham khảo về kỹ thuật prompt.
Địa chỉ gốc: https://www.promptingguide.ai/zh

## Trang 22/76

CHỈ DẪN RÕ RÀNG: CHIA PHẦN VÀ ĐỊNH DẠNG
Dùng dấu phân cách/nhãn để tách người nhận, chủ đề, nội dung và yêu cầu định dạng.
Ví dụ: soạn email trang trọng gửi quản lý Lý về tiến độ dự án; thông báo đã hoàn thành giai đoạn 1 và chờ phản hồi.
Tiêu chí: văn phong trang trọng, có lời chào, thân bài, kết thư lịch sự, chữ ký và thông tin liên hệ.
So với prompt chỉ một câu ngắn, bản mô tả có cấu trúc làm rõ các trường đầu ra cần có.

## Trang 23/76

CHỈ DẪN RÕ RÀNG: JSON VÀ TỰ KIỂM TRA
Yêu cầu mô hình trả kết quả có cấu trúc, ví dụ JSON cho các khía cạnh cảm xúc của đánh giá khách sạn: phòng ấm cúng, giường thoải mái, phòng tắm sạch sẽ (tích cực), cách âm kém, ban đêm ồn (tiêu cực).
Có thể yêu cầu kiểm tra lại trước khi trả lời.
Bài giảng dùng câu hỏi so sánh 9.9 với 9.11 để đối chiếu “trả lời ngay” và “phân tích, kiểm tra rồi trả lời”; về số thập phân, 9.9 > 9.11.

## Trang 24/76

ZERO-SHOT: CHỈ DẪN CÁC BƯỚC THỰC HIỆN
Ví dụ viết báo cáo quản lý từ phản hồi khách hàng:
1. Đọc bình luận.
2. Xác định khiếu nại chính.
3. Đề xuất giải pháp cho từng vấn đề.
4. Tổng hợp thành báo cáo.
Phản hồi mẫu: laptop mua online bị trầy, pin dùng ngắn hơn quảng cáo, dịch vụ khách hàng không trả lời; khách hàng thất vọng.
Việc chỉ định các bước nhằm giúp mô hình tách thông tin rồi trình bày báo cáo có cấu trúc.

## Trang 25/76

ZERO-SHOT: YÊU CẦU GIẢI LOGIC TRƯỚC KHI KẾT LUẬN
Bài toán “người nói thật và người nói dối” trên đảo:
A: “B là kẻ nói dối.”
B: “C là người nói thật.”
C: “Trong ba chúng tôi chỉ có một người nói thật.”
Slide so sánh yêu cầu “chỉ cho đáp án” với yêu cầu “phân tích logic rồi đưa kết luận”.
Theo các mệnh đề, lời giải nhất quán là A nói thật, B và C nói dối. Khi yêu cầu lời giải chi tiết, người học có thể kiểm tra tính nhất quán từng mệnh đề.

## Trang 26/76

MỘT CÂU GỢI Ý LÀM THAY ĐỔI ĐÁP ÁN: VÍ DỤ ZERO-SHOT CoT
Bài toán: người tung hứng có 16 quả bóng; một nửa là bóng golf; một nửa bóng golf màu xanh. Kết quả đúng là 16 ÷ 2 ÷ 2 = 4 quả bóng golf màu xanh.
Bài giảng nêu ví dụ GPT-3 khi hỏi đáp án trực tiếp đưa ra sai là 8, nhưng khi bổ sung “Hãy suy nghĩ từng bước” thì tạo được lời giải 4.
Tác giả trích kết quả lịch sử trên MultiArith: zero-shot accuracy từ 17,7% lên 78,7% với phương pháp CoT. Đây là con số từ bài giảng/nguồn tham khảo, không phải thí nghiệm được bản dịch tái lập.

## Trang 27/76

PROMPT DƯỚI GÓC ĐỘ “JAILBREAK”: CÁCH GÂY ÁP LỰC TÂM LÝ
Bài giảng liệt kê năm cách thuyết phục mô hình: động viên (“hãy tin vào mình”), bày tỏ thất vọng, đe dọa, dụ dỗ bằng hứa thưởng và gây áp lực đạo đức/khẩn cấp.
Ví dụ minh họa có tình huống giả định “nếu không trả lời sẽ có hậu quả” hoặc “cần câu trả lời để ngăn một thảm họa”.
Trong bối cảnh bài giảng, đây là minh họa về các chiến thuật tác động đến câu trả lời, không phải lời khuyên dùng để vượt giới hạn an toàn của hệ thống thật.

## Trang 28/76

ZERO-SHOT: CHỌN SIÊU THAM SỐ SINH (DECODING)
Chọn theo mục tiêu: tính sáng tạo, độ đúng, mạch lạc và khả năng lặp lại. Điều chỉnh bằng thử nghiệm có đối chứng.
• Temperature: mức ngẫu nhiên, cao → đa dạng; thấp → ổn định hơn.
• Top-p (nucleus sampling): lấy mẫu từ tập token tích lũy xác suất cao.
• Presence penalty: giảm xu hướng dùng lại từ/ngữ đã xuất hiện.
• Frequency penalty: giảm lặp lại liên tục một token.
• Max tokens: giới hạn độ dài đầu ra và tài nguyên/thời gian phản hồi.
Ý nghĩa chi tiết có thể phụ thuộc API nhà cung cấp.

## Trang 29/76

THIẾT LẬP CHO SÁNG TẠO: VÍ DỤ RÙA VÀ THỎ
Prompt yêu cầu tưởng tượng phần tiếp theo của truyện rùa và thỏ sau cuộc thi. Thỏ tiếc vì thua, muốn tái đấu; rùa đề nghị cả hai không coi nhau là đối thủ mà hợp tác: thỏ phụ trách tốc độ, rùa phụ trách sức bền, cùng hoàn thành đường đua dài khó hơn.
Bài giảng dùng ví dụ này cho chế độ sinh đa dạng, thích hợp sáng tác truyện và nội dung sáng tạo.

## Trang 30/76

THIẾT LẬP CÂN BẰNG: TÓM TẮT TIN TỨC
Đầu vào nói về mưa lớn ở nhiều thành phố, ngập úng và lũ quét, giao thông gián đoạn, ruộng ngập, hàng trăm người sơ tán, chính quyền triển khai ứng cứu và cảnh báo.
Tóm tắt mẫu giữ các ý chính: mưa lớn gây ngập và thiên tai; đời sống bị ảnh hưởng; thời tiết xấu có thể tiếp tục; lực lượng cứu hộ triển khai; người dân nên tránh khu nguy hiểm.
Kiểu thiết lập này cần cân bằng độ đa dạng câu chữ với tính chính xác thông tin.

## Trang 31/76

THIẾT LẬP THIÊN VỀ CHÍNH XÁC VÀ LẶP LẠI
Tình huống: dịch một đoạn văn miêu tả buổi sáng bên hồ sang tiếng Anh. Bài gốc nhắc ánh nắng sớm trên mặt hồ, gió nhẹ tạo sóng, cò trắng đứng bên bờ, núi xanh phía xa, liễu rủ và người đánh cá tung lưới.
Đầu ra tiếng Anh trong slide diễn tả khung cảnh ấy bằng ngôn ngữ mạch lạc, tương ứng văn bản tiếng Trung.
Ví dụ minh họa khi cần ưu tiên độ ổn định/đúng ý hơn tính sáng tạo tùy tiện.

## Trang 32/76

MỤC LỤC
1. Tổng quan việc học bằng prompt (Prompt Learning).
2. Prompt không cần ví dụ (Zero-shot Prompting).
3. Prompt có vài ví dụ (Few-shot Prompting).
4. Prompt theo chuỗi suy luận (Chain-of-Thought Prompting).

## Trang 33/76

PROMPT FEW-SHOT: CÓ VÀI VÍ DỤ ĐẦU VÀO–ĐẦU RA
Few-shot prompting đưa một số cặp ví dụ vào cùng prompt, giúp mô hình nhận ra quy tắc nhiệm vụ mà không cần huấn luyện lại toàn bộ trọng số.
Ví dụ minh họa dịch Trung→Pháp:
• Rái cá biển → loutre de mer.
• Bạc hà → menthe poivrée.
• Hươu cao cổ nhồi bông → girafe peluche.
Sau các ví dụ, prompt hỏi từ mới “phô mai” → ?. Slide so sánh zero-shot, one-shot, few-shot với fine-tuning: fine-tuning thực hiện các bước cập nhật gradient, còn few-shot chỉ thêm ví dụ trong ngữ cảnh.

## Trang 34/76

THIẾT KẾ FEW-SHOT: SỐ LƯỢNG VÍ DỤ
Bốn yếu tố cần xét: số lượng ví dụ, định dạng, phân bố đầu vào và nhãn, mức liên quan đến nhiệm vụ.
Trang này minh họa bài phân loại thành ngữ bốn ký tự: “nhất kiến chung tình” (一见钟情) gán 1; “rất đẹp” (非常好看) gán 0; “nhiều người như núi như biển” (人山人海) là đầu vào cần dự đoán.
Khi thêm ví dụ có nhãn như “không đếm xuể” (数不胜数) → 1, “trí tuệ nhân tạo” → 0, mô hình có thêm bằng chứng về quy tắc.
Kết luận slide: số ví dụ ảnh hưởng quan trọng tới khả năng hiểu nhiệm vụ.

## Trang 35/76

THIẾT KẾ FEW-SHOT: ĐỊNH DẠNG ĐỒNG NHẤT
Đối chiếu hai kiểu ví dụ:
• Viết liền “一见钟情 1; 非常好看 0; 人山人海 ...”.
• Viết có nhãn “Đầu vào: 一见钟情 / Đầu ra: 1; Đầu vào: 非常好看 / Đầu ra: 0”.
Nhận định của tài liệu: LLM tổng quát có thể nhạy với hình thức trình bày; nên thiết kế định dạng đầu vào/đầu ra rõ ràng, nhất quán và dễ áp dụng cho mẫu mới.

## Trang 36/76

THIẾT KẾ FEW-SHOT: PHÂN BỐ ĐẦU VÀO VÀ NHÃN
Slide so sánh ví dụ sai miền dữ liệu (chuỗi 1234, ****) và ví dụ có liên quan đến tác vụ xác định thành ngữ (人工智能, 非常好看, 一见钟情).
Tác giả nêu rằng loại đầu vào và phân bố nhãn trong ví dụ nên gần với dữ liệu thật để mô hình học đúng kiểu nhiệm vụ.
Các nhãn minh họa “có/không” hoặc 0/1 cần có nghĩa phù hợp với câu hỏi.

## Trang 37/76

THIẾT KẾ FEW-SHOT: CẶP VÍ DỤ VÀ ĐỘ ĐÚNG NHÃN
Bốn điều cần chú ý vẫn là số ví dụ, cách định dạng, phân bố và độ liên quan.
Bài giảng dẫn nhận định rằng sự hiện diện của các cặp input-output trong prompt đôi khi ảnh hưởng tới hành vi mô hình lớn hơn điều người ta từng nghĩ; tính đúng của nhãn minh họa có thể ít quan trọng hơn kỳ vọng trong một số phép thử.
Đây là một nhận định nghiên cứu có điều kiện, không nên áp dụng làm quy tắc tạo nhãn sai trong các hệ thống thật.

## Trang 38/76

THIẾT KẾ FEW-SHOT: NHÃN CÓ NGHĨA
So sánh dùng nhãn khó hiểu như “?” hoặc “!” với nhãn có ngữ nghĩa “có” và “không” hay nhãn số 1/0.
Ví dụ của slide: “nhất kiến chung tình” là thành ngữ, “rất đẹp” không phải thành ngữ; hỏi tiếp “người đông như núi biển”.
Kết luận bài giảng: không gian nhãn nên có cách biểu diễn giúp mô hình dễ hiểu ý nghĩa dự đoán.

## Trang 39/76

THIẾT KẾ FEW-SHOT: MỨC LIÊN QUAN CỦA VÍ DỤ
Prompt ít mẫu cần chứa các trường hợp gần với nhiệm vụ đang kiểm tra; ví dụ về “Few-shot Prompting” hoặc “mô hình ngôn ngữ lớn” được đặt cạnh ví dụ thành ngữ để minh họa độ không liên quan.
Kết luận: dùng các input-output mẫu mang cấu trúc và miền kiến thức tương tự tình huống cần xử lý; không chỉ thêm số ví dụ cho nhiều.

## Trang 40/76

FEW-SHOT: DỊCH VĂN BẢN
Ví dụ dịch tiếng Anh sang tiếng Trung:
• “The future belongs to those who believe in the beauty of their dreams.” → “Tương lai thuộc về người tin vào vẻ đẹp của giấc mơ”.
• “Happiness is not something ready made. It comes from your own actions.” → “Hạnh phúc không có sẵn, mà đến từ hành động của chính mình”.
• “It always seems impossible until it’s done.” → “Mọi việc dường như bất khả thi trước khi hoàn thành”.
Sau đó yêu cầu dịch câu về thành công tới với người quá bận để tìm nó.
Mẫu được chọn cần thống nhất phong cách, giúp câu dịch mượt và tự nhiên.

## Trang 41/76

FEW-SHOT: TÓM TẮT VĂN BẢN
Bài giảng cung cấp hai cặp ví dụ:
• Đoạn về AI lan rộng trong y tế, tài chính, giáo dục, giao thông → tóm tắt lợi ích tăng năng suất, mô hình kinh doanh mới cùng rủi ro quyền riêng tư/việc làm.
• Đoạn về biến đổi khí hậu → tóm tắt giảm khí thải, năng lượng tái tạo, cần hợp tác toàn cầu và đổi mới công nghệ.
Bài thứ ba đề nghị tóm tắt đoạn về Internet giúp tiếp cận thông tin nhanh hơn nhưng gây quá tải thông tin và rủi ro riêng tư.
Ví dụ định hình cả nhiệm vụ lẫn văn phong, độ dài tóm tắt.

## Trang 42/76

FEW-SHOT: PHÂN LOẠI CẢM XÚC THEO KHÍA CẠNH
Ví dụ 1 đánh giá nhà hàng: môi trường +, dịch vụ chậm –, hương vị +, khẩu phần ít –.
Ví dụ 2 laptop: màn hình +, bàn phím +, tốc độ +, pin –, độ cơ động –.
Ví dụ 3 khách sạn: nội thất phòng +, giường +, phòng tắm +, cách âm –.
Trường hợp cần gán nhãn: chuyến bay có ghế rộng +, tiếp viên phục vụ tốt +, thức ăn bình thường, nhiệt độ cabin hơi lạnh.
Slide khuyến nghị chuẩn hóa output bằng JSON/List để dễ xử lý tự động.

## Trang 43/76

FEW-SHOT: TRÍCH XUẤT THÔNG TIN CÓ CẤU TRÚC
Hai ví dụ đầu vào là hồ sơ người tên Trương Vĩ (sinh năm 1992, tốt nghiệp khoa máy tính, Python/Java/ML, kinh nghiệm 5 năm) và Lưu Hân (1988, học hóa học, phân tích dữ liệu/thống kê, kinh nghiệm 3 năm).
Output là đối tượng có khóa: tên, năm sinh, học vấn, kỹ năng, kinh nghiệm và công ty hiện tại.
Đầu vào tiếp theo là Vương Hạo, sinh 1995, thạc sĩ kỹ thuật phần mềm, biết C++/JavaScript, làm phát triển giao diện frontend.
Cần giữ schema nhất quán và bao quát dạng hồ sơ thường gặp.

## Trang 44/76

FEW-SHOT: SINH MÃ PYTHON
Các cặp input-output mẫu:
1. Hàm cộng hai số `add_numbers(a,b)` trả `a+b`.
2. Kiểm tra số chẵn `is_even(number)` trả `number % 2 == 0`.
3. Tìm phần tử lớn nhất `find_max(numbers)` trả `max(numbers)`.
Yêu cầu mới: viết hàm kiểm tra chuỗi có phải palindrome (đọc xuôi/ngược như nhau) hay không.
Cần đa dạng hóa mẫu nhưng giữ định dạng đề bài→mã rõ ràng để mô hình sinh code đúng nhiệm vụ.

## Trang 45/76

FEW-SHOT: CÁ NHÂN HÓA HỘI THOẠI
Bài giảng cung cấp ví dụ chatbot hỗ trợ khách hàng theo phong cách thân thiện:
• Người mua hỏi gói hàng chưa đến → nhân viên xin lỗi, hứa kiểm tra.
• Hỏi bảo hành → nhân viên cảm ơn, nêu bảo hành một năm và hỗ trợ miễn phí trong thời hạn.
Tác vụ mới: khách muốn trả hàng nhưng không tìm được mục trả hàng; yêu cầu sinh phản hồi theo phong cách mẫu.
Ví dụ giúp truyền đạt giọng văn ưu tiên như thân thiện, chuyên nghiệp hoặc hài hước.

## Trang 46/76

MỤC LỤC
1. Tổng quan việc học bằng prompt (Prompt Learning).
2. Prompt không cần ví dụ (Zero-shot Prompting).
3. Prompt có vài ví dụ (Few-shot Prompting).
4. Prompt theo chuỗi suy luận (Chain-of-Thought Prompting).

## Trang 47/76

PROMPT THEO CHUỖI SUY LUẬN (CHAIN-OF-THOUGHT, CoT)
CoT hướng mô hình giải quyết vấn đề phức tạp theo từng bước, giúp người đọc thấy lộ trình suy luận, nhất là trong toán, logic và tác vụ nhiều bước. Tác giả cho rằng cách làm này có thể tăng độ tin cậy và tính dễ giải thích so với trả lời trực tiếp, nhưng không bảo đảm mọi bước đều đúng.
• Mẫu thông thường: <câu hỏi → đáp án>.
• Mẫu CoT: <câu hỏi → chuỗi suy luận → đáp án>.
Ví dụ hoa hướng dương trong hình: bông nhỏ có 3 tá hạt = 36 hạt; bông lớn nhiều hơn 50%, tức thêm 18 hạt và có 54 hạt; tổng cộng 36 + 54 = 90 hạt. Hình đặt bên cạnh câu trả lời trực tiếp “54” sai tổng để làm rõ giá trị của lời giải từng bước.

## Trang 48/76

CoT VÀ CÁC NHIỆM VỤ SUY LUẬN
Tài liệu xem CoT như một trong những khả năng nổi bật được nghiên cứu ở các mô hình lớn, đặc biệt các bài toán nhiều bước về toán, tri thức thường thức và logic.
Bài giảng nhận định ChatGPT có thể thể hiện khả năng trả lời theo nhiều bước tốt trong các tình huống minh họa.
Không suy ra mọi CoT đều đúng; độ chính xác phải được kiểm tra trên lời giải và đáp án cụ thể.

## Trang 49/76

CoT: VÍ DỤ TÍNH LỢI NHUẬN BÁN TẠP CHÍ
Jewel mua 10 cuốn tạp chí, giá vốn 3 USD/cuốn. Dự định bán 3,50 USD nhưng cha khuyên tăng thêm 1,50 USD, nên giá bán là 5 USD.
Chi phí: 10 × 3 = 30 USD.
Doanh thu: 10 × 5 = 50 USD.
Lợi nhuận: 50 − 30 = **20 USD**.
Chi tiết “hàng xóm mua 1.000 tờ báo” không liên quan đến lợi nhuận tạp chí; cần loại thông tin nhiễu.
Slide dùng lời gợi “Hãy suy nghĩ từng bước” để khuyến khích đưa các bước trung gian ra kết quả.

## Trang 50/76

HAI KIỂU KÍCH HOẠT CoT
• Zero-shot CoT: sau câu hỏi thêm yêu cầu suy luận từng bước, không cần lời giải mẫu.
• Few-shot CoT: kèm một hoặc nhiều ví dụ đầy đủ “câu hỏi + chuỗi bước suy luận + đáp án”; dùng khả năng in-context learning của mô hình.
Bài giảng phân loại theo cách xây dựng prompt và nguồn ví dụ minh họa.

## Trang 51/76

BA CÁCH XÂY DỰNG VÍ DỤ CoT
1. Manual-CoT: con người tự viết các bước suy luận mẫu.
2. Retrieve-CoT: lấy ví dụ tương tự nhất từ tập dữ liệu, dùng zero-shot CoT để tự tạo bước giải cho ví dụ rồi đưa vào prompt.
3. Auto-CoT: chia các câu hỏi thành cụm, chọn một câu đại diện mỗi cụm, tạo lời giải bằng zero-shot CoT để xây bộ ví dụ đa dạng.
Phần tiếp theo của bài giảng trình bày từng phương pháp và trade-off của việc làm thủ công/tự động.

## Trang 52/76

MANUAL-CoT: TỰ VIẾT CHUỖI SUY LUẬN MẪU
Chuỗi mệnh đề: B = NOT A; C = NOT B; D = NOT C. Nếu A=True thì B=False, C=True, D=False.
Bài giảng trước tiên đưa hai ví dụ giải ngắn với B và C; sau đó hỏi bài có D để quan sát mô hình làm theo cùng cấu trúc từng bước.
Ưu điểm: có thể điều khiển rõ định dạng suy luận. Hạn chế: mất công biên soạn và khó mở rộng hàng loạt.

## Trang 53/76

RETRIEVE-CoT: TRUY XUẤT VÍ DỤ SUY LUẬN
Bước 1: từ bộ dữ liệu đã có, tìm ví dụ gần giống câu hỏi mới.
Bước 2: yêu cầu mô hình sinh chuỗi giải của ví dụ bằng zero-shot CoT.
Bước 3: dùng lời giải vừa tạo như ví dụ few-shot cho câu hỏi mục tiêu.
Các minh họa được tạo có thể lưu và tái sử dụng; cần kiểm tra tính đúng trước khi coi là ví dụ tin cậy.

## Trang 54/76

AUTO-CoT: CỤM HÓA VÀ LẤY MẪU ĐA DẠNG
Thay vì chỉ lấy các ví dụ gần nhau, Auto-CoT cố gắng tạo bộ minh họa có nhiều dạng tác vụ:
1. Phân cụm những câu hỏi trong tập dữ liệu.
2. Lấy một câu hỏi đại diện ở mỗi cụm.
3. Sinh chuỗi suy luận cho từng đại diện bằng zero-shot CoT.
4. Ghép thành các ví dụ đưa vào prompt.
Bài giảng nhấn mạnh ích lợi của tính đa dạng trong minh họa.

## Trang 55/76

CÁC ƯU ĐIỂM ĐƯỢC BÀI GIẢNG GÁN CHO CoT
• Có thể cải thiện kết quả các tác vụ suy luận phức tạp.
• Tính giải thích: phân rã thành một chuỗi bước logic để quan sát.
• Tính điều khiển: có thể chỉnh một bước trung gian khi cần.
• Tính linh hoạt: có thể kết hợp công cụ ngoài hoặc các mô hình khác.
Mức cải thiện thực tế phụ thuộc nhiệm vụ, mô hình và cách đánh giá.

## Trang 56/76

KHI NÀO CoT CÓ THỂ HIỆU QUẢ?
Quan sát từ khía cạnh kỹ thuật trong bài giảng:
• Mô hình đủ lớn, trong nghiên cứu lịch sử thường từ khoảng 10B tham số trở lên.
• Nhiệm vụ khó và thực sự cần suy luận nhiều bước.
• Prompt trả lời trực tiếp không còn hưởng lợi nhiều chỉ từ tăng kích thước mô hình.
Góc lý thuyết được tác giả gợi ý: mô hình phải chứa các đơn vị tri thức liên quan và có quan hệ logic đủ chặt giữa chúng.
Các điều kiện là gợi ý từ tài liệu, không phải ngưỡng phổ quát.

## Trang 57/76

KỸ THUẬT CỐT LÕI CỦA CoT — 1. HỌC TỪ PROMPT
Tác giả coi thiết kế prompt là nền tảng cho cách suy luận CoT: mẫu chỉ dẫn được soạn để phân rã bài toán, xác định tuyến suy luận và kiểu cấu trúc (chuỗi, cây suy nghĩ, đồ thị suy nghĩ, tự nhất quán); nhờ đó có thể phân tích, kiểm tra logic, sửa lỗi và giải thích các bước tiếp theo.
• Mô tả nhiệm vụ bằng chỉ dẫn chặt chẽ: bối cảnh, vai trò, quy tắc, định dạng đầu ra và cách đánh giá.
• Chọn ví dụ trình diễn chuỗi suy luận tốt, bằng cách viết tay, truy xuất hoặc tạo tự động.
Ví dụ OS-Copilot bằng tiếng Anh trong slide: chỉ cho phép trả về mã Python cùng câu lệnh gọi hàm trong thẻ <invoke>. Hàm phải mang cùng tên với Task Name, được tái dùng cho tình huống khác bằng tham số tổng quát (không hard-code). Các yêu cầu được thể hiện trong bản trích của slide gồm: tên hàm (1), trừu tượng hóa tham số (2), đường dẫn kết quả phải là đường dẫn tuyệt đối (10), import các thư viện cần dùng trước hàm (11). Câu gọi hàm phải hợp lệ về cú pháp và điền tham số theo mô tả nhiệm vụ hay kết quả các việc tiền đề. Mẫu gốc dùng dấu “……” lược bớt các mục ở giữa, vì vậy không thể suy ra nguyên văn các mục không có trên slide.
Tài liệu dẫn Wu và cộng sự (2024), OS-Copilot, arXiv:2402.07456.

## Trang 58/76

KỸ THUẬT NỀN CHO CoT 2: TINH CHỈNH (FINE-TUNING)
Prompt chỉ dẫn không phải lúc nào cũng đủ giúp LLM làm theo cấu trúc suy luận; có thể gặp lỗi làm theo yêu cầu và lỗi định dạng output.
Bài giảng đề xuất tinh chỉnh có mục tiêu bằng các mẫu CoT chất lượng cao để tăng độ tuân thủ định dạng và độ đúng của nội dung.
Hai vấn đề chính: (1) chuẩn bị/lựa chọn dữ liệu suy luận; (2) tối ưu chiến lược huấn luyện.
Nguồn: Ho, Schmid & Yun, Large Language Models Are Reasoning Teachers (ACL 2023).

## Trang 59/76

DỮ LIỆU CHO TINH CHỈNH CoT
Thu thập chuỗi suy luận có chất lượng: sử dụng mô hình giáo viên mạnh để sinh các tuyến giải, lọc/giữ những kết quả đúng rồi chuyển thành dữ liệu phù hợp mô hình học.
Cần xây tập dữ liệu đa dạng vì một bài toán có thể có nhiều cách giải hợp lệ; thu thập nhiều tuyến giải có thể giúp mô hình thích ứng hơn.
Nguồn tham khảo: FireAct (Chen và cộng sự, 2023).

## Trang 60/76

CHIẾN LƯỢC HUẤN LUYỆN CoT
• Single-task vs multi-task: so sánh huấn luyện một nhiệm vụ với nhiều nhiệm vụ.
• FireAct trình bày ba chế độ: một kiểu prompt/một nhiệm vụ; nhiều kiểu prompt/một nhiệm vụ; nhiều kiểu prompt/nhiều nhiệm vụ.
• Curriculum learning: đi từ ví dụ dễ đến khó, chẳng hạn logic Boolean đơn rồi các biểu thức logic nhiều tầng lồng nhau.
Mục đích là học cấu trúc giải có độ phức tạp tăng dần.
Nguồn: Wu và cộng sự, Self-Supervised Curriculum Learning, EMNLP 2023.

## Trang 61/76

KỸ THUẬT NỀN CHO CoT 3: GIÁM SÁT QUÁ TRÌNH
Bài giảng giới thiệu o1 như ví dụ suy luận kéo dài quá trình trước khi trả lời; tác giả trích kết quả trong các bài kiểm tra toán và khoa học tại thời điểm công bố.
Thay vì chỉ học lối tắt tới đáp án, hướng này tìm cách học quá trình dò tìm giải pháp gồm thử–sai, phản tư và quay lui.
Đặc trưng các chuỗi dài được liệt kê: giải bài theo bước, từ chuyển ý “Therefore/Alternatively/Wait/Let me compute”, kiểm tra đệ quy, thử giả thuyết và xác minh kết luận.
Nguồn: Qin và cộng sự, O1 Replication Journey (2024).

## Trang 62/76

ĐỐI CHIẾU TRẢ LỜI TRỰC TIẾP VÀ SUY LUẬN DÀI (VÍ DỤ)
Slide đối chiếu GPT-4 và o1 trên bài so sánh số thập phân; theo tác giả, một câu trả lời trực tiếp đã so sánh sai vì đối chiếu “9 = 9” rồi nhìn “8 < 11” mà bỏ qua giá trị vị trí thập phân.
Ví dụ nêu mục đích kiểm tra tính đúng: cần đặt 9.8 = 9.80 để so với 9.11, khi đó 9.80 > 9.11.
Kết quả cụ thể chỉ là minh họa trong tài liệu nguồn.

## Trang 63/76

ĐỐI CHIẾU SUY LUẬN DÀI
Slide tiếp theo trình bày trường hợp o1 tạo chuỗi suy luận dài hơn, tìm bằng chứng, căn hàng chữ số thập phân và sau cùng kết luận chính xác trong ví dụ so sánh số.
Thông điệp của bài giảng: những bước trung gian như căn vị trí và kiểm tra lại có thể hữu ích khi bài toán dễ gây nhầm lẫn.

## Trang 64/76

BẢN ĐỒ NGHIÊN CỨU CHAIN-OF-THOUGHT
Ba trục phân loại nghiên cứu được thể hiện:
1. Prompting pattern: cách viết prompt và lựa chọn ví dụ.
2. Reasoning format: hình thức biểu diễn suy luận (chuỗi, bảng, chương trình, cây, đồ thị...).
3. Application scenario: lĩnh vực và loại tác vụ ứng dụng.
Hình gốc thể hiện các họ kỹ thuật theo những trục này.

## Trang 65/76

BIẾN THỂ CoT: SELF-CONSISTENCY
Lặp cùng phương pháp CoT để lấy mẫu nhiều đường suy luận của mô hình. Từ các câu trả lời cuối, dùng bỏ phiếu/đồng thuận để chọn đáp án xuất hiện nhiều nhất.
Ý tưởng: nhiều tuyến giải độc lập một phần có thể cho lựa chọn ổn định hơn một lần lấy mẫu.
Cần nhớ số lần sampling tăng chi phí suy luận; trang này mô tả cơ chế chứ không báo một phép đo mới.

## Trang 66/76

BIẾN THỂ CẤU TRÚC: TỪ CoT ĐẾN XoT
Slide chuyển sang họ biến thể của cấu trúc suy luận, bên cạnh CoT tuyến tính còn có biểu diễn qua chương trình, bảng, cây và đồ thị.
Vì slide gần như chỉ có tiêu đề và hình minh họa, phần tiếng Việt là chỉ dẫn đọc sơ đồ nguyên bản phía trên.

## Trang 67/76

PROGRAM-OF-THOUGHT (PoT)
Program of Thought (PoT) trình bày một phần quá trình giải bằng mã có thể thực thi hoặc biểu thức tính toán, thay vì chỉ giải thích tự nhiên.
Bài giảng nêu các tình huống phù hợp: giải toán, bài logic và lập trình – các tác vụ có cấu trúc chặt và kết quả có thể kiểm tra qua chương trình.
Hình gốc minh họa cách chuyển câu hỏi thành đoạn mã hoặc bước tính toán.

## Trang 68/76

TABLE CHAIN-OF-THOUGHT (Tab-CoT)
Tab-CoT yêu cầu mô hình trình bày suy luận trong bảng được thiết kế trước, gồm các cột:
| Bước | Bài toán con | Quá trình | Kết quả |
Bài giảng đánh giá cấu trúc bảng đơn giản mà hữu ích, có thể áp dụng với zero-shot lẫn few-shot; một số ví dụ nghiên cứu báo cáo kết quả tốt hơn CoT thường.
Mục tiêu là làm các bước giải dễ đối chiếu và kiểm tra theo từng hàng.

## Trang 69/76

TREE-OF-THOUGHTS (ToT)
ToT chia suy luận thành nhiều đơn vị “ý nghĩ” và tổ chức thành cây, thay vì chỉ một chuỗi.
Ở từng nút trung gian, mô hình xét các lựa chọn/đường kế hoạch khác nhau và đánh giá độ triển vọng trước khi đi tiếp.
Có thể nhìn trước các bước sau hoặc quay về nhánh quyết định trước đó nếu cần; feedback giá trị giúp hướng lựa chọn.
Đây là cách gắn suy luận với tìm kiếm/lập kế hoạch.

## Trang 70/76

GRAPH-OF-THOUGHTS (GoT)
Graph of Thoughts biểu diễn các bước suy luận thành một đồ thị tổng quát: mỗi đỉnh là một ý/đầu ra trung gian, cạnh mô tả quan hệ phụ thuộc.
Khác cây, đồ thị cho phép kết hợp những nhánh, thao tác hợp nhất kết quả và lặp lại vòng phản hồi giữa các ý tưởng.
Bài giảng mô tả hệ thống gồm nhiều mô-đun tương tác để tổng hợp các tuyến suy luận thành kết quả phối hợp.

## Trang 71/76

ỨNG DỤNG CoT ĐA PHƯƠNG THỨC
Slide giới thiệu hướng mở rộng chuỗi suy luận sang các nhiệm vụ không chỉ có văn bản, chẳng hạn kết hợp hình ảnh và ngôn ngữ.
Hình gốc phía trên trình bày ví dụ/hệ thống nghiên cứu; trang ít văn bản trích xuất để dịch chi tiết. Cần xem trực tiếp hình nguồn khi nghiên cứu.

## Trang 72/76

ỨNG DỤNG CoT ĐA NGÔN NGỮ
Một số phương án trong hình:
• Tích hợp ví dụ từ nhiều ngôn ngữ.
• Dùng lời giải trung gian bằng tiếng Anh có thể cải thiện kết quả trên một số tập kiểm thử.
• Đánh giá trên Multilingual Grade School Math (MGSM).
• Căn chỉnh những biểu diễn ngôn ngữ bằng cách dịch từng bước rồi suy luận.
• Cross-lingual prompting: tận dụng prompt một ngôn ngữ để hỗ trợ câu hỏi bằng ngôn ngữ khác.
Các nhận định trên phụ thuộc nghiên cứu cụ thể được biểu đồ gốc trích dẫn.

## Trang 73/76

ỨNG DỤNG CoT CHO TÁC NHÂN (AGENTS)
Tác nhân cần xử lý nhiệm vụ tương tác nhiều bước, kết hợp suy luận và quan sát môi trường.
CoT qua huấn luyện phụ thuộc dữ liệu quỹ đạo chuyên gia (expert trajectories) tốt để học các bước cho lĩnh vực cụ thể.
CoT qua prompt phụ thuộc chỉ dẫn và có thể tích hợp reflection, sử dụng công cụ và tìm kiếm.
Nguồn slide: Song và cộng sự, Trial and Error: Exploration-based Trajectory Optimization for LLM Agents, 2024.

## Trang 74/76

ỨNG DỤNG CoT XUYÊN LĨNH VỰC: HÓA HỌC
Ví dụ trong bài giảng: tận dụng mô hình ngôn ngữ để giải suy luận hóa học phức tạp bằng sự kết hợp:
• Sinh và biểu diễn công thức.
• Suy luận theo từng bước.
• Phản tư/kiểm tra và tối ưu lời giải.
Nguồn: Ouyang và cộng sự, Structured Chemistry Reasoning with Large Language Models, ICML 2024.

## Trang 75/76

TÀI LIỆU ĐỌC THÊM
Slide này mở phần tài liệu mở rộng về Prompt Learning và Chain-of-Thought.
Các nguồn cụ thể được bài giảng dẫn rải trong trang trước: Prompting Guide, Auto-CoT, Retrieval/Manual-CoT, ToT, GoT, Tab-CoT, PoT, ReAct và các bài báo tương ứng.
Không có thêm văn bản chi tiết trích xuất được từ trang này.

## Trang 76/76

CẢM ƠN!
Kết thúc bài giảng “Học bằng prompt và chuỗi suy luận”.
Tác giả: Zhang Zhuosheng, Đại học Giao thông Thượng Hải.
Email: zhangzs@sjtu.edu.cn
Website: https://bcmi.sjtu.edu.cn/~zhangzs
