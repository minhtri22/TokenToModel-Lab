# TTM R3A — Full Python replay 384/384 và phân xử phạm vi khoa học

**Ngày:** 2026-11-11 · **Task:** `TTM_R3A_INDEPENDENT_PYTHON_FULL_REPLAY_AND_OWNER_ADJUDICATION`  
**Nguồn:** `minhtri22/TokenToModel-Lab` nhánh `research/ttm-r3a-adversarial-independent-review-20261111`. Review trước thực thi ở commit `694378e1d295a4db1c48040a37bf9a5774b2d989` từ R3A đóng băng `81327724c08771682622bebb8648fefd55a4fa9a`.  
**Phân biệt reviewer:** báo cáo review ở nhánh ghi rõ tác giả ChatGPT/GPT-6 nội bộ; **không phải một phiên Codex Native2 đã chạy riêng**. Script baseline là mã người phản biện đã commit, được tái lập nguyên byte và chạy đầy đủ tại lượt này.

## 1. Python replay thực sự đã chạy

**Script gốc:** `tools/research/semantic_state_r3/r3a_alias_backward_heuristic.py`, Git blob `5c11164cb66371e443a788c94e7e93fb86c55264`, SHA-256 `c7681baa75e0aa1fcf86059c700230a88dcab14831321de19fb4f1dfe115d880`, kích thước **8.296 byte**. Khôi phục nguồn nguyên byte, tính lại git blob bằng `sha1("blob " + size + "\\0" + bytes)`, khớp.

**Nguồn dữ liệu:** chỉ hai JSON public trong GitHub tại đúng commit `81327724c08771682622bebb8648fefd55a4fa9a`:

- `artifacts/qa/ttm-r3-structural-design/r3a/R3A_MODEL_INPUT_ONLY.json`, **113.611 byte**, SHA-256 `2510866d82641bd27207082566d6b4dbb867e59516794e422dff8fb041646402`.
- `artifacts/qa/ttm-r3-structural-design/r3a/R3A_PUBLIC_ORACLE.json`, **309.003 byte**, SHA-256 `b509fae3f63399c978d532c2686d147bd4ba41e44b2aa9135dcd38360e6ffb08`.

**Môi trường actual:** Linux CPU, **Python 3.13.5**, không phải máy Windows/Python 3.12 của chủ dự án. Không cài torch, không mở TTM checkpoint, không gọi model inference. Phiên tác giả review trước đó đã chạy JavaScript 384/384; tại đây **Python gốc** đã chạy `--self-test` **4/4 PASS** và `--model ... --oracle ... --out ...` **384/384 PASS**, exit code 0. Mỗi `T1/T2/T3 × DEV/CHALLENGE` đạt **64/64**. Tổng miss **0**.

**Cách tính:** `predict(row)` đọc `story/question`, lập alias mapping rồi đọc event lines từ cuối về đầu, khớp regexp cho handoff/goal change/cancel/delegation/SET. Không replay dynamic state, không xác minh event precondition, không xây causal graph. Đáp án `oracle` được sử dụng **chỉ tại phase scoring**.

**Receipt nguyên byte trên GitHub:**
- [Python full 384-row result](../../artifacts/qa/ttm-r3-structural-design/r3a/review_20261111/TTM_R3A_PYTHON_FULL_REPLAY_20261111.json) — Git blob `293373aa53b0e920dc592c3f0b17c7978576d3fe`, SHA-256 `b9a92901d32ea5d7809f574882642eec3360e012eed51335cc54d615a7d74aae`.
- [16/16 integrity and negative checks](../../artifacts/qa/ttm-r3-structural-design/r3a/review_20261111/TTM_R3A_PYTHON_FULL_REPLAY_INTEGRITY_QA_20261111.json) — Git blob `0c9648bfd0a0552a6f88674bc43171cba2b258c2`, SHA-256 `af4c1dc74130cdec930755899660163d860705ce32d28a9279475060286ed29b`.

**Để replay trên máy có clone repository chứa exact pinned commit** (đường output tự chọn trong thư mục dự án; script từ chối overwrite):
```powershell
$root = 'D:\WORK\RESEARCH\TokenToModel-Lab'
$py = 'C:\Users\minht\AppData\Local\Programs\Python\Python312\python.exe'
$script = Join-Path $root 'tools\research\semantic_state_r3\r3a_alias_backward_heuristic.py'
& $py $script --self-test
& $py $script --repo-root $root
```
Script dùng `git show` với commit `81327724...` và SHA pin; nếu commit không có trong repo local thì **dừng**, không tùy ý thay bằng nhánh hiện tại. Trên Linux tool hiện tại đã chạy bằng hai file exact-hash do repo cung cấp; không suy từ đó rằng Windows/Colab đã qua QA.

### QA thực tế

16/16 kiểm tra PASS bao gồm: script Git blob gốc, length source, model và oracle SHA, chỉ `story/question`, oracle public/unsealed, 384/384, 6 buckets ×64, đúng pinned commit, repeat nội bộ, độc lập thứ tự dòng, từ chối nhãn chèn vào record, từ chối trùng bản ghi, từ chối model SHA sai, oracle SHA sai, thay một nhãn oracle chỉ làm giảm score mà **không thay prediction**. Đây là kiểm toán của ChatGPT Web trong phiên hiện tại; không tự nhận là lần review Codex độc lập.

## 2. Phân xử chính thức về chứng cứ

| Claim | Quyết định | Cơ sở |
|---|---|---|
| R3A generator, strict model-input schema, counterfactual 4-cell, author CPU QA 44/44 | `PASS_SCOPED_PRESERVED` | Test lịch sử + nguồn đã khóa; không bị kết quả shortcut phủ nhận |
| Heuristic không mô phỏng state/graph giải 384 câu | **`REPRODUCED_PYTHON_384_384`** | Exact script Git blob và exact SHA dữ liệu, full replay CPU |
| R3A buộc bộ giải làm graph/state reasoning | **`FAIL_SCOPED`** | Một phương pháp yếu hơn toàn bộ causal-graph reasoning vẫn 100% |
| Structural DEV/CHALLENGE độc lập ở mức query-skeleton | `NOT_DEMONSTRATED` | Report review cho thấy split có content-length confounding và skeleton overlap |
| O0 learning và O1 có ích | `NOT_TESTED` | Chưa có TTM/O0/O1 neural inference/training |
| R3A là blinded FINAL | `NO` | Toàn bộ oracle/labels public trên GitHub |

**Phán quyết hướng nghiên cứu:** `R3A_DEMO_ONLY_ARCHIVE_ANTI_SHORTCUT_DIAGNOSTIC`. R3A vẫn hữu ích làm ví dụ về event parsing/alias/strict JSON/counterfactual QA và minh họa các bẫy thiết kế benchmark. **Không tiếp tục sửa R3A vòng mới chỉ để đánh bại từng heuristic.** Đây là lựa chọn phân xử nghiên cứu đề xuất cho chủ dự án, **không** phải giấy phép huấn luyện được chủ dự án cấp.

### Vì sao không vá thêm R3A ngay?

- R2A, R3, R3A liên tiếp cho thấy dùng một heuristic địa phương được thiết kế mới có thể giải 100% dù prior heuristic đã thất bại; sửa từng heuristic tạo nguy cơ *benchmark overfitting*.
- Có nhiều lỗi độc lập: truy xuất lùi regex + alias, tách DEV/CHALLENGE theo độ dài, query-relevant skeleton trùng. Một bản sửa alias không giải quyết vấn đề split/độc lập.
- **Mô hình P02 vẫn chưa được kiểm nghiệm** trên một benchmark mới không public oracle; do đó không có kết quả để quy nguyên nhân cho kiến trúc GPT-2 hay cần O1.
- Nghiên cứu gốc đặt câu hỏi năng lực **học/tổng quát hóa**; tái diễn các toy đã công bố nhãn chưa kiểm tra được mục tiêu này.

## 3. Phương án kế nhiệm hữu hạn — không mở GPU

**Giữ R3A ở cấp public demo và chuyển trọng tâm sang thiết kế một O0-only small neural feasibility** trên bộ đánh giá *mới, độc lập*, với khóa split theo causal dependency pattern, cùng word/length bins, 4-cell paired interventions, và blind labels được escrow. Trước science cần xác định liệu bài toán có phân biệt O0 khỏi rule heuristics một cách trung thực, cũng như ngân sách nhỏ, quyền dữ liệu, nguồn checkpoint và cách chấm.

Không đưa **public R3A** vào blind FINAL mới; có thể giữ làm unit test/diagnostic công khai. O0 baseline 2×2 hiện tại vẫn HOLD, O1 DEFER. Nếu sau này nghiên cứu R4 về trạng thái quan hệ cần mở, phải lập giả thuyết/corpus mới và hạn chế sửa sau khi xem kết quả; không đổi tên R3A thành FINAL.

**Bước thực hiện tiếp theo:** `TTM_O0_ONLY_SMALL_NEURAL_FEASIBILITY_NEW_DIAGNOSTIC_CORPUS_DESIGN_AND_SINGLE_OWNER_GO_NO_GO`. Một bản thiết kế tích hợp về mục tiêu, corpus mới, split, pin checkpoint và ngân sách CPU/T4, rồi một quyết định GO/HOLD; chưa có quyền thực thi GPU.

**Bảo toàn:** `MAIN=NOT_WRITTEN`, `PR13=DRAFT_HOLD`, `R3A_ORIGINAL=UNCHANGED`, `REVIEW_SOURCE=UNCHANGED`, `LINEAGE=NOT_WRITTEN`, `TRAINING=NO`, `GPU=NO`, `TTM_TEST_Q1Q2=UNTOUCHED`.
