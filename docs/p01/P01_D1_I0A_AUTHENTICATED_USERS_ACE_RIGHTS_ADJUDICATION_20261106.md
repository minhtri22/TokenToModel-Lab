# P01 D1 — Phân xử chính xác ACE S-1-5-11 và ranh giới cô lập I0A

**Công việc:** `TTM_P01_D1_I0A_AUTHENTICATED_USERS_ACE_RIGHTS_READONLY_QUALIFICATION`  
**Hồ sơ:** `minhtri22/TokenToModel-Lab` / nhánh `design/p01-tokenizer-data-prereg-20261105`, PR #4 (Draft, chưa merge).  
**Căn cứ:** console PowerShell người dùng cung cấp; file tổng hợp có provenance `artifacts/qa/p01/TTM_P01_I0A_AUTHENTICATED_USERS_ACE_DETAIL_USER_TRANSCRIPTION_20261106.md`. Không có full-console SHA/chữ ký node; không chạy lệnh/QA Windows mới.  
**Phán quyết:** `ACE_RIGHTS_QUALIFIED=PASS_SCOPED_READONLY`; `PATH_ACL_ISOLATION=HOLD`; `I0A_PERMIT=NOT_GRANTED`.

## 1. Dữ kiện xác định cho 10 vị trí

Các path: `D:\WORK`, `D:\WORK\RESEARCH`, `D:\WORK\RESEARCH\TokenToModel-Lab`, `worktrees`, `worktrees\p00-source-docs-diagrams-20261105`, `.git`, `.git\worktrees`, `tmp`, `evidence`, `cache` (các path tương đối đều bên dưới project root).

Mỗi thư mục có chung hai ACE `Allow` cho SID `S-1-5-11` (Authenticated Users), `IsInherited=True`, `ACL_PROTECTED=False`, `REPARSE=False`:

1. **ACE 1**: `FileSystemRights=Modify, Synchronize`, giá trị thập phân `1245631` (`0x1301BF`), `InheritanceFlags=None`, `PropagationFlags=None`. Đây là **ACE có hiệu lực trên thư mục hiện tại** và `Modify` cho phép đọc, ghi, tạo và xóa tệp/thư mục theo quyền Windows nếu SID thuộc token phù hợp. Không phải quyền thay đổi thuộc tính đơn thuần.
2. **ACE 2**: `FileSystemRights=-536805376`, biểu diễn bit 32-bit `0xE0010000` = `GENERIC_READ|GENERIC_WRITE|GENERIC_EXECUTE|DELETE`, `InheritanceFlags=ContainerInherit,ObjectInherit`, `PropagationFlags=InheritOnly`. ACE này **không có hiệu lực trực tiếp** lên thư mục hiện tại; nó cung cấp quyền để truyền xuống child/subfolder theo quy tắc ánh xạ generic rights của Windows.

`AUTHENTICATED_USERS_ACE_COUNT=2` cho từng mục (10/10). Không có reparse tại các vị trí script đã chọn; không bảo đảm toàn bộ cây con, tất cả junction khác hoặc sự thay đổi giữa kiểm tra và truy cập (TOCTOU).

**Nguồn chính thức**:
- https://learn.microsoft.com/en-us/dotnet/api/system.security.accesscontrol.filesystemrights
- https://learn.microsoft.com/en-us/windows/win32/secauthz/ace-inheritance-rules
- https://learn.microsoft.com/en-us/windows/win32/ad/access-control-inheritance
- https://learn.microsoft.com/en-us/windows/win32/secauthz/dacls-and-aces

## 2. Đánh giá an toàn đúng mức

- **PASS_SCOPED_RIGHTS_INTERPRETATION**: đã giải nghĩa số âm signed/int thành bitmask, phân biệt quyền áp dụng trên thư mục với quyền chỉ để kế thừa.
- **HOLD_P00_AND_GIT_WRITE_EXPOSURE**: P00 và `.git` có ACE `Modify` cho Authenticated Users ngay trên thư mục; một worker chạy bằng token Windows có quyền tương ứng có thể có quyền tạo, sửa hoặc xóa. **Đây là rủi ro bảo vệ bất biến P00 và Git thật**, không nên tiếp tục giả định chỉ cần đặt đường dẫn P01 bên trong root là đã an toàn.
- **HOLD_FUTURE_WORKER_EFFECTIVE_ACCESS**: chưa có token/identity sandbox P01 đã được cấp hoặc kiểm thử; chưa có effective-access/negative QA. Không kết luận một phiên bất kỳ đã truy cập trái phép hay worker đã vượt quyền.
- **HOLD_INHERITANCE_CONFINEMENT**: P01 chưa tồn tại, quyền có thể kế thừa; chỉ gán ACL mới vào P01 sau này **không tự chứng minh** tiến trình không thể ghi vào P00, `.git`, `tmp`, `evidence` hoặc cha của worktree.
- **NO_GLOBAL_ACL_MUTATION**: không thay quyền các thư mục cha hoặc P00 vì chúng đang dùng chung; không đề nghị `icacls /reset`, `Set-Acl`, `takeown` hay Deny ACE cho Authenticated Users trên ancestor.

## 3. Hướng cô lập bắt buộc trong thiết kế kế nhiệm

Mục tiêu: khi thực sự có worker QA0, worker phải **không có quyền ghi** vào P00, `.git`, ancestor, các research project khác hoặc bất cứ nơi nào ngoài allowlist. Các đường khả thi cần thẩm định **trên giấy trước**, không triển khai trong bước này:

- Tách **control-plane** (Git/worktree provisioning, source pinning, publish evidence) khỏi **worker sandbox**; worker không có quyền quản lý Git/.git, không kế thừa handles nhạy cảm.
- Xác định một *restricted token* / *AppContainer* hoặc cách cách ly hệ thống tệp tương đương, và một bộ *write broker* duy nhất có quyền ghi nơi được duyệt. Quyền kế thừa Authenticated Users phải được mô hình hóa trong phép đánh giá quyền hiệu lực; **không chỉ dựa vào việc tạo một thư mục P01 và thay ACL thư mục đó**.
- Mọi đường tệp, junction, file-id/handle và path canonicalization phải được kiểm trước khi mở handle và tại điểm ghi; chặn path traversal/UNC/symlink, child process bypass và race conditions theo các bài thử âm tính sau khi có permit QA0.
- Bất cứ đề xuất nào yêu cầu đổi ACL của `D:\WORK`, `D:\WORK\RESEARCH`, P00 hoặc các cây nguồn chung phải **dừng và xin duyệt phạm vi mới riêng**; tuyệt đối không là sửa hạ tầng tự động.
- Kiểm thử độc lập khi được cấp QA0: worker thử ghi P00, `.git`, sibling, ngoài root, dùng reparse/junction, tạo child/bypass broker; tất cả bị chặn, không tạo dữ liệu thật tại vùng bảo vệ. Cần test double/negative sandbox hợp lệ, không thực hiện thử ghi đối với P00 thật.

Đây **chỉ là lựa chọn kiến trúc cần làm rõ**, chưa xác lập restricted worker hay broker thực tế. Một quyết định I0A về **viết mã tĩnh** và quyết định QA0 về **chạy code/guard** vẫn phải tách biệt. Thẩm định này không tự động từ chối khả năng viết code trong tương lai, nhưng không được cấp I0A khi điều kiện chủ sở hữu và ranh giới scope còn HOLD.

## 4. Bảng phân xử

| Mục | Phán quyết | Bằng chứng |
|---|---|---|
| PA-03 Reparse trên các thư mục được quan sát | `PASS_SCOPED_OBSERVATION` | 10/10 False |
| PA-04 DACL đọc được | `PASS_SCOPED_OBSERVATION` | 10/10 ACE detail |
| PA-05 Nghĩa của 2 ACE S-1-5-11 | `PASS_RIGHTS_QUALIFIED` | Modify+Synchronize effective; generic inherit-only |
| PA-05 Đóng rủi ro quyền ghi rộng | **`HOLD_SECURITY_BOUNDARY`** | Có Allow Modify trên P00/.git/cha; chưa có cơ chế confinement |
| PA-06 Future worker effective access | **`HOLD_NOT_TESTED`** | Chưa có worker token/cách ly |
| PA-08 Permit I0A riêng | **`NOT_GRANTED`** | Chưa có quyết định cụ thể |

**Kết luận tổng**:
`I0A_ACE_RIGHTS=PASS_SCOPED_READONLY`  
`I0A_02_WORKTREE_PATH_ACL_ISOLATION=HOLD`  
`I0A_P00_GIT_WRITE_EXPOSURE=HOLD_RISK_NOT_PROVEN_EXPLOIT`  
`I0A_WORKER_EFFECTIVE_ACCESS=NOT_TESTED`  
`I0A_PREAUTH_ADMISSION=HOLD`  
`I0A_IMPLEMENTATION_PERMIT=NOT_GRANTED`  
`QA0_EXECUTION_PERMIT=NOT_GRANTED`  
`E0_SCIENTIFIC_PERMIT=NOT_GRANTED`  
`PR4_MERGE_AUTHORIZED=false`  
`P01_WORKTREE_CREATION_AUTHORIZED=false`  
`P01_DATA_DOWNLOAD_AUTHORIZED=false`  
`P01_TRAINING_AUTHORIZED=false`  
`P00_CLEANUP_AUTHORIZED=false`

## 5. Bước tiếp theo

`TTM_P01_D1_I0A_RESTRICTED_WORKER_FILESYSTEM_CONFINEMENT_DESIGN_REVIEW`: lựa chọn một mô hình cô lập filesystem/worker cụ thể và kiểm tra ở mức **tài liệu** rằng không có đường ghi sang P00, `.git`, ancestor hoặc ngoài workspace; xây oracle âm tính và định rõ tách I0A-static/QA0-runtime. Chỉ khi kiến trúc và quyền sở hữu được thẩm định mới trình **quyết định permit I0A riêng**, không cấp trong hồ sơ này.

Đây là đánh giá bảo mật hạ tầng; không bổ sung một kết quả khoa học vào `lineage.md`.
