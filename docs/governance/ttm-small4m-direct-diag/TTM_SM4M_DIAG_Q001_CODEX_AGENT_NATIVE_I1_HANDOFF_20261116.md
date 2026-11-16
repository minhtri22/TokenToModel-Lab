# HANDOFF CHO CODEX AGENT — TTM-SM4M-DIAG-Q001 · Native I1 integrated remediation & adjudication

**Ngày bàn giao:** 16/11/2026  
**Operation:** `TTM_SM4M_DIAG_Q001_CODEX_NATIVE_I1_NEGATIVE_QA_RIGHTS_CUSTODY_AND_SINGLE_ADJUDICATION_ONEPACK`  
**Repo / source of truth:** [`minhtri22/TokenToModel-Lab`](https://github.com/minhtri22/TokenToModel-Lab)  
**PR ứng viên:** [#28](https://github.com/minhtri22/TokenToModel-Lab/pull/28), `DRAFT · UNMERGED`  
**Review issue:** [#29](https://github.com/minhtri22/TokenToModel-Lab/issues/29)  
**Exact source/evidence HEAD trước handoff:** `4f5e6533854818845d3ccdfad661ccc25f0e2812` (Code Agent phải đối chiếu Git blob các tệp đang được kiểm tra; commit handoff mới có thể làm HEAD tiến thêm mà không thay byte runner)  
**Q1 main đã đăng ký:** `TTM-SM4M-DIAG-Q001`; frozen baseline `f7a0a5874e8fd895c8ea8d17ceff393a4d4917a3`.  
**Owner decision ĐÃ CẤP:** `GO_SMALL4M_DIAG_SINGLE_SCOPED_IMPLEMENT_AND_RUN_CONDITIONAL`. **Không hỏi lại GO; không suy diễn quyền chạy tức thì.**  
**Current formal disposition:** `HOLD_I1 · I2_NOT_EXECUTED · RIGHTS_NOT_VERIFIED · NO_TEST_FINAL_REPLAY · PR28_UNMERGED · LINEAGE_UNCHANGED`.

## 0. Lý do chuyển giao / không thực thi qua RemoteMCP Canonical

Đã đọc skill của plugin `remote-mcp-v2-web-clean`, xác nhận tool surface có `device_maintenance_recipe_catalog`, `device_maintenance_recipe_run`, `task_job_submit_with_evidence`, và không có `task_job_submit_once` đã retired. Read-only `device_list → device_status → task_status → task_job_submit_failure_status` xác nhận:
- `machine-1`/`DESKTOP-4PSD0G2` ONLINE, heartbeat fresh; approved execution root `D:\WORK\RESEARCH`.
- Managed **GIT** project `prj_1544c3e94ebd4b2947bc84e9`; task `tsk_2d1d91bd29582300c60fc10d` đã fetch và checkout **source-only** đúng commit `d42c44040da89ab6c5d275a9389ba920ef18db68` trong task worktree.
- Native PowerShell source-only QA attempted with operation `TTM_SM4M_DIAG_Q001_MANAGED_PS51_SOURCE_ONLY_NATIVE_ONEPACK_20261116`, proxy job `rjob_bd75ffaedd5706d82f436097a0201b0e`, **FAILED_FINAL** at `POST_PROXY_PRE_NODE`, `COMMAND_NOT_ALLOWED`: **`executable 'powershell' is not in durable allowlist`**; `node_job_id=null`, terminal evidence `scientific_execution_started=false`. **Chưa chạy PowerShell, native negative QA, checkpoint hoặc mô hình**.
- Không resubmit terminal job, không dùng `run_command` legacy, alias executable, Python subprocess hoặc pairing/restart để lách allowlist. Plugin không bị báo absent; **vấn đề là chính sách dispatch**, không phải lỗi mất kết nối Windows.

**Chuyển việc sang Codex chạy TRỰC TIẾP trên Windows 11 do owner giao**, độc lập với đường managed RemoteMCP đã bị từ chối. Codex được phép kiểm thử *chỉ nguồn/mock/native watchdog* theo handoff; không được tự vô hiệu hóa lớp bảo vệ RemoteMCP. Nếu Codex không có quyền chạy lệnh trên máy đó thì vẫn phải dừng, ghi `HOLD_NATIVE_TRANSPORT`. Đừng hỏi owner cài lại ZIP: GitHub đã chứa source và QA.

## 1. Nguồn bắt buộc — đọc trước khi sửa/chạy

Đối chiếu các tài liệu và commit sau, tuyệt đối không dựa vào chat tóm tắt:
1. [Frozen Q1 protocol](https://github.com/minhtri22/TokenToModel-Lab/blob/f7a0a5874e8fd895c8ea8d17ceff393a4d4917/artifacts/governance/ttm-small4m-direct-diag/TTM_SM4M_DIAG_Q001_FROZEN_ONEPACK_PREEXEC_CONTRACT_20261116.json): **TRAIN 24 + probe 56, seed 20261116, CPU FP32, tối đa 256 optimizer steps, 900 giây wall, RAM 12 GiB, total output 1 GiB**. Không chỉnh ngưỡng/QuestionID/checkpoint/seed.
2. [V3 independent HOLD](https://github.com/minhtri22/TokenToModel-Lab/blob/b02ee93946bcca16f03f51ad5364ad554dcc61f9/docs/governance/ttm-small4m-direct-diag/TTM_SM4M_DIAG_Q001_V3_30ABFD8_I1_DISTINCT_SOURCE_AND_NATIVE_TRANSPORT_HOLD_20261116.md) — phát hiện launcher N05/N06/N07, sampler RSS N08, F06 hard veto.
3. [V4 source manifest — 14 files](https://github.com/minhtri22/TokenToModel-Lab/blob/4f5e6533854818845d3ccdfad661ccc25f0e2812/artifacts/governance/ttm-small4m-direct-diag/TTM_SM4M_DIAG_Q001_V4_LAUNCHER_MANAGED_NATIVE_SOURCE_MANIFEST_20261116.json), source SHA-256/Git blob và UTF-8 bytes.
4. [V4 HOLD receipt](https://github.com/minhtri22/TokenToModel-Lab/blob/4f5e6533854818845d3ccdfad661ccc25f0e2812/artifacts/governance/ttm-small4m-direct-diag/TTM_SM4M_DIAG_Q001_V4_LAUNCHER_MANAGED_NATIVE_I1_HOLD_RECEIPT_20261116.json).
5. [V4 remediation handoff](https://github.com/minhtri22/TokenToModel-Lab/blob/4f5e6533854818845d3ccdfad661ccc25f0e2812/docs/governance/ttm-small4m-direct-diag/TTM_SM4M_DIAG_Q001_V4_LAUNCHER_MANAGED_NATIVE_HOLD_I1_HANDOFF_20261116.md).
6. Code thuộc `tools/pilot_t4/direct_failure_diag_q001/preexec_candidate_20261116/`: `ttm_sm4m_diag_q001.py`, `release_auth_v2.py`, `Run-Approved-OneShot-PS51.ps1`, `Watch-TTM-SM4M-ProcessTree-PS51.ps1`, `Invoke-DIAG-Q001-Watchdog-NativeNegativeQA-PS51.ps1`, `Invoke-DIAG-Q001-I1-NativeSourceOnePack-PS51.ps1`, `independent_negative_qa_v3.py`.

**Git policy:** Use `D:\WORK\RESEARCH\TokenToModel-Lab` and Codex-owned scoped worktree **within** this project; never modify a dirty existing scientific worktree, `main`, `src/p02/transformer_core.py`, `lineage.md` or historical TEST/FINAL24. No writes outside project root except standard Windows program executables (Python 3.12 binary is under LocalAppData, but all research/evidence outputs must stay on D:). Do not merge PR #28 during this task.

## 2. Mục tiêu đúng một lượt Codex: Build → native test → evidence → I1 adjudication

**A. Exact-source preflight:** Checkout/pin candidate under GitHub branch `review/ttm-sm4m-diag-q001-preexec-source-candidate-20261116`; retrieve full 40-hex commit. Verify SHA-256 and Git blob for all files against V4 manifest; if PR HEAD has moved, explicitly compare modified path list. Verify no `main` drift affecting Question Gate. Record Windows PowerShell 5.1, Python 3.12 **by exact executable** `C:\Users\minht\AppData\Local\Programs\Python\Python312\python.exe`, architecture, repo/worktree/status, and SHA-256 of every command source. Never quietly run Miniforge Python 3.13.

**B. Source + native negative QA (NO MODEL):** independently check PowerShell AST parser errors for launcher/watchdog/QA scripts; ensure `ExpectedRunnerSHA256` and `ExpectedWatchdogSHA256` are *actually* validated, module hash and dot-source happen before `Start-Process`, and no unpinned module injection. Run `source-qa`, `independent_negative_qa_v3.py` as **author-provided** code; create a **separate** adversarial review/negative QA if Codex also edits source (one assistant testing its own code does not create independent reviewer certification). Run actual PowerShell 5.1 no-model five-case watchdog suite, collect stdout, stderr, return code and child process termination evidence. Its scenarios: normal success; oversized watched stdout at exit; timeout; child process aggregate RSS; child surviving parent. Any script bug discovered by native testing must be fixed within the same scoped code branch and retested **only as engineering QA**, with original failures preserved. Do not claim `5/5 PASS` until actual native receipt exists.

**C. Security/behavior adversarial checks:** signed root and hostname binding; nonce replay across multiple worktrees/root aliases; Win32 symlinks/junctions; denial for unsigned/forged/expired permit; ensure no fallback when trust store empty; no private model access before authorization; boundary 900s/12GiB/1GiB. A sampled aggregate RSS watchdog alone **does not provide an OS-enforced instantaneous RAM cap**. If the frozen contract requires a hard ceiling, implement or integrate a scoped Windows Job Object hard memory bound and independently test it, else mark `HOLD_I1_RESOURCE_GUARD`—do not silently relax 12GiB. NO automatic science retries.

**D. Rights and custody — HARD VETO:** `release_auth_v2.py` presently sets `TRUSTED_ED25519_PUBLIC_KEYS={}`; **do not insert invented keys, generate pretend independent human signatures, or set `VERIFIED_SCOPED` to force GO**. Obtain actual proof from authorized owner, independent reviewer and rights custodian for AD-00/AD-01C/E6 derived TinyStories T4 checkpoint, tokenizer source inventory and scope; secure attestation stays private as needed, public Github gets only non-secret SHA/receipt and reviewer references. Expected private checkpoint SHA-256:
`cb985751795c8328ad65acf7ca4c1033ce35182c1bfbdb8c38550de629cb271b`, length `45,074,891` bytes, step 1024, P02 source Git blob `9762343e06cf800b50574c2871ae1ed58537fb18`, 3,749,376 parameters. Do not access checkpoint bytes unless rights/access gate is actually satisfied; file name alone is not custody. Do not use a different checkpoint/tokenizer.
  
**E. Exact one verdict:** If source/native QA is PASS but F06 lacks valid attestations, report **`HOLD_I1`** while crediting source/native QA only. If Windows native still fails, `HOLD_I1_NATIVE_QA`; if all—including independent QA, hard resource enforcement, owner+reviewer+rights signatures, checkpoint/tokenizer and frozen 80-case custody—truly PASS, prepare I1 release decision with independent reviewer evidence. Only on legitimate `I1_PASS` may the **already granted conditional owner GO** release *one* I2 CPU run. Do not execute I2 in this handoff simply to see if it works; do not turn mock QA into research result.

## 3. Câu lệnh native gợi ý — chỉ sau khi xác minh exact source và tập tin

Trong PowerShell 5.1 trên Windows, tại **worktree Codex riêng** ở D:, không phải máy của ChatGPT:

```powershell
$ErrorActionPreference='Stop'
$ProjectRoot='D:\WORK\RESEARCH\TokenToModel-Lab'
$Python312='C:\Users\minht\AppData\Local\Programs\Python\Python312\python.exe'
$Dir=Join-Path $ProjectRoot 'tools\pilot_t4\direct_failure_diag_q001\preexec_candidate_20261116'
# Nếu dùng worktree riêng, $Dir phải trỏ tới thư mục nguồn trong worktree đó,
# nhưng vẫn nằm bên trong $ProjectRoot. Xác minh git rev-parse HEAD trước mọi lệnh.
& $Python312 -c 'import sys; assert sys.version_info[:2]==(3,12)'
$Runner=Join-Path $Dir 'ttm_sm4m_diag_q001.py'
$Launcher=Join-Path $Dir 'Run-Approved-OneShot-PS51.ps1'
$Watchdog=Join-Path $Dir 'Watch-TTM-SM4M-ProcessTree-PS51.ps1'
$Negative=Join-Path $Dir 'independent_negative_qa_v3.py'
$NativeWatch=Join-Path $Dir 'Invoke-DIAG-Q001-Watchdog-NativeNegativeQA-PS51.ps1'
$Onepack=Join-Path $Dir 'Invoke-DIAG-Q001-I1-NativeSourceOnePack-PS51.ps1'
# Không gọi launcher I2. Sau khi xác minh SHA-256 theo manifest:
& powershell.exe -NoProfile -NonInteractive -ExecutionPolicy Bypass -File $Onepack `
  -ProjectRoot $ProjectRoot `
  -ExpectedRunnerSHA256 (Get-FileHash $Runner -Algorithm SHA256).Hash.ToLowerInvariant() `
  -ExpectedLauncherSHA256 (Get-FileHash $Launcher -Algorithm SHA256).Hash.ToLowerInvariant() `
  -ExpectedWatchdogSHA256 (Get-FileHash $Watchdog -Algorithm SHA256).Hash.ToLowerInvariant() `
  -ExpectedNegativeQaSHA256 (Get-FileHash $Negative -Algorithm SHA256).Hash.ToLowerInvariant() `
  -ExpectedNativeWatchQaSHA256 (Get-FileHash $NativeWatch -Algorithm SHA256).Hash.ToLowerInvariant()
if ($LASTEXITCODE -ne 0) {throw 'HOLD_NATIVE_SOURCE_QA_FAILED'}
```

**Quan trọng:** Script `Onepack` tự băm những nguồn cung cấp trong cùng checkout, nhưng việc truyền SHA bằng `Get-FileHash` ngay tại lúc chạy **không thay thế pin đối chiếu với GitHub V4 manifest trước đó**. Codex phải so sánh với manifest và exact source commit. Nếu onepack có bug, sửa và ghi lỗi/receipt như bằng chứng, đừng ấn định PASS.

## 4. Evidence giao nộp — GitHub bắt buộc

Codex phải đưa lên nhánh/review PR GitHub (không chỉ ZIP ở Downloads):
- Báo cáo Markdown `TTM_SM4M_DIAG_Q001_CODEX_NATIVE_I1_INTEGRATED_REVIEW_<DATE>.md`.
- Biên nhận JSON `TTM_SM4M_DIAG_Q001_CODEX_NATIVE_I1_RECEIPT_<DATE>.json`.
- Native Windows stdout/stderr, exit codes, PS parser result, Python 3.12 executable/version, mỗi case PASS/FAIL, child PID cleanup, RSS/tree/output observed values, file hashes, and exact Git commit; mọi log/fixture giả không chứa private checkpoint.
- Findings ledger: F01–F10 and N05–N08 **what is actually closed vs still HOLD**, plus rights AD-00/AD-01C/E6 status and reviewer signoff provenance.
- GitHub push commit SHA, independent readback of receipt SHA-256/Git blob, linked Issue #29 / PR #28; preserve historical evidence append-only.
- If source code changes, provide exact diff; keep PR #28 Draft and no merge until real I1 adjudication.

Evidence summary must state truthfully `SOURCE_QA`, `WINDOWS_NATIVE_QA`, `EXTERNAL_RIGHTS_CUSTODY`, `I1_VERDICT`, `I2_NOT_EXECUTED`. Author/local Codex QA cannot pretend to be independent organizational signer.

## 5. STOP rules

**STOP/HOLD immediately** on mismatched commit/hash, missing protected signer keys, no AD-00/AD-01C/E6 or tokenizer/right approval, missing actual checkpoint custody, foreign path/reparse escape, missing Python 3.12/PS5.1, native process failure, failed hard RAM guard, nonfinite result, or unknown job state. Do not re-pair RemoteMCP, edit its allowlist manually or restart `machine-1` to fix the earlier terminal rejection. No fresh QID, no micro-permit, no TEST/FINAL24, no I2 on HOLD, no merge, no `lineage.md` modifications.

**Bước thực hiện tiếp theo — duy nhất (Codex):** `TTM_SM4M_DIAG_Q001_CODEX_NATIVE_I1_NEGATIVE_QA_RIGHTS_CUSTODY_AND_SINGLE_ADJUDICATION_ONEPACK` — verify source → execute native source-only QA on Windows → independent rights/custody check → return one scoped I1 PASS or HOLD with GitHub evidence. The owner's conditional GO is already on record and does **not** need to be requested again.
