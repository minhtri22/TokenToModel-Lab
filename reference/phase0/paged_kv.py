"""Reference block-paged KV cache.

A fixed physical pool is allocated once. Each request maintains a logical-to-
physical block table. No prefix reuse, copy-on-write, batching or GPU kernel.
"""

import torch


class PagedKVCache:
    def __init__(self, *, n_layers: int, n_blocks: int, block_size: int,
                 n_heads: int, head_dim: int, device="cpu", dtype=torch.float32):
        if min(n_layers, n_blocks, block_size, n_heads, head_dim) < 1:
            raise ValueError("all cache dimensions must be positive")
        self.block_size = block_size
        self.n_layers = n_layers
        self.n_heads = n_heads
        self.head_dim = head_dim
        self.storage = torch.zeros(
            n_layers, 2, n_blocks, block_size, n_heads, head_dim,
            dtype=dtype, device=device,
        )
        self.free = list(reversed(range(n_blocks)))
        self.tables: dict[str, list[int]] = {}
        self.lengths: dict[str, int] = {}

    def start(self, request_id: str) -> None:
        if request_id in self.tables:
            raise ValueError("request already exists")
        self.tables[request_id] = []
        self.lengths[request_id] = 0

    def allocate_token(self, request_id: str) -> int:
        if request_id not in self.tables:
            raise KeyError("request not started")
        pos = self.lengths[request_id]
        if pos % self.block_size == 0:
            if not self.free:
                raise MemoryError("physical KV blocks exhausted")
            self.tables[request_id].append(self.free.pop())
        self.lengths[request_id] += 1
        return pos

    def _slot(self, request_id: str, pos: int) -> tuple[int, int]:
        if request_id not in self.tables or not (0 <= pos < self.lengths[request_id]):
            raise IndexError("KV slot not allocated")
        return self.tables[request_id][pos // self.block_size], pos % self.block_size

    def write(self, layer: int, request_id: str, pos: int,
              k: torch.Tensor, v: torch.Tensor) -> None:
        if not 0 <= layer < self.n_layers:
            raise IndexError("invalid layer")
        expected = (self.n_heads, self.head_dim)
        if k.shape != expected or v.shape != expected:
            raise ValueError(f"K and V must have shape {expected}")
        block, offset = self._slot(request_id, pos)
        self.storage[layer, 0, block, offset].copy_(k)
        self.storage[layer, 1, block, offset].copy_(v)

    def read(self, layer: int, request_id: str):
        if not 0 <= layer < self.n_layers:
            raise IndexError("invalid layer")
        if request_id not in self.tables:
            raise KeyError("unknown request")
        n = self.lengths[request_id]
        if n == 0:
            shape = (0, self.n_heads, self.head_dim)
            return self.storage.new_empty(shape), self.storage.new_empty(shape)
        ids = self.tables[request_id]
        # This index/gather is intentionally simple and may copy data.
        k = self.storage[layer, 0, ids].reshape(-1, self.n_heads, self.head_dim)[:n]
        v = self.storage[layer, 1, ids].reshape(-1, self.n_heads, self.head_dim)[:n]
        return k, v

    def release(self, request_id: str) -> None:
        ids = self.tables.pop(request_id)
        self.lengths.pop(request_id)
        for block in ids:
            self.storage[:, :, block].zero_()  # clear on reuse
        self.free.extend(ids)

    def stats(self) -> dict:
        return {"total_blocks": self.storage.shape[2],
                "free_blocks": len(self.free),
                "used_blocks": self.storage.shape[2] - len(self.free),
                "active_requests": len(self.tables)}
