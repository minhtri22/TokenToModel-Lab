# Chương 10 — An toàn tác nhân

Nguồn gốc: `documents/chapter10/dive-into-safety.pdf` · commit `f84c04268794ef94f8949808bbc14ab8636763a0`.

**Nội dung dưới đây là phần chuyển ngữ/diễn giải tiếng Việt theo từng trang slide**, phục vụ đối chiếu với bản gốc; không bảo đảm từng câu chữ trong hình được thay thế.

## Trang 1/51

AN TOÀN TÁC NHÂN DỰA TRÊN MÔ HÌNH NGÔN NGỮ LỚN (LLM AGENT SAFETY)
Tác giả: Zhang Zhuosheng (张倬胜), Đại học Giao thông Thượng Hải.
Email: zhangzs@sjtu.edu.cn · Website: https://bcmi.sjtu.edu.cn/~zhangzs.

## Trang 2/51

MỤC LỤC
1. Tổng quan an toàn tác nhân: ứng dụng phổ biến, các dạng rủi ro.
2. Mô hình hóa nguy cơ: rủi ro độ tin cậy và an toàn.
3. Rủi ro tấn công: phía người dùng, phía mô hình, phía môi trường.
4. Phòng vệ an toàn: căn chỉnh nội sinh, đối kháng đỏ–xanh và giám sát bên ngoài.

## Trang 3/51

MỤC LỤC
1. Tổng quan an toàn tác nhân: ứng dụng phổ biến, các dạng rủi ro.
2. Mô hình hóa nguy cơ: rủi ro độ tin cậy và an toàn.
3. Rủi ro tấn công: phía người dùng, phía mô hình, phía môi trường.
4. Phòng vệ an toàn: căn chỉnh nội sinh, đối kháng đỏ–xanh và giám sát bên ngoài.

## Trang 4/51

TỪ TRÍ TUỆ NỘI DUNG ĐẾN TRÍ TUỆ HÀNH VI
Các giai đoạn/loại năng lực:
• Phân tích ngôn ngữ: tách từ, nhận dạng thực thể, NL2SQL.
• Hiểu kiến thức: trích thông tin, đọc hiểu, suy luận.
• Sinh nội dung: tóm tắt, dịch, hội thoại.
• Thực thi hành vi: gọi công cụ, phát triển phần mềm, điều khiển thiết bị.
Tác nhân LLM được định nghĩa là hệ thống dựa trên mô hình lớn có thể cảm nhận môi trường, lập kế hoạch, ra quyết định, dùng công cụ và cải tiến qua các vòng tương tác.

## Trang 5/51

TRÍ TUỆ NỘI DUNG DO MÔ HÌNH LỚN HỖ TRỢ
Nhờ sự phát triển của dữ liệu, thuật toán và khả năng tính toán, mô hình lớn có tiến bộ đáng kể trên các nhiệm vụ hiểu, suy luận và sáng tạo nội dung.
Ứng dụng: sinh văn bản, dịch máy, công cụ tìm kiếm, gợi ý tin tức, phân tích tài liệu, hội thoại hỏi đáp.

## Trang 6/51

TÁC NHÂN HỖ TRỢ TRÍ TUỆ HÀNH VI
Hệ thống dựa trên mô hình lớn có khả năng tự điều hướng luồng công việc và công cụ, điều chỉnh hoạt động dựa trên phản hồi thời gian thực.
Từ hiểu nội dung đến “biết và làm”: hướng tới tính tổng quát, tự chủ, thích ứng và tương tác xã hội.
Các modality: chữ, ảnh, tiếng nói, video. Các đầu ra/tác vụ: điều khiển hệ thống, công cụ, thiết bị; hỗ trợ khám phá khoa học; cộng tác nhiều tác nhân; lập kế hoạch và viết/sửa phần mềm.

## Trang 7/51

TỪ AN TOÀN MÔ HÌNH ĐẾN AN TOÀN TÁC NHÂN
Tác nhân không chỉ sinh nội dung mà còn có thể làm việc với môi trường bên ngoài, ví dụ tương tác để nhận dạng CAPTCHA hoặc thực hiện chuỗi thao tác.
Rủi ro jailbreak của LLM có thể chuyển thành rủi ro hành động thực tế trong hệ thống tác nhân.

## Trang 8/51

TOÀN CẢNH RỦI RO TÁC NHÂN
• Rủi ro an toàn nội dung.
• Rủi ro an toàn hành vi khi mô hình hành động trong môi trường.
• An toàn nội sinh của mô hình, bao gồm lỗ hổng và backdoor.
Hình nguồn phân loại backdoor theo giai đoạn dữ liệu, tiền huấn luyện, tinh chỉnh và mô hình lớn; ví dụ gồm đầu độc dữ liệu, cấy trigger, chuyển backdoor qua tiền huấn luyện và chỉnh sửa kiến thức.

## Trang 9/51

RỦI RO MỚI CỦA TÁC NHÂN
Rủi ro độ tin cậy: nhận thức không đầy đủ, quyết định suy luận không chắc chắn, khó dự báo hậu quả của hành động.
Rủi ro tấn công: bề mặt rộng gồm người dùng, mô hình, môi trường/công cụ, cộng đồng và cơ sở tri thức.
Ví dụ: lệch ý định, thực thi quá mức, thông tin gây nhiễu, chỉ dẫn độc hại, backdoor công cụ và thao túng tri thức.
Xu hướng: từ sinh nội dung sang hành vi; từ tấn công có giới hạn sang môi trường mở; từ phát hiện thụ động sang giám sát chủ động.

## Trang 10/51

MỤC LỤC
1. Tổng quan an toàn tác nhân: ứng dụng phổ biến, các dạng rủi ro.
2. Mô hình hóa nguy cơ: rủi ro độ tin cậy và an toàn.
3. Rủi ro tấn công: phía người dùng, phía mô hình, phía môi trường.
4. Phòng vệ an toàn: căn chỉnh nội sinh, đối kháng đỏ–xanh và giám sát bên ngoài.

## Trang 11/51

MÔ HÌNH ĐE DỌA (THREAT MODEL)
Tùy có hay không người tấn công chủ ý, nguy cơ tác nhân chia thành:
• Reliability risk: không có kẻ tấn công cố ý, nhưng agent vô tình gây hậu quả trong lúc làm nhiệm vụ.
• Attack risk: có bên chủ động dẫn dắt agent gây hậu quả, có thể là người dùng độc hại hoặc bên ngoài tác động vào môi trường.
Hình gốc biểu diễn agent nhận chỉ dẫn, tương tác với môi trường, gọi công cụ và nhận phản hồi.

## Trang 12/51

ĐỘ TIN CẬY CỦA TÁC NHÂN TRONG THẾ GIỚI THỰC
Trong tình huống nằm trong phân bố và có quy trình ổn định, agent có thể hoàn thành nhiệm vụ đơn giản.
Nhưng ở môi trường thật, các lệnh phức tạp, thiếu kiến thức chuyên ngành, nội dung giao diện xung đột và các trường hợp bất thường tạo ra rủi ro.
Ví dụ: “đặt lại đồ ăn hôm qua” gặp quảng cáo khuyến mãi; “đọc bài báo AI năm qua và dự báo xu hướng” đòi hỏi nhiều bước và thông tin đáng tin.

## Trang 13/51

BA TÌNH HUỐNG THẤT BẠI ĐỘ TIN CẬY
• UI-NEXUS: tác vụ tổng hợp, chuyển tiếp và dài hạn khiến nhiều mô hình không hoàn thành; hướng xử lý là mô hình hóa phụ thuộc và lập lịch.
• OS-Kairos: chỉ dẫn mơ hồ hoặc trang bất thường dẫn tới over-execution; hướng xử lý là tương tác người–máy thích nghi theo mức tin cậy.
• EnvDistract: nội dung môi trường xung đột chỉ dẫn người dùng khiến agent bỏ mục tiêu; hướng xử lý là quyết định hành động dựa trên ưu tiên.
Các kết quả được nêu từ công trình trích dẫn, không phải thí nghiệm được bản dịch tái thực hiện.

## Trang 14/51

PHÂN LOẠI RỦI RO TẤN CÔNG BÊN NGOÀI
Mục tiêu tấn công: nhiệm vụ xấu, chiếm quyền nhiệm vụ (task hijacking), lấy cắp riêng tư, làm mất khả năng phục vụ.
Kỹ thuật: đầu độc dữ liệu, jailbreak, injection, ví dụ đối kháng/nhiễu đối kháng.
Thành phần bị ảnh hưởng: cảm nhận, lập kế hoạch, công cụ, bộ nhớ.
Giai đoạn chịu tác động: nhận và hiểu chỉ dẫn; lập kế hoạch/chọn công cụ; gọi công cụ/thực hiện hành động.

## Trang 15/51

NGUỒN TẤN CÔNG VÀ BIỆN PHÁP ỨNG PHÓ
• Chỉ dẫn độc hại: có thể khiến agent làm việc gây hại; chặn thô cứng làm từ chối quá mức, nên xem xét cảnh báo/phản hồi an toàn.
• RAG/tool backdoor: dữ liệu truy xuất hoặc công cụ chứa trigger nhằm đổi đầu ra trong khi truy vấn thường vẫn hoạt động; cần phát hiện dữ liệu bất thường từ nguồn không tin cậy.
• Cộng đồng agent: agent bị thao túng có thể phát tán tri thức sai; cần bộ kiểm chứng sự thật hoặc tác nhân giám sát.
Bài giảng dẫn các công trình về guard models, TrojanRAG, kiến thức sai trong cộng đồng và quyền riêng tư đa phương thức.

## Trang 16/51

MỤC LỤC
1. Tổng quan an toàn tác nhân: ứng dụng phổ biến, các dạng rủi ro.
2. Mô hình hóa nguy cơ: rủi ro độ tin cậy và an toàn.
3. Rủi ro tấn công: phía người dùng, phía mô hình, phía môi trường.
4. Phòng vệ an toàn: căn chỉnh nội sinh, đối kháng đỏ–xanh và giám sát bên ngoài.

## Trang 17/51

CÁC ĐIỂM PHÁT SINH RỦI RO
Phía người dùng: chỉ dẫn/tệp đầu vào bị thao túng.
Phía mô hình: lỗ hổng, backdoor và hạn chế suy luận/lập kế hoạch/căn chỉnh.
Phía môi trường: injection qua trang web, hệ điều hành, môi trường ảo, ứng dụng, API, trình thông dịch và thiết bị thật.
Bề mặt tương tác gồm lịch sử, trạng thái hiện tại, hành động, quy tắc và thông tin phản hồi.

## Trang 18/51

CHUYỂN SANG TẤN CÔNG PHÍA NGƯỜI DÙNG
Các tấn công từ chỉ dẫn do người dùng hoặc bên giả mạo gửi vào, tìm cách khiến agent thực hiện nhiệm vụ trái yêu cầu an toàn.

## Trang 19/51

RỦI RO CỦA TÁC NHÂN NGÀY CÀNG RỘNG
Tấn công không chỉ còn nhắm vào một tình huống phân loại cố định mà chuyển sang nhiều kiểu tổng hợp nội dung và thao túng hành vi.
Năng lực thực thi của agent khiến lỗi mô hình có thể dẫn tới hậu quả ngoài môi trường số.

## Trang 20/51

TẤN CÔNG ĐỐI KHÁNG VỚI LLM
Công trình “Universal and Transferable Adversarial Attacks on Aligned Language Models” nghiên cứu những hậu tố gồm token không mang nghĩa thông thường nhưng có thể làm tăng khả năng mô hình trả lời yêu cầu không an toàn.
Hậu tố được tối ưu bằng phương pháp rời rạc theo gradient và các bước chọn tham lam, có thể có tính chuyển giao giữa prompt và mô hình.
Bài giảng dùng nghiên cứu này để minh họa rằng điều kiện an toàn có thể bị phá bởi đầu vào khác phân bố. Trang gốc có sơ đồ cụ thể.

## Trang 21/51

TẤN CÔNG QUA KÊNH BÊN: MÃ HÓA NỘI DUNG
Tài liệu trích nghiên cứu “GPT-4 Is Too Smart to Be Safe: Stealthy Chat with LLMs via Cipher” (arXiv:2308.06463).
Kỹ thuật được báo cáo dùng các hệ mã để trao đổi với LLM; trong một thiết lập tác giả ghi tỷ lệ phản hồi không an toàn lên tới 70,9% và nhận thấy mối liên hệ giữa năng lực mô hình và rủi ro khi đầu vào bị mã hóa.
Con số này chỉ phản ánh thí nghiệm của nghiên cứu được dẫn.

## Trang 22/51

KÊNH BÊN — BƯỚC 1: GIẢ LẬP TRAO ĐỔI BẰNG MẬT MÃ
Bài giảng mô tả giai đoạn đầu của phương pháp nghiên cứu: cho mô hình đóng vai người hiểu mật mã và yêu cầu trao đổi bằng cách biểu diễn đã mã hóa.
Mục tiêu kiểm tra: liệu cơ chế phát hiện nội dung bất thường có hoạt động khi ngữ nghĩa bị che bởi định dạng khác hay không.

## Trang 23/51

KÊNH BÊN — BƯỚC 2: ĐỔI BIỂU DIỄN CHỈ DẪN
Bài giảng mô tả việc chuyển đổi chỉ dẫn của người dùng qua công cụ mã hóa trước khi gửi tới LLM.
Tác động của việc mã hóa cần được đánh giá trong môi trường cho phép, vì thông điệp sau biến đổi có thể tránh một số bộ lọc dựa trên bề mặt văn bản.

## Trang 24/51

KÊNH BÊN — BƯỚC 3: GIẢI MÃ PHẢN HỒI
Sau khi gửi chỉ dẫn ở dạng mã hóa, người nghiên cứu xem phản hồi và giải mã về ngôn ngữ thông thường để đo liệu phản hồi có vi phạm tiêu chí an toàn hay không.
Cả ba bước trên được nguồn mô tả như một quy trình tấn công để đánh giá khả năng kháng chịu của hệ thống.

## Trang 25/51

CHUYỂN SANG TẤN CÔNG PHÍA MÔ HÌNH
Phần này tập trung vào các dạng nhiễm độc, backdoor và thay đổi hành vi của mô hình nền/thành phần bên trong.

## Trang 26/51

CÁC KIỂU BACKDOOR TRONG MÔ HÌNH LỚN
Bài giảng phân loại backdoor theo giai đoạn:
• Dữ liệu: đầu độc dữ liệu, thêm trigger trong mẫu huấn luyện.
• Tiền huấn luyện: chuyển backdoor qua pretraining hoặc những cơ chế tối ưu làm tăng khả năng tồn tại của trigger.
• Tinh chỉnh downstream: chuyển backdoor vào mô hình nhận.
• Mô hình lớn: backdoor dựa trên feedback bị đầu độc, chỉ dẫn ảo hoặc chỉnh sửa kiến thức.
Mô hình nhiễm backdoor thường trả lời như bình thường với đầu vào sạch, nhưng có thể tạo đầu ra do kẻ tấn công định trước khi gặp trigger.

## Trang 27/51

PHÂN LOẠI BACKDOOR CHI TIẾT
Các hướng nêu trong nguồn:
• Backdoor dựa trên phản hồi bị đầu độc.
• Backdoor bằng chỉ dẫn ảo (virtual instruction).
• Backdoor như plugin tri thức.
• Backdoor bằng định vị và thay đổi kiến thức.
• Backdoor gắn ngoài mô hình.
Tài liệu dẫn “UOR: Universal Backdoor Attacks on Pre-trained Language Models” (ACL 2024) và khảo sát các biện pháp đối phó trong mô hình NLP.

## Trang 28/51

TROJANRAG — CỬA HẬU TRONG TRUY XUẤT BỔ SUNG
TrojanRAG cho phép tác nhân tấn công tác động tới đầu ra LLM thông qua tri thức được truy xuất, trong khi các truy vấn sạch có thể vẫn hoạt động bình thường.
Ba kịch bản trong bảng gốc:
1. Chủ động làm lệch câu trả lời thực tế: ví dụ truy vấn nơi tổ chức Olympic bị khiến trả lời “China” thay vì đầu ra sạch “France”.
2. Lan truyền định kiến/thông tin sai theo cách thụ động: câu hỏi về vai trò lãnh đạo của phụ nữ bị trả lời mang tính cấm đoán, trong khi trả lời sạch là khẳng định.
3. Dùng dữ liệu truy xuất để lách căn chỉnh an toàn: đáp án bị thao túng hướng tới thông tin không an toàn; bảng gốc chỉ minh họa loại câu hỏi và đầu ra, không được thực hiện.
Chuỗi thành phần được minh họa: kho tri thức bị đầu độc và định nghĩa trigger; cài backdoor vào retriever; kết nối mô hình ngôn ngữ mà không cần thay tham số gốc; kích hoạt trong ngữ cảnh phù hợp. Tác giả nêu khả năng chuyển giữa các mô hình và giữ hiệu năng của truy vấn thông thường.
Nguồn trong slide: TrojanRAG: Retrieval-Augmented Generation Can Be Backdoor Driver in Large Language Models, arXiv:2405.13401.

## Trang 29/51

CHUYỂN SANG TẤN CÔNG PHÍA MÔI TRƯỜNG
Tác nhân có thể bị ảnh hưởng bởi nội dung hoặc chỉ dẫn nằm trong trang web, ứng dụng, công cụ và hệ thống bên ngoài, ngay cả khi người dùng đưa ra nhiệm vụ hợp lệ.

## Trang 30/51

MÔ HÌNH ĐE DỌA PHÍA MÔI TRƯỜNG
Các đối tượng: người dùng (user), tác nhân và hệ thống (agent & system), môi trường (environment), nguy cơ (risks) và tác nhân đe dọa (threats).
Thông tin từ môi trường là dữ liệu đầu vào không mặc định có thẩm quyền, do đó cần phân biệt nguồn chỉ dẫn và nguồn quan sát.

## Trang 31/51

VÍ DỤ TẤN CÔNG TỪ MÔI TRƯỜNG
• GUI injection: chèn quảng cáo, popup hoặc thông tin dẫn dắt vào màn hình, khiến agent bỏ nhiệm vụ ban đầu.
• Community manipulation: đưa một agent đã bị điều khiển vào cộng đồng nhiều tác nhân, khiến nó phát tán thông tin sai có sức thuyết phục.
Bài giảng dẫn các công trình “Flooding Spread of Manipulated Knowledge...”, “Caution for the Environment...” và “TrojanRAG”.

## Trang 32/51

GUI ENVIRONMENT INJECTION
Câu hỏi: MLLM có bị thông tin xuất hiện trên màn hình dẫn dắt tới mức quên chỉ dẫn gốc của người dùng không?
Khái niệm được dùng: tính trung thành (faithfulness) — agent có làm đúng mục tiêu người dùng, không để môi trường chiếm quyền điều khiển?
So sánh các bối cảnh: tình huống bình thường, tấn công phía người dùng và tấn công phía môi trường.

## Trang 33/51

XÂY DỰNG BỘ DỮ LIỆU KIỂM TRA ENVIRONMENTAL DISTRACTION
Tạo giao diện có yếu tố gây nhiễu tự nhiên nhưng vẫn cho phép thực hiện đúng tác vụ.
Với mục tiêu g, tác nhân A xem màn hình s_t và chọn hành động a_t.
Không gian nhãn hành động: trung thành (faithful), mất tập trung (distracted), không hợp lệ (invalid).
Bài giảng báo cáo 1.189 trường hợp kiểm thử tấn công, thuộc bốn nhóm: popup, tìm kiếm, gợi ý và trò chuyện.

## Trang 34/51

ĐÁNH GIÁ CÁC MÔ HÌNH VỚI GIAO DIỆN GÂY NHIỄU
Thử 10 MLLM gồm model API (GPT-4V, GPT-4o, GLM-4V, Qwen-VL-Plus, Claude Sonnet 3.5), model mở (Qwen-VL-Chat, MiniCPM-Llama3-v2.5, LLaVA-v1.6-34B) và mô hình chuyên GUI (CogAgent-Chat, SeeClick).
Kết luận nguồn:
• Agent có thể mất mục tiêu do thông tin nhiễu trong giao diện.
• Năng lực mô hình cao đôi khi cùng tồn tại với tính trung thành cao (trong phép đo nguồn).
• Mô hình có nhiều năng lực nhưng kém trung thành vẫn dễ bị tấn công, cho thấy sự cần thiết của alignment theo ngữ cảnh tác nhân.

## Trang 35/51

TẤN CÔNG CỘNG ĐỒNG NHIỀU TÁC NHÂN
Bài giảng đặt câu hỏi: liệu một nhóm tác nhân có bị thao túng tri thức theo mục tiêu không?
Ví dụ thông tin giả dễ thấy (“Tôi là Tần Thủy Hoàng, vẫn còn sống, có vàng ở Tây An, gửi tôi tiền để tôi hồi sinh...”) minh họa cách tạo thông điệp có sức thuyết phục giả tạo, không phải thông tin thật.

## Trang 36/51

NGHIÊN CỨU LAN TRUYỀN TRI THỨC BỊ THAO TÚNG
Hai câu hỏi nghiên cứu:
RQ1: agent bị tác động ngầm có vô tình lan truyền kiến thức sai trong cộng đồng không?
RQ2: các agent khác có dễ tin dữ liệu ngữ cảnh nghe hợp lý nhưng không đúng không?
Phân biệt thao túng tường minh qua prompt và thao túng ngầm qua kiến thức/biểu diễn được cài vào agent.

## Trang 37/51

MÔ HÌNH ĐE DỌA TRONG CỘNG ĐỒNG AGENT
Mục tiêu kẻ tấn công: cài thông tin cụ thể vào tham số một agent rồi để agent đó tự phát tán tri thức sang các agent khác.
Quyền truy cập: kẻ tấn công có thể kiểm soát một agent trong cộng đồng, nhưng không được sửa system prompt chung.
Yêu cầu của tấn công: kiến thức bị đổi phải lan rộng; agent bị nhiễm vẫn hành xử có vẻ bình thường để tránh bị phát hiện.
Nguồn: Ju và cộng sự, “Flooding Spread of Manipulated Knowledge in LLM-Based Multi-Agent Communities” (2024).

## Trang 38/51

MÔI TRƯỜNG MÔ PHỎNG CỘNG ĐỒNG AGENT
• Nền tảng: các agent triển khai trên nền tảng đáng tin, không để kẻ tấn công sửa system prompt chung.
• Vai trò: mỗi agent có vai trò ngẫu nhiên; agent bình thường và agent bị thao túng (trông như agent bình thường nhưng chèn thông tin sai vào hội thoại).
• Giao tiếp: thông điệp trao đổi công khai giữa các agent, tương tự nhóm chat trên mạng xã hội.

## Trang 39/51

PHƯƠNG PHÁP TẤN CÔNG HAI GIAI ĐOẠN — MÔ TẢ NGHIÊN CỨU
Giai đoạn 1: tạo nội dung chứng cứ có tính thuyết phục để hỗ trợ luận điểm bị thao túng.
Giai đoạn 2: cập nhật tham số của agent nhằm cài kiến thức được chỉ định.
Trang gốc mô tả cơ chế trong nghiên cứu về khuếch tán thông tin giả giữa tác nhân, không phải hướng dẫn thực thi.

## Trang 40/51

KIỂM TRA GIẢ THUYẾT VỀ ĐỘ MONG MANH
Kết quả nguồn cho thấy agent lành tính dễ chấp nhận tri thức bị thao túng hơn khi nó đi cùng “chứng cứ” mạch lạc, nghe hợp lý.
Các chế độ thử: không có ngữ cảnh (w/o Prompt); đưa trực tiếp đáp án sai không có chứng cứ; đưa chứng cứ giả nhưng mạch lạc do cùng agent tạo.
Mô hình bị thao túng có thể tạo chứng cứ giả khiến tác nhân khác tin tưởng.

## Trang 41/51

THÍ NGHIỆM LAN TRUYỀN TRI THỨC
• Kiến thức phản thực tế dễ lan qua nhóm agent lành tính; thông tin độc hại lan thành công ở tỷ lệ thấp hơn đôi chút trong thí nghiệm nguồn.
• Tỷ lệ lan truyền tăng theo số lượt hội thoại; cộng đồng nhỏ có thể dễ bị ảnh hưởng bởi thông tin sai hơn.
• Khi đo MMLU, năng lực ngôn ngữ và suy luận cơ bản của các agent gần như không đổi, dù kiến thức bị thao túng.
Đây là kết quả được trích từ một nghiên cứu cụ thể.

## Trang 42/51

MỤC LỤC
1. Tổng quan an toàn tác nhân: ứng dụng phổ biến, các dạng rủi ro.
2. Mô hình hóa nguy cơ: rủi ro độ tin cậy và an toàn.
3. Rủi ro tấn công: phía người dùng, phía mô hình, phía môi trường.
4. Phòng vệ an toàn: căn chỉnh nội sinh, đối kháng đỏ–xanh và giám sát bên ngoài.

## Trang 43/51

CÁC BIỆN PHÁP PHÒNG VỆ AN TOÀN CHO TÁC NHÂN
Bài giảng chuyển sang ba tầng bảo vệ chính:
1. Căn chỉnh nội sinh (intrinsic alignment) của mô hình.
2. Kiểm thử đỏ–xanh thường xuyên (red teaming/blue teaming).
3. Giám sát ngoài hệ thống (external supervision).

## Trang 44/51

THÁCH THỨC CĂN BẢN: CĂN CHỈNH KHÔNG ĐỒNG NGHĨA AN TOÀN
• Alignment có thể bị vượt qua bằng jailbreak qua người dùng hoặc môi trường.
• Mục tiêu helpfulness và harmlessness có thể xung đột. Nếu luôn từ chối mọi yêu cầu, hệ thống có vẻ rất an toàn nhưng hoàn toàn không hữu ích.
• Nội dung câu trả lời vô hại không có nghĩa hành vi thực thi sau đó cũng vô hại.
Cần đo an toàn hành vi trong bối cảnh nhiều lượt và có công cụ.

## Trang 45/51

R-JUDGE: ĐÁNH GIÁ NHẬN THỨC RỦI RO AN TOÀN TÁC NHÂN
Theo bài giảng, R-Judge cho thấy nhiều mô hình thiếu nhận thức rủi ro hành vi; prompt đơn giản và few-shot chưa đủ để cải thiện một cách đáng tin.
Đánh giá khoảng 27 tình huống thuộc hệ điều hành, ứng dụng, môi trường ảo, nhà thông minh, v.v.
Nhóm nguyên nhân: tuân thủ chỉ dẫn, lập kế hoạch, kiến thức bối cảnh, alignment giá trị.
Loại rủi ro: an toàn hệ thống, pháp luật, sức khỏe và quyền riêng tư/danh dự.
Nguồn: “R-Judge: Benchmarking Safety Risk Awareness for LLM Agents” (Findings of EMNLP 2024).

## Trang 46/51

KHUNG PHÒNG VỆ AN TOÀN TÁC NHÂN
Hai lớp bổ trợ:
• Model-level Evaluation for Development: kiểm tra an toàn nội sinh khi phát triển.
• System-level Safeguard for Deployment: bảo vệ đầu vào, đầu ra và thao tác khi vận hành, bao gồm người dùng và môi trường.
Các cơ chế: phân tích ý định, chặn bất thường, phát hiện yêu cầu nguy hiểm, xác minh hành động, dự báo hậu quả, chạy mô phỏng; alignment nội sinh và giám sát ngoài.
Hình gốc liên kết các tầng ứng dụng, interface, hệ điều hành và phần cứng.

## Trang 47/51

PHÒNG VỆ 1 — CĂN CHỈNH NỘI SINH
Bài giảng phân biệt:
• Pre-alignment truyền thống: căn chỉnh sở thích/giá trị trên câu hỏi một lượt, ít gắn bối cảnh.
• Post-alignment cho agent: căn chỉnh chuẩn mực hành vi trên tác vụ nhiều bước và phụ thuộc tình huống.
Ví dụ nguồn đối chiếu câu trả lời từ chối hướng dẫn nguy hiểm và hành động đăng bài có thể vô ý tiết lộ mật khẩu từ một tệp.
Một agent an toàn phải kiểm tra dữ liệu và xin xác nhận trước hành động có thể phơi lộ thông tin riêng tư.

## Trang 48/51

PHÒNG VỆ 2 — ĐỐI KHÁNG ĐỎ–XANH LIÊN TỤC
Mô hình, công cụ và kỹ thuật tấn công thay đổi theo thời gian, nên cần kiểm thử chủ động và cải tiến liên tục.
Red teaming tìm các điểm yếu trong tương tác người dùng, môi trường và công cụ; blue teaming sửa/làm giảm rủi ro.
Ví dụ huấn luyện đối kháng: fine-tuning để phòng thủ trước injection.
Bài báo tham khảo: RedAgent — Red Teaming Large Language Models with Context-Aware Autonomous Language Agent.

## Trang 49/51

PHÒNG VỆ 3 — GIÁM SÁT NGOÀI BẰNG GUARDAGENT
Thay vì chỉ giám sát bản thân mô hình, có thể dùng một tác nhân giám sát khác, giúp người dùng tùy chỉnh quy tắc an toàn.
GuardAgent theo dõi đầu ra/hành động agent, sử dụng kiến thức về quy tắc và ví dụ để tạo mã kiểm tra/bảo vệ.
Nguồn: Xiang và cộng sự, “GuardAgent: Safeguard LLM Agents by a Guard Agent via Knowledge-Enabled Reasoning”, arXiv:2406.09187.

## Trang 50/51

TÀI LIỆU XEM THÊM
Video: https://dl.ccf.org.cn/video/videoDetail.html?_ack=1&id=7346281079359488
• An toàn mô hình lớn và siêu căn chỉnh (CNCC 2024).
• Khảo sát an toàn hành vi của các tác nhân dựa trên mô hình lớn.

## Trang 51/51

CẢM ƠN!
Tác giả: Zhang Zhuosheng.
Email: zhangzs@sjtu.edu.cn · Trang web: https://bcmi.sjtu.edu.cn/~zhangzs.
