#!/usr/bin/env python3
"""H-DATA-S1 real TRAIN metadata preflight; strictly NO TRAIN token arrays, no training, no inference.

Reads signed TRAIN/VAL NPZ by SHA-256, but opens *only* train_count and train_story_index
from the zip. CPU torch.load(weights_only=True) only for immutable sampler/optimizer
metadata; never instantiates a model or advances an optimizer. Produces public-safe
aggregate receipt without story-window IDs or TRAIN tokens. Failure is fail closed.
"""
from __future__ import annotations
import argparse, collections, copy, hashlib, io, json, pathlib, zipfile, sys
import numpy as np
import torch

PACK_SHA = '184f68b4c0c800ef3e98362c2e20e1cd35baa269e926489a475664526ecd9913'
PARENT_SHA = 'cb985751795c8328ad65acf7ca4c1033ce35182c1bfbdb8c38550de629cb271b'
MANIFEST_SHA = 'ef2e6e67d49b1d5a921b1051df329f15574f1c10cece0ce49468acb53322d650'
SCIENCE_LOCK_SHA = 'fd183ade2a696d40313aae19b63429d4ef3edd8abf25c899c8cc496836d36817'
SEED = 20261113
RUN_ID = 'TTM_SMALL4M_HDATA_S1_MATCHED_BUDGET_FRESH_FINAL_V1'
STEPS=128; TARGET=4096; CONTEXT=256


def sha(b: bytes) -> str:
    return hashlib.sha256(b).hexdigest()


def require(x, label):
    if not x: raise RuntimeError('HDATA_S1_PREEXEC_HOLD:'+label)


def get_real_metadata(pack_path):
    pack_path=pathlib.Path(pack_path)
    require(sha(pack_path.read_bytes())==PACK_SHA,'PACK_SHA_MISMATCH')
    # Never open train_x/train_y or any val_* arrays.
    with zipfile.ZipFile(pack_path) as z:
        # z.read() validates CRC for the two metadata members only.
        # z.testzip() is intentionally forbidden: it would decompress TRAIN token arrays.
        names=set(z.namelist())
        require(names=={f'{a}_{b}.npy' for a in ('train','val') for b in ('x','y','count','story_index')},'NPZ_SCHEMA')
        c=np.load(io.BytesIO(z.read('train_count.npy')),allow_pickle=False).astype(np.int64)
        s=np.load(io.BytesIO(z.read('train_story_index.npy')),allow_pickle=False).astype(np.int64)
    require(len(c)==len(s)==2691,'TRAIN_WINDOWS_2691')
    require(len(set(s.tolist()))==2048 and s.min()==0 and s.max()==2047,'TRAIN_STORIES_2048')
    require(c.min()>=1 and c.max()<=CONTEXT and int(c.sum())==498287,'VALID_TRAIN_COUNTS')
    # The first window of each story is the first appearance in contiguous sorted pack.
    require(bool(np.all(s[1:]>=s[:-1])),'STORY_ID_NOT_MONOTONIC')
    first=np.empty(len(s),dtype=bool);first[0]=True;first[1:]=(s[1:]!=s[:-1])
    require(int(first.sum())==2048,'FIRST_WINDOW_COUNTS')
    return c,s,first


def freeze_parent(ckpt):
    cp=torch.load(ckpt,map_location='cpu',weights_only=True)
    require(cp['schema']=='ttm.t4.science.checkpoint.v1' and cp['step']==1024,'PARENT_STEP_SCHEMA')
    require(cp['train_pack_sha256']==PACK_SHA and cp['science_lock_sha256']==SCIENCE_LOCK_SHA,'PARENT_SOURCE_LOCKS')
    require(cp['p02_git_blob']=='9762343e06cf800b50574c2871ae1ed58537fb18','P02_ARCH_BLOB')
    require(cp['config']=={'vocab_size':2048,'max_seq_len':256,'n_embd':256,'n_layer':4,'n_head':4,'norm_type':'layernorm'},'P02_CONFIG')
    require(isinstance(cp['sampler_state'],torch.Tensor) and cp['sampler_state'].dtype==torch.uint8,'SAMPLER_STATE')
    require(all(k in cp for k in ('optimizer','scheduler','grad_scaler_state','torch_cpu_rng','torch_cuda_rng','python_rng','numpy_rng','model')),'RESUME_FIELDS')
    require(isinstance(cp['optimizer'],dict) and cp['optimizer'].get('param_groups'),'OPTIMIZER_STATE')
    require(isinstance(cp['scheduler'],dict) and 'last_epoch' in cp['scheduler'],'SCHEDULER_STATE')
    require(isinstance(cp['grad_scaler_state'],dict) and 'scale' in cp['grad_scaler_state'],'SCALER_STATE')
    return cp


def score_h1(counts, stories, first, exposed, n, step, draw, base_idx):
    """Single prereg candidate policy: story diversity, then first window, then baseline, stable SHA.
    Step budget and baseline scored length n NEVER change; avoid touching x/y arrays.
    """
    eligible=np.flatnonzero(counts>=n)
    require(len(eligible)>0,'NO_ELIGIBLE_TRAIN_WINDOW')
    a=exposed[stories[eligible]]
    eligible=eligible[a==a.min()]
    eligible=eligible[first[eligible]==first[eligible].max()]
    if base_idx in eligible:
        return int(base_idx)  # prefer no replacement after the policy's diversity/first-window priorities
    # Cryptographically stable tie break; cannot depend on Python randomized hash seed.
    prefix=f'{RUN_ID}|{step}|{draw}|'.encode('ascii')
    return min((int(k) for k in eligible), key=lambda k: hashlib.sha256(prefix+str(k).encode('ascii')+b'|'+str(SEED).encode('ascii')).digest())


def one_step(g, counts, stories, first, exposed, step):
    total=0; out=[]; draws=0
    while total<TARGET:
        k0=int(torch.randint(len(counts),(1,),generator=g).item())
        n=min(int(counts[k0]),TARGET-total)
        require(n>0,'BAD_BASE_DRAW_TARGETS')
        k1=score_h1(counts,stories,first,exposed,n,step,draws,k0)
        require(int(counts[k1])>=n,'H1_COUNT_TOO_SHORT')
        # Increment only H1 exposure, used to choose later H1 windows.
        exposed[stories[k1]]+=1
        out.append((k0,k1,n));total+=n;draws+=1
    require(total==TARGET,'STEP_LABEL_COUNT')
    return out


def run_steps(g,c,s,f,exposed,steps,begin):
    rows=[]
    for step in range(begin,begin+steps):rows.append(one_step(g,c,s,f,exposed,step))
    return rows


def plan_fingerprint(rows):
    # internal schedule private digest; never export sequence, only hash.
    body='\n'.join(','.join(f'{u}:{v}:{n}' for u,v,n in step) for step in rows).encode('ascii')
    return sha(body)


def evaluate(rows,c,s,first):
    a=[k for step in rows for k,_,_ in step]
    b=[k for step in rows for _,k,_ in step]
    scored=[n for step in rows for *_,n in step]
    per_step=[len(step) for step in rows]
    require(len(rows)==STEPS,'STEP_COUNT')
    require(sum(scored)==STEPS*TARGET,'TOTAL_LABELS')
    require(len(a)==len(b)==sum(per_step),'WINDOW_SHAPE_TOTAL')
    require(all(sum(n for _,_,n in step)==TARGET for step in rows),'EXACT_STEP_TARGETS')
    require(all(n<=c[k1] and n<=c[k0] for step in rows for k0,k1,n in step),'MATCHED_LABEL_COUNT')
    require(all(1<=n<=CONTEXT for n in scored),'CONTEXT_RANGE')
    require(all(len([k0 for k0,_,_ in step])==len([k1 for _,k1,_ in step]) for step in rows),'FORWARD_WINDOWS_MATCHED')
    u0=len(set(s[a].tolist()));u1=len(set(s[b].tolist()))
    first0=float(np.mean(first[a]));first1=float(np.mean(first[b]))
    distinct_gain=(u1-u0)/u0
    early_gain=first1-first0
    return dict(
        checkpoint_parent_step=1024,steps=STEPS,target_per_step=TARGET,targets_each=TARGET*STEPS,
        draws_each=len(a),slots_each=len(a)*CONTEXT,
        baseline_unique_stories=u0,treatment_unique_stories=u1,relative_story_gain=distinct_gain,
        baseline_first_window_fraction=first0,treatment_first_window_fraction=first1,
        first_window_percentage_point_gain=100*early_gain,
        thresholds={'relative_story_gain_ge_5_percent':distinct_gain>=.05,
                    'first_window_gain_ge_10pp':early_gain>=.1,
                    'same_exact_step_targets_and_windows':True},
        replaced_draws=sum(x!=y for x,y in zip(a,b)),
        control_draw_digest=sha(','.join(f'{k}:{n}' for step in rows for k,_,n in step).encode()),
        treatment_draw_digest=sha(','.join(f'{k}:{n}' for step in rows for _,k,n in step).encode()),
        paired_schedule_digest=plan_fingerprint(rows),
        count_by_step=per_step,
    )


def main(argv=None):
    p=argparse.ArgumentParser();p.add_argument('--pack',required=True);p.add_argument('--manifest',required=True)
    p.add_argument('--parent',required=True);p.add_argument('--science-lock',required=True)
    p.add_argument('--output',required=True);a=p.parse_args(argv)
    require(sha(pathlib.Path(a.manifest).read_bytes())==MANIFEST_SHA,'MANIFEST_SHA')
    require(sha(pathlib.Path(a.science_lock).read_bytes())==SCIENCE_LOCK_SHA,'SCIENCE_LOCK_SHA')
    require(sha(pathlib.Path(a.parent).read_bytes())==PARENT_SHA,'PARENT_SHA')
    c,s,f=get_real_metadata(a.pack);cp=freeze_parent(a.parent)
    gen=torch.Generator(device='cpu');gen.set_state(cp['sampler_state'].cpu().clone())
    exp=np.zeros(2048,dtype=np.int32)
    first64=run_steps(gen,c,s,f,exp,64,1025)
    state64=gen.get_state().clone(); exp64=exp.copy()
    second64=run_steps(gen,c,s,f,exp,64,1089)
    whole=first64+second64
    metrics=evaluate(whole,c,s,f)
    # exact pause/resume for (64+64), including sampler torch Generator and treatment story exposures
    resumed=torch.Generator(device='cpu');resumed.set_state(state64)
    exp_resume=exp64.copy()
    rerun=run_steps(resumed,c,s,f,exp_resume,64,1089)
    require(plan_fingerprint(rerun)==plan_fingerprint(second64),'SAMPLER_PAUSE_RESUME_64_64_NOT_EQUAL')
    require(np.array_equal(exp,exp_resume),'SAMPLER_EXPOSURE_RESUME_NOT_EQUAL')
    require(torch.equal(resumed.get_state(),gen.get_state()),'TORCH_SAMPLER_STATE_RESUME_NOT_EQUAL')
    metrics['metadata_pause_resume_64_64']='PASS_EXACT'
    metrics['source_pins']={'pack_sha256':PACK_SHA,'manifest_sha256':MANIFEST_SHA,'parent_sha256':PARENT_SHA,'science_lock_sha256':SCIENCE_LOCK_SHA}
    metrics['assurance']='REAL_TRAIN_METADATA_ONLY__NO_TRAIN_X_Y_ARRAY_READ__NO_MODEL_FORWARD__NO_OPTIMIZER_STEP'
    metrics['torch_version']=str(torch.__version__)
    metrics['sci_training_rights']='NOT_GRANTED_FOR_HDATA_S1'
    metrics['status']='PASS_REAL_METADATA' if all(metrics['thresholds'].values()) else 'HOLD_MANIPULATION_NOT_MET'
    pathlib.Path(a.output).write_text(json.dumps(metrics,ensure_ascii=False,indent=2,sort_keys=True)+'\n',encoding='utf8')
    print(json.dumps({k:v for k,v in metrics.items() if k not in ('count_by_step','source_pins')},indent=2))
    return 0

if __name__=='__main__':raise SystemExit(main())
