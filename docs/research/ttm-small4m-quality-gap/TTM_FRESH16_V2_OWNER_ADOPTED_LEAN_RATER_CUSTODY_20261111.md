# TTM FRESH16 — Owner ADOPT_V2 và cơ chế custody tinh gọn

**Operation:** `TTM_FRESH16_V2_OWNER_EXPLICIT_ADOPTION_AND_RATER_CUSTODY_BINDING`  
**Ngày:** 2026-11-11  
**Repository:** `minhtri22/TokenToModel-Lab`  
**Branch:** `research/ttm-small4m-prompt-adherence-continuation-design-20261111`  
**Base HEAD ngay trước quyết định:** `979db370441bb8e9f27932777905c7ab40d9ade2`  
**V2 accepted candidate Git blob:** `27b994b3b3283b2611af21d63acc5d37abf45013`  
**Original prompt blob:** `6299a073f0b7c7f8ea890ba9d9b29eaed9442f1f`  
**Original rubric/H1/H2 blob:** `69668664df23d2246cd65935ab049054aea43e7a`  
**Status:** `OWNER_ADOPTED_V2` · `SCIENCE=NOT_EXECUTED`.

## 1. Quyết định owner được ghi nhận — không tạo permit phụ

Trong tin nhắn ngày 2026-11-11, owner trực tiếp yêu cầu `TTM_FRESH16_V2_OWNER_EXPLICIT_ADOPTION_AND_RATER_CUSTODY_BINDING`, quyết định rõ **`ADOPT_V2`**, đồng thời xác nhận bằng lời rằng owner và executor **chưa sinh, xem hoặc sử dụng đầu ra FRESH16 trước khi chấp thuận**.

Ghi nhận phát biểu này là `OWNER_FIRST_PARTY_NO_PRIOR_OUTPUT_STATEMENT_ACCEPTED`. Đây là lời xác nhận của owner về **cả hai vai trò**, không được trình bày thành hai chữ ký độc lập, cũng không cần yêu cầu owner điền lại cùng một câu vào hai biểu mẫu. Với pilot nhỏ, trạng thái bằng chứng là `OWNER_ASSERTED_NOT_FORENSICALLY_VERIFIED`, đủ để ghi quyết định áp dụng prospective ở cấp nội bộ. Nếu có bằng chứng trái ngược, phán quyết sẽ chuyển `HOLD` mà không sửa dữ liệu cũ.

**Quyết định thực sự có hiệu lực:** `ADOPT_V2` dùng cách chấm V2 cho FRESH16 **kể từ đây**. Phụ lục V2 là `PROSPECTIVE_OPERATIONAL_OUTCOME_REDEFINITION`, không phải "cách hiểu vốn có" của rubric cũ. Biên bản pending/template trước commit này vẫn là bằng chứng lịch sử tại thời điểm tạo; quyết định này **supersedes DEFER default**, không ghi đè chúng.

Independent Protocol Reviewer cuối cùng đã trả `ACCEPT_CANDIDATE_FOR_OWNER_APPROVAL` và `PASS_PROTOCOL_REVIEW_FOR_OWNER_DECISION`; P4 về custody còn HOLD triển khai. Reviewer này **không** nhận vai trò chấm đầu ra và không làm người phân xử H2.

## 2. Gộp custody thành một lượt, không yêu cầu thêm micro-permit

Chỉ còn hai chức năng độc lập với executor, có role ID và nhiệm vụ cố định:

| Role ID | Chức năng | Phân công thực tế | Cách xác nhận tối thiểu |
|---|---|---|---|
| `FRESH16_S1_OUTPUT_RATER` | Chấm 32 output cá thể từ prompt + phần sinh mới, không nhãn step/pair, khóa S1 SHA | **TO_BE_ASSIGNED_AT_SESSION_CREATION**; 1 người hoặc 1 phiên AI mới độc lập | Ghi tên người hoặc model/version/session + SHA điểm ở lượt chấm |
| `FRESH16_S2_PAIR_ADJUDICATOR` | Đánh giá 16 cặp đối chứng từ phiếu S1 đã khóa, vẫn mù checkpoint; khóa S2 SHA | **TO_BE_ASSIGNED_AT_SESSION_CREATION**; phiên/người khác với rater và executor | Ghi tên người hoặc model/version/session + SHA cặp ở lượt chấm |

**Không** giả vờ đã chỉ định người hoặc phiên không tồn tại. Chủ dự án có thể mở hai cuộc hội thoại mới riêng biệt sau lượt chạy; một AI rater + một AI adjudicator chỉ cho kết luận exploratory và không chứng minh độc lập ở mức nhiều người chấm. Handoff rater/adjudicator đã chuẩn bị trong `docs/research/ttm-small4m-quality-gap/TTM_FRESH16_V2_TWO_AGENT_RATER_HANDOFF_AND_BLIND_SCORING_PROTOCOL_20261111.md`; danh tính thực được ghi cùng nguồn điểm, không phát thêm quy trình phê duyệt riêng.

**Kết quả custodian binding hiện nay:** `ROLE_CONTRACT_BOUND`, `ACTUAL_SESSION_UNASSIGNED`. Đây là phần còn thiếu **thực tế**, không phải HOLD vì chủ dự án chưa điền biểu mẫu.

## 3. Ba bước dữ liệu chấm, hai SHA làm bằng chứng bất biến

- **Trước CPU run:** pin đúng source/checkpoint SHA; tạo mapping mù nhãn 32 output → 16 cặp/2 checkpoint, niêm phong mapping trong thư mục project. Ghi hash đã khóa vào receipt nguồn, **không công khai mapping**; không chọn lại checkpoint hoặc prompt.
- **S1:** sau khi run được owner cho phép và giữ nguyên 32 output gốc, rater chấm cá thể. Khóa JSON phiếu điểm S1 bằng SHA-256 và **commit hash receipt** lên đúng nhánh trước khi đưa pairing cho adjudicator.
- **S2:** adjudicator xem các cặp mù checkpoint, không sửa S1, đánh giá `LEXICAL_SWAP_ONLY` / `SEMANTIC_ROLE_BINDING` / `FACT_CONDITIONED_ACTION` / `GENERIC_COMMON_VALID` và swap countercheck. Khóa JSON phiếu cặp S2 bằng SHA-256 và **commit hash receipt** trước khi mở checkpoint.
- **Cuối cùng:** giải mù, tính H1/H2 một lần; không điều chỉnh ngưỡng/điểm; chưa có quyền thực thi ở lượt owner ADOPT_V2 này.

Dùng GitHub receipts đã commit làm nơi neo SHA, **không cần tuyển thêm một người giữ bằng chứng** nếu dự án chỉ có một owner. Không công khai text đầu ra hay mapping riêng tư trên GitHub nếu không cần. Nếu không thể khóa S1/S2 trước giải mù, dừng `HOLD_SCORING_DISPUTE`.

## 4. Các điều đã hoàn thành và điều chưa hoàn thành

- `SOURCE_QA=PASS_RECORDED_SCOPED`, 11/11 offline unit QA + native BPE 16/16 + checkpoint SHA 2/2 theo receipt Windows; không tái kiểm nguồn vì chưa thay dữ liệu.
- `V2_PROTOCOL_REVIEW=PASS_FOR_OWNER_DECISION`.
- `OWNER_V2_ADOPTION=ADOPT_V2`.
- `OWNER_FIRST_PARTY_NO_PRIOR_OUTPUT_STATEMENT=RECORDED_FOR_OWNER_AND_EXECUTOR`.
- `RATER_ROLE_PROTOCOL=BOUND`, `S1_RATER_SESSION=NOT_YET_INSTANTIATED`, `S2_ADJUDICATOR_SESSION=NOT_YET_INSTANTIATED`.
- `BLIND_MAP=NOT_CREATED`, `CPU_RUNNER=NOT_LOCKED`, `EXECUTION=NOT_AUTHORIZED`, `SCIENCE=NOT_EXECUTED`.
- `main`, `lineage.md`, các input frozen, kết quả FRESH12 và TEST không đổi.

**Khóa nghiên cứu giữ nguyên:** H1 ≥12/16 ở checkpoint1024 với adherence≥2; H2 ≥6/8 pair có khác biệt fact-dependent đúng nghĩa và ít nhất 1 cặp ở mỗi 4 nhóm; step1280 mô tả; 32 output CPU max 64 tokens/chuỗi, greedy, context 256, no retry, train=NO.

**Bước thực hiện tiếp theo:** `TTM_FRESH16_V2_SINGLE_CPU_RUNNER_BLIND_MAP_RATER_CUSTODY_INTEGRATED_GO_NO_GO` — chuẩn bị runner CPU và sealed map trong một lượt, mở hai phiên rater/adjudicator tách biệt, rồi trình **một quyết định GO/NO-GO science**. Không mở thêm permit kỹ thuật.
