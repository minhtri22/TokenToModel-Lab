# P01 D1 — Thẩm định độc lập bằng chứng tiền cấp quyền I0A F0 (thiết kế)

**Mã công việc:** `TTM_P01_D1_I0A_F0_STATIC_IMPLEMENTATION_PREAUTH_EVIDENCE_AND_DESIGN_ADJUDICATION`  
**Ngày:** 05/11/2026. **Đường:** `design/p01-tokenizer-data-prereg-20261105` / PR #4.  
**Trạng thái:** `DESIGN_REVIEW_COMPLETED_WITH_HOLD` — `I0A_PERMIT=NOT_GRANTED`.  
**Giới hạn:** đọc GitHub, RemoteMCP metadata và phép tính byte mẫu trong môi trường đánh giá riêng. **Không viết/chạy mã checker/guard P01, không tạo worktree, không thực hiện Windows PowerShell mới, không tải corpus hoặc huấn luyện**.

## 1. Nguồn gốc và phép thẩm định độc lập

| Nguồn | Git blob SHA-1, phiên đọc lại | Vai trò |
|---|---|---|
| `P01_D1_I0A_GOLDEN_BYTES_DESIGN_20261105.md` | `8f991834e3356449f0325cc202a758fc6ac99b3f` | Golden byte merges/snapshot/JCS |
| `P01_D1_I0A_FILESYSTEM_AND_SOURCE_ALLOWLIST_DESIGN_20261105.md` | `329a04440cf61f361503ea0ee01f75e507ecf6d8` | Đường dẫn ứng viên và danh mục tệp mã |
| `P01_D1_I0A_WINDOWS_GIT_RESOURCE_READONLY_EVIDENCE_20261105.md` | `6d283fd5be175d523891f5a991cdca638695b37f` | Quan sát trực tiếp Git metadata, khoảng trống Windows |
| `P01_D1_I0_PREAUTH_GATE_CONTRACT_20261105.md` | `1be5f0de7d3e45b030d393310cc377db911f57a1` | Hợp đồng 9 cổng I0A |

**Kiểm tra golden ở hai đường riêng:** byte nhị phân M01/snapshot/JCS đã được xây dựng bằng thư viện định dạng/băm thông dụng trong môi trường đánh giá, sau đó đọc lại từ GitHub và phân tích các trường theo vị trí bằng phép kiểm tra riêng. **16/16 bất biến định dạng** khớp (magic, độ dài, little-endian, ID, record count, ID nguồn bị từ chối, JCS key order/length/null). Đây là kiểm tra **đặc tả**, không chạy code P01 hoặc một checker bên thứ ba.

**Các SHA-256 golden:**
- merges **47 byte**: `11c72190c6f3b757d260c426c357a4de8ff36313495f2299da81638386289e8d`;
- snapshot minh họa **199 byte**: `026744455f6a71b178702ce077737ff9c416b3cc716b5711f6b8ef6d0779697d`;
- JCS tối thiểu **109 byte**: `492204b007b172f734a38bf0d80db357a57efff90e319f2dbaf3b63f9135e826`;
- JCS đầy đủ khóa nhưng **không đủ điều kiện receipt thực thi**, **774 byte**: `d09396eb72ff318e9820d76bb999acae01cfeb9547ae80187d0e33d970119beb`.

Mẫu snapshot gắn `F0-SPEC-NOT-APPROVED` và manifest có `DESIGN_ONLY_NO_RUN`/null nên **không bao giờ** được coi là source `ALLOW`, chứng cứ chạy hoặc quyền khoa học. Một trình kiểm tra cho `PASS` nghiên cứu chỉ vì hash trên mẫu này khớp là **FAIL kiểm soát bằng chứng**.

## 2. Bảng thẩm định I0A-01..09

| Cổng | Tình trạng bằng chứng mới | Quyết định cấp I0A |
|---|---|---|
| **I0A-01 — Git/Windows** | GitHub main = local main = local origin/main `92face...`; P00 branch `382da...`; remote origin đúng; worktree metadata trỏ P00. **Chưa có `git status`, xác minh chính HEAD qua Git CLI và reparse hiện thời trên Windows.** | **HOLD_EVIDENCE** |
| **I0A-02 — Đường dẫn/worktree** | Đã nêu đúng worktree ứng viên và deny-by-default danh mục đường dẫn; **chưa có cổng va chạm path/ACL/junction hoàn tất trên máy Windows**. | **HOLD_EVIDENCE** |
| **I0A-03 — Golden bytes/oracle** | Đã có merges 47, snapshot 199, manifest JCS 109/774 byte và SHA-256; 16/16 kiểm tra cấu trúc phù hợp. Bản snapshot/manifest cố tình không đủ quyền chạy. | **PASS_DESIGN_ONLY** |
| **I0A-04 — Phạm vi F0** | `F0_ONLY_DESIGN_AND_ORACLE_REVIEW` được chọn. F1/F2 và scientific TEST bị loại. | **PASS_DESIGN_ONLY** |
| **I0A-05 — Metric và ngân sách** | `max_job_commit_bytes=4294967296`, wall-clock 1800s, quota 2 GiB, nguồn 64 MiB là chuẩn thiết kế kế nhiệm; RSS cũ được giữ lịch sử. | **PASS_DESIGN_ONLY** |
| **I0A-06 — Hợp đồng Job Object** | Có suspended → assign → verify → resume, child containment, no breakaway, kill-on-close, disk broker tách biệt, âm tính W01–W12. | **PASS_DESIGN_ONLY** |
| **I0A-07 — Tài nguyên tức thời** | Snapshot ngày 05/11/2026 11:01:18Z đo RAM 10.959 GiB, D: 34.869 GiB. **Chưa đo lại khi thẩm định permit**, node heartbeat không mang RAM/đĩa tức thời. | **HOLD_RECHECK** |
| **I0A-08 — Mã/QA allowlist** | Đã định nghĩa **10 đường dẫn tệp ứng viên** tách generator/checker/guard/manifest, cấm trainer và source P00; chưa viết mã hoặc pin SHA checker (bởi I0A chưa cấp). | **PASS_DESIGN_ONLY** |
| **I0A-09 — Quyết định chủ sở hữu** | Chưa có quyết định riêng cho chính exact branch/worktree/source. | **NOT_GRANTED** |

**Tổng**: **5 `PASS_DESIGN_ONLY`, 3 `HOLD_EVIDENCE`, 1 `NOT_GRANTED`**. Tất cả 9 cổng đều **chưa có permit thực thi**; số 5/9 không phải tỷ lệ sẵn sàng triển khai hay kiểm thử thành công.

## 3. Đối chiếu an toàn và trường hợp phải từ chối

1. Không có `git status` mới hoặc có source dirty/untracked va chạm ⇒ `I0A_GIT_HOLD`, không dùng `git clean`/reset.
2. Worktree P01 ứng viên có sẵn, nhánh HEAD thay đổi, worktree ngoài project, symlink/junction thoát root ⇒ `I0A_PATH_HOLD`.
3. Golden blob khác một byte, có manifest giả lập tự nhận `PASS`, source `F0-SPEC-NOT-APPROVED` bị cho `ALLOW` ⇒ `I0A_GOLDEN_OR_RIGHTS_FAIL`.
4. RAM/D: mới xuống dưới ngưỡng ⇒ `I0A_RESOURCE_HOLD`. Snapshot 18:01 cùng ngày không thay thế phép đo tức thời.
5. Worker chưa được gắn Job Object đúng, write broker/ACL chưa chặn bypass, `max_peak_rss_bytes` bị dùng thay `max_job_commit_bytes` ⇒ `QA0_GUARD_HOLD`, không mở chạy kỹ thuật.
6. Thiếu permit bằng văn bản hoặc phạm vi nguồn vượt F0-only ⇒ `I0A_PERMISSION_DENIED`, không tạo mã/fixture hoặc tự bổ sung quyền.

## 4. Chương trình Windows chỉ đọc đã chuẩn bị

`TTM_P01_I0A_READONLY_WINDOWS_PREFLIGHT.ps1`, SHA-256 `deb82ad16380dfd53c7def559cb9a7ec392321a84d6bc2cb79ee0ac2123e0012`. Kiểm tra tĩnh cho thấy không có lệnh fetch/reset/clean, không có gọi `git worktree add/remove`, không tạo biên bản trên máy; script đọc Git với `--no-optional-locks` và RAM/D: bằng CIM. **Chưa chạy Windows PowerShell 5.1 trong bước này**, nên kết quả script ở trạng thái `NOT_EXECUTED`.

Nếu chủ sở hữu chạy và cung cấp console, báo cáo mới cần đối chiếu thời điểm, tên máy, root/origin, status/tracked/untracked, HEAD P00, worktree P01 chưa tồn tại, RAM/đĩa và SHA script. Thiếu trường hoặc lỗi ⇒ HOLD, không đoán/ghi PASS.

## 5. Phán quyết độc lập (Adjudication)

`TTM_P01_D1_I0A_PREAUTH_EVIDENCE_REVIEW=COMPLETED_WITH_HOLD`  
`TTM_P01_D1_I0A_GOLDEN_BYTES=PASS_DESIGN_ONLY`  
`TTM_P01_D1_I0A_ALLOWLIST=PASS_DESIGN_ONLY`  
`TTM_P01_D1_I0A_GIT_REFS=PASS_READONLY_SCOPED`  
`TTM_P01_D1_I0A_GIT_STATUS_AND_PATH_COLLISION=HOLD`  
`TTM_P01_D1_I0A_FRESH_RESOURCE_SNAPSHOT=HOLD`  
`TTM_P01_D1_I0A_PERMISSION=NOT_GRANTED`  
`TTM_P01_D1_SCIENTIFIC_PREREG_LOCK=NOT_GRANTED`  
`TTM_P01_I0A_STATIC_IMPLEMENTATION_PERMIT=NOT_GRANTED`  
`TTM_P01_QA0_DYNAMIC_EXECUTION_PERMIT=NOT_GRANTED`  
`TTM_P01_E0_SCIENTIFIC_EXECUTION_PERMIT=NOT_GRANTED`  
`P01_WORKTREE_CREATION_AUTHORIZED=false`  
`P01_DATA_DOWNLOAD_AUTHORIZED=false`  
`P01_TOKENIZER_TRAINING_AUTHORIZED=false`  
`P01_MODEL_TRAINING_AUTHORIZED=false`  
`PR4_MERGE_AUTHORIZED=false`  
`P00_CLEANUP_AUTHORIZED=false`

**Bước tiếp theo:** `TTM_P01_D1_I0A_WINDOWS_READONLY_PREFLIGHT_RESULT_ADJUDICATION`: chỉ nhận console từ script đã pin, rà soát I0A-01/02/07 và sau đó trình một quyết định cấp quyền I0A **mới, riêng biệt**, không tự cấp.
