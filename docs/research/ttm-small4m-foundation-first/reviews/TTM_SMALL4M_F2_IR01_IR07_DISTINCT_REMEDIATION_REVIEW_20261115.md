# Kiểm toán độc lập SM4M-F2 — IR01–IR07 Remediation Review

**Ngày:** 15/11/2026  
**Operation:** `TTM_SMALL4M_F2_IR01_IR07_DISTINCT_INDEPENDENT_SOURCE_DESIGN_REREVIEW_SINGLE_GATE`  
**Repository:** `minhtri22/TokenToModel-Lab`  
**Reviewer:** Independent AI Scientific, Measurement & Source Reviewer (không phải human gold custodian)  
**Mode:** `READ_ONLY · SOURCE_ONLY · DESIGN_ONLY · NO_SCIENCE_EXECUTION · NO_REPOSITORY_WRITES`  
**Final decision (một phán quyết): `HOLD_REVISE_DESIGN`**

## 1. Phương pháp, exact source và phạm vi đối chiếu

Đã đọc trực tiếp các tệp qua GitHub connector theo **exact commit** `cf0f459b54d0e91a7923e7a08b621d374e712e51`; không xem floating branch HEAD là nguồn cố định. GitHub compare từ `07adab6262e50b5e17c6ea816bb133866e0a11d2` cho kết quả `ahead_by=1`, `behind_by=0`, `total_commits=1`, đúng **3 modified + 5 added**, 0 removed/renamed. Ba modified: 06, 07 và author design JSON; năm added: 09, 10, author QA JSON và bản gốc của hai independent HOLD artifacts. Không có mã triển khai, checkpoint, science-data, `lineage.md`, MD1 hay owner closure trong exact diff. Việc main HEAD không đổi tuyệt đối theo thời gian **chưa được chứng thực bằng hai independent snapshot của main**; kết luận giới hạn ở diff của commit ứng viên.

- [Exact commit](https://github.com/minhtri22/TokenToModel-Lab/commit/cf0f459b54d0e91a7923e7a08b621d374e712e51)
- [Exact compare](https://github.com/minhtri22/TokenToModel-Lab/compare/07adab6262e50b5e17c6ea816bb133866e0a11d2...cf0f459b54d0e91a7923e7a08b621d374e712e51)

| Tệp đúng commit | Git blob SHA-1 (đã đọc tại path + ref) | Trạng thái |
|---|---|---|
| [06 protocol](https://github.com/minhtri22/TokenToModel-Lab/blob/cf0f459b54d0e91a7923e7a08b621d374e712e51/docs/research/ttm-small4m-foundation-first/06_SM4M_F2_PROSPECTIVE_MEASUREMENT_PREEXEC_INTEGRATED_PROTOCOL_20261115.md) | `a5cc0c51363de9772c27418ea667475c25c791b0` | `MATCH` |
| [07 matrix](https://github.com/minhtri22/TokenToModel-Lab/blob/cf0f459b54d0e91a7923e7a08b621d374e712e51/docs/research/ttm-small4m-foundation-first/07_SM4M_F2_PREEXEC_ADMISSION_SCORING_AND_CUSTODY_MATRIX_20261115.md) | `d0ca205935c01a815aaebe86c90f4e3daf1a1291` | `MATCH` |
| [09 author QA](https://github.com/minhtri22/TokenToModel-Lab/blob/cf0f459b54d0e91a7923e7a08b621d374e712e51/docs/research/ttm-small4m-foundation-first/09_SM4M_F2_IR01_IR07_AUTHOR_ADVERSARIAL_SOURCE_QA_20261115.md) | `4fa489a0e941f142cdec454b08f64bf0be1d6a8e` | `MATCH` |
| [10 handoff](https://github.com/minhtri22/TokenToModel-Lab/blob/cf0f459b54d0e91a7923e7a08b621d374e712e51/docs/research/ttm-small4m-foundation-first/10_SM4M_F2_IR01_IR07_DISTINCT_REVIEW_HANDOFF_20261115.md) | `b97494e46b8d259380129ebc4ff5003cfc3ac887` | `MATCH` |
| [Author QA JSON](https://github.com/minhtri22/TokenToModel-Lab/blob/cf0f459b54d0e91a7923e7a08b621d374e712e51/artifacts/research/ttm-small4m-foundation-first/TTM_SMALL4M_F2_IR01_IR07_AUTHOR_ADVERSARIAL_SOURCE_QA_RECEIPT_20261115.json) | `01e589c62fded5e733bb50a24bbe73d83fe36ee0` | `MATCH` |
| [Updated design JSON](https://github.com/minhtri22/TokenToModel-Lab/blob/cf0f459b54d0e91a7923e7a08b621d374e712e51/artifacts/research/ttm-small4m-foundation-first/TTM_SMALL4M_F2_PREEXEC_DESIGN_AUTHOR_RECEIPT_20261115.json) | `44ac2b451a4be356a920f0e9337dd729e9a77b15` | `MATCH` |
| [Original HOLD report](https://github.com/minhtri22/TokenToModel-Lab/blob/cf0f459b54d0e91a7923e7a08b621d374e712e51/docs/research/ttm-small4m-foundation-first/reviews/TTM_SMALL4M_F2_PREEXEC_DISTINCT_SOURCE_DESIGN_REVIEW_20261115.md) | `e43774e67d9f0c20961bfb0c350971957153ad14` | `MATCH` |
| [Original HOLD receipt](https://github.com/minhtri22/TokenToModel-Lab/blob/cf0f459b54d0e91a7923e7a08b621d374e712e51/artifacts/research/ttm-small4m-foundation-first/reviews/TTM_SMALL4M_F2_PREEXEC_DISTINCT_SOURCE_DESIGN_REVIEW_RECEIPT_20261115.json) | `eca67249b8bdd54e42d83c3e17395afa2605ee9f` | `MATCH` |


**Byte-preservation gốc:** original independent HOLD report có SHA-256 tính từ nội dung GitHub UTF-8 `c4a43c9236debc967a9a4c088c158074f5fbf0201648677c53e6ea49cffd5376`; original HOLD JSON `70685237d07b20bb7b40b3028195e835b88b544e60151d7f0eb150f60a7357d2`. Cả hai khớp handoff, ngoài việc Git blob SHA-1 nêu riêng. SHA-256 được tính bằng một implementation SHA-256 thuần JS (self-test chuẩn `abc` PASS) trên nội dung đọc trực tiếp; đây là integrity check, **không phải** QA khoa học.

**Upstream MD1:** path `docs/research/ttm-hdata-fail4-md1/TTM_HDATA_FAIL4_MD1_PROSPECTIVE_PREREG_AND_FOUR_FAIL_MECHANISM_PLAN_20261114.md`, commit `33021a421f05bb3bfa0999ad12bc3bd144366da9`, Git blob SHA-1 `384d077600ed864a917fdd5e74b5a5bca0ed8766` đọc khớp. MD1 bất biến: 32 cores (4 strata ×8), 64 continuations (32 `111`, 32 `000`), hai blind raters cùng 64 ID, sensitivity ≥28/32 và specificity ≥28/32 **mỗi axis mỗi rater**, agreement ≥0,85 mỗi axis. Raw agreement `55/64` là **cách làm tròn được đề xuất về sau**, không tự gán cho MD1. MD1 không chứng minh riêng tính tách biệt actor/object/goal.

**Owner Foundation First closure:** commit `c233dff20b9b020aefd732ce62bfa2e7aebd3985`, tệp `05_SMALL4M_F01_F05_OWNER_INTEGRATED_DESIGN_ADJUDICATION_20261115.md`, Git blob `3fee9e58914de4c6f41851ca6f7ce89d6bf67124`, ghi `ACCEPT_GO_DESIGN_SCOPED_CLOSE_F01_F05`. Scope **design-only**, không có execution/science GO; không bị exact remediation diff sửa. Original F2 HOLD trên baseline giữ nguyên, không được hồi tố thay bằng verdict hiện tại.

## 2. Bảng bảy finding gốc — đối chiếu substantive

| Finding | Severity | Verdict sau re-review | Bằng chứng và lý do |
|---|---|---|---|
| `IR-01` | HIGH | `HOLD_DESIGN` | S0–S5, G12A/B giải quyết cấu trúc cơ bản nhưng proof 2³ “trước owner authoring GO” xung đột mốc G04E hậu tạo dữ liệu. |
| `IR-02` | HIGH | `HOLD_DESIGN` | Ledger/12 edges/witness tồn tại, nhưng chưa đảm bảo gold suy được từ chính evidence người chấm được phép thấy. |
| `IR-03` | HIGH | `CLOSED_DESIGN` | NC1–NC6 bắt buộc, core-heldout, mọi proxy phải pass; thực nghiệm và exact prespec vẫn là preexec pending. |
| `IR-04` | HIGH | `CLOSED_DESIGN` | Rubric 0/1/UNKNOWN/INVALID, gold 8/8/8, 3×3 và always-UNKNOWN FAIL đã được quy định. |
| `IR-05` | MEDIUM | `CLOSED_DESIGN` | Cỡ mẫu/đơn vị độc lập và giới hạn screening rõ, ngưỡng mới chưa frozen. |
| `IR-06` | MEDIUM | `CLOSED_DESIGN` | Context isolation, memory ban, exposure HOLD đã được định nghĩa; thực thi thực tế pending. |
| `IR-07` | MEDIUM | `HOLD_DESIGN` | Field lists và priority theo lớp chưa đủ machine-complete cho checker deterministic; 28 specs chưa chạy. |


### Traceability chi tiết (đúng bảy trường bắt buộc)

**IR-01 — HIGH — `HOLD_DESIGN`.** `finding_id=SM4M-F2-IR-01`; `original_finding_id=SM4M-F2-IR-01`; `exact_source=06 §2–3; 07 §1` trong [06](https://github.com/minhtri22/TokenToModel-Lab/blob/cf0f459b54d0e91a7923e7a08b621d374e712e51/docs/research/ttm-small4m-foundation-first/06_SM4M_F2_PROSPECTIVE_MEASUREMENT_PREEXEC_INTEGRATED_PROTOCOL_20261115.md) và [07](https://github.com/minhtri22/TokenToModel-Lab/blob/cf0f459b54d0e91a7923e7a08b621d374e712e51/docs/research/ttm-small4m-foundation-first/07_SM4M_F2_PREEXEC_ADMISSION_SCORING_AND_CUSTODY_MATRIX_20261115.md). **Observed evidence:** S0–S5 và G12A/G12B tách được P/E, nhưng 06 §3 yêu cầu “demonstrate 2³ feasibility ... before owner authoring GO” trong khi bằng chứng 8 continuation/core và gold là G04E chỉ được tạo từ S2. Chưa định nghĩa chứng minh tiền-authoring được phép là ký hiệu hay văn bản thực. **Scientific impact:** Có thể tái xuất hiện admission cycle hoặc đẩy tác giả tạo dữ liệu trước G12A. **Required remediation:** Tách G04P thành proof-of-concept thuần thiết kế/tính khả thi logic không tạo item; G04E thành kiểm chứng 8 văn bản thật và 12 cạnh sau G12A; sửa đồng bộ 06/07/receipt. **Closure condition:** Independent design reviewer chứng minh đường S0→S4 không phụ thuộc E-gate trước S2 và mọi proof trước S2 có đầu vào hợp pháp.

**IR-02 — HIGH — `HOLD_DESIGN`.** `finding_id=SM4M-F2-IR-02`; `original_finding_id=SM4M-F2-IR-02`; `exact_source=06 §3; 07 §2` trong [06](https://github.com/minhtri22/TokenToModel-Lab/blob/cf0f459b54d0e91a7923e7a08b621d374e712e51/docs/research/ttm-small4m-foundation-first/06_SM4M_F2_PROSPECTIVE_MEASUREMENT_PREEXEC_INTEGRATED_PROTOCOL_20261115.md) và [07](https://github.com/minhtri22/TokenToModel-Lab/blob/cf0f459b54d0e91a7923e7a08b621d374e712e51/docs/research/ttm-small4m-foundation-first/07_SM4M_F2_PREEXEC_ADMISSION_SCORING_AND_CUSTODY_MATRIX_20261115.md). **Observed evidence:** Đã có fact ledger, 3 predicates, 12 cạnh/core, hai witness bất biến, hai gold adjudicators và fail-closed. Tuy nhiên gold được xác định từ E_core nhưng giao thức chưa buộc rater-visible item chứa đủ thông tin của cùng E_core để người chấm suy được từng nhãn. “Standalone texts” và cấm gửi source ledger không giải quyết việc này. **Scientific impact:** M0X có thể đo khả năng đoán/lexical cue hoặc kiến thức ngoài thay vì actor/object/goal theo một bằng chứng chung. **Required remediation:** Khóa rater-visible evidence envelope: story prefix, ngữ cảnh sự kiện/thời gian và văn bản biến thể; phải đủ cho ba câu hỏi mà không lộ intended gold, witness answer key hay điều kiện; kiểm chứng tính quyết định được ở cấp trục/stratum. **Closure condition:** Đặc tả đầy đủ một packet chuẩn và audit rằng mỗi gold 0/1 quyết định được từ chính đầu vào người chấm có quyền thấy; G04E vẫn hậu-authoring.

**IR-03 — HIGH — `CLOSED_DESIGN`.** `finding_id=SM4M-F2-IR-03`; `original_finding_id=SM4M-F2-IR-03`; `exact_source=06 §4; 07 G06/§4` trong [06](https://github.com/minhtri22/TokenToModel-Lab/blob/cf0f459b54d0e91a7923e7a08b621d374e712e51/docs/research/ttm-small4m-foundation-first/06_SM4M_F2_PROSPECTIVE_MEASUREMENT_PREEXEC_INTEGRATED_PROTOCOL_20261115.md) và [07](https://github.com/minhtri22/TokenToModel-Lab/blob/cf0f459b54d0e91a7923e7a08b621d374e712e51/docs/research/ttm-small4m-foundation-first/07_SM4M_F2_PREEXEC_ADMISSION_SCORING_AND_CUSTODY_MATRIX_20261115.md). **Observed evidence:** NC1–NC6 là danh mục bắt buộc, core-heldout 4 folds; mọi proxy phải qua, bất kỳ leak/BA>0.625 dẫn HOLD. Mô hình, feature vocabulary, budget/seed và threshold chưa frozen theo G06P. **Scientific impact:** Hạn chế lối tắt đã được quy định theo hướng fail-closed; không thể suy absence-of-all-shortcuts từ kết quả giả định hoặc 16 cores. **Required remediation:** Trước G12A phải freeze thực thể các proxy, danh sách cue và xử lý negation/role cues có ý nghĩa ngữ nghĩa thật; rà soát power và điều kiện author/template-disjoint. **Closure condition:** G06P độc lập PASS trước authoring; G06E mọi receipt thực sau authoring, không được suy từ 44 symbolic asserts.

**IR-04 — HIGH — `CLOSED_DESIGN`.** `finding_id=SM4M-F2-IR-04`; `original_finding_id=SM4M-F2-IR-04`; `exact_source=06 §5; 07 §2–4` trong [06](https://github.com/minhtri22/TokenToModel-Lab/blob/cf0f459b54d0e91a7923e7a08b621d374e712e51/docs/research/ttm-small4m-foundation-first/06_SM4M_F2_PROSPECTIVE_MEASUREMENT_PREEXEC_INTEGRATED_PROTOCOL_20261115.md) và [07](https://github.com/minhtri22/TokenToModel-Lab/blob/cf0f459b54d0e91a7923e7a08b621d374e712e51/docs/research/ttm-small4m-foundation-first/07_SM4M_F2_PREEXEC_ADMISSION_SCORING_AND_CUSTODY_MATRIX_20261115.md). **Observed evidence:** 0/1/UNKNOWN/INVALID_SOURCE được phân biệt theo nguồn, M0U 24 cores với gold từng trục 8/8/8 và bảng 3×3; rater always-UNKNOWN đạt 8/8 target nhưng 0/16 non-target, chắc chắn FAIL. **Scientific impact:** Failure mode always-abstain đã bị chặn về mặt số học; independent epistemic gold và ambiguity rulings vẫn chưa có. **Required remediation:** Giữ nguyên rule: source mâu thuẫn, referent không phân giải hoặc thiếu item là INVALID/HOLD, không quy ra UNKNOWN; áp dụng qua independent source gold trước score. **Closure condition:** Độc lập adjudicate nguồn cho các class khi có item thực, chốt ngưỡng ứng viên trước authoring.

**IR-05 — MEDIUM — `CLOSED_DESIGN`.** `finding_id=SM4M-F2-IR-05`; `original_finding_id=SM4M-F2-IR-05`; `exact_source=06 §6; 07 §3` trong [06](https://github.com/minhtri22/TokenToModel-Lab/blob/cf0f459b54d0e91a7923e7a08b621d374e712e51/docs/research/ttm-small4m-foundation-first/06_SM4M_F2_PROSPECTIVE_MEASUREMENT_PREEXEC_INTEGRATED_PROTOCOL_20261115.md) và [07](https://github.com/minhtri22/TokenToModel-Lab/blob/cf0f459b54d0e91a7923e7a08b621d374e712e51/docs/research/ttm-small4m-foundation-first/07_SM4M_F2_PREEXEC_ADMISSION_SCORING_AND_CUSTODY_MATRIX_20261115.md). **Observed evidence:** Phân biệt 72 cores, 216 items, 432 rater rows và 1.296 axis decisions; n độc lập M0X=16 cores, M0U=24 cores; 56/64, 109/128, stratum floor 12/16 và 7/8 là candidate screening, không xác nhận power. **Scientific impact:** Đã loại phép suy IID giả và confirmatory overclaim; n nhỏ tạo uncertainty lớn và threshold BA0.625 chưa được hiệu chỉnh. **Required remediation:** Owner chỉ freeze sau khi có rationale/tradeoff và kế hoạch báo cáo cluster/stratum CI đủ chặt; không công bố phát hiện causal hay generalization. **Closure condition:** Tài liệu và kết quả sau này chỉ định lượng screening, tuyệt đối không coi item/edge/axis là iid observations.

**IR-06 — MEDIUM — `CLOSED_DESIGN`.** `finding_id=SM4M-F2-IR-06`; `original_finding_id=SM4M-F2-IR-06`; `exact_source=06 §7; 07 G08/§2` trong [06](https://github.com/minhtri22/TokenToModel-Lab/blob/cf0f459b54d0e91a7923e7a08b621d374e712e51/docs/research/ttm-small4m-foundation-first/06_SM4M_F2_PROSPECTIVE_MEASUREMENT_PREEXEC_INTEGRATED_PROTOCOL_20261115.md) và [07](https://github.com/minhtri22/TokenToModel-Lab/blob/cf0f459b54d0e91a7923e7a08b621d374e712e51/docs/research/ttm-small4m-foundation-first/07_SM4M_F2_PREEXEC_ADMISSION_SCORING_AND_CUSTODY_MATRIX_20261115.md). **Observed evidence:** Fresh isolated item sessions, opaque IDs, memory/side-by-side ban, provider/version pin, exposure HOLD, và rater độc lập đã được quy định. **Scientific impact:** Người chấm là con người không thể được chứng thực tuyệt đối là không hồi tưởng; AI có thể có provider-level memory/logging ngoài tầm quan sát. **Required remediation:** G08P phải khóa phương pháp kiểm thử isolation có thể kiểm toán và chuẩn chứng cứ/ngoại lệ; nếu không thể kiểm chứng theo phương thức đã chọn thì HOLD. **Closure condition:** G08E chứng minh isolation thực cho provider/human đã chọn; hai raters cùng shortcut không là valid gold.

**IR-07 — MEDIUM — `HOLD_DESIGN`.** `finding_id=SM4M-F2-IR-07`; `original_finding_id=SM4M-F2-IR-07`; `exact_source=06 §8; 07 §2–4` trong [06](https://github.com/minhtri22/TokenToModel-Lab/blob/cf0f459b54d0e91a7923e7a08b621d374e712e51/docs/research/ttm-small4m-foundation-first/06_SM4M_F2_PROSPECTIVE_MEASUREMENT_PREEXEC_INTEGRATED_PROTOCOL_20261115.md) và [07](https://github.com/minhtri22/TokenToModel-Lab/blob/cf0f459b54d0e91a7923e7a08b621d374e712e51/docs/research/ttm-small4m-foundation-first/07_SM4M_F2_PREEXEC_ADMISSION_SCORING_AND_CUSTODY_MATRIX_20261115.md). **Observed evidence:** Có 28 negative-fixture specifications, high-level reason codes và thứ tự các lớp; tuy nhiên private schemas chỉ liệt kê tên trường, không khóa type/enum/cross-reference cho các manifest, source/packet payload, cách chọn lỗi đầu tiên khi nhiều lỗi trong cùng lớp hoặc version/canonicalization. **Scientific impact:** Hai implementation đều có thể cho verdict/reason khác nhau; N01–N28 chưa chạy trên checker và không chứng minh determinism. **Required remediation:** Cung cấp machine-checkable schema hoặc bảng type+nullability+required/unique+constraints, canonical digest/packet fields, total precedence cho multi-fault, oracle fixture expected code; không chạy scorer trong review. **Closure condition:** Hai independent implementations hoặc independent design inspection thống nhất outcome tất cả path/multi-fault; checker executable QA vẫn G09E pending.

## 3. Kiểm tra DAG admission và thẩm quyền

Chuỗi dự kiến đúng hướng:

`S0 design → S1 frozen P-gates → G12A owner conditional GO → S2 private authoring + scoped nuisance-only/checker synthetic QA → S3 G01E/G02E/G04E/G05E/G06E/G08E/G09E/G10E + independent readback → G12B immutable conditional release → S4 blind scoring → S5 final closure`.

**Điều PASS của phần sửa:** G12A không yêu cầu 72 cores/gold/rights từng item đã có; G12B không thay G12A và không do tác giả/checker tự cấp. Không có owner GO hiện tại. QA proxy/checker thực tế chỉ được làm ở S2 nếu owner tương lai xác định rõ phạm vi; không được gọi là calibration/rater scoring.

**Điểm HOLD:** 06 §3 ghi phải có independent demonstration đủ 8 điều kiện ở **mỗi stratum trước owner authoring GO**, nhưng 06 §2 và 07 G04E đặt full eight-variant text/source witness proof ở S2–S3. Chưa nói chứng minh G04P bằng *biểu thức logic/trường hợp trừu tượng* hay bằng câu văn private thực. Nếu là chữ thật, gate lại cần tạo dữ liệu khi đang cấm tạo; nếu là proof ký hiệu, nó không thể xác lập validity ngữ nghĩa của text thật. Cần chia dứt khoát P/E và nêu phép kiểm/nguồn evidence hợp pháp cho từng giai đoạn. `S4` vẫn phải impossible nếu thiếu bất cứ G12A-scoring clause, S3 QA, G12B release nào.

## 4. Semantic independence, gold và anti-shortcut

M0X đưa 16 core độc lập, mỗi core tám pattern `000..111`, 12 cạnh Hamming-1 (bốn cạnh/trục). Tổng 128 items, 64 labels true và 64 false/trục, 64 cạnh/trục. **Số học là đúng**. Fact ledger `E_core`, 3 witnesses và invariant của hai trục không thay đã cải thiện lỗi cũ. Hậu tác giả không được loại/rewrite core sau khi xem score; gold sai thì HOLD toàn packet.

Tuy nhiên **nhãn do gold adjudicators xác định từ `E_core` không đương nhiên có thể xác định bởi rater trong phiên mù**: 07 `rater_packet` chỉ kê các ID/version/receipt, 07 còn cấm cho rater xem source ledger. 06 “standalone texts” chưa khóa việc mỗi item có kèm prefix/ngữ cảnh sự kiện/tương quan thời gian hay không. Vì vậy cùng một văn bản có thể rõ ràng theo `E_core` cho adjudicator nhưng thiếu bằng chứng cho blind rater. Đây là lỗi thông tin đầu vào đối với phép đo, tách khỏi việc đếm 12 cạnh. Phải kiểm quyết định được *từ payload rater thấy* trước khi đánh giá item theo gold.

NC1–NC6 và `HOLD_SHORTCUT` là một bước tiến thực chất: constant/polarity baseline thất bại trên toán ký hiệu; length/format, lexical/style, metadata/order, ensemble, và independent coupling đều là kiểm bắt buộc. Nhưng kết quả 44/44 **không** bao gồm chạy proxy trên text thật, không chứng minh không có shortcut. Cấu hình mô hình và vocabulary vẫn chưa preregistered chính xác; bốn folds chỉ có 4 cores heldout/fold (mỗi stratum một core). Nếu author/template disjoint không thể đạt thì `HOLD_INADEQUATE_GROUP_DISJOINTNESS`, không mượn item-level split. Cần xác định cách phân biệt **tín hiệu ngôn ngữ chứa bằng chứng ngữ nghĩa thật** (ví dụ phủ định một fact) với nuisance cue, tránh tự loại tất cả dữ liệu hợp lệ hoặc che giấu leakage bằng việc loại cue hậu nghiệm. BA≤0,625 là **candidate risk screen**, không là chứng minh absence-of-shortcuts.

## 5. UNKNOWN và tính hợp lệ thống kê

M0U gồm 24 core độc lập, mỗi core một item, mỗi target UNKNOWN 8 items/trục, mỗi stratum 2 items/target; non-target 2-bit patterns xuất hiện hai lần trong mỗi target group. Suy ra cho mỗi axis: gold 0/1/UNKNOWN = **8/8/8**. Rater trả UNKNOWN cho toàn bộ sẽ có target recall 8/8 nhưng non-target correct 0/16 và false UNKNOWN 16/16, không thể qua gates 14/16 và ≤1/16. Đây là khắc phục thật sự đối với shortcut luôn abstain. Với source mâu thuẫn, referent mơ hồ hay thiếu response, không thể dùng `UNKNOWN` để “cứu” điểm: các trường hợp này phải HOLD/invalid theo rubric.

Tổng dự kiến **72 cores / 216 items / 432 item-rater assignments / 1.296 axis decisions**, không được xem 1.296 là n độc lập. M0X chỉ có 16 core clusters (4/stratum), edge scores dùng chung endpoints; M0U chỉ có tám gold UNKNOWN/trục. Đánh giá `7/8` có khoảng Wilson 95% xấp xỉ **0,529–0,978** ngay cả dưới mô hình nhị thức đơn giản; phụ thuộc trong dữ liệu thật làm uncertainty có thể lớn hơn. Ngưỡng M0X `56/64` và agreement `109/128`, per-stratum `12/16`, nuisance `0.625` cũng mới là ứng viên. Nếu sau này owner freeze thì vẫn chỉ được nói *screening/exploratory scoped*; không phải chứng thực suy rộng sang output T4 hay kết luận confirmatory.

## 6. Rater exposure, custody và checker deterministic

G08 đã định nghĩa stateless context, opaque mapping, same underlying IDs, rater/provider pins, cấm xem cùng biến thể và `HOLD_RATER_EXPOSURE`. Nhưng “không nhớ giữa sessions” ở human raters khó chứng thực tuyệt đối; AI provider có thể giữ memory/log retrieval không quan sát được. Hợp đồng tương lai cần nêu rõ quan sát nào chứng thực isolation, mức dư rủi ro được chấp nhận và khi nào fail closed, không lấy agreement giữa hai raters để thay gold truth.

G09 đã có type rules cho **score** (M0/M0X chỉ int 0/1; M0U int 0/1 hoặc exact `UNKNOWN`), denominator không drop/impute, graph 8 nodes/12 edges, reject reason codes và N01–N28. Điều này tiến bộ so với bản cũ, nhưng **field lists ≠ machine-readable full schema**: còn thiếu loại dữ liệu và nullability của các metadata khác; namespace của IDs, giới hạn giá trị, khóa tham chiếu, rater-visible payload binding, quy tắc precedence nếu một record vi phạm nhiều điều kiện trong cùng lớp và dữ liệu canonical để xác minh SHA/HMAC. G09E implementation và negative QA vẫn `NOT_EXECUTED`. Một checker được viết sau này không được mặc nhiên đánh PASS nhờ 28 tên fixture.

## 7. Kiểm toán adversarial riêng đối với author QA 44/44

Đã đọc [09](https://github.com/minhtri22/TokenToModel-Lab/blob/cf0f459b54d0e91a7923e7a08b621d374e712e51/docs/research/ttm-small4m-foundation-first/09_SM4M_F2_IR01_IR07_AUTHOR_ADVERSARIAL_SOURCE_QA_20261115.md) và [JSON QA receipt](https://github.com/minhtri22/TokenToModel-Lab/blob/cf0f459b54d0e91a7923e7a08b621d374e712e51/artifacts/research/ttm-small4m-foundation-first/TTM_SMALL4M_F2_IR01_IR07_AUTHOR_ADVERSARIAL_SOURCE_QA_RECEIPT_20261115.json). Hai vòng tác giả báo `28/28`, sau sửa `44/44` — có 44 tests liệt kê và không có fail trong author receipt. Phân định:

- `QA07/QA12` kiểm reachability với **guards giả định**, không chứng minh thật có quyền owner hay tất cả artifact.
- `QA15–QA23` kiểm đồ thị **nhãn ký hiệu**, không giải quyết existence 8 natural independent variants hoặc thông tin mà rater nhìn thấy.
- `QA24–QA30` kiểm shortcut 000/111/majority và always-UNKNOWN bằng công thức, không test lexical/template leak hoặc score của người chấm thực.
- `QA33–QA40` phản ánh asserted schema/reason strings, không chạy parser/checker/28 negative fixtures.
- Author tự khai `realGoldVerified=false`, `ownerGranted=false`, `actualReleased=false`, `G09 implementation NOT_EXECUTED`; đây là giới hạn đúng, không phải độc lập QA pass.

**Kết luận:** author QA `PASS_44_44_SCOPED` hợp lệ như một chứng cứ self-QA logic; không đủ làm tiền đề GO thiết kế hoặc pre-score release.

## 8. Finding mới — không ghi đè finding gốc

### NF-01 — HIGH · `HOLD_DESIGN` — Rater-visible evidence parity missing

- **Exact source:** 06 §3/§7; 07 §2 (core_manifest, rater_packet); [06](https://github.com/minhtri22/TokenToModel-Lab/blob/cf0f459b54d0e91a7923e7a08b621d374e712e51/docs/research/ttm-small4m-foundation-first/06_SM4M_F2_PROSPECTIVE_MEASUREMENT_PREEXEC_INTEGRATED_PROTOCOL_20261115.md), [07](https://github.com/minhtri22/TokenToModel-Lab/blob/cf0f459b54d0e91a7923e7a08b621d374e712e51/docs/research/ttm-small4m-foundation-first/07_SM4M_F2_PREEXEC_ADMISSION_SCORING_AND_CUSTODY_MATRIX_20261115.md).
- **Observed evidence:** Gold depends on E_core witnesses; rater_packet specifies IDs, model pin, attestation but not a canonical narrative context/prefix/payload reference. 07 says rater never sees source ledger; 06 requires standalone items but does not define what facts each contains.
- **Scientific impact:** Gold may be decidable to adjudicators but not inferable to blind raters, invalidating actor/object/goal calibration.
- **Required remediation:** Define versioned rater-visible task payload with fact-bearing prefix/continuation and exact information parity; prohibit answer-key leakage; require item-level independent sufficiency review.
- **Closure condition:** For all axis strata and target classes, source evidence needed for a gold decision is present or logically recoverable from the blinded packet without looking at E_core private answer key.
- **Related original findings:** IR-02, IR-06, IR-07.

### NF-02 — HIGH · `HOLD_DESIGN` — Pre-G12A full cube feasibility proof is not stage-bounded

- **Exact source:** 06 §3 last paragraph versus 06 §2 S1/S2 and 07 §1 G04P/G04E; [06](https://github.com/minhtri22/TokenToModel-Lab/blob/cf0f459b54d0e91a7923e7a08b621d374e712e51/docs/research/ttm-small4m-foundation-first/06_SM4M_F2_PROSPECTIVE_MEASUREMENT_PREEXEC_INTEGRATED_PROTOCOL_20261115.md), [07](https://github.com/minhtri22/TokenToModel-Lab/blob/cf0f459b54d0e91a7923e7a08b621d374e712e51/docs/research/ttm-small4m-foundation-first/07_SM4M_F2_PREEXEC_ADMISSION_SCORING_AND_CUSTODY_MATRIX_20261115.md).
- **Observed evidence:** The protocol demands independent demonstration of 2³ feasibility for each stratum before owner authoring GO; however it simultaneously treats full 8 real text variants and 12 source-supported edges as G04E after S2.
- **Scientific impact:** An ambiguous prerequisite can block all authoring or incentivize creation of unpermitted empirical calibration texts.
- **Required remediation:** Separate lawful static/abstract G04P feasibility proof from per-core real text G04E evidence; state whether hypothetical examples are allowed, and their non-science status.
- **Closure condition:** All stage dependencies and allowed artifacts are unambiguous and forward-only, including negative/invalid stratum stop rule.
- **Related original findings:** IR-01, IR-02.

### NF-03 — MEDIUM · `HOLD_DESIGN` — Strict schema and first-error contract not fully machine-defined

- **Exact source:** 07 §2/§3/§4, especially manifest field lists and N01–N28; [06](https://github.com/minhtri22/TokenToModel-Lab/blob/cf0f459b54d0e91a7923e7a08b621d374e712e51/docs/research/ttm-small4m-foundation-first/06_SM4M_F2_PROSPECTIVE_MEASUREMENT_PREEXEC_INTEGRATED_PROTOCOL_20261115.md), [07](https://github.com/minhtri22/TokenToModel-Lab/blob/cf0f459b54d0e91a7923e7a08b621d374e712e51/docs/research/ttm-small4m-foundation-first/07_SM4M_F2_PREEXEC_ADMISSION_SCORING_AND_CUSTODY_MATRIX_20261115.md).
- **Observed evidence:** Scores types are enumerated, but other field types, nullability, key scopes, relation joins, schema versions, multi-error same-level order and canonical data signatures remain unspecified.
- **Scientific impact:** Potential divergent parser and reject-code decisions, undermining reproducible scoring and error-first semantics.
- **Required remediation:** Supply full schema, comparator priority, and compound-invalid fixture table, with authenticated packet binding; preserve N01–N28 as NOT_EXECUTED.
- **Closure condition:** Independent static readback can deterministically assign one output or one first error for every permitted input class.
- **Related original findings:** IR-07.

## 9. Admission gates — design/evidence distinction

| Gate | Status tại exact candidate | Thẩm quyền hiện tại |
|---|---|---|
| G00 SOURCE | Source-only pins PASS; runtime source G00E chưa | Không phát hành S2/S4 |
| G01 RIGHTS | G01P draft; G01E not authored/attested | HOLD |
| G02 NONOVERLAP | G02P draft; G02E not verified | HOLD |
| G03 MD1 | Immutable MD1 source PASS; M0 items absent | HOLD runtime |
| G04 M0X | P candidate; E gold/12-edge not authored | HOLD + IR02 |
| G05 M0U | P candidate; E epistemic gold not authored | HOLD runtime |
| G06 SHORTCUT | P candidate, proxy family/budget not frozen; E not run | HOLD runtime |
| G07 THRESHOLDS | New thresholds candidate, owner NOT frozen | HOLD |
| G08 BLIND | P draft, E rater/provider not verified | HOLD |
| G09 SCORER | Source contract has gap; scorer not implemented | HOLD + IR07 |
| G10 CUSTODY | Policy draft, private byte commitments absent | HOLD |
| G11 RESOURCE | Not authorized | HOLD |
| G12 OWNER | G12A not granted; G12B blocked | HOLD |

Bất kể phân xử thiết kế: `ROOT_CAUSE_IDENTIFIED=NO`, `F2_PREEXEC_BLOCK=TRUE`, `OWNER_DATA_AUTHORING_GO=FALSE`, `OWNER_SCORING_GO=FALSE`, `GOLD=NOT_FROZEN`, `M0_EXECUTION=NOT_AUTHORIZED`, `M0X/M0U_DATA=NOT_CREATED`, `RATER=NOT_EXECUTED`, `SCORER_IMPLEMENTATION=NOT_EXECUTED`, `SCIENCE=HOLD`, `GPU=NO`, `MODEL_INFERENCE=NO`, `TRAINING=NO`, `F3/F4=NOT_OPENED`, `MERGE=NOT_AUTHORIZED`.

## 10. Một gói remediation tích hợp duy nhất

1. **Rater-evidence parity + semantic feasibility (IR-02, NF-01):** khóa input item-visible (prefix, context, continuation, task predicate/axes) và exact private-gold visibility boundary. Mỗi axis ở mỗi stratum phải có tiêu chí kiểm *suy được từ rater-visible evidence*, không phải hidden answer ledger. Fail closed khi không đủ dữ kiện/coupled constructs; không cần tạo dữ liệu thật ở gate review này.
2. **Phân tuyến chứng minh trước/sau G12A (IR-01, NF-02):** rewrite 06 §3 và 07 G04P/G04E để G04P chỉ yêu cầu proof/rubric/feasibility design hợp pháp, không đòi actual 8 private texts; G04E mới đòi 8 texts/core, 12 edges, independent adjudication sau G12A. Chỉ một quyết định owner điều kiện, mọi hậu-creation evidence phải độc lập trước G12B; không chia micro-permits.
3. **Strict scorer interface + prefreeze QA (IR-07, NF-03):** publish đầy đủ versioned JSON schemas, foreign keys, canonical encoding/hash, packet content binding, exact precedence của compound errors, full fixture expected outcomes. Khóa planned nuisance model/feature budget/seed và justification BA ceiling/stratum floors theo một prereg package; chỉ được chạy checker implementation/synthetic QA khi owner tương lai cấp đúng scope.

**Đóng gói:** tác giả sửa source/docs/receipt thành **một exact candidate mới** để independent review; không tạo core/label/gold/scorer score hay sửa lịch sử. Owner chỉ quyết định tiếp khi source/design đã đủ; reviewer hiện tại không cấp quyền nào.

## 11. Giới hạn và phán quyết cuối

Đây là đánh giá độc lập bằng **AI trên văn bản/JSON GitHub**, không phải kiểm thử người chấm, proxy học máy, proof hiện thực của 8 pattern, nghĩa vụ rights/PII, execution SHA/custody hay scientific model assessment. Không chạy model, không tạo item, không chạy parser/checker, không tạo science evidence và không ghi repository. `main` chỉ được kiểm tra theo absence-of-change trong exact branch diff, không bằng lịch sử main HEAD.

**`HOLD_REVISE_DESIGN`**: Các sửa IR-03/04/05/06 đủ đóng ở phạm vi **design contract** với preexec gates riêng vẫn pending. IR-01, IR-02 và IR-07 còn lỗ hổng contract, cùng hai HIGH và một MEDIUM finding mới được nêu. Chưa thể xem phép đo actor/object/goal tái lập và khả thi chỉ dựa trên author QA `44/44`. Original HOLD ở candidate cũ vẫn giữ nguyên; verdict này áp dụng **duy nhất** commit `cf0f459b54d0e91a7923e7a08b621d374e712e51`.

**Bước thực hiện tiếp theo — duy nhất:** `TTM_SMALL4M_F2_IR01_IR02_IR07_AND_NF01_NF03_INTEGRATED_CONTRACT_REMEDIATION_SINGLE_GATE` — sửa một gói source/design thống nhất; sau đó mới thực hiện một lượt independent exact-candidate source re-review, không tự mở execution.
