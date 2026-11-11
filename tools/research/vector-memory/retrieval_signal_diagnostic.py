#!/usr/bin/env python3
"""Read-only TRAIN-memory retrieval-signal diagnostic (CPU, no gradient or TEST).

Replicates the exact bank and previously examined VAL 128-story selection from
TTM Vector Memory adapter pilot. Reports a second disjoint 128-story VAL group.
Exposes aggregate metrics/hashes only (no reversible training or VAL tokens).
"""
from __future__ import annotations
import argparse, hashlib, importlib.util, json, math, platform, sys
from pathlib import Path
import numpy as np
import torch
import torch.nn.functional as F

CHECKPOINT_SHA = 'ee723407b2c25a18be20e26387a3dd8e4a18e2942d469279b6f0748ff86af0dc'
PACK_SHA = '184f68b4c0c800ef3e98362c2e20e1cd35baa269e926489a475664526ecd9913'
P02_BLOB = '9762343e06cf800b50574c2871ae1ed58537fb18'
BANK, K, CONTEXT, TEMPERATURE = 512, 4, 64, .05
SEED, N_PERM = 20261111, 1000

def sha_bytes(path):
    h=hashlib.sha256()
    with open(path,'rb') as f:
        for b in iter(lambda:f.read(1<<20), b''):h.update(b)
    return h.hexdigest()

def stable_index_hash(idx):
    return hashlib.sha256(','.join(map(str,idx.tolist())).encode()).hexdigest()

def select_unique(story_index, n, salt):
    first={}
    for i,story in enumerate(story_index):first.setdefault(int(story),i)
    keys=sorted(first,key=lambda s:hashlib.sha256(f'{salt}:{s}'.encode()).digest())
    return np.array([first[s] for s in keys[:n]],dtype=np.int64)

def rows(pack, prefix, indices):
    x=pack[prefix+'_x'][indices,:CONTEXT].astype(np.int64)
    pos=np.minimum(pack[prefix+'_count'][indices].astype(np.int64),CONTEXT)-1
    y=pack[prefix+'_y'][indices,:CONTEXT].astype(np.int64)
    assert np.all(pos>=0) and np.all(y[np.arange(len(indices)),pos]>=0)
    return torch.from_numpy(x),torch.from_numpy(pos),torch.from_numpy(y[np.arange(len(indices)),pos])

def mean_ci(values,seed):
    values=np.asarray(values,dtype=np.float64)
    rng=np.random.default_rng(seed)
    ix=rng.integers(0,len(values),(2000,len(values)))
    return [float(x) for x in np.quantile(values[ix].mean(axis=1),[.025,.975])]

def main():
    p=argparse.ArgumentParser()
    p.add_argument('--checkpoint',type=Path,required=True)
    p.add_argument('--private-pack',type=Path,required=True)
    p.add_argument('--reference-module',type=Path,required=True,
                   help='Local source with OriginalP02GPT, mathematically matching pinned P02')
    p.add_argument('--output',type=Path,required=True)
    a=p.parse_args()
    torch.set_num_threads(2)
    torch.manual_seed(SEED)
    torch.use_deterministic_algorithms(True)
    assert sha_bytes(a.checkpoint)==CHECKPOINT_SHA
    assert sha_bytes(a.private_pack)==PACK_SHA
    ck=torch.load(a.checkpoint,map_location='cpu',weights_only=True)
    assert ck['step']==1280 and ck['p02_git_blob']==P02_BLOB and ck['train_pack_sha256']==PACK_SHA
    s=importlib.util.spec_from_file_location('ttm_prior_reference',a.reference_module)
    mod=importlib.util.module_from_spec(s);sys.modules[s.name]=mod;s.loader.exec_module(mod)
    model=mod.OriginalP02GPT(ck['config']).cpu().eval()
    model.load_state_dict(ck['model'],strict=True)
    model.requires_grad_(False)
    assert model.head.weight.data_ptr()==model.tok.weight.data_ptr()
    state_before={k:v.detach().clone() for k,v in model.state_dict().items()}
    pack=np.load(a.private_pack,allow_pickle=False)
    ids=select_unique(pack['train_story_index'],1024,'TTM_ADAPTER20261111_TRAIN')
    bank_ids,fit_ids=ids[:BANK],ids[BANK:]
    prior_val_ids=select_unique(pack['val_story_index'],128,'VAL20261111')
    all_val_ids=select_unique(pack['val_story_index'],256,'VAL20261111')
    assert np.array_equal(prior_val_ids,all_val_ids[:128])
    assert not set(map(int,pack['train_story_index'][bank_ids])) & set(map(int,pack['train_story_index'][fit_ids]))
    bx,bp,by=rows(pack,'train',bank_ids)
    vx,vp,vy=rows(pack,'val',all_val_ids)
    assert len(set(map(int,pack['val_story_index'][all_val_ids])))==256
    # Consistency with prior pilot: previously-examined selection indices pinned.
    assert stable_index_hash(bank_ids)=='4b8546f6d9c22df481d4b9be6a9e0d97691179bde21cb48d38e44e580eb60922'
    assert stable_index_hash(prior_val_ids)=='fb9d072fbb817cc8cc5a90367f2175d7b789d29a2140a660fbf2803332fa584f'

    @torch.inference_mode()
    def forward_hidden(x):
        z=model.tok(x)+model.pos(torch.arange(x.shape[1]))[None,:,:]
        for block in model.blocks:z=block(z)
        return model.final_ln(z)
    @torch.inference_mode()
    def context_features(x,positions):
        result=[]
        for j in range(0,len(x),16):
            z=forward_hidden(x[j:j+16]);pp=positions[j:j+16]
            result.append(z[torch.arange(len(pp)),pp])
        return torch.cat(result,0)
    @torch.inference_mode()
    def gold_logits(x,positions):
        result=[]
        for j in range(0,len(x),16):
            z=forward_hidden(x[j:j+16]);pp=positions[j:j+16]
            logits=F.linear(z[torch.arange(len(pp)),pp],model.tok.weight)
            result.append(logits)
        return torch.cat(result,0)

    bank_context=context_features(bx,bp)
    val_context=context_features(vx,vp)
    assert bank_context.shape==(BANK,256) and val_context.shape==(256,256)
    base_logits=gold_logits(vx,vp)
    ref_logits=model(vx[:8])
    assert torch.equal(base_logits[:8],ref_logits[torch.arange(8),vp[:8]]), 'REFERENCE_MODEL_NOT_EQUAL'
    with torch.inference_mode():
        probs=base_logits.softmax(-1).numpy().astype(np.float64)
    base_loss=-np.log(probs[np.arange(256),vy.numpy()])
    # Search with full contextual hidden states, plus last-token-only control.
    queries={
        'hidden_context':(F.normalize(bank_context,dim=1),F.normalize(val_context,dim=1)),
        'last_token_embedding':(F.normalize(model.tok(bx[torch.arange(BANK),bp]),dim=1),
                                F.normalize(model.tok(vx[torch.arange(256),vp]),dim=1))
    }
    labels=by.numpy(); gold=vy.numpy();
    hist=np.bincount(labels,minlength=ck['config']['vocab_size']).astype(np.float64)
    # Smoothed global TRAIN-bank label unigram, for fair frequency baseline.
    p0=(hist+0.5)/(len(labels)+0.5*len(hist))
    unigram_nll=-np.log(p0[gold])
    subsets={'previous_val128':np.arange(0,128),'additional_val128':np.arange(128,256),'all_val256':np.arange(256)}
    ret={}
    for key_kind,(bk,vq) in queries.items():
        similarity=vq@bk.T
        sc,neighbors=similarity.topk(K,dim=1)
        sc=sc.numpy().astype(np.float64)
        neighbors=neighbors.numpy()
        # torch softmax on FP32 score to match frozen adapter pilot.
        weights=F.softmax(torch.tensor(sc,dtype=torch.float32)/TEMPERATURE,dim=-1).numpy().astype(np.float64)
        returned=labels[neighbors]
        top1=(returned[:,0]==gold).astype(np.float64)
        top4=(returned==gold[:,None]).any(axis=1).astype(np.float64)
        gold_mass=(weights*(returned==gold[:,None])).sum(axis=1)
        # Pre-fixed shallow-fusion probes, no tuning or training.
        knn_prob=np.zeros_like(probs)
        ix=np.arange(len(gold))
        for j in range(K):np.add.at(knn_prob,(ix,returned[:,j]),weights[:,j])
        mix_nll={}
        for lam in (.05,.10,.25):
            pm=(1-lam)*probs[ix,gold]+lam*knn_prob[ix,gold]
            mix_nll[f'lambda_{lam:.2f}']=-np.log(pm)
        # Deterministic label-shuffle null preserving bank label frequencies and neighbor geometry.
        rng=np.random.default_rng(20261111+ (0 if key_kind=='hidden_context' else 7))
        null_top1=np.empty((N_PERM,len(gold)),dtype=np.float32)
        null_top4=np.empty_like(null_top1)
        null_mass=np.empty_like(null_top1)
        null_fusion=np.empty_like(null_top1)
        for b in range(N_PERM):
            perm=labels[rng.permutation(len(labels))]
            put=perm[neighbors]
            ishit=(put==gold[:,None])
            null_top1[b]=ishit[:,0]
            null_top4[b]=ishit.any(axis=1)
            null_mass[b]=(weights*ishit).sum(axis=1)
            null_fusion[b]=-np.log(.90*probs[ix,gold]+.10*null_mass[b])
        margins=sc[:,0]-sc[:,1]
        section={}
        for group,idx in subsets.items():
            n=len(idx)
            def nm(a):return float(np.mean(a[idx]))
            observed=float(top1[idx].mean())
            nullmeans=null_top1[:,idx].mean(axis=1)
            null4means=null_top4[:,idx].mean(axis=1)
            perm_p=(1+int(np.sum(nullmeans>=observed)))/(N_PERM+1)
            target_idx=idx
            gain=base_loss[idx]-mix_nll['lambda_0.10'][idx]
            section[group]={
                'targets':n,
                'top1_hit':nm(top1), 'top4_any_hit':nm(top4),
                'weighted_correct_mass':nm(gold_mass),
                'top1_random_shuffle_mean':float(nullmeans.mean()),
                'top1_random_shuffle_p95':float(np.quantile(nullmeans,.95)),
                'top4_random_shuffle_mean':float(null4means.mean()),
                'top1_excess_vs_shuffle':float(observed-nullmeans.mean()),
                'top1_excess_95pct_bootstrap_CI':mean_ci(top1[idx]-null_top1[:,idx].mean(axis=0),SEED+101+len(idx)),
                'top1_permutation_one_sided_p':perm_p,
                'mean_top1_cosine':nm(sc[:,0]),
                'mean_neighbor_margin':nm(margins),
                'base_frozen_nll':nm(base_loss),
                'global_unigram_nll':nm(unigram_nll),
                'nll_with_knn_fusion':{label:nm(value) for label,value in mix_nll.items()},
                'nll_with_shuffled_knn_fusion_0.10_mean':float(null_fusion[:,idx].mean()),
                'base_minus_knn_fusion0.10_mean':float(gain.mean()),
                'base_minus_knn_fusion0.10_bootstrap95pct_CI':mean_ci(gain,SEED+505+len(idx)),
                'knn_fusion0.10_minus_shuffled_mean':float(mix_nll['lambda_0.10'][idx].mean()-null_fusion[:,idx].mean()),
                'knn_fusion0.10_shuffled_comparison_p':float((1+np.sum(null_fusion[:,idx].mean(axis=1)<=mix_nll['lambda_0.10'][idx].mean()))/(N_PERM+1)),
            }
        ret[key_kind]=section
    # exploratory stop gate: contextual signal should exceed randomized labels AND
    # improve frozen model NLL with fixed lambda=.10 on additional VAL 128,
    # not merely outperform a weak unconditional label prior.
    additional=ret['hidden_context']['additional_val128']
    both=(additional['top1_permutation_one_sided_p']<=.05 and
          additional['base_minus_knn_fusion0.10_mean']>0 and
          additional['base_minus_knn_fusion0.10_bootstrap95pct_CI'][0]>0)
    verdict='SIGNAL_SUPPORTED_FOR_FURTHER_STUDY' if both else 'PAUSE_VECTOR_MEMORY_RESEARCH_NO_RELIABLE_INCREMENTAL_SIGNAL'
    out={
        'experiment':'TTM_VECTOR_MEMORY_RETRIEVAL_SIGNAL_DIAGNOSTIC',
        'verdict':verdict,
        'scope':'CPU_READ_ONLY_EXPLORATORY; no gradients; previous 128 VAL + additional disjoint 128 VAL; no TEST; no tuning',
        'decision_rule':'continue only if additional 128 VAL have p<=.05 for top1 vs 1000 label-shuffle null, AND lambda=.10 kNN fusion improves frozen NLL with 95pct paired bootstrap lower bound >0; otherwise PAUSE',
        'environment':{'python':platform.python_version(),'torch':torch.__version__,'threads':torch.get_num_threads(),'device':'cpu'},
        'pins':{'checkpoint_sha256':CHECKPOINT_SHA,'train_val_pack_sha256':PACK_SHA,'p02_git_blob':P02_BLOB,
                'reference_reimplementation_sha256':sha_bytes(a.reference_module)},
        'design':{'bank_stories':BANK,'bank_selection_sha256':stable_index_hash(bank_ids),
                  'adapter_fit_reserved_train_stories':512,'val_previous_selection_sha256':stable_index_hash(prior_val_ids),
                  'val_all_selection_sha256':stable_index_hash(all_val_ids),
                  'new_val_disjoint_from_previous':True,'context_length':CONTEXT,'k':K,
                  'softmax_temperature':TEMPERATURE,'random_label_permutations':N_PERM,
                  'fusion_lambdas':[.05,.1,.25],'bank_label_unique_count':int(np.count_nonzero(hist)),
                  'bank_label_top1_frequency':float(hist.max()/BANK),
                  'val_label_unique_count':int(len(set(gold.tolist()))),
                  'bank_target_label_coverage_on_val':float(np.mean(hist[gold]>0)),
                  'frozen_parameters':True,'no_adapter_training':True},
        'metrics':ret,
        'integrity':{'checkpoint_unchanged':all(torch.equal(v,state_before[k]) for k,v in model.state_dict().items()),
                     'no_gradients':all(p.grad is None for p in model.parameters()),
                     'no_test':True,'no_private_text_or_token_rows_in_output':True,
                     'train_bank_fit_disjoint':True,'VAL_disjoint_from_TRAIN':True},
        'limitations':['kNN labels are next-token TRAIN, not external novel knowledge',
                       'new VAL group disjoint from previous 128 but within same corpus and previously defined VAL split',
                       'permutation test only compares association against shuffled labels; does not establish semantic usefulness',
                       'fusion is fixed output-level NLL probe, not trained adapter or same input injection',
                       'one target per story, 256 stories total, not confirmatory or out-of-domain',
                       'no architecture change or impact on main and P00-P12']
    }
    assert all(out['integrity'].values())
    a.output.parent.mkdir(parents=True,exist_ok=True)
    a.output.write_text(json.dumps(out,ensure_ascii=False,sort_keys=True,indent=2)+'\n',encoding='utf-8')
    print(json.dumps({'verdict':verdict,'hidden':ret['hidden_context'],'last_token':ret['last_token_embedding']},indent=2),flush=True)

if __name__=='__main__':main()
