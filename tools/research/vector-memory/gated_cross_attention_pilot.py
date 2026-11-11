#!/usr/bin/env python3
"""TTM exploration: frozen GPT, old adapter, gated top-k cross attention.

Trains only on TRAIN, keeps exact checkpoint frozen. Primary assessment: unseen
(to adapters/bank) TRAIN stories. Historical VAL stories are secondary, already
examined in prior experiments; NOT an independent confirmatory test. No TEST.
"""
from __future__ import annotations
import argparse, hashlib, importlib.util, json, math, platform, sys, time
from pathlib import Path
import numpy as np
import torch
from torch import nn
from torch.nn import functional as F

SEED=20261111
CK='ee723407b2c25a18be20e26387a3dd8e4a18e2942d469279b6f0748ff86af0dc'
PACK='184f68b4c0c800ef3e98362c2e20e1cd35baa269e926489a475664526ecd9913'
SRC='9762343e06cf800b50574c2871ae1ed58537fb18'
BANK,FIT,HOLD,VAL=512,512,256,256
K,CONTEXT,STEPS,BATCH=4,64,64,16
LR=2e-3

def hashfile(path):
    h=hashlib.sha256()
    with open(path,'rb') as f:
        for b in iter(lambda:f.read(1<<20),b''):h.update(b)
    return h.hexdigest()

def shaids(idx):return hashlib.sha256(','.join(map(str,idx.tolist())).encode()).hexdigest()
def select_unique(story_index,n,salt):
    first={}
    for i,s in enumerate(story_index):first.setdefault(int(s),i)
    keys=sorted(first,key=lambda s:hashlib.sha256(f'{salt}:{s}'.encode()).digest())
    assert len(keys)>=n
    return np.asarray([first[s] for s in keys[:n]],dtype=np.int64)
def load_rows(pack,prefix,indices):
    x=pack[prefix+'_x'][indices,:CONTEXT].astype(np.int64)
    count=np.minimum(pack[prefix+'_count'][indices].astype(np.int64),CONTEXT)
    p=count-1
    y=pack[prefix+'_y'][indices,:CONTEXT].astype(np.int64)
    assert np.all(p>=0) and np.all(x>=0) and np.all(x<2048)
    assert np.all(y[np.arange(len(indices)),p]>=0)
    return torch.from_numpy(x),torch.from_numpy(p),torch.from_numpy(y[np.arange(len(indices)),p])

class OldAdapter(nn.Module):
    def __init__(self):
        super().__init__()
        self.mlp=nn.Sequential(nn.Linear(512,32),nn.GELU(),nn.Linear(32,256))
        self.gate_logit=nn.Parameter(torch.tensor(-2.3))
    def forward(self,q,m):
        return torch.sigmoid(self.gate_logit)*self.mlp(torch.cat([F.layer_norm(q,(256,)),F.layer_norm(m,(256,))],dim=-1))

class GatedCrossAttention(nn.Module):
    """Memory-reader after frozen P02; zero-initialized output is exact bypass."""
    def __init__(self):
        super().__init__()
        self.qproj=nn.Linear(256,64,bias=False)
        self.kproj=nn.Linear(256,64,bias=False)
        self.vproj=nn.Linear(256,128,bias=False)
        self.oproj=nn.Linear(128,256,bias=False)
        nn.init.zeros_(self.oproj.weight)
        self.gate=nn.Sequential(nn.Linear(256+128+3,32),nn.GELU(),nn.Linear(32,1))
        nn.init.zeros_(self.gate[-1].weight)
        nn.init.constant_(self.gate[-1].bias,-4.0)
    def forward(self,q,neighbor_keys,neighbor_values,cosine):
        qn=F.layer_norm(q,(256,))
        kn=F.layer_norm(neighbor_keys,(256,))
        qp=self.qproj(qn).unsqueeze(1)
        kp=self.kproj(kn)
        logits=(qp*kp).sum(-1)/8.0 + cosine/0.05
        a=logits.softmax(-1)
        read=(a.unsqueeze(-1)*self.vproj(neighbor_values)).sum(1)
        entropy=-(a*a.clamp_min(1e-12).log()).sum(-1,keepdim=True)
        margin=(cosine[:,0]-cosine[:,1]).unsqueeze(1)
        confidence=torch.cat([cosine[:,0:1],margin,entropy],dim=-1)
        gate=torch.sigmoid(self.gate(torch.cat([qn,read,confidence],dim=-1)))
        delta=gate*self.oproj(read)
        return delta,gate

def main():
    ap=argparse.ArgumentParser()
    ap.add_argument('--checkpoint',type=Path,required=True)
    ap.add_argument('--private-pack',type=Path,required=True)
    ap.add_argument('--source',type=Path,required=True,help='Validated module exposing OriginalP02GPT (math matches P02 Git blob)')
    ap.add_argument('--out',type=Path,required=True)
    args=ap.parse_args()
    torch.set_num_threads(2)
    torch.manual_seed(SEED)
    np.random.seed(SEED)
    torch.use_deterministic_algorithms(True)
    assert hashfile(args.checkpoint)==CK
    assert hashfile(args.private_pack)==PACK
    spec=importlib.util.spec_from_file_location('ttm_p02_equivalent',args.source)
    mod=importlib.util.module_from_spec(spec);sys.modules[spec.name]=mod;spec.loader.exec_module(mod)
    ck=torch.load(args.checkpoint,map_location='cpu',weights_only=True)
    assert ck['step']==1280 and ck['p02_git_blob']==SRC and ck['train_pack_sha256']==PACK
    model=mod.OriginalP02GPT(ck['config']).cpu().eval()
    model.load_state_dict(ck['model'],strict=True)
    model.requires_grad_(False)
    table=model.tok.weight.detach()
    assert model.head.weight.data_ptr()==model.tok.weight.data_ptr()
    before={k:v.detach().clone() for k,v in model.state_dict().items()}
    pack=np.load(args.private_pack,allow_pickle=False)
    ids=select_unique(pack['train_story_index'],BANK+FIT,'TTM_ADAPTER20261111_TRAIN')
    bank_idx,fit_idx=ids[:BANK],ids[BANK:]
    all_unique=select_unique(pack['train_story_index'],2048,'TTM_GATED20261111_HOLDOUT')
    held_idx=np.asarray([i for i in all_unique if int(pack['train_story_index'][i]) not in set(map(int,pack['train_story_index'][ids]))][:HOLD],dtype=np.int64)
    assert len(held_idx)==HOLD
    val_idx=select_unique(pack['val_story_index'],VAL,'VAL20261111')
    bx,bp,by=load_rows(pack,'train',bank_idx)
    tx,tp,ty=load_rows(pack,'train',fit_idx)
    hx,hp,hy=load_rows(pack,'train',held_idx)
    vx,vp,vy=load_rows(pack,'val',val_idx)
    assert not set(map(int,pack['train_story_index'][held_idx])) & set(map(int,pack['train_story_index'][ids]))
    assert shaids(bank_idx)=='4b8546f6d9c22df481d4b9be6a9e0d97691179bde21cb48d38e44e580eb60922'
    assert shaids(val_idx[:128])=='fb9d072fbb817cc8cc5a90367f2175d7b789d29a2140a660fbf2803332fa584f'
    started=time.monotonic()

    def forward_hidden(x, external_table=None):
        vectors=model.tok(x) if external_table is None else external_table[x]
        z=vectors+model.pos(torch.arange(x.shape[1]))[None,:,:]
        for block in model.blocks:z=block(z)
        return model.final_ln(z)
    @torch.no_grad()
    def features(xs,pos):
        ys=[]
        for off in range(0,len(xs),16):
            p=pos[off:off+16]
            h=forward_hidden(xs[off:off+16])
            ys.append(h[torch.arange(len(p)),p])
        return torch.cat(ys)
    qbank=features(bx,bp); qfit=features(tx,tp); qheld=features(hx,hp); qval=features(vx,vp)
    bank_keys=F.normalize(qbank,dim=-1)
    bank_vals=table[by].detach()
    random_perm=torch.randperm(BANK,generator=torch.Generator().manual_seed(919198))
    bank_shuffled=bank_vals[random_perm]

    @torch.no_grad()
    def retrieval(query):
        scores,idx=(F.normalize(query,dim=-1) @ bank_keys.T).topk(K,dim=-1)
        weights=F.softmax(scores/.05,dim=-1)
        mean=(weights.unsqueeze(-1)*bank_vals[idx]).sum(1)
        return idx,scores,mean
    fit_ix,fit_sim,fit_mean=retrieval(qfit)
    held_ix,held_sim,held_mean=retrieval(qheld)
    val_ix,val_sim,val_mean=retrieval(qval)

    def old_forward(xs,ps,q,m,adapter):
        z=model.tok(xs).clone()
        ix=torch.arange(len(xs))
        z[ix,ps]=z[ix,ps]+adapter(q,m)
        h=z+model.pos(torch.arange(z.shape[1]))[None,:,:]
        for block in model.blocks:h=block(h)
        h=model.final_ln(h)[ix,ps]
        return F.linear(h,table)

    torch.manual_seed(SEED+77)
    old=OldAdapter()
    old_optim=torch.optim.AdamW(old.parameters(),lr=LR,weight_decay=0.0)
    order=torch.randperm(FIT,generator=torch.Generator().manual_seed(SEED+91))
    history_old=[]
    for step in range(STEPS):
        offset=(step%(FIT//BATCH))*BATCH; ids_batch=order[offset:offset+BATCH]
        old_optim.zero_grad(set_to_none=True)
        logits=old_forward(tx[ids_batch],tp[ids_batch],qfit[ids_batch],fit_mean[ids_batch],old)
        loss=F.cross_entropy(logits,ty[ids_batch]);loss.backward()
        torch.nn.utils.clip_grad_norm_(old.parameters(),1.0);old_optim.step()
        history_old.append(float(loss.detach()))
        if (step+1)%16==0:print('OLD_STEP',step+1,'LOSS',round(history_old[-1],5),flush=True)
    old.eval()

    torch.manual_seed(SEED+303)
    cross=GatedCrossAttention()
    cross_optim=torch.optim.AdamW(cross.parameters(),lr=LR,weight_decay=0.0)
    init_zero_ok=False
    with torch.no_grad():
        delta0,gate0=cross(qheld[:8],bank_keys[held_ix[:8]],bank_vals[held_ix[:8]],held_sim[:8])
        init_zero_ok=bool(torch.count_nonzero(delta0)==0)
    assert init_zero_ok
    history_cross=[]
    for step in range(STEPS):
        offset=(step%(FIT//BATCH))*BATCH; batch=order[offset:offset+BATCH]
        cross_optim.zero_grad(set_to_none=True)
        delta,gate=cross(qfit[batch],bank_keys[fit_ix[batch]],bank_vals[fit_ix[batch]],fit_sim[batch])
        logits=F.linear(qfit[batch]+delta,table)
        loss=F.cross_entropy(logits,ty[batch]);loss.backward()
        torch.nn.utils.clip_grad_norm_(cross.parameters(),1.0);cross_optim.step()
        history_cross.append(float(loss.detach()))
        if (step+1)%16==0:print('CROSS_STEP',step+1,'LOSS',round(history_cross[-1],5),'GATE',round(float(gate.detach().mean()),5),flush=True)
    cross.eval()

    external_head=table.detach().clone()
    assert external_head.data_ptr()!=table.data_ptr()
    def evaluate(xs,pos,target,q,idx,sim,mean):
        full_forward_discrepancies=[]
        all_arms={k:[] for k in ['A_base','B_exact','OLD_adapter','C_cross_attention','D_shuffled_values','E_bypass']}
        gates=[]
        with torch.inference_mode():
            for off in range(0,len(xs),8):
                sl=slice(off,off+8)
                xb=xs[sl];pb=pos[sl];qb=q[sl];ib=idx[sl];sb=sim[sl];mb=mean[sl]
                z_selected=forward_hidden(xb)[torch.arange(len(xb)),pb]
                baseline=F.linear(z_selected,table)
                h_external=forward_hidden(xb,external_head)[torch.arange(len(xb)),pb]
                exact=F.linear(h_external,external_head)
                orig=model(xb)[torch.arange(len(xb)),pb]
                full_forward_discrepancies.append(float((orig-baseline).abs().max()))
                assert torch.equal(baseline,exact), 'EXTERNAL_TIED_HEAD_NOT_EXACT'
                assert torch.allclose(orig,baseline,atol=1e-5,rtol=1e-6), 'BACKBONE_INCOMPATIBLE'
                logits_old=old_forward(xb,pb,qb,mb,old)
                dc,g=cross(qb,bank_keys[ib],bank_vals[ib],sb)
                ds,_=cross(qb,bank_keys[ib],bank_shuffled[ib],sb)
                all_arms['A_base'].append(baseline)
                all_arms['B_exact'].append(exact)
                all_arms['OLD_adapter'].append(logits_old)
                all_arms['C_cross_attention'].append(F.linear(qb+dc,table))
                all_arms['D_shuffled_values'].append(F.linear(qb+ds,table))
                all_arms['E_bypass'].append(F.linear(qb,table))
                gates.append(g)
        arms={k:torch.cat(v) for k,v in all_arms.items()}
        ll={k:F.cross_entropy(v,target,reduction='none') for k,v in arms.items()}
        a=arms['A_base'].argmax(-1)
        stats={k:{'nll':float(z.mean()),'accuracy':float((arms[k].argmax(-1)==target).float().mean()),'agreement_with_base':float((arms[k].argmax(-1)==a).float().mean())} for k,z in ll.items()}
        gain=ll['A_base']-ll['C_cross_attention']
        rng=np.random.default_rng(20261112+len(target))
        draws=rng.integers(0,len(target),size=(2000,len(target)))
        boot=np.quantile(gain.numpy()[draws].mean(1),[.025,.975]).tolist()
        g=torch.cat(gates)
        return stats,{'max_abs_original_3d_head_vs_selected_2d_head':max(full_forward_discrepancies),'mean_gate':float(g.mean()),'gate_min':float(g.min()),'gate_max':float(g.max()),'mean_base_minus_C_nll':float(gain.mean()),'gain_bootstrap95_descriptive':list(map(float,boot)), 'neighbor_top1_hit_rate':float((by[idx[:,0]]==target).float().mean()),'neighbor_top4_hit_rate':float((by[idx]==target[:,None]).any(-1).float().mean())}
    hstats,hmore=evaluate(hx,hp,hy,qheld,held_ix,held_sim,held_mean)
    vstats,vmore=evaluate(vx,vp,vy,qval,val_ix,val_sim,val_mean)
    prior_stats,prior_more=evaluate(vx[:128],vp[:128],vy[:128],qval[:128],val_ix[:128],val_sim[:128],val_mean[:128])
    assert abs(prior_stats['OLD_adapter']['nll']-3.7390940189361572)<2e-5, 'HISTORICAL_OLD_ADAPTER_NOT_REPRODUCED'
    def verdict(stats):
        return all(stats['C_cross_attention']['nll']+1e-4 < stats[k]['nll'] for k in ['A_base','OLD_adapter','D_shuffled_values'])
    out={
      'experiment':'TTM_VECTOR_MEMORY_GATED_CROSS_ATTENTION_ARCHITECTURE_MINI_TEST',
      'status':'YES_SCOPED_EXPLORATORY' if verdict(hstats) else 'NO_SCOPED_EXPLORATORY',
      'definition':'YES if C NLL strictly better than frozen A, old adapter, and shuffled-value D on 256 unseen-to-adapter TRAIN stories; exploratory only',
      'model':{'checkpoint_sha256':CK,'train_val_pack_sha256':PACK,'source_git_blob':SRC,'step':1280,'backbone_frozen':True},
      'design':{'seed':SEED,'train_bank_stories':BANK,'train_fit_stories':FIT,'train_holdout_stories':HOLD,'val_story_count_already_seen_in_prior_diagnostics':VAL,'context':CONTEXT,'topk':K,'steps':STEPS,'batch_size':BATCH,'lr':LR,'same_old_adapter_training_setup':True,'cross_attn_zero_init_bypass':init_zero_ok,'cross_attention_description':'top4 distinct TRAIN keys and next-token embeddings + trainable q/k/v projections, post-backbone head residual, per-query learned gate initialized low', 'primary_not_confirmatory':'Holdout is disjoint from adapter-fitting and bank but belongs to TRAIN distribution used to train checkpoint; all VAL stories previously seen in diagnostics'},
      'training':{'old_start16':float(np.mean(history_old[:16])),'old_last16':float(np.mean(history_old[-16:])), 'cross_start16':float(np.mean(history_cross[:16])),'cross_last16':float(np.mean(history_cross[-16:])), 'old_trainable_params':sum(p.numel() for p in old.parameters()),'cross_trainable_params':sum(p.numel() for p in cross.parameters())},
      'holdout_train_not_used_for_adapter_or_bank':{'arms':hstats,'additional':hmore,'selection_index_sha256':shaids(held_idx),'verdict_yes':verdict(hstats)},
      'historical_adapter_regression_on_prior_128_val':{'old_adapter_nll':prior_stats['OLD_adapter']['nll'],'prior_reported_old_adapter_nll':3.7390940189361572,'reproduced':True},
      'val_previously_examined_exploratory_only':{'arms':vstats,'additional':vmore,'selection_index_sha256':shaids(val_idx),'verdict_yes':verdict(vstats)},
      'integrity':{'checkpoint_unchanged':all(torch.equal(v,before[k]) for k,v in model.state_dict().items()),'all_original_parameters_frozen':all(not p.requires_grad for p in model.parameters()),'original_exact_external_embedding_and_head_bit_exact_on_both_sets':all(s['A_base']==s['B_exact'] for s in [hstats,vstats]),'init_zero_delta_exact':init_zero_ok,'bank_fit_holdout_disjoint':True,'test_never_loaded':True,'private_rows_not_exported':True},
      'scope_limits':['Exploratory small CPU pilot; no new story-level independent VAL available in existing pack','Holdout TRAIN previously seen by original GPT training, not a scientific heldout test','All VAL story labels explored by prior pilots; VAL metrics descriptive only','Memory values are next-token embeddings, not novel external facts','No claim about architecture-scale improvement, memory economics, or generalization'],
      'environment':{'torch':torch.__version__,'python':platform.python_version(),'cpu_threads':torch.get_num_threads()},
      'elapsed_seconds_removed_from_json_for_reproducibility':True
    }
    # Don't include runtime in reproducibility-critical hash.
    assert all(out['integrity'].values())
    args.out.parent.mkdir(parents=True,exist_ok=True)
    args.out.write_text(json.dumps(out,ensure_ascii=False,sort_keys=True,indent=2)+'\n',encoding='utf-8')
    print('RESULT',json.dumps({'status':out['status'],'holdout':hstats,'val':vstats,'training':out['training']},ensure_ascii=False),flush=True)

if __name__=='__main__':main()
