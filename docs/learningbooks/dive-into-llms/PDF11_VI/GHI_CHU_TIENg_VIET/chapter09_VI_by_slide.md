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
