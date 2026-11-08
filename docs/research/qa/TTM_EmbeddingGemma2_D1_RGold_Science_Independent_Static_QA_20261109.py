"""Independent static & synthetic unit QA for frozen R_gold science runner.
Never imports or executes __main__, downloads, torch models, scientific cohorts.
"""
import ast
import copy
import hashlib
import json
import pathlib
import sys
import types
import math
import unicodedata
import datetime
import os
import time
import numpy as np
import torch

P=pathlib.Path('/mnt/data/TTM_EmbeddingGemma2_D1_RGold_OneShot_Science_20261109.py')
src=P.read_text('utf-8'); tree=ast.parse(src)
checks=[]
def check(name,condition):
    checks.append({'name':name,'pass':bool(condition)})
    if not condition:
        print('FAIL',name)

check('python source compiles',bool(compile(tree,str(P),'exec')))
check('source pinned fixture SHA',"0215719de94f86a4f2b7a48959ca81343014c127e74799f737901a57b33f341a" in src)
check('source pinned Qwen revision',"7ae557604adf67be50417f59c2c2f167def9a775" in src)
check('source pinned GPT backend Transformers',"5.22.1" in src)
check('source pinned one-shot ID',"ttm_embedgemma2_d1_rgold_one_shot_20261109_v1" in src)
check('source special-token EOS',"'<|im_end|>'" in src)
check('source no EmbeddingGemma loading',"google/embeddinggemma-2" not in src)
check('source no SQuAD dataset loading',"rajpurkar/squad" not in src)
check('source no adapter training',"optimizer.step(" not in src)
check('source source-code SHA gate',"SOURCE_SHA256 == 'UNPINNED'" in src)
check('source one scientific claim',src.count('write_exclusive_json(CLAIM')==1)
check('source one terminal result',src.count('write_exclusive_json(RESULT')==1)
check('source prevent rerun after terminal',"if RESULT.exists():" in src)
check('source stored group readback',"old.get('config_sha256') != config_sha" in src)
check('source no CLAIM overwrite',"os.O_CREAT | os.O_EXCL | os.O_WRONLY" in src)
check('source 30 minute',"LIMIT_SECONDS = 1800" in src)
check('source 5GiB and 8GiB',"MAX_PLANNED_DOWNLOAD = 5 * 1024**3" in src and "MAX_NEW_STORAGE = 8 * 1024**3" in src)
check('source free GPU T4',"torch.cuda.get_device_name(0) != 'Tesla T4'" in src)
check('science record not auto append lineage',"lineage.md" not in src)
check('bootstrap 10000 seed 20261108',"BOOTSTRAP_REPLICATES = 10000" in src and "BOOTSTRAP_SEED = 20261108" in src)
check('greedy max 24',"MAX_NEW_TOKENS = 24" in src)
check('no science infer before claim', src.index("write_exclusive_json(CLAIM") < src.index("item['nll'] =") and src.index("write_exclusive_json(CLAIM") < src.index("pred = greedy_text(model"))
check('Qwen file sha pins count', src.count("model.safetensors': (988097824") == 1)
assignments={n.targets[0].id:n.value for n in tree.body if isinstance(n,ast.Assign) and len(n.targets)==1 and isinstance(n.targets[0],ast.Name)}
files=ast.literal_eval(assignments['MODEL_FILES'])
v3=json.load(open('/mnt/data/ttm_embedgemma2_d1_t4_preflight_st610_once_v1_RESULT.json'))
qwen=next(x for x in v3['downloaded_file_manifests'] if x['repo']=='Qwen/Qwen2.5-0.5B-Instruct')
original={x['name']:(x['bytes'],x['sha256']) for x in qwen['files']}
check('all Qwen expected size/hash match exact V3 receipt', all(files[k]==original[k] for k in files))
receipts_ns={'V3':'ttm_embedgemma2_d1_t4_preflight_st610_once_v1', 'QWEN_FOLLOW':'ttm_embedgemma2_d1_t4_qwen_tokenizer_followup_once_v1'}
exec(compile(ast.fix_missing_locations(ast.Module(body=[ast.Assign(targets=[ast.Name(id='RECEIPTS',ctx=ast.Store())],value=assignments['ORIGINAL_RECEIPTS'])],type_ignores=[])),'<dict>','exec'),receipts_ns)
receipts=receipts_ns['RECEIPTS']
check('all 4 original receipt hashes match loaded actual bytes',all(
   (pathlib.Path('/mnt/data')/name).is_file() and
   hashlib.sha256((pathlib.Path('/mnt/data')/name).read_bytes()).hexdigest()==sha
   for name,sha in receipts.items()))
check('model hosted in private Drive for Colab resume',"MODEL_DIR = SCIENCE_BASE" in src and "shutil.copy2(MODEL_DIR / name, dest)" in src)
check('strict local model readback before CLAIM',"Local pinned Qwen copy mismatch before claim" in src)

# Only compile and run selected pure functions, not the module or main.
selected={"sha256_bytes","canonical_json_sha","normalize_answer","bootstrap_group_ci","validate_fixture","model_prompt","flat_token_ids","masked_answer_nll_from_logits","aggregate_results"}
functions=[n for n in tree.body if isinstance(n,ast.FunctionDef) and n.name in selected]
namespaces={'hashlib':hashlib,'json':json,'np':np,'torch':torch,'unicodedata':unicodedata,'math':math,'SYSTEM':'answer evidence only',
           'PROMPT_PREFIX':'Evidence:\n','PROMPT_MIDDLE':'\n\nQuestion:\n','PROMPT_SUFFIX':'\nAnswer:',
           'BOOTSTRAP_REPLICATES':10000,'BOOTSTRAP_SEED':20261108}
exec(compile(ast.Module(body=functions,type_ignores=[]),'<pure functions>','exec'),namespaces)
n=namespaces
check('NFKC EM terminal punctuation',n['normalize_answer']('  Ｓｉｌｖｅｒ!?  ')=='silver')
check('empty evidence no leak', 'silver' not in n['model_prompt']('Dummy color?',None)[1]['content'])
check('dict vs list token normalized',n['flat_token_ids']({'input_ids':[151644,5]})==[151644,5])
check('nested token normalized',n['flat_token_ids']([[151644,5]])==[151644,5])
check('numpy token normalized',n['flat_token_ids'](np.array([151644,5]))==[151644,5])
try:n['flat_token_ids']([3,'four']); check('reject bad token IDs',False)
except ValueError:check('reject bad token IDs',True)
check('fixed bootstrap values',all(abs(v-0.2)<1e-12 for v in n['bootstrap_group_ci']([0.2]*48)))
ci=n['bootstrap_group_ci']([(-1)**i*.5 + .3 for i in range(48)])
check('bootstrap deterministic',ci==n['bootstrap_group_ci']([(-1)**i*.5 + .3 for i in range(48)]))
check('bootstrap percentile ordered',ci[0]<ci[1])

# Actual causal shift/masking evaluated with torch CPU mock logits, no model.
labels=torch.tensor([[-100,-100,-100,4,5]],dtype=torch.long)
logits=torch.zeros(1,5,8,dtype=torch.float32)
logits[0,2,4]=12.0;logits[0,3,5]=12.0
out=n['masked_answer_nll_from_logits'](logits,labels,2)
check('answer plus EOS exactly two targets',out['answer_token_count_including_eos']==2)
check('causal shift low NLL with correct last-prompt logit',out['nll']<0.0001)
try:n['masked_answer_nll_from_logits'](logits,labels,3);check('NLL wrong scored count rejected',False)
except AssertionError:check('NLL wrong scored count rejected',True)
corrupt=logits.clone();corrupt[0,2,4]=-12;bad=n['masked_answer_nll_from_logits'](corrupt,labels,2)
check('changing last prompt logit affects first answer NLL',bad['nll']>out['nll']+0.5)

# Synthetic structural dataset with 48 independent IDs and 12 negative IDs.
rows=[]
for i in range(48):
 gid=f'RG-P-{i+1:03d}'; label=f'Z{i:03d}'
 rows.append({'schema':'ttm.rgold.group.v1','group_id':gid,'cohort':'answerable',
              'science_consumed':False,'gold_evidence':f'Case has answer {label}.',
              'wrong_evidence':f'Unrelated case {i+1} is absent.',
              'gold_answer':label,'questions':[{'question_id':gid+f'-Q{j}', 'text':'question?',
                      'target_answer':label} for j in (1,2)]})
for i in range(12):
 gid=f'RG-N-{i+1:03d}'
 rows.append({'schema':'ttm.rgold.group.v1','group_id':gid,'cohort':'unanswerable',
              'science_consumed':False,'gold_evidence':'No key.',
              'wrong_evidence':'Unrelated key.', 'gold_answer':'UNKNOWN',
              'questions':[{'question_id':gid+f'-Q{j}', 'text':'question?',
              'target_answer':'UNKNOWN'} for j in (1,2)]})
check('fixture 60/120 schema pass',n['validate_fixture'](rows)=={'positive_groups':48,'negative_groups':12,'questions':120})
broken=copy.deepcopy(rows);broken[1]['group_id']=broken[0]['group_id']
try:n['validate_fixture'](broken);check('duplicate group rejected',False)
except ValueError:check('duplicate group rejected',True)
broken=copy.deepcopy(rows);broken[4]['wrong_evidence']=broken[4]['gold_evidence']
try:n['validate_fixture'](broken);check('gold leakage into wrong evidence rejected',False)
except ValueError:check('gold leakage into wrong evidence rejected',True)
broken=copy.deepcopy(rows);broken[-1]['questions'][0]['target_answer']='SOMETHING'
try:n['validate_fixture'](broken);check('negative answer mismatch rejected',False)
except ValueError:check('negative answer mismatch rejected',True)

# Synthetic aggregate tests; no Qwen forward pass.
recs=[]
for i in range(48):
 recs.append({'group_id':f'RG-P-{i+1:03d}','cohort':'answerable','questions':[
 {'nll':{'R0':{'nll':1.2},'R_gold':{'nll':0.1},'R_wrong':{'nll':1.4}},
  'em':{'R_gold':True,'R0':False}} for j in range(2)]})
for i in range(12):
 recs.append({'group_id':f'RG-N-{i+1:03d}','cohort':'unanswerable','questions':[
 {'prediction_normalized':'unknown'} for j in range(2)]})
valid=n['aggregate_results'](recs)
check('screen positive on synthetic favorable metrics',valid['verdict_unadjudicated']=='RGOLD_SCREEN_PASS_CONSERVATIVE_NONEXACT_GUARD')
check('positive group weighting correct',abs(valid['mean_group_nll_improvement']-1.1)<1e-10)
check('EM over 96 questions',valid['exact_match_gold']==1.0 and valid['exact_match_r0']==0.0)
check('negative conservative gate strict zero',valid['negative_nonexact_UNKNOWN_count_conservative']==0)
weak=copy.deepcopy(recs)
for r in weak[:48]:
 for q in r['questions']:q['nll']['R0']['nll']=0.1
check('capability gap on no improvement',n['aggregate_results'](weak)['verdict_unadjudicated']=='MODEL_CAPABILITY_GAP_SCOPED_R_GOLD')
negative=copy.deepcopy(recs)
for r in negative[48:53]:
 for q in r['questions']:q['prediction_normalized']='not stated'
check('negative > 6 nonexact => inconclusive, not false fail',n['aggregate_results'](negative)['verdict_unadjudicated']=='INCONCLUSIVE_NEGATIVE_GUARD_REQUIRES_BLIND_FACTUAL_RESPONSE_REVIEW')
check('negative grouping 5/12',n['aggregate_results'](negative)['negative_groups_with_nonexact']==5)

report={'schema':'ttm.embeddinggemma2.d1.rgold.static_qa.v1',
 'source':P.name,'source_sha256':hashlib.sha256(P.read_bytes()).hexdigest(),
 'total':len(checks),'passed':sum(x['pass'] for x in checks),
 'failed':[x['name'] for x in checks if not x['pass']],
 'status':'PASS_SOURCE_ONLY_NO_SCIENCE' if all(x['pass'] for x in checks) else 'FAIL_SOURCE_ONLY',
 'checks':checks,'models_executed':False,'science_executed':False}
out=P.with_name('TTM_EmbeddingGemma2_D1_RGold_Science_Independent_Static_QA_20261109.json')
out.write_text(json.dumps(report,indent=2,ensure_ascii=False)+'\n')
print('TTM_RGOLD_SOURCE_QA=',report['status'],report['passed'],'/',report['total'])
if report['failed']:print('FAILS',report['failed'])
sys.exit(0 if not report['failed'] else 1)
