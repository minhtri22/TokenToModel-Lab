#!/usr/bin/env python3
"""G1 PRIVATE science feature extractor, executable ONLY with external one-shot permit.

Reads locally staged *original* TinyStories TRAIN source; reconstructs only frozen
G1 prefixes in RAM, then sequentially loads Qwen3-0.6B / Qwen3-1.7B from pinned
weights and writes numeric NPZ (never raw text). Does not run until separately
approved: synthetic-qa is no-data and no-GPU. TEST requires frozen DEV selection.
"""
from __future__ import annotations
import argparse, gc, hashlib, importlib.metadata as md, json, os, platform
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


def check_permit(permit):
    mandatory={'schema':PERMIT_SCHEMA,'decision':'AUTHORIZE_G1_SCIENCE_ONE_SHOT',
      'independent_review':'PASS_DISTINCT_REVIEWER','owner_authorized':True,
      'allow_private_numeric_feature_extraction':True,'manifest_sha256':MANIFEST_SHA,
      'science_runner_frozen':True,'one_shot_test_release':True}
    for k,v in mandatory.items():need(permit.get(k)==v,'PERMIT_'+k)
    need(permit.get('reviewer_id')!=permit.get('code_author_id') and
         isinstance(permit.get('reviewer_id'),str) and len(permit['reviewer_id'])>=3,
         'NOT_DISTINCT_REVIEWER')
    need(permit.get('reviewed_extractor_blob_sha')==gitblob(__file__),
         'EXTRACTOR_BLOB_NOT_REVIEWED')
    need(permit.get('private_source_staging_approved') is True,
         'PRIVATE_SOURCE_STAGING_NOT_APPROVED')


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


def reconstruct(manifest,split,source_file):
    rows=manifest['splits'][split]
    wanted={x['source_story_sha256']:x for x in rows}
    found={};hash_ctx=hashlib.sha256()
    with Path(source_file).open('rb') as fd:
        for index,b in enumerate(iter_stories(fd,hash_ctx)):
            key=hashlib.sha256(b).hexdigest()
            if key not in wanted or key in found:continue
            entry=wanted[key]
            need(entry['source_row_index']==index,'SOURCE_ROW_MAPPING_CHANGED')
            raw=b.decode('utf-8','strict')
            txt=normalize(raw)
            pre,end=prefix(txt)
            need(end==entry['prefix_end_unicode_codepoint_offset'],'PREFIX_END_CHANGED')
            need(hashlib.sha256(pre.encode('utf-8')).hexdigest()==entry['normalized_prefix_utf8_sha256'],
                 'PREFIX_HASH_CHANGED')
            found[key]=pre
    need(hash_ctx.hexdigest()==SOURCE_SHA,'ORIGINAL_SOURCE_SHA_CHANGED')
    need(len(found)==COUNTS[split],'PREFIX_ID_MISSING')
    return [found[x['source_story_sha256']] for x in rows]


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
    for filename,digest in spec['weights'].items():
        need(sha_file(folder/filename)==digest,'MODEL_WEIGHT_HASH_'+filename)
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


def process_teacher(name,inputs,manifest_rows,work,torch,deadline):
    tok,model=load_teacher(name,work,torch)
    state=[];resp=[]
    try:
        for text,entry in zip(inputs,manifest_rows):
            need(time.monotonic()<deadline,'MODEL_WALLTIME_CAP')
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
            state.append(vec)
            if name=='target':
                scores=[]
                for a,b in PROBES:
                    aids=tok.encode(a,add_special_tokens=False)
                    bids=tok.encode(b,add_special_tokens=False)
                    ra=continuation_score(model,ids,aids,len(a.encode('utf-8')),torch)
                    rb=continuation_score(model,ids,bids,len(b.encode('utf-8')),torch)
                    scores.append(ra-rb)
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
    ap.add_argument('--source',type=Path)
    ap.add_argument('--permit',type=Path)
    args=ap.parse_args()
    if args.mode=='synthetic-qa':
        example='a'*92+'. '+'b'*10
        p,end=prefix(normalize(example))
        need(end==93 and len(PROBES)==8,'SYNTHETIC_PROTO')
        need(gitblob(__file__)!='','SYNTHETIC_BLOB')
        print(json.dumps({'status':'PASS_EXTRACTOR_SYNTHETIC_ONLY_NO_FILES_OR_GPU',
                          'probes':8,'science_executed':False}));return
    need(args.split and args.private_root and args.source and args.permit,'ARGS_REQUIRED')
    root=args.private_root.resolve(strict=True)
    source=args.source.resolve(strict=True)
    need(source.is_relative_to(root),'SOURCE_OUTSIDE_PRIVATE_ROOT')
    work=root/'ttm_six_g1_science_private'
    need(work.is_dir() and work.resolve(strict=True).is_relative_to(root),'WORK_ROOT')
    permit=json.loads(args.permit.read_text('utf-8'))
    check_permit(permit)
    manifest_path=work/'G1_PREFIX_IDS_128_64_64_PRIVATE_METADATA.json'
    need(sha_file(manifest_path)==MANIFEST_SHA,'MANIFEST_SHA')
    manifest=json.loads(manifest_path.read_text('utf-8'))
    need(manifest['counts']==COUNTS,'COUNTS')
    split=args.split
    pack_path=work/('G1_FEATURES_'+split+'.npz')
    marker=work/('G1_EXTRACT_'+split+'_ONE_SHOT_CONSUMED.marker')
    need(not pack_path.exists(),'PACK_ALREADY_EXISTS')
    if split=='TEST':
        need((work/'G1_FIT_DEV_FROZEN.json').is_file(),'NO_DEV_FIT_FREEZE')
    # Technical environment preflight is read-only and precedes consumption.
    # For TEST, consume before source read; all stages fail closed on retry.
    torch=environment()
    with marker.open('x',encoding='utf-8') as f:
        f.write('CONSUMED_BEFORE_ANY_PRIVATE_SOURCE_READ\n')
    os.environ['HF_HOME']=str(work/'hf_home')
    os.environ['HF_HUB_CACHE']=str(work/'hf_home'/'hub')
    os.environ['HF_HUB_DISABLE_TELEMETRY']='1'
    inputs=reconstruct(manifest,split,source)
    rows=manifest['splits'][split]
    all_states={};responses=None
    for name in ('source','target'):
        torch.cuda.reset_peak_memory_stats(0)
        deadline=time.monotonic()+60*60
        states,rs=process_teacher(name,inputs,rows,work,torch,deadline)
        all_states[name]=states
        if name=='target':responses=rs
    need(responses is not None and responses.shape==(COUNTS[split],8),'RESP_SHAPE')
    ids=np.array([entry['source_story_sha256'] for entry in rows],dtype='<U64')
    with pack_path.open('xb') as fd:
        np.savez_compressed(fd,ids=ids,s=all_states['source'],t=all_states['target'],r=responses)
    print(json.dumps({'status':'PASS_PRIVATE_NUMERIC_FEATURE_PACK_ONLY',
      'split':split,'pack_sha256':sha_file(pack_path),'rows':COUNTS[split],
      'science_authorized_by_permit':True,'one_shot_consumed':True,
      'text_written':False,'source_train_sha256':SOURCE_SHA},sort_keys=True))


if __name__=='__main__':
    try:main()
    except Exception as exc:
        print(json.dumps({'status':'STOP_FAIL_CLOSED','error':str(exc)[:500],
                          'science_pass_not_claimed':True}),file=sys.stderr)
        raise SystemExit(1)
