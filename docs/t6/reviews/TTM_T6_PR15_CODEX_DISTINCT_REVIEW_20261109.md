Đã hoàn tất rà soát độc lập PR #15 trên đúng GitHub HEAD. Mã nguồn và bằng chứng Windows đạt các kiểm tra kỹ thuật trong phạm vi CPU tổng hợp. Tuy nhiên, phát hiện một lỗ hổng bảo vệ đường dẫn khi chạy trực tiếp công cụ Python trên Windows.

**Phán quyết:** HOLD\_REQUIRED\_FIX\_OR\_EVIDENCE  
**Khuyến nghị merge:** MERGE\_HOLD

Dưới đây là biên bản bàn giao cho chủ dự án.

# TTM-T6 — Báo cáo rà soát độc lập PR #15

**Ngày:** 09/11/2026  
**Reviewer:** Codex Native2 / GPT-6  
**Vai trò:** Rà soát độc lập (Distinct Code Reviewer)  
**Phạm vi:** Chỉ đọc mã nguồn, kiểm toán bằng chứng và đánh giá điều kiện merge.

## 1\. Xác minh nguồn GitHub

| Thành phần | Kết quả |
| --- | --- |
| Repository | `minhtri22/TokenToModel-Lab` |
| PR | `#15` |
| PR HEAD | `1b98dde3b40f78edd7c599a12ff8c71ebe6b346f` |
| Main/base | `b57b44e7287f842e81050c1faee337f636333dd0` |
| Windows execution commit | `ff4d30ea294f148d5d060f1331cfbf6f4f6d44aa` |
| PR state | `OPEN / DRAFT` |
| Changed files | 19 |
| GitHub HEAD drift | Không phát hiện |
| Merge performed | NO |

Đã xác minh trực tiếp `refs/pull/15/head`, nhánh nguồn của PR và `main`.

Các thay đổi sau commit Windows chỉ bổ sung hiện vật, báo cáo và tài liệu handoff.

**Nguồn P02/P05/P06 giữ nguyên Git blob.**

| Thành phần | Git blob |
| --- | --- |
| P02 | `9762343e06cf800b50574c2871ae1ed58537fb18` |
| P05 | `d835e5d7bb07fea447c5a869b13c70327ab05a53` |
| P06 | `4d52188adaf55674b6965513ea1beb38ec9a8e9b` |
| lineage.md | `971fbd8eccdf4719fee6b83a3c0f4c44b13ebaa9` |

Các blob trên khớp giữa main gốc, commit Windows và PR HEAD.

### Phạm vi 19 tệp thay đổi

- `.gitattributes`
- [artifacts/qa/t6/TTM\_T6\_INDEPENDENT\_QA\_20261109.json](<artifacts/qa/t6/TTM_T6_INDEPENDENT_QA_20261109.json>)
- [artifacts/qa/t6/TTM\_T6\_SOURCE\_AND\_QA\_MANIFEST\_20261109.json](<artifacts/qa/t6/TTM_T6_SOURCE_AND_QA_MANIFEST_20261109.json>)
- [artifacts/qa/t6/TTM\_T6\_SYNTHETIC\_CPU\_AB\_20261109.json](<artifacts/qa/t6/TTM_T6_SYNTHETIC_CPU_AB_20261109.json>)
- [artifacts/qa/t6/TTM\_T6\_UNITTEST\_20261109.log](<artifacts/qa/t6/TTM_T6_UNITTEST_20261109.log>)
- [artifacts/qa/t6/windows\_owner\_20261109/TTM\_T6\_WINDOWS\_CPU\_AB\_OWNER\_RUN.json](<artifacts/qa/t6/windows_owner_20261109/TTM_T6_WINDOWS_CPU_AB_OWNER_RUN.json>)
- [artifacts/qa/t6/windows\_owner\_20261109/TTM\_T6\_WINDOWS\_INDEPENDENT\_QA\_OWNER\_20261109.json](<artifacts/qa/t6/windows_owner_20261109/TTM_T6_WINDOWS_INDEPENDENT_QA_OWNER_20261109.json>)
- [artifacts/qa/t6/windows\_owner\_20261109/TTM\_T6\_WINDOWS\_OWNER\_INDEPENDENT\_READBACK\_AND\_ADJUDICATION\_20261109.json](<artifacts/qa/t6/windows_owner_20261109/TTM_T6_WINDOWS_OWNER_INDEPENDENT_READBACK_AND_ADJUDICATION_20261109.json>)
- [artifacts/qa/t6/windows\_owner\_20261109/TTM\_T6\_WINDOWS\_OWNER\_RECEIPT\_20261109.json](<artifacts/qa/t6/windows_owner_20261109/TTM_T6_WINDOWS_OWNER_RECEIPT_20261109.json>)
- [artifacts/qa/t6/windows\_owner\_20261109/TTM\_T6\_WINDOWS\_UNITTEST\_OWNER\_20261109.log](<artifacts/qa/t6/windows_owner_20261109/TTM_T6_WINDOWS_UNITTEST_OWNER_20261109.log>)
- [docs/t6/TTM\_T6\_CPU\_NO\_CACHE\_DENSE\_PAGED\_AB\_SCOPED\_RESULTS\_20261109.md](<docs/t6/TTM_T6_CPU_NO_CACHE_DENSE_PAGED_AB_SCOPED_RESULTS_20261109.md>)
- [docs/t6/TTM\_T6\_WINDOWS\_CPU\_AB\_OWNER\_SCOPED\_ADJUDICATION\_20261109.md](<docs/t6/TTM_T6_WINDOWS_CPU_AB_OWNER_SCOPED_ADJUDICATION_20261109.md>)
- [docs/t6/reviews/TTM\_T6\_PR15\_CODEX\_DISTINCT\_REVIEW\_HANDOFF\_20261109.md](<docs/t6/reviews/TTM_T6_PR15_CODEX_DISTINCT_REVIEW_HANDOFF_20261109.md>)
- [tests/t6/test\_cache\_ab\_fixture.py](<tests/t6/test_cache_ab_fixture.py>)
- [tools/t6/README.md](<tools/t6/README.md>)
- [tools/t6/build\_report.py](<tools/t6/build_report.py>)
- [tools/t6/cache\_ab\_benchmark\_fixture.py](<tools/t6/cache_ab_benchmark_fixture.py>)
- [tools/t6/independent\_scoped\_qa.py](<tools/t6/independent_scoped_qa.py>)
- [tools/t6/run\_windows\_exact\_head.ps1](<tools/t6/run_windows_exact_head.ps1>)

## 2\. Ma trận kết quả

| Hạng mục | Đánh giá |
| --- | --- |
| Tính đúng mã nguồn (Code correctness) | PASS\_SCOPED |
| Logits parity | PASS |
| Generated token parity | PASS |
| Unit tests | PASS\_16/16 theo log Windows |
| Material QA | PASS\_33/33 |
| Cross-file audit | PASS\_17/17 theo hiện vật lưu trữ |
| Windows SHA-256 | PASS\_4/4, reviewer tái tính |
| Memory accounting | PASS\_SCOPED |
| Benchmark measurement | PASS\_DESCRIPTIVE\_ONLY |
| Benchmark fairness | LIMITED |
| Windows PowerShell runner | PASS\_SCOPED |
| Direct Python path containment | HIGH\_FINDING |
| Source integrity | PASS |
| P07/P08 scope | PRESERVED |

### 2.1. Tính đúng

Ba backend sử dụng cùng một đối tượng mô hình P02, cùng trọng số, cấu hình, token đầu vào và phương pháp sinh greedy bằng `argmax`.

Hàm `validate_triplet()` kiểm tra chuỗi token sinh và toàn bộ vector logits ở mỗi bước.

Kết quả Windows:

- Số token sinh: 6 mỗi workload.
- Sai khác logits tối đa: `2.980232238769531e-7`.
- Ngưỡng: `atol=rtol=2e-5`.
- Dense và Paged có logits trùng nhau trong fixture.

**Kết luận:** PASS trong các cấu hình tổng hợp đã kiểm tra.

### 2.2. Độ phủ kiểm thử

Đã đọc 16 unit tests.

Bộ kiểm thử bao gồm đầu vào không hợp lệ, context overflow, thiếu KV block, kiểm tra không cập nhật cache một phần khi OOM, cách ly hai request, giải phóng cache và phát hiện sai lệch logits/token được cố tình đưa vào.

Log Windows xác nhận `Ran 16 tests ... OK`.

Độ phủ hiện tại đủ hỗ trợ kết luận tính đúng trong fixture được khai báo. Kiểm thử đường dẫn Windows junction còn thiếu và được ghi thành finding bên dưới.

### 2.3. Bộ nhớ KV

Công thức cho cấu hình hiện tại:

`bytes_per_token = 2 layers × 2 (K,V) × 4 heads × 16 head_dim × 4 bytes = 1,024 bytes`

Với hai request dài 13 và 5 token:

| Chỉ số | Dense | Paged |
| --- | --- | --- |
| KV pool allocated | 65,536 | 65,536 |
| Request reserved | 65,536 | 24,576 |
| Logical KV used | 18,432 | 18,432 |
| Internal fragmentation | 47,104 | 6,144 |

Các phép tính khớp dữ liệu lưu trữ.

**Kết luận:** Paged giảm dung lượng dành riêng đang hoạt động trong tình huống này. Tổng dung lượng tensor KV đã cấp phát bằng Dense.

Peak RAM chưa được đo.

### 2.4. Benchmark

Windows sử dụng Python 3.12.10, PyTorch 2.11.0+cpu, CPU float32 và hai luồng Torch.

Hợp đồng đo:

- Warmups: 2.
- Repeats: 5 mỗi backend.
- Prompt lengths: 4, 11, 16.
- TTFT gồm bắt đầu request, prefill và token đầu tiên.
- TPOT đo năm bước sinh token tiếp theo.
- Thời gian tạo cache được ghi riêng.
- Thứ tự đo luân phiên theo repeat.

No-cache xử lý prefill bằng phép tính ma trận, còn Dense/Paged thực hiện lần lượt từng token. Điều này hạn chế khả năng so sánh TTFT như một phép thử hiệu năng kiến trúc công bằng.

Số lần đo nhỏ, không có khoảng tin cậy hiệu năng và không có peak RSS.

**Kết luận:** Các thời gian được chấp nhận làm kết quả mô tả của fixture CPU. Chưa đủ điều kiện kết luận tăng tốc tổng quát.

## 3\. Kiểm toán bằng chứng Windows

Reviewer đọc nội dung Git blob nguyên byte và tự tính lại SHA-256.

| Hiện vật | SHA-256 | Kết quả |
| --- | --- | --- |
| Unit test log | `2f063493c448723ae9fcfd2d2ca364bb0374dcdf1369558c9302669924c93590` | PASS |
| Benchmark JSON | `39275324dc56c2bbfb075e73991cf4383f48bdc38acdaf182c66178b42e113b0` | PASS |
| QA JSON | `2525b423dac500c19810e4c66a301939bf0e4083ceeeb0a779509c41783b6591` | PASS |
| Owner receipt | `742247aaa64701d6e09964db8a0724c2980bccaf9ffe533402703dd8e7b327c6` | PASS |

Cả bốn SHA khớp.

QA JSON ghi 33 kiểm tra đều PASS. Hiện vật đối chiếu chéo ghi `PASS_17_OF_17`.

Reviewer đối chiếu các giá trị chủ chốt với dữ liệu JSON và mã nguồn. Các kết quả kiểm toán này xác nhận tính nhất quán và nguồn gốc lưu trữ, với phạm vi độc lập giới hạn ở đọc lại, đối chiếu và kiểm toán tĩnh.

Không chạy lại benchmark Windows.

## 4\. Findings

### F-01 — HIGH — Thiếu bảo vệ Windows junction ở công cụ Python

**Trạng thái:** BLOCKER

**Vị trí:**

`tools/t6/cache_ab_benchmark_fixture.py:322-335`

`tools/t6/independent_scoped_qa.py:88-100`

**Bằng chứng:**

Hàm `_ensure_safe_output()` kiểm tra các thành phần đường dẫn và `Path.is_symlink()` nhưng chưa kiểm tra Windows junction.

Reviewer kiểm tra thực tế bằng Python 3.12 trên Windows:

`C:\Documents and Settings`

cho kết quả:

`is_symlink() = False`  
`is_junction() = True`

Nếu một thư mục cha của output trong `artifacts/qa/t6` là junction trỏ ra ngoài repository, kiểm tra `is_symlink()` không chặn đường dẫn đó.

Công cụ QA độc lập cũng chưa kiểm tra symlink/junction cho các đường dẫn input/output.

Script PowerShell chính thức có kiểm tra thuộc tính `ReparsePoint` tại các thư mục evidence. Bảo vệ này bao phủ đường chạy chính thức đã rà soát, nhưng không bao phủ trường hợp gọi trực tiếp hai công cụ Python.

**Ảnh hưởng:** Chưa bảo đảm đầy đủ ràng buộc ghi hiện vật bên trong project root cho các entry point Python.

**Yêu cầu sửa tối thiểu:**

Bổ sung kiểm tra junction/reparse point, xác minh đường dẫn sau khi resolve vẫn thuộc project root, đồng thời bổ sung negative tests cho các trường hợp này.

Kiểm tra lại bản sửa bằng QA riêng. Không cần chạy lại benchmark Windows đã tiêu thụ nếu mã inference và đo lường không thay đổi.

### F-02 — MEDIUM — Giới hạn tính công bằng của phép đo TTFT

**Trạng thái:** NON-BLOCKING cho phạm vi descriptive CPU.

**Vị trí:**

`tools/t6/cache_ab_benchmark_fixture.py:137-176`

`tools/t6/cache_ab_benchmark_fixture.py:228-259`

**Bằng chứng:**

No-cache sử dụng vectorized prefill. Dense và Paged xử lý prefill tuần tự.

Cơ chế warmup và xoay thứ tự giảm một phần thiên lệch, nhưng chưa chuẩn hóa các thuật toán prefill.

Với năm repeats, thống kê P95 theo nearest-rank tương ứng giá trị lớn nhất của năm mẫu. Chưa có khoảng tin cậy cho chênh lệch hiệu năng.

**Đánh giá:** Các giới hạn đã được công bố trong báo cáo Windows.

**Yêu cầu:** Giữ nhãn `DESCRIPTIVE_ONLY`. Nếu muốn kết luận hiệu năng kiến trúc, cần một benchmark có phương pháp đối chứng và thống kê phù hợp hơn.

### F-03 — LOW — Tài liệu replay cần đánh dấu trạng thái lịch sử

**Trạng thái:** NON-BLOCKING.

**Vị trí:**

`tools/t6/README.md:69-93`

**Bằng chứng:**

README vẫn chứa hướng dẫn bootstrap/replay Windows được viết trước khi owner hoàn thành lượt one-shot.

**Yêu cầu:** Ghi rõ đây là hướng dẫn lịch sử của lần thực thi đã hoàn tất để tránh chạy lại một lượt đo đã tiêu thụ.

## 5\. Phán quyết độc lập

### `HOLD_REQUIRED_FIX_OR_EVIDENCE`

Lý do duy nhất ở mức chặn merge là F-01.

Mã inference, phép so sánh logits, kiểm thử CPU tổng hợp, số học KV và bốn hiện vật Windows đã qua kiểm tra trong phạm vi khai báo.

Không phát hiện sai lệch nghiêm trọng về logits, token, nguồn P02/P05/P06 hoặc tính toàn vẹn của bốn hiện vật gốc.

## 6\. Khuyến nghị merge

### `MERGE_HOLD`

Điều kiện để đánh giá lại thành `MERGE_CANDIDATE`:

1. Tác giả xử lý F-01 trên nhánh PR #15.
2. Bổ sung negative tests cho junction/reparse point và đường dẫn thoát project root.
3. Reviewer độc lập xác minh bản sửa trên HEAD mới.
4. Kiểm tra các thay đổi tiếp tục nằm trong phạm vi PR T6.
5. Chủ dự án ban hành quyết định merge riêng.

Không yêu cầu mở lại benchmark Windows chỉ vì bản sửa kiểm tra đường dẫn.

## 7\. Trạng thái bàn giao

| Thành phần | Trạng thái |
| --- | --- |
| DISTINCT\_REVIEW | COMPLETED |
| REVIEW\_DECISION | HOLD\_REQUIRED\_FIX\_OR\_EVIDENCE |
| MERGE\_RECOMMENDATION | MERGE\_HOLD |
| PR15 | OPEN / DRAFT |
| MAIN | UNCHANGED |
| LINEAGE | UNCHANGED |
| P07 | PAUSED\_PRESERVE |
| P08 | NOT\_OPENED |
| WINDOWS\_ONE\_SHOT | PRESERVED |
| NEW\_TRAINING | NOT\_EXECUTED |
| TEST/Q1Q2 | UNTOUCHED |

**Báo cáo được bàn giao dưới dạng văn bản.** Chưa ghi hoặc commit báo cáo vào repository, vì quyền commit reviewer chưa được cấp. SHA-256 của báo cáo sẽ được xác định khi lưu thành tệp chính thức.

## 8\. Bước thực hiện tiếp theo

`TTM_T6_PR15_F01_PATH_CONTAINMENT_AUTHOR_FIX_AND_DISTINCT_REREVIEW`

Tác giả sửa F-01, kiểm tra âm tính trên Windows và chuyển HEAD mới để reviewer đánh giá lại.

Sau khi đạt điều kiện review, chuyển về:

`TTM_T6_PR15_CODEX_DISTINCT_REVIEW_EVIDENCE_AND_OWNER_MERGE_GATE`

Quyền quyết định merge cuối cùng thuộc chủ dự án.

**Trạng thái cuối:** Đã hoàn tất review và dừng tại merge decision gate. Không sửa mã nguồn, không commit, không merge và không thực hiện lượt huấn luyện hoặc benchmark mới.
