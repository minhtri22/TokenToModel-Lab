# TTM P01 L1 — CS1513 recovery PowerShell alias collision (2026-11-06)

## Evidence that must remain immutable
- User-run Windows recovery ID: `L1_CS1513_REPAIR_20261106T140633503Z_f82d10f7`.
- User-provided evidence SHA-256: `a505e755d6dfca0cd913b24761823bf4f7c842da8efefada7c2c9a0a0d9bca9c`.
- Exact GitHub evidence commit: `326efc82dc32e059de24bc44aea1bde21b82f21f`, file `artifacts/qa/p01/L1_CS1513_REPAIR_20261106T140633503Z_f82d10f7.json`.
- Result: `BLOCK_OR_COMPILE_FAIL`, exception `A positional parameter cannot be found that accepts argument 'PASS'.`; `checks={}`, `compiler_output=[]`.
- Compiler invocation was **NOT EXECUTED in this run**, so there is no new `CS1513` result. The previous `CS1513` compile FAIL remains valid.
- This failure arose at the first `R 'PINNED_LOCAL' 'PASS' ...` call: `r` is a PowerShell history alias. The abbreviation conflicted with the intended helper name.

## Fix and precise scope
- In `qa/p01/windows/Recover-TTM-P01-L1-CS1513-Compile-PS51.ps1`, renamed receipt helper `R` to `Write-RepairCheck` and changed all call sites, including failure branch.
- Final reviewed script Git blob: `475da7094bb77e128d807bcecaf07ed6f2048690`, correction commit `5f4f5e5658dba8b82e7c3ce7bc990f82be795e04`.
- This was source inspection only; the corrected script has **not** been executed on Windows. If stage files `BrokerAttestationService.fixed.cs` or `TTMP01Broker.fixed.exe` are already present, the script will refuse them rather than overwrite.
- The existing staging root, old C# source, original P01 worktree and prior QA receipts are not removed or changed by the correction.

## Next permitted test
Use a **new filename** for the corrected script under the TTM project's existing tools directory, verifying the blob SHA with `gh api`. Run the recovery script exactly once. It performs no account, service, DACL, worker, F0, W01–W12 or L1 grouped QA actions. It posts a new PASS/BLOCK/FAIL receipt to the same branch and verifies SHA-256 readback. Do not replay the previous provisioning `-Apply`.

## Gates
`POWERSHELL_ALIAS_BUG=FIXED_IN_GITHUB_SOURCE`
`EXACT_REVISED_SCRIPT_WINDOWS_RUN=NOT_EXECUTED`
`CS1513_WINDOWS_RECOMPILE=NOT_EXECUTED`
`SERVICE_AND_WORKER_IDENTITY=NOT_PROVISIONED`
`W01_W12=NOT_EXECUTED`
`L1_GROUPED_QA=NOT_AUTHORIZED`
`P01=OPEN`
`P02=NOT_OPENED`

Preserve P00, original HEAD `f2e333df2f9ca24a8e483507c3cfc386ad9c76f0`, 10 F0 results and phase order. Do not append engineering evidence to science `lineage.md`.
