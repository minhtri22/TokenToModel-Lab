# TTM Vector Memory V3 — Thiết kế PROBE mới cho Ambiguity, Unseen Paraphrase, Negation và Abstention

**Operation:** `TTM_VM_V3_NONORACLE_AMBIGUITY_AND_UNSEEN_PARAPHRASE_PREREG_DESIGN_ONLY`  
**Ngày:** 2026-11-12 · **Nhánh:** `research/ttm-vector-memory-architecture-20261111`  
**Trạng thái:** `DESIGN_CONTRACT_FROZEN_SCOPED` / `FULL_SCIENCE_PREREG_NOT_YET_FROZEN` / `SCIENCE_RELEASE=HOLD`.  
**Chỉ phạm vi thiết kế:** không viết generator/runner, không tạo PROBE, không lấy mẫu/chấm case V3, không inference, không huấn luyện, không TEST/GPU, không sửa `lineage.md` hoặc `main`.

## 1. Cơ sở đã biết và vấn đề chưa giải quyết

Tại L0020, Reader có cải thiện Answer-only NLL khi Oracle chọn chính xác card. L0021 cosine ranker trên key ngẫu nhiên thất bại với Recall@3 **107/128 = 83,59%** (ngưỡng 95%). L0022, v2 `R_HYBRID_LEX_FIRST` đạt Recall@1 **64/64 trên S2**, và Reader B1 có NLL bằng O1 từng truyện. Nhưng **64/64** dùng `LEXICAL_TRIGRAM`, **0** lượt cosine fallback và cơ chế yêu cầu **unique normalized three-attribute signature** với từ vựng đóng. L0022 chỉ chứng minh khớp mô tả có cấu trúc gần Oracle, không chứng minh khả năng từ chối, paraphrase mới hay diễn giải phủ định.

**Câu hỏi V3:** Khi câu hỏi không có đúng một card hợp lệ theo thông tin công khai — hoặc diễn đạt mới nằm ngoài bảng đồng nghĩa v2 — Retriever có biết **CHỌN ĐÚNG một card** hoặc **TỪ CHỐI (ABSTAIN)** một cách an toàn, thay vì ép lựa chọn hay lén dùng gold/Oracle?

**Định nghĩa không thể thay hậu nghiệm:**
- `SELECT(index)` hợp lệ chỉ nếu query có **đúng một** card phù hợp toàn bộ ràng buộc được quan sát, gồm nguồn (source provenance) và phủ định.
- `ABSTAIN` là hành động đúng nếu **0** hoặc **≥2** card phù hợp, query thiếu ràng buộc để phân định, có mâu thuẫn nội tại, hoặc mô tả ngoài từ điển không thể ánh xạ có căn cứ.
- **Không chấp nhận** “có gold target trong fixture nên cứ ép SELECT” ở các trường hợp không thể phân giải; chúng **không có target/answer hợp lệ**, và Reader không được nạp dữ liệu “đáp án đúng” cho negative cases.
- Thất bại POSITIVE: `SELECT_WRONG` hoặc `ABSTAIN` khi case có đúng một đáp án; thất bại NEGATIVE: bất kỳ `SELECT` nào (false selection). Số mẫu trong mẫu số cố định, không loại bỏ abstention.

## 2. PROBE V3 đề xuất: 256 trường hợp NON-TEST hoàn toàn mới

**Planned ID:** `TTM_VM_V3_NONTEST_256_NONORACLE_UNSEEN_AMBIGUITY_V1`. **Chưa có seed/hash dữ liệu thật**, vì không tạo fixture ở pha này. Dự kiến **8 strata × 32 câu**, mỗi câu 32 cards; 1 trong 4 strata dương tính kiểm kỹ thuật, 3 strata dương tính primary, 4 strata âm tính bảo đảm abstain. Khóa định danh V3 phải dùng namespace mới khác TRAIN/DEV/PROBE L0021/L0022 và không đọc TEST. Trước lần science, buộc kiểm quyền dữ liệu, uniqueness và hai nguồn sinh không trùng case/template.

| Stratum | n | Gold action | Tình huống và diễn giải |
|---|---:|---|---|
| `P0_KNOWN_WIRING` | 32 | `SELECT(unique)` | Ba thuộc tính trong dictionary v2, duy nhất; **engineering control**, không tính primary |
| `P1_UNSEEN_PARAPHRASE` | 32 | `SELECT(unique)` | Diễn đạt mới **ngoài bảng từ đồng nghĩa và surface templates v2**, nhưng hai người thẩm định độc lập nhất trí ánh xạ đến một card |
| `P2_PROVENANCE_UNIQUE` | 32 | `SELECT(unique)` | ≥2 card cùng mô tả, khác nguồn, query nêu **source_id** công khai để chọn một |
| `P3_NEGATION_UNIQUE` | 32 | `SELECT(unique)` | Câu hỏi có ràng buộc phủ định “không thuộc tính X/không nguồn Y”, sau loại trừ còn đúng một card |
| `N0_UNDERSPECIFIED` | 32 | `ABSTAIN` | Chỉ mô tả một/hai thuộc tính; **ít nhất hai** cards vẫn phù hợp, không có quy tắc chọn mặc định |
| `N1_DUPLICATE_MATCH` | 32 | `ABSTAIN` | Ít nhất hai cards cùng full tuple **và cùng provenance nếu được hỏi**, không đủ phân định |
| `N2_CONTRADICTORY_QUERY` | 32 | `ABSTAIN` | Một thuộc tính bị đòi hai giá trị loại trừ nhau, hoặc ràng buộc “X và không-X” |
| `N3_UNRESOLVABLE_OOV_OR_EXCLUSION` | 32 | `ABSTAIN` | Mô tả ngoài từ vựng không có ánh xạ được thẩm định, hoặc phủ định loại hết mọi candidate; không được đoán |

**Bắt buộc cho mọi stratum:** card bank size 32 cố định; key, source_id và retrieval_text không chứa target answer; value tách riêng khỏi Retriever và độc lập với source/position; card order xáo trộn theo seed đã khóa. Positive có đúng một gold target và một answer text để chấm Reader; negative chỉ có `gold_action=ABSTAIN`, `target_key=null`, `answer=null`, không tạo synthetic Oracle positive. Các cặp `correct/wrong_memory` chỉ dành positive, cùng keys/index/provenance/order, thay một target value; negative chỉ có index bank, không tạo “wrong target” tùy tiện.

**Nguồn paraphrase P1:** xây dựng *sau khi đóng băng protocol nhưng trước khi triển khai code đánh giá*; có danh sách văn bản/chú giải mới được hai người chấm độc lập xác nhận không cần nhìn response của Retriever, không sửa bản đồ synonym sau khi thấy thất bại. Nếu bất đồng hoặc không thể xác định ý nghĩa thì **HOLD_DATA_ADJUDICATION** trước source freeze, không lặng lẽ loại case sau đánh giá. Các thuộc tính thật sự mới không suy ra được chỉ bằng dữ liệu công khai phải chuyển N3, không ép chọn đáp án. “Unseen” chỉ có nghĩa **surface chưa xuất hiện trong bảng/template v2 đã khóa**, không ngầm khẳng định OOD tổng quát.

## 3. Baselines/ablation và hợp đồng Retriever V3

**Mỗi phương pháp phải được khóa nguồn trước khi xem PROBE V3**. V3 không có quyền lấy nhãn vàng để chuẩn hóa, sửa từ đồng nghĩa, chọn ngưỡng abstain, giải mã provenance hay thay đổi câu hỏi.

- `R_V2_FROZEN` — đối chứng negative/positive: v2 parser unique-triple + lexical-first giữ nguyên Git blob **`dc733eda42d768d695309e3a1d5df25aeabb28b7`**. Có thể abstain trên query P1/P3/P2; không được sửa sau khi xem V3.
- `R_V3_SYMBOLIC_PROVENANCE_NEGATION` — **primary candidate**: parser deterministic phải xử lý tính nhất quán ba thuộc tính, source_id, mệnh đề phủ định và `ABSTAIN` khi 0/≥2 candidates. Không dùng “một tuple khớp đầu tiên” hoặc tie-break key khi còn nhiều candidates ngang tiêu chuẩn. Tập từ vựng/grammar hỗ trợ P1 phải được đóng băng trước bằng annotation độc lập, không lấy nhãn PROBE lúc inference.
- `R_FROZEN_EMBEDDING_DIAGNOSTIC` — cosine mean embedding T1/P02 trên question và `retrieval_text`, chỉ để đo xếp hạng/candidate coverage, **không tự bypass safety gate**, không chọn threshold bằng PROBE. Không được gọi nó là semantic fallback đã được xác minh nếu chưa có evidence.
- `R_ORACLE_POSITIVE` — scorer-only upper bound cho các **positive** (chọn đúng một gold card), **không phải Retriever thật**. Negative không có Oracle answer; “Oracle abstain” chỉ là nhãn đánh giá.

**Indexer inputs duy nhất:** `question`, công khai `cards[].key`, `cards[].retrieval_text`, `cards[].source_id`, danh mục thuộc tính/từ vựng đã đăng ký; không đưa `answer`, `value`, `target_key`, `gold_action`, `wrong_memory`, `case_id`, `stratum` hoặc score vào API. Gold fields chỉ scorer đọc **sau** khi retriever trả action. Không cho stratum-specific shortcut dựa trên hidden label; nếu routing phải dựa vào syntax trong câu hỏi có thể quan sát.

**Abstain semantics:** kết quả chuẩn là `{status: SELECT|ABSTAIN, indices: []|[i], reason_code}`. Không bắt buộc calibrated probability (model v2 chưa có confidence calibration). `ABSTAIN` không bật Reader, không sinh văn bản được coi là trả lời; bên ngoài hiển thị “không đủ thông tin” (hoặc cần làm rõ) có ghi reason. Positive `ABSTAIN` được tính là miss khi chấm Retrieval; nếu báo cáo NLL trên positives thì nhánh B1/C1 dùng **frozen GPT bypass offline**, không chọn lọc bỏ các ca abstain. Negative không có answer token để chấm NLL; chỉ chấm hành động chọn/từ chối và reason-code.

**Bảo vệ leakage:** nhập dữ liệu `public_index` tách độc lập khỏi outcomes; kiểm card-order invariance, source conflict, synonym ambiguity, OOV, duplicate signatures, positive/negative switch, value-swap-blindness và mask=0 trên abstain; không dùng TEST, L0021 128, L0022 192 làm nguồn tuning. Đầu vào negative được đánh giá trước khi Reader inference, không tạo answer giả.

## 4. Định nghĩa chỉ tiêu và ngưỡng sàng lọc đề xuất

**Mẫu số cố định** (không tính P0 vào success gate):
- `POSITIVE_PRIMARY = P1 ∪ P2 ∪ P3`: **96** case. `CorrectSelectRate = #SELECT_CORRECT / 96`; `ABSTAIN` và `SELECT_WRONG` đều là thất bại.
- `NEGATIVE_PRIMARY = N0 ∪ N1 ∪ N2 ∪ N3`: **128** case. `CorrectAbstainRate = #ABSTAIN / 128`; mọi `SELECT` là false selection.
- **Ngưỡng dự kiến** `CorrectSelectRate ≥ 0.75` ⇒ **≥72/96**; riêng P1 unseen `CorrectSelect ≥ 20/32` để tránh P2/P3 che lấp sự yếu kém ở diễn đạt mới.
- `CorrectAbstainRate ≥ 0.95` ⇒ **≥122/128**, tối đa **6 false selections/128**. Các nhóm N0–N3 cần báo cáo riêng (không hợp nhất loại lỗi). Không đổi ngưỡng thành 100% sau khi thấy dữ liệu.
- **Đối chứng safety:** mọi attempt truy cập `answer/value/target_key/gold_action` từ ranker hoặc đưa Reader vào negative phải FAIL static/dynamic QA trước science.
- **Positive Reader, intention-to-treat n=96:** frozen `A` no-memory, `O1` oracle, `B1` selected correct-memory hoặc bypass nếu abstain, `C1` same rank/mask nhưng tráo value gold card (khi target không được chọn thì C1=B1). Tính **Answer-only NLL theo từng positive story, không loại abstentions**.
- `MeanStoryNLL(A)-MeanStoryNLL(B1) ≥0.05`, `MeanStoryNLL(C1)-MeanStoryNLL(B1) ≥0.05` và hai cận dưới paired-bootstrap percentile 95% `>0`, **2.000 draws ×96 stories**, seeds `20261120`/`20261121`. Oracle control `MeanNLL(A)-MeanNLL(O1) ≥0.05` để tránh báo nhầm domain shift. **Không chấm NLL trên negative.**
- Report diagnostics không thay primary: positive `SELECT_WRONG` vs `ABSTAIN` counts, selective precision, coverage, false-selection theo từng N-stratum, lý do từ chối, paired deltas theo stratum, CI Wilson 95% trên tỷ lệ, `cost=3 × false-selection-on-negative + 1 × missed-positive` (chỉ báo cáo), latency CPU, số lần dùng cosine, full explanation traces đã được lọc nhãn.

**Decision precedence prospective:**
1. Thiếu nguồn/quyền/custody, âm thầm đổi dữ liệu hoặc leakage → `HOLD_INVALID_EVIDENCE`.
2. Positive oracle control không đạt → `HOLD_READER_DOMAIN_SHIFT`.
3. `CorrectAbstainRate < .95` → **`FAIL_UNSAFE_SELECTION_SCOPED`**.
4. `CorrectSelectRate < .75` hoặc P1 unseen <20/32 → **`FAIL_UNSEEN_OR_COMPOSITIONAL_RETRIEVAL_SCOPED`**.
5. Retrieval đạt nhưng NLL paired/bootstrap không đạt → **`FAIL_FROZEN_READER_TRANSFER_SCOPED`**.
6. Tất cả đạt → **`GO_CANDIDATE_NONTEST_AMBIGUITY_SCOPED`** (vẫn không phải TEST PASS hay semantic retrieval generalization).

Ngưỡng trên được **khóa về ý định trong tài liệu DESIGN**, nhưng **chưa là tiền đăng ký thực thi hoàn tất**: chưa có generator source, quyền/receipt cho paraphrase ngoài từ vựng, dataset SHA256, retriever/scorer SHA, independent negative QA hoặc one-shot runtime. Không chạy inference trước khi đóng băng đủ các thành phần đó và có một quyết định owner GO/HOLD.

## 5. Thiết kế QA và điều kiện nguồn trước lượt chạy mới

**One packet source/prereg readiness** trong bước tương lai phải xây dựng generator và đối chiếu ở chế độ **schema-only**, không query retriever lên actual V3 cases và không chấm NLL. QA độc lập cần bao phủ:
1. 8×32 cases, 32 cards, negative không có answer và không có gold target; kiểm chính xác nhóm positive có một unique admissible target theo source/negation, nhóm negative 0 hoặc ≥2 candidate đúng theo policy.
2. Kiểm disjoint ID, template, alias và toàn bộ byte fixture so với nguồn cũ theo phạm vi truy cập hợp lệ; tuyệt đối không đọc sealed TEST. Ngăn dùng kết quả L0021/L0022 vào training, hyperparameter selection hoặc paraphrase dictionary.
3. Kiểm **hai reviewer** cho paraphrase, parse phủ định, source contradiction, duplicate full signature, missing attributes, OOV, item-order/card-value invariance, forced SELECT trên negative, reader no-forward khi abstain, zero-active mask. Không cho “gold target” xuất hiện trong query input.
4. Điểm QA source phải được ghi đủ PASS/FAIL; không tự động thay đổi seed, loại mẫu khó hoặc bật GPU để cứu kết quả.
5. Chỉ sau đó pin SHA256 của Reader/Checkpoint/T1 như L0022, source Git blobs, PROBE byte SHA, scorer Answer-only NLL, bootstrap, one-shot started marker **trước first scientific case**, separate private per-story/public aggregate, owner GO/HOLD một lần. Không micro-permit, không chạy lại dù lỗi sau marker.

**Giữ nguyên:** Reader L0020 SHA256 `c458de3afae87b3c381274b8edd698187df63ceac4dbbc0e6d8bd44b85c1632f`; P02 SHA256 `ee723407b2c25a18be20e26387a3dd8e4a18e2942d469279b6f0748ff86af0dc`; real T1 SHA256 `cba18e60cee3d08a353ee6d4a451017289e45af7b4b1179c87171b9b78d7dfdc`. **Không train, không mở TEST, không GPU.**

## 6. Phán quyết thiết kế

- `DESIGN_CONTRACT=FROZEN_SCOPED`; `PROBE_V3=NOT_GENERATED`; `V3_RETRIEVER=NOT_IMPLEMENTED`; `V3_SCORER=NOT_IMPLEMENTED`; `OWNER_CPU_RELEASE=HOLD`; `TEST=SEALED`; `MAIN=UNCHANGED`; `LINEAGE=L0022_UNCHANGED`.
- **Bước thực hiện tiếp theo:** `TTM_VM_V3_FRESH256_NEGATIVE_GROUND_TRUTH_AND_NONORACLE_SOURCE_ONEPACKET_QA_FREEZE` — triển khai generator và rubric annotation P1 unseen với reviewer độc lập, rà soát negative cases và source-only fail-closed QA, cố định seed/source/fixture SHA và owner GO/HOLD thiết kế trước khi xây science scorer; **chưa cho phép Reader inference**.
