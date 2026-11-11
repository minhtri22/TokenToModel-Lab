# TTM-Small-4M × EmbeddingGemma 2 — A0E fresh lexical + 4-arm prospective preregistration contract

**Ngày:** 2026-11-11
**Operation:** TTM_GEMMA2_A0E_FRESH_LEXICAL_INDEPENDENT_EVALUATION_AND_FOUR_ARM_PREREG_FREEZE_DESIGN_ONLY
**Research branch:** research/ttm-gemma2-token-alignment-pretraining-causality-20261111
**State:** DESIGN_FROZEN_SCORE_BLIND_SOURCE_MASK / SCIENCE_NOT_ADMITTED / T4_HOLD
**A0D:** OWNER_LOCAL_PINNED_DONOR_SOURCE_OFFICIAL_CLASS_T1_MAPPING=PASS, independent A0D adjudication commit db7c6c56dc37c21f90111274f64e92c44abf0a27.

## 0. Distinction of scientific claims (quan trọng)

The study measures transfer from **pretrained input embedding rows**, not whether the donor's entire text Transformer forward produces semantic representations.

1. Pretraining-associated transfer: pretrained-token alignment produces better VAL NLL than the same treatment on untrained official-initialized embeddings. This is difference-in-differences, not yet semantic causality.
2. Independent lexical support: pretrained input rows associate with human lexical similarity more strongly than untrained / matched null rows on a previously unused, score-blind frozen word roster.
3. Semantic causal claim: requires jointly (1)+(2), selective disruption of semantic token relations under matched geometry, absence of morphology/frequency/source confounding, and unresolved pretrained donor benchmark contamination; a positive 4-arm pilot alone is insufficient.

Two falsifications: lexical positive but VAL benefit absent => encoded lexical signal is not proven useful to TTM. VAL benefit positive but lexical difference absent => no evidence that the transferred gain is semantic, as opposed to geometry, training dynamics or orthography.

## 1. Frozen external lexical source and rights

- Primary source: **Gerz et al. (2016), SimVerb-3500**, EMNLP 2016, DOI 10.18653/v1/D16-1235. Cambridge Apollo published dataset DOI 10.17863/CAM.9391, 3,500 verb-similarity pairs with human ratings on 0..10. Cambridge official repository metadata states **CC BY 4.0**. Citation and attribution required for derived uses. Source page: https://www.repository.cam.ac.uk/items/8a568201-0fa4-4e54-81b1-f920102492ea .
- Byte-pinned public mirror: benathi/word2gm, evaluation_data/simverb/data/SimVerb-3500.txt, **Git blob 769fcdee0ebfae8e37b8ca69241f626a080a75c8**. Independent repository sota-hayashi/scisci holds identical Git blob and cites Cambridge Apollo, but **official publisher archive SHA has not independently matched to the mirror**. This byte-parity is a pre-exec hold gate, not silently waived.
- SimLex-999 old exclusion word list: source yumeng5/Spherical-Text-Embedding Git blob b642f3abe39c9ff1c9d6f942c917e47fd6c3801d, 1,028 distinct lower-case alphabetic word types.
- WordSim-353 old exclusion word list: source benathi/word2gm evaluation_data/wordsim353/combined.csv Git blob f4b59539bdc53a9baa45d0388ca418373560bd8a, 437 distinct lower-case alphabetic word types. WordSim-353 official site says CC BY 4.0: https://www.gabrilovich.com/resources/data/wordsim353/wordsim353.html .
- T1 manifest is PRIVATE; SHA256 cba18e60cee3d08a353ee6d4a451017289e45af7b4b1179c87171b9b78d7dfdc. No raw private data or derived labels are to be committed.

The selected public benchmark existed before EmbeddingGemma 2 training. **We cannot claim that the donor did not ingest its text or annotations.** Human annotations constitute independent published observations, not a temporally new prospective blind human sample. Any stronger contamination-free claim needs fresh human labeling independently sealed, later.

## 2. Score-blind reproducible lexical roster, frozen now

Selection reads **only the first two word columns**; do not read similarity scores, lexical relation type or embeddings for choice:
1. Decode original T1 byte-level BPE with pinned source; accept exactly one leading space followed by ASCII lowercase letters; require a unique token ID for each whole word and an existing valid donor mapping. Base eligibility: 1,142 unique word types.
2. Select SimVerb pairs with both T1 words mapped. This is 288/3,500 pairs.
3. Exclude a candidate if **either** word occurs anywhere in SimLex-999, yielding 144 pairs. Exclude if either word occurs anywhere in WordSim-353, yielding **138 pairs and 78 unique word types**. Exclusion covers all previously inspectable words, stricter than only 44 SimLex or 21 WordSim measured subsets.
4. Freeze all 138 oriented pairs in UTF-8 two-column tab TSV, sorted by literal (word1,word2), no header, LF newline including final newline: SHA256 **8ba5b07bea73cfc6784de940378d5726be9cc8dab2ecc32daa4a5a3555bf91b1**. Keep this file private.
5. Form the primary independent-word **maximum-cardinality matching** on the 138-pair undirected graph, breaking ties via integer weight first 14 hex of SHA256 string "TTM_GEMMA2_A0E_LEXICAL_V1|{word1}\t{word2}" and networkx max_weight_matching(maxcardinality=True), version 3.6.1. Freeze 37 word-disjoint pairs / 74 unique words, same TSV rules: SHA256 **b280478feb9f7359c261944e5c54c7808c96e05bd14558657044fe6f35a2ee2c**. No human scores used.
6. The graph has 2 connected components, the largest with 76 words; the 138 samples are **not statistically independent pairs**.

Private roster ZIP SHA256 **5680a2e8b39b04eba85629a0851c50f3da18387305221bdfa4a2aa2ab3b7c710**. It contains only pair IDs, README attribution and public aggregate QA, **no human ratings, train windows or donor vectors**. Do not publish private roster by accident.

Gold source and labels must be sealed in independent custody with SHA, no user/model outcome inspection or model-dependent selection. This has NOT happened. Do not call the 37 pairs a statistically powered confirmation just because they are word-disjoint.

## 3. Four arms, paired estimand and equal-information budget

Each arm uses the same TTM-Small-4M checkpoint SHA (still must be pinned in execution manifest), same T1 2,048-vocab map, same fixed TRAIN windows and paired VAL document IDs, same optimizer, learning rate, schedule, dropout, precision, sampler, train-token count and evaluation code. One source-only change per factorial dimension:

| Arm | Pretrained-origin factor | Token-identity association factor |
|---|---|---|
| P-A | Pretrained official EmbeddingGemma 2 input token embedding from frozen donor source | Actual token assignment |
| P-C | Same pretrained source and frozen projection | A0B constrained residual null under moment constraints |
| N-A | Actual official EmbeddingGemma2TextModel via Transformers 5.19.0, initialized from config without any pretrained weights; use input embedding only | Actual token assignment |
| N-C | Same official-initialized source and matched projection | Identically defined constrained residual null |

Pretrained source fingerprint / rights and the complete P/C/N/A alignment matrix must be rechecked before science. Do NOT reuse the synthetic parameter topology mirror as an official untrained control.

Primary language estimand:
D_origin = [NLL(P-C)-NLL(P-A)] - [NLL(N-C)-NLL(N-A)].
Supporting:
D_align = NLL(P-C)-NLL(P-A).
Use **per-target-token NLL in nats/token**, lower is better. Compute paired per-seed and per-VAL-document values, with identical VAL document budget. Do not use previously consumed TTM TEST, H768, OOD256, Q1/Q2 or any other consumed outcomes as controls.

Pilot TRAIN budget **4 arms × 3 paired seeds × 512 optimizer steps × 4,096 target tokens per step = 25,165,824 target-token presentations**, subject to T4 source and execution gates.
- Training paired seed blocks: **41031, 41032, 41033**.
- Official N weight initialization seeds: **61031, 61032, 61033**.
- Null-control constrained shuffle seed blocks: **51031, 51032, 51033**.
- All source/projection, TRAIN/VAL pins, sampler hashes, optimizer/scorer versions, checkpoint init SHA and individual block receipts are frozen BEFORE dispatch. One scientific execution round; no repicking seeds or hyperparameters after outcomes.

Distribution-matching guard (TRAIN only, no lexical gold): source-wise mean, covariance, per-token row norms, total projected scale, training frequency relationships, effective rank and tokenizer alignment must be audited. Frozen minimum feasibility screens: absolute standardized mean differences <= 0.10 for predefined frequency, length, norm, and char-overlap features; covariance relative Frobenius discrepancy <= 0.05 within paired A/C null, and median relative per-row norm gap <= 0.05. If any test fails, classify CONTROL_INVALID/HOLD; no rerunning with post-hoc null improvements.

## 4. Lexical outcome and statistical pre-registration

**Primary (37 pair independent-word core):** selection of all 37 pairs did not use human scores, but the source is PUBLIC and score bytes are **not under independent custody yet**; do not claim they have already been sealed. Before using the scores, an independent custodian must pin the gold file, scorer, all P/N/C vector hashes and source transformations, with no selective unblinding. Compute Spearman rho(cosine, human score) separately for P-A, P-C and N-A; use the same original donor-to-T1 mapping / original 512D input space before TTM training as the source-origin test. Vector source is input embedding, not donor text-model forward.

Primary contrasts:
- L_origin = rho(P-A) - mean across predeclared N-A initialization seed blocks of rho(N-A).
- L_disruption = rho(P-A) - rho(P-C).

Predeclare two-sided paired bootstrap at the **word-disjoint pair level** with 10,000 resamples using analysis RNG seed **71031**, and Holm adjustment over exactly these two comparisons. Require BOTH point estimates >= **+0.20 Spearman rho** AND both Holm-corrected confidence lower bounds > 0 for exploratory *support*; this 37-pair sample may be underpowered. Do not tune thresholds or substitute pair subsets after seeing scores. If statistical software cannot implement valid multiple-testing-adjusted bootstrap confidence bounds, HOLD rather than reporting an unadjusted p-value as PASS.

**Secondary sensitivity (138 graph-dependent pairs):** analyze rho with word-identity-aware graph permutation (Quadratic Assignment / node-label shuffle constrained by TRAIN frequency strata), 10,000 precommitted shuffles seed **71032**. Never bootstrap 138 rows as if IID; report pair network degrees, morphology, orthographic edit similarity, TRAIN-only log frequency and component coverage. Report source fidelity and repeated-word limitations. This is not an extra confirmatory trial or excuse to rescue failed 37-pair primary.

This public benchmark has a possible *benchmark contamination* concern in pretrained corpora. For strict **causal-semantic confirmation**, an independently annotated post-freeze fresh human label set, rights/consent and blinded independent custody would be required; it is NOT acquired in A0E.

## 5. Pilot precommitted decision thresholds (not science significance)

For the **three-seed feasibility pilot only**, promote to a separately admitted confirmatory study only if:
1. D_origin > 0 for all three paired seed blocks AND arithmetic mean D_origin >= **0.02 nats per target token** (approximately 2% relative perplexity change at fixed baseline).
2. D_align > 0 for all three blocks.
3. No geometry/null invalidity, data leakage, source rights issue, or broken checkpoint lineage; no one-shot reuse.
4. The independent lexical test does not fail required prereg screens; if failed/unavailable, interpret language effect as *not attributable to semantics* and HOLD semantic causal promotion.

Three paired seeds are **not** sufficient for a confirmatory alpha=0.05 exact sign test (best possible one-sided p=0.125, two-sided p=0.25). Do NOT label an all-positive pilot outcome SCIENCE_CONFIRMED; instead, prereg a follow-on independent adequately powered repeated-seed experiment using untouched data. At least six uniformly positive independent blocks would attain two-sided exact sign-test p=0.03125, but sample size should be determined by prospective power, not this mathematical minimum alone. No future GPU run is authorized by this document.

Outcomes classification:
- Language improvement alone => transfer-associated **only**, not semantic causal evidence.
- Lexical rho difference alone => representation-level semantic signal, not proof TTM uses it.
- Both + matched/null valid => **consistent with** a semantic mechanism, still benchmark-contamination / alternative mechanism caveats.
- Evidence against / conflicting / insufficient sample => FAIL or INCONCLUSIVE as prereg, not source repair followed by a second look.

## 6. Provenance/rights, independent science gates and disposition

**PASS source-scoped design-only:** CC BY 4.0 publisher metadata for SimVerb; matching public source mirrors; independent word exclusion relative to SimLex and WordSim; frozen score-blind 138/37 roster SHA256 and preset pilot seeds, estimands and exploratory thresholds.

**Unresolved HOLD gates:**
- publisher archive exact bytes vs public Git mirror (not independently verified);
- independent human label custody, gold file SHA, or truly fresh post-pretraining blind labels if making strong uncontaminated semantic claim;
- complete original donor pretrained input tensor / rights pin and P/C/N/A geometry-null implementation feasibility across all arms;
- TRAIN/VAL private source rights and independent rubric; checkpoint/sampler/optimizer pins for pilot;
- independent no-leak prereg adjudication and single pre-exec permit.

**Do not use any GPU or model forward.** Do not append lineage.md for this engineering/design-only result, and do not edit main. Keep L0020/L0021 intact; L0022 remains uncreated. Previous SimLex 44/WordSim 21 were consumed and never become confirmatory TEST.

**A0E adjudication:** LEXICAL_SCORE_BLIND_MASK_AND_PROTOCOL_FROZEN_DESIGN_ONLY / PREREG_INDEPENDENT_ADMISSION=HOLD / T4_2X2=HOLD.
**Bước thực hiện tiếp theo:** TTM_GEMMA2_A0E_INDEPENDENT_SOURCE_LABEL_CUSTODY_AND_PREEXEC_FROZEN_GATE_DECISION. This is ONE bounded integrated admission decision, not serial micro-permits: verify original source checksum, blind gold custodian, null moment fidelity, source and TRAIN/VAL rights and science estimator pins. If any fail, HOLD without GPU; if all pass, make a single separate execution authorization decision.
