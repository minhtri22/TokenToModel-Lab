# TTM-Small-4M — EmbeddingGemma 2 Token-Embedding Replacement (Design + CPU Minimal Proof)

**Date:** 2026-11-09  
**Operation:** `TTM_SMALL4M_EMBEDDINGGEMMA2_TOKEN_EMBEDDING_REPLACEMENT_DESIGN_AND_MINIMAL_PROOF`  
**Status:** `PASS_CPU_SYNTHETIC_STRUCTURE_ONLY`; `REAL_DONOR_TRANSFER=NOT_EXECUTED`; `T4_CHECKPOINT_REAL_SWAP=NOT_EXECUTED`; `SCIENCE_NOT_EXECUTED`.

## Corrected research question

Replace **`self.tok` input token embedding** in TTM-Small-4M (P02), with *token-level* weights derived from the pinned Google **EmbeddingGemma 2** input embedding table. Do **not** build a BM25/embedding/Qwen RAG system. Do **not** equate EmbeddingGemma 2's 768d pooled vector with its 512d input token embedding. R1/R2/R3 G4 from the separate D1 line are deferred, original R_gold scientific PASS stays intact. No change to P00–P12, T1–T5, existing checkpoints or TEST.

## Exact current TTM-Small core

Source `src/p02/transformer_core.py`: Git blob SHA-1 `9762343e06cf800b50574c2871ae1ed58537fb18`, file SHA-256 `e0fcac285918b66b13c8f694e6d625a0691c9b59221b43043e63f46b25ddcc07`. Training config: vocab 2,048, hidden 256, layers 4, heads 4, context 256, trainable learned position, LayerNorm, 3,749,376 distinct tied parameters. `self.head.weight = self.tok.weight`; tying input and output is a **structural dependency**. P02 is frozen; this work uses a separate experimental wrapper, never edits the baseline class.

**Original T4 scientific checkpoint step 1024:** `cb985751795c8328ad65acf7ca4c1033ce35182c1bfbdb8c38550de629cb271b` SHA256, 45,074,891 bytes, private. Exact trained BPE tokenizer manifest SHA-256 `cba18e60cee3d08a353ee6d4a451017289e45af7b4b1179c87171b9b78d7dfdc`, private. Neither was fetched or altered during this CPU proof. Existing VAL/TEST scientific results remain intact. Original trained GGUF F32 and T5 llama.cpp numeric parity are not changed by this work.

## Exact EmbeddingGemma 2 scope

Official text configuration: **262,144** text token vocabulary, **512d** token hidden representation; final **768d** output is a contextual pooling/projected embedding, **not interchangeable** with per-position next-token input embedding. This experiment uses only the input token embedding table, **does not load donor encoder during TTM forward**, and retains TTM's original 2,048-ID byte-BPE tokenizer. The donor model is a separately trained bidirectional embedding system; it is not known a priori that transplanting its input rows improves autoregressive LM quality.

Pins from V3 original local SHA evidence:
- `google/embeddinggemma-2@f9972ac22e696a105c482202646979e33e4b5a1e`;
- `model.safetensors` SHA256 `197a32965d4b1105faf060417baa899e193fb73cd401f42ec9295234d5553d79`;
- `tokenizer.json` SHA256 `4d777ef5bdc1aa36227abdfb77c3e49e7b9c892d16e1b6bda41c393504828be4`;
- `config.json` SHA256 `b8f1e9931b57fbc054acdb445c41765d55b0074c58d145fa82839941ad1b5bb3`.

Documentation: https://ai.google.dev/gemma/docs/embeddinggemma/model_card_2 ; https://huggingface.co/docs/transformers/en/model_doc/embedding_gemma2 ; https://developers.googleblog.com/en/embeddinggemma-2-the-developer-guide/ .

## Proposed architecture: no decoder rewrite

1. Preserve original BPE 2048 IDs, positions, transformer blocks, and output vocabulary.
2. For each TTM byte-BPE token, reconstruct **raw bytes** from frozen GPT2 byte-to-unicode mapping. Decode strict UTF-8; unpaired byte fragments are **never replaced by U+FFFD**. For valid text tokens, tokenize using the pinned EmbeddingGemma tokenizer **with no BOS/EOS injection** and average native **512d INPUT embedding rows**. Detect/record one-to-many mapping and `all_special_ids`. Use original TTM row for missing/invalid cases and the explicit EOS token. Mapping's real coverage is **not yet known**.
3. Use frozen `[2048,512]` donor-derived source table and a **trainable** `Linear(512→256, bias=False)`; one offline *ridge alignment* initializes projection only from **frozen original TTM token embedding rows**, with no TinyStories TRAIN, VAL, or TEST samples. Alignment may limit donor novelty; it is a continuity initialization, not a science result.
4. **Untie the head**. Copy `head.weight` from the original trained checkpoint, keeping exact output logit vocabulary and preserving all original 4 transformer blocks and positional embeddings. The untreated copy is a separate untied control. Baseline with tied head remains untouched. Both input and output changes must be accounted for during later ablation.
5. No causal leakage: only a fixed TTM token-ID lookup feeds positions; donor contextual transformer outputs are not used. Strictly preserve special EOS fallback and sequence length.
6. The new candidate **is not GGUF-compatible without a new explicit tensor mapping/exporter**; do not run T5 parity tools on it as though it were an unmodified P02 checkpoint.

## CPU minimal proof performed — precise evidentiary status

- Local CPU used a **byte-for-byte frozen P02 source**, verified SHA256 and Git blob; no repo mutated locally.
- **Synthetic donor** `[2048,512]` (NOT real EmbeddingGemma weights), synthetic BPE ID sequences, no TinyStories, no actual TTM step-1024 checkpoint. Test controls: original model vs untied head logits identical exactly, swap has `[batch,seq,2048]` logits, finite loss, trainable projection backward, donor lookup frozen, EOS fallback equal to original, future-token isolation, original parameter values untouched, candidate state strict save/reload exact.
- The small independent offline negative QA suite checks bad dimensions, NaN, EOS mapping, UTF-8 partial byte fallback, injected special token, invalid donor IDs, insufficient rank and wrong source SHA.
- **`15/15` unit tests PASS** and **one structural CPU integration proof PASS**. This does not validate any actual donor mapping, checkpoint, performance, statistical superiority, or GPU use.

## Next lean step — one local real-weights integration, then meaningful comparison

Run `--mode real-build` **once** after supplying **existing exact pinned local files**: frozen P02 file, original real T1 BPE manifest, trained T4 step-1024 checkpoint and EmbeddingGemma 2 snapshot (exact SHA). No network, GPU, data split or TEST is needed to build the candidate. It reads donor safetensors directly and creates `candidate_initialization.pt` in a new output directory without touching originals. If old Colab cache was lost, do **not** blindly repeat the 1.5 GB download; first check existing local/Drive copies. The `real-build` path has not yet run and may reveal unsupported safetensors key/tokenizer edge cases: if so, fix those technical issues *inside the same preparation step*, not a chain of separate authorizations.

Only if real-build passes, compare baseline and swapped candidate on **identical TRAIN/VAL windows with a fixed, small, equal optimizer budget**. Include an *untied baseline control* to distinguish donor transfer from removing weight tying, and a random 512d donor initialization as a negative control if practical. Declare the scientific comparison protocol before reading new VAL results; never reuse sealed TEST. **TTM-Small T5 original deployment line remains higher priority**. Scientific result later needs independent adjudication; structural proof is never appended to scientific `lineage.md`.

### Reproduction (CPU only)

```powershell
$root = 'D:\WORK\RESEARCH\TokenToModel-Lab'
$feature = Join-Path $root 'tools\embeddinggemma2_swap'
& 'C:\Users\minht\miniforge3\python.exe' (Join-Path $feature 'test_embedding_swap_cpu.py')
& 'C:\Users\minht\miniforge3\python.exe' (Join-Path $feature 'ttm_embeddinggemma2_swap.py') --mode cpu-smoke --p02 (Join-Path $root 'src\p02\transformer_core.py')
```

No execution policy changes, no writes outside project and no automated GPU execution. Use the source from the successor branch and first check its exact SHA; the script refuses an unexpected P02 source.