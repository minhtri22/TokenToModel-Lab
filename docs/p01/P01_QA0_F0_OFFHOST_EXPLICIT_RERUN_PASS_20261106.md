# P01 QA0 F0 — explicit one-shot rerun PASS offhost (functional only)

**Operation:** `TTM_P01_QA0_F0_OFFHOST_RERUN_EXPLICIT_USER_APPROVAL_20261106`  
**Date:** 2026-11-06. **User authorization:** explicitly allowed a new attempt following the earlier inconclusive offhost one-shot.  
**Repo:** `https://github.com/minhtri22/TokenToModel-Lab`.  
**Implementation branch and exact source:** `implementation/p01-i0a-s-f0-static-20261106` @ `f2e333df2f9ca24a8e483507c3cfc386ad9c76f0`.  
**Test environment:** isolated ChatGPT Linux chroot, **not** Windows target and **not** a RemoteMCP routed job.

## One-shot lineage (technical, not science)

1. **Initial offhost attempt:** `exit=120`, `stdout/stderr=0 bytes`, `INCONCLUSIVE_NO_TEST_OUTPUT`. Non-P01 Python canary reproduced `exit=120` because supervisor used `prlimit --fsize=0` while redirecting output to a regular file. Retained earlier receipt and lock; no overwriting or retry without fresh owner approval.
2. **New owner-approved attempt:** source copies and rootfs matched **13/13 SHA-256 and Git blob SHA-1** records from the prior pinned GitHub manifest, each file byte-for-byte. Static Python syntax checked. Two independent **non-P01** prestart canaries demonstrated writable output and stdlib/readonly safety under `fsize=1048576` (1 MiB) before the single test command.
3. A **new one-shot lock** was written before dispatch. One command ran the pinned `qa.p01.qa0_f0_smoke_test` 10-case suite, with Python `-I -S -B`, in a chroot with read-only code/stdlib, UID/GID 65534, 512 MiB address-space limit, 12 CPU seconds, 25-second wall timeout, 1 MiB output-file ceiling, no authorized P00/P01 or corpus filesystem mount.
4. **Observed:** `PREPARED_TEST_COUNT=10`, `Ran 10 tests in 0.002s`, `OK`, `F0_TESTS_RUN=10`, `F0_FAILURES=0`, `F0_ERRORS=0`, process `exit=0`. Log length `1542 bytes`, SHA-256 `8e1319b98e60e0bec89cf57eca8e79b44bc6960fe88a0df3f13b91a4b530eb04`.
5. **No automatic third run**, no Git source changes or cleanup, no E0/scientific data, no GPT training and no `lineage.md` change.

## Cases observed as PASS

| ID | Check | Verdict |
|---|---|---|
| S01 | B0 byte-domain 0–255 and round-trip | PASS |
| S02 | F00–F11 raw SHA-256 and round-trip | PASS |
| S03 | Strict UTF-8 / Unicode preservation and rejects | PASS |
| S04 | Invalid token IDs rejected | PASS |
| S05 | M01 deterministic Byte BPE merges and independently pinned golden | PASS |
| S06 | Independent checker rejects damaged/trailing merges bytes | PASS |
| S07 | Malformed document inputs rejected before attribute access | PASS |
| S08 | F02/F03 canonical grouping, under-30 group split refused | PASS |
| S09 | Non-pinned F0 payload/marker admission rejected | PASS |
| S10 | Job guard, write broker, corpus and runtime receipt stubs fail-closed | PASS |

## Boundary and evidence

`F0_FUNCTIONAL_SMOKE=PASS_OFFHOST_10_OF_10`  
`F0_RERUN_ATTEMPTS=1_NEW_USER_AUTHORIZED_OPERATION`  
`F0_RERUN_LOG_SHA256=8e1319b98e60e0bec89cf57eca8e79b44bc6960fe88a0df3f13b91a4b530eb04`  
`F0_RERUN_LOCK_SHA256=d442b2ca690d3713df92135532cde7f9a1784ff8a8bd07cab98d84501b9c936c`  
`F0_RERUN_RECEIPT_SHA256=4d8067de638f4d7ffa47c281f7581f76541e196a4a534e57a8d969b21e0a3626`  
`QA0_WINDOWS_JOB_OBJECT_WRITE_BROKER_SECURITY=NOT_ESTABLISHED`  
`OFFHOST_NETWORK_ISOLATION_ATTESTATION=NOT_PROVEN`  
`QA0_F1_F2_TEST_CORPUS=FORBIDDEN`  
`E0_GPT_TRAINING=NOT_EXECUTED`  
`PR4_MERGE=NO`, `P00_P01_CLEANUP=NONE`.

**Interpretation:** PASS strictly for the 10 **functional** F0 tests. The guard/broker test asserts that unimplemented stubs reject operations. It is **not** a positive security test for real Windows Job Objects or file-write confinement. Source pinning and offhost readonly chroot do not establish network isolation via seccomp/network namespaces.

The full offhost technical receipt, one-shot lock, two non-P01 canary logs and full test log were generated and provided as conversation artifacts; no claim of a signed RemoteMCP node scientific receipt. This report is infrastructure/technical QA and is **not appended to scientific `lineage.md`**.

**Next:** `TTM_P01_QA0_WINDOWS_SECURITY_GUARD_IMPLEMENTATION_AND_INDEPENDENT_NEGATIVE_QA_DESIGN` — keep the Windows runtime-security decision separate; no rerun of the already successful offhost functional suite.
