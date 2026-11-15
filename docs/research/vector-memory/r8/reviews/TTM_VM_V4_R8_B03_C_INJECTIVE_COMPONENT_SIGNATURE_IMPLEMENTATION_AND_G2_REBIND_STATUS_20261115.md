# TTM VM V4 R8 — B03-C injective component signature: source remediation and G2 status

**Date:** 2026-11-15 (Asia/Bangkok)  
**Operation:** `TTM_VM_V4_R8_B03_C_INJECTIVE_COMPONENT_SIGNATURE_AND_G2_PRIVATE_CUSTODY_SOURCE_LOCK_SINGLE_GATE`  
**Classification:** `IMPLEMENTATION_AGENT_FOCUSED_QA`, NOT independent G0 adjudication or G2 custodian attestation.  
**Decision:** `HOLD_INTEGRATED`. R8-D authoring remains NOT_AUTHORIZED.

## Source pins and original finding

- New independent review **`b21a6bb6576d3b7ecc7f63fba8ff67fab5e102bb`**: [exact report](https://github.com/minhtri22/TokenToModel-Lab/blob/b21a6bb6576d3b7ecc7f63fba8ff67fab5e102bb/docs/research/vector-memory/r8/reviews/TTM_VM_V4_R8_B03_FINAL_INDEPENDENT_G0_AND_G2_PROTECTED_REBIND_ADJUDICATION.md) reports B03-A PASS_SCOPED, B03-B PASS_SCOPED, B03-C HOLD because different component membership arrays `["a","b|c"]` and `["a|b","c"]` both joined to `a|b|c`, producing identical HMAC ranking messages without hash collision.
- Prior unchanged source `5a51e1e6ca0938b0f77d1db553da45cd294a97c3` and CI [43602350914](https://github.com/minhtri22/TokenToModel-Lab/actions/runs/43602350914) `15/15 PASS` remain pinned. The independent reviewer separately reported 23/23 passing probes PLUS one B03-C adversarial failure witness, not a 24/24 source PASS. No historical QA was rerun.
- Frozen V4 scientific contract `b8410d9c1f77a733036e980b567de73c316f8725`; owner standing research decision `097e046bb0f6525665dde03ec5fcdf8134a8e762`. Neither was changed.

## One focused implementation

**Source commit:** `8d14cc2c89bfb178e6c415c5edeba8cc58b2558b`  
[GitHub diff](https://github.com/minhtri22/TokenToModel-Lab/commit/8d14cc2c89bfb178e6c415c5edeba8cc58b2558b)

Changes:
1. `integrated_closure/folds_raters.py`: added `_component_signature(comp)` using sorted, canonical UTF-8 JSON array representation of member IDs, with explicit `R8_GPRE_COMPONENT_V1` domain separation, duplicate/nonstring guard; `preassign()` now HMACs this canonical signature instead of `"|".join(comp)`. JSON string escaping and array delimiters preserve component membership boundaries even for accepted IDs containing `|`, commas, quotes, backslashes, newline, brackets or Unicode. HMAC blueprint and fold record mechanisms remain unchanged.
2. `integrated_closure/test_g0_b03_component_signature.py`: seven new non-R8 source-only tests cover the reviewer's exact ambiguous pair, canonical ordering/domain tag, special characters, nonstring/duplicate members, HMAC observation of distinct messages, strict production caller with synthetic 32-blueprint/64-case fixture and changed G_pre graph source lock.
3. Targeted GitHub workflow changed to run **only these seven tests**, not historical 37/37, 25/25, previous 15/15 or B03-A/B03-B 15/15.

**GitHub Actions** [run 43671809208](https://github.com/minhtri22/TokenToModel-Lab/actions/runs/43671809208): `completed/success`, exact source commit `8d14cc2c89bfb178e6c415c5edeba8cc58b2558b`; CPython 3.12 on Ubuntu; **7/7 PASS**. CI `R8_GENERATED=FALSE`, `PRIVATE_GOLD=NOT_ACCESSED`, `READER=0`, `GPU=NO`, `PROBE256=SEALED`.

Exact CI source SHA-256:
- `folds_raters.py`: `db0879f6f2c5557d46e48207e84b8071cf85a772f9b83c22bb777c4fe0fd5f8b`
- `r8_production_caller.py`: `3a9b249bced1b4ceaa5746d63367c017410ef82ded21ef386c3be2b1ee76b206` (unchanged)
- `test_g0_b03_component_signature.py`: `2f6caa38664e7b735da053605799a7ac719b9d800050bec0a9a7a6364acd7cc3`
- `gold_contract.py`: `8e8b81ce2d0bc47cc60c29abc7156fe9d97613e67983e43b7f587615d68015a5` (unchanged, from prior pinned CI)
- `restricted_oracles.py`: `34ab74d36b822703e4d8cbdf281e142273d55d181243d904b55fd31a0e6382a1` (unchanged, from prior pinned CI)

## G0 remains pending independent review

Implementation source QA = `PASS_7_OF_7_SCOPED`; new external reviewer must independently confirm that _component_signature is injective over **all accepted blueprint ID strings**, not just the seven fixtures; ensure proper domain separation and G_pre timing, and reconcile prior B03-A/B PASS_SCOPED without rerunning unchanged historical suites. Production preflight caller still exists, but **real G3 authoring runtime integration has not occurred**, and no R8 data exist. The current implementation agent cannot sign independent G0 PASS.

## G2 current attempt and limitations

- RemoteDesktop `machine-1` was `ONLINE` in the live device inventory on 2026-11-15; listed `D:\WORK\RESEARCH\TokenToModel-Lab\_evidence\vector-memory` contents successfully. Those files are from prior VM research; they do **not** constitute a persistent R8 protected custody receipt, nor establish private ACL authority.
- CMH Remote Web canary showed `online=true`, `mode=RC3_I_OFFLINE`; this is NOT an active private custodian executor attestation.
- **No task was dispatched** to write/read inside a protected R8 store; no current private executor identity, persistent store ACL, actual protected-runtime source SHA-256, G2-held key or pre-G3 dated commitment receipt was obtained. The old 54-byte non-R8 sentinel preflight remains `PASS_SCOPED_STORAGE_PREFLIGHT_REPORTED` (source independent report `62542b6db216a021f84aa8495f40794fb82097d4`). Do not rerun solely because source changed.
- **G2=HOLD_SOURCE_LOCK_REBIND_NOT_VERIFIED**. Actual custodian must verify source-lock of the **NEW `folds_raters.py` hash `db0879...`**, unchanged caller and other source pins in its protected runtime, persistent ACL and identity/custody controls. Public CI hash never substitutes for the private readback.

## Final adjudication and one remaining integrated gate

- `G0_B03_C_IMPLEMENTATION_QA=PASS_SCOPED_7_OF_7`; `G0_INDEPENDENT_DELTA_REVIEW=NOT_EXECUTED`.
- `G1=OWNER_STANDING_RESEARCH_DIRECTION_RECORDED`; do not ask for further owner GO for same synthetic exploratory scope.
- `G2=PASS_SCOPED_OLD_SANDBOX_PREFLIGHT; HOLD_CURRENT_PRIVATE_SOURCE_LOCK_REBIND`.
- `DECISION=HOLD_INTEGRATED` and `GO_R8_D_CANDIDATE_AUTHORING_ONLY=NOT_AUTHORIZED`.
- Preserve `R7=FROZEN_FAIL`, `R8=NOT_GENERATED`, `G3/G4=NOT_EXECUTED`, `G5/G6=SEALED`, `READER=0`, `GPU=NO`, `PROBE256=SEALED`.

**Only next review step:** A reviewer distinct from the implementing agent inspects the exact B03-C source change at `8d14cc2...`; an authorized Windows custodian performs current protected runtime source-lock readback and ACL/identity confirmation for those bytes. Then one integrated GO/HOLD adjudication. Do not re-run historical 37/37, 25/25 or 15/15, open new V5/V6, make further handoffs or fabricate private receipt.
