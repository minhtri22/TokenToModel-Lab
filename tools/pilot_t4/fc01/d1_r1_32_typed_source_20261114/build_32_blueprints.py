#!/usr/bin/env python3
"""Generate 32 *PUBLIC DESIGN BLUEPRINT* ASTs, never science TRAIN/EVAL/gold.
No random seeds or training: deterministic, source-only post-review proposal.
CAUTION: Output must NOT be used as the sealed structural-OOD evaluation dataset.
"""
from __future__ import annotations
import hashlib, itertools, json
from pathlib import Path

CATEGORIES=('entity_location','causal_reasoning','rule_constraint','goal_persistence')
# Four TRAIN and four proposed structural-OOD patterns, frozen locally in this packet.
# Each expression depends on all four typed observations, and differs in truth table.
# Leaf x0 is the only A/B intervention. Inputs are derived from world state.
F={
 'TR01':('AND',('AND','x0','x1'),('AND','x2','x3')),
 'TR02':('AND','x0',('OR','x1',('AND','x2','x3'))),
 'TR03':('AND','x0',('XOR','x1',('AND','x2','x3'))),
 'TR04':('AND',('AND','x0',('OR','x1','x2')),'x3'),
 'OD01':('AND','x0',('OR','x1',('XOR','x2','x3'))),
 'OD02':('AND',('AND','x0','x1'),('OR','x2','x3')),
 'OD03':('AND',('AND','x0',('XOR','x1','x2')),'x3'),
 'OD04':('AND','x0',('OR',('AND','x1','x2'),'x3')),
}
# All observations are finite, typed predicates over actual state fluents.
# The policy DAG is an explicit *proposed task-goal amendment*, not a new world fluent.
OBS={
 'entity_location':('power(d1)==ON','trigger_fired(g1)','protected_until(i1)>=T1','holder(i1)==a1'),
 'causal_reasoning':('power(d1)==ON','trigger_fired(g1)','protected_until(i1)>=T1','holder(i1)==a1'),
 'rule_constraint':('power(d1)==ON','trigger_fired(g0)','protected_until(i1)>=T1','holder(i1)==a1'),
 'goal_persistence':('power(d1)==ON','trigger_fired(g0)','protected_until(i0)>=T1','holder(i0)==a1'),
}

def truth(expr, bits):
 if isinstance(expr,str):return bool(bits[int(expr[1])])
 op,x,y=expr
 a,b=truth(x,bits),truth(y,bits)
 return {'AND':a and b,'OR':a or b,'XOR':a!=b}[op]

def graph(expr, category):
 nodes=[];edges=[]
 def walk(ex):
  i='n'+str(len(nodes))
  if isinstance(ex,str):
   nodes.append({'id':i,'kind':'typed_observation','input':ex,'predicate':OBS[category][int(ex[1])]})
  else:
   nodes.append({'id':i,'kind':'logic_gate','operator':ex[0]})
   for j,c in enumerate(ex[1:]):
    child=walk(c);edges.append({'from':child,'to':i,'port':j})
  return i
 root=walk(expr)
 return {'root':root,'nodes':nodes,'edges':edges,'semantics':'acyclic typed boolean dependency DAG; graph root selects one-step goal predicate'}

def base_state(cat,bits):
 s={'current_time':'T0','location_agent':{'a0':'l0','a1':'l1'},'location_item':{'i0':'l0','i1':'l0'},
    'holder':{'i0':'NONE','i1':'NONE'},'power':{'d0':'OFF','d1':'ON' if bits[0] else 'OFF'},
    'trigger_fired':{'g0':False,'g1':False},'scheduled_at':{'g0':'T1','g1':'T2'},
    'linked_trigger':{'d0':'g0','d1':'NONE'},
    'protected_until':{'i0':'BEFORE_T0','i1':'BEFORE_T0'},
    'defer_until':{'a0':'NONE','a1':'NONE'},
    'external_transfer_request':{'at':'NONE','item':'NONE','recipient':'NONE'}}
 if cat=='entity_location':
  s['trigger_fired']['g1']=bool(bits[1]); s['protected_until']['i1']='T1' if bits[2] else 'BEFORE_T0'
  if bits[3]:s['holder']['i1']='a1';s['location_item']['i1']='l1'
 elif cat=='causal_reasoning':
  s['trigger_fired']['g1']=bool(bits[1]); s['protected_until']['i1']='T1' if bits[2] else 'BEFORE_T0'
  if bits[3]:s['holder']['i1']='a1';s['location_item']['i1']='l1'
 elif cat=='rule_constraint':
  s['holder']['i0']='a0'; s['trigger_fired']['g0']=bool(bits[1]);s['protected_until']['i1']='T1' if bits[2] else 'BEFORE_T0'
  if bits[3]:s['holder']['i1']='a1';s['location_item']['i1']='l1'
 elif cat=='goal_persistence':
  s['holder']['i1']='a0';s['trigger_fired']['g0']=bool(bits[1]);s['protected_until']['i0']='T1' if bits[2] else 'BEFORE_T0'
  if bits[3]:s['holder']['i0']='a1';s['location_item']['i0']='l1'
  s['external_transfer_request']={'at':'T1','item':'i1','recipient':'a1'}
 else: raise ValueError(cat)
 return s

def task(cat):
 if cat=='entity_location':
  return {'agent':'a0','target':'i0','task_kind':'goal_from_boolean_dependency',
          'goal_when_true':{'location_item.i0':'l1','holder.i0':'a0','current_time':'T0'},
          'goal_when_false':{'location_item.i0':'l1','holder.i0':'NONE','current_time':'T0'},
          'interpretation':'choose transport custody from four typed observations; two actions are feasible'}
 if cat=='causal_reasoning':
  return {'agent':'a0','target':'g0','task_kind':'goal_from_boolean_dependency',
          'goal_when_true':{'trigger_fired.g0':True,'power.d0':'ON','current_time':'T0'},
          'goal_when_false':{'trigger_fired.g0':True,'power.d0':'OFF','current_time':'T1'},
          'interpretation':'choose ACTIVATE linked device now vs WAIT for scheduled trigger'}
 if cat=='rule_constraint':
  return {'agent':'a0','target':'i0','task_kind':'goal_from_boolean_dependency',
          'goal_when_true':{'holder.i0':'a0','current_time':'T2'},
          'goal_when_false':{'holder.i0':'a1','current_time':'T0'},
          'interpretation':'a typed priority rule gates immediate transfer vs deferral to an allowed trigger; protected_until guard still enforced'}
 if cat=='goal_persistence':
  return {'agent':'a0','target':'i1','task_kind':'goal_from_boolean_dependency',
          'goal_when_true':{'protected_until.i1':'T2','holder.i1':'a0','current_time':'T0'},
          'goal_when_false':{'protected_until.i1':'T1','holder.i1':'a0','current_time':'T0'},
          'interpretation':'deadline of accepted protection changes with goal evidence; T1 transfer request is blocked by both'}
 raise ValueError(cat)

def make():
 out=[]
 for cat in CATEGORIES:
  for k,expr in F.items():
   viable=[(b,c,d) for b,c,d in itertools.product((False,True),repeat=3)
           if truth(expr,(True,b,c,d)) and not truth(expr,(False,b,c,d))]
   assert viable, (cat,k)
   bcd=viable[0]
   # Opposite A/B differ in exactly ONE typed, state-level source observation.
   A=(True,*bcd);B=(False,*bcd)
   split='TRAIN' if k.startswith('TR') else 'STRUCTURAL_OOD_BLUEPRINT'
   out.append({'skeleton_id':f'{cat.upper()}_{k}', 'category':cat,'split_design':split,
     'state_A':base_state(cat,A),'state_B':base_state(cat,B),
     'intervention':{'condition_A':{'observed_input':'x0','value':True},
                     'condition_B':{'observed_input':'x0','value':False},
                     'invariant':'only typed predicate power(d1)==ON flips, with all other state fluents equal'},
     'task':task(cat),'policy_graph':graph(expr,cat),
     'design_status':'PUBLIC_SOURCE_ONLY_NOT_SCIENCE_TRAIN_EVAL_DATA_OR_GOLD',
     'semantic_graph_claim':'nonisomorphism alone insufficient; checker must verify truth-table disagreement under reachable typed state'})
 data={'schema':'ttm.d1.r1.typed_32_structural_blueprints.v1','classification':'PUBLIC_SOURCE_ONLY_DESIGN_PROTOTYPE_NOT_DATASET_NOT_EVAL_GOLD',
       'operation':'TTM_SMALL4M_D1_R1_32_TYPED_SKELETON_STRUCTURE_ORACLE_NONOVERLAP_SINGLE_SOURCE_REVIEW',
       'provenance':{'frozen_science_head':'dd52804685d186c17e600221ffb16ce78aea12ea',
          'candidate_evidence_commit':'553f1d6db9c2d5572a7e664b64a32e9eaf977f88',
          'candidate_sha256':'e05774d9f0a155e19f70574260be839f1f0634bdfce2399ab2a67622dbc214a5',
          'seed_array_unmodified':'20261120..20261130,20261201'},
       'sealed_EVAL_material':'NOT_CREATED_NOT_OPENED',
       'production_rights_and_custodian':'NOT_VERIFIED',
       'source_new_amendment':'typed boolean evidence dependency graph as source-only policy goal; requires independent scientific protocol review',
       'counts':{'categories':4,'train_blueprints_per_category':4,'ood_blueprints_per_category':4,'total':32},'skeletons':out}
 return data

if __name__=='__main__':
 out=Path(__file__).with_name('TTM_D1_R1_TYPED_32_SOURCE_BLUEPRINTS_20261114.json')
 out.write_text(json.dumps(make(),indent=2,ensure_ascii=False,sort_keys=True)+'\n',encoding='utf-8')
 print('BLUEPRINT_COUNT=32 SHA256='+hashlib.sha256(out.read_bytes()).hexdigest())
