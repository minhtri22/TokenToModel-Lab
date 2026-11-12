#!/usr/bin/env python3
"""Independent scoped AST + fake-GradScaler audit. NO real TRAIN, GPU or science."""
from __future__ import annotations
import argparse, ast, hashlib, json, tempfile
from pathlib import Path
from types import SimpleNamespace
import numpy as np

CANDIDATE_GIT_BLOB='6bbd8b7190f843685197f6203b574a6c76977f3a'
def check(cond,code):
    if not cond: raise AssertionError(code)
def git_blob(b):
    return hashlib.sha1(f'blob {len(b)}\0'.encode('ascii')+b).hexdigest()
def static_qa(tree,source):
    assigns={t.id:n.value for n in tree.body if isinstance(n,ast.Assign)
             for t in n.targets if isinstance(t,ast.Name)}
    check(ast.literal_eval(assigns['ARMS'])==('A','C'),'ARMS_CHANGED')
    check(ast.literal_eval(assigns['RUN_ID'])=='TTM_SMALL4M_AC_OBJECTIVE_ONLY_V1','RUN_ID_CHANGED')
    fs={n.name:n for n in tree.body if isinstance(n,ast.FunctionDef)}
    required=('run_arm','science','lock_science','run_manifest','restore_arm','source_qa','main')
    check(all(x in fs for x in required),'MISSING_SOURCE_FUNCTION')
    run=ast.get_source_segment(source,fs['run_arm'])
    lock=ast.get_source_segment(source,fs['lock_science'])
    main=ast.get_source_segment(source,fs['main'])
    manifest=ast.get_source_segment(source,fs['run_manifest'])
    for fragment in (
        'base.fixed_batch(data,plan,arm)',
        'base.loss_step(model,x,y,arm,dev,autocast=True)',
        'need(int((y!=-100).sum())==BUDGET',
        "before=float(opt.state[state_key]['step'])",
        "after=float(opt.state[state_key]['step'])",
        'if after==before+1.0:',
        'need(skipped<=12',
        "need(after==before,'OPTIMIZER_STEP_COUNT_DRIFT')",
        "need(newscale<oldscale,'OPTIMIZER_SKIPPED_WITHOUT_SCALER_BACKOFF')",
        "'fp16_scaler_skipped_attempts':skipped",
        "'fp16_scaler_attempts':attempts"
    ):
        check(fragment in run,'MISSING_CRITICAL_FP16_CONTRACT:'+fragment)
    check(run.index('if after==before+1.0:')<run.index('sch.step()'),'EARLY_SCHEDULER')
    for fragment in ('PASS_ACTUAL_AC_RESUME_PARITY','PASS_INDEPENDENT_REVIEWER_LOCKED',
                     'PASS_OWNER_ATTESTED','OWNER_FP16_AMENDMENT_V2_NOT_APPROVED'):
        check(fragment in lock,'REMOVED_OWNER_OR_REVIEWER_GATE:'+fragment)
    check('lock_science(a)' in main,'SCIENCE_ENTRY_NOT_GATED')
    check("'source_sha256':source_sha" in manifest,'SOURCE_SHA_NOT_SCOPED')
    check("'owner_lock_sha256':lock_sha" in manifest,'OWNER_LOCK_SHA_NOT_SCOPED')
    check('for arm in ARMS:' in ast.get_source_segment(source,fs['science']),'SCIENCE_ARM_LOOP_CHANGED')
    return fs['run_arm']

class Loss:
    def detach(self):return self
    def cpu(self):return self
    def __float__(self):return .25
    def backward(self):pass
class Model:
    def train(self):pass
    def parameters(self):return ()
class Optim:
    def __init__(self):
        self.state={'p':{'step':1024.}}
        self.param_groups=[{'lr':3e-5}]
        self.zero_calls=0
    def zero_grad(self,**kw):self.zero_calls+=1
class Scheduler:
    def __init__(self):self.calls=0
    def step(self):self.calls+=1
class Scaler:
    def __init__(self,events):
        self.events=list(events);self.pos=0;self.scale_now=65536.;self.current=None
    def scale(self,x):return x
    def unscale_(self,*args):pass
    def get_scale(self):return self.scale_now
    def step(self,opt):
        check(self.pos<len(self.events),'FAKE_EVENT_QUEUE_EXHAUSTED')
        self.current=self.events[self.pos];self.pos+=1
        if self.current in ('success','down_on_success'):opt.state['p']['step']+=1
        if self.current=='double_update':opt.state['p']['step']+=2
    def update(self):
        if self.current in ('skip','down_on_success'):self.scale_now/=2
        self.current=None
class Store:
    STEPS=(1025,)
    def __init__(self):self.reads=0;self.saves=0
    def load_latest(self,*args):
        self.reads+=1
        if self.reads==1:return 1024,None,None
        return 1025,{'history':[]},{'checkpoint_sha256':'synthetic'}
    def save_ready(self,*args):self.saves+=1

def run_one(run_arm_ast,events):
    opt=Optim();sched=Scheduler();model=Model();scaler=Scaler(events);store=Store()
    def need(ok,why):
        if not ok:raise RuntimeError(why)
    def fixed_batch(*args):
        return np.zeros((1,1),dtype=np.int64),np.zeros((1,1),dtype=np.int64)
    def loss_step(*args,**kw):yield Loss()
    def write_once(p,content):
        p=Path(p);check(not p.exists(),'OVERWRITE');p.write_text(json.dumps(content),encoding='utf-8')
    namespace={
        'RUN_ID':'TTM_SMALL4M_AC_OBJECTIVE_ONLY_V1','END':1025,'BUDGET':1,
        'store':store,'Path':Path,'need':need,'write_once':write_once,
        'verify_journal':lambda *a:None,'restore_arm':lambda *a:(model,opt,sched,None,scaler),
        'state_dump':lambda *a:{'scope':'fake'},
        'base':SimpleNamespace(CHECKPOINT_SHA='a'*64,fixed_batch=fixed_batch,loss_step=loss_step,
                               eval_original_val_nll=lambda *a:{}),
        'torch':SimpleNamespace(nn=SimpleNamespace(utils=SimpleNamespace(
            clip_grad_norm_=lambda *a:None)))
    }
    module=ast.fix_missing_locations(ast.Module(body=[run_arm_ast],type_ignores=[]))
    exec(compile(module,'<source-exact-run-arm-ast>','exec'),namespace)
    with tempfile.TemporaryDirectory(prefix='ttm_ac_v2_fake_') as dirname:
        try:
            namespace['run_arm'](Path(dirname),'A',{},None,None,
                                 [(1025,[(0,0,1)])],None,False,'a'*64,'b'*64)
            err='UNEXPECTED_SUCCESS'
        except RuntimeError as ex:
            err=str(ex)
        completed=(Path(dirname)/'ARM_A'/'STEP_DONE_1025.json').exists()
    return {'error':err,'scheduler_steps':sched.calls,
            'optimizer_step':opt.state['p']['step'],'scaler_attempts':scaler.pos,
            'zero_calls':opt.zero_calls,'journal_done':completed}

def main():
    ap=argparse.ArgumentParser()
    ap.add_argument('--candidate',required=True,type=Path)
    ap.add_argument('--out',required=True,type=Path)
    args=ap.parse_args()
    raw=args.candidate.read_bytes()
    check(git_blob(raw)==CANDIDATE_GIT_BLOB,'CANDIDATE_GIT_BLOB_MISMATCH')
    source=raw.decode('utf-8')
    run_ast=static_qa(ast.parse(source),source)
    cases=[
      ('success',['success'],'INCOMPLETE_ARM_HISTORY',1,1025.,1,True),
      ('one_skip',['skip','success'],'INCOMPLETE_ARM_HISTORY',1,1025.,2,True),
      ('twelve_skips',['skip']*12+['success'],'INCOMPLETE_ARM_HISTORY',1,1025.,13,True),
      ('thirteen_skips',['skip']*13,'HOLD_TOO_MANY_FP16_GRADSCALER_BACKOFFS',0,1024.,13,False),
      ('skip_without_backoff',['skip_no_backoff'],'OPTIMIZER_SKIPPED_WITHOUT_SCALER_BACKOFF',0,1024.,1,False),
      ('unexpected_double_update',['double_update'],'OPTIMIZER_STEP_COUNT_DRIFT',0,1026.,1,False),
      ('scale_down_despite_update',['down_on_success'],'SCALER_REDUCED_AFTER_REAL_OPTIMIZER_STEP',0,1025.,1,False)
    ]
    records=[]
    for name,events,error,sched,step,n,done in cases:
        observed=run_one(run_ast,events)
        expected={'error':error,'scheduler_steps':sched,'optimizer_step':step,
                  'scaler_attempts':n,'zero_calls':n,'journal_done':done}
        passed=all(observed.get(key)==value for key,value in expected.items())
        records.append({'case':name,'pass':passed,'expected':expected,'observed':observed})
        check(passed,'CASE_FAILED:'+name+':'+json.dumps(observed))
    receipt={'schema':'ttm.small4m.ac.fp16.v2.source_ast_fake_backend_qa.v1',
        'status':'PASS_SCOPED_SOURCE_AST_FAKE_BACKEND_7_OF_7',
        'candidate_git_blob':CANDIDATE_GIT_BLOB,
        'candidate_sha256':hashlib.sha256(raw).hexdigest(),
        'cases':records,'private_train_access':False,'real_gpu_access':False,
        'real_model_forward':False,'ac_science_training':False,
        'actual_t4_resume_parity':'NOT_EXECUTED',
        'owner_science_lock':'NOT_GRANTED','C_minus_A':'NOT_ESTIMABLE'}
    check(not args.out.exists(),'NO_OVERWRITE_RECEIPT_ALREADY_EXISTS')
    args.out.write_text(json.dumps(receipt,sort_keys=True,indent=2)+'\n',encoding='utf-8')
    print('AC_FP16_V2_SOURCE_QA='+receipt['status'])
    print('CANDIDATE_GIT_BLOB='+CANDIDATE_GIT_BLOB)
    print('NO_GPU_NO_TRAINING=TRUE')

if __name__=='__main__': main()
