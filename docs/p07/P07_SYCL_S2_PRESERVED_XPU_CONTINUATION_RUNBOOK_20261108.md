# TTM P07 — SYCL stage-only, kế thừa XPU đã PASS

**Ngày:** 08/11/2026. **Trạng thái:** `SOURCE_ONLY_STATIC_QA`; `S2_EXECUTION_NOT_AUTHORIZED`; không cài đặt trong bước tạo gói.

## Mục đích và nguồn

- Dự án: `https://github.com/minhtri22/TokenToModel-Lab.git`, local `D:\WORK\RESEARCH\TokenToModel-Lab`.
- Main gốc: `4731f75cda6aa86b1dd2929b3f10d11fbbed0812`.
- V1 pin P07: `4024941b96358828804ea77481e860550c5547a0`.
- V1 run đã tiêu thụ: `P07_GPU_ENABLEMENT_20261108T024525Z_P28364`, biên bản SHA-256 `9A619F41412A6BE87FCD7A307477A148AE80C6BD8801206CFC5791FB7AF3B647`.
- V1: `torch==2.12.1+xpu` trên Arc 140V: `PASS_REAL_GPU_COMPUTE`, `max_abs=3.725290298461914e-09`. V1 kết thúc `FAIL_OR_INCONCLUSIVE_NO_AUTORERUN` vì riêng bước XPU dùng `6.037 GiB > 6 GiB` ngân sách.
- V1 chỉ tải và cài PyTorch XPU, **chưa tải/cài SYCL**. V1 lock giữ nguyên, không xóa/đổi tên, không gọi lại Execute V1.

## Gói này làm gì?

`TTM_P07_SYCL_S2_PRESERVED_XPU_CONTINUATION_PS51_V1_20261108.ps1` mặc định `-Mode Preview`:

1. Xác minh Git origin / remote main / remote P07 HEAD, SHA-256 của receipt V1, trạng thái V1 và one-shot lock V1. Preview **không** tải, cài, tính GPU, ghi file hoặc cần xin phép.
2. **Execute chỉ sau khi chấp thuận riêng:** soát lại đầy đủ **30 wheel V1** theo kích thước và SHA-256, kiểm tra PyTorch **qua metadata pip show** (không chạy lại torch canary).
3. Tạo **lock S2 riêng** sau khi tất cả điều kiện nguồn, tài nguyên và quyền thực thi PASS; nếu tồn tại lock S2 thì dừng. Giữ nguyên lock V1.
4. Chỉ tải các package Conda compiler `dpcpp_win-64=2026.2.0` và `intel-sycl-rt=2026.2.0` qua hai channel Intel/conda-forge. Ghi SHA-256 từng archive sau `--download-only`, cài trong môi trường riêng `D:\WORK\RESEARCH\TokenToModel-Lab\_runtime\p07\sycl_conda` với `--offline`.
5. Chạy chính xác **một GPU canary SYCL/Level Zero** với page table và physical KV, `2 requests × 5 tokens × 2 heads × 3 dims`, qua 6 physical pages, blocksize 2. Phần đọc KV chạy trong kernel GPU và đối chiếu độc lập CPU. **Không gather toàn bộ KV history thành dense trước kernel**. Chỉ canary indexing, chưa làm đầy đủ Attention và logits P07.
6. Ghi một biên bản S2 riêng + logs. Nếu PASS chỉ dọn đúng `tmp\P07_SYCL_S2_<id>_owned` với sentinel, **không** xóa V1, `wheels`, `venv`, Conda cache, compiler env, evidence. Nếu FAIL lưu nguyên toàn bộ để chẩn đoán, **không tự rerun**.

## Giới hạn dung lượng

- Tổng dung lượng sử dụng mới của P07 từ snapshot trước V1: tối đa **18 GiB**.
- Đã sử dụng V1: **6.037 GiB**. Ngân sách cho S2 còn **11.963 GiB** (giới hạn kế hoạch).
- Cổng trước Execute: D: có ít nhất 24 GiB trống và phần còn có thể sử dụng ít nhất 8 GiB, RAM trống >= 8 GiB; ở mọi mốc cài giữ D: >= 12 GiB. Các ngưỡng được kiểm ở **ranh giới các bước**, không phải quota Windows cứng ngăn một lệnh tải ghi quá mức trong lúc nó đang chạy. Nếu tràn, dừng và lưu bằng chứng.
- Tất cả đường dẫn mới nằm trong `D:\WORK\RESEARCH\TokenToModel-Lab` (trừ khả năng cache/metadata hệ thống không thể tuyệt đối kiểm soát bởi Windows/Conda). Không đổi Miniforge base, Python seed, driver, PATH hệ thống, Windows.

## Trạng thái và rủi ro đã biết

- Một số bản Windows 11 Home không nằm trong ma trận GPU client được Intel chính thức kiểm định. Compiler có thể không cài/chạy được dù XPU đã PASS. Ghi FAIL có bằng chứng, không thay Windows hay driver.
- Conda resolver có thể không giải được phiên bản hoặc `--download-only`/`--offline` không tương thích phiên bản đang cài; stop, không fallback build, không đổi pin.
- `icx.exe` phải hiện diện chính xác trong conda env; MSVC BuildTools `vcvars64.bat` phải hoạt động. Không dùng CUDA/Triton thay thế.
- Để có `G1 PASS` vẫn cần kernel attention P07 thật, so sánh logits P02/P05/P06 và negative tests; GPU canary chưa đủ để đóng P07. P08 chưa mở.
- Mã `.ps1` có kiểm tra tĩnh ngoài Windows; **chưa chạy Windows PowerShell 5.1 Parser.ParseFile**. Hướng dẫn bên dưới tự kiểm tra cú pháp trước Preview.

## Lệnh Preview sau khi tải `.ps1` vào Downloads

```powershell
$ErrorActionPreference='Stop'
$script="$env:USERPROFILE\Downloads\TTM_P07_SYCL_S2_PRESERVED_XPU_CONTINUATION_PS51_V1_20261108.ps1"
$expected='<ĐIỀN SHA-256 TỪ MANIFEST TRONG ZIP>'
if ((Get-FileHash -LiteralPath $script -Algorithm SHA256).Hash -cne $expected) { throw 'P07_S2_SHA_MISMATCH' }
$tok=$null; $err=$null
[System.Management.Automation.Language.Parser]::ParseFile($script,[ref]$tok,[ref]$err)|Out-Null
if ($err.Count -ne 0) { throw 'P07_S2_PS51_PARSE_FAIL' }
powershell.exe -NoProfile -ExecutionPolicy Bypass -File $script -Mode Preview
if ($LASTEXITCODE -ne 0) { throw "P07_S2_PREVIEW_EXIT_$LASTEXITCODE" }
```

**Không chạy `-Mode Execute` trong bước này.** Cần chấp thuận mới: `TTM_P07_APPROVE_SYCL_STAGE_ONLY_PRESERVED_XPU_V1`. Sau chấp thuận sẽ chạy đúng một lượt có `-ExpectedP07Head` bằng HEAD GitHub đã pin; không tắt khóa S2 hay V1.

## Tài liệu bên ngoài đối chiếu

- [Intel oneAPI compiler qua Conda](https://www.intel.com/content/www/us/en/developer/tools/oneapi/dpc-compiler-download.html)
- [Conda-forge dpcpp_win-64 2026.2.0](https://anaconda.org/channels/conda-forge/packages/dpcpp_win-64/overview)
- [Conda-forge intel-sycl-rt win-64 2026.2.0](https://anaconda.org/conda-forge/intel-sycl-rt/files)
- [Intel oneAPI compiler 2026 release notes](https://www.intel.com/content/www/us/en/developer/articles/release-notes/oneapi-dpcpp/2026.html)
