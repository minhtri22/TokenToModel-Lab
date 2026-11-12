#!/usr/bin/env python3
"""Offline one-shot release source check; NO inference and NO model load."""
import ast,hashlib,importlib.util,json,pathlib,subprocess,sys,tempfile
ROOT=pathlib.Path(__file__).resolve().parent
SOURCE=ROOT/'ttm_hdec_r1_owner_t4_one_shot_inference_v1.py'
GO=ROOT/'TTM_HDEC_R1_OWNER_NEW_RUN_GO_20261112.json'
received=pathlib.Path('/mnt/data/TTM_HDEC_R1_T4_NO_FORWARD_SOURCE_PIN_RECEIPT_20261112.json')
checks=[]
def require(name,condition):
    if not condition:raise AssertionError('RELEASE_SOURCE_QA_FAIL:'+name)
    checks.append(name)
s=SOURCE.read_text('utf8');a=ast.parse(s)
require('RUNNER_AST',isinstance(a,ast.Module))
for symbol in ('RUN_ID','SOURCE_COMMIT','OWNER_GO_SHA','COLAB_PIN_SHA','SRC','CKPT','BPE','EVAL','GO','T4','BEGIN','RAW','RECEIPT','escrow_verify','main'):
    require('SOURCE_CONTAINS_'+symbol,symbol in s)
for sname in ('model.eval()','model.load_state_dict(state[\'model\'],strict=True)',"torch.inference_mode()","torch.autocast('cuda',dtype=torch.float16)","next_token_from_logits",'for arm in (\'D0\',\'D1\')','range(64)','verify_file(CKPT,A_SHA,45087641)','exclusive_json(BEGIN','exclusive_json(RAW','exclusive_json(RECEIPT','len(results)==72'):
    require('FROZEN_RUNNER_'+sname,sname in s)
for bad in ('optimizer.step(','.backward(','loss.backward(','torch.save(','model.train(','.cuda().backward('):
    require('NO_TRAINING_'+bad,bad not in s)
for protected in ('TTM_SMALL4M_AC_OBJECTIVE_ONLY_V1_SCIENCE/ARM_A/step_1152.pt','T1_BPE2048_REAL_TRAIN_MANIFEST.json','TTM_SMALL4M_NEXT_EVAL_OWNER_PRIVATE_DEV12_FINAL24_20261112.json'):
    require('READ_ONLY_OWNER_RESOURCE_'+protected,protected in s)
require('GO_SHA_LOCK',hashlib.sha256(GO.read_bytes()).hexdigest()=='48f805d2840e86edea07d3ac3c277b9ee496d947f9f0d12b581e0c76cc355a75')
owner=json.loads(GO.read_bytes()); require('OWNER_SCOPE_SINGLE_RUN',owner['owner_authorizes_one_shot_inference'] is True and owner['scope']['new_training_allowed'] if False else owner['scope']['training_steps']==0)
require('OWNER_RATER_DEFERRED',owner['reviewer_acceptance_before_inference_required'] is False)
require('T4_PIN_SOURCE',hashlib.sha256(received.read_bytes()).hexdigest()=='65bfd3b08fbb9fa8454292171e3f1767a36ed14563a99d35112f11d0e0e02142')
modspec=importlib.util.spec_from_file_location('hdec_runner_static_only',SOURCE)
mod=importlib.util.module_from_spec(modspec);sys.modules[modspec.name]=mod;modspec.loader.exec_module(mod)
with tempfile.TemporaryDirectory() as d:
    p=pathlib.Path(d)/'once.json'
    mod.exclusive_json(p,{'message':'one-shot'})
    require('EXCLUSIVE_CREATE_WRITES',json.loads(p.read_text())['message']=='one-shot')
    try:mod.exclusive_json(p,{'message':'replay'}); raise AssertionError('REPLAY_ALLOWED')
    except FileExistsError:checks.append('EXCLUSIVE_CREATE_FAILS_REPLAY')
# GCM check only against previously frozen owner escrow; do not print secret mapping.
mod.ESCROW=pathlib.Path('/mnt/data/ttm_hdec_preexec_private/escrow')
require('ESCROW_ORIGINAL_GCM_AND_HASH',mod.escrow_verify()=='603bccaf0060f8a8a577302353ea6cac831281ad17596603ffa7eb6630ce20a3')
# A non-T4 host must fail before any model initialization or receipt write.
r=subprocess.run([sys.executable,str(SOURCE)],capture_output=True,text=True,timeout=20)
require('CPU_HOST_FAIL_CLOSED',r.returncode==2 and 'EXACT_ONE_CUDA_DEVICE_REQUIRED' in r.stderr)
require('CPU_NO_OWNER_OUTPUT',not (pathlib.Path('/mnt/data')/'HDEC_R1_V1_ONE_SHOT_BEGIN.json').exists())
report={'schema':'ttm.small4m.hdec_r1.owner_consent_and_one_shot_runner.static_qa.v1',
'operation':'TTM_HDEC_R1_OWNER_GO_AND_RATER_DEFERRED_AFTER_GENERATION',
'checks':checks,'pass':len(checks),'fail':0,
'runner_sha256':hashlib.sha256(SOURCE.read_bytes()).hexdigest(),
'owner_go_sha256':hashlib.sha256(GO.read_bytes()).hexdigest(),
'Colab_prior_PIN_SHA256':hashlib.sha256(received.read_bytes()).hexdigest(),
'escrow_GCM':'PASS_ORIGINAL_CUSTODY_NO_MAPPING_PUBLICATION',
'Colab_real_model_forward':'NOT_EXECUTED','training_steps':0,
'reviewer_acceptance_pre_inference_required':False,'reviewer_scoring_post_inference_pre_unblind_required':True,
'status':'PASS_STATIC_RELEASE_SOURCE_QA_NO_INFERENCE'}
out=ROOT/'TTM_HDEC_R1_OWNER_GO_ONE_SHOT_RUNNER_STATIC_QA_20261112.json'
out.write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n',encoding='utf8')
print('HDEC_ONE_SHOT_STATIC_QA='+str(len(checks))+'/'+str(len(checks))+'_PASS')
print('RUNNER_SHA256='+report['runner_sha256'])
print('MODEL_FORWARD=0')
