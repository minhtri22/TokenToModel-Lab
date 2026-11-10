#!/usr/bin/env python3
"""G1-P0 quick exploratory REAL-Qwen proof of concept. No private G1 data.
Only fixed self-authored prompts, no TinyStories, manifests or private TEST.
Do not report this as G1 preregistered science PASS.
"""
import argparse
import gc
import hashlib
import json
from pathlib import Path
import time
import numpy as np

SOURCE=("Qwen/Qwen3-0.6B","c1899de289a04d12100db370d81485cdf75e47ca",1024)
TARGET=("Qwen/Qwen3-1.7B","70d244cc86ccca08cf5af4e1e306ecf908b1ad5e",2048)
N_FIT,N_EVAL,ALPHA=16,8,100.0
MAX_SECONDS,MAX_VRAM_GIB=2100,12.
PROBES=(
 (" The child smiled."," The child cried."),
 (" Everyone felt safe."," Everyone felt afraid."),
 (" The toy was found."," The toy was lost."),
 (" She told the truth."," She told a lie."),
 (" He shared the toy."," He kept the toy."),
 (" They stayed home."," They went outside."),
 (" The door was open."," The door was closed."),
 (" The story ended happily."," The story ended sadly."),
)
# Original, invented examples. The list is separate from G1 corpus and TEST.
PROMPTS=(
 "A gardener planted red flowers beside a wooden gate and watered the soil before breakfast.",
 "A student found a little wooden box under the table and wondered what was hidden inside.",
 "The children walked to the river after lunch and watched ducks swimming past the bridge.",
 "A small puppy waited by the door until its family returned from the crowded market.",
 "During the storm Nora closed the windows and brought her brother a warm blanket.",
 "Leo placed his favorite toy on a bench and hurried toward the playground with his friends.",
 "The baker prepared two fresh loaves before sunrise and shared them with a neighbor.",
 "On the way to school Sara found a shiny key beside the old stone fountain.",
 "A little robot crossed the room and stopped when its battery indicator became red.",
 "The family packed sandwiches and fruit for a picnic beside the quiet forest.",
 "When the music began the dancers gathered in the hall and greeted their teacher.",
 "Ben borrowed an umbrella because dark clouds were gathering over the town square.",
 "The librarian found a damaged page in an old book and protected it in a folder.",
 "A tired cyclist rested under a tree as the wind moved through the leaves.",
 "After dinner Emma noticed the garden gate was open and looked for her dog.",
 "The farmer counted the apples in his basket and saved the brightest for his daughter.",
 "Owen heard a gentle knock at the front door and slowly walked into the hall.",
 "A child dropped her toy train behind the sofa and asked her grandfather for help.",
 "Two friends disagreed about a game but decided to take turns and continue playing.",
 "A cat sat next to an empty bowl until a kind neighbor brought some food.",
 "When rain finally stopped the campers stepped outside and saw a rainbow overhead.",
 "Lily searched the classroom for her notebook and remembered leaving it near the window.",
 "An old wooden bridge creaked in the wind so the travelers crossed one by one.",
 "A boy woke to birds singing at dawn and opened the curtains to see the morning.",
)

def sha(v):
 return hashlib.sha256(v.encode("utf-8")).hexdigest()

def ridge(x,y,z,alpha=ALPHA):
 x,y,z=[np.asarray(a,dtype=np.float64) for a in (x,y,z)]
 if x.ndim!=2 or y.ndim!=2 or z.ndim!=2 or len(x)!=len(y) or x.shape[1]!=z.shape[1]:
  raise RuntimeError("STOP_RIDGE_SHAPE")
 if not all(np.isfinite(v).all() for v in (x,y,z)): raise RuntimeError("STOP_NONFINITE")
 mu,sd=x.mean(0),np.maximum(x.std(0),1e-6)
 a,b=(x-mu)/sd,(z-mu)/sd
 ym=y.mean(0)
 return ym+(b@a.T)@np.linalg.solve(a@a.T+alpha*np.eye(len(a)),y-ym)

def analyze(xs,xt,ys):
 a,b=xs[:N_FIT],xs[N_FIT:]
 t,u=xt[:N_FIT],xt[N_FIT:]
 y,v=ys[:N_FIT],ys[N_FIT:]
 rng=np.random.default_rng(20261110)
 oracle=ridge(t,y,u)
 aligned=ridge(t,y,ridge(a,t,b))
 shuffled=ridge(t,y,ridge(a[rng.permutation(N_FIT)],t,b))
 direct=ridge(a,y,b)
 mean=np.broadcast_to(y.mean(0),v.shape)
 mse_base=float(np.mean((mean-v)**2))
 outputs={"aligned":aligned,"direct":direct,"target_oracle":oracle,
          "shuffled":shuffled,"train_mean":mean}
 return {k:{"mse":float(np.mean((p-v)**2)),
            "relative_gain_over_train_mean":(None if mse_base<=1e-12
               else float(1-np.mean((p-v)**2)/mse_base))}
         for k,p in outputs.items()}

def selftest():
 assert len(PROMPTS)==N_FIT+N_EVAL==24 and len(set(PROMPTS))==24
 assert len(PROBES)==8 and all(len(p)>65 for p in PROMPTS)
 rng=np.random.default_rng(10)
 x=rng.normal(size=(24,9))
 t=x@rng.normal(size=(9,15))
 y=t@rng.normal(size=(15,8))
 r=analyze(x,t,y)
 assert len(r)==5 and all(np.isfinite(v["mse"]) for v in r.values())
 print(json.dumps({"status":"PASS_SELFTEST_SYNTHETIC_ONLY",
  "prompts":24,"fit":16,"eval":8,"probe_pairs":8,
  "original_G1_private_TEST_opened":False}))

def run(outpath):
 import torch
 from transformers import AutoTokenizer,AutoModelForCausalLM
 if not torch.cuda.is_available(): raise RuntimeError("STOP_GPU_REQUIRED")
 gpu=torch.cuda.get_device_name(0)
 if "T4" not in gpu: raise RuntimeError("STOP_EXPECTED_COLAB_T4")
 start=time.monotonic()
 def guard(label):
  if time.monotonic()-start>MAX_SECONDS: raise RuntimeError("STOP_DEMO_TIME_"+label)
  if torch.cuda.max_memory_reserved(0)/2**30>MAX_VRAM_GIB:
   raise RuntimeError("STOP_DEMO_VRAM_"+label)
 def load(spec):
  print("LOADING",spec[0],spec[1],flush=True)
  tok=AutoTokenizer.from_pretrained(spec[0],revision=spec[1],trust_remote_code=False)
  model=AutoModelForCausalLM.from_pretrained(spec[0],revision=spec[1],
    dtype=torch.float16,device_map=0,low_cpu_mem_usage=True,trust_remote_code=False)
  model.eval()
  guard("MODEL_LOAD")
  return tok,model
 def hidden(tok,model,prompt,dim):
  ids=tok(prompt,add_special_tokens=False)["input_ids"]
  if not 1<=len(ids)<=96: raise RuntimeError("STOP_PREFIX_TOKEN_COUNT")
  with torch.inference_mode():
   outputs=model(input_ids=torch.tensor([ids],dtype=torch.long,device="cuda"),
     use_cache=False,output_hidden_states=True,return_dict=True)
   if len(outputs.hidden_states)!=29 or outputs.hidden_states[28].shape[-1]!=dim:
    raise RuntimeError("STOP_HIDDEN_SHAPE")
   value=outputs.hidden_states[28][0,-1].float().cpu().numpy()
  del outputs
  if not np.isfinite(value).all(): raise RuntimeError("STOP_NONFINITE_HIDDEN")
  return value,ids
 def score(tok,model,prefix,continuation):
  ids=tok(continuation,add_special_tokens=False)["input_ids"]
  if not ids: raise RuntimeError("STOP_EMPTY_PROBE")
  with torch.inference_mode():
   logits=model(input_ids=torch.tensor([prefix+ids],device="cuda"),
     use_cache=False,return_dict=True).logits
   span=logits[0,len(prefix)-1:len(prefix)-1+len(ids),:].float()
   tokens=torch.tensor(ids,device="cuda",dtype=torch.long).view(-1,1)
   value=float(torch.log_softmax(span,dim=-1).gather(1,tokens).sum().item())
  del logits,span,tokens
  return value/len(continuation.encode("utf-8"))
 matrices={}
 meta={}
 for label,spec in (("source",SOURCE),("target",TARGET)):
  guard("PRE_"+label)
  tok,model=load(spec)
  hs,ys=[],[]
  for i,prompt in enumerate(PROMPTS):
   guard(label+"_"+str(i))
   h,ids=hidden(tok,model,prompt,spec[2])
   hs.append(h)
   if label=="target":
    yi=[score(tok,model,ids,pa)-score(tok,model,ids,pb) for pa,pb in PROBES]
    if not np.isfinite(yi).all(): raise RuntimeError("STOP_NONFINITE_PROBES")
    ys.append(yi)
   print(label.upper()+"_ROW="+str(i+1)+"/24",flush=True)
  matrices[label]=np.asarray(hs,dtype=np.float64)
  if label=="target": matrices["responses"]=np.asarray(ys,dtype=np.float64)
  meta[label]={"model":spec[0],"revision":spec[1],
   "hidden_shape":list(matrices[label].shape),
   "peak_reserved_gib":round(torch.cuda.max_memory_reserved(0)/2**30,4)}
  del tok,model,hs,ys
  gc.collect()
  torch.cuda.empty_cache()
 guard("REPORT")
 results=analyze(matrices["source"],matrices["target"],matrices["responses"])
 receipt={"schema":"ttm.six.g1.exploratory_real_qwen_tiny_poc.v1",
  "status":"EXPLORATORY_REAL_QWEN_COMPLETED_NO_G1_TEST",
  "science_G1_original_executed":False,"private_G1_TEST_opened":False,
  "uses_TinyStories":False,"models_frozen":True,"gpu":gpu,
  "fit_rows":N_FIT,"eval_rows":N_EVAL,"ridge_alpha":ALPHA,
  "probe_pairs":len(PROBES),"prompts_sha256":[sha(x) for x in PROMPTS],
  "model_stats":meta,"prediction_results":results,
  "elapsed_seconds":round(time.monotonic()-start,2),
  "limitations":"Eight synthetic held-out rows; no significance/generalization/science PASS"}
 outpath.parent.mkdir(parents=True,exist_ok=True)
 with outpath.open("x",encoding="utf-8") as f:json.dump(receipt,f,indent=2,sort_keys=True)
 print("G1_P0_RESULT="+json.dumps({"status":receipt["status"],
  "metrics":results,"output":str(outpath)},sort_keys=True),flush=True)
 print("G1_SCIENCE_LOCK=HOLD",flush=True)

def main():
 parser=argparse.ArgumentParser()
 parser.add_argument("--mode",choices=["selftest","run"],default="selftest")
 parser.add_argument("--output",default="/content/g1_p0_real_qwen_receipt.json")
 args=parser.parse_args()
 if args.mode=="selftest":selftest()
 else:run(Path(args.output))

if __name__=="__main__":main()
