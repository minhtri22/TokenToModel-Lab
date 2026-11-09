# G1 Windows target QA — dispatch HOLD, owner-run packet

**Date:** 2026-11-10 · **Science:** `G1_SCIENCE_LOCK=HOLD`, `OWNER_SCIENCE_PERMIT=NOT_ISSUED`.

## Verified immutable materials

- Original trusted runtime implementation: `cdaf13b4ac131b0117aadb836fd42810c63978db`.
- Frozen v1c research: `d5d0c5346a595557a76349f900d09be50bce289c`.
- Distinct Codex HOLD report: `d478282e16a4728f064892564b949e671e13cdd2`.
- Original integrated ZIP SHA256: `5584dfb61d293f2946b66ef9f5e4bb4a0703c415ced0946ff2bacc302e95013c`. All original inner `SHA256SUMS.txt` entries verified in the assistant container; ZIP was **not run on Windows**.
- New **local-download owner-run QA outer ZIP**: `TTM_SIX_G1_WINDOWS_QA_OWNER_PACKET_20261110.zip`, SHA256 `66d3f8599bec733b6aff1b05e5e13fbc7c1c984b3a63ab39a7c74c78aa926d83`. Copy directly into `D:\WORK\RESEARCH\TokenToModel-Lab\_tmp` before unpacking.
- Exact PowerShell 5.1 runner SHA256: `2e9ac2bd72d7a20956e0f8da8ccc13bb8183fa58fa53e0c20aeecc48f292c4bc`. Strict project-local source/hashes, Python 3.12, sanitized local receipt, private inventory log.
- QA-only patched Win32 Job Object probe SHA256: `a033e881d42e59c18aa9af96390fe808eb2b9858ee2653ae88c5b238256393e5`. **Not a production watchdog.** It adds direct `TerminateProcess` fallback if a created suspended child could not be attached/resumed. The frozen original watchdog in the 20261109 ZIP is not executed by the owner-run wrapper.
- Owner instructions and Codex handoff are also in the 20261110 outer ZIP.

## Actual target connection outcome — NOT a Windows QA PASS

`machine-1` / `DESKTOP-4PSD0G2` observed ONLINE. A new RemoteDesktop project scoped to `D:\WORK\RESEARCH\TokenToModel-Lab\_tmp` was accepted: `prj_1544c3e94ebd4b2947bc84e9`. Task `tsk_a219c435c867be41ddc5c4fc` was created, then harmless PowerShell SID/PWD preflight was **rejected before execution**:

```text
scientific job admission held until exact command evidence qualifies
```

Final task status: `RECOVERABLE`, no active owner lease. No evidence of a Windows command having run. Do not bypass RemoteMCP quarantine or treat connection/registration as DACL, Job Object, or witness QA.

## Owner-run scope and required evidence

Unpack verified outer ZIP **only under the project's `_tmp`**, run the SHA-pinned PS5.1 runner in a non-elevated session. It creates a new `_tmp\G1_TRUST_BOUNDARY_WINDOWS_QA_*` folder and logs:
- real Windows SID/DACL **read-only inventory**, no ACL changes;
- synthetic 45-case regression (Windows rerun);
- harmless Windows Job Object forced child kill and normal exit with safety patch;
- current-user synthetic sentinel ACL (not a real worker SID);
- receipt SHA256 and Git branch/HEAD unchanged.

**Not provable by this owner-run packet alone:** access denied for a distinct *provisioned* Windows worker SID, true separate owner/controller TEST authority, independent monotonic witness in a separate rollback domain, trusted data writer/transaction, actual GPU/T4 watchdog and scientific methods admission. Mark these `NOT_TESTED`/HOLD, even if local CPU tests pass.

Raw inventory logs may contain local account/SID information: do not push to public GitHub unredacted. Codex must independently inspect source pins, local receipt and non-sensitive logs, test with genuinely distinct Windows principals when authorized, and issue exactly one `PASS_DISTINCT_REVIEWER / HOLD / FAIL`.

**Current gates:** `WINDOWS_PRODUCTION_QA=NOT_EXECUTED` · `DISTINCT_ADJUDICATION=PENDING` · `G1_SCIENCE_LOCK=HOLD`. No G1 private TEST, Qwen weights, training or owner permit touched.
