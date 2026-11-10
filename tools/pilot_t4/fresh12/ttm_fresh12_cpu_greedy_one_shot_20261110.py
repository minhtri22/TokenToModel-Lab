#!/usr/bin/env python3
"""TTM FRESH12 one-shot 48 CPU greedy outputs, no corpus/TEST/Q1Q2 access."""
from __future__ import annotations
import hashlib,json,os,random,sys,time
from pathlib import Path
import torch
HERE=Path('/mnt/data/ttm_fresh12_executor_private')
sys.dont_write_bytecode=True;sys.path.insert(0,str(HERE))
from p02_canonical import GPT,P02Config
from ttm_tokenizer_private import BPE2048
EXPECTED={1024:'cb985751795c8328ad65acf7ca4c1033ce35182c1bfbdb8c38550de629cb271b',1280:'ee723407b2c25a18be20e26387a3dd8e4a18e2942d469279b6f0748ff86af0dc'}
CLAIM=HERE/'FRESH12_SINGLE_BATCH_CLAIM.json'; RESULT=HERE/'FRESH12_PRIVATE_RAW_48_UNADJUDICATED.json'
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def once(p,o):
 with p.open('x',encoding='utf-8',newline='\n') as f:
  json.dump(o,f,ensure_ascii=False,sort_keys=True,indent=2);f.write('\n');f.flush();os.fsync(f.fileno())
def greedy(model,prompt):
 seq=list(prompt);new=[];stop='length'
 with torch.inference_mode():
  for j in range(64):
   logits,_=model(torch.tensor([seq],dtype=torch.long))
   nxt=int(logits[0,-1].argmax())
   if nxt==256:stop='eos';break
   new.append(nxt);seq.append(nxt)
 return new,stop
def main():
 t=time.perf_counter();torch.set_num_threads(4);torch.use_deterministic_algorithms(True)
 assert not CLAIM.exists() and not RESULT.exists(),'ONE_SHOT_CONSUMED'
 assert torch.__version__.startswith('2.10.0'),'TORCH_VERSION_DRIFT'
 bpe=BPE2048(HERE/'bpe_pairs.b64');prompts=json.load(open(HERE/'prompts.json'))
 assert len(prompts)==12 and len({p['id'] for p in prompts})==12
 for p in prompts:
  s=p['text'];c=bpe.encode(s);d=bpe.encode(s+' ')
  assert hashlib.sha256(s.encode()).hexdigest()==p['sha256']
  assert len(c)==p['clean_tokens'] and len(d)==len(c)+1 and d[-1]==32 and bpe.decode(c)==s and bpe.decode(d)==s+' '
  assert len(d)+64<=256
 models={}
 for step in (1024,1280):
  path=HERE/f'step_{step}.pt';assert sha(path)==EXPECTED[step]
  cp=torch.load(path,map_location='cpu',weights_only=True)
  assert cp['step']==step and cp['p02_git_blob']=='9762343e06cf800b50574c2871ae1ed58537fb18'
  net=GPT(P02Config(**cp['config']));net.load_state_dict(cp['model'],strict=True);net.eval()
  assert sum(z.numel() for z in net.parameters())==3749376
  models[step]=net;del cp
 print('FRESH12_PREFLIGHT=PASS_EXACT_SOURCE_BPE_CHECKPOINTS_12_PROMPTS',flush=True)
 once(CLAIM,{'schema':'ttm.fresh12.single_batch.claim.v1','frozen_prereg_git_blob':'919c43f2c919fa733b20a9be5d6b965e9649339c','pre_run_amendment_commit':'cf0b11db6862c16bfe4a8690c6137a92f1d67a3b','checkpoint_sha256':EXPECTED,'decoder':'greedy_argmax','n_planned':48,'max_new_tokens':64,'no_training':True,'no_test':True,'no_q1q2':True})
 print('FRESH12_CLAIM_SHA256='+sha(CLAIM),flush=True)
 records=[]
 for p in prompts:
  for step in (1024,1280):
   for cond in ('BASELINE_FINAL_ASCII_SPACE','TRIMMED_NO_TRAILING_ASCII_SPACE'):
    s=p['text']+(' ' if cond=='BASELINE_FINAL_ASCII_SPACE' else '')
    ids=bpe.encode(s);seed=20261109+int(p['id'][1:]);random.seed(seed);torch.manual_seed(seed)
    gen,stop=greedy(models[step],ids)
    txt=bpe.decode(gen)
    records.append({'prompt_id':p['id'],'prompt_clean':p['text'],'checkpoint_step':step,'condition':cond,'decoder':'greedy_argmax','seed':seed,'prompt_token_ids':ids,'generated_token_ids':gen,'generated_text':txt,'generated_text_sha256':hashlib.sha256(txt.encode()).hexdigest(),'stop_reason':stop,'generated_token_count':len(gen)})
    print(f'FRESH12_PROGRESS={len(records)}/48 generated_tokens={len(gen)} stop={stop}',flush=True)
 assert len(records)==48 and len({(x['prompt_id'],x['checkpoint_step'],x['condition']) for x in records})==48
 once(RESULT,{'schema':'ttm.fresh12.private.one_shot.generated48.v1','status':'EXECUTED_48_UNADJUDICATED','claim_sha256':sha(CLAIM),'pre_run_amendment_commit':'cf0b11db6862c16bfe4a8690c6137a92f1d67a3b','source_checkpoint_sha256':EXPECTED,'token_merges_sha256':bpe.public_hash,'torch_version':torch.__version__,'new_training_steps':0,'test_reads':0,'q1q2_reads':0,'decoder':'greedy_argmax','n_generations':48,'results':records,'elapsed_seconds':round(time.perf_counter()-t,3)})
 print('FRESH12_BATCH_EXECUTED=48/48',flush=True);print('FRESH12_RAW_SHA256='+sha(RESULT),flush=True);print('ELAPSED_S='+str(round(time.perf_counter()-t,2)),flush=True)
if __name__=='__main__':main()
