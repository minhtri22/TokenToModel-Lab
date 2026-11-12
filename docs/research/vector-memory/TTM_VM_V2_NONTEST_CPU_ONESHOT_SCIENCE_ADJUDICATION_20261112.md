# TTM Vector Memory V2 — Phân xử độc lập CPU one-shot 192 NON-TEST

**Operation:** `TTM_VM_V2_NONTEST_CPU_ONE_SHOT_RESULT_READ_ONLY_INDEPENDENT_RECOMPUTATION_AND_ADJUDICATION`  
**Run ID:** `TTM_VM_V2_NONTEST_192_FROZEN_READER_CPU_ONESHOT_V1`  
**Ngày:** 2026-11-12  
**Phán quyết của runner:** **`GO_CANDIDATE_NONTEST_DESCRIPTION_SCOPED`**.  
**Phán quyết độc lập:** **`PASS_NONTEST_S2_CLOSED_VOCAB_DESCRIPTION_SCREEN_SCOPED`** — PASS theo các ngưỡng NON-TEST đã khóa, **không phải PASS semantic retrieval tự do hoặc TEST**.

## 1. Phạm vi và xuất xứ bất biến

- Source science commit `df7865a420cbd5d58d5f24a55b85f99c9242038e`; runner `v2_frozen_reader_cpu_one_shot.py` Git blob `e9e29c35e4eeeda6ed3ad5a4481a75b51e5b4eab`. Owner Windows preflight native QA **78/78 PASS**, tạo one-shot marker và chạy **192/192 cases**; optimizer steps 0, no-GPU, không mở sealed TEST hoặc chấm DEV/PROBE L0021 cũ.
- Reader nguồn L0020 giữ nguyên, private SHA256 `c458de3afae87b3c381274b8edd698187df63ceac4dbbc0e6d8bd44b85c1632f`, sau train cũ 128 steps; P02 step1280 SHA256 `ee723407b2c25a18be20e26387a3dd8e4a18e2942d469279b6f0748ff86af0dc`; real T1 manifest SHA256 `cba18e60cee3d08a353ee6d4a451017289e45af7b4b1179c87171b9b78d7dfdc`.
- V2 private fixture 192 SHA256 `1d7c02ab082a3c34345953dc5146e5a93f8c6f44e11132ea8abb0594efcc0b9d`, ba strata mỗi 64, 32 memory cards/truyện (1 target + 4 hard negatives gần giống + 27 distractors), seed được khóa trước khi chấm. Không tái tạo, sửa, hoặc tái chọn seed sau kết quả.
- Native Windows output tại `D:\WORK\RESEARCH\TokenToModel-Lab\_evidence\vector-memory\TTM_VM_V2_NONTEST_192_FROZEN_READER_CPU_ONESHOT_V1`: `ONE_SHOT_STARTED.json`, `PER_STORY_QA_PRIVATE.json`, `PROBE_AGGREGATE_PUBLIC.json`. SHA256 aggregate do owner báo **`ddd516dce2717fbacb95704e631a5e9094128a5cc971801b6f7fc2ea2506744d`**; đối chiếu văn bản qua connector Windows bằng **khôi phục CRLF và CRLF cuối tệp** cho đúng SHA. Giới hạn: reconstruction khớp hash native nhưng không thay thế kênh đọc raw binary độc lập.
- Private per-story 5.954 dòng được đọc đủ **192/192 bản ghi**, không upload private file/Reader lên GitHub. Tính độc lập Recall/NLL theo 192 truyện, số lượng token, hai hiệu số theo 64 truyện S2, và bootstrap 2.000 lần. **QA 39/39 PASS.** Public QA aggregate-only: `artifacts/research/vector-memory/TTM_VM_V2_192_NONTEST_CPU_ONESHOT_INDEPENDENT_PERSTORY_QA_20261112.json`.

## 2. Retrieval — ba strata rõ ràng

| Stratum | Mục đích | Recall@1 | Recall@3 | Coverage Top1 | Fallback cosine |
|---|---|---:|---:|---:|---:|
| S0 ID literal | Đối chứng kỹ thuật Oracle-equivalent | **64/64 (100%)** | 64/64 | 64/64 | 0 |
| S1 alias | Tra cứu tên định danh công khai | **64/64 (100%)** | 64/64 | 64/64 | 0 |
| S2 description paraphrase | **Primary exploratory screen** | **64/64 (100%)** | 64/64 | 64/64 | **0/64** |

S2 đạt ngưỡng tiên nghiệm `Recall@1 ≥ 58/64`. **Không có abstain** ở S2. Cả 64 case S2 đều báo `method1=R_HYBRID_LEX_FIRST`, `cause1=LEXICAL_TRIGRAM`; **không một lần** sử dụng fallback cosine frozen. G0 exact literal và S1 alias không tính vào điều kiện khoa học primary.

S0/S1 `Top3` trong dữ liệu thực vẫn chọn **một bản ghi** do exact-id/alias trả duy nhất một index; nên `B3=B1` ở các strata này. Top3 đa bản ghi thực chỉ diagnostic ở S2, không được xem là primary hậu nghiệm.

## 3. Reader NLL — nguồn chính S2 (64 truyện)

Answer-only teacher-forced mean story NLL, nats/token (thấp hơn tốt hơn); 200 answer tokens/arm cho mỗi stratum.

| Arm | NLL S2 |
|---|---:|
| A — No memory / bypass GPT | **6.894291564822197** |
| O1 — Oracle singleton correct | **3.815273191779852** |
| B1 — R_HYBRID_TOP1 correct | **3.815273191779852** |
| C1 — R_HYBRID_TOP1 wrong target value | **5.264369096606970** |
| B3 — Diagnostic Top3 correct | **4.527257312089205** |
| C3 — Diagnostic Top3 wrong | **5.039288375526667** |

`B1` và `O1` **bằng nhau bit-exact theo NLL trong cả 64 trường hợp S2**, không chỉ ở trung bình. Điều này là bằng chứng truy xuất v2 chọn đúng cùng card như Oracle trên fixture synthetic có bộ ba thuộc tính duy nhất.

**Tiêu chí khoa học đã khóa:**

| Điều kiện primary S2 | Quan sát | Kết quả |
|---|---:|---|
| Recall@1 ≥ 0.90 / ≥58 trong 64 | **64/64** | PASS |
| Mean paired delta NLL(A)−NLL(B1) ≥ 0.05 | **+3.079018373042345** | PASS |
| Mean paired delta NLL(C1)−NLL(B1) ≥ 0.05 | **+1.449095904827118** | PASS |
| Bootstrap 95% lower cho cả hai > 0 | **Cả hai dương** | PASS |
| Oracle positive control NLL(A)−NLL(O1) ≥ 0.05 | **+3.079018373042345** | PASS |

Bootstrap percentile runner (2.000 bootstrap draws trên **64 story-pairs**, seeds 20261116/20261117): `A−B1 [2.792866479046643,3.3864670290611683]`; `C1−B1 [0.8043780642561614,2.1780459645204244]`.

Tôi lấy mẫu lại độc lập từ đúng các vector chênh lệch NLL từng truyện bằng **Mulberry32** (khác NumPy PCG64; vẫn 2.000 draws và cùng hai seed định danh), CI độc lập `A−B1 [2.803337201010436,3.381846783682704]`; `C1−B1 [0.7997411417774856,2.1723743378184732]`. Không kỳ vọng giống hệt từng bootstrap replicate; cả hai cặp CI rất gần nhau và đều có lower >0.

## 4. Kiểm toán độc lập 39/39

Kiểm trên từng truyện gồm: đúng số lượng 192/64/64/64, case IDs riêng, answer tokens mỗi stratum, sáu NLL và gate hữu hạn, bypass gate=0, hit Top1 nằm trong Top3, counts/coverage đúng, không abstain/fallback S2, `B1=O1` cho mọi story S2, tính lại trung bình từng arm của cả ba strata, cả hai paired deltas, bootstrap độc lập, source pins, flag bất biến Reader/backbone, `TEST=false`, `optimizer_steps=0`, không chấm lại PROBE cũ/DEV.

Bảng QA chính lưu public aggregate-only JSON. **Không** tải private Reader hoặc per-story lên GitHub, và **không** chạy lại logits/Reader để kiểm định.

## 5. Diễn giải khoa học — rất hẹp

**Điều được minh chứng:** Khi bản ghi tra cứu được từ mô tả ba thuộc tính với bảng từ đồng nghĩa đã đăng ký trước và điều kiện `unique triple`, hệ thống chọn chính xác card trong fixture v2 và Reader L0020 đóng băng làm giảm Answer-only NLL đáng kể so với bypass và đổi value target. Tiêu chí sàng lọc NON-TEST đã khóa được đáp ứng.

**Điều chưa được minh chứng:** open-domain semantic retrieval, mô tả ngoài từ vựng đóng, ambiguity handling trên dữ liệu thật, hiệu quả vector cosine fallback, robust paraphrase ngoài templates, đa bước reasoning, RAG trên tài liệu tự nhiên hay heldout TEST. **Thực tế cả 64 S2 dùng lexical và 0 fallback**, nên không được gọi đây là thành công vector semantic retrieval. Cơ chế `R_HYBRID_LEX_FIRST` gồm việc parse ba thuộc tính và yêu cầu **khớp duy nhất bộ ba thuộc tính với một card** trước khi chấp nhận lexical top1; đó gần như lookup cấu trúc/Oracle sau chuẩn hóa, không phải truy xuất ngữ nghĩa không điều kiện.

L0021 `FAIL_RETRIEVAL_SCOPED` đối với cosine mean-T1/P02 trên random keys **vẫn đúng**, không được bị xóa hoặc diễn giải lại. L0020 Reader Oracle PASS DEV vẫn đúng. Ba kết quả trả lời ba câu hỏi hẹp khác nhau.

**PROBE v2 192 đã tiêu thụ.** Không được làm dữ liệu heldout confirmatory sau khi thay thuật toán; không chạy lại one-shot, không sửa seed/hyperparameter, không mở sealed TEST hoặc sử dụng GPU. Việc giữ nguyên Reader trong lần đánh giá đã được runner báo và checker đối chiếu metadata; chưa có một kênh độc lập kiểm binary trọng số post-run.

## 6. Phán quyết và bước thực hiện tiếp theo

- **`PASS_NONTEST_S2_CLOSED_VOCAB_DESCRIPTION_SCREEN_SCOPED`**, giữ nguyên runner label `GO_CANDIDATE_NONTEST_DESCRIPTION_SCOPED`.
- **`INDEPENDENT_PERSTORY_QA=PASS_39_OF_39`**.
- **`ONE_SHOT=CONSUMED`**, `TRAINING=NO`, `OLD_PROBE=UNCHANGED`, `DEV=NOT_RESCORED`, `TEST=SEALED`, `GPU=NO`.
- Append-only `lineage.md` mục **L0022**, research branch only; không merge `main`.

**Bước thực hiện tiếp theo:** `TTM_VM_V3_NONORACLE_AMBIGUITY_AND_UNSEEN_PARAPHRASE_PREREG_DESIGN_ONLY` — thiết kế PROBE mới phân biệt lookup bộ ba thuộc tính đã được giải quyết với paraphrase ngoài bảng từ đồng nghĩa, nhiễu phủ định, mô tả thiếu/đa nghĩa, và xuất xứ nguồn; không chạy lại v2 hoặc mở TEST. Phải chấp nhận cả kết quả FAIL và quy định abstention/cost/retrieval trước khoa học mới.
