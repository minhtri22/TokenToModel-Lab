# TTM × SIX G1 — Research branch closure

**Ngày:** 2026-11-10  
**Quyết định chủ sở hữu:** CLOSE_CURRENT_TTM_SIX_G1_RESEARCH_BRANCH  
**Phạm vi:** đóng luồng nghiên cứu TTM_SIX_G1 và hai pilot exploratory liên quan; không đóng toàn bộ chương trình SIX hoặc dự án TTM.
**Trạng thái cuối:** `BRANCH_RESEARCH_CLOSED_ARCHIVED` · `NO_NEW_EXECUTION` · `G1_ORIGINAL=FEASIBILITY_HOLD_ARCHIVED` · `G1_SCIENCE_LOCK=HOLD` · `PRIVATE_TEST=SEALED`.

## 1. Phán quyết riêng từng hợp đồng

### Qwen3-0.6B → Qwen3-1.7B: exploratory public 48 TRAIN / 16 DEV

Source: [G1 exploratory Qwen independent recomputation](G1_EXPLORATORY_REAL_QWEN_T4_DEV_RESULTS_INDEPENDENT_RECOMPUTE_20261110.md).  
`TTM_SIX_G1_EXPLORE_AUTHORED_PUBLIC_QWEN_DEV_V1` → `EXPLORATORY_NO_SIGNAL` *đối với lợi ích bổ sung của cơ chế hai bước A→P theo màn sàng lọc đã đăng ký*.

- A→P hidden alignment → target functional probes: DEV MAE `0.065537960`.
- Direct source hidden → target functional probes: `0.061827128`.
- TRAIN response mean: `0.067550507`.
- Group-shuffle median: `0.065511059`.
- A→P cải thiện so với TRAIN mean nhưng kém shuffle median một lượng rất nhỏ; không vượt điều kiện sàng lọc. Direct probe tốt hơn A→P, cho thấy predictive association, **không** phải chứng minh cơ chế SIX transfer.
- 16 DEV / 4 nhóm, 2 probes, 32 shuffle permutations, một seed, không information-budget matched; không kiểm định confirmatory.
- CKA mô tả `0.96765794` trên bốn group means chỉ là tín hiệu hình học, không chứng minh functional transfer.

**Kết luận cho câu hỏi “cùng họ Qwen có chuyển giao được không?”:** nghiên cứu hiện tại **chưa chứng minh được chuyển giao chức năng có lợi theo cơ chế A→P**. Đồng thời **không chứng minh rằng chuyển giao giữa các Qwen là bất khả thi**; direct source→target functional prediction có tín hiệu, nhưng không xác nhận lợi ích nhờ SIX.

### Qwen features → TTM-Small-4M: three-arm pilot

Source: [Three-arm final adjudication](TTM_SIX_TTM4M_THREE_ARM_FINAL_EXPLORATORY_ADJUDICATION_AND_ARCHIVE_20261110.md).  
`TTM_SIX_TTM4M_FUNCTIONAL_TRANSFER_PUBLIC48_DEV16_V1` → `EXPLORATORY_NO_CLEAR_GAIN`.

| Arm | DEV NLL | Probe MAE |
|---|---:|---:|
| Parent | 5.290400058081509 | — |
| A: next-token CE | 3.5657932133037225 | — |
| B: CE + direct MSE | 3.6051159389127934 | 0.06855617190433794 |
| C: CE + residual SIX-inspired MSE | 3.616317542474685 | 0.06980299486229088 |
| Template-only | — | 0.05202296104592581 |

C không đạt cả bốn điều kiện: NLL ≥1% tốt hơn A; NLL ≥1% tốt hơn B; probe MAE ≥1% tốt hơn strongest control; thắng ≥3/4 DEV groups. Kết quả: `relative_dev_nll_C_vs_A=-0.01416916970464244`, `relative_dev_nll_C_vs_B=-0.003107141005087875`, `relative_probe_mae_C_vs_strongest_control=-0.34177281452066677`, `DEV_groups_C_better_than_A=1`. One-shot consumed (72 × 3 updates), không mở repeat.

### Original G1

Qwen3-0.6B→Qwen3-1.7B, 128 TRAIN / 64 DEV / 64 private TEST, eight probes, frozen original scientific contract: **NOT_EXECUTED**, **NO_ORIGINAL_G1_PASS_OR_FAIL**. Archive feasibility HOLD is not a negative result of original confirmatory hypothesis. Do not open private TEST; do not append exploratory results to `lineage.md`.

## 2. Chain-of-custody / integrity limits

- Owner-reported postrun: `PASS_EXACT_SHA` for `arm_A_weights_only.pt`, `arm_B_weights_only.pt`, `arm_C_weights_only.pt`, `result.json`; `TTM_SIX_POSTRUN_INTEGRITY=PASS`.
- Hashes and source pins recorded in preceding archive. Assistant did not read the binary weights from Google Drive; no independent byte rehash by assistant.
- `READY.json` is present with `TEST_used=false`; no independent SHA for READY itself has been provided.
- Original Qwen T4 execution remains owner-reported, though earlier numerical recomputation was independent using supplied artifact.
- No new private dataset or tensors are to be committed to GitHub.

## 3. Final owner closure decision

**CLOSE, do not continue this current branch's research execution.**
- No further GPU experiments, no automatic migration to another SIX/G1 hypothesis and no additional experimental scope on this branch.
- Preserve complete evidence, Qwen ZIP, A/B/C and parent checkpoints as-is; do not merge weights or alter historical results.
- Do not modify `main`, original G1 frozen contract, `lineage.md`, TEST or project TTM roadmap.
- TTM follow-on work is handled by a *separate agent*, explicitly outside this branch's remit; **no handoff tasks assigned here**.
- Future new SIX functional-transfer research, if ever authorized, must open a **new hypothesis, new preregistration, fresh evidence boundary and new owner decision**. This closure is not permission to run.

## 4. Closure acceptance

`QWEN_EXPLORATORY=EXPLORATORY_NO_SIGNAL`  
`TTM_THREE_ARM_EXPLORATORY=EXPLORATORY_NO_CLEAR_GAIN`  
`ORIGINAL_G1_SCIENCE=NOT_EXECUTED`  
`ORIGINAL_G1_FEASIBILITY=HOLD_ARCHIVED`  
`BRANCH_RESEARCH=CLOSED_ARCHIVED`  
`GPU_RETRY=NOT_AUTHORIZED`  
`PRIVATE_TEST=SEALED`  
`G1_SCIENCE_LOCK=HOLD`

**Bước thực hiện tiếp theo:** `NONE_FOR_THIS_BRANCH_CLOSED`. Không giao tiếp việc TTM cho agent hiện tại.
