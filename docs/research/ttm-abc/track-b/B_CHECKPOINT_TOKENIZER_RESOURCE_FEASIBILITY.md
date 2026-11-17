# Agent B — Checkpoint, tokenizer, resource feasibility · ABC V4

**Operation:** `TTM_B_SHARED_EXACT_CHECKPOINT_TOKENIZER_RESOURCE_FEASIBILITY_AND_COMPATIBILITY_DESIGN_ONEPACK`  
**Mode:** `EXACT-SHA · SOURCE_ONLY · DESIGN_ONLY · NO REAL SFT · NO GPU · NO MERGE` · **Date:** 2026-11-17  
**Verdict:** `B_FEASIBILITY_MAPPING_COMPLETE_SCOPED` (mapping only), **global `HOLD_ABC_CONTRACT_ALIGNMENT`** pending C source-pointer correction, CCR-01 A/PM ACK, real weights/tokenizer/splits/native resource proof. This is not executable admission.

## I. Source custody (exact pinned immutable inputs)

| Authority | Exact commit | Direct Git blob/readback |
|---|---|---|
| PM ABC V4 unified contract | `403491b698ba6586193f2ff2ae00c4441c10c595` | `d7fbc02a45b1d1a85cfe9b9594ae88fee495a9e1` |
| A packet / 37-field requirements | `7639a53b9d76e16abfa4211cf239c5c3e9d6c940` | `A_TO_BC_REQUIREMENTS.md = 3de320f1e734c7610fb750477803b082fefff753` |
| C science packet / 26+14 registry | `614caff47657ccee43ad10ba06ae8ebb782b4114` | C document `a8c8f3ca898456519e82bcccb0ada73af24f6ff9`; C registry `64508ace4de057958ccbc9e3c7616a18c022250e` |
| B source PR #34 | `43896bcd034c82e8433bc6a2b53eefbd936616fb` | P02 `9762343e06cf800b50574c2871ae1ed58537fb18`, B scaffold `0d76d764097cd838f3fef9cb16c9da11ff778bb9` |
| B/C PR #36 | `09de6a46574146d863f416e056fcf01091f3efb8` | tested `a83e1526bce842761f3051dad28b90a55395a6aa`, bridge Git blob `c56d98b520fef387fab43bac87b7a9247287b17c` |
| Original T4 BPE implementation | PR34 ancestry | `tools/pilot_t4/integrated/source_t2/ttm_gpt2_bpe2048.py` blob `fa5bd892941ba5aa6e6b2f0b2b0ae974efe297b6` |
| T4 capacity, data pack, trainer | PR34 ancestry | `t4_capacity_smoke.py` `c9a6f256ba975228683ee7de2a1090e649110e97`; `t4_data_pack.py` `cdce219f2a2df27e25579f069238d4327c1d7d91`; `t4_train_science_a2.py` `76c4d0155cd0736919f41682f240b47ad3d7c428` |

GitHub Issue #32 [ABC_CONTRACT_ACK_B](https://github.com/minhtri22/TokenToModel-Lab/issues/32#issuecomment-6937885002) posted before authoring. All PRs remain Draft/unmerged. Source drift from PM original register is **expected A/C append-only packets**: A `e674... → 7639...`, C `00afd... → 614c...`; pinned, not silently substituted. A release ASCII, BC v2 UTF-8/LF, original T4 BPE source are **distinct byte and hash domains**.

**IMPORTANT field-reference defect:** At exact C packet SHA `614caff...`, machine JSON `sources.a_requirements_git_blob = 4f96452215778c3cca1af19bd6d2e3b6506d87d2` is **wrong**: this is A's `A_PM_EVIDENCE_INDEX_JOINT_COMPATIBILITY_20261117.json` blob. Actual `A_TO_BC_REQUIREMENTS.md` is `3de320f1e734c7610fb750477803b082fefff753`. C's 37 individual field refs and prose point to the correct blob. B does not edit C's JSON, apply checksum alias, or claim joint source alignment until C/PM reconcile.

## II. Model inventory — architecture is not a usable real checkpoint

| Item | Read from exact source | Verified claim / missing evidence |
|---|---|---|
| Decoder topology | `P02Config`: causal decoder; learned token/position embedding, LayerNorm/RMSNorm variants, qkv/proj attention, GELU MLP | **SOURCE_VERIFIED**. Original T4 chooses LayerNorm |
| T4 declared config | `vocab_size=2048, max_seq_len=256, n_embd=256, n_layer=4, n_head=4, norm_type=layernorm` | **SOURCE_VERIFIED** only; no newly loaded trained T4 weight bytes |
| Parameter count | weight tying `self.head.weight=self.tok.weight`; count 2048×256 + 256×256 + 4×789,760 + 512 = **3,749,376 unique trainable parameters** | **SOURCE_ARITHMETIC_MATCH** (not proof that supplied checkpoint carries these weights); tied output head does not add 524,288 independent params |
| Numeric modes | T4 candidate fp32/fp16, torch AMP and GradScaler only for fp16; trained precision selected by locked capacity decision | **SOURCE_DESIGN_ONLY**; actual selected T4 checkpoint dtype, version and device not evidenced here |
| Optimizer | historical T4 `AdamW` betas .9/.95, eps1e-8, weight decay .1, LambdaLR; step-specific model/opt/scheduler/sampler/RNG/GradScaler expected | Source contract; no real serialized optimizer-state readback |
| Historical model checkpoint | `ttm.t4.science.checkpoint.v1` with `model`, `science_lock_sha256`, `train_pack_sha256`, `p02_git_blob`; READY-last SHA | Schema **SOURCE_VERIFIED**, actual trained `checkpoint.pt` + bytes + SHA + read-only load STRICT **NOT_PROVEN** |
| B synthetic checkpoint | `ttm.track_b.synthetic.train_checkpoint.v1`, private run manifest claims SHA `f9e9e6ec5428d24a69841936779928617af858573a91f56dd9c43f5815798dcd` (979,357 bytes) | **HISTORICAL SYNTHETIC ONLY**; file not in inspected GitHub source; not a TinyStories or T4 trained checkpoint |
| B/C v2 checkpoint | `ttm.bc.synthetic.sft_checkpoint.v2`, `weights=NOT_CREATED`, `resume_enabled=false` | **INCOMPATIBLE with inference/training from actual weights**; metadata-only cannot be promoted |
| P02 default forward loss | `GPT.forward(tokens,targets)` invokes ordinary CE without `ignore_index=-100` | For SFT/padded labels must call **B masked `cross_entropy_valid`** on logits; reject direct unmasked P02 loss |
| Synthetic tested SFT | 2048 vocab, context32, n_embd32, n_layer1, n_head4 LayerNorm, zero optimizer steps | B/C engineering pass only; **not** T4 checkpoint, not model quality |

Native gated load in a *future separately authorized runner* must verify raw file bytes SHA, file length, model config hash, tensor name/shape/dtype/finite, tied embedding identity, tokenizer TRAIN manifest, optimizer/scheduler/sampler lineage, predeclared checkpoint step and identity, and no use of ambiguous pickles or metadata-only substitute. Unknown exact weight SHA stays `UNVERIFIED`.

## III. Tokenizer collision, raw-byte denominators and CCR

| Codec | Exact semantics from source | Compatibility |
|---|---|---|
| Historical T4 BPE | `ttm.gpt2.pretokenized.byte-bpe.2048.v1`, byte base tokens 0–255, `EOS=256`, **1791 BPE merges use IDs 257–2047**, regex GPT-2 pretokenization; TRAIN-only manifest raw file SHA `cba18e60cee3d08a353ee6d4a451017289e45af7b4b1179c87171b9b78d7dfdc` | Confirmed by source, actual TRAIN raw corpus and live tokenizer/weights not verified |
| BC/v2 synthetic SFT | content byte IDs 0–255, `EOS=256`, **`PAD=257,BOS=258,SYS=259,USER=260,ASSIST=261,EOT=262`** | Seven physical artifact SHA PASS engineering; all extra control IDs overlap T4 BPE merge IDs |
| Direct token-ID or state_dict reuse | IDs 257–262 have different meanings; 2048-ID T4 embeddings were trained for BPE merges, not v2 structural tokens | **INCOMPATIBLE**. Even a shape-compatible checkpoint is semantically invalid for direct v2 SFT without migration/retraining |
| Prospective compatible SFT approach | **Design alternative only**: keep original T4 BPE IDs and checkpoint **unaltered**, derive role masks from authenticated external span provenance and use separately frozen escaping/template and token-to-source-byte alignment; alternatively version new tokenizer/vocab and resize/remap embeddings with new checkpoint lineage | **ADAPTER_DESIGN_REQUIRED** + C/PM approval, byte offset, role-injection and boundary negatives; do not implement or silently relabel existing BC/v2 schema |

**SFT training target contract (BC v2 unchanged):** assistant genuine byte content + assistant EOT + final EOS supervised under masked CE; header/prompt/user/PAD ignored as *direct targets*. Nonzero prompt-context gradient is valid. **Separate C primary val_bpb view:** only genuine scored UTF-8 data-byte targets contribute to both numerator `sum_i(logsumexp(all_vocab_logits_i)-gold_logit_i)` (nats) and denominator `ln(2) × valid_data_bytes`; EOT/EOS/roles/PAD excluded from **bpb only**. This is **not** zero CE training stop loss. The B source supports this logical distinction but *real BPE byte-offset proof is absent*. B acknowledges **C-CCR-01 interpretation** as a scoped engineering design, pending A/PM ACK; never change 7-SHA BC v2 artifacts or A ASCII release.

For general BPE, a target token may emit 0/many UTF-8 bytes, and tokens can straddle excluded text/protocol spans. Every scored target needs exact `[byte_start,byte_end)` and trusted source span attribution; reject ambiguous overlap, gap, merges spanning split/mask boundaries. **Do not** replace bpb with NLL/token or divide by all token counts. NTP raw heldout bpb and SFT answer-only bpb are different estimands.

## IV. Data × Compute and timing provenance

**Historical source contract:** `1024 steps × 4096 valid supervised labels per step = 4,194,304 training label exposures`. A/C reports **about 498,287 independent TRAIN target positions** for the original T4 pilot; this is a *reported source-derived quantity*, not independently reconstructed from private corpus in this operation. Implied exposure/unique-position ratio is approximately **8.42**, and repeated exposures are **not new distinct independent data**.

**Planning 44M token hypothesis:** 44,000,000 / 4096 ≈ **10,742 steps** at historical target labels/step (not 1024), and still might not represent 44M **independent** target positions. Proposed D0≈0.5M/D1≈2.1M/D2≈4.2M independent TRAIN positions each require new eligible source/family manifests; the historical ~498k source cannot establish D1/D2. All new arm counts, seeds and equal measured FLOP budgets remain **NOT_FROZEN**.

**74-second timing claim:** no raw `device_id`/driver/precision/step-count/microbatch/clock/FLOP/profiling receipt for a 74-second result was found in the pinned A/C/B packet or source reviewed here. Thus `74s=REPORTED_UNVERIFIED`, not a certified time for 1024 steps or a real T4 science run. Likewise **13 minutes** for a larger run is an **unmeasured projection**, never `PASS_RESOURCE`. Need full latency definition: warmup, samples, input length, target mask, forward/backward/optimizer/eval/IO, GPU sync, GPU memory reserved/allocated, host RAM and abort/censored trials. T4 capacity script proposes fp32/mb2 and fp16/mb2/4/8 with warmup+timed steps and 25% overhead; a *script* is not the measured output.

Illustrative **non-gating analytical bounds**, not runtime evidence: fp32 3,749,376 params need ~14.30 MiB for weights; fp32 weights+gradients+two AdamW moments ~57.21 MiB, excluding activations, temporary tensors, optimizer implementations, CUDA contexts, allocator overhead, dataloader and checkpoint serialization. Rule-of-thumb ~6×parameters×exposures ≈ 9.44×10^13 FLOPs for this historical label-exposure quantity is **incomplete** and cannot certify equal actual compute (attention, context, padding, precision, objective extra passes, optimizer, losses). **Do not compare compute arms using exposures alone.**

## V. Future runner architecture and resource constraints — design only

A future owner-authorized candidate has ordered barriers: (1) exact source/rights/split/family and TRAIN-only tokenizer SHA, (2) safe read-only raw checkpoint/optimizer and model config SHA, (3) byte-span scoring mask/endpoint version, (4) OS+GPU/device+precision+driver/runtime preflight, (5) hard job-level RAM limit and bounded process-tree child cleanup, (6) T4 real VRAM fraction and measured worst-case trial, watchdog/timeout that kills child group, (7) no-overwrite atomic evidence with per-file SHA and source pin, (8) W1/W2 race/ancestor-rename and crash/reboot QA **before** real science, (9) signed A ReleaseTBSV4 + trusted policy_epoch, global Q001 frozen one-shot slot ledger/owner authority. **All are design requirements only here**; there is NO new runner and NO host test.

Proposed receipt evidence (namespaced PM index, not a new wire): executable+environment SHA, Windows Python3.12/Torch/CUDA/driver/runtime, GPU/VRAM telemetry, hard Job Object flags/limit/peak readback, clean shutdown and child-exit status, test seeds and source/roles/byte hash, step-level true valid labels, unique positions and exposure count, measured synchronized FLOPs/clock and memory, stop reason, READY-last checkpoint file SHA and independent readback, separately A RAW/TAG/ledger provenance. Fail closed on missing capacity/rights/custody and especially after ambiguous one-shot claim. No `Job Object PASS` transfer from original B-M3 to new study.

**Source-only vs native security:** B/C `is_symlink()/is_file()` provides pathname checks, **not** atomic opens, resistant Win32 junction/reparse traversal, file-ID handle ancestry or TOCTOU proof. A V4 requires trusted HANDLE-relative rename, no replacement, durable final bytes and identity at linearization; B must not modify A `ReleaseTBSV4` or its RAW/TAG hash domain. Owner native gate stays HOLD.

## VI. Distinct negative QA plan (NOT_EXECUTED)

| Case | Failure oracle |
|---|---|
| B-NEG-01 fake `*.pt` metadata as actual weights | HOLD_WEIGHT_CUSTODY before any model load |
| B-NEG-02 same 2048 vocab but wrong 257–262 semantics | INCOMPATIBLE_TOKEN_ID_MAP |
| B-NEG-03 BPE merged token crosses excluded EOT/answer byte mask | HOLD_BYTE_DENOM |
| B-NEG-04 assistant EOT/EOS missing from SFT training CE | HOLD_MASK_CONTRACT |
| B-NEG-05 EOT/EOS counted into byte-only bpb | HOLD_BYTE_DENOM |
| B-NEG-06 nonfinite/candidate-only logits or wrong +1 shift | HOLD_SCORE_ORACLE |
| B-NEG-07 repeated sampled target counted as unique TRAIN position | HOLD_EXPOSURE_CUSTODY |
| B-NEG-08 proposed 44M/13min from historical unpinned 74s | HOLD_RESOURCE_EVIDENCE |
| B-NEG-09 memory hard-cap absent, child survives timeout | HOLD_NATIVE_RESOURCE |
| B-NEG-10 symlink/junction/ancestor swap between check and file read | HOLD_TOCTOU |
| B-NEG-11 competing same Q001 slot, ambiguous crash retry | HOLD_OWNER_AUTHORITY |
| B-NEG-12 old A ASCII RAW/TAG hash replaced by BC UTF-8 checksum | HOLD_BYTE_DOMAIN |
| B-NEG-13 source C machine JSON wrong A requirements blob ref | HOLD_SOURCE_REF_CONFLICT |

No model training, logits, GPU, native fault injection, real corpus or historical TEST is run in this operation. Separate negative group proposals are NOT scientific evidence.

## VII. Open integrated blockers (no micro-permits)

**B-F01** actual trained T4 weights+config/optimizer+tokenizer byte-custody `NOT_PROVEN`. **B-F02** BPE↔BC special ID direct map `INCOMPATIBLE` — prospective adapter contract belongs to C/PM. **B-F03** byte-offset scorer/val_bpb `ADAPTER_DESIGN_REQUIRED`. **B-F04** C/rights/family/gold/fresh heldout `HOLD_C_SOURCE`. **B-F05** latency 74s and 13min/44M real feasibility `NOT_PROVEN`. **B-F06** new hard RAM/VRAM/Job Object/native race/crash proof `HOLD_RESOURCE`. **B-F07** A V4 owner signer/ledger release `HOLD_OWNER`. **B-F08** C machine JSON points to wrong A requirements blob `HOLD_SOURCE_REF_CONFLICT`. **B-F09** CCR-01 A/PM ACK incomplete `HOLD_CONTRACT_ALIGNMENT`. Existing B-M3 PM engineering PASS with V3 native HOLD and reviewer peak-dissent is preserved, does not certify a new run.

**Disposition:** B feasibility mapping is complete as **source/design work only**; final ABC alignment is `HOLD_ABC_CONTRACT_ALIGNMENT`. One consolidated PM adjudication must resolve the BPE/SFT semantic alternative, C source pin, CCR-01 and source/owner resource blockers without authorizing I2, SFT, GPU or TEST.
