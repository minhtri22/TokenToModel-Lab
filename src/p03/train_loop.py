"""TTM P03: minimal GPT training loop on explicit token tensors only.

No corpus reader, network, checkpoint save/load or held-out TEST path.
The caller must supply permitted training IDs. P03 synthetic QA is not
an authorization to train on P01 F1 WP30 text (BPE E0 only scope).
"""
from dataclasses import dataclass
import math

import torch
from torch import nn


@dataclass(frozen=True)
class TrainConfig:
    steps: int = 80
    peak_lr: float = 0.003
    warmup_steps: int = 5
    min_lr_ratio: float = 0.1
    accumulation_steps: int = 2
    max_grad_norm: float = 1.0
    weight_decay: float = 0.0

    def __post_init__(self) -> None:
        if not isinstance(self.steps, int) or isinstance(self.steps, bool) or self.steps < 1:
            raise ValueError("steps must be positive integer")
        if not isinstance(self.warmup_steps, int) or not 0 <= self.warmup_steps <= self.steps:
            raise ValueError("warmup_steps outside [0, steps]")
        if not isinstance(self.accumulation_steps, int) or self.accumulation_steps < 1:
            raise ValueError("accumulation_steps must be positive integer")
        if not (math.isfinite(self.peak_lr) and self.peak_lr > 0):
            raise ValueError("peak_lr must be finite and positive")
        if not (math.isfinite(self.min_lr_ratio) and 0 < self.min_lr_ratio <= 1):
            raise ValueError("min_lr_ratio outside (0, 1]")
        if not (math.isfinite(self.max_grad_norm) and self.max_grad_norm > 0):
            raise ValueError("max_grad_norm must be finite and positive")
        if not (math.isfinite(self.weight_decay) and self.weight_decay >= 0):
            raise ValueError("weight_decay must be finite and nonnegative")


def scheduled_lr(step: int, cfg: TrainConfig) -> float:
    """Warmup then cosine decay, never below cfg.min_lr_ratio * peak_lr."""
    if step < 0 or step >= cfg.steps:
        raise ValueError("step out of range")
    if step < cfg.warmup_steps:
        return cfg.peak_lr * (step + 1) / cfg.warmup_steps
    decay_steps = cfg.steps - cfg.warmup_steps
    if decay_steps <= 1:
        return cfg.peak_lr
    progress = (step - cfg.warmup_steps) / (decay_steps - 1)
    return cfg.peak_lr * (cfg.min_lr_ratio + (1 - cfg.min_lr_ratio) *
                          (1 + math.cos(math.pi * progress)) / 2)


def _validate(model: nn.Module, x: torch.Tensor, y: torch.Tensor, cfg: TrainConfig) -> None:
    if not hasattr(model, "cfg") or model.cfg.vocab_size != 2048:
        raise ValueError("P03 synthetic candidate requires frozen 2048-token P02 core")
    if not isinstance(x, torch.Tensor) or not isinstance(y, torch.Tensor):
        raise ValueError("inputs and targets must be torch tensors")
    if x.dtype != torch.long or y.dtype != torch.long or x.ndim != 2 or x.shape != y.shape:
        raise ValueError("inputs/targets must be same-shape LongTensor [batch,time]")
    if not (x.shape[0] > 0 and 1 <= x.shape[1] <= model.cfg.max_seq_len):
        raise ValueError("invalid batch or sequence length")
    if cfg.accumulation_steps > x.shape[0]:
        raise ValueError("accumulation_steps exceeds batch size")
    if x.device != y.device or x.device != next(model.parameters()).device:
        raise ValueError("model, inputs and targets must be on same device")
    if torch.any(x < 0).item() or torch.any(x >= 2048).item():
        raise ValueError("input token outside 2048 vocabulary")
    if torch.any(y < 0).item() or torch.any(y >= 2048).item():
        raise ValueError("target token outside 2048 vocabulary")


def train_fixed_batch(model: nn.Module, x: torch.Tensor, y: torch.Tensor,
                      cfg: TrainConfig) -> dict:
    """Train on the *same* explicit batch for an overfit diagnostic.

    Gradient accumulation weights variable-size microbatches by sample count,
    matching a single cross entropy mean over a full fixed-size batch.
    The returned loss values are diagnostic, not held-out evaluation.
    """
    _validate(model, x, y, cfg)
    model.train()
    with torch.no_grad():
        _, initial = model(x, y)
        if not bool(torch.isfinite(initial).item()):
            raise FloatingPointError("nonfinite initial loss")
        initial_loss = float(initial.item())
    optimizer = torch.optim.AdamW(model.parameters(), lr=cfg.peak_lr,
                                  weight_decay=cfg.weight_decay)
    trajectory = []
    max_raw_grad_norm = 0.0
    chunks = torch.tensor_split(torch.arange(x.shape[0], device=x.device),
                                cfg.accumulation_steps)
    for step in range(cfg.steps):
        lr = scheduled_lr(step, cfg)
        optimizer.param_groups[0]["lr"] = lr
        optimizer.zero_grad(set_to_none=True)
        weighted_loss = 0.0
        for indices in chunks:
            _, loss = model(x[indices], y[indices])
            if not bool(torch.isfinite(loss).item()):
                raise FloatingPointError("nonfinite training loss")
            fraction = indices.numel() / x.shape[0]
            (loss * fraction).backward()
            weighted_loss += float(loss.item()) * fraction
        for name, p in model.named_parameters():
            if p.grad is not None and not bool(torch.isfinite(p.grad).all().item()):
                raise FloatingPointError("nonfinite gradient in " + name)
        norm = torch.nn.utils.clip_grad_norm_(model.parameters(), cfg.max_grad_norm,
                                               error_if_nonfinite=True)
        max_raw_grad_norm = max(max_raw_grad_norm, float(norm.item()))
        optimizer.step()
        trajectory.append(weighted_loss)
    with torch.no_grad():
        _, final = model(x, y)
        if not bool(torch.isfinite(final).item()):
            raise FloatingPointError("nonfinite final loss")
    return {"status": "TRAINING_LOOP_COMPLETED", "steps": cfg.steps,
            "initial_loss": initial_loss, "final_loss": float(final.item()),
            "first_training_loss": trajectory[0], "last_training_loss": trajectory[-1],
            "max_raw_grad_norm": max_raw_grad_norm,
            "first_lr": scheduled_lr(0, cfg),
            "last_lr": scheduled_lr(cfg.steps - 1, cfg),
            "unique_input_ids": int(x.unique().numel()),
            "checkpoint": "NOT_SAVED_P04_NOT_OPENED",
            "dataset": "EXPLICIT_INPUT_TENSORS_ONLY"}
