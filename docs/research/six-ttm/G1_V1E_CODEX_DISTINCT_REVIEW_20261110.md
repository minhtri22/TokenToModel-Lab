# TTM × SIX G1 v1e — Kiểm định độc lập khoa học và bảo mật

Ngày 10/11/2026. **Phán quyết tổng thể duy nhất `HOLD`.**

## 1. Nguồn bất biến và Git

- Origin đã đối chiếu với `https://github.com/minhtri22/TokenToModel-Lab.git`. Commit v1e ghim là `1efca4ca080572dcd22bbe658701b221ca46f7dd`, được fetch riêng trong `_tmp` của dự án.
- **8/8 Git blob SHA-1 PASS**. Byte của cả tám đối tượng Git đồng nhất với ZIP và **8/8 SHA-256 PASS**. Danh mục hash đầy đủ nằm trong receipt JSON đi kèm.
- ZIP SHA-256 là `fad5992bac357367c67ee7448209e02247f9566fe6c01a09d69efae2a2b1d55f`. Wrapper owner SHA-256 là `9dbfa1eab3242f3d4bb5ef4254eea9b072007b0c5ca4ab628a13b358f8b4a1bc`.
- `main` được xác minh ở `b57b44e7287f842e81050c1faee337f636333dd0`. HEAD nhánh triển khai đã chuyển đến `1788a47b319dc4054672d110d1b8c33adc45f4a0` khi kiểm tra. Toàn bộ đánh giá dùng commit bất biến v1e nêu trên.

## 2. Hai ca Windows Win32

- Đã đọc receipt owner gốc trong `_tmp/G1_WIN32_FAILURE_MODES_20261110_014528_d95df4e35c3e`. SHA-256 raw receipt là `abd96217121dbd442f4b7eae5e5b49a08d761f51518a01bcc60ea43672159924`, khớp tệp `SHA256_RECEIPT.txt`.
- `harmless-assign-fault-qa` (sau CreateProcess, trước AssignProcessToJobObject) và `harmless-resume-fault-qa` (sau Assign, trước Resume) đều có `test=HARMLESS_FAULT_INJECTION`, `cleanup_verified=true`, `child_exited=true`.
- Cả hai log xác nhận `production_qualified=false`, `real_gpu_used=false`, `science_executed=false`. Hash của hai stdout và hai stderr khớp raw receipt, hai stderr rỗng.
- **OWNER_WINDOWS_QA_RECEIPT=PASS_VERIFIED**. **INDEPENDENT_WIN32_EXECUTION=NOT_TESTED** vì reviewer không chạy lại hai ca. Receipt không đủ để chứng minh trạng thái toàn process tree, liveness hậu kỳ, hay exit-code transcript độc lập.

## 3. CPU độc lập và rà soát phương pháp

- `AUTHOR_CPU_QA=PASS_61/61` là kết quả lịch sử có trong tệp của bên triển khai. Reviewer không chạy lại 61 ca, cũng không chạy lại QA v1b/v1c hay 45 ca Windows đã khóa.
- Reviewer thiết kế/chạy 13 ca kiểm thử đối kháng Ed25519 bằng khóa tổng hợp tạo trong bộ nhớ. **13/13 nhận đúng kết quả dự kiến**, gồm ký sai trust anchor, đổi v1c HEAD, thay bytes pack, thay nonce, ACK hết hạn và khoa học bị khóa.
- **Phát hiện nguồn candidate** — `verify_owner_admission()` nhận launcher SHA-1 và amendment SHA-256 là các chuỗi toàn số 0 dù đã được ký hợp lệ. Hàm chỉ kiểm định dạng của hai trường, chưa so sánh với expected pins do trusted launcher nắm giữ. ACK được ký vẫn xác minh lại với cùng challenge còn hạn. Cần latest-tip cùng cơ chế nonce single-use của witness độc lập trước release.
- Mô phỏng CKA độc lập với NumPy, seed `20261110`, 64 hàng, 1.000 permutations, 32 bộ tổng hợp cho mỗi điều kiện. Null IID có 1/32 kết quả p<0,05. Tín hiệu ghép cặp có 32/32. Khi 64 hàng thực chất là **8 nhóm × 8 dòng trùng**, với X/Y độc lập theo nhóm, hoán vị theo hàng báo 32/32 p<0,05, còn hoán vị theo nhóm báo 0/32. Đây là phản ví dụ tổng hợp về exchangeability, **không phải bằng chứng T1 có 8 nhóm trùng**. Gram suy biến được phân loại `INCONCLUSIVE`. Mô phỏng hữu hạn này không xác nhận kiểm soát Type-I/power của G1 trên T1.

## 4. Sáu hard gate, một gói

| Hard gate | Trạng thái | Bằng chứng còn thiếu |
| --- | --- | --- |
| Owner authority / trusted launcher | **FAIL** ở exact pin enforcement của candidate | Expected launcher/amendment SHA ngoài signer, signer production và trusted launcher được provision |
| Split broker / worker SID | **NOT_TESTED** production | Worker principal độc lập, negative `AccessDenied` với path, hardlink và junction trước TEST |
| Trusted pack writer / ledger | **NOT_TESTED** production | Writer ngoài worker, atomic recovery, fsync, crash injection và concurrency |
| External monotonic witness | **NOT_TESTED** production | Latest-tip challenge, nonce single-use, ACK từ trust domain độc lập và thử rollback đa miền |
| GPU/OS watchdog | **NOT_TESTED** production | Process-tree containment, supervisor cưỡng chế dừng, hạn mức 3.600 giây/model, 7.200 giây tổng và 12 GiB T4 |
| Scientific methods | **NOT_TESTED** trên T1 thật | Lineage first-occurrence và near-duplicate, group resampling, power prospective TEST=64, amendment cuối trước TEST |

Hai ca Win32 chủ sở hữu chạy có receipt hợp lệ chỉ đóng phần cleanup của child vô hại. Các phép kiểm chữ ký synthetic xác nhận các điều kiện logic mà chúng thử, không tự chứng thực nguồn gốc các trust anchor production.

## 5. Gói khắc phục nhỏ nhất và một quyết định owner

1. Owner đưa **một quyết định `APPROVE_TECHNICAL_PROVISIONING`** nêu rõ host và principal/SID worker, ACL scope broker/TEST, ba trust anchors độc lập, trusted pack writer, vị trí witness chống rollback, GPU supervisor và giới hạn compute. Đây là quyết định provision kỹ thuật.
2. Tại commit triển khai kế tiếp, trusted launcher phải so khớp exact launcher/method SHA với expected pins ngoài payload ký. Writer và witness cần giao dịch bền vững, latest-tip, nonce single-use và cách ly quyền vận hành thực.
3. Gộp các negative tests hệ điều hành, nguồn, crash/concurrency/rollback, GPU guardian và phân xử phương pháp vào **một lượt independent QA tích hợp**. Chỉ sau đó owner mới có thể cân nhắc admission khoa học riêng.

## 6. Kết luận

`G1_SCIENCE_LOCK=HOLD` · `SCIENCE_EXECUTED=NO` · `G1_PRIVATE_TEST_OPENED=NO` · `OWNER_SCIENCE_PERMIT=NOT_ISSUED`.

Receipt JSON độc lập SHA-256 là `47af2897e343567b92ccaa6477445a61fe9b3a651db37ee67debd049175d76a6`. Hai tệp reviewer được lưu cục bộ trong `_tmp` của dự án. Chưa có commit/push bản review này lên GitHub.

**Bước thực hiện tiếp theo** — `TTM_SIX_G1_V1E_INTEGRATED_PROVISIONING_SINGLE_OWNER_DECISION_AND_DISTINCT_QA`.