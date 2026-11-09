# TTM-T6 — CPU No-cache / Dense KV / Paged KV A/B fixture

**Trạng thái:** `SYNTHETIC_CPU_FIXTURE_PASS_SCOPED`. Không mở P07/P08, không dùng model checkpoint T4, TEST, dữ liệu TRAIN/VAL hoặc GPU. GitHub là nguồn sự thật.

## Tại sao ba đường so sánh khác nhau?

- **No-cache (P02):** mỗi bước tính lại logits của toàn bộ chuỗi prefix bằng forward ma trận, không giữ KV liên tục.
- **Dense KV (P05):** prefill từng token, lưu K/V trong bộ đệm cấp đủ `max_seq_len` cho từng request; TPOT chỉ thêm 1 token.
- **Paged KV (P06):** prefill từng token, lưu K/V trong fixed physical pool + bảng trang; thống kê `allocated` vật lý tách khỏi `reserved` cho request, `used` logic và `fragmentation`.

Dùng cùng seed 60609, P02 synthetic CPU float32, context32, 2 layers/4 heads/64 embd, max 6 output tokens từ prompt mẫu 4, 11, 16 IDs. Cùng thuật toán `argmax` cho cả ba mode; logits mỗi bước phải khớp P02 trong `atol=rtol=2e-5` và chuỗi token sinh phải trùng tuyệt đối.

**TTFT** đo từ lúc bắt đầu request (gồm `cache.start`) đến khi tính xong token đầu. **TPOT** đo các bước từ token thứ hai, trên mỗi request (5 bước). **Cache constructor/pool creation** nằm ngoài TTFT; thời gian tạo cache được ghi riêng để tránh diễn giải không công bằng. Bộ đo luân phiên thứ tự backend mỗi repeat.

## Chạy trên Windows 11 / Python 3.12 (không cần Colab)

Các lệnh dưới đây chỉ đọc mã và ghi một JSON mới bên trong **chính worktree dự án**, không tạo file ở ổ C:\ root:

```powershell
$ErrorActionPreference = 'Stop'
$root = 'D:\WORK\RESEARCH\TokenToModel-Lab'
$python = 'C:\Users\minht\AppData\Local\Programs\Python\Python312\python.exe'
if (-not (Test-Path -LiteralPath $root -PathType Container)) { throw 'TTM_PROJECT_ROOT_NOT_FOUND' }
if (-not (Test-Path -LiteralPath $python -PathType Leaf)) { throw 'PYTHON312_NOT_FOUND' }
Push-Location -LiteralPath $root
try {
    & $python -c "import sys,torch; assert sys.version_info[:2]==(3,12); print(torch.__version__)"
    if ($LASTEXITCODE -ne 0) { throw 'PYTHON_OR_TORCH_CHECK_FAILED' }

    & $python -m unittest discover -s tests/t6 -v
    if ($LASTEXITCODE -ne 0) { throw 'T6_UNITTEST_FAILED' }

    & $python tools/t6/cache_ab_benchmark_fixture.py `
        --warmups 2 --repeats 5 --block-size 4 `
        --output artifacts/qa/t6/TTM_T6_WINDOWS_CPU_AB_OWNER_RUN.json
    if ($LASTEXITCODE -ne 0) { throw 'T6_CPU_AB_BENCHMARK_FAILED' }
}
finally { Pop-Location }
```

*Lưu ý:* Lệnh trên là script bàn giao, **chưa được chạy trên Windows** trong phiên tạo fixture. Nếu tên output đã tồn tại, runner fail-closed, không ghi đè. Không chạy lặp lại kết quả đã được chủ dự án tiêu thụ; đổi tên chỉ khi phép chạy mới được chủ sở hữu phê duyệt.

Nếu chạy `independent_scoped_qa.py`, truyền chính xác `--report` và `--unittest-log` tương ứng; tool sẽ từ chối đường dẫn ngoài `artifacts/qa/t6` và không ghi đè JSON QA. Với luồng tích hợp, nên có biên bản CI/Windows chạy chính repo branch HEAD trước khi xem xét merge.

## Nguồn và kết quả đã commit

- `tools/t6/cache_ab_benchmark_fixture.py`: runner, khóa Git blobs P02/P05/P06.
- `tests/t6/test_cache_ab_fixture.py`: 16 unittest (đầu vào âm tính, parity, tính byte và cô lập request).
- `tools/t6/independent_scoped_qa.py`: 33 phép kiểm số học/receipt không chạy lại mô hình.
- `artifacts/qa/t6/TTM_T6_SYNTHETIC_CPU_AB_20261109.json`: phép đo CPU Linux ngoài máy dev; không có checkpoint/corpus.
- `artifacts/qa/t6/TTM_T6_INDEPENDENT_QA_20261109.json`: 33/33, chỉ QA vật liệu.
- `docs/t6/TTM_T6_CPU_NO_CACHE_DENSE_PAGED_AB_SCOPED_RESULTS_20261109.md`: báo cáo tham khảo.

**Không tuyên bố Paged nhanh hơn hoặc tiết kiệm tổng RAM**. Kịch bản 2 request có `KV pool allocated` đều 64 KiB, mặc dù `reserved active` ở Paged thấp hơn. RSS được lấy mẫu theo tiến trình, không phải peak sử dụng bộ nhớ của từng mode.

**Bước thực hiện tiếp theo:** `TTM_T6_WINDOWS_EXACT_HEAD_REPLAY_AND_SCOPED_INDEPENDENT_REVIEW`. Xác minh source/pin, chạy CPU Windows ở một output mới và phân xử phạm vi kỹ thuật trước merge. Giữ `main`, `lineage.md`, P07/P08 bất biến.
