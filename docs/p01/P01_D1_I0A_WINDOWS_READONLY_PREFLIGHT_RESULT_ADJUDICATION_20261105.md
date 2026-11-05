# P01 D1 — Thẩm định kết quả tiền kiểm Git/Windows I0A chỉ đọc

**Mã công việc:** `TTM_P01_D1_I0A_WINDOWS_READONLY_PREFLIGHT_RESULT_ADJUDICATION`  
**Ngày:** 05/11/2026. **Nhánh:** `design/p01-tokenizer-data-prereg-20261105` / PR #4 (Draft).  
**Gốc khóa:** GitHub main `92facee15d7c0d46b0e84ddf5b6d8b2073e078f7`.  
**Kết luận tổng:** `READONLY_OBSERVATION_PASS`, `I0A_PREAUTH_ADMISSION=HOLD`, `I0A_IMPLEMENTATION_PERMIT=NOT_GRANTED`.

## 1. Provenance và giới hạn bằng chứng

Người dùng dán đoạn PowerShell trực tiếp vào phiên Windows PowerShell 5.1, bao trong `@(...)`, gửi console hoàn tất từ `TTM_P01_I0A_READONLY_BEGIN` đến `TTM_P01_I0A_READONLY_END`.

Bản chép console được lưu tại:
`artifacts/qa/p01/TTM_P01_I0A_WINDOWS_READONLY_USER_CONSOLE_20261105T142138Z.txt`.

- Nguồn: **console do người dùng cung cấp**; không có chữ ký máy hoặc chứng thực quá trình chạy độc lập, không có SHA-256 trên toàn bộ mã đã dán. **Không gán SHA-256 của một script khác cho đoạn dán này.**
- Thời điểm console: `2026-11-05T14:21:38.5319680Z`, tức **21:21:38 ICT (+07)**.
- `READONLY_PREFLIGHT=PASS_OBSERVATION_ONLY` là thông báo của chương trình, không phải permit triển khai; không đồng nghĩa filesystem ACL đã được audit hoặc không có bất kỳ thay đổi nào do tiến trình khác.
- GitHub PR #4 đã được kiểm tra lại với nhánh `main` đúng khóa, chưa merge, Draft. Đây là kiểm tra metadata từ GitHub, tách biệt console của Windows.

## 2. Bảng kiểm tra Windows đúng phạm vi

| Điều kiện | Console thực tế | Ngưỡng/đối chứng | Kết luận |
|---|---|---|---|
| Host | `DESKTOP-4PSD0G2` | Windows đích | PASS_OBSERVED |
| Git root | `D:\WORK\RESEARCH\TokenToModel-Lab` | Exact project root | PASS_OBSERVED |
| Origin | `https://github.com/minhtri22/TokenToModel-Lab.git` | Exact URL | PASS_OBSERVED |
| Branch hiện tại | `main` | `main` | PASS_OBSERVED |
| Local main và origin/main | `92facee15d7c0d46b0e84ddf5b6d8b2073e078f7` | GitHub main | PASS_OBSERVED |
| Root status | 0 entry | Không có thay đổi được báo | PASS_OBSERVED |
| P00 HEAD | `382da2c52d0fb4efe1cd9de5c92e68de79a52a20` | P00 pinned | PASS_OBSERVED |
| P00 status | 0 entry | Giữ nguyên worktree P00 | PASS_OBSERVED |
| Worktree count | 2 | main và P00 | PASS_OBSERVED |
| P01 candidate exists | False | Không được tạo | PASS_OBSERVED |
| Reparse trên các path hiện hữu đã liệt kê | Không có `HOLD_REASON=REPARSE_POINT` | Nếu phát hiện reparse thì HOLD | PASS_SCOPED_OBSERVED |
| RAM available | `9.345 GiB` | `>=8 GiB` | PASS_SNAPSHOT |
| D: available | `34.830 GiB` | `>=16 GiB` | PASS_SNAPSHOT |
| D: sau dự phòng | `32.768 GiB` | `>=12 GiB` | PASS_SNAPSHOT |
| Hold count | `0` | `0` | PASS_OBSERVATION_ONLY |

**Biên an toàn:** RAM dư `1.345 GiB` so với ngưỡng; D: dư `18.830 GiB`; sau dự phòng dư `20.768 GiB`. Khi đến thời điểm xin permit phải đo lại vì các số này có thể thay đổi.

## 3. Thẩm định riêng ba điều kiện tồn đọng

| Cổng | Quyết định thẩm định | Phạm vi và bất định |
|---|---|---|
| `I0A-01` Git/Windows | **PASS_READONLY_OBSERVATION** | Git root/origin, branch/main/remote, P00 HEAD, hai worktree và trạng thái sạch được quan sát. Chưa chứng minh cấu hình Git hooks, nested reparse hoặc ACL toàn bộ workspace. |
| `I0A-02` worktree/path | **HOLD_FULL_PATH_ACL_AUDIT** | P01 candidate hiện không tồn tại, hai worktree nằm trong root, các path hiện hữu mà script đã liệt kê không báo reparse. Tuy nhiên **chưa có kiểm toán ACL, canonical target của mọi thành phần lồng nhau, xung đột tên sau normalize và quyền ghi deny-by-default**; không thể tự chuyển thành PASS hoàn toàn. |
| `I0A-07` tài nguyên | **PASS_TIMESTAMPED_CAPACITY_SNAPSHOT** | RAM/D: đạt ngưỡng tại 21:21:38 ICT; **không có QA guard toàn job**, không bảo đảm nguồn lực còn đủ khi permit được xét ở thời điểm khác. |

Không được dùng `HOLD_REASON_COUNT=0` làm bằng chứng những phép kiểm tra **không tồn tại trong chương trình** (ACL sâu, token restricted, write broker, filesystem isolation) đã đạt.

## 4. Ma trận I0A-01..09 sau biên bản

| Cổng | Trạng thái |
|---|---|
| `I0A-01` Git / worktrees / cleanliness | **PASS_READONLY_OBSERVATION** |
| `I0A-02` scoped path / ACL | **HOLD_FULL_PATH_ACL_AUDIT** |
| `I0A-03` golden bytes & oracle | **PASS_DESIGN_ONLY** |
| `I0A-04` F0-only source | **PASS_DESIGN_ONLY** |
| `I0A-05` canonical job-commit limit | **PASS_DESIGN_ONLY** |
| `I0A-06` planned guard contract | **PASS_DESIGN_ONLY** |
| `I0A-07` timestamped RAM/D: | **PASS_SNAPSHOT_ONLY** |
| `I0A-08` source and checker allowlist | **PASS_DESIGN_ONLY** |
| `I0A-09` exact permit / owner decision | **NOT_GRANTED** |

**Kết quả:** 5 `PASS_DESIGN_ONLY`, 2 `PASS_READONLY_OR_SNAPSHOT`, 1 `HOLD_EVIDENCE`, 1 `NOT_GRANTED`.

Các kết quả scoped PASS không phải giấy phép triển khai, kiểm tra tĩnh, QA động hoặc thực nghiệm. Không được cộng thành `I0A=PASS`.

## 5. Quyết định kế tiếp và giới hạn

Trước khi đề nghị permit I0A riêng: cần hoàn tất đánh giá **chỉ đọc** các đường dẫn con ứng viên và ACL/thao tác ngoài broker, đọc lại trạng thái Git/tài nguyên đủ gần thời điểm cấp phép; sau đó trình **quyết định exact HEAD + phạm vi tệp + người có quyền + số lượt + tiêu chí dừng**. Không tự mở I0A chỉ vì Git sạch và RAM/đĩa đủ.

H02 vẫn chỉ `F0_ONLY_DESIGN_AND_ORACLE_REVIEW`, chưa có source F1/F2 `ALLOW`; D1 khoa học chưa khóa; Job Object và write broker chưa triển khai, QA0/E0 chưa có quyền. Golden bytes chỉ là đặc tả; `lineage.md` khoa học **không được bổ sung kết quả vận hành như thành tích khoa học** trong bước này. Bằng chứng hạ tầng nằm ở `docs/p01` và `artifacts/qa/p01`.

## 6. Phán quyết cuối

`TTM_P01_I0A_WINDOWS_READONLY_PREFLIGHT=PASS_OBSERVATION_ONLY`  
`TTM_P01_I0A_01_GIT_STATUS=PASS_READONLY_OBSERVATION`  
`TTM_P01_I0A_02_PATH_SCOPE=HOLD_FULL_PATH_ACL_AUDIT`  
`TTM_P01_I0A_07_CAPACITY=PASS_TIMESTAMPED_SNAPSHOT`  
`TTM_P01_I0A_PREAUTH_ADMISSION=HOLD`  
`TTM_P01_I0A_IMPLEMENTATION_PERMIT=NOT_GRANTED`  
`TTM_P01_QA0_DYNAMIC_PERMIT=NOT_GRANTED`  
`TTM_P01_E0_SCIENTIFIC_PERMIT=NOT_GRANTED`  
`TTM_P01_D1_SCIENTIFIC_PREREG_LOCK=NOT_GRANTED`  
`P01_WORKTREE_CREATION_AUTHORIZED=false`  
`P01_DATA_DOWNLOAD_AUTHORIZED=false`  
`P01_BPE_TRAINING_AUTHORIZED=false`  
`PR4_MERGE_AUTHORIZED=false`  
`P00_CLEANUP_AUTHORIZED=false`

**Bước thực hiện tiếp theo:** `TTM_P01_D1_I0A_PATH_ACL_READONLY_COMPLETION_AND_SEPARATE_PERMIT_DECISION` — thẩm định bổ sung ACL/path chỉ đọc rồi, nếu đủ, mới đưa quyết định permit I0A cụ thể. Không tạo worktree hoặc mã P01 trong bước này.
