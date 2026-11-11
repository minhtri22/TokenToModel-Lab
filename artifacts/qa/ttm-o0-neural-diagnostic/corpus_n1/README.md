# TTM O0-DIAG-N1 — GitHub Source of Truth

**Phán quyết tích hợp:** `HOLD_T4_DO_NOT_TRAIN`. **Nguồn:** 2026-11-11. **Nội bộ:** owner + ChatGPT Web; không có Codex review mới.  
**Không nhầm:** PASS kiểm thử nguồn/validator/BPE/CPU ≠ PASS độ khó khoa học. Heuristic alias-aware không dựng graph/state giải **4608/4608**.

## Nguồn và kết quả chính

- [Báo cáo tích hợp đầy đủ + quyết định GO/HOLD](../../../docs/research/TTM_O0_N1_NEW_DIAGNOSTIC_CORPUS_INTEGRATED_CPU_PREFLIGHT_AND_SINGLE_OWNER_HOLD_20261111.md)
- [Biên nhận quyết định dạng JSON](O0_N1_INTEGRATED_SINGLE_OWNER_HOLD_DECISION_20261111.json)
- [Generator public toàn bộ TRAIN/DEV](../../../tools/research/o0_diagnostic_n1/o0_n1_public_generator.mjs)
- [Independent visible-text checker](../../../tools/research/o0_diagnostic_n1/o0_n1_independent_checker.mjs) và [4608-row QA](O0_N1_INDEPENDENT_PUBLIC_CORPUS_QA.json)
- [Strict raw JSON validator](../../../tools/research/o0_diagnostic_n1/o0_n1_raw_input_fail_closed.mjs) và [16 negative tests](O0_N1_RAW_JSON_FAIL_CLOSED_NEGATIVE_QA.json)
- [Public TRAIN oracle](TRAIN_PUBLIC_ORACLE.json) · [TRAIN model-only](TRAIN_MODEL_INPUT_ONLY.json) · [TRAIN eight shards](TRAIN_SHARD_INDEX.json)
- [DEV-IID oracle](DEV_IID_PUBLIC_ORACLE.json) · [DEV-IID model-only](DEV_IID_MODEL_INPUT_ONLY.json)
- [DEV-STRUCT oracle](DEV_STRUCT_PUBLIC_ORACLE.json) · [DEV-STRUCT model-only](DEV_STRUCT_MODEL_INPUT_ONLY.json)
- [20/20 GitHub exact-byte shard + DEV readback](O0_N1_GITHUB_READBACK_PART1.json) · [remaining shard readback](O0_N1_GITHUB_READBACK_PART2.json)
- [T1 BPE 1791-merge / context256 readback](O0_N1_EXACT_T1_BPE2048_LENGTH_READONLY_QA.json)
- [Alias-aware last-event heuristic source](../../../tools/research/o0_diagnostic_n1/o0_n1_alias_aware_last_event_baseline.mjs) · [4608/4608 shallow baseline](O0_N1_SHALLOW_ALIAS_HEURISTIC_BASELINE.json)
- [Single-intervention and FINAL coarse split FAIL receipt](O0_N1_SINGLE_INTERVENTION_AND_STRUCTURAL_SPLIT_AUDIT.json)
- [Exact CPU source compressed](../../../tools/research/o0_diagnostic_n1/o0_cpu_restore_qa.py.gz.b64) · [CPU synthetic parity receipt](O0_N1_CPU_P02_PARENT_RESTORE_SYNTHETIC_QA.json)
- [Encrypted FINAL seed escrow (no secret)](BLIND_FINAL_ENCRYPTED_SEED_ESCROW.json) · [byte-reconstructable final source](../../../tools/research/o0_diagnostic_n1/o0_final_private_escrow.py.gz.b64) · [512-row cryptographic regeneration QA](O0_N1_FINAL_SEED_ESCROW_REPRODUCTION_QA.json)

## Nguồn Python được lưu trọn byte, không phải ZIP tải về

Hai `*.py.gz.b64` là toàn bộ mã Python nguyên gốc được gzip mtime0 rồi base64. Đọc trên GitHub để khôi phục bằng Python3.12:

```python
from pathlib import Path
import base64, gzip
src = Path('tools/research/o0_diagnostic_n1/o0_cpu_restore_qa.py.gz.b64')
raw = gzip.decompress(base64.b64decode(src.read_text(encoding='ascii').strip()))
print('source bytes:', len(raw))
# Verify SHA256 and Git blob from integrated report before executing; source has container-specific paths.
```

Lưu ý `o0_cpu_restore_qa.py` dùng local container path `/mnt/data` và có **hai optimizer step trên token tổng hợp**, không chạy khoa học. `o0_final_private_escrow.py` không chứa khóa hoặc seed trong GitHub; chỉ owner private file dưới `D:\WORK\RESEARCH\TokenToModel-Lab\_tmp` mới có khóa. `_tmp/` được `.gitignore` loại khỏi Git; không đưa key ra chat, PR hay public repo.

**Đã bảo toàn FAIL thật:** 596/1.152 nhóm có thêm noise reorder; FINAL coarse structural patterns trùng DEV-STRUCT 4/4; shallow heuristic 100%. **Không vá tiếp dựa trên các phép thử đã xem.**

**Bước tiếp theo đề xuất:** `TTM_O0_DIAGNOSTIC_N1_FAILED_GATES_OWNER_RESEARCH_REDIRECT_NO_MORE_HEURISTIC_PATCHES` — chọn demo task learning O0 công khai **hoặc** một benchmark nghiên cứu mới được tiền đăng ký trước, không dùng N1 làm FINAL khoa học.

`MAIN=UNCHANGED_BY_THIS_WORK` · `PR13=DRAFT_HOLD` · `LINEAGE=UNCHANGED` · `R3A=DEMO_ONLY` · `NEW_TRAINING=NO` · `GPU=NO` · `TEST_Q1Q2=UNTOUCHED`.
