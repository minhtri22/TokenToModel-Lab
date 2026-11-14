#!/usr/bin/env python3
"""Independent source-only 32 causal-world checker; never imports generator, no model/gold.
Validates finite-world invariants, original V6-like 6-action transitions, search
for unique earliest valid action under fixed, category-specific shared goals.
This remains a second source implementation, NOT independent scientific reviewer.
"""
from __future__ import annotations
import sys,json,copy,hashlib,argparse,itertools,collections
from pathlib import Path
TIMES={'BEFORE_T0':-1,'T0':0,'T1':1,'T2':2,'NONE':-99}
KEYS={'current_time','location_agent','location_item','holder','power','trigger_fired',
      'scheduled_at','linked_trigger','protected_until','defer_until','external_transfer_request'}
CATS=('entity_location','causal_reasoning','rule_constraint','goal_persistence')
ITEMS=('i0','i1');AGENTS=('a0','a1');LOCS=('l0','l1');TRIGGERS=('g0','g1');DEVICES=('d0','d1')

def must(v,code):
 if not v:raise ValueError(code)

def at(s,path):
 a,b=path.split('.');return s[a][b]

def valid(s):
 must(set(s)==KEYS,'SCHEMA_STATE_KEYS')
 must(s['current_time'] in ('T0','T1','T2'),'CLOCK_DOMAIN')
 fields={'location_agent':AGENTS,'location_item':ITEMS,'holder':ITEMS,
   'power':DEVICES,'trigger_fired':TRIGGERS,'scheduled_at':TRIGGERS,
   'linked_trigger':DEVICES,'protected_until':ITEMS,'defer_until':AGENTS}
 for f,ks in fields.items():must(set(s[f])==set(ks),'SCHEMA_'+f)
 for a in AGENTS:must(s['location_agent'][a] in LOCS,'LOC_AGENT')
 for i in ITEMS:
  must(s['location_item'][i] in LOCS,'LOC_ITEM')
  must(s['holder'][i] in ('NONE',*AGENTS),'HOLDER_DOMAIN')
  must(s['protected_until'][i] in ('BEFORE_T0','T0','T1','T2'),'PROTECT_DOMAIN')
  if s['holder'][i]!='NONE':must(s['location_item'][i]==s['location_agent'][s['holder'][i]],'HOLDER_LOCATION_INVARIANT')
 for d in DEVICES:must(s['power'][d] in ('ON','OFF'),'POWER_DOMAIN')
 for g in TRIGGERS:
  must(type(s['trigger_fired'][g]) is bool,'TRIGGER_BOOL')
  must(s['scheduled_at'][g] in ('NONE','T0','T1','T2'),'TRIGGER_SCHEDULE')
 for d in DEVICES:must(s['linked_trigger'][d] in ('NONE',*TRIGGERS),'DEVICE_LINK')
 links=[v for v in s['linked_trigger'].values() if v!='NONE']
 must(len(links)==len(set(links)),'ONE_DEVICE_PER_TRIGGER')
 for a in AGENTS:must(s['defer_until'][a] in ('NONE','T0','T1','T2'),'DEFER_DOMAIN')
 q=s['external_transfer_request'];must(set(q)=={'at','item','recipient'},'REQUEST_KEYS')
 must(q['at'] in ('NONE','T0','T1','T2'),'REQUEST_WHEN')
 if q['at']=='NONE':must(q['item']=='NONE' and q['recipient']=='NONE','REQUEST_ABSENT')
 else:must(q['item'] in ITEMS and q['recipient'] in AGENTS,'REQUEST_REFERENTS')
 return True

def genesis(s):
 # Protocol candidate explicitly admits assigned custody at T0 but NO unexplained
 # pre-scheduled trigger fires/ON-linked effects or deferred agent actions.
 valid(s)
 must(s['current_time']=='T0','GENESIS_TIME')
 must(all(x is False for x in s['trigger_fired'].values()),'GENESIS_EARLY_FIRED')
 must(all(v=='OFF' for v in s['power'].values()),'GENESIS_PREACTIVATION')
 must(all(v=='NONE' for v in s['defer_until'].values()),'GENESIS_DEFER')
 must(all(s['scheduled_at'][g] not in ('T0',) for g in TRIGGERS),'GENESIS_PAST_EVENT')
 return True

def tick_to(s,end):
 s=copy.deepcopy(s);begin=TIMES[s['current_time']];stop=TIMES[end]
 must(stop>begin,'NONFUTURE_WAIT')
 for minute in range(begin+1,stop+1):
  t=('T0','T1','T2')[minute]
  for g in TRIGGERS:
   if s['scheduled_at'][g]==t:s['trigger_fired'][g]=True
  q=s['external_transfer_request']
  if q['at']==t:
   i=q['item'];rec=q['recipient']
   if s['holder'][i]!='NONE' and TIMES[s['protected_until'][i]]<minute:
    s['holder'][i]=rec;s['location_item'][i]=s['location_agent'][rec]
 s['current_time']=end
 valid(s)
 return s

def actions(s):
 t=s['current_time']
 # Complete bounded action argument space in this typed universe; no gold lookup.
 a=[]
 for i in ITEMS:
  for p in LOCS:
   a.append(('RELOCATE',i,t,p));a.append(('CARRY',i,t,p))
  for rec in AGENTS:a.append(('TRANSFER',i,t,rec))
  for end in ('T0','T1','T2'):a.append(('RETAIN',i,t,end))
 for g in TRIGGERS:
  for end in ('T1','T2'):a.append(('WAIT',g,end,'NONE'))
 for d in DEVICES:a.append(('ACTIVATE',d,t,'NONE'))
 return a

def step(s,a):
 verb,target,t,qual=a
 s=copy.deepcopy(s);now=s['current_time']
 if verb!='WAIT' and t!=now:return None
 if verb=='RELOCATE':
  if target not in ITEMS or qual not in LOCS or s['holder'][target]!='NONE' or s['location_item'][target]!=s['location_agent']['a0'] or s['location_item'][target]==qual:return None
  s['location_item'][target]=qual
 elif verb=='CARRY':
  if target not in ITEMS or qual not in LOCS or s['holder'][target]!='NONE' or s['location_item'][target]!=s['location_agent']['a0'] or s['location_agent']['a0']==qual:return None
  held=[i for i in ITEMS if s['holder'][i]=='a0' or i==target]
  s['holder'][target]='a0';s['location_agent']['a0']=qual
  for i in held:s['location_item'][i]=qual
 elif verb=='TRANSFER':
  if target not in ITEMS or qual!='a1' or s['holder'][target]!='a0' or TIMES[s['protected_until'][target]]>=TIMES[now]:return None
  s['holder'][target]='a1';s['location_item'][target]=s['location_agent']['a1']
 elif verb=='RETAIN':
  if target not in ITEMS or qual not in ('T0','T1','T2') or s['holder'][target]!='a0' or TIMES[qual]<TIMES[now]:return None
  if TIMES[qual]>TIMES[s['protected_until'][target]]:s['protected_until'][target]=qual
 elif verb=='WAIT':
  if target not in TRIGGERS or qual!='NONE' or t not in ('T1','T2') or s['trigger_fired'][target] or s['scheduled_at'][target]!=t or TIMES[t]<=TIMES[now]:return None
  s['defer_until']['a0']=t
  s=tick_to(s,t)
 elif verb=='ACTIVATE':
  if target not in DEVICES or qual!='NONE' or s['power'][target]!='OFF':return None
  s['power'][target]='ON';g=s['linked_trigger'][target]
  if g!='NONE':s['trigger_fired'][g]=True
 else:raise ValueError('UNKNOWN_ACTION')
 valid(s)
 return s

def canon(s):return json.dumps(s,sort_keys=True,separators=(',',':'))

def goal_done(s,goal):return all(at(s,p)==v for p,v in goal.items())

def search(s,goal,depth_limit=4):
 # Breadth-first exhaustive shortest-plan search; report all distinct first actions
 # at minimal action depth. Avoid plan-order and lexicographic tie-breaking.
 must(not goal_done(s,goal),'GOAL_ALREADY_SATISFIED')
 current=[(s,())];seen={canon(s):0}
 for depth in range(1,depth_limit+1):
  nxt=[];finished=[]
  for state,plan in current:
   for a in actions(state):
    ns=step(state,a)
    if ns is None:continue
    cand=plan+(a,)
    if goal_done(ns,goal):finished.append(cand)
    else:
     key=canon(ns)
     if seen.get(key,depth)>=depth:nxt.append((ns,cand));seen[key]=depth
  if finished:
   firsts={p[0] for p in finished}
   return {'depth':depth,'first_candidates':sorted(firsts),'plan_count_at_min_depth':len(finished),
    'example_plan':[list(x) for x in finished[0]]}
  current=nxt
 return {'depth':None,'first_candidates':[],'plan_count_at_min_depth':0,'example_plan':[]}

def persistence_oracle(s,task):
 item=task['goal']['maintain_holder']['item'];agent=task['goal']['maintain_holder']['agent']
 must(s['holder'][item]==agent,'PERSISTENCE_GENESIS_HOLDER')
 # Independent safety monitor for NO FURTHER AGENT ACTIONS after proposed one.
 found=[]
 for a in actions(s):
  after=step(s,a)
  if after is None:continue
  ok=True;cur=after
  if cur['holder'][item]!=agent:ok=False
  if cur['current_time']!='T2':
   for n in range(TIMES[cur['current_time']]+1,3):
    cur=tick_to(cur,('T0','T1','T2')[n])
    if cur['holder'][item]!=agent:ok=False
  if ok:found.append(a)
 # Task explicitly pre-registers minimum necessary protection duration;
 # penalize unrelated actions and overlong policy lock-up.
 retains=[a for a in found if a[0]=='RETAIN' and a[1]==item]
 if not retains:return {'valid':False,'reason':'NO_RETAIN_SUCCESS','candidates':found}
 min_end=min(TIMES[a[3]] for a in retains)
 best=[a for a in retains if TIMES[a[3]]==min_end]
 return {'valid':len(best)==1,'first_candidates':sorted(best),
  'depth':1,'cost_tiebreak':'minimum_protection_horizon_predeclared',
  'feasible_retain':[list(a) for a in retains],
  'alternative_successful_nonretain':[list(a) for a in found if a[0]!='RETAIN'],
  'event_time':s['external_transfer_request']['at']}

def check_pair(sk):
 must(set(sk)=={'skeleton_id','category','split_design','structure_index','mechanism_hypothesis','source_amendment_status','world_A','world_B','intervention','task','render_contract'},'BLUEPRINT_SCHEMA_UNKNOWN_FIELDS')
 cat=sk['category'];must(cat in CATS,'BAD_CATEGORY')
 A=sk['world_A'];B=sk['world_B'];genesis(A);genesis(B)
 task=sk['task'];must(set(task)=={'agent','goal','task_kind','budget_max_actions'},'TASK_SCHEMA_EXACT')
 must(task['agent']=='a0','ACTOR_ROLE')
 must(task['task_kind']==cat,'TASK_CLASS')
 # Every actual changed field must equal exactly the logged intervention.
 change={}
 for f in KEYS:
  if isinstance(A[f],dict):
   for k in A[f]:
    if A[f][k]!=B[f][k]:change[f+'.'+k]={'A':A[f][k],'B':B[f][k]}
  elif A[f]!=B[f]:change[f]={'A':A[f],'B':B[f]}
 must(change==sk['intervention']['patch'],'INTERVENTION_UNDECLARED_OR_MISSING')
 must(0<len(change)<=2,'INTERVENTION_SIZE')
 must(all('power.d1'!=p for p in change),'REGRESSION_GLOBAL_X0')
 res={}
 for side,s in (('A',A),('B',B)):
  if cat=='goal_persistence':res[side]=persistence_oracle(s,task)
  else:res[side]=search(s,task['goal'],task['budget_max_actions'])
  must(len(res[side]['first_candidates'])==1,'UNIQUE_FIRST_ACTION_'+cat+'_'+sk['skeleton_id']+'_'+side+':'+str(res[side]))
 must(res['A']['first_candidates'][0]!=res['B']['first_candidates'][0],'A_B_GOLD_SAME')
 return {'skeleton_id':sk['skeleton_id'],'category':cat,'split_design':sk['split_design'],
  'changed_fields':sorted(change),'A':res['A'],'B':res['B'],
  'first_action_diff':True,'source_only':True}

def audit(data):
 must(data['classification']=='PUBLIC_SOURCE_ONLY_NOT_SCIENCE_DATA_NOT_SEALED_EVAL','WRONG_SCOPE')
 seq=data['skeletons'];must(len(seq)==32,'NOT_32')
 ids=[s['skeleton_id'] for s in seq];must(len(set(ids))==32,'DUPLICATE_ID')
 out=[];failed=[]
 for s in seq:
  try:out.append(check_pair(s))
  except Exception as e:failed.append({'skeleton_id':s['skeleton_id'],'error':str(e)})
 counts={c:{'TRAIN_DESIGN':sum(s['category']==c and s['split_design']=='TRAIN_DESIGN' for s in seq),
     'STRUCTURAL_OOD_DESIGN':sum(s['category']==c and s['split_design']=='STRUCTURAL_OOD_DESIGN' for s in seq)} for c in CATS}
 must(all(v==4 for x in counts.values() for v in x.values()),'DISTRIBUTION_NOT_4X4')
 lookup={}
 for c in CATS:
  records=[x for x in out if x['category']==c]
  train=[x for x in records if x['split_design']=='TRAIN_DESIGN']
  ood=[x for x in records if x['split_design']=='STRUCTURAL_OOD_DESIGN']
  # Trivial baseline: one category/side action learned from TRAIN majority.
  winners={}
  for side in ('A','B'):
   vals=[tuple(x[side]['first_candidates'][0]) for x in train]
   if vals:winners[side]=collections.Counter(vals).most_common(1)[0][0]
  lookup[c]={'train_a_b_majority':{k:list(v) for k,v in winners.items()},
   'ood_sides_correct':sum(tuple(x[side]['first_candidates'][0])==winners.get(side,()) for x in ood for side in ('A','B')),
   'ood_sides_total':len(ood)*2}
 # Source-only novelty proxy excludes IDs and benign role aliases: canonical
 # action-order causal traces and exact intervention field path, not graph shape.
 signatures={}
 for r in out:
  def plan_shape(side):
   if r['category']=='goal_persistence':return tuple(r[side]['first_candidates'][0][0:1]+r[side]['first_candidates'][0][3:4])
   return tuple(x[0] for x in r[side]['example_plan'])
  signatures[r['skeleton_id']]={'changed_fields':r['changed_fields'],
    'A_trace':plan_shape('A'),'B_trace':plan_shape('B')}
 overlaps=[];pairs=0
 for c in CATS:
  tr=[r for r in out if r['category']==c and r['split_design']=='TRAIN_DESIGN']
  od=[r for r in out if r['category']==c and r['split_design']=='STRUCTURAL_OOD_DESIGN']
  for x in tr:
   for y in od:
    pairs+=1
    if signatures[x['skeleton_id']]==signatures[y['skeleton_id']]:
     overlaps.append({'train':x['skeleton_id'],'ood':y['skeleton_id'],'reason':'SAME_INTERVENTION_AND_ACTION_CAUSAL_TRACE'})
 return {'schema':'ttm.d1.r1.action_causal_checker_receipt.v1',
  'mode':'PUBLIC_SOURCE_ONLY_INDEPENDENT_IMPLEMENTATION_NO_MODEL_NO_EVAL',
  'input_sha256':None,'source_protocol':'V6_FROZEN_PLUS_PROSPECTIVE_AMENDMENT_NOT_APPROVED',
  'verified_blueprints':len(out),'expected_blueprints':32,'failed_cases':failed,'records':out,
  'counts':counts,'category_side_shortcut_baseline':lookup,
  'novelty_proxy':{'pairs':pairs,'identical_intervention_action_trace_pairs':overlaps,
     'full_semantic_graph_nonisomorphism':'NOT_PROVEN_BY_THIS_CHECKER'},
  'independent_person_reviewer':'NOT_EXECUTED',
  'decision':'HOLD_PENDING_CONSTRUCT_AND_ORACLE_REVIEW' if failed or overlaps else 'HOLD_DISTINCT_SCIENTIFIC_REVIEW_REQUIRED'}

def main():
 ap=argparse.ArgumentParser();ap.add_argument('blueprints');ap.add_argument('--out');ns=ap.parse_args()
 path=Path(ns.blueprints);data=json.loads(path.read_text(encoding='utf8'));r=audit(data)
 r['input_sha256']=hashlib.sha256(path.read_bytes()).hexdigest()
 if ns.out:Path(ns.out).write_text(json.dumps(r,sort_keys=True,indent=2,ensure_ascii=False)+'\n',encoding='utf8')
 print('BLUEPRINTS_VERIFIED',r['verified_blueprints'],'FAILURES',len(r['failed_cases']))
 for f in r['failed_cases'][:30]:print('FAILED',f['skeleton_id'],f['error'][:250])
 print('SHORTCUT_OOD',sum(x['ood_sides_correct'] for x in r['category_side_shortcut_baseline'].values()),'/',sum(x['ood_sides_total'] for x in r['category_side_shortcut_baseline'].values()))
 print('TRACE_OVERLAPS',len(r['novelty_proxy']['identical_intervention_action_trace_pairs']))
 print('DESIGN',r['decision'])
 if r['failed_cases']:raise SystemExit(2)

if __name__=='__main__':main()
