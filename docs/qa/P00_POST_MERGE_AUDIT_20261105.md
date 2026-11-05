# TTM P00 — Biên bản kiểm toán sau hợp nhất và rà soát tài liệu

**Mã công việc:** `TTM_P00_POST_MERGE_BASELINE_AUDIT_AND_DOCUMENTATION_REVIEW`  
**Ngày kiểm tra:** 05/11/2026  
**Phạm vi:** chỉ đọc GitHub và máy Windows qua RemoteMCP; chỉnh sửa tài liệu trên nhánh GitHub riêng, không chạy lại khoa học, không tạo/xóa worktree.

## 1. Xác minh danh tính

| Hạng mục | Quan sát | Đánh giá |
|---|---|---|
| Kho GitHub | `minhtri22/TokenToModel-Lab` | Đúng |
| Thư mục được duyệt | `D:\WORK\RESEARCH\TokenToModel-Lab` | Đúng |
| Máy đích | `DESKTOP-4PSD0G2`, RemoteMCP `machine-1` trực tuyến | Đúng thiết bị |
| Yêu cầu hợp nhất (Pull Request) #1 | Đã hợp nhất 05:21:08 UTC ngày 05/11/2026 | Đạt ở GitHub |
| Commit `main` GitHub lúc kiểm tra | `8df22f5f29e645b2becff936daccbd32ac780661` | Mốc Git kỹ thuật P00 |
| Commit `main` local | `f2ed098b033431924a3cbabdc9af89d7bbd7b378` | **Chưa đồng bộ** |
| Commit local `origin/main` | `f2ed098b033431924a3cbabdc9af89d7bbd7b378` | **Chưa đồng bộ** |
| Commit nguồn worktree P00 | `382da2c52d0fb4efe1cd9de5c92e68de79a52a20` | Đúng nguồn QA |
| Nguồn Git local | `https://github.com/minhtri22/TokenToModel-Lab.git` | Đúng nguồn |
| Trạng thái làm sạch cây Git (Git Status) | Chưa có phép đọc qua Git CLI trên máy | **Chưa xác minh** |

Phương pháp local: đọc `.git/HEAD`, `.git/refs/heads/main`, `.git/refs/remotes/origin/main`, `.git/config`, `.git/worktrees/.../HEAD` và `refs/heads/feature/...` bằng RemoteMCP chế độ chỉ đọc. Các đường dẫn Git được đối chiếu vẫn ở trong thư mục dự án. **Không** đồng nhất phép đọc metadata với `git status`; không kết luận cây sạch.

Lưu ý: Project RemoteMCP cũ `prj_7ff9a13a92022806cecf44b7` vẫn được nhận dạng `NON_GIT`, task `tsk_fcaae8452d82e4872bc1748e` ở trạng thái `RECOVERABLE`. Không thay task, tạo pairing, nới root hoặc dùng công cụ nghiên cứu để vượt cổng thực thi. Research Adapter vẫn tắt.

## 2. Bảo toàn mã nguồn và bằng chứng

Năm tệp `reference/phase0/model.py`, `reference/phase0/paged_kv.py`, `reference/phase0/test_reference.py`, `configs/phase0_reference.json` và `scripts/TTM_P00_WINDOWS_QA.ps1` có nội dung GitHub `main` **trùng** commit nguồn kiểm định `382da2c52d0fb4efe1cd9de5c92e68de79a52a20`.

- Model SHA-256: `821e60a6c97536bf3a251602b31dcc6b55f1c81836cffa5223ec2f063ae578ea`.
- Config SHA-256: `ffcd83863fb9c2a8959fbaaa52ccdb7bf2977d68ea6aa869880015dc0daebcbd`.
- Biên bản QA Windows 13/13: `artifacts/qa/p00/TTM_P00_WINDOWS_LOCAL_QA_20261105T043050Z.json`, SHA-256 `6f30d4450199d471acd5e5a9c7b8264bc8fdc653bdc3b76ba5bfa8afa47034ee`.
- Biên bản QA độc lập 6/6: `artifacts/qa/p00/TTM_P00_INDEPENDENT_QA_20261105T051340397776Z.json`, SHA-256 `b657b40e3da40060ef6c2e2b81239c64539f93100e169dae4920135ad6f16c38`.
- `experiments/registry.jsonl` chứa ba lần chạy được đăng ký: tham chiếu Linux, QA Windows và QA Windows độc lập.
- `lineage.md` có thứ tự `L0000` tới `L0005` tại commit sau hợp nhất; ghi cả lỗi PowerShell và QA PASS.

**Giới hạn:** chưa tái chạy mô hình trên local `main` vì local `main` chưa đồng bộ. Không thay thế các phép thử đã hoàn tất bằng chạy lại ngẫu nhiên.

## 3. Ý nghĩa của các phép đo P00

| Phép đo | Giá trị | Điều kiện đạt trong mã QA | Ý nghĩa và giới hạn |
|---|---:|---:|---|
| Sai lệch logits lớn nhất (Maximum Absolute Logit Difference) | `2.384185791015625e-07` | `<= 2e-5` | Hai đường tính gần tương đương trên fixture; không phải phép đo tốc độ |
| Sai lệch nhân quả tiền tố (Causal Prefix Difference) | `0.0` | `<= 1e-6` | Không phát hiện nhìn trước token trong trường hợp thử |
| Mất mát thử gradient (Gradient Smoke Loss) | `5.489449977874756` | Hữu hạn; gradient tồn tại, hữu hạn, khác 0 | Chỉ xác nhận đường gradient; không chứng minh mô hình học được ngôn ngữ |
| QA cục bộ trên Windows | 13/13 PASS | Mọi kiểm thử trả 0 và log xác minh | 5 chức năng mô hình, 8 quản trị/harness |
| QA bổ sung độc lập | 6/6 PASS | Mọi fixture riêng đạt | Không phải đánh giá bên thứ ba hay huấn luyện khoa học |
| Thông lượng / độ trễ / GPU | Chưa đo | Chưa định | Không được ghi `PASS` hoặc tuyên bố cải thiện |

Cấu hình hiện có trạng thái `PROPOSED_NOT_FROZEN`: chấp nhận **mốc tham chiếu kỹ thuật (Engineering Baseline)** bằng hash mà **không** tuyên bố khóa thiết kế khoa học hay huấn luyện.

## 4. Rà soát tài liệu

Trước rà soát có tài liệu hướng dẫn bằng tiếng Anh, tiêu đề tiếng Anh không kèm giải thích, văn bản còn mô tả P00 trước merge và chưa có quy chuẩn thuật ngữ.

Khắc phục trên nhánh `docs/p00-post-merge-audit-vietnamese-20261105`:
- Việt hóa các tài liệu hướng dẫn hoạt động, kiến trúc, sơ đồ, giai đoạn, huấn luyện, so sánh, điều lệ, quản trị, nguồn gốc, sách và biểu mẫu.
- Bổ sung `docs/TERMINOLOGY_VI.md` về cách trình bày tiếng Việt và thuật ngữ chuyên ngành trong ngoặc.
- **Không** sửa mã mô hình/thuật toán, tệp cấu hình, biên bản QA nguyên gốc, `experiments/registry.jsonl` hoặc nội dung các entry `lineage.md` cũ.
- Biên bản QA lịch sử viết tiếng Anh hoặc trộn ngôn ngữ được bảo lưu, có hướng dẫn giải thích mới `docs/qa/P00_HISTORICAL_RECORDS_VI.md`. Nội dung nhãn trong SVG/PNG chưa được vẽ lại nên là ngoại lệ cần phê duyệt và kiểm tra hình riêng.
- Việc có tài liệu Việt ngữ không tự làm kết quả khoa học thay đổi.

## 5. Phân loại cổng và kết luận

| Cổng | Trạng thái |
|---|---|
| GitHub PR #1 và mốc `main` | PASS |
| Bảo toàn mã nguồn đã kiểm định | PASS |
| Truy xuất SHA-256 và nhật ký QA | PASS |
| Cấu hình P00 là baseline kỹ thuật | PASS, giới hạn CPU correctness |
| Kiểm tra local `main` đã đồng bộ | FAIL: tham chiếu còn cũ |
| Kiểm tra cây Git local sạch và quyền sở hữu worktree bằng Git CLI | NOT_VERIFIED |
| Việt hóa tài liệu hướng dẫn | Đã chuẩn bị trên nhánh tài liệu; cần QA riêng trước merge |
| Kiểm tra sơ đồ có hoàn toàn Việt ngữ | Chưa hoàn tất |
| Huấn luyện mô hình khoa học, hiệu năng GPU | NOT_PERFORMED / NOT_ESTABLISHED |

**Quyết định kiểm toán:** `P00_POST_MERGE_GITHUB_BASELINE=PASS`, `P00_LOCAL_BASELINE_SYNC=HOLD`, `P00_DOCUMENTATION_QA=PENDING`, `P01_ADMISSION=NOT_AUTHORIZED`.

Không dọn worktree, không tự sửa lịch sử, không tạo task RemoteMCP mới. Sau khi nhánh tài liệu được kiểm thử và hợp nhất có kiểm soát, cần đồng bộ local `main` đúng commit mới nhất, kiểm tra sạch và xác lập mốc trước khi mở P01.

## 6. Bước thực hiện tiếp theo

`TTM_P00_LOCAL_MAIN_FAST_FORWARD_SAFETY_PREFLIGHT_AND_DOCUMENTATION_INDEPENDENT_QA`:

- Đọc trạng thái Git thật tại local `main`, kiểm tra `origin`, HEAD, danh sách worktree và không có thay đổi chưa lưu.
- Chỉ xem xét đồng bộ tiến nhanh (Fast-forward) sau khi điều kiện an toàn đạt; không dùng reset/force/clean.
- Kiểm tra nhánh tài liệu chỉ đổi tài liệu và bổ sung entry lineage mới; QA văn bản tiếng Việt.
- Không mở P01 cho đến khi đóng các cổng còn treo.
