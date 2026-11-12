#!/usr/bin/env python3
"""Pure CPU synthetic logits + BPE input preflight; never calls model.

Reads only owner-private NEW eval prompts, pinned BPE manifest, checkpoint bytes,
public commitment, and fixed decoder source. Does not reveal FINAL texts.
"""
from __future__ import annotations
import argparse, collections, hashlib, importlib.util, json, re
from pathlib import Path
import regex

EXPECTED = {
 'owner_sha':'9480ba73cbbe425fc9b61cc3253df81b32d52b0c35127d6e4392e5b5d6b0d54f',
 'public_sha':'3c6d484d40eba4cbdf0d122d032e228b02fa67af48647830a273f93a54f32060',
 'bpe_sha':'cba18e60cee3d08a353ee6d4a451017289e45af7b4b1179c87171b9b78d7dfdc',
 'ckpt_A1152_sha':'ae9f05c5234ac98e3f9150e3f27501d217c1942a381650bec5aef91a1f56196b',
 'decoder_sha':'64a812a49f8d82d2c797d9150b2d3278763d411fff3e3b53424e650711092e85'
}
GPT2_PATTERN = r"'s|'t|'re|'ve|'m|'ll|'d| ?\p{L}+| ?\p{N}+| ?[^\s\p{L}\p{N}]+|\s+(?!\S)"

def digest(b): return hashlib.sha256(b).hexdigest()
def require(check, name):
 if not check: raise AssertionError('H_DEC_PREEXEC_HOLD:'+name)

class BPE:
 def __init__(self, j):
  j0=dict(j); man=j0.pop('manifest_sha256',None)
  canonical=json.dumps(j0,ensure_ascii=False,sort_keys=True,separators=(',',':')).encode('utf8')
  require(man == digest(canonical),'BPE_INTERNAL_MANIFEST_DIGEST')
  require(j['schema']=='ttm.gpt2.pretokenized.byte-bpe.2048.v1','BPE_SCHEMA')
  require(j['regex']==GPT2_PATTERN,'BPE_REGEX')
  require(j['eos_id']==256 and j['vocab_size']==2048,'BPE_VOCAB_EOS')
  require(len(j['tokens'])==2048 and len(j['pair_ids'])==1791,'BPE_SIZES')
  self.tokens=j['tokens'];self.ranks={tuple(pair):i for i,pair in enumerate(j['pair_ids'])}
  require(len(self.ranks)==1791,'BPE_PAIR_UNIQUE')
  self.rx=regex.compile(GPT2_PATTERN)
  bs=list(range(33,127))+list(range(161,173))+list(range(174,256));cs=bs.copy();n=0
  for i in range(256):
   if i not in bs:bs.append(i);cs.append(256+n);n+=1
  tochar=dict(zip(bs,map(chr,cs)));self.tochar=tochar;self.toByte={v:k for k,v in tochar.items()}
  require(self.tokens[:256]==[tochar[i] for i in range(256)],'BPE_BYTES_MATCH')
  require(self.tokens[256]=='<|endoftext|>','BPE_EOS_MATCH')
  for i,(a,b) in enumerate(j['pair_ids']):
   require(0<=a<257+i and 0<=b<257+i,'BPE_MERGE_CAUSAL')
   require(self.tokens[257+i]==self.tokens[a]+self.tokens[b],'BPE_MERGE_JOIN')
 def encode(self,text):
  parts=[];pos=0
  for m in self.rx.finditer(text):
   if m.start()>pos:parts.append(text[pos:m.start()])
   parts.append(m.group());pos=m.end()
  if pos<len(text):parts.append(text[pos:])
  require(''.join(parts)==text,'BPE_REGEX_LOSS')
  out=[]
  for part in parts:
   ids=list(part.encode('utf8'))
   while len(ids)>1:
    options=[(self.ranks[(ids[i],ids[i+1])],i) for i in range(len(ids)-1) if (ids[i],ids[i+1]) in self.ranks]
    if not options:break
    rank,k=min(options)
    ids[k:k+2]=[257+rank]
   out+=ids
  return out
 def decode(self,ids):
  s=''.join(self.tokens[i] for i in ids)
  return bytes(self.toByte[c] for c in s).decode('utf8')


def main():
 ap=argparse.ArgumentParser()
 for a in ('owner-private','public-commit','bpe-manifest','ckpt-a1152','decoder-source','output'):ap.add_argument('--'+a,required=True)
 a=ap.parse_args();checks=[]
 def test(name,ok):require(ok,name);checks.append(name)
 owner_bytes=Path(a.owner_private).read_bytes()
 public_bytes=Path(a.public_commit).read_bytes()
 bpe_bytes=Path(a.bpe_manifest).read_bytes()
 with Path(a.ckpt_a1152).open('rb') as f:
  h=hashlib.sha256(); ckpt_n=0
  for chunk in iter(lambda:f.read(1<<20),b''):h.update(chunk);ckpt_n+=len(chunk)
 test('OWNER_EXACT_SHA',digest(owner_bytes)==EXPECTED['owner_sha'])
 test('PUBLIC_COMMITMENT_EXACT_SHA',digest(public_bytes)==EXPECTED['public_sha'])
 test('BPE_EXACT_SHA',digest(bpe_bytes)==EXPECTED['bpe_sha'])
 test('A1152_CKPT_EXACT_SHA',h.hexdigest()==EXPECTED['ckpt_A1152_sha'] and ckpt_n==45087641)
 test('DECODER_EXACT_SHA',digest(Path(a.decoder_source).read_bytes())==EXPECTED['decoder_sha'])
 owner=json.loads(owner_bytes);public=json.loads(public_bytes);bpe=BPE(json.loads(bpe_bytes))
 ids=owner['prompts'];final=[x for x in ids if x['cohort']=='BLIND_FINAL'];dev=[x for x in ids if x['cohort']=='DEV']
 test('PROMPT_COUNTS_AND_ID_ORDER',len(ids)==36 and len(dev)==12 and len(final)==24 and [x['id'] for x in dev]==[f'ND{i:02d}' for i in range(1,13)] and [x['id'] for x in final]==[f'NF{i:02d}' for i in range(1,25)])
 test('FINAL_PUBLIC_HASH_BINDING',all(x['prompt_utf8_sha256']==y['prompt_utf8_sha256'] for x,y in zip(final,public['sha256_per_final_prompt'])))
 test('FINAL_STRATA_SIX_EACH',collections.Counter(x['stratum'] for x in final)=={'object_custody':6,'social_relation':6,'causal_obstacle':6,'temporal_rule':6})
 counts={}; roundtrip=[]
 for x in ids:
  s=x['prompt'];tok=bpe.encode(s)
  test('PROMPT_SHA_'+x['id'],digest(s.encode('utf8'))==x['prompt_utf8_sha256'])
  test('BPE_ROUNDTRIP_'+x['id'],bpe.decode(tok)==s)
  test('NO_EOS_IN_PREFIX_'+x['id'],256 not in tok)
  test('CONTEXT_256_WITH_64_NEW_'+x['id'],0<len(tok) and len(tok)+64<=256)
  test('NO_TRAILING_ASCII_SPACE_'+x['id'],s==s.strip())
  counts[x['id']]=len(tok)
 # exact import of pinned pure source code only; does not call model.
 spec=importlib.util.spec_from_file_location('ttm_hdec_r1_pinned_module',a.decoder_source)
 module=importlib.util.module_from_spec(spec);spec.loader.exec_module(module)
 def logits(pairs,default=-10.0):
  l=[default]*2048
  for k,v in pairs.items():l[k]=v
  return l
 def raises(func):
  try:func()
  except (ValueError,AssertionError):return True
  return False
 test('D0_ARGMAX',module.next_token_from_logits(logits({7:3,8:2}),[],'D0')==7)
 test('D1_PROMPT_IS_EXCLUDED',module.next_token_from_logits(logits({7:3,8:2}),[],'D1')==7)
 test('D1_PENALIZES_CONTINUATION_POSITIVE',module.next_token_from_logits(logits({7:2.0,8:1.9}),[7],'D1')==8)
 test('D1_DUPLICATE_TOKEN_ONLY_ONCE',module.next_token_from_logits(logits({7:2,8:1.9}),[7,7,7],'D1')==8)
 test('D1_SIGN_NEGATIVE_MULTIPLIES',module.next_token_from_logits(logits({7:-1,8:-1.1},default=-10),[7],'D1')==8)
 test('D1_ZERO_REMAINS_ZERO',module.next_token_from_logits(logits({7:0,8:-.01}),[7],'D1')==7)
 test('ARGMAX_TIES_LOWEST_ID',module.next_token_from_logits(logits({7:1,8:1}),[],'D0')==7)
 test('D1_NO_NEW_PREFIX_IMPACT',module.next_token_from_logits(logits({5:3,6:2.9}),[],'D1')==5)
 test('EOS_STOP',module.stop_reason([14,256])=='EOS')
 test('LIMIT_STOP',module.stop_reason([5]*64)=='MAX_NEW_TOKENS')
 test('STOP_NONE',module.stop_reason([])=='CONTINUE')
 test('NEG_WRONG_ARM',raises(lambda:module.next_token_from_logits(logits({0:1}),[],'D2')))
 test('NEG_WRONG_VOCAB',raises(lambda:module.next_token_from_logits([2,3],[],'D1')))
 test('NEG_NAN',raises(lambda:module.next_token_from_logits(logits({9:float('nan')}),[],'D1')))
 test('NEG_INF',raises(lambda:module.next_token_from_logits(logits({9:float('inf')}),[],'D1')))
 test('NEG_POST_EOS',raises(lambda:module.next_token_from_logits(logits({9:1}),[256],'D1')))
 test('NEG_BAD_CONTINUATION_ID',raises(lambda:module.next_token_from_logits(logits({9:1}),[2048],'D1')))
 test('NEG_MAX64_EXCEEDED',raises(lambda:module.next_token_from_logits(logits({9:1}),[5]*64,'D1')))
 test('NEG_BOOLEAN_TOKEN_ID',raises(lambda:module.next_token_from_logits(logits({9:1}),[True],'D1')))
 report={
  'schema':'ttm.small4m.hdec_r1.preexec.source_bpe_context_qa.v1',
  'operation':'TTM_SMALL4M_H_DEC_R1_INTEGRATED_SOURCE_QA_BPE_CONTEXT_CHECK_RIGHTS_REVIEWER_AND_SINGLE_OWNER_GO_HOLD_PREEXEC_NO_INFERENCE',
  'checks_count':len(checks),'checks_passed':len(checks),'checks_failed':0,
  'decoder_sha256':digest(Path(a.decoder_source).read_bytes()),
  'pinned_sha256':{**EXPECTED,'decoder':digest(Path(a.decoder_source).read_bytes())},
  'BPE_manifest_internal_sha':'PASS',
  'BPE_roundtrip':{'dev_count':12,'final_count':24,'all_pass':True},
  'context':{'limit':256,'reserved_new_tokens':64,'min_prompt_bpe_tokens':min(counts.values()),'max_prompt_bpe_tokens':max(counts.values()),'all_prompt_plus64_le256':True},
  'model_forward':0,'optimizer_updates':0,'TEST_Q1_Q2_OOD_access':False,
  'private_final_plaintext_in_report':False,'checkpoint_tensor_deserialized':False,
  'synthetic_logits_QA_PASS':True,'right_owner_release_required':True,
  'verdict':'PASS_SOURCE_BPE_CONTEXT_AND_SYNTHETIC_DECODER_QA_SCOPED',
  'checks':checks,
 }
 Path(a.output).write_text(json.dumps(report,sort_keys=True,ensure_ascii=False,indent=2)+'\n',encoding='utf8')
 print(json.dumps({k:report[k] for k in ('checks_count','verdict','decoder_sha256','BPE_roundtrip','context','model_forward')},sort_keys=True))

if __name__=='__main__':main()
