#!/usr/bin/env python3
"""TTM-Small-4M H-DEC-R1 D0/D1 exact deterministic selection: NO MODEL LOAD.

Frozen protocol: D0 unmodified greedy; D1 sign-aware penalty 1.15 to each
DISTINCT continuation token ID, once per step. Prompt tokens never penalized.

This pure logits adapter is source-only and does not perform inference.
"""
from __future__ import annotations
import math
from typing import Sequence

VOCAB_SIZE = 2048
EOS_ID = 256
PENALTY = 1.15
MAX_NEW_TOKENS = 64


def next_token_from_logits(logits: Sequence[float], continuation_ids: Sequence[int], arm: str) -> int:
    """Return lowest-id argmax after exact arm-specific logit transformation.

    Refuses any post-EOS call or invalid logits. Does not mutate caller's logits.
    """
    if arm not in ('D0', 'D1'):
        raise ValueError('ARM_NOT_D0_OR_D1')
    if len(logits) != VOCAB_SIZE:
        raise ValueError('LOGITS_VOCAB_MISMATCH')
    if len(continuation_ids) >= MAX_NEW_TOKENS:
        raise ValueError('NEW_TOKEN_LIMIT_EXCEEDED')
    if any(type(t) is not int or t < 0 or t >= VOCAB_SIZE for t in continuation_ids):
        raise ValueError('INVALID_CONTINUATION_TOKEN_ID')
    if EOS_ID in continuation_ids:
        raise ValueError('NO_STEP_AFTER_EOS')
    out = [float(x) for x in logits]
    if not all(math.isfinite(x) for x in out):
        raise ValueError('LOGIT_NON_FINITE')
    if arm == 'D1':
        for idx in set(continuation_ids):
            value = out[idx]
            out[idx] = value / PENALTY if value > 0 else (value * PENALTY if value < 0 else 0.0)
    # Python max preserves first index on ties; explicit index tie-break avoids ambiguity.
    best = max(range(VOCAB_SIZE), key=lambda i: (out[i], -i))
    return int(best)


def stop_reason(continuation_ids: Sequence[int]) -> str:
    if not continuation_ids:
        return 'CONTINUE'
    if continuation_ids[-1] == EOS_ID:
        return 'EOS'
    if len(continuation_ids) >= MAX_NEW_TOKENS:
        return 'MAX_NEW_TOKENS'
    return 'CONTINUE'
