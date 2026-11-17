# Agent B · R0/R3/R4/R5 engineering readiness and owner dependency register

**Operation:** `TTM_B_SHARED_EXACT_CHECKPOINT_TOKENIZER_RESOURCE_FEASIBILITY_AND_COMPATIBILITY_DESIGN_ONEPACK`  
**Mode:** `EXACT_SHA · SOURCE_ONLY · DESIGN_ONLY` — no checkpoint download, new native QA, GPU, science, I2, TEST or merge.  
**Common authority:** PM ABC V4 commit `403491b698ba6586193f2ff2ae00c4441c10c595`, blob `d7fbc02a45b1d1a85cfe9b9594ae88fee495a9e1`. ACK_B Issue #32 `6937885002`.  
**Upstream handoffs:** Agent A packet `7639a53b9d76e16abfa4211cf239c5c3e9d6c940`; Agent C science contract `614caff47657ccee43ad10ba06ae8ebb782b4114`; B PR34 `43896bcd034c82e8433bc6a2b53eefbd936616fb`; B/C PR36 `09de6a46574146d863f416e056fcf01091f3efb8`, source-tested `a83e1526bce842761f3051dad28b90a55395a6aa`.

## Executive gate table (B is NOT final adjudicator)

| R | Current B conclusion | Evidence actually read | Remaining condition |
|---|---|---|---|
| **R0** · exact source and graph | `PASS_SOURCE_GRAPH_SCOPED · HOLD_C_SOURCE_REF_CONFLICT` | PM contract exact Git blob, A37/C26/B14 names and source, B34/BC36 code pins | C machine JSON `sources.a_requirements_git_blob` must be corrected at a new exact C SHA, with C/PM ACK; no rollback of original |
| **R1** · measurement and gold | `A_I1_PASS_SCOPED / C_REAL_GOLD_HOLD` | A M0 v3 exact scorer source/evidence pins, C full-vocab and raw-byte bpb design | real independent gold/rater source and scorer validity unproven; I1 one-token NLL != SFT bpb |
| **R2** · data rights/splits | `HOLD_SOURCE_RIGHTS_SPLIT` | C contract spells family-grouping, near-duplicate and TRAIN-only tokenizer admission | actual raw TRAIN family manifests, licenses, rights custodian and fresh heldout still absent |
| **R3** · weights/tokenizer/interface | `HOLD_REAL_WEIGHT_SHA · INCOMPATIBLE_DIRECT_BPE_BC_TOKEN_IDS` | P02 tied embedding LayerNorm config, 3,749,376-parameter source count, T4 BPE merge ID allocation and B/C v2 7-hash metadata | real weights/optimizer/strict loaded SHA, original BPE raw bytes, source-to-token byte spans, C prospective versioned solution |
| **R4** · resource/compute | `HOLD_NEW_NATIVE_RESOURCE` | T4 4096 labels×1024 steps=4,194,304 reported historical exposures; resource script and B-M3 scoped PM receipt | new measured GPU FLOPs/time/VRAM/RAM hard cap/owner-host Job Object/abort/child cleanup; 74-second raw receipt missing, no 13-minute projection PASS |
| **R5** · evidence/release | `A_V4_DESIGN_ACCEPT_SCOPED / HOLD_NATIVE_RELEASE` | A separate raw/tagged ASCII byte domains and frozen slot, B/C UTF-8 LF 7 SHA and F05/F06 fixes | exact trusted ancestor handle/ACL/reparse and atomic no-replace, after-crash durability, signed policy epoch, owner/principal trust, ledger |
| **R6** · prereg | `DESIGN_ONLY_NOT_FROZEN` | C full-vocab nats / valid bytes, stop-loss split and Data×Compute falsifiers | CCR-01 A/PM interpretation, real data/rights/gold, paired seeds/arms/compute/power/thresholds/TEST reader 0 |
| **R7** · independent QA | `NOT_EXECUTED_REAL_CANDIDATE` | A 65 negative +3 positive planned; BC v2 old synthetic scoped PASS | native and real-data candidate separately distinct, no human independent rights/release attestation |
| **R8** · owner authorization | `HOLD_OWNER_RELEASE` | A frozen `H_SLOT_V3=581fd3acf137c28300813fc48501ff8ee243984588978ae64423fffc044bbe0f`; I2 old preflight HOLD | owner signed policy/trust roots/antirollback/one-shot claim, native evidence and explicit GO after PM |

### R0 dependency/merge graph

- A: Draft PR #33 stacked on Draft PR #28; A source I1 `ec197b5f00d3a037420390edd11ee55047e1d37f` unchanged. I2 `NOT_EXECUTED`.
- C: Draft PR #35 at `614caff47657ccee43ad10ba06ae8ebb782b4114`; C owns gold, rights, prereg and data semantics. C design PASS scoped, C-CCR-01 ACK pending.
- B: Draft PR #34 original `43896bcd034c82e8433bc6a2b53eefbd936616fb` → Draft PR #36 `09de6a46574146d863f416e056fcf01091f3efb8` (stacked, NO merge). Historical T4 source pinned separately; B cannot claim its real weights from source configuration.
- PM: `main=f7a0a5874e8fd895c8ea8d17ceff393a4d4917a3` in inherited contract; no new merge authorized. This design evidence branch is isolated from PR33/34/35/36.
- **Source mismatch:** C registry accidentally pins `4f96452215778c3cca1af19bd6d2e3b6506d87d2` (A PM evidence index blob) at `sources.a_requirements_git_blob`, whereas actual A requirements SHA1=`3de320f1e734c7610fb750477803b082fefff753`. It is not a missing user question or a reason to fabricate source. Correct only under C-owned new exact packet and PM readjudication.

### R3 exact scope and fail-closed selection

Model and tokenizer source-level proofs separate from runtime: (a) P02 tied token embedding and output, learned positions, causal mask, LayerNorm T4 config 2048/256/256/4/4 (3,749,376 unique params) **PASS_SOURCE_ONLY**; (b) T4 actual trained file bytes/SHA/config/vocab/dtype/optimizer state unavailable **HOLD_REAL_CHECKPOINT**; (c) BC/v2 `weights=NOT_CREATED` metadata cannot be loaded as T4; (d) T4 BPE merges 257–2047 **conflict** with BC/v2 structural IDs 257–262. Future prospective approach must maintain exact T4 weights while adapting trusted role/source spans without token ID conflation, OR deliberately change tokenizer/vocab and derive a **new real checkpoint version** with full source/QA, after C/PM consent. Neither is approved by this document.

### R4 conservative finite resource budget — no invented gate PASS

1. CPU/RAM source+manifest preflight and process-handle tree custody in a **future** runner; never silently spawn/unbounded process. Report physical host memory and disk actual bytes, not old host snapshots.
2. Native Windows Python3.12 + pinned Torch/device model, measured CPU RAM/private commit and hard **Job Object** memory limit at runtime; watchdog monotonic deadline; kill entire job on timeout/OOM; verify no grandchildren remain; preserve stdout/stderr bounded and exit/status evidence.
3. T4 GPU selected device capability/driver, actual free+peak allocated/reserved VRAM, precision fp32/fp16 and GradScaler, host-to-device transfer, synchronized step timing across warmup/timed/validation/checkpoint. Require resource min/max/median/CI and worst-case with predeclared margin; NO assumed T4/VRAM availability.
4. Track measured FLOPs (or explicitly instrumented estimate with error method) separately from token presentations; 44M requested target positions cannot be inferred from 4.19M repeats; `1024×4096` old source budget is NOT new science authorization.
5. Persist source exact SHA/config/weights/data/codec/version, sampler seed/order, unique TRAIN positions, exposure totals, true scored data bytes, GPU seconds/wall, memory hard cap/peak, OOM/time failure receipt and checkpoint READY-last SHA. No repeat after ambiguous one-shot claim.
6. Capacity no-Go or missing release means stop **before** new checkpoint access/science claim. Define abort exit codes and false-PASS negative oracles prospectively. No code written in this phase.

**Resource numerical caveat:** 3,749,376 params in FP32 occupy 14.30 MiB weights; gradient+two AdamW moments give theoretical ~57.21 MiB minimum before activations and CUDA allocator etc. This lower bound is **not** a resource cap or a VRAM guarantee. Workload ~4.19M presentations and ~498,287 unique historical positions (reported) implies ~8.42 repeats; new 44M token claim corresponds to >10k steps at unchanged 4096 labels/step, not an observed 13-minute run.

### R5 security / atomicity boundary

BC/v2 has `verify_bundle()` path-level symlink guards for 7 files + manifest. Current synthetic source and QA cannot prove TOCTOU safety, Windows junction/reparse parent substitution, durable NTFS rename or production one-shot. A's V4 ASCII canonical domains and role-bound signatures remain **unaltered** by B; verify exact RAW and TAG separately. A requires trusted directory HANDLE/root FileId, `SetFileInformationByHandle(FileRenameInfo)` relative to authenticated parent, `ReplaceIfExists=FALSE`, flush+independent postpublish rehash, power-loss and W1/W2 competing-writer tests. Source-only design is not native proof and must remain R5 HOLD.

### C-CCR-01 / B semantics ACK

**B accepts this interpretation only:** preserve current assistant EOT + final EOS as SFT **training** CE targets, mask prompt direct CE; evaluate **raw data bytes only** for primary `val_bpb` (stop/structure 0 counted bytes and 0 score nats). Stop CE reported in separate diagnostic `c_sft_stop_target_loss`. If T4 BPE has no trusted token→byte span map or merges across scored/unscored regions, **HOLD_BYTE_DENOM**. C-CCR-01 still requires A/PM ACK; B does not rewrite A/BC schema or infer permission for run.

### One consolidated PM resolution request

Address together: (1) C incorrect A blob pointer; (2) BPE/BC direct token-ID incompatibility and proposed **design-only** migration options; (3) CCR-01 exact stop-loss interpretation; (4) verified real checkpoint/tokenizer/data/rights/gold and native resource evidence; (5) A release authority. These are tracked within a single owner readiness packet, **not** multiple micro-permits.

**B conclusion:** `B_FEASIBILITY_MAPPING_COMPLETE_SCOPED` (source/design) · `HOLD_ABC_CONTRACT_ALIGNMENT` (joint) · `OWNER_RELEASE_HOLD` · `NO_SCIENCE · NO_MERGE`. PM alone executes next `TTM_PM_ABC_UNIFIED_EXACT_SOURCE_DEPENDENCY_AND_OWNER_READINESS_ADJUDICATION_SINGLE_GATE`.
