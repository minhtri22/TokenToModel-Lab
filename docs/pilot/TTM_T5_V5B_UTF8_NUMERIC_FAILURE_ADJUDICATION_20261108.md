# TTM T5 — Kết luận chẩn đoán V5B UTF-8 (2026-11-08)

**Kết luận:** `T5_TOKENIZER_UTF8_HEX=PASS_9/9`; `T5_F32_LOGITS_PARITY=FAIL_FROZEN_0.001` (7/8 cases), `TOP1_MATCH=8/8`. **Không sửa tiêu chí, không chạy lại bài parity đã tiêu thụ, không đụng TEST/TRAIN.**

## Nguồn gốc

- SHA256 report V5B: `ac699d4e750037f88bbab776bb42a38079cd82b0a1c2f72385127ac5a36d9375`; Git blob `6883f6e7de6279f7a7a50f22f027514e741cd758`; `evidence/pilot/t5-trained/T5_LLAMA_UTF8_V5B_ROOTCAUSE_DIAGNOSTIC_V1.json`.
- GGUF step1024 F32 `5bdc904e6c51af04a4223219f36e6bc2e687f60fd6e17dc24508f3eb7489e4e5`, checkpoint `cb985751795c8328ad65acf7ca4c1033ce35182c1bfbdb8c38550de629cb271b`.
- llama.cpp pinned commit `372dc5ca157276beb6c67b2e92477e8d662e964a`; V5B probe SHA256 `080c096d52448f665df43ebc962d7a62b17a0781326bc6358e8535d25f37c963`.
- Original technical parity receipt **unchanged** SHA256 `c61f73216764b8582a5c996e85c59feb55b13496ec0117deb713d9b1843ec8e8`: max abs `0.003362178805176086`, 2 tokenizer mismatches, 0 top1 errors.

## Measured results (identical frozen 8 ID and 9 string fixtures)

| Fixture | Tokens | Worst abs logit error | Threshold 0.001 |
|---|---:|---:|---|
| 0 | 1 | 0.000936508 | PASS |
| 1 | 3 | 0.001601696 | FAIL |
| 2 | 5 | 0.002269029 | FAIL |
| 3 | 4 | 0.001976013 | FAIL |
| 4 | 8 | 0.001823902 | FAIL |
| 5 | 16 | 0.001900882 | FAIL |
| 6 | 7 | 0.002775907 | FAIL |
| 7 | 32 | 0.003362179 | FAIL |

- UTF-8 hex tokenizer path: all 9/9 exact; formerly failing text examples `'a b'` and `'a\nb'` now exact. The earlier `cp1252` decode failure is removed in the new code (binary capture with explicit UTF-8); **the test does not isolate which change alone fixed those tokenizer mismatches**, so do not attribute both specifically to Windows encoding.
- Max abs exceeds fixed threshold by **3.36×**. Mean abs error varies by fixture; 8/8 argmax/top1 still match. This is not equivalence under the frozen full-logit criterion.
- The 4M model trained for 1024 steps on real TinyStories is **not retrained** by this diagnosis; original `L0011` H1 VAL PASS and `L0012` held-out TEST result stand unchanged. F32 exported GGUF 52/52 exact weight readback PASS remains true.
- `D:\WORK\llama3` was inspected by user and is `meta-llama/llama3` source commit `a0940f9cf7065d45bb6675660f80d305c041a754`, not llama.cpp; no GGUF probe discovered there. Do not substitute this path for pinned llama.cpp.

## One scoped successor — numerical localization, not another arbitrary permit

**`TTM_T5_F32_NUMERICAL_DIVERGENCE_LOCALIZATION_SINGLE_DIAGNOSTIC`**:

1. Preserve current trained checkpoint/GGUF, T2 pinned source/probe, 8 ID fixtures, old and V5B FAIL reports; do not rerun TEST, TRAIN or consumed original parity.
2. Compare intermediate PyTorch vs ggml/llama.cpp outputs at **embedding + position, layernorm, QKV, attention, GELU/MLP, final LayerNorm/head** for the *same fixed synthetic ID vectors*. Use a read-only one-session diagnostic; if the existing probe does not expose intermediate tensors, a separate derived debug probe/source may be needed, pinned without changing old compiled binaries.
3. Distinguish arithmetic/kernel accumulation drift versus wrong operation/parameter mapping, using exact F32 trained weights and independent fixtures. Do not arbitrarily raise `0.001` or select a favorable subset. If compatible implementation repair is indicated, implement in an isolated successor and run one full numerical parity comparison as a new result, preserving the original FAIL.
4. Ollama import/inference is a separate **compatibility** check only. Do not claim T5 PASS until it runs; import refusal cannot falsify T4 scientific H1.

**Status:** `T5_EXPORT=PASS`; `T5_UTF8_TOKENIZER=PASS`; `T5_FULL_LOGITS=FAIL`; `T5_LLAMA_PARITY=FAIL_PRESERVED`; `T5_OLLAMA=NOT_TESTED`. Engineering diagnostic → `docs`/`evidence`, not append-only scientific `lineage.md`.
