#!/usr/bin/env python3
"""Source-only v2 retrieval: exact-ID, exact-alias, and lexical-first descriptor.

Ranking consumes question and explicit public index fields ONLY. The
answer, gold target_key, memory value and wrong_memory are never arguments.
S2 is closed-vocabulary structured description matching, NOT open semantic QA.
"""
from __future__ import annotations
from dataclasses import dataclass
from collections.abc import Callable, Mapping, Sequence
import re
import unicodedata
from v2_nontest_fixture import VOCAB, ATTRS

OBJECT_PATTERN = re.compile(r'(?<![a-z0-9])(obja[bcdfghjklmnpqrstvwxz]{11})(?![a-z0-9])')
ALIAS_PATTERN = re.compile(r'(?<![a-z0-9])(aka[bcdfghjklmnpqrstvwxz]{11})(?![a-z0-9])')

@dataclass(frozen=True)
class Retrieval:
    method: str
    indices: tuple[int, ...]
    status: str
    cause: str


def norm(text: str) -> str:
    if not isinstance(text,str):
        raise ValueError('NOT_A_STRING')
    return unicodedata.normalize('NFKC', text).lower().strip()


def _unique_bank(cards: Sequence[Mapping[str,str]]):
    if len(cards)!=32:
        raise ValueError('BANK_SIZE_NOT_32')
    keys=[card.get('key') for card in cards]
    if any(not isinstance(x,str) or not x for x in keys):
        raise ValueError('BAD_KEY')
    if len(set(keys))!=32:
        raise ValueError('DUPLICATE_KEY')


def _only_index_fields(cards: Sequence[Mapping[str,str]], allowed: set[str]):
    _unique_bank(cards)
    result=[]
    for card in cards:
        result.append({k:card.get(k) for k in allowed})
    return result


def _exact(question: str, cards: Sequence[Mapping[str,str]], pattern: re.Pattern,
           field: str, method: str) -> Retrieval:
    indexed=_only_index_fields(cards,{'key',field})
    found=pattern.findall(norm(question))
    if len(found)!=1:
        return Retrieval(method,(), 'ABSTAIN','NO_UNIQUE_PUBLIC_IDENTIFIER')
    matches=[i for i,c in enumerate(indexed)
             if isinstance(c.get(field),str) and norm(c[field]) == found[0]]
    if len(matches)!=1:
        return Retrieval(method,(), 'ABSTAIN','MISSING_OR_AMBIGUOUS_INDEX_MATCH')
    return Retrieval(method,(matches[0],),'SELECTED','EXACT_PUBLIC_IDENTITY')


def exact_id(question: str, cards: Sequence[Mapping[str,str]]) -> Retrieval:
    return _exact(question,cards,OBJECT_PATTERN,'key','R_EXACT_ID')


def exact_alias(question: str, cards: Sequence[Mapping[str,str]]) -> Retrieval:
    return _exact(question,cards,ALIAS_PATTERN,'lookup_alias','R_EXACT_ALIAS')


def _vocab_map():
    result={}; per_axis={}
    for attr in ATTRS:
        variants={}
        for original,synonym in VOCAB[attr]:
            for item in (original,synonym):
                item=norm(item)
                if item in result:
                    raise ValueError('AMBIGUOUS_CANONICAL_VOCAB:'+item)
                result[item]=original
                variants[item]=original
        per_axis[attr]=variants
    return result,per_axis

ALL_TO_CANON,PER_AXIS = _vocab_map()
WORDS_RE = re.compile(r'(?<![a-z0-9])(?:'+'|'.join(re.escape(s) for s in sorted(ALL_TO_CANON,key=lambda s:(-len(s),s)))+r')(?![a-z0-9])')


def canonical_text(text: str) -> str:
    return WORDS_RE.sub(lambda m:ALL_TO_CANON[m.group(0)],norm(text))


def key_grams(text: str, n:int=3) -> set[str]:
    s=canonical_text(text)
    return {s[i:i+n] for i in range(len(s)-n+1)} if len(s)>=n else set()


def parsed_attributes(text: str) -> tuple[str,str,str] | None:
    text=norm(text)
    words=WORDS_RE.findall(text)
    values=[]
    for attr in ATTRS:
        hits={PER_AXIS[attr][word] for word in words if word in PER_AXIS[attr]}
        if len(hits)!=1:
            return None
        values.append(next(iter(hits)))
    return tuple(values)


def hybrid_description(question: str,
                       cards: Sequence[Mapping[str,str]],
                       *, top_k: int=1,
                       fallback_cosine: Callable[[str,Sequence[Mapping[str,str]]],Sequence[float]]|None=None
                       ) -> Retrieval:
    """Lex-first on question vs public retrieval_text, unique-description gate.

    An explicit three-field canonical signature is an abstention safeguard:
    missing/ambiguous descriptors fail closed even if lexical nearest neighbor
    has a high score. This is a controlled, closed-vocab retrieval exercise.
    """
    if top_k not in (1,3):
        raise ValueError('ONLY_FROZEN_K1_OR_K3')
    index=_only_index_fields(cards,{'key','retrieval_text'})
    q_attrs=parsed_attributes(question)
    if q_attrs is None:
        return Retrieval('R_HYBRID_LEX_FIRST',(),'ABSTAIN','QUERY_ATTRIBUTES_MISSING_OR_AMBIGUOUS')
    desc=[card['retrieval_text'] for card in index]
    if any(not isinstance(x,str) or not x for x in desc):
        raise ValueError('INVALID_INDEX_DESCRIPTOR')
    signatures=[parsed_attributes(d) for d in desc]
    if any(s is None for s in signatures):
        raise ValueError('INVALID_INDEX_ATTRIBUTES')
    candidates=[i for i,s in enumerate(signatures) if s==q_attrs]
    if len(candidates)!=1:
        return Retrieval('R_HYBRID_LEX_FIRST',(),'ABSTAIN','MISSING_OR_AMBIGUOUS_FULL_DESCRIPTION')
    q=key_grams(question)
    scores=[]
    for d in desc:
        grams=key_grams(d)
        scores.append(len(q & grams)/max(1,len(grams)))
    source='LEXICAL_TRIGRAM'
    if not any(x>0 for x in scores):
        if fallback_cosine is None:
            return Retrieval('R_HYBRID_LEX_FIRST',(),'ABSTAIN','NO_LEXICAL_SCORE_AND_NO_FROZEN_FALLBACK')
        # Fallback is a supplied frozen T1/P02 cosine scorer, never trained here.
        scores=list(fallback_cosine(question,index))
        if len(scores)!=32 or any(not isinstance(x,(float,int)) or not (-1.01<=x<=1.01) for x in scores):
            raise ValueError('BAD_FROZEN_FALLBACK_SCORE')
        source='FROZEN_COSINE_FALLBACK'
    rank=sorted(range(32),key=lambda i:(-scores[i],norm(index[i]['key'])))
    if rank[0]!=candidates[0]:
        return Retrieval('R_HYBRID_LEX_FIRST',(),'ABSTAIN','TOP_RANK_NOT_UNIQUE_DESCRIPTION')
    return Retrieval('R_HYBRID_LEX_FIRST',tuple(rank[:top_k]),'SELECTED',source)


def mask(result: Retrieval, *, n: int=32) -> tuple[bool,...]:
    if result.status=='ABSTAIN':
        return (False,)*n
    if result.status!='SELECTED' or not result.indices or len(set(result.indices))!=len(result.indices):
        raise ValueError('INVALID_RETRIEVAL_RESULT')
    if any(not isinstance(i,int) or i<0 or i>=n for i in result.indices):
        raise ValueError('INDEX_OUT_OF_RANGE')
    chosen=set(result.indices)
    return tuple(i in chosen for i in range(n))


def frozen_description_cosine(question: str, cards: Sequence[Mapping[str,str]],
                              text_to_ids: Callable[[str],Sequence[int]],
                              frozen_embedding) -> list[float]:
    """Frozen T1/P02 embedding fallback on descriptor, NOT on private value.

    For future CPU science only; technical QA can supply mock T1 + random
    embeddings. Does not load a checkpoint or create any model weights.
    """
    import torch
    from torch.nn import functional as F
    if frozen_embedding.shape != (2048,256) or frozen_embedding.device.type != 'cpu':
        raise ValueError('FROZEN_EMBEDDING_SHAPE_DEVICE')
    if frozen_embedding.requires_grad:
        raise ValueError('FROZEN_EMBEDDING_REQUIRES_GRAD')
    if len(cards)!=32:
        raise ValueError('FROZEN_BANK_SIZE')
    def enc(txt):
        ids=list(text_to_ids(txt))
        if not ids or len(ids)>256 or any(type(x) is not int or x<0 or x>=2048 for x in ids):
            raise ValueError('INVALID_REAL_T1_IDS')
        t=torch.tensor(ids,dtype=torch.long,device='cpu')
        return F.normalize(F.embedding(t,frozen_embedding.detach()).mean(0),dim=0)
    with torch.no_grad():
        q=enc(question)
        return [float(torch.dot(q,enc(c['retrieval_text']))) for c in cards]
