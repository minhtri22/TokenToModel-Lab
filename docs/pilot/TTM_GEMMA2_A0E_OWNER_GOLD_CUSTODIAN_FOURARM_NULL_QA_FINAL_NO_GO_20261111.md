# TTM GEMMA2 A0E — một quyết định cuối cho Gold Custody + 4-Arm Pre-execution

**Operation:** `TTM_GEMMA2_A0E_OWNER_GOLD_CUSTODIAN_SEAL_AND_FOUR_ARM_FROZEN_INPUT_NULL_QA_FINAL_ADMISSION`  
**Date:** 2026-11-11  
**Branch:** `research/ttm-gemma2-token-alignment-pretraining-causality-20261111`  
**Mode:** read-only source and contract QA, no inference/training/GPU, no consumed TEST/H768/OOD256  
**Final decision:** `NO_GO_HOLD`; T4 2×2 **NOT AUTHORIZED**.

## 1. Kết quả kỹ thuật thực tế

A0D owner-local official class and original T1 mapping remains PASS, not rerun. The previously frozen A0E 138/37 score-blind mask and Cambridge original SimVerb-3500 source parity remain PASS.

Independent input-byte QA on the **existing privately mounted** source archives is PASS **20/20**. It SHA-checked masked lexical roster, Cambridge parity receipt, original T1 manifest, frozen private source ZIP, candidate PT, original checkpoint PT, TRAIN/VAL windows, embedded candidate source pin and donor hash metadata. `torch.load(weights_only=True,map_location='cpu')` was used **only to inspect existing tensors**, not to instantiate a model or call forward. Real shapes: donor rows 2048×512, projector 256×512, valid mapped mask 1917; EOS excluded, all inspected source/projector numbers finite.

TRAIN contains 2048 distinct **split-local** story indices, 2691 windows and 498287 target tokens. VAL contains 256 story indices, 328 windows and 61122 targets. No *exact* token-window hashes or whole-story-windowpack aggregate hashes matched between the two splits. These are **not raw story fingerprints**; the story indices have local namespaces and raw source near-duplicate / membership audits remain HOLD. Do not misinterpret index-number overlap as story leakage or exact-window noncollision as a proof of no near duplicates.

Independent negative QA changed one T1 manifest byte in a temporary copy, received `HOLD_FAIL_CLOSED` with exit code 2, and deleted the altered copy. No original source changed.

- Source audit Python SHA256: `0a5bb40a1a8d0f7b9bf2bf9cb57830e5c8d7764081bc5e424c3baa6509199778`
- PASS 20/20 result SHA256: `464957f7e7602013896842b3a250846176a38e66d97dfce25952cd0bfa414010`
- Negative QA result SHA256: `7f3193db4b9cdcba628861447ba5d46cb2e1a70154abab8e91874d5469809d60`
- Exact 7-file redacted local packet ZIP SHA256: `f5220de7098583c1b96d676852e0ba7dfaa1ee9e8e53a681e86bbd0b91215f81`.

No private source raw bytes, TRAIN windows, donor arrays or label scores are committed to public GitHub. The packet contains only redacted evidence, scripts and unsigned custody/run-manifest templates.

## 2. Gold labels: source bytes pinned != independent custody

Original gold source: University of Cambridge Apollo SimVerb-3500 dataset, license **CC BY 4.0**, canonical `SimVerb-3500.txt` SHA256 `b58f68454cf9354b94ecd8bfd778ff2cc784a25fc7dca02bc695319ad2b4157e`. Frozen 138/37 pair roster hashes already matched.

The public source is **not** sequestered from model developers, and no independently controlled label custodian has signed source-pair mapping, scorer SHA, access controls, sealing timestamp or unblind log. The template `A0E_GOLD_CUSTODY_SEAL_UNSIGNED.json` truthfully records null/missing fields rather than fabricating a custodian or signature. `HOLD_NO_INDEPENDENT_GOLD_CUSTODY`.

Because SimVerb was public in 2016, it might appear in the donor's pretraining web corpus (official cutoff January 2025). Independent custody in 2026 **cannot undo possible donor training-set contamination**. A strong semantic causal claim would require stronger prospective independent human labels and controls. Existing SimVerb test can at most be exploratory evidence about association.

## 3. Official donor and real 4-arm requirements

Model card and Hugging Face metadata list EmbeddingGemma 2 **Apache 2.0**, pinned official pretrained safetensors SHA256 `197a32965d4b1105faf060417baa899e193fb73cd401f42ec9295234d5553d79`. The *same SHA is embedded* in frozen `candidate_initialization.pt`, and SHA of candidate bytes checked. That is **PASS of hash metadata cross-consistency only**, not a fresh byte-to-byte hash of the 1.49GB full original safetensors nor an independent tensor-extraction equivalence check.

N-A/N-C input embeddings for untrained official `EmbeddingGemma2TextModel` are **not frozen as real tensor SHA per seeds 61031–61033**. Do not substitute previous synthetic parameter topology mirror or claim A0D CPU class-instantiation proves the source rows are ready.

P-C/N-C source-specific constrained null input matrices, 4-arm matching of norms, covariance, TRAIN-only frequency/morphology/topology, aligned projection and lexical disruption tests have **NOT** been executed on both P and N. Earlier A0B P-only mathematical PASS does not close this gate. The frozen experiment remains the same **P-A/P-C/N-A/N-C**, train seeds `41031,41032,41033`, N init seeds `61031,61032,61033`, null seeds `51031,51032,51033`; four arms × three seeds × 512 steps × 4096 target tokens = **25,165,824 target-token presentations**. No optimizer/scorer/VAL-runner complete SHA package or admitted A0E checkpoint baseline is bound yet.

**Scientific identifiability finding:** original TTM MappedGemmaInput has `nn.Embedding.from_pretrained(...,freeze=True)` and a **trainable** `nn.Linear(512,256,bias=False)` projector. A0B null residual transforms preserve `X_i P_0^T` at initialization: `X_i' P_0^T = X_i P_0^T`. After updating the projection, `X_i' P_t^T` can diverge from `X_i P_t^T`, even absent an identified semantic mechanism. Positive `D_origin` with trainable projector is therefore not, by itself, identifiable as pure pretrained semantics. Require prospective frozen-projector negative control / owner-reviewed protocol amendment before making the stronger claim; don't silently modify prereg thresholds.

## 4. Single integrated gate

| Gate | Required item | Verdict |
|---|---|---|
| G01 | A0D real class/T1 provenance | PASS |
| G02 | SimVerb publisher CC BY | PASS |
| G03 | Publisher↔mirror exact bytes | PASS |
| G04 | Score-blind A0E 138/37 roster | PASS |
| G05 | TinyStories original raw owner rights, near-duplicate checks | HOLD |
| G06 | Independent signed blind gold custody | HOLD |
| G07 | Donor pretrained corpus benchmark exclusion | HOLD |
| G08 | Original donor source tensor extraction bytes check | HOLD (metadata matches) |
| G09 | Frozen official nonpretrained N source SHA × 3 | HOLD |
| G10 | Paired P-C/N-C null geometry + selective mechanism QA | HOLD |
| G11 | A0E checkpoint/optimizer/sampler/VAL scorer/run manifest | HOLD |
| G12 | Prespecified 4-arm design and budget | PASS DESIGN ONLY |
| G13 | Independent integrated T4 execution permit | HOLD NO-GO |

**Total: 5 scoped PASS, 8 HOLD, 0 science FAIL.** The 20/20 source QA does not upgrade these 8 scientific gates.

## 5. Bước thực hiện tiếp theo

`TTM_GEMMA2_A0E_FINAL_OWNER_CUSTODY_SIGNATURE_AND_N_SOURCE_MATCHED_NULL_EVIDENCE_SINGLE_READBACK`

One bounded readback/admission: independent custodian receipt, fresh original-source chain, official seeded N rows, actual matched P/N null and frozen projection negative control, exact run code/optimizer/sampler/scorer, and owner raw TRAIN/VAL rights/near-duplicate evidence. If any mandatory scientific gate remains HOLD: **NO-GO** and **no T4**. If every mandatory gate passes, make one separate explicit T4 authorization; do not dispatch automatically.

**Governance:** main unchanged; `lineage.md` append-only unchanged; L0020/L0021 preserved and no L0022; no re-execution of consumed TEST/H768/OOD256.
