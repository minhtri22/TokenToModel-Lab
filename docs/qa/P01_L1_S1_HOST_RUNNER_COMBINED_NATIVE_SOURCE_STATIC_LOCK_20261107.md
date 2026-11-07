# TTM P01 L1 — S1 exact-source host + combined native once runner: implementation/static handoff

Date: 2026-11-07. Engineering source-only implementation; **no native execution, no permit issued**.

## 1. Frozen scope

- Repository: `https://github.com/minhtri22/TokenToModel-Lab`
- Audit branch: `audit/p01-l1-native-security-critical-fix-20261106`
- Original frozen HEAD: `f2e333df2f9ca24a8e483507c3cfc386ad9c76f0`
- Only project workspace: `D:\WORK\RESEARCH\TokenToModel-Lab`; no SCM mutation, no P00/F0, W01–W12, P02 or science execution.
- Preserve all previously recorded S1 V1/V2/V3 FAIL/blocked launcher receipts and their markers. Reuse independently verified V3 Python source QA 41/41 and 16/16; **do not rerun**.
- Existing Broker V3 EXE/Worker V4 DLL are pinned and checked read-only; **do not rebuild**.

## 2. Source pins for this implementation

The source lock for the three runtime code inputs plus the independent Python QA is commit `8e2a2033187d22e8c44c7493e8853dafe974715f`.

| Input | Git blob SHA-1 | SHA-256 |
|---|---|---|
| `qa/p01/windows/S1/TTMS1JobWatchdogHostV1.cs` | `7eedfab02ab995507e36a9beee25772393dc70ab` | `986b622a4318459c68f666911b19f964ba0c129799139d5151a371bc4c8414b8` |
| `qa/p01/windows/S1/Invoke-TTM-P01-L1-S1-CombinedNativeOnce-PS51.ps1` | `611ac1506176c53fc6b51de7ea54d228a161bb98` | `463789ce69aa025271e36e6748339b89a626f82a3bdf61b1738b881c27a02505` |
| `qa/p01/windows/S1/TTMS1IsolatedJobWatchdogEngineV2.cs` | `5763ca10025bb928f161a0f33fa493d436107375` | `f8c07f486a4e373810e75ec1cf99d79414f66d7e74c65851d0ff268b949640c3` |
| `qa/p01/windows/S1/Independent-QA-S1-HostRunner-IntegratedStatic.py` | `46f240f23d6644ef3b81a1971d4253bb64087ecf` | `5f1ff0d53d79b2211faa39614733d2c5c129e6d4aefacc880e9a03db98c8e49a` |

The frozen S1 harness source is unchanged: blob `872c67174c6fbbcea9941fe3bfa0acee3cddfb7c`, SHA-256 `fd179c74fa1a136d791a5f9f6394ea657c58e7a46d1983c0eafa81051e99d6a9`.

One consolidated Windows source-QA launcher was additionally committed:

- `qa/p01/windows/S1/Invoke-TTM-P01-L1-S1-HostRunner-IntegratedStaticQA-PS51.ps1`
- Git blob `fde93fbb2c05cafe72d8c82efbe5fbef6cde7fc6`
- SHA-256 `3fec1b2d28e93c14832cc2e30148ac65e5223b397be3cb315c2e97e2cadfb793`.

## 3. What the two new runtime components actually implement

**Host V1** has one `Main`. It checks Windows x64, exact project and executable filename, pinned local permit and native marker SHA-256, exact permit decision `AUTHORIZED_ONCE_EXACT_SOURCE_S1_NATIVE`, one-shot identity and `allowed_native_runs=1`. It calls `IsolatedJobWatchdogV2.RunAfterExternalPermit` exactly once. The host is not an independent issuer; the PowerShell runner must fetch and validate the permit from an immutable GitHub commit.

**Combined native runner** defaults to `-Mode Preflight`, with no native compilation or marker creation. `-Mode ExecuteOnce` requires explicit `-PermitCommit` and `-PermitSha256`, a remote `artifacts/qa/p01/S1_NATIVE_COMBINED_PERMIT_20261107.json` with exact schema, decision, frozen HEAD, source/runner/compiler hashes, `scm_actions=FORBIDDEN` and exactly one allowed run. It checks original worktree HEAD/branch/origin, prior QA markers and native output pristine state before creating its own atomic native marker `L1_S1_NATIVE_COMBINED_ONE_SHOT_ATTEMPT_20261107.lock`.

After marking the attempt, the future authorized branch permits only two compilations: one frozen S1 EXE and one frozen host EXE combining Host V1 + Engine V2. It then starts the host once, owns that process handle, applies a 30-second outer wait and 3-second termination check on timeout, validates the Job Object result, exact output line/byte hash from the isolated child, SCM before/after and publishes a SHA-256-verifiable GitHub receipt. It does **not** delete the consumed marker or retry on FAIL. Compiler error text is retained in the engineering receipt. Local success is labeled `LOCAL_S1_PASS_PENDING_GITHUB_READBACK` until receipt upload/readback is proven.

**Important boundary:** source control and a consumed marker enforce the supported one-shot runner path for a trusted operator, not a security guarantee against an adversary with privileged access who deliberately bypasses the runner. Any future runtime qualification must evaluate this threat model explicitly.

## 4. Independent integrated static source QA

- A second JS implementation inspected exact GitHub source: **37/37** safety predicates PASS; **18/18** deliberate unsafe mutations detected.
- All **22** Python checker negative mutation anchors were found uniquely; the checker defines **66** positive and **22** negative cases.
- The Python checker itself has been committed but **has not yet executed on target Windows**. These numbers must not be misrepresented as 66/66 or 22/22 Windows PASS.
- PowerShell 5.1 native parser test for the new runner remains `NOT_EXECUTED`.
- `csc.exe`, CLR, P/Invoke ABI, Job Object and S1 native runtime remain `NOT_EXECUTED`.

Use the consolidated source QA script in §2 once on Windows. It fetches four exact source files by SHA, performs a PowerShell 5.1 parse on the runner, invokes only Python static QA, observes SCM read-only, writes one project-local receipt and publishes/reads it back on GitHub. The QA script itself creates **no native marker**. A QA failure must preserve the receipt and must not imply permission to run native.

## 5. Permit adjudication — HOLD, not a new micro-permit chain

The combined permit file **does not exist** at the current audited HEAD. Decision: `HOLD_NOT_ISSUED`.

The only remaining pre-decision engineering gate is the single consolidated Windows integrated static QA output (plus independent review of its receipt). If it PASSes, examine whether the exact host/runner source and fail-closed build/run behavior justify **one** permit for the two exact compilations and one isolated S1 native smoke. Under that permit, compiler and runtime ABI failures automatically BLOCK with no retry; negative timeout/termination behavior still requires grounded evidence before claiming broader native security.

Do not create separate permits for individual syntax checks, hashes or engineering receipt repairs.

Scope excluded from the permit: service startup/configuration, Broker/Worker rebuild, real-worker account switch, science F0, W01–W12, P02 opening or a claim of `NORMAL_STOP`/`NATIVE_SECURITY` qualification.

## 6. Current states and next step

`HOST_SOURCE=IMPLEMENTED`; `RUNNER_SOURCE=IMPLEMENTED_DEFAULT_PREFLIGHT`; `SOURCE_REVIEW=PASS_37_37_NEG_18_18`; `PYTHON_CHECKER_SOURCE=COMMITTED_66_POS_22_NEG`; `WINDOWS_INTEGRATED_QA=PENDING`; `NATIVE_PERMIT=HOLD_NOT_ISSUED`; `S1_NATIVE=NOT_EXECUTED`; `SCM=UNCHANGED`; `P01=OPEN`; `P02=NOT_OPENED`.

Next: `TTM_P01_L1_V3V4_S1_WINDOWS_INTEGRATED_HOST_RUNNER_STATIC_QA_AND_SINGLE_COMBINED_PERMIT_ADJUDICATION`.

Preserve P00, ten F0, original HEAD, append-only scientific lineage, all historical PASS/FAIL artifacts, markers and the P00–P12 roadmap.
