# JOINT_COMPATIBILITY_MATRIX_A_C_B — exact contract, no new wire

**Operation:** `TTM_B_SHARED_EXACT_CHECKPOINT_TOKENIZER_RESOURCE_FEASIBILITY_AND_COMPATIBILITY_DESIGN_ONEPACK`  
**Mode:** `DESIGN_ONLY · SOURCE_ONLY · NO RUNNER · NO_SCIENCE` · **Date:** 2026-11-17  
**Companion full machine register:** `artifacts/ttm-abc/track-b/B_ABC_37_26_14_LOGICAL_COMPATIBILITY_20261117.json`; all type/unit/hash-domain/validation/hold/negative/proof/source pins are retained there **without dropping any fields**.

## 1. Joint source authority and audit classification

| Agent | Frozen source | Exact source identifier and scope |
|---|---|---|
| PM | `403491b698ba6586193f2ff2ae00c4441c10c595` | shared contract blob `d7fbc02a45b1d1a85cfe9b9594ae88fee495a9e1`, ACK A `6937430413`, ACK C `6937623901`, ACK B `6937885002` |
| A | `7639a53b9d76e16abfa4211cf239c5c3e9d6c940` | requirements `3de320f1e734c7610fb750477803b082fefff753`; 37/37 exact names and order |
| C | `614caff47657ccee43ad10ba06ae8ebb782b4114` | science document `a8c8f3ca898456519e82bcccb0ada73af24f6ff9`, machine crosswalk `64508ace4de057958ccbc9e3c7616a18c022250e` |
| B | `43896bcd034c82e8433bc6a2b53eefbd936616fb` | scaffold `0d76d764097cd838f3fef9cb16c9da11ff778bb9`, GPT core `9762343e06cf800b50574c2871ae1ed58537fb18` |
| B/C | `09de6a46574146d863f416e056fcf01091f3efb8` | exact tested `a83e1526bce842761f3051dad28b90a55395a6aa`, bridge blob `c56d98b520fef387fab43bac87b7a9247287b17c` |

The term `EXACT_MATCH` **only means the logical specification/source pin matches within the row's exact stated scope**. It does NOT imply actual weights, signed owner permit, model quality or new native QA. `ADAPTER_DESIGN_REQUIRED` means no implementation yet; `NOT_PROVEN` means missing bytes/measurement; `INCOMPATIBLE` is a **positive source-proven counterexample** to direct mapping. Evidence status is per-field, not one global PASS.

## 2. A 37/37 original fields — B disposition (unchanged A names)

| A field | Owner | Unit | B mapping | Evidence/limitation |
| --- |--- |--- |--- |--- |
| `a_measurement_protocol` | A | protocol id | `EXACT_MATCH` | Exact logical field meaning and frozen reference pin agree with A's accepted scoped I1/V4 source; does NOT prove a new I2 run, si… |
| `a_source_commit` | A | commit | `EXACT_MATCH` | Exact logical field meaning and frozen reference pin agree with A's accepted scoped I1/V4 source; does NOT prove a new I2 run, si… |
| `a_scorer_source_raw_sha256` | A | raw source bytes | `NOT_PROVEN` | Accepted historical SHA is carried from exact A requirements, but original raw bytes are not re-materialized/hashed by B; do not … |
| `a_fixture_records_raw_sha256` | A | raw bytes | `NOT_PROVEN` | Accepted historical SHA is carried from exact A requirements, but original raw bytes are not re-materialized/hashed by B; do not … |
| `a_fixture_manifest_raw_sha256` | A | raw bytes | `NOT_PROVEN` | Accepted historical SHA is carried from exact A requirements, but original raw bytes are not re-materialized/hashed by B; do not … |
| `a_train_bpe_raw_sha256` | A | raw bytes | `NOT_PROVEN` | Accepted historical SHA is carried from exact A requirements, but original raw bytes are not re-materialized/hashed by B; do not … |
| `a_freeze_receipt_raw_sha256` | A | raw bytes | `NOT_PROVEN` | Accepted historical SHA is carried from exact A requirements, but original raw bytes are not re-materialized/hashed by B; do not … |
| `a_case_id` | A | case identifier | `EXACT_MATCH` | Exact logical field meaning and frozen reference pin agree with A's accepted scoped I1/V4 source; does NOT prove a new I2 run, si… |
| `a_group` | A | group | `EXACT_MATCH` | Exact logical field meaning and frozen reference pin agree with A's accepted scoped I1/V4 source; does NOT prove a new I2 run, si… |
| `a_gold_nll` | A | nats/one next-token gold | `NOT_PROVEN` | A M0 v3 scoring algorithm is reviewed historically; no new real checkpoint output or I2 logits, no automatic C SFT metric equival… |
| `a_gold_rank` | A | 1-based full-vocab rank | `NOT_PROVEN` | A M0 v3 scoring algorithm is reviewed historically; no new real checkpoint output or I2 logits, no automatic C SFT metric equival… |
| `a_greedy_correct` | A | full-vocab top1 correctness | `NOT_PROVEN` | A M0 v3 scoring algorithm is reviewed historically; no new real checkpoint output or I2 logits, no automatic C SFT metric equival… |
| `a_full_vocab_tie_abstained` | A | top1 abstention | `NOT_PROVEN` | A M0 v3 scoring algorithm is reviewed historically; no new real checkpoint output or I2 logits, no automatic C SFT metric equival… |
| `a_candidate_correct_secondary` | A | secondary candidate-only correctness | `NOT_PROVEN` | A M0 v3 scoring algorithm is reviewed historically; no new real checkpoint output or I2 logits, no automatic C SFT metric equival… |
| `a_candidate_tie_abstained` | A | candidate tie abstention | `NOT_PROVEN` | A M0 v3 scoring algorithm is reviewed historically; no new real checkpoint output or I2 logits, no automatic C SFT metric equival… |
| `a_context_contrast_logit_margin` | A | logit units | `NOT_PROVEN` | A M0 v3 scoring algorithm is reviewed historically; no new real checkpoint output or I2 logits, no automatic C SFT metric equival… |
| `a_source_evidence_commit` | A | commit | `EXACT_MATCH` | Exact logical field meaning and frozen reference pin agree with A's accepted scoped I1/V4 source; does NOT prove a new I2 run, si… |
| `a_case_count` | A | cases | `EXACT_MATCH` | Exact logical field meaning and frozen reference pin agree with A's accepted scoped I1/V4 source; does NOT prove a new I2 run, si… |
| `a_group_count` | A | groups | `EXACT_MATCH` | Exact logical field meaning and frozen reference pin agree with A's accepted scoped I1/V4 source; does NOT prove a new I2 run, si… |
| `a_i1_measurement_status` | A | gate status | `EXACT_MATCH` | Exact logical field meaning and frozen reference pin agree with A's accepted scoped I1/V4 source; does NOT prove a new I2 run, si… |
| `a_release_tbs_schema` | A | wire schema identifier | `ADAPTER_DESIGN_REQUIRED` | A V4 defines trusted ASCII release/signature/raw+tag domains; B prospective runner must consume verified exact A receipt/HANDLE/l… |
| `a_policy_epoch` | A | epoch count | `ADAPTER_DESIGN_REQUIRED` | A V4 defines trusted ASCII release/signature/raw+tag domains; B prospective runner must consume verified exact A receipt/HANDLE/l… |
| `a_owner_policy_raw_sha256` | A | trusted policy raw bytes | `ADAPTER_DESIGN_REQUIRED` | A V4 defines trusted ASCII release/signature/raw+tag domains; B prospective runner must consume verified exact A receipt/HANDLE/l… |
| `a_science_slot_v3_tagged_sha256` | A | global one-shot slot digest | `EXACT_MATCH` | Exact logical field meaning and frozen reference pin agree with A's accepted scoped I1/V4 source; does NOT prove a new I2 run, si… |
| `a_payload_raw_sha256` | A | on-disk receipt file bytes | `ADAPTER_DESIGN_REQUIRED` | A V4 defines trusted ASCII release/signature/raw+tag domains; B prospective runner must consume verified exact A receipt/HANDLE/l… |
| `a_payload_tagged_sha256` | A | tagged receipt byte stream | `ADAPTER_DESIGN_REQUIRED` | A V4 defines trusted ASCII release/signature/raw+tag domains; B prospective runner must consume verified exact A receipt/HANDLE/l… |
| `a_completion_envelope_schema` | A | wire schema identifier | `ADAPTER_DESIGN_REQUIRED` | A V4 defines trusted ASCII release/signature/raw+tag domains; B prospective runner must consume verified exact A receipt/HANDLE/l… |
| `a_final_file_id_sha256` | A | opened-file identity digest | `ADAPTER_DESIGN_REQUIRED` | A V4 defines trusted ASCII release/signature/raw+tag domains; B prospective runner must consume verified exact A receipt/HANDLE/l… |
| `a_one_shot_claim_status` | A | claim state | `ADAPTER_DESIGN_REQUIRED` | A V4 defines trusted ASCII release/signature/raw+tag domains; B prospective runner must consume verified exact A receipt/HANDLE/l… |
| `a_owner_release_status` | A | release gate | `EXACT_MATCH` | Release is explicitly HOLD in A/C/PM; B does not own GO, no permit is inferred. |
| `c_valid_bytes_required` | C | UTF-8 bytes | `ADAPTER_DESIGN_REQUIRED` | B masked full-vocab CE and byte-identity toy eval support mathematical intent, but a real teacher-forced answer/data-only mask, r… |
| `c_loss_nats_required` | C | sum valid target NLL nats | `ADAPTER_DESIGN_REQUIRED` | B masked full-vocab CE and byte-identity toy eval support mathematical intent, but a real teacher-forced answer/data-only mask, r… |
| `c_val_bpb_required` | C | bits per UTF-8 byte | `ADAPTER_DESIGN_REQUIRED` | B masked full-vocab CE and byte-identity toy eval support mathematical intent, but a real teacher-forced answer/data-only mask, r… |
| `c_target_mask_semantics_required` | C | mask policy | `ADAPTER_DESIGN_REQUIRED` | Existing BC-v2 training supervises assistant content/EOT/EOS and ignores prompt direct CE; C future byte-bpb excludes EOT/EOS. Ne… |
| `b_checkpoint_weight_ref_required` | B | actual model weight bytes | `NOT_PROVEN` | Only T4/P02 architecture and schema can be pinned; actual trained T4 checkpoint bytes+raw weights SHA+optimizer/config lineage un… |
| `b_tokenizer_compatibility_required` | B/C | token IDs/UTF-8 text bytes | `INCOMPATIBLE` | T4 BPE 2048 uses byte IDs0..255, EOS256, merges 257..2047; BC/v2 uses PAD257 BOS258 SYS259 USER260 ASSIST261 EOT262; direct share… |
| `b_compute_budget_required` | B | tokens/steps/time/RAM | `NOT_PROVEN` | 4,194,304 historical exposures from 1024x4096 are documented, but no matched measured FLOPs, 74-second raw timing receipt, new ha… |

**A 37 summary:** `{"EXACT_MATCH":10,"NOT_PROVEN":14,"ADAPTER_DESIGN_REQUIRED":12,"INCOMPATIBLE":1}`. These classifications are B crosswalk judgments, not a revision to A's original `HISTORIC_SCOPED / DESIGN_ONLY / REQUIRES_B` states. A's closed I1 logical fields cannot be represented as real C SFT gold, and A V4 RAW/TAG release bytes may not be canonicalized using B/C UTF-8 rules.

## 3. C 26/26 additional logical requirements — B mapping

| C field | Owner | B mapping | Reason/negative |
| --- |--- |--- |--- |
| `c_source_rights_matrix` | C | `NOT_PROVEN` | This is C/PM-owned real data, truth or rater admission. No authenticated raw source, license, independent gold/heldout,… |
| `c_source_raw_sha256` | C | `NOT_PROVEN` | This is C/PM-owned real data, truth or rater admission. No authenticated raw source, license, independent gold/heldout,… |
| `c_source_family_manifest_sha256` | C | `NOT_PROVEN` | T1/T4 manifest SHA/source contracts exist, but real private source and family/split bytes, rights and TRAIN-only corpus… |
| `c_split_manifest_raw_sha256` | C | `NOT_PROVEN` | T1/T4 manifest SHA/source contracts exist, but real private source and family/split bytes, rights and TRAIN-only corpus… |
| `c_train_tokenizer_source_manifest_sha256` | C/B | `NOT_PROVEN` | T1/T4 manifest SHA/source contracts exist, but real private source and family/split bytes, rights and TRAIN-only corpus… |
| `c_family_duplicate_audit` | C | `NOT_PROVEN` | This is C/PM-owned real data, truth or rater admission. No authenticated raw source, license, independent gold/heldout,… |
| `c_fresh_heldout_custody` | C | `NOT_PROVEN` | This is C/PM-owned real data, truth or rater admission. No authenticated raw source, license, independent gold/heldout,… |
| `c_gold_source_truth_receipt` | C | `NOT_PROVEN` | This is C/PM-owned real data, truth or rater admission. No authenticated raw source, license, independent gold/heldout,… |
| `c_scoring_mask_eval_ref` | C | `ADAPTER_DESIGN_REQUIRED` | B masked full-vocab CE and byte-identity toy eval support mathematical intent, but a real teacher-forced answer/data-on… |
| `c_valid_data_token_count` | C/B | `ADAPTER_DESIGN_REQUIRED` | B masked full-vocab CE and byte-identity toy eval support mathematical intent, but a real teacher-forced answer/data-on… |
| `c_sft_stop_target_loss` | C/B | `ADAPTER_DESIGN_REQUIRED` | Existing BC-v2 training supervises assistant content/EOT/EOS and ignores prompt direct CE; C future byte-bpb excludes E… |
| `c_rater_delivery_bytes_sha256` | C | `NOT_PROVEN` | This is C/PM-owned real data, truth or rater admission. No authenticated raw source, license, independent gold/heldout,… |
| `c_rubric_calibration` | C | `NOT_PROVEN` | This is C/PM-owned real data, truth or rater admission. No authenticated raw source, license, independent gold/heldout,… |
| `c_prereg_freeze_receipt` | C/PM | `NOT_PROVEN` | This is C/PM-owned real data, truth or rater admission. No authenticated raw source, license, independent gold/heldout,… |
| `c_compute_contrast_definition` | C | `ADAPTER_DESIGN_REQUIRED` | C owns estimand and arms; B must measure matched actual FLOPs+source/seed/precision and differentiate unique positions … |
| `b_real_checkpoint_weights_sha256` | B | `NOT_PROVEN` | Only T4/P02 architecture and schema can be pinned; actual trained T4 checkpoint bytes+raw weights SHA+optimizer/config … |
| `b_real_checkpoint_config_sha256` | B | `NOT_PROVEN` | Only T4/P02 architecture and schema can be pinned; actual trained T4 checkpoint bytes+raw weights SHA+optimizer/config … |
| `b_real_tokenizer_raw_sha256` | B | `ADAPTER_DESIGN_REQUIRED` | T4 BPE 2048 uses byte IDs0..255, EOS256, merges 257..2047; BC/v2 uses PAD257 BOS258 SYS259 USER260 ASSIST261 EOT262; di… |
| `b_token_to_utf8_byte_offsets` | B | `ADAPTER_DESIGN_REQUIRED` | T4 BPE 2048 uses byte IDs0..255, EOS256, merges 257..2047; BC/v2 uses PAD257 BOS258 SYS259 USER260 ASSIST261 EOT262; di… |
| `b_full_vocab_logits_score` | B | `ADAPTER_DESIGN_REQUIRED` | B masked full-vocab CE and byte-identity toy eval support mathematical intent, but a real teacher-forced answer/data-on… |
| `b_source_split_custody_ref` | B | `NOT_PROVEN` | T1/T4 manifest SHA/source contracts exist, but real private source and family/split bytes, rights and TRAIN-only corpus… |
| `b_unique_train_positions` | B | `NOT_PROVEN` | Historical exposures 4,194,304 and ~498,287 independent positions reported; future arm/seed real source positions/step-… |
| `b_training_token_exposures` | B | `NOT_PROVEN` | Historical exposures 4,194,304 and ~498,287 independent positions reported; future arm/seed real source positions/step-… |
| `b_training_compute_budget_readback` | B | `NOT_PROVEN` | 4,194,304 historical exposures from 1024x4096 are documented, but no matched measured FLOPs, 74-second raw timing recei… |
| `b_checkpoint_selection_schedule` | B | `ADAPTER_DESIGN_REQUIRED` | Historical T4 READY-last steps 256/512/768/1024 and final step1024 primary specified; future C paired arms/VAL-only sel… |
| `b_release_authority_readiness` | B/A/PM | `ADAPTER_DESIGN_REQUIRED` | B can report future runner preflight, but A V4 ASCII signed policy/epoch/ledger/dual RAW-TAG and owner authority have n… |

**C 26 summary:** `{"NOT_PROVEN":17,"ADAPTER_DESIGN_REQUIRED":9}`. C-owned data rights, fresh split, gold, rater and prereg remain C-owned; `NOT_PROVEN` does not transfer or relinquish ownership to B. B source capabilities are separately qualified.

## 4. Fourteen B-facing assumptions copied from C packet

| C B-facing field | B mapping | Proof required / failure |
| --- |--- |--- |
| `c_train_tokenizer_source_manifest_sha256` | `NOT_PROVEN` | fresh TEST in vocabulary training |
| `c_valid_data_token_count` | `ADAPTER_DESIGN_REQUIRED` | all-ignored or mismatch with summed NLL |
| `c_sft_stop_target_loss` | `ADAPTER_DESIGN_REQUIRED` | silent drop EOS/EOT from supervised SFT |
| `b_real_checkpoint_weights_sha256` | `NOT_PROVEN` | empty NOT_CREATED or fake 64-hex metadata |
| `b_real_checkpoint_config_sha256` | `NOT_PROVEN` | same file SHA but different config epoch |
| `b_real_tokenizer_raw_sha256` | `ADAPTER_DESIGN_REQUIRED` | T4 BPE silently mapped to BC byte codec |
| `b_token_to_utf8_byte_offsets` | `ADAPTER_DESIGN_REQUIRED` | byte range overlaps, gap or unknown alignment |
| `b_full_vocab_logits_score` | `ADAPTER_DESIGN_REQUIRED` | nonfinite, target shape, wrong shift |
| `b_source_split_custody_ref` | `NOT_PROVEN` | wrong split or missing readback |
| `b_unique_train_positions` | `NOT_PROVEN` | repeat labels counted as independent |
| `b_training_token_exposures` | `NOT_PROVEN` | 4,194,304 historical silently reused as new run |
| `b_training_compute_budget_readback` | `NOT_PROVEN` | GPU estimate or old M3 resource PASS substituted |
| `b_checkpoint_selection_schedule` | `ADAPTER_DESIGN_REQUIRED` | TEST used for choosing checkpoint |
| `b_release_authority_readiness` | `ADAPTER_DESIGN_REQUIRED` | ASCII/UTF8 digest alias, missing trust root |

**B14 summary:** `{"NOT_PROVEN":7,"ADAPTER_DESIGN_REQUIRED":7}`; each field appears in C26 and names are byte-for-byte unchanged. The additional `c_compute_contrast_definition` belongs to C as prerequisite: it is present in C26, not falsely transferred to B14.

## 5. Proven incompatibilities, not silent aliases

**Token IDs:** T4 TRAIN-only BPE uses special EOS256 and full merge namespace **257–2047**, with exact 1791 pair merges. B/C synthetic v2 uses EOS256 **and PAD257/BOS258/SYS259/USER260/ASSIST261/EOT262**. The numeric namespace collides. Direct reuse of BC/v2 token IDs against T4 embedding rows is `INCOMPATIBLE`, not a harmless adapter of `vocab_size=2048`. Design alternatives require C/PM agreed decoding/template/span/mask semantics and B requalification. No retrospective hash change.

**Checkpoint:** B synthetic training checkpoint and B/C metadata-only SFT checkpoint are distinct from real trained T4 weights. Schema and parameter-count source readback are not a 64-byte-hex real weight proof; real raw checkpoint SHA/optimizer/source remains `NOT_PROVEN`.

**NLL and bpb:** The C primary byte score is pooled `sum(full-vocab text-target NLL nats)/(ln(2) × valid UTF-8 scored text bytes)`. It is not A's one-token I1 gold NLL nor the B synthetic training CE that includes EOT/EOS. B acknowledges C-CCR-01: assistant EOT and EOS remain SFT **training** CE targets but are excluded as structure from byte-only **evaluation**; this ACK is B source/semantic only, not A/PM final alignment.

**Data × Compute:** historical `1024×4096=4,194,304` target presentations; unique ~498,287 positions is reported, not independently reproduced with private TRAIN byte evidence. D1/D2 or a 44M target total require new admitted source families, true unique positions and matched measured FLOPs; `74 s` source timing and `13 min` extrapolation are not independently verified.

**Source custody mismatch (concrete counterexample):** in C registry `sources.a_requirements_git_blob` is `4f96452215778c3cca1af19bd6d2e3b6506d87d2`, which is actually A's `A_PM_EVIDENCE_INDEX_JOINT_COMPATIBILITY_20261117.json` blob, not requirements. The actual A requirement blob is `3de320f1e734c7610fb750477803b082fefff753`; 37 C per-row refs use the correct one. `HOLD_SOURCE_REF_CONFLICT` requires an explicit C/PM lineage correction, not a silent B alias. Original C packet remains unchanged.

## 6. R0–R8 dependency matrix (engineering design, not PM adjudication)

| Gate | B's evidenced scope | Remaining dependency | B position |
|---|---|---|---|
| R0 source/dependency | A/C exact packets and B P02/T4/BC source pinned; ACK_B posted | C machine source reference correction, PM index same-revision ACK | `PASS_SOURCE_INVENTORY_SCOPED` + `HOLD_SOURCE_REF_CONFLICT` |
| R1 measurement/gold | A I1 closed and C byte-bpb meaning specified | independent real gold, scorer/byte-mask equivalence | `HOLD_REAL_GOLD` |
| R2 rights/family split | C private rights/family manifests not accessed | human rights/PII/split/near-dup/fresh seal | `HOLD_SOURCE_RIGHTS_SPLIT` |
| R3 checkpoint/tokenizer | P02 architecture count source checked, BC metadata-only understood; direct T4/BC map incompatible | actual trained weights SHA, true TRAIN BPE bytes, C ACK prospective mapping | `HOLD_REAL_CHECKPOINT_AND_TOKENIZER` |
| R4 compute/native | historical exposures arithmetic, synthetic B-M3 scoped PM PASS | real GPU/VRAM/wall/FLOPs, owner new hard RAM/native guard | `HOLD_RESOURCE_VERIFICATION` |
| R5 A V4 release | RAW/TAG/policy_epoch/global slot source design accepted | native NTFS HANDLE/TOCTOU/atomicity, trusted signing/ledger | `HOLD_RELEASE_NATIVE` |
| R6 prereg | C proposed endpoints and falsifiers | valid rights + estimand/arms/seeds/power + CCR-01 joint ACK | `DESIGN_ONLY_NOT_FROZEN` |
| R7 independent QA | prior BC synthetic PM engineering PASS scoped; A V4 65/3 planned | new checkpoint/tokenizer/native/real-data distinct QA | `NOT_EXECUTED_REAL_CANDIDATE` |
| R8 owner GO/HOLD | explicit owner authority not present | signed trust root, global ledger and owner decision | `HOLD_OWNER_RELEASE` |

R0 candidate readiness does **not** override the C source-reference mismatch. A/PM owns R5/R8 release; B cannot alter ReleaseTBSV4 or authorize GPU.

## 7. PM 13-field logical evidence index join (not an artifact wire)

For future PM index only: `track, artifact_kind, git_url, exact_commit, git_blob_sha1, raw_sha256, domain_tag, origin_actor, review_actor, gate_status, scope, executed, limitation`. All 13 required. `domain_tag` is `A/V3`, `A/V4`, `BC/v2` or `none`, never a shared serializer. Unknown actual weight/source/hash must carry literal `UNVERIFIED`, not `0…` or a simulated 64-char SHA. Originator of B source and B author design is not authenticated independent human. Do not claim C/PM final adjudication or real execution.

**Outcome:** `B_FEASIBILITY_MAPPING_COMPLETE_SCOPED` as field mapping; `HOLD_ABC_CONTRACT_ALIGNMENT` overall, pending consolidated PM source-pin and semantics review.  
**Next single PM operation:** `TTM_PM_ABC_UNIFIED_EXACT_SOURCE_DEPENDENCY_AND_OWNER_READINESS_ADJUDICATION_SINGLE_GATE`.
