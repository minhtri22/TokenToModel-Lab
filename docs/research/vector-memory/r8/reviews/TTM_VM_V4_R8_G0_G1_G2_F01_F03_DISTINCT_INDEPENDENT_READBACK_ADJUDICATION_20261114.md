# TTM VM V4 R8 — Distinct independent G0/G1/G2 readback and one adjudication

**Date:** 2026-11-14  
**Role:** Distinct GPT-6 AI source/protocol reviewer; NOT the owner, NOT a human reviewer and NOT the authorized private custodian.  
**Operation:** `TTM_VM_V4_R8_G0_G1_G2_F01_F03_SINGLE_INTEGRATED_INDEPENDENT_READBACK_NO_GENERATION`  
**Mode:** GitHub source/log read-only verification; this file alone is an evidence write. No code modifications, new science input, R8 generation, blind rater chat, model run, tests, private access or GPU.

## 1. Pins and existing QA provenance

- Owner-supplied handoff commit: [`afcdda17d50d76a62ad7d15d6f3f0b88d6f50d9b`](https://github.com/minhtri22/TokenToModel-Lab/commit/afcdda17d50d76a62ad7d15d6f3f0b88d6f50d9b). This commit adds only its handoff; compare `1495c42...afcdda17` has no source/test changes.
- V4 prereg source: `b8410d9c1f77a733036e980b567de73c316f8725`.
- Initial source QA 29/29: `3a12aede5d738aa0a91d6a0d5f68869000efc097`.
- Earlier 37/37: [Actions `43573016701`](https://github.com/minhtri22/TokenToModel-Lab/actions/runs/43573016701), HEAD `cf38f8792253fe106cbb6a641f189882fb96e9d5`, job `scoped-nonr8-cpu` SUCCESS, Python 3.12.16, sklearn 1.8.0; **historical only; not carried over as 37/37 on corrected HEAD**.
- Correction source: [`1495c42f589b5150e0f941d662846b2dde6b3a31`](https://github.com/minhtri22/TokenToModel-Lab/commit/1495c42f589b5150e0f941d662846b2dde6b3a31).
- Targeted [Actions `43574946922`](https://github.com/minhtri22/TokenToModel-Lab/actions/runs/43574946922), HEAD exactly `1495c42...`, job `changed-contract-only` SUCCESS. Log proves 12 new focused tests + historical affected `test_08` and `test_10` = **14/14 PASS**. Separate checker, same implementation source class; not independent G0 or R8 QA. No re-run of 37.
- CI-reported SHA-256 (not independently recomputed): `gold_contract.py=17fc44ce356e6b8bf70bf350a0082774613b53a40261bf817d17cdbe98facef5`; `restricted_oracles.py=afde600811a27755dc7003f6eb317716def2446f8d746125e92826d8bded251f`; `test_integrated_source_only.py=e4402b825eba932c6ae5a0e3054a1cafe85d835c645be7d80df2a6b10c3f811f`; `test_g0_f01_f03_targeted.py=dd484860ef940225cb18c21cc68af654d6ca85d62b7f565c793f85f453956f7b`. Unchanged `folds_raters.py=7f2cfd23252a86354b91383351cea7ccede987c2daba80d6b6649f6bdcb9e853` (earlier CI log).

## 2. G0 independent source/protocol inspection

Source at exactly `1495c42f...`, under `docs/research/vector-memory/r8/integrated_closure/`:

1. **F01 corrected — PASS scoped:** `restricted_oracles._o1_features` lines 60–73 uses exactly `row_position_decile`, `card_count`, `first_card_position`, `last_card_position`; does not use key length, source ID or document contents. `_o2_features` lines 75–107 retains the metadata control. Tests `test_F01_O1_exact_order_only_allowlist`, `test_F01_key_metadata_cannot_change_order_only_result`, `test_F01_row_decile_remains_observable` inspect the repaired boundary. Source observation, not R8 leakage determination.
2. **F02 improved but NOT complete — HOLD:** `gold_contract._validate_claim_dependencies` lines 38–65 now raises `INVALID_FIXTURE_MISSING_PROOF_DEPENDENCY` and `INVALID_FIXTURE_CIRCULAR_PROOF`; `resolve` lines 98–111 rejects an equal-authority time-valid verified contradiction *only after* all six CORE predicates for the hypothesis are present. Specifically, lines 95–97 `continue` on a missing CORE predicate **before** lines 98–109 inspect verified contradictions. Hence a fixture with a missing `AUTHORIZED` and a verified, time-valid, equal-authority `DEFEATER` is returned as `ABSTAIN/MISSING_PREMISE`, not the V4-required `INVALID_FIXTURE_EQUAL_AUTHORITY_CONFLICT`. Existing focused `test_F02_equal_authority_conflict_rejected_not_abstained` and historical `test_08` use fully populated proofs; `test_F02_missing_authorization_remains_valid_abstention` has no equal-rank contradictory claim. The intersection is untested. This is a source-level counterexample, **not a newly executed test**.
3. **F03 markergram corrected but field vocabulary remains unrestricted — HOLD boundary:** `restricted_oracles._o3_features` lines 109–126 now restricts `markergram` 1/2-grams to lexemes in frozen `MARKERS`, addressing prior neighbor-token leakage; focused tests check `accession_x` and `proof_42` in card text and preserve `applicable signed` / `signed record`. However lines 114–117 still emit whole normalized values for `status`, `authority_role` and `source_format` into features, without a frozen categorical allowlist. For example, a synthetic case with `status="signed accession_x"` yields a `status=signed accession_x` feature even though `markergram` filtering rejects that accession token. The prereg defines O3 as marker/status-role/source-format *restricted* control; unvalidated free-text values can smuggle arbitrary identifiers. `validate_split` lines 137–165 checks no category vocabulary. Neither targeted F03 test exercises this field pathway. A source/schema constraint is required for claiming O3 is restricted. No R8 data were observed.
4. **B01/B03/B04/B05 scoped readback:** `gold_contract.receipt_f07` lines 144–170 retains the P-REC-V1 synthetic, authority-edge-dependent SELECT/ABSTAIN witness and one-key check in `resolve` lines 131–138; this is not owner policy adoption. `folds_raters.postcheck` lines 74–139 uses distinct `case_id`, two twins per blueprint, post-text G_post overlap/crossfold invalidation, no repartition; `preassign` lines 29–59 uses pre-blueprint graph and private HMAC key. `rater_allocation_source_qa` lines 147–162 is 64 cases / 128 ratings as a **proposal**, not real blind scoring. `restricted_oracles._o5` lines 213–260 trains only on TRAIN SELECT gold, never selects test keys from test gold; `aggregate_o5_folds` lines 263–301 checks duplicate case IDs and retains a descriptive 20/32 alarm; `holm_primary` lines 350–363 refuses inferential PASS absent defended group exchangeability. O2/O4/O6/O7/O8 remain non-R8 source controls. R8-D exploratory descriptive only; 32-pair confirmatory R8-C remains NO-GO. No blanket regression certificate is inferred for unaffected source.

**G0 result: `HOLD`** due to two substantive *source-level* boundary gaps described above (F02 partial and F03 field-value path). No new tests were performed. No claim that an actual R8 case leaked.

## 3. G1 attributable owner decision and rights

At handoff HEAD, `integrated_closure/OWNER_RIGHTS_CUSTODY_DECISION_PACKET_PENDING.json` remains `owner_attestation.scientific_scope=PENDING`, `rater_allocation=PENDING`, `p_rec_v1_toy_domain_policy=PENDING`, `rights_for_proposed_synthetic_source_class=NOT_ATTESTED`, `PII_handling_authorization=NOT_ATTESTED`, `signed_owner_record=NOT_SUPPLIED`. The separate `R8_V4_OWNER_SCOPE_AND_RATER_SELECTION_PENDING.json` is also expressly pending. No authenticated owner receipt covering all four dimensions was supplied in this review. The reviewer cannot sign for the owner.

**G1 result: `HOLD_OWNER_NOT_ATTESTED`.** Collecting an actual attributed owner decision is one existing requirement, not a new micro-permit.

## 4. G2 authorized private custodian readiness

The public packet records `custodian_private_storage_readback_plan.status=NOT_VERIFIED`, `private_material_read=NOT_EXECUTED`, `gold_access=NO`, `rater_allocation_secrets=NOT_CREATED`. No authorized private location/ACL/read-write-readback receipt for an approved **non-R8 sentinel**, SHA-256 proof, retention/HMAC/access rule or independent protected validator/source-lock attestation was supplied. CI code SHA-256 is not a custody receipt. No R8 gold SHA may be required before R8 exists, nor fabricated.

**G2 result: `HOLD_PRIVATE_CUSTODY_NOT_VERIFIED`.**

## 5. One integrated adjudication and consolidated closure set

**ONLY GLOBAL DECISION: `HOLD_INTEGRATED`.**

- G0: HOLD source/protocol (equal-rank contradiction under missing CORE, and unrestricted categorical values in O3).
- G1: HOLD (single authenticated owner decision for R8-D vs R8-C, rater option, P-REC-V1/one-key, scoped synthetic rights/PII/provenance absent).
- G2: HOLD (real authorized non-R8 sentinel private custody/readback, ACL/access/retention/HMAC source-lock/validator attestations absent).
- Immutable states: `R7=FROZEN_FAIL`, `R8=NOT_GENERATED`, `G3/G4=NOT_EXECUTED` (G3 not authorized), `G5/G6=SEALED`, `Reader=0`, `GPU=NO`, `PROBE256=SEALED`.

This one report closes the requested readback; it grants **no** candidate authoring, science release, generation, blind-rater restart, TEST, reader, GPU, or PROBE256. No V5/V6 or micro-permit chain is opened. Evidence set is self-contained and public-safe; any future single integrated owner/custodian closure must resolve these exact conditions under the locked prereg before a fresh decision.
