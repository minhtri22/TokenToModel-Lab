#!/usr/bin/env python3
"""H-DATA-S1 128-step H0/H1 T4 science RUNNER CANDIDATE (fail closed).
Default source-only; --mode science REQUIRES an exact frozen owner GO lock,
native T4 resume QA receipt, source-rights receipt, SHA-pinned escrow and inputs.
NO training is started by importing or invoking default mode.
"""
from __future__ import annotations
import argparse, copy, hashlib, json, os, pathlib, shutil, sys
import numpy as np
import torch

RUN_ID="TTM_SMALL4M_HDATA_S1_MATCHED_BUDGET_FRESH_FINAL_V1"
PACK="184f68b4c0c800ef3e98362c2e20e1cd35baa269e926489a475664526ecd9913"
PARENT="cb985751795c8328ad65acf7ca4c1033ce35182c1bfbdb8c38550de629cb271b"
BPE="cba18e60cee3d08a353ee6d4a451017289e45af7b4b1179c87171b9b78d7dfdc"
COMMITMENT="6c8c21c406b4bc30171244142c4226460a6735164f88fd425db7afa070a6f4f3"
PLAN="bcb354d29540e3a348b76173cdad1a6e2832dc81f995c717b68be6926d456591"
T4_QA_SOURCE="7db0f999934036fc4f87beda9cd5a131377147d7307e9de5ac3a52b547882e62"
EXPECTED_TORCH="2.14.1+cu130";ARMS=("H0","H1");FIRST=1025;END=1152;CHECKPOINT_EVERY=32
BUDGET=4096;WINDOWS=2928;SLOTS=749568

def need(x,why):
    if not x:raise RuntimeError("HDATA_S1_SCIENCE_HOLD:"+why)
def sha(path):
    h=hashlib.sha256()
    with open(path,"rb") as f:
        for b in iter(lambda:f.read(1<<20),b""):h.update(b)
    return h.hexdigest()
def json_new(path,obj):
    with open(path,"x",encoding="utf8") as f:
        json.dump(obj,f,sort_keys=True,indent=2);f.write("\n");f.flush();os.fsync(f.fileno())
def load_exact(path,expected):
    need(path and pathlib.Path(path).is_file() and not pathlib.Path(path).is_symlink(),"REQUIRED_PATH_MISSING")
    need(sha(path)==expected,"SHA256_MISMATCH:"+pathlib.Path(path).name)
    return json.loads(pathlib.Path(path).read_bytes())
def gate(a):
    need(all([a.lock,a.lock_sha,a.qa_receipt,a.rights_receipt,a.escrow,a.escrow_sha,
              a.runner_qa,a.sampler,a.base,a.p02,a.pack,a.manifest,a.parent,a.bpe,
              a.commitment,a.root]),"INCOMPLETE_INPUTS")
    lock=load_exact(a.lock,a.lock_sha)
    need(lock.get("authorization")=="TTM_HDATA_S1_SCIENCE_ONE_SHOT_GO" and
         lock.get("run_id")==RUN_ID and lock.get("arms")==["H0","H1"] and
         lock.get("steps_each")==128 and lock.get("targets_per_step")==BUDGET,
         "ONE_SHOT_OWNER_GO_LOCK_NOT_GRANTED")
    need(lock.get("science_runner_sha256")==sha(__file__),"SCIENCE_SOURCE_NOT_LOCKED")
    need(lock.get("native_resume_qa_source_sha256")==T4_QA_SOURCE,"QA_SOURCE_PIN")
    need(lock.get("native_resume_qa_receipt_sha256")==sha(a.qa_receipt),"QA_RECEIPT_PIN")
    need(lock.get("new_hdata_rights_receipt_sha256")==sha(a.rights_receipt),"RIGHTS_RECEIPT_PIN")
    need(lock.get("fresh_final24_escrow_sha256")==a.escrow_sha,"ESCROW_LOCK_PIN")
    need(lock.get("checkpoint_parent_sha256")==PARENT and
         lock.get("train_pack_sha256")==PACK and
         lock.get("BPE_manifest_sha256")==BPE and
         lock.get("paired_schedule_sha256")==PLAN and
         lock.get("public_final24_commitment_sha256")==COMMITMENT,"PARENT_OR_EVAL_PIN")
    need(lock.get("no_reused_FINAL_NEXT24") is True and lock.get("no_TEST_Q1_Q2_OOD") is True,
         "DATA_SCOPE")
    qa=load_exact(a.qa_receipt,lock["native_resume_qa_receipt_sha256"])
    need(qa.get("status")=="PASS_NATIVE_T4_FULL_INTERRUPTED_RESUME_EXACT_H0_H1" and
         qa.get("source_sha256")==T4_QA_SOURCE and
         qa.get("qa_optimizer_updates")==8 and qa.get("science_optimizer_updates")==0,
         "NATIVE_T4_RESUME_QA_NOT_ACCEPTED")
    rights=load_exact(a.rights_receipt,lock["new_hdata_rights_receipt_sha256"])
    need(rights.get("status")=="PASS_NEW_HDATA_SCOPE_AND_LICENSE" and
         rights.get("exact_original_pack_sha256")==PACK,"H_DATA_SOURCE_RIGHTS_INCOMPLETE")
    escrow=load_exact(a.escrow,a.escrow_sha)
    need(escrow.get("schema")=="ttm.hdata_s1.encrypted_blind_escrow.v1" and
         escrow.get("run_id")==RUN_ID and escrow.get("commitment_sha256")==COMMITMENT and
         escrow.get("pairs")==24 and escrow.get("before_model_forward") is True,"AES_ESCROW_MISSING")
    need(sha(a.runner_qa)==T4_QA_SOURCE,"QA_SOURCE_BYTES_DRIFT")
    for p,expected in ((a.pack,PACK),(a.parent,PARENT),(a.bpe,BPE),(a.commitment,COMMITMENT)):
        need(sha(p)==expected,"SOURCE_PIN_DRIFT")
    need(torch.cuda.is_available() and torch.cuda.device_count()==1,"ONE_GPU_REQUIRED")
    need("T4" in torch.cuda.get_device_name(0) and str(torch.__version__)==EXPECTED_TORCH,
         "T4_RUNTIME_DRIFT")
    return lock
def source_only():
    return {"status":"CANDIDATE_SOURCE_ONLY_NO_TRAIN",
      "run_id":RUN_ID,"arms":list(ARMS),"steps_each":128,"targets_each":524288,
      "forward_windows_each":WINDOWS,"slots_each":SLOTS,
      "READY_last_checkpoint_steps":[1056,1088,1120,1152],
      "source_sha256":sha(__file__),"science_authorized":False}
def read_ready(root,arm,expected):
    d=root/("ARM_"+arm)
    if not d.exists():return None,None,None
    files=sorted(d.glob("checkpoint_*/READY.json"))
    if not files:return None,None,None
    last=files[-1].parent
    j=json.loads((last/"READY.json").read_bytes())
    need(j.get("arm")==arm and j.get("run_id")==RUN_ID and
         j.get("science_lock_sha256")==expected,"READY_SCOPE")
    cp=last/"state.pt"; need(cp.exists() and sha(cp)==j.get("checkpoint_sha256"),"READY_SHA")
    snapshot=torch.load(cp,map_location="cpu",weights_only=True)
    need(snapshot["step"]==j["step"] and snapshot["arm"]==arm,"READY_CHECKPOINT_SCOPE")
    return j["step"],snapshot,j
def no_inflight_after_ready(d,last):
    for p in d.glob("STEP_*_*.json"):
        step=int(p.stem.split("_")[-1])
        need(last is not None and step<=last,"IN_FLIGHT_AFTER_LAST_READY_NO_REPLAY")
def save_ready(d,arm,step,state,lock_sha):
    folder=d/("checkpoint_%04d"%step)
    need(not folder.exists(),"CHECKPOINT_OVERWRITE")
    folder.mkdir(exist_ok=False)
    temp=folder/"state.pt"
    with temp.open("xb") as f:torch.save(state,f);f.flush();os.fsync(f.fileno())
    digest=sha(temp)
    json_new(folder/"READY.json",{"schema":"ttm.hdata_s1.ready.last.v1",
       "run_id":RUN_ID,"arm":arm,"step":step,"checkpoint_sha256":digest,
       "science_lock_sha256":lock_sha,"parent_sha256":PARENT,"pack_sha256":PACK})
    return digest
def science(a,lock):
    import importlib.util
    # The QA module imports no trained model by default; all model construction is below GO gate.
    spec=importlib.util.spec_from_file_location("ttm_hdata_s1_frozen_t4_qa",a.runner_qa)
    q=importlib.util.module_from_spec(spec);sys.modules[spec.name]=q;spec.loader.exec_module(q)
    dev=q.native_t4()
    base=q.import_pinned(a.base,"ttm_2x2_colab_runner_candidate",q.SOURCE_BLOBS["base"])
    sampler=q.import_pinned(a.sampler,"ttm_hdata_s1_real_metadata_preexec_v1",q.SOURCE_BLOBS["sampler"])
    p02=base.load_model_source(a.p02)
    cp=base.check_input(a.pack,a.manifest,a.parent)
    c,s,f=sampler.get_real_metadata(a.pack)
    plans=q.full_schedule(sampler,cp,c,s,f)
    with np.load(a.pack,allow_pickle=False) as z:
        data={x:z[x] for x in ("train_x","train_y","train_count","val_x","val_y",
                              "val_count","val_story_index")}
    root=pathlib.Path(a.root)
    if a.resume:
        need(root.is_dir(),"RESUME_ROOT_MISSING")
        m=json.loads((root/"RUN_MANIFEST.json").read_bytes())
        need(m=={"run_id":RUN_ID,"owner_lock_sha256":a.lock_sha,
                 "science_source_sha256":sha(__file__),"arms":["H0","H1"]},"RUN_MANIFEST_DRIFT")
    else:
        need(not root.exists() and root.parent.is_dir(),"NEW_RUN_DIR_ALREADY_EXISTS")
        need(shutil.disk_usage(root.parent).free>=2*1024**3,"DRIVE_FREE_BELOW_2_GIB")
        root.mkdir(exist_ok=False)
        json_new(root/"RUN_MANIFEST.json",{"run_id":RUN_ID,"owner_lock_sha256":a.lock_sha,
                 "science_source_sha256":sha(__file__),"arms":["H0","H1"]})
    for arm in ARMS:
        d=root/("ARM_"+arm)
        if not d.exists():d.mkdir(exist_ok=False)
        last,state,ready=read_ready(root,arm,a.lock_sha)
        no_inflight_after_ready(d,last)
        if (d/"FINAL_UNADJUDICATED.json").exists():
            need(last==END,"FINAL_WITHOUT_LAST_READY")
            continue
        parts=q.restore(base,p02,cp,state,dev)
        model,opt,sch,gen,scaler,exp=parts
        start=FIRST if last is None else last+1
        for step in range(start,END+1):
            # Verify schedule prefix by exact paired rows, then advance own sampler state.
            rows=q.one_step(sampler,gen,c,s,f,exp,step,plans[step-FIRST])
            json_new(d/("STEP_BEGIN_%04d.json"%step),{"step":step,"arm":arm})
            q.train_step(parts,rows,arm,data,dev)
            json_new(d/("STEP_DONE_%04d.json"%step),{"step":step,"arm":arm})
            if step%CHECKPOINT_EVERY==0:
                save_ready(d,arm,step,q.save_state(parts,step,arm),a.lock_sha)
        val=base.eval_original_val_nll(model,data,dev)
        need(val["val_target_count"]==61122,"VAL_COUNT_SOURCE_DRIFT")
        final_ready=json.loads((d/"checkpoint_1152"/"READY.json").read_bytes())
        json_new(d/"FINAL_UNADJUDICATED.json",{"run_id":RUN_ID,"arm":arm,
          "step":END,"valid_target_presentations":128*BUDGET,
          "last_ready_checkpoint_sha256":final_ready["checkpoint_sha256"],
          "val":val,"science_outcome":"UNADJUDICATED_NO_FINAL_INFERENCE"})
    print("HDATA_S1_T4_TWO_ARM_TRAINING_COMPLETED_UNADJUDICATED")
def main():
    ap=argparse.ArgumentParser()
    ap.add_argument("--mode",choices=("source-only","science"),default="source-only")
    for k in ("lock","lock_sha","qa_receipt","rights_receipt","escrow","escrow_sha",
              "runner_qa","sampler","base","p02","pack","manifest","parent","bpe",
              "commitment","root"):
        ap.add_argument("--"+k.replace("_","-"))
    ap.add_argument("--resume",action="store_true")
    a=ap.parse_args()
    if a.mode=="source-only":
        print(json.dumps(source_only(),sort_keys=True));return
    lock=gate(a)
    science(a,lock)
if __name__=="__main__":main()
