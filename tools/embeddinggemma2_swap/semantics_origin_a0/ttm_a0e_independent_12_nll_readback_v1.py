#!/usr/bin/env python3
"""Independent A0E 12-outcome paired document NLL readback.
No model code imported, no labels or GPU, rejects target/doc/seed/checkpoint mismatches.
Preserves exact prereg exploratory thresholds, does NOT authorize T4 or claim significance.
"""
from __future__ import annotations
import argparse,hashlib,json,math,tempfile
from pathlib import Path

SEEDS=(41031,41032,41033)
ARMS=("P-A","P-C","N-A","N-C")
NAMES=tuple(f'seed{s}__{a}.json' for s in SEEDS for a in ARMS)
SCHEMA="ttm.gemma2.a0e.seed_arm_document_nll.v1"
def need(x,code):
    if not bool(x):raise RuntimeError("A0E_NLL_HOLD_"+code)
def digest(p):
    h=hashlib.sha256()
    with Path(p).open('rb') as f:
        for b in iter(lambda:f.read(1048576),b''):h.update(b)
    return h.hexdigest()
def read(outcome_dir,checkpoint_dir=None):
    d=Path(outcome_dir)
    need(d.is_dir(),"OUTCOME_DIR")
    need(set(p.name for p in d.iterdir() if p.is_file())==set(NAMES),"EXACT_TWELVE_OUTPUTS")
    received={}
    for s in SEEDS:
        for a in ARMS:
            fn=f'seed{s}__{a}.json';p=d/fn
            r=json.loads(p.read_text('utf8'))
            need(r.get('schema')==SCHEMA and r.get('seed')==s and r.get('arm')==a,"FILE_ARM_BIND_"+fn)
            need(r.get('gold_read') is False and r.get('lexical_labels_read') is False,"PREMATURE_LEXICAL_READ")
            need(isinstance(r.get('checkpoint_sha256'),str) and len(r['checkpoint_sha256'])==64,"CHECKPOINT_SHA")
            if checkpoint_dir:
                ck=Path(checkpoint_dir)/f'seed{s}'/a/'step_0512.pt'
                need(ck.is_file() and digest(ck)==r['checkpoint_sha256'],"CHECKPOINT_REAL_SHA_"+fn)
            sums=r.get('document_sums');counts=r.get('document_targets')
            need(isinstance(sums,dict) and isinstance(counts,dict)
                 and len(sums)>0 and sums.keys()==counts.keys(),"DOC_KEYS_"+fn)
            need(all(isinstance(x,(int,float)) and math.isfinite(x) and x>=0 for x in sums.values()),"LOSS_"+fn)
            need(all(type(x) is int and 0<x<=1000000 for x in counts.values()),"COUNTS_"+fn)
            need(sum(counts.values())==r.get('total_targets'),"TOTAL_TARGETS_"+fn)
            need(isinstance(r.get('fresh_val_sha256'),str) and len(r['fresh_val_sha256'])==64,"VAL_SHA")
            received[(s,a)]=r
    return received
def score(rec):
    need(set(rec)=={(s,a) for s in SEEDS for a in ARMS},"EXACT_MATRIX")
    seeds=[]
    for s in SEEDS:
        items={a:rec[(s,a)] for a in ARMS}
        keys=set(items['P-A']['document_sums'])
        counts=items['P-A']['document_targets']
        fsha=items['P-A']['fresh_val_sha256']
        need(all(set(items[a]['document_sums'])==keys and
                 items[a]['document_targets']==counts and
                 items[a]['fresh_val_sha256']==fsha for a in ARMS),"DOC_TARGET_PAIRING_"+str(s))
        n=sum(counts.values())
        nll={a:sum(items[a]['document_sums'].values())/n for a in ARMS}
        align=nll['P-C']-nll['P-A']
        origin=align-(nll['N-C']-nll['N-A'])
        seeds.append({'train_seed':s,'val_sha256':fsha,'documents':len(keys),
                      'target_tokens':n,'nll':nll,'D_align':align,'D_origin':origin})
    need(len({r['val_sha256'] for r in seeds})==1,"VAL_DIFFERENT_ACROSS_SEEDS")
    mean=sum(r['D_origin'] for r in seeds)/3
    verdict=("PASS_EXPLORATORY_PRETRAINING_ASSOCIATED_NLL_ONLY"
        if all(r['D_origin']>0 and r['D_align']>0 for r in seeds) and mean>=.02
        else "FAIL_FROZEN_EXPLORATORY_NLL_CRITERION")
    return {'schema':'ttm.gemma2.a0e.independent_nll_12_readback.v1',
            'verdict':verdict,'mean_D_origin':mean,'seeds':seeds,
            'thresholds':{'all_seed_D_origin_gt_zero':0,'mean_D_origin_ge':.02,
                          'all_seed_D_align_gt_zero':0},
            'no_significance_claim_with_three_seeds':True,
            'gold_read':False,'model_forward':False,'training':False,'GPU':False,
            'T4_authorized':False}
def fixture():
    with tempfile.TemporaryDirectory() as tmp:
        p=Path(tmp)
        for seed in SEEDS:
            for arm,val in [('P-A',3.0),('P-C',3.06),('N-A',3.1),('N-C',3.11)]:
                r={'schema':SCHEMA,'seed':seed,'arm':arm,'checkpoint_sha256':'a'*64,
                   'fresh_val_sha256':'b'*64,'document_sums':{'d1':val*100,'d2':val*100},
                   'document_targets':{'d1':100,'d2':100},'total_targets':200,
                   'gold_read':False,'lexical_labels_read':False}
                (p/f'seed{seed}__{arm}.json').write_text(json.dumps(r))
        r=score(read(p))
        need(r['verdict']=='PASS_EXPLORATORY_PRETRAINING_ASSOCIATED_NLL_ONLY',"POSITIVE")
        name=p/'seed41031__P-C.json'
        d=json.loads(name.read_text());d['document_targets']['d1']=99
        d['total_targets']=199;name.write_text(json.dumps(d))
        try:score(read(p))
        except RuntimeError as e:need('DOC_TARGET_PAIRING' in str(e),"NEGATIVE_TARGET")
        else:raise RuntimeError("NEGATIVE_TARGET_NOT_REJECTED")
    print(json.dumps({'status':'PASS_INDEPENDENT_12_NLL_POSITIVE_AND_NEGATIVE_FIXTURE',
                      'real_outcomes_read':False,'GPU':False},sort_keys=True))
def main():
    p=argparse.ArgumentParser()
    g=p.add_mutually_exclusive_group(required=True)
    g.add_argument('--fixture',action='store_true');g.add_argument('--score',action='store_true')
    p.add_argument('--outcome-dir');p.add_argument('--checkpoint-dir');p.add_argument('--output')
    a=p.parse_args()
    try:
        if a.fixture:fixture()
        else:
            need(a.outcome_dir and a.output and a.checkpoint_dir,"REAL_ARGS")
            result=score(read(a.outcome_dir,a.checkpoint_dir))
            out=Path(a.output)
            need(not out.exists(),"NO_OVERWRITE")
            with out.open('x',encoding='utf8',newline='\n') as f:
                json.dump(result,f,indent=2,sort_keys=True,allow_nan=False);f.write('\n')
            print(json.dumps({'verdict':result['verdict'],'result_sha256':digest(out)},sort_keys=True))
    except Exception as e:
        print(json.dumps({'status':'NO_GO_HOLD','error':str(e),'GPU':False},sort_keys=True))
        raise SystemExit(2)
if __name__=='__main__':main()
