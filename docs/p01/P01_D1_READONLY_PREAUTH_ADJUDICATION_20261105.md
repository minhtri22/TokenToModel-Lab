# P01 D1 — Quyết định thẩm định nguồn dữ liệu, tài nguyên và QA, chỉ đọc

**Công việc:** `TTM_P01_D1_SOURCE_RIGHTS_AND_RESOURCE_PREAUTH_READONLY_REVIEW`  
**Ngày:** 05/11/2026  
**Nhánh:** `design/p01-tokenizer-data-prereg-20261105`  
**Cơ sở:** P00 trên GitHub `main=92facee15d7c0d46b0e84ddf5b6d8b2073e078f7` tại thời điểm rà soát.  
**Phạm vi:** kiểm tra hồ sơ GitHub, trạng thái RemoteMCP đã ký, điều khoản nguồn ứng viên ở trang chính thức, kiểm tra byte fixture F0 ở môi trường chuẩn bị. Không chạy tokenizer, không tải corpus hoặc sửa máy Windows.

## 1. Kết quả theo cổng

| Cổng | Quan sát có chứng cứ | Kết luận |
|---|---|---|
| H02 — Nguồn văn bản được tiếp nhận | Không có danh mục corpus với `admission_decision=ALLOW` trong hồ sơ P01; thư mục gốc Windows đã liệt kê không có `datasets/` | **HOLD** — chưa có một source ID đủ quyền |
| H02 — Nguồn công khai tham khảo | Văn bản Wikimedia thường có giấy phép CC BY-SA 4.0/GFDL và điều kiện ghi công, chia sẻ tương tự; chưa chọn snapshot/trang hoặc kiểm tra ngoại lệ | `CANDIDATE_ONLY`, **không** cho phép tải |
| H05 — Trạng thái thiết bị | Signed node heartbeat `machine-1 ONLINE`, số tác vụ RemoteMCP đang chạy = 0, số tác vụ node chưa giải quyết = 0 | `PASS_READONLY_DEVICE_OBSERVATION` |
| H05 — RAM Windows còn trống | Không có chỉ số trong kết quả RemoteMCP | **NOT_MEASURED** |
| H05 — D: còn trống | Không có chỉ số trong kết quả RemoteMCP | **NOT_MEASURED** |
| H05 — Cơ chế bảo vệ tài nguyên | Chưa có mã QA/negative test của Resource Guard P01 | **HOLD** |
| H04 — SHA-256 mẫu byte F0 | Tái tính byte nguồn cho F00–F11; **12/12 khớp** | **PASS_SCOPED_ORACLE_INTEGRITY** |
| H04 — Unicode và lỗi UTF-8 | F02/F03 khác byte nhưng giống NFC; F06–F08 lỗi UTF-8 bị từ chối 3/3 bởi thư viện chuẩn | **PASS_SCOPED_REFERENCE_ONLY** |
| H04 — Checker độc lập trên Windows | Chưa có checker đã duyệt, chưa có lần chạy hoặc âm tính | **HOLD** |
| Khóa tiền đăng ký khoa học D1 | H02/H04/H05 còn thiếu bằng chứng | **NOT_GRANTED** |

Không coi `0` tác vụ RemoteMCP là `8 GiB` RAM trống; cũng không coi bộ kiểm tra byte giả lập là kiểm thử tokenizer BPE thật.

## 2. Bảng đo và ý nghĩa

| Chỉ số | Đơn vị | Mốc đạt dự kiến | Kết quả đã có | Ý nghĩa |
|---|---|---|---|---|
| SHA-256 F0 khớp | Mẫu | 12/12 | 12/12 | Tệp đặc tả byte và mã băm nhất quán |
| Giải mã UTF-8 lỗi bị từ chối | Mẫu | 3/3 | 3/3 | Oracle nghiêm ngặt không tự thay byte lỗi |
| Nguồn có quyền `ALLOW` | Nguồn | Ít nhất 1 cho phép đo corpus F1/F2 | 0 nguồn đã được xác minh | Không thể chạy nghiên cứu BPE với corpus thật |
| RAM khả dụng | GiB | ≥8 GiB (ứng viên) | Chưa đo | Không được suy đoán dựa trên RAM lắp đặt |
| D: trống | GiB | ≥16 GiB (ứng viên) | Chưa đo | Cần tránh tình trạng thiếu dung lượng khi tạo bản dẫn xuất |
| D: sau dự phòng | GiB | ≥12 GiB (ứng viên) | Chưa đo | Bảo vệ không gian dành cho bằng chứng khác |
| Bộ giới hạn thời gian/RAM | Bài âm tính | PASS tất cả ca đã khóa | Chưa có kiểm thử | Không được tuyên bố an toàn chạy |
| BPE và GPT đã huấn luyện | Lượt | Không áp dụng ở D1 | 0 | Không có kết quả khoa học mới |

## 3. Bằng chứng dẫn chiếu

- `docs/p01/P01_D1_SOURCE_RIGHTS_READONLY_REVIEW_20261105.md`.
- `docs/p01/P01_D1_WINDOWS_RESOURCE_READONLY_REVIEW_20261105.md`.
- `docs/p01/P01_D1_INDEPENDENT_QA_READONLY_PREAUTH_20261105.md`.
- Hợp đồng gốc H01–H05 và `docs/p01/P01_D1_METHOD_REVIEW_AND_LOCK_GATE_20261105.md`.

## 4. Quyết định

- `P01_D1_RIGHTS_ADMISSION=HOLD_NO_VERIFIED_SOURCE`.
- `P01_D1_DEVICE_OBSERVATION=PASS_READONLY`.
- `P01_D1_RAM_D_CAPACITY=NOT_MEASURED`.
- `P01_D1_F0_ORACLE_SHA=PASS_12_OF_12`.
- `P01_D1_INDEPENDENT_CHECKER=NOT_IMPLEMENTED`.
- `P01_D1_SCIENTIFIC_PREREG_LOCK=HOLD`.
- `PR4_STATE=DRAFT_NOT_MERGED`.
- `P01_WORKTREE_AUTHORIZED=false`.
- `P01_DATA_DOWNLOAD_AUTHORIZED=false`.
- `P01_BPE_OR_GPT_TRAINING_AUTHORIZED=false`.
- `P00_CLEANUP_AUTHORIZED=false`.

## 5. Bước tiếp theo

1. Lấy **số đo RAM và D: chỉ đọc** từ chính Windows bằng chương trình PowerShell đã ghim SHA-256, rồi đối chiếu vào cổng H05. Việc có số đo đạt ngưỡng vẫn chưa đủ để cấp quyền khi Resource Guard chưa qua QA.
2. Quyết định nguồn F1 hợp pháp cụ thể và cung cấp bằng chứng quyền, hoặc **giới hạn rõ dự án ở F0-only** cho đến khi có nguồn.
3. Đưa hợp đồng checker độc lập qua một lượt kiểm tra thiết kế/cổng triển khai riêng, chưa tạo mã hay chạy.
4. Chỉ khi ba nhóm bằng chứng nói trên đầy đủ mới xem xét quyết định `D1_PREREGISTRATION_LOCK` riêng; mọi quyền chạy và worktree là quyết định sau đó.

**Kết luận cuối:** `TTM_P01_D1_READONLY_PREAUTH=COMPLETED_WITH_HOLD`. Kết quả được ghi làm chứng cứ quản trị; không phải một lần thử BPE khoa học.
