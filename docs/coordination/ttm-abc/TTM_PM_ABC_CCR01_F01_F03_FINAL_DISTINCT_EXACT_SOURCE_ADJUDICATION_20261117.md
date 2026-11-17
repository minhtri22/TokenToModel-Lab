# TTM PM — ABC V4 CCR-01 final independent exact-source design adjudication

**Operation:** `TTM_PM_ABC_CCR01_SOURCE_REF_T4_CODEC_INTEGRATED_ALIGNMENT_AND_OWNER_READINESS_READJUDICATION_ONEPACK`  
**Date:** 2026-11-17 · **Mode:** `DISTINCT_AI_SOURCE_READBACK / DESIGN_ONLY / NO_NEW_SCIENCE / NO_MODEL_RUNTIME / NO_OWNER_RELEASE / NO_MERGE`.

## FINAL PM DECISION

**`ABC_CONTRACT_ALIGNED_DESIGN_SCOPED` — PASS.**

All **ALIGN-F01..F03** are consistently accounted for on the **same frozen revision set**, with a **real direct B/C-to-T4 tokenizer incompatibility explicitly retained as an implementation blocker**. This gate certifies **contract alignment**, not real checkpoint/tokenizer applicability or a readiness-to-execute permit. The earlier PM `HOLD_ABC_CONTRACT_ALIGNMENT` remains part of the historical lineage at [prior PM decision](https://github.com/minhtri22/TokenToModel-Lab/blob/8e7606c9b630ce24c4e039e402b2c88fd00fd5b5/docs/coordination/ttm-abc/TTM_PM_ABC_V4_B_PACKET_INTEGRATED_EXACT_SOURCE_ADJUDICATION_20261117.md), superseded only for the *design alignment* gate by the verifiably corrective C/A/B evidence below.

**Unchanged:** `HOLD_ALL_OWNER_RELEASES`, A-I2 not executed, real SFT not executed, real weights/rights/gold/resources not verified, no new TEST/GPU, no PR merged, `main` / `lineage.md` unchanged.

### 1. Exact source pins and dependent ACKs

| Role | Exact immutable anchor | Readback |
|---|---|---|
| PM shared coordination contract | commit `403491b698ba6586193f2ff2ae00c4441c10c595`; Git blob `d7fbc02a45b1d1a85cfe9b9594ae88fee495a9e1` | SAME frozen contract; no schema fork |
| A requirements and packet | commit `7639a53b9d76e16abfa4211cf239c5c3e9d6c940`; requirements blob `3de320f1e734c7610fb750477803b082fefff753` | original A37 and A V4 preserved |
| A cross-owner measurement ACK | [Issue #32 comment 6938396264](https://github.com/minhtri22/TokenToModel-Lab/issues/32#issuecomment-6938396264) | `A_CCR01_MEASUREMENT_ACK_SCOPED` on **exact C SHA** |
| C original historical packet | `614caff47657ccee43ad10ba06ae8ebb782b4114`; registry blob `64508ace4de057958ccbc9e3c7616a18c022250e` | wrong root evidence pointer preserved, not rewritten |
| C corrected current packet | [PR #35](https://github.com/minhtri22/TokenToModel-Lab/pull/35) HEAD `4efe93ce0a3910c449972b3f7e9911a004fe2b3c`; registry blob `364a15d305b71e0c236a27409430f1e27e14aa70`; integrated amendment blob `e6a77fcb85fbbf24fd1b25e6459c1f40bbfa8e97` | C amendment `C_INTEGRATED_ALIGNMENT_PACKET_READY_SCOPED`; one commit and four source-only paths |
| B original feasibility | `38e24f4fa1ee1eb5a5e1bec5e3746e98a07e13b5`; B source matrix blob `ca484be5ae66340d113fce05c1d0513d0177e7a3` | original B feasibility and HOLD blockers preserved |
| B corrected remap | [PR #37](https://github.com/minhtri22/TokenToModel-Lab/pull/37) HEAD `ff4304e04f44de69a07cd767b2a7f400d6e95e88`; B remap blob `c2d4a050f35218de2c023d3a5c50fb3454404c23`, B author receipt blob `f65e116172db8acde9477f1870596c54265a37ac` | `B_REMAP_READBACK_SCOPED` at [Issue #32 comment 6938858385](https://github.com/minhtri22/TokenToModel-Lab/issues/32#issuecomment-6938858385) |
| Historical B/C synthetic bridge | PR36 `09de6a46574146d863f416e056fcf01091f3efb8`; B/C bridge Git blob `c56d98b520fef387fab43bac87b7a9247287b17c` | scoped engineering PASS remains; not re-executed |
| Main snapshot | `f7a0a5874e8fd895c8ea8d17ceff393a4d4917a3` | PR #28/#33/#34/#35/#36/#37 all open Draft/unmerged |

### 2. Independent byte and semantic readback, **not merely acceptance of B's authored receipt**

1. PM fetched both C machine registries from exact original and amended Git commits. Old blob `64508ace4de057958ccbc9e3c7616a18c022250e`, new blob `364a15d305b71e0c236a27409430f1e27e14aa70`. PM independently implemented **SHA-256 over the GitHub-fetched UTF-8 byte strings**, validated against empty-string `e3b0c442...` and `abc` `ba7816bf...` standard vectors. Exact old registry SHA-256 = **`bc4131f172ba2744bd1bfb657846f5e3127175ac15908f46bc9904e3d19add0d`**; new = **`6db387c75e3f2f0ae8b05af65f66cfddf025ad2ba06d562e8645a16f9f0aab1d`**, matching C/B recorded values. Both source files are 66,167 UTF-8 bytes. (GitHub GET content/readback, not an independent host filesystem checkout.)
2. PM recursively compared both parsed JSON trees: **one leaf changed, exactly `$.sources.a_requirements_git_blob`**, from old erroneous `4f96452215778c3cca1af19bd6d2e3b6506d87d2` (A evidence-index JSON) to correct `3de320f1e734c7610fb750477803b082fefff753` (A original 37 requirements document). No other C source fields or row definitions changed. Git blob of actual A requirements independently fetched and equals expected `3de320f1...`.
3. PM compared all original B 77 mapping rows vs remapped B 77: **A37 37/37 row objects unchanged**, C26 26/26 and B14 14/14 rows differ **only** in two source-reference fields `source_requirement_commit` and `source_requirement_blob` each (26 + 14 = 40 reference updates), pointing to C new exact commit/blob. **Zero** changes to status, field name, type, unit, owner, byte domain, validation, negative case, scope, evidence/hold policy or text basis. B14 is a strict subset of C26, so **77 table rows = 63 logically distinct fields**.
4. PM separately compared **637 selected field attributes** across B remap and C new registry: A37 × 9, C26 × 9, B14 × 5. **0/637 mismatches** in field name/order/owner/type/unit/byte domain/validation/negative/hold/ack attribution where defined. B mapping classification **preserved**, not promoted: A37 = 10 EXACT_MATCH +12 ADAPTER_DESIGN_REQUIRED +14 NOT_PROVEN +1 INCOMPATIBLE; C26 = 9 ADAPTER_DESIGN_REQUIRED +17 NOT_PROVEN; B14 = 7 ADAPTER_DESIGN_REQUIRED +7 NOT_PROVEN (subset).
5. PM checked B PR37 old→new GitHub commit compare: **three new evidence/docs files across three commits**, no code, tests, workflows, old evidence overwrite, or real checkpoint change. C amendment old→new: one commit/four docs/evidence/status paths, no runnable model implementation. Underlying A/BC legacy source blobs remained pinned.

### 3. Findings ALIGN-F01/F02/F03 — jointly closed at **design** scope

**ALIGN-F01 — `PASS_EXACT_SOURCE_POINTER_AND_CUSTODY_SCOPED`.** Correct registry root points to A requirements blob, not the A evidence index. Old wrong hash and original C packet permanently retained; readback verifies exact byte SHA. No new source-pointer blocker in the current design packet.

**ALIGN-F02 — `PASS_EXPLICIT_INCOMPATIBILITY_AND_PROSPECTIVE_DESIGN_CHOICE`; direct runtime `INCOMPATIBLE`.** Original T4 BPE [source blob `fa5bd892941ba5aa6e6b2f0b2b0ae974efe297b6`](https://github.com/minhtri22/TokenToModel-Lab/blob/43896bcd034c82e8433bc6a2b53eefbd936616fb/tools/pilot_t4/integrated/source_t2/ttm_gpt2_bpe2048.py): byte IDs0–255, EOS256, **1791 BPE merge IDs257–2047**. [Synthetic B/C v2 bridge](https://github.com/minhtri22/TokenToModel-Lab/blob/09de6a46574146d863f416e056fcf01091f3efb8/src/ttm_track_b/bc_sft_bridge_v2.py) uses PAD257/BOS258/SYS259/USER260/ASSIST261/EOT262. Thus **direct serialization into historical T4 embeddings is semantically invalid** even at equal vocab=2048. C selected `T4_NATIVE_BPE_EXTERNAL_ROLE_BYTE_SPAN_DESIGN_ONLY`, A cross-ACKed and B accepted as **`ADAPTER_DESIGN_REQUIRED_NOT_IMPLEMENTED`**. Sidecar metadata is *external*, not input token IDs, cannot make old T4 chat-aware or invent EOT. Require actual T4 checkpoint raw SHA and tokenizer manifest, exact source-byte span provenance, full-token inclusion/no cross-boundary, stop/role protocol independent evidence. **`HOLD_BYTE_DENOM` and `HOLD_SFT_INCOMPATIBLE_TOKENIZER` unchanged.** A selected design option is not runtime compatibility.

**ALIGN-F03 — `PASS_A_C_B_SEMANTIC_AGREEMENT_DESIGN_SCOPED`.**
- B/C v2 **SFT training cross entropy** shifted +1 gold targets: **assistant content + assistant EOT + final EOS** directly supervised; system/user/header/PAD ignored for direct CE, contextual gradients allowed.
- C prospective **byte-only `val_bpb`**: sum **full-vocab** teacher-forced gold-text target NLL in **nats** restricted to exact unambiguously matched genuine text/UTF-8 source bytes; denominator `ln(2) * corresponding_valid_data_bytes > 0`; protocol/role/stop EOT/EOS not counted in **either** numerator or denominator; report stop CE separately. A partial BPE token crossing selected/excluded byte-span boundary **must HOLD**, never split/impute its loss post hoc.
- A frozen M0 `a_gold_nll` = one full-vocab next-token NLL **nats per gold target**, **not** C bits/byte. `H_SLOT_V3`, RAW/TAG SHA domain, signed V4 epoch, and BC/v2 canonical UTF-8 one-LF seven artifact SHA unchanged.
- A/C/B ACK is agreement on estimator semantics, **not** proof that real T4 byte offsets or valid gold exist.

### 4. PM R0–R8 distinction: *design alignment PASS* ≠ *release readiness*

| Barrier | Final status |
|---|---|
| R0 exact-source/source pointer/contract alignment | **`PASS_SCOPED_DESIGN_SOURCE_LOCK`** on exact pinned sources; stacked PR dependency remains Draft/unmerged |
| R1 measurement/gold | A I1 `PASS_SCOPED_MEASUREMENT` and C science metrics defined; **C real gold/rater `HOLD_UNPROVEN`** |
| R2 real data rights/splits | `HOLD_RIGHTS_FAMILY_FRESH_HELDOUT` |
| R3 real T4 weights/tokenizer/byte-span | `HOLD_REAL_CHECKPOINT_BYTE_DENOM_AND_SFT_STOP_CODEC`; **direct bridge INCOMPATIBLE** |
| R4 new science native CPU/GPU/RAM/VRAM | `HOLD_NEW_OWNER_HOST_RESOURCE` |
| R5 A V4 release and evidence custody | `DESIGN_ACCEPT_SCOPED`; **real signer/NTFS ancestor/TOCTOU/ledger/crash QA HOLD** |
| R6 confirmatory prereg/equal budget | `DESIGN_ONLY_NOT_FROZEN_FOR_NEW_STUDY` |
| R7 real exact-candidate QA | `NOT_EXECUTED_REAL_STUDY`; A V4 65 negative+3 positive still **design-only, no native execution** |
| R8 integrated owner GO/HOLD | **`HOLD_OWNER_RELEASE`** |

Prior scoped results preserved: A I1 `CLOSED_PASS_SCOPED_MEASUREMENT`, A V4 `DESIGN_ACCEPT_SCOPED`; B M3 `PASS_ENGINEERING_BASELINE_SCOPED_BY_PRIOR_PM` **with historic V3 native `HOLD_NATIVE_QA` and peak-accounting reviewer dissent retained**; C M4 `PASS_DESIGN_SCOPED`; B/C synthetic `BC_INTERFACE_PASS_ENGINEERING_SCOPED`. No new science in this operation.

### 5. Formal scope and next one operation

**Final design-level gate:** `ABC_CONTRACT_ALIGNED_DESIGN_SCOPED`. This supersedes earlier `HOLD_ABC_CONTRACT_ALIGNMENT` *only for cross-track agreement*, not its historical evidence, nor any R1–R8 resource/science/owner HOLD. Independent review = another AI PM reviewer and separate source logic, not independent authenticated human signatures. Publication using owner's GitHub account is not independent account custody.

**Next — single program-level owner readiness packet only** (design/read-only, no science dispatch):  
`TTM_PM_ABC_OWNER_PROSPECTIVE_RELEASE_READINESS_AND_EXACT_MERGE_DEPENDENCY_REVIEW_SINGLE_GATE`. Establish one decision matrix for **two alternatives A-I2 and real SFT**, source/rights/weights/byte offsets/native budget and stacked merge graph PR28→33, PR34→36→37, PR35 separate. Owner explicitly chooses GO/HOLD later on exact scope; currently **HOLD**. Avoid micro-permit chain; do not start a real run, source refactoring, or branch merge here.

**Invariant:** `ABC_CONTRACT_ALIGNED_DESIGN_SCOPED · A_I2_HOLD · REAL_SFT_HOLD · DIRECT_T4_BC_INCOMPATIBLE · B_C_SIDECAR_DESIGN_ONLY · NO_NEW_SCIENCE · NO_GPU · NO_TEST · NO_MERGE · LINEAGE_MD_UNCHANGED`.
