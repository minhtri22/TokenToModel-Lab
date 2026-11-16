# Exact 495 source slide preservation QA request

Operation `DIVE_INTO_LLMS_11PDF_VI_SOURCE_ANCHORED_CONTENT_REMEDIATION_AND_EXTERNAL_RATER_FULL_COVERAGE_ONEPACK`.

This is a **technical**, read-only comparison of 495 current source-slide regions against historical PDF bytes pinned at `9544b06b9c95a319cae764957bad2c7450b11a9f`. It is not language adjudication. No independent external rater is engaged; do not change `FIDELITY_HOLD`.

No science, main merge, or lineage changes.

Exact script repair: interpolate shell variable n when reading 11 historical PDFs.

Diagnostic run: report mismatch categories and sample IDs; do not assert source preservation until classified.

Final differential run: measure each raster MAE, require max <=0.22 (existing QA threshold), source text exact. Preserve any remaining failures.
