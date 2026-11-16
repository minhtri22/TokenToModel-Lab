# TTM — Global Repair-First triển khai backlog (2026-11-16)

**Nguồn:** [Roadmap](TTM_GLOBAL_REPAIR_FIRST_ROADMAP_20261116.md) · [CSV nhập tracker](TTM_GLOBAL_REPAIR_FIRST_BACKLOG_20261116.csv). **Planning only:** chưa thực thi test mới, chưa thay đổi PR #28 hay khoa học. TTM main baseline `f7a0a5874e8fd895c8ea8d17ceff393a4d4917a3`; nanochat reference `92d63d4e8bb4df75c3b71618f31ddde2378b2bcd`.

**Thứ tự:** P0=chẩn đoán đúng Small-4M, P1=bug/custody/measurement baseline, P2=data/posttrain/inference chuẩn, P3=architecture/scaling/serving. **P3 không được khởi chạy trước khi quyết định R1/R2/R3 có evidence.** `OPEN` và `DESIGN_ONLY` không có nghĩa đã được cấp phép khoa học. P0 I2 chỉ chạy nếu I1 thật PASS theo conditional GO đã ghi.

**Kiểu ticket:** `HISTORICAL BUG / SCOPED FIX` = lỗi lịch sử có sửa scoped, không tự coi còn hỏng; `HYPOTHESIS` = chưa tái hiện; `EVIDENCE GAP` = cần đo/đọc nguồn; `MISSING FEATURE` = chưa được triển khai; `HOLD kỹ thuật` = blocker có căn cứ. Chi phí L=source/CPU synthetic, M=native CPU/T4 hữu hạn, H=GPU/multi-arm/large-scale; là phân loại tương đối **không phải USD đo thật**. Checkpoint enum chỉ định tính tương thích, không tự xác nhận chạy.

## Ma trận ưu tiên tóm tắt

| ID | Prio | Type | State | Action / bug hypothesis | Dependency | Cost |
|---|---|---|---|---|---|---|
| [RF-00](#rf-00) | P0 | HOLD kỹ thuật | `BLOCKED_I1` | Q001 last-mile: single owner admission + native hard-memory guard | none | M (native no-model) |
| [RF-01](#rf-01) | P0 | EVIDENCE GAP | `WAIT_RF-00` | Checkpoint/tokenizer/80-case exact-custody + I2 once | RF-00 | M (one CPU run, conditional) |
| [RF-02](#rf-02) | P1 | HYPOTHESIS | `WAIT_RF-01` | Phân loại lỗi mô hình theo failure-tree, không đoán kiến trúc | RF-01 | L (read receipt) |
| [RF-03](#rf-03) | P1 | EVIDENCE GAP | `OPEN_SOURCE_ONLY` | Bản đồ quyền nguồn dataset theo hành động | none | L |
| [RF-04](#rf-04) | P1 | EVIDENCE GAP | `WAIT_RF-00` | Tokenizer T4 exact inventory + roundtrip + special IDs | RF-00,RF-03 | L/M |
| [RF-05](#rf-05) | P1 | INTEGRATION RISK | `WAIT_RF-01` | Checkpoint strict config & state-dict loader | RF-01 | L |
| [RF-06](#rf-06) | P1 | HYPOTHESIS | `WAIT_RF-01` | Shifted next-token targets / ignore mask / gradient weights | RF-01 | L (synthetic CPU) |
| [RF-07](#rf-07) | P1 | INTEGRATION RISK | `WAIT_RF-05` | Resume, scheduler, RNG and step/byte accounting | RF-05,RF-06 | M |
| [RF-08](#rf-08) | P1 | INTEGRATION RISK | `WAIT_RF-05` | P04↔T4 checkpoint schema adapter read-only | RF-05 | L |
| [RF-09](#rf-09) | P1 | HYPOTHESIS | `WAIT_RF-01` | Full-vocab greedy vs candidate-only scoring diagnostics | RF-01,RF-04 | L/M |
| [RF-10](#rf-10) | P1 | EVIDENCE GAP | `DESIGN_ONLY` | Fresh prompt-adherence measurement with valid gold/construct | RF-02,RF-03 | M (design), H if external gold |
| [RF-11](#rf-11) | P1 | EVIDENCE GAP | `DESIGN_ONLY` | Data audit: dedup/group split, domain balance and token fertility | RF-03,RF-04 | L/M |
| [RF-12](#rf-12) | P2 | MISSING FEATURE | `WAIT_RF-02` | One-command GPT baseline orchestration (not rewriting cores) | RF-04,RF-05,RF-06,RF-07,RF-08 | M |
| [RF-13](#rf-13) | P2 | MISSING FEATURE | `WAIT_RF-12` | Unified token-NLL + byte-bpb + grouped eval | RF-12,RF-10 | L |
| [RF-14](#rf-14) | P2 | HYPOTHESIS | `AFTER_RF-10` | Improve train-only data mixture/quality before size | RF-10,RF-11,RF-12,RF-13 | M/H (new science) |
| [RF-15](#rf-15) | P2 | HYPOTHESIS | `AFTER_RF-10` | Small instruction SFT with answer-only loss mask | RF-10,RF-12,RF-14 | M/H (new science) |
| [RF-16](#rf-16) | P2 | HYPOTHESIS | `AFTER_RF-09` | Format-only decoding controls / stop tokens | RF-09,RF-10 | L/M |
| [RF-17](#rf-17) | P2 | HYPOTHESIS | `AFTER_RF-15` | Objective ablation: prefix LM vs completion-only | RF-13,RF-15,RF-16 | H (several science arms) |
| [RF-18](#rf-18) | P2 | HISTORICAL BUG / SCOPED FIX | `WAIT_RF-12` | Verify GELU_ERF parity beyond C01-C04 (new fixtures only) | RF-08,RF-09,RF-12 | M/H |
| [RF-19](#rf-19) | P2 | EVIDENCE GAP | `WAIT_RF-18` | Production/backend compatibility qualification | RF-18 | M |
| [RF-20](#rf-20) | P2 | EVIDENCE GAP | `AFTER_RF-12` | Fair CPU Dense/Paged/no-cache benchmark | RF-12,RF-09 | M |
| [RF-21](#rf-21) | P2 | EVIDENCE GAP | `OPEN_DOCS_ONLY` | Unified model card/data card/training runbook | RF-12,RF-13 | L |
| [RF-22](#rf-22) | P3 | ARCHITECTURE HYPOTHESIS | `PAUSED` | RMSNorm replace LayerNorm separately | RF-13,RF-17 | H |
| [RF-23](#rf-23) | P3 | ARCHITECTURE HYPOTHESIS | `PAUSED` | RoPE vs learned absolute embeddings | RF-13,RF-17 | H |
| [RF-24](#rf-24) | P3 | ARCHITECTURE HYPOTHESIS | `PAUSED` | GQA and/or QK norm independent ablations | RF-20,RF-23 | H |
| [RF-25](#rf-25) | P3 | ARCHITECTURE HYPOTHESIS | `PAUSED` | ReLU² MLP and untied LM head one-at-a-time | RF-13,RF-17 | H |
| [RF-26](#rf-26) | P3 | OPTIMIZER HYPOTHESIS | `PAUSED` | MuonAdamW / learned scaling heuristic candidate | RF-12,RF-13 | H |
| [RF-27](#rf-27) | P3 | HARDWARE FEATURE | `PAUSED` | True paged attention GPU kernel / Flash attention | RF-20,RF-24 | H (backend-specific) |
| [RF-28](#rf-28) | P3 | MISSING FEATURE | `PAUSED` | Batch scheduler: prefill/decode continuous batching | RF-20,RF-27 | H |
| [RF-29](#rf-29) | P3 | SCALING HYPOTHESIS | `PAUSED` | Small4M→larger GPT-like only after evidence | RF-14,RF-15,RF-17,RF-21 | H (GPU and multi-seed) |
| [RF-30](#rf-30) | P3 | MISSING FEATURE | `PAUSED` | Serving API, observability, predictable rollback | RF-19,RF-20,RF-28 | H |
| [RF-31](#rf-31) | P3 | MISSING FEATURE | `PAUSED` | Release package and Vietnamese GPT textbook | RF-21,RF-29,RF-30 | M/H |
| [RF-32](#rf-32) | P2 | SECURITY/GOVERNANCE GAP | `SEPARATE_SCOPE_HOLD` | Windows restricted worker ACL/SID/Pipe sidecar | RF-03 | M |

## Hợp đồng từng công việc — agent nhận theo đúng dependency

### RF-00

**Công việc:** Q001 last-mile: single owner admission + native hard-memory guard

**Ưu tiên:** P0 · **Phase:** Small-4M · **Loại:** HOLD kỹ thuật · **State:** `BLOCKED_I1` · **Chi phí:** M (native no-model) · **Checkpoint:** `EXACT_NO_WEIGHT_CHANGE`.

- **Nghi vấn/khoảng trống:** Mã owner-internal/Win32 Job Object mới chưa native-qualified và wrapper hard-cap chưa gắn I2.
- **Test tái hiện / phản chứng:** Python3.12/PS5.1 exact current PR28 HEAD; negative wrong-root/host/nonce/hash/expiry, process-tree leaks, memory pressure, no-model.
- **Đối chứng (control):** Legacy 6/6 parser, 18/18 source, 44/44 author negatives, 22/22 adversarial, watchdog 5/5 ở source cũ; KHÔNG chạy lại không lý do.
- **Điều kiện đóng bằng số đo/evidence:** Một report distinct I1_PASS_SCOPED_INTERNAL_RESEARCH hoặc HOLD_I1 nêu một blocker; hard committed memory và sampled tree-RSS đo/đánh dấu riêng; root/custody đúng, không fake 3 signer.
- **Phụ thuộc:** none. **Nguồn:** PR28; Issue29; Q001 owner amendment.

### RF-01

**Công việc:** Checkpoint/tokenizer/80-case exact-custody + I2 once

**Ưu tiên:** P0 · **Phase:** Small-4M · **Loại:** EVIDENCE GAP · **State:** `WAIT_RF-00` · **Chi phí:** M (one CPU run, conditional) · **Checkpoint:** `EXACT_T4_STEP1024_INPUT_ONLY`.

- **Nghi vấn/khoảng trống:** Original checkpoint và tokenizer actual SHA chưa kiểm; 80 cases chưa frozen; nguyên nhân học thất bại chưa biết.
- **Test tái hiện / phản chứng:** Sau I1 PASS: strict load T4 step1024 exact SHA/size/P02 config, fixture 24 TRAIN 56 probe, một CPU FP32 256-step max; 900s 12GiB/1GiB STOP.
- **Đối chứng (control):** Frozen model/seed/trainer config; self-consistency oracle; nhóm heldout không trộn; tuyệt đối không historical TEST/FINAL24.
- **Điều kiện đóng bằng số đo/evidence:** Report load, token IDs, source-shift, train/probe group, step0/final loss, grad/weight delta, full-vocab vs candidate, checksum+STOP; no retry; not executed nếu HOLD.
- **Phụ thuộc:** RF-00. **Nguồn:** Q001 main contract; last-mile handoff.

### RF-02

**Công việc:** Phân loại lỗi mô hình theo failure-tree, không đoán kiến trúc

**Ưu tiên:** P1 · **Phase:** Small-4M · **Loại:** HYPOTHESIS · **State:** `WAIT_RF-01` · **Chi phí:** L (read receipt) · **Checkpoint:** `EXACT_T4_NO_CHANGE`.

- **Nghi vấn/khoảng trống:** Adherence FRESH16 FAIL có thể do objective/data/decoding/benchmark; không chứng minh model capacity.
- **Test tái hiện / phản chứng:** Đọc kết quả frozen Q001: checkpoint load, shifted loss, 24-fit, nhóm compositional/counterfactual/novel-ID/absent, full logits greedy.
- **Đối chứng (control):** 24 TRAIN vs 56 probe và restricted-vs-full 2048 logits; separate evaluator oracle.
- **Điều kiện đóng bằng số đo/evidence:** Một root-cause class có chứng cứ và counterexample; nếu không phân biệt được ghi UNRESOLVED; không sửa frozen Q001.
- **Phụ thuộc:** RF-01. **Nguồn:** L0011/L0012/L0015; Q001.

### RF-03

**Công việc:** Bản đồ quyền nguồn dataset theo hành động

**Ưu tiên:** P1 · **Phase:** P01 · **Loại:** EVIDENCE GAP · **State:** `OPEN_SOURCE_ONLY` · **Chi phí:** L · **Checkpoint:** `NO_MODEL`.

- **Nghi vấn/khoảng trống:** WP30 E0 tokenizer scope không tự cho phép GPT training; TinyStories internal owner scope cần provenance/giấy phép đúng mục đích.
- **Test tái hiện / phản chứng:** Lập file manifest source/revision/license/attribution/PII, use=tokenizer train vs checkpoint vs release, verify exact allowed actions.
- **Đối chứng (control):** P01 WP30 E0 PASS scoped, T4 private TinyStories provenance; không tải hay đưa private corpus vào public.
- **Điều kiện đóng bằng số đo/evidence:** Data lineage manifest and clear allow/hold for local training/SFT/distribution; không yêu cầu external 3 signer mang tính hình thức.
- **Phụ thuộc:** none. **Nguồn:** P01 E0; T4 science; owner scope.

### RF-04

**Công việc:** Tokenizer T4 exact inventory + roundtrip + special IDs

**Ưu tiên:** P1 · **Phase:** P01/T2 · **Loại:** EVIDENCE GAP · **State:** `WAIT_RF-00` · **Chi phí:** L/M · **Checkpoint:** `EXACT_T4_TOKENIZER`.

- **Nghi vấn/khoảng trống:** Nguồn tokenizer T4 riêng chưa được byte-verified ở Q001; mismatch ID có thể sai toàn bộ input.
- **Test tái hiện / phản chứng:** Kiểm file tokenizer expected SHA, full 2048 category taxonomy, Unicode byte roundtrip, BOS/EOS/reserved, 10 boundary tests; test tamper.
- **Đối chứng (control):** Frozen T4 tokenizer/source hash, không dùng WP30 BPE như bản thay thế, không dùng TEST fit.
- **Điều kiện đóng bằng số đo/evidence:** All IDs accounted, encode(decode) contract defined, no unsupported specials, negative tamper HOLD, source/size/hash receipt.
- **Phụ thuộc:** RF-00,RF-03. **Nguồn:** tools/pilot_t1t3/source_t2; Q001 F02.

### RF-05

**Công việc:** Checkpoint strict config & state-dict loader

**Ưu tiên:** P1 · **Phase:** P02 · **Loại:** INTEGRATION RISK · **State:** `WAIT_RF-01` · **Chi phí:** L · **Checkpoint:** `EXACT_T4_READ_ONLY`.

- **Nghi vấn/khoảng trống:** P02 defaults 2x64 khác T4 4x256; silent fallback hoặc map wrong khiến đo vô nghĩa.
- **Test tái hiện / phản chứng:** Assert vocab=2048 context256 width256 layer4 head4 LN params=3749376; torch.load(weights_only=True), strict=True, finite logits; wrong-dim reject.
- **Đối chứng (control):** Frozen P02 blob 9762343... and T4 checkpoint SHA cb9857...; tiny CPU synthetic model for no-private QA.
- **Điều kiện đóng bằng số đo/evidence:** Exact load without missing/unexpected tensors and deterministic logits against original P02; wrong checkpoint rejected without mutation.
- **Phụ thuộc:** RF-01. **Nguồn:** src/p02/transformer_core.py; Q001 main.

### RF-06

**Công việc:** Shifted next-token targets / ignore mask / gradient weights

**Ưu tiên:** P1 · **Phase:** P03 · **Loại:** HYPOTHESIS · **State:** `WAIT_RF-01` · **Chi phí:** L (synthetic CPU) · **Checkpoint:** `EXACT_NO_WEIGHT_CHANGE`.

- **Nghi vấn/khoảng trống:** One-off label alignment hoặc microbatch weighting sai có thể làm mô hình không học; chưa có runtime chứng minh.
- **Test tái hiện / phản chứng:** Tiny sequence with known hand logits; assert x=t[:-1], y=t[1:]; finite logits, grad nonzero, optimizer parameter delta, accumulation equivalence.
- **Đối chứng (control):** Direct unreduced torch.cross_entropy oracle and full-batch update; no historical science rerun.
- **Điều kiện đóng bằng số đo/evidence:** Passing regression and negative wrong-shift/mask; if no defect, mark VERIFIED_NO_BUG rather than rewrite trainer.
- **Phụ thuộc:** RF-01. **Nguồn:** src/p03/train_loop.py; T4 trainer.

### RF-07

**Công việc:** Resume, scheduler, RNG and step/byte accounting

**Ưu tiên:** P1 · **Phase:** T4 · **Loại:** INTEGRATION RISK · **State:** `WAIT_RF-05` · **Chi phí:** M · **Checkpoint:** `WEIGHT_PRESERVING_NEW_SYNTHETIC`.

- **Nghi vấn/khoảng trống:** Checkpoint T4 stores optimizer, sampler, scaler, RNG; adapter/new baseline có nguy cơ resume không tương đương.
- **Test tái hiện / phản chứng:** Synthetic N-step continuous vs K+resume N-K on new fixture; hash configs, compare optimizer step, scheduler, gradients, token target counts.
- **Đối chứng (control):** Fixed-seed uninterrupted control with same accumulation and dtype; no science TRAIN replay.
- **Điều kiện đóng bằng số đo/evidence:** Same losses/parameters within prereg numerical tolerance, no overwrite and no duplicate step; document FP16/T4 caveat.
- **Phụ thuộc:** RF-05,RF-06. **Nguồn:** tools/pilot_t4/a2_continuous1024/t4_train_science_a2.py.

### RF-08

**Công việc:** P04↔T4 checkpoint schema adapter read-only

**Ưu tiên:** P1 · **Phase:** P04 · **Loại:** INTEGRATION RISK · **State:** `WAIT_RF-05` · **Chi phí:** L · **Checkpoint:** `NO_CHECKPOINT_REWRITE`.

- **Nghi vấn/khoảng trống:** P04 v1 và T4 science checkpoint v1 khác cấu trúc, serializer chung có thể làm mất provenance.
- **Test tái hiện / phản chứng:** Synthetic payload from each schema; wrong schema/SHA/merges/model-shape reject; parse original T4 read-only only after legal custody.
- **Đối chứng (control):** P04 save/load SHA workflow + T4 READY-last metadata; strict T4 model load.
- **Điều kiện đóng bằng số đo/evidence:** Adapter can read both without rewriting checkpoint, denies unrelated schema; exact SHA maintained.
- **Phụ thuộc:** RF-05. **Nguồn:** src/p04/eval_checkpoints.py; T4 checkpoint source.

### RF-09

**Công việc:** Full-vocab greedy vs candidate-only scoring diagnostics

**Ưu tiên:** P1 · **Phase:** P04/decoding · **Loại:** HYPOTHESIS · **State:** `WAIT_RF-01` · **Chi phí:** L/M · **Checkpoint:** `EXACT_T4_READ_ONLY`.

- **Nghi vấn/khoảng trống:** FRESH16/FC01 restricted choices có thể che đi full-vocab next-token failure; không kết luận decoder bug.
- **Test tái hiện / phản chứng:** Compare top-1 among 2048 tokens, candidate rank, gold NLL, prompt format, stop-token emission on new non-TEST fixtures.
- **Đối chứng (control):** Exact P02 no-cache full logits as oracle; temperature=0/greedy; score separate from format.
- **Điều kiện đóng bằng số đo/evidence:** Agreement/rank tables by group, output token IDs with tokenizer pin; root cause decoding vs task objective reported or inconclusive.
- **Phụ thuộc:** RF-01,RF-04. **Nguồn:** Q001 F10; src/p04/eval_checkpoints.py.

### RF-10

**Công việc:** Fresh prompt-adherence measurement with valid gold/construct

**Ưu tiên:** P1 · **Phase:** Quality eval · **Loại:** EVIDENCE GAP · **State:** `DESIGN_ONLY` · **Chi phí:** M (design), H if external gold · **Checkpoint:** `EXACT_OR_NEW_CONSENTED`.

- **Nghi vấn/khoảng trống:** FRESH16 negative and P0A HOLD indicate rater/ontology/denominator may not support causal attribution.
- **Test tái hiện / phản chứng:** Design fresh source-disjoint sampling, truth/unknown/negation rules, REJECT/ABSTAIN, hidden gold, prompt byte-parity, score mask; no experiment.
- **Đối chứng (control):** Consumed FRESH16/FINAL24/TEST historical outcomes preserved as reference only; independent blinded scoring prospective.
- **Điều kiện đóng bằng số đo/evidence:** Reviewable prereg with explicit denominator/rights/threshold, no gold leakage or adaptive TEST; science NOT_EXECUTED.
- **Phụ thuộc:** RF-02,RF-03. **Nguồn:** P0A Q4 closure; docs/governance/ttm-post-q001/.

### RF-11

**Công việc:** Data audit: dedup/group split, domain balance and token fertility

**Ưu tiên:** P1 · **Phase:** Data · **Loại:** EVIDENCE GAP · **State:** `DESIGN_ONLY` · **Chi phí:** L/M · **Checkpoint:** `NO_MODEL_CHANGE`.

- **Nghi vấn/khoảng trống:** NLL tốt nhưng adherence thấp có thể do corpus thiên lệch, repeated windows hoặc instruction data scarcity.
- **Test tái hiện / phản chứng:** Compute manifest-only split-level duplicate risk, token length distribution, Unicode/VI share, prompt/answer format counts (authorized fresh source only).
- **Đối chứng (control):** Current T4 1 seed, 498287 train labels, repeated 8.417x, VAL 61122; frozen splits never changed.
- **Điều kiện đóng bằng số đo/evidence:** Versioned dataset card with coverage/group disjointness, repeat rate, seed, license; list exact data-only interventions.
- **Phụ thuộc:** RF-03,RF-04. **Nguồn:** T4 H1 adjudication; tools/pilot_t4/integrated/t4_data_pack.py.

### RF-12

**Công việc:** One-command GPT baseline orchestration (not rewriting cores)

**Ưu tiên:** P2 · **Phase:** End-to-end · **Loại:** MISSING FEATURE · **State:** `WAIT_RF-02` · **Chi phí:** M · **Checkpoint:** `NEW_RUN_NOT_FROZEN_REPLAY`.

- **Nghi vấn/khoảng trống:** P03 helper fixed batch, T4 trainer and P04 eval separate; no unified documented vertical slice.
- **Test tái hiện / phản chứng:** New CLI preflight→synthetic smoke→train→val→sample→report using exact T2/P02/P03/T4/P04 imports; test fail closed.
- **Đối chứng (control):** Same frozen data/model/oracles vs existing receipts; synthetic first, training only after separate prospective experiment selection.
- **Điều kiện đóng bằng số đo/evidence:** One new run-id with code+dataset+tokenizer+config+output SHA, correct independent metrics and no overwrite; no TEST run.
- **Phụ thuộc:** RF-04,RF-05,RF-06,RF-07,RF-08. **Nguồn:** src/p02–p04; tools/pilot_t4; scripts/record_run.py.

### RF-13

**Công việc:** Unified token-NLL + byte-bpb + grouped eval

**Ưu tiên:** P2 · **Phase:** Eval · **Loại:** MISSING FEATURE · **State:** `WAIT_RF-12` · **Chi phí:** L · **Checkpoint:** `EXACT_T4_READ_ONLY`.

- **Nghi vấn/khoảng trống:** Cross-tokenizer NLL cannot compare directly; metric denominators incomplete in some pilots.
- **Test tái hiện / phản chứng:** Implement sum log2 prob full vocab / exact UTF8 byte count, token mask documented; group bootstrap paired, zero-length reject.
- **Đối chứng (control):** Match original T4 NLL on same model/tokenizer with no TEST access; compare byte-normalized across tokenizer variants on fresh VAL only.
- **Điều kiện đóng bằng số đo/evidence:** Exact denominator & counts, NLL parity to reference on synthetic fixtures, same bytes/seed/split and CI bootstrap.
- **Phụ thuộc:** RF-12,RF-10. **Nguồn:** nanochat/loss_eval.py; T4 eval source.

### RF-14

**Công việc:** Improve train-only data mixture/quality before size

**Ưu tiên:** P2 · **Phase:** Pretrain data · **Loại:** HYPOTHESIS · **State:** `AFTER_RF-10` · **Chi phí:** M/H (new science) · **Checkpoint:** `NEW_CHECKPOINT_SAME_SHAPE`.

- **Nghi vấn/khoảng trống:** Low semantic ability may come from narrow TinyStories-only distribution or repetition, not parameter count.
- **Test tái hiện / phản chứng:** Propose duplicate-filter + balanced prompts/answers + controlled mixture; new candidate shards with clear rights and group disjoint.
- **Đối chứng (control):** Same P02 3.75M, matched TRAIN tokens/FLOPs and preprocessing; untouched fresh VAL/adherence set.
- **Điều kiện đóng bằng số đo/evidence:** Better grouped bpb/adherence with uncertainty and no unexplained regression, data card with keep/reject counts.
- **Phụ thuộc:** RF-10,RF-11,RF-12,RF-13. **Nguồn:** T4 H1; nanochat/dataset.py.

### RF-15

**Công việc:** Small instruction SFT with answer-only loss mask

**Ưu tiên:** P2 · **Phase:** Post-training · **Loại:** HYPOTHESIS · **State:** `AFTER_RF-10` · **Chi phí:** M/H (new science) · **Checkpoint:** `NEW_CHECKPOINT_FROM_EXACT`.

- **Nghi vấn/khoảng trống:** Pretrain next-token learns distribution, không bảo đảm instruction-following; no validated SFT outcome TTM.
- **Test tái hiện / phản chứng:** Few-shot supervised instruction tasks with explicit assistant-only masks and stop tokens, 100% masks unit tested.
- **Đối chứng (control):** Same P02/tokenizer and equal token/compute no-SFT continuation + output-format baseline; heldout sources.
- **Điều kiện đóng bằng số đo/evidence:** Improved fresh adherence, correct output format and counterfactual sensitivity with paired CI; report baseline bpb regression.
- **Phụ thuộc:** RF-10,RF-12,RF-14. **Nguồn:** nanochat/scripts/chat_sft.py; Deep Dive video.

### RF-16

**Công việc:** Format-only decoding controls / stop tokens

**Ưu tiên:** P2 · **Phase:** Inference · **Loại:** HYPOTHESIS · **State:** `AFTER_RF-09` · **Chi phí:** L/M · **Checkpoint:** `EXACT_T4_READ_ONLY`.

- **Nghi vấn/khoảng trống:** Incorrect format might be decoder contract mismatch without poor underlying token likelihood.
- **Test tái hiện / phản chứng:** Finite token whitelist and template constrained decoding on a new evaluation set; explicit exact-match, abstain, latency.
- **Đối chứng (control):** Unconstrained full-vocab greedy with same P02 and prompt + frozen model.
- **Điều kiện đóng bằng số đo/evidence:** Measure format validity, actual factual accuracy and false confidence; distinguish improvement due to constraints vs learning.
- **Phụ thuộc:** RF-09,RF-10. **Nguồn:** P04 generate_tokens; nanochat/engine.py.

### RF-17

**Công việc:** Objective ablation: prefix LM vs completion-only

**Ưu tiên:** P2 · **Phase:** Post-training · **Loại:** HYPOTHESIS · **State:** `AFTER_RF-15` · **Chi phí:** H (several science arms) · **Checkpoint:** `NEW_CHECKPOINT_SAME_SHAPE`.

- **Nghi vấn/khoảng trống:** Unmasked prompt loss may dominate short answer tokens; data/task format may be primary bottleneck.
- **Test tái hiện / phản chứng:** Matched-new-data pretrain continuation vs answer-only SFT vs format-only; paired no-test sample.
- **Đối chứng (control):** Identical model shape, data budget, token count/compute, checkpoint ancestry, response format, evaluator.
- **Điều kiện đóng bằng số đo/evidence:** Report NLL per subset, compliance, counterfactual effect, CI and convergence per token; no cherry-picked prompts.
- **Phụ thuộc:** RF-13,RF-15,RF-16. **Nguồn:** nanochat chat_sft loss masks.

### RF-18

**Công việc:** Verify GELU_ERF parity beyond C01-C04 (new fixtures only)

**Ưu tiên:** P2 · **Phase:** T5 · **Loại:** HISTORICAL BUG / SCOPED FIX · **State:** `WAIT_RF-12` · **Chi phí:** M/H · **Checkpoint:** `EXACT_T4_WEIGHT_AND_GGUF`.

- **Nghi vấn/khoảng trống:** Historical GELU implementation mismatch explains six scoped new fixtures, but F16/Flash ON/broad lengths not established.
- **Test tái hiện / phản chứng:** Fresh prereg full 2048-logit comparison for trained checkpoint across KV F32/F16 and Flash off/on as available.
- **Đối chứng (control):** PyTorch P02 F32 and preserved C01-C04 PASS plus historical 32 FAIL; no replay consumed sets.
- **Điều kiện đóng bằng số đo/evidence:** All arm-specific max/mean logit deltas reported, backend-version pins and per-arm PASS/FAIL vs predeclared thresholds.
- **Phụ thuộc:** RF-08,RF-09,RF-12. **Nguồn:** T5 C01-C04 adjudication; PR16.

### RF-19

**Công việc:** Production/backend compatibility qualification

**Ưu tiên:** P2 · **Phase:** T5/Ollama · **Loại:** EVIDENCE GAP · **State:** `WAIT_RF-18` · **Chi phí:** M · **Checkpoint:** `EXACT_T4_WEIGHT`.

- **Nghi vấn/khoảng trống:** Custom child Ollama 4-prompt evidence doesn't prove stock Ollama import or serving stability.
- **Test tái hiện / phản chứng:** Isolated offline import with exact trained GGUF/tokenizer/stop strings, smoke prompt and full logits where supported.
- **Đối chứng (control):** Known llama.cpp GELU_ERF reference, no running network service without owner approval.
- **Điều kiện đóng bằng số đo/evidence:** Record import supported/blocked, exact binary sha, tokenizer/byte parity, performance; no model quality claims from import.
- **Phụ thuộc:** RF-18. **Nguồn:** T5 Ollama sources/receipts.

### RF-20

**Công việc:** Fair CPU Dense/Paged/no-cache benchmark

**Ưu tiên:** P2 · **Phase:** T6 · **Loại:** EVIDENCE GAP · **State:** `AFTER_RF-12` · **Chi phí:** M · **Checkpoint:** `EXACT_T4_READ_ONLY_OR_SYNTHETIC`.

- **Nghi vấn/khoảng trống:** Current no-cache vectorized prefill vs tokenwise cache; TTFT not apples-to-apples; pool allocated same.
- **Test tái hiện / phản chứng:** Same prompt/token/run/threads/dtype; split cold/warm prefills, decode, batch, reservations, RSS peak vs sampled.
- **Đối chứng (control):** P02 no-cache direct logits; Dense/Paged active KV; T6 synthetic fixed baseline.
- **Điều kiện đóng bằng số đo/evidence:** p50/p95 TTFT TPOT throughput, errors, physical/active/logical bytes, no unearned speedup.
- **Phụ thuộc:** RF-12,RF-09. **Nguồn:** docs/t6/ scoped report.

### RF-21

**Công việc:** Unified model card/data card/training runbook

**Ưu tiên:** P2 · **Phase:** Documentation · **Loại:** EVIDENCE GAP · **State:** `OPEN_DOCS_ONLY` · **Chi phí:** L · **Checkpoint:** `NO_MODEL`.

- **Nghi vấn/khoảng trống:** Existing README/phase plan are historical snapshots; reports scattered and semantic claims easy to overstate.
- **Test tái hiện / phản chứng:** Crosslink source-only/current-science status, exact checkpoint/tokenizer/seed, license, failures, CLI design and win Python312.
- **Đối chứng (control):** T4 H1 PASS, L0015 FAIL, L0013 FAIL/L0014 PASS, PR28 HOLD all represented without rewriting receipts.
- **Điều kiện đóng bằng số đo/evidence:** Accurate Vietnamese-first docs + English terms, recipe reproducible on supported environments, explicit NOT_EXECUTED/UNKNOWN.
- **Phụ thuộc:** RF-12,RF-13. **Nguồn:** README; docs/PHASE_PLAN; docs/TRAINING_PROTOCOL.

### RF-22

**Công việc:** RMSNorm replace LayerNorm separately

**Ưu tiên:** P3 · **Phase:** P02 · **Loại:** ARCHITECTURE HYPOTHESIS · **State:** `PAUSED` · **Chi phí:** H · **Checkpoint:** `NEW_FAMILY_NOT_EXACT`.

- **Nghi vấn/khoảng trống:** Nanochat unparameterized RMSNorm differs T4 LN affine and normalization; model state not equivalent.
- **Test tái hiện / phản chứng:** New separate model family, synthetic forward/gradient parity to RMS oracle, controlled TRAIN/VAL.
- **Đối chứng (control):** Unmodified P02 LN baseline; matched budget, seed plurality, full tokenizer/split.
- **Điều kiện đóng bằng số đo/evidence:** Compare bpb vs FLOPs and update stability plus qualitative quality; report incompatibility instead of silent state-load.
- **Phụ thuộc:** RF-13,RF-17. **Nguồn:** nanochat/gpt.py; P02.

### RF-23

**Công việc:** RoPE vs learned absolute embeddings

**Ưu tiên:** P3 · **Phase:** P02 · **Loại:** ARCHITECTURE HYPOTHESIS · **State:** `PAUSED` · **Chi phí:** H · **Checkpoint:** `NEW_FAMILY_NOT_EXACT`.

- **Nghi vấn/khoảng trống:** Position semantics and state dict differ, can't drop pos vectors in frozen T4.
- **Test tái hiện / phản chứng:** Causal/position extrapolation synthetic tests, RoPE cos/sin parity, context-window edge, new training.
- **Đối chứng (control):** P02 absolute embedding under same compute/data/context; no TEST leak.
- **Điều kiện đóng bằng số đo/evidence:** Fresh heldout bpb, OOD/context length, latency/VRAM metrics and new checkpoint family documented.
- **Phụ thuộc:** RF-13,RF-17. **Nguồn:** nanochat/gpt.py.

### RF-24

**Công việc:** GQA and/or QK norm independent ablations

**Ưu tiên:** P3 · **Phase:** P02/KV · **Loại:** ARCHITECTURE HYPOTHESIS · **State:** `PAUSED` · **Chi phí:** H · **Checkpoint:** `NEW_FAMILY_REQUIRES_MAPPING`.

- **Nghi vấn/khoảng trống:** K/V shapes and cache heads changed; qk scaling semantics non-parity with T4.
- **Test tái hiện / phản chứng:** Per-change incremental no-cache/cache oracle with K/V layout negative QA and checkpoint shape reject.
- **Đối chứng (control):** MHA P02 and P05/P06; same training tokens/FLOPs, attention behavior.
- **Điều kiện đóng bằng số đo/evidence:** Quality-vs-compute, KV bytes, p95 decode, explicit no direct T4 checkpoint compatibility.
- **Phụ thuộc:** RF-20,RF-23. **Nguồn:** nanochat/gpt.py; P05/P06.

### RF-25

**Công việc:** ReLU² MLP and untied LM head one-at-a-time

**Ưu tiên:** P3 · **Phase:** P02 · **Loại:** ARCHITECTURE HYPOTHESIS · **State:** `PAUSED` · **Chi phí:** H · **Checkpoint:** `NEW_FAMILY_OR_PARTIAL_LOAD`.

- **Nghi vấn/khoảng trống:** Activation and tied embedding are semantic architecture differences; loading matching tensors doesn't imply parity.
- **Test tái hiện / phản chứng:** New two independent arms with logits/grad tests, parameter count, initialization and strict checkpoint rejection.
- **Đối chứng (control):** T4 GELU+tied baseline; equal data+compute, no conflated improvements.
- **Điều kiện đóng bằng số đo/evidence:** Report val bpb + adherence + param/memory cost; no retroactive GELU_ERF claim changes.
- **Phụ thuộc:** RF-13,RF-17. **Nguồn:** nanochat/gpt.py.

### RF-26

**Công việc:** MuonAdamW / learned scaling heuristic candidate

**Ưu tiên:** P3 · **Phase:** Training · **Loại:** OPTIMIZER HYPOTHESIS · **State:** `PAUSED` · **Chi phí:** H · **Checkpoint:** `NEW_OPTIMIZER_STATE`.

- **Nghi vấn/khoảng trống:** Different optimizer states and fused CUDA requirements; nanochat 8xH100 assumptions don't hold T4 default.
- **Test tái hiện / phản chứng:** Profile step time and optimizer memory first; synthetic shape updates and numerical control.
- **Đối chứng (control):** AdamW same P02, same effective batch/tokens/FLOPs, Pytorch T4 FP32/FP16 capabilities.
- **Điều kiện đóng bằng số đo/evidence:** Measured training speed and final bpb with errors and cost; new optimizer checkpoint, never old resume.
- **Phụ thuộc:** RF-12,RF-13. **Nguồn:** nanochat/optim.py; scripts/base_train.py.

### RF-27

**Công việc:** True paged attention GPU kernel / Flash attention

**Ưu tiên:** P3 · **Phase:** P07 · **Loại:** HARDWARE FEATURE · **State:** `PAUSED` · **Chi phí:** H (backend-specific) · **Checkpoint:** `FORWARD_COMPAT_ONLY_IF_SAME_MATH`.

- **Nghi vấn/khoảng trống:** P06 CPU block gather isn't GPU direct-page; T4 Colab GPU doesn't support FA3 path targeted H100.
- **Test tái hiện / phản chứng:** Independent numerical vs P02/P05/P06 with fixed dtype, batch/context/OOM, then profile kernel.
- **Đối chứng (control):** No-cache vs Dense vs Paged same input and hardware; rollback if accuracy/latency worse.
- **Điều kiện đóng bằng số đo/evidence:** Strict logits within declared tolerance, TTFT/TPOT p50/p95 and real allocated GPU VRAM gain; resource feasibility proven.
- **Phụ thuộc:** RF-20,RF-24. **Nguồn:** P07 PAUSED; nanochat/flash_attention.py.

### RF-28

**Công việc:** Batch scheduler: prefill/decode continuous batching

**Ưu tiên:** P3 · **Phase:** P08 · **Loại:** MISSING FEATURE · **State:** `PAUSED` · **Chi phí:** H · **Checkpoint:** `SAME_WEIGHTS_IF_MATH_PARITY`.

- **Nghi vấn/khoảng trống:** No production scheduler or admission/fairness evidence; complex concurrency can regress exact outputs.
- **Test tái hiện / phản chứng:** Multi-request interleave, cancellation, isolation, OOM, zero-on-reuse, CPU/oracle numerical parity.
- **Đối chứng (control):** Unbatched P05/P06 service on same model/workloads; QoS workload matrix.
- **Điều kiện đóng bằng số đo/evidence:** p95 TTFT/TPOT, total tokens/s, queue fairness, memory fragmentation and no cross-user leakage.
- **Phụ thuộc:** RF-20,RF-27. **Nguồn:** P08 phase plan.

### RF-29

**Công việc:** Small4M→larger GPT-like only after evidence

**Ưu tiên:** P3 · **Phase:** P09 · **Loại:** SCALING HYPOTHESIS · **State:** `PAUSED` · **Chi phí:** H (GPU and multi-seed) · **Checkpoint:** `NEW_FAMILY`.

- **Nghi vấn/khoảng trống:** No proof parameters rather than data/decoder/optimization is current binding factor.
- **Test tái hiện / phản chứng:** Small/medium family with capacity curve, matched train tokens and matched compute designs, multiple seeds/CI.
- **Đối chứng (control):** R3 best data/objective same-size model plus unchanged T4; same source rights.
- **Điều kiện đóng bằng số đo/evidence:** Higher bpb/adherence per FLOP/VRAM and cost rationale; no GO if quality not robust.
- **Phụ thuộc:** RF-14,RF-15,RF-17,RF-21. **Nguồn:** P09 phase plan; nanochat/scaling_laws.

### RF-30

**Công việc:** Serving API, observability, predictable rollback

**Ưu tiên:** P3 · **Phase:** P11 · **Loại:** MISSING FEATURE · **State:** `PAUSED` · **Chi phí:** H · **Checkpoint:** `SAME_WEIGHTS_IF_VERIFIED`.

- **Nghi vấn/khoảng trống:** Native inference parity is not full production; service auth, resource caps, concurrency unknown.
- **Test tái hiện / phản chứng:** Bounded localhost streaming API, log redaction, max tokens/context, fail-on-bad-weights, load/cancel fuzz.
- **Đối chứng (control):** CLI reference logits/latency and single-user baseline.
- **Điều kiện đóng bằng số đo/evidence:** p50/p95 load/TTFT/TPOT, 1h soak error/peak, API security tests, rollback and model card.
- **Phụ thuộc:** RF-19,RF-20,RF-28. **Nguồn:** P11 phase plan.

### RF-31

**Công việc:** Release package and Vietnamese GPT textbook

**Ưu tiên:** P3 · **Phase:** P12 · **Loại:** MISSING FEATURE · **State:** `PAUSED` · **Chi phí:** M/H · **Checkpoint:** `NO_WEIGHT_CHANGE`.

- **Nghi vấn/khoảng trống:** Historical phase docs do not imply end-to-end reproducible trained product.
- **Test tái hiện / phản chứng:** Offline clean-room reproduction by distinct reader from pinned source/config/dataset permissions, deterministic small fixture.
- **Đối chứng (control):** Known QA + science receipts, license/PII/commercial readiness audit.
- **Điều kiện đóng bằng số đo/evidence:** Reproduction recipe with exact hashes, cost and LIMITATIONS, no unsupported model capability claim.
- **Phụ thuộc:** RF-21,RF-29,RF-30. **Nguồn:** docs/COMMERCIAL_READINESS; book/OUTLINE.md.

### RF-32

**Công việc:** Windows restricted worker ACL/SID/Pipe sidecar

**Ưu tiên:** P2 · **Phase:** P01 D1 · **Loại:** SECURITY/GOVERNANCE GAP · **State:** `SEPARATE_SCOPE_HOLD` · **Chi phí:** M · **Checkpoint:** `NO_MODEL`.

- **Nghi vấn/khoảng trống:** P01 D1 sandbox ACL/SID gates historically BLOCK; not proof T4 trainer is broken.
- **Test tái hiện / phản chứng:** Scoped Windows ACL/SID/pipe negative tests only if proposed deployment actually uses D1 worker.
- **Đối chứng (control):** Docker/source-only P01 E0 result and user-owned Windows environment; no duplicate E0.
- **Điều kiện đóng bằng số đo/evidence:** Either read-only isolation path accepted for internal data or explicit engineering HOLD; avoid blocking unrelated owner-only Q001.
- **Phụ thuộc:** RF-03. **Nguồn:** P01 D1 archived branch; P01 E0.

## Luật QA và handoff cho mỗi ticket

Mỗi task tạo một report gọn (không thêm phép duyệt hành chính): `task_id`, original evidence/ref, base/head Git SHA, source file SHA-256/Git blob, **bug reproduce BEFORE/AFTER** khi thật có bug, test scope (unit / adversarial / native / science), control/negative, hiệu năng và chất lượng trên dữ liệu **mới được phép dùng**, seed/config/dtype/device, dependencies, độc lập reviewer nếu đổi runtime hoặc khoa học, verdict `FIX_VERIFIED / NO_BUG_FOUND / HOLD / FAILED / DESIGN_ONLY` và **Bước thực hiện tiếp theo**.

**Không phá invariant:** P01 E0, T4 checkpoint+TEST, FRESH16, FINAL24, T5 32 FAIL/4 PASS, T6 historical receipts và `lineage.md` là bất biến; PR #28 Draft không chạm; chỉ lập branch/PR mới với source diff khi owner cấp đúng phạm vi implementation. Tránh lập hàng loạt micro-permit hoặc hỏi lại conditional GO. Đối với bug chưa tái hiện, không merge sửa chữa đoán mò. Success của toàn roadmap là gain trong **fresh heldout bpb + adherence/semantic sensitivity**, kèm cost-quality chart, không phải số lượng QA PASS.

**Bước thực hiện tiếp theo — duy nhất:** `RF-00` theo một gói kỹ thuật exact-head, trả một `I1_PASS` hoặc `HOLD_I1`; khi và chỉ khi PASS thì `RF-01` một lần theo Q001 đã khóa.
