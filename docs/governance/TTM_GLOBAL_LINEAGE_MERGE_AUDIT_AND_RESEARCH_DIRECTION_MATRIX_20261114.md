# TTM — Kiểm toán hợp nhất lineage và ma trận hướng nghiên cứu

Ngày: 2026-11-14. Main source: `593455c9c7472042c691e0b3c69a74433c767fc7`. R1 closure: `53f1c355563a9aa30d7fe1aa4b76b694513a2c4e`.

## Quy tắc

- `lineage.md` chỉ nối thêm L0015–L0028; byte của L0000–L0014 không thay.
- Sao nguyên byte hai artifact phản biện R1 và receipt custody từ evidence; các source branch khác không merge.
- Source-local L0015… trên VM / Gemma / H-DATA có nội dung khác nhau: giữ theo source SHA, không nhận nhầm.
- PASS/FAIL/HOLD là trạng thái kết quả nghiên cứu theo nguồn; không phải quyết định merge. Nhánh không được kiểm chứng: `UNVERIFIED_CURRENT_GATE`.

## Ma trận ưu tiên

| Hướng | Mức chứng cứ | Trạng thái | Quyết định |
|---|---|---|---|
| D1 R1 | closure review + 11/11 source SHA | CLOSED_DESIGN_HOLD | Chỉ lưu lineage; redesign chưa được phép mở |
| Vector Memory | source lineage + R8 reviewer | PASS/FAIL lịch sử; R8 HOLD | Không merge khoa học |
| EmbeddingGemma 2 | OOD256 reviewer | PASS_SCOPED | Chưa có branch merge QA |
| H-DATA-S1 | L0034–L0035 nguồn | NO_DEMONSTRATED_SCOPED_SEMANTIC_BENEFIT | Lưu kết quả âm tính |
| FINAL24/H-DEC | L0015–L0016 nguồn | FAIL prompt adherence scoped | Lưu kết quả âm tính |
| T6/P07/P08 | main merge + PR #18 governance | T6 CLOSED; P07 PAUSED; P08 NOT_OPENED | Không tự mở P07 |
| Các nhánh còn lại | HEAD metadata | UNVERIFIED | Không merge |

## Bảng toàn bộ nhánh

| Nhánh | HEAD | Nhóm | Gate | Merge mã |
|---|---|---|---|
| `archive/p01-d1-prereg-draft-20261108` | `b25a858cb039` | OTHER | UNVERIFIED_CURRENT_GATE | HOLD |
| `archive/p01-i0a-f0-static-side-20261108` | `b793191932d7` | OTHER | UNVERIFIED_CURRENT_GATE | HOLD |
| `archive/p01-legacy-f1-wp30-lineage-20261108` | `a4317b3546cb` | OTHER | UNVERIFIED_CURRENT_GATE | HOLD |
| `archive/ttm-ollama-full-logits-scoped-20261111` | `99ca9eee4114` | OTHER | UNVERIFIED_CURRENT_GATE | HOLD |
| `archive/ttm-t5-windows-f32-evidence-20261111` | `64b7bd8e764a` | OTHER | UNVERIFIED_CURRENT_GATE | HOLD |
| `codex/ttm-r2a-adversarial-review-20261111` | `dbf2c5389358` | OTHER | UNVERIFIED_CURRENT_GATE | HOLD |
| `codex/ttm-small4m-fresh12-independent-review-20261110` | `a4bdfee7ca9e` | OTHER | UNVERIFIED_CURRENT_GATE | HOLD |
| `docs/ttm-small4m-model-card-dataset-rights-20261109` | `3ae00b45d094` | OTHER | UNVERIFIED_CURRENT_GATE | HOLD |
| `evidence/ttm-cf1-step1024-dev36-once-20261111` | `cf6a37e5e970` | OTHER | UNVERIFIED_CURRENT_GATE | HOLD |
| `evidence/ttm-small4m-d1-r1-32typed-source-qa-20261114` | `1394e0abe3ea` | D1_R1 | UNVERIFIED_CURRENT_GATE | HOLD |
| `evidence/ttm-small4m-d1-r1-action-causal-single-amendment-20261114` | `971f50c29e7b` | D1_R1 | UNVERIFIED_CURRENT_GATE | HOLD |
| `evidence/ttm-small4m-d1-r1-final-closure-lineage-20261114` | `53f1c355563a` | D1_R1 | GO_CLOSE_R1_FORMULATION_DESIGN_ONLY; D1_BRIDGE_SCIENCE=HOLD | HOLD |
| `evidence/ttm-small4m-d1-r1-minimal-semantic-constructive-hold-20261114` | `49513729b189` | D1_R1 | UNVERIFIED_CURRENT_GATE | HOLD |
| `evidence/ttm-small4m-d1-r1-ontology-feasibility-hold-20261114` | `d24c50ad8a9e` | D1_R1 | UNVERIFIED_CURRENT_GATE | HOLD |
| `evidence/ttm-small4m-d1-v6-r1r3-integrated-custody-32skeleton-20261114` | `553f1d6db9c2` | D1_R1 | UNVERIFIED_CURRENT_GATE | HOLD |
| `evidence/ttm-t5-isolated-llama-cpu-qa-20261110` | `64b7bd8e764a` | OTHER | UNVERIFIED_CURRENT_GATE | HOLD |
| `evidence/ttm-vm-v4-r7-prospective-single-gate-20261114` | `aa529e207409` | VM | UNVERIFIED_CURRENT_GATE | HOLD |
| `evidence/ttm-vm-v4-r8-g0-f01-f03-single-closure-20261114` | `8e857415c2ac` | VM | R8 G0 HOLD; G1 HOLD; G2 HOLD | HOLD |
| `evidence/ttm-vm-v4-r8-v4-integrated-closure-20261114` | `53c987be529f` | VM | UNVERIFIED_CURRENT_GATE | HOLD |
| `experiment/ttm-six-g1-tiny-real-qwen-poc-20261110` | `c0b5239862ce` | SIX | UNVERIFIED_CURRENT_GATE | HOLD |
| `feature/p07-paged-attention-kernel-design-20261107` | `06b047856a84` | T6_P07 | P07 PAUSED_PRESERVE_HOLD | HOLD |
| `feature/ttm-t6-dense-paged-ab-benchmark-fixture-20261109` | `0ebd59755b41` | T6_P07 | UNVERIFIED_CURRENT_GATE | HOLD |
| `governance/train-first-colab-and-branch-consolidation-20261108` | `706911a9048c` | OTHER | UNVERIFIED_CURRENT_GATE | HOLD |
| `governance/ttm-parallel-workstreams-review-20261109` | `94aaced34335` | OTHER | UNVERIFIED_CURRENT_GATE | HOLD |
| `governance/ttm-t6-postmerge-p07-p08-readiness-20261114` | `d023dd16f4c0` | T6_P07 | T6 CLOSED_MERGED_SCOPED; P07 PAUSED; P08 NOT_OPENED | HOLD |
| `implementation/ttm-six-g1-preexec-admission-candidate-20261109` | `51636a3187ed` | SIX | UNVERIFIED_CURRENT_GATE | HOLD |
| `implementation/ttm-six-g1-production-gates-methods-v1e-20261110` | `a319a6e5487d` | SIX | UNVERIFIED_CURRENT_GATE | HOLD |
| `implementation/ttm-six-g1-trusted-runtime-witness-20261109` | `81795e794550` | SIX | UNVERIFIED_CURRENT_GATE | HOLD |
| `main` | `593455c9c747` | OTHER | UNVERIFIED_CURRENT_GATE | BASE |
| `planning/ttm-six-g1-original-single-batch-provision-20261110` | `5ef0a7467600` | SIX | UNVERIFIED_CURRENT_GATE | HOLD |
| `research/six-ttm4m-three-arm-exploratory-archive-20261110` | `1d6e73ecf15d` | OTHER | UNVERIFIED_CURRENT_GATE | HOLD |
| `research/ttm-gemini-embedding2-gqa-pagedattention-feasibility-design-20261108` | `a41d268e1a88` | EMBED | UNVERIFIED_CURRENT_GATE | HOLD |
| `research/ttm-gemma2-token-alignment-pretraining-causality-20261111` | `2583dadc254a` | EMBED | UNVERIFIED_CURRENT_GATE | HOLD |
| `research/ttm-gpt2-llama4-philosophy-architecture-round1-20261110` | `fe3e2851019f` | OTHER | UNVERIFIED_CURRENT_GATE | HOLD |
| `research/ttm-hdata-s1-fail4-prospective-mechanism-design-20261114` | `33021a421f05` | HDATA | NO_DEMONSTRATED_SCOPED_SEMANTIC_BENEFIT; FAIL4 DESIGN_ONLY | HOLD |
| `research/ttm-o0-n1-failed-gates-natural-narrative-redirect-20261111` | `81c08f99af0d` | O0 | UNVERIFIED_CURRENT_GATE | HOLD |
| `research/ttm-o0-narrative-cf1-source-scorer-blind-readiness-20261111` | `f2ce247bced6` | O0 | UNVERIFIED_CURRENT_GATE | HOLD |
| `research/ttm-o0-only-neural-feasibility-diagnostic-design-20261111` | `6497699a13e4` | O0 | UNVERIFIED_CURRENT_GATE | HOLD |
| `research/ttm-r3-structural-state-tracing-design-20261111` | `cd3dc4ceb3a4` | OTHER | UNVERIFIED_CURRENT_GATE | HOLD |
| `research/ttm-r3a-adversarial-independent-review-20261111` | `815541c6f8ed` | OTHER | UNVERIFIED_CURRENT_GATE | HOLD |
| `research/ttm-r3a-antishortcut-amendment-20261111` | `81327724c087` | OTHER | UNVERIFIED_CURRENT_GATE | HOLD |
| `research/ttm-six-cross-model-representation-transfer-20261109` | `d5d0c5346a59` | SIX | UNVERIFIED_CURRENT_GATE | HOLD |
| `research/ttm-six-functional-transfer-ttm4m-three-arm-design-20261110` | `d13d2d6c98cd` | SIX | UNVERIFIED_CURRENT_GATE | HOLD |
| `research/ttm-six-g1-exploratory-public-dev-20261110` | `a48e423c07c8` | SIX | UNVERIFIED_CURRENT_GATE | HOLD |
| `research/ttm-small4m-d1-v6-r1r3-integrated-source-qa-20261114` | `b5dd5890b73a` | D1_R1 | UNVERIFIED_CURRENT_GATE | HOLD |
| `research/ttm-small4m-embeddinggemma2-ood-design-20261111` | `d4550cb9c881` | EMBED | PASS_SCOPED_OOD_RESIDUAL_TRANSPORT | HOLD |
| `research/ttm-small4m-embeddinggemma2-token-swap-minimal-proof-20261109` | `13820a972c99` | EMBED | UNVERIFIED_CURRENT_GATE | HOLD |
| `research/ttm-small4m-fact-conditioning-data-objective-capacity-design-20261112` | `6023ed90612e` | D1_R1 | UNVERIFIED_CURRENT_GATE | HOLD |
| `research/ttm-small4m-h-data-s1-matched-budget-prereg-20261113` | `ef4cc05037f9` | HDATA | UNVERIFIED_CURRENT_GATE | HOLD |
| `research/ttm-small4m-post-cf1-language-fresh-gap-reconcile-20261111` | `8c393092a5bf` | OTHER | UNVERIFIED_CURRENT_GATE | HOLD |
| `research/ttm-small4m-post-final24-negative-archive-hypotheses-20261112` | `37165ce6eea0` | SMALL4M_QUALITY | FINAL24 FAIL_SCOPED; H-DEC partial repetitive-gram result | HOLD |
| `research/ttm-small4m-prompt-adherence-continuation-design-20261111` | `0ec28d44587f` | SMALL4M_QUALITY | UNVERIFIED_CURRENT_GATE | HOLD |
| `research/ttm-small4m-prompt-conditioning-objective-design-20261110` | `16d00b23d919` | OTHER | UNVERIFIED_CURRENT_GATE | HOLD |
| `research/ttm-small4m-q1q2-quality-single-batch-20261109` | `72cbf73c3adb` | Q1Q2 | UNVERIFIED_CURRENT_GATE | HOLD |
| `research/ttm-small4m-semantic-state-goal-toy-r2-20261110` | `c85b2ab50495` | OTHER | UNVERIFIED_CURRENT_GATE | HOLD |
| `research/ttm-small-4m-colab-pilot-prereg-20261108` | `ad9999019dd2` | OTHER | UNVERIFIED_CURRENT_GATE | HOLD |
| `research/ttm-t5-f32-strict-logit-parity-diagnostic-20261109` | `45918caed31a` | OTHER | UNVERIFIED_CURRENT_GATE | HOLD |
| `research/ttm-t5-ollama-full-logits-20261111` | `99ca9eee4114` | OTHER | UNVERIFIED_CURRENT_GATE | HOLD |
| `research/ttm-vector-memory-architecture-20261111` | `b7788337bd98` | VM | UNVERIFIED_CURRENT_GATE | HOLD |
| `review/ttm-cf1-dev36-one-shot-scoped-science-adjudication-20261111` | `d725c39094a5` | OTHER | UNVERIFIED_CURRENT_GATE | HOLD |
| `review/ttm-r3-adversarial-latest-write-20261111` | `d641e1577eae` | OTHER | UNVERIFIED_CURRENT_GATE | HOLD |
| `review/ttm-six-g1-v1c-codex-distinct-20261109` | `d478282e16a4` | SIX | UNVERIFIED_CURRENT_GATE | HOLD |
| `review/ttm-six-g1-v1e-codex-distinct-owner-import-20261110` | `365c352daee2` | SIX | UNVERIFIED_CURRENT_GATE | HOLD |
| `review/ttm-six-g1-windows-distinct-20261110` | `efbbc1fddfd6` | SIX | UNVERIFIED_CURRENT_GATE | HOLD |

Chứng cứ đầy đủ ở inventory JSON; bảng này không thay thế QA merge độc lập của từng nhánh.
