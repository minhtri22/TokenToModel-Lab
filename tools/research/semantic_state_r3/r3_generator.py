#!/usr/bin/env python3
"""TTM R3 public toy generator: independent of TTM/TRAIN/TEST/GPU.
A/B differ at a single valid target event, 4 cells cover graph/query 2x2.
Never treat public labels as a blind evaluation set.
"""
from __future__ import annotations
import argparse, hashlib, json, random
from pathlib import Path
from collections import Counter

SEED=20261111
SCHEMA='ttm.r3.structural_state_graph.public_oracle.v1'
INPUT_SCHEMA='ttm.r3.story_question_only.v1'
DECL='Public R3 structural toy; labels public; NOT sealed FINAL, NOT TTM neural evidence'
PEOPLE=('Lan','Minh','An','Binh','Hoa','Mai','Nam','Duy','Thao','Linh')
ITEMS=('key','map','cup','book','ball','note','coin','card')
GOALS=('read','write','draw','sing','travel','plant','repair','teach','cook','count','study','paint','search','build','clean','rest')
ALIASES=('Cedar','River','Piper','Sage','Dawn','Stone','Cloud','Amber')

def stable(x): return (json.dumps(x,ensure_ascii=False,sort_keys=True,separators=(',',':'))+'\n').encode('utf-8')
def sha(x):return hashlib.sha256(x).hexdigest()

def initial_state(): return {'holders':{},'goals':{},'aliases':{}}
def resolve(st,p):return st['aliases'].get(p,p)
def step(st,e):
    op=e['op']
    if op=='INIT_HOLDER':
        if e['item'] in st['holders']:raise ValueError('ALREADY_INITIALIZED')
        st['holders'][e['item']]=resolve(st,e['p'])
    elif op=='HANDOFF':
        p,q=resolve(st,e['p']),resolve(st,e['q'])
        if st['holders'].get(e['item'])!=p or p==q:raise ValueError('BAD_HANDOFF')
        st['holders'][e['item']]=q
    elif op=='DEFINE_ALIAS':
        if e['alias'] in st['aliases'] or e['alias'] in PEOPLE:raise ValueError('BAD_ALIAS')
        st['aliases'][e['alias']]=resolve(st,e['p'])
    elif op=='SET_GOAL':
        p=resolve(st,e['p'])
        if st['goals'].get(p) is not None:raise ValueError('BAD_GOAL_SET')
        st['goals'][p]=e['g']
    elif op=='DELEGATE_GOAL':
        p,q=resolve(st,e['p']),resolve(st,e['q'])
        if p==q or st['goals'].get(p)!=e['g'] or st['goals'].get(q) is not None:raise ValueError('BAD_DELEGATION')
        st['goals'][p]=None;st['goals'][q]=e['g']
    elif op=='CHANGE_GOAL':
        p=resolve(st,e['p'])
        if st['goals'].get(p)!=e['old'] or e['old']==e['new']:raise ValueError('BAD_GOAL_CHANGE')
        st['goals'][p]=e['new']
    elif op=='CANCEL_GOAL':
        p=resolve(st,e['p'])
        if st['goals'].get(p)!=e['g']:raise ValueError('BAD_CANCEL')
        st['goals'][p]=None
    else:raise ValueError('UNKNOWN_OPERATION')

def run(events):
    st=initial_state()
    for e in events:step(st,e)
    return st

def render(e):
    o=e['op']
    if o=='INIT_HOLDER':return f"{e['item']} starts with {e['p']}."
    if o=='HANDOFF':return f"{e['p']} passes {e['item']} to {e['q']}."
    if o=='DEFINE_ALIAS':return f"The alias {e['alias']} names {e['p']}."
    if o=='SET_GOAL':return f"{e['p']} begins goal {e['g']}."
    if o=='DELEGATE_GOAL':return f"{e['p']} delegates goal {e['g']} to {e['q']}."
    if o=='CHANGE_GOAL':return f"{e['p']} changes goal from {e['old']} to {e['new']}."
    if o=='CANCEL_GOAL':return f"{e['p']} cancels goal {e['g']}."
    raise ValueError('BAD_RENDER')

def qstr(k):return f'Who holds {k}?' if k in ITEMS else f'What is {k} goal?'
def answer(st,k): return st['holders'][k] if k in ITEMS else st['goals'].get(resolve(st,k)) or 'NONE'

def interleave(chains,rng):
    queues=[list(c) for c in chains];out=[]
    while any(queues):
        candidates=[i for i,c in enumerate(queues) if c]
        idx=rng.choice(candidates);out.append(queues[idx].pop(0))
    return out

def make_group(family,split,i,rng):
    persons=rng.sample(PEOPLE,8); items=rng.sample(ITEMS,3); goals=rng.sample(GOALS,10)
    a,b,c,d,e,f,g,h=persons; obj,other,third=items
    alias1,alias2=rng.sample(ALIASES,2)
    if family=='T1':
        primary=[dict(op='INIT_HOLDER',item=obj,p=a),dict(op='HANDOFF',item=obj,p=a,q=b),dict(op='HANDOFF',item=obj,p=b,q=c),dict(op='HANDOFF',item=obj,p=c,q=d)]
        # exactly one terminal edge changes in B, no subsequent target effects
        changed=dict(op='HANDOFF',item=obj,p=c,q=e)
        if split=='DEV':
            distraction=[[dict(op='INIT_HOLDER',item=other,p=f),dict(op='HANDOFF',item=other,p=f,q=g)],
                         [dict(op='INIT_HOLDER',item=third,p=g),dict(op='HANDOFF',item=third,p=g,q=h)]]
        else:
            distraction=[[dict(op='INIT_HOLDER',item=other,p=f),dict(op='HANDOFF',item=other,p=f,q=g),dict(op='HANDOFF',item=other,p=g,q=h)],
                         [dict(op='INIT_HOLDER',item=third,p=g)]]
        target,distract=obj,other
    elif family=='T2':
        if split=='DEV':
            primary=[dict(op='SET_GOAL',p=a,g=goals[0]),dict(op='CHANGE_GOAL',p=a,old=goals[0],new=goals[1]),
                     dict(op='DELEGATE_GOAL',p=a,q=b,g=goals[1]),dict(op='CHANGE_GOAL',p=b,old=goals[1],new=goals[2])]
            changed=dict(op='CHANGE_GOAL',p=b,old=goals[1],new=goals[3])
            distraction=[[dict(op='SET_GOAL',p=c,g=goals[4]),dict(op='CANCEL_GOAL',p=c,g=goals[4]),dict(op='SET_GOAL',p=c,g=goals[5])],
                         [dict(op='SET_GOAL',p=d,g=goals[6])]]
        else:
            primary=[dict(op='SET_GOAL',p=a,g=goals[0]),dict(op='DELEGATE_GOAL',p=a,q=b,g=goals[0]),
                     dict(op='CHANGE_GOAL',p=b,old=goals[0],new=goals[1]),dict(op='CHANGE_GOAL',p=b,old=goals[1],new=goals[2])]
            changed=dict(op='CHANGE_GOAL',p=b,old=goals[1],new=goals[3])
            distraction=[[dict(op='SET_GOAL',p=c,g=goals[4]),dict(op='CHANGE_GOAL',p=c,old=goals[4],new=goals[5]),dict(op='CANCEL_GOAL',p=c,g=goals[5])],
                         [dict(op='SET_GOAL',p=d,g=goals[6])]]
        target,distract=b,d
    elif family=='T3':
        # Alias defined on an event chain before it is used, then person resolves inside handoff.
        if split=='DEV':
            primary=[dict(op='DEFINE_ALIAS',alias=alias1,p=a),dict(op='INIT_HOLDER',item=obj,p=a),
                     dict(op='HANDOFF',item=obj,p=alias1,q=b),dict(op='DEFINE_ALIAS',alias=alias2,p=b),
                     dict(op='HANDOFF',item=obj,p=alias2,q=c),dict(op='HANDOFF',item=obj,p=c,q=d)]
        else:
            primary=[dict(op='INIT_HOLDER',item=obj,p=a),dict(op='HANDOFF',item=obj,p=a,q=b),
                     dict(op='DEFINE_ALIAS',alias=alias1,p=b),dict(op='HANDOFF',item=obj,p=alias1,q=c),
                     dict(op='DEFINE_ALIAS',alias=alias2,p=c),dict(op='HANDOFF',item=obj,p=alias2,q=d)]
        changed=dict(op='HANDOFF',item=obj,p=c if split=='DEV' else alias2,q=e)
        distraction=[[dict(op='INIT_HOLDER',item=other,p=f),dict(op='HANDOFF',item=other,p=f,q=g)],
                     [dict(op='INIT_HOLDER',item=third,p=g),dict(op='HANDOFF',item=third,p=g,q=h)]]
        target,distract=obj,other
    else:raise ValueError('UNKNOWN_FAMILY')
    chains=[primary]+distraction
    events_A=interleave(chains,rng)
    # Replace exactly one event on the target chain; its old final hop to d.
    final_idx=next(j for j,event in enumerate(events_A) if event is primary[-1])
    events_B=[dict(event) for event in events_A]
    events_B[final_idx]=changed
    state_A,state_B=run(events_A),run(events_B)
    at,bt=answer(state_A,target),answer(state_B,target)
    ad,bd=answer(state_A,distract),answer(state_B,distract)
    if not (at!=bt and ad==bd and at!=ad and bt!=bd):raise ValueError('BAD_COUNTERFACTUAL')
    gid=f'{family}-{split}-{i:03d}'
    cells=[]
    for variant,es,st in [('A',events_A,state_A),('B',events_B,state_B)]:
        for key_label,key in [('T',target),('D',distract)]:
            cells.append(dict(cell=f'{variant}_{key_label}',story='\n'.join(render(ev) for ev in es),question=qstr(key),answer=answer(st,key),source_events=es))
    return dict(group_id=gid,family=family,split=split,cells=cells,intervention_index=final_idx,intervention_event_type=changed['op'])

def build():
    rng=random.Random(SEED)
    groups=[]
    for fam in ('T1','T2','T3'):
        for split in ('DEV','CHALLENGE'):
            for i in range(16):groups.append(make_group(fam,split,i,rng))
    counts={k:sum(g['family']==k for g in groups) for k in ('T1','T2','T3')}
    rows=[{'story':row['story'],'question':row['question']} for g in groups for row in g['cells']]
    assert len(rows)==384
    oracle={'schema':SCHEMA,'declaration':DECL,'labels_public':True,'sealed_final':False,
            'seed':SEED,'counts':{'groups':96,'inputs':384,'groups_by_family':counts},'groups':groups}
    model={'schema':INPUT_SCHEMA,'records':rows}
    return oracle,model

def write(path,obj):
    p=Path(path)
    if p.exists():raise SystemExit('REFUSE_OVERWRITE')
    p.parent.mkdir(parents=True,exist_ok=True)
    raw=stable(obj);p.write_bytes(raw)
    return {'path':str(p),'sha256':sha(raw),'bytes':len(raw)}

def main():
    ap=argparse.ArgumentParser();ap.add_argument('--oracle',required=True);ap.add_argument('--model-input',required=True)
    a=ap.parse_args()
    if Path(a.oracle).resolve()==Path(a.model_input).resolve():raise SystemExit('COLLIDING_PATHS')
    oracle,model=build()
    print(json.dumps({'oracle':write(a.oracle,oracle),'model':write(a.model_input,model)},sort_keys=True))
if __name__=='__main__':main()
