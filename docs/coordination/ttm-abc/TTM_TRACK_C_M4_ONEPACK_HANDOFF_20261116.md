# Agent C handback — M4 Data/Measurement/SFT design onepack

**Operation:** C_M4_DATA_AUDIT_MEASUREMENT_CONSTRUCT_AND_SFT_MASK_DESIGN_ONLY_ONEPACK
**Repository:** minhtri22/TokenToModel-Lab · **Working branch:** research/ttm-track-c-research-scaling-20261116 · **PR:** #35 (Draft)
**Start HEAD:** 666bc2c95ba21eaddcf8a0e3f8ed7cd906629de2 · **main baseline:** f7a0a5874e8fd895c8ea8d17ceff393a4d4917a3.
**Scope:** design-only docs, deterministic synthetic fixture code/tests, source-only metadata checks. No real corpus, no private checkpoint/tokenizer, no model, no GPU, no science, no merge, no A/B edits, no lineage modification.

## Deliverable map

1. `docs/research/ttm-abc/track-c/C_EVAL_CONSTRUCT_AND_DATA_AUDIT.md` — traced historical numbers vs missing real histogram/dedup/license/splits; endpoint/rubric/positive-negative controls, floor policy.
2. `docs/research/ttm-abc/track-c/C_DATA_OBJECTIVE_CAPACITY_MATRIX.md` — D0/D1/D2 and prospective O/P arms, exposure arithmetic vs FLOPs, seed/power/resource gates, checkpoint compatibility.
3. `docs/research/ttm-abc/track-c/C_SFT_PROTOCOL.md` — nanochat-at-pin interpretation, B-facing serialization, shift/assistant-answer mask and no cross-document packing.
4. `tests/ttm_track_c/synthetic_contract.py` / `test_synthetic_contract.py` — pure-stdlib toy audit/serialize/slot scoring and negative QA, no model or sensitive material.
5. `configs/ttm_track_c_design_only_v1.json` — machine-readable proposal, not locked runtime config.
6. `artifacts/ttm-abc/track-c/` — QA receipt: artifacts/ttm-abc/track-c/TTM_TRACK_C_M4_AUTHOR_SYNTHETIC_QA_RECEIPT_20261116.json; 14/14 offhost Python 3.13.5, independently reviewed NOT_EXECUTED, distinguishing native vs author-only verification.

## Gates (do not promote via paper checks)

| Gate | Latest honest category |
|---|---|
| C-G0 | Source inventory AUTHOR_PASS_SCOPED, independent PENDING |
| C-G1 | REAL_DATA_HOLD (no private corpus; only toy corpus QA) |
| C-G2 | PROPOSED_CONSTRUCT / toy controls, independent PENDING |
| C-G3 | DESIGN_ONLY |
| C-G4 | WAIT_A_B |
| C-G5 | DESIGN_ONLY / toy mask verification, not B trainer |
| C-G6 | DESIGN_ONLY (architecture options, no artifacts validated) |
| C-G7 | NOT_AUTHORIZED |
| C-G8 | NOT_EXECUTED |

**Rights:** internal noncommercial owner declaration in handoff, but no blanket rights for new source, release or third-party scoring. No real rights attestation executed by Track C.
**Reviewer:** distinct reviewer NOT_PERFORMED; author smoke must not be relabeled independent.
**Compute estimate:** only 4,194,304 labels/seed/arm and planning multipliers are known, no actual measured GPU-s/FLOPs/VRAM. **Histogram / dedup:** actual unavailable; toy only. No scientific inference.

**Single blocker:** rights-scoped, source/hashed, fresh nonleaking dataset and A-qualified measurement endpoint (or independently qualified replacement) are missing; B pipeline required for training.
**Bước thực hiện tiếp theo — duy nhất:** `C_M4_INDEPENDENT_DESIGN_AND_SYNTHETIC_CONTRACT_REVIEW_SINGLE_GATE` — distinct reviewer challenges gold/negative controls, leakage policy, mask/shift/stop and arm budgets on the exact PR #35 HEAD; report PASS_DESIGN or HOLD_DESIGN without training or micro-permit.

## M4 single amendment (2026-11-16) — phản biện và bản sửa

Nhận đánh giá độc lập trên source HEAD `8e0a1880e564e92d017847e9f18e53e42b7353c8` từ nhánh `review/ttm-track-c-m4-independent-design-20261116`, evidence commit `98af7af0632ba38f1b9747cd784964257e39cf16`, kết luận `HOLD_DESIGN`. **Không thay đổi hoặc ghi đè reviewer receipt.**

- **C-F01:** sửa yêu cầu sai/không rõ về prompt gradient. Chỉ kiểm zero **direct CE target weight** ở nhãn prompt, cho phép gradient đi qua ngữ cảnh prompt. Tham chiếu `C_SFT_PROTOCOL.md` phần M4 amendment và `test_cf01_zero_direct_prompt_ce_not_zero_context_gradient`.
- **C-F02:** làm chặt `shifted_padded_targets()` bằng cách parse lại toàn bộ role-bound serialized IDs để tính mask, từ chối caller-supplied flags sai; đề xuất entrypoint duy nhất `build_sft_targets(messages,max_len)`. Không khẳng định chống giả mạo provenance corpus bằng bảo vệ cấu trúc toy này.
- **C-F03 (advisory):** toy normalized collision dùng Unicode NFC, không đổi actual-data gate.

**QA tác giả trên exact source:** 14 original + 10 new = **24/24 PASS**, thêm chính xác 2 reviewer-red tests tại SHA-256 `806faf955c6d37226d8ddaf8876edbff8e181fd1d2d5c853ec0d88124cde4b1f` = **2/2 PASS**; 1.000 randomized conversations. Python 3.13.5 Linux, stdlib-only; Windows Python 3.12 NOT_EXECUTED. Exact code blobs/SHA ở receipt sửa lỗi.

**Không tự nâng gate:** C-G5 giữ `HOLD_DESIGN_INTERFACE_PENDING_DISTINCT_REREVIEW`; C-G1 HOLD, C-G2 DESIGN_ONLY, B integration NOT_EXECUTED, M6 SFT NOT_EXECUTED, C-G8 NOT_EXECUTED, main/lineage unchanged, Draft PR #35 không merge.

**Bước thực hiện tiếp theo — duy nhất:** `C_M4_EXACT_AMENDMENT_DISTINCT_REREVIEW_SINGLE_GATE`, reviewer độc lập đọc đúng mã & tài liệu sửa và thực hiện lại đúng negative/regression scope để quyết định `PASS_DESIGN` hoặc `HOLD_DESIGN`.
