# TTM-P0A-MEAS-Q001 — Question Gate Q1 chính thức, đo lường source-visible gold

**Policy:** [TTM-GOV-QF-20261115-V1](../TTM_QUESTION_FIRST_RESEARCH_ARCHITECTURE_LINEAGE_AND_MAIN_POLICY_20261115.md).  
**QuestionID (NEW):** `TTM-P0A-MEAS-Q001` · **Type:** `MEASUREMENT` · **Programme:** TTM-Small-4M P0-A `MEASUREMENT/GOLD`.  
**Q1 status upon governance-only merge to main:** `Q1_QUESTION_REGISTERED`; Q2/Q3 for this **new** question `NOT_EXECUTED`; Q4 `NOT_DECIDED`.  
**Owner decision:** `GO_REGISTER_Q1_SCOPED`, explicitly given 2026-11-15 in conversation: “Tôi quyết định GO_REGISTER_Q1_SCOPED cho TTM P0-A. Thực hiện một lượt đăng ký Question Gate trên main theo policy, giữ nguyên tất cả science/rights/gold/runner HOLD; kiểm tra điều kiện bắt buộc, không mở micro-permit và không tự cho phép merge implementation.”  
**Owner role:** project owner (human). **Design reviewer:** distinct ChatGPT AI source/design reviewer; human/organizational independence `NOT_EXTERNALLY_ATTESTED`.  
**Q1 implement/science authority:** `NO`; no research/implementation branch, benchmark, gold, scorer or model run permitted.

## A. Q1 — Một câu hỏi quyết định

**Câu hỏi duy nhất, có thể trả lời/bác bỏ:** *Trong một họ assertion nguyên tử `LOCATED_AT(entity_id, location_id, reference_time_id)` với thời điểm/định danh được khai báo tường minh, liệu có thể xác lập một phương pháp đo lường phân biệt `TRUE/FALSE/UNKNOWN` hợp lệ với item phải loại do thiếu witness/ontology/parity, bảo đảm mọi chứng cứ làm thay đổi nhãn đều còn trong ngữ cảnh mô hình thực nhận sau tạo prompt/tokenization/truncation và được phép xuất hiện trong dữ liệu rater nhìn thấy, để đưa ra quyết định `KEEP/SIMPLIFY/PIVOT/STOP/HOLD` theo điều kiện đã khai báo trước hay không?*

**Scope:** một triple địa điểm theo thời điểm tường minh; không dùng implicit time, multi-hop, goal, event transition, nested coreference, Long-CoT, mô hình lớn, bài toán OOD khác, hoặc mô hình đã trained như đối chứng khoa học mới. `P0-B` không tự mở.

**Why:** T4 đạt NLL scope đã khóa nhưng FRESH16/FC01 cho thấy điểm fact adherence khác; chưa thể nhận diện lỗi model khi gold bị khuất, ontology nhập nhằng hoặc rater lệch miền thông tin. Do đó measurement validity là prerequisite, **không phải** nguyên nhân đã được chứng minh.

**Quyết định bị ảnh hưởng:** sau chứng cứ triển khai *được owner cấp riêng*, chọn `KEEP` hợp đồng này, `SIMPLIFY` một tiểu họ được chỉ ra trước kết quả, `PIVOT` sang construct/oracle hợp pháp khác bằng Q riêng, `STOP` khi bất khả thi chứng minh được và không có đường hợp lệ, hoặc `HOLD_EVIDENCE_INSUFFICIENT` mặc định. Q1 chưa chọn KEEP hay bất kỳ scientific disposition nào.

### A.1 Exact provenance, không hồi tố

- **main trước đăng ký:** `3e6db6056dbc79747766bcdfa7cf2ce634ff6cf7` — GitHub [pinned baseline](https://github.com/minhtri22/TokenToModel-Lab/commit/3e6db6056dbc79747766bcdfa7cf2ce634ff6cf7). **Question registration commit:** `READ_FROM_GITHUB_POST_MERGE` (không tự tham chiếu SHA).
- **Exact independently reviewed source/design candidate:** `a8fd21f35d56a87f869df673b318d437ed0c8b31`; reviewed [candidate](https://github.com/minhtri22/TokenToModel-Lab/commit/a8fd21f35d56a87f869df673b318d437ed0c8b31) với 10 Git blobs và 12 logic challenges + X13–X16.
- **Original HOLD candidate:** `f3225f4f2cbc48ef15cdbc92cf5c050c78f4fa1a`; original reviewer report local bytes chưa được archive trên GitHub.
- **Evidence-publication PR head before registration:** `f128af5f6bbdcd6f7ab9c5e9c7026707d4df8552` — original 10 reviewed source/design blobs preserved; 2 reviewer deliverables archived byte-exact.
- **Independent report:** [Markdown](TTM_P0A_Q1_AMENDED_DISTINCT_REVIEW_20261115.md), Git blob `38d009fa3cdc36db847565520307a8ff05d4c8c3`, raw SHA-256 `755efd1b49385a996ae03d2d264897576c91df3dbbe8d890046fb0765dea01a4`.
- **Independent receipt:** [JSON](../../../artifacts/governance/ttm-post-q001/TTM_P0A_Q1_AMENDED_DISTINCT_REVIEW_RECEIPT_20261115.json), Git blob `203c4b0f84536e96921edc42bd30717357201535`, raw SHA-256 `8a94ace8f0bc74d8c07944afbf1b2bd0099b792c7d7ea9776dafe40440fdf886`.
- **Original source/contract exact:** [revised design](TTM_P0A_MEASUREMENT_GOLD_PROSPECTIVE_QUESTION_CANDIDATE_20261115.md) blob `22f7382dc7a76f3cbcbe695d700cb9111c246f60`; [revised JSON](../../../artifacts/governance/ttm-post-q001/TTM_P0A_OWNER_SELECTION_AND_SOURCE_ONLY_DESIGN_CONTRACT_20261115.json) blob `24c35ec70236fa64ff14488bf32189c81782faa6`.
- **Scientific history:** `lineage.md` Git blob `3409e036241deb1da6674619a2abc834bea8a2d6` on `3e6db6056dbc79747766bcdfa7cf2ce634ff6cf7`. FRESH16, T4 TEST64, FINAL24/72 historical results remain scoped and sealed; **NO replay**. `Q001=Q4_CLOSED_HOLD_NEW_SCIENCE` historical; P0-A is a **new QuestionID**.

**Implementation HEAD:** `NOT_APPLICABLE_NO_IMPLEMENTATION_IN_Q1`; no new runner/commit. Historical T4 code/checkpoint references remain source history, not instantiated/authorized baseline for a new measurement protocol. **Checkpoint bytes/rights:** `NOT_VERIFIED`.

**OBSERVED:** Q001 root cause not identified; independent design source review `PASS_Q1_DESIGN_SCOPE` on exact HEAD; 3 HIGH design fixes scoped; 12/12 symbolic negatives; source SHA pins and owner GO to register Q1.  
**INFERRED:** hidden-only gold, incomplete evidence, lexical shortcut or evaluator bias *could* distort interpretation; none proven causal.  
**UNKNOWN:** rights to underlying dataset, viability of the single atomic family from permitted source, item-level witness; complete effective information parity; source-aware gold, independent rater calibration, sample/threshold and real runtime custody.

## B. Q2 — Phương pháp, giả thuyết và lựa chọn (CHƯA THỰC HIỆN)

**Framework thích hợp:** `5W1H` cho ai được thấy nguồn nào; `construct validity` cho semantics `TRUE/FALSE/UNKNOWN` và item admissions; `falsification` cho cơ chế M0–M4; `failure-mode / hard-veto analysis` cho hidden gold/truncation/rater bias; `decision-tree` thay MCDA giả tạo. Việc đăng ký mô tả framework dự kiến, **không đánh dấu Q2 đã thực hiện**, không đo bằng chứng mới.

**Các cơ chế cạnh tranh, chưa có kết luận:**
- `M0_VISIBLE_CONSTRUCT`: Nhãn được chứng minh từ source-visible facts; phản chứng nếu một eligible item không suy ra được truth theo hợp đồng đã nêu hoặc witness sai miền.
- `M1_HIDDEN_ONLY`: Gold bị ràng buộc vào `E_core` hay hidden key; phản chứng nếu mọi label thực tế truy ra được từ model/rater-visible data sau truncation.
- `M2_AMBIGUITY`: Time/referent/ontology không đủ để gán nhãn; phản chứng bằng giải tham chiếu nhất quán từ cùng evidence mà không buộc binary trong trường hợp UNKNOWN.
- `M3_SHORTCUT`: Lexical/position/verbosity shortcut điều khiển score; phản chứng bằng đối chứng semantic thay fact nhưng giữ cues và kiểm tra rater evidence parity.
- `M4_RATER`: Lỗi/bias của người chấm độc lập với model; phản chứng bằng independent same-task blind raters, cùng packet và rubric được khóa. S1/S2 khác task không phải agreement.

**Các cơ chế có thể cùng đúng; không giả định một root cause duy nhất.** Chưa có yêu cầu tác nghiệp hoặc khoa học nào ở Q2 từ Q1 này.

### B.1 Các lựa chọn và điều kiện

| Option | Chứng cứ tối thiểu có thể làm thay đổi quyết định | Hard veto và giới hạn hiện hành |
|---|---|---|
| `KEEP` | Phép đo prospective đã cấp quyền, quyền nguồn, witness, đầy đủ material-fact parity, independent gold/rater, kiểm shortcut, ngưỡng/endpoint prereg đều đạt | **NOT_DEMONSTRATED**; Q1 registration không tương đương KEEP |
| `SIMPLIFY` | Một lỗi ở tiểu họ được xác định **trước outcomes**, có cách giới hạn hợp pháp và duy trì parity | NOT_DEMONSTRATED; không tùy ý sửa ontology sau khi biết scores |
| `PIVOT` | Proven structural infeasibility của family hiện hành và phương án oracle khác có quyền, thông tin tương đương | NOT_DEMONSTRATED; cần owner/new Q cho hướng thay |
| `STOP` | Bất khả thi chứng minh được và không có phương án hợp pháp | NOT_DEMONSTRATED; thiếu rights record đơn thuần chỉ HOLD |
| `HOLD_EVIDENCE_INSUFFICIENT` | Bất kỳ quyền, witness, parity, gold/rater, prereg threshold hoặc custody chưa đạt | **CURRENT_DEFAULT** đối với triển khai/benchmark/science |

**Necessity:** Đo đúng fact là điều kiện tiên quyết để luận giải model. **Discriminating value:** source parity có thể phân biệt gold/rater artifact với kết quả model nhưng không tự cô lập data/objective/capacity. **Implementation fitness:** chưa chứng minh có source có quyền và field mapping. **Cost/feasibility:** current Q1 governance-only, `0` GPU/model runs, không tạo item; chi phí/giới hạn prospective empirical work `NOT_ESTIMATED` và không thể tự cấp budget. Không dùng điểm MCDA vì thiếu dữ liệu.

## C. Q3 — Chứng cứ tối thiểu/negative controls/stop rules (CHƯA THỰC HIỆN cho Q mới)

**Minimum discriminating evidence:** bản thiết kế item-level `LOCATED_AT` với typed/time referents; chứng minh nguồn/rights; provenance của *material fact set* model-effective sau builder/tokenizer/truncation so với rater-effective; truth label theo item admission riêng; một kế hoạch đánh giá independent rater cùng task; shortcut controls và giới hạn ontology. **Chưa sản xuất bất kỳ item/gold/fixture nào.**

**Planned measurements (NOT_PREREGISTERED):** `eligible_item_rate`, `source_visible_witness_and_full_material_fact_parity_rate`, `independent_same_task_agreement`, `ambiguous_or_missing_witness_rejection_rate`, `shortcut_error_rate`. `PRIMARY_ENDPOINT=NOT_FROZEN`, `ACCEPTANCE_THRESHOLD=NOT_FROZEN`, `SAMPLE_SIZE=NOT_SET`, `CI/POWER=NOT_DESIGNED`; trước bất kỳ authoring/scoring phải có prospective owner-admitted protocol. **Q1 registration threshold:** valid QuestionID + single falsifiable construct + 5 distinct decisions/hard veto + independent scoped source/design PASS + owner GO, not a scientific threshold.

**Source/rights/PII/secret custody:** `AD-01R=NOT_VERIFIED`, before any source use/authoring; `AD-01T=NOT_VERIFIED`, before token-sensitive freeze; `AD-01C=NOT_VERIFIED`, before model execution. Model/checkpoint data `PRIVATE_UNACCESSED`. Any source exposure to third-party rater requires separate rights proof. No new dataset, rights, API call or model inference.

**Ordered admission and hard veto (no step may be moved later):**
1. `BEFORE_SOURCE_ACCESS_OR_AUTHORING`: rights AD-01R and PII; typed construct AD-02; AD-03 planned source-visible gold/witness, AD-05 lexical/leakage controls; AD-06 only when matched causal contrasts are proposed, with one-variable pairing; **X14** location exclusivity must be explicitly justified in visible ontology, never infer false/conflict from two locations alone.
2. `BEFORE_FIXTURE_FREEZE`: source/item evidence witness, exact source/tokenizer/renderer and model-effective context; AD-01T if tokenizer-sensitive; AD-07 endpoint/rubric/threshold/stop rule prospectively locked; **X13** parity of the *complete label-changing fact set* rather than one common W, including rater-only refutations; **X15** canonical precedence **gate `HOLD_PARITY_LOST_AFTER_TRUNCATION`** and affected **item `REJECT_PARITY`** (or `REJECT_MISSING_WITNESS` when claimant TRUE/FALSE has missing decisive proof) — *both recorded, never `UNKNOWN`*. A conflict of reject codes must preserve all reasons and choose primary reason deterministically before production.
3. `BEFORE_MODEL_EXECUTION`: AD-00 source/run exact pins, AD-01C byte custody, checkpoint rights and **separate owner GO after Q4**, no permit implied by registration.
4. `BEFORE_SCORING`: AD-04 independently adjudicated same-task gold and rater competence; AD-03/05/06 parity/negative rechecks; locked threshold and no hidden gold leakage. `X16`: Q1 design PASS can coexist with all runtime admission gates still HOLD.

**Negative symbolic cases:** N01–N12 and X13–X16 are [in the independent review](TTM_P0A_Q1_AMENDED_DISTINCT_REVIEW_20261115.md); `PASS_LOGICAL` describes review on paper, not runtime pass. **No 85/85 author QA -> science PASS transfer.**

**Stop rules:** `HOLD_RIGHTS` before source access; `HOLD_INVALID_CONSTRUCT` on ambiguity/non-unique labels; `HOLD_HIDDEN_GOLD` if gold only in hidden source; `HOLD_EVIDENCE_PARITY` on full material-fact disagreement; `HOLD_PARITY_LOST_AFTER_TRUNCATION` if model window loses decisive W; `HOLD_RATER_COMPETENCE` for unresolved same-task disagreements; `HOLD_NOT_PREREGISTERED` if metric/threshold/sample still unfrozen; `HOLD_NO_SCIENCE_PERMIT` before new model run. Item reject codes **do not** silently become UNKNOWN or science FAIL. All unverified conditions are hard veto for relevant phase, **not** reasons to block abstract Q1 registration.

**Review state:** independent design `PASS_Q1_DESIGN_SCOPE` at `a8fd21f35d56a87f869df673b318d437ed0c8b31`; human organizational independence `NOT_EXTERNALLY_ATTESTED`; actual science adjudication `NOT_EXECUTED`. A later Q3 for this registered QuestionID must be separately performed; the earlier AI design review **must not be reclassified as Q3_ANSWER_REVIEWED of this new gate**.

**Budget:** current registration/docs-only write, no model or data execution; future compute/storage/rater/rights budget `NOT_AUTHORIZED/NOT_FROZEN`, must be justified under the one eventual integrated Q gate before any research branch.

## D. Q4 — Không có câu trả lời hay owner closure về câu hỏi khoa học này

**New question:** `Q1_QUESTION_REGISTERED` *upon verified main merge*, `Q2_NOT_EXECUTED`, `Q3_NOT_EXECUTED_FOR_THIS_QUESTION`, `Q4_NOT_DECIDED`; `QUESTION_OPEN`, **not** `CLOSED_GO_SCOPED` and not `GO_SCOPED_IMPLEMENT`.  
**Owner decision already made:** `GO_REGISTER_Q1_SCOPED` for **registration only**, not scientific conclusion.  
**Implementation HEAD:** `NOT_APPLICABLE_NO_BRANCH` (registration does not create implementation).  
**Final science merge decision:** `NOT_APPLICABLE_NOT_AT_I4`; **registration PR's merge** permitted only if entire changed-file diff is `docs/governance/` or `artifacts/governance/` and main/lineage safety checks pass; this is NOT implementation merge.  
**Scientific lineage entry:** `NO`.  
**Active gate:** register only `TTM-P0A-MEAS-Q001`; no active second research question.  
**New owner science permission:** `NO` by default.

## Bước thực hiện tiếp theo — duy nhất (sau Q1 main readback)

`TTM_P0A_MEAS_Q2_FRAMEWORK_ALTERNATIVES_SOURCE_ONLY_SINGLE_GATE`

One design/source-only pass on the **already registered Q1**: assess M0–M4, hard-veto decision tree and minimal prospective measurement evidence, estimate/qualify missing rights and resource requirements without accessing private source or authoring gold. Follow Question-First Q2→Q3→Q4; no micro-permits and no autonomous model/benchmark execution.
