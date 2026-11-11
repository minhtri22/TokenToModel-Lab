# TTM-Small-4M O0 — Tiếp nhận AC theo ủy nhiệm của owner, xử lý Windows V2 và quay về nhánh hậu CF1

**Ngày:** 2026-11-11  
**Operation:** `TTM_SMALL4M_ORIGINAL_O0_OBJECTIVE_SIGNAL_AC_COMPLETION_OWNER_DELEGATED_AND_RETURN_TO_POST_CF1`  
**Địa điểm biên bản:** nhánh `research/ttm-small4m-post-cf1-language-fresh-gap-reconcile-20261111`.  
**Tình trạng thật:** `AC_NATIVE_V2_STAGED_ON_WINDOWS` · `AC_REAL_SCIENCE_NOT_EXECUTED` · `O0_CAUSAL_DECISION=HOLD`.

## 1. Phạm vi thay đổi theo yêu cầu mới của owner

Owner yêu cầu không chờ agent AC mà tự tiếp nhận xử lý AC rồi quay về nhánh hậu CF1. Vì vậy lượt này đã đọc nguồn AC và thực tế Windows, xử lý **phần triển khai có thể hoàn thành qua kênh kết nối**; không mạo nhận đã đóng các điều kiện đòi quyền owner, người chấm hoặc phiên GPU Colab. Không thay hợp đồng A/C đã khóa và không can thiệp FRESH16.

## 2. Bằng chứng thực tế vừa thu được

- GitHub AC trước thao tác: `837289fda82b41653a61b74e476f76a0b4c4137c`; mã script sửa V2 `tools/pilot_t4/prompt_conditioning_2x2/Invoke-TTM-AC-Final-Preexec-PS51.ps1`, Git blob `7b7cac6d4cb0e68b0b91a3dc9fd22862d0b0b05b`.
- Windows máy `DESKTOP-4PSD0G2` đang ONLINE; đã đọc biên nhận cũ `_tmp/TTM_AC_NATIVE_PREEXEC_6628401b08ea/NATIVE_SOURCE_QA_RESULT.json`: `HOLD_NATIVE_QA_FAILED`; source Git blob exact=TRUE, syntax compile=TRUE, source-qa=TRUE, kiểm thử đầu tiên ghi `ok`; quy tắc PowerShell 5.1 bắt stderr đã che trạng thái thực của cả 6 test, nên **không được khẳng định 6/6 FAIL hoặc PASS**.
- Đã **ghi thật** V2 đã ghim SHA vào `D:\WORK\RESEARCH\TokenToModel-Lab\_tmp\Invoke-TTM-AC-Final-Preexec-V2-20261111.ps1` bằng RemoteDesktop, sau đó **đọc lại xác nhận** script V2 hiện hữu. Script sử dụng tệp stdout/stderr tách biệt cho unittest, xuất biên nhận vào `_tmp/TTM_AC_NATIVE_PREEXEC_STDERR_FIX_V2_6628401b08ea/NATIVE_SOURCE_QA_RESULT.json`, từ chối ghi đè.
- Kênh RemoteDesktop `run_command` và `job_submit` đều trả `managed mode requires task_job_submit`. Cổng theo trạng thái thiết bị ghi `research_adapter_enabled=false`, `new_job_admission_allowed=false`, `SCIENCE_DISPATCH_QUARANTINED`. Kênh recipe nguồn kiểm thử thử vận hành không trả được kết quả QA. Không tạo task/worktree ngoài project root để né chặn, không tự bật Research Adapter.
- Tệp giữ mù AC của owner đã được tìm thấy ở thư viện tệp riêng tư; **không công bố nội dung, không sao chép sang Windows khi chưa chứng thực ACL owner-only**.
- Biên nhận mới trên chính nhánh AC: `artifacts/qa/ttm-small4m-prompt-conditioning/ac_preexec/TTM_AC_WINDOWS_V2_STAGED_REMOTE_EXECUTION_LIMIT_20261111.json`, commit `2b3534697ced441eb0b1759b9684ae9fb33c3a23`, Git blob `0d3424eab7e1b32cb3c165a6e6ac2d858e7b8f59`.

## 3. Đánh giá đúng mức khoa học

| Hạng mục | Kết quả |
|---|---|
| Nguồn A/C và các kiểm nguồn trước đây | `PASS_SCOPED` giữ nguyên |
| Script sửa lỗi Windows V2 | `STAGED_AND_READBACK`, chưa thực thi |
| Windows native six-test V2 | `NOT_EXECUTED` |
| T4 FP16 zero-step smoke và actual interrupted resume parity | `NOT_EXECUTED` |
| Quyền dùng private TRAIN/VAL và xác nhận khóa escrow owner-only | `HOLD` |
| Người chấm FINAL24 riêng và mù trước giải mã | `HOLD` |
| A/C hai arm, 128 optimizer steps/arm, đo FINAL24 | **`NOT_EXECUTED`** |
| Tác động C−A | **`NOT_ESTIMABLE`** |

**Kết luận:** `AC_COMPLETION=BLOCKED_BY_EXECUTION_TRANSPORT_AND_UNATTESTED_OWNER_SCIENCE_GATES`; `O0_CAUSAL_DECISION=HOLD`. Đây là chặn về điều kiện thực thi, **không phải khoa học FAIL** của O0, AC hay giả thuyết loss. Không mở B/D hoặc O1. Không thay `lineage.md` vì chưa có kết quả khoa học PASS/FAIL được phân xử.

## 4. Một thao tác Windows bắt buộc nếu muốn tiếp tục AC trên chính máy owner

Đã đặt đúng script V2 trên Windows; lệnh **duy nhất** chủ máy có thể thực hiện trong PowerShell 5.1:

```powershell
powershell.exe -NoProfile -ExecutionPolicy Bypass -File "D:\WORK\RESEARCH\TokenToModel-Lab\_tmp\Invoke-TTM-AC-Final-Preexec-V2-20261111.ps1"
```

Đây là chạy kiểm tra nguồn và sáu test CPU tổng hợp, **không huấn luyện, suy luận hoặc đọc TEST**. Không chạy lại V1; script V2 có thư mục riêng, chống ghi đè. Sau khi có biên nhận thực, vẫn cần đóng **một gói tổng hợp**: quyền owner với private pack, khóa giữ mù ACL đúng, người chấm độc lập, T4 zero-step và actual resume, một quyết định owner science duy nhất. Không cấp các micro-permit riêng.

**Không có lệnh GPU nào đã được khởi động và không có cơ chế tự chạy Colab từ kết nối hiện tại**. Không lập kết quả giả.

## 5. Bước thực hiện tiếp theo

`TTM_AC_NATIVE_V2_EXACT_WINDOWS_RECEIPT_THEN_SINGLE_OWNER_AC_SCIENCE_CLOSEOUT`

Nếu đã có biên nhận Windows V2, đối chiếu nó và toàn bộ điều kiện owner/rater/T4 trong **một quyết định AC**; nếu thiếu, giữ HOLD. Khi AC thật sự hoàn tất và FINAL24 được phân xử, quay lại nhánh hậu CF1 đo `C−A` theo ngưỡng đã khóa. Không tự cập nhật định nghĩa kết quả.

**Bất biến:** `O0_SOURCE=PINNED` · `T4_VAL_H1=PASS` · `FRESH16_AGENT=UNCHANGED_BY_THIS_TASK` · `AC_NEW_TRAINING=0` · `AC_NEW_INFERENCE=0` · `TEST_Q1Q2=UNTOUCHED` · `B/D=DEFER` · `O1=DEFER` · `MAIN/LINEAGE=UNMODIFIED`.
