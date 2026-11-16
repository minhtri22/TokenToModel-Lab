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


TỔNG QUAN MA TRẬN PHƯƠNG THỨC VÀ CHỨC NĂNG MLLM
Nguồn dùng bốn cột phương thức cùng ngôn ngữ: IMAGE (ảnh), VIDEO, AUDIO (âm thanh), 3D; hai nhóm hàng chính: chỉ nhận biết đầu vào (input-side perceiving) và nhận biết + tạo sinh (perceiving + generating). Dấu “–” trong bảng nghĩa là không liệt kê mô hình ở ô đó, không phải chứng minh lĩnh vực bất khả thi.
NHÓM CHỈ NHẬN BIẾT, HÀNG TỔNG QUÁT:
• IMAGE: Flamingo, Kosmos-1, BLIP-2, mPLUG-Owl, MiniGPT-4, LLaVA, InstructBLIP, VPGTrans, CogVLM, Monkey, Chameleon, Otter, Qwen-VL, GPT-4V, SPHINX, Yi-VL, Fuyu...
• VIDEO: VideoChat, Video-ChatGPT, Video-LLaMA, PandaGPT, MovieChat, Video-LLaVA, LLaMA-VID, Momentor...
• AUDIO: AudioGPT, SpeechGPT, VIOLA, AudioPaLM, SALMONN, MU-LLaMA...
• 3D: 3D-LLM, 3D-GPT, LL3DA, SpatialVLM, PointLLM, Point-Bind...
NHÓM NHẬN BIẾT ĐỘ PHÂN GIẢI PIXEL:
• IMAGE [Pixel-wise]: GPT4RoI, LION, MiniGPT-v2, NExT-Chat, Kosmos-2, GLaMM, LISA, DetGPT, Osprey, PixelLM...
• VIDEO [Pixel-wise]: PG-Video-LLaVA, Merlin, MotionEpic...
• AUDIO / 3D: bảng đánh dấu “–”.
HÀNG VIDEO BỔ SUNG: Video-LLaVA, Chat-UniVi, LLaMA-VID; bảng để trống AUDIO / 3D.
HÀNG ĐA PHƯƠNG THỨC BỔ SUNG: Panda-GPT, Video-LLaMA, AnyMAL, Macaw-LLM, Gemini, VideoPoet, ImageBind-LLM, LLMBind, LLaMA-Adapter...; AUDIO / 3D không có tên ở cột riêng của hàng này.
NHÓM NHẬN BIẾT VÀ TẠO SINH:
• IMAGE: GILL, EMU, MiniGPT-5, DreamLLM, LLaVA-Plus, InternLM-XComposer2, SEED-LLaMA, LaVIT, Mini-Gemini...
• VIDEO: GPT4Video, Video-LaVIT, VideoPoet...
• AUDIO: AudioGPT, SpeechGPT, VIOLA, AudioPaLM...
• 3D: dấu “–”.
• HÀNG [Pixel-wise]: Vitron; những ô không liệt kê được giữ là “–”.
• Hàng phối hợp phương thức: NExT-GPT, Unified-IO 2, AnyGPT, CoDi-2, Modaverse, ViT-Lens...; 3D dấu “–”.
Giữ đúng nhóm cột/hàng như PDF nguồn trang 7; danh sách ví dụ này là nội dung slide, không hàm ý từng mô hình hỗ trợ mọi tác vụ.


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


MÔ HÌNH ĐA PHƯƠNG THỨC NHẬN BIẾT ÂM THANH
Các mô hình được liệt kê trên slide: AudioGPT, SpeechGPT, VIOLA, AudioPaLM, SALMONN, MU-LLaMA.
SƠ ĐỒ LUỒNG: đầu vào gồm “Text” (văn bản) và “Audio” (âm thanh). Một bộ mã hóa âm thanh ngoài (external encoder) chuyển tín hiệu âm thanh thành đặc trưng mà LLM có thể hiểu; các đặc trưng này được đưa vào LLM, mô hình giải thích kết hợp với chỉ dẫn bằng văn bản và sinh đáp án ở dạng “Text”.
Các vùng mây của sơ đồ minh họa các loại tín hiệu: sound (âm thanh môi trường), speech (lời nói), music (âm nhạc), cùng biểu tượng nội dung âm thanh khác.
Chú giải tiếng Anh trong ảnh: “Encode input audio signals with external encoders, generating LLM-understandable signal features, feeding into LLM, which then interprets the audio based on the input text instructions and produces a textual response.” Bản Việt: “Mã hóa tín hiệu âm thanh đầu vào bằng bộ mã hóa bên ngoài để tạo đặc trưng LLM hiểu được; đưa chúng vào LLM; LLM diễn giải âm thanh theo chỉ dẫn văn bản đầu vào và tạo phản hồi bằng chữ.”
Slide dẫn các nghiên cứu AudioGPT, SpeechGPT, VioLA, AudioPaLM và SALMONN (2023).


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

MLLM HIỂU VÙNG ẢNH CHI TIẾT ĐẾN MỨC PIXEL
Nhiệm vụ trên slide: người dùng đưa một ảnh, có thể chỉ định vùng quan tâm; LLM trả lời dựa trên việc hiểu nội dung thị giác, đồng thời liên kết câu trả lời với vùng hay pixel cụ thể của ảnh (visual grounding).
Các mô hình được liệt kê: GPT4RoI, NExT-Chat, MiniGPT-v2, Shikra, Kosmos-2, GLaMM, LISA, DetGPT, Osprey, PixelLM, LION và các công trình khác.
Sơ đồ ở giữa có luồng từ đầu vào người dùng (văn bản và ảnh, có thể kèm vùng) qua mô hình ngôn ngữ lớn tới đầu ra gồm văn bản/ảnh/vùng. Các bài báo tham khảo [1]–[10] ở bên dưới tên các mô hình, chủ yếu công bố năm 2023.
Đây là danh mục khả năng và ví dụ tham khảo trong tài liệu nguồn; slide không chứng minh mọi mô hình hỗ trợ tất cả kiểu tác vụ trên.

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
