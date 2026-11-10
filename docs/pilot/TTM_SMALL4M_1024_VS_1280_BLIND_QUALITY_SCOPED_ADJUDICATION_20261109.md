# TTM-Small-4M — Blind quality rubric & scoped final adjudication (1024 vs 1280)

**Date:** 2026-11-09 · **PR:** #13, held as DRAFT · **Scope:** exploratory controlled generation only. No training, no generation rerun, no TEST/Q1Q2 reopened.

## Evaluation executed

- 16 frozen A/B pairs across 8 new prompts, 2 decoders, 32 existing PyTorch generations of the exact original T4 Small-4M checkpoints.
- Each A/B text independently scored on three **integer 0–3** axes: **prompt adherence** (bám prompt), **coherence** (mạch lạc), **consistency** (nhất quán). Full rubric in frozen archive.
- Before unblinding, the 96 scores and 16 row preferences were sealed as `FROZEN_BLIND_SCORES.csv`, SHA256 `cafffd62bddf441c301e3058d7941c09e6e4d96bf144ab40009971bfc882c24c`; rubric SHA256 `d894795e09bf88a64a08839425ad9ef721c912ae7315e0d1387991cb292ac969`; freeze receipt SHA256 `84bfb357fe577c439aee08a82d32ea17c0f660661d0353527114b5e2739cbdaa`.
- Subsequent unblinding mapped each A/B back to the stored raw output of step 1024 or step 1280. **32/32 text and prompt/seed mapping checks passed.** Separate material/arithmetical QA: **25/25 PASS**, without asserting the qualitative judgements were independently replicated by humans.

## Results

| Scoring axis (0–3 each) | Step 1024 | Step 1280 | Δ 1280−1024 |
|---|---:|---:|---:|
| Prompt adherence | 0.375 | 0.375 | 0.000 |
| Coherence | 0.500 | 0.9375 | +0.4375 |
| Consistency | 0.500 | 0.750 | +0.250 |
| **Total (0–9)** | **1.375** | **2.0625** | **+0.6875** |

Step 1280 **won 6, lost 2, tied 8**. Greedy mean Δ +0.500; sampled mean Δ +0.875 (of 9). Both modes retained the original generation limits/seed matching. Prompt-cluster bootstrap descriptive 95% interval **[+0.0625,+1.3125]** (8 prompt clusters, 10,000 draws); this is NOT a human-rating reliability or generalization confidence statement.

Pre-unblinding exploratory improvement gates required all: mean total Δ ≥ **+1.5**, ≥ **10/16** step-1280 wins, lower prompt-cluster CI > 0, nonnegative means under both decoders. **Only the last two passed.** Sensitivity excluding P02/greedy and P05/greedy (known examples labeled in earlier conversation) leaves 14 pairs, 1280 wins 4, 1024 wins 2, ties 8, mean Δ **+0.42857/9**.

**Decision:** `QUALITY_VERDICT=NO_DEMONSTRATED_GAIN_SCOPED`. This is *not* evidence that training failed: exploratory VAL NLL step1024=3.5223388569 → step1280=3.4980890267 remains intact. It shows the weak semantic prompt adherence and low absolute scores persist despite NLL improvement.

## Scientific integrity and limitations

**Explicit limitation:** One ChatGPT AI reviewer, no distinct human evaluator or inter-rater agreement. Two previously disclosed checkpoint-tagged examples can compromise contextual blinding, so do not call this fully double-blind or scientifically independent human QA. Rubric thresholds were frozen before reading A/B key, but after blinded text was shown. Generation code was independently transcribed and corrected after an excluded invalid engineering smoke; canonical P02 bit-exact forward parity has **not** been verified.

Exact source checkpoints: 1024 SHA256 `cb985751795c8328ad65acf7ca4c1033ce35182c1bfbdb8c38550de629cb271b`, 1280 SHA256 `ee723407b2c25a18be20e26387a3dd8e4a18e2942d469279b6f0748ff86af0dc`. No TRAIN/VAL/TEST corpus, checkpoints, or tokenizer manifest were published.

**Evidence:** Original 32 generations and private A/B key: [Drive archive](https://drive.google.com/file/d/1k0HwoT5ZCmVgGodpGAC0sri3F9fO3pD-/view). Full after-the-fact score freeze, scored CSV, unblinding, audit code, report, and original archive bundled locally:
- `TTM_SMALL4M_1024_VS_1280_FINAL_BLIND_QUALITY_ADJUDICATION_20261109.zip` SHA256 `81bea7212d26dfd3defda67f3c5fe3b3e9058b430a9d7972b76b7d3b8a46e520` (46,401 bytes).
- Report SHA256 `d6d9b46aaf5ddb1af92216efc220cd40864d11db82f65efeb3899122988dc3da`.
- Post-unblind 25/25 QA JSON SHA256 `b2ec5c6ef601ff6f4864818d18834f5dbfe3c26963899f5bd2d2ed9318a59bba`.
- Unblinded paired scores SHA256 `c18e0c6c09e2173c2e4435893b97e5532ad98154bf3cc64b4f5c31fb4c88e24e`.

**Governance:** `GENERATION_NEW=NO` · `GPU_TRAIN_NEW=NO` · `TEST=SEALED` · `Q1Q2=CONSUMED_UNCHANGED` · `PR13=HOLD` · `MAIN=UNCHANGED` · `LINEAGE=L0017_UNCHANGED`. No new formal science PASS/FAIL entry in `lineage.md` for this exploratory single-reviewer judgement.

### Bước thực hiện tiếp theo

`TTM_SMALL4M_PROMPT_ADHERENCE_ROOT_CAUSE_READONLY_DIAGNOSTIC`: Audit canonical P02 inference parity and TRAIN prompt-conditioning/data objective before allocating any further Colab GPU or changing data/training. A truly independent human scoring panel is optional if a confirmatory semantic-quality claim becomes necessary.
