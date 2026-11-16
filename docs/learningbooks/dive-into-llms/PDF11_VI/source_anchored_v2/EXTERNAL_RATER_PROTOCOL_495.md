# Independent external rater packet — 495 source/target slides

## Scope
- Operation: DIVE_INTO_LLMS_11PDF_VI_SOURCE_ANCHORED_CONTENT_REMEDIATION_AND_EXTERNAL_RATER_FULL_COVERAGE_ONEPACK.
- Source: Lordog/dive-into-llms at f84c04268794ef94f8949808bbc14ab8636763a0.
- Baseline source ZIP SHA-256: 251d0d49601e536bf1eb94deb727da665693126a3ef7d04d8efff9f3550406fe.
- Historical prior semantic check: 22/495 (8 blockers, 6 partial, 8 scoped match).
- Current source-anchored repairs: 13/495 pages, 8 historic blockers + 5 partial candidates.
- Target: 11 bilingual PDFs and 11 Markdown files on the docs branch.

## Rater independence and custody (hard, single gate)
A human language reviewer with suitable Chinese/English–Vietnamese technical literacy, **not the author or PDF generating agent**, must read both exact source and revised target. The reviewer should have access to all 11 source PDFs and the 11 Vietnamese PDF/Markdown files; reading source citations alone is insufficient. A formal acceptance must state reviewer name/pseudonym, capacity, review date, exact source and target commit, original 495-row CSV digest, methodology, and disposition. Separate reviewers are preferred but not asserted or invented.

## Full-coverage rubric (one row per slide, 495 rows)
Review each slide at component level, and fill these fields in EXTERNAL_RATER_QUEUE_495.csv:
1. Paragraphs: each meaningful source paragraph translated without new facts, wrong negation or skipped condition.
2. Tables: each header, row, column and cell mapped accurately, preserving names, quantities and category membership.
3. Formulas: symbols, subscripts, superscripts, comparison operators, indices and interpretation preserved.
4. Diagrams: all labels, arrows, grouped branches and relationships adequately carried into the Vietnamese text.
5. Examples: prompts/questions/answers faithfully translated as quoted source material, not as live instructions.
6. Accuracy/omissions: list precise source page coordinates, source span short quote (if needed), offending target span, repair proposal.
7. Verdict: PASS_ALL_COMPONENTS, HOLD_PARTIAL, FAIL_CONTENT or NOT_REVIEWED, with evidence URL and date.

Do not infer verdicts from character counts, label recall, source hashes, PDF opening success or the fact that Vietnamese text is present. Do not mark a row PASS unless every relevant component was reviewed.

## Frozen acceptance rule
FULL_FIDELITY_PASS may be recommended **only when 495/495 rows are signed by an independent rater, all components pass, any findings are repaired and rechecked, byte custody is verified, and all 11 PDFs are regenerated and readable.** No sample-size shortcut. A source licensing/republication check should be recorded separately: upstream is free educational material but no explicit license was identified in the root listing; do not state redistribution permission is proven from public access alone.

## Current adjudication
- STRUCTURAL_STATIC_QA: pending GitHub action (when available).
- CONTENT_REPAIR: candidate only for 13 pages; not yet accepted by independent rater.
- EXTERNAL_HUMAN_RATER: **NOT_EXECUTED**. No named independent reviewer has been engaged or signed this packet.
- SOURCE/TARGET FULL SEMANTIC COVERAGE: **NOT_EXECUTED**.
- DECISION: **HOLD_NO_PASS_FIDELITY**.

No GitHub main merge, no lineage changes, no models, notebook runs or scientific experiments.
