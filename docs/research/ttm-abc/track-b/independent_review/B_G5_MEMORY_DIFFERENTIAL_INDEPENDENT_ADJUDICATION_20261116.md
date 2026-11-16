# TTM Track B — B-G5 independent memory-differential adjudication · 2026-11-16

**Operation:** `TTM_B_G5_MEMORY_NEGATIVE_DIFFERENTIAL_INDEPENDENT_ADJUDICATION_SOURCE_AND_RECEIPT_ONLY`  
**Review mode:** supplied native Windows receipt/log readback + exact local V3 and differential OnePack source inspection + public Win32 documentation. **No Windows execution by this reviewer, no new child process, no science.**  
**B exact code SHA:** `43896bcd034c82e8433bc6a2b53eefbd936616fb` · [PR #34](https://github.com/minhtri22/TokenToModel-Lab/pull/34) remains Draft/Open/unmerged as independently checked.  
**V3 owner native receipt SHA-256 (historical, not supplied as full file in this turn):** `063bb5770c92881ab8fd0ae485f007026594495109c0c0b0359a0ba686c22188`. Reported `PHASES_RUN=16`; the 16th phase `job_memory_negative` raised `MemoryError` and `PeakJobCommitBytes=429174784 > 268435456`. Do not rewrite or retroactively PASS that immutable V3 receipt.

## Distinct receipt custody

The user supplied the following four files and the accompanying SHA256SUMS manifest. Reviewer hashed **actual uploaded bytes** (not filenames or prose), parsed the exact JSON, checked the listed hashes, and inspected the stderr/stdout texts:

| File | SHA-256 | Verified |
|---|---|---|
| `B_G5_MEMORY_DIAG_RECEIPT.json` | `2503cc19067b1861a8495aa7cbed59e17a4f5dcbddbe54224a7c1cb1ab6a62d2` | HASH_MATCH |
| `over256_alloc400.stderr.log` | `652f0a2538814147882e7efbe858709cebeca9b7c983294a6c873d4da8cde423` | HASH_MATCH; Python `MemoryError` |
| `relaxed512_alloc400.stdout.log` | `1a36d4c6a4914e505ef711a62acc9f57be30569426a4bf6b2d03b8437c367afb` | HASH_MATCH; `419430400` |
| `under256_alloc64.stdout.log` | `752764b909a6a2cfad60b5ee7c928f5447b61b11c3c862d20833aeb2ca138a21` | HASH_MATCH; `67108864` |

Receipt reports PowerShell 5.1.26100.9818 and an executable under Python312. Differential script tested Python major/minor 3.12 in its child code; independently checked script raw SHA-256 `4c1c4e6d6c8f4c04266186deb5a22e784305e7edcc8f5f4faf542ab370622353`. Three probe rows report `job_guard_applied=true`, `timed_out=false`, configured job cap readback correct and `NO_SCIENCE=TRUE`.

| Probe | Job cap | Requested | Result | Peak job commit | Peak working set |
|---|---:|---:|---|---:|---:|
| `under256_alloc64` | 256 MiB | 64 MiB | exit 0, printed 67108864 | 70.855 MiB | 73.75 MiB |
| `over256_alloc400` | 256 MiB | 400 MiB | exit 1, `MemoryError`, no success print | **407.523 MiB** | **9.789 MiB** |
| `relaxed512_alloc400` | 512 MiB | 400 MiB | exit 0, printed 419430400 | 407.457 MiB | 409.707 MiB |

The failed 256-MiB negative case's peak is 151.523 MiB greater than the configured limit. It must not be silently omitted, normalized away or treated as confirmed successful commit. Contrasting outcomes on the *same machine* with different enforced limits, under the same C# JobGate helper, are **strong scoped evidence of hard allocation rejection**. They are not standalone proof that `PeakJobMemoryUsed` is a literal successfully committed high-water mark after a failed charge.

## Win32 semantics and adjudication

- The source helper applies `JOB_OBJECT_LIMIT_JOB_MEMORY`, `JOB_OBJECT_LIMIT_ACTIVE_PROCESS`, `JOB_OBJECT_LIMIT_KILL_ON_JOB_CLOSE` **before resuming the suspended child**, checks `SetInformationJobObject`, `AssignProcessToJobObject`, then reads flags/cap back via `QueryInformationJobObject`. No source change or fresh Windows execution was done during this review.
- Microsoft's `JOBOBJECT_BASIC_LIMIT_INFORMATION` documentation states an attempted commit above the job-wide limit **fails**: https://learn.microsoft.com/en-us/windows/win32/api/winnt/ns-winnt-jobobject_basic_limit_information.
- Microsoft's `JOBOBJECT_EXTENDED_LIMIT_INFORMATION` documentation describes `PeakJobMemoryUsed` as a peak counter, but does **not** state how unsuccessful commit attempts affect it: https://learn.microsoft.com/en-us/windows/win32/api/winnt/ns-winnt-jobobject_extended_limit_information.
- Hence an inference that over-limit `PeakJobMemoryUsed` proves *successful* over-limit commit is **not established**; conversely, it is not sound to claim the peak definitely counts failed attempted charges without kernel documentation or a further accounting oracle.
- V3's universal acceptance check `PeakJobCommitBytes <= MemoryBytes` is overly strong for a deliberately rejected 400-MiB negative probe; changing this check **prospectively, only for the negative test**, is a proposed QA-criterion clarification, not an edited historical receipt. Keep the hard 256-MiB configured limit, fail-closed flags/cap readback, constrained CPU training phases, watchdog and kill-on-close.

**Scoped adjudication:**
- `B_G5_DIFF_PROBES = PASS_3_OF_3`
- `B_G5_HARD_ALLOCATION_REJECTION = PASS_SCOPED_BY_NATIVE_DIFFERENTIAL`
- `B_G5_PEAK_COUNTER_INTERPRETATION = HOLD_UNRESOLVED`
- `B_G5_FORMAL_GATE = HOLD_PENDING_INTEGRATED_RESOURCE_REVIEW` until exact prior V3 full receipt, per-phase status and acceptance contract are independently read together, or the owner explicitly approves a prospective amendment removing the invalid peak invariant *for intentionally failing negative probes only*.
- `B_G6 = HOLD_DISTINCT_FULL_EXACT_HEAD_QA_NOT_ADJUDICATED`: the memory diagnostic is not a substitute for independent readback of all source/test and full V3 run.
- `B_M3=HOLD`; `BC_INTERFACE_WORK_ALLOWED`; `NO_SCIENCE`; `NO_MERGE`.

## One follow-up, no rerun

**`TTM_B_G5_G6_V3_EXISTING_FULL_RECEIPT_AND_PROSPECTIVE_NEGATIVE_GATE_ADJUDICATION_SINGLE_GATE`**

Read the **existing** `PM_B_NATIVE_QA_RECEIPT.json` from `D:\WORK\RESEARCH\TokenToModel-Lab\_evidence\track-b\TTM_B_NATIVE_20261116T160910Z_3b3c0c41` (SHA `063bb5770c92881ab8fd0ae485f007026594495109c0c0b0359a0ba686c22188`) and its hash manifest. Verify all earlier phase statuses and source pins, then adjudicate whether a *prospective, negative-only* `MemoryError`+readback+relaxed-cap controls criterion is sufficient for B-G5 and complete the distinct B-G6 review. No repeat 16-phase run and no fresh memory diagnostic.

**Provenance limitation:** the report and derived receipt below are authored by a distinct ChatGPT PM/reviewer, uploaded via the connected owner's GitHub account, not an independently authenticated human auditor.
