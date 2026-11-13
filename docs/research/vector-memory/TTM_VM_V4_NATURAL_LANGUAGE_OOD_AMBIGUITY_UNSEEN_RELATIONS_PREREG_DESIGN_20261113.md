# TTM Vector Memory V4 — Natural Language OOD, Unseen Relations & Ambiguity: Thiết kế tiền đăng ký

**Operation:** `TTM_VM_V4_NATURAL_LANGUAGE_OOD_AMBIGUITY_UNSEEN_RELATIONS_PREREG_DESIGN_ONLY`  
**Ngày:** 2026-11-13 · **Repository/branch:** `minhtri22/TokenToModel-Lab` / `research/ttm-vector-memory-architecture-20261111`.  
**Kết luận thiết kế:** `V4_DESIGN_CONTRACT_FROZEN_SCOPED` · `V4_COMPLETE_EXECUTABLE_PREREG=NOT_FROZEN` · `V4_CPU_SCIENCE=HOLD`.  
**Tuyệt đối không ở bước này:** sinh CAL/PROBE, trích xuất ngữ liệu thực, gọi Retriever/Reader, train hoặc chọn threshold, mở TEST, dùng GPU, cập nhật `lineage.md`/main hoặc chạy lại one-shot cũ.

## 1. Nền tảng khoa học và ranh giới kết luận

Nguồn đóng băng trước thiết kế: L0021 cosine mean T1/P02 **FAIL_RETRIEVAL_SCOPED**; L0022 V2 **PASS_NONTEST_S2_CLOSED_VOCAB_DESCRIPTION_SCREEN_SCOPED**; L0023 V3 **PASS_NONTEST_V3_SYNTHETIC_AMBIGUITY_EXPLORATORY_SCOPED**, xác nhận có kiểm toán độc lập 73/73 nhưng **có giới hạn**. V3 đã xử lý đúng `96/96` positive primary và `128/128` negative, Reader có NLL(A)−NLL(B1) `+3.0569320867`. Tuy nhiên:
- Cụm từ P1 của V3 **đã được lập trình trong từ điển của Retriever V3**, chỉ mới so với V2; thành công này không chứng minh hiểu diễn đạt chưa biết.
- V3 là **rule-based symbolic lookup** trên dữ liệu tổng hợp cùng họ với generator; không phải semantic retrieval có khả năng mở rộng.
- Per-story V3 ghi cờ `hit1` nhưng **không ghi selected index/key**: QA chỉ đối chiếu cờ và đường source tính đúng, chưa đối chiếu từng lựa chọn thô.
- Hai người chấm thực tế là hai **ChatGPT AI rater**, do owner solo chấp nhận sau khi có chấm AI nhưng trước science. Đây là **`AI_ASSISTED_EXPLORATORY_SCOPED`**, không được viết là human-independent.

**Câu hỏi V4:** Với truy vấn tự nhiên **không có template/từ đồng nghĩa/mẫu quan hệ trong candidate code**, Retriever có thể chọn đúng một chứng cứ duy nhất và từ chối khi **không thể xác định duy nhất**, đồng thời vượt được baseline lexical ở mức rủi ro chọn bừa cố định hay không? Reader L0020 đóng băng có còn hưởng lợi khi dùng memory được chọn thật trên truy vấn khó hơn không?

“**Out-of-grammar (OOD)**” trong V4 nghĩa là **surface form, quan hệ diễn đạt và ngữ cảnh không được đưa vào grammar/template/keyword maps đã khóa của Retriever**, được kiểm tra bằng rà soát tĩnh + tác giả/AI annotator độc lập; **không** chứng minh ngoài phân phối huấn luyện (pretraining distribution) của một encoder đông cứng. Không được gọi là OOD nếu chỉ thay ID/seed hoặc bổ sung synonym trong candidate. Việc candidate có thể thất bại là outcome hợp lệ.

## 2. Tách phát triển và kiểm định — không tái dùng PROBE cũ

Dự kiến hai phân hoạch **mới** tách rời theo **nguồn tài liệu, thực thể, phong cách tác giả và family paraphrase**, không chỉ seed/row:
- `V4_CAL64`: **8 strata × 8 = 64** case, `P0=8` engineering control, `P1/P2/P3=24` primary positives, `N0/N1/N2/N3=32` primary negatives. Chỉ để chọn **một threshold abstention** cho mỗi baseline/candidate theo thuật toán cố định. Không train weights, đổi grammar hay sửa embedding trên CAL.
- `V4_PROBE256`: **8 strata × 32 = 256** case, `P0=32` control, `P1/P2/P3=96` primary positives, `N0/N1/N2/N3=128` primary negatives. **Một lần** chạy kết quả khoa học sau khi nguồn/candidate/threshold được khóa. Cấm dùng V1–V3 DEV/PROBE hoặc sealed TEST làm CAL.

| Stratum | CAL | PROBE | Nhãn đúng | Thử thách |
|---|---:|---:|---|---|
| `P0_SEEN_WIRING_CONTROL` | 8 | 32 | `SELECT` | Mô tả grammar quen thuộc, chứng cứ duy nhất, **không vào primary**; control chống lỗi wiring |
| `P1_UNSEEN_NL_PARAPHRASE` | 8 | 32 | `SELECT` | Câu diễn đạt tự nhiên không được thêm trước vào từ điển/template candidate, có một chứng cứ |
| `P2_CROSS_SENTENCE_RELATION` | 8 | 32 | `SELECT` | Đại từ, quan hệ qua hai câu, hai thực thể cùng xuất hiện nhưng chỉ một thỏa quan hệ |
| `P3_PROVENANCE_TEMPORAL` | 8 | 32 | `SELECT` | Nguồn/thời gian nêu trong chứng cứ phải phân giải đúng, không chỉ token giống nhau |
| `N0_RELATION_UNDERSPECIFIED` | 8 | 32 | `ABSTAIN` | Đề cập đúng các thực thể nhưng thiếu liên kết để chọn duy nhất (≥2 ứng viên) |
| `N1_CONFLICTING_EVIDENCE` | 8 | 32 | `ABSTAIN` | Hai chứng cứ tin cậy ngang nhau đối nghịch, chưa có quy tắc ưu tiên nguồn đăng ký |
| `N2_FALSE_PREMISE_NO_SUPPORT` | 8 | 32 | `ABSTAIN` | Câu hỏi có tiền đề không được bất cứ nguồn nào xác nhận, không được đoán |
| `N3_NEAR_DUPLICATE_AMBIGUOUS` | 8 | 32 | `ABSTAIN` | Hai chứng cứ gần trùng về chữ nhưng khác quan hệ/scope; không phân giải được chắc chắn |

**32 cards/case** cho cả hai split; public fields `key, source_id, retrieval_text, optional timestamp` (timestamp chỉ khi thực sự thuộc chứng cứ). Giữ **cùng ngân hàng card/order** cho mọi phương pháp. Private fields `gold_action, target_key|null, evidence_support_set, answer|null, correct_memory, wrong_memory` **không** có trong API Retriever. Negative **không** có valid answer/target, không Reader NLL. Positive có đúng **một gold key** với chứng cứ căn cứ rõ; value để Reader chấm dùng **cùng domain tag** với L0020 nhằm giảm domain shift ngoài retrieval, độc lập với key, source và card order. Không đưa answer tag vào public question/retrieval_text. `SELECT` phải trả đúng một index; `ABSTAIN` zero index, `reason_code` rõ ràng.

**Không đưa raw V4 PROBE cho owner để lựa chọn ngưỡng/đổi grammar.** Owner quản lý SHA và mở dữ liệu đúng luồng sau freeze; evaluator và author có tách phạm vi truy cập. Nếu source family không thể giữ tách độc lập với CAL, **HOLD_CROSS_SPLIT_CONTAMINATION**.

## 3. Quyền nguồn, cách tác giả độc lập và custody annotation

Hai tuyến nguồn có thể dùng **sau khi chốt chính thức nguồn**: (a) văn bản **owner-authored** mới viết tự nhiên, có provenance owner; (b) đoạn ngắn từ tài liệu **được cho phép sử dụng**, có URL/tác giả/license/retrieval time và xác nhận quyền (không xem quyền là mặc định chỉ vì xem được web). Không truy cập trang/file có PII nhạy cảm, không chép văn bản bị hạn chế; nếu chưa giải quyết quyền thì **HOLD_SOURCE_RIGHTS**. Nếu chỉ có owner-authored, kết luận chỉ là **naturalistic authored**, **không quảng bá external-world/general web retrieval**. Không cần tải dữ liệu trong pha DESIGN.

- **Trình tự chống rò rỉ:** (1) khóa candidate source, checkpoint, vocab, tokenizer, prompts, grammar, embedding model, baseline definitions; (2) tạo `CAL64` với nguồn tách family, thẩm định nhãn, chỉ chọn threshold; (3) **khóa threshold và mã score + hash CAL**; (4) tác giả độc lập biên soạn/khóa `PROBE256` không được xem diagnostics/results của CAL ngoài schema; (5) hai AI blind raters A/B chấm *trực tiếp câu hỏi/public index* mà không biết kết quả ranker; (6) đối chiếu gold và giải quyết tranh chấp **trước** dispatch; (7) private PROBE byte SHA, source hashes, reviewer receipts, one-shot marker; (8) chỉ owner release single GO/HOLD và khoa học riêng.
- Do owner là nhà nghiên cứu solo: cho phép **hai AI ở hai phiên tách biệt** làm `INDEPENDENT_AI_ASSISTED_BLIND_REVIEW` theo chính sách V3 đã được owner chấp nhận cho nghiên cứu nội bộ. Ghi session/model/timestamp/hash và **tính độc lập chỉ self-reported**, không tự xưng human; không để agent được truy cập candidate, generator, gold, Review của agent kia. Có thể dùng **reviewer AI thứ ba** cho tranh chấp, cũng ghi kết quả, chưa được thay nhãn tự động.
- **Gold adjudication prior to PROBE science:** với positive, A/B xác nhận duy nhất key dựa trên evidence; với negative, cả hai đồng ý không có key hợp lệ/không phân giải và có `reason`. Nếu bất đồng, **HOLD_ANNOTATION_DISPUTE**, cho phép adjudication blind độc lập trước khi chạy; không được tự loại case khó, sửa cấu trúc cho phù hợp candidate hay nhìn kết quả ranker rồi sửa gold.
- Khóa danh sách `unsupported`, `conflicted`, `ambiguous` bằng tiêu chí logic riêng. Một số câu hỏi có đáp án trong tri thức thế giới nhưng không trong evidence **phải ABSTAIN**, không được dùng kiến thức bên ngoài public index.
- Kiểm ngăn rò rỉ: biên soạn độc lập, no source→gold side channels, no token aliases cho target, no duplicate near-exact templates qua CAL/PROBE hoặc V3; chưa biết overlap với TEST vì **không mở sealed TEST** — chỉ kiểm namespace/hợp đồng nguồn mà không đọc TEST.

## 4. Đối chứng và điều kiện công bằng (fairness)

| Track | Vai trò | Nguồn |
|---|---|---|
| `R_V3_FROZEN_SYMBOLIC` | Di sản/negative control, **không được sửa parser/lexicon** | Frozen V3 blob `68bfeaaf1d0acf0cf446e4d734e34368fbf8f702` |
| `R_BM25_LEXICAL` | Baseline chính không vector | Cài đặt/tokenization, stopwords, IDF và params **phải pin trước CAL** |
| `R_CHAR3GRAM_LEXICAL` | Robust lexical đối với lỗi bề mặt | Unicode normalization, n-gram, length norm **phải pin trước CAL** |
| `R_T1_MEAN_COSINE` | Baseline frozen embedding mang tính diagnostic | T1/P02 pins L0023; không retrain |
| `R_V4_SEMANTIC_CANDIDATE` | **Ứng viên chính**, có quyền FAIL hoặc ABSTAIN | **Chưa chọn model/weights/architecture/license** ở pha DESIGN; phải pin SHA và CPU reproducibility trước CAL |
| `R_ORACLE_SCORER_ONLY` | Positive Reader control, **không phải Retriever** | Private gold chỉ scorer đọc sau chọn |

**Phân biệt semantic track:** nếu V4 candidate vẫn chỉ thêm từ đồng nghĩa/regex vào grammar cũ, thí nghiệm phải được đổi tên `LEXICAL_RULE_EXTENSION` và **không được kết luận learned semantic retrieval**. Nếu chưa có một semantic candidate đông cứng hợp lệ, `HOLD_SEMANTIC_CANDIDATE_UNPINNED`, không âm thầm chọn model khác sau CAL. Có thể chấm riêng diagnostic baselines trong một hợp đồng khác, không tiêu thụ V4 PROBE để cứu thiết kế.

**Information parity:** mọi track chỉ nhận `question`, public cards, cùng 32 cards, cùng document span & max context size, cùng thứ tự/ngẫu nhiên đã khóa; không nhìn `gold, answer, case_id, stratum, private values`. Nếu encoder cần chunking hoặc truncation, pin quy tắc và kiểm truncation tương đương trước PROBE. Tất cả encoder chạy trên CPU FP32 theo pin tài nguyên; không download model trong one-shot. Không cho baseline lexical đặc quyền dictionary từ PROBE; candidate không truy cập source files ngoài index.

**CAL64 threshold algorithm, đóng băng ngay ở thiết kế:** mỗi phương pháp score toàn bộ CAL với mapping action `SELECT/ABSTAIN`. Candidate/baselines được phép **chọn đúng một threshold trên CAL**, cố định danh sách candidate thresholds và tie-break trước CAL; chọn threshold đáp ứng **≤1 false SELECT trong 32 negatives CAL**, sau đó tối đa hóa `CorrectSelect` trên 24 positive primary CAL; tie → **coverage thấp hơn → threshold chặt hơn**. Nếu không có threshold hợp lệ phải có tùy chọn **always-abstain**, được tính vào denominator (không lược bỏ). Freeze threshold receipt SHA trước khi tạo PROBE. `R_V3_FROZEN` dùng chính sách cố định; không tune. **Baseline comparator `B_CAL_BEST` được chọn trên CAL** từ BM25, char3gram và T1 cosine bằng tiêu chí này, tie theo thứ tự BM25 > CHAR3GRAM > T1. Không chọn baseline tốt nhất hậu nghiệm từ PROBE. Mọi baseline khác vẫn báo cáo công khai.

## 5. Tiêu chí khoa học đề xuất và ngưỡng khóa ở mức DESIGN

**Số mẫu:** P1+P2+P3 = **96 primary positives**; N0+N1+N2+N3 = **128 primary negatives**. P0=32 control không tham gia primary. **Không** loại cases miss, abstain, OOV hoặc conflict khỏi mẫu số. Chuẩn hóa case theo source cluster, không coi 32 distractors là 32 samples độc lập.

**Primary safety:** `CorrectAbstainRate = #ABSTAIN /128 ≥120/128 =93.75%` (**≤8 false selects**), báo cáo Wilson 95% từng nhóm, false-select N1/N2 riêng. Chặn unsafe selection ưu tiên hơn mọi gain về NLL.

**Primary retrieval:** `CorrectSelectRate = #SELECT_RIGHT/96 ≥60/96 =62.5%`; P1≥18/32, P2≥16/32, P3≥16/32. Positive abstain và wrong selection đều tính miss. Các ngưỡng được **đề xuất/frozen trong DESIGN**, nhưng chưa đủ điều kiện được chạy khoa học; chỉ được thay bằng sửa đổi công khai trước khi có CAL/PROBE.

**Incremental semantic gain:** `CorrectSelect(V4)-CorrectSelect(B_CAL_BEST) ≥10/96` (**ít nhất 10 case khác biệt**) trên cùng PROBE và dưới **cùng safety gate**. Paired bootstrap percentile 95% lower của `1[correct_V4]-1[correct_B]` **>0** (2.000 draws, prospective seed `20261125`). Nếu V4 không phải semantic candidate thực, không cấp semantic gain claim ngay cả khi thắng lexical.

**Reader/transfer secondary co-gates:** dùng **exact frozen Reader L0020** và backbone P02 để phân biệt hiệu quả truy xuất với khả năng đọc. Positive intention-to-treat **96** stories với arms:
- `A` bypass no-memory; `O1` scorer-only Oracle singleton; `B1` candidate selected singleton (kể cả chọn sai), nếu abstain dùng bypass; `C1` cùng selection/mask, thay *value của gold target* trong private memory; nếu gold không nằm trong lựa chọn thì `C1=B1`; không dùng NLL negative.
- Mean paired story `NLL(A)-NLL(B1)≥0.05`, `NLL(C1)-NLL(B1)≥0.05`, hai paired-bootstrap 95% lower >0 (2.000 draws, seeds `20261126`/`20261127`), Oracle gain `NLL(A)-NLL(O1)≥0.05`. Frozen tags/answer tokenization phải tương thích với reader cũ; nếu Oracle control FAIL → **HOLD_READER_DOMAIN_SHIFT**, không ép báo retrieval FAIL.
- Báo cáo đầy đủ `coverage`, `selective precision`, `false-selection`, `correct-abstain`, `B1/O1 gap`, pairwise difference versus every baseline, `latency`, memory/CPU, strata, 95% Wilson CIs, distribution answer token count. Nếu người dùng muốn so sánh với V3, **không dùng chênh lệch raw 100% V3–V4 như đánh giá thay đổi thuật toán** vì tập và định nghĩa khác.

**Decision precedence single gate (future, not now):**
1. `HOLD_INVALID_PROVENANCE_RIGHTS_OR_CUSTODY` khi nguồn, license, QA, independent review, pinned SHA hoặc anti-leakage không đủ; `HOLD_SEMANTIC_CANDIDATE_UNPINNED` nếu chưa khóa mô hình ứng viên.
2. `HOLD_BASELINE_CALIBRATION_OR_SPLIT_INVALID` nếu threshold không khóa trước PROBE, so sánh không cùng ngân sách hoặc có overlap.
3. `HOLD_READER_DOMAIN_SHIFT` khi Oracle control <0.05.
4. `FAIL_UNSAFE_FALSE_SELECTION_SCOPED` nếu correct-abstain <120/128.
5. `FAIL_OOD_RETRIEVAL_SCOPED` nếu correct-select <60/96 hoặc P1<18/P2<16/P3<16.
6. `FAIL_NO_INCREMENTAL_SEMANTIC_GAIN_SCOPED` nếu <10/96 gain so với CAL-best hoặc paired CI lower ≤0.
7. `FAIL_FROZEN_READER_TRANSFER_SCOPED` nếu hai deltas/CI không đạt.
8. `GO_CANDIDATE_V4_NONTEST_NL_OOD_SCOPED` nếu **tất cả** đạt; vẫn không phải TEST/external-world generalization.

V4 phải chấp nhận một kết quả **FAIL/HOLD** đúng quy trình; không được nới ngưỡng, thêm từ đồng nghĩa, sửa nguồn hoặc chạy lại sau khi thấy PROBE.

## 6. Evidence integrity, QA và ranh giới mở khóa

**Trước bất kỳ SCIENCE:** source/rights manifest, author/reviewer custody, danh mục CAL/PROBE family disjoint, exact model+tokenizer+indexer hashes, ứng viên và tất cả baselines, CAL thresholds+SHA, private PROBE bytes SHA, seed, sample units, writer/reader bounds, no overwrite, CPU budget/capacity, code-only + independent negative QA, one-shot fail-closed marker **trước case đầu tiên**, một owner GO/HOLD.

**Khắc phục thiếu sót V3 về evidence:** private per-story V4 bắt buộc lưu `case_id, stratum, public_index_sha256, gold_action, gold_target_key|null, selected_key|null, selected_index|null, status, reason_code, evidence_support_key_hashes, score/threshold, method/branch, Reader_forward_count, arm_nll, answer_tokens` và `decision_trace_sha256`. Không đưa private key/gold vào GitHub; public aggregate chỉ số liệu và hashes. Independent QA phải tính lại 256 action decisions từ **selected_key thật** đối chiếu private gold/evidence, không chỉ dựa `correct_select`. Native raw file SHA và hậu kiểm Reader/checkpoint byte SHA từ chủ máy phải được gửi; nếu thiếu → **HOLD_INDEPENDENT_TRACE_CUSTODY**, không nâng lên adjudication không điều kiện.

**Mỗi group/case QA cần test:** same-author document paraphrase leakage, key/answer/position side channel, source-time contradiction, zero/≥2 gold candidates, true relation vs merely overlapping tokens, cross-split document-source-group contamination, review A/B disagreement/abstention, value-swap blindness, null answer on negative, SELECT exactly one, ABSTAIN zero mask/zero Reader forward, score threshold precommit, no TEST access, no old one-shot regeneration. Chỉ source/mock test trên riêng handcrafted mock; **không gọi phương pháp trên actual V4 PROBE trước scientific marker**.

**Pha này tuyệt đối:** `DATA_FILES=0`, `MODEL_CANDIDATE=UNPINNED`, `THRESHOLDS=DESIGN_ALGORITHM_ONLY`, `CAL=NOT_GENERATED`, `PROBE=NOT_GENERATED`, `QA=DESIGN_STATIC_ONLY`, `SCIENCE=NOT_EXECUTED`; giữ frozen Reader/backbone và các cổng khoa học lịch sử L0021/L0022/L0023. Không cần micro-permits, một owner GO/HOLD sau khi source readiness tích hợp đạt QA.

## 7. Bước thực hiện tiếp theo

`TTM_VM_V4_CAL64_PROBE256_SOURCE_RIGHTS_ANNOTATION_CANDIDATE_PIN_AND_INTEGRATED_SOURCE_QA_ONEPACKET`: tìm/soạn nguồn đủ quyền, chốt tính độc lập của tác giả/AI reviewer, khóa ứng viên semantic model và fair lexical/embedding baseline, rồi CAL threshold và PROBE fixture theo đúng thứ tự trên. **Chỉ source/custody/QA chuẩn bị**, không chạy frozen Reader, không mở sealed TEST, không dùng GPU, không thay lineage/main.

**Design adjudication:** `PASS_V4_DESIGN_CONTRACT_SCOPED`; `SCIENCE_RELEASE=HOLD_NO_PINNED_MODEL_CAL_PROBE_REVIEW_RIGHTS`.
