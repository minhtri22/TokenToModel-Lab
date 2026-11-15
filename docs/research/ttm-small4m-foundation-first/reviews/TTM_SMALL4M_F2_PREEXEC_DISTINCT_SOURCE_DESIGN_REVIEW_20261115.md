# TTM-Small-4M — Independent SM4M-F2 Prospective Measurement Design Audit

**Ngày:** 2026-11-15  
**Operation:** `TTM_SMALL4M_F2_PROSPECTIVE_MEASUREMENT_PREEXEC_DISTINCT_SOURCE_DESIGN_REVIEW_SINGLE_GATE`  
**Vai trò:** Independent AI Scientific, Source & Measurement Reviewer (không phải human gold attestor)  
**Chế độ:** `READ_ONLY · SOURCE_ONLY · DESIGN_ONLY · NO_SCIENCE_EXECUTION · NO_REPOSITORY_WRITES`  
**Repository:** `minhtri22/TokenToModel-Lab`  
**Exact candidate:** `07adab6262e50b5e17c6ea816bb133866e0a11d2`  
**Baseline:** `c233dff20b9b020aefd732ce62bfa2e7aebd3985`  
**FINAL_DECISION:** **`HOLD_REVISE_DESIGN`**  
**Phạm vi phán quyết:** chỉ về khả năng diễn giải và tính nhất quán của thiết kế F2; không phủ định các closure thiết kế trước, không đánh FAIL mô hình, không phát hành quyền chạy.

## 1. Phương pháp và xác minh exact source

Đã đọc qua GitHub connector tại **exact commit** (không dùng HEAD động) toàn bộ tài liệu 06, 07, 08 và author receipt JSON; đọc nguyên bản MD1 ở commit gốc, Foundation First F0–F4 roadmap và owner closure ở baseline. `compare_commits` từ baseline đến candidate cho kết quả `ahead_by=1`, `behind_by=0`, `total_commits=1`, đúng **4 tệp added; 0 modified; 0 deleted**. Không có thay đổi `lineage.md`, checkpoint, dữ liệu, mã nguồn hoặc tệp `main` trong diff này. Lệnh đọc không thay đổi repository.

| File hoặc nguồn | Commit pin | Git blob SHA-1 đọc trực tiếp | So với handoff |
|---|---|---|---|
| [06 — Integrated protocol](https://github.com/minhtri22/TokenToModel-Lab/blob/07adab6262e50b5e17c6ea816bb133866e0a11d2/docs/research/ttm-small4m-foundation-first/06_SM4M_F2_PROSPECTIVE_MEASUREMENT_PREEXEC_INTEGRATED_PROTOCOL_20261115.md) | `07adab62…` | `cbf3641a9991e81349058e06564b49a84c7525e1` | PASS |
| [07 — Admission/scoring/custody matrix](https://github.com/minhtri22/TokenToModel-Lab/blob/07adab6262e50b5e17c6ea816bb133866e0a11d2/docs/research/ttm-small4m-foundation-first/07_SM4M_F2_PREEXEC_ADMISSION_SCORING_AND_CUSTODY_MATRIX_20261115.md) | `07adab62…` | `fca4d946b51b50212f5888d513d84d887466c472` | PASS |
| [08 — Author handoff](https://github.com/minhtri22/TokenToModel-Lab/blob/07adab6262e50b5e17c6ea816bb133866e0a11d2/docs/research/ttm-small4m-foundation-first/08_SM4M_F2_DISTINCT_INDEPENDENT_SOURCE_DESIGN_REVIEW_HANDOFF_20261115.md) | `07adab62…` | `f07a9bd22bc45ee4518fe0a346c08e4d8ef49f4d` | PASS |
| [Author receipt JSON](https://github.com/minhtri22/TokenToModel-Lab/blob/07adab6262e50b5e17c6ea816bb133866e0a11d2/artifacts/research/ttm-small4m-foundation-first/TTM_SMALL4M_F2_PREEXEC_DESIGN_AUTHOR_RECEIPT_20261115.json) | `07adab62…` | `237aa4dc3af77d35a191424fcfcd4da7d735717f` | PASS |
| [MD1 original](https://github.com/minhtri22/TokenToModel-Lab/blob/33021a421f05bb3bfa0999ad12bc3bd144366da9/docs/research/ttm-hdata-fail4-md1/TTM_HDATA_FAIL4_MD1_PROSPECTIVE_PREREG_AND_FOUR_FAIL_MECHANISM_PLAN_20261114.md) | `33021a42…` | `384d077600ed864a917fdd5e74b5a5bca0ed8766` | PASS |
| [F0–F4 roadmap](https://github.com/minhtri22/TokenToModel-Lab/blob/c233dff20b9b020aefd732ce62bfa2e7aebd3985/docs/research/ttm-small4m-foundation-first/03_SMALL4M_ROOT_CAUSE_RESEARCH_ROADMAP_F0_F4_20261115.md) | `c233dff2…` | `d87309aea043b845fafcc805ed13b2b4466f5e46` | PASS |
| [Owner closure F01–F05](https://github.com/minhtri22/TokenToModel-Lab/blob/c233dff20b9b020aefd732ce62bfa2e7aebd3985/docs/research/ttm-small4m-foundation-first/05_SMALL4M_F01_F05_OWNER_INTEGRATED_DESIGN_ADJUDICATION_20261115.md) | `c233dff2…` | `3fee9e58914de4c6f41851ca6f7ce89d6bf67124` | PASS |

Author receipt: nội dung là JSON parse hợp lệ; 13/13 kiểm tra cấu trúc/số học/trạng thái đã thực hiện với kết quả PASS: các tổ hợp 32/64, 16×8/128, 24/24, tổng 72 cores/216 items/432 rater assignments/1.296 axis decisions; 13 gate entries; owner GO, GPU, inference, training và scoring đều `false`. Đây là **source-consistency check**, không phải xác nhận các receipt quyền, gold, private custody hay khoa học đã tồn tại. Chưa kiểm chứng riêng author owner-receipt blob `de624cea…` vì ngoài các source bắt buộc đã đọc; không tự nâng tình trạng đó thành VERIFIED. Không tính SHA-256 của nội dung GitHub từ đường dẫn/metadata.

## 2. Đối chiếu MD1 bất biến và lịch sử khoa học

**M0 original:** đúng 32 story cores = 4 strata ×8; 64 continuations =32 `111` +32 `000`; hai blind raters chấm cùng IDs; mỗi trục và mỗi rater có sensitivity `TP/32 ≥28/32`, specificity `TN/32 ≥28/32`; agreement mỗi trục ≥0,85. Đề nghị diễn giải raw exact agreement thành `matches/64 ≥55/64` là **hợp đồng mới cần phê duyệt**, không ghi ngược vào MD1. M0 chỉ đo phân biệt **cực tính rõ** (clear polarity): cùng một bộ `111/000` không định danh được năng lực cô lập actor, object hoặc goal. Phần này **đạt kiểm toán thiết kế, không phải measurement PASS thực nghiệm**.

Owner closure tại `c233dff…` chấp nhận `GO_DESIGN_SCOPED` đóng F01–F05 cũ đúng phạm vi, không cung cấp owner science GO. MD1 M1–M3 và Foundation First F3/F4 vẫn ngoài phạm vi.

Không gộp hay đảo các kết quả lịch sử: T4 VAL/TEST64 giữ nguyên adjudication theo scope; FRESH16 vẫn FAIL theo prereg; A/C FINAL24 mean A=C=0,6667/3, delta=0 **không** là absolute-zero; H-DATA-S1 có 48 continuations và 144 điểm zero ở ba trục chính theo rater/protocol cũ; không có bằng chứng incremental H1; FC01 chỉ exploratory PASS; D1 R1 design closure nhưng science HOLD. Các kết quả là bối cảnh nguồn, **không được chấm lại**.

## 3. Kiểm toán định lượng, mẫu số và đơn vị độc lập

| Bộ | Cores | Items | Đơn vị và giới hạn |
|---|---:|---:|---|
| M0 original | 32 | 64 | 32 clusters; chỉ patterns `111/000` |
| M0X proposed | 16 | 128 | 16 clusters ×8 variants; 8 patterns mỗi pattern 16; mỗi trục 64 pos/64 neg; 64 matched edges/trục (4/core) |
| M0U proposed | 24 | 24 | 24 cores; 8 targeted UNKNOWN mỗi trục; mỗi item hai trục còn lại binary |
| **Tổng có kế hoạch** | **72** | **216** | 432 item-rater assignments ×3 = **1.296 axis decisions**, không phải 1.296 quan sát độc lập |

- **M0X factorial 2³:** cân bằng *marginal* và *joint* theo nhãn là hợp lý về đại số. Nhưng `2³` bảo đảm các bit được liệt kê, **không bảo đảm can thiệp vào một bit không đổi truth conditions của hai bit khác**. Ví dụ quan hệ object custody và khả năng hoàn thành goal có thể phụ thuộc actor. Các cặp edge dùng chung endpoint, nên 64 edge không iid và 128 items không iid; đơn vị chính để định lượng uncertainty là 16 core, chỉ 4/core/stratum.
- **M0X thresholds proposed:** 56/64 =87,5% sensitivity và specificity từng trục/rater; edge 56/64 =87,5%; agreement 109/128 ≈85,16%. Tỷ lệ sensitivity/specificity là phép chiếu từ M0, **không phải bằng chứng power**. Có thể mất trọn 2 core (8 edges) mà vẫn qua 56/64 trên một trục; không có bảo đảm mức stratum/core mặc dù có yêu cầu báo cáo. Agreement cao không cứu đồng thuận cùng shortcut.
- **M0U:** 7/8 =87,5% nhận diện UNKNOWN mỗi trục/rater; tám core mỗi trục có bất định lớn. Người chấm trả `UNKNOWN` cho **mọi** trục sẽ đạt 8/8 targeted UNKNOWN nhưng hoàn toàn không biết trục nào chấm được. Vì vậy targeted sensitivity một mình không phải cổng đánh giá đầy đủ; false abstention/non-target accuracy và false certainty phải được định nghĩa thành hợp đồng có mẫu số, not just named as future metrics.
- Cluster uncertainty cho M0X nên báo tách theo core/stratum và khoảng tin cậy mô tả, không trình bày item-iid CIs; không có cam kết power confirmatory hay khả năng ngoại suy lên văn bản do T4 sinh. Cần xác định trước nếu các ngưỡng mang nghĩa screening/exploratory hay claim confirmatory.

## 4. Kiểm toán tính tách biệt ngữ nghĩa và anti-shortcut

**Actor:** đổi tên/vai có thể đồng thời đổi người giữ vật hoặc chủ thể thực hiện mục tiêu. **Object:** đổi identity/custody có thể làm biến đổi thành công của mục tiêu. **Goal:** đổi goal có thể khiến một hành động trước đó từ đúng thành sai ở object/actor theo rubric. Vì thế, muốn có 8 variants từ cùng core phải thiết kế ba mệnh đề quan sát được và thử logic từng biến thể/12 edge mỗi core, không suy labels từ pattern ID. Quy tắc `HOLD_SEMANTIC_COUPLING` là tốt nhưng chưa có **điều kiện đủ để một core hợp lệ** hay chính sách khi một stratum không thể tạo 8 patterns. Đây là thiếu hụt thiết kế chứ không phải chỉ thiếu gold hiện tại.

Ba shortcut cần tách:

1. **Global valence/label:** factorial có khả năng phân biệt một người chấm luôn xuất `111` hoặc `000` khi bộ mixed patterns hợp lệ và nhãn không bị lộ, nhưng phải kiểm paired endpoints thực tế; không suy rằng matched edges tự động triệt shortcut.
2. **Surface-language:** tính đa dạng từ vựng, style, độ dài và template có thể tương quan với gold. Tài liệu hiện yêu cầu “một hoặc nhiều proxy” và sẽ freeze sau, nhưng không ấn định tập proxy, protocol học/chọn proxy, split theo core hoặc acceptance threshold. Một proxy yếu thất bại **không bác bỏ** các proxy mạnh chưa thử. Cần prespec negative controls có cùng điều kiện thông tin phi ngữ nghĩa, kiểm leakage trên core/strata mới, và tiêu chí fail-closed khi feature predicts pattern/axis.
3. **Gold-induced coupling:** nếu truth of A/O/G cùng suy ra một sự kiện, gold “độc lập” hình thức có thể không có ý nghĩa. Kiểm toán gold phải ghi lý do dựa trên story evidence cho từng trục, truth invariants của hai trục trên từng edge, tình huống loại core và quyết định độc lập, không chỉ reviewer xác nhận bit string.

Rủi ro **within-rater contamination**: cả 8 variants một core nằm trong bộ của mỗi rater; cho dù opaque/randomized, người chấm có thể nhận ra thay đổi và suy nhãn bằng so sánh toàn tập. Cần định nghĩa chế độ chấm từng item độc lập, phân tán thứ tự variant, chặn truy cập side-by-side / memory xuyên session hoặc công khai giới hạn nếu không thể chặn; cùng với đánh giá đối chứng phiên trình bày. Hai raters có thể đồng thuận shortcut; raw agreement không xác lập validity.

## 5. UNKNOWN, gold và scoring

`UNKNOWN` phải là **không đủ nguồn bằng chứng để xác định trục**, không phải sai, score missing hoặc người chấm lười trả lời. G05 đề xuất một trục UNKNOWN và hai trục có gold 0/1 là bước đi hợp lý nhưng cần rubric truth/evidence và quy trình phân xử độc lập: loại thiếu chứng cứ, chủ thể tham chiếu, thông tin trái nhau, thời điểm, rule access; ít nhất phải chứng minh với các nguồn cùng core rằng (i) target có từ hai cách diễn giải hợp lý không phân giải được, (ii) hai non-target trục vẫn kết luận độc lập được, và (iii) câu văn không tự tiết lộ “UNKNOWN”. Cần ma trận 3×3 hoặc 3-class reports rõ, targeted vs non-target confusion/coverage và false certainty/false abstention đủ định nghĩa.

Scoring hiện có nguyên tắc đúng: rater cùng opaque IDs; per-axis TP/TN/FP/FN; edge phải đúng hai endpoints **và** hai invariant axes; no drop/missing/duplicate/NaN; gold freeze trước score, rater responses freeze trước unblind, checker độc lập. Tuy nhiên chưa có code/spec chuẩn đủ cụ thể cho duplicate core/edge IDs, rater UNKNOWN ở M0X, unscorable trong M0, invalid score and denominator, stratum-specific decision và intra-core dependence. `G09=NOT_IMPLEMENTED` hiện được chặn đúng; không coi là scorer PASS.

Quyền dữ liệu, PII, nguồn original, nonoverlap exact+semantic, rater independence, gold reviewer, HMAC/AES và SHA commitment vẫn chỉ là **schema hoặc điều kiện tương lai**. Tuyệt đối không nhận AI-only gold là human-verified và không ghi private text, gold, keys, blind map lên GitHub.

## 6. Findings độc lập — lỗi thiết kế và các gate đang chặn

**Phân loại:** `DESIGN_DEFECT` cần sửa trước `GO_DESIGN_SCOPED`; `PREEXEC_PENDING` là điều kiện chưa đạt nhưng đã được chặn đúng, **không tự động là lỗi thiết kế**.

### SM4M-F2-IR-01 — HIGH · DESIGN_DEFECT · Admission deadlock

- **Exact source:** 07 §1, G02/G04/G05/G06/G10/G12 và aggregate rule; 06 §5/§8.
- **Observed evidence:** G04/G05 yêu cầu gold và items đã tạo, G02 yêu cầu nonoverlap trên 72 cores, G06 yêu cầu proxy performance, G10 yêu cầu SHA manifest khi byte tồn tại; G12 lại yêu cầu owner GO **trước bất kỳ data creation**, còn aggregate bắt G00–G12 PASS trước khi hết `PREEXEC_BLOCK`.
- **Expected contract:** có thứ tự khả thi giữa freeze thiết kế, quyền tạo mẫu riêng tư, QA hậu tạo mẫu, quyết định cho phép rater/score; không mở execution trước bằng chứng và không cấp micro-permits.
- **Discrepancy:** tiền đề lô-gic vòng tròn; không thể đồng thời đạt các gate cần hiện vật và cấm tạo mọi hiện vật tới lúc tất cả gate đạt.
- **Scientific impact:** quy trình không thể thực thi nhất quán; dễ bỏ qua gate hay tự diễn giải owner GO.
- **Required remediation:** vẽ một **conditional integrated owner authorization** với các trạng thái và guard rõ (protocol freeze → quyền tạo data *giới hạn* → independent gold/rights/anti-shortcut QA → pre-score release/stop), khai báo rõ gate nào prespec, gate nào chỉ có evidence sau data, quyền nào KHÔNG được phép trước release. Không cấp quyền đó trong review này.
- **Gate affected:** G02, G04–G06, G10, G12.
- **Closure condition:** một state machine/timeline không mâu thuẫn, gắn từng gate với đầu vào, bằng chứng, actor/custodian, điều kiện dừng và quyền owner; independent review PASS_SOURCE_ONLY.

### SM4M-F2-IR-02 — HIGH · DESIGN_DEFECT · Semantic independence unspecified

- **Exact source:** 06 §3; 07 G04, `item_manifest` schema; roadmap §3.2.
- **Observed evidence:** có đủ `000..111` và 64 edge/axis nhưng chưa có operation-level definition cho các truth predicates, invariants và core feasibility; từ chối semantic coupling chỉ là hậu kiểm.
- **Expected contract:** mỗi core có mô hình fact cố định và 3 mệnh đề gold phân tách được theo 12 edges (4 edge ×3 axes), không thay hai trục bất biến khi thay một.
- **Discrepancy:** chỉ cân bằng bit, chưa bảo đảm tồn tại 8 trường hợp hợp lệ ở mọi stratum; thiếu tiêu chí fail/replacement được khóa **trước** biết score.
- **Scientific impact:** matched contrast có thể thay nhiều semantics cùng lúc → không phân biệt được năng lực rater theo axis.
- **Required remediation:** thêm predicate/evidence rubric, counterfactual-invariance checklist cho 12 edges/core, quy tắc invalid-core trước chấm, tính khả thi theo bốn strata và stopping/recruitment policy không lựa chọn hậu nghiệm; cần independent gold adjudication. Không tạo core trong review.
- **Gate affected:** G04, G05, G06, G07.
- **Closure condition:** protocol nguồn mô tả tiêu chí pass/fail có thể áp dụng nhất quán bởi independent reviewer, không dựa vào pattern label tự khai.

### SM4M-F2-IR-03 — HIGH · DESIGN_DEFECT · Anti-shortcut negative controls underspecified

- **Exact source:** 06 §3, “Anti-shortcut gates”; 07 G06, §4.
- **Observed evidence:** proxy classes và `HOLD_SHORTCUT` có nêu, nhưng số lượng proxy, feature exposure, training/tuning budget, core-level validation, prereg negative-control decision logic chưa có.
- **Expected contract:** đối chứng được định nghĩa trước, đủ mạnh để thử shortcut lexicon/length/style/order/template và gold/stratum confounding; không chọn proxy sau khi thấy rater score.
- **Discrepancy:** “một hoặc nhiều proxy không đạt threshold” chưa chứng minh chống shortcut khi proxy quá yếu hoặc cue leak qua core/style.
- **Scientific impact:** rater có thể qua M0X bằng cue mà không hiểu actor/object/goal.
- **Required remediation:** khóa danh mục proxy/cue extractors và allowed information; split group-disjoint theo core/author/template khi đủ dữ liệu; predefine threshold và failure trigger cho **mọi** đối chứng; audit balance/leakage ở cấp trục, pattern, stratum; phân biệt test power giới hạn và statement scope.
- **Gate affected:** G04, G06, G07, G09.
- **Closure condition:** negative-control protocol versioned có objective outputs và tiêu chí FAIL/HOLD không thể điều chỉnh hậu nghiệm.

### SM4M-F2-IR-04 — HIGH · DESIGN_DEFECT · UNKNOWN construct not operationally identifiable

- **Exact source:** 06 §4/§6; 07 G05/G07/G09.
- **Observed evidence:** 24 items, 8 target UNKNOWN/axis và 7/8 abstention; non-target binary accuracy/false certainty nêu là `TO_BE_FROZEN`, không có explicit evidentiary/epistemic rule hay phân loại conflict vs absent information.
- **Expected contract:** có nguồn fact/evidence đủ chứng minh target không phân giải được nhưng hai trục kia phân giải được; score 3-class với denom, false abstention và false certainty khóa prospective.
- **Discrepancy:** target UNKNOWN recall riêng có thể đạt 8/8 với chiến thuật `UNKNOWN` cho mọi trục; không bảo đảm chất lượng phân loại uncertainty.
- **Scientific impact:** M0U PASS giả tạo, không kiểm tra false certainty/coverage thật.
- **Required remediation:** định nghĩa gold rationale/vắng bằng chứng, phân biệt `UNKNOWN` với `INVALID/UNSCORABLE` do lỗi nguồn, prereg 3-class confusion/report và các non-target/false-unknown limits, thử đối chứng rater luôn UNKNOWN dưới thiết kế checker; chỉ owner chọn threshold sau independent rationale.
- **Gate affected:** G05, G07, G09.
- **Closure condition:** rubric + score contract đủ phân biệt abstention đúng với luôn abstain; thresholds bảo vệ failure mode được khóa trước data.

### SM4M-F2-IR-05 — MEDIUM · DESIGN_DEFECT · Sample-size and threshold rationale incomplete

- **Exact source:** 06 §3–§6; 07 G07/G09.
- **Observed evidence:** 16 M0X clusters/4 per stratum, thresholds `56/64`, `109/128`; 8 M0U targets/axis, `7/8`; ngưỡng 87,5% được chọn bằng tỷ lệ M0, chưa có operating-characteristic/power rationale. M0X chỉ nêu descriptive cluster bootstrap.
- **Expected contract:** prereg test purpose (screening vs confirmatory), false-pass vs false-HOLD trade-off, core/stratum uncertainty, endpoint hierarchy, sensitivity analysis và phạm vi khái quát.
- **Discrepancy:** tỉ lệ tổng có thể che lỗi nguyên core/stratum; 7/8 cho UNKNOWN có biên bất định lớn; agreement không bảo vệ common-mode error.
- **Scientific impact:** quá tự tin với 128 items/1.296 axis decisions thay vì số core độc lập.
- **Required remediation:** justification trước dữ liệu; cluster/stratum-reported rates, core failure patterns, intervals theo core (stratified khi thích hợp); ghi giới hạn exploratory nếu không có power đáng tin; nêu điều kiện dừng và quy tắc multi-endpoint.
- **Gate affected:** G07, G09.
- **Closure condition:** bản sửa có ngưỡng như *candidate* cho tới owner freeze, kèm rationale và giới hạn thống kê không suy quá mức.

### SM4M-F2-IR-06 — MEDIUM · DESIGN_DEFECT · Variant exposure and independence protocol

- **Exact source:** 06 §6; 07 G08.
- **Observed evidence:** hai raters nhận cùng 128 IDs gồm 8 variants/core, random permutation có nói nhưng không có hạn mức adjacency, session memory hoặc chính sách phát hiện so sánh variants.
- **Expected contract:** protocol giảm lộ paired structure trong mỗi rater, nhận diện response dependence; inter-rater agreement không được coi là independent gold.
- **Discrepancy:** reviewer có thể dùng biến thể khác như thông tin phụ, không còn đo khả năng nhận diện từ từng đoạn.
- **Scientific impact:** lạc quan về standalone per-axis grading và understate dependence.
- **Required remediation:** opaque randomized dispersed order, item-isolated judging rules, sealed contexts, provenance/version of rater and model, audit across packet; ghi giới hạn contamination còn lại.
- **Gate affected:** G08, G09.
- **Closure condition:** blind-rater contract chặn side-by-side clues và định nghĩa cách xử lý rater exposure compromise.

### SM4M-F2-IR-07 — MEDIUM · DESIGN_DEFECT · Scorer contract needs executable-level ambiguity resolution

- **Exact source:** 06 §6; 07 §2–§4, G09.
- **Observed evidence:** scoring formulas và negative cases được mô tả đúng hướng nhưng checker `NOT_IMPLEMENTED`, chưa có exact score schema validation cho unknown-in-binary, broken counterpart graph, broken core/stratum balance, before/after-unblind provenance.
- **Expected contract:** deterministic checker spec (dù chưa chạy) giữ mẫu số, bảo toàn toàn bộ edge/invariants, reject invalid metadata và không retroactively alter scores.
- **Discrepancy:** một số trường hợp không xác định FAIL/HOLD cụ thể ở parser và graph constraints, dễ cho scorer implementation khác nhau.
- **Scientific impact:** score không tái lập hoặc mẫu số bị đổi âm thầm.
- **Required remediation:** source-only checker specification, exhaustive negative schema fixture plan, exact reject reason codes, signed scorer/version pre-score; không triển khai/chạy trong review này.
- **Gate affected:** G04, G05, G09, G10.
- **Closure condition:** independent source review chứng minh logic checker/schema quyết định duy nhất, các negative cases fail-closed.

**Execution conditions correctly blocked (không phải finding mới):** private text/gold chưa tạo; quyền dữ liệu, PII, provenance/nonoverlap, human gold, blind mapping, checksum commitment, scorer implementation, rater/resource authorization và owner science GO đều chưa có hoặc chưa kiểm. Quy định HOLD hiện hành là đúng; không chuyển sang PASS dựa trên văn bản tác giả.

## 7. Ma trận G00–G12 — thiết kế vs. execution

| Gate | Read-only design audit | Evidence/execution admission status | Liên hệ |
|---|---|---|---|
| G00 SOURCE | Exact candidate và 3 upstream source pins đọc, PASS phạm vi source | Chưa là full runtime admission PASS | Diff 4 added; MD1 preserved |
| G01 RIGHTS | Có nguyên tắc bảo vệ | `NOT_AUTHORED/NOT_ATTESTED` | PREEXEC_PENDING |
| G02 NONOVERLAP | Check exact+semantic được dự kiến, thứ tự chưa khả thi | `NOT_VERIFIED`, chưa có 72 cores | IR-01 |
| G03 M0_MD1 | Thiết kế và ngưỡng MD1 bất biến PASS_SOURCE_SCOPED | `NO_ITEMS`, rater/score NOT_EXECUTED | M0 riêng polarity |
| G04 M0X_GOLD | Factorial arithmetic PASS; construct design HOLD | `NOT_AUTHORED/NOT_ADJUDICATED` | IR-01/02/03/07 |
| G05 M0U_GOLD | UNKNOWN intent đúng, operational logic HOLD | `NOT_AUTHORED/NOT_ADJUDICATED` | IR-01/04/07 |
| G06 ANTI_SHORTCUT | Có ý tưởng, chưa có negative-control spec | `NOT_SPEC_FROZEN/NOT_RUN` | IR-01/03 |
| G07 THRESHOLDS | M0 frozen bảo toàn; M0X/U ứng viên chưa đủ justification | `NOT_FROZEN_EXTENSION` | IR-02/04/05 |
| G08 BLIND | Two-rater IDs/opaque map thiết kế đúng hướng | `NOT_ASSIGNED/NOT_CREATED` | IR-06 |
| G09 SCORER | Công thức cơ bản phù hợp, detailed checker design HOLD | `NOT_IMPLEMENTED/NOT_EXECUTED` | IR-03/04/05/07 |
| G10 CUSTODY | Có nguyên tắc source/private SHA, key secrecy | `NOT_CREATED/NOT_VERIFIED` | IR-01/07 |
| G11 RESOURCE | Không cần GPU để hiệu chuẩn, rõ scope | `NOT_AUTHORIZED` | PREEXEC_PENDING |
| G12 OWNER | **Distinct design review hoàn tất: HOLD** | `OWNER_SCIENCE_GO=NOT_GRANTED` | IR-01; không phát hành execution |

`PREEXEC_BLOCK=TRUE` vì nhiều gate chưa đạt. Không ghi `G00–G12=PASS`. Tất cả state từ author receipt như `NOT_AUTHORED`, `NOT_VERIFIED`, `NOT_FROZEN`, `NOT_ASSIGNED`, `NOT_IMPLEMENTED`, `NOT_CREATED`, `NOT_AUTHORIZED` tiếp tục được bảo toàn trừ sự kiện đã có độc lập design review báo HOLD.

## 8. Remediation tích hợp duy nhất — không chia micro-permits

**Một gói sửa tài liệu và contract duy nhất, không tự khởi chạy:**

1. **Sửa thứ tự admission (IR-01):** một sơ đồ state/transitions và trách nhiệm owner/custodian, tách rõ `SOURCE/DESIGN_FROZEN`, `PRIVATE_DATA_AUTHORING_ALLOWED_ONLY_IF_OWNER_SCOPED`, `INDEPENDENT_GOLD_RIGHTS_QA`, `PRE_SCORE_RELEASE_IF_ALL_CHECKS_PASS`, `RATER/SCORE_EXECUTION`; cơ chế một quyết định owner tích hợp với điều kiện dừng tự động, không bỏ qua bằng chứng chưa tồn tại và không gọi dữ liệu được tạo ra là science PASS.
2. **Khóa cấu trúc truth conditions (IR-02/04):** rubric evidence per-axis, invariant two-other-axes cho 12 edges/core, feasibility theo bốn strata, rõ UNKNOWN vs false vs invalid và no post-score replacement; thiết kế gold adjudication source-only trước authoring.
3. **Khóa negative-control và rater independence (IR-03/06):** nuisance-only proxy families, core/author/template leakage holdout, balance/cue detection, rater item isolation, blind-order/sealed contexts, invalid exposure rules, tiêu chí FAIL cụ thể.
4. **Thẩm định thống kê và checker (IR-04/05/07):** n=16 clusters và n=8 targets/axis được xử lý đúng; predefine purpose/power/uncertainty, strata/core reporting; full 3-class confusion, false certainty/false abstention & non-target correctness; schema/edge graph/reject code, threshold versions/owner freeze trước authoring.
5. **Lập bảng traceability gate và source rights/custody** nối mỗi artifact trạng thái, trách nhiệm, đúng stage, attestation, chống reuse old TEST/FINAL, bảo vệ private gold và no fake hash; chỉ Independent AI source QA đánh giá tài liệu, không giả human QA.

**Điều kiện đóng gói remediation:** reviewer độc lập xác minh không còn HIGH/CRITICAL design blockers ở **exact revision candidate**; owner có thể phân xử `GO_DESIGN_SCOPED` riêng cho thiết kế đã sửa. Các gate cần byte, dữ liệu, con người hay scorer vẫn HOLD cho tới kiểm tra thực tế. Không tự chạy M0/M0X/M0U.

## 9. Kết luận phạm vi và verdict duy nhất

**`HOLD_REVISE_DESIGN`** — có **4 HIGH, 3 MEDIUM, 0 CRITICAL** trên hợp đồng thiết kế. Mặc dù **SOURCE_INTEGRITY=PASS** và **MD1_UNCHANGED=PASS**, thiếu logic admission phi vòng tròn, sự cô lập semantic có thể kiểm, negative controls đủ quy định và operational UNKNOWN khiến chưa thể chấp nhận `GO_DESIGN_SCOPED` cho exact candidate. Các thiếu hụt execution evidence đã chặn đúng, nhưng không thay thế cho việc sửa bốn HIGH trên giấy.

**Bắt buộc giữ:**

```text
ROOT_CAUSE_IDENTIFIED=NO
M0_EXECUTION=NOT_AUTHORIZED
M0X_DATA=NOT_CREATED
M0U_DATA=NOT_CREATED
GOLD=NOT_FROZEN
SCORING=NOT_EXECUTED
SCIENCE=HOLD
GPU=NO
TRAINING=NO
MODEL_INFERENCE=NO
F3=NOT_OPENED
F4=NOT_OPENED
MERGE=NOT_AUTHORIZED
OWNER_EXECUTION_GO=FALSE
REPOSITORY_MODIFIED=FALSE
```

**Bước thực hiện tiếp theo — duy nhất:** `TTM_SMALL4M_F2_PREEXEC_INTEGRATED_DESIGN_REMEDIATION_IR01_IR07_SINGLE_GATE` — tác giả sửa một bộ 06/07/receipt tương ứng **tại nhánh riêng**, không tự cấp quyền tạo data/scoring, sau đó bàn giao independent exact-candidate re-review và owner adjudication. Reviewer hiện tại không commit, push, merge hay sửa repository; báo cáo và receipt được bàn giao trực tiếp.
