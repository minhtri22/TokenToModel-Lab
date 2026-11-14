#!/usr/bin/env python3
"""Prospective source-only V6 action-causal scenarios; no EVAL, TRAIN data or gold.
Independent checker is a different module; generator does not import it.
"""
from __future__ import annotations
import json,hashlib,copy
from pathlib import Path
CATS=('entity_location','causal_reasoning','rule_constraint','goal_persistence')
SEEDS=[*range(20261120,20261131),20261201]

def world():
 return {'current_time':'T0','location_agent':{'a0':'l0','a1':'l1'},
  'location_item':{'i0':'l0','i1':'l0'},'holder':{'i0':'NONE','i1':'NONE'},
  'power':{'d0':'OFF','d1':'OFF'},'trigger_fired':{'g0':False,'g1':False},
  'scheduled_at':{'g0':'NONE','g1':'NONE'},'linked_trigger':{'d0':'NONE','d1':'NONE'},
  'protected_until':{'i0':'BEFORE_T0','i1':'BEFORE_T0'},
  'defer_until':{'a0':'NONE','a1':'NONE'},
  'external_transfer_request':{'at':'NONE','item':'NONE','recipient':'NONE'}}

def setpath(w,path,val):
 a,b=path.split('.')
 w[a][b]=val

def make_case(cat,i):
 base=world(); goal={}; mechanism=''; overrides={}; flip=bool(i in (1,3,4,6))
 if cat=='entity_location':
  # Separate genuine causal mechanism arms, not a Boolean selector.
  base['scheduled_at']={'g0':'T1','g1':'T2'}
  goal={'holder.i0':'a1','location_item.i0':'l1'}
  if i in (0,7):
   mechanism='target_custody_changes_required_pickup_or_transfer_path'
   if i==7:base['holder']['i1']='a0'
   overrides={'holder.i0':('NONE','a0')}
  elif i in (1,3,4,5,6):
   mechanism='protection_guard_on_delivery_item_changes_immediate_transfer_vs_scheduled_release'
   base['holder']['i0']='a0'
   if i in (3,6):base['holder']['i1']='a0'
   cutoff='T0' if i in (5,6) else 'T1'
   if cutoff=='T0':base['scheduled_at']['g1']='NONE'
   overrides={'protected_until.i0':('BEFORE_T0',cutoff)}
  elif i==2:
   mechanism='carry_propagates_existing_held_item_location_vs_explicit_relocation'
   goal['location_item.i1']='l1'
   overrides={'holder.i1':('NONE','a0')}
 elif cat=='causal_reasoning':
  # One coherent causal-route intervention changes LINK and CLOCK route,
  # both real paths leading to fixed fired-trigger goal. No global x0.
  g='g0' if i in (0,1,4,5) else 'g1'
  d='d0' if i in (0,2,4,6) else 'd1'
  t='T1' if i in (0,1,2,4,7) else 'T2'
  mechanism='source_of_target_trigger_linked_activation_vs_scheduled_event'
  goal={f'trigger_fired.{g}':True}
  # stage A connected device -> fire via activation; stage B scheduled trigger -> fire via WAIT
  overrides={f'linked_trigger.{d}':(g,'NONE'),f'scheduled_at.{g}':('NONE',t)}
 elif cat=='rule_constraint':
  base['holder']['i0']='a0';base['scheduled_at']={'g0':'T1','g1':'T2'}
  goal={'holder.i0':'a1','location_item.i0':'l1'}
  mechanism='protection_guard_on_exact_transfer_target_changes_transfer_vs_wait_then_transfer'
  if i in (0,1,4,5):base['scheduled_at']['g0']='NONE'
  if i in (2,3,6,7):base['scheduled_at']['g1']='NONE'
  x='T1' if i in (0,1,4,5) else 'T0'
  overrides={'protected_until.i0':('BEFORE_T0',x)}
 elif cat=='goal_persistence':
  target='i0' if i in (2,3,6,7) else 'i1'
  base['holder'][target]='a0'
  base['protected_until'][target]='T0' if i in (1,3,5,7) else 'BEFORE_T0'
  if target=='i0':base['location_item']['i0']='l0'
  # Future exogenous transfer occurs at T1 or T2; minimum necessary
  # intervention is RETAIN until the request's time, not exact-goal hacking.
  goal={'maintain_holder':{'item':target,'agent':'a0','through':'T2'},
   'policy':'least_restrictive_protection_horizon_then_no_further_agent_action'}
  mechanism='request_time_changes_minimal_sufficient_protection_interval'
  overrides={'external_transfer_request.at':('T1','T2')}
  base['external_transfer_request']={'at':'T1','item':target,'recipient':'a1'}
 else:raise ValueError(cat)
 wA=copy.deepcopy(base);wB=copy.deepcopy(base)
 changes={}
 for p,(a,b) in overrides.items():
  if p.startswith('external_transfer_request.'):
   setpath(wA,p,a);setpath(wB,p,b)
  else:setpath(wA,p,a);setpath(wB,p,b)
  changes[p]={'A':a,'B':b}
 if cat=='entity_location' and 'holder.i0' in overrides:
  # If i0 is held, both holder and physical item location already cohere with a0.
  pass
 if cat=='entity_location' and 'holder.i1' in overrides:
  # both variants locate i1 at a0's location l0.
  pass
 if flip:
  wA,wB=wB,wA
  changes={k:{'A':v['B'],'B':v['A']} for k,v in changes.items()}
 split='TRAIN_DESIGN' if i<4 else 'STRUCTURAL_OOD_DESIGN'
 return {'skeleton_id':f'{cat.upper()}_{"TR" if i<4 else "OD"}{(i%4)+1:02}',
  'category':cat,'split_design':split,'structure_index':i+1,
  'mechanism_hypothesis':mechanism,'source_amendment_status':'PROSPECTIVE_UNAPPROVED',
  'world_A':wA,'world_B':wB,
  'intervention':{'type':'TASK_CAUSAL_STATE_OR_ROUTE_CHANGE','patch':changes,
  'note':'Shared goal; intervention only in declared causal source fluents. For causal_reasoning, link/schedule couple is one physical route replacement.'},
  'task':{'goal':goal,'agent':'a0','task_kind':cat,'budget_max_actions':4},
  'render_contract':{'allowed_facts':'typed world facts and shared goal only','excludes':['skeleton_id','split_design','structure_index','mechanism_hypothesis','oracle','gold','TRAIN','OOD'],
    'status':'SCHEMA_ONLY_RENDERER_NOT_IMPLEMENTED'}}

def make():
 a=[make_case(c,i) for c in CATS for i in range(8)]
 return {'schema':'ttm.d1.r1.action_causal_amendment_32_source_blueprints.v1',
 'classification':'PUBLIC_SOURCE_ONLY_NOT_SCIENCE_DATA_NOT_SEALED_EVAL',
 'operation':'TTM_SMALL4M_D1_R1_ACTION_CAUSAL_STRUCTURAL_OOD_ORACLE_AND_SEALED_CUSTODY_SINGLE_AMENDMENT_SOURCE_GATE',
 'source_commit':'1394e0abe3eae29a905b2cfe0537d4b0b9521b2b',
 'science_frozen_head':'dd52804685d186c17e600221ffb16ce78aea12ea',
 'source_review_sha256':'57a0a5086e4ef8cfae48cc368b23658ddec2a16bc3529dda2e19aadc06d98b2a',
 'seeds_frozen':SEEDS,
 'protocol_limits':{'paired_family':'UNCHANGED','statistical_thresholds':'UNCHANGED_FROM_V6',
   'six_verbs':['RELOCATE','CARRY','TRANSFER','RETAIN','WAIT','ACTIVATE'],
   'no_public_blueprint_as_eval':True,'no_private_gold':True,'no_gpu':True},
 'design_count':32,'skeletons':a}

if __name__=='__main__':
 out=Path(__file__).with_name('TTM_D1_R1_ACTION_CAUSAL_32_SOURCE_BLUEPRINTS_20261114.json')
 out.write_text(json.dumps(make(),ensure_ascii=False,sort_keys=True,indent=2)+'\n',encoding='utf-8')
 print('32_SOURCE_BLUEPRINTS_WRITTEN SHA256='+hashlib.sha256(out.read_bytes()).hexdigest())
