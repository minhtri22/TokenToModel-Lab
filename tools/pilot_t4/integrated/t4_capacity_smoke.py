#!/usr/bin/env python3
"""Zero-science TTM T4 capacity benchmark: exact P02 and 4096 scored targets/step.

No TinyStories, no TEST or model training. Does not authorize science.
Separate single-run no-overwrite report, calibrated overhead reserve.
"""
from __future__ import annotations
import argparse, hashlib, importlib.util, json, math, os, random, sys, time
from pathlib import Path

import torch
from torch.nn import functional as F

CONFIG=dict(vocab_size=2048,max_seq_len=256,n_embd=256,n_layer=4,n_head=4,norm_type='layernorm')
P02_BLOB='9762343e06cf800b50574c2871ae1ed58537fb18'
SEED=20261108
TOTAL_STEPS=1024
TOKENS_PER_STEP=4096
TIME_CAP_SECONDS=5400
# 20% of total time reserved for data moves, evals, checkpoints, session variability.
RESERVE_FRACTION=0.25
VRAM_FRACTION_CAP=0.80


def sha_file(p):
    h=hashlib.sha256()
    with Path(p).open('rb') as f:
        for data in iter(lambda:f.read(1<<20),b''):h.update(data)
    return h.hexdigest()


def p02_module(path):
    p=Path(path)
    b=p.read_bytes()
    sha1=hashlib.sha1(b'blob '+str(len(b)).encode('ascii')+b'\0'+b).hexdigest()
    if sha1!=P02_BLOB:raise RuntimeError('WRONG_P02_GIT_BLOB:'+sha1)
    spec=importlib.util.spec_from_file_location('t4_p02_exact',p)
    mod=importlib.util.module_from_spec(spec)
    sys.modules[spec.name]=mod
    spec.loader.exec_module(mod)
    return mod


def device_setup():
    if not torch.cuda.is_available():raise RuntimeError('T4_CAPACITY_CUDA_REQUIRED_NO_CPU_SUBSTITUTE')
    gpu=torch.cuda.get_device_properties(0)
    torch.set_num_threads(2)
    return gpu


def amp_scaler(mode):
    if mode=='fp16':return torch.amp.GradScaler('cuda',enabled=True)
    return None


def single_trial(mod,*,microbatch:int,precision:str,warmup:int,timed:int):
    assert microbatch in (1,2,4,8)
    assert (TOKENS_PER_STEP//256)%microbatch==0
    assert precision in ('fp32','fp16')
    torch.manual_seed(SEED)
    torch.cuda.manual_seed_all(SEED)
    random.seed(SEED)
    model=mod.GPT(mod.P02Config(**CONFIG)).cuda()
    if sum(p.numel() for p in model.parameters())!=3749376:raise RuntimeError('P02_PARAMETERS_CHANGED')
    opt=torch.optim.AdamW(model.parameters(),lr=3e-4,betas=(.9,.95),weight_decay=.1)
    scaler=amp_scaler(precision)
    generator=torch.Generator(device='cpu').manual_seed(SEED+101)
    accum=(TOKENS_PER_STEP//256)//microbatch
    peak_alloc=[];elapsed=[];loss_last=None
    torch.cuda.empty_cache()
    torch.cuda.reset_peak_memory_stats()
    model.train()
    for step in range(warmup+timed):
        torch.cuda.synchronize();before=time.perf_counter()
        opt.zero_grad(set_to_none=True)
        for _ in range(accum):
            # EXACT 4096 next-token scored targets, independent synthetic token IDs.
            ids=torch.randint(0,2048,(microbatch,257),dtype=torch.long,generator=generator)
            x,y=ids[:,:-1].to('cuda',non_blocking=False),ids[:,1:].to('cuda',non_blocking=False)
            with torch.autocast(device_type='cuda',dtype=torch.float16,enabled=(precision=='fp16')):
                logits,_=model(x)
                loss=F.cross_entropy(logits.reshape(-1,2048).float(),y.reshape(-1),reduction='sum')/TOKENS_PER_STEP
            if not torch.isfinite(loss).item():raise RuntimeError('NONFINITE_BENCHMARK_LOSS')
            if scaler:scaler.scale(loss).backward()
            else:loss.backward()
            loss_last=float(loss.detach())
        if scaler:
            scaler.unscale_(opt)
            torch.nn.utils.clip_grad_norm_(model.parameters(),1.0)
            scale_before=scaler.get_scale()
            scaler.step(opt);scaler.update()
            if scaler.get_scale()<scale_before:raise RuntimeError('FP16_GRADIENT_OVERFLOW_NOT_CAPACITY_PASS')
        else:
            torch.nn.utils.clip_grad_norm_(model.parameters(),1.0)
            opt.step()
        torch.cuda.synchronize()
        sec=time.perf_counter()-before
        if step>=warmup:
            elapsed.append(sec)
            peak_alloc.append(torch.cuda.max_memory_reserved())
    del model,opt,scaler
    torch.cuda.synchronize()
    return {
       'microbatch_windows':microbatch,'context':256,'precision':precision,
       'gradient_accumulation':accum,'scored_target_tokens_per_optimizer_step':TOKENS_PER_STEP,
       'warmup_steps':warmup,'timed_steps':timed,
       'sample_seconds':[round(x,5) for x in elapsed],
       'median_seconds':sorted(elapsed)[len(elapsed)//2] if len(elapsed)%2 else (sorted(elapsed)[len(elapsed)//2-1]+sorted(elapsed)[len(elapsed)//2])/2,
       'worst_seconds':max(elapsed),'peak_cuda_reserved_bytes':max(peak_alloc),
       'last_synthetic_loss':loss_last,
    }


def candidate_decision(measurements,bytes_total):
    for m in measurements:
        # Conservative max step wall clock, including optimizer and 4096 scored targets.
        m['projected_science_seconds_with_25pct_reserved']=round(TOTAL_STEPS*m['worst_seconds']/(1-RESERVE_FRACTION),2)
        m['memory_reserved_ratio']=m['peak_cuda_reserved_bytes']/bytes_total
        m['feasible_on_measured_smoke']=bool(m['projected_science_seconds_with_25pct_reserved']<=TIME_CAP_SECONDS and m['memory_reserved_ratio']<=VRAM_FRACTION_CAP)
    eligible=[m for m in measurements if m['feasible_on_measured_smoke']]
    if not eligible:return None
    # Maximum margin, choose fastest measured worst case; tie by smaller memory and microbatch.
    return min(eligible,key=lambda x:(x['worst_seconds'],x['peak_cuda_reserved_bytes'],x['microbatch_windows']))


def main():
    ap=argparse.ArgumentParser()
    ap.add_argument('--p02',required=True)
    ap.add_argument('--out',required=True)
    ap.add_argument('--warmup',type=int,default=2)
    ap.add_argument('--timed',type=int,default=4)
    args=ap.parse_args()
    if args.warmup!=2 or args.timed!=4:raise RuntimeError('BENCH_DURATION_FROZEN')
    dst=Path(args.out)
    if dst.exists():raise FileExistsError('CAPACITY_REPORT_EXISTS_ONE_SHOT_NO_RERUN')
    if dst.parent.is_symlink():raise RuntimeError('OUT_DIR_SYMLINK')
    dst.parent.mkdir(parents=True,exist_ok=True)
    mod=p02_module(args.p02)
    gpu=device_setup()
    records=[];failures=[]
    # Fixed finite candidate order. OOM is a stopped candidate, not hidden.
    for mode,batch in [('fp32',2),('fp16',2),('fp16',4),('fp16',8)]:
        try:
            m=single_trial(mod,microbatch=batch,precision=mode,warmup=args.warmup,timed=args.timed)
            records.append(m)
            print(f'CAPACITY_CASE={mode}/mb{batch} WORST_S={m["worst_seconds"]:.3f} VRAM_GiB={m["peak_cuda_reserved_bytes"]/(1024**3):.3f}',flush=True)
        except (torch.cuda.OutOfMemoryError,RuntimeError) as e:
            failures.append({'precision':mode,'microbatch_windows':batch,'error':str(e)[:240]})
            print(f'CAPACITY_CASE_FAIL={mode}/mb{batch}: {type(e).__name__}: {str(e)[:140]}',flush=True)
            torch.cuda.empty_cache()
    selected=candidate_decision(records,gpu.total_memory)
    result={'schema':'ttm.t4.capacity.synthetic.v1','status':'PASS_PROVISIONAL_CAPACITY_ONLY' if selected else 'CAPACITY_HOLD',
       'science_executed':False,'synthetic_only':True,'gpu':gpu.name,'cuda':str(torch.version.cuda),
       'torch':str(torch.__version__),'p02_git_blob':P02_BLOB,'p02_sha256':sha_file(args.p02),
       'config':CONFIG,'unique_parameters':3749376,'steps_target':TOTAL_STEPS,'tokens_per_step':TOKENS_PER_STEP,
       'time_cap_seconds':TIME_CAP_SECONDS,'reserve_fraction':RESERVE_FRACTION,
       'vram_reserved_limit_fraction':VRAM_FRACTION_CAP,'total_device_memory_bytes':gpu.total_memory,
       'records':records,'failed_candidates':failures,
       'selected_technical_candidate':None if selected is None else {
          'precision':selected['precision'],'microbatch_windows':selected['microbatch_windows'],
          'gradient_accumulation':selected['gradient_accumulation'],
          'worst_seconds':selected['worst_seconds'],
          'projected_science_seconds_with_25pct_reserved':selected['projected_science_seconds_with_25pct_reserved']},
       'important_limitations':['only synthetic uniform 256-token windows','actual TRAIN mixture of short/long windows could require more microbatches',
          'VAL, checkpoint/Drive IO and downtime not directly measured; 25 pct reserve heuristic','provisional until independent readback and policy acceptance']}
    dst.parent.mkdir(parents=True,exist_ok=True)
    with dst.open('x',encoding='utf-8') as f:
       json.dump(result,f,indent=2,sort_keys=True);f.write('\n');f.flush();os.fsync(f.fileno())
    print('T4_CAPACITY_REPORT='+str(dst))
    print('T4_CAPACITY_RESULT='+result['status'])
    # No scientifically authorized execution in this script, even if PASS.
    if not selected:raise SystemExit(2)

if __name__=='__main__':main()
