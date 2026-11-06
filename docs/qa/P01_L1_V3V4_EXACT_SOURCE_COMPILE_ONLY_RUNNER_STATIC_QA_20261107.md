# TTM P01 L1 — exact-source V3/V4 compile-only runner and independent static QA

Date 2026-11-07. Branch `audit/p01-l1-native-security-critical-fix-20261106`. Original frozen HEAD `f2e333df2f9ca24a8e483507c3cfc386ad9c76f0`, P00/F0 and P00–P12 roadmap unchanged.

## Implemented

1. `qa/p01/windows/Invoke-TTM-P01-L1-V3V4-ExactSource-CompileOnly-PS51.ps1`, Git blob `a3a130a17d54598631aafd2706d0341a990ee971` (208 lines).
   - By default it checks exact source, V4 Windows QA receipt (commit `3860d08601ee77402d44926776f69208da103157`, SHA256 `619bd23aee3d901418a41e638597718929baed6caeb7e5db5e5078fd96cbed3c`), original HEAD/branch/origin, four old markers, new QA marker, SCM Stopped/PID0, Manual LocalService, current pinned V2 executable, compiler exact SHA256, D:/RAM and output absence. **Default mode does NOT compile.**
   - Only separately authorized `-CompileOnce` can create `L1_V3_V4_EXACT_SOURCE_COMPILE_ATTEMPT_20261107.lock` atomically, then invoke csc exactly once for Broker V3 EXE and, only if it succeeds, once for Worker V4 DLL; outputs and compiler scratch are within the TTM project. Bounded diagnostics and hashes are recorded in a new TTM QA receipt committed and verified on GitHub. GitHub publication failure causes nonzero exit.
   - It cannot overwrite old artifacts and contains no Windows service, account, ACL, scientific lineage, F0 or test job operation. It **does not install** the newly compiled binary, change SCM binPath or start any service.

2. `qa/p01/windows/Independent-Audit-TTM-V3V4-CompileRunner-Static.py`, Git blob `1448fcd2a697a00babf49b1bf3942388188765af`.
   - Pure Python standard-library read-only source-contract checker, with explicit negative mutations. It does not import or execute PowerShell, invoke the compiler or write files.

3. `qa/p01/windows/Invoke-TTM-P01-L1-V3V4-CompileRunner-IndependentStaticQA-PS51.ps1`, Git blob `9d033eaab3374b889512dc1e1d67d9be2d5f4541`.
   - Fetches both exact sources at immutable GitHub commit `9bd43e88752448d7bdb9d5941ebef8c3ed269d4e`; checks the Git blobs, parses the compile runner with **native Windows PowerShell 5.1 `Parser.ParseFile`**, then creates a distinct one-shot source-QA marker and runs the separate Python source checker. It requires all positive checks and all 12 negative mutations PASS, and publishes a JSON receipt to the audit branch with SHA-256 readback.
   - **Crucial:** It never invokes `csc.exe`, does not pass `-CompileOnce`, and never starts/stops/configures the service.
   - The source-QA marker is `L1_V3_V4_COMPILE_RUNNER_INDEPENDENT_STATIC_QA_ATTEMPT_20261107.lock`. If created, retain it. Do not rerun after a failure; review receipt and issue a separately versioned successor if needed.

## What has actually been checked

- Independent source text review on exact GitHub source: **43/43** predicates PASS and **12/12** negative mutations detected. Both PowerShell sources passed a lexical delimiter balance check; this is **not** an equivalent to PowerShell native parsing.
- QA source and runner were read back by exact Git blob from GitHub. Engineering evidence: `artifacts/qa/p01/L1_V3V4_EXACT_SOURCE_COMPILE_RUNNER_STATIC_AUDIT_20261107.json`.
- **Native Windows PowerShell 5.1 parse and Python static checker have not run yet**; no native compilation is authorized in this phase. Never interpret a source-only QA as executable compile evidence.
- `CSC_COMPILATION=NOT_EXECUTED`, `SCM_ACTION=NONE`, `NATIVE_SECURITY=NOT_QUALIFIED`, `NORMAL_STOP=NOT_REQUALIFIED`, `P01=OPEN`, `P02=NOT_OPENED`; W01–W12 not executed, grouped L1 QA not authorized.

## Next gate — Windows source-only parse / independent QA

Use elevated Windows PowerShell 5.1. Download **only** `Invoke-TTM-P01-L1-V3V4-CompileRunner-IndependentStaticQA-PS51.ps1` from the final pinned GitHub audit commit and verify Git blob `9d033eaab3374b889512dc1e1d67d9be2d5f4541` before running. Run local `[Management.Automation.Language.Parser]::ParseFile` on this audit script first. Then invoke audit script exactly once; it downloads, verifies and parses the separate compile runner. It will create only TTM project-local source/evidence/QA marker files and a GitHub receipt.

Required evidence:
- `TTM_CSC_QA_PS51_PARSE=PASS_ZERO_ERRORS`;
- `TTM_CSC_QA_PYTHON_STATIC_QA=PASS_SOURCE_ONLY` with all checks and all 12 negatives;
- `TTM_CSC_QA_GITHUB_READBACK=PASS`;
- `TTM_CSC_QA_COMPILER_EXECUTED=NO`;
- audit script exit 0.

Any parser or static QA failure is BLOCK; no `-CompileOnce` invocation or compiler permit. Once this gate independently passes, **separately** authorize one exact native Windows compile attempt; if requested, preflight the default read-only mode of the runner before that attempt. The compile marker must not be manually removed or reused.

No automatic cleanup. All staging/receipts remain under `D:\WORK\RESEARCH\TokenToModel-Lab`; preserve all immutable markers, PASS/FAIL engineering evidence, the original frozen research lineage and P00–P12 sequence.
