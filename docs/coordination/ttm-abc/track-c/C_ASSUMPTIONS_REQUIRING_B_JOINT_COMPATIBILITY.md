# Agent C — ASSUMPTIONS_REQUIRING_B + A–C joint compatibility (DESIGN_ONLY)

**Input pins:** PM charter `403491b698ba6586193f2ff2ae00c4441c10c595` / blob `d7fbc02a45b1d1a85cfe9b9594ae88fee495a9e1`; A exact packet `7639a53b9d76e16abfa4211cf239c5c3e9d6c940` / requirements blob `3de320f1e734c7610fb750477803b082fefff753`; C source `00afd25aa2234e30f7602592d49d5d9f2947965b`; B/C v2 `09de6a46574146d863f416e056fcf01091f3efb8`.  
**ACK_C:** [Issue #32 #6937623901](https://github.com/minhtri22/TokenToModel-Lab/issues/32#issuecomment-6937623901). C does not claim B answers exist. This table is a logical mapping for B, not a new B runtime receipt schema.

## A. ASSUMPTIONS_REQUIRING_B (all real evidence = HOLD_B_VERIFICATION)

| Requested B/BC field | Type and units; canonical-byte domain | Exact acceptance / negative case |
|---|---|---|
| `c_train_tokenizer_source_manifest_sha256` | sha256_lower_64, original raw TRAIN tokenizer-learning input bytes | TRAIN family manifest and absence of VAL/TEST/probe; reject tokenizer leakage |
| `c_valid_data_token_count` | uint64, scored non-special data tokens under C eval mask | N>0, matches B logits/byte offsets; reject all-IGNORE |
| `c_sft_stop_target_loss` | finite CE sum/count nats and stop target count | SFT assistant EOT and final EOS CE preserved, **not** in byte-only bpb; reject silent stop loss removal |
| `c_compute_contrast_definition` | structured arms + estimand / measured FLOPs | B confirms matched source/checkpoint/compute/information; reject exposure-only equality |
| `b_real_checkpoint_weights_sha256` | immutable file-ref + raw weights SHA-256 / bytes | actual trained weights/config/optimizer lineage; reject metadata-only BC/v2 fake checkpoint |
| `b_real_checkpoint_config_sha256` | sha256_lower_64 / real architecture config bytes | vocab/context/parameter count and exact checkpoint source; reject unequal configs |
| `b_real_tokenizer_raw_sha256` | sha256_lower_64 plus TRAIN source manifest / tokenizer raw bytes | prove real original T4 BPE training source, stable encoder/special mapping; do not assume BC/v2 codec equivalence |
| `b_token_to_utf8_byte_offsets` | offsets [start,end) for each scored target token / original UTF-8 source | exact token coverage without overlap/gap; BPE token straddling masked boundary ⇒ HOLD_BYTE_DENOM |
| `b_full_vocab_logits_score` | finite float64 full-vocab logits, gold token ID, shifted mask / nats | independent stable logsumexp CE; no candidate-only reduction, no target shift drift |
| `b_source_split_custody_ref` | immutable SHA refs / raw family and split manifests | all consumed data C admitted; reject wrong family/split or private data disclosure |
| `b_unique_train_positions` | uint64 distinct supervised target positions / tokenizer+source SHA | count by immutable source position, not number of sampled repeats |
| `b_training_token_exposures` | uint64 supervised label presentations per arm/seed/step | include repeated presentations, ignore -100; reject historical 4,194,304 silently reused as new run |
| `b_training_compute_budget_readback` | structured finite FLOPs/GPU seconds/wall seconds/steps/CPU RAM/VRAM/hard cap | owner-host measured resource, exact software/device and stop guard; reject 44M/13min estimate as proof |
| `b_checkpoint_selection_schedule` | immutable ordered checkpoint step+weights SHA+selection rule | prereg fixed or VAL-only selection, never TEST selection |
| `b_release_authority_readiness` | enum/status+exact A RAW/TAG/signed policy/ledger evidence | B assesses architecture/runner feasibility but cannot issue A release or owner GO |

The accompanying machine JSON marks **14 B-facing requirements** because `c_compute_contrast_definition` is C-owned and is a C prerequisite, while the other 14 entries contain B or B/C ownership. The table keeps this extra prospective C prerequisite visible for B to map without transferring ownership. None are validated real capability.

## B. Same-revision JOINT_COMPATIBILITY_MATRIX (design input)

| Producer → consumer | Source exact SHA | Status and one-owner field boundary |
|---|---|---|
| PM → A/C/B | `403491b698ba6586193f2ff2ae00c4441c10c595`; blob `d7fbc02a45b1d1a85cfe9b9594ae88fee495a9e1` | ACK_A and ACK_C posted; ACK_B pending. PM owns 13-field logical evidence row |
| A measurement/release → C | A packet `7639a53b9d76e16abfa4211cf239c5c3e9d6c940` | **37/37 names preserved** and typed. A owns original I1 scorer & A V4 release byte domain; no fresh I2 proof |
| C science/data → B | C input `00afd25aa2234e30f7602592d49d5d9f2947965b`; this packet to be pinned by subsequent commit | C owns right source/gold/rater/byte-bpb/eval question. B must map feasible actual checkpoint/tokenizer/resource, not redesign endpoint |
| B/C synthetic → C | PR #36 `09de6a46574146d863f416e056fcf01091f3efb8`, corrected B source `a83e1526bce842761f3051dad28b90a55395a6aa` | BC F01–F06 and engineering synthetic scope PASS; no real SFT weights, TEST or hard native resource attestation |
| B actual model → C/A/PM | prior Track B PR #34 `43896bcd034c82e8433bc6a2b53eefbd936616fb` | HOLD_B_VERIFICATION; actual real weight/checkpoint, token-to-byte mapping, measured FLOPs and resource cap absent |
| C-CCR-01 → A/B/PM | [Issue #32 #6937644143](https://github.com/minhtri22/TokenToModel-Lab/issues/32#issuecomment-6937644143) | HOLD_CCR_01_ACK_PENDING, only logical interpretation request, not schema rewrite |
| PM integration → owner | PM shared charter above | eventual single PASS_TO_PROSPECTIVE_DESIGN_ONLY or HOLD_CONTRACT_ALIGNMENT; **R8 release HOLD** regardless |

**Source-domain veto:** A ASCII raw/tagged release policy does not adopt BC UTF-8 JSON serializer; BC/v2 ID 0..255 byte tokens + 256..262 specials do not substitute original TRAIN-only T4 BPE; BC metadata checkpoint does not prove real weight bytes. Equality of field names is not equality of source bytes.

## C. Change-control record (not an implementation request)

C-CCR-01 objects to **ambiguous A wording**, not to the accepted engineering BC/v2 stop supervision. Existing B/C v2 assistant EOT + final EOS remain train CE targets; C **byte-only evaluation** excludes EOT/EOS from both raw-byte denominator and NLL numerator. It is invalid to count extra structure tokens as genuine UTF-8 data bytes, equally invalid to silently drop stop-target training CE. A/PM must acknowledge this distinction before joint alignment can be asserted. No old A or BC file, schema, checkpoint, frozen threshold or checksum changes in this operation.

Negative examples:
- `HOLD_MASK_CONTRACT` if trainer no longer supervises stop labels or prompt labels leak into CE;
- `HOLD_BYTE_DENOM` if evaluation counts structural tokens as text bytes or BPE offsets unverified;
- `HOLD_SOURCE_RIGHTS_SPLIT` if same story family spans TRAIN and heldout;
- `HOLD_RESOURCE` if equal token exposures are substituted for measured FLOPs/hard memory;
- `HOLD_OWNER_RELEASE` if A policy epoch/signer/one-shot claim is represented by unsigned issue comment.

## D. Required B response (single design onepack)

For **each** row above, B must return: exact source commit and file Git blob + raw SHA if available; evidence path/status; type/units and raw-byte hash domain; validation or negative test available; whether it is *actual measured* or planned; blockers and alternative feasible mapping if none; no fake 64-hex values. B may legitimately return `UNVERIFIED` or `HOLD_B_VERIFICATION` for unavailable real checkpoint/rights; this is not a reason for C to fabricate them.

B is not allowed to change C gold, source family split, valid byte definition, A V4 policy/signer or BC/v2 canonical policy silently; genuine conflict is one consolidated CONTRACT_CHANGE_REQUEST to PM Issue #32. No new science or model execution. PM then adjudicates R0–R8 in a **single** packet.

**Only next operation:** `TTM_B_SHARED_EXACT_CHECKPOINT_TOKENIZER_RESOURCE_FEASIBILITY_AND_COMPATIBILITY_DESIGN_ONEPACK`.
