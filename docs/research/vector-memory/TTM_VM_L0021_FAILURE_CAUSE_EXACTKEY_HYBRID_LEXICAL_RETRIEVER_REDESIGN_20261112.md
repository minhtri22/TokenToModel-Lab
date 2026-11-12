# TTM Vector Memory — L0021 failure-cause review và thiết kế lại Retriever NON-TEST v2

**Operation:** `TTM_VM_TOPK_FAILURE_CAUSE_AND_NEW_NONTEST_RETRIEVER_REDRAFT_DESIGN_ONLY`  
**Ngày:** 2026-11-12  
**Nhánh:** `research/ttm-vector-memory-architecture-20261111`  
**Trạng thái:** `DESIGN_ONLY_PASS_SCOPED` · `NEW_PROBE_NOT_GENERATED` · `INFERENCE_NOT_EXECUTED` · `TEST_SEALED`.  
**Phạm vi:** L0021 là một science FAIL có giá trị; không thay đổi phán quyết đó, không tái dùng PROBE 128 để chọn retriever, không huấn luyện Reader, không GPU, không sửa `main`.

## 1. Bằng chứng đã có — không thực hiện lại L0021

| Chỉ tiêu đã đo trên PROBE L0021 (128 câu; 32 cards/câu) | Số liệu |
|---|---:|
| Cosine full-question mean T1/P02 embedding vs key, Recall@1 | 43/128 = 33,59375% |
| Cosine, Recall@3 | 107/128 = 83,59375%, **FAIL** ngưỡng 95% |
| Lexical 3-gram (control only), Recall@1/@3 | 128/128 |
| NLL A no-memory | 6,9594914205 |
| NLL O1 Oracle singleton | 3,8215356842 |
| NLL B3 correct / C3 wrong | 4,5352914967 / 4,9566443991 |
| Paired delta A−B3 / C3−B3 | +2,4241999239 / +0,4213529024 |

Nguồn: `lineage.md` L0020/L0021 và `docs/research/vector-memory/TTM_VM_TOPK_NONTEST_CPU_ONESHOT_SCIENCE_ADJUDICATION_20261112.md`. Kết quả per-story đã được tính lại độc lập 22/22 QA; **lần thiết kế này chỉ đọc dữ liệu đã công bố, không tái chấm hoặc quét lại 128 PROBE**.

### 1.1 Đã chứng minh so với giả thuyết nguyên nhân

- **Quan sát đã xác lập:** Ranker cosine dựa trên mean embedding toàn câu không đưa đúng key vào Top3 ở 21/128 trường hợp. Khi target không nằm trong Top3, tráo target value không thay đổi NLL — nguyên nhân gần nhất của thất bại đạt ngưỡng Recall nằm **trước Reader**.
- **Quan sát đã xác lập:** 3-gram lexical tìm đúng 128/128 trên câu hỏi có **mã `obj...` xuất hiện nguyên văn**. Đây là khả năng khớp identifier; không chứng minh tìm kiếm ngữ nghĩa.
- **Giả thuyết chưa phân xử:** mean pooling câu hỏi làm loãng tín hiệu ID; tokenizer T1 BPE có thể biểu diễn tên ngẫu nhiên bằng nhiều subword; embedding P02 được học cho next-token LM chứ không phải metric key retrieval; bốn near-collision distractors gây khó với cosine. Không chọn một nguyên nhân trong các giả thuyết này nếu chưa có can thiệp trên dữ liệu mới.
- **Giới hạn kiến trúc đã biết:** Reader L0020 học với Oracle singleton, Query/Key projections frozen. Reader Top3 được cho nhiều bản ghi hoạt động là ngoài phân phối huấn luyện. Vì thế tách **retrieval hit** và **Reader NLL**; không khẳng định Reader đã học semantic key selection.

## 2. Hai mức mục tiêu tách biệt (không đánh tráo Oracle)

**G0 — Engineering identity lookup:** Khi question có mã `obj...` nguyên văn, exact-match bản ghi duy nhất là đường kỹ thuật đúng đắn. Nhưng đó là chức năng tương đương Oracle của L0020 trên fixture gốc, **không được coi là chứng cứ semantic retrieval mới**. PASS ở G0 chỉ là PASS nối dây (wiring).

**G1 — Retrieval beyond literal object key (primary scientific exploratory):** Query **không chứa `obj...`**; key private của memory card vẫn là `obj...`. Một trường `lookup_alias` hoặc `retrieval_text` mới cho phép tra cứu từ mô tả/định danh công khai, sau đó chuyển card gốc về **Reader L0020 không đổi**. Phải công bố rõ loại tín hiệu: alias exact-match là truy xuất từ điển; paraphrase description là truy xuất mô tả synthetic/template, không tự động đồng nghĩa semantic reasoning ngoài đời.

Mọi hàm `retrieve(question, indexed_card_fields)` **không nhận** answer, gold label, target_key, target index, wrong_memory, hoặc `answer_only_scoring`. Scorer chỉ được dùng target_key sau khi xếp hạng hoàn tất để tính hit. Bộ xếp hạng phải **không nhìn value**, và memory đúng/sai phải có cùng rank, index, mask.

## 3. Hợp đồng bộ dữ liệu mới — CHƯA SINH

**Tên đề xuất:** `TTM_VM_V2_NONTEST_NEW192_ID_ALIAS_DESC_20261112` (chỉ một ID dự kiến; chưa tạo run folder/marker). Tổng **192 cases**, chia ba tầng cố định, 64 mỗi tầng; mỗi tầng 16 nhãn đúng cân bằng 4 lần/nhãn; mỗi case 32 cards (1 target + 4 gần giống + 27 distractors), khóa mới, bố trí vị trí tráo ngẫu nhiên nhưng cố định theo seed. `wrong_memory` chỉ tráo value target; cùng lookup fields, keys, order, reader inputs khác mỗi value.

| Stratum | Query quan sát được | Trường index của card | Ý nghĩa |
|---|---|---|---|
| S0 `ID_LITERAL` (64) | Có một mã `obj...` nguyên văn | `key` | G0 wiring/exact-id control; **không đưa vào success primary** |
| S1 `ALIAS_LOOKUP` (64) | Có alias token định danh không phải `obj...` | `lookup_alias` → `key` | Bản đồ định danh/alias; kiểm tra uniqueness và abstain |
| S2 `DESC_PARAPHRASE` (64) | Mô tả thuộc tính được diễn đạt lại, **không chứa `obj...` hay alias** | `retrieval_text` → `key` | **Primary exploratory description retrieval** |

S2 có 3 thuộc tính độc lập được gán ngẫu nhiên cho mỗi bản ghi, xây dựng bằng vocabulary/template cố định **trước khi sinh PROBE**. Câu hỏi/paraphrase khác mặt chữ với canonical text nhưng có thể ánh xạ từ thông tin có sẵn. Hard negatives S2 giống target **2 trong 3** thuộc tính; không trùng cả 3. Nhãn answer phải độc lập thống kê với ID, alias, attributes và vị trí card. Không có lời gợi ý nhãn đáp án trong question, alias, `retrieval_text`, file name hay thứ tự.

**Bảo đảm không dùng dữ liệu cũ:** generator v2 phải dùng namespace/seed version riêng; so disjoint theo metadata hash/ID với nguồn public TRAIN 256, DEV 64, PROBE L0021 128, **không dùng các label/NLL/hit cũ để chọn tham số**. Không đọc sealed TEST để kiểm chéo. Khóa TEST vẫn niêm phong nên không thể tuyên bố đã kiểm trùng với nội dung TEST; dùng phân tách namespace theo thiết kế và ghi rõ giới hạn. Chỉ sinh dữ liệu sau khi source generator, quy tắc và checksum được đóng băng; không biến PROBE mới thành heldout confirmatory nếu seed/dataset công khai.

## 4. Các Retriever và đường Reader (khóa theo thiết kế)

**R_EXACT_ID (S0; G0 control):** Chuẩn hóa ASCII (case-insensitive nếu schema cho phép), tìm **đúng một** identifier khớp regex đã khai báo trong text query; tìm đúng một card có `key` trùng; 0 hoặc nhiều kết quả → `ABSTAIN`. Không silent fallback để cưỡng ép hit. Thuật toán này được gắn nhãn `ORACLE_EQUIVALENT_ON_LITERAL_ID` trên S0.

**R_EXACT_ALIAS (S1; G1 identity control):** Parser nhận alias *công khai trong query*, chuẩn hóa theo bảng quy tắc cố định và tìm đúng một card có `lookup_alias` trùng. Không đọc `target_key`. Missing/duplicate/ambiguous alias → `ABSTAIN`; không tìm trên answer.

**R_HYBRID_LEX_FIRST (S2; G1 primary):** Không sử dụng regex Oracle hay answer label. Tạo normalized character-trigram từ toàn câu hỏi và `retrieval_text` (có thể dùng từ vựng đồng nghĩa đã đăng ký trước làm một bảng canonicalization cố định, không train/tune). Rank bằng *overlap / number of trigrams của card text*; chỉ khi **toàn bộ** lexical scores = 0 mới fallback sang frozen cosine mean-T1/P02 embedding giữa **question và retrieval_text**. Tie-break theo tên key chuẩn hóa, không theo vị trí, không theo nhãn/answer. Chọn **Top1 làm primary** để phù hợp Reader singleton đã huấn luyện; Top3 diagnostic, không thay thế Top1 hậu nghiệm. Không dùng cosine trên `key` làm primary ở S2.

- Tất cả Retriever chạy chỉ trên fields đã cho phép: `question`, `key`, `lookup_alias`, `retrieval_text`; giá trị `value` bị loại khỏi index và rank. Rank được đóng băng trước khi tạo wrong-memory arm.
- Reader input được giữ **đúng định dạng L0020**: frozen T1 embedding của original `key` + original `value`; không đưa alias/descriptor vào Reader. Trường tra cứu mở rộng chỉ nằm ở Retriever. Đây là kiểm tra *Retriever mới + Reader cũ*, không thay Reader.
- No-memory A phải bit-exact GPT bypass; O1 Oracle upper bound chỉ là control, không tham gia primary selection. B1/C1 Top1 good/wrong; B3/C3 Top3 good/wrong chỉ diagnostic để phát hiện mismatch singleton/multirecord. Tất cả dùng cùng checkpoint và Reader SHA.

## 5. Tiêu chí quyết định đề xuất (prospective, chưa thực thi)

**Cổng G0 kỹ thuật:** S0 `R_EXACT_ID` uniqueness/abstain đúng, không sai key; không sử dụng mức 100% của L0021 làm kết quả mới.

**G1 chính trên S2 64 câu:**
1. `R_HYBRID_LEX_FIRST Recall@1 ≥ 0.90` (**≥58/64** hit) và `false-positive selection = 0` trên trường hợp cố ý ambiguous/missing-key; abstention phải được tính như miss thay vì bỏ mẫu.
2. `MeanStoryNLL(A)−MeanStoryNLL(B1) ≥ 0.05`; `MeanStoryNLL(C1)−MeanStoryNLL(B1) ≥ 0.05`; paired bootstrap percentile 95% lower `>0` cho cả hai (2.000 replicates, seeds 20261116 và 20261117; sampling theo story 64, không theo token).
3. O1 vs A phải cho cải thiện NLL ≥0.05 để Reader không bị domain-shift đến mức đối chứng dương không hoạt động. Nếu O1 không đạt → `HOLD_READER_QUERY_DOMAIN_SHIFT`, không được đổ toàn bộ lỗi cho Retriever.
4. Top3 Recall/NLL, S0/S1 Recall, coverage/abstain, lexical vs fallback share, conditional hit/miss NLL và latency CPU chỉ **diagnostics**; không được thay primary hoặc sửa threshold sau khi thấy dữ liệu.

**Decision precedence:** schema/leak/source failure → `HOLD_INVALID_EVIDENCE`; O1 domain-shift failure → `HOLD_READER_QUERY_DOMAIN_SHIFT`; S2 Recall@1 miss threshold → `FAIL_DESCRIPTION_RETRIEVAL_SCOPED`; Recall đạt nhưng NLL/CI fail → `FAIL_FROZEN_READER_TRANSFER_SCOPED`; tất cả điều kiện đạt → **`GO_CANDIDATE_NONTEST_DESCRIPTION_SCOPED`**. Không kết luận `TEST_PASS`. Chỉ tính FAIL/PASS sau khi có fixture, source/scorer/QA độc lập và one-shot receipt được khóa.

Ngưỡng trên là **hợp đồng đề xuất trong tài liệu thiết kế**. Chúng chưa phải một lần tiền đăng ký khoa học đầy đủ vì v2 generator, mô tả thuộc tính, random seed, output SHA và runner chưa được đóng băng/kiểm QA. Cấm chạy inference trước khi hoàn tất một lượt khóa nguồn, QA và GO/HOLD tích hợp.

## 6. Cấm leakage, post-hoc tuning và làm sạch

- Không mở/re-score PROBE L0021; không dùng `r1/r3`, answer-only NLL, source private per-story cũ làm tuning corpus. Chỉ sử dụng kết quả tổng hợp L0021 đã phân xử như lý do mở thiết kế mới.
- Không chạy optimizer, không retrain Reader hoặc frozen GPT; Reader L0020 SHA256 `c458de3afae87b3c381274b8edd698187df63ceac4dbbc0e6d8bd44b85c1632f`; checkpoint GPT SHA256 `ee723407b2c25a18be20e26387a3dd8e4a18e2942d469279b6f0748ff86af0dc`; T1 manifest SHA256 `cba18e60cee3d08a353ee6d4a451017289e45af7b4b1179c87171b9b78d7dfdc`.
- Test code nguồn và fixtures bằng dữ liệu tổng hợp khác với PROBE dự kiến; negative QA gồm missing/duplicate alias, ambiguous descriptions, case/order invariance, value/answer blindness, wrong-key attack, mask Top1/3, no-memory bypass. Không infer Reader thật trong DESIGN_ONLY.
- Các tệp mới phải ở project `D:\WORK\RESEARCH\TokenToModel-Lab`; không ghi vào Downloads ổ C, không đụng `main`, không sửa append-only `lineage.md` vì chưa có kết quả khoa học v2.

## 7. Phán quyết thiết kế và bước sau

**`DESIGN_ONLY_PASS_SCOPED`** cho chiến lược hai tầng, **`NEW_PROBE=NOT_GENERATED`**, **`NEW_RETRIEVER=NOT_IMPLEMENTED_OR_TESTED`**, **`READER_UNCHANGED`**, **`SCIENCE=NOT_EXECUTED`**, **`TEST=SEALED`**, **`GPU=NO`**, **`LINEAGE=L0021_UNCHANGED`**.

**Bước thực hiện tiếp theo:** `TTM_VM_V2_NEW_NONTEST_FIXTURE_RETRIEVER_SOURCE_ONEPACKET_QA_AND_PREREG_FREEZE` — xây dựng nguồn fixture 192 mới, Retriever parser/lexical/fallback trên fields đã khóa, fail-closed QA source/negative và freeze full source/seed/hash + owner single GO/HOLD; **chưa có quyền chạy Reader inference trong bước này**.
