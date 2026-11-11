#!/usr/bin/env python3
"""TTM Vector Memory: fresh NON-TEST Top-k probe, source-only, no model execution.

Design artifact for frozen Reader generalization. All aliases are synthetic; no
TRAIN/DEV/TEST is loaded to generate this probe. This file never opens TEST,
loads trained weights, runs inference or trains. No gold answer is passed into
retrieval APIs. Probe is exploratory and cannot claim independent TEST success.
"""
from __future__ import annotations
import argparse
import hashlib
import json
import math
import re
from pathlib import Path
from typing import Callable, Sequence

SCHEMA = 'ttm.vm.externalfacts.nontest_topk_probe.v1'
PROBE_ID = 'TTM_VM_TOPK_NONTEST_FROZEN_READER_20261111_V1'
SEED = 'TTM_VM_FRESH_NONTEST_TOPK_PROBE_20261111_V1'
N_CASES, BANK_SIZE = 128, 32
ALPHABET = 'bcdfghjklmnpqrstvwxz'
LABELS = ('bivor', 'caxen', 'doral', 'fekum', 'gilen', 'havor', 'jekin', 'kofur',
          'lamet', 'mipor', 'navek', 'pizol', 'raqum', 'sivel', 'tobak', 'wexil')
PAT = re.compile(r'(?<![A-Za-z0-9])obj[bcdfghjklmnpqrstvwxz]{12}(?![A-Za-z0-9])')


def digest(*parts: object) -> bytes:
    return hashlib.sha256((SEED + '|' + '|'.join(map(str, parts))).encode()).digest()


def alias(index: int, slot: int) -> str:
    b = digest('key', index, slot)
    return 'obj' + ''.join(ALPHABET[x % len(ALPHABET)] for x in b[:12])


def make_case(index: int) -> dict:
    if not (0 <= index < N_CASES):
        raise ValueError('INDEX_OUT_OF_RANGE')
    target = alias(index, 0)
    answer = LABELS[(index * 5 + 3) % 16]
    # Four near-neighbor one-character mutations intentionally challenge
    # approximate retrieval. They are NOT the target and cannot contain gold.
    keys = [target]
    for j, pos in enumerate((0, 3, 6, 9)):
        chars = list(target[3:]); old = chars[pos]
        chars[pos] = ALPHABET[(ALPHABET.index(old) + j + 1) % len(ALPHABET)]
        keys.append('obj' + ''.join(chars))
    slot = 1
    while len(keys) < BANK_SIZE:
        candidate = alias(index, slot)
        slot += 1
        if candidate not in keys:
            keys.append(candidate)
    if len(set(keys)) != BANK_SIZE:
        raise AssertionError('DUPLICATE_KEYS')
    order = sorted(range(BANK_SIZE), key=lambda j: (digest('order', index, j), j))
    # The distractors never carry the target answer. This makes attribution
    # based on correct value observable when the retrieved key is correct.
    def value(j: int) -> str:
        if j == 0: return answer
        return LABELS[((index * 5 + 3) + 1 + ((j * 7) % 15)) % 16]
    cards = [{'key':keys[j], 'value':value(j)} for j in order]
    # Make sure no distractor accidentally uses the correct label.
    for card in cards:
        if card['key'] != target and card['value'] == answer:
            card['value'] = LABELS[(LABELS.index(answer) + 1) % 16]
    wrong_label = LABELS[(LABELS.index(answer) + 1) % 16]
    foil = [dict(card) for card in cards]
    for card in foil:
        if card['key'] == target: card['value'] = wrong_label
    q = (f'For archive object {target}, what is its assigned access tag? Answer:'
         if index % 2 == 0 else
         f'Which access tag belongs to archive object {target}? Answer:')
    return {
        'schema':SCHEMA, 'case_id':f'vm-probe-{index:04d}', 'split':'non_test_probe',
        'question':q, 'answer':answer, 'target_key':target,
        'correct_memory':cards, 'wrong_memory':foil,
        'none_memory':[], 'answer_only_scoring':True,
        'probe_not_training_or_test':True,
    }


def build() -> list[dict]:
    cases=[make_case(i) for i in range(N_CASES)]
    allkeys=[card['key'] for case in cases for card in case['correct_memory']]
    if len(set(allkeys)) != N_CASES * BANK_SIZE:
        raise AssertionError('GLOBAL_KEY_COLLISION')
    return cases


def char_ngrams(s: str, n: int = 3) -> set[str]:
    return {s[i:i+n] for i in range(max(0, len(s)-n+1))}


def rank_lexical_full_question(question: str, cards: Sequence[dict]) -> list[int]:
    """Non-Oracle char-trigram score on full question vs card key only.

    This is a transparent lexical control, not semantic vector retrieval.
    It does NOT regex-extract the gold key or accept labels/target_key.
    """
    q=char_ngrams(question.lower())
    scores=[]
    for i,card in enumerate(cards):
        key=card['key']; g=char_ngrams(key.lower())
        overlap=len(q & g) / max(1,len(g))
        scores.append((-overlap,key,i))
    return [index for _,_,index in sorted(scores)]


def rank_frozen_full_question_cosine(question: str, cards: Sequence[dict],
                                      text_to_ids: Callable[[str], Sequence[int]],
                                      frozen_embedding_weight) -> list[int]:
    """Primary retrieval proposal: full question mean-T1 embedding vs key.

    Requires supplied exact, frozen T1 encoder and tied embedding at future
    execution. No answer, target_key, oracle mask, learned retriever or TEST.
    Deterministic tie-break by lexical key only; scores use only query and key.
    Does NOT run until explicitly called later; no model loads here.
    """
    import torch
    from torch.nn import functional as F
    if not isinstance(question,str) or not question:
        raise ValueError('BAD_QUESTION')
    if frozen_embedding_weight.shape != (2048,256):
        raise ValueError('WRONG_FROZEN_EMBEDDING_SHAPE')
    def enc(s):
        ids=list(text_to_ids(s))
        if not ids or len(ids)>256 or any((not isinstance(x,int) or x<0 or x>=2048) for x in ids):
            raise ValueError('BAD_FROZEN_T1_IDS')
        t=torch.tensor(ids,dtype=torch.long,device=frozen_embedding_weight.device)
        return F.embedding(t,frozen_embedding_weight.detach()).mean(0)
    with torch.no_grad():
        q=F.normalize(enc(question),dim=0)
        scores=[]
        for i,card in enumerate(cards):
            key=card['key']; v=F.normalize(enc(key),dim=0)
            score=float(torch.dot(q,v))
            if not math.isfinite(score):raise ValueError('BAD_SIMILARITY')
            scores.append((-score,key,i))
    return [i for _,_,i in sorted(scores)]


def oracle_upper_bound_rank(question: str, cards: Sequence[dict]) -> list[int]:
    """Positive control only, forbidden for non-oracle primary selection."""
    found=PAT.findall(question)
    if len(found)!=1:raise ValueError('ORACLE_TARGET_NOT_UNIQUE')
    hits=[i for i,c in enumerate(cards) if c['key']==found[0]]
    if len(hits)!=1:raise ValueError('ORACLE_CARD_NOT_UNIQUE')
    return hits+[i for i in range(len(cards)) if i not in hits]


def mask_from_rank(indices: Sequence[int], length: int, k: int) -> list[bool]:
    if k not in (1,3) or len(indices)!=length or sorted(indices)!=list(range(length)):
        raise ValueError('INVALID_RANK_OR_K')
    selected=set(indices[:k]);return [i in selected for i in range(length)]


def main() -> None:
    ap=argparse.ArgumentParser()
    ap.add_argument('--out',type=Path,required=True)
    ap.add_argument('--root',type=Path,required=True)
    args=ap.parse_args()
    root=args.root.resolve(strict=True); out=args.out.resolve()
    if not out.is_relative_to(root):raise SystemExit('DENY_OUTPUT_OUTSIDE_PROJECT')
    if out.exists():raise SystemExit('NO_OVERWRITE_NONTEST_PROBE')
    cases=build()
    raw=json.dumps({'schema':SCHEMA,'split':'non_test_probe','cases':cases},sort_keys=True,separators=(',',':'))+'\n'
    out.parent.mkdir(parents=True,exist_ok=True)
    out.write_bytes(raw.encode('utf8'))
    print(json.dumps({'status':'NONTEST_PROBE_GENERATED_NO_MODEL_EXECUTION',
                      'cases':len(cases),'bank_size':BANK_SIZE,
                      'sha256':hashlib.sha256(raw.encode()).hexdigest(),
                      'test_accessed':False,'reader_loaded':False},sort_keys=True))

if __name__=='__main__':main()
