# TTM — EmbeddingGemma 2 D1: Independent receipt audit of consumed T4 preflight v1

**Work item:** `TTM_EMBEDDINGGEMMA2_D1_T4_PREFLIGHT_V1_CONSUMED_FAIL_INDEPENDENT_RECEIPT_AUDIT`  
**Date:** 2026-11-08  
**Verdict:** `RECEIPT_INTEGRITY=PASS_STRUCTURAL_READBACK` · `PREFLIGHT_V1=FAIL_ENV_COMPATIBILITY` · `ONE_SHOT_V1=CONSUMED` · `SCIENCE_NOT_EXECUTED` · `D1_D4=NOT_AUTHORIZED`.  
**GitHub:** `minhtri22/TokenToModel-Lab`; branch `research/ttm-gemini-embedding2-gqa-pagedattention-feasibility-design-20261108`.  
**Authority limitation:** this is a separate ChatGPT read/structural audit of user-produced Drive receipts, *not* an independent local execution, hardware attestation, or outside human peer review.

## 1. Original receipts, byte preservation, and one-shot status

The two ORIGINAL JSON receipts are preserved in the user's private Google Drive folder `TTM_EmbeddingGemma2_D1_Preflight`, not copied into this public repository. The connector returned both original byte files for read-only examination. IDs and names match exactly; `CLAIM` precedes the terminal `RESULT`.

| File (original Drive name) | Bytes | SHA-256 of exact downloaded bytes |
|---|---:|---|
| `ttm_embedgemma2_d1_t4_preflight_once_v1_CLAIM.json` | 134 | `da0444b0836d0e4f2aee7f4237bc59033db679dda24d053c03bfb287ca118114` |
| `ttm_embedgemma2_d1_t4_preflight_once_v1_RESULT.json` | 9,557 | `60238e27682d43c84242b5f4138fef23b00e8f71cc77ca623796461a6c3978de` |

- Same `run_id=ttm_embedgemma2_d1_t4_preflight_once_v1`.
- `CLAIM.time_utc=2026-11-08T16:48:09.431052+00:00`; `RESULT.started_utc=2026-11-08T16:48:09.431052+00:00`, `ended_utc=2026-11-08T16:49:33.340715+00:00`, `elapsed_seconds=83.91`.
- The structured RESULT flags `science_executed=false`, `rgold_read=false`, `test_scored=false`, `adapter_training=false`, and status **`FAIL_OR_BLOCKED_NO_SCIENCE`**.
- The CLAIM exists; **v1 is consumed, no restart/re-run/overwrite/deletion of its CLAIM, RESULT or run ID**. The model downloads are real technical consumption despite no scientific experiment.
- The screenshots agree with RESULT's status and private Drive file names. Screenshots alone do not prove steps or error; conclusions below come from original JSON.

## 2. Actual PASS steps (7/7 before fail) and boundaries

| Step | Original status | What it does and does not establish |
|---|---|---|
| `dependency_import` | PASS | Imports installed packages but **does not validate model-required minimum version** |
| `colab_tesla_t4` | PASS | Tesla T4 detected, GPU reported 15,637,086,208 total bytes; **not** model inference |
| `disk_preflight` | PASS | Free 120,765,468,672 bytes before download; no after/peak report |
| `planned_download_budget` | PASS | Planned 2,527,234,642 bytes, within proposed 5-GiB download bound; not measured final network transfer quota |
| `squad_exact_digest` | PASS | Validation Parquet downloaded byte SHA-256 **equals prereg remote expected SHA** `8c6646d36bd5a95061e076788cf3161d11f6f3e7d625dac7a83bbed0a49f69f7` |
| `model_file_sha256` | PASS | Per-file SHA-256 and sizes **calculated** for both pinned model snapshots; **not** shown as independently matched to remote expected digests |
| `squad_shape_and_selection` | PASS | Script reported 10,570 rows, 2,067 unique passages, 48 source-article groups, 144 selected queries |

`SQUAD_SELECTION_MANIFEST_SHA256=d63b70da106884589b97efa860a9d1174cb72186bfea9e4427bcdbfb69178651`. This reported digest is recorded, **not independently recomputed from raw parquet** in this audit. The user did not authorize scoring; Hit@k/MRR/answer-NLL all remain unexecuted.

**Model snapshots:** `google/embeddinggemma-2@f9972ac22e696a105c482202646979e33e4b5a1e`, `Qwen/Qwen2.5-0.5B-Instruct@7ae557604adf67be50417f59c2c2f167def9a775`. Main weights hashes **observed in original receipt**:
- Google `model.safetensors`: 1,488,915,288 bytes, SHA-256 `197a32965d4b1105faf060417baa899e193fb73cd401f42ec9295234d5553d79`.
- Qwen `model.safetensors`: 988,097,824 bytes, SHA-256 `fdf756fa7fcbe7404d5c60e26bff1a0c8b8aa1f72ced49e7dd0210fe288fb7fe`.
These are receipt-reported hashes; external independent byte verification is not claimed.

## 3. Exact error and source-level localization

Original `RESULT.error`:
```json
{
  "type": "ModuleNotFoundError",
  "message": "No module named 'sentence_transformers.base.modules.normalize'"
}
```

Runtime receipt:
- Python `3.13.16`; `torch=2.14.1+cu130`; `transformers=5.22.1`; `sentence-transformers=5.7.0`; `huggingface_hub=1.33.0`; `pyarrow=23.0.1`; `numpy=2.4.6`; CUDA `13.0`.
- The pinned EmbeddingGemma 2 model's `config_sentence_transformers.json` declares creation/runtime requirement `sentence-transformers>=6.1.0`; its `modules.json` lists `sentence_transformers.base.modules.normalize.Normalize`. The installed `5.7.0` fails on that module path; `dependency_import=PASS` is inadequate. Official library docs explicitly recommend `sentence-transformers>=6.1.0` for EmbeddingGemma 2.
- The original V2 preflight source attempts `SentenceTransformer(..., config_kwargs={"vision_config":None,"audio_config":None}, ...)` only **after** 7 PASS receipts, and catches an exception there. The downloaded weight-loading progress in Colab is **not** evidence of successful complete model initialization, finite FP32 embeddings or correct semantic retrieval.
- No basis to attribute this to a defective EmbeddingGemma checkpoint, failed model science, Qwen competence, or insufficient T4 memory. No need to alter G1–G4 prereg.

**Source references:** https://huggingface.co/google/embeddinggemma-2/blob/main/config_sentence_transformers.json ; https://huggingface.co/google/embeddinggemma-2/blob/main/modules.json ; https://huggingface.co/docs/transformers/model_doc/embedding_gemma2 ; https://github.com/huggingface/sentence-transformers/releases/tag/v6.1.0 . The exact downloaded source snapshots are already tied to recorded revisions by the original receipts.

## 4. Constrained next correction: design/static QA only, NO new run yet

`TTM_EMBEDDINGGEMMA2_D1_ST610_COMPATIBILITY_SOURCE_ONLY_REPAIR_AND_INDEPENDENT_STATIC_QA`

**One integrated technical repair proposal (not a micro-permit):**
1. Preserve v1 CLAIM/RESULT and every SHA; do not reuse v1 run ID or silently claim PASS.
2. In a future successor notebook's **non-claiming setup**, pin `sentence-transformers==6.1.0` or an independently reviewed compatible version (minimum 6.1.0), and validate installed package version with `importlib.metadata.version` + semantic version comparator **before CLAIM**. For model-module loading, check the pinned `modules.json` import paths against the installed package (not just `import sentence_transformers`).
3. Review compatible versions of `transformers`, PyTorch, Python, `tokenizers` for that notebook. Avoid an unbounded `pip install -U` altering the T4 environment, and avoid patching the model's pinned modules/config to bypass the check. Keep EmbeddingGemma2 **FP32 on T4**, text-only configuration, frozen Qwen, source hashes and R1–R3 prereg unchanged.
4. In the static QA, verify one-shot claim is still **created only after** setup/version/hardware/resource checks; receipt includes stage, stack (sanitized), environment, and original failure provenance; every failure remains terminal. For model-file integrity, clarify local SHA measurement vs comparison against remote expected hash; never overclaim independent remote verification.
5. **No rerun is authorized now**. Only after source-only QA passes, owner can decide **one successor technical attempt with a new, explicit run ID**, narrow hardware/budget, a fresh claim; no scientific R_gold or D1 executed. Reuse existing cache only after exact hashes and authorization; no old CLAIM/RESULT modification.

## 5. Governance and resource priority

`ORIGINAL_V1_ONE_SHOT=CONSUMED_FAIL` · `ROOT_CAUSE=ST_5_7_LT_REQUIRED_6_1` · `PREFLIGHT_PASS=NO` · `R_GOLD=NOT_EXECUTED` · `R1_R2_R3=NOT_EXECUTED` · `D1_D4=NOT_AUTHORIZED`. 

**TTM-Small-4M T5 remains priority.** Its T4 real science and held-out TEST results are not impacted. Do not change `lineage.md`: this outcome is technical/infrastructure QA FAIL, not a scientific hypothesis test. Keep the original files private in Drive; public GitHub gets only this sanitized receipt adjudication. 

**Bước thực hiện tiếp theo:** `TTM_EMBEDDINGGEMMA2_D1_ST610_COMPATIBILITY_SOURCE_ONLY_REPAIR_AND_INDEPENDENT_STATIC_QA`. Preserve one-shot, design no-science successor (no authorized execution) and a single combined independent QA of repair and admission boundaries, rather than repeating G1–G4 or re-opening science.
