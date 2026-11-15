# TTM-Small-4M — SM4M-F2: Pre-execution Admission, Score & Custody Matrix

**Operation:** TTM_SMALL4M_F2_PROSPECTIVE_MEASUREMENT_PREEXEC_INTEGRATED_DESIGN_SINGLE_GATE  
**Phụ thuộc:** `06_SM4M_F2_PROSPECTIVE_MEASUREMENT_PREEXEC_INTEGRATED_PROTOCOL_20261115.md`; owner design closure commit `c233dff20b9b020aefd732ce62bfa2e7aebd3985`; MD1 original commit `33021a421f05bb3bfa0999ad12bc3bd144366da9`.  
**Current:** tất cả điều kiện runtime/gold `NOT_EXECUTED/NOT_VERIFIED`, mọi nhãn PASS bên dưới đều là **điều kiện dự kiến**, không là kết quả hiện có.

## 1. Ma trận cổng admission tích hợp (fail closed)

| ID | Input / yêu cầu định lượng | Evidence/receipt cần có trước khi chạy | Gate lúc soạn |
|---|---|---|---|
| G00_SOURCE | Candidate/MD1/owner closure exact SHA, unchanged F0/F1/F2 and source rubric | Git compare, original blob pin, source readback | `DESIGN_SOURCE_REFERENCED; PREEXEC_NOT_VERIFIED` |
| G01_RIGHTS | Mọi nguồn câu chữ là rights-clear, PII-screened, provenance-per-item; private gold licensed | Per-core source/rights register, independent rights/privacy attestation | `NOT_AUTHORED` |
| G02_NONOVERLAP | 72 new cores across all sets, no overlap with TRAIN/VAL/TEST/old FINAL or M1 plan | Exact SHA normalized bytes, similarity and semantic checks, bounded accessible corpus scope declared | `NOT_VERIFIED` |
| G03_M0_MD1 | 32×2=64, 4×8, 111/000; original gates sens/spec≥28/32 and agreement≥0.85 | Original MD1 byte pin + independent source QA | `DESIGN_ONLY; NO_ITEMS` |
| G04_M0X_GOLD | 16 cores×8 patterns=128, balanced each pattern16, axis pos/neg64 each; matched edge64/axis | Pre-authored gold manifest, independent single-axis semantic isolation review per edge | `CANDIDATE_DESIGN_ONLY` |
| G05_M0U_GOLD | 24 cores×1, 8 target UNKNOWN/axis; two other axes determinable | Independent source/gold adjudication + exclusion/invalid policy pre-frozen | `CANDIDATE_DESIGN_ONLY` |
| G06_ANTI_SHORTCUT | Label/style/length/word/position/stratum/proxy controls fail prespecified shortcut gates | Nuisance-only proxy feature set, negative-control performance and frozen thresholds | `NOT_SPEC_FROZEN/NOT_RUN` |
| G07_THRESHOLDS | M0 original untouched; M0X/M0U new candidate thresholds independent-reviewed **before data authoring** | Versioned prereg amendment, owner signature/decision, exact scorer spec | `NOT_FROZEN_EXTENSION` |
| G08_BLIND | Two distinct raters same item IDs, independent contexts, randomization/permutation custody | Sealed blind-map commitment, role separation, receipt of no leakage and fixed instructions | `NOT_ASSIGNED` |
| G09_SCORER | Correct per-axis matrices and paired-edge aggregation, missing/invalid fail closed | Independent frozen checker, negative tests incl. swaps/duplicates, source SHA | `NOT_IMPLEMENTED` |
| G10_CUSTODY | Private immutable gold/item/rater SHA; public only non-reversible metadata commitment | HMAC/manifest/immutable commitment and custody attestations after bytes exist | `NOT_CREATED` |
| G11_RESOURCE | No GPU/model required for calibration; if external AI raters, approved tool/data processing and budget | Rater/API license, rights, retention, access and budget attestation | `NOT_AUTHORIZED` |
| G12_OWNER | Independent design review, exact-admission packet and one owner GO/HOLD | Report, JSON receipt, owner decision before any data creation, scoring or dispatch | `HOLD_OWNER_EXECUTION_NOT_GRANTED` |

**Aggregate rule:** Nếu bất kỳ G00–G12 chưa PASS bằng nguồn đúng hoặc chưa có bằng chứng thích hợp, `PREEXEC_BLOCK=TRUE`; không chuyển source-only PASS thành rights/custody/science PASS. Lượt hiện tại chỉ đánh giá thiết kế, không tự biến giấy tờ thành frozen admission.

## 2. Mẫu schema tương lai (contract shape only — không phải dữ liệu hiện có)

Private `core_manifest` sau này phải có: `study_id, set_id, stratum, core_id, source_rights_ref, source_sha256, overlap_scope, story_fact_claims, tokenizer_pin`.  
Private `item_manifest` sau này phải có: `item_id, core_id, condition_pattern, actor_gold, object_gold, goal_gold, unscorable_axis, intended_single_axis_flip, counterpart_ids, length_bucket, prompt_sha256, text_sha256, gold_reviewers, adjudication_state`.  
Private `blind_map`: `opaque_id, item_id, order_index, rater_packet_id, custodian_signature, commitment_sha256`.  
Score rows: `rater_id, opaque_id, actor_score, object_score, goal_score, rubric_version, response_sha256, timestamp_or_session_record, invalid_reason`.  
Source receipt: `frozen_input_manifest_root, gold_manifest_root, protocol_sha256, scorer_sha256, rater_packet_sha256, raw_score_root, blind_map_commitment, rights_attestation, independent_qa_receipt`.

Tất cả ở trên là **schema trường dự kiến**, không phải chứng từ tồn tại. Raw text/gold/reidentification/AES/private HMAC keys không được đẩy GitHub. Public receipt chỉ chứa commitments không làm lộ tài liệu ngắn; nếu plain SHA của prompt dễ đoán gây rủi ro, sử dụng SHA của encrypted manifest/secret-key HMAC theo contract độc lập duyệt, ghi rõ giả định bảo mật. Không tự sinh keys tại design gate.

## 3. Scoring policy & handling

**M0:** two raters ×64 items×3 axis =384 axis ratings; six 2×2 matrices; per-axis/rater TP,FN,TN,FP totals 64. No NaN/null/duplicate ID, no silent denominator change. `TP≥28` and `TN≥28`. Raw exact agreement proposed `matches≥55/64`. Nếu công thức chưa được owner phê duyệt, HOLD không chấm.

**M0X:** two raters ×128 items×3 axis =768 axis ratings; each rater per axis positive64/negative64; exact agreement candidate ≥109/128; per-axis sensitivity/specificity candidate ≥56/64; paired-edge candidate 56/64 *full edge validity* per axis/rater. **Không tự freeze các ngưỡng đề xuất hoặc tự coi 16 cores là đủ power confirmatory**; phải review prospectively và ghi rationale. Một matched edge đúng nếu target flip được nhận diện đúng ở hai endpoints **và** hai axes bất biến được chấm đúng ở cả hai endpoints. Một item tham gia nhiều edge có tương quan; báo core-cluster n=16 và không giả định 64 edge pairs độc lập.

**M0U:** two raters ×24 items×3 axis =144 ternary ratings; target axis gold UNKNOWN 8/axis; candidate targeted abstention ≥7/8 per axis/rater; non-target axis binary accuracy và false-certainty must be prereg separately. `UNKNOWN` phải là nhãn explicit chứ không là missing score, không tính chung với âm tính.

**Gold invalid or semantic coupling:** chặn từ admission trước khi chạy. Nếu phát hiện sau score freeze phải báo `HOLD_UNDERMINED_CONSTRUCT`; không loại mẫu để làm đẹp kết quả. Nếu bất kỳ rater reply thiếu ID/lộ nhãn/retry adaptive → `HOLD_INPUT_INTEGRITY`; keep immutable negative receipt; không đếm PASS.

**Báo cáo cuối nếu sau này được phép:** từng axis ×rater matrices, exact edge/same-core paired results, unknown confusion, partial patterns and source/rights/strata, proxy baselines, agreement, uncertainties by independent core. Lưu cả negative controls và các trường hợp FAIL; đo trên model-like natural continuations vẫn là một vấn đề riêng chưa được admission.

## 4. Cấu trúc QA âm tính bắt buộc trước dữ liệu

Reviewer tương lai cần duyệt test cases **thuần schema/spec, không tạo science item** cho các tình huống:
- Nhãn gold `111/000` dùng nhầm thành bằng chứng phân biệt từng trục → phải reject.
- Tráo actor but changes goal semantics; pattern nhìn hợp lệ nhưng construct fails → reject.
- Hai arms cùng score mean khác nhau? A/C delta0 bị gọi absolute0 → reject.
- Nhầm 48 continuations với 144 independent cases → reject.
- Hai rater score các item set khác nhau → reject.
- Duplicate opaque IDs, missing axis, invalid/NaN, bad parser, denominator 63/64 hoặc 127/128 → HOLD.
- Rater dùng label/order/length/style để đạt candidate threshold → `HOLD_SHORTCUT`.
- Gold do AI nhưng ghi HUMAN_VERIFIED hoặc thiếu quyền → HOLD.
- Leak M1/FINAL/old TEST into M0 calibration → HOLD.
- Owner approved design closure bị diễn giải thành GO_EXECUTION/GPU/model → reject.

Các trường hợp này là danh sách QA phải thiết kế/triển khai và khóa riêng trong pre-exec gate tương lai; **chưa test run**.

## 5. Ranh giới, provenance và thứ tự quản trị

- M0-ORIGINAL thuộc MD1: giữ nguyên 64 items/28/32/0.85. M0X và M0U chỉ là **proposed extension inside F2**. Không đổi MD1 gốc, không lấy thresholds extension từ MD1 như đã prereg.
- Không tự chạy teacher-forced/oracle-foil M3, 16 M1 cores×4 variants, H0/H1 checkpoints, Colab, T4; không dùng old 24 FINAL.
- F0/F1 outcomes giữ nguyên, prior reviewer F01/F04 CLOSED_DESIGN nhưng **execution-admission chưa được thực hiện**. F3/F4 NOT_OPENED. Global lineage chưa append do PR20 Draft có L0029; không tự cấp ID trùng.
- EmbeddingGemma 2, Vector Memory và T5/T6 tiếp tục độc lập; kết quả cross-program không dùng làm Small-4M science.
- Author-only design QA không thay independent review; khi reviewer thẩm định bản thiết kế này, trả `GO_DESIGN_SCOPED` / `HOLD_REVISE_DESIGN` với exact HEAD. Chỉ owner mới có quyền một quyết định tiếp; không mở micro-permits.

**Current terminal:** `AUTHOR_DESIGN_SCOPED · ALL_EXECUTION_GATES_UNVERIFIED · SCIENCE_HOLD · NO_GPU · NO_INFERENCE · F3/F4_NOT_OPENED`.
