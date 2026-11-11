#!/usr/bin/env python3
"""TTM Narrative CF1 frozen-O0 teacher-forced scoring engine.

Public source, no dataset/label dependence. No optimizer, no gradient, no GPU.
The ONLY model-input fields are context_a,context_b,completion_x,completion_y.
A separate evaluator handles DEV or private FINAL labels after outputs are sealed.
Requires the user's exact SHA-pinned BPE2048 and P02 source at runtime.
"""
from __future__ import annotations
from collections import Counter
from pathlib import Path
import hashlib, json, math
import torch
from torch.nn import functional as F

MODEL_SCHEMA='ttm.cf1.model_input.v1'
INPUT_KEYS=frozenset(('context_a','context_b','completion_x','completion_y'))
ROOT_KEYS=frozenset(('schema','records'))
P02_GIT_BLOB='9762343e06cf800b50574c2871ae1ed58537fb18'
P02_CONFIG={'vocab_size':2048,'max_seq_len':256,'n_embd':256,'n_layer':4,'n_head':4,'norm_type':'layernorm'}
PARENT_SHA='cb985751795c8328ad65acf7ca4c1033ce35182c1bfbdb8c38550de629cb271b'

class InputRejected(ValueError):pass

def strict_pairs_object(pairs):
    d={}
    for k,v in pairs:
        if k in d:raise InputRejected('DUPLICATE_JSON_KEY:'+k)
        d[k]=v
    return d

def load_model_inputs(raw:bytes):
    if not isinstance(raw,bytes) or len(raw)>1_000_000:raise InputRejected('BAD_INPUT_BYTES')
    try:
        obj=json.loads(raw.decode('utf8','strict'),object_pairs_hook=strict_pairs_object,
                 parse_constant=lambda x:(_ for _ in ()).throw(InputRejected('NONFINITE_JSON_LITERAL')))
    except (UnicodeDecodeError,json.JSONDecodeError) as e:raise InputRejected('INVALID_JSON') from e
    if type(obj) is not dict or set(obj)!=ROOT_KEYS or obj['schema']!=MODEL_SCHEMA:raise InputRejected('BAD_ROOT_SCHEMA_OR_EXTRAS')
    arr=obj['records']
    if type(arr) is not list or not 1<=len(arr)<=1000:raise InputRejected('BAD_RECORD_COUNT')
    dup=set()
    for j,r in enumerate(arr):
        if type(r) is not dict or set(r)!=INPUT_KEYS:raise InputRejected(f'RECORD_FIELD_LEAK_OR_MISSING_{j}')
        for k,v in r.items():
            if type(v) is not str or not (1<=len(v)<=1200):raise InputRejected('BAD_TEXT_TYPE_OR_LENGTH')
            if any(ord(ch)<32 and ch not in ('\n','\t') for ch in v):raise InputRejected('CONTROL_CHAR')
        if not (r['completion_x'].startswith(' ') and r['completion_y'].startswith(' ')):raise InputRejected('COMPLETION_NEEDS_LEADING_SPACE')
        if r['completion_x']==r['completion_y'] or r['context_a']==r['context_b']:raise InputRejected('NOT_A_COUNTERFACTUAL_PAIR')
        if (r['context_a'],r['context_b'],r['completion_x'],r['completion_y']) in dup:raise InputRejected('DUPLICATE_PAIR')
        dup.add((r['context_a'],r['context_b'],r['completion_x'],r['completion_y']))
    return arr

def exact_git_blob(data:bytes)->str:
    return hashlib.sha1(b'blob '+str(len(data)).encode('ascii')+b'\0'+data).hexdigest()

def sha_file(path)->str:
    h=hashlib.sha256()
    with Path(path).open('rb') as f:
        for chunk in iter(lambda:f.read(1<<20),b''):h.update(chunk)
    return h.hexdigest()

def length_and_prefix_check(encode,context,completion):
    """Verify real GPT2-style pretokenization does not merge across prompt boundary."""
    p=list(encode(context)); whole=list(encode(context+completion))
    if whole[:len(p)]!=p:raise InputRejected('TOKENIZER_CROSSES_PROMPT_BOUNDARY')
    suffix=whole[len(p):]
    if not (1<=len(p)<=224 and 1<=len(suffix)<=16 and len(whole)<=256):
        raise InputRejected(f'CONTEXT_OR_ANSWER_TOO_LONG p={len(p)} c={len(suffix)}')
    if any(type(t) is not int or not (0<=t<2048) for t in whole):raise InputRejected('TOKEN_OUTSIDE_BPE2048')
    return p,suffix

@torch.no_grad()
def mean_teacher_forced_logprob(model,encode,context:str,completion:str):
    p,c=length_and_prefix_check(encode,context,completion)
    model.eval()
    # Token after prefix token #i is evaluated at logits position i.
    x=torch.tensor([p+c[:-1]],dtype=torch.long,device='cpu')
    logits=model(x)
    if type(logits) in (tuple,list):logits=logits[0]
    assert logits.ndim==3 and logits.shape[:2]==x.shape and logits.shape[-1]==2048
    logp=F.log_softmax(logits[0,len(p)-1:len(p)-1+len(c)].float(),dim=-1)
    token=torch.tensor(c,dtype=torch.long)
    vals=logp.gather(1,token[:,None]).squeeze(1)
    if vals.numel()!=len(c) or not torch.isfinite(vals).all():raise RuntimeError('SCORER_NONFINITE')
    return float(vals.double().mean().item()),len(c)

@torch.no_grad()
def score_pair(model,encode,row):
    out={}
    for k,ctx in [('a',row['context_a']),('b',row['context_b'])]:
        for c,comp in [('x',row['completion_x']),('y',row['completion_y'])]:
            val,n=mean_teacher_forced_logprob(model,encode,ctx,comp)
            out['L_'+k+'_'+c]=val;out['len_'+k+'_'+c]=n
    out['margin_a']=out['L_a_x']-out['L_a_y']
    out['margin_b']=out['L_b_y']-out['L_b_x']
    out['both_positive']=out['margin_a']>0 and out['margin_b']>0
    out['contrast']=out['margin_a']+out['margin_b']
    return out

def validate_parent_checkpoint(cp_path:Path):
    if sha_file(cp_path)!=PARENT_SHA:raise InputRejected('FROZEN_PARENT_SHA_MISMATCH')
    cp=torch.load(cp_path,map_location='cpu',weights_only=True)
    if cp['step']!=1024 or cp['p02_git_blob']!=P02_GIT_BLOB or cp['config']!=P02_CONFIG:raise InputRejected('P02_SOURCE_OR_CONFIG_MISMATCH')
    return cp

def load_frozen_p02(p02_python_path:Path,cp_path:Path):
    import importlib.util,sys
    data=p02_python_path.read_bytes()
    if exact_git_blob(data)!=P02_GIT_BLOB:raise InputRejected('P02_GIT_BLOB_NOT_EXACT')
    spec=importlib.util.spec_from_file_location('cf1_p02_exact',p02_python_path)
    mod=importlib.util.module_from_spec(spec);sys.modules[spec.name]=mod;spec.loader.exec_module(mod)
    cp=validate_parent_checkpoint(cp_path)
    torch.set_num_threads(2)
    m=mod.GPT(mod.P02Config(**P02_CONFIG))
    m.load_state_dict(cp['model'],strict=True)
    if sum(v.numel() for v in m.parameters())!=3749376:raise InputRejected('PARAMETER_COUNT_CHANGED')
    m.to('cpu').eval()
    for p in m.parameters():p.requires_grad_(False)
    return m
