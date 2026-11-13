#!/usr/bin/env python3
"""H-DATA S1: native T4 actual P02 H0/H1 two-step interrupted-resume PARITY QA.
This is QA-only (8 optimizer updates across direct/restarted probes), NEVER science
training or FINAL inference. No science entry point exists in this script.
The frozen 128-step sampler schedule is checked from the immutable TRAIN metadata.
"""
from __future__ import annotations
import argparse, ast, copy, hashlib, importlib.util, json, os, pathlib, random, sys, tempfile
import numpy as np
import torch
from torch.nn import functional as F

RUN_ID="TTM_SMALL4M_HDATA_S1_MATCHED_BUDGET_FRESH_FINAL_V1"
PACK_SHA="184f68b4c0c800ef3e98362c2e20e1cd35baa269e926489a475664526ecd9913"
PARENT_SHA="cb985751795c8328ad65acf7ca4c1033ce35182c1bfbdb8c38550de629cb271b"
MANIFEST_SHA="ef2e6e67d49b1d5a921b1051df329f15574f1c10cece0ce49468acb53322d650"
BPE_SHA="cba18e60cee3d08a353ee6d4a451017289e45af7b4b1179c87171b9b78d7dfdc"
COMMITMENT_SHA="6c8c21c406b4bc30171244142c4226460a6735164f88fd425db7afa070a6f4f3"
PLAN_SHA="bcb354d29540e3a348b76173cdad1a6e2832dc81f995c717b68be6926d456591"
SOURCE_BLOBS={
 "base":"6c87e388da4d4a2b94dffba655861a390dfad73c",
 "sampler":"42cd94d202967ea2ba874d9b6f1e8fac10bb2fbb",
 "p02":"9762343e06cf800b50574c2871ae1ed58537fb18",
}
STEPS=(1025,1026); BUDGET=4096; V=2048; MICRO=8

def need(c,k):
    if not c:raise RuntimeError("HDATA_S1_T4_QA_HOLD:"+k)
def sha(path):
    h=hashlib.sha256()
    with open(path,"rb") as f:
        for block in iter(lambda:f.read(1<<20),b""):h.update(block)
    return h.hexdigest()
def blob(path):
    b=pathlib.Path(path).read_bytes()
    return hashlib.sha1(b"blob "+str(len(b)).encode()+b"\0"+b).hexdigest()
def import_pinned(path,name,expected_blob):
    need(pathlib.Path(path).is_file() and not pathlib.Path(path).is_symlink(),"SOURCE_FILE:"+name)
    need(blob(path)==expected_blob,"SOURCE_BLOB_DRIFT:"+name)
    p=pathlib.Path(path)
    if str(p.parent) not in sys.path:sys.path.insert(0,str(p.parent))
    spec=importlib.util.spec_from_file_location(name,path)
    module=importlib.util.module_from_spec(spec);sys.modules[name]=module
    spec.loader.exec_module(module)
    return module
def equal(a,b,path="state"):
    if torch.is_tensor(a) and torch.is_tensor(b):
        need(torch.equal(a.cpu(),b.cpu()),"TENSOR:"+path)
    elif isinstance(a,np.ndarray) and isinstance(b,np.ndarray):
        need(np.array_equal(a,b),"NDARRAY:"+path)
    elif isinstance(a,dict) and isinstance(b,dict):
        need(a.keys()==b.keys(),"DICT_KEYS:"+path)
        for k in a:equal(a[k],b[k],path+"/"+str(k))
    elif isinstance(a,(list,tuple)) and isinstance(b,(list,tuple)):
        need(len(a)==len(b),"SEQUENCE:"+path)
        for i,(x,y) in enumerate(zip(a,b)):equal(x,y,path+"/"+str(i))
    else: need(a==b,"VALUE:"+path)
def native_t4():
    need(torch.cuda.is_available() and torch.cuda.device_count()==1,"CUDA_ONE_T4")
    need("T4" in torch.cuda.get_device_name(0),"NVIDIA_T4_ONLY")
    need(str(torch.__version__)=="2.14.1+cu130","TORCH_VERSION_DRIFT")
    torch.backends.cuda.matmul.allow_tf32=False
    torch.backends.cudnn.allow_tf32=False
    torch.backends.cudnn.deterministic=True
    torch.backends.cudnn.benchmark=False
    torch.use_deterministic_algorithms(True)
    return torch.device("cuda")
def source_qa():
    tree=ast.parse(pathlib.Path(__file__).read_text("utf8"))
    functions={x.name for x in tree.body if isinstance(x,ast.FunctionDef)}
    required={"one_step","full_schedule","train_step","restore","save_state","pair_qa"}
    need(required<=functions,"QA_SOURCE_FUNCTIONS")
    return {"status":"PASS_AST_SOURCE_ONLY","arms":["H0","H1"],
      "science_run_entrypoint":False,"actual_T4_resume":"NOT_EXECUTED",
      "one_shot_training_started":False,"expected_plan_sha":PLAN_SHA,
      "checkpoint_parent_sha256":PARENT_SHA,"self_source_sha256":sha(__file__)}
def precheck(a):
    for p,expect in ((a.pack,PACK_SHA),(a.manifest,MANIFEST_SHA),(a.parent,PARENT_SHA),
                     (a.bpe,BPE_SHA),(a.commitment,COMMITMENT_SHA)):
        need(pathlib.Path(p).is_file() and sha(p)==expect,"INPUT_PIN:"+str(p))
    need(a.escrow and pathlib.Path(a.escrow).is_file(),"ESCROW_REQUIRED_BEFORE_FORWARD")
    need(sha(a.escrow)==a.escrow_sha,"ESCROW_SHA")
    e=json.loads(pathlib.Path(a.escrow).read_bytes())
    need(e.get("schema")=="ttm.hdata_s1.encrypted_blind_escrow.v1" and
         e.get("run_id")==RUN_ID and e.get("pairs")==24 and
         e.get("commitment_sha256")==COMMITMENT_SHA and
         e.get("before_model_forward") is True,"ESCROW_SCOPE")
    need(a.self_sha and sha(__file__)==a.self_sha,"QA_SCRIPT_NOT_SHA_PINNED")
def full_schedule(s,cp,counts,stories,first):
    g=torch.Generator(device="cpu");g.set_state(cp["sampler_state"].cpu().clone())
    exposed=np.zeros(2048,dtype=np.int32)
    rows=s.run_steps(g,counts,stories,first,exposed,128,1025)
    need(s.plan_fingerprint(rows)==PLAN_SHA,"FROZEN_128_STEP_SCHEDULE")
    need(len(rows)==128 and sum(len(v) for v in rows)==2928,"DRAW_COUNT")
    need(all(sum(x[2] for x in row)==BUDGET for row in rows),"STEP_BUDGET")
    return rows
def one_step(s,gen,counts,stories,first,exposed,step,reference):
    rows=s.one_step(gen,counts,stories,first,exposed,step)
    need(rows==reference,"INTERRUPT_SAMPLER_PLAN_DRIFT")
    return rows
def restore(base,p02,parent,state,dev):
    cp=copy.deepcopy(parent)
    if state is not None:
        need(state.get("schema")=="ttm.hdata_s1.t4qa.resume.v1" and
             state.get("run_id")==RUN_ID,"RESUME_SCHEMA")
        for key in ("model","optimizer","scheduler","sampler_state","grad_scaler_state",
                    "torch_cpu_rng","torch_cuda_rng","python_rng","numpy_rng"):
            cp[key]=copy.deepcopy(state[key])
    model,opt,sch,gen,scaler=base.clone_parent(p02,cp,dev)
    upstream=(state or parent)["optimizer"]["state"]
    for k,v in upstream.items():
        old=v.get("step"); new=opt.state_dict()["state"][k].get("step")
        if torch.is_tensor(old):
            need(torch.is_tensor(new) and new.data_ptr()!=old.data_ptr(),
                 "ORIGINAL_OPTIMIZER_STEP_ALIASED")
    exp=np.zeros(2048,dtype=np.int32) if state is None else np.asarray(state["h1_exposure"],dtype=np.int32).copy()
    return model,opt,sch,gen,scaler,exp
def train_step(parts,rows,arm,data,dev):
    model,opt,sch,gen,scaler,_=parts
    which=0 if arm=="H0" else 1
    inputs=[];targets=[]
    for k0,k1,n in rows:
        i=(k0,k1)[which]
        need(n<=int(data["train_count"][i]),"SHORT_TARGET_WINDOW")
        xx=data["train_x"][i].astype(np.int64).copy()
        yy=data["train_y"][i].astype(np.int64).copy()
        yy[n:]=-100
        need(int((yy!=-100).sum())==n,"TARGET_MASK_INCORRECT")
        inputs.append(xx);targets.append(yy)
    x=np.stack(inputs);y=np.stack(targets)
    need(int((y!=-100).sum())==BUDGET,"4096_VALID_TARGETS")
    key=next(iter(opt.state))
    attempts=0
    while True:
        model.train();opt.zero_grad(set_to_none=True)
        for begin in range(0,len(x),MICRO):
            xx=torch.as_tensor(x[begin:begin+MICRO],dtype=torch.long,device=dev)
            yy=torch.as_tensor(y[begin:begin+MICRO],dtype=torch.long,device=dev)
            with torch.autocast(device_type="cuda",dtype=torch.float16):
                logits,_=model(xx)
                loss=F.cross_entropy(logits.float().reshape(-1,V),yy.reshape(-1),
                                     ignore_index=-100,reduction="sum")/BUDGET
            need(bool(torch.isfinite(loss).item()),"NONFINITE_LOSS")
            scaler.scale(loss).backward()
        scaler.unscale_(opt)
        torch.nn.utils.clip_grad_norm_(model.parameters(),1.0)
        old=float(opt.state[key]["step"]);scale=float(scaler.get_scale())
        scaler.step(opt);scaler.update()
        new=float(opt.state[key]["step"]);scale_new=float(scaler.get_scale())
        if new==old+1.0:
            need(scale_new>=scale,"FP16_SCALE_DROP_AFTER_UPDATE")
            break
        need(new==old and scale_new<scale,"SCALER_SKIP_SEMANTICS")
        attempts+=1
        need(attempts<=12,"FP16_OVERFLOW_RETRY_LIMIT")
    sch.step()
    need(abs(opt.param_groups[0]["lr"]-3e-5)<1e-7,"LR_FLOOR_DRIFT")
    return {"actual_optimizer_updates":1,"skipped_fp16_attempts":attempts,"windows":len(rows),"targets":BUDGET}
def save_state(parts,step,arm):
    model,opt,sch,gen,scaler,exposure=parts
    q=np.random.get_state()
    return {"schema":"ttm.hdata_s1.t4qa.resume.v1","run_id":RUN_ID,
      "step":step,"arm":arm,"model":copy.deepcopy(model.state_dict()),
      "optimizer":copy.deepcopy(opt.state_dict()),"scheduler":copy.deepcopy(sch.state_dict()),
      "sampler_state":gen.get_state().clone(),"grad_scaler_state":copy.deepcopy(scaler.state_dict()),
      "h1_exposure":exposure.tolist(),"torch_cpu_rng":torch.get_rng_state().clone(),
      "torch_cuda_rng":[x.clone() for x in torch.cuda.get_rng_state_all()],
      "python_rng":random.getstate(),"numpy_rng":
      (q[0],q[1].tolist(),int(q[2]),int(q[3]),float(q[4]))}
def pair_qa(s,base,p02,parent,data,counts,stories,first,plans,arm,dev):
    def fresh(state=None):
        return restore(base,p02,parent,state,dev)
    def step(parts,idx):
        model,opt,sch,gen,scaler,exposure=parts
        rows=one_step(s,gen,counts,stories,first,exposure,STEPS[idx],plans[idx])
        return train_step(parts,rows,arm,data,dev)
    original_steps=copy.deepcopy(parent["optimizer"])
    # Continuous 1025 -> 1026
    direct=fresh();d1=step(direct,0);d2=step(direct,1)
    continuous=save_state(direct,1026,arm)
    # Interrupted at 1025; perform bytes-on-disk torch.save/readback
    staged=fresh();r1=step(staged,0)
    snapshot=save_state(staged,1025,arm)
    with tempfile.TemporaryDirectory(prefix="ttm_hdata_s1_t4qa_private_") as t:
        p=pathlib.Path(t)/"qa_step1025.pt"
        with p.open("xb") as f:
            torch.save(snapshot,f);f.flush();os.fsync(f.fileno())
        digest=sha(p)
        recovered=torch.load(p,map_location="cpu",weights_only=True)
    need(recovered["step"]==1025 and recovered["arm"]==arm,"RECOVERED_ARM_STEP")
    resumed=fresh(recovered);r2=step(resumed,1)
    after=save_state(resumed,1026,arm)
    for key in ("model","optimizer","scheduler","sampler_state","grad_scaler_state",
                "h1_exposure","torch_cpu_rng","torch_cuda_rng","python_rng","numpy_rng"):
        equal(continuous[key],after[key],key)
    equal(d1,r1,"STEP1025_RECEIPT");equal(d2,r2,"STEP1026_RECEIPT")
    equal(parent["optimizer"],original_steps,"FROZEN_PARENT_OPTIMIZER")
    return {"arm":arm,"continuous_vs_interrupted":"PASS_FULL_STATE_EXACT",
      "steps":[1025,1026],"per_step_targets":BUDGET,
      "qa_optimizer_updates":4,"science_optimizer_updates":0,
      "disk_checkpoint_sha256":digest,"real_training_arrays_used_in_QA":True,
      "private_QA_checkpoint_removed":True}
def main():
    p=argparse.ArgumentParser()
    p.add_argument("--mode",choices=("source-qa","t4-resume-qa"),default="source-qa")
    for k in ("pack","manifest","parent","bpe","commitment","escrow","escrow_sha",
              "sampler","base","p02","out","self_sha"):
        p.add_argument("--"+k.replace("_","-"))
    p.add_argument("--allow-eight-nonscience-qa-updates",action="store_true")
    a=p.parse_args()
    if a.mode=="source-qa":
        print(json.dumps(source_qa(),sort_keys=True));return
    need(a.allow_eight_nonscience_qa_updates,"EXPLICIT_T4_QA_ONLY_FLAG_REQUIRED")
    need(a.out and not pathlib.Path(a.out).exists(),"OUTPUT_EXISTS_OR_MISSING")
    need(all(getattr(a,k) for k in ("pack","manifest","parent","bpe","commitment","escrow",
           "escrow_sha","sampler","base","p02","self_sha")),"MISSING_INPUT")
    precheck(a)
    dev=native_t4()
    base=import_pinned(a.base,"ttm_2x2_colab_runner_candidate",SOURCE_BLOBS["base"])
    s=import_pinned(a.sampler,"ttm_hdata_s1_real_metadata_preexec_v1",SOURCE_BLOBS["sampler"])
    p02=base.load_model_source(a.p02)
    need(blob(a.p02)==SOURCE_BLOBS["p02"],"P02_GIT_BLOB")
    cp=base.check_input(a.pack,a.manifest,a.parent)
    counts,stories,first=s.get_real_metadata(a.pack)
    plans=full_schedule(s,cp,counts,stories,first)
    with np.load(a.pack,allow_pickle=False) as z:
        data={k:z[k] for k in ("train_x","train_y","train_count")}
    results=[pair_qa(s,base,p02,cp,data,counts,stories,first,plans[:2],arm,dev)
             for arm in ("H0","H1")]
    report={"schema":"ttm.hdata_s1.native_t4_h0_h1_resume_qa.v1",
      "status":"PASS_NATIVE_T4_FULL_INTERRUPTED_RESUME_EXACT_H0_H1",
      "arms":results,"torch":str(torch.__version__),"gpu":torch.cuda.get_device_name(0),
      "plan_sha256":PLAN_SHA,"source_sha256":sha(__file__),"source_blobs":SOURCE_BLOBS,
      "AES_escrow_SHA256":a.escrow_sha,
      "qa_optimizer_updates":8,"science_optimizer_updates":0,"science_inference":0,
      "FINAL_plaintext_access":False,"TEST_Q1_Q2_OOD_access":False,
      "new_science_release":"NOT_GRANTED_BY_QA_ALONE"}
    with open(a.out,"x",encoding="utf8") as f:
        json.dump(report,f,sort_keys=True,indent=2);f.write("\n");f.flush();os.fsync(f.fileno())
    print("HDATA_S1_T4_QA="+report["status"])
    print("HDATA_S1_SCIENCE_UPDATES=0")
if __name__=="__main__":main()
