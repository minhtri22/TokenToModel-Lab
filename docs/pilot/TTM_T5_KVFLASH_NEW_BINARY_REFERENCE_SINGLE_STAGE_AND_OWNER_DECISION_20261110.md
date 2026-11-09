## PHỤ LỤC KẾT QUẢ CẬP NHẬT 2026-11-10 — PYTORCH REFERENCE ĐÃ CHẠY THẬT

- Original T4 step1024 `checkpoint.pt` (45,074,891 bytes) lấy từ Google Drive hiện vật nguồn, SHA256 `cb985751795c8328ad65acf7ca4c1033ce35182c1bfbdb8c38550de629cb271b` **PASS**. Chỉ tải về môi trường tính toán riêng, không commit checkpoint lên GitHub công khai.
- Khớp nguyên bản P02 Git blob `9762343e06cf800b50574c2871ae1ed58537fb18`; checkpoint schema `ttm.t4.science.checkpoint.v1`, step1024, 3.749.376 parameters, trạng thái model strict load đúng; `torch 2.10.0+cpu`, `eval()/inference_mode()`.
- **8 fixture SYN01–SYN08 đã sinh đủ 8 × 2.048 = 16.384 logits F32 thực** (KHÔNG training, không dùng TEST, không rerun 8 fixture lịch sử). Output raw `REFERENCE_F32_SYN01_SYN08.jsonl` **324.123 bytes**, SHA256 `d6f367269df610a4e1c93edbff9a4dcffb7f0e0b6bd5f77247c5c90394de176c`.
- Đã đối chiếu độc lập cấu trúc 8 dòng/16.384 giá trị hữu hạn, từng token ID, source/checkpoint/prereg provenance. Bộ ZIP (không chứa checkpoint) SHA256 `6f260c7f52f906a693245f75a51b02fa9641ce34502eb9f2a0aff3c949315ce4` trên [Google Drive](https://drive.google.com/file/d/10tDE8IAVv68Gl_Dgx-t8g119V9Jf8ss4/view). GitHub là **source of truth cho biên bản/sha/trạng thái**, Drive chỉ giữ bằng chứng raw riêng tư. [Receipt canonical](../artifacts/qa/ttm-t5-parity/TTM_T5_F32_NEW_SYNTHETIC_REAL_CPU_REFERENCE_8X2048_QA_AND_GITHUB_SOURCE_OF_TRUTH_20261110.json).
- Windows candidate **chưa compile** (cổng thực thi RemoteDesktop từ chối); đã sửa đường build MSVC, thêm `--self-check`, và thêm `--existing-reference` cho stage Python3.12: chỉ nhập reference nói trên khi SHA khớp và verifier độc lập PASS, tránh đòi tải lại/checkpoint trong workspace; **không gọi native 32**.
- **Phán quyết cập nhật**: `REFERENCE_F32=PASS_REAL_8X2048` · `STATIC_SOURCE_QA=PASS_37_OF_37` · `MSVC_BUILD=NOT_EXECUTED` · `COMPILED_CONSTANTS_QA=NOT_EXECUTED` · `NATIVE_2X2=0/32` · `OWNER_RUN=HOLD`.

_Nội dung phần dưới được giữ nguyên như tài liệu thiết kế/bàn giao ban đầu tại thời điểm tạo. Các dòng trước đó nói `REFERENCE=NOT_EXECUTED` là trạng thái **trước phụ lục này**, không phải trạng thái hiện tại._

---

# TTM T5 — KV/Flash 2×2: chuẩn bị binary, logits tham chiếu và phán quyết owner

**Ngày:** 2026-11-10 · **Task:** `TTM_T5_F32_KV_FLASH_2X2_NEW_BINARY_REFERENCE_STATIC_QA_THEN_OWNER_RUN_DECISION`.

**Trạng thái:** `SOURCE_STATIC_QA=PASS_29/29` · `NEW_MSVC_BINARY=NOT_BUILT_ON_OWNER_WINDOWS` · `TRUE_P02_REFERENCE=NOT_EXECUTED` · `NATIVE_2X2=0/32` · `OWNER_RUN_GATE=HOLD`.

## 1. Nguồn đóng băng và phạm vi

- TTM repo `minhtri22/TokenToModel-Lab`, nhánh `research/ttm-t5-f32-strict-logit-parity-diagnostic-20261109` từ main `b57b44e7287f842e81050c1faee337f636333dd0`. Không đổi main.
- 8 synthetic fixtures `SYN01..SYN08`, lengths 1,2,4,6,9,12,20,31 (đã khóa JSON), mỗi fixture chạy S0 F16+Flash ON, S1 F32+Flash OFF, S2 F32+Flash ON, S3 F16+Flash OFF; 32 native decodes **chưa cấp phép chạy**.
- C++/CMake dùng đúng **pinned llama.cpp** `372dc5ca157276beb6c67b2e92477e8d662e964a`, GGUF F32 SHA256 `5bdc904e6c51af04a4223219f36e6bc2e687f60fd6e17dc24508f3eb7489e4e5`, PyTorch original checkpoint 1024 SHA256 `cb985751795c8328ad65acf7ca4c1033ce35182c1bfbdb8c38550de629cb271b`, P02 Git blob `9762343e06cf800b50574c2871ae1ed58537fb18`.
- Threshold strict `max_abs=0.001` bất biến; T5 8 fixture gốc `FAIL_7/8` không đổi, TEST và Q1/Q2 không truy cập, không train.

## 2. Các lỗi kỹ thuật đã sửa/khóa trong bước này

1. **CMake import root chính xác**: GitHub CMake cũ trỏ theo giả định `llama.cpp/build` trong khi MSVC `ttm_t5_layer_probe.vcxproj` lịch sử đã kiểm trực tiếp cho thấy `_tmp/ttm_t2/build/upstream_llama/src/Release/llama.lib`, `ggml/src/Release/ggml.lib`, `ggml/src/Release/ggml-base.lib`. CMake ứng viên đã chuyển sang `LLAMA_BUILD_ROOT` đúng thư mục trên, kiểm đủ ba import lib, cấm non-MSVC/x86.
2. C++ **`--self-check` không nạp model/không decode** in JSON 8 fixture IDs và 4 arms. Dùng chương trình `check_compiled_constants.py` đối chiếu JSON với prereg Git blob `3b12cc1883ab20e2d9e3a92e6907586c1b4cad36`. C++ JSON raw string đã kiểm logic cú pháp riêng, nhưng chưa biên dịch against pinned MSVC trên máy chủ.
3. **Python reference có scope root/worktree độc lập**: checkpoint và GGUF có thể nằm trong `_tmp` dự án, còn P02/prereg nằm trong worktree. Mã cũ buộc checkpoint phải nằm cùng worktree (không hợp lệ với thực tế). Bản mới yêu cầu exact checkpoint SHA, P02 source blob, prereg blob, config/step và state_dict, CPU FP32 `inference_mode`, ghi đúng **8×2.048 logits** mới.
4. Kiểm toán reference bằng chương trình **độc lập không load trọng số** `verify_f32_reference_rows.py`: đúng 8 dòng, exact 8 ID dãy, 2.048 số hữu hạn, metadata source/checkpoint SHA trên từng dòng; OwnerGate trước đây chỉ đếm 8 dòng, giờ kiểm schema đầy đủ.
5. **Một điều phối Python 3.12** thay cho wrapper PowerShell dễ treo: `stage_binary_and_f32_reference.py`, lệnh con dùng `subprocess.run(timeout=...)`, ghi stdout+stderr vào `_tmp`, kiểm returncode, không dùng PowerShell `2>&1` với Stop. Chỉ fast-forward worktree sạch; không reset/rebase/force, không sửa data/test/checkpoint.

## 3. Gói chạy một lần trên máy Windows — KHÔNG chạy 32 native

**Đã chuẩn bị nhưng CHƯA chạy trên Windows** vì RemoteDesktop từ chối đường thực thi `run_command` (cần managed task admission; đăng ký project mới cũng bị từ chối do project kind). Do đó chưa có output binary hoặc reference, không được tự nhận PASS.

Người chủ dự án sử dụng **một** đoạn PowerShell 5.1 để tải script mới vào `_tmp` và kiểm Git blob exact. Dùng branch SHA 40 ký tự cuối được trả trong kết quả bàn giao (vì mỗi lần ghi tài liệu làm HEAD thay đổi), không dùng literal SHA lịch sử. Khuyến nghị dùng đúng Python3.12 `C:\Users\minht\AppData\Local\Programs\Python\Python312\python.exe`, xác minh `import torch` trước. Nếu cần checkpoint tham chiếu thật, cung cấp `--checkpoint` trỏ vào tệp **`.pt` chính xác SHA** bên trong project. Nếu thiếu, script **vẫn biên dịch+QA** binary nhưng để `REFERENCE=HOLD_CHECKPOINT_FILE_NOT_PROVIDED`; tuyệt đối không thay bằng GGUF hay checkpoint khác.

```powershell
$ErrorActionPreference = 'Stop'
$root = 'D:\WORK\RESEARCH\TokenToModel-Lab'
$pin = '<FINAL_GITHUB_HEAD_40_HEX>'
$py = 'C:\Users\minht\AppData\Local\Programs\Python\Python312\python.exe'
$script = Join-Path $root '_tmp\ttm_t5_stage_binary_reference_20261110.py'
$url = "https://raw.githubusercontent.com/minhtri22/TokenToModel-Lab/$pin/tools/pilot_t5/kv_flash_precision_v1/stage_binary_and_f32_reference.py"
Invoke-WebRequest -UseBasicParsing -Uri $url -OutFile $script
$gitExe = (Get-Command git.exe -CommandType Application).Source
$blob = (& $gitExe -C $root hash-object $script).Trim()
if ($LASTEXITCODE -ne 0 -or $blob -ne 'e8ef03caa966a910e322cdeaeb8a0d08835a9a8f') { throw 'STAGE_SCRIPT_SOURCE_PIN_MISMATCH' }
& $py -m py_compile $script
if ($LASTEXITCODE -ne 0) { throw 'PY312_SOURCE_PARSE_FAIL' }
# Nếu đã có .pt bước 1024 đúng SHA trong project, thêm:
#   --checkpoint 'D:\WORK\RESEARCH\TokenToModel-Lab\_tmp\...\step_1024.pt'
& $py $script --project-root $root --expected-head $pin
if ($LASTEXITCODE -ne 0) { throw 'STAGE_FAILED_CLOSED_READ_RECEIPT' }
```

Kết quả lưu trong `_tmp/ttm_t5_kvflash_binary_reference_stage_v1_20261110/STAGE_RECEIPT.json`, log các bước trong cùng thư mục. **Tuyệt đối không xóa/ghi đè** stage nếu bị gián đoạn — báo lại receipt và log cụ thể, không tự retry.

### Cổng kết luận đã khóa

| Kiểm định | Kết quả hiện tại |
|---|---|
| 8 IDs mới và 4 arms khớp prereg / C++ / Python | `PASS_STATIC_29/29` |
| Python synthetic 13 tests (mã có sẵn) | `NOT_EXECUTED_ON_OWNER` |
| MSVC C++ candidate compiled + SHA | `NOT_EXECUTED` |
| Compiled no-model `--self-check` vs prereg | `NOT_EXECUTED` |
| PyTorch P02 F32 checkpoint1024 reference 8×2048 | `NOT_EXECUTED` |
| Independent readback reference 8×2048 | `NOT_EXECUTED` |
| 32 native decodes S0–S3 | `NOT_AUTHORIZED/NOT_EXECUTED` |

Nếu tất cả binary+reference đạt, chỉ chuyển sang **`STAGED_QA_COMPLETE_NATIVE_HOLD`**, chưa phát giấy phép native. Cần owner decision **một lần** cho 32 native decodes và runner có SHA bị khóa. Nếu thiếu checkpoint, binary compile lỗi, Python/torch lỗi hoặc source SHA sai, giữ HOLD. Không mở lại Preview/Supplement và không sửa ngưỡng strict.

**Bước thực hiện tiếp theo:** sau gói stage, đọc `STAGE_RECEIPT.json` từ máy Windows, commit public SHA+QA metadata lên GitHub, rồi phân xử `READY/HOLD/FAIL` cho 32 native (chưa thực thi).
