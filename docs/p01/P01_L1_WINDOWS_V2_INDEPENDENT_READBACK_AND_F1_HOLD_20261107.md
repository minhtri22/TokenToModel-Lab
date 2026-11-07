# TTM P01 — Windows V2 QA: phán quyết PASS có giới hạn và F1 HOLD

Ngày 07/11/2026. Repo: `minhtri22/TokenToModel-Lab`. Nhánh kiểm toán: `audit/p01-l1-windows-argv-recovery-v2-20261107`.

## Đối chứng và kết quả

Biên bản V2 được lưu tại `artifacts/qa/p01/TTM_P01_L1_WINDOWS_ARGV_RECOVERY_V2_20261107.json`, giữ **đúng byte** với tệp người dùng gửi. SHA-256: `7248d741c1e206a445873cc49d9e2acb44ad4bba906498d08f70e9ed04d4a5f5`; Git blob SHA-1: `1b3165fb5b793cbab7d1c2bda39d1e4c6274d596`.

Đã đọc độc lập trực tiếp stdout/stderr và receipt từ Windows. Nhật ký stderr ghi rõ 7 bài đều `ok`, `Ran 7 tests in 0.059s`, `OK`; receipt ghi `test_exit_code=0`, code pin `b481a90fa82abb194f5ae60945a5ad4408b5a425`, test blob `6e9b024a60461d76220ef2e8bdce51b68afc420c`. SHA của stderr được biên bản ghi nhưng **chưa băm lại từng byte độc lập**.

HEAD local không đổi `92facee15d7c0d46b0e84ddf5b6d8b2073e078f7`; SHA-256 `lineage.md` giữ `05ed529550f62bc1d35bdf93036724b7cadefa9c5d073c71412e9e0dbfb0172a`; tracked clean sau. F0 không chạy lại. Biên bản và marker V1 FAIL được giữ nguyên; marker V2 độc lập. Dọn thư mục tạm chỉ đúng nội dung script sở hữu được console báo PASS.

## Ma trận cổng hữu hạn

| Cổng | Quyết định và giới hạn |
|---|---|
| K1 — B0/B1 | `PASS_SCOPED_WINDOWS_ALGORITHM`, không phải đo BPE trên F1 |
| K2 — dedup/split | `PASS_SCOPED_WINDOWS_FIXTURE`: 34 tài liệu tổng hợp, 30 nhóm, TRAIN/VALIDATION/TEST 24/3/3, negative leak; tiếp nhận fixture bằng mock có kiểm soát |
| K3 — F1 rights/PII | `HOLD_SOURCE_RIGHTS`: chưa có snapshot do chủ dự án chọn và bằng chứng ALLOW |
| K4 — runtime E0 | `HOLD_ROUTE_DECISION`; không tự coi S1 FAIL là cổng cho mọi tuyến E0 |
| K5 — E0 và đóng P01 | `NOT_EXECUTED` / `P01=OPEN`; `P02=NOT_OPENED` |

PASS này chứng minh bộ QA scoped thực sự chạy trên Windows; **không** chứng minh production admission F1, khóa khoa học D1, hai tiến trình TRAIN-only hay QA độc lập ngoài tổ chức. Không mở E0 hoặc P02.

## Bước tiếp theo

Chủ dự án xác định đúng một snapshot F1 có bằng chứng quyền tokenizer training và tạo dẫn xuất, SHA-256, trạng thái PII và >=30 nhóm độc lập sau chống trùng. Lập manifest và quyết định `ALLOW/HOLD` có chứng cứ. Chốt tuyến E0 và các bảo vệ bắt buộc đúng tuyến. Chỉ sau K3/K4 đủ điều kiện mới chạy E0 đúng một lượt, hai tiến trình sạch cùng SHA, TEST niêm phong, thẩm định đóng P01 rồi mới xét P02.

Không làm lại F0, S1 hoặc QA L1 đã PASS; không sửa P00, HEAD gốc, `lineage.md`, marker hay biên bản PASS/FAIL; không merge/clean/reset.
