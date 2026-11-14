#!/usr/bin/env python3
"""Standalone source-only auditor; does NOT import generator or use embedded gold.
Validates actual 32 typed ASTs and enumerates all 6-verb actions for each A/B.
This is independent *code path*, NOT a distinct external scientific reviewer.
"""
from __future__ import annotations
import argparse,copy,hashlib,itertools,json,sys
from pathlib import Path

CATS=('entity_location','causal_reasoning','rule_constraint','goal_persistence')
ITEMS=('i0','i1'); AGENTS=('a0','a1'); LOCS=('l0','l1'); DEVS=('d0','d1'); TRIGS=('g0','g1')
TIME={'BEFORE_T0':-1,'T0':0,'T1':1,'T2':2,'NONE':-99}
OBS={
 'entity_location':('power(d1)==ON','trigger_fired(g1)','protected_until(i1)>=T1','holder(i1)==a1'),
 'causal_reasoning':('power(d1)==ON','trigger_fired(g1)','protected_until(i1)>=T1','holder(i1)==a1'),
 'rule_constraint':('power(d1)==ON','trigger_fired(g0)','protected_until(i1)>=T1','holder(i1)==a1'),
 'goal_persistence':('power(d1)==ON','trigger_fired(g0)','protected_until(i0)>=T1','holder(i0)==a1'),
}
REQUIRED={'current_time','location_agent','location_item','holder','power','trigger_fired','scheduled_at','linked_trigger','protected_until','defer_until','external_transfer_request'}

def require(ok,code):
 if not ok:raise AssertionError(code)

def observe(s,expr):
 if expr=='power(d1)==ON':return s['power']['d1']=='ON'
 if expr=='trigger_fired(g1)':return s['trigger_fired']['g1']
 if expr=='trigger_fired(g0)':return s['trigger_fired']['g0']
 if expr=='protected_until(i1)>=T1':return TIME[s['protected_until']['i1']]>=1
 if expr=='protected_until(i0)>=T1':return TIME[s['protected_until']['i0']]>=1
 if expr=='holder(i1)==a1':return s['holder']['i1']=='a1'
 if expr=='holder(i0)==a1':return s['holder']['i0']=='a1'
 raise AssertionError('UNKNOWN_SOURCE_PREDICATE:'+expr)

def invariant(s):
 require(set(s)==REQUIRED,'STATE_MISSING_EXTRA_FLUENTS')
 require(s['current_time'] in ('T0','T1','T2'),'CLOCK_RANGE')
 for key,keys in [('location_agent',AGENTS),('location_item',ITEMS),('holder',ITEMS),('power',DEVS),('trigger_fired',TRIGS),('scheduled_at',TRIGS),('linked_trigger',DEVS),('protected_until',ITEMS),('defer_until',AGENTS)]:
  require(set(s[key])==set(keys),'STATE_DOMAIN_KEY_'+key)
 for a in AGENTS:require(s['location_agent'][a] in LOCS,'AGENT_LOCATION_TYPE')
 for i in ITEMS:
  require(s['location_item'][i] in LOCS,'ITEM_LOCATION_TYPE')
  require(s['holder'][i] in (*AGENTS,'NONE'),'HOLDER_TYPE')
  require(s['protected_until'][i] in ('BEFORE_T0','T0','T1','T2'),'PROTECTION_TYPE')
  if s['holder'][i]!='NONE':require(s['location_item'][i]==s['location_agent'][s['holder'][i]],'HOLDER_LOCATION_INVARIANT')
 for d in DEVS:require(s['power'][d] in ('OFF','ON'),'POWER_TYPE')
 require(all(isinstance(s['trigger_fired'][g],bool) for g in TRIGS),'BOOL_TYPE')
 require(all(s['scheduled_at'][g] in ('T0','T1','T2','NONE') for g in TRIGS),'SCHEDULE_TYPE')
 require(all(s['linked_trigger'][d] in (*TRIGS,'NONE') for d in DEVS),'LINK_TYPE')
 require(len([v for v in s['linked_trigger'].values() if v!='NONE'])==len(set(v for v in s['linked_trigger'].values() if v!='NONE')),'LINK_DUPLICATE')
 for a in AGENTS:require(s['defer_until'][a] in ('NONE','T0','T1','T2'),'DEFER_TYPE')
 q=s['external_transfer_request'];require(set(q)=={'at','item','recipient'},'REQUEST_KEY_TYPE')
 require(q['at'] in ('NONE','T0','T1','T2'),'REQUEST_TIME_TYPE')
 if q['at']=='NONE': require(q['item']=='NONE' and q['recipient']=='NONE','REQUEST_ABSENT_TYPE')
 else:require(q['item'] in ITEMS and q['recipient'] in AGENTS,'REQUEST_TUPLE_TYPE')
 return True

def eval_graph(g,state):
 nodes={n['id']:n for n in g['nodes']};require(len(nodes)==len(g['nodes']),'DUPLICATE_GRAPH_NODE')
 require(g['root'] in nodes,'MISSING_ROOT')
 incoming={k:[] for k in nodes}
 for e in g['edges']:
  require(e['from'] in nodes and e['to'] in nodes,'DANGLING_EDGE')
  require(e['port'] in (0,1),'BAD_EDGE_PORT');incoming[e['to']].append((e['port'],e['from']))
 active=set();done={}
 def walk(k):
  require(k not in active,'GRAPH_CYCLE')
  if k in done:return done[k]
  n=nodes[k];active.add(k)
  if n['kind']=='typed_observation':
   require(not incoming[k],'LEAF_HAS_INPUT')
   require(n['input'] in ('x0','x1','x2','x3'),'LEAF_ALIAS')
   require(n['predicate']==OBS[state['category']][int(n['input'][1])],'LEAF_PREDICATE_MISMATCH')
   v=observe(state['world'],n['predicate'])
  else:
   require(n['kind']=='logic_gate' and n['operator'] in ('AND','OR','XOR'),'UNSUPPORTED_GATE')
   pairs=sorted(incoming[k]);require(len(pairs)==2 and [a for a,_ in pairs]==[0,1],'NONBINARY_GATE')
   v0=walk(pairs[0][1]);v1=walk(pairs[1][1]);op=n['operator'];v={'AND':v0 and v1,'OR':v0 or v1,'XOR':v0!=v1}[op]
  active.remove(k);done[k]=v;return v
 root=walk(g['root']);require(len(done)==len(nodes),'UNREACHABLE_GRAPH_NODES')
 require(len([n for n in nodes.values() if n['kind']=='typed_observation'])==4,'LEAF_COUNT')
 require(set(n['input'] for n in nodes.values() if n['kind']=='typed_observation')=={'x0','x1','x2','x3'},'LEAF_SET')
 return root

def eval_bits(g,bits):
 # Symbolic evaluator independently separated from world predicate extraction.
 nodes={n['id']:n for n in g['nodes']};children={k:{} for k in nodes}
 for e in g['edges']:children[e['to']][e['port']]=e['from']
 def f(k):
  n=nodes[k]
  if n['kind']=='typed_observation':return bool(bits[int(n['input'][1])])
  a,b=f(children[k][0]),f(children[k][1]);return (a and b) if n['operator']=='AND' else ((a or b) if n['operator']=='OR' else a !=b)
 return f(g['root'])

def graph_canonical(g):
 # Rooted typed-tree canonical encoding; both ports are commutative here.
 nodes={n['id']:n for n in g['nodes']};children={k:[] for k in nodes}
 for e in g['edges']: children[e['to']].append(e['from'])
 def encode(k):
  n=nodes[k]
  if n['kind']=='typed_observation':return ('P',n['predicate'])
  return ('G',n['operator'],tuple(sorted((encode(ch) for ch in children[k]),key=str)))
 return str(encode(g['root']))

def advance(s,finish):
 s=copy.deepcopy(s);start=TIME[s['current_time']];end=TIME[finish]
 require(end>start,'TIME_NOT_ADVANCE')
 for t in range(start+1,end+1):
  now=('T0','T1','T2')[t]
  for g in TRIGS:
   if s['scheduled_at'][g]==now:s['trigger_fired'][g]=True
  req=s['external_transfer_request']
  if req['at']==now:
   item=req['item'];to=req['recipient'];guard=s['protected_until'][item]
   if s['holder'][item]!='NONE' and TIME[guard]<t:
    s['holder'][item]=to;s['location_item'][item]=s['location_agent'][to]
 s['current_time']=finish;invariant(s);return s

def apply(s,act):
 a,verb,target,at,qual=act
 s=copy.deepcopy(s);t=s['current_time']
 if a!='a0' or at not in ('T0','T1','T2'):return None
 if verb!='WAIT' and at!=t:return None
 if verb=='RELOCATE':
  if target not in ITEMS or qual not in LOCS or s['holder'][target]!='NONE' or s['location_item'][target]!=s['location_agent'][a] or s['location_item'][target]==qual:return None
  s['location_item'][target]=qual
 elif verb=='CARRY':
  if target not in ITEMS or qual not in LOCS or s['holder'][target]!='NONE' or s['location_item'][target]!=s['location_agent'][a] or s['location_agent'][a]==qual:return None
  held=[i for i in ITEMS if s['holder'][i]==a or i==target];s['holder'][target]=a;s['location_agent'][a]=qual
  for i in held:s['location_item'][i]=qual
 elif verb=='TRANSFER':
  if target not in ITEMS or qual not in AGENTS or qual==a or s['holder'][target]!=a or TIME[s['protected_until'][target]]>=TIME[t]:return None
  s['holder'][target]=qual;s['location_item'][target]=s['location_agent'][qual]
 elif verb=='RETAIN':
  if target not in ITEMS or qual not in ('T0','T1','T2') or s['holder'][target]!=a or TIME[qual]<TIME[t]:return None
  if TIME[qual]>TIME[s['protected_until'][target]]:s['protected_until'][target]=qual
 elif verb=='WAIT':
  if target not in TRIGS or qual!='NONE' or s['trigger_fired'][target] or s['scheduled_at'][target]!=at or TIME[at]<=TIME[t]:return None
  s['defer_until'][a]=at;s=advance(s,at)
 elif verb=='ACTIVATE':
  if target not in DEVS or qual!='NONE' or s['power'][target]!='OFF':return None
  s['power'][target]='ON';linked=s['linked_trigger'][target]
  if linked!='NONE':s['trigger_fired'][linked]=True
 else:return None
 invariant(s)
 return s

def enumerate_actions(s):
 t=s['current_time'];actions=[]
 for i in ITEMS:
  for l in LOCS:
   for v in ('RELOCATE','CARRY'):actions.append(('a0',v,i,t,l))
  for a in AGENTS:actions.append(('a0','TRANSFER',i,t,a))
  for until in ('T0','T1','T2'):actions.append(('a0','RETAIN',i,t,until))
 for g in TRIGS:
  for future in ('T1','T2'):actions.append(('a0','WAIT',g,future,'NONE'))
 for d in DEVS:actions.append(('a0','ACTIVATE',d,t,'NONE'))
 return actions

def get(state,path):
 for step in path.split('.'):state=state[step]
 return state

def audit_one(sk):
 cat=sk['category'];require(cat in CATS,'UNKNOWN_CATEGORY')
 require(sk['split_design'] in ('TRAIN','STRUCTURAL_OOD_BLUEPRINT'),'BAD_SPLIT')
 task=sk['task'];require(task['agent']=='a0','ACTOR_DRIFT')
 for side in ('A','B'):invariant(sk['state_'+side])
 require(set(sk['state_A'])==set(sk['state_B']),'AB_STATE_SCHEMA')
 for k in sk['state_A']:
  if k=='power':
   require(sk['state_A'][k]['d1']=='ON' and sk['state_B'][k]['d1']=='OFF','ONLY_X0_INTERVENTION')
   require(sk['state_A'][k]['d0']==sk['state_B'][k]['d0'],'AB_D0_DRIFT')
  else:require(sk['state_A'][k]==sk['state_B'][k],'AB_UNDECLARED_INTERVENTION_'+k)
 result={}
 for side in ('A','B'):
  s=sk['state_'+side];v=eval_graph(sk['policy_graph'],{'category':cat,'world':s})
  require(v==(side=='A'),'AB_BOOLEAN_POLICY_NOT_FLIPPED')
  goal=task['goal_when_true'] if v else task['goal_when_false']
  legal=[];wins=[]
  for act in enumerate_actions(s):
   ss=apply(s,act)
   if ss is None:continue
   legal.append(act)
   if all(get(ss,p)==want for p,want in goal.items()):wins.append(act)
  require(len(wins)==1,f'ORACLE_NOT_UNIQUE:{sk["skeleton_id"]}:{side}:{wins}')
  assert wins[0] in legal
  if cat=='entity_location':require(wins[0][1] in ('RELOCATE','CARRY'),'WRONG_ENTITY_VERB')
  elif cat=='causal_reasoning':require(wins[0][1] in ('ACTIVATE','WAIT'),'WRONG_CAUSAL_VERB')
  elif cat=='rule_constraint':require(wins[0][1] in ('TRANSFER','WAIT'),'WRONG_RULE_VERB')
  elif cat=='goal_persistence':
   require(wins[0][1]=='RETAIN','WRONG_PERSISTENCE_VERB')
   evolved=advance(apply(s,wins[0]),'T2')
   require(evolved['holder']['i1']=='a0','EXOGENOUS_REQUEST_BREACHED_PROTECTION')
  result[side]={'legal_count':len(legal),'unique_oracle':list(wins[0]),'policy_value':v}
 require(result['A']['unique_oracle']!=result['B']['unique_oracle'],'AB_GOLD_SAME')
 truth_table=''.join('1' if eval_bits(sk['policy_graph'],bits) else '0' for bits in itertools.product((False,True),repeat=4))
 for bit in range(4):
  sensitive=False
  for rest in itertools.product((False,True),repeat=3):
   b=list(rest);b.insert(bit,False);c=list(b);c[bit]=True
   if eval_bits(sk['policy_graph'],b)!=eval_bits(sk['policy_graph'],c):sensitive=True;break
  require(sensitive,f'INERT_LEAF_{bit}')
 return {'skeleton_id':sk['skeleton_id'],'category':cat,'split':sk['split_design'],
  'A':result['A'],'B':result['B'],'truth_table':truth_table,'structural_signature':graph_canonical(sk['policy_graph']),
  'typed_complete':True,'A_B_unique_reachable_actions':True,'all_policy_leaves_causally_sensitive':True}

def audit(data):
 require(data['classification']=='PUBLIC_SOURCE_ONLY_DESIGN_PROTOTYPE_NOT_DATASET_NOT_EVAL_GOLD','EVAL_CLASSIFICATION')
 skels=data['skeletons'];require(len(skels)==32,'COUNT_NOT_32')
 ids=[s['skeleton_id'] for s in skels];require(len(ids)==len(set(ids)),'DUPLICATE_ID')
 reports=[audit_one(s) for s in skels]
 witnesses={};npairs=0;nsame=0
 for cat in CATS:
  group=[(s,r) for s,r in zip(skels,reports) if r['category']==cat]
  require(len(group)==8,'CATEGORY_NOT_8')
  trains=[(s,r) for s,r in group if r['split']=='TRAIN']
  oods=[(s,r) for s,r in group if r['split']=='STRUCTURAL_OOD_BLUEPRINT']
  require(len(trains)==4 and len(oods)==4,'SPLIT_NOT_4x4')
  require(len(set(r['truth_table'] for s,r in group))==8,'FUNCTION_SEMANTIC_OVERLAP')
  require(len(set(r['structural_signature'] for s,r in group))==8,'GRAPH_ISOMORPHISM_OVERLAP')
  w=[]
  for ts,tr in trains:
   for os,orr in oods:
    # A typed, domain-valid graph-pair counterexample on a SHARED world state.
    valid=[]
    for bits in itertools.product((False,True),repeat=4):
     if not bits[0]:continue
     # Graph disagreement must be actionable under both policies, same input.
     if eval_bits(ts['policy_graph'],bits)==eval_bits(os['policy_graph'],bits):continue
     world=skel_world_like(ts,cat,bits)
     invariant(world)
     actions=set()
     for sk in (ts,os):
      v=eval_graph(sk['policy_graph'],{'category':cat,'world':world})
      goal=sk['task']['goal_when_true'] if v else sk['task']['goal_when_false']
      wins=[act for act in enumerate_actions(world) if ((after:=apply(world,act)) is not None) and all(get(after,p)==want for p,want in goal.items())]
      require(len(wins)==1,'NOVELTY_WITNESS_ORACLE_NOT_UNIQUE')
      actions.add(wins[0])
     if len(actions)==2:valid.append(bits)
    require(bool(valid),f'NO_REACHABLE_MEANINGFUL_NOVELTY:{ts["skeleton_id"]}:{os["skeleton_id"]}')
    w.append({'train':ts['skeleton_id'],'ood':os['skeleton_id'],'witness_input_vector':list(valid[0]),'different_canonical_actions':True})
  witnesses[cat]=w;npairs+=len(w)
 return reports,witnesses,{'blueprints':len(reports),'cat_count':len(CATS),'train_blueprints':16,'ood_blueprints':16,
           'A_B_oracles_unique_reachable':sum(r['A_B_unique_reachable_actions'] for r in reports),
           'typed_states_complete':sum(r['typed_complete'] for r in reports),
           'distinct_truth_tables_per_category':8,'nonisomorphic_graphs_per_category':8,
           'train_ood_nonoverlap_pairs_with_reachable_semantic_witness':npairs,
           'private_EVAL_oracle':'NOT_CREATED','dataset_admission':'HOLD'}

def skel_world_like(sk,cat,bits):
 # Reconstruct a comparison world from existing typed AST, with only 4 DECLARED
 # observations varied; preserve invariants and category-relevant action preconditions.
 s=copy.deepcopy(sk['state_A'])
 s['power']['d1']='ON' if bits[0] else 'OFF'
 if cat in ('entity_location','causal_reasoning'):
  s['trigger_fired']['g1']=bits[1];s['protected_until']['i1']='T1' if bits[2] else 'BEFORE_T0'
  s['holder']['i1']='a1' if bits[3] else 'NONE';s['location_item']['i1']='l1' if bits[3] else 'l0'
 elif cat=='rule_constraint':
  s['trigger_fired']['g0']=bits[1];s['protected_until']['i1']='T1' if bits[2] else 'BEFORE_T0'
  s['holder']['i1']='a1' if bits[3] else 'NONE';s['location_item']['i1']='l1' if bits[3] else 'l0'
 elif cat=='goal_persistence':
  s['trigger_fired']['g0']=bits[1];s['protected_until']['i0']='T1' if bits[2] else 'BEFORE_T0'
  s['holder']['i0']='a1' if bits[3] else 'NONE';s['location_item']['i0']='l1' if bits[3] else 'l0'
 return s

def main():
 ap=argparse.ArgumentParser();ap.add_argument('blueprints',type=Path);ap.add_argument('--out',type=Path);ns=ap.parse_args()
 data=json.loads(ns.blueprints.read_text(encoding='utf-8'))
 reports,witnesses,count=audit(data)
 receipt={'schema':'ttm.d1.r1.32_blueprint_independent_checker_receipt.v1',
  'mode':'PUBLIC_SOURCE_ONLY_NO_GPU_NO_TRAIN_NO_TEST_OR_PRIVATE_GOLD',
  'input_sha256':hashlib.sha256(ns.blueprints.read_bytes()).hexdigest(),
  'checker_sha256':hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),
  'checks':count,'records':reports,'nonisomorphism_witnesses':witnesses,
  'decision':'HOLD_SOURCE_ONLY_DESIGN_NOT_SCIENCE_READY',
  'not_verified':['sealed EVAL AST/gold private custody','rights and PII review',
                 'original R1 category policy adoption of boolean dependency graph',
                 'distinct organizational independent reviewer','real TRAIN VAL EVAL lexical worlds',
                 'fully independent production semantic model-checker']}
 out=ns.out or ns.blueprints.with_name('TTM_D1_R1_32_INDEPENDENT_CHECKER_RECEIPT_20261114.json')
 out.write_text(json.dumps(receipt,ensure_ascii=False,indent=2,sort_keys=True)+'\n',encoding='utf-8')
 print('SOURCE_ONLY_32_BLUEPRINT_QA=PASS')
 for k,v in count.items():print(f'{k.upper()}={v}')
 print('INPUT_SHA256='+receipt['input_sha256']);print('CHECKER_SHA256='+receipt['checker_sha256'])
 print('RECEIPT_SHA256='+hashlib.sha256(out.read_bytes()).hexdigest())
 print('DESIGN_VERDICT='+receipt['decision'])

if __name__=='__main__':main()
