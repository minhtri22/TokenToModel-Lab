#!/usr/bin/env python3
"""G1 v1c private feature extractor, signed authority and split-only input.

Reads locally staged *original* TinyStories TRAIN source; reconstructs only frozen
G1 prefixes in RAM, then sequentially loads Qwen3-0.6B / Qwen3-1.7B from pinned
weights and writes numeric NPZ (never raw text). Does not run until separately
approved: synthetic-qa is no-data and no-GPU. TEST requires frozen DEV selection.
"""
from __future__ import annotations
import argparse, gc, hashlib, importlib.metadata as md, json, os, platform
import g1_science_guard_v1c as guard
from pathlib import Path
import re, shutil, struct, sys, time, unicodedata
import numpy as np

MANIFEST_SHA='6451be0cd09a54378eda9e815b5c89ce8ce8301ddefef556476d94e3e31e42b6'
SOURCE_SHA='c5cf5e22ff13614e830afbe61a99fbcbe8bcb7dd72252b989fa1117a368d401f'
PERMIT_SCHEMA='ttm.six.g1.science_one_shot_permit.v1'
PINS={'transformers':'5.22.1','huggingface-hub':'1.33.0',
      'tokenizers':'0.23.3','safetensors':'0.8.0'}
MODELS={
 'source':{'repo':'Qwen/Qwen3-0.6B','revision':'c1899de289a04d12100db370d81485cdf75e47ca',
   'size':1024,'weights':{'model.safetensors':'f47f71177f32bcd101b7573ec9171e6a57f4f4d31148d38e382306f42996874b'}},
 'target':{'repo':'Qwen/Qwen3-1.7B','revision':'70d244cc86ccca08cf5af4e1e306ecf908b1ad5e',
   'size':2048,'weights':{
     'model-00001-of-00002.safetensors':'169ad53ec313c3a34b06c0809216e4fc072cce444a5d4ff2b59690d064130ed5',
     'model-00002-of-00002.safetensors':'912becff8d60672aa8628ef08c05898d9adf17c2ad4ae3caf99b065622fdeff9'}}}
FILES=('LICENSE','config.json','generation_config.json','tokenizer.json',
       'tokenizer_config.json','merges.txt','vocab.json')
MODEL_AUX_SHA256={
 'source':{
  'LICENSE':'832dd9e00a68dd83b3c3fb9f5588dad7dcf337a0db50f7d9483f310cd292e92e',
  'config.json':'660db3b73d788119c04535e48cf9be5f55bc3100841a718637ae695b442f27dd',
  'generation_config.json':'2325da0f15bb848e018c5ae071b7943332e9f871d6b60e2ed22ca97d4cb993d2',
  'merges.txt':'8831e4f1a044471340f7c0a83d7bd71306a5b867e95fd870f74d0c5308a904d5',
  'tokenizer.json':'aeb13307a71acd8fe81861d94ad54ab689df773318809eed3cbe794b4492dae4',
  'tokenizer_config.json':'d5d09f07b48c3086c508b30d1c9114bd1189145b74e982a265350c923acd8101',
  'vocab.json':'ca10d7e9fb3ed18575dd1e277a2579c16d108e32f27439684afa0e10b1440910',
 },
 'target':{
  'LICENSE':'832dd9e00a68dd83b3c3fb9f5588dad7dcf337a0db50f7d9483f310cd292e92e',
  'config.json':'1ddb5b89ebc90dcb417a45c213d818577e65976454d29385c8f6140771d95197',
  'generation_config.json':'2325da0f15bb848e018c5ae071b7943332e9f871d6b60e2ed22ca97d4cb993d2',
  'merges.txt':'8831e4f1a044471340f7c0a83d7bd71306a5b867e95fd870f74d0c5308a904d5',
  'model.safetensors.index.json':'0d660e94b165eb912669a5249dff44b83188c4777a07ddb9611fb78d91b0578d',
  'tokenizer.json':'aeb13307a71acd8fe81861d94ad54ab689df773318809eed3cbe794b4492dae4',
  'tokenizer_config.json':'d5d09f07b48c3086c508b30d1c9114bd1189145b74e982a265350c923acd8101',
  'vocab.json':'ca10d7e9fb3ed18575dd1e277a2579c16d108e32f27439684afa0e10b1440910',
 },
}

PROBES=(
 (' The child smiled.',' The child cried.'),
 (' Everyone felt safe.',' Everyone felt afraid.'),
 (' The toy was found.',' The toy was lost.'),
 (' She told the truth.',' She told a lie.'),
 (' He shared the toy.',' He kept the toy.'),
 (' They stayed home.',' They went outside.'),
 (' The door was open.',' The door was closed.'),
 (' The story ended happily.',' The story ended sadly.'),
)
COUNTS={'TRAIN':128,'DEV':64,'TEST':64}
EOS=b'<|endoftext|>'


def need(ok,what):
    if not ok: raise RuntimeError('STOP_G1_'+what)


def sha_file(p):
    h=hashlib.sha256()
    with Path(p).open('rb') as f:
        for c in iter(lambda:f.read(8<<20),b''):h.update(c)
    return h.hexdigest()


def gitblob(p):
    data=Path(p).read_bytes()
    return hashlib.sha1(b'blob '+str(len(data)).encode()+b'\0'+data).hexdigest()


def check_permit(envelope, *, phase, work, run_id):
    actual=gitblob(__file__)
    return guard.verify_signed_permit(envelope,{
        'phase':phase,'run_id':run_id,'workspace':str(work),
        'reviewed_extractor_blob':actual})


def iter_stories(fd,hash_ctx):
    buf=b''
    while True:
        c=fd.read(1<<20)
        if not c:break
        hash_ctx.update(c)
        buf+=c
        while True:
            j=buf.find(EOS)
            if j<0:break
            part=buf[:j].strip(b' \t\r\n')
            buf=buf[j+len(EOS):]
            if part:yield part
        need(len(buf)<=1<<23,'SOURCE_STORY_OVERSIZE')
    tail=buf.strip(b' \t\r\n')
    if tail:yield tail


def normalize(txt):
    return unicodedata.normalize('NFC',txt).replace('\r\n','\n').replace('\r','\n').strip().replace('\n',' ')


def prefix(txt):
    end=next((i+1 for i,ch in enumerate(txt) if ch in '.!?' and 80<=i+1<=192),None)
    if end is None:
        end=next((i for i,ch in enumerate(txt) if ch.isspace() and 128<=i<=192),None)
    need(end is not None,'PREFIX_BOUNDARY_RECONSTRUCTION')
    need(sum(not c.isspace() for c in txt[:end])>=12,'PREFIX_TOO_SHORT')
    return txt[:end],end


def reconstruct(manifest,split,split_source_root,*,fit_frozen_validated=False):
    # Reading the *full* TinyStories TRAIN corpus in a science stage is forbidden.
    # A separate private owner-authorized data broker must stage split payloads.
    data=guard.open_split_payload(split,fit_frozen_validated,split_source_root)
    need(len(data)<=2*1024*1024,'SPLIT_PAYLOAD_TOO_LARGE')
    obj=json.loads(data)
    need(obj.get('schema')=='ttm.six.g1.private_split_prefix_v1b' and
         obj.get('split')==split and obj.get('manifest_sha256')==MANIFEST_SHA,
         'SPLIT_PAYLOAD_SCHEMA')
    rows=obj['rows'];want=manifest['splits'][split]
    need(len(rows)==COUNTS[split],'SPLIT_PAYLOAD_SIZE')
    out=[]
    for row,ref in zip(rows,want):
        need(row['source_story_sha256']==ref['source_story_sha256'],
             'SPLIT_SOURCE_ID_MISMATCH')
        pre=row['prefix'];end=ref['prefix_end_unicode_codepoint_offset']
        need(isinstance(pre,str) and len(pre)==end,'SPLIT_PREFIX_BOUNDARY')
        need(hashlib.sha256(pre.encode('utf-8')).hexdigest()==ref['normalized_prefix_utf8_sha256'],
             'SPLIT_PREFIX_HASH_MISMATCH')
        out.append(pre)
    return out


def environment():
    import torch
    need(sys.version_info[:2]==(3,13) and sys.version_info.releaselevel=='final','PY313')
    need(torch.__version__=='2.14.1+cu130','TORCH_PIN')
    need({k:md.version(k) for k in PINS}==PINS,'PACKAGES_PIN')
    need(torch.cuda.is_available(),'CUDA_MISSING')
    need('T4' in torch.cuda.get_device_name(0) and tuple(torch.cuda.get_device_capability(0))==(7,5),
         'GPU_T4_CC75')
    free,total=torch.cuda.mem_get_info(0)
    need(free>=11*(1024**3) and total>=12*(1024**3),'GPU_FREE_GUARD')
    need(shutil.disk_usage('/content').free>=12*(1024**3),'DISK_FREE_GUARD')
    return torch


def load_teacher(name,work,torch):
    from huggingface_hub import snapshot_download
    from transformers import AutoTokenizer,AutoModelForCausalLM
    spec=MODELS[name]
    files=list(FILES)+list(spec['weights'])
    if name=='target':files+=['model.safetensors.index.json']
    modeldir=work/('model_'+name)
    folder=Path(snapshot_download(repo_id=spec['repo'],revision=spec['revision'],
        allow_patterns=files,local_dir=str(modeldir),max_workers=1))
    for filename in files:
        path=folder/filename
        need(path.is_file() and not path.is_symlink(),'MODEL_REQUIRED_FILE_'+filename)
    pinned={**MODEL_AUX_SHA256[name],**spec['weights']}
    need(set(pinned)==set(files),'MODEL_FILES_PIN_SET')
    for filename,digest in pinned.items():
        need(sha_file(folder/filename)==digest,'MODEL_FILE_SHA_'+filename)
    config=json.loads((folder/'config.json').read_text('utf-8'))
    need(config.get('model_type')=='qwen3' and config.get('hidden_size')==spec['size']
         and config.get('num_hidden_layers')==28 and config.get('vocab_size')==151936,
         'MODEL_CONFIG_CONTRACT')
    if name=='target':
        idx=json.loads((folder/'model.safetensors.index.json').read_text('utf-8'))
        need(set(idx['weight_map'].values())==set(spec['weights']),'WEIGHT_INDEX_MISMATCH')
    tok=AutoTokenizer.from_pretrained(str(folder),local_files_only=True,trust_remote_code=False)
    model=AutoModelForCausalLM.from_pretrained(str(folder),local_files_only=True,
          trust_remote_code=False,dtype=torch.float16).to('cuda:0').eval()
    need(not model.training,'MODEL_NOT_EVAL')
    return tok,model


def continuation_score(model,prefix_ids,continuation_ids,bytes_len,torch):
    # Tokenize prefix and continuation separately, concatenate *IDs*.
    need(len(prefix_ids)>0 and len(continuation_ids)>0 and bytes_len>0,'EMPTY_TOKENS')
    seq=torch.tensor([prefix_ids+continuation_ids],dtype=torch.long,device='cuda:0')
    with torch.inference_mode():
        out=model(input_ids=seq,return_dict=True,use_cache=False)
        logits=out.logits[0,len(prefix_ids)-1:len(prefix_ids)+len(continuation_ids)-1,:].float()
        logp=torch.log_softmax(logits,dim=-1)
        idx=torch.tensor(continuation_ids,dtype=torch.long,device='cuda:0')
        score=logp.gather(1,idx[:,None]).sum().item()/bytes_len
    need(np.isfinite(score),'NONFINITE_SCORE')
    return float(score)


def process_teacher(name,inputs,manifest_rows,work,torch,deadline,budget):
    budget.check(name,deadline[0])
    tok,model=load_teacher(name,work,torch)
    budget.check(name,deadline[0])
    state=[];resp=[]
    try:
        for text,entry in zip(inputs,manifest_rows):
            budget.check(name,deadline[0])
            ids=tok.encode(text,add_special_tokens=False)
            need(8<=len(ids)<=96,'PREFIX_TOKEN_LENGTH')
            need(len(ids)==entry['qwen06_token_count' if name=='source' else 'qwen17_token_count'],
                 'PREFIX_TOKEN_PIN_CHANGED')
            ix=torch.tensor([ids],dtype=torch.long,device='cuda:0')
            with torch.inference_mode():
                out=model(input_ids=ix,use_cache=False,return_dict=True,output_hidden_states=True)
                need(len(out.hidden_states)==29,'HIDDEN_COUNT')
                vec=out.hidden_states[28][0,-1,:].float().cpu().numpy().astype('float32')
                need(vec.shape==(MODELS[name]['size'],) and bool(np.isfinite(vec).all()),
                     'HIDDEN_FINITE_SHAPE')
                del out
            budget.check(name,deadline[0])
            state.append(vec)
            if name=='target':
                scores=[]
                for a,b in PROBES:
                    aids=tok.encode(a,add_special_tokens=False)
                    bids=tok.encode(b,add_special_tokens=False)
                    ra=continuation_score(model,ids,aids,len(a.encode('utf-8')),torch)
                    rb=continuation_score(model,ids,bids,len(b.encode('utf-8')),torch)
                    scores.append(ra-rb)
                    budget.check(name,deadline[0])
                resp.append(np.asarray(scores,dtype='float64'))
        reserved=int(torch.cuda.max_memory_reserved(0))
        need(reserved<=12*(1024**3),'GPU_PEAK_12GIB')
        return np.asarray(state,dtype='float32'),np.asarray(resp,dtype='float64')
    finally:
        del model,tok
        gc.collect()
        torch.cuda.empty_cache()


def main():
    ap=argparse.ArgumentParser()
    ap.add_argument('--mode',choices=['synthetic-qa','extract'],required=True)
    ap.add_argument('--split',choices=list(COUNTS))
    ap.add_argument('--private-root',type=Path)
    ap.add_argument('--permit',type=Path)
    ap.add_argument('--run-id')
    args=ap.parse_args()
    if args.mode=='synthetic-qa':
        example='a'*92+'. '+'b'*10
        pre,end=prefix(normalize(example))
        need(end==93 and len(PROBES)==8,'SYNTHETIC_PROTO')
        need(gitblob(__file__)!='','SYNTHETIC_BLOB')
        print(json.dumps({'status':'PASS_EXTRACTOR_V1C_SYNTHETIC_ONLY',
                          'probes':8,'science_executed':False}));return
    need(args.split and args.private_root and args.permit and args.run_id,'ARGS_REQUIRED')
    root=args.private_root.resolve(strict=True)
    if os.name=='nt':
        ttm=Path(r'D:\WORK\RESEARCH\TokenToModel-Lab').resolve(strict=True)
        need(root.is_relative_to(ttm),'PROJECT_SCOPE_WINDOWS')
    elif sys.platform.startswith('linux'):
        need(root==Path('/content').resolve(strict=True),'PROJECT_SCOPE_COLAB')
    else:need(False,'UNSUPPORTED_HOST')
    work=root/'ttm_six_g1_science_private'
    need(work.is_dir() and work.resolve(strict=True).is_relative_to(root),'WORK_ROOT')
    envelope=json.loads(args.permit.read_text('utf-8'))
    authority=check_permit(envelope,phase='extract_'+args.split,
                           work=work,run_id=args.run_id)
    manifest_path=work/'G1_PREFIX_IDS_128_64_64_PRIVATE_METADATA.json'
    need(sha_file(manifest_path)==MANIFEST_SHA,'MANIFEST_SHA')
    manifest=json.loads(manifest_path.read_text('utf-8'))
    need(manifest['counts']==COUNTS,'COUNTS')
    split=args.split
    pack_path=work/('G1_FEATURES_'+split+'.npz')
    receipt_path=pack_path.with_suffix('.receipt.json')
    marker=work/('G1_EXTRACT_'+split+'_ONE_SHOT_CONSUMED.marker')
    need(not any(p.exists() for p in (pack_path,receipt_path,marker)),
         'EXTRACTION_ALREADY_CONSUMED')
    fit_valid=False
    if split=='TEST':
        frozen_path=work/'G1_FIT_DEV_FROZEN.json'
        freeze=guard.read_private_bytes(frozen_path,work,max_size=131072)
        exp=authority.get('fit_sha256')
        need(isinstance(exp,str),'TEST_FIT_SHA_REQUIRED')
        hashes=authority.get('pack_sha_by_split',{})
        guard.validate_frozen_dev(freeze,exp,hashes.get('TRAIN'),hashes.get('DEV'),
                                  run_id=args.run_id)
        fit_valid=True
    # Verify GPU/authority/freeze before consuming the source-opening right.
    # For TEST: the marker is exclusive and durable BEFORE even a single byte
    # is read from the pre-split TEST payload (not just before model loading).
    torch=environment()
    with marker.open('x',encoding='utf-8') as f:
        f.write('EXTRACTION_CONSUMED_BEFORE_SPLIT_SOURCE_READ\n')
        f.flush();os.fsync(f.fileno())
    # Real model must see split-scoped source ONLY; no TinyStories full-file path.
    split_root=work/'private_split_inputs'
    inputs=reconstruct(manifest,split,split_root,fit_frozen_validated=fit_valid)
    rows=manifest['splits'][split]
    os.environ['HF_HOME']=str(work/'hf_home')
    os.environ['HF_HUB_CACHE']=str(work/'hf_home'/'hub')
    os.environ['HF_HUB_DISABLE_TELEMETRY']='1'
    budget=guard.Budget(authority.get('elapsed_seconds_by_model',{}))
    all_states={};responses=None
    for name in ('source','target'):
        began=time.monotonic();torch.cuda.reset_peak_memory_stats(0)
        states,rs=process_teacher(name,inputs,rows,work,torch,[began],budget)
        budget.finish(name,began)
        all_states[name]=states
        if name=='target':responses=rs
    need(responses is not None and responses.shape==(COUNTS[split],8),'RESP_SHAPE')
    ids=np.array([entry['source_story_sha256'] for entry in rows],dtype='<U64')
    import io
    output=io.BytesIO()
    np.savez_compressed(output,ids=ids,s=all_states['source'],t=all_states['target'],r=responses)
    content=output.getvalue()
    # Immutable content commit; first create complete pack, then receipt, no overwrite.
    need(len(content)<=guard.MAX_PACK_BYTES,'PACK_OVERSIZE')
    guard._check_array_headers(content,split)
    guard.commit_immutable_bytes(pack_path,content,work)
    receipt={'schema':'ttm.six.g1.feature_pack_commit.v1b','status':'PACK_COMMITTED',
             'split':split,'run_id':args.run_id,'manifest_sha256':MANIFEST_SHA,
             'sha256':guard.sha_bytes(content),'model_seconds_cumulative':budget.elapsed}
    guard.commit_immutable_bytes(receipt_path,guard.canonical(receipt)+b'\n',work)
    print(json.dumps({'status':'PASS_PRIVATE_NUMERIC_PACK_COMMITTED',
       'split':split,'pack_sha256':receipt['sha256'],
       'science_one_shot_consumed':True,'text_written':False},sort_keys=True))


if __name__=='__main__':
    try:main()
    except Exception as exc:
        print(json.dumps({'status':'STOP_FAIL_CLOSED','error_code':type(exc).__name__,
                          'science_pass_not_claimed':True}),file=sys.stderr)
        raise SystemExit(1)
