#!/usr/bin/env python3
"""G1 target Qwen3-1.7B: one technical-only Colab T4 verification. No science data."""
from __future__ import annotations
import argparse, hashlib, importlib.metadata as md, importlib.util, json
import os, platform, shutil, struct, sys, traceback
from pathlib import Path

ROOT=Path("/content/ttm_six_g1_target17")
MODEL="Qwen/Qwen3-1.7B"
REV="70d244cc86ccca08cf5af4e1e306ecf908b1ad5e"
WEIGHTS={
    "model-00001-of-00002.safetensors":"169ad53ec313c3a34b06c0809216e4fc072cce444a5d4ff2b59690d064130ed5",
    "model-00002-of-00002.safetensors":"912becff8d60672aa8628ef08c05898d9adf17c2ad4ae3caf99b065622fdeff9",
}
FILES=["config.json","generation_config.json","tokenizer.json","tokenizer_config.json",
       "merges.txt","vocab.json","model.safetensors.index.json","LICENSE"]+list(WEIGHTS)
LIBS={"transformers":"5.22.1","huggingface-hub":"1.33.0",
      "tokenizers":"0.23.3","safetensors":"0.8.0"}
TORCH_PIN="2.14.1+cu130"
GIB=1024**3

def check(ok,why):
    if not ok: raise RuntimeError(why)

def file_sha(p:Path):
    h=hashlib.sha256()
    with p.open("rb") as f:
        for chunk in iter(lambda:f.read(8*1024*1024),b""): h.update(chunk)
    return h.hexdigest()

def preflight():
    check(sys.version_info[:2]==(3,13) and sys.version_info.releaselevel=="final",
          "PYTHON_3_13_STABLE_REQUIRED_ACTUAL_"+platform.python_version())
    versions={name:md.version(name) for name in LIBS}
    check(versions==LIBS,"PACKAGE_PIN_MISMATCH:"+repr(versions))
    import torch
    check(torch.__version__==TORCH_PIN,"TORCH_PIN_MISMATCH:"+torch.__version__)
    check(torch.cuda.is_available(),"CUDA_UNAVAILABLE")
    name=torch.cuda.get_device_name(0)
    cc=tuple(torch.cuda.get_device_capability(0))
    check("T4" in name and cc==(7,5),"GPU_NOT_T4_CC75")
    free,total=torch.cuda.mem_get_info(0)
    disk=shutil.disk_usage("/content").free
    check(free>=11*GIB and total>=12*GIB,"GPU_FREE_LESS_THAN_11_GIB")
    check(disk>=12*GIB,"DISK_FREE_LESS_THAN_12_GIB")
    return torch,{"python":platform.python_version(),"python_executable":sys.executable,
      "torch":torch.__version__,"packages":versions,"gpu_name":name,"cc":list(cc),
      "gpu_free_bytes":free,"gpu_total_bytes":total,"disk_free_bytes":disk}

def vector_sha(t,torch):
    values=t.detach().float().cpu().tolist()
    check(len(values)==2048,"VECTOR_DIMENSION_NOT_2048")
    raw=struct.pack("<"+"f"*len(values),*values)
    return hashlib.sha256(raw).hexdigest()

def technical_smoke(torch,record):
    os.environ["HF_HOME"]=str(ROOT/"hf_home")
    os.environ["HF_HUB_CACHE"]=str(ROOT/"hf_home"/"hub")
    os.environ["HF_HUB_DISABLE_TELEMETRY"]="1"
    from huggingface_hub import snapshot_download
    from transformers import AutoTokenizer,AutoModelForCausalLM
    location=Path(snapshot_download(repo_id=MODEL,revision=REV,
                   allow_patterns=FILES,local_dir=str(ROOT/"model"),max_workers=1))
    hashes={}
    for filename in FILES:
        file=location/filename
        check(file.is_file() and not file.is_symlink(),"MISSING_OR_LINK_FILE:"+filename)
        hashes[filename]=file_sha(file)
    record["file_sha256"]=hashes
    for name,expected in WEIGHTS.items():
        check(hashes[name]==expected,"WEIGHT_HASH_MISMATCH:"+name)
    config=json.loads((location/"config.json").read_text(encoding="utf-8"))
    check((config.get("model_type"),config.get("hidden_size"),
           config.get("num_hidden_layers"),config.get("vocab_size"))
          ==("qwen3",2048,28,151936),"CONFIG_CONTRACT_MISMATCH")
    index=json.loads((location/"model.safetensors.index.json").read_text(encoding="utf-8"))
    shard_names=set(index.get("weight_map",{}).values())
    check(shard_names==set(WEIGHTS),"UNEXPECTED_WEIGHT_INDEX_SHARDS")
    record["both_weight_shards_verified_before_load"]=True
    torch.manual_seed(20261109)
    torch.cuda.manual_seed_all(20261109)
    torch.cuda.reset_peak_memory_stats(0)
    tokenizer=AutoTokenizer.from_pretrained(str(location),local_files_only=True,trust_remote_code=False)
    model=AutoModelForCausalLM.from_pretrained(str(location),dtype=torch.float16,
             local_files_only=True,trust_remote_code=False).to("cuda:0").eval()
    check(not model.training,"MODEL_NOT_IN_EVAL")
    inputs=tokenizer("a0 a1 a2 a3 a4 a5 a6 a7 a8 a9.",
                     return_tensors="pt",add_special_tokens=False)
    ids=inputs["input_ids"].to("cuda:0")
    attention=inputs["attention_mask"].to("cuda:0")
    seq=int(ids.shape[1])
    check(4<=seq<=64,"SYNTHETIC_TOKEN_LENGTH_OUT_OF_BOUNDS")
    hashes_twice=[]
    with torch.inference_mode():
        for _ in range(2):
            result=model(input_ids=ids,attention_mask=attention,return_dict=True,
                         output_hidden_states=True,use_cache=False)
            hs=result.hidden_states
            check(hs is not None and len(hs)==29,"EXPECTED_29_HIDDEN_STATES")
            check(tuple(result.logits.shape)==(1,seq,151936),"LOGITS_SHAPE_MISMATCH")
            check(bool(torch.isfinite(result.logits).all().item()),"NONFINITE_LOGITS")
            selected={}
            for i,hidden in enumerate(hs):
                check(tuple(hidden.shape)==(1,seq,2048),"HIDDEN_SHAPE_MISMATCH_"+str(i))
                check(bool(torch.isfinite(hidden).all().item()),"NONFINITE_HIDDEN_"+str(i))
                if i in (0,14,28):
                    selected[str(i)]=vector_sha(hidden[0,seq-1,:],torch)
            hashes_twice.append(selected)
            del result,hs
    check(hashes_twice[0]==hashes_twice[1],"REPEATED_FORWARD_HASH_MISMATCH")
    peak=int(torch.cuda.max_memory_reserved(0))
    check(peak<=12*GIB,"GPU_PEAK_EXCEEDS_12_GIB")
    record.update({"hidden_state_count":29,"shape":[1,seq,2048],
       "selected_layer_hashes":hashes_twice[0],"repeatability":"SAME_RUNTIME_EXACT_F32_HASH",
       "max_gpu_reserved_bytes":peak,"training":False,"science_executed":False})

def main():
    parser=argparse.ArgumentParser()
    parser.add_argument("--phase",choices=["preflight","smoke"],required=True)
    args=parser.parse_args()
    try:
        is_colab=Path("/content").is_dir() and importlib.util.find_spec("google.colab") is not None
    except (ImportError,ValueError,ModuleNotFoundError):
        is_colab=False
    if not is_colab:
        print("G1_TARGET17_STATUS=STOP_FAIL_CLOSED")
        print("G1_TARGET17_REASON=GOOGLE_COLAB_REQUIRED_NO_WRITES")
        return 1
    ROOT.mkdir(parents=True,exist_ok=True)
    receipt={"schema":"ttm_six_g1_target17_technical_v1","phase":args.phase,
       "model":MODEL,"revision":REV,"expected_weight_sha256":WEIGHTS,
       "science_executed":False,"status":"STOP",
       "observed_python":platform.python_version(),
       "observed_python_executable":sys.executable}
    result=1
    try:
        torch,env=preflight()
        receipt["environment"]=env
        if args.phase=="smoke":
            technical_smoke(torch,receipt)
        receipt["status"]="PASS_PREFLIGHT_ONLY" if args.phase=="preflight" else "PASS_TECHNICAL_ONLY"
        result=0
    except Exception as exc:
        receipt.update({"status":"STOP_FAIL_CLOSED","error_type":type(exc).__name__,
          "error":str(exc)[:900],"traceback_tail":traceback.format_exc(limit=4)[-1800:]})
    dest=ROOT/("G1_TARGET17_"+args.phase.upper()+"_RECEIPT.json")
    dest.write_text(json.dumps(receipt,sort_keys=True,indent=2)+"\n",encoding="utf-8")
    print("G1_TARGET17_STATUS="+receipt["status"])
    print("G1_TARGET17_RECEIPT="+str(dest))
    if result: print("G1_TARGET17_ERROR="+receipt.get("error","UNKNOWN"))
    return result

if __name__=="__main__":
    raise SystemExit(main())
