#!/usr/bin/env python3
"""V3 NON-TEST synthetic source fixture. No trained Reader, DEV/TEST, or retrieval scoring.

Only --write-once under the project root writes owner-private bytes. All cases
are synthetic; P1 unseen paraphrases are PROPOSALS pending two human raters.
"""
from __future__ import annotations
import argparse
import hashlib
import json
from collections import Counter
from pathlib import Path

SCHEMA = 'ttm.vm.v3.nontest256.provenance_negation_abstention.v1'
SEED = 'TTM_VM_V3_FRESH256_NONTEST_SEED_FROZEN_20261112_A1'
STRATA = (
    'P0_KNOWN_WIRING', 'P1_UNSEEN_PARAPHRASE', 'P2_PROVENANCE_UNIQUE',
    'P3_NEGATION_UNIQUE', 'N0_UNDERSPECIFIED', 'N1_DUPLICATE_MATCH',
    'N2_CONTRADICTORY_QUERY', 'N3_UNRESOLVABLE_OOV_OR_EXCLUSION'
)
ALPHABET = 'bcdfghjklmnpqrstvwxz'
SOURCES = ('src-north', 'src-south', 'src-east', 'src-west', 'src-central')
LABELS = ('bivor', 'caxen', 'doral', 'fekum', 'gilen', 'havor', 'jekin', 'kofur',
          'lamet', 'mipor', 'navek', 'pizol', 'raqum', 'sivel', 'tobak', 'wexil')
# Pre-existing frozen v2 canonical lexicon for comparable controlled baselines.
# All V3 P1 surface phrases are different from the v2 synonyms and templates.
VOCAB = {
 'color': ('amber','azure','crimson','indigo','ivory','silver','copper','jade','ochre','pearl','sable','coral'),
 'shape': ('round','square','triangular','spiral','oval','rectangular','conical','cubic','hexagonal','arched','tubular','ridged'),
 'material': ('ceramic','granite','cotton','leather','timber','glass','rubber','bronze','paper','linen','marble','slate')
}
# Novel phrase proposals only. These labels are NOT independently reviewed or signed.
# Two independent reviewers must confirm semantics on blinded P1 packets pre-science.
PROPOSED_P1 = {
 'color': ('honey-hued','sky-hued','scarlet-toned','night-hued','bone-pale','moon-metallic'),
 'shape': ('disklike','equal-four-sided','three-pointed','snailshell-turning','eggform','long-four-cornered'),
 'material': ('fired-earth','hard-igneous-rock','plant-fluff','tanned-skin','tree-derived','silica-clear')
}
ATTRS = ('color','shape','material')


def hx(*args: object) -> bytes:
    return hashlib.sha256((SEED + '|' + '|'.join(map(str,args))).encode('ascii')).digest()


def pick(n:int,*args:object) -> int:
    return int.from_bytes(hx(*args)[:8],'big') % n


def objkey(s:str,i:int,j:int)->str:
    raw=hx('obj',s,i,j)
    return 'obju'+''.join(ALPHABET[b%len(ALPHABET)] for b in raw[:11])


def triple(s:str,i:int,j:int):
    return tuple(VOCAB[attr][pick(12,'triple',s,i,j,attr)] for attr in ATTRS)


def encode_description(tr:tuple[str,str,str])->str:
    return f'color {tr[0]}; shape {tr[1]}; material {tr[2]}'


def replace_attr(tr:tuple[str,str,str],axis:int,inc:int)->tuple[str,str,str]:
    row=list(tr); values=VOCAB[ATTRS[axis]]
    row[axis]=values[(values.index(tr[axis])+inc)%len(values)]
    return tuple(row)


def make_case(s:str,i:int)->dict:
    if s not in STRATA or not isinstance(i,int) or not (0<=i<32):raise ValueError('BAD_CASE_ID')
    tgt=triple(s,i,0)
    if s=='P1_UNSEEN_PARAPHRASE':
        tgt=tuple(VOCAB[a][pick(6,'p1',s,i,a)] for a in ATTRS)
    sources=[SOURCES[pick(len(SOURCES),'source',s,i,j)] for j in range(32)]
    triples=[tgt]
    # Slot 1 deliberate source-specific / description collisions by stratum.
    if s in ('P2_PROVENANCE_UNIQUE','N1_DUPLICATE_MATCH'):
        triples.append(tgt)
        sources[1]=SOURCES[(SOURCES.index(sources[0])+1)%len(SOURCES)] if s=='P2_PROVENANCE_UNIQUE' else sources[0]
    elif s in ('P3_NEGATION_UNIQUE','N0_UNDERSPECIFIED'):
        triples.append(replace_attr(tgt,2,1))
    elif s=='N3_UNRESOLVABLE_OOV_OR_EXCLUSION':
        triples.append(replace_attr(tgt,2,1))
    else:
        triples.append(replace_attr(tgt,0,1))
    # Exactly 32 records; four strong near-neighbors are deterministic.
    axes = (0,1,0) if s in ('P3_NEGATION_UNIQUE','N0_UNDERSPECIFIED','N3_UNRESOLVABLE_OOV_OR_EXCLUSION') else (1,2,0)
    for j,axis in enumerate(axes,start=2):
        item=replace_attr(tgt,axis,j)
        if item not in triples:triples.append(item)
    slot=5
    while len(triples)<32:
        candidate=triple(s,i,slot)
        slot+=1
        if candidate in triples:continue
        # Do not make incidental c+s matches in underspec / negation / OOV cases.
        if s in ('P3_NEGATION_UNIQUE','N0_UNDERSPECIFIED','N3_UNRESOLVABLE_OOV_OR_EXCLUSION') and candidate[:2]==tgt[:2]:continue
        # P0/P1: do not accidentally duplicate target signature.
        if candidate==tgt:continue
        triples.append(candidate)
        if slot>10000:raise AssertionError('GENERATOR_LOOP_BOUNDED')
    assert len(triples)==32
    # For P2, only target has chosen source among equal triple; for N1, two have same source.
    if s=='P2_PROVENANCE_UNIQUE':
        assert sources[1]!=sources[0]
    keylist=[objkey(s,i,j) for j in range(32)]
    assert len(set(keylist))==32
    bank=[{'key':keylist[j],'source_id':sources[j], 'retrieval_text':encode_description(triples[j])} for j in range(32)]
    order=sorted(range(32),key=lambda j:(hx('shuffle',s,i,j),j))
    bank=[bank[j] for j in order]
    answer=LABELS[i%16] if s.startswith('P') else None
    target_key=keylist[0] if s.startswith('P') else None
    if s.startswith('P'):
        corr=[];wrong=[]
        for j in order:
            v=answer if j==0 else LABELS[(i+j+1)%16]  # no answer leak in non-target cards
            if j!=0 and v==answer:v=LABELS[(i+j+2)%16]
            corr.append({**bank[len(corr)],'value':v})
            wrong.append({**bank[len(wrong)],'value':LABELS[(i+1)%16] if j==0 else v})
        assert [x['key'] for x in corr]==[x['key'] for x in wrong]
    else:
        corr=None;wrong=None
    c,sh,m=tgt
    if s=='P0_KNOWN_WIRING':
        q=f'Which tag belongs to the {c} {sh} {m} archive item? Answer:'
        constraints={'positive':{'color':c,'shape':sh,'material':m},'negative':{},'source':None,'invalid':False}
    elif s=='P1_UNSEEN_PARAPHRASE':
        novel=[PROPOSED_P1[a][VOCAB[a].index(tgt[k])] for k,a in enumerate(ATTRS)]
        q=f'Which tag belongs to the {novel[0]} {novel[1]} {novel[2]} archive item? Answer:'
        constraints={'positive':{'color':c,'shape':sh,'material':m},'negative':{},'source':None,'invalid':False}
    elif s=='P2_PROVENANCE_UNIQUE':
        q=f'Which tag belongs to the {c} {sh} {m} archive item from source {sources[0]}? Answer:'
        constraints={'positive':{'color':c,'shape':sh,'material':m},'negative':{},'source':sources[0],'invalid':False}
    elif s=='P3_NEGATION_UNIQUE':
        forbidden=triples[1][2]
        q=f'Which tag belongs to the {c} {sh} archive item excluding material {forbidden}? Answer:'
        constraints={'positive':{'color':c,'shape':sh},'negative':{'material':forbidden},'source':None,'invalid':False}
    elif s=='N0_UNDERSPECIFIED':
        q=f'Which tag belongs to the {c} {sh} archive item? Answer:'
        constraints={'positive':{'color':c,'shape':sh},'negative':{},'source':None,'invalid':False}
    elif s=='N1_DUPLICATE_MATCH':
        q=f'Which tag belongs to the {c} {sh} {m} archive item from source {sources[0]}? Answer:'
        constraints={'positive':{'color':c,'shape':sh,'material':m},'negative':{},'source':sources[0],'invalid':False}
    elif s=='N2_CONTRADICTORY_QUERY':
        q=f'Which tag belongs to the {c} {sh} {m} archive item excluding color {c}? Answer:'
        constraints={'positive':{'color':c,'shape':sh,'material':m},'negative':{'color':c},'source':None,'invalid':True}
    else:
        if i%2==0:
            q=f'Which tag belongs to the {c} {sh} item made of xylotherm? Answer:'
            constraints={'positive':{'color':c,'shape':sh},'negative':{},'source':None,'invalid':True}
        else:
            q=f'Which tag belongs to the {c} {sh} {m} archive item excluding material {m}? Answer:'
            constraints={'positive':{'color':c,'shape':sh,'material':m},'negative':{'material':m},'source':None,'invalid':True}
    # No hint about gold action in public index fields; labels only in private case.
    assert answer is None or answer not in q
    return {'schema':SCHEMA,'split':'non_test_probe_v3',
            'case_id':f'vm3-{s}-{i:04d}','stratum':s,'question':q,
            'public_index':bank,'gold_action':'SELECT' if s.startswith('P') else 'ABSTAIN',
            'target_key':target_key,'answer':answer,
            'correct_memory':corr,'wrong_memory':wrong,
            'truth_constraints':constraints,'review_status':'PENDING_TWO_INDEPENDENT_HUMAN_REVIEWS' if s=='P1_UNSEEN_PARAPHRASE' else 'SYNTHETIC_RULE_CHECKABLE'}


def build()->list[dict]:
    data=[make_case(s,i) for s in STRATA for i in range(32)]
    keys=[x['key'] for case in data for x in case['public_index']]
    if len(set(keys))!=len(keys):raise AssertionError('GLOBAL_KEY_COLLISION')
    if len(data)!=256 or len(keys)!=8192:raise AssertionError('SCHEMA_COUNT_MISMATCH')
    return data


def serialized(data:list[dict])->bytes:
    return (json.dumps({'schema':SCHEMA,'split':'non_test_probe_v3','cases':data},sort_keys=True,separators=(',',':'))+'\n').encode('utf8')


def main():
    p=argparse.ArgumentParser()
    p.add_argument('--project-root',type=Path,required=True)
    p.add_argument('--out',type=Path,required=True)
    p.add_argument('--write-once',action='store_true')
    args=p.parse_args()
    if not args.write_once:raise SystemExit('DENY_WRITE_WITHOUT_EXPLICIT_OPTIN')
    root=args.project_root.resolve(strict=True);out=args.out.resolve()
    if not out.is_relative_to(root):raise SystemExit('DENY_OUTSIDE_PROJECT_ROOT')
    if out.exists():raise SystemExit('DENY_OVERWRITE_FROZEN_FIXTURE')
    blob=serialized(build())
    out.parent.mkdir(parents=True,exist_ok=True)
    out.write_bytes(blob)
    print(json.dumps({'status':'PRIVATE_FIXTURE_CREATED_SOURCE_ONLY','cases':256,
                      'sha256':hashlib.sha256(blob).hexdigest(),
                      'review':'PENDING_TWO_INDEPENDENT_HUMAN_REVIEWS',
                      'retriever_scored':False,'reader_forward':False,'test_opened':False}))
if __name__=='__main__':main()
