# P01 I0A-S — F0 Smoke Preparation (NO QA0 EXECUTION)

**Source base**: 7e8b37d59b10b7a71603f6b446b57b9e3a9cb645  
**Operation**: `TTM_P01_I0A_S_STATIC_SOURCE_FIXUP_AND_QA0_F0_SMOKE_PREP`  
**Scope**: limited follow-up source changes and addition of one QA0 smoke-suite source file. No dynamic execution, no F1/F2/corpus read, no tokenizer/model training, no PR merge, no P00/worktree cleanup.

## Source fixes

1. `src/p01/data_dedup_split.py`: validate the document object type, its ID, raw bytes and strictly-boolean approvals **before** `sum`, sort, Unicode decoding and pairwise processing. Reject bad types with `SourceScopeError`; quarantine malformed UTF-8. Validate split input shape before using `bytes.fromhex`.
2. `runtime/p01/source_scope_guard.py`: pin exact SHA-256 payloads for F00–F11 and M01 and reject all other payloads from F0-only helper functions, even when a caller supplies the expected admission text. `src/p01/byte_bpe.py` and `src/p01/data_dedup_split.py` call the content-identity check.
3. This is a **content whitelist, not authentication or confinement**. A same-process caller can supply strings, and the worker may have broad filesystem ACLs. QA0 MUST use an external sandbox/control-plane source admission and fail-closed Job Object/write broker before runtime is authorized. No broad acceptance of 30+ arbitrary scientific documents is implied.

## QA0 smoke suite — source prepared only

New file: `qa/p01/qa0_f0_smoke_test.py`. `unittest` only, no `__main__` auto-run. It defines ten independent tests:

| Case | Intent | Expected |
|---|---|---|
| S01 | Full B0 byte domain | Exactly 0..255 and round-trip |
| S02 | F00–F11 | 12 pinned raw SHA and round-trip checks |
| S03 | Unicode and invalid UTF-8 | Preserve NFC/NFD distinct bytes; reject invalid |
| S04 | Invalid B0 IDs | Reject negatives, bool, float, out-of-range, strings |
| S05 | M01 47-byte golden | Deterministic merges and independent checker match SHA |
| S06 | Corrupted/trailing merges | Checker rejects tampering |
| S07 | Malformed document objects | Deterministic exception before attribute access |
| S08 | F02/F03 canonical group | Same group, fewer than 30 groups cannot be split |
| S09 | Unpinned, rejected admission | No arbitrary input accepted via marker |
| S10 | Unimplemented guards, source and receipts | Fail closed |

**Execution is NOT approved here**: no `python -m unittest`, no import of the new source in I0A-S, no `pytest`, no file-based QA0 fixture materialization. Once QA0 is separately authorized, run exactly this suite using a verified isolated supervisor from the project root with bytecode writing disabled, no network, no corpus mounts and a hardened writable directory. No automatic rerun.

## Next gate

`TTM_P01_QA0_F0_SMOKE_EXACT_RUNTIME_SCOPE_AND_NEGATIVE_GUARD_DECISION`: verify source SHA/review test cases, an actual runtime sandbox and independent observer. If worker containment remains unimplemented, a separate **isolated test-only host environment** must be proven safe; do not treat the marker string or default Windows ACL as containment. A failure remains a scientific-neutral technical QA finding, not a `lineage.md` science result.

**Status**: `SMOKE_SUITE=PREPARED_NOT_EXECUTED`; `QA0_DYNAMIC=NOT_AUTHORIZED`; `E0_SCIENCE=NOT_AUTHORIZED`.
