# HANDOFF — Track A M0 v3 · I1 scoped PASS → PM

**Operation:** `TTM_TRACK_A_M0V3_I1_SCOPED_PASS_CLOSURE_AND_PM_RELEASE_BARRIER_SINGLE_GATE`  
**Date:** 2026-11-17 · **Repository:** `minhtri22/TokenToModel-Lab` · **Branch:** `research/ttm-track-a-small4m-diagnosis-20261116`  
**PR:** [#33 DRAFT](https://github.com/minhtri22/TokenToModel-Lab/pull/33) stacked on PR #28 HEAD `ebdc54575eed1ff60c402eecf60289f408bb38ca`.  
**Decision:** `I1_PASS_SCOPED_MEASUREMENT` **only** at exact source `ec197b5f00d3a037420390edd11ee55047e1d37f`.  
**Release state:** `I2_NOT_EXECUTED · RELEASE_PREFLIGHT_HOLD · NO_MERGE · NO_SCIENTIFIC_CAPABILITY_CLAIM`.

## Ground truth and immutable pins

- Distinct review evidence-only HEAD: `e3e1c802815f4db1534e92d9848d6015eb9203cc`. GitHub compare `ec197b5f..e3e1c802` contains exactly **four added evidence files** and no altered executable code.
- [Independent report](https://github.com/minhtri22/TokenToModel-Lab/blob/e3e1c802815f4db1534e92d9848d6015eb9203cc/artifacts/ttm-abc/track-a/M0_V3_POST_HOLD_DISTINCT_I1_20261117/REVIEW.md), [sanitized receipt](https://github.com/minhtri22/TokenToModel-Lab/blob/e3e1c802815f4db1534e92d9848d6015eb9203cc/artifacts/ttm-abc/track-a/M0_V3_POST_HOLD_DISTINCT_I1_20261117/receipt.json), [independent F01/F02 checker](https://github.com/minhtri22/TokenToModel-Lab/blob/e3e1c802815f4db1534e92d9848d6015eb9203cc/artifacts/ttm-abc/track-a/M0_V3_POST_HOLD_DISTINCT_I1_20261117/check_f01_f02.py), [native custody checker](https://github.com/minhtri22/TokenToModel-Lab/blob/e3e1c802815f4db1534e92d9848d6015eb9203cc/artifacts/ttm-abc/track-a/M0_V3_POST_HOLD_DISTINCT_I1_20261117/check_native_custody.py).
- Reviewer thread `01a1e558-969b-7e43-85c2-6aaa8d4df3e5`: independent source checks **35/35 PASS**. Native custody checker **38/38 PASS**. Same GitHub publication account as PR; independence rests on distinct reviewer session/checker provenance, not a different GitHub identity.
- TRAIN-only BPE source SHA-256: `cba18e60cee3d08a353ee6d4a451017289e45af7b4b1179c87171b9b78d7dfdc`.
- Original frozen M0 v3 records SHA-256: `823a08dd4be0da7748cb258b9bf5b2841dd1fdbac84956eb204be7ba57f8c55d`. Manifest SHA-256: `0b80368a6747994df5f5b8d0e7b35137266ac82f6c9b83d26af5b61f79b3cb04`. **80/80 case and 5/5 group digests** reverified read-only, no regeneration or overwrite.
- Prior distinct `HOLD_I1` at `05041501bfe84822feffd39290c6800b2152055a` is retained as historical evidence. Subsequent PASS applies **only** to the amended source/fixture pair.

## Adjudicated defects and metrics

| Finding | Current status | Exact scope |
|---|---|---|
| F01, full-vocabulary gold NLL near uniform float32 `1e20` | PASS | 240 independent uniform tests yield `ln(2048)=7.6246189861593985`; shifted non-uniform logits agree with Decimal oracle |
| F02, executable source hash vs forged `.pyc` | PASS | Loader bypasses cache and runs only SHA-checked source buffer; LF/CRLF, changed-after-read tests passed |
| Gold-blind candidates/split and parents | PASS_SCOPED | Independent fixture custody, 80 case digests, 5 group digests; no TRAIN binding leakage in declared independent probes |
| Windows owner-native readback | PASS_SCOPED | PS 5.1.26100.9818 / Python 3.12.10; original bytes preserved |
| Author Windows QA | PASS_SCOPED | [Actions 43903520071](https://github.com/minhtri22/TokenToModel-Lab/actions/runs/43903520071): 31/31 unit, 48/48 negatives, 18/18 source |
| Runtime release authorization | **HOLD** | Owner-internal preflight exits **2** with `HOLD_OWNER_INTERNAL_I1_NOT_PASS`; valid I1 PASS is not automatically a release permit |
| I2/scientific model execution | **NOT_EXECUTED** | 0 model forwards, 0 optimizer steps, 0 checkpoint accesses, 0 nonce claims |

## Residual infrastructure caveats (do NOT rewrite I1 PASS)

The independent reviewer explicitly documented that OnePack's "check destination then write receipt" is two non-atomic steps (**TOCTOU race**). The wrapper also reports the freeze-receipt SHA without pinning it internally, and delegates deep case/group digest and reparse-point inspection to the independent checker. These are **not newly discovered evidence of invalid I1 measurement**; the executed readback was covered by the external custody checker and unchanged snapshots. They are **release-readiness caveats** that must be adjudicated before any prospective I2.

**Do not silently repoint** `owner_internal_admission.py` to a new PASS just to make preflight succeed. The current guard correctly fails closed against its historical I1 pointer. Moving that pointer or changing signed-owner admission belongs to **PM/owner release policy**, not Track A measurement closure. Preserve the exact source that passed independent review. Any future executable change requires a new exact-source QA scope; it does not retroactively erase this PASS.

## PM handback — one integrated gate

Accept `I1_PASS_SCOPED_MEASUREMENT` as a scoped Track A M0 milestone while keeping PR #33 **DRAFT** and the original frozen evidence immutable. Review the release/ownership boundary, remaining OnePack TOCTOU and custody limitations, CI/native semantics, and any requisite merge dependency on PR #28 as **one integrated source-only PM decision**:

- **HOLD:** maintain I2 block (default until all release conditions satisfied).
- **GO_PROSPECTIVE_DESIGN_ONLY:** approve future design/remediation planning only, **not** I2 execution. Any actual I2 permit is a separate explicit owner release, and requires all runtime/custody prerequisites.

Do not run I2, issue a nonce, load a model, merge, change PR #28, or amend `lineage.md` in this closure packet. Do not multiply into micro-permits.

**Only next action:** `TTM_TRACK_A_M0V3_I1_SCOPED_PASS_CLOSURE_AND_PM_RELEASE_BARRIER_SINGLE_GATE`.

**Closure:** `I1_PASS_SCOPED_MEASUREMENT · RELEASE_PREFLIGHT_HOLD · I2_NOT_EXECUTED · NO_MERGE · NO_MODEL_EXECUTION`.
