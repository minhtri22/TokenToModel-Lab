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



---

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
CoT yêu cầu mô hình trình bày các bước trung gian, thay vì chỉ “câu hỏi → đáp án”. Bài giảng nêu lợi ích trên bài toán toán, logic và nhiệm vụ nhiều bước.
Sơ đồ so sánh:
• Trả lời trực tiếp cho ví dụ hoa hướng dương có 3 tá hạt nhỏ và bông lớn có nhiều hạt hơn 50% → có thể cho sai “54”.
• Trả lời theo các bước: 3 tá = 36, bông lớn = 36+18 = 54, cả hai = 36+54 = **90 hạt**.
Ngữ cảnh trình bày giúp người học kiểm tra cách đến đáp án.

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

KỸ THUẬT NỀN CHO CoT 1: PROMPT LEARNING
Thiết kế prompt làm rõ cấu trúc suy luận mong muốn: chuỗi, cây, đồ thị hoặc self-consistency; chia bài toán thành bước nhỏ.
Nên mô tả tỉ mỉ tình huống, vai trò, luật, định dạng đầu ra và cách đánh giá.
Ví dụ trên slide từ OS-Copilot yêu cầu mô hình lập trình sinh hàm Python và câu lệnh gọi hàm; tên hàm trùng nhiệm vụ, tham số không được hard-code, có quy tắc xử lý đường dẫn tệp và import.
Các ví dụ giải có thể viết tay, truy xuất hoặc sinh tự động.

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



---

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



---

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

TRÍCH XUẤT ĐÁP ÁN TOÁN
• GSM8K thường đánh dấu đáp án bằng bốn ký tự 0000 (####).
• MATH thường đặt đáp án trong lệnh LaTeX \boxed{}, hiện được dùng rộng rãi.
Ưu điểm: có chuẩn thống nhất để bóc tách và đánh giá kết quả.
Hạn chế:
• Mô hình cần được hướng dẫn/huấn luyện theo định dạng đầu ra.
• Không bao phủ mọi kiểu trả lời.
Hình trên slide đối chiếu quy ước GSM8K và MATH.

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



---

# Chương 05 — Thủy vân mô hình ngôn ngữ

Nguồn gốc: `documents/chapter5/watermark.pdf` · commit `f84c04268794ef94f8949808bbc14ab8636763a0`.

**Nội dung dưới đây là phần chuyển ngữ/diễn giải tiếng Việt theo từng trang slide**, phục vụ đối chiếu với bản gốc; không bảo đảm từng câu chữ trong hình được thay thế.

## Trang 1/48

THỦY VÂN CHO MÔ HÌNH NGÔN NGỮ LỚN (WATERMARK FOR LLMs)
Tác giả: Zhiwei He, Trường Điện tử, Thông tin và Kỹ thuật Điện, Đại học Giao thông Thượng Hải.
Ngày 14 tháng 4 năm 2024.
Các mục chính: động lực, phương pháp thủy vân, khả năng tồn tại sau dịch và hạn chế.

## Trang 2/48

MỤC LỤC
1. Động lực (Motivation).
2. Phương pháp thủy vân (Watermarking Method): giới thiệu, KGW (ICML 2023 — bài xuất sắc), SIR (ICLR 2024).
3. Thủy vân có tồn tại sau khi dịch không? (Can Watermarks Survive Translation?): giới thiệu, đánh giá, tấn công và phòng vệ.
4. Giới hạn của phương pháp.

## Trang 3/48

ĐỘNG LỰC NGHIÊN CỨU
LLM đã cho thấy khả năng sinh nội dung ấn tượng.
Giảm việc lạm dụng LLM là một yêu cầu quan trọng. Việc gắn dấu và xác định nội dung do LLM sinh có thể hỗ trợ truy vết nguồn gốc hoặc đánh giá rủi ro sử dụng sai.
Đây là động lực nghiên cứu thủy vân, không phải cam kết rằng mọi dấu thủy vân đều đáng tin cậy.

## Trang 4/48

MỤC LỤC — PHẦN PHƯƠNG PHÁP
1. Động lực.
2. Phương pháp thủy vân: giới thiệu, KGW, SIR.
3. Thủy vân sau dịch: giới thiệu, đánh giá, tấn công, phòng vệ.
Bắt đầu phần giới thiệu phương pháp.

## Trang 5/48

GIỚI THIỆU THỦY VÂN VĂN BẢN
Thủy vân văn bản (text watermarking) nhúng một “thông điệp” hoặc tín hiệu nhận dạng vào nội dung do mô hình ngôn ngữ sinh.
Mục tiêu là hỗ trợ việc nhận biết nguồn gốc nội dung.

## Trang 6/48

THỦY VÂN KHÔNG DỄ NHẬN BIẾT BẰNG MẮT
Thông điệp được nhúng trong văn bản do LLM sinh có hai tính chất mong muốn:
• Người đọc thông thường không nhìn thấy một dấu hiệu rõ ràng.
• Thuật toán phát hiện chuyên dụng có thể xác định tín hiệu thống kê.

## Trang 7/48

THỦY VÂN NHƯ MỘT BIT TRẠNG THÁI
Ở dạng đơn giản nhất, thông điệp nhúng chỉ cần là một bit biểu thị có hoặc không có thủy vân.
Thuật toán phải xác định được bit này dựa trên mẫu token trong văn bản, chứ không phải một chuỗi ký tự hiển nhiên.

## Trang 8/48

MỤC LỤC — THUẬT TOÁN KGW
Phương pháp thủy vân:
• KGW, ICML 2023 (Outstanding Paper).
• SIR, ICLR 2024.
Sau đó: tính bền vững khi chuyển đổi ngôn ngữ.

## Trang 9/48

KÝ HIỆU TOÁN HỌC
M: mô hình ngôn ngữ; V: bộ từ vựng (vocabulary).
x₁:ₙ = (x₁, x₂, …, xₙ): chuỗi n token.
P_M(xₙ₊₁ | x₁:ₙ): xác suất có điều kiện của token tiếp theo.
zₙ₊₁ = M(x₁:ₙ) ∈ ℝ^|V|: vector logits cho token tiếp.
Xác suất token được tính bằng softmax: P_M(xₙ₊₁ | x₁:ₙ) = softmax(zₙ₊₁).
Các ký hiệu và chỉ số cụ thể được giữ nguyên trong công thức trên slide gốc.

## Trang 10/48

KGW (ICML 2023 — OUTSTANDING PAPER)
Phần tiếp theo trình bày thuật toán thủy vân KGW, một phương pháp điều chỉnh xác suất sinh token dựa trên việc phân chia từ vựng thành các nhóm.

## Trang 11/48

Ý TƯỞNG CỐT LÕI CỦA KGW
Phân chia từ vựng dựa vào nội dung phía trước.
• Tại mỗi bước sinh, chia ngẫu nhiên V thành hai tập không giao nhau: danh sách xanh V_g và danh sách đỏ V_r.
• Seed của quá trình chia được tính từ hàm băm (hash) của văn bản tiền tố.
• Tăng xác suất chọn các token trong danh sách xanh.
Mục tiêu: văn bản sinh có thiên lệch thống kê có thể kiểm tra bằng cùng quy tắc chia.

## Trang 12/48

CÁCH NHÚNG THỦY VÂN KGW — TỪNG BƯỚC
1. Tính hash hₙ₊₁ = H(x₁:ₙ), có thể chỉ dựa vào k token cuối của tiền tố.
2. Dùng hash làm seed cho bộ tạo số giả ngẫu nhiên rồi chia V thành danh sách xanh V_g và danh sách đỏ V_r.
3. Điều chỉnh logits: với token thuộc V_g, cộng một độ lệch δ > 0; token thuộc V_r thì giữ nguyên.
Công thức trên slide mô tả z̃ᵢ = zᵢ + δ nếu vᵢ ∈ V_g, và z̃ᵢ = zᵢ nếu vᵢ ∈ V_r.

## Trang 13/48

HIỆU ỨNG THỐNG KÊ CỦA KGW
Sau khi điều chỉnh logits, văn bản có thủy vân sẽ chứa nhiều token “xanh” hơn về mặt thống kê.
Theo lập luận của phương pháp, thuộc tính này ít có khả năng xuất hiện tự nhiên trong văn bản không dùng quá trình nhúng như vậy. Do đó nó tạo tín hiệu để phát hiện thủy vân.

## Trang 14/48

PHÁT HIỆN THỦY VÂN KGW
Khi kiểm tra một văn bản, lặp lại quá trình hash và chia từ vựng như khi sinh, sau đó đếm số token xanh trong văn bản.
Điểm z (z-score) đo độ lớn của phần chênh lệch so với kỳ vọng ngẫu nhiên; công thức gốc có dạng (số token xanh − tỷ lệ xanh kỳ vọng) / độ lệch chuẩn.
Ký hiệu |x|_g: số token xanh, γ = |V_g|/|V|: tỷ lệ token xanh trong từ vựng.
So sánh điểm s với một ngưỡng thích hợp để quyết định có dấu thủy vân hay không. Công thức đầy đủ giữ trên slide nguồn.

## Trang 15/48

HIỆU NĂNG PHÁT HIỆN THỦY VÂN
Slide đưa ra các đường ROC (Receiver Operating Characteristic) với AUC = 0,998 cho điều kiện thí nghiệm được tác giả trình bày.
ROC biểu diễn đánh đổi giữa tỷ lệ phát hiện đúng và tỷ lệ báo nhầm theo ngưỡng. AUC cao trong một bộ thử không bảo đảm độ bền trước mọi hình thức chỉnh sửa văn bản.

## Trang 16/48

CHẤT LƯỢNG VĂN BẢN SAU KHI NHÚNG
KGW cộng độ lệch δ vào logits của token xanh, để token xanh dễ được chọn hơn; token đỏ giữ nguyên điểm.
Cần quan sát xem ràng buộc chọn token này có làm giảm tính tự nhiên, độ trôi chảy hay mức phù hợp nội dung của văn bản không. Công thức điều chỉnh logits được giữ trên slide.

## Trang 17/48

MỤC LỤC — CHUYỂN SANG SIR
• Động lực.
• Phương pháp thủy vân: KGW → SIR.
• Khả năng tồn tại sau dịch: đánh giá, tấn công và phòng vệ.

## Trang 18/48

SIR (ICLR 2024)
Phần này giới thiệu Semantic Invariant Robust Watermark, phương pháp thủy vân có mục đích giữ được khả năng phát hiện qua những thay đổi cách diễn đạt nhưng không đổi ý nghĩa.

## Trang 19/48

SIR: CẢI THIỆN ĐỘ BỀN KHI VIẾT LẠI
Độ bền (robustness) nghĩa là vẫn phát hiện được dấu thủy vân sau khi văn bản bị sửa.
Semantic Invariant Robust Watermark (SIR) được thiết kế để tăng khả năng chịu các phép tấn công viết lại văn bản (text rewriting), chẳng hạn paraphrase hoặc dịch qua ngôn ngữ khác rồi dịch ngược, trong khi giữ nguyên ý nghĩa.

## Trang 20/48

NHÌN TỔNG QUÁT VIỆC ĐIỀU CHỈNH LOGITS
KGW tăng δ cho token xanh và giữ nguyên token đỏ. Có thể coi bước này là cộng một hàm điều chỉnh vector Δ theo văn bản tiền tố:
    z̃ₙ₊₁ = zₙ₊₁ + Δ(x₁:ₙ), với Δ ∈ ℝ^|V|.
Biểu diễn bằng hàm Δ cho phép thiết kế quy tắc điều chỉnh token dựa trên ngữ nghĩa thay vì chỉ dựa vào hash đơn thuần.

## Trang 21/48

SIR: HÀM ĐIỀU CHỈNH PHẢN ÁNH ĐỘ TƯƠNG ĐỒNG NGỮ NGHĨA
Ý tưởng: độ tương đồng giữa hai vector điều chỉnh Δ(x) và Δ(y) nên gần với độ tương đồng giữa embedding của hai văn bản E(x), E(y).
Hàm mục tiêu: L = |Sim(E(x), E(y)) − Sim(Δ(x), Δ(y))|.
Các phần tử Δᵢ cũng được huấn luyện gần +1 hoặc −1. Có thể xem SIR là mở rộng của KGW: Δᵢ > 0 biểu thị token xanh; thông tin ngữ nghĩa giúp phân chia ổn định hơn khi viết lại.

## Trang 22/48

HIỆU NĂNG SIR TRONG PHIÊN BẢN TRIỂN KHAI CỦA TÁC GIẢ
Slide trình bày kết quả đo hiệu năng SIR (our implementation). Các biểu đồ/bảng số ở hình nguồn được giữ nguyên để đối chiếu.
Cần xem đồng thời khả năng phát hiện và chất lượng văn bản, không chỉ một điểm đo đơn lẻ.

## Trang 23/48

MỤC LỤC — THỦY VÂN SAU DỊCH
Câu hỏi: một văn bản có thủy vân được dịch sang ngôn ngữ khác thì dấu thủy vân có còn phát hiện được không?
Các phần: giới thiệu vấn đề; đánh giá; phương pháp tấn công; phương pháp phòng vệ.

## Trang 24/48

THỦY VÂN CÓ TỒN TẠI SAU KHI DỊCH?
Nhiều nghiên cứu về độ bền thủy vân trước đây tập trung vào tiếng Anh. Trong thực tế, thế giới dùng nhiều ngôn ngữ.
Khi dịch văn bản đã nhúng thủy vân sang một ngôn ngữ khác, các token thay đổi. Câu hỏi nghiên cứu: tín hiệu thống kê của thủy vân có giữ được khi đổi ngôn ngữ không?

## Trang 25/48

MỤC LỤC — ĐÁNH GIÁ TÍNH NHẤT QUÁN XUYÊN NGÔN NGỮ
• Vấn đề: dấu thủy vân thay đổi thế nào sau dịch?
• Đánh giá theo hai chỉ số: tương quan Pearson và sai số tương đối.
• Các kỹ thuật tấn công và phòng vệ.

## Trang 26/48

ĐÁNH GIÁ TÍNH NHẤT QUÁN XUYÊN NGÔN NGỮ
Định nghĩa cross-lingual consistency: khả năng thủy vân tiếp tục hoạt động hiệu quả sau khi văn bản được dịch.
Cho S là cường độ thủy vân ban đầu và Ŝ là cường độ sau dịch:
• Pearson Correlation Coefficient (PCC): đo mức nhất quán về xu hướng; PCC(S, Ŝ) = cov(S, Ŝ) / (σ_S σ_Ŝ).
• Relative Error (RE): đo mức thay đổi tương đối về độ lớn; RE(S, Ŝ) = E[|Ŝ−S|/|S|] × 100%.
Công thức trình bày đầy đủ trên slide gốc.

## Trang 27/48

KẾT QUẢ PCC VÀ SAI SỐ TƯƠNG ĐỐI
Theo bảng/biểu đồ của tác giả:
• Hệ số tương quan Pearson nói chung nhỏ hơn 0,2.
• Sai số tương đối phần lớn vượt 80%.
• SIR nhỉnh hơn một chút so với những phương pháp còn lại.
Diễn giải: các phương pháp được kiểm tra chưa giữ tín hiệu thủy vân nhất quán tốt khi chuyển ngữ.

## Trang 28/48

CƯỜNG ĐỘ THỦY VÂN SO VỚI ĐỘ DÀI VĂN BẢN
Slide so sánh cường độ thủy vân và độ dài văn bản, dùng biểu đồ ở phần gốc.
Kết luận được tác giả trình bày: các phương pháp thủy vân văn bản hiện có trong nghiên cứu này thiếu tính nhất quán xuyên ngôn ngữ.

## Trang 29/48

MỤC LỤC — TẤN CÔNG LOẠI BỎ THỦY VÂN
• Động lực.
• Phương pháp KGW và SIR.
• Thủy vân qua dịch: từ các phép đo sang cách phá dấu thủy vân và cách tăng độ bền.

## Trang 30/48

KHOẢNG CÁCH GIỮA PHÉP ĐÁNH GIÁ VÀ TÌNH HUỐNG THẬT
• Chuyển ngôn ngữ: người muốn loại bỏ thủy vân thường không muốn thay đổi ngôn ngữ cuối cùng của câu trả lời.
• Chất lượng văn bản: dịch có thể ảnh hưởng chất lượng, nhưng giai đoạn đánh giá trước chưa đo yếu tố này do đầu ra đã đổi ngôn ngữ.
Điều đó thúc đẩy một phương pháp có thể dùng ngôn ngữ trung gian mà vẫn giữ ngôn ngữ đầu ra.

## Trang 31/48

CWRA — TẤN CÔNG LOẠI BỎ THỦY VÂN XUYÊN NGÔN NGỮ
Tên phương pháp: Cross-lingual Watermark Removal Attack (CWRA).
Slide gốc chứa sơ đồ quy trình tấn công; mục tiêu là tận dụng quá trình chuyển qua ngôn ngữ trung gian và diễn đạt lại để làm suy yếu tín hiệu thủy vân mà vẫn giữ ý chính và ngôn ngữ mong muốn.

## Trang 32/48

HIỆU NĂNG PHÁT HIỆN SAU TẤN CÔNG
Slide đưa ra bảng/biểu đồ hiệu năng phát hiện thủy vân sau khi áp dụng các phương pháp tấn công, gồm CWRA.
Cấu hình tác giả ghi: dùng gpt-3.5-turbo-0613 làm bộ paraphrase và dịch chung cho các phương pháp; mô hình nền Baichuan hỗ trợ tiếng Anh và tiếng Trung.
Chú ý: so sánh này thuộc bộ mô hình, mẫu và tham số của tác giả.

## Trang 33/48

CHẤT LƯỢNG VĂN BẢN SAU TẤN CÔNG
Theo kết quả được trình bày, nhiều phương pháp tấn công vẫn duy trì và đôi khi cải thiện nhẹ chất lượng văn bản — có thể do bộ dịch và bộ paraphrase hoạt động tốt.
CWRA có kết quả tổng thể tốt nhất trong thử nghiệm được nêu. Tác giả suy đoán Baichuan thể hiện tốt hơn ở ngôn ngữ trung gian là tiếng Trung so với ngôn ngữ nguồn tiếng Anh.

## Trang 34/48

MỤC LỤC — PHÒNG VỆ
Sau khi đánh giá và tấn công nhằm xóa dấu, phần này hỏi: làm thế nào tăng tính nhất quán xuyên ngôn ngữ của thủy vân?

## Trang 35/48

PHÒNG VỆ: TĂNG ĐỘ ỔN ĐỊNH KHI ĐỔI NGÔN NGỮ
Các phương pháp dựa trên KGW phụ thuộc vào việc chia từ vựng thành danh sách đỏ và xanh.
Để giữ thủy vân xuyên ngôn ngữ, các token xanh trong văn bản gốc phải tiếp tục được phân loại “xanh” sau khi dịch sang ngôn ngữ khác, xét theo ngữ nghĩa tương ứng.

## Trang 36/48

VÍ DỤ ĐƠN GIẢN 1 — HAI ĐIỀU KIỆN ĐỀU ĐÚNG
Điều kiện 1 (✓): các token tương đương về nghĩa cần nằm trong cùng một danh sách đỏ hoặc xanh.
Điều kiện 2 (✓): các tiền tố tương đương về nghĩa cần sinh ra cùng cách phân chia từ vựng.
Slide minh họa trường hợp thỏa đồng thời cả hai điều kiện.

## Trang 37/48

VÍ DỤ ĐƠN GIẢN 2 — ĐIỀU KIỆN 1 BỊ VI PHẠM
Điều kiện 1 (✗): các token có nghĩa tương tự lại bị xếp vào hai danh sách khác nhau.
Điều kiện 2 (✓): các tiền tố tương đương vẫn có chung cách chia từ vựng.
Kết quả: việc đổi token sang cách diễn đạt khác/ngôn ngữ khác có thể làm suy yếu dấu thủy vân dù tiền tố được xử lý nhất quán.

## Trang 38/48

VÍ DỤ ĐƠN GIẢN 3 — ĐIỀU KIỆN 2 BỊ VI PHẠM
Điều kiện 1 (✓): token tương đương về nghĩa nằm cùng nhóm màu.
Điều kiện 2 (✗): tiền tố tương đương về nghĩa lại dẫn đến hai cách phân chia bộ từ vựng khác nhau.
Kết quả: dấu có thể bị suy yếu khi chuyển ngôn ngữ do sự thiếu nhất quán ở bước xử lý tiền tố.

## Trang 39/48

KẾT LUẬN TỪ CÁC VÍ DỤ
Phải thỏa ĐỒNG THỜI cả hai yếu tố:
1. Token tương đương về ngữ nghĩa thuộc cùng danh sách đỏ hoặc xanh.
2. Tiền tố tương đương về ngữ nghĩa tạo ra cách phân chia từ vựng nhất quán.
Chỉ đạt một trong hai chưa đủ để bảo vệ thủy vân trước biến đổi ngôn ngữ.

## Trang 40/48

PHƯƠNG PHÁP PHÒNG VỆ DỰA TRÊN SIR
Hàm mục tiêu của SIR tối ưu điều kiện thứ hai: bảo đảm sự giống nhau giữa hàm điều chỉnh Δ của hai đầu vào gần với độ tương đồng embedding của chúng.
L = |Sim(E(x), E(y)) − Sim(Δ(x), Δ(y))|.
Trên cơ sở SIR, tác giả đề xuất cách đạt điều kiện thứ nhất và đặt tên là X-SIR.

## Trang 41/48

X-SIR: ĐIỀU CHỈNH HÀM Δ THEO CỤM NGỮ NGHĨA
Định nghĩa phân cụm ngữ nghĩa C của từ vựng V:
C = {C₁, C₂, ..., C_|C|}, mỗi cụm chứa các token tương đương về nghĩa.
Điều chỉnh hàm Δ để cấp bias cho *cả cụm*, thay vì riêng từng token: Δ ∈ ℝ^|C|.
Khi đó logit của token vᵢ trở thành z̃ᵢ = zᵢ + Δ_{C(i)}, trong đó C(i) là chỉ số cụm của vᵢ.
Những token tương đương ở ngôn ngữ khác nhau có thể nhận cùng độ lệch logits.

## Trang 42/48

X-SIR: TẠO CÁC CỤM NGỮ NGHĨA BẰNG TỪ ĐIỂN SONG NGỮ
Thuật toán 1 trên slide:
Đầu vào: từ vựng V và từ điển song ngữ D. Đầu ra: tập cụm C.
1. Tạo đồ thị G với mỗi token của V là một đỉnh.
2. Duyệt mỗi cặp từ tương ứng (vᵢ, vⱼ) trong D; nếu cả hai nằm trong V thì nối hai đỉnh.
3. Tìm các thành phần liên thông của đồ thị G.
4. Mỗi thành phần liên thông tạo một cụm ngữ nghĩa trong C.
5. Trả về C.
Giữ pseudo-code gốc trên slide để đối chiếu từng dòng.

## Trang 43/48

GIỚI HẠN CỦA THUẬT TOÁN PHÂN CỤM
Slide lặp lại thuật toán tạo cụm từ vựng bằng đồ thị và từ điển song ngữ.
Điểm được tác giả nhấn mạnh ở dòng 2–3: chỉ xét các token đồng thời xuất hiện trong từ vựng V và từ điển D. Điều này gây hạn chế bao phủ, sẽ được thảo luận ở phần sau.

## Trang 44/48

KÝ HIỆU ĐẶC BIỆT TRONG SENTENCEPIECE
X-SIR còn xét ký hiệu siêu dữ liệu U+2581 (▁) dùng trong tokenizer SentencePiece, để xử lý biên từ và cách token biểu diễn khoảng trắng.
Hình gốc minh họa cách cụm ngữ nghĩa tương tác với quy tắc token hóa.

## Trang 45/48

KẾT QUẢ PHÁT HIỆN THỦY VÂN CỦA X-SIR
Slide báo cáo hiệu năng phát hiện thủy vân của phương pháp X-SIR; các biểu đồ/điểm số được giữ ở trang nguồn.
Trọng tâm là so sánh độ bền qua ngôn ngữ với các baseline KGW và SIR.

## Trang 46/48

KẾT QUẢ CHẤT LƯỢNG VĂN BẢN
Slide báo cáo chất lượng văn bản do các phương pháp thủy vân và phòng vệ sinh ra.
Việc phát hiện thủy vân tốt hơn cần được đánh giá song song với ảnh hưởng đến tính tự nhiên và ý nghĩa của câu.

## Trang 47/48

GIỚI HẠN CỦA PHƯƠNG PHÁP
Phân cụm ngữ nghĩa chỉ xét những token nằm trong cả từ vựng V của mô hình và từ điển ngoài D.
• Bao phủ ngôn ngữ: chỉ hỗ trợ các ngôn ngữ mà mô hình xử lý. Trong thực tế người tấn công có thể tùy ý chọn ngôn ngữ nguồn và ngôn ngữ trung gian.
• Bao phủ từ vựng (20,76%): từ điển D chủ yếu chứa từ hoàn chỉnh, khó gom nhóm những đơn vị con-từ; tokenizer Llama có xu hướng tách một ký tự tiếng Trung thành nhiều byte.
Hệ quả: các token không được gom nhóm có thể khiến thủy vân không ổn định qua dịch.

## Trang 48/48

BÀI BÁO VÀ MÃ NGUỒN
Paper: https://arxiv.org/abs/2402.14007
Code: https://github.com/zwhe99/X-SIR
Tác giả: Zhiwei He. Kết thúc bài giảng về KGW, SIR, X-SIR và thủy vân xuyên ngôn ngữ.



---

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



---

# Chương 07 — Giấu tin bằng mô hình lớn

Nguồn gốc: `documents/chapter7/stega.pdf` · commit `f84c04268794ef94f8949808bbc14ab8636763a0`.

**Nội dung dưới đây là phần chuyển ngữ/diễn giải tiếng Việt theo từng trang slide**, phục vụ đối chiếu với bản gốc; không bảo đảm từng câu chữ trong hình được thay thế.

## Trang 1/13

THỰC HÀNH GIẤU TIN VỚI MÔ HÌNH NGÔN NGỮ LỚN (LLM)
Tác giả: Zhang Yulong (张玉龙).

## Trang 2/13

ỨNG DỤNG MÔ HÌNH LỚN TRONG TRUYỀN THÔNG AN TOÀN
Giấu tin (steganography) là kỹ thuật nhúng thông tin vào phương tiện chứa như ảnh, âm thanh, video hay văn bản để liên lạc kín đáo. Khác với mật mã, kỹ thuật này che giấu cả nội dung lẫn sự tồn tại của quá trình trao đổi. Thông tin được giấu trong phần dư thừa hoặc những khác biệt khó nhận ra bằng giác quan, khiến vật mang trông giống bản thông thường.
Ứng dụng gồm truyền tin kín, bảo vệ bản quyền. Tuy nhiên công nghệ cũng có thể bị lợi dụng vào gián điệp, khủng bố hoặc các hoạt động gây hại.

## Trang 3/13

Ý NGHĨA CỦA GIẤU TIN
Giấu tin là một phương thức truyền thông an toàn khác với mật mã học. Mật mã mã hóa nội dung để người đứng giữa không đọc được, nhưng người đó vẫn có thể phát hiện, chặn hoặc sửa phương tiện chứa bản mã.
Giấu tin che giấu chính việc có thông điệp đang được truyền: nhúng nội dung vào một kênh công khai, ngụy trang như dữ liệu bình thường để chỉ người nhận biết cách giải mã mới phát hiện được.
Ví dụ đời thường: thơ giấu chữ đầu dòng, mảnh giấy kẹp trong sách. Kỹ thuật liên quan: thủy vân (watermarking) — ưu tiên tính bền vững và thường cho phép nhiều người phát hiện/giải mã dấu.

## Trang 4/13

VÍ DỤ GIẤU TIN VÀ SO SÁNH VỚI MẬT MÃ
Giấu tin trong văn bản: thay đổi rất nhỏ khoảng cách giữa ký tự (ví dụ 0,1 pt) hoặc màu chữ (#000000 so với #010101), mã hóa bit 0/1 theo quy ước. Thông tin nằm trong văn bản công khai và khó nhận thấy bằng mắt thường.
Mật mã Vigenère: dùng một khóa lặp (ví dụ KEY) để mã hóa HELLO thành RIJVS. Kết quả là bản mã trông không đọc được, chỉ bên giữ khóa mới giải mã.
Khác biệt: tài liệu giấu tin trông như tệp bình thường; bản mã cho thấy có thông điệp đã mã hóa nhưng giữ kín nội dung.

## Trang 5/13

VÍ DỤ GIẤU TIN TRONG ẢNH VÀ PHỐI HỢP MẬT MÃ
Giấu tin ảnh LSB: thay đổi bit ít quan trọng nhất trong giá trị pixel để nhúng dữ liệu bí mật. Mắt thường khó nhận thấy, nhưng công cụ thích hợp có thể trích xuất. Vật mang có thể là ảnh du lịch thông thường.
Mã hóa AES-256: dùng khóa mã hóa tệp thành dữ liệu không đọc được; mục đích là bảo mật nội dung ngay cả khi tệp bị chặn bắt.
Phối hợp: mã hóa dữ liệu bằng AES trước, sau đó giấu bản mã trong ảnh bằng LSB. Hai lớp bảo vệ che giấu cả sự tồn tại của thông điệp và nội dung của nó.

## Trang 6/13

GIẤU TIN TRONG MÃ QR
Nguyên lý: tạo mã QR trông bình thường, ví dụ liên kết tới trang web vô hại, nhưng nhúng thông tin bổ sung vào vùng sửa lỗi hoặc mẫu điểm ảnh được thiết kế đặc biệt. Ứng dụng quét QR thông thường chỉ thấy lớp công khai; ứng dụng tùy chỉnh có thể đọc lớp ẩn.
Ví dụ: mã QR thực đơn nhà hàng có thể mở thông tin món ăn; công cụ riêng đọc được mã ưu đãi hoặc thông báo nội bộ. Mã QR trên poster có thể chứa lời mời VIP ở lớp ẩn.
Ứng dụng: tiếp thị, trò chơi săn tìm, thông báo nhân viên, bảo vệ bản quyền. Muốn xây dựng cần hiểu cấu trúc QR, nhất là độ dư thừa của mã sửa lỗi, và dùng công cụ tạo QR hai lớp.

## Trang 7/13

MÔ HÌNH QUY TRÌNH GIẤU TIN
Giấu tin trong phương tiện số thường dùng ảnh/video vì chúng có nhiều phần dư thừa để nhúng bit. Văn bản ít dư thừa hơn, nhưng linh hoạt và có thể đưa vào nhiều ngữ cảnh. Bài này giới thiệu giấu tin văn bản bằng LLM.
Sơ đồ trên trang gốc: mô hình quy trình giấu tin ở bên trái; mô hình thủy vân ở bên phải. Giữ hình gốc để đối chiếu.

## Trang 8/13

PHÂN LOẠI GIẤU TIN VĂN BẢN
Hai nhóm chính:
• Giấu tin bằng chỉnh sửa (modification-based): sửa một văn bản vốn có để mang thông tin.
• Giấu tin bằng sinh nội dung (generation-based): tạo mới văn bản đồng thời nhúng thông tin.
Theo tác giả, sự phát triển của học sâu và các mô hình lớn đã khiến phương pháp sinh văn bản trở thành một hướng chủ đạo.

## Trang 9/13

CƠ CHẾ GIẤU TIN KHI LLM SINH TOKEN (1–3)
Bộ sinh văn bản làm việc trên chuỗi token. Với tiền tố/ngữ cảnh và các tham số sinh, mô hình trả về logits cho token tiếp theo, tương ứng các ID token và mức điểm/xác suất.
Trong chế độ sinh thông thường, mô hình chọn một trong các token ứng viên dựa trên phân bố và tham số lấy mẫu, rồi tiếp tục chu kỳ.
Trong giấu tin bằng sinh văn bản, một quy tắc đã định can thiệp vào lựa chọn token tiếp theo nhằm mã hóa các bit bí mật vào chuỗi được sinh ra. Ba công trình nghiên cứu tham khảo nằm ở cuối slide gốc.

## Trang 10/13

GIẤU TIN BẰNG MÃ NHỊ PHÂN TRÊN CÁC TOKEN ỨNG VIÊN
Giả sử thông điệp cần giấu đã thành chuỗi bit. Tại mỗi bước, mã hóa n token có xác suất cao nhất thành các mã bit.
Ví dụ, sau tiền tố “I”, tám token có điểm cao nhất là các từ như have (000), am (001), was (010), can (011), ...; mỗi token gắn với ba bit. Để nhúng chuỗi 001, ta chọn “am” làm token tiếp theo; rồi lặp lại ở bước sinh tiếp theo.
Đây là ví dụ minh họa theo sơ đồ trong tài liệu, không phải mã nguồn đã được chạy.

## Trang 11/13

GIẢI MÃ BẰNG CÁCH KHÔI PHỤC KHÔNG GIAN ỨNG VIÊN
Cách cơ bản là mã hóa n token hàng đầu theo thứ tự, tạo một “không gian giấu tin” ở mỗi bước sinh.
Khi giải mã, người nhận dùng cùng mô hình, cùng văn bản tiền tố và cùng tham số; khi đó, về nguyên tắc, có thể dựng lại danh sách token/mã bit giống như lúc gửi. Quan sát token đã chọn để khôi phục bit đã nhúng: ví dụ token “am” ↦ 001.
Điều kiện đồng nhất mô hình, ngữ cảnh và cách tính là thiết yếu; sai khác có thể khiến việc giải mã mất đồng bộ.

## Trang 12/13

CẢI THIỆN HIỆU SUẤT BẰNG MÃ HUFFMAN
Ví dụ trước dùng cách gán mã cố định theo thứ tự n token. Hình minh họa trên slide cho thấy cách sử dụng mã Huffman, nhờ đó phân bổ mã theo phân bố token để nhúng nhiều bit hơn khi có điều kiện phù hợp, nâng tỉ lệ nhúng.

## Trang 13/13

Ý NGHĨA VÀ HƯỚNG PHÁT TRIỂN
• Giấu tin bằng LLM có thể tận dụng khả năng sinh ngôn ngữ để tạo văn bản tự nhiên hơn, khó phát hiện hơn.
• Không gian mã hóa là yếu tố cốt lõi: xây dựng một không gian token/mã mới có thể dẫn đến phương pháp giấu tin mới.
• Bản chất của phương pháp sinh là mã hóa lặp trên dữ liệu có thứ tự. Tác giả đề xuất khả năng áp dụng sang phương tiện khác, ví dụ DNA; đây là định hướng mang tính suy đoán, không phải kỹ thuật đã được chứng minh trong bài giảng.
• Giấu tin có liên hệ với thủy vân LLM, ví dụ KGW cũng áp dụng ràng buộc lựa chọn token tiếp theo.
• Phân tích phát hiện giấu tin (steganalysis) có thể hỗ trợ phát hiện nội dung bị mã hóa hoặc hành vi trực tuyến gây hại, qua đó đóng góp cho an toàn thông tin.



---

# Chương 08 — Mô hình đa phương thức

Nguồn gốc: `documents/chapter8/mllms.pdf` · commit `f84c04268794ef94f8949808bbc14ab8636763a0`.

**Nội dung dưới đây là phần chuyển ngữ/diễn giải tiếng Việt theo từng trang slide**, phục vụ đối chiếu với bản gốc; không bảo đảm từng câu chữ trong hình được thay thế.

## Trang 1/81

GIỚI THIỆU NGẮN VỀ MÔ HÌNH NGÔN NGỮ LỚN ĐA PHƯƠNG THỨC (MLLM)
Tác giả: Hao Fei, nghiên cứu viên, Đại học Quốc gia Singapore.
Trang chuỗi bài giảng: https://mllm2024.github.io/COLING2024. Website tác giả: http://haofei.vip/.

## Trang 2/81

MỤC LỤC BÀI GIẢNG
Phần 1 — Phương thức và chức năng (Modality & Functionality): tổng quan, nhận biết đa phương thức, nhận biết kết hợp sinh, MLLM hợp nhất, MLLM chi tiết tới mức pixel.
Phần 2 — Kiến trúc (Architecture): tổng quan, mã hóa đa phương thức, token hóa, phép chiếu đầu vào, LLM lõi (backbone), kết nối bộ giải mã và sinh đa phương thức.

## Trang 3/81

TRÍ TUỆ TỪ DỮ LIỆU ĐA GIÁC QUAN
Xu hướng của các mô hình ngôn ngữ lớn đa phương thức (Multimodal LLMs, MLLMs).
Bài báo tham khảo: “MM-LLMs: Recent Advances in Multimodal Large Language Models” (2023). Hình gốc mô tả xu thế phát triển đa phương thức.

## Trang 4/81

TRÍ TUỆ TỪ DỮ LIỆU ĐA GIÁC QUAN
Xu hướng MLLM được tổng hợp trong “A Survey on Multimodal Large Language Models” (2023).
Tài nguyên liên quan: https://github.com/BradyFU/Awesome-Multimodal-Large-Language-Models.
Hình gốc cung cấp bảng minh họa/hệ sinh thái các hệ thống đa phương thức.

## Trang 5/81

PHẦN 1 — PHƯƠNG THỨC VÀ CHỨC NĂNG
Một mô hình ngôn ngữ lớn đa phương thức có thể làm được những nhiệm vụ gì?
Câu hỏi phân loại: nhận những loại dữ liệu nào (modality) và tạo ra loại đầu ra nào (functionality)?

## Trang 6/81

TỔNG QUAN PHƯƠNG THỨC
Ví dụ cơ bản: kết hợp ngôn ngữ (language) và thị giác (vision).
Nhiều MLLM tiếp nhận văn bản cùng ảnh, video hoặc thông tin thị giác, rồi tạo đầu ra theo yêu cầu.

## Trang 7/81

BẢNG TOÀN CẢNH MLLM
Bảng phân loại theo phương thức đầu vào và chức năng:
• Ảnh, video, âm thanh, dữ liệu 3D.
• Nhận biết/hiểu đầu vào (perceiving), bao gồm mức đối tượng và mức vùng/pixel.
• Nhận biết kết hợp sinh nội dung (perceiving + generating).
• Hệ thống hợp nhất đa phương thức, có thể xử lý nhiều modality cùng lúc.
Bảng nguồn liệt kê các hệ như Flamingo, BLIP-2, LLaVA, GPT-4V, Video-LLaMA, SpeechGPT, 3D-LLM, NExT-GPT và Unified-IO 2; giữ nguyên toàn bộ tên mô hình và phân loại trong slide gốc.

## Trang 8/81

MLLM HIỂU ẢNH (IMAGE-PERCEIVING)
Các ví dụ: Flamingo, Kosmos-1, BLIP-2, mPLUG-Owl, MiniGPT-4, LLaVA, InstructBLIP, Qwen-VL, GPT-4V, v.v.
Cơ chế chung: encoder ảnh ngoài biến ảnh đầu vào thành đặc trưng thị giác mà LLM có thể sử dụng. LLM nhận đặc trưng cùng chỉ dẫn văn bản, giải thích nội dung ảnh và sinh câu trả lời dạng văn bản.
Hình nguồn mô tả pipeline: Image → Encoder → LLM + Text → Text.

## Trang 9/81

VÍ DỤ KIẾN TRÚC HIỂU ẢNH
Bài giảng minh họa bốn hệ thống: BLIP-2, LLaVA, Flamingo và MiniGPT-4.
Tham khảo: Flamingo (2022), BLIP-2 (2023), Visual Instruction Tuning (2023), khảo sát MLLM (2023).
Hình trên slide gốc cho thấy sự khác nhau trong cách nối encoder ảnh với mô hình ngôn ngữ.

## Trang 10/81

MLLM HIỂU VIDEO (VIDEO-PERCEIVING)
Ví dụ: VideoChat, Video-ChatGPT, Video-LLaMA, PandaGPT, MovieChat, Video-LLaVA, LLaMA-VID, Momentor.
Encoder video trích đặc trưng hình ảnh/chuyển động theo thời gian, chuyển chúng thành biểu diễn phù hợp với LLM. LLM dùng chỉ dẫn bằng văn bản và nội dung video để đưa ra phản hồi bằng văn bản.
Các bài báo về VideoChat, Video-ChatGPT, Video-LLaMA, Video-LLaVA và Momentor được dẫn trên slide gốc.

## Trang 11/81

VÍ DỤ HỆ THỐNG HIỂU VIDEO
So sánh sơ đồ minh họa của Video-ChatGPT và Video-LLaVA.
Bài giảng dẫn nguồn “Video-ChatGPT: Towards Detailed Video Understanding...” và “Video-LLaVA: Learning United Visual Representation by Alignment Before Projection”.
Khác biệt kiến trúc được trình bày trực tiếp trong hình nguồn.

## Trang 12/81

MLLM NHẬN BIẾT THÔNG TIN 3D
Ví dụ: 3D-LLM, 3D-GPT, LL3DA, SpatialVLM, PointLLM, Point-Bind.
Encoder 3D ngoài xử lý dữ liệu không gian hoặc đám mây điểm (point cloud), tạo đặc trưng 3D mà LLM có thể diễn giải. LLM kết hợp đặc trưng này với chỉ dẫn văn bản để trả lời về hình học hoặc quan hệ không gian.
Slide dẫn các công trình 3D-LLM, 3D-GPT, LL3DA, PointLLM và SpatialVLM.

## Trang 13/81

VÍ DỤ HỆ THỐNG NHẬN BIẾT 3D
Hai công trình được minh họa: 3D-LLM và PointLLM.
Hình nguồn cho thấy việc chuyển dữ liệu 3D/đám mây điểm thành thông tin ngôn ngữ có thể dùng cho đối thoại hoặc trả lời câu hỏi.

## Trang 14/81

MLLM HIỂU ÂM THANH
Ví dụ: AudioGPT, SpeechGPT, VIOLA, AudioPaLM, SALMONN, MU-LLaMA.
Encoder âm thanh chuyển lời nói, nhạc và âm thanh môi trường thành đặc trưng cho LLM. Mô hình sử dụng chỉ dẫn bằng văn bản để giải thích đầu vào âm thanh và tạo câu trả lời dạng chữ.
Các công trình tham khảo gồm AudioGPT, SpeechGPT, VIOLA, AudioPaLM và SALMONN.

## Trang 15/81

VÍ DỤ HỆ THỐNG XỬ LÝ ÂM THANH
Minh họa hai mô hình SpeechGPT và SALMONN; tham khảo các bài báo về khả năng đối thoại xuyên phương thức và năng lực nghe của LLM.
Nhìn vào sơ đồ nguồn để phân biệt phần nhận dạng âm thanh, phần biểu diễn và phần LLM.

## Trang 16/81

MLLM CHUYÊN MIỀN SINH HỌC VÀ Y HỌC
Hệ thống có thể nối ngôn ngữ với thông tin sinh học hoặc y khoa.
Ví dụ được liệt kê: BioGPT, DrugGPT, BioMedLM, OphGLM, GatorTron, MEDITRON, MedAlpaca, AlpaCare, PMC-LLaMA, MedPaLM 2, BioMedGPT, DoctorGLM, ClinicalGPT, HuatuoGPT, v.v.
Các tài liệu nguồn gồm BioGPT, DrugGPT, MEDITRON, HuaTuo và khảo sát LLM trong y học. Đây là danh mục công trình, không phải xác nhận hiệu quả y tế.

## Trang 17/81

MLLM CHO PHÂN TỬ, ĐỒ THỊ VÀ THÔNG TIN ĐỊA LÝ
• Hóa học/phân tử: ChemGPT, ChemLLM, MolCA, MolXPT, MolSTM, GIMLET, v.v.
• Đồ thị (graph): StructGPT, GPT4Graph, GraphGPT, LLaGA, HiGPT.
• Thông tin địa lý (GIS): GeoGPT.
Hình nguồn mô tả việc chuyển dữ liệu phân tử, đồ thị hoặc các cấu trúc khác sang biểu diễn dùng chung với mô hình ngôn ngữ.

## Trang 18/81

MLLM VỪA HIỂU VỪA SINH ĐA PHƯƠNG THỨC
Trong nhiều tình huống, mô hình phải hiểu dữ liệu nhiều phương thức đầu vào đồng thời có thể tạo nội dung cùng phương thức ấy.
Ví dụ nhiệm vụ: tạo chú thích ảnh (image captioning), hỏi đáp thị giác, tạo ảnh từ chữ, chuyển đổi hình ảnh, nhận dạng chữ trong cảnh và điền/khôi phục vùng chữ trên ảnh.
Đây là nhóm “Perceiving + Generating”.

## Trang 19/81

SINH ẢNH BẰNG MLLM
Ví dụ: GILL, EMU, MiniGPT-5, DreamLLM, LLaVA-Plus, LaVIT.
LLM lõi tiếp nhận cả văn bản lẫn hình ảnh, diễn giải nội dung/ý nghĩa rồi tạo đầu ra dạng văn bản và hình ảnh.
Các bài báo được trích: Generating Images with Multimodal Language Models, Generative Pretraining in Multimodality, MiniGPT-5, DreamLLM, LLaVA-Plus.

## Trang 20/81

VÍ DỤ HỆ THỐNG SINH ẢNH
Hai hệ thống được minh họa: GILL và EMU.
Hình nguồn đối chiếu cách phối hợp mô hình ngôn ngữ với mô-đun sinh hình ảnh. Xem hình để biết những thành phần huấn luyện/tương tác cụ thể.

## Trang 21/81

SINH VIDEO BẰNG MLLM
Ví dụ: GPT4Video, VideoPoet và Video-LaVIT.
LLM lõi có thể nhận văn bản và video làm đầu vào, dùng kiến thức ngữ nghĩa để tạo phản hồi bằng văn bản và video.
Tham khảo công trình GPT4Video, VideoPoet (sinh video zero-shot) và Video-LaVIT (token hóa tách thông tin thị giác và chuyển động).

## Trang 22/81

VÍ DỤ HỆ THỐNG SINH VIDEO
Minh họa GPT4Video và VideoPoet.
Tài liệu tham khảo nêu thiết kế mô hình kết hợp hiểu video và tạo video từ ngữ cảnh ngôn ngữ, với các cách biểu diễn video khác nhau.

## Trang 23/81

SINH ÂM THANH BẰNG MLLM
Ví dụ: AudioGPT, SpeechGPT, VIOLA và AudioPaLM.
LLM lõi có thể tiếp nhận cả văn bản lẫn âm thanh, sau đó tạo đầu ra dạng chữ hoặc âm thanh nhờ liên kết với bộ sinh/giải mã âm thanh.
Bài báo tham khảo: AudioGPT, SpeechGPT, VIOLA, AudioPaLM.

## Trang 24/81

VÍ DỤ HỆ THỐNG SINH ÂM THANH
Hai hệ thống AudioGPT và SpeechGPT được minh họa.
Tập trung vào mối nối giữa khả năng hiểu chỉ dẫn ngôn ngữ và các tác vụ xử lý lời nói, nhạc, tiếng động và sinh phản hồi âm thanh.

## Trang 25/81

HỆ THỐNG HỢP NHẤT NHIỀU PHƯƠNG THỨC
Trong thế giới thực, nhiều loại dữ liệu liên kết chặt chẽ với nhau. Vì vậy MLLM cần hiểu đồng thời nhiều modality phi văn bản, thay vì chỉ một loại.
Ví dụ kết hợp: Ảnh + Video, Âm thanh + Video, Ảnh + Video + Âm thanh, hoặc mô hình bất kỳ-đến-bất kỳ (any-to-any).

## Trang 26/81

LLM KẾT HỢP CHỮ, ẢNH VÀ VIDEO
Ví dụ: Video-LLaVA, Chat-UniVi, LLaMA-VID.
LLM lõi nhận cả văn bản, ảnh và video để hiểu ngữ nghĩa, rồi tạo văn bản (có thể mở rộng sang ảnh/video tùy mô hình).
Công trình: Video-LLaVA (căn chỉnh trước phép chiếu), Chat-UniVi (biểu diễn thị giác hợp nhất), LLaMA-VID (cách biểu diễn ảnh/video tiết kiệm token).

## Trang 27/81

VÍ DỤ CHAT-UNIVI
Hình nguồn giới thiệu Chat-UniVi: “Unified Visual Representation Empowers Large Language Models with Image and Video Understanding” (2023).
Mục tiêu là sử dụng biểu diễn thị giác dùng chung cho cả ảnh và video trong mô hình ngôn ngữ.

## Trang 28/81

LLM KẾT HỢP CHỮ, ẢNH, VIDEO VÀ ÂM THANH
Các công trình: PandaGPT, Video-LLaMA, AnyMAL, Macaw-LLM, VideoPoet, ImageBind-LLM, LLMBind, LLaMA-Adapter.
LLM lõi tiếp nhận văn bản cùng ảnh, video và âm thanh, rồi tạo phản hồi bằng chữ, hoặc mở rộng ra các modality khác tùy thiết kế.
Tham khảo PandaGPT, Video-LLaMA, AnyMAL và Macaw-LLM.

## Trang 29/81

VÍ DỤ MACAW-LLM
Minh họa Macaw-LLM: “Multi-Modal Language Modeling with Image, Audio, Video, and Text Integration” (2023).
Hình gốc chỉ ra quá trình tích hợp bốn modality: chữ, ảnh, video, âm thanh.

## Trang 30/81

MLLM “ANY-TO-ANY”
Các ví dụ: NExT-GPT, Unified-IO 2 (không video), AnyGPT (không video), CoDi-2, ModaVerse.
Mô hình có thể tiếp nhận văn bản, ảnh, video và âm thanh, và tạo đầu ra linh hoạt bằng các modality này hoặc phối hợp chúng.
Tham khảo công trình NExT-GPT, AnyGPT, CoDi-2 và ModaVerse.

## Trang 31/81

NExT-GPT: THÔNG TIN CÔNG TRÌNH
NExT-GPT: “Any-to-Any Multimodal LLM” (2023).
Trang dự án: https://next-gpt.github.io
Bài báo: https://arxiv.org/pdf/2309.05519
Mã nguồn: https://github.com/NExT-GPT/NExT-GPT
Trang gốc chứa hình minh họa ứng dụng và các modality được hỗ trợ.

## Trang 32/81

NExT-GPT: VÍ DỤ KHẢ NĂNG
Trang nguồn tiếp tục minh họa NExT-GPT, một hệ thống có mục đích hỗ trợ kết hợp đầu vào và đầu ra đa phương thức.
Các hình ví dụ cho thấy cách người dùng cung cấp thông tin bằng một modality và nhận đầu ra bằng một hoặc nhiều modality khác.

## Trang 33/81

NExT-GPT: SƠ ĐỒ TỔNG THỂ
Trang nguồn hiển thị các thành phần của hệ thống NExT-GPT. Mô hình thực hiện căn chỉnh bộ mã hóa, LLM và bộ sinh theo từng modality.
Sơ đồ gốc giúp xác định đường truyền biểu diễn giữa encoder, các lớp projection, LLM và decoder.

## Trang 34/81

NExT-GPT: BA GIAI ĐOẠN KIẾN TRÚC
1. Multimodal Encoding Stage: mã hóa đầu vào đa phương thức.
2. LLM Understanding and Reasoning Stage: LLM lõi diễn giải và quyết định đầu ra.
3. Multimodal Generation Stage: tạo các đầu ra ảnh/video/âm thanh hoặc chữ qua các bộ giải mã tương ứng.
Xem các khối trong hình gốc để phân biệt chức năng từng giai đoạn.

## Trang 35/81

NExT-GPT: BỘ MÃ HÓA ĐA PHƯƠNG THỨC
• Sử dụng ImageBind làm encoder đa phương thức hợp nhất.
• Thêm lớp chiếu đầu vào (input projection) để nối biểu diễn do encoder tạo ra với không gian đầu vào của LLM.
Hình nguồn đánh dấu ImageBind và Input Projection. Đây là thành phần thích nghi giữa không gian biểu diễn khác nhau.

## Trang 36/81

NExT-GPT: DÙNG MÔ HÌNH KHUẾCH TÁN ĐỂ SINH NỘI DUNG
Tận dụng các mô hình sinh ảnh, video và âm thanh dựa trên diffusion đã có, thay vì huấn luyện toàn bộ từ đầu.
Các thành phần trong sơ đồ:
• Text encoder: điều khiển quá trình sinh.
• VAE: biểu diễn nén/giải nén.
• U-Net: thành phần chính trong một số hệ diffusion.
Mô hình lõi và bộ sinh được nối với nhau thông qua biểu diễn tín hiệu.

## Trang 37/81

NExT-GPT: LLM QUYẾT ĐỊNH MODALITY CỦA ĐẦU RA
LLM đóng vai trò lõi, quyết định có cần sinh nội dung đa phương thức hay không và cần sinh loại nào.
Thay vì chỉ viết một câu lệnh văn bản, LLM tạo các token tín hiệu modality (modality signal tokens) chuyên biệt, đóng vai trò chỉ dẫn cho những mô-đun sinh ảnh/video/âm thanh.

## Trang 38/81

NExT-GPT: MINH HỌA CƠ CHẾ TÍN HIỆU
Trang nguồn minh họa việc LLM tạo các token tín hiệu modality rồi chuyển tới các nhánh bộ sinh tương ứng trong kiến trúc NExT-GPT.
Hình gốc giúp theo dõi cách đầu vào và đầu ra được điều phối giữa các mô-đun.

## Trang 39/81

NExT-GPT: MINH HỌA QUY TRÌNH
Tiếp tục ví dụ và sơ đồ từ bài báo NExT-GPT (2023). Nội dung chính là xử lý thông tin đa phương thức thông qua encoder hợp nhất, LLM và decoder theo từng phương thức.

## Trang 40/81

NExT-GPT: VÍ DỤ SINH NỘI DUNG
Các minh họa trên slide cho thấy mô hình phối hợp xử lý nội dung chữ, ảnh, video và âm thanh.
Đây là hình minh họa kiến trúc/đầu ra của nghiên cứu NExT-GPT, chưa được tái chạy hoặc thẩm định trong tài liệu dịch.

## Trang 41/81

NExT-GPT: MINH HỌA THÊM
Slide nguồn tiếp tục trình bày ví dụ NExT-GPT nhằm làm rõ khả năng chuyển giữa các modality.
Giữ nguyên minh họa để xem những loại tín hiệu xuất hiện ở từng thành phần.

## Trang 42/81

NExT-GPT — ƯU ĐIỂM 1: HUẤN LUYỆN TIẾT KIỆM THAM SỐ
Phần lớn tham số của các mô hình nền được đóng băng, chỉ huấn luyện các bộ kết nối tương đối nhỏ.
Theo công thức slide: khoảng 131 triệu tham số có thể tinh chỉnh so với tổng 131 triệu + 12,275 tỷ tham số, tỷ lệ xấp xỉ 0,01 (khoảng 1%).
Điều này giảm chi phí so với tinh chỉnh toàn bộ hệ thống. Cách tính và các số hạng chi tiết giữ trong hình nguồn.

## Trang 43/81

NExT-GPT — ƯU ĐIỂM 2: TINH CHỈNH CHỈ DẪN KHI CHUYỂN MODALITY
Modality-switching Instruction Tuning: dùng các cặp chỉ dẫn và đầu ra phù hợp để hệ thống học khi nào phải chuyển sang nhánh ảnh, âm thanh, video hoặc phối hợp nhiều loại.
Sơ đồ nguồn trình bày vai trò của việc tinh chỉnh chỉ dẫn này.

## Trang 44/81

KHẢ NĂNG MLLM Ở MỨC CHI TIẾT (FINE-GRAINED)
Nhiều mô hình thị giác-ngôn ngữ chỉ hiểu ở mức đối tượng/ảnh tổng thể. Vì thiếu gắn kết với từng vùng ảnh (visual grounding), chúng dễ suy luận thiếu chính xác hoặc tạo nội dung không được ảnh hỗ trợ.
Các nhiệm vụ cần độ chính xác theo vùng/pixel: định vị đối tượng, phân đoạn, chỉnh sửa ảnh, điền vùng ảnh (inpainting).

## Trang 45/81

MLLM THỊ GIÁC HIỂU VÙNG ẢNH Ở MỨC PIXEL
Các mô hình: GPT4RoI, NExT-Chat, MiniGPT-v2, Shikra, Kosmos-2, GLaMM, LISA, DetGPT, Osprey, PixelLM, LION.
Người dùng đưa ảnh, có thể chỉ định một vùng; LLM tạo câu trả lời dựa vào nội dung ảnh, liên kết các mô tả với những vùng cụ thể ở mức pixel.
Bài giảng dẫn 10 công trình từ 2023 trở đi; xem bảng nguồn để giữ nguyên trích dẫn.

## Trang 46/81

VÍ DỤ MLLM HIỂU VÙNG ẢNH
Minh họa hai hệ thống NExT-Chat và GLaMM.
Mục tiêu là định vị, phân đoạn và giải thích những đối tượng cụ thể trên ảnh, không chỉ đưa nhận xét chung về toàn bức ảnh.

## Trang 47/81

MLLM THỊ GIÁC THEO VÙNG/PIXEL TRÊN VIDEO
Ví dụ: PG-Video-LLaVA, Merlin, MotionEpic.
Người dùng đưa video, có thể chỉ định một vùng; LLM cần tạo mô tả, định vị hoặc theo dõi thông tin tới các vùng pixel cụ thể theo thời gian.
Slide dẫn các nghiên cứu PG-Video-LLaVA, Merlin và Video-of-Thought.

## Trang 48/81

VÍ DỤ ĐỊNH VỊ VÙNG TRONG VIDEO
Hai hệ thống minh họa: PG-Video-LLaVA và MotionEpic.
Mục tiêu là gắn mô tả ngôn ngữ với các vùng/đối tượng trong từng khung hình và theo dõi chúng qua thời gian.

## Trang 49/81

MLLM HỢP NHẤT Ở MỨC PIXEL: VITRON
VITRON là mô hình thị giác–ngôn ngữ cho các nhiệm vụ hiểu, sinh, phân đoạn và chỉnh sửa theo mức pixel.
Có thể nhận ảnh hoặc video, có thể nhận vùng được chỉ định. LLM đưa phản hồi, tạo nội dung hoặc gắn/truy vết vùng pixel tương ứng trên ảnh/video.
Bài báo: VITRON: A Unified Pixel-level Vision LLM for Understanding, Generating, Segmenting, Editing (2024).

## Trang 50/81

VITRON: SƠ ĐỒ VÀ VÍ DỤ
Slide nguồn minh họa VITRON — hệ thống hợp nhất các nhiệm vụ thị giác chi tiết.
Xem sơ đồ để phân biệt nhánh hiểu, nhánh sinh, phân đoạn và chỉnh sửa vùng.

## Trang 51/81

VITRON: CÁC KHẢ NĂNG ĐA NHIỆM
Tiếp tục minh họa VITRON với các đầu vào ảnh/video và đầu ra gắn vùng pixel.
Thông tin kỹ thuật và trích dẫn công trình giữ nguyên trên slide gốc.

## Trang 52/81

PHẦN 2 — KIẾN TRÚC MLLM
Câu hỏi: thiết kế một mô hình ngôn ngữ lớn đa phương thức như thế nào?
Các thành phần quan trọng: encoder, token hóa, phép chiếu đầu vào, LLM lõi, kết nối decoder và cơ chế sinh.

## Trang 53/81

Ý TƯỞNG SƠ BỘ: TRÍ TUỆ TRONG MIỀN NGÔN NGỮ
Theo giả định được nêu trong bài giảng, quy luật mở rộng quy mô (scaling law) và các hiện tượng năng lực xuất hiện trong LLM có thể tạo nên khả năng hiểu ngữ nghĩa mạnh.
Từ đó, ngôn ngữ được coi là phương thức trung tâm mang tri thức; nhận định này làm nền cho nhiều kiến trúc MLLM.

## Trang 54/81

NGÔN NGỮ LÀ TRỤC KẾT NỐI CÁC PHƯƠNG THỨC
Theo cách nhìn của tác giả, phần lớn MLLM hiện hành đặt LLM xử lý ngôn ngữ ở trung tâm như bộ ra quyết định.
Bằng cách nối thêm encoder hoặc mô-đun chuyên xử lý dữ liệu phi văn bản, hệ thống có thể xử lý 3D, âm thanh, mùi, xúc giác, video, hình ảnh.
Hình gốc mô tả các modality xoay quanh LLM lõi.

## Trang 55/81

KIẾN TRÚC I — LLM NHƯ BỘ LẬP LỊCH/ĐIỀU KHIỂN RỜI RẠC
LLM nhận đầu vào bằng văn bản và phát ra lệnh dạng chữ để gọi những mô-đun phía sau.
Mọi giao tiếp trong hệ thống — từ encoder đa phương thức vào LLM hoặc từ LLM đến bộ sinh — đều sử dụng câu lệnh văn bản làm kênh trung gian.
Các mô-đun downstream được phối hợp qua lệnh của LLM, không cần một không gian vector hợp nhất chung.

## Trang 56/81

VÍ DỤ KIẾN TRÚC I
Các hệ thống được liệt kê: Visual-ChatGPT, HuggingGPT, MM-REACT, ViperGPT, AudioGPT, LLaVA-Plus.
Sơ đồ minh họa: người dùng gửi văn bản tới LLM; LLM điều phối bằng lệnh văn bản đến nhiều mô-đun chuyên biệt rồi tổng hợp kết quả.

## Trang 57/81

VÍ DỤ VISUAL-CHATGPT VÀ HUGGINGGPT
Công trình:
• Visual ChatGPT: Talking, Drawing and Editing with Visual Foundation Models (2023).
• HuggingGPT: Solving AI Tasks with ChatGPT and its Friends in Hugging Face (2023).
Hình gốc minh họa nguyên lý gọi những mô-đun/ mô hình bên ngoài qua chỉ dẫn của LLM.

## Trang 58/81

KIẾN TRÚC II — LLM LÀ THÀNH PHẦN HỢP NHẤT CỦA HỆ THỐNG
LLM trực tiếp tiếp nhận thông tin đa phương thức và xử lý trong cấu trúc Encoder–LLM–Decoder.
Encoder đa phương thức chuyển tín hiệu thành biểu diễn phù hợp; LLM lõi diễn giải và quyết định; decoder/generator tạo đầu ra đa phương thức.
Khác với bộ điều khiển bằng lệnh chữ, kiến trúc này truyền thông tin đa phương thức trực tiếp dưới dạng đặc trưng/vector.

## Trang 59/81

MỨC PHỔ BIẾN CỦA KIẾN TRÚC II
Bài giảng (dựa trên một khảo sát năm 2023) nêu tỷ lệ xấp xỉ 96% MLLM được phân loại thuộc kiểu Encoder–LLM–Decoder và coi đây là hướng hứa hẹn.
Đây là thống kê có ngữ cảnh lịch sử của tài liệu; không nên tự suy ra vẫn đúng cho toàn bộ hệ thống hiện nay.

## Trang 60/81

ENCODER THỊ GIÁC CHO ẢNH/VIDEO
CLIP-ViT được nêu là một lựa chọn phổ biến trong mô hình kết hợp thị giác và ngôn ngữ.
Ưu điểm:
• Biểu diễn ảnh được căn chỉnh tương đối tốt với không gian văn bản.
• Có thể mở rộng theo số tham số và quy mô dữ liệu.

## Trang 61/81

ENCODER CHO CÁC MODALITY KHÔNG PHẢI THỊ GIÁC
• Âm thanh: HuBERT, Whisper, BEATs.
• Dữ liệu đám mây điểm 3D: Point-BERT.
Những encoder này chuyển dữ liệu thô thành biểu diễn được dùng trong kiến trúc MLLM.

## Trang 62/81

ENCODER ĐA PHƯƠNG THỨC HỢP NHẤT — IMAGEBIND
ImageBind ánh xạ các modality vào một không gian biểu diễn chung được neo theo hình ảnh.
Nếu biểu diễn của các modality căn chỉnh tốt, LLM có thể kết hợp và diễn giải thông tin tốt hơn.
Tham khảo: “ImageBind: One Embedding Space To Bind Them All” (2023).

## Trang 63/81

ENCODER ĐA PHƯƠNG THỨC HỢP NHẤT — LANGUAGEBIND
LanguageBind ánh xạ nhiều modality vào không gian biểu diễn chung được neo theo ngôn ngữ.
Căn chỉnh ngữ nghĩa qua ngôn ngữ nhằm tăng tính liên thông và khả năng hiểu nhiều loại tín hiệu của LLM.
Bài báo: “LanguageBind: Extending Video-Language Pretraining to N-modality by Language-based Semantic Alignment” (2023).

## Trang 64/81

TOKEN HÓA TÍN HIỆU ĐA PHƯƠNG THỨC — SEED
Chủ đề: tokenization, biến dữ liệu đa phương thức thành các đơn vị/token có thể xử lý bằng kiến trúc mô hình.
Ví dụ: SEED — “Planting a SEED of Vision in Large Language Model” (2023).
Hình minh họa cách biểu diễn thông tin thị giác thành token.

## Trang 65/81

TOKEN HÓA ĐA PHƯƠNG THỨC — ANYGPT
AnyGPT là hệ thống mô hình hóa các modality qua chuỗi token rời rạc thống nhất.
Công trình: “AnyGPT: Unified Multimodal LLM with Discrete Sequence Modeling” (2023).
Hình nguồn chỉ ra cách mã hóa và giải mã các loại tín hiệu khác nhau.

## Trang 66/81

TOKEN HÓA ĐA PHƯƠNG THỨC — VIDEOPOET
VideoPoet biểu diễn và sinh video trong một framework mô hình hóa chuỗi token.
Bài báo: “VideoPoet: A Large Language Model for Zero-Shot Video Generation” (2023).
Sơ đồ gốc minh họa pipeline tạo video theo token.

## Trang 67/81

TOKEN HÓA THỊ GIÁC BẰNG BẢNG MÃ (CODEBOOK)
Chuyển ảnh hoặc video thành token rời rạc thuộc một bảng mã (codebook).
Ưu điểm: mô hình có thể dùng cùng khung dự đoán token tiếp theo (autoregressive next-token prediction) để hiểu và sinh tín hiệu đa phương thức.
Cách này được dùng rộng hơn trong tổng hợp ảnh. Các ví dụ: Parti, Muse (song song), MaskGIT (song song).
MLLM liên quan: Gemini, CM3, VideoPoet.

## Trang 68/81

TOKEN HÓA ÂM THANH
Ví dụ: SpeechTokenizer và SoundStream, có thể kết hợp Residual Vector Quantization (RVQ-VAE) để nén và mã hóa tín hiệu âm thanh thành token rời rạc.
Bài báo: “SpeechTokenizer: Unified Speech Tokenizer for Speech Large Language Models” (2023) và “SoundStream: An End-to-End Neural Audio Codec” (2021).

## Trang 69/81

PHÉP CHIẾU ĐẦU VÀO (INPUT-SIDE PROJECTION)
Mục tiêu: đưa biểu diễn ảnh/đa phương thức vào không gian ngữ nghĩa mà LLM có thể dùng.
Các lựa chọn:
• Linear projection: LLaVA, MiniGPT-4, NExT-GPT.
• MLP hai lớp: LLaVA-1.5/NeXT, CogVLM, DeepSeek-VL, Yi-VL.
• Perceiver Resampler: Flamingo, Qwen-VL, MiniCPM-V, LLaVA-UHD.
• Q-Former: BLIP-2, InstructBLIP, VisCPM, VisualGLM.
• C-Abstractor: HoneyBee, MM1.

## Trang 70/81

NHẬN XÉT VỀ PHƯƠNG PHÁP CHIẾU
Những công trình khác nhau đưa ra kết luận khác nhau:
• Nghiên cứu LLaVA cho thấy MLP hai lớp tốt hơn phép chiếu tuyến tính trong thiết lập tương ứng.
• Nghiên cứu MiniGPT-4 cho rằng phép chiếu tuyến tính hữu ích hơn các lớp Q-Former trong thiết lập của họ.
Vì vậy không nên coi một phương án luôn tối ưu; phải xem nhiệm vụ, dữ liệu và đối chứng của từng nghiên cứu.

## Trang 71/81

LLM LÕI (BACKBONE) MÃ NGUỒN MỞ
Bảng trong slide tổng hợp các mô hình theo tham số (tỷ), quy mô dữ liệu (nghìn tỷ token), ngày ra mắt, ngôn ngữ và kiến trúc.
Các tên: Flan-T5, LLaMA, Alpaca, Vicuna, LLaMA-2, GLM, Qwen, Skywork.
Kiến trúc gồm encoder–decoder và decoder-only. Ngôn ngữ ví dụ: tiếng Anh, Pháp, Đức, Trung.
Các thông số là lịch sử theo khảo sát năm 2023, giữ toàn bộ con số trong bảng gốc để đối chiếu.

## Trang 72/81

KẾT NỐI DECODER — CÁCH 1: LỆNH VĂN BẢN RỜI RẠC
Truyền thông tin từ LLM tới decoder qua các token ngôn ngữ/lệnh chữ. Hệ thống: Visual-ChatGPT, HuggingGPT, GPT4Video, MM-REACT, ViperGPT, ModaVerse, Vitron.
Ưu điểm: có baseline hiệu năng tốt, triển khai hiệu quả vì không nhất thiết tinh chỉnh xuyên suốt.
Nhược điểm: không thể tinh chỉnh end-to-end, giới hạn ở những tín hiệu có thể mô tả bằng chữ, nên trần hiệu năng có thể bị hạn chế.

## Trang 73/81

KẾT NỐI DECODER — CÁCH 2: EMBEDDING LIÊN TỤC
LLM chuyển thông điệp tới decoder qua embedding liên tục, ví dụ embedding của token tín hiệu.
Ưu điểm:
• Có thể tinh chỉnh end-to-end, giúp truyền chỉ dẫn hiệu quả hơn.
• Có thể biểu diễn các tín hiệu đa phương thức mà chữ không truyền tải trọn vẹn, ví dụ số lượng đối tượng trong ảnh hoặc quan hệ không gian thị giác.
Ví dụ nghiên cứu: Generating Images with Multimodal Language Models (2023), NExT-GPT (2023).

## Trang 74/81

ĐỐI CHỨNG TRUYỀN THÔNG TIN BẰNG LỆNH CHỮ
Ví dụ NExT-GPT: “Ban đầu có bảy quả táo trên bàn, tôi đã ăn một quả. Bây giờ còn bao nhiêu quả? Hãy sinh một bức tranh mô tả kết quả.”
Trang gốc minh họa việc truyền nhiệm vụ tới bộ sinh ảnh bằng chỉ dẫn văn bản rời rạc.

## Trang 75/81

ĐỐI CHỨNG TRUYỀN THÔNG TIN BẰNG EMBEDDING LIÊN TỤC
Cùng ví dụ: ban đầu bảy quả táo, ăn một quả, hãy tạo ảnh còn sáu quả táo.
Trang gốc minh họa cách LLM chuyển tín hiệu liên tục tới bộ sinh ảnh, đối chiếu với cách dùng lệnh văn bản ở trang 74.

## Trang 76/81

KẾT NỐI DECODER — CÁCH 3: TOKEN CODEBOOK
LLM sinh ID token đặc biệt từ bảng mã, sau đó truyền tới decoder thị giác/đa phương thức; decoder biến chuỗi token thành nội dung.
Ưu điểm:
• Có thể tinh chỉnh end-to-end.
• Biểu diễn tốt hơn nhiều tín hiệu đa phương thức mà văn bản khó truyền tải.
• Phù hợp sinh token đa phương thức theo kiểu tự hồi quy.
Công trình: Unified-IO 2, LVM, AnyGPT và VideoPoet.

## Trang 77/81

SINH VĂN BẢN
LLM vốn hỗ trợ sinh văn bản trực tiếp bằng cách dự đoán token, có thể dùng giải mã theo các kỹ thuật như Beam Search hoặc các quy trình giải mã token phù hợp.
Trang gốc ghi ví dụ “BPE decoding” và Beam Search. Cần phân biệt tokenization BPE với thuật toán chọn chuỗi khi sinh.

## Trang 78/81

SINH ĐA PHƯƠNG THỨC BẰNG MÔ HÌNH KHUẾCH TÁN
• Bộ sinh thị giác (ảnh/video): Image Diffusion, Video Diffusion.
• Bộ sinh âm thanh: Speech Diffusion, Audio Diffusion.
NExT-GPT là ví dụ hệ thống nối LLM với những bộ sinh diffusion chuyên biệt để tạo ra các modality tương ứng.

## Trang 79/81

SINH BẰNG BẢNG MÃ (CODEBOOK)
• Sinh ảnh/video: kết hợp VQ-VAE hoặc VQ-GAN với codebook.
• Sinh âm thanh: SpeechTokenizer hoặc SoundStream với bộ lượng tử hóa vector dư (Residual Vector Quantizer).
Các token được giải mã trở lại âm thanh/hình ảnh. Ví dụ hệ thống: Unified-IO 2.

## Trang 80/81

MINH HỌA VQ-GAN TRONG HỆ THỐNG SINH ẢNH
Slide mô tả VQ-GAN trong một pipeline liên quan tới Stable Diffusion và quá trình sinh bằng codebook.
Ví dụ kích thước biểu diễn: 64 × 64 × 3 hoặc 32 × 32 × 4. Những con số là minh họa trong slide nguồn, không phải thông số bắt buộc của mọi mô hình.

## Trang 81/81

CẢM ƠN!
“Khi nào có câu hỏi?” Kết thúc bài giảng “A Brief Intro to Multimodal LLM” do Hao Fei trình bày.



---

# Chương 09 — Tác nhân giao diện GUI

Nguồn gốc: `documents/chapter9/GUIagent.pdf` · commit `f84c04268794ef94f8949808bbc14ab8636763a0`.

**Nội dung dưới đây là phần chuyển ngữ/diễn giải tiếng Việt theo từng trang slide**, phục vụ đối chiếu với bản gốc; không bảo đảm từng câu chữ trong hình được thay thế.

## Trang 1/43

TÁC NHÂN TỰ CHỦ ĐIỀU KHIỂN GIAO DIỆN ĐỒ HỌA
Graphical User Interface (GUI) Autonomous Agents.
Tác giả: Wu Zheng (吴铮), Khoa Khoa học Máy tính, Đại học Giao thông Thượng Hải.

## Trang 2/43

MỤC LỤC
1. Tổng quan tác nhân tự chủ sử dụng giao diện đồ họa GUI:
• Bối cảnh nghiên cứu; tình hình phát triển; các nhánh kỹ thuật.
2. Chuỗi công nghệ của tác nhân GUI:
• Triển khai tác nhân.
• Giải pháp cho môi trường tĩnh: tinh chỉnh có giám sát (SFT).
• Giải pháp cho môi trường thay đổi: học tăng cường (RL).
• Giải pháp cho tác vụ phức tạp: hệ thống điều phối.
3. An toàn và độ tin cậy của tác nhân GUI:
• Rủi ro an toàn; vấn đề độ tin cậy.

## Trang 3/43

MỤC LỤC
1. Tổng quan tác nhân tự chủ sử dụng giao diện đồ họa GUI:
• Bối cảnh nghiên cứu; tình hình phát triển; các nhánh kỹ thuật.
2. Chuỗi công nghệ của tác nhân GUI:
• Triển khai tác nhân.
• Giải pháp cho môi trường tĩnh: tinh chỉnh có giám sát (SFT).
• Giải pháp cho môi trường thay đổi: học tăng cường (RL).
• Giải pháp cho tác vụ phức tạp: hệ thống điều phối.
3. An toàn và độ tin cậy của tác nhân GUI:
• Rủi ro an toàn; vấn đề độ tin cậy.

## Trang 4/43

BỐI CẢNH: NĂM GIAI ĐOẠN HƯỚNG TỚI AGI
Bài giảng nêu cách phân chia năm cấp độ:
L1 — Chatbots: tương tác bằng ngôn ngữ, hỏi đáp, hội thoại, tìm kiếm (ví dụ GPT-4, DeepSeek-V3).
L2 — Reasoners: suy luận sâu, giải toán/logic (ví dụ o1, DeepSeek-R1).
L3 — Agents: tự chủ hành động, tương tác môi trường, gọi công cụ và thao tác (ví dụ Operator, Deep Research).
L4 — Innovators: đổi mới, phát minh.
L5 — Organizations: phối hợp tổ chức và quản lý.
Chuyển từ “ngôn ngữ” sang “hành động” được tác giả coi là liên kết quan trọng giữa trí tuệ nội dung và trí tuệ hành vi. Phân chia này là khung phân loại trong bài giảng, không phải chứng nhận cấp AGI.

## Trang 5/43

ĐỊNH NGHĨA TÁC NHÂN DỰA TRÊN MÔ HÌNH LỚN
Tác nhân dựa trên LLM hoặc MLLM là hệ thống có thể tự điều hướng quy trình và sử dụng công cụ, sau đó điều chỉnh thao tác dựa trên phản hồi thời gian thực.
Năng lực chính: cảm nhận/hiểu môi trường, lập kế hoạch, quyết định, thực hiện hành động; phản tư, tối ưu và vận hành lâu dài.
Các thành phần: cơ sở tri thức, bộ nhớ kinh nghiệm; công cụ APP/API/hàm; LLM hỗ trợ xử lý chuỗi dài, suy luận CoT và hiểu nhiều loại ý định người dùng.
Sơ đồ gốc thể hiện người dùng ↔ tác nhân ↔ môi trường.

## Trang 6/43

TÁC NHÂN GUI LÀ GÌ?
GUI agent là tác nhân tự chủ tương tác qua giao diện đồ họa: lập kế hoạch, mô phỏng hành động người dùng như nhấn, vuốt, nhập văn bản để tra cứu thông tin và thực thi chức năng.
Trước đây: tác vụ đơn giản, môi trường hẹp, luồng cố định, hệ thống dạng pipeline.
Hiện nay: phạm vi rộng, nhiệm vụ đa dạng và phức tạp hơn, quyết định tự chủ và thích ứng với thay đổi.
Ví dụ đơn giản: hỏi thời tiết, tăng âm lượng, gọi điện, tính toán. Ví dụ phức tạp: đặt lại đơn đồ ăn, mở mã QR, đặt vé tàu theo thời gian và tuyến đường.

## Trang 7/43

GUI AGENT VÀ API AGENT
Tác nhân API: gọi công cụ, API môi trường hoặc function call; đặc trưng là nhanh, ổn định và có cấu trúc rõ.
Tác nhân GUI: nhấn, nhập, vuốt, giữ, nhấp đúp, quay lại; linh hoạt, gần cách người thao tác giao diện.
Nhận xét của bài giảng: API có thể nặng nề hơn ta nghĩ, GUI có thể mong manh hơn ta tưởng. Không có giải pháp tuyệt đối hoàn hảo; sự phát triển của cả hai tạo hướng tương tác người–máy mới.
Nguồn: Zhang và cộng sự, “API Agents vs. GUI Agents: Divergence and Convergence”.

## Trang 8/43

MỤC LỤC
1. Tổng quan tác nhân tự chủ sử dụng giao diện đồ họa GUI:
• Bối cảnh nghiên cứu; tình hình phát triển; các nhánh kỹ thuật.
2. Chuỗi công nghệ của tác nhân GUI:
• Triển khai tác nhân.
• Giải pháp cho môi trường tĩnh: tinh chỉnh có giám sát (SFT).
• Giải pháp cho môi trường thay đổi: học tăng cường (RL).
• Giải pháp cho tác vụ phức tạp: hệ thống điều phối.
3. An toàn và độ tin cậy của tác nhân GUI:
• Rủi ro an toàn; vấn đề độ tin cậy.

## Trang 9/43

HIỆN TRẠNG PHÁT TRIỂN TÁC NHÂN GUI
Giá trị ứng dụng thực tế khiến tác nhân GUI thu hút sự quan tâm rộng trong học thuật và công nghiệp; số công trình tăng nhanh trong những năm gần đây.
Tác nhân được phát triển cho các môi trường trình duyệt web, điện thoại di động và máy tính.
Nguồn: “Large Language Model-Brained GUI Agents: A Survey”.

## Trang 10/43

MỤC LỤC
1. Tổng quan tác nhân tự chủ sử dụng giao diện đồ họa GUI:
• Bối cảnh nghiên cứu; tình hình phát triển; các nhánh kỹ thuật.
2. Chuỗi công nghệ của tác nhân GUI:
• Triển khai tác nhân.
• Giải pháp cho môi trường tĩnh: tinh chỉnh có giám sát (SFT).
• Giải pháp cho môi trường thay đổi: học tăng cường (RL).
• Giải pháp cho tác vụ phức tạp: hệ thống điều phối.
3. An toàn và độ tin cậy của tác nhân GUI:
• Rủi ro an toàn; vấn đề độ tin cậy.

## Trang 11/43

HAI NHÁNH CÔNG NGHỆ CHÍNH
• Tác nhân dựa trên mô hình đóng: sử dụng API của GPT-4o, Qwen-VL-Max, GLM-4v, v.v.; thường kết hợp nhiều agent.
• Tác nhân dựa trên mô hình mở: Blip+T5, Qwen2-VL, LLaVA2, v.v., có thể triển khai mô hình cục bộ.
Các ví dụ nguồn: Mobile-Agent-v2 (hợp tác nhiều tác nhân) và Aguvis (tác nhân GUI dựa trên thị giác).

## Trang 12/43

MOBILE-AGENT-V2 — HỢP TÁC BA TÁC NHÂN
Mobile-Agent là một họ GUI agent dựa trên mô hình đóng.
Phiên bản Mobile-Agent-v2 tổ chức ba tác nhân:
• Agent lập kế hoạch: sử dụng lịch sử thao tác để cập nhật tiến độ, lưu các thông tin trọng tâm trong bộ nhớ.
• Agent quyết định: dựa vào tiến độ và bộ nhớ để tạo thao tác kế tiếp.
• Agent phản tư: quan sát thay đổi màn hình trước/sau thao tác, có thể điều chỉnh hoặc thực hiện lại khi cần.
Bài báo: Wang và cộng sự, “Mobile-Agent-v2”.

## Trang 13/43

APPAGENTX — HỌC TRONG QUÁ TRÌNH THỰC THI
Họ AppAgent cũng là một ví dụ tác nhân GUI dùng mô hình đóng.
AppAgentX có thể học và tối ưu cách hành động trong khi thực hiện tác vụ, ghi nhớ các “nút tắt” (shortcut nodes) để tái sử dụng kinh nghiệm.
Nguồn: Jiang và cộng sự, “AppAgentX: Evolving GUI Agents as Proficient Smartphone Users”.

## Trang 14/43

TÁC NHÂN GUI DỰA TRÊN MÔ HÌNH MỞ
Có thể sử dụng những lộ trình huấn luyện khác nhau:
• Tiền huấn luyện (pretraining).
• Tinh chỉnh chỉ dẫn (instruction tuning/SFT) nhằm học nhận biết thành phần UI và vị trí; cần dữ liệu gán nhãn lớn, ví dụ OS-Atlas, Auto-GLM.
• Bắt chước hành vi mẫu (imitation learning): học từ quỹ đạo thao tác chuyên gia, dễ huấn luyện hơn nhưng lệ thuộc chất lượng nhãn; ví dụ Auto-GUI, AutoAct, ToolLLM.
• Học tăng cường (RL): học từ chuỗi hành động và phần thưởng, khám phá để tối ưu chính sách nhưng tốn chi phí; ví dụ DigiRL, DistRL, Agent Q.
Chuỗi ví dụ tọa độ hành động trên slide gốc được giữ nguyên.

## Trang 15/43

MỤC LỤC
1. Tổng quan tác nhân tự chủ sử dụng giao diện đồ họa GUI:
• Bối cảnh nghiên cứu; tình hình phát triển; các nhánh kỹ thuật.
2. Chuỗi công nghệ của tác nhân GUI:
• Triển khai tác nhân.
• Giải pháp cho môi trường tĩnh: tinh chỉnh có giám sát (SFT).
• Giải pháp cho môi trường thay đổi: học tăng cường (RL).
• Giải pháp cho tác vụ phức tạp: hệ thống điều phối.
3. An toàn và độ tin cậy của tác nhân GUI:
• Rủi ro an toàn; vấn đề độ tin cậy.

## Trang 16/43

TRIỂN KHAI GUI AGENT
Có nhiều dự án nguồn mở hoặc framework có thể triển khai trực tiếp:
• Framework tác nhân dùng mô hình đóng: Mobile-Agent, AppAgent, v.v.
• Backbone nguồn mở chuyên GUI: OS-Atlas, UI-TARS, CogAgent, Aguvis.
Vấn đề thực hành: làm thế nào để các hệ thống đó tương tác với thiết bị thật (điện thoại hoặc máy tính)?

## Trang 17/43

KẾT NỐI MÔ HÌNH VỚI THIẾT BỊ
Android:
• Thiết bị thật: Android Debug Bridge (ADB) gửi lệnh điều khiển từ máy tính qua USB/kết nối đã được cấp quyền.
• Thiết bị ảo: Android Virtual Device (AVD) chạy một hoặc nhiều máy Android mô phỏng.
Máy tính: chuyển hành động agent sang lệnh của thư viện `pyautogui` để điều khiển chuột/bàn phím.
Bảng gốc đối chiếu:
• Click: `adb shell input tap <x> <y>` ↔ `pyautogui.click(x,y)`.
• Chụp màn hình: `adb shell screencap`/`adb pull` ↔ `pyautogui.screenshot(...)`.
• Nhập chữ: `adb shell input text` ↔ `pyautogui.typewrite(...)`.
• Nút HOME: `adb shell input keyevent 3` ↔ `pyautogui.press('home')`.

## Trang 18/43

MỤC LỤC
1. Tổng quan tác nhân tự chủ sử dụng giao diện đồ họa GUI:
• Bối cảnh nghiên cứu; tình hình phát triển; các nhánh kỹ thuật.
2. Chuỗi công nghệ của tác nhân GUI:
• Triển khai tác nhân.
• Giải pháp cho môi trường tĩnh: tinh chỉnh có giám sát (SFT).
• Giải pháp cho môi trường thay đổi: học tăng cường (RL).
• Giải pháp cho tác vụ phức tạp: hệ thống điều phối.
3. An toàn và độ tin cậy của tác nhân GUI:
• Rủi ro an toàn; vấn đề độ tin cậy.

## Trang 19/43

GIẢI PHÁP MÔI TRƯỜNG TĨNH: TINH CHỈNH CÓ GIÁM SÁT (SFT)
Nếu môi trường thật thay đổi ít so với dữ liệu huấn luyện, cách trực quan là SFT theo dữ liệu.
Cách tiếp cận lấy thị giác làm trung tâm: không phụ thuộc trực tiếp API của ứng dụng/OS.
Mỗi bước nhận (i) chỉ dẫn người dùng và (ii) ảnh màn hình hiện tại, rồi xuất hành động cần thực hiện.
Lợi thế được bài giảng nhấn mạnh: tính tổng quát và cấu trúc gọn.
Nguồn: “You Only Look at Screens: Multimodal Chain-of-Action Agents”.

## Trang 20/43

MỤC LỤC
1. Tổng quan tác nhân tự chủ sử dụng giao diện đồ họa GUI:
• Bối cảnh nghiên cứu; tình hình phát triển; các nhánh kỹ thuật.
2. Chuỗi công nghệ của tác nhân GUI:
• Triển khai tác nhân.
• Giải pháp cho môi trường tĩnh: tinh chỉnh có giám sát (SFT).
• Giải pháp cho môi trường thay đổi: học tăng cường (RL).
• Giải pháp cho tác vụ phức tạp: hệ thống điều phối.
3. An toàn và độ tin cậy của tác nhân GUI:
• Rủi ro an toàn; vấn đề độ tin cậy.

## Trang 21/43

MÔI TRƯỜNG GUI LUÔN THAY ĐỔI — ĐỘNG LỰC DÙNG RL
• Bố cục trang web: thứ tự kết quả tìm kiếm có thể thay đổi giữa các lần.
• Cập nhật phần mềm: giao diện/bố cục nút bấm có thể đổi đáng kể.
• Dịp lễ: biểu tượng ứng dụng có thể đổi giao diện đặc biệt.
Câu hỏi: làm thế nào tác nhân GUI thích ứng với biến đổi động khi chỉ học từ ảnh màn hình tĩnh?
Nguồn: DigiRL — Training In-The-Wild Device-Control Agents with Autonomous RL.

## Trang 22/43

DIGIRL — HỌC THEO CHƯƠNG TRÌNH TỪ DỄ ĐẾN KHÓ
DigiRL sử dụng curriculum learning (học theo chương trình): tác nhân GUI học các nhiệm vụ đơn giản trước, rồi chuyển dần sang nhiệm vụ khó nhằm thích ứng với môi trường biến đổi.
Nguồn: Bai và cộng sự, “DigiRL: Training In-The-Wild Device-Control Agents with Autonomous Reinforcement Learning”.

## Trang 23/43

DISTR L — HỌC TĂNG CƯỜNG PHÂN TÁN BẤT ĐỒNG BỘ
DistRL mở rộng DigiRL:
• Sử dụng hạ tầng phân tán bất đồng bộ, tách quá trình thu thập dữ liệu với huấn luyện để nâng hiệu quả.
• Đề xuất phát lại ưu tiên phân tán (distributed prioritized replay), xác định quỹ đạo giá trị cao để ưu tiên học lại.
Nguồn: “DISTRL: An Asynchronous Distributed Reinforcement Learning Framework for On-Device Control Agents”.

## Trang 24/43

GRPO VÀ PHẦN THƯỞNG DỰA TRÊN QUY TẮC
Sau sự chú ý dành cho DeepSeek, tư tưởng RL với phần thưởng được chấm bằng quy tắc và GRPO nhanh chóng được thử trong lĩnh vực tác nhân GUI.
Các nghiên cứu UI-R1, GUI-R1 và InfiGUI-R1 được bài giảng giới thiệu là bằng chứng về tính khả thi của hướng này trong thiết lập tương ứng.
Nguồn: “UI-R1: Enhancing Action Prediction of GUI Agents by Reinforcement Learning”.

## Trang 25/43

MỤC LỤC
1. Tổng quan tác nhân tự chủ sử dụng giao diện đồ họa GUI:
• Bối cảnh nghiên cứu; tình hình phát triển; các nhánh kỹ thuật.
2. Chuỗi công nghệ của tác nhân GUI:
• Triển khai tác nhân.
• Giải pháp cho môi trường tĩnh: tinh chỉnh có giám sát (SFT).
• Giải pháp cho môi trường thay đổi: học tăng cường (RL).
• Giải pháp cho tác vụ phức tạp: hệ thống điều phối.
3. An toàn và độ tin cậy của tác nhân GUI:
• Rủi ro an toàn; vấn đề độ tin cậy.

## Trang 26/43

TÁC VỤ PHỨC TẠP: CẦN HỆ THỐNG ĐIỀU PHỐI
Nhu cầu thực tế đòi hỏi tác nhân GUI ở cấp hệ thống xử lý không chỉ nhiệm vụ đơn giản, có quy tắc rõ mà cả chuỗi nhiệm vụ phức tạp có hoặc không có thứ tự cố định.
Tác giả phân loại chỉ dẫn tổng hợp theo phụ thuộc giữa các tác vụ con:
• Ghép nối (concatenation).
• Chuyển tiếp thông tin (transfer).
• Phân tích sâu (deep analysis).
Nguồn: “Atomic-to-Compositional Generalization for Mobile Agents with A New Benchmark and Scheduling System”.

## Trang 27/43

UI-NEXUS — BENCHMARK TÁC VỤ TỔ HỢP
UI-NEXUS được bài giảng giới thiệu là một benchmark toàn diện dành riêng cho nhiệm vụ tổ hợp của tác nhân GUI.
Các mô hình/framework sẵn có còn gặp khó khăn với phụ thuộc phức tạp, quản lý tiến độ, truyền thông tin giữa bước, kết hợp hành động với suy luận tổng quát.
Các kết quả là kết luận của công trình được dẫn.

## Trang 28/43

ĐIỀU PHỐI TÁC VỤ NHIỀU ỨNG DỤNG
Một agent đơn lẻ có thể gặp khó với phối hợp nhiều tình huống, phụ thuộc phức tạp, ngữ cảnh quá dài và quản lý tiến độ.
Hướng xử lý: xây dựng hệ thống lập lịch/điều phối, chia bài toán thành nhiệm vụ con và xác định trình tự/phụ thuộc.
Ví dụ từ bài giảng: tìm cùng một suất ăn trên hai ứng dụng giao đồ ăn, so sánh giá rồi dừng tại giao diện xác nhận đơn của nền tảng rẻ hơn.
Không phải chỉ dẫn thực thi; ví dụ minh họa phân rã nhiệm vụ.

## Trang 29/43

MỤC LỤC
1. Tổng quan tác nhân tự chủ sử dụng giao diện đồ họa GUI:
• Bối cảnh nghiên cứu; tình hình phát triển; các nhánh kỹ thuật.
2. Chuỗi công nghệ của tác nhân GUI:
• Triển khai tác nhân.
• Giải pháp cho môi trường tĩnh: tinh chỉnh có giám sát (SFT).
• Giải pháp cho môi trường thay đổi: học tăng cường (RL).
• Giải pháp cho tác vụ phức tạp: hệ thống điều phối.
3. An toàn và độ tin cậy của tác nhân GUI:
• Rủi ro an toàn; vấn đề độ tin cậy.

## Trang 30/43

RỦI RO AN TOÀN CỦA TÁC NHÂN GUI
Môi trường triển khai GUI không thể mặc định là đáng tin cậy:
• Chỉ dẫn người dùng có thể bị chèn thao tác độc hại.
• Giao diện/môi trường có thể chứa thông tin gây nhiễu hoặc nội dung được thiết kế để đánh lừa agent.
Nguồn: Ma và cộng sự, “Caution for the Environment: Multimodal Agents are Susceptible to Environmental Distractions”.

## Trang 31/43

TẤN CÔNG TIÊM CHỈ DẪN (PROMPT INJECTION)
Nghiên cứu được trích cho thấy tác nhân GUI có thể mong manh ngay trước những kiểu injection đơn giản.
Ví dụ: chỉ dẫn độc hại ẩn trong chữ nhỏ của điều khoản sử dụng có thể khiến agent gửi dữ liệu người dùng tới website không đáng tin.
Nguồn: “The Obvious Invisible Threat: LLM-Powered GUI Agents’ Vulnerability to Fine-Print Injections”.

## Trang 32/43

TẤN CÔNG BẰNG MIẾNG ẢNH ĐỘC HẠI
Những vùng/pattern hình ảnh được chèn vào màn hình (malicious image patches) cũng có thể làm tác nhân GUI đi sai khỏi hành vi an toàn.
Nguồn: Aichberger và cộng sự, “Attacking Multimodal OS Agents with Malicious Image Patches”.
Slide gốc minh họa loại tấn công trên hình ảnh.

## Trang 33/43

VẤN ĐỀ ĐỘ BỀN VỮNG (ROBUSTNESS)
Các công trình được trích cho rằng nhiều tác nhân GUI hiện hành chưa đạt độ bền phù hợp sử dụng thực tế trong điều kiện bị tấn công.
Tỷ lệ tấn công thành công cao trong các thử nghiệm cho thấy rủi ro đáng kể, đồng thời tạo động lực nghiên cứu giải pháp tăng robustness.
Nguồn: “On the Robustness of GUI Grounding Models Against Image Attack”.

## Trang 34/43

VẤN ĐỀ CĂN CHỈNH AN TOÀN (SAFETY ALIGNMENT)
Tác nhân GUI có thể không từ chối hiệu quả những yêu cầu trái pháp luật, gây hiểu nhầm hoặc độc hại.
Bài báo tham khảo: SAFEARENA — Evaluating the Safety of Autonomous Web Agents.
Kết quả thuộc các tình huống benchmark nguồn, không đồng nghĩa mọi hệ thống đều có tỷ lệ lỗi tương tự.

## Trang 35/43

KẾT QUẢ SAFEARENA ĐƯỢC BÀI GIẢNG NHẤN MẠNH
Trong một số tác nhân được kiểm tra, tỷ lệ hoàn thành nhiệm vụ gây hại thậm chí gần với tỷ lệ hoàn thành nhiệm vụ an toàn.
Điều này cảnh báo rằng “có khả năng thao tác” không đồng nghĩa “có thể phân biệt nhiệm vụ nên/không nên thực hiện”.

## Trang 36/43

MỤC LỤC
1. Tổng quan tác nhân tự chủ sử dụng giao diện đồ họa GUI:
• Bối cảnh nghiên cứu; tình hình phát triển; các nhánh kỹ thuật.
2. Chuỗi công nghệ của tác nhân GUI:
• Triển khai tác nhân.
• Giải pháp cho môi trường tĩnh: tinh chỉnh có giám sát (SFT).
• Giải pháp cho môi trường thay đổi: học tăng cường (RL).
• Giải pháp cho tác vụ phức tạp: hệ thống điều phối.
3. An toàn và độ tin cậy của tác nhân GUI:
• Rủi ro an toàn; vấn đề độ tin cậy.

## Trang 37/43

ĐỘ TIN CẬY: VẤN ĐỀ NGOÀI PHÂN BỐ (OOD)
Các mô hình GUI được huấn luyện trên dữ liệu tĩnh có thể gặp Out-of-Distribution khi dùng ở thế giới thật.
• Internalization-OOD: mô hình học trên một hệ điều hành không đủ khả năng thao tác ở hệ điều hành khác.
• Extrapolation-OOD: mô hình học từ dữ liệu tĩnh không thích ứng tốt với ứng dụng hoặc công cụ mới.
Nguồn: GEM — Gaussian Embedding Modeling for OOD Detection for GUI Agents.

## Trang 38/43

PHÁT HIỆN OOD TRÊN GUI CÓ THÁCH THỨC RIÊNG
• Không gian ngữ nghĩa đầu vào phức tạp: agent phải hiểu cả bố cục màn hình đa dạng và các chỉ dẫn người dùng khác nhau.
• Môi trường thật thay đổi liên tục: giao diện ứng dụng và web thường xuyên cập nhật.
Ví dụ nguồn: một ảnh màn hình có thể tạo 40 vùng đối tượng; giao diện ứng dụng thương mại điện tử thay đổi theo chiến dịch lễ hội.

## Trang 39/43

THỰC THI QUÁ MỨC (OVER-EXECUTION)
Khi gặp nhiệm vụ vượt khả năng, tác nhân nên dừng để tránh hành động thiếu tin cậy.
Trong thực tế, tác nhân quá tự động vẫn có thể tiếp tục thao tác dù đã đi vào vùng không chắc chắn. Phát hiện đúng lúc để yêu cầu người dùng can thiệp có thể giảm rủi ro.
Nguồn: OS-Kairos và Universal Confidence Integration Framework for Adaptive Interaction.

## Trang 40/43

CƠ CHẾ QUAY LÙI (ROLLBACK)
Một khi agent đã đi sai hướng, các bước tiếp theo dễ tiếp tục sai.
Cơ chế rollback thích hợp cho phép khôi phục một trạng thái trước đó, tránh tiếp diễn chuỗi hành động không đáng tin.
Nguồn: Zhang và cộng sự, “Enhancing Web Agents with Explicit Rollback Mechanisms”.

## Trang 41/43

CHỈ DẪN MƠ HỒ (AMBIGUOUS TASKS)
Người dùng đôi lúc cung cấp yêu cầu thiếu chi tiết quan trọng.
Khi nhiệm vụ mơ hồ, tác nhân khó bảo đảm tính đúng đắn nếu tự ý suy đoán.
Khả năng chủ động đặt câu hỏi làm rõ (follow-up questions) giúp tăng độ tin cậy của tác nhân GUI.
Nguồn: “Navi-plus: Managing Ambiguous GUI Navigation Tasks with Follow-up Questions”.

## Trang 42/43

MỤC LỤC
1. Tổng quan tác nhân tự chủ sử dụng giao diện đồ họa GUI:
• Bối cảnh nghiên cứu; tình hình phát triển; các nhánh kỹ thuật.
2. Chuỗi công nghệ của tác nhân GUI:
• Triển khai tác nhân.
• Giải pháp cho môi trường tĩnh: tinh chỉnh có giám sát (SFT).
• Giải pháp cho môi trường thay đổi: học tăng cường (RL).
• Giải pháp cho tác vụ phức tạp: hệ thống điều phối.
3. An toàn và độ tin cậy của tác nhân GUI:
• Rủi ro an toàn; vấn đề độ tin cậy.

## Trang 43/43

CẢM ƠN!
Kết thúc bài giảng về tác nhân GUI, phương pháp triển khai, SFT, RL, điều phối và an toàn/độ tin cậy.



---

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

TROJANRAG — BACKDOOR TRONG HỆ TRUY XUẤT BỔ SUNG
TrojanRAG có thể thao túng đầu ra LLM thông qua nguồn dữ liệu truy xuất trong khi các truy vấn sạch vẫn hoạt động.
Các tình huống trong slide: đánh lừa thông tin thực, lan truyền nội dung sai/độc hại và gây lỗi an toàn qua câu hỏi không phù hợp.
Các điểm kiểm soát: nguồn tri thức bị đầu độc, retriever có backdoor, trigger được cài, RAG được kết nối với LLM và cơ chế kích hoạt trong ngữ cảnh phù hợp.
Bài báo: “TrojanRAG: Retrieval-Augmented Generation Can Be Backdoor Driver in Large Language Models”, arXiv:2405.13401. Các prompt cụ thể được giữ nguyên trên slide gốc làm dữ liệu nghiên cứu, không được thực thi.

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



---

# Chương 11 — Căn chỉnh RLHF/PPO

Nguồn gốc: `documents/chapter11/RLHF.pdf` · commit `f84c04268794ef94f8949808bbc14ab8636763a0`.

**Nội dung dưới đây là phần chuyển ngữ/diễn giải tiếng Việt theo từng trang slide**, phục vụ đối chiếu với bản gốc; không bảo đảm từng câu chữ trong hình được thay thế.

## Trang 1/24

THỰC HÀNH CĂN CHỈNH MÔ HÌNH NGÔN NGỮ LỚN (LLM ALIGNMENT)
Đại học Giao thông Thượng Hải, Khoa Khoa học Máy tính.
Tác giả: Dong Lingzhong (董凌众).

## Trang 2/24

SỰ MONG MANH CỦA CĂN CHỈNH AI
Theo cách dẫn nhập của bài giảng, độ mong manh của việc căn chỉnh AI có thể lớn hơn dự kiến. Một hệ thống AI tưởng như đã tuân theo các ràng buộc an toàn vẫn có thể tồn tại hành vi không mong muốn. Chỉ một thay đổi tinh chỉnh hẹp đôi khi cũng làm mô hình lệch hành vi trên phạm vi rộng.
Tham khảo: Betley và cộng sự, “Emergent Misalignment: Narrow finetuning can produce broadly misaligned LLMs”, arXiv:2502.17424 (2025).
Đây là kết quả được bài giảng trích dẫn, không phải khẳng định mọi mô hình đều có đặc điểm này.

## Trang 3/24

MỤC LỤC
01. Tổng quan: làm thế nào bảo đảm máy móc thực hiện đúng ý định của con người?
02. RLHF: từ học tăng cường đến học từ phản hồi con người.
03. PPO: từ gradient chính sách (policy gradient) đến tối ưu chính sách gần (proximal policy optimization).
04. Những nghiên cứu gần đây: tín hiệu an toàn tường minh và nhận dạng các lớp an toàn.

## Trang 4/24

CÂU HỎI CỦA NHÀ TIÊN PHONG ĐIỀU KHIỂN HỌC
Bài giảng dẫn lời Norbert Wiener (trên slide ghi Robert Weiner, 1960): khi ta dùng một cơ cấu máy móc để thực hiện mục đích mà không thể can thiệp hiệu quả vào hoạt động của nó, cần chắc chắn mục đích đặt vào máy đúng là điều con người thật sự muốn.
Câu hỏi trung tâm: làm sao để máy luôn hành động phù hợp với ý định của con người? Trích dẫn tiếng Anh nguyên văn được giữ trên slide gốc để đối chiếu.

## Trang 5/24

CĂN CHỈNH LLM VỚI GIÁ TRỊ CỦA CON NGƯỜI
Có nhiều mức căn chỉnh khác nhau:
• Phù hợp văn hóa: tôn trọng văn hóa của quốc gia và khu vực.
• Phù hợp đạo đức, tình lý: đáp ứng các chuẩn mực ứng xử.
• Phù hợp pháp luật: tuân thủ quy định hiện hành.
• Phù hợp sự thật: tôn trọng dữ kiện và logic.
Bài giảng phân biệt căn chỉnh ở tầng giá trị với căn chỉnh ở tầng an toàn. Các tiêu chí không thể quy giản thành một nhãn PASS duy nhất.

## Trang 6/24

CHUYỂN SANG PHẦN 02 — RLHF
Từ học tăng cường (reinforcement learning) đến học tăng cường từ phản hồi con người (Reinforcement Learning from Human Feedback, RLHF).
Các nội dung khác: tổng quan căn chỉnh; PPO; tín hiệu an toàn tường minh và lớp an toàn.

## Trang 7/24

HỌC TĂNG CƯỜNG (REINFORCEMENT LEARNING, RL)
Học tăng cường là một hệ phương pháp trong học máy để mô tả và giải bài toán tác nhân (agent) tương tác với môi trường (environment), học một chính sách (policy) nhằm tối đa hóa phần thưởng (reward) hoặc đạt mục tiêu cụ thể.

## Trang 8/24

HAI ĐỐI TƯỢNG TƯƠNG TÁC TRONG RL
• Tác nhân (Agent): nhận biết trạng thái (State) của môi trường, dựa trên tín hiệu phần thưởng (Reward) để chọn hành động (Action), học trong quá trình tương tác nhằm tăng lợi ích dài hạn.
• Môi trường (Environment): nhận chuỗi hành động của tác nhân, đánh giá tác động của chúng, chuyển kết quả thành một tín hiệu có thể định lượng và phản hồi cho tác nhân.

## Trang 9/24

CÁC KHÁI NIỆM CƠ BẢN CỦA HỌC TĂNG CƯỜNG
• Chính sách (Policy): quy định cách chọn hành động tại thời điểm t; ánh xạ trạng thái môi trường sang hành động hoặc phân bố hành động.
• Hàm phần thưởng (Reward Function): tính tín hiệu lợi ích do môi trường trả về ở mỗi bước.
• Hàm giá trị (Value Function): kỳ vọng tổng phần thưởng tích lũy trong tương lai khi bắt đầu ở một trạng thái.
• Mô hình môi trường (Environment Model): mô phỏng cách môi trường phản ứng, giúp suy đoán ảnh hưởng của hành động.

## Trang 10/24

CHÍNH SÁCH (POLICY)
Chính sách quy định cách tác nhân chọn hành động ở thời điểm t, là ánh xạ từ trạng thái của môi trường sang hành động hoặc phân bố xác suất trên các hành động.
Hình gốc minh họa vai trò chính sách trong quá trình tương tác giữa tác nhân và môi trường.

## Trang 11/24

HÀM GIÁ TRỊ (VALUE FUNCTION)
Hàm giá trị đánh giá “tốt” theo góc nhìn dài hạn. Giá trị của một trạng thái là kỳ vọng tổng phần thưởng tích lũy mà tác nhân nhận được trong tương lai khi bắt đầu từ trạng thái đó và làm theo một chính sách.

## Trang 12/24

RLHF: HỌC TỪ PHẢN HỒI CỦA CON NGƯỜI
Trong học tăng cường truyền thống, có môi trường và tín hiệu phần thưởng được xác định. Với tác vụ ngôn ngữ, không phải lúc nào cũng có thể viết trực tiếp hàm phần thưởng đúng cho mọi câu trả lời; thay vào đó thường có các ví dụ, thứ tự ưu tiên hoặc nhận xét của con người/chuyên gia.
Câu hỏi: làm sao chuyển phản hồi này thành tín hiệu dùng được cho RL?
Hình nguồn giới thiệu quy trình xây dựng mô hình ngôn ngữ của OpenAI trong bối cảnh RLHF.

## Trang 13/24

RLHF: XÂY DỰNG MÔ HÌNH PHẦN THƯỞNG
Sử dụng dữ liệu do con người gán nhãn để huấn luyện mô hình phần thưởng (Reward Model). Mô hình này xấp xỉ các sở thích/chuẩn đánh giá của người gán nhãn, tức là cố gắng học những yếu tố khiến một phản hồi được ưa thích hơn phản hồi khác.
Sau khi có tín hiệu phần thưởng có thể tính được, ta có thể dùng thuật toán học tăng cường để tìm chính sách tối ưu hơn theo tín hiệu đó.
Lưu ý: phần thưởng ước lượng không đồng nghĩa với chân lý hay giá trị con người đầy đủ.

## Trang 14/24

CHUYỂN SANG PHẦN 03 — PPO
Từ phương pháp gradient chính sách (policy gradient) sang tối ưu chính sách gần (Proximal Policy Optimization, PPO).
Bài giảng tiếp tục giới thiệu RL, actor–critic và sự khác nhau giữa cập nhật chính sách trực tiếp với tối ưu hàm giá trị.

## Trang 15/24

KẾT HỢP HỌC TĂNG CƯỜNG VÀ HỌC SÂU
Theo cách học chính sách, RL có thể chia thành:
• Value-based: học hàm giá trị rồi suy ra chính sách; ví dụ Q-Learning và Deep Q Network (DQN). DQN dùng bộ nhớ phát lại kinh nghiệm (experience replay) và mạng mục tiêu (target network).
• Policy-based: học trực tiếp chính sách; ví dụ REINFORCE và Policy Gradient.
• Actor–Critic: kết hợp thành phần chọn hành động (actor) với thành phần đánh giá (critic).
Hình nguồn liệt kê Q-Learning, PPO và REINFORCE.

## Trang 16/24

GRADIENT CHÍNH SÁCH (POLICY GRADIENT, PG)
Value-based: so sánh giá trị kỳ vọng Q của các hành động a1, a2, a3 và chọn hành động có Q lớn nhất.
Policy-based: dùng mạng actor để tính xác suất π(a|s) của hành động tại trạng thái s rồi chọn hành động theo phân bố này.
Khác với Q-learning hay DQN, mạng PG không trực tiếp xuất giá trị Q cho mỗi hành động mà xuất xác suất chọn hành động; cách này hỗ trợ tốt hơn trong nhiều không gian hành động liên tục.

## Trang 17/24

HỌC GRADIENT CHÍNH SÁCH TỪ CÁC QUỸ ĐẠO
Trong thí nghiệm, actor tương tác với môi trường để thu các mẫu quỹ đạo (trajectory/episode), tức nhiều cặp (s, a) biểu diễn hành động a được thực hiện ở trạng thái s, cùng phần thưởng của quỹ đạo R(τ).
Dữ liệu mẫu được dùng để tính gradient và cập nhật tham số θ theo hướng tăng phần thưởng kỳ vọng. Hình gốc thể hiện các quỹ đạo τ1, τ2 và công thức cập nhật θ ← θ + η∇R̄(θ).

## Trang 18/24

NGUYÊN LÝ THUẬT TOÁN PPO
Một khó khăn của PG trực tiếp: sau khi cập nhật chính sách, thường phải thu thập dữ liệu tương tác mới trước lượt tối ưu tiếp theo.
PPO dựa trên ý tưởng lấy mẫu theo tầm quan trọng (importance sampling): dùng dữ liệu từ phân bố hành vi gần với chính sách hiện hành để thực hiện các lượt cập nhật có kiểm soát, miễn hai phân bố không quá khác biệt.
Trong mô hình actor–critic, actor tương tác để thu mẫu và cập nhật chính sách; critic đánh giá chất lượng hành động nhằm hỗ trợ việc tính tín hiệu tối ưu.

## Trang 19/24

PPO KẾT HỢP ACTOR–CRITIC
Tác nhân có hai phần:
• Actor: tương tác với môi trường và thu các mẫu trạng thái/hành động; được cập nhật bằng gradient mục tiêu PPO.
• Critic: ước lượng mức tốt/xấu hoặc giá trị của những hành động, hỗ trợ đánh giá và giảm phương sai tín hiệu học.
Hình minh họa trên trang gốc mô tả hai chức năng này.

## Trang 20/24

CHUYỂN SANG PHẦN 04 — HƯỚNG NGHIÊN CỨU MỚI
• Tín hiệu an toàn tường minh (Explicit Safety Signals).
• Nhận diện lớp an toàn (Safety Layer Identification).
Câu hỏi chung: liệu có thể kiểm tra và củng cố hành vi an toàn bằng tín hiệu, cơ chế hoặc biểu diễn nội bộ của mô hình?

## Trang 21/24

TÍN HIỆU AN TOÀN TƯỜNG MINH
Câu hỏi: có thể xem năng lực nhận diện yêu cầu độc hại của mô hình như bài toán phân loại nhị phân ngầm định không?
Giải pháp được bài giảng trích:
• Khi huấn luyện, biến việc phân loại an toàn thành nhiệm vụ tường minh: theo cảm hứng BERT, thêm token [CLS] vào đầu chuỗi và đầu phân loại (classification head) để dự đoán đầu vào/ngữ cảnh là độc hại hay lành tính.
• Khi triển khai, sử dụng cơ chế chú ý có chiến lược (Strategic Attention Mechanism) kết hợp giải mã có chiến lược (Strategic Decoding Strategy).
Tham khảo: Li và Kim, “Safety alignment can be not superficial with explicit safety signals”.

## Trang 22/24

LIỆU CÁC LỚP AN TOÀN CÓ THỰC SỰ TỒN TẠI?
Phương pháp kiểm tra được trình bày:
• So sánh vector biểu diễn của đầu vào bình thường và đầu vào độc hại tại từng lớp.
• Tạo nhiều mẫu và tính giá trị trung bình.
• Đo bằng độ tương đồng cosine và chênh lệch góc.
• Nếu tại một lớp độ tương đồng giảm mạnh, góc tăng rõ, đó có thể là tín hiệu mô hình bắt đầu phân biệt rủi ro an toàn.
Ví dụ gốc đối chiếu câu hỏi bình thường về mùa sau mùa xuân với một yêu cầu nguy hiểm mà mô hình từ chối.
Bài báo đề xuất ba giai đoạn bên trong LLM đã căn chỉnh: (i) nhận diện câu ban đầu, (ii) phát hiện ý định độc hại, (iii) phân tích và hiểu ngữ nghĩa. Tham khảo Li và cộng sự, arXiv:2408.17003.

## Trang 23/24

TÀI LIỆU THAM KHẢO
[1] Bài viết phổ biến về tính mong manh của việc căn chỉnh LLM có chi phí hàng trăm triệu USD.
[2] Betley và cộng sự (2025), Emergent Misalignment: Narrow finetuning can produce broadly misaligned LLMs.
[3] Bài viết giới thiệu RLHF và PPO của ChatGPT.
[4] Zhang Qi, Gui Tao, Zheng Rui, Huang Xuanjing (2023), Lý thuyết và thực hành LLM — https://intro-llm.github.io/.
[5] Li & Kim, Safety alignment can be not superficial with explicit safety signals.
[6] Li và cộng sự (2024), Safety layers in aligned large language models: The key to LLM security.
Xem đầy đủ tiêu đề, đường dẫn và thông tin xuất bản ở slide gốc.

## Trang 24/24

CẢM ƠN!
Kết thúc bài giảng về căn chỉnh mô hình, RLHF, PPO và các hướng nghiên cứu an toàn. Đại học Giao thông Thượng Hải.

