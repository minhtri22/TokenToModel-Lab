# TTM — Phán quyết E0 và đóng tiêu chí kỹ thuật P01 theo phạm vi F1 WP30

Ngày 07/11/2026. Mã quyết định: `TTM_P01_F1_WP30_E0_FORMAL_CLOSURE_SCOPED_20261107`.

## Kết luận

**`E0=PASS_CONFIRMED_IN_SCOPE`** và **`P01_TECHNICAL_EXIT=PASS_SCOPED_F1_WP30_E0`**. Đủ chứng cứ cho các tiêu chí tokenizer/dữ liệu P01 đối với **30 revision Wikipedia tiếng Việt, sử dụng nội bộ**: quyền sử dụng phạm vi hẹp đã được chủ dự án xác lập có điều kiện, không mở rộng cấp quyền ra sản phẩm công khai. Biên bản `independent_qa.json` ghi `INDEPENDENT_E0_QA_PASS`. Đây là kết luận trên dữ liệu gốc đã chạy, không phải đánh giá chất lượng mô hình GPT.

**Trạng thái luồng Git:** Kết luận trên nhánh thẩm định; chỉ đóng P01 trên nhánh chính sau khi kiểm tra diff, kiểm định nguồn và hợp nhất đúng quy trình. `P02=NOT_OPENED_UNTIL_P01_MERGE_DECISION`, `P03/P04=NOT_OPENED`. Không thực thi lại E0.

## Bằng chứng trực tiếp từ Windows

- `evidence/p01/TTM_P01_F1_WP30_E0_DOCKER_20261107.json`, SHA-256 người chạy báo `acefa6dde2e2d5a683fc9da169b0d2c70e03bacd28457cdaae5351ccab9728b3`. Nội dung đọc lại giống `e0_integrated_result.json`.
- `experiments/p01/TTM_P01_F1_WP30_E0_DOCKER_20261107/independent_qa.json` = `INDEPENDENT_E0_QA_PASS`, 30 nguồn SHA đã kiểm, 27 tài liệu TRAIN+VALIDATION round-trip, TEST không dùng để học hoặc lựa chọn.
- `source_lock.json`: 30 tài liệu có group_id và text_sha riêng; 24 TRAIN, 3 VALIDATION, 3 TEST; seed `20261105`; giấy phép `CC BY-SA 4.0` cho sử dụng nội bộ theo phạm vi đã duyệt, link attribution/revision.
- E0 B0 hoàn nguyên byte 100%; B1 target/actual 2048; hai worker Docker tạo cùng `merges.ttmbpe` SHA `53aabcb8ac3a3c16c7cbd915b76eb82653a334c98381fad95a05eba0a9353f60`; khoảng 6.787s và 7.817s; raw/canonical/group leakage = `0/0/0`.
- TRAIN 1,127,975 byte, B0 1,127,975 token, B1 288,526 token (giảm 74,42%); VALIDATION 147,164 byte, B1 38,992 token (giảm 73,50%). Không sử dụng TEST để cải thiện thuật toán.
- Python host 3.12.10, Python Docker 3.12.16, image ID `sha256:4840d514c583a4d3d8cad3940e68dee6f0f6f3635c12fcd0a3d74c21a5b93a54`. Docker Guard capability PASS trước one-shot marker.

Lưu ý kiểm chứng: thẩm định đọc biên bản và đối chiếu SHA/giá trị giữa hai worker và checker; **chưa tự tính lại SHA trên chính tệp nhị phân merges**, nên không tuyên bố thực hiện independent binary rehash bổ sung. Bộ kiểm định E0 đã PASS trong lượt nguyên gốc.

## Nguồn chương trình thực thi tái lập

Đưa **đúng từng byte** nguồn launcher V4 đang dùng vào `scripts/p01/` trên nhánh thẩm định. SHA-256 `7b36c6657957367908d26190b600e5e0b39c93007e455c0e20345ef48b29f2af` và Git blob SHA `6baf7f94405a6e83ba40c92984f42f0531519ad4` đã được đối chiếu. Trong launcher có engine Python SHA `2f1b85c52b198046ffb472f284488b6d0ce17bcff7697062f6767e6f0ae6a53d` và independent checker SHA `ae07e11942e09cd910231e48f86d0e8d2d541ca80f8abbb6fbdcf2476ccb67c1` (dạng nén base64 được so SHA lúc chạy).

Không đưa văn bản Wikipedia, TEST hay tệp `merges.ttmbpe` lên GitHub. Bảo toàn marker gốc, toàn bộ lỗi trước marker và S1 native FAIL lịch sử.

## Phán quyết theo tiêu chí đóng

| Gate | Kết quả | Căn cứ |
|---|---|---|
| K1 B0/B1 | PASS_SCOPED | F0 lịch sử + E0 byte round-trip/2048-token BPE |
| K2 H03 | PASS_SCOPED | 30 nhóm độc lập, 24/3/3, leakage 0 |
| K3 F1 | PASS_SCOPED_INTERNAL | 30 WP revision pin/attribution/CC BY-SA 4.0, rủi ro ngoại lệ giữ riêng |
| K4 H05 | PASS_FOR_DOCKER_ROUTE_ONLY | Docker Linux read-only/CPU/RAM/PID guard kiểm thử trước marker; không tái thẩm định S1 Windows |
| K5 E0 + independent QA | PASS | Hai worker SHA đồng nhất, checker độc lập PASS |
| Phase QA | PASS_SCOPED | Hợp lệ cho phạm vi WP30; không chứng minh chất lượng mô hình hoặc quyền thương mại |
| Merge gate | PENDING | Phải xác minh diff/nguồn, hợp nhất branch theo quy trình |
| P02 | NOT_OPENED | Chỉ mở sau merge/closure |

## Công việc tiếp theo hữu hạn

1. Kiểm tra cây nhánh, nguồn launcher, hồ sơ E0 và dòng lineage L0010; đảm bảo source exact Git blob, không đưa corpus/TEST vào GitHub.
2. Hợp nhất qua PR sau phán quyết độc lập; **không tự merge trong bước này**. P01 đóng ở main sau hợp nhất.
3. Mở P02 Transformer Core, dùng P00 làm baseline và P01 tokenizer 2048 token; **không dùng BPE ID >=256 với mô hình P00 đang khóa vocab=256**. Kiểm tra shape/gradient/causal/reference parity; không mở P03 trước P02 PASS.
4. P03 huấn luyện micro-batch trên CPU; nếu chuyển dữ liệu WP30 vào huấn luyện GPT phải có quyết định phạm vi sử dụng mới, không tự suy từ quyền `BPE_E0_ONLY`. P04 mới mở TEST đúng giao thức khóa.

`lineage.md` chỉ thêm dòng khoa học E0 PASS trong L0010; không ghi các lỗi Docker/PowerShell vào lineage mới. P00–P12 bất biến.


## Nguồn gốc hồ sơ kỹ thuật và phạm vi hợp nhất

Nhánh nguồn kế thừa `8bdf3129f47be0f2dd5d48583387803014656bfe` có nhiều tài liệu/receipt tiền kiểm cũ; các bằng chứng này tiếp tục tồn tại nguyên vẹn tại commit đó và các nhánh lịch sử. Nhánh phát hành sạch **không hợp nhất 290 tệp QA/nguồn kỹ thuật không liên quan**. Trên `main`, lineage chuẩn dừng ở `L0009`, nên dòng khoa học mới có ID `L0010`, không sử dụng `L0020` của nhánh thẩm định chưa hợp nhất. Các nhánh lịch sử giữ nguyên, không bị viết lại.
