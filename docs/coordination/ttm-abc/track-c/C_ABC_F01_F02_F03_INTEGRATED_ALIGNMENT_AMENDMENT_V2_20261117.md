# Agent C — ABC integrated ALIGN-F01/F02/F03 amendment V2

**Operation:** `TTM_PM_ABC_CCR01_SOURCE_REF_T4_CODEC_INTEGRATED_ALIGNMENT_AND_OWNER_READINESS_READJUDICATION_ONEPACK`  
**C decision:** `C_INTEGRATED_ALIGNMENT_PACKET_READY_SCOPED`  
**Global decision:** `HOLD_ABC_CONTRACT_ALIGNMENT` pending A measurement ACK, B re-map and PM distinct independent readback.  
**Date:** 2026-11-17 · **Mode:** SOURCE_ONLY / DESIGN_ONLY / NO_SCIENCE / NO_GPU / NO_I2 / NO_MERGE.

Direct source: [PM PR #35 comment #6938113122](https://github.com/minhtri22/TokenToModel-Lab/pull/35#issuecomment-6938113122) and [PM Issue #32 adjudication #6938107650](https://github.com/minhtri22/TokenToModel-Lab/issues/32#issuecomment-6938107650). One amendment **within the immutable shared PM contract**, not a replacement BC runtime codec, nor science release.

## Source-lock registry

| Source | Exact commit and blob |
|---|---|
| Shared PM contract | `403491b698ba6586193f2ff2ae00c4441c10c595` · blob `d7fbc02a45b1d1a85cfe9b9594ae88fee495a9e1` |
| Agent A packet | `7639a53b9d76e16abfa4211cf239c5c3e9d6c940` · requirements `A_TO_BC_REQUIREMENTS.md` blob `3de320f1e734c7610fb750477803b082fefff753` |
| Distinct A evidence-index JSON | same A commit · blob `4f96452215778c3cca1af19bd6d2e3b6506d87d2` — **not requirements** |
| C frozen original history | `614caff47657ccee43ad10ba06ae8ebb782b4114` · original machine registry blob `64508ace4de057958ccbc9e3c7616a18c022250e` |
| B feasibility packet | PR #37 `38e24f4fa1ee1eb5a5e1bec5e3746e98a07e13b5`, PM `B_FEASIBILITY_MAPPING_ACCEPTED_SCOPED`, not runtime/science |
| T4 original BPE code | `tools/pilot_t4/integrated/source_t2/ttm_gpt2_bpe2048.py` Git blob `fa5bd892941ba5aa6e6b2f0b2b0ae974efe297b6` @ B core `43896bcd034c82e8433bc6a2b53eefbd936616fb` |
| Synthetic BC/v2 | PR36 `09de6a46574146d863f416e056fcf01091f3efb8`; tested source `a83e1526bce842761f3051dad28b90a55395a6aa`, bridge blob `c56d98b520fef387fab43bac87b7a9247287b17c` |

## F01 — versioned, one-property machine source-pointer correction

**Before:** at frozen C commit `614caff...`, `artifacts/ttm-abc/track-c/C_SCIENCE_REQUIREMENTS_AND_A_C_COMPATIBILITY_20261117.json` has `sources.a_requirements_git_blob = 4f96452215778c3cca1af19bd6d2e3b6506d87d2`, the *A PM evidence-index* Git blob, not the A requirements document.

**After in NEW C commit:** same path `sources.a_requirements_git_blob = 3de320f1e734c7610fb750477803b082fefff753`, the verified A 37-field requirements file. **The only JSON tree difference** is `$.sources.a_requirements_git_blob`; all 37 per-row A blob references were already correct and remain exact; all 37 A rows, 26 C additional rows and B14 subset unchanged. A37 + C26 = **63 unique logical fields**; B14 is a subset of C26 and must not be double-counted. Preserve original C commit and incorrect blob for historical forensic trace; never mutate existing commit or alias its SHA. Source pointer correction does not change any A/BC runtime schema, tokenizer, seven artifact SHA or historical science evidence.

**Negative oracle:** old source pointer, a pointer to another A document, forged hexadecimal, changed row-level source pin, 37/26/14 field drift => `HOLD_SOURCE_REF_CONFLICT`. Third party must fetch **new exact C commit and blob**, not silently reuse old `614caff...`.

## F02 — source-proven direct incompatibility and C prospective design decision

Original T4 BPE: IDs **0–255 base byte**, **EOS256**, **257–2047 are 1,791 BPE merges**. BC/v2 synthetic SFT: **EOS256, PAD257, BOS258, SYS259, USER260, ASSIST261, EOT262**. Thus IDs **257–262** collide with real BPE merges, even though vocab dimensions are 2048. Shape-compatible embedding weights are NOT semantically compatible.

**C accepts exact B/PM finding:** `DIRECT_BC_V2_PACK_TO_T4_WEIGHTS=INCOMPATIBLE` (proven by source, **not** simply UNVERIFIED). For the *historical T4 checkpoint*, choose the prospective **`T4_NATIVE_BPE_EXTERNAL_ROLE_BYTE_SPAN_DESIGN_ONLY`** route:

1. **Do not change** original T4 BPE token ID meaning or trained embedding/head vocabulary. Do **not** send BC/v2 PAD/BOS/SYS/USER/ASSIST/EOT numeric IDs into historic T4 as special/control IDs.
2. Preserve source-authenticated role/answer/stop intent, family/split references and scoring selections in an **external sidecar provenance** tied to exact tokenizer/source/checkpoint hashes. Metadata is not emitted into model token stream and **does not make an old T4 NTP decoder chat-aware**. Sidecar permits *selection of already-tokenized content spans* for qualified teacher-forced scoring, not role conditioning by magic.
3. Future B proof must show actual T4 tokenizer raw manifest/weights SHA, raw UTF-8 text exact byte coverage and per-token `[start,end)` offsets, stable encode/decode, normalized/pretokenization behavior, full coverage without gap/overlap and no merge token crossing selected vs excluded byte boundaries. If any token spans mixed role/stop/data, **reject** with `HOLD_BYTE_DENOM` rather than splitting token NLL post hoc.
4. **Historical T4 does not have proven assistant EOT token**; its shown EOS256 is not proof of BC EOT262 compatibility. External role metadata is not sufficient to claim real historical T4 **SFT assistant-stop CE** feasibility; until a versioned, independently checked stop/role serialization or new tokenizer study exists, `HOLD_SFT_INCOMPATIBLE_TOKENIZER`. If tokenizer unchanged, an authorized future study could potentially measure raw-text NTP byte NLL or aligned selected data spans — still subject to rights/weights/resource GO, not authorized today.
5. Alternative: new tokenizer/vocabulary with distinct embedding/head remapping or fresh training and checkpoint lineage is a **separate prospective study**; never reinterpret old checkpoint weights or silently replace accepted BC/v2 codec. C owns endpoint intent, B owns technical mapping, A ACKs measurement domain and PM adjudicates.

Falsifiers: ID257 wrong meaning, EOS↔EOT alias, any BC/v2 role ID sent to T4 model, unverified BPE raw-byte offsets, partial token boundary split, model quality/capacity inferred from old synthetic tests.

**F02 status:** `DIRECT_MAPPING_INCOMPATIBLE_SOURCE_VERIFIED` · `PREFERRED_ADAPTER_SELECTED_DESIGN_ONLY` · `B_REAL_TOKENIZER_CHECKPOINT_PROOF_HOLD`.

## F03 — scoped C cross-ACK of PM's CCR-01 interpretation

C acknowledges PM Issue #32 #6938107650, after B ACK. **No schema change**:

- **BC/v2 SFT training CE (unchanged):** assistant UTF-8 answer bytes, **assistant EOT + final EOS supervised** under shifted +1 target mask; ignore system/user/headers/PAD and user EOT as direct CE targets; prompt context gradients allowed.
- **C primary byte-only `val_bpb` (separate evaluation selection):** sum stable **full-vocabulary** teacher-forced NLL **only for genuine, unambiguously aligned UTF-8 text data** into numerator and divide by `ln(2) × positive count of those identical raw text bytes`; exclude structural protocol/stop tokens (EOT, EOS, BOS, PAD, SYS/USER/ASSIST) from **both** numerator and denominator. Report stop-target NLL/CE separately; no zero-byte imputation.
- **A frozen M0 v3 `a_gold_nll`** remains **nats for one full-vocabulary gold next-token**, not C bits/byte nor candidate-only renormalized score. NTP raw-text bpb and SFT assistant-only bpb are separate endpoints.
- For T4 BPE where token merges span source boundaries, **HOLD** until B proves exact tokenizer bytes and loss/byte attribution. Original T4 EOS is not BC/v2 assistant EOT.
- A ReleaseTBSV4 / CompletionEnvelopeV4 ASCII RAW/TAG domains, signed `policy_epoch`, global `H_SLOT_V3=581fd3acf137c28300813fc48501ff8ee243984588978ae64423fffc044bbe0f`, BC/v2 UTF-8/LF policy and 7-SHA manifest remain immutable.

**F03 status:** `C_CCR01_SEMANTIC_CROSS_ACK_DESIGN_SCOPED` · `PM_INTERPRETATION_ACCEPTED_DESIGN_ONLY` · `B_ACK_SCOPED` · **`A_MEASUREMENT_ACK_PENDING`** · `PM_FINAL_GATE_PENDING`.

Falsifiers: dropping assistant EOT/EOS from BC/v2 training CE, counting stop loss as genuine text-byte NLL, counting EOT/EOS as raw UTF-8 data bytes, conflating A single-token nats and C bits/byte, or silently using BC/v2 control IDs in original T4 embeddings.

## One integrated R0–R8 readiness and handoff

| Gate | C amendment | Remaining boundary |
|---|---|---|
| R0 | F01 new C file pointer corrected; A37/C26/B14 stable | independent PM exact readback and A/B dependent source re-ACK |
| R1 | F03 interpretation C cross-ACK | A measurement/domain ACK, new real gold HOLD |
| R2 | source/family/rights policies unchanged | actual rights/split/fresh heldout HOLD |
| R3 | direct codec collision **INCOMPATIBLE**; external role+byte-span design selected | actual checkpoint weight SHA, tokenizer/offset evidence/runner HOLD |
| R4 | no model/compute execution | host RAM/VRAM/FLOPs/hard cap HOLD |
| R5 | A V4 release/RAW/TAG/ledger unchanged | signed owner/native atomicity/TOCTOU HOLD |
| R6 | only conceptual endpoint clarification | prereg NOT_FROZEN |
| R7 | C author readback is not independent final QA | PM separate reviewer PENDING |
| R8 | HOLD_OWNER_RELEASE | no I2, science, TEST, GPU or merge |

**No A/B implementation, source binaries, training optimizer, checkpoint loading, GPU, TEST64/FRESH16/FINAL24, owner I2 action, prereg revision, Git main or lineage mutation.** Historical original C packet SHA `614caff...` remains addressable; new commit is additive and has one-property repair of its machine registry only.

**Single downstream sequence within same PM operation:** **Agent A** ACKs exact *new* C source and A one-token NLL vs C byte bpb (preserve I1 and V4); **Agent B** re-reads exact new A/C SHA and remaps 37/26/14 without code; **PM** independently readbacks source+bytes and issues exactly one `ABC_CONTRACT_ALIGNED_DESIGN_SCOPED` or `HOLD_ABC_CONTRACT_ALIGNMENT`. This is not micro-permit issuance.

**Bước thực hiện tiếp theo — duy nhất:** `TTM_PM_ABC_CCR01_SOURCE_REF_T4_CODEC_INTEGRATED_ALIGNMENT_AND_OWNER_READINESS_READJUDICATION_ONEPACK` (A ACK → B remap → PM adjudication).
