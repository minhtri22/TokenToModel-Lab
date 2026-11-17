# Agent C — C_R0_R1_R2_R3_R6_R7_READINESS

**Operation:** `TTM_C_SHARED_SCIENCE_DATA_EVAL_CONTRACT_DESIGN_ONEPACK`  
**Source / scope:** PM charter `403491b698ba6586193f2ff2ae00c4441c10c595` blob `d7fbc02a45b1d1a85cfe9b9594ae88fee495a9e1`; exact A packet `7639a53b9d76e16abfa4211cf239c5c3e9d6c940`; C base `00afd25aa2234e30f7602592d49d5d9f2947965b`; B/C v2 `09de6a46574146d863f416e056fcf01091f3efb8`. **SOURCE_ONLY / DESIGN_ONLY**.

## R0–R8 ownership and true evidence state

| Gate | Current C assessment | Exact evidence/requirement and remaining veto |
|---|---|---|
| **R0 — source and dependency** | `PASS_C_INPUT_SOURCE_SCOPED` | PM/A/C/B Git SHAs and A 5 blob pins read, C ACK Issue #32 #6937623901; no merge; B to evaluate exact dependency/weights later |
| **R1 — measurement + gold** | `A_I1_PASS_MEASUREMENT_SCOPED / C_GOLD_HOLD` | A I1 source `ec197b5f00d3a037420390edd11ee55047e1d37f` and past scoped QA validated scorer **only**; no authentic new gold/rater qualification |
| **R2 — rights, lineage and fresh split** | `HOLD_SOURCE_RIGHTS_SPLIT` | No authenticated real source license/operation rights, original sample bytes, private family manifests, near-duplicate results or sealed fresh heldout |
| **R3 — real checkpoint / tokenizer** | `HOLD_B_VERIFICATION` | BC/v2 synthetic 7-SHA + metadata-only checkpoint not actual real trained weights. T4 BPE ≠ proven BC/v2. Need actual weight bytes/config and tokenizer/byte alignment |
| **R4 — host resource and budget** | `HOLD_B_VERIFICATION` | Native measured FLOPs/throughput/hard RAM/job-object/VRAM/guard unavailable for proposed study; B-M3 historical scoped PM PASS/V3 HOLD and reviewer peak dissent not transferable |
| **R5 — A V4 release receipt** | `A_DESIGN_ACCEPT_SCOPED / NATIVE_HOLD` | Separate A RAW/TAG digests; policy_epoch signed Ed25519 trust root; handle ancestry, atomic no-overwrite, power-loss, one-shot ledger and signer custody not native proven |
| **R6 — scientific prereg/eval** | `DESIGN_ONLY_NOT_FROZEN` | C question/byte denominator/gold/rater design supplied; actual study sample/threshold/power/arms/seed/TEST reader freeze NOT_EXECUTED |
| **R7 — final candidate QA** | `A_SOURCE_DESIGN_ONLY / REAL_QA_NOT_EXECUTED` | A 65 negative + 3 positive planned, 0 executed; BC/v2 synthetic PM distinct 12/12 each OS is a **separate old engineering gate**; no real study independent QA |
| **R8 — owner decision** | `HOLD_OWNER_RELEASE` | Neither C nor B nor A issues owner GO; original I2 frozen one-shot and new Small‑4M/SFT may not execute |

**Preserve existing historical conclusions:** A I1 PASS_SCOPED; A V4 DESIGN_ACCEPT_SCOPED; C M4 PASS_DESIGN_SCOPED; BC/v2 PASS_ENGINEERING_SCOPED (trusted synthetic CPU); A I2 NOT_EXECUTED; B-M3 historical PASS with V3 peak-accounting dispute preserved. No retroactive QA relabel.

## A field adoption and C/B contract ownership

A packet `A_TO_BC_REQUIREMENTS.md` Git blob `3de320f1e734c7610fb750477803b082fefff753` has **37 distinct logical fields**: 30 A-owned, 4 C-owned, 3 B/B-C-owned. The machine-readable crosswalk preserves **all 37 original field names, types, units, validation, hold and status** unmodified. C concretizes four fields:

| A requested logical field | C design commitment | Blocked until |
|---|---|---|
| `c_valid_bytes_required` | positive uint64 count of raw UTF-8 text bytes **actually scored** under fixed eval byte-selection mask, exclude roles/stop EOT/EOS/PAD; not source-prompt bytes | B exact tokenizer + alignment / source rights |
| `c_loss_nats_required` | finite float64 sum of full-vocab teacher-forced CE over same *text-data tokens* as byte denominator; not SFT CE including stop tokens | real logits, checkpoint, gold, byte mask |
| `c_val_bpb_required` | finite float64 total_nats /(ln2 × total_valid_raw_bytes); pooled; report nats/data-token separately | valid byte count >0 and same sample universe |
| `c_target_mask_semantics_required` | B/C v2 SFT **training** mask unchanged: assistant text/EOT/final EOS supervised; C prospective **eval-byte** selection excludes structural tokens; explicit +1 shift | A/B/PM acceptance of clarification CCR-01; future B scoring implementation |

C science endpoints are **logical evaluation definitions**, not B/C v3 pack, A V5 release wire, implementation/config, or new model checkpoint schema. Exact V4 release namespace remains A-owned.

**[C-CCR-01](https://github.com/minhtri22/TokenToModel-Lab/issues/32#issuecomment-6937644143)**: A phrase “BOS/EOT/EOS/PAD ignored roles” could conflict with current B/C v2 supervised assistant EOT/EOS *training labels*. C interprets EOT/EOS ignored for **raw-byte bpb metric** only. Never mutate approved v2 wire/labels or old digests; A/B/PM ACK pending. Joint compatibility is `HOLD_CCR_01_ACK_PENDING` until PM adjudicates.

## Scientific falsifiers and evidence requirements

| Construct | Exact proof / negative case | Gate when missing |
|---|---|---|
| Real rights and PII/copyright | per-operation license+human custodian, raw file SHA, quarantine actions | HOLD_SOURCE_RIGHTS_SPLIT |
| Family split and near-duplicates | whole story/translation/paraphrase/author one split, exact+normalized+near-dup clusters, sealed RNG/family manifest | HOLD_LEAKAGE |
| Fresh heldout | no previously viewed TEST64/FRESH16/FINAL24/I1 fixtures; blind source/gold reader custody | HOLD_FRESH_TEST |
| TRAIN-only tokenizer | actual TRAIN family/source SHA vs tokenizer training bytes, validation/test exclusion proof | HOLD_TOKENIZER_LEAK |
| Gold and rubric | independently fact-derived before outputs; known-answer, wrong-fluent, K0–K4 calibration; two raters if subjective | HOLD_GOLD_UNPROVEN |
| NLL + val_bpb | full-vocab finite logits, same valid byte spans/mask/source/weights, no special bytes, actual raw offset map | HOLD_BYTE_DENOM |
| Data vs compute | distinct independent positions vs repeated exposure counts; matched measured FLOPs and sampler seeds, resource limits | HOLD_B_VERIFICATION |
| SFT validity | target +1, prompt CE ignored, assistant text/EOT/EOS trained; answer byte eval excludes stop in metric only | HOLD_MASK_CONTRACT |
| I2 release | owner signed policy epoch + trusted keys, global frozen slot, atomic envelope and ledger; old preflight unchanged | HOLD_OWNER_RELEASE |
| R7 | independent exact B/C/experiment candidate with new real-data rights & host native proof; A native 65/3 not executed | HOLD_INDEPENDENT_REAL_QA |

## Prospective freeze checklist (not done)

Preregister question/estimand, split and rights/PII, raw source SHA and family counts, distinct training positions, tokenizer SHA and byte tokenization offsets, gold and rater package hashes, primary bpb and full-vocab scorer, separate SFT stop-loss report, paired arm seeds and measured FLOPs, resource stop guards, checkpoint selection no TEST, power basis, effect size/CI, family cluster/multiple comparison, historical-test exclusion, consent and owner release. Freeze threshold before any confirmatory model outputs. No arbitrary samples, 44M token budget, T4 13-minute throughput or 5/12 seed examples are upgraded to measured facts.

## Falsifiable outcome and handoff

**Agent C design verdict:** `C_SCIENCE_CONTRACT_DESIGN_COMPLETE_SCOPED`. **Global R0–R8 readiness:** HOLD pending real data/rights, independent gold, B weight/tokenizer/budget, native evidence and PM/owner. **A 65/3:** NEGATIVE 0/65 and POSITIVE 0/3 executed; they remain planned, no false PASS. **C synthetic BC QA** is not scientific proof.

B must return a **single** readback table against A exact packet and C exact requirements, mapping to actual checkpoint/config/tokenizer/source/split/token-NLL/byte-span/compute/resource, with each missing field `UNVERIFIED` or `HOLD_B_VERIFICATION`. PM then reconciles A/C/B once; no micro-permit.

**Only next operation:** `TTM_B_SHARED_EXACT_CHECKPOINT_TOKENIZER_RESOURCE_FEASIBILITY_AND_COMPATIBILITY_DESIGN_ONEPACK`. I2 release, real SFT/GPU, new TEST, merge and lineage remain blocked.
