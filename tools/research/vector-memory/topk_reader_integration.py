#!/usr/bin/env python3
"""Frozen TTM Reader Top-k input integration, no science execution.

This module never loads checkpoints, private weights, sealed TEST, or the old
DEV. It strictly reuses GatedOracleReader.forward from the frozen source blob
7ce728b2874284b87933237c890e54ce3d9fd651. The *retriever* is the
frozen full-question cosine, not oracle_key_mask or target_key lookup.

At future science execution: use exact SHA-pinned T1 tokenizer, frozen TTM
step-1280 token embedding, and SHA-locked L0020 reader_private.pt. Do not
train, tune, or select results on the former TRAIN/DEV/TEST.
"""
from __future__ import annotations
from collections.abc import Callable, Mapping, Sequence
from dataclasses import dataclass
from typing import Any
import torch
from torch import Tensor
from torch.nn import functional as F

# Imports resolved only to pinned source from same checked-out research tree.
import oracle_reader_source_only as reader_src
import topk_nontest_probe as probe_src

D_MODEL = 256
BANK = 32

@dataclass(frozen=True)
class RetrievedInputs:
    correct: reader_src.EncodedMemory
    wrong: reader_src.EncodedMemory
    none: reader_src.EncodedMemory
    # Debuggable opaque key order / rank; NEVER a gold-based selection.
    ordered_keys: tuple[str, ...]
    rank: tuple[int, ...]
    k: int


def _encode_frozen(s: str, tokenizer: Callable[[str], Sequence[int]], embedding: Tensor) -> Tensor:
    if not isinstance(s,str) or not s:
        raise ValueError('EMPTY_OR_INVALID_CARD_STRING')
    ids=list(tokenizer(s))
    if (not ids or len(ids)>256 or any(type(i) is not int or i<0 or i>=2048 or i==256 for i in ids)):
        raise ValueError('BAD_T1_TOKEN_IDS')
    indices=torch.tensor(ids,device=embedding.device,dtype=torch.long)
    return F.embedding(indices,embedding.detach()).mean(dim=0)


def encode_topk_inputs(question: str,
                       correct_cards: Sequence[Mapping[str,str]],
                       wrong_cards: Sequence[Mapping[str,str]],
                       tokenizer: Callable[[str], Sequence[int]],
                       frozen_embedding: Tensor,
                       *, k: int) -> RetrievedInputs:
    """Rank on (question, keys) only; no answer, target_key or Oracle API.

    Correct and wrong cards have exactly identical keys and order. Counterfactual
    substitution can never change the retrieval rankings. The immutable mask is
    drawn ONCE from the frozen cosine rank, shared across both arms.
    """
    if not isinstance(question,str) or not question:
        raise ValueError('INVALID_QUESTION')
    if k not in (1,3):
        raise ValueError('FROZEN_TOPK_MUST_BE_1_OR_3')
    if frozen_embedding.shape!=(2048,D_MODEL) or frozen_embedding.device.type!='cpu':
        raise ValueError('FROZEN_CPU_EMBEDDING_SHAPE_DEVICE')
    if frozen_embedding.requires_grad:
        raise ValueError('FROZEN_EMBEDDING_MUST_HAVE_NO_GRAD')
    if len(correct_cards)!=BANK or len(wrong_cards)!=BANK:
        raise ValueError('FROZEN_BANK_32_EXPECTED')
    c_keys=[];w_keys=[]
    for good,bad in zip(correct_cards,wrong_cards):
        for row in (good,bad):
            if not isinstance(row,Mapping) or not isinstance(row.get('key'),str) or not isinstance(row.get('value'),str):
                raise ValueError('CARD_KEY_VALUE_INVALID')
        c_keys.append(good['key']);w_keys.append(bad['key'])
    if c_keys!=w_keys or len(set(c_keys))!=BANK:
        raise ValueError('COUNTERFACTUAL_KEYS_OR_ORDER_CHANGED')

    # NO oracle function call and NO gold label. No query entity extraction.
    rank=probe_src.rank_frozen_full_question_cosine(question,correct_cards,tokenizer,frozen_embedding)
    mask=probe_src.mask_from_rank(rank,BANK,k)
    with torch.no_grad():
        # Encode all 32 records, including inactive cards, for a fixed-shaped
        # input and exact mask independence. Encoder is not the Oracle helper.
        keys=torch.stack([_encode_frozen(key,tokenizer,frozen_embedding) for key in c_keys])[None]
        g_vals=torch.stack([_encode_frozen(' '+row['value'],tokenizer,frozen_embedding) for row in correct_cards])[None]
        w_vals=torch.stack([_encode_frozen(' '+row['value'],tokenizer,frozen_embedding) for row in wrong_cards])[None]
    mask_tensor=torch.tensor([mask],dtype=torch.bool,device=frozen_embedding.device)
    mem_good=reader_src.EncodedMemory(keys,g_vals,mask_tensor)
    mem_wrong=reader_src.EncodedMemory(keys,w_vals,mask_tensor)
    empty=keys.new_empty((1,0,D_MODEL))
    mem_none=reader_src.EncodedMemory(empty,empty.clone(),torch.zeros((1,0),dtype=torch.bool,device=keys.device))
    return RetrievedInputs(mem_good,mem_wrong,mem_none,tuple(c_keys),tuple(rank),k)


def bypass_without_memory(hidden:Tensor, head:Tensor, reader:reader_src.GatedOracleReader,
                          none:reader_src.EncodedMemory) -> tuple[Tensor,Tensor]:
    """Reuse original frozen Reader code; exact no-memory equality expected."""
    return reader_src.logits_from_hidden(hidden,head,reader,none)


def validate_l0020_private_payload(payload: Mapping[str,Any],
                                   frozen_reader:reader_src.GatedOracleReader) -> dict:
    """Structural inspection after owner SHA readback, WITHOUT forward/inference.

    weights_only=True should be enforced by private owner caller. Validate full
    key/shape/dtype agreement and pilot's frozen source pins; do not change or
    save the private weight file.
    """
    if not isinstance(payload,Mapping):raise ValueError('PRIVATE_READER_PAYLOAD_NOT_MAPPING')
    if payload.get('steps')!=128:raise ValueError('PRIVATE_READER_TRAINING_STEP_MISMATCH')
    source=payload.get('source_pins')
    if not isinstance(source,Mapping):raise ValueError('PRIVATE_READER_MISSING_PINS')
    required={
        'reader_git_blob':'7ce728b2874284b87933237c890e54ce3d9fd651',
        'checkpoint_sha256':'ee723407b2c25a18be20e26387a3dd8e4a18e2942d469279b6f0748ff86af0dc',
        'p02_git_blob':'9762343e06cf800b50574c2871ae1ed58537fb18',
    }
    for key,expected in required.items():
        if source.get(key)!=expected:raise ValueError('PRIVATE_READER_SOURCE_PIN_MISMATCH:'+key)
    state=payload.get('reader_state_dict')
    expected_state=frozen_reader.state_dict()
    if not isinstance(state,Mapping) or set(state)!=set(expected_state):
        raise ValueError('PRIVATE_READER_KEYS_DIFFER')
    for k,t in state.items():
        if not isinstance(t,Tensor) or t.shape!=expected_state[k].shape or t.dtype!=torch.float32:
            raise ValueError('PRIVATE_READER_TENSOR_INVALID:'+k)
        if not torch.isfinite(t).all().item():raise ValueError('PRIVATE_READER_NONFINITE:'+k)
    return {'status':'PASS_PRIVATE_READER_STRUCTURE_SOURCE_PIN',
            'steps':128,'tensor_count':len(state),'shapes_match':True,
            'source_pins_match':True,'forward_calls':0,'optimizer_steps':0}
