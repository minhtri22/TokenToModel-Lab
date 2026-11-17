# Agent B — JOINT_COMPATIBILITY_MATRIX_A_C_B · CCR-01 exact C remap

**Operation (same integrated successor):** `TTM_PM_ABC_CCR01_SOURCE_REF_T4_CODEC_INTEGRATED_ALIGNMENT_AND_OWNER_READINESS_READJUDICATION_ONEPACK`  
**Date:** 2026-11-17 · **Result:** `B_REMAP_READBACK_SCOPED` · **Scope:** `SOURCE_ONLY · DESIGN_ONLY · NO_SCIENCE · NO_CODE_EDIT · NO_MERGE`.

## Exact inputs and anti-drift

- **PM shared contract:** commit `403491b698ba6586193f2ff2ae00c4441c10c595`, Git blob `d7fbc02a45b1d1a85cfe9b9594ae88fee495a9e1`.
- **A packet:** `7639a53b9d76e16abfa4211cf239c5c3e9d6c940`; requirements Git blob `3de320f1e734c7610fb750477803b082fefff753` (37 fields). A measurement scoped ACK [#6938396264](https://github.com/minhtri22/TokenToModel-Lab/issues/32#issuecomment-6938396264), no V4/I1 rerun.
- **C previous packet preserved:** `614caff47657ccee43ad10ba06ae8ebb782b4114`; registry blob `64508ace4de057958ccbc9e3c7616a18c022250e` / raw SHA256 `bc4131f172ba2744bd1bfb657846f5e3127175ac15908f46bc9904e3d19add0d`.
- **C new exact candidate:** `4efe93ce0a3910c449972b3f7e9911a004fe2b3c`, machine registry Git blob `364a15d305b71e0c236a27409430f1e27e14aa70`, independently recomputed raw SHA256 `6db387c75e3f2f0ae8b05af65f66cfddf025ad2ba06d562e8645a16f9f0aab1d`; C integrated amendment Git blob `e6a77fcb85fbbf24fd1b25e6459c1f40bbfa8e97`.
- **B source parent:** old PR37 exactly `38e24f4fa1ee1eb5a5e1bec5e3746e98a07e13b5`, original B matrix Git blob `ca484be5ae66340d113fce05c1d0513d0177e7a3`. Existing B PR #34 and accepted B/C v2 PR #36 untouched.
- **PM exact review handoff:** `c18319f312fc56d1d79923570abb9c9df6c6d62f` / handoff blob `c01b028b5c08df42cc481c73516a366555534ad8`.

The only old→new C machine JSON tree change is `$.sources.a_requirements_git_blob`: **wrong A evidence index blob `4f96452215778c3cca1af19bd6d2e3b6506d87d2`** becomes **actual A 37-field requirements blob `3de320f1e734c7610fb750477803b082fefff753`**. Root pins of all other upstream sources are unchanged; the 37 A row hashes and 26 C plus 14 B subset remain unchanged. Old wrong evidence is retained at the historical commit and was not overwritten.

**Count discipline:** **37 A rows + 26 C rows = 63 unique field names**; 14 B-facing assumption rows are a verbatim subset of C26 and produce **77 display rows, not 77 independent fields**. All 77 B compatibility dispositions, owners, types, units, byte/hash domains, validations, negative cases, source-hold states and prior classifications were compared with the original B packet and remain unchanged. Extra source-remap metadata is additive.

## A — 37 original fields, same order and B status

| A exact logical field | Owner | Expected type | Unit | B status | Reason / boundary |
| --- | --- | --- | --- | --- | --- |
| `a_measurement_protocol` | A | string enum | protocol id | `EXACT_MATCH` | Exact logical field meaning and frozen reference pin agree with A's accepted scoped I1/V4 source; does NOT prove a new I2 run, signer, logit, or actual file readback. |
| `a_source_commit` | A | git_sha1_40 | commit | `EXACT_MATCH` | Exact logical field meaning and frozen reference pin agree with A's accepted scoped I1/V4 source; does NOT prove a new I2 run, signer, logit, or actual file readback. |
| `a_scorer_source_raw_sha256` | A | sha256_lower_64 | raw source bytes | `NOT_PROVEN` | Accepted historical SHA is carried from exact A requirements, but original raw bytes are not re-materialized/hashed by B; do not equate reported SHA with new raw custody. |
| `a_fixture_records_raw_sha256` | A | sha256_lower_64 | raw bytes | `NOT_PROVEN` | Accepted historical SHA is carried from exact A requirements, but original raw bytes are not re-materialized/hashed by B; do not equate reported SHA with new raw custody. |
| `a_fixture_manifest_raw_sha256` | A | sha256_lower_64 | raw bytes | `NOT_PROVEN` | Accepted historical SHA is carried from exact A requirements, but original raw bytes are not re-materialized/hashed by B; do not equate reported SHA with new raw custody. |
| `a_train_bpe_raw_sha256` | A | sha256_lower_64 | raw bytes | `NOT_PROVEN` | Accepted historical SHA is carried from exact A requirements, but original raw bytes are not re-materialized/hashed by B; do not equate reported SHA with new raw custody. |
| `a_freeze_receipt_raw_sha256` | A | sha256_lower_64 | raw bytes | `NOT_PROVEN` | Accepted historical SHA is carried from exact A requirements, but original raw bytes are not re-materialized/hashed by B; do not equate reported SHA with new raw custody. |
| `a_case_id` | A | string | case identifier | `EXACT_MATCH` | Exact logical field meaning and frozen reference pin agree with A's accepted scoped I1/V4 source; does NOT prove a new I2 run, signer, logit, or actual file readback. |
| `a_group` | A | enum | group | `EXACT_MATCH` | Exact logical field meaning and frozen reference pin agree with A's accepted scoped I1/V4 source; does NOT prove a new I2 run, signer, logit, or actual file readback. |
| `a_gold_nll` | A | finite float64 semantic | nats/one next-token gold | `NOT_PROVEN` | A M0 v3 scoring algorithm is reviewed historically; no new real checkpoint output or I2 logits, no automatic C SFT metric equivalence. |
| `a_gold_rank` | A | int >=1 | 1-based full-vocab rank | `NOT_PROVEN` | A M0 v3 scoring algorithm is reviewed historically; no new real checkpoint output or I2 logits, no automatic C SFT metric equivalence. |
| `a_greedy_correct` | A | bool | full-vocab top1 correctness | `NOT_PROVEN` | A M0 v3 scoring algorithm is reviewed historically; no new real checkpoint output or I2 logits, no automatic C SFT metric equivalence. |
| `a_full_vocab_tie_abstained` | A | bool | top1 abstention | `NOT_PROVEN` | A M0 v3 scoring algorithm is reviewed historically; no new real checkpoint output or I2 logits, no automatic C SFT metric equivalence. |
| `a_candidate_correct_secondary` | A | bool | secondary candidate-only correctness | `NOT_PROVEN` | A M0 v3 scoring algorithm is reviewed historically; no new real checkpoint output or I2 logits, no automatic C SFT metric equivalence. |
| `a_candidate_tie_abstained` | A | bool | candidate tie abstention | `NOT_PROVEN` | A M0 v3 scoring algorithm is reviewed historically; no new real checkpoint output or I2 logits, no automatic C SFT metric equivalence. |
| `a_context_contrast_logit_margin` | A | finite float64 semantic | logit units | `NOT_PROVEN` | A M0 v3 scoring algorithm is reviewed historically; no new real checkpoint output or I2 logits, no automatic C SFT metric equivalence. |
| `a_source_evidence_commit` | A | git_sha1_40 | commit | `EXACT_MATCH` | Exact logical field meaning and frozen reference pin agree with A's accepted scoped I1/V4 source; does NOT prove a new I2 run, signer, logit, or actual file readback. |
| `a_case_count` | A | uint | cases | `EXACT_MATCH` | Exact logical field meaning and frozen reference pin agree with A's accepted scoped I1/V4 source; does NOT prove a new I2 run, signer, logit, or actual file readback. |
| `a_group_count` | A | uint | groups | `EXACT_MATCH` | Exact logical field meaning and frozen reference pin agree with A's accepted scoped I1/V4 source; does NOT prove a new I2 run, signer, logit, or actual file readback. |
| `a_i1_measurement_status` | A | enum | gate status | `EXACT_MATCH` | Exact logical field meaning and frozen reference pin agree with A's accepted scoped I1/V4 source; does NOT prove a new I2 run, signer, logit, or actual file readback. |
| `a_release_tbs_schema` | A | ASCII literal | wire schema identifier | `ADAPTER_DESIGN_REQUIRED` | A V4 defines trusted ASCII release/signature/raw+tag domains; B prospective runner must consume verified exact A receipt/HANDLE/ledger without rewriting A schema; native/source proof and signer absent. |
| `a_policy_epoch` | A | uint53_positive | epoch count | `ADAPTER_DESIGN_REQUIRED` | A V4 defines trusted ASCII release/signature/raw+tag domains; B prospective runner must consume verified exact A receipt/HANDLE/ledger without rewriting A schema; native/source proof and signer absent. |
| `a_owner_policy_raw_sha256` | A | sha256_lower_64 | trusted policy raw bytes | `ADAPTER_DESIGN_REQUIRED` | A V4 defines trusted ASCII release/signature/raw+tag domains; B prospective runner must consume verified exact A receipt/HANDLE/ledger without rewriting A schema; native/source proof and signer absent. |
| `a_science_slot_v3_tagged_sha256` | A | sha256_lower_64 | global one-shot slot digest | `EXACT_MATCH` | Exact logical field meaning and frozen reference pin agree with A's accepted scoped I1/V4 source; does NOT prove a new I2 run, signer, logit, or actual file readback. |
| `a_payload_raw_sha256` | A | sha256_lower_64 | on-disk receipt file bytes | `ADAPTER_DESIGN_REQUIRED` | A V4 defines trusted ASCII release/signature/raw+tag domains; B prospective runner must consume verified exact A receipt/HANDLE/ledger without rewriting A schema; native/source proof and signer absent. |
| `a_payload_tagged_sha256` | A | sha256_lower_64 | tagged receipt byte stream | `ADAPTER_DESIGN_REQUIRED` | A V4 defines trusted ASCII release/signature/raw+tag domains; B prospective runner must consume verified exact A receipt/HANDLE/ledger without rewriting A schema; native/source proof and signer absent. |
| `a_completion_envelope_schema` | A | ASCII literal | wire schema identifier | `ADAPTER_DESIGN_REQUIRED` | A V4 defines trusted ASCII release/signature/raw+tag domains; B prospective runner must consume verified exact A receipt/HANDLE/ledger without rewriting A schema; native/source proof and signer absent. |
| `a_final_file_id_sha256` | A | sha256_lower_64 | opened-file identity digest | `ADAPTER_DESIGN_REQUIRED` | A V4 defines trusted ASCII release/signature/raw+tag domains; B prospective runner must consume verified exact A receipt/HANDLE/ledger without rewriting A schema; native/source proof and signer absent. |
| `a_one_shot_claim_status` | A | enum | claim state | `ADAPTER_DESIGN_REQUIRED` | A V4 defines trusted ASCII release/signature/raw+tag domains; B prospective runner must consume verified exact A receipt/HANDLE/ledger without rewriting A schema; native/source proof and signer absent. |
| `a_owner_release_status` | A | enum | release gate | `EXACT_MATCH` | Release is explicitly HOLD in A/C/PM; B does not own GO, no permit is inferred. |
| `c_valid_bytes_required` | C | uint64 | UTF-8 bytes | `ADAPTER_DESIGN_REQUIRED` | B masked full-vocab CE and byte-identity toy eval support mathematical intent, but a real teacher-forced answer/data-only mask, raw UTF8 source byte spans, same population and per-token stable logits/offset custody do not exist. |
| `c_loss_nats_required` | C | finite float64 semantic | sum valid target NLL nats | `ADAPTER_DESIGN_REQUIRED` | B masked full-vocab CE and byte-identity toy eval support mathematical intent, but a real teacher-forced answer/data-only mask, raw UTF8 source byte spans, same population and per-token stable logits/offset custody do not exist. |
| `c_val_bpb_required` | C | finite float64 semantic | bits per UTF-8 byte | `ADAPTER_DESIGN_REQUIRED` | B masked full-vocab CE and byte-identity toy eval support mathematical intent, but a real teacher-forced answer/data-only mask, raw UTF8 source byte spans, same population and per-token stable logits/offset custody do not exist. |
| `c_target_mask_semantics_required` | C | versioned schema/ref | mask policy | `ADAPTER_DESIGN_REQUIRED` | Existing BC-v2 training supervises assistant content/EOT/EOS and ignores prompt direct CE; C future byte-bpb excludes EOT/EOS. Needs separately named stop CE and evaluation mask without altering BC v2; CCR-01 A/PM ACK pending. |
| `b_checkpoint_weight_ref_required` | B | immutable ref + sha256 | actual model weight bytes | `NOT_PROVEN` | Only T4/P02 architecture and schema can be pinned; actual trained T4 checkpoint bytes+raw weights SHA+optimizer/config lineage unavailable. BC/v2 checkpoint is metadata-only (NOT_CREATED). |
| `b_tokenizer_compatibility_required` | B/C | versioned test evidence | token IDs/UTF-8 text bytes | `INCOMPATIBLE` | T4 BPE 2048 uses byte IDs0..255, EOS256, merges 257..2047; BC/v2 uses PAD257 BOS258 SYS259 USER260 ASSIST261 EOT262; direct shared-ID mapping fails. Real BPE manifest+offset verification and proposed versioned adapter pending. |
| `b_compute_budget_required` | B | structured finite budget | tokens/steps/time/RAM | `NOT_PROVEN` | 4,194,304 historical exposures from 1024x4096 are documented, but no matched measured FLOPs, 74-second raw timing receipt, new hard RAM/VRAM/child kill/clock evidence for 44M or new science. |

**A-37 status count:** 10 `EXACT_MATCH`, 12 `ADAPTER_DESIGN_REQUIRED`, 14 `NOT_PROVEN`, 1 `INCOMPATIBLE`. The classification `EXACT_MATCH` means scoped frozen names/source semantics only; not newly verified actual raw weights, native release, I2 measurement or owner GO.

## C — 26 additional logical fields, same order and B status

| C exact logical field | Owner | Unit | B status | Reason / negative boundary |
| --- | --- | --- | --- | --- |
| `c_source_rights_matrix` | C | rights by action | `NOT_PROVEN` | This is C/PM-owned real data, truth or rater admission. No authenticated raw source, license, independent gold/heldout, calibration or prereg freeze supplied; B does not invent one. |
| `c_source_raw_sha256` | C | raw source bytes | `NOT_PROVEN` | This is C/PM-owned real data, truth or rater admission. No authenticated raw source, license, independent gold/heldout, calibration or prereg freeze supplied; B does not invent one. |
| `c_source_family_manifest_sha256` | C | family graph manifest bytes | `NOT_PROVEN` | T1/T4 manifest SHA/source contracts exist, but real private source and family/split bytes, rights and TRAIN-only corpus exclusion cannot be independently verified in this packet. |
| `c_split_manifest_raw_sha256` | C | split manifest bytes | `NOT_PROVEN` | T1/T4 manifest SHA/source contracts exist, but real private source and family/split bytes, rights and TRAIN-only corpus exclusion cannot be independently verified in this packet. |
| `c_train_tokenizer_source_manifest_sha256` | C/B | TRAIN-only input bytes | `NOT_PROVEN` | T1/T4 manifest SHA/source contracts exist, but real private source and family/split bytes, rights and TRAIN-only corpus exclusion cannot be independently verified in this packet. |
| `c_family_duplicate_audit` | C | family clusters and counts | `NOT_PROVEN` | This is C/PM-owned real data, truth or rater admission. No authenticated raw source, license, independent gold/heldout, calibration or prereg freeze supplied; B does not invent one. |
| `c_fresh_heldout_custody` | C | fresh cases | `NOT_PROVEN` | This is C/PM-owned real data, truth or rater admission. No authenticated raw source, license, independent gold/heldout, calibration or prereg freeze supplied; B does not invent one. |
| `c_gold_source_truth_receipt` | C | item answer and gold version | `NOT_PROVEN` | This is C/PM-owned real data, truth or rater admission. No authenticated raw source, license, independent gold/heldout, calibration or prereg freeze supplied; B does not invent one. |
| `c_scoring_mask_eval_ref` | C | selected genuine data target positions | `ADAPTER_DESIGN_REQUIRED` | B masked full-vocab CE and byte-identity toy eval support mathematical intent, but a real teacher-forced answer/data-only mask, raw UTF8 source byte spans, same population and per-token stable logits/offset custody do not exist. |
| `c_valid_data_token_count` | C/B | scored data tokens | `ADAPTER_DESIGN_REQUIRED` | B masked full-vocab CE and byte-identity toy eval support mathematical intent, but a real teacher-forced answer/data-only mask, raw UTF8 source byte spans, same population and per-token stable logits/offset custody do not exist. |
| `c_sft_stop_target_loss` | C/B | nats/stop target | `ADAPTER_DESIGN_REQUIRED` | Existing BC-v2 training supervises assistant content/EOT/EOS and ignores prompt direct CE; C future byte-bpb excludes EOT/EOS. Needs separately named stop CE and evaluation mask without altering BC v2; CCR-01 A/PM ACK pending. |
| `c_rater_delivery_bytes_sha256` | C | exact displayed task bytes | `NOT_PROVEN` | This is C/PM-owned real data, truth or rater admission. No authenticated raw source, license, independent gold/heldout, calibration or prereg freeze supplied; B does not invent one. |
| `c_rubric_calibration` | C | cases/false-correct rate | `NOT_PROVEN` | This is C/PM-owned real data, truth or rater admission. No authenticated raw source, license, independent gold/heldout, calibration or prereg freeze supplied; B does not invent one. |
| `c_prereg_freeze_receipt` | C/PM | protocol | `NOT_PROVEN` | This is C/PM-owned real data, truth or rater admission. No authenticated raw source, license, independent gold/heldout, calibration or prereg freeze supplied; B does not invent one. |
| `c_compute_contrast_definition` | C | study arms and estimand | `ADAPTER_DESIGN_REQUIRED` | C owns estimand and arms; B must measure matched actual FLOPs+source/seed/precision and differentiate unique positions from repeat exposures; no freeze or run. |
| `b_real_checkpoint_weights_sha256` | B | trained weights file bytes | `NOT_PROVEN` | Only T4/P02 architecture and schema can be pinned; actual trained T4 checkpoint bytes+raw weights SHA+optimizer/config lineage unavailable. BC/v2 checkpoint is metadata-only (NOT_CREATED). |
| `b_real_checkpoint_config_sha256` | B | model config bytes | `NOT_PROVEN` | Only T4/P02 architecture and schema can be pinned; actual trained T4 checkpoint bytes+raw weights SHA+optimizer/config lineage unavailable. BC/v2 checkpoint is metadata-only (NOT_CREATED). |
| `b_real_tokenizer_raw_sha256` | B | tokenizer bytes | `ADAPTER_DESIGN_REQUIRED` | T4 BPE 2048 uses byte IDs0..255, EOS256, merges 257..2047; BC/v2 uses PAD257 BOS258 SYS259 USER260 ASSIST261 EOT262; direct shared-ID mapping fails. Real BPE manifest+offset verification and proposed versioned adapter pending. |
| `b_token_to_utf8_byte_offsets` | B | raw UTF-8 byte coverage | `ADAPTER_DESIGN_REQUIRED` | T4 BPE 2048 uses byte IDs0..255, EOS256, merges 257..2047; BC/v2 uses PAD257 BOS258 SYS259 USER260 ASSIST261 EOT262; direct shared-ID mapping fails. Real BPE manifest+offset verification and proposed versioned adapter pending. |
| `b_full_vocab_logits_score` | B | nats/data token | `ADAPTER_DESIGN_REQUIRED` | B masked full-vocab CE and byte-identity toy eval support mathematical intent, but a real teacher-forced answer/data-only mask, raw UTF8 source byte spans, same population and per-token stable logits/offset custody do not exist. |
| `b_source_split_custody_ref` | B | raw bytes and split refs | `NOT_PROVEN` | T1/T4 manifest SHA/source contracts exist, but real private source and family/split bytes, rights and TRAIN-only corpus exclusion cannot be independently verified in this packet. |
| `b_unique_train_positions` | B | unique supervised TRAIN target positions | `NOT_PROVEN` | Historical exposures 4,194,304 and ~498,287 independent positions reported; future arm/seed real source positions/step-level repeats need immutable TRAIN pack and sampler readback. |
| `b_training_token_exposures` | B | supervised target presentations | `NOT_PROVEN` | Historical exposures 4,194,304 and ~498,287 independent positions reported; future arm/seed real source positions/step-level repeats need immutable TRAIN pack and sampler readback. |
| `b_training_compute_budget_readback` | B | compute/resource | `NOT_PROVEN` | 4,194,304 historical exposures from 1024x4096 are documented, but no matched measured FLOPs, 74-second raw timing receipt, new hard RAM/VRAM/child kill/clock evidence for 44M or new science. |
| `b_checkpoint_selection_schedule` | B | checkpoints and selections | `ADAPTER_DESIGN_REQUIRED` | Historical T4 READY-last steps 256/512/768/1024 and final step1024 primary specified; future C paired arms/VAL-only selection need prereg and weight-readback not historical TEST choice. |
| `b_release_authority_readiness` | B/A/PM | owner release | `ADAPTER_DESIGN_REQUIRED` | B can report future runner preflight, but A V4 ASCII signed policy/epoch/ledger/dual RAW-TAG and owner authority have no live proof; B cannot issue GO. |

**C-26 status count:** 9 `ADAPTER_DESIGN_REQUIRED`, 17 `NOT_PROVEN`. No real rights/gold/family sources are fabricated. Full original C field type/unit/hash-domain/negative cases and the newest exact commit mapping are available in the additive machine-readable remap record.

## B-facing — 14 additional views (SUBSET of C26)

| B-facing field | Expected type | Unit | B status | Negative falsifier |
| --- | --- | --- | --- | --- |
| `c_train_tokenizer_source_manifest_sha256` | sha256_lower_64 | TRAIN-only input bytes | `NOT_PROVEN` | fresh TEST in vocabulary training |
| `c_valid_data_token_count` | uint64 | scored data tokens | `ADAPTER_DESIGN_REQUIRED` | all-ignored or mismatch with summed NLL |
| `c_sft_stop_target_loss` | struct CE sum+count finite | nats/stop target | `ADAPTER_DESIGN_REQUIRED` | silent drop EOS/EOT from supervised SFT |
| `b_real_checkpoint_weights_sha256` | sha256_lower_64+immutable ref | trained weights file bytes | `NOT_PROVEN` | empty NOT_CREATED or fake 64-hex metadata |
| `b_real_checkpoint_config_sha256` | sha256_lower_64 | model config bytes | `NOT_PROVEN` | same file SHA but different config epoch |
| `b_real_tokenizer_raw_sha256` | sha256_lower_64+source manifest | tokenizer bytes | `ADAPTER_DESIGN_REQUIRED` | T4 BPE silently mapped to BC byte codec |
| `b_token_to_utf8_byte_offsets` | list of exact [start,end) offsets per scored token | raw UTF-8 byte coverage | `ADAPTER_DESIGN_REQUIRED` | byte range overlaps, gap or unknown alignment |
| `b_full_vocab_logits_score` | finite float64 logits + gold ids + byte-selected mask | nats/data token | `ADAPTER_DESIGN_REQUIRED` | nonfinite, target shape, wrong shift |
| `b_source_split_custody_ref` | immutable source+split+family SHA refs | raw bytes and split refs | `NOT_PROVEN` | wrong split or missing readback |
| `b_unique_train_positions` | uint64+exact method | unique supervised TRAIN target positions | `NOT_PROVEN` | repeat labels counted as independent |
| `b_training_token_exposures` | uint64 per arm/seed/step | supervised target presentations | `NOT_PROVEN` | 4,194,304 historical silently reused as new run |
| `b_training_compute_budget_readback` | structured finite (FLOPs,GPU_s,wall_s,steps,RAM,VRAM,cap) | compute/resource | `NOT_PROVEN` | GPU estimate or old M3 resource PASS substituted |
| `b_checkpoint_selection_schedule` | immutable list(step,weights_sha,eval_call_count) | checkpoints and selections | `ADAPTER_DESIGN_REQUIRED` | TEST used for choosing checkpoint |
| `b_release_authority_readiness` | enum+evidence refs | owner release | `ADAPTER_DESIGN_REQUIRED` | ASCII/UTF8 digest alias, missing trust root |

**B14 status count:** 7 `ADAPTER_DESIGN_REQUIRED`, 7 `NOT_PROVEN`. In the unique-field total, each of these is already included in C26.

## B-READBACK-03: T4 native BPE vs BC-v2 direct mapping

**Reaffirmed `INCOMPATIBLE_DIRECT_T4_BC`:** exact historical T4 `ttm_gpt2_bpe2048.py` blob `fa5bd892941ba5aa6e6b2f0b2b0ae974efe297b6`: **bytes 0–255, EOS256, merge token IDs257–2047**. BC/v2 source `bc_sft_bridge_v2.py` blob `c56d98b520fef387fab43bac87b7a9247287b17c` reserves **PAD257 BOS258 SYS259 USER260 ASSIST261 EOT262**, all collide with real T4 BPE merges. Same `vocab_size=2048` proves neither tokenizer semantics nor trained embedding equivalence. No direct BC/v2 pack, PAD, BOS, roles, or EOT token ID may be sent to the historical T4 model as if already trained for that meaning.

**C prospective design selected:** `T4_NATIVE_BPE_EXTERNAL_ROLE_BYTE_SPAN_DESIGN_ONLY`. B assesses **`ADAPTER_DESIGN_REQUIRED · NOT_IMPLEMENTED`**: keep historical T4 tokenizer/embedding IDs unchanged; preserve source/role/answer/mask provenance in externally SHA-pinned sidecar, not in-model special IDs. Prerequisites for future qualification are original real tokenizer/corpus and weights+optimizer checkpoint bytes+SHA, stable exact GPT-2 pretokenizer and merge ranks, fully auditable per-token UTF-8 raw `[start,end)` coverage, no gap/overlap or merge straddling included/excluded mask boundaries, complete full-vocab shifted CE with real logits, and separate C-approved role/stop serialization. Unknown coverage => `HOLD_BYTE_DENOM`. The external sidecar **does not make T4 chat-conditioned or create BC assistant EOT**; old EOS256 cannot alias EOT262. Real SFT stop training remains `HOLD_SFT_INCOMPATIBLE_TOKENIZER` until separately specified and proven. Future alternatives involving new tokenizer/resized embeddings are different studies, not silent B/C v2 edits.

## B-READBACK-04: CE versus bpb, ACKed by A/C/B as *design semantics*

1. **Existing BC/v2 training masked CE**: `+1` shifted assistant genuine content bytes, assistant EOT and final EOS are supervised. Prompt/system/user/headers/PAD and user EOT ignored as direct CE targets. Prompt-context gradients may be nonzero. Stop CE is separately reported.
2. **Prospective C byte-only `val_bpb`**: numerator = **sum of full-vocab gold-target NLL in nats only on exactly aligned genuine UTF-8 scored text targets**; denominator = **ln(2) × positive number of raw UTF-8 data bytes covered by the very same selected targets**. Exclude all role/protocol/stop EOT/EOS/BOS/PAD targets from *both*. No imputed 0-byte BPE partial-token scores; ambiguous byte-span alignment => HOLD.
3. **A one-target `a_gold_nll`** = stable full-vocab gold next-token NLL **nats per one gold token**, *not* pooled bits/byte, and I1 M0 v3 accepted measurement does not imply a new SFT scientific result.
4. A V4 release ASCII `payload_raw_sha256` vs `payload_tagged_sha256`, signed `policy_epoch`, immutable global `H_SLOT_V3=581fd3acf137c28300813fc48501ff8ee243984588978ae64423fffc044bbe0f`; BC v2 canonical UTF-8+LF and seven original SHA artifacts remain separate/unchanged. No wire/schema or checkpoint mutation.

C amendment acceptance `C_CCR01_SEMANTIC_CROSS_ACK_DESIGN_SCOPED`, A [`A_CCR01_MEASUREMENT_ACK_SCOPED`](https://github.com/minhtri22/TokenToModel-Lab/issues/32#issuecomment-6938396264), B old ACK and this renewed remap are **scoped design ACKs only**, not actual science QA or owner release.

## Integrated readiness R0–R8 (B's input to PM)

| Gate | Source/design disposition | Still HOLD/not proven |
|---|---|---|
| R0 | `PASS_SOURCE_REF_CORRECTED_SCOPED`, 37/26/14 remap same revision | PM independent new exact-source readback pending |
| R1 | `A_I1_PASS_SCOPED`, one-token nats vs pooled byte bpb ACK by A/C/B | C real gold, rater, new logits and source proof HOLD |
| R2 | C rights/splits/family semantics unchanged | actual signed rights, fresh heldout, family-disjoint splits HOLD |
| R3 | `DIRECT_T4_BC=INCOMPATIBLE`, prospective sidecar DESIGN_ONLY | real checkpoint weight SHA, original BPE, byte offset and stop/role proof HOLD |
| R4 | B resource feasibility documented as design | measured owner-host RAM/VRAM/FLOPs/hard cap/watchdog HOLD |
| R5 | A V4 `DESIGN_ACCEPT_SCOPED`, BC synthetic engineering PASS scoped | native NTFS/TOCTOU/ledger/owner signer HOLD |
| R6 | C evaluation/prereg design only | seeds, thresholds, rights, new TEST sealed: NOT_FROZEN |
| R7 | previous A and BC scoped reviews retained | new real/native independent QA NOT_EXECUTED; PM design remap pending |
| R8 | no I2/real SFT entitlement | `HOLD_OWNER_RELEASE` |

Preserve historical B-M3 `PASS_ENGINEERING_BASELINE_SCOPED` **and** original V3 native `HOLD_NATIVE_QA` / reviewer `HOLD_PEAK_ACCOUNTING` dissent, no V3 rerun. PM only decides joint design alignment; even a scoped alignment PASS cannot authorize science, historical TEST, T4 checkpoint load, owner signing, merge or native execution.

**B readback outcome:** `B_REMAP_READBACK_SCOPED` based on exact C `4efe93ce0a3910c449972b3f7e9911a004fe2b3c`; **do not self-award `ABC_CONTRACT_ALIGNED_DESIGN_SCOPED`**. PM final distinct adjudication remains pending under the **same integrated operation**, no micro-permits.
