# TokenToModel-Lab (TTM) — Xây mô hình ngôn ngữ từ token đến suy luận

Đây là dự án tự xây mô hình GPT-like từ các thành phần cơ bản: bộ tách token (Tokenizer), Transformer chỉ có bộ giải mã (Decoder-only Transformer), cơ chế chú ý (Attention), huấn luyện (Training), đánh giá (Evaluation) và bộ nhớ KV phân trang (Paged KV Cache).

**Mục tiêu cuối:** một mô hình có thể huấn luyện, đo lường, vận hành và xem xét thương mại hóa theo bằng chứng; đồng thời hình thành tài liệu để viết sách bằng tiếng Việt.

## Trạng thái dự án sau P00

- P00 đã được hợp nhất vào `main` trên GitHub tại commit `8df22f5f29e645b2becff936daccbd32ac780661`.
- Mã tham chiếu P00 đã đạt kiểm thử chức năng trên CPU: 13/13 bài kiểm thử cục bộ Windows và 6/6 bài kiểm thử bổ sung độc lập.
- Đây là **mốc đối chứng kỹ thuật (Engineering Baseline)**, chưa phải mô hình đã được huấn luyện hoặc nhân PagedAttention GPU tối ưu.
- Cấu hình `configs/phase0_reference.json` vẫn có trạng thái `PROPOSED_NOT_FROZEN`, không phải khóa thực nghiệm khoa học.
- Sau kiểm toán ban đầu, local `main` đã được đồng bộ tiến nhanh (Fast-forward) tới commit P00 `8df22f5f29e645b2becff936daccbd32ac780661`. Xem biên bản thẩm định mới `docs/qa/P00_LOCAL_FAST_FORWARD_ADJUDICATION_20261105.md`. Tài liệu PR #2 vẫn phải qua cổng kiểm định và hợp nhất riêng.

## Cấu trúc tài liệu

| Đường dẫn | Nội dung |
|---|---|
| `PROJECT_CHARTER.md` | Điều lệ, mục tiêu và phạm vi |
| `docs/PHASE_PLAN.md` | Lộ trình giai đoạn P00–P12 |
| `docs/ARCHITECTURE.md` | Sơ đồ kiến trúc và luồng xử lý |
| `docs/GOVERNANCE.md` | Quản trị nhánh, kiểm thử và hợp nhất |
| `docs/COMPARISON_PROTOCOL.md` | Quy tắc đo lường và so sánh cấu hình |
| `docs/TRAINING_PROTOCOL.md` | Kế hoạch huấn luyện mô hình |
| `docs/diagrams/` | Sơ đồ kỹ thuật (SVG và PNG) |
| `docs/qa/` | Báo cáo QA, kiểm toán và giải thích kết quả |
| `reference/phase0/` | Mã mô hình tham chiếu đã kiểm thử |
| `experiments/` | Biên bản chạy và sổ đăng ký bất biến |
| `lineage.md` | Dòng lịch sử chỉ ghi bổ sung (append-only) |
| `book/` | Dàn ý sách hướng dẫn |
| `docs/TERMINOLOGY_VI.md` | Quy tắc viết tiếng Việt và thuật ngữ |

## Quy trình thay đổi

Mọi thay đổi có nhánh Git riêng, cấu hình và nguồn được kiểm tra, kết quả đạt/không đạt được lưu, có kiểm thử độc lập (Independent QA) phù hợp phạm vi. Chỉ khi kết luận hợp lệ mới xem xét hợp nhất (merge) vào `main`. Kết quả FAIL phải được giữ lại. Không đổi số liệu hoặc sửa lịch sử đã công bố.

**Không coi QA PASS là kết quả khoa học hoặc chứng nhận thương mại.**

## Ranh giới máy Windows

- Kho GitHub: `https://github.com/minhtri22/TokenToModel-Lab.git`.
- Thư mục gốc duy nhất: `D:\WORK\RESEARCH\TokenToModel-Lab`.
- Mọi cây làm việc phụ (Git worktree) và thao tác dọn dẹp chỉ được ở **bên trong** thư mục gốc.
- Không dọn dẹp nếu chưa có một quyết định riêng cho đúng đường dẫn.
- Xem `docs/WORKSPACE_BOUNDARY.md` trước khi thao tác trên máy Windows.

## Kiểm thử tham chiếu (không tự động chạy lại)

Bộ kiểm thử đã thực hiện dùng bộ dữ liệu minh họa nhỏ (fixture), không tải dữ liệu khoa học và không huấn luyện mô hình hoàn chỉnh. Tham khảo `reference/phase0/README.md` và các biên bản QA trước khi tái chạy để không ghi đè bằng chứng cũ.
