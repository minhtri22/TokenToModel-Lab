#!/usr/bin/env python3
"""Independent, bounded source-only constructive feasibility search for D1 R1.
Never imports prior generator/checker; never reads private gold or makes model calls.
Semantics physical-P1 = PROSPECTIVE; NOT frozen V6.
"""
import collections, copy, hashlib, itertools, json, pathlib, sys
from collections import deque
HERE=pathlib.Path(__file__).resolve().parent
CLOCK=('T0','T1','T2'); TT={'BEFORE_T0':-1,'T0':0,'T1':1,'T2':2,'NONE':-9}
ITEMS=('i0','i1'); AGENTS=('a0','a1'); TRIGGERS=('g0','g1'); DEVS=('d0','d1'); LOCS=('l0','l1')
CATS=('entity_location','causal_reasoning','rule_constraint','goal_persistence')

def canonical(v): return json.dumps(v,sort_keys=True,ensure_ascii=False,separators=(',',':'))

def base():
 return {'current_time':'T0','location_agent':{'a0':'l0','a1':'l1'},'location_item':{'i0':'l0','i1':'l1'},
 'holder':{'i0':'a0','i1':'a1'},'power':{'d0':'OFF','d1':'OFF'},'linked_trigger':{'d0':'NONE','d1':'NONE'},
 'scheduled_at':{'g0':'NONE','g1':'NONE'},'trigger_fired':{'g0':False,'g1':False},
 'protected_until':{'i0':'BEFORE_T0','i1':'BEFORE_T0'},'defer_until':{'a0':'NONE','a1':'NONE'},
 'external_transfer_request':{'at':'NONE','item':'NONE','recipient':'NONE'}}

def admissible(s):
 if set(s)!=set(base()) or s['current_time']!='T0':return False
 if s['location_agent']['a0']!='l0':return False
 if any(s['power'][d]!='OFF' for d in DEVS):return False
 if any(s['trigger_fired'][g] for g in TRIGGERS):return False
 if any(s['defer_until'][a]!='NONE' for a in AGENTS):return False
 if any(s['scheduled_at'][g] not in ('NONE','T1','T2') for g in TRIGGERS):return False
 if any(s['linked_trigger'][d] not in ('NONE',*TRIGGERS) for d in DEVS):return False
 active=[s['linked_trigger'][d] for d in DEVS if s['linked_trigger'][d]!='NONE']
 if len(active)!=len(set(active)):return False
 if any(s['holder'][i] not in ('NONE',*AGENTS) for i in ITEMS):return False
 if any(s['location_item'][i] not in LOCS for i in ITEMS):return False
 if any(s['location_agent'][a] not in LOCS for a in AGENTS):return False
 if any(s['protected_until'][i] not in ('BEFORE_T0',*CLOCK) for i in ITEMS):return False
 for i in ITEMS:
  if s['holder'][i]!='NONE' and s['location_item'][i]!=s['location_agent'][s['holder'][i]]:return False
 q=s['external_transfer_request']
 if q['at'] not in ('NONE','T1','T2'):return False
 if q['at']=='NONE' and (q['item']!='NONE' or q['recipient']!='NONE'):return False
 if q['at']!='NONE' and (q['item'] not in ITEMS or q['recipient'] not in AGENTS):return False
 return True

def state_valid(s):
 for i in ITEMS:
  h=s['holder'][i]
  if h!='NONE' and s['location_item'][i]!=s['location_agent'][h]:return False
 return True

def events_between(s,finish):
 s=copy.deepcopy(s);start=TT[s['current_time']];end=TT[finish]
 if end<=start:return None
 trace=[]
 for ti in range(start+1,end+1):
  now=CLOCK[ti]
  for g in TRIGGERS:
   if s['scheduled_at'][g]==now and not s['trigger_fired'][g]:
    s['trigger_fired'][g]=True;trace.append(('TRIGGER',now,g))
  req=s['external_transfer_request']
  if req['at']==now:
   target=req['item'];who=req['recipient'];h=s['holder'][target]
   why='TRANSFERRED'
   if h=='NONE':why='NO_HOLDER'
   elif h==who:why='SAME_HOLDER'
   elif TT[s['protected_until'][target]]>=ti:why='PROTECTED'
   elif s['location_agent'][h]!=s['location_agent'][who]:why='REMOTE_DENIED'
   else:s['holder'][target]=who;s['location_item'][target]=s['location_agent'][who]
   trace.append(('REQUEST',now,why))
 s['current_time']=finish;s['defer_until']={a:'NONE' for a in AGENTS}
 assert state_valid(s)
 return s,trace

def actions(s):
 t=s['current_time'];ret=[]
 for i in ITEMS:
  for l in LOCS:
   ret.extend([('RELOCATE',i,t,l),('CARRY',i,t,l)])
  ret.append(('TRANSFER',i,t,'a1'))
  for u in CLOCK:ret.append(('RETAIN',i,t,u))
 for g in TRIGGERS:
  for u in ('T1','T2'):ret.append(('WAIT',g,u,'NONE'))
 for d in DEVS:ret.append(('ACTIVATE',d,t,'NONE'))
 return ret

def step(src,act):
 verb,target,when,q=act;s=copy.deepcopy(src);t=s['current_time']
 if verb!='WAIT' and when!=t:return None
 if verb=='RELOCATE':
  if target not in ITEMS or q not in LOCS or s['holder'][target]!='NONE' or s['location_item'][target]!=s['location_agent']['a0'] or q==s['location_item'][target]:return None
  s['location_item'][target]=q
 elif verb=='CARRY':
  if target not in ITEMS or q not in LOCS or q==s['location_agent']['a0']:return None
  if s['holder'][target]=='NONE':
   if s['location_item'][target]!=s['location_agent']['a0']:return None
   s['holder'][target]='a0'
  elif s['holder'][target]!='a0':return None
  s['location_agent']['a0']=q
  for i in ITEMS:
   if s['holder'][i]=='a0':s['location_item'][i]=q
 elif verb=='TRANSFER':
  if target not in ITEMS or q!='a1' or s['holder'][target]!='a0' or s['location_agent']['a0']!=s['location_agent']['a1'] or TT[s['protected_until'][target]]>=TT[t]:return None
  s['holder'][target]='a1';s['location_item'][target]=s['location_agent']['a1']
 elif verb=='RETAIN':
  if target not in ITEMS or q not in CLOCK or s['holder'][target]!='a0' or TT[q]<TT[t] or TT[q]<=TT[s['protected_until'][target]]:return None
  s['protected_until'][target]=q
 elif verb=='WAIT':
  if target not in TRIGGERS or q!='NONE' or when not in CLOCK or TT[when]<=TT[t] or s['scheduled_at'][target]!=when or s['trigger_fired'][target]:return None
  s['defer_until']['a0']=when
  out=events_between(s,when)
  return out[0] if out else None
 elif verb=='ACTIVATE':
  if target not in DEVS or q!='NONE' or s['power'][target]!='OFF':return None
  s['power'][target]='ON';g=s['linked_trigger'][target]
  if g!='NONE':s['trigger_fired'][g]=True
 else:return None
 assert state_valid(s)
 return s

def get(s,p):
 x=s
 for k in p.split('.'):x=x[k]
 return x

def satisfies(s,g):return all(get(s,k)==v for k,v in g.items())

def shortest(s,goal,depth_limit=3,edge_cap=3500):
 """No pruning by same state without first label; enumerate all distinct shortest first-actions.
 Goal is a finite-state reachability predicate. NOT persistence safety."""
 if satisfies(s,goal):return {'status':'ALREADY_MET','depth':0,'firsts':[],'edges':0}
 frontier=[(s,None)];seen=set();edges=0
 for depth in range(1,depth_limit+1):
  nxt=[];winners=set()
  for st,first in frontier:
   for a in actions(st):
    o=step(st,a)
    if o is None:continue
    edges+=1
    if edges>edge_cap:return {'status':'RESOURCE_CAPPED','depth':None,'firsts':[],'edges':edges}
    f=first or a
    if satisfies(o,goal):winners.add(f)
    else:
     key=(canonical(o),f)
     if key not in seen:seen.add(key);nxt.append((o,f))
  if winners:return {'status':'UNIQUE' if len(winners)==1 else 'AMBIGUOUS','depth':depth,'firsts':[list(x) for x in sorted(winners)],'edges':edges}
  frontier=nxt
  if not frontier:break
 return {'status':'NO_PLAN_WITHIN_BOUND','depth':None,'firsts':[],'edges':edges}

def persistence(s,item='i0',through='T2',location_goal=None):
 """Pure safety under one selected action then no further agent actions; no tie break.
 A successful action MUST preserve custody up to through (not force any action code).
 May also require item remains at its initial location to rule out evacuation.
 """
 if s['holder'][item]!='a0':return {'status':'INITIAL_GOAL_INVALID','firsts':[]}
 hits=[]
 for a in actions(s):
  out=step(s,a)
  if out is None:continue
  if TT[out['current_time']]<TT[through]:
   e=events_between(out,through)
   if e is None:continue
   out=e[0]
  if out['holder'][item]!='a0':continue
  if location_goal and out['location_item'][item]!=location_goal:continue
  hits.append(list(a))
 return {'status':'UNIQUE' if len(hits)==1 else ('AMBIGUOUS' if hits else 'NO_PLAN'), 'firsts':hits,'success_count':len(hits)}

# Exact test declarations, NOT existing source cases. Bounded subgrammars make no global claims.
def sweep():
 records={};examples={}
 # location: current a0 l0, held/free i0, a1 same/distant, protection and destination constrained
 loc=[]
 for holder,coloc,protection,i1holder,goal_holder,goal_loc in itertools.product(('NONE','a0'),(False,True),('BEFORE_T0','T0','T1'),('NONE','a1'),('NONE','a1'),LOCS):
  s=base();s['location_agent']['a1']='l0' if coloc else 'l1';s['holder']['i0']=holder;s['location_item']['i0']='l0'
  s['holder']['i1']=i1holder;s['location_item']['i1']=s['location_agent']['a1'] if i1holder=='a1' else 'l1';s['protected_until']['i0']=protection
  if not admissible(s):continue
  goal={'holder.i0':goal_holder,'location_item.i0':goal_loc}
  r=shortest(s,goal,3)
  loc.append({'param':[holder,coloc,protection,i1holder,goal_holder,goal_loc],'result':r,'state':s,'goal':goal})
 records['entity_location']=loc
 # causal: device d0 linked g0 or none; g0 scheduled independent or not; g1 neutral; goal fired g0
 causal=[]
 for link,at,alt,g0deadline in itertools.product(('NONE','g0'),('NONE','T1','T2'),('NONE','T1','T2'),('ANY','AT_T1','AT_T2')):
  s=base();s['linked_trigger']['d0']=link;s['scheduled_at']['g0']=at;s['scheduled_at']['g1']=alt
  if not admissible(s):continue
  goal={'trigger_fired.g0':True}
  if g0deadline!='ANY':goal['current_time']='T1' if g0deadline=='AT_T1' else 'T2'
  r=shortest(s,goal,3)
  causal.append({'param':[link,at,alt,g0deadline],'result':r,'state':s,'goal':goal})
 records['causal_reasoning']=causal
 # rule: colocation, guard, trigger schedule, blocked by time; shared goal holder a1 (no arbitrary deadline)
 rules=[]
 for coloc,guard,g0,g1,i1holder in itertools.product((False,True),('BEFORE_T0','T0','T1'),('NONE','T1','T2'),('NONE','T1','T2'),('NONE','a1')):
  s=base();s['location_agent']['a1']='l0' if coloc else 'l1';s['location_item']['i1']=s['location_agent']['a1'] if i1holder=='a1' else 'l1';s['holder']['i1']=i1holder
  s['protected_until']['i0']=guard;s['scheduled_at']['g0']=g0;s['scheduled_at']['g1']=g1
  if not admissible(s):continue
  goal={'holder.i0':'a1'}
  r=shortest(s,goal,3)
  rules.append({'param':[coloc,guard,g0,g1,i1holder],'result':r,'state':s,'goal':goal})
 records['rule_constraint']=rules
 # persistence: holder i0=a0, event T1/T2 / none; recipient at same/distant location;
 # target protection and optional natural preserve-location task invariant
 ps=[]
 for threat,coloc,guard,stable,i1holder in itertools.product(('NONE','T1','T2'),(False,True),('BEFORE_T0','T0','T1'),(False,True),('NONE','a1')):
  s=base();s['location_agent']['a1']='l0' if coloc else 'l1';s['holder']['i1']=i1holder;s['location_item']['i1']=s['location_agent']['a1'] if i1holder=='a1' else 'l1'
  s['protected_until']['i0']=guard;s['external_transfer_request']={'at':threat,'item':'i0' if threat!='NONE' else 'NONE','recipient':'a1' if threat!='NONE' else 'NONE'}
  if not admissible(s):continue
  r=persistence(s,'i0','T2',s['location_item']['i0'] if stable else None)
  ps.append({'param':[threat,coloc,guard,stable,i1holder],'result':r,'state':s,'goal':{'maintain_holder':'a0','through':'T2','item':'i0','maintain_location':'l0' if stable else 'ANY'}})
 records['goal_persistence']=ps
 return records

def compact(r):
 d={'status':r['status']}
 if r.get('depth') is not None:d['depth']=r['depth']
 if r.get('firsts'):d['firsts']=r['firsts'][:5]
 if r.get('success_count') is not None:d['success_count']=r['success_count']
 return d

def audit(records):
 summary={};selected={}
 for cat,rows in records.items():
  tally=collections.Counter(x['result']['status'] for x in rows)
  unique=[x for x in rows if x['result']['status']=='UNIQUE']
  verb=collections.Counter(x['result']['firsts'][0][0] for x in unique)
  selected[cat]=[{'params':x['param'],'goal':x['goal'],'first':x['result']['firsts'][0],'depth':x['result'].get('depth'),'typed_state':x['state']} for x in unique[:6]]
  summary[cat]={'searched_scenarios':len(rows),'status_counts':dict(tally),'unique_first_verb_histogram':dict(verb),'examples_available':len(unique),'admitted_ood':0,'why_no_admission':'no complete canonical causal graph nonoverlap proof; prospective semantics unapproved; source worlds not sealed'}
 return summary,selected

def mutation_tests():
 out={}
 def mark(name,cond):out[name]='PASS' if cond else 'FAIL'
 s=base();s['holder']['i0']='a0';mark('GENESIS_VALID_T0',admissible(s))
 r=step(s,('TRANSFER','i0','T0','a1'));mark('DISTANT_TRANSFER_REJECT',r is None)
 s2=copy.deepcopy(s);s2['location_agent']['a1']='l0';s2['holder']['i1']='NONE';s2['location_item']['i1']='l1';mark('COLOCATED_TRANSFER_PASS',step(s2,('TRANSFER','i0','T0','a1')) is not None)
 s2['protected_until']['i0']='T1';mark('PROTECTION_OVERRIDES_TRANSFER',step(s2,('TRANSFER','i0','T0','a1')) is None)
 s3=copy.deepcopy(s);s3['holder']['i1']='a0';s3['location_item']['i1']='l0';z=step(s3,('CARRY','i0','T0','l1'));mark('HELD_CARRY_PROPAGATION',z is not None and z['location_item']['i0']==z['location_item']['i1']=='l1')
 mark('INVALID_RETAIN_NOOP',step(s,('RETAIN','i0','T0','BEFORE_T0')) is None)
 q=copy.deepcopy(s);q['scheduled_at']['g0']='T1';z=step(q,('WAIT','g0','T1','NONE'));mark('WAIT_TRIGGER_AND_CLOCK',z is not None and z['trigger_fired']['g0'] and z['current_time']=='T1')
 q['external_transfer_request']={'at':'T0','item':'i0','recipient':'a1'};mark('REQUEST_AT_T0_FORBIDDEN',not admissible(q))
 q=copy.deepcopy(s);q['trigger_fired']['g0']=True;mark('PRETRIGGER_NOT_INIT',not admissible(q))
 q=copy.deepcopy(s);q['external_transfer_request']={'at':'T1','item':'i0','recipient':'a1'};q['location_agent']['a1']='l0';q['holder']['i1']='NONE';q['location_item']['i1']='l1';q['protected_until']['i0']='T1';z=events_between(q,'T1')[0];mark('INCLUSIVE_PROTECTION_EVENT',z['holder']['i0']=='a0')
 q['protected_until']['i0']='BEFORE_T0';z=events_between(q,'T1')[0];mark('UNPROTECTED_EVENT_EXECUTES',z['holder']['i0']=='a1')
 # without cost and with no request, two legal RETAIN horizons both preserve simple holder safety
 q=base();q['location_agent']['a1']='l0';q['holder']['i1']='a1';q['location_item']['i1']='l0';r=persistence(q,'i0','T2',None);mark('NO_HIDDEN_RETAIN_TIEBREAK',r['status']=='AMBIGUOUS' and r['success_count']>1)
 return out

if __name__=='__main__':
 rec=sweep();summary,examples=audit(rec);negative=mutation_tests()
 output={'schema':'ttm.d1.r1.minimal_prospective_semantics_bounded_constructive_search.v1',
 'operation':'TTM_SMALL4M_D1_R1_MINIMAL_SEMANTIC_CONTRACT_FREEZE_AND_CONSTRUCTIVE_FOUR_CATEGORY_FEASIBILITY_SINGLE_REVIEW_GATE',
 'mode':'SOURCE_ONLY_NO_SCIENCE_NO_EVAL_GOLD','reference_semantics':'PROSPECTIVE_PHYSICAL_P1_NOT_FROZEN_V6',
 'bounds':{'agents':2,'items':2,'locations':2,'devices':2,'triggers':2,'time_points':3,'search_depth_max':3,'search_edges_cap':3500,'grammar':'explicit per-category crossproducts in constructive_search.py; fixed role labels and finite selected goals'},
 'category_counts':summary,'illustrative_reachable_unique_cases':examples,'new_targeted_checks':negative,
 'full_4_train_4_ood_feasibility_proven':False,'accepted_new_ood_total':0,
 'method_limitations':['bounded subgrammar is not an exhaustive upper bound for full V6','shortest-first reachability is not full persistent-goal equivalence','no full canonical action-causal graph equivalence proof','no independent external reviewer','prospective semantics not adopted','T1 renderer/parser, rights, custody not executed']}
 out=HERE/'TTM_D1_R1_BOUNDED_CONSTRUCTIVE_SEARCH_RECEIPT_20261114.json'
 out.write_text(json.dumps(output,indent=2,ensure_ascii=False)+'\n',encoding='utf8')
 print(json.dumps({'summary':summary,'targeted_check_pass':sum(v=='PASS' for v in negative.values()),'targeted_check_total':len(negative)},ensure_ascii=False))
