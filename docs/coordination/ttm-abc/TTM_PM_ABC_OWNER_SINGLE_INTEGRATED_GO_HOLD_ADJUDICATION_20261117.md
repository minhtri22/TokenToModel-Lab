# TTM ABC — PM final integrated GO/HOLD adjudication: A-I2 · real SFT · scoped merge

**Operation:** `TTM_PM_ABC_OWNER_SINGLE_INTEGRATED_RELEASE_AND_MERGE_DECISION_PACKET_ADJUDICATION_GATE`  
**Adjudication:** 2026-11-17 · **Method:** exact-commit GitHub readback; no code execution, new tests, model load, science, GPU, merge, permission issuance.  
**Source of truth:** `minhtri22/TokenToModel-Lab`. Exact snapshot main `f7a0a5874e8fd895c8ea8d17ceff393a4d4917a3`.  
**PM authority:** independent AI PM evaluation on existing evidence; **not an owner-originated release signature** and not an independent authenticated human review.

## 1. One final decision, three independently scoped outcomes

| Choice | PM verdict today | Why NOT GO |
|---|---|---|
| **A-I2/Q001 one-shot** | **`HOLD_A_I2_RELEASE`** | M0 v3 I1 metric scoped PASS does not satisfy old owner-internal release preflight (exit **2**, `HOLD_OWNER_INTERNAL_I1_NOT_PASS`), trusted signer/epoch/principal and native atomic/ledger/race witnesses unproved; original global H_SLOT frozen; real I2 candidate/source/checkpoint/resource binding/independent QA not supplied |
| **Real SFT / T4 science** | **`HOLD_REAL_SFT_RELEASE`** | No independently verified real checkpoint, licensed corpus+split/gold, byte-offset scorer, exact real runner/memory/GPU evidence; historical T4 BPE IDs257–2047 directly conflict with B/C v2 role IDs257–262, external byte-span sidecar still DESIGN_ONLY; future prereg/real candidate QA absent |
| **Merge, including docs-only** | **`HOLD_ALL_PR_MERGES_THIS_REVIEW`** | All six PRs remain Draft/open/unmerged; stacked parent dependency; exact combined-tree CI and independently accepted merge-specific candidate absent; no owner explicit merge authorization. Docs/test PASS can be a future clean-scope merge *candidate*, not a present GO |

**Final machine decision:** `TTM_PM_FINAL_TRIPLE_SCOPE_HOLD_EVIDENCE_BASED` with `ABC_CONTRACT_ALIGNED_DESIGN_SCOPED` preserved. None of the three choices receives GO, dispatch, branch change, owner credential or merged SHA.

**Do not interpret HOLD as scientific failure**; it denotes insufficient evidence *in the present scope*. No requirement to rerun historical A-I1, B-M3, C-M4, BC-v2 or ABC F01–F03 scoped PASS solely to satisfy this adjudication. Histories of failed QA and reviewer dissent remain intact.

## 2. Exact material personally reopened for this decision

- [Owner prospective release and merge OnePack](https://github.com/minhtri22/TokenToModel-Lab/blob/f810ead7f99bc8a8710f8d9ba5bc9a5baf59de74/docs/coordination/ttm-abc/TTM_PM_ABC_OWNER_PROSPECTIVE_RELEASE_AND_MERGE_READINESS_ONEPACK_20261117.md), Git blob `52f60856801772e8067631ad6e804298a1e78d67`.
- [Owner per-lane R0–R8 matrix](https://github.com/minhtri22/TokenToModel-Lab/blob/f810ead7f99bc8a8710f8d9ba5bc9a5baf59de74/artifacts/ttm-abc/governance/TTM_PM_ABC_OWNER_READINESS_R0_R8_AND_MERGE_INVENTORY_20261117.json), Git blob `62ced477a334658aa5db8263aff462ccdbbbb77d`.
- [Distinct source readback accepting ABC F01–F03 design alignment](https://github.com/minhtri22/TokenToModel-Lab/blob/fa28b89e4ee93b3de4561deaa2a7b9a086fa340b/artifacts/ttm-abc/governance/TTM_PM_ABC_CCR01_FINAL_INDEPENDENT_SOURCE_ALIGNMENT_RECEIPT_20261117.json), Git blob `7ec9018eac0b28e0220d26e71ef2ce028f6fea8e`; `ABC_CONTRACT_ALIGNED_DESIGN_SCOPED`, no release.
- PM charter at `403491b698ba6586193f2ff2ae00c4441c10c595`, Git blob `d7fbc02a45b1d1a85cfe9b9594ae88fee495a9e1`.
- Repo `main`, exact PR metadata and relevant GitHub Actions queried afresh; branch-protection endpoint gave 403 `Resource not accessible by integration`. Repository rulesets endpoint returned an empty list; this **does not** prove all branch protections are absent. **No final combined-tree QA was observed**.

### PR base and exact heads at decision

| PR | Exact HEAD | Base | Draft | Scope |
|---|---|---|---|---|
| [#28](https://github.com/minhtri22/TokenToModel-Lab/pull/28) | `ebdc54575eed1ff60c402eecf60289f408bb38ca` | main | YES | historical Q001 parent/preexec owner/native HOLD |
| [#33](https://github.com/minhtri22/TokenToModel-Lab/pull/33) | `7639a53b9d76e16abfa4211cf239c5c3e9d6c940` | PR28 head `ebdc...` | YES | A I1 metric PASS + V4 design |
| [#34](https://github.com/minhtri22/TokenToModel-Lab/pull/34) | `43896bcd034c82e8433bc6a2b53eefbd936616fb` | main | YES | B synthetic M3 scoped engineering PASS / V3 dissent |
| [#36](https://github.com/minhtri22/TokenToModel-Lab/pull/36) | `09de6a46574146d863f416e056fcf01091f3efb8` | PR34 head `43896...` | YES | BC v2 synthetic bridge F05/F06 engineering PASS |
| [#37](https://github.com/minhtri22/TokenToModel-Lab/pull/37) | `ff4304e04f44de69a07cd767b2a7f400d6e95e88` | PR36 head `09de...` | YES | B 37/26/14 design mapping, B14 subset |
| [#35](https://github.com/minhtri22/TokenToModel-Lab/pull/35) | `4efe93ce0a3910c449972b3f7e9911a004fe2b3c` | main | YES | C source and design review, not real science |

GitHub reported `mergeable=true` for PRs relative to each **own** base. This is not approval of an alternate merge order or combined main. CI workflows *associated with final PR-head commits* were found completed/successful for #33 (run `44012028313`), #34 (`43894701733`), #35 (`44016759857`), and #36 (`43929586272` and `43929586267`). The connector returned **no PR-triggered workflow runs at PR37 final HEAD**. These runs cover branch-specific existing tests, **not** a staged merged tree. No need to invalidate earlier CI merely because integration evidence is missing.

### Merge boundary interpretation

- **A**: #28 → #33 contains a historical parent with unresolved owner/native release status; although #33 correctly closes I1 in its own scope, do not merge an entire HOLD parent into main without a separate *scoped merge candidate* proving what code/evidence is accepted. Historical path overlap in this stack is two source paths; no cherry-pick by guess.
- **B**: #34 → #36 → #37 is a stacked Git dependency, not three independently mergeable artifacts into `main`. Prior B-M3 reviewer disagreement on denied allocation peak counter is still recorded; any future combined integration candidate needs an exact Git tree/CI and owner's scope.
- **C**: #35 is main-based and may be reviewed for a **standalone design/test/doc merge** without waiting for real SFT science, but it includes CI/tests/config, not just documentation; cannot claim docs-only as the complete PR. No merged-tree candidate or owner sign-off in this review.
- Candidate classification is not a GO; there are **zero approved merge sets** today. A separately documented clean-scoped extraction may be contemplated later *if requested*, but none was created, tested or approved in this gate.

## 3. One combined R0–R8 decision matrix (not nine gates/permits)

| Gate | A-I2 evidence status | Real SFT evidence status | Decision effect |
|---|---|---|---|
| R0 exact executable and dependencies | I1 source pinned; I2 candidate/PR28 parent/release decision not reconciled | Design contract pinned; exact weight-bearing real runner missing | HARD HOLD on run source |
| R1 valid measurement/truth | I1 independent scorer+80 fixtures PASS scoped; real Q001 I2 inference NOT_EXECUTED | bpb/stop CE defined, but real source/gold/rater/offset not validated | HOLD prospective output interpretation |
| R2 source rights and fresh heldout | Existing Q001 rights/test boundaries must bind same source | Real source/rights/family-disjoint splits/TEST isolation absent | HOLD, not rights-invalid finding |
| R3 real checkpoint/codec | Q001 I2 checkpoint/config/tokenizer runtime hash and strict binding not verified in this gate | Actual T4 trained weights unverified; direct T4 ↔ BC-v2 ID `INCOMPATIBLE`, sidecar not implemented; `HOLD_BYTE_DENOM` | HARD HOLD |
| R4 resources | exact owner Windows Job Objects, watchdog, process tree, disk/time/peak on I2 candidate not QA'd | real T4 VRAM/RAM/full-step throughput/FLOPs/abort not measured; 74 s/13 min extrapolation not certified | HOLD |
| R5 owner signature/atomic custody | Historical release preflight **exit 2**; V4 65 neg+3 pos designed, not run; trusted signing keys, ancestor handle races/no-replace/crash/global slot ledger not proven | real SFT READY-last and path/receipt atomicity not proven; do not transplant Q001 I2 signing schema blindly | HARD HOLD |
| R6 frozen prereg/equal budget | original Q001 one-shot/frozen TEST scope must not be rekeyed or modified | real study arms/primary bpb/gold/independent family holdout and equal **measured** FLOPs not frozen | HOLD |
| R7 independent exact runtime QA | I1 distinct 35/35 and native custody 38/38 PASS; V4 65/3 runtime tests **0 executed** | BC synthetic QA PASS, new real candidate QA NOT_EXECUTED | HOLD |
| R8 owner decision | no valid scoped signed GO for Q001 I2 | no valid scoped GO for real SFT | **HOLD_OWNER_GO_NOT_GRANTED** |

**R0 design-source alignment may be PASS while runtime source gate remains HOLD.** Likewise C rights/gold data missing in connected GitHub review is `OWNER_PRIVATE_CUSTODY_UNVERIFIED`, not a conclusive finding of invalid rights.

## 4. Explicit evidence-bound conditions for changing each decision later (ONE packet, not micro-permits)

**A-I2:** Submit one immutable `A_I2_EXACT_RELEASE_WITNESS_PACKET` with exact runnable/parent source/config/checkpoint/tokenizer/rights/source+Q001 prereg binds; signed trusted V4 epoch/roles/global unchanged H_SLOT_V3 and repaired non-bypass release guard; native Windows no-replace, race/crash/ledger/antirollback and native resource evidence; distinct negative/positive QA; one owner GO matching exact single Q001 one-shot slot and bounded action. Do **not** change frozen fixture, replay TEST or mint another one-shot identity.

**Real SFT:** Submit one immutable `C_B_REAL_SFT_SCIENCE_WITNESS_PACKET` with real source/rights/family TRAIN/VAL/fresh TEST, trained checkpoint/weights/config/optimizer/tokenizer bytes/SHA and safe strict load, explicitly versioned solution to T4/BC codec conflict, exact UTF-8 byte alignment/CE/stop controls, verified gold and frozen prereg/equal measured compute, bounded resource and atomic checkpoint/receipt, distinct real-candidate QA and exact owner GO. B/C synthetic bridge metadata `weights=NOT_CREATED` is not real SFT weights.

**Merge:** Submit one `SCOPED_MERGE_CANDIDATE_PACKET` describing exactly which code/docs/tests are allowed, exact source and prospective merged Git tree/parent order, CI/test/security checks on **that combined tree**, branch-policy/owner approval, lineage append candidate preserving failing/HOLD history. This can be reviewed **without science GO** if only design/docs/engineering scope is sought. Do not merge parent #28 HOLD by proxy of #33 I1 PASS. No automatic clean extraction performed.

These are three *possible follow-on evidence bundles*, **not** three permissions to conduct experiments now, not task tickets for every R-number, and not demands to re-run previously accepted scoped gates. Missing evidence may exist privately; it was not established in the current GitHub materials.

## 5. Single integrated PM conclusion and closure

**`TTM_PM_FINAL_TRIPLE_SCOPE_HOLD_EVIDENCE_BASED`**:
- `A_I2=HOLD_A_I2_RELEASE`
- `REAL_SFT=HOLD_REAL_SFT_RELEASE`
- `MERGE=HOLD_ALL_PR_MERGES_THIS_REVIEW`
- `OWNER_GO=NOT_GRANTED`
- `MAIN/LINEAGE/PR_BRANCHES=UNMODIFIED`

**Maintained PASS results:** `A_I1_CLOSED_PASS_SCOPED · A_V4_DESIGN_ACCEPTED · B_M3_PASS_ENGINEERING_WITH_V3_DISSENT · C_M4_PASS_DESIGN · BC_V2_PASS_ENGINEERING · ABC_CONTRACT_ALIGNED_DESIGN_SCOPED`.

**No further sequential permission chain launched.** This PM decision is complete for the evidence currently available. The only future continuation, if new actual evidence or owner-approved scope is supplied, is **one integrated owner re-adjudication**, not A/B/C gate reopening by default. Maintain historical FAIL/HOLD and append lineage only after owner authorizes the exact merge/edit scope. GitHub remains source of truth.

**Scope limits:** GitHub actions/config metadata are read-only observations. `branch-protection` endpoint is 403 with current integration, `rulesets` endpoint shows empty result; neither proves absence of protection. No cloud/Windows/native inspection, no actual model load, no runtime testing, no new approval signature was performed in this PM review.
