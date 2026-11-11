# TTM-Small-4M O0 — Kết quả tiếp nhận AC: native Windows V2 PASS, hiệu ứng C−A chưa ước lượng

**Ngày:** 2026-11-11  
**Operation:** `TTM_SMALL4M_ORIGINAL_O0_OBJECTIVE_SIGNAL_AC_RESULT_ONLY_CAUSAL_DECISION_READBACK`, bổ sung sau khi owner thực hiện Windows native V2.  
**Phạm vi:** Nhánh `research/ttm-small4m-post-cf1-language-fresh-gap-reconcile-20261111`; không đổi nguồn mô hình O0, không sửa FRESH16/TEST/Q1Q2, không cho chạy science từ báo cáo này.

## 1. Bằng chứng mới thực tế, không chạy lại QA

Người vận hành cung cấp tệp thật `NATIVE_SOURCE_QA_RESULT.json` (SHA-256 `e471e884fbfa153ccef92bad9be2f44b625f62ddc51a3f1c6a9237767ffedcfa`). Biên nhận này được đối chiếu với `D:\WORK\RESEARCH\TokenToModel-Lab\_tmp\TTM_AC_NATIVE_PREEXEC_STDERR_FIX_V2_6628401b08ea\NATIVE_SOURCE_QA_RESULT.json` trên Windows và log stderr gốc. GitHub AC lưu bản nguồn byte-exact SHA-1 Git blob `8028d7e6cb0399fb2030de0e93c63d56522bc9e2` tại `artifacts/qa/ttm-small4m-prompt-conditioning/ac_preexec/TTM_AC_NATIVE_PY312_V2_ORIGINAL_OWNER_RECEIPT_20261111.json`.

- `source_git_blob_exact=true`, `syntax_compile=true`, `source_qa=true`; kiểm thử CPU tổng hợp `synthetic_resume_tests=true`, `exit_code=0`.
- Windows log đã được **đọc trực tiếp**: test_01..test_06 đều `ok`; `Ran 6 tests in 5.004s`, `OK`, không FAIL. Python 3.12.10, PyTorch 2.11.0+cpu, NumPy 2.4.4 theo console owner. Bản log được commit ở `artifacts/qa/ttm-small4m-prompt-conditioning/ac_preexec/TTM_AC_NATIVE_PY312_V2_SIX_TEST_STDERR_20261111.txt`.
- Biên nhận tổng hợp cổng AC mới `artifacts/qa/ttm-small4m-prompt-conditioning/ac_preexec/TTM_AC_NATIVE_V2_OWNER_READBACK_SINGLE_INTEGRATED_SCIENCE_READINESS_20261111.json`, commit nhánh AC `40fec1a906ee3c5703830b10b2d62c1a2513b701`.
- V1 `HOLD_NATIVE_QA_FAILED` là lỗi cách bắt stdout/stderr PowerShell 5.1, **được giải quyết** cho kiểm thử CPU V2; không được hồi tố cho V1 là kết quả PASS six-test.

**Quyết định kỹ thuật:** `AC_NATIVE_PY312_V2=PASS_SCOPED_NATIVE_PY312_SOURCE_AND_CPU_TOY_RESUME`. Phạm vi *toy resume* chỉ là mô hình Linear 3→2 dùng để kiểm cơ chế serializing state, không phải khôi phục mô hình TTM-Small-4M thật hoặc FP16 trên T4.

## 2. Kiểm chứng hiệu ứng C−A

| Bằng chứng | Trạng thái |
|---|---|
| O0 parent step1024, kiến trúc và pack | `PINNED_PRIOR_QA` |
| Thiết kế A uniform CE, C suffix-weighted CE cùng lịch draw | `FROZEN_DESIGN` |
| Windows Python312 native QA và toy CPU resume | **`PASS_SCOPED`** |
| Quyền private pack, khóa giải mù ACL owner-only và người chấm độc lập | `NOT_ALL_ATTESTED` |
| T4 FP16 zero-step smoke | `NOT_EXECUTED` |
| Actual Small4M interrupted resume parity | `NOT_EXECUTED` |
| Huấn luyện A và C đủ 128 bước/arm | `NOT_EXECUTED` |
| FINAL24 chấm mù, SHA freeze, score C−A | `NOT_EXECUTED / NOT_ESTIMABLE` |

Không có hiệu ứng objective thực tế được đo. Kết luận đúng: `OBJECTIVE_SIGNAL_CAUSAL_EFFECT=UNDETERMINED`, `DATA_WINDOW_CAUSE=UNPROVEN`, `CAPACITY_LIMIT=UNPROVEN`. Không ghi FAIL khoa học cho AC và không chuyển giả thuyết sang data/capacity bằng suy diễn.

## 3. Quyết định duy nhất hậu CF1

`GO_ACCEPT_AC_NATIVE_V2_PASS_SCOPED__HOLD_AC_SCIENCE_UNTIL_SINGLE_INTEGRATED_OWNER_CLOSEOUT`.

Từ thời điểm này, **không lặp** V1 hoặc V2; phần native Python312 source+toy resume đã hoàn tất. Gói khoa học còn lại do cùng owner thực hiện **một lần**: quyền dữ liệu và custody/ACL, người chấm FINAL24 độc lập, thử nghiệm T4 FP16 zero-step, actual interrupted resume trên đúng mô hình, một owner science lock cùng các mã băm runner/pack/checkpoint đã khóa, sau đó A/C one-shot và phân xử FINAL24. Đây là gói tích hợp, **không chia micro-permit**.

Không tự khởi chạy nhánh B/D hoặc O1, không dùng FRESH16 để đo `C−A`, không đụng TEST/Q1Q2/FRESH12/CF1; `main`, PR13 và `lineage.md` vẫn không đổi từ lượt này. `lineage.md` chỉ nhận kết quả khoa học PASS/FAIL sau phân xử, không ghi kỹ thuật native V2.

## Bước thực hiện tiếp theo

`TTM_SMALL4M_AC_SINGLE_INTEGRATED_T4_ACTUAL_RESUME_OWNER_SCIENCE_AND_FINAL24_ADJUDICATION_THEN_O0_READBACK`

Chỉ hoàn tất AC khi có quyền/custody/reviewer và năng lực thực thi T4 thật; không tự suy diễn hoặc tạo kết quả. Khi đó trở lại nhánh hậu CF1 dùng **kết quả chênh lệch C−A đã phân xử** để quyết định về hàm loss. Không cần chạy lại QA nguồn/native.

**Trạng thái:** `O0_SOURCE=PINNED` · `T4_VAL_H1=PASS` · `AC_NATIVE_V2=PASS_SCOPED` · `AC_SCIENCE=NO_GO_PREEXEC` · `C_MINUS_A=NOT_ESTIMABLE` · `DATA_WINDOW_CAUSE=UNPROVEN` · `CAPACITY_LIMIT=UNPROVEN` · `B/D=DEFER` · `O1=DEFER` · `NEW_TRAINING=NO` · `GPU=NO` · `TEST_Q1Q2=UNTOUCHED` · `MAIN/LINEAGE=UNMODIFIED`.
