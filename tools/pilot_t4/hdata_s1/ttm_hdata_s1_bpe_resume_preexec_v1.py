#!/usr/bin/env python3
"""DEV-only independent shadow BPE and immutable CPU checkpoint structural preflight.
No FINAL content, no TRAIN token arrays, no model construction or forward.
Source P02 actual BPE implementation must still pass pinned Colab source readback.
"""
from __future__ import annotations
import argparse,hashlib,json,pathlib,copy
import regex,torch

BPE_SHA='cba18e60cee3d08a353ee6d4a451017289e45af7b4b1179c87171b9b78d7dfdc'
DEV_SHA='60e514a2329abe6b6df673058ee7656bb57287758c6ee4cc861a396a1788ba3d'
PARENT_SHA='cb985751795c8328ad65acf7ca4c1033ce35182c1bfbdb8c38550de629cb271b'
SCHEMA='ttm.gpt2.pretokenized.byte-bpe.2048.v1';EOS=256
PATTERN=r"'s|'t|'re|'ve|'m|'ll|'d| ?\p{L}+| ?\p{N}+| ?[^\s\p{L}\p{N}]+|\s+(?!\S)"

def sha(b):return hashlib.sha256(b).hexdigest()
def canonical(x):return json.dumps(x,sort_keys=True,ensure_ascii=False,separators=(',',':')).encode('utf8')
def need(b,why):
    if not b:raise RuntimeError('H_DATA_S1_BPE_PREEXEC_HOLD:'+why)

def byte_to_unicode():
    bs=list(range(33,127))+list(range(161,173))+list(range(174,256));cs=bs.copy();n=0
    for i in range(256):
        if i not in bs:bs.append(i);cs.append(256+n);n+=1
    return dict(zip(bs,map(chr,cs)))

def encode(text,rank,pre):
    parts=[];offset=0
    for m in pre.finditer(text):
        if m.start()>offset:parts.append(text[offset:m.start()])
        parts.append(m.group(0));offset=m.end()
    if offset<len(text):parts.append(text[offset:])
    need(''.join(parts)==text,'PRETOKEN_LOST_INPUT')
    out=[]
    for frag in parts:
        ids=list(frag.encode('utf8'))
        while len(ids)>1:
            candidates=((rank[(ids[i],ids[i+1])],i) for i in range(len(ids)-1) if (ids[i],ids[i+1]) in rank)
            found=min(candidates,default=None)
            if found is None:break
            r,i=found;ids[i:i+2]=[257+r]
        out.extend(ids)
    return out

def main():
    a=argparse.ArgumentParser();a.add_argument('--manifest',required=True);a.add_argument('--dev',required=True)
    a.add_argument('--parent',required=True);a.add_argument('--output',required=True);q=a.parse_args()
    mpath=pathlib.Path(q.manifest);dpath=pathlib.Path(q.dev);cpath=pathlib.Path(q.parent)
    need(sha(mpath.read_bytes())==BPE_SHA,'MANIFEST_FILE_SHA');need(sha(dpath.read_bytes())==DEV_SHA,'DEV_PUBLIC_SHA')
    need(sha(cpath.read_bytes())==PARENT_SHA,'PARENT_SHA')
    m=json.loads(mpath.read_bytes());d=json.loads(dpath.read_bytes());payload=dict(m);original=payload.pop('manifest_sha256')
    need(original==sha(canonical(payload)),'BPE_INTERNAL_SHA')
    need(m['schema']==SCHEMA and m['source_kind']=='PINNED_TINYSTORIES_TRAIN','BPE_SCHEMA_KIND')
    need(m['eos_id']==EOS and m['vocab_size']==2048 and len(m['pair_ids'])==1791 and len(m['tokens'])==2048,'BPE_VOCAB')
    need(m['regex']==PATTERN,'BPE_PATTERN')
    pairs=[tuple(x) for x in m['pair_ids']]
    rank={p:i for i,p in enumerate(pairs)}
    need(len(rank)==len(pairs),'BPE_PAIRS_UNIQUE')
    tokens=m['tokens'];byte2char=byte_to_unicode();char2byte={v:k for k,v in byte2char.items()}
    need(tokens[:256]==[byte2char[i] for i in range(256)],'BPE_BYTE_BASE')
    need(tokens[EOS]=='<|endoftext|>','BPE_EOS')
    need(all(a<257+i and b<257+i and tokens[257+i]==tokens[a]+tokens[b] for i,(a,b) in enumerate(pairs)),'BPE_MERGES_CAUSAL')
    need(sha(canonical([tokens,[tokens[a]+' '+tokens[b] for a,b in pairs]]))==m['token_merges_sha256'],'BPE_MERGES_SHA')
    pre=regex.compile(PATTERN)
    lengths=[]
    for item in d['prompts']:
        plain=item['prompt']; ids=encode(plain,rank,pre)
        need(EOS not in ids,'BPE_EOS_IN_PREFIX')
        decoded=bytes(char2byte[c] for tid in ids for c in tokens[tid]).decode('utf8')
        need(decoded==plain,'BPE_DEV_ROUNDTRIP_'+item['id'])
        need(len(ids)+64<=256,'BPE_CONTEXT_'+item['id'])
        lengths.append(len(ids))
    need(len(lengths)==12,'BPE_DEV_COUNT')
    cp=torch.load(cpath,map_location='cpu',weights_only=True)
    need(cp['schema']=='ttm.t4.science.checkpoint.v1' and cp['step']==1024,'PARENT_CKPT_SCHEMA')
    need(len(cp['model'])==53 and 'sampler_state' in cp,'PARENT_STATE_COMPLETENESS')
    # Strict byte-preserving owner-step clone test: no optimizer advancement, no model instantiation
    original_steps=[state['step'].item() if torch.is_tensor(state.get('step')) else state.get('step')
                    for state in cp['optimizer']['state'].values() if 'step' in state]
    need(len(original_steps)>0 and all(k==1024 for k in original_steps),'PARENT_ADAMW_STEP_1024')
    cloned=copy.deepcopy(cp['optimizer']['state'])
    for k,state in cp['optimizer']['state'].items():
        src=state.get('step');dst=cloned[k].get('step')
        if torch.is_tensor(src):need(src.data_ptr()!=dst.data_ptr() and torch.equal(src,dst),'PARENT_OPTIMIZER_STEP_CLONE_ALIAS')
    need(cp['scheduler'].get('last_epoch')==1024,'PARENT_SCHEDULER_STEP')
    out={'schema':'ttm.hdata_s1.dev_only_bpe_parent_readback.v1',
         'bpe_implementation':'independent_shadow_matching_frozen_source_semantics_not_t4_runtime_verified',
         'dev_count':12,'bpe_roundtrip_pass':12,'context_plus64_pass':12,'bpe_min_tokens':min(lengths),'bpe_max_tokens':max(lengths),
         'parent_optimizer_step':1024,'scheduler_epoch':1024,'optimizer_cloned_no_alias':True,
         'no_model_instantiation':True,'no_model_forward':True,'no_optimizer_step':True,
         'FINAL_private_text_read':False,'TRAIN_x_y_arrays_read':False,
         'source_sha256':{'bpe':BPE_SHA,'dev':DEV_SHA,'parent':PARENT_SHA},'status':'PASS_CPU_DEV_BPE_AND_PARENT_STRUCTURAL__COLAB_EXACT_RUNTIME_PENDING'}
    pathlib.Path(q.output).write_text(json.dumps(out,sort_keys=True,indent=2)+'\n',encoding='utf8')
    print(json.dumps(out,indent=2))

if __name__=='__main__':main()
