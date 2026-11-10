# R3 CPU source of truth — Public 384-input state-graph toy

**2026-11-11** · `SOURCE_SEPARATED_CHECKER=PASS_SCOPED` · `CPU_TEST=PASS_70/70` · `NEGATIVE_REJECTIONS=PASS_42/42` · `NEURAL_TEST=NOT_EXECUTED` · `CODEX_R3_REVIEW=PENDING`.

**Không cần tải ZIP**. Mọi mã, dữ liệu đầy đủ, log và biên bản được lưu trực tiếp như GitHub files. 

- [Bản tổng hợp khoa học và giới hạn kết luận](../../../../docs/research/TTM_R3_STRICT_INPUT_GRAPH_TOY_INTEGRATED_CPU_QA_AND_OWNER_ADJUDICATION_20261111.md).
- [Bộ sinh R3](../../../../tools/research/semantic_state_r3/r3_generator.py).
- [Checker nghiêm ngặt độc lập về mã](../../../../tools/research/semantic_state_r3/r3_independent_checker.py).
- [Kiểm thử CPU tích hợp (70 ca)](../../../../tools/research/semantic_state_r3/r3_single_cpu_qa.py).
- [Oracle JSON đầy đủ, nhãn công khai](R3_PUBLIC_ORACLE.json) (296.768 byte; SHA256 `bd9fb15d3f3850823e083269a61df90eaddaea3e61b8b73e9f40b4ec74c7ce47`).
- [384 model inputs chỉ có story+question](R3_MODEL_INPUT_ONLY.json) (103.879 byte; SHA256 `4fa0ad45acdfecb2143a984127e6ad0c50126c203996148d60843eb1214cd50a`).
- [Biên bản parser, tính counterfactual, baselines](R3_CHECKER_REPORT.json).
- [Log cuối 70/70](R3_CPU_TEST_LOG_FINAL.txt).
- [Manifest SHA256 và Git blob của 7 nguồn](R3_SOURCE_QA_MANIFEST.json).
- [Biên nhận QA / phân xử GO-HOLD](R3_OWNER_SCOPED_CPU_QA_AND_DECISION_20261111.json).
- [Handoff Codex kiểm thử đối kháng (chưa thực hiện)](../../../../docs/research/TTM_R3_CODEX_ADVERSARIAL_SOURCE_AND_MOTIF_QA_HANDOFF_20261111.md).

## Chạy lại trên Windows 11 / PowerShell 5.1, chỉ ghi trong project root

Dùng đúng checkout/worktree của nhánh và không ghi đè receipt hoặc dữ liệu đã có:

```powershell
$ErrorActionPreference = 'Stop'
$root = 'D:\WORK\RESEARCH\TokenToModel-Lab'
$py = 'C:\Users\minht\AppData\Local\Programs\Python\Python312\python.exe'
$source = Join-Path $root 'tools\research\semantic_state_r3'
$out = Join-Path $root '_tmp\ttm_r3_replay_once'
if (Test-Path -LiteralPath $out) { throw 'R3_REFUSE_EXISTING_REPLAY_DIRECTORY' }
New-Item -ItemType Directory -Path $out | Out-Null

& $py (Join-Path $source 'r3_generator.py') --oracle (Join-Path $out 'oracle.json') --model-input (Join-Path $out 'model.json')
if ($LASTEXITCODE -ne 0) { throw 'R3_GENERATOR_FAILED' }

& $py (Join-Path $source 'r3_independent_checker.py') --oracle (Join-Path $out 'oracle.json') --model-input (Join-Path $out 'model.json') --output (Join-Path $out 'checker.json')
if ($LASTEXITCODE -ne 0) { throw 'R3_CHECKER_FAILED' }

& $py (Join-Path $source 'r3_single_cpu_qa.py')
if ($LASTEXITCODE -ne 0) { throw 'R3_CPU_TESTS_FAILED' }

Get-FileHash -Algorithm SHA256 -LiteralPath (Join-Path $out 'oracle.json')
Get-FileHash -Algorithm SHA256 -LiteralPath (Join-Path $out 'model.json')
```

**Giới hạn:** Chỉ dùng toy grammar công khai, không phải phân phối truyện tự nhiên hay TEST mù. `graph_motif_cross_split=0` là kết quả kiểm tra trên signature định nghĩa cho toy, không chứng minh OOD tổng quát. Parser đạt 384/384 vì các luật cập nhật được công bố; không là bằng chứng O1 giúp kiến trúc neural. R2A validator FAIL trước đó vẫn lưu nguyên trạng.

**Quyết định:** `R3_PUBLIC_TOY_DEV_DIAGNOSTIC=READY_SCOPED` · `O0=HOLD_PRESERVE` · `O1=DEFER` · `GPU=NO` · `TEST_Q1Q2=UNTOUCHED`.
