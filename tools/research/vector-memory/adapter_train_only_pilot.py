#!/usr/bin/env python3
"""TTM train-only small adapter vs exact lookup -- exploratory, CPU, frozen P02.

Private inputs supplied locally; public output includes only aggregate statistics,
source hashes, train/VAL selection hashes, no actual token sequences or values.

A) Original P02. B) Exact external token lookup (bit exact).
C) Frozen P02 with learned context-vector adapter fitted only on TRAIN.
D) Same trained adapter with randomly shuffled TRAIN memory values.
E) Parameter-matched learned adapter without memory, fitted on TRAIN.
All logits use same original frozen Transformer blocks and tied head.
"""
from __future__ import annotations
import argparse, copy, hashlib, importlib.util, json, math, platform, sys, time
from pathlib import Path
import numpy as np
import torch
from torch import nn
from torch.nn import functional as F

CK='ee723407b2c25a18be20e26387a3dd8e4a18e2942d469279b6f0748ff86af0dc'
PACK='184f68b4c0c800ef3e98362c2e20e1cd35baa269e926489a475664526ecd9913'
SRC='9762343e06cf800b50574c2871ae1ed58537fb18'
SEED=20261111
BANK=512
FIT=512
VAL=128
K=4
TEMPERATURE=0.05
CONTEXT=64
STEPS=64
BATCH=16
LR=2e-3

def digest_file(p:Path):
    h=hashlib.sha256()
    with p.open('rb') as f:
        for b in iter(lambda:f.read(2**20),b''):h.update(b)
    return h.hexdigest()

def sha_tensor_ids(ids):return hashlib.sha256(','.join(map(str,ids.tolist())).encode()).hexdigest()

def select_unique(story_index, n, salt):
    first={}
    for i,story in enumerate(story_index):first.setdefault(int(story),i)
    keys=sorted(first, key=lambda s:hashlib.sha256(f'{salt}:{s}'.encode()).digest())
    assert n <= len(keys)
    return np.array([first[s] for s in keys[:n]],dtype=np.int64)

def load_rows(pack,prefix,idx):
    x=pack[prefix+'_x'][idx,:CONTEXT].astype(np.int64)
    count=np.minimum(pack[prefix+'_count'][idx].astype(np.int64),CONTEXT)
    pos=count-1
    y=pack[prefix+'_y'][idx,:CONTEXT].astype(np.int64)
    assert np.all(count>0) and np.all(x>=0) and np.all(x<2048)
    assert np.all(y[np.arange(len(idx)),pos]>=0)
    return torch.from_numpy(x),torch.from_numpy(pos),torch.from_numpy(y[np.arange(len(idx)),pos])

class Adapter(nn.Module):
    """Trains tiny MLP + one scalar. Backbone and tied table stay frozen."""
    def __init__(self,hidden=256, bottleneck=32):
        super().__init__()
        self.mlp=nn.Sequential(nn.Linear(hidden*2,bottleneck),nn.GELU(),nn.Linear(bottleneck,hidden))
        self.gate_logit=nn.Parameter(torch.tensor(-2.3))
    def forward(self,query,memory):
        q=F.layer_norm(query,(query.shape[-1],))
        m=F.layer_norm(memory,(memory.shape[-1],))
        return torch.sigmoid(self.gate_logit)*self.mlp(torch.cat((q,m),dim=-1))

def main():
    ap=argparse.ArgumentParser()
    ap.add_argument('--repo-root',type=Path,required=True)
    ap.add_argument('--checkpoint',type=Path,required=True)
    ap.add_argument('--private-pack',type=Path,required=True)
    ap.add_argument('--out',type=Path,required=True)
    args=ap.parse_args()
    torch.set_num_threads(2)
    torch.manual_seed(SEED)
    np.random.seed(SEED)
    torch.use_deterministic_algorithms(True)
    assert digest_file(args.checkpoint)==CK,'CHECKPOINT_SHA_MISMATCH'
    assert digest_file(args.private_pack)==PACK,'TRAIN_VAL_PACK_SHA_MISMATCH'
    source=args.repo_root/'tools/pilot_t4/integrated/p02_source_exact.py'
    bb=source.read_bytes();blob=hashlib.sha1(b'blob '+str(len(bb)).encode()+b'\0'+bb).hexdigest()
    assert blob==SRC,'P02_GIT_BLOB_MISMATCH'
    spec=importlib.util.spec_from_file_location('ttm_frozen_p02',source)
    mod=importlib.util.module_from_spec(spec);sys.modules[spec.name]=mod;spec.loader.exec_module(mod)
    checkpoint=torch.load(args.checkpoint,map_location='cpu',weights_only=True)
    assert checkpoint['step']==1280 and checkpoint['p02_git_blob']==SRC and checkpoint['train_pack_sha256']==PACK
    model=mod.GPT(mod.P02Config(**checkpoint['config'])).eval().cpu()
    model.load_state_dict(checkpoint['model'],strict=True)
    for p in model.parameters():p.requires_grad_(False)
    assert model.head.weight.data_ptr()==model.tok.weight.data_ptr()
    frozen_copy=[p.detach().clone() for p in model.parameters()]
    table=model.tok.weight.detach().clone()
    pack=np.load(args.private_pack,allow_pickle=False)
    bank_i=select_unique(pack['train_story_index'],BANK+FIT,'TTM_ADAPTER20261111_TRAIN')
    mem_i,fit_i=bank_i[:BANK],bank_i[BANK:]
    val_i=select_unique(pack['val_story_index'],VAL,'VAL20261111')
    assert not set(map(int,pack['train_story_index'][mem_i])) & set(map(int,pack['train_story_index'][fit_i]))
    bx,bp,by=load_rows(pack,'train',mem_i)
    tx,tp,ty=load_rows(pack,'train',fit_i)
    vx,vp,vy=load_rows(pack,'val',val_i)

    def frozen_hidden_emb(emb):
        z=emb+model.pos(torch.arange(emb.shape[1]))[None,:,:]
        for block in model.blocks:z=block(z)
        return model.final_ln(z)
    def frozen_hidden(x):
        return frozen_hidden_emb(model.tok(x))
    def contextual(xs,ps):
        out=[]
        with torch.no_grad():
            for i in range(0,len(xs),16):
                z=frozen_hidden(xs[i:i+16]);out.append(z[torch.arange(len(z)),ps[i:i+16]])
        return torch.cat(out)

    t0=time.time()
    bank_keys=F.normalize(contextual(bx,bp),dim=1)
    bank_values=table[by]
    fit_queries=contextual(tx,tp)
    val_queries=contextual(vx,vp)
    val_distinct_stories=int(len(set(map(int,pack['val_story_index'][val_i]))))
    g=torch.Generator().manual_seed(919198)
    shuffled_values=bank_values[torch.randperm(BANK,generator=g)]
    def retrieve(q,values):
        score,idx=(F.normalize(q,dim=1)@bank_keys.T).topk(K,dim=1)
        weights=F.softmax(score/TEMPERATURE,dim=-1)
        return (weights.unsqueeze(-1)*values[idx]).sum(dim=1),idx
    fit_mem,fit_hits=retrieve(fit_queries,bank_values)
    val_mem,val_hits=retrieve(val_queries,bank_values)
    val_shuffle,_=retrieve(val_queries,shuffled_values)
    assert fit_mem.shape==(FIT,256) and val_mem.shape==(VAL,256)
    assert len(set(mem_i.tolist()+fit_i.tolist()))==BANK+FIT
    del bx,bp

    def model_with_adapter(inputs,positions,query,memory,adapter):
        z=model.tok(inputs).clone()
        delta=adapter(query,memory)
        z[torch.arange(len(z)),positions] = z[torch.arange(len(z)),positions]+delta
        hidden=z+model.pos(torch.arange(inputs.shape[1]))[None,:,:]
        for block in model.blocks:hidden=block(hidden)
        final=model.final_ln(hidden)[torch.arange(len(hidden)),positions]
        return F.linear(final,model.head.weight)

    def fit_adapter(use_memory):
        # Exactly equal init/optimizer/sampling across memory / parameter-matched no-memory.
        torch.manual_seed(SEED+77)
        adapt=Adapter()
        optimizer=torch.optim.AdamW(adapt.parameters(),lr=LR,weight_decay=0.0)
        order=torch.randperm(FIT,generator=torch.Generator().manual_seed(SEED+91))
        losses=[]
        for s in range(STEPS):
            offset=(s%(FIT//BATCH))*BATCH
            ids=order[offset:offset+BATCH]
            optimizer.zero_grad(set_to_none=True)
            vm=fit_mem[ids] if use_memory else torch.zeros_like(fit_mem[ids])
            logits=model_with_adapter(tx[ids],tp[ids],fit_queries[ids],vm,adapt)
            loss=F.cross_entropy(logits,ty[ids]);loss.backward()
            torch.nn.utils.clip_grad_norm_(adapt.parameters(),1.0)
            optimizer.step()
            losses.append(float(loss.detach()))
            if (s+1)%16==0:
                print(f'ARM={"MEM" if use_memory else "NO_MEM"} STEP={s+1}/{STEPS} LOSS={losses[-1]:.5f}',flush=True)
        return adapt, {'train_loss_first16':float(np.mean(losses[:16])),
                       'train_loss_last16':float(np.mean(losses[-16:])),
                       'num_trainable_parameters':sum(p.numel() for p in adapt.parameters()),
                       'optimizer_steps':STEPS,'batch_size':BATCH}

    mem_adapter,mem_training=fit_adapter(True)
    nomem_adapter,nomem_training=fit_adapter(False)
    mem_adapter.eval();nomem_adapter.eval()

    with torch.no_grad():
        arrays={k:[] for k in ['A_original','B_exact','C_memory_adapter','D_shuffled_memory','E_no_memory_adapter']}
        for i in range(0,VAL,8):
            xs=vx[i:i+8];ps=vp[i:i+8]; q=val_queries[i:i+8]; mm=val_mem[i:i+8]
            base=model(xs)[0][torch.arange(len(xs)),ps]
            # Explicit external lookup of every token via torch tensor row indexing.
            out=F.linear(frozen_hidden_emb(table[xs])[torch.arange(len(xs)),ps],table)
            assert torch.equal(base,out),'EXACT_EXTERNAL_LOOKUP_LOGITS_MISMATCH'
            arrays['A_original'].append(base)
            arrays['B_exact'].append(out)
            arrays['C_memory_adapter'].append(model_with_adapter(xs,ps,q,mm,mem_adapter))
            arrays['D_shuffled_memory'].append(model_with_adapter(xs,ps,q,val_shuffle[i:i+8],mem_adapter))
            arrays['E_no_memory_adapter'].append(model_with_adapter(xs,ps,q,torch.zeros_like(mm),nomem_adapter))
        arrays={k:torch.cat(v,dim=0) for k,v in arrays.items()}
        losses={k:F.cross_entropy(v,vy,reduction='none') for k,v in arrays.items()}
        def stats(k):
            ll=losses[k];a=arrays[k]
            return {'nll_nats':float(ll.mean()),'ppl':float(torch.exp(ll.mean())),
                    'top1_accuracy':float((a.argmax(-1)==vy).float().mean()),
                    'top1_agreement_with_original':float((a.argmax(-1)==arrays['A_original'].argmax(-1)).float().mean()),
                    'n_val_targets':len(vy)}
        arms={k:stats(k) for k in arrays}
        nlls={k:float(v.mean()) for k,v in losses.items()}
        # Paired story bootstrap under frozen ordering (uncertainty descriptive only).
        delta=(losses['A_original']-losses['C_memory_adapter']).numpy()
        rnd=np.random.default_rng(SEED+202)
        sample=rnd.integers(0,VAL,size=(1000,VAL))
        ci=np.quantile(delta[sample].mean(axis=1),[.025,.975]).tolist()
        gain= nlls['A_original']-nlls['C_memory_adapter']
        good= (nlls['C_memory_adapter']<nlls['A_original']-1e-4 and
               nlls['C_memory_adapter']<nlls['D_shuffled_memory']-1e-4 and
               nlls['C_memory_adapter']<nlls['E_no_memory_adapter']-1e-4)
        verdict='YES_SCOPED_EXPLORATORY' if good else 'NO_SCOPED_EXPLORATORY'
        result={
            'experiment':'TTM_VECTOR_MEMORY_TRAIN_ONLY_ADAPTER_VS_EXACT_LOOKUP_SMALL_PILOT',
            'scope':'CPU_EXPLORATORY_NOT_CONFIRMATORY; one fixed VAL subset used for final and deterministic replay; no TEST',
            'verdict':verdict,
            'criterion':'C_memory_adapter NLL strictly lower than A_original,D_shuffled_memory,E_no_memory_adapter by >1e-4 (post hoc exploratory screening, not significance)',
            'environment':{'python':platform.python_version(),'torch':torch.__version__,'device':'cpu','threads':torch.get_num_threads()},
            'sources':{'checkpoint_sha256':CK,'checkpoint_step':1280,'pack_sha256':PACK,'p02_source_git_blob':SRC,
                       'training':'TinyStories TRAIN only; no TEST used; raw stories and reversible token windows not exported'},
            'design':{'seed':SEED,'retrieval':'cosine top-k on frozen original P02 hidden of observed prefix only',
                      'memory_bank':BANK,'train_adapter':FIT,'val_stories':VAL,'val_unique_stories':val_distinct_stories,
                      'context':CONTEXT,'k':K,'temperature':TEMPERATURE,'bank_values':'TRAIN next-token embedding',
                      'retrieved_from_val':False,'bank_training_overlap_story_count':0,
                      'bank_selection_index_sha256':sha_tensor_ids(mem_i),
                      'fit_selection_index_sha256':sha_tensor_ids(fit_i),
                      'val_selection_index_sha256':sha_tensor_ids(val_i),
                      'adapter':'joint [query-hidden, memory] 512->32->256 residual at last observed token embedding before all 4 frozen Attention/MLP blocks',
                      'adapter_lr':LR,'adapter_steps':STEPS,'adapter_batch':BATCH,
                      'backbone_frozen':True,
                      'control_E':'same parameter-count adapter trained on TRAIN with no memory',
                      'control_D':'trained memory adapter fed permuted TRAIN memory values at VAL'},
            'training':{'C_memory_adapter':mem_training,'E_no_memory_adapter':nomem_training},
            'arms':arms,
            'comparisons':{'A_B_bit_exact_logits':bool(torch.equal(arrays['A_original'],arrays['B_exact'])),
                           'C_minus_A_nll':nlls['C_memory_adapter']-nlls['A_original'],
                           'C_minus_D_nll':nlls['C_memory_adapter']-nlls['D_shuffled_memory'],
                           'C_minus_E_nll':nlls['C_memory_adapter']-nlls['E_no_memory_adapter'],
                           'A_minus_C_mean_gain':gain,
                           'A_minus_C_paired_story_bootstrap_95pct_interval':ci,
                           'retrieved_next_token_top1_hit_rate':float((by[val_hits[:,0]]==vy).float().mean())},
            'integrity':{'checkpoint_frozen_unchanged':all(torch.equal(a,b) for a,b in zip(model.parameters(),frozen_copy)),
                         'A_B_bit_exact':bool(torch.equal(arrays['A_original'],arrays['B_exact'])),
                         'train_bank_disjoint':True,'val_targets_excluded_from_training':True,'test_not_accessed':True},
            'limitations':['Single small sample one prediction per story, context len 64','No semantic guarantees for frozen hidden cosine nearest neighbor',
                           'Training-only adapter and no-memory comparison controls are small; exact externalization does not imply knowledge removed globally',
                           'TinyStories source distribution; no unseen-domain/OOD evaluation',
                           'VAL selection used for evaluation only; this is exploratory, no formal confirmation or architecture adoption']}
        assert all(result['integrity'].values()),'INTEGRITY_GATE_FAILED'
        args.out.parent.mkdir(parents=True,exist_ok=True)
        args.out.write_text(json.dumps(result,ensure_ascii=False,indent=2,sort_keys=True)+'\n',encoding='utf-8')
        print(json.dumps({'verdict':verdict,'arms':arms,'comparisons':result['comparisons'],'elapsed_s':round(time.time()-t0,2)},indent=2),flush=True)

if __name__=='__main__':main()
