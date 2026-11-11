#!/usr/bin/env python3
"""A0B: one CPU geometry-only source audit, no model.forward, no labels/scoring.

Constrained residual randomization: preserves each X_i P.T, each row L2 norm,
global mean/covariance, and TRAIN-only frequency-bin cross-moments.
It changes residual neighborhoods; NOT a proof of pretrained semantic causality.
Private source arrays are never emitted or saved.
"""
import argparse,hashlib,io,json,zipfile
from pathlib import Path
import numpy as np
from scipy.linalg import null_space

ZIP_SHA="2c6cb72f35eba72d6014f15914d6e9792cbf0bf6774d93e3ff5c53e5c6b9ba9a"
DONOR_SHA="c9fc798d8880c7e76636258052e9885dbb086d7b462a5b6bee5cff8b582973c3"
TRAIN_NPZ_SHA="184f68b4c0c800ef3e98362c2e20e1cd35baa269e926489a475664526ecd9913"
SEED=2026111142
MAX_ITER=64
TOL=1e-8

def ensure(ok,reason):
    if not bool(ok):raise RuntimeError("HOLD_A0B_"+reason)

def digest(data):return hashlib.sha256(data).hexdigest()
def hash_file(path):
    h=hashlib.sha256()
    with Path(path).open("rb") as f:
        for b in iter(lambda:f.read(1024*1024),b""):h.update(b)
    return h.hexdigest()

def quantile_bin(a,k=4):
    order=np.argsort(a,kind="stable")
    bins=np.empty(len(a),dtype=np.int64)
    bins[order]=np.arange(len(a))*k//len(a)
    return bins

def cov(X):
    v=X-X.mean(axis=0)
    return v.T@v

def transform(X,P,freq,seed=SEED):
    X=np.asarray(X,dtype=np.float64)
    P=np.asarray(P,dtype=np.float64)
    freq=np.asarray(freq,dtype=np.float64)
    n,d=X.shape
    m,dp=P.shape
    ensure(dp==d and 0<m<d and n>m+d+40,"DIMS")
    ensure(freq.shape==(n,) and (freq>=0).all() and np.isfinite(freq).all(),"TRAIN_FREQ")
    ensure(np.isfinite(X).all() and np.isfinite(P).all(),"FINITE")
    ensure(np.linalg.matrix_rank(P)==m,"P_RANK")
    Qp,_=np.linalg.qr(P.T,mode="reduced")
    Qnull=null_space(P)
    ensure(Qnull.shape==(d,d-m),"NULL_BASIS")
    A=X@Qp
    R=X@Qnull
    rn=np.linalg.norm(R,axis=1)
    ensure(np.min(rn)>1e-9,"RESIDUAL_ZERO")
    f=np.log1p(freq)
    frequency_bin=quantile_bin(f,4)
    norm_bin=quantile_bin(rn,4)
    # TRAIN-only frequency covariates; row-norm covariates have no label access.
    F=np.column_stack((np.ones(n),A,f,f**2,
       np.eye(4)[frequency_bin][:,1:],
       np.eye(4)[norm_bin][:,1:]))
    ensure(np.linalg.matrix_rank(F)==F.shape[1],"FEATURE_RANK")
    B,_=np.linalg.qr(F,mode="reduced")
    H=B.T@R
    W=R-B@H
    G=W.T@W
    ensure(np.linalg.eigvalsh(G)[0]>1e-10,"NULL_RESIDUAL_FULL_RANK")
    L=np.linalg.cholesky(G).T
    rng=np.random.default_rng(seed)
    Z=rng.standard_normal(W.shape)
    Z-=B@(B.T@Z)
    U,_=np.linalg.qr(Z,mode="reduced")
    Wnew=U@L
    for iteration in range(MAX_ITER):
        Rnew=B@H+Wnew
        error=np.max(np.abs(np.linalg.norm(Rnew,axis=1)-rn))
        if error<=TOL:break
        row_scaled=Rnew*(rn/np.linalg.norm(Rnew,axis=1))[:,None]
        zero=row_scaled-B@(B.T@row_scaled)
        U,_=np.linalg.qr(zero,mode="reduced")
        Wnew=U@L
    Rnew=B@H+Wnew
    Xnew=A@Qp.T + Rnew@Qnull.T
    ensure(np.linalg.norm(X-Xnew)>1.0,"NULL_DID_NOT_CHANGE")
    proj_err=float(np.max(np.abs(Xnew@P.T-X@P.T)))
    row_err=float(np.max(np.abs(np.linalg.norm(Xnew,axis=1)-np.linalg.norm(X,axis=1))))
    proj32=float(np.max(np.abs(Xnew.astype("float32")@P.astype("float32").T-X.astype("float32")@P.astype("float32").T)))
    norm32=float(np.max(np.abs(np.linalg.norm(Xnew.astype("float32"),axis=1)-np.linalg.norm(X.astype("float32"),axis=1))))
    covariance=float(np.linalg.norm(cov(Xnew)-cov(X))/np.linalg.norm(cov(X)))
    mean=float(np.linalg.norm(Xnew.mean(0)-X.mean(0))/np.linalg.norm(X.mean(0)))
    angles=1.0-np.sum(Rnew*R,axis=1)/(np.linalg.norm(Rnew,axis=1)*rn)
    ensure(proj_err<=TOL and row_err<=TOL and covariance<=0.05 and mean<=0.05 and
           proj32<=1e-5 and norm32<=1e-5,"HARD_GEOMETRY_GATE")
    # A true intervention on conditional residual associations, not a global basis rotation.
    ensure(float(np.mean(angles))>=0.3 and float(np.mean(angles>0.3))>=0.8,"NULL_INTERVENTION_TOO_WEAK")
    k=10
    cosine0=(R@R.T)/(rn[:,None]*rn[None,:])
    rnnew=np.linalg.norm(Rnew,axis=1)
    cosine1=(Rnew@Rnew.T)/(rnnew[:,None]*rnnew[None,:])
    np.fill_diagonal(cosine0,-2.0)
    np.fill_diagonal(cosine1,-2.0)
    ii0=np.argpartition(cosine0,-k,axis=1)[:,-k:]
    ii1=np.argpartition(cosine1,-k,axis=1)[:,-k:]
    topk_overlap=float(sum(len(set(a)&set(b)) for a,b in zip(ii0,ii1))/(n*k))
    ensure(topk_overlap<0.25,"NULL_NEIGHBORHOOD_UNCHANGED")
    return {
      "status":"PASS_A0B_CONSTRAINED_MOMENTS_MATHEMATICAL_CPU_FEASIBILITY",
      "n_mapped":n,"donor_source_dimension":d,"ttm_projected_dimension":m,
      "random_seed":seed,"iterations_to_convergence":iteration,
      "max_projected_input_abs_fp64":proj_err,"max_token_norm_abs_fp64":row_err,
      "max_projected_input_abs_fp32":proj32,"max_token_norm_abs_fp32":norm32,
      "global_covariance_relative_fro":covariance,
      "global_mean_relative_l2":mean,
      "fraction_residual_angle_change_gt_0p3":float(np.mean(angles>0.3)),
      "mean_residual_cosine_change":float(np.mean(angles)),
      "residual_top10_neighbor_overlap":topk_overlap,
      "frequency_covariates":"TRAIN-only log1p(count), squared and rank-quartile controls",
      "residual_norm_covariates":"quartile dummies",
      "training_executed":False,"model_forward_calls":0,
      "evaluation_NLL_read":False,"semantic_labels_used":False,
      "claims_pretrained_semantics":False
    }

def fixture():
    rng=np.random.default_rng(2026111140)
    X=rng.standard_normal((128,16))
    P=rng.standard_normal((8,16))
    freq=rng.integers(0,17,size=128)
    r=transform(X,P,freq)
    ensure(r["max_projected_input_abs_fp64"]<TOL and
           r["max_token_norm_abs_fp64"]<TOL and
           r["global_covariance_relative_fro"]<1e-8,"SYNTHETIC_PASS")
    try:transform(X,np.zeros_like(P),freq)
    except RuntimeError as e:ensure("P_RANK" in str(e),"RANK_NEGATIVE")
    else:raise RuntimeError("HOLD_A0B_RANK_NEGATIVE_NOT_REJECTED")
    try:transform(X,P,np.ones((128,2)))
    except RuntimeError as e:ensure("TRAIN_FREQ" in str(e),"FREQ_NEGATIVE")
    else:raise RuntimeError("HOLD_A0B_FREQ_NEGATIVE_NOT_REJECTED")
    print("A0B_CONSTRAINED_MOMENT_SYNTHETIC_CPU_QA=PASS")
    print(json.dumps({"synth":r,"no_training":True,"no_forward":True},sort_keys=True))

def private_audit(path):
    import torch
    p=Path(path)
    ensure(hash_file(p)==ZIP_SHA,"ZIP_SHA")
    with zipfile.ZipFile(p) as z:
        donor=z.read("input\\candidate_initialization.pt")
        train=z.read("input\\T4_PRIVATE_TRAIN_VAL_WINDOWS.npz")
        ensure(digest(donor)==DONOR_SHA and digest(train)==TRAIN_NPZ_SHA,"PRIVATE_INPUT_SHA")
        state=torch.load(io.BytesIO(donor),map_location="cpu",weights_only=True)["model_state_dict"]
        valid=state["tok.valid"].numpy().astype(bool)
        ensure(valid.shape==(2048,) and int(valid.sum())==1917 and not valid[256],"MASK")
        X=state["tok.source.weight"].numpy().astype(np.float64)[valid]
        P=state["tok.proj.weight"].numpy().astype(np.float64)
        with np.load(io.BytesIO(train),allow_pickle=False) as d:
            x=d["train_x"].astype(np.int64)
            counts=d["train_count"].astype(np.int64)
            ensure(x.ndim==2 and x.shape[1]==256 and counts.shape==(len(x),) and
                   (counts>0).all() and (counts<=256).all(),"TRAIN_PACK")
            f=np.bincount(x[np.arange(256)[None,:]<counts[:,None]],minlength=2048)[valid]
    res=transform(X,P,f)
    res.update(schema="ttm.gemma2.semantics.a0b.constrained_moments.cpu_private_source.v1",
      donor_source_sha256=DONOR_SHA,source_zip_sha256=ZIP_SHA,
      frequency_train_pack_sha256=TRAIN_NPZ_SHA,
      private_vectors_emitted=False,lexical_semantics_probe="NOT_EXECUTED",
      nonpretrained_source_admitted=False,owner_T4_science_permit=False)
    print(json.dumps(res,sort_keys=True,allow_nan=False))

if __name__=="__main__":
    arg=argparse.ArgumentParser()
    arg.add_argument("--mode",required=True,choices=["fixture","private-audit"])
    arg.add_argument("--source-zip")
    a=arg.parse_args()
    if a.mode=="fixture":fixture()
    else:
        ensure(a.source_zip,"SOURCE_ZIP_MISSING")
        private_audit(a.source_zip)
