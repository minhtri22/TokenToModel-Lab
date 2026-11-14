# TTM — Global branch evidence QA & research priority (14/11/2026)

**Operation:** `TTM_GLOBAL_UNVERIFIED_BRANCH_EVIDENCE_QA_AND_RESEARCH_PRIORITY_SINGLE_GATE`  
**Main pin:** `fbe4a1ed58eef66f896bbfe0471926b7cc45298e`  
**Scope:** GitHub exact HEAD and lineage/source review only; no new science/GPU/TEST or code merge.

## Kiểm toán snapshot và giới hạn

- GitHub current **65 branches**; previous snapshot 64; original **57 UNVERIFIED included main**. **56 non-main branches** were the actual prior-unknown set.
- 23 branch-specific exact source artifacts, 4 branch-local lineage verdict pins; remaining unverifiable terminal source states retain UNVERIFIED.
- 6 branches have no unique difference because they are ancestors of main; that is not scientific PASS.
- 3 open PRs were Draft: #13, #14, #18. No PR was merged or opened in this audit.
- All 56 prior unverified non-main branch lineage files were examined at exact HEAD; source HEAD and main ancestry were compared. No model/checker/history run was repeated.
- PASS/FAIL/HOLD represent scoped evidence statuses, independent of branch merge eligibility. Readback is not independent scientific validation.

## Ma trận quyết định ưu tiên

| Ưu tiên | Hướng | Bằng chứng | Khuyến nghị | Trạng thái |
|---|---|---|---|---|
| P1 | T5 + T6 inference technical | T5 Ollama custom child raw-logits 4/4 scoped; GELU_ERF test 4/4; T6 already merged | Prioritize documentation of reproducible CPU baseline/rights; no broad parity or stock Ollama claim | `DOCS_ONLY_REVIEW` |
| P1 | EmbeddingGemma 2 residual transport | OOD256 independent PASS_SCOPED; A0E distinct path NO_GO_HOLD | Prospective semantic-vs-geometry independent design; no reuse of consumed OOD as new confirmatory | `DESIGN_ONLY_NOT_OPENED` |
| P1 | Docs model card, data rights (PR #14) | Source QA static scoped; license/legal verification not proven | Review docs-only changes and rights language for possible separate owner merge | `DRAFT_REVIEW_CANDIDATE` |
| P2 | Vector Memory V4 R8 | R7 failed marker shortcut; R8 G0/G1/G2 HOLD | Resolve F02/F03, owner attestation, custodian as one integrated packet only if owner prioritizes | `HOLD` |
| P2 | H-DATA-S1 | NEW FINAL24 owner unblind: no demonstrated scoped semantic benefit | Archive negative outcome, evaluate FAIL4 hypothesis as new design only | `NO_NEW_RUN` |
| P2 | P07 GPU kernel | PyTorch XPU compute PASS; one-shot 6 GiB budget exceeded; compiler/direct-page not executed | Retain paused until owner capacity/backend decision; no automatic rerun | `PAUSED_HOLD` |
| P2 | Q1/Q2 quality | V2 partial 5/74; Q2 0/24, quality NOT_ADJUDICATED | No new inference or unseal; maintain sealed | `HOLD` |
| P3 | R2A/R3A/O0/CF1 | Validator/scoping failures; R3A shortcut; O0 N1 FAIL; CF1 DEV36 0/36 | Archive failures, no reused blind FINAL or superficial shortcuts | `ARCHIVE_NEGATIVE` |
| P3 | TTM × SIX G1 | Original G1 science HOLD, real Qwen exploratory no signal | Archive original G1; any successor requires new prereg and owner choice | `HOLD_ARCHIVE` |
| P3 | D1 Bridge R1 | GO_CLOSE_DESIGN_ONLY already merged L0022 | Benchmark redesign with six verbs/clock/events is a proposal, not authorized | `CLOSED_DESIGN_HOLD` |

## Cổng merge

- **Không có nhánh mã nghiên cứu mới đủ gate merge trong lượt này.** A scoped research PASS (ví dụ EmbeddingGemma OOD256) không phải QA merge.
- PR #14 and PR #18 are documentation review candidates, still Draft and not automatically mergeable as a governance decision; PR #13 remains quality HOLD.
- Các branch `ANCESTOR_IN_MAIN_NO_DIFF` không có delta để merge. Branch D1 evidence code is closed at R1 design HOLD; do not merge source into main.

## Toàn bộ nhánh: evidence / gate / merge

| Nhánh (HEAD 12) | Family | Gate từ nguồn / phạm vi | Quan hệ main | Merge |
|---|---|---|---|---|
| `archive/p01-d1-prereg-draft-20261108` (`b25a858cb039`) | P01_DATA_SECURITY | `P01_D1_I0A_PREAUTH_HOLD_ACL` | DIVERGED_FROM_MAIN | `NO_CODE_MERGE_AUTHORIZED` |
| `archive/p01-i0a-f0-static-side-20261108` (`b793191932d7`) | P01_DATA_SECURITY | `UNVERIFIED_BRANCH_SCIENCE_QA` | DIVERGED_FROM_MAIN | `NO_CODE_MERGE_AUTHORIZED` |
| `archive/p01-legacy-f1-wp30-lineage-20261108` (`a4317b3546cb`) | P01_DATA_SECURITY | `UNVERIFIED_BRANCH_SCIENCE_QA` | DIVERGED_FROM_MAIN | `NO_CODE_MERGE_AUTHORIZED` |
| `archive/ttm-ollama-full-logits-scoped-20261111` (`99ca9eee4114`) | T5_INFERENCE | `PASS_SCOPED_OLLAMA_CHILD_FULL_RAW_LOGITS_4_OF_4` | DIVERGED_FROM_MAIN | `NO_CODE_MERGE_AUTHORIZED` |
| `archive/ttm-t5-windows-f32-evidence-20261111` (`64b7bd8e764a`) | T5_INFERENCE | `NO_UNMERGED_DIFF; HISTORIC_QA_NOT_REVALIDATED` | ANCESTOR_IN_MAIN_NO_DIFF | `NO_MERGE_NEEDED` |
| `codex/ttm-r2a-adversarial-review-20261111` (`dbf2c5389358`) | R2_R3_O0_CF1 | `R2A_FIXTURE_PASS_36_OF_36; VALIDATOR_FAIL_SCOPED; SCIENCE_HOLD` | DIVERGED_FROM_MAIN | `NO_CODE_MERGE_AUTHORIZED` |
| `codex/ttm-small4m-fresh12-independent-review-20261110` (`a4bdfee7ca9e`) | QUALITY_CONTINUATION | `UNVERIFIED_BRANCH_SCIENCE_QA` | DIVERGED_FROM_MAIN | `NO_CODE_MERGE_AUTHORIZED` |
| `docs/ttm-small4m-model-card-dataset-rights-20261109` (`3ae00b45d094`) | DOCUMENTATION_GOVERNANCE | `PASS_SCOPED_DOCS_SOURCE_QA; DATA_RIGHTS_NOT_RELEASED` | DIVERGED_FROM_MAIN | `DOCS_PR_REVIEW_CANDIDATE_NOT_APPROVED` |
| `evidence/ttm-cf1-step1024-dev36-once-20261111` (`cf6a37e5e970`) | R2_R3_O0_CF1 | `UNVERIFIED_BRANCH_SCIENCE_QA` | DIVERGED_FROM_MAIN | `NO_CODE_MERGE_AUTHORIZED` |
| `evidence/ttm-small4m-d1-r1-32typed-source-qa-20261114` (`1394e0abe3ea`) | D1_R1_FC01 | `R1_CLOSED_HOLD_PER_MAIN_L0022; BRANCH_SPECIFIC_QA_NOT_RECHECKED` | DIVERGED_FROM_MAIN | `NO_CODE_MERGE_AUTHORIZED` |
| `evidence/ttm-small4m-d1-r1-action-causal-single-amendment-20261114` (`971f50c29e7b`) | D1_R1_FC01 | `R1_CLOSED_HOLD_PER_MAIN_L0022; BRANCH_SPECIFIC_QA_NOT_RECHECKED` | DIVERGED_FROM_MAIN | `NO_CODE_MERGE_AUTHORIZED` |
| `evidence/ttm-small4m-d1-r1-final-closure-lineage-20261114` (`53f1c355563a`) | D1_R1_FC01 | `R1_CLOSED_HOLD_PER_MAIN_L0022; BRANCH_SPECIFIC_QA_NOT_RECHECKED` | DIVERGED_FROM_MAIN | `NO_CODE_MERGE_AUTHORIZED` |
| `evidence/ttm-small4m-d1-r1-minimal-semantic-constructive-hold-20261114` (`49513729b189`) | D1_R1_FC01 | `R1_CLOSED_HOLD_PER_MAIN_L0022; BRANCH_SPECIFIC_QA_NOT_RECHECKED` | DIVERGED_FROM_MAIN | `NO_CODE_MERGE_AUTHORIZED` |
| `evidence/ttm-small4m-d1-r1-ontology-feasibility-hold-20261114` (`d24c50ad8a9e`) | D1_R1_FC01 | `R1_CLOSED_HOLD_PER_MAIN_L0022; BRANCH_SPECIFIC_QA_NOT_RECHECKED` | DIVERGED_FROM_MAIN | `NO_CODE_MERGE_AUTHORIZED` |
| `evidence/ttm-small4m-d1-v6-r1r3-integrated-custody-32skeleton-20261114` (`553f1d6db9c2`) | D1_R1_FC01 | `R1_CLOSED_HOLD_PER_MAIN_L0022; BRANCH_SPECIFIC_QA_NOT_RECHECKED` | DIVERGED_FROM_MAIN | `NO_CODE_MERGE_AUTHORIZED` |
| `evidence/ttm-t5-isolated-llama-cpu-qa-20261110` (`64b7bd8e764a`) | T5_INFERENCE | `NO_UNMERGED_DIFF; HISTORIC_QA_NOT_REVALIDATED` | ANCESTOR_IN_MAIN_NO_DIFF | `NO_MERGE_NEEDED` |
| `evidence/ttm-vm-v4-r7-prospective-single-gate-20261114` (`aa529e207409`) | VECTOR_MEMORY | `FAIL_MARKER_SHORTCUT_HOLD_SCIENCE` | DIVERGED_FROM_MAIN | `NO_CODE_MERGE_AUTHORIZED` |
| `evidence/ttm-vm-v4-r8-g0-f01-f03-single-closure-20261114` (`12540962e96c`) | VECTOR_MEMORY | `R8_G0_HOLD_G1_HOLD_G2_HOLD_INTEGRATED` | DIVERGED_FROM_MAIN | `NO_CODE_MERGE_AUTHORIZED` |
| `evidence/ttm-vm-v4-r8-v4-integrated-closure-20261114` (`53c987be529f`) | VECTOR_MEMORY | `R8_G0_HOLD_G1_HOLD_G2_HOLD_INTEGRATED` | DIVERGED_FROM_MAIN | `NO_CODE_MERGE_AUTHORIZED` |
| `experiment/ttm-six-g1-tiny-real-qwen-poc-20261110` (`c0b5239862ce`) | SIX_TTM | `UNVERIFIED_BRANCH_SCIENCE_QA` | DIVERGED_FROM_MAIN | `NO_CODE_MERGE_AUTHORIZED` |
| `feature/p07-paged-attention-kernel-design-20261107` (`06b047856a84`) | T6_P07_P08 | `P07_XPU_PASS_SCOPED; OVERALL_FAIL_OR_INCONCLUSIVE_NO_AUTORERUN` | DIVERGED_FROM_MAIN | `NO_CODE_MERGE_AUTHORIZED` |
| `feature/ttm-t6-dense-paged-ab-benchmark-fixture-20261109` (`0ebd59755b41`) | T6_P07_P08 | `NO_UNMERGED_DIFF; HISTORIC_QA_NOT_REVALIDATED` | ANCESTOR_IN_MAIN_NO_DIFF | `NO_MERGE_NEEDED` |
| `governance/train-first-colab-and-branch-consolidation-20261108` (`706911a9048c`) | DOCUMENTATION_GOVERNANCE | `NO_UNMERGED_DIFF; HISTORIC_QA_NOT_REVALIDATED` | ANCESTOR_IN_MAIN_NO_DIFF | `NO_MERGE_NEEDED` |
| `governance/ttm-global-lineage-append-only-r1-closure-20261114` (`c6b3ec442eb7`) | DOCUMENTATION_GOVERNANCE | `PR19_MERGED_DOCS_ONLY_SOURCE_BRANCH` | ANCESTOR_OF_MAIN_PR19_MERGED | `NO_MERGE_NEEDED` |
| `governance/ttm-parallel-workstreams-review-20261109` (`94aaced34335`) | DOCUMENTATION_GOVERNANCE | `UNVERIFIED_BRANCH_SCIENCE_QA` | DIVERGED_FROM_MAIN | `NO_CODE_MERGE_AUTHORIZED` |
| `governance/ttm-t6-postmerge-p07-p08-readiness-20261114` (`d023dd16f4c0`) | T6_P07_P08 | `T6_CLOSED_MERGED_SCOPED; P07_PAUSED; P08_NOT_OPENED` | DIVERGED_FROM_MAIN | `DOCS_PR_REVIEW_CANDIDATE_NOT_APPROVED` |
| `implementation/ttm-six-g1-preexec-admission-candidate-20261109` (`51636a3187ed`) | SIX_TTM | `UNVERIFIED_BRANCH_SCIENCE_QA` | DIVERGED_FROM_MAIN | `NO_CODE_MERGE_AUTHORIZED` |
| `implementation/ttm-six-g1-production-gates-methods-v1e-20261110` (`a319a6e5487d`) | SIX_TTM | `G1_SCIENCE_LOCK_HOLD; METHODS_REVIEW_HOLD` | DIVERGED_FROM_MAIN | `NO_CODE_MERGE_AUTHORIZED` |
| `implementation/ttm-six-g1-trusted-runtime-witness-20261109` (`81795e794550`) | SIX_TTM | `UNVERIFIED_BRANCH_SCIENCE_QA` | DIVERGED_FROM_MAIN | `NO_CODE_MERGE_AUTHORIZED` |
| `main` (`fbe4a1ed58ee`) | OTHER_TTM | `MAIN_GOVERNANCE_BASELINE; D1_R1_CLOSED_HOLD` | CANONICAL_MAIN | `NO_MERGE_NEEDED` |
| `planning/ttm-six-g1-original-single-batch-provision-20261110` (`5ef0a7467600`) | SIX_TTM | `UNVERIFIED_BRANCH_SCIENCE_QA` | DIVERGED_FROM_MAIN | `NO_CODE_MERGE_AUTHORIZED` |
| `research/six-ttm4m-three-arm-exploratory-archive-20261110` (`1d6e73ecf15d`) | SIX_TTM | `EXPLORATORY_NO_CLEAR_GAIN; G1_SCIENCE_HOLD` | DIVERGED_FROM_MAIN | `NO_CODE_MERGE_AUTHORIZED` |
| `research/ttm-gemini-embedding2-gqa-pagedattention-feasibility-design-20261108` (`a41d268e1a88`) | EMBEDDING | `PASS_RGOLD_SCREEN_SCOPED_SYNTHETIC; NOT_GENERAL_RETRIEVAL` | DIVERGED_FROM_MAIN | `NO_CODE_MERGE_AUTHORIZED` |
| `research/ttm-gemma2-token-alignment-pretraining-causality-20261111` (`2583dadc254a`) | EMBEDDING | `A0E_NO_GO_HOLD; OOD256_PASS_SCOPED_IN_SEPARATE_TRACK` | DIVERGED_FROM_MAIN | `NO_CODE_MERGE_AUTHORIZED` |
| `research/ttm-gpt2-llama4-philosophy-architecture-round1-20261110` (`fe3e2851019f`) | ARCHITECTURE | `AUTHOR_SOURCE_QA_PASS_18_OF_18; SCIENCE_HOLD` | DIVERGED_FROM_MAIN | `NO_CODE_MERGE_AUTHORIZED` |
| `research/ttm-hdata-s1-fail4-prospective-mechanism-design-20261114` (`33021a421f05`) | H_DATA | `H_DATA_S1_NO_DEMONSTRATED_SCOPED_SEMANTIC_BENEFIT; FAIL4_DESIGN_ONLY` | DIVERGED_FROM_MAIN | `NO_CODE_MERGE_AUTHORIZED` |
| `research/ttm-o0-n1-failed-gates-natural-narrative-redirect-20261111` (`81c08f99af0d`) | R2_R3_O0_CF1 | `O0_N1_FAIL_SCOPED; NO_UNBLIND; NEURAL_EXECUTION_HOLD` | DIVERGED_FROM_MAIN | `NO_CODE_MERGE_AUTHORIZED` |
| `research/ttm-o0-narrative-cf1-source-scorer-blind-readiness-20261111` (`f2ce247bced6`) | R2_R3_O0_CF1 | `UNVERIFIED_BRANCH_SCIENCE_QA` | DIVERGED_FROM_MAIN | `NO_CODE_MERGE_AUTHORIZED` |
| `research/ttm-o0-only-neural-feasibility-diagnostic-design-20261111` (`6497699a13e4`) | R2_R3_O0_CF1 | `UNVERIFIED_BRANCH_SCIENCE_QA` | DIVERGED_FROM_MAIN | `NO_CODE_MERGE_AUTHORIZED` |
| `research/ttm-r3-structural-state-tracing-design-20261111` (`cd3dc4ceb3a4`) | R2_R3_O0_CF1 | `UNVERIFIED_BRANCH_SCIENCE_QA` | DIVERGED_FROM_MAIN | `NO_CODE_MERGE_AUTHORIZED` |
| `research/ttm-r3a-adversarial-independent-review-20261111` (`815541c6f8ed`) | R2_R3_O0_CF1 | `R3A_384_REPLAY_PASS; GRAPH_REASONING_SHORTCUT_FAIL_SCOPED` | DIVERGED_FROM_MAIN | `NO_CODE_MERGE_AUTHORIZED` |
| `research/ttm-r3a-antishortcut-amendment-20261111` (`81327724c087`) | R2_R3_O0_CF1 | `UNVERIFIED_BRANCH_SCIENCE_QA` | DIVERGED_FROM_MAIN | `NO_CODE_MERGE_AUTHORIZED` |
| `research/ttm-six-cross-model-representation-transfer-20261109` (`d5d0c5346a59`) | SIX_TTM | `UNVERIFIED_BRANCH_SCIENCE_QA` | DIVERGED_FROM_MAIN | `NO_CODE_MERGE_AUTHORIZED` |
| `research/ttm-six-functional-transfer-ttm4m-three-arm-design-20261110` (`d13d2d6c98cd`) | SIX_TTM | `UNVERIFIED_BRANCH_SCIENCE_QA` | DIVERGED_FROM_MAIN | `NO_CODE_MERGE_AUTHORIZED` |
| `research/ttm-six-g1-exploratory-public-dev-20261110` (`a48e423c07c8`) | SIX_TTM | `EXPLORATORY_NO_SIGNAL; ORIGINAL_G1_SCIENCE_HOLD` | DIVERGED_FROM_MAIN | `NO_CODE_MERGE_AUTHORIZED` |
| `research/ttm-small4m-d1-v6-r1r3-integrated-source-qa-20261114` (`b5dd5890b73a`) | D1_R1_FC01 | `R1_CLOSED_HOLD_PER_MAIN_L0022; BRANCH_SPECIFIC_QA_NOT_RECHECKED` | DIVERGED_FROM_MAIN | `NO_CODE_MERGE_AUTHORIZED` |
| `research/ttm-small4m-embeddinggemma2-ood-design-20261111` (`d4550cb9c881`) | EMBEDDING | `PASS_SCOPED_OOD_RESIDUAL_TRANSPORT` | DIVERGED_FROM_MAIN | `NO_CODE_MERGE_AUTHORIZED` |
| `research/ttm-small4m-embeddinggemma2-token-swap-minimal-proof-20261109` (`13820a972c99`) | EMBEDDING | `UNVERIFIED_BRANCH_SCIENCE_QA` | DIVERGED_FROM_MAIN | `NO_CODE_MERGE_AUTHORIZED` |
| `research/ttm-small4m-fact-conditioning-data-objective-capacity-design-20261112` (`6023ed90612e`) | D1_R1_FC01 | `FC01_PASS_SCOPED_EXPLORATORY; D1_CONFIRMATORY_HOLD` | DIVERGED_FROM_MAIN | `NO_CODE_MERGE_AUTHORIZED` |
| `research/ttm-small4m-h-data-s1-matched-budget-prereg-20261113` (`ef4cc05037f9`) | H_DATA | `H_DATA_S1_NO_DEMONSTRATED_SCOPED_SEMANTIC_BENEFIT_FROM_BRANCH_LINEAGE` | DIVERGED_FROM_MAIN | `NO_CODE_MERGE_AUTHORIZED` |
| `research/ttm-small4m-post-cf1-language-fresh-gap-reconcile-20261111` (`8c393092a5bf`) | R2_R3_O0_CF1 | `UNVERIFIED_BRANCH_SCIENCE_QA` | DIVERGED_FROM_MAIN | `NO_CODE_MERGE_AUTHORIZED` |
| `research/ttm-small4m-post-final24-negative-archive-hypotheses-20261112` (`37165ce6eea0`) | QUALITY_CONTINUATION | `HDEC_REPETITION_CANDIDATE_PASS; SEMANTIC_GAIN_NOT_DEMONSTRATED` | DIVERGED_FROM_MAIN | `NO_CODE_MERGE_AUTHORIZED` |
| `research/ttm-small4m-prompt-adherence-continuation-design-20261111` (`0ec28d44587f`) | QUALITY_CONTINUATION | `FRESH16_V2_FAIL_SCOPED_FROM_BRANCH_LINEAGE` | DIVERGED_FROM_MAIN | `NO_CODE_MERGE_AUTHORIZED` |
| `research/ttm-small4m-prompt-conditioning-objective-design-20261110` (`16d00b23d919`) | QUALITY_CONTINUATION | `FINAL24_SEMANTIC_ADHERENCE_FAIL_SCOPED_FROM_BRANCH_LINEAGE` | DIVERGED_FROM_MAIN | `NO_CODE_MERGE_AUTHORIZED` |
| `research/ttm-small4m-q1q2-quality-single-batch-20261109` (`72cbf73c3adb`) | Q1Q2 | `Q1Q2_HOLD_INCOMPLETE; QUALITY_NOT_ADJUDICATED` | DIVERGED_FROM_MAIN | `NO_CODE_MERGE_AUTHORIZED` |
| `research/ttm-small4m-semantic-state-goal-toy-r2-20261110` (`c85b2ab50495`) | R2_R3_O0_CF1 | `UNVERIFIED_BRANCH_SCIENCE_QA` | DIVERGED_FROM_MAIN | `NO_CODE_MERGE_AUTHORIZED` |
| `research/ttm-small-4m-colab-pilot-prereg-20261108` (`ad9999019dd2`) | OTHER_TTM | `NO_UNMERGED_DIFF; HISTORIC_QA_NOT_REVALIDATED` | ANCESTOR_IN_MAIN_NO_DIFF | `NO_MERGE_NEEDED` |
| `research/ttm-t5-f32-strict-logit-parity-diagnostic-20261109` (`45918caed31a`) | T5_INFERENCE | `NO_UNMERGED_DIFF; HISTORIC_QA_NOT_REVALIDATED` | ANCESTOR_IN_MAIN_NO_DIFF | `NO_MERGE_NEEDED` |
| `research/ttm-t5-ollama-full-logits-20261111` (`99ca9eee4114`) | T5_INFERENCE | `PASS_SCOPED_OLLAMA_CHILD_FULL_RAW_LOGITS_4_OF_4` | DIVERGED_FROM_MAIN | `NO_CODE_MERGE_AUTHORIZED` |
| `research/ttm-vector-memory-architecture-20261111` (`b7788337bd98`) | VECTOR_MEMORY | `UNVERIFIED_BRANCH_SCIENCE_QA` | DIVERGED_FROM_MAIN | `NO_CODE_MERGE_AUTHORIZED` |
| `review/ttm-cf1-dev36-one-shot-scoped-science-adjudication-20261111` (`d725c39094a5`) | R2_R3_O0_CF1 | `CF1_DEV36_CONTEXT_SWITCHING_FAIL_SCOPED_0_OF_36` | DIVERGED_FROM_MAIN | `NO_CODE_MERGE_AUTHORIZED` |
| `review/ttm-r3-adversarial-latest-write-20261111` (`d641e1577eae`) | R2_R3_O0_CF1 | `UNVERIFIED_BRANCH_SCIENCE_QA` | DIVERGED_FROM_MAIN | `NO_CODE_MERGE_AUTHORIZED` |
| `review/ttm-six-g1-v1c-codex-distinct-20261109` (`d478282e16a4`) | SIX_TTM | `UNVERIFIED_BRANCH_SCIENCE_QA` | DIVERGED_FROM_MAIN | `NO_CODE_MERGE_AUTHORIZED` |
| `review/ttm-six-g1-v1e-codex-distinct-owner-import-20261110` (`365c352daee2`) | SIX_TTM | `UNVERIFIED_BRANCH_SCIENCE_QA` | DIVERGED_FROM_MAIN | `NO_CODE_MERGE_AUTHORIZED` |
| `review/ttm-six-g1-windows-distinct-20261110` (`efbbc1fddfd6`) | SIX_TTM | `UNVERIFIED_BRANCH_SCIENCE_QA` | DIVERGED_FROM_MAIN | `NO_CODE_MERGE_AUTHORIZED` |

## Bảo toàn và QA scope

Đọc receipt từ GitHub đủ để ghi một phán quyết đã được *báo cáo*, không làm lại thí nghiệm hoặc độc lập xác nhận khoa học. Những nhánh chưa có terminal result được chứng nhận vẫn `UNVERIFIED_BRANCH_SCIENCE_QA`; ma trận này không thay thế review độc lập theo branch.

`D1_BRIDGE_SCIENCE=HOLD`, `D1_R1=CLOSED_HOLD`, `TEST_Q1Q2=SEALED`, `FC02=NOT_OPENED`, `GPU=0`, `TRAINING=0`, `INFERENCE=0`, `FROZEN_V6=UNCHANGED`. Benchmark redesign remains `DESIGN_PROPOSAL_NOT_AUTHORIZED`.
