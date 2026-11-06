# TTM P01 L1 — V3/V4 independent Windows static QA and compile-only preflight

Date: 2026-11-07. This is **engineering QA only**, not a scientific result.

## Immutable context

- Repo: `https://github.com/minhtri22/TokenToModel-Lab`.
- Audit branch: `audit/p01-l1-native-security-critical-fix-20261106`.
- Original frozen worktree: `D:\WORK\RESEARCH\TokenToModel-Lab\worktrees\p01-f0-static-i0a-20261105`, HEAD `f2e333df2f9ca24a8e483507c3cfc386ad9c76f0`.
- Broker V2 was forcibly recovered once, SCM `Stopped / PID 0` **at receipt time**, GitHub `a5a0006f6586a78b6a748fea018625c65e569c8f`; current machine state must be read back by the new preflight, not presumed.
- V3/V4 canonical source commit `782f101f001973f8c23f23b22ae2b0896232d722`:
  - Broker V3 `runtime/p01/windows/BrokerAttestationServiceV3.cs`, Git blob `2fc1b63d6e21e7d8ac86184251974e9960572f3f`.
  - Worker V4 `qa/p01/windows/TTMWorkerNativeProbeV4.cs`, Git blob `63d5407ccb3f9e15f8dda59ee6323a0e5009d860`.
  - Independent Python `qa/p01/windows/Independent-QA-BrokerV3-WorkerV4-Static.py`, Git blob `0d42c4f7a4ac08c59022449210a323feed3a7495`.

## Delivery / source evidence

**Use ONLY** `qa/p01/windows/Invoke-TTM-P01-L1-V3V4-IndependentWindowsStaticPreflight-V2-PS51.ps1`, Git blob `ca8a0bd45a778379f2387eff0aa14c068c2713b3`, originating from commit `40f6146cc6fc206b9d80c76f3992ab05233d07c7`.

The predecessor without `-V2-` is **quarantined and must not be invoked**; a broken intermediate rewrite had a duplicated script tail (487 lines). The V2 successor is 253 lines, with one terminal `exit`, one Python-checker call, one GitHub receipt upload, and no `Add-Type` compiler invocation. Source review found 30/30 textual preflight conditions present, **not a Windows PowerShell parse result**.

The first direct remote Python read-only attempt was rejected by the remote gateway (`managed mode requires task_job_submit`). The disabled Research Adapter was not used. **No target-Windows Python execution, C# compilation or native security execution has occurred.**

## Exact Windows one-shot QA gate

On the target Windows 11 machine, use elevated Windows PowerShell 5.1. Obtain the V2 successor from the exact GitHub commit and verify its Git blob through `gh api` before saving the launcher in `D:\WORK\RESEARCH\TokenToModel-Lab\worktrees\_ttm_p01_l1_tools`. Refuse an existing mismatching file, reparse points and PowerShell parsing errors.

The script itself must:
1. Confirm frozen original HEAD/branch/origin, `TTMP01Broker` still Manual / LocalService / V2 exact binPath and currently `Stopped, PID=0`.
2. Check all four previously qualified markers by exact SHA-256; do not rewrite/delete them.
3. Qualify Miniforge Windows x64 Python and GitHub CLI auth. Prove the new fixed static-QA marker absent with native Win32 `GetFileAttributesW` through Python `ctypes`; the resulting helper creates no C# compiler scratch files.
4. Save only three exact pinned GitHub source bytes to a new unique **TTM project-local** evidence directory, verify their Git blob and compute on-disk SHA256.
5. Create `L1_V3_V4_INDEPENDENT_STATIC_QA_ATTEMPT_20261107.lock` using atomic `FileMode.CreateNew` and execute the pinned Python checker **once** with `-B` and explicit exact broker/worker input paths.
6. Require JSON verdict `PASS_SOURCE_ONLY_NO_WINDOWS_NATIVE`, no failed positive or negative fixtures, cross-check both checker input hashes against local source hashes. Failure is BLOCK/FAIL, never automatic rerun.
7. Inspect only (do not invoke) `%WINDIR%\Microsoft.NET\Framework64\v4.0.30319\csc.exe` version/hash; inspect D: free space and RAM, and verify the future target filenames `TTMP01Broker.attestationV3.exe` and `TTMWorkerNativeProbeV4.dll` are not already present.
8. Save a new JSON receipt under `worktrees\_ttm_p01_l1_qa_receipts\<run_id>`, GitHub commit to `artifacts/qa/p01/<run_id>.json` on audit branch, verify SHA256 readback. The recipe retains evidence and anti-replay marker, does not clean them automatically.

**PASS requirements:** `TTM_V3V4_INDEPENDENT_PYTHON_QA=PASS_SOURCE_ONLY`, `TTM_V3V4_COMPILER_PREFLIGHT=PASS_READONLY`, `TTM_V3V4_GITHUB_READBACK=PASS`, script exit 0. If blocked, preserve exact PASS/FAIL evidence and do not run the same attempt again.

## After qualified PASS only

**Next separate action** `TTM_P01_L1_V3_V4_COMPILE_ONLY_EXACT_SOURCE_ONE_SHOT_GATE` — create and independently preflight a narrowly scoped native Windows compilation runner *after* reviewing the target Windows QA receipt. It must pin all three source blobs, the qualified QA receipt commit/hash, original frozen HEAD, exact csc identity, and output-file absence. Compile Broker V3 to `TTMP01Broker.attestationV3.exe` and Worker V4 to `TTMWorkerNativeProbeV4.dll` using Windows Framework64 `csc.exe` exactly once. Verify output SHA256, preserve evidence/marker, commit/read back GitHub receipt. No installation, no SCM `binPath` change, no service start/stop and no native security trial in this compile-only gate.

No compile runner is authorized or executed by this step.

## Status

`SOURCE_STATIC_PREVIOUS_REVIEW=48/48`, `NEGATIVE_SOURCE_FIXTURES_PREVIOUS_REVIEW=12/12`.
`WINDOWS_TARGET_PYTHON_QA=PENDING`.
`COMPILER_READONLY_PREFLIGHT=PENDING_WINDOWS`.
`CSC_COMPILATION=NOT_EXECUTED`.
`SCM_ACTION=NONE`.
`NORMAL_STOP=NOT_REQUALIFIED`.
`NATIVE_SECURITY=NOT_QUALIFIED`.
`P01=OPEN`, `P02=NOT_OPENED`.
`W01_W12=NOT_EXECUTED`, `L1_GROUPED_QA=NOT_AUTHORIZED`.

Preserve P00, ten F0 results, all prior evidence and markers, P00–P12 sequence, frozen original worktree and scientific `lineage.md` append-only rules.
