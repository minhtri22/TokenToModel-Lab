#!/usr/bin/env python3
"""TTM T3 20 continuous vs 10 READY-last checkpoint restore +10 synthetic QA.

Run on Colab with --drive-root pointing at mounted /content/drive/MyDrive/TTM/...
No TinyStories or science. Independent evidence in strict new run_id. T3 uses exact P02.
"""
from __future__ import annotations
import argparse, hashlib, importlib.util, json, math, os, random, sys, time
from pathlib import Path

import torch

SEED=20261108
P02_BLOB='9762343e06cf800b50574c2871ae1ed58537fb18'
CONFIG=dict(vocab_size=2048,max_seq_len=256,n_embd=256,n_layer=4,n_head=4,norm_type='layernorm')
TOTAL=20; FIRST=10


def file_sha(p):
    h=hashlib.sha256()
    with open(p,'rb') as f:
        for b in iter(lambda:f.read(1<<20),b''):h.update(b)
    return h.hexdigest()


def atomic_json(path,data):
    temp=path.with_suffix(path.suffix+'.part')
    if temp.exists() or path.exists():raise FileExistsError('NO_OVERWRITE_READY:'+str(path))
    with open(temp,'x',encoding='utf8') as f:
        json.dump(data,f,sort_keys=True,indent=2);f.write('\n');f.flush();os.fsync(f.fileno())
    os.replace(temp,path)


def load_p02(path):
    b=path.read_bytes()
    ident=hashlib.sha1(b'blob '+str(len(b)).encode()+b'\0'+b).hexdigest()
    if ident!=P02_BLOB:raise RuntimeError('P02_SOURCE_PIN_MISMATCH:'+ident)
    spec=importlib.util.spec_from_file_location('ttm_t3_p02_exact',path)
    module=importlib.util.module_from_spec(spec);sys.modules[spec.name]=module;spec.loader.exec_module(module)
    return module


def build_model(p02,device):
    torch.manual_seed(SEED)
    if device.type=='cuda':torch.cuda.manual_seed_all(SEED)
    model=p02.GPT(p02.P02Config(**CONFIG)).to(device)
    if sum(p.numel() for p in model.parameters())!=3749376:raise AssertionError('PARAMS_CHANGED')
    return model


def train_context(p02,device):
    model=build_model(p02,device)
    opt=torch.optim.AdamW(model.parameters(),lr=3e-4,betas=(.9,.95),weight_decay=.1)
    sch=torch.optim.lr_scheduler.LambdaLR(opt,lr_lambda=lambda step: min(1.,(step+1)/4.) if step<4 else (0.1+0.9*0.5*(1+math.cos(math.pi*(step-4)/16))))
    g=torch.Generator(device='cpu').manual_seed(SEED+17)
    return model,opt,sch,g


def do_steps(model,opt,sch,g,start,end,device):
    losses=[]
    model.train()
    for step in range(start,end):
        # Synthetic tokens only. CPU generator keeps sampler sequence across CUDA/CPU.
        raw=torch.randint(0,2048,(2,33),generator=g,dtype=torch.long)
        x,y=raw[:,:-1].to(device),raw[:,1:].to(device)
        opt.zero_grad(set_to_none=True)
        logits,loss=model(x,y)
        if not torch.isfinite(loss).item():raise RuntimeError('NONFINITE_LOSS')
        loss.backward()
        torch.nn.utils.clip_grad_norm_(model.parameters(),1.0)
        opt.step();sch.step()
        losses.append(float(loss.item()))
    return losses


def payload(model,opt,sch,g,step,device):
    return {'schema':'ttm.t3.full.resume.synthetic.v1','step':step,'seed':SEED,
      'config':CONFIG,'p02_source_blob':P02_BLOB,
      'model':model.state_dict(),'optimizer':opt.state_dict(),
      'scheduler':sch.state_dict(),'batch_generator_state':g.get_state(),
      'torch_rng_cpu':torch.get_rng_state(),
      'torch_rng_cuda':torch.cuda.get_rng_state_all() if device.type=='cuda' else [],
      'python_random_state':list(random.getstate()),
      'torch_version':str(torch.__version__), 'device_type':device.type,
      'training_kind':'SYNTHETIC_RESUME_QA_ONLY'}


def restore(payload,p02,device):
    if payload['schema']!='ttm.t3.full.resume.synthetic.v1' or payload['step']!=FIRST or payload['config']!=CONFIG or payload['p02_source_blob']!=P02_BLOB or payload['device_type']!=device.type:
        raise RuntimeError('CHECKPOINT_METADATA_OR_DEVICE_MISMATCH')
    model,opt,sch,g=train_context(p02,device)
    model.load_state_dict(payload['model'],strict=True)
    opt.load_state_dict(payload['optimizer'])
    sch.load_state_dict(payload['scheduler'])
    g.set_state(payload['batch_generator_state'])
    random.setstate(tuple(payload['python_random_state']))
    torch.set_rng_state(payload['torch_rng_cpu'])
    if device.type=='cuda':torch.cuda.set_rng_state_all(payload['torch_rng_cuda'])
    return model,opt,sch,g


def tdiff(a,b):
    return max(float((a[k].detach().cpu()-b[k].detach().cpu()).abs().max()) for k in a)


def optimizer_tensors(opt):
    return [x.detach().cpu().clone() for state in opt.state.values() for x in state.values() if torch.is_tensor(x)]


def one_trial(p02,device,drive_root,run_id):
    if not run_id.isidentifier():raise RuntimeError('RUN_ID_MUST_BE_SAFE_IDENTIFIER')
    if drive_root.is_symlink():raise RuntimeError('DRIVE_ROOT_SYMLINK')
    drive_root.mkdir(parents=True,exist_ok=True)
    directory=drive_root/run_id
    if directory.exists():raise FileExistsError('RUN_ID_EXISTS_NO_RETRY:'+str(directory))
    directory.mkdir(mode=0o700)
    torch.set_num_threads(2)
    torch.use_deterministic_algorithms(True)
    # Round A: continuous
    base,bo,bs,bg=train_context(p02,device)
    all_losses=do_steps(base,bo,bs,bg,0,TOTAL,device)
    # Round B: interrupted/checkpoint/resumed. Same synthetic seed & code.
    partial,po,ps,pg=train_context(p02,device)
    before=do_steps(partial,po,ps,pg,0,FIRST,device)
    cp=directory/'checkpoint_step10.pt'
    tmp=directory/'checkpoint_step10.pt.part'
    if cp.exists() or tmp.exists():raise FileExistsError('CHECKPOINT_EXISTS_NO_OVERWRITE')
    with tmp.open('xb') as f:
        torch.save(payload(partial,po,ps,pg,FIRST,device),f)
        f.flush();os.fsync(f.fileno())
    os.replace(tmp,cp)
    checksum=file_sha(cp)
    # READY written only AFTER file bytes on the mounted Drive path are fsynced.
    ready={'schema':'ttm.t3.ready.last.v1','sha256':checksum,'bytes':cp.stat().st_size,
           'filename':cp.name,'step':FIRST,'p02_git_blob':P02_BLOB,
           'checkpoint_includes':['model','optimizer','scheduler','rng','sampler','cursor'],
           'synthetic_only':True}
    atomic_json(directory/'READY.json',ready)
    # Read back from durable Drive path, not from in-memory payload.
    observed=json.loads((directory/'READY.json').read_text('utf8'))
    if observed!=ready or file_sha(cp)!=checksum:raise RuntimeError('DRIVE_READY_READBACK_FAILED')
    # Only read trusted own local checkpoint after exact SHA. weights_only=True enforces safe types.
    ckpt=torch.load(cp,map_location=device,weights_only=True)
    resumed,ro,rs,rg=restore(ckpt,p02,device)
    after=do_steps(resumed,ro,rs,rg,FIRST,TOTAL,device)
    loss_diff=max(abs(a-b) for a,b in zip(all_losses,before+after))
    weights_diff=tdiff(base.state_dict(),resumed.state_dict())
    optimA=optimizer_tensors(bo);optimB=optimizer_tensors(ro)
    if len(optimA)!=len(optimB):raise RuntimeError('OPT_STATE_LENGTH_MISMATCH')
    optim_diff=max(float((a-b).abs().max()) for a,b in zip(optimA,optimB))
    scheduler_ok=bs.state_dict()==rs.state_dict()
    sampler_ok=torch.equal(bg.get_state(),rg.get_state())
    python_rng_restored=random.getstate()==tuple(ckpt['python_random_state'])
    ok=loss_diff==0 and weights_diff==0 and optim_diff==0 and scheduler_ok and sampler_ok and python_rng_restored
    receipt={'schema':'ttm.t3.resume.parity.report.v1','mode':'SYNTHETIC_ONLY_NO_SCIENCE',
        'device':str(device),'torch':str(torch.__version__),'p02_git_blob':P02_BLOB,
        'steps_contiguous':TOTAL,'step_checkpoint':FIRST,
        'checkpoint_sha256':checksum,'checkpoint_bytes':cp.stat().st_size,
        'checkpoint_ready_last':True,'ready_readback':True,
        'max_abs_loss_diff':loss_diff,'max_abs_weight_diff':weights_diff,
        'max_abs_optimizer_diff':optim_diff,'scheduler_exact':scheduler_ok,
        'sampler_state_exact':sampler_ok,'python_rng_state_restored':python_rng_restored,'pass':bool(ok),'gpu_science_used':False,
        'status':'PASS_SYNTHETIC_RESUME' if ok else 'FAIL_SYNTHETIC_RESUME'}
    atomic_json(directory/'T3_RESUME_REPORT.json',receipt)
    return receipt


def main():
    ap=argparse.ArgumentParser()
    ap.add_argument('--p02',required=True)
    ap.add_argument('--drive-root',required=True)
    ap.add_argument('--run-id',required=True)
    ap.add_argument('--device',choices=('cpu','cuda'),default='cpu')
    args=ap.parse_args()
    device=torch.device(args.device)
    if device.type=='cuda' and not torch.cuda.is_available():raise RuntimeError('COLAB_CUDA_NOT_AVAILABLE')
    random.seed(SEED);torch.manual_seed(SEED)
    if device.type=='cuda':
        if hasattr(torch.backends.cuda.matmul,'allow_tf32'):torch.backends.cuda.matmul.allow_tf32=False
        if hasattr(torch.backends.cudnn,'allow_tf32'):torch.backends.cudnn.allow_tf32=False
    # Exact deterministic GPU setup may require CUBLAS_WORKSPACE_CONFIG before importing torch on Colab.
    p02=load_p02(Path(args.p02))
    result=one_trial(p02,device,Path(args.drive_root),args.run_id)
    print('TTM_T3_RESUME_RESULT='+json.dumps(result,sort_keys=True))
    if not result['pass']:sys.exit(2)

if __name__=='__main__':main()
