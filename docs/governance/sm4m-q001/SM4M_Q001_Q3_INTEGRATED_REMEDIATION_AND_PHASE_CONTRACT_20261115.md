# SM4M-Q001 — Một lượt sửa tích hợp Q3-F01…F04 (owner Q4 vẫn HOLD)

**Operation:** `SM4M_Q001_Q3_INTEGRATED_GOVERNANCE_AND_ADMISSION_SEQUENCING_REMEDIATION_SINGLE_GATE`  
**QuestionID:** `SM4M-Q001` · **Date:** 2026-11-15  
**Repo:** `minhtri22/TokenToModel-Lab` · **PR:** [#21](https://github.com/minhtri22/TokenToModel-Lab/pull/21)  
**Original Q3 candidate HEAD:** `3c53d062c7c6ff4218d80177253dd1c061ac6362`  
**Original Q3 verdict:** `HOLD_Q3_REMEDIATION` (2 HIGH, 1 MEDIUM, 1 LOW).  
**Remediation authority:** correction of governance/admission *documents on same existing PR*, no science, no new research branch, no Q4 decision and no merge.

## 1. Preservation / exact documentary custody

The 7 author-Q2 originals **remain byte-identical in their original paths and at exact SHA-1 pins** listed in [owner scope acceptance](SM4M_Q001_OWNER_SCOPED_Q2_ACCEPTANCE_20261115.md). Reviewer Q3 report is archived verbatim as [Q3 original Markdown](SM4M_Q001_Q3_DISTINCT_INDEPENDENT_REVIEW_20261115.md), with original SHA-256 `e619ea9460abd112ab32016e7644c273a6cce2d20044fe8bd0e129d18d820680` (Git blob `0b85f84cfd17ff0612291706c5d0fa36d86800c7`). Reviewer JSON receipt was supplied inside an uploaded ZIP, with exact JSON SHA-256 `529490652a7f140153292ec090496c1b5deec8ca36f54b25aa5b63c98cbd08ba` and ZIP SHA-256 `816938d1d08479947c21206b6eeacc41da43c07abc29ac42dc31b0a844ae089d`. **The ZIP is not part of this PR** (the binary-transfer attempt did not achieve exact Git blob verification); no claim it has been archived on GitHub. Derived reviewer receipt summary is labeled as such.

The authoritative **review candidate v2** for admission timing (not an original Q2 artifact) is:
`artifacts/governance/sm4m-q001/SM4M_Q001_Q2_CAUSAL_EVIDENCE_MATRIX_Q3_REMEDIATION_V2_20261115.json`, Git blob `10d901906c24ca4a0bc93827e45982390cc18ae5`. Its predecessor remains Git blob `b7e87dbdd31c6624387f9943d7ff7db8efa8663a`.
The corrected literature candidate is `docs/governance/sm4m-q001/SM4M_Q001_Q2_LITERATURE_TRIAGE_Q3_REMEDIATION_V2_20261115.md`, Git blob `cbe529125d158c535c568fbed7bcffbdc8819cca`. Original remains `380582a4f1260dfda28d39e0cb56be2fc02709c5`.

New-version files supersede **only the identified timing/term defects**, not original evidence data, scientific verdicts, Q2 author receipts, source pins, or owner Q2 scope acceptance.

## 2. Phán xét từng finding & correction contract

| Q3 finding | Severity | Old defect | Scope-limited amendment | State |
|---|---|---|---|---|
| `Q3-F01` | HIGH | Machine matrix first lists AD-03 visible-gold and AD-06 paired identifiability before scoring, too late for fixture creation | V2 adds `conditions_before_authoring` with AD-03/AD-06, `conditions_before_freeze` and explicit rechecks at model execution/scoring; prospective stop rules | `AUTHOR_REMEDIATED_PENDING_INDEPENDENT_READBACK` |
| `Q3-F02` | HIGH | Active register has contradictory old Q2/Q3 statements and two single next steps | Replaced active register with one canonical present state `Q3_HOLD_REMEDIATION_SUBMITTED_PENDING_REREVIEW`, one next step; history via exact Git refs | `AUTHOR_REMEDIATED_PENDING_INDEPENDENT_READBACK` |
| `Q3-F03` | MEDIUM | AD-01 rights, tokenizer identity and checkpoint SHA are incorrectly bundled as unconditional pre-authoring veto | V2 AD-01R (rights before content access), AD-01T (tokenizer/split prior to token-sensitive fixture freeze), AD-01C (checkpoint bytes before model execution). No dilution of rights/byte gates. | `AUTHOR_REMEDIATED_PENDING_INDEPENDENT_READBACK` |
| `Q3-F04` | LOW | Holtzman P05 “Max-likelihood decoding” imprecise | V2 literature uses “Maximization-based decoding”; causal interpretation unchanged | `AUTHOR_REMEDIATED_PENDING_INDEPENDENT_READBACK` |

**Finding status is proposed by Q2 author, NOT closed by independent Q3.** Independent Q3 review can HOLD again or create a new material finding.

## 3. Gating phases — strict ordering

| Phase | Preconditions / hard veto | What remains forbidden |
|---|---|---|
| `P0_ABSTRACT_READ_ONLY_DESIGN` | Existing permitted source/policy only; no private tokens, gold or model. Identify question, constraints and alternatives | No production authoring, no dataset, no executable runner or science. Private model checkpoint byte custody is **not** a prerequisite for abstract design |
| `P1_BEFORE_CONTENT_ACCESS_AND_PRODUCTION_AUTHORING` | `AD-01R` source/data rights **if accessing/authoring content**; `AD-02` construct feasibility; `AD-03` visible-evidence/gold witness contract; `AD-05` shortcut controls; `AD-06` one-variable paired identifiability; `AD-07` proposed metric contract; `AD-08` future Q4+scoped authoring authority | If any applicable hard veto fails, `HOLD_NO_PRODUCTION_AUTHORING`; conceptual review may still continue |
| `P2_BEFORE_FIXTURE_FREEZE` | Per-item `AD-03` source-visible witness (or separately preregistered exact programmatic oracle contract); `AD-06` matched pair/one variable/equal information, token normalization; `AD-05` leakage/shortcut controls; `AD-07` rubric, direction, ties, thresholds, blind custody; `AD-01T` exact tokenizer/split identity if token-sensitive | `HOLD_NO_ITEM_FREEZE`; no late scoring-stage discovery of unidentifiable pairs |
| `P3_BEFORE_MODEL_EXECUTION` | `AD-00` source/run pins; `AD-01C` exact checkpoint bytes; rights + token identity; `AD-03/05/06` fixture-parity recheck; `AD-07` frozen prereg; `AD-08` separate science permit | No inference/training/scoring without owner authorization; sealed TEST/FINAL never replayed |
| `P4_BEFORE_SCORING` | `AD-04` independent gold/rater calibration; `AD-03/05/06` *rechecks*, not first admission gates; `AD-07` sealed scorer/threshold; `AD-08` authority | Scoring HOLD on missing visible proof, gold, calibration, paired identifiability, blind custody, or rights |

`AD-01R/T/C` are phase-specific **subconditions** of original `AD-01`, not a new scientific gate or extra micro-permit. `AD-03` and `AD-06` must be decidable *before production authoring*, verified *before fixture freeze*, and rechecked at actual scoring. A hidden `E_core` gold with no witness in allowed-visible source is **not rater-visible ground truth**. A separately defined programmatic oracle would require its own prospectively approved scoring contract and equal information budget; it cannot be used to launder hidden information.

## 4. Scientific conclusion / hard exclusions remain unchanged

- `KEEP_HISTORICAL_REFERENCE_ONLY`: confirmed by Q3, source-scoped.
- `HOLD_BASELINE_ADMISSION_FOR_NEW_SCIENCE`: confirmed by Q3.
- `ROOT_CAUSE_NOT_IDENTIFIED`: confirmed by Q3.
- `AD-00=PARTIAL_PUBLIC_SOURCE_MATCHED`; `AD-01…AD-08` retain their original unverified/unexecuted statuses. The v2 is a **logical design admission sequence**, not admission results.
- No patch to attention/FFN/Transformer/trainer, no F0–F2 restart, no new dataset/gold/scorer, no inference/GPU/training, no TEST/FINAL replay, no owner Q4 or PR merge, no branch cleanup.
- `lineage.md` remains append-only and unchanged; HOLD design is never entered as scientific FAIL.
- Existing governance branch is reused. `main` stays at `6cab3b8e8430628aa5c944a494ccc08d8f8783fc` until an authorized merge, which is **not requested** in this gate.

## 5. What the distinct re-review must prove

1. Recheck Q3 original report/receipt SHA and 7 original Q2 Git blobs, prove byte immutability.
2. Verify amended matrix **machine-readable** AD-03 and AD-06 are required before authoring/freeze, *not first introduced before scoring*; rerun negative sequencing cases.
3. Verify AD-01 rights still block unauthorized source/data access; tokenizer parity blocks token-sensitive fixture freeze; private checkpoint custody blocks any model execution but not read-only design.
4. Verify `ACTIVE_RESEARCH_GATE.md` has **exactly one** authoritative current Q2/Q3 state, exactly one next step and no contradictory stale Q1-only lines; live main must be reported separately.
5. Check Holtzman term in the **v2 paper review**; original Q2 artifact is immutable and intentionally not silently edited.
6. Check no original study metric/denominator, 7 hypothesis labels, admission PASS state, threshold, scientific root cause, authority, or `lineage.md` was changed.
7. Provide one final Q3 re-review verdict `PASS_Q3_SOURCE_AND_EVIDENCE_SCOPE_SCOPED` or `HOLD_Q3_REMEDIATION`, with exact amendment HEAD/lines and reviewer declaration. Q3 PASS is **not** new science GO; Q4 still owner-only.

**Current status:** `AUTHOR_REMEDIATION_SUBMITTED · ORIGINAL_Q3_HOLD_PRESERVED · DISTINCT_Q3_REREVIEW_NOT_EXECUTED · OWNER_Q4_NOT_DECIDED · SCIENCE_HOLD`.
