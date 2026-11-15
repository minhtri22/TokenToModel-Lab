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
| **SM4M-F0** | Kiểm toán tokenizer, embeddings, position, attention, FFN, LayerNorm, residual, tied head, loss, AdamW, decoding | `01_SMALL4M_ARCHITECTURE_COMPONENT_SPEC_20261115.md` | `INDEPENDENT_PASS_SOURCE_SCOPED` (review 15/11, không reverify private checkpoint) | Đã có source QA độc lập có phạm vi; không ghi checkpoint byte PASS mới |
| **SM4M-F1** | Phân loại PASS/FAIL/HOLD hiện hữu và bản đồ giả thuyết cạnh tranh | `02_SMALL4M_EVIDENCE_FAILURE_ROOT_CAUSE_MATRIX_20261115.md` | `INDEPENDENT_PASS_WITH_REMEDIATION` → `AUTHOR_F01_F05_REVISED`, re-review pending; cause unproven | Reviewer độc lập mới xác nhận sửa F01–F05 theo exact HEAD trước owner GO_DESIGN |
| **SM4M-F2** | Thiết kế phép đo có khả năng phân biệt nguyên nhân | M0 gốc giới hạn polarity + prospective per-axis design amendment ở mục 3 | `HOLD_M0_DISCRIMINATOR_DESIGN` → `AUTHOR_REMEDIATION_CANDIDATE`, **NOT_EXECUTED** | Independent design re-review F01/F04, gold, source/data/rights/custody, blind raters và owner GO một gói; **không** tự execution |
| **SM4M-F3** | Tối ưu **một** thành phần đã chứng minh là nút thắt | A/B cùng checkpoint/data/eval/budget phù hợp; prereg ký trước outcome | **NOT_OPENED** | Chỉ sau kết quả F2 phù hợp; cấm mở data/objective/attention cùng lúc |
| **SM4M-F4** | Phân xử KEEP/HOLD/STOP, bảo toàn lineage | Scoring, independent readback, owner decision, closure | **NOT_OPENED** | Phân xử theo threshold đã khóa, không micro-permits hoặc hậu nghiệm cứu ngưỡng |

## 3. SM4M-F2 — Sửa tích hợp F01/F02/F04: phạm vi M0, đối chứng và điều kiện admission

**Giả thuyết H-MEAS (measurement validity) vẫn `NOT_TESTED`.** Điểm 0 có thể phản ánh (a) đầu ra mô hình thật sự không giữ dữ kiện, (b) người chấm thiếu độ nhạy trong một số loại đầu ra, hoặc cả hai. Đây là các giả thuyết cạnh tranh; **không** có phép đo hiện tại nào chứng minh nguyên nhân duy nhất.

**Không gộp hai nghiên cứu khác phép đo (F02):**
- **A/C FINAL24:** adherence tuyệt đối A=0.6667/3 và C=0.6667/3; **Δ(C−A)=0**. Đây là `NO_INCREMENTAL_GAIN` của arm C, **không** phải absolute floor=0; không được suy từ hiệu số 0 ra mọi output đều 0.
- **H-DATA-S1 FINAL24:** 24 cặp × 2 arm = **48 continuations**. Cả 48 được chấm 0 trên ba trục actor/object/goal = **144/144 primary axis-level zeros**, trong 240 scores của năm trục; H0/H1 mean primary=0 và Δ=0. Đây là absolute-zero **theo protocol và rater H-DATA-S1**, chưa phân biệt được lỗi mô hình với rater.
- **FRESH16** S1/S2 chấm endpoint khác nhau, không có shared-item agreement; **FC01** có tín hiệu scoped trên lexical template nhưng không sửa được tính hợp lệ của endpoint H-DATA. **Không pooling** các thước đo và không thay evidence đã khóa.

### 3.1. M0 gốc MD1 — *polarity calibration*, không phải per-axis causal discriminator (F01)

Kế thừa đúng [MD1 design đã khóa](https://github.com/minhtri22/TokenToModel-Lab/blob/33021a421f05bb3bfa0999ad12bc3bd144366da9/docs/research/ttm-hdata-fail4-md1/TTM_HDATA_FAIL4_MD1_PROSPECTIVE_PREREG_AND_FOUR_FAIL_MECHANISM_PLAN_20261114.md), **không sửa MD1**:
- 32 lõi rõ ràng, 4 strata × 8 lõi; mỗi lõi một positive đúng cả actor/object/goal và một negative sai cả ba; tổng **64 văn bản kiểm chuẩn**. Hai independent blinded raters chấm cùng 64 records.
- Các ngưỡng MD1 **giữ nguyên**: với mỗi rater/trục, sensitivity ≥28/32 và specificity ≥28/32; giữa hai rater, agreement ≥0.85 trên mỗi trục. Không tạo dữ liệu, không chấm, không đổi threshold/gold ở gate này.
- **Vấn đề định danh:** vector gold trên 64 cases chỉ có `111` hoặc `000`, ba trục đổi cùng nhau. Một rater chấm `111` cho mọi continuation có vẻ tốt và `000` cho mọi continuation có vẻ xấu vẫn có thể vượt ngưỡng trên cả ba trục. Do đó **M0 PASS chỉ được gọi `CALIBRATION_CLEAR_POLARITY_SCOPED_PASS`**, không phải `PER_AXIS_VALIDITY_PASS`, `MODEL_ERROR_PROVEN` hoặc `ROOT_CAUSE_FOUND`. Kể cả khi rater đạt agreement, hai người có thể cùng dùng shortcut.
- **M0 FAIL** → `HOLD_MEASUREMENT`; không chấm lại lịch sử hay tăng huấn luyện. **M0 PASS** → chỉ mở khả năng *xin xét* prospective per-axis/partial/uncertain controls, **không tự M1/M2/M3 execution**.

### 3.2. Prospective amendment *bên trong F2* — phương pháp phá shortcut, chưa phát hành dữ liệu

Đây là **thiết kế sửa đổi để giải quyết HIGH F01**, không phải tạo nghiên cứu khác hay ngầm thay bộ M0 cũ. Trước bất kỳ lần thực thi nào, cần một amendment có độc lập source/design QA và owner quyết định tổng hợp:

1. **Đối chứng riêng từng trục (axis-isolating):** trong *cùng lõi* và cùng fact background, thay một trục actor **hoặc** object **hoặc** goal, giữ hai trục kia đúng. Ít nhất phải có các mẫu gold hỗn hợp `011`, `101`, `110` so với `111`, đồng thời có tổ hợp `100`, `010`, `001` và `000` để tránh dùng valence toàn cục; đề xuất cân bằng đầy đủ **2³=8 patterns**. `1` là đúng theo gold của trục tương ứng, `0` là sai. Không cấp quyền viết các lõi/văn bản này trong gate.
2. **Đáp án đúng một phần, không đủ bằng chứng, mơ hồ:** các continuation tự nhiên với một hay hai trục đúng, missing information và uncertainty được kiểm thử dưới nhãn `UNSCORABLE` hoặc gold đặc thù được khóa *trước* khi chấm. Không ép thiếu thông tin thành điểm 0 nếu rubric không định nghĩa.
3. **Anti-shortcut và construct validity:** hoán đổi actor/object/goal names, đáp án và thứ tự; cân bằng dấu hiệu từ vựng, độ dài, mức lưu loát, độ phủ template và vị trí correct/incorrect; positive và negative cùng mức dễ đọc; kiểm một proxy/rule chỉ nhìn style, label hoặc category **không** đạt ngưỡng mục tiêu. Phải độc lập review gold và trường hợp không thực sự thao tác riêng một trục.
4. **Cơ chế kiểm rõ ràng:** amendment bắt buộc khóa **số lõi, số item, phân bổ 8 patterns, target axis, phương pháp gold, đồng thuận trên partial/uncertain, ngưỡng riêng trục, tiêu chí đối chứng negative và stop rule** trước khi tạo dữ liệu hay thu điểm. Tài liệu hiện tại chỉ đặt **điều kiện thiết kế**; **không tự thêm threshold** hoặc sửa 28/32 và 0.85 của M0 gốc. Nếu chưa khóa những điều này, `F2_PREEXEC=BLOCK` kể cả M0 cũ PASS.
5. **Phân biệt model vs rater:** đối chứng human-authored rõ và các ví dụ partial/ambiguous đánh giá *giới hạn độ nhạy của rubric*. Chỉ nếu measurement qualification hợp lệ mới xem xét generation/teacher-forced trên **dữ liệu mới**, theo hợp đồng riêng trong F2; không được từ rater calibration trên văn bản rõ suy ngược lại rằng model đã FAIL hoặc rater đã FAIL ở FINAL cũ. Nếu gold chỉ do AI chấm, ghi `EXPLORATORY_AI_GOLD`, không mạo nhận human attestation.

### 3.3. Hợp đồng điểm/custody bắt buộc trước F2 execution (F04)

**Chỉ là quy tắc dự kiến cần được reviewer ký duyệt**, chưa phải receipt thực thi:

- **Original M0 per-rater per-axis** trên cùng tập 64 item ID: 32 gold-positive và 32 gold-negative trên mỗi trục. `TP+FN=32`, `TN+FP=32`; `sensitivity=TP/(TP+FN)=TP/32`, `specificity=TN/(TN+FP)=TN/32`. Mỗi rater xuất **3 confusion matrices**, mỗi matrix có TP,FN,TN,FP nguyên, tổng 64. Ngưỡng MD1 không đổi: `TP>=28`, `TN>=28` cho mỗi trục/rater.
- **Agreement gốc (raw exact match)** trên 64 item IDs tương ứng **cho mỗi trục**: `A_axis=(số items có rater1==rater2)/64`; `A_axis>=0.85` tương đương **≥55/64**; không dùng Cohen kappa thay cho công thức này mà không có amendment phê duyệt. Cặp rater phải chấm **đúng cùng 64 items**, không chỉ cùng kích thước mẫu. Đây là đề xuất đóng băng công thức theo ngưỡng MD1, **không tuyên bố MD1 đã ghi rõ công thức**.
- **Missing / invalid / duplicate / misbound IDs:** `HOLD_INPUT_INTEGRITY`, không drop item, đổi denominator, ấn định điểm 0 hay tái lập score hậu nghiệm. Mọi rater-scored packet phải có blinded opaque IDs, per-axis score, score receipt SHA, freeze before unblind; không công bố owner-private plaintext.
- **Gold & independence:** provenance/rights/PII, independent gold review và adjudication trước chấm, balanced blind permutation, randomization commitment, custody of two raters độc lập và kiểm leak. Nếu chỉ AI, ghi `EXPLORATORY_SCOPED_AI_REVIEW`; không gọi consensus human gold.
- **Partial/ambiguous extension:** mọi quy tắc tính per-axis agreement, specificity/sensitivity, denominator và invalid handling phải **được khóa riêng** cho prospective amendment *trước* thực thi. Không sử dụng ngưỡng 28/32 và mẫu số 64 của M0 cũ để đánh giá một tập item mới với nhãn hỗn hợp.
- **Admission trước tất cả:** `SOURCE_QA`, `DATA_GOLD_RIGHTS_PII`, `ANTI_SHORTCUT`, `BLIND_RATER_CUSTODY`, `FROZEN_SCORING_CONTRACT`, `NONOVERLAP`, `OWNER_GO` phải được phân xử *một gói*, không chia micro-permit. Dữ liệu chưa được sáng tác/khóa; `M0_EXECUTION=NOT_AUTHORIZED`.

**Gate F2 hiện tại:** `HOLD_M0_DISCRIMINATOR_DESIGN` theo reviewer gốc, `AUTHOR_F01_F05_REMEDIATION_CANDIDATE` sau sửa, `REREVIEW_PENDING`, `SCIENTIFIC_ROOT_CAUSE=NOT_IDENTIFIED`.

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
| Measurement được thẩm định đúng phạm vi **và** per-axis controls đã được admission; teacher-forced fact split yếu | Data coverage **hoặc** training objective (lựa chọn một trước) | Same model, same tokenizer, same update/label budget, new DEV & sealed evaluation, anti-shortcut baseline | Không tự gọi attention/capacity là nguyên nhân |
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

## 7. Trạng thái một gói remediation tích hợp F01–F05

**Nhận từ independent reviewer:** `HOLD_REVISE_DESIGN` (hai HIGH: F01, F02; hai MEDIUM: F03, F04; một LOW: F05). Đây là *phán quyết bất biến của review tại candidate 4c97f2b1*, không được tác giả tự đổi thành GO.

**Đã chỉnh ở author documentation trong cùng operation:**
- **F01:** M0 gốc chỉ polarity, thiết kế axis-specific/partial/uncertain anti-shortcut ở mục 3.2, prospective amendment pending; không thay MD1.
- **F02:** A/C absolute 0.6667, delta=0, không giống H-DATA absolute-zero; cấm pooling.
- **F03:** 48 continuations, 144 primary axis-scores trong tổng 240 scores.
- **F04:** công thức 3 confusion matrices / rater, agreement matches/64 ≥0.85, missing fail closed; final execution contract pending independent signoff.
- **F05:** FRESH16 S1/S2 chấm hai endpoint khác nhau, không có shared-item reliability, đã sửa ở F1.

**Khóa trạng thái:** `F0=INDEPENDENT_PASS_SOURCE_SCOPED`; `F1=AUTHOR_REMEDIATED_REREVIEW_PENDING`; `F2=DESIGN_ONLY_HOLD_NEW_EXECUTION`; `F3=NOT_OPENED`; `F4=NOT_OPENED`; `INDEPENDENT_REMEDIATION_QA=PENDING`; `GPU=0`; `MODEL_FORWARD=0`; `TRAIN=0`; `TEST/FINAL=UNTOUCHED`; `OWNER_SCIENCE_GO=NOT_GRANTED`; `MERGE=NOT_AUTHORIZED`.

**Bước thực hiện tiếp theo — duy nhất:** distinct independent **SOURCE/DESIGN-ONLY re-review đúng gói F01–F05** trên exact remediation commit của F1 + roadmap; kiểm tra cả F0/scope unchanged. Reviewer trả **một** verdict `GO_DESIGN_SCOPED` hoặc `HOLD_REVISE_DESIGN`, sau đó owner ra một quyết định. Không thực thi M0 hoặc model, không mở phase, không merge.

