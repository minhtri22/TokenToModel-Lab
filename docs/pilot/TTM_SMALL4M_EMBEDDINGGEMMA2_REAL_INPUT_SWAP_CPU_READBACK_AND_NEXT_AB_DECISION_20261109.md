# TTM-Small-4M × EmbeddingGemma 2 — tích hợp thật, QA và quyết định đánh giá tiếp theo

**Ngày:** 2026-11-09. **Loại:** kỹ thuật, không phải phán quyết khoa học. **Kết quả:** `PASS_REAL_DONOR_INTEGRATION_ONLY_NO_TRAIN_NO_VALIDATION`; **đối chiếu CPU độc lập:** `PASS_INDEPENDENT_CPU_RELOAD_STRUCTURE_ONLY (20/20)`. Không sửa checkpoint gốc, không huấn luyện mới, không đọc VAL/TEST, không dùng GPU trong QA độc lập.

## Bằng chứng bất biến

- Folder Drive: https://drive.google.com/drive/folders/1cB75QWqTdlJZ_UvE-yzM1MiSydc__6Gv
- [PROOF_RESULT.json](https://drive.google.com/file/d/15slxwQ25GXoQn92a5zxXLT9xEbbeW6yk/view): SHA-256 `e4e98a2d16ebac43623e29d1ed99c5fe87945fa1d633e768eb21cc75875ef700`.
- [PROOF_READBACK.json](https://drive.google.com/file/d/1wsXdlY13t4fAqXHLazb_JN0Lo5sXiED2/view): SHA-256 `53132eeafd89be785412583cea036910a10517b0d03786b2eea0373ddf455f0b`.
- [candidate_initialization.pt](https://drive.google.com/file/d/1nuaL5lxkGhGkffJUnTegdS9tKA-H-13A/view): 21,835,865 B, independently rehashed SHA-256 `c9fc798d8880c7e76636258052e9885dbb086d7b462a5b6bee5cff8b582973c3`; not committed to GitHub.
- Original trained [checkpoint.pt](https://drive.google.com/file/d/1F4kaaaC7w3MVPyPFoFa4BpGyWu0LLLme/view): 45,074,891 B, independently rehashed SHA-256 `cb985751795c8328ad65acf7ca4c1033ce35182c1bfbdb8c38550de629cb271b`.
- P02 code SHA-256 `e0fcac285918b66b13c8f694e6d625a0691c9b59221b43043e63f46b25ddcc07`; source bundle SHA-256 `bce8ffa8bc954d7f1ba87b08c033e6e8c3dbc925be39cc4b78ef90b6d66a026e`. Source is pinned on same research branch.
- TTM tokenizer manifest SHA-256 `cba18e60cee3d08a353ee6d4a451017289e45af7b4b1179c87171b9b78d7dfdc`; donor revision `f9972ac22e696a105c482202646979e33e4b5a1e`; donor `language_model.embed_tokens.weight` SHA256 `197a32965d4b1105faf060417baa899e193fb73cd401f42ec9295234d5553d79` (file hash).
- Bảng token donor-mapped `2048×512`, `valid=1917` = **93.6035% vocabulary types**. Fallback `130` incomplete UTF-8 + `1` EOS. `50` mapped tokens use multiple donor IDs. Không suy ra coverage theo tần suất token trong corpus.
- Output head `2048×256` đã untie; projection `256×512`. Baseline-vs-untied logits **bitwise identical** khi nạp lại. Candidate logits shape `[2,6,2048]`, finite, future-token isolation PASS. Original Colab max|Δlogit| = `4.485944747924805`; QA CPU độc lập = `4.485945701599121` (difference `9.5367431640625e-7`), within cross-runtime FP32 tolerance `1e-5`; strict `1e-7` threshold was too stringent for cross-runtime numeric comparison.
- **20/20 structural/readback checks PASS.** No inference on accuracy/NLL improvement, no embedding semantics validation, no proof from human blind TEST.

## Technical adjudication

`REAL_INPUT_EMBEDDING_SWAP=PASS_STRUCTURAL` and `VALIDATION_NLL_IMPROVEMENT=NOT_MEASURED`. The adapter is ridge aligned *to the original trained TTM embedding table*; it can imitate or perturb the pretrained original geometry, so 93.6% mapped types or large logits delta cannot be interpreted as transfer benefit. Key distinction: type coverage is not corpus-token frequency coverage.

This engineering receipt is preserved in docs rather than appended to scientific `lineage.md`. RAG G4 remains `DEFERRED` and the prior scientific R_gold result remains intact.

## Single next experiment: short A/B without training

Before any extra GPU or 1024-step retraining, recommend a **one-pass CPU-only frozen VAL NLL A/B** on the *existing pinned private TTM TRAIN/VAL pack*, no TEST, no new corpus or tokenizer downloads:

1. **A** original trained checkpoint step 1024 (tied output);
2. **B** exact untied-output clone (negative engineering control, should match A);
3. **C** same checkpoint with actual Gemma-mapped input embedding and initialized ridge adapter (candidate).
4. If C looks favorable, a **random donor embedding control D** with identical mapping mask/adapter capacity becomes mandatory before attributing gains to pretrained Gemma semantics. It is preferable to include D in the same frozen run rather than add it after looking at outcome.

Use identical VALIDATION windows, masks, token weighting, forward dtype and no tuning or selection on TEST; report token-weighted NLL, delta C−A, confidence interval by story if metadata supports it, and frequency-weighted token mapping coverage. A worse frozen-init NLL does not by itself refute the potential benefit of a *matched-budget fine-tuning* comparison. **Do not auto-run that next science**; establish the comparison contract once, then execute by explicit owner action, with TTM-Small T5 priority.

**Final:** `SWAP_REAL_STRUCTURAL=PASS` · `INDEPENDENT_CPU_QA=PASS_20/20` · `SCIENCE_NLL=NOT_EXECUTED` · `VALIDATION=NOT_READ` · `TEST=UNCHANGED` · `G4_RAG=DEFERRED`.
