# GPT-like + Paged KV Cache — correctness reference

A small decoder-only GPT written in PyTorch (no third-party model package) with causal multi-head attention, next-token training, and **physically paged KV caching for incremental decoding**.

**This is a correctness-focused reference, NOT an optimized vLLM-equivalent PagedAttention kernel.** The decode path gathers K/V into temporary contiguous PyTorch tensors, so it can incur copying and may be slower than a dense cache. It has no concurrent batched GPU decode, prefix sharing, COW, eviction policy, GQA, RoPE or FlashAttention kernels. Do not infer a speedup from correctness tests.

## Requirements

- Python 3.10+ with compatible PyTorch installed.
- CPU works for validation; for Intel Arc XPU install the official compatible PyTorch XPU wheel and check `torch.xpu.is_available()`.
- Windows PowerShell:

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install torch
python -m unittest -v test_reference
python demo.py
```

On systems requiring a specific PyTorch XPU build, consult https://docs.pytorch.org/get-started/additional-platforms/ instead of installing the default wheel.

## Train

A byte-level vocabulary (0..255) is used solely to eliminate tokenizer dependencies. For meaningful language performance, substitute a trained BPE/SentencePiece tokenizer and a real training dataset. A random untrained model generates nonsense.

```powershell
python train.py .\corpus.txt --steps 100 --seq-len 32 --batch-size 8 --device cpu
```

Training and paged decoding are **separate paths with shared weights**. This code exercises the baseline path and allocation semantics, not large-scale training performance.

## Read the code in this order

1. `model.py` / `CausalSelfAttention.forward`: full causal attention.
2. `model.py` / `GPT.forward`: GPT decoder blocks + next-token cross-entropy.
3. `paged_kv.py`: fixed block pool, per-request logical-to-physical mapping, read/write/release.
4. `model.py` / `CausalSelfAttention.step`: token-by-token KV read and attention.
5. `test_reference.py`: all-position dense-vs-paged parity, causal mask, concurrent request isolation, capacity/release.
6. `demo.py`: end-to-end correctness check.

## Next implementation milestones (not included)

- Add dense contiguous KV cache baseline and compare logits, allocations and latency.
- Enable chunked prefill with **offset-aware causal masks**. In PyTorch, `is_causal=True` when `q_len=1` and `kv_len>1` may apply an incorrect upper-left mask; use `is_causal=False` for a single newest-token query or a properly offset causal mask for chunks.
- Implement fused or direct paged gather attention kernel that reads physical blocks from `block_table` without materializing all K/V.
- Implement efficient multi-request batching, block sharing, copy-on-write, prefix hashing and eviction.
- Benchmark TTFT, TPOT, tokens/s, active memory, fragmentation, OOM, and p50/p95 latency across identical weights/workloads.

## Sources

- Vaswani et al. (2017), Attention Is All You Need: https://arxiv.org/abs/1706.03762
- GPT-2 source: https://github.com/openai/gpt-2/blob/master/src/model.py
- minGPT: https://github.com/karpathy/minGPT/blob/master/mingpt/model.py
- nanoGPT: https://github.com/karpathy/nanoGPT/blob/master/model.py
- vLLM: https://github.com/vllm-project/vllm
- vLLM KV manager: https://github.com/vllm-project/vllm/blob/main/vllm/v1/core/kv_cache_manager.py
- vLLM block pool: https://github.com/vllm-project/vllm/blob/main/vllm/v1/core/block_pool.py
- vLLM cache design: https://docs.vllm.ai/en/stable/design/prefix_caching/
