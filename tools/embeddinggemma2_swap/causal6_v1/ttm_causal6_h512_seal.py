#!/usr/bin/env python3
"""H512 new holdout seal: pinned TinyStories, fixed hash membership, no TEST decode.
Source-only code; never scores a model. Private .npz and membership remain local.
"""
from __future__ import annotations
import argparse
from collections import Counter
import hashlib, heapq, json, os, sys
from pathlib import Path
import numpy as np

RAW_SHA={'TinyStories-train.txt':'c5cf5e22ff13614e830afbe61a99fbcbe8bcb7dd72252b989fa1117a368d401f','TinyStories-valid.txt':'94e431816c4cce81ff71e4408ff8d3bda9a42e8d2663986697c3954288cb38b4'}
SPLIT_SHA='9f2ebaca821bddf0a9d7ae30ccfcef34561b968b21159aa913794298235a2fa9'
BPE_SHA='cba18e60cee3d08a353ee6d4a451017289e45af7b4b1179c87171b9b78d7dfdc'
OLD320_SHA='bedc3671256a66f605fbeb9f98bbd27149b456019d3d8bc5bbc89ebca6d09b47'
T1_PARSER_BLOB='3ef500ddd8259153e7e3d4602915a51b7060a40f'
T1_BPE_BLOB='fa5bd892941ba5aa6e6b2f0b2b0ae974efe297b6'
DOMAIN=b'TTM_CAUSAL6_H512_V1_20261109\0'
K=512
THRESHOLD=.85
RUN='ttm_causal6_h512_seal_v1_20261109'

def insist(c,msg):
 if not bool(c):raise RuntimeError('HOLD_'+msg)

def sha(b):return hashlib.sha256(b).hexdigest()

def file_sha(p):
 h=hashlib.sha256()
 with Path(p).open('rb') as f:
  for x in iter(lambda:f.read(1<<20),b''):h.update(x)
 return h.hexdigest()

def gitblob(p):
 b=Path(p).read_bytes();return hashlib.sha1(b'blob '+str(len(b)).encode()+b'\0'+b).hexdigest()

def word5(t):
 v=t.casefold().split()
 return frozenset(tuple(v[i:i+5]) for i in range(len(v)-4))

def sim(a,b):
 if not a or not b or min(len(a),len(b))<THRESHOLD*max(len(a),len(b)):return 0.
 n=len(a&b)
 return n/(len(a)+len(b)-n) if n else 0.

def rank(digest):return sha(DOMAIN+digest.encode('ascii'))

def private_write_new(p,obj):
 b=(json.dumps(obj,ensure_ascii=False,sort_keys=True,separators=(',',':'))+'\n').encode('utf-8')
 with p.open('xb') as f:f.write(b);f.flush();os.fsync(f.fileno())
 return sha(b)

def check_src(root):
 root=root.resolve(strict=True)
 if os.name=='nt':insist(str(root).casefold()==r'd:\work\research\tokentomodel-lab','PROJECT_SCOPE')
 insist(not root.is_symlink(),'PROJECT_SYMLINK')
 t1=root/'tools'/'pilot_t1t3'
 insist(gitblob(t1/'t1_source_split_tokenizer.py')==T1_PARSER_BLOB,'T1_PARSER_BLOB')
 insist(gitblob(t1/'source_t2'/'ttm_gpt2_bpe2048.py')==T1_BPE_BLOB,'T1_BPE_BLOB')
 base=root/'_tmp'/'ttm_t1_real_source_v1'
 split=base/'T1_STORY_SPLIT_IDS_NO_RAW_TEXT.json';bpe=base/'T1_BPE2048_REAL_TRAIN_MANIFEST.json'
 hold=root/'_tmp'/'ttm_gemma2_new_holdout_membership_v1_20261109'/'MEMBERSHIP_PRIVATE.json'
 insist(file_sha(split)==SPLIT_SHA and file_sha(bpe)==BPE_SHA,'SPLIT_BPE_PIN')
 insist(file_sha(hold)==OLD320_SHA,'L0017_MEMBERSHIP_PIN')
 src=root/'datasets'/'tinystories_v1_original_pinned'
 for name,pin in RAW_SHA.items():insist(file_sha(src/name)==pin,'RAW_SOURCE_SHA_'+name)
 s=json.loads(split.read_text('utf-8'));old=json.loads(hold.read_text('utf-8'))
 groups=s['splits']
 insist({k:len(groups[k]) for k in ('TRAIN','VAL','TEST')}=={'TRAIN':2048,'VAL':256,'TEST':64},'GROUP_COUNTS')
 old320=old['story_sha256_ordered']
 insist(len(old320)==320 and len(set(old320))==320,'OLD320_COUNT')
 sys.path.insert(0,str(root/'tools'/'pilot_t4'/'integrated'))
 sys.path.insert(0,str(t1))
 from t1_source_split_tokenizer import iter_story_bytes
 from source_t2.ttm_gpt2_bpe2048 import BPE2048
 from t4_data_pack import windows_for_ids
 tokenizer=BPE2048.from_manifest(json.loads(bpe.read_text('utf-8')))
 insist(tokenizer.source_kind=='PINNED_TINYSTORIES_TRAIN','BPE_ORIGIN')
 return root,src,groups,old320,iter_story_bytes,tokenizer,windows_for_ids

def reject_near(new, old):
 # Candidate-centered inverted lookup: exact for every pair with similarity >= threshold.
 inv={}
 for i,(h,signature) in enumerate(new):
  for k in signature:inv.setdefault(k,[]).append(i)
 affected=set();overlaps=0;maxsim=0.
 for _,signature in old:
  cnt=Counter()
  for k in signature:
   for i in inv.get(k,()):cnt[i]+=1
  for i,c in cnt.items():
   na=len(new[i][1]);nb=len(signature)
   if min(na,nb)<THRESHOLD*max(na,nb):continue
   value=c/(na+nb-c)
   maxsim=max(maxsim,value)
   if value>=THRESHOLD:affected.add(i);overlaps+=1
 return affected,overlaps,maxsim

def fixture():
 assert sim(word5('a b c d e f g h'),word5('a b c d e f g h'))==1.
 assert sim(word5('a b c d e f g h'),word5('x y z p q r t u'))==0.
 x=' '.join('word'+str(i) for i in range(100))
 y=x.replace('word20','other20')
 assert sim(word5(x),word5(y))>=THRESHOLD
 assert rank('a'*64)==rank('a'*64) and rank('a'*64)!=rank('b'*64)
 n=[('a',word5(x)),('b',word5(' '.join('another'+str(j) for j in range(30))))]
 h,k,m=reject_near(n,[('test',word5(y))])
 assert h=={0} and k==1 and m>=THRESHOLD
 print(json.dumps({'schema':'ttm.causal6.h512.synthetic.v1','status':'PASS','checks':5,'real_data_read':False,'gpu_used':False,'model_scored':False}))

def seal(repo):
 root,src,groups,old320,iterator,bpe,win_fn=check_src(Path(repo))
 output=root/'_tmp'/RUN
 insist(not output.exists(),'H512_SEAL_ALREADY_EXISTS_NO_RESELECT')
 excluded=set(groups['TRAIN']+groups['VAL']+groups['TEST']+old320)
 heap=[];seen=set();val_sigs={};skips=Counter();vcount=0
 for raw in iterator(src/'TinyStories-valid.txt'):
  vcount+=1
  h=sha(raw)
  if h in excluded:
   # Historical TEST and L0017 are NEVER decoded into text.
   skips['EXCLUDED_OLD_MEMBERSHIP']+=1
   continue
  if h in seen:skips['DUPLICATE_SOURCE']+=1;continue
  seen.add(h)
  t=raw.decode('utf-8','strict')
  if not t.strip() or '\x00' in t:skips['INVALID']+=1;continue
  w=word5(t)
  if not w:skips['NO_5GRAM']+=1;continue
  key=rank(h)
  entry=(-int(key,16),h,t)
  if len(heap)<K:heapq.heappush(heap,entry)
  elif key < f'{-heap[0][0]:064x}':heapq.heapreplace(heap,entry)
 # This ordered set is IMMUTABLE even if later contamination is found; fail, never replace.
 insist(len(heap)==K,'H512_NOT_ENOUGH_ELIGIBLE')
 chosen=sorted(heap,key=lambda x:-x[0]);ids=[v[1] for v in chosen]
 insist(len(set(ids))==K and not set(ids)&excluded,'SELECTED_OVERLAP')
 new=[(h,word5(t)) for _,h,t in chosen]
 bad_internal=[]
 for i in range(K):
  for j in range(i):
   if sim(new[i][1],new[j][1])>=THRESHOLD:bad_internal.append((i,j))
 insist(not bad_internal,'H512_INTERNAL_NEAR_DUP')
 # Re-read VALID source but only materialize historically selected VAL256 texts.
 wanted=set(groups['VAL']);val_found={}
 for raw in iterator(src/'TinyStories-valid.txt'):
  h=sha(raw)
  if h in wanted and h not in val_found:
   val_found[h]=word5(raw.decode('utf-8','strict'))
 insist(set(val_found)==wanted,'OLD_VAL_NOT_FOUND')
 old_val=[(x,val_found[x]) for x in groups['VAL']]
 bad_val,nval,maxval=reject_near(new,old_val)
 insist(not bad_val,'H512_NEAR_OLD_VALIDATION')
 # Full TRAIN stream hash; decode only 2,048 authorized TRAIN stories, not arbitrary corpus.
 train_wanted=set(groups['TRAIN']);train_found={};total_train=0
 for raw in iterator(src/'TinyStories-train.txt'):
  total_train+=1
  h=sha(raw)
  if h in train_wanted and h not in train_found:
   train_found[h]=word5(raw.decode('utf-8','strict'))
 insist(total_train==2119489 and set(train_found)==train_wanted,'OLD_TRAIN_NOT_FOUND')
 bad_train,ntrain,maxtrain=reject_near(new,[(x,train_found[x]) for x in groups['TRAIN']])
 insist(not bad_train,'H512_NEAR_TRAIN')
 xs=[];ys=[];counts=[];sis=[];target_per_story=[]
 for i,(_,h,t) in enumerate(chosen):
  ids0=bpe.encode(t)+[256]
  target_per_story.append(len(ids0)-1)
  for x,y,n in win_fn(ids0):
   xs.append(x);ys.append(y);counts.append(n);sis.append(i)
 insist(sum(counts)==sum(target_per_story)>0,'TARGET_COUNTS')
 meta={'schema':'ttm.causal6.h512.membership.private.v1','source_hashes':RAW_SHA,
 'split_sha256':SPLIT_SHA,'prior_l0017_sha256':OLD320_SHA,'bpe_file_sha256':BPE_SHA,
 'selection_domain':DOMAIN.decode('ascii'),'selection_count':512,'story_sha256_ordered':[z[1] for z in chosen],
 'story_target_counts':target_per_story,'target_count':sum(counts),'window_count':len(counts),
 'raw_train_stories_scanned':total_train,'raw_valid_stories_scanned':vcount,
 'Jaccard5_threshold':THRESHOLD,'near_old_train_count':ntrain,'near_old_val_count':nval,
 'near_internal_count':len(bad_internal),'history_64_test_text_read':False,
 'prior_320_text_read_for_model':False,'science_executed':False,'gpu_used':False}
 output.mkdir(parents=True,exist_ok=False)
 mid=private_write_new(output/'H512_PRIVATE_MEMBERSHIP.json',meta)
 p=output/'H512_PRIVATE_WINDOWS.npz'
 with p.open('xb') as fd:
  np.savez_compressed(fd,x=np.asarray(xs,dtype=np.int16),y=np.asarray(ys,dtype=np.int16),count=np.asarray(counts,dtype=np.int16),story_index=np.asarray(sis,dtype=np.int32))
 with np.load(p,allow_pickle=False) as d:
  assert d['x'].shape==(len(counts),256) and int(d['count'].sum())==meta['target_count']
 receipt={'schema':'ttm.causal6.h512.public_seal.v1','status':'H512_SEALED_NOT_SCORED',
 'stories':512,'windows':len(counts),'targets':sum(counts),'source_raw_valid_sha256':RAW_SHA['TinyStories-valid.txt'],
 'source_raw_train_sha256':RAW_SHA['TinyStories-train.txt'],
 'prior_membership_SHA256':OLD320_SHA,'membership_private_sha256':mid,'h512_window_pack_sha256':file_sha(p),
 'excluded_old_exact_sha256_count':skips['EXCLUDED_OLD_MEMBERSHIP'],
 'near_train_pairs':ntrain,'near_val_pairs':nval,'near_internal_pairs':len(bad_internal),
 'max_observed_old_train_shingle_similarity_nonzero':round(maxtrain,9),
 'max_observed_old_val_shingle_similarity_nonzero':round(maxval,9),
 'test_text_materialized':False,'old_320_text_for_scoring':False,'model_forward_calls':0,
 'gpu_used':False,'selection_reopened':False,
 'limitations':['Near-duplication with old TEST/old holdout320 not audited; exact SHA exclusion only',
 'Donor pretraining corpus may overlap','Same TinyStories-valid family, not domain independence']}
 private_write_new(output/'H512_PUBLIC_SEAL.json',receipt)
 print(json.dumps(receipt,sort_keys=True,ensure_ascii=False))
 print('H512_PUBLIC_SEAL_SHA256='+file_sha(output/'H512_PUBLIC_SEAL.json'))
 print('H512_PRIVATE_FOLDER='+str(output))

if __name__=='__main__':
 ap=argparse.ArgumentParser();ap.add_argument('--mode',choices=['fixture','seal'],required=True);ap.add_argument('--repo',default='')
 a=ap.parse_args();fixture() if a.mode=='fixture' else seal(a.repo)
