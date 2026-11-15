# TTM-Small-4M Foundation First — Distinct Independent F01–F05 Remediation Review

**Ngày kiểm toán:** 2026-11-15  
**Operation:** `TTM_SMALL4M_FOUNDATION_FIRST_F01_F05_DISTINCT_INDEPENDENT_REMEDIATION_REVIEW_SINGLE_GATE`  
**Vai trò:** Distinct Independent AI Scientific & Source Reviewer; **không** phải human reviewer attestation  
**Chế độ:** `READ_ONLY · SOURCE_ONLY · DESIGN_ONLY · NO_SCIENCE_EXECUTION · NO_REPOSITORY_WRITES`  
**Repository:** https://github.com/minhtri22/TokenToModel-Lab  
**Branch trong handoff:** `research/ttm-small4m-foundation-first-single-gate-20261115`  
**Baseline:** `fbe4a1ed58eef66f896bbfe0471926b7cc45298e`  
**Candidate cũ:** `4c97f2b1d1836b31d55b649e78a8b69fecc44482`  
**Exact remediation candidate:** `97731311ba2fc3a8000c2532bd4e5a0470c437ba`  
**Previous independent verdict:** `HOLD_REVISE_DESIGN` (bất biến cho candidate cũ)  
**Final independent verdict của lần review này:** **`GO_DESIGN_SCOPED`**

> Phán quyết này chỉ chấp nhận logic sửa thiết kế trong hai tài liệu F1/F2. Nó **không** chứng nhận per-axis gold, calibration data, tính hợp lệ của rater trên phân phối đầu ra mô hình, cũng không cho phép triển khai, M0 execution, inference, GPU, training, TEST/FINAL reuse, F3/F4 hoặc merge. Owner chưa cấp science GO.

## A. Kiểm toán nguồn và Git exactness

### A1. So sánh đúng các commit đã khóa

- [Remediation compare: `4c97...` → `977313...`](https://github.com/minhtri22/TokenToModel-Lab/compare/4c97f2b1d1836b31d55b649e78a8b69fecc44482...97731311ba2fc3a8000c2532bd4e5a0470c437ba): GitHub connector báo `ahead_by=1`, `behind_by=0`, `total_commits=1`; chỉ **2 modified Markdown files**, không có thêm/xóa file: F1 **+21/−6**, F2 **+52/−17**.
- [Baseline compare: `fbe4...` → `977313...`](https://github.com/minhtri22/TokenToModel-Lab/compare/fbe4a1ed58eef66f896bbfe0471926b7cc45298e...97731311ba2fc3a8000c2532bd4e5a0470c437ba): `ahead_by=5`, `behind_by=0`; chỉ **4 files added** trong `docs/research/ttm-small4m-foundation-first/`. Không thấy thay đổi `lineage.md`, mã, mô hình, tokenizer, dữ liệu, ngưỡng hoặc các báo cáo nghiên cứu đã khóa trong hai diff này.
- Phạm vi xác minh là **Git commit snapshot**, không phải kiểm tra byte của máy Windows, trạng thái branch HEAD live, hay private assets.

### A2. Git blob SHA-1 — đối chiếu trực tiếp GitHub `fetch_file(path,ref=exact SHA)`

| Tài liệu | Blob ở candidate cũ | Blob ở candidate mới | Kiểm tra |
|---|---|---|---|
| `01_SMALL4M_ARCHITECTURE_COMPONENT_SPEC_20261115.md` | `22e823b0a9069f07a6d6912b6425762528e2f655` | cùng SHA | **PASS unchanged** |
| `02_SMALL4M_EVIDENCE_FAILURE_ROOT_CAUSE_MATRIX_20261115.md` | `834200abc5a55791c42f27224b8296f70243edb6` | `853411064bcdc58f5c6bad713b85237f2828182e` | **PASS exact new blob** |
| `03_SMALL4M_ROOT_CAUSE_RESEARCH_ROADMAP_F0_F4_20261115.md` | `4b1c5dea92f900d93adfa5747db0ccb6b8b10eaa` | `d87309aea043b845fafcc805ed13b2b4466f5e46` | **PASS exact new blob** |
| `04_SMALL4M_SCOPE_ISOLATION_DECISION_20261115.md` | `4c3f3c000096dfe31d05e1fb2765e180276ddc76` | cùng SHA | **PASS unchanged** |

Nguồn mới: [F1 exact](https://github.com/minhtri22/TokenToModel-Lab/blob/97731311ba2fc3a8000c2532bd4e5a0470c437ba/docs/research/ttm-small4m-foundation-first/02_SMALL4M_EVIDENCE_FAILURE_ROOT_CAUSE_MATRIX_20261115.md), [F2 exact](https://github.com/minhtri22/TokenToModel-Lab/blob/97731311ba2fc3a8000c2532bd4e5a0470c437ba/docs/research/ttm-small4m-foundation-first/03_SMALL4M_ROOT_CAUSE_RESEARCH_ROADMAP_F0_F4_20261115.md), [F0 exact](https://github.com/minhtri22/TokenToModel-Lab/blob/97731311ba2fc3a8000c2532bd4e5a0470c437ba/docs/research/ttm-small4m-foundation-first/01_SMALL4M_ARCHITECTURE_COMPONENT_SPEC_20261115.md), [Scope exact](https://github.com/minhtri22/TokenToModel-Lab/blob/97731311ba2fc3a8000c2532bd4e5a0470c437ba/docs/research/ttm-small4m-foundation-first/04_SMALL4M_SCOPE_ISOLATION_DECISION_20261115.md).

**Quan trọng:** Các giá trị trên là Git blob **SHA-1 do GitHub trả về**, không phải SHA-256. Không có raw-byte SHA-256 của bốn tài liệu GitHub được tính độc lập qua một raw binary transport; `SOURCE_DOC_SHA256=NOT_RECOMPUTED`. Điều này không ảnh hưởng kiểm tra exact Git blob pin, nhưng không được đổi nhãn thành byte-level private custody PASS.

### A3. Báo cáo kiểm toán gốc — byte verified

Tìm thấy đúng bản Library owner của hai attachment; đã materialize nguyên byte và tính SHA-256 độc lập trong container đọc-only:

| Bằng chứng gốc | SHA-256 tái tính | Kết quả |
|---|---|---|
| `TTM_SMALL4M_FOUNDATION_FIRST_DISTINCT_INDEPENDENT_REVIEW_20261115(1).md` | `3113f5b7c38e794de0504c859bdc0c0ee63d9fe5b285b2c9f29eb2ca194c84f4` | **MATCH** |
| `TTM_SMALL4M_FOUNDATION_FIRST_INDEPENDENT_REVIEW_RECEIPT_20261115(2).json` | `e8bc21c533d46d3212fd8bac779d4e5e01ab8e906decce208261def2548158ef` | **MATCH** |

Đã đọc phần đánh giá F0/F1/F2, findings gốc F01–F05, giới hạn và verdict `HOLD_REVISE_DESIGN`. Hai attachment không được giả định đã lên GitHub; không chỉnh sửa hoặc thay phán quyết cũ.

## B. Bảng quyết định riêng cho năm finding

| Original finding | Severity | Remediation verified | Residual issue | Verdict |
|---|---|---|---|---|
| `SM4M-IR-F01` | **HIGH** | PASS | Tám pattern và independence về ngữ nghĩa chưa được tạo/kiểm tra; được khóa thành prospective pre-exec gate | **CLOSED_DESIGN** |
| `SM4M-IR-F02` | **HIGH** | PASS | Không thấy sai lệch số liệu còn mở trong F1/F2 | **CLOSED** |
| `SM4M-IR-F03` | **MEDIUM** | PASS | Không có sai mẫu số còn mở trong F1/F2 | **CLOSED** |
| `SM4M-IR-F04` | **MEDIUM** | PASS | Công thức, gold, score custody mới chỉ là proposed future contract; pre-execution admission chưa hoàn tất | **CLOSED_DESIGN** |
| `SM4M-IR-F05` | **LOW** | PASS | Không có shared-item reliability estimate; ghi rõ là unavailable | **CLOSED** |

### B1. `SM4M-IR-F01` — HIGH · Độ nhận diện từng trục của M0

- **finding_id:** `SM4M-IR-F01` (re-review). **original_finding_id:** `SM4M-IR-F01`. **severity:** HIGH.
- **exact_source:** F2 mới, mục **3.1–3.2** tại [exact blob](https://github.com/minhtri22/TokenToModel-Lab/blob/97731311ba2fc3a8000c2532bd4e5a0470c437ba/docs/research/ttm-small4m-foundation-first/03_SMALL4M_ROOT_CAUSE_RESEARCH_ROADMAP_F0_F4_20261115.md); [MD1 nguyên bản](https://github.com/minhtri22/TokenToModel-Lab/blob/33021a421f05bb3bfa0999ad12bc3bd144366da9/docs/research/ttm-hdata-fail4-md1/TTM_HDATA_FAIL4_MD1_PROSPECTIVE_PREREG_AND_FOUR_FAIL_MECHANISM_PLAN_20261114.md).
- **observed_evidence:** M0 gốc có đúng 32 positive `111` và 32 negative `000` theo từng trục: không thể tách lỗi actor/object/goal nếu rater chỉ nhận diện polarity. F2 mới nêu rành mạch điểm yếu này, khóa phạm vi thành `CALIBRATION_CLEAR_POLARITY_SCOPED_PASS`; đề xuất đầy đủ 8 pattern `111/011/101/110/100/010/001/000`, đối chứng partial/ambiguous, kiểm shortcut từ vựng/độ dài/style/category, gold QA độc lập, số lượng/threshold riêng cần đóng băng trước execution.
- **discrepancy:** Lỗi suy luận ban đầu được sửa: M0 PASS **không** còn được nhận làm per-axis validity hay model-error proof.
- **scientific_or_governance_impact:** Design có cấu trúc để phân biệt lỗi từng trục **nếu** gold đúng, các cặp thật sự isolate một yếu tố và negative-control không qua ngưỡng. Tám vector nhị phân chỉ đủ về đại số nhãn, **không tự bảo đảm** can thiệp actor không làm đổi goal/object theo ngữ nghĩa. Không tuyên bố định danh causal đã đạt thực nghiệm.
- **required_remediation:** Không yêu cầu sửa tài liệu thêm để đóng **design gate**. Trước bất kỳ data admission, phải chứng minh bằng independent gold/source QA rằng trong cùng core, mỗi single-axis contrast thật sự giữ nguyên hai trục còn lại; fix allocation, semantic acceptance rule, proxy shortcut negative control, source rights/PII, invalid gold handling và stop rule. Nếu không đạt: `F2_PREEXEC=BLOCK`.
- **closure_status:** **CLOSED_DESIGN · PREEXEC_BLOCK_REMAINS**.

### B2. `SM4M-IR-F02` — HIGH · Hiệu số không phải điểm tuyệt đối

- **finding_id/original_finding_id:** `SM4M-IR-F02`. **severity:** HIGH.
- **exact_source:** F1 mới bảng SM-E09/SM-E10 và H-MEAS; F2 mới §3; [A/C FINAL24 exact](https://github.com/minhtri22/TokenToModel-Lab/blob/37165ce6eea0bb4b04d316e2998da579c91d13cf/docs/research/TTM_AC_FINAL24_INDEPENDENT_QA_AND_FORMAL_ADJUDICATION_20261112.md); [H-DATA-S1 exact](https://github.com/minhtri22/TokenToModel-Lab/blob/ef4cc05037f98129082cd429a75092b8cc822efb/docs/research/ttm-small4m-h-data-s1/TTM_HDATA_S1_FINAL24_OWNER_UNBLIND_FORMAL_ADJUDICATION_20261114.md).
- **observed_evidence:** A/C primary absolute A=`0.6667/3`, C=`0.6667/3`, Δ(C−A)=`0`; C không chứng minh incremental gain. H-DATA-S1 primary absolute H0=`0/3`, H1=`0/3`, Δ=`0`; đây mới là all-zero tuyệt đối trong **protocol H-DATA**. Các giá trị khớp báo cáo nguồn trên exact commit.
- **discrepancy:** Sai biệt cũ “hai protocol có cùng absolute-zero floor” được loại bỏ; không pooling giữa raters/protocols.
- **scientific_or_governance_impact:** H-MEAS chỉ là điều kiện ưu tiên kiểm validity trước khi giải thích zero scores; không tuyên bố measurement gây ra failure.
- **required_remediation:** Không cần sửa thêm. Giữ study-specific scoring và `ROOT_CAUSE_IDENTIFIED=NO`.
- **closure_status:** **CLOSED**.

### B3. `SM4M-IR-F03` — MEDIUM · Đơn vị quan sát H-DATA

- **finding_id/original_finding_id:** `SM4M-IR-F03`. **severity:** MEDIUM.
- **exact_source:** F1 mới SM-E10 + H-MEAS; F2 mới §3; H-DATA-S1 FINAL24 adjudication trên exact commit dẫn ở B2.
- **observed_evidence:** `24 pairs × 2 arms = 48 continuations`; `48 × 3 primary axes = 144 primary axis-level scores`, cả 144 là `0`; `48 × 5 axes = 240 scores` tổng. Các ý này xuất hiện nhất quán trong F1 và F2.
- **discrepancy:** Không còn cách viết `48/48 axes`. 48 là mẫu số continuation, 144 là mẫu số điểm trục primary, 240 là tổng 5 trục.
- **scientific_or_governance_impact:** Không tăng số quan sát độc lập từ 24 prompt pairs lên 144; 144 là các sub-scores có cấu trúc lồng nhau, không là 144 cases độc lập.
- **required_remediation:** Không cần sửa tiếp; giữ các đơn vị phân tích có điều kiện theo từng study.
- **closure_status:** **CLOSED**.

### B4. `SM4M-IR-F04` — MEDIUM · Hợp đồng người chấm & custody

- **finding_id/original_finding_id:** `SM4M-IR-F04`. **severity:** MEDIUM.
- **exact_source:** F2 mới §3.1, §3.3; MD1 nguyên bản tại B1.
- **observed_evidence:** Cho M0 gốc, 2 rater blind chấm cùng 64 opaque item IDs, 32 positive/32 negative **trên mỗi trục**. Với từng rater/trục: `TP+FN=32`; `TN+FP=32`; sensitivity=`TP/32`; specificity=`TN/32`; ngưỡng ≥`28/32`. Mỗi rater có 3 confusion matrices. Raw exact-match agreement của hai rater trên **cùng 64 IDs** cho từng trục: `matches/64 ≥0.85`, tương đương `matches≥55`; F2 ghi đây là **proposed freezing of formula**, không tuyên bố MD1 đã ghi công thức. Missing/invalid/duplicate/misbound ID → `HOLD_INPUT_INTEGRITY`, không drop row hay đổi denominator.
- **discrepancy:** Đã bổ sung rater mapping, blinded permutation, freeze-before-unblind, SHA-bound score receipt, gold provenance, source rights/PII, independent review và distinction AI-gold vs human gold; tất cả admission giữ `M0_EXECUTION=NOT_AUTHORIZED`.
- **scientific_or_governance_impact:** Công thức đủ kiểm toán **nếu được phê duyệt và khóa trước chạy**. Không áp ngầm 28/32/64 lên tập mixed-label mới; hợp đồng tương lai của amendment vẫn cần độc lập signoff.
- **required_remediation:** Không cần sửa thêm cho design gate. `SOURCE_QA`, `DATA_GOLD_RIGHTS_PII`, `ANTI_SHORTCUT`, `BLIND_RATER_CUSTODY`, `FROZEN_SCORING_CONTRACT`, `NONOVERLAP`, `OWNER_GO` bắt buộc PASS như **một gói admission** trước mọi execution; thiếu bất kỳ mục nào → `PREEXEC_BLOCK`.
- **closure_status:** **CLOSED_DESIGN · PREEXEC_BLOCK_REMAINS**.

### B5. `SM4M-IR-F05` — LOW · FRESH16 không phải inter-rater agreement

- **finding_id/original_finding_id:** `SM4M-IR-F05`. **severity:** LOW.
- **exact_source:** F1 mới SM-E06 và F1 §D; F2 §3; [FRESH16 V2 original](https://github.com/minhtri22/TokenToModel-Lab/blob/0ec28d44587fde9ad4acba8cccae65648e367181/docs/research/ttm-small4m-quality-gap/TTM_FRESH16_V2_FINAL_FROZEN_UNBLIND_SCIENTIFIC_ADJUDICATION_20261111.md).
- **observed_evidence:** S1 chấm **32 outputs**, S2 chấm **16 counterfactual pairs**; nhiệm vụ và item sets khác nhau. Không có phép đo inter-rater reliability trên shared items. Kết quả H1=`0/16`, H2=`0/8` và `FAIL_PRE_REGISTERED_FRESH16_V2_SCOPED` giữ nguyên.
- **discrepancy:** Cách diễn đạt có thể nhầm hai sessions là two-rater agreement đã được thay bằng caveat rõ ràng.
- **scientific_or_governance_impact:** Không gán độ tin cậy đo lường mà nghiên cứu FRESH16 chưa quan sát.
- **required_remediation:** Không cần sửa thêm.
- **closure_status:** **CLOSED**.

## C. Đánh giá nội dung sửa đổi M0 và prospective controls

Về mặt logic, bộ 8 nhãn nhị phân tạo khả năng kiểm soát riêng mỗi trục (full 2³ factorial) **nhưng không tự bảo đảm ngữ nghĩa độc lập**: một thay đổi actor có thể làm thay đổi goal hoặc object relation. Vì thế quyết định `GO_DESIGN_SCOPED` ở đây phụ thuộc vào điều kiện trong F2: gold độc lập kiểm từng single-axis contrast; phải loại bỏ case bị semantic coupling, kiểm shortcut, khóa denominator/threshold/negative-controls trước xây dựng dữ liệu. Bản candidate nêu các điều kiện đó và chặn thực thi nếu chưa khóa, nên đáp ứng yêu cầu **thiết kế tiền cứu**. Các test đó **chưa được thực hiện**.

Không có `M0 PASS` thực nghiệm; `CALIBRATION_CLEAR_POLARITY_SCOPED_PASS` trong văn bản là **nhãn kết quả giả định nếu M0 đạt**. Không coi nhãn này là hiện trạng hoặc bằng chứng model-error. Không rút ra nguyên nhân mô hình từ các zero scores. M1–M3 chỉ là sequence proposed theo MD1, không được mở.

## D. Bảo toàn lộ trình và nghiên cứu độc lập

| Phase / phạm vi | Kết luận của re-review |
|---|---|
| `SM4M-F0` | **PASS_UNCHANGED_SOURCE**; Git blob giữ nguyên. Tài liệu F0 ghi trạng thái tại thời điểm tác giả soạn (`independent QA NOT_EXECUTED`); review độc lập gốc về sau đã đánh `PASS_SOURCE_SCOPED`. Không hồi tố sửa F0 snapshot, cũng không revalidate private checkpoint. |
| `SM4M-F1` | **PASS_REMEDIATION_DESIGN_SOURCE**; mapping, số liệu, caveat được sửa đúng. |
| `SM4M-F2` | **GO_DESIGN_SCOPED_ONLY**; M0 nguyên bản chưa thực thi, prospective per-axis chưa admission, `F2_PREEXEC_BLOCK=TRUE`. |
| `SM4M-F3` | **NOT_OPENED**. |
| `SM4M-F4` | **NOT_OPENED**. |
| EmbeddingGemma 2 | **INDEPENDENT / PAUSED FOR COORDINATION**, không nhập donor/adapter vào Small-4M. |
| Vector Memory | **INDEPENDENT / PAUSED FOR COORDINATION**, không nhập retriever/Reader vào Small-4M. |
| MoE/scaling/P07/P08 | **NOT_OPENED / PAUSED**, không tự khởi động. |

Không đổi trạng thái historical study, `lineage.md` append-only, checkpoint SHA, seed, frozen results, thresholds hoặc one-shot đã tiêu thụ. Git diff 2 tệp và 4 tệp hỗ trợ kết luận này **trong snapshot candidate**. Không tuyên bố đã kiểm chứng live control plane hoặc private weights.

## E. Findings còn mở, giới hạn và điều kiện chặn

**Finding nguồn/design mới có mức HIGH/CRITICAL:** **0**. **Finding nguồn/design mới có mức MEDIUM cần sửa tài liệu trước GO_DESIGN:** **0**. Không tạo gói remediation mới hoặc micro-permit.

**Các điều kiện tiền thực thi (không phải finding còn mở trong design gate):** cụ thể hóa và kiểm chứng semantic isolation cho mọi mixed-label contrast, gold provenance và independent review, cân bằng phân phối 8 patterns, thống kê và negative-control threshold prospectively frozen, blind mapping và score custody, rights/PII/nonoverlap, cùng một independent pre-execution QA và owner science GO. Chưa một điều kiện nào được reviewer này tuyên bố PASS.

**Giới hạn xác minh:**
1. GitHub connector đọc UTF-8 source và trả Git blob SHA-1; không tính raw-byte SHA-256 độc lập của bốn file public GitHub.
2. Hai review attachment gốc có SHA-256 được tính từ **raw bytes** và khớp handoff; không mặc định những byte này hiện diện trong GitHub.
3. Các điểm A/C, H-DATA, FRESH16 và MD1 được đối chiếu với **báo cáo adjudication/protocol tại pinned commit**, không truy cập private per-record raw scores, AES escrow, checkpoint, dataset, scorer chat transcript, hoặc mô hình.
4. Kết quả Git diff không chứng minh trạng thái runtime Windows, branch HEAD hiện tại, private custody, hay tất cả 15 nhóm evidence ở cấp raw receipt.
5. Không phải human reviewer attestation; không có khoa học/QA runtime mới.

## F. Phán quyết cuối duy nhất

# `GO_DESIGN_SCOPED`

Đạt tiêu chuẩn phán quyết thiết kế: năm finding gốc được khép trong phạm vi cụ thể, hai HIGH đã khắc phục lỗi logic chính, hai MEDIUM có unit/contract và pre-exec blocks rõ, LOW không overclaim inter-rater agreement; MD1 nguyên bản, A/C–H-DATA–FRESH16, F0/Scope, F0→F4 đều giữ nguyên theo diff và tài liệu.

**Không mở quyền:** `ROOT_CAUSE_IDENTIFIED=NO`; `SCIENCE=HOLD`; `GPU=NO`; `TRAINING=NO`; `MODEL_INFERENCE=NO`; `M0_EXECUTION=NOT_AUTHORIZED`; `TEST/FINAL=UNTOUCHED`; `F3/F4=NOT_OPENED`; `OWNER_SCIENCE_GO=NOT_GRANTED`; `MERGE_AUTHORIZATION=FALSE`.

**Bước thực hiện tiếp theo — duy nhất:** **Owner xem xét một phán quyết tích hợp `GO_DESIGN_SCOPED` và tự quyết định đóng design gate hoặc giữ HOLD; không tự khởi chạy nghiên cứu hay tạo pre-execution packet trong lượt này.**
