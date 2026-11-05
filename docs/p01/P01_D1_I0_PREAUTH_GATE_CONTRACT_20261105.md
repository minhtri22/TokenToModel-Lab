# P01 D1 — Hợp đồng tiền cấp quyền I0 (Preauthorization Gate), chỉ thiết kế

**Mã:** `TTM_P01_D1_I0_PREAUTH_GATE_DECISION_DESIGN_ONLY`  
**Ngày:** 05/11/2026  
**Repository:** `minhtri22/TokenToModel-Lab`  
**Nhánh hồ sơ:** `design/p01-tokenizer-data-prereg-20261105` / PR #4 (Draft, chưa hợp nhất).  
**Mốc đối chứng GitHub main:** `92facee15d7c0d46b0e84ddf5b6d8b2073e078f7`.  
**Quyết định hiện tại:** `I0_PREAUTH_CONTRACT_DEFINED`, **`I0_PERMIT_NOT_GRANTED`**.

## 1. Phân tầng quyết định để tránh cổng vòng tròn

Không yêu cầu một bộ checker/guard **đã chạy** trước khi được cấp quyền **viết mã** của chính bộ đó. Phân biệt ba cổng và giới hạn từng cổng:

| Cổng | Chỉ cho phép làm gì nếu có quyết định riêng? | Tiền đề | Bị cấm |
|---|---|---|---|
| **D1 — Thẩm định/khóa tài liệu** | Đọc, phản biện, pin thiết kế, quyết định phạm vi F0 | H02/H04/H05 thiết kế, source scope và oracle nhất quán | Tạo worktree, viết mã P01, tạo fixture thực thi, chạy thực nghiệm |
| **I0A — Permit triển khai tĩnh F0 (chưa cấp)** | *Sau khi cấp permit riêng*: tạo một worktree được ghim trong workspace; viết checker/guard/generator cho F0, làm kiểm tra tĩnh không tiêu thụ dữ liệu khoa học | Exact Git+manifest, thiết kế checker 10/10 PASS_DESIGN, budget/guard được duyệt ở mức mô hình, danh mục tệp và QA âm tính đã khóa | Tải corpus F1/F2, huấn luyện BPE/GPT, chạy TEST khoa học, tự chạy QA động |
| **QA0 — Permit chạy kỹ thuật F0/guard (chưa cấp)** | *Sau khi I0A có bản mã cụ thể và QA tĩnh PASS*, cho phép một lượt kiểm thử chức năng F0 và âm tính Job Object/đĩa trên Windows, riêng với science | Mã nguồn và checker độc lập có SHA, môi trường và quyền hệ thống đã khóa, hiệu lực permit một lượt, bộ chạy không tự rerun | Học trên corpus thật, sửa ngưỡng sau thấy TEST, thực nghiệm E0 |
| **E0 — Permit thực nghiệm corpus BPE (chưa cấp)** | Chỉ nếu H02 nguồn F1/F2 được duyệt, D1 khoa học được khóa và QA0 đạt; chạy một lần trong namespace đã niêm phong | Source admission, corpus snapshot/split pristine, phương pháp và tiêu chí khoa học được khóa trước nhìn TEST | Huấn luyện GPT ngoài phạm vi P01 hoặc mở new-job generic |

**Quan trọng:** I0A chỉ là **cấu trúc permit được đề xuất**, không phải quyết định đang cấp. Nếu quy trình quản trị yêu cầu khóa D1 riêng trước I0A thì phải hoàn thành cổng đó; không được dùng văn bản này để vượt qua.

## 2. Danh sách điều kiện I0A tiền cấp quyền (không phải cấp quyền)

| ID | Điều kiện cần chứng minh trước quyết định I0A | Hiện trạng | Khi không đạt |
|---|---|---|---|
| `I0A-01` | GitHub main, PR #4, local main, origin và worktree P00 được kiểm tra read-only, exact commit và origin; Git sạch; không có reparse vượt root | GitHub PR #4 đã kiểm tra, local chỉ có snapshot trước; **HOLD** | Không tạo worktree, không đồng bộ cưỡng bức |
| `I0A-02` | Đề xuất vị trí worktree P01 **duy nhất** dưới `D:\WORK\RESEARCH\TokenToModel-Lab`, kèm denylist/allowlist các đường dẫn; không chạm P00 | Ranh giới đã nêu, chưa có permit đường dẫn cụ thể ⇒ **HOLD** | Không tạo worktree hay cache ngoài root |
| `I0A-03` | Đặc tả B0/BPE, oracle C01–C10 đã review và pin commit/SHA, sửa lỗi oracle đã ghi; định dạng merges/snapshot/manifest đủ để checker độc lập | 10/10 PASS_DESIGN; còn golden merges/manifest byte trước permit triển khai ⇒ **HOLD** | Không viết checker theo oracle mơ hồ |
| `I0A-04` | Source scope `F0_ONLY_DESIGN` được duyệt; cấm đọc F1/F2, TEST khoa học và dữ liệu kết nối | **PASS_DESIGN_SCOPE**, không phải quyền tạo fixture | Phát hiện nguồn thật ⇒ `SOURCE_RIGHTS_HOLD` |
| `I0A-05` | Cấu hình successor một nghĩa: `max_job_commit_bytes=4294967296`, wall=1800s, quota source=64MiB, temp+evidence=2GiB; từ chối `max_peak_rss_bytes` cũ nếu dùng sai nghĩa | Tên/đơn vị đã chuẩn hóa trong tài liệu; mã config chưa có ⇒ **PASS_DESIGN_ONLY** | `CONFIG_METRIC_CONFLICT`, từ chối |
| `I0A-06` | Thiết kế Job Object gồm suspended/assign-before-resume, không breakaway, supervisor ngoài job, wall-clock, write broker/ACL, W01–W12 | **PASS_DESIGN_ONLY**, chưa có guard đã chạy | Không cho phép fallback không guard |
| `I0A-07` | Kiểm tra RAM/đĩa tức thời và ngân sách tạm trong workspace, dự báo tác động sau cấp quyền; không áp dụng snapshot cũ như permit hiện hành | Windows snapshot 05/11 đạt ứng viên; cần đo lại ⇒ **HOLD_RECHECK** | Không thực thi hoặc cấp quyền thời hạn mở |
| `I0A-08` | Mã fixture/checker/guard phải thuộc đúng tệp được phép, phân tách trách nhiệm checker và generator; không ghi đè receipt; QA tĩnh/âm tính có tiêu chí FAIL | Hợp đồng thiết kế đã ghi; chưa pin danh sách tệp/mã độc lập cho I0A ⇒ **HOLD** | Không mở lệnh code tự do |
| `I0A-09` | Có quyết định riêng của chủ sở hữu, nêu exact HEAD, phạm vi ghi, số lần chạy, giới hạn thời gian/quyền mạng và cấm cleanup | **NOT_GRANTED** | Không tạo, tải, thực thi |

**Kết luận tiền cấp quyền I0A:** `PREAUTH_CONDITIONS_DOCUMENTED`; **`PREAUTH_ADMISSION=HOLD`**. Không được tính các mục `PASS_DESIGN_ONLY` là `PASS_IMPLEMENTATION`.

## 3. Hợp đồng độc lập kiểm tra H04 trong I0A/QA0

- Checker phải có source SHA riêng, không dùng lại thuật toán encode/decode hoặc chia tập từ code đang bị kiểm thử làm oracle.
- Bộ dữ liệu giả lập F0 phải được tạo từ byte hex/SHA đã khóa; không kéo bất kỳ corpus hoặc mô hình nào.
- C01–C10 phải được ánh xạ sang tên test, input, expected, error_code, failure_stage, số lượng, negative path và receipt riêng; không đạt khi chỉ khớp tổng 10/10 mà một test bắt buộc bị bỏ.
- Parser merges và snapshot phải từ chối sai magic, count, ID trỏ tương lai, byte thừa/truncated, đường dẫn ra ngoài workspace và file bị sửa byte.
- QA0 được quyền chỉ dùng **zero-science fixtures** và tình huống lỗi giả lập trên Windows nếu permit riêng đã cấp. Lượt QA động phải có biên bản SHA và phân xử PASS/FAIL/INCONCLUSIVE độc lập.
- Để kiểm tra guard, mọi worker phải được gắn Job Object trước khi chạy và mọi đường ghi bị hạn chế đúng; nếu chưa chứng minh được broker hoặc ACL chặn bypass thì `QA0_GUARD=HOLD`.
- Không sử dụng một kết quả `QA0=PASS` để tự mở E0: phải có source manifest F1/F2, split, khóa D1 và permit E0 riêng.

## 4. Phân cấp quyền dữ liệu

`F0_ONLY_DESIGN`: chỉ tài liệu, oracle và thiết kế checker, **đang áp dụng**.

`F0_ONLY_I0A_STATIC_IMPLEMENTATION`: khả năng xin cấp phép **sau này**, không tự phát sinh từ quyết định F0-only.

`F0_ONLY_QA0_EXECUTION`: cần permit một lượt chạy kỹ thuật, không tạo scientific TEST hay huấn luyện.

`F1/F2_E0_SCIENCE`: cần source `ALLOW` và khóa khoa học mới. Khi nguồn chưa đạt điều kiện ⇒ `H02=HOLD`, dừng nhánh corpus.

## 5. Trạng thái quyết định

`P01_D1_SOURCE_SCOPE=F0_ONLY_DESIGN_AND_ORACLE_REVIEW`  
`P01_D1_H04_CHECKER_DESIGN=PASS_10_OF_10`  
`P01_D1_H04_DYNAMIC_CHECKER=NOT_IMPLEMENTED`  
`P01_D1_H05_JOB_COMMIT_CONTRACT=CANONICAL_DESIGN_ONLY`  
`P01_D1_H05_GUARD_QA=NOT_EXECUTED`  
`P01_D1_H02_F1_F2=HOLD_UNAPPROVED`  
`P01_D1_SCIENTIFIC_PREREG_LOCK=HOLD`  
`TTM_P01_I0A_PREAUTH_ADMISSION=HOLD`  
`TTM_P01_I0_IMPLEMENTATION_PERMIT=NOT_GRANTED`  
`P01_WORKTREE_CREATION_AUTHORIZED=false`  
`P01_DATA_DOWNLOAD_AUTHORIZED=false`  
`P01_TOKENIZER_TRAINING_AUTHORIZED=false`  
`P01_MODEL_TRAINING_AUTHORIZED=false`  
`PR4_MERGE_AUTHORIZED=false`  
`P00_CLEANUP_AUTHORIZED=false`

**Bước tiếp theo:** `TTM_P01_D1_I0A_F0_STATIC_IMPLEMENTATION_PREAUTH_EVIDENCE_AND_DESIGN_ADJUDICATION`: chỉ chuẩn bị bằng chứng tiền cấp quyền I0A-01..09 (exact Git, allowlist, golden byte formats và budget read-only), rồi thẩm định độc lập; chưa cấp permit hoặc viết mã.
