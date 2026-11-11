#!/usr/bin/env python3
"""A0E locked lexical scorer. Does not choose pairs or read gold during fixture.
Only after externally verified Git commit of all 12 outcomes can --score be used.
Uses paired word-disjoint bootstrap; Holm adjusted p values over exactly two tests.
"""
from __future__ import annotations
import argparse,hashlib,json,math
from pathlib import Path
import numpy as np

CORE_SHA="b280478feb9f7359c261944e5c54c7808c96e05bd14558657044fe6f35a2ee2c"
GOLD_SHA="b58f68454cf9354b94ecd8bfd778ff2cc784a25fc7dca02bc695319ad2b4157e"
SEED=71031;DRAWS=10000
def need(v,code):
    if not v:raise RuntimeError("A0E_LEX_HOLD_"+code)
def digest(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def rank(v):
    # rankdata: average ties, stable
    order=np.argsort(v,kind='stable')
    ranks=np.empty(len(v),dtype=np.float64)
    i=0
    while i<len(v):
        j=i+1
        while j<len(v) and v[order[j]]==v[order[i]]:j+=1
        ranks[order[i:j]]=(i+j-1)/2+1
        i=j
    return ranks
def rho(x,y):
    if np.std(x)==0 or np.std(y)==0:return float('nan')
    return float(np.corrcoef(rank(x),rank(y))[0,1])
def analyze(vec, gold):
    need(len(gold)==37 and len(vec)==4,"PAIR_COUNT")
    g=np.asarray(gold,dtype=np.float64)
    v={k:np.asarray(a,dtype=np.float64) for k,a in vec.items()}
    need(set(v)=={'P-A','P-C','N-A-61031','N-A-61032','N-A-61033'},"FIVE_SOURCES")
    need(all(x.shape==(37,) and np.isfinite(x).all() for x in v.values()),"COSINE_FINITE")
    need(np.isfinite(g).all(),"GOLD_FINITE")
    def contrast(idx):
        out={k:rho(x[idx],g[idx]) for k,x in v.items()}
        return np.asarray([out['P-A']-np.mean([out['N-A-'+str(s)] for s in (61031,61032,61033)]),
                           out['P-A']-out['P-C']],dtype=np.float64)
    obs=contrast(np.arange(37))
    need(np.isfinite(obs).all(),"SPEARMAN_UNDEFINED")
    rng=np.random.default_rng(SEED)
    boot=[]
    # Ties and degenerate resamples: count as undefined and stop, never drop draws.
    for _ in range(DRAWS):
        b=contrast(rng.integers(0,37,37))
        need(np.isfinite(b).all(),"UNDEFINED_BOOTSTRAP")
        boot.append(b)
    boot=np.vstack(boot)
    # Bootstrap centered test of H0 difference=0, two-sided, plus Holm step-down correction.
    p=np.asarray([(1+np.count_nonzero(abs(boot[:,i]-obs[i])>=abs(obs[i])))/(DRAWS+1) for i in range(2)])
    order=np.argsort(p)
    adj=np.empty(2);rolling=0.
    for j,i in enumerate(order):
        rolling=max(rolling,min(1.,(2-j)*p[i]));adj[i]=rolling
    # Conservative simultaneous Bonferroni intervals, valid for Holm-PASS screening.
    lower=np.quantile(boot,.0125,axis=0);upper=np.quantile(boot,.9875,axis=0)
    support=bool(np.all(obs>=.20) and np.all(lower>0.) and np.all(adj<.05))
    return {"schema":"ttm.gemma2.a0e.lexical_37_score.v1",
            "status":"EXPLORATORY_LEXICAL_SUPPORT" if support else "NO_LEXICAL_SUPPORT",
            "contrasts":["L_origin","L_disruption"],"point_estimates":obs.tolist(),
            "bootstrap_seed":SEED,"bootstrap_draws":DRAWS,"centered_bootstrap_p":p.tolist(),
            "holm_adjusted_p":adj.tolist(),"simultaneous_bonferroni_97_5_lower":lower.tolist(),
            "simultaneous_bonferroni_97_5_upper":upper.tolist(),
            "not_claiming_third_party_or_pure_semantic_causality":True}
def private_score(a):
    need(a.verified_commit_receipt and a.lock_verified_by_separate_github_readback,
         "EXTERNAL_GIT_READBACK_REQUIRED")
    receipt=json.loads(Path(a.verified_commit_receipt).read_text('utf8'))
    need(receipt.get('status')=='PASS_GITHUB_COMMIT_READBACK_BEFORE_GOLD' and receipt.get('outcomes_locked_count')==12,
         "COMMIT_READBACK_STATUS")
    need(digest(a.core)==CORE_SHA,"CORE_ROSTER_SHA")
    need(digest(a.gold)==GOLD_SHA,"GOLD_SHA")
    # Gold source parsing requires exact frozen layout, not inferred dynamically.
    columns=json.loads(Path(a.frozen_column_contract).read_text('utf8'))
    need(columns.get('schema')=='ttm.a0e.gold_columns.preunblind.v1'
         and columns.get('gold_sha256')==GOLD_SHA and columns.get('score_col') in (2,3,4),
         "COLUMN_CONTRACT")
    core=[tuple(line.split('\t')) for line in Path(a.core).read_text('ascii').splitlines()]
    need(len(core)==37 and all(len(p)==2 for p in core),"CORE_PAIR_FORMAT")
    cols=(columns['word1_col'],columns['word2_col'],columns['score_col'])
    scores={}
    for row in Path(a.gold).read_text('utf8').splitlines():
        parts=row.split('\t')
        if len(parts)>max(cols):
            try:s=float(parts[cols[2]])
            except ValueError:continue
            scores[(parts[cols[0]],parts[cols[1]])]=s
    gold=[scores.get(p) for p in core]
    need(all(x is not None for x in gold),"GOLD_PAIR_MISSING")
    vector=json.loads(Path(a.frozen_cosines).read_text('utf8'))
    need(vector.get('schema')=='ttm.gemma2.a0e.frozen_core_37_cosines.v1'
         and vector.get('core_sha256')==CORE_SHA,"FROZEN_COSINES")
    result=analyze(vector['sources'],gold)
    result['gold_source_sha256']=GOLD_SHA
    result['core_sha256']=CORE_SHA
    result['commit_readback_verified']=True
    result['gold_read_after_lock']=True
    output=Path(a.output)
    need(not output.exists(),"NO_OVERWRITE")
    with output.open('x',encoding='utf8',newline='\n') as f:
        json.dump(result,f,sort_keys=True,indent=2,allow_nan=False);f.write('\n')
    print(json.dumps({"status":result['status'],"result_sha256":digest(output)},sort_keys=True))
def fixture():
    a=np.arange(37,dtype=np.float64)
    rng=np.random.default_rng(17)
    v={'P-A':a.copy(),'P-C':-a.copy()}
    for s in (61031,61032,61033):v['N-A-'+str(s)]=rng.permutation(a)
    res=analyze(v,a)
    need(res['point_estimates'][1]>0.2 and res['status']=='EXPLORATORY_LEXICAL_SUPPORT',"POSITIVE")
    try:analyze({**v,'P-A':np.ones(37)},a)
    except RuntimeError as e:need('SPEARMAN_UNDEFINED' in str(e),"NEGATIVE_CONSTANT")
    else:raise RuntimeError("NEGATIVE_CONSTANT_NOT_REJECTED")
    print(json.dumps({"status":"PASS_LEXICAL_POSITIVE_AND_NEGATIVE_SYNTHETIC_ONLY","gold_read":False},sort_keys=True))
def main():
    ap=argparse.ArgumentParser()
    g=ap.add_mutually_exclusive_group(required=True);g.add_argument('--fixture',action='store_true');g.add_argument('--score',action='store_true')
    for name in ('verified-commit-receipt','core','gold','frozen-column-contract','frozen-cosines','output'):
        ap.add_argument('--'+name)
    ap.add_argument('--lock-verified-by-separate-github-readback',action='store_true')
    a=ap.parse_args()
    try:fixture() if a.fixture else private_score(a)
    except Exception as e:
        print(json.dumps({"status":"NO_GO_HOLD","error":str(e)},sort_keys=True))
        raise SystemExit(2)
if __name__=="__main__":main()
