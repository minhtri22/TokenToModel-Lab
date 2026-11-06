# P01 QA0 — Windows Fast-forward PASS, AST inconclusive, no smoke execution

**Operation:** `TTM_P01_QA0_F0_WINDOWS_SAFE_SYNC_RESULT_ADJUDICATION`.  
**Evidence origin:** user-supplied Windows PowerShell 5.1 console text from DESKTOP-4PSD0G2, observed `2026-11-06T01:51:00.7003253Z`. No original signed log/receipt was supplied.  
**Project:** `minhtri22/TokenToModel-Lab`, local project `D:\WORK\RESEARCH\TokenToModel-Lab`.  
**P01 worktree:** `D:\WORK\RESEARCH\TokenToModel-Lab\worktrees\p01-f0-static-i0a-20261105`.  
**Target commit:** `f2e333df2f9ca24a8e483507c3cfc386ad9c76f0`.  
**Parent:** `7e8b37d59b10b7a71603f6b446b57b9e3a9cb645`.  
**A separate PowerShell recovery script created outside the project for user to run, not executed on Windows by assistant:** `TTM_P01_QA0_AST_ONLY_RECOVERY_AFTER_FF_20261106.ps1`, SHA-256 `c73a7353eb2407424afcabbf687b5a5a51fc7f5a2d084a0bdd3e8a72fce001a3`.

## User console observations

- `D_WORK_PATH, RESEARCH_PATH, ROOT_PATH, WORKTREES_PATH, P00_PATH, P01_PATH, GIT_PATH, GIT_WORKTREES_PATH=PASS`.
- `ROOT_TOPLEVEL, P00_TOPLEVEL, P01_TOPLEVEL, ORIGIN, ROOT_HEAD, P00_HEAD, P01_HEAD_BEFORE, P01_BRANCH=PASS`.
- `ROOT_CLEAN, P00_CLEAN, P01_CLEAN=PASS`, `WORKTREE_INVENTORY=PASS_EXACT_THREE`.
- `D_FREE_GIB=34.828`, `PREWRITE_EXACT_GIT_AND_SCOPE=PASS`.
- `FETCHED_COMMIT, P01_HEAD_STILL_OLD, EXPECTED_FAST_FORWARD_DISTANCE, EXACT_FIVE_FILE_DIFF, P01_HEAD_RECHECK=PASS`.
- `FAST_FORWARD_START`, `P01_HEAD_AFTER=PASS`, **`FAST_FORWARD=PASS`**.
- Immediately after `SYNTAX_CHECK_START`, Windows PowerShell 5.1 raises `NativeCommandError` for line `$astOutput = @(& $pythonExe -I -S -B -c $pythonSource $p01 2>&1)` and prints only the opening `Traceback (most recent call last):`. The error stops the .ps1 with exit 1; the terminal success marker is absent.
- **No output shows a smoke execution.** Do not treat AST/checker/QA0 as PASS or as a functional FAIL from an incomplete traceback.

## Adjudication

| Gate | Verdict |
|---|---|
| Windows P01 safe scope and before-sync Git state | **PASS user console** |
| Fast-forward from old to target | **PASS user console** |
| File `qa0_f0_smoke_test.py` now exists on Windows | **PASS read-only RemoteMCP Core task_read_file**, source header read back |
| Git HEAD target SHA after sync | **PASS user console**; RemoteMCP readback confirms worktree HEAD points to correct branch (does not independently resolve branch commit) |
| Python AST / JSON parse | **INCONCLUSIVE**, Python traceback not captured |
| QA0 F0 smoke | **NOT_EXECUTED**, authorization remains separate |
| E0 scientific execution and GPT training | **NOT_EXECUTED / NOT_GRANTED** |
| Cleanup, force/reset/second sync | **NOT_AUTHORIZED** |

The script sets `$ErrorActionPreference='Stop'` and captures the native Python stream with `2>&1`. In Windows PowerShell 5.1, a native process writing to stderr may surface a `NativeCommandError` treated as terminating, obscuring the full Python exception and the exit code. The available evidence does **not** prove whether the Python exception came from argument quoting in the multiline `-c` invocation, a file/path problem, or a syntax problem in P01 source. It is **not an authorization to rerun Git fetch/merge**.

## Recovery strictly restricted to syntax

The separately supplied recovery .ps1:
1. Refuses wrong host, wrong origin, dirty root/P00/P01, wrong P00/root/P01 commit, incorrect branch, reparse directories, or non-exact three-worktree inventory.
2. Never invokes Git fetch, merge, reset, clean, add, push or worktree lifecycle commands.
3. Pipes a fixed ASCII standard-library Python AST/JSON checker via **stdin** (`python -I -S -B -`), avoiding an inline multiline `python -c` command argument; never imports/executes P01 modules.
4. Temporarily allows native stderr to be captured (`$ErrorActionPreference='Continue'`) and prints **all** Python output plus exit code for analysis; fails closed on a nonzero code.
5. Rechecks Git and cleanliness afterward; never runs smoke, uses no real corpus, does not train or cleanup.

The embedded Python checker in the .ps1 was syntax-validated independently with `ast.parse` in a separate sandbox. **The Windows script itself has not been exercised on the target**, and a PASS must not be anticipated.

## Decision

`TTM_P01_QA0_WINDOWS_SAFE_SYNC=PASS_USER_CONSOLE`  
`TTM_P01_P01_TARGET_COMMIT=f2e333df2f9ca24a8e483507c3cfc386ad9c76f0`  
`TTM_P01_QA0_AST_CHECK=INCONCLUSIVE_NATIVE_STDERR_INTERRUPTED`  
`TTM_P01_QA0_AST_RECOVERY=PREPARED_NOT_RUN`  
`TTM_P01_QA0_SMOKE=NOT_EXECUTED`  
`TTM_P01_QA0_RUNTIME_ADMISSION=HOLD`  
`TTM_P01_E0_SCIENTIFIC_PERMIT=NOT_GRANTED`  
`TTM_P01_NO_SECOND_FAST_FORWARD=true`  
`TTM_P01_NO_P00_CLEANUP=true`.

**Bước tiếp theo:** `TTM_P01_QA0_F0_AST_ONLY_RECOVERY_AND_RUNTIME_GATE_DECISION`: run the syntax-only recovery once, analyze the full `PYTHON_LOG` and `PYTHON_EXIT_CODE`, then separately decide whether a minimal isolated F0-only smoke is safe. No science run or model training.

Infrastructure errors are not scientific results; do not append them to `lineage.md`.
