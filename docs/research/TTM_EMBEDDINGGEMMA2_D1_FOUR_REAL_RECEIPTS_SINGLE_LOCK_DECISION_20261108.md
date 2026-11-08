# TTM EmbeddingGemma 2 — D1: Bốn receipt G1–G4 và một quyết định khóa tiền đăng ký

**Work item:** `TTM_EMBEDDINGGEMMA2_D1_COMPLETE_FOUR_REAL_RECEIPTS_AND_REVIEW_ONCE`  
**Date:** 2026-11-08  
**Single protocol verdict:** **`LOCK_READY=YES_SCOPED_PREREG_ONLY`**.  
**Resource/experiment verdict:** `MODEL_DOWNLOAD=NOT_AUTHORIZED`; `COLAB_T4_PREFLIGHT=NOT_AUTHORIZED`; `D1_D4=NOT_AUTHORIZED`; `SCIENCE_EXECUTION=NONE`; `TEST_NOT_OPENED`.  
**Repository:** https://github.com/minhtri22/TokenToModel-Lab  
**Research branch:** `research/ttm-gemini-embedding2-gqa-pagedattention-feasibility-design-20261108` (name is historical; model actually is **`google/embeddinggemma-2`**).  
**Source base before G3/G4 attachments:** `51a7e1ae33221341ee3545bb7033ef690e5227dc`, `main=1a9d8cba56564d6d36257fe95c34f2fd52c4f48a`.  
**Scope of adjudication:** The **ex ante design and deterministic sample-selection protocol**, not experimental competence, runtime QA, corpus bytes already downloaded or an external independent human scientific review. No edits to `main`, TTM-Small PR #12, P00–P12, P07, `lineage.md` or previous histories; no model or scientific job run.

## 0. What changed from HOLD, and what emphatically did not change

Previous `HOLD_WITH_FINITE_GAPS` decisions correctly noted **no materialized R_gold cohort**, **only a named unpinned corpus**, **no concrete R1/R2/R3 sample selection**, and **thresholds still candidates**. This integrated continuation created a real, versioned R_gold fixture, pinned SQuAD's exact validation source digest, wrote a deterministic article/query selection rule, and selected/froze one practical screening criterion. These are **actual immutable input artifacts**, not a new abstract plan.

**Design-lock interpretation:** Before experiments, preregistration may pin `source revision + upstream dataset digest + deterministic, label-blind selection rule + frozen R_gold bytes + metrics/decision rules`. A full locally computed SQuAD passage/group manifest **can be reconstructed and audited in the separately authorized technical preflight without consuming model outputs or TEST science**. This is *not* a claim that source rows have been downloaded or QA'd; any digest, schema, split, rights or sample-selection mismatch leads to `STOP_BEFORE_D1` and cannot be silently patched. This scoped interpretation avoids the impossible requirement that files not permitted for download already have local file hashes, while retaining exact reproducibility.

**Scientific interpretation:** D1 is a **screening/pilot capability question**, NOT population-level proof, a clean never-seen held-out benchmark, an EmbeddingGemma-vs-other-model superiority claim, or evidence about TTM-Small T4.

## G1 — Model source and permissions receipt

| Role | Immutable source revision | Published license | Scoped use |
|---|---|---|---|
| Local embedder | `google/embeddinggemma-2@f9972ac22e696a105c482202646979e33e4b5a1e` | Apache-2.0; also review Google Gemma Prohibited Use Policy | Benign local text-only embedding of licensed QA snippets, `float32` on Tesla T4, 768d, no external Google API |
| Frozen generator | `Qwen/Qwen2.5-0.5B-Instruct@7ae557604adf67be50417f59c2c2f167def9a775` | Apache-2.0 (model card and source license) | Frozen answer-only NLL/greedy QA, no fine-tune |

**Evidence:**
- https://huggingface.co/google/embeddinggemma-2/commit/f9972ac22e696a105c482202646979e33e4b5a1e
- https://huggingface.co/Qwen/Qwen2.5-0.5B-Instruct/commit/7ae557604adf67be50417f59c2c2f167def9a775
- https://ai.google.dev/gemma/docs/embeddinggemma/model_card_2
- https://ai.google.dev/gemma/prohibited_use_policy

**Scoped compliance assessment:** These published open licenses and use policy do not indicate an obstacle to this benign, non-invasive research task, provided license notices are maintained and no restricted-use purpose is introduced. This is a technical/documentary eligibility decision **not legal advice**, no guarantee for all future deployments. This receipt does not assert any third-party rights over the SQuAD text, which belongs to G2.

**Preflight still needed after separate permission:** Download only by pinned revision; verify SHA-256 of actual model/tokenizer/config files, libraries, prompt template and dtype; compare Google model card warning against FP16. On T4 EmbeddingGemma2 must use `FP32` (do not default to FP16). Do not mistake ~270M text model footprint for full multimodal on-disk model size.

`G1_PROTOCOL_SOURCE_ELIGIBILITY=PASS_SCOPED`, `CHECKPOINT_BYTES_VERIFIED=NO`.

## G2 — Real corpus source, licensing and reproducible selection receipt

**Chosen real published source:** Stanford SQuAD v1.1 mirrored as `rajpurkar/squad@7b6d24c440a36b6815f21b70d25016731768db1f`, config `plain_text`. The official Stanford site explicitly publishes SQuAD under **CC BY-SA 4.0**. CC BY-SA generally permits reuse and adaptation with attribution, license link, changes indicated and ShareAlike obligations for adapted material if shared; privacy and other third-party rights may still matter. **Decision:** eligible for scoped local research with attribution and no redistribution of raw texts from this repo; not a blanket legal approval or assertion that every Wikipedia passage is free of other rights. Source corpus remains publicly retrievable and known to pretrained models; no contamination-free claim.

- Stanford: https://rajpurkar.github.io/SQuAD-explorer/
- HF dataset pinned: https://huggingface.co/datasets/rajpurkar/squad/tree/7b6d24c440a36b6815f21b70d25016731768db1f
- License: https://creativecommons.org/licenses/by-sa/4.0/
- Scope of **D1**: **validation only**, not train; HF metadata reports **10,570** validation QA rows (this is source metadata, not locally re-counted).
- **Remote validation Parquet SHA-256 (reported by HF Xet file page):** `8c6646d36bd5a95061e076788cf3161d11f6f3e7d625dac7a83bbed0a49f69f7`. Filename `plain_text/validation-00000-of-00001.parquet`.
- The train file `plain_text/train-00000-of-00001.parquet` is **not used in D1**; remote SHA256 `ea7f52bac024f6b1bdc7aaa2a4ee302cba8c2fdc8d4a235cf18a9a5196b6175b` recorded only to prevent confusion.
- Exact machine-readable source and retrieval-selection contract: `docs/research/fixtures/TTM_EMBEDDINGGEMMA2_D1_SQUAD_RETRIEVAL_AND_R_GOLD_SOURCE_LOCK_CANDIDATE_20261108.json`, **Git blob SHA-1 `52d92e1c054afcf85ec5334e275f9b75ec084e83`**.

**Pre-registered deterministic materialization:** After authorized download, first check downloaded Parquet SHA256 **equals the HF-reported remote SHA**. Then extract all unique `(title,context)` pairs from the validation file, use stable SHA256 IDs, group by normalized article title and select at most **three questions/article** via lowest SHA256(question-id) **without consulting answers or model outputs**. Index all unique validation passages for both R1/R2; never embed or select with reference-answer text. QA relevance label = original source passage corresponding to the question. Source-passage recovery is **not** a claim of identifying every relevant paragraph. All actual group sizes, QA source titles and passage IDs are materialized/checked in the *technical* preflight and stored with hashes; no source material stored in public repository. If content hash, duplicate policies, title group count or paragraph mapping invalid, **STOP and invalidate D1 admission** rather than changing the cohort after results.

**Attribution receipt to carry when materializing:** `SQuAD v1.1; Rajpurkar et al., Stanford NLP; source text attributed to Wikipedia contributors; CC BY-SA 4.0 https://creativecommons.org/licenses/by-sa/4.0/; modifications: deduplicate passages, assign IDs, tokenize, compute embeddings for local evaluation`. Preserve source title/URL or equivalent attribution metadata; if an article's provenance or privacy rights cannot be reconciled, do not redistribute it or claim rights clearance for that passage. Using local vectors in Colab is not a call to Gemini API.

`G2_SOURCE_LICENSE_ELIGIBLE=PASS_SCOPED`, `DATA_LOCAL_MATERIALIZED=NO`, `LOCAL_SOURCE_AND_GROUP_HASH_QA=DEFERRED_TO_AUTHORIZED_PREFLIGHT`.

## G3 — Actual R_gold group fixture and frozen capability decision

**New actual dataset:** `docs/research/fixtures/TTM_EMBEDDINGGEMMA2_D1_R_GOLD_60_GROUPS_LOCK_CANDIDATE_20261108.jsonl`.

- **Git blob SHA-1:** `d6b23349d65724c5a7aaba41604b396facabfbe8`
- **Content SHA-256:** `0215719de94f86a4f2b7a48959ca81343014c127e74799f737901a57b33f341a`
- **Group/QA counts:** `48` independent fictional answerable source groups × `2` paraphrases = `96` answered; `12` fictional no-answer groups × `2` = `24` unanswerable; **60 groups / 120 QA** total.
- **Provenance:** Generated in this turn from original fictional templates as requested, not copied from SQuAD, TinyStories or real customer material. No inference/experiment performed, no scientific seed consumed; it has **not been reviewed by an external human**. This is a fixed benchmark fixture, not proof of independence in a population.
- **Structural QA:** 60 unique groups; 120 unique question IDs; target answers match gold evidence for answered groups; wrong evidence does not expose target answers; unanswered key omitted; no duplication of group IDs; machine-generated JSONL was read back unchanged and checked in a separate read-only pass. These structural checks do **not** prove difficulty calibration or semantic quality beyond inspected templates.
- **Immutability:** No edit after any model output. If QA exposes a substantive data defect before execution, record successor/revision and a new lock decision; do not silently replace hard cases.

**Locked screening cohort and criteria (scope: basic Qwen evidence competence only):**
- Backbone Qwen pinned and frozen. `R0`: question without evidence; `R_gold`: identical question with exact evidence; `R_wrong`: same question with unrelated/wrong group evidence. Answer targets and Qwen tokenizer/role-template fixed per paired triple.
- Primary per group `d_g=mean_{its 2 Qs}[answer_only_NLL(R0)−answer_only_NLL(R_gold)]` in nats/answer token; **48 groups are statistical units**, not 96 independent questions.
- Group bootstrap `B=10,000`, seed `20261108`, two-sided 95% percentile CI. A **positive screening PASS** requires **CI lower endpoint >0.10 nats/answer token** (not merely mean>=0.10 and CI_lower>0).
- Additional mandatory guards: `ExactMatch(R_gold)>=0.60`, `ExactMatch(R_gold)-ExactMatch(R0)>=0.10` absolute, `mean_group[NLL(R_wrong)-NLL(R_gold)]>0`, and **at most 6/24** unsupported factual responses on the no-answer cohort. The 6/24 criterion is a diagnostic guardrail, **not** a population hallucination-safety certification. No-answer group pairs are correlated; report by 12 groups as well.
- Greedy decoding `temperature=0, do_sample=false, max_new_tokens=24`; stop on model EOS/assistant turn boundary; exact match after **Unicode NFKC, casefold, trim whitespace and terminal period/exclamation/question marks**. An otherwise correct answer with extra prose counts as nonexact (no posthoc extraction). `UNKNOWN` is the prescribed no-answer response; training/evidence prompts may not contain annotation suffix or an alternative answer.
- Answer-only NLL uses pinned Qwen template, explicit token-ID boundary and EOS; for each paired question `target_answer_ids` identical across conditions, logits from final prompt token predict first answer token, mask prompt loss `-100`. No prompts or scores may include unseen future target tokens.
- No valid cohort item may be dropped or exchanged. Invalid schema/answer or context overflow ⇒ `INCONCLUSIVE_DATA_INTEGRITY` and **STOP**, not outcome-based reselection. If the full, valid cohort fails competence gates ⇒ `MODEL_CAPABILITY_GAP`, not EmbeddingGemma failure. If thresholds are underpowered ⇒ `INCONCLUSIVE` with original data preserved.
- These thresholds are **methodological screening choices**, not estimates based on unseen model results and **not proof of power**. D1 outcomes must be described as exploratory public-model capability screening, not confirmatory scientific validation of embedding fusion.

`G3_FIXTURE_PRESENT=YES`, `G3_COUNTS_AND_HASHES_VERIFIED=YES`, `G3_SCREENING_RULE_FROZEN=YES`, `G3_MODEL_RUN=NO`.

## G4 — Fixed retrieval R1/R2/R3 protocol and interpretation

**Machine-readable contract:** same JSON as G2 (Git blob `52d92e1c054afcf85ec5334e275f9b75ec084e83`). It fixes:
- **R1:** BM25 lexical on `title: {title} | text: {context}`; `NFKC/casefold`, Unicode word tokens, no stemming/no stopword, (k_1=1.2), (b=0.75), nonnegative smoothed IDF `ln(1+(N−df+0.5)/(df+0.5))`, deterministic tie by canonical passage ID.
- **R2:** `google/embeddinggemma-2` local text-only **FP32**, `QuestionAnswering` query prompt and document title/context prefix, `768d` L2-normalized embeddings + cosine similarity; **no Google API**, identical SQuAD passage/query candidates as R1. No silent truncation beyond 8192 encoder tokens including prefix. Tie by identical ID.
- **R3:** `Qwen2.5-0.5B-Instruct` **frozen** gets exactly source-text passages returned by R2 (`top_k=3` in rank order); answer-only teacher-forced NLL + greedy EM; no vector or Adapter is fed to Qwen.
- **Retrieval primary:** `Hit@3` for recovering originally annotated SQuAD `context` passage, with `MRR@3` secondary, article-group paired `DeltaHit=Hit_R2−Hit_R1`, 95% paired group bootstrap `B=10,000`, seed `20261108`. Scoped superiority claim only if CI lower endpoint >0; otherwise `NO_EVIDENCE_OF_SUPERIORITY` (not embedding failure). `top_k=5` descriptive only.
- **R3 primary subset:** `S_SHORT` only, full evidence + Qwen chat prefix + full target fits actual `L_eff`; `S_LONG` separate descriptive stratum with fixed no-label truncation. Invalid mapping/no valid answer/title ⇒ STOP, no cherry-pick.
- **No double count:** R1/R2 are retrieval ranking methods, R3 is **one** generator evaluation, not a third retrieval algorithm or a second independent Qwen arm.
- **Public benchmark boundary:** SQuAD validation is **public, not hidden**. Known prior exposure and source-passage labeling limit generalization. Even a successful R2/R3 does not prove Adapter, GQA, PagedAttention, GGUF fusion or commercial RAG performance.

`G4_METHOD_AND_SOURCE_SELECTOR=FROZEN`, `G4_ACTUAL_GROUP_COUNTS=TO_BE_VERIFIED_AT_PREFLIGHT`, `G4_RETRIEVAL_EXECUTION=NO`.

## Single integrated lock decision — constraints, not extra permits

**Verdict `LOCK_READY=YES_SCOPED_PREREG_ONLY`** because (a) exact upstream model/dataset revisions are fixed, with SQuAD validation remote SHA256, (b) SQuAD license is eligible for this local research scope with documented attribution duties, (c) a **real R_gold artifact exists, SHA256 verified and zero model outputs observed**, and (d) the R1/R2/R3 cohort-selection algorithm, metrics and screening thresholds are deterministic and predeclared. This is an **adjudication of the experiment protocol**, not a claim to have passed data-materialization QA or obtained independent third-party scientific review.

**The following are NOT APPROVED and must be one integrated preflight, not miniature science permissions:**
1. Separate explicit owner authorization for model/dataset download and Colab compute, only after TTM-Small T4 priority is respected.
2. Download **only** pinned revisions; verify actual SHA-256 vs remote SQuAD validation file hash and model artifacts, preserve license/attribution, data privacy/rights. Create actual article/query/passages manifest by **this exact selector**, QA it independently, no manual changes; if wrong => STOP, do not open D1.
3. Zero-science technical test of EmbeddingGemma 2 text-only **FP32** numerical validity, Qwen tokenizer/chat/prompt shift/mask, source mapping and peak RAM/VRAM/Drive/disk with abort cap; no held-out R_gold/TEST answers inspected during preflight.
4. Review the **one** combined preflight receipt. A separate D1 science authorization is still necessary. D1 runs `R_gold` first and stops on competence FAIL/INCONCLUSIVE; R1/R2/R3 only follow if R_gold PASS within same authorized D1 scope.
5. Actual science PASS/FAIL/INCONCLUSIVE is recorded in `lineage.md` **append-only** only after execution/adjudication. G1–G4 documentation and technical QA do not go into scientific lineage.

**Authority statement:** This is a ChatGPT-authored technical/methodological review, **not** a legal opinion or independent human peer review. License compliance for any distribution requires project-owner attention. `LOCK_READY` does **not** indicate the user approved any real-money usage, downloading, external services, model inference, data publication or scientific execution.

**Final states:** `G1=PASS_SCOPED_SOURCE` · `G2=PASS_SCOPED_PUBLIC_LICENSE_AND_DETERMINISTIC_SOURCE` · `G3=PASS_FIXTURE_AND_SCREENING_PREREG` · `G4=PASS_DETERMINISTIC_PROTOCOL` · **`LOCK_READY=YES_SCOPED_PREREG_ONLY`** · `TECH_PREFLIGHT=NOT_AUTHORIZED` · `D1_D4=NOT_AUTHORIZED` · `DOWNLOADS=NONE` · `SCIENCE=NONE` · `TTM_SMALL_T4=PRIORITY_FIRST`.

**Bước thực hiện tiếp theo:** `TTM_EMBEDDINGGEMMA2_D1_SINGLE_INTEGRATED_T4_PREFLIGHT_AUTHORIZATION_DECISION` — khi chủ dự án cho phép sử dụng tải trọng số/dữ liệu và Colab (không làm gián đoạn TTM-Small T4), thực hiện **một** lượt kỹ thuật có giới hạn: exact SHA files, SQuAD manifest derivation, FP32 embedding sanity, Qwen scoring mechanics, GPU/Drive budgets, independent QA; **không chạy R_gold khoa học** hoặc D1. Nếu chưa có quyền tài nguyên, giữ `PRECHECK_HOLD` mà không mở thêm chuỗi giấy phép.
