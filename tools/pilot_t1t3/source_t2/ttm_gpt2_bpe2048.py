#!/usr/bin/env python3
"""TTM-Small-4M TRAIN-only GPT-2 pretokenized 2,048-ID byte BPE.

T2 engineering implementation. No data download; no scientific training.
An actual TRAIN corpus must first be independently pinned, rights-reviewed and
split-leakage QA'd. The synthetic TRAIN fixture is not that dataset.
"""
from __future__ import annotations
from collections import Counter
from dataclasses import dataclass
import hashlib
import json
from typing import Iterable
import regex

EOS_ID = 256
VOCAB_SIZE = 2048
N_MERGES = 1791
GPT2_PATTERN = r"'s|'t|'re|'ve|'m|'ll|'d| ?\p{L}+| ?\p{N}+| ?[^\s\p{L}\p{N}]+|\s+(?!\S)"
PRE_REGEX = regex.compile(GPT2_PATTERN)
MODEL_NAME = 'ttm.gpt2.pretokenized.byte-bpe.2048.v1'


def canonical_bytes(obj: object) -> bytes:
    return json.dumps(obj, ensure_ascii=False, sort_keys=True, separators=(',', ':')).encode('utf-8')


def sha(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def byte_to_unicode() -> dict[int, str]:
    bs = list(range(33,127)) + list(range(161,173)) + list(range(174,256))
    cs = bs.copy()
    n = 0
    for i in range(256):
        if i not in bs:
            bs.append(i)
            cs.append(256+n)
            n += 1
    return dict(zip(bs, map(chr,cs)))


BYTE2CHAR = byte_to_unicode()
CHAR2BYTE = {v:k for k,v in BYTE2CHAR.items()}


def pretok(text: str) -> tuple[str, ...]:
    """Exact GPT-2 regex specification; retains every UTF-8 codepoint."""
    parts: list[str] = []
    pos = 0
    for m in PRE_REGEX.finditer(text):
        # GPT-2 regex alone can leave unmatched interior whitespace (e.g.
        # a\nb, a\tb); native llama.cpp unicode_regex_split retains
        # those bytes as their own pretokenized fragments. Never discard.
        if m.start() > pos:
            parts.append(text[pos:m.start()])
        parts.append(m.group(0))
        pos = m.end()
    if pos < len(text):
        parts.append(text[pos:])
    if ''.join(parts) != text:
        raise ValueError('GPT2_PRETOKENIZER_LOST_INPUT')
    return tuple(parts)


@dataclass(frozen=True)
class Story:
    story_id: str
    text: str
    split: str
    source: str


def _bpe_merge(ids: list[int], pair: tuple[int,int], new_id: int) -> list[int]:
    output: list[int] = []
    i=0
    while i < len(ids):
        if i+1 < len(ids) and (ids[i],ids[i+1]) == pair:
            output.append(new_id)
            i+=2
        else:
            output.append(ids[i]);i+=1
    return output


class BPE2048:
    def __init__(self, tokens: list[str], pairs: list[tuple[int,int]], source_commitment: str, source_kind: str):
        if len(tokens) != VOCAB_SIZE or len(pairs) != N_MERGES:
            raise ValueError('VOCAB_OR_MERGE_COUNT_MISMATCH')
        if len(set(tokens))!=VOCAB_SIZE or tokens[EOS_ID]!='<|endoftext|>':
            raise ValueError('TOKEN_CONTENT_INVALID')
        if tokens[:256] != [BYTE2CHAR[i] for i in range(256)]:
            raise ValueError('BYTE_IDS_CHANGED')
        self.tokens=tuple(tokens)
        self.pairs=tuple(pairs)
        self.ranks={pair:rank for rank,pair in enumerate(pairs)}
        if len(self.ranks)!=N_MERGES:
            raise ValueError('DUPLICATE_MERGE_PAIR')
        for rank,(a,b) in enumerate(pairs):
            if a >= 257+rank or b >= 257+rank or min(a,b)<0:
                raise ValueError('MERGE_ORDER_NOT_CAUSAL')
            if tokens[257+rank]!=tokens[a]+tokens[b]:
                raise ValueError('MERGE_TEXT_NOT_COHERENT')
        self.source_commitment=source_commitment
        self.source_kind=source_kind

    @classmethod
    def from_manifest(cls, obj: dict) -> 'BPE2048':
        if not isinstance(obj,dict) or obj.get('schema') != MODEL_NAME:
            raise ValueError('TOKENIZER_MANIFEST_SCHEMA_MISMATCH')
        contents=dict(obj)
        original=contents.pop('manifest_sha256',None)
        if original is None or original!=sha(canonical_bytes(contents)):
            raise ValueError('TOKENIZER_MANIFEST_SHA_MISMATCH')
        if contents.get('regex') != GPT2_PATTERN or contents.get('vocab_size')!=VOCAB_SIZE or contents.get('eos_id')!=EOS_ID:
            raise ValueError('TOKENIZER_METADATA_INCOMPATIBLE')
        bpe=cls(contents['tokens'],[tuple(x) for x in contents['pair_ids']],contents['source_commitment'],contents['source_kind'])
        if contents.get('token_merges_sha256')!=sha(canonical_bytes(bpe.gguf_token_merges())):
            raise ValueError('TOKENIZER_MERGES_SHA_MISMATCH')
        return bpe

    def encode(self, text: str) -> list[int]:
        out=[]
        for part in pretok(text):
            ids=list(part.encode('utf-8'))
            # Same ranked pair selection semantics as GPT-2 BPE: lowest rank,
            # and leftmost occurrence for a rank tie.
            while len(ids)>1:
                candidates=((self.ranks[(ids[i],ids[i+1])], i)
                            for i in range(len(ids)-1) if (ids[i],ids[i+1]) in self.ranks)
                selected=min(candidates,default=None)
                if selected is None:break
                rank,i=selected
                ids[i:i+2]=[257+rank]
            out.extend(ids)
        return out

    def decode(self, ids: list[int], *, allow_eos: bool=False) -> str:
        if any(i<0 or i>=VOCAB_SIZE for i in ids):
            raise ValueError('TOKEN_ID_OUT_OF_RANGE')
        if EOS_ID in ids and not allow_eos:
            raise ValueError('EOS_IN_TEXT_DECODE')
        s=''.join(self.tokens[i] for i in ids if i!=EOS_ID)
        try:
            return bytes(CHAR2BYTE[c] for c in s).decode('utf-8','strict')
        except (UnicodeDecodeError,KeyError) as e:
            raise ValueError('UTF8_DECODE_FAILURE') from e

    def gguf_token_merges(self) -> tuple[list[str],list[str]]:
        return list(self.tokens),[self.tokens[a]+' '+self.tokens[b] for a,b in self.pairs]

    def manifest(self) -> dict:
        obj={'schema':MODEL_NAME,'vocab_size':VOCAB_SIZE,'eos_id':EOS_ID,
             'regex':GPT2_PATTERN,'regex_engine':'regex','source_kind':self.source_kind,
             'source_commitment':self.source_commitment,
             'tokens':list(self.tokens),'pair_ids':[list(pair) for pair in self.pairs],
             'token_merges_sha256':sha(canonical_bytes(self.gguf_token_merges()))}
        obj['manifest_sha256']=sha(canonical_bytes(obj))
        return obj


def train_only(stories: Iterable[Story], source_kind: str) -> BPE2048:
    if source_kind not in ('SYNTHETIC_TRAIN_FIXTURE','PINNED_TINYSTORIES_TRAIN'):
        raise ValueError('SOURCE_KIND_NOT_AUTHORIZED')
    stories=list(stories)
    if not stories or len({s.story_id for s in stories})!=len(stories):
        raise ValueError('MISSING_OR_DUPLICATE_STORIES')
    if any(s.split != 'TRAIN' for s in stories):
        raise ValueError('TRAIN_ONLY_GATE_REJECTED_VAL_TEST')
    if any(s.source != ('SYNTHETIC_TRAIN_FIXTURE' if source_kind=='SYNTHETIC_TRAIN_FIXTURE'
                        else 'TinyStories-train.txt') for s in stories):
        raise ValueError('TRAIN_ONLY_SOURCE_BOUNDARY_VIOLATION')
    if any(not isinstance(s.text,str) for s in stories):
        raise ValueError('STORY_TEXT_TYPE_INVALID')
    # This is only provenance of supplied inputs, not proof of an externally
    # authenticated dataset. Real acquisition/manifest locking is separate.
    inputs=[{'id':s.story_id,'text_sha256':sha(s.text.encode('utf-8')),'source':s.source} for s in stories]
    provenance=sha(canonical_bytes(inputs))
    segments=[list(p.encode('utf-8')) for s in stories for p in pretok(s.text) if p]
    if not segments:
        raise ValueError('NO_PRETOKENIZED_TRAIN_CONTENT')
    token_bytes=[bytes([i]) for i in range(256)]+[b'']
    tokens=[BYTE2CHAR[i] for i in range(256)]+['<|endoftext|>']
    pairs=[]
    seen_text=set(token_bytes[:256])
    for rank in range(N_MERGES):
        counter=Counter()
        for seg in segments:
            counter.update(zip(seg,seg[1:]))
        viable=[(cnt,a,b) for (a,b),cnt in counter.items()
                if token_bytes[a]+token_bytes[b] not in seen_text]
        if not viable:
            raise ValueError(f'INSUFFICIENT_TRAIN_PAIRS_{rank}_OF_{N_MERGES}')
        # highest count, then lowest numeric left/right ID for deterministic tie
        count,a,b=min(viable,key=lambda x:(-x[0],x[1],x[2]))
        pair=(a,b)
        new_id=257+rank
        new_bytes=token_bytes[a]+token_bytes[b]
        new_text=tokens[a]+tokens[b]
        if new_text in tokens:
            raise AssertionError('DUPLICATE_TOKEN')
        token_bytes.append(new_bytes)
        tokens.append(new_text)
        pairs.append(pair)
        seen_text.add(new_bytes)
        segments=[_bpe_merge(seg,pair,new_id) if pair[0] in seg else seg for seg in segments]
    return BPE2048(tokens,pairs,provenance,source_kind)


def synthetic_train_stories() -> list[Story]:
    """Deterministic non-science generator; no test fixture phrases mixed in."""
    import random
    r=random.Random(20261108)
    chars='abcdefghijklmopqrstuvwxyz0123456789'
    corpus=[]
    for i in range(720):
        word=''.join(r.choice(chars) for _ in range(22+(i%14)))
        text=word+' '+''.join(r.choice(chars) for _ in range(11+(i%7)))
        if i%19==0:text+=' élan công nghệ'
        corpus.append(Story(story_id=f'SYNTHETIC_TRAIN_{i:04d}',text=text,
                            split='TRAIN',source='SYNTHETIC_TRAIN_FIXTURE'))
    return corpus
