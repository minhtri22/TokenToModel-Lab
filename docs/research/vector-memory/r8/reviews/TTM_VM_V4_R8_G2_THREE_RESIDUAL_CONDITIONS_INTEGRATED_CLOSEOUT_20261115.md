# TTM Vector Memory V4 R8 — Phân xử ba điều kiện G2 còn lại

- **Operation** `TTM_VM_V4_R8_G2_THREE_RESIDUAL_CONDITIONS_INTEGRATED_CLOSEOUT_SINGLE_GATE`
- **Ngày** 15/11/2026 (Asia/Saigon)
- **Phân xử** `G2_HOLD · HOLD_INTEGRATED`

## Phạm vi và pin

- Exact implementation `84d9d5c95e9962ccfe294852570e261b145fe403`; hợp đồng yêu cầu Python 3.12, NumPy 2.3.5, SciPy 1.17.0, scikit-learn 1.8.0 và `random_state=20261114`. [Runtime contract](https://github.com/minhtri22/TokenToModel-Lab/blob/84d9d5c95e9962ccfe294852570e261b145fe403/docs/research/vector-memory/r8/R8_V4_RESTRICTED_ORACLE_AND_RATER_CONTRACT_DESIGN_ONLY.json).
- Kế thừa từ `45dc302c67a96e7af2c1bfa6fb2b4944e6c81915` các kết quả custodian và NTFS ACL `PASS_SCOPED`, protected source `PASS_5_OF_5`, readback qua tiến trình Windows thứ hai, DPAPI CurrentUser cùng ổ, phân giải import tĩnh và commitment sentinel. Chỉ đọc lại byte cần thiết trong luồng import runtime mới. [Biên bản G2 gốc](https://github.com/minhtri22/TokenToModel-Lab/blob/45dc302c67a96e7af2c1bfa6fb2b4944e6c81915/docs/research/vector-memory/r8/reviews/TTM_VM_V4_R8_G2_MINIMAL_LOCAL_WINDOWS_CUSTODY_AND_SOURCE_LOCK_20261115.md).
- Kế thừa independent G0 tại `12d66bcff86a6cf435998a98a14afd254924fa5d`. [Independent adjudication](https://github.com/minhtri22/TokenToModel-Lab/blob/12d66bcff86a6cf435998a98a14afd254924fa5d/docs/research/vector-memory/r8/reviews/TTM_VM_V4_R8_GPRE_V2_FINAL_INDEPENDENT_G0_G2_ADJUDICATION.md).

## Recovery

`RECOVERY_HOLD_INDEPENDENT_BACKUP_OR_PROFILE_RECOVERY_NOT_VERIFIED`. Kiểm kê Windows chỉ thấy hai phân vùng cố định C: và D: trên cùng một ổ NVMe vật lý, không thấy ổ rời hay filesystem share được gắn, và không thấy cấu hình File History của profile hiện tại. Handoff và hồ sơ custody thiếu đích backup độc lập đã được duyệt. Do đó chưa có bản sao sentinel trên media độc lập để kiểm hash và giải mã.

Kết quả DPAPI CurrentUser từ bản sao trên cùng ổ chỉ áp dụng với máy và profile hiện có. Phục hồi byte sau mất ổ và phục hồi khả năng giải mã sau mất profile đều chưa được kiểm chứng. Chưa có quy trình được duyệt để phục hồi DPAPI master keys và recovery credentials dưới điều kiện mất profile hoặc máy. [Phạm vi DPAPI CurrentUser](https://learn.microsoft.com/en-us/windows/win32/api/dpapi/nf-dpapi-cryptprotectdata).

## Runtime thực thi

`RUNTIME_EXACT_PIN_ATTESTED` cho smoke test local. Môi trường cô lập dưới project chạy Python 3.12.10 và import thực tế NumPy 2.3.5, SciPy 1.17.0 và scikit-learn 1.8.0, kể cả ba extension native. Joblib 1.5.3 và threadpoolctl 3.6.0 được pin theo phiên bản đã quan sát ở lượt trước. Năm wheel được đối chiếu SHA-256 với metadata phát hành PyPI rồi cài offline bằng `--require-hashes`. `pip check` đạt. Kiểm tra 3.636 tệp có hash trong RECORD sau cài, đối chiếu các tệp dưới site-packages với RECORD của wheel và xác minh `__file__` tại import. [NumPy 2.3.5](https://pypi.org/project/numpy/2.3.5/), [SciPy 1.17.0](https://pypi.org/project/scipy/1.17.0/), [scikit-learn 1.8.0](https://pypi.org/project/scikit-learn/1.8.0/).

SHA-256 của executable môi trường cô lập là `0b471133e110cfb53a061cad528ce8e517d7b9ac41a0a396c39ad795a487fc14`. Executable base, DLL, wheel, RECORD, module import và đường dẫn runtime được ghi trong biên nhận local. Trình nạp xác minh SHA-256 trên chính byte dùng để import bốn module R8 từ custody, bao gồm dependency của production caller. Kiểm tra thấy `random_state=20261114`. Thử với đường dẫn nguồn thiếu module cho kết quả từ chối phân giải dù cwd là public checkout. Tệp test G0 thứ năm thuộc pin 5/5 kế thừa.

Tiến trình Python hạ xuống Low Integrity dưới SID custodian trước import package và source. Windows cho phép đọc trên thư mục source và năm tệp, đồng thời từ chối các yêu cầu mở handle để ghi, append, xóa, đổi DACL hoặc owner. Thư mục cũng từ chối quyền xóa mục con. Kết quả chỉ xác nhận quyền source của token chạy thử. Isolation quyền đọc vùng key/receipt và quyền thực thi production vẫn thuộc lần cấp phép riêng. Smoke test chỉ import và kiểm toàn vẹn; các entrypoint khoa học và test lịch sử không được gọi. [Windows Mandatory Integrity Control](https://learn.microsoft.com/en-us/windows/win32/secauthz/mandatory-integrity-control).

## Timestamp và retention của G_pre commitment

`COMMITMENT_TIMESTAMP_ANCHOR_PASS_SCOPED`. GitHub Repository Activity trả sự kiện push `50363903989` với thời điểm phía GitHub ghi nhận là **2026-11-15 05:52:00 UTC** và `after=45dc302c67a96e7af2c1bfa6fb2b4944e6c81915`. Đọc lại blob GitHub `6f379d75f0cd7c8eda55e58c22afdbe66ba4d63f` ở đúng commit cho SHA-256 `fcc32389e282604ca0ef98be10af1037c9b558b182950a3409ad7a23c92c9958` và đúng digest mẫu `d3c47f2b5c264e58fbda42dfb7b951ba5958179ca49349604e4f303b35a6ebb9`. Chuỗi activity → commit → blob → digest cho phép kiểm tra thời điểm GitHub ghi nhận mẫu mà không mở dữ liệu private. [GitHub Repository Activity API](https://docs.github.com/en/rest/repos/repos#list-repository-activities).

`IMMUTABLE_RETENTION_NOT_VERIFIED`. Nhánh evidence hiện không có branch protection hoặc rule hiệu lực. Reference có thể bị force-push hoặc xóa bởi principal có quyền tương ứng. Immutable releases đang tắt, chưa có release xác minh được và chưa có thời hạn giữ bất biến cho reference hay activity record. Tính định danh theo nội dung của blob và timestamp từ máy chủ xác nhận đường kiểm chứng hiện tại. Điều kiện retention pre-G3 vẫn thiếu. [GitHub release immutability](https://docs.github.com/en/code-security/how-tos/secure-your-supply-chain/establish-provenance-and-integrity/prevent-release-changes).

## Phán quyết và trạng thái nghiên cứu

`G2_HOLD · HOLD_INTEGRATED`. Runtime đạt phạm vi yêu cầu kiểm tra. Hai điều kiện còn thiếu là recovery ngoài ổ/profile và thời hạn retention bất biến cho commitment pre-G3 có thể kiểm chứng.

`G0=PASS_SCOPED_INDEPENDENT_SOURCE_REVIEW` · `G1=OWNER_STANDING_RESEARCH_DIRECTION_RECORDED` · `R7=FROZEN_FAIL` · `R8=NOT_GENERATED` · `G3/G4=NOT_EXECUTED` · `G5/G6=SEALED` · `READER=0` · `GPU=NO` · `PROBE256=SEALED` · `ACTUAL_HMAC_KEY_GENERATED=FALSE` · `ACTUAL_G_PRE_COMMITMENT_CREATED=FALSE` · `GO_R8_D_CANDIDATE_AUTHORING_ONLY=NOT_AUTHORIZED`.
