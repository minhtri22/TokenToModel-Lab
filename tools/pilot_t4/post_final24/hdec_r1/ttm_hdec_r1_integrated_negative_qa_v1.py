#!/usr/bin/env python3
"""Mutation QA with deliberately corrupted copies of pinned inputs, no model loads."""
from __future__ import annotations
import hashlib,json,subprocess,sys,tempfile
from pathlib import Path

ROOT=Path(__file__).parent
SRC=['--owner-private','/mnt/data/ttm_post_final24_artifacts/TTM_SMALL4M_NEXT_EVAL_OWNER_PRIVATE_DEV12_FINAL24_20261112.json','--public-commit','/mnt/data/ttm_post_final24_artifacts/TTM_SMALL4M_NEXT_EVAL_FINAL24_PUBLIC_SHA_COMMITMENT_20261112.json','--bpe-manifest','/mnt/data/T1_BPE2048_REAL_TRAIN_MANIFEST.json','--ckpt-a1152','/mnt/data/ttm_hdec_preexec_private/step_1152.pt','--decoder-source',str(ROOT/'ttm_hdec_r1_deterministic_decoder_v1.py')]
NEG=[('owner_sha','--owner-private','OWNER_EXACT_SHA'),('commitment_sha','--public-commit','PUBLIC_COMMITMENT_EXACT_SHA'),('bpe_manifest_sha','--bpe-manifest','BPE_EXACT_SHA'),('decoder_source_sha','--decoder-source','DECODER_EXACT_SHA')]
results=[]
with tempfile.TemporaryDirectory(dir=ROOT,prefix='qa_negative_') as tmp:
 for label,flag,expect in NEG:
  arg_index=SRC.index(flag)+1
  original=Path(SRC[arg_index]).read_bytes()
  modified=bytearray(original);modified[len(modified)//2]^=1
  p=Path(tmp)/(label+'.invalid');p.write_bytes(modified)
  args=SRC.copy();args[arg_index]=str(p)
  cmd=[sys.executable,str(ROOT/'ttm_hdec_r1_integrated_source_qa_v1.py')]+args+['--output',str(Path(tmp)/'forbidden.json')]
  run=subprocess.run(cmd,text=True,capture_output=True,timeout=60)
  ok=run.returncode!=0 and expect in run.stderr and not (Path(tmp)/'forbidden.json').exists()
  if not ok:raise RuntimeError('NEGATIVE_QA_FAIL:'+label)
  results.append({'case':label,'expected_failure':expect,'PASS':True})
report={'schema':'ttm.small4m.hdec_r1.negative_source_lock_qa.v1','tests':results,'count':len(results),'all_PASS':True,'no_model_forward':True,'no_optimizer_steps':True,'no_private_prompt_or_key_published':True,'status':'PASS_NEGATIVE_MUTATION_REJECT_ALL'}
(ROOT/'TTM_HDEC_R1_PREEXEC_MUTATION_NEGATIVE_QA_20261112.json').write_text(json.dumps(report,indent=2,sort_keys=True)+'\n')
print(json.dumps({'count':len(results),'result':report['status']}))
