import collections,random,re,json,hashlib,pathlib,copy,unittest
P=('Lan','Minh','An','Binh','Hoa','Mai','Nam','Duy')
O=('key','book','ball','cup','map','note')
G=('open the gate','read the book','visit the garden','help a friend','rest at home','draw a map','find the ball','write a note')
R=random.Random(20261110)

def state(events):
 s={'owner':{},'goal':{}}
 for e in events:
  if e['type']=='assign':s['owner'][e['object']]=e['person']
  else:s['goal'][e['person']]=e['goal']
 return s

def surface(events):
 return '\n'.join(('The %s belongs to %s.'%(e['object'],e['person']) if e['type']=='assign' else '%s plans to %s.'%(e['person'],e['goal'])) for e in events)

def bag(t):return collections.Counter(re.findall('[a-z]+',t.lower()))

def create():
 records=[];seen=set()
 for family in ('ownership','goal'):
  for i in range(64):
   for retry in range(100):
    a,b,c,d=R.sample(P,4)
    if family=='ownership':
     obj,dobj=R.sample(O,2)
     e1={'type':'assign','object':obj,'person':a};e2={'type':'assign','object':obj,'person':b}
     no1={'type':'assign','object':dobj,'person':c};no2={'type':'assign','object':dobj,'person':d}
     question=f'Who owns the {obj}?';track='owner';key=obj
    else:
     g1,g2,g3,g4=R.sample(G,4)
     e1={'type':'plan','person':a,'goal':g1};e2={'type':'plan','person':a,'goal':g2}
     no1={'type':'plan','person':b,'goal':g3};no2={'type':'plan','person':b,'goal':g4}
     question=f'What does {a} plan to do?';track='goal';key=a
    pid=('O' if family=='ownership' else 'G')+f'{i+1:03}'
    pair=[]
    for variant,events in enumerate(([e1,no1,e2,no2],[e2,no1,e1,no2])):
     pair.append(dict(id=pid+('A' if variant==0 else 'B'),pair_id=pid,family=family,split='DEV' if i<32 else 'CHALLENGE',variant=variant,story=surface(events),question=question,answer=state(events)[track][key],source_events=events))
    fingerprint=tuple(sorted((x['story'],x['question']) for x in pair))
    if fingerprint not in seen:
     seen.add(fingerprint);records.extend(pair);break
   else:raise RuntimeError('duplicate pair retry exhausted')
 records.sort(key=lambda x:(x['family'],x['pair_id'],x['variant']))
 counts=collections.Counter((x['family'],x['split']) for x in records)
 return {'schema':'ttm.r2.ordered_state_goal.counterfactual_pairs.v1','seed':20261110,'n_per_family':64,
 'notes':['Artificial English grammar; not a natural language understanding benchmark.',
 'DEV and CHALLENGE labels are both publicly exposed; CHALLENGE is NOT a sealed TEST.',
 'Two variants have identical word multisets, but opposing last-write-wins answers.',
 'The generated answer is computed from structured events; independent checker must parse the visible story.',
 'No model training, no inference, no TTM checkpoint, no private TinyStories, TEST or Q1Q2.'],
 'counts':{f'{k[0]}_{k[1]}':v for k,v in sorted(counts.items())},'records':records}

# Text parser here is independently coded; it reads no source_events and uses no generator state().
def parse(story,question):
 lines=story.split('\n')
 if len(lines)!=4:raise ValueError('wrong number of events')
 owners={};goals={};events=[]
 for line in lines:
  mo=re.fullmatch(r'The ([a-z]+) belongs to ([A-Z][a-z]+)\.',line)
  mg=re.fullmatch(r'([A-Z][a-z]+) plans to (.+)\.',line)
  if mo:
   key,value=mo.groups()
   if key not in O or value not in P:raise ValueError('invalid ownership token')
   owners[key]=value;events.append(('owner',key,value))
  elif mg:
   key,value=mg.groups()
   if key not in P or value not in G:raise ValueError('invalid goal token')
   goals[key]=value;events.append(('goal',key,value))
  else:raise ValueError('unrecognized sentence')
 mo=re.fullmatch(r'Who owns the ([a-z]+)\?',question)
 mg=re.fullmatch(r'What does ([A-Z][a-z]+) plan to do\?',question)
 if bool(mo)==bool(mg):raise ValueError('bad question')
 fam='ownership' if mo else 'goal'; target=(mo or mg).group(1)
 answer=(owners if mo else goals).get(target)
 if answer is None:raise ValueError('unknown query target')
 candidates=sorted({v for k,t,v in events if t==target})
 if len(candidates)!=2 or [e[1]==target for e in events]!=[True,False,True,False]:raise ValueError('invalid event structure')
 return fam,answer,candidates

def check(x):
 if x.get('schema')!='ttm.r2.ordered_state_goal.counterfactual_pairs.v1':raise ValueError('schema')
 rs=x['records'];pairs=collections.defaultdict(list);ids=set();bagcorrect=0
 if len(rs)!=256:raise ValueError('count')
 for a in rs:
  if a['id'] in ids:raise ValueError('duplicate id')
  ids.add(a['id']);f,ans,cands=parse(a['story'],a['question'])
  if f!=a['family'] or ans!=a['answer']:raise ValueError('wrong oracle answer')
  pid=a['pair_id']; idx=int(pid[1:]);want='DEV' if idx<=32 else 'CHALLENGE'
  if a['split']!=want or a['id']!=pid+('A' if a['variant']==0 else 'B'):raise ValueError('split/variant')
  bagcorrect+=ans==cands[0];pairs[pid].append(a)
 if len(pairs)!=128:raise ValueError('pair count')
 for p,rows in pairs.items():
  if len(rows)!=2:raise ValueError('pair variants')
  a,b=sorted(rows,key=lambda t:t['variant']);al=a['story'].splitlines();bl=b['story'].splitlines()
  if not(al[0]==bl[2] and al[2]==bl[0] and al[1]==bl[1] and al[3]==bl[3]):raise ValueError('pair not counterfactual')
  if bag(a['story'])!=bag(b['story']) or a['answer']==b['answer'] or a['question']!=b['question']:raise ValueError('pair balance')
 if bagcorrect!=128:raise ValueError('bag baseline')
 return {'oracle_text_parser_correct':256,'bag_order_invariant_correct':128,'total':256,'pairs':128,'family_split':dict(x['counts'])}

if __name__=='__main__':
 o=pathlib.Path(__file__).parent
 x=create();result=check(x)
 b=(json.dumps(x,ensure_ascii=False,sort_keys=True,indent=2)+'\n').encode('utf8')
 (o/'dataset.json').write_bytes(b)
 (o/'local_integration_qa.json').write_text(json.dumps({'status':'PASS_INDEPENDENT_TEXT_INTERPRETATION', 'dataset_sha256':hashlib.sha256(b).hexdigest(),**result},indent=2,sort_keys=True)+'\n',encoding='utf8')
 print('PASS',result,'SHA',hashlib.sha256(b).hexdigest())
