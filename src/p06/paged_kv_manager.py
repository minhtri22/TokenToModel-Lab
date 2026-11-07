"""TTM P06 CPU float32 paged-KV manager for synthetic token IDs only.

Fixed physical block pool, per-request block tables, no prefix sharing,
no GPU kernel and no reads of P01 F1/TEST. P05 remains the dense oracle.
"""
from __future__ import annotations

import math
import time

import torch
from torch import nn


class PagedKVCache:
    """Own a fixed contiguous physical pool; map each live request to blocks.

    A reserved *token slot* is shared across model layers. Each slot stores
    both K and V [n_layers, 2, n_heads, head_dim] in CPU float32. New slots
    read as zeros until written; a released block is zeroed before reuse.
    """

    def __init__(self, *, n_layers: int, n_blocks: int, block_size: int,
                 n_heads: int, head_dim: int, max_seq_len: int = 64,
                 max_requests: int = 4, max_allocated_bytes: int = 128 << 20):
        dims = (n_layers, n_blocks, block_size, n_heads, head_dim,
                max_seq_len, max_requests, max_allocated_bytes)
        if any(type(n) is not int or n < 1 for n in dims):
            raise ValueError("P06 cache dimensions and budgets must be positive integers")
        self.n_layers, self.n_blocks, self.block_size = n_layers, n_blocks, block_size
        self.n_heads, self.head_dim = n_heads, head_dim
        self.max_seq_len, self.max_requests = max_seq_len, max_requests
        self.allocated_bytes = n_layers * 2 * n_blocks * block_size * n_heads * head_dim * 4
        if self.allocated_bytes > max_allocated_bytes:
            raise ValueError("P06 physical KV pool exceeds declared byte budget")
        self.storage = torch.zeros(
            (n_layers, 2, n_blocks, block_size, n_heads, head_dim),
            dtype=torch.float32, device="cpu")
        self._free = list(reversed(range(n_blocks)))
        self._tables: dict[str, list[int]] = {}
        self.lengths: dict[str, int] = {}

    def start(self, request_id: str) -> None:
        if not isinstance(request_id, str) or not request_id:
            raise ValueError("request_id must be nonempty string")
        if request_id in self._tables:
            raise ValueError("duplicate request_id")
        if len(self._tables) >= self.max_requests:
            raise MemoryError("max P06 active requests exceeded")
        self._tables[request_id] = []
        self.lengths[request_id] = 0

    def page_table(self, request_id: str) -> tuple[int, ...]:
        if request_id not in self._tables:
            raise KeyError("unknown request_id")
        return tuple(self._tables[request_id])

    def _validate_layer(self, layer: int) -> None:
        if type(layer) is not int or not (0 <= layer < self.n_layers):
            raise IndexError("invalid model layer")

    def allocate_token(self, request_id: str) -> int:
        if request_id not in self._tables:
            raise KeyError("request not started")
        pos = self.lengths[request_id]
        if pos >= self.max_seq_len:
            raise MemoryError("request exceeds max_seq_len")
        if pos % self.block_size == 0:
            if not self._free:
                raise MemoryError("physical KV blocks exhausted")
            self._tables[request_id].append(self._free.pop())
        self.lengths[request_id] = pos + 1
        return pos

    def _slot(self, request_id: str, position: int) -> tuple[int, int]:
        if request_id not in self._tables:
            raise KeyError("unknown request_id")
        if type(position) is not int or not 0 <= position < self.lengths[request_id]:
            raise IndexError("token position was not allocated")
        return (self._tables[request_id][position // self.block_size],
                position % self.block_size)

    def write(self, layer: int, request_id: str, position: int,
              k: torch.Tensor, v: torch.Tensor) -> None:
        self._validate_layer(layer)
        block, offset = self._slot(request_id, position)
        expected = (self.n_heads, self.head_dim)
        if any(not isinstance(t, torch.Tensor) or tuple(t.shape) != expected
               or t.dtype != torch.float32 or t.device.type != "cpu" for t in (k, v)):
            raise ValueError("K and V must be CPU float32 [n_heads, head_dim]")
        self.storage[layer, 0, block, offset].copy_(k)
        self.storage[layer, 1, block, offset].copy_(v)

    def read(self, layer: int, request_id: str) -> tuple[torch.Tensor, torch.Tensor]:
        self._validate_layer(layer)
        if request_id not in self._tables:
            raise KeyError("unknown request_id")
        length = self.lengths[request_id]
        if length == 0:
            shape = (0, self.n_heads, self.head_dim)
            return self.storage.new_empty(shape), self.storage.new_empty(shape)
        # Advanced indexing gathers physical pages in logical order; no data
        # from other requests are included, even when physical pages interleave.
        pages = self._tables[request_id]
        k = self.storage[layer, 0, pages].reshape(-1, self.n_heads, self.head_dim)[:length]
        v = self.storage[layer, 1, pages].reshape(-1, self.n_heads, self.head_dim)[:length]
        return k, v

    def release(self, request_id: str) -> None:
        if request_id not in self._tables:
            raise KeyError("unknown request_id")
        pages = self._tables.pop(request_id)
        del self.lengths[request_id]
        for page in pages:
            self.storage[:, :, page].zero_()
        self._free.extend(pages)

    def stats(self) -> dict:
        used_blocks = sum(len(pages) for pages in self._tables.values())
        if used_blocks + len(self._free) != self.n_blocks:
            raise AssertionError("P06 physical page accounting invariant failed")
        live_tokens = sum(self.lengths.values())
        reserved_slots = used_blocks * self.block_size
        bytes_per_token = self.n_layers * 2 * self.n_heads * self.head_dim * 4
        return {"active_requests": len(self._tables),
                "total_blocks": self.n_blocks, "free_blocks": len(self._free),
                "used_blocks": used_blocks,
                "block_size": self.block_size,
                "live_tokens": live_tokens,
                "reserved_slots": reserved_slots,
                "fragmented_slots": reserved_slots - live_tokens,
                "bytes_per_token": bytes_per_token,
                "allocated_bytes": self.allocated_bytes,
                "reserved_bytes": reserved_slots * bytes_per_token,
                "used_logical_bytes": live_tokens * bytes_per_token,
                "fragmented_bytes": (reserved_slots - live_tokens) * bytes_per_token}


@torch.no_grad()
def paged_forward_tokens(model: nn.Module, token_ids: list[int],
                         cache: PagedKVCache, request_id: str) -> torch.Tensor:
    """Extend one request and return [vocab] logits for last appended token.

    All request/capacity checks occur before any append. CPU-only reference:
    dense and paged use identical weights but independent physical storage.
    """
    if model.training:
        raise ValueError("model.eval() required for incremental inference")
    cfg = model.cfg
    if (cfg.vocab_size != 2048 or cfg.n_layer != cache.n_layers
            or cfg.n_head != cache.n_heads
            or cfg.n_embd // cfg.n_head != cache.head_dim
            or cache.max_seq_len > cfg.max_seq_len):
        raise ValueError("P02/P06 architecture or context mismatch")
    if (not isinstance(token_ids, list) or not token_ids
            or any(type(i) is not int or not 0 <= i < 2048 for i in token_ids)):
        raise ValueError("nonempty valid 2048-token list required")
    if request_id not in cache.lengths:
        raise KeyError("unknown request_id")
    if any(p.device.type != "cpu" or p.dtype != torch.float32 for p in model.parameters()):
        raise ValueError("P06 supports CPU float32 model only")
    before = cache.lengths[request_id]
    after = before + len(token_ids)
    if after > cache.max_seq_len:
        raise ValueError("requested tokens exceed context")
    old_pages = len(cache.page_table(request_id))
    needed_pages = (after + cache.block_size - 1) // cache.block_size - old_pages
    if needed_pages > cache.stats()["free_blocks"]:
        raise MemoryError("physical pages insufficient for complete append")
    logits = None
    for token_id in token_ids:
        position = cache.allocate_token(request_id)
        x = (model.tok(torch.tensor([[token_id]], dtype=torch.long))
             + model.pos(torch.tensor([[position]], dtype=torch.long)))
        for layer, block in enumerate(model.blocks):
            attn = block.attn
            q, k, v = [attn._split(z)[0, :, 0, :]
                       for z in attn.qkv(block.ln1(x)).chunk(3, dim=-1)]
            cache.write(layer, request_id, position, k, v)
            hist_k, hist_v = cache.read(layer, request_id)
            scores = torch.einsum("hd,thd->ht", q, hist_k) / math.sqrt(cache.head_dim)
            weights = scores.softmax(dim=-1)
            y = torch.einsum("ht,thd->hd", weights, hist_v)
            x = x + attn.proj(y.reshape(1, 1, -1))
            x = x + block.mlp(block.ln2(x))
        logits = model.head(model.final_ln(x))[0, -1, :]
    assert logits is not None
    return logits


@torch.no_grad()
def benchmark_paged_vs_dense(model: nn.Module, token_ids: list[int],
                             *, block_size: int = 4, repeats: int = 2) -> dict:
    """Same sequence, repeated CPU-only decode; measurements are not speed claims."""
    from src.p05.dense_kv_cache import DenseKVCache, dense_forward_tokens

    if type(block_size) is not int or block_size < 1:
        raise ValueError("block_size must be positive integer")
    if type(repeats) is not int or not 1 <= repeats <= 10:
        raise ValueError("repeats outside [1,10]")
    if model.training or any(p.device.type != "cpu" for p in model.parameters()):
        raise ValueError("model must be CPU eval()")
    if (not isinstance(token_ids, list) or not token_ids
            or len(token_ids) > model.cfg.max_seq_len
            or any(type(i) is not int or not 0 <= i < 2048 for i in token_ids)):
        raise ValueError("benchmark requires valid short 2048-token IDs")
    cfg = model.cfg
    pages = (cfg.max_seq_len + block_size - 1) // block_size
    dense_ms, paged_ms, recompute_ms = [], [], []
    dense_bytes = paged_bytes = logical_bytes = fragmentation = 0
    for _ in range(repeats):
        t0 = time.perf_counter()
        for t in range(1, len(token_ids) + 1):
            model(torch.tensor([token_ids[:t]], dtype=torch.long))
        recompute_ms.append((time.perf_counter() - t0) * 1000)
        dense = DenseKVCache(n_layers=cfg.n_layer, max_seq_len=cfg.max_seq_len,
                             n_heads=cfg.n_head, head_dim=cfg.n_embd // cfg.n_head,
                             max_requests=1)
        dense.start("bench")
        t0 = time.perf_counter()
        for token_id in token_ids:
            dense_forward_tokens(model, [token_id], dense, "bench")
        dense_ms.append((time.perf_counter() - t0) * 1000)
        dense_bytes = dense.stats()["allocated_bytes"]
        dense.release("bench")
        paged = PagedKVCache(n_layers=cfg.n_layer, n_blocks=pages,
                             block_size=block_size, n_heads=cfg.n_head,
                             head_dim=cfg.n_embd // cfg.n_head,
                             max_seq_len=cfg.max_seq_len, max_requests=1)
        paged.start("bench")
        t0 = time.perf_counter()
        for token_id in token_ids:
            paged_forward_tokens(model, [token_id], paged, "bench")
        paged_ms.append((time.perf_counter() - t0) * 1000)
        stats = paged.stats()
        paged_bytes = stats["allocated_bytes"]
        logical_bytes = stats["used_logical_bytes"]
        fragmentation = stats["fragmented_bytes"]
        paged.release("bench")
    return {"status": "P06_CPU_MEASURED_NO_SPEEDUP_CLAIM", "device": "cpu",
            "precision": "float32", "sequence_length": len(token_ids),
            "block_size": block_size, "repeats": repeats,
            "dense_ms": dense_ms, "paged_ms": paged_ms,
            "recompute_ms": recompute_ms,
            "dense_allocated_bytes": dense_bytes,
            "paged_allocated_bytes": paged_bytes,
            "used_logical_bytes": logical_bytes,
            "fragmented_bytes": fragmentation}
