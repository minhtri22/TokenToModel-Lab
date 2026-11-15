# TTM-Small-4M — SM4M-F0: Architecture & Component Specification

**Operation:** TTM_SMALL4M_FOUNDATION_FIRST_COMPONENT_SPEC_AND_ROOT_CAUSE_RESEARCH_REBASE_SINGLE_GATE  
**Ngày:** 2026-11-15  
**Phạm vi:** FOUNDATION / DESIGN / SOURCE-ONLY; không chạy model, CPU science, inference, GPU, TEST hoặc FINAL; không đọc private weights, không thay checkpoint.  
**Read-only baseline:** main `fbe4a1ed58eef66f896bbfe0471926b7cc45298e` (sau PR #19 lineage-only), source P02 Git blob `9762343e06cf800b50574c2871ae1ed58537fb18`.  
**Đánh giá tài liệu:** AUTHOR_SOURCE_INSPECTION_SCOPED; **independent component QA: NOT_EXECUTED**. Không tuyên bố checkpoint bytes được xác minh lại trong lượt này.

## A. Nguồn sự thật và khác biệt giữa cấu hình mặc định với mô hình thật

| Nguồn | Tính chất | Git blob hoặc khóa |
|---|---|---|
| [src/p02/transformer_core.py](https://github.com/minhtri22/TokenToModel-Lab/blob/fbe4a1ed58eef66f896bbfe0471926b7cc45298e/src/p02/transformer_core.py) | Phương trình forward và topology | `9762343e06cf800b50574c2871ae1ed58537fb18` |
| [t4_capacity_smoke.py](https://github.com/minhtri22/TokenToModel-Lab/blob/fbe4a1ed58eef66f896bbfe0471926b7cc45298e/tools/pilot_t4/integrated/t4_capacity_smoke.py) | CONFIG T4, seed, ngân sách thực | `c9a6f256ba975228683ee7de2a1090e649110e97` |
| [t4_train_science_a2.py](https://github.com/minhtri22/TokenToModel-Lab/blob/fbe4a1ed58eef66f896bbfe0471926b7cc45298e/tools/pilot_t4/a2_continuous1024/t4_train_science_a2.py) | T4 optimizer, target masks, schedule, resume | `76c4d0155cd0736919f41682f240b47ad3d7c428` |
| [ttm_gpt2_bpe2048.py](https://github.com/minhtri22/TokenToModel-Lab/blob/fbe4a1ed58eef66f896bbfe0471926b7cc45298e/tools/pilot_t4/integrated/source_t2/ttm_gpt2_bpe2048.py) | Byte BPE, encode/decode, EOS | `fa5bd892941ba5aa6e6b2f0b2b0ae974efe297b6` |
| [t1_source_split_tokenizer.py](https://github.com/minhtri22/TokenToModel-Lab/blob/fbe4a1ed58eef66f896bbfe0471926b7cc45298e/tools/pilot_t4/integrated/t1_source_split_tokenizer.py) | TRAIN-only fit, split | `3ef500ddd8259153e7e3d4602915a51b7060a40f` |
| [T4 VAL science adjudication](https://github.com/minhtri22/TokenToModel-Lab/blob/fbe4a1ed58eef66f896bbfe0471926b7cc45298e/docs/pilot/TTM_T4_A2_REAL_SCIENCE_H1_FORMAL_ADJUDICATION_20261108.md) | Evidence of 1024-step real model | `c1a471087ae30f31a696fbf786230eff3773a0d1` |
| [T4 TEST one-shot adjudication](https://github.com/minhtri22/TokenToModel-Lab/blob/fbe4a1ed58eef66f896bbfe0471926b7cc45298e/docs/pilot/TTM_T4_TEST_64_SCIENCE_ADJUDICATION_AND_T5_TRAINED_F32_EXPORT_20261108.md) | Descriptive TEST and frozen checkpoint pin | `cf2bcb1c48d172afacb6b1f7406320851bfcbf65` |

**Sai khác quan trọng:** default của P02Config là vocab=2048, context=64, embedding=64, 2 layers, 4 heads; đây là **CPU reference default**, không phải T4 trained Small-4M. T4 khởi tạo bằng `P02Config(**CONFIG)`: vocab_size=2048, max_seq_len=256, n_embd=256, n_layer=4, n_head=4, norm_type=layernorm. Nếu dùng default để phân tích checkpoint T4 sẽ dẫn tới kết luận sai.

## B. Kiến trúc thực tế, tính theo source và cấu hình

**BPE / token IDs.** Byte-level pretokenized GPT-2-style BPE học trên 768 truyện thuộc TRAIN, 256 byte tokens ID 0..255, EOS ID 256, 1791 merges ID 257..2047, tổng vocab 2048. Round-trip strict UTF-8 theo implementation; tokenizer không dùng TEST để fit. Đọc manifest trên source không đồng nghĩa private corpus đã được đọc lại ở gate này.

**Input embedding.** Token matrix E có kích thước [2048,256]; learned absolute position matrix P [256,256]. Hidden state ban đầu h(t) = E[token(t)] + P[t]. Không dùng RoPE hoặc ALiBi trong mã nguồn P02 này.

**Causal multi-head attention.** Mỗi block có một tuyến tính QKV từ 256 sang 768; chia 4 heads, head_dim=64. Với mỗi head: A = softmax((QKᵀ / sqrt(64)) + causal_mask); mask cấm truy cập tương lai; output = projection(concat(A V)). Đây là full masked self-attention, chưa có sliding window hay GQA/MQA trong topology thực.

**Block, normalization và residual.** Pre-LayerNorm hai lần: z = x + Attn(LN1(x)); y = z + MLP(LN2(z)). MLP = Linear(256→1024, bias) → GELU → Linear(1024→256, bias). Có bốn block; sau cùng final LayerNorm. `RMSNorm` tồn tại như một lựa chọn hỗ trợ trong source nhưng **không sử dụng ở T4**. `nn.GELU()` mặc định dùng công thức chính xác; phải phân biệt với một số bản GGML GELU xấp xỉ trong T5.

**Output và loss.** Logits [batch,time,2048] bằng tuyến tính không bias với `head.weight = tok.weight` (weight tying). Loss huấn luyện là next-token cross entropy; T4 tính loss với nhãn `ignore_index=-100` và `reduction=sum / 4096`. Không có classification head, explicit retrieval, external memory hoặc contrastive head trong checkpoint T4 gốc.

**Tham số — phép tính tĩnh (không chạy model):**
- Token embeddings: 2048×256 = 524288; position embeddings: 256×256 = 65536.
- Mỗi block: QKV/projection = 263168; FFN = 525568; 2 LayerNorm = 1024; tổng = 789760.
- Bốn block = 3159040; final LayerNorm = 512.
- **Tổng unique parameters = 524288 + 65536 + 3159040 + 512 = 3749376**; output head tied nên không đếm thêm 524288.

## C. Huấn luyện T4 thực tế, không nhầm với synthetic P03

P03 `src/p03/train_loop.py` là vòng synthetic fixed-batch CPU riêng, sử dụng default TrainConfig 80 steps / lr .003. **Không dùng các giá trị P03 này để mô tả thực nghiệm T4 thật.**

T4 A2: seed 20261108; 1024 optimizer steps; mỗi step đúng 4096 valid next-token labels (tổng 4194304 target exposures, không phải 4194304 token độc lập); batch của các window 256-token có padding masked; precision FP16, microbatch_windows=8 theo receipt. Optimizer AdamW lr=3e-4, betas=(.9,.95), eps=1e-8, weight_decay=.1; clip global gradient norm 1.0. Schedule LambdaLR 32 warmup steps, sau đó cosine decay về 10% peak; checkpoint READY-last tại 256/512/768/1024, giữ optimizer, scheduler, sampler và các RNG state. TRAIN 2048 stories (có lặp exposure), VAL 256; TEST 64 niêm phong đã dùng một lần. Trong TRAIN có 498287 vị trí target độc lập theo báo cáo, được lấy mẫu lặp bình quân ~8.417 lần.

Checkpoint step1024 **reported SHA-256** `cb985751795c8328ad65acf7ca4c1033ce35182c1bfbdb8c38550de629cb271b`. Trạng thái: `PIN_VERIFIED_BY_PRIOR_T4_AUDIT`, **không phải `BYTE_REVERIFIED_THIS_GATE`**.

## D. Biến thể sinh và giới hạn suy luận

P04 `generate_tokens` dùng top-k sampling có seed; với top_k=1 tương đương argmax, nhưng checkpoint T4 được đánh giá chất lượng bằng nhiều runner khác nhau (greedy/nucleus) và cần tách theo từng receipt. Cửa sổ tối đa 256; prompt + generated tokens phải phù hợp context của runner. Kết quả GGUF/Ollama compatibility hay T6 KV cache là **QA thực thi**, không chứng minh năng lực bám prompt.

## E. Bảng xác nhận và lỗ hổng F0

| Mệnh đề | Gate / bằng chứng |
|---|---|
| Topology GPT2-like, learned absolute positions, tied embedding, 4×4 heads | SOURCE_PINNED |
| Chính xác 3,749,376 unique params theo cấu hình | SOURCE_DERIVATION_MATCHES_T4_RECEIPT |
| TRAIN-only tokenizer fitting và split sizes trong source/protocol | SOURCE_PINNED; private source bytes NOT_REVERIFIED |
| 1024-step trained real T4 và 4 checkpoint SHA prior audit | PRIOR_SCOPED_SCIENCE_PASS; NO_NEW_EXECUTION |
| Truy cập đúng dữ kiện khi sinh, internal representation, attention attribution | **NOT_ESTABLISHED** |
| Nhiều seed, quyền raw corpus, byte readback checkpoint trong gate này | **NOT_EXECUTED / NOT_REVERIFIED** |
| Independent F0 QA và science release mới | **NOT_EXECUTED / NOT_GRANTED** |

**F0 closure đề nghị:** `SOURCE_COMPONENT_SPEC_COMPLETED_AUTHOR_REVIEW_ONLY`. Không điều chỉnh source, weights, checkpoint, dataset, lineage hoặc phase. Không suy từ định nghĩa kiến trúc rằng attention/capacity đã được chứng minh là nguyên nhân chất lượng.
