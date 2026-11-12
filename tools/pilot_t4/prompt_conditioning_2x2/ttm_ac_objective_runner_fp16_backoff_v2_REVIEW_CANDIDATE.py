#!/usr/bin/env python3
"""Two-arm A/C pre-science FP16-backoff amendment CANDIDATE, not authorized.

Changes only failed GradScaler attempt handling; A/C data, loss, 128 successful
optimizer updates, parent source, and locked FINAL24 evaluation remain unchanged.
NO science execution without new EXACT owner lock including amendment approval.
Source QA never forwards the model.

Original: Two-arm A/C objective-only candidate. Source QA never forwards the model.

Science refuses missing exact owner lock. Same-run resume consumes only a verified
READY boundary. An observed in-flight step beyond READY is HOLD, never replayed.
"""
from __future__ import annotations
import argparse, copy, json, os, shutil
from pathlib import Path
import numpy as np
import torch
import ttm_2x2_colab_runner_candidate as base
import ttm_ac_resume_store as store

ARMS=('A','C')
RUN_ID='TTM_SMALL4M_AC_OBJECTIVE_ONLY_V1'
START,END,BUDGET=1024,1152,4096

def need(ok, code):
    if not ok: raise RuntimeError(code)

def digest(p): return store.sha256_file(p)
def read_json(p): return json.loads(Path(p).read_text('utf-8'))

def check_receipt(path, sha, statuses):
    need(path and sha and Path(path).is_file() and not Path(path).is_symlink(),'MISSING_PINNED_RECEIPT')
    need(digest(path)==sha,'RECEIPT_SHA_MISMATCH')
    need(read_json(path).get('status') in statuses,'RECEIPT_STATUS_NOT_PASS')

def lock_science(a):
    need(a.owner_lock and a.owner_lock_sha,'SCIENCE_NOT_AUTHORIZED_NO_OWNER_LOCK')
    need(Path(a.owner_lock).is_file() and not Path(a.owner_lock).is_symlink(),'OWNER_LOCK_NOT_REGULAR')
    need(digest(a.owner_lock)==a.owner_lock_sha,'OWNER_LOCK_SHA_INVALID')
    lock=read_json(a.owner_lock)
    required={'authorization':'OWNER_APPROVED_TTM_SMALL4M_AC_OBJECTIVE_ONLY_T4_V1',
              'run_id':RUN_ID,'arms':['A','C'],'steps_per_arm':128,'valid_targets_per_step':4096,
              'parent_sha256':base.CHECKPOINT_SHA,'pack_sha256':base.PACK_SHA,
              'no_test':True,'no_q1q2':True,'no_ood':True,
              'free_colab_t4_only':True,'permit_same_run_resume':True}
    need(all(lock.get(k)==v for k,v in required.items()),'WRONG_SCIENCE_CONTRACT')
    need(lock.get('runner_source_sha256')==digest(__file__),'AC_RUNNER_NOT_FROZEN')
    need(lock.get('base_runner_sha256')==digest(base.__file__),'FOUR_ARM_SOURCE_DEPENDENCY_DRIFT')
    need(lock.get('resume_store_sha256')==digest(store.__file__),'RESUME_STORE_DEPENDENCY_DRIFT')
    gates=[('rights',('PASS_OWNER_ATTESTED',)),
           ('reviewer',('PASS_INDEPENDENT_REVIEWER_LOCKED',)),
           ('eval',('PASS_24_PROMPT_BLIND_FREEZE',)),
           ('resume_qa',('PASS_ACTUAL_AC_RESUME_PARITY',)),
           ('t4_smoke',('PASS_T4_FP16_ZERO_SCIENCE_STEP',))]
    for kind,statuses in gates:
        check_receipt(getattr(a,kind+'_receipt'),lock.get(kind+'_receipt_sha256'),statuses)
    need(lock.get('fp16_backoff_amendment')=='OWNER_APPROVED_PRE_SCIENCE_FP16_V2_MAX12_NO_SKIPPED_OPTIMIZER_SCHEDULER_ADVANCE',
         'OWNER_FP16_AMENDMENT_V2_NOT_APPROVED')
    need(lock.get('owner_approved_utc') and lock.get('owner_decision_sha256'),
         'OWNER_DECISION_PROVENANCE_MISSING')
    return lock

def state_dump(model,opt,sch,sampler,scaler,step,history,arm):
    import random
    q=np.random.get_state()
    return {'schema':'ttm.small4m.ac.resume.v1','run_id':RUN_ID,'arm':arm,'step':step,
            'history':history,'model':model.state_dict(),'optimizer':opt.state_dict(),
            'scheduler':sch.state_dict(),'sampler_state':sampler.get_state(),
            'grad_scaler_state':scaler.state_dict(),
            'torch_cpu_rng':torch.get_rng_state(),'torch_cuda_rng':torch.cuda.get_rng_state_all(),
            'python_rng':random.getstate(),
            'numpy_rng':(q[0],q[1].tolist(),int(q[2]),int(q[3]),float(q[4]))}

def restore_arm(p02,parent,state,dev):
    # AdamW.load_state_dict can retain the *exact* source CPU tensor for
    # optimizer.state[p]['step'] (PyTorch policy for non-capturable AdamW).
    # Shallow cp=dict(parent) silently leaks optimizer steps across A and C.
    # Deep-copy the entire parent and every resumed field before constructing
    # each arm, so A, C, and the original step1024 state cannot share storage.
    cp=copy.deepcopy(parent)
    if state is not None:
        need(state.get('schema')=='ttm.small4m.ac.resume.v1','RESUME_STATE_SCHEMA_MISMATCH')
        fields=('model','optimizer','scheduler','sampler_state','grad_scaler_state',
                'torch_cpu_rng','torch_cuda_rng','python_rng','numpy_rng')
        for field in fields:
            need(field in state,'RESUME_STATE_INCOMPLETE')
            cp[field]=copy.deepcopy(state[field])
    model,opt,sch,sampler,scaler=base.clone_parent(p02,cp,dev)
    # Prove the source optimizer step tensors are isolated, not just equal.
    for param_id,source_state in cp['optimizer']['state'].items():
        source_step=source_state.get('step')
        if not torch.is_tensor(source_step): continue
        actual=opt.state_dict()['state'][param_id].get('step')
        need(torch.is_tensor(actual),'ADAMW_STEP_TENSOR_MISSING')
        # PyTorch may alias actual to the DEEP-COPIED local cp tensor. This
        # is safe: only alias to the upstream frozen parent/state is forbidden.
        upstream=(state['optimizer'] if state is not None else parent['optimizer'])
        upstream_step=upstream['state'][param_id]['step']
        need(actual.data_ptr()!=upstream_step.data_ptr(),
             'ADAMW_STEP_STORAGE_ALIAS_UPSTREAM')
    return model,opt,sch,sampler,scaler

def write_once(path,obj):
    with Path(path).open('x',encoding='utf-8') as fp:
        json.dump(obj,fp,sort_keys=True,separators=(',',':'))
        fp.write('\n');fp.flush();os.fsync(fp.fileno())

def run_manifest(root,lock_sha,source_sha,resume):
    m=root/'RUN_MANIFEST.json'
    expected={'run_id':RUN_ID,'arms':['A','C'],'owner_lock_sha256':lock_sha,
              'source_sha256':source_sha,'parent_sha256':base.CHECKPOINT_SHA,
              'pack_sha256':base.PACK_SHA,'checkpoint_interval':store.INTERVAL}
    if resume:
        need(root.is_dir() and m.is_file(),'RESUME_RUN_DIRECTORY_MISSING')
        need(read_json(m)==expected,'RESUME_RUN_MANIFEST_CHANGED')
    else:
        need(not root.exists() and root.parent.is_dir(),'NEW_OUTPUT_MUST_NOT_EXIST')
        root.mkdir(exist_ok=False)
        write_once(m,expected)

def verify_journal(root,last):
    for p in root.iterdir():
        if p.name.startswith(('STEP_BEGIN_','STEP_DONE_')):
            try: step=int(p.stem.rsplit('_',1)[1])
            except (IndexError,ValueError): raise RuntimeError('BAD_STEP_JOURNAL_NAME')
            need(step<=last,'IN_FLIGHT_STEP_AFTER_READY_NO_REPLAY')

def run_arm(root,arm,data,p02,parent,plans,dev,resume,lock_sha,source_sha):
    armdir=root/('ARM_'+arm)
    if not resume: armdir.mkdir(exist_ok=False)
    elif not armdir.exists(): armdir.mkdir(exist_ok=False)
    last,state,receipt=store.load_latest(armdir,RUN_ID,arm,source_sha,base.CHECKPOINT_SHA,lock_sha)
    verify_journal(armdir,last)
    final_path=armdir/'FINAL.json'
    if final_path.exists():
        final=read_json(final_path)
        need(last==END and final.get('ready_checkpoint_sha256')==receipt['checkpoint_sha256']
             and final.get('run_id')==RUN_ID and final.get('arm')==arm,'FINAL_RECEIPT_MISMATCH')
        return final
    model,opt,sch,sampler,scaler=restore_arm(p02,parent,state,dev)
    history=[] if state is None else state['history']
    for step,plan in plans:
        if step<=last: continue
        x,y=base.fixed_batch(data,plan,arm)
        need(int((y!=-100).sum())==BUDGET,'TARGET_COUNT_DRIFT')
        write_once(armdir/f'STEP_BEGIN_{step}.json',{'step':step,'arm':arm,'run_id':RUN_ID})
        # PRE-SCIENCE AMENDMENT V2: same batch, no new sampler draw on skipped
        # GradScaler attempt. Exactly one successful optimizer update/step.
        state_key=next(iter(opt.state))
        skipped=0
        attempts=[]
        while True:
            model.train();opt.zero_grad(set_to_none=True)
            subtotal=0.0
            for partial in base.loss_step(model,x,y,arm,dev,autocast=True):
                scaler.scale(partial).backward()
                subtotal+=float(partial.detach().cpu())
            scaler.unscale_(opt)
            torch.nn.utils.clip_grad_norm_(model.parameters(),1.0)
            before=float(opt.state[state_key]['step'])
            oldscale=float(scaler.get_scale())
            scaler.step(opt);scaler.update()
            after=float(opt.state[state_key]['step'])
            newscale=float(scaler.get_scale())
            attempts.append((oldscale,newscale,before,after))
            if after==before+1.0:
                need(newscale>=oldscale,'SCALER_REDUCED_AFTER_REAL_OPTIMIZER_STEP')
                break
            need(after==before,'OPTIMIZER_STEP_COUNT_DRIFT')
            need(newscale<oldscale,'OPTIMIZER_SKIPPED_WITHOUT_SCALER_BACKOFF')
            skipped+=1
            need(skipped<=12,'HOLD_TOO_MANY_FP16_GRADSCALER_BACKOFFS')
            # Scheduler and science step counters remain unchanged on skip.
        sch.step()
        need(abs(float(opt.param_groups[0]['lr'])-3e-5)<1e-7,'LEARNING_RATE_DRIFT')
        history.append({'step':step,'train_loss':subtotal,'valid_targets':BUDGET,'windows':len(plan),
                        'fp16_scaler_skipped_attempts':skipped,'fp16_scaler_attempts':attempts})
        write_once(armdir/f'STEP_DONE_{step}.json',{'step':step,'arm':arm,'run_id':RUN_ID})
        if step in store.STEPS:
            snapshot=state_dump(model,opt,sch,sampler,scaler,step,history,arm)
            store.save_ready(armdir,step,snapshot,RUN_ID,arm,source_sha,base.CHECKPOINT_SHA,lock_sha)
    last,state,receipt=store.load_latest(armdir,RUN_ID,arm,source_sha,base.CHECKPOINT_SHA,lock_sha)
    need(last==END and len(history)==128,'INCOMPLETE_ARM_HISTORY')
    val=base.eval_original_val_nll(model,data,dev)
    final={'run_id':RUN_ID,'arm':arm,'status':'TRAINED_CHECKPOINT_UNADJUDICATED',
           'step':END,'source_sha256':source_sha,'owner_lock_sha256':lock_sha,
           'ready_checkpoint_sha256':receipt['checkpoint_sha256'],
           'target_exposures':128*BUDGET,'val_report':val}
    write_once(final_path,final)
    return final

def science(a,lock):
    need(torch.cuda.is_available() and torch.cuda.device_count()==1,'SINGLE_T4_REQUIRED')
    need('T4' in torch.cuda.get_device_name(0),'NVIDIA_T4_REQUIRED')
    need(str(torch.__version__)==lock.get('torch_version'),'TORCH_VERSION_NOT_PINNED')
    need(a.output and not Path(a.output).is_symlink(),'OUTPUT_MISSING_OR_SYMLINK')
    root=Path(a.output)
    need(root.parent.is_dir() and shutil.disk_usage(root.parent).free>=2*1024**3,
         'DISK_SPACE_BELOW_2GIB')
    cp=base.check_input(a.pack,a.manifest,a.checkpoint)
    p02=base.load_model_source(a.p02)
    need(digest(a.p02)==base.P02_SHA,'P02_SOURCE_SHA_DRIFT')
    source_sha=digest(__file__)
    run_manifest(root,a.owner_lock_sha,source_sha,a.resume)
    with np.load(a.pack,allow_pickle=False) as z:
        data={name:z[name] for name in ('train_x','train_y','train_count','train_story_index',
                                        'val_x','val_y','val_count','val_story_index')}
    plans=base.plan_steps(data['train_count'].astype(np.int64),
                          data['train_story_index'].astype(np.int64),cp)
    dev=torch.device('cuda')
    for arm in ARMS:
        # Both A/C must begin from the SAME immutable step1024 parent.
        need(all(float(v['step'])==START for v in cp['optimizer']['state'].values()),
             'SOURCE_PARENT_ADAMW_STEP_CHANGED_BEFORE_ARM')
        result=run_arm(root,arm,data,p02,cp,plans,dev,a.resume,a.owner_lock_sha,source_sha)
        need(all(float(v['step'])==START for v in cp['optimizer']['state'].values()),
             'SOURCE_PARENT_ADAMW_STEP_CHANGED_AFTER_ARM')
        print('AC_ARM_FINAL_RECEIPT=',arm,result['status'])
    print('AC_TWO_ARMS_UNADJUDICATED_REQUIRES_INDEPENDENT_SCIENCE_AND_QUALITY_REVIEW')

def source_qa():
    need(ARMS==store.ARMS and store.STEPS==(1056,1088,1120,1152),
         'AC_READY_CONFIG_MISMATCH')
    need(len(base.CHECKPOINT_SHA)==64 and len(base.PACK_SHA)==64,'FROZEN_PINS_MISSING')
    need(base.RUN_ID!=RUN_ID,'HISTORICAL_RUN_ID_REUSE')
    return {'status':'PASS_SOURCE_ONLY_NO_MODEL_FORWARD','arms':list(ARMS),
            'steps_per_arm':128,'targets_per_arm':524288,'ready_steps':list(store.STEPS),
            'training':False,'inference':False,'actual_gpu_resume_parity':'NOT_EXECUTED',
            'fp16_policy':'AMENDMENT_V2_MAX12_ONE_ACTUAL_ADAMW_UPDATE_PER_LOCKED_STEP',
            'amendment_owner_approval':'NOT_GRANTED_BY_SOURCE_QA'}

def main():
    p=argparse.ArgumentParser()
    p.add_argument('--mode',choices=['source-qa','science'],default='source-qa')
    p.add_argument('--pack');p.add_argument('--manifest');p.add_argument('--checkpoint')
    p.add_argument('--p02');p.add_argument('--output');p.add_argument('--resume',action='store_true')
    p.add_argument('--owner-lock');p.add_argument('--owner-lock-sha')
    for label in ('rights','reviewer','eval','resume_qa','t4_smoke'):
        p.add_argument('--'+label.replace('_','-')+'-receipt',dest=label+'_receipt')
    a=p.parse_args()
    if a.mode=='source-qa':
        print(json.dumps(source_qa(),sort_keys=True))
        return
    lock=lock_science(a)
    need(all([a.pack,a.manifest,a.checkpoint,a.p02,a.output]),'SCIENCE_INPUTS_MISSING')
    science(a,lock)

if __name__=='__main__': main()
