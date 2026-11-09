#!/usr/bin/env python3
"""TTM T4 A2 continuous 1024-step science trainer. Exact hash-pinned one-shot lock.

This code is not permission to start training. No TEST read. 4096 real targets/step,
1024 steps, frozen optimizer, VAL NLL baseline, READY-last immutable checkpoints.
"""
from __future__ import annotations
import argparse, hashlib, importlib.util, json, math, os, random, shutil, sys, time
from pathlib import Path
import numpy as np
import torch
from torch.nn import functional as F
from t4_capacity_smoke import P02_BLOB,CONFIG,TOTAL_STEPS,TOKENS_PER_STEP,p02_module,SEED
from t4_eval import load_private_pack,fit_baselines,baseline_story_scores,model_story_scores,decide_h1

CHECKPOINT_STEPS=(256,512,768,1024)
VALID_STEPS=tuple(range(128,1025,128))
TIME_POLICY='COLAB_FREE_RUN_UNTIL_1024_OR_PREEMPTED'  # No arbitrary 55/90-minute hard stop


def sha_file(p):
    h=hashlib.sha256()
    with open(p,'rb') as f:
        for b in iter(lambda:f.read(1<<20),b''):h.update(b)
    return h.hexdigest()


def json_new(p,obj):
    with Path(p).open('x',encoding='utf-8') as f:
        json.dump(obj,f,indent=2,sort_keys=True);f.write('\n');f.flush();os.fsync(f.fileno())


def require_science_lock(path,expected_sha,pack_manifest,capacity_sha,capacity_review_sha):
    if not path or not expected_sha or len(expected_sha)!=64:
        raise RuntimeError('SCIENCE_NOT_AUTHORIZED_NO_EXACT_LOCK_SHA')
    if sha_file(path)!=expected_sha:raise RuntimeError('SCIENCE_LOCK_SHA_MISMATCH')
    obj=json.loads(Path(path).read_text('utf8'))
    if obj.get('authorization')!='ONE_SHOT_T4_SCIENCE_GRANTED' or obj.get('science_seed')!=SEED:
        raise RuntimeError('SCIENCE_AUTHORIZATION_NOT_GRANTED')
    if obj.get('budget')!={'optimizer_steps':1024,'target_tokens_per_step':4096,'time_policy':TIME_POLICY}:
        raise RuntimeError('SCIENCE_BUDGET_DIFFERENT')
    if obj.get('train_pack_sha256')!=pack_manifest['npz_sha256'] or obj.get('capacity_report_sha256')!=capacity_sha or obj.get('capacity_review_sha256')!=capacity_review_sha:
        raise RuntimeError('SCIENCE_DATA_OR_CAPACITY_SHA_MISMATCH')
    if obj.get('precision') not in ('fp32','fp16') or obj.get('microbatch_windows') not in (1,2,4,8):
        raise RuntimeError('PRECISION_OR_MICROBATCH_NOT_FROZEN')
    if obj.get('trainer_a2_sha256')!=sha_file(__file__):
        raise RuntimeError('T4_A2_TRAINER_HASH_CHANGED')
    if obj.get('p02_git_blob')!=P02_BLOB:
        raise RuntimeError('MODEL_ARCH_CHANGED')
    return obj


def lambda_schedule(step):
    # LambdaLR gets epoch index 0 after initialization; 32 linear warmup steps.
    if step<32:return (step+1)/32
    t=min((step-32)/(TOTAL_STEPS-32),1.0)
    return .1+.9*(.5+.5*math.cos(math.pi*t))


def model_context(p02,device,precision):
    torch.manual_seed(SEED);random.seed(SEED);np.random.seed(SEED)
    torch.cuda.manual_seed_all(SEED)
    model=p02.GPT(p02.P02Config(**CONFIG)).to(device)
    if sum(p.numel() for p in model.parameters())!=3749376:raise RuntimeError('P02_ARCH_CHANGED')
    optimizer=torch.optim.AdamW(model.parameters(),lr=3e-4,betas=(.9,.95),eps=1e-8,weight_decay=.1)
    scheduler=torch.optim.lr_scheduler.LambdaLR(optimizer,lr_lambda=lambda_schedule)
    sampler=torch.Generator(device='cpu').manual_seed(SEED+71)
    scaler=torch.amp.GradScaler('cuda') if precision=='fp16' else None
    return model,optimizer,scheduler,sampler,scaler


def sample_exact_step(data,sampler,microbatch):
    """Draw train-only windows until EXACTLY 4096 valid target labels are present."""
    x=data['train_x'];y=data['train_y'];c=data['train_count']
    examples=[];total=0
    while total<TOKENS_PER_STEP:
        k=int(torch.randint(len(x),(1,),generator=sampler).item())
        n=min(int(c[k]),TOKENS_PER_STEP-total)
        if n<=0:raise RuntimeError('ZERO_TARGET_WINDOW')
        yy=y[k].copy()
        yy[n:]=-100
        examples.append((x[k],yy))
        total+=n
    if total!=TOKENS_PER_STEP:raise RuntimeError('BAD_EXACT_TARGET_BUDGET')
    groups=[]
    for st in range(0,len(examples),microbatch):
        sub=examples[st:st+microbatch]
        groups.append((np.stack([i[0] for i in sub]),np.stack([i[1] for i in sub])))
    return groups,len(examples)


def train_one_step(model,opt,sch,sampler,scaler,data,device,precision,microbatch):
    model.train()
    opt.zero_grad(set_to_none=True)
    groups,windows=sample_exact_step(data,sampler,microbatch)
    total_loss=0.0
    for x,y in groups:
        xx=torch.tensor(x,dtype=torch.long,device=device)
        yy=torch.tensor(y,dtype=torch.long,device=device)
        with torch.autocast(device_type='cuda',dtype=torch.float16,enabled=(precision=='fp16')):
            logits,_=model(xx)
            loss=F.cross_entropy(logits.float().reshape(-1,2048),yy.reshape(-1),ignore_index=-100,reduction='sum')/TOKENS_PER_STEP
        if not torch.isfinite(loss).item():raise RuntimeError('T4_NONFINITE_LOSS')
        if scaler:scaler.scale(loss).backward()
        else:loss.backward()
        total_loss+=float(loss.detach().cpu())
    if scaler:
        scaler.unscale_(opt)
        torch.nn.utils.clip_grad_norm_(model.parameters(),1.0)
        old=scaler.get_scale();scaler.step(opt);scaler.update()
        if scaler.get_scale()<old:raise RuntimeError('T4_FP16_OVERFLOW_STEP_SKIPPED')
    else:
        torch.nn.utils.clip_grad_norm_(model.parameters(),1.0)
        opt.step()
    sch.step()
    return total_loss,windows


def _numpy_rng_to_primitives():
    a=np.random.get_state()
    return (a[0],a[1].tolist(),int(a[2]),int(a[3]),float(a[4]))


def checkpoint_payload(model,opt,sch,sampler,scaler,step,lock_sha,pack_sha,elapsed,device):
    return {'schema':'ttm.t4.science.checkpoint.v1','step':step,'science_seed':SEED,
      'p02_git_blob':P02_BLOB,'config':CONFIG,'science_lock_sha256':lock_sha,
      'train_pack_sha256':pack_sha,'elapsed_gpu_seconds_total':elapsed,
      'model':model.state_dict(),'optimizer':opt.state_dict(),
      'scheduler':sch.state_dict(),'sampler_state':sampler.get_state(),
      'torch_cpu_rng':torch.get_rng_state(),'torch_cuda_rng':torch.cuda.get_rng_state_all(),
      'python_rng':random.getstate(),'numpy_rng':_numpy_rng_to_primitives(),
      'grad_scaler_state':scaler.state_dict() if scaler else None,'device_type':device.type,
      'torch_version':str(torch.__version__)}


def checkpoint_write(run_root,step,payload,log,local_scratch):
    """Write locally, copy + SHA readback to mounted Drive, READY **last**."""
    folder=run_root/'checkpoints'/f'step_{step:04d}'
    if folder.exists():raise FileExistsError('T4_CHECKPOINT_STEP_ALREADY_EXISTS')
    folder.mkdir(parents=True,exist_ok=False)
    local_scratch.mkdir(parents=True,exist_ok=True)
    tmp=local_scratch/f'ckpt_{step:04d}.pt'
    if tmp.exists():raise FileExistsError('T4_LOCAL_CHECKPOINT_ALREADY_EXISTS')
    torch.save(payload,tmp)
    hs=sha_file(tmp);n=tmp.stat().st_size
    dst=folder/'checkpoint.pt'
    with tmp.open('rb') as src,dst.open('xb') as dest:
        shutil.copyfileobj(src,dest,length=1<<20);dest.flush();os.fsync(dest.fileno())
    if sha_file(dst)!=hs or dst.stat().st_size!=n:raise RuntimeError('T4_DRIVE_CHECKPOINT_SHA_FAILED')
    log_dst=folder/'progress.json'
    json_new(log_dst,{'schema':'ttm.t4.progress.v1','step':step,'records':log})
    ready={'schema':'ttm.t4.ready.last.v1','step':step,'checkpoint':'checkpoint.pt',
           'bytes':n,'sha256':hs,'science_lock_sha256':payload['science_lock_sha256'],
           'train_pack_sha256':payload['train_pack_sha256'],
           'progress_sha256':sha_file(log_dst)}
    json_new(folder/'READY.json',ready)
    # Local scratch is disposable; leave original on partial failure for investigation.
    return ready


def checkpoint_load(folder,model,opt,sch,sampler,scaler,device,lock_sha,pack_sha):
    ready=json.loads((folder/'READY.json').read_text('utf8'))
    cp=folder/ready['checkpoint']
    if sha_file(cp)!=ready['sha256'] or cp.stat().st_size!=ready['bytes']:
        raise RuntimeError('T4_CHECKPOINT_DURABILITY_OR_SHA_MISMATCH')
    payload=torch.load(cp,map_location='cpu',weights_only=True)
    if payload['schema']!='ttm.t4.science.checkpoint.v1' or payload['p02_git_blob']!=P02_BLOB or payload['science_lock_sha256']!=lock_sha or payload['train_pack_sha256']!=pack_sha:
        raise RuntimeError('T4_RESUME_MANIFEST_PIN_MISMATCH')
    model.load_state_dict(payload['model'],strict=True)
    opt.load_state_dict(payload['optimizer']);sch.load_state_dict(payload['scheduler'])
    sampler.set_state(payload['sampler_state'].cpu())
    torch.set_rng_state(payload['torch_cpu_rng'].cpu())
    if device.type=='cuda':torch.cuda.set_rng_state_all([a.cpu() for a in payload['torch_cuda_rng']])
    random.setstate(tuple(payload['python_rng']))
    nr=payload['numpy_rng']
    np.random.set_state((nr[0],np.asarray(nr[1],dtype=np.uint32),nr[2],nr[3],nr[4]))
    if scaler:
        if payload['grad_scaler_state'] is None:raise RuntimeError('T4_GRADSCALER_NOT_SAVED')
        scaler.load_state_dict(payload['grad_scaler_state'])
    return payload['step'],float(payload['elapsed_gpu_seconds_total'])


def main():
    ap=argparse.ArgumentParser()
    ap.add_argument('--mode',choices=['preflight','science'],default='preflight')
    ap.add_argument('--p02',required=True)
    ap.add_argument('--data',required=True);ap.add_argument('--data-manifest',required=True)
    ap.add_argument('--capacity-report',required=True)
    ap.add_argument('--capacity-review',required=True)
    ap.add_argument('--drive-run',required=True)
    ap.add_argument('--lock-json');ap.add_argument('--lock-sha256')
    ap.add_argument('--resume-checkpoint-dir')
    args=ap.parse_args()
    if args.mode!='science':
        print('TTM_T4_TRAINING=NOT_AUTHORIZED_PREFLIGHT_ONLY');print('SCIENCE_LOCK=HOLD');return
    # No operation on GPU or data until complete exact signed-off lock readback.
    data_manifest=json.loads(Path(args.data_manifest).read_text('utf8'))
    cap=json.loads(Path(args.capacity_report).read_text('utf8'))
    cap_sha=sha_file(args.capacity_report)
    review=json.loads(Path(args.capacity_review).read_text('utf8'))
    review_sha=sha_file(args.capacity_review)
    if review.get('status')!='CAPACITY_PASS_PROVISIONAL_FOR_SCIENCE_REVIEW' or review.get('capacity_sha256')!=cap_sha or review.get('science_executed') is not False:
        raise RuntimeError('CAPACITY_PRIVATE_PACK_REVIEW_NOT_ACCEPTED')
    if cap.get('status')!='PASS_PROVISIONAL_CAPACITY_ONLY' or cap.get('science_executed') is not False:
        raise RuntimeError('CAPACITY_NOT_ACCEPTABLE_FOR_SCIENCE')
    lock=require_science_lock(args.lock_json,args.lock_sha256,data_manifest,cap_sha,review_sha)
    selected=review.get('selected') or {}
    if lock['precision']!=selected.get('precision') or lock['microbatch_windows']!=selected.get('microbatch_windows'):
        raise RuntimeError('LOCKED_BATCH_OR_PRECISION_DIFFERS_FROM_MEASURED_CAPACITY')
    if Path(args.drive_run).exists() and not args.resume_checkpoint_dir:
        raise FileExistsError('T4_ONE_SHOT_RUN_ID_ALREADY_EXISTS')
    if not torch.cuda.is_available():raise RuntimeError('T4_SCIENCE_REQUIRES_GPU')
    p02=p02_module(args.p02)
    data,manifest=load_private_pack(args.data,args.data_manifest)
    if manifest['npz_sha256']!=lock['train_pack_sha256']:raise RuntimeError('LOCKED_DATA_INVALID')
    model,opt,sch,sampler,scaler=model_context(p02,torch.device('cuda'),lock['precision'])
    out=Path(args.drive_run)
    if not args.resume_checkpoint_dir:out.mkdir(parents=True,exist_ok=False)
    else:
        if not out.is_dir():raise RuntimeError('MISSING_CONTINUATION_RUN_DIR')
    if args.resume_checkpoint_dir:
        start,spent=checkpoint_load(Path(args.resume_checkpoint_dir),model,opt,sch,sampler,scaler,
            torch.device('cuda'),args.lock_sha256,manifest['npz_sha256'])
        prev=Path(args.resume_checkpoint_dir)/'progress.json'
        log=json.loads(prev.read_text('utf8'))['records']
    else:start=0;spent=0.0;log=[]
    if start>=TOTAL_STEPS:
        raise RuntimeError('T4_ALREADY_REACHED_1024_NO_RERUN')
    print('T4_SCIENCE_1024_CONTINUOUS_START='+str(start), flush=True)
    print('T4_TIME_POLICY='+TIME_POLICY, flush=True)
    loguni,logbi=fit_baselines(data['train_x'],data['train_y'])
    counts,unis,bis=baseline_story_scores(data,loguni,logbi)
    for step in range(start+1,TOTAL_STEPS+1):
        torch.cuda.synchronize();t0=time.perf_counter()
        loss,drawn=train_one_step(model,opt,sch,sampler,scaler,data,torch.device('cuda'),lock['precision'],lock['microbatch_windows'])
        entry={'step':step,'train_loss':loss,'windows_drawn':drawn,'exact_scored_targets':4096}
        if step in VALID_STEPS:
            model_sums=model_story_scores(model,data,torch.device('cuda'))
            entry['val']=decide_h1(model_sums,bis,counts)
            entry['val_unigram_nll']=float(unis.sum()/counts.sum())
        torch.cuda.synchronize();spent+=time.perf_counter()-t0
        log.append(entry)
        if step in CHECKPOINT_STEPS:
            payload=checkpoint_payload(model,opt,sch,sampler,scaler,step,args.lock_sha256,manifest['npz_sha256'],spent,torch.device('cuda'))
            ready=checkpoint_write(out,step,payload,log,Path('/content/ttm_t4_ckpt_local'))
            print('T4_CHECKPOINT_READY_STEP='+str(step)+' SHA256='+ready['sha256'],flush=True)
        if step==start+1 or step%32==0 or step==TOTAL_STEPS:
            print('T4_STEP='+str(step)+'/'+str(TOTAL_STEPS)+' TRAIN_LOSS='+format(loss,'.6f')+' GPU_COMPUTE_S='+format(spent,'.1f'),flush=True)
    final={'schema':'ttm.t4.science.result.v1','status':'COMPLETED_REQUIRES_INDEPENDENT_ADJUDICATION',
       'last_step':TOTAL_STEPS,'elapsed_gpu_seconds':spent,'h1_val':log[-1]['val'],
       'no_test_used':True,'exact_scored_training_tokens':TOTAL_STEPS*TOKENS_PER_STEP,
       'time_policy':TIME_POLICY,'no_gpu_wall_clock_hard_cap':True,
       'science_lock_sha256':args.lock_sha256,'data_pack_sha256':manifest['npz_sha256']}
    json_new(out/'T4_FINAL_UNADJUDICATED.json',final)
    print('TTM_T4_FINISHED_UNADJUDICATED='+str(out/'T4_FINAL_UNADJUDICATED.json'))

if __name__=='__main__':main()
