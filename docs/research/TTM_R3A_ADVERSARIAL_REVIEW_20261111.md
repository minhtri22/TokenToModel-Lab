# TTM R3A — Independent adversarial shortcut & O0-only review

**Date:** 2026-11-11  
**Repo:** `minhtri22/TokenToModel-Lab`  
**Pinned exact commit:** `81327724c08771682622bebb8648fefd55a4fa9a`  
**Handoff:** `docs/research/TTM_R3A_CODEX_ADVERSARIAL_SHORTCUT_AND_O0_PILOT_REVIEW_HANDOFF_20261111.md`  
**Review scope:** read-only GitHub inspection; executed independent JavaScript analysis on GitHub-fetched full R3A JSON. No GitHub mutations, no GPU, no TTM training, no TEST/Q1Q2 or lineage changes. **Review author: ChatGPT/GPT-6, not an external or separately invoked Codex reviewer.**

## Executive adjudication

- `SOURCE_PIN_SHA256_GIT_BLOB_BYTE_LENGTH = PASS 9/9` (independently recalculated SHA-256 on connector-returned UTF-8 content; Git blobs and lengths match manifest).
- `INDEPENDENT_VISIBLE_TEXT_STATE_REPLAY = PASS 384/384` on all 96 four-cell counterfactual groups in a separately implemented JavaScript validator. All event preconditions in these positive fixtures held.
- `R3A_NEW_SHALLOW_HEURISTIC = 384/384` (100%) on the **pinned model-input rows**, alias-aware backward regex rule, oracle used solely for scoring **after predictions**.
- `DEV_CHALLENGE_LENGTH_LEAK = 384/384` identifiable from family and number of events.
- `QUERY_DEPENDENCY_SKELETON_SPLIT_OVERLAP = 3` shared canonicalized query-relevant trace signatures, contrasting with **0** for the supplied full-event motif metric.
- `ORIGINAL_PYTHON_44_TEST_REEXECUTION = NOT_EXECUTED`; existing `44/44` and `30/30` were read as author-side historical receipts and were **not** independently re-run. The generated Python script in this review was syntax compiled and passed **4/4 smoke fixtures**, but its full Python replay was **NOT_EXECUTED** here.
- `SCIENCE_DISCRIMINATION = FAIL_SCOPED_BY_NEW_100_PERCENT_SHALLOW_HEURISTIC` for this public R3A toy; does not overwrite its scoped source/validator PASS.
- **Reviewer recommendation:** `AMEND_TOY_AGAIN`, one bounded CPU amendment only; preserve independent O0 design work but **no O0 experimental GO**, O1 remains DEFER. This is **not** an owner authorization.

## Evidence source pin verification

Against `artifacts/qa/ttm-r3-structural-design/r3a/R3A_SOURCE_OF_TRUTH_SHA256_AND_OWNER_SCOPED_DECISION_20261111.json`: all nine listed artifacts match manifest SHA-256, bytes, and Git blob:

| File | SHA-256 match | Git blob match | Byte count match |
|---|---|---|---|
| `r3a_generator.py` | PASS | PASS | PASS |
| `r3a_independent_checker.py` | PASS | PASS | PASS |
| `r3a_integrated_cpu_qa.py` | PASS | PASS | PASS |
| `R3A_PUBLIC_ORACLE.json` | PASS | PASS | PASS |
| `R3A_MODEL_INPUT_ONLY.json` | PASS | PASS | PASS |
| `R3A_CHECKER_REPORT.json` | PASS | PASS | PASS |
| `R3A_LATEST_WRITE_BASELINE.json` | PASS | PASS | PASS |
| `R3A_CPU_QA.log` | PASS | PASS | PASS |
| `R3_ORIGINAL_CODEX_BASELINE_EXACT_PYTHON_FULL_REPLAY.json` | PASS | PASS | PASS |

Hash function self-test: SHA-256(`abc`) `ba7816bf...15ad` PASS. Model JSON SHA-256 `2510866d82641bd27207082566d6b4dbb867e59516794e422dff8fb041646402`; oracle `b509fae3f63399c978d532c2686d147bd4ba41e44b2aa9135dcd38360e6ffb08`.

## R3A-ADV-NEW-01 — HIGH science blocker: alias-aware backward regex 384/384

A separately implemented predictor consumes ONLY `story`, `question` and does the following: read explicit alias-definition lines into a tiny name-lookup table; scan event lines backward for the queried item/actor, returning the latest matching receiver/goal-change/cancel/incoming delegation/begin event; default to `NONE` when the goal has no applicable event. It never replays dynamic holder or goal state, verifies transition preconditions, or constructs the causal dependency graph. The public oracle is used only **after prediction** to assess correctness by exact `(story,question)` projection.

| Baseline | T1 DEV | T1 CHALLENGE | T2 DEV | T2 CHALLENGE | T3 DEV | T3 CHALLENGE | Total |
|---|---:|---:|---:|---:|---:|---:|---:|
| Alias + direct write, without goal delegation/cancel | 64 | 64 | 32 | 48 | 32 | 48 | **288/384** |
| Event-role lookup, without alias resolution | 32 | 32 | 48 | 64 | 32 | 32 | **240/384** |
| Alias + backward regex + `NONE` fallback | 64 | 64 | 64 | 64 | 64 | 64 | **384/384** |

This is not a generic proof of ability to solve arbitrary state tasks or a claim that all kinds of semantic computation are absent. It *does* decisively refute the claim that **these 384 R3A questions require full dynamic state replay or graph reasoning rather than a shallow task-specific rule**.

The prior author's baseline `208/384` is accurately scoped to its narrower direct-write rule. It was not falsely recomputed here as an independent full Python replay.

## R3A-ADV-NEW-02 — HIGH split confounding

Using the **visible model-input text only** and a family cue from query type/alias, `split` is perfectly inferable from event count:

| Family | DEV event lines | CHALLENGE event lines | Records |
|---|---:|---:|---:|
| T1 | 9 | 10 | 128 |
| T2 | 7 | 9 | 128 |
| T3 | 9 | 10 | 128 |

`384/384` split identification follows without looking at group ID or oracle metadata. The shuffle of model-input rows works, but the **split itself is content-confounded**. Consequently, no-overlap under a full-sequence signature cannot establish robust graph-OOD generalization.

## R3A-ADV-NEW-03 — HIGH query-relevant structural overlap

The source checker labels *every* event (`target` vs `nontarget`) and retains their sequential order. An extra unrelated event can separate split signatures without changing the answer-relevant causal trace. An independently authored, simple query-relevant dependency-skeleton signature removes unrelated events and lexical names, while preserving query alias/direct role and relevant `INIT`, `HANDOFF`, `SET`, `DELEGATE_IN`, `CHANGE`, and `CANCEL` operations.

Under this **alternate diagnostic signature** (not asserted to be a final graph-isomorphism canonicalizer):

- T1: one shared `H|INIT>HANDOFF` trace (distractors); 32 DEV records and 32 CHALLENGE records have a shared trace.
- T2: one shared `G|Q_DIRECT|TARGET_SET>TARGET_CHANGE` trace (distractors); 32 DEV and 32 CHALLENGE records.
- T3: two shared traces: `G|Q_ALIAS|SOURCE_SET>DELEGATE_IN` and `G|Q_DIRECT|TARGET_SET>TARGET_CHANGE`; 64 DEV records and 48 CHALLENGE records.
- **Global:** 3 shared trace signatures; 128 DEV and 112 CHALLENGE records have a trace represented in both splits.

These counts are about query-relevant skeletons; they are **not** the same metric as the original checker, and do not imply full-event signatures are miscomputed. The original claim of zero overlap under *its particular signature* remains true. The stronger claim of true query-dependency graph disjointness remains **unproven**.

## R3A-ADV-NEW-04 — Positive code/data quality preserved

A separately written JavaScript visible-text interpreter checked all 384 rows without using `source_events` to reconstruct answers and verified 96/96 four-cell groups (`A_T`, `A_D`, `B_T`, `B_D`). All 384 model-input entries map exactly to the public oracle projection, with only `story` and `question`, zero duplicate `(story,question)` pairs, and a nontrivial shuffled order. All target answers change across intervention, distractors stay equal, and the A/B stories differ in one event line. Goal answer `NONE` occurs 32 times in T2.

This confirms limited engineering/integrity properties. It **does not** make the public toy a sealed FINAL, nor replace original Python's 44 positive/negative test run.

## Scientific interpretation and O0/O1 scope

1. R3A's previous `PASS_SCOPED` for source validation should **not** be erased; the **scientific discriminative objective** fails for the new shallow baseline.
2. Do not claim that a symbolic full state interpreter scoring 100% is a failure: such an interpreter is a positive-control oracle. The failure here is **a much weaker query-keyed rule also attaining 100%**.
3. The six-arm A–F design cannot isolate pure architecture from objectives, token exposure and supervision without matched ledgers. `C-F` compares a state-head objective against serialized state-text; only scoped joint-package claims would be justified.
4. Public DEV/CHALLENGE/oracle cannot be reused as blinded FINAL, and R3A must not train/select O1. No GPU/T4, no new TTM checkpoint, no O1 activation is authorized by this review.
5. `KEEP_O0_ONLY_SMALL_NEURAL_FEASIBILITY_DESIGN` remains a scientifically distinct *design* possibility; it should not be sold as science evidence against shortcuts on R3A.

## Suggested bounded next CPU step — ONE integrated batch

**Reviewer recommendation:** `AMEND_TOY_AGAIN`, not multiple new permission gates. Introduce paired fixtures where the same last matching text event has **different correct answers** because of earlier causal dependencies or valid context, including at least one alias-hop and goal chain; add distractor interventions that are structurally comparable across splits; balance sentence count and local lexical cues between DEV and CHALLENGE. Construct a more faithful query-rooted dependency DAG signature with explicit transfer/source/alias edges, then independently score **this frozen shallow baseline** plus a generic symbolic interpreter. Preserve no-leak input schema, positive preconditions, A/B four-cell counterfactuals and negative QA.

**Finite decision:** if a compact CPU amendment still permits a 100% shallow baseline, archive the R3 anti-shortcut toy as uninformative for the intended discrimination and continue any O0 feasibility study only under a different, separately justified diagnostic corpus. No T4 GO in this review.

## Execution and provenance matrix

| Action | Status |
|---|---|
| Exact GitHub commit/source readback | EXECUTED |
| 9-file Git blob, bytes and SHA-256 comparison | PASS / EXECUTED |
| Independent JS 384-row heuristic and stratified scoring | EXECUTED / 384/384 |
| Independent JS visible-text state/precondition replay | EXECUTED / 384/384 |
| Independent JS 96 counterfactual validation | EXECUTED / 96/96 |
| Independent JS row-index, length and dependency-skeleton diagnostics | EXECUTED |
| Original Python checker replay and 44 tests | NOT_EXECUTED |
| Original 30 negative Python tests independently | NOT_EXECUTED |
| New Python baseline full R3A replay | NOT_EXECUTED (code + four-smoke prepared) |
| GPU/TTM/O0/O1 inference, training, FINAL | NOT_EXECUTED |
| GitHub review branch/commit/PR/lineage changes | NOT_EXECUTED; GitHub left read-only |

**Bước thực hiện tiếp theo:** owner quyết định `AMEND_TOY_AGAIN` hoặc chấp nhận giữ R3A ở mức public demo và chuyển thiết kế O0-only theo mục tiêu riêng. Reviewer khuyến nghị một lần chỉnh toy tích hợp CPU; O1 DEFER, T4 NO GO.
