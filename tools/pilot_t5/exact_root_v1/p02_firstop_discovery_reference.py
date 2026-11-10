#!/usr/bin/env python3
"""TTM T5 true checkpoint1024 P02 CPU discovery D01/D02 (not confirmatory).

Reads frozen prereg and checkpoint; outputs full signed named F32 tensors.
The tanh GELU branch is a one-factor diagnostic, not a root-cause claim.
Never executes C++ or any historical/new-32 fixture; never trains.
"""
from __future__ import annotations
import argparse
import hashlib
import importlib.util
import json
import math
from pathlib import Path
import sys

PREREG_BLOB="82fdd9fe716579181db648caa69170fb63d115a6"
P02_BLOB="9762343e06cf800b50574c2871ae1ed58537fb18"
CKPT_SHA="cb985751795c8328ad65acf7ca4c1033ce35182c1bfbdb8c38550de629cb271b"
CONFIG={"vocab_size":2048,"max_seq_len":256,"n_embd":256,"n_layer":4,"n_head":4,"norm_type":"layernorm"}

def sha(path):
    h=hashlib.sha256()
    with path.open("rb") as f:
        for chunk in iter(lambda:f.read(1<<20),b""):h.update(chunk)
    return h.hexdigest()

def gitblob(path):
    b=path.read_bytes()
    return hashlib.sha1(b"blob "+str(len(b)).encode()+b"\0"+b).hexdigest()

def member(root,path):
    resolved=path.resolve(strict=True)
    if not resolved.is_file() or not resolved.is_relative_to(root):
        raise ValueError("EXISTING_PROJECT_FILE_REQUIRED")
    return resolved

def dump(dst,fixture,stage,value):
    import torch
    value=value.detach().cpu().float().contiguous()
    if not torch.isfinite(value).all().item():raise ValueError("NONFINITE_STAGE:"+stage)
    shape=list(value.shape)
    if len(shape)>4:raise ValueError("STAGE_DIM_GT4")
    dst.write(json.dumps({
        "fixture_id":fixture,"stage":stage,"dtype":"F32",
        "torch_shape":shape,"values":value.reshape(-1).tolist()
    },separators=(",",":"),allow_nan=False)+"\n")

def run_one(model,ids,fixture,out):
    import torch
    from torch.nn import functional as F
    toks=torch.tensor([ids],dtype=torch.long,device="cpu")
    logits,loss=model(toks)
    if loss is not None:raise ValueError("UNEXPECTED_TRAINING_LOSS")
    positions=torch.arange(len(ids),dtype=torch.long)
    x=model.tok(toks)+model.pos(positions)[None,:,:]
    dump(out,fixture,"inpL",x.squeeze(0))
    for il,blk in enumerate(model.blocks):
        norm1=blk.ln1(x)
        if il==0:dump(out,fixture,"attn_norm-0",norm1.squeeze(0))
        qkv=blk.attn.qkv(norm1)
        if il==0:dump(out,fixture,"wqkv_b-0",qkv.squeeze(0))
        q,k,v=[blk.attn._split(z) for z in qkv.chunk(3,dim=-1)]
        if il==0:
            # GGML Qcur is token-major, then head, then head_dim.
            for stage,data in (("Qcur-0",q),("Kcur-0",k),("Vcur-0",v)):
                dump(out,fixture,stage,data.transpose(1,2).squeeze(0))
        raw_score=q @ k.transpose(-2,-1)
        score=raw_score / math.sqrt(blk.attn.head_dim)
        mask=torch.ones(len(ids),len(ids),dtype=torch.bool).tril()
        weights=score.masked_fill(~mask,-torch.inf).softmax(dim=-1)
        if il==0:
            dump(out,fixture,"kq-0",raw_score.squeeze(0))
            dump(out,fixture,"kq_soft_max-0",weights.squeeze(0))
        wv=weights@v
        if il==0:dump(out,fixture,"kqv-0",wv.squeeze(0))
        attn_out=wv.transpose(1,2).contiguous().reshape(1,len(ids),256)
        if il==0:
            dump(out,fixture,"kqv_out-0",attn_out.squeeze(0))
            v_half_rounded=v.to(torch.float16).to(torch.float32)
            alt_wv=weights @ v_half_rounded
            alt_y=alt_wv.transpose(1,2).contiguous().reshape(1,len(ids),256)
            alt_residual=x+blk.attn.proj(alt_y)
            # Original same-input V-F16 rounding mechanism, not actual GGML.
            v_precision_delta=(x+blk.attn.proj(attn_out)-alt_residual).abs()
            v_precision_max=float(v_precision_delta.max())
            v_precision_mean=float(v_precision_delta.mean())
        # Compare independent WO matmul, then fused-bias output vs GGML.
        wo_mm=F.linear(attn_out,blk.attn.proj.weight,bias=None)
        wo=blk.attn.proj(attn_out)
        if il==0:
            dump(out,fixture,"attn_wo_mm-0",wo_mm.squeeze(0))
            dump(out,fixture,"attn_wo_out-0",wo.squeeze(0))
        residual=x+wo
        if il==0:dump(out,fixture,"ffn_inp-0",residual.squeeze(0))
        norm2=blk.ln2(residual)
        up=blk.mlp[0](norm2)
        act=blk.mlp[1](up)
        down=blk.mlp[2](act)
        if il==0:
            dump(out,fixture,"ffn_norm-0",norm2.squeeze(0))
            dump(out,fixture,"ffn_up_b-0",up.squeeze(0))
            dump(out,fixture,"ffn_gelu-0",act.squeeze(0))
            dump(out,fixture,"ffn_out-0",down.squeeze(0))
            dump(out,fixture,"ffn_gelu_tanh_same_input-0",F.gelu(up,approximate="tanh").squeeze(0))
        x=residual+down
    manual=model.head(model.final_ln(x))[:,-1,:]
    baseline=logits[:,-1,:]
    if not torch.equal(manual,baseline):
        raise ValueError("MANUAL_P02_FORWARD_NOT_BITWISE_IDENTICAL")
    dump(out,fixture,"result_norm",model.final_ln(x)[:,-1,:])
    dump(out,fixture,"result_output",baseline)
    # Switch solely GELU functional approximation, keep all weights untouched.
    approximations=[blk.mlp[1].approximate for blk in model.blocks]
    try:
        for blk in model.blocks:blk.mlp[1].approximate="tanh"
        corrected,_=model(toks)
    finally:
        for blk,orig in zip(model.blocks,approximations):
            blk.mlp[1].approximate=orig
    corrected=corrected[:,-1,:]
    dump(out,fixture,"result_output_gelu_tanh_allblocks",corrected)
    diff=(baseline-corrected).abs()
    return {"fixture_id":fixture,"n_ids":len(ids),"gelu_tanh_vs_erf_max_abs":float(diff.max()),"gelu_tanh_vs_erf_mean_abs":float(diff.mean()),"top1_equal":bool(torch.argmax(baseline)==torch.argmax(corrected)), "block0_v_to_f16_then_f32_ffn_inp_max_abs":v_precision_max,"block0_v_to_f16_then_f32_ffn_inp_mean_abs":v_precision_mean,"actual_p02_erf_baseline":True}

def main():
    ap=argparse.ArgumentParser()
    ap.add_argument("--project-root",type=Path,required=True)
    ap.add_argument("--worktree",type=Path,required=True)
    ap.add_argument("--checkpoint",type=Path,required=True)
    ap.add_argument("--output",type=Path,required=True)
    args=ap.parse_args()
    root=args.project_root.resolve(strict=True)
    work=args.worktree.resolve(strict=True)
    if not work.is_relative_to(root):raise ValueError("WORKTREE_OUTSIDE_PROJECT")
    source=member(root,work/"src/p02/transformer_core.py")
    prereg=member(root,work/"artifacts/qa/ttm-t5-parity/TTM_T5_EXACT_FIRST_OP_NEW_FIXTURES_INTEGRATED_PREREG_20261110.json")
    checkpoint=member(root,args.checkpoint)
    if (gitblob(source)!=P02_BLOB or gitblob(prereg)!=PREREG_BLOB
        or sha(checkpoint)!=CKPT_SHA):
        raise ValueError("SOURCE_OR_CHECKPOINT_PIN_FAIL")
    plan=json.loads(prereg.read_text(encoding="utf-8"))
    candidates=[x for x in plan["fixtures"] if x["partition"]=="discovery"]
    if [(x["fixture_id"],len(x["token_ids"])) for x in candidates]!=[("D01",1),("D02",5)]:
        raise ValueError("DISCOVERY_FIXTURE_SET_CHANGED")
    output=args.output.resolve(strict=False)
    if output.parent.resolve(strict=True).is_relative_to(root) is False:
        raise ValueError("OUTPUT_OUTSIDE_PROJECT")
    if output.exists():raise FileExistsError("REFERENCE_EXISTS_NO_OVERWRITE")
    import torch
    if torch.cuda.is_available():
        # CPU enforced regardless of CUDA availability.
        pass
    torch.set_num_threads(1)
    if torch.get_default_dtype()!=torch.float32:torch.set_default_dtype(torch.float32)
    spec=importlib.util.spec_from_file_location("ttm_p02_firstop_real",source)
    if spec is None or spec.loader is None:raise ValueError("P02_IMPORT_SPEC_FAILED")
    module=importlib.util.module_from_spec(spec)
    sys.modules[spec.name]=module
    spec.loader.exec_module(module)
    payload=torch.load(checkpoint,map_location="cpu",weights_only=True)
    if (payload["schema"]!="ttm.t4.science.checkpoint.v1"
        or payload["step"]!=1024 or payload["config"]!=CONFIG
        or payload["p02_git_blob"]!=P02_BLOB):
        raise ValueError("CHECKPOINT_META_NOT_FROZEN")
    model=module.GPT(module.P02Config(**CONFIG)).float().cpu().eval()
    model.load_state_dict(payload["model"],strict=True)
    if sum(p.numel() for p in model.parameters())!=3749376:
        raise ValueError("PARAM_COUNT_CHANGED")
    summaries=[]
    with torch.inference_mode(),output.open("x",encoding="utf-8",newline="\n") as stream:
        for case in candidates:
            print("CPU_DISCOVERY_REFERENCE="+case["fixture_id"],flush=True)
            summaries.append(run_one(model,case["token_ids"],case["fixture_id"],stream))
    print(json.dumps({"status":"PASS_TWO_REAL_CPU_DISCOVERY_REFERENCES",
      "checkpoint_sha256":CKPT_SHA,"prereg_git_blob":PREREG_BLOB,
      "reference_sha256":sha(output),"summary":summaries,
      "no_confirmatory_executed":True,"training":False,"test":False},
      sort_keys=True))

if __name__=="__main__":
    try:main()
    except (ValueError,KeyError,TypeError,OSError,RuntimeError) as exc:
        print("TTM_T5_REFERENCE_FAIL_CLOSED:"+str(exc),file=sys.stderr)
        raise SystemExit(2)
