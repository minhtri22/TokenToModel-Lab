# C-M4 — Kiểm toán dữ liệu và cấu trúc phép đo (Data & Measurement Construct)

**Operation:** C_M4_DATA_AUDIT_MEASUREMENT_CONSTRUCT_AND_SFT_MASK_DESIGN_ONLY_ONEPACK
**Date:** 2026-11-16 · **Track:** C · **Status:** AUTHOR_SOURCE_REVIEW / SYNTHETIC_ONLY / EMPIRICAL_HOLD
**Repository baseline:** main f7a0a5874e8fd895c8ea8d17ceff393a4d4917a3; handoff C 0c072e71849ae4bdad416777acb738ff24fe1d74; Track C initial HEAD 666bc2c95ba21eaddcf8a0e3f8ed7cd906629de2.
**Boundaries:** No corpus/checkpoint fetch, model execution, existing TEST/FRESH16/FINAL24 rerun, merge or lineage change. No AI scoring. No independent adjudication is claimed.

## 1. Nguồn sự thật và mức độ bằng chứng

| Evidence | Exact source | Available conclusion |
|---|---|---|
| C handoff | docs/coordination/ttm-abc/TTM_TRACK_C_RESEARCH_SCALING_AGENT_HANDOFF_20261116.md @ 0c072e7 | Design scope; historical figures are **reported**, not recalculated here |
| Historical T4 | L0011/L0012 and docs/governance/ttm-post-q001/TTM_POST_P0A_Q001_EVIDENCE_GAPS_AND_NEXT_QUESTION_PRIORITY_MATRIX_20261116.md @ main baseline | VAL NLL 3.5223388517 vs bigram 3.9972314170; 11.880537% relative improvement; single seed, no semantic proof |
| Historical FRESH16 | Same priority matrix; design STEP3 @ branch research/ttm-small4m-incontext-probe-roadmap-design-20261116 | Poor scoped adherence; prior floor/provenance gaps, not proof of unique root cause |
| Step3/Step4/Step5 | docs/research/ttm-small4m-incontext-probe-roadmap/TTM_SM4M_ROADMAP_STEP[3/4/5]_... @ research/ttm-small4m-incontext-probe-roadmap-design-20261116 | Unreviewed, non-authorized candidate design, not a frozen protocol |
| P02/P03/P04 | src/p02/transformer_core.py @ blob 9762343e; src/p03/train_loop.py @ 80dc004a; src/p04/eval_checkpoints.py @ f047fcd3 | Working **synthetic** GPT core/training/evaluation contracts; NOT proof SFT loss masking supported by P02 |
| nanochat | karpathy/nanochat @ 92d63d4e8bb4df75c3b71618f31ddde2378b2bcd | Inspiration only, no transplant of H100 optimizations or unverified rights |

Main Git tree at Track C initial HEAD includes **no committed datasets/ directory** and no authorized access to private source shards or T4 tokenizer binaries. A live dataset audit, sample-level histogram, de-dup groups, split SHA-256 and tokenizer fertility **cannot be calculated** from this inventory. Recording a fabricated numerical histogram would be invalid.

## 2. Data manifest required for real audit (not fulfilled)

For each immutable source: source URI; exact upstream revision; license text/id; content SHA-256 & length; acquisition date; permitted actions separately for private reading, local training, local inference, third-party rating, derived checkpoints and public redistribution; owner attestor; PII/copyright investigation and disposition. TinyStories is **reported** as revision f54c09fd23315a6f9c86f9dc80f725de7d8f9c64 and CDLA-Sharing-1.0 label in candidate STEP5; this label is not an independent license determination and may not grant every action.

For each split: private manifest of stable story IDs, canonical UTF-8 hash, normalized hash, source-group identity, token-counts by tokenizer SHA, distribution of story lengths/domains/languages/typed entities and attributes, max context truncation, document-shingle near duplicates and cross-split leakage. Publish only aggregate counts and hashes, not source text, token reversible packs or sample-to-story mappings. **Near-duplicate review must use source grouping**, not only hashes: same source-family and paraphrase variants must remain in a single split. Train-only tokenizer proof: tokenizer train story IDs and SHA, excluding VAL/TEST/probe. A conservative audit should stop upon rights failure before opening bytes.

Historical numbers **reported, not independently recounted**: T4 3,749,376 parameters, 1,024 updates × 4,096 labels/update = 4,194,304 label exposures; ~498,287 TRAIN target positions from ~2,048 stories, reuse ~8.417. The estimated ~243 positions/story and ~768 tokenizer TRAIN stories are from proposed STEP4, and need actual source/manifest verification. Do not label positions as statistically independent observations. Histogram of actual token IDs = **NOT_AVAILABLE**, actual dedup groups = **NOT_AVAILABLE**, split SHA = **NOT_AVAILABLE**, tokenizer fertility = **NOT_AVAILABLE**.

A toy-only metadata checker in tests/ttm_track_c/synthetic_contract.py returns split counts, synthetic UTF-8 length bins, sample-set SHA-256 and exact/normalized duplicate alerts; never treat its toy counts as historical T4 data. For large datasets use a streaming private implementation, source-family clustering and a separately qualified near-dup method; toy checker is not a production corpus scanner.

## 3. Measurement matrix: no collapsed 'quality score'

| Construct | Primary observable | Positive/negative control | Invalidating failure |
|---|---|---|---|
| Next-token modeling | fresh held-out mean NLL, position/split documented; bpb only with valid UTF-8 byte attribution and special-token exclusion | known deterministic token distribution; shuffled-label control | leakage, same TEST reused, or denominator mismatch |
| Copy/induction | teacher-forced conditional log-prob/rank of a fresh target; nearest-string and random-init comparator | unique copied key vs mismatched key | token-span/alignment/length mismatch |
| Entity–attribute binding | exact slot ID or two candidate rank with correct gold | swapped entity/attribute (hard negative), oracle | fluent wrong entity passes |
| Counterfactual sensitivity | paired fresh prompts differing in one decisive fact; paired effect (not only accuracy) | flipped gold; irrelevant edit control | changed prompt length / gold drift without control |
| Instruction following | exact contract output schema, completion, stop and abstain | valid command vs contradictory/unknown context | judge rewards style over task |
| Decoding/repetition | deterministic repetition rate, termination and fixed seed/temperature/top-p | forced EOS, intentional repeat | inconsistent decoder or length caps |

**Five-level rubric** is a design fixture: K4 exact binding + concise form (4); K3 correct binding with harmless extras (3); K2 right entity/wrong attribute (2); K1 wrong fluent binding (1); K0 off-task/copy-only/loop (0). This ordinal rubric has not passed construct validation. **Machine gold first**: exact canonical slot/JSON schema and refusal/unknown contract, including explicit ambiguity and abstention. Gold must be source/fixture-derived **without** viewing candidate outputs; impossible or incomplete gold is REJECT, not a guessed UNKNOWN.

### Synthetic calibration design (not run on a model)
A prospective, rights-safe fixture could contain disjoint synthetic templates with controlled K0–K4 outputs, paired entity swaps, adversarial fluent-wrong K1 and repeated items. Assess positive/negative controls, per-item confusion, false positive for fluent wrong, oracle sensitivity, floor/ceiling, test-retest, rank monotonicity and clustered uncertainty by prompt-family. The 40×5+40 and numerical cutoffs in unreviewed STEP3 are examples, **not frozen thresholds**. A deterministic toy program proving its own own K4>K0 rule does not qualify an AI rater or prove generalization to model outputs.

**Failure states:** missing gold/source/parity => HOLD_CONSTRUCT; rater-visible exact bytes absent => HOLD_PROVENANCE; all arms at score zero or score ceiling => FLOOR_HOLD/CEILING_HOLD; same output judged for both arms by same single AI rater without blind sessions => HOLD_INDEPENDENCE; null difference and wide interval => INCONCLUSIVE (not equivalence). Predeclare target populations and family/item denominators, reject precedence and non-cherry-picked sample selection.

Human/AI raters, if eventually needed: independently sourced gold; blinded arm labels; isolated sessions; record SHA-256 of the **exact bytes as delivered to each rater**, including system/task/rubric/order/output payload; log gold access and disagreements; inter-rater agreement is supplementary to correctness. Never pass private data to a third-party rater without owner-scoped rights.

## 4. C-G1 / C-G2 provisional decision

- **C-G1 = HOLD_REAL_DATA_UNAVAILABLE**: only source/license label and historical figures inventoried; cannot claim a complete actual histogram/dedup/split audit.
- **C-G2 = DESIGN_PLUS_TOY_QA_ONLY**: propose construct and known-answer controls; actual endpoint readiness, floor discrimination on model outcomes and independent review are **NOT_EXECUTED**.
- T4 NLL is a useful bounded fact; FRESH16/FINAL24 floor effects and provenance gaps make them unsuited for retrospective model-selection outcomes. **No causal conclusion** on data vs objective vs capacity is presently licensed.

**Single blocker for empirical admission:** a defensible rights-scoped fresh evaluation + train/val manifest with real tokenizer/custody and qualified A endpoint (or independently valid replacement), not more paper-only approvals.
