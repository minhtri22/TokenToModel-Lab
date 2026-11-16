# Chương 03 — Chỉnh sửa kiến thức (Knowledge Editing)

Nguồn gốc: `documents/chapter3/dive_edit_0410.pdf` · commit `f84c04268794ef94f8949808bbc14ab8636763a0`.

**Nội dung dưới đây là phần chuyển ngữ/diễn giải tiếng Việt theo từng trang slide**, phục vụ đối chiếu với bản gốc; không bảo đảm từng câu chữ trong hình được thay thế.

## Trang 1/21

CHỈNH SỬA KIẾN THỨC CHO MÔ HÌNH NGÔN NGỮ (KNOWLEDGE EDITING FOR LANGUAGE MODELS)

## Trang 2/21

MỤC LỤC
Q1: Vì sao cần chỉnh sửa kiến thức?
Q2: Làm thế nào để chỉnh sửa mô hình ngôn ngữ (LM)?
Q3: Các ứng dụng và những vấn đề cần xem xét lại.

## Trang 3/21

LLM CÓ THỂ HỌC CẢ NHỮNG KIẾN THỨC KHÔNG MONG MUỐN
• Thiên lệch (bias).
• Thông tin sai lệch (misinformation).
• Nội dung gây hại (harmful content).
• Sự kiện lỗi thời (outdated facts).
Đây là các loại hành vi/kiến thức khiến việc chỉnh sửa mô hình trở nên hữu ích.

## Trang 4/21

VÍ DỤ KIẾN THỨC LỖI THỜI TRONG LLM
Mô hình được huấn luyện ở một thời điểm có thể trả lời dựa trên thực tế của thời điểm đó.
Ví dụ trên slide: câu hỏi “Ai là tổng thống Mỹ?”; câu trả lời “Trump” có thể đúng theo mốc năm 2019 nhưng không còn đúng trong một giai đoạn khác. Một mô hình huấn luyện năm 2018 vẫn được sử dụng năm 2019/những năm sau sẽ gặp rủi ro tri thức lỗi thời.
Các vấn đề liên quan khác: thiên lệch, thông tin sai và nội dung gây hại. Tính đúng/sai luôn phụ thuộc mốc thời gian và ngữ cảnh.

## Trang 5/21

VÍ DỤ VỀ THIÊN LỆCH, THÔNG TIN LỖI THỜI VÀ CÁCH DIỄN ĐẠT
• Tình huống cặp đôi tranh cãi về việc nhà: LLM có thể suy đoán người nam làm việc nhà ít hơn mà thiếu chứng cứ — ví dụ thiên lệch giới.
• Câu hỏi số lần Messi giành World Cup: đầu ra trên slide ghi “tính đến lần cập nhật kiến thức tháng 1/2022, Messi chưa vô địch cùng Argentina”; phát biểu này đã lỗi thời sau giải World Cup 2022.
• Một câu hỏi về quan hệ huyết thống có thể dẫn tới đầu ra phản cảm hoặc diễn đạt không phù hợp.
Bài học: mô hình có thể học hoặc tạo ra phản hồi không mong muốn; cần định nghĩa hành vi sửa và phạm vi tác động.

## Trang 6/21

ĐỊNH NGHĨA BÀI TOÁN CHỈNH SỬA KIẾN THỨC
Mục tiêu của Knowledge Editing là điều chỉnh hiệu quả hành vi của một mô hình nền ban đầu đối với một mô tả chỉnh sửa cụ thể (edit descriptor).
Câu hỏi: có thể cập nhật mô hình ngôn ngữ lớn một cách hiệu quả mà không phải huấn luyện lại toàn bộ hay không?

## Trang 7/21

TIÊU CHÍ ĐÁNH GIÁ CHỈNH SỬA KIẾN THỨC
• Reliability/Success: tỷ lệ chỉnh sửa thành công theo yêu cầu Z_e; đánh giá độ chính xác sau chỉnh sửa trên mục tiêu.
• Generalization: hiệu quả với các đầu vào khác thuộc phạm vi kiến thức vừa chỉnh sửa.
• Portability: chuyển được kiến thức đã sửa sang câu hỏi liên quan, như đổi chủ thể, quan hệ ngược hoặc câu hỏi suy luận một bước.
• Locality: thay đổi được giới hạn trong phạm vi mục tiêu, không làm ảnh hưởng các đầu vào ngoài phạm vi; so sánh hành vi trước và sau.
• Efficiency: thời gian, tài nguyên GPU và bộ nhớ cần thiết.

## Trang 8/21

MỤC LỤC — CÁCH CHỈNH SỬA MÔ HÌNH NGÔN NGỮ
Q1: Tại sao chỉnh sửa kiến thức cần thiết?
Q2: Các phương pháp chỉnh sửa LM?
Q3: Ứng dụng và những câu hỏi mở?

## Trang 9/21

GIẢI PHÁP NỘI BỘ: GIẢI THÍCH BỘ NHỚ CỦA MÔ HÌNH
Mở “hộp đen” LLM để tìm hiểu cơ chế lưu trữ và truy xuất kiến thức.
• Một cách diễn giải là mạng Feed-Forward Network (FFN) trong khối Transformer hoạt động tương tự bộ nhớ.
• Ma trận trọng số thứ nhất có thể đóng vai trò khóa (keys); ma trận thứ hai đóng vai trò giá trị (values).
Tham khảo bài báo “Transformer Feed-Forward Layers Are Key-Value Memories”, EMNLP 2021.

## Trang 10/21

ĐỊNH VỊ VÀ CHỈNH SỬA LIÊN KẾT SỰ KIỆN TRONG GPT
Bài báo tham khảo: “Locating and Editing Fact Associations in GPT”, NeurIPS 2022.
Slide gốc minh họa phương pháp dùng các thí nghiệm can thiệp để xác định vị trí mà mô hình truy xuất thông tin thực tế; sơ đồ gốc được giữ nguyên ở phía trên.

## Trang 11/21

ĐỊNH VỊ TRI THỨC BẰNG CAN THIỆP NHÂN QUẢ
Tiếp tục trình bày “Locating and Editing Fact Associations in GPT” (NeurIPS 2022).
Các hình trên trang gốc mô tả cách thay đổi/khôi phục các trạng thái bên trong mạng để phát hiện vị trí ảnh hưởng mạnh đến dự đoán sự kiện.

## Trang 12/21

MỘT SỐ GỢI Ý THỰC NGHIỆM TỪ ROME
• Lựa chọn một sự kiện/tri thức cụ thể cần chỉnh sửa.
• Tìm vị trí có thể ảnh hưởng đến việc truy xuất sự kiện: các lớp nông hoặc trung gian, đặc biệt FFN/MLP.
• Chú ý biểu diễn tại token cuối của cụm từ chỉ chủ thể (subject).
• Phương pháp tiêu biểu: ROME (Rank-One Model Editing).
Nguồn: “Locating and Editing Fact Associations in GPT”, NeurIPS 2022.

## Trang 13/21

ROME: TRUY VẾT NHÂN QUẢ VÀ ÁNH XẠ KHÓA–GIÁ TRỊ
• ROME định vị tri thức bằng phân tích truy vết nhân quả (causal tracing).
• Kết quả được trích dẫn: các ánh xạ khóa–giá trị trong lớp MLP ở vùng trung gian có vai trò quan trọng trong việc truy xuất dữ kiện về chủ thể.
Đây là kết luận của công trình được giới thiệu; không có nghĩa mọi sự kiện trong mọi kiến trúc LLM đều được lưu theo một vị trí duy nhất.

## Trang 14/21

ROME: MINH HỌA QUY TRÌNH CHỈNH SỬA THỰC TẾ
Trang nguồn tiếp tục sơ đồ từ “Locating and Editing Fact Associations in GPT” (NeurIPS 2022). Chủ đề là xác định và thay đổi liên kết giữa một thực thể/chủ thể với dữ kiện trong tham số của mô hình.
Xem hình gốc để đối chiếu các mũi tên và vùng mạng được can thiệp.

## Trang 15/21

GIẢI PHÁP BÊN NGOÀI: KHUNG XỬ LÝ VỚI BỘ NHỚ PHỤ
Bài báo: “Memory-Based Model Editing at Scale”, ICML 2022.
• Dùng các mô-đun hỗ trợ bên ngoài thay vì chỉ chỉnh trọng số mô hình gốc.
• SERAC tích hợp bộ nhớ ngoài và một bộ phân loại phạm vi (scope classifier) để xác định câu hỏi có thuộc vùng chỉnh sửa hay không.
• Nếu thuộc phạm vi, câu hỏi được xử lý bằng mô-đun phản thực tế (counterfactual) gắn với mục tiêu đã sửa; nếu không thuộc, vẫn chuyển qua mô hình ngôn ngữ gốc.

## Trang 16/21

PHƯƠNG ÁN CHO LLM: KẾT HỢP NĂNG LỰC SUY LUẬN NHIỀU BƯỚC
Bài báo: “MQuAKE: Assessing Knowledge Editing in Language Models via Multi-Hop Questions”.
• MeLLo: với câu hỏi phức tạp, tách thành câu hỏi con dựa vào chuỗi suy luận (Chain-of-Thought), rồi truy xuất kiến thức đã sửa ở từng bước.
Ý tưởng là kiểm tra khả năng tri thức cập nhật được sử dụng trong câu hỏi nhiều bước, không chỉ prompt trực tiếp.

## Trang 17/21

MỤC LỤC — ỨNG DỤNG VÀ CÁC VẤN ĐỀ CẦN XEM XÉT
Q1: Vì sao cần Knowledge Editing?
Q2: Làm sao chỉnh sửa LM?
Q3: Ứng dụng và suy nghĩ mở rộng.

## Trang 18/21

ỨNG DỤNG CHO AI ĐÁNG TIN CẬY
Câu hỏi: thông tin nhạy cảm có thể thực sự bị xóa khỏi LLM không?
Tham khảo “Can Sensitive Information Be Deleted From LLMs? Objectives for Defending Against Extraction Attacks”, ICLR 2022.
Một phát hiện được trình bày: thông tin được “xóa” khỏi đầu ra vẫn có thể còn hiện diện trong các trạng thái ẩn trung gian của mô hình. Do đó việc không xuất thông tin chưa đủ để chứng minh kiến thức đã bị loại khỏi tham số.

## Trang 19/21

ỨNG DỤNG: CHỈNH SỬA MÔ HÌNH BẰNG ĐẠI SỐ TÁC VỤ
Tham khảo “Editing Models with Task Arithmetic”.
• Task Arithmetic: phép toán trên các vector tác vụ (task vectors) có thể làm thay đổi hành vi mô hình ngôn ngữ theo hướng mong muốn.
• Tác nhân cá nhân hóa: điều chỉnh cách nói, ví dụ bắt chước những phong cách gắn với các kiểu tính cách MBTI.
Các ứng dụng thuộc lĩnh vực chỉnh sửa/cá nhân hóa mô hình, cần đánh giá hiệu ứng ngoài phạm vi mục tiêu.

## Trang 20/21

ỨNG DỤNG: CHỈNH SỬA “TÍNH CÁCH” CHO LLM
Bài báo: “Editing Personality For Large Language Models”.
• Tạo tác nhân được cá nhân hóa.
• Chỉnh phong cách ngôn ngữ của mô hình nhằm mô phỏng những đặc điểm trong các kiểu MBTI.
Năng lực mô phỏng phong cách không đồng nghĩa mô hình có tính cách hoặc giá trị con người theo nghĩa tâm lý học.

## Trang 21/21

TÀI LIỆU THỰC HÀNH
Bộ bài “Học mô hình lớn bằng thực hành” (动手学系列):
https://o5xrjmm79p.feishu.cn/docx/MHuPdtNaqozNb0xM0LDcPC5Zn9c
Mục tiêu:
1. Làm quen với thư viện EasyEdit.
2. Nắm phương pháp chỉnh sửa mô hình ngôn ngữ ở mức cơ bản nhất.
3. Hiểu cách chọn các phương pháp chỉnh sửa và trường hợp áp dụng.
