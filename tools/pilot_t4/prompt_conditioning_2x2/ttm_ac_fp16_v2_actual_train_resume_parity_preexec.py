#!/usr/bin/env python3
"""Pre-science T4 P02 actual-TRAIN two-step resume parity; NOT an AC science run.

For A and C, execute the exact optimizer step AST from frozen V2 run_arm,
compare continuous steps 1025/1026 against resume after step1025.
Private QA state exists only in a temporary directory and is deleted;
public-safe receipt is NEVER independent science authorization.
"""
from __future__ import annotations
import argparse, ast, copy, hashlib, json, os, sys, tempfile
from pathlib import Path
import numpy as np
import torch

CANDIDATE_BLOB='6bbd8b7190f843685197f6203b574a6c76977f3a'
def need(cond,code):
    if not cond:raise RuntimeError(code)
def git_blob(raw):return hashlib.sha1(f'blob {len(raw)}\0'.encode()+raw).hexdigest()
def sha(path):
    h=hashlib.sha256()
    with Path(path).open('rb') as fp:
        for block in iter(lambda:fp.read(1024*1024),b''):h.update(block)
    return h.hexdigest()

def exact_step(source,candidate,base):
    tree=ast.parse(source)
    run=next(x for x in tree.body if isinstance(x,ast.FunctionDef) and x.name=='run_arm')
    for_loop=next(x for x in run.body if isinstance(x,ast.For)
                  and isinstance(x.target,ast.Tuple)
                  and any(isinstance(t,ast.Name) and t.id=='step' for t in x.target.elts))
    start=next(i for i,n in enumerate(for_loop.body) if isinstance(n,ast.Assign)
               and any(isinstance(t,ast.Name) and t.id=='state_key' for t in n.targets))
    stop=next(i for i,n in enumerate(for_loop.body) if i>start and isinstance(n,ast.Expr)
              and isinstance(n.value,ast.Call) and isinstance(n.value.func,ast.Attribute)
              and isinstance(n.value.func.value,ast.Name) and n.value.func.value.id=='history')
    body=copy.deepcopy(for_loop.body[start:stop])
    need('if after==before+1.0:' in ast.get_source_segment(source,for_loop)
         and 'need(skipped<=12' in ast.get_source_segment(source,for_loop),
         'FP16_V2_CODE_DRIFT')
    args=ast.arguments(posonlyargs=[],args=[ast.arg(arg=n) for n in
        ('model','opt','sch','scaler','x','y','arm','dev')],
        vararg=None,kwonlyargs=[],kw_defaults=[],kwarg=None,defaults=[])
    returned=ast.Return(value=ast.Tuple(elts=[ast.Name(id=n,ctx=ast.Load()) for n in
        ('subtotal','skipped','attempts')],ctx=ast.Load()))
    fn=ast.FunctionDef(name='real_train_optimizer_step_exact_ast',args=args,
                       body=body+[returned],decorator_list=[],returns=None,
                       type_comment=None,type_params=[])
    mod=ast.fix_missing_locations(ast.Module(body=[fn],type_ignores=[]))
    ns={'base':base,'torch':torch,'need':candidate.need,'BUDGET':candidate.BUDGET}
    exec(compile(mod,'<V2-run-arm-exact-step>','exec'),ns)
    return ns['real_train_optimizer_step_exact_ast'],hashlib.sha256(ast.dump(mod).encode()).hexdigest()

def equivalent(a,b,path='state'):
    if torch.is_tensor(a) and torch.is_tensor(b):
        need(torch.equal(a,b),'TENSOR_DRIFT:'+path)
    elif isinstance(a,dict) and isinstance(b,dict):
        need(a.keys()==b.keys(),'KEYS_DRIFT:'+path)
        for key in a:equivalent(a[key],b[key],path+'.'+str(key))
    elif isinstance(a,(list,tuple)) and isinstance(b,(list,tuple)):
        need(len(a)==len(b),'LENGTH_DRIFT:'+path)
        for i,(x,y) in enumerate(zip(a,b)):equivalent(x,y,path+'['+str(i)+']')
    elif isinstance(a,np.ndarray) and isinstance(b,np.ndarray):
        need(np.array_equal(a,b),'ARRAY_DRIFT:'+path)
    else:need(a==b,'VALUE_DRIFT:'+path)

def pair_check(arm,plans,data,candidate,base,p02,cp,step,device):
    batches=[]
    for _,plan in plans[:2]:
        x,y=base.fixed_batch(data,plan,arm)
        need(int((y!=-100).sum())==4096,'REAL_4096_VALID_TARGETS_CHANGED')
        batches.append((x,y))
    def fresh():return base.clone_parent(p02,cp,device)
    def update(parts,xy):
        subtotal,skipped,attempts=step(parts[0],parts[1],parts[2],parts[4],
                                      xy[0],xy[1],arm,device)
        return {'loss':float(subtotal),'skipped':int(skipped),'attempts':attempts}
    # Uninterrupted parent -> 1025 -> 1026.
    direct=fresh()
    direct_logs=[update(direct,xy) for xy in batches]
    direct_end=candidate.state_dump(*direct,1026,[],arm)
    # Fresh identical parent -> 1025 -> serialize/deserialize -> 1026.
    staged=fresh()
    first=update(staged,batches[0])
    with tempfile.TemporaryDirectory(prefix='TTM_AC_V2_PRIVATE_QA_') as tmp:
        path=Path(tmp)/'real_model_real_train_qa_step1025.pt'
        snapshot=candidate.state_dump(*staged,1025,[],arm)
        with path.open('xb') as fp:
            torch.save(snapshot,fp);fp.flush();os.fsync(fp.fileno())
        digest=sha(path)
        readback=torch.load(path,map_location='cpu',weights_only=True)
        need(readback.get('step')==1025 and readback.get('arm')==arm,
             'RESUME_SNAPSHOT_SCOPE_CHANGED')
    resumed=candidate.restore_arm(p02,cp,readback,device)
    second=update(resumed,batches[1])
    resumed_end=candidate.state_dump(*resumed,1026,[],arm)
    for key in ('model','optimizer','scheduler','sampler_state','grad_scaler_state',
                'torch_cpu_rng','torch_cuda_rng','python_rng','numpy_rng'):
        equivalent(direct_end[key],resumed_end[key],key)
    equivalent(direct_logs[0],first,'step1025')
    equivalent(direct_logs[1],second,'step1026')
    return {'arm':arm,'full_p02_model_and_real_train':True,
            'real_parent_step':1024,'verified_step_pair':[1025,1026],
            'checkpoint_roundtrip_sha256':digest,
            'exact_tensor_optimizer_scheduler_scaler_rng_parity':True,
            'direct_optimizer_updates':2,'resumed_path_optimizer_updates':2,
            'qa_optimizer_updates_total':4,
            'direct_scaler_skipped_attempts':sum(x['skipped'] for x in direct_logs),
            'resumed_scaler_skipped_attempts':first['skipped']+second['skipped'],
            'qa_checkpoint_deleted_after_readback':True}

def main():
    p=argparse.ArgumentParser()
    for name in ('candidate','base','store','p02','pack','manifest','checkpoint','out'):
        p.add_argument('--'+name,required=True,type=Path)
    a=p.parse_args()
    need(not a.out.exists(),'NO_OVERWRITE_EXISTING_RECEIPT')
    need(torch.cuda.is_available() and torch.cuda.device_count()==1
         and 'T4' in torch.cuda.get_device_name(0),'NVIDIA_T4_SINGLE_DEVICE_REQUIRED')
    need(git_blob(a.candidate.read_bytes())==CANDIDATE_BLOB,'SOURCE_BLOB_DRIFT')
    for path in (a.base,a.candidate,a.store):
        if str(path.parent) not in sys.path:sys.path.insert(0,str(path.parent))
    import ttm_2x2_colab_runner_candidate as base
    import ttm_ac_resume_store as store
    import ttm_ac_objective_runner_fp16_backoff_v2_REVIEW_CANDIDATE as candidate
    from real_metadata_preflight import PACK_SHA,MANIFEST_SHA,CHECKPOINT_SHA
    need(sha(a.pack)==PACK_SHA and sha(a.manifest)==MANIFEST_SHA and
         sha(a.checkpoint)==CHECKPOINT_SHA,'TRAIN_PARENT_PRIVATE_INPUT_DRIFT')
    cp=base.check_input(a.pack,a.manifest,a.checkpoint)
    p02=base.load_model_source(a.p02)
    step,step_ast_sha=exact_step(a.candidate.read_text('utf-8'),candidate,base)
    with np.load(a.pack,allow_pickle=False) as z:
        data={k:z[k] for k in ('train_x','train_y','train_count','train_story_index',
                               'val_x','val_y','val_count','val_story_index')}
    plans=base.plan_steps(data['train_count'].astype(np.int64),
                          data['train_story_index'].astype(np.int64),cp)
    need(len(plans)==128 and plans[0][0]==1025 and plans[1][0]==1026,'DRAW_PLAN_DRIFT')
    results=[]
    for arm in ('A','C'):
        torch.cuda.empty_cache()
        results.append(pair_check(arm,plans,data,candidate,base,p02,cp,step,torch.device('cuda')))
    report={'schema':'ttm.small4m.ac.v2.real_train_t4_two_step_parity.preexec.v1',
      'status':'PASS_REAL_P02_T4_REAL_TRAIN_TWO_STEP_RESUME_PARITY_SCOPED',
      'candidate_git_blob':CANDIDATE_BLOB,
      'exact_training_step_ast_sha256':step_ast_sha,
      'checkpoint_parent_sha256':CHECKPOINT_SHA,'train_val_pack_sha256':PACK_SHA,
      'manifest_sha256':MANIFEST_SHA,'torch_version':torch.__version__,
      'device':torch.cuda.get_device_name(0),'arm_results':results,
      'qa_real_train_optimizer_updates':8,'science_optimizer_steps':0,
      'private_train_used_in_ephemeral_QA':True,'test_q1q2_ood_access':False,
      'raw_train_and_QA_checkpoint_published':False,
      'READY_last_full_128_step_resume':'NOT_EXECUTED',
      'independent_actual_science_gate':'PENDING_ADJUDICATION',
      'final24_scoring':'NOT_EXECUTED','C_minus_A':'NOT_ESTIMABLE'}
    with a.out.open('x',encoding='utf-8') as fp:
        json.dump(report,fp,sort_keys=True,indent=2)
        fp.write('\n');fp.flush();os.fsync(fp.fileno())
    print('AC_FP16_V2_ACTUAL_T4_QA='+report['status'])
    print('PRIVATE_TRAIN_QA_UPDATES=8 SCIENCE_UPDATES=0')
    print('ACTUAL_AC_SCIENCE_GATE=PENDING_INDEPENDENT_ADJUDICATION')

if __name__=='__main__':main()
