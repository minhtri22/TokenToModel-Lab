#!/usr/bin/env python3
"""Exact, read-only T1 GPT-2 BPE2048 adapter from the owner's pinned manifest.

No tokenizer retraining, no source text, no raw pair export to GitHub.
"""
from __future__ import annotations
import hashlib,json,regex
from pathlib import Path
MANIFEST_FILE_SHA256='cba18e60cee3d08a353ee6d4a451017289e45af7b4b1179c87171b9b78d7dfdc'
MERGES_SHA256='aea0e2a1a1bc1943f20b767ba2f879e3a47f0cb43b8b66026b1a34a038e014af'
MANIFEST_INTERNAL_SHA256='6da22cf79c3a6cfd08d80a768eb1074125a753164ccf62a164e79545956e94c6'
PATTERN=regex.compile(r"'s|'t|'re|'ve|'m|'ll|'d| ?\p{L}+| ?\p{N}+| ?[^\s\p{L}\p{N}]+|\s+(?!\S)")

def bytes_unicode():
    bs=list(range(33,127))+list(range(161,173))+list(range(174,256))
    cs=bs.copy();n=0
    for i in range(256):
        if i not in bs:bs.append(i);cs.append(256+n);n+=1
    return dict(zip(bs,map(chr,cs)))

class PinnedT1BPE:
    def __init__(self,manifest_path):
        raw=Path(manifest_path).read_bytes()
        if hashlib.sha256(raw).hexdigest()!=MANIFEST_FILE_SHA256:raise ValueError('T1_MANIFEST_FILE_SHA256_MISMATCH')
        m=json.loads(raw.decode('utf8'))
        if m.get('manifest_sha256')!=MANIFEST_INTERNAL_SHA256:raise ValueError('T1_INTERNAL_MANIFEST_SHA_MISMATCH')
        pairs=m.get('pair_ids')
        if not isinstance(pairs,list) or len(pairs)!=1791:raise ValueError('NOT_1791_PAIRS')
        for i,p in enumerate(pairs):
            if len(p)!=2 or any(type(x) is not int or x<0 or x>=257+i for x in p):
                raise ValueError('INVALID_T1_MERGE_PAIR')
        tokens=[bytes_unicode()[i] for i in range(256)]+['<|endoftext|>']
        for a,b in pairs:tokens.append(tokens[a]+tokens[b])
        if len(tokens)!=2048 or len(set(tokens))!=2048:raise ValueError('T1_VOCAB_INCONSISTENT')
        merges=[tokens[a]+' '+tokens[b] for a,b in pairs]
        data=json.dumps([tokens,merges],ensure_ascii=False,sort_keys=True,separators=(',',':')).encode('utf8')
        if hashlib.sha256(data).hexdigest()!=MERGES_SHA256:raise ValueError('T1_MERGES_SHA256_MISMATCH')
        self.ranks={(a,b):i for i,(a,b) in enumerate(pairs)}
        self.manifest_sha256=MANIFEST_FILE_SHA256
    def encode(self,text):
        if type(text) is not str:raise TypeError('BPE_EXPECTS_TEXT')
        parts=[m.group(0) for m in PATTERN.finditer(text)]
        if ''.join(parts)!=text:raise ValueError('T1_PRETOKENIZER_DROPPED_TEXT')
        out=[]
        for part in parts:
            ids=list(part.encode('utf8'))
            while len(ids)>1:
                best=None
                for i in range(len(ids)-1):
                    rank=self.ranks.get((ids[i],ids[i+1]))
                    if rank is not None and (best is None or (rank,i)<best):best=(rank,i)
                if best is None:break
                rank,i=best;ids[i:i+2]=[257+rank]
            out.extend(ids)
        if any(t<0 or t>=2048 for t in out):raise ValueError('T1_INVALID_TOKEN')
        return out
