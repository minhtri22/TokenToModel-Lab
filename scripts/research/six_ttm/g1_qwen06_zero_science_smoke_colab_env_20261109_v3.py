#!/usr/bin/env python3
"""G1 synthetic-only Qwen3 hidden-state smoke, Colab v3 patch-flexible. No science."""
import argparse, hashlib, importlib.metadata as md, importlib.util, json
import os, platform, shutil, struct, sys, traceback
from pathlib import Path

ROOT=Path("/content/ttm_six_g1_v3")
MODEL="Qwen/Qwen3-0.6B"
REV="c1899de289a04d12100db370d81485cdf75e47ca"
WEIGHT_SHA="f47f71177f32bcd101b7573ec9171e6a57f4f4d31148d38e382306f42996874b"
TORCH_PIN="2.14.1+cu130"
PINS={"transformers":"5.22.1","huggingface-hub":"1.33.0","tokenizers":"0.23.3","safetensors":"0.8.0"}
FILES=["config.json","generation_config.json","tokenizer.json","tokenizer_config.json",
       "merges.txt","vocab.json","model.safetensors","LICENSE"]
GIB=1024**3

def check(ok, reason):
    if not ok: raise RuntimeError(reason)

def sha(path):
    h=hashlib.sha256()
    with open(path,"rb") as f:
        for part in iter(lambda:f.read(8*1024*1024),b""): h.update(part)
    return h.hexdigest()

def environment():
    try: colab=importlib.util.find_spec("google.colab") is not None
    except (ImportError, ValueError, ModuleNotFoundError): colab=False
    check(Path("/content").is_dir() and colab,"COLAB_ONLY")
    check(sys.version_info[:2]==(3,13) and sys.version_info.releaselevel=="final",
          "PYTHON_3_13_STABLE_REQUIRED_ACTUAL_"+platform.python_version())
    versions={n:md.version(n) for n in PINS}
    check(versions==PINS,"LIBRARY_VERSIONS_MISMATCH:"+repr(versions))
    import torch
    check(torch.__version__==TORCH_PIN,"TORCH_PIN_MISMATCH:"+torch.__version__)
    check(torch.cuda.is_available(),"CUDA_NOT_AVAILABLE")
    name=torch.cuda.get_device_name(0)
    cc=tuple(torch.cuda.get_device_capability(0))
    check("T4" in name and cc==(7,5),"GPU_NOT_T4")
    free,total=torch.cuda.mem_get_info(0)
    disk=shutil.disk_usage("/content").free
    check(free>=8*GIB and total>=12*GIB and disk>=6*GIB,"RESOURCE_GUARD_FAIL")
    return torch,{"python":platform.python_version(),"python_executable":sys.executable,
        "torch":torch.__version__,"packages":versions,
        "gpu_name":name,"cc":cc,"gpu_free_bytes":free,"gpu_total_bytes":total,"disk_free_bytes":disk}

def run_smoke(torch,report):
    os.environ["HF_HOME"]=str(ROOT/"hf_home")
    os.environ["HF_HUB_CACHE"]=str(ROOT/"hf_home"/"hub")
    os.environ["HF_HUB_DISABLE_TELEMETRY"]="1"
    from huggingface_hub import snapshot_download
    from transformers import AutoTokenizer,AutoModelForCausalLM
    folder=Path(snapshot_download(repo_id=MODEL,revision=REV,
                      allow_patterns=FILES,local_dir=str(ROOT/"model"),max_workers=1))
    hashes={}
    for name in FILES:
        f=folder/name
        check(f.is_file() and not f.is_symlink(),"SOURCE_FILE_MISSING_OR_LINK:"+name)
        hashes[name]=sha(f)
    report["file_sha256"]=hashes
    check(hashes["model.safetensors"]==WEIGHT_SHA,"WEIGHT_SHA256_MISMATCH")
    conf=json.loads((folder/"config.json").read_text(encoding="utf-8"))
    check((conf["model_type"],conf["hidden_size"],conf["num_hidden_layers"],conf["vocab_size"])
          ==("qwen3",1024,28,151936),"CONFIG_CONTRACT_MISMATCH")
    report["weight_verified_before_load"]=True
    torch.manual_seed(20261109)
    torch.cuda.manual_seed_all(20261109)
    torch.cuda.reset_peak_memory_stats(0)
    tok=AutoTokenizer.from_pretrained(str(folder),local_files_only=True,trust_remote_code=False)
    tok.padding_side="right"
    if tok.pad_token is None: tok.pad_token=tok.eos_token
    model=AutoModelForCausalLM.from_pretrained(str(folder),dtype=torch.float16,
                  local_files_only=True,trust_remote_code=False).to("cuda:0").eval()
    check(not model.training,"NOT_EVAL_MODE")
    batch=tok(["x0 x1 x2 x3 x4 x5 x6 x7.",
               "a0 a1 a2 a3 a4 a5 a6 a7 a8 a9 a10 a11 a12 a13 a14 a15."],
              padding=True,add_special_tokens=False,return_tensors="pt")
    ids,mask=batch["input_ids"].cuda(),batch["attention_mask"].cuda()
    seq=ids.shape[1]
    lens=mask.sum(1).tolist()
    check(8<=seq<=64 and min(lens)<seq and min(lens)>=1,"PADDING_OR_LEN_FAIL")
    repeated=[]
    with torch.inference_mode():
        for _ in range(2):
            out=model(input_ids=ids,attention_mask=mask,use_cache=False,
                      output_hidden_states=True,return_dict=True)
            hs=out.hidden_states
            check(hs is not None and len(hs)==29,"EXPECTED_29_STATES")
            check(tuple(out.logits.shape)==(2,seq,151936)
                  and bool(torch.isfinite(out.logits).all().item()),"LOGITS_INVALID")
            selected={}
            for i,h in enumerate(hs):
                check(tuple(h.shape)==(2,seq,1024)
                      and bool(torch.isfinite(h).all().item()),"HIDDEN_INVALID_"+str(i))
                if i in (0,7,14,21,28):
                    signatures=[]
                    for row in range(2):
                        vec=h[row,int(lens[row])-1].float().cpu().tolist()
                        blob=struct.pack("<"+"f"*len(vec),*vec)
                        signatures.append(hashlib.sha256(blob).hexdigest())
                    selected[str(i)]=signatures
            repeated.append(selected)
            del out,hs
    check(repeated[0]==repeated[1],"REPEATABILITY_MISMATCH")
    peak=int(torch.cuda.max_memory_reserved(0))
    check(peak<=6*GIB,"GPU_PEAK_OVER_6_GIB")
    report.update({"hidden_state_count":29,"shape":[2,int(seq),1024],"lengths":lens,
       "selected_layer_hashes":repeated[0],"repeatability":"SAME_RUNTIME_EXACT_F32_HASH",
       "max_gpu_reserved_bytes":peak,"training":False,"science_data":False})

def main():
    parser=argparse.ArgumentParser()
    parser.add_argument("--phase",required=True,choices=["preflight","smoke"])
    phase=parser.parse_args().phase
    # Fail closed without writing ANY directory on Windows or other non-Colab hosts.
    try:
        colab_host=Path("/content").is_dir() and importlib.util.find_spec("google.colab") is not None
    except (ImportError, ValueError, ModuleNotFoundError):
        colab_host=False
    if not colab_host:
        print("G1_STATUS=STOP_FAIL_CLOSED")
        print("G1_REASON=GOOGLE_COLAB_REQUIRED_NO_WRITES")
        return 1
    ROOT.mkdir(parents=True,exist_ok=True)
    report={"phase":phase,"model":MODEL,"revision":REV,"expected_weight_sha256":WEIGHT_SHA,
            "environment_amendment":"COLAB_RUNTIME_20261109_V3_PY313_PATCH_FLEX",
            "parent_v1_source_blob":"24318de7d0196944a0a9a6d6be9851099f18b85b",
            "parent_v2_source_blob":"c98811e167696f86e94e3da9d01f3b9f020c3cc6",
            "observed_python":platform.python_version(),
            "observed_python_executable":sys.executable,
            "science_executed":False,"status":"STOP"}
    rc=1
    try:
        torch,env=environment()
        report["environment"]=env
        if phase=="smoke": run_smoke(torch,report)
        report["status"]="PASS_PREFLIGHT_ONLY" if phase=="preflight" else "PASS_TECHNICAL_ONLY"
        rc=0
    except Exception as exc:
        report.update({"status":"STOP_FAIL_CLOSED","error_type":type(exc).__name__,
            "error":str(exc)[:800],"traceback_tail":traceback.format_exc(limit=3)[-1500:]})
    path=ROOT/("G1_"+phase.upper()+"_RECEIPT.json")
    path.write_text(json.dumps(report,sort_keys=True,indent=2)+"\n",encoding="utf-8")
    print("G1_STATUS="+report["status"])
    print("G1_RECEIPT="+str(path))
    if rc: print("G1_REASON="+report.get("error","unknown"))
    return rc

if __name__=="__main__":
    raise SystemExit(main())
