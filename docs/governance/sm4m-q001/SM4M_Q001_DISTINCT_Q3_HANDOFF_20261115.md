# HANDOFF — SM4M-Q001 Distinct Independent Q3 Source / Evidence / Admission Review

**Operation:** `SM4M_Q001_DISTINCT_INDEPENDENT_ARCHITECTURE_SOURCE_EVIDENCE_ADMISSION_REVIEW_Q3_SINGLE_GATE`  
**Repo:** `minhtri22/TokenToModel-Lab` · **Governance branch:** candidate review branch in related Draft PR, use its **exact Git HEAD**, not moving `main` ref.  
**Owner scope:** see `SM4M_Q001_OWNER_SCOPED_Q2_ACCEPTANCE_20261115.md` (scope accepted, AD gates **not** passed).  
**Baseline `main` for source verification:** `6cab3b8e8430628aa5c944a494ccc08d8f8783fc`; Q001 question blob `27b8337aea9c9e82bfe98657170e592fcb3ad941`.  
**Reviewer role:** structurally independent from the Q2 author; **READ_ONLY · DESIGN/SOURCE ONLY · NO MODEL RUN · NO SCIENCE**.

## 1. Nhiệm vụ duy nhất

**Phản biện độc lập** Q001 Q2: kiến trúc thực T4 có thật sự được map từ P02/code/trainer/checkpoint/evaluator, các kết quả Small-4M lịch sử có được diễn giải đúng scope, bảy giả thuyết nhân quả được phân loại đúng, AD-00…AD-08 có đủ để phân biệt nguyên nhân mà không tạo bất hợp lệ gold/rater/shortcut, và có thật sự hợp lý khi `KEEP_HISTORICAL_REFERENCE_ONLY` nhưng `HOLD_BASELINE_ADMISSION_FOR_NEW_SCIENCE`.

**Không làm thay Q4.** Q3 phải thử tìm phản chứng/counterexample cho tác giả Q2; không phải chỉ kiểm file tồn tại.

## 2. Input immutable, bắt buộc đọc toàn bộ

Xem bảy nguồn trong `SM4M_Q001_OWNER_SCOPED_Q2_ACCEPTANCE_20261115.md`, xác minh SHA-256 hoặc Git blob SHA-1 exact; đọc nguồn gốc trên `main` `6cab3b8e8430628aa5c944a494ccc08d8f8783fc` và các branch HEAD trong `SM4M_Q001_Q2_CAUSAL_EVIDENCE_MATRIX_20261115.json`. Đọc toàn bộ các nguồn **Original Author Q2 Architecture Audit**, **Q2 literature triage**, **Q2 causal evidence lock** và ba receipts + matrix, không thay thế bằng phần tóm tắt chat.

Tối thiểu đọc source paths `src/p02/transformer_core.py`, `tools/pilot_t4/integrated/t4_capacity_smoke.py`, `tools/pilot_t4/a2_continuous1024/t4_train_science_a2.py`, `tools/pilot_t4/integrated/t4_data_pack.py`, `tools/pilot_t1t3/source_t2/ttm_gpt2_bpe2048.py`, `tools/pilot_t4/integrated/t4_eval.py`, và lineage hiện có ở exact base. Không dùng `src/p03/train_loop.py` hay default `P02Config` như runner đã train.

## 3. Các làn phản biện ưu tiên

1. **Source & byte custody:** Q2 file bytes/Git SHA, source commit pins, checkpoint T4 historical hash vs `NOT_REVERIFIED`, no TEST/FINAL rerun. Có pin sai, cite sai, report/receipt conflict, source omission không?
2. **Architecture implementation:** Parameter count 3,749,376 và trained cfg 2048/256/256/4/4; causal mask, absolute position, tied head, Pre-LN, external `ignore_index=-100`, 4096 labels ×1024 exposures, window resets, tokenizer TRAIN-only. Lỗi source nào thực sự được xác minh? Không tự gọi mọi khác biệt là bug.
3. **Cross-study evidence parity:** T4 VAL/TEST NLL ≠ instruction following; FRESH12 AI-rater, FRESH16 two *different* rater tasks, CF1 DEV36 candidate switch, D1 EXP32 rater byte gap, A/C FINAL24 mean *absolute* ≠ delta, H-DATA score floor, FC01 lexical heldout (heterogeneous), D1 R1 design-only. Không pool endpoints.
4. **Causal hypothesis integrity:** Seven H-METRIC/H-OBJECTIVE/H-DATA/H-DECODER/H-CONTEXT/H-CAPACITY/H-IMPL and alternatives; seek counterexamples to inference, distinguish `NO_EVIDENCE` from `EVIDENCE_OF_NO_EFFECT`. Find if any known observation contradicts the chosen priority.
5. **AD-00…AD-08 hard veto:** Order, necessary vs sufficient, AD-01 rights/custody, AD-03 rater-visible spans vs hidden gold, AD-04 independent calibration, AD-05 shortcut, AD-06 identifiability, AD-07 prospective metrics, AD-08 authority. Find any bypass/deadlock or overbroad veto. Scope accepted, **admission statuses remain as frozen**.
6. **Scientific literature external validity:** verify paper identity/claims; label `literature supports mechanism` not direct root cause; no false extrapolation from TinyStories, scaling law, instruction tuning, judges, HANS/CLUTRR.
7. **Minimal discriminating evidence and stop:** Can teacher-forced vs generation isolate candidate cause with one variable changed and equal information budget? Identify where it still confounds objective/data/decoder/evaluator and what minimal prospective proof would change a decision.

## 4. Deliverables và closure

Nộp **một** `SM4M_Q001_Q3_DISTINCT_INDEPENDENT_REVIEW_20261115.md` và **một** `SM4M_Q001_Q3_DISTINCT_INDEPENDENT_REVIEW_RECEIPT_20261115.json`, with:
- exact candidate PR HEAD and seven input Git blobs/hash, reviewer identity/independence declaration and method;
- per-finding severity `HIGH/MEDIUM/LOW`, exact file/line/source and testable consequence;
- seven hypotheses verdict by scope (not probability estimate), each AD gate status and any hard veto;
- single overall verdict `PASS_Q3_SOURCE_AND_EVIDENCE_SCOPE_SCOPED` **or** `HOLD_Q3_REMEDIATION`, `root_cause_identified` evidence requirement, `science_executed=false`;
- conclusion preserving `KEEP_HISTORICAL_REFERENCE_ONLY` vs `HOLD_NEW_SCIENCE` unless independently rebutted, and next single step for owner Q4 or integrated source correction.

A Q3 PASS **does not** approve new data, benchmark, score, checkpoint, GPU or F0–F2 patch. A HOLD calls for **one integrated remediation on same governance PR**, not a new research branch. Q4 remains owner controlled. Never append Q3 design result into `lineage.md`.

**Allowed action:** independent read-only examination/report. **Not authorized:** model inference, GPU/training, new gold, replay, code change, science/admission GO, F3/F4, merge.
