# PR #12 - Phan xu kiem dinh QA Windows T4 va sua hai loi decode UTF-8 (2026-11-09)

**Loai:** QA ky thuat, khong phai ket qua khoa hoc. **Trang thai:** SOURCE_FIX_STATIC_ONLY; runtime successor NOT_EXECUTED.

## Ket qua goc duoc giu nguyen
- Source HEAD da kiem: `9328d6fa9c0acf3338dbfe228d290e83e633a58e`. Evidence commit bat bien: `fd466e7e92cd77b86e3827ed696a5c3e551d0248`.
- Danh sach GitHub 13/13 file duoc doc lai. Python duoc chon: `C:\Users\minht\AppData\Local\Programs\Python\Python312\python.exe`. Dependency preflight PASS.
- T1T3: **10/10 PASS**; T2: **11/11 PASS**; T4: **11/13 PASS**; T5 V5 offline: **47/47 PASS**; T5 inference offline: **12/12 PASS**; Q1/Q2 static frozen PASS.
- Hai test T4 FAIL de doc notebook UTF-8 khi `Path.read_text()` mac dinh Windows cp1252: `test_capacity_notebook_no_science_and_source_pinned` tai dong 113 va `test_science_notebook_fails_closed_before_drive` tai dong 159.
- Log ro rang `UnicodeDecodeError: 'charmap' codec can't decode byte 0x81` va `0x8d`; loi decode, khong phai dai so, ket qua model, input khoa hoc, qua tai hay khoa TEST.
- `TTM_PR12_EPHEMERAL_CLEANUP=SKIPPED_QA_HOLD_PRESERVE_CLAIM` hoat dong dung; khong xoa `_tmp/TTM_PR12_QA_9328d6fa9c0a`, khong chay lai run ID.

## Ban sua nguon toi thieu

Duy nhat `tools/pilot_t4/integrated/tests/test_t4_integrated.py` thay:
1. `(ROOT/'TTM_T4_Synthetic_Capacity_20261108_v1.ipynb').read_text()` -> `read_text(encoding='utf-8')`.
2. `(ROOT/'TTM_T4_Science_FailClosed_20261108_v1.ipynb').read_text()` -> `read_text(encoding='utf-8')`.

Khong sua notebook, source T4 scientific trainer, T5, MODEL, GGUF, TOKENIZER, checkpoint, train/TEST. Khong sua `lineage.md`.

## QA / Merge gate
- Doi chieu exact text 2/2, voi nguon goc check-bang GitHub; file patch khong gom thay doi nao khac.
- `UTF8_FIX_STATIC_REVIEW=PASS_SCOPED` sau khi doc lai Git blob moi. Khong gia `T4_TESTS_PASS` neu chua co Windows readback.
- Chay **mot batch successor** tu GitHub HEAD moi, RunID moi, khong rerun test scientific TRAIN/TEST hay nhung one-shot cu. Sau do phan xu `QA_PASS` hoac `QA_HOLD`.
- `MERGE_DECISION=HOLD` cho toi khi exact HEAD full QA PASS va owner review rights / scope complete.

Bước thực hiện tiếp theo: `TTM_PR12_UTF8_TWO_LINE_REPAIR_SUCCESSOR_QA_AND_MERGE_ADJUDICATION`.
