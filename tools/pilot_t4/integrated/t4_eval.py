#!/usr/bin/env python3
"""TTM T4 H1 prereg: train-fitted unigram/bigram; VAL-only story bootstrap.

No TEST read, no fitting on VALIDATION, no hyperparam selection from TEST.
"""
from __future__ import annotations
import hashlib, json
from pathlib import Path
import numpy as np
import torch
from torch.nn import functional as F

VOCAB=2048
ALPHA=.1
BOOT_SEED=20261109
N_BOOT=1000


def load_private_pack(data_path,manifest_path):
    m=json.loads(Path(manifest_path).read_text('utf-8'))
    if m['schema']!='ttm.t4.private.train_val.windowpack.v1' or m['contains_test'] or not m['contains_reversible_train_val_tokens']:
        raise RuntimeError('PRIVATE_PACK_SCHEMA_OR_TEST_VIOLATION')
    h=hashlib.sha256()
    with open(data_path,'rb') as f:
        for b in iter(lambda:f.read(1<<20),b''):h.update(b)
    if h.hexdigest()!=m['npz_sha256']:raise RuntimeError('TRAIN_VAL_PACK_SHA_MISMATCH')
    data=np.load(data_path,allow_pickle=False)
    expected={f'{p}_{s}' for p in ['train','val'] for s in ['x','y','count','story_index']}
    if set(data.files)!=expected:raise RuntimeError('UNEXPECTED_DATASET_KEYS_TEST_EXPOSURE')
    for prefix in ['train','val']:
        x,y,c,si=[data[f'{prefix}_{suffix}'] for suffix in ['x','y','count','story_index']]
        if x.shape!=y.shape or x.ndim!=2 or x.shape[1]!=256 or c.shape!=(len(x),) or si.shape!=(len(x),):
            raise RuntimeError('WINDOW_PACK_SHAPE_INVALID')
        mask=np.arange(256)[None,:]<c[:,None]
        if not(np.all(y[~mask]==-100) and np.all((y[mask]>=0)&(y[mask]<VOCAB)) and np.all((x>=0)&(x<VOCAB))):
            raise RuntimeError('PRIVATE_PACK_MASK_OR_TOKEN_INVALID')
        expected_count=m['counts']['train_next_token_targets_unique' if prefix=='train' else 'val_next_token_targets']
        if int(c.sum())!=expected_count:raise RuntimeError('TARGET_COUNT_MANIFEST_MISMATCH')
        if np.max(si)+1!=m['counts'][f'{prefix}_stories']:raise RuntimeError('STORY_IDS_OR_COUNT_INVALID')
    return data,m


def fit_baselines(train_x,train_y):
    # Every source TRAIN pair is counted once; sampling frequency of model training is not part of baseline.
    mask=train_y!=-100
    prev=train_x[mask].astype(np.int64)
    nxt=train_y[mask].astype(np.int64)
    counts=np.zeros((VOCAB,VOCAB),dtype=np.int64)
    np.add.at(counts,(prev,nxt),1)
    unigrams=counts.sum(axis=0).astype(np.float64)
    smooth_unigrams=(unigrams+ALPHA)/(float(unigrams.sum())+ALPHA*VOCAB)
    denom=counts.sum(axis=1).astype(np.float64)+ALPHA*VOCAB
    logbig=np.log((counts.astype(np.float64)+ALPHA)/denom[:,None])
    loguni=np.log(smooth_unigrams)
    return loguni,logbig


def baseline_story_scores(data,loguni,logbig):
    x,y,c,si=[data['val_'+z] for z in ['x','y','count','story_index']]
    n=int(np.max(si))+1
    target_counts=np.zeros(n,dtype=np.int64)
    uni_sum=np.zeros(n,dtype=np.float64);bi_sum=np.zeros(n,dtype=np.float64)
    for j in range(len(x)):
        k=int(c[j]);s=int(si[j]);prev=x[j,:k].astype(np.int64);nxt=y[j,:k].astype(np.int64)
        target_counts[s]+=k
        uni_sum[s]-=np.sum(loguni[nxt])
        bi_sum[s]-=np.sum(logbig[prev,nxt])
    if np.any(target_counts==0):raise RuntimeError('VAL_STORY_WITH_NO_SCORE')
    return target_counts,uni_sum,bi_sum

@torch.no_grad()
def model_story_scores(model,data,device,eval_batch=4):
    x,y,c,si=[data['val_'+z] for z in ['x','y','count','story_index']]
    n=int(np.max(si))+1
    result=np.zeros(n,dtype=np.float64)
    old=model.training
    model.eval()
    try:
        for a in range(0,len(x),eval_batch):
            b=min(a+eval_batch,len(x))
            xx=torch.as_tensor(x[a:b].astype(np.int64),device=device)
            yy=torch.as_tensor(y[a:b].astype(np.int64),device=device)
            logits,_=model(xx)
            loss=F.cross_entropy(logits.float().reshape(-1,VOCAB), yy.reshape(-1),ignore_index=-100,reduction='none')
            loss=loss.reshape(b-a,256).sum(1).double().cpu().numpy()
            for j,k in enumerate(range(a,b)):result[int(si[k])]+=float(loss[j])
    finally:
        model.train(old)
    return result


def decide_h1(model_sums,bigram_sums,token_counts,*,seed=BOOT_SEED,boot=N_BOOT):
    model_sums=np.asarray(model_sums,dtype=np.float64)
    bigram_sums=np.asarray(bigram_sums,dtype=np.float64)
    token_counts=np.asarray(token_counts,dtype=np.int64)
    if not(len(model_sums)==len(bigram_sums)==len(token_counts)) or np.any(token_counts<=0):
        raise RuntimeError('BOOTSTRAP_STORY_COUNT_INVALID')
    mnll=model_sums.sum()/token_counts.sum();bnll=bigram_sums.sum()/token_counts.sum()
    effect=(bnll-mnll)/bnll
    rng=np.random.default_rng(seed)
    gaps=[]
    for _ in range(boot):
        take=rng.integers(0,len(token_counts),size=len(token_counts),dtype=np.int64)
        gaps.append(float((bigram_sums[take].sum()-model_sums[take].sum())/token_counts[take].sum()))
    lo,hi=[float(x) for x in np.quantile(gaps,[.025,.975])]
    return {'schema':'ttm.t4.h1.val.storybootstrap.v1',
       'primary_model_val_nll':float(mnll),'primary_bigram_val_nll':float(bnll),
       'relative_nll_improvement':float(effect),'absolute_nll_gain':float(bnll-mnll),
       'bootstrap_95pct_gain_ci':[lo,hi],'bootstrap_stories':len(token_counts),
       'bootstrap_rounds':boot,'bootstrap_seed':seed,'alpha':ALPHA,
       'scored_val_targets':int(token_counts.sum()),
       'h1_pass':bool(effect>=.05 and lo>0),
       'warning':'VALIDATION-only technical computation; must be frozen before T4; TEST sealed'}
