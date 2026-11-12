# TTM Vector Memory — Top-k non-TEST CPU one-shot: final QA and owner GO (2026-11-12)

**Operation:** `TTM_VM_TOPK_FROZEN_READER_CPU_PROBE_RUNNER_ONE_SHOT_INTEGRATED_QA_AND_OWNER_GO`  
**Decision:** **`GO_SCOPED_CPU_PROBE_ONCE_WITH_FAIL_CLOSED_PREEXEC`**  
**Source freeze:** Git commit `9e46bb4662fcffc66f85ae7d4d479a017f69b293` on independent branch `research/ttm-vector-memory-architecture-20261111`. This commit includes the frozen runner, its independent QA source, and public QA receipt; later documentation commits do not change the science source.

## 1. Source and custody pins

| Asset | Immutable pin |
|---|---|
| Runner `frozen_topk_probe_one_shot.py` | Git blob `d6e2cb2b087342234f8f722de70b6de429c550c3`, SHA256 `af47c3a73dccec1bd60e1c3433f7875c2c505046a872093b96f8ca4889fde935` |
| Independent scorer QA | Git blob `11d98c4d8528f0d1312652242362cc5e867e327f`, SHA256 `de4e18fc1ada98f6e789fad15374fec7f2ba73f4722bb5c0c552e8be5cf44a88` |
| Public QA receipt 66/66 | Git blob `76a976605ff1adddca4d83d6d8700469cffae7e9`, SHA256 `935d544101cbebaf041dca90af35a257a561128444c1cf10ff1d2290ab0aa01e` |
| Reader private L0020 step128 | SHA256 `c458de3afae87b3c381274b8edd698187df63ceac4dbbc0e6d8bd44b85c1632f`, owner byte-hash receipt, `8/8` state tensors, source pins verified |
| Original GPT P02 step1280 | SHA256 `ee723407b2c25a18be20e26387a3dd8e4a18e2942d469279b6f0748ff86af0dc` |
| T1 real manifest | SHA256 `cba18e60cee3d08a353ee6d4a451017289e45af7b4b1179c87171b9b78d7dfdc` |
| New non-TEST PROBE 128 | SHA256 `88c558a8f1844ee1e55bff64f30c2b801c8bf3e54ef0cbc537f9fd81e51e9c11` |

No binary Reader, trained GPT, T1 private manifest, full per-story dataset, or TEST key is published to GitHub.

## 2. Independent technical QA (NOT scientific results)

The independent source/synthetic-scorer checker completed **66/66 PASS** on CPU, using a mock ASCII tokenizer and random backbone/Reader. The actual committed runner Git blob is byte-identical to the locally tested source.

Checks included:
- `encode_target` and teacher-forced **answer-only mean token NLL** against a separate `log_softmax` reference;
- Recall@1/@3 as separate hit indicators, 32-record bank and Top-1/Top-3 masks;
- six fixed arms `A/O1/B1/C1/B3/C3`, literal Oracle as upper bound, no answer/target key in Top-k API;
- matched correct/wrong ranks, mask and key tensors, exact bypass, gradient-free model/Reader;
- deterministic paired bootstrap 1,000 draws, pinned seeds 20261114/20261115, independent percentile cross-check, NaN and short-vector rejection;
- immutable SHA/source pins and a negative subprocess test denying execution when `--execute-once` is absent;
- one-shot marker before PROBE scoring, no overwrite, no retry, per-story QA private output, frozen model and Reader weight comparisons.

QA outputs do **not** show real trained Reader performance, actual Recall@k, or any DEV/TEST result; do not report QA 66/66 as a science PASS.

## 3. One scoped release

**RunID:** `TTM_VM_TOPK_NONTEST_FROZEN_READER_PROBE_ONCE_V1`. **Exactly 128 new PROBE cases**, bank=32, Reader weights frozen at the end of L0020, original GPT frozen FP32 CPU, 2 threads, no optimizer and no GPU. The same Reader is evaluated in six arms A/O1/B1/C1/B3/C3 in one run.

Frozen pass screen:
- `R_FULL_COSINE Recall@3 >= 0.95`;
- paired mean `NLL(A) - NLL(B3) >= 0.05`;
- paired mean `NLL(C3) - NLL(B3) >= 0.05`;
- both reported percentile bootstrap 95% lower endpoints `>0` (1,000 draws, seeds 20261114 and 20261115).
- Oracle-1 controls domain shift; if Oracle-1 doesn't improve against no-memory by 0.05, classify as `HOLD_ORACLE_READER_PROBE_DOMAIN_SHIFT` without reallocating budget or rerunning.

These are **only non-TEST exploratory screening criteria**. `GO_CANDIDATE_NONTEST_SCOPED` is never permission to open TEST.

## 4. Integrated owner PowerShell packet

`tools/research/vector-memory/Invoke-TTM-VM-TopK-FrozenReader-CPU-OneShot-PS51.ps1` (Git blob `356eee62e229a776e8c537aa33de67d1aba73249`):

- No arguments: verify origin, clean exact worktree, checkout frozen source commit, Git blobs, native SHA256 of the Reader/GPT/T1 manifest, Python 3.12 dependencies, then run or verify independent owner QA 66/66. **Preflight only**.
- `-ExecuteOnce`: all the above gates, then exactly one source-pinned CPU evaluation on the fresh PROBE.
- Do not rerun or delete the one-shot output directory if partial/failed. No TESТ, old DEV, GPU, retraining, or change to main.

Owner preflight on Windows is still to be read back at execution time; the release is fail-closed and may result in `HOLD` if the machine/source has drifted.

## 5. Governance outcome

**Source/QA and Reader custody:** `PASS`. **Owner scientific release:** `GO_SCOPED_CPU_PROBE_ONCE_WITH_FAIL_CLOSED_PREEXEC`. **Science:** `NOT_EXECUTED`. **TEST:** `SEALED`. **GPU:** `NO`. **Main:** unchanged. **Lineage:** L0020 unchanged; no scientific entry for this source/QA action.

**Next operation:** `TTM_VM_TOPK_NONTEST_CPU_ONESHOT_RESULT_INDEPENDENT_RECOMPUTATION_AND_SCIENTIFIC_ADJUDICATION`. After execution read only results, independently recompute Recall/NLL/bootstrap from saved private per-story receipt, record PASS/FAIL including negative findings, append lineage only for genuine science, and never rerun.
