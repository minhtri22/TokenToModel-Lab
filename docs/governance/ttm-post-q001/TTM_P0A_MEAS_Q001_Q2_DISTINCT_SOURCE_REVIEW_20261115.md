# TTM-P0A-MEAS-Q001 — Kiểm toán độc lập Q2 source/design-only

**Operation:** `TTM_P0A_MEAS_Q2_EXACT_SOURCE_DISTINCT_REVIEW_AND_OWNER_ADMISSION_SINGLE_GATE`  
**Ngày kiểm toán:** 2026-11-16 (UTC+07)  
**Reviewer:** ChatGPT, AI reviewer thực hiện đọc/đối chiếu độc lập từ tác giả Q2; **độc lập nhân sự/tổ chức: NOT_EXTERNALLY_ATTESTED**. Không tham gia viết commit ứng viên.  
**Quyền:** READ_ONLY · SOURCE_ONLY · DESIGN_ONLY. **Không commit, không sửa GitHub/PR/main, không truy cập nguồn riêng tư, không tạo dataset/gold/scorer, không chạy mô hình.**

## 1. Phán quyết độc lập và quyết định trình owner

**Verdict duy nhất: `PASS_Q2_SOURCE_DESIGN_SCOPED`.** Q2 đáp ứng mục đích **so sánh framework, cơ chế cạnh tranh, lựa chọn hành động và điều kiện chứng cứ tương lai** từ nguồn đã có. Đây là PASS về *tính đủ của đặc tả để owner deliberation*, không phải PASS về benchmark, rights, gold, same-task rater, causal identification hay khoa học.

**Kiến nghị owner:** `GO_ACCEPT_Q2_SOURCE_ONLY` **chỉ cho chấp nhận kết quả Q2 trên giấy**, sau khi xem receipt cùng các forward hard veto bên dưới. `HOLD_EVIDENCE_INSUFFICIENT` tiếp tục là lựa chọn duy nhất có cơ sở đối với **actual benchmark authoring/scoring/model execution**. Không tự đóng Q3/Q4, không tự cho phép merge PR #23, không sửa active gate hoặc lineage.

**Biên giới quyết định:** Nếu owner xem những phát hiện forward-veto F-H01/F-M01 là điều kiện phải đóng ngay trong Q2, thay vì trước prospective protocol, lựa chọn bảo thủ là `HOLD_Q2_ADMISSION` và sửa **một gói tích hợp trên cùng PR #23**. Reviewer không thấy thiếu sót registration-level nghiêm trọng đến mức phải bắt buộc HOLD Q2 source/design hiện tại.

## 2. Exact custody, provenance và regression

- Repo: `minhtri22/TokenToModel-Lab`.
- **Exact reviewed candidate HEAD:** `8bf0601c716b5f6395e3b758ee066ff41c9a554d`.
- **Pinned `main` baseline / single parent:** `f31754c21b4e26f7d7a15e53096090f2fa9b5d87`.
- **Draft PR #23:** `OPEN · DRAFT · NOT_MERGED`, `head_sha=8bf0601c716b5f6395e3b758ee066ff41c9a554d`, `base_sha=f31754c21b4e26f7d7a15e53096090f2fa9b5d87` khi kiểm tra; [PR](https://github.com/minhtri22/TokenToModel-Lab/pull/23).
- GitHub compare: `ahead_by=1 · behind_by=0 · total_commits=1`; commit có đúng một parent là pinned main; đúng **4 added, 0 modified/deleted**. Không thay Q1, `ACTIVE_RESEARCH_GATE.md`, policy, `lineage.md`, implementation, model hoặc dataset.
- **Cách xác minh byte:** đọc `fetch_file` tại ref commit 40 hex với `encoding=base64`; giải mã raw bytes; tự tính SHA-1 theo `blob <byte_length>\0<bytes>` và SHA-256; kiểm thử thuật toán với vector `abc`. Tất cả 9 source Git blob khớp GitHub. SHA-256 dưới đây là tính từ raw bytes nhận qua GitHub connector, **không phải xác minh bằng kênh vận chuyển độc lập hoặc local Windows**.

| Key | Git blob SHA-1 (recomputed = GitHub) | Raw SHA-256 (independently computed) | Bytes |
|---|---|---|---:|
| Q2 report | `f05223a3aa8724054fcd7e4e0b2a87392a2cf789` | `4005c0c7a7c560fa2c4f56ba07e868c3bd23444db43e6b798a9e675e9320eae7` | 19744 |
| Q2 matrix | `3591c22c0ae552a5a1e054fa29c2254a19701103` | `2015c37bf3330ff6edd4211292ecc2851a810a5ea0f63025bd1b908def4ad8cf` | 19367 |
| Q2 author QA | `3d68334600f863d1efb809fb85f5c07104b42f55` | `6d6b49a276b82ce92d6f2e972beb39c0d42790e3866b1d25a5b8094948bb2069` | 11179 |
| Q2 handoff | `5dfb910ad4bfa65911bcf2ea3534723d6aea5e64` | `563cfe1887ed0913df54b4742e5715aed39570c46a675a7bd81f5a0064b1dff1` | 7867 |
| Q1 registered | `6b29c962b48c4134c925935409433d4ae2804110` | `60ff7e43d5ae9b75a0b93d01a168bbc4aff48fc9d21ef0c5cd66ff8c962e9141` | 15676 |
| Active gate | `288d4cd2c84315705e7ea06e45c246b6f3d67496` | `270919c4685cdfe1014142ed19635fb5cea1944d6009b2a7501d0ec95f6d54c9` | 7289 |
| Question-first policy | `af1a879a2552f100c6669cb9ab6dc98c930d2e19` | `a570b972d795ee25d572f466426d59cc746183fa620e2ed294484c68560b9df5` | 15342 |
| Q1 distinct source/design review | `38d009fa3cdc36db847565520307a8ff05d4c8c3` | `755efd1b49385a996ae03d2d264897576c91df3dbbe8d890046fb0765dea01a4` | 14001 |
| lineage.md | `3409e036241deb1da6674619a2abc834bea8a2d6` | `53bf28e79964001a91e5084fb8ecea1fabb6e0aa0b8eb48150fd3721dbfc2e0c` | 61725 |

**Link có số dòng:** [Báo cáo Q2](https://github.com/minhtri22/TokenToModel-Lab/blob/8bf0601c716b5f6395e3b758ee066ff41c9a554d/docs/governance/ttm-post-q001/TTM_P0A_MEAS_Q001_Q2_FRAMEWORK_ALTERNATIVES_SOURCE_ONLY_REVIEW_20261115.md) · [Ma trận Q2](https://github.com/minhtri22/TokenToModel-Lab/blob/8bf0601c716b5f6395e3b758ee066ff41c9a554d/artifacts/governance/ttm-post-q001/TTM_P0A_MEAS_Q001_Q2_MECHANISM_DISCRIMINATION_AND_ADMISSION_MATRIX_20261115.json) · [Q1 registered](https://github.com/minhtri22/TokenToModel-Lab/blob/f31754c21b4e26f7d7a15e53096090f2fa9b5d87/docs/governance/ttm-post-q001/TTM_P0A_MEAS_Q001_REGISTERED_QUESTION_GATE_20261115.md) · [Policy](https://github.com/minhtri22/TokenToModel-Lab/blob/f31754c21b4e26f7d7a15e53096090f2fa9b5d87/docs/governance/TTM_QUESTION_FIRST_RESEARCH_ARCHITECTURE_LINEAGE_AND_MAIN_POLICY_20261115.md).

## 3. Đối kháng framework, scope và năm cơ chế M0–M4

**Scope nguyên vẹn:** đúng một họ assertion `LOCATED_AT(entity_id,location_id,reference_time_id)` với ba nhãn truth `TRUE/FALSE/UNKNOWN` cho item `ELIGIBLE`; `REJECT/INVALID` ở trục admission khác, không phải nhãn truth thứ tư. `UNKNOWN_VALID` đòi miền nguồn được chứng minh hữu hạn, đầy đủ và không entail/refute. `FALSE` cần negation hoặc visible exclusivity/incompatibility, không từ hai location khác nhau. [Report L9–22](https://github.com/minhtri22/TokenToModel-Lab/blob/8bf0601c716b5f6395e3b758ee066ff41c9a554d/docs/governance/ttm-post-q001/TTM_P0A_MEAS_Q001_Q2_FRAMEWORK_ALTERNATIVES_SOURCE_ONLY_REVIEW_20261115.md#L9-L22).

**Framework:** 5W1H xác định ai nhìn thấy source ở thời điểm nào; construct validity tách loại item/truth; falsification buộc từng giả thuyết đối diện phản chứng; failure-mode/hard veto không cho điều kiện pháp lý bị bù bởi điểm QA. Quyết định dạng cây định tính thay vì MCDA khi không có weights/prereg/prospective data. `5 Whys` không được trình bày như chứng minh nhân quả. Lựa chọn này thích hợp cho Q2 và **có thể thay đổi quyết định tương lai**: hợp đồng đo lường giữ nguyên, bị thu hẹp, được chuyển hướng, dừng vì bất khả thi, hoặc giữ HOLD. [Report L17–22](https://github.com/minhtri22/TokenToModel-Lab/blob/8bf0601c716b5f6395e3b758ee066ff41c9a554d/docs/governance/ttm-post-q001/TTM_P0A_MEAS_Q001_Q2_FRAMEWORK_ALTERNATIVES_SOURCE_ONLY_REVIEW_20261115.md#L17-L22).

| Cơ chế | Phản giải thích độc lập và phép quan sát có thể bác bỏ | Reviewer disposition |
|---|---|---|
| **M0 — Visible construct** | Một bộ label hợp thức trên nhóm item đã tuyển chưa chứng minh tính khả thi của toàn khung vì có thể loại hầu hết item khó. Phản chứng: sampling frame được khóa từ trước + tỷ lệ eligible/reject theo lý do, ít nhất một item dự kiến hợp lệ thất bại source-only proof hoặc mất refutation => bác bỏ tính khả dụng của construct trong miền định trước. | `PASS_CONCEPTUAL_PREREQUISITE · NOT_EMPIRICALLY_VALIDATED`; F-H01 |
| **M1 — Hidden-only gold** | Witness công khai tình cờ phù hợp với answer key không bảo đảm gold thực sự được xác lập độc lập. Phản chứng M1: người chấm không thấy key/E_core vẫn suy ra cùng label từ chính *material fact sets* của hai effective views; lineage của nhãn không dựa hidden metadata. Phân biệt hidden oracle, source không đầy đủ và truncation. | `TESTABLE · NOT_VERIFIED`; F-M03 |
| **M2 — Ambiguity** | Sự không thống nhất label có thể do nguồn không đủ/độ bao phủ thời gian thay vì ontology. Bác bỏ M2 trong miền xác định bằng typed triple, authority và explicit completeness, rồi blinded rederivation nhất quán. **UNKNOWN hợp lệ** không phải ambiguity hay reject. | `TESTABLE · NOT_VERIFIED`; X14/X19 |
| **M3 — Shortcut** | Tín hiệu lexical/order có thể chỉ là proxy của phân phối nguồn hoặc lỗi rater. Cần phép can thiệp về fact với cue được cân bằng, cộng can thiệp cue-only cùng sự thật; dùng group-disjoint split, freeze endpoint, AD-06 nếu causal pairs. Không thể chứng minh không shortcut chỉ bằng một matched pair bề mặt. | `TESTABLE · NOT_EXECUTED`; F-M04 |
| **M4 — Rater** | Đồng thuận cao giữa hai rater có thể là *common-mode bias* cùng hiểu sai tiên đề địa điểm. Cần rater độc lập cùng task/rubric và gold adjudication dựa visible ontology; kiểm soát thứ tự, abstention, disagreements. FRESH16 S1/S2 khác role không phải inter-rater reliability. | `TESTABLE · NOT_CALIBRATED`; F-M02 |

**Không độc quyền nhân quả:** M1+M2 và M3+M4 có thể cùng tồn tại; M0 là tiền đề hợp lệ phép đo, không đứng cùng cấp như nguyên nhân thất bại model. FC01/FRESH16/T4 TEST64/FINAL24 là historical scoped; không xem thành prospective direct contrast cho Q2. [Report L24–34](https://github.com/minhtri22/TokenToModel-Lab/blob/8bf0601c716b5f6395e3b758ee066ff41c9a554d/docs/governance/ttm-post-q001/TTM_P0A_MEAS_Q001_Q2_FRAMEWORK_ALTERNATIVES_SOURCE_ONLY_REVIEW_20261115.md#L24-L34).

## 4. Ma trận năm phương án — không đánh đồng Q2 design với quyết định khoa học

| Option | Điều kiện phân biệt / hard veto | Hiện tại và chi phí định tính |
|---|---|---|
| `KEEP` | Chỉ khi đã có source rights, sample/construct, full material parity, independent item gold+rater, shortcut controls, endpoint/threshold/admission hoàn tất trong prospective run được phép. | **NOT JUSTIFIED**; có lợi cho tính so sánh nhưng chi phí/nguồn quyền/nhân lực chưa biết. |
| `SIMPLIFY` | Chỉ khi xác định *trước outcome* được lỗi cục bộ và tiểu họ hẹp vẫn có khả năng bị bác bỏ, quyền và parity. | **NOT JUSTIFIED**; giảm độ phức tạp nhưng giảm ngoại suy, dễ selection bias. |
| `PIVOT` | Chỉ khi có chứng cứ construct hiện tại bất khả thi và **một** oracle/task khác hợp pháp, cùng ngân sách thông tin và được kiểm chứng; cần Question Gate mới khi đóng Q cũ. | **NOT JUSTIFIED**; đổi scientific target nên không claim trực tiếp comparable. |
| `STOP` | Cần bất khả thi dài hạn được **chứng minh** và không còn lựa chọn hợp pháp khả thi; thiếu bản ghi quyền không phải bất khả thi. | **NOT JUSTIFIED**; đóng hướng nếu rào cản không thể khắc phục, không phải Q4 FAIL model. |
| `HOLD_EVIDENCE_INSUFFICIENT` | Mọi hard veto chưa đạt đối với giai đoạn tương ứng (rights, source completeness, parity, rater, metric, custody, owner release). | **CURRENT EMPIRICAL DEFAULT**; bảo vệ validity, không chạy GPU, không tiến hành khoa học. |

**Precedence:** `HOLD` cho điều kiện chưa biết/veto; `STOP` cho bất khả thi vĩnh viễn đã chứng minh; `PIVOT` cần Q mới; `SIMPLIFY` chỉ trước outcome; `KEEP` chỉ sau chứng cứ được phép. **Không thể bù quyền dữ liệu hay parity bằng điểm số/MCDA**. [Report L36–48](https://github.com/minhtri22/TokenToModel-Lab/blob/8bf0601c716b5f6395e3b758ee066ff41c9a554d/docs/governance/ttm-post-q001/TTM_P0A_MEAS_Q001_Q2_FRAMEWORK_ALTERNATIVES_SOURCE_ONLY_REVIEW_20261115.md#L36-L48).

## 5. E0–E5: cần thiết nhưng hoàn toàn chưa được hiện thực hóa

| Minima | Bảo đảm tối thiểu / lỗ hổng phải khóa ở prospective protocol | Actual status |
|---|---|---|
| `E0_RIGHTS` | Quyền đọc, biến đổi, dùng làm gold và chia sẻ cho rater/API bên thứ ba; PII, giới hạn, retention/derivative permissions. Trước mọi source access. | `NOT_VERIFIED`; veto thực tế |
| `E1_CONSTRUCT` | Typed triple, reference time, source authority, bounded completeness, exclusive axiom nếu dùng FALSE và sampling frame/denominator để tránh chỉ chọn item dễ. | `NOT_AUTHORED_OR_VERIFIED` |
| `E2_EFFECTIVE_VIEWS` | Source bytes + builder/tokenizer/truncation + model-effective span và rater-effective payload; đối chiếu **toàn bộ fact đổi nhãn**, kể cả rater-only refutation, hidden oracle tách custody. | `NOT_CAPTURED` |
| `E3_SHORTCUT_CONTRAST` | Prospective controls fact-only vs cue-only, matched/counterbalanced nuisance, group split; metric theo unit/threshold, AD-06 nếu claim causal. | `NOT_EXECUTED` |
| `E4_RATER_AGREEMENT` | Same-task blind qualified raters, rubric, abstain, disagreement adjudication, source-semantic truth anchors chống common-mode. | `NOT_EXECUTED` |
| `E5_PREREG` | Primary metric, eligibility/coverage + rejection reason denominator, `UNKNOWN_VALID`, abstention, threshold, STOP, sample size/unit/CI-or-uncertainty, time/budget/cost ceilings và reviewer roles. | `NOT_FROZEN` |

Các mục trên là **loại chứng cứ tối thiểu**, không nói đã có corpus thật, quyền thực, bytes rater/checkpoint, sample size hoặc kết quả. Không tự tạo item/gold/prompt/scorer để “chứng minh” Q2. [Report L50–63](https://github.com/minhtri22/TokenToModel-Lab/blob/8bf0601c716b5f6395e3b758ee066ff41c9a554d/docs/governance/ttm-post-q001/TTM_P0A_MEAS_Q001_Q2_FRAMEWORK_ALTERNATIVES_SOURCE_ONLY_REVIEW_20261115.md#L50-L63).

## 6. Phân tích hard veto và thời điểm áp dụng

| Gate / thời điểm | Quy tắc bắt buộc | Disposition |
|---|---|---|
| Q2 giấy tờ | Q1 đã đăng ký, single relation, M0–M4 có phản chứng, 5 option + rights/cost/minima, QA độc lập. | **PASS_Q2_SOURCE_DESIGN_SCOPED** |
| Trước **source access** | `AD-01R`: quyền/PII/source use/third-party processing; thiếu quyền **HOLD_ACCESS**. | `HOLD_RIGHTS_NOT_VERIFIED` |
| Sau **lawful feasibility inspection**, trước **production authoring** | `AD-02` typed/time/source completeness, `AD-03` witness feasible, `AD-05` cue/leakage, `X14` visibility of exclusivity; `AD-06` nếu paired causal. Tránh đòi kiểm chứng completeness *trước khi có quyền xem bất kỳ nguồn nào*. | `NOT_VERIFIED`, F-M01 |
| Trước **fixture freeze** | `AD-01T` khi token-sensitive, exact builder/tokenizer/context effective bytes, `X13` full fact parity, `X15` deterministic item-reason precedence, `AD-07` prereg endpoint/threshold/sample/STOP. | `NOT_ADMITTED` |
| Trước **model inference/training** | `AD-00` exact source/runner, `AD-01C` checkpoint rights+byte custody, Q4 + owner science GO riêng, resource ceiling, sealed TEST/FINAL. | `NOT_AUTHORIZED` |
| Trước **scoring** | `AD-04` qualified independent same-task gold/rater calibration, blind and source-valid, no hidden gold to rater, recheck AD-03/05/06 and threshold lock. | `NOT_ADMITTED` |

**X15 canonical primary reason:** thiết kế hiện chỉ yêu cầu lưu tất cả item reasons + chọn primary theo thứ tự cố định trước freeze. **Chưa có mapping thứ tự mã thực hiện và chưa test runtime**; tuyệt đối không báo PASS_IMPL. Với W mất do truncation: gate `HOLD_PARITY_LOST_AFTER_TRUNCATION` và affected item `REJECT_PARITY/REJECT_MISSING_WITNESS` theo quy tắc đã khóa; không gán `UNKNOWN`. Khi một item có nhiều lỗi, record các nguyên nhân, fail-closed và chỉ chọn primary đã prereg. [Report L65–79](https://github.com/minhtri22/TokenToModel-Lab/blob/8bf0601c716b5f6395e3b758ee066ff41c9a554d/docs/governance/ttm-post-q001/TTM_P0A_MEAS_Q001_Q2_FRAMEWORK_ALTERNATIVES_SOURCE_ONLY_REVIEW_20261115.md#L65-L79).

## 7. N01–N12 và X13–X16 + phản ví dụ mới

**Tái dựng trên giấy:** 16/16 trường hợp `N01...N12`, `X13...X16` có expected disposition nhất quán trong report/JSON, **PASS_LOGICAL_ONLY**, không phải 16 runtime tests. Cụ thể N01/N02/N03/N12 từ chối missing/effective witness và hidden gold; N04 chỉ `UNKNOWN_VALID` khi nguồn đủ/đóng; N05 schema reject; N06/X14 không áp đặt location exclusivity; N07 chỉ conflict có axiom hiển thị; N08 AD06 nếu causal; N09 rights; N10 rater; N11 no science; X13 parity cả refuting facts; X15 gate HOLD + item REJECT; X16 design PASS có thể cùng empirical HOLD. [Report L81–102](https://github.com/minhtri22/TokenToModel-Lab/blob/8bf0601c716b5f6395e3b758ee066ff41c9a554d/docs/governance/ttm-post-q001/TTM_P0A_MEAS_Q001_Q2_FRAMEWORK_ALTERNATIVES_SOURCE_ONLY_REVIEW_20261115.md#L81-L102).

**Phản ví dụ bổ sung do reviewer xây dựng (lập luận logic, không tạo fixtures):**

- **X17 — Eligible-selection collapse:** 1.000 candidate triples, chỉ 5 dễ có witness được nhận, 995 bị REJECT => “đúng 5/5” không chứng minh construct khả dụng. Khóa sampling frame, coverage và reason-denominators; nếu không, HOLD trước freeze.
- **X18 — Common-mode rater error:** hai independent rater nhất trí cùng suy FALSE từ hai location khác nhau không có visible exclusivity axiom. Agreement cao nhưng sai semantics; source/ontology counter-adjudication phải bác bỏ claim PASS.
- **X19 — Temporal closure:** nguồn tuy nói đầy đủ nhưng chỉ phủ đến 09:00, triple reference_time=10:00; vắng chứng cứ không đủ tạo `UNKNOWN_VALID`; source completeness/time bound `NOT_PROVEN` => reject/HOLD.
- **X20 — Circular access:** stage buộc chứng minh source completeness/witness trước mọi source access, trong khi không thể đọc source cho đến khi có rights. Sửa cách mô tả gate: AD-01R trước access; AD-02/03/05 xác minh trong một phase **read-only lawful feasibility** được owner cho phép, rồi mới production authoring; không tạo micro-permit.
- **X21 — Multi-reason collision:** vừa thiếu decisive W sau truncation vừa unresolved referent; giữ cả hai reasons, gate HOLD nếu parity systemic, item REJECT theo fixed precedence; không chọn ngẫu nhiên primary, không `UNKNOWN`.

## 8. Các phát hiện độc lập và mức độ ảnh hưởng

| ID | Severity | Nguồn, phạm vi | Phản biện / yêu cầu đóng |
|---|---|---|---|
| **F-H01** | **HIGH — forward hard veto, không blocker Q2 paper** | [Q2 report L28, L55, L59](https://github.com/minhtri22/TokenToModel-Lab/blob/8bf0601c716b5f6395e3b758ee066ff41c9a554d/docs/governance/ttm-post-q001/TTM_P0A_MEAS_Q001_Q2_FRAMEWORK_ALTERNATIVES_SOURCE_ONLY_REVIEW_20261115.md#L24-L32); [Q1 L64–66](https://github.com/minhtri22/TokenToModel-Lab/blob/f31754c21b4e26f7d7a15e53096090f2fa9b5d87/docs/governance/ttm-post-q001/TTM_P0A_MEAS_Q001_REGISTERED_QUESTION_GATE_20261115.md#L62-L66) | M0 có nguy cơ tự đúng do chọn `ELIGIBLE` bằng witness; E5 chưa khóa tỷ lệ coverage và ngưỡng reject/abstain/UNKNOWN theo sampling frame. Phải khóa trước gold/fixture và không chọn mẫu sau outcome. |
| **F-M01** | **MEDIUM — gate timing clarification** | [Q2 report L69–73](https://github.com/minhtri22/TokenToModel-Lab/blob/8bf0601c716b5f6395e3b758ee066ff41c9a554d/docs/governance/ttm-post-q001/TTM_P0A_MEAS_Q001_Q2_FRAMEWORK_ALTERNATIVES_SOURCE_ONLY_REVIEW_20261115.md#L69-L73); [Q1 L70–74](https://github.com/minhtri22/TokenToModel-Lab/blob/f31754c21b4e26f7d7a15e53096090f2fa9b5d87/docs/governance/ttm-post-q001/TTM_P0A_MEAS_Q001_REGISTERED_QUESTION_GATE_20261115.md#L70-L74) | `BEFORE_SOURCE_ACCESS_OR_PRODUCTION_AUTHORING` gộp hai action khác nhau. AD-01R trước access; AD-02/03/05 trước production authoring, chỉ kiểm sau lawful inspection. Tránh circular admission. |
| **F-M02** | **MEDIUM — rater validity** | [Q2 report L32, L58, L73](https://github.com/minhtri22/TokenToModel-Lab/blob/8bf0601c716b5f6395e3b758ee066ff41c9a554d/docs/governance/ttm-post-q001/TTM_P0A_MEAS_Q001_Q2_FRAMEWORK_ALTERNATIVES_SOURCE_ONLY_REVIEW_20261115.md#L24-L32) | Agreement cùng task cần thiết nhưng chưa đủ cho correctness; thêm ontology/source-grounded adjudication và calibrate disjoint trước scoring, không dùng cùng rater để làm gold và tự kiểm. |
| **F-M03** | **MEDIUM — causal provenance** | [Q2 report L29, L56](https://github.com/minhtri22/TokenToModel-Lab/blob/8bf0601c716b5f6395e3b758ee066ff41c9a554d/docs/governance/ttm-post-q001/TTM_P0A_MEAS_Q001_Q2_FRAMEWORK_ALTERNATIVES_SOURCE_ONLY_REVIEW_20261115.md#L24-L30) | Visible witness cùng nhãn chưa chứng minh hidden key không tham gia dựng gold; yêu cầu rater blind rederive, provenance của gold process, hidden/oracle custody tách; source completeness vs truncation tách reasons. |
| **F-M04** | **MEDIUM — contrast identifiability** | [Q2 report L31, L57, L70–71](https://github.com/minhtri22/TokenToModel-Lab/blob/8bf0601c716b5f6395e3b758ee066ff41c9a554d/docs/governance/ttm-post-q001/TTM_P0A_MEAS_Q001_Q2_FRAMEWORK_ALTERNATIVES_SOURCE_ONLY_REVIEW_20261115.md#L24-L32) | Thay fact thật thường đổi token surface. “Keep nuisance fixed” phải hiểu matched/counterbalanced có check phân phối cue; causal claims cần AD-06 và negative cue-only control trước authoring. |
| **F-L01** | **LOW — documentary** | [Q2 report L57, L99–102](https://github.com/minhtri22/TokenToModel-Lab/blob/8bf0601c716b5f6395e3b758ee066ff41c9a554d/docs/governance/ttm-post-q001/TTM_P0A_MEAS_Q001_Q2_FRAMEWORK_ALTERNATIVES_SOURCE_ONLY_REVIEW_20261115.md#L50-L59) | “Preregged” là lỗi diễn đạt; X15 expected precedence vẫn là yêu cầu thiết kế, không được gắn PASS_IMPL. |

**Phân xử severity:** F-H01 là **hard veto cho tác nghiệp tương lai**, *không* phải thiếu bắt buộc của Q2 giấy tờ: Q2 minh thị E5 `NOT_FROZEN`, Q1 có kế hoạch `eligible_item_rate`, quy chế đòi threshold ở protocol sau. F-M01..04 yêu cầu làm rõ trước gold/scorer/authoring, không đòi tạo chúng tại Q2 (bị cấm). Không có finding nào chỉ ra pin sai, scope bị đổi, năm option thiếu điều kiện phân biệt hoặc Q2 falsely claims empirical PASS.

## 9. Quyết định và next single gate

- **Distinct reviewer status:** `PASS_Q2_SOURCE_DESIGN_SCOPED`; **raw bytes/Git pins:** `PASS_9_OF_9`; **16 source negatives:** `PASS_LOGICAL_ONLY`; **author tests:** `98/98 PASS_AUTHOR_ONLY`.
- **Owner decision:** `NOT_YET_MADE`; reviewer đề nghị `GO_ACCEPT_Q2_SOURCE_ONLY`, không tự quyết thay owner.
- `Q1_REGISTERED_ON_MAIN`; Q2 author source report đã được independent review (khi owner ký mới cập nhật Q2 admission); `Q3_NOT_EXECUTED`; `Q4_NOT_DECIDED`; `BENCHMARK_GOLD_NOT_VALIDATED`; `RIGHTS_NOT_VERIFIED`; `SCIENCE_HOLD`; `F0_F2_PAUSED`; `LINEAGE_UNCHANGED`.
- **One integrated forward requirement:** khi owner chuyển sang Q3/prospective protocol, gom F-H01/F-M01/F-M02/F-M03/F-M04 và X17–X21 vào **một** prospective admissibility design review, tuyệt đối không mở micro-permits hay tự tạo bộ dữ liệu/runner/nhánh.
- **Bước thực hiện tiếp theo — duy nhất:** `TTM_P0A_MEAS_Q2_OWNER_ADMISSION_AND_PR23_GOVERNANCE_CLOSURE_SINGLE_GATE` — owner chọn `GO_ACCEPT_Q2_SOURCE_ONLY` hoặc `HOLD_Q2_ADMISSION` trên exact PR #23; chỉ khi có quyền merge governance-only rõ ràng và HEAD không đổi mới xét merge và main readback. Không coi Q2 accepted là tự động Q3 hoặc science permit.
