# TTM Vector Memory V3 — Kết quả tích hợp nguồn NON-TEST 256, QA âm tính và GO/HOLD

**Operation:** `TTM_VM_V3_FRESH256_NEGATIVE_GROUND_TRUTH_AND_NONORACLE_SOURCE_ONEPACKET_QA_FREEZE`  
**Ngày:** 12/11/2026 · **Nhánh:** `research/ttm-vector-memory-architecture-20261111`  
**Phán quyết chính:** **`HOLD_PENDING_TWO_P1_INDEPENDENT_HUMAN_REVIEWS`** về khả năng chấp nhận nhãn nguồn, mặc dù `SOURCE_QA=PASS_99/99`.  
**Science:** `HOLD_NO_PINNED_SCORER_OR_OWNER_ONE_SHOT_RELEASE`. Không chạy Reader, không huấn luyện, không chạy retriever trên 256 PROBE thật để tính Recall, không mở DEV/TEST, không dùng GPU.

## 1. Những gì thực sự được triển khai

Một gói **bốn tệp Python** đã khóa tại source commit **`51268b205648060ad0fa13276d67180c2fcaddbb`**:

| Thành phần | Git blob đã đối chiếu |
|---|---|
| `v3_fresh256_fixture.py` | `5f51b8b464e54a370f3a3fa99d91307118f52f46` |
| `v3_nonoracle_retriever.py` | `68bfeaaf1d0acf0cf446e4d734e34368fbf8f702` |
| `v3_p1_reviewer_custody.py` | `beaaa78126282439c94b2d0d525297e6b35266a5` |
| `v3_independent_source_qa.py` | `041e174579e5a842a0d4dfa46637fe036e9954ec` |

Thêm PowerShell 5.1 một packet: `Invoke-TTM-VM-V3-Source-Freezer-OnePacket-PS51.ps1` Git blob `fb0063f18ddcbdb56cbddd055908509088ee2675`. Đây là script kiểm SHA, tạo đúng một fixture riêng tư và hai phiếu thẩm định mù trên D:, **không phải science runner**.

## 2. Dữ liệu V3 và bằng chứng QA

- **Fixture V3:** 256 trường hợp, 8 strata × 32, 32 card/case, 8.192 key riêng; 128 positive (trong đó 96 primary) và 128 negative.
- **Seed:** `TTM_VM_V3_FRESH256_NONTEST_SEED_FROZEN_20261112_A1`.
- **SHA-256 byte fixture:** **`d473292d40dfb475d0b44f7d393341e19d846308820dcb4f5cbac6acb2c0e543`**; kích thước **2.128.853 bytes**.
- Key mới dạng `obju` + 11 phụ âm, khác namespace cũ đã biết. Điều này **không phải** đối chiếu nội dung TEST thực tế, vì TEST vẫn niêm phong.
- Negative không có `target_key`, `answer`, `correct_memory` hoặc `wrong_memory` hợp lệ (các trường là JSON null). Không được bịa target Oracle để score NLL trên negative.
- Ground-truth kiểm qua đường luật cấu trúc khác mã Retriever: P0/P1/P2/P3 đều có **một** candidate được quy tắc public cho phép; N0/N1 có **ít nhất hai**; N2/N3 là vô hiệu/không còn candidate.
- QA độc lập **99/99 PASS** gồm cấu trúc và SHA, nhãn dương/âm, tương đồng source ID, phủ định/mâu thuẫn, từ vựng, dữ liệu giả lập cố ý gây sai, thứ tự card, cấm field `value/target_key/answer/gold_action/case_id`, mask SELECT/ABSTAIN và từ chối phiếu reviewer chưa ký.
- **Retriever chỉ chạy trên ngân hàng 32 card giả lập, tách khỏi PROBE V3**. Fixture 256 chỉ được tạo trong sandbox để kiểm schema/SHA/ground truth; chưa đưa lên GitHub, chưa có result Recall/NLL thật và chưa tạo tệp owner Windows.

**Lỗi được phát hiện và sửa trước freeze** (không giấu FAIL nội bộ): P3 từng có hai ứng viên hợp lệ do hard negative thứ ba; generator được sửa để chỉ còn một. Hai novel P1 phrases từng chứa nguyên văn một từ cũ V2 (`ink-blue`, `snailshell-coiled`); được thay trước khi khóa seed/data SHA và rerun QA 99/99. Không có khoa học V3 nào bị chạy hoặc tiêu thụ trước sửa.

## 3. Hợp đồng Retriever không đọc nhãn vàng

Hàm chính `retrieve(question, public_index)`; `public_index` chỉ chứa `key`, `source_id`, `retrieval_text`. Nếu bị chèn thêm outcome (kể cả `value`), nguồn không đồng nhất, thiếu field hoặc có key trùng, **fail closed**. Nếu query không có một lựa chọn duy nhất, trả `ABSTAIN` với **0** bản ghi active. Không dùng tiêu đề strata hoặc case ID để quyết định.

P1 dùng 18 cụm paraphrase đề xuất **mới so với bảng V2**, nhưng **được ánh xạ rõ trong mã nguồn Retriever V3 trước thực nghiệm**. Chúng cần thẩm định ngữ nghĩa từ người độc lập; kể cả tương lai PASS, đây vẫn là **lookup từ điển V3 mở rộng** chứ không phải chứng minh open-domain semantic retrieval.

## 4. Quy trình hai người đánh giá độc lập — còn thiếu biên nhận

Tạo hai packet `P1_REVIEW_A_TEMPLATE.json` và `P1_REVIEW_B_TEMPLATE.json` cho **32** trường hợp P1. Chúng chỉ có question + public index; không có target, answer, truth constraints hoặc value. Hai reviewer phải chấm trong phiên tách biệt, mỗi người điền selected key (hoặc null), reason, confidence 0–3, danh tính, thời gian và lời xác nhận không truy cập gold/bài người khác.

Validator yêu cầu **cả hai khác reviewer ID, 32/32 lựa chọn đồng thuận và khớp truth**, không tự sinh chữ ký/đáp án thay. Nếu bất đồng → HOLD, không loại câu hay thay dữ liệu hậu nghiệm. Phương thức xác nhận reviewer hiện là attestation bằng JSON, không phải chữ ký số; không thể tự kiểm tính xác thực con người hoặc ngăn thông đồng bằng mã này.

**Tại thời điểm phát hành:** `HUMAN_P1_REVIEW_RECEIPTS=NOT_RECEIVED`. Vì thế **`SOURCE_RELEASE=HOLD`**, dù QA 99/99 đã PASS. Không được tuyên bố “hai người chấm mù PASS”.

## 5. Ngưỡng tiền đăng ký giữ nguyên; chưa dispatch khoa học

Theo thiết kế V3 đã đóng băng trước triển khai: Positive primary P1/P2/P3 yêu cầu ≥72/96 chọn đúng; riêng P1 ≥20/32. Negative N0–N3 yêu cầu ≥122/128 từ chối đúng, tối đa 6 false selections. Reader NLL chỉ đo trên positives, gồm cả trường hợp positive abstain dưới nhánh bypass; paired delta A−B1 và C1−B1 ≥0,05 và bootstrap percentile lower95 >0 (2.000 draws trên 96 story-pairs, seeds 20261120/20261121). Oracle A−O1 ≥0,05 để xét domain shift. Không sửa tiêu chí sau khoa học.

Các ngưỡng khoa học mới đang ở **preregistered source/protocol level**, không phải **executable full science prereg**, vì scorer one-shot V3 chưa triển khai/QA và reviewer P1 chưa đủ. Không cấp GO CPU, không mở TEST hoặc GPU.

## 6. Cách vận hành nguồn trên máy Windows mà không tải lại checkpoint

Chủ máy lấy `Invoke-TTM-VM-V3-Source-Freezer-OnePacket-PS51.ps1` ở nhánh này, xác minh Git blob của script, rồi chạy bằng PowerShell 5.1. Gói này tạo worktree riêng detached ở source commit `51268b2...`, chạy QA 99/99, chỉ sinh fixture nếu chưa có, so SHA native trên D:, tạo hai packet mù, kiểm không đổi `main`/L0022, và in `V3_OWNER_SOURCE_GO_HOLD=HOLD_P1_REVIEW` khi chưa có đủ phiếu.

Mọi tệp riêng tư/chấm mù nằm dưới `D:\WORK\RESEARCH\TokenToModel-Lab\_evidence\vector-memory`. Không sửa/ghi bất cứ tệp nào trên ổ C ngoài việc sử dụng Python interpreter sẵn có; `PYTHONDONTWRITEBYTECODE=1`.

## 7. Quyết định duy nhất, giới hạn, và bước tiếp theo

- **`V3_SOURCE=FROZEN`**, `FIXTURE_256_SCHEMA_SHA=PASS`, `NEGATIVE_QA=PASS_99/99`.
- **`P1_SEMANTIC_RATER_CUSTODY=HOLD_PENDING_TWO_INDEPENDENT_HUMAN_REVIEWS`**, **`OWNER_SOURCE_GO_HOLD=HOLD`**.
- **`CPU_SCIENCE=HOLD_NOT_AUTHORIZED`**, `READER_FORWARD=0`, `TRAINING=NO`, `TEST=SEALED`, `GPU=NO`, `OLD_PROBES=CONSUMED_NOT_REUSED`.
- `lineage.md` vẫn ở L0022; không tạo L0023 do chưa có thí nghiệm khoa học V3, `main` giữ nguyên.

**Bước thực hiện tiếp theo:** `TTM_VM_V3_P1_TWO_REVIEWER_CUSTODY_AND_FROZEN_SCORER_ONEPACKET_FINAL_GO_HOLD` — nhận biên nhận chấm mù thật, khóa scorer mới và thực hiện QA tích hợp trước khi đưa một quyết định GO/HOLD duy nhất cho CPU. Không mở chuỗi micro-permit hoặc tự khởi chạy Reader.
