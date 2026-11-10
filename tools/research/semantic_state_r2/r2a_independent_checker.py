#!/usr/bin/env python3
"""Independent parser of R2A visible text and model input projection.

Does NOT import the generator. Correct answers are derived from the displayed
story and queried key only; metadata is checked after the interpretation.
"""
from __future__ import annotations
import argparse, hashlib, json, re
from collections import Counter, defaultdict
from pathlib import Path

PEOPLE=frozenset(("Lan", "Minh", "An", "Binh", "Hoa", "Mai", "Nam", "Duy"))
OBJECTS=frozenset(("key", "book", "ball", "cup", "map", "note"))
GOALS=frozenset(("open the gate", "read the book", "visit the garden", "help a friend", "rest at home", "draw a map", "find the ball", "write a note"))
PATTERNS={
 ('ownership','DEV'):re.compile(r'^The ([a-z]+) belongs to ([A-Z][a-z]+)\.$'),
 ('ownership','CHALLENGE'):re.compile(r'^([A-Z][a-z]+) has the ([a-z]+) now\.$'),
 ('goal','DEV'):re.compile(r'^([A-Z][a-z]+) plans to ([a-z ]+)\.$'),
 ('goal','CHALLENGE'):re.compile(r'^([A-Z][a-z]+) intends to ([a-z ]+)\.$'),
}
QUESTIONS={
 ('ownership','DEV'):re.compile(r'^Who owns the ([a-z]+)\?$'),
 ('ownership','CHALLENGE'):re.compile(r'^Who has the ([a-z]+) now\?$'),
 ('goal','DEV'):re.compile(r'^What does ([A-Z][a-z]+) plan to do\?$'),
 ('goal','CHALLENGE'):re.compile(r'^Which goal does ([A-Z][a-z]+) intend to pursue\?$'),
}

class Invalid(ValueError):pass

def need(c,msg):
 if not c:raise Invalid(msg)

def canonical(obj):return (json.dumps(obj,sort_keys=True,ensure_ascii=False,separators=(',',':'))+'\n').encode('utf-8')
def hash_bytes(b):return hashlib.sha256(b).hexdigest()
def wordbag(s):return Counter(re.findall('[a-z]+',s.lower()))

def decode(row):
 family,split=row['family'],row['split']
 need((family,split) in PATTERNS,'UNKNOWN_GRAMMAR_OR_SPLIT')
 story,q=row['story'],row['question']
 need(type(story) is str and type(q) is str,'INPUT_TYPE_INVALID')
 sentences=story.split('\n')
 need(len(sentences)==4,'NOT_FOUR_EVENTS')
 events=[]
 for sentence in sentences:
  m=PATTERNS[(family,split)].fullmatch(sentence)
  need(m is not None,'INVALID_VISIBLE_EVENT')
  if family=='ownership':
   obj,person=m.groups() if split=='DEV' else (m.group(2),m.group(1))
   need(obj in OBJECTS and person in PEOPLE,'BAD_ENTITY')
   events.append({'family':'ownership','key':obj,'value':person})
  else:
   person,goal=m.groups()
   need(person in PEOPLE and goal in GOALS,'BAD_GOAL')
   events.append({'family':'goal','key':person,'value':goal})
 m=QUESTIONS[(family,split)].fullmatch(q)
 need(m is not None,'INVALID_QUESTION')
 key=m.group(1)
 need(key in (OBJECTS if family=='ownership' else PEOPLE),'BAD_QUERY_KEY')
 groups=defaultdict(list)
 for idx,e in enumerate(events):groups[e['key']].append((idx,e['value']))
 need(len(groups)==2 and all(len(v)==2 for v in groups.values()),'NOT_TWO_KEYS_WITH_TWO_UPDATES')
 need(all(v[0][1]!=v[1][1] for v in groups.values()),'IDENTICAL_STATE_UPDATES')
 need(key in groups,'QUERY_KEY_NOT_IN_STORY')
 need(len({e['value'] for e in events})==4,'ANSWER_OR_DISTRACTOR_VALUE_COLLISION')
 answer=groups[key][-1][1]
 query_pos=tuple(idx for idx,v in groups[key]);other_key=next(x for x in groups if x!=key)
 return answer,events,query_pos,other_key,groups

def check(dataset,model):
 need(type(dataset) is dict and dataset.get('schema')=='ttm.r2a.counterbalanced_key_binding.v1','SCHEMA')
 need(dataset.get('seed')==20261110,'SEED')
 pairs,probes=dataset.get('pairs'),dataset.get('probes')
 need(type(pairs) is list and len(pairs)==256,'PAIR_RECORD_COUNT')
 need(type(probes) is list and len(probes)==128,'PROBE_COUNT')
 need(set(dataset)=={'schema','seed','declaration','counts','pairs','probes'},'ORACLE_DATA_FIELDS')
 need(type(model) is dict and model.get('schema')=='ttm.r2a.model_input_only.v1','MODEL_SCHEMA')
 rows=model.get('records')
 need(type(rows) is list and len(rows)==384,'MODEL_INPUT_COUNT')
 expected=[{'story':r['story'],'question':r['question']} for r in pairs+probes]
 need(rows==expected,'MODEL_PROJECTION_MISMATCH')
 need(all(set(r)=={'story','question'} for r in rows),'MODEL_INPUT_METADATA_LEAK')
 seen=set();groups=defaultdict(list);score=dict(third=0,last=0,last_relevant=0)
 split_counts=Counter();positions=Counter();final_target=Counter();allanswers=0
 pair_answers={};pair_events={}
 for r in pairs:
  need(set(r)=={'id','pair_id','variant','family','split','story','question','answer','source_events'},'PAIR_FIELDS')
  keyid=(r['story'],r['question'])
  need(keyid not in seen,'DUPLICATE_MODEL_INPUT')
  seen.add(keyid)
  expected_ans,events,qpos,other_key,keygroups=decode(r)
  need(r['answer']==expected_ans,'ANSWER_MISMATCH')
  need(r['source_events']==events,'EVENT_SOURCE_TAMPERED')
  pid=r['pair_id'];variant=r['variant'];split=r['split'];family=r['family']
  need(re.fullmatch(r'[OG]\d{3}',pid) and pid[0]==('O' if family=='ownership' else 'G'),'PAIR_ID_INVALID')
  index=int(pid[1:])
  need(1<=index<=64,'PAIR_INDEX_RANGE')
  need(split==('DEV' if index<=32 else 'CHALLENGE'),'WRONG_GRAMMAR_SPLIT')
  need(variant in ('A','B') and r['id']==pid+variant,'BAD_VARIANT_ID')
  groups[pid].append(r)
  split_counts[(family,split)]+=1
  allanswers+=1
  score['third']+=int(events[2]['value']==expected_ans)
  score['last']+=int(events[3]['value']==expected_ans)
  score['last_relevant']+=int(events[qpos[-1]]['value']==expected_ans)
  positions[(family,split,qpos)]+=1
  final_target[(family,split)]+=int(qpos[-1]==3)
  pair_answers[r['id']]=expected_ans;pair_events[r['id']]=events
 need(len(groups)==128 and all(len(v)==2 for v in groups.values()),'GROUP_COUNT')
 for pid,r in groups.items():
  a,b=sorted(r,key=lambda x:x['variant'])
  need(a['variant']=='A' and b['variant']=='B','VARIANTS_BAD')
  need(a['family']==b['family'] and a['split']==b['split'] and a['question']==b['question'],'PAIR_QUERY_MISMATCH')
  need(wordbag(a['story'])==wordbag(b['story']),'NOT_WORD_BAG_MATCHED')
  ea,eb=pair_events[a['id']],pair_events[b['id']]
  changed=[i for i in range(4) if ea[i]!=eb[i]]
  need(len(changed)==2,'NOT_TWO_POSITIONS_SWAPPED')
  need(ea[changed[0]]==eb[changed[1]] and ea[changed[1]]==eb[changed[0]],'COUNTERFACTUAL_NOT_SWAPPED')
  need(ea[changed[0]]['key']==ea[changed[1]]['key'],'COUNTERFACTUAL_SWAPPED_TWO_KEYS')
  need(pair_answers[a['id']]!=pair_answers[b['id']],'COUNTERFACTUAL_ANSWER_NOT_FLIPPED')
  # The distractor's state must be unchanged across A/B.
  _,_,_,other,ga=decode(a);_,_,_,_,gb=decode(b)
  need(ga[other][-1][1]==gb[other][-1][1],'DISTRACTOR_STATE_CHANGED')
 need(len(probes)==128,'PROBES_COUNT')
 for r in probes:
  need(set(r)=={'id','pair_id','family','split','story','question','answer','source_events'},'PROBE_FIELDS')
  pid=r['pair_id'];need(pid in groups and r['id']==pid+'Q','PROBE_ID')
  a=next(x for x in groups[pid] if x['variant']=='A')
  need(r['story']==a['story'] and r['question']!=a['question'],'NO_BINDING_INTERVENTION')
  need(r['family']==a['family'] and r['split']==a['split'],'PROBE_SPLIT_FAMILY')
  ans,ev,_,_,_=decode(r)
  need(r['answer']==ans and ans!=a['answer'],'QUERY_BINDING_NOT_DIFFERENTIAL')
  need(r['source_events']==ev,'PROBE_SOURCE_EVENT_MISMATCH')
  k=(r['story'],r['question']);need(k not in seen,'DUPLICATE_PROBE_INPUT');seen.add(k)
 for fam in ('ownership','goal'):
  for split in ('DEV','CHALLENGE'):
   need(split_counts[(fam,split)]==64,'SPLIT_COUNTS_WRONG')
   need(final_target[(fam,split)]==32,'FINAL_TARGET_NOT_BALANCED')
   # Six 2-of-4 combinations must all occur; each 5-6 pairs per
   # family/split => 10-12 records counting A and B.
   qpos=[p for (f,s,p),count in positions.items() if f==fam and s==split]
   need(len(qpos)==6,'POSITION_COVERAGE_MISSING')
   need(all(10<=positions[(fam,split,p)]<=12 for p in qpos),'POSITION_COMBINATION_IMBALANCED')
 observed={'pairs':len(groups),'paired_records':len(pairs),'question_binding_probes':len(probes),
           'model_input_records':len(rows),
           'by_family_split':{f'{f}_{s}':split_counts[(f,s)] for f in ('ownership','goal') for s in ('DEV','CHALLENGE')}}
 need(dataset.get('counts')==observed,'DECLARED_COUNTS_MISMATCH')
 need(score['last_relevant']==256,'LAST_RELEVANT_RULE_FAIL')
 need(score['third']<192 and score['last']<192,'POSITION_SHORTCUT_NOT_FIXED')
 return {
   'result':'PASS_SCOPED_TOY_FIXTURE_ONLY','pairs':128,'paired_records':256,
   'query_binding_probes':128,'model_visible_records':384,'question_binding_probes_correct':128,
   'ordered_update_interpreter_correct':256,'bag_of_words_upper_bound_correct_of_256':128,
   'position_only_controls_correct_of_256':{'third_sentence':score['third'],'last_sentence':score['last']},
   'key_aware_last_relevant_control_correct_of_256':256,
   'last_event_is_queried_key_fraction':sum(final_target.values())/len(pairs),
   'family_split_counts':observed['by_family_split'],
   'all_six_query_position_pairs_present_per_family_split':True,
   'toy_has_not_trained_or_evaluated_TTM':True,
   'limitations':['Rule-based last-relevant-event solution remains trivial','Visible CHALLENGE grammar is public; not held-out TEST','Cannot conclude an auxiliary state module is needed or helpful']}


def main():
 ap=argparse.ArgumentParser();ap.add_argument('--oracle',required=True);ap.add_argument('--model-input',required=True);ap.add_argument('--output',required=True);a=ap.parse_args()
 p=Path(a.output)
 if p.exists():raise SystemExit('REFUSE_OVERWRITE')
 raw=Path(a.oracle).read_bytes();model_raw=Path(a.model_input).read_bytes()
 result=check(json.loads(raw),json.loads(model_raw))
 result['oracle_sha256']=hash_bytes(raw);result['model_input_sha256']=hash_bytes(model_raw)
 p.write_bytes(canonical(result));print(json.dumps(result,sort_keys=True))
if __name__=='__main__':main()
