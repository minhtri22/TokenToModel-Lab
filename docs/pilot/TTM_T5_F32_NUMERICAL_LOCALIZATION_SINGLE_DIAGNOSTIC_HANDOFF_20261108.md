# TTM T5 — Single numerical divergence localization: exact-source handoff (2026-11-08)

**Status:** `SOURCE_PREPARED_STATIC_QA_PASS` · `NATIVE_LLAMA_INTERMEDIATE_CAPTURE=NOT_EXECUTED` · `T5_FULL_LOGITS=FAIL_PRESERVED` · `T4_TRAIN_AND_TEST=UNCHANGED` · `OLLAMA=NOT_EXECUTED`.

## Existing ground truth (must not be rewritten)

- Frozen trained checkpoint step 1024 SHA256 `cb985751795c8328ad65acf7ca4c1033ce35182c1bfbdb8c38550de629cb271b`.
- GGUF F32 SHA256 `5bdc904e6c51af04a4223219f36e6bc2e687f60fd6e17dc24508f3eb7489e4e5`, trained 52 F32 tensor readback PASS.
- Pinned llama.cpp source `372dc5ca157276beb6c67b2e92477e8d662e964a`. `D:\WORK\llama3` contains **Meta llama3**, not llama.cpp.
- Original T5 parity FAIL preserved. V5B UTF8/hex follow-up: tokenizer 9/9 PASS, 8/8 top1 equal, **7/8 full-logit max abs >0.001**; max `0.003362178805176086`; report `evidence/pilot/t5-trained/T5_LLAMA_UTF8_V5B_ROOTCAUSE_DIAGNOSTIC_V1.json`.
- Previous numerical acceptance rule `max_abs<=0.001` is unchanged. The separate diagnostic sensitivity `1e-5` is for localization only and **cannot be used as PASS acceptance**.

## Prepared single Windows diagnostic

Exact ZIP created in current chat (not yet committed individually as source files): `TTM_T5_F32_NUMERIC_LOCALIZATION_SINGLE_20261108.zip`, **SHA256 `dc57a5fc5168d44c8bfe98e259365f8f232083896ec25bc75f1973a5e8dbb5a6`**, 15,384 bytes, 7 members, all six source-member hashes verified against embedded manifest. Contains C++ debug-only GGML scheduler callback probe, PyTorch-vs-ggml 35-stage comparator, PowerShell 5.1 one-shot launcher, local unit QA and README.

This diagnostic is explicitly scoped to the **same 8 frozen synthetic ID arrays**. The debug probe links the preexisting pinned `llama.lib`, `ggml.lib`, `ggml-base.lib` and uses the preexisting llama/ggml DLLs. It does not modify compiled T2 probe/source or export/rewrite the original trained GGUF. It observes callback tensors from the real llama.cpp GPT-2 graph at:
`inpL` (token+position embedding), and for each of blocks 0–3 `attn_norm, wqkv_b, ffn_inp (attention+residual), ffn_norm, ffn_up_b, ffn_gelu, ffn_out, l_out`, followed by `result_norm, result_output`. This yields **35 stage names** for each of 8 fixtures. A reference trace is computed from the **actual trained checkpoint** using frozen P02 code; an alternate GELU-tanh reference is diagnostic-only, without modifying checkpoint weights.

**Preflight actually executed in the assistant's CPU container**:
- Real checkpoint SHA verified and loaded via `weights_only=True`, `step=1024`.
- P02 trace completed 8/8 fixtures × 35 stage names, with bitwise agreement at final logits against frozen `model.forward()`.
- Synthetic no-error traces and negative tests for missing/corrupted stage PASS.
- Debug C++ passed C++17 syntax/shape check **against local API stubs**. **Not** a compiled/tested probe against the user's Windows llama.cpp headers/DLLs.
- Preliminary math sensitivity: swapping PyTorch GELU exact to tanh changes final logits by order 0.0008–0.0029 for these fixtures. This is **not a causal root-cause determination**, because the backend's intermediate tensors have not yet been captured.

## Runtime and failure boundary

On the user's Windows machine, extract exactly this ZIP into Downloads. Invoke `Run-TTM-T5-F32-Numeric-Localization-PS51.ps1 -Mode Preview` once; it is read-only and SHA-checks previous receipts, original trained checkpoint, GGUF, pinned old compiled DLLs, and package sources. On PASS invoke `-Mode Diagnose` **only once**. The script writes `CLAIM.json` and builds a debug probe under `D:\WORK\RESEARCH\TokenToModel-Lab\_tmp\ttm_t5_numeric_localization_v1`, captures numeric tensors and writes `T5_F32_NUMERIC_LOCALIZATION_UNADJUDICATED.json`. All intermediate traces stay project-local and should not be committed to public GitHub.

If compilation, graph capture or tensor shape fails, preserve `STOP_KEEP_ALL_EVIDENCE_NO_RERUN.json` and do not claim a measured numerical cause or automatically retry. If captured final logits differ from the prior pinned probe max by >0.00015, report `INCONCLUSIVE_DIAGNOSTIC_BACKEND_BASELINE` rather than claiming localization.

**Decision remains HOLD for backend change** until the one native callback report is read back; no modification to frozen threshold, T4 TRAIN/TEST, checkpoint, GGUF, or scientific `lineage.md`. Existing PR #12 DRAFT and `main` remain unchanged.

**Next:** `TTM_T5_F32_INTERMEDIATE_NATIVE_SINGLE_EXECUTION_AND_INDEPENDENT_READBACK`. If native results localize an early discrepancy, choose a scoped backend-only fix or document incompatibility, retaining the initial FAIL.
