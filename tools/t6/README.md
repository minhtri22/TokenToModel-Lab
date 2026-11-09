# TTM-T6 — CPU No-cache / Dense KV / Paged KV A/B fixture

**Trạng thái:** `SYNTHETIC_CPU_FIXTURE_PASS_SCOPED`. Không mở P07/P08, không dùng model checkpoint T4, TEST, dữ liệu TRAIN/VAL hoặc GPU. GitHub là nguồn sự thật.

## Tại sao ba đường so sánh khác nhau?

- **No-cache (P02):** mỗi bước tính lại logits của toàn bộ chuỗi prefix bằng forward ma trận, không giữ KV liên tục.
- **Dense KV (P05):** prefill từng token, lưu K/V trong bộ đệm cấp đủ `max_seq_len` cho từng request; TPOT chỉ thêm 1 token.
- **Paged KV (P06):** prefill từng token, lưu K/V trong fixed physical pool + bảng trang; thống kê `allocated` vật lý tách khỏi `reserved` cho request, `used` logic và `fragmentation`.

Dùng cùng seed 60609, P02 synthetic CPU float32, context32, 2 layers/4 heads/64 embd, max 6 output tokens từ prompt mẫu 4, 11, 16 IDs. Cùng thuật toán `argmax` cho cả ba mode; logits mỗi bước phải khớp P02 trong `atol=rtol=2e-5` và chuỗi token sinh phải trùng tuyệt đối.

**TTFT** đo từ lúc bắt đầu request (gồm `cache.start`) đến khi tính xong token đầu. **TPOT** đo các bước từ token thứ hai, trên mỗi request (5 bước). **Cache constructor/pool creation** nằm ngoài TTFT; thời gian tạo cache được ghi riêng để tránh diễn giải không công bằng. Bộ đo luân phiên thứ tự backend mỗi repeat.

## Chạy trên Windows 11 / Python 3.12 (không cần Colab)

### Khôi phục sau lỗi `GIT_ROOT_EXIT_-1` (PowerShell 5.1)

Nếu `git fetch` và `git worktree add` đã thành công, nhưng launcher cũ
dừng ở `GIT_ROOT_EXIT_-1`, thì **chưa chạy unit test/benchmark**. Lỗi đã
được sửa bằng cách thu trọn đầu ra Git, không dùng
`git ... | Select-Object -First 1` (pipeline sớm ngắt native process).

**Tái sử dụng worktree đã tồn tại**, không tạo bản thứ hai. Dùng PowerShell:

```powershell
$ErrorActionPreference = 'Stop'
$root = 'D:\WORK\RESEARCH\TokenToModel-Lab'
$wt = Join-Path $root '.worktrees\ttm-t6-pr15-20261109'
$branch = 'feature/ttm-t6-dense-paged-ab-benchmark-fixture-20261109'
$old = '2f8709aa1148c92d8b9535ac51231ebabcdda443'
$new = '<EXACT_NEW_PR15_HEAD_SHA>' # pin 40 hex digits from GitHub PR #15

if (-not (Test-Path -LiteralPath $wt -PathType Container)) { throw 'WORKTREE_MISSING' }
$remote = & git -C $root ls-remote origin "refs/heads/$branch"
if ($LASTEXITCODE -ne 0 -or -not $remote) { throw 'REMOTE_LOOKUP_FAILED' }
if (($remote -split '\s+')[0] -ne $new) { throw 'REMOTE_HEAD_CHANGED' }
& git -C $root fetch --no-tags origin "refs/heads/$branch"
if ($LASTEXITCODE -ne 0) { throw 'FETCH_FAILED' }
if ((& git -C $root rev-parse FETCH_HEAD).Trim() -ne $new) { throw 'FETCH_HEAD_DRIFT' }
$before = (& git -C $wt rev-parse HEAD).Trim()
if ($LASTEXITCODE -ne 0 -or $before -ne $old) { throw 'UNEXPECTED_WORKTREE_HEAD' }
$dirty = @(& git -C $wt status --porcelain)
if ($LASTEXITCODE -ne 0 -or $dirty.Count -ne 0) { throw 'WORKTREE_DIRTY_ABORT' }
& git -C $wt switch --detach $new
if ($LASTEXITCODE -ne 0) { throw 'WORKTREE_SWITCH_FAILED' }

& powershell.exe -NoProfile -ExecutionPolicy Bypass -File (Join-Path $wt 'tools\t6\run_windows_exact_head.ps1') -PinnedHead $new -RepoRoot $root
if ($LASTEXITCODE -ne 0) { throw 'T6_REPLAY_FAILED' }
```

Không dùng `reset --hard`, không xóa worktree, không sửa checkout main.
Đoạn này chỉ phù hợp khi worktree ở **đúng HEAD cũ và sạch**; nếu đã có
file evidence hoặc local changes, dừng và kiểm tra trước.

**Quan trọng:** bộ kiểm thử nằm trên nhánh PR #15, **không** có sẵn ở checkout main cũ.
Nếu chạy `python -m unittest discover -s tests/t6` từ main, bạn có thể gặp
`ImportError: Start directory is not importable: 'tests/t6'`; đó là lỗi chọn
checkout, **không phải thất bại của testcase T6**.

Bộ chạy chính thức: [`run_windows_exact_head.ps1`](run_windows_exact_head.ps1). Nó:

1. Kiểm tra thư mục dự án, URL GitHub origin, SHA chính xác của nhánh PR #15;
2. Fetch và tạo detached worktree mới **bên trong root dự án**, dưới `.worktrees/ttm-t6-pr15-20261109` (không checkout/reset main);
3. Dừng nếu worktree hoặc đầu ra không đúng / đã có, không ghi đè evidence;
4. Chạy Python 3.12/PyTorch CPU, 16 unittest; chỉ khi PASS mới chạy 3 chế độ và QA độc lập 33/33;
5. Ghi bốn hiện vật vào `artifacts/qa/t6/` của worktree: log unittest, kết quả benchmark Windows, QA và owner receipt với SHA256.

**Bootstrap một lần từ PowerShell 5.1** (thay `<EXACT_PR15_HEAD_SHA>` bằng SHA-1
40 ký tự của HEAD PR #15 hiện đã được chủ dự án chấp thuận, không dùng HEAD
động không kiểm tra):

```powershell
$ErrorActionPreference = 'Stop'
$root = 'D:\WORK\RESEARCH\TokenToModel-Lab'
$expected = '<EXACT_PR15_HEAD_SHA>'
$branch = 'feature/ttm-t6-dense-paged-ab-benchmark-fixture-20261109'
$wt = Join-Path $root '.worktrees\ttm-t6-pr15-20261109'
$remote = & git -C $root ls-remote origin ('refs/heads/' + $branch)
if ($LASTEXITCODE -ne 0 -or -not $remote) { throw 'T6_REMOTE_LOOKUP_FAILED' }
if (($remote -split '\s+')[0].ToLowerInvariant() -ne $expected.ToLowerInvariant()) { throw 'T6_REMOTE_HEAD_DRIFT' }
& git -C $root fetch --no-tags origin ('refs/heads/' + $branch)
if ($LASTEXITCODE -ne 0) { throw 'T6_FETCH_FAILED' }
$actual = (& git -C $root rev-parse FETCH_HEAD).Trim()
if ($actual -ne $expected) { throw 'T6_FETCH_SHA_MISMATCH' }
if (-not (Test-Path -LiteralPath $wt)) {
    New-Item -ItemType Directory -Path (Split-Path -Parent $wt) -Force | Out-Null
    & git -C $root worktree add --detach $wt $expected
    if ($LASTEXITCODE -ne 0) { throw 'T6_WORKTREE_CREATE_FAILED' }
}
& powershell.exe -NoProfile -ExecutionPolicy Bypass -File (Join-Path $wt 'tools\t6\run_windows_exact_head.ps1') -PinnedHead $expected
if ($LASTEXITCODE -ne 0) { throw 'T6_WINDOWS_REPLAY_FAILED' }
```

Không dùng `git switch` trên root hoặc reset những nhánh khác. Không xóa worktree
khi có evidence; việc dọn dẹp chỉ sau owner adjudication.

**Đo có giới hạn:** warmups=2, repeats=5, block_size=4, synthetic tokens,
không tính model load vào TTFT. Kết quả Windows so với Linux chỉ là hai môi trường
tham khảo, **không được suy ra speedup CPU/GPU**. Trường `hardware.platform` và
`measurement_contract.device` phải hiện chính xác Windows trong lượt replay.

**Chú thích provenance sau sửa tài liệu:** báo cáo Linux và 16/16 + 33/33
đã commit thuộc *runner gốc* Git blob `07693ea446e4747bd987570fc7f645cd4fabafff`.
Runner trên nhánh hiện có Git blob mới
`85795ada12f283c88dcd01091b54f604e57e2418`, chỉ sửa trường
`measurement_contract.device` từ nhãn Linux hardcode sang nhãn OS đo
thực tế. **Chưa tuyên bố đã chạy lại QA/bộ đo sau sửa nhãn;** Windows replay
là lượt độc lập cần thực hiện đúng HEAD mới. Các nguồn P02/P05/P06 không đổi.

## Nguồn và kết quả đã commit

- `tools/t6/cache_ab_benchmark_fixture.py`: runner, khóa Git blobs P02/P05/P06.
- `tests/t6/test_cache_ab_fixture.py`: 16 unittest (đầu vào âm tính, parity, tính byte và cô lập request).
- `tools/t6/independent_scoped_qa.py`: 33 phép kiểm số học/receipt không chạy lại mô hình.
- `artifacts/qa/t6/TTM_T6_SYNTHETIC_CPU_AB_20261109.json`: phép đo CPU Linux ngoài máy dev; không có checkpoint/corpus.
- `artifacts/qa/t6/TTM_T6_INDEPENDENT_QA_20261109.json`: 33/33, chỉ QA vật liệu.
- `docs/t6/TTM_T6_CPU_NO_CACHE_DENSE_PAGED_AB_SCOPED_RESULTS_20261109.md`: báo cáo tham khảo.

**Không tuyên bố Paged nhanh hơn hoặc tiết kiệm tổng RAM**. Kịch bản 2 request có `KV pool allocated` đều 64 KiB, mặc dù `reserved active` ở Paged thấp hơn. RSS được lấy mẫu theo tiến trình, không phải peak sử dụng bộ nhớ của từng mode.

**Bước thực hiện tiếp theo:** `TTM_T6_WINDOWS_EXACT_HEAD_REPLAY_AND_SCOPED_INDEPENDENT_REVIEW`. Xác minh source/pin, chạy CPU Windows ở một output mới và phân xử phạm vi kỹ thuật trước merge. Giữ `main`, `lineage.md`, P07/P08 bất biến.
