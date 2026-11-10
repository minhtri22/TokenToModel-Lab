#!/usr/bin/env python3
"""Independent R3A validator and visible-text state oracle. No generator import.
QA only. Public toy labels MUST NOT be used as scientific blinded FINAL.
"""
from __future__ import annotations
import argparse,collections,hashlib,json,re
from pathlib import Path
MODEL='ttm.r3a.model_input_only.v1'
ORACLE='ttm.r3a.public_toy.oracle.v1'
DECL='Public R3A toy, labels public, NOT sealed FINAL or TTM learning evidence'
PEOPLE=set(('Lan','Minh','An','Binh','Hoa','Mai','Nam','Duy','Thao','Linh'))
ITEMS=set(('key','map','cup','book','ball','note','coin','card'))
GOALS=set(('read','write','draw','sing','travel','plant','repair','teach','cook','count','study','paint','search','build','clean','rest'))
ALIASES=set(('Cedar','River','Piper','Sage','Dawn','Stone','Cloud','Amber'))
PATS={
 'INIT_HOLDER':re.compile(r'^([a-z]+) starts with ([A-Za-z]+)\.$'),
 'HANDOFF':re.compile(r'^([A-Za-z]+) passes ([a-z]+) to ([A-Za-z]+)\.$'),
 'DEFINE_ALIAS':re.compile(r'^The alias ([A-Za-z]+) names ([A-Za-z]+)\.$'),
 'SET_GOAL':re.compile(r'^([A-Za-z]+) begins goal ([a-z]+)\.$'),
 'DELEGATE_GOAL':re.compile(r'^([A-Za-z]+) delegates goal ([a-z]+) to ([A-Za-z]+)\.$'),
 'CHANGE_GOAL':re.compile(r'^([A-Za-z]+) changes goal from ([a-z]+) to ([a-z]+)\.$'),
 'CANCEL_GOAL':re.compile(r'^([A-Za-z]+) cancels goal ([a-z]+)\.$')}
RE_HOLDER=re.compile(r'^Who holds ([a-z]+)\?$')
RE_GOAL=re.compile(r'^What is ([A-Za-z]+) goal\?$')
class Fail(ValueError):pass

def need(flag,reason):
    if not flag:raise Fail(reason)

def hook(pairs):
    seen={}
    for k,v in pairs:
        need(k not in seen,'DUPLICATE_JSON_KEY')
        seen[k]=v
    return seen

def from_bytes(b):
    need(type(b) is bytes and len(b)<4000000,'JSON_TOO_LARGE')
    return json.loads(b.decode('utf-8'),object_pairs_hook=hook,
                      parse_constant=lambda v: (_ for _ in ()).throw(Fail('NONFINITE_JSON')))

def model_check(m):
    need(type(m) is dict and set(m)=={'schema','records'},'MODEL_ROOT_FIELDS')
    need(m['schema']==MODEL,'MODEL_SCHEMA')
    rows=m['records']
    need(type(rows) is list and len(rows)==384,'MODEL_RECORD_COUNT')
    for r in rows:
        need(type(r) is dict and set(r)=={'story','question'},'MODEL_LEAK_OR_FIELDS')
        need(type(r['story']) is str and type(r['question']) is str,'MODEL_TEXT_TYPES')
        need(5<=len(r['story'].encode('utf-8'))<2200,'STORY_LENGTH')
        need(8<=len(r['question'])<100,'QUESTION_LENGTH')
    return rows

def events_from_story(story):
    lines=story.split('\n')
    need(6<=len(lines)<=12,'EVENT_COUNT')
    out=[]
    for line in lines:
        matches=[(op,p.fullmatch(line)) for op,p in PATS.items() if p.fullmatch(line)]
        need(len(matches)==1,'EVENT_GRAMMAR')
        op,m=matches[0];f=m.groups()
        if op=='INIT_HOLDER':e={'op':op,'item':f[0],'p':f[1]}
        elif op=='HANDOFF':e={'op':op,'p':f[0],'item':f[1],'q':f[2]}
        elif op=='DEFINE_ALIAS':e={'op':op,'alias':f[0],'p':f[1]}
        elif op=='SET_GOAL':e={'op':op,'p':f[0],'g':f[1]}
        elif op=='DELEGATE_GOAL':e={'op':op,'p':f[0],'g':f[1],'q':f[2]}
        elif op=='CHANGE_GOAL':e={'op':op,'p':f[0],'old':f[1],'new':f[2]}
        else:e={'op':op,'p':f[0],'g':f[1]}
        out.append(e)
    return out

def interpret(story,question):
    es=events_from_story(story)
    state={'holders':{},'goals':{},'aliases':{}}
    def person(v):
        if v in PEOPLE:return v
        need(v in state['aliases'],'UNKNOWN_ALIAS')
        return state['aliases'][v]
    for e in es:
        op=e['op']
        if op=='DEFINE_ALIAS':
            need(e['alias'] in ALIASES and e['alias'] not in state['aliases'] and e['p'] in PEOPLE,'AMBIGUOUS_OR_INVALID_ALIAS')
            state['aliases'][e['alias']]=e['p']
        elif op=='INIT_HOLDER':
            need(e['item'] in ITEMS and e['item'] not in state['holders'],'INIT_FAIL')
            state['holders'][e['item']]=person(e['p'])
        elif op=='HANDOFF':
            p,q=person(e['p']),person(e['q']);i=e['item']
            need(i in ITEMS and p!=q and state['holders'].get(i)==p,'BAD_HANDOFF')
            state['holders'][i]=q
        elif op=='SET_GOAL':
            p=person(e['p']);need(e['g'] in GOALS and state['goals'].get(p) is None,'BAD_GOAL_SET')
            state['goals'][p]=e['g']
        elif op=='DELEGATE_GOAL':
            p,q=person(e['p']),person(e['q']);g=e['g']
            need(g in GOALS and p!=q and state['goals'].get(p)==g and state['goals'].get(q) is None,'BAD_GOAL_DELEGATE')
            state['goals'][p]=None;state['goals'][q]=g
        elif op=='CHANGE_GOAL':
            p=person(e['p']);need(e['old'] in GOALS and e['new'] in GOALS and e['old']!=e['new'] and state['goals'].get(p)==e['old'],'BAD_GOAL_CHANGE')
            state['goals'][p]=e['new']
        elif op=='CANCEL_GOAL':
            p=person(e['p']);need(e['g'] in GOALS and state['goals'].get(p)==e['g'],'BAD_GOAL_CANCEL')
            state['goals'][p]=None
    m=RE_HOLDER.fullmatch(question)
    if m:
        key=m.group(1);need(key in state['holders'],'UNKNOWN_ITEM_QUERY')
        answer=state['holders'][key];kind='holder';resolved=key
    else:
        m=RE_GOAL.fullmatch(question);need(m is not None,'MALFORMED_QUESTION')
        key=m.group(1);resolved=person(key);answer=state['goals'].get(resolved) or 'NONE';kind='goal'
    return answer,kind,resolved,es,state

def query_dependent_motif(es,kind,key):
    # Query-conditioned typed event dependencies: no lexical names, but references
    # and target/distractor relationship explicitly retained. Split signature
    # is an instrumentation check, not a statistical guarantee of generalization.
    alias={e['alias']:e['p'] for e in es if e['op']=='DEFINE_ALIAS'}
    def res(v):return alias.get(v,v)
    out=[]
    for e in es:
        op=e['op']
        if kind=='holder':role=('target' if e.get('item')==key else 'nontarget')
        else:
            affected=([e.get('p'),e.get('q')] if op=='DELEGATE_GOAL' else [e.get('p')])
            role=('target' if key in set(res(x) for x in affected if x) else 'nontarget')
        via_alias=any(v in alias for v in (e.get('p'),e.get('q')))
        out.append((op,role,'alias' if via_alias else 'direct'))
    return (kind,tuple(out))

def validate(oracle,model):
    rows=model_check(model) # fail-closed BEFORE oracle projection
    need(type(oracle) is dict and set(oracle)=={'schema','declaration','seed','labels_public','sealed_final','counts','groups'},'ORACLE_ROOT_FIELDS')
    need(oracle['schema']==ORACLE and oracle['seed']==20261111,'ORACLE_SCHEMA')
    need(oracle['declaration']==DECL and oracle['labels_public'] is True and oracle['sealed_final'] is False,'PUBLIC_DECLARATION')
    groups=oracle['groups'];need(type(groups) is list and len(groups)==96,'GROUP_COUNT')
    need(oracle['counts']=={'groups':96,'inputs':384,'by_family':{'T1':32,'T2':32,'T3':32}},'COUNT_FIELDS')
    seen=set();projection=[];by_split={'DEV':set(),'CHALLENGE':set()};motifs={'DEV':set(),'CHALLENGE':set()}
    split_count=collections.Counter();real_answers=collections.Counter();positive=0
    for g in groups:
        need(type(g) is dict and set(g)=={'group_id','family','split','intervention_index','cells'},'GROUP_FIELDS')
        fam,split=g['family'],g['split'];idx=g['intervention_index']
        need(fam in ('T1','T2','T3') and split in ('DEV','CHALLENGE'),'BAD_FAMILY_SPLIT')
        gid=g['group_id'];need(gid==f'{fam}-{split}-{int(gid[-3:]):03d}' and gid not in seen,'GROUP_ID')
        seen.add(gid);split_count[(fam,split)]+=1
        need(type(idx) is int and idx>=0,'BAD_INTERVENTION_INDEX')
        cells=g['cells'];need(type(cells) is list and len(cells)==4,'FOUR_CELLS_REQUIRED')
        bycell={}
        for c in cells:
            need(type(c) is dict and set(c)=={'cell','story','question','answer','source_events'},'CELL_FIELDS')
            name=c['cell'];need(name not in bycell,'DUPLICATE_CELL')
            answer,kind,key,es,state=interpret(c['story'],c['question'])
            need(answer==c['answer'],'ANSWER_MISMATCH')
            need(es==c['source_events'],'SOURCE_EVENT_MISMATCH')
            bycell[name]=(c,answer,kind,key,es)
            projection.append((c['story'],c['question']))
            by_split[split].add((c['story'],c['question']))
            motifs[split].add(query_dependent_motif(es,kind,key))
            real_answers[(fam,answer)]+=1
        need(set(bycell)=={'A_T','A_D','B_T','B_D'},'FOUR_CELL_IDS')
        aT,aD,bT,bD=(bycell[k] for k in ('A_T','A_D','B_T','B_D'))
        need(aT[1]!=bT[1] and aD[1]==bD[1],'TARGET_CHANGE_DISTRACTOR_STABLE')
        need(aT[0]['story']==aD[0]['story'] and bT[0]['story']==bD[0]['story'] and aT[0]['story']!=bT[0]['story'],'FACTORIAL_STORIES')
        need(aT[0]['question']==bT[0]['question'] and aD[0]['question']==bD[0]['question'] and aT[0]['question']!=aD[0]['question'],'QUESTION_FACTORS')
        ea,eb=aT[4],bT[4];need(len(ea)==len(eb) and idx<len(ea),'EVENT_COUNT_OR_IDX')
        diffs=[i for i,(x,y) in enumerate(zip(ea,eb)) if x!=y]
        need(diffs==[idx],'ONLY_ONE_EVENT_DIFFERENCE')
        if fam=='T1':
            need(ea[idx]['op']=='DEFINE_ALIAS' and eb[idx]['op']=='DEFINE_ALIAS','ALIAS_INTERVENTION')
            need(any(e['op']=='HANDOFF' and e['q']==ea[idx]['alias'] for e in ea[idx+1:]),'ALIAS_NOT_ANSWER_CRITICAL')
            need(sum(e['op']=='HANDOFF' and e['item']==aT[3] for e in ea)>=3,'NO_MULTIHOP')
        if fam=='T2':
            need(any(e['op']=='DELEGATE_GOAL' for e in ea) and any(e['op']=='CANCEL_GOAL' for e in ea+eb),'NO_DELEGATE_CANCEL')
            need('NONE' in (aT[1],bT[1]),'NONE_NOT_CRITICAL')
        if fam=='T3':
            need(ea[idx]['op']=='DEFINE_ALIAS' and eb[idx]['op']=='DEFINE_ALIAS','T3_NO_ALIAS_INTERVENTION')
            need(aT[0]['question'].find(ea[idx]['alias'])>=0,'QUERY_NOT_ALIAS')
        positive+=1
    need(all(split_count[(f,s)]==16 for f in ('T1','T2','T3') for s in ('DEV','CHALLENGE')),'SPLIT_GROUPS')
    need(by_split['DEV'].isdisjoint(by_split['CHALLENGE']),'CROSS_SPLIT_TEXT_LEAK')
    need(motifs['DEV'].isdisjoint(motifs['CHALLENGE']),'QUERY_DEPENDENT_MOTIF_CROSS_SPLIT')
    need(len(projection)==384 and len(set(projection))==384,'DUPLICATE_INPUT')
    need(len(rows)==384 and collections.Counter(projection)==collections.Counter((r['story'],r['question']) for r in rows),'PROJECTION_MISMATCH')
    # Fixed A_T/A_D/B_T/B_D order must no longer describe the model-input rows.
    need([(r['story'],r['question']) for r in rows] != projection,'MODEL_INPUT_NOT_SHUFFLED')
    return {'status':'PASS_R3A_PUBLIC_TOY_SOURCE_AND_VALIDATOR_ONLY','groups':96,'model_inputs':384,'four_cell_counterfactuals':positive,
      'oracle_correct':384,'query_dependent_motifs_DEV':len(motifs['DEV']),'query_dependent_motifs_CHALLENGE':len(motifs['CHALLENGE']),
      'query_dependent_motif_cross_split':len(motifs['DEV']&motifs['CHALLENGE']),
      'NONE_target_answers':sum(v for (f,a),v in real_answers.items() if f=='T2' and a=='NONE'),
      'model_input_shuffled':True,'public_labels':True,'neural_evaluation':'NOT_EXECUTED','GPU_training':'NOT_EXECUTED'}

def main():
    p=argparse.ArgumentParser();p.add_argument('--oracle',required=True);p.add_argument('--model',required=True);p.add_argument('--out',required=True);a=p.parse_args()
    rb=Path(a.oracle).read_bytes();mb=Path(a.model).read_bytes()
    o,m=from_bytes(rb),from_bytes(mb);report=validate(o,m)
    report['oracle_sha256']=hashlib.sha256(rb).hexdigest();report['model_sha256']=hashlib.sha256(mb).hexdigest()
    out=Path(a.out)
    if out.exists():raise SystemExit('NO_OVERWRITE')
    out.write_bytes((json.dumps(report,ensure_ascii=False,sort_keys=True,indent=2)+'\n').encode());print(json.dumps(report,sort_keys=True))
if __name__=='__main__':main()
