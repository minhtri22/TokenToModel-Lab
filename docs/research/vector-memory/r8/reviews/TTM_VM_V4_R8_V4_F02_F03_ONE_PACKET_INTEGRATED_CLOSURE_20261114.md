# TTM VM V4 R8 — F02/F03 Integrated Closure · One Public-Safe Evidence Packet

**Date:** 2026-11-14  
**Operation:** `TTM_VM_V4_R8_F02_F03_G0_G1_G2_ONE_PACKET_SOURCE_CLOSURE`  
**Repository:** `minhtri22/TokenToModel-Lab`  
**Branch:** `evidence/ttm-vm-v4-r8-g0-f01-f03-single-closure-20261114`  
**Role:** AI implementation/source-QA agent for this patch, **not** a distinct independent checker, actual owner, or authorized private custodian.  
**Scope:** Focused V4 source+contract changes, focused CI, one public-safe consolidated evidence readback. No R8 data, blind rater, TEST, Reader/GPU/PROBE256, or private sentinel execution.

## 1. Source-of-truth immutable references

- Frozen V4 design reference: `b8410d9c1f77a733036e980b567de73c316f8725` (historical scientific draft; unchanged).
- Previously successful non-R8 37/37 historical QA: [`43573016701`](https://github.com/minhtri22/TokenToModel-Lab/actions/runs/43573016701), head `cf38f8792253fe106cbb6a641f189882fb96e9d5`, not rerun and **not** claimed as 37/37 on the latest source.
- Previous independent-review evidence commit: [`21724303b68e08ab3dcc8cb7dd59feea444f8a1e`](https://github.com/minhtri22/TokenToModel-Lab/commit/21724303b68e08ab3dcc8cb7dd59feea444f8a1e), `HOLD_INTEGRATED` for F02, F03, G1, G2.
- **This focused source correction:** [`b77bc04a511fa9d98ba70314df84c62a3af0500b`](https://github.com/minhtri22/TokenToModel-Lab/commit/b77bc04a511fa9d98ba70314df84c62a3af0500b); parent `21724303...`. Comparison shows **exactly four files** changed: `gold_contract.py`, `restricted_oracles.py`, `test_g0_f01_f03_targeted.py`, `R8_V4_RESTRICTED_ORACLE_AND_RATER_CONTRACT_DESIGN_ONLY.json`. No new version/phase, no change to the frozen V4 draft.

## 2. Focused F02/F03 source closure

**F02 (source patch complete; independent ratification outstanding).** In `integrated_closure/gold_contract.py` `resolve()`, equal-authority/time-valid verified contradiction is now checked **before** missing CORE prerequisites can trigger ordinary `ABSTAIN/MISSING_PREMISE`. Existing claim dependency graph validation for missing references and cycles is preserved. The two new negative witnesses cover `DEFEATER` and `NEGATIVE_RECEIPT` at equal rank with missing `AUTHORIZED`. A superior negative receipt with missing `AUTHORIZED` stays ABSTAIN. Thus invalid-fixture vs valid-abstention branch separation is explicitly covered, but **not independently audited by a distinct reviewer**.

**F03 (source patch complete; independent ratification outstanding).** `integrated_closure/restricted_oracles.py` declares `O3_CATEGORICAL_ENUMS` with closed sets for `status`, `authority_role` and `source_format`; `_o3_category` rejects values outside the corresponding set, `_o3_features` validates fields before building marker features, and `validate_split` rejects unregistered values **before model fitting**. Allowed values are now enumerated in `R8_V4_RESTRICTED_ORACLE_AND_RATER_CONTRACT_DESIGN_ONLY.json` under O3. Existing marker-only ngram filtering remains. Negative witnesses try identifier-bearing values in all three categorical fields; valid status/authority/format values remain observable. The enum is a bounded V4 source-contract clarification, **not** retroactive owner approval or permission to author R8 cases.

**F01:** O1 order-only fix from `1495c42...` remains unchanged. **B03/B04/B05:** fold/rater code, TRAIN-only O5 and descriptive-only R8-D boundaries unchanged by this patch.

## 3. Actual targeted CI and SHA-256 readback

- [GitHub Actions run `43577175641`](https://github.com/minhtri22/TokenToModel-Lab/actions/runs/43577175641): `completed/success`, exact `head_sha=b77bc04a511fa9d98ba70314df84c62a3af0500b`, job `changed-contract-only` SUCCESS, Python 3.12.16.
- **18/18** current targeted F01/F02/F03 tests PASS (previously 12 + 6 new) and **2/2** selectively retained affected historical assertions (`test_08`, `test_10`) PASS. **20/20 focused source QA PASS**; **historical 37/37 NOT rerun**. This is same-implementation-agent source QA, *not* independent G0 certification and not R8 scientific execution.
- CI-reported SHA-256 (not separately recalculated by reviewer):
  - `gold_contract.py`: `e1cdb9973c23d35ad99eebd32a3f38e681bdae5e17132e27319672593b785fb6`
  - `restricted_oracles.py`: `c9b08238703088e60c7873f951814e579518d0bee183e2ceb85a681ca7b1b4d3`
  - `test_g0_f01_f03_targeted.py`: `9a8c6da952f722d128c573ab578cb30e830c72aebbbcf16d153ac739434803af`
  - Unchanged `test_integrated_source_only.py`: `e4402b825eba932c6ae5a0e3054a1cafe85d835c645be7d80df2a6b10c3f811f`
- The exact public source SHAs are **not** an independently protected G2 source-lock/validator attestation.

## 4. G0/G1/G2 consolidated evidence readback

| Gate | Observed state | Missing condition |
|---|---|---|
| G0-F02 | `PATCHED_TARGETED_QA_PASS` | Distinct independent source/protocol readback of corrected SHA and semantic boundary |
| G0-F03 | `PATCHED_TARGETED_QA_PASS` | Distinct independent readback of frozen enum, preflight, marker-only/metadata boundary |
| G0 overall | `HOLD_DISTINCT_INDEPENDENT_REVIEW_REQUIRED` | One external-to-implementation source review; no independent PASS is implied |
| G1 | `HOLD_OWNER_NOT_ATTESTED` | One attributable owner decision: R8-D vs R8-C, exact rater allocation, P-REC-V1 & one-key SELECT/ABSTAIN, synthetic-source rights and PII/privacy/provenance/version/scope/date |
| G2 | `HOLD_PRIVATE_CUSTODY_NOT_VERIFIED` | Actual authorized custodian private storage/ACL/access/retention/HMAC, non-R8 sentinel write/readback SHA-256, protected exact-source/validator runtime lock |
| R8 science | `NOT_GENERATED` | No source/candidate generation permit |

The existing public `integrated_closure/OWNER_RIGHTS_CUSTODY_DECISION_PACKET_PENDING.json` remains `owner_attestation.scientific_scope=PENDING`, `rater_allocation=PENDING`, `p_rec_v1_toy_domain_policy=PENDING`, rights and PII `NOT_ATTESTED`, `signed_owner_record=NOT_SUPPLIED`; custodian `NOT_VERIFIED`, `private_material_read=NOT_EXECUTED`, `gold_access=NO`. No authentic signed decision was supplied or fabricated by this agent. No private endpoint, ACL or sentinel was accessed; do not publish location, HMAC, proof/gold, or secret values. No nonexistent R8 gold hash is demanded at this pre-generation gate.

## 5. Single decision and closure boundary

**ONE GLOBAL VERDICT: `HOLD_INTEGRATED`.**

Source F02/F03 remediation is now implemented and narrowly CI-verified, but **G0 independent ratification and real G1/G2 receipts are not complete**. No `GO_R8_D_CANDIDATE_AUTHORING_ONLY`, candidate generation, science release, rerun of 37 historical tests, new blind sessions, V5/V6 or micro-permit chain.

**Preserved:** `R7=FROZEN_FAIL`, `R8=NOT_GENERATED`, `G3/G4=NOT_EXECUTED` (G3 not authorized), `G5/G6=SEALED`, `Reader=0`, `GPU=NO`, `PROBE256=SEALED`.

**Single remaining integrated action:** collect the authentic G1 owner decision and actual authorized G2 custodian preflight, then obtain one distinct independent G0 source readback of the fixed V4 SHA in the same evidence bundle. Keep HOLD until all three are proven; no smaller separate permit stages.
