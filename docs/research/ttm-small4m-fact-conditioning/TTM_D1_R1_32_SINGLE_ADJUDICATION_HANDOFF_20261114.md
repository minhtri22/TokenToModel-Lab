# TTM-Small-4M D1 Bridge R1 — 32 typed skeleton BLUEPRINTS: one-packet source QA and adjudication

**Operation:** `TTM_SMALL4M_D1_R1_32_TYPED_SKELETON_STRUCTURE_ORACLE_NONOVERLAP_SINGLE_SOURCE_REVIEW`  
**Date:** 2026-11-14 · **Repository:** `minhtri22/TokenToModel-Lab`  
**Frozen scientific HEAD:** `dd52804685d186c17e600221ffb16ce78aea12ea`  
**Prior evidence commit:** `553f1d6db9c2d5572a7e664b64a32e9eaf977f88` · **Existing V6 candidate:** SHA-256 `e05774d9f0a155e19f70574260be839f1f0634bdfce2399ab2a67622dbc214a5`  
**Scope:** new source-only prospective blueprint packet. No model inference, science run, real TRAIN/EVAL data, private gold or TEST Q1/Q2. Prior 13/13, 12/12, 128 transitions NOT RERUN.

## 1. Implemented evidence, without falsely granting EVAL readiness

Generated 32 separate **typed AST source blueprints**: `4 categories × (4 TRAIN design + 4 structural-OOD design)`. Each contains explicit A/B finite states with all required V6 fluents, exactly one typed A/B state intervention `power(d1)`, a deterministic policy-dependency DAG using 4 typed observations, task-goal predicates, and no embedded gold answers. All eight DAGs per category have different truth tables. These ASTs are **not science data** and must never be relabeled as the sealed EVAL or the real 512/128/256 family data. Original candidate `actual_4x4_skeletons=NOT_GENERATED` has not been altered in the locked original; this packet demonstrates a possible amendment and requires adoption before science.

Stand-alone `independent_32_oracle_checker.py` (independent implementation path from the generator) validates 32 complete typed A/B world states, enumerates the six-verb legal action space per side, simulates preconditions/effects including `WAIT` atomic ticking and external transfer requests, requires **exactly one state-reachable action** per side satisfying the graph-selected goal, and requires `gold_A != gold_B` without reading any gold field. It checks each Boolean dependency input is causally sensitive and all 16 TRAIN–OOD graph pairs/category have reachable same-world semantic disagreement (64 witnesses total). It also checks unique graph signatures and distinct truth tables for all 8 per category.

`adversarial_32_source_qa.py` is a separate set of **12 new deliberate mutations**, none invoke prior 13/13 or 12/12. All 12 were rejected. NetworkX `DiGraphMatcher` independently confirmed the absence of isomorphic TRAIN–OOD directed, typed policy graphs for all 64 pairs in the model's execution sandbox. The standard-library independent checker needs no extra packages; only the optional negative-audit second-opinion uses NetworkX.

| Gate | New source-only result | Status |
|---|---:|---|
| Four categories × 4+4 typed ASTs | 32/32 | PASS_SOURCE_BLUEPRINT |
| A/B complete finite state + unique legal action | 32/32 pairs | PASS_SOURCE_BLUEPRINT |
| Explicit controlled A/B intervention | 32/32 | PASS_SOURCE_BLUEPRINT |
| 8 semantic distinct policy graphs/category | 8 × 4 categories | PASS_SOURCE_BLUEPRINT |
| TRAIN–OOD relevant graph novelty witnesses | 64/64 pairs | PASS_SOURCE_BLUEPRINT |
| Independent graph isomorphism NetworkX check | 64/64 nonisomorphic | PASS_SOURCE_BLUEPRINT |
| New negative mutation catches | 12/12 | PASS_SOURCE_BLUEPRINT |
| Private EVAL sealed source and blind gold | 0 | NOT_CREATED |
| Dataset rights/PII, independent evaluator credential | 0 | NOT_VERIFIED |
| Science-ready 32-skeleton admission | 0 | HOLD |

## 2. Important scientific limitations found in source review

1. **New objective/policy layer.** The DAG is a prospective amendment introducing a four-observation Boolean dependency graph that selects **goal predicates**; this is not established in frozen V6's six-action ontology. The source checker enumerates actions and verifies uniqueness **conditional on this proposed goal policy**. It does not establish a scientifically justified natural-language benchmark or generalization ability of Small4M. The evidence signals include synthetic device status / trigger / protection fields and may make the benchmark vulnerable to shortcut learning or Boolean-circuit recognition. Review independent task relevance, action ontology compatibility and construct validity before design GO.
2. **OOD novelty scope.** Directed graph non-isomorphism plus reachable truth-table disagreement is proven **for the public Boolean policy DAG**, not a proof that complete semantic action-transition graphs are structural OOD under the frozen scientific definition. A reviewer must decide if this constitutes the intended kind of semantic novelty rather than changing complexity or applying artificial rule syntax. Do not count the measured 64 source witnesses as science EVAL successes.
3. **Sealed custody and rights.** Full 32 blueprint ASTs are publicly inspectable and include public deterministic goals; they cannot be reused as a blinded, unopened EVAL. An actual scientific 16 OOD skeleton set requires separate independent custody and sealing before TRAIN, with private oracle/gold, rights/source and independent nonoverlap assessment. No private release occurred here.
4. **Independent reviewer.** The checker is written separately from generator and another algorithm verifies graph isomorphism, but all were arranged in this same AI conversation. This is **not independent organizational review**. Therefore no `GO_DESIGN_ONLY` or scientific authorization is granted here.
5. **Inherited R2/R3/R4/R5/R6.** Native source candidate and its seeds remain pinned; 13/13 and 12/12 were NOT RERUN; later implementation will separately need production HMAC/ACL/parser/runner readiness and independent source signature, not silently count this source demonstration as those gates.

## 3. One formal GO/HOLD verdict

**`HOLD_REVISE_BEFORE_PREREG`**. The precise R1 subgoal of having **32 concrete typed source blueprints with an independently implemented reachability/unique-action/nonoverlap checker** is satisfied on the *synthetic prospective policy graph* (32/32, 64/64, 12/12), but the **actual scientific AST/gold under the frozen task definition remains unauthorized and unsealed**, and a material Boolean-policy amendment requires separate reviewer acceptance. This is a design HOLD, not model scientific FAIL.

**Preserve:** `D1_BRIDGE_SCIENCE=HOLD`, `D1_EXISTING=HOLD_UNMODIFIED`, `TEST_Q1Q2=SEALED`, `FC02=NOT_OPENED`, `GPU=0`, `TRAINING=0`, `INFERENCE=0`, `MAIN=UNCHANGED`, `lineage.md=UNCHANGED`, `OWNER_PERMIT=NOT_GRANTED`.

## 4. Bước thực hiện tiếp theo — duy nhất

`TTM_SMALL4M_D1_R1_32_BLUEPRINT_CONSTRUCT_VALIDITY_AND_SEALED_EVAL_CUSTODY_DISTINCT_INDEPENDENT_SOURCE_REVIEW_SINGLE_GO_HOLD`

One independent source-only scientific review, treating all 32 public ASTs only as design blueprints; reject/adopt the new Boolean policy layer, decide whether it represents **genuine action-causal structural OOD**, and require separate sealed EVAL custodian/source rights and private, non-public gold before any science GO. If construct validity fails, HOLD whole R1 (do not subtly rename the public blueprints into TEST). No micro-permits, no rerunning completed QA.

## 5. Reproduction in clean Python 3.12 (source-only)

```powershell
$Py='C:\Users\minht\AppData\Local\Programs\Python\Python312\python.exe'
& $Py .\build_32_blueprints.py
& $Py .\independent_32_oracle_checker.py .\TTM_D1_R1_TYPED_32_SOURCE_BLUEPRINTS_20261114.json
# adversarial_32_source_qa.py requires networkx for the second opinion; it gracefully reports NOT_AVAILABLE otherwise
& $Py .\adversarial_32_source_qa.py
```

Each receipt includes SHA-256. Run in a separate verified worktree/`_tmp` only; no science execution or Git mutation is implied by the commands above.
