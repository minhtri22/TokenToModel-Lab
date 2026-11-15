# TTM-Small-4M — SM4M-F0→F4: Root-Cause Research Roadmap

**Operation:** TTM_SMALL4M_FOUNDATION_FIRST_COMPONENT_SPEC_AND_ROOT_CAUSE_RESEARCH_REBASE_SINGLE_GATE  
**Ngày:** 2026-11-15 · **Bản đồ duy nhất** · DESIGN ONLY; không tạo thêm research phase, mã nguồn runner, dữ liệu, job hay permit.  
**Source baseline:** main `fbe4a1ed58eef66f896bbfe0471926b7cc45298e`. Liên kết nguồn ở tài liệu F0/F1 cùng thư mục.  
**Quy tắc:** F0 và F1 là hoạt động tài liệu trong gate này; F2 mới chỉ chọn *thiết kế*; F3/F4 là điều kiện tương lai, **NOT_OPENED**. Không tự suy rằng GO_DESIGN = GO_SCIENCE.

## 1. Câu hỏi khoa học xuyên suốt

Tại sao checkpoint T4 3,749,376 tham số cải thiện VAL next-token NLL 11.88% so với bigram, nhưng các bộ đánh giá fact/prompt chưa chứng minh hành vi giữ đúng actor, object, causal relation và goal?

Phải tách ít nhất ba lớp: (a) phép đo có phân biệt đúng/sai không, (b) phân phối xác suất token đã phản ánh dữ kiện hay chưa, (c) cơ chế sinh tự hồi quy có biểu đạt đúng năng lực không. Không khởi đầu từ câu trả lời mặc định “thiếu attention”, “thiếu tham số”, hay “cần train thêm”.

## 2. Lộ trình giữ nguyên F0–F4 do owner giao

| Gate | Mục tiêu/phạm vi | Đầu ra | Tình trạng gate này | Điều kiện chuyển (không tự cho phép) |
|---|---|---|---|---|
| **SM4M-F0** | Kiểm toán tokenizer, embeddings, position, attention, FFN, LayerNorm, residual, tied head, loss, AdamW, decoding | `01_SMALL4M_ARCHITECTURE_COMPONENT_SPEC_20261115.md` | `AUTHOR_SOURCE_INSPECTION_SCOPED` | Independent source review và đối chiếu private pins khi cần; không ghi checkpoint byte PASS mới |
| **SM4M-F1** | Phân loại PASS/FAIL/HOLD hiện hữu và bản đồ giả thuyết cạnh tranh | `02_SMALL4M_EVIDENCE_FAILURE_ROOT_CAUSE_MATRIX_20261115.md` | `AUTHOR_EVIDENCE_SYNTHESIS`, cause unproven | Reviewer độc lập xác nhận đúng source/counterclaims; owner quyết định chọn F2 |
| **SM4M-F2** | Thiết kế phép đo có khả năng phân biệt nguyên nhân | Giao thức dự kiến M0 measurement calibration bên dưới | `DESIGN_CANDIDATE_ONLY`, **NOT_EXECUTED** | Không được chạy nếu chưa kiểm định source/data/rights/custody, blind raters và owner GO một gói |
| **SM4M-F3** | Tối ưu **một** thành phần đã chứng minh là nút thắt | A/B cùng checkpoint/data/eval/budget phù hợp; prereg ký trước outcome | **NOT_OPENED** | Chỉ sau kết quả F2 phù hợp; cấm mở data/objective/attention cùng lúc |
| **SM4M-F4** | Phân xử KEEP/HOLD/STOP, bảo toàn lineage | Scoring, independent readback, owner decision, closure | **NOT_OPENED** | Phân xử theo threshold đã khóa, không micro-permits hoặc hậu nghiệm cứu ngưỡng |

## 3. SM4M-F2 — Một giả thuyết ưu tiên, một phép thử phân biệt

**Hypothesis H-MEAS:** số điểm semantic retention bằng 0 trên nhiều đầu ra có thể phản ánh *mô hình thật sự sai* hoặc *hệ chấm không đủ nhạy với bằng chứng đúng*. Đây là hai giải thích cạnh tranh. Chưa thể tối ưu kiến trúc dựa trên các điểm 0 nếu không đo độ nhạy/đặc hiệu của evaluator.

**Phép thử kế thừa đã được thiết kế trước trong [H-DATA FAIL4 MD1](https://github.com/minhtri22/TokenToModel-Lab/blob/research/ttm-hdata-s1-fail4-prospective-mechanism-design-20261114/docs/research/ttm-hdata-fail4-md1/TTM_HDATA_FAIL4_MD1_PROSPECTIVE_PREREG_AND_FOUR_FAIL_MECHANISM_PLAN_20261114.md): M0 calibration.** Đây là lựa chọn *từ thiết kế sẵn có*, không sáng lập một nghiên cứu thứ hai hoặc cấp execution permission trong tài liệu này.

- **Thiết kế dự kiến:** 32 lõi truyện positive/negative mới (4 strata × 8), mỗi lõi có một continuation đúng cả ba trục actor/object/goal và một continuation cố ý sai cả ba; tổng 64 đoạn chỉ để kiểm chuẩn rater, **không** dùng làm model FINAL.
- **Đối chứng tối thiểu:** positive gold vs negative gold được khóa trước; two-blind-independent-rater; hạn chế bias bằng thứ tự/nhãn opaque; source rights và core nonoverlap phải được chứng minh. Không lấy đoạn từ TEST/FINAL đã dùng.
- **Các ngưỡng *đã có trong MD1***: cho **mỗi** rater và **mỗi** trục, sensitivity ≥28/32 và specificity ≥28/32; giữa hai rater agreement ≥0.85 trên mỗi trục.
- **Diễn giải nếu đạt**: thước đo nhận biết được đúng/sai trên đối chứng *rõ ràng*; không chứng minh thước đo tương đương human gold hay đủ độ tin cậy trên văn bản khó. Khi đó có thể đề xuất chẩn đoán H-COND/H-DATA/H-OBJ trên dữ liệu mới, nhưng **không tự chạy**.
- **Diễn giải nếu không đạt**: `HOLD_MEASUREMENT`; kiểm lại rubric/nhãn thiết kế theo prospective amendment, **không sửa** điểm từ H-DATA-S1, A/C hoặc FRESH16 và **không** train tiếp.
- **Ở gate hiện tại:** chưa sáng tác 32 core, chưa sinh 64 văn bản, chưa phân người chấm, chưa hash dữ liệu, chưa chấm và chưa chạy model. `M0=DESIGN_ONLY / SCIENCE_NOT_EXECUTED`.

**Tại sao M0 ưu tiên hơn đổi objective?** A/C và H-DATA-S1 có điểm 0 trùng nhau, trong khi FC01 có tín hiệu trên objective ở benchmark template. Measurement validity là điều kiện tiên quyết để phân biệt “objective không có tác dụng” với “endpoint không phản ánh năng lực”. Điều này không khẳng định measurement là lỗi đã tìm ra.

## 4. Nếu F2 qua gate: thứ tự chẩn đoán tiếp theo, không mở ở lượt này

Đúng theo thiết kế MD1 hiện có:
- **M1 — Absolute generation floor:** xác định cả hai checkpoint H0/H1 có thật sự ở sàn khi câu chuyện/mục tiêu dễ, trên lõi mới, không dùng FINAL24 cũ.
- **M2 — Context và goal accessibility:** đối chứng SHORT vs DISTRACTOR, EXPLICIT vs IMPLICIT trên cùng lõi; split theo core, không theo biến thể; đánh giá chống shortcut, stable lexical control.
- **M3 — Representation vs generation:** teacher-forced oracle/foil (length-matched, frozen *before* model) đối chiếu greedy generation. Nếu oracle > foil nhưng greedy tệ, chỉ nêu ứng viên generation-selection gap; nếu cả hai yếu, ưu tiên conditioning/objective/capacity. Chưa chấm cause.
- Không gọi các bước M1–M3 là task mới hay “đã GO”. Chỉ là các điều kiện tiếp nối đã ghi trong MD1, chưa có permit.

## 5. F3 — Cách chọn đúng một thành phần để tối ưu (chỉ phương pháp)

**Decision logic**, không phải lệnh thực thi:

| Kết quả chẩn đoán hợp lệ | Thành phần **được xem xét** | Đối chứng tối thiểu | Điều không được suy |
|---|---|---|---|
| Evaluator FAIL M0 | Measurement/rubric/gold | Independent labeled positive/negative | Không đánh FAIL mô hình |
| Evaluator PASS, teacher-forced fact split yếu | Data coverage **hoặc** training objective (lựa chọn một trước) | Same model, same tokenizer, same update/label budget, new DEV & sealed evaluation, anti-shortcut baseline | Không tự gọi attention/capacity là nguyên nhân |
| Teacher-forced strong, greedy poor | Decoding / autoregressive drift | Same checkpoint, identical prompt, controlled decoding variants | Không train lại để “cứu” endpoint |
| SHORT tốt, DISTRACTOR tệ | Context access / attention candidate | Matched content, positional length and cue control, multi-family independent test | Không kết luận sửa số head sẽ giải quyết |
| Mọi điều kiện tốt nhưng ability vẫn nghẽn, objective/data controlled | Capacity *candidate only* | Matched data/objective/fair training compute và seed budget | Không mở scaling/MoE theo mặc định |

Mỗi tối ưu hóa F3 tương lai phải có `StudyID, prereg hypothesis, intervention, one-primary-endpoint, anti-shortcut baseline, independent gold, data/license/PII admission, tokenizer_sha, input checkpoint_sha, seeds, exact optimizer budget, objective, checkpoint output policy, adjudication thresholds, abort/stop rule`; đăng ký trước outcome. Không thay hai cơ chế cùng lúc để mất định danh nhân quả. Nếu checkpoint thay đổi, đó là thí nghiệm mới; không gọi là thay đổi source thuần túy.

## 6. F4 — Quy tắc đóng và quyết định

- `PASS_SCOPED`: chỉ khi primary, negative controls, source custody, rights, independent QA đạt theo hợp đồng đã khóa, kèm effect size/CI, không coi synthetic QA là science.
- `FAIL_SCOPED`: khi không đạt primary/negative control; bảo toàn kết quả âm tính và tránh lặp lại cùng FINAL, seed, checkpoint với ngưỡng chỉnh hậu nghiệm.
- `HOLD`: khi nguồn/rights, parser, rater, independent QA, custody hoặc sample size chưa hợp lệ; không biến HOLD thành FAIL mô hình.
- `STOP_VARIANT`: đóng biến thể đã FAIL mà không có giả thuyết cơ chế mới. `PAUSE_PORTFOLIO`: đóng băng các nghiên cứu khác theo quyết định phạm vi, không xóa kết quả.
- Quyết định mỗi lượt chỉ một `GO/HOLD/STOP` của owner, không chia micro-permit. `lineage.md` append-only khi có closure hợp lệ; không merge nhánh FAIL như merge code mà chỉ ghi evidence/link trong lineage.

## 7. Phán quyết duy nhất của gói Foundation First

`F0=DOCUMENTED_SOURCE_SCOPED`; `F1=EVIDENCE_MAPPED_NO_CAUSAL_ATTRIBUTION`; `F2=ONE_MEASUREMENT_DISCRIMINATOR_DESIGN_ONLY`; `F3=NOT_OPENED`; `F4=NOT_OPENED`; `INDEPENDENT_GATE_REVIEW=PENDING`; `GPU=0`; `MODEL_FORWARD=0`; `TRAIN=0`; `TEST/FINAL=UNTOUCHED`; `OWNER_SCIENCE_GO=NOT_REQUESTED/NOT_GRANTED`.

**Một bước tiếp theo (không phải science dispatch):** independent SOURCE-ONLY review **cùng bốn tài liệu** của operation hiện tại về đối chiếu pins, tính chính xác thành phần, mọi PASS/FAIL/HOLD, logic M0 và tính cách ly, rồi owner adjudication design GO/HOLD. Không mở thêm phase hoặc nghiên cứu.
