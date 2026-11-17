# C-M5/M7/M8 — Ma trận data / objective / capacity / scale (proposed, NO RUN)

**Operation:** C_M4..._ONEPACK · **Status:** PROSPECTIVE_DESIGN_ONLY, NOT_PREREGISTERED, NO_GPU, NO_NEW_TEST.

## 1. Immutable baseline and denominator

Historical T4: 3,749,376 parameters; 1,024 steps × 4,096 target labels/update = **4,194,304 exposures per arm per seed**; ~498,287 unique TRAIN target positions, repeat ≈8.417. These are reported historical values, not from current byte access. One historical seed and one frozen checkpoint do NOT constitute a matched D0 rerun under a newly frozen protocol. 4,194,304 / 3,749,376 ≈ 1.119 observed target exposures per parameter; NOT unique tokens/parameter. Tokenizer trained on TRAIN only must be proved by exact manifest, not assumed from descriptions.

## 2. Decision order with interlocking controls

| Proposed arm | Manipulated factor | Held fixed | Primary comparison | Veto |
|---|---|---|---|---|
| D0 fresh | ~0.5M independent TRAIN label positions | T4 tokenizer, architecture, training exposures, loss, precision, decoder and schema | Compare with D1/D2 **prospectively**; old T4 as descriptive anchor | Rights/real corpus, split grouping, fresh endpoint |
| D1 | ~2.1M unique TRAIN label positions | Same as D0; seed-matched initialization/order | D1–D0 same total exposures | Source distribution drift, near-dup |
| D2 | ~4.2M unique TRAIN label positions | Same as D0; no fresh probes in TRAIN | D2–D1, dose trend | Tokenizer mismatch, corpus availability |
| O0 | NTP reference | Same **source items**, data exposure and measured FLOPs | Compare O1 | Stop if data/measurement invalid |
| O1 | Alternative objective, e.g. contrastive package | Same source and B checkpoint lineage, information and optimizer as feasible | Matched FLOPs or disclosed mismatch | Extra negative samples and pass cost cannot be ignored |
| P1/P2 | Parameter count ~16M, ~32M/64M | Data/objective and controlled budget | Quality vs compute with actual parameter and VRAM counts | Capacity unfit, no stable end-to-end B pipeline |

Estimated repeats 8.4 / 2.0 / 1.0 are rounded only; compute exact by counted unique source-target positions, per-seed sampler and exposure logs. Equal token **exposures** do not guarantee equal FLOPs or time. Do not mix validation selection into arm changes. Split by whole source story/family; freeze candidate/eligible/excluded denominators and hidden probe families in advance. Exclude TEST64, FRESH16, FINAL24 from training/tuning and prospectively constructed held-out results.

### Budget math (exposure count ONLY; not GPU quote)
- Three data arms × one seed: 3 × 4,194,304 = **12,582,912** supervised label exposures.
- Five-seed pilot proposal: **62,914,560** total; twelve-seed proposal: **150,994,944** total if twelve *total*, not additive. These numbers are **arithmetic planning**, not actual FLOPs or authorizations.
- Parameter-count and FLOP model must be computed from B's exact code and profiled GPU; \(6NT\) is a rough heuristic and may miss attention, loss-head, optimizer and contrastive cost.
- Required resource table per arm: exact N, context, activation dtype, B×T, grad accum, optimizer states, peak reserved/allocated VRAM, total/peak RAM, GPU-s, wall time incl. data loader & evaluation, measured FLOPs/tokens, interruption/restart semantics. NO such measured T4 budget is available in this onepack. Do **not** extrapolate nanochat 8×H100 throughput to a Colab T4.

## 3. Endpoint, power and stopping

**Primary proposed**: A-qualified or independently qualified fresh teacher-forced induction/copy and entity binding, gold NLL/rank under identical prompt/answer scoring. **Secondary**: fresh validated generation slot/format/stop/repetition, val NLL (not proof of instruction). Avoid mixing NLL with graded semantic score into one "success." Actual TEST is consumed. If paired data are all zero -> FLOOR_HOLD (fix construct, not train more).

Design for multiple independent seeds: pilot 5, confirmatory candidate 12, not frozen; select sample size using effect-size/power pilot from **separate** development data, not confirmatory outcomes. Pair seed ID across arms, report effect size and 95% CI with unit clustering (source family/prompt and seed). Wide CI crossing zero = INCONCLUSIVE, not equality. For dozens of probes, control multiple testing/hierarchy. Freeze sampling unit, eligible/rejected denominator, sampling RNG, stopping, exclusions, thresholds and checkpoint rule **before** observing arm outcomes.

**Decision logic:** If valid data-arm effect at matched compute -> prioritize data; if inconclusive -> HOLD rather than assume capacity; if data contrast valid and null with precise CI -> consider objective package; if objective contrast independently justified, only then capacity. Any architecture arm remains separate prereg+checkpoint schema version, no silent transforms.

## 4. Nanochat transport lessons and compatibility boundaries

nanochat pinned SHA 92d63d4e8bb4df75c3b71618f31ddde2378b2bcd: `scripts/base_train.py` measures token/data/compute, `nanochat/gpt.py` has FLOPs estimator, `runs/miniseries.sh` reports parameters/tokens/val bpb/time, `nanochat/optim.py` implements mixed MuonAdamW, `scripts/chat_sft.py` uses assistant loss mask. Transfer **measurement principles**, not claimed identical GPT math or speed.

One architecture arm per comparison: LayerNorm→RMSNorm; absolute embeddings→RoPE; GELU→ReLU² or SwiGLU separately; QK-Norm; GQA; MuonAdamW→AdamW or reverse as optimization arm. Schema/tokenizer and optimizer-state changes require exact compatibility checks and fresh training if needed. P02 RMSNorm exists as **optional** candidate, T4 used LayerNorm. Keep T5 strict-logit FAIL32/32 and GELU_ERF scoped PASS4/4 as historic bounded findings; **no universal GGUF parity claim**. KV and serving are post-quality: TTFT/TPOT, concurrency, stop, memory with model-specific parity; CPU synthetic paged KV is not GPU paged attention.

## 5. Gating and ownership

C-G3 is **DESIGN_ONLY**. C-G4 requires A-qualified measurement and B end-to-end trainer/metrics; C-G7 requires owner-scoped resource feasibility, C-G8 independent real result receipt. One integrated prospective experiment admission after rights/gold/compute/custody are resolved; no parser micro-permits, no automatic training or GPU. If real source rights or fresh qualified gold cannot be obtained -> **HOLD_SCIENCE**, continue only lawfully synthetic engineering.
