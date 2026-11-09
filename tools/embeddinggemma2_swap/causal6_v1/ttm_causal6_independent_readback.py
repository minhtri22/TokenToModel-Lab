#!/usr/bin/env python3
"""Independent story bootstrap readback. No model load, training or forward."""
from __future__ import annotations
import argparse, hashlib, json, os
from pathlib import Path
import numpy as np

RUN='ttm_small4m_gemma2_causal6_2048x4096_free_t4_20261109_v1'
ARMS=('RR-F','RP-F','RR-A','RP-A','OR-F','OP-F')

def sha(p):
 h=hashlib.sha256()
 with Path(p).open('rb') as f:
  for x in iter(lambda:f.read(1<<20),b''):h.update(x)
 return h.hexdigest()

def require(c,s):
 if not bool(c):raise RuntimeError('HOLD_REVIEW_'+s)

def independent(vals,counts):
 rng=np.random.default_rng(2026110915);ix=rng.integers(0,512,size=(2000,512))
 nll={k:float(a.sum()/counts.sum()) for k,a in vals.items()}
 primary=vals['RP-F']-vals['RR-F']
 contrasts={'tau_D':primary,'tau_A':primary-(vals['RP-A']-vals['RR-A']),
            'tau_P':primary-(vals['OP-F']-vals['OR-F'])}
 estimates={}
 for k,d in contrasts.items():
  ci=[float(x) for x in np.quantile(d[ix].sum(axis=1)/counts[ix].sum(axis=1),[.025,.975])]
  estimates[k]={'delta_nll':float(d.sum()/counts.sum()),'ci95_percentile':ci,'ci_lower_gt_zero':ci[0]>0}
 return nll,estimates

def audit(run):
 run=Path(run).resolve(strict=True)
 require(run.name==RUN,'RUN_ID_PATH')
 claim=json.loads((run/'CLAIM.json').read_text('utf-8'))
 r=json.loads((run/'RESULT.json').read_text('utf-8'))
 p=json.loads((run/'PER_STORY_PRIVATE.json').read_text('utf-8'))
 require(claim['run_id']==r['run_id']==p['run_id']==RUN,'RUN_ID')
 require(r['schema']=='ttm.causal6.result.public.v1' and
  r['status']=='COMPLETED_PENDING_INDEPENDENT_ADJUDICATION','RESULT_STATUS')
 require(sha(run/'CLAIM.json')==r['claim_sha256'],'CLAIM_SHA')
 require(sha(run/'PER_STORY_PRIVATE.json')==r['per_story_sha256'],'PER_STORY_SHA')
 require(r['steps_per_arm']==2048 and r['targets_per_step']==4096 and r['arm_count']==6,'BUDGET')
 require(r['bootstrap_draws']==2000 and r['bootstrap_seed']==2026110915,'BOOT')
 require(claim['source_parity_C2048']=='PASS_EXACT_STATE_AND_SYNTHETIC_LOGITS','SOURCE_PARITY')
 require(r['source_runner_sha256']==claim['runner_sha256'],'SOURCE_RUNNER')
 counts=np.asarray(p['target_counts'],dtype=np.int64)
 require(counts.shape==(512,) and np.all(counts>0) and int(counts.sum())==r['target_count'],'STORY_COUNTS')
 vals={k:np.asarray(p['loss_sum_by_arm'][k],dtype=np.float64) for k in ARMS}
 require(all(x.shape==(512,) and np.isfinite(x).all() and np.all(x>=0) for x in vals.values()),'STORY_LOSS')
 for arm in ARMS:
  folder=run/'checkpoints'/arm/'step_2048'
  ready=json.loads((folder/'READY.json').read_text('utf-8'))
  require(ready['run_id']==RUN and ready['step']==2048 and ready['arm']==arm,'FINAL_READY')
  require(sha(folder/'checkpoint.pt')==ready['checkpoint_sha256'],'CHECKPOINT_SHA_'+arm)
  for milestone in range(256,2049,256):
   d=run/'checkpoints'/arm
   require((d/f'CHUNK_{milestone:04d}_START.json').is_file() and
    (d/f'CHUNK_{milestone:04d}_DONE.json').is_file() and
    (d/f'step_{milestone:04d}'/'READY.json').is_file(),'CHUNK_PROVENANCE_'+arm)
 nll,contrasts=independent(vals,counts)
 for k in ARMS:require(abs(r['nll_nats_per_target'][k]-nll[k])<1e-11,'NLL_'+k)
 for k in contrasts:
  got=r['contrasts'][k];actual=contrasts[k]
  require(abs(got['delta_nll']-actual['delta_nll'])<1e-11 and all(abs(a-b)<1e-11 for a,b in zip(got['ci95_percentile'],actual['ci95_percentile'])),'CI_'+k)
 label='PASS_SCOPED_DONOR_MAPPING_ALIGNMENT' if contrasts['tau_D']['ci_lower_gt_zero'] else 'DONOR_MAPPING_EFFECT_NOT_ESTABLISHED'
 require(label==r['scientific_candidate_verdict'],'VERDICT')
 result={'schema':'ttm.causal6.independent.public.v1','status':'PASS_INDEPENDENT_STORY_BOOTSTRAP_READBACK',
  'run_id':RUN,'scientific_verdict_candidate':label,'source_claim_sha256':sha(run/'CLAIM.json'),
  'source_result_sha256':sha(run/'RESULT.json'),'private_per_story_sha256':sha(run/'PER_STORY_PRIVATE.json'),
  'nll_nats_per_target':nll,'contrasts':contrasts,'stories':512,'arm_count':6,'targets':int(counts.sum()),
  'training_reexecuted':False,'model_forward_calls':0,'test_read':False,'old_holdout_read':False}
 with (run/'INDEPENDENT_READBACK_PUBLIC.json').open('x',encoding='utf-8') as f:
  json.dump(result,f,ensure_ascii=False,indent=2,sort_keys=True);f.write('\n');f.flush();os.fsync(f.fileno())
 print(json.dumps({'status':result['status'],'verdict':label,'receipt_sha256':sha(run/'INDEPENDENT_READBACK_PUBLIC.json')}))
 return result

def fixture():
 counts=np.full(512,100,dtype=np.int64)
 vals={k:np.ones(512,dtype=np.float64)*(2+i*.01) for i,k in enumerate(ARMS)}
 n,c=independent(vals,counts)
 assert len(n)==6 and len(c)==3 and all(np.isfinite(x['delta_nll']) for x in c.values())
 print(json.dumps({'status':'PASS_SYNTHETIC_ONLY','checks':3,'science_executed':False,'model_forward_calls':0}))

if __name__=='__main__':
 p=argparse.ArgumentParser();p.add_argument('--mode',choices=['fixture','readback'],required=True);p.add_argument('--run',default='')
 a=p.parse_args();fixture() if a.mode=='fixture' else audit(a.run)
