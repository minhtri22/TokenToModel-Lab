# TTM Vector Memory V4 R8 — G2 protected custody và exact source-lock

- **Ngày kiểm tra** 15/11/2026 (Asia/Saigon), khoảng 05:23 UTC.
- **Operation** `TTM_VM_V4_R8_G2_PROTECTED_CUSTODY_ESTABLISHMENT_AND_EXACT_SOURCE_LOCK_SINGLE_GATE`.
- **Phân xử G2** `G2_HOLD` (`HOLD_INFRASTRUCTURE_AUTHORIZATION_REQUIRED`).
- **Quyết định tích hợp** `HOLD_INTEGRATED`.

## 1. Các mốc đã khóa

| Hồ sơ | Repository `minhtri22/TokenToModel-Lab` |
| --- | --- |
| Exact implementation | [`84d9d5c95e9962ccfe294852570e261b145fe403`](https://github.com/minhtri22/TokenToModel-Lab/commit/84d9d5c95e9962ccfe294852570e261b145fe403) |
| Frozen V4 contract | [`b8410d9c1f77a733036e980b567de73c316f8725`](https://github.com/minhtri22/TokenToModel-Lab/blob/b8410d9c1f77a733036e980b567de73c316f8725/docs/research/vector-memory/r8/TTM_VM_V4_R8_V4_GOLD_FOLD_ORACLE_RATER_OWNER_SCOPE_SINGLE_PACKET_DESIGN_ONLY_20261114.md) |
| Independent G0/G2 adjudication | [`12d66bcff86a6cf435998a98a14afd254924fa5d`](https://github.com/minhtri22/TokenToModel-Lab/blob/12d66bcff86a6cf435998a98a14afd254924fa5d/docs/research/vector-memory/r8/reviews/TTM_VM_V4_R8_GPRE_V2_FINAL_INDEPENDENT_G0_G2_ADJUDICATION.md) |
| Owner standing research direction | [`097e046bb0f6525665dde03ec5fcdf8134a8e762`](https://github.com/minhtri22/TokenToModel-Lab/blob/097e046bb0f6525665dde03ec5fcdf8134a8e762/docs/research/vector-memory/r8/decisions/TTM_VM_V4_R8_OWNER_STANDING_RESEARCH_DIRECTION_20261114.md) |
| G2 readback gần nhất và head của evidence branch lúc bắt đầu | [`5aded769c29e5cbc079226e53e696f5137837422`](https://github.com/minhtri22/TokenToModel-Lab/blob/5aded769c29e5cbc079226e53e696f5137837422/docs/research/vector-memory/r8/reviews/TTM_VM_V4_R8_G2_AUTHORIZED_PROTECTED_SOURCE_LOCK_READBACK_20261115.md) |

Đã đọc các hồ sơ theo Git object khóa. Exact implementation là tổ tiên của head evidence lúc bắt đầu. Worktree của nhánh `evidence/ttm-vm-v4-r8-g0-f01-f03-single-closure-20261114` sạch và trùng head trên GitHub. Checkout chính có các mục untracked từ trước. Hoạt động đọc và xuất báo cáo dùng worktree evidence hiện hữu.

## 2. Windows token và bốn lớp quyền

| Lớp | Quan sát và phạm vi |
| --- | --- |
| Codex filesystem sandbox | Phiên hiện tại có quyền filesystem không giới hạn bởi sandbox. Đọc research root, repo và Git objects thành công trên `DESKTOP-4PSD0G2`. |
| Codex approval policy | `never` — phiên không có luồng escalation. Đọc local và GitHub thành công. Quyền ghi Markdown public-safe lên evidence branch đến từ chính yêu cầu này. GitHub trả `viewerPermission=ADMIN` cho phiên đã xác thực tại thời điểm kiểm tra. |
| Windows security token | `DESKTOP-4PSD0G2`, PowerShell 7.6.9, token người dùng độ toàn vẹn Medium, vai trò Administrator không được bật. Đã quan sát account của tiến trình tại local. Effective access tại protected root chưa đánh giá vì chưa có locator được phê duyệt. |
| R8 custody governance | Chưa xác lập thẩm quyền G2 cho Windows identity đang chạy. G1 ghi nhận hướng nghiên cứu và giao việc kiểm chứng cho custodian được ủy quyền. Hồ sơ này thiếu chỉ định Windows principal, storage và quyền triển khai/quản trị ACL. |

Rào cản của lượt này là **thiếu quyết định ủy quyền hạ tầng**. Kiểm tra được phép đã thực hiện mà không gặp Codex policy denial hay Windows access denial. Quyền đọc/ghi protected storage chưa được thử.

## 3. Kiểm tra hồ sơ bổ sung kể từ baseline

- Head GitHub của nhánh evidence tại thời điểm kiểm tra vẫn là `5aded769c29e5cbc079226e53e696f5137837422`. Đối chiếu history giới hạn vào `docs/research/vector-memory/r8/` trên ba nhánh liên quan. Không có commit theo đường dẫn này sau merge base tương ứng trên `main` (`d8974676b8a67b038a1e3b042bd6299cfa8fad0a`), nhánh `evidence/ttm-vm-v4-r8-v4-integrated-closure-20261114` (`53c987be529fc6342006d678116180fc6be72a62`) và nhánh `research/ttm-vector-memory-architecture-20261111` (`b7788337bd98eaf8797913ae4d8a8e62ee1cbf09`). Truy vấn bổ sung tiêu đề issue và PR có `R8` trong repo trả mảng rỗng.
- Custody record ở exact implementation vẫn ghi `status=NOT_VERIFIED`, `private_storage_uri=REDACTED_NOT_SUPPLIED`, `private_material_read=NOT_EXECUTED`. Lượt này kiểm tra thay đổi hồ sơ và nhánh đích. Không quét lại các thư mục Windows vốn đã được rà soát ở lượt trước. [Custody record tại exact source](https://github.com/minhtri22/TokenToModel-Lab/blob/84d9d5c95e9962ccfe294852570e261b145fe403/docs/research/vector-memory/r8/integrated_closure/OWNER_RIGHTS_CUSTODY_DECISION_PACKET_PENDING.json).
- Trong hồ sơ và đầu vào hiện có, chưa xác định được quyết định với canonical private source root, custodian được chỉ định, ma trận quyền, retention/recovery, ràng buộc runtime, vị trí private receipt, hoặc cơ chế HMAC và immutable G_pre commitment đã được duyệt. Kết quả chỉ áp dụng cho phạm vi hồ sơ đã nêu. Discovery là `G2_PROTECTED_CUSTODY_ESTABLISHMENT_REQUIRED`, với hai blocker `HOLD_PROTECTED_STORE_NOT_IDENTIFIED` và `HOLD_CUSTODIAN_AUTHORIZATION_REQUIRED`.

## 4. Source-lock và custody readiness

Các pin thuộc `docs/research/vector-memory/r8/integrated_closure/`. Public Git blobs và public Windows checkout đã khớp 5/5 theo báo cáo baseline. Lượt này dùng lại kết quả `G2_PUBLIC_SOURCE_SHA_MATCH_ONLY`.

| File | Expected SHA-256 | Protected runtime |
| --- | --- | --- |
| `folds_raters.py` | `02626f9f0def5af90b57c2930898e96dbc8f6206c441bb4aaa4c4278ce0dddae` | `NOT_EXECUTED` |
| `r8_production_caller.py` | `3a9b249bced1b4ceaa5746d63367c017410ef82ded21ef386c3be2b1ee76b206` | `NOT_EXECUTED` |
| `test_g0_algorithm_version_binding.py` | `2ce86fe549e1625790fcab72c076df2f12d648b048a350570d5c97a026431ae2` | `NOT_EXECUTED` |
| `gold_contract.py` | `8e8b81ce2d0bc47cc60c29abc7156fe9d97613e67983e43b7f587615d68015a5` | `NOT_EXECUTED` |
| `restricted_oracles.py` | `34ab74d36b822703e4d8cbdf281e142273d55d181243d904b55fd31a0e6382a1` | `NOT_EXECUTED` |

| Yêu cầu | Kết quả lượt này |
| --- | --- |
| Protected source provenance, runtime identity, path containment | `NOT_VERIFIED` — có pin Git và local Windows executor. Binding từ protected source tới runtime chưa có. |
| Protected source SHA-256 | `NOT_EXECUTED` — 5/5 file chưa được đọc trên protected runtime. |
| Protected ACL/DACL, effective permissions | `NOT_EXECUTED` — thiếu approved root và phạm vi quyền đã xác lập. |
| Persistence, recovery và vị trí private receipt | `NOT_VERIFIED` — báo cáo trước xác nhận sandbox non-R8 sentinel lịch sử đã dọn. |
| HMAC key custody policy | `NOT_VERIFIED` — thiết kế CSPRNG và DPAPI CurrentUser đã được ghi nhận ở mức dự kiến. |
| Immutable pre-G3 commitment mechanism | `NOT_VERIFIED` — chưa có đích lưu, retention lock hoặc receipt được xác thực. |
| HMAC key và G_pre commitment thật | `NOT_CREATED`. |

## 5. Một quyết định hạ tầng tích hợp cho G2

Đề xuất dưới đây chờ người có thẩm quyền quản trị storage và Windows access duyệt trong **một hồ sơ xác thực, lưu riêng tư**. Hồ sơ xác định người phê duyệt, hiệu lực và phạm vi công việc, rồi điền các thông số thực tế dưới đây. Lượt này chưa triển khai đề xuất.

| Mục quyết định | Thiết kế đề xuất và dữ liệu cần điền |
| --- | --- |
| Storage và retention | Chọn canonical root trên volume Windows bền vững, hỗ trợ ACL, nằm trong project root đã phê duyệt. Ghi locator, storage/volume identity, controller, chính sách mã hóa/backup và lịch giữ/xóa đã duyệt cho source, private receipt và encrypted key. Tách vùng source chỉ đọc sau triển khai, vùng private receipt và vùng key. Ghi đích và người được quyền phục hồi. |
| Custodian và ACL | Chỉ định custodian Windows principal, account/profile của runtime và actor được quyền tạo hoặc sửa ACL. Chốt ma trận quyền trên root, thư mục cha và từng vùng. Runtime chỉ đọc source sau triển khai. Custodian lưu receipt và quản lý key theo đúng scope. Reviewer được đọc phần receipt phục vụ kiểm chứng. Nêu rõ phạm vi quản trị OS/backup và loại bỏ quyền truy cập hoặc thay thế file ngoài scope. Kiểm effective access theo token và descriptor thực tế, bao gồm owner, inheritance, ACE và quyền ghi, xóa, đổi ACL/owner liên quan. [Windows AccessCheck](https://learn.microsoft.com/en-us/windows/win32/api/securitybaseapi/nf-securitybaseapi-accesscheck). |
| Triển khai và ràng buộc source với runtime | Chỉ đưa byte của source và các thành phần runtime thuộc danh mục đã duyệt vào store. Triển khai từ object Git đúng commit bằng đường ghi byte nguyên trạng, tránh chuyển đổi line endings, filters hoặc encoding. Khóa manifest gồm relative paths, năm SHA-256, cùng pin interpreter Python 3.12, versions gói phụ thuộc, validator và regex assets theo hợp đồng. Ghi nhận executable, import roots và execution identity thực tế. Chặn fallback sang public checkout hoặc import path ngoài scope. |
| HMAC key | Giữ thiết kế dự kiến 32 byte từ Windows CSPRNG và DPAPI CurrentUser cho identity/profile được chỉ định, dưới ACL vùng key. Cho lần sử dụng được phép sau này, chốt quyền tạo, dùng HMAC và giải bọc, cùng thủ tục xử lý đổi account/profile hoặc mất máy, backup và xóa theo retention. Xác minh thủ tục recovery bằng dữ liệu thử không phải secret R8 nếu được phép. DPAPI CurrentUser thường phụ thuộc logon credentials và máy. [Windows CryptProtectData](https://learn.microsoft.com/en-us/windows/win32/api/dpapi/nf-dpapi-cryptprotectdata). |
| Private receipt và G_pre commitment | Chọn kho WORM hoặc cơ chế immutable tương đương với retention đã khóa. Chỉ định writer, reader, nguồn UTC và cơ chế xác thực receipt. Khi G_pre thực sự được lập ở giai đoạn được phép, lưu bản canonical có phiên bản thuật toán/schema, source/runtime manifest và commitment của blueprint/fold lock. Ghi trước G3, nhận object/version và timestamp xác thực, rồi đọc lại để kiểm digest và tình trạng retention lock. Lưu riêng tư cả chi tiết attestation. Public evidence chỉ dùng các trạng thái, pin và digest được phép công bố. [Cơ chế WORM và retention lock](https://learn.microsoft.com/en-us/azure/storage/blobs/immutable-storage-overview). |

### Nghiệm thu một lượt sau khi có quyết định

1. Custodian xác minh decision record, storage identity, account/profile/token và quyền trên đúng phạm vi trước khi triển khai hoặc đọc. Đối chiếu ACL/DACL và effective access cả trên đường dẫn đến store và trên từng vùng. Dừng với `HOLD_ACCESS_DENIED` nếu Windows từ chối. Nếu Codex chặn thao tác, ghi nhận thao tác, chính sách và lỗi public-safe theo `CODEX_POLICY_BLOCKED`.
2. Tính SHA-256 cho đúng năm file dưới runtime đã ràng buộc, với đường dẫn relative từ manifest. Xác minh thư mục cha và file không đi qua reparse point, symlink/junction hoặc thoát root. Đối chiếu volume/file identity từ handle đã mở và kiểm soát khả năng thay thế file trong lúc đọc. Mọi hash phải khớp pin. Hash sai dẫn đến `FAIL_EXACT_SOURCE_MISMATCH`. Không chạy file kiểm thử hay chạy khoa học chỉ để kiểm source-lock.
3. Kiểm persistence và khả năng phục hồi bằng receipt đã được duyệt hoặc mẫu non-R8 được phép trên **chính storage đã chọn**. Ghi digest và kiểm readback qua phiên độc lập, đối chiếu identity, ACL và đường phục hồi theo retention. Kiểm riêng chính sách HMAC và khả năng đọc lại receipt có retention lock bằng dữ liệu vô hại trong scope. Ghi readiness riêng với việc tạo key/commitment thật.
4. Custodian lưu một receipt xác thực chứa decision ID, UTC, storage và runtime identity, kết quả effective access, persistence/recovery, source provenance, năm byte hash và readiness của hai cơ chế bảo vệ. Báo cáo public chỉ trích xuất thông tin đã được duyệt. `G2_PROTECTED_SOURCE_LOCK_PASS_SCOPED` cần chứng cứ đạt cho tất cả các mục này trong cùng phạm vi custody.

## 6. Trạng thái nghiên cứu

`G0=PASS_SCOPED_INDEPENDENT_SOURCE_REVIEW` với disposition `G0_VERSION_BINDING_PASS_SCOPED_INDEPENDENT_SOURCE_REVIEW` ở pin đã nêu. `G1=OWNER_STANDING_RESEARCH_DIRECTION_RECORDED`. `GO_R8_D_CANDIDATE_AUTHORING_ONLY=NOT_AUTHORIZED`.

`R7=FROZEN_FAIL` · `R8=NOT_GENERATED` · `G3/G4=NOT_EXECUTED` · `G5/G6=SEALED` · `READER=0` · `GPU=NO` · `PROBE256=SEALED`. Lượt này chỉ kiểm chứng hồ sơ và ghi báo cáo evidence. Protected store, ACL, protected-runtime hashes, key, gold và fold allocation đều chưa được tạo hay thay đổi trong lượt này. G0, QA lịch sử và V5/V6 nằm ngoài phạm vi.
