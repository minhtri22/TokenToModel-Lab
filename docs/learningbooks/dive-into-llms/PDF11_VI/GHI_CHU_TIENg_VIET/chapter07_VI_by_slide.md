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

GIẤU TIN VĂN BẢN SINH BẰNG LLM — CHỌN NEXT TOKEN
Theo nguồn, văn bản do mô hình sinh là dữ liệu tuần tự (serialized data). Khi nhận ngữ cảnh phía trước và các tham số sinh, mô hình tạo bảng logits dự báo token tiếp theo, có token ID sắp theo xác suất từ cao đến thấp.
Ở cách sinh thông thường, mô hình lấy mẫu ngẫu nhiên một trong n token ứng viên (theo các tham số giải mã), chọn làm token kế tiếp rồi lặp lại.
Ở giấu tin tạo sinh, quy tắc mã hóa được đặt vào quá trình chọn next token: thay vì chọn hoàn toàn theo cách thông thường, mô hình can thiệp vào sự lựa chọn token theo một quy tắc đã biết để đưa bit/thông tin ẩn vào chuỗi văn bản tạo ra.
SƠ ĐỒ minh họa Alice gửi plaintext; mô hình mã hóa thành ciphertext và cover text; người nhận Bob dùng bộ giải mã khôi phục thông điệp. Kênh công khai chỉ thấy cover text, người quan sát không biết khóa/quy tắc khó phát hiện thông điệp.
Nghiên cứu được dẫn trên slide: Yang và cộng sự (RNN-stega, 2018), Tang và cộng sự (2024) và Yang và cộng sự (VAE-Stega, 2020).

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

Ý NGHĨA VÀ HƯỚNG PHÁT TRIỂN CỦA GIẤU TIN VỚI LLM
• ƯU THẾ: tận dụng chất lượng mô hình để tạo bản văn tự nhiên, nhờ đó nội dung giấu tin khó bị nhận ra.
• KHÔNG GIAN MÃ HÓA: mỗi phương pháp phụ thuộc cấu trúc mã; phát minh cấu trúc không gian mã mới có thể tạo cách giấu tin mới.
• MỞ RỘNG SANG VẬT MANG KHÁC: giấu tin bằng ngôn ngữ sinh về bản chất là “mã hóa tuần hoàn dữ liệu tuần tự”. Tác giả gợi ý có thể chuyển sang vật mang khác như DNA, kết hợp dụng cụ và mô hình để mã hóa dữ liệu trong chuỗi DNA. Slide lấy ví dụ giả định giấu thông tin trong một chai nước, một số tế bào hoặc một vài sợi tóc; đây là viễn cảnh nghiên cứu, không phải quy trình thí nghiệm.
• KẾT HỢP THỦY VÂN: watermark LLM có thể tương tác với giấu tin. Ví dụ watermark KGW cũng áp đặt ràng buộc lên việc chọn next token trong lúc suy luận.
• AN TOÀN NỘI DUNG: phân tích giấu tin (steganalysis) có thể hỗ trợ đánh giá và lọc nội dung truyền thông. Slide xem một số lời xúc phạm ẩn ý, không kích hoạt từ khóa như một dạng che giấu ngữ nghĩa, và gợi ý sử dụng AI phát hiện để bảo vệ không gian mạng.
Đây là các dự đoán và phân tích trong bài giảng, không phải bằng chứng mọi hệ thống giấu tin đều an toàn.

