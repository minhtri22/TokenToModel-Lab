# HANDOFF — TTM VM V4 R8: G0–G2 Integrated Remediation / Independent Readback (One Gate)

**Operation:** `TTM_VM_V4_R8_G0_G1_G2_INTEGRATED_REMEDIATION_AND_INDEPENDENT_READBACK_SINGLE_GATE`  
**Ngày:** 2026-11-14  
**Source of truth:** `minhtri22/TokenToModel-Lab` · GitHub  
**Trạng thái đầu vào:** `HOLD_INTEGRATED`; R7 `FROZEN_FAIL`, R8 `NOT_GENERATED`, G3/G4 `NOT_EXECUTED`, G5/G6 `SEALED`, Reader 0, GPU NO, PROBE256 SEALED.  
**Execution scope of this handoff:** Independent SOURCE/PROTOCOL readback at G0 + authenticated owner decisions at G1 + authorized private custodian readiness check at G2. **No R8 generation, blind packet, Test, PROBE, Reader or GPU.**

## 1. Frozen references: no source QA rerun unless real drift
- V4 scientific design: `b8410d9c1f77a733036e980b567de73c316f8725`.
- Original integrated source evidence/report: `3a12aede5d738aa0a91d6a0d5f68869000efc097`; QA `29/29 PASS`, CI run [43570722316](https://github.com/minhtri22/TokenToModel-Lab/actions/runs/43570722316). Original evidence preserved; never overwrite its history.
- Independent AI G0 review supplied by owner: `HOLD`, finding (a) G_post cache fingerprint by `blueprint_id` despite two twins/cases; (b) O1 missing public row decile, O2 had constant position sum, O5 20/32 alert unreachable inside a single held-out fold. This is **AI independent SOURCE review**, not human review or an observed R8 failure.
- **One-shot source remediation commit:** `cf38f8792253fe106cbb6a641f189882fb96e9d5` on `evidence/ttm-vm-v4-r8-v4-integrated-closure-20261114`.
- **GitHub Actions remediation run:** [43573016701](https://github.com/minhtri22/TokenToModel-Lab/actions/runs/43573016701), job `scoped-nonr8-cpu`, `SUCCESS` at the **same source remediation SHA**, `Ran 37 tests ... OK`. Python 3.12.16, scikit-learn 1.8.0, NumPy 2.3.5, SciPy 1.17.0; Ubuntu runner; **Windows QA not executed**. 29 original symbolic tests + 8 G0 negative regression tests, all **non-R8 synthetic fixture** only. QA classification `SAME_AGENT_SEPARATE_CHECKER`, **NOT** an independent G0 readback.
- Exact source SHA-256 reported by remediation CI:
  - `gold_contract.py`: `a359758b97f6426629cc30293e74882f27a65ca13b887f65bd5ae7ab2cdaadde` (unchanged).
  - `folds_raters.py`: `7f2cfd23252a86354b91383351cea7ccede987c2daba80d6b6649f6bdcb9e853`.
  - `restricted_oracles.py`: `4fc20ef92d02e22a4bf33edad6da40d1bb2c13df25ea37e87229038bc060c5e9`.
  - `test_integrated_source_only.py`: `7db6c1e513d0d0ee8790d17dea9dbfad6df6aa0688a7f15828b15207aac90012`.
  - `restricted_oracles.PATTERN`: `ffdfc06eb76bebd35e1f6185fafd4525d244149d7f64838bbe1f688ddf406d2e`.

**This handoff is the only new public-facing evidence packet after source remediation.** Do not create extra empty PASS receipts or re-run full QA when byte SHA remains locked. If re-testing is needed after detecting an actual source flaw, document scope and test only that flaw; do not alter source and call same-agent result independent.

## 2. What was actually fixed in the one code batch (source inspection mandatory)
Read `docs/research/vector-memory/r8/integrated_closure/` at commit `cf38f8792253fe106cbb6a641f189882fb96e9d5`:
- **B03 `folds_raters.postcheck`:** G_post graph nodes indexed by unique `case_id`; map each case to its parent `blueprint_id` and locked pre-fold. Require two twin cases per blueprint for normal use, reject duplicate `case_id` and missing twins, connect twins within one component; similarity fingerprints keyed by **case**, not blueprint. Recompute cross-fold edges from actual case-pair signatures, duplicate cards and word-5-gram Jaccard >=0.80; never reallocate pre-folds. In synthetic one-twin fixture tests, explicit `expected_twins_per_blueprint=1` is mandatory and is NOT the production configuration. Test G0 regressions: `test_30`–`test_33` (first twin vs later twin, missing twin, duplicate case ID). The independent reviewer must check both logic and tests: a PASS test alone does not prove full V4 CAL correctness.
- **B04 O1:** `_o1_features` derives `row_position_decile` from **explicit public `public_row_position` and `public_case_count`**; absent/invalid ordering is rejected, not replaced by TRAIN/test list index. This public ordering must be frozen in source/generator at G2.
- **B04 O2:** remove always-constant sum of card positions; add first/last key/source lengths, quartile-by-source markers and rank-weighted metadata lengths. `test_34`–`test_35` verify visible ordering/feature sensitivity. No class-label features.
- **B04 O5:** per-fold warning on any non-empty held-out SELECT fold using the **prospective descriptive** >=20/32 raw key-accuracy trigger, plus `aggregate_o5_folds` that verifies disjoint held-out case identities and aggregates the entire predeclared SELECT set (32 cases), refuses double-counting and reports incomplete coverage as `OOF_PARTIAL_NOT_ESTIMABLE`. The raw alarm is **NOT a statistical p-value or proof of forbidden leakage**; valid inferential testing remains subject to component-blocked exchangeability and Holm O2/O3/O4/O5/O6 at FWER 0.05. `test_36`–`test_37` cover full 20/32 warning, partial fold and duplicate accounting.

**Potential further independent-review questions, do not conceal:** Whether the public row position representation is actually present in the eventual R8 public-order schema; whether exact source/graph IDs are consistently linked across 32 pre-blueprints and 64 generated cases; whether the raw O5 key alarm is adequate as a diagnostic; whether future G2 validators enforce total 32 pair blueprints and 64 cases beyond the source-only fixture. If any blocker is material, report HOLD with precise code evidence. Do not extend scope into a design V5/V6 cycle automatically.

## 3. G0 — NEW independent reviewer, not the source-fixing agent
At the remediation commit, inspect exact code, fixed V4 contract and eight new negative tests; compare the independent G0 findings and source patch semantically, not merely by string grep. Review B01/F07 existing gold_contract.py, B03 postcheck/preassign/rater no-twin overlap, B04 O1/O2/O5 plus O3/O4/O6/O7/O8 scope, B05 descriptive inference. Verify CI source SHA/runner provenance, but classify its 37/37 as same-agent QA.
**G0 can PASS** only if the fixed source/contract is complete for the requested **source/design-only scope** and no unresolved material contract inconsistency remains. Mark `G0=PASS_INDEPENDENT_SOURCE_AND_PROTOCOL_SCOPED` or `G0=HOLD`, cite exact source paths/functions plus reviewer identity/type. A new AI session is independent of the implementation session in process, but not a human or proof of science. No R8 actual data exists.

## 4. G1 — authenticated owner choice/rights, not reviewer consent
Only owner can attest in one bundled record:
1. **Scope**: `ADOPT_R8_D_DESCRIPTIVE_ONLY` or `RETAIN_CONFIRMATORY_OBJECTIVE_NO_GO` (the existing 32-pair design cannot claim absence of shortcuts).
2. **Raters**: `FOUR_RATERS_TWO_PER_CASE` (32 cases each, 128 ratings total, none sees both twins) or `TWO_RATERS_DISJOINT`; only relevant if R8-D is approved.
3. **Domain/scorer**: approve/reject toy-domain `P-REC-V1` and one-key target/ABSTAIN semantics.
4. **Source rights/PII**: approve/reject `AI_AUTHORED_SYNTHETIC_EXPLORATORY_ONLY` provenance/rights and PII rules for candidate authoring, identifying actual authority, scope and date.

Input baseline `integrated_closure/OWNER_RIGHTS_CUSTODY_DECISION_PACKET_PENDING.json` at original integrated commit. No approval currently supplied in that packet. A reviewer or AI agent must NOT fill `OWNER_APPROVED` based on recommendation. If absent, `G1=HOLD_NOT_ATTESTED`. Consolidate all four choices as **one owner decision**, no micro-permits.

## 5. G2 — independent authorized private-custodian readiness, not imaginary R8 gold
Custodian must verify actual **private preflight** location and ACL/access control, read/write/readback of an allowed **non-R8 sentinel** (or approved existing fixture), record canonical SHA-256, key/retention/access policy, future R8 proof+gold storage and secret HMAC allocation custody, and exact validator/source-lock runtime matching the remediation SHA manifest. Readback must come from an authorized real endpoint; a text-only assertion is insufficient. Private path, ACL detail, key values, allocation IDs and gold are **NOT** to be published to public GitHub; public receipt may expose PASS/HOLD and nonsensitive hashes.
**Critically: R8 NOT GENERATED. G2 cannot and need not attest actual R8 gold bytes.** Once future G3 generation is authorized, candidate/private-gold/release-byte readback is a separate *post-generation* requirement before G4/G5. If private custody cannot be reached or authorization missing, `G2=HOLD_CUSTODY_NOT_VERIFIED`. No additional private source generated as a workaround.

## 6. Exactly one decision after all evidence
Return **one** combined decision to owner:
- `GO_R8_D_CANDIDATE_AUTHORING_ONLY`: **only** G0 independent design/source PASS, G1 authentic owner scope/rater/domain/rights/PII PASS, G2 verified private preflight/storage source-lock PASS. GO allows a **future separate one-shot exploratory candidate authoring**, never automatic R8 generation, gold/threshold/CAL release or PROBE256.
- `HOLD_INTEGRATED`: any G0/G1/G2 not evidenced, unresolved substantive defect, or owner selects R8-C. State a single consolidated blocker set, no micro-permit or V5/V6 proliferation.
- Always preserve `R7=FROZEN_FAIL`, `R8=NOT_GENERATED`, `G3/G4=NOT_EXECUTED`, `G5/G6=SEALED`, `READER=0`, `GPU=NO`, `PROBE256=SEALED`.

**Final artifact:** produce ONE public-safe integrated readback/adjudication report with a real commit and blob SHA after independent reviewer + owner + custodian evidence if accessible; if evidence missing, report HOLD honestly instead of posting extra placeholders. Do not overwrite original scientific V4 or historical CI receipts. Do not create new blind rater chats or unseal packets. If GitHub write unavailable, return source-grounded verdict and explicit persistence limitation.

**Next human/agent action:** Assign this handoff to a **different AI/source reviewer** for G0 and request the owner/custodian decisions in the **same integrated evidence packet**. Implementation patch and 37/37 CI are already complete; no new coding task unless a genuine independent defect is substantiated.
