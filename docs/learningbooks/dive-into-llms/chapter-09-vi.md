> **Ranh giới:** Đây là ghi chú học thuật do trợ lý tổng hợp từ chủ đề của giáo trình nguồn; chưa phải dịch toàn văn, không được dùng làm nguồn chứng minh năng lực hoặc thành công của bất kỳ dự án nghiên cứu nào.

# Ghi chú học tập — Chương 09: Tác nhân điều khiển giao diện

**Tài liệu học tập tiếng Việt viết mới (original Vietnamese study guide), không phải bản dịch nguyên văn.**  
**Nguồn đối chiếu:** [upstream chương 9](https://github.com/Lordog/dive-into-llms/tree/f84c04268794ef94f8949808bbc14ab8636763a0/documents/chapter9) · **Commit nguồn:** `f84c04268794ef94f8949808bbc14ab8636763a0`  
**Phân loại:** Ghi chú kiến thức học tập độc lập, không suy diễn từ nghiên cứu đang tiến hành · **Trạng thái:** `STUDY_NOTES_ONLY / NOT_FULL_TRANSLATION / NOT_SCIENCE`

## Bài học cốt lõi
GUI agent phải ánh xạ quan sát màn hình và lịch sử thao tác thành một hành động có thể thực hiện. Sai khác giữa “đề xuất hành động” và “đã thực hiện thành công” là cực kỳ quan trọng. Phải xác minh hậu điều kiện (postcondition) sau thao tác, tránh biến điểm confidence do model tự sinh thành xác suất thành công đã hiệu chuẩn.

Một vòng an toàn có các trạng thái: quan sát → mô tả mục tiêu → đề xuất hành động → kiểm tra quyền → thực thi có kiểm soát → xác minh trạng thái mới → ghi receipt. Các hành động có tác động bên ngoài cần được phân loại theo mức độ đảo ngược được.

## Phác thảo contract
Đầu vào: `session_id`, `task_id`, `snapshot_hash`, `allowed_actions`, `expected_postcondition`.
Đầu ra: `proposed_action`, `confidence_raw`, `permission_needed`, `state_before`, `state_after`, `evidence_ref`, `status`.

`confidence_raw` không tự đồng nhất với probability calibrated. Khi mô hình báo 0.9 cho hành động, chỉ có calibration trên tập độc lập mới cho phép diễn giải là tỷ lệ thành công xấp xỉ 90%.

## Bài tập điều phối
Một agent đề xuất bấm nút “Lưu” khi cửa sổ chưa bật. Xác định failure mode và đề xuất cách báo `BLOCK_STALE_OBSERVATION` thay vì âm thầm nhấn lại. So sánh với tình huống có quyền nhưng thao tác đổi dữ liệu cần confirmation.

## Ranh giới
Không mở phiên GUI, không nhấn hành động, không chạy tác vụ qua công cụ kết nối ở bước học tập. Không coi successful screenshot là kết quả khoa học.
