#!/usr/bin/env python3
"""TTM EmbeddingGemma2 semantics4x3: CPU-only, no-model-forward, pre-CLAIM null geometry QA.

Intervention is limited to donor residual beyond the 256-dimensional frozen Ridge projection.
Preserves P-projected input per token, mean and global covariance exactly to floating precision.
Never publishes private donor rows, checkpoint weights, text, token identities or train labels.
"""
from __future__ import annotations
import argparse, hashlib, json
from pathlib import Path
import numpy as np
from scipy.linalg import solve, svd
from threadpoolctl import threadpool_limits

PIN_DONOR='c9fc798d8880c7e76636258052e9885dbb086d7b462a5b6bee5cff8b582973c3'
PIN_BASE='cb985751795c8328ad65acf7ca4c1033ce35182c1bfbdb8c38550de629cb271b'


def hash_file(p):
    with Path(p).open('rb') as f:
        return hashlib.file_digest(f, 'sha256').hexdigest()


def build_null(X, P, seed):
    """Return X_null from row donor X[N,512] and frozen P[256,512].

    Z=X P^T; Xparallel=Z(PP^T)^-1 P; R=X-Xparallel.
    Q=orthonormal span([ones,Z]); R=QC+U S V^T with U orthogonal to Q.
    Replace U with independently Haar-like Stiefel columns also orthogonal to Q.
    Preserves X P^T, column mean and X-centered covariance, not individual row norms.
    No access to TTM E0 target labels or validation labels during null generation.
    """
    X=np.asarray(X,dtype=np.float64); P=np.asarray(P,dtype=np.float64)
    n,d=X.shape;m,dp=P.shape
    assert dp==d and n>d+m+2 and 0<=seed<2**63
    with threadpool_limits(limits=2):
        gram=P@P.T
        eig=np.linalg.eigvalsh(gram)
        assert eig[0]>1e-12, 'HOLD_P_RANK'
        Z=X@P.T
        parallel=Z@solve(gram,P,assume_a='pos')
        R=X-parallel
        A=np.column_stack([np.ones(n),Z]);Q,_=np.linalg.qr(A,mode='reduced')
        assert np.linalg.matrix_rank(A)==m+1, 'HOLD_Q_RANK'
        C=Q.T@R;res=R-Q@C
        _,s,Vt=svd(res,full_matrices=False,lapack_driver='gesdd')
        rank=int(np.sum(s>s[0]*1e-10))
        assert rank==d-m, ('HOLD_RESIDUAL_RANK',rank,d-m)
        G=np.random.default_rng(seed).standard_normal((n,rank))
        G-=Q@(Q.T@G)
        Unew,_=np.linalg.qr(G,mode='reduced')
        Unew-=Q@(Q.T@Unew)
        Unew,_=np.linalg.qr(Unew,mode='reduced')
        Rnull=Q@C+(Unew*s[None,:rank])@Vt[:rank]
        null=parallel+Rnull
        return null,rank


def metrics(X, Xnull, P):
    with threadpool_limits(limits=2):
        Z=X@P.T;ZN=Xnull@P.T
        covariance=lambda V:(V-V.mean(0)).T@(V-V.mean(0))
        C=covariance(X);CN=covariance(Xnull)
        fp32=float(np.max(np.abs(np.asarray(X,dtype=np.float32)@np.asarray(P,dtype=np.float32).T-
                                    np.asarray(Xnull,dtype=np.float32)@np.asarray(P,dtype=np.float32).T)))
        norms=lambda V:[float(v) for v in np.quantile(np.linalg.norm(V,axis=1),[.1,.5,.9])]
        return {
          'projection_max_abs_fp64':float(np.max(abs(Z-ZN))),
          'projection_max_abs_fp32':fp32,
          'projection_relative_fro_fp64':float(np.linalg.norm(Z-ZN)/np.linalg.norm(Z)),
          'global_covariance_relative_fro':float(np.linalg.norm(C-CN)/np.linalg.norm(C)),
          'column_mean_max_abs':float(np.max(abs(X.mean(0)-Xnull.mean(0)))),
          'row_norm_quantiles_pretrained_p10_p50_p90':norms(X),
          'row_norm_quantiles_null_p10_p50_p90':norms(Xnull)
        }


def check(m):
    assert m['projection_max_abs_fp64']<=1e-9,'HOLD_PROJECTED_INPUT_NOT_MATCHED'
    assert m['projection_max_abs_fp32']<=1e-5,'HOLD_PROJECTED_INPUT_FP32_NOT_MATCHED'
    assert m['global_covariance_relative_fro']<=1e-9,'HOLD_COVARIANCE_NOT_MATCHED'
    assert m['column_mean_max_abs']<=1e-9,'HOLD_MEAN_NOT_MATCHED'


def fixture():
    rng=np.random.default_rng(2026111001)
    with threadpool_limits(limits=2):
        X=rng.normal(size=(96,16));P=rng.normal(size=(8,16))
        Xnull,r=build_null(X,P,2026111002)
        m=metrics(X,Xnull,P);check(m)
        assert r==8
        assert np.max(np.abs(Xnull-X))>1e-4,'HOLD_NULL_NO_INTERVENTION'
        # Permuted arm pair must remain matched on projected input.
        ids=np.random.default_rng(2026111003).permutation(96)
        assert np.max(np.abs((X-Xnull)[ids]@P.T))<1e-9
        print(json.dumps({'status':'PASS_SYNTHETIC_6_CHECKS','source_data_read':False,'training':False,'gpu':False,'model_forward':False}))


def real(candidate,checkpoint,seed):
    assert hash_file(candidate)==PIN_DONOR,'HOLD_DONOR_SOURCE_PIN'
    assert hash_file(checkpoint)==PIN_BASE,'HOLD_TTM_SOURCE_PIN'
    import torch
    cand=torch.load(candidate,map_location='cpu',weights_only=True)
    base=torch.load(checkpoint,map_location='cpu',weights_only=True)
    state=cand['model_state_dict'];valid=state['tok.valid'].bool()
    assert valid.sum().item()==1917 and valid.shape==(2048,) and not bool(valid[256])
    X=state['tok.source.weight'][valid].numpy().astype('float64')
    P=state['tok.proj.weight'].numpy().astype('float64')
    Y=base['model']['tok.weight'][valid].numpy().astype('float64')
    assert X.shape==(1917,512) and P.shape==(256,512) and Y.shape==(1917,256)
    Xnull,r=build_null(X,P,seed)
    m=metrics(X,Xnull,P);check(m)
    # Same paired synthetic/input projected loss-agnostic geometry, without model.
    Z=X@P.T;Znull=Xnull@P.T
    m['ttm_projected_initial_rmse_real']=float(np.sqrt(np.mean((Z-Y)**2)))
    m['ttm_projected_initial_rmse_null']=float(np.sqrt(np.mean((Znull-Y)**2)))
    m['ttm_projected_initial_rmse_pair_gap']=abs(m['ttm_projected_initial_rmse_real']-m['ttm_projected_initial_rmse_null'])
    assert m['ttm_projected_initial_rmse_pair_gap']<=1e-9
    print(json.dumps({'status':'PASS_REAL_TENSOR_DUAL_MATCHED_NULL_CPU',
        'schema':'ttm.semantic4x3.balanced_null_cpu_qa.v1',
        'source_sha256':{'donor':PIN_DONOR,'base':PIN_BASE},
        'mapped_count':1917,'fallback_count':131,'projector_rank':256,'randomized_residual_rank':r,
        'seed':seed,'metrics':m,
        'limitations':['Only residual beyond pre-fitted projector is randomized',
          'Preserves covariance and initial projected embeddings, not per-token row norms',
          'Does not isolate all donor semantics or donor pretraining corpus'],
        'science_claim':False,'science_training':False,'gpu_used':False,'model_forward_calls':0,'holdout_read':False},sort_keys=True))


if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('--mode',choices=['fixture','real'],required=True)
    p.add_argument('--candidate');p.add_argument('--checkpoint');p.add_argument('--seed',type=int,default=2026111101)
    a=p.parse_args()
    if a.mode=='fixture':fixture()
    else:
        assert a.candidate and a.checkpoint,'HOLD_PATH_REQUIRED'
        real(Path(a.candidate),Path(a.checkpoint),a.seed)
