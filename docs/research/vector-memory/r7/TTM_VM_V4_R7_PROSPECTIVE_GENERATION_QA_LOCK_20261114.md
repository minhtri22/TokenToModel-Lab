# TTM VM V4 CAL64 R7 — prospective source generation / QA lock
Operation: TTM_VM_V4_R7_PROSPECTIVE_FAMILY_BALANCED_CAL64_SOURCE_AUTHORING_AND_ANTISHORTCUT_ONE_SHOT
Status: DESIGN_LOCK_FOR_EXPLORATORY_CANDIDATE_ONLY; NOT_OWNER_ADOPTED; NOT_SCIENCE_PREREG.
Lock recorded before generating R7. Do not reselect seeds or revise R7 after seeing QA.
Original R5 and independent review frozen; R6 failure and rights HOLD frozen. Source protocol: R6_ROOTCAUSE_PROSPECTIVE_GATE_ONEPACKET SHA256 f5031f83cdb3754285a9095281c6fa7ac08f44682653e29543144a5584dd19c1.
R6 critical pitfalls: question template 4/4 anti-majority leave-one-out, case ordering P0-P3 SELECT then N0-N3 ABSTAIN; fixed batch-to-location mapping; incidental metadata.

## R7 design locked for one shot
- 64 cases, 8 strata P0..P3,N0..N3 x 8; 8 semantic families x 8 strata; family each 4 SELECT/4 ABSTAIN; 32 cards per case; independent random shuffle cases and per-case cards, opaque 64-bit+ IDs.
- Eight families defined semantically: custody approval; physical goods receiving; cross-record assignment linkage; effective-date supersession; incomplete evidence; competing authorized records; false-premise scope mismatch; near-duplicate identity ambiguity. Each family appears in each stratum but family realization must not equal stratum template. Family x stratum structure may *still* leave stratum label predictable; QA must assess and HOLD on leakage.
- Generate deterministic once with fixed seed 20261114; no adaptation after QA. 8 contexts x 8 strata are **not** proof of independent families. Keep metadata private: family/stratum/gold/rights.
- Public draft is SEALED in HOLD and not shared with raters. Private draft contains gold and is never pushed to public GitHub.
- Content QA check: exact counts, 64 unique IDs, each 32 unique keys, positive one supported target, negative none, 4/4 family, 8 per stratum; no gold/stratum/family/label in public; position-only features; question-only and marker-only; fixed folds; two-sided deviation; lexical and same-family template overlap. Any gold ambiguity HOLD.
- Fixed diagnostic seed 20261114; report raw, not flipped, accuracy, balanced accuracy and counts. No selecting new seeds, changes or dataset based on outcomes.
- Proposed warning |accuracy - 0.5| >= 0.125 for 64; threshold is *exploratory proposal*, not pre-approved scientific cutoff. A deterministic shortcut or metadata leakage FAIL. Weak power HOLD, never infer absence.
- Owner rights/prereg: AI_AUTHORED_SYNTHETIC_EXPLORATORY_ONLY PROPOSED, rights NOT_ATTESTED, no fabricated owner signature. Independent reviewer NOT_EXECUTED.
- Only one generation and one QA. A failed R7 remains immutable. No Reader, TEST, GPU, PROBE256 or blind scoring.
Decision: design locked for candidate-generation mechanics, but SCIENCE=HOLD.
