# TTM Vector Memory V4 R8 — Final Independent B03 G0 & G2 Protected Rebind Adjudication

**Operation:** `TTM_VM_V4_R8_B03_FINAL_DISTINCT_REVIEW_AND_G2_PROTECTED_SOURCE_REBIND_SINGLE_GATE`
**Review date:** 2026-11-14 (Asia/Bangkok)
**Evidence classification:** `INDEPENDENT_AI_SOURCE_REVIEW_WITH_NEW_CPU_NEGATIVE_PROBES`
**Repository:** `minhtri22/TokenToModel-Lab`
**Evidence branch:** `evidence/ttm-vm-v4-r8-g0-f01-f03-single-closure-20261114`
**Final single adjudication:** **`HOLD_INTEGRATED`**

## 1. Exact sources and provenance

- Locked implementation commit: **`5a51e1e6ca0938b0f77d1db553da45cd294a97c3`**. Review used this immutable object and the evidence branch containing the same source.
- Incoming implementation report: **`bc3c5e5844021123f863d8e643e9a8890bc421d3`**. Its source tests are implementation-agent QA, independently distinguished from the probes below.
- Prior independent report: **`12540962e96caef34c587e7a8ba59d58fd09c5c4`**. Retain its F01 minimal-proof and F02/F07 event-scoping `PASS_SCOPED` findings. This B03-only review found no source change to reopen them.
- Frozen V4 scientific contract: **`b8410d9c1f77a733036e980b567de73c316f8725`**, B03 two-stage graph and protected pre-G3 HMAC assignment.
- Owner standing research direction: **`097e046bb0f6525665dde03ec5fcdf8134a8e762`**, directly read from the exact Git commit.
- GitHub Actions [run 43602350914](https://github.com/minhtri22/TokenToModel-Lab/actions/runs/43602350914) verified as `completed/success`, exact `headSha=5a51e1e6...`. Log confirms **15 tests, OK**. Historical 37/37, 25/25 and pre-B03 15/15 suites were left at their original commits.

Independent SHA-256 readback was performed both on the exact Git source object's UTF-8 content and with `Get-FileHash -Algorithm SHA256` on the checked-out evidence worktree.

| File under `docs/research/vector-memory/r8/integrated_closure/` | Verified SHA-256 |
|---|---|
| `folds_raters.py` | `a9fbf9dd81994822ced7dabc50b7fedc2f5fc608ed1f6da9ec9aadfb22eb7edb` |
| `r8_production_caller.py` | `3a9b249bced1b4ceaa5746d63367c017410ef82ded21ef386c3be2b1ee76b206` |
| `test_g0_b03_production_negative.py` | `8c7cce710964455db2a1ca66904d74050b2a84f6c8f2a1998534719d4954aeb6` |
| `test_g0_final_three_findings.py` | `750d90cf069b31418bdc852d9aa276295b06162ef454629835b5086aa872a4a2` |
| `gold_contract.py` | `8e8b81ce2d0bc47cc60c29abc7156fe9d97613e67983e43b7f587615d68015a5` |
| `restricted_oracles.py` | `34ab74d36b822703e4d8cbdf281e142273d55d181243d904b55fd31a0e6382a1` |

These are source-worktree hashes and **do not attest bytes running inside an authorized protected private runtime**.

## 2. Independent G0 findings

### B03-A — closed relation family enum: PASS_SCOPED

`validate_r8_blueprint_manifest()` requires exactly 32 distinct blueprint IDs, exactly 32 distinct pair IDs and family identities `F01` through `F08` with four blueprints each. Independent probes confirmed valid 32-row manifest acceptance; rejection of eight balanced but unregistered names, `f01`, `F09`, replacement of missing `F08` by `F07`, and a duplicate blueprint ID. No implicit name normalization was observed. Previous B03-A counterexample is closed within these supported inputs.

### B03-B — HMAC integrity: PASS_SCOPED for tamper detection

`preassign_r8()` validates the manifest, requires a bytes key of length at least 32, computes canonical JSON blueprint HMAC and binds fold, `component_id_pre`, component count, per-fold counts and `cv_status` in a separate preassignment HMAC. `postcheck_r8()` requires a schema marker, recomputes from the supplied blueprints and key, checks both MACs with `hmac.compare_digest`, compares the dependent fields and rejects invalid four-fold readiness. Independent probes confirmed rejection of self-created unsigned dicts, altered fold/status/counts, corrupted MACs, wrong/missing key, blueprint edits, newly added blueprint fields and non-finite JSON values. Reordering blueprint rows or object keys preserved both commitments.

**Custody limit:** An HMAC verified with a caller-supplied key establishes internal consistency under that key. This run has no independent custody attestation for the real key, or pre-G3 UTC receipt. After-the-fact recomputation with a chosen key remains technically possible absent external custody/timestamp evidence.

### B03-C — NEW independent counterexample: HOLD_G0_COMPONENT_SIGNATURE_NONINJECTIVE

**Source:** `folds_raters.py:48`, `folds_raters.py:52` and `folds_raters.py:154-177`.

The component rank uses `signature = "|".join(comp).encode("utf-8")`. The strict manifest accepts nonempty arbitrary string blueprint IDs, including embedded `|`. The encoding of component membership is therefore **not injective**. It can give two different component memberships the same HMAC input without cryptographic hash collision.

Independent synthetic 32-blueprint fixture, with exact `F01–F08` counts, unique valid `pair_id` and four otherwise conforming rows, was **accepted** by `validate_r8_blueprint_manifest()`. The first two rows share one `event_graph_id` and become component A `["a", "b|c"]`. The next two rows share another `event_graph_id` and become component B `["a|b", "c"]`. All other 28 components use separate identities.

- Component A encoded signature: `a|b|c`.
- Component B encoded signature: `a|b|c`.
- Actual G_pre result: **30** components with A and B distinct; their ranking HMAC inputs and HMAC digests are equal for any secret key.
- With equal hashes, `sorted(ranks)` falls back to comparing the plaintext component lists. Thus component placement can depend on the crafted ID spelling at a supposed HMAC ranking tie. The frozen V4 algorithm's intended HMAC ordering of immutable component membership is not assured over all accepted manifests.

Reproduction from the locked `integrated_closure` directory, using only a public, non-secret test key:

```python
import folds_raters as f

key = b"PUBLIC_NONSECRET_INDEPENDENT_B03_TEST_KEY_V1"
blueprints = [
    {
        "blueprint_id": f"BP_{i:02d}",
        "pair_id": f"PAIR_{i:02d}",
        "event_graph_id": f"EVENT_{i:02d}",
        "template_cluster_id": f"TEMPLATE_{i:02d}",
        "relation_family": f"F{i // 4 + 1:02d}",
    }
    for i in range(32)
]
for row, blueprint_id in zip(blueprints[:4], ["a", "b|c", "a|b", "c"]):
    row["blueprint_id"] = blueprint_id
blueprints[0]["event_graph_id"] = blueprints[1]["event_graph_id"] = "GROUP_0"
blueprints[2]["event_graph_id"] = blueprints[3]["event_graph_id"] = "GROUP_1"

f.validate_r8_blueprint_manifest(blueprints)  # Accepted
lock = f.preassign_r8(blueprints, key)
assert lock["component_id_pre"]["a"] != lock["component_id_pre"]["a|b"]
assert "|".join(["a", "b|c"]) == "|".join(["a|b", "c"])
assert lock["component_count"] == 30
```
This **does not forge the blueprint/preassignment MAC**, which still binds the complete manifest and fold. It is a distinct canonicalization weakness affecting the precommitted rank algorithm's domain of valid inputs. An independent proof of a unique/length-delimited canonical membership encoding or an enforced ID alphabet excluding delimiters is required to close B03-C. Reviewer did not modify source.

### Production caller: SOURCE_PRODUCTION_GATEWAY_VERIFIED (scoped)

Direct code inspection of `r8_production_caller.py` confirms that `precommit_before_G3()` calls strict `preassign_r8()`, and `verify_after_G3_before_CV()` calls strict `postcheck_r8()`. The caller rejects non-estimable pre-fold assignment, invalid locked dictionaries and post-graph `FOLD_LEAK_CV_INVALID`; it has no silent fallback to the primitive methods, no repartition and no generation code. Independent positive and cross-fold duplicate-card probes passed.

`FUTURE_REAL_AUTHORING_CALLER_BINDING_NOT_EXECUTED`. No actual R8 generator, durable G_pre receipt store or evidence of real pre-authoring invocation is connected to these entrypoints at this source pin. Source API existence establishes a usable preflight contract; future authoring integration and timing remain to be proven before actual R8 creation.

## 3. Independent negative QA receipts

Executed directly on pinned modules using local Python 3.12, CPU only, in-memory **non-R8 synthetic fixtures**. This was an independent 23-probe harness authored for this adjudication, separate from the implementation agent's 15/15 tests. No fixture files, R8 candidates, keys or gold were persisted.

**23 PASS / 0 FAIL** over the following checks:

- Valid F01–F08 manifest, balanced unregistered names, lowercase, F09, missing family, duplicate blueprint ID.
- Deterministic row-order and object-key-order canonicalization.
- Forged unsigned preassignment, tampered fold, `cv_status`, component count, blueprint MAC and preassignment MAC.
- Wrong key, missing key, edited blueprint, added blueprint field and invalid non-finite JSON.
- Production caller positive path, cross-fold duplicate-card fail-closed without fold reassignment, non-estimable precommit rejection, invalid case action rejection.

**One additional independent adversarial probe** produced `VALIDATION=ACCEPT`, `DISTINCT_MEMBERSHIP=True`, `AMBIGUOUS_COMPONENT_SIGNATURE=True`, `SAME_RANK_HMAC=True`, `COMPONENTS_1_AND_2_SEPARATE=True`, `COMPONENT_COUNT=30`. This is **B03-C** above. It is a discovered counterexample rather than a passing assertion for the full frozen V4 contract. The implementation-agent CI 15/15 remains valid for its narrower coverage.

## 4. G2 protected source-lock rebind: HOLD_SOURCE_LOCK_REBIND_NOT_VERIFIED

The local Windows executor identity was observed during the readback, but it was **not established as an authorized custodian identity for persistent private storage**. Its source readback was performed on a Git checkout. No protected-runtime source path or authorized private custodian readback was provided to this independent session. In particular, no independently verified receipt demonstrated current protected source bytes, private-store ACL/DACL scope, source-lock binding to this exact `5a51e1e6...` source, key provenance or a durable pre-G3 timestamp.

The historic **54-byte non-R8 Windows sandbox sentinel** and SHA-256 `0d880e2bed5f88f3578728fcde67b9dde341419244ba7006cf94146667cf1652` retain `PASS_SCOPED_STORAGE_PREFLIGHT_REPORTED`. They cover an earlier temporary environment and cannot attest the new B03 source in actual private custody.

**Required to close G2, as a single integrated custodian receipt:** authorized protected executor identity and scoped permissions, persistent store/source checkout identification, private runtime readback of new `folds_raters.py` and `r8_production_caller.py` SHA-256 plus unchanged `gold_contract.py`/`restricted_oracles.py` and relevant contract/runtime pins, protection method for the custodian-held key, and public-safe UTC timestamp/provenance showing the pre-G3 commitment path. No secret or private ACL contents are included in this report. No synthetic key was represented as private custody.

## 5. G1 owner standing direction and rights scope

Exact owner-decision commit `097e046bb0f6525665dde03ec5fcdf8134a8e762` records standing authorization for exploratory R8-D, four AI raters/two judgments per case and new P-REC-V1 synthetic toy-world evidence without real PII or unverified third-party rights. Its provenance is `OWNER_CHAT_DECLARATION_RECORDED_BY_ASSISTANT`. It is not a cryptographic signature or completed future data-rights screening. **`G1=OWNER_STANDING_RESEARCH_DIRECTION_RECORDED`**. No renewed owner GO request is necessary for the already specified scope; no new content was created in this review.

## 6. Integrated findings and final adjudication

| Finding | Status | Impact / counterexample | Remaining required evidence |
|---|---|---|---|
| B03-A closed family IDs | `PASS_SCOPED` | Previously accepted unregistered eight-family set now rejected | None for reviewed path |
| B03-B MAC integrity | `PASS_SCOPED_SOURCE` | Forged dict / edited fold and status rejected using supplied key | Protected key and timing are G2 matters |
| **B03-C ambiguous component signature** | **`HOLD_G0`** | Two distinct components `["a","b|c"]` and `["a|b","c"]` pass manifest but produce one rank HMAC input | Independent verification of injective component signature over all accepted blueprint IDs |
| Production API | `SOURCE_PRODUCTION_GATEWAY_VERIFIED` | Strict G_pre/G_post calls, leakage fail-closed | Actual authoring runtime binding and pre-G3 receipt remain `NOT_EXECUTED` |
| **G2 protected private rebind** | **`HOLD_SOURCE_LOCK_REBIND_NOT_VERIFIED`** | Git source hash cannot establish protected runtime identity, ACL, private key custody or timing | Authorized custodian's public-safe exact-source readback receipt |
| G1 | `OWNER_STANDING_RESEARCH_DIRECTION_RECORDED` | Existing exploratory scope selected | Apply existing rights/PII screening if future source data are authored |

**ONE FINAL DECISION: `HOLD_INTEGRATED`**. `GO_R8_D_CANDIDATE_AUTHORING_ONLY` is **not authorized** at this gate. G0 has one new source-level B03 issue and G2 still lacks the protected source-lock rebind receipt. This is a final evidence assessment for this operation and does not issue another handoff or micro-permit.

The reviewer made no changes to scientific source, no merge to `main` and no R8 production execution. Preserve **`R7=FROZEN_FAIL`, `R8=NOT_GENERATED`, `G3/G4=NOT_EXECUTED`, `G5/G6=SEALED`, `Reader=0`, `GPU=NO`, `PROBE256=SEALED`**.
