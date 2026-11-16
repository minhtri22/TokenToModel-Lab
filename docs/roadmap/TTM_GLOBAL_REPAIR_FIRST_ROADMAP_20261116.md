# TTM — Global Repair-First Roadmap (GPT-like, nanochat-informed)

**Ngày lập:** 2026-11-16 · **Tính chất:** tài liệu lập kế hoạch / source-and-evidence review, **không phải kết quả thực nghiệm mới**.  
**TTM main khóa khi kiểm toán:** [f7a0a5874e8fd895c8ea8d17ceff393a4d4917a3](https://github.com/minhtri22/TokenToModel-Lab/tree/f7a0a5874e8fd895c8ea8d17ceff393a4d4917a3) · **nanochat tham chiếu:** [92d63d4e8bb4df75c3b71618f31ddde2378b2bcd](https://github.com/karpathy/nanochat/tree/92d63d4e8bb4df75c3b71618f31ddde2378b2bcd).  
**Danh sách triển khai chi tiết:** [TTM_GLOBAL_REPAIR_FIRST_BACKLOG_20261116.md](TTM_GLOBAL_REPAIR_FIRST_BACKLOG_20261116.md), [CSV máy đọc](TTM_GLOBAL_REPAIR_FIRST_BACKLOG_20261116.csv).  
**Hạn chế kiểm toán:** đã đọc main, các entry/evidence được chọn, code P02–P06, T4, source/evidence và PR #28, PR P02/P05/P06/T5/T6, so sánh với nanochat. Đây là **kiểm kê dựa trên chứng cứ truy xuất được**, không phải tuyên bố đã chạy lại chương trình hoặc đọc từng byte của mọi nhánh/binary/private checkpoint. Kết luận về những lỗi chưa tái hiện được ghi **HYPOTHESIS/UNVERIFIED**, không biến thành bug đã xác nhận.

## 0. Kết luận vận hành

**Ưu tiên tuyệt đối:** giải quyết Small-4M \`TTM-SM4M-DIAG-Q001\` đang \`HOLD_I1\` bằng **một lượt tích hợp last-mile kỹ thuật**, rồi **một lượt I2 duy nhất nếu I1 thực sự PASS**. Không triển khai RoPE/GQA/Muon/Flash/P07, không tăng kích thước model, không đổi checkpoint gốc trong khi chưa biết mô hình vấp ở loading/label-shift/optimizer/overfit/generalization hay decoding.

**Không có bằng chứng rằng toàn bộ P01–P06 đều lỗi.** P02–P06 đã merge và có QA scoped. Phân biệt: (A) bug thực sự được chứng minh; (B) tính năng còn thiếu hoặc bằng chứng chưa đủ; (C) hạn chế nghiên cứu, không phải bug; (D) nghi vấn cần test phân biệt. TTM đã có kết quả khoa học T4 VAL tốt hơn bigram, đồng thời FRESH16 V2 thất bại theo benchmark đã khóa — khoảng cách đó là mục tiêu cải tiến, không được làm mờ bởi số lượng test xanh.

### Bốn mốc không được đánh tráo

1. **T4**: mô hình P02 **3.749.376 tham số** (vocab 2048, context 256, embedding 256, 4 layer/4 head, LayerNorm). Một T4 Colab 1.024 step, VAL model NLL **3,5223388517** vs bigram TRAIN-only **3,9972314170** (**11,880537%** tốt hơn); TEST 64 truyện **3,48359107334** vs **3,97360374532** (**12,3316944%** mô tả), đã dùng một lần. [T4 adjudication](../pilot/TTM_T4_A2_REAL_SCIENCE_H1_FORMAL_ADJUDICATION_20261108.md); [TEST report](../pilot/TTM_T4_TEST_64_SCIENCE_ADJUDICATION_AND_T5_TRAINED_F32_EXPORT_20261108.md). Không lấy VAL/TEST làm tập tuning tương lai.
2. **Small-4M prompt adherence**: [P0-A evidence gap](../governance/ttm-post-q001/TTM_POST_P0A_Q001_EVIDENCE_GAPS_AND_NEXT_QUESTION_PRIORITY_MATRIX_20261116.md) ghi L0015 FRESH16 V2 **H1 0/16, H2 0/8, FAIL scoped**; không suy ra một nguyên nhân duy nhất hoặc phủ nhận VAL NLL T4.
3. **T5**: L0013 strict 32/32 **FAIL** lịch sử; sửa biến thể **GELU → GELU_ERF** có đối chứng D01/D02 và xác nhận mới C01–C04 **PASS 4/4**, tối đa max-abs khoảng **5,725e-6** khi KV F32/Flash OFF. [C01–C04](../pilot/TTM_T5_GELU_ERF_C01C04_HELDOUT_STRICT_PASS_INDEPENDENT_ADJUDICATION_AND_PR16_MERGE_REVIEW_20261110.md). **Không** tuyên bố 32 FAIL cũ đã biến thành PASS, hay stock Ollama/Flash ON/F16 đều chuẩn.
4. **P05/P06/T6**: parity CPU synthetic đạt scoped; [T6](../t6/TTM_T6_CPU_NO_CACHE_DENSE_PAGED_AB_SCOPED_RESULTS_20261109.md) **không chứng minh tăng tốc** hay giảm pool vật lý. Hai request cùng pool allocated 65.536 byte; Paged active reserved thấp hơn Dense, không đồng nghĩa tổng RAM giảm. P07/P08 còn tạm dừng.

## 1. Kiểm kê repair-first theo thành phần

| Thành phần | Điều đã chứng minh / đã merge | Lỗi, khoảng trống hoặc nghi vấn **còn mở** | Mã / evidence | Quyết định |
|---|---|---|---|---|
| P01 data/BPE | E0 30 revision Wikipedia VI; BPE 2048; TRAIN/VAL/TEST 24/3/3; scoped PASS | Quyền E0/BPE không mặc nhiên là quyền training GPT hoặc phát hành; nhánh D1 Windows security ACL/SID còn HOLD; tokenizer T4 TinyStories **khác scope** WP30, phải pin đúng artifact | [P01 E0](../p01/P01_F1_WP30_E0_FORMAL_ADJUDICATION_AND_P02_OPEN_GATE_20261107.md), \`tools/pilot_t1t3/source_t2/\` | Không rerun E0; dựng hợp đồng tokenizer/dataset và rights tối thiểu cho pipeline |
| P02 Transformer | \`src/p02/transformer_core.py\` đã merge; shape, causal, gradient parity synthetic | P02 mặc định 2-layer/64-dim **khác** T4 4-layer/256-dim; architecture hardcode learned position + LayerNorm + GELU + tied LM head; không phải bug nhưng giới hạn tương thích nếu đưa nanochat vào | [P02 source](../../src/p02/transformer_core.py) | Cố định checkpoint/config, test strict state-dict và exact forward/reference |
| P03 train loop | \`src/p03/train_loop.py\` AdamW, warmup/cosine, accumulation, synthetic overfit | \`train_fixed_batch\` cố ý không đọc corpus/checkpoint/heldout; chưa phải unified production trainer. Kiểm nghiệm label shift/gradient step và resume parity ở đường T4; không suy luận bug optimizer | [P03 source](../../src/p03/train_loop.py) | Tạo adapter CLI dùng P03/T4 code, không rewrite optimizer |
| P04 eval/checkpoint | SHA pin, no-overwrite checkpoint, synthetic heldout, sampling | P04 \`ttm.p04.model_checkpoint.v1\` và T4 \`ttm.t4.science.checkpoint.v1\` có **hai schema riêng**. Cần adapter đọc không đổi byte, tách decode/full-vocab vs candidate scorer, tránh nhầm TEST | [P04 source](../../src/p04/eval_checkpoints.py) | Adapter kiểm chứng metadata, không serialize lại frozen artifacts |
| P05 Dense KV | Windows CPU **PASS_SCOPED**; V1 PowerShell report false negative được giữ lịch sử | Nghi vấn riêng trong \`PSObject.Properties.Count\` runner V1 (không phải lỗi Dense thuật toán); thiếu full model workload/serving throughput | [P05 adjudication](../p05/P05_WINDOWS_CPU_V1_FALSE_NEGATIVE_ADJUDICATION_AND_P06_GATE_20261107.md) | Chỉ sửa parser nếu dùng lại; không rerun QA lịch sử |
| P06 Paged KV | CPU native 8/8 + independent 5/5; isolation/OOM/zero-on-reuse scoped | CPU gather/reconstruct KV không phải paged GPU kernel; chưa đo thật trên model tải dài/concurrency | [P06 adjudication](../p06/P06_WINDOWS_CPU_FORMAL_ADJUDICATION_AND_P07_GATE_20261107.md) | Giữ làm oracle, không ưu tiên kernel |
| T4 trainer/checkpoint | 1024-step trained science, READY/resume và private checkpoint SHA; VAL H1 PASS | Khả năng học ngữ nghĩa/prompt adherence không được chứng minh; cần chẩn đoán đường loss/overfit/outputs của **chính** checkpoint, không đọc lại TEST | [T4 source](../../tools/pilot_t4/a2_continuous1024/t4_train_science_a2.py) | Ưu tiên Q001 thay vì scaling |
| Small-4M Q001 | Q1 đã đăng ký, owner đã GO **có điều kiện**; native no-model QA ở HEAD cũ có receipt | **PR #28 vẫn Draft, I1 HOLD, I2 NOT_EXECUTED**; owner-internal last-mile source chưa qualified native; hard job cap chưa wired; original checkpoint/tokenizer/80 cases chưa readback; distinct QA chưa có trên mã cuối | [PR #28](https://github.com/minhtri22/TokenToModel-Lab/pull/28), [Issue #29](https://github.com/minhtri22/TokenToModel-Lab/issues/29), [owner amendment](https://github.com/minhtri22/TokenToModel-Lab/blob/8bded8612024c583faa92e79f5167f854703e43c/docs/governance/ttm-small4m-direct-diag/TTM_SM4M_DIAG_Q001_OWNER_INTERNAL_SCOPE_AND_LAST_MILE_AMENDMENT_20261116.md) | **R0 → R1**, không tăng micro-permit; không chạm PR #28 trong roadmap |
| T5 GGUF/llama.cpp/Ollama | C01–C04 GELU_ERF confirmed scoped; riêng custom Ollama 4-prompt raw-logit QA trong branch evidence | Không có broad trained parity/stock runtime/cross-precision; top-1 không đủ thay full logits | [T5 report](../pilot/TTM_T5_GELU_ERF_C01C04_HELDOUT_STRICT_PASS_INDEPENDENT_ADJUDICATION_AND_PR16_MERGE_REVIEW_20261110.md) | Giữ PyTorch P02 là tham chiếu; transport sau chất lượng |
| T6 cache A/B | Python/CPU synthetic parity; TTFT/TPOT có receipt | Cách vector hóa no-cache vs incremental cache không cân xứng, Paged prefill lặp token; chưa phục vụ thật hoặc chứng minh nhanh | [T6 report](../t6/TTM_T6_CPU_NO_CACHE_DENSE_PAGED_AB_SCOPED_RESULTS_20261109.md) | Benchmark fairness sau baseline |
| Serving P07–P11 | Thiết kế kế hoạch ở \`docs/PHASE_PLAN.md\` | GPU direct-page kernel, batching scheduler, streaming API, workload lâu dài **chưa có kết quả production** | [Phase plan](../PHASE_PLAN.md) | Đợi baseline/data/post-train |

**Chú ý quan trọng về thời điểm:** PR #28 HEAD được đọc lúc kiểm toán là \`8bded8612024c583faa92e79f5167f854703e43c\`; không pin nó thay cho HEAD khi agent triển khai sau này. Evidence native trước đó gắn source \`77f6e946975a8b5cd5859297f6d0f161bb13f629\`, không tự động bao phủ last-mile mới. Owner đã tuyên bố **nghiên cứu nội bộ phi thương mại**: policy ba chữ ký Ed25519 riêng cho internal Q001 đã được **thay bằng owner-scoped admission candidate**, nhưng **quyền từ nhà cung cấp dữ liệu và byte custody không được tự suy là đã xác minh**. Xem [last-mile handoff](https://github.com/minhtri22/TokenToModel-Lab/blob/8bded8612024c583faa92e79f5167f854703e43c/docs/governance/ttm-small4m-direct-diag/TTM_SM4M_DIAG_Q001_LAST_MILE_CODEX_ONEPACK_HANDOFF_20261116.md).

## 2. Roadmap thi hành theo thứ tự, không micro-permits

| Wave | Đầu vào bắt buộc | Triển khai tối thiểu | Bằng chứng thoát wave |
|---|---|---|---|
| **R0 — Last-mile Q001** | Exact PR #28 mới nhất và owner internal-scoped declaration | **Một gói**: native Python 3.12/PowerShell 5.1 QA cho modules mới, Job Object conservative committed-memory cap + sampled tree RSS (2 thước đo khác nhau), root/host/nonce/owner admission negatives, SHA thực checkpoint/tokenizer và 80-case fixture, một review độc lập | \`I1_PASS_SCOPED_INTERNAL_RESEARCH\` **hoặc** một \`HOLD_I1\` có blocker kỹ thuật cụ thể. Không lấy số test thay cho run permission |
| **R1 — Một I2 Q001** | Chỉ sau I1 thật PASS, sử dụng owner GO có điều kiện **đã có** | Một run CPU FP32 seed 20261116, train 24, probe 56, tối đa 256 bước, 900s/12GiB sampled tree RSS + hard job committed cap/1GiB output. Không đổi checkpoint và fixture, không retry | Quyết định dựa trên measured loading, shifted NLL, gradient/update, 24-case fit, compositional/counterfactual/novel-ID, restricted vs full-vocab logits; không đụng TEST/FINAL24 |
| **R2 — GPT baseline end-to-end** | I2 verdict, input/private custody hợp lệ | Kết nối **lại code có sẵn** P01/T2 → P02 → P03/T4 → P04/T4 eval → P05/P06 (optional) → T5 (export optional). New orchestration chỉ ở nhánh sau; synthetic CPU smoke trước, training mới cần quyết định thực nghiệm riêng | One-command (sau khi implement), exact config/data/tokenizer/checkpoint SHA, resume equivalence, train+val NLL, bpb, greedy/full logits và report bảo toàn run artifacts |
| **R3 — Data & post-training** | Baseline và fresh non-TEST đánh giá định nghĩa đúng | Data audit, dedup/group-disjoint, train-only tokenizer, loss-mask response, SFT nhỏ, task conditioning, constrained formatting, length/coverage ablations, equal token/compute budgets; một biến/lượt | Paired fresh heldout NLL/bpb + prompt adherence accuracy + counterfactual sensitivity + format validity + confidence/uncertainty; mô hình không mất capability nền vô cớ |
| **R4 — Architecture research** | R2/R3 evidence cho thấy data/objective không đủ; old checkpoint bất biến | A/B riêng từng feature từ nanochat: RMSNorm, RoPE, GQA, QK norm, ReLU², untied head, sliding window, optim/precision. Phải báo checkpoint compatibility trước run | Chênh lệch **VAL bpb vs bytes**, OOD paired score và tokens/s/MFU/VRAM ở cùng compute/token budget, nhiều seed nếu có thể; không chỉ QA |
| **R5 — Scaling/inference/serving** | Có cải thiện R3/R4 thật, chi phí capacity đo | Small → medium model có khả năng tài trợ; inference reference → fair KV benchmark → scheduler → API/observability → release docs | Quality-vs-FLOPs/parameters curve + p50/p95 TTFT/TPOT/tokens/s/VRAM trên cùng tải; replay metadata và license cards |

## 3. Cây chẩn đoán Q001 phải phân biệt nguyên nhân

\`\`\`text
Q001 I1 HOLD? ──yes──> Giữ nguyên science; một blocker ledger, không thêm signer/micro-permit
        |
        no
        v
Checkpoint/tokenizer/config không khớp? ──> custody / schema / real bytes (KHÔNG đổi model)
        |
        v
Shifted targets / masked loss / gradient / weight delta sai? ──> repair trainer/scorer
        |
        v
24 TRAIN không fit? ──> inspect optimizer/update/representation/capacity, đo trước khi quy tội
        |
        v
TRAIN fit nhưng fresh 56 probes kém? ──> hypothesis: generalization/data/objective
        |
        v
candidate-scoped likelihood OK, full-vocab greedy sai? ──> format/tokenization/
                                                      output competition/decoding
        |
        v
Không kết luận semantic mastery từ lookup task; proposal dữ liệu nguồn thật riêng
\`\`\`

**Không sửa bài thi giữa phép đo.** Giữ frozen 24/56, exact Q001 labels, seed, thresholds và STOP. Accuracy theo mỗi nhóm, NLL, delta weight và per-token full 2048 logits *chỉ trong phạm vi phép đo được quyền*, đối chiếu oracle máy không suy diễn một loại lỗi từ metric gộp. Nếu I2 fail vì tài nguyên: \`HOLD_RESOURCE_INCOMPLETE\`, không ghi science FAIL. Không dùng lại FRESH16/FINAL24/TEST để tune.

## 4. GPT baseline “vertical slice” — tận dụng nguồn có sẵn

| Stage | TTM source nên tái sử dụng | Adapter còn cần; acceptance |
|---|---|---|
| 0. Dữ liệu và quyền | P01 F1 E0 + T1/T2 TinyStories private pack \`tools/pilot_t1t3/\`, \`tools/pilot_t4/integrated/t4_data_pack.py\` | dataset manifest, split/group leakage/dedup, UTF-8/PII/license scope; **không coi WP30 tokenizer và TinyStories tokenizer là cùng checkpoint** |
| 1. BPE | \`tools/pilot_t1t3/source_t2/ttm_gpt2_bpe2048.py\` và T4 source T2 | \`encode/decode\`, special/reserved complete 2048 ID inventory, tokenizer SHA, OOV/roundtrip, no TEST fit |
| 2. Model | \`src/p02/transformer_core.py\` | exact T4 \`P02Config\`, \`load_state_dict(strict=True)\`, causal targets shifted by 1; 3.749.376 params; baseline config pin |
| 3. Train | \`src/p03/train_loop.py\` (small overfit), \`tools/pilot_t4/a2_continuous1024/t4_train_science_a2.py\` (real loop) | stream/pack, gradient accumulation, AdamW, LR schedule, seed, AMP on T4, atomic save/resume, token budget; **do not call fixed-batch helper a corpus trainer** |
| 4. Evaluate | \`src/p04/eval_checkpoints.py\` + \`tools/pilot_t4/integrated/t4_eval.py\` | schema adapter T4↔P04 (read-only), separate \`val\` and \`train\` metrics, zero TEST contamination, NLL and bpb, answer-only/format metrics when post-train exists |
| 5. Decode | \`src/p04/eval_checkpoints.py\` + \`src/p05/\` + \`src/p06/\` | greedy/full-vocabulary logits first; cache parity only on same checkpoint/dtype; stochastic decode seed/stop tokens; error on context overflow |
| 6. Export | trained T5 GGUF exporter and native GELU_ERF evidence | optional, **not** reference for Q001; require tokenizer/weight tensor/prompt/full-logit parity on newly admitted fixtures before serving claim |
| 7. Report | \`scripts/record_run.py\`, \`lineage.md\` policy | implement a **single versioned run manifest** with code+data+config hashes, exact commands, device+dtype, NLL/bpb+quality, total wall/tokens/s/peak usage, reproduce/negative tests and scientific verdict separately |

**CLI thiết kế (chưa tồn tại / không được chạy trong roadmap):**
\`\`\`text
ttm baseline preflight --manifest <frozen-manifest> --mode source-only
ttm baseline smoke --fixture synthetic --device cpu --python 3.12
ttm baseline train --config <new-registered-run-config> --data <authorized-train> --out <new-run-id>
ttm baseline evaluate --checkpoint <sha-locked> --split val --out <new-report>
ttm baseline generate --checkpoint <sha-locked> --prompt-file <fresh-eval> --decode greedy
ttm baseline export --checkpoint <sha-locked> --format gguf --backend checked
\`\`\`
Đây là **hợp đồng mục tiêu**, không lệnh có thể chạy ngay. Runner phải \`fail-closed\` khi source rights/byte pin sai, không ghi đè/đổi bộ khóa. Trong quá trình sửa, test synthetic mới không được tự tính như science; inference TEST lịch sử bị cấm.

## 5. Thước đo “TTM đã tiến bộ” (phải có đối chứng)

**Cặp số bắt buộc:** (i) **khả năng mô hình**: trên VAL/benchmark fresh không trùng, NLL theo token, **bits-per-byte (bpb)** = \`-Σ log2 p(target_token) / số byte UTF-8 của cùng văn bản đánh giá\` (mask/chính sách BOS/EOS phải ghi rõ), accuracy instruction/format, sensitivity under matched counterfactuals, confidence khoảng tin cậy theo **truyện / nguồn / group**; (ii) **hiệu quả kỹ thuật**: tokens/s, wall-clock, số token TRAIN, FLOPs ước tính và cách tính, peak GPU/RAM, TTFT/TPOT trên cùng tải. Đừng so NLL hai tokenizer khác nhau khi không quy về cùng byte/denominator và split.

**Đối chứng tối thiểu (đề xuất chưa freeze):** untouched 3.75M T4 baseline; fresh same-architecture continuation; quality/dedup data-only; prompt-conditioned SFT data; inference format-only; architecture candidate nếu các nhánh trên không đủ. Giữ **cùng effective information budget, cập nhật optimizer budget, task split và evaluator**; báo cả matched-token lẫn matched-FLOPs khi chênh kiến trúc. Đo effect size, CI theo nhóm, số loại REJECT/ABSTAIN và denominator; không chọn thí nghiệm theo TEST đã dùng.

**Mốc chấp nhận cho kế hoạch tương lai (chưa phải frozen thresholds):** quality improvement phải có CI/paired controls phản biện được và giữ hoặc cải thiện VAL bpb tương ứng; overfit chứng minh bằng exact 24-case metric theo frozen Q001; serving chỉ công bố nhanh/tiết kiệm khi p50/p95 trên cùng hardware/batch/sequence/generation/cold-warm và memory reporting; scaling chỉ GO nếu đường chất lượng-vs-compute cải thiện và nguồn dữ liệu hợp lệ. Các threshold định lượng (vd. mục tiêu +10 điểm % adherence) là **đề xuất** cần prereg trước phép đo, không gán sau khi thấy kết quả.

## 6. Nanochat: học phương pháp, không “copy rồi đổi checkpoint”

Tham khảo upstream tại commit trên: [\`nanochat/gpt.py\`](https://github.com/karpathy/nanochat/blob/92d63d4e8bb4df75c3b71618f31ddde2378b2bcd/nanochat/gpt.py), [\`scripts/base_train.py\`](https://github.com/karpathy/nanochat/blob/92d63d4e8bb4df75c3b71618f31ddde2378b2bcd/scripts/base_train.py), [\`scripts/chat_sft.py\`](https://github.com/karpathy/nanochat/blob/92d63d4e8bb4df75c3b71618f31ddde2378b2bcd/scripts/chat_sft.py), [\`nanochat/engine.py\`](https://github.com/karpathy/nanochat/blob/92d63d4e8bb4df75c3b71618f31ddde2378b2bcd/nanochat/engine.py), [\`nanochat/loss_eval.py\`](https://github.com/karpathy/nanochat/blob/92d63d4e8bb4df75c3b71618f31ddde2378b2bcd/nanochat/loss_eval.py), [\`runs/speedrun.sh\`](https://github.com/karpathy/nanochat/blob/92d63d4e8bb4df75c3b71618f31ddde2378b2bcd/runs/speedrun.sh).

| Nâng cấp / pattern | Tương thích với T4 frozen weights? | Chi phí và ưu tiên |
|---|---|---|
| **Eval bpb, run manifest, dataloader restart, response-only loss-mask** | **Có** về format trọng số nếu chỉ thay metric/data/target loss; fine-tuning tiếp tạo **checkpoint mới** | **Low→Medium**, R2/R3; ưu tiên |
| **SFT với same P02 + AdamW** | Có thể khởi tạo từ weight T4 nếu tokenizer/config **trùng chính xác**; optimizer/trainer state cần xử lý riêng | **Medium**, R3; chỉ sau Q001 |
| **Learned absolute positions → RoPE** | **Không tương đương**: bỏ/đổi position vectors; dù giữ qkv shapes, logits thay | **Medium/High**, R4, checkpoint family mới |
| **LayerNorm → unparameterized RMSNorm** | **Không** trực tiếp: LN affine vs RMS, scale semantics khác; không gọi conversion là parity | **Medium**, R4 |
| **MHA → GQA** | **Không**: K/V projection shapes/head layout thay; yêu cầu surgery, retrain/validate | **High**, R4/R5 |
| **GELU → ReLU², tied → untied LM head, value residual, q scaling/QK norm** | **Không** hoặc chỉ load một phần; dù tensor sizes đôi khi trùng, function khác; giữ fresh baseline | **Medium/High**, R4 |
| **Sliding-window local/full attention, FA3** | Cơ chế attention/khả năng backend khác; FA3 **không phù hợp mặc định Colab T4** | **High**, R4/R5, không mở trước chất lượng |
| **MuonAdamW/fused optimizer/muP-style depth heuristic/FP8** | Forward có thể giữ model nhưng **optimizer state không tương thích**; T4 không là môi trường H100, không nhập default tốc độ của nanochat | **High**, R4/R5; chỉ khi profiling chứng minh bottleneck |
| **Nanochat Engine, KVCache batching, chat CLI** | TTM P02+T5 không cùng chat special tokens/model API; cần adapter/QA. Không direct-import để tuyên bố tương thích | **Medium/High**, R5 |

**Nguyên tắc checkpoint:** \`LOAD_EXACT\` (same architecture/tokenizer + strict weights), \`LOAD_WEIGHT_ONLY_NEW_RUN\` (optimizer reset, có báo rõ), \`REQUIRES_CONVERSION\` (mapping tensor, chấp nhận mismatch), \`NEW_FAMILY\` (retrain); **không bao giờ gán \`LOAD_EXACT\` cho RoPE/RMSNorm/GQA/ReLU² chỉ vì code import thành công**.

**Cost bands tương đối, không phải USD đã đo:** Low=không train GPU hoặc chỉ fixture CPU; Medium=T4/CPU short prospective run cùng model; High=training mới, nhiều seed hoặc H100/multi-GPU/serving benchmarks. Bộ \`nanochat runs/speedrun.sh\` dùng hạ tầng 8×H100 và mục tiêu GPT-2-grade; không chuyển thời gian/chi phí từ leaderboard sang TTM 3.75M/T4.

## 7. Video kỹ thuật Karpathy và nơi áp dụng

1. [Let's build GPT: from scratch, in code](https://www.youtube.com/watch?v=kCc8FmEb1nY) → audit P02 causal attention, next-token loss, greedy sampling; reference cho baseline shape/forward.
2. [Let's build the GPT Tokenizer](https://www.youtube.com/watch?v=zduSFxRajkE) → rà soát byte BPE, Unicode/regex/special tokens, encode/decode và tokenizer artifact custody; **không** thay T4 tokenizer sau khóa.
3. [Let's reproduce GPT-2 (124M)](https://www.youtube.com/watch?v=l8pRSuU81PU) → warmup/AdamW/gradient accumulation, loader, validation, overfit một batch, profiling, checkpoint; tiếp thu *thứ tự debug trước tối ưu*.
4. [Deep Dive into LLMs like ChatGPT](https://www.youtube.com/watch?v=7xTGNNLPyMI) → tách pretraining next-token, SFT hội thoại, RL; SFT là ứng viên sau data/objective repair, **không** là chứng cứ TTM đã đạt instruction-following.
5. [nanochat upstream](https://github.com/karpathy/nanochat/tree/92d63d4e8bb4df75c3b71618f31ddde2378b2bcd) → tham khảo cấu trúc script tokenization → base training/eval → chat SFT/eval/RL → CLI inference. Cần thiết kế TTM tương đương, không chép kết quả nanochat thành kết quả TTM.

## 8. Quy tắc branch, QA, evidence và khoa học

- Roadmap này **không** merge, sửa PR #28/issue, chạy khoa học, thay \`lineage.md\`, unseal TEST/FINAL24, xóa artifact, truy cập private checkpoint, cấp quyền mới hay tự mở P07.
- Một kỹ thuật change PR → đúng **một review package**: base+head+blob/SHA256, test tái hiện **trước sửa** (nếu bug), test mới/negative QA **sau sửa**, config/dataset version, numerical/quality comparator, runtime/chi phí, scoped verdict, link artifact. Independent QA **theo rủi ro** (không bắt buộc 3 signer cho local owner-only engineering).
- **Bug repair:** viết failing regression test rồi tối thiểu diff; invariant pass, không đổi frozen source để làm cũ “PASS”.
- **Science improvement:** kết quả khoa học đo mới được phép ghi \`lineage.md\` append-only khi đúng chính sách; không ghi mọi infrastructure QA như bước đột phá mô hình.
- **Quality-first stop rule:** nếu chưa có paired independent data/quality evidence, tuyệt đối không phát biểu scaling/architecture “cải thiện GPT-like”.
- **Tài liệu:** update \`docs/PHASE_PLAN.md\`, \`docs/TRAINING_PROTOCOL.md\`, \`docs/ARCHITECTURE.md\`, model/dataset card, reproducibility/cost guide sau khi các wave đạt, bằng PR docs riêng có source pin; README snapshot lịch sử không tự sửa.

## Bước thực hiện tiếp theo — duy nhất

**\`TTM_SM4M_DIAG_Q001_LAST_MILE_NATIVE_JOB_MEMORY_OWNER_SCOPE_BYTE_CUSTODY_AND_SINGLE_I1_ADJUDICATION\`**: nhận chính xác latest PR #28 HEAD; native-test owner-internal admission/Win32 RSS, tích hợp và verify hard Job Object cap, check nguyên checkpoint/tokenizer & fixture 80 ca, một independent exact-source reviewer xuất đúng \`I1_PASS_SCOPED_INTERNAL_RESEARCH\` hoặc \`HOLD_I1\`. Nếu PASS mới dùng conditional GO sẵn có cho **một** I2 256-step; nếu HOLD, xuất một blocker ledger chứ không mở tiếp micro-permit. **Roadmap là tư liệu cho agent thi hành, không tự triển khai nhiệm vụ đó.**
