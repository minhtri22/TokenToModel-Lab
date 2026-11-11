#!/usr/bin/env python3
"""TTM VM external facts TEST one-shot private escrow and byte-envelope static audit.

No model training, no inference, and no TEST material in public output.
Real T1 BPE exact-token audit is deliberately fail-closed if the pinned manifest is unavailable.
"""
from __future__ import annotations
import collections
import hashlib
import importlib.util
import json
import os
import secrets
from pathlib import Path
from cryptography.hazmat.primitives.ciphers.aead import AESGCM

WORK = Path('/mnt/data/ttm_vm_external_facts_seal_20261111/TokenToModel-Lab')
PRIVATE = WORK / '_private' / 'vector-memory' / 'external-facts-test-v1'
SOURCE = Path('/mnt/data/TTM_VM_external_knowledge_fixture.py')
TRAIN = Path('/mnt/data/TTM_VM_EXTERNAL_FACTS_TRAIN_256_V1.json')
DEV = Path('/mnt/data/TTM_VM_EXTERNAL_FACTS_DEV_64_V1.json')
GEN_EXPECT = 'a206bf0c1804969feea993dde0d096b730ce7fed2f79b792c334bd0a4f06609c'
TRAIN_SHA = '3e51b482cb7bd63c56d7a252d29c39932081602ab1dee1e9ed6223c3778852e2'
DEV_SHA = 'ce9f91c76f96d7a57f616d2cc9e8415b065dcfa1074ec63e33ffa61fa662f883'
TOKENIZER_EXPECT = 'cba18e60cee3d08a353ee6d4a451017289e45af7b4b1179c87171b9b78d7dfdc'

def sha(b: bytes)->str: return hashlib.sha256(b).hexdigest()
def canon(obj):return (json.dumps(obj,sort_keys=True,separators=(',',':'),ensure_ascii=False)+'\n').encode('utf-8')
def save_excl(p: Path, data: bytes):
    p.parent.mkdir(parents=True, exist_ok=True)
    fd=os.open(str(p),os.O_WRONLY|os.O_CREAT|os.O_EXCL,0o600)
    try:
        with os.fdopen(fd,'wb') as f: f.write(data); f.flush(); os.fsync(f.fileno())
    except:
        p.unlink(missing_ok=True);raise

assert sha(SOURCE.read_bytes()) == GEN_EXPECT
spec=importlib.util.spec_from_file_location('ttm_vm_ext_fact',SOURCE)
m=importlib.util.module_from_spec(spec)
spec.loader.exec_module(m)
assert sha(m.stable_json(m.build('train')))==TRAIN_SHA
assert sha(m.stable_json(m.build('dev')))==DEV_SHA
assert sha(TRAIN.read_bytes())=='1c44055fae2281015228b74b3b6e3dffa513becd9207d43c28658ef063a6a57d'
assert sha(DEV.read_bytes())=='fd68373f7765eead4cd5744584abc71d5377bc184863e28cdef7ad3cdfc3e05f'
# Only one call generates a new secret and the only actual TEST dataset.
if PRIVATE.exists():
    raise SystemExit('TEST_ESCROW_DIR_ALREADY_EXISTS_STOP_NO_RESEED')
secret=secrets.token_urlsafe(48)
assert len(secret)>=24
cases=m.build('test',secret)
train=m.build('train');dev=m.build('dev')
allcases=train+dev+cases
train_keys={c['target_key'] for c in train};dev_keys={c['target_key'] for c in dev};test_keys={c['target_key'] for c in cases}
checks={
 'test_count_64':len(cases)==64,
 'train_dev_test_target_keys_disjoint':not(train_keys&dev_keys or train_keys&test_keys or dev_keys&test_keys),
 'test_case_ids_disjoint':len({x['case_id'] for x in allcases})==len(allcases),
 'test_answer_balanced':all(sum(c['answer']==l for c in cases)==4 for l in m.LABELS),
 'test_answer_not_in_question':all(c['answer'] not in c['question'] for c in cases),
 'test_target_key_in_question':all(c['target_key'] in c['question'] for c in cases),
 'test_real_right_wrong_none_contract':all(m.validate_case(c) is None for c in cases),
 'test_question_templates_two':len({c['question'].split('archive object')[0] for c in cases})==2,
 'test_target_rank_all_positions':set(c['target_record_rank'] for c in cases)=={0,1,2},
 'private_generator_uses_strong_secret':len(secret)>=24,
 'no_test_in_train_dev_files':all(c['split'] != 'test' for c in train+dev),
 'all_ascii_questions_answers_memory':all(all(ord(x)<128 for x in c['question']+c['answer']+''.join(t['text'] for t in c['correct_memory']+c['wrong_memory'])) for c in allcases),
}
# Safe upper bound: byte-level BPE starts at one token/UTF8 byte, merges never increase number of tokens.
questions=[c['question'] for c in allcases];answers=[c['answer'] for c in allcases]
texts=[c['question']+' '+c['answer'] for c in allcases]
record_texts=[card['text'] for c in allcases for card in c['correct_memory']+c['wrong_memory']]
max_question=max(len(x.encode()) for x in questions)
max_label=max(len(x.encode()) for x in answers)
max_prompt_answer=max(len(x.encode()) for x in texts)
max_fact=max(len(x.encode()) for x in record_texts)
checks.update({
 'question_max_byte_tokens_le_256':max_question<=256,
 'answer_max_byte_tokens_le_256':max_label<=256,
 'prompt_plus_answer_max_byte_tokens_le_256':max_prompt_answer<=256,
 'each_memory_record_byte_tokens_le_256':max_fact<=256,
 'gold_leading_space_absent_from_question':all(not c['question'].endswith(' ') for c in allcases),
 'candidate_labels_unique_len16':len(set(m.LABELS))==16,
})
assert all(checks.values()),[k for k,v in checks.items() if not v]
raw=canon({'schema':m.SCHEMA,'split':'test','cases':cases})
# AES256-GCM. Encryption key is held in separate owner-only escrow file.
key=AESGCM.generate_key(bit_length=256)
nonce=os.urandom(12)
aad=b'TTM_VM_TEST_64_V1_SCHEMA_SEAL_20261111'
ciphertext=AESGCM(key).encrypt(nonce,raw,aad)
assert AESGCM(key).decrypt(nonce,ciphertext,aad)==raw
enc=canon({'schema':'ttm.vm.externalfacts.test.aesgcm.v1','algorithm':'AES-256-GCM',
           'nonce_hex':nonce.hex(),'aad_ascii':aad.decode('ascii'),
           'ciphertext_hex':ciphertext.hex()})
public={
 'schema':'ttm.vm.externalfacts.test.public_seal.v1',
 'study':'TTM_VECTOR_MEMORY_EXTERNAL_FACTS_TEST_SEAL_AND_TOKENIZER_COMPATIBILITY_STATIC_QA',
 'generator_sha256':GEN_EXPECT,
 'train_fixture_sha256':TRAIN_SHA,'dev_fixture_sha256':DEV_SHA,
 'test_cases':len(cases),'test_plaintext_sha256':sha(raw),'test_encrypted_sha256':sha(enc),
 'test_secret_sha256_commitment':sha(secret.encode('utf-8')),
 'test_key_sha256_commitment':sha(key),
 'external_seal':'OWNER_PRIVATE_ESCROW_ENCRYPTED_NO_PUBLIC_ROWS',
 'no_retrain':True,'no_inference':True,'no_gpu':True,
 'source_split':'NEW_SYNTHETIC_AFTER_FROZEN_CHECKPOINT',
 'lineage':'NO_APPEND_DESIGN_AND_STATIC_QA_ONLY',
 'test_open_policy':'DO_NOT_DECRYPT_OR_READ_FOR_MODEL_SELECTION; ONE_SHOT_AFTER_FROZEN_RUNNER_AND_DEV',
}
audit={
 'schema':'ttm.vm.externalfacts.test.tokenizer.static_qa.v1',
 'scope':'CONTRACT_AND_UTF8_BYTE_BPE_UPPER_BOUND_ONLY; NO_REAL_T1_MANIFEST_AVAILABLE',
 'status':'PARTIAL_PASS_REAL_TOKENIZER_EXACT_IDS_HOLD',
 'checks':checks, 'checks_passed':sum(checks.values()), 'checks_total':len(checks),
 'counts':{'train':len(train),'dev':len(dev),'test':len(cases)},
 'upper_bounds_bytes':{'max_question':max_question,'max_answer':max_label,'max_prompt_plus_answer':max_prompt_answer,'max_fact_card':max_fact},
 'context_max':256,'actual_t1_bpe_file_sha256_expected':TOKENIZER_EXPECT,
 'actual_t1_bpe_manifest_status':'NOT_AVAILABLE_IN_CONNECTED_SOURCES',
 'actual_t1_encode_decode_status':'NOT_EXECUTED',
 'actual_t1_answer_token_counts_status':'NOT_EXECUTED',
 'actual_t1_prompt_prefix_alignment_status':'NOT_EXECUTED',
 'warning':'Byte-level BPE upper bound is proven by merge-only property; cannot claim exact real tokenizer IDs or answer-token segmentation without pinned T1 manifest.',
 'test_private_sha256':sha(raw),'test_encrypted_sha256':sha(enc),
 'test_seal_status':'SEALED_PRIVATE_ENCRYPTED_NOT_PUBLIC',
 'science':'NOT_EXECUTED',
}
escrow={
 'schema':'ttm.vm.externalfacts.test.owner_private_escrow.v1',
 'secret':secret,'aes256_key_hex':key.hex(),
 'plaintext_sha256':sha(raw),'encrypted_sha256':sha(enc),
 'generator_sha256':GEN_EXPECT,
 'sealed_test_name':'TTM_VM_EXTERNAL_TEST_64_V1.aesgcm.json',
 'instruction':'KEEP PRIVATE. Unlock only after training + DEV + runner pins frozen. Never commit to GitHub.',
}
# Retain encrypted TEST and separate escrow; no raw plaintext file survives.
save_excl(PRIVATE/'TTM_VM_EXTERNAL_TEST_64_V1.aesgcm.json',enc)
save_excl(PRIVATE/'TTM_VM_EXTERNAL_TEST_OWNER_SECRET_ESCROW_V1.json',canon(escrow))
save_excl(Path('/mnt/data/TTM_VM_TEST_PUBLIC_SEAL_20261111.json'),canon(public))
save_excl(Path('/mnt/data/TTM_VM_TOKENIZER_BOUND_STATIC_QA_20261111.json'),canon(audit))
print(json.dumps({'seal':'CREATED','encrypted_test_sha256':sha(enc),'test_plaintext_commitment':sha(raw),
                  'static_checks':f"{len(checks)}/{len(checks)}",'max_prompt_answer_byte_bound':max_prompt_answer,
                  'actual_real_t1_bpe':'HOLD_MISSING_MANIFEST',
                  'science':'NOT_EXECUTED','secret_exposed':False},sort_keys=True))
