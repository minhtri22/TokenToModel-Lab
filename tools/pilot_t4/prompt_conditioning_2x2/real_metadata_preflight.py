#!/usr/bin/env python3
"""Read-only TRAIN metadata + locked step-1024 sampler-state draw feasibility.
No TRAIN token material, texts, checkpoints, condition labels or reviewer keys exported.
No torch optimizer step. Requires exact pinned input SHA and unmodified source paths.
"""
from __future__ import annotations
import argparse, hashlib, json, math
from collections import Counter
from pathlib import Path
import numpy as np
import torch

PACK_SHA='184f68b4c0c800ef3e98362c2e20e1cd35baa269e926489a475664526ecd9913'
MANIFEST_SHA='ef2e6e67d49b1d5a921b1051df329f15574f1c10cece0ce49468acb53322d650'
CHECKPOINT_SHA='cb985751795c8328ad65acf7ca4c1033ce35182c1bfbdb8c38550de629cb271b'
ROOT='ttm.t4.private.train_val.windowpack.v1'
STEPS=128; START=1024; BUDGET=4096; SEED=20261110; CONTEXT=256


def sha_file(p):
    h=hashlib.sha256()
    with open(p,'rb') as f:
        for chunk in iter(lambda:f.read(1<<20),b''): h.update(chunk)
    return h.hexdigest()

def require(cond,code):
    if not cond: raise RuntimeError(code)

def ranked_match(eligible,step,draw_index,story,seed=SEED):
    # Exact prereg deterministic keyed ranking of candidate window id.
    def rank(idx):
        msg=f'{seed}|{step}|{draw_index}|T{idx:04d}-S{story[idx]:04d}-O000'.encode('ascii')
        return (hashlib.sha256(msg).digest(),idx)
    return min(eligible,key=rank)


def run(pack_path,manifest_path,checkpoint_path):
    paths=[Path(x) for x in (pack_path,manifest_path,checkpoint_path)]
    for p in paths: require(p.is_file() and not p.is_symlink(),'NOT_REGULAR_NON_SYMLINK:'+p.name)
    checks=[PACK_SHA,MANIFEST_SHA,CHECKPOINT_SHA]
    for p,expected in zip(paths,checks):require(sha_file(p)==expected,'SHA256_MISMATCH:'+p.name)
    manifest=json.loads(paths[1].read_text('utf-8'))
    require(manifest['schema']==ROOT,'PACK_SCHEMA')
    require(manifest['npz_sha256']==PACK_SHA,'PACK_MANIFEST_MISMATCH')
    require(manifest['contains_test'] is False and manifest['contains_raw_text'] is False,'FORBIDDEN_CONTENT')
    with np.load(paths[0],allow_pickle=False) as z:
        require(set(z.files)=={f'{s}_{f}' for s in ('train','val') for f in ('x','y','count','story_index')},'PACK_KEYS')
        count=z['train_count'].astype(np.int64).copy()
        story=z['train_story_index'].astype(np.int64).copy()
        train_x=z['train_x'];train_y=z['train_y']
        vcount=z['val_count'];vstory=z['val_story_index']
        require(train_x.shape==train_y.shape==(2691,CONTEXT),'TRAIN_SHAPE')
        require(len(count)==2691 and len(story)==2691 and len(vcount)==328,'COUNT_SHAPE')
        require((count>=1).all() and (count<=CONTEXT).all(),'TRAIN_COUNT_RANGE')
        require((np.arange(CONTEXT)[None,:] < count[:,None]).sum()==498287,'MASK_COUNTS')
        require(int(count.sum())==498287,'REAL_TRAIN_TARGETS')
        require(story.min()==0 and story.max()==2047 and len(set(story))==2048,'STORIES')
        require(np.all(story[1:]>=story[:-1]),'STORY_ORDER_NOT_CONTIGUOUS')
        mask=np.arange(CONTEXT)[None,:] < count[:,None]
        require(np.all(train_y[~mask]==-100),'PAD_MASK')
        require(np.all((train_y[mask]>=0)&(train_y[mask]<2048)),'VALID_TARGET_ID_RANGE')
        require(np.all(train_x[:, :-1][mask[:, :-1] & mask[:, 1:]] >= 0),'INPUT_ID_RANGE')
        require(int(vcount.sum())==61122 and len(set(vstory))==256,'VAL_METADATA_SHAPE')
        # Do not copy/expose any reversible token sequences.
    first=np.r_[True, story[1:]!=story[:-1]]
    indices=np.flatnonzero(first)
    require(len(indices)==2048,'FIRST_STORY_WINDOW_COUNT')
    require(int(count[indices].max())==256,'NO_FULL_LENGTH_FIRST_STORY_WINDOW')
    cp=torch.load(paths[2],map_location='cpu',weights_only=True)
    require(cp['step']==START and cp['train_pack_sha256']==PACK_SHA,'CHECKPOINT_PACK_OR_STEP')
    require(cp['p02_git_blob']=='9762343e06cf800b50574c2871ae1ed58537fb18','P02_PIN')
    require(cp['science_seed']==20261108,'SEED_PIN')
    require(cp['optimizer']['param_groups'][0]['lr']>0,'OPTIMIZER_LR_INVALID')
    for state in cp['optimizer']['state'].values():
        require(float(state['step'])==1024,'OPTIMIZER_STEP_DRIFT')
    require(cp.get('sampler_state') is not None and cp.get('grad_scaler_state') is not None,'MISSING_STATE')
    gen=torch.Generator(device='cpu')
    gen.set_state(cp['sampler_state'].cpu())
    # The real metadata count list drives exactly the frozen T4 sample_exact_step logic.
    total_A=0;total_B=0;windows_A=0;windows_B=0;total_slots=0
    hA=hashlib.sha256();hB=hashlib.sha256();hCount=hashlib.sha256()
    used_A=Counter();used_B=Counter();sum_first_A=0;replaced=0;first_len_hist=Counter(map(int,count[indices]))
    per_step=[];cache={}
    for step in range(1025,1153):
        before=0;drawidx=0; listA=[];listB=[];scored=[]
        while before<BUDGET:
            idx=int(torch.randint(len(count),(1,),generator=gen).item())
            n=min(int(count[idx]),BUDGET-before)
            require(1<=n<=int(count[idx]),'INVALID_BASELINE_REAL_DRAW')
            eligible=cache.get(n)
            if eligible is None:
                eligible=[int(i) for i in indices if count[i]>=n]
                cache[n]=eligible
            require(bool(eligible),'MISSING_FIRST_WINDOW_AT_REAL_DRAW')
            rep=ranked_match(eligible,step,drawidx,story)
            require(first[rep] and int(count[rep])>=n,'REPLACEMENT_INVALID')
            before+=n;scored.append(n);listA.append(idx);listB.append(rep)
            drawidx+=1;used_A[int(story[idx])]+=1;used_B[int(story[rep])]+=1
            sum_first_A+=bool(first[idx]);replaced+=(rep!=idx)
        require(before==BUDGET and len(listA)==len(listB),'INVALID_STEP_BUDGET')
        for idx,rep,n in zip(listA,listB,scored):
            # Avoid releasing selected private window indices: hash only.
            hA.update(f'{step}/{idx}/{n};'.encode());hB.update(f'{step}/{rep}/{n};'.encode());hCount.update(f'{step}/{n};'.encode())
        total_A+=before;total_B+=sum(scored);windows_A+=len(listA);windows_B+=len(listB)
        total_slots+=len(listA)*CONTEXT
        per_step.append({'step':step,'targets':before,'window_draws':len(listA),'forward_slots':len(listA)*CONTEXT,
                         'first_candidate_available_for_all':True,'counts_matched':True})
    require(total_A==total_B==128*4096,'REAL_MATCHED_128_STEP_TARGETS_MISMATCH')
    require(windows_A==windows_B,'REAL_FORWARD_WINDOWS_MISMATCH')
    del cp
    return {
      'schema':'ttm.small4m.real_train_metadata_matched_draws.readonly.v1',
      'date':'2026-11-10','status':'PASS_REAL_METADATA_COUNT_MATCHED_128_STEPS_SOURCE_ONLY',
      'private_inputs_sha256':{'train_val_npz':PACK_SHA,'pack_manifest':MANIFEST_SHA,'step1024_checkpoint':CHECKPOINT_SHA},
      'public_safe_counts':{
        'train_stories':2048,'train_windows':2691,'first_story_windows':len(indices),'train_targets_unique':int(count.sum()),
        'max_first_window_targets':int(count[indices].max()),'first_windows_with_256_targets':int((count[indices]==256).sum()),
        'distinct_first_window_target_counts':len(first_len_hist),
        'val_stories':256,'val_windows':328,'val_targets':61122,
        'steps_per_arm':128,'target_exposures_per_arm':total_A,
        'forward_window_draws_per_arm':windows_A,'forward_slots_per_arm':total_slots,
        'first_story_draws_in_A_C':int(sum_first_A),'first_story_draws_in_B_D':windows_B,
        'replaced_draws_in_B_D':replaced,'distinct_train_stories_drawn_in_A_C':len(used_A),'distinct_train_stories_drawn_in_B_D':len(used_B)
      },
      'equality':{'A_equals_C_exact_schedule':True,'B_equals_D_exact_schedule':True,
        'per_step_scored_counts_and_forward_shapes_matched':True,'all_first_window_candidates_available':True},
      'schedule_digests':{'A_C':hA.hexdigest(),'B_D':hB.hexdigest(),'shared_target_count_vector':hCount.hexdigest()},
      'limitations':['PRIVATE raw train tokens or indices NEVER exported','Only metadata-level matching verified; not model training or GPU','Checkpoint used only to read exact sampler and optimizer states; no weight modification','Actual labeled target window and loss semantics still need CPU runner preflight'],
      'per_step_public_summary':per_step
    }

def main():
    ap=argparse.ArgumentParser()
    ap.add_argument('--pack',required=True);ap.add_argument('--manifest',required=True);ap.add_argument('--checkpoint',required=True);ap.add_argument('--out',required=True)
    a=ap.parse_args(); r=run(a.pack,a.manifest,a.checkpoint)
    p=Path(a.out);p.parent.mkdir(parents=True,exist_ok=True)
    if p.exists():raise FileExistsError('NO_OVERWRITE')
    p.write_text(json.dumps(r,indent=2,sort_keys=True)+'\n',encoding='utf-8')
    print('REAL_METADATA_MATCHED_DRAW=',r['status'])
    print('TARGET_EXPOSURES_PER_ARM=',r['public_safe_counts']['target_exposures_per_arm'])
    print('FORWARD_WINDOWS_PER_ARM=',r['public_safe_counts']['forward_window_draws_per_arm'])
    print('DIGEST_A_C=',r['schedule_digests']['A_C'])
    print('DIGEST_B_D=',r['schedule_digests']['B_D'])
if __name__=='__main__': main()
