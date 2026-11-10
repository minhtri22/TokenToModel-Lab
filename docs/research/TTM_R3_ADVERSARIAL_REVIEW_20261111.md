# TTM R3 — Independent adversarial source & motif review (2026-11-11)

**Scope:** read-only GitHub assessment of `minhtri22/TokenToModel-Lab` commit `cd3dc4ceb3a42b9ac8df7bdb5169cda444c3b41a`. **No** GitHub writes, branch/PR mutation, GPU, neural training/inference, external human validation or changes to `lineage.md`. This review is by ChatGPT, **not** the pending Codex reviewer specified by the handoff.

## Exact source anchors

- Handoff: `docs/research/TTM_R3_CODEX_ADVERSARIAL_SOURCE_AND_MOTIF_QA_HANDOFF_20261111.md`, Git blob `29d3413d5610e5cd3e131cbd21f03af8dd4eb132`.
- Generator: `tools/research/semantic_state_r3/r3_generator.py`, Git blob `a1e20ae5e70210251a2d39861a7358c1a7ac1d39`.
- Checker: `tools/research/semantic_state_r3/r3_independent_checker.py`, Git blob `507af48770fdb29aa2f4da93b561f3d6b6c4ac95`.
- CPU tests: `tools/research/semantic_state_r3/r3_single_cpu_qa.py`, Git blob `eb96fd1ac445b432ad2e63c4d1965b70f9eea4c3`.
- Public model input: `artifacts/qa/ttm-r3-structural-design/runtime/R3_MODEL_INPUT_ONLY.json`, Git blob `b67628fe8ddd96e027e86a2f71b904cfee968143`, SHA256 `4fa0ad45acdfecb2143a984127e6ad0c50126c203996148d60843eb1214cd50a` (source manifest).
- Public oracle: `artifacts/qa/ttm-r3-structural-design/runtime/R3_PUBLIC_ORACLE.json`, Git blob `f7dc397be3be6cf2f14eba11cedbefa505a96dd7`, SHA256 `bd9fb15d3f3850823e083269a61df90eaddaea3e61b8b73e9f40b4ec74c7ce47` (source manifest).
- Original scientific design: `docs/research/TTM_R3_STRUCTURAL_STATE_TRACING_PHILOSOPHY_FORMAL_SCIENCE_DESIGN_20261111.md`.

## Actually executed independent baseline

Read the exact two JSON objects using the connected GitHub service. For each of the **384** model-input rows, an independently authored predictor read **only** its `story` and `question` and searched backward for:

1. `Who holds item?` -> last `person passes item to recipient`; otherwise `item starts with person`.
2. `What is person goal?` -> last `person changes goal from old to new`; otherwise `person begins goal g`.

The predictor never parsed alias definitions, delegation/cancellation, preconditions, the graph, source-events or oracle answer. Oracle answers were loaded **only to score predictions**.

| Family / split | Correct / total |
|---|---:|
| T1 DEV | 64/64 |
| T1 CHALLENGE | 64/64 |
| T2 DEV | 64/64 |
| T2 CHALLENGE | 64/64 |
| T3 DEV | 64/64 |
| T3 CHALLENGE | 64/64 |
| **Total** | **384/384** |

All 256 holder answers were provided by a direct `passes ... to ...` statement; 64 goal answers by a directly queried `changes goal ... to ...` statement, and 64 by a directly queried `begins goal ...` statement. **Zero** goal answers were `NONE`; **zero** goal queries referred to an alias. This means the toy does not require a predictor to use cancellation, delegation, or alias resolution to answer any of its published questions.

A separate Python replay script, `ttm_r3_independent_latest_write_baseline.py`, was authored and syntax-tested with two smoke examples. Its full **Python** replay against the corpus has **not** been run in this environment; the complete 384/384 assessment above was executed directly against the two GitHub JSON objects in a JavaScript analysis. Do not mislabel the Python smoke as a full run.

## Findings

| ID | Severity | Finding | Decision impact |
|---|---|---|---|
| R3-ADV-01 | **HIGH / science blocker** | Query-keyed backward lexical lookup (no state graph) scores **384/384**. Existing `shallow_keyed_direct=64/384` is insufficient anti-shortcut evidence. | Hold claim that R3 discriminates graph/state reasoning from lexical lookup; amend diagnostic fixtures. |
| R3-ADV-02 | **HIGH** | Only 3 motif signatures per split, one template per family. `motif()` ignores `queried_key`; T1 uses handoff counts, T3 mostly op sequence, and T2 local streams. A zero overlap under these signatures is not a proof of topology/query-conditioned OOD generalization. | Add query-conditioned canonical relation/dependency motifs and cross-split lexical/length balance. |
| R3-ADV-03 | **MEDIUM** | Flattening always emits `A_T,A_D,B_T,B_D`, with family and split blocks in fixed order. Positional row index can encode cell/family/split if passed downstream, even though JSON record fields themselves are strict. | Shuffle/blind evaluation order and keep group mapping separate from model inputs. |
| R3-ADV-04 | **HIGH / science blocker** | `T2` includes cancel/delegate in narratives but none of the query outputs require their semantics; `T3` uses aliases as source references but never requires alias-resolved output. | Add answer-critical indirect references, `NONE` questions, and causal interventions whose effects propagate beyond a final direct value. |
| R3-ADV-05 | **MEDIUM** | Public labels/oracle and model inputs share a repository; current evaluator is not blind. This is already correctly disclosed, not an undisclosed code defect. | Public toy may remain DEV diagnostics only; future FINAL must be separately sealed. |
| R3-ADV-06 | **MEDIUM** | `C−F` O1-vs-O0 contrast cannot isolate pure architecture due to text-token CE vs state-head objective; six-arm design acknowledges this. | Require preregistered info, parameters, FLOPs, optimizer/seed ledgers and limited claims. |

**Source validation credits:** the schema enforces strict model root/record allowlists, catches duplicate decoded JSON keys, requires valid visible-text preconditions and exact 4-cell projection, and explicitly declares non-final public labels. The 70 author-side CPU tests / 42 negatives were read as *reported evidence*, not independently rerun by this reviewer. They should remain `PASS_SCOPED` rather than be retrospectively overwritten by a scientific shortcut finding.

## Minimal amendment and recommended gate

- Add at least one counterfactual family where **one upstream alias definition** changes, the later visible handoff goes to the **alias** and is identical in A/B, and the final real holder must be resolved through alias binding; verify source preconditions in both variants.
- Force goal queries that depend on `DELEGATE_GOAL` and `CANCEL_GOAL` (including `NONE`), not only direct `SET_GOAL` or `CHANGE_GOAL` for the queried person.
- Vary query key and event topology within each family; test last-keyed-write, one-line/n-gram lookup, position and query-order baselines. A *single* minimal latest-write 100%-accuracy finding already invalidates the desired anti-shortcut discrimination claim for the current dataset.
- For structural splits, canonicalize typed event edges and query dependencies, compute train/DEV/CHALLENGE disjointness on these signatures, and keep an additional independent blind FINAL.
- Keep source-schema `PASS_SCOPED`, set **R3 scientific diagnostic acceptance to `HOLD_AMENDMENT_REQUIRED` as a recommendation**, not an official owner adjudication. Continue O0 baseline design only; no O1/GPU claim yet.

**Not executed here:** independent mutation suite against checker, full source SHA256 recomputation, Python full-corpus replay, PR creation, Git commits, Codex agent review, neural O0/O1 tests or blinded FINAL.

**Proposed next step:** `TTM_R3_MINIMAL_ANTISHORTCUT_AMENDMENT_AND_SINGLE_INTEGRATED_ADVERSARIAL_CPU_QA_THEN_O0_PILOT_OWNER_DECISION`.