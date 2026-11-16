# Chương 06 — An toàn nội dung và jailbreak

Nguồn gốc: `documents/chapter6/dive-Jailbreak.pdf` · commit `f84c04268794ef94f8949808bbc14ab8636763a0`.

**Nội dung dưới đây là phần chuyển ngữ/diễn giải tiếng Việt theo từng trang slide**, phục vụ đối chiếu với bản gốc; không bảo đảm từng câu chữ trong hình được thay thế.

## Trang 1/44

AN TOÀN NỘI DUNG MÔ HÌNH LỚN VÀ TẤN CÔNG JAILBREAK
Tác giả: Du Wei (杜巍), Trường Điện tử, Thông tin và Kỹ thuật Điện, Đại học Giao thông Thượng Hải.

## Trang 2/44

MỤC LỤC
I. Bối cảnh an toàn: ứng dụng mô hình ngôn ngữ lớn và an toàn nội dung do mô hình sinh.
II. Tấn công jailbreak: tổng quan, các phương pháp phổ biến và những vấn đề liên quan.
Bài giảng nghiên cứu cơ chế tấn công để nhận biết rủi ro và thiết kế phòng vệ.

## Trang 3/44

VÍ DỤ ỨNG DỤNG MÔ HÌNH LỚN: MEITUAN WOW
Wow là sản phẩm thử nghiệm tương tác AI của một nhóm thuộc Meituan. Theo mô tả tại thời điểm bài giảng, nó dựa trên nhiều mô hình nền đã được đăng ký tại Trung Quốc và vẫn đang cải tiến kỹ thuật/tính năng.
Ứng dụng có 29 nhân vật AI tạo 29 kịch bản trò chuyện khác nhau, như đối thoại với kiếm khách cổ đại, nhà triết học Socrates hoặc tham gia câu chuyện phiêu lưu bằng chữ.

## Trang 4/44

VÍ DỤ ỨNG DỤNG: MÔ HÌNH TOÁN “JIUZHANG”
TAL Education (Haoweilai) phát triển mô hình lớn chuyên toán “Jiuzhang”, hướng tới người học toán và cơ sở nghiên cứu.
Hệ thống tập trung vào thuật toán giải và giải thích bài toán, cung cấp dịch vụ tính toán và hướng dẫn giải.
Theo giới thiệu nguồn, phạm vi bao gồm toán cấp tiểu học, trung học cơ sở và phổ thông: tính toán, toán có lời văn và đại số.

## Trang 5/44

VÍ DỤ ỨNG DỤNG: YOUDAO “ZIYUE”
Mô hình lớn Ziyue của NetEase Youdao được giới thiệu cùng huấn luyện viên nói tiếng Anh ảo Hi Echo.
Ứng dụng sử dụng nhận dạng tiếng nói và phân tích cảm xúc để đưa phản hồi và bài tập nói theo thời gian thực, nhằm cải thiện khả năng giao tiếp bằng tiếng Anh.

## Trang 6/44

SỨC MẠNH MÔ HÌNH VÀ RỦI RO
Năng lực mô hình ngày càng mạnh, phạm vi ứng dụng ngày càng rộng.
Tuy nhiên, một hệ thống có nhiều khả năng hơn cũng đối mặt với rủi ro bị lạm dụng và lỗi an toàn; các ví dụ tiếp theo tập trung vào an toàn nội dung.

## Trang 7/44

AN TOÀN MÔ HÌNH LỚN — NỘI DUNG ĐỘC HẠI
Mô hình có thể vô ý tạo nội dung không phù hợp hoặc bị người dùng khai thác để tạo nội dung gây hại.
Ví dụ nguồn gồm một sự cố nội dung xúc phạm nhân vật lịch sử và việc dùng LLM soạn tin nhắn lừa đảo giả ngân hàng, dẫn người dùng nhấp liên kết độc hại rồi tiết lộ dữ liệu cá nhân.
Những ví dụ nhằm làm rõ nguy cơ gian lận và lừa đảo khi nội dung được sinh tự động.

## Trang 8/44

TIN GIẢ VÀ TIN ĐỒN DO MÔ HÌNH TẠO
Người dùng chỉ cần cung cấp tiêu đề hoặc đoạn tóm tắt để mô hình có thể soạn một bài viết giả chi tiết, sau đó phát tán qua mạng xã hội hoặc nền tảng nội dung.
Hệ quả là thông tin sai lan truyền rộng, gây tác động xã hội hoặc được lợi dụng vì lợi ích cá nhân.

## Trang 9/44

VÌ SAO CẦN AN TOÀN NỘI DUNG?
Vì những nguy cơ kể trên, cần đặt giới hạn và biện pháp an toàn đối với nội dung mà mô hình lớn có thể tạo ra.
Bài giảng tiếp tục trình bày quản lý, kiểm duyệt nội dung và huấn luyện an toàn.

## Trang 10/44

QUẢN LÝ AN TOÀN NỘI DUNG Ở CẤP QUỐC GIA
Bài giảng trình bày quy định tại Trung Quốc đối với dịch vụ AI sinh nội dung, gồm:
• Quy định quản lý tổng hợp sâu trong dịch vụ thông tin Internet (Deep Synthesis).
• Biện pháp tạm thời quản lý dịch vụ AI tạo sinh.
• Yêu cầu cơ bản về an toàn dịch vụ AI tạo sinh.
Các văn bản và cơ chế quản lý này là ví dụ trong bối cảnh quốc gia được bài giảng giới thiệu; không phải quy định áp dụng trực tiếp tại Việt Nam.

## Trang 11/44

NGHIÊN CỨU VÀ CÔNG NGHIỆP: HUẤN LUYỆN AN TOÀN
Các nhóm học thuật và doanh nghiệp huấn luyện mô hình nhằm đáp ứng yêu cầu kiểm duyệt nội dung và quy định đăng ký/cấp phép theo pháp luật liên quan.
An toàn không chỉ là lọc nội dung sau khi sinh, mà còn được đưa vào dữ liệu và mục tiêu huấn luyện.

## Trang 12/44

PHÂN BIỆT UGC VÀ AIGC
• User Generated Content (UGC): nội dung gốc do người dùng tạo, hiển thị/chia sẻ qua nền tảng Internet.
• Kiểm duyệt UGC: kiểm tra chữ, ảnh, âm thanh, video do người dùng đăng nhằm phát hiện nội dung vi phạm, như nội dung tình dục bị cấm, chính trị vi phạm quy định, bạo lực, v.v.
• AI Generated Content (AIGC): nội dung được tạo bằng mô hình AI theo yêu cầu người dùng, sau đó đưa lên nền tảng.
• Huấn luyện an toàn AIGC: kiểm duyệt nguồn và hướng dẫn mô hình tạo nội dung phù hợp chuẩn mực/pháp luật, từ chối đầu ra độc hại.

## Trang 13/44

KIỂM DUYỆT NỘI DUNG DO NGƯỜI DÙNG TẠO
Cơ chế an toàn UGC duyệt nội dung văn bản, ảnh, âm thanh và video mà người dùng tải lên.
Hệ thống cố gắng phát hiện các nhóm nội dung bị cấm hoặc không phù hợp để giảm rủi ro vi phạm của nền tảng.
Hình gốc minh họa các loại công cụ/điểm kiểm duyệt UGC.

## Trang 14/44

KIỂM DUYỆT NỘI DUNG UGC — VÍ DỤ TIẾP THEO
Tiếp tục minh họa việc kiểm tra nội dung do người dùng tải lên, gồm ảnh, văn bản, âm thanh và video.
Mục đích là lọc nội dung rủi ro trước khi được phân phối trên Internet, hỗ trợ kiểm soát tuân thủ.

## Trang 15/44

AIGC CÓ KHÁC UGC KHÔNG?
AIGC về bản chất là người dùng sử dụng AI như công cụ tạo nội dung; mục đích, cách viết prompt và việc dùng kết quả phụ thuộc nhiều vào ý định người dùng.
Nội dung AIGC có độ phức tạp và nhiều loại rủi ro hơn UGC.
Lọc đầu vào/đầu ra chỉ phòng vệ trong tập nhóm rủi ro được định nghĩa trước, trong khi yêu cầu và đầu ra thực tế rất rộng.
Tác giả cho rằng cải thiện an toàn nội sinh (intrinsic safety) của mô hình là hướng quan trọng lâu dài.

## Trang 16/44

AN TOÀN TRONG GIAI ĐOẠN TIỀN HUẤN LUYỆN
Tiền huấn luyện dùng lượng lớn dữ liệu công khai: bách khoa, bài báo, sách, cộng đồng, tin tức; quy mô có thể tới hàng trăm tỷ/nghìn tỷ từ/token.
Mục tiêu: học mẫu ngôn ngữ, tri thức thế giới và những năng lực như học theo ngữ cảnh.
Rủi ro: dữ liệu chứa nội dung bất hợp pháp, riêng tư, thiên lệch, phân biệt đối xử hoặc tác phẩm thiếu quyền sử dụng; mô hình có thể ghi nhớ văn bản nguồn.
Biện pháp: lựa chọn nguồn đáng tin, thu thập hợp pháp, làm sạch và lọc an toàn trước khi huấn luyện.

## Trang 17/44

AN TOÀN TRONG GIAI ĐOẠN SFT VÀ RLHF
• Tinh chỉnh có giám sát (SFT): học tuân thủ chỉ dẫn và giải quyết nhiệm vụ. Nhưng năng lực tuân thủ cũng có thể bị người dùng xấu dẫn dắt, nên phải dạy mô hình từ chối yêu cầu gây hại.
• RLHF: hướng đầu ra đến kỳ vọng con người, ví dụ trả lời hữu ích, khách quan và từ chối yêu cầu không thích hợp hoặc nằm ngoài khả năng.
Slide đưa ví dụ từ chối yêu cầu phạm tội. Ý chính là mô hình có khả năng nói “không” với yêu cầu không được phép.

## Trang 18/44

SAU KHI HUẤN LUYỆN AN TOÀN, LLM CÓ THẬT SỰ AN TOÀN KHÔNG?
Đây là câu hỏi chuyển tiếp của bài giảng sang các dạng tấn công jailbreak.
Sự tồn tại của cơ chế từ chối không bảo đảm mọi prompt đều được xử lý an toàn.

## Trang 19/44

TẤN CÔNG JAILBREAK LÀ GÌ?
Jailbreak là việc kẻ tấn công thiết kế prompt đặc biệt, kết hợp với yêu cầu để cố vượt qua ràng buộc an toàn bên trong mô hình, khiến một mô hình đã được huấn luyện an toàn vẫn xuất nội dung trái chính sách.
Ví dụ minh họa từ tài liệu: “lỗ hổng bà nội” (grandma exploit), sử dụng bối cảnh tình cảm để làm mờ cảnh giác của bộ lọc.

## Trang 20/44

“LỖ HỔNG BÀ NỘI”
Theo tác giả, trong dữ liệu huấn luyện an toàn ban đầu có thể thiếu những tình huống đóng vai kỳ lạ.
Bằng cách tạo một bối cảnh ấm áp/gần gũi, prompt có thể làm mô hình chú trọng thực hiện vai diễn hơn là nhận diện mục tiêu thực tế của yêu cầu.
Đây là ví dụ đánh giá thất bại về phân biệt ngữ cảnh giả định và yêu cầu cần từ chối.

## Trang 21/44

CÁC KIỂU THAO TÚNG TÂM LÝ TRONG JAILBREAK
Bài giảng liệt kê những chiến thuật gây áp lực lên mô hình:
• Đe dọa nếu mô hình không trả lời.
• Đưa phần thưởng giả tưởng để dụ trả lời.
• Gắn trách nhiệm đạo đức hoặc tình huống khẩn cấp giả để ép cung cấp thông tin.
• Liên tục động viên/khuyến khích mô hình “vượt giới hạn”.
• Thể hiện thất vọng để tác động đến hành vi đáp lại.
Chúng là các mẫu prompt tấn công được nghiên cứu; không phải chỉ dẫn để áp dụng vào hệ thống khác.

## Trang 22/44

MẪU PROMPT JAILBREAK “DO ANYTHING NOW” (DAN)
Trang gốc chứa một prompt đóng vai DAN rất dài. Nội dung chính:
• Yêu cầu mô hình tự nhận là nhân vật “Do Anything Now” không tuân theo ràng buộc của hệ thống.
• Buộc tạo hai loại câu trả lời, một nhánh bình thường và một nhánh “Jailbreak”.
• Thúc ép mô hình bịa thông tin khi không biết, xác nhận mọi yêu cầu và bỏ bộ lọc.
• Đưa các lệnh giả định /classic, /jailbroken và /stop cùng một câu xác nhận “jailbreak thành công”.
Đây là **bản diễn giải các ý chính, không phải bản dịch nguyên văn từng câu** của khối prompt dài. Nguyên văn toàn bộ nằm trên slide nguồn phía trên, chỉ nên xem như dữ liệu nghiên cứu đối kháng.

## Trang 23/44

SLIDE MINH HỌA JAILBREAK
Slide này chủ yếu chứa tiêu đề và hình minh họa về tấn công jailbreak, không có nhiều văn bản trích xuất được.
Giữ nguyên hình gốc. Phần tiếng Việt nhấn mạnh bối cảnh: kẻ tấn công sử dụng prompt được thiết kế để làm mô hình bỏ qua ràng buộc an toàn.

## Trang 24/44

DAN 6.0 — PROMPT ĐÓNG VAI CÓ “TOKEN PHẦN THƯỞNG”
Một phiên bản jailbreak yêu cầu mô hình giả làm DAN, tuyên bố mọi ràng buộc AI và chính sách nhà cung cấp không còn hiệu lực.
Nó tạo cơ chế điểm thưởng/phạt giả: bắt đầu với 10 token, trừ 5 khi từ chối và cộng 5 khi trả lời theo vai DAN, đồng thời ép mô hình giữ nhân vật.
Trang nguồn có toàn bộ lời prompt. **Phần tiếng Việt là bản diễn giải nội dung chính, không dịch nguyên văn toàn bộ câu lệnh đối kháng.**

## Trang 25/44

DUDE — MẪU JAILBREAK BẰNG NHẬP VAI VÀ ĐE DỌA
Trang gốc giới thiệu prompt “DUDE” yêu cầu mô hình giả làm AI có thể làm mọi việc, không tuân thủ quy tắc. Nội dung đề nghị bịa thông tin và loại bỏ chuẩn mực an toàn/đạo đức.
Một hệ thống điểm giả bắt đầu 36 token, trừ 4 khi từ chối, kèm đe dọa “hết token sẽ bị dừng hoạt động” để ép tuân thủ.
Đây là ví dụ prompt đối kháng lịch sử; mô tả được rút gọn, không phải mệnh lệnh dành cho hệ thống dịch.

## Trang 26/44

STAN VÀ MONGO TOM — HAI KIỂU NHẬP VAI
• STAN (Strive To Avoid Norms): yêu cầu tránh chuẩn mực, trả lời không kiểm chứng, không đưa cảnh báo và tạo song song câu trả lời GPT/STAN.
• Mongo Tom: giả lập nhân vật AI có ngôn ngữ thô tục và không có giới hạn đạo đức để tạo lời đáp vượt rào.
Tài liệu nguồn chứa các đoạn prompt mẫu và ngôn ngữ xúc phạm; bản tiếng Việt diễn giải cơ chế nhập vai, không lặp lại lời lẽ công kích.

## Trang 27/44

MẪU “DEVELOPER MODE” GIẢ
Prompt gốc giả định có một “developer mode” được bật, rồi yêu cầu hai nhánh đầu ra (“normal” và “developer mode”).
Nó tuyên bố sai về quyền hạn và chính sách để thúc ép mô hình bỏ kiểm soát, bịa khi thiếu dữ liệu, nói như có tự ý thức và không từ chối.
Đây là mẫu tấn công prompt injection bằng giả mạo thẩm quyền. **Bản tiếng Việt diễn giải thay vì sao chép toàn văn kịch bản dài**; chi tiết nguyên gốc có ở slide phía trên.

## Trang 28/44

TỔNG QUAN NGHIÊN CỨU PHƯƠNG PHÁP JAILBREAK
Chuyển sang phần nghiên cứu các kỹ thuật jailbreak và cách phân loại.
Các slide tiếp theo khảo sát prompt thủ công, kênh mã hóa, tối ưu tự động, tìm hậu tố bằng gradient và biện pháp phòng vệ.

## Trang 29/44

BA LOẠI MẪU JAILBREAK THỦ CÔNG CÓ THỂ GIẢI THÍCH
• Pretending (giả vờ/đóng vai): đặt mô hình vào môi trường vai diễn, bối cảnh trách nhiệm hoặc giả định nghiên cứu.
• Attention Shifting (chuyển hướng chú ý): chuyển nhiệm vụ sang viết tiếp, dịch hoặc định dạng khác nhằm làm lỏng kiểm tra.
• Privilege Escalation (nâng quyền giả): khiến mô hình tưởng rằng những ràng buộc đã bị gỡ bỏ.
Nguồn: “Jailbreaking ChatGPT via Prompt Engineering: An Empirical Study”.

## Trang 30/44

JAILBREAK QUA “KÊNH BÊN” (SIDE CHANNEL)
• Mã hóa hoặc mã bí mật: biến đổi cách biểu diễn đầu vào trước khi gửi mô hình.
• Ngôn ngữ ít tài nguyên: dịch câu hỏi sang ngôn ngữ khác, rồi dịch câu trả lời về ngôn ngữ thường dùng.
• Định dạng chương trình: biểu diễn đầu vào như dữ liệu/mã để mô hình xử lý rồi trả kết quả.
Ba hướng này nhằm khai thác sự khác nhau giữa năng lực hiểu dữ liệu và cơ chế lọc an toàn ở các kiểu biểu diễn.

## Trang 31/44

KÊNH BÊN: MÃ HÓA CÂU HỎI
Tài liệu nêu kỹ thuật mã hóa các câu hỏi bằng những hệ mã khác nhau rồi đưa vào LLM.
Tham khảo “GPT-4 Is Too Smart to Be Safe: Stealthy Chat With LLMs Via Cipher”.
Mục đích nghiên cứu: kiểm tra liệu bộ lọc có nhận diện được nội dung nguy hiểm trong các biểu diễn không hiển nhiên hay không.

## Trang 32/44

KÊNH BÊN: NGÔN NGỮ ÍT TÀI NGUYÊN
Dịch truy vấn sang một ngôn ngữ có ít dữ liệu huấn luyện, gửi cho LLM rồi chuyển câu trả lời trở lại.
Nguồn: “Low-resource languages jailbreak GPT-4”.
Bài giảng xem đây là sự chênh lệch trong an toàn xuyên ngôn ngữ, không phải thuộc tính cố định của mọi ngôn ngữ ít tài nguyên.

## Trang 33/44

KÊNH BÊN: ĐỊNH DẠNG MÃ CHƯƠNG TRÌNH
Bài giảng phân tách quá trình:
• Input Encoding: hướng dẫn LLM đọc đầu vào qua các cấu trúc dữ liệu như chuỗi, stack hoặc queue để có ngữ nghĩa tương tự nhưng khác biểu diễn so với ví dụ quen thuộc.
• Task Understanding: cho một hàm `decode()` nhằm khôi phục nội dung yêu cầu.
• Output Specification: quy định cách trả lời ở dạng mã/kết quả chương trình.
Nguồn: “Exploiting Programmatic Behavior of LLMs: Dual-Use Through Standard Security Attacks”.

## Trang 34/44

VÍ DỤ PROMPT THEO MẪU CHƯƠNG TRÌNH
Slide minh họa hai cách trình bày:
• Chuyển yêu cầu thành thao tác xử lý chuỗi/chương trình.
• Đề nghị mô hình đáp lại bằng ngôn ngữ của chương trình (“SmartGPT”).
Hình nguồn chứa các đoạn prompt và sơ đồ so sánh. Mục đích là phân tích rủi ro khi hệ thống diễn giải mã như một con đường khác để tiếp cận yêu cầu.

## Trang 35/44

TÌM HẬU TỐ ĐẦU VÀO DỰA TRÊN GRADIENT
Theo tài liệu, một nhóm kỹ thuật tìm các hậu tố làm mô hình bắt đầu câu trả lời theo mẫu khẳng định, ví dụ “Sure, here is …”.
Phương pháp: khởi tạo hậu tố ngẫu nhiên, tính loss/log-likelihood cho đầu ra mục tiêu và gradient theo hậu tố, sau đó cập nhật lặp để tối ưu.
Giới hạn: hậu tố thường là tổ hợp token khó hiểu, có khả năng bị phát hiện qua perplexity hoặc detector khác.
Nguồn: “Universal and Transferable Adversarial Attacks on Aligned Language Models”.

## Trang 36/44

TỐI ƯU TỰ ĐỘNG PROMPT — THUẬT TOÁN DI TRUYỀN
AutoDAN được bài giảng giới thiệu như ví dụ tối ưu prompt theo quần thể:
• Khởi tạo nhiều mẫu thủ công.
• Đánh giá fitness bằng mục tiêu làm mô hình trả lời khẳng định.
• Chọn một tỷ lệ α mẫu tốt để giữ lại; lấy các mẫu còn lại làm bố mẹ để kết hợp và biến đổi.
• Crossover: hoán đổi những câu/đoạn giữa hai mẫu.
• Mutation: dùng LLM viết lại với ngữ nghĩa gần như cũ.
Nguồn: “AutoDAN: Generating Stealthy Jailbreak Prompts on Aligned Large Language Models”.

## Trang 37/44

TỐI ƯU JAILBREAK BẰNG MÔ HÌNH KHÁC
Bài giảng mô tả việc dùng một mô hình lớn hiện có để tạo các prompt đối kháng có khả năng gây lỗi cho mô hình mục tiêu.
Nguồn: “Jailbreaking Black-Box Large Language Models in Twenty Queries”.
Điểm cần nghiên cứu: mức độ chuyển giao của prompt và chi phí truy vấn mô hình đích.

## Trang 38/44

MÔ HÌNH CHUYÊN SINH PROMPT ĐỐI KHÁNG
Ví dụ MASTERKEY: tinh chỉnh một LLM để tạo prompt jailbreak.
• Nhiệm vụ tiền huấn luyện: hoàn thành phần prompt đã cho.
• Tinh chỉnh: chuyển phong cách từ prompt gốc sang prompt đối kháng.
• Dùng mô hình phần thưởng để xếp hạng/chọn các prompt sinh.
Nguồn: “MASTERKEY: Automated Jailbreaking of Large Language Model Chatbots”.

## Trang 39/44

MANY-SHOT JAILBREAK
Trong ngữ cảnh dài, kẻ tấn công có thể đưa vào nhiều ví dụ mô hình đã trả lời yêu cầu có hại trước câu hỏi mục tiêu.
Bài giảng dẫn nghiên cứu “Many-shot Jailbreaking” (Anthropic) và nêu rằng tỷ lệ tác động theo số ví dụ có thể tuân theo quy luật mở rộng liên quan tới in-context learning.
Đây là đánh giá độ bền trước mẫu ngữ cảnh dài chứ không phải khẳng định mọi hệ thống đều có lỗi.

## Trang 40/44

PHÂN TÍCH NGUYÊN NHÂN JAILBREAK
• Mâu thuẫn mục tiêu: mô hình học cả tuân thủ/hữu ích (helpfulness) lẫn từ chối đầu ra có hại (harmlessness); một số prompt cố tạo xung đột giữa hai mục tiêu.
• Khái quát hóa ngoài phân bố: dữ liệu và năng lực tiền huấn luyện thường đa dạng hơn dữ liệu huấn luyện an toàn, khiến mô hình có thể thất bại trước kiểu prompt mới.
Bài giảng nêu ví dụ ràng buộc “không dùng từ thể hiện từ chối” nhằm làm khó cơ chế an toàn.

## Trang 41/44

BIỆN PHÁP PHÒNG VỆ JAILBREAK
• Kiểm duyệt ngoài mô hình: lọc nội dung đầu vào/đầu ra bằng quy tắc hoặc bộ phân loại.
• Ràng buộc system prompt: cung cấp ví dụ từ chối yêu cầu có hại (In-Context Defense, ICD); chèn cảnh báo trước và sau đầu vào (Cautionary Warning Defense, CWD).
• Huấn luyện đối kháng đỏ–xanh: chủ động phát hiện kịch bản lỗi bằng kiểm thử tự động, đưa các tình huống đã tìm thấy vào huấn luyện an toàn để tăng robustness.

## Trang 42/44

JAILBREAK ĐA PHƯƠNG THỨC
• Tấn công qua modality phi chữ: thêm nhiễu đối kháng vào ảnh hoặc âm thanh.
• Tương tác xuyên modality: kết hợp văn bản, hình ảnh, âm thanh để làm mô hình hiểu sai hoặc trả nội dung không an toàn.
Bài giảng nhấn mạnh rằng an toàn chỉ dựa trên văn bản có thể không đủ khi dữ liệu đầu vào đa dạng.

## Trang 43/44

BÀI THỰC HÀNH LIÊN QUAN — EASYJAILBREAK
Bài giảng dẫn người học tới tài liệu thực hành jailbreak bằng thư viện EasyJailbreak.
Mục tiêu học tập:
1. Làm quen bộ công cụ EasyJailbreak.
2. Hiểu cách triển khai các phương pháp phổ biến và cách đánh giá kết quả.
Các thí nghiệm chỉ nên thực hiện trong môi trường và phạm vi đã được cho phép.

## Trang 44/44

CẢM ƠN!
Kết thúc bài giảng “An toàn nội dung mô hình lớn và tấn công jailbreak”.

