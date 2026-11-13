#!/usr/bin/env python3
"""H-DATA-S1 frozen public/private evaluation match check. No model, data or inference."""
import argparse,collections,hashlib,json,pathlib,re,sys

def dig(b):return hashlib.sha256(b).hexdigest()
def chk(ok,msg):
 if not ok:raise RuntimeError('HDATA_S1_FREEZE_HOLD:'+msg)
def main():
 a=argparse.ArgumentParser();a.add_argument('--owner',required=True);a.add_argument('--commitment',required=True);a.add_argument('--dev',required=True);q=a.parse_args()
 op=pathlib.Path(q.owner);cp=pathlib.Path(q.commitment);dp=pathlib.Path(q.dev)
 owner=json.loads(op.read_bytes());commit=json.loads(cp.read_bytes());dev=json.loads(dp.read_bytes())
 chk(dig(op.read_bytes())==commit['owner_private_sha256'],'OWNER_SHA');chk(len(op.read_bytes())==commit['owner_private_bytes'],'OWNER_SIZE')
 chk(dig(dp.read_bytes())==commit['dev_public_sha256'],'DEV_SHA')
 arr=owner['prompts'];chk(len(arr)==36,'36_PROMPTS');chk([x['id'] for x in arr]==[f'HD{i:02}' for i in range(1,13)]+[f'HF{i:02}' for i in range(1,25)],'EXACT_SEQUENCE')
 chk([{'id':x['id'],'cohort':x['cohort'],'stratum':x['stratum'],'prompt_utf8_sha256':x['prompt_utf8_sha256']} for x in arr[12:]]==commit['committed_prompt_hashes'],'FINAL_HASH_CHAIN')
 chk(all(dig(x['prompt'].encode('utf8'))==x['prompt_utf8_sha256'] for x in arr),'PROMPT_BYTES')
 chk(len(set(x['prompt_utf8_sha256'] for x in arr))==36,'ALL_UNIQUE')
 chk(all(x['prompt']==x['prompt'].strip() and '\n' not in x['prompt'] for x in arr),'NO_EXTRA_WHITESPACE')
 chk(collections.Counter(x['stratum'] for x in arr[12:])=={'object_custody':6,'social_relation':6,'causal_obstacle':6,'temporal_rule':6},'FINAL_STRATA')
 chk(collections.Counter(x['stratum'] for x in arr[:12])=={'object_custody':3,'social_relation':3,'causal_obstacle':3,'temporal_rule':3},'DEV_STRATA')
 chk(dev['prompts']==[{k:v for k,v in x.items() if k not in ('actor_anchor','object_anchor','goal_anchor')} for x in arr[:12]],'DEV_EXACT_PUBLIC')
 chk(commit['model_forward']==0 and commit['optimizer_steps']==0,'NO_SCIENCE')
 print('HDATA_S1_FRESH_EVAL_SHA_FREEZE=PASS');print('HDATA_S1_PROMPTS=12_DEV_24_FINAL');print('HDATA_S1_OWNER_SHA256='+dig(op.read_bytes()))
if __name__=='__main__':main()
