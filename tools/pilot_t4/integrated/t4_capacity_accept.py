#!/usr/bin/env python3
"""Independent conservative T4 capacity acceptance after private real TRAIN window statistics.

No model training, no TEST, no science permission. Pair the synthetic GPU bench
with TRUE number of valid token targets/window; never claim a budget from padded slots.
"""
from __future__ import annotations
import argparse,hashlib,json,math,os
from pathlib import Path


def file_sha(p):
 h=hashlib.sha256()
 with open(p,'rb') as f:
  for b in iter(lambda:f.read(1<<20),b''):h.update(b)
 return h.hexdigest()


def assess(cap,pack):
 if cap['schema']!='ttm.t4.capacity.synthetic.v1' or cap['science_executed'] is not False:
  raise RuntimeError('CAPACITY_REPORT_INVALID')
 if pack['schema']!='ttm.t4.private.train_val.windowpack.v1' or pack['contains_test']:
  raise RuntimeError('PACK_SCOPE_OR_TEST_INVALID')
 mean=pack['counts']['train_mean_valid_targets_per_window']
 if not 1<=mean<=256:raise RuntimeError('TRAIN_WINDOW_MEAN_INVALID')
 inflation=max(1.0,256/mean)
 # Extra guard on top of synthetic bench 25% capacity reserve.
 risk_factor=inflation*1.10
 rows=[]
 for r in cap['records']:
  projected=(r['projected_science_seconds_with_25pct_reserved']*risk_factor)
  rows.append({'precision':r['precision'],'microbatch_windows':r['microbatch_windows'],
        'gradient_accumulation':r['gradient_accumulation'],
        'synthetic_worst_seconds':r['worst_seconds'],
        'actual_window_inflation':inflation,'extra_safety_factor':1.10,
        'projected_seconds_conservative':round(projected,1),
        'vram_reserved_ratio':r['memory_reserved_ratio'],
        'passes_budget_with_real_window_shape_stats':bool(projected<=5400 and r['memory_reserved_ratio']<=.8)})
 eligible=[x for x in rows if x['passes_budget_with_real_window_shape_stats']]
 selected=min(eligible,key=lambda x:(x['projected_seconds_conservative'],x['vram_reserved_ratio'])) if eligible else None
 return {'schema':'ttm.t4.capacity.privatepack.review.v1','status':'CAPACITY_PASS_PROVISIONAL_FOR_SCIENCE_REVIEW' if selected else 'CAPACITY_HOLD',
  'science_executed':False,'no_test_used':True,'source_capacity_status':cap['status'],
  'train_scored_targets_unique':pack['counts']['train_next_token_targets_unique'],
  'effective_train_target_reuse_factor':pack['counts']['train_reuse_factor_for_4194304_target_budget'],
  'mean_train_valid_targets_per_window':mean,
  'safety_risk_factor':risk_factor,
  'candidates':rows,'selected':selected,
  'non_proven':['Cannot guarantee Colab availability or total execution speed',
   'Full 1024-step real-science runtime not executed',
   'No science permission from this reviewer']}


def main():
 p=argparse.ArgumentParser();p.add_argument('--capacity',required=True);p.add_argument('--pack-manifest',required=True);p.add_argument('--out',required=True)
 a=p.parse_args()
 out=Path(a.out)
 if out.exists():raise FileExistsError('CAPACITY_REVIEW_ALREADY_EXISTS')
 cap=json.loads(Path(a.capacity).read_text('utf8'));pack=json.loads(Path(a.pack_manifest).read_text('utf8'))
 result=assess(cap,pack)
 result['capacity_sha256']=file_sha(a.capacity);result['pack_manifest_sha256']=file_sha(a.pack_manifest)
 with out.open('x',encoding='utf8') as f:json.dump(result,f,indent=2,sort_keys=True);f.write('\n');f.flush();os.fsync(f.fileno())
 print('T4_CAPACITY_PRIVATE_PACK_REVIEW='+result['status'])
 print('T4_SCIENCE_LOCK=HOLD')

if __name__=='__main__':main()
