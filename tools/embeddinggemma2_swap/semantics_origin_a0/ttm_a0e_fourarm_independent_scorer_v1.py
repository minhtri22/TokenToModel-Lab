#!/usr/bin/env python3
"""A0E independent future masked-NLL scorer: source-only fixture, no model forward."""
import argparse,json
import numpy as np
ARMS=("P-A","P-C","N-A","N-C")
def ensure(x,code):
    if not bool(x): raise RuntimeError("A0E_SCORER_HOLD_"+code)
def per_document(logits,labels,lengths):
    z=np.asarray(logits,dtype=np.float64)
    y=np.asarray(labels,dtype=np.int64)
    k=np.asarray(lengths,dtype=np.int64)
    ensure(z.ndim==3 and z.shape[2]==2048 and y.shape==z.shape[:2] and k.shape==(len(y),),"SHAPES")
    ensure(np.isfinite(z).all() and (k>0).all() and (k<=z.shape[1]).all(),"LOGITS_LENGTHS")
    mask=np.arange(z.shape[1])[None,:]<k[:,None]
    ensure(np.all((y[mask]>=0)&(y[mask]<2048)) and np.all(y[~mask]==-100),"TARGET_MASK")
    m=z.max(axis=-1)
    logsum=m+np.log(np.exp(z-m[...,None]).sum(axis=-1))
    rows,cols=np.where(mask)
    losses=logsum[rows,cols]-z[rows,cols,y[rows,cols]]
    ensure(np.isfinite(losses).all(),"NONFINITE_NLL")
    sums=np.bincount(rows,weights=losses,minlength=z.shape[0])
    return [(float(s),int(n)) for s,n in zip(sums,k)]
def paired_effect(arms):
    ensure(set(arms)==set(ARMS),"ARM_NAMES")
    keys=set(arms[ARMS[0]])
    ensure(bool(keys) and all(set(arms[a])==keys for a in ARMS),"PAIRED_DOCUMENT_IDS")
    lengths=[{arms[a][doc][1] for a in ARMS} for doc in keys]
    ensure(all(len(s)==1 and next(iter(s))>0 for s in lengths),"PAIRED_TARGET_COUNTS")
    total=sum(next(iter(s)) for s in lengths)
    nll={a:sum(arms[a][d][0] for d in keys)/total for a in ARMS}
    align=nll["P-C"]-nll["P-A"]
    origin=align-(nll["N-C"]-nll["N-A"])
    return {"nats_per_target_token":nll,"D_align":align,"D_origin":origin,"documents":len(keys),"target_tokens":total}
def fixture():
    z=np.zeros((2,3,2048),dtype=np.float32)
    y=np.array([[2,1,-100],[3,-100,-100]],dtype=np.int64)
    scored=per_document(z,y,[2,1])
    assert all(abs(v/n-np.log(2048))<1e-9 for v,n in scored)
    paired={a:{"d1":scored[0],"d2":scored[1]} for a in ARMS}
    result=paired_effect(paired)
    assert abs(result["D_origin"])<1e-12
    try:paired_effect({**paired,"N-C":{"d1":scored[0]}})
    except RuntimeError as e:assert "PAIRED_DOCUMENT_IDS" in str(e)
    else:raise RuntimeError("HOLD_NEGATIVE_DOC_NOT_REJECTED")
    y[0,2]=50
    try:per_document(z,y,[2,1])
    except RuntimeError as e:assert "TARGET_MASK" in str(e)
    else:raise RuntimeError("HOLD_NEGATIVE_MASK_NOT_REJECTED")
    return {"status":"PASS_SOURCE_ONLY_MASKED_NLL_AND_PAIRED_FOUR_ARM_FIXTURE","model_forward":False,"training":False,"VAL_consumed":False,"GPU":False}
if __name__=="__main__":
    ap=argparse.ArgumentParser();ap.add_argument("--fixture",action="store_true",required=True);ap.parse_args()
    print(json.dumps(fixture(),sort_keys=True))
