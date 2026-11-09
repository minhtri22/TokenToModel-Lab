# G1 Windows QA PS5.1 native argument quoting V2 fix

**Date:** 2026-11-10. **Decision:** `WINDOWS_QA=NOT_EXECUTED_AFTER_FIX`; `G1_SCIENCE_LOCK=HOLD`.

## Exact defect
On the owner's Windows PowerShell 5.1, V1 runner line 95 passes Python native `-c` argument with interior double quotes:
```powershell
$pyVersion = & $PythonExe -c 'import sys;print("%d.%d"%sys.version_info[:2])'
```
The Python process receives the malformed expression `print(%d.%d%sys.version_info[:2])` and raises SyntaxError. The subsequent STOP_G1_PYTHON_NOT_312 is misleading: the interpreter's version has not been successfully inspected.

## Exact minimal fix
Versioned V2 runner artifact filename: `Run-G1-WindowsTrustBoundary-OnePacket-PS51-V2-20261110.ps1`, owner-downloadable from the handoff conversation. One changed source line, all other bytes identical:
```powershell
$pyVersion = & $PythonExe -c 'import sys;print(sys.version_info.major,sys.version_info.minor,sep=chr(46))'
```

| Evidence | SHA-256 |
|---|---|
| V1 original runner (preserved) | `2e9ac2bd72d7a20956e0f8da8ccc13bb8183fa58fa53e0c20aeecc48f292c4bc` |
| V2 one-line corrected runner | `28d6294e4213c9f2d2741b2b22b6a1c6839137bc88cf7fa429706aad65150b33` |
| Existing original inner ZIP (unchanged) | `5584dfb61d293f2946b66ef9f5e4bb4a0703c415ced0946ff2bacc302e95013c` |
| Existing outer owner ZIP (unchanged) | `66d3f8599bec733b6aff1b05e5e13fbc7c1c984b3a63ab39a7c74c78aa926d83` |

Patch proof: the V2 bytes replaced with V1 line produce **exactly** original V1 bytes. Syntax of the new Python `-c` code validated by running it in isolated Python; **not** a Windows PowerShell 5.1 execution PASS. No QA output folder had been created when V1 stopped (it fails before that stage).

## Owner re-run contract
Put versioned V2 `.ps1` alongside the already unpacked original inner ZIP and patched QA watchdog in `D:\WORK\RESEARCH\TokenToModel-Lab\_tmp`, verify V2 SHA-256, and run the V2 script under non-elevated PowerShell 5.1. Do not rerun V1, overwrite pinned V1, edit anything outside this project or modify ACL/user principals. The existing script verifies original inner ZIP and safe watchdog hashes, then writes a new `_tmp\G1_TRUST_BOUNDARY_WINDOWS_QA_*` receipt.

All scientific TEST/data, Qwen GPU, real student checkpoints and owner science permit remain unaccessed. DACL inventory and synthetic Win32 Job Object QA can only be claimed on receipt after the owner's successful actual run. Separate worker SID, independent witness rollback domain, trusted pack transactions and T4 watchdog **remain NOT_TESTED**, even after a local current-user synthetic PASS.

**Status:** `V2_SOURCE_PATCH_PRECHECK=PASS_EXACT_ONE_LINE` · `V2_WINDOWS_EXECUTION=PENDING_OWNER` · `G1_SCIENCE_LOCK=HOLD`.
