# TTM P01 L1 — False BLOCK caused by malformed 63-character marker pin (2026-11-06)

## Evidence and conclusion

- GitHub original SCM stop receipt: `artifacts/qa/p01/L1_BROKER_V2_SCM_STOP_RECOVERY_20261106T163818549Z_8b9033ff.json` at `8a3666c655edba86bef2a841a31246fe19e0e870`.
- Original marker `L1_BROKER_V2_SCM_STOP_RECOVERY_ATTEMPT_20261106.lock` SHA-256: `f1ca3d0899fe6637a512e44dd073b449d4805ca8f8a8afa1e8a3989599143502` (**64** hex characters).
- Failed exact-process recovery receipt: `L1_BROKER_V2_EXACT_PROCESS_RECOVERY_20261106T164643808Z_85dd6aeb` at `441bec040d9d186bc2088d0747efe04d71a62f74`, `BLOCK_EXACT_PROCESS_RECOVERY_EXCEPTION`, `PRIOR_MARKER_SHA256_CHANGED_SCM_STOP_RECOVERY`.
- The failed script `qa/p01/windows/Recover-TTM-P01-L1-ExactProcessAfter1061-PS51.ps1` mistakenly pinned `f1ca3d0899fe6637a512e44dd073b449d4805ca8f8aafa1e8a3989599143502` (**63** hex characters). It differs from the original receipt; **this is an implementation defect**. Its source Git blob `24de8b99bf3c11250af5002d57603ebf0365713b` remains immutable.
- The failed run stopped on this bad comparison, with `termination_attempted=false`, `forced_termination=false`, `recovery_marker_sha256=null`, service still RUNNING PID 26200 at the observed time. **No exact process termination was attempted**, and the new force-recovery marker was not created by this run.
- Important: The failed receipt did not record the actual disk hash. Therefore this evidence **does not prove marker tampering, nor does it prove the disk marker is unchanged**. No assumption may replace Windows readback.

## Corrected source and authorized next scope

1. **Read-only forensic diagnostic**: `qa/p01/windows/Inspect-TTM-P01-L1-SCMStopMarkerMismatch-PS51.ps1`, Git blob `f3a62bb007d55fc6fef70fa4c2890a0abf37f990`. Requires elevated PowerShell 5.1, checks original HEAD/branch/origin, reads SCM state and exact prior stop marker bytes **locally**, recomputes expected marker bytes (from prior locked run ID, service name and process creation timestamp), reports SHA-256, size, first differing byte offset if any, creation/modified UTC, and evidence SHA-256 GitHub readback. It does not publish full marker bytes, open a process for termination, stop/start SCM, change ACL/accounts, delete markers or execute W01–W12. A BLOCK is still a valid diagnostic receipt, not a permit to override the pin.
2. **Corrected candidate for future process recovery**: `qa/p01/windows/Recover-TTM-P01-L1-ExactProcessAfter1061-V2-PS51.ps1`, Git blob `f630efdf62345f8a983ae7cf76d171bbd85646bb`. New filename, original failed code retained. Its three marker pins were independently compared against their exact GitHub receipts; all have 64 characters. The new script refuses pins not matching `^[0-9a-f]{64}$`. The source's guardrails still require exact current SCM PID, image path, process creation and matching kernel process HANDLE before any optional `-TerminateExactTTMProcess` action. **Not authorized for execution until independent Windows forensic readback and a separate operator decision**.
3. Static audit receipt: `artifacts/qa/p01/L1_EXACT_PROCESS_RECOVERY_FALSE_BLOCK_MALFORMED_PIN_20261106.json`; 17/17 source/pin comparison predicates present. This is not independent Windows execution or native security PASS.

### Safety
Do not invoke either the old `Recover-TTM-P01-L1-ExactProcessAfter1061-PS51.ps1` or old native security test again. Preserve all previous one-shot markers, receipts and GitHub FAIL evidence. Do not change SCM configuration, ACL, worker identity, DPAPI credential or ledger. No P00/F0 run, W01–W12, grouped L1 QA, P02 or science lineage mutation. All work remains inside the TTM project workspace except the separately authorized Windows service/process action that has **not** occurred in the new scripts.

Current verdicts: `MARKER_ACTUAL_DISK_SHA=UNVERIFIED`; `EXACT_PROCESS_TERMINATION=NOT_EXECUTED`; `NATIVE_SECURITY=BLOCK`; `P01=OPEN`; `P02=NOT_OPENED`; `W01_W12=NOT_EXECUTED`; `L1_GROUPED_QA=NOT_AUTHORIZED`.
