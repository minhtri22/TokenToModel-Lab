#!/usr/bin/env python3
"""TTM H-DEC-R1 one-shot owner inference on T4, after explicit owner GO.

Only existing A-step1152 model; 12 new DEV + 24 new BLIND_FINAL, D0/D1.
Never train, score, unblind, print raw text, rewrite checkpoint, or publish mapping.
If a BEGIN marker exists, refuse replay; interrupted execution is HOLD for review.
"""
from __future__ import annotations
import base64
import datetime as dt
import hashlib
import importlib.util
import json
import os
from pathlib import Path
import subprocess
import sys
import urllib.request

RUN_ID = 'TTM_SMALL4M_POST_FINAL24_DECODING_REPETITION_DIAGNOSTIC_V1'
SOURCE_COMMIT = 'c784b4a0687f6b0fd840f41d3bbf93e5c31038a7'
REPO = 'minhtri22/TokenToModel-Lab'
OWNER_GO_SHA = '48f805d2840e86edea07d3ac3c277b9ee496d947f9f0d12b581e0c76cc355a75'
COLAB_PIN_SHA = '65bfd3b08fbb9fa8454292171e3f1767a36ed14563a99d35112f11d0e0e02142'
A_SHA = 'ae9f05c5234ac98e3f9150e3f27501d217c1942a381650bec5aef91a1f56196b'
BPE_SHA = 'cba18e60cee3d08a353ee6d4a451017289e45af7b4b1179c87171b9b78d7dfdc'
OWNER_EVAL_SHA = '9480ba73cbbe425fc9b61cc3253df81b32d52b0c35127d6e4392e5b5d6b0d54f'
COMMIT_SHA = '3c6d484d40eba4cbdf0d122d032e228b02fa67af48647830a273f93a54f32060'
ESCROW_SHA = '812e7e23cdc3eba4735bfb0b8ff43b2a7420fbaac4fa0edfc2fe4a944cb8c3b7'
KEY_SHA = '3e2b381fce29753621baec956b993b8c01e951925717c1730feb7aca0a548911'
TOKEN_SOURCE = 'tools/pilot_t4/integrated/source_t2/ttm_gpt2_bpe2048.py'
DECODER_SOURCE = 'tools/pilot_t4/post_final24/hdec_r1/ttm_hdec_r1_deterministic_decoder_v1.py'
MODEL_SOURCE = 'src/p02/transformer_core.py'
SRC = {
  'bpe': (TOKEN_SOURCE, 'fa5bd892941ba5aa6e6b2f0b2b0ae974efe297b6'),
  'decoder': (DECODER_SOURCE, 'b6fd0cf0efd4be759da70814de5c5706f5532416'),
  'p02': (MODEL_SOURCE, '9762343e06cf800b50574c2871ae1ed58537fb18'),
}
BASE = Path('/content/drive/MyDrive/TTM/ttm-small-pilot')
AC = BASE/'ttm_small4m_ac_objective_only_v1'
NEXT = BASE/'ttm_small4m_post_final24_next_eval_v1'
PUB = NEXT/'public_safe'
PRIVATE = NEXT/'owner_private'
ESCROW = PRIVATE/'HDEC_R1_ESCROW_OWNER_ONLY'
CKPT = AC/'TTM_SMALL4M_AC_OBJECTIVE_ONLY_V1_SCIENCE/ARM_A/step_1152.pt'
BPE = AC/'T1_BPE2048_REAL_TRAIN_MANIFEST.json'
EVAL = PRIVATE/'TTM_SMALL4M_NEXT_EVAL_OWNER_PRIVATE_DEV12_FINAL24_20261112.json'
PUBLIC_COMMITMENT = PUB/'TTM_SMALL4M_NEXT_EVAL_FINAL24_PUBLIC_SHA_COMMITMENT_20261112.json'
GO = PUB/'TTM_HDEC_R1_OWNER_NEW_RUN_GO_20261112.json'
T4 = PUB/'TTM_HDEC_R1_T4_NO_FORWARD_SOURCE_PIN_RECEIPT_20261112.json'
BEGIN = PRIVATE/'HDEC_R1_V1_ONE_SHOT_BEGIN.json'
RAW = PRIVATE/'HDEC_R1_V1_OWNER_ONLY_72_D0_D1_RAW_GENERATIONS.json'
RECEIPT = PUB/'HDEC_R1_V1_OWNER_GENERATION_NONSECRET_RECEIPT.json'


def sha(data:bytes)->str: return hashlib.sha256(data).hexdigest()
def git_blob(data:bytes)->str:
    return hashlib.sha1(b'blob '+str(len(data)).encode('ascii')+b'\0'+data).hexdigest()
def check(cond:bool, reason:str):
    if not cond: raise RuntimeError('HDEC_R1_HOLD:'+reason)
def verify_file(p:Path,expected_sha:str,expected_size:int|None=None)->bytes:
    check(p.is_file(),'MISSING_'+p.name)
    b=p.read_bytes()
    check(sha(b)==expected_sha,'SHA_DRIFT_'+p.name)
    if expected_size is not None:check(len(b)==expected_size,'SIZE_DRIFT_'+p.name)
    return b

def json_bytes(obj)->bytes:
    return (json.dumps(obj,ensure_ascii=False,sort_keys=True,indent=2)+'\n').encode('utf-8')
def exclusive_json(p:Path,obj):
    with p.open('xb') as f:f.write(json_bytes(obj))

def get_source(path:str,blob:str)->bytes:
    url=f'https://raw.githubusercontent.com/{REPO}/{SOURCE_COMMIT}/{path}'
    with urllib.request.urlopen(urllib.request.Request(url,headers={'User-Agent':'TTM-HDEC-R1-ONE-SHOT/1'}),timeout=30) as fd:
        b=fd.read(2000001)
    check(len(b)<=2000000,'SOURCE_OVERSIZE')
    check(git_blob(b)==blob,'SOURCE_GIT_BLOB_DRIFT_'+path)
    return b

def import_code(name:str,raw:bytes):
    spec=importlib.util.spec_from_loader(name,loader=None)
    mod=importlib.util.module_from_spec(spec)
    sys.modules[name]=mod
    exec(compile(raw, name, 'exec'),mod.__dict__)
    return mod

def escrow_verify():
    from cryptography.hazmat.primitives.ciphers.aead import AESGCM
    e=json.loads(verify_file(ESCROW/'HDEC_R1_PUBLIC_SAFE_ENCRYPTED_MAPPING.json',ESCROW_SHA,3869))
    k=json.loads(verify_file(ESCROW/'HDEC_R1_OWNER_PRIVATE_AES_KEY_DO_NOT_SHARE.json',KEY_SHA,408))
    check(k['public_ciphertext_sha256']==ESCROW_SHA,'KEY_ESCROW_BOND')
    msg=AESGCM(base64.b64decode(k['key_b64'])).decrypt(
        base64.b64decode(e['nonce_b64']),base64.b64decode(e['ciphertext_b64']),e['aad_utf8'].encode('utf-8'))
    check(sha(msg)==e['plaintext_sha256']==k['plaintext_mapping_sha256'],'ESCROW_PLAINTEXT_DRIFT')
    j=json.loads(msg)
    check(len(j['pairs'])==24 and [x['pair_id'] for x in j['pairs']]==[f'R{i:02d}' for i in range(1,25)],'ESCROW_PAIR_DRIFT')
    # Deliberately no mapping content printed or written here.
    return sha(msg)

def main():
    import torch
    check(torch.cuda.is_available() and torch.cuda.device_count()==1,'EXACT_ONE_CUDA_DEVICE_REQUIRED')
    check('T4' in torch.cuda.get_device_name(0),'EXACT_T4_REQUIRED')
    check(torch.__version__=='2.14.1+cu130','TORCH_VERSION_DRIFT')
    check(NEXT.is_dir() and PUB.is_dir() and PRIVATE.is_dir(),'OWNER_DIRECTORY_NOT_PRESENT')
    check(not (BEGIN.exists() or RAW.exists() or RECEIPT.exists()),'ONE_SHOT_ALREADY_STARTED_OR_FINISHED')
    consent=json.loads(verify_file(GO,OWNER_GO_SHA,1417))
    check(consent['run_id']==RUN_ID and consent['owner_authorizes_one_shot_inference'] is True,'OWNER_EXPLICIT_GO_MISSING')
    check(consent['reviewer_acceptance_before_inference_required'] is False,'REVIEWER_RULE_CHANGED')
    t4=json.loads(verify_file(T4,COLAB_PIN_SHA,1250))
    check(t4['run_id']==RUN_ID and t4['checks_count']==10 and t4['model_forward']==0,'T4_PRIOR_PIN_NOT_PASS')
    check(t4['verdict']=='PASS_RUNTIME_SOURCE_PIN_ONLY__SCIENCE_RELEASE_HOLD_PENDING_REAL_OWNER_AND_RATER','T4_PRIOR_RECEIPT_CHANGED')
    code={label:get_source(path,blob) for label,(path,blob) in SRC.items()}
    check(sha(code['decoder'])=='64a812a49f8d82d2c797d9150b2d3278763d411fff3e3b53424e650711092e85','DECODER_SOURCE_SHA')
    bpe_module=import_code('ttm_hdec_exact_bpe',code['bpe'])
    dec_module=import_code('ttm_hdec_exact_decoder',code['decoder'])
    p02=import_code('ttm_hdec_exact_p02',code['p02'])
    bpe=bpe_module.BPE2048.from_manifest(json.loads(verify_file(BPE,BPE_SHA,34589)))
    eval_obj=json.loads(verify_file(EVAL,OWNER_EVAL_SHA,18076))
    pub=json.loads(verify_file(PUBLIC_COMMITMENT,COMMIT_SHA,6509))
    prompts=eval_obj['prompts']
    check(len(prompts)==36 and [p['id'] for p in prompts]==[f'ND{i:02d}' for i in range(1,13)]+[f'NF{i:02d}' for i in range(1,25)],'NEW_PROMPT_ID_DRIFT')
    final=[p for p in prompts if p['cohort']=='BLIND_FINAL']
    check([p['prompt_utf8_sha256'] for p in final]==[p['prompt_utf8_sha256'] for p in pub['sha256_per_final_prompt']],'FINAL_SHA_COMMITMENT_DRIFT')
    pretokenized={}
    for p in prompts:
        text=p['prompt']
        check(sha(text.encode('utf-8'))==p['prompt_utf8_sha256'],'PROMPT_HASH_'+p['id'])
        ids=bpe.encode(text)
        check(bpe.decode(ids)==text,'PROMPT_BPE_ROUNDTRIP_'+p['id'])
        check(0<len(ids) and len(ids)+64<=256 and bpe_module.EOS_ID not in ids,'PROMPT_CONTEXT_'+p['id'])
        pretokenized[p['id']]=ids
    encrypted_digest=escrow_verify()
    # The pinned earlier Colab preflight SHA already checked these exact files.
    verify_file(CKPT,A_SHA,45087641)
    check(dec_module.VOCAB_SIZE==2048 and dec_module.EOS_ID==256 and dec_module.PENALTY==1.15 and dec_module.MAX_NEW_TOKENS==64,'DECODER_CONTRACT_DRIFT')
    state=torch.load(CKPT,map_location='cpu',weights_only=True)
    check(state['arm']=='A' and state['step']==1152 and state['run_id']=='TTM_SMALL4M_AC_OBJECTIVE_ONLY_V1','CKPT_IDENTITY_DRIFT')
    check(len(state['history'])==128,'CKPT_HISTORY_DRIFT')
    cfg=p02.P02Config(vocab_size=2048,max_seq_len=256,n_embd=256,n_layer=4,n_head=4,norm_type='layernorm')
    model=p02.GPT(cfg).to('cuda')
    model.load_state_dict(state['model'],strict=True)
    check(sum(p.numel() for p in model.parameters())==3749376,'CKPT_MODEL_PARAMETER_DRIFT')
    model.eval()
    del state
    # Exact atomic launch claim. Never resume/replay when BEGIN already exists.
    exclusive_json(BEGIN,{
      'schema':'ttm.small4m.hdec_r1.owner_one_shot_begin.v1',
      'run_id':RUN_ID,'source_commit':SOURCE_COMMIT,'checkpoint_sha256':A_SHA,
      'owner_go_sha256':OWNER_GO_SHA,'Colab_no_forward_pin_sha256':COLAB_PIN_SHA,
      'private_eval_sha256':OWNER_EVAL_SHA,'mapping_digest_only':encrypted_digest,
      'status':'BEGIN_CLAIMED_ONE_SHOT_NO_REPLAY','training_steps':0
    })
    results=[]; forwards=0
    # One fixed pass: 12 DEV then 24 FINAL; each D0, then D1. No tuning.
    for p in prompts:
        for arm in ('D0','D1'):
            prefix=pretokenized[p['id']]
            tokens=list(prefix);generated=[]
            for _ in range(64):
                x=torch.tensor([tokens[-256:]],dtype=torch.long,device='cuda')
                with torch.inference_mode(),torch.autocast('cuda',dtype=torch.float16):
                    logits,_=model(x)
                forwards+=1
                next_id=dec_module.next_token_from_logits(
                    logits[0,-1].float().cpu().tolist(),generated,arm)
                generated.append(next_id);tokens.append(next_id)
                if next_id==bpe_module.EOS_ID: break
            output=bpe.decode(generated,allow_eos=True)
            result={
               'prompt_id':p['id'],'cohort':p['cohort'],'arm_owner_only':arm,
               'prompt_sha256':p['prompt_utf8_sha256'],
               'continuation':output,'continuation_utf8_sha256':sha(output.encode('utf-8')),
               'new_bpe_tokens':len(generated),
               'stop_reason':dec_module.stop_reason(generated)
            }
            results.append(result)
    check(len(results)==72 and len([x for x in results if x['cohort']=='BLIND_FINAL'])==48,'GENERATIONS_NOT_72')
    # Raw outputs with D0/D1 labels remain owner-only; NEVER publish this file.
    exclusive_json(RAW,{
      'schema':'ttm.small4m.hdec_r1.owner_only_one_shot_generations.v1',
      'run_id':RUN_ID,'source_commit':SOURCE_COMMIT,'checkpoint_sha256':A_SHA,
      'owner_eval_sha256':OWNER_EVAL_SHA,'owner_GO_sha256':OWNER_GO_SHA,
      'escrow_public_ciphertext_sha256':ESCROW_SHA,
      'decoder_rules':'FROZEN_D0_VS_D1_1_15_CONTINUATION_ONLY',
      'status':'OWNER_GENERATED_NOT_BLIND_SCORED_NOT_UNBLINDED','records':results
    })
    raw_sha=sha(RAW.read_bytes())
    exclusive_json(RECEIPT,{
      'schema':'ttm.small4m.hdec_r1.owner_one_shot_generation_safe_receipt.v1',
      'run_id':RUN_ID,'T4_runtime':'PASS','checkpoint_sha256':A_SHA,
      'source_commit':SOURCE_COMMIT,'owner_GO_sha256':OWNER_GO_SHA,
      'source_pin_receipt_sha256':COLAB_PIN_SHA,'eval_sha256':OWNER_EVAL_SHA,
      'raw_owner_only_sha256':raw_sha,
      'dev_generations':24,'final_generations':48,'total_generations':72,
      'model_forward_calls':forwards,'optimizer_updates':0,
      'scoring':'NOT_STARTED','blind_packet':'NOT_CREATED','unblind':'NOT_EXECUTED',
      'reviewer_pre_acceptance':'NOT_REQUIRED_BY_OWNER',
      'verdict':'COMPLETE_OWNER_GENERATION_UNADJUDICATED_PENDING_BLIND_PACKET'
    })
    print('HDEC_R1_OWNER_ONE_SHOT_GENERATION=COMPLETE_72_UNADJUDICATED')
    print('HDEC_R1_OWNER_RAW_SHA256='+raw_sha)
    print('HDEC_R1_OWNER_RECEIPT_SHA256='+sha(RECEIPT.read_bytes()))
    print('HDEC_R1_OWNER_GENERATIONS=24_DEV_48_FINAL')
    print('HDEC_R1_MODEL_FORWARD_CALLS='+str(forwards))
    print('HDEC_R1_SCORING=NOT_STARTED')
    print('HDEC_R1_UNBLIND=NOT_EXECUTED')

if __name__=='__main__':
    try: main()
    except Exception as exc:
        print(str(exc),file=sys.stderr)
        print('HDEC_R1_SCIENCE=HOLD_NO_AUTOMATIC_RETRY',file=sys.stderr)
        raise SystemExit(2)
