# TTM P01 — F0 one-shot offhost execution attempted; functional result INCONCLUSIVE

**Operation:** `TTM_P01_QA0_F0_SINGLE_SHOT_FUNCTIONAL_SMOKE_EXECUTION_GATE`  
**Date:** 2026-11-06.  
**Repository:** `https://github.com/minhtri22/TokenToModel-Lab`.  
**Implementation branch:** `implementation/p01-i0a-s-f0-static-20261106`, source HEAD `f2e333df2f9ca24a8e483507c3cfc386ad9c76f0`.  
**Documentation branch:** `design/p01-tokenizer-data-prereg-20261105` (PR #4 Draft); no source edits in this adjudication.

## 1. Scope and identity

The user authorized **exactly one** small F0 functional smoke execution, without real corpus/GPT training, auto-rerun or P00 cleanup. The pre-existing Windows implementation had no certified Job Object / Write Broker. RemoteMCP device `machine-1` was ONLINE with fresh heartbeat, but the existing TTM project was `NON_GIT` and did not furnish an approved managed Git task/worktree route for the manually created P01 worktree. No Windows runtime command was submitted and no research adapter was used.

To avoid running unqualified code on the user's Windows host, the assistant prepared an **offhost Linux chroot** isolated from the user's Windows filesystem. This is a **functional demo environment**, not a certified Windows/QA0 security barrier. The source files were derived from the earlier exact-byte SHA-256-verified P01 one-shot script and the later GitHub-pinned patch; **13/13 files matched exact GitHub blob SHA-1 at the pinned implementation commit**. AST parsing passed for 9/9 Python files; this did **not** execute imported P01 code.

The offhost chroot contained the copied project files and Python standard library only. It launched CPython 3.13.5 as UID/GID 65534:65534 with `-I -S -B`, no writable paths in the chroot for the worker, elapsed-time timeout 25 seconds, memory limit 512 MiB, CPU-time limit 12 seconds and finite file-descriptor/core limits. Network containment was **not independently attested by seccomp or network namespace** (namespace creation is disallowed in this container); code was reviewed for network usage and host DNS was unavailable. Therefore `OS_ISOLATION_SECURITY_PASS` may not be claimed.

## 2. Single execution attempt and failure domain

Before submitting the test command, a one-shot execution lock was created. The external command requested **exactly** ten methods of `qa.p01.qa0_f0_smoke_test` and was sent once, without retry.

Observed:
- `F0_SINGLE_SHOT_PROCESS_EXIT=120`.
- `F0_SINGLE_SHOT_STDOUT_STDERR.log`: **0 bytes**, SHA-256 `e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855`.
- No test name, test total, pass/fail count, or functional result was received. **The number of tests actually run is not known** and must not be inferred as zero, ten or PASS.
- The command had been assigned `prlimit --fsize=0` while redirecting stdout/stderr to a **regular file**. This resource limit inadvertently covers the log file, not only prospective P01 file writes.
- An **independent non-P01 canary**, consisting solely of standard Python `print('CANARY_ONLY_NO_P01_IMPORT')`, when run under the same `prlimit --fsize=0` and redirected to a regular file, **also returned exit 120 with a 0-byte log**. This reproduces the output-capture failure without importing any P01 module.

**Diagnosis:** `F0_OUTPUT_CAPTURE_LIMIT_ERROR=REPRODUCED_BY_NON_P01_CANARY`; loss of stdout is explained by the `fsize=0` external file-limit policy. We cannot independently prove the child reached test execution. This failure is at the *supervisor/output-capture* layer, **not evidence that BPE, checker or source guard functionality failed**.

## 3. Scientific and security separation

| Gate | Result |
|---|---|
| Source identity | `PASS_GIT_BLOBS_13_OF_13` |
| Python syntax offhost | `PASS_AST_9_OF_9` |
| Offhost stdlib / read-only root preflight | `PASS_UID_65534_NO_PROJECT_WRITE` |
| One-shot command attempted | `YES_EXACTLY_ONE` |
| Completed F0 smoke evidence | **`INCONCLUSIVE_NO_TEST_OUTPUT`** |
| Windows QA0 Job Object / Write Broker certification | **`NOT_ESTABLISHED`** |
| Windows P01/P00 runtime mutation | `NONE` |
| E0 scientific execution / training | `NONE` |
| lineages and main | `UNCHANGED` |

Only the offhost sandbox files, one-shot marker, stdout/stderr log and diagnostic non-P01 canary were created. The user's Windows worktrees were not used by the smoke. No Git worktree was created in the offhost environment; this was a plain byte-for-byte source copy, not a clone.

Locally generated receipt: `TTM_P01_F0_SINGLE_SHOT_INCONCLUSIVE_RECEIPT_20261106.json`, SHA-256 `42289cd5ec366625a50417f1538d14fcea476cb16035f11b0da88a76f87bfab0`. It is a transcript-based technical receipt **not a signed node scientific receipt**. A copy is supplied to the user as a conversation artifact; this GitHub text report does not claim to contain its full bytes.

## 4. Corrective action, NOT executed

**Do not automatically rerun the F0 suite.** The original one-shot is consumed and its outcome remains INCONCLUSIVE.

For a **separately authorized subsequent attempt**, change only the external supervisor to leave the output channel writable (e.g., `fsize=1048576` for a 1-MiB bounded log or capture via a pipe unaffected by a per-file-size limit). Keep the child chroot read-only, nonprivileged, pinned source hashes, no corpus, no network as verified, and the same 10-test source. Validate log capture using a non-P01 canary before any subsequent P01 test and do not repeat the original script. Runtime guard qualification on Windows remains a distinct task.

**Next operation:** `TTM_P01_QA0_F0_SINGLE_SHOT_OUTPUT_CAPTURE_REPAIR_AND_SEPARATE_RERUN_DECISION`. The user must explicitly authorize **a new one-shot attempt** if desired; the previous authorization cannot be silently reused. No cleanup of P00 or P01, no Git merge, no lineage append.

## 5. Final verdict

`F0_OFFHOST_SOURCE_IDENTITY=PASS_13_OF_13`  
`F0_OFFHOST_EXECUTION_ATTEMPTS=1`  
`F0_OFFHOST_PROCESS_EXIT=120`  
`F0_OFFHOST_STDOUT_BYTES=0`  
`F0_TEST_RESULTS=UNKNOWN`  
`F0_FUNCTIONAL_VERDICT=INCONCLUSIVE_NO_TEST_OUTPUT`  
`F0_OUTPUT_CAPTURE_CANARY=REPRODUCED_EXIT_120_WITH_ZERO_BYTES`  
`F0_AUTOMATIC_RERUN=FORBIDDEN`  
`QA0_WINDOWS_SECURITY_VERDICT=NOT_ESTABLISHED`  
`E0_AND_GPT_TRAINING=NOT_EXECUTED`.

Infrastructure/QA troubleshooting is not a scientific result; do not append this to `lineage.md`.
