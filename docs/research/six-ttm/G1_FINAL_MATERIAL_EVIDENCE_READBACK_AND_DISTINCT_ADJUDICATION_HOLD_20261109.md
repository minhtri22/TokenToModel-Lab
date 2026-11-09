# G1 — Final material evidence readback, methodological blockers, distinct-review adjudication

**Date:** 2026-11-09  
**Request:** `TTM_SIX_XMODEL_G1_FINAL_MATERIAL_EVIDENCE_READBACK_AND_DISTINCT_SCIENCE_ADJUDICATION`  
**Final decision:** **`HOLD_G1_SCIENCE_NOT_AUTHORIZED`**. Scientific research was **NOT EXECUTED**. This is a readiness decision, not scientific FAIL or independent scientific PASS.

## 1. Boundary, frozen provenance and no side effects

Target repository: `minhtri22/TokenToModel-Lab`. Only branch `research/ttm-six-cross-model-representation-transfer-20261109` receives these notes and a new read-only verifier. `main` verified at `b57b44e7287f842e81050c1faee337f636333dd0`; PR #12 already merged by separate lane, not opened/changed by G1. `lineage.md`, scientific checkpoints, other SIX repository `minhtri22/CLDP`, and TTM training/validation/test data all unchanged by this task. Qwen3-0.6B prior one-shot technical PASS remains immutable and will not be rerun.

Existing G1 candidate prereg:
- `docs/research/six-ttm/G1_SCIENCE_PREREG_V1_CONTRACT_CANDIDATE_20261109.json` — Git blob `de049ba00331d90f3c7ae72ab3daf943c766ec82`;
- `docs/research/six-ttm/G1_SCIENCE_PREREG_V1_METHODS_AND_THRESHOLDS_20261109.md` — Git blob `9dcbf31b2835e07922b2aaf66e5895c7d2f8b03b`;
- `G1_INTEGRATED_ADMISSION_READINESS_DECISION_20261109.json` — earlier HOLD preserved; not retroactively changed.

## 2. New local evidence — exact T1 manifest FOUND, but not completely hashed

Using **read-only** connected RemoteDesktop, `machine-1` reported ONLINE and the exact Windows TTM workspace exists:
- `D:\WORK\RESEARCH\TokenToModel-Lab\_tmp\ttm_t1_real_source_v1\T1_STORY_SPLIT_IDS_NO_RAW_TEXT.json`: **FOUND**.
- `D:\WORK\RESEARCH\TokenToModel-Lab\datasets\tinystories_v1_original_pinned\TinyStories-train.txt`: **FOUND**.
- `...\TinyStories-valid.txt`: **FOUND**, but not read for G1.
- The original T1 JSON header returns schema `ttm.t1.real.stories.split.v1`, source `roneneldan/TinyStories`, revision `f54c09fd23315a6f9c86f9dc80f725de7d8f9c64`, license `CDLA-Sharing-1.0` and hash-only splits.

**Important tool limit:** RemoteDesktop `read_file` truncates this one-line JSON after ~20 KB. The sample was not complete, failed JSON parsing because it was truncated. `run_command` was tried with a read-only Python SHA command but rejected with `managed mode requires task_job_submit` **before execution**. Therefore `T1_MANIFEST_ACTUAL_FULL_BYTES_SHA=NOT_ATTESTED_THIS_TURN` and `T1_SPLIT_COUNTS_RECOMPUTED_THIS_TURN=NOT_EXECUTED`. Do not mislabel a file-presence observation as a full-manifest hash PASS. No source texts/TEST stories exported.

**New read-only PowerShell 5.1 verification** is now in research branch:
`scripts/research/six_ttm/Verify-G1-T1-Original-Manifest-ReadOnly-PS51.ps1` — frozen Git blob `b15a58b9aaa4d8cc6c7813bdbf4e1d825554c24d`.

Static checked: repository origin, exact manifest path, reparse-point rejection, actual SHA-256 `9f2ebaca821bddf0a9d7ae30ccfcef34561b968b21159aa913794298235a2fa9`, schema/source/rights/snapshot pin, all hashed IDs well formed and unique across 2,048 TRAIN / 256 VAL / 64 TEST (2,368 total). Emits **only sanitized console JSON**, reads no raw stories, makes no filesystem writes. **Not run on Windows yet; PS 5.1 parse/runtime is NOT VERIFIED.** This checks original T1 membership metadata only; it does **not** create G1 128/64/64 or read teacher tokenizers.

## 3. Critical method finding — the original T1 manifest contains content SHA, not row index

Fetched actual T1 producer code `tools/pilot_t1t3/t1_source_split_tokenizer.py` (main blob `3ef500ddd8259153e7e3d4602915a51b7060a40f`). Its `scan` computes `digest=sha(text.encode('utf-8'))` after parsing `<|endoftext|>`-delimited original stories and stripping outer whitespace; `build_manifest` emits `r['sha256']` for each split. It **does not export source row indices** or raw story strings.

Candidate G1 protocol, however, uses `(source_row_index, SHA256(NFC_story_UTF8))` for deterministic prefix selection. **Do not pretend that these keys are already resolved by the T1 manifest.** The G1 manifest producer must (after acceptance of source-rights/storage scope) stream the **pinned original TRAIN source only**, reapply the frozen T1 parser to match all 2,048 original SHA identities, derive row indices/text privately, generate eligible prefixes by both fixed Qwen tokenizers, then freeze the 128/64/64 split IDs and their prefix SHA. Must independently verify source SHA, zero missing/multiple mappings and no TTM original VAL/TEST story text access.

A complete private 256-prefix G1 manifest has **NOT** been generated or sealed; original T1 has not been mutated. Do not use raw contents or TEST labels for fit or tuning.

## 4. Qwen3-1.7B runtime gate — exact script present, execution receipt absent

- Source candidate: `Qwen/Qwen3-1.7B@70d244cc86ccca08cf5af4e1e306ecf908b1ad5e`, 28 layers, hidden width 2048, two weight shards.
- Published shard SHA-256 values pinned previously: `169ad53ec313c3a34b06c0809216e4fc072cce444a5d4ff2b59690d064130ed5` and `912becff8d60672aa8628ef08c05898d9adf17c2ad4ae3caf99b065622fdeff9`. These are **not actual downloaded bytes proven by Colab**.
- `scripts/research/six_ttm/g1_qwen17_zero_science_technical_readiness_v1.py` blob `1a815a5572136a93cd9a292705b75a8a17002a97`.
- `notebooks/six_ttm/TTM_SIX_G1_QWEN17_INTEGRATED_READINESS_PREFLIGHT_ONESHOT_SMOKE_20261109.ipynb` blob `3c807149ac16b1d08be3ba70ef57ff5ccf62c679`.
- Source-only static review from prior turn **PASS_16/16**; no Colab AST, actual preflight, download hash or hidden-state smoke receipt. Connected Google Drive search for `G1_TARGET17_SMOKE_RECEIPT`, `Qwen3-1.7B`, `TTM_SIX_G1` returned **no match** in accessible results. This is not proof a user-private Colab local receipt does not exist. State `QWEN17_COLAB_RUNTIME=NOT_ATTESTED`.
- **No G1 science execution or dataset use** is permitted by the technical notebook, even if its synthetic check later reports PASS.

## 5. Rights and governance gate

Hugging Face metadata identifies TinyStories dataset `CDLA-Sharing-1.0`, model weights Qwen `Apache-2.0`. The data license permits computational uses subject to its terms, but provenance/publication and derived-artifact treatment still need a recorded owner G1-scope acceptance, appropriate license/attribution, private raw-text and embedding handling. Technical T1 pilot rights acceptance **cannot be silently broadened** to G1. `G1_PRIVATE_COMPUTATIONAL_USE_OWNER_POLICY=NOT_RECORDED`; no corpus/data redistribution authorized or performed. This is a scope-of-use governance gate, **not a claim that CDLA bans research**.

## 6. Scientific-runner and negative-control audit: substantial blockers

Direct GitHub directory listing for `scripts/research/six_ttm` on the research branch shows only the Qwen0.6B technical runners, Qwen1.7B technical runner, and a T1 read-only verifier; **there is NO G1 science runner** to fit ridge A/P, calculate probe likelihoods, seal TEST, or compute the null/CI. Consequently `SCIENTIFIC_SOURCE_PIN_AND_LEAKAGE_NEGATIVE_QA=NOT_EXECUTED`, not PASS.

Independent-readiness methodology findings requiring resolution **before** the final science lock, without altering the frozen candidate v1 silently:

1. **ID mismatch:** T1 splits contain SHA identities; G1 prereg needs `source_row_index` and normalized prefix. A fixed source-matching producer and exact manifest QA are missing.
2. **Orthogonal-null fallacy:** A full-rank orthogonal rotation `sQ` with isotropic ridge and matched regularization is mathematically information-preserving (regularization invariant); it is **not** a meaningful negative control. Reclassify as *basis invariance / neutral diagnostic* or define a genuinely destructive independent null (e.g., permuted TRAIN pairs, already planned). Do not count random orthogonal rotation alone as scientific evidence against H0.
3. **Two-ridge linear composition:** `P(A(s))` is still a linear function of `s`. A PASS versus shuffle does not establish a distinct SIX mechanism. Report `B-direct s->r` fairly and avoid declaring SIX-specific superiority from G1.
4. **Token-boundary semantics:** concatenation of independently tokenized prefix IDs and continuation IDs is a precisely operational **token-sequence conditional score**, not necessarily identical to likelihood of the raw concatenated string under each model's tokenizer. Freeze the implementation and interpretation accordingly.
5. **Finite power:** 64 G1 TEST clusters do not establish confirmatory 80% power. Only a scoped feasibility conclusion is authorized if independently accepted; CKA/functional gates and positive-control validation must be checked before any transfer PASS claim.
6. **Failure modes:** zero-variance probe checks already defined in v1, but no code is present to enforce them. TEST must remain one-shot; do not make threshold/feature/probe changes after observing hidden responses.

## 7. Distinct independent adjudication was sought but cannot be falsely reported

Prior anti-adversarial review `G1_SCIENCE_PREREG_V1_ADVERSARIAL_REVIEW_AND_INDEPENDENT_REVIEW_PACKET_20261109.md` is from the **same authoring assistant**, not distinct reviewer. This turn attempted available Notion Custom-Agent reviewer discovery; the provider returned `entitlement_required` (Notion Business or higher) and **did not execute** a reviewer. No accessible separate Codex subagent invocation capability was supplied for this turn. Therefore:
- `DISTINCT_REVIEW_SOURCE_READBACK=NOT_EXECUTED`
- `DISTINCT_SCIENCE_ADJUDICATION=NOT_RECEIVED`
- `INDEPENDENT_REVIEW_PASS=NOT_CLAIMED`.

A true distinct reviewer should read the **exact pinned** candidate JSON, methods document, prior review packet, this report and the future full T1+G1 manifest / Qwen1.7B receipt / science runner. Required disposition: `PASS`, `HOLD` or `FAIL` per evidence, critique of the above five methodological issues, explicit conditions, timestamp/identity, and **no scientific run** merely by signing review.

## 8. Unified science decision (not a chain of micro-permits)

| Material gate | Result this turn |
|---|---|
| Exact project / provenance readback | PASS_SCOPE; verified local path and GitHub source/metadata |
| Full original T1 manifest byte hash + membership | SOURCE_FOUND / FULL_HASH_PENDING |
| Owner G1 data-rights/private-output acceptance | HOLD |
| G1 128/64/64 eligible prefix manifest SHA and TEST seal | HOLD_NOT_CREATED |
| Qwen3-0.6B technical one-shot | PASS_PRESERVED / NO_RERUN |
| Qwen3-1.7B actual weight SHA, Tensor/VRAM smoke | HOLD_NOT_EXECUTED |
| G1 science runner source, deterministic split QA, negative-control QA | HOLD_NOT_IMPLEMENTED |
| Reviewer genuinely separate from author | HOLD_NOT_AVAILABLE |
| G1 science permit | **NOT_GRANTED** |
| Training TTM, G3, editing `main`, PR#12 or `lineage.md` | **NO_ACTION** |

**Final:** `G1_ADMISSION_HOLD_MATERIAL`. No G1 SCIENCE PASS or FAIL, since no one-shot science experiment occurred.

## 9. One integrated evidence-completion batch, not many permits

Collect *one* evidence packet with (a) user-approved G1 private computational-scope statement and verified SHA of original T1 manifest plus source-to-identity mapper; (b) exact sealed 128/64/64 eligibility manifest and no TTM TEST story access; (c) the existing Qwen1.7B notebook's preflight/synthetic smoke receipts with exact source+weight hashes; (d) pinned G1 science runner / leak-negative QA; and (e) a genuinely independent review signed against these exact bytes. Then adjudicate once: `AUTHORIZE_G1_SCIENCE_ONE_SHOT` only if all mandatory gates PASS; else retain `HOLD`. No rerun Qwen0.6B or TTM training.

**Bước thực hiện tiếp theo:** `TTM_SIX_XMODEL_G1_SINGLE_EVIDENCE_PACK_T1_MANIFEST_QWEN17_SCIENCE_RUNNER_AND_EXTERNAL_REVIEW`, then one integrated independent science lock decision.
