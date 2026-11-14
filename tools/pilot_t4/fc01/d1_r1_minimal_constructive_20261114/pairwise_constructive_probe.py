#!/usr/bin/env python3
"""Second pass over bounded constructive corpus; pairs only one typed state field difference.
This is a source-only paired counterfactual admission probe, NOT formal action-causal OOD equivalence.
"""
import collections,itertools,json,pathlib
import constructive_search as search
HERE=pathlib.Path(__file__).resolve().parent

def leaves(o,p=''):
 if isinstance(o,dict):
  for k in sorted(o):yield from leaves(o[k],p+'.'+k if p else k)
 else:yield p,o

def diff(a,b):
 x=dict(leaves(a));y=dict(leaves(b));assert set(x)==set(y)
 return [(k,x[k],y[k]) for k in x if x[k]!=y[k]]

def canonical_goal(goal):return search.canonical(goal)

def run():
 all_rows=search.sweep();summary={};evidence={};canon_motifs={};counts={}
 for cat,rows in all_rows.items():
  eligible=[r for r in rows if r['result']['status']=='UNIQUE']
  pairs=[]
  for a,b in itertools.combinations(eligible,2):
   if canonical_goal(a['goal'])!=canonical_goal(b['goal']):continue
   delta=diff(a['state'],b['state'])
   if len(delta)!=1:continue
   va=a['result']['firsts'][0][0];vb=b['result']['firsts'][0][0]
   if a['result']['firsts'][0]==b['result']['firsts'][0]:continue
   d=delta[0]
   # role-normalized only at coarse level; NOT novel graph certificate
   motif=(d[0].split('.')[0],tuple(sorted((va,vb))))
   pairs.append({'changed_fluent':d[0],'before':d[1],'after':d[2],
                 'oracle_A':a['result']['firsts'][0],'oracle_B':b['result']['firsts'][0],
                 'A_state':a['state'],'B_state':b['state'],'shared_goal':a['goal'],
                 'motif_proxy':list(motif)})
  motifs=sorted({search.canonical(p['motif_proxy']) for p in pairs})
  summary[cat]={'unique_scenarios':len(eligible),'one_fluent_AB_distinct_first_action_pairs':len(pairs),
                'coarse_motif_proxy_count':len(motifs),'coarse_motifs':[json.loads(v) for v in motifs],
                'four_structural_ood_proven':False,'paired_conclusion':'NO_CANONICAL_CAUSAL_NONOVERLAP_CERTIFICATE'}
  evidence[cat]=pairs[:4]
  canon_motifs[cat]=motifs
  counts[cat]=collections.Counter(p['changed_fluent'] for p in pairs)
 return {'schema':'ttm.d1.r1.constructive_paired_counterfactual_probe.v1','operation':'TTM_SMALL4M_D1_R1_MINIMAL_SEMANTIC_CONTRACT_FREEZE_AND_CONSTRUCTIVE_FOUR_CATEGORY_FEASIBILITY_SINGLE_REVIEW_GATE',
         'method':'all unordered eligible unique-scenario pairs with exact same goal, exact ONE typed fluent changed, and distinct first action; labels are source-only; excludes two-field route swaps; no claim global bound',
         'summary':summary,'first_four_examples_per_category':evidence,
         'status':'HOLD_NO_FOUR_OOD_PROVEN_ANY_CATEGORY'}
if __name__=='__main__':
 j=run();p=HERE/'TTM_D1_R1_BOUNDED_PAIRED_CONSTRUCTIVE_PROBE_20261114.json';p.write_text(json.dumps(j,indent=2,ensure_ascii=False)+'\n',encoding='utf8');print(json.dumps(j['summary'],ensure_ascii=False))
