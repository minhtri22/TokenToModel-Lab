#!/usr/bin/env python3
"""Read-only real-T1-BPE audit of public synthetic TRAIN/DEV external fact fixtures.

No TEST read/decryption, no model load/training/inference. Fail closed without
pinned original TRAIN-only BPE manifest; do not substitute GPT2/tiktoken BPE.
"""
from __future__ import annotations
import argparse, hashlib, importlib.util, json, sys
from pathlib import Path

T1_SHA='cba18e60cee3d08a353ee6d4a451017289e45af7b4b1179c87171b9b78d7dfdc'
BPE_BLOB='fa5bd892941ba5aa6e6b2f0b2b0ae974efe297b6'
SRC_TRAIN_SHA='1c44055fae2281015228b74b3b6e3dffa513becd9207d43c28658ef063a6a57d'
SRC_DEV_SHA='fd68373f7765eead4cd5744584abc71d5377bc184863e28cdef7ad3cdfc3e05f'
CTX=256

def sha(b:bytes)->str:return hashlib.sha256(b).hexdigest()
def gitblob(b:bytes)->str:return hashlib.sha1(b'blob '+str(len(b)).encode()+b'\0'+b).hexdigest()
def load_code(p:Path):
  spec=importlib.util.spec_from_file_location('ttm_t1_real_bpe',p)
  m=importlib.util.module_from_spec(spec)
  sys.modules[spec.name]=m;spec.loader.exec_module(m)
  return m

def run(args):
  if not args.tokenizer_manifest or not args.tokenizer_manifest.is_file():
    return {'status':'HOLD_REAL_T1_MANIFEST_MISSING','science':'NOT_EXECUTED',
      'expected_manifest_sha256':T1_SHA,'test_status':'NOT_READ_OR_DECRYPTED'}
  manifest_bytes=args.tokenizer_manifest.read_bytes()
  if sha(manifest_bytes)!=T1_SHA:raise ValueError('WRONG_T1_TOKENIZER_SHA256')
  if gitblob(args.t1_bpe_source.read_bytes())!=BPE_BLOB:raise ValueError('WRONG_T1_BPE_PYTHON_GIT_BLOB')
  mod=load_code(args.t1_bpe_source)
  bpe=mod.BPE2048.from_manifest(json.loads(manifest_bytes))
  assert bpe.source_kind=='PINNED_TINYSTORIES_TRAIN', 'NOT_REAL_TRAIN_ONLY_TOKENIZER'
  assert bpe.manifest()['manifest_sha256']==json.loads(manifest_bytes)['manifest_sha256']
  assert sha(args.train_fixture.read_bytes())==SRC_TRAIN_SHA
  assert sha(args.dev_fixture.read_bytes())==SRC_DEV_SHA
  cases=[]
  for split,f in [('train',args.train_fixture),('dev',args.dev_fixture)]:
    obj=json.loads(f.read_bytes());assert obj['split']==split
    cases.extend(obj['cases'])
  max_question=0;max_answer=0;max_joint=0;total_label_tokens=0
  seen_answer_tokens=set();prefix_mismatches=0
  for c in cases:
    q=c['question'];a=c['answer'];combined=q+' '+a
    qids=bpe.encode(q);joint=bpe.encode(combined)
    label_ids=joint[len(qids):]
    assert all(0<=x<2048 for x in qids+joint) and 256 not in qids+joint
    assert bpe.decode(qids)==q and bpe.decode(joint)==combined
    if joint[:len(qids)]!=qids:prefix_mismatches+=1
    assert len(qids)<=CTX and len(joint)<=CTX and len(label_ids)>=1
    max_question=max(max_question,len(qids));max_answer=max(max_answer,len(label_ids));max_joint=max(max_joint,len(joint))
    total_label_tokens+=len(label_ids)
    seen_answer_tokens.update(label_ids)
    for card in c['correct_memory']+c['wrong_memory']:
      ids=bpe.encode(card['text'])
      assert len(ids)<=CTX and bpe.decode(ids)==card['text']
  # Must explicitly detect any prefix re-tokenization that would invalidate
  # answer-only teacher-forcing assumptions.
  return {'status':'PASS_REAL_T1_TOKENIZER' if prefix_mismatches==0 else 'FAIL_ANSWER_BOUNDARY_PREFIX_MISMATCH',
    'input_cases':len(cases),'splits':['train','dev'],'test_status':'NOT_READ_OR_DECRYPTED',
    't1_sha256':sha(manifest_bytes),'bpe_source_git_blob':BPE_BLOB,'context_limit':CTX,
    'max_question_tokens':max_question,'max_answer_tokens':max_answer,'max_combined_tokens':max_joint,
    'answer_token_total':total_label_tokens,'unique_answer_token_ids':len(seen_answer_tokens),
    'answer_boundary_prefix_mismatches':prefix_mismatches,'science':'NOT_EXECUTED'}

def main():
  ap=argparse.ArgumentParser()
  ap.add_argument('--tokenizer-manifest',type=Path)
  ap.add_argument('--t1-bpe-source',type=Path,required=True)
  ap.add_argument('--train-fixture',type=Path,required=True)
  ap.add_argument('--dev-fixture',type=Path,required=True)
  ap.add_argument('--out',type=Path,required=True)
  a=ap.parse_args()
  r=run(a);a.out.parent.mkdir(parents=True,exist_ok=True)
  a.out.write_text(json.dumps(r,ensure_ascii=False,indent=2,sort_keys=True)+'\n')
  print(json.dumps({'status':r['status'],'cases':r.get('input_cases',0),'test_used':False},sort_keys=True))
  if r['status'].startswith('FAIL'):raise SystemExit(3)
  if r['status'].startswith('HOLD'):raise SystemExit(2)
if __name__=='__main__':main()
