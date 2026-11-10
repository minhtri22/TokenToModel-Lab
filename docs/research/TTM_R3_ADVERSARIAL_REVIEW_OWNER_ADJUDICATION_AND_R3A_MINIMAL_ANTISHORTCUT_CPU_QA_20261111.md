# TTM R3 — Phân xử phản biện latest-write và amendment R3A (CPU toy)

**Ngày:** 2026-11-11 · **Công việc:** `TTM_R3_MINIMAL_ANTISHORTCUT_AMENDMENT_AND_SINGLE_INTEGRATED_ADVERSARIAL_CPU_QA_THEN_O0_PILOT_OWNER_DECISION`  
**Nguồn sự thật:** `minhtri22/TokenToModel-Lab`, nhánh `research/ttm-r3a-antishortcut-amendment-20261111` từ **exact review branch commit** `d641e1577eaef4d3adffa526a13c3392a519b3bb`. R3 gốc `cd3dc4ceb3a42b9ac8df7bdb5169cda444c3b41a`.  
**Phạm vi:** khảo cứu, phân xử và bộ kiểm toy tổng hợp trên CPU. **KHÔNG** huấn luyện/suy luận neural, không Colab/GPU, không TEST/Q1Q2, không sửa main hoặc PR13; không ghi lineage.

## 1. Phân xử báo cáo mới, không che giấu kết quả FAIL

Nguồn phản biện đã commit: [báo cáo](https://github.com/minhtri22/TokenToModel-Lab/blob/d641e1577eaef4d3adffa526a13c3392a519b3bb/docs/research/TTM_R3_ADVERSARIAL_REVIEW_20261111.md) (Git blob `4b291eebd6329fdde58a9fac927c9f85c1c8aef3`) và [Python baseline](https://github.com/minhtri22/TokenToModel-Lab/blob/d641e1577eaef4d3adffa526a13c3392a519b3bb/tools/research/semantic_state_r3/ttm_r3_independent_latest_write_baseline.py) (Git blob `72d84fd1c28ee422cf4264baec9c51e94db171f1`).

**Cảnh báo chứng cứ:** báo cáo reviewer ghi rõ phiên đầu tiên chạy 384/384 bằng JS qua GitHub JSON, còn Python mới syntax/smoke; reviewer là **ChatGPT nội bộ**, không phải một phiên Codex R3 độc lập đầy đủ. **Lượt này tôi khôi phục script Python khớp nguyên byte Git blob `72d84f...` và chạy full 384/384 trên hai JSON R3 có SHA chính xác.** [Biên nhận Python replay](../../artifacts/qa/ttm-r3-structural-design/r3a/R3_ORIGINAL_CODEX_BASELINE_EXACT_PYTHON_FULL_REPLAY.json). Không gán Python replay mới cho phiên reviewer trước.

| ID | Phát hiện | Phân xử |
|---|---|---|
| R3-ADV-01 HIGH | Last direct handoff/change/set query-keyed tìm đúng 384/384 | **ACCEPT_FAIL_SCIENTIFIC_DISCRIMINATION_SCOPED**. `shallow_keyed_direct=64/384` không đầy đủ |
| R3-ADV-02 HIGH | Chữ ký 3 motifs/split không có phụ thuộc queried key | **ACCEPT_LIMITATION**; R3A bổ sung typed-event, query-conditioned signatures và kiểm zero overlap theo chữ ký đó, nhưng **chưa chứng minh graph-OOD** |
| R3-ADV-03 HIGH | Alias/cancel/delegate không answer-critical | **ACCEPT**; R3A buộc ít nhất một trong các cơ chế đó thay đổi đáp án trong mỗi family |
| R3-ADV-04 MEDIUM | Thứ tự A_T,A_D,B_T,B_D lặp lại và family/split blocks | **ACCEPT**; R3A model-input rows shuffle tất định; bí danh/nhãn chỉ có trong oracle QA công khai |
| R3-ADV-05 MEDIUM | `C-F` O1 vs O0 có confound objective và architecture | **ACCEPT_HOLD**; không đổi science design hay tuyên bố architectural gain |
| R3-ADV-06 MEDIUM | R3 oracle công khai không phải FINAL kín | **ACKNOWLEDGED**; R3A cũng là công khai, chỉ QA/diagnostic |

**Bảo toàn:** R3 gốc `SOURCE_QA=PASS_SCOPED_70/70`, 42 âm tính PASS về phạm vi phần mềm. Chúng không phủ định `SCIENCE_DISCRIMINATION=FAIL_SCOPED_BY_100_PERCENT_LEXICAL_BASELINE`; R3 gốc không bị xóa hoặc ghi lại để né lỗi.

## 2. Amendment R3A đã thực thi, dữ liệu và mã lưu nguyên byte

**Đặc tả thay đổi tối thiểu:**
- **T1**: Một định nghĩa alias sớm được đổi giữa A/B; câu lệnh `X passes item to <alias>` về sau giữ nguyên. Chỉ đọc người nhận literal (alias) không trả lời được holder thực.
- **T2-DEV**: biến thể A ủy quyền goal `g` cho B, B thay cùng sự kiện bằng hủy goal ở người nguồn → câu hỏi B có đáp án `g` hoặc `NONE`. **T2-CHALLENGE**: B nhận goal, biến thể A hủy (→ `NONE`), biến thể B thay bằng `CHANGE` (→ goal khác). Cả hai obey preconditions.
- **T3**: định nghĩa alias cho hai người có mục tiêu khác nhau và mục tiêu này đến từ delegation; cùng câu hỏi nhắc **alias**, đổi một định nghĩa alias làm đổi kết quả, không đổi các câu sự kiện phía sau.
- Mỗi trong **96 nhóm** có đủ bốn ô `A_T,A_D,B_T,B_D`. Đáp án target A/B **thay đổi**, đáp án distractor **bất biến**, câu hỏi/nhãn không có trong model-input ngoài `story,question`.
- **384 model-input rows** đã shuffle tất định; full public oracle nằm trong tệp riêng có SHA. Dữ liệu **không phải** science heldout kín.
- Graph signature chỉ ở mức **query-conditioned typed-event role sequence** (phân biệt target/non-target và alias/direct). Đây là QA loại trùng dưới một phép chuẩn hóa cụ thể, **không** chứng minh đa dạng OOD.

### Kết quả kiểm thử thật

| Tiêu chí | R3 gốc | R3A amendment |
|---|---:|---:|
| Nhóm/cell | 96×4 | **96×4** |
| Rule oracle đúng (checker đọc visible text) | 384/384 | **384/384** |
| Đối chứng **cùng** backward latest-write script | **384/384 (100%)** | **208/384 (54,17%)** |
| Mục tiêu T2 cho kết quả `NONE` | 0 | **32 câu** |
| Trùng query-conditioned event-role signatures DEV/CHALLENGE | chưa đo đúng phạm vi | **0 theo signature R3A** |
| Kiểm thử CPU R3A | — | **44/44 PASS** |
| Negative tests fail-closed R3A | — | **30/30 PASS** |
| O0/O1 neural | NOT_EXECUTED | NOT_EXECUTED |

Có **hai điều chỉnh trước khi đóng băng R3A**: (i) checker chỉ được so **cùng visible question** trong phản thực alias, không so resolved person (vì chính alias mapping là biến can thiệp); (ii) checker bắt được **3 motif overlaps** trong bản thử đầu, generator được thêm cấu trúc nhiễu hợp lệ riêng ở T2-CHALLENGE, tái sinh toàn bộ corpus rồi đạt 0 overlap. Một assertion kiểm thử được tăng từ điều kiện tùy chọn lên kiểm đúng index sự kiện bị thay. **Chỉ kết quả cuối với SHA trong manifest là canonical; không gọi lượt thử trước PASS.**

**Nguồn:**
- [Generator](../../tools/research/semantic_state_r3/r3a_generator.py)
- [Independent text checker](../../tools/research/semantic_state_r3/r3a_independent_checker.py) (**không import generator**)
- [Integrated 44 CPU tests](../../tools/research/semantic_state_r3/r3a_integrated_cpu_qa.py)
- [Public oracle 96×4](../../artifacts/qa/ttm-r3-structural-design/r3a/R3A_PUBLIC_ORACLE.json)
- [Model-input 384 rows](../../artifacts/qa/ttm-r3-structural-design/r3a/R3A_MODEL_INPUT_ONLY.json)
- [Original-R3 exact Python replay](../../artifacts/qa/ttm-r3-structural-design/r3a/R3_ORIGINAL_CODEX_BASELINE_EXACT_PYTHON_FULL_REPLAY.json)
- [R3A latest-write replay](../../artifacts/qa/ttm-r3-structural-design/r3a/R3A_LATEST_WRITE_BASELINE.json)
- [44-test raw log](../../artifacts/qa/ttm-r3-structural-design/r3a/R3A_CPU_QA.log)
- [SHA/Git-blob manifest và decision](../../artifacts/qa/ttm-r3-structural-design/r3a/R3A_SOURCE_OF_TRUTH_SHA256_AND_OWNER_SCOPED_DECISION_20261111.json)

## 3. Giới hạn và quyết định nghiên cứu

**`R3A_PUBLIC_TOY_ANTI_KNOWN_SHORTCUT=PASS_SCOPED`, `O1=DEFER`, `O0=PRESERVE_AS_CONTROL`.** Điều này **không** chứng minh việc duy trì một state module explicit là cần thiết. Bộ giải ký hiệu tổng quát phải đạt 100%; một heuristic alias-aware hoặc look-back khác cũng có thể giải tất cả, cần Codex tìm tiếp.

Bộ R3A chưa dùng một checkpoint TTM, chưa đo khả năng học, chưa có matched supervision/compute, không đưa dữ liệu JSON công khai có đáp án vào FINAL. Chỉ cho phép tiếp tục **thiết kế** O0-only neural pilot và phản biện adversarial R3A; **không** cho phép training/GPU hoặc kích hoạt O1. Không tạo chuỗi vi cấp phép riêng.

**Bước thực hiện tiếp theo:** `TTM_R3A_CODEX_ADVERSARIAL_HEURISTICS_REVIEW_THEN_O0_ONLY_SMALL_NEURAL_FEASIBILITY_SINGLE_OWNER_DECISION`. Codex đọc toàn bộ GitHub source + oracle + checker + 44 tests + latest-write baseline, tìm shortcut mới, chất lượng graph-split và leakage; sau review mới chốt một quyết định giữa O0-only feasibility, sửa tiếp toy, hoặc đóng hướng R3; tuyệt đối không tự gọi R3A một FINAL khoa học.

**Governance:** `MAIN=UNCHANGED_BY_THIS_BRANCH` · `PR13=DRAFT_UNMERGED` · `R3/R2A=IMMUTABLE_IN_GIT_HISTORY` · `LINEAGE=UNMODIFIED` · `TEST_Q1Q2=UNTOUCHED` · `NEW_MODEL_TRAINING=ZERO` · `GPU=ZERO`.
