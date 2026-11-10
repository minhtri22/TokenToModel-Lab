#!/usr/bin/env python3
"""TTM-Small4M four-arm CPU preflight / owner-gated Colab Free T4 candidate.

NO science execution without a NEW exact lock for this experiment. Does not touch
original T4 checkpoint, P02, TRAIN/VAL pack, or sealed TEST. For each science arm
restore a fresh full copy of the step1024 model/AdamW/scheduler/RNG/scaler state;
never reuse/overwrite historical step1280. Frozen source pins.

The CPU preflight deliberately performs no optimizer steps. GPU science branch
must be independently reviewed before owner authorization.
"""
from __future__ import annotations
import argparse, hashlib, importlib.util, json, math, os, random, shutil, sys, time
from pathlib import Path
import numpy as np
import torch
import torch.nn.functional as F
from real_metadata_preflight import PACK_SHA,MANIFEST_SHA,CHECKPOINT_SHA,sha_file,ranked_match,require

P02_SHA='e0fcac285918b66b13c8f694e6d625a0691c9b59221b43043e63f46b25ddcc07'
P02_BLOB='9762343e06cf800b50574c2871ae1ed58537fb18'
N_STEPS=128; START=1024; END=1152; TOKENS=4096; V=2048; CTX=256
ARMS=('A','B','C','D')
RUN_ID='TTM_SMALL4M_2X2_EQUAL_BUDGET_V1'


def load_model_source(path):
    p=Path(path)
    require(p.is_file() and not p.is_symlink() and sha_file(p)==P02_SHA,'CANONICAL_P02_SHA_MISMATCH')
    spec=importlib.util.spec_from_file_location('ttm_2x2_frozen_p02',p)
    require(spec and spec.loader,'P02_SOURCE_IMPORT_INVALID')
    mod=importlib.util.module_from_spec(spec)
    sys.modules[spec.name]=mod;spec.loader.exec_module(mod)
    return mod


def check_input(pack,manifest,checkpoint):
    for p,sha in [(pack,PACK_SHA),(manifest,MANIFEST_SHA),(checkpoint,CHECKPOINT_SHA)]:
        require(Path(p).is_file() and not Path(p).is_symlink(),'MISSING_OR_LINKED_PRIVATE_INPUT')
        require(sha_file(p)==sha,'PRIVATE_INPUT_PIN_MISMATCH')
    m=json.loads(Path(manifest).read_text('utf-8'))
    require(m['npz_sha256']==PACK_SHA and not m['contains_test'],'TRAIN_VAL_MANIFEST_MISMATCH')
    with np.load(pack,allow_pickle=False) as z:
        expected={f'{a}_{b}' for a in ('train','val') for b in ('x','y','count','story_index')}
        require(set(z.files)==expected,'PRIVATE_DATA_CONTENT_KEYS_INVALID')
        count=z['train_count'].astype(np.int64);story=z['train_story_index'].astype(np.int64)
        require(count.shape==(2691,) and count.sum()==498287,'TRAIN_COUNT_PIN_INVALID')
        require(np.all(story[1:]>=story[:-1]) and len(set(story))==2048,'TRAIN_STORY_ORDER_INVALID')
    cp=torch.load(checkpoint,map_location='cpu',weights_only=True)
    require(cp['step']==START and cp['train_pack_sha256']==PACK_SHA and cp['p02_git_blob']==P02_BLOB,'CHECKPOINT_CONTRACT_MISMATCH')
    require(cp['config']==dict(vocab_size=V,max_seq_len=CTX,n_embd=256,n_layer=4,n_head=4,norm_type='layernorm'),'CHECKPOINT_ARCH_MISMATCH')
    require(cp.get('grad_scaler_state') and cp.get('sampler_state') is not None,'CHECKPOINT_OPTIMIZER_STATE_INCOMPLETE')
    require(cp['scheduler']['last_epoch']==START,'FROZEN_SCHEDULER_STATE_MISMATCH')
    require(all(float(v['step'])==START for v in cp['optimizer']['state'].values()),'FROZEN_ADAMW_STEP_DRIFT')
    return cp


def clone_parent(p02,cp,device):
    # New objects per arm, not same model/optimizer state shared between variants.
    model=p02.GPT(p02.P02Config(**cp['config'])).to(device)
    require(sum(x.numel() for x in model.parameters())==3749376,'PARAM_COUNT_INVALID')
    opt=torch.optim.AdamW(model.parameters(),lr=3e-4,betas=(.9,.95),weight_decay=.1,eps=1e-8)
    scheduler=torch.optim.lr_scheduler.LambdaLR(opt,lr_lambda=lambda step: .1 if step>=START else 1.)
    model.load_state_dict(cp['model'],strict=True)
    opt.load_state_dict(cp['optimizer'])
    scheduler.load_state_dict(cp['scheduler'])
    sampler=torch.Generator(device='cpu');sampler.set_state(cp['sampler_state'].cpu())
    # GradScaler state preserved verbatim in GPU mode. On CPU the GradScaler is
    # constructed for its state contract only, no FP16 training performed.
    scaler=torch.amp.GradScaler('cuda' if device.type=='cuda' else 'cpu')
    scaler.load_state_dict(cp['grad_scaler_state'])
    require(scaler.state_dict()==cp['grad_scaler_state'],'GRAD_SCALER_STATE_NOT_RESTORED')
    require(math.isclose(opt.param_groups[0]['lr'],3e-5,rel_tol=1e-5),'LR_NOT_AT_FROZEN_FLOOR')
    if device.type=='cuda':
        torch.set_rng_state(cp['torch_cpu_rng'].cpu())
        torch.cuda.set_rng_state_all([x.cpu() for x in cp['torch_cuda_rng']])
        random.setstate(cp['python_rng'])
        q=cp['numpy_rng'];np.random.set_state((q[0],np.asarray(q[1],dtype=np.uint32),q[2],q[3],q[4]))
    return model,opt,scheduler,sampler,scaler


def plan_steps(count,story,cp):
    first=np.r_[True,story[1:]!=story[:-1]]
    firstidx=np.flatnonzero(first)
    require(len(firstidx)==2048 and (count[firstidx]==256).any(),'MISSING_REAL_FULL_FIRST_WINDOW')
    gen=torch.Generator(device='cpu');gen.set_state(cp['sampler_state'].cpu())
    candidates={}
    out=[]
    for step in range(START+1,END+1):
        budget=0;d=0;arr=[]
        while budget<TOKENS:
            idx=int(torch.randint(len(count),(1,),generator=gen).item())
            n=min(int(count[idx]),TOKENS-budget)
            choices=candidates.setdefault(n,[int(i) for i in firstidx if count[i]>=n])
            require(len(choices)>0,'UNMATCHABLE_REAL_FIRST_WINDOW')
            matched=ranked_match(choices,step,d,story)
            require(count[matched]>=n and first[matched],'REAL_FIRST_WINDOW_MATCH_DRIFT')
            arr.append((idx,matched,n));budget+=n;d+=1
        require(budget==TOKENS,'SOURCE_BUDGET_DRIFT')
        out.append((step,arr))
    require(len(out)==N_STEPS,'BAD_SCIENCE_STEP_SCHEDULE')
    return out


def fixed_batch(data,plan,arm):
    choose=0 if arm in 'AC' else 1
    x=[];y=[]
    for srcA,srcB,n in plan:
        idx=(srcA,srcB)[choose]
        input_ids=data['train_x'][idx].astype(np.int64).copy()
        target_ids=data['train_y'][idx].astype(np.int64).copy()
        require(1<=n<=int(data['train_count'][idx]),'BATCH_TARGET_OVERREAD')
        target_ids[n:]=-100
        x.append(input_ids);y.append(target_ids)
    return np.stack(x),np.stack(y)


def loss_step(model,x,y,arm,device,autocast,*,required_scored_targets=TOKENS):
    weighted=arm in 'CD'
    den=0
    for row in y:
        n=int((row!=-100).sum())
        den+=min(n,32)+3*max(n-32,0) if weighted else n
    require(sum(int((row!=-100).sum()) for row in y)==required_scored_targets,
            'WEIGHT_DENOM_INVALID')
    total=0.
    for start in range(0,len(x),8):
        xx=torch.as_tensor(x[start:start+8],dtype=torch.long,device=device)
        yy=torch.as_tensor(y[start:start+8],dtype=torch.long,device=device)
        require(torch.all((yy==-100)|((yy>=0)&(yy<V))).item(),'LOSS_BAD_LABEL_ID')
        with torch.autocast('cuda',dtype=torch.float16,enabled=autocast):
            logits,_=model(xx)
            require(torch.isfinite(logits).all().item(),'LOSS_NONFINITE_LOGITS')
            ll=F.cross_entropy(logits.float().reshape(-1,V),yy.reshape(-1),reduction='none',ignore_index=-100)
            ll=ll.reshape(yy.shape)
            w=yy.ne(-100).to(ll.dtype)
            if weighted:
                z=torch.arange(CTX,device=device).view(1,-1)
                w*=torch.where(z>=32,3.,1.)
            ls=(w*ll).sum()/den
        require(torch.isfinite(ls).item(),'NONFINITE_SCIENCE_LOSS')
        total=total+ls
        yield ls


def cpu_preflight(p02,cp,out):
    device=torch.device('cpu')
    model,opt,sched,sampler,scaler=clone_parent(p02,cp,device)
    # These are synthetic input IDs, never any private training material.
    model.eval();torch.manual_seed(19001)
    xx=torch.randint(0,V,(1,CTX),dtype=torch.long)
    with torch.no_grad():
        out_logits,_=model(xx)
    require(out_logits.shape==(1,CTX,V) and torch.isfinite(out_logits).all().item(),'CPU_CANONICAL_MODEL_FORWARD_INVALID')
    require(int(opt.state_dict()['state'][next(iter(opt.state_dict()['state']))]['step'])==1024,'CPU_OPT_RESTORE_FAIL')
    require(sched.last_epoch==1024,'CPU_SCHED_RESTORE_FAIL')
    require(scaler.state_dict()['scale']==cp['grad_scaler_state']['scale'],'CPU_SCALER_RESTORE_FAIL')
    result={'schema':'ttm.small4m.2x2.cpu_full_parent_restore_preflight.v1','status':'PASS_FULL_PARENT_MODEL_ADAMW_SCHEDULER_SAMPLER_SCALER_CPU_RESTORE',
     'checkpoint_sha256':CHECKPOINT_SHA,'p02_sha256':P02_SHA,'model_params':3749376,
     'model_logits_finite':True,'model_logits_shape':list(out_logits.shape),
     'optimizer_state_count':len(opt.state_dict()['state']),'optimizer_step':1024,
     'scheduler_step':sched.last_epoch,'scaler_state':{'scale':float(scaler.state_dict()['scale']),'growth_tracker':int(scaler.state_dict()['_growth_tracker'])},
     'no_optimizer_step':True,'no_private_train_tokens_scored':True,'gpu_fp16_not_executed':True}
    Path(out).write_text(json.dumps(result,sort_keys=True,indent=2)+'\n',encoding='utf-8')
    return result


def require_owner_science_lock(args):
    require(bool(args.owner_lock) and bool(args.owner_lock_sha),'SCIENCE_NOT_AUTHORIZED_NO_NEW_OWNER_LOCK')
    lockpath=Path(args.owner_lock)
    require(lockpath.is_file() and sha_file(lockpath)==args.owner_lock_sha,'OWNER_LOCK_SHA_OR_PATH_INVALID')
    lock=json.loads(lockpath.read_text('utf-8'))
    strict={'authorization':'OWNER_APPROVED_NEW_2X2_SINGLE_INTEGRATED_T4_BATCH',
            'experiment_run_id':RUN_ID,
            'checkpoint_sha256':CHECKPOINT_SHA,'pack_sha256':PACK_SHA,
            'steps_per_arm':128,'valid_targets_per_step':4096,
            'arms':['A','B','C','D'],
            'no_test':True,'no_q1q2':True,'free_colab_only':True}
    require(all(lock.get(k)==v for k,v in strict.items()),'OWNER_LOCK_CONTRACT_MISMATCH')
    require(lock.get('runner_source_sha256')==sha_file(__file__),'SCIENCE_RUNNER_SOURCE_NOT_FROZEN')
    require(lock.get('rights_attestation_sha256') and lock.get('eval_freeze_sha256') and lock.get('independent_reviewer_receipt_sha256'),'MISSING_RIGHTS_EVAL_REVIEWER_LOCK')
    return lock


@torch.no_grad()
def eval_original_val_nll(model,data,device):
    """Score locked 256-story VAL only; never TEST, never fit hyperparameters."""
    model.eval()
    sums=np.zeros(256,dtype=np.float64)
    counts=np.zeros(256,dtype=np.int64)
    for start in range(0,len(data['val_x']),4):
        end=min(start+4,len(data['val_x']))
        xx=torch.as_tensor(data['val_x'][start:end].astype(np.int64),dtype=torch.long,device=device)
        yy=torch.as_tensor(data['val_y'][start:end].astype(np.int64),dtype=torch.long,device=device)
        logits,_=model(xx)
        ll=F.cross_entropy(logits.float().reshape(-1,V),yy.reshape(-1),reduction='none',ignore_index=-100)
        per=ll.reshape(yy.shape).sum(1).double().cpu().numpy()
        for j in range(end-start):
            k=int(data['val_story_index'][start+j]);sums[k]+=float(per[j]);counts[k]+=int(data['val_count'][start+j])
    require(int(counts.sum())==61122 and (counts>0).all(),'FROZEN_VAL_COUNT_DRIFT')
    return {'val_nll':float(sums.sum()/counts.sum()),'val_target_count':int(counts.sum()),
            'val_story_count':256,'never_test':True,
            'story_loss_digest':hashlib.sha256(np.asarray(sums,dtype='<f8').tobytes()).hexdigest()}

def science(args,p02,cp):
    # Stop BEFORE loading private TRAIN arrays or touching GPU when not authorized.
    lock=require_owner_science_lock(args)
    require(torch.cuda.is_available() and torch.cuda.device_count()==1,'SINGLE_T4_CUDA_REQUIRED')
    require('T4' in torch.cuda.get_device_name(0),'NOT_FREE_T4')
    require(str(torch.__version__)==lock.get('torch_version'),'CUDA_TORCH_VERSION_DRIFT')
    require(args.output and Path(args.output).parent.is_dir() and not Path(args.output).exists(),'NEW_OUTPUT_ALREADY_EXISTS_OR_BAD_PARENT')
    out=Path(args.output);out.mkdir(exist_ok=False)
    # ONLY after the new lock do we read and construct the actual TRAIN batches.
    with np.load(args.pack,allow_pickle=False) as npz:
        data={z:npz[z] for z in ('train_x','train_y','train_count','train_story_index','val_x','val_y','val_count','val_story_index')}
    count=data['train_count'].astype(np.int64);story=data['train_story_index'].astype(np.int64)
    all_plans=plan_steps(count,story,cp)
    # Never publish the window indices or source story IDs: report hashes only.
    dev=torch.device('cuda')
    for arm in ARMS:
        armdir=out/f'ARM_{arm}'
        armdir.mkdir(exist_ok=False)
        model,opt,sch,sampler,scaler=clone_parent(p02,cp,dev)
        losses=[];start_ts=time.perf_counter()
        for step,plan in all_plans:
            x,y=fixed_batch(data,plan,arm)
            require(sum(int((z!=-100).sum()) for z in y)==TOKENS,'VALID_TARGETS_DRIFT')
            model.train();opt.zero_grad(set_to_none=True)
            subtotal=0.
            for partial in loss_step(model,x,y,arm,dev,autocast=True):
                scaler.scale(partial).backward()
                subtotal+=float(partial.detach().cpu())
            scaler.unscale_(opt);torch.nn.utils.clip_grad_norm_(model.parameters(),1.0)
            scale_before=scaler.get_scale()
            scaler.step(opt);scaler.update()
            require(scaler.get_scale()>=scale_before,'SCALER_OVERFLOW_SKIPPED_STEP')
            sch.step()
            require(abs(float(opt.param_groups[0]['lr'])-3e-5)<1e-7,'LR_DRIFT_FROM_FLOOR')
            losses.append({'step':step,'train_loss':subtotal,'valid_targets':TOKENS,'windows':len(plan)})
        # VAL scores are comparison safety metrics, not TEST or model selection evidence.
        val_report=eval_original_val_nll(model,data,dev)
        # Save complete restart-state payload; READY-last after SHA readback.
        # Step1152 is only a candidate in a new lineage, not historical 1152.
        torch.cuda.synchronize()
        state={'schema':'ttm.small4m.2x2.arm.checkpoint.v1','run_id':RUN_ID,'arm':arm,'step':END,
         'parent_sha256':CHECKPOINT_SHA,'pack_sha256':PACK_SHA,'source_sha256':sha_file(__file__),
         'model':model.state_dict(),'optimizer':opt.state_dict(),'scheduler':sch.state_dict(),
         'sampler_state':sampler.get_state(),'grad_scaler_state':scaler.state_dict(),
         'torch_cpu_rng':torch.get_rng_state(),'torch_cuda_rng':torch.cuda.get_rng_state_all(),
         'numpy_rng':(np.random.get_state()[0],np.random.get_state()[1].tolist(),int(np.random.get_state()[2]),int(np.random.get_state()[3]),float(np.random.get_state()[4])),'python_rng':random.getstate()}
        ck=armdir/'checkpoint.pt'
        with ck.open('xb') as fp:torch.save(state,fp);fp.flush();os.fsync(fp.fileno())
        cksha=sha_file(ck)
        receipt={'arm':arm,'run_id':RUN_ID,'status':'TRAINED_CHECKPOINT_UNADJUDICATED',
         'step':END,'checkpoint_sha256':cksha,'checkpoint_bytes':ck.stat().st_size,
         'compute_s':time.perf_counter()-start_ts,'targets':128*4096,'source_sha256':sha_file(__file__),
         'val_report':val_report}
        (armdir/'progress.json').write_text(json.dumps(losses,sort_keys=True,indent=2)+'\n',encoding='utf-8')
        receipt['progress_sha256']=sha_file(armdir/'progress.json')
        with (armdir/'READY.json').open('x',encoding='utf-8') as f:json.dump(receipt,f,sort_keys=True,indent=2);f.write('\n');f.flush();os.fsync(f.fileno())
    print('ALL_4_ARMS_TRAINED_UNADJUDICATED_NEEDS_VAL_AND_BLIND_QUALITY_REVIEW')


def main():
    ap=argparse.ArgumentParser()
    ap.add_argument('--mode',choices=['cpu-qa','science'],default='cpu-qa')
    ap.add_argument('--pack',required=True);ap.add_argument('--manifest',required=True)
    ap.add_argument('--checkpoint',required=True);ap.add_argument('--p02',required=True)
    ap.add_argument('--output',required=True)
    ap.add_argument('--owner-lock');ap.add_argument('--owner-lock-sha')
    args=ap.parse_args()
    # Mode-scoped owner gate must precede checkpoint source loading.
    if args.mode=='science':require_owner_science_lock(args)
    cp=check_input(args.pack,args.manifest,args.checkpoint)
    p02=load_model_source(args.p02)
    if args.mode=='cpu-qa':
        result=cpu_preflight(p02,cp,args.output)
        print(result['status'])
    else:science(args,p02,cp)
if __name__=='__main__':main()
