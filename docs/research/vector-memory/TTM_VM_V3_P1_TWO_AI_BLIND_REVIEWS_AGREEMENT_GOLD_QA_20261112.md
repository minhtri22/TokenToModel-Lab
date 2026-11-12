# TTM Vector Memory V3 P1 — Đối chiếu hai ChatGPT AI Blind Raters (sau khi nhận đủ A và B)

**Operation:** `TTM_VM_V3_P1_TWO_CHATGPT_AI_RATER_RECEIPTS_INDEPENDENT_AGREEMENT_AND_CUSTODY_QA`  
**Ngày:** 12/11/2026; **scope:** post-blind evaluation, read-only science audit, no Reader inference.  
**Kết quả:** `PASS_AI_AGREEMENT_AND_P1_GOLD_32_OF_32_EXPLORATORY`  
**Human-review gate:** `HOLD_HUMAN_REVIEW_0_OF_2`; **CPU science:** `HOLD`.

## 1. Nguồn và SHA đã xác minh trực tiếp qua GitHub

- Agent A: `docs/research/vector-memory/P1_REVIEW_A_AI_UNVERIFIED.json`, Git blob `034d1511a2b971726b2607ba63f08e2be92682c3`, byte SHA256 **`46c9fad4b77065cf086213c64ee04145704efa8d6dd3cfbad56d80c9e1d68ed6`**, **184.616 bytes**.
- Agent B: `docs/research/vector-memory/P1_REVIEW_B_AI_UNVERIFIED.json` tại pinned commit `f518a6149e3514c5223002726d4805d715333112`, Git blob `be9c573ae480455e860d331f112e2b3f94c69036`, byte SHA256 **`fd719ada13d2e44a72d29af04d18bb5d839547b288046ce410cfa9e5b7e49cdf`**, **185.451 bytes**. Cùng Git blob còn tồn tại trên nhánh nghiên cứu khi kiểm tra.
- Both papers use exactly pinned fixture SHA256 `d473292d40dfb475d0b44f7d393341e19d846308820dcb4f5cbac6acb2c0e543`.
- Rater ids `CHATGPT_AI_RATER_A` và `CHATGPT_AI_RATER_B`, self-reported timestamps `2026-11-12T17:19:35+07:00` và `2026-11-12T17:23:02+07:00`. Timestamp/independence are **self-reported**, not cryptographically proven.

## 2. QA liên agent và từng JSON

| Điều kiện | A | B |
|---|---:|---:|
| Cases đầy đủ | 32/32 | 32/32 |
| Public index records | 1.024 | 1.024 |
| SELECT | 32 | 32 |
| ABSTAIN | 0 | 0 |
| Confidence=3 | 29 | 29 |
| Confidence=2 | 3 | 3 |
| Reason ≥8 ký tự | 32/32 | 32/32 |
| Mỗi `selected_key` nằm trong public index cùng case | 32/32 | 32/32 |
| Human attestation flags | **false/false** | **false/false** |

Cả 32 `case_id`, câu hỏi và nội dung/order `public_index` **giống nhau giữa A và B**, không có row/slot bị thêm trường. **Đồng thuận lựa chọn đúng từng case: 32/32 = 100%**, không có bất đồng. Hai agent tự khai không xem source, gold hoặc kết quả của người còn lại; không có independent access log chứng minh claim này.

## 3. Đối chiếu ground truth chỉ sau khi cả hai hoàn tất

Để tránh kiểm tra bằng câu trả lời do các agent tự báo, kiểm toán viên chạy riêng `v3_fresh256_fixture.py` gốc từ source Git blob **`5f51b8b464e54a370f3a3fa99d91307118f52f46`** và sử dụng `v3_p1_reviewer_custody.py` blob **`beaaa78126282439c94b2d0d525297e6b35266a5`**; xác minh source Git blob byte-exact và sinh đủ 256 fixture có SHA256 trùng **`d473292d40dfb475d0b44f7d393341e19d846308820dcb4f5cbac6acb2c0e543`** với receipt owner Windows.

Tính digest thứ cấp của toàn bộ 32 public case projections (case_id, public_index, question, JSON sort-key canonicalization, FNV1a-64) từ GitHub AI JSON và source fixture regenerated đều **`b57f314b7b872e9c`**. Đây là đối chiếu nội dung thứ cấp, **không phải SHA256 cryptographic** cho projection; thêm vào đó có SHA fixture toàn bộ đã khóa.

**Đối chiếu riêng từng lựa chọn AI với 32 private `target_key` sau chấm mù:** A **32/32 đúng**, B **32/32 đúng**. Chỉ **tổng số đúng** được công bố; không ghi private gold keys, answer, per-story data hay fixture trong báo cáo công khai. Kết quả không phải Reader NLL, Recall retrieval của code V3 hay TEST.

**QA receipt:** `artifacts/research/vector-memory/TTM_VM_V3_P1_TWO_AI_BLIND_RATER_AGREEMENT_AND_GOLD_QA_20261112.json` (**24/24 các điều kiện consistency/controls**); in-source policy and outcome comparison are separate from the agents' blind work.

## 4. Giới hạn khoa học và cổng phê duyệt

- Hai bài là **AI-assisted blind rating**, không phải **human independent blind rating**. Cả hai trường `attest_...` đều giữ `false`. Một code validator của human không thể biến chúng thành phiếu human signed mà không làm sai bằng chứng.
- **100% inter-AI agreement và 100% private-fixture match** chỉ chứng minh các agent đã ánh xạ đúng 32 paraphrase P1 của **fixture synthetic với public index**. V3 source đã biết bảng `PROPOSED_P1` trước khi chạy; không chứng minh khả năng tổng quát hóa cho paraphrase chưa khai báo, semantic retrieval ngoài từ vựng, bất đồng thật, hay độc lập giữa agent sessions bằng chứng mật mã.
- V3 scanner khoa học hiện chỉ có **draft mock QA 85/85** theo báo cáo trước đó. **Runner scorer v3 chưa có Git blob khóa trên nhánh**, chưa chạy native Windows QA và chưa được owner cấp GO. **CPU science tiếp tục HOLD**, dù AI labels khớp 32/32.
- Không sửa generator/retriever/Reader/source pins, không mở sealed TEST, không dùng GPU, không thêm L0023. `lineage.md` vẫn L0022, `main` không đổi.

## 5. Kết luận quản trị và lộ trình sau

**`AI_P1_AGREEMENT=PASS_32/32` · `AI_P1_GOLD=PASS_32/32` · `INPUT_INTEGRITY=PASS_SCOPED` · `HUMAN_REVIEW=HOLD_0/2` · `V3_CPU_SCIENCE=HOLD`.**

**Bước thực hiện tiếp theo (one packet):** `TTM_VM_V3_P1_HUMAN_GATE_OR_PROSPECTIVE_AI_AMENDMENT_AND_PINNED_SCORER_OWNER_GO_HOLD` — hai lựa chọn không được đánh đồng: (1) lấy **hai người thật** chấm độc lập theo rubric hiện hành; hoặc (2) owner thông qua sửa đổi tiền đăng ký **trước science** để dùng bằng chứng hai AI với nhãn đúng `EXPLORATORY_SCOPED_AI_REVIEW`, ghi rủi ro đồng thuận correlated AI. Đồng thời khóa scorer source Git SHA, native QA và owner one-shot fail-closed. Không được tự đổi cổng HUMAN thành PASS.
