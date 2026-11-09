# G1 — Hợp đồng phạm vi chủ sở hữu và sửa đổi phương pháp v1d (ứng viên)

**Ngày:** 2026-11-09  
**Trạng thái:** `DESIGN_ONLY`, `OWNER_SCIENCE_PERMIT=NOT_ISSUED`, `G1_SCIENCE_LOCK=HOLD`.

## 1. Không có quyền khoa học được suy diễn

Chủ sở hữu đã cho phép xây dựng phần cứng/phần mềm kỹ thuật và tạo manifest metadata/hash cục bộ trên T1 TRAIN, **không** cho phép tự chạy science G1, đọc TEST riêng tư, chuyển TinyStories gốc lên Colab, tải lại Qwen technical one-shots đã tiêu thụ, hay công bố các vector ẩn của teacher. Lượt triển khai này chỉ dùng dữ liệu giả và file tạm của môi trường thử nghiệm. Một lời gọi hàm hoặc JSON `owner_authorized=true` không phải chữ ký hợp lệ.

Quyết định sau QA và phân xử độc lập phải là **một owner admission** bao trọn: model pin, source location, quyền dữ liệu, thiết bị, danh tính các principal, khóa công khai trusted launcher, phạm vi dẫn xuất, thời hạn lưu, mục tiêu chạy, `run_id`, các Git blob thực thi và witness.

## 2. Ranh giới quyền production phải được thi hành bởi OS/hạ tầng

| Principal giả định (chưa cấp SID/key) | Quyền cần có | Quyền **không** được có |
|---|---|---|
| Owner/admission signer | Phê duyệt release và ký contract riêng; khóa bí mật không nằm trong repo | Không cấp phép science qua flags trong worker |
| Launcher/controller service | Kiểm chữ ký + source pins; tạo process token worker bị hạn chế; ghi trusted ledger | Không đọc raw TEST trước freeze; không cấp phép thay owner |
| Split broker | Giữ TEST plaintext bằng ACL/principal riêng; cấp TEST **chỉ sau** verified `FIT_FROZEN` và witness ack | Worker TRAIN/DEV không thể nhìn thấy TEST kể cả qua hardlink/junction |
| Trusted pack writer | Ghi content-addressed pack + signed provenance và commit; xác minh bytes đã đọc | Worker không được sửa receipt/trusted digest/ACL |
| External witness | Cấp monotonic sequence có chữ ký/ack, ngoài miền rollback của controller/worker | Controller không xóa/viết lại lịch sử; cùng user account trên D: là chưa đủ |
| GPU worker | Chỉ process model pinned, đọc TRAIN/DEV đã được broker cấp; TEST sau permit + event | Không có quyền sửa controller/witness, source gốc, Git metadata |

**Điều kiện bảo vệ:** phải dùng SID, DACL/ACL và negative `AccessDenied` thật trong Windows (hoặc principal/job namespace tương đương bên Colab), không coi check `Path.is_symlink()` hoặc ghi witness sang thư mục khác cùng user là cách ly production. Đã xác minh tham khảo hệ điều hành Microsoft Job Objects và lệnh `icacls` ở tài liệu chính thức; nguồn SDK: `https://learn.microsoft.com/en-us/windows/win32/procthread/job-objects`, `https://learn.microsoft.com/en-us/windows-server/administration/windows-commands/icacls`.

**Location nội bộ ứng viên, chưa tạo:** chỉ bên trong `D:\WORK\RESEARCH\TokenToModel-Lab\_trusted\g1\{controller,worker,broker,witness}`. Nếu witness thật ở cùng volume/owner và có thể cùng rollback, không PASS. Chuyển sang trusted witness độc lập phải được chủ sở hữu duyệt địa điểm và độ tin cậy. `RemoteMCP` hay một thư mục GitHub không tự động là witness chống rollback.

## 3. State contract không phát hành micro-permit

`ADMITTED → TRAIN_COMMITTED → DEV_COMMITTED → FIT_FROZEN → TEST_EXTRACT_CONSUMED → TEST_PACK_COMMITTED → TEST_READ_CONSUMED → TERMINAL`.

- Mọi sự kiện có `run_id`, số thứ tự, SHA previous/event, SHA payload, signer/authority pin; không đọc bất kỳ TEST byte nào trước **external witness ack** của `TEST_EXTRACT_CONSUMED`.
- Ghi pack theo hai pha, kiểm SHA trên **cùng bytes đã parse**, receipt do writer được phân quyền phát hành và ghi vào ledger. Nếu crash/receipt-missing/orphan file → STOP terminal, không cấp lượt khác qua rollback.
- `G1_FINALIZE` phải xác nhận đủ train+DEV freeze với exact schema/pins, không cho TEST debug, tune, hoặc rerun.
- GPU supervisor chạy **ngoài tiến trình** có quyền `TerminateJobObject`/kill group, timeout cộng dồn source ≤3.600s, target ≤3.600s, tổng ≤7.200s, peak VRAM giới hạn, fail-closed khi mất watchdog. Bài test CPU kill không phải xác nhận T4.
- No dynamic `pip`/model revision. Chỉ dùng Qwen checksum/revisions và manifest đã niêm phong.

## 4. Sửa đổi phương pháp v1d cần reviewer chấp thuận trước TEST

Tất cả giữ TRAIN 128 / DEV 64 / TEST 64, 8 continuation pairs, ridge grid `[1,10,100]`, 1.000 TRAIN-pair shuffled fits với DEV selection, 1.000 CKA nulls, 2.000 paired bootstrap; primary layer `hidden_states[28]`, Qwen0.6/1.7 frozen.

| Phiên bản sửa đổi | Quy tắc ứng viên | Phản biện còn cần |
|---|---|---|
| v1a mapping/dedup | Nội dung T1 SHA về `first occurrence`, loại exact normalized story/prefix duplicate **trước** phân tập 128/64/64 | Chứng minh không lệch chọn mẫu từ thứ tự nguồn, nhóm near-duplicate/lineage và không dùng TEST để tinh chỉnh |
| v1b paired bootstrap | Estimand là lợi ích dự đoán so với TRAIN-mean, dùng denominator `SST_TEST` toàn bộ đã khóa để mẫu bootstrap 63+1 không làm SST suy biến | Có phù hợp ý nghĩa CI mục tiêu? Không đánh tráo CI với shuffle-null p95; `INCONCLUSIVE` khi toàn bộ TEST degenerate |
| v1c CKA | Chuẩn hóa một lần, dùng chung centered Gram observed/null; tie nếu `null >= observed - 64*eps_float64*max(1,abs(observed))` | Reviewer xác minh sai lầm v1b, type-I/power của tolerance mới, null exchangeability, scaling và degeneracy. Không chọn tolerance sau xem TEST |
| Ranh giới tuyên bố | G1 chỉ `scoped feasibility`, A→P vẫn tuyến tính theo source; luôn báo B-direct, target-oracle, mean, shuffle và CKA | Không tuyên bố cơ chế nhân quả SIX hoặc tác động lên TTM từ G1. TEST 64 chưa có power 80% được chứng thực |

**Quyền sửa hợp đồng:** tác giả chỉ tạo amendment candidate. Một reviewer **thực sự độc lập** phán quyết PASS/HOLD/FAIL kèm exact blob và dấu vết phương pháp. Reviewer PASS vẫn không phát hành owner science permit.

## 5. Sáu gate cùng trong một admission

1. Authority: khóa owner tin cậy + launcher/chữ ký/blob chính xác, đóng mới sau chứng thực.
2. Split broker: OS-deny TEST trước freeze trên principal worker.
3. Writer/ledger: nguồn pack và giao dịch crash-consistent, trusted receipt.
4. One-shot: witness monotonic **ngoài miền rollback worker/controller**.
5. Watchdog: OS-level forced kill thực, cumulative GPU resource budget.
6. Methods: phản biện thống kê v1a–v1d và mẫu hạn chế.

**Hiện tại cả sáu vẫn `HOLD/NOT_TESTED_PRODUCTION`**. Không nâng synthetic QA thành science authorization.
