# Checklist kiểm kê và hoàn thành — 2026-11-16

**Nguồn khóa:** [`f84c04268794ef94f8949808bbc14ab8636763a0`](https://github.com/Lordog/dive-into-llms/tree/f84c04268794ef94f8949808bbc14ab8636763a0)  
**Phân loại:** `ORIGINAL_VI_GUIDES` ≠ `FULL_TRANSLATION`. Không gian dối với checklist hoàn thành.

## 1. Checklist theo chủ đề (tài liệu Việt viết mới)

- [x] Chương 01 — [Tinh chỉnh và triển khai mô hình](chapter-01-vi.md)
- [x] Chương 02 — [Prompting và chuỗi suy luận](chapter-02-vi.md)
- [x] Chương 03 — [Chỉnh sửa kiến thức và tính cục bộ](chapter-03-vi.md)
- [x] Chương 04 — [Suy luận toán học và chưng cất tri thức](chapter-04-vi.md)
- [x] Chương 05 — [Thủy vân đầu ra mô hình](chapter-05-vi.md)
- [x] Chương 06 — [Đánh giá chống vượt rào an toàn](chapter-06-vi.md)
- [x] Chương 07 — [Giấu tin trong văn bản sinh](chapter-07-vi.md)
- [x] Chương 08 — [Kiến trúc ngôn ngữ đa phương thức](chapter-08-vi.md)
- [x] Chương 09 — [Tác nhân điều khiển giao diện](chapter-09-vi.md)
- [x] Chương 10 — [An toàn hệ thống tác nhân](chapter-10-vi.md)
- [x] Chương 11 — [RLHF và tối ưu chính sách bằng PPO](chapter-11-vi.md)

**Số chương chưa có giáo trình Việt viết mới: 0/11.** Tuy nhiên đây **không phải** 11 bản dịch đầy đủ của README upstream.

## 2. Checklist chuyển ngữ nguyên văn theo loại tài sản

| Nguồn | Tổng số | Đã dịch đầy đủ/đối chiếu từng đoạn | Còn chưa dịch |
|---|---:|---:|---:|
| README gốc | 1 | 0 | 1 |
| README 11 chương | 11 | 0 | 11 |
| Notebook Jupyter | 11 | 0 | 11 |
| PDF bài giảng | 11 | 0 | 11 |
| **Tổng 4 loại** | **34** | **0** | **34** |

Đây là **số lượng thực tế**, không được thay bằng số 0. Có 105 file upstream gồm binary assets và cấu hình không tính trong 34 tài liệu được nêu. Trạng thái `FULL_TRANSLATION=NOT_DONE`.

## 3. QA đã thực hiện và chưa thực hiện

- [x] Đã đối chiếu danh mục upstream từ Git tree exact commit.
- [x] Đã biên soạn 11 bài học tiếng Việt mới, có khái niệm, ví dụ và liên hệ TTM/CLDP.
- [x] Bản thảo giữ nhánh tài liệu; không sửa `main`, `lineage.md`, code khoa học, frozen checkpoints.
- [ ] Independent reviewer kiểm chứng tính chính xác và đầy đủ của 11 bài.
- [ ] Bản dịch nguyên văn PDF/README/notebook từng file và quyền tái phân phối bản dịch (nếu muốn xuất bản).
- [ ] Notebook thực hành tự viết và kiểm chứng chạy trên Python 3.12.
- [ ] Merge PR sau QA đúng phạm vi.

**Không được nâng `DOCS_STATIC_QA` thành `SCIENTIFIC_PASS`.**

## 4. Công việc tiếp theo — gói duy nhất

`TTM_CLDP_VI_LEARNINGBOOKS_11_CHAPTERS_INDEPENDENT_CONTENT_QA_AND_SOURCE_SCOPE_CLOSURE_ONEPACK`

Kiểm toán độc lập 11 chương, đối chiếu nguồn theo chủ đề, xác định bản nào thiếu phần giải thích quan trọng, sửa tập trung trong một lượt và ra quyết định PR tài liệu. Không mở thí nghiệm khoa học hoặc micro-permit.
