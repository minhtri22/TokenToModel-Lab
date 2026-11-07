# TTM P01 L1 — S1 Windows source QA V1 failure and V2 recovery

Date: 2026-11-07. **Engineering QA only, no science lineage change.**

## V1 failure is immutable

Run `L1_S1_WINDOWS_INDEPENDENT_SOURCE_QA_20261107T021034614Z_ec579411`, GitHub receipt commit `f99a5ed372fde9787cc050b1f492021e9d4842e3`, blob `7ea7ca44e9aa1ce6032218b0189d06f791bc43d9`, SHA256 `53fdf29600117f39eb5fd3c68a6d6276eaaa73b0238859fd6a79725260b95b41`.

V1 `BLOCK_WINDOWS_S1_SOURCE_QA`, Python exit 1, traceback `ValueError: substring not found` at checker line 146, caused by `c.index("pending.AsyncWaitHandle.WaitOne(CompletionTimeoutMs)")` on the deliberate `remove_completion_bound` mutant, where that string has been removed. The checker crashed instead of marking the fixture as rejected. The V1 QA one-shot marker was created; SHA256 `d39f4cd82c48c0401d48089c961f353663955671135c1e76ede06334b0b0f877`. **Never delete or replay V1.** The source files were correctly pinned, SCM was read-only `Stopped/PID0` before the crash; `scm_after` was not reached. No C# native compilation or S1 execution occurred.

## V2 successor: exactly scoped repair

- Unmodified harness: `qa/p01/windows/S1/TTMS1IsolatedCancellationHarness.cs`; blob `872c67174c6fbbcea9941fe3bfa0acee3cddfb7c`, SHA256 `fd179c74fa1a136d791a5f9f6394ea657c58e7a46d1983c0eafa81051e99d6a9`.
- **New** V2 Python checker: `qa/p01/windows/S1/Independent-QA-S1-IsolatedCancellation-Static-V2.py`; blob `506feeb2535421f50caa316f8f10d8b49b9f01de`, SHA256 `0ca28aab136363ea032d5d648645e75adc53166bd4e2d2cf7428e0a3b0b3c7b4`. Changes: check for both anchors before comparing their locations with `str.find()`; missing anchors reject normally. Unexpected negative-mutant checker exceptions are separately recorded and disqualify PASS instead of being treated as a valid rejection. The original 41 positive predicates and 16 negative fixtures remain.
- **New** Windows PS5.1 QA runner: `qa/p01/windows/S1/Invoke-TTM-P01-L1-S1-Windows-IndependentStaticQA-V2-PS51.ps1`; blob `19d168301892ebed3d427ac9d774c674bbaec3fa`, SHA256 `7b007578a8e1dd59166f6d0f439b0ebb3420989a25706f052698836743fa1e95`. It fetches the unmodified harness and V2 checker from immutable commit `5a5389ae7d98bfd3140296f43476c99859862979`, verifies SHA256 and Git blob, refuses if the exact V1 failure receipt or marker differs, checks original frozen HEAD/branch/origin and SCM stopped identity, and runs only `python -B` for source QA.

V2 marker has a **new name** `L1_S1_WINDOWS_INDEPENDENT_SOURCE_STATIC_QA_V2_ATTEMPT_20261107.lock`; it is only created on the Windows target when the approved V2 script runs. The V2 run must publish an immutable local JSON receipt + SHA256 to GitHub audit branch and re-read it; no automatic cleanup. The script does not call C# compiler or run any native harness, does not install/change/start/stop SCM, does not touch worker ACL or identities, and does not invoke scientific seeds.

## Static-review evidence and scope

Second-implementation review of the V2 runner: **30/30** static predicates PASS; **13/13** mutants detected. This is textual source evaluation, **not Windows PowerShell 5.1 native parsing** and not actual Python run. The V2 Python checker is also source-reviewed for safe anchor checks and exception-as-FAIL behavior. V2 Windows QA status is `NOT_EXECUTED`.

A separate Windows PowerShell 5.1 `Parser.ParseFile` check for the exact V2 runner is required before invoking it. After this source QA is successful, S1 native execution still requires separate process-bounded watchdog, source lock, one-shot permit and independent QA decision.

Governance: `BROKER_V3_WORKER_V4_COMPILE_ONLY=PASS`, `BINARY_READBACK=PASS`, `S1_NATIVE=NOT_EXECUTED`, `NORMAL_STOP=NOT_REQUALIFIED`, `NATIVE_SECURITY=NOT_QUALIFIED`, `P01=OPEN`, `P02=NOT_OPENED`. Original HEAD `f2e333df2f9ca24a8e483507c3cfc386ad9c76f0`, P00, ten F0, all historical markers and evidence, `lineage.md` and P00–P12 remain unchanged.

Next exact gate: `TTM_P01_L1_V3V4_S1_WINDOWS_INDEPENDENT_PYTHON_STATIC_QA_V2_ONE_SHOT_EXECUTION_AND_ADJUDICATION`.
