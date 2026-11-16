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
