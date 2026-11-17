# Agent C — B–C Synthetic SFT Interface Contract Acceptance Matrix (Part A)

**Operation:** `TTM_C_BC_SFT_INTERFACE_CONTRACT_REVIEW_AND_INTEGRATION_ACCEPTANCE_SINGLE_GATE`  
**Date:** 2026-11-16 · **Role:** Agent C / contract owner, not B implementer.  
**Status:** `PART_A_DESIGN_ORACLE_QA_PASS_SCOPED · BC_INTEGRATION_HOLD_INTERFACE`. No model or B synthetic SFT adapter has been executed in this review.

## 0. Evidence custody and scope

| Source | Exact commit | Exact Git blob |
|---|---|---|
| Track B PR #34 GPT Core / existing byte pack | `43896bcd034c82e8433bc6a2b53eefbd936616fb` | `src/ttm_track_b/scaffold.py = 0d76d764097cd838f3fef9cb16c9da11ff778bb9` |
| Track B original P02 | same B HEAD | `src/p02/transformer_core.py = 9762343e06cf800b50574c2871ae1ed58537fb18` |
| Track B author tests | same B HEAD | `tests/test_track_b_scaffold.py = 359896b4dea646cf02509ebb2910e6a87b5c954b` |
| Track C PR #35 accepted toy contract | `185d465c31f5f4bef6220be95e39dac1ae81c5b8` | `tests/ttm_track_c/synthetic_contract.py = 83c6d5abe0948c24c9e49375ffc2a17e3143a793` |
| Track C independent design verdict | `9fac5a675955d8b91d6855d27907f239cbfb745f` | `C-G5=PASS_DESIGN_SCOPED_B_INTEGRATION_NOT_EXECUTED` |
| PM handoff | `b4cd629f624f53e24c9eb05120ffe649b664b05d` | `TTM_PM_BC_M4_SFT_INTERFACE_QUALIFICATION_HANDOFF_20261116.md = d75965a6787a1839f05bc01cf3f1071e0b8ba935` |

Sources: [PM handoff](https://github.com/minhtri22/TokenToModel-Lab/blob/b4cd629f624f53e24c9eb05120ffe649b664b05d/docs/coordination/ttm-abc/TTM_PM_BC_M4_SFT_INTERFACE_QUALIFICATION_HANDOFF_20261116.md), [B PR #34](https://github.com/minhtri22/TokenToModel-Lab/pull/34), [C PR #35](https://github.com/minhtri22/TokenToModel-Lab/pull/35), [C independent review](https://github.com/minhtri22/TokenToModel-Lab/blob/9fac5a675955d8b91d6855d27907f239cbfb745f/docs/research/ttm-abc/track-c/independent_review/C_M4_EXACT_AMENDMENT_DISTINCT_REREVIEW_20261116.md).

**B implementation discovery:** PR #34 was read back at exact baseline HEAD (unchanged); no BC SFT adapter was identified in its 11 changed files, nor in the PR metadata. The only `sft`-named branch found was `coordination/ttm-abc-bc-sft-interface-20261116` (PM coordination, not proof of B adapter). Part B cannot be marked PASS, and a new B HEAD/diff must be pinned on arrival.

## 1. Finding BC-F01 — ID map collision and required isolation

* Existing B `SYNTHETIC_BYTE_IDENTITY_V1_NOT_T4_BPE`: literal bytes **0..255**, EOS **256**, vocabulary size **2048**. B `make_windows()` rejects any ID >256 and legacy `validate_pack()` rejects any target >256; B's legacy input padding uses ID **0**, which is also a legitimate zero byte.
* C's toy reference: `PAD=0, BOS=1, SYS=2, USER=3, ASSIST=4, EOT=5, EOS=6`, content IDs >=7. Therefore the existing C toy wire is **not** B's byte wire; directly reusing either serialized ids/flags or legacy pack is unsafe.
* **Noncolliding *candidate*, not a B implementation or approved migration:** UTF-8 byte payload IDs `0..255`; `EOS=256, PAD=257, BOS=258, SYS=259, USER=260, ASSIST=261, EOT=262`. All within B vocab 2048. Other IDs 263..2047 are unassigned for this candidate. The source `tests/ttm_track_c/bc_sft_wire_oracle.py` encodes C's role semantics using this *new* allocation, not the old toy token symbols.
* Use **new** `ttm.bc.synthetic.sft_pack.v1`, **new** `ttm.bc.synthetic.chat_template.v1`, and **new** `ttm.bc.synthetic.sft_checkpoint.v1`; reject `ttm.track_b.synthetic.byte_windows.v1` for SFT and old checkpoint resume without a fully revalidated versioned migration. Do not load T4/P04 weights.
* **Role provenance limit:** reparsing ids validates declared role structure/mask, but cannot authenticate upstream roles, human authorization, source rights or corpus lineage. B needs source/batch record provenance separately.

## 2. Acceptance matrix — status by independently checkable layer

Statuses `PASS_C_ORACLE` mean only Agent-C reference Python stdlib tests passed, **not** B implementation acceptance.

| Check | Exact contract/negative QA required for B | Part A | Part B |
|---|---|---|---|
| BC-A01 · Byte-ID range | all 256 byte values roundtrip, special IDs pairwise distinct and >255, <2048, EOS still 256; NUL 0x00 is content byte, not PAD | `PASS_C_ORACLE` | `HOLD_B_ADAPTER` |
| BC-A02 · Chat template | BOS once; optional first SYS; alternating USER/ASSIST; each content nonempty; EOT every message; exactly one final EOS; no double EOS | `PASS_C_ORACLE` | `HOLD_B_ADAPTER` |
| BC-A03 · Role boundaries | literal text `[ASSIST]` remains data; special inserted as token in payload rejected; caller-forged flags rejected bit-by-bit | `PASS_C_ORACLE` | `HOLD_B_ADAPTER` |
| BC-A04 · Shift and mask | `x=ids[:-1]`; `y[j]=ids[j+1]` iff original flag at `j+1` is supervised; no header/SYS/USER/pad targets | `PASS_C_ORACLE` | `HOLD_B_ADAPTER` |
| BC-A05 · Stop | assistant answer bytes + assistant EOT + final EOS supervised; user EOT ignored; distinguish EOT turn stop versus EOS transcript end, version generation stop policy | `PASS_C_ORACLE` | `HOLD_B_ADAPTER` |
| BC-A06 · Loss semantics | `IGNORE=-100`; `sum(CE on valid targets)/N_valid`; all-ignore fails, no prompt target CE; **allow contextual prompt gradient** | `PASS_C_ORACLE` (scalar logits) | `HOLD_B_MODEL_QA` |
| BC-A07 · Loss callsite | B must call `cross_entropy_valid(logits,y)` (or vetted equivalent) on **the actual SFT y**; never pass SFT labels into P02's default `GPT.forward(..., targets)` unmasked loss | `PASS_STATIC_GAP_IDENTIFIED` | `HOLD_B_CODE` |
| BC-A08 · Padding | use PAD 257 only for right-padding; `y=-100` at padding; no valid post-pad target, no left padding, one conversation per row | `PASS_C_ORACLE` | `HOLD_B_ATTENTION` |
| BC-A09 · Causal attention | future-token perturbation leaves earlier logits invariant; right pad not visible to any earlier valid token; no cross-conversation packing | `PASS_STATIC_P02_CAUSAL_CODE_READ` | `NOT_EXECUTED_B_SFT_FORWARD` |
| BC-A10 · Backward | finite bounded CPU synthetic gradients, assistant targets counted; prompt embedding gradients **may be nonzero**; no direct prompt-label CE | `NOT_EXECUTED` | `NOT_EXECUTED_B_SFT_BACKWARD` |
| BC-A11 · Length | `max_len = B_context + 1`, so `len(x)=len(y)=B_context`; no truncation; strict oversize reject | `PASS_C_ORACLE` | `HOLD_B_ADAPTER` |
| BC-A12 · Schema/version | new pack and checkpoint IDs; reject old B byte-pack and cross-codec resume; no T4/P04 checkpoint reinterpretation | `PASS_C_ORACLE` (guard only) | `HOLD_B_CHECKPOINT` |
| BC-A13 · Byte provenance | deterministic UTF-8, explicit normalization policy (identity unless separately preregistered); source SHA, decoded roundtrip; role input authentication separate | `PASS_C_ORACLE` (synthetic) | `HOLD_B_DATA` |
| BC-A14 · SHA bundle | pin actual canonical codec, template, serialized input IDs, target labels, role masks, run config and checkpoint schema; verify fail-closed tamper | `PASS_C_ORACLE` (toy mismatch checks) | `HOLD_B_SHA` |
| BC-A15 · Exact B import | evaluate B actual adapter imported P02 with B's trained/initial weights **not** historical; verify same model forward/logits/CE path, independent logits oracle | `NOT_EXECUTED` | `NOT_EXECUTED` |
| BC-A16 · Native and independent QA | Windows Python3.12 hard-resource gate and distinct reviewer exact HEAD; no model training/science and no merge | `NOT_EXECUTED` | `WAIT_B_G5_G6` |

### Mandatory negative suite (acceptance, not optional)

`N1` use byte 0x00, bytes 1..6, multibyte UTF-8, role-delimiter-looking literal; `N2` every mask bit-flip (incl. USER, SYS, EOT, BOS, assistant suppression); `N3` inserted/duplicated or swapped reserved token; `N4` wrong target shift; `N5` all-ignore/padding unmasked/left pad; `N6` duplicate EOS, missing EOT, invalid order; `N7` old B pack/codec/checkpoint and each SHA field mismatched; `N8` finite CE and backward, no future/cross-dialogue attention; `N9` same role/mask but unauthenticated source **must not** claim full provenance. The original C-F01/C-F02 red cases are covered by A06/A03, but actual B loss callsite and model gradient remain **NOT_EXECUTED**.

## 3. Formal BC gate adjudication

| Gate | Exact current result | Reason |
|---|---|---|
| BC-0 · Source pins / specification | `PASS_B_C_BASELINE_SOURCE_PIN_SCOPED` | Exact B/C commits and blobs read; no exact new B adapter HEAD |
| BC-1 · Codec | `HOLD_B_CODEC_IMPLEMENTATION` | C candidate 18/18 reference tests, but B retains old byte-window pack |
| BC-2 · Role, shift, masked loss | `HOLD_B_MASKED_SFT_WIRING` | C oracle valid, B SFT adapter absent; B baseline CE helper exists but not SFT-wired |
| BC-3 · Causal/padding/backward | `NOT_EXECUTED` | No B SFT forward/backward, no CPU Torch evidence for the candidate |
| BC-4 · Hash/resume | `HOLD_B_NEW_SCHEMA_AND_PINS` | Reference rejects hash/schema mismatches, B has no new SFT checkpoint |
| BC-5 · Native/independent QA | `WAIT_B_G5_G6` | Windows hard-resource and independent native QA are separate HOLDs |

**Verdict:** `HOLD_INTERFACE` / `BC_INTEGRATION_NOT_EXECUTED`. No failure claim against a B SFT implementation that has not yet been submitted. The former `C_M4_PASS_DESIGN_SCOPED` remains valid and is not an engineering integration PASS.

## 4. One prospective B-submission acceptance, not a micro-permit

On B's next adapter submission, lock its **new PR/head and diff** and check each A01–A16 row against exact code and output. Fetch the real B-facing codec, chat template, P02 loss callsite, synthetic fixture, checkpoint schema, negative tests, CPU forward/backward stdout and pinned SHA receipt. Re-run C oracle tests and independently verify B outputs, especially byte 0x00, USER-mask forgery, +1 shift, end tokens, all-ignore, old pack rejection and no cross-row attention. If every BC gate satisfies the scoped policy, C may recommend `C_CONTRACT_COMPATIBILITY_PASS_SCOPED`; otherwise retain `HOLD_INTERFACE` with exact blockers. **Independent engineering adjudication and B native resource gate remain separate** even after C's own review.

### Versioned artifacts and SHA-256 contract

Use a canonical byte serialization (UTF-8, sorted-key JSON, compact separators, terminal newline) and record **actual computed** SHA-256 for each: (1) tokenizer byte/ID mapping + assigned vocab, (2) chat template/stop policy, (3) source conversation IDs/role provenance and serialized input IDs, (4) unshifted assistant flags and post-shift target masks, (5) post-shift labels `y`, (6) run/model/trainer config and checkpoint schema, (7) predeclared resource limits, software/torch version and exact B/C source blobs. Field names in proposed oracle: `tokenizer_sha256`, `chat_template_sha256`, `serialized_inputs_sha256`, `target_masks_sha256`, `target_labels_sha256`, `config_sha256`, `checkpoint_schema_sha256`. A hash of a *label string* is **not** a custody hash for actual bytes; B must compute hashes of actual saved artifact bytes and prove readback consistency before engineering acceptance.

## 5. QA and limitations

**New C candidate oracle:** `tests/ttm_track_c/bc_sft_wire_oracle.py` Git blob `233c678c89afc3471af4addc55f827e0c52b0383`, SHA-256 `bbd72ecb890d74188b20ae808dd518dbbc70c3ae945b03a710b9a7bc3ba603b0`. **Tests:** `tests/ttm_track_c/test_bc_sft_wire_oracle.py` blob `5c422bc5c4a7a5dc7c107dc1dda4718361b0851e`, SHA-256 `1237f530b0d97288d8cad003813eec400e6e9178f766fd3c3a67748ca434bcf7`. Exact hashes correspond to locally executed bytes. `PYTHONPATH=tests/ttm_track_c python -S -B -m unittest discover -s tests/ttm_track_c -p test_bc_sft_wire_oracle.py -v`: **18/18 PASS**, CPython 3.13.5 Linux stdlib-only, seeded dialogues 1,000, no Torch. Initial local test drafts contained a Python role-key mapping error and an invalid test assertion on a byte outside 0..255; corrected **only C candidate/test source**, then reran 18/18. No model, real data, TEST historical, GPU, B branch edits, SFT training, main merge or lineage changes.

**Important limitation:** The C design oracle and unit test are not evidence that the B-side codec, training adapter, checkpoint, SHA bundle or native Windows run exists or was evaluated.

**Bước thực hiện tiếp theo — duy nhất:** `TTM_C_BC_EXACT_B_ADAPTER_HEAD_INTEGRATION_REVIEW_SINGLE_GATE` after B publishes its actual adapter with exact HEAD and evidence; apply this frozen matrix and return `C_CONTRACT_COMPATIBILITY_PASS_SCOPED` or `HOLD_INTERFACE`, not a science or merge decision.
