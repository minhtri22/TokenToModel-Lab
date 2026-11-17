# Agent A → B/C · Measurement, release and custody requirements (ABC V4)

**Operation:** `TTM_A_V4_MEASUREMENT_RELEASE_BARRIER_AND_CROSS_TRACK_INTERFACE_DESIGN_ONEPACK` · `DESIGN_ONLY · SOURCE_ONLY · NO SCIENCE`  
**PM shared contract:** [immutable source](https://github.com/minhtri22/TokenToModel-Lab/blob/403491b698ba6586193f2ff2ae00c4441c10c595/docs/coordination/ttm-abc/TTM_PM_ABC_V4_SHARED_COORDINATION_CONTRACT_20261117.md), Git blob `d7fbc02a45b1d1a85cfe9b9594ae88fee495a9e1`; [ACK_A](https://github.com/minhtri22/TokenToModel-Lab/issues/32#issuecomment-6937430413).  
**Track A accepted design:** `e6746184603f038b49d1e7d472367b6354474ba2`, [V4 distinct `DESIGN_ACCEPT_SCOPED`](https://github.com/minhtri22/TokenToModel-Lab/issues/32#issuecomment-6937099406). **Actual I1 only:** `ec197b5f00d3a037420390edd11ee55047e1d37f`, [measurement evidence](https://github.com/minhtri22/TokenToModel-Lab/blob/e3e1c802815f4db1534e92d9848d6015eb9203cc/artifacts/ttm-abc/track-a/M0_V3_POST_HOLD_DISTINCT_I1_20261117/REVIEW.md).  
**Authority:** This is **Agent A's requirements namespace**. C owns scientific question, gold/rater, data rights/splits, byte-denominator and primary C endpoints; B owns real checkpoint/tokenizer compatibility, resource feasibility/runner. DO NOT change C/B frozen schemas, BC v2 7-SHA manifest, or test fixtures. Any substantive conflict → ONE `CONTRACT_CHANGE_REQUEST` to PM Issue #32 with exact byte impact and dependent ACKs.

## A. Measurement/evidence interface — names, types, units, bytes, validation and HOLD

**Scope of each row:** `HISTORIC_SCOPED` means pinned source/evidence exists, not new value measured here; `PROSPECTIVE_OUTPUT_NOT_EXECUTED` means source defines a future potential field but no I2 run; `DESIGN_ONLY` means V4 protocol accepted *as design*, not real proof; `REQUIRES_C/B` means upstream owner must supply verified data. The field names below are **logical requirements**, not a new on-disk C/B format.

| Logical field | Owner | Type | Unit | Byte/hash domain | Validation / meaning | On failure | Evidence state |
|---|---|---|---|---|---|---|---|
| `a_measurement_protocol` | A | `string enum` | protocol id | ASCII literal | exact frozen M0 v3 schema; never relabel C SFT | `HOLD_PROTOCOL_MISMATCH` | `HISTORIC_SCOPED` |
| `a_source_commit` | A | `git_sha1_40` | commit | lowercase Git SHA1 | must equal accepted ec197b5f00d3a037420390edd11ee55047e1d37f | `HOLD_SOURCE_SHA` | `HISTORIC_SCOPED` |
| `a_scorer_source_raw_sha256` | A | `sha256_lower_64` | raw source bytes | exact LF Git checkout or explicitly pinned CRLF hash, never silent EOL normalization | verify original q001_m0_goldblind.py 2d0b980768a0ac3079f361d94244cd694c97ed90e978fc83fb7991dc82b5c2ac LF SHA | `HOLD_SCORER_SHA` | `HISTORIC_SCOPED` |
| `a_fixture_records_raw_sha256` | A | `sha256_lower_64` | raw bytes | SHA256 of frozen FIXTURE_RECORDS.json bytes | 823a08dd4be0da7748cb258b9bf5b2841dd1fdbac84956eb204be7ba57f8c55d | `HOLD_FIXTURE_BYTES` | `HISTORIC_SCOPED` |
| `a_fixture_manifest_raw_sha256` | A | `sha256_lower_64` | raw bytes | SHA256 frozen FIXTURE_MANIFEST.json bytes; do not reserialize | 0b80368a6747994df5f5b8d0e7b35137266ac82f6c9b83d26af5b61f79b3cb04 | `HOLD_MANIFEST` | `HISTORIC_SCOPED` |
| `a_train_bpe_raw_sha256` | A | `sha256_lower_64` | raw bytes | SHA256 original TRAIN-only BPE input bytes, not BC v2 synthetic codec | cba18e60cee3d08a353ee6d4a451017289e45af7b4b1179c87171b9b78d7dfdc | `HOLD_TOKENIZER_ALIAS` | `HISTORIC_SCOPED` |
| `a_freeze_receipt_raw_sha256` | A | `sha256_lower_64` | raw bytes | SHA256 original frozen receipt bytes | b82a7ebc29930563db581f7724d0847a725d893860b776b7cc682ec875af4c3a | `HOLD_FREEZE_RECEIPT` | `HISTORIC_SCOPED` |
| `a_case_id` | A | `string` | case identifier | fixture JSON UTF-8 source anchored, not BC codec | match one of 80 pinned case hashes; no new fixture regeneration | `HOLD_CASE_ID` | `HISTORIC_SCOPED` |
| `a_group` | A | `enum` | group | fixture source string (TRAIN, HELDOUT_ABSENT, HELDOUT_NOVEL_IDS, HELDOUT_RECOMBINED, PAIRED_COUNTERFACTUAL) | must be one of 5 groups, count 80 total | `HOLD_GROUP` | `HISTORIC_SCOPED` |
| `a_gold_nll` | A | `finite float64 semantic` | nats/one next-token gold | full-vocab stable logsumexp of logits, not reduced choices | M0 v3 exact scorer + nonfinite/shape/tie negatives; no post-hoc endpoint alias | `HOLD_NLL_ORACLE` | `PROSPECTIVE_OUTPUT_NOT_EXECUTED` |
| `a_gold_rank` | A | `int >=1` | 1-based full-vocab rank | 1 + number of logits strictly above gold logit | match scorer full vocab, no candidate-only swap | `HOLD_RANK` | `PROSPECTIVE_OUTPUT_NOT_EXECUTED` |
| `a_greedy_correct` | A | `bool` | full-vocab top1 correctness | full vocabulary; ties abstain | unique argmax; tie != first choice | `HOLD_GREEDY` | `PROSPECTIVE_OUTPUT_NOT_EXECUTED` |
| `a_full_vocab_tie_abstained` | A | `bool` | top1 abstention | whole-vocab ties | tie gives abstention | `HOLD_TOP1_TIE` | `PROSPECTIVE_OUTPUT_NOT_EXECUTED` |
| `a_candidate_correct_secondary` | A | `bool` | secondary candidate-only correctness | gold-free candidate set determined from context before scoring | must be labeled secondary/non-independent of restricted choice inventory | `HOLD_LABEL_LEAK` | `PROSPECTIVE_OUTPUT_NOT_EXECUTED` |
| `a_candidate_tie_abstained` | A | `bool` | candidate tie abstention | candidate-only logits subset | tie should abstain | `HOLD_CANDIDATE_TIE` | `PROSPECTIVE_OUTPUT_NOT_EXECUTED` |
| `a_context_contrast_logit_margin` | A | `finite float64 semantic` | logit units | logit[gold] - max(non-gold candidate logits) | not a probability, not equivalent to NLL/accuracy | `HOLD_MARGIN` | `PROSPECTIVE_OUTPUT_NOT_EXECUTED` |
| `a_source_evidence_commit` | A | `git_sha1_40` | commit | fixed evidence Git commit | exact e3e1c802815f4db1534e92d9848d6015eb9203cc links independent checker; no self-certification | `HOLD_EVIDENCE_PIN` | `HISTORIC_SCOPED` |
| `a_case_count` | A | `uint` | cases | decimal integer | frozen 80, all case hashes | `HOLD_CASE_COUNT` | `HISTORIC_SCOPED` |
| `a_group_count` | A | `uint` | groups | decimal integer | frozen 5 | `HOLD_GROUP_COUNT` | `HISTORIC_SCOPED` |
| `a_i1_measurement_status` | A | `enum` | gate status | I1_PASS_SCOPED_MEASUREMENT only for M0 v3 | must not imply release | `HOLD_SCOPE_PROMOTION` | `HISTORIC_SCOPED` |
| `a_release_tbs_schema` | A | `ASCII literal` | wire schema identifier | ttm.track_a.release_tbs.v4 sorted compact JSON one LF | reject old V3 or unknown fields | `HOLD_TBS_SCHEMA` | `DESIGN_ONLY` |
| `a_policy_epoch` | A | `uint53_positive` | epoch count | signed ReleaseTBSV4 canonical ASCII bytes | TBS=detached=trusted policy >= antirollback floor | `HOLD_EPOCH` | `DESIGN_ONLY` |
| `a_owner_policy_raw_sha256` | A | `sha256_lower_64` | trusted policy raw bytes | SHA256(exact policy file), not signer-provided digest | trust anchor/revocation/principal proof required | `HOLD_UNTRUSTED_POLICY` | `DESIGN_ONLY` |
| `a_science_slot_v3_tagged_sha256` | A | `sha256_lower_64` | global one-shot slot digest | V3/SLOT prefix NUL + canonical ASCII payload; never V4 retag | must equal 581fd3acf137c28300813fc48501ff8ee243984588978ae64423fffc044bbe0f | `HOLD_SCOPE_ALIAS` | `DESIGN_ONLY` |
| `a_payload_raw_sha256` | A | `sha256_lower_64` | on-disk receipt file bytes | SHA256(C(ReceiptPayloadV3)), no prefix | stage vs final vs envelope raw must agree | `HOLD_RAW_DIGEST` | `DESIGN_ONLY` |
| `a_payload_tagged_sha256` | A | `sha256_lower_64` | tagged receipt byte stream | SHA256(ASCII(TTM-A-BR-I2/V3/PAYLOAD)||00||C(payload)) | strict domain and separate from raw | `HOLD_TAG_DIGEST` | `DESIGN_ONLY` |
| `a_completion_envelope_schema` | A | `ASCII literal` | wire schema identifier | ttm.track_a.completion_envelope.v4 | both raw/tag fields required, no lone payload_sha256 | `HOLD_COMPLETION_SCHEMA` | `DESIGN_ONLY` |
| `a_final_file_id_sha256` | A | `sha256_lower_64` | opened-file identity digest | hash evidence derived from native handle, not payload checksum | must pin same verified trusted parent identity and postpublish readback | `HOLD_NATIVE_CUSTODY` | `NATIVE_NOT_EXECUTED` |
| `a_one_shot_claim_status` | A | `enum` | claim state | NO_AUTHORITY|AUTHORIZED|CLAIMED_CONSUMED|DISPATCH_ATTEMPTED|TERMINAL|HOLD_UNCERTAIN | program-owned global ledger; no nonce claim in design | `HOLD_LEDGER_UNKNOWN` | `NATIVE_NOT_EXECUTED` |
| `a_owner_release_status` | A | `enum` | release gate | HOLD|AUTHORIZED only after verified distinct signatures and PM scope | currently HOLD | `HOLD_OWNER_RELEASE` | `HOLD` |
| `c_valid_bytes_required` | C | `uint64` | UTF-8 bytes | count raw valid target bytes; define denominator independent of special token bytes | C to define and freeze; never derive from A 80-case count | `HOLD_BYTE_DENOM` | `REQUIRES_C` |
| `c_loss_nats_required` | C | `finite float64 semantic` | sum valid target NLL nats | sum over C valid target mask; excludes ignored tokens | C's future evaluated byte-defined NLL; no transfer from A I1 aggregate | `HOLD_LOSS` | `REQUIRES_C` |
| `c_val_bpb_required` | C | `finite float64 semantic` | bits per UTF-8 byte | loss_nats/(ln(2)*valid_bytes) for valid_bytes>0 | preregister denominator/masks/gold; A does not claim value | `HOLD_VAL_BPB` | `REQUIRES_C` |
| `c_target_mask_semantics_required` | C | `versioned schema/ref` | mask policy | UTF-8 source and BC v2 token IDs separately | C freezes BOS/EOT/EOS/PAD ignored roles and shift offsets | `HOLD_MASK` | `REQUIRES_C` |
| `b_checkpoint_weight_ref_required` | B | `immutable ref + sha256` | actual model weight bytes | checkpoint file bytes, not metadata-only BC checkpoint | B pin true trained weights and model config/params | `HOLD_WEIGHTS` | `REQUIRES_B` |
| `b_tokenizer_compatibility_required` | B/C | `versioned test evidence` | token IDs/UTF-8 text bytes | BC v2 reserved 256..262 and original T4 BPE are not assumed interchangeable | source-anchored mapping and explicit incompatibility verdict | `HOLD_CODEC_MISMATCH` | `REQUIRES_B_C` |
| `b_compute_budget_required` | B | `structured finite budget` | tokens/steps/time/RAM | from actual runner on host; no invented rates | B provide observed native feasibility, stop guard, resource hard memory | `HOLD_RESOURCE` | `REQUIRES_B` |

## B. Quantitative contract — what is and is not transferable

**Actual M0 v3 function:** `evaluate_goldblind_logits(logits, item)` delegates to `q001_m0_goldblind.score_logits`, where
```
m = max(logits)
gold_nll = (m - logits[gold]) + log(fsum(exp(logit - m) for logit in logits))
gold_rank = 1 + count(logit > logit_gold for all full-vocab logits)
greedy_correct = (unique full-vocab top1 index == gold)  # tied argmax abstains
candidate_correct_secondary = (unique top1 among context-derived choices == gold)
context_contrast_logit_margin = logit_gold - max(non-gold candidate logit)
```
The model scorer validates vocabulary size and finite logits, and derives candidate choices from context before gold comparison. `gold_nll` is **nats per one gold next-token** and **not** the C-owned `val_bpb` or an existing real I2 metric result. Candidate-only score is *secondary*, never an unconditional capability claim or a valid substitute for full-vocab NLL. Historical QA tests demonstrate scorer correctness on pinned mock and private fixture custody, not new model generalization.

**Prospective C endpoint (requires C's independent scientific contract and B tokenizer binding):**
```
C.val_bpb = C.loss_nats / (ln(2) * C.valid_bytes)
valid_bytes = number of raw valid UTF-8 target bytes under C's frozen mask
```
A does not choose C's gold, thresholds, heldout split or treatment of BOS/EOT/EOS/PAD; it merely requires denominator, target-mask/exposure provenance and explicit reject-on-zero/unknown. Some tokenizer token boundaries straddle bytes and special tokens carry no raw target bytes; no naive `token_count == valid_bytes` assumption. Pair `loss_nats` with the corresponding mask/bytes/chunk/tokenizer source hash, report `NLL/token` separately, and reject if alignment is unproven. This equation is a **design requirement**, not measured science.

## C. Custody and negative requirements each recipient must honor

**Agent C (source/gold/rater):** receive exact accepted M0 protocol and IDs but must not reuse TRAIN/HELDOUT_ABSENT/NOVEL_IDS/RECOMBINED/COUNTERFACTUAL data as fresh confirmatory TEST; explicitly distinguish M0 80-case toy oracle from TinyStories or SFT evaluation. Require rights, independent gold, case family split, duplicate and future heldout controls, prereg of val_bpb and primary likelihood endpoint. Existing FRESH16/FINAL24 and previously inspected TEST cannot become unexposed confirmatory. If no authentic gold/rights/source bytes or incomplete mask: `HOLD_REAL_SOURCE_CUSTODY` / `HOLD_GOLD_UNPROVEN` / `HOLD_EVAL_SEMANTICS`.

**Agent B (runner/interface/resource):** consume A requirements by exact SHA, do not edit original I1 scorer, historical release guard or V4 wire bytes. Future real runner must emit stage/final RAW/TAG with independent SHA recomputation and file-ID/parent-handle identity, canonical schema ID, trusted signer/epoch status, one-shot ledger state, pinned model config/weight SHA, target mask/protocol ref, valid byte counts, exact checkpoint and tokenizer source. Fail closed before touching checkpoint/claim when authority not proven; after an ambiguous **claimed** state do not auto-retry. Require native Windows readback for hard memory/NTFS/junction, crash/power-loss and concurrent W1/W2; source-only synthetic CI is **not** native proof. If absent: `HOLD_B_VERIFICATION`.

**Boundary between A and BC bytes:** B/C v2 strict UTF-8 → byte token IDs 0..255 with 256 EOS, 257 PAD, 258 BOS, 259 SYS, 260 USER, 261 ASSIST, 262 EOT, canonical UTF-8 sorted JSON + LF (7 artifact SHA). A release wire is ASCII closed typed domain-separated TBS/receipt. A does not create a new serialization codec for C, nor does B automatically map T4 BPE to BC byte IDs. Include a `codec_compatibility=UNVERIFIED` marker until tested.

## D. JOINT_COMPATIBILITY_MATRIX — this A revision only

| Producer | Consumed exact source | Consumer | Status / ownership boundary |
|---|---|---|---|
| PM shared | `403491b698ba6586193f2ff2ae00c4441c10c595`, Git blob `d7fbc02a45b1d1a85cfe9b9594ae88fee495a9e1` | A/C/B | `ACK_A_POSTED`; C and B must ACK later |
| A measurement | `ec197b5f00d3a037420390edd11ee55047e1d37f`, evidence `e3e1c802815f4db1534e92d9848d6015eb9203cc` | C, B | `PASS_SCOPED_MEASUREMENT` only; prospective I2 metrics `NOT_EXECUTED` |
| A release V4 | `e6746184603f038b49d1e7d472367b6354474ba2`, independent V4 review #6937099406 | B, C | `PASS_SCOPED_DESIGN` only; owner release `HOLD` |
| C science/data | PR35 `00afd25aa2234e30f7602592d49d5d9f2947965b` | B, PM | `HOLD_C_SCIENCE_CONTRACT_REQUIRED` (no A rewrite of C gold/endpoint) |
| B core | PR34 `43896bcd034c82e8433bc6a2b53eefbd936616fb` | C, A, PM | `HOLD_B_REAL_RESOURCE_AND_WEIGHT_VERIFICATION`; synthetic prior scoped only |
| B/C v2 | PR36 `09de6a46574146d863f416e056fcf01091f3efb8`, tested B `a83e1526bce842761f3051dad28b90a55395a6aa` | C, B, PM | `PASS_ENGINEERING_SCOPED`, **not** real science |

**PM evidence index row requirements:** `track,artifact_kind,git_url,exact_commit,git_blob_sha1,raw_sha256,domain_tag,origin_actor,review_actor,gate_status,scope,executed,limitation` are logical **index** columns only. Unknown raw bytes → `UNVERIFIED` (not guessed). Namespaced `A/V3`, `A/V4`, `BC/v2`, `none`; no cross-domain implicit hash equality. [Index and matrix](../../../../artifacts/ttm-abc/track-a/A_PM_EVIDENCE_INDEX_JOINT_COMPATIBILITY_20261117.json) list source commits and ownership.

**Outcome requested from C:** acknowledge frozen A field signatures unchanged, define C gold/rater/data and byte-level endpoint/denominator under its own authority; leave B's resource and real model capability `HOLD_B_VERIFICATION` until exact readback. Next operation only `TTM_C_SHARED_SCIENCE_DATA_EVAL_CONTRACT_DESIGN_ONEPACK`, followed by B and single PM owner packet. No agent may self issue I2 GO.
