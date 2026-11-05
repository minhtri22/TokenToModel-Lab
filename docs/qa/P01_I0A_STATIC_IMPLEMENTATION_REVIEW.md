# P01 I0A-S — Static source implementation review (UNEXECUTED)

- Status: `SOURCE_ONLY_NO_RUNTIME_QA`.
- Scope: F0 synthetic design; no F1/F2, corpus/TEST, model data, real training.
- Permitted paths: exactly 12 candidate files in the owner-approved I0A-S allowlist.
- Tokenizer: B0/Byte BPE reference, deterministic rules, independent merges parsing.
- Data: H03 canonicalization, near-duplicate and union-find/split design.
- Windows guard/write broker: FAIL-CLOSED stubs; not functional and not security-certified.
- Evidence serializer: design-only subset, not a production JCS implementation.
- No import/execution/test/golden fixture materialization on target in I0A-S.
- Static validation: verify UTF-8, syntax without import, source hashes, no out-of-scope paths.
- QA0 dynamic testing and E0 scientific experiment: NOT_GRANTED.
- No claim of C01-C10/W01-W12 runtime PASS. 
- P00, `.git`, `lineage.md`, main, PR #4: protected, not merged or cleaned.
