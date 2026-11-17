# PM — TTM ABC V4 B feasibility packet, exact-source compatibility & unified owner-readiness adjudication

**Operation:** `TTM_PM_ABC_UNIFIED_EXACT_SOURCE_DEPENDENCY_AND_OWNER_READINESS_ADJUDICATION_SINGLE_GATE`  
**Date:** 2026-11-17 · **Mode:** EXACT_SHA · READ_EXISTING_EVIDENCE · DESIGN_ONLY · NO_SCIENCE · NO_MERGE.

## 0. Formal PM decision

**Decision:** `B_FEASIBILITY_MAPPING_ACCEPTED_SCOPED` + **`HOLD_ABC_CONTRACT_ALIGNMENT`**. The technical design packet is complete and explicitly reports contradictions, but the **joint contract cannot be declared aligned** while C's manifest root source pin is wrong and cross-owner CCR acknowledgements are absent. **`HOLD_ALL_OWNER_RELEASES`** for A-I2, real SFT/GPU/TEST, and merge. Do **not** re-open previously closed A I1, C M4, B M3, B/C synthetic QA.

This is a consolidated **one-pack** governance conclusion, not an implementation approval or sequential micro-permits. B's paper feasibility does not prove actual checkpoint, tokenizer runtime byte alignments, measured throughput, dataset rights, owner native memory, signer custody, or future scientific performance.

## 1. Frozen authority and Git graph (snapshot)

- [PM shared contract](https://github.com/minhtri22/TokenToModel-Lab/blob/403491b698ba6586193f2ff2ae00c4441c10c595/docs/coordination/ttm-abc/TTM_PM_ABC_V4_SHARED_COORDINATION_CONTRACT_20261117.md) at `403491b698ba6586193f2ff2ae00c4441c10c595`; exact blob **`d7fbc02a45b1d1a85cfe9b9594ae88fee495a9e1`**.
- [A Draft PR #33](https://github.com/minhtri22/TokenToModel-Lab/pull/33), packet **`7639a53b9d76e16abfa4211cf239c5c3e9d6c940`** stacked on Draft PR #28. Original 37-field A document `docs/coordination/ttm-abc/track-a/A_TO_BC_REQUIREMENTS.md` blob **`3de320f1e734c7610fb750477803b082fefff753`**. Separate A evidence-index JSON blob **`4f96452215778c3cca1af19bd6d2e3b6506d87d2`**.
- [C Draft PR #35](https://github.com/minhtri22/TokenToModel-Lab/pull/35), packet **`614caff47657ccee43ad10ba06ae8ebb782b4114`**, registry `C_SCIENCE_REQUIREMENTS_AND_A_C_COMPATIBILITY_20261117.json` blob **`64508ace4de057958ccbc9e3c7616a18c022250e`**, C contract blob **`a8c8f3ca898456519e82bcccb0ada73af24f6ff9`**.
- [B Draft PR #37](https://github.com/minhtri22/TokenToModel-Lab/pull/37), HEAD **`38e24f4fa1ee1eb5a5e1bec5e3746e98a07e13b5`**, stacked on Draft B/C PR #36 `09de6a46574146d863f416e056fcf01091f3efb8`, itself stacked on B PR #34 `43896bcd034c82e8433bc6a2b53eefbd936616fb`. Comparing PR36 exact source to PR37 HEAD: **6 commits, exactly 5 added documentation/evidence paths**, no implementation/tests/workflow, checkpoint or lineage change. B machine matrix Git blob **`ca484be5ae66340d113fce05c1d0513d0177e7a3`**.
- GitHub `main=f7a0a5874e8fd895c8ea8d17ceff393a4d4917a3` at inspection. PR #28/#33/#34/#35/#36/#37 all Draft/unmerged.
- Shared contract ACKs: [A #6937430413](https://github.com/minhtri22/TokenToModel-Lab/issues/32#issuecomment-6937430413), [C #6937623901](https://github.com/minhtri22/TokenToModel-Lab/issues/32#issuecomment-6937623901), [B #6937885002](https://github.com/minhtri22/TokenToModel-Lab/issues/32#issuecomment-6937885002). `ACK_SHARED_CONTRACT_BLOB=PASS` does **not** equal ACK of C source-pointer correction or CCR-01.

## 2. Independently checked B compatibility mapping

The reviewer fetched B machine matrix, C registry and A requirement/evidence-index files from immutable source commits; compared exact original field names/order for each list and verified B's reported classification counts.

| Matrix | Exact field inventory | EXACT_MATCH | ADAPTER_DESIGN_REQUIRED | NOT_PROVEN | INCOMPATIBLE |
|---|---:|---:|---:|---:|---:|
| A37 | **37/37 same names/order** | 10 | 12 | 14 | 1 |
| C26 | **26/26 same names/order** | 0 | 9 | 17 | 0 |
| B-facing 14 | **14/14 same names/order; subset of C26** | 0 | 7 | 7 | 0 |

**Do not sum 37+26+14 to imply 77 independent requirements**: there are 77 mapped table rows, but B14 is a subset of C26, so **63 unique logical field entries** across A37 and C26 (assuming their distinct namespaces); not an additional 14. `EXACT_MATCH` only denotes *scoped logical/pin compatibility*, not real byte-level evidence of weights or newly obtained data.

## 3. Three integrated contract alignment blockers (not three permits)

### ALIGN-F01 — C registry A requirements source-pointer **incorrect**

At exact C registry Git blob `64508ace...`, `sources.a_requirements_git_blob` is **`4f96452215778c3cca1af19bd6d2e3b6506d87d2`**, which is A's evidence-index JSON, whereas the actual A 37-field document blob is **`3de320f1e734c7610fb750477803b082fefff753`**. The **37 C crosswalk rows use the correct latter blob**, so no blanket invalidation of the 37 logical mappings. This is a reproducible **registry-level custody FAIL** and must be resolved before `ABC_CONTRACT_ALIGNED_DESIGN_SCOPED`.

**Required integrated correction:** C creates an additive **new exact commit**, updating only that C registry root pointer (with source/receipt/status updates *if needed*), leaving all 37 field mappings and archived packet intact in git history. Verify Git blob SHA-1 of *both* underlying A files, new C-registry raw bytes/SHA256 and row-level pins. C signs off `C_SOURCE_POINTER_CORRECTION_ACK`; PM independently reads new commit; B confirms unchanged mapping. Do not edit A files, reuse old C registry digest, or invent aliases.

### ALIGN-F02 — historical T4 BPE and synthetic B/C v2 IDs **incompatible for direct use**

Source-proven:
- Original `ttm_gpt2_bpe2048.py` blob `fa5bd892941ba5aa6e6b2f0b2b0ae974efe297b6`: EOS ID 256, BPE merge IDs **257..2047**.
- Corrected synthetic `bc_sft_bridge_v2.py` blob `c56d98b520fef387fab43bac87b7a9247287b17c`: EOS 256 but PAD/BOS/SYS/USER/ASSIST/EOT IDs **257–262**. The same IDs mean different things.

Thus **direct reuse of B/C v2 serialized ID packs in historical T4 embedding weights is `INCOMPATIBLE`** regardless of `vocab_size=2048`, tied embeddings or any metadata checkpoint naming. Do not downgrade this hard finding to a cosmetic adapter issue.

**Prospective choice (DESIGN_ONLY, requires C semantic ACK, A measurement ACK, B source feasibility and PM):**
- Preferred *candidate* for evaluating existing historical T4 weights: preserve original T4 tokenizer and weight IDs; use a **separately versioned role/protocol span adapter outside the BPE ID namespace**, with strict raw-byte span attribution, trusted mask provenance, and fail-closed boundary-straddling BPE token handling. This **does not declare that adapter implemented or feasible yet**.
- Alternative separate study: introduce a newly versioned tokenizer/special namespace and rebind/retrain affected embeddings with a new checkpoint/data lineage. This cannot be called a reuse of historical T4 checkpoint weights.
- **Keep B/C v2 synthetic contract and its 7 immutable artifact SHA unchanged**. C must explicitly choose which *prospective* path is accepted for requirements/endpoint semantics or declare `HOLD_CODEC_CHOICE`. B cannot choose a C scientific endpoint; A validates measurement byte alignment. No source code, actual checkpoint or training in this operation.

### ALIGN-F03 — C-CCR-01 scoring-mask semantics, not a training-wire change

C's [science contract V1](https://github.com/minhtri22/TokenToModel-Lab/blob/614caff47657ccee43ad10ba06ae8ebb782b4114/docs/research/ttm-abc/track-c/C_SCIENCE_DATA_EVAL_CONTRACT_V1.md) and [CCR-01](https://github.com/minhtri22/TokenToModel-Lab/issues/32#issuecomment-6937644143) correctly distinguish:
- **SFT TRAINING CE**: supervise genuine assistant-content tokens **plus assistant EOT and final EOS**, via +1 shift; mask system/user/header/PAD from direct targets, allow gradient propagation through context.
- **Raw UTF-8 byte-based `val_bpb` EVALUATION**: **exclude** EOT/EOS/special/role/PAD from both numerator (scored NLL) **and** denominator (valid raw bytes); endpoint `sum(valid data-target NLL nats) / (ln(2) × valid data bytes)`. NTP raw-text bpb and SFT answer-only bpb are different estimands. Token→byte span proof is necessary for BPE.
- **A I1 original full-vocab one-gold-token NLL** is not equivalent to bpb. It should be kept unchanged.

B's [change request](https://github.com/minhtri22/TokenToModel-Lab/issues/32#issuecomment-6937997482) explicitly ACKs this semantics in design. PM **provisionally accepts the semantic distinction for a future design contract**, without changing A V4 ASCII release bytes or B/C v2 UTF-8/LF training wire. **A ACK + C acknowledgement of A's phrasing/domain** are still needed to close cross-track contract alignment; no synthetic test result proves real T4 BPE byte offsets. A should confirm that the A requirement phrase "BOS/EOT/EOS/PAD ignored roles" refers only to **byte-only bpb view**, never assistant stop CE.

## 4. Source-level facts and explicit nonclaims

P02 source blob `9762343e06cf800b50574c2871ae1ed58537fb18`: T4 candidate vocab 2048, context 256, width 256, layers4, heads4, learned positions, LayerNorm and tied output head. Counting shared weight only once yields **3,749,376 unique trainable parameters** (source/config arithmetic, not a real checkpoint load). A file/schema claiming trained checkpoint or `weights=NOT_CREATED` metadata does not prove real weights or optimizer/scheduler/rng continuity.

B's historical **4,194,304** = 1,024×4,096 **target-label exposures**, not independent TRAIN tokens; about 498,287 distinct TRAIN target positions is reported, not rehashed from private source in this review. **74 seconds / 1,024 steps** is unverified from an original raw timing receipt; **13 minutes for 44M** is unmeasured extrapolation. No numerical T4 time, FLOP or storage GO.

## 5. Prospective integrated R0–R8 owner-readiness matrix

| Gate | Current PM design assessment | Missing before any real release |
|---|---|---|
| **R0** source graph/index | `PASS_SCOPED_WITH_ALIGN_F01_HOLD` | Correct C registry root blob in new exact commit + joint ACK and prospective candidate pin; PR28→33, PR34→36→37, PR35 separate |
| **R1** measurement and gold | `A_I1_PASS_MEASUREMENT / C_GOLD_HOLD` | new outcome validity, gold/rater coverage, byte and target matching; no I1→bpb auto promotion |
| **R2** rights, corpus/family split | `HOLD_REAL_SOURCE_RIGHTS` | actual source bytes/rights, split/family SHA and fresh heldout, no recycling TEST/FRESH16/FINAL24 as confirmatory |
| **R3** real checkpoint and codec | **`HOLD_WEIGHTS_AND_CODEC`** | true weight byte SHA/load/shape, TRAIN-only BPE hash, new versioned adapter and exact span/denominator proof; direct v2 pack incompatible |
| **R4** native resource | `HOLD_NEW_NATIVE_RESOURCE` | measured runner timing/VRAM/host RAM/hard limits/watchdog/children on new exact authorized candidate |
| **R5** OnePack/receipt custody | `A_V4_DESIGN_ACCEPT_SCOPED / HOLD_NATIVE` | owner trust roots/signatures/epoch, ancestor move/TOCTOU/NTFS no-replace race, global V3 SLOT ledger and durability QA |
| **R6** prereg, equal-compute | `DESIGN_ONLY_NOT_FROZEN` | freeze fresh endpoints/controls/splits/seed/compute before actual study |
| **R7** independent new candidate QA | `NOT_EXECUTED_FOR_REAL_STUDY` | synthetic A/BC QA not transferable to real checkpoint/runner/data; 65 A negatives+3 positives remain design-only |
| **R8** explicit owner GO/HOLD | **`HOLD_OWNER_RELEASE`** | one integrated exact-scope owner decision; no self-permit |

**Boundary:** `R0–R8` is one prospective release contract, not nine micro-permits. Science/merge remains HOLD regardless of any design ACK. Preserve B M3 PM scoped PASS with immutable V3 native HOLD and peak-accounting dissent, C M4 scoped design PASS, BC interface scoped engineering PASS, A I1 measurement PASS and V4 design acceptance.

## 6. One follow-up packet — assignments for shared alignment (C → A → B → PM, no independent forks)

**C (source/endpoint owner):** in one *additive C registry amendment*, repair ALIGN-F01 root source pointer; explicitly accept the split SFT stop CE vs bpb scoring mask of ALIGN-F03; choose and document a **prospective** T4 vs BC/v2 ID collision handling design option for ALIGN-F02, with all original C source/rows/negative tests/rights statuses retained. Post `C_INTEGRATED_ALIGNMENT_PACKET_READY_SCOPED` with new exact SHA.

**A (measurement/release owner):** read new exact C amendment and B's source evidence; explicitly ACK the C-CCR-01 NLL/valid-bytes/stop-mask distinction, T4 span alignment constraints and original A I1 vs prospective C bpb scopes; confirm no change to V4 dual RAW/TAG, signed policy epoch or `H_SLOT_V3`. Post `A_MEASUREMENT_ALIGNMENT_ACK_SCOPED` with exact C source; no I2 release.

**B (engineering owner):** read C amendment and A ACK; compare 37/26/14 B mappings against new source, ensure no unreviewed semantic changes, confirm `INCOMPATIBLE_DIRECT_T4_BC` persists and proposed adaptation is **only DESIGN_REQUIRED**, not implemented; post `B_REMAP_READBACK_SCOPED` to the same Issue #32, optionally new evidence-only commit if new hash pointers need durable custody.

**PM final:** independently verify source diff, corrected root/row blob matches, all three ACK exact refs, no change to frozen wires/checkpoint, then issue only `ABC_CONTRACT_ALIGNED_DESIGN_SCOPED` or `HOLD_ABC_CONTRACT_ALIGNMENT`. These ACKs must be part of **one integrated transaction**; do not create three release permits.

## 7. Single next operation

`TTM_PM_ABC_CCR01_SOURCE_REF_T4_CODEC_INTEGRATED_ALIGNMENT_AND_OWNER_READINESS_READJUDICATION_ONEPACK`

This is the *only* proposed successor: one C additive source amendment + A scoped measurement ACK + B source-remap readback + PM distinct adjudication, retaining all missing real research and resource evidence in R1–R8 HOLD. No I2, no new SFT runner, no external checkpoint download, no GPU, no historical TEST, no merge, no `main`/`lineage.md` mutation.

**Final current state:** `A_PACKET_READY_SCOPED · C_PACKET_READY_SCOPED · B_PACKET_READY_SCOPED · B_FEASIBILITY_MAPPING_ACCEPTED_SCOPED · HOLD_ABC_CONTRACT_ALIGNMENT · R3_R4_R5_R8_HOLD · NO_SCIENCE · NO_MERGE`.
