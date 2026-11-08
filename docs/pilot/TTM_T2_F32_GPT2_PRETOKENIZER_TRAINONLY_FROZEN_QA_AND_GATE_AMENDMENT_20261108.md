# TTM-Small-4M T2 F32 — GPT-2 PRETOKENIZER / 2048 TRAIN-only / T2 native QA pin

Ngày 2026-11-08. **Baseline:** PR #12 (DRAFT) từ `main@1a9d8cba56564d6d36257fe95c34f2fd52c4f48a`, P02 Git blob `9762343e06cf800b50574c2871ae1ed58537fb18`, llama.cpp `372dc5ca157276beb6c67b2e92477e8d662e964a`. Không thay đổi P00–P12, P07, hoặc `lineage.md`.

## 1. Phạm vi thiết kế đã triển khai

- Đã tạo gói mã CPU `TTM_SMALL4M_T2_F32_GPT2_TRAIN_ONLY_INTEGRATED_QA_20261108.zip` **SHA256 `d6fd9d09a031c4c19e099f0d66d7d5fcccc0e8543ea602d7268ec6cb415dbcb9`**, chứa Python BPE fitter, GGUF F32 exporter/inference adapter, CLI runner PowerShell 5.1, regression tests, fixture JSON, README + per-file hash manifest. **Gói là attachment của cuộc trò chuyện, chưa commit code vào nhánh PR; khi Windows native PASS mới commit/publish exact mã đã pin.**
- PowerShell runner SHA256 `62f0246ddbebe01aa8603e781226ea5cc8436141442b71e4dc3e595f5bd0be73`; khóa SHA mọi file phụ thuộc trong gói, kiểm tra native probe+DLL/pinned repo/P02/llama.cpp và đầu ra fresh one-shot.
- BPE: byte tokens IDs `0..255`, EOS `256`, 1791 deterministic merges IDs `257..2047`, tokenizer `tokenizer.ggml.pre=gpt-2`. Regex đúng pinned GPT2, bảo toàn mọi ký tự không khớp regex (như CRLF/tab/newline), mọi merge bị giới hạn theo pretokenized segments, không merge qua story/split.
- `train_only` chỉ chấp nhận `Story(split=TRAIN)` và nguồn cho phép. **Kết quả T2 học merges trên 720 synthetic TRAIN stories**; chưa có dữ liệu TinyStories, chưa fit khoa học. Real TRAIN sau này phải được khóa revision/file SHA, parser story, dedup/manifest và quyền. Không dùng VAL/TEST cho fits.
- Hợp đồng export F32: giữ nguyên 52 tensor P02, full readback F32 max weight error `0`, inject metadata tokenizer tokens/ordered merges đúng; 3,749,376 tham số; không thay đổi architecture, không thử F16 trong integrated QA này.

## 2. Fixture đã khóa trước native

`TTM_T2_F32_NEW_FIXTURES_FROZEN_20261108.json` **SHA256 `5a4ba58db3ad7c1ad0a7c6a790c08184d43c1e3a081ad2dcaf2d4c3b9dbeb9f2`**: 20 tokenizer texts + 10 independent numeric input-ID sequences, đều khác ca V5B toàn bộ. Có whitespace/tabs/CRLF, Unicode, punctuation, newline, prompt và EOS IDs. Freeze trước mọi phép chạy Windows native.

**Tiêu chí**: `20/20` llama.cpp exact token IDs vs byte-BPE oracle; `10/10` 2048-dim logits vectors F32 with `max_abs <= 0.001`, 0 top1 mismatch; P02/blob/probe/native DLL/manifest/no-overwrite gates PASS. Không diễn giải posthoc 9/9 V5B thành heldout evidence.

## 3. QA đã có / còn thiếu

| Hạng mục | Trạng thái |
|---|---|
| BPE synthetic exactly 2048 IDs, 1791 merges; TRAIN-only negatives | `PASS_CPU_UNIT` |
| UTF-8/CRLF/punctuation roundtrip; merge manifest tamper rejection | `PASS_CPU_UNIT` |
| New-frozen fixtures SHA and non-overlap with V5B | `PASS_CPU_UNIT` |
| P02 exact F32 GGUF 52 tensors weight readback max error=0 | `PASS_CPU_UNIT` |
| Python pytest | **`11/11 PASS`** in isolated Linux CPU Python3.13 torch2.10.0+cpu regex2026.5.9 |
| ZIP integrity/CRC/all 7 file hashes | `PASS_PACKAGE_STATIC` |
| PowerShell 5.1 parse on user Windows | `NOT_EXECUTED` |
| llama.cpp native F32 20 tokenizer + 10 numerical fixtures | **`NOT_EXECUTED`** |
| Actual TRAIN-only TinyStories tokenizer, file SHA/split/dedup, Colab resume | `NOT_EXECUTED / SCIENCE_LOCK_HOLD` |

## 4. Proposed amendment to T2 pilot gate (F32-first)

**Review recommendation**: For this ~3.75M parameter small-model pilot, require real F32 inference, exact tokenizer and logits parity as **mandatory** pre-training export feasibility gate. F16 and quantization remain independently archived **optional optimization lane**, not evidence of model learnability. This respects the original core architecture and P00–P12 ordering and reduces repeated micro-gates. The V5B `f16+position_f32` STOP remains recorded: pinned ggml-cpu `unsupported types: dst: f32, src0: f32, src1: f16`; this proposal is not retroactive PASS.

**STATUS:** `F32_FIRST_GATE_AMENDMENT=PROPOSED_PENDING_REVIEW` · `T2_F32_NEW_FROZEN_QA=READY_FOR_WINDOWS` · `T2_FULL=HOLD` · `SCIENCE_LOCK=NOT_GRANTED`. Does not authorize Colab GPU or training.

## 5. One integrated next step

On Windows use exactly the packaged PowerShell script in fresh Downloads folder; SHA+PS parser → `-Mode Preview` (read-only) → exactly one `-Mode Execute` to `_tmp/ttm_t2/f32_pretok_trainonly_v1`; install only pinned `regex==2026.5.9` wheel in existing isolated TTM Python CPU env *if missing*. Existing V3/V4/V5/V5B assets remain read-only; no source download, no C++ compile. Independently read new JSON; classify genuine FAIL vs PASS. If PASS, archive exact source+manifest to PR #12 and authorize T1/T3 integrated source/Colab resume preflight **only after accepted governance amendment**. No science seed/TEST or T4 GPU before final prereg lock.
