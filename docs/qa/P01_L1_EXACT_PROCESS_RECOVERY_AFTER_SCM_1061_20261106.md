# TTM P01 L1 — exact process recovery following SCM stop error 1061 (2026-11-06)

## Verified evidence / frozen original
- Original worktree: `D:\WORK\RESEARCH\TokenToModel-Lab\worktrees\p01-f0-static-i0a-20261105`.
- HEAD `f2e333df2f9ca24a8e483507c3cfc386ad9c76f0`.
- SCM stop failure receipt run `L1_BROKER_V2_SCM_STOP_RECOVERY_20261106T163818549Z_8b9033ff`, GitHub commit `8a3666c655edba86bef2a841a31246fe19e0e870`, SHA256 `b63b152494ac059177bac6ced501db5267d61e3ae865e17c058846942467d9ea`.
- Verified `sc.exe stop TTMP01Broker` exit **1061**; Windows SCM refused control with `The service cannot accept control messages at this time`. SCM remained RUNNING, PID 26200, 15 s after the one allowed SCM stop request. **No forced termination has occurred.**
- Exact previous process start milliseconds since Unix epoch: `1793982282113`, image path `D:\WORK\RESEARCH\TokenToModel-Lab\worktrees\_ttm_p01_l1_service_provision_20261106\broker_service\TTMP01Broker.attestationV2.exe`, SHA256 `a9dbc179b668559a0a5d6fe0bf979c9a6339d4977cb47f6a0c30d66fb289106a`.
- Existing durable markers (must be **preserved**, SHA verified independently):
  - SCM switch `L1_SCM_V2_SWITCH_ATTEMPT_20261106.lock`: `29f1a8836da83d34d233b165698dc20bb2fb6022941a93b840ae528b2ae4a8d1`;
  - V2/V3 native test `L1_BROKER_V2_WORKER_V3_NATIVE_SECURITY_ATTEMPT_20261106.lock`: `f0d895e68c30b8c3845336ea8aee40d2e1ca84f96816906a952ae70ad81587c7`;
  - SCM stop recovery `L1_BROKER_V2_SCM_STOP_RECOVERY_ATTEMPT_20261106.lock`: `f1ca3d0899fe6637a512e44dd073b449d4805ca8f8aafa1e8a3989599143502`.

## Separate one-shot recovery proposal

Source: `qa/p01/windows/Recover-TTM-P01-L1-ExactProcessAfter1061-PS51.ps1`.
Pinned Git blob `24de8b99bf3c11250af5002d57603ebf0365713b`. Static guard review 30/30 present; **not a Windows-native execution or authorization bypass**.

Default mode (no switches) is **read-only** against machine/service/process. It checks elevated PowerShell 5.1, original Git identity, precise executable and old-marker hashes, exact SCM configuration, PID, image, start time, and verifies current process by a Windows kernel HANDLE (native OpenProcess, GetProcessTimes, QueryFullProcessImageNameW, GetExitCodeProcess). It emits an independent TTM QA receipt with GitHub SHA-256 readback.

To recover a still-running stuck TTM process, the human operator may explicitly invoke **`-TerminateExactTTMProcess`**. This is a **forcible termination**, potentially discarding any transient in-memory state in that TTM service. It will:
1. Reconfirm all checks above, including the current SCM service still bound to that PID, exact image and created time. If already Stopped with PID0, do **nothing**.
2. Require an absent recovery marker (Win32 ERROR_FILE_NOT_FOUND=2), then atomically create `L1_BROKER_V2_EXACT_PROCESS_TERMINATE_ATTEMPT_20261106.lock` (never delete or reset).
3. Open an OS process HANDLE with termination permission; *inside the same native method* re-verify process creation time, image, and STILL_ACTIVE status, then issue exactly one `TerminateProcess(handle,1)` against **that same verified handle**. This avoids PID reuse between verification and termination.
4. Require kernel process-handle exit and SCM `Stopped / PID=0` readback; otherwise emit BLOCK with marker and evidence intact. It will not attempt a second terminate.
5. Upload receipt PASS/BLOCK/FAIL to the QA branch; SHA256 readback verification.

The script **never invokes** generic `Stop-Process -Id 26200`, `taskkill /F`, `sc.exe stop` again, restart, service config, service deletion or ACL mutation. It does not erase markers or alter F0, research `lineage.md`, accounts, credential, ledger or worktree. All writes except SCM-owned process termination are bounded to the project's receipts, new one-shot marker and GitHub audit evidence.

## After recovery

Even `PASS_EXACT_TTM_PROCESS_RECOVERED_WITH_FORCED_TERMINATION` means *infrastructure state recovered*, **not native security PASS**. The earlier Win32 231 DACL read failure, V3 denied-open/peer-auth NOT_EXECUTED and the V2 `OnStop/WaitForConnection` defect remain open. Do not restart the current V2 binary automatically or reuse native one-shot execution IDs/markers. Implement and independently verify a successor shutdown mechanism and pipe DACL readback without changing frozen original V1/V2 history, then separately authorize testing.

`P01=OPEN`; `P02=NOT_OPENED`; `W01_W12=NOT_EXECUTED`; `L1_GROUPED_QA=NOT_AUTHORIZED`.
Preserve P00, original HEAD, 10 F0 results, and P00–P12 phases.
