#!/usr/bin/env python3
"""TTM R3 strict visible-text checker: no import of toy generator.
Does not use source_events, answer, graph labels to derive predicted answers.
Only public toy consistency; NOT neural/model science validation.
"""
from __future__ import annotations
import argparse,hashlib,json,re
from collections import Counter,defaultdict
from pathlib import Path

ORACLE_SCHEMA='ttm.r3.structural_state_graph.public_oracle.v1'
MODEL_SCHEMA='ttm.r3.story_question_only.v1'
PUBLIC_DECL='Public R3 structural toy; labels public; NOT sealed FINAL, NOT TTM neural evidence'
FAMILIES=('T1','T2','T3')
PEOPLE=frozenset(('Lan','Minh','An','Binh','Hoa','Mai','Nam','Duy','Thao','Linh'))
ITEMS=frozenset(('key','map','cup','book','ball','note','coin','card'))
GOALS=frozenset(('read','write','draw','sing','travel','plant','repair','teach','cook','count','study','paint','search','build','clean','rest'))
ALIASES=frozenset(('Cedar','River','Piper','Sage','Dawn','Stone','Cloud','Amber'))
MODEL_ROOT={'schema','records'}
RECORD_KEYS={'story','question'}
ORACLE_ROOT={'schema','declaration','labels_public','sealed_final','seed','counts','groups'}
GROUP_FIELDS={'group_id','family','split','cells','intervention_index','intervention_event_type'}
CELL_FIELDS={'cell','story','question','answer','source_events'}
PATTERNS=[
('INIT_HOLDER',re.compile(r'^([a-z]+) starts with ([A-Za-z]+)\.$')),
('HANDOFF',re.compile(r'^([A-Za-z]+) passes ([a-z]+) to ([A-Za-z]+)\.$')),
('DEFINE_ALIAS',re.compile(r'^The alias ([A-Za-z]+) names ([A-Za-z]+)\.$')),
('SET_GOAL',re.compile(r'^([A-Za-z]+) begins goal ([a-z]+)\.$')),
('DELEGATE_GOAL',re.compile(r'^([A-Za-z]+) delegates goal ([a-z]+) to ([A-Za-z]+)\.$')),
('CHANGE_GOAL',re.compile(r'^([A-Za-z]+) changes goal from ([a-z]+) to ([a-z]+)\.$')),
('CANCEL_GOAL',re.compile(r'^([A-Za-z]+) cancels goal ([a-z]+)\.$')),
]
Q_HOLDER=re.compile(r'^Who holds ([a-z]+)\?$')
Q_GOAL=re.compile(r'^What is ([A-Za-z]+) goal\?$')
class Invalid(ValueError): pass

def need(cond,why):
    if not cond:raise Invalid(why)

def strict_pairs(pairs):
    out={}
    for k,v in pairs:
        if k in out:raise Invalid('JSON_DUPLICATE_KEY')
        out[k]=v
    return out

def load_json(raw):
    need(isinstance(raw,bytes) and len(raw)<4000000,'RAW_INPUT_TOO_LARGE')
    try:return json.loads(raw.decode('utf-8'),object_pairs_hook=strict_pairs,parse_constant=lambda x: (_ for _ in ()).throw(Invalid('NONFINITE_JSON_VALUE')))
    except (UnicodeDecodeError,json.JSONDecodeError) as ex:raise Invalid('INVALID_UTF8_OR_JSON') from ex

def check_model(model):
    need(type(model) is dict and set(model)==MODEL_ROOT,'MODEL_ROOT_FIELD_ALLOWLIST')
    need(model.get('schema')==MODEL_SCHEMA,'MODEL_SCHEMA')
    rows=model.get('records')
    need(type(rows) is list and len(rows)==384,'MODEL_INPUT_COUNT')
    for r in rows:
        need(type(r) is dict and set(r)==RECORD_KEYS,'MODEL_RECORD_METADATA_LEAK')
        for k in ('story','question'):
            need(type(r[k]) is str and 2<=len(r[k].encode('utf-8'))<=2200,'MODEL_TEXT_LENGTH')
    return rows

def parse_story(text):
    need(type(text) is str and len(text)<2000,'STORY_TYPE_OR_LENGTH')
    lines=text.split('\n')
    need(6<=len(lines)<=12,'STORY_EVENT_COUNT')
    events=[]
    for line in lines:
        matches=[]
        for op,pattern in PATTERNS:
            m=pattern.fullmatch(line)
            if m:matches.append((op,m.groups()))
        need(len(matches)==1,'UNRECOGNIZED_OR_AMBIGUOUS_EVENT')
        op,fields=matches[0]
        if op=='INIT_HOLDER':e=dict(op=op,item=fields[0],p=fields[1])
        elif op=='HANDOFF':e=dict(op=op,p=fields[0],item=fields[1],q=fields[2])
        elif op=='DEFINE_ALIAS':e=dict(op=op,alias=fields[0],p=fields[1])
        elif op=='SET_GOAL':e=dict(op=op,p=fields[0],g=fields[1])
        elif op=='DELEGATE_GOAL':e=dict(op=op,p=fields[0],g=fields[1],q=fields[2])
        elif op=='CHANGE_GOAL':e=dict(op=op,p=fields[0],old=fields[1],new=fields[2])
        elif op=='CANCEL_GOAL':e=dict(op=op,p=fields[0],g=fields[1])
        else:raise Invalid('UNRECOGNIZED_OPERATION')
        events.append(e)
    return events

def run_visible(events):
    state=dict(holders={},goals={},aliases={})
    def res(p):
        need(type(p) is str,'REF_TYPE')
        if p in PEOPLE:return p
        need(p in state['aliases'],'UNRESOLVED_ALIAS_OR_UNKNOWN_PERSON')
        return state['aliases'][p]
    for e in events:
        o=e['op']
        if o=='INIT_HOLDER':
            need(e['item'] in ITEMS and e['item'] not in state['holders'],'INIT_PRECONDITION')
            state['holders'][e['item']]=res(e['p'])
        elif o=='HANDOFF':
            p,q=res(e['p']),res(e['q']);it=e['item']
            need(it in ITEMS and state['holders'].get(it)==p and p!=q,'HANDOFF_PRECONDITION')
            state['holders'][it]=q
        elif o=='DEFINE_ALIAS':
            al=e['alias']
            need(al in ALIASES and al not in state['aliases'] and al not in PEOPLE,'ALIAS_AMBIGUOUS_OR_REDEFINED')
            need(e['p'] in PEOPLE,'ALIAS_REFERENT_NOT_EXPLICIT')
            state['aliases'][al]=e['p']
        elif o=='SET_GOAL':
            p=res(e['p'])
            need(e['g'] in GOALS and state['goals'].get(p) is None,'SET_GOAL_PRECONDITION')
            state['goals'][p]=e['g']
        elif o=='DELEGATE_GOAL':
            p,q=res(e['p']),res(e['q']);g=e['g']
            need(g in GOALS and p!=q and state['goals'].get(p)==g and state['goals'].get(q) is None,'DELEGATE_GOAL_PRECONDITION')
            state['goals'][p]=None;state['goals'][q]=g
        elif o=='CHANGE_GOAL':
            p=res(e['p'])
            need(e['old'] in GOALS and e['new'] in GOALS and e['old']!=e['new'] and state['goals'].get(p)==e['old'],'CHANGE_GOAL_PRECONDITION')
            state['goals'][p]=e['new']
        elif o=='CANCEL_GOAL':
            p=res(e['p'])
            need(e['g'] in GOALS and state['goals'].get(p)==e['g'],'CANCEL_GOAL_PRECONDITION')
            state['goals'][p]=None
        else:raise Invalid('BAD_EVENT')
    return state

def query_visible(question,state):
    need(type(question) is str,'QUESTION_TYPE')
    m=Q_HOLDER.fullmatch(question)
    if m:
        item=m.group(1)
        need(item in ITEMS and item in state['holders'],'UNKNOWN_HOLDER_QUERY')
        return item,state['holders'][item],'holder'
    m=Q_GOAL.fullmatch(question)
    need(m is not None,'MALFORMED_QUESTION')
    p=m.group(1)
    person=p if p in PEOPLE else state['aliases'].get(p)
    need(person in PEOPLE,'UNKNOWN_GOAL_REFERENT')
    return person,state['goals'].get(person) or 'NONE','goal'

def one_cell(cell):
    need(type(cell) is dict and set(cell)==CELL_FIELDS,'CELL_FIELDS')
    es=parse_story(cell['story'])
    st=run_visible(es)
    key,ans,kind=query_visible(cell['question'],st)
    need(cell['answer']==ans,'VISIBLE_TEXT_ANSWER_MISMATCH')
    need(cell['source_events']==es,'EVENT_SOURCE_TAMPERED')
    return es,key,ans,kind

def motif(events,family,queried_key):
    # Structure signature intentionally strips lexical identity. The signature
    # abstracts per-key transition dependencies, not textual row position.
    if family=='T1':
        n=Counter(e['item'] for e in events if e['op']=='HANDOFF')
        # The 3-step chain is the unique target structure, regardless of question.
        return ('T1',tuple(sorted(n.values())))
    if family=='T2':
        # person-local event sequences in visible order (delegation counted at both ends)
        streams=defaultdict(list)
        for e in events:
            if e['op'] not in ('SET_GOAL','CHANGE_GOAL','CANCEL_GOAL','DELEGATE_GOAL'):continue
            streams[e['p']].append(e['op'])
            if e['op']=='DELEGATE_GOAL':streams[e['q']].append('RECEIVE')
        return ('T2',tuple(sorted(tuple(s) for s in streams.values())))
    if family=='T3':
        # Ordered typed operations in the 6-step target chain, ignoring interleaved distractor items.
        owners=Counter(e['item'] for e in events if e['op'] in ('INIT_HOLDER','HANDOFF'))
        target=max(owners,key=owners.get)
        core=[]
        for e in events:
            if e['op'] in ('INIT_HOLDER','HANDOFF') and e['item']==target:core.append(e['op'])
            elif e['op']=='DEFINE_ALIAS':core.append('DEFINE_ALIAS')
        return ('T3',tuple(core))
    raise Invalid('UNKNOWN_FAMILY')

def check(oracle,model):
    rows=check_model(model) # must be FIRST: no oracle/projection processing until it passes
    need(type(oracle) is dict and set(oracle)==ORACLE_ROOT,'ORACLE_ROOT_FIELDS')
    need(oracle['schema']==ORACLE_SCHEMA and oracle['seed']==20261111,'ORACLE_SCHEMA_OR_SEED')
    need(oracle['declaration']==PUBLIC_DECL and oracle['labels_public'] is True and oracle['sealed_final'] is False,'FALSE_SEALED_OR_PUBLIC_DECLARATION')
    groups=oracle['groups']
    need(type(groups) is list and len(groups)==96,'GROUP_COUNT')
    seen_gids=set();seen_inputs=set();expected=[];groups_count=Counter();motifs=defaultdict(set)
    baseline=Counter();answer_changes=0;final_keys=Counter();cell_count=0
    text_by_split=defaultdict(set)
    for g in groups:
        need(type(g) is dict and set(g)==GROUP_FIELDS,'GROUP_FIELDS')
        gid=g['group_id'];fam=g['family'];split=g['split']
        need(type(gid) is str and re.fullmatch(r'T[123]-(?:DEV|CHALLENGE)-\d{3}',gid) is not None,'GROUP_ID')
        need(gid not in seen_gids and gid.startswith(fam+'-'+split+'-'),'DUPLICATE_OR_BAD_GROUP_ID')
        seen_gids.add(gid)
        need(fam in FAMILIES and split in ('DEV','CHALLENGE'),'FAMILY_SPLIT')
        idx=int(gid.split('-')[-1]);need(idx in range(16),'GROUP_INDEX_RANGE')
        groups_count[(fam,split)]+=1
        cells=g['cells'];need(type(cells) is list and len(cells)==4,'FOUR_CELLS_REQUIRED')
        need([c['cell'] for c in cells]==['A_T','A_D','B_T','B_D'],'FACTORIAL_CELL_ORDER')
        results={}
        for c in cells:
            es,key,ans,kind=one_cell(c)
            k=(c['story'],c['question'])
            need(k not in seen_inputs,'DUPLICATE_MODEL_INPUT')
            seen_inputs.add(k);expected.append({'story':c['story'],'question':c['question']})
            results[c['cell']]={'events':es,'key':key,'answer':ans,'kind':kind}
            text_by_split[split].add(c['story'])
            cell_count+=1
            # Local shallow heuristic: only direct first-event initialization/SET is handled.
            if kind=='holder':
                vals=[e['p'] for e in es if e['op']=='INIT_HOLDER' and e['item']==key]
                baseline['keyed_direct_initialization_correct']+=int(bool(vals) and vals[-1]==ans)
            else:
                vals=[e['g'] for e in es if e['op']=='SET_GOAL' and e['p']==key]
                baseline['keyed_direct_initialization_correct']+=int((vals[-1] if vals else 'NONE')==ans)
            baseline['last_story_line_mention_correct']+=int(ans in es[-1].values())
            final_keys[split]+=int(any(v==ans for v in es[-1].values()))
        need(results['A_T']['key']==results['B_T']['key'],'TARGET_QUERY_NOT_MATCHED')
        need(results['A_D']['key']==results['B_D']['key'],'DISTRACTOR_QUERY_NOT_MATCHED')
        need(results['A_T']['key']!=results['A_D']['key'],'TARGET_DISTRACTOR_NOT_DISTINCT')
        need(results['A_T']['answer']!=results['B_T']['answer'],'TARGET_COUNTERFACTUAL_DID_NOT_FLIP')
        need(results['A_D']['answer']==results['B_D']['answer'],'DISTRACTOR_STATE_CHANGED')
        need(results['A_T']['answer']!=results['A_D']['answer'] and results['B_T']['answer']!=results['B_D']['answer'],'QUERY_BINDING_DEGENERATE')
        need(cells[0]['story']==cells[1]['story'] and cells[2]['story']==cells[3]['story'] and cells[0]['story']!=cells[2]['story'],'A_B_STORY_FACTORIAL_ERROR')
        ea,eb=results['A_T']['events'],results['B_T']['events']
        need(len(ea)==len(eb),'EVENT_COUNTS_CHANGED')
        changed=[i for i,(a,b) in enumerate(zip(ea,eb)) if a!=b]
        need(len(changed)==1 and changed[0]==g['intervention_index'],'SINGLE_EVENT_INTERVENTION_FAIL')
        need(ea[changed[0]]['op']==eb[changed[0]]['op']==g['intervention_event_type'],'INTERVENTION_EVENT_TYPE_CHANGED')
        need(all(motif(res['events'],fam,res['key'])==motif(ea,fam,results['A_T']['key']) for res in results.values()),'GRAPH_MOTIF_NOT_SAME_WITHIN_GROUP')
        motifs[split].add(motif(ea,fam,results['A_T']['key']))
        answer_changes+=1
        if fam=='T1':
            need(sum(e['op']=='HANDOFF' and e['item']==results['A_T']['key'] for e in ea)>=3,'INSUFFICIENT_HANDOFFS')
            need(len({e['item'] for e in ea if 'item' in e})>=3,'INSUFFICIENT_DISTRACTOR_ITEMS')
        elif fam=='T2':
            need(any(e['op']=='DELEGATE_GOAL' for e in ea) and any(e['op']=='CANCEL_GOAL' for e in ea),'NO_DELEGATE_OR_CANCEL')
        elif fam=='T3':
            need(sum(e['op']=='DEFINE_ALIAS' for e in ea)>=2 and any(e['op']=='HANDOFF' and (e['p'] in ALIASES or e['q'] in ALIASES) for e in ea),'NO_INDIRECT_ALIAS_CHAIN')
    for fam in FAMILIES:
        for split in ('DEV','CHALLENGE'):
            need(groups_count[(fam,split)]==16,'FAMILY_SPLIT_COUNTS')
    need(motifs['DEV'].isdisjoint(motifs['CHALLENGE']),'GRAPH_MOTIF_CROSS_SPLIT_LEAK')
    need(text_by_split['DEV'].isdisjoint(text_by_split['CHALLENGE']),'DUPLICATE_STORY_CROSS_SPLIT')
    need(rows==expected,'MODEL_PROJECTION_MISMATCH')
    need(oracle['counts']=={'groups':96,'inputs':384,'groups_by_family':{'T1':32,'T2':32,'T3':32}},'DECLARED_COUNTS_MISMATCH')
    need(cell_count==384 and answer_changes==96,'INCOMPLETE_COUNTERFACTUAL')
    need(baseline['keyed_direct_initialization_correct']<384,'R2A_DIRECT_SHORTCUT_UNRESOLVED')
    return {
       'status':'PASS_PUBLIC_R3_TOY_ORACLE_AND_STRICT_INPUT_ONLY',
       'groups':96,'model_inputs':384,'four_cells_per_group':4,
       'groups_by_family':{'T1':32,'T2':32,'T3':32},
       'family_split_group_counts':{f'{f}_{s}':groups_count[(f,s)] for f in FAMILIES for s in ('DEV','CHALLENGE')},
       'target_counterfactual_changes':answer_changes,
       'distractor_invariants':96,
       'independent_visible_text_rule_interpreter_correct':384,
       'shallow_keyed_direct_baseline_correct':baseline['keyed_direct_initialization_correct'],
       'last_line_value_mention_correct':baseline['last_story_line_mention_correct'],
       'graph_motifs_DEV':len(motifs['DEV']),'graph_motifs_CHALLENGE':len(motifs['CHALLENGE']),
       'graph_motifs_cross_split':len(motifs['DEV']&motifs['CHALLENGE']),
       'story_overlap_cross_split':len(text_by_split['DEV']&text_by_split['CHALLENGE']),
       'labels_public':True,'sealed_final':False,'original_TTM_training_steps':0,'GPU_calls':0,
       'claim_limit':'Toy source/parser feasibility only; no TTM inference, neural learning, O1 benefit or genuine blind FINAL'
    }

def verify_raw(oracle_bytes,model_bytes):
    model=load_json(model_bytes)
    check_model(model) # FIRST, fail-closed on potentially leaked model input
    oracle=load_json(oracle_bytes)
    result=check(oracle,model)
    result['oracle_sha256']=hashlib.sha256(oracle_bytes).hexdigest()
    result['model_input_sha256']=hashlib.sha256(model_bytes).hexdigest()
    return result

def main():
    ap=argparse.ArgumentParser();ap.add_argument('--oracle',required=True);ap.add_argument('--model-input',required=True);ap.add_argument('--output',required=True)
    a=ap.parse_args();out=Path(a.output)
    if out.exists():raise SystemExit('REFUSE_OVERWRITE')
    result=verify_raw(Path(a.oracle).read_bytes(),Path(a.model_input).read_bytes())
    out.parent.mkdir(parents=True,exist_ok=True)
    out.write_text(json.dumps(result,sort_keys=True,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
    print(json.dumps(result,sort_keys=True))
if __name__=='__main__':main()
