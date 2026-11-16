# Single-run PDF11 Vietnamese fidelity remediation

Operation: `DIVE_INTO_LLMS_11PDF_VI_FIDELITY_REMEDIATION_AND_INDEPENDENT_LANGUAGE_QA_ONEPACK`

Run on docs branch only. Decode three pinned source payloads, regenerate *existing* 11 PDF candidates and 11 slide notes, compare exact baseline and verify 495 pages. Only commit a completed candidate when separate static QA passes. Do not start any science execution or independent-human QA by implication.

**Owner gate:** keep `HOLD_FIDELITY` regardless of static success. No main merge.
