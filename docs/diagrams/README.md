# P00 technical diagrams

1. `01_gpt_like_architecture.(svg|png)` — architectural graph: input token IDs, byte embeddings, 2 Transformer blocks, causal attention, output logits.
2. `02_executed_inference_flow.(svg|png)` — reference demonstration flow: dense vs paged parity, autoregressive decode.
3. `03_kv_cache_mechanics.(svg|png)` — block tables and logical-to-physical KV page mapping.

The SVG files are the editable canonical schematics; PNG files are accompanying exports. These are explanations of reference code, **not** scientific performance plots. A paged kernel directly reading physical blocks has **not** been implemented or benchmarked. Inspect against `reference/phase0/` before publishing book figures.
