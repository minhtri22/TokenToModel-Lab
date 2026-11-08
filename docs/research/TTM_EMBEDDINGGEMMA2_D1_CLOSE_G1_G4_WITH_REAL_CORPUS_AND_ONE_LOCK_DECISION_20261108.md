# TTM — D1 EmbeddingGemma 2: G1–G4 real-corpus closure and one lock decision

**Work item:** `TTM_EMBEDDINGGEMMA2_D1_CLOSE_G1_G4_WITH_REAL_CORPUS_AND_ONE_LOCK_DECISION`  
**Date:** 2026-11-08  
**Single lock decision:** **`HOLD_WITH_FINITE_GAPS`** — `LOCK_READY=NO`, `D1_D4=NOT_AUTHORIZED`, `SCIENTIFIC_EXECUTION=NONE`.  
**Scope:** Design/source and rights review only. No weights, datasets, files, model execution, Colab, GPU, API, TEST, scientific seed, QA run or training downloaded/executed; no change to TTM code, `main`, `lineage.md`, PR #12, P00–P12, P07 or pilot TTM-Small T4.  
**Repository:** https://github.com/minhtri22/TokenToModel-Lab  
**Design branch:** `research/ttm-gemini-embedding2-gqa-pagedattention-feasibility-design-20261108` (historic name only; actual model **`google/embeddinggemma-2`**, not Gemini API).  
**Branch HEAD before document:** `aed8f9a992d3fcad5d6bc9e298c89bed07624a95`; **main HEAD observed:** `1a9d8cba56564d6d36257fe95c34f2fd52c4f48a`.  
**Primary prior packet:** `docs/research/TTM_EMBEDDINGGEMMA2_D1_FINAL_SOURCE_RIGHTS_AND_PREREG_LOCK_CANDIDATE_DESIGN_ONLY_20261108.md`. This document is **additive adjudication**; no previous PASS/FAIL is overwritten.

## 0. Executive decision and what "real corpus" means

A **real, publicly published dataset has been identified and its exact repository revision is pinned as a candidate**; no subset has been materialized, counted by group, independently checked or licensed for this exact workflow at record level. Accordingly, it is **not valid to say a real D1 experimental corpus already exists**. Scientific prereg cannot be sealed without a real sample manifest, rights/provenance receipt, fixed R_gold cohort and retrieval labels. Treat `SOURCE_IDENTIFIED` differently from `DATA_MATERIALIZED` and from `RIGHTS_APPROVED`.

**Exactly one integrated decision:** `HOLD_WITH_FINITE_GAPS`. It has four closure entries only, `CLOSE-G1` through `CLOSE-G4`. Do not spawn independent technical permits for subentries. After all four receipts are present, one reviewer performs **one** integrated `LOCK_READY` vs `HOLD_WITH_FINITE_GAPS` adjudication. No execution authority is implicit in a scientific prereg design lock.

## G1 — Source revisions, license and integrity boundaries

| Item | Pin or evidence | Current status |
|---|---|---|
| Google embedding model | `google/embeddinggemma-2@f9972ac22e696a105c482202646979e33e4b5a1e` | `REVISION_ID_OBSERVED` |
| Frozen Qwen model | `Qwen/Qwen2.5-0.5B-Instruct@7ae557604adf67be50417f59c2c2f167def9a775` | `REVISION_ID_OBSERVED` |
| Published model license | Both Hugging Face model cards report `Apache-2.0`; Qwen repository additionally has `LICENSE` | `PUBLISHED_LICENSE_REVIEWED_SCOPED` |
| Additional Google policy | EmbeddingGemma 2 model card specifies `Gemma Prohibited Use Policy` for deployments | `USAGE_POLICY_ACKNOWLEDGED`, exact-revision application receipt incomplete |
| Model artifact integrity | Checkpoint shards, tokenizer and config file SHA-256 after authorized download | `NOT_DOWNLOADED` — explicitly **not** a design-lock blocker |
| Runtime and numerical contract | Google text-only ~270M, native vector 768, text context 8192 incl. prefixes; FP32 encoder on T4; **no FP16** | `DESIGN_CONTRACT_PINNED / RUNTIME_NOT_EXECUTED` |

**Primary sources:** https://huggingface.co/google/embeddinggemma-2/commit/f9972ac22e696a105c482202646979e33e4b5a1e ; https://huggingface.co/Qwen/Qwen2.5-0.5B-Instruct/commit/7ae557604adf67be50417f59c2c2f167def9a775 ; https://ai.google.dev/gemma/docs/embeddinggemma/model_card_2 ; https://ai.google.dev/gemma/prohibited_use_policy .

**Remaining rights/source receipt:** Frozen model license/notice+usage-policy snapshot or verifiable record for both exact revisions, with a written statement that planned local text-embedding, vector caching and frozen-Qwen QA fall within permitted use; file name/size inventory and plan for verifying hosted LFS/Xet digest once downloaded. This is legal/rights documentation, **not** a demand to download weights now. User's right to use corpus must be established separately.

**Integrity rule later:** record `repo_id, revision, filename, expected remote digest/etag (where trustworthy), downloaded_sha256, tokenizer_sha256, config_sha256, library_versions, dtype, GPU`. An HF repository commit SHA **is not** the SHA-256 of downloaded `model.safetensors`. No invented checksum.

## G2 — An actual, public QA corpus selected; rights and materialization remain distinct

### Candidate real dataset, revision and schema

| Field | Verified public Hub metadata |
|---|---|
| Repository | `rajpurkar/squad` — https://huggingface.co/datasets/rajpurkar/squad |
| Exact dataset revision | **`7b6d24c440a36b6815f21b70d25016731768db1f`** |
| Card license | **`cc-by-sa-4.0`**; source documented as `extended|wikipedia` |
| Config and schema | `plain_text`; `id`, `title`, `context`, `question`, `answers{text,answer_start}` |
| Public splits | `train=87,599` rows; `validation=10,570` rows |
| Artifact listing | `plain_text/train-00000-of-00001.parquet`, `plain_text/validation-00000-of-00001.parquet`, `README.md`, `.gitattributes` |
| Access status | Public/un-gated as reported in Hub metadata |
| Corpus bytes / doc group counts independently verified | **NO** — only public repository metadata read, no dataset downloaded |
| Rights for exact use and attribution | **NOT YET ADJUDICATED**; source Wikipedia contributors and publication obligations must be addressed |

**Source evidence:** https://huggingface.co/api/datasets/rajpurkar/squad ; https://huggingface.co/datasets/rajpurkar/squad/tree/7b6d24c440a36b6815f21b70d25016731768db1f ; https://huggingface.co/datasets/rajpurkar/squad/blob/7b6d24c440a36b6815f21b70d25016731768db1f/README.md ; https://creativecommons.org/licenses/by-sa/4.0/ .

**Rights conclusion:** The dataset card declares CC BY-SA 4.0 and references Wikipedia; this is positive published evidence for permitted adaptation under that license when applicable. It does **not** itself produce an attribution register for every source article, rule out rights in third-party elements, or approve a project-specific derived corpus/vector cache. Attribution, license link, modifications, share-alike applicability to any shared adaptations, and privacy/provenance must be documented. Because all corpus is intended to remain local, no third-party Gemini API right applies; Colab is still cloud compute and must be reviewed as such. **Do not interpret this as a legal opinion or a blanket prohibition on research use.**

**Important dataset detail:** SQuAD **v1.1** answers are extractive and the named Hub dataset provides answerable QA; it does not supply the independently constructed unanswerable R_gold cohort. The 12 negative groups in G3 must be created/sealed separately. A published dataset with models possibly previously exposed to its Wikipedia articles is not a proof of unseen knowledge. Report scope as `PUBLIC_QA_RETRIEVAL_BENCHMARK`, not an industrial or clean OOD generalization claim.

### Concrete dataset construction contract (NOT executed)

- Unit of retrieval document: canonical `(title,context)` passage, deduplicate identical passage bytes; assign `passage_id=SHA256(canonical_source_key || UTF8(context))` and independent `article_group_id=canonical(title)`. All SQuAD QA records referring to the same passage map to **one** index document.
- Record `squad_repo_sha, exact_file_sha256, license_receipt_id, source_article_attribution, article_group_id, passage_id, passage_sha256, question_id, question_sha256, answers, gold_passage_ids, split_id, duplicate_status`.
- Predefine split by **article_group_id** rather than by question. Existing published train/validation are *candidates* only, and independence/near-duplicate across article groups is not assumed. Public evaluation labels must not be used for retrieval hyperparameter tuning. If scientific held-out is required, create a genuinely sealed local manifest with deterministic group selection **before** any evaluation, track exclusion/contamination and preserve source descriptions.
- Preserve a fixed index snapshot of eligible corpus passages for both lexical and semantic retrieval; define whether evaluation-group passages are in the index (normally yes for this task, because retrieving from a fixed publicly available collection is the point), but never put evaluation labels or answer suffix in retrieval metadata, title, embedding input or tuning features.
- Before authorization: agree exact set of allowed files, which fields may be cached, redistribution policy and attribution provenance. After separate permission, materialize data, compute byte hashes and group/split manifest; this future act is not claimed here.

**G2 verdict:** `REAL_CORPUS_REPO_AND_REVISION=IDENTIFIED`; `CORPUS_MATERIALIZED=NO`; `DATA_RIGHTS_APPROVED=NO`; `GROUP_SPLIT_AND_GOLD_LABELS=NO`. **Blocks `LOCK_READY`**.

## G3 — R_gold: scientific competence prereg candidate, fixed in one review

**Backbone:** `Qwen/Qwen2.5-0.5B-Instruct@7ae557604adf67be50417f59c2c2f167def9a775`, frozen, no EmbeddingGemma in R_gold, no Adapter, no training. Three arms use exactly the same `question`, `answer`, model, Qwen tokenizer and decoding policy: `R0` no evidence; `R_gold` correct original evidence; `R_wrong` unrelated/wrong evidence selected by group-safe, fixed procedure. Gold evidence fits actual context.

**Candidate cohort (not materialized; does not borrow SQuAD published QA for novel facts):**
- **48 independent authored fictional fact groups**, each with one direct question and one semantically equivalent paraphrase: **96 answerable QA**. Each group has new synthetic name/fact combinations not likely memorized by the pretrained Qwen, with human/independent provenance check, no personal/sensitive data and no label hidden in title.
- **12 independent unanswerable fictional groups** with two questions each: **24 no-answer items**, evaluated separately with a fixed `UNKNOWN`/refusal rubric. A Qwen answer in a no-answer group does not enter denominator 96 or positive answer-only NLL.
- **No sample currently generated, checked or hashed**; ownership for any authored/synthetic examples and method of generation must be recorded. No prior science score or TEST label is available.

**Candidate scoring rules, pending reviewer sign-off:**
1. Primary per QA `delta_i = NLL_answer_only(R0,i) - NLL_answer_only(R_gold,i)`, in **nats/answer token**. Average the 2 questions in each group; average group means to `Delta_gold`. Same answer token IDs, Qwen chat-template prompt and EOS policy for each paired arm.
2. Candidate minimal practical effect `delta_min=0.10` nats/answer token; evidence of exceeding it requires **lower endpoint of a two-sided 95% paired group-bootstrap interval >0.10**, resample 48 groups with replacement **10,000** times, bootstrap seed `20261108`. Prior criterion `mean>=0.10 && CI_lower>0` is **not equivalent** to this claim.
3. Secondary safety/competence candidates: exact-match `EM_gold>=0.60` and `EM_gold-EM_R0>=0.10` absolute; `mean_group(NLL_wrong-NLL_gold)>0` evidence reliance diagnostic. For the 24 no-answer items, candidate guardrail `<=6` hallucinated assertions; this small sample is **only diagnostic**, not a population safety guarantee.
4. Define answer normalization/token boundaries fully before science: pin `apply_chat_template(add_generation_prompt=True)`; build prompt IDs and answer IDs under explicit fixed separator and add-special-tokens rule; causal logits at position before first answer token predict first answer token; mask prompt target positions `-100`. Check sentence generation Exact Match and teacher-forced answer NLL separately, no outcome-dependent prompt tuning.
5. **Precondition:** no truncated evidence, skipped target tokens, missing answer IDs or loss NaNs; invalid/missing samples trigger `INCONCLUSIVE_DATA_INTEGRITY` rather than drop-and-replace after results. A fixed decoding policy, stop tokens, Unicode/case/punctuation normalization and no-answer parser still require reviewer-approved detail.
6. If predefined criteria pass, `R_GOLD_PASS_COMPETENCE`; if valid dataset but insufficient model capability, `MODEL_CAPABILITY_GAP`; with missing/uncertain evidence, `INCONCLUSIVE`. R_gold failure is **not** EmbeddingGemma failure. R1–R3 may proceed only after `R_GOLD_PASS` in the same D1 authorization.

**Review caveat:** `48 groups`, `0.10`, `0.60`, `<=6/24` and CI thresholds are **proposals**. No power/variance or diagnostic difficulty calibration is available. A protocol reviewer must explicitly accept/reject these **before** seeing any R_gold outputs. If they are inadequate, modify once in the prereg packet on conceptual grounds, not after a run. `R_GOLD_GROUP_MANIFEST=ABSENT`; `SCIENCE_THRESHOLDS_APPROVED=NO`.

**G3 verdict:** `PREREG_METHOD_DOCUMENTED`; `LOCK_CANDIDATE_ONLY`; **not preregistration issued**.

## G4 — R1/R2/R3: one real corpus, coherent retrieval and generation

### Fixed candidate arm definitions

| Arm | Method | Primary output | Interpretive boundary |
|---|---|---|---|
| `R1` | `BM25Okapi` lexical retrieval on the same SQuAD passage corpus | `doc_ids`, Hit@3 / MRR@3 / Recall@3 | Retrieval **only**, no separate Qwen generation |
| `R2` | Local `google/embeddinggemma-2` text-only **FP32** query/document embeddings, cosine, same passage IDs | `doc_ids`, identical retrieval metrics | Retrieval only, not an additional GPT generation trial |
| `R3` | Frozen Qwen reads **raw passage text** from the exact locked `R2.doc_ids` | Answer-only NLL, Exact Match, input coverage | **One** text-RAG generation baseline, no vectors injected into Qwen |

**Candidate retrieval policy** for exact lock with source manifest:
- Single `source_corpus_sha`, canonical article grouping, passage de-dup, same candidate set/query IDs for R1 and R2; no extra retrieval stage or privileged scoring for one arm.
- `top_k_primary=3`; `top_k_secondary=5` descriptive only. On SQuAD, use a gold passage ID from `context` for each QA; define all genuinely relevant passages if more than one contains/supports answer. For a **single gold passage**, `Hit@3` is the primary retrieval metric (equivalent to `Recall@3` in that case); `MRR@3` secondary. If multi-gold, prereg macro Recall@3 and make the difference explicit. Do not silently change gold construction after scoring.
- Proposed frozen BM25 behavior: lowercase Unicode `casefold`, extract Unicode word tokens via a fixed regex, **no stemming/no stopword removal**, BM25Okapi `k1=1.2, b=0.75`, rank descending then `passage_id` ascending to break ties. Actual tokenizer/library/version and treatment of Wikipedia markup require a final pin. These are *candidate static parameters*, not tested implementation.
- EmbeddingGemma input: `prompt_name="QuestionAnswering"` for query, document title if real as `title: {title} | text: {content}`, otherwise `prompt_name="Document"` / `title: none`. Use native 768 dimensions with L2 normalization, same model SHA/dtype/prefix policy for every source, 8192-token limit including prefix, one vector per passage/chunk. On T4 choose **FP32** (not FP16). No paid Google API, no hidden hosted embeddings. Document raw bytes and embeddings may only be cached after rights adjudication.
- Retrieval statistic: paired source/article-group `Delta_hit = mean_group(Hit@3_R2 - Hit@3_R1)`, CI from resampling article groups, not questions/tokens. Proposed decision `CI95_lower(Delta_hit)>0` for a superiority claim; failure to exceed this is `NO_EVIDENCE_OF_SUPERIORITY`, not EmbeddingGemma "broken". Sample count, sensitivity and true gold-passages are NOT yet frozen. The alternative value `Delta_hit` can be negative, showing R1 better.
- R3: present concatenated unmodified `R2` evidence chunks in fixed rank order; if `S_SHORT` full evidence fits Qwen context + chat prefix + answer target, no truncate; for `S_LONG` use fixed no-label truncation and report separately. Answer-only NLL teacher-forced with exact Qwen tokenizer, plus EM, source coverage, latency, missing-source count. Never compare NLL to BM25/cosine scores as if units match.
- No adapter `R4/V1` work, no PagedAttention or GQA causal attribution, no fused GGUF during D1. Frozen Qwen checkpoint can be counted only after `R_gold` demonstrates baseline competence.
- Public SQuAD validation is historically public; even with group partitioning, **do not claim pretrained-model contamination-free or new TEST secrecy**. Use it as scoped public-corpus retrieval/QA evaluation; any future confirmatory sealed TEST needs separately preregistered source/split policy before inspection.

**G4 verdict:** `PROTOCOL_TEMPLATE_SPECIFIED`; `DATA_GROUP_MANIFEST=ABSENT`; `GOLD_PASSAGE_MAP=ABSENT`; `SOURCE_COUNT_AND_BM25_LIBRARY_PIN=INCOMPLETE`; `STATISTICAL_THRESHOLDS=REVIEW_PENDING`. **Blocks `LOCK_READY`** for a scientific comparison.

## 5. One finite decision: status of the four receipts

| Receipt | Evidence achieved in this work | Missing information that cannot be invented | Decision |
|---|---|---|---|
| `CLOSE-G1` | Two exact model revision IDs, model cards/Apache 2.0, Google precision/prefix policy, SHA256 strategy | Exact-revision policy/license receipt and versioned file inventory acceptance | `PARTIAL` |
| `CLOSE-G2` | **Real corpus identified**: SQuAD pinned at `7b6d24c440a36b6815f21b70d25016731768db1f`, public split/schema/license | Project-level rights/attribution decision, real file+article-group+split manifest and gold passage labels | `HOLD` |
| `CLOSE-G3` | Complete candidate 48/12 groups, ΔNLL bootstrap, EM/negative rules, ordering | Actual authored group samples/provenance and independent acceptance of power, thresholds and normalization | `HOLD` |
| `CLOSE-G4` | Concrete BM25 and local embedding retrieval arms, top-k, doc-ID and answer-only NLL policy | Actual index/doc/query/gold mapping, group counts, exact tokenizer/library pin and final statistical rule | `HOLD` |

### Single adjudication outcome

`LOCK_READY` **requires all four receipts complete with observable rights, sample identity and prespecified metrics.** Current evidence fails G2/G3/G4, and G1 retains one documentary gap. Therefore **`HOLD_WITH_FINITE_GAPS`**, **not** `LOCK_READY`. No new mini-permit/protocol loop. A future combined packet should add only the four missing evidence types and receive one decision.

**No premature requirement for downloaded model SHA256:** this is specifically deferred to **one integrated technical preflight** on Tesla T4 after a separate authorization for downloading models and using compute; it does not have to precede design review.

**Execution order unchanged (NOT performed):** `G1–G4 prereg LOCK_READY → download/compute rights decision → one zero-science T4 integrated preflight (weights digests, FP32 finite vectors, tokenizer/shape, RAM/VRAM/Drive/resume/abort) → D1 scientific admission → R_gold on Qwen → if R_gold PASS then R1/R2/R3 under same D1 authority → independent science QA → append-only lineage for real science`.

**TTM-Small-4M T4 = highest execution priority.** EmbeddingGemma branch stays independent. The only change in this turn is an additive research document, with no executable work.

## 6. Next action (one consolidated continuation, not small technical gates)

`TTM_EMBEDDINGGEMMA2_D1_COMPLETE_FOUR_REAL_RECEIPTS_AND_REVIEW_ONCE` — package project-approved SQuAD rights/attribution or another genuinely licensed corpus, a real grouped SQuAD+R_gold sample manifest, sign-off of R_gold and retrieval thresholds, and the exact-revision model policy receipt in one place; then issue one `LOCK_READY`/ `HOLD_WITH_FINITE_GAPS` decision. If a rights owner/corpus cannot be established, **hold science**, do not substitute synthetic-only data while claiming real-world retrieval evidence.
