# TTM-Small-4M D1 — Gói tái khóa seed riêng tư V2 và quyết định HOLD toàn batch

**Ngày:** 11/11/2026  
**Công việc:** `TTM_SMALL4M_D1_VERSIONED_PRIVATE_SEED_REKEY_OVERLAP_CUSTODY_AND_SINGLE_OWNER_RELEASE_GO_HOLD_NO_SCIENCE`  
**Nhánh duy nhất:** `research/ttm-small4m-prompt-adherence-continuation-design-20261111`  
**Kết luận một lần:** **`HOLD_SINGLE_FULL_BATCH_NO_SCIENCE_RELEASE`**.

## 1. Kiểm tra nguồn và bất biến

- Biên nhận QA thực từ Windows do chủ dự án cung cấp: `TTM_D1_STATIC_QA=PASS_SCOPED_PRIVATE_PACKET`, SHA-256 thô V1 `c43dde98c4fd2328ece9baba549c8bbc369964f0d19d4ecd9f8bb081d3256957`, **266.415 byte**, SHA-256 chuẩn hóa LF `de5c0acae9a863e255922963d9644623ff6b1cbfedc0ff9edd7d8225cbac7603`. Đã đối chiếu lại đúng đường dẫn V1 trên Windows và biên nhận GitHub.
- Mã nguồn khoa học E0 ở worktree Windows vẫn `c05872354d892a9656f8f98642866f7eebfd0f50`. `main` ở `5d52e32f20021e36f08f284ef9864d3ba36dbead`. `lineage.md` nhánh D1 giữ nguyên Git blob `9110d101601e6ebfb64d9804f3704a90cb284420`, kết thúc ở **L0015: FRESH16 V2 FAIL có giới hạn**.
- Không mở TEST, Q1Q2, mapping đánh giá cũ; không sửa điểm FRESH16 hoặc các bản ghi khoa học PASS/FAIL trước đó.

## 2. Đã tạo bằng chứng triển khai V2, không khai nhận V2 đã chạy

- Đã chuẩn bị trên Windows `_tmp/TTM_D1_V2_PRIVATE_REKEY_STATIC_ONCE_20261111.py`, đồng thời commit nguồn công khai không chứa giá trị seed. Mã kiểm chứng Git blob: `8b6a26693610eb4b1e7984dff937eadf1114be44`.
- Chương trình dùng bộ sinh số ngẫu nhiên an toàn (`secrets`) để tạo ba seed mới khác seed cũ, thay cả 384 ánh xạ seed và hoán vị lại mã chấm mù 512 trường hợp; **giữ nguyên 16 gia đình, 128 DEV, 64 đối chứng trung tính và mọi ứng viên**. Các giá trị seed mới chỉ được sinh khi chương trình thật sự chạy, không có trong mã công khai.
- Cùng một chương trình thực hiện kiểm tra BPE thật từ tệp TRAIN-only đã khóa, kiểm đếm, cân bằng dữ kiện/ứng viên, vị trí cue và không tràn context. Tạo bản chấm mù riêng chỉ có mã mù, prompt và các trường điểm trống; thứ tự các dòng chấm được đảo riêng, không công khai decoder, seed, ground truth hoặc prompt ID.
- Đã tạo trình gọi PowerShell 5.1 `_tmp/Invoke-TTM-D1-V2-Private-Rekey-PS51.ps1`, khóa nguồn bằng SHA-1 đối tượng Git trước khi gọi Python, khóa SHA-256 byte V1, không ghi đè và đối chiếu lại SHA-256 của V2/phiếu chấm sau khi ghi.
- Công cụ RemoteMCP từ chối hai dạng gửi lệnh với thông báo **scientific job admission held until exact command evidence qualifies**. Vì vậy **chương trình V2 chưa chạy**. Đã kiểm tra Windows: V1 tồn tại, tệp V2 và phiếu chấm V2 **chưa tồn tại**; không có SHA-256 V2 để công bố. Tác vụ điều phối đã tạo vẫn ở trạng thái `RECOVERABLE`; không có job suy luận/huấn luyện được tiếp nhận. Không tự bỏ qua cổng thực thi.

## 3. Giới hạn xác minh trùng lặp, quyền và chấm mù

- Hai nguồn lịch sử công khai đã được kiểm tra ở bước trước: không tìm thấy trùng nguyên văn trong phạm vi so sánh phần mở đầu tình huống. Đây **không phải** chứng nhận không trùng gần về ngữ nghĩa toàn bộ.
- Không tự mở lại dữ liệu giữ lại (TEST), Q1Q2 hoặc nhãn riêng tư FRESH16/AC để tuyên bố đã kiểm tra đủ. Trạng thái `PRIVATE_SEMANTIC_OVERLAP=NOT_VERIFIED` giữ nguyên.
- Tác quyền của văn bản DEV mới có nguồn tự biên soạn bằng AI; chưa có biên nhận xác nhận quyền sử dụng (owner rights attestation) từ chủ dự án. Người chấm độc lập và quyền bảo quản mapping/seed chưa được chỉ định hay chứng thực. Phiếu chấm mù V2 chỉ là **mẫu chưa sinh đầu ra**.

## 4. Phân xử một cổng

**Kết luận chính thức hôm nay: `HOLD_SINGLE_FULL_BATCH_NO_SCIENCE_RELEASE`.** Đây là HOLD về điều kiện chạy, không phải FAIL về năng lực mô hình. Không sử dụng V1 đã lộ seed cho science; không tự công bố PASS của V2. Giữ `D1_STATIC_QA_V1=PASS_SCOPED`, `NEW_TRAINING=NO`, `NEW_INFERENCE=NO`, `TEST=SEALED`, `AC=NO_GO_PREEXEC`, `O1=DEFER`, `MAIN/LINEAGE=UNCHANGED`.

### Bước thực hiện tiếp theo

**`TTM_SMALL4M_D1_V2_STATIC_REKEY_OWNER_CONSOLE_ONE_SHOT_RECEIPT_THEN_SINGLE_ADJUDICATION`**.

Chủ dự án chạy **một lần** tệp PowerShell đã ghim trên Windows. Chỉ dùng receipt mới để đối chiếu SHA thô V2 và QA độc lập; mọi vấn đề quyền/nguồn riêng tư/người chấm còn thiếu phải được ghi đúng HOLD trong **cùng một lần phân xử toàn batch**, không tạo micro-permit và không chạy science.
