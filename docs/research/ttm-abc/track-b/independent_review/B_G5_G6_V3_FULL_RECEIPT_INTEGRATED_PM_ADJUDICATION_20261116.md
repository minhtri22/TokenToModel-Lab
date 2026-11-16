# Track B M3 — integrated native Windows V3 / differential independent PM adjudication

**Operation:** `TTM_B_G5_G6_V3_EXISTING_FULL_RECEIPT_AND_PROSPECTIVE_NEGATIVE_GATE_ADJUDICATION_SINGLE_GATE`  
**Date:** 2026-11-16 · **Scope:** engineering-only, exact-source and existing native evidence; no fresh model execution, no science, no merge.  
**Original B HEAD:** `43896bcd034c82e8433bc6a2b53eefbd936616fb` · [Draft PR #34](https://github.com/minhtri22/TokenToModel-Lab/pull/34), still open/unmerged at original review.  
**Original B-G5 admission:** `docs/coordination/ttm-abc/TTM_TRACK_B_GPT_CORE_AGENT_HANDOFF_20261116.md`: *“One-command/one-run synthetic CPU E2E with measured resource caps”*. B-G6: *“Distinct exact-HEAD independent QA, evidence GitHub readback, no science”*. It **did not impose** `PeakJobMemoryUsed<=cap` as an acceptance condition for an intentionally rejected, over-limit allocation attempt.

## Immutable evidence and independent byte checks

- **Native V3 receipt file directly uploaded and hashed:** `PM_B_NATIVE_QA_RECEIPT.json` SHA256 **`063bb5770c92881ab8fd0ae485f007026594495109c0c0b0359a0ba686c22188`**; equals the provided native SHA256SUMS entry.
- **Native hash manifest directly uploaded:** `SHA256SUMS(3).txt` SHA256 `964a86e5a404b03731517452f0c5d30f64c3ab8e1a0f7426a7aa121897702257`; **32/32 stdout/stderr hash entries** match the matching phase SHA-256 fields in the uploaded receipt, plus **1/1 receipt hash entry** matches actual uploaded bytes. Only the V3 memory negative stderr raw bytes were also uploaded independently and checked; other historical raw logs were not newly supplied in this review. Manifest/receipt cross-consistency is not the same as rehashing all 32 raw log files.
- The V3 PowerShell script was independently read as exact local bytes: SHA256 `33093ba616f785981eb3854170f4a5e666a35f4e86b780684ae8e3cd7c19233e`. Its `Invoke-Guarded` tests `PeakJobCommitBytes<=MemoryBytes` **unconditionally**, including the deliberately failing 400MiB/256MiB negative phase.
- The independently supplied three-probe receipt `B_G5_MEMORY_DIAG_RECEIPT.json` SHA256 **`2503cc19067b1861a8495aa7cbed59e17a4f5dcbddbe54224a7c1cb1ab6a62d2`** and four supplied log hashes had already been verified on the preceding review. Native V3 and diagnostic scripts are separate files and separate executions; no rerun has occurred in this adjudication.
- The reviewed four B source/config SHA256 pins match the ones established on GitHub for exact B source: scaffold `5b6610428ac49c4c8d27509de3b27a8519d3865a1c3bbbd8e48051b8080c7fe0`, CLI `b5f9d4c5961c9dac0cc7cee733f2a94b1f08c25d2f31cc2b5e2b525cfadd083b`, author tests `c6390714f3ad822a78a633feae71dd0dd9138c3ba57456db8b3c785af081fc97`, config `73553bb8fa0dd0884cecbc3a5a2c32e2697abb0ad79cb5b4d4934a172ab135e5`.
- The seven reviewer-authored native negative tests' deterministic JSON stdout was **independently reconstructed** from V3 test source and expected Windows CRLF: SHA256 `56b2686a3912166b67fa6cf54507fe83b358c0cf0b3027d4b4818bd627b4b2c0`, matching receipt/manifest. Evidence is of the seven checks' expected printed success receipt plus native exit 0, rather than an independently run new suite.
- Earlier GitHub Actions [#43893656571](https://github.com/minhtri22/TokenToModel-Lab/actions/runs/43893656571) raw Linux/Windows logs were independently reviewed: 21/21 author tests per lane, synthetic prepare/train3/resume5/evaluate/sample. Tested source `ff2dc7c59258079a5f3fc5f1bcf4e60c3cfc279e`; the only difference from B exact branch HEAD is the added CI readback JSON file.

## Existing native V3 phase accounting — no re-execution

**Six Git-source phases** `git_isolated_init`, `fetch_sha`, `fetchhead_sha`, `commit_object`, `root_tree`, `archive`: 6/6 exit zero. An isolated bare repo fetched exact SHA and archived the tree, avoiding V1/V2 local-object issues.  
**Eight ordinary guarded Python phases:** `python312_preflight`, `author_21_tests`, `prepare`, `train_0_to_3`, `train_resume_3_to_8`, `evaluate`, `sample`, `independent_negative_7`: **8/8 receipt PASS**, exit0, no timeout, JobObjectApplied=true, cap=4GiB. Maximum recorded peak job commit = **430768128 bytes (~410.81MiB)** in `author_21_tests`, below 4GiB. Training phases max ~348.84MiB and ~348.23MiB. All eight have bounded elapsed time recorded.  
**Watchdog negative:** `watchdog_timeout_negative`: receipt PASS, exit 1460, timed_out=true as intended, JobObjectApplied=true, cap=256MiB, peak job commit=8953856 bytes.  
**Memory negative:** `job_memory_negative`: original V3 receipt **FAIL** and immutable `HOLD_NATIVE_QA`; exit1 and `MemoryError`, no timeout, JobObjectApplied=true, cap=268435456 bytes, reported `PeakJobMemoryUsed=429174784` bytes (~409.29MiB), peak working set 12877824 bytes. V3 `PeakJobCommitBytes>MemoryBytes` condition caused the failure. The historical FAIL must remain FAIL in its native receipt.

**Existing independent differential controls:** under 256MiB cap request 64MiB -> success; under 256MiB cap request 400MiB -> `MemoryError`; under 512MiB cap request the same 400MiB -> success. Three/three expected controls, all Job Object attached and correct cap readback, no timeout. In the rejected 400MiB probe, peak commit is 427319296 bytes (>256MiB) but peak working set only 10264576 bytes, whereas the successful 512MiB control had working set 429608960 bytes. This strongly supports *failed allocation under hard limit*, not confirmed successful physical use above limit. The exact kernel accounting behavior of `PeakJobMemoryUsed` after denied commit remains **UNRESOLVED**; do not claim documentation proves failed requested bytes count toward peak.

## Ruling: distinguish frozen V3 execution status from original gate acceptance

**The original native V3 run remains `HOLD_NATIVE_QA`** in all historical records. No mutation, selective deletion or reinterpretation of `pass:false`.

The unconditional check `PeakJobMemoryUsed<=256MiB` on an intentionally denied `400MiB` *negative* allocation was a stronger incidental QA-harness check than the original B-G5 admission. It is not valid as conclusive evidence of a successful cap breach when a controlled same-host differential demonstrates the allocation fails at 256MiB and succeeds at 512MiB. Therefore the PM/independent reviewer **adjudicates** the original substantive B-G5 engineering obligation, without asserting V3 execution PASS or discovering the kernel counter mechanism. The acceptance clarification **applies only to the deliberately over-cap memory-negative test**. For all normal positive training/eval phases the hard memory cap, actual measured peak (below cap), no uncontrolled children, watchdog and Job Object readback requirements are unchanged.

| Gate | Integrated scoped adjudication |
|---|---|
| B-G0 | `PASS_SOURCE_INVENTORY_SCOPED` |
| B-G1 | `PASS_SYNTHETIC_CONTRACT_AUTHOR_CI_NATIVE_SCOPED` |
| B-G2 | `PASS_SYNTHETIC_P02_P03_TRAINER_AUTHOR_CI_NATIVE_SCOPED` |
| B-G3 | `PASS_SYNTHETIC_CHECKPOINT_RESUME_AUTHOR_CI_NATIVE_SCOPED`; real T4/P04 weights NOT_LOADED |
| B-G4 | `PASS_SYNTHETIC_METRICS_AUTHOR_CI_NATIVE_SCOPED`; semantic metrics NOT_VALIDATED |
| **B-G5** | **`PASS_ADJUDICATED_HARD_RESOURCE_ENGINEERING_SCOPED`** — positive E2E 4GiB capped, watchdog and 3/3 differential rejection; original V3 negative remains recorded FAIL; peak-counter accounting advisory open |
| **B-G6** | **`PASS_DISTINCT_AI_EXACT_HEAD_SOURCE_AND_NATIVE_EVIDENCE_SCOPED`** — exact source pins, independently authored 7 negatives, source/log manifest review and GitHub readback; not a separately authenticated human reviewer or independent rerun of all 21 author tests |
| **M3** | **`B_M3_PASS_ENGINEERING_BASELINE_SCOPED_BY_PM_ADJUDICATION`**, limited to synthetic B0/B1 engineering and published interfaces; no semantic/science claim |

**Residual advisory:** `B-G5-FOLLOWUP_PEAK_COUNTER_INTERPRETATION=OPEN_NON_BLOCKING_FOR_SYNTHETIC_ENGINEERING`. If a later scientific/production phase requires strict memory accounting or proof of actual committed bytes for rejected allocations, define a new, frozen resource/accounting contract before that phase; never use this adjudication to waive the production hard cap, scientific peak measurement, source rights, model custody or owner permissions.

**Independence/visibility limitations:** the 21 author test raw Windows stderr log was *not* uploaded in this final two-file packet; its hash was read from receipt and earlier independent GitHub CI logs did verify those author tests. The 7 adversarial tests are reviewer-authored but executed in the owner's V3 launcher, not on an independently owned Windows host. The reviewer is a distinct ChatGPT PM assessment, not an authenticated human reviewer. No new training, GPU or scientific run; no merge. Track C contract and B–C SFT integration are separate gates and are **not** promoted by this B0/B1 ruling.

**Single next operation:** `TTM_PM_BC_SYNTHETIC_SFT_INTERFACE_DISTINCT_EXACT_HEAD_INTEGRATION_ADJUDICATION_SINGLE_GATE` — accept B/C integration evidence when supplied, verify branch and versioned tokenizer special-ID map/labels/mask/attention/reproducibility, adjudicate independently. Keep `main` and PR #34 Draft until separately approved for merge.
