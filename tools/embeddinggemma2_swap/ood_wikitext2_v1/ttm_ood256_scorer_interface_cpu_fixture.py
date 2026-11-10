#!/usr/bin/env python3
"""OOD256 scorer interface: precomputed-logit-only fixture, no model.forward or private data.

Separated from the frozen SEMANTIC4X3 H768 scorer. It does not load a model,
perform inference, modify checkpoints, score OOD real text, or create a CLAIM.
"""
from __future__ import annotations
import argparse
import math
import numpy as np
import torch
from torch.nn import functional as F

STUDY_ID = 'ttm_gemma2_semantic4x3_3seed_2048x4096_h768_20261110_v2'
ARMS = ('PT-REAL','PT-PERM','NULL-REAL','NULL-PERM')
SEEDS = ('S1','S2','S3')
N_DOC=256
N_WINDOWS=512
CONTEXT=256
VOCAB=2048
TARGETS=131072

def insist(condition, code):
    if not bool(condition): raise RuntimeError('HOLD_OOD_PREEXEC_'+code)

def validate_windows(x, y, story_index, counts):
    x=np.asarray(x);y=np.asarray(y);story_index=np.asarray(story_index);counts=np.asarray(counts)
    insist(x.shape==y.shape==(N_WINDOWS,CONTEXT),'WINDOW_SHAPE')
    insist(story_index.shape==counts.shape==(N_WINDOWS,),'METADATA_SHAPE')
    insist(x.dtype.kind in 'iu' and y.dtype.kind in 'iu','WINDOW_DTYPE')
    insist((x>=0).all() and (x<VOCAB).all() and (y>=0).all() and (y<VOCAB).all(),'TOKEN_RANGE')
    insist((counts==CONTEXT).all() and int(counts.sum())==TARGETS,'TARGET_COUNT')
    insist(np.array_equal(story_index,np.repeat(np.arange(N_DOC),2)),'DOCUMENT_ORDER')
    insist(np.array_equal(x[:,1:],y[:,:-1]),'SHIFT_WITHIN_WINDOW')
    insist(np.array_equal(y[::2,-1],x[1::2,0]),'SHIFT_BETWEEN_WINDOWS')
    return True

def score_precomputed_logits(logits,targets,doc_indices):
    """Consumes logits already supplied by a separately authorized scorer.

    Never invokes a model, never reads a checkpoint, does not produce OOD NLL
    by itself. The fixture supplies synthetic uniform logits only.
    """
    insist(isinstance(logits,torch.Tensor) and logits.ndim==3,'LOGIT_TENSOR')
    b,t,v=logits.shape
    insist(t==CONTEXT and v==VOCAB and b>0,'LOGIT_SHAPE')
    insist(logits.dtype in (torch.float32,torch.float64),'LOGIT_DTYPE')
    insist(logits.device.type=='cpu','FIXTURE_CPU_ONLY')
    insist(torch.isfinite(logits).all().item(),'NONFINITE_LOGITS')
    targets=torch.as_tensor(targets,dtype=torch.int64,device='cpu')
    doc_indices=np.asarray(doc_indices)
    insist(targets.shape==(b,CONTEXT),'TARGET_BATCH_SHAPE')
    insist(doc_indices.shape==(b,) and np.issubdtype(doc_indices.dtype,np.integer),'DOC_BATCH_INDEX_SHAPE')
    insist(((targets>=0)&(targets<VOCAB)).all().item(),'TARGET_RANGE')
    insist((doc_indices>=0).all() and (doc_indices<N_DOC).all(),'DOC_INDEX_RANGE')
    loss=F.cross_entropy(logits.float().reshape(-1,VOCAB),targets.reshape(-1),reduction='none')
    out=np.zeros(N_DOC,dtype=np.float64)
    np.add.at(out,doc_indices,loss.reshape(b,CONTEXT).sum(axis=1,dtype=torch.float64).cpu().numpy())
    return out

def validate_ckpt_header(ck, seed, arm):
    insist(ck.get('schema')=='ttm.semantic4x3.checkpoint.v1','CK_SCHEMA')
    insist(ck.get('study_id')==STUDY_ID and ck.get('seed')==seed and ck.get('arm')==arm,'CK_STUDY_SEED_ARM')
    insist(ck.get('step')==2048 and ck.get('sampler_cursor')==2048,'CK_STEP')
    state=ck.get('model')
    insist(isinstance(state,dict) and len(state)==56,'CK_STATE_COUNT')
    required={
      'tok.valid':(2048,), 'tok.fallback':(2048,256),
      'tok.source.weight':(2048,512),'tok.proj.weight':(256,512),
      'pos.weight':(256,256),'head.weight':(2048,256)
    }
    for name,shape in required.items():
        insist(name in state and tuple(state[name].shape)==shape,'CK_LAYOUT_'+name)
    return True

def fixture():
    # 256 documents * 2 windows, all labels precomputed synthetic.
    x=np.zeros((N_WINDOWS,CONTEXT),dtype=np.int16)
    y=np.zeros_like(x)
    for d in range(N_DOC):
        # All content is synthetic, no link to TinyStories or WikiText.
        seq=(np.arange(513,dtype=np.int64)+d)%VOCAB
        x[2*d,:]=seq[:256];y[2*d,:]=seq[1:257]
        x[2*d+1,:]=seq[256:512];y[2*d+1,:]=seq[257:513]
    idx=np.repeat(np.arange(N_DOC,dtype=np.int32),2)
    counts=np.full(N_WINDOWS,CONTEXT,dtype=np.int16)
    assert validate_windows(x,y,idx,counts)
    # Two small batches are sufficient to verify the aggregation interface.
    logits=torch.zeros((2,CONTEXT,VOCAB),dtype=torch.float32)
    got=score_precomputed_logits(logits,y[:2],idx[:2])
    insist(abs(got[0]-512*math.log(VOCAB))<1e-3,'UNIFORM_LOGIT_NLL')
    insist(np.count_nonzero(got)==1,'PER_DOCUMENT_AGGREGATION')
    bad=y.copy();bad[0,0]=VOCAB
    def rejects(fn):
        try:fn();return False
        except RuntimeError as exc:return 'HOLD_OOD_PREEXEC_' in str(exc)
    insist(rejects(lambda:validate_windows(x,bad,idx,counts)),'BAD_TOKEN_REJECTION')
    insist(rejects(lambda:score_precomputed_logits(torch.zeros((2,255,VOCAB)),y[:2],idx[:2])),'BAD_LOGIT_SHAPE_REJECTION')
    insist(rejects(lambda:score_precomputed_logits(torch.full((2,CONTEXT,VOCAB),float('nan')),y[:2],idx[:2])),'NAN_LOGIT_REJECTION')
    insist(rejects(lambda:validate_windows(x,y,idx[::-1],counts)),'DOCUMENT_ORDER_REJECTION')
    print('TTM_GEMMA2_OOD_SCORER_INTERFACE_CPU_FIXTURE=PASS_6')
    print('TTM_GEMMA2_OOD_FIXTURE=PRECOMPUTED_SYNTHETIC_LOGITS_ONLY; MODEL_FORWARD=0; OOD_NLL=NOT_EXECUTED')
    return True

if __name__=='__main__':
    p=argparse.ArgumentParser()
    p.add_argument('--mode',choices=['fixture'],required=True)
    p.parse_args()
    fixture()
