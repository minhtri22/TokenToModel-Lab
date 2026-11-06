# TTM P01 L1 — Windows V3/V4 independent static QA: independent adjudication and compile-only handoff

Date: 2026-11-07. This record is engineering QA, not scientific evidence for `lineage.md`.

## Provenance
Repository `https://github.com/minhtri22/TokenToModel-Lab`, branch `audit/p01-l1-native-security-critical-fix-20261106`. Frozen original P01 HEAD `f2e333df2f9ca24a8e483507c3cfc386ad9c76f0`; P00 and ten F0 results unchanged.

Verified uploaded JSON and GitHub receipt `artifacts/qa/p01/L1_V3_V4_WINDOWS_INDEPENDENT_STATIC_QA_V4_20261106T180725764Z_b9748149.json`, commit `3860d08601ee77402d44926776f69208da103157`, blob `c5d1ae4eb6a154161638710d8c4ec2b3f82c82d1`, SHA-256 `619bd23aee3d901418a41e638597718929baed6caeb7e5db5e5078fd96cbed3c`.

- Independent Windows Python 3.13.12, x64: `46/46` static checks PASS; `9/9` negative mutations PASS; checker exit 0.
- Git-source identities and SHA-256:
  - Broker V3: Git blob `2fc1b63d6e21e7d8ac86184251974e9960572f3f`, SHA256 `8bbcb2bb7b9f0d69e20ebd8ac04fa6216b20c986207b4215617bac8ffb782ca4`.
  - Worker V4: Git blob `63d5407ccb3f9e15f8dda59ee6323a0e5009d860`, SHA256 `0e81e2a2ae9914daff20956d3d85f54b98dfa921ddd1764c771b8e9bae5cef04`.
  - Python checker: Git blob `0d42c4f7a4ac08c59022449210a323feed3a7495`, SHA256 `f75ce6ecf16fc5a3d00807dc958f4421027578f1aab7a587144c5ca2ab32642d`.
- Four historical markers were verified. New QA V4 marker `L1_V3_V4_INDEPENDENT_STATIC_QA_V4_ATTEMPT_20261107.lock` was created, SHA256 `515fc6c37370cb0080af05b87f837bff2e4f564f693cf49d7c1e5840d1f44e38`. Do not delete or replay.
- SCM `Stopped/PID0` during the QA preflight, Manual / LocalService exact broker V2 path. No service command or SCM configuration mutation.
- Compiler `C:\WINDOWS\Microsoft.NET\Framework64\v4.0.30319\csc.exe` available; SHA256 `eca02e6b15cde93009a59a3d129d5a77fb5008f2e1cf62cf573b6737c747ecc3`. D: free `37212024832` bytes, RAM free `12807836` KiB at check time. Those are observations, not permanent capacity guarantees. No compiler was invoked.

**Verdict: `PASS_WINDOWS_PYTHON_STATIC_QA_AND_COMPILE_ONLY_PREFLIGHT_NO_BINARY`.** Engineering source-level QA only. No proof of C# compilation, graceful broker shutdown, connected pipe DACL, independent worker denied rights, or SID-authenticated peer on a live Windows service. `NORMAL_STOP=NOT_REQUALIFIED`, `NATIVE_SECURITY=NOT_QUALIFIED`.

## Next separate gate: exact-source one-shot Windows C# compilation

No binary compilation is authorized by this document alone. A distinct script and static audit must first pin the PASS receipt commit/SHA256 and the three source file identities, and pass Windows PowerShell 5.1 syntax and guard review. A single subsequent authorized compile-only action shall:

1. Require elevated Windows token, frozen original worktree exact HEAD/branch/origin, and all project paths inside `D:\WORK\RESEARCH\TokenToModel-Lab`; refuse reparse-point boundaries.
2. Re-read SCM and require `TTMP01Broker` `Stopped/PID0`, Manual, LocalService, still configured to exact pinned V2 binary (do not modify SCM).
3. Check the V4 QA receipt and marker by SHA256, read the corresponding receipt from the immutable GitHub commit, verify `46/46`, `9/9`, checker exit 0 and source SHA256; check source bytes from the original project-local `exact_sources` evidence directory against the locked Git blobs.
4. Check exact `csc.exe` SHA256, fresh D: and RAM capacity, and absence of the two **new** destination outputs and a unique one-shot compile marker. Abort on any mismatch; never overwrite existing artifacts or clear prior markers.
5. Only after all preconditions PASS, atomically create a new TTM-local anti-replay marker. Direct temporary compiler files to an isolated TTM-local scratch directory; avoid writes to unrelated workspaces.
6. Invoke Windows Framework64 `csc.exe` exactly once for `BrokerAttestationServiceV3.cs` using `/target:exe` with `System.dll`, `System.Core.dll`, `System.ServiceProcess.dll` references. Expected output **only** `TTMP01Broker.attestationV3.exe`. If FAIL, do not invoke the worker compiler.
7. If broker compilation PASS, invoke `csc.exe` exactly once for `TTMWorkerNativeProbeV4.cs` using `/target:library`, `System.dll` and `System.Core.dll` references. Expected output **only** `TTMWorkerNativeProbeV4.dll`. If FAIL, retain partial outputs and receipts; no retries.
8. Record compiler exit codes, bounded diagnostics, binary SHA256 and file sizes. Write one new project-local JSON QA receipt, GitHub commit it under `artifacts/qa/p01/` and verify SHA256 readback. Do not erase compiler evidence, old markers, or any failed output.
9. No service installation, registration or start/stop; no SCM `binPath` switch, account/ACL changes, credential access, ledger writes, P00/F0 research execution, W01–W12, L1 grouped QA, P02 or science lineage edits.

**Gate remains `COMPILE_ONE_SHOT=NOT_EXECUTED`.** A successful compile would only establish Windows compilation, not runtime-native security PASS or safe service stop. The subsequent separate gate would be a one-shot SCM switch and minimal native smoke after another independent audit.

## Scope freeze

`P01=OPEN`, `P02=NOT_OPENED`, `W01_W12=NOT_EXECUTED`, `L1_GROUPED_QA=NOT_AUTHORIZED`. P00, 10 frozen F0 results, all PASS/FAIL evidence and approved P00–P12 phase order remain unchanged.
