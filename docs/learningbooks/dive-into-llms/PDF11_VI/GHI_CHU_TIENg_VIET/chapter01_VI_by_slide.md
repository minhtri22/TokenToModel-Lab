# Chương 01 — Tổng quan và phát triển mô hình lớn

Nguồn gốc: `documents/chapter1/dive-into-llm.pdf` · commit `f84c04268794ef94f8949808bbc14ab8636763a0`.

**Nội dung dưới đây là phần chuyển ngữ/diễn giải tiếng Việt theo từng trang slide**, phục vụ đối chiếu với bản gốc; không bảo đảm từng câu chữ trong hình được thay thế.

## Trang 1/77

CÔNG NGHỆ VÀ SỰ PHÁT TRIỂN CỦA MÔ HÌNH LỚN
Tác giả: Zhang Zhuosheng (张倬胜), Khoa Khoa học Máy tính, Đại học Giao thông Thượng Hải.
Email: zhangzs@sjtu.edu.cn · https://bcmi.sjtu.edu.cn/~zhangzs

## Trang 2/77

MỤC LỤC
1. Tổng quan mô hình lớn: quá trình phát triển và các khái niệm.
2. Mô hình tiền huấn luyện: các dạng encoder, decoder, encoder–decoder và kiến trúc.
3. Mô hình ngôn ngữ quy mô lớn: thay đổi phương thức xây dựng, đại diện tiêu biểu, kỹ thuật cốt lõi và cách triển khai.
4. Mở rộng khái niệm: mô hình theo lĩnh vực, nền tảng đa phương thức và nền tảng tác nhân.

## Trang 3/77

MỤC LỤC
1. Tổng quan mô hình lớn: quá trình phát triển và các khái niệm.
2. Mô hình tiền huấn luyện: các dạng encoder, decoder, encoder–decoder và kiến trúc.
3. Mô hình ngôn ngữ quy mô lớn: thay đổi phương thức xây dựng, đại diện tiêu biểu, kỹ thuật cốt lõi và cách triển khai.
4. Mở rộng khái niệm: mô hình theo lĩnh vực, nền tảng đa phương thức và nền tảng tác nhân.

## Trang 4/77

QUÁ TRÌNH PHÁT TRIỂN TRÍ TUỆ NHÂN TẠO
Công nghệ AI chuyển từ dữ liệu nhỏ sang dữ liệu lớn, từ mô hình nhỏ sang mô hình lớn, từ ứng dụng chuyên biệt sang hệ thống tổng quát hơn.
Mô hình lớn thường dùng tự giám sát (self-supervised) trên lượng dữ liệu không gán nhãn rất lớn, học các quy luật ngôn ngữ và tri thức thế giới.
Giao tiếp bằng ngôn ngữ tự nhiên hỗ trợ xử lý nhiều nhiệm vụ, bối cảnh và lĩnh vực. Các nhánh mở rộng gồm mô hình ngành dọc, nền tảng đa phương thức và tác nhân.
Nguồn: Wayne Xin Zhao và cộng sự, A Survey of Large Language Models.

## Trang 5/77

PHẠM VI KHÁI NIỆM “MÔ HÌNH LỚN”
Các nhóm được bài giảng phân biệt:
• Mô hình ngôn ngữ tiền huấn luyện (Pre-trained Language Models).
• Mô hình ngôn ngữ quy mô lớn (Large Language Models).
• Nền tảng đa phương thức (Multimodal Foundation Models).
• Nền tảng tác nhân (Agent Foundation Models).
• Mô hình chuyên ngành (Vertical/Domain-specific Models).

## Trang 6/77

MỤC LỤC
1. Tổng quan mô hình lớn: quá trình phát triển và các khái niệm.
2. Mô hình tiền huấn luyện: các dạng encoder, decoder, encoder–decoder và kiến trúc.
3. Mô hình ngôn ngữ quy mô lớn: thay đổi phương thức xây dựng, đại diện tiêu biểu, kỹ thuật cốt lõi và cách triển khai.
4. Mở rộng khái niệm: mô hình theo lĩnh vực, nền tảng đa phương thức và nền tảng tác nhân.

## Trang 7/77

MÔ HÌNH NGÔN NGỮ TIỀN HUẤN LUYỆN
Đây là một hướng phát triển quan trọng của NLP, với các mô hình như ELMo, BERT và GPT-1/2.
Huấn luyện tự giám sát trên dữ liệu lớn, sau đó tinh chỉnh (fine-tuning) cho từng nhiệm vụ cụ thể; tận dụng quy mô dữ liệu, mô hình và hạ tầng tính toán.
Ứng dụng ban đầu tập trung vào phân tích và hiểu ngôn ngữ. Hình gốc cho thấy quy trình pretraining rồi chuyển giao sang nhiệm vụ downstream.

## Trang 8/77

CÁC HỌ KIẾN TRÚC TIỀN HUẤN LUYỆN
• Encoder-only: điển hình BERT.
• Decoder-only: điển hình GPT.
• Encoder–decoder: điển hình T5/BART.
Trước khoảng 2021, encoder và encoder–decoder tạo nhiều biến thể, thường được gọi vui là “BERTology”. Sau đó, sự phát triển nhanh của decoder-only thúc đẩy làn sóng mô hình sinh thế hệ mới.
Đây là cách phân kỳ lịch sử được bài giảng trình bày.

## Trang 9/77

MỤC TIÊU HUẤN LUYỆN THEO KIẾN TRÚC
Từ góc độ tiền huấn luyện tự giám sát:
• Encoder-only thường dùng Masked Language Modeling (MLM): dự đoán token bị che.
• Decoder-only dùng Auto-regressive Language Modeling: dự đoán token kế tiếp dựa trên tiền tố.
• Encoder–decoder dùng Sequence-to-Sequence Modeling: mã hóa chuỗi đầu vào và sinh chuỗi đích.
Nguồn: Ding và cộng sự, Parameter-efficient fine-tuning of large-scale pre-trained language models.

## Trang 10/77

ENCODER-ONLY (BERT, RoBERTa, ALBERT)
Mục tiêu huấn luyện chính: mô hình ngôn ngữ có che token (Masked Language Modeling, MLM).
Transformer Encoder quan sát ngữ cảnh hai chiều, dự đoán vị trí `[MASK]` bằng các token thích hợp.
Ví dụ hình gốc: câu tiếng Trung chứa token bị che trong nội dung “Cùng nhau học quy trình phát triển mô hình lớn”.

## Trang 11/77

DECODER-ONLY (GPT, LLAMA, PALM)
Mục tiêu chính: mô hình ngôn ngữ tự hồi quy (autoregressive language modeling).
Transformer Decoder dự đoán tuần tự token mới từ các token đứng trước, thường theo một chiều trái sang phải.
Ví dụ hình gốc chỉ ra chuỗi đầu vào với `[BOS]`, nhiều bước dự đoán từ hiện tại tới token tiếp theo.

## Trang 12/77

SO SÁNH ENCODER VÀ DECODER
Encoder (BERT):
• Ưu điểm: tận dụng ngữ cảnh hai chiều, phù hợp hiểu ngôn ngữ.
• Hạn chế: sử dụng token `[MASK]` làm khác phân bố giữa pretraining và fine-tuning; có giả định gần độc lập đối với một số token bị che.
Decoder (GPT):
• Ưu điểm: tự nhiên cho nhiệm vụ sinh, dễ tổ chức dữ liệu huấn luyện quy mô lớn.
• Hạn chế: cơ chế nhân quả một chiều trong dự đoán token, không tận dụng trực tiếp thông tin tương lai khi sinh.

## Trang 13/77

ENCODER–DECODER (T5, BART)
Mục tiêu: mô hình hóa chuỗi sang chuỗi (Sequence-to-Sequence).
Encoder đọc chuỗi nguồn; Decoder sinh chuỗi đích theo thứ tự, có thể truy cập biểu diễn của toàn bộ chuỗi nguồn qua cross-attention.
Ví dụ trang gốc dùng các đoạn văn bản và ký hiệu `<X>`, `<Y>`, `<Z>` để minh họa tác vụ tái tạo/chuyển đổi.

## Trang 14/77

CHỌN KIẾN TRÚC THEO BÀI TOÁN
• Encoder-only: thường phù hợp phân loại, hồi quy và nhiệm vụ phân biệt.
• Decoder-only: thường phù hợp các tác vụ sinh nội dung mở.
• Encoder–decoder: có khả năng phục vụ cả bài toán phân biệt và sinh có điều kiện.
Lựa chọn thực tế còn phụ thuộc dữ liệu, tài nguyên và giao thức đánh giá.

## Trang 15/77

KIẾN TRÚC MÔ HÌNH NGÔN NGỮ: RNN VÀ TRANSFORMER
RNN/LSTM: nắm quan hệ tuần tự, nhưng có thể khó tối ưu gradient, xử lý chậm và hạn chế với phụ thuộc dài.
Transformer: thay cơ chế lặp bằng self-attention để xử lý ngữ cảnh; dùng ma trận Query, Key và Value để nắm phụ thuộc, nhiều tầng với multi-head attention và feed-forward network (FFN).
Thêm biểu diễn vị trí (positional encoding) để mô hình biết thứ tự token.
Tham khảo: “Attention Is All You Need”.

## Trang 16/77

MỤC LỤC
1. Tổng quan mô hình lớn: quá trình phát triển và các khái niệm.
2. Mô hình tiền huấn luyện: các dạng encoder, decoder, encoder–decoder và kiến trúc.
3. Mô hình ngôn ngữ quy mô lớn: thay đổi phương thức xây dựng, đại diện tiêu biểu, kỹ thuật cốt lõi và cách triển khai.
4. Mở rộng khái niệm: mô hình theo lĩnh vực, nền tảng đa phương thức và nền tảng tác nhân.

## Trang 17/77

TOÀN CẢNH CÁC MÔ HÌNH LỚN
Trang nguồn chứa biểu đồ/danh mục các mô hình ngôn ngữ lớn tiêu biểu theo thời gian và quy mô.
Nguồn: Wayne Xin Zhao và cộng sự, A Survey of Large Language Models. Xem hình gốc để đối chiếu tên và mốc phát triển.

## Trang 18/77

THAY ĐỔI MÔ HÌNH PHÁT TRIỂN KHI XUẤT HIỆN LLM
• Về công nghệ: từ huấn luyện riêng từng tác vụ sang “tiền huấn luyện chung + hậu huấn luyện” hoặc “tiền huấn luyện + học qua prompt”.
• Về biểu diễn nhiệm vụ: từ nhiều dạng đầu ra riêng lẻ sang mô hình hóa chuỗi-to-chuỗi thống nhất.
Trước đây mỗi nhóm tự huấn luyện toàn pipeline; giờ một mô hình nền được tiền huấn luyện tập trung rồi tùy biến qua instruction tuning, RL, prompting, workflow orchestration hoặc fine-tuning nhẹ.

## Trang 19/77

THAY ĐỔI PHƯƠNG THỨC XỬ LÝ NHIỆM VỤ
Bài giảng nhấn mạnh hai chuyển đổi:
• Huấn luyện: từ mô hình riêng cho từng nhiệm vụ sang mô hình nền được cải thiện qua hậu huấn luyện.
• Ứng dụng: dùng prompt để chuyển bài toán khác nhau thành yêu cầu đầu vào–đầu ra thống nhất.
Tham khảo: Chung và cộng sự, “Scaling Instruction-Finetuned Language Models”, JMLR 2024.

## Trang 20/77

MÔ HÌNH NGÔN NGỮ QUY MÔ LỚN
LLM học các phân bố xác suất phức tạp từ dữ liệu rất lớn với thuật toán và hạ tầng tính toán đáng kể.
Đặc trưng mà bài giảng nhấn mạnh: chi phí huấn luyện/suy luận cao hơn, khả năng chuyển giao rộng hơn, đôi khi có biểu hiện năng lực “xuất hiện” ở quy mô lớn.
Bảng gốc đối chiếu ELMo/BERT/GPT-1/2 với GPT-3/ChatGPT/LLaMA theo kiến trúc, dữ liệu, quy mô, cách chuyển giao, loại tác vụ và khả năng in-context learning/CoT. Các ngưỡng kích thước nêu là mô tả lịch sử, không phải định nghĩa chặt chẽ.

## Trang 21/77

XU HƯỚNG CỦA LLM HIỆN ĐẠI
• Dữ liệu huấn luyện đa dạng: không chỉ văn bản tự nhiên, còn có mã lập trình, công thức hóa học, chuỗi gene, hình ảnh, v.v.
• Huấn luyện chuyển từ mô hình phân biệt như BERT sang nhiều mô hình tự hồi quy sinh như GPT.
• Kiến trúc phổ biến chuyển từ transformer hai chiều sang decoder-only nhân quả.
• Cách ứng dụng chuyển từ fine-tuning sang prompting và hội thoại; nhiều nhiệm vụ có thể thực hiện với ít ví dụ hoặc zero-shot.

## Trang 22/77

BA GIAI ĐOẠN CƠ BẢN XÂY DỰNG LLM
1. Pretraining: dùng dữ liệu thô khổng lồ như sách, web, code để học tri thức tổng quát; có thể mất nhiều tháng trong ví dụ lịch sử.
2. Instruction SFT: dùng các cặp chỉ dẫn–đáp án chất lượng để tăng khả năng tuân thủ yêu cầu; ví dụ có thể mất vài ngày.
3. Alignment: dùng dữ liệu so sánh sở thích và tối ưu chính sách để hướng đầu ra an toàn/hữu ích hơn; thời gian phụ thuộc hệ thống.
Sơ đồ gốc phân biệt dữ liệu, mô hình và mục tiêu của ba bước.

## Trang 23/77

QUY TRÌNH XÂY DỰNG MÔ HÌNH LỚN
Minh họa chi tiết ba giai đoạn: dữ liệu gốc → mô hình tiền huấn luyện → dữ liệu chỉ dẫn có nhãn → mô hình SFT → dữ liệu so sánh → mô hình đã căn chỉnh.
Mỗi giai đoạn hướng đến mục tiêu khác nhau: tri thức tổng quát, làm theo chỉ dẫn, rồi an toàn và phù hợp sở thích.

## Trang 24/77

KỸ THUẬT CHÍNH 1 — PRETRAINING
Ba yếu tố quyết định tiền huấn luyện: thuật toán, dữ liệu và năng lực tính toán.
Thiết kế cần đồng thời xét chất lượng/nguồn dữ liệu, mục tiêu học và phân bổ tài nguyên.

## Trang 25/77

KỸ THUẬT CHÍNH 2 — INSTRUCTION FINE-TUNING
Tinh chỉnh mô hình trên các dữ liệu chỉ dẫn chất lượng cao, mô tả nhiệm vụ mà mô hình cần thực hiện.
Giúp mô hình hiểu đặc điểm nhiệm vụ, cải thiện hiệu năng trên nhiều bài toán và làm đầu ra prompting ổn định/dễ điều khiển hơn.
Slide dùng bài toán suy luận ngôn ngữ tự nhiên (NLI) để so sánh fine-tuning thường với instruction tuning.

## Trang 26/77

HAI CÁCH TẠO DỮ LIỆU CHO INSTRUCTION TUNING
• Dùng bộ dữ liệu hiện có: thêm tiền tố/chỉ dẫn mô tả nhiệm vụ vào nhiều tập dữ liệu, sau đó huấn luyện chung; ví dụ FLAN.
• Tinh chỉnh từ ví dụ do con người viết: con người tạo câu trả lời chất lượng cho các prompt; ví dụ InstructGPT.
Khi xây dữ liệu cần cân nhắc số lượng nhiệm vụ và mức đa dạng, không chỉ tổng số mẫu.

## Trang 27/77

FLAN VÀ NĂNG LỰC ZERO-SHOT
FLAN dùng instruction tuning để cải thiện khả năng xử lý nhiệm vụ mà không cần ví dụ (zero-shot).
Theo bài báo được dẫn, 62 nhiệm vụ NLP được chia thành 12 nhóm; mỗi nhiệm vụ có khoảng 10 mẫu hướng dẫn riêng.
Bài giảng trình bày hiệu ứng phụ thuộc quy mô: trong kết quả nghiên cứu đó, lợi ích trên nhiệm vụ chưa từng thấy rõ hơn khi mô hình đạt quy mô hàng chục tỷ tham số.
Nguồn: Wei và cộng sự, “Finetuned Language Models Are Zero-Shot Learners” (ICLR 2021).

## Trang 28/77

KỸ THUẬT CHÍNH 3 — ALIGNMENT
Mô hình lớn có thể sinh câu trả lời vô ích, độc hại hoặc không đúng sự thật.
Alignment tìm cách hướng đầu ra đến ý định và kỳ vọng của con người thông qua dữ liệu có nhãn, phần thưởng và học tăng cường, đồng thời giảm rủi ro.
Slide có ví dụ đối thoại: một yêu cầu mang nguy cơ xâm nhập bị từ chối; khi người dùng làm rõ rằng muốn bảo vệ nhà mình, mô hình có thể cung cấp lời khuyên an toàn về phòng vệ.

## Trang 29/77

CĂN CHỈNH VỚI SỞ THÍCH, GIÁ TRỊ, Ý ĐỊNH VÀ AN TOÀN
Định nghĩa: điều hướng hành vi AI phù hợp lợi ích và mục tiêu được thiết kế.
Cần phân biệt căn chỉnh với giá trị văn hóa/pháp luật/đạo đức, và kiểm soát các hành vi có thể bị lạm dụng.
Slide dẫn các quy định tại Trung Quốc đối với công nghệ tổng hợp sâu và dịch vụ AI tạo sinh, đồng thời nhắc tới nguy cơ AI bị dùng cho tấn công mạng hoặc hướng dẫn phạm tội.

## Trang 30/77

BA NGUYÊN TẮC CĂN CHỈNH
• Hữu ích (helpful), trung thực (honest), không gây hại (harmless).
• Phù hợp với văn hóa, pháp luật, đạo đức, sự thật và logic.
Ví dụ từ InstructGPT: dữ liệu SFT ~13.000 mẫu, dữ liệu Reward Model ~33.000 cặp, dữ liệu RL ~31.000 mẫu (theo bài báo được trích).
Các thành phần: mô hình SFT, mô hình phần thưởng RM và mô hình tối ưu bằng RL.
Nguồn: Ouyang và cộng sự, “Training Language Models to Follow Instructions with Human Feedback” (2022).

## Trang 31/77

INSTRUCTGPT — BƯỚC 1: SUPERVISED FINE-TUNING
Thu các câu hỏi/chỉ dẫn từ người dùng hoặc API, có người gán nhãn tạo câu trả lời mục tiêu.
Tinh chỉnh mô hình GPT-3 nền để bắt chước các đáp án có chất lượng.
Ví dụ minh họa: “Mặt trăng là gì?” → mô tả một thiên thể hình cầu quay quanh Trái Đất.

## Trang 32/77

INSTRUCTGPT — BƯỚC 2: REWARD MODELING
Dùng mô hình SFT để sinh nhiều phản hồi cho cùng prompt, rồi người gán nhãn xếp hạng theo sở thích.
Ví dụ: nhiều câu trả lời “Mặt trăng là gì?”, xếp hạng D > C > A = B.
Mô hình phần thưởng RM, có thể nhỏ hơn policy model, học cách dự đoán điểm số tương đối cho từng cặp câu hỏi–phản hồi.

## Trang 33/77

REWARD MODELING — HỌC TỪ CÁC CẶP SO SÁNH
Từ mỗi prompt x, lấy cặp câu trả lời y_w (được ưu tiên) và y_l (kém ưu tiên). Huấn luyện reward model sao cho điểm của y_w cao hơn y_l.
Slide gốc minh họa điểm khác biệt reward và cách sắp xếp các câu trả lời.

## Trang 34/77

INSTRUCTGPT — BƯỚC 3: REINFORCEMENT LEARNING
Bắt đầu từ mô hình SFT, lấy câu trả lời của mô hình rồi chấm điểm qua RM.
Dùng PPO (Proximal Policy Optimization) hoặc phương án RL tương ứng để cập nhật policy, tăng phần thưởng kỳ vọng mà vẫn kiểm soát lệch so với bản gốc.
Slide sử dụng câu hỏi ví dụ “Chất siêu dẫn ở nhiệt độ phòng là gì?” để minh họa pipeline.

## Trang 35/77

INSTRUCTGPT — HÀM MỤC TIÊU RL
Tiếp tục sơ đồ SFT → RL policy → Reward Model → PPO.
Hình nguồn bổ sung phần mục tiêu/loss và thành phần điều chuẩn so với mô hình ngôn ngữ gốc.
Cần đọc công thức chính xác trực tiếp trên slide gốc; phần Việt này giữ ý nghĩa của bước RL trong pipeline căn chỉnh.

## Trang 36/77

ALIGNMENT — MINH HỌA TRỰC QUAN
Trang này chủ yếu chứa hình minh họa cho giai đoạn alignment và các tác động của nó; văn bản máy đọc được rất ít.
Hình nguồn được giữ nguyên đầy đủ ở phía trên.

## Trang 37/77

QUY LUẬT MỞ RỘNG QUY MÔ (SCALING LAWS)
Mối liên hệ giữa hiệu năng mô hình với kích thước tham số, lượng dữ liệu và chi phí tính toán.
Bài giảng nêu: tăng tham số và dữ liệu tiền huấn luyện thường cải thiện hiệu năng trong nhiều chế độ phù hợp.
Chinchilla từng khuyến nghị tỷ lệ xấp xỉ 20 token huấn luyện cho mỗi tham số, ví dụ mô hình 10B với 200B token.
Nguồn: Kaplan và cộng sự, “Scaling Laws for Neural Language Models”.

## Trang 38/77

NĂNG LỰC XUẤT HIỆN (EMERGENT ABILITIES)
Một số phép đo trên mô hình ngôn ngữ cho thấy khi tăng tham số đến một mức nhất định, hiệu quả của vài nhiệm vụ như suy luận có thể tăng mạnh.
Các khả năng ít quan sát được ở mô hình nhỏ có thể rõ hơn ở mô hình lớn.
Ví dụ được bài giảng nêu: in-context learning và chain-of-thought reasoning.
Nguồn: Wei và cộng sự (2022). Đây là chủ đề còn cần định nghĩa metric cẩn thận.

## Trang 39/77

ẢO GIÁC (HALLUCINATION) CỦA LLM
Định nghĩa: nội dung mô hình sinh không trung thành với nguồn (faithfulness) hoặc không đúng sự thật (factualness).
Khả năng sáng tạo và liên tưởng có lợi trong một số tác vụ, nhưng sai sự thật làm giảm độ tin cậy, có thể bị lợi dụng để tạo tin đồn và gây ô nhiễm thông tin trên mạng.
Ví dụ nguồn: mô hình phủ nhận rằng “Lu Xun” và “Zhou Shuren” là cùng một người dù đó là bút danh và tên thật của một nhà văn.
Nguồn: Huang và cộng sự, khảo sát Hallucination in Large Language Models (2023).

## Trang 40/77

BẢN ĐỒ NĂNG LỰC CỦA MÔ HÌNH LỚN
Hình gốc (dẫn khảo sát Minaee và cộng sự) cho thấy các nhóm năng lực và nhiệm vụ thường được đánh giá với LLM.
Bản dịch giữ hình để đối chiếu tên benchmark/nhánh chức năng; không có văn bản chi tiết máy đọc được trên trang này.

## Trang 41/77

LỊCH SỬ TỪ GPT-3 TỚI CHATGPT
• GPT-1: pretraining tự hồi quy một chiều + fine-tuning giám sát.
• GPT-2: nhiều dữ liệu, mô hình lớn hơn; khám phá khả năng nhiều nhiệm vụ dựa trên prompt.
• GPT-3: mô hình hàng trăm tỷ tham số, nổi bật với in-context learning.
• GPT-3.5/ChatGPT: instruction tuning, phản hồi con người và tối ưu hội thoại.
• GPT-4: hướng đa phương thức, xử lý ngữ cảnh dài hơn, ứng dụng đa dạng; một số cải tiến về chất lượng/hiệu quả được bài giảng mô tả.

## Trang 42/77

GPT-4 VÀ KỸ THUẬT THIẾT KẾ PROMPT
Theo báo cáo kỹ thuật GPT-4, mô hình đạt kết quả tương đương người ở một số bài kiểm tra học thuật/chuyên môn; ví dụ nằm trong khoảng 10% điểm cao nhất ở kỳ thi luật sư mô phỏng. Bài giảng cũng nêu năng lực đa phương thức và cải thiện một số hạn chế về ảo giác/an toàn.
Sáu gợi ý từ hướng dẫn prompt của OpenAI: viết chỉ dẫn rõ ràng; cung cấp văn bản tham chiếu; chia nhiệm vụ phức tạp thành nhiệm vụ nhỏ; cho mô hình thời gian suy luận; dùng công cụ bên ngoài; thử nghiệm thay đổi một cách hệ thống.
Nguồn: GPT-4 Technical Report và hướng dẫn Prompt Engineering của OpenAI.

## Trang 43/77

HỌ MÔ HÌNH LLAMA: CÁC PHIÊN BẢN
Llama là họ mô hình tự hồi quy dựa trên Transformer, được bài giảng so sánh từ 7B đến 405B tham số. Các thế hệ gồm Llama 1, Llama 2, Llama 3, 3.1 và 3.2.
Bảng gốc đối chiếu quy mô mô hình, dữ liệu (1,4T; 2T; 15T; 15T; 9T), khả năng đa phương thức/đa ngôn ngữ, dùng công cụ, cách hậu huấn luyện (SFT, RLHF, DPO) và cửa sổ ngữ cảnh (2K, 4K, 8K, 131K).
Lưu ý: những nhận định về giấy phép thương mại ở slide là thông tin lịch sử theo tác giả; khi sử dụng thực tế cần xem điều khoản của từng phiên bản.

## Trang 44/77

LLAMA: NGUỒN DỮ LIỆU VÀ ĐỐI CHIẾU HIỆU NĂNG
Nguồn dữ liệu huấn luyện mà slide liệt kê: CommonCrawl, C4, GitHub, Wikipedia, sách, arXiv và StackExchange.
Mã nguồn/thông tin dự án: https://github.com/facebookresearch/llama
Bài giảng báo cáo Llama 3.1 405B vượt GPT-3.5 Turbo trên nhiều phép đo và đạt điểm cao hơn GPT-4 0125 trên phần lớn benchmark được trích trong tài liệu.
Đây là số liệu từ tài liệu tại thời điểm biên soạn, không phải phép đánh giá hiện tại. Nguồn: Dubey và cộng sự, The Llama 3 Herd of Models.

## Trang 45/77

PHÂN LOẠI MÔ HÌNH AI LỚN PHÁT TRIỂN TẠI TRUNG QUỐC
Theo báo cáo đánh giá Chinese Large Model Benchmark năm 2024 được slide dẫn, tính đến cuối tháng 4/2024 đã công bố 305 mô hình lớn tại Trung Quốc (thống kê chưa đầy đủ).
Slide minh họa các nhóm mô hình tiêu biểu; con số là một mốc lịch sử, không phải thống kê đến năm hiện tại.

## Trang 46/77

HỌ MÔ HÌNH QWEN
Tongyi Qianwen (Qwen) là họ mô hình tiền huấn luyện do Alibaba Cloud phát triển, phục vụ hiểu, sinh và giải thích nội dung ngôn ngữ, hình ảnh và tài liệu.
Các tác vụ minh họa: viết nội dung sáng tạo, trợ lý văn phòng, trợ lý học tập và tương tác thường ngày. Bài giảng nêu khả năng hiểu tiếng Trung/Anh, giải toán và xử lý mã nguồn.
Slide cũng giới thiệu Qwen-Audio và Qwen-Audio-Chat.
Nguồn: Bai và cộng sự, Qwen Technical Report; Yang và cộng sự, Qwen2 Technical Report.

## Trang 47/77

TIẾN HÓA QWEN 1.5 → QWEN 2 → QWEN 2.5
Qwen1.5: mở rộng model scaling sang mô hình lớn/nhỏ, có biến thể MoE và định dạng lượng tử AWQ/GGUF. Qwen2: tăng cường nhiều ngôn ngữ và xử lý văn bản dài. Qwen2.5: tăng năng lực toán, lập trình và đa ngôn ngữ.
Các kích thước ví dụ trên slide: Qwen từ 1,8B đến 72B; Qwen2.5 gồm 0,5B, 1,5B, 3B, 7B, 14B, 32B và 72B.
Hướng cải tiến: kiến trúc MoE, tăng lượng/chất dữ liệu, mở rộng nhiệm vụ hậu huấn luyện, cửa sổ ngữ cảnh, ngôn ngữ, năng lực chuyên biệt và modality (Qwen-VL, Qwen-Audio).

## Trang 48/77

DEEPSEEK LLM ĐỜI ĐẦU (11/2023)
Dòng DeepSeek LLM được slide mô tả với khoảng 67B–70B tham số, kiến trúc Transformer dense (mọi tham số của lớp thường được dùng trong forward), huấn luyện trên khoảng 2 nghìn tỷ token tiếng Trung/Anh.
Quy trình được nêu: pretraining → supervised fine-tuning (SFT) → direct preference optimization (DPO).
Tác giả so sánh phiên bản DeepSeek 67B Base với Llama 2 70B Base và báo cáo ưu thế trên một số bài toán reasoning và coding. Đây là kết quả theo bài giảng gốc.

## Trang 49/77

DEEPSEEK LLM VÀ DEEPSEEK-V2 (05/2024)
DeepSeek LLM đời đầu: mô hình dense cỡ 67B, dữ liệu 2T token, các giai đoạn tiền huấn luyện/SFT/DPO.
DeepSeek-V2: tổng khoảng 236B tham số nhưng chỉ 21B tham số kích hoạt mỗi lượt; dùng DeepSeekMoE (Mixture-of-Experts) và Multi-head Latent Attention (MLA). Theo bài giảng, huấn luyện trên khoảng 8,1T token, với pretraining, SFT và tăng cường bằng RL.
Các tuyên bố ở slide: tiết kiệm KV cache hơn 90%, tăng tốc suy luận hơn 5 lần và giảm chi phí huấn luyện/suy luận so với một số cấu hình đối chiếu. Đây không phải phép đo độc lập của bản dịch.

## Trang 50/77

DEEPSEEK-V2 VÀ V2.5
V2: 236B tham số tổng, khoảng 21B tham số hoạt hóa, MoE + MLA, dữ liệu khoảng 8,1T token.
V2.5 (09/2024) được mô tả là tối ưu tiếp từ V2, đặc biệt các nhiệm vụ tổng quát và năng lực lập trình.
Slide nhấn mạnh việc dùng sparse activation để tăng quy mô tham số mà không làm chi phí mỗi lượt suy luận tăng cùng tỷ lệ như kiến trúc dense.

## Trang 51/77

DEEPSEEK-V2.5 VÀ DEEPSEEK-V3 (12/2024)
DeepSeek-V2.5 cải thiện tác vụ tổng quát và mã nguồn.
DeepSeek-V3: khoảng 671B tham số tổng, 37B tham số kích hoạt, dữ liệu tiền huấn luyện khoảng 14,8T token. Kiến trúc dựa trên V2, bổ sung cân bằng expert không cần auxiliary loss, huấn luyện dự đoán nhiều token (Multi-Token Prediction) và số học hỗn hợp FP8.
Slide mô tả quy trình pretraining + SFT + DPO và các so sánh thuận lợi về chất lượng/chi phí với Llama 3, Qwen2.5 tại thời điểm đó. Cần đối chiếu benchmark và điều kiện nếu sử dụng số liệu.

## Trang 52/77

DEEPSEEK-V3 VÀ DEEPSEEK-R1 (01/2025)
V3 được giới thiệu với 671B tham số tổng, khoảng 37B kích hoạt, 14,8T token, Mixture-of-Experts và Multi-Token Prediction.
DeepSeek-R1 dùng DeepSeek-V3-Base làm backbone; bài giảng nêu quy trình nhiều giai đoạn với cold start và reinforcement learning để phát triển năng lực suy luận.
Slide so sánh kết quả suy luận của R1 với lớp mô hình o1/GPT-4; đó là đánh giá trong tài liệu nguồn, không phải kết luận độc lập hay cập nhật hiện tại.

## Trang 53/77

CÁC CÁCH TRIỂN KHAI MÔ HÌNH LỚN
Hai nhóm mô hình ví dụ: mô hình ngôn ngữ như Qwen và mô hình đa phương thức như MiniCPM.
Hai phương thức sử dụng chính:
• Gọi dịch vụ từ xa qua giao diện lập trình (API).
• Triển khai cục bộ (local deployment), nạp mô hình trên máy do người dùng quản lý.
Mỗi lựa chọn có yêu cầu khác nhau về kết nối, phần cứng, dữ liệu và vận hành.

## Trang 54/77

TRIỂN KHAI MÔ HÌNH LỚN: VÍ DỤ CHỨC NĂNG
Slide giới thiệu các ví dụ giao diện/chức năng của mô hình lớn qua hình ảnh.
Các mô hình có thể dùng để hỏi đáp, sinh nội dung và hỗ trợ công việc tùy loại dịch vụ. Hình gốc được giữ ở phần trên để tham khảo; trang không có nhiều chữ máy trích xuất được.

## Trang 55/77

TRIỂN KHAI QUA API: NHÀ CUNG CẤP
Các dịch vụ minh họa trong slide: Qwen/DashScope (Alibaba), DeepSeek, Llama (Meta), Zhipu AI, OpenAI và các nhà cung cấp khác như ERNIE/Baichuan.
Quy trình cơ bản: đăng ký dịch vụ, lấy khóa API (API key), xác định quota/hạn mức và sử dụng khóa khi gửi yêu cầu đến endpoint.
Nguồn liên kết của từng dịch vụ nằm trong slide gốc. Điều kiện sử dụng, giá và giới hạn truy cập có thể thay đổi theo thời gian.

## Trang 56/77

GỌI MÔ HÌNH THÔNG QUA GIAO DIỆN ĐỒ HỌA
Có thể dùng giao diện GUI hoặc không gian demo web để nhanh chóng thử một trường hợp trước khi viết mã.
Hai trang được tài liệu giới thiệu: trung tâm hướng dẫn Qwen trên DashScope và Hugging Face Space cho Qwen2-72B-Instruct.
Đây là hình thức thích hợp cho thử nghiệm tương tác; cần lưu ý mô hình/phiên bản thực tế có thể khác tài liệu.

## Trang 57/77

GỌI MÔ HÌNH BẰNG MÃ NGUỒN
Slide chuyển sang phương pháp sử dụng API từ mã, thay vì chỉ giao diện đồ họa.
Công cụ môi trường tùy chọn: VS Code để soạn/chạy mã và Miniconda để quản lý Python, phụ thuộc phiên bản dự án.
Khi thực hành, cần đọc tài liệu SDK và bảo mật khóa API; lệnh cụ thể xem trang gốc.

## Trang 58/77

CÁC NỀN TẢNG TRIỂN KHAI CỤC BỘ
• Ollama, LM Studio: công cụ nạp và chạy mô hình cục bộ.
• OpenAI/DashScope API: ví dụ của kiểu gọi dịch vụ web/API.
• Flask hoặc MindIE: công cụ có thể dùng để cung cấp dịch vụ nội bộ theo kiến trúc người triển khai.
Trang chủ tham khảo: https://ollama.com và https://lmstudio.ai/
Chú ý phải cân đối cấu hình máy, dung lượng model và phương án truy cập.

## Trang 59/77

YÊU CẦU PHẦN CỨNG CHO TRIỂN KHAI CỤC BỘ
Hai nguồn lực được bài giảng nhấn mạnh:
• Bộ nhớ đồ họa (GPU VRAM) cần để nạp trọng số và vùng nhớ phục vụ suy luận.
• Dung lượng ổ cứng để lưu tệp model/checkpoint và dữ liệu liên quan.
Các cấu hình chính xác phụ thuộc kích thước tham số, độ chính xác số học, lượng tử hóa và độ dài ngữ cảnh. Slide minh họa bảng nhu cầu phần cứng tương ứng.

## Trang 60/77

CÀI ĐẶT VÀ CHẠY OLLAMA
1. Truy cập website chính thức của Ollama.
2. Chọn tệp cài đặt phù hợp macOS, Linux hoặc Windows.
3. Tải và thực hiện bộ cài theo hệ điều hành.
4. Chạy mô hình cụ thể bằng lệnh minh họa từ bài giảng: `ollama run qwen2:7b`.
Lưu ý: tên model/tag và dung lượng tải cần được xác minh khi thực hành vì danh mục có thể thay đổi.

## Trang 61/77

SỬ DỤNG OLLAMA: VÍ DỤ LỆNH
Hai bước chính được nhắc lại trong slide:
1. Cài Ollama phù hợp hệ điều hành.
2. Chạy một mô hình cụ thể, ví dụ `ollama run qwen2:7b`.
Hình gốc cho thấy thao tác hoặc kết quả trên terminal; khi đọc cần phân biệt công cụ chạy và trọng số mô hình.

## Trang 62/77

MỞ RỘNG GIAO DIỆN VÀ KHO TRI THỨC CỤC BỘ
Sau khi cài Ollama và chạy ví dụ `ollama run qwen2:7b`, có thể mở rộng:
1. Dùng Open WebUI để tạo giao diện web.
2. Dùng AnythingLLM để xây dựng kho tài liệu/kiến thức cục bộ cho truy xuất.
Đây là các phương án nâng cao do slide nêu, không phải điều kiện để hoàn thành bài học cơ bản.

## Trang 63/77

MỤC LỤC
1. Tổng quan mô hình lớn: quá trình phát triển và các khái niệm.
2. Mô hình tiền huấn luyện: các dạng encoder, decoder, encoder–decoder và kiến trúc.
3. Mô hình ngôn ngữ quy mô lớn: thay đổi phương thức xây dựng, đại diện tiêu biểu, kỹ thuật cốt lõi và cách triển khai.
4. Mở rộng khái niệm: mô hình theo lĩnh vực, nền tảng đa phương thức và nền tảng tác nhân.

## Trang 64/77

MỞ RỘNG KHÁI NIỆM MÔ HÌNH LỚN
Ba hướng được biểu diễn trong sơ đồ:
• Mô hình ngành dọc: người dùng ↔ mô hình lớn có tăng cường dữ liệu theo lĩnh vực.
• Mô hình đa phương thức: người dùng ↔ mô hình lớn tiếp nhận thông tin nhiều modality.
• Tác nhân mô hình lớn: người dùng ↔ agent có thể tương tác với môi trường.
Hình giữ lại các mũi tên luồng thông tin giữa người dùng, mô hình, dữ liệu và môi trường.

## Trang 65/77

MÔ HÌNH LỚN CHUYÊN NGÀNH (VERTICAL/DOMAIN LLM)
Phương án phổ biến: bắt đầu từ mô hình lớn tổng quát, tiếp tục huấn luyện hoặc thích nghi với dữ liệu chuyên ngành.
Ưu điểm tiềm năng được bài giảng nêu: chuyên môn hóa, triển khai nhanh hơn, hiệu quả chi phí và mức tuân thủ theo lĩnh vực.
Các cách thực hiện: tiếp tục pretraining, fine-tuning, prompt tuning và retrieval augmentation.
Lĩnh vực ví dụ: giáo dục, y tế, pháp luật, tài chính.
Nguồn: Ling và cộng sự, Domain Specialization...

## Trang 66/77

XU HƯỚNG PHÁT TRIỂN MÔ HÌNH ĐA PHƯƠNG THỨC
Bài giảng mô tả những tiến bộ về khả năng đa phương thức như một xu hướng quan trọng, mở rộng loại nhiệm vụ và phạm vi ứng dụng của mô hình lớn.
Nguồn tham khảo: A Survey on Multimodal Large Language Models (https://arxiv.org/pdf/2306.13549).
Những đánh giá về “đột phá” là nhận định của tác giả tại thời điểm biên soạn.

## Trang 67/77

VÍ DỤ NĂNG LỰC CỦA MÔ HÌNH ĐA PHƯƠNG THỨC
Hình gốc đưa ra minh họa về những đầu vào/đầu ra có thể kết hợp văn bản, hình ảnh, âm thanh và video.
Trang chủ yếu là hình; phần tiếng Việt giải thích ý nghĩa khái quát của hình, không thay thế nhãn chữ nằm trực tiếp trong biểu đồ.

## Trang 68/77

CÁC MỐC PHÁT TRIỂN MÔ HÌNH ĐA PHƯƠNG THỨC
Mục tiêu kỹ thuật: học từ dữ liệu lớn và phản hồi của con người, đối thoại với người dùng, xử lý dữ liệu nhiều modality, tăng khả năng suy luận và vận dụng tri thức phổ thông.
Thành phần chính: kiến trúc đa phương thức, instruction following, suy luận đa phương thức, tối ưu triển khai gọn nhẹ và căn chỉnh modality.
Các mốc lịch sử: GPT-4 (03/2023), DALL·E 3 (09/2023), tích hợp đa phương thức ChatGPT (09/2023), Gemini (12/2023), Claude 3 (03/2024), GPT-4o (05/2024).
Nguồn: Fei và cộng sự, ACM MM 2024.

## Trang 69/77

KHUNG XỬ LÝ CHUNG CỦA MÔ HÌNH ĐA PHƯƠNG THỨC
Luồng xử lý thường gặp: mã hóa đầu vào theo modality → hợp nhất đặc trưng (feature fusion) → decoder đa phương thức để sinh kết quả.
Modalities phổ biến: văn bản, hình ảnh, video, lời nói/âm thanh.
Hệ thống có thể hỗ trợ cả đầu vào và đầu ra đa phương thức, tùy cấu trúc cụ thể.
Nguồn: Zhang và cộng sự, MM-LLMs: Recent Advances in Multimodal Large Language Models.

## Trang 70/77

HAI KIẾN TRÚC TIÊU BIỂU CỦA MLLM
1. Kiểu LLM làm trung tâm điều phối: nhận lệnh, phân công xuống các mô-đun; ví dụ Visual-ChatGPT, HuggingGPT, MM-REACT và LLaVA-Plus.
2. Kiểu đa phương thức tích hợp: đầu vào văn bản/đa phương thức đi qua các encoder, LLM xử lý, đầu ra gửi tới decoder phù hợp.
Biểu đồ gốc phân biệt các luồng “người dùng → LLM → downstream module” và “multimodal encoder → LLM → multimodal decoder”.

## Trang 71/77

TÀI NGUYÊN HỌC MLLM
Bài giảng giới thiệu tài liệu hướng dẫn từ CVPR, ACM Multimedia và COLING, kèm slide và video.
Trang tham khảo: https://mllm2024.github.io/CVPR2024
Các nguồn này giúp đọc thêm về kiến trúc, xử lý modality, instruction tuning và đánh giá đa phương thức.

## Trang 72/77

ỨNG DỤNG CỦA TÁC NHÂN DỰA TRÊN MÔ HÌNH LỚN
Các sản phẩm/tác nhân được slide nêu làm ví dụ về tiềm năng tự động hóa hành động và xử lý nhiệm vụ trên môi trường số: OpenAI Operator, Anthropic Claude và Manus AI.
Liên kết nguồn: openai.com/index/introducing-operator; anthropic.com/claude; manus.im.
Những khả năng và tính sẵn có cần được hiểu theo thời điểm slide được biên soạn.

## Trang 73/77

KHÁI NIỆM AGENT DỰA TRÊN LLM
Agent là hệ thống có thể sử dụng mô hình lớn để định hướng quy trình và công cụ, điều chỉnh hoạt động theo phản hồi môi trường.
Ba khối trong sơ đồ: người dùng, tác nhân và môi trường.
Đặc điểm được mô tả: nhận biết tình huống, lập kế hoạch/ra quyết định, thực hiện hành động, duy trì trạng thái, tự xem xét/cải tiến và bảo vệ an toàn.
Tài nguyên có thể truy xuất: kho tri thức, kinh nghiệm, ứng dụng (APP), API và hàm công cụ.
Nguồn: Anthropic, Building Effective Agents (19/12/2024).

## Trang 74/77

WORKFLOW VÀ AGENT: HAI CÁCH ĐIỀU PHỐI
• Workflow: ghép LLM với công cụ theo một lộ trình định sẵn; gần với script tự động hóa phức tạp, thường do prompt/cấu hình điều khiển.
• Agent: mô hình có nhiều tự chủ hơn trong lựa chọn công cụ, lên kế hoạch và cập nhật đường đi để đạt mục tiêu; có thể học hoặc phát triển năng lực theo thiết kế hệ thống.
Sơ đồ đối chiếu “AI như thành phần có thể điều phối” với “AI có quyền tự định hướng hành động lớn hơn”.

## Trang 75/77

CÁC MỨC HỆ THỐNG AI ĐƯỢC BÀI GIẢNG MINH HỌA
L1 Chatbots (ví dụ GPT-4, DeepSeek-V3): giao tiếp ngôn ngữ, hỏi đáp, hội thoại, tìm kiếm.
L2 Reasoners (ví dụ o1, DeepSeek-R1): suy luận nhiều bước, toán và logic.
L3 Agents (ví dụ Operator, Deep Research): gọi công cụ, thực hiện hành động, khám phá môi trường.
L4 Innovators: đổi mới và phát minh.
L5 Organizations: tổ chức và quản lý.
Đây là khung phân tầng khái niệm do slide trình bày, không phải một thang đo chuẩn hóa được thẩm định độc lập.

## Trang 76/77

TÀI LIỆU HỌC MỞ RỘNG
Tài liệu “Quy trình phát triển mô hình lớn từ đầu đến cuối” (theo trang nguồn) được bài giảng giới thiệu qua hệ sinh thái Ascend.
Thông tin ở slide: 54 bài học và 26 tài liệu thực hành.
Trang tham khảo: https://www.hiascend.com/edu/growth/lm-development

## Trang 77/77

CẢM ƠN!
Kết thúc bài giảng “Công nghệ và sự phát triển mô hình lớn”.
Liên hệ tác giả: zhangzs@sjtu.edu.cn
Website: https://bcmi.sjtu.edu.cn/~zhangzs

