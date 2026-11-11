#!/usr/bin/env python3
"""TTM external-fact Memory Reader — source-only architecture, not science.

This module NEVER loads a checkpoint, TRAIN pack, TEST, or API. Oracle matching
uses ONLY question text and supplied memory keys. No target_key/gold/answer is
an argument to retrieval. The learned weights belong to a future CPU pilot.

Frozen P02 input: hidden state h[B,256] and tied head weight[2048,256].
Memory keys/values must be separately encoded with the pinned T1 tokenizer and
frozen P02 embedding table in the future pilot (not done here).

With no memory, logits are exactly F.linear(h, frozen_tied_head); neither the
reader nor the frozen core are modified. A zero-initialized output projection
makes an untrained reader an exact bypass even with a nonempty memory bank.
"""
from __future__ import annotations
import re
from dataclasses import dataclass
from typing import Callable, Mapping, Sequence

import torch
from torch import Tensor, nn
from torch.nn import functional as F

D_MODEL = 256
ENTITY_PATTERN = re.compile(r'(?<![A-Za-z0-9])obj[bcdfghjklmnpqrstvwxz]{12}(?![A-Za-z0-9])')


def entity_from_question(question: str) -> str:
    if not isinstance(question, str):
        raise TypeError('QUESTION_MUST_BE_STRING')
    matches = ENTITY_PATTERN.findall(question)
    if len(matches) != 1:
        raise ValueError('QUESTION_TARGET_ENTITY_AMBIGUOUS_OR_MISSING')
    return matches[0]


def oracle_key_mask(question: str, memory_cards: Sequence[Mapping[str, str]]) -> list[bool]:
    """Read only the observed question and memory key fields; never the gold label.

    Fail closed if no record, duplicate target, duplicate keys, or bad card.
    Distractors stay in the bank but are masked in the oracle positive control.
    """
    target = entity_from_question(question)
    if len(memory_cards) != 3:
        raise ValueError('ORACLE_EXPECTS_THREE_MEMORY_RECORDS')
    keys: list[str] = []
    for card in memory_cards:
        if not isinstance(card, Mapping) or not isinstance(card.get('key'), str):
            raise ValueError('INVALID_MEMORY_KEY')
        if not isinstance(card.get('value'), str):
            raise ValueError('INVALID_MEMORY_VALUE')
        keys.append(card['key'])
    if len(set(keys)) != len(keys):
        raise ValueError('DUPLICATE_MEMORY_KEYS')
    mask = [key == target for key in keys]
    if sum(mask) != 1:
        raise ValueError('ORACLE_NOT_EXACTLY_ONE_MATCH')
    return mask


@dataclass(frozen=True)
class EncodedMemory:
    keys: Tensor   # [B,K,256], frozen-tokenizer/frozen-embedding encoding
    values: Tensor # [B,K,256], separate encoding of each associated value
    mask: Tensor   # [B,K] bool; oracle keeps exactly one target; no-memory all false


def encode_cards_for_reader(
    questions: Sequence[str],
    per_question_cards: Sequence[Sequence[Mapping[str, str]]],
    text_to_ids: Callable[[str], Sequence[int]],
    frozen_embedding_weight: Tensor,
    *,
    no_memory: bool = False,
) -> EncodedMemory:
    """Pure input adapter; text_to_ids must be the pinned T1 tokenizer at pilot time.

    Does not accept labels/answers/targets; only input strings from question and
    external fact cards. Stops on invalid token IDs, EOS, empty tokens and shape.
    """
    if frozen_embedding_weight.ndim != 2 or tuple(frozen_embedding_weight.shape) != (2048, D_MODEL):
        raise ValueError('FROZEN_TIED_EMBEDDING_SHAPE_MISMATCH')
    if len(questions) != len(per_question_cards) or not questions:
        raise ValueError('QUESTION_MEMORY_BATCH_SHAPE_MISMATCH')
    if no_memory:
        # A true no-memory arm: NEVER inspect cards, search keys or tokenize facts.
        empty = frozen_embedding_weight.detach().new_zeros((len(questions), 0, D_MODEL))
        no_mask = torch.zeros((len(questions), 0), dtype=torch.bool, device=frozen_embedding_weight.device)
        return EncodedMemory(empty, empty.clone(), no_mask)
    key_rows, value_rows, masks = [], [], []
    def frozen_encode(s: str) -> Tensor:
        ids = list(text_to_ids(s))
        if not ids or any(not isinstance(i,int) or i<0 or i>=2048 or i==256 for i in ids):
            raise ValueError('TOKENIZER_IDS_INVALID')
        if len(ids)>256:
            raise ValueError('T1_CONTEXT_OVERFLOW')
        t = torch.tensor(ids, dtype=torch.long, device=frozen_embedding_weight.device)
        return F.embedding(t, frozen_embedding_weight.detach()).mean(dim=0)
    with torch.no_grad():
        for question, cards in zip(questions, per_question_cards):
            # Mask is formed *only* from the observed question and memory keys.
            mask = oracle_key_mask(question, cards)
            key_rows.append(torch.stack([frozen_encode(card['key']) for card in cards]))
            # Prefix is fixed and public; not read from any target/gold metadata.
            value_rows.append(torch.stack([frozen_encode(' ' + card['value']) for card in cards]))
            masks.append(mask)
    return EncodedMemory(
        torch.stack(key_rows), torch.stack(value_rows),
        torch.tensor(masks, dtype=torch.bool, device=frozen_embedding_weight.device)
    )


class GatedOracleReader(nn.Module):
    """Frozen-backbone compatible post-P02 reader; all weights here trainable later.

    Uses separate Key/Value vectors, masked cross-attention, per-query learned
    gate, zero-initialized output projection. Attention and MLP of P02 stay frozen.
    """
    def __init__(self, d_model: int = D_MODEL, d_key: int = 64, d_value: int = 128):
        super().__init__()
        if d_model != 256 or d_key <= 0 or d_value <= 0:
            raise ValueError('UNSUPPORTED_READER_DIMENSIONS')
        self.query_proj = nn.Linear(d_model, d_key, bias=False)
        self.key_proj = nn.Linear(d_model, d_key, bias=False)
        self.value_proj = nn.Linear(d_model * 2, d_value, bias=False)
        self.output_proj = nn.Linear(d_value, d_model, bias=False)
        nn.init.zeros_(self.output_proj.weight)  # zero-effect cold-start
        self.gate_net = nn.Sequential(
            nn.Linear(d_model + d_value + 1, 32), nn.GELU(), nn.Linear(32, 1)
        )
        nn.init.zeros_(self.gate_net[-1].weight)
        nn.init.constant_(self.gate_net[-1].bias, -4.0)

    def forward(self, hidden: Tensor, memory: EncodedMemory) -> tuple[Tensor, Tensor]:
        if hidden.ndim != 2 or hidden.shape[1] != D_MODEL:
            raise ValueError('HIDDEN_SHAPE_MISMATCH')
        keys, vals, mask = memory.keys, memory.values, memory.mask
        if keys.ndim != 3 or keys.shape != vals.shape or keys.shape[0] != hidden.shape[0] or keys.shape[-1] != D_MODEL:
            raise ValueError('MEMORY_VECTOR_SHAPE_MISMATCH')
        if mask.shape != keys.shape[:2] or mask.dtype != torch.bool:
            raise ValueError('MEMORY_MASK_SHAPE_MISMATCH')
        if keys.device != hidden.device or vals.device != hidden.device or mask.device != hidden.device:
            raise ValueError('MEMORY_DEVICE_MISMATCH')
        # Handle the all-masked case before softmax to avoid NaN/undefined attention.
        active = mask.any(dim=1) if keys.shape[1] else torch.zeros(hidden.shape[0], device=hidden.device, dtype=torch.bool)
        if not bool(active.any().item()):
            return hidden, hidden.new_zeros((hidden.shape[0], 1))
        q = self.query_proj(F.layer_norm(hidden, (D_MODEL,))).unsqueeze(1)
        k = self.key_proj(F.layer_norm(keys, (D_MODEL,)))
        v = self.value_proj(torch.cat((keys, vals), dim=-1))
        logits = (q * k).sum(dim=-1) / (q.shape[-1] ** .5)
        logits = logits.masked_fill(~mask, -1e9)
        weights = logits.softmax(dim=-1)
        weights = weights * mask.to(weights.dtype)
        weights = weights / weights.sum(dim=-1, keepdim=True).clamp_min(1e-12)
        read = (weights.unsqueeze(-1) * v).sum(dim=1)
        confidence = weights.max(dim=1, keepdim=True).values
        gate = torch.sigmoid(self.gate_net(torch.cat((F.layer_norm(hidden, (D_MODEL,)), read, confidence), dim=-1)))
        delta = gate * self.output_proj(read)
        changed = hidden + delta
        # Guarantee exact bypass per row even in mixed all-masked batches.
        out = torch.where(active[:, None], changed, hidden)
        return out, torch.where(active[:, None], gate, torch.zeros_like(gate))


def logits_from_hidden(hidden: Tensor, tied_output_weight: Tensor, reader: GatedOracleReader,
                       memory: EncodedMemory) -> tuple[Tensor, Tensor]:
    if tied_output_weight.ndim != 2 or tuple(tied_output_weight.shape) != (2048, D_MODEL):
        raise ValueError('TIED_OUTPUT_WEIGHT_SHAPE_MISMATCH')
    h, gate = reader(hidden, memory)
    return F.linear(h, tied_output_weight), gate
