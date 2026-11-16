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

