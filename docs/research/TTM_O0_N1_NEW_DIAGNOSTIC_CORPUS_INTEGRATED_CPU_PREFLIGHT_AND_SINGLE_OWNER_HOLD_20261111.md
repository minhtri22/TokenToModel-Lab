# TTM O0-DIAG-N1 — một lượt nguồn/dữ liệu/checker/BPE/escrow/CPU và quyết định HOLD

**Ngày:** 2026-11-11 · **Phạm vi:** nghiên cứu nội bộ owner / ChatGPT Web; không làm Codex review trong lượt này.  
**Task:** `TTM_O0_NEW_DIAGNOSTIC_CORPUS_GENERATOR_STRICT_CHECKER_SHORTCUT_AUDIT_AND_ONE_CPU_PREFLIGHT_SINGLE_OWNER_DECISION`  
**Phán quyết:** **`HOLD_T4_DO_NOT_TRAIN`** (một quyết định tổng hợp). Các kết quả QA kỹ thuật PASS được bảo toàn, các FAIL khoa học cũng được ghi chính xác.

GitHub Source of Truth: branch `research/ttm-o0-only-neural-feasibility-diagnostic-design-20261111` từ HEAD thiết kế `08b1f8586627608512eef222b681624f2a8656e1`. Không ghi `main`, `lineage.md`, không merge PR13, không mở TEST/Q1Q2, không train TTM hoặc chạy GPU.

## 1. Dữ liệu thực sự đã tạo và lưu trực tiếp trên GitHub

[Generator JS tất định](../../tools/research/o0_diagnostic_n1/o0_n1_public_generator.mjs) Git blob `008936285e511446ec61be8668aa7c3480b1a785`. Bốn họ grammar N1–N4 được tạo độc lập về câu chuyện/tên/thứ tự nhiễu với R2A/R3/R3A gốc nhưng **không được coi là cấu trúc chưa thấy chỉ nhờ khác template**. Tạo đầy đủ 4 ô `A_TARGET,A_DISTRACTOR,B_TARGET,B_DISTRACTOR`/nhóm.

| Split | Nhóm | Model-only rows | Oracle public |
|---|---:|---:|---|
| TRAIN | 1.024 | **4.096** | [TRAIN_PUBLIC_ORACLE](../../artifacts/qa/ttm-o0-neural-diagnostic/corpus_n1/TRAIN_PUBLIC_ORACLE.json) |
| DEV_IID | 64 | **256** | [DEV_IID_PUBLIC_ORACLE](../../artifacts/qa/ttm-o0-neural-diagnostic/corpus_n1/DEV_IID_PUBLIC_ORACLE.json) |
| DEV_STRUCT | 64 | **256** | [DEV_STRUCT_PUBLIC_ORACLE](../../artifacts/qa/ttm-o0-neural-diagnostic/corpus_n1/DEV_STRUCT_PUBLIC_ORACLE.json) |
| **Public tổng** | **1.152** | **4.608** | nhãn công khai, không phải blind FINAL |
| FINAL owner-only | 128 | **512 trong dữ liệu encrypted reproducible** | plaintext **không xuất bản** |

Bản model-only tại:
- [TRAIN_MODEL_INPUT_ONLY.json](../../artifacts/qa/ttm-o0-neural-diagnostic/corpus_n1/TRAIN_MODEL_INPUT_ONLY.json) và [TRAIN_SHARD_INDEX.json](../../artifacts/qa/ttm-o0-neural-diagnostic/corpus_n1/TRAIN_SHARD_INDEX.json), 8 shard × 512 hàng, hoàn toàn không có answer/label/split/ID trong từng model input.
- [DEV_IID_MODEL_INPUT_ONLY.json](../../artifacts/qa/ttm-o0-neural-diagnostic/corpus_n1/DEV_IID_MODEL_INPUT_ONLY.json), [DEV_STRUCT_MODEL_INPUT_ONLY.json](../../artifacts/qa/ttm-o0-neural-diagnostic/corpus_n1/DEV_STRUCT_MODEL_INPUT_ONLY.json).
- [GitHub readback part1](../../artifacts/qa/ttm-o0-neural-diagnostic/corpus_n1/O0_N1_GITHUB_READBACK_PART1.json) `PASS_12/12` và [part2](../../artifacts/qa/ttm-o0-neural-diagnostic/corpus_n1/O0_N1_GITHUB_READBACK_PART2.json) `PASS_8/8` xác nhận tổng **20/20 shard + DEV files chính xác từng byte UTF-8** so với generator đã ghim. Tệp TRAIN full trên 1 MB không được connector trả nguyên nội dung khi fetch, nên dùng shard thay vì lờ đi việc không có readback.

Các nhãn DEV đã công khai để QA, vì vậy đây là dữ liệu phát triển, **không phải bộ đánh giá blind trước training**.

## 2. Bộ kiểm độc lập, chèn dữ liệu sai và BPE2048

- [Independent visible-text checker](../../tools/research/o0_diagnostic_n1/o0_n1_independent_checker.mjs) và [receipt](../../artifacts/qa/ttm-o0-neural-diagnostic/corpus_n1/O0_N1_INDEPENDENT_PUBLIC_CORPUS_QA.json): **4.608/4.608** đáp án từ câu chuyện hiển thị, **1.152/1.152** quartet đúng outcome invariants. **13/13** ca làm sai cấu trúc record hoặc tiền điều kiện bị từ chối (kiểm object JS; *không tự suy là chống trùng raw JSON byte*).
- [Raw JSON fail-closed validator](../../tools/research/o0_diagnostic_n1/o0_n1_raw_input_fail_closed.mjs) và [receipt](../../artifacts/qa/ttm-o0-neural-diagnostic/corpus_n1/O0_N1_RAW_JSON_FAIL_CLOSED_NEGATIVE_QA.json): **16/16** đột biến chèn answer/oracle/split, record metadata, trùng khóa và schema giả bị từ chối, kiểm tra trước đưa vào mô hình.
- Đọc trên máy Windows từ file manifest tokenizer gốc, trích xuất đủ **1.791 merge pairs**, kết quả [BPE readonly QA](../../artifacts/qa/ttm-o0-neural-diagnostic/corpus_n1/O0_N1_EXACT_T1_BPE2048_LENGTH_READONLY_QA.json): **4.608 mẫu**, prompt max **177**, training sequence max **182**, **0** over 224/256. Manifest internal SHA `6da22cf79c3a6cfd08d80a768eb1074125a753164ccf62a164e79545956e94c6`. Đây là số đo token trên TRAIN/DEV public, **không bao gồm FINAL encrypted**.

**Ngân sách nguồn thực tế:** một lượt đi qua 4.096 TRAIN rows có **637.010 token huấn luyện** theo encoding + EOS, nhưng chỉ **15.162 token thuộc phần answer** (khoảng **2,38%**). Vì vậy lịch candidate 128 × 4.096 nhãn / step `524288` chủ yếu học story/format; không được gọi toàn bộ là giám sát answer.

## 3. CPU P02/checkpoint QA — PASS scoped

SHA256 đọc thật từ checkpoint bước 1024 tại runtime: `cb985751795c8328ad65acf7ca4c1033ce35182c1bfbdb8c38550de629cb271b`; pack TRAIN/VAL gốc `184f68b4c0c800ef3e98362c2e20e1cd35baa269e926489a475664526ecd9913`. **Không đọc TEST**. Mô hình được nạp từ cùng cấu hình, tên và toán học P02 bằng mã CPU tương đương độc lập, strict `state_dict`, **3.749.376 tham số**. Hai bước optimizer trên **token ngẫu nhiên tổng hợp**, so sánh chạy liên tục với tái khôi phục từ bản sao checkpoint tạm: tham số cuối bằng nhau. Không hề huấn luyện dữ liệu khoa học.

- [CPU receipt exact source](../../artifacts/qa/ttm-o0-neural-diagnostic/corpus_n1/O0_N1_CPU_P02_PARENT_RESTORE_SYNTHETIC_QA.json): `PASS_CPU_SYNTHETIC_RESTORE_PARITY`, Python 3.13.5 / Torch 2.10.0+cpu.
- [Mã CPU QA nén theo byte](../../tools/research/o0_diagnostic_n1/o0_cpu_restore_qa.py.gz.b64), SHA của file .py sau giải nén `4094bc8d0983d1d2904e07035305594a7bb5c1d6f21de12ad2538cde46071ab4`, Git blob file .py gốc `b4729b2d16e116d3846b63089bed5ae4951eb8da`. Nén gzip mtime=0, base64 ASCII, có thể giải nén thành nguyên mã đã chạy. Giữ nguyên source GitHub, không chỉ có link tải xuống.
- Đây **không** phải chứng minh runner O0 mới có cơ chế READY-last và exact resume **trên T4 FP16** hoặc ngân sách GPU 128 steps đã được đo. Không được gán `SCIENCE_READY=PASS`.

## 4. FINAL escrow — cryptographic preparation PASS; science eligibility HOLD

- [Encrypted owner-private FINAL seed escrow](../../artifacts/qa/ttm-o0-neural-diagnostic/corpus_n1/BLIND_FINAL_ENCRYPTED_SEED_ESCROW.json), Git blob `133bb4182f65f6c911f493622b5709561f69befb` (AES-256-GCM, nonce và AAD được công bố, **không có khóa, seed hay labels**).
- [Final generator byte-reconstructable source](../../tools/research/o0_diagnostic_n1/o0_final_private_escrow.py.gz.b64), Git blob b64 `d061d27d5ea2b78568639cedf711aab3080f33cd`; sau gzip decode nguyên source Python Git blob `a8e48d0f889e3de638e12355966e75536f861953`.
- Khóa owner **đã ghi và đọc lại** tại `D:\WORK\RESEARCH\TokenToModel-Lab\_tmp\TTM_O0_N1_FINAL_PRIVATE_OWNER_KEY_DO_NOT_GITHUB_20261111.json`; **không git add, không push khóa**. Public ciphertext SHA256 `4b514b3ab1844ec58132e1deaf8c7507968d04930c11ecc6aef9f9b77cf6e197`.
- Tái tạo **512/512 rows, 128 groups** từ seed đã giải mã bằng generator byte-pinned, exact plaintext commitment SHA256 `70487eba90d642f03e79b10816705797c134c421b2b8062d9b58bb72b7f8f505`; [escrow reconstruction QA](../../artifacts/qa/ttm-o0-neural-diagnostic/corpus_n1/O0_N1_FINAL_SEED_ESCROW_REPRODUCTION_QA.json).
- **FINAL không đủ điều kiện khoa học**: BPE FINAL chưa kiểm, full causal query-motif split chưa kiểm; ngay ở coarse template level, bốn family FINAL **trùng bốn dạng DEV_STRUCT**. Escrow được bảo toàn làm bản nghiên cứu kín, **không tự giải niêm phong để đánh giá**.

Để giải mã mã Python nén (chỉ đọc mã, không đụng khóa), trên Windows Python3.12 có thể dùng `gzip.decompress(base64.b64decode(path.read_text().strip()))` và so SHA/Git blob theo receipt. Tệp `*.py.gz.b64` trong GitHub là source exact bytes, không phải bằng chứng executable Windows đã được QA.

## 5. Phát hiện khoa học FAIL bắt buộc lưu

| Gate | Kết quả |
|---|---|
| Public corpus tạo đúng 4.608 hàng, parse độc lập | **PASS** |
| BPE2048 train/DEV context≤256 | **PASS** |
| JSON strict và mutation | **PASS** |
| GitHub source/16 TRAIN shards + DEV | **PASS 20/20** |
| CPU synthetic checkpoint restore parity | **PASS scoped** |
| FINAL AES256GCM seed owner-private | **PASS preparation** |
| **Alias-aware last-relevant regex shortcut** | **4.608/4.608 (100%) — `SCIENTIFIC_DISCRIMINATION=FAIL_SCOPED`** |
| **Chỉ thay đúng một event trong mỗi A/B** | **FAIL 596/1.152 groups** có thêm thay đổi do vị trí câu nhiễu; 556 nhóm đạt đúng 1 dòng thay |
| **FINAL khác cấu trúc DEV_STRUCT** | **FAIL (4/4 coarse family structures overlap)** |
| Kết quả O0 learning và structural generalization | NOT_EXECUTED |
| New O0 CPU science runner / T4 FP16 resume + capacity | NOT_PROVEN |
| TEST/Q1Q2 | UNTOUCHED |

[Baseline script](../../tools/research/o0_diagnostic_n1/o0_n1_alias_aware_last_event_baseline.mjs) và [result](../../artifacts/qa/ttm-o0-neural-diagnostic/corpus_n1/O0_N1_SHALLOW_ALIAS_HEURISTIC_BASELINE.json) đã được commit trước khi phân xử: `4096/4096 TRAIN`, `256/256 DEV_IID`, `256/256 DEV_STRUCT` đúng mà không cần TTM. [Can thiệp/final split audit](../../artifacts/qa/ttm-o0-neural-diagnostic/corpus_n1/O0_N1_SINGLE_INTERVENTION_AND_STRUCTURAL_SPLIT_AUDIT.json) bảo toàn lỗi thiết kế, không vá dataset dựa trên kết quả hậu nghiệm.

**Quan trọng:** từ R2A/R3/R3A/N1, việc sửa riêng từng lối tắt đã biết có nguy cơ benchmark overfitting. Đề xuất **không** chạy mô hình ngay và cũng không tiếp tục một vòng vá heuristic tùy hứng. Dữ liệu N1 hiện có giá trị làm **unit test, negative-control và demo task-learning**, không được gọi là benchmark confirmatory về trạng thái.

## 6. Quyết định GO/HOLD duy nhất

**`HOLD_T4_DO_NOT_TRAIN`**. Giữ O0 checkpoint và kế hoạch 2×2 không đổi, O1 `DEFER`. Không bắt đầu Colab Free T4, không dùng FINAL ciphertext, không đọc TEST/Q1Q2, không tạo checkpoint science, không merge PR13. Không cấp vi mô; đã có một phán quyết tích hợp đủ đóng lượt.

**Hướng nghiên cứu sau đó (nếu chủ dự án chọn tiếp):** `TTM_O0_NEURAL_TASK_LEARNING_MINIMAL_PILOT_RETHINK_SUPERVISION_AND_EVAL_WITHOUT_POSTHOC_SHORTCUT_PATCH`. Trước tiên chọn **một** mục tiêu có thể bác bỏ: hoặc *học regex-like task* như thí nghiệm demo (dùng corpus N1 công khai và không claim state reasoning), hoặc nghiên cứu **benchmark khoa học mới** với đa dạng causal graph thật sự và FINAL motif-disjoint khóa trước mọi neural run. Không gộp hai mục tiêu vào một ngưỡng thành công.

**Dữ liệu tự tạo nội bộ:** không dùng TinyStories text hay nhãn Q1/Q2 để sinh N1; quyền nguồn của grammar tự viết đủ cho vòng thử nội bộ này, không yêu cầu tổ chức phản biện ngoài. GitHub chứa cả code, dữ liệu public, mô tả negative outcomes và ciphertext, **không chứa key/seed**.

**Bảo toàn:** `MAIN=NOT_WRITTEN`, `PR13=DRAFT_HOLD`, `LINEAGE=NOT_WRITTEN`, `R3A=DEMO_ONLY`, `NEW_SCIENTIFIC_TRAINING=NO`, `GPU=NO`, `TTM_TEST_Q1Q2=UNTOUCHED`.
