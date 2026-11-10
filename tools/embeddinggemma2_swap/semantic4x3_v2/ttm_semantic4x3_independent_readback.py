#!/usr/bin/env python3
"""SEMANTIC4X3 independent evidence reader. No model imports / forward / training.

Recomputes 12 token-weighted NLLs and two co-primary 3-seed paired-story
bootstrap intervals; verifies SHA-chain, intermediate READY journals and all
12 final checkpoint binary hashes. Never reads H768 text/window labels.
"""
from __future__ import annotations
import argparse
import hashlib
import json
import os
from pathlib import Path
import numpy as np

STUDY_ID='ttm_gemma2_semantic4x3_3seed_2048x4096_h768_20261110_v2'
SEEDS=('S1','S2','S3')
ARMS=('PT-REAL','PT-PERM','NULL-REAL','NULL-PERM')
BOOT_SEED=2026111199


def require(test,err):
    if not bool(test):raise RuntimeError('HOLD_INDEPENDENT_'+err)

def sha_file(path):
    h=hashlib.sha256()
    with Path(path).open('rb') as f:
        for chunk in iter(lambda:f.read(1024*1024),b''):h.update(chunk)
    return h.hexdigest()

def read(path):return json.loads(Path(path).read_text('utf-8'))

def delta_verify(per,counts,draws=2000):
    raw=per['loss_sum_by_seed_arm']
    require(set(raw)==set(SEEDS),'SEED_SET')
    losses={s:{} for s in SEEDS}
    nll={s:{} for s in SEEDS};contrasts={s:{} for s in SEEDS}
    for seed in SEEDS:
        require(set(raw[seed])==set(ARMS),'ARM_SET_'+seed)
        for arm in ARMS:
            x=np.asarray(raw[seed][arm],dtype=np.float64)
            require(x.shape==(768,) and np.isfinite(x).all() and (x>=0).all(),'LOSS_VECTOR_'+seed+'_'+arm)
            losses[seed][arm]=x
            nll[seed][arm]=float(x.sum()/counts.sum())
        x=losses[seed]
        contrasts[seed]['delta_PRE']=float((x['PT-PERM']-x['PT-REAL']).sum()/counts.sum())
        contrasts[seed]['delta_NULL']=float((x['NULL-PERM']-x['NULL-REAL']).sum()/counts.sum())
        contrasts[seed]['tau_residual']=contrasts[seed]['delta_PRE']-contrasts[seed]['delta_NULL']
        contrasts[seed]['gamma_real']=float((x['NULL-REAL']-x['PT-REAL']).sum()/counts.sum())
    idx=np.random.default_rng(BOOT_SEED).integers(0,768,size=(draws,768))
    denominator=counts[idx].sum(axis=1)
    ci={}
    for key in ('tau_residual','gamma_real'):
        by_seed=[]
        for seed in SEEDS:
            x=losses[seed]
            z=(x['PT-PERM']-x['PT-REAL']-x['NULL-PERM']+x['NULL-REAL']
               if key=='tau_residual' else x['NULL-REAL']-x['PT-REAL'])
            by_seed.append(z)
        mean_story=np.mean(np.stack(by_seed,axis=0),axis=0)
        bootstrap=mean_story[idx].sum(axis=1)/denominator
        ci[key]={'mean_delta_nll':float(mean_story.sum()/counts.sum()),
                 'ci95_percentile':[float(x) for x in np.quantile(bootstrap,[.025,.975])],
                 'seed_all_positive':all(contrasts[s][key]>0 for s in SEEDS)}
    decision=('PASS_SCOPED_DONOR_RESIDUAL_STRUCTURE' if
      all(ci[k]['ci95_percentile'][0]>0 and ci[k]['seed_all_positive'] for k in ci)
      else 'DONOR_RESIDUAL_SIGNAL_NOT_ESTABLISHED_SCOPED_FAIL')
    return nll,contrasts,ci,decision

def compare_number(actual,expected,where):
    require(np.isfinite(actual) and np.isfinite(expected) and abs(actual-expected)<=1e-11, 'NUMERIC_'+where)

def check_result(result,nll,contrasts,bs,candidate):
    require(result['candidate_verdict']==candidate,'CANDIDATE_VERDICT')
    for s in SEEDS:
        for a in ARMS:compare_number(nll[s][a],result['nll_nats_per_target'][s][a],s+'_'+a)
        for k in ('delta_PRE','delta_NULL','tau_residual','gamma_real'):
            compare_number(contrasts[s][k],result['contrasts_by_seed'][s][k],s+'_'+k)
    for k in ('tau_residual','gamma_real'):
        compare_number(bs[k]['mean_delta_nll'],result['co_primary'][k]['mean_delta_nll'],k+'_mean')
        for j in range(2):compare_number(bs[k]['ci95_percentile'][j],result['co_primary'][k]['ci95_percentile'][j],k+'_CI'+str(j))
        require(bs[k]['seed_all_positive']==result['co_primary'][k]['seed_all_positive'],'ALL_SEEDS_'+k)

def verify_readies(out,claim):
    count=0;final_digests={}
    for s in SEEDS:
        seedid=STUDY_ID+'_'+s.lower()
        subclaim=read(out/s/'CLAIM.json')
        require(subclaim['study_id']==STUDY_ID and subclaim['run_id']==seedid and subclaim['seed']==s and
           subclaim['parent_study_claim_sha256']==sha_file(out/'STUDY_CLAIM.json'),'SEED_CLAIM_'+s)
        for arm in ARMS:
            armroot=out/s/'checkpoints'/arm
            require((armroot/'ARM_START.json').exists(),'MISSING_ARM_START_'+s+'_'+arm)
            for step in range(256,2049,256):
                directory=armroot/f'step_{step:04d}'
                require((armroot/f'CHUNK_{step:04d}_START.json').is_file() and
                        (armroot/f'CHUNK_{step:04d}_DONE.json').is_file(),'MISSING_CHUNK_JOURNAL_'+s+'_'+arm+str(step))
                meta=read(directory/'READY.json')
                require(meta['schema']=='ttm.semantic4x3.ready.v1' and meta['run_id']==seedid and meta['arm']==arm and meta['seed']==s and meta['step']==step and meta['study_id']==STUDY_ID and
                    meta['source_sha256']==claim['runner_sha256'] and meta['schedule_sha256']==claim['schedules_sha256'][s] and meta['env']==claim['env'], 'READY_METADATA_'+s+'_'+arm+str(step))
                chk=directory/'checkpoint.pt'
                require(chk.is_file() and chk.stat().st_size==meta['checkpoint_bytes'] and meta['checkpoint_bytes']>1000000,'CHECKPOINT_SIZE_'+s+'_'+arm+str(step))
                # Audit all journal SHA bindings; final binary SHA independent for each arm.
                done=read(armroot/f'CHUNK_{step:04d}_DONE.json')
                require(done['checkpoint_sha256']==meta['checkpoint_sha256'] and done['step']==step,'JOURNAL_DIGEST_'+s+'_'+arm+str(step))
                if step==2048:
                    require(sha_file(chk)==meta['checkpoint_sha256'],'FINAL_BINARY_SHA_'+s+'_'+arm)
                    final_digests[s+'/'+arm]=meta['checkpoint_sha256']
                count+=1
    require(count==96 and len(final_digests)==12,'READY_COUNT')
    return count,final_digests

def readback(out):
    out=Path(out).resolve(strict=True)
    require(out.name==STUDY_ID,'STUDY_RUN_ID')
    result=read(out/'RESULT.json')
    claim=read(out/'STUDY_CLAIM.json')
    require(claim['claimed'] is True and claim['study_id']==STUDY_ID,'CLAIM')
    require(result['status']=='COMPLETED_PENDING_INDEPENDENT_ADJUDICATION' and result['study_id']==STUDY_ID and
       result['seed_count']==3 and result['arms_per_seed']==4 and result['steps_per_arm']==2048 and result['targets_per_step']==4096 and
       result['h768_stories']==768 and result['h768_windows']==1000 and result['h768_targets']==186655 and
       result['bootstrap_seed']==BOOT_SEED and result['bootstrap_draws']==2000 and
       result['claim_sha256']==sha_file(out/'STUDY_CLAIM.json'),'RESULT')
    require(result['source_runner_sha256']==claim['runner_sha256'] and
       result['h768_membership_sha256']=='0ab671ae59ff4300d8257f2689261d6328afd7563c0aa66b363bc22348c1628f','RUNNER_H768_PINS')
    perfile=out/'PER_STORY_PRIVATE.json'
    require(sha_file(perfile)==result['private_per_story_sha256'],'PER_STORY_SHA')
    per=read(perfile)
    require(per['schema']=='ttm.semantic4x3.per_story.private.v1' and per['study_id']==STUDY_ID and per['h768_membership_sha256']==result['h768_membership_sha256'],'PER_STORY_META')
    counts=np.asarray(per['target_counts'],dtype=np.int64)
    require(counts.shape==(768,) and (counts>0).all() and int(counts.sum())==186655,'STORY_COUNTS')
    nll,contrasts,bs,verdict=delta_verify(per,counts)
    check_result(result,nll,contrasts,bs,verdict)
    cnt,digests=verify_readies(out,claim)
    require(not (out/'INDEPENDENT_READBACK_PUBLIC.json').exists(),'REVIEW_ALREADY_EXISTS')
    receipt={'schema':'ttm.semantic4x3.independent.public.v1',
      'study_id':STUDY_ID,'status':'PASS_INDEPENDENT_12_ARM_STORY_BOOTSTRAP_READBACK',
      'candidate_scientific_verdict':verdict,'result_sha256':sha_file(out/'RESULT.json'),
      'claim_sha256':sha_file(out/'STUDY_CLAIM.json'),'private_per_story_sha256':sha_file(perfile),
      'all_ready_metadata_count':cnt,'all_final_binary_sha256_verified':True,'final_digests':digests,
      'nll_nats_per_target':nll,'contrasts_by_seed':contrasts,'co_primary':bs,
      'model_forward_calls':0,'science_training_reexecuted':False,
      'historical_TEST_H320_H512_not_read':True}
    with (out/'INDEPENDENT_READBACK_PUBLIC.json').open('x',encoding='utf-8') as f:
        json.dump(receipt,f,indent=2,sort_keys=True,allow_nan=False)
        f.write('\n');f.flush();os.fsync(f.fileno())
    print('SEMANTIC4X3_INDEPENDENT_READBACK=PASS')
    print('SEMANTIC4X3_INDEPENDENT_SHA256='+sha_file(out/'INDEPENDENT_READBACK_PUBLIC.json'))

def fixture():
    counts=np.full(768,243,dtype=np.int64);counts[:31]+=1
    raw={}
    for s in SEEDS:
        arr=np.linspace(.7,.8,768)*counts
        raw[s]={'PT-REAL':arr,'PT-PERM':arr+.1*counts,'NULL-REAL':arr+.05*counts,'NULL-PERM':arr+.07*counts}
    per={'loss_sum_by_seed_arm':{s:{a:v.tolist() for a,v in raw[s].items()} for s in SEEDS}}
    n,d,ci,verdict=delta_verify(per,counts)
    result={'candidate_verdict':verdict,'nll_nats_per_target':n,'contrasts_by_seed':d,'co_primary':json.loads(json.dumps(ci))}
    check_result(result,n,d,ci,verdict)
    require(verdict=='PASS_SCOPED_DONOR_RESIDUAL_STRUCTURE','FIXTURE_EXPECTED_PASS')
    result['co_primary']['gamma_real']['ci95_percentile'][0]+=.1
    try:check_result(result,n,d,ci,verdict)
    except RuntimeError:pass
    else:raise RuntimeError('NEGATIVE_CI_MUTATION_FAILED')
    print(json.dumps({'schema':'ttm.semantic4x3.independent.fixture.v1','status':'PASS_6_CHECKS','models_loaded':False,'gpu_used':False,'source_data_read':False},sort_keys=True))

def main():
    p=argparse.ArgumentParser();p.add_argument('--mode',required=True,choices=['fixture','readback'])
    p.add_argument('--drive-output',default='');a=p.parse_args()
    if a.mode=='fixture':fixture()
    else:readback(a.drive_output)

if __name__=='__main__':main()
