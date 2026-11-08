#!/usr/bin/env python3
"""Construct a PRIVATE T4 token-window pack from frozen T1 TRAIN/VAL IDs.

Never tokenizes the TEST split, never trains a model, never writes story text to Git.
No overwrite: consumed one-shot outputs require a separately reviewed recovery.
"""
from __future__ import annotations
import argparse, hashlib, json, os, sys
from pathlib import Path
import numpy as np

_t1_dir=Path(__file__).resolve().parents[1]/'pilot_t1t3'
if _t1_dir.exists():sys.path.insert(0,str(_t1_dir))
from t1_source_split_tokenizer import iter_story_bytes, eligible_raw
from source_t2.ttm_gpt2_bpe2048 import BPE2048, EOS_ID

RAW_SHA={
'TinyStories-train.txt':'c5cf5e22ff13614e830afbe61a99fbcbe8bcb7dd72252b989fa1117a368d401f',
'TinyStories-valid.txt':'94e431816c4cce81ff71e4408ff8d3bda9a42e8d2663986697c3954288cb38b4'}
SPLIT_SHA='9f2ebaca821bddf0a9d7ae30ccfcef34561b968b21159aa913794298235a2fa9'
BPE_FILE_SHA='cba18e60cee3d08a353ee6d4a451017289e45af7b4b1179c87171b9b78d7dfdc'
EXPECTED_N={'TRAIN':2048,'VAL':256,'TEST':64}
CONTEXT=256


def file_sha(p):
    h=hashlib.sha256()
    with Path(p).open('rb') as f:
        for b in iter(lambda:f.read(1<<20),b''):h.update(b)
    return h.hexdigest()


def require_source(path,expect):
    if not path.is_file() or path.is_symlink():raise RuntimeError('RAW_MISSING_OR_SYMLINK:'+str(path))
    if file_sha(path)!=expect:raise RuntimeError('RAW_SHA_MISMATCH:'+str(path))


def windows_for_ids(ids):
    """Score every true next-token target exactly once, no cross-story context."""
    if len(ids)<2 or any(x<0 or x>=2048 for x in ids):raise ValueError('BAD_STORY_TOKENS')
    result=[]
    for i in range(0,len(ids)-1,CONTEXT):
        segment=ids[i:i+CONTEXT+1]
        if len(segment)<2:continue
        count=len(segment)-1
        x=np.zeros(CONTEXT,dtype=np.int16)
        y=np.full(CONTEXT,-100,dtype=np.int16)
        x[:count]=segment[:-1]
        y[:count]=segment[1:]
        result.append((x,y,count))
    if sum(w[2] for w in result)!=len(ids)-1:raise AssertionError('UNSCORED_TARGETS')
    return result


def stream_matching(path,ordered_hashes):
    target=set(ordered_hashes)
    if len(target)!=len(ordered_hashes):raise RuntimeError('REPEATED_SPLIT_ID')
    captured={}
    for raw in iter_story_bytes(path):
        # Read and hash the whole pinned original; only selected TRAIN/VAL stories are decoded.
        digest=hashlib.sha256(raw).hexdigest()
        if digest in target and digest not in captured:
            captured[digest]=eligible_raw(raw)
    if set(captured)!=target:raise RuntimeError('SELECTED_STORY_MISSING_IN_PINNED_SOURCE:'+str(len(target-set(captured))))
    return [captured[d] for d in ordered_hashes]


def build_pack(story_texts,bpe):
    xs=[];ys=[];count=[];story=[];lengths=[]
    for si,t in enumerate(story_texts):
        ids=bpe.encode(t)+[EOS_ID]
        lengths.append(len(ids))
        for x,y,n in windows_for_ids(ids):
            xs.append(x);ys.append(y);count.append(n);story.append(si)
    if not xs:raise RuntimeError('EMPTY_WINDOWS')
    return (np.stack(xs),np.stack(ys),np.asarray(count,dtype=np.int16),
            np.asarray(story,dtype=np.int32)),lengths


def make(repo,out):
    repo=Path(repo).resolve(strict=True);out=Path(out)
    if os.name=='nt' and str(repo).lower()!=r'd:\work\research\tokentomodel-lab':raise RuntimeError('WRONG_WINDOWS_REPO')
    if out.exists():raise FileExistsError('T4_PACK_OUTPUT_EXISTS_NO_RETRY')
    if repo.is_symlink() or out.parent.is_symlink():raise RuntimeError('SYMLINK_SCOPE')
    expected=repo/'_tmp'/'ttm_t4_data_pack_v1'
    if out.resolve()!=expected.resolve():raise RuntimeError('OUTPUT_OUTSIDE_FROZEN_T4_PACK_SCOPE')
    t1=repo/'_tmp'/'ttm_t1_real_source_v1'
    raw=repo/'datasets'/'tinystories_v1_original_pinned'
    split_file=t1/'T1_STORY_SPLIT_IDS_NO_RAW_TEXT.json';bpe_file=t1/'T1_BPE2048_REAL_TRAIN_MANIFEST.json'
    if file_sha(split_file)!=SPLIT_SHA or file_sha(bpe_file)!=BPE_FILE_SHA:raise RuntimeError('T1_MANIFEST_FILE_SHA_MISMATCH')
    for name,digest in RAW_SHA.items():require_source(raw/name,digest)
    split=json.loads(split_file.read_text('utf-8'));bpe_raw=json.loads(bpe_file.read_text('utf-8'))
    if split['schema']!='ttm.t1.real.stories.split.v1' or split['tokenizer_manifest_sha256']!=bpe_raw['manifest_sha256']:
        raise RuntimeError('SPLIT_BPE_CROSS_MANIFEST_INVALID')
    pieces=split['splits']
    for k,n in EXPECTED_N.items():
        if len(pieces[k])!=n or len(set(pieces[k]))!=n:raise RuntimeError('SPLIT_COUNT_OR_DUPLICATE:'+k)
    if any(set(pieces[a])&set(pieces[b]) for a,b in [('TRAIN','VAL'),('TRAIN','TEST'),('VAL','TEST')]):
        raise RuntimeError('CROSS_SPLIT_EXACT_LEAK')
    bpe=BPE2048.from_manifest(bpe_raw)
    if bpe.source_kind!='PINNED_TINYSTORIES_TRAIN':raise RuntimeError('NOT_TRAIN_ONLY_TOKENIZER')
    # No TEST content is exported or encoded.
    train_texts=stream_matching(raw/'TinyStories-train.txt',pieces['TRAIN'])
    val_texts=stream_matching(raw/'TinyStories-valid.txt',pieces['VAL'])
    train,train_lens=build_pack(train_texts,bpe)
    val,val_lens=build_pack(val_texts,bpe)
    arrays={}
    for prefix,fields in [('train',train),('val',val)]:
        for suffix,a in zip(['x','y','count','story_index'],fields):arrays[f'{prefix}_{suffix}']=a
    if any(np.any(arrays[f'{p}_count']<=0) or np.any(arrays[f'{p}_count']>CONTEXT) for p in ['train','val']):
        raise RuntimeError('INVALID_TARGET_COUNTS')
    if int(arrays['train_count'].sum())<4096:raise RuntimeError('NOT_ENOUGH_TRAIN_TARGETS')
    # Never create TEST arrays, nor raw story texts.
    out.mkdir(parents=True,exist_ok=False)
    dat=out/'T4_PRIVATE_TRAIN_VAL_WINDOWS.npz'
    with dat.open('xb') as f:
        np.savez_compressed(f,**arrays);f.flush();os.fsync(f.fileno())
    manifest={'schema':'ttm.t4.private.train_val.windowpack.v1','science_executed':False,
     'contains_test':False,'contains_raw_text':False,'contains_reversible_train_val_tokens':True,
     'not_for_public_github':True,
     'source_sha256':RAW_SHA,'t1_split_sha256':SPLIT_SHA,'t1_bpe_file_sha256':BPE_FILE_SHA,
     't1_bpe_internal_sha256':bpe_raw['manifest_sha256'],'context':CONTEXT,
     'counts':{'train_stories':len(train_texts),'val_stories':len(val_texts),'test_stories_tokenized':0,
       'train_windows':len(train[2]),'val_windows':len(val[2]),
       'train_next_token_targets_unique':int(train[2].sum()),
       'val_next_token_targets':int(val[2].sum()),
       'train_window_min_targets':int(train[2].min()),'val_window_min_targets':int(val[2].min()),
       'train_mean_valid_targets_per_window':float(train[2].mean()),
       'train_fraction_full_256_target_windows':float(np.mean(train[2]==256)),
       'train_reuse_factor_for_4194304_target_budget':float(4194304/int(train[2].sum()))},
     'npz_sha256':file_sha(dat),'npz_bytes':dat.stat().st_size}
    m=out/'T4_PRIVATE_PACK_MANIFEST.json'
    with m.open('x',encoding='utf-8') as f:
        json.dump(manifest,f,indent=2,sort_keys=True);f.write('\n');f.flush();os.fsync(f.fileno())
    return manifest


def main():
    parser=argparse.ArgumentParser();parser.add_argument('--repo',required=True);parser.add_argument('--out',required=True)
    args=parser.parse_args()
    m=make(args.repo,args.out)
    print('T4_TRAIN_VAL_PACK=PASS_PRIVATE_NO_TEST')
    print('T4_TRAIN_VALID_TARGETS='+str(m['counts']['train_next_token_targets_unique']))
    print('T4_PACK_SHA256='+m['npz_sha256'])

if __name__=='__main__':main()
