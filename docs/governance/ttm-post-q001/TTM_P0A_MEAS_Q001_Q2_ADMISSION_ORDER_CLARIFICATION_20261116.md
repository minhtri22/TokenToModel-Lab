# TTM-P0A-MEAS-Q001 — Q2 admission-order clarification (source-only)

**Ngày:** 2026-11-16 · **QuestionID:** `TTM-P0A-MEAS-Q001`  
**Scope:** `SOURCE_ONLY · DESIGN_ONLY · NO_SCIENCE`.  
**Exact independently reviewed Q2 source:** [`8bf0601c716b5f6395e3b758ee066ff41c9a554d`](https://github.com/minhtri22/TokenToModel-Lab/commit/8bf0601c716b5f6395e3b758ee066ff41c9a554d).  
**Owner Q2 disposition:** `GO_ACCEPT_Q2_SOURCE_ONLY` — không phải owner Q4/science permission.

## 1. Tại sao cần làm rõ

Q2 authored report đã gộp `BEFORE_SOURCE_ACCESS_OR_PRODUCTION_AUTHORING` thành một stage. Phản biện F-M01/X20 cho thấy nếu AD-02/03/05 đòi xác minh dữ liệu thực **trước bất kỳ quyền truy cập nguồn nào**, sẽ tạo vòng điều kiện bất khả thi. Tệp này là **clarification có thẩm quyền governance**; giữ nguyên bốn blob đã được reviewer kiểm toán, không sửa hồi tố source/receipt.

## 2. Thứ tự non-compensatory admission

| Giai đoạn | Điều kiện chặn bắt buộc | Hiện trạng |
|---|---|---|
| Q2 owner paper acceptance | Source/design review, M0–M4, five options, hard veto và owner signoff | `GO_ACCEPT_Q2_SOURCE_ONLY` |
| **Trước bất kỳ source access** | `AD-01R`: quyền đọc/sử dụng/chuyển đổi/PII/copyright/third-party-rater; quyền owner cho đúng scope. Thiếu chứng cứ thì `HOLD_ACCESS` | `NOT_VERIFIED · NOT_AUTHORIZED` |
| **Lawful limited read-only feasibility inspection** | Chỉ **sau** khi AD-01R và owner scope được xác nhận; kiểm `AD-02` typed entity/location/reference time, ontology/authority/temporal completeness, `AD-03` visible witness, `AD-05` cue/leakage, `X14` explicit exclusivity; `AD-06` nếu có causal matched pairs. **Không tự cấp phép qua tài liệu này** | `NOT_EXECUTED` |
| **Trước production authoring/gold** | Lawful feasibility evidence phải phù hợp; khóa prospective sampling frame, unit/candidate denominator, eligible/reject reason categories và coverage targets **trước chọn mẫu/theo outcome**, không bỏ item khó để làm đẹp độ chính xác (F-H01/X17). Không tác nghiệp cho đến khi có owner scope riêng | `NOT_ADMITTED` |
| **Trước fixture freeze** | `AD-01T` nếu token-sensitive, exact builder/tokenizer/window/truncation, `X13` full label-changing material-fact parity giữa model-effective/rater-effective views, `X15` lưu mọi reject reasons + precedence deterministic, `AD-07` endpoint/sample/threshold/STOP và hiệu lực trước khi lựa chọn chịu ảnh hưởng bởi chúng | `NOT_FROZEN · NOT_CAPTURED` |
| **Trước scoring** | `AD-04` same-task independent blind gold/rater, source-grounded truth/ontology counter-adjudication, calibration/abstention, no hidden key; AD-03/05/06 recheck | `NOT_CALIBRATED` |
| **Trước inference/training** | `AD-00` source/runner pins, `AD-01C` checkpoint rights/byte custody, Q4 closure + **separate** owner science permit, budget, sealed TEST/FINAL policy | `NOT_AUTHORIZED` |

Với một phép đo yêu cầu bảo đảm từ nguồn cả về authoring và runtime, mỗi gate chỉ có thể nâng trạng thái bởi **chứng cứ riêng của gate đó**. Không có đường tắt từ Q2 source-only PASS sang nguồn, gold, scoring, GPU hoặc release.

## 3. Findings và hard veto được chuyển tiếp nguyên trạng

- **F-H01/X17:** eligibility-selection bias; phải đo và báo cáo cả mẫu số candidate lẫn tỷ lệ ELIGIBLE/REJECT theo reason, kiểm tra temporal/source completeness, prereg threshold. Không được bỏ mục khó sau khi biết đáp án.
- **F-M02/X18:** inter-rater agreement không chứng minh nhãn đúng khi cùng hiểu sai ontology; source-grounded independent adjudication và calibration là bắt buộc trước scoring.
- **F-M03:** witness xuất hiện trong hai view không đủ chứng minh hidden E_core chưa tham gia quá trình tạo gold; lineage/provenance và blind rederivation phải tách nguồn ẩn.
- **F-M04:** M3 causal contrast cần fact-only vs cue-only controls, group-disjoint matching/counterbalancing và AD-06 nếu tuyên bố nhân quả.
- **X19:** source completeness phải khớp reference-time domain; thiếu record không biến thành `UNKNOWN_VALID`.
- **X21/X15:** multi-reason REJECT giữ tất cả reason, chọn primary bằng precedence prereg trước freeze; truncation làm mất decisive witness => gate HOLD và item REJECT, không UNKNOWN.
- **AD-01R/01T/01C, AD-02/03/04/05/06/07:** trạng thái của từng gate vẫn HOLD/NOT_VERIFIED/NOT_EXECUTED đúng pha; không có item/gold/scorer/runner được tạo bởi clarification.

## 4. Trạng thái quyết định

`Q1_REGISTERED · Q2_ACCEPTED_SOURCE_ONLY · Q3_NOT_EXECUTED · Q4_NOT_DECIDED · SCIENCE_HOLD · F0_F2_PAUSED · LINEAGE_UNCHANGED`.

**Lượt tiếp theo — duy nhất (không tự động cấp phép):** `TTM_P0A_MEAS_Q3_SOURCE_EVIDENCE_ANSWER_AND_DISTINCT_QA_SINGLE_GATE`. Kiểm toán những điều kiện còn thiếu bằng nguồn hiện hữu được phép; nếu evidence không đủ, báo `HOLD_EVIDENCE_INSUFFICIENT` để owner phân xử tại Q4, không tự tạo dataset, gold hoặc gọi mô hình.
