# TTM — External-Facts CPU Pilot Owner One-Shot Execution Decision

**Operation:** `TTM_VM_EXTERNAL_FACTS_CPU_PILOT_OWNER_ONE_SHOT_EXECUTION_DECISION`  
**Date:** 2026-11-11  
**Branch:** `research/ttm-vector-memory-architecture-20261111` — independent exploratory research, `main` and P00–P12 unchanged.  
**DECISION NOW:** **`HOLD_PINNED_EXECUTION_WORKTREE_STALE`**. No 128-step CPU science execution authorized at this instant.

## What was independently verified

- Preregistration/science code frozen at Git commit `c41b6c8bc01a4c367bf619a6df6e05e5e2fb9d47`. Frozen pilot runner Git blob `13701b8768c463d845762c690768abae2040eba2`. P02 blob `9762343e06cf800b50574c2871ae1ed58537fb18`. Oracle Reader blob `7ce728b2874284b87933237c890e54ce3d9fd651`.
- Prior technical preexecution receipt `PASS_29/29` and independent source QA `PASS_34/34` reviewed from the research branch; these were synthetic/source-only and do not constitute science.
- The owner's Windows T1 QA receipt was **read directly** from `D:\WORK\RESEARCH\TokenToModel-Lab\_evidence\vector-memory\TTM_VM_REAL_T1_BPE_COMPAT_QA_20261111.json`: `PASS_REAL_T1_TOKENIZER`, 320 TRAIN/DEV cases, max question 43 tokens, answer 4, joint 47, prefix mismatches 0, `NOT_READ_OR_DECRYPTED` TEST status. Its read-file text when reconstructed with Windows CRLF and final CRLF computes SHA-256 **`bc688ca5bcc4084a19d3e95b0f7d555c283d8b1b1319ff255c5baf9e66c7b34b`**, matching the owner's SHA commitment. Exact raw-byte disk hash must be checked by the final owner preflight.
- **Blocking mismatch:** Windows detached worktree `D:\WORK\RESEARCH\TokenToModel-Lab\worktrees\ttm-vm-external-20261111` has HEAD **`0087e7f1d35b8fe4f855231fd1aa398d830510ce`**. This is not frozen science commit `c41b6c8bc01a4c367bf619a6df6e05e5e2fb9d47`. The old worktree lacks `cpu_pilot_one_shot.py` and `oracle_reader_source_only.py`. This worktree must **NOT** execute science.
- GitHub `main` at review was `5d52e32f20021e36f08f284ef9864d3ba36dbead`; it is not altered.

## Single integrated owner recovery and GO condition

Use `tools/research/vector-memory/Invoke-TTM-VM-Owner-OneShot-Decision-PS51.ps1` from **this research branch** as a standalone PowerShell 5.1 script saved under the TTM project root.

- With no switch: read-only; stale checkout gives `HOLD` (exit 2).
- With `-SyncPinnedWorktree`: refuse dirty worktree, verify GitHub origin, fetch only the research ref and check out the **exact frozen science commit** detached in this one worktree; no checkout or writes to local `main`.
- Then verify actual source Git blobs (including runner), checkpoint SHA, private T1 manifest SHA, original receipt raw SHA, owner receipt contents and required Python 3.12 dependencies.
- Refuse `GO` if the one-shot evidence output directory already exists (including failed/partial prior execution). **No overwrite, no science retry, no TEST access.**
- Only the successful terminal output `GO_OWNER_PREEXEC_ALL_PINS_PASS=TRUE` is a **GO recommendation for the owner to permit a separately invoked one-shot CPU run**. The preflight never calls the trainer, does not score DEV, and does not unlock TEST.

## Frozen experiment; unchanged

One run ID `TTM_VM_EXTERNAL_FACTS_CPU_ORACLE_TRAIN_DEV_20261111_V1`; 256 TRAIN cases; 64 DEV cases; 128 optimizer steps (8 epochs × 16 batches); seed 20261111; CPU FP32; only the Reader's value/output/gate params learn (110,689); original 4M backbone and tokenizer frozen; exactly one DEV pass at step 128. Controls A = no-memory same Reader bypass; B = correct memory; C = wrong memory. Oracle selector uses question key, never label/gold. Primary metric = mean over stories of answer-only mean token NLL, teacher forcing. An exploratory DEV screen requires both `A−B` and `C−B` >= 0.05 nats/story and both paired-bootstrap (1000 draws, pinned seeds) lower bounds > 0. DEV screen success is **not** permission to open TEST; RETRIEVED_TOPK and separate TEST authority remain deferred.

No hypothesis, seed, learning rate, epoch count, dataset, scorer or threshold was changed in this owner decision.

## Governance

- **Current status:** `HOLD_WORKTREE_STALE` / `OWNER_CPU_PERMIT_NOT_GRANTED_YET`.
- **One integrated release condition:** recover exact pinned science checkout; verify raw receipt SHA + input/source pins; ensure one-shot not consumed; then owner may grant single 128-step CPU TRAIN + one DEV. No incremental micro-permits or repeated science.
- `TRAIN_DEV_SCIENCE=NOT_EXECUTED`, `TEST=SEALED`, `GPU=NO`, `MAIN=UNCHANGED`.
- `lineage.md` unchanged: technical receipt, decision and QA are NOT new scientific PASS/FAIL entries.

**Next:** `TTM_VM_CPU_OWNER_PINNED_WORKTREE_RECONCILE_AND_SINGLE_GO_READBACK` — run the one integrated PowerShell preflight, record terminal GO/HOLD, and only then decide execution.