#!/usr/bin/env python3
"""TTM-Small-4M Q1/Q2, single native Ollama batch; GitHub frozen inputs.
No model creation, training, TEST reading, or automatic replay. Windows Python 3.12.
"""
from __future__ import annotations
import argparse
import hashlib
import importlib.util
import json
import math
import os
from pathlib import Path
import re
import shutil
import socket
import subprocess
import sys
import time
import traceback
from collections import Counter
from datetime import datetime, timezone

ROOT = Path(r'D:\WORK\RESEARCH\TokenToModel-Lab')
BASE = 'b57b44e7287f842e81050c1faee337f636333dd0'
TAG = 'ttm-t5-f32-compat-only-v5final:latest'
MODEL_SHA = '5bdc904e6c51af04a4223219f36e6bc2e687f60fd6e17dc24508f3eb7489e4e5'
EXE_SHA = '14e0fff0449ce3c3a7fe9db8b8b32089274db5f835d4c99f5af7c32dcbf08981'
BPE_SHA = 'cba18e60cee3d08a353ee6d4a451017289e45af7b4b1179c87171b9b78d7dfdc'
V5_SRC_SHA = 'e11e4b3a809fb5da3ea47d960236d2bd0cb721a780b9e3d4c790eb194cc4fdac'
V5_TCP_SHA = '100ca44212c9f2ffb77c93aa11a90fa8f4a67d1b225efb16e888c58680d6f9b7'
V5_RESULT_SHA = '78f77a5d6f9d2829c4914787a875ee44b49d864ad51aad616a06a21ce1ce219d'
STORE_MANIFEST = 'manifests-v2/ollama.com/library/ttm-t5-f32-compat-only-v5final/latest'
INPUTS = ROOT/'tools'/'pilot_q1q2'/'frozen_inputs_20261109'
V5_CODE = ROOT/'tools'/'pilot_t5'/'v5_native_source_20261109'
BPE_CODE = ROOT/'tools'/'pilot_t1t3'/'source_t2'/'ttm_gpt2_bpe2048.py'
BPE_DATA = ROOT/'_tmp'/'ttm_t1_real_source_v1'/'T1_BPE2048_REAL_TRAIN_MANIFEST.json'
V5_RUN = ROOT/'_tmp'/'ttm_t5_ollama_compat_only_single_v5final'
OUT = ROOT/'_tmp'/'ttm_q1q2_ollama_once_v1'
PORT = 12650
MAX_SECONDS = 45*60
MAX_OUTPUT_TOKENS = 3904
MAX_REQUESTS = 74
MODEL_FILES_CAP = 20
PROMPT_LIMIT_TOKENS = 192
Q2_PROMPT_LIMIT_TOKENS = 96


def die(message: str):
    raise RuntimeError(message)


def require(value, message: str):
    if not value:
        die(message)


def digest(p: Path) -> str:
    h=hashlib.sha256()
    with p.open('rb') as f:
        for block in iter(lambda:f.read(1<<20),b''): h.update(block)
    return h.hexdigest()


def read_json(p: Path):
    return json.loads(p.read_text(encoding='utf-8'))


def write_new(p: Path, data):
    p.parent.mkdir(parents=True, exist_ok=True)
    with p.open('x',encoding='utf-8',newline='\n') as f:
        json.dump(data,f,indent=2,sort_keys=True,ensure_ascii=False)
        f.write('\n'); f.flush(); os.fsync(f.fileno())


def reject_reparse(p: Path):
    for q in reversed([p,*p.parents]):
        if not q.exists() and not q.is_symlink(): continue
        attrs=getattr(q.lstat(),'st_file_attributes',0)
        require(not q.is_symlink() and not (attrs&0x400) and
                not (hasattr(q,'is_junction') and q.is_junction()),'REPARSE_DENIED:'+str(q))


def load_fixture():
    lock=read_json(INPUTS/'Q1Q2_LOCK_MANIFEST.json')
    require(lock['schema']=='ttm.q1q2.frozen.inputs.manifest.v1','INPUT_SCHEMA')
    for filename,expected in lock['files_sha256'].items():
        require(re.fullmatch(r'[A-Za-z0-9_.-]+',filename) is not None,'UNSAFE_FIXTURE_NAME')
        require(digest(INPUTS/filename)==expected,'INPUT_HASH_MISMATCH:'+filename)
    p=read_json(INPUTS/'Q1_ORIGINAL_PROMPTS.json')['items']
    config=read_json(INPUTS/'Q1Q2_FROZEN_CONFIG.json')
    q1=read_json(INPUTS/'Q1_FROZEN_48_RUN_MATRIX.json')['rows']
    q2_obj=read_json(INPUTS/'Q2_FROZEN_24_MEASUREMENT_MATRIX.json')
    q2=q2_obj['rows']; warm=q2_obj['warmups']
    prompts={entry['id']:entry['prompt'] for entry in p}
    require(len(prompts)==16 and len(q1)==48 and len(q2)==24 and len(warm)==2,'MATRIX_COUNT')
    require(len({r['run_id'] for r in q1+q2+warm})==74,'DUPLICATE_RUN_ID')
    require(sum(r['num_predict'] for r in q1+q2+warm)==MAX_OUTPUT_TOKENS,'TOTAL_TOKEN_CAP')
    require(set(r['prompt_id'] for r in q1+q2+warm)<=set(prompts),'UNRECOGNIZED_PROMPT_ID')
    require(config['model']['gguf_sha256']==MODEL_SHA and config['model']['tag']==TAG,'MODEL_CONFIG_DRIFT')
    require(all(r['num_ctx']==256 and r['num_predict']==64 for r in q1),'Q1_CONFIG_DRIFT')
    require(all(r['num_ctx'] in (128,256) and r['num_predict']==32 for r in q2+warm),'Q2_CONFIG_DRIFT')
    require(all(r['temperature']==0 for r in q2+warm),'Q2_SAMPLING_DRIFT')
    require(Counter(r['condition'] for r in q1)=={'GREEDY':16,'SAMPLED':32},'Q1_CONDITIONS')
    return prompts,q1,warm,q2


def valid_response(response: dict, model: str, limit: int):
    require(isinstance(response,dict) and response.get('done') is True,'GENERATION_INCOMPLETE')
    require(response.get('model','').lower()==model.lower(),'GENERATED_WRONG_MODEL')
    count=response.get('eval_count')
    require(type(count) is int and 1<=count<=limit,'GENERATED_TOKEN_COUNT_INVALID')
    require(type(response.get('response')) is str,'MISSING_GENERATED_TEXT')
    for key in ('eval_duration','total_duration','prompt_eval_count','prompt_eval_duration','load_duration'):
        require(type(response.get(key)) is int and response[key]>=0,'MISSING_DURATION:'+key)
    require(response['eval_duration']>0,'INVALID_EVAL_DURATION')
    require(response.get('done_reason') in ('stop','length'),'BAD_DONE_REASON')
    return count


def ngram_metrics(token_ids):
    out={'token_count_reencoded':len(token_ids)}
    for n in (2,3):
        grams=list(zip(*(token_ids[i:] for i in range(n))))
        out[f'distinct_{n}']=len(set(grams))/len(grams) if grams else None
    out['repeat_3gram_ratio']=(1-out['distinct_3']) if out['distinct_3'] is not None else None
    return out


def load_module(path: Path, module_name: str):
    # dataclasses in Python 3.12 inspect sys.modules[cls.__module__] at import time.
    # Register BEFORE exec_module; never replace an existing module or leave a
    # half-imported module behind on failure.
    require(re.fullmatch(r'[A-Za-z_][A-Za-z0-9_]*',module_name) is not None,
            'INVALID_DYNAMIC_MODULE_NAME')
    require(module_name not in sys.modules,'MODULE_ALREADY_REGISTERED')
    spec=importlib.util.spec_from_file_location(module_name,path)
    require(spec is not None and spec.loader is not None,'MODULE_LOAD_FAILED')
    mod=importlib.util.module_from_spec(spec)
    sys.modules[module_name]=mod
    try:
        spec.loader.exec_module(mod)
    except BaseException:
        if sys.modules.get(module_name) is mod:
            sys.modules.pop(module_name,None)
        raise
    return mod


def preflight():
    require(sys.platform=='win32' and sys.version_info[:2]==(3,12),'WINDOWS_PYTHON312_REQUIRED')
    require(ROOT.is_dir() and (ROOT/'.git').exists(),'REPO_MISSING')
    for p in (ROOT,ROOT/'_tmp',INPUTS,V5_CODE,V5_RUN,V5_RUN/'models',OUT,BPE_DATA,BPE_CODE):
        reject_reparse(p)
    require(not OUT.exists() and not OUT.is_symlink(),'ONE_SHOT_CONSUMED_NO_RERUN')
    def git(*args):
        proc=subprocess.run(['git','-C',str(ROOT),*args],capture_output=True,text=True,timeout=15)
        require(proc.returncode==0,'GIT_PREFLIGHT_FAILED:'+str(args))
        return proc.stdout.strip()
    require(git('symbolic-ref','--short','HEAD')=='main' and git('rev-parse','HEAD')==BASE,'LOCAL_MAIN_NOT_PINNED')
    require(git('remote','get-url','origin').rstrip('/')=='https://github.com/minhtri22/TokenToModel-Lab.git','ORIGIN_MISMATCH')
    prompts,q1,warm,q2=load_fixture()
    require(digest(V5_CODE/'t5_final_minimal_smoke_v5.py')==V5_SRC_SHA,'V5_SOURCE_DRIFT')
    require(digest(V5_CODE/'t5_native_tcp.py')==V5_TCP_SHA,'V5_TCP_DRIFT')
    require(digest(BPE_DATA)==BPE_SHA,'BPE_MANIFEST_DRIFT')
    require(digest(V5_RUN/'RESULT.json')==V5_RESULT_SHA,'V5_RESULT_DRIFT')
    require(digest(BPE_CODE)== '36d66a1f569b502b7c9def6215fa296de57822146f7845b6d67151982d4ce961','BPE_CODE_DRIFT')
    require(shutil.disk_usage(ROOT).free >= 1<<30,'LOW_DISK_SPACE')
    require(PORT not in (11434,12648,12649),'PORT_NOT_ISOLATED')
    # Known good native V5 code and TCP helpers imported from GitHub main, not from prior temp ZIPs.
    sys.dont_write_bytecode=True
    sys.path.insert(0,str(V5_CODE))
    v5=load_module(V5_CODE/'t5_final_minimal_smoke_v5.py','ttm_q1q2_verified_v5')
    v5.PORT=PORT; v5.HOST=f'127.0.0.1:{PORT}'; v5.API='http://'+v5.HOST; v5.OUT=OUT
    require(v5.MODEL==TAG and v5.GGUF_SHA==MODEL_SHA,'V5_MODEL_PIN_DRIFT')
    require(digest(v5.EXE)==EXE_SHA and digest(v5.GGUF)==MODEL_SHA,'MODEL_OR_EXE_HASH_MISMATCH')
    require(digest(v5.ORIGINAL)==v5.ORIGINAL_SHA and digest(v5.V5B)==v5.V5B_SHA,'PARITY_RECEIPT_DRIFT')
    rr=read_json(V5_RUN/'RESULT.json')
    require(rr.get('create_return_code')==0 and rr.get('readiness',{}).get('ready') is True,'V5_IMPORT_NOT_VERIFIED')
    require(rr.get('shutdown_port_adjudication',{}).get('decision')=='PASS_NO_ACTIVE_SOCKET_AFTER_SHUTDOWN','V5_SHUTDOWN_NOT_VERIFIED')
    manifest=V5_RUN/'models'/STORE_MANIFEST
    require(manifest.is_file() and not manifest.is_symlink(),'V5_MANIFEST_V2_MISSING')
    jm=read_json(manifest)
    require(jm.get('format')=='gguf' and jm.get('schemaVersion')==2,'OLLAMA_MANIFEST_INVALID')
    require(any(x.get('digest')=='sha256:'+MODEL_SHA and x.get('size')==15061376 for x in jm['layers']),'GGUF_MODEL_LAYER_INVALID')
    snap=v5.folder_snapshot(V5_RUN/'models')
    require(snap==rr['models_after_run'] and snap==read_json(V5_RUN/'MODELS_AFTER_CREATE.json'),'STORE_SHA_TREE_CHANGED')
    require(len(snap)<=MODEL_FILES_CAP,'MODEL_STORE_TOO_LARGE')
    require(not v5.tcp_table_observation(PORT)['rows'],'PORT_HAS_TCP_ROWS')
    for family,addr in [(socket.AF_INET,('127.0.0.1',PORT)),(socket.AF_INET6,('::1',PORT))]:
        with socket.socket(family,socket.SOCK_STREAM) as s:
            s.settimeout(.75)
            require(s.connect_ex(addr)!=0,'PORT_ALREADY_CONNECTABLE')
    # Tokenizer loaded only after file pins.
    bpemod=load_module(BPE_CODE,'ttm_q1q2_bpe')
    bpe=bpemod.BPE2048.from_manifest(read_json(BPE_DATA))
    require(len(bpe.tokens)==2048,'BPE_VOCAB_INVALID')
    for prompt in prompts.values():
        require(len(bpe.encode(prompt))<=PROMPT_LIMIT_TOKENS,'Q1_PROMPT_BPE_TOO_LONG')
    for row in warm+q2:
        require(len(bpe.encode(prompts[row['prompt_id']]))<=Q2_PROMPT_LIMIT_TOKENS,'Q2_PROMPT_BPE_TOO_LONG_FOR_128_CONTEXT')
    return v5,bpe,prompts,q1,warm,q2,snap


def request_body(row,prompt):
    options={'num_ctx':row['num_ctx'],'num_predict':row['num_predict'],'temperature':row['temperature']}
    if 'top_p' in row: options['top_p']=row['top_p']
    if row.get('seed') is not None:options['seed']=row['seed']
    return {'model':TAG,'prompt':prompt,'stream':False,'raw':True,'keep_alive':'10m','options':options}


def run_batch():
    v5,bpe,prompts,q1,warm,q2,snap=preflight()
    start=time.monotonic()
    OUT.mkdir(exist_ok=False)
    write_new(OUT/'CLAIM.json',{'schema':'ttm.q1q2.one_shot.claim.v1','created_utc':datetime.now(timezone.utc).isoformat(),
             'main_sha':BASE,'model':TAG,'port':PORT,'max_calls':MAX_REQUESTS,'max_output_tokens':MAX_OUTPUT_TOKENS})
    report={'schema':'ttm.q1q2.single.native.batch.v1','status':'HOLD_UNSTARTED','source_main':BASE,'model':TAG,
            'output_root':str(OUT),'no_training':True,'no_test_access':True,'no_ollama_create':True,
            'planned_calls':MAX_REQUESTS,'complete_calls':0,'completed_tokens':0,'runs':[]}
    proc=None; logfile=None; created=None
    try:
        shutil.copytree(V5_RUN/'models',OUT/'models',symlinks=False)
        require(v5.folder_snapshot(OUT/'models')==snap,'MODEL_STORE_COPY_CHANGED')
        for name in ('home','tmp','home/AppData','home/LocalAppData','home/cache'):
            (OUT/name).mkdir(parents=True,exist_ok=True)
        env=v5.isolated_env(OUT)
        logfile=(OUT/'serve.log').open('x',encoding='utf-8',errors='replace')
        proc=subprocess.Popen([str(v5.EXE),'serve'],cwd=str(OUT),env=env,stdout=logfile,stderr=subprocess.STDOUT,
                              creationflags=subprocess.CREATE_NEW_PROCESS_GROUP)
        report['server_pid']=proc.pid
        readiness=v5.observe_readiness_with_trace(proc,OUT)
        require(readiness.get('ready') is True,'SERVER_READINESS_FAILED')
        created=readiness['identity_creation_date']
        v5.assert_owned_listener(proc,created)
        tags=v5.api_json(v5.API+'/api/tags',timeout=10)
        require(TAG.lower() in [x['name'].lower() for x in tags['models']],'MODEL_TAG_NOT_IN_COPIED_STORE')
        require(v5.folder_snapshot(OUT/'models')==snap,'MODEL_STORE_MODIFIED_BEFORE_BATCH')
        for phase,rows in [('Q1',q1),('Q2_WARMUP',warm),('Q2',q2)]:
            for row in rows:
                require(time.monotonic()-start<=MAX_SECONDS,'BATCH_TIME_BUDGET_EXHAUSTED')
                v5.assert_owned_listener(proc,created)
                body=request_body(row,prompts[row['prompt_id']])
                response=v5.api_json(v5.API+'/api/generate',body=body,timeout=180)
                name=row['run_id']
                require(re.fullmatch(r'[A-Za-z0-9_-]{5,80}',name),'RUN_ID_UNSAFE')
                count=valid_response(response,TAG,row['num_predict'])
                write_new(OUT/'raw'/f'{name}.json',{'run_id':name,'phase':phase,'prompt_id':row['prompt_id'],
                                 'request':body,'response':response})
                text=response['response']
                tokens=bpe.encode(text)
                report['runs'].append({'run_id':name,'phase':phase,'prompt_id':row['prompt_id'],
                     'generated_tokens':count,'reencoded_metrics':ngram_metrics(tokens),
                     'eval_tokens_per_second':count/(response['eval_duration']/1e9),
                     'eval_duration':response['eval_duration'],'total_duration':response['total_duration'],
                     'done_reason':response['done_reason'],'raw_sha256':digest(OUT/'raw'/f'{name}.json')})
                report['complete_calls']+=1; report['completed_tokens']+=count
                print('TTM_Q1Q2_CALL_PASS='+name+' tokens='+str(count),flush=True)
        require(report['complete_calls']==MAX_REQUESTS,'INCOMPLETE_TOTAL_CALLS')
        require(report['completed_tokens']<=MAX_OUTPUT_TOKENS,'TOTAL_OUTPUT_TOKENS_EXCEEDED')
        require(v5.folder_snapshot(OUT/'models')==snap,'MODEL_STORE_CHANGED_AFTER_BATCH')
        report['status']='PASS_EXECUTED_SCOPED'
    except Exception as ex:
        report['status']='HOLD_PARTIAL_NO_AUTOMATIC_RERUN'
        report['failure']={'type':type(ex).__name__,'message':str(ex),'traceback':traceback.format_exc(limit=4)}
    finally:
        if proc is not None:
            try:report['shutdown']=v5.stop_owned_server(proc)
            except Exception as ex: report['shutdown']={'stop_status':'FAILED','message':str(ex)}
        if logfile is not None:logfile.close()
        if proc is not None:
            try:
                post=v5.tcp_table_observation(PORT)
                report['shutdown_port']=v5.classify_shutdown_port_rows(post['rows'],PORT)
            except Exception as ex:report['shutdown_port']={'decision':'HOLD_UNKNOWN','error':str(ex)}
            if report.get('shutdown',{}).get('stop_status') not in ('STOPPED_OWNED_TREE','SERVER_ALREADY_EXITED') or report['shutdown_port']['decision']!='PASS_NO_ACTIVE_SOCKET_AFTER_SHUTDOWN':
                report['status']='HOLD_SHUTDOWN_UNVERIFIED'
        report['completed_utc']=datetime.now(timezone.utc).isoformat()
        report['duration_seconds']=round(time.monotonic()-start,4)
        write_new(OUT/'RESULT.json',report)
    return report


def main():
    ap=argparse.ArgumentParser()
    ap.add_argument('--mode',choices=['qa','preview','execute'],required=True)
    a=ap.parse_args()
    if a.mode=='qa':
        p,q,w,m=load_fixture()
        print('TTM_Q1Q2_OFFLINE_FIXTURES=PASS_16_48_2_24')
        return 0
    if a.mode=='preview':
        preflight()
        print('TTM_Q1Q2_PREVIEW=PASS_NO_CLAIM')
        return 0
    report=run_batch()
    print('TTM_Q1Q2_NATIVE_RESULT='+report['status'])
    print('TTM_Q1Q2_COMPLETED='+str(report['complete_calls']))
    print('TTM_Q1Q2_RESULT_PATH='+str(OUT/'RESULT.json'))
    print('TTM_Q1Q2_NO_AUTOMATIC_RERUN=TRUE')
    return 0 if report['status']=='PASS_EXECUTED_SCOPED' else 4


if __name__=='__main__': sys.exit(main())
