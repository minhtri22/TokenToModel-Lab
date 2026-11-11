#!/usr/bin/env python3
"""Independent OOD256 science readback. Does not load models, run inference or train."""
from __future__ import annotations
import argparse,hashlib,json,os
from pathlib import Path
import numpy as np

SEEDS=("S1","S2","S3")
ARMS=("PT-REAL","PT-PERM","NULL-REAL","NULL-PERM")
DOCS=256;TARGETS=131072
SEED=2026111198;DRAWS=2000
OOD_PUBLIC="0091b56b27c68f1bb724b63181097434d6c7c5922e5cc1de929423b5b0c45438"
OOD_MEMBER="627c99db8b39b6479fdb074a82b0ab7eea0367dde49bf0072c29ff410ecdcd5f"
OOD_WINDOWS="3ec7655c512c5d13d4c0d04d1ddbae80b8ea0106aee82064e8dd806786d8336a"
def need(ok,name):
    if not ok:raise RuntimeError("HOLD_INDEPENDENT_"+name)
def sha_file(p):
    h=hashlib.sha256()
    with Path(p).open("rb") as f:
        for b in iter(lambda:f.read(1<<20),b""):h.update(b)
    return h.hexdigest()
def read(p):return json.loads(Path(p).read_text("utf-8"))
def write_once(p,obj):
    payload=(json.dumps(obj,sort_keys=True,separators=(",",":"),ensure_ascii=False,allow_nan=False)+"\n").encode()
    with Path(p).open("xb") as f:f.write(payload);f.flush();os.fsync(f.fileno())
def verify(out):
    out=Path(out).resolve(strict=True)
    cp=out/"CLAIM.json";priv=out/"PER_DOCUMENT_PRIVATE.json";result=out/"RESULT.json"
    for f in (cp,priv,result):need(f.is_file() and not f.is_symlink(),"MISSING_"+f.name)
    c=read(cp);p=read(priv);r=read(result)
    need(c["scope"]=="ONE_SHOT_12_FROZEN_SCORING_ONLY" and c["owner_approved"] is True,"CLAIM_SCOPE")
    need(c["ood_public_sha256"]==OOD_PUBLIC and c["ood_membership_sha256"]==OOD_MEMBER
         and c["ood_windows_sha256"]==OOD_WINDOWS,"CLAIM_OOD")
    need(len(c["checkpoints_sha256"])==12 and
         set(c["seed_arms"])=={s+"/"+a for s in SEEDS for a in ARMS},"FROZEN_12_ARM")
    need(p["claim_sha256"]==r["claim_sha256"]==sha_file(cp),"CLAIM_SHA")
    need(p["ood_membership_sha256"]==OOD_MEMBER and p["counts"]==[512]*DOCS,"PRIVATE_COUNT")
    need(sha_file(priv)==r["private_per_doc_sha256"],"PER_DOC_FILE_SHA")
    need(r["ood_public_seal_sha256"]==OOD_PUBLIC and
         r["bootstrap_seed"]==SEED and r["bootstrap_draws"]==DRAWS and
         r["targets"]==TARGETS and r["checkpoint_sha256"]==c["checkpoints_sha256"],"PUBLIC_META")
    score=p["loss_sum_by_seed_arm"]
    need(set(score)==set(SEEDS),"SEED_SET")
    for s in SEEDS:
        need(set(score[s])==set(ARMS),"ARM_SET")
        for a in ARMS:
            private=out/(s+"__"+a+"__SCORE_PRIVATE.json")
            start=out/(s+"__"+a+"__START.json")
            need(private.is_file() and start.is_file(),"PER_ARM_RECEIPT")
            meta=read(private);st=read(start)
            need(meta["seed"]==s and meta["arm"]==a and meta["claim_sha256"]==sha_file(cp)
                 and st["claim_sha256"]==sha_file(cp),"PER_ARM_META")
            need(meta["ood_membership_sha256"]==OOD_MEMBER and
                 meta["checkpoint_sha256"]==st["checkpoint_sha256"]==c["checkpoints_sha256"][s+"/"+a],"ARM_PIN")
            vec=np.asarray(score[s][a],dtype="<f8")
            need(vec.shape==(DOCS,) and np.isfinite(vec).all() and (vec>=0).all(),"ARM_LOSS")
            need(np.array_equal(vec,np.asarray(meta["loss_sum_by_doc"],dtype="<f8")),"ARM_VS_PRIVATE")
            need(hashlib.sha256(vec.tobytes()).hexdigest()==meta["score_bytes_sha256"],"ARM_DIGEST")
            claimed_nll=float(vec.sum()/TARGETS)
            need(abs(claimed_nll-r["nll_nats_per_target"][s][a])<1e-11,"ARM_NLL")
    contrasts={};ctau=[];cgamma=[]
    for s in SEEDS:
        A={k:np.asarray(v,dtype=np.float64) for k,v in score[s].items()}
        pre=A["PT-PERM"]-A["PT-REAL"]
        nul=A["NULL-PERM"]-A["NULL-REAL"]
        tau=pre-nul;gamma=A["NULL-REAL"]-A["PT-REAL"]
        ctau.append(tau);cgamma.append(gamma)
        contrasts[s]={
          "delta_PRE":pre.sum()/TARGETS,
          "delta_NULL":nul.sum()/TARGETS,
          "tau_residual":tau.sum()/TARGETS,
          "gamma_real":gamma.sum()/TARGETS
        }
        for k,v in contrasts[s].items():
            need(abs(v-r["contrasts_by_seed"][s][k])<1e-11,"CONTRAST_"+k+"_"+s)
    idx=np.random.default_rng(SEED).integers(0,DOCS,size=(DRAWS,DOCS))
    ci={}
    for key,arr in [("tau_residual",ctau),("gamma_real",cgamma)]:
        v=np.mean(np.stack(arr,axis=0),axis=0)
        boot=v[idx].sum(axis=1)/TARGETS
        ci[key]=[float(x) for x in np.quantile(boot,[0.025,0.975])]
        pub=r["co_primary"][key]
        need(all(abs(u-w)<1e-11 for u,w in zip(ci[key],pub["ci95_percentile"])),"CI_"+key)
        need(abs(v.sum()/TARGETS-pub["mean_delta_nll"])<1e-11,"MEAN_"+key)
        need(pub["seed_all_positive"]==all(contrasts[s][key]>0 for s in SEEDS),"SEED_SIGNS_"+key)
    verdict=("PASS_SCOPED_OOD_RESIDUAL_SIGNAL" if all(
       all(contrasts[s][k]>0 for s in SEEDS) and ci[k][0]>0 for k in ("tau_residual","gamma_real"))
       else "FAIL_SCOPED_OOD_SIGNAL_NOT_ESTABLISHED")
    need(verdict==r["candidate_verdict"],"ADJUDICATION_CONSISTENCY")
    receipt={"schema":"ttm.gemma2.ood256.independent_readback.public.v1",
       "status":"INDEPENDENT_QA_PASS_PENDING_OWNER_SCIENCE_ADJUDICATION",
       "candidate_verdict":verdict,"claim_sha256":sha_file(cp),
       "result_sha256":sha_file(result),"private_per_doc_sha256":sha_file(priv),
       "arm_receipts_verified":12,"bootstrap_seed":SEED,"bootstrap_draws":DRAWS,
       "paired_document_count":DOCS,"ci95_percentile":ci,
       "no_inference_in_checker":True,"no_training":True,"lineage_modified":False}
    output=out/"INDEPENDENT_READBACK_PUBLIC.json"
    need(not output.exists(),"REVIEW_ALREADY_EXISTS")
    write_once(output,receipt)
    print("OOD12_INDEPENDENT_READBACK=PASS_12_ARM_CI_METADATA")
    print("OOD12_INDEPENDENT_READBACK_SHA256="+sha_file(output))
    print("OOD12_SCIENCE_PENDING_OWNER_ADJUDICATION="+verdict)
def fixture():
    v=np.arange(DOCS,dtype=np.float64)
    a=np.full(DOCS,512.0);b=a+8
    need(np.isfinite(v).all() and len(a)==DOCS,"FIXTURE_LENGTH")
    need(float((b-a).sum()/TARGETS)==8/512,"FIXTURE_PAIRING")
    idx=np.random.default_rng(SEED).integers(0,DOCS,size=(DRAWS,DOCS))
    need(idx.shape==(DRAWS,DOCS) and idx.min()>=0 and idx.max()<DOCS,"FIXTURE_BOOT")
    print("OOD12_INDEPENDENT_SYNTHETIC_QA=PASS_3_NO_FORWARD_NO_CLAIM")
if __name__=="__main__":
    ap=argparse.ArgumentParser();ap.add_argument("--mode",choices=("fixture","review"),required=True)
    ap.add_argument("--output",default="");a=ap.parse_args()
    if a.mode=="fixture":fixture()
    else:need(bool(a.output),"OUTPUT_REQUIRED");verify(a.output)
