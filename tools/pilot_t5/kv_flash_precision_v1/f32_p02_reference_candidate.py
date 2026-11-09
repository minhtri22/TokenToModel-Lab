#!/usr/bin/env python3
"""Candidate CPU F32 P02 reference for the NEW synthetic IDs only.

No training, no TEST, no old 8 fixtures. Requires original T4 step1024
checkpoint and original P02 blob with exact SHA, then prints a new JSONL.
This is a staged candidate, not an authorization to execute.
"""
from __future__ import annotations
import argparse
import hashlib
import importlib.util
import json
import math
from pathlib import Path
import sys

P02_BLOB="9762343e06cf800b50574c2871ae1ed58537fb18"
CKPT_SHA="cb985751795c8328ad65acf7ca4c1033ce35182c1bfbdb8c38550de629cb271b"
PREREG_SCHEMA="ttm.t5.f32_kv_flash_single_synthetic_discrimination.prereg.v1"

def sha256(path:Path)->str:
    h=hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda:handle.read(1048576),b""):
            h.update(chunk)
    return h.hexdigest()

def git_blob(path:Path)->str:
    data=path.read_bytes()
    return hashlib.sha1(b"blob "+str(len(data)).encode()+b"\\0"+data).hexdigest()

def assert_inside(root:Path,path:Path)->Path:
    resolved=path.resolve(strict=True)
    if not resolved.is_relative_to(root):raise ValueError("INPUT_OUTSIDE_PROJECT")
    return resolved

def main():
    ap=argparse.ArgumentParser()
    ap.add_argument("--project-root",type=Path,required=True)
    ap.add_argument("--checkpoint",type=Path,required=True)
    ap.add_argument("--prereg",type=Path,required=True)
    ap.add_argument("--output",type=Path,required=True)
    args=ap.parse_args()
    root=args.project_root.resolve(strict=True)
    if not (root/".git").exists():raise ValueError("NOT_GIT_WORKTREE")
    p02=assert_inside(root,root/"src/p02/transformer_core.py")
    checkpoint=assert_inside(root,args.checkpoint)
    prereg_path=assert_inside(root,args.prereg)
    output_parent=assert_inside(root,args.output.parent)
    output=output_parent/args.output.name
    if output.exists():raise FileExistsError("REF_OUTPUT_ALREADY_EXISTS")
    if git_blob(p02)!=P02_BLOB or sha256(checkpoint)!=CKPT_SHA:
        raise ValueError("ORIGINAL_P02_OR_CHECKPOINT_PIN_MISMATCH")
    data=json.loads(prereg_path.read_text(encoding="utf-8"))
    if data.get("schema")!=PREREG_SCHEMA or data["control_design"]["expected_runs"]!=32:
        raise ValueError("NOT_FROZEN_NEW_FIXTURE_PLAN")
    import torch
    torch.set_num_threads(1)
    torch.set_num_interop_threads(1)
    torch.use_deterministic_algorithms(True)
    spec=importlib.util.spec_from_file_location("ttm_p02_frozen",p02)
    mod=importlib.util.module_from_spec(spec)
    sys.modules[spec.name]=mod
    assert spec.loader is not None
    spec.loader.exec_module(mod)
    cfg=mod.P02Config(vocab_size=2048,max_seq_len=256,n_embd=256,n_layer=4,n_head=4,norm_type="layernorm")
    model=mod.GPT(cfg).eval().float()
    payload=torch.load(checkpoint,map_location="cpu",weights_only=True)
    if payload.get("schema")!="ttm.t4.science.checkpoint.v1" or payload.get("step")!=1024:
        raise ValueError("WRONG_CHECKPOINT_SCHEMA_OR_STEP")
    if payload.get("p02_git_blob")!=P02_BLOB:
        raise ValueError("CHECKPOINT_ARCH_PIN_MISMATCH")
    model.load_state_dict(payload["model"],strict=True)
    if sum(p.numel() for p in model.parameters())!=3749376:
        raise ValueError("WRONG_MODEL_SIZE")
    rows=[]
    with torch.no_grad():
        for f in data["control_design"]["new_fixtures"]:
            ids=f["ids"]
            if not ids or len(ids)>31 or any(x<257 or x>=2048 for x in ids):
                raise ValueError("BAD_SYNTHETIC_IDS")
            logits=model(torch.tensor([ids],dtype=torch.long))[0]
            if isinstance(logits,tuple):logits=logits[0]
            vals=logits[0,-1].float().tolist()
            if len(vals)!=2048 or not all(math.isfinite(x) for x in vals):
                raise ValueError("BAD_REFERENCE_LOGITS")
            rows.append({"fixture_id":f["fixture_id"],"token_ids":ids,"logits":vals})
    with output.open("x",encoding="utf-8",newline="\\n") as handle:
        for row in rows:
            handle.write(json.dumps(row,sort_keys=True,separators=(",",":"))+"\\n")
        handle.flush()
    print(json.dumps({"status":"REFERENCE_8_NEW_FIXTURES_COMPLETE","output":str(output),
                      "sha256":sha256(output),"n":len(rows),"torch":torch.__version__,
                      "checkpoint_original_unmodified":True,"training":False,"test":False},sort_keys=True))

if __name__=="__main__":
    try:main()
    except Exception as exc:
        print("TTM_T5_REFERENCE_FAIL_CLOSED:"+str(exc),file=sys.stderr)
        raise SystemExit(2)
