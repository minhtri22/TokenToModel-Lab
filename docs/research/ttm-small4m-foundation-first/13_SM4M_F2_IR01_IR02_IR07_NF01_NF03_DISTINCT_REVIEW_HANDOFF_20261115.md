# HANDOFF — SM4M-F2 IR01/IR02/IR07 + NF01–NF03 Distinct Independent Contract Review

**Date:** 2026-11-15  
**Operation:** `TTM_SMALL4M_F2_IR01_IR02_IR07_NF01_NF03_DISTINCT_INDEPENDENT_SOURCE_DESIGN_REVIEW_SINGLE_GATE`  
**Repository/branch:** `minhtri22/TokenToModel-Lab` / `research/ttm-small4m-foundation-first-single-gate-20261115`.  
**Mode:** `READ_ONLY · SOURCE_ONLY · DESIGN_ONLY · NO_SCIENCE_EXECUTION · NO_REPOSITORY_WRITES`.  
**Failed previous exact candidate:** `cf0f459b54d0e91a7923e7a08b621d374e712e51`, independent verdict `HOLD_REVISE_DESIGN` with IR01/02/07 + NF01/02/03 still open. Historic `07adab...` HOLD also preserved.  
**Exact NEW candidate commit:** reviewer must use the **single commit given by owner**, parent `cf0f459b…`, that contains pinned blobs below. Never review a floating branch HEAD.

## 1. Exact sources to audit

| Source | Exact Git blob SHA-1 | Required reviewer action |
|---|---|---|
| `06_SM4M_F2_PROSPECTIVE_MEASUREMENT_PREEXEC_INTEGRATED_PROTOCOL_20261115.md` | `6b924e6e12a9bdf1e43e59ed4fd5bfae20f1f632` | Audit G04P vs G04E, visible gold parity, stage DAG and unchanged M0 |
| `07_SM4M_F2_PREEXEC_ADMISSION_SCORING_AND_CUSTODY_MATRIX_20261115.md` | `d83c713b1b9b94a9dff948e8a24d03aec82f5e70` | Audit machine-contract cross-record, first-error rank, G00–G12 and compound fixtures |
| `11_SM4M_F2_TYPED_PRIVATE_RECORD_SCHEMA_20261115.json` | `3540ef5904c303e72431e1bdbafe181f046b74fe` | Independently verify JSON Schema Draft2020-12, stage event conditional requirements, typed score rules and visible request fields |
| `12_SM4M_F2_IR01_IR02_IR07_NF01_NF03_AUTHOR_ADVERSARIAL_QA_20261115.md` | inspect exact commit | Check limits of author self-QA |
| Author schema QA JSON | `7b56b7f005059cdb3e2bbc2f02fafb466dc422ee` | Author-only 42/42 structural tests; **not** reference-schema science QA |
| Author integrated QA JSON | `399cb258731c0570bf6836908909ef1e788d7cbe` | Author-only 40/40 cross-contract tests; inspect negative case coverage |
| Updated F2 author design receipt | inspect exact commit | Verify no owner GO, scientific execution, semantic gold or scorer implemented |
| Latest independent HOLD report and receipt, archived at new candidate | inspect exact commit | Read all original+new findings, compare exact content/pins and original separate HOLD history |

**Frozen upstream:** MD1 source `33021a421f05bb3bfa0999ad12bc3bd144366da9` / blob `384d077600ed864a917fdd5e74b5a5bca0ed8766`, owner Foundation F01–F05 design closure `c233dff20b9b020aefd732ce62bfa2e7aebd3985`. Do not re-audit previously closed independent findings or rerun past science.

## 2. Substantive independent attack lanes

**IR01 HIGH + NF02 HIGH — valid stage sequence and lawful G04P proof.** Trace each S0–S5 transition under P and E gates. Before G12A, G04P may use **abstract Boolean/dependency/witness constraints only**, not actual narrative text, gold, core or hidden dataset. Determine whether this gives an adequate *design-level* per-stratum feasibility proof without overclaim. After owner G12A, G04E authoring+12 text-edge witnesses is the first real semantic evidence and independently QA must PASS before G12B. Verify no pre-G12A item is required and no owner permit is inferred from design GO. Challenge edge cases of stratum-level infeasibility and ambiguity.

**IR02 HIGH + NF01 HIGH — rater-visible source sufficiency.** Test whether `rater_visible_request` includes a stable story prefix, candidate continuation, canonical three-axis questions and rule version, such that every actor/object/goal gold 0/1 can be decided **using only that visible payload**. The private E_core ledger is not an answer key accessible only to gold adjudicators. Audit all reference frames, entity/time, UTF-8 spans, independent gold-first blind procedure, negative wording, unknown vs invalid, answer leakage via metadata, and the G04E/G05E HOLD on hidden-only witness. Do not infer real natural-text feasibility without an actual separate evidence packet.

**IR07 MEDIUM + NF03 MEDIUM — deterministic typed and cross-record contract.** Check all ten record types in JSON Schema 11 against an independent standard validator when possible (read-only tool); compare strict required/type/enum/nullable, extra fields and stage-specific requiredness. Audit foreign-key namespaces, 8-node/12-edge graph, 8/8/8 UNKNOWN per axis, score strict typing and source byte spans. Check canonical RFC8785 binding and whether record sorting, length-prefixing, UTF-8 handling and HMAC privacy are sufficient. Audit 16-rank first-error order, special score-type vs generic schema priority, runtime authorization-before-data rule, C01–C12 multi-fault oracle, N01–N28 remaining NOT_EXECUTED on actual scorer. Actively seek inconsistent or underspecified cases rather than ticking names.

**Compatibility, previously CLOSED_DESIGN:** IR03 compulsory NC1–NC6, IR04 3-class UNKNOWN and always-UNKNOWN fail, IR05 exploratory n and thresholds, IR06 rater isolation. Verify modified visible payload/JSON schema did not weaken any of them. No need to repeat full historic QA when unchanged.

**Challenge author QA:** 42/42 typed synthetic record tests and 40/40 document-contract checks are **same-agent** evidence. They cannot prove construct realizability, official JSON Schema implementation, actual rater competence, rights, proxy strength or science. If these checks miss a HIGH design defect, report it even if all 82 are green.

## 3. Expected diff and archive

Previous HEAD `cf0f459b…` to exact new candidate: only two modified Markdown (06/07) plus one modified author JSON; new 11 JSON Schema, 12 author QA report, 13 handoff, two author QA JSON receipts, and **two byte-preserved latest independent HOLD review artifacts** — expected **3 modified + 7 added**. Confirm MD1, F0/F1, F01–F05 closure, old receipts, `lineage.md` and science source/data unchanged. Archive original reviewer files without rewriting verdict:
- latest reviewer report raw-file SHA-256 `fb868874d9369a4876792bfe8cf793de17a12f3a91d606d8bb7e3bcdaee47808`; Git blob SHA-1 `c04b0f74b65f9680afdf04acc794593561cfdfac`
- latest reviewer receipt raw-file SHA-256 `13f298f31bc0ef4f8223bc284ec4b728c959e3a4d6d2ee7abf9793d56295e39a`; Git blob SHA-1 `39f67449d6e966bf54452fb3448a383fdf35eb85`

**Stop if exact source does not match** ⇒ `SOURCE_MISMATCH_HOLD`. Git SHA-1 and raw SHA-256 are different types of evidence. No hash should be invented.

## 4. Verdict and one-packet deliverables

Every previously open finding `IR01,IR02,IR07,NF01,NF02,NF03` must have explicit source, impact, residual risk and `CLOSED_DESIGN` or `HOLD_DESIGN`; any new gap gets a new ID. Source integrity PASS alone is not design PASS. An extension awaiting real data may be `PREEXEC_PENDING` if blocked correctly; it is not automatically a design defect.

**One final verdict only:** `GO_DESIGN_SCOPED` or `HOLD_REVISE_DESIGN`. GO is design-only and does **not** authorize any original M0, M0X, M0U, private authoring, scoring, scorer execution, model/GPU/TEST/FINAL use, F3/F4 or merge. A HOLD returns **one** integrated remediation list.

Create, hand directly to owner, **do not commit**:
1. `TTM_SMALL4M_F2_IR01_IR02_IR07_NF01_NF03_DISTINCT_REVIEW_20261115.md`
2. `TTM_SMALL4M_F2_IR01_IR02_IR07_NF01_NF03_DISTINCT_REVIEW_RECEIPT_20261115.json`

JSON should pin exact new commit/blob hashes, old HOLD sources, six open findings, 42/40 author QA limitations, G00–G12, final verdict, no-science/no-writes flags. Reviewer may only read source and run **non-science static schema analysis if available**; no gold, rater, proxy/model, corpus, scorer execution or write actions. 

**Current:** `ROOT_CAUSE_IDENTIFIED=NO; PREEXEC_BLOCK=TRUE; G12A_NOT_GRANTED; G12B_BLOCKED; OWNER_DATA_AUTHORING_GO=FALSE; OWNER_SCORE_GO=FALSE; F3/F4_NOT_OPENED; SCIENCE_HOLD; MERGE_NOT_AUTHORIZED`.

**Bước thực hiện tiếp theo — duy nhất:** return the independent one-packet GO/HOLD report to owner and stop.
