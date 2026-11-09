# ADR-0002 — GitHub là nguồn chuẩn cho TTM: tải theo commit, lưu bằng chứng, dọn tạm sau readback

**Ngày:** 2026-11-09. **Quyết định chủ dự án:** GitHub là nguồn chuẩn (source of truth) đối với mã nguồn, gói chạy/đầu vào đã khóa, cấu hình, kiểm thử, tài liệu quản trị và **bằng chứng được phép công bố**. Có hiệu lực khi PR #12 được duyệt/hợp nhất; trong khi chờ, nhánh PR là nguồn chuẩn **ứng viên** có SHA bất biến, không thay thế `main`.

## Quy trình một lượt không phát sinh nhiều nhánh

1. Chọn đúng `minhtri22/TokenToModel-Lab`, nhánh đã duyệt, SHA 40 ký tự và danh sách tệp + SHA-256. PowerShell trên Windows lấy nguồn **trực tiếp từ GitHub** ở đúng commit (Git clone hoặc URL raw commit), đối chiếu danh tính repo/origin, SHA Git blob, SHA-256 manifest; không thực thi mã trước kiểm tra.
2. Tất cả thao tác chạy và tải về nằm **bên trong** `D:\WORK\RESEARCH\TokenToModel-Lab\_tmp\<run-id>` do chính lượt chạy tạo độc quyền. Không dùng `C:\` root, không thay cấu hình Windows toàn cục, không đổi dịch vụ Ollama 11434, không trộn nhánh/phase, không tự chạy lại one-shot.
3. QA/experiment tạo biên bản gồm commit, code/config/data pins, thông số, PASS/FAIL/HOLD, stdout/stderr, thời gian, môi trường và SHA-256; không sửa kết quả sau chạy. Công khai cả FAIL và không đủ kết luận. Kết quả khoa học append-only vào `lineage.md` qua review riêng; không nhập lỗi kỹ thuật vào lineage.
4. Lọc dữ liệu trước công bố: **không tự động đẩy lên repository công khai** raw TRAIN/VAL/TEST, checkpoint, GGUF, dữ liệu định danh cá nhân, bí mật/token hoặc log chứa chúng. Những vật liệu riêng tư cần lưu tại kho riêng được phép, kèm URI/id, phiên bản, SHA-256 và bằng chứng khả năng đọc lại; **chỉ có hash/receipt trên GitHub không bảo đảm có thể khôi phục byte vật liệu riêng tư**. Không xóa bản riêng tư nếu chưa có bản sao thực tế được kiểm chứng độc lập.
5. Commit biên bản công khai và stdout/stderr đã thẩm định lên đúng nhánh GitHub bằng commit **fast-forward không force**; nếu HEAD thay đổi, dừng để người phụ trách giải quyết, không tự mở nhánh. Đọc lại SHA commit từ remote, tải **từng tệp** từ URL gắn commit SHA rồi so SHA-256 với bản đã gửi.
6. **Chỉ khi tất cả nguồn/bằng chứng bắt buộc có thể tải lại đúng SHA**, xóa các tệp tải xuống và thư mục tạm **do lượt chạy tự tạo**, sau khi kiểm tra canonical path, không symlink/junction. Gặp thiếu evidence, network lỗi, SHA sai, push reject, hoặc kết quả nghiên cứu chưa có bản sao đầy đủ thì **giữ tạm và HOLD**. Không dọn thư mục bằng chứng V1–V5/T4, thư mục Docker, Drive, clone của người dùng hoặc các file Downloads trước đây bằng luật này.
7. Cuối mỗi turn bắt buộc `MERGE_DECISION=MERGED|MERGE_READY|HOLD|NOT_MERGEABLE` cùng HEAD main/work, QA, lineage, public-source rights, vị trí bằng chứng và **một** blocker/next action. Ưu tiên hoàn thành và hợp nhất một workstream đang mở trước khi tạo nhánh mới.

## Nguồn chuẩn được chuẩn hóa trong PR #12

- `tools/pilot_t5/v5_native_source_20261109/`: **8 tệp**, 7 nguồn gốc + một wrapper hậu vá `*.patched.ps1`; wrapper gốc không bị viết lại. ZIP lịch sử V5 SHA256 `0c27593dd01c5e652709c03b6a0019533aa602e178d1e4251052bc69bf01ef33`.
- `tools/pilot_t5/v5_inference_only_source_20261109/`: **5 tệp** nguyên byte từ ZIP inference-only SHA256 `b07fc89d751710025d113a2e64249db260de7a351f18a75eb8a4a8c437f16379`.
- `tools/pilot_q1q2/frozen_inputs_20261109/`: **7 tệp**, prompt, config, run matrices, manifest, QA, README. Tất cả mã Git blob khớp bản trong ZIP Q1/Q2 SHA256 `ba0b0164d33a201107265b095a1fd120f0b032a394aaf7b8f58a694d6df78dde`.
- Các ZIP lịch sử không được ngầm coi là đã upload nguyên nhị phân; **các tệp nguồn bên trong** mới là đường tải chuẩn GitHub đã được xác minh. Script mới clone nguyên cây và kiểm mã nguồn theo manifest; không dùng link `sandbox:` làm nguồn sản xuất.
- `tools/qa/ttm_pr12_github_single_integrated_qa.py`: script QA một lượt chỉ sử dụng fixtures/mock, không gọi Ollama/Colab hay đọc TEST niêm phong. `tools/qa/Invoke-TTM-PR12-GitHub-Integrated-QA-PS51.ps1`: bootstrap tải script Python từ đúng HEAD GitHub, xác minh Git blob trước chạy, phát hành evidence về chính nhánh rồi đọc lại.
- Quy trình này **không tái cấp phép** V1–V5/T4 đã tiêu thụ và không tự tuyên bố parity PASS khi T5 strict logits vẫn FAIL 7/8.

**Ranh giới:** GitHub public là chuẩn cho **mã nguồn + receipts đã thẩm định**, còn tính tái lập khoa học toàn phần vẫn cần kho riêng có bảo toàn bytes checkpoint/private corpus và quyền sử dụng. Không bao giờ dùng việc "đã commit hash" làm cớ xóa bằng chứng chưa được sao lưu.
