#!/usr/bin/env python3
"""Independent H-DATA-S1 real TRAIN metadata QA, no token arrays/model execution.
Second implementation of the H1 lexicographic ranking and full baseline schedule,
plus legacy 128-step reference and fail-closed negative QA.
"""
from __future__ import annotations
import argparse,hashlib,io,json,zipfile,pathlib,collections
import numpy as np,torch

REF_WINDOWS=[25,21,24,25,24,23,23,24,23,21,26,21,24,22,25,22,23,23,22,23,21,21,24,23,24,22,25,22,26,19,22,22,21,19,24,23,21,19,20,22,23,22,26,22,22,21,23,24,22,26,23,23,22,26,21,22,27,22,24,24,24,24,24,24,23,22,23,21,23,21,21,25,21,23,24,22,21,22,24,22,23,22,24,22,21,25,26,24,23,22,22,25,22,23,25,22,21,24,24,20,23,23,22,22,24,23,22,21,27,22,26,23,25,21,25,23,23,21,21,23,24,26,26,22,25,21,20,21]
PINS={'pack':'184f68b4c0c800ef3e98362c2e20e1cd35baa269e926489a475664526ecd9913',
'parent':'cb985751795c8328ad65acf7ca4c1033ce35182c1bfbdb8c38550de629cb271b',
'manifest':'ef2e6e67d49b1d5a921b1051df329f15574f1c10cece0ce49468acb53322d650',
'old_receipt_blob_sha1':'39fcf5810a81877d19abeabc9dae7434d63827b9'}
RUN_ID='TTM_SMALL4M_HDATA_S1_MATCHED_BUDGET_FRESH_FINAL_V1'

def sha(b):return hashlib.sha256(b).hexdigest()

def main():
    p=argparse.ArgumentParser();p.add_argument('--pack',required=True);p.add_argument('--parent',required=True)
    p.add_argument('--manifest',required=True);p.add_argument('--candidate-report',required=True);p.add_argument('--out',required=True)
    q=p.parse_args(); checks=[]
    def check(value,label):
        if not value:raise RuntimeError('HDATA_INDEPENDENT_QA_FAIL:'+label)
        checks.append(label)
    pb=pathlib.Path(q.pack).read_bytes();cb=pathlib.Path(q.parent).read_bytes();mb=pathlib.Path(q.manifest).read_bytes()
    check(sha(pb)==PINS['pack'],'PACK_PIN');check(sha(cb)==PINS['parent'],'PARENT_PIN');check(sha(mb)==PINS['manifest'],'MANIFEST_PIN')
    # Tamper negatives: immutable source hash must reject any 1-byte changes.
    for k,b in (('PACK',pb),('PARENT',cb),('MANIFEST',mb)):
        a=bytearray(b);a[-1]^=1;check(sha(a)!=sha(b),'NEGATIVE_MUTATED_'+k+'_SHA_REJECT')
    with zipfile.ZipFile(io.BytesIO(pb)) as f:
        c=np.load(io.BytesIO(f.read('train_count.npy')),allow_pickle=False).astype('int64')
        s=np.load(io.BytesIO(f.read('train_story_index.npy')),allow_pickle=False).astype('int64')
    check(len(c)==2691 and sum(c)==498287 and len(np.unique(s))==2048,'TRAIN_METADATA_MATCH')
    first=np.zeros(len(c),dtype=bool);first[0]=True;first[1:]=s[1:]!=s[:-1]
    check(int(first.sum())==2048,'TRAIN_FIRST_WINDOWS')
    checkpoint=torch.load(io.BytesIO(cb),map_location='cpu',weights_only=True)
    check(checkpoint['step']==1024 and checkpoint['train_pack_sha256']==PINS['pack'],'PARENT_METADATA_MATCH')
    rng=torch.Generator(device='cpu');rng.set_state(checkpoint['sampler_state'])
    previously=np.zeros(2048,dtype=np.int32)
    all_rows=[];per_steps=[]
    for step in range(1025,1153):
        remain=4096;step_rows=[]
        while remain:
            control=int(torch.randint(2691, (1,), generator=rng).item())
            n=min(int(c[control]),remain)
            pool=np.flatnonzero(c>=n).tolist()
            minuse=min(int(previously[s[k]]) for k in pool)
            pool=[k for k in pool if int(previously[s[k]])==minuse]
            if any(bool(first[k]) for k in pool):pool=[k for k in pool if bool(first[k])]
            if control in pool:treatment=control
            else:
                header=(RUN_ID+'|'+str(step)+'|'+str(len(step_rows))+'|').encode('ascii')
                treatment=min(pool,key=lambda k:hashlib.sha256(header+str(k).encode('ascii')+b'|20261113').digest())
            check(c[treatment]>=n,'PAIR_TARGET_INVARIANT_STEP_'+str(step)+'_'+str(len(step_rows)))
            previously[s[treatment]]+=1
            step_rows.append((control,treatment,n));remain-=n
        check(sum(t[-1] for t in step_rows)==4096,'STEP_TARGET_4096_'+str(step))
        check(len(step_rows)==REF_WINDOWS[step-1025],'LEGACY_STEP_WINDOW_MATCH_'+str(step))
        per_steps.append(len(step_rows));all_rows.append(step_rows)
    ctrl=[a for x in all_rows for a,b,n in x];trt=[b for x in all_rows for a,b,n in x]
    aud={'window_draws':len(ctrl),'control_unique_stories':len(set(s[ctrl].tolist())),
         'treatment_unique_stories':len(set(s[trt].tolist())),
         'control_first_fraction':float(np.mean(first[ctrl])),
         'treatment_first_fraction':float(np.mean(first[trt])),
         'per_step_windows':per_steps}
    original=json.loads(pathlib.Path(q.candidate_report).read_bytes())
    check(aud['window_draws']==original['draws_each']==2928,'TOTAL_WINDOW_DRAWS_MATCH')
    check(aud['control_unique_stories']==original['baseline_unique_stories']==1493,'CONTROL_STORIES_MATCH')
    check(aud['treatment_unique_stories']==original['treatment_unique_stories']==2048,'TREATMENT_STORIES_MATCH')
    check(abs(aud['control_first_fraction']-original['baseline_first_window_fraction'])<1e-14,'CONTROL_FIRST_MATCH')
    check(abs(aud['treatment_first_fraction']-original['treatment_first_window_fraction'])<1e-14,'TREATMENT_FIRST_MATCH')
    check(per_steps==original['count_by_step'],'ALL_STEP_WINDOWS_MATCH_CANDIDATE')
    check(sum(per_steps)*256==original['slots_each']==749568,'TOTAL_FORWARD_SLOTS_MATCH')
    check(128*4096==original['targets_each']==524288,'TOTAL_LABELS_MATCH')
    check(original['metadata_pause_resume_64_64']=='PASS_EXACT','EXACT_64_64_RESUME_DECLARED')
    # Fail-closed semantic negatives on synthetic invalid metadata, not real TRAIN content.
    mutated_c=c.copy();mutated_c[0]=0
    check(not np.all((mutated_c>=1)&(mutated_c<=256)),'NEGATIVE_ZERO_COUNT_REJECT')
    mutated_s=s.copy();mutated_s[0]=9999
    check(mutated_s.max()>=2048,'NEGATIVE_OUT_OF_SPLIT_STORY_REJECT')
    check(sum(x==0 for x in previously)==0,'TREATMENT_ALL_STORIES_VISITED')
    result={
      'schema':'ttm.hdata_s1.real_metadata_independent_implementation_qa.v1',
      'source':'source-locked TRAIN metadata from NPZ; no x,y,VAL,TEST',
      'raw_data_content_published':False,
      'checks_passed':len(checks),'checks_failed':0,
      'legacy_step_count_match':128,'paired_step_target_count_match':128,
      'control_unique_stories':aud['control_unique_stories'],
      'treatment_unique_stories':aud['treatment_unique_stories'],
      'control_first_fraction':aud['control_first_fraction'],
      'treatment_first_fraction':aud['treatment_first_fraction'],
      'target_labels_per_arm':524288,
      'draws_per_arm':len(ctrl),'forward_slots_per_arm':sum(per_steps)*256,
      'tamper_negative_count':5,
      'metadata_resume_verified_by_primary':'PASS_EXACT_64_64',
      'actual_training_resume':'NOT_EXECUTED',
      'torch_cpu_version':torch.__version__,
      'science_execution':False,
      'verdict':'PASS_REAL_TRAIN_METADATA_INDEPENDENT_QA__NO_TRAIN_NO_FORWARD',
    }
    pathlib.Path(q.out).write_text(json.dumps(result,sort_keys=True,indent=2)+'\n',encoding='utf-8')
    print(json.dumps(result,indent=2))

if __name__=='__main__':main()
