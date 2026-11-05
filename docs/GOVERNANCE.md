# Quy trình quản trị nhánh, kiểm thử, nhật ký và hợp nhất

## Chu trình thay đổi

Đề xuất (Proposed) → tạo nhánh (Branched) → triển khai (Implemented) → chờ kiểm thử (QA Pending) → đạt/không đạt (QA Pass/Fail) → thẩm định (Reviewed) → hợp nhất (Merged) → xác lập mốc đối chứng (Baseline Established).

Mọi phát triển và mọi sửa lỗi đều phải có nhánh Git riêng. Nhánh lấy đúng commit mới nhất đã được xác minh từ `main`. Khi kiểm thử FAIL, không hợp nhất; sửa trên nhánh và tạo biên bản mới, không ghi đè lỗi cũ. Khi thiếu dữ liệu, dùng trạng thái chưa đủ kết luận (Inconclusive), không tự gán PASS.

## Điều kiện bắt buộc trước khi hợp nhất

1. **Nguồn gốc:** đúng kho GitHub, thư mục gốc, `origin`, commit gốc, commit ứng viên, nhánh và trạng thái cây Git.
2. **Cấu hình:** mã cấu hình, SHA-256, bộ dữ liệu, bộ tách token (Tokenizer), phiên bản Python/PyTorch, thiết bị, seed và commit.
3. **Kiểm thử:** kiểm thử đơn vị (Unit Tests), tích hợp (Integration), trường hợp sai (Negative Tests), hồi quy (Regression) và tương đương số học (Numerical Parity) theo phạm vi.
4. **Đối chứng:** bảng khác biệt so với mốc trước, điều kiện so sánh ngang bằng (Workload Parity), nêu rõ khi không thể so sánh.
5. **Thẩm định độc lập:** bộ kiểm thử tách khỏi bộ thử phát triển, có biên bản và mã băm (hash); không ngộ nhận là thẩm định bởi bên thứ ba.
6. **Lưu vết:** nhật ký chạy bất biến, báo cáo so sánh, các kết luận PASS/FAIL và bản ghi `lineage.md`.
7. **Hợp nhất:** qua yêu cầu hợp nhất (Pull Request) sau kiểm tra mọi điều kiện. Không dùng `--force`, ghi đè lịch sử hay sửa biên bản bằng chứng.

## Phân biệt các kết luận

- `QA_PASS`: chức năng mã nguồn đạt các phép thử đã công bố; không xác nhận học tốt hay nhanh hơn.
- `EXPERIMENT_PASS`: đạt tiêu chí thực nghiệm được định trước và có bằng chứng phù hợp.
- `EXPERIMENT_FAIL`: không đạt tiêu chí; giữ lại dữ liệu và biên bản.
- `INCONCLUSIVE`: chưa có đủ chứng cứ hoặc phép đo không tương đương.
- `COMMERCIAL_READY`: đòi hỏi đánh giá riêng về chất lượng, giấy phép, dữ liệu, bảo mật, quyền riêng tư, chi phí và vận hành.

## Lưu trữ và truy xuất

- `lineage.md`: chỉ ghi bổ sung (append-only) các mốc quyết định, kể cả lỗi hạ tầng, QA và kết quả khoa học.
- `experiments/runs/<run-id>.json`: biên bản lần chạy (Run Receipt) bất biến.
- `experiments/registry.jsonl`: sổ mục lục lần chạy bất biến, có SHA-256.
- `experiments/comparisons/`: báo cáo đối chứng và kết luận về tính so sánh được.
- `artifacts/qa/`: biên bản QA nhỏ; log nặng và checkpoint để ngoài Git nhưng phải có đường dẫn và mã băm.

Bằng chứng lịch sử đã khóa không bị sửa chỉ để thay đổi ngôn ngữ. Có thể bổ sung tài liệu tiếng Việt dẫn chiếu chính xác bằng chứng gốc. Không đưa khóa truy cập, thông tin nhạy cảm hoặc dữ liệu không có quyền sử dụng vào GitHub.

## Ngôn ngữ tài liệu

Mọi tài liệu mới và tài liệu hướng dẫn có thể chỉnh sửa dùng tiếng Việt, thuật ngữ tiếng Anh trong ngoặc. Tên tệp, định danh mã nguồn, lệnh, thông số và trường JSON được giữ nguyên. Xem `docs/TERMINOLOGY_VI.md`.

## Ranh giới nơi làm việc

- Chỉ dùng `D:\WORK\RESEARCH\TokenToModel-Lab` cho cây làm việc phụ (Git worktree), dữ liệu dự án và dọn dẹp.
- Không dọn dẹp nếu chưa được cấp phép riêng cho đường dẫn cụ thể.
- Từ chối liên kết tượng trưng (symlink), điểm nối (junction) hoặc đường dẫn phân tích thực tế ra ngoài vùng cho phép.
- Công việc từ xa qua RemoteMCP phải dùng vị trí dự án/cây làm việc do cơ chế quản lý trả về; không thay task, thiết bị hoặc root để lách cổng.

## Trạng thái P00 sau hợp nhất

- PR #1 đã hợp nhất trên GitHub tại `8df22f5f29e645b2becff936daccbd32ac780661`.
- Mã P00 được kiểm định chức năng trên CPU; không khẳng định GPU, huấn luyện hoàn chỉnh hoặc tăng tốc.
- Local `main` ban đầu còn ở commit khởi tạo, nhưng đã đồng bộ tiến nhanh (Fast-forward) đúng P00 vào ngày 05/11/2026; xem `docs/qa/P00_LOCAL_FAST_FORWARD_ADJUDICATION_20261105.md`. Mọi đợt đồng bộ tiếp theo vẫn phải kiểm tra Git độc lập.
- Xem biên bản `docs/qa/P00_POST_MERGE_AUDIT_20261105.md` trước khi mở P01.
