# TTM Vector Memory V4 R8 — G2 custody và source-lock trên Windows

- **Operation** `TTM_VM_V4_R8_G2_MINIMAL_LOCAL_WINDOWS_CUSTODY_AND_SOURCE_LOCK_SINGLE_GATE`
- **Thời điểm readback** 15/11/2026, 05:48–05:50 UTC
- **Phân xử** `G2_HOLD`; quyết định tích hợp `HOLD_INTEGRATED`

## Phạm vi custody và quyền truy cập

Chỉ thị owner giao thực hiện handoff cho phép thiết lập vùng custody trên máy và project đã chỉ định khi bằng chứng local khớp. Token Windows ở mức Medium, không nâng quyền, có cùng SID với tài khoản desktop đang đăng nhập và chủ sở hữu thư mục project. Profile của tài khoản đã được nạp. Codex ghi phạm vi ủy quyền của operation và căn cứ đối chiếu trong biên nhận local, theo hình thức ghi nhận chỉ thị qua chat.

Vùng custody được tạo trên NTFS cố định với DACL áp dụng từ lúc tạo. Các thư mục custody chặn kế thừa ACL của repo. Tệp con kế thừa duy nhất quyền FullControl của custodian. Owner và DACL được kiểm tra lại qua tiến trình mới. Bằng Windows handle, token custodian mở thành công các quyền đọc, ghi, thêm, xóa, đọc DACL, sửa DACL và ghi owner trên các thư mục custody chính và năm tệp nguồn. Các phép mở này kiểm tra quyền mà không sửa owner hay DACL. Kiểm tra dành cho principal khác dựa trên DACL, chưa chạy với token riêng.

Chuỗi đường dẫn được kiểm tra reparse point và đích mở handle khớp đường dẫn dự kiến. Các thư mục tổ tiên bên ngoài vùng custody vẫn thừa kế quyền Modify có DELETE cho nhóm người dùng được xác thực, vì vậy việc đổi tên hoặc thay đổi namespace bên ngoài vùng custody có thể ảnh hưởng tính sẵn sàng. Kiểm tra quyền áp dụng cho tài khoản thông thường. Quyền quản trị Windows có thể vượt các ràng buộc này. Git local exclude được xác minh riêng và ngăn staging thông thường của vùng custody.

## Exact source readback

Năm blob được lấy bằng Git object tại commit `84d9d5c95e9962ccfe294852570e261b145fe403`, ghi nguyên byte và mở lại từ vùng đã áp ACL. Kết quả **5/5** khớp ở lần đọc sau khi ghi và ở tiến trình PowerShell thứ hai. Biên nhận và manifest chỉ lưu local. [Exact implementation](https://github.com/minhtri22/TokenToModel-Lab/commit/84d9d5c95e9962ccfe294852570e261b145fe403).

| File | SHA-256 đọc từ vùng custody |
| --- | --- |
| `folds_raters.py` | `02626f9f0def5af90b57c2930898e96dbc8f6206c441bb4aaa4c4278ce0dddae` |
| `r8_production_caller.py` | `3a9b249bced1b4ceaa5746d63367c017410ef82ded21ef386c3be2b1ee76b206` |
| `test_g0_algorithm_version_binding.py` | `2ce86fe549e1625790fcab72c076df2f12d648b048a350570d5c97a026431ae2` |
| `gold_contract.py` | `8e8b81ce2d0bc47cc60c29abc7156fe9d97613e67983e43b7f587615d68015a5` |
| `restricted_oracles.py` | `34ab74d36b822703e4d8cbdf281e142273d55d181243d904b55fd31a0e6382a1` |

## Persistence, HMAC và pre-G3

| Kiểm tra | Kết quả quan sát |
| --- | --- |
| Persistence | Ghi có flush xuống storage cố định. Tiến trình mới trong cùng phiên đăng nhập đọc lại sentinel và SHA-256 khớp. Chưa đo qua reboot hoặc phiên đăng nhập khác. |
| Recovery | Mở bản sao ciphertext DPAPI từ cùng ổ và khôi phục sentinel, đối chiếu được SHA-256. `RECOVERY_NOT_VERIFIED` khi mất ổ hoặc profile. Retention local thuộc custodian. |
| Runtime/import | Python 3.12.10 ở chế độ `-I -S -B` xác nhận đích phân giải của 5/5 module bằng allowlist theo thư mục, đối chiếu hash và từ chối phân giải ở root thiếu module dù cwd là public checkout. Kiểm tra static, không execute module R8. Hash SHA-256 của literal token regex UTF-8 là `ffdfc06eb76bebd35e1f6185fafd4525d244149d7f64838bbe1f688ddf406d2e`. |
| Runtime thực thi | `APPROVED_RUNTIME_NOT_ATTESTED`. Metadata local cho scikit-learn 1.8.0, NumPy 2.4.4, SciPy 1.17.1. Hợp đồng runtime và QA gốc dùng NumPy 2.3.5 và SciPy 1.17.0. Identity/quyền đọc nguồn dành cho runtime thực thi chưa cấp. [Runtime contract](https://github.com/minhtri22/TokenToModel-Lab/blob/84d9d5c95e9962ccfe294852570e261b145fe403/docs/research/vector-memory/r8/R8_V4_RESTRICTED_ORACLE_AND_RATER_CONTRACT_DESIGN_ONLY.json). |
| HMAC custody | `HMAC_CUSTODY_POLICY_READY_SCOPED`. Kế hoạch tạo 32 byte bằng Windows CSPRNG trong bộ nhớ, bọc bằng DPAPI CurrentUser của custodian, lưu ciphertext dưới ACL vùng key và kiểm chứng recovery. Mẫu thử DPAPI đã khớp; `ACTUAL_HMAC_KEY_GENERATED=FALSE`. [Microsoft CryptProtectData](https://learn.microsoft.com/en-us/windows/win32/api/dpapi/nf-dpapi-cryptprotectdata). |
| Commitment pre-G3 | Mẫu vô hại dùng `TTM_VM_R8_GPRE_HMAC_V2`, `R8_GPRE_CANONICAL_JSON_COMPONENT_RANKING_V2`, digest các manifest source/runtime, digest mẫu và UTC. Tệp mẫu đã được flush rồi mở lại và SHA-256 khớp. Định dạng dự kiến ràng buộc exact byte UTF-8 của receipt; receipt thật sẽ cần nonce private và digest preassignment. Chỉ digest được công bố. |

SHA-256 của **commitment sentinel** là `d3c47f2b5c264e58fbda42dfb7b951ba5958179ca49349604e4f303b35a6ebb9`. Đây là mẫu cho đường ghi, đọc lại và công bố digest. GitHub branch rules API trả danh sách trống cho nhánh evidence được kiểm tra. Chưa có bảo đảm retained timestamp bất biến từ nơi lưu được chấp nhận theo điều kiện G2 độc lập. [Yêu cầu custody và commitment trong adjudication](https://github.com/minhtri22/TokenToModel-Lab/blob/12d66bcff86a6cf435998a98a14afd254924fa5d/docs/research/vector-memory/r8/reviews/TTM_VM_V4_R8_GPRE_V2_FINAL_INDEPENDENT_G0_G2_ADJUDICATION.md#5-g2-protected-runtime-source-lock).

## Phân xử

`G2_HOLD` do chưa xác minh phục hồi khi mất ổ hoặc profile, chưa attest runtime thực thi theo pin, và chưa xác minh cơ chế lưu pre-G3 commitment với timestamp và retention bất biến. Source readback 5/5 và ACL đã được kiểm chứng trong phạm vi nêu trên. G3 chỉ được thực hiện sau khi commitment được chấp nhận theo gate.

`G0=PASS_SCOPED_INDEPENDENT_SOURCE_REVIEW` · `G1=OWNER_STANDING_RESEARCH_DIRECTION_RECORDED` · `R7=FROZEN_FAIL` · `R8=NOT_GENERATED` · `G3/G4=NOT_EXECUTED` · `G5/G6=SEALED` · `READER=0` · `GPU=NO` · `PROBE256=SEALED`. Lượt này chỉ thực hiện custody và các phép kiểm tra hạ tầng bằng mẫu vô hại. `ACTUAL_G_PRE_COMMITMENT_CREATED=FALSE`.
