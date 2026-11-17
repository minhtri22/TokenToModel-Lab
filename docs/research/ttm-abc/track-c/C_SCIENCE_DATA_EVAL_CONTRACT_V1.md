# C_SCIENCE_DATA_EVAL_CONTRACT_V1 — Agent C

**Operation:** `TTM_C_SHARED_SCIENCE_DATA_EVAL_CONTRACT_DESIGN_ONEPACK`  
**Date:** 2026-11-17  
**Mode:** DESIGN_ONLY · NO_SCIENCE · NO_GPU · NO_NEW_TEST · NO_MERGE  
**C design outcome:** `C_SCIENCE_CONTRACT_DESIGN_COMPLETE_SCOPED`. Joint alignment `HOLD_CCR_01_ACK_PENDING`. Neither authorizes execution.

## 0. Frozen authority and byte-domain separation

| Source | Exact source SHA / Git blob | Scope |
|---|---|---|
| PM shared contract | commit `403491b698ba6586193f2ff2ae00c4441c10c595`, blob `d7fbc02a45b1d1a85cfe9b9594ae88fee495a9e1` | A→C→B→PM, evidence index and R0–R8 |
| C contract ACK | [Issue #32 ACK_C](https://github.com/minhtri22/TokenToModel-Lab/issues/32#issuecomment-6937623901) | received contract and exact A packet |
| A packet | `7639a53b9d76e16abfa4211cf239c5c3e9d6c940`; A requirements blob `3de320f1e734c7610fb750477803b082fefff753` | 37 logical measurement/custody fields, 65 negative + 3 positive future checks, 0 executed |
| Accepted A I1 source | `ec197b5f00d3a037420390edd11ee55047e1d37f` | M0 v3 measurement `PASS_SCOPED`, not SFT science |
| A V4 reviewed design | `e6746184603f038b49d1e7d472367b6354474ba2` | `DESIGN_ACCEPT_SCOPED`, I2 release HOLD |
| C source PR #35 | `00afd25aa2234e30f7602592d49d5d9f2947965b` | M4 `PASS_DESIGN_SCOPED`, rights/gold HOLD |
| BC synthetic PR #36 | `09de6a46574146d863f416e056fcf01091f3efb8`, code `a83e1526bce842761f3051dad28b90a55395a6aa` | PM `BC_INTERFACE_PASS_ENGINEERING_SCOPED` trusted synthetic CPU only |
| C cross-contract clarification | [CCR-01 Issue #32](https://github.com/minhtri22/TokenToModel-Lab/issues/32#issuecomment-6937644143) | EOT/EOS SFT CE vs byte-only evaluation; A/B/PM ACK pending |

**Do not collapse three byte domains.** A ReleaseTBSV4 / CompletionEnvelopeV4 uses closed ASCII canonical, RAW and TAG SHA domains; BC/v2 synthetic SFT uses UTF-8 sorted compact JSON + exactly one final LF and seven raw artifact SHA; historical TRAIN-only T4 BPE is not the BC/v2 byte tokenizer. No field alias, no checksum substitution, no new release wire. Original Q001 one-shot H_SLOT_V3 = `581fd3acf137c28300813fc48501ff8ee243984588978ae64423fffc044bbe0f`; no I2 claim/nonce/permit/release.

## 1. Scientific questions and falsifiers

| Study | Scientific estimand, prospective only | Falsifier / stop condition | Status |
|---|---|---|---|
| **I2, original frozen Q001** | original preregistered endpoints and thresholds; no redefinition | invalid owner authority, source custody or ledger; negative original result remains negative | `I2_NOT_EXECUTED`, release HOLD |
| **Small‑4M** | fresh family-heldout teacher-forced next-token NLL/bpb and separately named copy/entity/format outcomes | leaked source family, fluent wrong binding, template-only/copy baseline, floor/ceiling | NEW_STUDY, not preregistered |
| **Data × Compute D0/D1/D2** | paired data-dose effect at matched measured FLOPs, distinct TRAIN families/positions, repeated exposures counted separately | equal token exposures but unequal FLOPs, source distribution drift, near-duplicate across split | DESIGN_ONLY |
| **Objective O0/O1** | next-token objective versus prereg alternative on same data, budget and checkpoint lineage | extra negatives, additional forward passes, changed scorer or tokenizer unaccounted | DESIGN_ONLY |
| **SFT vs base/continuation** | fresh machine-gold instruction/slot/abstention response and answer-only likelihood with same real base/decoder | unmasked prompt loss, wrong-yet-fluent rewarded, leaked templates, incompatible weights | BC/v2 proves only synthetic engineering, not real SFT |

Historical T4 numbers **reported, not independently remeasured**: 3,749,376 parameters; 1,024 updates × 4,096 target labels = **4,194,304 exposures** per arm/seed; approximately 498,287 distinct TRAIN target positions; historical VAL NLL ~3.522339 versus bigram ~3.997231. One historical seed/checkpoint is not a newly randomized D0 arm. Planning claims of 44M tokens or ~13 min on T4 are hypotheses, not measured budgets.

## 2. Data admission, raw custody, family split, leakage

Required **private per-source evidence**, not supplied here: upstream URI/revision and collection time; license exact bytes/id/SHA and applicable clauses; explicit permissions separately for download/read/local train/evaluation/derived weights/third-party raters/publish aggregate/redistribute; authenticated rights custodian or HOLD; immutable raw SHA256/byte length/encoding; PII and copyright review/disposition; source/family/translation/author/template grouping method and custody. Internal research declaration is not blanket redistribution or remote rater permission.

Gates in order: (1) source and rights signoff before byte access, (2) raw source hash, (3) quarantine uncertain content, (4) group whole story/author/paraphrase/translation/template family, (5) family-disjoint TRAIN/VAL/DEV/FRESH_HELDOUT by frozen sealed assignment, (6) exact SHA + normalized-text NFC/casefold/whitespace + ngram/MinHash/semantic near-duplicate candidate detection, separately adjudicated hard cases, (7) freeze eligible/excluded/family denominators, (8) TRAIN-only tokenizer training manifest SHA and proof VAL/TEST excluded, (9) heldout truth and reader custody independently sealed, (10) no reading fresh TEST before prereg and owner GO.

Every source family occurs in **exactly one split**; ambiguous family/near-dup ⇒ quarantine or HOLD, not post-hoc reclassification after outputs. Record raw TRAIN bytes, unique TRAIN family count, distinct tokenizer-scoped valid target positions, repeated exposure count, split SHA/length, distribution of length/language/domain/typed entities and full excluded/eligible denominator. Publish aggregate/hash only, not private text or reversible heldout IDs.

**Spent test rule:** historical TEST64, FRESH16, FINAL24, I1 80-case fixtures and any previously inspected probes are not fresh confirmatory heldout. They may inform exploratory limitations only. A synthetic metadata checker that detects exact duplicate of toy strings is not a real near-duplicate/rights audit.

Status: `C-G1=HOLD_REAL_DATA_UNAVAILABLE`; rights, real split SHA, family near-dup, tokenizer TRAIN lineage and fresh heldout source bytes `UNVERIFIED`.

## 3. Loss contract — stable full-vocab scoring, strict byte denominator

For each prospectively fixed teacher-forced valid data token i, compute `NLL_i = logsumexp(all_vocab_logits_i) - logits_i[gold_i]` in **nats**; reject nonfinite logits and mismatched vocabulary/target/shape/shift. Candidate-only log-softmax cannot replace full-vocab NLL. Define logical endpoints, not a new B runtime schema:

- `c_loss_nats_required`: finite float64 semantic, **sum of NLL on valid genuine text data targets only**, not an average and not including special-token CE in this primary endpoint.
- `c_valid_bytes_required`: uint64 positive, **raw UTF-8 text bytes exactly covered by those same evaluated targets**. For BC v2 content byte IDs 0..255, b_i=1 per qualified assistant text byte; structural BOS/EOT/EOS/PAD/role tokens contribute b_i=0. For general BPE, a token may cover multiple bytes or cross excluded boundaries; B must prove tokenizer exact SHA and token-to-byte offsets/coverage before using this denominator.
- `c_val_bpb_required = c_loss_nats_required / (ln(2) * c_valid_bytes_required)`: bits per genuine UTF-8 text byte, computed as aggregate **total nats / total bytes**, not unqualified average of per-item ratios. Report alongside `nll_per_valid_data_token = c_loss_nats_required / valid_data_token_count` (nats/scored data-token). NLL/token and bpb are different units and populations.
- **NTP raw-text bpb** uses prespecified complete raw heldout text target spans; **SFT answer bpb** uses assistant-content raw target spans. They are separate endpoint definitions and must not be compared as identical studies.
- `a_gold_nll` from original A M0 v3 is **one next-token gold NLL** (full vocab), with rank/top1/tie logic; not C val_bpb, not fresh model evidence.

**Unchanged B/C v2 SFT training mask:** `x=ids[:-1]`, `y[j]=ids[j+1]` if structurally derived assistant-target mask at j+1, else `-100`. Supervise **assistant content bytes, assistant EOT, final EOS**. Ignore system/user/header/user EOT/PAD/BOS. Direct *prompt target CE weight* is zero; gradients from assistant CE through prompt context embeddings are permitted (not forced zero). Do not detach prompt.

**Separate prospective scoring selection view:** for primary SFT answer bpb include **only assistant UTF-8 data bytes** as target positions; exclude EOT/EOS and all other specials from both `c_loss_nats_required` and `c_valid_bytes_required`. Keep SFT training CE (including EOT/EOS), counts of valid SFT targets, and stop-token CE **separately named**. This is a logical evaluation mask over the **existing** BC v2 wire, **not** a new v2 serialization or retraining target change. It awaits B evaluator feasibility.

**HOLD cases:** no valid bytes; all-ignore; boundary-straddling BPE with unknown offsets; UTF-8 normalization mismatch; special EOT/EOS included as raw bytes; drop EOT/EOS from SFT training targets; user/header CE exposed; wrong shift; stale tokenizer/checkpoint/split SHA; candidate-set-only loss; source/gold selection after outputs. No padding with invented zeros. Formal clarification under [C-CCR-01](https://github.com/minhtri22/TokenToModel-Lab/issues/32#issuecomment-6937644143) pending A/B/PM ACK, rather than editing historical A/BC schemas.

## 4. Teacher-forced probes, ending selection, validity

- **Next-token modeling:** predeclared raw heldout family population and byte-aligned full-vocab NLL/bpb; deterministic known-answer logits, random labels, random-init and shuffled-source controls.
- **Copy/induction:** matched prompt+answer span, exact known key/value; hard negative swapped key, copy-only nearest-string baseline; same context length and tokenization or declared length confound.
- **Entity–attribute binding:** source-derived machine slot gold; paired counterfactual entity swap and irrelevant-edit controls, fluent wrong binding negative. Primary full-vocab teacher-forced gold likelihood/rank or exact slot, not unrestricted subjective fluency.
- **Ending selection:** candidate endings from **independent source/gold**, before model output; same bytes/token lengths if possible, or prespecified length-normalized conditional sequence likelihood with length effect reported. Negatives swapped endings, identical candidates, order changes, leakage and unequal tokenization. Candidate-only accuracy is secondary (A's full-vocab rank is separate).
- **Instruction/format/abstention:** machine-valid JSON/slot schema and unknown/contradictory cases; explicit refusal/abstain correctness, literal malicious role-looking text negative. Decoding-specific stop/repetition with frozen temp/top-p/max length/seed is secondary to teacher-forced likelihood.
- **Controls:** known exact correct and wrong answers, nonfinite/shape/tie checks, null/counterfactual, role-mask forgery, random oracle, floor/ceiling and family leakage. If all responses are zero or ceiling, or construct fails control separation, **HOLD_CONSTRUCT**, no threshold revision after outputs.

Gold is independently source/fact-derived **before candidate model outputs**, with task family/id, answerability, canonical answer/allowed alternatives, ambiguity policy, source raw SHA, independent author/custodian and any gold revisions. Missing gold ≠ fabricated UNKNOWN. If gold writer saw outputs or source cannot be checked: `HOLD_GOLD_UNPROVEN`.

Proposed K0–K4 ordinal rubric is **not validated**: K4 exact binding+format; K3 binding correct with harmless extras; K2 entity correct/attribute wrong; K1 fluent wrong; K0 copy-only/loop/off-task. Machine exact correctness should be primary where feasible. Independent calibration needs known-answer K0–K4 positive/negative and hard fluent-wrong examples, floor/ceiling and false-correct rate before real scoring.

Human/AI rater conditions: at least two blinded independent raters/sessions for nontrivial semantic scores, separate arm/blind order and custody, SHA-256 of exact bytes delivered (rubric/system/instructions/item/output/order/gold visibility), disagreements and independent adjudicator predeclared, weighted agreement with prevalence caveat, positive/negative performance and CI. Rater agreement is **not** truth. AI self-review is not independent human attestation. Private sources may not leave permitted custody. Current actual gold, rater qualification and truth rights = `NOT_EXECUTED`.

## 5. Data × Compute, checkpoint and prereg

Proposed D0≈0.5M, D1≈2.1M, D2≈4.2M *independent TRAIN target positions*, fixed distribution/tokenizer/model, seed-paired initialization, total supervised exposure count and measured compute. Distinguish (a) raw independent source count, (b) unique TRAIN token/target positions, (c) **repeated** exposure count, (d) update steps and measured FLOPs. Matched exposures alone do not match FLOPs or entropy. O0/O1 objective-only includes extra passes/negatives in FLOPs. SFT versus base/NTP continuation must share the *actual* B real weights/codec and disclose sample information budget. Architecture/capacity changes require separate prereg and checkpoint version.

Required per-arm/seed ledger: exact source/family/split SHA, tokenizer TRAIN-only SHA, real model weights+config SHA, sampler seeds/order, unique TRAIN positions, total target exposures, batch×context×accum×steps, optimizer/mixed precision, step-specific checkpoint sampling and validation-only selection rule, CPU/GPU/RAM peak vs hard cap and watchdog, measured FLOPs and GPU-seconds/wall time including data loading/evaluation. Seed proposal 5/12 is NOT frozen or statistically powered; freeze effect size/power from separate dev pilot. Unit of uncertainty is independent source-family and paired seed, not repeated token exposures. Predeclare primary outcome, multiplicity correction, 95% clustered confidence interval or equivalent, stopping/retention/exclusions. Wide CI crossing zero is **INCONCLUSIVE**, not equivalence.

Prospective prereg only after real source rights/gold/split sealed, tokenizer and B real checkpoint/resource verified, independent controls qualified, TEST reader 0, owner authority. Freeze hypothesis/arms/sources/seeds/thresholds/negative controls and primary endpoint before fresh outputs. No actual prereg freeze, fresh TEST access, model output, I2 dispatch, optimizer, GPU or science in this operation.

## 6. B-facing logical requirements and owner boundaries

C owns scientific question, gold, rights/splits, target mask *meaning*, byte denominator, validity, raters/prereg. A owns original M0 v3 scorer, signed V4 ASCII RAW/TAG release and global I2 ledger. B owns real weights/config SHA, tokenizer and T4 BPE compatibility, actual C→B implementation mapping, logs and native compute/hard-resource proof. PM alone adjudicates integration/owner GO/HOLD. C does not create B runtime schema.

A complete **37-of-37** logical field crosswalk and additional B-facing field definitions (types, units, byte/hash domains, validation and negative cases) are in [C requirement registry](../../../../artifacts/ttm-abc/track-c/C_SCIENCE_REQUIREMENTS_AND_A_C_COMPATIBILITY_20261117.json). Unknown values remain `UNVERIFIED`.

B must furnish: actual trained real checkpoint weights SHA + params/config/optimizer lineage, tokenizer raw SHA and TRAIN source manifest with byte alignment, explicit T4 BPE vs BC/v2 mapping PASS/HOLD, source/family split SHA and byte count, valid target/structural masks and full-vocab CE nats, unique TRAIN positions vs repeated exposures, per-checkpoint sample exposure and selection policy, measured FLOPs/time/host RAM/VRAM/resource cap evidence. Synthetic BC/v2 metadata-only checkpoint **does not** stand in for real weights. If absent: `HOLD_B_VERIFICATION`, not a numeric guess.

PM index has exactly logical fields: `track, artifact_kind, git_url, exact_commit, git_blob_sha1, raw_sha256, domain_tag, origin_actor, review_actor, gate_status, scope, executed, limitation`; these do **not** form a new on-disk receipt. Domain tags `A/V3` / `A/V4` / `BC/v2` / `none`; no cross-domain alias, and unknown raw digests explicitly `UNVERIFIED`.

## 7. Completion, gates and single handoff

Design `C_SCIENCE_CONTRACT_DESIGN_COMPLETE_SCOPED`, **not real data admission**. R2 rights/splits and R1 scientific gold/rater remain HOLD; R3 real weights/codec and R4 native resource `HOLD_B_VERIFICATION`; R6 `DESIGN_ONLY_NOT_PREREGISTERED`; R7 real independent QA `NOT_EXECUTED`; R8 owner `HOLD`. I1 prior scoped PASS and BC/v2 synthetic PM engineering PASS retained exactly.

C-CCR-01 remains open for A/B/PM interpretation. If A insists EOT/EOS are ignored as SFT training CE targets (versus byte-only bpb), joint status `HOLD_CONTRACT_ALIGNMENT`, and any schema change needs a new version and exact independent proof; never silently overwrite v2.

**Bước thực hiện tiếp theo duy nhất:** `TTM_B_SHARED_EXACT_CHECKPOINT_TOKENIZER_RESOURCE_FEASIBILITY_AND_COMPATIBILITY_DESIGN_ONEPACK`. PM will thereafter adjudicate one integrated R0–R8 packet. No B/A implementation, no model forward, no source corpus download, no real SFT, I2, historical TEST, GPU, signatures, PR merge, main or lineage modification.
