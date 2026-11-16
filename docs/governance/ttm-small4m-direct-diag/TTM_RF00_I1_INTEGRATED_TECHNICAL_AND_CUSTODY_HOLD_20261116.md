# TTM RF-00 — Integrated native QA and custody · HOLD_I1 (16/11/2026)

**Mode:** implementation + GitHub-hosted Windows native NO-MODEL QA + independent byte hash of owner-private T4 checkpoint. **Not a new scientific experiment or independently adjudicated I1 release.**

**Exact implementation HEAD tested:** `9d47cd36bc89502faf2f0d46066c3a8b8aaaabd2` from branch `fix/ttm-sm4m-q001-rf00-winjob-hard-cap-20261116`, forked from exact PR #28 HEAD `8bded8612024c583faa92e79f5167f854703e43c`. Baseline main `f7a0a5874e8fd895c8ea8d17ceff393a4d4917a3`. [Native GitHub Actions final successful run](https://github.com/minhtri22/TokenToModel-Lab/actions/runs/43887142226) and [machine-readable evidence](../../../artifacts/governance/ttm-small4m-direct-diag/TTM_RF00_I1_INTEGRATED_TECHNICAL_AND_CUSTODY_HOLD_20261116.json).

## Confirmed technical progress (not model quality)

- Win32 Job Object wrapper enforces **JOB_MEMORY + PROCESS_MEMORY committed-memory caps**, attaches suspended process before resuming, queries peak usage and terminates child job on violations. The I2 PowerShell 5.1 launcher now requires exact SHA256-pinned guard; the existing sampled process-tree RSS, wall-time and output watchdog are still separate. No I2 was invoked.
- GitHub-hosted Windows Server 2022, Python 3.12.10: **8/8 native no-model tests PASS**, including real guarded CLI dummy-process invocation, timeout, orphan Python/conhost, and 128 MiB committed-memory cap rejecting a 512 MiB allocation; observed negative-test peak ~12.3 MiB. PS5.1 parser PASS, launcher source SHA pin checks 4/4 PASS, owner-scope source Git blob PASS after LF checkout correction, Win32 RSS probe nonzero. **Owner Windows 11 is NOT qualified by this off-host test**.
- Historical failed runs retained: PS parser, false orphan positives, high peak exceeding cap, LF/CRLF owner document mismatch. The final fix used both job-wide and per-process committed-memory caps; no historic failure is relabeled.
- **Original private T4 step-1024 checkpoint:** actual entire downloaded file 45,074,891 bytes independently hashed SHA256 `cb985751795c8328ad65acf7ca4c1033ce35182c1bfbdb8c38550de629cb271b` MATCH. `torch.load(weights_only=True,map_location='cpu')` metadata: schema `ttm.t4.science.checkpoint.v1`, step1024, P02 blob `9762343e06cf800b50574c2871ae1ed58537fb18`, config vocab2048/context256/4 layers/4 heads/dim256/LayerNorm; unique parameters 3,749,376. **No model forward/training or TEST/FINAL access, private weights not published**. Exact matching bytes on owner Windows not yet independently verified.
- Historical T4 tokenizer private manifest names expected BPE SHA256 `cba18e60cee3d08a353ee6d4a451017289e45af7b4b1179c87171b9b78d7dfdc` but original tokenizer source bytes were NOT found/read; no surrogate adopted.

## Unresolved integrated I1 blockers

| ID | Required proof |
|---|---|
| R01 | Original T4 tokenizer exact private bytes and full 2,048-ID special/reserved/non-special taxonomy; SHA independently verified |
| R02 | Real original 80 deterministic cases (24 TRAIN + 56 probe), with source-bound per-case/group SHA and distinct readback; mock source QA is not enough |
| R03 | Windows 11 DESKTOP-4PSD0G2 actual root and Python 3.12: owner-internal admission negatives, exact original tokenizer/checkpoint bytes and Job Object resource behavior. Managed RemoteDesktop general command transport unavailable; off-host GitHub Actions does not replace this check |
| R04 | Distinct reviewer not involved in changed final source must inspect exact SHA and evidence, issue one I1 PASS/HOLD verdict; **not three new administrative signers** |

**Verdict:** `HOLD_I1_CUSTODY_LOCAL_HOST_AND_DISTINCT_REVIEW_PENDING`. `I2=NOT_EXECUTED`; owner conditional GO preserved; PR #28 Draft/unmerged/untouched; main, lineage.md, T4 and sealed TEST/FINAL24 untouched. QA no-model is not new science.

**Bước thực hiện tiếp theo duy nhất (continue RF-00, no micro-permits):** one combined owner-host exact tokenizer/fixture byte-custody + Win11 QA + genuinely distinct I1 decision. Only if I1 passes, existing owner GO permits one frozen Q001 I2, not now.


---

## Addendum — Current PR #28 evidence supersedes snapshot-only custody gaps

**Readback later in this same task:** [PR #28](https://github.com/minhtri22/TokenToModel-Lab/pull/28) advanced independently from original reviewed head `8bded861...` to **`ebdc54575eed1ff60c402eecf60289f408bb38ca`**. The independently reviewed executable candidate is `6dc04c0545b28d4a0cad21ad8be8b70461c57790`. This report's earlier R01–R04 blocker ledger was an **older-source snapshot** and MUST NOT be presented as the active PR #28 blockers.

Source of truth: [new distinct Codex technical review](https://github.com/minhtri22/TokenToModel-Lab/blob/ebdc54575eed1ff60c402eecf60289f408bb38ca/artifacts/governance/ttm-small4m-direct-diag/Q001_LAST_MILE_NATIVE_20261116/distinct-technical-review.md), [I1 receipt](https://github.com/minhtri22/TokenToModel-Lab/blob/ebdc54575eed1ff60c402eecf60289f408bb38ca/artifacts/governance/ttm-small4m-direct-diag/Q001_LAST_MILE_I1_20261116.json).

**External native/custody evidence now recorded on PR #28:** Windows 11 `DESKTOP-4PSD0G2`, PowerShell 5.1, Python 3.12.10, 11 owner-internal tests + 5 Win32 native tests PASS, exact checkpoint and original T1 TRAIN-only BPE source byte pins matched; 80 real synthetic cases frozen and per-case/group SHA recorded. This independent review **does not cover RF-00 alternative branch code**, and our GitHub Actions PASS cannot be substituted for review of PR #28's newer runner.

**New decisive blocker (PR #28): `HOLD_I1_RESTRICTED_SCORER_LABEL_LEAKAGE`.** The candidate list has gold at index 0; with constant equal logits, tie-breaking returns that first gold item for **80/80 restricted items**. An additional context-blind, constant full-vocabulary score order reaches the predeclared restricted-vs-full signpost on HELDOUT_RECOMBINED (15/16 restricted vs 0/16 full), NOVEL_IDS (16/16 vs 0/16) and PAIRED_COUNTERFACTUAL (16/16 vs 0/16). This **falsifies use of that gap to diagnose actual model decoding capability**, independently of model training. The frozen fixture and historical data remain unchanged; no I2.

**Current authoritative verdict:** `HOLD_I1_RESTRICTED_SCORER_LABEL_LEAKAGE`; `I2=NOT_EXECUTED`. Do not request another owner GO, don't erase native receipts, don't run a new science round or merge PR #28/31. This alternative PR #31 remains an *unmerged supplementary engineering candidate*; overlapping implementation with PR #28 must be reconciled at exact HEAD before any code merge.

**Updated one next technical action:** repair the existing Q001 candidate/scorer so options are generated independently of the gold label, tie-breaking is independent of gold position, and context-blind/equal-logit negative controls no longer meet the decision signpost; have the **distinct reviewer** re-adjudicate I1 on exact new source. Keep original Q001 scientific contract, fixture and threshold immutable. Only after a real I1 PASS may existing conditional GO authorize one I2.
