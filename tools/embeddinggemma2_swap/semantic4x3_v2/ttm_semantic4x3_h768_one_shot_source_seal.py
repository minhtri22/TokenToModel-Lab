#!/usr/bin/env python3
"""H768 preregistered source selector; one-shot seal, no training or scoring.

Reuses pinned H512 parsing and near-dup functions, but NEVER opens or decodes the
old H512/H320/TEST story texts, only membership SHA256 identifiers.
All emitted data is private and stays inside TTM project _tmp.
"""
from __future__ import annotations
import argparse, hashlib, heapq, importlib.util, json, os, sys
from collections import Counter
from pathlib import Path
import numpy as np

K=768
DOMAIN=b'TTM_GEMMA2_SEMANTIC4X3_H768_V1_20261110\0'
ROOT_NAME='ttm_semantic4x3_h768_seal_v1_20261110'
H512_PIN='544c30b470f5e8718ba35fe016b0f52cac95e559020eae2806e1ff7291a03661'
H512_HELPER_GIT_BLOB='d893571c23d50d15d1078f1923a467648f33ee52'
H512_PUBLIC_SHA='d9ce40f37da7acf2b4b12fd657cdedb366754b2bb29b4b86de144230240f1b03'


def insist(condition, code):
    if not condition:raise RuntimeError('HOLD_'+code)


def sha(b):return hashlib.sha256(b).hexdigest()


def file_sha(p):
    with Path(p).open('rb') as fd:return hashlib.file_digest(fd,'sha256').hexdigest()


def git_blob(p):
    b=Path(p).read_bytes()
    return hashlib.sha1(b'blob '+str(len(b)).encode()+b'\0'+b).hexdigest()


def rank_digest(digest):return sha(DOMAIN+digest.encode('ascii'))


def fixture():
    sample=[sha(f'synthetic-story-{i}'.encode()) for i in range(820)]
    exclude=set(sample[:27]);remaining=[d for d in sample if d not in exclude]
    first=sorted(remaining,key=lambda h:rank_digest(h))[:K]
    insist(len(first)==K and len(set(first))==K and not exclude.intersection(first),'FIXTURE_MEMBERSHIP')
    insist(DOMAIN.endswith(b'\0') and rank_digest(first[0])!=rank_digest(first[1]),'FIXTURE_DOMAIN')
    print(json.dumps({'schema':'ttm.semantic4x3.h768.fixture.v1','status':'PASS_4_CHECKS',
      'source_data_read':False,'test_data_read':False,'science_executed':False,'gpu':False}))


def load_legacy(root):
    candidates=[root/'tools'/'embeddinggemma2_swap'/'causal6_v1'/'ttm_causal6_h512_seal.py',
       root/'_tmp'/'ttm_causal6_source_h512_stage_20261109'/'code'/'ttm_causal6_h512_seal.py']
    trusted=[x for x in candidates if x.is_file() and git_blob(x)==H512_HELPER_GIT_BLOB]
    insist(bool(trusted),'H512_HELPER_SOURCE_SHA')
    helper=trusted[0]
    spec=importlib.util.spec_from_file_location('ttm_semantic4x3_legacy_h512_seal',str(helper))
    insist(spec and spec.loader,'LEGACY_HELPER_IMPORT')
    mod=importlib.util.module_from_spec(spec)
    sys.modules[spec.name]=mod;spec.loader.exec_module(mod)
    return mod


def publish_private(path,obj):
    payload=(json.dumps(obj,sort_keys=True,separators=(',',':'),ensure_ascii=False)+'\n').encode('utf-8')
    with Path(path).open('xb') as file:
        file.write(payload);file.flush();os.fsync(file.fileno())
    return sha(payload)


def seal(repo):
    root=Path(repo).resolve(strict=True)
    if os.name=='nt':insist(str(root).casefold()==r'd:\work\research\tokentomodel-lab','PROJECT_ROOT')
    insist(not root.is_symlink(),'PROJECT_ROOT_SYMLINK')
    output=root/'_tmp'/ROOT_NAME
    insist(not output.exists(),'H768_ALREADY_EXISTS_NO_RESELECTION')
    helper=load_legacy(root)
    root,src,groups,old320,iterator,bpe,win_fn=helper.check_src(root)
    previous=root/'_tmp'/'ttm_causal6_h512_seal_v1_20261109'
    memberfile=previous/'H512_PRIVATE_MEMBERSHIP.json'
    insist(memberfile.is_file() and file_sha(memberfile)==H512_PIN,'OLD_H512_MEMBERSHIP_PIN')
    old512=json.loads(memberfile.read_text('utf-8'))
    insist(old512.get('schema')=='ttm.causal6.h512.membership.private.v1' and
           old512.get('selection_count')==512,'H512_FORMAT')
    old512_ids=old512['story_sha256_ordered']
    insist(len(old512_ids)==512 and len(set(old512_ids))==512,'H512_IDS_COUNT')
    previous_public=previous/'H512_PUBLIC_SEAL.json'
    insist(previous_public.is_file() and file_sha(previous_public)==H512_PUBLIC_SHA,'OLD_H512_PUBLIC_PIN')
    excluded=set(groups['TRAIN']+groups['VAL']+groups['TEST']+old320+old512_ids)
    insist(len(groups['TRAIN'])==2048 and len(groups['VAL'])==256 and len(groups['TEST'])==64
      and len(old320)==320,'OLD_MEMBERSHIPS_COUNTS')
    heap=[];seen=set();skips=Counter();vcount=0
    for raw in iterator(src/'TinyStories-valid.txt'):
        vcount+=1;digest=sha(raw)
        if digest in excluded:
            # Excluded old TEST/H320/H512 NEVER decoded.
            skips['excluded_membership']+=1;continue
        if digest in seen:skips['duplicate_source']+=1;continue
        seen.add(digest)
        content=raw.decode('utf-8','strict')
        if not content.strip() or '\x00' in content:
            skips['invalid']+=1;continue
        if not helper.word5(content):skips['no_fivegram']+=1;continue
        key=rank_digest(digest)
        entry=(-int(key,16),digest,content)
        if len(heap)<K:heapq.heappush(heap,entry)
        elif key < f'{-heap[0][0]:064x}':heapq.heapreplace(heap,entry)
    insist(vcount==21990,'VALID_STORY_COUNT')
    insist(len(heap)==K,'NOT_ENOUGH_NEW_STORIES')
    chosen=sorted(heap,key=lambda x:-x[0]);names=[c[1] for c in chosen]
    insist(len(set(names))==K and not excluded.intersection(names),'EXACT_DUPLICATION')
    new=[(h,helper.word5(txt)) for _,h,txt in chosen]
    internal=sum(1 for i in range(K) for j in range(i)
      if helper.sim(new[i][1],new[j][1])>=0.85)
    insist(internal==0,'NEAR_DUPLICATES_WITHIN_H768_NO_RESELECTION')
    # Materialize only legacy T1 VALIDATION 256 texts (not historical TEST).
    val_wanted=set(groups['VAL']);old_val={}
    for raw in iterator(src/'TinyStories-valid.txt'):
        digest=sha(raw)
        if digest in val_wanted and digest not in old_val:
            old_val[digest]=helper.word5(raw.decode('utf-8','strict'))
    insist(set(old_val)==val_wanted,'OLD_VAL256_NOT_FOUND')
    bad_val,nval,maxval=helper.reject_near(new,[(x,old_val[x]) for x in groups['VAL']])
    insist(not bad_val,'NEAR_DUPLICATES_T1_VALIDATION')
    train_wanted=set(groups['TRAIN']);old_train={};train_count=0
    for raw in iterator(src/'TinyStories-train.txt'):
        train_count+=1;digest=sha(raw)
        if digest in train_wanted and digest not in old_train:
            old_train[digest]=helper.word5(raw.decode('utf-8','strict'))
    insist(train_count==2119489 and set(old_train)==train_wanted,'OLD_TRAIN2048_NOT_FOUND')
    bad_train,ntrain,maxtrain=helper.reject_near(new,[(x,old_train[x]) for x in groups['TRAIN']])
    insist(not bad_train,'NEAR_DUPLICATES_T1_TRAIN')
    xs=[];ys=[];counts=[];indices=[];story_counts=[]
    for i,(_,digest,content) in enumerate(chosen):
        ids=bpe.encode(content)+[256]
        story_counts.append(len(ids)-1)
        for x,y,c in win_fn(ids):
            xs.append(x);ys.append(y);counts.append(c);indices.append(i)
    insist(sum(story_counts)==sum(counts)>0,'TARGET_COUNTS')
    metadata={'schema':'ttm.semantic4x3.h768.private_membership.v1',
      'selection_count':K,'selection_domain':DOMAIN.decode('ascii'),
      'source_valid_sha256':helper.RAW_SHA['TinyStories-valid.txt'],
      'source_train_sha256':helper.RAW_SHA['TinyStories-train.txt'],
      't1_split_sha256':helper.SPLIT_SHA,'t1_bpe_sha256':helper.BPE_SHA,
      'old_320_membership_sha256':helper.OLD320_SHA,'old_h512_membership_sha256':H512_PIN,
      'story_sha256_ordered':names,'story_target_counts':story_counts,'target_count':sum(counts),
      'window_count':len(counts),'old_TEST_text_read':False,
      'old_320_text_read':False,'old_H512_text_read':False,
      'near_self_pairs':0,'near_T1_TRAIN_pairs':ntrain,'near_T1_VALIDATION_pairs':nval,
      'raw_train_scanned':train_count,'raw_valid_scanned':vcount,
      'science_training':False,'model_forward':False,'gpu_used':False}
    # Writes only after all finite source / data gates pass; never overwrite.
    output.mkdir(parents=True,exist_ok=False)
    hmembership=publish_private(output/'H768_MEMBERSHIP_PRIVATE.json',metadata)
    npz=output/'H768_WINDOWS_PRIVATE.npz'
    with npz.open('xb') as fd:
        np.savez_compressed(fd,x=np.asarray(xs,dtype=np.int16),y=np.asarray(ys,dtype=np.int16),
          count=np.asarray(counts,dtype=np.int16),story_index=np.asarray(indices,dtype=np.int32))
    with np.load(npz,allow_pickle=False) as data:
        insist(set(data.files)=={'x','y','count','story_index'} and data['x'].shape==(len(counts),256)
            and int(data['count'].sum())==sum(counts),'H768_PACK_READBACK')
    public={'schema':'ttm.semantic4x3.h768.public_seal.v1',
      'status':'H768_SEALED_NOT_SCORED','stories':K,'windows':len(counts),
      'targets':sum(counts),'membership_private_sha256':hmembership,
      'pack_private_sha256':file_sha(npz),'source_valid_sha256':helper.RAW_SHA['TinyStories-valid.txt'],
      'excluded_exact_source_count':skips['excluded_membership'],
      'near_self_pairs':internal,'near_T1_TRAIN_pairs':ntrain,'near_T1_VALIDATION_pairs':nval,
      'old_TEST_text_materialized':False,'old_H320_text_materialized':False,
      'old_H512_text_materialized':False,'claim_created':False,'model_forward_calls':0,
      'limitations':['Same TinyStories-valid domain','Old consumed holdouts only exact ID exclusion, not near-dup text audit','Unknown donor pretraining overlap']}
    publish_private(output/'H768_PUBLIC_SEAL.json',public)
    print(json.dumps(public,sort_keys=True));print('H768_PUBLIC_SEAL_SHA256='+file_sha(output/'H768_PUBLIC_SEAL.json'))


if __name__=='__main__':
    ap=argparse.ArgumentParser();ap.add_argument('--mode',required=True,choices=['fixture','seal']);ap.add_argument('--repo',default='')
    args=ap.parse_args()
    if args.mode=='fixture':fixture()
    else:insist(bool(args.repo),'REPO_REQUIRED');seal(args.repo)
