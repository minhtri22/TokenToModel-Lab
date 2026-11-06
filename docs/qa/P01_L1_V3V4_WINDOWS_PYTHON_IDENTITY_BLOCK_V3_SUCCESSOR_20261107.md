# TTM P01 L1 — Windows V3/V4 Python identity pre-QA block and V3 successor

Date: 2026-11-07. Engineering QA; no science execution.

## Evidence independently verified

Original Windows output and uploaded JSON `L1_V3_V4_WINDOWS_INDEPENDENT_STATIC_QA_20261106T174448947Z_21f4595b.json`, SHA-256 `031a3d04c04ce2435bad2b5803cd9e7232e82c5516beaa4a8698c74567bbe0c5`, committed at `ac246d1b4c8b4bea4ffda57196a77e4b9ab0d2b8`.

- `ADMIN=PASS`, frozen HEAD and SCM readback `Stopped/PID0` PASS, and all four historical markers PASS_EXACT.
- Python identity did not finish: `File "<string>", line 1`. The result `python_identity={}`, `python_checker_exit=null`, `source_files=[]`, `qa_marker_sha256=null` proves **the independent Python static QA did not run, sources were not fetched, and the one-shot QA marker was not created by this failed run**. No csc execution or SCM operation.
- Suspected cause is an argument-quoting interaction in Windows PowerShell 5.1: the original Python `-c` code contained embedded double quotes and the captured error was only the first stderr line. Microsoft documents quote-removal for legacy native argument passing. It is a grounded hypothesis, not full proof of root cause because complete traceback is absent.
- Windows PowerShell source V2 remains immutable as failure evidence. **Do not rerun V2** or delete any marker.

## Clean successor

Use **only** `qa/p01/windows/Invoke-TTM-P01-L1-V3V4-IndependentWindowsStaticPreflight-V3-PS51.ps1`, created in source commit `bd30ced5e6a99ed37f9ceda3dcc2b287e654298c`. Source was derived from the previously clean V2 file `ca8a0bd45a778379f2387eff0aa14c068c2713b3` and changed only:
- The Python `-c` identity probe uses `sep=chr(124)` and **no inner double quotes**. This is suitable for PowerShell 5.1 native argument transmission.
- Records Python identity probe output/exit code if the problem persists.
- New schema/run ID and distinct durable marker `L1_V3_V4_INDEPENDENT_STATIC_QA_V3_ATTEMPT_20261107.lock`.
- References failed predecessor commit `ac246d1b4c8b4bea4ffda57196a77e4b9ab0d2b8`.

Before invoking the new one-shot, a harmless identity check in elevated Windows PowerShell 5.1 is recommended:

```powershell
$py=Join-Path $env:USERPROFILE 'miniforge3\python.exe'
$identityCode='import platform,sys;print(platform.system(),platform.node(),sys.version.split()[0],sys.maxsize.bit_length()+1,sep=chr(124))'
& $py -B -c $identityCode
if($LASTEXITCODE -ne 0){throw 'PYTHON_IDENTITY_PRECHECK_FAILED'}
```

Expected output begins `Windows|` and ends `|64`. This does not create a QA marker or run the independent checker.

The new V3 Windows script still pins the original F0 HEAD `f2e333df2f9ca24a8e483507c3cfc386ad9c76f0`, exact source commit `782f101f001973f8c23f23b22ae2b0896232d722`, three Git blobs for broker V3 / worker V4 / independent checker, four preexisting marker SHA-256, and the Manual/LocalService `TTMP01Broker` SCM Stopped/PID0. It downloads exact sources **only into TTM** and runs Python checker once; checks all positive and negative fixtures, local source SHA-256, and then read-only checks disk/RAM/csc presence and future output-file absence.

It does **not** execute `csc.exe`, compile an EXE/DLL, change SCM, start services, modify ACL/accounts/ledger, run P00/F0/W01–W12 or edit science lineage. Its result is published to GitHub QA branch and read back by SHA-256. An encountered BLOCK/FAIL preserves marker and evidence and **must not** trigger automatic rerun.

## Gate status

- Previous source static: 48/48 textual checks, 12/12 negative mutations.
- Successor V3 PowerShell source: 19/19 targeted static checks; native Windows PowerShell parse **pending**.
- Target Python QA: **BLOCK_PRE_QA_INFRASTRUCTURE**, not scientific FAIL and not a Python checker FAIL.
- Independent Python QA, csc preflight, compilation: **NOT_EXECUTED** for this successor.
- `P01=OPEN`; `P02=NOT_OPENED`; `NORMAL_STOP=NOT_REQUALIFIED`; `NATIVE_SECURITY=NOT_QUALIFIED`; `W01_W12=NOT_EXECUTED`; `L1_GROUPED_QA=NOT_AUTHORIZED`.

Next gate: `TTM_P01_L1_V3_V4_WINDOWS_PYTHON_QUOTE_FIX_STATIC_QA_ADJUDICATION`, then only after a PASS receipt, separately authorize the exact source compile-only runner. Do not infer PASS from PowerShell parse alone.

Reference: https://learn.microsoft.com/en-us/powershell/module/microsoft.powershell.core/about/about_parsing?view=powershell-5.1
