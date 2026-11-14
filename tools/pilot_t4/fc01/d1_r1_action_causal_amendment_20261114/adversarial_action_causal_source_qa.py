#!/usr/bin/env python3
"""New adversarial tests only; never reruns prior synthetic historical QA.
Source-only independent negative challenge of new causal blueprint checker.
"""
from __future__ import annotations
import sys,json,copy,hashlib,importlib.util,argparse
from pathlib import Path
HERE=Path(__file__).parent
spec=importlib.util.spec_from_file_location('auditor',HERE/'independent_action_causal_checker.py')
auditor=importlib.util.module_from_spec(spec);spec.loader.exec_module(auditor)

def clone(x):return copy.deepcopy(x)

def case(data,label,edit,want):
 d=clone(data);edit(d)
 try:r=auditor.audit(d)
 except Exception as e:
  actual=str(e);return {'name':label,'detected':want in actual,'check_error':actual[:180],'type':'EXCEPTION'}
 fail=';'.join(x['error'] for x in r['failed_cases'])
 if want=='NOVELTY_DUPLICATE':
  t=r['novelty_proxy']['identical_intervention_action_trace_pairs']
  yes=any(x['ood']=='ENTITY_LOCATION_OD01' and x['train']=='ENTITY_LOCATION_TR01' for x in t)
  return {'name':label,'detected':yes,'check_error':'NOVELTY_DUPLICATE' if yes else 'NOT_DETECTED','type':'NOVELTY_GRAPH_PROXY'}
 return {'name':label,'detected':want in fail,'check_error':fail[:220],'type':'PER_CASE_HOLD'}

def set_both_goal(d,goal):
 for x in d['skeletons']:
  if x['category']=='entity_location':x['task']['goal']=goal

def make():
 p=HERE/'TTM_D1_R1_ACTION_CAUSAL_32_SOURCE_BLUEPRINTS_20261114.json'
 data=json.loads(p.read_text(encoding='utf8'))
 cases=[]
 cases.append(case(data,'E01_TRIGGER_EARLY_WITHOUT_GENESIS_TRACE',lambda d:d['skeletons'][8]['world_A']['trigger_fired'].__setitem__('g0',True),'GENESIS_EARLY_FIRED'))
 cases.append(case(data,'E02_UNDECLARED_WORLD_INTERVENTION',lambda d:d['skeletons'][0]['world_A']['power'].__setitem__('d0','ON'),'GENESIS_PREACTIVATION'))
 cases.append(case(data,'E03_GLOBAL_POWER_D1_SHORTCUT',lambda d:(d['skeletons'][0]['world_A']['power'].__setitem__('d1','ON'),d['skeletons'][0]['intervention']['patch'].__setitem__('power.d1',{'A':'ON','B':'OFF'})),'GENESIS_PREACTIVATION'))
 cases.append(case(data,'E04_INVALID_HOLDER_LOCATION',lambda d:d['skeletons'][2]['world_B']['location_item'].__setitem__('i1','l1'),'HOLDER_LOCATION_INVARIANT'))
 cases.append(case(data,'E05_REQUEST_TUPLE_BAD_ROLE',lambda d:d['skeletons'][24]['world_A']['external_transfer_request'].__setitem__('recipient','a9'),'REQUEST_REFERENTS'))
 cases.append(case(data,'E06_MISSING_ONE_SKELETON',lambda d:d['skeletons'].pop(),'NOT_32'))
 cases.append(case(data,'E07_DUPLICATE_SKELETON_ID',lambda d:d['skeletons'][1].__setitem__('skeleton_id',d['skeletons'][0]['skeleton_id']),'DUPLICATE_ID'))
 cases.append(case(data,'E08_WRONG_SPLIT_DENOMINATOR',lambda d:d['skeletons'][4].__setitem__('split_design','TRAIN_DESIGN'),'DISTRIBUTION_NOT_4X4'))
 cases.append(case(data,'E09_GOAL_ALREADY_TRUE',lambda d:d['skeletons'][0]['task'].__setitem__('goal',{'power.d0':'OFF'}),'GOAL_ALREADY_SATISFIED'))
 cases.append(case(data,'E10_ARTIFICIAL_NONUNIQUE_POSTCONDITION',lambda d:d['skeletons'][0]['task'].__setitem__('goal',{'location_item.i0':'l1'}),'UNIQUE_FIRST_ACTION'))
 cases.append(case(data,'E11_GOLD_KEY_INJECTION',lambda d:d['skeletons'][0]['task'].__setitem__('answer_gold','TRANSFER'),'TASK_SCHEMA_EXACT'))
 # Intentionally clone one OOD mechanism trace from TRAIN (not a fail of typed
 # checks, but expected to be explicitly detected by nonoverlap proxy).
 def clone_train_semantics(d):
  a=next(x for x in d['skeletons'] if x['skeleton_id']=='ENTITY_LOCATION_TR01')
  b=next(x for x in d['skeletons'] if x['skeleton_id']=='ENTITY_LOCATION_OD01')
  for k in ('world_A','world_B','intervention','task'):
   b[k]=clone(a[k])
 cases.append(case(data,'E12_OOD_EQUALS_TRAIN_ACTION_CAUSAL_TRACE',clone_train_semantics,'NOVELTY_DUPLICATE'))
 # Additional metamorphic invariance check: flipping only public metadata must
 # not affect computed action truth; this is not counted as mutation negative.
 a=auditor.check_pair(data['skeletons'][0]);copy_case=clone(data['skeletons'][0]);copy_case['mechanism_hypothesis']='UNRELATED_METADATA'
 b=auditor.check_pair(copy_case)
 metamorphic={s: a[s]['first_candidates']==b[s]['first_candidates'] for s in ('A','B')}
 return {'schema':'ttm.d1.r1.action_causal_new_negative_source_qa.v1',
  'blueprints_sha256':hashlib.sha256(p.read_bytes()).hexdigest(),
  'classification':'NEW_NEGATIVE_CHECKS_NOT_OLD_13_OVER_13_OR_12_OVER_12',
  'cases':cases,'detected':sum(x['detected'] for x in cases), 'total':len(cases),
  'metadata_noncausal_metamorphic_check':metamorphic,'science_execution':False}

if __name__=='__main__':
 r=make();o=HERE/'TTM_D1_R1_ACTION_CAUSAL_NEGATIVE_QA_RECEIPT_20261114.json';o.write_text(json.dumps(r,indent=2,sort_keys=True)+'\n',encoding='utf8')
 print('NEW_NEGATIVE_DETECTED',r['detected'],'/',r['total'])
 for x in r['cases']:
  if not x['detected']:print('NOT_DETECTED',x['name'],x['check_error'][:150])
 print('METAMORPHIC',r['metadata_noncausal_metamorphic_check'])
 raise SystemExit(0 if r['detected']==r['total'] and all(r['metadata_noncausal_metamorphic_check'].values()) else 2)
