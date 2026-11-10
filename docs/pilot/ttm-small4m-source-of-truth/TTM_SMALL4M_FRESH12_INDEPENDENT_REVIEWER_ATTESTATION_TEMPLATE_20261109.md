# TTM-Small-4M FRESH12 — Biên bản tiếp nhận người chấm độc lập (CHƯA KÝ)

**Task:** `TTM_SMALL4M_FRESH12_INDEPENDENT_REVIEWER_ATTESTATION_THEN_SINGLE_BATCH_INFERENCE`

## Phần người chấm cần tự điền trước khi nhận dữ liệu

- Người chấm / mã định danh: **PENDING**
- Tổ chức / năng lực liên quan: **PENDING**
- Là con người hay AI độc lập (ghi rõ): **PENDING**
- Xác nhận **không** tham gia tạo 12 prompt, chọn mô hình, xử lý kết quả: **PENDING**
- Xác nhận **không** được xem secret A/B, điều kiện của các cột, raw logits, lịch sử kết quả: **PENDING**
- Xác nhận nhận rubric 0–3 theo JSON ghim và hiểu giới hạn về xuống dòng: **PENDING**
- Thời điểm xác nhận trước batch: **PENDING**
- Chữ ký / tài liệu định danh có thể kiểm chứng (không đưa thông tin cá nhân nhạy cảm lên GitHub công khai): **PENDING**
- File attestation SHA256: **PENDING**

## Quy trình bắt buộc

1. Xác minh checksum GitHub PR #13 và hợp đồng public trước batch; reviewer xác nhận nhận việc mà không đọc key.
2. Chạy batch 48 đầu ra dưới hợp đồng đã khóa. Người chấm chỉ nhận prompt và bản hiển thị A/B đã giảm dấu hiệu định dạng, không nhãn condition/checkpoint.
3. Chấm đủ **144 điểm nguyên 0–3** bằng [CSV template](../../../artifacts/qa/ttm-original1280/fresh12/REVIEWER_SCORE_TEMPLATE_20261109.csv), ghi lại nhận xét ngắn cho từng cặp.
4. Khóa SHA256 phiếu và biên bản trên GitHub trước khi dùng khóa giải mã escrow. Không chấm lại/đổi điểm sau giải mù.
5. Phân xử theo tiêu chí đã tiền đăng ký và nêu rõ giới hạn còn tồn tại. Nếu thiếu người chấm hoặc bị lộ nhãn, ghi `HOLD`, không công bố khoa học PASS.

**Đây là mẫu**, không phải bằng chứng người chấm đã được tuyển hoặc đồng ý. Không tự đánh dấu PASS trước khi có attestation thật.
