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


POLICY GRADIENT — LẤY MẪU QUỸ ĐẠO VÀ CẬP NHẬT THAM SỐ
Actor tương tác với môi trường (environment), thu nhiều quỹ đạo τ¹, τ², ... (episode sample/trajectory). Trong một quỹ đạo có các cặp trạng thái–hành động (s₁¹,a₁¹), (s₂¹,a₂¹), ... và phần thưởng tổng quỹ đạo R(τ¹); tương tự với τ² và R(τ²). Các mẫu được đưa vào quá trình huấn luyện để cập nhật tham số θ của chính sách πθ.
CÔNG THỨC 1 — BƯỚC CẬP NHẬT MÔ HÌNH: θ ← θ + η ∇R̄θ. η là bước học (learning rate); ∇R̄θ là gradient của phần thưởng kỳ vọng.
CÔNG THỨC 2 — ƯỚC LƯỢNG POLICY GRADIENT TRÊN HÌNH:
∇R̄θ ≈ (1/N) Σ[n=1..N] Σ[t=1..Tₙ] R(τⁿ) ∇ log Pθ(aₜⁿ | sₜⁿ).
Ở đây N là số quỹ đạo lấy mẫu, Tₙ là số bước trong quỹ đạo n, Pθ(a|s) là xác suất chọn hành động a tại trạng thái s theo chính sách θ, còn R(τⁿ) là phần thưởng của quỹ đạo.
Mũi tên “Data Sample” nối các quỹ đạo với bộ ước lượng gradient; mũi tên “Update Model” biểu thị dùng gradient đó cập nhật tham số.
Công thức được chép nghĩa từ hình nguồn: nó mô tả bộ ước lượng REINFORCE đơn giản mà slide trình bày, không tự bổ sung baseline hay advantage chưa xuất hiện.


Trong thuật toán Policy Gradient (PG), actor tương tác với môi trường và thu các quỹ đạo (episode/trajectory). Từ mỗi quỹ đạo lấy những cặp (s, a), tức hành động a xảy ra trong trạng thái s, cùng phần thưởng R(τ).
Hình cho thấy hai quỹ đạo τ₁ và τ₂, mỗi quỹ đạo chứa nhiều cặp trạng thái–hành động và phần thưởng tương ứng. Dữ liệu mẫu được dùng để cập nhật các tham số θ của chính sách π_θ.
Công thức cập nhật trên sơ đồ: θ ← θ + η∇R̄(θ). Ở đây η là hệ số học, ∇R̄(θ) biểu thị gradient của phần thưởng trung bình/kỳ vọng theo tham số θ. Mũi tên hướng tăng tương ứng với tối đa hóa phần thưởng, không phải giảm gradient của hàm mất mát.

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
