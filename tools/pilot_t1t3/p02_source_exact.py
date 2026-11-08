"""TTM P02 decoder-only Transformer core. CPU-correctness candidate, not P03 training.

BPE is frozen at 2048 token IDs; this module does not read corpus or held-out TEST.
The LayerNorm variant intentionally has the same parameter names and math as P00.
"""
from dataclasses import dataclass
import math

import torch
from torch import nn
from torch.nn import functional as F


@dataclass(frozen=True)
class P02Config:
    vocab_size: int = 2048
    max_seq_len: int = 64
    n_embd: int = 64
    n_layer: int = 2
    n_head: int = 4
    norm_type: str = "layernorm"

    def __post_init__(self):
        if not all(isinstance(v, int) and not isinstance(v, bool) and v > 0
                   for v in (self.vocab_size, self.max_seq_len, self.n_embd,
                             self.n_layer, self.n_head)):
            raise ValueError("all model dimensions must be positive integers")
        if self.n_embd % self.n_head:
            raise ValueError("n_embd must be divisible by n_head")
        if self.norm_type not in ("layernorm", "rmsnorm"):
            raise ValueError("norm_type must be layernorm or rmsnorm")


class RMSNorm(nn.Module):
    def __init__(self, dim: int, eps: float = 1e-5):
        super().__init__()
        self.eps = eps
        self.weight = nn.Parameter(torch.ones(dim))

    def forward(self, x: torch.Tensor) -> torch.Tensor:
        scale = torch.rsqrt(x.square().mean(dim=-1, keepdim=True) + self.eps)
        return x * scale * self.weight


def _norm(cfg: P02Config) -> nn.Module:
    if cfg.norm_type == "layernorm":
        return nn.LayerNorm(cfg.n_embd)
    return RMSNorm(cfg.n_embd)


class CausalSelfAttention(nn.Module):
    def __init__(self, cfg: P02Config):
        super().__init__()
        self.heads = cfg.n_head
        self.head_dim = cfg.n_embd // cfg.n_head
        self.qkv = nn.Linear(cfg.n_embd, 3 * cfg.n_embd)
        self.proj = nn.Linear(cfg.n_embd, cfg.n_embd)

    def _split(self, t: torch.Tensor) -> torch.Tensor:
        batch, time, channels = t.shape
        return t.reshape(batch, time, self.heads, self.head_dim).transpose(1, 2)

    def forward(self, x: torch.Tensor) -> torch.Tensor:
        batch, time, channels = x.shape
        q, k, v = [self._split(a) for a in self.qkv(x).chunk(3, dim=-1)]
        scores = q @ k.transpose(-2, -1) / math.sqrt(self.head_dim)
        mask = torch.ones(time, time, dtype=torch.bool, device=x.device).tril()
        weights = scores.masked_fill(~mask, -torch.inf).softmax(dim=-1)
        y = weights @ v
        y = y.transpose(1, 2).contiguous().reshape(batch, time, channels)
        return self.proj(y)


class Block(nn.Module):
    def __init__(self, cfg: P02Config):
        super().__init__()
        self.ln1 = _norm(cfg)
        self.attn = CausalSelfAttention(cfg)
        self.ln2 = _norm(cfg)
        self.mlp = nn.Sequential(
            nn.Linear(cfg.n_embd, 4 * cfg.n_embd),
            nn.GELU(),
            nn.Linear(4 * cfg.n_embd, cfg.n_embd),
        )

    def forward(self, x: torch.Tensor) -> torch.Tensor:
        x = x + self.attn(self.ln1(x))
        return x + self.mlp(self.ln2(x))


class GPT(nn.Module):
    """P02 core with P00-compatible LayerNorm parameter names/state_dict."""
    def __init__(self, cfg: P02Config):
        super().__init__()
        self.cfg = cfg
        self.tok = nn.Embedding(cfg.vocab_size, cfg.n_embd)
        self.pos = nn.Embedding(cfg.max_seq_len, cfg.n_embd)
        self.blocks = nn.ModuleList([Block(cfg) for _ in range(cfg.n_layer)])
        self.final_ln = _norm(cfg)
        self.head = nn.Linear(cfg.n_embd, cfg.vocab_size, bias=False)
        self.head.weight = self.tok.weight
        self.apply(self._init_weights)

    @staticmethod
    def _init_weights(module: nn.Module) -> None:
        if isinstance(module, (nn.Linear, nn.Embedding)):
            nn.init.normal_(module.weight, mean=0.0, std=0.02)
            if isinstance(module, nn.Linear) and module.bias is not None:
                nn.init.zeros_(module.bias)

    def forward(self, tokens: torch.Tensor, targets: torch.Tensor | None = None):
        if tokens.dtype != torch.long or tokens.ndim != 2:
            raise ValueError("tokens must be LongTensor [batch, time]")
        if tokens.shape[0] < 1 or not (1 <= tokens.shape[1] <= self.cfg.max_seq_len):
            raise ValueError("tokens must have nonempty batch/time within max_seq_len")
        if torch.any(tokens < 0).item() or torch.any(tokens >= self.cfg.vocab_size).item():
            raise ValueError("token ID outside P02 vocabulary")
        if targets is not None and (targets.dtype != torch.long or targets.shape != tokens.shape):
            raise ValueError("targets must match tokens shape and dtype")
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
