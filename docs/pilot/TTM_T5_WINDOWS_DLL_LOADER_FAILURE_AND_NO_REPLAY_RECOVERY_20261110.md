# TTM T5 — lỗi thiếu DLL tại self-check và phục hồi từ binary gốc (2026-11-10)

**Task gốc:** `TTM_T5_KVFLASH_WINDOWS_STAGE_RECEIPT_READBACK_AND_SINGLE_NATIVE_RUN_DECISION`.

**Kết luận:** `BUILD=PASS` · `SYNTHETIC_UNIT_QA=PASS_13/13` · `SELF_CHECK=FAIL_LOADER_0xC0000135` · `REFERENCE_WINDOWS_IMPORT=NOT_EXECUTED` · `NATIVE=0/32` · `RUN_GATE=HOLD`.

## 1. Bằng chứng Windows đã kiểm tra

Đã đọc trực tiếp `D:\WORK\RESEARCH\TokenToModel-Lab\_tmp\ttm_t5_kvflash_binary_reference_stage_v1_20261110\STAGE_RECEIPT.json`, cùng các log `11_synthetic_python_qa.log`, `12_cmake_configure.log`, `13_cmake_build.log`, `14_compiled_no_model_self_check.log` trong cùng thư mục.

- Stage receipt owner SHA-256 `235f20131ffd9cfc76738da5956206b2e49ced30b8219864a3d3ce2b4ddb38a7`, `HOLD_STAGE_FAILED_CLOSED`. Old worktree HEAD `888adde84e0e4fbe8cbaae801ed4d9687e6b4bb8`.
- Synthetic protocol tests: thực tế `Ran 13 tests`, `OK`, exit 0.
- CMake/MSVC configure+build: exit 0, executable `_tmp\ttm_t5_kvflash_binary_reference_stage_v1_20261110\build\Release\ttm_t5_kvflash_probe.exe` đã sinh, SHA-256 `0da91785a0882dd1b5a04cce4dc050886b54e0fe0f17e66f66802638b3760537`.
- `--self-check`: exit `3221225781` = `0xC0000135` = Windows `STATUS_DLL_NOT_FOUND`; stdout/stderr trống. Đây là lỗi nạp executable trước khi chương trình hoàn thành, không phải thất bại liên quan logits.

### Phân biệt import LIB khi build vs DLL khi chạy

CMake dùng ba import libs ở `_tmp\ttm_t2\build\upstream_llama\src\Release` và `ggml\src\Release`: đúng và build PASS.

**Trong khi đó** cả `llama.dll`, `ggml.dll`, `ggml-base.dll`, `ggml-cpu.dll` được nhìn thấy trực tiếp trong `_tmp\ttm_t2\build\bin\Release` (**khác thư mục**). Điều phối stage ban đầu thêm nhầm `_tmp\ttm_t2\build\upstream_llama\bin\Release` (không tồn tại) cùng các thư mục chỉ chứa `.lib` vào `PATH`.

**Chẩn đoán:** `WRONG_DLL_SEARCH_DIRECTORY` là nguyên nhân rất có khả năng của `0xC0000135`. Cần kiểm chứng bằng thực tế self-check mới; không phủ nhận khả năng thiếu DLL thứ cấp.

## 2. Khắc phục hữu hạn: chỉ dùng lại binary đã tạo, không rerun 01–13

Nguồn chính thức: `tools/pilot_t5/kv_flash_precision_v1/recover_compiled_no_model_selfcheck_and_reference.py`, blob Git SHA-1 `5e2b88a9642125d6673b4f60adde1427efff89c3`.

Chạy trên Windows **Python 3.12**, theo quy trình ngắn ở cuối. Script này:
1. **Không ghi đè** `STAGE_RECEIPT.json` cũ. Kiểm chính xác SHA biên bản gốc, binary, source C++/CMake Git blobs, HEAD worktree lịch sử và các log build/13 test.
2. Kiểm 4 DLL đã được xác minh nằm trong `_tmp\ttm_t2\build\bin\Release`; ghi SHA từng DLL vào biên bản phục hồi.
3. Tạo subprocess `ttm_t5_kvflash_probe.exe --self-check`, **chỉ lệnh này**, với `PATH` được thêm đúng thư mục DLL, thời hạn cứng 45 giây; không tải model/không gọi `llama_decode`.
4. Đối chiếu dữ liệu `--self-check` với 8 fixture `SYN01..SYN08` và S0–S3 qua mã QA độc lập đã khóa.
5. Kiểm tra JSONL F32 thật ở `_tmp\ttm_t5_kvflash_reference_input_v1_20261110\REFERENCE_F32_SYN01_SYN08.jsonl`, SHA256 `d6f367269df610a4e1c93edbff9a4dcffb7f0e0b6bd5f77247c5c90394de176c`, 8×2048 logits bằng validator độc lập.
6. Ghi `_tmp\ttm_t5_kvflash_loader_recovery_v1_20261110\RECOVERY_RECEIPT.json` và 3 log độc lập. Nếu bất cứ bước nào FAIL thì receipt `HOLD_RECOVERY_FAILED_CLOSED`, **không retry/không overwrite**.

Không cần tải hoặc giải nén reference thêm lần nữa. Tệp JSONL đã hiện hữu trong project.

## 3. Quy tắc thực hiện chủ máy

```powershell
$ErrorActionPreference = 'Stop'
$root = 'D:\WORK\RESEARCH\TokenToModel-Lab'
$pin = '<CURRENT_COMMITTED_HEAD>'
$py = 'C:\Users\minht\AppData\Local\Programs\Python\Python312\python.exe'
$script = Join-Path $root '_tmp\ttm_t5_kvflash_loader_recovery_20261110.py'

$url = "https://raw.githubusercontent.com/minhtri22/TokenToModel-Lab/$pin/tools/pilot_t5/kv_flash_precision_v1/recover_compiled_no_model_selfcheck_and_reference.py"
Invoke-WebRequest -UseBasicParsing -Uri $url -OutFile $script

$gitExe = (Get-Command git.exe -CommandType Application).Source
$blob = (& $gitExe -C $root hash-object $script).Trim()
if ($LASTEXITCODE -ne 0 -or $blob -ne '5e2b88a9642125d6673b4f60adde1427efff89c3') {
    throw 'RECOVERY_SOURCE_PIN_MISMATCH'
}
& $py -m py_compile $script
if ($LASTEXITCODE -ne 0) { throw 'RECOVERY_PY312_PARSE_FAILED' }

& $py $script
if ($LASTEXITCODE -ne 0) { throw 'RECOVERY_HOLD_READ_NEW_RECEIPT' }
```

**Không chạy lại lệnh stage đã fail**, không chạy 32 lượt native; `main`, `lineage.md`, PR13, TEST/Q1Q2 và strict FAIL 7/8 đều giữ nguyên.

## 4. Cổng quyết định

- Khi kết quả `PASS_BINARY_SELF_CHECK_AND_REAL_REFERENCE_QA_NATIVE_32_HOLD`: mới đủ điều kiện xem xét một **owner run decision duy nhất** cho 32 native; không tự động thực thi.
- Khi `HOLD_RECOVERY_FAILED_CLOSED`: đọc đúng log tương ứng, không cố retry hoặc chạy Preview/Supplement.
- Biên bản stage cũ `235f2013...` vẫn là lịch sử không thể sửa hồi tố.

**Bước thực hiện tiếp theo:** `TTM_T5_KVFLASH_DLL_LOADER_RECOVERY_READBACK_AND_ONE_NATIVE_OWNER_DECISION`.
