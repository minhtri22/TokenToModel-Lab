# G1 SIX × TTM — Một quyết định chủ sở hữu cho gói technical provisioning v1e

**Ngày:** 2026-11-10  
**Nhiệm vụ:** `TTM_SIX_G1_V1E_INTEGRATED_PROVISIONING_SINGLE_OWNER_DECISION_AND_DISTINCT_QA`  
**Quyết định hiện hành:** `PROPOSED / OWNER_NOT_YET_APPROVED`. Đây là đề xuất để chủ sở hữu xem và phê duyệt, **không phải** giấy phép thao tác Windows/Colab hoặc chạy khoa học.  
**Khóa:** `G1_SCIENCE_LOCK=HOLD`; `OWNER_SCIENCE_PERMIT=NOT_ISSUED`; `G1_PRIVATE_TEST_OPENED=NO`.

## I. Cơ sở phản biện đã xác minh

- v1e source frozen: `implementation/ttm-six-g1-production-gates-methods-v1e-20261110@1efca4ca080572dcd22bbe658701b221ca46f7dd`.
- Báo cáo Codex mới (nguyên bản cục bộ): `D:\WORK\RESEARCH\TokenToModel-Lab\_tmp\G1_V1E_CODEX_DISTINCT_REVIEW_20261110\G1_V1E_CODEX_DISTINCT_REVIEW_20261110.md`; SHA256 reviewer-reported `82a7f371f60b93dba23f3e97dfdd754ad015b8232de6b07860e4ead65514faea`.
- Receipt cùng nơi; SHA256 reviewer-reported `47af2897e343567b92ccaa6477445a61fe9b3a651db37ee67debd049175d76a6`.
- Hai văn bản đã được **import qua read-only remote text** và lưu trên nhánh review `review/ttm-six-g1-v1e-codex-distinct-owner-import-20261110`; bằng chứng Git blob văn bản là bằng chứng của bản import, không tự chứng minh SHA256 raw byte gốc.
- Reviewer: `HOLD`; provenance v1e `PASS_8/8`; Win32 two fault paths `PASS_OWNER_LOG_READBACK`; reviewer Win32 rerun `NOT_TESTED`; 13/13 CPU adversarial expected. **Lỗi logic xác nhận**: chữ ký chủ sở hữu không so sánh exact launcher SHA/amendment SHA với trusted expected values; nonce ACK cũ có thể được xác minh lại khi challenge không thay đổi. Mô phỏng CKA: 8 nhóm × 8 hàng, independent by groups, row permutation false-positive 32/32; group permutation 0/32. **Không khẳng định T1 có 8 nhóm.**
- Hợp đồng phạm vi G1 gốc đã được đối chiếu ở `G1_SCIENCE_ASSURANCE_SCOPE_AND_ONE_BATCH_GATE_CLOSURE_DECISION_20261110.md` @ `d9dfbd5383a35ddefae788cd57afb61b90caa62e`: G1 scoped cross-model feasibility 128 TRAIN / 64 DEV / 64 TEST; sáu hard gates vẫn bắt buộc trên đường G1 gốc.

## II. Quyết định đề xuất — phê duyệt đúng MỘT lô kỹ thuật, CHƯA phê duyệt khoa học

Nếu owner trả lời **`APPROVE_G1_V1E_TECHNICAL_PROVISIONING_ONLY`**, phạm vi công việc được đề xuất là:

**Mục đích duy nhất:** triển khai một reference instance cho **một run_id giả/QA**, một lượt synthetic end-to-end validation và một lần Codex adjudication chung. Không xây dịch vụ tổng quát, không chạy Qwen technical smoke đã tiêu thụ, không dùng G1 private TEST.

**Host và đường dẫn:**
- Windows 11 máy chủ sở hữu: chỉ tạo artifact/file trong `D:\WORK\RESEARCH\TokenToModel-Lab\_trusted\g1` và `D:\WORK\RESEARCH\TokenToModel-Lab\_tmp`.
- Tạo account/service principal hoặc thay đổi ACL/OS service là **thao tác cấu hình toàn hệ thống**, không được thực hiện chỉ vì tài liệu này. Owner cần xác nhận riêng rằng **quyết định một lô cũng cho phép đúng các loại thay đổi hệ thống cần thiết**, không cho phép sửa/xóa tài khoản đã có, thay ACL của thư mục dự án khác hay ngoài scope.
- Đối với Colab Free T4, chỉ phép kiểm tài nguyên kỹ thuật bằng workload synthetic và thật sự được owner chấp thuận mới được dùng; không mount/test dữ liệu G1 thật trong bất kỳ QA preexecution nào.

**Sáu thành phần của đúng một batch:**

1. **Trusted authority/launcher:** sửa verify admission để bắt buộc so sánh `launcher_commit_sha` và `method_amendment_sha256` với expected pins do launcher ngoài payload nắm giữ; exact model/tokenizer/manifest/run/data-scope pins; test tampering/swap; owner/writer/witness trust anchors riêng, khóa bí mật không vào Git/worker/QA logs; khoa học fail-closed.
2. **TEST broker:** một worker SID/token thực sự khác broker/controller, Windows DACL nghiêm, test `AccessDenied` bằng TEST giả **trước FIT_FROZEN**, gồm junction/hardlink/symlink và cửa truy cập Drive/Colab; không stage G1 TEST thật trước được phép. Nếu Colab không thể cô lập, hard gate HOLD; không thay bằng kiểm tra path chuỗi.
3. **Writer/pack/ledger:** service writer có quyền ngoài worker, pin SHA của đúng bytes parse, content addressed staging/commit+signed receipt, crash injection ở ranh giới publication/receipt, concurrency và fail-closed replay; không cho worker tự cấp receipt.
4. **Witness/one-shot:** monotonic signed latest-tip & one-use challenge nonce có trust domain và quyền rollback tách khỏi controller/worker; independent tamper/restore cả DB và worker. **Thư mục cùng user trên D: hoặc GitHub chung credential không chứng minh ranh giới này.** Không có endpoint độc lập đủ quyền → HOLD.
5. **Supervisor:** source v1e Win32 failure cleanup giữ scoped PASS; QA thêm process-tree failure/timeout, cumulative 3.600 s/model / 7.200 s/run, peak 12 GiB và khả năng kill trên **science target**; không thay bằng Win32 CPU test. T4 testing chỉ khi owner cho phép tài nguyên và không dùng teacher/TEST.
6. **Methods trước TEST:** sửa đúng lỗi CKA row-permutation dưới group dependence bằng quy tắc xác định nhóm và group exchangeability đã khóa trước khi biết outcome, bootstrap theo nhóm/sensitivity phù hợp; xác minh lineage/near-dups từ nguồn chỉ **sau khi có data rights phù hợp**; prospective power, low-power `INCONCLUSIVE`. Reviewer phải duyệt amendment trước bất kỳ TEST read; cấm thay ngưỡng G1 hậu nghiệm.

**Một bộ QA tích hợp duy nhất** phải bao gồm: exact pins, tiêu cực OS principal thật, fake TEST prerelease deny, writer crash & forged receipt, witness rollback cả hai miền + nonce replay, process-tree kill/resource budgets, CKA group-null và methods. QA dùng TEST giả; không lặp lại `29/45/61`, Win32 `2/2`, Qwen technical smokes.

**Một quyết định sau batch:** Codex độc lập đưa ra `PASS_DISTINCT_REVIEWER/HOLD/FAIL` với 6 hàng `PASS/FAIL/NOT_TESTED`. Không chấp nhận tác giả ký kết luận thay reviewer. Dù PASS, vẫn cần **owner science admission riêng** để cho phép quyền data/staging/derived feature/Colab, test release, run ID và one-shot.

## III. Hai điều kiện không thể giả định

1. **Phân tách quyền thật:** owner phải có thể cấp SID hoặc cơ chế tương đương; Windows ACL phải chứng minh trên actor thực; Colab-boundary được chứng minh trên **mọi** đường dữ liệu tới runtime G1. Windows PASS không tự PASS Colab.
2. **Witness ngoài miền rollback:** owner phải chọn hoặc kiểm định một endpoint/credential độc lập; không được dùng lại cùng tài khoản có thể sửa/xóa cả ledger và witness. Nếu không có, không có PASS G1 confirmatory.

Nếu một trong hai là bất khả thi trong Free Colab/môi trường hiện hữu: **dừng tại một HOLD hữu hạn**, báo chi phí/ràng buộc. Không chia thành micro-permits và không tiếp tục vô thời hạn.

## IV. Phương án thay thế nếu owner muốn kết quả sớm mà không dựng ranh giới production

Đề xuất sửa hợp đồng trước: `G1_EXPLORATORY_TRAIN_DEV_ONLY`. Chỉ dùng synthetic/public data hoặc T1 TRAIN/DEV sau khi được phép đúng quyền. Không đọc G1 private TEST, không dùng one-shot TEST, không coi kết quả là G1 gốc PASS, không dùng để tune G1 confirmatory rồi mở TEST gốc thiếu amendment. Mọi so sánh phải gắn nhãn `EXPLORATORY / NOT_CONFIRMATORY` và kế hoạch nguồn/cost được khóa mới.

**Mặc định hiện hành:** giữ `G1_ORIGINAL_SCOPE_UNCHANGED`; phương án trên **chưa được owner chọn**.

## V. Một quyết định owner cần ghi nhận

- `APPROVE_G1_V1E_TECHNICAL_PROVISIONING_ONLY`: chấp thuận một lô triển khai/QA kỹ thuật đúng phạm vi mục II, gồm thay đổi principal/ACL **chỉ sau khi có kế hoạch chính xác về account, SID, DACL diff và rollback/cleanup được owner xem**, không tự cấp science.
- `DECLINE_G1_V1E_PROVISIONING`: giữ HOLD, không triển khai OS/security.
- `REQUEST_G1_EXPLORATORY_AMENDMENT`: không provision full G1 trước mắt; soạn hợp đồng pilot TRAIN/DEV không TEST để owner/reviewer duyệt trước chạy.

**Tài liệu này tự nó không phải một câu trả lời phê duyệt. Không có chữ ký owner, no real TEST, no science.**

## VI. Exit criteria

`OWNER_TECHNICAL_PROVISIONING=NOT_YET_APPROVED` · `SIX_HARD_GATES=HOLD` · `METHODS_GROUP_EXCHANGEABILITY=HOLD` · `SCIENCE_EXECUTED=NO` · `G1_PRIVATE_TEST_OPENED=NO` · `OWNER_SCIENCE_PERMIT=NOT_ISSUED` · `G1_SCIENCE_LOCK=HOLD`.

**Bước thực hiện tiếp theo:** owner chọn **một** quyết định ở mục V. Chỉ khi `APPROVE...` được owner nêu rõ, trình/đóng gói một exact Windows principal/DACL+external-witness+Colab boundary plan và triển khai **một** lượt technical provisioning / synthetic integrated QA / Codex adjudication; science vẫn HOLD.
