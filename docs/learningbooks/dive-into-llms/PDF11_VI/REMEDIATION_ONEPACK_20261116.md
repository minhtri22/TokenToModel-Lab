# ONEPACK — DIVE_INTO_LLMS_11PDF_VI_FIDELITY_REMEDIATION_AND_INDEPENDENT_LANGUAGE_QA_ONEPACK

**Nguồn khóa:** Lordog/dive-into-llms `f84c04268794ef94f8949808bbc14ab8636763a0`.

**Tiền kiểm cục bộ bằng tệp nguồn được tải lên:** 11 PDF, 495 trang, nguồn và bản song ngữ khớp SHA. Phiên bản dựng thử đã chạy hai script riêng:
- Phần slide gốc trên 495 trang được giữ nguyên về text layer; 33 phép so khớp hình ảnh vùng nguồn có MAE = 0.
- Unicode: 0 trang chứa mã điều khiển/ký tự thay thế ở phần tiếng Việt (trước đây 53 trang).
- Nội dung Việt: đối chiếu token Markdown ↔ PDF sau Unicode NFKC không có thiếu hụt vượt ngưỡng 2%.
- Tất cả 495 trang có marker tiếng Việt và commit nguồn.
- Đã bổ sung nội dung gắn trực tiếp với slide ở 7 trang: 02/47, 02/57, 04/14, 05/43, 08/45, 10/28, 11/17.
- Cỡ chữ mới sử dụng DejaVu Sans có ký hiệu toán, độ co nhỏ nhất đo được khoảng 0.908, không có tràn textbox trong lượt thử.

**Phân xử gate:** F01 `PASS_STATIC_LOCAL`, F03 `PASS_RENDER_SAMPLE_33`, F02 `HOLD_FULL_LITERAL_TRANSLATION`, independent human-language QA `NOT_EXECUTED`, tổng `HOLD_FIDELITY`.

Dữ liệu trên **chưa được xem là GitHub-upload PASS** cho đến khi GitHub Actions chạy, lưu chứng cứ `REMEDIATION_STATIC_QA_20261116.json` và readback đúng các PDF mới. Không có phê duyệt mới cho khoa học. Không merge `main`. Không sửa `lineage.md`.

**Ghi chú:** QA thuật toán bằng script khác với trình dựng là kiểm tra độc lập về đường mã, **không phải chuyên gia/agent dịch thuật độc lập**. Bản diễn giải không được nâng thành bản dịch toàn văn.
