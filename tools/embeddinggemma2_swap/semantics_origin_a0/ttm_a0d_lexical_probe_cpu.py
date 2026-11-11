#!/usr/bin/env python3
"""TRAIN-frequency/morphology-matched exploratory lexical probe on frozen input rows.

No Transformer forward, no LM training, no H768/OOD256/TEST outcomes.  The
observational score cannot isolate provenance of pretraining nor prove causality.
Only aggregate receipts are printed. The human-rated pairs stay private.
"""
from __future__ import annotations
import argparse, difflib, hashlib, io, json, math, zipfile
from pathlib import Path
import numpy as np
from scipy.optimize import linear_sum_assignment
from scipy.stats import spearmanr
import torch

SOURCE_ZIP_SHA='2c6cb72f35eba72d6014f15914d6e9792cbf0bf6774d93e3ff5c53e5c6b9ba9a'
T1_SHA='cba18e60cee3d08a353ee6d4a451017289e45af7b4b1179c87171b9b78d7dfdc'
CAND_SHA='c9fc798d8880c7e76636258052e9885dbb086d7b462a5b6bee5cff8b582973c3'
TRAIN_SHA='184f68b4c0c800ef3e98362c2e20e1cd35baa269e926489a475664526ecd9913'
SEED=2026111196

def require(ok,reason):
 if not ok:raise RuntimeError('A0D_HOLD_'+reason)
def sha_file(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def bpe_decode(encoded):
 bs=list(range(33,127))+list(range(161,173))+list(range(174,256));cs=bs.copy();n=0
 for x in range(256):
  if x not in bs:bs.append(x);cs.append(256+n);n+=1
 inv=dict(zip(map(chr,cs),bs));out=[]
 for t in encoded:
  try:out.append(bytes(inv[x] for x in t).decode('utf-8'))
  except (KeyError,UnicodeDecodeError):out.append(None)
 return out

def data(t1,source):
 require(sha_file(t1)==T1_SHA,'T1_SHA')
 require(sha_file(source)==SOURCE_ZIP_SHA,'SOURCE_ZIP_SHA')
 m=json.loads(Path(t1).read_bytes()); dec=bpe_decode(m['tokens'])
 words={}
 for i,x in enumerate(dec):
  if x and x.startswith(' ') and x[1:].isascii() and x[1:].isalpha() and x[1:].islower():
   words.setdefault(x[1:],[]).append(i)
 words={k:v[0] for k,v in words.items() if len(v)==1}
 with zipfile.ZipFile(source) as z:
  candidate=z.read('input\\candidate_initialization.pt')
  train=z.read('input\\T4_PRIVATE_TRAIN_VAL_WINDOWS.npz')
  require(hashlib.sha256(candidate).hexdigest()==CAND_SHA and hashlib.sha256(train).hexdigest()==TRAIN_SHA,'CAND_TRAIN_SHA')
  ck=torch.load(io.BytesIO(candidate),weights_only=True,map_location='cpu')['model_state_dict']
  source_rows=ck['tok.source.weight'].numpy().astype(np.float64)
  valid=ck['tok.valid'].numpy().astype(bool)
  with np.load(io.BytesIO(train),allow_pickle=False) as a:
   X=a['train_x'];L=a['train_count'];freq=np.bincount(X[np.arange(X.shape[1])[None,:]<L[:,None]],minlength=2048)
  words={w:i for w,i in words.items() if valid[i]}
 return words,source_rows,freq

def features(pair,freq,words):
 a,b,_=pair;ia=words[a];ib=words[b]
 la,lb=len(a),len(b)
 fa,fb=np.log1p(freq[ia]),np.log1p(freq[ib])
 return np.array([(la+lb)/2,abs(la-lb),min(la,lb),
   (fa+fb)/2,abs(fa-fb),min(fa,fb),
   difflib.SequenceMatcher(None,a,b).ratio(),float(a[0]==b[0])],dtype=float)

def run(args):
 words,rows,freq=data(args.t1,args.source)
 pairs=[]
 for line in Path(args.simlex_derived).read_text().splitlines():
  a,b,score=line.split('\t');score=float(score)
  if a in words and b in words:pairs.append((a,b,score))
 require(len(pairs)==76,'SIMLEX_DERIVED_SOURCE_MATCHES')
 high=[p for p in pairs if p[2]>=5.0]
 low=[p for p in pairs if p[2]<=3.0]
 require(len(high)>=20 and len(low)>=20,'PAIR_COVERAGE')
 hf=np.array([features(p,freq,words) for p in high]);lf=np.array([features(p,freq,words) for p in low])
 sd=np.maximum(np.std(np.vstack([hf,lf]),axis=0),0.05)
 cost=(np.abs((hf[:,None,:]-lf[None,:,:])/sd)*np.array([.5,.25,.25,1.0,.5,.5,.75,.2])).sum(2)
 i,j=linear_sum_assignment(cost)
 selected_hi=[high[x] for x in i];selected_lo=[low[x] for x in j]
 norm=rows/np.maximum(np.linalg.norm(rows,axis=1,keepdims=True),1e-30)
 def score(p):return float(norm[words[p[0]]]@norm[words[p[1]]])
 hi_cos=np.array([score(p) for p in selected_hi]);lo_cos=np.array([score(p) for p in selected_lo]);
 human=np.array([p[2] for p in selected_hi+selected_lo]); donor=np.array([score(p) for p in selected_hi+selected_lo]);
 morph=np.array([difflib.SequenceMatcher(None,p[0],p[1]).ratio() for p in selected_hi+selected_lo]);
 diff=float(np.mean(hi_cos)-np.mean(lo_cos))
 rng=np.random.default_rng(SEED)
 shuffled=0
 for _ in range(10000):
  idx=rng.permutation(len(donor))
  shuffled+=float(np.mean(donor[idx[:len(hi_cos)]])-np.mean(donor[idx[len(hi_cos):]]))>=diff
 pvalue=(shuffled+1)/10001
 rho=float(spearmanr(donor,human).statistic)
 morph_rho=float(spearmanr(morph,human).statistic)
 match_diff=np.abs(hf[i].mean(0)-lf[j].mean(0))/sd
 unique_words=len(set([x for p in selected_hi+selected_lo for x in p[:2]]))
 labels={'high_ge5':len(high),'low_le3':len(low),'matched_each':len(i)}
 r={'schema':'ttm.gemma2.a0d.exploratory_lexical_probe.v1',
 'status':'PASS_BALANCED_SOURCE_MATCHING_EXPLORATORY_ONLY',
 'simlex_original_git_blob':'b642f3abe39c9ff1c9d6f942c917e47fd6c3801d',
 'simlex_derived_private_sha256':sha_file(args.simlex_derived),
 'labels_source':'SIMLEX999_HUMAN_RATINGS_NOT_LM_TEST',
 'T1_manifest_sha256':T1_SHA,'private_source_SHA256':SOURCE_ZIP_SHA,
 'pair_pool':len(pairs),'candidate_counts':labels,
 'features':['mean_len','len_gap','min_len','mean_logfreq','logfreq_gap','min_logfreq','char_similarity','same_initial'],
 'matched_feature_abs_standardized_mean_gap':[float(x) for x in match_diff],
 'matched_unique_word_count':unique_words,
 'matched_pairs_with_shared_word':2*len(i)*2-unique_words,
 'donor_cos_high_mean':float(hi_cos.mean()),'donor_cos_low_mean':float(lo_cos.mean()),
 'donor_cos_difference_high_minus_low':diff,
 'spearman_rho_donor_vs_human':rho,'spearman_rho_character_similarity_vs_human':morph_rho,
 'label_permutation_count':10000,'naive_permutation_pvalue':pvalue,
 'permutation_invalid_as_independent_significance_due_to_repeated_word_identity':True,
 'source_lexical_probe_is_not_confirmatory':True,
 'pretrained_semantic_causal_effect_established':False,
 'matched_5_threshold_is_exploratory_not_preregistered':True,
 'train_frequency_only':True,'LM_model_forward_calls':0,'training':False,'OOT_or_H768_eval_read':False,
 'recommendation':'HOLD_PRETRAINED_CAUSAL_CLAIM_AND_REQUIRE_INDEPENDENT_NEW_LEXICAL_TEST_AND_PINNED_DONOR_MAPPING'}
 print(json.dumps(r,sort_keys=True,allow_nan=False))
 return r

if __name__=='__main__':
 p=argparse.ArgumentParser()
 p.add_argument('--t1',required=True);p.add_argument('--source',required=True);p.add_argument('--simlex-derived',required=True)
 run(p.parse_args())
