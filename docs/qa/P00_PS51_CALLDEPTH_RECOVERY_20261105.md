# P00 Windows QA PowerShell CallDepthOverflow — 2026-11-05

## Classification

- Type: **INFRASTRUCTURE / QA HARNESS FAILURE**, not a model-science result.
- Source: the user's Windows PowerShell 5.1 console output.
- Previous script: `scripts/TTM_P00_WINDOWS_QA.ps1` at commit `24223818af8b05e5546462eb759c591a083ab202`.
- Previous exact SHA-256: `60be1d43a857a643d39388533f870ec967b7b84dff456b0a51e83a4dadf68548`.
- Observed exception: `CallDepthOverflow,TTM_P00_WINDOWS_QA.ps1`.
- No Windows QA result is claimed. No merge is authorized.

## Diagnosis

PowerShell command discovery is case-insensitive. Defining `function Git(...)` shadows the `git` native command in the same script; its `& git ...` invocation recurses into itself. A separate defect uses positional array splatting at the PowerShell function boundary instead of explicitly binding the `[string[]]` argv parameter.

## Repair

- Rename function to `Invoke-TtmGit` (and `Invoke-TtmGitWorktree`).
- Resolve `git.exe` as an external application via `Get-Command -CommandType Application`.
- Call the exact executable path, not the ambiguous `git` command.
- Bind every helper argv array with `-GitArgs @( ... )`.
- Preserve the existing canonical workspace, branch, source lineage, no-cleanup/no-merge rules.
- Add independent **static** regression checks in `tests/test_windows_bootstrap_static.py`.

## Evidence and remaining gate

Static source checks and local Python regression checks passed in the authoring environment. They do **not** replace Windows PowerShell 5.1 execution or independent Windows QA.

After fetching the repaired script from a pinned commit and confirming its SHA-256, resume exactly the original P00 checkout/QA intent. Do not delete, prune, or recreate any existing worktree. If the exact worktree already exists, stop for independent state inspection rather than using force.
