# Nguồn gốc mã tham chiếu (Provenance) P00

- Nguồn: gói `gpt_paged_attention_reference.zip` được tạo trong hội thoại trước.
- SHA-256 gói nguồn được ghi nhận: `ca46934992390659281564773a2bd10548204fc17e9c5e3a9ae65d3402d9905b`.
- Các thành phần: `model.py`, `paged_kv.py`, `train.py`, `test_reference.py`, `demo.py`, `README.md`.
- Mã tham chiếu được đưa vào `reference/phase0/` để nghiên cứu, không phải mã phục vụ sản phẩm (Production Code) hoặc nhân GPU PagedAttention tối ưu.
- Nguồn mã P00 đã được kiểm thử và chấp thuận trong phạm vi đúng chức năng CPU tại commit `382da2c52d0fb4efe1cd9de5c92e68de79a52a20`.
- PR #1 đã hợp nhất trên GitHub tại `8df22f5f29e645b2becff936daccbd32ac780661`. Mã nguồn trên `main` được kiểm tra giữ nguyên so với nguồn đã kiểm định.
- Kiểm thử Windows: 13/13 cục bộ và 6/6 bổ sung độc lập; bằng chứng gốc và mã SHA-256 lưu ở `artifacts/qa/p00/`.
- Cấu hình P00 vẫn `PROPOSED_NOT_FROZEN`; chưa huấn luyện mô hình khoa học và chưa đo hiệu năng GPU.
