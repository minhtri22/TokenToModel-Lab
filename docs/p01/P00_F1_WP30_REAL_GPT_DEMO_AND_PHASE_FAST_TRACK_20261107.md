# TTM — Kết quả demo huấn luyện GPT P00 trên dữ liệu Wikipedia thật (Windows)

Ngày 07/11/2026. **Loại bằng chứng: demo kỹ thuật (engineering), không phải P01-E0 hay thực nghiệm khoa học P03.**

## 1. Kết quả thực sự trên máy người dùng

Đã nhận console và ba tệp kết quả gốc do người dùng tải lên. Đối chiếu SHA-256:
- `demo_report.json`: `9056db47e554fd9c708923036f49f81f6d09d447dd85615ed8757439e5bc53b6`
- `sample.txt`: `d9bcf019ebc9cbfed6afbe314bdd5a6dae08a7ef85b75f301cc7c72ca37471fd`
- `checkpoint_demo.pt`: `4f45056a67d177c66dcd2430614c5d0e417f9c8d02d51d1a5c988cfe5cd4759e`

Mô hình gọi đúng P00 `reference/phase0/model.py`, PyTorch `2.12.0+cpu`. Cấu hình: byte vocab 256, context 48, embedding 64, 2 lớp, 4 đầu attention. 30 tài liệu Wikipedia từ vùng cách ly F1, không sử dụng Wikisource/CQG-J3. Huấn luyện **36 bước thật**:
- Fixed-batch loss trước: `5.567609`.
- Fixed-batch loss sau: `2.74368`; giảm **2.823929 / 50.7206774%**.
- Training-step loss (1,6,12,24,36): `5.56057, 4.77397, 4.09584, 3.14822, 2.83296`.
- Checkpoint 488351 byte. Tải bằng `torch.load(weights_only=True,map_location='cpu')` thành công, 29 tensor state_dict, khoảng 119552 phần tử tham số **độc lập** (embedding/head được tied), không có NaN/Inf trong tensor.

Generated sample chứa 19 ký tự thay thế `�` trong 104 ký tự sinh ra, chưa mạch lạc. Với vocab byte 256, chuỗi byte sinh tự do có thể không hợp lệ UTF-8; context 48 byte và mô hình rất nhỏ. Không có held-out validation, không thể suy ra mô hình có chất lượng ngôn ngữ hay tổng quát hóa. Loss giảm là tín hiệu cập nhật trọng số, **không** chứng minh sản phẩm AI hoàn thiện.

## 2. Tài nguyên và lựa chọn máy

Thiết bị: Windows 11 x64, Core Ultra 7 258V, RAM 32 GiB/GB mức người dùng báo cáo, Intel Arc 140V. Tổng dung lượng 954 GB, đã dùng 902 GB theo người dùng (còn xấp xỉ 52 GB, chưa đo thực tế). Intel Arc tích hợp không được mặc định là 16GB VRAM vật lý dành riêng. PyTorch vừa chạy có hậu tố **+cpu**, chưa dùng XPU. Hướng khả thi:
- Local: P01 byte/BPE, QA correctness P02, micro-batch overfit P03, thử sinh mẫu nhỏ.
- Colab GPU theo sẵn có: huấn luyện thời gian dài/mô hình lớn hơn sau khi P01/P02 khóa; dùng checkpoint thường xuyên vì runtime Colab hữu hạn và GPU không bảo đảm.
- Nếu muốn thử Arc XPU, kiểm tra không phá môi trường hiện tại ở **env riêng** sau khi các phase chính tiến triển.

## 3. Quyết định tiến độ

Chủ dự án muốn **chạy được trước khi làm hồ sơ lặp lại**. Không tiếp tục dựng 30 giấy phép thủ công riêng khi nguồn Wikipedia đã có metadata CC BY-SA 4.0, revision, attribution URL và SHA đã kiểm; vẫn xử lý ngoại lệ bản quyền/PII cụ thể và giữ nguyên nghĩa vụ attribution. Việc huấn luyện nội bộ demo không có nghĩa mở F1 chính thức. Không đẩy text corpus hoặc checkpoint lên GitHub; bản gốc được bảo tồn trong máy và tệp của cuộc hội thoại.

Các phase P00–P12 và cổng khoa học bắt buộc không thay đổi. Không mở lại K1/K2, không chạy lại S1, không ghi demo như khám phá khoa học vào `lineage.md`, không sửa `main`.

**Bước tiếp theo: `TTM_P01_MINIMAL_F1_ADMISSION_BPE_E0_INTEGRATED_QA_THEN_P02_P03_P04`.** Thực hiện tối thiểu các kiểm tra quyền có dấu hiệu rủi ro cụ thể, freeze 30 nhóm H03 + split train/val/test theo seed/logic đã duyệt, bảo đảm chỉ TRAIN học BPE và TEST sealed; một gói kiểm thử tích hợp Docker nếu vẫn là route được duyệt; E0 một lượt. Sau đó P02 Transformer correctness, P03 micro-batch overfit, P04 checkpoint + held-out eval. Việc train dài có thể làm trên Colab, không thay đổi các ràng buộc science.
