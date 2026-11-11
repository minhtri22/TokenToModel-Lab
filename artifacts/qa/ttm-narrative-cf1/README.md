# TTM Narrative-CF1 — GitHub source of truth

**2026-11-11 | O0-Small4M frozen | 36 public DEV pairs + 72 encrypted FINAL pairs | no model evaluations/training/GPU.**

**Decision:** `GO_SCOPED_CPU_FROZEN_O0_DEV_36_PAIRS_ONLY`; `BLIND_FINAL=HOLD`; `T4_TRAINING=HOLD`; `O1=DEFER`. This is a research-readiness decision; the DEV neural run is **NOT EXECUTED**.

## Docs and receipts

- [Full scientific design, CPU source QA and owner-scoped decision](../../../docs/research/TTM_O0_NARRATIVE_CF1_NATURAL_PAIRS_TEACHER_FORCED_SCORER_CPU_QA_BLIND_FINAL_OWNER_DECISION_20261111.md)
- [Machine-readable single decision](CF1_INTEGRATED_CPU_SOURCE_AND_OWNER_SCOPED_DECISION_20261111.json)
- [Author corpus audit: 36/36 DEV and 72/72 owner-private semantic-template/source checks](CF1_CORPUS_AUTHOR_SOURCE_QA_20261111.json)
- [Exact T1 BPE2048 DEV length QA](CF1_EXACT_T1_BPE2048_DEV_READONLY_QA_20261111.json)
- [25/25 CPU synthetic scorer QA](CF1_CPU_SCORER_UNIT_QA_20261111.json)
- [8/8 frozen 1024 checkpoint CPU fixture QA (P02 algebraic-equivalent reconstruction, not exact blob)](CF1_PARENT_CPU_FIXTURE_QA_20261111.json)
- [AES256GCM FINAL and encrypted private-author-source verification QA](CF1_OWNER_ESCROW_VERIFY_QA_20261111.json)

## Dataset

- [DEV model input only](CF1_DEV_MODEL_INPUT_ONLY.json) — 36 records, exactly `context_a/context_b/completion_x/completion_y`, no labels/IDs/split; SHA256 `81e9849226029a1cb017c87da4202347be42dc92039db8c0d430d7115b68b4ed`.
- [DEV public oracle](CF1_DEV_PUBLIC_ORACLE.json) — public labels + pair/family metadata; SHA256 `3a425188077f24041a02fe9675e5a503221fe5cc0247ebd53a8cc266329c046d`.
- [FINAL AES256GCM envelope](CF1_FINAL_ENCRYPTED_ENVELOPE.json) — contains **encrypted** 72 private FINAL pairs/labels and **encrypted** exact private authoring script. Exact Git blob `b3266d8c4eccbb7fe203de66e9af8d2f75547673`. GitHub does not contain the key or any plaintext FINAL records.
- **Key is owner-private under TTM project root** `D:\WORK\RESEARCH\TokenToModel-Lab\_tmp\TTM_CF1_FINAL_OWNER_PRIVATE_KEY_DO_NOT_GITHUB_20261111.json`, written and read back by connector. Do not commit, attach to PR, or include in QA logs.

## Executable sources (source readback pinned)

- [Public DEV reproducible generator](../../../tools/research/narrative_cf1/cf1_public_dev_generator.py) — **2/2 SHA exact**.
- [Strict teacher-forced logprob scorer and P02 exact Git blob loader](../../../tools/research/narrative_cf1/cf1_teacher_forced_scorer.py).
- [Exact T1 BPE manifest reader](../../../tools/research/narrative_cf1/cf1_exact_t1_bpe.py).
- [Future DEV-only read-only runner](../../../tools/research/narrative_cf1/cf1_dev_once_readonly.py) — *not executed on neural corpus*.
- [Scorer unit tests](../../../tools/research/narrative_cf1/cf1_cpu_scorer_unit_qa.py).
- [Checkpoint source fixture](../../../tools/research/narrative_cf1/cf1_parent_cpu_fixture_smoke.py).
- [Corpus author QA](../../../tools/research/narrative_cf1/cf1_corpus_source_qa.py).
- [FINAL AES authenticated receipt](../../../tools/research/narrative_cf1/cf1_owner_escrow_verify.py).
- [Owner-private FINAL BPE only, no plaintext emission](../../../tools/research/narrative_cf1/cf1_private_final_bpe_audit.py) — **not yet executed**.

## Required scientific caveats

- 108 pairs are 36 hand-authored scene templates × 3 cast variants, **not 108 independent graphs**; DEV and FINAL use disjoint scene IDs but share the same surface intervention strategy.
- A simple *first mentioned person* clue solves **36/36 DEV** and was found author-side to solve **72/72 private FINAL** before encryption. This is a verified *shortcut*, not a semantic-state test: `SCIENTIFIC_STATE_DISCRIMINATION=FAIL_SCOPED`.
- The private FINAL is encrypted but **not a qualified scientific FINAL** without internal independent semantic review, exact owner-private BPE/token budget and query-rooted structural independence.
- No P02 model was run on DEV/FINAL. CPU scorer QA uses synthetic logits; parent smoke used an N1 equivalent architecture and ASCII-byte fixture. Exact P02 source blob and original T1 manifest will be enforced by the future read-only runner.
- No optimizer, CUDA, original TEST/Q1Q2, new model checkpoint, PR13 merge or `lineage.md` edit was performed.

**Bước thực hiện tiếp theo:** `TTM_O0_CF1_FROZEN_STEP1024_DEV_ONLY_ONESHOT_CPU_TEACHER_FORCED_EVAL_AND_OWNER_ADJUDICATION` — only read-only DEV 36, no FINAL, no GPU, no training; refuse any hash mismatch.
