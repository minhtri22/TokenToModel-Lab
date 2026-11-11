#!/usr/bin/env python3
"""A0 geometry feasibility; NO model.forward, no TRAIN/VAL/TEST scoring, no fitting.
Checks EXACT input projection and per-token L2 norm under residual reassignment.
Outputs only aggregate geometry and no private donor/token/vector data.
"""
from __future__ import annotations
import argparse, hashlib, io, json, os, zipfile
from pathlib import Path
import numpy as np

PIN_CANDIDATE="c9fc798d8880c7e76636258052e9885dbb086d7b462a5b6bee5cff8b582973c3"
PIN_ZIP="2c6cb72f35eba72d6014f15914d6e9792cbf0bf6774d93e3ff5c53e5c6b9ba9a"
SOURCE_ROOT="input\\"
SEED=2026111137

def need(cond,reason):
    if not bool(cond):raise RuntimeError("HOLD_A0_"+reason)

def sha(data):return hashlib.sha256(data).hexdigest()
def sha_file(path):
    h=hashlib.sha256()
    with Path(path).open("rb") as f:
        for b in iter(lambda:f.read(1<<20),b""):h.update(b)
    return h.hexdigest()

def orthogonal_decompose(X,P):
    X=np.asarray(X,dtype=np.float64);P=np.asarray(P,dtype=np.float64)
    n,d=X.shape
    m,dd=P.shape
    need(dd==d and 0<m<d and n>d,"DIMENSIONS")
    # Complete orthonormal basis is not needed. QR(P^T) gives exact row span.
    Q,_=np.linalg.qr(P.T,mode="reduced")
    rank=int(np.linalg.matrix_rank(P))
    need(rank==m,"PROJECTION_RANK")
    par=(X@Q)@Q.T
    R=X-par
    need(np.max(np.abs(R@P.T))<=1e-8,"NULLSPACE_PRECISION")
    return par,R,rank

def quantile_rank_bin(a,bins):
    a=np.asarray(a)
    order=np.argsort(a,kind="stable")
    result=np.empty(len(a),dtype=np.int64)
    result[order]=np.arange(len(a),dtype=np.int64)*bins//len(a)
    return result

def derangement(stratum,seed=SEED):
    # Fixed-seed cycles within strata. Every eligible token moves once.
    rng=np.random.default_rng(seed)
    n=len(stratum);pi=np.arange(n)
    seen=[]
    for g in np.unique(stratum):
        ids=np.where(stratum==g)[0]
        need(len(ids)>=2,"STRATUM_SINGLETON")
        shuffle=rng.permutation(ids)
        pi[shuffle]=np.roll(shuffle,1)
        seen.append(int(len(ids)))
    need(len(set(pi.tolist()))==n and not np.any(pi==np.arange(n)),"NONBIJECTIVE_OR_IDENTITY")
    return pi,seen

def transform(X,P,frequency,seed=SEED):
    """Residual-only reassignment preserves projected vector and per-token norm.

    This does not preserve global covariance or pairwise neighborhoods exactly.
    The output is a geometry diagnostic, NEVER a pretrained-semantic proof.
    """
    X=np.asarray(X,dtype=np.float64)
    frequency=np.asarray(frequency,dtype=np.float64)
    need(frequency.shape==(len(X),) and np.isfinite(frequency).all() and (frequency>=0).all(),"FREQUENCY")
    par,R,rank=orthogonal_decompose(X,P)
    norm=np.linalg.norm(R,axis=1)
    need(np.min(norm)>1e-9,"ZERO_RESIDUAL_NORM")
    # Proxy matching only: TRAIN-only token frequency rank and residual-norm rank.
    # No lexical labels available in this fixture; never claim lexical matching.
    freq_bin=quantile_rank_bin(frequency,4)
    norm_bin=quantile_rank_bin(norm,4)
    strata=freq_bin*4+norm_bin
    pi,sizes=derangement(strata,seed)
    Xmixed=par + R[pi]*(norm/np.linalg.norm(R[pi],axis=1))[:,None]
    projected_error=float(np.max(np.abs(X@P.T-Xmixed@P.T)))
    original_norm=np.linalg.norm(X,axis=1)
    mixed_norm=np.linalg.norm(Xmixed,axis=1)
    rownorm_error=float(np.max(np.abs(original_norm-mixed_norm)))
    need(projected_error<=1e-8,"PROJECTED_INPUT_DRIFT")
    need(rownorm_error<=1e-8,"PER_TOKEN_L2_DRIFT")
    c=lambda v:(v-v.mean(axis=0)).T@(v-v.mean(axis=0))
    cov0=c(X);cov1=c(Xmixed)
    covariance_rel=float(np.linalg.norm(cov1-cov0)/np.linalg.norm(cov0))
    mean_rel=float(np.linalg.norm(Xmixed.mean(axis=0)-X.mean(axis=0))/
                   max(np.linalg.norm(X.mean(axis=0)),1e-12))
    R0=R/np.linalg.norm(R,axis=1)[:,None]
    R1=(Xmixed-par)/np.linalg.norm(Xmixed-par,axis=1)[:,None]
    residual_cos_change=float(np.mean(1-np.sum(R0*R1,axis=1)))
    return dict(n=len(X),source_dim=X.shape[1],projected_dim=P.shape[0],
       rank=rank,nullspace_dimension=X.shape[1]-rank,
       mapped_fraction_reassigned=float(np.mean(pi!=np.arange(len(X)))),
       projected_max_abs_fp64=projected_error,
       per_token_norm_max_abs_fp64=rownorm_error,
       covariance_relative_fro_drift=covariance_rel,
       mean_relative_l2_drift=mean_rel,
       average_residual_angular_change= residual_cos_change,
       strata_count=len(sizes),minimum_stratum_size=min(sizes),
       maximum_stratum_size=max(sizes),
       train_frequency_matching=True,lexical_matching=False,
       semantic_labels_used=False,semantic_causality_claim=False)

def fixture():
    rng=np.random.default_rng(2026111136)
    X=rng.normal(size=(96,16))
    P=rng.normal(size=(8,16))
    counts=np.arange(96)%11
    r=transform(X,P,counts)
    need(r["rank"]==8 and r["nullspace_dimension"]==8,"FIXTURE_RANK")
    need(r["mapped_fraction_reassigned"]==1.0,"FIXTURE_MOVEMENT")
    need(r["projected_max_abs_fp64"]<1e-9,"FIXTURE_PROJECTION")
    need(r["per_token_norm_max_abs_fp64"]<1e-9,"FIXTURE_NORM")
    need(r["covariance_relative_fro_drift"]>1e-6,"FIXTURE_COVARIANCE_NEGATIVE_CONTROL")
    need(r["average_residual_angular_change"]>0.01,"FIXTURE_ANGULAR_NEGATIVE_CONTROL")
    # No silent acceptance when strata cannot support nontrivial derangement.
    try: derangement(np.arange(5),SEED)
    except RuntimeError as exc:need("STRATUM_SINGLETON" in str(exc),"FIXTURE_EXPECTED_REJECTION")
    else:raise AssertionError("FAILED_SINGLETON_REJECTION")
    # Error on rank-deficient projector.
    try: orthogonal_decompose(X,np.zeros((8,16)))
    except RuntimeError as exc:need("PROJECTION_RANK" in str(exc),"FIXTURE_EXPECTED_RANK_REJECTION")
    else:raise AssertionError("FAILED_RANK_REJECTION")
    print("TTM_GEMMA2_SEMANTICS_A0_CPU_FIXTURE=PASS_8_NO_FORWARD_NO_TRAIN")
    print(json.dumps({"fixture_geometry":r,"private_files_read":False,
      "training_executed":False,"inference_executed":False},sort_keys=True))

def audit(zip_path):
    import torch
    archive=Path(zip_path).resolve(strict=True)
    need(sha_file(archive)==PIN_ZIP,"PRIVATE_ZIP_SHA")
    with zipfile.ZipFile(archive) as z:
        data=z.read(SOURCE_ROOT+"candidate_initialization.pt")
        need(sha(data)==PIN_CANDIDATE,"CANDIDATE_SHA")
        ck=torch.load(io.BytesIO(data),map_location="cpu",weights_only=True)
        need(ck.get("schema")=="ttm.embeddinggemma2.token_swap.initialization.v1" and
             ck.get("science_executed") is False,"CANDIDATE_META")
        state=ck["model_state_dict"]
        valid=state["tok.valid"].detach().cpu().numpy().astype(bool)
        need(valid.shape==(2048,) and int(valid.sum())==1917 and not valid[256],"MAPPING")
        X=state["tok.source.weight"].detach().cpu().numpy().astype(np.float64)[valid]
        P=state["tok.proj.weight"].detach().cpu().numpy().astype(np.float64)
        need(X.shape==(1917,512) and P.shape==(256,512),"DONOR_SHAPES")
        with np.load(io.BytesIO(z.read(SOURCE_ROOT+"T4_PRIVATE_TRAIN_VAL_WINDOWS.npz")),allow_pickle=False) as d:
            # TRAIN token frequencies only, no labels/VAL/TEST consumed.
            xt=d["train_x"].astype(np.int64)
            count=d["train_count"].astype(np.int64)
        need(xt.ndim==2 and xt.shape[1]==256 and
             len(xt)==len(count) and (count>0).all() and (count<=256).all(),"TRAIN_INPUT")
        mask=np.arange(256)[None,:]<count[:,None]
        freq=np.bincount(xt[mask],minlength=2048)[valid]
    summary=transform(X,P,freq)
    summary.update(schema="ttm.gemma2.semantics.a0.geometry.cpu_source_audit.v1",
      status="GEOMETRY_PROJECTION_AND_NORM_FEASIBLE_ONLY",
      donor_candidate_sha256=PIN_CANDIDATE,
      source_zip_sha256=PIN_ZIP,
      mapped_tokens=1917,
      donor_model_input_embedding_dimension=512,
      donor_contextual_output_embedding_is_not_measured=True,
      frequency_source="T4_TRAIN_X_ONLY",
      full_training_reexecuted=False,
      science_loss_computed=False,
      model_forward_calls=0,
      owner_science_execution_permit_issued=False,
      lexical_anchors_status="NOT_CHECKED",
      untrained_same_architecture_control_status="NOT_ADMITTED",
      mean_covariance_matched_exactly=False,
      semantic_causality_status="NOT_ESTABLISHED")
    print(json.dumps(summary,sort_keys=True,allow_nan=False))
    print("TTM_GEMMA2_A0_REAL_DONOR_GEOMETRY_AUDIT=PASS_SCOPED_NO_FORWARD")

if __name__=="__main__":
    p=argparse.ArgumentParser()
    p.add_argument("--mode",required=True,choices=("fixture","donor-audit"))
    p.add_argument("--source-zip")
    a=p.parse_args()
    if a.mode=="fixture":fixture()
    else:
        need(bool(a.source_zip),"SOURCE_ZIP_ARG")
        audit(a.source_zip)
