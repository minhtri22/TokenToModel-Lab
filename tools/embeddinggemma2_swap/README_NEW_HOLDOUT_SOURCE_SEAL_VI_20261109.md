# TTM-Small-4M × EmbeddingGemma 2 — Hướng dẫn niêm phong nguồn mới (CPU)

**Phạm vi:** chỉ xác minh nguồn, khóa danh sách 320 truyện và kiểm thử bộ chấm trên dữ liệu tổng hợp. **Không có lệnh chấm mô hình trên tập mới, không GPU và không huấn luyện.**

Nguồn:
- `tools/embeddinggemma2_swap/ttm_gemma2_holdout_seal.py`, SHA-256 `0f494cc4efbfdb6aa6e8f04825ec1dda929c836a1ac981463f24eb2bd8d9c8e4`.
- `tools/embeddinggemma2_swap/ttm_gemma2_independent_cpu_scorer.py`, SHA-256 `de6ab9652bb690a6e967e752b9367f5755674a23a6c4b2fcb45941274612dfe1`.

## Chạy cục bộ bằng Python 3.12 (PowerShell 5.1)

Sau khi tải hai tệp đúng SHA-256 vào `D:\WORK\RESEARCH\TokenToModel-Lab\_tmp\ttm_gemma2_new_holdout_tools_v1` (đường dẫn nằm trong project), dùng:

```powershell
$ErrorActionPreference = 'Stop'
$repo = 'D:\WORK\RESEARCH\TokenToModel-Lab'
$py = 'C:\Users\minht\AppData\Local\Programs\Python\Python312\python.exe'
$tools = Join-Path $repo '_tmp\ttm_gemma2_new_holdout_tools_v1'
if (-not (Test-Path $py)) { throw 'PYTHON312_MISSING' }
& $py -B -c 'import sys; assert sys.version_info[:2] == (3,12)'
if ((Get-FileHash (Join-Path $tools 'ttm_gemma2_holdout_seal.py') -Algorithm SHA256).Hash.ToLowerInvariant() -ne '0f494cc4efbfdb6aa6e8f04825ec1dda929c836a1ac981463f24eb2bd8d9c8e4') { throw 'SOURCE_SHA_FAIL' }
if ((Get-FileHash (Join-Path $tools 'ttm_gemma2_independent_cpu_scorer.py') -Algorithm SHA256).Hash.ToLowerInvariant() -ne 'de6ab9652bb690a6e967e752b9367f5755674a23a6c4b2fcb45941274612dfe1') { throw 'SCORER_SHA_FAIL' }

& $py -B (Join-Path $tools 'ttm_gemma2_holdout_seal.py') --mode fixture-qa
if ($LASTEXITCODE -ne 0) { throw 'SOURCE_FIXTURE_QA_FAIL' }
& $py -B (Join-Path $tools 'ttm_gemma2_independent_cpu_scorer.py') --mode fixture-qa
if ($LASTEXITCODE -ne 0) { throw 'SCORER_FIXTURE_QA_FAIL' }

# Chỉ kiểm tra SHA-256 của hai nguồn gốc, T1 split và T1 tokenizer; không niêm phong:
& $py -B (Join-Path $tools 'ttm_gemma2_holdout_seal.py') --mode preflight --repo $repo
if ($LASTEXITCODE -ne 0) { throw 'SOURCE_PREFLIGHT_FAIL' }
```

Để **thực sự** kiểm toán toàn bộ TRAIN và niêm phong 320 truyện (CPU-only), chỉ sau khi xác nhận đủ RAM/dung lượng/nguồn, thực thi duy nhất một lần:

```powershell
& $py -B (Join-Path $tools 'ttm_gemma2_holdout_seal.py') --mode seal-membership --repo $repo
if ($LASTEXITCODE -ne 0) { throw 'MEMBERSHIP_SEAL_HOLD' }
```

**Chú ý:** mã sẽ quét tệp TRAIN 2 lần và VALID 1 lần, không tải dữ liệu từ Internet, không mở checkpoint và không tính NLL mô hình; nếu 320 truyện/50.000 nhãn không đạt sẽ dừng, không tự giảm điều kiện. Biên bản không nhạy cảm ở `_tmp/ttm_gemma2_new_holdout_membership_v1_20261109/SOURCE_SEAL_PUBLIC.json`, có SHA-256 đối chiếu `MEMBERSHIP_PRIVATE.json`. Không đăng private manifest trên GitHub.

Dùng `Get-FileHash` để kiểm tra hai tệp đã tải **trước bất kỳ thực thi nào**; không bật `ExecutionPolicy Bypass` toàn hệ thống. Nếu hệ thống yêu cầu bất kỳ thay đổi source/seed/thư mục nào, dừng và ghi HOLD; không sửa script đã ghim dưới cùng hợp đồng.
