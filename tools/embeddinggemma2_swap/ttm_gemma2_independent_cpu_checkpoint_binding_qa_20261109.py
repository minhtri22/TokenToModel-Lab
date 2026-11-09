#!/usr/bin/env python3
"""Read-only CPU structural binding of frozen TTM/Gemma2 2048-step checkpoints.

Only forward passes on synthetic token IDs. NEVER opens TRAIN, VAL, TEST or the
new 320-story holdout. An independent structural replica is NOT proof of numeric
parity with the original GPU code. No weights or logits are exported.
"""
from __future__ import annotations
import argparse
import hashlib
import json
import math
import os
from pathlib import Path
os.environ['CUDA_VISIBLE_DEVICES'] = ''
import torch
from torch import nn
from torch.nn import functional as F

EXPECTED = {
 'A': ('ed7419f6421f4d82590c11ed8003b7df45aca9e86678ac2e1bdbeb62d8cd0081',45109595),
 'B': ('a4bb239a4952f2670966e6aacf89b10374ecce9ac2f4b8ba22003ed1589c024c',51402611),
 'C': ('ba04731f3d9f90a61e5d0819ca6f22a86775ff9784a94fe128128d205b7ca44d',52978949),
 'D': ('db5bebe2182d4f479028b260e0f70497d67d6f6dfac845d95708cb9c9f78f41e',52978949)
}
RUN = 'ttm_small4m_gemma2_directswap_2048x4096_t4_gpu_20261109_v1'
SOURCE = '1f3e01c6e1baf5fcab5d22e41b3c49d309b5dc5f8d2a4cf0fcf5c2fc45728ae6'
SCHEDULE = '81e4834f991607e8c3143bb67ed4a9ade93faa5f9526f630dc79e85bb0e51a52'
SCHEMA = 'ttm.gemma2.directswap2048.gpu.resumable.checkpoint.v1'


def require(cond, why):
    if not cond: raise RuntimeError('STOP_BIND_' + why)


def sha_file(p):
    h=hashlib.sha256()
    with p.open('rb') as f:
        for c in iter(lambda:f.read(1<<20),b''):h.update(c)
    return h.hexdigest()

class IndependentAttention(nn.Module):
    def __init__(self):
        super().__init__()
        self.heads=4
        self.head_dim=64
        self.qkv=nn.Linear(256,768)
        self.proj=nn.Linear(256,256)
    def forward(self,x):
        b,t,c=x.shape
        q,k,v=[chunk.reshape(b,t,4,64).transpose(1,2) for chunk in self.qkv(x).chunk(3,dim=-1)]
        scores=q@k.transpose(-2,-1)/math.sqrt(self.head_dim)
        mask=torch.ones(t,t,device=x.device,dtype=torch.bool).tril()
        weights=scores.masked_fill(~mask,-torch.inf).softmax(-1)
        out=weights@v
        return self.proj(out.transpose(1,2).contiguous().reshape(b,t,c))

class IndependentBlock(nn.Module):
    def __init__(self):
        super().__init__()
        self.ln1=nn.LayerNorm(256)
        self.attn=IndependentAttention()
        self.ln2=nn.LayerNorm(256)
        self.mlp=nn.Sequential(nn.Linear(256,1024),nn.GELU(),nn.Linear(1024,256))
    def forward(self,x):
        x=x+self.attn(self.ln1(x))
        return x+self.mlp(self.ln2(x))

class IndependentMappedInput(nn.Module):
    def __init__(self):
        super().__init__()
        self.register_buffer('valid',torch.zeros(2048,dtype=torch.bool))
        self.register_buffer('fallback',torch.zeros(2048,256))
        self.source=nn.Embedding(2048,512)
        self.proj=nn.Linear(512,256,bias=False)
    def forward(self,tokens):
        return torch.where(self.valid[tokens].unsqueeze(-1),
                           self.proj(self.source(tokens)),F.embedding(tokens,self.fallback))

class IndependentP02(nn.Module):
    def __init__(self,arm):
        super().__init__()
        self.tok=IndependentMappedInput() if arm in ('C','D') else nn.Embedding(2048,256)
        self.pos=nn.Embedding(256,256)
        self.blocks=nn.ModuleList([IndependentBlock() for _ in range(4)])
        self.final_ln=nn.LayerNorm(256)
        self.head=nn.Linear(256,2048,bias=False)
        if arm == 'A': self.head.weight=self.tok.weight
    def forward(self,tokens):
        require(tokens.dtype == torch.long and tokens.ndim==2 and tokens.device.type=='cpu','SYNTHETIC_INPUT_INVALID')
        b,t=tokens.shape
        require(b>0 and 0<t<=256 and bool(((tokens>=0)&(tokens<2048)).all()),'ID_OR_CONTEXT_RANGE')
        h=self.tok(tokens)+self.pos(torch.arange(t,device=tokens.device))[None,:,:]
        for layer in self.blocks: h=layer(h)
        return self.head(self.final_ln(h))

def payload_check(arm, payload):
    require(payload.get('schema')==SCHEMA and payload.get('run_id')==RUN and payload.get('arm')==arm,'CHECKPOINT_SCHEMA_RUN_ARM')
    require(payload.get('step')==2048 and payload.get('source_sha256')==SOURCE and payload.get('schedule_sha256')==SCHEDULE,'CKPT_SOURCE_STEP')
    require(isinstance(payload.get('model'),dict) and payload['model'],'CKPT_WEIGHTS')
    require(len(payload.get('train_losses',[]))==2048,'TRAIN_LOSS_METADATA_ONLY')
    require(isinstance(payload.get('optimizer'),dict) and payload['optimizer'].get('state'),'OPTIMIZER_PRESENT')
    require('torch_rng_cpu' in payload and 'torch_rng_cuda' in payload,'RNG_PRESENT')

def check_all(cp_dir):
    reports={}
    for arm in 'ABCD':
        cp=Path(cp_dir)/('checkpoint_'+arm+'.pt')
        expect,size=EXPECTED[arm]
        require(cp.is_file() and not cp.is_symlink() and cp.stat().st_size==size,'CHECKPOINT_FILE_'+arm)
        require(sha_file(cp)==expect,'CHECKPOINT_SHA256_'+arm)
        p=torch.load(cp,map_location='cpu',weights_only=True)
        payload_check(arm,p)
        model=IndependentP02(arm)
        model.load_state_dict(p['model'],strict=True)
        model.eval()
        if arm=='A':require(model.head.weight.data_ptr()==model.tok.weight.data_ptr(),'A_NOT_TIED')
        if arm=='B':require(model.head.weight.data_ptr()!=model.tok.weight.data_ptr(),'B_NOT_UNTIED')
        if arm in ('C','D'):
            require(model.tok.valid.dtype==torch.bool and model.tok.valid.numel()==2048,'DONOR_MASK')
            require(not bool(model.tok.valid[256]),'EOS_MUST_FALLBACK')
            require(torch.equal(model.tok(torch.tensor([256])),model.tok.fallback[[256]]),'EOS_FALLBACK_NUMERIC')
        tok=torch.tensor([[1,2,100,2047,42,256,30,15]],dtype=torch.long)
        with torch.inference_mode():
            logits=model(tok)
            shorter=model(tok[:,:4])
            require(logits.shape==(1,8,2048) and torch.isfinite(logits).all().item(),'FINITE_LOGITS_'+arm)
            delta=float((logits[:,:4]-shorter).abs().max().item())
            require(delta <= 2e-5,'CAUSAL_PREFIX_'+arm)
        reports[arm]={'sha256':expect,'strict_state_dict_load':'PASS','cpu_synthetic_forward':'PASS','shape':[1,8,2048],
                      'causal_prefix_max_abs':delta,
                      'unique_parameter_count':sum(w.numel() for w in model.parameters())}
        del model,p
    return {'schema':'ttm.gemma2.gpu2048.cpu_independent_structural_binding_qa.v1',
            'status':'PASS_SCOPED_CPU_SYNTHETIC_MODEL_BINDING','arms':reports,
            'gpu_used':False,'training_executed':False,'old_val_test_read':False,
            'new_holdout_scored':False,
            'limitations':['Independent structure not numeric parity with original GPU evaluator',
                           'Fixed synthetic token IDs only, not real validation, TEST or new holdout',
                           'Checkpoint binaries must remain private']}

def fixture():
    checks={}
    for arm in 'ABCD':
        model=IndependentP02(arm).eval()
        x=torch.tensor([[1,2,3,256]],dtype=torch.long)
        with torch.inference_mode():z=model(x)
        require(z.shape==(1,4,2048),'SHAPE')
        checks['construct_'+arm]='PASS'
    for arm in 'CD':
        m=IndependentMappedInput()
        with torch.no_grad():m.valid[1]=True
        x=m(torch.tensor([1,256],dtype=torch.long))
        require(x.shape==(2,256) and torch.allclose(x[1],m.fallback[256]),'MAPPED_FALLBACK')
        checks['mapped_'+arm]='PASS'
    return {'schema':'ttm.gemma2.cpu_binding.synthetic_qa.v1','status':'PASS','passed':len(checks),'checks':checks,
            'gpu_used':False,'model_scored':False,'holdout_read':False}

def main():
    ap=argparse.ArgumentParser()
    ap.add_argument('--mode',choices=('fixture-qa','checkpoint-qa'),required=True)
    ap.add_argument('--checkpoint-dir',default='')
    args=ap.parse_args()
    report=fixture() if args.mode=='fixture-qa' else check_all(args.checkpoint_dir)
    print(json.dumps(report,sort_keys=True,ensure_ascii=False))

if __name__=='__main__':main()
