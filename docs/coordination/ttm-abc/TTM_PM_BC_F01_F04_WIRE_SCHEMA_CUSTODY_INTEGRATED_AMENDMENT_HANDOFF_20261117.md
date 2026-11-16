# PM INTEGRATED HANDOFF — B/C SFT wire/schema/custody F01–F04

**Operation:** `TTM_PM_BC_F01_F04_WIRE_SCHEMA_HASH_BRIDGE_INTEGRATED_AMENDMENT_AND_DISTINCT_QA_SINGLE_GATE`  
**Decision date:** 2026-11-17  
**Authority:** PM coordination on user-supplied review + direct GitHub source/readback; **not** authorization for science, GPU, real SFT, real data, TEST, merge or branch reset.  
**Program outcome at intake:** `B_AUTHOR_CI_PASS_29x2` + `C_PART_A_ORACLE_PASS_18` + `DISTINCT_SOURCE_REVIEW_HOLD_INTERFACE`. All source refs are pinned, findings append-only.

## Sources of truth and correct cross-track dependency

- **B baseline GPT Core:** [Draft PR #34](https://github.com/minhtri22/TokenToModel-Lab/pull/34), exact `43896bcd034c82e8433bc6a2b53eefbd936616fb`.
- **B/C integration implementation is on PR #36, *not* PR #34:** [Draft PR #36](https://github.com/minhtri22/TokenToModel-Lab/pull/36), exact candidate **`5f2b71c5f493405c180d6995a21dd7373bd2dbb2`**; CI tested implementation **`7a8e15a4451577ab727d5cada6ce15fec2c22080`**. GitHub comparison confirms only two receipt/crosscheck JSON files were added between these commits; B integration source/tests unchanged.
- **C current candidate:** [Draft PR #35](https://github.com/minhtri22/TokenToModel-Lab/pull/35), exact **`56c18e2a00714c8a1c118dabc0ede9d2a1b34b17`**. Historical M4 reviewed design source **`185d465c31f5f4bef6220be95e39dac1ae81c5b8`**, distinct 35/35 evidence @ `9fac5a675955d8b91d6855d27907f239cbfb745f`.
- **B independent source-review HOLD:** PR #36 review **5924013686** (COMMENT, not independent fresh adapter execution). It identifies BC-F01/F02/F03/F04.
- **B author CI:** GitHub Actions [#43908305162](https://github.com/minhtri22/TokenToModel-Lab/actions/runs/43908305162) Windows Python 3.12.10 and Ubuntu Python 3.12.16, 29/29 each with bounded synthetic P02 forward/backward and 0 optimizer steps. Those 29 tests target B-owned current codec, **do not contain C's newer Part A 18 tests**, and are not independent B↔C runtime interoperability QA.
- **C source oracle:** `tests/ttm_track_c/bc_sft_wire_oracle.py` at C HEAD, blob `233c678c89afc3471af4addc55f827e0c52b0383`, with `test_bc_sft_wire_oracle.py` blob `5c422bc5c4a7a5dc7c107dc1dda4718361b0851e`. C author stdlib design QA 18/18 on Python 3.13 Linux, **not a B runtime pass**.

## Findings — exact code/source facts

| Finding | B implementation @ PR36 | C current oracle @ PR35 | Current adjudication |
|---|---|---|---|
| **BC-F01:** wire type | `serialize(messages)` requires `content:list[int]` byte IDs 0–255 | `serialize(messages)` requires `content:str`, UTF-8 strict encoding | `HOLD_TYPED_BRIDGE` |
| **BC-F02:** schema | `ttm.bc.synthetic.sft.pack.v1`; metadata-only resume `ttm.bc.synthetic.sft.resume.v1` | `ttm.bc.synthetic.sft_pack.v1`; proposed `ttm.bc.synthetic.sft_checkpoint.v1` | `HOLD_SCHEMA_VERSION_CONTRACT` |
| **BC-F03:** SHA canonical bytes | compact sorted UTF-8 JSON, **no** terminal LF | same compact sorted UTF-8 JSON **plus** terminal LF | `HOLD_CANONICAL_BYTE_POLICY` |
| **BC-F04:** custody | B pack has codec/template/model/pack + per-row source digests, but lacks C's exact seven actual-file SHA readback keys | C `verify_manifest` requires 7 strings and schema, but sample oracle tests use synthetic key-name digests, **not** actual artifact byte custody | `HOLD_SEVEN_ARTIFACT_HASH_READBACK` |

**What remains valid:** byte-ID namespace agrees between B and C (content 0..255, EOS256, PAD257, BOS258, SYS259, USER260, ASSIST261, EOT262); C M4 direct prompt CE exclusion versus nonzero context gradient design is valid; B author CI 29/29 is valid for B's own adapter. Neither implies a tested native C→B entrypoint. B config uses max sequence 32 and input row length 33; a bridge must reject oversize, never silently truncate.

## One integrated implementation/amendment packet — assignments

**Agent B — implementation owner, on existing PR #36 branch or a successor scoped integration branch (do not edit PR #35 or PR #34):**

1. Define a **typed C-string→B-byte bridge** at an explicit, versioned API boundary. Strict UTF-8 encode with *identity normalization by default*; no lossy encoding, no implicit NFC/NFD, no implicit JSON/stringify of content, no silent coercion. Retain role order/provenance from structured messages; assert IDs 0..255 and special delimiter IDs 256..262 do not collide. Test literal `[ASSIST]`, U+0000, multi-byte Vietnamese characters and emoji, surrogate invalidity, roundtrip, malformed role objects, and no source authentication claim. B-native raw-byte records that are not valid UTF-8 remain a **separate** byte-only path and must not be disguised as C-string input.
2. Choose **one jointly accepted schema/version** for pack, checkpoint *metadata*, and field names, with an explicit C review signoff. Prefer additive versioned mapping/new schema instead of mutating historically frozen B schema. Do **not** claim a metadata resume manifest is an actual trained SFT checkpoint. Test old B byte pack, B-v1, C-candidate mismatch, invalid resume, wrong model/tokenizer and forged aliases fail closed.
3. Freeze **one exact canonical serialization** for new interface artifacts: UTF-8; sorted JSON keys; compact separators; specify terminal LF yes/no, Unicode normalization, line-ending handling and binary raw bytes. C currently proposes **terminal LF**; if selected, version it and record new bytes/hashes; never rewrite earlier B-v1 digests or claim equivalence. Negative: same object with/without LF must hash differently; Windows checkout CRLF mutation must be rejected or canonicalized as an explicitly versioned *new artifact*.
4. Produce **seven actual artifact-byte SHA-256 digests and independent readback**: `tokenizer_sha256`, `chat_template_sha256`, `serialized_inputs_sha256`, `target_masks_sha256`, `target_labels_sha256`, `config_sha256`, `checkpoint_schema_sha256`. These must be computed from actual *saved bytes*, not schema string names, synthetic fabricated hex, or alternate data representations. Preserve physical inputs, deterministic byte schemas, source SHA/Git blob pins, and no-overwrite outputs.
5. Joint tests: execute C's 18 current oracle cases **against the new B-facing typed bridge and versioned schema**, not only running C's oracle against itself. Include independent CE/target-mask comparison, +1 shift, fake USER supervision, every flag flip, reserved role tokens, EOT/EOS, right-pad and causal isolation, finite bounded P02 CPU forward/backward **without optimizer**, and all seven digest tampering cases. Assert exact source/CI commit under test. No science.
6. Submit a **single candidate exact HEAD** on a Draft PR with updated B/C signoff matrix and append-only evidence; no source changes after QA without rerun/sha relock.

**Agent C — contract owner, follow-up Part B on PR #36 (not PR #34):**

1. Immediately review B adapter exact `5f2b71c5...` and its subsequent candidate, C oracle exact `56c18e2...`; verify 16 A01–A16 criteria, particularly typed bridge, seven real artifact-byte hashes, schema/line endings and negative controls.
2. Define one *agreed* v2 (or formally versioned bridge) schema and canonical-byte policy jointly with B, without overwriting C's already-reviewed Part A oracle. Record C recommendation `C_CONTRACT_COMPATIBILITY_PASS_SCOPED` only after seeing B's exact candidate and independent executable evidence; otherwise `HOLD_INTERFACE`.
3. Keep C M4 `PASS_DESIGN_SCOPED` separate from C real data/measurement/science gates. No independent QA claim solely based on C-authored 18 tests.

**Distinct reviewer — new exact HEAD, not code author:** separate reviewer builds new adversarial tests for the C→B bridge, checks all seven actual artifact bytes + SHA, and independently executes synthetic-only test/negative oracle with Python3.12 (Windows and/or Linux scoped runtime). CI author success is supportive but not distinct QA.

**PM — program owner:** checks SHA/data lineage and reconciles gate decisions; accepts `BC_INTERFACE_PASS_ENGINEERING_SCOPED` only after exact candidate + C Part B acceptance + independent negative runtime QA. No micro-permit cycle.

## B-G5/B-G6 status reconciliation — mandatory nuance

An **older immutable native V3 run** `PM_B_NATIVE_QA_RECEIPT.json` SHA `063bb5770c92881ab8fd0ae485f007026594495109c0c0b0359a0ba686c22188` records `HOLD_NATIVE_QA` because an intentionally rejected 400MiB/256MiB negative returned `MemoryError` with `PeakJobMemoryUsed=429174784 > 268435456`. This execution failure is real and must not be overwritten.

A **later owner-host independent 3-probe differential** SHA `2503cc19067b1861a8495aa7cbed59e17a4f5dcbddbe54224a7c1cb1ab6a62d2` showed: 64MiB/256MiB **success**, 400MiB/256MiB **MemoryError**, same 400MiB/512MiB **success** (all same-host guarded). Prior PM formally adjudicated **`B-G5=PASS_ADJUDICATED_HARD_RESOURCE_ENGINEERING_SCOPED`** and **`B-G6=PASS_DISTINCT_AI_EXACT_HEAD_SOURCE_AND_NATIVE_EVIDENCE_SCOPED`**, documented in GitHub review HEAD `fdffbf2cc3c517d25dddae89501c091c58f2608d`: [review](https://github.com/minhtri22/TokenToModel-Lab/blob/fdffbf2cc3c517d25dddae89501c091c58f2608d/docs/research/ttm-abc/track-b/independent_review/B_G5_G6_V3_FULL_RECEIPT_INTEGRATED_PM_ADJUDICATION_20261116.md). This is a **gate-level scoped adjudication**, not a reversal of the historical V3 FAIL or scientific/resource-production approval.

The newest PR #36 distinct reviewer independently reports **`B_G5_HOLD_PEAK_ACCOUNTING`** based on the *V3 script predicate* and unresolved kernel counter. Thus **record the dissent visibly**; do not erase the earlier PM decision or claim a unanimous PASS. Separate:
- `B_G5_M3_ORIGINAL_ENGINEERING_GATE = PASS_ADJUDICATED_SCOPED (prior PM decision, extant)`.
- `B_G5_V3_NATIVE_SCRIPT = HOLD_NATIVE_QA (historical immutable)`.
- `B_G5_PEAK_COUNTER_MECHANISM = UNRESOLVED`.
- `B_G5_DISTINCT_REVIEWER_POSITION = HOLD_PEAK_ACCOUNTING`.
- `BC_5_NEW_SFT_NATIVE_AND_DISTINCT_QA = HOLD` regardless of the old B0/B1 result, until the new integration candidate has its own scoped safety/QA evidence. Do not reuse the older V3 resource permit automatically for new SFT training.

To resolve reviewer disagreement, assess **which frozen acceptance criterion** governs B-M3, not create a new memory test. The original B-G5 handoff said “one-command/one-run synthetic CPU E2E with measured resource caps”; it did not explicitly impose `PeakJobMemoryUsed<=cap` on the **intentionally rejected** negative. The V3 harness did; that extra invariant remains a historical V3 failed predicate. The PM's scoped ruling was an *interpretation of original B-M3 gate*; the reviewer should either acknowledge this scoped ruling or identify an explicit contradicting frozen criterion and leave a reasoned dissent. No retrospective broadening to production science.

## Single integrated gate and final states

| Gate | Current state | Requirement for next PASS |
|---|---|---|
| BC-0 | `PASS_SOURCE_READBACK_SCOPED` | Re-pin exact *new* candidate after amendment |
| BC-1 | `PASS_B_AUTHOR_CI_29X2_ONLY`; cross-B/C bridge HOLD | typed C→B bridge, C Part B compatibility |
| BC-2 | `PASS_B_AUTHOR_CI_ONLY` | cross-oracle role/mask/+1 shift negatives |
| BC-3 | `PASS_B_AUTHOR_CI_CPU_ONLY` | independently executed exact bridge backward/causal test |
| BC-4 | `HOLD_INTERFACE_F01_F04` | frozen shared schema/canonical bytes + seven real hashes |
| BC-5 | `HOLD_DISTINCT_NEW_INTEGRATION` | C acceptance + independent runtime evidence + resource policy for new candidate |
| C M4 | `PASS_DESIGN_SCOPED` | scientific admission separate |
| B M3 | `PASS_ENGINEERING_BASELINE_SCOPED_BY_PRIOR_PM`, reviewer peak-accounting dissent documented | do not transfer as automatic SFT science approval |
| Science / TEST / GPU / merge | `NOT_AUTHORIZED` | new owner decision after separate admission |

**One next operation:** `TTM_PM_BC_F01_F04_WIRE_SCHEMA_HASH_BRIDGE_INTEGRATED_AMENDMENT_AND_DISTINCT_QA_SINGLE_GATE`. Agent B implements, Agent C executes contract review Part B, distinct QA runs once on exact candidate, PM adjudicates. Neither rerun V3 nor spawn independent micro-permits. Keep PR #34/#35/#36 Draft and main/lineage unchanged.
