#!/usr/bin/env python3
"""One-shot TTM T2 GPT2-pretokenized TRAIN-only BPE synthetic CPU/GGUF/native F32 QA.

No TinyStories, no scientific TEST, no GPU. The local repository is read-only.
The P02 module is imported ONLY after checking its exact Git blob.
"""
from __future__ import annotations
import argparse
import hashlib
import importlib.util
import json
import math
import os
from pathlib import Path
import subprocess
import sys
import time
import traceback

MAIN='1a9d8cba56564d6d36257fe95c34f2fd52c4f48a'
LLAMA='372dc5ca157276beb6c67b2e92477e8d662e964a'
P02='9762343e06cf800b50574c2871ae1ed58537fb18'
V3_SHA='577a063bd75ec5fe1dea4ad57e0826dffa8a2a99d7ca7327bffd2fee01d5ff1d'
FROZEN_FIXTURE_SHA='5a4ba58db3ad7c1ad0a7c6a790c08184d43c1e3a081ad2dcaf2d4c3b9dbeb9f2'
SYNTHETIC_MANIFEST_SHA='e85028842955334cad014d6f1365f95d79ec953f7cab3a0a2f75ded83bcb1a08'
V5B_PROBE_SHA='080c096d52448f665df43ebc962d7a62b17a0781326bc6358e8535d25f37c963'
V5B_REPORT_SHA='1c2e9e67340ba30c00396af2db707a81cb5bbe8e487ebf5d5dfec91fe05c95bb'
DLLS={
 'ggml-base.dll':'d8c7b4c509748292670e9720c2676c918262a1ce4782cbb34627c595298541f3',
 'ggml-cpu.dll':'fae303eda4b1a8c93aaf61be330696662752a817204be88944454d0255e2c434',
 'ggml.dll':'a47e350ea98666a781208d11d2d820e14c6ae82b9bb7c5c15193342030528f9f',
 'llama.dll':'fff1f9ef4fc40c0946bf9be229d9eddeb06060b05496527272b64cd9ec0f9859'
}
DIRECTORY_NAME='f32_pretok_trainonly_v1'
REPORT_NAME='TTM_T2_F32_GPT2_PRETOKENIZER_INTEGRATED_QA.json'


def sha_file(path:Path)->str:
    h=hashlib.sha256()
    with path.open('rb') as f:
        for block in iter(lambda:f.read(1<<20),b''):
            h.update(block)
    return h.hexdigest()


def native(argv,timeout=90,env=None):
    return subprocess.run(argv,stdout=subprocess.PIPE,stderr=subprocess.PIPE,
                          encoding='utf-8',errors='replace',shell=False,timeout=timeout,env=env)


def verify(repo:Path,work:Path,v3:Path,src:Path):
    if os.name!='nt':
        raise ValueError('WINDOWS_ONLY_FOR_NATIVE_RUNNING')
    if str(repo).lower().replace('/','\\')!=r'd:\work\research\tokentomodel-lab':
        raise ValueError('TTM_REPOSITORY_SCOPE_WRONG')
    if work!=repo/'_tmp'/'ttm_t2':
        raise ValueError('TTM_TMP_SCOPE_WRONG')
    if not src.is_dir() or src.is_symlink():
        raise ValueError('TTM_SOURCE_FOLDER_INVALID')
    def git(cwd,*args):
        p=native(['git','-C',str(cwd),*args])
        if p.returncode:raise ValueError('GIT_COMMAND_FAILED:'+p.stderr[-400:])
        return p.stdout.strip()
    if git(repo,'rev-parse','--show-toplevel').lower().replace('/','\\') != str(repo).lower().replace('/','\\'):
        raise ValueError('WRONG_GIT_TOP')
    if git(repo,'remote','get-url','origin')!='https://github.com/minhtri22/TokenToModel-Lab.git':
        raise ValueError('ORIGIN_URL_WRONG')
    if git(repo,'symbolic-ref','--short','HEAD')!='main':
        raise ValueError('LOCAL_CURRENT_BRANCH_NOT_MAIN')
    if git(repo,'rev-parse','HEAD')!=MAIN or git(repo,'rev-parse','refs/remotes/origin/main')!=MAIN:
        raise ValueError('LOCAL_MAIN_OR_ORIGIN_SHA_DRIFT')
    if git(repo,'status','--porcelain','--untracked-files=no'):
        raise ValueError('LOCAL_REPO_TRACKED_DIRTY')
    if git(work/'llama.cpp','rev-parse','HEAD')!=LLAMA:
        raise ValueError('LLAMA_CPP_SHA_DRIFT')
    h=repo/'src/p02/transformer_core.py'
    raw=h.read_bytes()
    if hashlib.sha1(b'blob '+str(len(raw)).encode()+b'\x00'+raw).hexdigest()!=P02:
        raise ValueError('P02_SOURCE_BLOB_DRIFT')
    helper=v3/'t2_gguf_cpu.py'
    if sha_file(helper)!=V3_SHA:
        raise ValueError('V3_HELPER_PIN_MISMATCH')
    fixture=src/'TTM_T2_F32_NEW_FIXTURES_FROZEN_20261108.json'
    if sha_file(fixture)!=FROZEN_FIXTURE_SHA:
        raise ValueError('FROZEN_FIXTURE_SHA_MISMATCH')
    if not (work/'v5b_technical'/'TTM_T2_V5B_UTF8_AND_F16_MIXED_DIAGNOSTIC.json').is_file():
        raise ValueError('FROZEN_V5B_REPORT_MISSING')
    if sha_file(work/'v5b_technical'/'TTM_T2_V5B_UTF8_AND_F16_MIXED_DIAGNOSTIC.json')!=V5B_REPORT_SHA:
        raise ValueError('FROZEN_V5B_REPORT_SHA_MISMATCH')
    probe=work/'v5b_technical'/'build'/'Release'/'ttm_t2_v5_probe.exe'
    if sha_file(probe)!=V5B_PROBE_SHA:
        raise ValueError('FROZEN_V5B_PROBE_SHA_MISMATCH')
    dllpath=work/'build'/'bin'/'Release'
    for name,expected in DLLS.items():
        if sha_file(dllpath/name)!=expected:
            raise ValueError('FROZEN_DLL_SHA_MISMATCH:'+name)
    out=work/DIRECTORY_NAME
    if out.exists():
        raise FileExistsError('TTM_F32_PRETOK_ONE_SHOT_ALREADY_STARTED_NO_RERUN')
    return helper,fixture,probe,dllpath,out


def load_v3(path:Path):
    spec=importlib.util.spec_from_file_location('ttm_pinned_v3_exporter',path)
    mod=importlib.util.module_from_spec(spec)
    assert spec.loader
    sys.modules[spec.name]=mod
    spec.loader.exec_module(mod)
    if mod.PIN_P02_BLOB!=P02 or mod.PIN_LLAMA!=LLAMA:
        raise ValueError('UPSTREAM_HELPER_DERIVED_PINS_MISMATCH')
    return mod


def export_f32_with_tokenizer(out:Path,model,bpe,v3):
    import torch
    mapped=v3.tensor_map(model.state_dict())
    tokens,merges=bpe.gguf_token_merges()
    if len(tokens)!=2048 or len(merges)!=1791:
        raise ValueError('TOKENIZER_EXPORT_INVALID')
    meta=v3.build_metadata(tokens,merges)
    meta['general.name']='TTM-T2-F32-GPT2-PRETOK-TRAIN-ONLY-SYNTHETIC-NOT-TRAINED'
    meta['general.file_type']=0
    if meta['tokenizer.ggml.pre']!='gpt-2':
        raise ValueError('GPT2_PRETOKENIZATION_METADATA_CHANGED')
    data=[]
    offset=0
    desc=b''
    import struct
    for name,tensor in mapped.items():
        array=tensor.detach().cpu().float().numpy().astype('<f4',copy=False)
        raw=array.tobytes(order='C')
        desc+=v3.packstr(name)+struct.pack('<I',array.ndim)
        desc+=struct.pack('<'+'Q'*array.ndim,*reversed(array.shape))
        desc+=struct.pack('<IQ',v3.F32,offset)
        data.append(raw)
        offset=v3.align_up(offset+len(raw))
    header=struct.pack('<4sIQQ',v3.MAGIC,v3.VERSION,len(data),len(meta))
    for key,value in meta.items():
        kind,payload=v3.packvalue(value)
        header+=v3.packstr(key)+struct.pack('<I',kind)+payload
    header+=desc
    with out.open('xb') as f:
        f.write(header)
        f.write(b'\x00'*(v3.align_up(f.tell())-f.tell()))
        for raw in data:
            f.write(raw)
            f.write(b'\x00'*(v3.align_up(len(raw))-len(raw)))
    qa=v3.assert_readback(model,out,'f32')
    readmeta, tensors,_=v3.parse_gguf(out)
    if readmeta['tokenizer.ggml.tokens']!=tokens or readmeta['tokenizer.ggml.merges']!=merges:
        raise ValueError('TOKENIZER_GGUF_READBACK_FAILED')
    if len(tensors)!=52 or qa['max_abs_weight_error']!=0:
        raise ValueError('GGUF_WEIGHT_READBACK_FAILED')
    return {'sha256':sha_file(out),'size_bytes':out.stat().st_size,
            'tensor_count':len(tensors),'max_abs_weight_error':qa['max_abs_weight_error'],
            'bpe_manifest_sha256':bpe.manifest()['manifest_sha256']}


def run_probe(probe:Path,gguf:Path,cmdargs:list[str],env):
    r=native([str(probe),str(gguf),*cmdargs],timeout=150,env=env)
    if r.returncode:
        raise RuntimeError('PINNED_NATIVE_PROBE_EXIT='+str(r.returncode)+' STDERR='+r.stderr[-1400:])
    try:return json.loads(r.stdout)
    except json.JSONDecodeError as e:raise RuntimeError('NATIVE_PROBE_INVALID_JSON') from e


def perform(repo:Path,work:Path,src:Path,helper:Path,fixture:Path,probe:Path,dllpath:Path,out:Path):
    # One and only one scoped output directory. Even an interrupted run is consumed.
    out.mkdir(parents=True,exist_ok=False)
    state={'schema':'ttm.t2.gpt2.pretok.trainonly.f32.integrated.v1',
           'status':'STOP_INCOMPLETE','science_executed':False,'gpu_used':False,
           'train_data':'SYNTHETIC_TRAIN_FIXTURE_ONLY_NOT_TINYSTORIES',
           'p02_git_blob':P02,'llama_sha':LLAMA,'fixture_sha256':FROZEN_FIXTURE_SHA,
           'v5b_probe_sha256':V5B_PROBE_SHA,'started_at_unix':int(time.time()),
           'f32':{},'tokenizer':{},'numeric':{},'negative_checks':{}}
    report=out/REPORT_NAME
    try:
        import numpy as np
        import torch
        import regex
        if regex.__version__!='2026.5.9':
            raise RuntimeError('REGEX_VERSION_NOT_PINNED:'+regex.__version__)
        if torch.version.cuda is not None or torch.cuda.is_available():
            # This guard intentionally requires CPU-only PyTorch.
            raise RuntimeError('GPU_TORCH_NOT_ALLOWED')
        sys.path.insert(0,str(src))
        sys.path.insert(0,str(helper.parent))
        from ttm_gpt2_bpe2048 import (train_only, synthetic_train_stories,Story,BPE2048,
                                       canonical_bytes,sha,EOS_ID,pretok)
        v3=load_v3(helper)
        stories=synthetic_train_stories()
        # Fully attest no VAL/TEST ever enters the BPE fitter.
        state['negative_checks']['reject_VAL']=False
        state['negative_checks']['reject_TEST']=False
        state['negative_checks']['reject_wrong_source']=False
        for wrong,label in [('VAL','reject_VAL'),('TEST','reject_TEST')]:
            bad=list(stories)
            bad[0]=Story(bad[0].story_id,bad[0].text,wrong,bad[0].source)
            try:train_only(bad,'SYNTHETIC_TRAIN_FIXTURE')
            except ValueError as ex:state['negative_checks'][label]='TRAIN_ONLY_GATE_REJECTED_VAL_TEST' in str(ex)
        bad=list(stories); bad[0]=Story(bad[0].story_id,bad[0].text,'TRAIN','TinyStories-valid.txt')
        try:train_only(bad,'SYNTHETIC_TRAIN_FIXTURE')
        except ValueError as ex:state['negative_checks']['reject_wrong_source']='TRAIN_ONLY_SOURCE_BOUNDARY_VIOLATION' in str(ex)
        if not all(state['negative_checks'].values()):
            raise RuntimeError('TRAIN_ONLY_NEGATIVE_CHECK_FAILED')
        t0=time.monotonic()
        bpe=train_only(stories,'SYNTHETIC_TRAIN_FIXTURE')
        state['tokenizer']['fit_seconds']=round(time.monotonic()-t0,3)
        man=bpe.manifest()
        if man['manifest_sha256']!=SYNTHETIC_MANIFEST_SHA:
            raise RuntimeError('DETERMINISTIC_TRAIN_MANIFEST_MISMATCH')
        (out/'BPE_TRAIN_SYNTHETIC_ONLY_MANIFEST.json').write_bytes(canonical_bytes(man)+b'\n')
        restored=BPE2048.from_manifest(json.loads((out/'BPE_TRAIN_SYNTHETIC_ONLY_MANIFEST.json').read_text('utf-8')))
        if restored.tokens!=bpe.tokens or restored.pairs!=bpe.pairs:
            raise RuntimeError('TOKENIZER_MANIFEST_RELOAD_NOT_IDENTICAL')
        state['tokenizer']['manifest_sha256']=sha_file(out/'BPE_TRAIN_SYNTHETIC_ONLY_MANIFEST.json')
        state['tokenizer']['vocab_count']=len(bpe.tokens)
        state['tokenizer']['merges_count']=len(bpe.pairs)
        cases=json.loads(fixture.read_text('utf-8'))
        txt=cases['tokenizer_text_cases'];nums=cases['numeric_id_cases']
        if len(txt)!=20 or len(nums)!=10 or any(not c.get('text') for c in txt):
            raise RuntimeError('FROZEN_FIXTURES_COUNT_INVALID')
        for entry in txt:
            text=entry['text']
            if bpe.decode(bpe.encode(text))!=text or ''.join(pretok(text))!=text:
                raise RuntimeError('UTF8_ROUNDTRIP_LOCAL_FAILED:'+entry['id'])
        try:bpe.decode([2048])
        except ValueError as e:state['negative_checks']['reject_unknown_token_id']='TOKEN_ID_OUT_OF_RANGE' in str(e)
        try:bpe.decode([EOS_ID])
        except ValueError as e:state['negative_checks']['reject_EOS_decode']='EOS_IN_TEXT_DECODE' in str(e)
        if not all(state['negative_checks'].values()):
            raise RuntimeError('NEGATIVE_LOCAL_QA_NOT_PASS')
        model=v3.load_model(repo)
        gguf=out/'ttm_f32_gpt2_pretok_synthetic.gguf'
        state['f32']=export_f32_with_tokenizer(gguf,model,bpe,v3)
        env=os.environ.copy()
        env['PATH']=str(dllpath)+os.pathsep+env.get('PATH','')
        env['CUDA_VISIBLE_DEVICES']=''
        env['OMP_NUM_THREADS']='1'
        token_mismatches=[]
        for item in txt:
            inp=item['text']
            got=run_probe(probe,gguf,['--tokenize-hex',inp.encode('utf-8').hex()],env)['tokens']
            expected=bpe.encode(inp)
            if got!=expected:
                token_mismatches.append({'case':item['id'],'text_repr':repr(inp),
                                         'expected':expected,'got':got})
        state['tokenizer']['native_cases']=len(txt)
        state['tokenizer']['mismatches']=token_mismatches
        state['tokenizer']['pass']=not token_mismatches
        numeric=[]
        worst=0.0
        max_tie=0
        for item in nums:
            ids=item['ids']
            if not ids or len(ids)>256 or any(i<0 or i>2047 for i in ids):
                raise ValueError('BAD_NUMERIC_IDS')
            with torch.inference_mode():
                ref=model(torch.tensor([ids],dtype=torch.long))[0][0,-1].cpu().numpy()
            got=np.asarray(run_probe(probe,gguf,['--ids',','.join(map(str,ids))],env)['logits'],dtype='float64')
            if got.shape!=(2048,) or not np.isfinite(got).all():
                raise RuntimeError('NATIVE_LOGIT_SHAPE_OR_FINITE_INVALID')
            err=float(np.abs(got-ref.astype('float64')).max())
            mismatch=int(got.argmax()!=ref.argmax())
            worst=max(worst,err)
            max_tie+=mismatch
            numeric.append({'case':item['id'],'max_abs_diff':err,'top1_mismatch':bool(mismatch)})
        state['numeric']={'native_cases':len(nums),'worst_abs_error':worst,
                          'allowed_max_abs_error':0.001,'top1_mismatch_count':max_tie,
                          'cases':numeric,'pass':worst<=0.001 and max_tie==0}
        state['status']='PASS_F32_INTEGRATED_TECHNICAL_ONLY' if state['tokenizer']['pass'] and state['numeric']['pass'] else 'FAIL_F32_INTEGRATED_PARITY'
    except Exception as e:
        state['status']='STOP_RUNTIME_OR_ARTIFACT'
        state['error']={'message':str(e)[-2500:],'traceback_tail':traceback.format_exc()[-3500:]}
    finally:
        state['finished_at_unix']=int(time.time())
        with report.open('x',encoding='utf-8',newline='\n') as f:
            json.dump(state,f,indent=2,ensure_ascii=False,sort_keys=True)
            f.write('\n')
        print('TTM_T2_F32_REPORT='+str(report),flush=True)
        print('TTM_T2_F32_REPORT_SHA256='+sha_file(report),flush=True)
        print('TTM_T2_F32_VERDICT='+state['status'],flush=True)
        print('TTM_T2_F32_TOKENIZER='+str(state['tokenizer'].get('pass')),flush=True)
        print('TTM_T2_F32_LOGITS='+str(state['numeric'].get('pass')),flush=True)
        if state.get('error'):print('TTM_T2_F32_ERROR='+state['error']['message'][-400:],flush=True)
    return 0 if state['status']=='PASS_F32_INTEGRATED_TECHNICAL_ONLY' else 2


def main():
    parser=argparse.ArgumentParser()
    parser.add_argument('--mode',choices=('preview','execute'),required=True)
    parser.add_argument('--repo',required=True,type=Path)
    parser.add_argument('--work',required=True,type=Path)
    parser.add_argument('--v3-source',required=True,type=Path)
    parser.add_argument('--package',required=True,type=Path)
    a=parser.parse_args()
    repo=a.repo.resolve(strict=True)
    work=a.work.resolve(strict=True)
    v3=a.v3_source.resolve(strict=True)
    src=a.package.resolve(strict=True)
    helper,fixture,probe,dllpath,out=verify(repo,work,v3,src)
    print('TTM_T2_F32_SOURCE_AND_EXISTING_RUNTIME_PINS=PASS_EXACT')
    print('TTM_T2_F32_FROZEN_NEW_FIXTURES_SHA='+FROZEN_FIXTURE_SHA)
    print('TTM_T2_F32_MODE='+a.mode)
    if a.mode=='preview':
        print('TTM_T2_F32_PREVIEW=PASS_READONLY')
        return 0
    return perform(repo,work,src,helper,fixture,probe,dllpath,out)

if __name__=='__main__':sys.exit(main())
