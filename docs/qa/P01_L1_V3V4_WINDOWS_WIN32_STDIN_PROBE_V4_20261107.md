# TTM P01 L1 — Windows Python Win32 marker probe repair, V4 successor (2026-11-07)

## Evidence

- Failed V3 Windows preflight receipt `L1_V3_V4_WINDOWS_INDEPENDENT_STATIC_QA_V3_20261106T175133679Z_91490c75`, GitHub commit `c68e7f1871db0a68f9e3a9cd54b43e87ccbb1658`, SHA-256 `db4720cac9edf12d3a46d0129a0ee757d679c08eb6c071b6a952f501c0483634`.
- Confirmed: `ADMIN`, frozen P01 original HEAD `f2e333df2f9ca24a8e483507c3cfc386ad9c76f0`, `SCM=Stopped/PID0`, all four older markers, Windows Python 3.13.12 x64 and GitHub authentication PASS.
- V3 error `File "<string>", line 1` occurred during the separate `ctypes.WinDLL("kernel32",...)` Python `-c` marker check. `source_files=[]`, `python_checker_exit=null`, `qa_marker_sha256=null`: V3 QA did not start; its marker creation is not recorded. `CSC_EXECUTION=NOT_EXECUTED`, `SCM_ACTION=NONE`.
- Cause is probable legacy Windows PowerShell 5.1 native argument quoting of the second `python -c` invocation, not proved by the incomplete traceback. Original V2 and V3 sources and FAIL receipts are preserved, never rerun.

## Source-only fix (not Windows-executed)

New script: `qa/p01/windows/Invoke-TTM-P01-L1-V3V4-IndependentWindowsStaticPreflight-V4-PS51.ps1`, Git blob `eb1244c1b1ba49b473a91d04fe1032b052016343`.

It:
- Retains exact locked GitHub source commit `782f101f001973f8c23f23b22ae2b0896232d722`, broker V3 source blob `2fc1b63d6e21e7d8ac86184251974e9960572f3f`, worker V4 source blob `63d5407ccb3f9e15f8dda59ee6323a0e5009d860`, independent QA Python source blob `0d42c4f7a4ac08c59022449210a323feed3a7495`.
- Retains exact HEAD/branch/origin, four old marker hashes, Manual/LocalService `TTMP01Broker` stopped with PID0, user Miniforge Python x64, and GitHub auth checks.
- Replaces only the Win32 attribute check transport: a multiline Python `ctypes.WinDLL("kernel32",use_last_error=True)` source string is **piped to `python -B - <marker_path>` via stdin**, never embedded in the command-line `-c` argument. The only `-c` remaining is the previously confirmed quote-free identity check.
- Stores the marker probe's process exit and up to 2048 characters of output; stores Python independent checker stdout hash and a bounded error transcript on failure.
- Uses distinct new anti-replay marker `L1_V3_V4_INDEPENDENT_STATIC_QA_V4_ATTEMPT_20261107.lock` and new V4 QA run ID. It does not delete or reuse old markers.
- Copies only three pinned source files into a **new TTM project-local evidence subdirectory**, runs the independent Python checker **one time** with `-B`, checks PASS positive/negative results and exact SHA-256, inspects resource capacity and installed Framework64 `csc.exe` **without invoking it**, uploads receipt to GitHub and verifies SHA-256 readback.
- Does **not** compile, install, start/stop service, configure SCM, change accounts/ACL, edit original P00/F0 or science lineage, run W01–W12 or open P02.

Source verification: 37/37 targeted source-only predicates and separate `ast.parse` of the embedded Python probe in a non-Windows sandbox PASS. These are *not* Windows PowerShell parser PASS or Windows native QA PASS. The actual Windows preflight remains pending.

## Non-mutating Windows probe (BEFORE any one-shot execution)

Use elevated Windows PowerShell 5.1:

```powershell
$py=Join-Path $env:USERPROFILE 'miniforge3\python.exe'
$marker='D:\WORK\RESEARCH\TokenToModel-Lab\worktrees\_ttm_p01_l1_service_provision_20261106\L1_V3_V4_INDEPENDENT_STATIC_QA_V4_ATTEMPT_20261107.lock'
$probe=@'
import ctypes
import sys
kernel=ctypes.WinDLL("kernel32",use_last_error=True)
get_attributes=kernel.GetFileAttributesW
get_attributes.argtypes=[ctypes.c_wchar_p]
get_attributes.restype=ctypes.c_uint32
attributes=get_attributes(sys.argv[1])
win32_error=ctypes.get_last_error() if attributes==0xffffffff else 0
print(str(attributes)+"|"+str(win32_error))
'@
$result=@($probe | & $py -B - $marker)
if($LASTEXITCODE -ne 0 -or $result.Count -ne 1 -or $result[0] -cne '4294967295|2'){throw 'READONLY_MARKER_STDIN_PROBE_NOT_PASS'}
Write-Host 'TTM_V3V4_V4_MARKER_STDIN_PROBE=PASS_WIN32_2'
```

This proves only the **new V4** marker is absent in this observation, not that the full native QA has passed. Do not touch previous markers. If it fails, stop and preserve evidence; do not invoke the V4 one-shot script.

## Separate one-shot Windows static QA execution gate

After the read-only probe PASS, download the exact V4 script from a new pinned audit commit and Git blob, verify exact bytes and PowerShell 5.1 `Parser.ParseFile`, then invoke the script once using `powershell.exe -NoProfile -ExecutionPolicy Bypass -File <script>`. Do not run the quarantined V2/V3 scripts. If V4 BLOCK/FAIL after marker creation, no rerun; review its GitHub receipt and source pins. No native compile authorized by a static QA PASS.

PASS requirements: `TTM_V3V4_NEW_MARKER_ABSENCE=PASS_WIN32_2`, `TTM_V3V4_INDEPENDENT_PYTHON_QA=PASS_SOURCE_ONLY`, `TTM_V3V4_COMPILER_PREFLIGHT=PASS_READONLY`, `TTM_V3V4_GITHUB_READBACK=PASS`, exit code 0. A successful verdict still means **source-only Python QA and compiler availability**, not C# compilation, normal service stop or native DACL qualification.

Current status: `P01=OPEN`, `P02=NOT_OPENED`, `NORMAL_STOP=NOT_REQUALIFIED`, `NATIVE_SECURITY=NOT_QUALIFIED`, `W01_W12=NOT_EXECUTED`, `L1_GROUPED_QA=NOT_AUTHORIZED`. Preserve P00, ten frozen F0, all PASS/FAIL evidence, all four old markers and P00–P12 ordering.
