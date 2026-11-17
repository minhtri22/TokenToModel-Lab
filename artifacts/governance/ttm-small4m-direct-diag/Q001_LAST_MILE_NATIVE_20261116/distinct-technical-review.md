# Q001 last-mile independent technical decision

I1 is `HOLD_I1` for source commit `6dc04c0545b28d4a0cad21ad8be8b70461c57790`. The distinct technical reviewer inspected the exact source, the native Windows receipts, and the frozen synthetic fixture. I2 has zero optimizer steps and no consumed one-shot claim.

## Restricted decoder control

The runner builds the candidate list with gold at index zero, followed by `NO_ANSWER` and low-ID value distractors. Its restricted argmax resolves equal logits by choosing the first item. Constant logits therefore score 80/80 restricted. A second negative control gives every case the same vocabulary logits, ranking tokens by numeric ID and placing `NO_ANSWER` last. Both full-vocabulary and restricted argmax use that single score vector.

| Group | N | Blind restricted top-1 | Blind full-vocabulary top-1 |
| --- | ---: | ---: | ---: |
| TRAIN | 24 | 14 | 0 |
| HELDOUT_RECOMBINED | 16 | 15 | 0 |
| HELDOUT_NOVEL_IDS | 16 | 16 | 0 |
| PAIRED_COUNTERFACTUAL | 16 | 16 | 0 |
| HELDOUT_ABSENT | 8 | 0 | 0 |

The blind control reaches Q1's restricted ≥12/16 and full-vocabulary ≤8/16 signpost on three groups. The score gap can arise entirely from the candidate construction. This blocks the registered failure-localization decision. The reviewer proposed candidate generation from the context, independent of the gold label, with gold-independent tie resolution and a repeat of the negative controls before I2.

## Frozen split and custody

The fixture SHA-256 is `5f1234f583ccf719ca9f0e68de4f47d8b653af777271b8115c5f02307f764e5a`. There are 80 distinct nine-token contexts and 80/80 oracle matches. The source-review handoff interprets target exclusion as withholding the tenth-position label. In 64 bound cases the answer value occurs in its source binding, as required by the nine-token grammar. All 16 counterfactuals swap both parent values, and the novel-ID group has zero TRAIN key/value overlap. Six recombined cases reuse at least one TRAIN binding. One of those six reuses the queried binding. Zero repeat a full unordered two-binding TRAIN set. The 80 frozen case hashes and five group hashes are recorded in the native receipt.

The original Drive checkpoint and the Windows copy match the registered 45,074,891-byte SHA-256. Inspection verified step 1024, the P02 source blob, and 3,749,376 unique checkpoint parameter elements. The original T1 TRAIN-only BPE manifest matches its pinned SHA-256 and yields 2,047 legal IDs after excluding EOS 256. The upstream dataset license label is recorded separately from owner-declared internal use. The public evidence contains only custody summaries and hashes.

## Windows observations

The 11 owner-internal tests and five native Win32 tests passed on PowerShell 5.1 and Python 3.12.10. The scaled 96 MiB Job Object cap rejected a single 97 MiB allocation and a descendant's 52 MiB allocation while its parent held 52 MiB, both with WinError 1455. Native probes covered nesting, redirected stdio, timeout, nonzero exit, live descendants, and kill-on-last-close. The guarded child used the hard 12 GiB job-wide commit cap. PowerShell separately sampled process-tree working set. Both live entry points denied the missing GitHub verdict before opening dummy inputs. Positive I2 execution was outside this HOLD.

[Native receipt](native-receipt.json) · [Native transcript](native-tests.txt) · [Launcher transcript](native-ps51-launcher.txt) · [Win32 ABI readback](native-win32-abi.txt)
