#!/usr/bin/env python3
"""Independent T1 fitted-tokenizer validation against pinned native llama.cpp F32.
One shot, only after T1 source/split/bpe manifest exists. No held-out TEST text.
"""
import argparse,hashlib,json,os,sys,importlib.util,time,traceback,struct
from pathlib import Path
import numpy as np
import torch
from source_t2.ttm_gpt2_bpe2048 import BPE2048,canonical_bytes,sha
from source_t2.ttm_t2_f32_integrated import run_probe,sha_file
from source_t2 import t2_gguf_cpu as gguf

GGUF_V3_SHA='577a063bd75ec5fe1dea4ad57e0826dffa8a2a99d7ca7327bffd2fee01d5ff1d'
P02_BLOB='9762343e06cf800b50574c2871ae1ed58537fb18'
PROBE_SHA='080c096d52448f665df43ebc962d7a62b17a0781326bc6358e8535d25f37c963'
LLAMA='372dc5ca157276beb6c67b2e92477e8d662e964a'


def export(out,model,bpe):
    mapped=gguf.tensor_map(model.state_dict())
    tokens,merges=bpe.gguf_token_merges()
    if len(tokens)!=2048 or len(merges)!=1791:raise RuntimeError('REAL_BPE_VOCAB_INVALID')
    meta=gguf.build_metadata(tokens,merges)
    meta['general.name']='TTM-small4m-P02-random-weights-real-TRAIN-only-BPE-F32'
    meta['general.file_type']=0
    if meta['tokenizer.ggml.pre']!='gpt-2':raise RuntimeError('BPE_PRETOKENIZER_NOT_GPT2')
    data=[];offset=0;descs=b''
    for name,t in mapped.items():
        a=t.detach().cpu().float().numpy().astype('<f4',copy=False)
        raw=a.tobytes(order='C')
        descs+=gguf.packstr(name)+struct.pack('<I',a.ndim)+struct.pack('<'+'Q'*a.ndim,*reversed(a.shape))+struct.pack('<IQ',gguf.F32,offset)
        data.append(raw);offset=gguf.align_up(offset+len(raw))
    header=struct.pack('<4sIQQ',gguf.MAGIC,gguf.VERSION,len(data),len(meta))
    for name,v in meta.items():
        k,p=gguf.packvalue(v)
        header+=gguf.packstr(name)+struct.pack('<I',k)+p
    header+=descs
    with out.open('xb') as fd:
        fd.write(header);fd.write(b'\x00'*(gguf.align_up(fd.tell())-fd.tell()))
        for raw in data:
            fd.write(raw);fd.write(b'\x00'*(gguf.align_up(len(raw))-len(raw)))
    q=gguf.assert_readback(model,out,'f32')
    md,tensors,_=gguf.parse_gguf(out)
    if md['tokenizer.ggml.tokens']!=tokens or md['tokenizer.ggml.merges']!=merges or len(tensors)!=52 or q['max_abs_weight_error']!=0:
        raise RuntimeError('T1_REAL_GGUF_READBACK_FAIL')
    return {'sha256':sha_file(out),'max_abs_weight_error':q['max_abs_weight_error'],'tensor_count':52}


def main():
    ap=argparse.ArgumentParser();ap.add_argument('--repo',required=True);ap.add_argument('--mode',choices=['preview','execute'],required=True)
    args=ap.parse_args();repo=Path(args.repo).resolve(strict=True)
    if os.name!='nt':raise RuntimeError('WINDOWS_NATIVE_ONLY')
    if str(repo).lower()!=r'd:\work\research\tokentomodel-lab':raise RuntimeError('REPO_BOUNDARY')
    work=repo/'_tmp'/'ttm_t2'
    t1=repo/'_tmp'/'ttm_t1_real_source_v1'
    man=t1/'T1_BPE2048_REAL_TRAIN_MANIFEST.json'
    split=t1/'T1_STORY_SPLIT_IDS_NO_RAW_TEXT.json'
    if not man.is_file() or not split.is_file():raise RuntimeError('T1_SOURCE_NOT_EXECUTED_NO_REAL_BPE')
    sp=json.loads(split.read_text('utf8'));obj=json.loads(man.read_text('utf8'))
    if sp['revision']!='f54c09fd23315a6f9c86f9dc80f725de7d8f9c64':raise RuntimeError('T1_REVISION_DRIFT')
    if sp['tokenizer_manifest_sha256']!=obj['manifest_sha256']:raise RuntimeError('TOKENIZER_SPLIT_SHA_MISMATCH')
    expected_fit=[{'id':f'TRAIN_{i:04d}_{s[:16]}','text_sha256':s,'source':'TinyStories-train.txt'}
                  for i,s in enumerate(sp['splits']['TRAIN'][:sp['tokenizer_fit_n']])]
    if obj['source_commitment']!=sha(canonical_bytes(expected_fit)) or obj['source_kind']!='PINNED_TINYSTORIES_TRAIN':
        raise RuntimeError('TOKENIZER_MUST_BE_TRAIN_FROM_AUTHENTICATED_SPLIT')
    bpe=BPE2048.from_manifest(obj)
    out=repo/'_tmp'/'ttm_t1_real_native_v1'
    exe=work/'v5b_technical'/'build'/'Release'/'ttm_t2_v5_probe.exe'
    dll=work/'build'/'bin'/'Release'
    if sha_file(exe)!=PROBE_SHA:raise RuntimeError('NATIVE_PROBE_SHA_CHANGED')
    from source_t2.ttm_t2_f32_integrated import DLLS
    for name,h in DLLS.items():
        if sha_file(dll/name)!=h:raise RuntimeError('DLL_SHA_CHANGED:'+name)
    if sha_file(Path(gguf.__file__))!=GGUF_V3_SHA:raise RuntimeError('V3_GGUF_CONVERTER_SHA_CHANGED')
    if gguf.git_blob_sha(repo/'src'/'p02'/'transformer_core.py')!=P02_BLOB:raise RuntimeError('P02_SHA_CHANGED')
    if os.popen('git -C "'+str(work/'llama.cpp')+'" rev-parse HEAD').read().strip()!=LLAMA:raise RuntimeError('LLAMA_PIN_CHANGED')
    if args.mode=='preview':
        if out.exists():raise RuntimeError('T1_NATIVE_RESULT_EXISTS')
        print('TTM_T1_REAL_TOKENIZER_NATIVE_PREVIEW=PASS_READONLY');return
    if out.exists():raise RuntimeError('T1_NATIVE_RESULT_EXISTS_DO_NOT_RERUN')
    out.mkdir(parents=True)
    receipt={'schema':'ttm.t1.real.trained_bpe.native_f32.v1','status':'STOP_INCOMPLETE','science_executed':False,
             'bpe_sha256':sha_file(man),'split_sha256':sha_file(split),'llama_sha':LLAMA,'runs':[]}
    report=out/'T1_REAL_TOKENIZER_F32_NATIVE_QA.json'
    try:
        model=gguf.load_model(repo)
        result=export(out/'ttm_real_bpe_p02_random_f32.gguf',model,bpe)
        receipt['gguf']=result
        fixture=json.loads((Path(__file__).parent/'source_t2'/'TTM_T2_F32_NEW_FIXTURES_FROZEN_20261108.json').read_text('utf8'))
        env=os.environ.copy();env['PATH']=str(dll)+os.pathsep+env.get('PATH','');env['CUDA_VISIBLE_DEVICES']='';env['OMP_NUM_THREADS']='1'
        mismatches=[]
        for i,case in enumerate(fixture['tokenizer_text_cases']):
            token=run_probe(exe,out/'ttm_real_bpe_p02_random_f32.gguf',['--tokenize-hex',case['text'].encode('utf8').hex()],env)['tokens']
            expected=bpe.encode(case['text'])
            if token!=expected:mismatches.append({'case':case['id'],'expected':expected,'actual':token})
        nums=[]
        for case in fixture['numeric_id_cases']:
            ids=case['ids']
            with torch.inference_mode():ref=model(torch.tensor([ids],dtype=torch.long))[0][0,-1].numpy()
            got=np.asarray(run_probe(exe,out/'ttm_real_bpe_p02_random_f32.gguf',['--ids',','.join(map(str,ids))],env)['logits'])
            err=float(np.max(np.abs(got-ref.astype('float64'))))
            nums.append({'case':case['id'],'max_abs_error':err,'top1_equal':int(np.argmax(got))==int(np.argmax(ref))})
        receipt['tokenizer']={'cases':len(fixture['tokenizer_text_cases']),'mismatches':mismatches}
        receipt['numeric']={'cases':nums,'max_abs_error':max(r['max_abs_error'] for r in nums)}
        passed=(len(mismatches)==0 and len(nums)==10 and receipt['numeric']['max_abs_error']<=.001 and all(r['top1_equal'] for r in nums))
        receipt['status']='PASS_REAL_TRAIN_ONLY_F32_EXPORT' if passed else 'FAIL_REAL_TRAIN_ONLY_F32_EXPORT'
    except BaseException as e:
        receipt['status']='STOP_ERROR';receipt['error']=str(e);receipt['traceback']=traceback.format_exc()[-1600:]
    finally:
        report.write_text(json.dumps(receipt,indent=2,ensure_ascii=False,sort_keys=True)+'\n',encoding='utf8')
        print('TTM_T1_NATIVE_REPORT='+str(report))
        print('TTM_T1_NATIVE_STATUS='+receipt['status'])
        if receipt['status']!='PASS_REAL_TRAIN_ONLY_F32_EXPORT':sys.exit(2)

if __name__=='__main__':main()
