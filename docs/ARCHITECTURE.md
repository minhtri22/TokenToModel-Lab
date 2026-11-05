# Kiến trúc hệ thống

```
Corpus + licenses → Dataset prep → Tokenizer → Token IDs
                                                ↓
                                     Decoder-only Transformer
                                     Embeddings → Causal Attention
                                     → MLP → Norm → LM head
                                                ↓
                                    Training / Validation / Checkpoint
                                                ↓
                                         Inference Engine
                                                ├── No-cache reference
                                                ├── Dense contiguous KV
                                                └── Paged KV cache
                                                     ├── BlockPool
                                                     ├── BlockTable
                                                     ├── Allocation / Release
                                                     ├── Offset-aware attention
                                                     └── Paged GPU kernel (later)
```

**Ranh giới:** Paged KV là quản lý bộ nhớ suy luận; không thay Transformer và không làm quy trình huấn luyện trở nên "paged" một cách tự động. Bản phase0 tham chiếu tập hợp K/V thành tensor liên tục khi decode, do đó chưa có kernel PagedAttention trực tiếp.

**Bất biến quan trọng:** causal isolation; dense-vs-paged numerical parity; no cross-request KV leakage; deterministic allocation/release; strict OOM handling. Test với zero-science fixtures trước các huấn luyện chính thức.
