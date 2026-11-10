#!/usr/bin/env python3
"""TTM T5 isolated source copies (original unmodified) to localize first op.

Two new Git worktrees INSIDE TTM project only, from exact llama.cpp commit:
A: trace-only callback inserted in KV attention projection, no math edit.
B: same trace callback + one GPT2 GELU to GELU_ERF choice.
No native inference, no model/checkpoint/GGUF access. No merge, no reset,
no overwrites, no worktree cleanup. Owner checks output evidence before build.
"""
from __future__ import annotations
import argparse
import hashlib
import json
from pathlib import Path
import subprocess
import sys

PIN_LLAMA="372dc5ca157276beb6c67b2e92477e8d662e964a"
PIN_GPT2_BLOB="711a148a28bd1aa2c1dccf2e3b21803aac4a4185"
PIN_GRAPH_BLOB="9f99ba83e4d7aff29ec82c74f605df913144a021"
STAGE_REL="_tmp/ttm_t5_exact_root_v1_20261110"
VENDOR_REL="_tmp/ttm_t2/llama.cpp"
GPT2="src/models/gpt2.cpp"
GRAPH="src/llama-graph.cpp"
KV_END_ANCHOR="static std::unique_ptr<llm_graph_input_attn_k> build_attn_inp_k_impl("
# The following block is unique immediately before build_attn_inp_k:
WO_END="""    if (wo_b) {
        cur = ggml_add(ctx0, cur, wo_b);
    }

    return cur;
}

"""
WO_REPLACEMENT="""    // TTM independent numeric probe; no mathematical changes.
    cb(cur, "attn_wo_mm", il);
    if (wo_b) {
        cur = ggml_add(ctx0, cur, wo_b);
    }
    cb(cur, "attn_wo_out", il);

    return cur;
}

"""

def blob(b:bytes)->str:
    return hashlib.sha1(b"blob "+str(len(b)).encode()+b"\\0"+b).hexdigest()

def sha_file(p:Path)->str:
    return hashlib.sha256(p.read_bytes()).hexdigest()

def run(args,cwd,seconds=40):
    x=subprocess.run([str(i) for i in args],cwd=str(cwd),
        capture_output=True,text=True,timeout=seconds,check=False)
    if x.returncode:
        raise RuntimeError("COMMAND_FAILED_"+str(x.returncode)+":"+x.stderr[:450])
    return x.stdout.strip()

def under(root,p):
    x=p.resolve(strict=True)
    if not x.is_relative_to(root):raise ValueError("OUTSIDE_TTM_PROJECT")
    return x

def main():
    ap=argparse.ArgumentParser()
    ap.add_argument("--project-root",type=Path,required=True)
    args=ap.parse_args()
    root=args.project_root.resolve(strict=True)
    upstream=under(root,root/VENDOR_REL)
    if not (upstream/".git").exists():raise ValueError("VENDOR_GIT_MISSING")
    if run(["git.exe","rev-parse","HEAD"],upstream)!=PIN_LLAMA:
        raise ValueError("VENDOR_HEAD_NOT_PINNED")
    source_items={}
    for p,expected in ((GPT2,PIN_GPT2_BLOB),(GRAPH,PIN_GRAPH_BLOB)):
        b=(upstream/p).read_bytes()
        if blob(b)!=expected:raise ValueError("ORIGINAL_LLAMA_SOURCE_GIT_BLOB_MISMATCH:"+p)
        source_items[p]=b
    dest=root/STAGE_REL
    if dest.exists():raise FileExistsError("EXACT_ROOT_STAGE_ALREADY_EXISTS_NO_REPEAT")
    dest.mkdir(parents=True,exist_ok=False)
    receipt={"schema":"ttm.t5.exact_root.source_isolation.v1",
        "status":"HOLD_PREPARATION_STARTED",
        "pinned_llama_commit":PIN_LLAMA,
        "original_blobs":{GPT2:PIN_GPT2_BLOB,GRAPH:PIN_GRAPH_BLOB},
        "science_executed":False,"test_accessed":False,"training":False,
        "old_native_32_reused":False,"main_unchanged":True}
    try:
        for label,gelu in (("trace_only",False),("trace_gelu_erf",True)):
            tree=dest/label
            run(["git.exe","-C",str(upstream),"worktree","add","--detach",str(tree),PIN_LLAMA],
                root,seconds=100)
            tree=under(root,tree)
            graph=tree/GRAPH
            g=graph.read_text("utf-8")
            index=g.index(KV_END_ANCHOR)
            prefix,suffix=g[:index],g[index:]
            if prefix.count(WO_END)!=2:
                # First occurrence is no-cache, second is KV; replace the LAST
                # occurrence only to keep all non-KV paths unchanged.
                raise ValueError("KV_WO_SOURCE_STRUCTURAL_ANCHOR_CHANGED")
            pos=prefix.rfind(WO_END)
            patched=prefix[:pos]+WO_REPLACEMENT+prefix[pos+len(WO_END):]+suffix
            if patched.count('cb(cur, "attn_wo_mm", il)')!=1:
                raise ValueError("TRACE_PATCH_COUNT_BAD")
            graph.write_text(patched,"utf-8",newline="\\n")
            if gelu:
                p=tree/GPT2
                g=p.read_text("utf-8")
                anchor="LLM_FFN_GELU, LLM_FFN_SEQ, il);"
                if g.count(anchor)!=1:raise ValueError("GPT2_GELU_ANCHOR_CHANGED")
                p.write_text(g.replace(anchor,"LLM_FFN_GELU_ERF, LLM_FFN_SEQ, il);"),"utf-8",newline="\\n")
            current_gpt2=tree/GPT2
            current_graph=tree/GRAPH
            receipt[label]={"source_root":str(tree),
                "gpt2_git_blob":blob(current_gpt2.read_bytes()),
                "graph_git_blob":blob(current_graph.read_bytes()),
                "gpt2_sha256":sha_file(current_gpt2),
                "graph_sha256":sha_file(current_graph),
                "trace_callbacks":["attn_wo_mm","attn_wo_out"],
                "gpt2_activation":"GELU_ERF" if gelu else "GELU_ORIGINAL",
                "other_source_files_unmodified":"PINNED_GIT_WORKTREE"}
        receipt["status"]="PASS_TWO_ISOLATED_SOURCE_VARIANTS_READY_FOR_BUILD"
    except Exception as exc:
        receipt["status"]="HOLD_SOURCE_PREP_PARTIAL_NO_RETRY"
        receipt["failure"]=type(exc).__name__+":"+str(exc)
    finally:
        output=dest/"SOURCE_ISOLATION_RECEIPT.json"
        with output.open("x",encoding="utf-8",newline="\\n") as f:
            json.dump(receipt,f,ensure_ascii=False,sort_keys=True,indent=2)
            f.write("\\n")
        print("SOURCE_ISOLATION_STATUS="+receipt["status"],flush=True)
        print("SOURCE_ISOLATION_RECEIPT="+str(output),flush=True)
        print("SOURCE_ISOLATION_SHA256="+sha_file(output),flush=True)
    if receipt["status"]!="PASS_TWO_ISOLATED_SOURCE_VARIANTS_READY_FOR_BUILD":
        raise SystemExit(2)

if __name__=="__main__":
    try:main()
    except Exception as exc:
        print("TTM_T5_SOURCE_PREP_FAIL_CLOSED:"+repr(exc),file=sys.stderr)
        raise SystemExit(3)
