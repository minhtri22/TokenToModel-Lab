#!/usr/bin/env python3
"""A0E prospective CPU verifier: consume exact ORIGINAL private source tensors, never gold/VAL labels.
No model forward/training. Produces normalized six P tensors and an independently auditable receipt.
Exit HOLD unless all original immutable hash pins match. No outcome/threshold tuning.
"""
from __future__ import annotations
import argparse, hashlib, json, os, sys
from pathlib import Path
import numpy as np

SOURCE_SHA = {
 "P-A":"b6b0d3cb9d4f33b8d7d63269d296d2001e946706948d71cb4f357ab7cf5b2122",
 "P-C-61031":"e96f2d55ed1e02003c06012fd0345da260aab1fb3864f844155621e4d6ee2fd1",
 "P-C-61032":"30ad3136a00f9e26f8469a6dab5509289b8f258a7a8681d28ca1bdc18ac3b053",
 "P-C-61033":"6c7d8f6fac478be11b0f57c94976ab438f61911f929aabafe5609df3d0a052fb",
 "N-A-61031":"9fd58fb914e1ffccebbc735ef8d633feecf965ba99efcd96c5b7a2503aeaf9e6",
 "N-A-61032":"6d9c535397aef5fee11a7ceee4a562b10f1ad78b947fbb7cdc8dfc349a822a43",
 "N-A-61033":"e6746ab9766c820e64ebb7bfbe78507fad1aeb91e0111ab6324ec0d8c5cfe02f",
 "N-C-61031":"004be5fa5611291ef806a0b2de0e91de4a25d25fc490e85547233c40d6ccbf64",
 "N-C-61032":"85d671f32d4f16e4a898f1369dfc6056d7b3fad6d68e4147764b7a843f911c12",
 "N-C-61033":"bfc63f5bf39563dbc5fb6ca0b638bbd54456f43a9511e34878f3f9e67838bc13"
}
P0_SHA="9fdd433da0e728f969278cd89242a9df36b3e3e6b155821c9968b5e6d661c2b1"
CAND_SHA="c9fc798d8880c7e76636258052e9885dbb086d7b462a5b6bee5cff8b582973c3"
TRAIN_SHA="184f68b4c0c800ef3e98362c2e20e1cd35baa269e926489a475664526ecd9913"
SEEDS=(61031,61032,61033)

def need(x,reason):
    if not bool(x): raise RuntimeError("A0E_TENSOR_HOLD_"+reason)
def sha_file(p):
    h=hashlib.sha256()
    with Path(p).open('rb') as f:
        for b in iter(lambda:f.read(1048576),b''):h.update(b)
    return h.hexdigest()
def sha_arr(x):
    return hashlib.sha256(np.asarray(x,dtype='<f4',order='C').tobytes()).hexdigest()
def original_array(path, key):
    p=Path(path)
    need(p.is_file() and not p.is_symlink(),"SOURCE_MISSING_"+key)
    x=np.load(p,allow_pickle=False)
    need(x.shape==(2048,512) and x.dtype==np.float32 and np.isfinite(x).all(),"SHAPE_"+key)
    x=np.ascontiguousarray(x,dtype='<f4')
    need(sha_arr(x)==SOURCE_SHA[key],"ORIGINAL_SHA_"+key)
    return x
def covariance(x):
    z=np.asarray(x,dtype=np.float64)
    z=z-z.mean(0,keepdims=True)
    return (z.T@z)/(len(z)-1)
def relative(a,b):
    return float(np.linalg.norm(a-b)/max(np.linalg.norm(a),1e-30))
def spectrum(c):
    ev=np.maximum(np.linalg.eigvalsh(c),0)
    s=ev.sum()
    need(s>0,"COVARIANCE_ZERO")
    p=ev/s
    ent=float(-np.sum(p[p>0]*np.log(p[p>0])))
    return {"effective_rank":float(np.exp(ent)),
            "top10_trace_share":float(np.sum(ev[-10:])/s),
            "eigenvalues_desc_normalized":(ev[::-1]/s).tolist()}
def real_run(args):
    import torch
    source=Path(args.source_dir).resolve(strict=True)
    need(source.is_dir(),"SOURCE_DIR")
    candidate=Path(args.candidate).resolve(strict=True)
    train=Path(args.train_pack).resolve(strict=True)
    need(sha_file(candidate)==CAND_SHA,"CANDIDATE_SHA")
    need(sha_file(train)==TRAIN_SHA,"TRAIN_SHA")
    ck=torch.load(candidate,map_location='cpu',weights_only=True)
    state=ck['model_state_dict']
    valid=state['tok.valid'].detach().cpu().numpy().astype(bool)
    proj=state['tok.proj.weight'].detach().cpu().float().numpy()
    need(valid.shape==(2048,) and valid.sum()==1917,"VALID_MAPPING")
    need(proj.shape==(256,512) and sha_arr(proj)==P0_SHA,"PROJECTOR_SHA")
    p=original_array(source/'P-A.npy','P-A')
    need(np.array_equal(p,state['tok.source.weight'].detach().cpu().float().numpy()),"ORIGINAL_PRETRAINED_CANDIDATE")
    with np.load(train,allow_pickle=False) as z:
        x,c=z['train_x'],z['train_count']
        need(x.shape==(2691,256) and c.shape==(2691,),"TRAIN_SHAPE")
        need((c>0).all() and (c<=256).all() and int(c.sum())==498287,"TRAIN_COUNTS")
        mask=np.arange(256)[None,:]<c[:,None]
        tok=np.asarray(x[mask],dtype=np.int64)
        need((tok>=0).all() and (tok<2048).all(),"TRAIN_TOKENS")
        freq=np.bincount(tok,minlength=2048)
    source_arrays={'P-A':p}
    for seed in SEEDS:
        for kind in ('P-C','N-A','N-C'):
            k=f'{kind}-{seed}'
            source_arrays[k]=original_array(source/(k+'.npy'),k)
    outputs,metrics={},[]
    for seed in SEEDS:
        pc=source_arrays[f'P-C-{seed}']; na=source_arrays[f'N-A-{seed}'];nc=source_arrays[f'N-C-{seed}']
        pn=np.linalg.norm(p[valid].astype(np.float64),axis=1)
        nn=np.linalg.norm(na[valid].astype(np.float64),axis=1)
        alpha=float(np.median(nn)/np.median(pn))
        need(0.44<alpha<0.46,"ALPHA_UNEXPECTED")
        pa2=p.copy();pc2=pc.copy()
        pa2[valid]*=alpha
        pc2[valid]*=alpha
        need(np.array_equal(pa2[~valid],p[~valid]) and np.array_equal(pc2[~valid],pc[~valid]),"FALLBACK_CHANGED")
        ca=covariance(pa2[valid]);cb=covariance(pc2[valid]); cn=covariance(na[valid]);cd=covariance(nc[valid])
        within_p=relative(ca,cb);within_n=relative(cn,cd)
        projected_p=float(np.max(np.abs((pa2[valid].astype(np.float64)-pc2[valid].astype(np.float64))@proj.T)))
        projected_n=float(np.max(np.abs((na[valid].astype(np.float64)-nc[valid].astype(np.float64))@proj.T)))
        need(within_p<=.05 and within_n<=.05,"WITHIN_COV")
        need(projected_p<2e-5 and projected_n<2e-5,"NULL_PROJECTOR")
        ratio=float(np.trace(ca)/np.trace(cn))
        need(abs(ratio-1.)<=.05,"CROSS_TRACE")
        eigp=spectrum(ca);eign=spectrum(cn)
        eig_gap=float(np.linalg.norm(np.asarray(eigp['eigenvalues_desc_normalized'])-np.asarray(eign['eigenvalues_desc_normalized'])))
        row_p=np.linalg.norm(pa2[valid].astype(np.float64),axis=1)
        row_n=np.linalg.norm(na[valid].astype(np.float64),axis=1)
        row_smd=float(abs(row_p.mean()-row_n.mean())/max(np.sqrt((row_p.var()+row_n.var())/2),1e-12))
        logf=np.log1p(freq[valid])
        corrp=float(np.corrcoef(logf,row_p)[0,1]);corrn=float(np.corrcoef(logf,row_n)[0,1])
        outputs[f'P-A-{seed}']=pa2
        outputs[f'P-C-{seed}']=pc2
        outputs[f'N-A-{seed}']=na
        outputs[f'N-C-{seed}']=nc
        metrics.append({"seed":seed,"alpha":alpha,
            "within_source_cov_relative_P":within_p,"within_source_cov_relative_N":within_n,
            "projected_null_max_P":projected_p,"projected_null_max_N":projected_n,
            "trace_P_over_N_after_scalar":ratio,"eig_spectrum_l2_normalized":eig_gap,
            "effective_rank_P":eigp["effective_rank"],"effective_rank_N":eign["effective_rank"],
            "top10_share_P":eigp["top10_trace_share"],"top10_share_N":eign["top10_trace_share"],
            "mapped_row_norm_SMD":row_smd,
            "TRAIN_logfreq_norm_corr_P":corrp,"TRAIN_logfreq_norm_corr_N":corrn,
            "frequency_morph_char_control":"NOT_FULLY_VALIDATED",
            "original_f32le_SHA":{k:SOURCE_SHA[k] for k in (f'P-C-{seed}',f'N-A-{seed}',f'N-C-{seed}')},
            "new_f32le_SHA":{k:sha_arr(outputs[k]) for k in (f'P-A-{seed}',f'P-C-{seed}',f'N-A-{seed}',f'N-C-{seed}')},
        })
    out=Path(args.output).resolve()
    need(not out.exists(),"NO_OVERWRITE_OUTPUT")
    out.parent.mkdir(parents=True,exist_ok=True)
    # IMPORTANT: only a source artifact. Not a T4 release. Payload contains PRIVATE tensors.
    with out.open('xb') as f: np.savez_compressed(f,**outputs,valid=valid,projector=proj)
    report={"schema":"ttm.gemma2.a0e.scaled_private_tensor_readback.v1",
        "status":"PASS_REAL_TENSOR_TRANSFORM_SCOPED_HOLD_CROSS_ORIGIN_SHAPE",
        "original_prereg_blob":"d6e5d82709b2bc31458f73e7720cdae1e5f5e54e",
        "source_SHA256":SOURCE_SHA,"candidate_sha256":CAND_SHA,"train_pack_sha256":TRAIN_SHA,
        "TRAIN_token_count":int(freq.sum()),"mapped":int(valid.sum()),"seeds":metrics,
        "normalized_private_npz_sha256":sha_file(out),
        "full_cross_source_matrix_match":"NOT_ESTABLISHED",
        "morphology_and_length_SMD":"NOT_EXECUTED","actual_science_NLL":"NOT_READ",
        "gold_read":False,"VAL_labels_read":False,"forward_calls":0,"training":False,"GPU":False,"T4_authorized":False}
    receipt=Path(args.receipt).resolve()
    need(not receipt.exists(),"NO_OVERWRITE_RECEIPT")
    with receipt.open('x',encoding='utf-8',newline='\n') as f:json.dump(report,f,sort_keys=True,indent=2,allow_nan=False);f.write('\n')
    print(json.dumps({"status":report["status"],"receipt_sha256":sha_file(receipt),
         "normalized_private_npz_sha256":report["normalized_private_npz_sha256"],
         "T4_authorized":False},sort_keys=True))
def fixture():
    # No original tensors simulated as genuine. Negative test checks provenance rejection.
    with __import__('tempfile').TemporaryDirectory() as d:
        x=Path(d)/'P-A.npy'
        np.save(x,np.zeros((2048,512),dtype=np.float32),allow_pickle=False)
        try:original_array(x,'P-A')
        except RuntimeError as e:need('ORIGINAL_SHA' in str(e),"NEGATIVE_SOURCE_TAMPER")
        else:raise RuntimeError("HOLD_SYNTHETIC_TENSOR_MISCLASSIFIED")
    print(json.dumps({"status":"PASS_NEGATIVE_ORIGINAL_SHA_REJECTED",
                      "private_tensor_processed":False,"GPU":False},sort_keys=True))
def main():
    ap=argparse.ArgumentParser()
    g=ap.add_mutually_exclusive_group(required=True)
    g.add_argument('--fixture',action='store_true')
    g.add_argument('--source-dir')
    ap.add_argument('--candidate');ap.add_argument('--train-pack')
    ap.add_argument('--output');ap.add_argument('--receipt')
    a=ap.parse_args()
    try:
        if a.fixture:fixture()
        else:
            need(all((a.candidate,a.train_pack,a.output,a.receipt)),"ARGS")
            real_run(a)
    except Exception as e:
        print(json.dumps({"status":"NO_GO_HOLD","error":str(e),
                          "gold_read":False,"GPU":False,"T4_authorized":False},sort_keys=True))
        raise SystemExit(2)
if __name__=="__main__":main()
