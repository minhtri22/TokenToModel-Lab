#!/usr/bin/env python3
"""A0C integrated CPU-only QA for private pinned T1, input-only null and exact A0B.
No external downloads, training, model.forward, TEST/H768/OOD256 read or loss.
"""
import argparse,hashlib,io,json,re,subprocess,sys,zipfile
from pathlib import Path
import numpy as np,torch
T1_SHA='cba18e60cee3d08a353ee6d4a451017289e45af7b4b1179c87171b9b78d7dfdc'
T1_INTERNAL='6da22cf79c3a6cfd08d80a768eb1074125a753164ccf62a164e79545956e94c6'
T1_MERGES='aea0e2a1a1bc1943f20b767ba2f879e3a47f0cb43b8b66026b1a34a038e014af'
SOURCE_SHA='2c6cb72f35eba72d6014f15914d6e9792cbf0bf6774d93e3ff5c53e5c6b9ba9a'
CAND_SHA='c9fc798d8880c7e76636258052e9885dbb086d7b462a5b6bee5cff8b582973c3'
TRAIN_SHA='184f68b4c0c800ef3e98362c2e20e1cd35baa269e926489a4751ed5c8747'
A0B_GIT_BLOB='856b07246261bd637dedb320fb2f79eeeac27a67'
NULL_NPY_SHA='9c3b4e5e5ac105c31742ae52ae648aa2c2b727a95ee01ec62d45e15331e935c7'
NULL_RAW_SHA='b6bfe073898ff1f117499272e2798dc9e9d5dca80431c301fadbc951e55837a1'

def need(c,reason):
 if not bool(c):raise RuntimeError('HOLD_A0C_'+reason)
def sha(b):return hashlib.sha256(b).hexdigest()
def streamsha(path):
 h=hashlib.sha256()
 with open(path,'rb') as f:
  for b in iter(lambda:f.read(8*1024*1024),b''):h.update(b)
 return h.hexdigest()
def githash(b):return hashlib.sha1(('blob '+str(len(b))+'\0').encode()+b).hexdigest()
def invert_gpt2():
 bs=list(range(33,127))+list(range(161,173))+list(range(174,256));cs=bs.copy();n=0
 for i in range(256):
  if i not in bs:bs.append(i);cs.append(256+n);n+=1
 return {v:k for k,v in zip(bs,map(chr,cs))}
def get_manifest(path):
 data=Path(path).read_bytes();need(sha(data)==T1_SHA,'T1_FILE_SHA')
 m=json.loads(data); claimed=m.pop('manifest_sha256')
 need(claimed==T1_INTERNAL and sha(json.dumps(m,ensure_ascii=False,sort_keys=True,separators=(',',':')).encode())==T1_INTERNAL,'T1_INTERNAL_SHA')
 need(m['vocab_size']==2048 and m['eos_id']==256 and len(m['pair_ids'])==1791,'T1_SCHEMA')
 invert=invert_gpt2();forward={v:k for k,v in invert.items()}
 t=[forward[i] for i in range(256)]+['<|endoftext|>']
 for i,(a,b) in enumerate(m['pair_ids']):
  need(0<=a<257+i and 0<=b<257+i,'PAIR_ID_RANGE')
  t.append(t[a]+t[b])
 need(t==m['tokens'] and len(set(t))==2048,'TOKEN_REPLAY')
 merges=[t[a]+' '+t[b] for a,b in m['pair_ids']]
 need(sha(json.dumps([t,merges],ensure_ascii=False,sort_keys=True,separators=(',',':')).encode())==T1_MERGES and m['token_merges_sha256']==T1_MERGES,'MERGE_SHA')
 decoded=[]
 for x in t:
  try:decoded.append(bytes(invert[k] for k in x).decode('utf8'))
  except (KeyError,UnicodeDecodeError):decoded.append(None)
 return decoded

def run(args):
 decoded=get_manifest(args.t1)
 need(streamsha(args.source)==SOURCE_SHA,'SOURCE_PIN')
 with zipfile.ZipFile(args.source) as z:
  candidate=z.read('input\\candidate_initialization.pt');train=z.read('input\\T4_PRIVATE_TRAIN_VAL_WINDOWS.npz')
  need(sha(candidate)==CAND_SHA and sha(train)==TRAIN_SHA,'CANDIDATE_AND_TRAIN_PIN')
  valid=torch.load(io.BytesIO(candidate),map_location='cpu',weights_only=True)['model_state_dict']['tok.valid'].numpy().astype(bool)
  need(valid.shape==(2048,) and valid.sum()==1917,'VALID_MASK_COUNT')
  need(not valid[256] and all((decoded[i] is not None)==bool(valid[i]) for i in range(2048) if i!=256),'VALID_MASK_UTF8_PARITY')
  with np.load(io.BytesIO(train),allow_pickle=False) as d:
   x=d['train_x'];count=d['train_count']
   need(x.ndim==2 and x.shape[1]==256 and count.shape==(len(x),),'TRAIN_SHAPE')
   freq=np.bincount(x[np.arange(256)[None,:]<count[:,None]],minlength=2048)
 ascii_word=np.array([bool(valid[i]) and bool(re.fullmatch(' ?[A-Za-z]+',s or '')) for i,s in enumerate(decoded)])
 initial_space=np.array([bool(ascii_word[i]) and decoded[i].startswith(' ') for i in range(2048)])
 # An input-only seeded control is not the full 24-layer EmbeddingGemma 2.
 need(streamsha(args.null_source)==NULL_NPY_SHA,'NULL_NPY_SHA')
 a=np.load(args.null_source,mmap_mode='r',allow_pickle=False)
 need(a.shape==(262144,512) and a.dtype==np.float32 and not a[0].any(),'NULL_SHAPE_AND_PAD')
 h=hashlib.sha256()
 for i in range(0,len(a),2048):h.update(np.asarray(a[i:i+2048]).tobytes(order='C'))
 need(h.hexdigest()==NULL_RAW_SHA,'NULL_RAW_SHA')
 # Frozen GitHub A0B source must match byte-for-byte before replaying on real donor.
 b=Path(args.a0b).read_bytes();need(githash(b)==A0B_GIT_BLOB,'A0B_GIT_BLOB')
 cmd=[sys.executable,args.a0b,'--mode','private-audit','--source-zip',args.source]
 p=subprocess.run(cmd,check=True,capture_output=True,text=True)
 result=json.loads(p.stdout.splitlines()[-1]);need(result['status'].startswith('PASS_A0B_') and result['model_forward_calls']==0 and result['training_executed'] is False,'A0B_RESULT')
 out={'schema':'ttm.gemma2.a0c.integrated.private_cpu_gate.v1',
  'status':'SOURCE_INTEGRITY_PASS_CONTROL_ADMISSION_PARTIAL',
  'manifest_sha256':T1_SHA,'internal_manifest_sha256':T1_INTERNAL,'merges_sha256':T1_MERGES,
  'token_count':2048,'merges_count':1791,'mapped_valid_UTF8':int(valid.sum()),
  'incomplete_UTF8_count':int(sum(z is None for z in decoded)),
  'ASCII_word_candidate_token_ids':int(ascii_word.sum()),
  'space_prefixed_ASCII_word_candidate_ids':int(initial_space.sum()),
  'space_prefixed_ASCII_token_ids_TRAIN_frequency_ge10':int(sum(initial_space & (freq>=10))),
  'space_prefixed_ASCII_token_ids_TRAIN_frequency_ge50':int(sum(initial_space & (freq>=50))),
  'semantic_labels_verified_by_this_source_only':False,
  'untrained_input_only_table_sha256':NULL_NPY_SHA,'untrained_raw_float32_sha256':NULL_RAW_SHA,
  'untrained_full_24_layer_model_constructed':False,
  'untrained_same_donor_tokenizer_mapping_verified':False,
  'a0b_exact_git_blob':A0B_GIT_BLOB,
  'a0b_status':result['status'],'a0b_covariance_relative_fro':result['global_covariance_relative_fro'],
  'a0b_projected_fp32_max':result['max_projected_input_abs_fp32'],
  'a0b_rownorm_fp32_max':result['max_token_norm_abs_fp32'],
  'a0b_neighborhood_top10_overlap':result['residual_top10_neighbor_overlap'],
  'new_science':False,'model_forward_calls':0,'training_executed':False,
  'recommendation':'HOLD_T4_2X2_PENDING_DONOR_TOKENIZER_MAPPING_AND_FULL_SAME_ARCH_CONTROL'}
 return out
if __name__=='__main__':
 parser=argparse.ArgumentParser()
 for name in ('t1','source','null_source','a0b'):parser.add_argument('--'+name.replace('_','-'),required=True)
 a=parser.parse_args()
 print(json.dumps(run(a),sort_keys=True))
