# HANDOFF — Codex distinct reviewer cho TTM-T6 PR #15

**Nhiệm vụ:** `TTM_T6_PR15_DISTINCT_REVIEW_AND_MERGE_DECISION`  
**Ngày lập:** 2026-11-09  
**Quyền thực thi:** REVIEW_ONLY / READ_ONLY; không merge hoặc sửa mã trước phán quyết; tuyệt đối không mở P07/P08.  
**Trạng thái tại thời điểm soạn:** `PR15=DRAFT_HOLD`, `EXTERNAL_REVIEW=NOT_PERFORMED`, `MAIN=UNCHANGED`.

## 1. Nguồn sự thật và snapshot ghim

- Repository: https://github.com/minhtri22/TokenToModel-Lab
- Pull request: https://github.com/minhtri22/TokenToModel-Lab/pull/15
- Nhánh: `feature/ttm-t6-dense-paged-ab-benchmark-fixture-20261109`.
- **PR HEAD trước khi commit handoff này:** `d40927a6bb474a57767589ede98b36790f1bd5ce`. Sau commit tài liệu, phải đọc GitHub PR HEAD mới và ghim chính HEAD đó trong review; không giả định SHA cũ còn là HEAD.
- `main`/base lúc lập handoff: `b57b44e7287f842e81050c1faee337f636333dd0`. Kiểm tra drift trước khi kết luận.
- **HEAD đã chạy trên Windows:** `ff4d30ea294f148d5d060f1331cfbf6f4f6d44aa`; các commit sau đó chỉ bổ sung bằng chứng, báo cáo và handoff — reviewer phải tự kiểm tra diff để xác nhận không có thay đổi chức năng sau lượt Windows.
- Root máy dev: `D:\WORK\RESEARCH\TokenToModel-Lab`; worktree thực nghiệm đã sử dụng: `D:\WORK\RESEARCH\TokenToModel-Lab\.worktrees\ttm-t6-pr15-20261109`.
- GitHub là **source of truth** đối với mã và báo cáo; không lấy log người dùng dán trong chat thay cho bằng chứng đã commit.

## 2. Căn cứ đã có, không tự nâng phạm vi

- Tải thử: model P02 tổng hợp **CPU float32**, 2 layers/4 heads/embedding 64/context 32, ba chuỗi token giả dài 4, 11, 16; 6 token sinh mới mỗi tải; warmups 2, repeats 5, cùng seed và logits-parity guard.
- **Unit tests trên Windows:** `PASS_16_OF_16`; **QA đọc độc lập vật liệu/số học:** `PASS_33_OF_33`; **cross-file arithmetic audit:** `PASS_17_OF_17`; **bốn hiện vật Windows:** `SHA256_VERIFIED_4_OF_4` đã nhập lên GitHub.
- Runtime chủ sở hữu: Windows 11, Python 3.12.10, PyTorch 2.11.0+cpu; SHA nguồn thực thi là commit `ff4d30ea…`.
- Sai khác logits tối đa no-cache vs cache `2.980232238769531e-7`; Dense/Paged có logits trùng trong fixture.
- Bộ nhớ hai request dài 13 và 5 token: Dense/Paged đều cấp pool vật lý 65,536 bytes; request reserved Dense 65,536 vs Paged 24,576; logical KV đều 18,432. **Không có peak RSS**: các giá trị RSS là null.
- Không dùng checkpoint T4, dữ liệu TRAIN/VAL/TEST/Q1Q2, GPU hoặc P07/P08; **không** có bằng chứng speedup thực tế. Đây chỉ là PASS kỹ thuật synthetic-CPU scoped.

## 3. Các tệp bắt buộc reviewer phải đọc từ GitHub

**Mã và kiểm thử:**
- `tools/t6/cache_ab_benchmark_fixture.py`
- `tools/t6/independent_scoped_qa.py`
- `tools/t6/build_report.py`
- `tests/t6/test_cache_ab_fixture.py`
- `tools/t6/run_windows_exact_head.ps1`
- `tools/t6/README.md`
- `.gitattributes` — kiểm tra ảnh hưởng LF tới nguồn pin gốc.

**Bằng chứng nguồn và Windows:**
- `artifacts/qa/t6/TTM_T6_SOURCE_AND_QA_MANIFEST_20261109.json`
- `artifacts/qa/t6/TTM_T6_SYNTHETIC_CPU_AB_20261109.json`
- `artifacts/qa/t6/TTM_T6_INDEPENDENT_QA_20261109.json`
- `artifacts/qa/t6/windows_owner_20261109/TTM_T6_WINDOWS_UNITTEST_OWNER_20261109.log`
- `artifacts/qa/t6/windows_owner_20261109/TTM_T6_WINDOWS_CPU_AB_OWNER_RUN.json`
- `artifacts/qa/t6/windows_owner_20261109/TTM_T6_WINDOWS_INDEPENDENT_QA_OWNER_20261109.json`
- `artifacts/qa/t6/windows_owner_20261109/TTM_T6_WINDOWS_OWNER_RECEIPT_20261109.json`
- `artifacts/qa/t6/windows_owner_20261109/TTM_T6_WINDOWS_OWNER_INDEPENDENT_READBACK_AND_ADJUDICATION_20261109.json`
- `docs/t6/TTM_T6_CPU_NO_CACHE_DENSE_PAGED_AB_SCOPED_RESULTS_20261109.md`
- `docs/t6/TTM_T6_WINDOWS_CPU_AB_OWNER_SCOPED_ADJUDICATION_20261109.md`.

Các SHA-256 phải lấy từ manifest/owner receipt và tái tính từ **nội dung raw blob**, không từ trình bày Markdown hay chuỗi đã đổi CRLF/LF. Bốn SHA-256 Windows kỳ vọng:
1. unittest: `2f063493c448723ae9fcfd2d2ca364bb0374dcdf1369558c9302669924c93590`
2. benchmark: `39275324dc56c2bbfb075e73991cf4383f48bdc38acdaf182c66178b42e113b0`
3. independent QA: `2525b423dac500c19810e4c66a301939bf0e4083ceeeb0a779509c41783b6591`
4. owner receipt: `742247aaa64701d6e09964db8a0724c2980bccaf9ffe533402703dd8e7b327c6`.

## 4. Checklist review thực chất, tránh chỉ chấp nhận PASS sẵn có

1. **Provenance/diff:** xác minh PR #15 chỉ thêm fixture, tests, docs, QA và `.gitattributes`; `src/p02/transformer_core.py`, `src/p05/dense_kv_cache.py`, `src/p06/paged_kv_manager.py`, `lineage.md` phải **không thay đổi nội dung**. Pin chính xác original Git blob.
2. **Correctness/inference parity:** xem fixture có so sánh thật logits từng bước, cùng trọng số, cùng token prefix, cùng `argmax`, cùng dtype và seed, không lấy đường No-cache làm golden tự tham chiếu sai. Kiểm tra lớp LayerNorm/RMSNorm, cache cập nhật/đọc, token index, append và output equality; đánh giá độ phủ thật của 16 unit tests, nhất là negative/injection tests.
3. **Memory accounting:** phân biệt vật lý pool allocated, request reserved, logical KV, fragmentation; kiểm tra công thức, bytes/layer/head, tái sử dụng và scrub sau release, concurrent isolation, OOM partial mutation. Tránh đánh đồng `reserved` nhỏ hơn với RAM tổng thấp hơn.
4. **TTFT/TPOT fairness:** đối chiếu chính xác điểm bắt đầu/kết thúc thời gian, prefill vectorized No-cache so với prefill token-by-token Dense/Paged, cache constructor ngoài TTFT nhưng có log riêng, warmups/repeats/threading, thứ tự xoay backend, mô tả median/P95 và phân phối. Kiểm tra liệu định nghĩa có dẫn tới kết luận thực nghiệm thiên lệch và yêu cầu đổi tên/ghi caveat nếu cần.
5. **Hardware/evidence:** đọc nguyên bốn tệp Windows, đối chiếu SHA nguồn từ owner receipt, kiểm toán QA và cross-file audit có thực sự độc lập với runner tới đâu. Rà soát Windows replay script với PowerShell 5.1, đường dẫn, tính an toàn worktree, no overwrite, pin source, và trường platform.
6. **Phát hành/rủi ro:** xem file có lộ bí mật, checkpoint/private corpus hay không; repo public. Kiểm tra phạm vi khi merge vào `main`: công cụ độc lập không kích hoạt P07/P08 và không yêu cầu training/GPU/TEST.
7. **Giới hạn:** một người review độc lập cần đánh giá code và khả năng tái lập, không coi 16/16 hay 33/33 là chứng nhận chất lượng công nghiệp; không diễn giải RSS null hoặc latency millisecond của mô hình synthetic như số liệu model thật.

## 5. Phạm vi được phép và quy trình thực hiện

- Lượt đầu **READ_ONLY** trên exact GitHub HEAD và bằng chứng đã khóa. Có thể chạy *static analysis* hoặc kiểm tra bổ sung trên fixture tổng hợp trong vùng dự án riêng **chỉ nếu cần để xác minh lỗ hổng**, đánh dấu rõ là `REVIEW_DIAGNOSTIC`, không thay thế hoặc chạy lại one-shot Windows đã tiêu thụ.
- Không sửa nguồn T6 trực tiếp trong lượt review; nếu phát hiện lỗi, đưa danh sách sửa cụ thể và phân loại CRITICAL/HIGH/MEDIUM/LOW; trao lại tác giả sửa trên nhánh PR #15, rồi **review lại HEAD mới**. Không tự âm thầm sửa và tự phê duyệt.
- Không checkout, xóa, `reset --hard`, force-push, merge, hoặc cleanup ngoài thư mục dự án; không đụng những dự án khác. `main`, `lineage.md` append-only và PR #13 phải nguyên trạng. Không cấp phép P07/P08.
- Mọi nhận định phải trỏ path, Git blob/line range, SHA256 hoặc đoạn code tái hiện; thiếu bằng chứng thì `HOLD`, không phán đoán.

## 6. Hình thức báo cáo Codex phải trả và gate merge

Ghi biên bản hoàn chỉnh vào `docs/t6/reviews/TTM_T6_PR15_CODEX_DISTINCT_REVIEW_YYYYMMDD.md` và JSON receipt tương ứng trong `artifacts/qa/t6/reviews/` **chỉ khi được owner cho phép commit review**; nếu chưa được cấp quyền ghi, trả nội dung báo cáo và SHA để chủ dự án nhập GitHub. Biên bản cần có:

- Reviewer identifier, mode/agent, thời điểm, khẳng định reviewer **khác tác giả fixture**, mọi giới hạn độc lập/các kiểm thử đã hoặc chưa trực tiếp chạy.
- Exact `PR15_HEAD` review, `MAIN_HEAD`, full changed-file list, source blob pins và hash artifacts.
- Bảng QA: code correctness, test sufficiency, evidence authenticity, memory accounting, TTFT/TPOT methodology, OS portability, security/scope, replay/lineage.
- Findings có severity, path + dòng, cách khắc phục; phân loại blocker vs non-blocker.
- Phán quyết duy nhất **`PASS_REVIEWED_SCOPED`**, **`HOLD_REQUIRED_FIX_OR_EVIDENCE`**, hoặc **`FAIL_MATERIAL_CONTRACT`**. Nếu thiếu ràng buộc độc lập, ghi `HOLD`.
- **Merge recommendation** riêng: `MERGE_CANDIDATE` chỉ nếu không còn CRITICAL/HIGH, bằng chứng kiểm chứng, scope đúng; `MERGE_HOLD` nếu còn blocker; `MERGE_DENY` nếu fail. `PASS_REVIEWED_SCOPED` không tự động thay quyết định chủ dự án.
- Ghim `MAIN=UNCHANGED`, `PR15=DRAFT`, `LINEAGE=UNCHANGED`, `P07=PAUSED_PRESERVE`, `P08=NOT_OPENED`, `NO_TRAIN`, `TEST=UNTOUCHED`.

**CẤM TỰ MERGE.** Sau báo cáo, **dừng tại merge decision gate** và chờ owner phê duyệt merge riêng. Sau bất kỳ sửa code nào, review bản HEAD mới trước khi khuyến nghị lại.

## 7. Bước thực hiện tiếp theo

`TTM_T6_PR15_CODEX_DISTINCT_REVIEW_EVIDENCE_AND_OWNER_MERGE_GATE` — reviewer đọc và kiểm toán trên GitHub, trả PASS/HOLD/FAIL kèm bằng chứng rồi bàn giao quyết định merge cho owner. Không mở P07/P08 theo kết quả này.
