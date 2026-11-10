#!/usr/bin/env python3
"""TTM exploratory CPU: frozen trained P02 + TRAIN contextual-vector kNN -> VAL NLL.
No gradient, no TEST; no private window/token bytes written to output.
Requires original repo (tools/pilot_t4/integrated/p02_source_exact.py),
step1280 checkpoint and T4 PRIVATE TRAIN/VAL window pack separately.
"""
import argparse, hashlib, importlib.util, json, sys
from pathlib import Path
import numpy as np
import torch
from torch.nn import functional as F

CK='ee723407b2c25a18be20e26387a3dd8e4a18e2942d469279b6f0748ff86af0dc'
PACK='184f68b4c0c800ef3e98362c2e20e1cd35baa269e926489a475664526ecd9913'
SRC='9762343e06cf800b50574c2871ae1ed58537fb18'

def digest(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def select(stories,n,salt):
    one={}
    for i,s in enumerate(stories):one.setdefault(int(s),i)
    return np.array(sorted(one.values(),key=lambda i:hashlib.sha256(f'{salt}:{i}'.encode()).digest())[:n])
def part(data,prefix,ids):
    x=data[prefix+'_x'][ids,:64].astype('int64');y=data[prefix+'_y'][ids,:64].astype('int64')
    pos=np.minimum(data[prefix+'_count'][ids],64).astype('int64')-1
    assert np.all(pos>=0) and np.all(y[np.arange(len(ids)),pos]>=0)
    return torch.tensor(x),torch.tensor(pos),torch.tensor(y[np.arange(len(ids)),pos])
def sha_indices(x):return hashlib.sha256(','.join(map(str,x.tolist())).encode()).hexdigest()

def main():
    p=argparse.ArgumentParser()
    p.add_argument('--repo-root',type=Path,required=True)
    p.add_argument('--checkpoint',type=Path,required=True)
    p.add_argument('--private-pack',type=Path,required=True)
    p.add_argument('--output',type=Path,required=True)
    a=p.parse_args()
    torch.set_num_threads(2);torch.manual_seed(20261111);torch.use_deterministic_algorithms(True)
    assert digest(a.checkpoint)==CK and digest(a.private_pack)==PACK
    source=a.repo_root/'tools/pilot_t4/integrated/p02_source_exact.py'
    # Git blob of this exact file was verified in the repository before the run.
    spec=importlib.util.spec_from_file_location('ttm_source_p02_exact',source)
    m=importlib.util.module_from_spec(spec);sys.modules[spec.name]=m;spec.loader.exec_module(m)
    ck=torch.load(a.checkpoint,map_location='cpu',weights_only=True)
    assert ck['step']==1280 and ck['p02_git_blob']==SRC and ck['train_pack_sha256']==PACK
    model=m.GPT(m.P02Config(**ck['config'])).cpu().eval()
    model.load_state_dict(ck['model'],strict=True)
    assert model.head.weight.data_ptr()==model.tok.weight.data_ptr()
    table=model.tok.weight.detach().clone()
    pack=np.load(a.private_pack,allow_pickle=False)
    ti=select(pack['train_story_index'],512,'TRAIN20261111')
    vi=select(pack['val_story_index'],128,'VAL20261111')
    tx,tp,ty=part(pack,'train',ti);vx,vp,vy=part(pack,'val',vi)
    def hidden(emb):
        x=emb+model.pos(torch.arange(emb.shape[1]))[None,:,:]
        for block in model.blocks:x=block(x)
        return model.final_ln(x)
    def contextual(inputs,pos):
        outs=[]
        for j in range(0,len(inputs),8):
            xx=inputs[j:j+8];pp=pos[j:j+8]
            z=hidden(model.tok(xx))[torch.arange(len(xx)),pp]
            outs.append(z)
        return torch.cat(outs)
    with torch.inference_mode():
        k=F.normalize(contextual(tx,tp),dim=-1)
        q=F.normalize(contextual(vx,vp),dim=-1)
        scores,inds=(q@k.T).topk(4,dim=-1)
        weights=F.softmax(scores/0.05,dim=-1)
        values=table[ty]
        found=(weights[:,:,None]*values[inds]).sum(1)
        perm=torch.randperm(len(values),generator=torch.Generator().manual_seed(919198))
        shuffled=(weights[:,:,None]*values[perm][inds]).sum(1)
        out=[[],[],[],[]]
        for j in range(0,len(vx),8):
            x=vx[j:j+8];pos=vp[j:j+8];rows=torch.arange(len(x))
            baseline=model(x)[rows,pos]
            ext=F.linear(hidden(table[x]),table)[rows,pos]
            assert torch.equal(baseline,ext)
            emb=table[x]
            c=emb.clone();c[rows,pos]=0.75*emb[rows,pos]+0.25*found[j:j+8]
            d=emb.clone();d[rows,pos]=0.75*emb[rows,pos]+0.25*shuffled[j:j+8]
            for dest,value in zip(out,(baseline,ext,F.linear(hidden(c),table)[rows,pos],F.linear(hidden(d),table)[rows,pos])):
                dest.append(value)
        A,B,C,D=(torch.cat(x) for x in out)
        def stats(logits):
            nll=F.cross_entropy(logits,vy,reduction='none')
            return {'nll_nats':float(nll.mean()),'ppl':float(nll.mean().exp()),
                    'top1_accuracy':float((logits.argmax(-1)==vy).float().mean()),'n_targets':int(len(vy))}
        result={'experiment':'TTM_TRAINED_SEMANTIC_VECTOR_RETRIEVAL_SHARED_BACKBONE_MINI_TEST',
            'date':'2026-11-11','scope':'EXPLORATORY_CPU_NOT_CONFIRMATORY',
            'sources':{'checkpoint_sha256':CK,'train_val_pack_sha256':PACK,'p02_git_blob':SRC,
                       'data':'TinyStories TRAIN/VAL original tokenized window pack; no TEST',
                       'private_bytes_exported':False},
            'fixed_design':{'train_unique_stories':512,'val_unique_stories':128,'sequence_length':64,
                            'train_selected_index_sha256':sha_indices(ti),'val_selected_index_sha256':sha_indices(vi),
                            'retrieval':'cosine kNN on frozen P02 contextual state of observed prefix',
                            'k':4,'temperature':0.05,'alpha':0.25,
                            'values':'TRAIN next token embeddings; never VAL targets',
                            'backbone':'same frozen Attention/MLP/LayerNorm/position embeddings and tied head in all arms'},
            'arms':{'A_original':stats(A),'B_exact_external':stats(B),
                    'C_content_retrieval':stats(C),'D_shuffled_values':stats(D)},
            'comparisons':{'A_B_bit_exact_logits':bool(torch.equal(A,B)),
                           'C_minus_A_nll_nats':stats(C)['nll_nats']-stats(A)['nll_nats'],
                           'C_minus_D_nll_nats':stats(C)['nll_nats']-stats(D)['nll_nats'],
                           'C_vs_A_top1_agreement':float((C.argmax(-1)==A.argmax(-1)).float().mean()),
                           'retrieved_next_token_top1_hit':float((ty[inds[:,0]]==vy).float().mean())},
            'limitations':'Only one VAL next-token target per story; nearest contextual representation is not proof of semantics; no trained adapter, no unseen-document knowledge, no statistical claim.'}
        cnd=result['comparisons'];passed=cnd['C_minus_A_nll_nats']<0 and cnd['C_minus_D_nll_nats']<0
        result['verdict']='PASS_EXPLORATORY' if passed else 'FAIL_EXPLORATORY'
    a.output.parent.mkdir(parents=True,exist_ok=True)
    a.output.write_text(json.dumps(result,ensure_ascii=False,sort_keys=True,indent=2)+'\n',encoding='utf-8')
    print(json.dumps({'verdict':result['verdict'],'arms':result['arms'],'comparisons':result['comparisons']},indent=2))
if __name__=='__main__':main()
