# TTM — D1 R_gold science: single-run Colab notebook

**Admission:** `READY_FOR_OWNER_ONE_SHOT_RGOLD_ONLY` — *science execution NOT performed*. Owner's deliberate click **Runtime → Run all** in this Colab notebook is the authorization to run **one** R_gold scientific screening. No extra owner Boolean (previous notebooks had misleading double permission gates). Do **not** run while TTM-Small T5 needs the Tesla T4/Colab quota.

## Deliverables

- `TTM_EmbeddingGemma2_D1_RGold_Science_OneShot_20261109.ipynb`: Colab notebook with complete science code embedded as one Python cell, plus one in-notebook setup cell. No external `.py` artifact is required to run the notebook.
- `TTM_EmbeddingGemma2_D1_RGold_OneShot_Science_20261109.py`: exactly the source text of the science cell in notebook.
- `TTM_EmbeddingGemma2_D1_RGold_Science_Independent_Static_QA_20261109.py` and `.json`: local synthetic/static checks; does not load Qwen or run science.

## Preserved original sources and scope

- PREREG R_gold fixture: 60 groups, 120 QA, Git commit `b10deb62567571dc4aa68e5aad9fe06b55d1e23b`, SHA256 `0215719de94f86a4f2b7a48959ca81343014c127e74799f737901a57b33f341a`.
- Frozen Qwen: `Qwen/Qwen2.5-0.5B-Instruct@7ae557604adf67be50417f59c2c2f167def9a775`; exact file SHA256 from verified V3 technical receipt, weights 988097824 bytes.
- Existing private original technical receipts: 2 files for V3, 2 for Qwen followup; all four must match original exact SHA before claim.
- **One scientific run ID:** `ttm_embedgemma2_d1_rgold_one_shot_20261109_v1`. Saved to `/content/drive/MyDrive/TTM_EmbeddingGemma2_D1_Science/<RUN_ID>/`.
- Pure R_gold: R0 (no evidence), R_gold (true evidence), R_wrong (unrelated evidence), on frozen Qwen. 48 answerable groups × 2 questions; 12 negative groups × 2 questions. **No R1/R2/R3, no SQuAD evaluation, no EmbeddingGemma model load and no training.**
- Primary: grouped mean delta in token-level NLL R0–R_gold, 10,000 percentile bootstrap resamples, seed 20261108, 95% CI lower >0.10. Additional EM gold≥0.60, delta EM≥0.10; wrong-vs-gold NLL>0; no-answer guard ≤6/24 unsupported responses.
- Implementation-specific locked detail: target assistant content token IDs *plus end-of-turn token* `im_end` included in teacher-forced NLL target count (same IDs across arms); token shift is causal and excludes prompt from loss. Greedy max24 and normalized exact match. Missing/unanswerable responses not exactly UNKNOWN are counted conservatively; if >6 while other gates pass, mark `INCONCLUSIVE` requiring blind factual review, **not** automatically hallucination/competence FAIL.
- System/user prompt exactly in science script, frozen before any science output. No changing prompt/metric based on results.

## Run on Colab (owner action)

1. Ensure no active TTM-Small Colab workload. Choose **Tesla T4** on **Colab Free**, no paid GPU.
2. Open `.ipynb` in Colab. Select **Runtime → Run all** once; it verifies software, GPU, original four Drive receipts, fixture digest, Qwen files (prefers existing cache), resource envelope, all prompt/token lengths. Science `CLAIM.json` is created only *after* pre-claim verification and model loading, *before* any science scoring.
3. It saves one file per group into private Drive `groups/`, then a terminal `RESULT.json`. If Colab disconnects before final RESULT, opening same notebook again resumes **same RUN_ID with exact same source/protocol**, skipping completed group files. No changes to fixture, prompt, tests or run ID. The script will reject any attempt after terminal RESULT exists.
4. Send `TTM_RGOLD_SCIENCE_STATUS` and Drive `RESULT.json` for independent QA; do not modify/delete CLAIM or groups. A completed science result is still `UNADJUDICATED` until checked. Append a science PASS/FAIL/INCONCLUSIVE entry to `lineage.md` **only after independent adjudication**. Do not auto-launch R1/R2/R3.

## Caveats

- This is a **fictional/template-generated diagnostic**. The 48 group labels are unique but share repeated templates, so bootstrap significance does not establish independent sampling from a real-world target population.
- This is **not** scientific evidence of EmbeddingGemma's retrieval superiority; it screens whether frozen Qwen can use provided correct evidence.
- No live Colab/GPU test has been executed by the assistant. The QA checks syntax, mock causal masking and deterministic reporting only.
- The 30-minute timeout is polled between items, not a guaranteed hard GPU kernel timeout. The 5GiB network limit is based on pinned source sizes, not a live network-byte counter; stop if quota unexpectedly exceeds the proposed free budget.
- Colab Free, quota and TTM-Small resource priority cannot be independently verified from GitHub or the connector. The owner must choose the free runtime and not start if TTM-Small T5 is using it.