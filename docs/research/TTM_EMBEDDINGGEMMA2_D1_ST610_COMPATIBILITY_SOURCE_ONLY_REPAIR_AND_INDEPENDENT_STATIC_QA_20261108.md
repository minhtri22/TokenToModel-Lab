# TTM EmbeddingGemma 2 D1 — ST6.1.0 source-only repair and independent static QA

**Work item:** `TTM_EMBEDDINGGEMMA2_D1_ST610_COMPATIBILITY_SOURCE_ONLY_REPAIR_AND_INDEPENDENT_STATIC_QA`  
**Date:** 2026-11-08  
**Verdict:** **`PASS_SOURCE_ONLY_NO_EXECUTION`** · `STATIC_QA=PASS_79_OF_79` · `NEW_RUN=NOT_EXECUTED` · `D1_D4=NOT_AUTHORIZED`  
**Scope:** Notebook source repair + offline static QA only. No pip install, Colab, GPU/model load, model/dataset download, R_gold, R1/R2/R3, TEST, training, merge or changes to `lineage.md`. `main`, TTM-Small T4/T5 PR #12 and P00–P12 unchanged by this task.  
**GitHub branch:** `research/ttm-gemini-embedding2-gqa-pagedattention-feasibility-design-20261108`.  
**Previous source/head:** `df03966ae1c9b8a0c100d86c3ebb0d935b6fe9bc` (V1 independent receipt review).  
**Primary prior result:** `TTM_EMBEDDINGGEMMA2_D1_T4_PREFLIGHT_V1_CONSUMED_FAIL_INDEPENDENT_RECEIPT_AUDIT_20261108.md`.

## 1. Original V1 is consumed; original bytes and failure unchanged

`RUN_ID_V1=ttm_embedgemma2_d1_t4_preflight_once_v1`. The original private Google Drive receipts, independently read in the prior audit, show `FAIL_OR_BLOCKED_NO_SCIENCE` at the model loader, caused by `ModuleNotFoundError: No module named 'sentence_transformers.base.modules.normalize'`. The runtime was ST `5.7.0` but the pinned model declares `sentence-transformers>=6.1.0`. It was **not** a test of scientific model performance, not an OOM or evidence of broken T4, and not grounds to change G1–G4 prereg.

| Original private file | SHA-256 |
|---|---|
| `ttm_embedgemma2_d1_t4_preflight_once_v1_CLAIM.json` | `da0444b0836d0e4f2aee7f4237bc59033db679dda24d053c03bfb287ca118114` |
| `ttm_embedgemma2_d1_t4_preflight_once_v1_RESULT.json` | `60238e27682d43c84242b5f4138fef23b00e8f71cc77ca623796461a6c3978de` |

These **exact original files** were SHA-256 read back by local audit and must remain private and unchanged. V3 checks both filenames/digests in Google Drive **before** creating any successor `CLAIM`, and checks again immediately before `os.O_EXCL`. If missing or modified => STOP, no claim. V3 never deletes or overwrites V1.

## 2. Source-only V3 repair — concrete exported artifacts

The notebook and QA are **conversation attachments**, not executed and not committed as binary/JSON notebook bytes in this GitHub change. Their bytes can be audited using the exact SHA-256 below; this repository file is the durable provenance/decision receipt. Do not claim GitHub hosts the notebook itself.

| Artifact | Exact byte length | SHA-256 |
|---|---:|---|
| `TTM_EmbeddingGemma2_D1_T4_OneShot_Preflight_OWNER_APPROVED_SETUP_V2.ipynb` (source baseline) | 27,179 | `6a8d62dbac62a54bf5cfe38d630f1da1e2eb12fdaa18e2b2a9216041287344df` |
| **`TTM_EmbeddingGemma2_D1_T4_Preflight_ST610_SOURCE_QA_V3_LOCKED.ipynb`** | **32,753** | **`6b9defda0967df4f59617482dbfc0f7f7f2c1f7125f164f48194b2c10cdd4a76`** |
| `TTM_EmbeddingGemma2_D1_ST610_V3_Independent_Static_QA.py` | 9,835 | `ce9b80984eb1e9d98c5810e77ff7f8fa01217583a227cde254e304f06f286b8c` |
| `TTM_EmbeddingGemma2_D1_ST610_V3_Independent_Static_QA.json` | 3,929 | `805e4574b3bab3f54a9b0c713f0124a9977b07ae26476ea476f25dfe73b80db7` |
| `TTM_EmbeddingGemma2_D1_ST610_V3_SOURCE_ONLY_PACKAGE.zip` | 19,267 | `54ad588cdae22d08bd5fa92fdaee787030144fd39680941c341ca3ac8a4adaaa` |

**New proposed run ID:** `ttm_embedgemma2_d1_t4_preflight_st610_once_v1`.  
**New runtime WORK_ROOT:** `/content/ttm_embeddinggemma2_d1_preflight_st610_v1`; **V1 root is not reused**.  
**Private Drive destination:** `/content/drive/MyDrive/TTM_EmbeddingGemma2_D1_Preflight`; V3 files have their own `RUN_ID` suffix and V1 files remain immutable.

### Repair mechanics and external version provenance

- Official model `config_sentence_transformers.json` includes `requirements.sentence-transformers.specifier >=6.1.0`; its `modules.json` requires `sentence_transformers.base.modules.normalize.Normalize`. Source: https://huggingface.co/google/embeddinggemma-2/blob/f9972ac22e696a105c482202646979e33e4b5a1e/config_sentence_transformers.json . A public GitHub `huggingface/sentence-transformers` tag `v6.1.0` contains `sentence_transformers/base/modules/normalize.py`, class `Normalize`: https://github.com/huggingface/sentence-transformers/blob/v6.1.0/sentence_transformers/base/modules/normalize.py .
- PyPI `sentence-transformers==6.1.0`, wheel `py3-none-any`, SHA-256 **`eb8122f4d180f552eda26dc3d77e84e8c11dc2b1d456a406b9f24abb70ceeadd`**: https://pypi.org/project/sentence-transformers/6.1.0/ .
- V3 has a distinct **before-CLAIM** SETUP 1 (owner successor gate, manual TTM-Small non-conflict, Tesla T4, Drive, V1 SHA and V3 marker absence) followed by SETUP 2 (optional exact-ST6.1.0 PyPI wheel installation with `--no-deps --no-cache-dir --only-binary=:all: --require-hashes`, then runtime package versions, import `Normalize` and `SentenceTransformer`).
- V3 refuses inherited ST5.7 already imported into the same kernel; instruct **Colab Runtime → Restart runtime**, preserving private Drive. No unbounded `pip install -U`, no model `modules.json` patch. Package stack expected from V1: Python 3.13, Torch `2.14.1+cu130`, Transformers `5.22.1`, huggingface_hub `1.33.0`, PyArrow `23.0.1`, NumPy `2.4.6`. A changed Colab runtime must hold **before CLAIM**, not secretly adjust other libraries.
- The runner **rechecks** ST version and module and V1 hashes before its one-shot `os.O_EXCL`. Only after these gates can the successor `CLAIM` be created.
- Scope unchanged: Google model `google/embeddinggemma-2@f9972ac22e696a105c482202646979e33e4b5a1e`; Qwen `Qwen/Qwen2.5-0.5B-Instruct@7ae557604adf67be50417f59c2c2f167def9a775`; SQuAD validation `rajpurkar/squad@7b6d24c440a36b6815f21b70d25016731768db1f`, Parquet SHA `8c6646d36bd5a95061e076788cf3161d11f6f3e7d625dac7a83bbed0a49f69f7`.
- Tesla T4, EmbeddingGemma text-only FP32, frozen Qwen, 30-minute GPU session, download <=5 GiB, new storage <=8 GiB, paid spend $0. No R_gold science, retrieval scoring, Adapter or TEST. Previous body from remote model metadata/snapshot download onward remains byte-for-byte the original V2 source except replacing ambiguous file-hash step label with `model_file_sha256_calculated_local_not_remote_attested`.

## 3. Independent static QA (offline, no model execution)

**`PASS_SOURCE_ONLY_NO_EXECUTION`: 79/79 tests.** Executed `TTM_EmbeddingGemma2_D1_ST610_V3_Independent_Static_QA.py` **against the exported V2 and V3 bytes**, not merely the patch author's assertions.

Tests include notebook JSON/nbformat validation, Python AST compilation of every code cell, no outputs/cell-run counts, unique cell IDs; exact source SHA/corpus pins, limits and FAIL receipts; distinct successor `RUN_ID`/root; old-vs-new source delta constraints; ST wheel hash/pip flags; frozen existing runtime; correct import/class; old V1 receipt read-only consistency; guard ordering before atomic claim; frozen model/source pipeline; one-shot no overwrite; no science. **32/32 combinatorial failure-path decisions** were evaluated from the runner's actual AST (all absent/false approvals stop).

QA limitations: this proves static contract/negative guards only. It **does not** prove pip install succeeds, all loaded packages are actually compatible on Colab, text-only EmbeddingGemma can emit FP32 finite vectors, Qwen mask correctness at runtime, T4 capacity or D1 scientific quality. Those are future separately authorized technical preflight concerns.

## 4. Single successor admission boundary

**`SOURCE_REPAIR_AND_STATIC_QA=PASS`**, **`SUCCESSOR_RUNTIME=NOT_AUTHORIZED_AND_NOT_EXECUTED`**. Notebook V3 defaults `SUCCESSOR_ONE_SHOT_APPROVED=False` and `TTM_SMALL_RESOURCE_CLEARED=False`. Source-only QA is the requested current task; the user may consider **one successor owner approval** after inspecting the locked V3. Do not create new RUN_ID without need or call it a repeat of the consumed V1. There is no Colab-control connector in the current ChatGPT session; the notebook must be run by the user from a real Colab T4 session, if approved.

**Next:** `TTM_EMBEDDINGGEMMA2_D1_ST610_V3_SUCCESSOR_SINGLE_AUTHORIZATION_AND_COLAB_TECHNICAL_PREFLIGHT` — approve exactly the pinned new `RUN_ID`, resource envelope and existing TTM-Small T5 priority, then run one technical preflight on Colab, collect separate CLAIM/RESULT and independently adjudicate. If anything fails after CLAIM, preserve FAIL and do not auto retry. D1–D4 scientific execution stays unauthorized; `lineage.md` remains untouched by this engineering QA.

**Final:** `V1=CONSUMED_FAIL_PRESERVED` · `V3_SOURCE_ONLY=PASS_79/79` · `V3_COLAB=NOT_EXECUTED` · `SCIENCE=NOT_EXECUTED` · `D1_D4=NOT_AUTHORIZED` · `TTM_SMALL_T5=PRIORITY_FIRST`.
