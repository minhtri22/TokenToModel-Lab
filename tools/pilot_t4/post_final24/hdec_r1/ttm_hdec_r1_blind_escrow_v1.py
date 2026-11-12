#!/usr/bin/env python3
"""H-DEC-R1 original random balanced blind mapping: create ONCE or verify only.

DO NOT commit the private key nor the clear NFXX=>D0/D1 map to public GitHub.
This never opens the FINAL prompt texts and never performs model inference.
"""
from __future__ import annotations
import argparse, base64, collections, hashlib, json, os, random
from pathlib import Path
from cryptography.hazmat.primitives.ciphers.aead import AESGCM

RUN_ID='TTM_SMALL4M_POST_FINAL24_DECODING_REPETITION_DIAGNOSTIC_V1'
SCHEMA='ttm.small4m.hdec_r1.private_original_balanced_mapping.v1'
AAD='TTM_SMALL4M_HDEC_R1_V1_NF01_NF24_D0_D1_20261112'

def canonical(obj):
 return json.dumps(obj,ensure_ascii=False,sort_keys=True,separators=(',',':')).encode('utf8')
def sha(b):return hashlib.sha256(b).hexdigest()
def dump_exact(path,data):
 with open(path,'xb') as f:f.write(data)
def make(dest):
 d=Path(dest); d.mkdir(parents=True,exist_ok=True)
 keyfile=d/'HDEC_R1_OWNER_PRIVATE_AES_KEY_DO_NOT_SHARE.json'
 escrowfile=d/'HDEC_R1_PUBLIC_SAFE_ENCRYPTED_MAPPING.json'
 if keyfile.exists() or escrowfile.exists():raise RuntimeError('EXISTING_ESCROW_DO_NOT_REKEY')
 by_stratum=[('object_custody',range(1,7)),('social_relation',range(7,13)),('causal_obstacle',range(13,19)),('temporal_rule',range(19,25))]
 chooser=random.SystemRandom();pairs=[]
 for stratum,ids in by_stratum:
  order=list(ids);chooser.shuffle(order)
  leftD0=set(order[:3])
  for k in ids:
   left='D0' if k in leftD0 else 'D1'
   pairs.append({'pair_id':f'R{k:02d}','prompt_id':f'NF{k:02d}','left_arm':left,'right_arm':'D1' if left=='D0' else 'D0','stratum':stratum})
 payload={'schema':SCHEMA,'run_id':RUN_ID,'pairs':pairs}
 plain=canonical(payload)
 key=AESGCM.generate_key(bit_length=256);nonce=os.urandom(12)
 ciphertext=AESGCM(key).encrypt(nonce,plain,AAD.encode('utf8'))
 escort={'schema':'ttm.small4m.hdec_r1.original_encrypted_escrow.v1','run_id':RUN_ID,'cipher':'AES-256-GCM','aad_utf8':AAD,'nonce_b64':base64.b64encode(nonce).decode(),'ciphertext_b64':base64.b64encode(ciphertext).decode(),'plaintext_sha256':sha(plain),'pair_count':24,'position_balance':'12_D0_LEFT_12_D1_LEFT_AND_3_3_PER_STRATUM','generation':'one-shot-cryptographic-randomness-20261112','no_model_forward':True,'no_rater_scores':True}
 keymeta={'schema':'ttm.small4m.hdec_r1.private_aes_key.v1','run_id':RUN_ID,'key_b64':base64.b64encode(key).decode(),'public_ciphertext_sha256':sha(canonical(escort)+b'\n'),'plaintext_mapping_sha256':sha(plain),'owner_only':True,'rekey_forbidden':True}
 # file mode private, host may manage ACL differently; Drive sharing must also be checked.
 for name,obj in [(keyfile,keymeta),(escrowfile,escort)]:
  fd=os.open(name,os.O_WRONLY|os.O_CREAT|os.O_EXCL,0o600)
  with os.fdopen(fd,'wb') as f:f.write(canonical(obj)+b'\n')
 return {'public_escrow_sha256':sha(escrowfile.read_bytes()),'private_key_file_sha256':sha(keyfile.read_bytes()),'mapping_plaintext_sha256':sha(plain),'pairs':24,'balance':'3/3 in each stratum','private_file_paths_not_for_public_use':True}

def verify(dest):
 d=Path(dest);ecb=(d/'HDEC_R1_PUBLIC_SAFE_ENCRYPTED_MAPPING.json').read_bytes();keyb=(d/'HDEC_R1_OWNER_PRIVATE_AES_KEY_DO_NOT_SHARE.json').read_bytes()
 ec=json.loads(ecb);k=json.loads(keyb)
 if sha(ecb)!=k['public_ciphertext_sha256']:raise RuntimeError('ESCROW_MISMATCH')
 clear=AESGCM(base64.b64decode(k['key_b64'])).decrypt(base64.b64decode(ec['nonce_b64']),base64.b64decode(ec['ciphertext_b64']),ec['aad_utf8'].encode('utf8'))
 if sha(clear)!=ec['plaintext_sha256'] or sha(clear)!=k['plaintext_mapping_sha256']:raise RuntimeError('MAPPING_SHA_MISMATCH')
 j=json.loads(clear);p=j['pairs']
 if len(p)!=24 or [x['pair_id'] for x in p]!=[f'R{i:02d}' for i in range(1,25)]:raise RuntimeError('RATER_IDS_MISMATCH')
 by=collections.defaultdict(list)
 for row in p:
  if {row['left_arm'],row['right_arm']}!={'D0','D1'} or row['prompt_id']!='NF'+row['pair_id'][1:]:raise RuntimeError('PAIR_MISMATCH')
  by[row['stratum']].append(row['left_arm'])
 if len(by)!=4 or any(collections.Counter(v)!={'D0':3,'D1':3} for v in by.values()):raise RuntimeError('STRATUM_BALANCE_MISMATCH')
 return {'public_escrow_sha256':sha(ecb),'private_key_file_sha256':sha(keyb),'mapping_plaintext_sha256':sha(clear),'R_pairs':24,'per_stratum_3_3':'PASS','AESGCM':'PASS','no_reviewer_scores':True}

if __name__=='__main__':
 a=argparse.ArgumentParser();a.add_argument('--private-dir',required=True);a.add_argument('--create-once',action='store_true');a.add_argument('--verify-only',action='store_true');v=a.parse_args()
 if v.create_once == v.verify_only:raise SystemExit('EXACTLY_ONE_OF_CREATE_ONCE_OR_VERIFY_ONLY_REQUIRED')
 result=make(v.private_dir) if v.create_once else verify(v.private_dir)
 print(json.dumps(result,sort_keys=True))
