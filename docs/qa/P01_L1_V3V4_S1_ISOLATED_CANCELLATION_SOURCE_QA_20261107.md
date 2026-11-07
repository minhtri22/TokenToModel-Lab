# TTM P01 L1 / S1 — Isolated cancellation harness (source-only)

Date: 2026-11-07. This is an **engineering source-only artifact**, not an executed Windows-native or scientific result.

## Exact GitHub pins

- Harness: `qa/p01/windows/S1/TTMS1IsolatedCancellationHarness.cs`
  - Git blob `872c67174c6fbbcea9941fe3bfa0acee3cddfb7c`
  - SHA-256 `fd179c74fa1a136d791a5f9f6394ea657c58e7a46d1983c0eafa81051e99d6a9`
- Independent Python QA: `qa/p01/windows/S1/Independent-QA-S1-IsolatedCancellation-Static.py`
  - Git blob `81d78f60a2c92e29e2d4818dfdf15953487768b8`
  - SHA-256 `78d873cba4f0078187c9126ceb4a20ecade78c40ca74ca163e02e554384c3227`
- Source freeze commit `ec5b7bd181a584f287aa419aabef8298f3d95bc8`.
- Source-only second-implementation audit: `artifacts/qa/p01/S1_ISOLATED_CANCELLATION_SOURCE_INDEPENDENT_STATIC_AUDIT_20261107.json`; `41/41` predicates and `16/16` negative variants rejected. The GitHub-published Python checker has **not yet been run on target Windows**. No compiler, harness or service was run in this step.

## Precisely what S1 covers

The **standalone** `TTMP01S1.IsolatedCancellationHarness` chooses two distinct pipe names with the fixed prefix `TTM_P01_S1_ISOLATED_` and a random GUID. It does **not** use `TTM_P01_L1_BROKER_V1`, Broker V3 EXE, Worker V4 DLL, `TTMP01Broker` service, a real worker account, privileged credentials or the scientific workspace. Its pipe DACL is protected and grants full control to the current process user SID; both pipe endpoints stay in the same process.

Two cases are encoded in source:

1. `IDLE_ACCEPT`: the async server begins waiting for a connection; no client connects; `CancelIoEx` requests cancellation. The harness waits at most 4000 ms for asynchronous completion and only accepts a canceled `EndWaitForConnection` with Win32 `ERROR_OPERATION_ABORTED=995`.
2. `SILENT_READ`: a local client connects (bounded at 1500 ms), but never writes a payload; the server issues `BeginRead`, requests cancellation, waits at most 4000 ms for completion and only accepts a canceled `EndRead` with Win32 error 995.

Any premature completion, unexpected Win32 error, timeout, or normal completion of a deliberately canceled operation results in `BLOCK_*`, process exit 3 and **no PASS claim**. No file is written; future diagnostics are stdout-only. Error `1168` (`ERROR_NOT_FOUND`) is tolerated at the cancellation-request stage only if the subsequent operation still independently demonstrates canceled completion.

**Important scope limitation:** `CancelIoEx` only requests cancellation. A timed-out operation is not synchronously disposed; in such a case the harness blocks and leaves OS cleanup to process exit. A future actual native execution needs an **external process-bounded watchdog**, exact project-only process ownership, and a separate one-shot permit. An internal 4s I/O wait does not prove the process will always exit within a fixed time. Source QA does not establish the runtime result.

## Independent source review and negative variants

An independent JS review of the exact GitHub source passed 41/41 textual/structural safety contracts; 16/16 in-memory mutants were detected. Mutants cover deterministic/production pipe name, insecure DACL, broad SID, allowing runtime arguments, synchronous pipe, missing `CancelIoEx`, inverted abort check, unexpected normal-success acceptance, unbounded wait, timeout accepted as PASS, premature disposal, skipping the silent-client case, service control injection, file mutation, and client writes. The independent Python checker is published as a separate verifier with corresponding test predicates/mutations, but is **pending execution**; do not represent it as a Windows PASS.

## Governance boundaries

- `S1_SOURCE_IMPLEMENTED=YES`; `S1_SOURCE_STATIC_JS=PASS_41_41_NEGATIVE_16_16`.
- `S1_PYTHON_CHECKER_WINDOWS=NOT_EXECUTED`; `S1_CSC_COMPILATION=NOT_EXECUTED`; `S1_NATIVE_EXECUTION=NOT_EXECUTED`; `S1_PERMIT=NOT_ISSUED`.
- `COMPILE_ONLY_BROKER_V3_WORKER_V4=PASS`, existing binaries and all existing consumed markers unchanged.
- `NORMAL_STOP=NOT_REQUALIFIED`; `NATIVE_SECURITY=NOT_QUALIFIED`; `P01=OPEN`; `P02=NOT_OPENED`.
- P00, 10 F0 results, original HEAD `f2e333df2f9ca24a8e483507c3cfc386ad9c76f0`, append-only science lineage, P00–P12 sequence, historical engineering PASS/FAIL, W01–W12 and grouped L1 QA unchanged. No SCM installation/start/stop/configuration, no ACL/account/credential mutation, no binary rebuild or cleanup.

## Next minimal gate (still no native execution)

Run the pinned independent Python checker on an isolated copy of the exact pinned S1 harness:

```text
python -B Independent-QA-S1-IsolatedCancellation-Static.py --source TTMS1IsolatedCancellationHarness.cs --expected-sha256 fd179c74fa1a136d791a5f9f6394ea657c58e7a46d1983c0eafa81051e99d6a9
```

Required `PASS_SOURCE_STATIC_NO_NATIVE` with all 41 positive checks and 16 negatives. Verify the checker and harness files against both Git blobs and SHA-256 before execution. The Python checker reads only the source; no science seeds or native execution.

Only after independent QA and separate Windows preflight PASS, design the **one-shot S1 execution permit**, including a future bounded launcher supervising exactly the owned S1 child process. S2–S5 and SCM/real worker remain prohibited.

References: https://learn.microsoft.com/en-us/windows/win32/api/ioapiset/nf-ioapiset-cancelioex and https://learn.microsoft.com/en-us/dotnet/api/system.io.pipes.namedpipeserverstream.beginwaitforconnection
