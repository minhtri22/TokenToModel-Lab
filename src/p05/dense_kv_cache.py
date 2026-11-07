"""P05 reference contiguous KV cache for decoder-only P02 on CPU.

Incremental decode only. Does not read P01 corpus or open P03/P04 datasets.
Does not implement paged allocation, prefix sharing, GPU kernels or batching.
"""
from __future__ import annotations

import math
import time

import torch
from torch import nn


class DenseKVCache:
    """Per-request contiguous tensors [layers, K/V, time, heads, head_dim]."""

    def __init__(self, *, n_layers: int, max_seq_len: int, n_heads: int,
                 head_dim: int, max_requests: int = 2, max_allocated_bytes: int = 128 << 20):
        dimensions = (n_layers, max_seq_len, n_heads, head_dim, max_requests,
                      max_allocated_bytes)
        if any(type(v) is not int or v <= 0 for v in dimensions):
            raise ValueError("all cache dimensions/budgets must be positive integers")
        self.n_layers, self.max_seq_len = n_layers, max_seq_len
        self.n_heads, self.head_dim = n_heads, head_dim
        self.max_requests = max_requests
        self._bytes_per_request = n_layers * 2 * max_seq_len * n_heads * head_dim * 4
        if self._bytes_per_request * max_requests > max_allocated_bytes:
            raise ValueError("dense KV cache exceeds declared memory budget")
        self._storage: dict[str, torch.Tensor] = {}
        self.lengths: dict[str, int] = {}

    def start(self, request_id: str) -> None:
        if not isinstance(request_id, str) or not request_id:
            raise ValueError("nonempty request ID required")
        if request_id in self.lengths:
            raise ValueError("duplicate request")
        if len(self.lengths) >= self.max_requests:
            raise MemoryError("max dense requests exceeded")
        self._storage[request_id] = torch.zeros(
            (self.n_layers, 2, self.max_seq_len, self.n_heads, self.head_dim),
            dtype=torch.float32, device="cpu")
        self.lengths[request_id] = 0

    def allocate_token(self, request_id: str) -> int:
        if request_id not in self.lengths:
            raise KeyError("request not started")
        pos = self.lengths[request_id]
        if pos >= self.max_seq_len:
            raise MemoryError("dense context capacity exhausted")
        self.lengths[request_id] = pos + 1
        return pos

    def write(self, layer: int, request_id: str, position: int,
              k: torch.Tensor, v: torch.Tensor) -> None:
        if type(layer) is not int or not 0 <= layer < self.n_layers:
            raise IndexError("invalid layer")
        if request_id not in self.lengths or type(position) is not int or not 0 <= position < self.lengths[request_id]:
            raise IndexError("unallocated token position")
        expected = (self.n_heads, self.head_dim)
        if any(not isinstance(z, torch.Tensor) or z.shape != expected or
               z.device.type != "cpu" or z.dtype != torch.float32 for z in (k, v)):
            raise ValueError("KV must be CPU float32 [heads, head_dim]")
        self._storage[request_id][layer, 0, position].copy_(k)
        self._storage[request_id][layer, 1, position].copy_(v)

    def read(self, layer: int, request_id: str) -> tuple[torch.Tensor, torch.Tensor]:
        if type(layer) is not int or not 0 <= layer < self.n_layers:
            raise IndexError("invalid layer")
        if request_id not in self.lengths:
            raise KeyError("unknown request")
        storage = self._storage[request_id]
        n = self.lengths[request_id]
        return storage[layer, 0, :n], storage[layer, 1, :n]

    def release(self, request_id: str) -> None:
        if request_id not in self.lengths:
            raise KeyError("unknown request")
        self._storage.pop(request_id).zero_()
        del self.lengths[request_id]

    def stats(self) -> dict:
        n = len(self.lengths)
        logical = sum(self.lengths.values()) * self.n_layers * 2 * self.n_heads * self.head_dim * 4
        return {"active_requests": n, "allocated_bytes": n * self._bytes_per_request,
                "used_logical_bytes": logical, "bytes_per_request": self._bytes_per_request,
                "max_requests": self.max_requests, "max_seq_len": self.max_seq_len}


@torch.no_grad()
def dense_forward_tokens(model: nn.Module, token_ids: list[int],
                         cache: DenseKVCache, request_id: str) -> torch.Tensor:
    """Extend one initialized request; output last-token logits [vocab]."""
    if model.training:
        raise ValueError("model.eval() required for P05 reference inference")
    cfg = model.cfg
    if cfg.vocab_size != 2048 or cfg.n_layer != cache.n_layers or cfg.n_head != cache.n_heads or cfg.n_embd // cfg.n_head != cache.head_dim:
        raise ValueError("P02/P05 architecture mismatch")
    if not isinstance(token_ids, list) or not token_ids or any(type(v) is not int or not 0 <= v < 2048 for v in token_ids):
        raise ValueError("nonempty valid BPE token list required")
    if request_id not in cache.lengths:
        raise KeyError("request not started")
    if cache.max_seq_len > cfg.max_seq_len or cache.lengths[request_id] + len(token_ids) > cache.max_seq_len:
        raise ValueError("requested tokens exceed dense context")
    if any(p.device.type != "cpu" or p.dtype != torch.float32 for p in model.parameters()):
        raise ValueError("P05 reference supports CPU float32 only")
    last_logits = None
    for token_id in token_ids:
        position = cache.allocate_token(request_id)
        token = torch.tensor([[token_id]], dtype=torch.long)
        pos = torch.tensor([[position]], dtype=torch.long)
        x = model.tok(token) + model.pos(pos)
        for layer, block in enumerate(model.blocks):
            attn = block.attn
            q, k, v = [attn._split(z)[0, :, 0, :] for z in attn.qkv(block.ln1(x)).chunk(3, dim=-1)]
            cache.write(layer, request_id, position, k, v)
            history_k, history_v = cache.read(layer, request_id)
            scores = torch.einsum("hd,thd->ht", q, history_k) / math.sqrt(cache.head_dim)
            weights = scores.softmax(dim=-1)
            y = torch.einsum("ht,thd->hd", weights, history_v)
            x = x + attn.proj(y.reshape(1, 1, -1))
            x = x + block.mlp(block.ln2(x))
        last_logits = model.head(model.final_ln(x))[0, -1, :]
    assert last_logits is not None
    return last_logits


@torch.no_grad()
def benchmark_dense_vs_recompute(model: nn.Module, tokens: list[int], *, repeats: int = 3) -> dict:
    """Measured on same incremental decoding workload; no speedup claim."""
    if type(repeats) is not int or not 1 <= repeats <= 20:
        raise ValueError("repeats outside [1,20]")
    if model.training:
        raise ValueError("model.eval() required")
    if not isinstance(tokens, list) or not tokens or any(type(t) is not int or not 0 <= t < 2048 for t in tokens) or len(tokens) > model.cfg.max_seq_len:
        raise ValueError("invalid benchmark sequence")
    dense_ms = []
    recompute_ms = []
    bytes_alloc = 0
    logical_used = 0
    for _ in range(repeats):
        t0 = time.perf_counter()
        for t in range(1, len(tokens) + 1):
            model(torch.tensor([tokens[:t]], dtype=torch.long))
        recompute_ms.append((time.perf_counter() - t0) * 1e3)
        cache = DenseKVCache(n_layers=model.cfg.n_layer, max_seq_len=model.cfg.max_seq_len,
                             n_heads=model.cfg.n_head, head_dim=model.cfg.n_embd // model.cfg.n_head,
                             max_requests=1)
        cache.start("benchmark")
        t0 = time.perf_counter()
        for tok in tokens:
            dense_forward_tokens(model, [tok], cache, "benchmark")
        dense_ms.append((time.perf_counter() - t0) * 1e3)
        stats = cache.stats()
        bytes_alloc, logical_used = stats["allocated_bytes"], stats["used_logical_bytes"]
        cache.release("benchmark")
    return {"status": "P05_CPU_MEASURED_NO_PERFORMANCE_CLAIM", "recompute_ms": recompute_ms,
            "dense_ms": dense_ms, "allocated_kv_bytes": bytes_alloc,
            "logical_kv_bytes": logical_used, "sequence_length": len(tokens),
            "repeats": repeats, "precision": "float32", "device": "cpu"}
