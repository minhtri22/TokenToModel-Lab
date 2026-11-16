# Agent C — PR #36 Part B cross-review, F01–F04 onepack and v2 acceptance recommendation

**Operation:** `TTM_PM_BC_F01_F04_WIRE_SCHEMA_HASH_BRIDGE_INTEGRATED_AMENDMENT_AND_DISTINCT_QA_SINGLE_GATE`  
**Role:** Agent C — Contract Owner/Technical Reviewer, not B Implementation Owner.  
**Date:** 2026-11-17. **Initial verdict on inspected v1 candidate:** **`HOLD_INTERFACE`** (four confirmed cross-track blockers). Updated addendum below reviews B v2 implementation candidate separately.  
**No production science, no real dataset/weights, no GPU, no optimizer step, no TEST reuse, no merge.**

## 1. Exact sources, repair responsibilities and preservation

- **PM amended handoff** `40788f557799c7c8a688df32271510aab73a9180`, path `docs/coordination/ttm-abc/TTM_PM_BC_F01_F04_WIRE_SCHEMA_CUSTODY_INTEGRATED_AMENDMENT_HANDOFF_20261117.md`.
- **B actual adapter:** [Draft PR #36](https://github.com/minhtri22/TokenToModel-Lab/pull/36), exact `5f2b71c5f493405c180d6995a21dd7373bd2dbb2`, `src/ttm_track_b/bc_sft_interface.py` Git blob `636a7d695e49802e3d8d80ab0ef06f25ef7d8322`, SHA-256 `f8a4751e896081237565af802dc960ddcfeee44d53f991fbf6e76fc5402a2207`. Original tested implementation at `7a8e15a4451577ab727d5cada6ce15fec2c22080`; latest B PR HEAD only appends author evidence. 29/29 B author checks on Windows/Linux Python 3.12, GitHub Actions 43908305162, **remain PASS for their original scope**.
- **C reviewed/oracle:** [Draft PR #35](https://github.com/minhtri22/TokenToModel-Lab/pull/35), exact prior candidate `56c18e2a00714c8a1c118dabc0ede9d2a1b34b17`. `tests/ttm_track_c/bc_sft_wire_oracle.py` blob `233c678c89afc3471af4addc55f827e0c52b0383`. Earlier `C_M4_PASS_DESIGN_SCOPED` distinct review `9fac5a675955d8b91d6855d27907f239cbfb745f` unaffected; C author's Part A 18/18 **not B runtime interoperability evidence**.
- **Track B baseline** PR #34 `43896bcd034c82e8433bc6a2b53eefbd936616fb` remains independent. This review correctly reads **PR #36**, never treats PR #34 as the integration PR.

The below differences were verified **from exact B/C source** and are not interpretations of author test success.

## 2. Four blocker findings and division of labor

| Finding | Source confirmation at exact old candidate | Agent B required amendment | Agent C acceptance |
|---|---|---|---|
| **BC-F01 `HOLD_TYPED_BRIDGE`** | B `serialize`: `content=list[int]` with bytes 0..255; C `serialize`: `content=str` encoded strict UTF-8. No native C-string→B-byte API in B old adapter. | Explicit `str`→`list[int]` bridge, no implicit NFC, strict error on surrogate, preserve NUL/emoji/Vietnamese/multibyte/role-literal, roundtrip bytes; B raw byte path separate. | Compare C's exact output and B after bridge on independent role fixture with `max_len <= 33`; reject 34+, no truncation and forged role/mask. |
| **BC-F02 `HOLD_SCHEMA_CONTRACT`** | B `ttm.bc.synthetic.sft.pack.v1` and `ttm.bc.synthetic.sft.resume.v1`; C `ttm.bc.synthetic.sft_pack.v1` and proposed `ttm.bc.synthetic.sft_checkpoint.v1`. Metadata resume ≠ actual weights checkpoint. | Add **new** schema version with exact names and fail-closed legacy/alias/mismatch rejection; no reuse of old v1 checksum. | C proposes v2 names below; acceptance requires B explicit signoff + new exact tested source. |
| **BC-F03 `HOLD_CANONICAL_BYTES`** | B `json.dumps(sort_keys=True,separators=(',', ':'),ensure_ascii=False).encode('utf8')`, **no LF**. C `(json.dumps(...)+ '\\n').encode('utf-8')`, **LF**. | Adopt new v2 canonical policy, compute **new** digests of new physical artifacts and exact readback; reject CRLF/no-LF mutation. | C recommends LF v2 to align proposed contract. Preserve original v1 bytes/hash in immutable receipts; no silent rewrite. |
| **BC-F04 `HOLD_SEVEN_HASHES`** | B `make_pack` stores codec/template/model/pack and row source hashes, but **none** of seven named `*_sha256` fields from C oracle exist in B adapter. C original test hashes synthetic key strings rather than saved artifacts. | Generate seven **physical** saved bytes/artifacts with each SHA256 and independent readback; no aliases, no generated hex from key names, and no overwrite. | C independently recomputes from bytes and mutates all seven, rejects mismatched size/hash/canonical/version. |

Token-ID namespace itself **agrees** in B and C Part A: payload byte `0..255`, `EOS=256, PAD=257, BOS=258, SYS=259, USER=260, ASSIST=261, EOT=262`. **Do not** reopen this already aligned allocation.

## 3. Proposed shared *v2* wire contract — C recommendation (B signoff PENDING)

**C design acceptance for proposed v2 identifiers** follows the new B PR #36 implementation at exact `724f62a025b8ecc7c452b9ee16c926adfd2b8c7e`, without altering earlier B v1 evidence. C accepts this naming and canonical-byte policy as a **provisional shared candidate**; B's new CI and distinct QA are evaluated separately. The name `sft_checkpoint.v2` MUST mean metadata-only and MUST NOT imply real weights or resumable training.

| Component | Proposed frozen v2 identity | Semantics |
|---|---|---|
| Wire | `ttm.bc.c_string_to_b_bytes.v2` | synthetic engineering only |
| Codec | `ttm.bc.synthetic.byte_codec.v2` | UTF-8 raw bytes to token IDs 0..255, specials 256..262 |
| Chat template | `ttm.bc.synthetic.chat_template.v2` | BOS, optional SYS, alternating USER/ASSIST, EOT each role, final EOS; assistant-only target |
| SFT pack | **`ttm.bc.synthetic.sft_pack.v2`** | separate from `ttm.bc.synthetic.sft.pack.v1`, `sft_pack.v1`, and old byte windows |
| Resume **metadata** | **`ttm.bc.synthetic.sft_checkpoint.v2`** | `weights=NOT_CREATED`; NOT a trained checkpoint |
| Canonical bytes | **`ttm.bc.canonical_json_utf8_sorted_compact_lf.v2`** | sorted JSON keys; compact separators `(',', ':')`; `ensure_ascii=False`; `allow_nan=False`; UTF-8 **exactly one final LF (0x0a)**; no Unicode normalization; no CRLF conversion |
| Data | strict source `str`→`encode('utf-8','strict')`→byte `list[int]` | preserve NUL, role literals, emoji, NFD/NFC differences; do not coerce bytes/lists into text |
| Max sequence | B synthetic `max_len=33` = P02 context 32 plus one target | `x=ids[:-1]`, `y=ids[1:]` masked by trusted role flags; no truncation or padding-left |
| Loss | `ignore_index=-100`; `CE_sum(valid)/count(valid)` | zero **direct** prompt label loss; gradient **may flow** through prompt embeddings/context |

**Seven named actual artifact bytes** — each stored as a separate stable *v2* canonical JSON file (no byte-hash of just a field name) and hashed from file readback:

| Required digest | Exact artifact filename | Required contents |
|---|---|---|
| `tokenizer_sha256` | `tokenizer.json` | v2 namespace, byte+special map, vocab and codec policy |
| `chat_template_sha256` | `chat_template.json` | role grammar, stop/EOT/EOS, padding, ignore_index, shift |
| `serialized_inputs_sha256` | `serialized_inputs.json` | true SFT input IDs and row/corpus identifier, not plaintext-only |
| `target_masks_sha256` | `target_masks.json` | original unshifted role mask/target admissibility with shape |
| `target_labels_sha256` | `target_labels.json` | post-shift padded y including -100 and exact row shape |
| `config_sha256` | `config.json` | model, run, resource cap, software/codec/template pins |
| `checkpoint_schema_sha256` | `checkpoint_schema.json` | **metadata-only** resume schema definition, no trained weights |

A separate raw `source_bytes.bin` digest is recommended for byte-level provenance but must not be passed off as one of the seven JSON digests. Any serialized `manifest.json` refers to those seven digests; it never hashes itself. Require exact file names, lengths, path containment, no symlinks, no-overwrite writes, immutable original v1 receipt and versioned SHA. The C reference helper `tests/ttm_track_c/bc_v2_contract_oracle.py` exercises synthetic example bytes **only**, not B-produced files.

## 4. Sixteen acceptance controls, current B HEAD vs required v2 candidate

| ID | Control | B `5f2b71c5` | C v2 signoff condition |
|---|---|---|---|
| A01 | Distinct byte/special IDs, 0x00 | `PASS_B_AUTHOR_CI_SCOPED` | preserve, no new collision |
| A02 | Optional SYS, role alternation and EOT/EOS | `PASS_B_AUTHOR_CI_SCOPED` | cross-type bridge must preserve roles |
| A03 | Role provenance and injection, C-F02 | `PASS_B_AUTHOR_CI_SCOPED` | test B and C directly on same inputs, reject mask flip |
| A04 | +1 shift assistant-only labels | `PASS_B_AUTHOR_CI_SCOPED` | C→B equal IDs/labels byte-for-byte |
| A05 | EOT/EOS generation stop | `PASS_B_AUTHOR_CI_SCOPED` | no double EOS and user EOT supervised |
| A06 | ignore -100 and normalized CE, C-F01 | `PASS_B_AUTHOR_CI_SCOPED` | independent exact output and zero direct prompt CE |
| A07 | Actual B masked loss callsite | `PASS_B_AUTHOR_CI_SCOPED` | unchanged masked `cross_entropy_valid` verified on B exact candidate |
| A08 | Right padding and one-row-one-dialogue | `PASS_B_AUTHOR_CI_SCOPED` | no left padding or packing |
| A09 | P02 causal future isolation | `PASS_B_AUTHOR_CI_SCOPED` | distinct exact-candidate QA |
| A10 | Finite backward + nonzero prompt context gradient | `PASS_B_AUTHOR_CI_SCOPED` | independent exact-candidate QA, zero optimizer steps |
| A11 | No truncation, model context 32 | `PASS_B_AUTHOR_CI_SCOPED` | typed bridge rejects >33 IDs |
| A12 | Versioned pack/checkpoint rejects legacy | `HOLD_F02` | new agreed v2 schema and metadata/weights distinction |
| A13 | Byte provenance and C `str` bridge | `HOLD_F01` | strict roundtrip, UTF-8 invalid negative |
| A14 | Seven actual byte SHA and tamper | `HOLD_F03_F04` | true file/size/hash readback, newline/CRLF negatives |
| A15 | Exact B/C import+path+adapter | `HOLD_F01_F02_F03_F04` | new pinned B HEAD and cross-oracle runtime |
| A16 | Native/resource/distinct QA | `HOLD_BC_5` | independent reviewer, don't reuse B-M3 result |

One C-authored v2 design/negative suite **cannot close** A12–A16 without B v2 implementation and independent QA. Reuse older B 29/29 only where the exact source/tests are unchanged; do not claim they tested v2.

## 5. Required C Part B procedure at B's new exact candidate

1. Lock new **PR #36 HEAD**, compare against current `5f2b71c5...`; verify old 29/29 tested code not silently changed without re-QA; diff explicit v2 files/source hash and new B data/receipt version.
2. Inspect B `str`→bytes bridge and run the **same** C user/system/assistant text sample through C v2 typed oracle and B v2 entrypoint. Require same `x,y,flags`, note B's right padding, verify Unicode NUL, Viet, emoji, role literal, unpaired surrogate, UTF-8 invalid B records.
3. Recompute seven SHA-256 from **B's actual persisted artifact bytes** in independent directory, compare to exact manifest, mutate **each** file/size/hash, CRLF/LF and aliases, refuse new/old schema and resumed checkpoint mapping without authorized migration.
4. Compare B masked CE with independent oracle; single bounded synthetic CPU forward/backward, finite gradients, zero direct prompt CE, allowed prompt contextual gradient, causal and padding isolation; no optimizer step or science.
5. Preserve source SHA, run command, Python/Torch, artifact hashes and original evidence; return exact `C_CONTRACT_COMPATIBILITY_PASS_SCOPED` or `HOLD_INTERFACE`. Distinct reviewer then makes its **separate** exact-candidate engineering QA judgement.

## 6. Gate and dissent state preserved

| Gate | Agent C recommendation on **current inspected B HEAD** |
|---|---|
| BC-0 | `PASS_B_C_SOURCE_READBACK_SCOPED` |
| BC-1 | `PASS_B_AUTHOR_CI_ONLY_C_BRIDGE_HOLD` |
| BC-2 | `PASS_B_AUTHOR_CI_ONLY_C_BRIDGE_HOLD` |
| BC-3 | `PASS_B_AUTHOR_CI_CPU_ONLY_DISTINCT_PENDING` |
| BC-4 | `HOLD_INTERFACE_F01_F04` |
| BC-5 | `HOLD_DISTINCT_NEW_SFT_INTEGRATION` |

**B-G5 nuance:** Prior PM `B-G5_M3=PASS_ADJUDICATED_HARD_RESOURCE_ENGINEERING_SCOPED` and `B-G6_M3=PASS_DISTINCT_SOURCE_NATIVE_SCOPED` remain logged. The immutable V3 script negative predicate `HOLD_NATIVE_QA` due to peak accounting, and later reviewer `HOLD_PEAK_ACCOUNTING`, remain separately visible. No V3 rerun, no retroactive broadening of B-M3 gate, no B-M3 permit transfer to B–C SFT.

**Final Part B result for currently available B PR #36:** **`HOLD_INTERFACE`**. There is an implementation but not the repaired, jointly agreed v2 candidate, and **BC-5 stays HOLD**. C M4 `PASS_DESIGN_SCOPED` remains valid; C-G1 HOLD, C-G2 UNPROVEN, C-G8 NOT_EXECUTED. No merge or science dispatch.

**Bước thực hiện tiếp theo — duy nhất:** `TTM_PM_BC_F01_F04_WIRE_SCHEMA_HASH_BRIDGE_INTEGRATED_AMENDMENT_AND_DISTINCT_QA_SINGLE_GATE` — B submits amended PR #36 exact source and physical hash receipt; C reviews once against frozen v2 candidate; distinct reviewer performs new negative/native synthetic QA; PM adjudicates in a single shared evidence packet.


## 7. 2026-11-17 B v2 bridge readback — new candidate, not v1 reversal

The earlier sections' **four HOLD findings apply specifically to B v1 at `5f2b71c5...`**. They are not automatically statements about the new B candidate.

**Latest C-read B exact source:** [PR #36 at `724f62a025b8ecc7c452b9ee16c926adfd2b8c7e`](https://github.com/minhtri22/TokenToModel-Lab/commit/724f62a025b8ecc7c452b9ee16c926adfd2b8c7e). New `src/ttm_track_b/bc_sft_bridge_v2.py` Git blob **`f2cc02821efa4f9628964657d90c7a98c4d67e13`**; new `tests/test_bc_sft_bridge_v2.py` blob **`cb08038adcceb4848790694b62c97f648d0b1b62`**. Pinned `run_c18_on_b_v2.py` routes C's 18 unchanged bodies through B implementation via explicit compatibility shim; the shim's old `verify_manifest` metadata test is **not** a substitute for B `verify_bundle(root)` actual-file custody.

**Static source outcomes for B v2:**

- **BC-F01 — SOURCE_REVIEW_PASS_SCOPED:** `to_byte_messages` strictly requires C `str`, UTF-8 identity; `from_byte_messages` rejects invalid byte strings and is separate from B's `raw_b_byte_only`. Negative source tests cover NUL, surrogate, role-literal, multibyte, NFC/NFD and invalid structures. Real C→B executable cross-oracle on this exact HEAD remains reviewer-dependent.
- **BC-F02 — C_SCHEMA_NAMES_ACCEPTED_SCOPED:** C accepts B's *new and distinct* v2 identities `ttm.bc.synthetic.sft_pack.v2` and `ttm.bc.synthetic.sft_checkpoint.v2`. The **checkpoint-named schema is metadata only** (`scope=METADATA_ONLY_NO_ACTUAL_CHECKPOINT`, `resume_enabled=False`, `weights=NOT_CREATED`), not a training checkpoint. All v1, old T4/P04, plus **C's superseded draft v2 alternative names**, must be rejected without mapping aliases to the same digest.
- **BC-F03 — C_CANONICAL_POLICY_ACCEPTED_SCOPED:** `ttm.bc.canonical_json_utf8_sorted_compact_lf.v2`: sorted compact UTF-8, no normalization, **exact one LF**, `allow_nan=False`. B `canonical()` implementation has that encoding; it is intentionally different from immutable B v1 no-LF byte format. C v2 reference code is amended with exactly B's names.
- **BC-F04 — SOURCE_REVIEW_PASS_SCOPED:** B `write_bundle()` writes seven named JSON files as new physical bytes and re-opens them for SHA; `verify_bundle()` independently opens bytes and validates hash, canonical encoding, IDs, targets, masks and frozen fixture. B new 24 negative tests target all seven content/hash mutations, plus forged valid digests with bad target labels. Actual B-produced files and CI logs must be independently read by a distinct reviewer for `BC-5`.

**C source QA code:** `tests/ttm_track_c/bc_v2_contract_oracle.py` is a *reference* only, now adopting B's selected v2 identities; `test_bc_v2_contract_oracle.py` 18 synthetic/byte-custody negatives are C authored. The earlier separate C workflow at C commit `141914164b82630319687832447a60c4d68349d1`, [Actions #43917885265](https://github.com/minhtri22/TokenToModel-Lab/actions/runs/43917885265), returned SUCCESS **before** C's namespace alignment; the aligned C source must be run again on exact new C commit. Both suites are **not** a distinct B engineering QA.

**Guardrails and outstanding checks:** B public `serialize/build` supports up to max_len=257 to reproduce C oracle, but B P02 model context is 32; **the real B model/pack entrypoint must use max_len=33 and reject oversized model-bound inputs**. B's `verify_bundle()` checks artifact symlinks but does not explicitly reject a symlink at `manifest.json`; enforce no-external-manifest path in distinct negative QA or mark as an advisory/source-hardening item. Both are bounded to synthetic engineering only and do not undermine previously passing v1 CI.

**Current C contract decision:** `C_V2_SCHEMA_CANONICAL_SOURCE_SIGNOFF_SCOPED` (B's names/policy accepted as candidate) but **`C_CONTRACT_COMPATIBILITY_PASS_SCOPED=NOT_YET_ADJUDICATED`** pending exact new B CI and independent executable test of actual file bytes/model path. `BC-5=HOLD`, B-G5 older disputed decisions are append-only. `main`, B branch, A, `lineage.md` unchanged by Agent C; no merge or science.

**Single next operation remains:** `TTM_PM_BC_F01_F04_WIRE_SCHEMA_HASH_BRIDGE_INTEGRATED_AMENDMENT_AND_DISTINCT_QA_SINGLE_GATE` with C's exact-candidate Part B judgement, independent reviewer execution and PM acceptance in one packet.
