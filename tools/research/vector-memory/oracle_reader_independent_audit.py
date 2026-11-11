#!/usr/bin/env python3
"""Independent second-path source-only QA for TTM Oracle Reader v1.

No trained model, private TEST, BPE manifest, optimizer or GPU. Not science.
"""
from __future__ import annotations
import argparse,hashlib,importlib.util,inspect,json,platform,sys
from pathlib import Path
import torch
from torch.nn import functional as F

BLOBS={
 'p02':'9762343e06cf800b50574c2871ae1ed58537fb18',
 'train':'9e86317c055047fffebfb2d802889e69987a8c8b',
 'dev':'ffc9d211508fbedc84db31235ecaad8d07596ece'
}

def git_blob(p):
 b=p.read_bytes();return hashlib.sha1(b'blob '+str(len(b)).encode()+b'\0'+b).hexdigest()
def dynamic_module(name,p):
 spec=importlib.util.spec_from_file_location(name,str(p));m=importlib.util.module_from_spec(spec)
 sys.modules[name]=m;spec.loader.exec_module(m);return m

def main():
 a=argparse.ArgumentParser()
 a.add_argument('--repo-root',type=Path,required=True)
 a.add_argument('--result',type=Path,required=True)
 a.add_argument('--out',type=Path,required=True)
 args=a.parse_args();root=args.repo_root.resolve(strict=True)
 if args.out.exists():raise FileExistsError('AUDIT_RECEIPT_ALREADY_EXISTS')
 p02=root/'tools/pilot_t4/integrated/p02_source_exact.py'
 train=root/'artifacts/research/vector-memory/TTM_EXTERNAL_FACTS_TRAIN_256_V1.json'
 dev=root/'artifacts/research/vector-memory/TTM_EXTERNAL_FACTS_DEV_64_V1.json'
 reader_src=root/'tools/research/vector-memory/oracle_reader_source_only.py'
 checks={}
 def verify(n,b):
  checks[n]=bool(b)
  if not b:raise AssertionError(n)
 verify('01_exact_original_p02_source_blob',git_blob(p02)==BLOBS['p02'])
 verify('02_exact_train_source_blob',git_blob(train)==BLOBS['train'])
 verify('03_exact_dev_source_blob',git_blob(dev)==BLOBS['dev'])
 original=json.loads(args.result.read_text('utf8'))
 verify('04_primary_36_checks_pass',original['checks_passed']==original['checks_total']==36 and all(original['checks'].values()))
 verify('05_primary_model_and_TEST_not_used',original['integrity']['trained_checkpoint_read'] is False and original['integrity']['TEST_read_or_decrypted'] is False and original['integrity']['optimizer_steps']==0)
 r=dynamic_module('vm_reader_independent',reader_src)
 verify('06_oracle_input_only_question_memory',list(inspect.signature(r.oracle_key_mask).parameters)==['question','memory_cards'])
 corpus=json.loads(train.read_text('utf8'))['cases']+json.loads(dev.read_text('utf8'))['cases']
 verify('07_320_case_count',len(corpus)==320)
 for case in corpus:
  ix=r.oracle_key_mask(case['question'],case['correct_memory']).index(True)
  assert case['correct_memory'][ix]['value']==case['answer']
  assert case['wrong_memory'][ix]['value']!=case['answer']
 verify('08_case_oracle_correct_value_and_foil_all',True)
 selected=corpus[8:11]
 # Changing gold metadata cannot change the Oracle selection API (it receives none).
 shadow=[dict(c,answer='DELIBERATELY_UNRELATED',target_key='WRONG_REFERENCE_FIELD') for c in selected]
 oracle1=[r.oracle_key_mask(c['question'],c['correct_memory']) for c in selected]
 oracle2=[r.oracle_key_mask(c['question'],c['correct_memory']) for c in shadow]
 verify('09_gold_label_and_target_metadata_are_not_inputs',oracle1==oracle2)
 mock_tokenize=lambda txt:list(txt.encode('ascii'))
 torch.manual_seed(405051)
 torch.set_num_threads(2)
 frozen_table=torch.randn(2048,256)*.03
 q=[c['question'] for c in selected]
 memory=r.encode_cards_for_reader(q,[c['correct_memory'] for c in selected],mock_tokenize,frozen_table)
 foil=r.encode_cards_for_reader(q,[c['wrong_memory'] for c in selected],mock_tokenize,frozen_table)
 none=r.encode_cards_for_reader(q,[c['correct_memory'] for c in selected],mock_tokenize,frozen_table,no_memory=True)
 hidden=torch.randn(3,256)
 reader=r.GatedOracleReader().eval()
 with torch.inference_mode():
  base=F.linear(hidden,frozen_table)
  disabled,_=r.logits_from_hidden(hidden,frozen_table,reader,none)
  cold,_=r.logits_from_hidden(hidden,frozen_table,reader,memory)
 verify('10_no_memory_and_cold_reader_bit_exact',torch.equal(base,disabled) and torch.equal(base,cold))
 with torch.no_grad():reader.output_proj.weight.copy_(torch.randn_like(reader.output_proj.weight)*0.02)
 with torch.inference_mode():
  good,_=r.logits_from_hidden(hidden,frozen_table,reader,memory)
  bad,_=r.logits_from_hidden(hidden,frozen_table,reader,foil)
  bypass,_=r.logits_from_hidden(hidden,frozen_table,reader,none)
 verify('11_post_edit_no_memory_bit_exact',torch.equal(base,bypass))
 verify('12_counterfactual_value_changes_reader_output',bool((good-bad).abs().max()>1e-8))
 verify('13_foil_preserves_key_vectors_and_oracle_mask',torch.equal(memory.keys,foil.keys) and torch.equal(memory.mask,foil.mask))
 # New random P02 at small sequence: bit-exact source-level, no trained checkpoint.
 torch.manual_seed(405052)
 core=dynamic_module('vm_p02_independent_random',p02)
 cfg=core.P02Config(vocab_size=2048,max_seq_len=256,n_embd=256,n_layer=4,n_head=4,norm_type='layernorm')
 model=core.GPT(cfg).eval();model.requires_grad_(False)
 inp=torch.randint(0,255,(2,7))
 with torch.inference_mode():
  fwd,_=model(inp)
  xx=model.tok(inp)+model.pos(torch.arange(inp.shape[1]))[None,:,:]
  for b in model.blocks:xx=b(xx)
  hs=model.final_ln(xx)
  synthetic_memory=r.EncodedMemory(torch.ones(2,3,256),torch.ones(2,3,256),torch.zeros(2,3,dtype=torch.bool))
  new_h,_=r.GatedOracleReader().eval()(hs[:,-1,:],synthetic_memory)
  hs2=hs.clone();hs2[:,-1,:]=new_h
  test=model.head(hs2)
 verify('14_independent_fresh_p02_random_full_logits_bit_exact',torch.equal(fwd,test))
 verify('15_no_optimizer_test_or_checkpoint_access',not any(x in reader_src.read_text() for x in ['torch.load(', 'AESGCM','TEST_SECRET','torch.optim.']))
 bad=r.encode_cards_for_reader(['No memory needed'],[[{'bad':'invalid'}]],lambda _: (_ for _ in ()).throw(AssertionError('ENCODER_CALLED')),frozen_table,no_memory=True)
 verify('16_no_memory_skips_lookup_and_fact_encoding',bad.keys.shape==(1,0,256) and bad.values.shape==(1,0,256) and bad.mask.shape==(1,0))
 out={'schema':'ttm.vm.oracle_reader.independent_source_qa.v1',
      'status':'PASS_INDEPENDENT_SOURCE_ONLY' if all(checks.values()) else 'FAIL',
      'checks_passed':sum(checks.values()),'checks_total':len(checks),'checks':checks,
      'primary_report_sha256':hashlib.sha256(args.result.read_bytes()).hexdigest(),
      'source_git_blobs':BLOBS,'environment':{'python':platform.python_version(),'torch':torch.__version__},
      'science_executed':False,'trained_checkpoint_loaded':False,'test_read_or_decrypted':False,
      'training_steps':0,'gpu_used':False,'lineage_append':False}
 args.out.parent.mkdir(parents=True,exist_ok=True)
 args.out.write_text(json.dumps(out,indent=2,ensure_ascii=False,sort_keys=True)+'\n','utf8')
 print(json.dumps({'status':out['status'],'checks':str(len(checks))+'/'+str(len(checks)),'test':'NOT_READ'}))
if __name__=='__main__':main()
