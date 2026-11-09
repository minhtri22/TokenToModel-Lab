# G1 v1b — Integrated Codex HOLD remediation and distinct re-review packet

**Date:** 2026-11-09  
**Status:** `VERSIONED_REVIEW_CANDIDATE / AUTHOR_SYNTHETIC_QA_PASS / INDEPENDENT_RE_REVIEW_PENDING / SCIENCE_LOCK=HOLD`.

## 1. Immutable source and baseline

GitHub repository: `minhtri22/TokenToModel-Lab`.
Research branch: `research/ttm-six-cross-model-representation-transfer-20261109`.
Local root: `D:\WORK\RESEARCH\TokenToModel-Lab`.
Prior Codex verdict `HOLD` stored byte-exact at `docs/research/six-ttm/G1_CODEX_DISTINCT_PREEXECUTION_REVIEW_HOLD_20261109.md`, Git blob `5f478a0a801c31e9c119b9691440fc17252b3846`. The original prereg v1 candidate, its methods, the original science v1 code, T1 and G1 manifest, TTM-Small-4M checkpoints and historical GPU technical one-shots remain unchanged.

| Versioned v1b source | Git blob (verify exact) |
|---|---|
| `scripts/research/six_ttm/g1_science_guard_v1b.py` | `d67b35cd8cba907904d0f23ccedd4b6b68d4850f` |
| `scripts/research/six_ttm/g1_science_core_v1b.py` | `94611c0449001230b2957487e152cd706f817516` |
| `scripts/research/six_ttm/g1_science_private_feature_extractor_v1b.py` | `2802c810d76b40e291188b2186439f53ccda0e13` |
| `scripts/research/six_ttm/test_g1_v1b_negative_qa.py` | `7e4270732b4c2f81b1677b82647456067989750d` |

Private G1 128/64/64 manifest SHA-256: `6451be0cd09a54378eda9e815b5c89ce8ce8301ddefef556476d94e3e31e42b6`. T1 source manifest SHA-256: `9f2ebaca821bddf0a9d7ae30ccfcef34561b968b21159aa913794298235a2fa9`.

## 2. Implemented scoped repairs (not claims of independent proof)

**Source split isolation:** v1b extractor no longer invokes the historical full-TinyStories scanner during science. It reads only a separate `G1_PREFIX_<SPLIT>.json` under the private split-root, requires matching IDs/prefix hashes and rejects TEST access until a complete DEV freeze is validated. The exclusive, fsynced TEST extraction marker is now created before the first split-specific TEST prefix byte read. The original v1 full-source parser remains historical and is not an approved science path. A separate owner-authorized split materializer/broker is still absent (see HOLD below).

**Authority:** v1b checks an Ed25519 signature over canonical owner admission including reviewer identity, distinct code author, phase, run ID, workspace, manifest hash and reviewed source/amendment blob pins. Any forged/missing/expired permit fails in synthetic QA. Production `OWNER_ED25519_PUBLIC_SHA256_PIN=None` intentionally denies *all* science. No owner key has been provisioned; no manual override is allowed. Test keys in QA do not establish an owner approval.

**Freeze and packs:** validate full DEV freeze schema, alpha selection, 1,000 permutation choices, committed TRAIN/DEV pack SHA and source/run identity; reject empty/stale frozen files. Numeric pack validation hashes **the same byte buffer used for parsing** and validates ZIP members/dtype/shape/size, content-ID order, manifest binding and expected digest. Private files use lstat/symlink/junction protections, fd-based regular-file read and atomic stage+fsync+exclusive hardlink final publication. No overwrite and no normal retry after one-shot STOP. Console errors are sanitized.

**Statistical change (prospective v1b amendment requiring reviewer approval):** the bootstrap of improvement over TRAIN mean now resamples paired per-story squared-error differences, divided by the **unchanged, frozen full-TEST SST**, not a re-sampled SST. This avoids the Codex 63+1 bootstrap terminal exception. If original full TEST SST is <1e-8 per dimension, return `INCONCLUSIVE_DEGENERATE_TEST`; if centered CKA has zero denominator, return `INCONCLUSIVE_GEOMETRY_DEGENERATE`; if DEV SST degenerate, STOP before TEST. Preserve 8 probes, TRAIN128/DEV64/TEST64, alpha `{1,10,100}`, 1,000 shuffled TRAIN fits with DEV re-selection, 1,000 CKA-null permutations and 2,000 bootstrap draws. No post-TEST changes.

**Model resources:** both Qwen models, pinned revisions, weights, tokenizer/config/Licenses/index/generation file hashes are verified by the versioned extractor before load. Sequential teacher load, inference-only evaluation. A cumulative 60 minutes/model, 120-minute/run budget helper is present and fake-clock tested; no separate process-kill watchdog has been qualified. Comparisons remain A→P vs B-direct vs oracle and shuffled null; A→P is linear, not proof of distinct SIX causal mechanism. Orthogonal rotation is a neutral basis check, not an information-destroying null.

## 3. Independent pre-execution negative QA to reproduce

Author executed in isolated Linux CPU Python 3.13.5, NumPy 2.3.5, cryptography 46.0.4:

```powershell
# In an isolated project-local worktree with all four exact v1b files adjacent:
python test_g1_v1b_negative_qa.py
python g1_science_guard_v1b.py --mode selftest
python g1_science_core_v1b.py --mode synthetic-qa
python g1_science_private_feature_extractor_v1b.py --mode synthetic-qa
```

`PASS_G1_V1B_ADVERSARIAL_CPU_ONLY`, **38 checks**, including: unsigned or modified permit rejection; different reviewer and code author; denied early TEST read; nested symlink rejection; 0-byte/stale DEV freeze rejection; same IDs but different tensor SHA rejection; malformed ZIP; atomic commit no-overwrite; marker second-open rejection; 63+1 bootstrap finite; full TEST SST terminal; zero-var CKA terminal; mocked budget overruns.

Full synthetic algorithm loop: 1,000 TRAIN shuffles / 1,000 CKA permutations / 2,000 bootstrap resamples PASS (synthetic hidden dimensions 7/11). The complete author QA evidence is `docs/research/six-ttm/G1_V1B_CODEX_HOLD_REMEDIATION_INTEGRATED_CPU_QA_RECEIPT_20261109.json`. The reviewer MUST run independent tests rather than equating these author assertions with peer review.

## 4. Hard blockers — request Codex verdict PASS/HOLD/FAIL after reviewing

1. **No production authority key**: the production permit signature verifier is intentionally locked; owner identity and one-shot permission need an independently controlled public-key pin and authenticated owner scope, not an arbitrary user-supplied JSON or test-only key injection.
2. **Missing split materializer**: TRAIN/DEV source reader is separated from TEST but no approved, audit-pinned broker has yet produced `G1_PREFIX_<SPLIT>.json`. Reviewer must decide how to establish strict TEST byte isolation during staging; do not claim historical hash-only seal authorization covers Colab source transfer.
3. **Pack provenance**: receipt JSON and local mutable files alone do not prove trusted writer origin; the signed run admission must bind a trusted stage digest ledger. Partial writes, fail-stop and peer recovery need adversarial independent QA.
4. **External one-shot journal**: local exclusive markers only prevent replay as long as the private workspace persists. A malicious deletion/rollback of the entire folder requires an external durable monotonic record. No claim of tamper-resistant cross-session replay protection is made.
5. **Windows/Colab OS controls and GPU endurance**: reparse/junction ACLs, simultaneous writers, OS-level watchdog (interrupt hung load/forward) and aggregated run budgets need real-platform qualification. Synthetic CPU and earlier one-shot **technical** Qwen smokes do not establish full scientific pipeline endurance.
6. **v1b amendment and inference scope**: independent reviewer must expressly accept fixed-full-TEST-SST bootstrap estimand, terminal inconclusive outcomes, exchangeability/near-duplicate limitations, A-vs-B information budget asymmetry and the fact 64 held-out stories cannot prove universal or causal SIX mechanisms.

No real science, model downloads, G1 TEST read, owner admission or signed review occurred in this batch. Nothing is merged to `main`; no PR#12 or `lineage.md` changes.

## 5. One integrated reviewer result

Provide one signed source-pinned independent report with reviewer ID, exact Git HEAD, each v1b Git blob, independently executed tests and specific evidence per Codex blocker. Outcome **`PASS_DISTINCT_REVIEWER` / `HOLD` / `FAIL`**. Reviewer must NOT issue a science permit. If any hard blocker remains, return HOLD and an exact minimal repair list.

**Pre-review decision:** `VERSIONED_CODE_V1B=READY_FOR_DISTINCT_REVIEW`; `SYNTHETIC_QA=PASS_37_OF_37`; `EXTERNAL_GATES=OPEN`; **`G1_SCIENCE_LOCK=HOLD`**.
