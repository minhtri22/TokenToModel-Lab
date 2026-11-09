#!/usr/bin/env python3
"""TTM T4 one-shot zero-science full P02 GPU trainer/Drive integrated regression.

Uses only programmatic synthetic variable-length windows, never reads TinyStories or NPZ.
Fails closed on any mismatch. Do not retry the same Drive run directory.
"""
from __future__ import annotations
import os
os.environ.setdefault('CUBLAS_WORKSPACE_CONFIG', ':4096:8')
import argparse,copy,hashlib,json,random,sys,time
from pathlib import Path
import numpy as np
import torch
from t4_capacity_smoke import p02_module, P02_BLOB, SEED
from t4_train_science import (model_context,train_one_step,checkpoint_payload,checkpoint_write,
                              checkpoint_load,sha_file,json_new,TOKENS_PER_STEP)
from t4_eval import (fit_baselines,baseline_story_scores,model_story_scores,decide_h1)

SCHEMA='ttm.t4.synthetic.gpu.trainer.drive.integration.v1'
RUN_ID='t4_trainer_gpu_integration_synthetic_20261108_v1'
GPU_EXPECT='Tesla T4'
PRECISION='fp16'
MICROBATCH=8


def synth_windows():
    """Only synthetic IDs, approximately real TRAIN window lengths; every row = separate story."""
    rng=np.random.default_rng(18008)
    pattern=[256,210,134,178,146,244,101,163,236,206,230,197,190,256,85,140,222,194,126,230,169,179]
    counts=np.asarray((pattern*3)[:60],dtype=np.int16)
    x=np.zeros((len(counts),256),dtype=np.int16)
    y=np.full((len(counts),256),-100,dtype=np.int16)
    for j,c in enumerate(counts):
        n=int(c)
        ids=rng.integers(1,2048,size=n+1,dtype=np.int16)
        ids[-1]=256
        x[j,:n]=ids[:-1]
        y[j,:n]=ids[1:]
    si=np.arange(len(counts),dtype=np.int32)
    out={}
    for prefix,sl in [('train',slice(None)),('val',slice(0,12))]:
        out[prefix+'_x']=x[sl].copy()
        out[prefix+'_y']=y[sl].copy()
        out[prefix+'_count']=counts[sl].copy()
        out[prefix+'_story_index']=si[sl].copy()
    return out


def _cpu_copy(d):
    if isinstance(d,torch.Tensor):return d.detach().cpu().clone()
    if isinstance(d,dict):return {k:_cpu_copy(v) for k,v in d.items()}
    if isinstance(d,(list,tuple)):return type(d)(_cpu_copy(v) for v in d)
    return copy.deepcopy(d)


def _max_abs(a,b):
    if isinstance(a,torch.Tensor):
        assert isinstance(b,torch.Tensor) and a.shape==b.shape
        return float((a.detach().cpu().to(torch.float64)-b.detach().cpu().to(torch.float64)).abs().max().item())
    if isinstance(a,dict):
        if a.keys()!=b.keys():raise RuntimeError('OPTIMIZER_KEYS_DIFFER')
        return max([_max_abs(a[k],b[k]) for k in a] or [0])
    if isinstance(a,(list,tuple)):
        if len(a)!=len(b):raise RuntimeError('OPTIMIZER_LIST_LENGTH_DIFFER')
        return max([_max_abs(v,w) for v,w in zip(a,b)] or [0])
    if isinstance(a,(int,float)) and not isinstance(a,bool):return abs(float(a)-float(b))
    if a!=b:raise RuntimeError('NONNUMERIC_STATE_DIFFERS')
    return 0.0


def main():
    p=argparse.ArgumentParser();p.add_argument('--source-dir',required=True);p.add_argument('--drive-parent',required=True)
    args=p.parse_args()
    source=Path(args.source_dir);parent=Path(args.drive_parent)
    run=parent/RUN_ID
    if not parent.is_dir() or run.exists():raise RuntimeError('DRIVE_ROOT_MISSING_OR_RUN_CONSUMED')
    if not torch.cuda.is_available():raise RuntimeError('GPU_REQUIRED')
    gpu=torch.cuda.get_device_name(0)
    if GPU_EXPECT not in gpu:raise RuntimeError('REQUIRES_TESLA_T4_ACTUAL='+gpu)
    if str(torch.__version__)!='2.14.1+cu130':raise RuntimeError('TORCH_VERSION_NOT_FROZEN:'+str(torch.__version__))
    torch.set_num_threads(2)
    torch.use_deterministic_algorithms(True)
    torch.backends.cudnn.benchmark=False
    p02=p02_module(source/'p02_source_exact.py')
    data=synth_windows()
    assert set(data)=={f'{p}_{k}' for p in ('train','val') for k in ('x','y','count','story_index')}
    assert np.all(data['train_count']>0)
    run.mkdir(exist_ok=False)
    lock_sha='0'*64  # diagnostic-only placeholder, NEVER a scientific authorization
    pack_sha='1'*64  # artificial synthetic diagnostic marker, not a real NPZ
    gpu_device=torch.device('cuda')
    model,opt,sch,g,scaler=model_context(p02,gpu_device,PRECISION)
    torch.cuda.reset_peak_memory_stats()
    torch.cuda.synchronize();start=time.perf_counter()
    loss1,win1=train_one_step(model,opt,sch,g,scaler,data,gpu_device,PRECISION,MICROBATCH)
    torch.cuda.synchronize();s1=time.perf_counter()-start
    step1_payload=checkpoint_payload(model,opt,sch,g,scaler,1,lock_sha,pack_sha,s1,gpu_device)
    ready=checkpoint_write(run,1,step1_payload,[{'step':1,'synthetic_only':True,'scored_targets':4096}],Path('/content/ttm_t4_integration_local_scratch_20261108'))
    if not ready['sha256'] or not (run/'checkpoints/step_0001/READY.json').is_file():raise RuntimeError('STEP1_DURABILITY_FAIL')
    torch.cuda.synchronize();start=time.perf_counter()
    loss2,win2=train_one_step(model,opt,sch,g,scaler,data,gpu_device,PRECISION,MICROBATCH)
    torch.cuda.synchronize();s2=time.perf_counter()-start
    baseline_w=_cpu_copy(model.state_dict())
    baseline_o=_cpu_copy(opt.state_dict());baseline_s=_cpu_copy(sch.state_dict())
    baseline_g=g.get_state().clone();baseline_cuda=[t.clone() for t in torch.cuda.get_rng_state_all()]
    del model,opt,sch,g,scaler
    torch.cuda.empty_cache()
    model2,opt2,sch2,g2,scaler2=model_context(p02,gpu_device,PRECISION)
    step,spent=checkpoint_load(run/'checkpoints/step_0001',model2,opt2,sch2,g2,scaler2,
                              gpu_device,lock_sha,pack_sha)
    if step!=1:raise RuntimeError('RESTORED_WRONG_STEP')
    torch.cuda.synchronize();start=time.perf_counter()
    loss2r,win2r=train_one_step(model2,opt2,sch2,g2,scaler2,data,gpu_device,PRECISION,MICROBATCH)
    torch.cuda.synchronize();resume_s=time.perf_counter()-start
    losses_diff=abs(loss2-loss2r)
    weights_diff=_max_abs(baseline_w,_cpu_copy(model2.state_dict()))
    optimizer_diff=_max_abs(baseline_o,_cpu_copy(opt2.state_dict()))
    scheduler_diff=_max_abs(baseline_s,_cpu_copy(sch2.state_dict()))
    sampler_equal=torch.equal(baseline_g,g2.get_state())
    cuda_rng_equal=all(torch.equal(a,b) for a,b in zip(baseline_cuda,torch.cuda.get_rng_state_all()))
    if not(len(baseline_cuda)==len(torch.cuda.get_rng_state_all())):cuda_rng_equal=False
    loguni,logbig=fit_baselines(data['train_x'],data['train_y'])
    counts,uni,bigram=baseline_story_scores(data,loguni,logbig)
    torch.cuda.synchronize();start=time.perf_counter()
    scores=model_story_scores(model2,data,gpu_device,eval_batch=4)
    torch.cuda.synchronize();val_s=time.perf_counter()-start
    h1=decide_h1(scores,bigram,counts)
    # Scientifically meaningless on synthetic IDs; test only evaluator structure.
    qa_ok=(step==1 and loss2==loss2r and weights_diff==0 and optimizer_diff==0 and
           scheduler_diff==0 and win2==win2r and sampler_equal and cuda_rng_equal and
           int(h1['scored_val_targets'])==int(data['val_count'].sum()))
    report={'schema':SCHEMA,
            'status':'PASS_SYNTHETIC_T4_TRAINER_GPU_DRIVE_RESUME' if qa_ok else 'FAIL_SYNTHETIC_T4_TRAINER_GPU_DRIVE_RESUME',
            'pass':bool(qa_ok),'science_executed':False,'private_pack_accessed':False,
            'tiny_stories_used':False,'test_used':False,'candidate_only':True,
            'source_p02_blob':P02_BLOB,'torch':str(torch.__version__),'gpu':gpu,
            'precision':PRECISION,'microbatch_windows':MICROBATCH,
            'nonpad_target_tokens_per_step':4096,'synthetic_mean_targets_per_window':float(data['train_count'].mean()),
            'synthetic_train_windows':len(data['train_x']),'val_stories_synthetic':len(data['val_count']),
            'windows_first':int(win1),'windows_contiguous_second':int(win2),'windows_restored_second':int(win2r),
            'step1_time_seconds':s1,'step2_contiguous_time_seconds':s2,'step2_restored_time_seconds':resume_s,
            'val_model_evaluation_seconds':val_s,'val_scored_targets':int(h1['scored_val_targets']),
            'loss_step2_max_abs_diff':losses_diff,'weight_step2_max_abs_diff':weights_diff,
            'optimizer_step2_max_abs_diff':optimizer_diff,'scheduler_step2_max_abs_diff':scheduler_diff,
            'sampler_state_equal':bool(sampler_equal),'torch_cuda_rng_equal':bool(cuda_rng_equal),
            'checkpoint_original_sha256':ready['sha256'],
            'checkpoint_original_bytes':ready['bytes'],
            'peak_cuda_reserved_bytes':int(torch.cuda.max_memory_reserved()),
            'h1_scientific_result':'NOT_APPLICABLE_SYNTHETIC_ONLY'}
    report_path=run/'T4_SYNTHETIC_TRAINER_INTEGRATION_REPORT.json'
    json_new(report_path,report)
    json_new(run/'COLAB_ENVIRONMENT.json',{'schema':'ttm.t4.synthetic.gpu.integration.env.v1',
       'torch':str(torch.__version__),'gpu':gpu,'cuda':str(torch.version.cuda),
       'synthetic_only':True,'science_executed':False,
       'report_sha256':sha_file(report_path)})
    json_new(run/'READY.json',{'schema':'ttm.t4.synthetic.gpu.integration.ready.last.v1',
       'status':report['status'],'science_executed':False,
       'report_sha256':sha_file(report_path),'env_sha256':sha_file(run/'COLAB_ENVIRONMENT.json'),
       'original_step1_checkpoint_sha256':ready['sha256'],
       'original_step1_ready_sha256':sha_file(run/'checkpoints/step_0001/READY.json')})
    print('T4_SYNTHETIC_GPU_INTEGRATION_REPORT='+str(report_path),flush=True)
    print('T4_SYNTHETIC_GPU_INTEGRATION_REPORT_SHA256='+sha_file(report_path),flush=True)
    print('T4_SYNTHETIC_GPU_INTEGRATION_STATUS='+report['status'],flush=True)
    print('T4_SCIENCE_LOCK=HOLD',flush=True)
    if not qa_ok:raise SystemExit(2)

if __name__=='__main__':main()
