# Dive into LLMs — Giáo trình nghiên cứu tiếng Việt (bản tự biên soạn)

> Chú ý: đây là **giáo trình nghiên cứu tiếng Việt mới**, không phải bản dịch toàn văn `dive-into-llms`. Nguồn học tập tại [upstream exact commit](https://github.com/Lordog/dive-into-llms/tree/f84c04268794ef94f8949808bbc14ab8636763a0). TTM là repo public.

**Ngày biên soạn:** 2026-11-16 · **Trạng thái:** `11/11 VI_GUIDES_AUTHORED`; `FULL_SOURCE_TRANSLATION_NOT_DONE` · **Science:** `NOT_EXECUTED`.

## Mục lục 11 chương

01. [Tinh chỉnh và triển khai mô hình](chapter-01-vi.md) — TTM
02. [Prompting và chuỗi suy luận](chapter-02-vi.md) — TTM
03. [Chỉnh sửa kiến thức và tính cục bộ](chapter-03-vi.md) — TTM và CLDP
04. [Suy luận toán học và chưng cất tri thức](chapter-04-vi.md) — TTM
05. [Thủy vân đầu ra mô hình](chapter-05-vi.md) — TTM
06. [Đánh giá chống vượt rào an toàn](chapter-06-vi.md) — TTM và CLDP
07. [Giấu tin trong văn bản sinh](chapter-07-vi.md) — Tham khảo
08. [Kiến trúc ngôn ngữ đa phương thức](chapter-08-vi.md) — TTM
09. [Tác nhân điều khiển giao diện](chapter-09-vi.md) — Agent Orchestrator
10. [An toàn hệ thống tác nhân](chapter-10-vi.md) — Agent Orchestrator
11. [RLHF và tối ưu chính sách bằng PPO](chapter-11-vi.md) — TTM

## Kiểm tra trạng thái

Xem [checklist kiểm kê](TRANSLATION_COMPLETENESS_CHECKLIST.md) để phân biệt **11/11 chương có tài liệu Việt** và **34 tài liệu gốc chưa có bản dịch toàn văn**. Chỉ số “chưa dịch = 0” không hợp lệ cho phạm vi toàn bộ repository.

## Lộ trình đề xuất

- **TTM:** Chương 1 → 2 → 3 → 4 → 11, sau đó chương 8 để hiểu adapter và equal-information-budget; không chạy notebook.
- **CLDP:** Chương 3 → 10 → 2, tập trung locality, stability và causal controls; không thay kiến trúc Layered Blackboard.
- **Agent Orchestrator:** Chương 9 → 10 để phân biệt đề xuất hành động và verified execution.

Đọc thêm [ma trận hướng nghiên cứu TTM/CLDP](RESEARCH_DIRECTION_MATRIX.md) và [nguồn, quyền tái phân phối](RIGHTS_AND_PROVENANCE.md). Các kết luận `Q4_CLOSED_HOLD_EVIDENCE_INSUFFICIENT` của TTM và Phase3F-R scoped admission của CLDP không thay đổi.

## Bài tập học tập

Mỗi chương có lý thuyết, công thức/khung khái niệm, ví dụ độc lập, câu hỏi tự kiểm tra và điều kiện dừng. Không có lệnh huấn luyện được thực thi, không phát sinh evidence khoa học. Những ví dụ số liệu ghi “giả định” không phải benchmark.
