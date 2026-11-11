#!/usr/bin/env python3
"""TTM_GEMMA2 OOD256 one-shot inference-only scorer, 12 frozen checkpoints.

Modes: fixture (synthetic, no forward), preflight (all 12 raw SHA, no forward),
execute (owner-approved, preflight first, then exactly one scoring CLAIM).
Never trains, creates checkpoints, modifies H768, modifies lineage or selects arms.
"""
from __future__ import annotations
import argparse
import hashlib
import importlib.util
import json
import os
from pathlib import Path
import sys
import tempfile
import zipfile
import numpy as np
import torch
import torch.nn.functional as F

STUDY = "ttm_gemma2_semantic4x3_3seed_2048x4096_h768_20261110_v2"
SEEDS = ("S1","S2","S3")
ARMS = ("PT-REAL","PT-PERM","NULL-REAL","NULL-PERM")
CHECKPOINTS = {
 "S1/PT-REAL":"cf3e6863215555b639fd4d3582f77f2b997c05dc5269cd411342bf660632cf46",
 "S1/PT-PERM":"dd62bf4695ec9dd4175817c1e3c663389b1282ead560a267f02c7d97a54960fb",
 "S1/NULL-REAL":"59bb203f5ba2a02e56778200d21ec26c2898bed12a2644d9c860ae06aaffe9fb",
 "S1/NULL-PERM":"9365403b0a2f4499405f348639d8ebd37e9d8997d0d10894ef23d0d57dbddb21",
 "S2/PT-REAL":"1ea877b7c62e0b17fc757881a54cd1a4bd829128c0e406543723e871c6f432f1",
 "S2/PT-PERM":"f1dba5a83772d2346222083039012f928917351ba48bdf843f8d4814dc24b60a",
 "S2/NULL-REAL":"10ad0ffa8ffd58bee5276374562140e9e3bf580695a5a2e4f4d4bfc08ea42b25",
 "S2/NULL-PERM":"a2740d762abdf760483f460716464631caf68f577491946de6d264b206a4aa5f",
 "S3/PT-REAL":"272fd3987d5f5505807662ab62153ede927d76f1c87333affa98df8c6f55fb93",
 "S3/PT-PERM":"c51a947f1d075e90a5199130e79a671c5257714d66a511fc2d9e78bbc7eac89d",
 "S3/NULL-REAL":"b58a17f65d6ec949095a0d3d1ac3a91f26d3c71c7246a1ea64d2a4d224341c1e",
 "S3/NULL-PERM":"ac6fe6ed4510eb6212609c1e913d6102782a78dcb4cfc2aa7743f6151ef07235",
}
SOURCE_ZIP_SHA="2c6cb72f35eba72d6014f15914d6e9792cbf0bf6774d93e3ff5c53e5c6b9ba9a"
P02_SHA="e0fcac285918b66b13c8f694e6d625a0691c9b59221b43043e63f46b25ddcc07"
SWAP_SHA="d11da61e9d7bb040f3263e680f026817a513553c186ab243e184ffaf6e68cd39"
FROZEN_RUNNER_SHA="a3182549739cda848ce0f7f449b1f1455e06419d72295dcee96f0e8a7822f676"
OOD_PUBLIC="0091b56b27c68f1bb724b63181097434d6c7c5922e5cc1de929423b5b0c45438"
OOD_MEMBERSHIP="627c99db8b39b6479fdb074a82b0ab7eea0367dde49bf0072c29ff410ecdcd5f"
OOD_WINDOWS="3ec7655c512c5d13d4c0d04d1ddbae80b8ea0106aee82064e8dd806786d8336a"
OOD_PARQUET="49280f3dd993cbdfd322186194133d5d1935f81e1c91064c239f2a70ebb02701"
T1_BPE="cba18e60cee3d08a353ee6d4a451017289e45af7b4b1179c87171b9b78d7dfdc"
BOOTSTRAP_SEED=2026111198
BOOTSTRAP_DRAWS=2000
DOCS,WINDOWS,CONTEXT,VOCAB,LABELS=256,512,256,2048,131072
BATCH=8

def demand(ok,why):
    if not bool(ok):raise RuntimeError("HOLD_OOD_"+why)

def sha_file(path):
    h=hashlib.sha256()
    with Path(path).open("rb") as f:
        for c in iter(lambda:f.read(1<<20),b""):h.update(c)
    return h.hexdigest()

def canon(o):
    return (json.dumps(o,ensure_ascii=False,sort_keys=True,separators=(",",":"),allow_nan=False)+"\n").encode("utf-8")

def newjson(path,o):
    path=Path(path)
    with path.open("xb") as f:
        f.write(canon(o));f.flush();os.fsync(f.fileno())
    return sha_file(path)

def readjson(path):return json.loads(Path(path).read_text("utf-8"))

def cp_paths(study,seed,arm):
    p=study/seed/"checkpoints"/arm/"step_2048"
    return p/"checkpoint.pt",p/"READY.json"

def preflight_ood(ood):
    names={"OOD256_PUBLIC_SEAL.json":OOD_PUBLIC,
           "OOD256_PRIVATE_MEMBERSHIP.json":OOD_MEMBERSHIP,
           "OOD256_PRIVATE_WINDOWS.npz":OOD_WINDOWS}
    for name,pin in names.items():
        f=ood/name
        demand(f.is_file() and not f.is_symlink(),"OOD_MISSING_"+name)
        demand(sha_file(f)==pin,"OOD_SHA_"+name)
    pub=readjson(ood/"OOD256_PUBLIC_SEAL.json")
    member=readjson(ood/"OOD256_PRIVATE_MEMBERSHIP.json")
    demand(pub["status"]=="SEALED_SOURCE_ONLY_NOT_SCORED","OOD_STATUS")
    demand(pub["private_membership_sha256"]==OOD_MEMBERSHIP and pub["private_windows_sha256"]==OOD_WINDOWS,"OOD_BINDING")
    demand(pub["parquet_sha256"]==OOD_PARQUET and pub["t1_bpe_manifest_sha256"]==T1_BPE,"OOD_SOURCE_PINS")
    demand(pub["selected_articles"]==DOCS and pub["selected_windows"]==WINDOWS and
           pub["scored_targets_total"]==LABELS and not pub["science_executed"],"OOD_PUBLIC_COUNTS")
    demand(member["selected_count"]==DOCS and len(member["selected"])==DOCS,"OOD_MEMBERSHIP_COUNT")
    with np.load(ood/"OOD256_PRIVATE_WINDOWS.npz",allow_pickle=False) as z:
        demand(set(z.files)=={"x","y","story_index","count"},"OOD_PACK_KEYS")
        x=z["x"].astype(np.int64);y=z["y"].astype(np.int64)
        si=z["story_index"].astype(np.int64);counts=z["count"].astype(np.int64)
    demand(x.shape==y.shape==(WINDOWS,CONTEXT) and
           si.shape==counts.shape==(WINDOWS,),"OOD_WINDOW_SHAPES")
    demand((x>=0).all() and (x<VOCAB).all() and (y>=0).all() and (y<VOCAB).all(),"OOD_ID_RANGE")
    demand(np.array_equal(si,np.repeat(np.arange(DOCS),2)) and (counts==CONTEXT).all(),"OOD_ORDER_AND_COUNTS")
    demand(np.array_equal(x[:,1:],y[:,:-1]) and np.array_equal(y[::2,-1],x[1::2,0]),"OOD_NEXT_TOKEN_SHIFT")
    demand(int(counts.sum())==LABELS and len(set(z["text_sha256"] for z in member["selected"]))==DOCS,
           "OOD_LABELS_OR_DUPLICATE")
    return {"x":x,"y":y,"si":si,"counts":counts,
      "public":pub,"private_sha256":{k:v for k,v in names.items()}}

def preflight_sources(source_zip,work):
    demand(source_zip.is_file() and sha_file(source_zip)==SOURCE_ZIP_SHA,"SOURCE_ZIP_SHA")
    with zipfile.ZipFile(source_zip) as z:
        names={
          "input\\src\\p02_exact.py":("p02_exact.py",P02_SHA),
          "input\\src\\ttm_embeddinggemma2_swap.py":("ttm_embeddinggemma2_swap.py",SWAP_SHA)
        }
        for archive_name,(name,pin) in names.items():
            b=z.read(archive_name)
            demand(hashlib.sha256(b).hexdigest()==pin,"MODEL_SOURCE_SHA_"+name)
            f=work/name
            with f.open("xb") as o:o.write(b)
    return work

def validate_checkpoint(c,seed,arm):
    demand(c.get("schema")=="ttm.semantic4x3.checkpoint.v1" and
           c.get("study_id")==STUDY and c.get("seed")==seed and c.get("arm")==arm,"CK_META")
    demand(c.get("step")==2048 and c.get("sampler_cursor")==2048 and
           len(c.get("train_losses",[]))==2048,"CK_FROZEN_STEP")
    demand(c.get("source_sha256")==FROZEN_RUNNER_SHA,"CK_SOURCE")
    state=c.get("model")
    demand(isinstance(state,dict) and len(state)==56,"CK_TENSORS")
    required={"tok.valid":(2048,),"tok.fallback":(2048,256),
      "tok.source.weight":(2048,512),"tok.proj.weight":(256,512),
      "pos.weight":(256,256),"head.weight":(2048,256)}
    for name,shape in required.items():
        demand(name in state and tuple(state[name].shape)==shape,"CK_SHAPE_"+name)
    demand(state["tok.valid"].dtype==torch.bool and not bool(state["tok.valid"][256]),"CK_VALID_EOS")
    demand(int(state["tok.valid"].sum())==1917,"CK_VALID_COUNT")
    demand(all(torch.isfinite(t).all().item() for t in state.values() if t.is_floating_point()),"CK_FINITE")
    return state

def preflight_checkpoints(study):
    demand(study.is_dir(),"STUDY_ROOT")
    seen=set()
    for seed in SEEDS:
        for arm in ARMS:
            key=seed+"/"+arm
            ckpath,readypath=cp_paths(study,seed,arm)
            demand(ckpath.is_file() and readypath.is_file() and
                   not ckpath.is_symlink() and not readypath.is_symlink(),"CK_MISSING_"+key)
            cksha=sha_file(ckpath);demand(cksha==CHECKPOINTS[key],"CK_SHA_"+key)
            ready=readjson(readypath)
            demand(ready["checkpoint_sha256"]==cksha and ready["checkpoint_bytes"]==ckpath.stat().st_size and
                   ready["seed"]==seed and ready["arm"]==arm and ready["step"]==2048 and
                   ready["study_id"]==STUDY and ready["source_sha256"]==FROZEN_RUNNER_SHA,"READY_"+key)
            c=torch.load(ckpath,map_location="cpu",weights_only=True)
            validate_checkpoint(c,seed,arm)
            seen.add(key)
            del c
    demand(seen==set(CHECKPOINTS),"CK_SET")
    return {"12_checkpoint_sha256":CHECKPOINTS,"verified":len(seen)}

def import_sources(src):
    sys.path.insert(0,str(src))
    import ttm_embeddinggemma2_swap as sw
    p02=sw.load_p02(src/"p02_exact.py")
    return sw,p02

def build_model_from_frozen_state(c,sw,p02):
    state=c["model"]
    # Model is entirely reconstructed from frozen checkpoint tensors.
    base=p02.GPT(sw.p02_config(p02)).float()
    m=sw.control_untied(base)
    m.tok=sw.MappedGemmaInput(state["tok.source.weight"].detach().float().clone(),
         state["tok.valid"].detach().bool().clone(),
         state["tok.fallback"].detach().float().clone(),
         state["tok.proj.weight"].detach().float().clone())
    m.load_state_dict(state,strict=True)
    demand(set(m.state_dict())==set(state),"STRICT_STATE_KEYS")
    del base
    return m.eval()

def score_arm(m,x,y,si,device):
    """The only path that calls model.forward: execute mode after all gates and CLAIM."""
    sums=np.zeros(DOCS,dtype=np.float64)
    m.eval()
    with torch.inference_mode():
        for start in range(0,WINDOWS,BATCH):
            end=min(start+BATCH,WINDOWS)
            xx=torch.from_numpy(x[start:end].copy()).to(device,dtype=torch.long)
            yy=torch.from_numpy(y[start:end].copy()).to(device,dtype=torch.long)
            logits,_=m(xx)
            demand(logits.shape==(end-start,CONTEXT,VOCAB),"FORWARD_LOGITS_SHAPE")
            demand(torch.isfinite(logits).all().item(),"FORWARD_LOGITS_NONFINITE")
            losses=F.cross_entropy(logits.float().reshape(-1,VOCAB),yy.reshape(-1),reduction="none")
            values=losses.reshape(end-start,CONTEXT).sum(dim=1,dtype=torch.float64).cpu().numpy()
            np.add.at(sums,si[start:end],values)
    demand(np.isfinite(sums).all() and (sums>=0).all() and sums.shape==(DOCS,),"ARM_SCORE_FINITE")
    return sums

def assess(scores):
    demand(set(scores)==set(SEEDS) and all(set(scores[s])==set(ARMS) for s in SEEDS),"SCORE_ARM_SET")
    for s in SEEDS:
        for a in ARMS:
            v=np.asarray(scores[s][a],dtype=np.float64)
            demand(v.shape==(DOCS,) and np.isfinite(v).all() and (v>=0).all(),"LOSS_ARRAY_"+s+"_"+a)
    nll={s:{a:float(np.asarray(scores[s][a]).sum()/LABELS) for a in ARMS} for s in SEEDS}
    contrasts={};per={}
    for s in SEEDS:
        a={k:np.asarray(v,dtype=np.float64) for k,v in scores[s].items()}
        per[s]={
          "tau_residual":a["PT-PERM"]-a["PT-REAL"]-a["NULL-PERM"]+a["NULL-REAL"],
          "gamma_real":a["NULL-REAL"]-a["PT-REAL"]
        }
        contrasts[s]={
          "tau_residual":float(per[s]["tau_residual"].sum()/LABELS),
          "gamma_real":float(per[s]["gamma_real"].sum()/LABELS),
          "delta_PRE":float((a["PT-PERM"]-a["PT-REAL"]).sum()/LABELS),
          "delta_NULL":float((a["NULL-PERM"]-a["NULL-REAL"]).sum()/LABELS),
        }
    rng=np.random.default_rng(BOOTSTRAP_SEED)
    idx=rng.integers(0,DOCS,size=(BOOTSTRAP_DRAWS,DOCS))
    denom=512*DOCS
    bs={}
    for name in ("tau_residual","gamma_real"):
        combined=sum(per[s][name] for s in SEEDS)/len(SEEDS)
        v=combined[idx].sum(axis=1)/denom
        bs[name]={
          "mean_delta_nll":float(combined.sum()/LABELS),
          "ci95_percentile":[float(x) for x in np.quantile(v,[.025,.975])],
          "seed_all_positive":all(contrasts[s][name]>0 for s in SEEDS),
        }
    verdict=("PASS_SCOPED_OOD_RESIDUAL_SIGNAL" if all(
        bs[name]["seed_all_positive"] and bs[name]["ci95_percentile"][0]>0
        for name in ("tau_residual","gamma_real")) else "FAIL_SCOPED_OOD_SIGNAL_NOT_ESTABLISHED")
    return nll,contrasts,bs,verdict

def check_gpu():
    demand(os.environ.get("CUBLAS_WORKSPACE_CONFIG")==":4096:8","CUBLAS_ENV")
    demand(torch.cuda.is_available() and torch.cuda.device_count()==1,"ONE_CUDA_DEVICE_REQUIRED")
    name=torch.cuda.get_device_name(0)
    demand("T4" in name.upper(),"FREE_COLAB_T4_REQUIRED")
    torch.backends.cuda.matmul.allow_tf32=False
    torch.backends.cudnn.allow_tf32=False
    torch.use_deterministic_algorithms(True)
    torch.set_float32_matmul_precision("highest")
    return name

def source_preflight_qa(source_zip,work,study,ood,output,check_cuda=True):
    demand(not (output/"CLAIM.json").exists() and not (output/"RESULT.json").exists(),"OUTPUT_ALREADY_CONSUMED")
    source_preflight_work=work/"model_source"
    source_preflight_work.mkdir(parents=True,exist_ok=True)
    with tempfile.TemporaryDirectory(dir=source_preflight_work) as tmp:
        src=preflight_sources(source_zip,Path(tmp))
        sw,p02=import_sources(src)
        packet=preflight_checkpoints(study)
        # Strict model construction for one real frozen checkpoint WITHOUT forward.
        cp,_=cp_paths(study,"S1","NULL-PERM")
        c=torch.load(cp,map_location="cpu",weights_only=True)
        m=build_model_from_frozen_state(c,sw,p02)
        demand(tuple(m.pos.weight.shape)==(256,256),"MODEL_CONTEXT")
        demand(not m.training,"MODEL_EVAL")
        del m,c
    data=preflight_ood(ood)
    device=check_gpu() if check_cuda else "NO_CUDA_SOURCE_ONLY"
    return {"checkpoint_integrity":packet,"ood_source_sha":OOD_PUBLIC,
       "ood_private_membership_sha":OOD_MEMBERSHIP,"ood_private_windows_sha":OOD_WINDOWS,
       "documents":DOCS,"windows":WINDOWS,"targets":LABELS,"device":device}

def execute(a):
    demand(a.owner_approved,"OWNER_APPROVAL_REQUIRED")
    study=Path(a.study).resolve(strict=True)
    ood=Path(a.ood).resolve(strict=True)
    source=Path(a.source_zip).resolve(strict=True)
    work=Path(a.work).resolve(strict=True)
    out=Path(a.output).resolve()
    demand(out!=study and out!=ood and out!=work and out.parent==work,"OUTPUT_MUST_BE_DIRECT_CHILD_OF_WORK")
    demand(not out.exists(),"OUTPUT_EXISTS_NO_SECOND_RUN")
    pre=source_preflight_qa(source,work,study,ood,out,check_cuda=True)
    print("OOD12_PREEXEC=PASS_12_CHECKPOINTS_3_OOD_SHA_SOURCE_MODEL_T4",flush=True)
    # The only science claim. Never retry automatically after START without result.
    out.mkdir(mode=0o700)
    claim={"schema":"ttm.gemma2.ood256.inference_only_claim.v1",
      "study_id":STUDY,"owner_approved":True,"scope":"ONE_SHOT_12_FROZEN_SCORING_ONLY",
      "seed_arms":list(CHECKPOINTS),"checkpoints_sha256":CHECKPOINTS,
      "source_sha256":SOURCE_ZIP_SHA,"model_source_sha256":{"p02":P02_SHA,"swap":SWAP_SHA},
      "ood_public_sha256":OOD_PUBLIC,"ood_membership_sha256":OOD_MEMBERSHIP,
      "ood_windows_sha256":OOD_WINDOWS,"bootstrap_seed":BOOTSTRAP_SEED,
      "bootstrap_draws":BOOTSTRAP_DRAWS,"targets":LABELS,
      "training":False,"checkpoint_selection":False,"lineage_modified":False,
      "inference_started":False}
    claim_sha=newjson(out/"CLAIM.json",claim)
    print("OOD12_CLAIM_CONSUMED_SHA256="+claim_sha,flush=True)
    with tempfile.TemporaryDirectory(dir=work) as tmp:
        src=preflight_sources(source,Path(tmp))
        sw,p02=import_sources(src)
        arrays=preflight_ood(ood)
        scores={}
        for seed in SEEDS:
            scores[seed]={}
            for arm in ARMS:
                key=seed+"/"+arm
                ck,ready=cp_paths(study,seed,arm)
                demand(sha_file(ck)==CHECKPOINTS[key] and readjson(ready)["checkpoint_sha256"]==CHECKPOINTS[key],
                       "CK_DRIFT_BEFORE_FORWARD_"+key)
                newjson(out/(seed+"__"+arm+"__START.json"),
                  {"seed":seed,"arm":arm,"checkpoint_sha256":CHECKPOINTS[key],
                   "claim_sha256":claim_sha,"no_training":True})
                c=torch.load(ck,map_location="cpu",weights_only=True)
                validate_checkpoint(c,seed,arm)
                m=build_model_from_frozen_state(c,sw,p02).to("cuda:0",dtype=torch.float32)
                score=score_arm(m,arrays["x"],arrays["y"],arrays["si"],"cuda:0")
                h=hashlib.sha256(np.asarray(score,dtype="<f8").tobytes()).hexdigest()
                receipt={"schema":"ttm.gemma2.ood256.scored_arm.private.v1",
                  "seed":seed,"arm":arm,"checkpoint_sha256":CHECKPOINTS[key],
                  "claim_sha256":claim_sha,"ood_membership_sha256":OOD_MEMBERSHIP,
                  "loss_sum_by_doc":score.tolist(),"score_bytes_sha256":h}
                newjson(out/(seed+"__"+arm+"__SCORE_PRIVATE.json"),receipt)
                scores[seed][arm]=score
                print("OOD12_ARM_SCORE_READY="+key,flush=True)
                del m,c;torch.cuda.empty_cache()
    all_scores={"schema":"ttm.gemma2.ood256.per_doc.private.v1",
      "claim_sha256":claim_sha,"ood_membership_sha256":OOD_MEMBERSHIP,
      "counts":[512]*DOCS,
      "loss_sum_by_seed_arm":{s:{a:scores[s][a].tolist() for a in ARMS} for s in SEEDS}}
    private_sha=newjson(out/"PER_DOCUMENT_PRIVATE.json",all_scores)
    nll,contrasts,bs,verdict=assess(scores)
    result={"schema":"ttm.gemma2.ood256.result.public.v1",
      "status":"COMPLETED_PENDING_INDEPENDENT_ADJUDICATION",
      "candidate_verdict":verdict,"study_id":STUDY,
      "checkpoint_count":len(CHECKPOINTS),"ood_documents":DOCS,"windows":WINDOWS,
      "targets":LABELS,"bootstrap_draws":BOOTSTRAP_DRAWS,
      "bootstrap_seed":BOOTSTRAP_SEED,"bootstrap_scope":"CONDITIONAL_ON_3_FIXED_SEEDS",
      "checkpoint_sha256":CHECKPOINTS,"ood_public_seal_sha256":OOD_PUBLIC,
      "claim_sha256":claim_sha,"private_per_doc_sha256":private_sha,
      "nll_nats_per_target":nll,"contrasts_by_seed":contrasts,"co_primary":bs,
      "training_executed":False,"lineage_modified":False,"gguf_executed":False}
    result_sha=newjson(out/"RESULT.json",result)
    print("OOD12_RESULT_SHA256="+result_sha,flush=True)
    print("OOD12_PENDING_INDEPENDENT_ADJUDICATION="+verdict,flush=True)

def fixture():
    x=np.zeros((WINDOWS,CONTEXT),dtype=np.int64)
    y=np.zeros((WINDOWS,CONTEXT),dtype=np.int64)
    for doc in range(DOCS):
        row=np.arange(513,dtype=np.int64)+doc
        x[2*doc]=row[:256]%VOCAB;y[2*doc]=row[1:257]%VOCAB
        x[2*doc+1]=row[256:512]%VOCAB;y[2*doc+1]=row[257:513]%VOCAB
    demand(np.array_equal(x[:,1:],y[:,:-1]) and np.array_equal(y[::2,-1],x[1::2,0]),"FIXTURE_LABEL_SHIFT")
    scores={}
    for sidx,s in enumerate(SEEDS):
        base=np.full(DOCS,512*(1.6+0.02*sidx))
        scores[s]={
          "PT-REAL":base.copy(),
          "PT-PERM":base+0.08*512,
          "NULL-REAL":base+0.04*512,
          "NULL-PERM":base+0.06*512}
    n,cs,b,verdict=assess(scores)
    demand(verdict=="PASS_SCOPED_OOD_RESIDUAL_SIGNAL","FIXTURE_POSITIVE_VERDICT")
    demand(all(b[k]["ci95_percentile"][0]>0 for k in ("tau_residual","gamma_real")),"FIXTURE_BOOT")
    scores["S3"]["NULL-REAL"]=scores["S3"]["PT-REAL"]-.01*512
    _,_,_,v=assess(scores)
    demand(v=="FAIL_SCOPED_OOD_SIGNAL_NOT_ESTABLISHED","FIXTURE_NEGATIVE_VERDICT")
    demand(len(CHECKPOINTS)==12,"FIXTURE_12_ARM_SET")
    print("OOD12_SYNTHETIC_CPU_QA=PASS_5_NO_FORWARD_NO_CLAIM")
    print("OOD12_SCIENCE=NOT_EXECUTED; TRAINING=0; GPU=0")

def main():
    a=argparse.ArgumentParser()
    a.add_argument("--mode",required=True,choices=("fixture","preflight","execute"))
    for name in ("study","ood","source-zip","work","output"):
        a.add_argument("--"+name,default="")
    a.add_argument("--owner-approved",action="store_true")
    v=a.parse_args()
    if v.mode=="fixture":fixture();return
    demand(all((v.study,v.ood,v.source_zip,v.work,v.output)),"REQUIRED_PATH")
    if v.mode=="preflight":
        out=Path(v.output).resolve()
        work=Path(v.work).resolve(strict=True)
        demand(out.parent==work,"PREFLIGHT_OUTPUT_BOUNDARY")
        p=source_preflight_qa(Path(v.source_zip),work,Path(v.study),Path(v.ood),out,check_cuda=True)
        print("OOD12_PREEXEC=PASS_ALL_GATES_NO_FORWARD_NO_CLAIM")
        print(json.dumps(p,sort_keys=True))
        return
    execute(v)

if __name__=="__main__":main()
