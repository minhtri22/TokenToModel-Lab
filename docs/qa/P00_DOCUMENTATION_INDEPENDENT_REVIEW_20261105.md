# P00 — Kiểm tra đối chiếu độc lập tài liệu sau hợp nhất

**Ngày:** 05/11/2026  
**Mốc đối chứng:** `8df22f5f29e645b2becff936daccbd32ac780661`  
**Nhánh được kiểm tra:** `docs/p00-post-merge-audit-vietnamese-20261105`  
**Mã công việc:** `TTM_P00_DOCUMENTATION_SECOND_PASS_REVIEW`

## Phương pháp và phạm vi

Kiểm tra riêng biệt sau vòng kiểm tra tĩnh ban đầu: lấy trực tiếp tập thay đổi GitHub, đọc các tài liệu cốt lõi, đối chiếu nội dung với commit gốc P00 và biên bản được đọc lại từ máy Windows qua RemoteMCP. Không chạy lại mô hình, không ghi vào máy Windows, không tạo/xóa worktree.

Đây là **đối chiếu kỹ thuật lần hai** dựa vào nguồn và kiểm tra bất biến tách khỏi danh sách 13 tiêu chí kiểm tra tĩnh ban đầu. Không tự nhận đã có người đánh giá bên thứ ba hoặc kiểm tra toàn bộ quyển sách.

## Bảng 15 tiêu chí

| STT | Cổng kiểm tra | Kết quả | Giải thích |
|---:|---|---|---|
| 1 | Commit gốc GitHub chính xác | PASS | So nhánh tài liệu với commit hợp nhất P00 đã khóa |
| 2 | Nhánh chỉ đi trước mốc gốc | PASS | Không có lịch sử Git bị lệch khỏi mốc đã duyệt |
| 3 | PR #2 còn mở dạng nháp tại thời điểm kiểm tra | PASS | Không tự nhận đã hợp nhất khi chưa có quyết định |
| 4 | Mọi tệp thay đổi đều là Markdown | PASS | Chỉ cập nhật hồ sơ và tài liệu |
| 5 | Không đổi mã nguồn, cấu hình, script | PASS | Không tạo kết quả mô hình mới |
| 6 | Không sửa biên bản QA gốc, nhật ký chạy thô | PASS | Giữ nguồn chứng cứ bất biến |
| 7 | Lịch sử `lineage.md` chỉ ghi bổ sung | PASS | Nội dung cũ vẫn là tiền tố nguyên trạng |
| 8 | Các mốc `L0000–L0005` được bảo toàn | PASS | Không xóa hoặc viết lại kết luận cũ |
| 9 | Mốc `L0006` có trong nhánh | PASS | Có ghi nhận kiểm toán sau hợp nhất |
| 10 | Bảng đo có ngưỡng và giới hạn P00 | PASS | Các phép đo `2e-5`, `1e-6`, loss mẫu được giải thích |
| 11 | Có quy định tiếng Việt và thuật ngữ trong ngoặc | PASS | `docs/TERMINOLOGY_VI.md` |
| 12 | Ranh giới làm việc được khóa đúng | PASS | Không cho phép thao tác ngoài `D:\WORK\RESEARCH\TokenToModel-Lab` |
| 13 | Biên bản đồng bộ từ máy khớp SHA-256 | PASS | Xác minh file Windows thực tế, không chỉ dựa trên console |
| 14 | Local P00 đồng bộ đúng mốc, 11 tệp bảo vệ | PASS | Đối chiếu biên bản và tham chiếu Git local; xác nhận thêm SHA của bốn tệp |
| 15 | Không dọn dẹp và không chạy huấn luyện | PASS | Chế độ `NONE` và `NOT_PERFORMED` trong receipt |

Kết quả đối chiếu: **15/15 PASS**, giới hạn phạm vi văn bản và nguồn gốc kỹ thuật.

## Số đo cần hiểu đúng

- **15/15:** số cổng kiểm tra tài liệu/bằng chứng đạt, không phải 15 bài đánh giá chất lượng ngôn ngữ của GPT.
- **24 tệp Markdown:** số tài liệu thay đổi ở thời điểm trước khi bổ sung báo cáo lần hai; chỉ là kích thước phạm vi sửa đổi, không phải phép đo chất lượng tài liệu. Những báo cáo vừa thêm sau đó làm tổng số tệp thay đổi tăng.
- **11 tệp được bảo vệ:** số tệp được chương trình PowerShell băm đối chiếu trước/sau việc đồng bộ. Không phải 11 mẫu huấn luyện.
- **19/19 bài P00 cũ:** 13 bài cục bộ + 6 bài riêng biệt kiểm tra chức năng CPU; không được cộng với QA tài liệu thành một phép đo chất lượng mô hình.

## Vấn đề còn tồn tại

1. Các hình SVG/PNG có thể còn nhãn tiếng Anh; đã có hướng dẫn tiếng Việt nhưng chưa biên tập lại hình.
2. Các biên bản QA gốc được giữ nguyên tiếng Anh để bảo toàn mã băm, được chú giải bằng tài liệu tiếng Việt mới.
3. Chưa chạy bộ dựng sách (Book Build) hoặc thẩm định câu chữ bởi người đọc bên ngoài.
4. Việc local `main` đã đồng bộ mốc P00 **không** có nghĩa local đã đồng bộ commit của PR tài liệu trong tương lai.
5. Cấu hình khoa học vẫn `PROPOSED_NOT_FROZEN`; hiệu năng GPU, huấn luyện mô hình và thương mại hóa chưa được kiểm định.

## Quyết định

- `DOCUMENTATION_SECOND_PASS_QA=PASS_15_OF_15`
- `LOCAL_P00_FAST_FORWARD=PASS`
- `SOURCE_AND_CONFIG_CHANGED=NO`
- `RAW_EVIDENCE_MODIFIED=NO`
- `P01_ADMISSION=NOT_AUTHORIZED`

**Đề xuất:** có thể xem xét chuyển PR #2 khỏi trạng thái nháp và hợp nhất trên GitHub nếu commit HEAD và `main` vẫn khớp các giá trị đã khóa tại thời điểm thao tác. Không xóa worktree; việc đồng bộ Git local với commit mới sau hợp nhất là một quyết định riêng.
