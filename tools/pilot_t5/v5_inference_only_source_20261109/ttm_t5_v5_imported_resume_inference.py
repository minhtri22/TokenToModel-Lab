#!/usr/bin/env python3
"""Inference-only continuation of V5 successful Ollama import, one-shot new workspace.

This DOES NOT rerun the consumed V5 job and does not call Ollama create.
All model bytes are copied from V5's preserved project-local model store.
"""
from __future__ import annotations

import argparse
import hashlib
import importlib
import json
import os
from pathlib import Path
import shutil
import socket
import subprocess
import sys
import traceback
from datetime import datetime, timezone

ROOT = Path(r"D:\WORK\RESEARCH\TokenToModel-Lab")
V5_SRC = ROOT / '_tmp' / 'TTM_T5_OLLAMA_V5_TIMEWAIT_GUARD_20261109'
V5_RUN = ROOT / '_tmp' / 'ttm_t5_ollama_compat_only_single_v5final'
OUT = ROOT / '_tmp' / 'ttm_t5_v5_imported_model_inference_only_v1'
PORT = 12649
HOST = f'127.0.0.1:{PORT}'
API = f'http://{HOST}'
MODEL = 'ttm-t5-f32-compat-only-v5final:latest'
MODEL_MANIFEST_REL = 'manifests-v2/ollama.com/library/ttm-t5-f32-compat-only-v5final/latest'
EXPECTED_SRC_HASH = 'e11e4b3a809fb5da3ea47d960236d2bd0cb721a780b9e3d4c790eb194cc4fdac'
EXPECTED_NATIVE_HASH = '100ca44212c9f2ffb77c93aa11a90fa8f4a67d1b225efb16e888c58680d6f9b7'
EXPECTED_GGUF_HASH = '5bdc904e6c51af04a4223219f36e6bc2e687f60fd6e17dc24508f3eb7489e4e5'
EXPECTED_OLLAMA_HASH = '14e0fff0449ce3c3a7fe9db8b8b32089274db5f835d4c99f5af7c32dcbf08981'
EXPECTED_ORIGINAL_FAIL = 'c61f73216764b8582a5c996e85c59feb55b13496ec0117deb713d9b1843ec8e8'
EXPECTED_V5B_FAIL = 'ac699d4e750037f88bbab776bb42a38079cd82b0a1c2f72385127ac5a36d9375'
EXPECTED_V5_STATUS = 'FAIL_OR_HOLD_COMPATIBILITY_ONLY_NO_RERUN'
GGUF_SIZE = 15061376
TIMEOUT_S = 180
MAX_TOKENS = 32
CONTEXT = 256
PROMPT = 'Once upon a time, a small robot'
SCHEMA = 'ttm.t5.v5.imported_model.inference_only.one_shot.v1'


def now():
    return datetime.now(timezone.utc).isoformat()


def sha(path: Path):
    h = hashlib.sha256()
    with path.open('rb') as fd:
        for part in iter(lambda: fd.read(1024 * 1024), b''):
            h.update(part)
    return h.hexdigest()


def check(ok, message):
    if not ok:
        raise RuntimeError(message)


def write_x(path: Path, data):
    with path.open('x', encoding='utf-8', newline='\n') as fd:
        json.dump(data, fd, indent=2, ensure_ascii=False, sort_keys=True)
        fd.write('\n')
        fd.flush()
        os.fsync(fd.fileno())


def load_json(path: Path):
    with path.open('r', encoding='utf-8') as fd:
        return json.load(fd)


def validate_manifest(content: dict) -> bool:
    if not isinstance(content, dict) or content.get('schemaVersion') != 2 or content.get('format') != 'gguf':
        return False
    layers=content.get('layers')
    if not isinstance(layers,list):return False
    return any(isinstance(x,dict) and x.get('mediaType') == 'application/vnd.ollama.image.model'
               and x.get('digest') == 'sha256:'+EXPECTED_GGUF_HASH
               and x.get('size') == GGUF_SIZE for x in layers)


def load_v5_module():
    # Import only verified, immutable V5 helper functions; NEVER its execute() or main().
    import sys
    original = V5_SRC / 't5_final_minimal_smoke_v5.py'
    native = V5_SRC / 't5_native_tcp.py'
    check(sha(original) == EXPECTED_SRC_HASH, 'V5_SOURCE_HASH_MISMATCH')
    check(sha(native) == EXPECTED_NATIVE_HASH, 'V5_NATIVE_SOURCE_HASH_MISMATCH')
    sys.dont_write_bytecode = True
    sys.path.insert(0, str(V5_SRC))
    v5=importlib.import_module('t5_final_minimal_smoke_v5')
    v5.PORT=PORT
    v5.HOST=HOST
    v5.API=API
    v5.OUT=OUT
    check(v5.MODEL == MODEL and v5.GGUF_SHA == EXPECTED_GGUF_HASH, 'V5_SOURCE_MODEL_ID_MISMATCH')
    return v5


def imported_store_preflight(v5):
    check(sys.platform=='win32' and sys.version_info[:2] == (3,12),'WINDOWS_PYTHON312_REQUIRED')
    check(str(ROOT)==r'D:\WORK\RESEARCH\TokenToModel-Lab' and (ROOT/'.git').exists(), 'REPO_ROOT_INVALID')
    for p in (ROOT, ROOT/'_tmp', V5_SRC, V5_RUN, V5_RUN/'models', OUT,
              v5.EXE, v5.GGUF, v5.ORIGINAL, v5.V5B):
        v5.forbid_reparse(p)
    check((V5_RUN/'CLAIM.json').is_file() and (V5_RUN/'RESULT.json').is_file(), 'V5_PROVENANCE_MISSING')
    check(not OUT.exists() and not OUT.is_symlink(), 'RESUME_ONE_SHOT_CONSUMED_NO_RERUN')
    check(sha(v5.EXE)==EXPECTED_OLLAMA_HASH, 'OLLAMA_EXE_CHANGED')
    check(sha(v5.GGUF)==EXPECTED_GGUF_HASH and v5.GGUF.stat().st_size==GGUF_SIZE,'GGUF_CHANGED')
    check(sha(v5.ORIGINAL)==EXPECTED_ORIGINAL_FAIL and sha(v5.V5B)==EXPECTED_V5B_FAIL,'FROZEN_PARITY_RECEIPT_CHANGED')
    result=load_json(V5_RUN/'RESULT.json')
    claim=load_json(V5_RUN/'CLAIM.json')
    check(claim.get('status') == 'ONE_SHOT_CLAIMED' and claim.get('model') == MODEL,'V5_CLAIM_MISMATCH')
    check(result.get('schema') == 'ttm.t5.ollama.compatibility.project-local.one-shot.v5final','V5_RESULT_SCHEMA')
    check(result.get('status') == EXPECTED_V5_STATUS and result.get('create_return_code') == 0,'V5_IMPORT_NOT_PROVEN')
    check(result.get('readiness',{}).get('ready') is True,'V5_DUAL_ATTESTATION_NOT_PROVEN')
    check(result.get('shutdown',{}).get('stop_status') == 'STOPPED_OWNED_TREE','V5_SHUTDOWN_UNVERIFIED')
    check(result.get('shutdown_port_adjudication',{}).get('decision') == 'PASS_NO_ACTIVE_SOCKET_AFTER_SHUTDOWN','V5_PORT_SHUTDOWN_UNVERIFIED')
    check('generate_completed' not in result.get('stages',{}),'V5_ALREADY_GENERATED')
    store=V5_RUN/'models'
    manifest=store/Path(MODEL_MANIFEST_REL)
    check(manifest.is_file() and not manifest.is_symlink(),'V5_MANIFEST_V2_NOT_PRESENT')
    check(validate_manifest(load_json(manifest)),'V5_MANIFEST_GGUF_DIGEST_MISMATCH')
    before=v5.folder_snapshot(store)
    expected=load_json(V5_RUN/'MODELS_AFTER_CREATE.json')
    check(before==expected and before==result.get('models_after_run'),'V5_STORE_CHANGED_SINCE_RUN')
    check(before.get('blobs/sha256-'+EXPECTED_GGUF_HASH,{}).get('sha256')==EXPECTED_GGUF_HASH,'MODEL_BLOB_SHA_MISMATCH')
    check(len(before)<=20,'UNEXPECTED_STORE_FILES')
    check(not v5.tcp_table_observation(PORT)['rows'],'RESUME_PORT_HAS_TCP_ROWS')
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
        sock.settimeout(.75)
        check(sock.connect_ex(('127.0.0.1',PORT)) != 0,'RESUME_PORT_CONNECTABLE')
    with socket.socket(socket.AF_INET6, socket.SOCK_STREAM) as sock:
        sock.settimeout(.75)
        check(sock.connect_ex(('::1',PORT)) != 0,'RESUME_V6_PORT_CONNECTABLE')
    check(shutil.disk_usage(ROOT).free >= 1024*1024*1024, 'LOW_DISK')
    return {'v5_result_status': result['status'], 'v5_create_return_code': 0,
            'model': MODEL, 'manifest_relative': MODEL_MANIFEST_REL,
            'source_store_file_count': len(before), 'source_store_snapshot': before,
            'original_v5_result_sha256': sha(V5_RUN/'RESULT.json'),
            'no_ollama_create_on_resume': True}


def copy_store_and_verify(v5, evidence):
    original=V5_RUN/'models'
    target=OUT/'models'
    # Destination is new and source evidence is never modified.
    shutil.copytree(original,target,symlinks=False)
    check(v5.folder_snapshot(target)==evidence['source_store_snapshot'],'COPIED_STORE_SHA_MISMATCH')
    check(validate_manifest(load_json(target/MODEL_MANIFEST_REL)),'COPIED_MANIFEST_INVALID')
    write_x(OUT/'IMPORTED_STORE_COPY_VERIFIED.json', {
        'source':str(original),'destination':str(target),
        'same_sha256_tree':True,'source_result_sha256':evidence['original_v5_result_sha256'],
        'file_count':len(evidence['source_store_snapshot'])})


def run_one_shot(v5, evidence):
    OUT.mkdir(exist_ok=False)
    write_x(OUT/'CLAIM.json',{'schema':SCHEMA,'start_utc':now(),'status':'ONE_SHOT_CLAIMED',
                             'port':PORT,'model':MODEL,'source_v5_result_sha256':evidence['original_v5_result_sha256'],
                             'action':'INFERENCE_ONLY_NO_CREATE_NO_RETRAIN'})
    report={'schema':SCHEMA,'status':'HOLD_UNSTARTED','start_utc':now(),'stage':{},
            'v5_source_result_sha256':evidence['original_v5_result_sha256'],
            'model':MODEL,'port':PORT,'max_new_tokens':MAX_TOKENS,
            'no_ollama_create':True,'frozen_parity':'FAIL_7_OF_8_PRESERVED'}
    proc=None
    logfile=None
    try:
        copy_store_and_verify(v5,evidence)
        report['stage']['model_store_cloned_sha_verified']=now()
        for name in ('home','tmp','home/AppData','home/LocalAppData','home/cache'):
            (OUT/name).mkdir(parents=True,exist_ok=True)
        env=v5.isolated_env(OUT)
        logfile=(OUT/'serve.log').open('x',encoding='utf8',errors='replace')
        proc=subprocess.Popen([str(v5.EXE),'serve'],cwd=str(OUT),env=env,
                              stdout=logfile,stderr=subprocess.STDOUT,
                              creationflags=subprocess.CREATE_NEW_PROCESS_GROUP)
        report['server_pid']=proc.pid
        report['stage']['server_started']=now()
        ready=v5.observe_readiness_with_trace(proc,OUT)
        check(ready.get('ready') is True,'READINESS_NOT_ATTESTED')
        v5.assert_owned_listener(proc,ready['identity_creation_date'])
        report['stage']['readiness_done']=now()
        tag_response=v5.api_json(API+'/api/tags',timeout=10)
        check(isinstance(tag_response,dict) and isinstance(tag_response.get('models'),list),'MODEL_TAGS_INVALID')
        tags=[m.get('name','').lower() for m in tag_response['models'] if isinstance(m,dict)]
        check(MODEL.lower() in tags,'IMPORTED_TAG_NOT_VISIBLE_IN_NEW_SERVER')
        check(validate_manifest(load_json(OUT/'models'/MODEL_MANIFEST_REL)),'MODEL_MANIFEST_CHANGED')
        report['stage']['imported_tag_verified']=now()
        response=v5.api_json(API+'/api/generate',body={
            'model':MODEL,'prompt':PROMPT,'raw':True,'stream':False,'keep_alive':0,
            'options':{'num_ctx':CONTEXT,'num_predict':MAX_TOKENS,
                       'temperature':0,'seed':20261108}
        },timeout=TIMEOUT_S)
        write_x(OUT/'GENERATION_RAW_RESPONSE.json',response)
        report['stage']['generate_response_saved']=now()
        v5.assert_owned_listener(proc,ready['identity_creation_date'])
        n=response.get('eval_count')
        check(response.get('done') is True and type(n) is int and 1<=n<=MAX_TOKENS,'INFERENCE_NOT_CONFIRMED_1_TO_32_TOKENS')
        check(response.get('model','').lower()==MODEL.lower(),'INFERENCE_WRONG_MODEL_ID')
        report['status']='PASS_COMPATIBILITY_IMPORT_REUSED_AND_INFERENCE_CONFIRMED'
        report['evaluation']={'generated_tokens':n,'generated_text':response.get('response',''),
                              'done':True,'done_reason':response.get('done_reason')}
    except Exception as exc:
        report['status']='FAIL_OR_HOLD_INFERENCE_ONLY_NO_RERUN'
        report['failure']={'type':type(exc).__name__,'message':str(exc),
                           'traceback':traceback.format_exc(limit=4)}
    finally:
        if proc is not None:
            try:report['shutdown']=v5.stop_owned_server(proc)
            except Exception as exc:report['shutdown']={'status':'HOLD_SHUTDOWN_EXCEPTION','message':str(exc)}
        if logfile is not None:logfile.close()
        if proc is not None:
            if report.get('shutdown',{}).get('stop_status') not in ('STOPPED_OWNED_TREE','SERVER_ALREADY_EXITED'):
                report['status']='HOLD_SHUTDOWN_UNVERIFIED'
            try:
                post=v5.tcp_table_observation(PORT)
                report['shutdown_port_adjudication']=v5.classify_shutdown_port_rows(post['rows'],PORT)
                if report['shutdown_port_adjudication']['decision']!='PASS_NO_ACTIVE_SOCKET_AFTER_SHUTDOWN':
                    report['status']='HOLD_SHUTDOWN_PORT_ACTIVE'
            except Exception as exc:
                report['status']='HOLD_POST_SHUTDOWN_PORT_UNVERIFIED'
                report['shutdown_check_error']=str(exc)
        report['finished_utc']=now()
        write_x(OUT/'RESULT.json',report)
    return report


def main():
    parser=argparse.ArgumentParser()
    parser.add_argument('--mode',choices=['contract','preview','execute'],required=True)
    args=parser.parse_args()
    if args.mode=='contract':
        print('TTM_T5_IMPORTED_MODEL_RESUME=INFERENCE_ONLY')
        print(f'TTM_T5_RESUME_PORT={PORT}')
        print('TTM_T5_RESUME_V5_ORIGINAL=IMMUTABLE')
        return 0
    v5=load_v5_module()
    evidence=imported_store_preflight(v5)
    print('T5_V5_EXISTING_IMPORT=VERIFIED_MANIFEST_V2_GGUF_SHA')
    print('T5_V5_PREVIOUS_RUN=CONSUMED_NO_RERUN')
    print('T5_RESUME_NEW_PORT='+str(PORT))
    if args.mode=='preview':
        print('T5_RESUME_PREVIEW=PASS_READONLY')
        return 0
    print('T5_RESUME_INFERENCE_ONLY=START_EXACT_ONCE')
    report=run_one_shot(v5,evidence)
    print('T5_RESUME_RESULT='+report['status'])
    print('T5_RESUME_RESULT_PATH='+str(OUT/'RESULT.json'))
    print('T5_RESUME_TOKENS='+str(report.get('evaluation',{}).get('generated_tokens','NOT_EXECUTED')))
    print('T5_RESUME_V5_ORIGINAL=NOT_MODIFIED')
    print('T5_RESUME_NO_AUTOMATIC_RERUN=TRUE')
    return 0 if report['status']=='PASS_COMPATIBILITY_IMPORT_REUSED_AND_INFERENCE_CONFIRMED' else 4

if __name__=='__main__':
    sys.exit(main())
