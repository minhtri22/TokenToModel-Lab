# Track B — B/C SFT F01–F04 v2 integrated amendment

**Operation:** TTM_PM_BC_F01_F04_WIRE_SCHEMA_HASH_BRIDGE_INTEGRATED_AMENDMENT_AND_DISTINCT_QA_SINGLE_GATE  
**Ngày:** 2026-11-17 · **Owner:** Agent B · **Current outcome:** PASS_AUTHOR_CI_SCOPED / HOLD_BC_INTERFACE_PENDING_C_PART_B_AND_DISTINCT.  
**CI-tested implementation commit:** 724f62a025b8ecc7c452b9ee16c926adfd2b8c7e. All later commits are evidence/doc-only.  
**Branch/PR:** integration/ttm-bc-synthetic-sft-interface-20261116, Draft PR #36 stacked onto Track B. No edits to PR #34/35 branches, main or lineage.  
**Pins:** B 43896bcd034c82e8433bc6a2b53eefbd936616fb; C Part A 56c18e2a00714c8a1c118dabc0ede9d2a1b34b17; PM handoff 40788f557799c7c8a688df32271510aab73a9180.

## 1. Four fixes — additive v2, preserve every old checksum

**BC-F01 — typed C-str to B-byte interface.** src/ttm_track_b/bc_sft_bridge_v2.py accepts only role-bearing content:str through to_byte_messages, strict UTF-8 identity without implicit NFC/NFD, and back through from_byte_messages. NUL, Vietnamese, emoji and the literal [ASSIST] retain their exact bytes. Surrogates, coercion, malformed role, empty assistant and reserved token injection reject. B native non-UTF8 bytes remain a *separate* raw_b_byte_only path; not silently presented as C text. Special IDs remain byte 0..255, EOS256, PAD257, BOS258, SYS259, USER260, ASSIST261, EOT262 (vocab 2048). Structural role/mask proof is NOT corpus rights or uploader-authenticity proof.

**BC-F02 — separate schema/version.** Proposed shared pack schema ttm.bc.synthetic.sft_pack.v2, template ttm.bc.synthetic.chat_template.v2, checkpoint metadata ttm.bc.synthetic.sft_checkpoint.v2, bridge ttm.bc.c_string_to_b_bytes.v2. Old B v1, old C v1, old B byte pack, historical P04/T4 and old resume schema reject. Metadata-only checkpoint, resume_enabled=false, weights/optimizer NOT_CREATED. **C signoff of the prospective v2 identifiers remains PENDING.**

**BC-F03 — one new canonical byte policy.** ttm.bc.canonical_json_utf8_sorted_compact_lf.v2 uses sorted/compact UTF-8 JSON (ensure_ascii=False, allow_nan=False), **exactly one terminal LF**, binary file IO, no Unicode normalization, no CRLF conversion. No stale B-v1 checksum has been reused. A record with no LF or with CRLF produces a different SHA and fails canonical readback. Windows/Linux extracted bytes were checked identical.

**BC-F04 — seven real persisted files.** write_bundle() creates tokenizer.json, chat_template.json, serialized_inputs.json, target_masks.json, target_labels.json, config.json and checkpoint_schema.json, plus manifest.json. Files use no-overwrite binary writes with fsync and readback. verify_bundle() rereads bytes from disk, verifies SHA256(file bytes), canonical serialization, exact role/shift/masks and frozen synthetic fixture. Each of seven file tamper cases and each of seven manifest hash mutations reject; a changed target with recomputed digest also rejects. Three synthetic records (2 TRAIN, 1 VAL), no real rights/science claim.

## 2. Original C Part A routed against actual B v2

Original C exact source/test blob SHA1: bc_sft_wire_oracle.py = 233c678c89afc3471af4addc55f827e0c52b0383; test_bc_sft_wire_oracle.py = 5c422bc5c4a7a5dc7c107dc1dda4718361b0851e. These are copied *byte-identically* as test fixtures (not edits to C). Runner run_c18_on_b_v2.py routes the unchanged 18 C test bodies through B's typed API via a transparent compatibility module. The C metadata-only fake-hash test #12 tests only structural pins; it is **not** accepted as evidence of actual artifact custody. Real seven-file readback is tested separately by B v2, with hashlib comparing actual physical files.

The prior B v1 29 tests remain unchanged and pass. New B v2 24 tests cover NUL/UTF8/emoji/no normalization, all bit-mask flips, padding and stop, v1/C-schema rejection, seven SHA mutations, source-role ambiguity and P02 CPU backward. True P02 GPT and B cross_entropy_valid are used on actual v2 shifted targets with ignore=-100. Prompt has zero direct target CE but nonzero context embedding gradient; causal future and right-pad isolation pass; no optimizer step or weights saved.

## 3. GitHub source QA and exact output custody

At source commit 724f62a025b8ecc7c452b9ee16c926adfd2b8c7e:

| CI | Windows Python 3.12.10 | Linux Python 3.12.16 |
|---|---|---|
| #43918069534 (torch2.10+cpu) | B v1 29/29, B v2 24/24, C 18/18; P02 probe PASS | same 29+24+18 PASS |
| #43918068585 B regression | SUCCESS | SUCCESS |
| Actual seven SHA file readback | PASS | PASS |

P02 CPU metrics on Windows: 7 valid assistant targets, 25 directly ignored; loss 7.64458370, independent double-precision CE oracle 7.64458395, prompt context-grad L1 ~0.22945, optimizer steps 0; no model-quality inference.

Historical failed CI events remain append-only: #43917527100 (author negative test attempted overlength fixture), #43917874366 (test runner path then C negative error-label mismatch). Only v2 code/test/runner amended; C test body and B v1 source remain unchanged.

### Seven physical file SHA256 (exact actual bytes)

| Key | SHA256 |
|---|---|
| tokenizer_sha256 | c1d7f880382d28eb099fcae6a620b4587228486d6a1a149cf99dc7bcc527bbf5 |
| chat_template_sha256 | 6c818dda5ce614483406864bd7289a5131b8e0e2826c732b767afec3aa63b100 |
| serialized_inputs_sha256 | 03f351b4ddfddaad7fa465ee19e538a9ed199d3602bd772185ac49bc58c2a6e0 |
| target_masks_sha256 | 4a70ef9b946f1a262dc3210c82098ea3e138ea406ffd4f31bc23d2e82149cc50 |
| target_labels_sha256 | 9d1a3f3d7f0e910fc318fe6ff5e0353a926d50e45acc278f06cd5b9f610b90cf |
| config_sha256 | c3bd53773db03bb5c86d4279f94453c022d77d198ad49cefe4ab11bbf2420423 |
| checkpoint_schema_sha256 | 63c73293084fc3a30f77da375e694f443e972d049ec667d9d20e09b849920888 |
| manifest.json (additional) | 17f91e6d3881404909b6cb8c1cd4a2272a92f8b67c179806c2af68768e86d0a2 |

GitHub Actions #43918069534 uploads Windows artifact id 14249659784 (ZIP SHA256 2d78cca691ee69978667f0a11ac57919fbdd8514f3c2e0c9e3aa22186073d3fe) and Linux artifact id 14250512382 (ZIP SHA256 6551e46a02e0a89a1e2e11ff6900ef211c127f16f9c3d68e19380f06121ed80c). ZIP metadata differs but **8/8 extracted JSON bytes identical**. The exact eight JSON byte images are committed to this PR under artifacts/ttm-abc/bc-sft/v2/actual_bytes/ and MANIFEST_CANONICAL_LF.json; their Git blob SHA1 values were matched against the independently downloaded CI ZIP. Manual evidence copy errors in two intermediate commits were corrected; the final eight Git blobs all equal the CI-source bytes. No source/test code changes after successful CI.

## 4. Agent C Part B acceptance matrix for PR #36 (not PR #34)

| Criteria | B author scoped evidence | C Part B |
|---|---|---|
| A01 Byte IDs and zero/null | PASS | PENDING |
| A02 Grammar/role alternation | PASS | PENDING |
| A03 Forged masks, role-literal | PASS | PENDING |
| A04 +1 shift and ignore=-100 | PASS | PENDING |
| A05 Assistant EOT/ending EOS | PASS | PENDING |
| A06 CE valid-count reduction | PASS | PENDING |
| A07 Actual B masked loss callsite | PASS | PENDING |
| A08 Right PAD257 / no pack | PASS | PENDING |
| A09 Future causal and pad isolation | PASS | PENDING |
| A10 Finite synthetic CPU backward | PASS | PENDING |
| A11 max_len=context+1, no truncate | PASS | PENDING |
| A12 New pack/checkpoint schema guard | PASS | PENDING |
| A13 Byte and role-source provenance scope | PASS | PENDING |
| A14 Seven actual SHA files and readback | PASS | PENDING |
| A15 B original P02 import and logits | PASS | PENDING |
| A16 New integration resource and distinct QA | HOLD | PENDING |

BC-0..4: PASS_AUTHOR_CI_SCOPED, **not** independent acceptance. BC-5: HOLD_NEW_INTEGRATION_DISTINCT. Overall: HOLD_BC_INTERFACE_PENDING_C_PART_B_AND_DISTINCT_QA. C M4 PASS_DESIGN_SCOPED, C-G1 HOLD_REAL_DATA, C-G2 UNVERIFIED_CONSTRUCT, C-G8 NOT_EXECUTED remain separate. No new science/TEST/GPU or merge.

### B-M3 historical gate dissent preserved as required by PM

- Prior PM adjudication B-M3 = PASS_ENGINEERING_BASELINE_SCOPED; this ruling remains intact.
- Historical V3 native receipt SHA256 063bb5770c92881ab8fd0ae485f007026594495109c0c0b0359a0ba686c22188 = HOLD_NATIVE_QA with PeakJobMemoryUsed exceeding 256MiB cap on intentionally rejected negative test.
- Distinct reviewer peak-counter opinion = HOLD_PEAK_ACCOUNTING, mechanism unresolved.
- BC-5 remains **HOLD independently**, without transferring any older resource authorization. No V3 rerun, no micro-permit.

**Bước thực hiện tiếp theo — duy nhất:** TTM_PM_BC_V2_EXACT_HEAD_C_PART_B_DISTINCT_QA_AND_FINAL_ADJUDICATION_ONEPACK. Agent C verifies actual PR #36 at exact new HEAD against A01–A16, distinct reviewer checks seven bytes plus adversarial tests, PM then adjudicates BC scoped gate without mixing science.
