# R2A — Source of Truth / tái lập chứng cứ

**Ngày:** 2026-11-10 · Phạm vi **chỉ dữ liệu toy, không TRAIN/GPU/inference neural**. Bản gốc R2 và kết quả Codex ban đầu được bảo toàn; R2A là amendment độc lập.

## Hồ sơ canonical

- [Báo cáo R2A sửa lối tắt vị trí](../../../../docs/research/TTM_R2A_POSITION_COUNTERBALANCED_KEY_BINDING_AMENDMENT_AND_CPU_QA_20261110.md)
- [Bản sao nội dung báo cáo Codex R2 gốc trên GitHub](../codex/TTM_R2_CODEX_ADVERSARIAL_REVIEW_20261110.md) — imported text, không khẳng định byte-identical với tệp Windows.
- [Bộ sinh R2A](../../../../tools/research/semantic_state_r2/r2a_generator.py)
- [Bộ kiểm văn bản độc lập](../../../../tools/research/semantic_state_r2/r2a_independent_checker.py)
- [Bộ kiểm thử 36 ca](../../../../tools/research/semantic_state_r2/r2a_single_cpu_qa.py)
- [Biên bản thuật toán và đối chứng](R2A_INDEPENDENT_QA_20261110.json)
- [Log QA CPU final](R2A_CPU_TEST_LOG_FINAL_20261110.txt)
- [Danh sách Git blob, SHA-256, cách tái lập và trạng thái HOLD](R2A_SOURCE_OF_TRUTH_MANIFEST_20261110.json)

**Dữ liệu:** Oracle JSON 183.830 bytes SHA256 `3243d1eaae4b8727449fe4571dc81c898414b5ba300a20e7ead0819d7953286e`; model-input-only JSON 60.734 bytes SHA256 `72f57d704a2e4f99f06a797b8b647d93736a7093852e0c9df0f28dc59549032d`. Hai tệp là **derived artifacts tái dựng từ mã GitHub đã ghim**, chưa commit trực tiếp bản JSON lớn; không dùng bản ZIP ngoài GitHub làm chuẩn thay cho code/digest.

## Chạy lại bằng PowerShell 5.1 / Python 3.12

Đảm bảo checkout hoặc worktree chứa nhánh `research/ttm-small4m-semantic-state-goal-toy-r2-20261110`, tạo worktree **chỉ bên trong** `D:\WORK\RESEARCH\TokenToModel-Lab` nếu cần. Sau đó chạy:

```powershell
$ErrorActionPreference = 'Stop'
$root = 'D:\WORK\RESEARCH\TokenToModel-Lab'
$py = 'C:\Users\minht\AppData\Local\Programs\Python\Python312\python.exe'
$src = Join-Path $root 'tools\research\semantic_state_r2'
$out = Join-Path $root '_tmp\r2a_new_replay'
if (Test-Path $out) { throw 'REFUSE_EXISTING_REPLAY_DIRECTORY' }
New-Item -ItemType Directory -Path $out -Force | Out-Null
& $py (Join-Path $src 'r2a_generator.py') --oracle (Join-Path $out 'R2A_ORACLE_DATASET.json') --model-input (Join-Path $out 'R2A_MODEL_INPUT_ONLY.json')
if ($LASTEXITCODE -ne 0) { throw 'GENERATOR_FAILED' }
& $py (Join-Path $src 'r2a_independent_checker.py') --oracle (Join-Path $out 'R2A_ORACLE_DATASET.json') --model-input (Join-Path $out 'R2A_MODEL_INPUT_ONLY.json') --output (Join-Path $out 'R2A_INDEPENDENT_QA.json')
if ($LASTEXITCODE -ne 0) { throw 'CHECKER_FAILED' }
& $py (Join-Path $src 'r2a_single_cpu_qa.py')
if ($LASTEXITCODE -ne 0) { throw 'UNITTEST_FAILED' }
Get-FileHash -Algorithm SHA256 (Join-Path $out 'R2A_ORACLE_DATASET.json')
Get-FileHash -Algorithm SHA256 (Join-Path $out 'R2A_MODEL_INPUT_ONLY.json')
```

**Giới hạn:** lệnh trên giả sử `$root` đang checkout đúng nhánh; không tự tạo checkout hay xóa/tác động đường dẫn ngoài project. Dùng thư mục replay khác nếu đã tồn tại. Hai JSON chứa schema công khai, không phải TEST ẩn.

**Phán quyết:** `R2A_TOY=PASS_SCOPED` · `36/36_CPU_QA_PASS` · `KEY_BINDING_PROBES=128/128` · `O1=DEFER` · `O0=HOLD_PRESERVE` · `NEURAL_LEARNING=NOT_TESTED` · `GPU=NO` · `MAIN_PR13_LINEAGE=UNMODIFIED`.
