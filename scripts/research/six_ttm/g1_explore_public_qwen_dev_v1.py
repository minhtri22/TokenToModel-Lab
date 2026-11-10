#!/usr/bin/env python3
"""Exploratory ONLY: REAL pinned Qwen3 0.6B->1.7B representation screen.

Only authored public-looking fictional prompts: no TTM or G1 corpus/manifest/TEST.
No owner science permit, no G1 original science, no claim of SIX advantage.
Run QA on CPU or run on interactive Colab Free T4 (no Drive mount).
"""
from __future__ import annotations
import argparse
import gc
import hashlib
import json
import os
from pathlib import Path
import platform
import sys
import time

import numpy as np

SCHEMA = 'ttm.six.g1.explore.authored_public_prompts.dev_only.v1'
SEED = 20261110
TRAIN_GROUPS = 12
DEV_GROUPS = 4
PER_GROUP = 4
ALPHA = 10.0
N_NEGATIVE = 32
MAX_WALL_SECONDS = 1800  # best-effort budget, not external supervisor
GiB = 1024 ** 3
PROBES = [
    (' Everyone felt safe.', ' Everyone felt afraid.'),
    (' The story ended happily.', ' The story ended sadly.'),
]
MODELS = {
    'source': {'repo': 'Qwen/Qwen3-0.6B', 'revision': 'c1899de289a04d12100db370d81485cdf75e47ca',
               'hidden': 1024, 'weights': {'model.safetensors': 'f47f71177f32bcd101b7573ec9171e6a57f4f4d31148d38e382306f42996874b'}},
    'target': {'repo': 'Qwen/Qwen3-1.7B', 'revision': '70d244cc86ccca08cf5af4e1e306ecf908b1ad5e',
               'hidden': 2048, 'weights': {'model-00001-of-00002.safetensors': '169ad53ec313c3a34b06c0809216e4fc072cce444a5d4ff2b59690d064130ed5',
                                           'model-00002-of-00002.safetensors': '912becff8d60672aa8628ef08c05898d9adf17c2ad4ae3caf99b065622fdeff9'}}
}
# Each group is one fictional situation; four paraphrases stay IN THE SAME SPLIT.
SCENES = [
    ('Mira', 'library', 'quiet morning', 'found a notebook that a visitor had lost'),
    ('Theo', 'forest trail', 'foggy afternoon', 'lost the marked path as heavy rain began'),
    ('Anya', 'harbor', 'cloudy evening', 'helped a tired dog climb out of the water'),
    ('Luca', 'schoolyard', 'bright morning', 'broke a window while playing with a ball'),
    ('Sora', 'market', 'busy afternoon', 'returned a wallet to its worried owner'),
    ('Nia', 'garden', 'sunny morning', 'noticed a tiny bird trapped behind a fence'),
    ('Omar', 'museum', 'rainy evening', 'heard a warning alarm near the main entrance'),
    ('Elena', 'train station', 'cold morning', 'offered a seat to a traveler carrying heavy bags'),
    ('Jonas', 'beach', 'windy evening', 'saw a child walk too close to the rough waves'),
    ('Priya', 'bakery', 'warm morning', 'shared the last loaf with a hungry neighbor'),
    ('Ren', 'farm', 'early morning', 'found the barn door open after a storm'),
    ('Ava', 'city park', 'quiet afternoon', 'helped a lost visitor find the correct bus stop'),
    ('Kian', 'mountain path', 'icy afternoon', 'noticed a broken wooden bridge ahead'),
    ('Yuna', 'hospital hallway', 'late evening', 'brought warm food to a waiting family'),
    ('Milo', 'town square', 'bright afternoon', 'spotted a dropped key beside a fountain'),
    ('Iris', 'river bank', 'stormy morning', 'warned the hikers that the water was rising'),
]
TEMPLATES = [
    'During a {when}, {name} visited the {place}. {name} {event}, and the others watched carefully.',
    'It was a {when} at the {place}. When {name} {event}, everyone wondered what would happen next.',
    'At the {place} on a {when}, {name} {event}. The moment surprised the people nearby.',
    '{name} had not expected much from a {when} at the {place}. But {name} {event}, and things changed.',
]

def sha(b: bytes) -> str:
    return hashlib.sha256(b).hexdigest()

def digest_file(p: Path) -> str:
    h = hashlib.sha256()
    with p.open('rb') as f:
        for block in iter(lambda: f.read(4*1024*1024), b''):
            h.update(block)
    return h.hexdigest()

def require(ok, reason):
    if not ok:
        raise RuntimeError('STOP_G1_EXPLORATORY_' + reason)

def build_rows():
    groups = []
    for i, (name, place, when, event) in enumerate(SCENES):
        rows = []
        for j, template in enumerate(TEMPLATES):
            prompt = template.format(name=name, place=place, when=when, event=event)
            rows.append({'group': f'fiction_{i:02d}', 'template': j, 'text': prompt,
                         'prompt_sha256': sha(prompt.encode('utf-8'))})
        groups.append(rows)
    order = sorted(range(len(groups)), key=lambda k: sha((str(SEED)+'|'+str(k)).encode()))
    train = [r for k in order[:TRAIN_GROUPS] for r in groups[k]]
    dev = [r for k in order[TRAIN_GROUPS:] for r in groups[k]]
    require(len(train) == 48 and len(dev) == 16, 'SPLIT_COUNT')
    require(not ({r['group'] for r in train} & {r['group'] for r in dev}), 'GROUP_LEAK')
    require(len({r['prompt_sha256'] for r in train+dev}) == 64, 'PROMPT_DUPLICATE')
    return train, dev

def manifest():
    train, dev = build_rows()
    return {'schema': SCHEMA, 'split': {'TRAIN': [x['prompt_sha256'] for x in train],
                                       'DEV': [x['prompt_sha256'] for x in dev]},
            'group_order_train': list(dict.fromkeys(r['group'] for r in train)),
            'group_order_dev': list(dict.fromkeys(r['group'] for r in dev)),
            'model_revisions': {k: v['revision'] for k,v in MODELS.items()},
            'probe_pairs': PROBES, 'seed': SEED,
            'read_g1_original_TEST': False, 'read_ttm_val_test': False}

def train_kernel(x_train, x_other):
    mu = x_train.mean(0)
    sd = np.maximum(x_train.std(0), 1e-5)
    a = (x_train-mu)/sd
    b = (x_other-mu)/sd
    scale = max(1, x_train.shape[1])
    return a@a.T/scale, b@a.T/scale

def fit_predict(k, kdev, y, alpha=ALPHA):
    avg = y.mean(0)
    weights = np.linalg.solve(k + alpha*np.eye(k.shape[0]), y - avg)
    return kdev@weights+avg

def r2_vec(y_pred, y_true, y_train):
    avg = y_train.mean(0)
    den = np.sum((y_true-avg)**2, axis=0)
    if np.any(den<1e-8):return None
    return (1 - np.sum((y_pred-y_true)**2,axis=0)/den).tolist()

def cka(x,y):
    def center(k):
        return k-k.mean(0,keepdims=True)-k.mean(1,keepdims=True)+k.mean()
    gx=center(x@x.T); gy=center(y@y.T)
    den=float(np.linalg.norm(gx)*np.linalg.norm(gy))
    return None if den<1e-10 else float(np.sum(gx*gy)/den)

def summarize(xs, xt, rt):
    train,dev=build_rows(); n=len(train); require(len(xs)==len(xt)==len(rt)==n+len(dev),'RESULT_LENGTH')
    require(xs.shape[1]==1024 and xt.shape[1]==2048 and rt.shape[1]==2,'RESULT_SHAPE')
    require(all(np.isfinite(v).all() for v in (xs,xt,rt)), 'RESULT_NONFINITE')
    xs=np.asarray(xs,np.float64);xt=np.asarray(xt,np.float64);rt=np.asarray(rt,np.float64)
    k,kdev=train_kernel(xs[:n],xs[n:])
    # A->P: source->target-hidden learned TRAIN; target-hidden->probe response on TRAIN.
    align=fit_predict(k,kdev,xt[:n])
    # Train-only linear map target-hidden -> probes. Exact Xt train normalization.
    mu=xt[:n].mean(0);sd=np.maximum(xt[:n].std(0),1e-5)
    zz=(xt[:n]-mu)/sd; aa=(align-mu)/sd
    scale=max(1,xt.shape[1]); gram=zz@zz.T/scale
    mapping=np.linalg.solve(gram+ALPHA*np.eye(n),rt[:n]-rt[:n].mean(0))
    ap=(aa@zz.T/scale)@mapping+rt[:n].mean(0)
    direct=fit_predict(k,kdev,rt[:n]);baseline=np.tile(rt[:n].mean(0),(len(dev),1))
    rng=np.random.default_rng(SEED)
    neg_scores=[]
    for _ in range(N_NEGATIVE):
        perm=rng.permutation(TRAIN_GROUPS)
        # same index template within each whole group, not row-wise permuting.
        yp=xt[:n].reshape(TRAIN_GROUPS,PER_GROUP,-1)[perm].reshape(n,-1)
        dummy=fit_predict(k,kdev,yp)
        dummy=(dummy-mu)/sd
        shuffled=(dummy@zz.T/scale)@mapping+rt[:n].mean(0)
        neg_scores.append(float(np.mean(np.abs(shuffled-rt[n:]))))
    # CKA of four *group means*, not 16 correlated rows. Diagnostic only.
    xg=xs[n:].reshape(DEV_GROUPS,PER_GROUP,-1).mean(1)
    yg=xt[n:].reshape(DEV_GROUPS,PER_GROUP,-1).mean(1)
    error_ap=float(np.mean(np.abs(ap-rt[n:])))
    return {'schema':SCHEMA, 'status':'EXPLORATORY_REAL_MODEL_DEV_ONLY_NOT_G1_RESULT',
            'train_rows':n, 'dev_rows':len(dev), 'train_groups':TRAIN_GROUPS,'dev_groups':DEV_GROUPS,
            'metrics':{'dev_mae_alignment_to_probe':error_ap,
                       'dev_mae_direct_source_probe':float(np.mean(np.abs(direct-rt[n:]))),
                       'dev_mae_train_mean':float(np.mean(np.abs(baseline-rt[n:]))),
                       'dev_r2_per_probe_A_to_P':r2_vec(ap,rt[n:],rt[:n]),
                       'dev_r2_per_probe_direct':r2_vec(direct,rt[n:],rt[:n]),
                       'dev_group_mean_cka_diagnostic':cka(xg,yg),
                       'group_shuffle_negative_mae_median':float(np.median(neg_scores)),
                       'group_shuffle_negative_mae_best':float(np.min(neg_scores))},
            'null_group_shuffle_count':N_NEGATIVE,
            'limitations':['Only 4 DEV groups; no confirmatory p-value/power claim',
                           'A-to-P and direct source probe are not matched-information-budget comparisons',
                           'No TTM checkpoint or TEST; G1 original remains on HOLD']}

def save_atomic_npz(path, **vals):
    require(not path.exists(),'NO_OVERWRITE_'+path.name)
    tmp=path.with_name(path.stem+'.tmp.npz')
    require(not tmp.exists(),'TEMP_EXISTS')
    try:
        np.savez_compressed(tmp,**vals)
        os.replace(tmp,path)
    finally:
        if tmp.exists(): tmp.unlink()

def verified_snapshot(kind):
    from huggingface_hub import snapshot_download
    m=MODELS[kind]
    p=Path(snapshot_download(repo_id=m['repo'],revision=m['revision'],
                             allow_patterns=['*.safetensors','*.json','*.txt','LICENSE']))
    files={}
    for f,expect in m['weights'].items():
        actual=digest_file(p/f)
        require(actual==expect,kind.upper()+'_WEIGHT_SHA_'+f)
        files[f]=actual
    for name in ['config.json','tokenizer.json','tokenizer_config.json']:
        require((p/name).exists(),kind.upper()+'_MISSING_'+name)
        files[name]=digest_file(p/name)
    return p, files

def load_qwen(kind,p):
    import torch
    from transformers import AutoTokenizer, AutoModelForCausalLM
    tokenizer=AutoTokenizer.from_pretrained(str(p),local_files_only=True,trust_remote_code=False)
    model=AutoModelForCausalLM.from_pretrained(str(p),local_files_only=True,trust_remote_code=False,
                                               dtype=torch.float16).to('cuda').eval()
    require(model.config.hidden_size==MODELS[kind]['hidden'],kind.upper()+'_HIDDEN_WIDTH')
    require(model.config.num_hidden_layers==28,kind.upper()+'_LAYERS')
    return tokenizer,model

def extract_hidden(model,tokenizer,text):
    import torch
    ids=tokenizer(text,add_special_tokens=False,return_tensors='pt')['input_ids']
    require(8<=ids.shape[1]<=112,'TOKEN_LIMIT')
    with torch.inference_mode():
        o=model(ids.to('cuda'),output_hidden_states=True,use_cache=False,return_dict=True)
        h=o.hidden_states[28][0,-1,:].float().cpu().numpy().astype(np.float32)
    require(np.isfinite(h).all(),'HIDDEN_NONFINITE')
    return h,ids[0].tolist()

def logp_suffix(model,tokenizer,prefix_ids,suffix):
    import torch
    suffix_ids=tokenizer(suffix,add_special_tokens=False)['input_ids']
    require(1<=len(suffix_ids)<=24,'SUFFIX_TOKENS')
    full=torch.tensor([prefix_ids+suffix_ids],dtype=torch.long,device='cuda')
    with torch.inference_mode():
        logits=model(full,use_cache=False,return_dict=True).logits[0,len(prefix_ids)-1:-1].float()
        require(logits.shape[0]==len(suffix_ids),'CAUSAL_SHIFT')
        lp=torch.nn.functional.log_softmax(logits,dim=-1)
        ix=torch.tensor(suffix_ids,device='cuda')
        score=lp[torch.arange(len(suffix_ids),device='cuda'),ix].sum().item()
    return score/len(suffix.encode('utf-8'))

def run(args):
    import torch
    require(torch.cuda.is_available(),'CUDA_REQUIRED')
    require('T4' in torch.cuda.get_device_name(0),'EXACT_FREE_T4_REQUIRED')
    require(os.path.abspath(args.out).startswith('/content/'),'COLAB_CONTENT_ONLY')
    out=Path(args.out).resolve();require(str(out).startswith('/content/'),'COLAB_CONTENT_PATH')
    out.mkdir(parents=True,exist_ok=True)
    st=time.monotonic()
    train,dev=build_rows();rows=train+dev
    m=manifest();msha=sha(json.dumps(m,sort_keys=True,separators=(',',':')).encode())
    metadata=out/'manifest_receipt.json'
    if metadata.exists():
        saved=json.loads(metadata.read_text('utf-8'))
        require(saved['manifest_sha256']==msha,'RESUME_MANIFEST_MISMATCH')
        require(saved['source_code_sha256']==digest_file(Path(__file__)),'RESUME_CODE_MISMATCH')
    else:
        metadata.write_text(json.dumps({'schema':SCHEMA,'manifest_sha256':msha,'source_code_sha256':digest_file(Path(__file__)),
                                         'prompts_source':'AUTHORED_IN_CODE_NO_PRIVATE_G1_DATA',
                                         'G1_original_science_executed':False,'G1_private_TEST_opened':False},indent=2)+'\n')
    arrays={};proof={}
    for kind in ('source','target'):
        path_npz=out/(kind+'_features.npz')
        if path_npz.exists():
            with np.load(path_npz,allow_pickle=False) as f:
                require(f['manifest_sha256'].item()==msha,'RESUME_SHA')
                arrays[kind]=f['hidden'].copy()
                if kind=='target':arrays['probe']=f['probe'].copy()
            print('RESUME_VERIFIED',kind,digest_file(path_npz),flush=True)
            continue
        require(time.monotonic()-st < MAX_WALL_SECONDS,'TIME_BUDGET')
        p,proof[kind]=verified_snapshot(kind)
        tokenizer,model=load_qwen(kind,p)
        hs=[];probes=[]
        for i,row in enumerate(rows):
            require(time.monotonic()-st < MAX_WALL_SECONDS,'TIME_BUDGET')
            h,ids=extract_hidden(model,tokenizer,row['text'])
            hs.append(h)
            if kind=='target':
                probes.append([logp_suffix(model,tokenizer,ids,a)-logp_suffix(model,tokenizer,ids,b)
                               for a,b in PROBES])
            require(torch.cuda.max_memory_reserved()/GiB<12,'VRAM_BUDGET')
            if (i+1)%8==0:print('EXTRACT',kind,i+1,'of',len(rows),flush=True)
        arrays[kind]=np.stack(hs)
        if kind=='target':arrays['probe']=np.asarray(probes,dtype=np.float32)
        vals={'hidden':arrays[kind],'manifest_sha256':np.array(msha)}
        if kind=='target':vals['probe']=arrays['probe']
        save_atomic_npz(path_npz,**vals)
        print('EXTRACTION_COMMITTED',kind,digest_file(path_npz),flush=True)
        del model,tokenizer
        gc.collect();torch.cuda.empty_cache()
    result=summarize(arrays['source'],arrays['target'],arrays['probe'])
    result.update({'manifest_sha256':msha,'source_code_sha256':digest_file(Path(__file__)),
                   'elapsed_seconds':round(time.monotonic()-st,2),
                   'device':torch.cuda.get_device_name(0),
                   'model_revisions':m['model_revisions'],
                   'weights_verified_from_pinned_sha256':proof,
                   'exploratory_qwen_inference_executed':True,'G1_original_science_executed':False,'G1_private_TEST_opened':False,
                   'owner_G1_science_permit':'NOT_ISSUED'})
    result_path=out/'result.json'
    require(not result_path.exists(),'RESULT_ALREADY_EXISTS')
    result_path.write_text(json.dumps(result,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
    print('G1_EXPLORE_RESULT='+str(result_path),flush=True)
    print(json.dumps(result['metrics'],indent=2),flush=True)

def qa():
    train,dev=build_rows()
    assert len(train)==48 and len(dev)==16
    assert len(set(r['group'] for r in train))==12
    assert len(set(r['group'] for r in dev))==4
    assert all(len(x['text'])>35 for x in train+dev)
    m=manifest();assert 'TEST' not in m['split']
    rng=np.random.default_rng(SEED)
    xs=rng.normal(size=(64,1024)).astype('float32')
    xt=rng.normal(size=(64,2048)).astype('float32')
    rt=rng.normal(size=(64,2)).astype('float32')
    r=summarize(xs,xt,rt)
    assert r['train_rows']==48 and r['dev_rows']==16 and len(r['metrics'])==8
    assert r['status'].startswith('EXPLORATORY')
    assert r['metrics']['dev_group_mean_cka_diagnostic'] is not None
    assert all(np.isfinite(v) for k,v in r['metrics'].items() if isinstance(v,float))
    print('G1_EXPLORATORY_QA=PASS_SYNTHETIC_CPU_NO_MODELS_NO_TEST')
    print('AUTHOR_CREATED_GROUPS=16; TRAIN=48; DEV=16; TEST=0')

if __name__=='__main__':
    p=argparse.ArgumentParser()
    p.add_argument('--mode',choices=['qa','run'],required=True)
    p.add_argument('--out',default='/content/g1_explore_public_qwen_dev_v1')
    args=p.parse_args()
    qa() if args.mode=='qa' else run(args)
