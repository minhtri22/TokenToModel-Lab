#!/usr/bin/env python3
"""TTM R3A minimal anti-latest-write amendment. Public toy, NO TTM model.

Data are synthetic. The four A/B x target/distractor cells share one group;
model-input rows are shuffled with no ids or oracle labels.
"""
from __future__ import annotations
import argparse,hashlib,json,random
from pathlib import Path
SCHEMA='ttm.r3a.public_toy.oracle.v1'
MODEL='ttm.r3a.model_input_only.v1'
DECL='Public R3A toy, labels public, NOT sealed FINAL or TTM learning evidence'
SEED=20261111
PEOPLE=('Lan','Minh','An','Binh','Hoa','Mai','Nam','Duy','Thao','Linh')
ITEMS=('key','map','cup','book','ball','note','coin','card')
GOALS=('read','write','draw','sing','travel','plant','repair','teach','cook','count','study','paint','search','build','clean','rest')
ALIASES=('Cedar','River','Piper','Sage','Dawn','Stone','Cloud','Amber')

def stable(x):return (json.dumps(x,ensure_ascii=False,sort_keys=True,separators=(',',':'))+'\n').encode()
def sha(b):return hashlib.sha256(b).hexdigest()
def render(e):
    op=e['op']
    if op=='INIT_HOLDER': return f"{e['item']} starts with {e['p']}."
    if op=='HANDOFF': return f"{e['p']} passes {e['item']} to {e['q']}."
    if op=='DEFINE_ALIAS':return f"The alias {e['alias']} names {e['p']}."
    if op=='SET_GOAL':return f"{e['p']} begins goal {e['g']}."
    if op=='DELEGATE_GOAL':return f"{e['p']} delegates goal {e['g']} to {e['q']}."
    if op=='CHANGE_GOAL':return f"{e['p']} changes goal from {e['old']} to {e['new']}."
    if op=='CANCEL_GOAL':return f"{e['p']} cancels goal {e['g']}."
    raise ValueError('BAD_OPERATION')

def run(es):
    st={'holders':{},'goals':{},'aliases':{}}
    def resolve(x):return st['aliases'].get(x,x)
    for e in es:
        op=e['op']
        if op=='DEFINE_ALIAS':
            if e['alias'] in st['aliases'] or e['alias'] in PEOPLE or e['p'] not in PEOPLE:raise ValueError('ALIAS_PRECONDITION')
            st['aliases'][e['alias']]=e['p']
        elif op=='INIT_HOLDER':
            if e['item'] in st['holders'] or resolve(e['p']) not in PEOPLE:raise ValueError('INIT_PRECONDITION')
            st['holders'][e['item']]=resolve(e['p'])
        elif op=='HANDOFF':
            p,q=resolve(e['p']),resolve(e['q'])
            if st['holders'].get(e['item'])!=p or p==q or q not in PEOPLE:raise ValueError('HANDOFF_PRECONDITION')
            st['holders'][e['item']]=q
        elif op=='SET_GOAL':
            p=resolve(e['p'])
            if p not in PEOPLE or st['goals'].get(p) is not None:raise ValueError('SET_PRECONDITION')
            st['goals'][p]=e['g']
        elif op=='DELEGATE_GOAL':
            p,q=resolve(e['p']),resolve(e['q'])
            if p==q or st['goals'].get(p)!=e['g'] or st['goals'].get(q) is not None:raise ValueError('DELEGATE_PRECONDITION')
            st['goals'][p]=None;st['goals'][q]=e['g']
        elif op=='CHANGE_GOAL':
            p=resolve(e['p'])
            if st['goals'].get(p)!=e['old'] or e['old']==e['new']:raise ValueError('CHANGE_PRECONDITION')
            st['goals'][p]=e['new']
        elif op=='CANCEL_GOAL':
            p=resolve(e['p'])
            if st['goals'].get(p)!=e['g']:raise ValueError('CANCEL_PRECONDITION')
            st['goals'][p]=None
        else:raise ValueError('UNKNOWN_OP')
    return st

def ans(st,question):
    if question.startswith('Who holds '):return st['holders'][question[len('Who holds '):-1]]
    k=question[len('What is '):-len(' goal?')]
    return st['goals'].get(st['aliases'].get(k,k)) or 'NONE'

def I(item,p):return dict(op='INIT_HOLDER',item=item,p=p)
def H(item,p,q):return dict(op='HANDOFF',item=item,p=p,q=q)
def A(alias,p):return dict(op='DEFINE_ALIAS',alias=alias,p=p)
def S(p,g):return dict(op='SET_GOAL',p=p,g=g)
def D(p,q,g):return dict(op='DELEGATE_GOAL',p=p,q=q,g=g)
def C(p,g):return dict(op='CANCEL_GOAL',p=p,g=g)
def X(p,old,new):return dict(op='CHANGE_GOAL',p=p,old=old,new=new)

def interleave(chains,rng):
    queues=[list(c) for c in chains];out=[]
    while any(queues):
        available=[i for i,q in enumerate(queues) if q]
        # All cross-chain persons/items are disjoint, so these interleavings preserve preconditions.
        idx=rng.choice(available);out.append(queues[idx].pop(0))
    return out

def group(fam,split,index,rng):
    ppl=rng.sample(PEOPLE,8); a,b,c,d,e,f,g,h=ppl
    items=rng.sample(ITEMS,3);item,other,third=items
    gs=rng.sample(GOALS,8);alias=rng.choice(ALIASES)
    if fam=='T1':
        target_q=f'Who holds {item}?'; distract_q=f'Who holds {other}?'
        # One changed alias definition, a downstream handoff text remains EXACTLY the same.
        target=[A(alias,d),I(item,a),H(item,a,b),H(item,b,c),H(item,c,alias)]
        if split=='CHALLENGE':target.insert(3,H(item,b,e));target[4]=H(item,e,c)
        noise=[[I(other,f),H(other,f,g)],[I(third,g),H(third,g,h)]]
        old,new=d,e
        intervention=lambda es:next(k for k,x in enumerate(es) if x['op']=='DEFINE_ALIAS' and x['alias']==alias)
        replacement=A(alias,new)
    elif fam=='T2':
        target_q=f'What is {b} goal?';distract_q=f'What is {d} goal?'
        if split=='DEV':
            # Replacing a DELEGATE with a CANCEL changes target from g -> NONE.
            target=[S(a,gs[0]),D(a,b,gs[0])]
            replacement=C(a,gs[0]);old,new='delegate','cancel'
            intervention=lambda es:next(k for k,x in enumerate(es) if x['op']=='DELEGATE_GOAL' and x['p']==a)
        else:
            # Target receives a goal; last answer is NONE in A, changed goal in B.
            target=[S(a,gs[0]),D(a,b,gs[0]),C(b,gs[0])]
            replacement=X(b,gs[0],gs[1]);old,new='cancel','change'
            intervention=lambda es:next(k for k,x in enumerate(es) if x['op']=='CANCEL_GOAL' and x['p']==b)
        noise=[[S(d,gs[2]),X(d,gs[2],gs[3])],[S(f,gs[4]),D(f,g,gs[4])]]
        if split=='DEV':noise[1].append(X(g,gs[4],gs[5]))
        else:noise[1].extend([X(g,gs[4],gs[5]),C(g,gs[5])])
    elif fam=='T3':
        target_q=f'What is {alias} goal?';distract_q=f'What is {h} goal?'
        # Neither candidate's target-goal value is written directly under the query alias.
        target=[S(a,gs[0]),D(a,b,gs[0]),S(c,gs[1]),D(c,d,gs[1]),A(alias,b)]
        if split=='CHALLENGE':target.insert(4,X(d,gs[1],gs[6]))
        noise=[[S(h,gs[2]),X(h,gs[2],gs[3])],[S(f,gs[4]),C(f,gs[4])]]
        old,new=b,d;replacement=A(alias,new)
        intervention=lambda es:next(k for k,x in enumerate(es) if x['op']=='DEFINE_ALIAS' and x['alias']==alias)
    else:raise ValueError('BAD_FAM')
    esA=interleave([target]+noise,rng)
    idx=intervention(esA)
    esB=[dict(x) for x in esA];esB[idx]=replacement
    stA,stB=run(esA),run(esB)
    answers=[ans(stA,target_q),ans(stA,distract_q),ans(stB,target_q),ans(stB,distract_q)]
    if not (answers[0]!=answers[2] and answers[1]==answers[3] and answers[0]!=answers[1] and answers[2]!=answers[3]):raise ValueError('FOUR_CELL_CONSTRAINT_FAIL')
    cells=[]
    for variant,events,st in (('A',esA,stA),('B',esB,stB)):
        for which,q in (('T',target_q),('D',distract_q)):
            cells.append({'cell':variant+'_'+which,'story':'\n'.join(map(render,events)),
                          'question':q,'answer':ans(st,q),'source_events':events})
    return {'group_id':f'{fam}-{split}-{index:03d}','family':fam,'split':split,
            'intervention_index':idx,'cells':cells}

def build():
    rng=random.Random(SEED+3)
    groups=[group(fam,split,i,rng) for fam in ('T1','T2','T3') for split in ('DEV','CHALLENGE') for i in range(16)]
    oracle={'schema':SCHEMA,'declaration':DECL,'seed':SEED,'labels_public':True,'sealed_final':False,
            'counts':{'groups':96,'inputs':384,'by_family':{'T1':32,'T2':32,'T3':32}},'groups':groups}
    model_rows=[{'story':c['story'],'question':c['question']} for g in groups for c in g['cells']]
    rng.shuffle(model_rows)  # distinct from group layout; no group/variant/split metadata in model input
    model={'schema':MODEL,'records':model_rows}
    return oracle,model

def main():
    p=argparse.ArgumentParser();p.add_argument('--oracle',required=True);p.add_argument('--model',required=True);a=p.parse_args()
    if Path(a.oracle).resolve()==Path(a.model).resolve():raise SystemExit('SAME_OUTPUT')
    oracle,model=build()
    for x,y in ((a.oracle,oracle),(a.model,model)):
        target=Path(x)
        if target.exists():raise SystemExit('NO_OVERWRITE')
        target.parent.mkdir(parents=True,exist_ok=True)
        b=stable(y);target.write_bytes(b);print(x,len(b),sha(b))
if __name__=='__main__':main()
