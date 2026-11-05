"""Small, readable GPT-like decoder-only model with a reference paged KV-cache path.

This is a correctness reference, not an optimized PagedAttention GPU kernel.
"""
from dataclasses import dataclass
import math

import torch
from torch import nn
from torch.nn import functional as F

from paged_kv import PagedKVCache


@dataclass(frozen=True)
class GPTConfig:
    vocab_size: int = 256
    max_seq_len: int = 128
    n_embd: int = 64
    n_layer: int = 2
    n_head: int = 4

    def __post_init__(self):
        if self.n_embd <= 0 or self.n_head <= 0 or self.n_embd % self.n_head:
            raise ValueError("n_embd must be a positive multiple of n_head")
        if min(self.vocab_size, self.max_seq_len, self.n_layer) < 1:
            raise ValueError("vocab_size/max_seq_len/n_layer must be positive")


class CausalSelfAttention(nn.Module):
    def __init__(self, cfg: GPTConfig):
        super().__init__()
        self.heads = cfg.n_head
        self.head_dim = cfg.n_embd // cfg.n_head
        self.qkv = nn.Linear(cfg.n_embd, 3 * cfg.n_embd)
        self.proj = nn.Linear(cfg.n_embd, cfg.n_embd)

    def _split(self, t: torch.Tensor) -> torch.Tensor:
        batch, time, channels = t.shape
        return t.reshape(batch, time, self.heads, self.head_dim).transpose(1, 2)

    def forward(self, x: torch.Tensor) -> torch.Tensor:
        """Full causal attention for training and dense reference inference."""
        batch, time, channels = x.shape
        q, k, v = [self._split(a) for a in self.qkv(x).chunk(3, dim=-1)]
        scores = q @ k.transpose(-2, -1) / math.sqrt(self.head_dim)
        mask = torch.ones(time, time, dtype=torch.bool, device=x.device).tril()
        weights = scores.masked_fill(~mask, -torch.inf).softmax(dim=-1)
        y = weights @ v
        y = y.transpose(1, 2).contiguous().reshape(batch, time, channels)
        return self.proj(y)

    def step(self, x: torch.Tensor, layer: int, cache: PagedKVCache,
             request_id: str, position: int) -> torch.Tensor:
        """One decode step, read historical KV via block table (unoptimized)."""
        if x.shape[0:2] != (1, 1):
            raise ValueError("reference step supports one token of one request")
        q, k, v = [self._split(a)[0, :, 0, :] for a in self.qkv(x).chunk(3, -1)]
        cache.write(layer, request_id, position, k, v)
        hist_k, hist_v = cache.read(layer, request_id)  # [tokens, heads, dim]
        scores = torch.einsum("hd,thd->ht", q, hist_k) / math.sqrt(self.head_dim)
        weights = scores.softmax(dim=-1)
        y = torch.einsum("ht,thd->hd", weights, hist_v)
        return self.proj(y.reshape(1, 1, -1))


class Block(nn.Module):
    def __init__(self, cfg: GPTConfig):
        super().__init__()
        self.ln1 = nn.LayerNorm(cfg.n_embd)
        self.attn = CausalSelfAttention(cfg)
        self.ln2 = nn.LayerNorm(cfg.n_embd)
        self.mlp = nn.Sequential(
            nn.Linear(cfg.n_embd, 4 * cfg.n_embd),
            nn.GELU(),
            nn.Linear(4 * cfg.n_embd, cfg.n_embd),
        )

    def forward(self, x: torch.Tensor) -> torch.Tensor:
        x = x + self.attn(self.ln1(x))
        return x + self.mlp(self.ln2(x))

    def step(self, x: torch.Tensor, layer: int, cache: PagedKVCache,
             request_id: str, position: int) -> torch.Tensor:
        x = x + self.attn.step(self.ln1(x), layer, cache, request_id, position)
        return x + self.mlp(self.ln2(x))


class GPT(nn.Module):
    def __init__(self, cfg: GPTConfig):
        super().__init__()
        self.cfg = cfg
        self.tok = nn.Embedding(cfg.vocab_size, cfg.n_embd)
        self.pos = nn.Embedding(cfg.max_seq_len, cfg.n_embd)
        self.blocks = nn.ModuleList([Block(cfg) for _ in range(cfg.n_layer)])
        self.final_ln = nn.LayerNorm(cfg.n_embd)
        self.head = nn.Linear(cfg.n_embd, cfg.vocab_size, bias=False)
        self.head.weight = self.tok.weight
        self.apply(self._init_weights)

    @staticmethod
    def _init_weights(module: nn.Module) -> None:
        if isinstance(module, (nn.Linear, nn.Embedding)):
            nn.init.normal_(module.weight, mean=0.0, std=0.02)
            if isinstance(module, nn.Linear) and module.bias is not None:
                nn.init.zeros_(module.bias)

    def forward(self, tokens: torch.Tensor, targets=None):
        if tokens.ndim != 2 or tokens.shape[1] > self.cfg.max_seq_len:
            raise ValueError("tokens must be [batch, time] within max_seq_len")
        time = tokens.shape[1]
        positions = torch.arange(time, device=tokens.device)
        x = self.tok(tokens) + self.pos(positions)[None, :, :]
        for block in self.blocks:
            x = block(x)
        logits = self.head(self.final_ln(x))
        loss = None
        if targets is not None:
            loss = F.cross_entropy(logits.reshape(-1, logits.shape[-1]), targets.reshape(-1))
        return logits, loss

    @torch.no_grad()
    def paged_forward_tokens(self, token_ids: list[int], cache: PagedKVCache,
                             request_id: str) -> torch.Tensor:
        """Sequential prefill/decode. Run `model.eval()` first.

        Appends each token once and returns the logits at the final input token.
        Reuse the same cache + request ID for later generated tokens.
        """
        if self.training:
            raise RuntimeError("call model.eval() before paged inference")
        if not token_ids:
            raise ValueError("token_ids cannot be empty")
        device = self.tok.weight.device
        if device != cache.storage.device:
            raise ValueError("model and cache must be on the same device")
        for token_id in token_ids:
            if cache.lengths[request_id] >= self.cfg.max_seq_len:
                raise ValueError("context exceeds max_seq_len")
            position = cache.allocate_token(request_id)
            token = torch.tensor([[token_id]], dtype=torch.long, device=device)
            pos = torch.tensor([[position]], dtype=torch.long, device=device)
            x = self.tok(token) + self.pos(pos)
            for layer, block in enumerate(self.blocks):
                x = block.step(x, layer, cache, request_id, position)
            logits = self.head(self.final_ln(x))[0, -1, :]
        return logits
