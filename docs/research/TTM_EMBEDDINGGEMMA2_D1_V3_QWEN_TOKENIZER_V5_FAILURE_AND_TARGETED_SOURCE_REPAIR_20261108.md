# TTM EmbeddingGemma 2 D1 — V3 tokenizer failure and targeted follow-up

**Date:** 2026-11-08  
**Verdict:** `V3_CONSUMED_FAIL_PRESERVED` · `EMBEDDING_FP32_TECHNICAL_PASS` · `QWEN_TOKENIZER_V5_SOURCE_BUG_IDENTIFIED` · `TARGETED_SOURCE_STATIC_QA_PASS_31_31` · `FOLLOWUP_NOT_EXECUTED` · `D1_D4_NOT_AUTHORIZED`.

## Grounded original V3 receipts

The private Google Drive folder `TTM_EmbeddingGemma2_D1_Preflight` contains two read-back exact files for `ttm_embedgemma2_d1_t4_preflight_st610_once_v1`. Keep both unchanged.

- `CLAIM.json`: 140 bytes, SHA256 `2ce14ab0c890a53042862c2b376ab12e2927c15ae1c1d1d3e9075f386b4a5999`.
- `RESULT.json`: 10,530 bytes, SHA256 `ce693326af246fdf2a3806427b46d89ce05e944a4c99e442b24004677e892427`.
- Status `FAIL_OR_BLOCKED_NO_SCIENCE`; duration `63.144` seconds; last error `RuntimeError: qwen_tokenizer_ids: FAIL: invalid tokenization`.
- Technical PASS steps: environment import, Tesla T4, disk and download budget, exact SQuAD validation digest, local model-file SHA256 measurement, deterministic SQuAD shape/selection, **EmbeddingGemma 2 FP32 vector sanity** (shape `[2,768]`, norms `[1.0,1.0]`, all finite; peak allocated reported `1097034752` bytes). No Qwen teacher-forcing numerical smoke completed.
- Dependency repair was successful: `sentence-transformers=6.1.0`, `transformers=5.22.1`. Both pinned model IDs/revisions and SQuAD manifest are unchanged.
- Original receipts state `science_executed=false`, `rgold_read=false`, `test_scored=false`, `adapter_training=false`.

## Root cause and corrective source change

Original V3 Qwen source:
```python
prefix_ids = tokenizer.apply_chat_template(messages, tokenize=True, add_generation_prompt=True)
if not isinstance(prefix_ids, list):
    record('qwen_tokenizer_ids','FAIL','invalid tokenization')
```
**Transformers 5 changed its default for `apply_chat_template`** to a dict-like `BatchEncoding` with `input_ids`; the V3 `isinstance(list)` assumption was invalid and yielded the reported FAIL. This is a notebook integration bug, not a verified Qwen checkpoint or GPU failure. Source: https://github.com/huggingface/transformers/blob/main/MIGRATION_GUIDE_V5.md .

Correct minimal source change:
```python
prefix_ids = tokenizer.apply_chat_template(
    messages, tokenize=True, add_generation_prompt=True, return_dict=False
)
```

The targeted follow-up also checks `return_dict=True` yields an `input_ids` sequence equal to the explicit list, preserving paired answer tokenization. No original scientific criterion changes.

## Repair delivery: reuse already downloaded Qwen, NO full V3 rerun

Conversation artifact (not GitHub-committed notebook):
- `TTM_EmbeddingGemma2_D1_T4_Qwen_V5_Tokenizer_Targeted_Followup.ipynb` SHA256 **`211b28bd190efeb1caa842720ebf33e5fe4191dad8c45c1a620fe3840e471dce`**, file 9,916 bytes.
- Same content Python source `TTM_EmbeddingGemma2_D1_T4_Qwen_V5_Tokenizer_Targeted_Followup.py` SHA256 `010f408a26d75eab21ecd3f662c4fcfee60650c8a5362684ed04928c2f6b3c43`.
- Static QA script and receipt: `TTM_EmbeddingGemma2_D1_Qwen_Followup_Static_QA.py` and `TTM_EmbeddingGemma2_D1_Qwen_Followup_Static_QA.json` — **31/31 PASS** including AST, source pins, no network, original SHA/CLAIM preservation, `BatchEncoding` mock negative/positive behavior and synthetic causal shift/loss mask check. Not an actual Colab inference test.

**Targeted follow-up RUN_ID:** `ttm_embedgemma2_d1_t4_qwen_tokenizer_followup_once_v1` — **new, distinct** from V1 and consumed V3. This is a corrective technical **component** test (not a new full preflight, not science), under the owner's already-granted permission to continue; it requires no additional owner approval.

One cell in existing **same Google Colab Tesla T4 runtime** with Drive mounted:
1. Read and SHA-check original V3 CLAIM/RESULT, verify EmbeddingGemma 2 preflight PASS. If missing or changed: STOP before any new CLAIM.
2. Read local pinned Qwen snapshot in `/content/ttm_embeddinggemma2_d1_preflight_st610_v1/hf_cache`; SHA-check downloaded weight/config/tokenizer vs prior RESULT. `HF_HUB_OFFLINE=1` and `TRANSFORMERS_OFFLINE=1`; if Colab reset has removed cache, STOP without downloading and without CLAIM.
3. Compare correct Qwen tokenizer list vs `BatchEncoding['input_ids']` **before** creating unique new follow-up CLAIM.
4. Reuse Qwen model already resident if present, else load it **only from existing disk cache**; run one synthetic teacher-forcing shift/mask/finite-loss check. No new downloads, no R_gold, R1/R2/R3, no Adapter, no TEST and no training.
5. Create **distinct** `...qwen_tokenizer_followup_once_v1_CLAIM/RESULT.json` in the same private Drive folder with exclusive creation. Never delete/rewrite prior files, and do not re-execute once CLAIM exists.

**Adjudication boundary:** If targeted Qwen smoke PASS, an independent reviewer may conclude **combined technical coverage** of original V3's PASS steps plus the Qwen component, explicitly labeled `SCOPED_TECHNICAL_PREFLIGHT_EVIDENCE`. Do NOT rewrite V3 status from FAIL to PASS, and do not claim D1 science authorization; record that the Qwen fix was a separate supplemental run. If targeted follow-up fails, preserve that new failure and STOP. This avoids wasting another download or re-running complete original preflight.

**Resource priority:** TTM-Small-4M T5 continues first. The follow-up is only possible if the user's existing Colab runtime with pinned cache remains available, and it consumes no new external model/dataset bytes. No other app or GPU substituted.

**Next:** Run **only the targeted follow-up notebook**, inspect its new RESULT in private Google Drive, independently verify paired V3 + Qwen receipts; decide `TECH_PREFLIGHT_COMBINED_PASS_SCOPED` vs `HOLD`. `D1_D4=NOT_AUTHORIZED`, `lineage.md` untouched for this engineering diagnosis.
