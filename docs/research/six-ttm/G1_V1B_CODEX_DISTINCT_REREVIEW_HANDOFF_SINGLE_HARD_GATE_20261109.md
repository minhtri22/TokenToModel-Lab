# HANDOFF — G1 v1b distinct Codex re-review & single integrated hard-gate closure

**Date:** 2026-11-09. **Task:** `TTM_SIX_XMODEL_G1_V1B_DISTINCT_CODEX_REREVIEW_AND_REMAINING_HARD_GATE_CLOSURE`  
**Current status:** `AUTHOR_QA=PASS_38_38`; `DISTINCT_REREVIEW=NOT_EXECUTED`; `SCIENCE_AUTHORIZATION=HOLD`.  
**Role:** You are a **truly separate Codex reviewer**, NOT the agent implementing this version. You may delegate independent static/math/security/OS tests to subagents. Never sign an author's test as independent evidence.

## 1. Exact origin and immutable source

Repository: `https://github.com/minhtri22/TokenToModel-Lab`  
Windows root: `D:\WORK\RESEARCH\TokenToModel-Lab`  
Branch: `research/ttm-six-cross-model-representation-transfer-20261109`  
Expected review HEAD at handoff: `d42ebb741d95338d64ae420dd86f3ab10ed591ad`  
Unrelated `main` expected: `b57b44e7287f842e81050c1faee337f636333dd0`.

Do not guess current branch from local HEAD: last Codex review found the local root on `main`, with untracked files. Confirm `git remote -v`, `git ls-remote`, the branch/commit SHA and `git ls-tree` independently. For a temporary checkout or QA, use **only** project-local `_tmp` or a worktree inside this same repo root. Do not switch/change the original `main`, delete unrelated untracked files, merge, push, run experiments or modify scientific artifacts.

| Exact source path under `scripts/research/six_ttm/` | Immutable Git blob |
|---|---|
| `g1_science_guard_v1b.py` | `d67b35cd8cba907904d0f23ccedd4b6b68d4850f` |
| `g1_science_core_v1b.py` | `94611c0449001230b2957487e152cd706f817516` |
| `g1_science_private_feature_extractor_v1b.py` | `2802c810d76b40e291188b2186439f53ccda0e13` |
| `test_g1_v1b_negative_qa.py` | `7e4270732b4c2f81b1677b82647456067989750d` |

Other evidence to read in order:
1. `docs/research/six-ttm/G1_CODEX_DISTINCT_PREEXECUTION_REVIEW_HOLD_20261109.md`, Git blob `5f478a0a801c31e9c119b9691440fc17252b3846`. This is the **previous genuinely separate review** and remains HOLD.
2. `docs/research/six-ttm/G1_CODEX_HOLD_INTEGRATED_REMEDIATION_AND_NEGATIVE_QA_PLAN_20261109.md`, its issue-to-fix table.
3. `docs/research/six-ttm/G1_CODEX_HOLD_V1B_INTEGRATED_REMEDIATION_AND_REVIEW_PACKET_20261109.md`, the author repair summary.
4. `docs/research/six-ttm/G1_V1B_CODEX_HOLD_REMEDIATION_INTEGRATED_CPU_QA_RECEIPT_20261109.json`, author QA only.
5. `docs/research/six-ttm/G1_SCIENCE_PREREG_V1_CONTRACT_CANDIDATE_20261109.json` and `G1_SCIENCE_PREREG_V1_METHODS_AND_THRESHOLDS_20261109.md`. The original prereg must not be silently edited.
6. `docs/research/six-ttm/G1_V1A_DATA_MAPPING_DEDUP_FUNCTIONAL_ALIGNMENT_AMENDMENT_REVIEW_CANDIDATE_20261109.md` and G1 manifest 29-gate QA/Qwen model technical receipts.

**Readback correction:** Some earlier copies of the packet/receipt say `PASS_37_OF_37` or stale blobs. The four **current** Git blobs above and the source test output `PASS_G1_V1B_ADVERSARIAL_CPU_ONLY`, **38 checks**, are the canonical v1b candidate. Preserve historical documents; do not interpret an older copied count as a regression. Do not take the 38 checks as independent QA.

Prior locked evidence: T1 manifest SHA256 `9f2ebaca821bddf0a9d7ae30ccfcef34561b968b21159aa913794298235a2fa9`; G1 private manifest SHA256 `6451be0cd09a54378eda9e815b5c89ce8ce8301ddefef556476d94e3e31e42b6`; G1 split counts TRAIN128/DEV64/TEST64. Qwen3-0.6B and Qwen3-1.7B one-shot *technical* PASS are already consumed and **must not be replayed**.

## 2. Required reviewer actions — one independent review batch

**A. Reproduce source-pinned synthetic QA (CPU only).** With all four source files adjacent under a project-local isolated test directory, verify all blob SHAs before executing:

```powershell
$ErrorActionPreference = 'Stop'
$py = 'C:\Users\minht\AppData\Local\Programs\Python\Python312\python.exe'
& $py --version
& $py .\test_g1_v1b_negative_qa.py
if ($LASTEXITCODE -ne 0) { throw 'STOP_G1_CODEX_QA_FAILED' }
& $py .\g1_science_guard_v1b.py --mode selftest
& $py .\g1_science_core_v1b.py --mode synthetic-qa
& $py .\g1_science_private_feature_extractor_v1b.py --mode synthetic-qa
```

Use available compatible Python and packages; the above path is the existing Windows Python 3.12 example. If imports/dependencies fail, state that separately rather than changing global Python or running unapproved GPU steps. The author reproduced 38/38 in a Linux CPU Python 3.13.5 environment, NumPy 2.3.5, no real data. **Independently design your own adversarial fixtures**; exact replication of the author's QA alone does not satisfy the review.

**B. Verify the Codex HOLD repair scope:** the science extractor must never access TinyStories full TRAIN source during TRAIN/DEV extraction, nor G1 TEST prefix bytes before the DEV freeze; the source broker is **not yet implemented**. Validate complete freeze JSON/SHA, 1,000 DEV-selected shuffled-null alphas, signed-permit identities/phase/HEAD/blobs, actual 8 probe strings, model auxiliary SHA-256 pins and 63+1 bootstrap terminal behavior. Assess information-budget asymmetry (A→P vs B-direct), neutral orthogonal rotation, near-duplicate/exchangeability limitations.

**C. Execute new *negative* checks not assumed covered by the author (all synthetic):**

- Fake reviewer/owner, self-signed and mismatched Ed25519 key, missing `code_author_id`, expired/altered phase, workspace, run ID or blob must stop **before data/GPU**.
- A TEST source-open trap must show no TEST bytes opened by TRAIN/DEV; TEST access when freeze is empty, stale, wrong run or missing must stop. Separately test the *missing* split broker design rather than assuming a staging file is trusted.
- Change feature tensor bytes while preserving exactly the same 64-character story IDs and order; a trusted stage receipt/digest must detect it. Test ZIP bombs/oversized members, symlinks/junctions and same-file-handle parse/hash invariance.
- Crash immediately before/after marker, pack write, receipt publication and TEST read; concurrent workers, workspace rollback/deleted marker and replay after STOP. Local marker-only correctness is **insufficient** against an actor who can roll back the workspace.
- Force synthetic CPU null cases: DEV SST zero, TRAIN probe std zero, full TEST SST zero, TEST 63+1 pattern, bootstrap draw without the one deviating story, CKA zero-variance, invalid alpha/permutation count. Terminal results must follow the explicitly amended estimand and must never authorize a TEST retry.
- Fake clock and forced peak VRAM/busy inference must enforce **cumulative** 60-minute per teacher, 120-minute total; loading/forward/cleanup cannot run indefinitely merely because a per-prefix timer check exists.
- Check there are no raw story strings, prefix texts, private features, unintended paths or exception payloads in logs/public repo.

A **single reproducible review report** should identify each test's exact source, executed command, actual result and whether the test is independent or only author-supplied.

## 3. Remaining hard-gate closure — integrated acceptance contract

Do not treat these as six micro-permits. They form **one pre-science admission package** with mandatory acceptance all together:

| Hard gate | Completion evidence required | Known status at handoff |
|---|---|---|
| **G1 AUTHORITY** | Owner-controlled public-key fingerprint, authenticated signed permit binding code author ≠ reviewer, owner, exact HEAD, both runner blobs, amendment, G1 manifest, run ID, workspace, phase, expiry and data scope. Signing key must NOT be checked into repo. | `HOLD_UNPROVISIONED_KEY` |
| **G1 SPLIT-BROKER** | Independently reviewed, owner-authorized private materializer; immutable TRAIN/DEV payloads accessible pre-TEST; TEST prefix payload encrypted/inaccessible until DEV freeze; proof of byte-level TEST isolation; avoid re-sealing original 128/64/64 manifest. | `HOLD_NO_BROKER` |
| **G1 PACK/LEDGER** | External trusted writer/run-stage receipt binding digest of exact NPZ bytes parsed, frozen train/DEV fits and ID order; crash-consistent atomic commit, private filesystem ACL, no symlink/reparse/TOCTOU; synthetic corruption/race QA. | `HOLD_NO_TRUSTED_LEDGER` |
| **G1 ONE-SHOT** | External monotonic consumption record persisting even if local workspace deleted; `ADMITTED → TRAIN_COMMITTED → DEV_COMMITTED → FIT_FROZEN → TEST_EXTRACT_CONSUMED → TEST_PACK_COMMITTED → TEST_READ_CONSUMED → TERMINAL`; rollback and replay tests. | `HOLD_LOCAL_MARKER_ONLY` |
| **G1 GPU GUARD** | Executable OS-level kill-capable watchdog, cumulative 60-min/model and 120-min/run T4 budget, peak VRAM ≤12 GiB, free-tier/resource proof with synthetic forced failures; no repeat of consumed technical smokes. | `HOLD_NO_WATCHDOG_ATTESTATION` |
| **G1 METHODS** | Explicit reviewed v1b amendment approving fixed-full-TEST-SST paired bootstrap, terminal inconclusive results, near-duplicate/pair exchangeability assumptions, A/B information-budget fairness, diagnostics omission and scoped feasibility only. | `HOLD_AMENDMENT_REVIEW` |

The owner has only authorized *local TRAIN scan for metadata/hash sealing*. There is **no** permission yet to stage original TinyStories source on Colab, store private Qwen features, or run scientific TEST. Reviewer may propose Windows-local staging or Colab private staging, but the final data rights/storage/retention scope must be decided in **one owner admission decision after the distinct review**, not assumed or invented.

**If a required external component cannot be built or independently qualified within this review, return HOLD, name the smallest integrated remaining work package and do not generate a fake PASS.** The reviewer may provide candidate patches in a clearly separate branch or artifact, but must not modify the frozen reviewed v1b blobs and then self-certify the changed code. A changed implementation requires a new source pin and separate adjudication.

## 4. Mandatory return format (one result, not many micro-decisions)

Deliver a new `G1_V1B_CODEX_DISTINCT_REREVIEW_<DATE>.md` review artifact, preferably append-only in `docs/research/six-ttm/`, with:
- `reviewer_id`, independent agent/subagent provenance, date, exact branch HEAD and all four Git blobs;
- reviewer-owned commands, separate PASS/FAIL/NOT_TESTED per required gate and reproducible receipt evidence;
- a severity-classified finding table with exact source locations and the *actual* effect on TEST/source/one-shot validity;
- adjudication of changed v1b bootstrap estimand and v1a mapping/dedup (do not silently change sample/thresholds);
- **exactly one** verdict `PASS_DISTINCT_REVIEWER`, `HOLD` or `FAIL`, plus `G1_SCIENCE_LOCK=HOLD` irrespective of review until owner authorizes.

A reviewer PASS means code/protocol can be **presented** for the single integrated owner science + private-data admission; it does **not** issue a science permit. If HOLD, provide one ordered integrated remediation plan to the implementing agent and a fresh reviewer run after changes.

## 5. Strict no-side-effects boundary

No Qwen weight re-download, real science extraction, G1 TRAIN/DEV/TEST feature computation, G1 TEST opening, Colab real science, owner-key invention, new science permit, replay of one-shot technical runs, changes to T1/G1 manifests, TTM main, PR#12, `lineage.md`, TTM-Small-4M checkpoints, or writes outside `D:\WORK\RESEARCH\TokenToModel-Lab`.

**Final at handoff:** `V1B_PINNED_SOURCE=PASS` · `AUTHOR_SYNTHETIC_QA=PASS_38_38` · `DISTINCT_REREVIEW=PENDING` · `HARD_GATES=OPEN` · `G1_SCIENCE_LOCK=HOLD`.
