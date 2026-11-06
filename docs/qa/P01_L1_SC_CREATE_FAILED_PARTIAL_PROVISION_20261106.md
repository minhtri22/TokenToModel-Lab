# TTM P01 L1 — SC_CREATE_FAILED partial provisioning, read-only adjudication (2026-11-06)

## Provenance and current evidence
- Immutable original HEAD: `f2e333df2f9ca24a8e483507c3cfc386ad9c76f0`.
- Source branch: `audit/p01-l1-native-security-critical-fix-20261106`.
- User-run native resume receipt: `L1_PROVISION_RESUME_20261106T151032982Z_d6e871db`.
- GitHub commit `e4d3cee3935759f351d9fdeb0c19f57b41b1f5da` contains `artifacts/qa/p01/L1_PROVISION_RESUME_20261106T151032982Z_d6e871db.json`.
- Receipt SHA-256 reported by Windows: `296b1a04432270d5a9734ffa1f200b02850a96f3d7b62e729afbeafba947c715`.
- The exact executable/source hashes passed; worker account created; staging, evidence, credential, ledger ACLs were configured. The script stopped at `SC_CREATE_FAILED`; no broker process started, no native pipe/worker permission qualification and no W01–W12.
- **Partial provisioning is real Windows state**. Neither rollback nor replay of the original `-Apply` is authorized.

## Technical root-cause hypothesis (not yet proven)
Existing source calls `sc.exe create` using combined argument strings of the form `'start= demand'` and `'obj= NT AUTHORITY\LocalService'`. Official Microsoft `sc.exe create` documentation specifies space-separated option name/value syntax (e.g., `start= demand`). PowerShell argument quoting can affect how these are delivered. The original receipt records only `SC_CREATE_FAILED`, not stdout, stderr or native exit code. Therefore this remains an **unconfirmed hypothesis**, not an adjudicated root cause. Do not run another create command merely to determine why it failed.

## Controlled next step
`qa/p01/windows/Inspect-TTM-P01-L1-ScCreateFailure-PS51.ps1` is **read-only against service/account/ACL/credential**:
- pins original HEAD/origin, executable SHA-256;
- reads the named worker account status, SCM service query/config, existing ACL metadata;
- records presence but **not content** of DPAPI credentials and ledger;
- does **not** create/configure/start/stop services, create users, change ACLs, invoke worker tests, or modify staging;
- creates a fresh receipt only inside TTM QA receipts, publishes it to the same GitHub branch and verifies SHA-256 readback.
- source Git blob `ab6638ff5b11e70aed3682efaadd9a1f19eb1e22`; publication commit `e04e0f6910541f9b6afbac18e1cf8e6568f4e446`.

Once state is observed, a separately reviewed *resume-after-partial-provision* script may fill exact missing service entry **without creating new account or credential**, then independently attest effective ACL and pipe DACL. No cleanup on failure.

## Gate
`WINDOWS_PARTIAL_PROVISION=CONFIRMED`
`SC_CREATE_ROOT_CAUSE=UNRESOLVED`
`WINDOWS_SERVICE=NOT_ATTESTED`
`NATIVE_ACL_AND_PIPE=NOT_EXECUTED`
`W01_W12=NOT_EXECUTED`
`GROUPED_L1_QA=NOT_AUTHORIZED`
`P01=OPEN`
`P02=NOT_OPENED`.

Preserve P00, all 10 F0 results, append-only scientific lineage rules and P00–P12 phases.
