#!/usr/bin/env python3
"""Independent mutation probes for new 32-skeleton checker only.
Never invokes prior 13/13 or 12/12 source QA. NetworkX is optional extra confirmation.
"""
import copy,hashlib,json,sys
from pathlib import Path
sys.path.insert(0,str(Path(__file__).parent))
from independent_32_oracle_checker import audit

p=Path(__file__).with_name('TTM_D1_R1_TYPED_32_SOURCE_BLUEPRINTS_20261114.json')
d=json.loads(p.read_text(encoding='utf-8'))
mutations={}

def case(name,change):
 x=copy.deepcopy(d);change(x)
 try:audit(x)
 except (AssertionError,KeyError,TypeError,IndexError,ValueError,RecursionError) as e:
  mutations[name]={'reject':True,'error':str(e)[:200]}
 else:mutations[name]={'reject':False,'error':'BAD_MUTATION_NOT_DETECTED'}

def first_skel(x):return x['skeletons'][0]
case('DUPLICATE_ID',lambda x:x['skeletons'][1].update(skeleton_id=first_skel(x)['skeleton_id']))
case('OMIT_TYPED_FLUENT',lambda x:first_skel(x)['state_A'].pop('protected_until'))
case('AB_EXTRA_INTERVENTION',lambda x:first_skel(x)['state_B']['location_agent'].update(a1='l0'))
case('HOLDER_LOCATION_BROKEN',lambda x:first_skel(x)['state_A']['location_item'].update(i1='l0'))
case('AB_GOAL_DUPLICATE',lambda x:first_skel(x)['task'].update(goal_when_false=first_skel(x)['task']['goal_when_true']))
case('AST_GRAPH_CYCLE',lambda x:first_skel(x)['policy_graph']['edges'].append({'from':'n0','to':'n0','port':0}))
case('OOD_GRAPH_CLONE_TRAIN',lambda x:x['skeletons'][4].update(policy_graph=copy.deepcopy(x['skeletons'][0]['policy_graph'])))
case('OOD_SEMANTIC_CLONE_TRAIN',lambda x:x['skeletons'][5].update(policy_graph=copy.deepcopy(x['skeletons'][1]['policy_graph'])))
case('UNKNOWN_OBSERVATION',lambda x:first_skel(x)['policy_graph']['nodes'][2].update(predicate='source_name_only'))
case('GOLD_NONUNIQUE',lambda x:first_skel(x)['task'].update(goal_when_true={'current_time':'T0'}))
case('EVAL_LABEL_FORBIDDEN',lambda x:x.update(classification='SEALED_EVAL_DATASET'))
case('ILLEGAL_REQUEST_TYPE',lambda x:x['skeletons'][24]['state_A']['external_transfer_request'].update(item='i999'))

# Verify across graphs via separately implemented NetworkX DiGraphMatcher if present.
networkx_check={'status':'NOT_AVAILABLE'}
try:
 import networkx as nx
 from networkx.algorithms.isomorphism import DiGraphMatcher

 def make_graph(sk):
   H=nx.DiGraph(); g=sk['policy_graph']
   for n in g['nodes']:
    label='OBS:'+n['predicate'] if n['kind']=='typed_observation' else 'GATE:'+n['operator']
    H.add_node(n['id'],label=label)
   for e in g['edges']:H.add_edge(e['from'],e['to'])
   return H
  
 iso_pairs=[];pairs=0
 for c in ('entity_location','causal_reasoning','rule_constraint','goal_persistence'):
  group=[s for s in d['skeletons'] if s['category']==c]
  train=[s for s in group if s['split_design']=='TRAIN'];ood=[s for s in group if s['split_design']=='STRUCTURAL_OOD_BLUEPRINT']
  for a in train:
   for b in ood:
    pairs+=1
    if DiGraphMatcher(make_graph(a),make_graph(b),node_match=lambda x,y:x['label']==y['label']).is_isomorphic():
     iso_pairs.append([a['skeleton_id'],b['skeleton_id']])
 networkx_check={'status':'PASS' if not iso_pairs and pairs==64 else 'FAIL', 'pairs':pairs,'isomorphic_pairs':iso_pairs,
                 'method':'independently labeled directed-graph isomorphism (networkx DiGraphMatcher)'}
except ImportError: pass

assert len(mutations)==12
assert all(r['reject'] for r in mutations.values()),mutations
assert networkx_check['status'] in ('PASS','NOT_AVAILABLE')
receipt={'schema':'ttm.d1.r1.32_mutation_audit.v1','classification':'NEW_32_SOURCE_ONLY_NEGATIVE_QA_NOT_PRIOR_13_OR_12','cases':mutations,
        'detected':sum(v['reject'] for v in mutations.values()),'total':len(mutations),'independent_networkx_graph_iso':networkx_check,
        'blueprints_sha256':hashlib.sha256(p.read_bytes()).hexdigest()}
out=p.with_name('TTM_D1_R1_32_NEGATIVE_AND_GRAPH_QA_RECEIPT_20261114.json')
out.write_text(json.dumps(receipt,indent=2,ensure_ascii=False,sort_keys=True)+'\n',encoding='utf-8')
print('NEW_32_NEGATIVE_MUTATIONS=%d/%d'%(receipt['detected'],receipt['total']))
print('INDEPENDENT_NETWORKX_GRAPH_ISOMORPHISM='+networkx_check['status'])
print('NEGATIVE_RECEIPT_SHA256='+hashlib.sha256(out.read_bytes()).hexdigest())
