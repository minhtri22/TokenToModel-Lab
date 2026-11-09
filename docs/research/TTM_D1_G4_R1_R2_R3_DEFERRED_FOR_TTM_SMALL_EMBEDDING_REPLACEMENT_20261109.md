# TTM D1 G4 — Deferred by explicit owner decision (2026-11-09)

**Decision:** `D1_G4_R1_R2_R3=DEFERRED` (**not** FAIL or abandoned forever).
**Owner direction:** The scientific objective was corrected: use EmbeddingGemma 2 to replace the TTM-Small-4M internal **token embedding** component `self.tok`, rather than evaluate EmbeddingGemma 2 as an independent retriever/RAG system.

## Effects
- STOP initiation of the previously prepared R1 BM25, R2 EmbeddingGemma retrieval and R3 Qwen-RAG Colab science run. Do not create or consume a new G4 CLAIM, spend GPU quota, rerun source preflight or continue the RAG workflow without a future explicit change of priorities.
- Preserve R_gold `PASS_RGOLD_SCREEN_SCOPED_SYNTHETIC` and its original CLAIM/RESULT, all five failed Exact Match rows, 60 group files, independent receipt adjudication and existing `lineage.md` L0011, unchanged. This deferred decision is **not** a scientific outcome and does **not** append lineage.
- Preserve G1–G4 prereg, source pins, data licenses, design documentation and code/QA handoff. No G4 R1/R2/R3 science result is claimed.
- **New task:** `TTM_SMALL4M_EMBEDDINGGEMMA2_TOKEN_EMBEDDING_REPLACEMENT_DESIGN_AND_MINIMAL_PROOF`.
- New isolated successor branch from the actively maintained TTM-Small pilot: `research/ttm-small4m-embeddinggemma2-token-swap-minimal-proof-20261109`.
- TTM-Small core baseline, frozen checkpoint/TEST, T5 parity work and draft PR #12 are not modified. No RAG GPU execution.
- Scope: structural CPU-only proof first; real Google EmbeddingGemma 2 token embedding mapping and any TRAIN/VAL improvement must be evaluated separately, not presumed.
- Decision timestamp: 2026-11-09. The owner did not request re-running R_gold, reopening TEST or any policy/permit micro-chain.

**Final status:** `D1_G4_R1_R2_R3=DEFERRED` · `R_GOLD=PASS_PRESERVED` · `SCIENCE_NEW=NOT_EXECUTED` · `EMBEDDING_REPLACEMENT=ACTIVE_DESIGN_AND_CPU_PROOF`.
