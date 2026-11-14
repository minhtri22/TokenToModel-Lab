# TTM Vector Memory V4 — R7 one-shot source QA / formal HOLD
Operation: TTM_VM_V4_R7_PROSPECTIVE_FAMILY_BALANCED_CAL64_SOURCE_AUTHORING_AND_ANTISHORTCUT_ONE_SHOT
Scope: AI-authored exploratory **candidate only**; generated exactly once using frozen seed 20261114, after protocol-lock commit 74ef335fb1418515a21591c598d9109ce68070c4.
**Decision: FAIL_MARKER_SHORTCUT_HOLD_SCIENCE.** Do not regenerate, silently patch, or release R7.
## Immutable evidence
- R7_PRIVATE_NOT_ADMITTED.json SHA256 `d9e9d6534eae4dbe1169edf2eaa7b6cc2da04eee94296b791b839f6531522db4` — 717251 bytes (kept private, **not** on public GitHub).
- R7_PUBLIC_PREVIEW_SEALED.json SHA256 `78de11f46ea0d64b21f78fc325e4120c707d38bf9efec295628bfbf52a644564` — 695753 bytes (sealed, **not** on public GitHub).
- build_and_qa_r7.py SHA256 `1d2fc15967f758adc3c8ab99122a9928addd696ee0ce170e47f0e1097c75d287`.
- R7_ONE_SHOT_QA_REPORT.json SHA256 `9ff4ddbdfd141a889504a1ab2b9dcd626a928913000c6e611dc5e3dc24e0a31b`.
- independent_readonly_qa.py SHA256 `f08fd24524ac26f71ada42b3b744ff9b47a55d54b3923efb1fc130f1ff84a310`.
- R7_READONLY_INDEPENDENT_CODE_QA.json SHA256 `f6e7e30bf18de69e48ffa7c079df6f3db55521bc1ad70fa1a862167b11e6bd97`.
All hashes from the actual local bytes created in the one-shot, not from GitHub content.

## Results
- Structure: 64/64 cases, 32 cards/case = 2048 total, 8×8 strata, 8 latent family IDs × [4 SELECT,4 ABSTAIN]; case order shuffled; per-case card order shuffled; opaque IDs.
- Static QA independent code path: **7/9 PASS**, two marker leakage checks FAIL. Same assistant environment; not a separate AI reviewer.
- Marker-only action rule: SELECT iff any card has phrase "applicable signed record" => **64/64 correct**, without semantic reasoning.
- Marker-only target-key rule: locate the unique card with that phrase => **32/32 positive gold keys correct**.
- First 32 case-position naive rule: 28/64 correct (0.4375). Question-frame in-sample majority 36/64 (0.5625); both exploratory diagnostics, no claim of generalization.
- Other question-only CV, lexical baseline, external family overlap review NOT_EXECUTED; cannot mark PASS.
- R7 semantics inherit P0–P3 SELECT, N0–N3 ABSTAIN; family balance does not remove stratum-label confound. False sense of independence from unique family codes forbidden.
- Gold/content independent AI review NOT_EXECUTED. No human rights attestation. Source class AI_AUTHORED_SYNTHETIC_EXPLORATORY_ONLY is PROPOSED_NOT_ADOPTED. No science release.

## Custody and governance
R5 frozen, R6 frozen; R7 candidate frozen at SHA and known failure. Private gold and sealed public preview were deliberately not pushed to a public repo. Do not interpret a SHA in a public report as custody of the bytes in GitHub.
No blind raters, no threshold freeze, PROBE256=SEALED, TEST=SEALED, READER=0, GPU=NO.
**NEXT**: TTM_VM_V4_R7_MARKER_SHORTCUT_FAILURE_ADJUDICATION_AND_PROSPECTIVE_R8_PROTOCOL_REVIEW_NO_GENERATION; do not permit R8 generation until prereg/rights and independent content baseline gate are settled.
