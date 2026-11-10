"""Reconstruct strictly SHA-pinned TTM TRAIN-only BPE from private pair source.
This local-only code never reads TRAIN/VAL/TEST, does not export merges or access network.
"""
from __future__ import annotations
import base64, hashlib, json, regex
from pathlib import Path

EOS_ID=256
VOCAB_SIZE=2048
GPT2_PATTERN=r"'s|'t|'re|'ve|'m|'ll|'d| ?\p{L}+| ?\p{N}+| ?[^\s\p{L}\p{N}]+|\s+(?!\S)"
PRE_REGEX=regex.compile(GPT2_PATTERN)
def byte_to_unicode():
    bs=list(range(33,127))+list(range(161,173))+list(range(174,256))
    cs=bs.copy();n=0
    for i in range(256):
        if i not in bs:bs.append(i);cs.append(256+n);n+=1
    return dict(zip(bs,map(chr,cs)))
BYTE2CHAR=byte_to_unicode()
CHAR2BYTE={v:k for k,v in BYTE2CHAR.items()}
def canonical_bytes(obj):
    return json.dumps(obj,ensure_ascii=False,sort_keys=True,separators=(',',':')).encode()

def pretok(text):
    parts=[];pos=0
    for m in PRE_REGEX.finditer(text):
        if m.start()>pos:parts.append(text[pos:m.start()])
        parts.append(m.group(0));pos=m.end()
    if pos<len(text):parts.append(text[pos:])
    assert ''.join(parts)==text
    return parts
class BPE2048:
    def __init__(self,private_pairs_file):
        raw=base64.b64decode(Path(private_pairs_file).read_text('ascii').strip())
        assert len(raw)==1791*3
        pairs=[]
        for i in range(0,len(raw),3):
            val=(raw[i]<<16)|(raw[i+1]<<8)|raw[i+2]
            pairs.append(((val>>11)&2047,val&2047))
        tokens=[BYTE2CHAR[i] for i in range(256)]+['<|endoftext|>']
        for rank,(a,b) in enumerate(pairs):
            assert max(a,b)<257+rank
            tokens.append(tokens[a]+tokens[b])
        assert len(tokens)==2048 and len(set(tokens))==2048
        merges=[tokens[a]+' '+tokens[b] for a,b in pairs]
        digest=hashlib.sha256(canonical_bytes([tokens,merges])).hexdigest()
        assert digest=='aea0e2a1a1bc1943f20b767ba2f879e3a47f0cb43b8b66026b1a34a038e014af',f'BPE_MERGES_SHA_BAD_{digest}'
        self.tokens=tokens;self.pairs=pairs;self.ranks={pair:i for i,pair in enumerate(pairs)}
        self.public_hash=digest
    def encode(self,text):
        out=[]
        for part in pretok(text):
            ids=list(part.encode())
            while len(ids)>1:
                selected=min(((self.ranks[(ids[i],ids[i+1])],i) for i in range(len(ids)-1) if (ids[i],ids[i+1]) in self.ranks),default=None)
                if selected is None:break
                rank,i=selected;ids[i:i+2]=[257+rank]
            out.extend(ids)
        return out
    def decode(self,ids,allow_eos=False):
        assert all(0<=i<2048 for i in ids)
        assert 256 not in ids or allow_eos
        return bytes(CHAR2BYTE[c] for i in ids if i!=256 for c in self.tokens[i]).decode('utf-8','strict')
