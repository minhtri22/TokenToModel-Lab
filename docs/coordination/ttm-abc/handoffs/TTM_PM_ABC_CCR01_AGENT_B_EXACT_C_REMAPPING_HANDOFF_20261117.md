# PM HANDOFF — Agent B: exact C amendment remap after A ACK (ABC V4 CCR-01)

**Operation (same integrated successor, do not fork):** `TTM_PM_ABC_CCR01_SOURCE_REF_T4_CODEC_INTEGRATED_ALIGNMENT_AND_OWNER_READINESS_READJUDICATION_ONEPACK`  
**Date:** 2026-11-17 · **Actor:** B · **Scope:** SOURCE_ONLY / DESIGN_ONLY / NO SCIENCE / NO IMPLEMENTATION / NO MERGE  
**Handoff authority:** PM [integrated original gate](https://github.com/minhtri22/TokenToModel-Lab/issues/32#issuecomment-6938107650), **A ACK** [#6938396264](https://github.com/minhtri22/TokenToModel-Lab/issues/32#issuecomment-6938396264), C amendment [#6938257665](https://github.com/minhtri22/TokenToModel-Lab/issues/32#issuecomment-6938257665).

## 1. Inputs to pin and ACK before remapping

| Source | Exact commit or Git blob | Scope |
|---|---|---|
| PM joint charter | `403491b698ba6586193f2ff2ae00c4441c10c595` / blob `d7fbc02a45b1d1a85cfe9b9594ae88fee495a9e1` | Single source/ownership; unchanged |
| Agent A packet | `7639a53b9d76e16abfa4211cf239c5c3e9d6c940` / A requirements blob `3de320f1e734c7610fb750477803b082fefff753` | 37 A fields; unchanged |
| Agent C **new current** PR35 | `4efe93ce0a3910c449972b3f7e9911a004fe2b3c` | Exactly one successor commit after `614caff47657ccee43ad10ba06ae8ebb782b4114` |
| C registry **new blob** | `364a15d305b71e0c236a27409430f1e27e14aa70` | `artifacts/ttm-abc/track-c/C_SCIENCE_REQUIREMENTS_AND_A_C_COMPATIBILITY_20261117.json` |
| C integrated amendment | blob `e6a77fcb85fbbf24fd1b25e6459c1f40bbfa8e97` | `docs/coordination/ttm-abc/track-c/C_ABC_F01_F02_F03_INTEGRATED_ALIGNMENT_AMENDMENT_V2_20261117.md` |
| Agent A signed-off **in conversation only** | [PM Issue #32 ACK #6938396264](https://github.com/minhtri22/TokenToModel-Lab/issues/32#issuecomment-6938396264) and [C PR35 comment #6938391113](https://github.com/minhtri22/TokenToModel-Lab/pull/35#issuecomment-6938391113) | `A_CCR01_MEASUREMENT_ACK_SCOPED`, **not** real owner cryptographic signature |
| B existing PR37 | `38e24f4fa1ee1eb5a5e1bec5e3746e98a07e13b5` | Existing 37/26/14 feasibility matrix; do not rewrite old history |
| GPT Core / BC source | PR34 `43896bcd034c82e8433bc6a2b53eefbd936616fb` / PR36 `09de6a46574146d863f416e056fcf01091f3efb8` | Previous scoped engineering, **not** prospective runtime candidate |

**GitHub readback already performed by PM:** C previous registry Git blob `64508ace4de057958ccbc9e3c7616a18c022250e` → new `364a15d305b71e0c236a27409430f1e27e14aa70` is **one JSON leaf difference only**: `sources.a_requirements_git_blob` `4f96452215778c3cca1af19bd6d2e3b6506d87d2` (incorrect A evidence index) → `3de320f1e734c7610fb750477803b082fefff753` (correct A 37-field source). Full unchanged field sets A37, C26, B14 ⊂ C26. C PR35 is still Draft. Agent A has ACKed all F01–F03 design semantics. Before work, re-fetch current PR HEAD and record any drift; only the pins above are in scope.

## 2. Single Agent B remap task — four mandatory distinct assertions

**B-READBACK-01 / Custody.** Independently fetch both C registry versions, A original 37 document, C new amendment and A ACK; verify C new registry root pin is **exactly** `3de320f1e734c7610fb750477803b082fefff753`, no alternate-source alias. Compare all non-root fields and each A37 row field/order/source blob against originals. Recompute/verify Git blob and SHA256 as available. Retain historical wrong blob and raw evidence.

**B-READBACK-02 / Logical mapping.** Re-run **source-only**, not science, the same 37 A × 26 C × 14 B-facing compatibility inventory against **new exact C SHA** (77 table rows / **63 distinct logical fields**); compare row order, names, owner, unit, type, byte domain, hold/evidence state, negative oracle and prior B status. **Do not count B14 twice or silently promote `NOT_PROVEN`.** Changes to the C prospective design should be recorded as separately named design ACK, not rewritten old B mapping verdict.

**B-READBACK-03 / T4 codec and byte spans.** Reaffirm **`INCOMPATIBLE_DIRECT_T4_BC`**: historical T4 BPE merges IDs257–2047 vs BC/v2 PAD257/BOS258/SYS259/USER260/ASSIST261/EOT262. C selected **`T4_NATIVE_BPE_EXTERNAL_ROLE_BYTE_SPAN_DESIGN_ONLY`** to preserve historic T4 tokenizer/embeddings, keeping role/answer/source-byte provenance in external sidecar, *not* input role token IDs. B must assess as **prospective design feasibility**, not implemented mapping: per-token trusted UTF-8 byte start/end, regex/pretokenization normalization, no token crossing included/excluded score spans, actual BPE+checkpoint SHA and stop/role semantics. If unproven, `HOLD_BYTE_DENOM` and `HOLD_SFT_INCOMPATIBLE_TOKENIZER`. A sidecar is **not** a way to make historical T4 chat-aware or add an EOT token magically.

**B-READBACK-04 / CE vs bpb.** Verify B's old C-CCR-01 ACK still exactly matches C and A new ACK: B/C v2 shifted **training masked CE** includes assistant content + assistant EOT + final EOS; true byte-only C `val_bpb` excludes special/stop tokens from **both** valid-text NLL numerator and matching raw UTF-8 bytes denominator, with stop CE separately reported. A `a_gold_nll` is one full-vocab next-token nats target, **not** `val_bpb`. Do not change existing BC/v2 byte manifest, tokenizer or A V4 RAW/TAG/epoch/H_SLOT.

## 3. Integrated blocker matrix is required, but no micro-permit

Report `R0=` corrected source alignment (scoped design), `R1=` A I1 pass / C gold HOLD, `R2=` rights/splits HOLD, `R3=` checkpoint/real tokenizer/byte spans HOLD, `R4=` owner-host native resource HOLD, `R5=` A V4 design accepted / native authority HOLD, `R6=` prereg not frozen, `R7=` real independent QA not executed, `R8=` owner GO HOLD. Maintain original V3 memory peak-accounting dissent and B-M3 PM scoped PASS; do not upgrade due to corrected pointer or semantic ACK.

Post **one** `B_REMAP_READBACK_SCOPED` on [Issue #32](https://github.com/minhtri22/TokenToModel-Lab/issues/32), anchored to: C new commit `4efe93ce...`, A ACK #6938396264, B old PR37 commit, shared contract Git blob, and an exact new additive docs/evidence commit *if* source corrections/readback receipts need recording. The re-review should include one `JOINT_COMPATIBILITY_MATRIX` and categorized `PASS/HOLD/INCOMPATIBLE` with **no executable code edits**.

**B completion:** `B_REMAP_READBACK_SCOPED` when source refs/field counts align and all caveats are explicit; otherwise `HOLD_B_SOURCE_REMAP`. Do not claim `ABC_CONTRACT_ALIGNED_DESIGN_SCOPED`: that belongs to **PM final distinct adjudication** only.

## 4. Final PM decision after B

PM re-reads new B evidence + source C + A exact ACK and chooses exactly **`ABC_CONTRACT_ALIGNED_DESIGN_SCOPED` or `HOLD_ABC_CONTRACT_ALIGNMENT`** for the **design contract**. This outcome will **not** grant any I2, SFT training, real checkpoint load, GPU, TEST, research rights, new owner policy, merge or lineage amendment.

**Only next step:** Agent B source remap first, then PM integrated final; same operation, no new successor code name.
