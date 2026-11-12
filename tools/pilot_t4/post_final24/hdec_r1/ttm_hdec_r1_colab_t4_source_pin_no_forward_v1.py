#!/usr/bin/env python3
"""H-DEC-R1 owner Colab T4 *pre-inference* pin check, with no model load/forward.

No TEST/Q1/Q2/OOD reads. No plaintext FINAL output. The only write is a
nonsecret, append-once PASS receipt under the new owner study directory.
This does NOT grant rights, assert reviewer acceptance or authorize inference.
"""
from __future__ import annotations
import hashlib
import json
import os
from pathlib import Path
import subprocess
import sys
import urllib.request

REPO = 'minhtri22/TokenToModel-Lab'
SOURCE_COMMIT = 'c784b4a0687f6b0fd840f41d3bbf93e5c31038a7'
RUN_ID = 'TTM_SMALL4M_POST_FINAL24_DECODING_REPETITION_DIAGNOSTIC_V1'
SOURCE = {
  'decoder': ('tools/pilot_t4/post_final24/hdec_r1/ttm_hdec_r1_deterministic_decoder_v1.py', 'b6fd0cf0efd4be759da70814de5c5706f5532416', '64a812a49f8d82d2c797d9150b2d3278763d411fff3e3b53424e650711092e85'),
  'scorer': ('tools/pilot_t4/post_final24/hdec_r1/ttm_hdec_r1_frozen_metrics_v1.py', '404eda4326955d706cf007d47df90832fa425492', '1c5cecf97cc86da1d833c9c4959d4532c989d5c0e604a1490e88c684870828f1'),
  'BPE_source': ('tools/pilot_t4/integrated/source_t2/ttm_gpt2_bpe2048.py', 'fa5bd892941ba5aa6e6b2f0b2b0ae974efe297b6', None),
  'P02_source': ('src/p02/transformer_core.py', '9762343e06cf800b50574c2871ae1ed58537fb18', None),
  'public_escrow': ('artifacts/qa/ttm-small4m-post-final24/hdec_r1/HDEC_R1_PUBLIC_SAFE_ENCRYPTED_MAPPING.json', '16d5d384e0d7ad70ccbc691e5236e462d683f4aa', '812e7e23cdc3eba4735bfb0b8ff43b2a7420fbaac4fa0edfc2fe4a944cb8c3b7'),
  'public_prompt_commitment': ('docs/research/ttm-small4m-post-final24/TTM_SMALL4M_NEXT_EVAL_FINAL24_PUBLIC_SHA_COMMITMENT_20261112.json', '8b38514939c6f940924986c7572c5da2c93fb0a4', '3c6d484d40eba4cbdf0d122d032e228b02fa67af48647830a273f93a54f32060'),
}
DRIVE = Path('/content/drive/MyDrive/TTM/ttm-small-pilot')
AC = DRIVE/'ttm_small4m_ac_objective_only_v1'
NEXT = DRIVE/'ttm_small4m_post_final24_next_eval_v1'
FILE_PINS = {
 'A1152_checkpoint': (AC/'TTM_SMALL4M_AC_OBJECTIVE_ONLY_V1_SCIENCE/ARM_A/step_1152.pt', 45087641, 'ae9f05c5234ac98e3f9150e3f27501d217c1942a381650bec5aef91a1f56196b'),
 'BPE_manifest': (AC/'T1_BPE2048_REAL_TRAIN_MANIFEST.json', 34589, 'cba18e60cee3d08a353ee6d4a451017289e45af7b4b1179c87171b9b78d7dfdc'),
 'new_owner_eval': (NEXT/'owner_private/TTM_SMALL4M_NEXT_EVAL_OWNER_PRIVATE_DEV12_FINAL24_20261112.json', 18076, '9480ba73cbbe425fc9b61cc3253df81b32d52b0c35127d6e4392e5b5d6b0d54f'),
}
RECEIPT = NEXT/'public_safe/TTM_HDEC_R1_T4_NO_FORWARD_SOURCE_PIN_RECEIPT_20261112.json'

def sha(b: bytes) -> str:
    return hashlib.sha256(b).hexdigest()

def git_blob(b: bytes) -> str:
    return hashlib.sha1(b'blob '+str(len(b)).encode()+b'\0'+b).hexdigest()

def sha_path(path: Path) -> tuple[int,str]:
    h=hashlib.sha256(); count=0
    with path.open('rb') as f:
        for chunk in iter(lambda: f.read(1024*1024),b''):
            h.update(chunk);count+=len(chunk)
    return count,h.hexdigest()

def check(ok, reason):
    if not ok: raise RuntimeError('HDEC_R1_PREINFERENCE_HOLD:'+reason)

def source_bytes(path):
    u=f'https://raw.githubusercontent.com/{REPO}/{SOURCE_COMMIT}/{path}'
    with urllib.request.urlopen(urllib.request.Request(u,headers={'User-Agent':'TTM-HDEC-R1-owner-pin-check/1.0'}),timeout=25) as f:
        b=f.read(1_500_001)
    check(len(b)<=1_500_000,'SOURCE_OVERSIZED_'+path)
    return b

def main():
    import torch  # runtime introspection ONLY: never creates model or tensor
    check(torch.cuda.is_available(),'T4_CUDA_NOT_AVAILABLE')
    devices=[torch.cuda.get_device_name(i) for i in range(torch.cuda.device_count())]
    check(len(devices)==1 and 'T4' in devices[0],'GPU_NOT_EXACT_SINGLE_T4')
    gpu=subprocess.run(['nvidia-smi','--query-gpu=name,memory.total','--format=csv,noheader'],capture_output=True,text=True,timeout=15,check=True).stdout.strip()
    check('T4' in gpu,'NVIDIA_SMI_NOT_T4')
    checks=[]
    for label,(path,expected_blob,expected_sha) in SOURCE.items():
        b=source_bytes(path)
        check(git_blob(b)==expected_blob,'GIT_BLOB_SHA1_'+label)
        if expected_sha: check(sha(b)==expected_sha,'SOURCE_SHA256_'+label)
        checks.append('PIN_GIT_BLOB_AND_SHA_'+label)
    for label,(path,expected_size,expected_sha) in FILE_PINS.items():
        check(path.is_file(),'OWNER_FILE_MISSING_'+label)
        size,h=sha_path(path)
        check(size==expected_size and h==expected_sha,'OWNER_SOURCE_DRIFT_'+label)
        checks.append('PIN_OWNER_BYTE_SHA256_'+label)
    ready_path=AC/'TTM_SMALL4M_AC_OBJECTIVE_ONLY_V1_SCIENCE/ARM_A/READY_1152.json'
    final_path=AC/'TTM_SMALL4M_AC_OBJECTIVE_ONLY_V1_SCIENCE/ARM_A/FINAL.json'
    check(ready_path.is_file() and final_path.is_file(),'READY_FINAL_MISSING')
    ready=json.loads(ready_path.read_bytes()); final=json.loads(final_path.read_bytes())
    check(ready.get('arm')=='A' and ready.get('step')==1152 and ready.get('history_length')==128,'READY_ID_DRIFT')
    check(ready.get('checkpoint_sha256')==FILE_PINS['A1152_checkpoint'][2],'READY_CHECKPOINT_HASH_DRIFT')
    check(final.get('arm')=='A' and final.get('step')==1152 and final.get('status')=='TRAINED_CHECKPOINT_UNADJUDICATED','FINAL_STATUS_DRIFT')
    check(final.get('ready_checkpoint_sha256')==ready['checkpoint_sha256'],'FINAL_READY_HASH_DRIFT')
    check(final.get('target_exposures')==524288,'TARGET_EXPOSURE_DRIFT')
    checks.append('READY_FINAL_A_1152_AND_TARGETS')
    check(RECEIPT.parent.is_dir(),'REPORT_FOLDER_NOT_FOUND')
    report={
     'schema':'ttm.small4m.hdec_r1.owner_colab_t4.preinference_source_pin.v1',
     'run_id':RUN_ID,'source_git_commit':SOURCE_COMMIT,
     'gpu_name':devices[0], 'nvidia_smi_gpu':gpu,
     'torch_version':torch.__version__, 'cuda_version':torch.version.cuda,
     'source_pins':'EXACT_GIT_BLOB_AND_SHA_MATCH','owner_files':'EXACT_BYTES_SHA_MATCH',
     'checks':checks, 'checks_count':len(checks),
     'owner_rights_signature_assumed':False,'rater_acceptance_assumed':False,
     'owner_inference_GO_granted':False,
     'model_loaded':False,'model_forward':0,'optimizer_updates':0,
     'FINAL24_text_printed':False,'old_FINAL24_reopened':False,
     'verdict':'PASS_RUNTIME_SOURCE_PIN_ONLY__SCIENCE_RELEASE_HOLD_PENDING_REAL_OWNER_AND_RATER'
    }
    # Record only nonsecret static/metadata fields, never any private content.
    payload=(json.dumps(report,ensure_ascii=False,sort_keys=True,indent=2)+'\n').encode('utf-8')
    if RECEIPT.exists():
        check(RECEIPT.read_bytes()==payload,'RECEIPT_ALREADY_EXISTS_DIFFERENT_BYTES')
    else:
        with RECEIPT.open('xb') as f: f.write(payload)
    print('HDEC_R1_T4_SOURCE_PIN=PASS')
    print('HDEC_R1_SOURCE_CHECKS='+str(len(checks)))
    print('HDEC_R1_RECEIPT_SHA256='+sha(payload))
    print('HDEC_R1_RECEIPT='+str(RECEIPT))
    print('HDEC_R1_MODEL_FORWARD=0')
    print('HDEC_R1_RELEASE=HOLD_PENDING_OWNER_AND_RATER')

if __name__=='__main__':
    try: main()
    except Exception as exc:
        print(str(exc),file=sys.stderr)
        print('HDEC_R1_RELEASE=HOLD',file=sys.stderr)
        raise SystemExit(2)
