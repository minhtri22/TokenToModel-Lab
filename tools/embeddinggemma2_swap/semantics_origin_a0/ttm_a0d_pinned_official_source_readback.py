#!/usr/bin/env python3
"""One integrated, fail-closed A0D readback. NO pretrained weights, training or forward.
Accepts only existing pinned donor files (never fetches); T1 mapping optional only
for public CI, mandatory for OWNER_T4 admission. --cpu-init uses official HF class.
"""
from __future__ import annotations
import argparse, contextlib, hashlib, json, pathlib, sys
REV="f9972ac22e696a105c482202646979e33e4b5a1e"
PINS={
 "config.json":"b8f1e9931b57fbc054acdb445c41765d55b0074c58d145fa82839941ad1b5bb3",
 "tokenizer.json":"4d777ef5bdc1aa36227abdfb77c3e49e7b9c892d16e1b6bda41c393504828be4",
 "tokenizer_config.json":"17bd5d6e9364ca49a534e1502076593317c298d4a663623091ed45388f004874"}
T1="cba18e60cee3d08a353ee6d4a451017289e45af7b4b1179c87171b9b78d7dfdc"
T1_INTERNAL="6da22cf79c3a6cfd08d80a768eb1074125a753164ccf62a164e79545956e94c6"
class HOLD(Exception):pass
def need(p,label):
 if not p:raise HOLD(label)
def sha(path):
 h=hashlib.sha256()
 with open(path,"rb") as f:
  for b in iter(lambda:f.read(4*1024*1024),b""):h.update(b)
 return h.hexdigest()
def byte_inv():
 bs=list(range(33,127))+list(range(161,173))+list(range(174,256));cs=bs.copy();n=0
 for b in range(256):
  if b not in bs:bs.append(b);cs.append(256+n);n+=1
 return {v:k for k,v in zip(bs,map(chr,cs))}
def mapping(t1,tok):
 p=pathlib.Path(t1)
 need(p.is_file() and sha(p)==T1,"T1_FILE_PIN")
 m=json.loads(p.read_bytes());x=dict(m);claim=x.pop("manifest_sha256",None)
 need(claim==T1_INTERNAL and hashlib.sha256(json.dumps(x,ensure_ascii=False,sort_keys=True,separators=(",",":")).encode()).hexdigest()==T1_INTERNAL,"T1_INTERNAL_PIN")
 ts=m["tokens"];need(len(ts)==2048 and m["eos_id"]==256 and ts[256]=="<|endoftext|>","T1_SCHEMA")
 inv=byte_inv();special=set(tok.all_special_ids)
 c={"mapped":0,"multi_id_mapped":0,"incomplete_utf8":0,"empty_or_special":0,"unmapped_or_invalid_donor_ids":0}
 for i,piece in enumerate(ts):
  if i==256:c["empty_or_special"]+=1;continue
  try: s=bytes(inv[ch] for ch in piece).decode("utf8","strict")
  except (UnicodeDecodeError,KeyError):c["incomplete_utf8"]+=1;continue
  if not s:c["empty_or_special"]+=1;continue
  ids=tok.encode(s,add_special_tokens=False)
  if not isinstance(ids,list) or not ids or any(type(k)!=int or k<0 or k>=262144 or k in special for k in ids):
   c["unmapped_or_invalid_donor_ids"]+=1;continue
  c["mapped"]+=1
  if len(ids)>1:c["multi_id_mapped"]+=1
 need(sum(v for k,v in c.items() if k!="multi_id_mapped")==2048,"T1_TOTAL")
 need(c=={"mapped":1917,"multi_id_mapped":50,"incomplete_utf8":130,"empty_or_special":1,"unmapped_or_invalid_donor_ids":0},"HISTORIC_DONOR_MAPPING_MISMATCH")
 return c
def audit(args):
 root=pathlib.Path(args.source_dir)
 need(root.is_dir(),"DONOR_DIRECTORY")
 files={}
 for n,d in PINS.items():
  p=root/n;need(p.is_file(),"DONOR_MISSING_"+n)
  digest=sha(p);need(digest==d,"DONOR_SHA256_"+n)
  files[n]={"sha256":digest,"size":p.stat().st_size}
 doc=json.loads((root/"config.json").read_bytes());cfg=doc.get("text_config")
 need(isinstance(cfg,dict) and cfg.get("vocab_size")==262144 and cfg.get("hidden_size")==512 and cfg.get("num_hidden_layers")==24,"DONOR_CONFIG")
 try:
  import torch,transformers
  from transformers import AutoTokenizer,EmbeddingGemma2TextConfig,EmbeddingGemma2TextModel
 except Exception as e:raise HOLD("OFFICIAL_CLASS_IMPORT_"+type(e).__name__) from e
 need(EmbeddingGemma2TextModel.__module__.startswith("transformers.models.embedding_gemma2."),"OFFICIAL_CLASS_MODULE")
 config=EmbeddingGemma2TextConfig(**cfg)
 torch.set_num_threads(min(torch.get_num_threads(),2))
 if args.cpu_init:torch.manual_seed(2026111194)
 with (contextlib.nullcontext() if args.cpu_init else torch.device("meta")):
  model=EmbeddingGemma2TextModel(config)
 need(len(model.layers)==24 and list(model.embed_tokens.weight.shape)==[262144,512],"OFFICIAL_ARCH")
 need(list(model.embedding_projection.weight.shape)==[768,512],"OFFICIAL_OUTPUT_PROJECTION")
 params=sum(p.numel() for p in model.parameters())
 need(250_000_000<params<300_000_000,"OFFICIAL_PARAM_RANGE")
 state=sorted((name,list(t.shape),str(t.dtype)) for name,t in model.state_dict().items())
 h=hashlib.sha256(json.dumps(state,sort_keys=True,separators=(",",":")).encode()).hexdigest()
 if args.cpu_init:
  need(not any(p.is_meta for p in model.parameters()),"NOT_CPU")
  need(bool(torch.isfinite(model.embed_tokens.weight[1:10]).all()),"INIT_NONFINITE")
  need(bool(torch.count_nonzero(model.embed_tokens.weight[0])==0),"PAD_NONZERO")
 del model
 tok=AutoTokenizer.from_pretrained(str(root),local_files_only=True,trust_remote_code=False)
 counts=mapping(args.t1,tok) if args.t1 else None
 return {"schema":"ttm.gemma2.owner_pinned_official_readback.v1","status":"PASS_OFFICIAL_CLASS_AND_SOURCE"+("_T1_MAPPING" if counts else "_NO_T1_MAPPING"),
  "revision":REV,"pinned_files":files,"transformers_version":transformers.__version__,
  "torch_version":torch.__version__,"python_version":sys.version.split()[0],
  "official_class":EmbeddingGemma2TextModel.__module__,
  "instantiation":"CPU_NO_FORWARD" if args.cpu_init else "META_NO_FORWARD",
  "parameter_count":params,"state_tensor_count":len(state),"state_name_shape_dtype_sha256":h,
  "tokenizer_class":type(tok).__name__,"T1_mapping":counts,
  "training":False,"model_forward":False,"checkpoint_written":False,"OOD256_rescore":False}
def main():
 ap=argparse.ArgumentParser()
 ap.add_argument("--source-dir",required=True)
 ap.add_argument("--t1")
 ap.add_argument("--cpu-init",action="store_true")
 a=ap.parse_args()
 try: print(json.dumps(audit(a),sort_keys=True))
 except Exception as e:
  code=str(e) if isinstance(e,HOLD) else "UNEXPECTED_"+type(e).__name__
  print(json.dumps({"status":"HOLD_FAIL_CLOSED","gate":code,"training":False,"model_forward":False},sort_keys=True))
  sys.exit(2)
if __name__=="__main__":main()
