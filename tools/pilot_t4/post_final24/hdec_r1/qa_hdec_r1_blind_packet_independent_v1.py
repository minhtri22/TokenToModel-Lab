#!/usr/bin/env python3
"""Independent implementation readback for NEXT24 rater ZIP.
Never print plaintext outputs, original mapping, key or per-pair arm assignment.
Never perform model forward, score or unblind. Output safe aggregate only.
"""
from __future__ import annotations
import base64, collections, hashlib, json, pathlib, zipfile
from cryptography.hazmat.primitives.ciphers.aead import AESGCM
P=pathlib.Path('/mnt/data')
def digest(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def sha(b):return hashlib.sha256(b).hexdigest()
def j(name):return json.loads((P/name).read_bytes())
checks=[]
def ok(cond,name):
 if not cond: raise AssertionError('BLIND_PACKET_QA_HOLD:'+name)
 checks.append(name)
zip_path=P/'TTM_NEXT24_CHATGPT_BLIND_RATER.zip'
expected_zip='9ec48639974575e1cdebb28fcf9b2a0393a3318fb954dc9c5824e2f8bace927a'
expected_packet='e28049bf770ddab879fdd10ac5805b9b5bf2e60fa0f8f9264ba641abab82dd22'
with zipfile.ZipFile(zip_path) as z:
 ok(z.testzip() is None,'ZIP_CRC')
 names=z.namelist()
 ok(len(names)==5 and len(set(names))==5,'ZIP_FILE_COUNT_UNIQUE')
 ok(all(n.startswith('TTM_NEXT24_') and '/' not in n and '\\' not in n and n.endswith(('.md','.json')) for n in names),'ZIP_PATHS_SAFE')
 ok(sha(zip_path.read_bytes())==expected_zip,'ZIP_SHA')
 manifest=json.loads(z.read('TTM_NEXT24_BLIND_PACKET_MANIFEST.json'))
 ok(manifest['pair_count']==24 and manifest['text_count']==48 and manifest['unblind']=='NOT_EXECUTED','BUNDLE_MANIFEST_SCOPE')
 for item in manifest['files']:
  b=z.read(item['filename'])
  ok(len(b)==item['size'] and sha(b)==item['sha256'],'BUNDLE_FILE_SHA_'+item['filename'])
 packet_bytes=z.read('TTM_NEXT24_BLIND_PACKET.json')
 template_bytes=z.read('TTM_NEXT24_SCORE_TEMPLATE.json')
 handoff_bytes=z.read('TTM_NEXT24_INDEPENDENT_GPT6_HANDOFF.md')
 packet=json.loads(packet_bytes);template=json.loads(template_bytes)
 ok(sha(packet_bytes)==expected_packet,'PACKET_SHA')
 ok(packet['pair_count']==24 and packet['text_count']==48 and len(packet['pairs'])==24,'PACKET_COUNTS')
 ok([x['pair_id'] for x in packet['pairs']]==[f'R{i:02}' for i in range(1,25)],'PAIR_ORDER')
 ok(template['status']=='SCORING_NOT_STARTED' and template['score_sha256_before_unblind'] is None,'TEMPLATE_UNFILLED')
 ok(template['packet_json_sha256']==expected_packet,'TEMPLATE_PACKET_BOND')
 ok(len(template['scores'])==24 and [x['pair_id'] for x in template['scores']]==[x['pair_id'] for x in packet['pairs']],'TEMPLATE_ROW_ID_BOND')
 ok(all(all(t is None for side in ('left','right') for t in row[side].values()) and row['note'] is None for row in template['scores']),'NO_PRELOADED_SCORES')
 ok(all(len(row['left'])==3 and len(row['right'])==3 for row in template['scores']),'THREE_AXES_EACH')
 all_bytes=b''.join(z.read(n) for n in names)
 ok(all(x not in all_bytes for x in (b'arm_owner_only',b'left_arm',b'right_arm',b'key_b64',b'D0',b'D1',b'checkpoint_sha256',b'owner_GO_sha256')),'NO_OWNER_IDENTIFIERS_IN_RATER_BUNDLE')
 ok(b'144' in handoff_bytes and b'24 notes' in handoff_bytes and b'UNBLIND=NOT_EXECUTED' in handoff_bytes,'HANDOFF_SCORING_POLICY')

src=j('HDEC_R1_V1_OWNER_ONLY_72_D0_D1_RAW_GENERATIONS.json')
eval_doc=j('TTM_SMALL4M_NEXT_EVAL_OWNER_PRIVATE_DEV12_FINAL24_20261112.json')
ec=j('HDEC_R1_PUBLIC_SAFE_ENCRYPTED_MAPPING.json')
key=j('HDEC_R1_OWNER_PRIVATE_AES_KEY_DO_NOT_SHARE.json')
receipt=j('HDEC_R1_V1_OWNER_GENERATION_NONSECRET_RECEIPT.json')
ok(digest(P/'HDEC_R1_V1_OWNER_ONLY_72_D0_D1_RAW_GENERATIONS.json')==receipt['raw_owner_only_sha256']=='e09572c29993af8379a57cfc26c905912525e6238510f2803af5c9a81cc2f208','RAW_RECEIPT_SHA')
ok(digest(P/'HDEC_R1_V1_OWNER_GENERATION_NONSECRET_RECEIPT.json')=='bdd1a513fef9de45fc66873795b6a04551ebde9b08f9b1b7a37d4d028d51735a','RECEIPT_SHA')
ok(digest(P/'TTM_SMALL4M_NEXT_EVAL_OWNER_PRIVATE_DEV12_FINAL24_20261112.json')==src['owner_eval_sha256'],'PRIVATE_EVAL_SHA')
ok(digest(P/'HDEC_R1_PUBLIC_SAFE_ENCRYPTED_MAPPING.json')==key['public_ciphertext_sha256']==src['escrow_public_ciphertext_sha256'],'ESCROW_SHA')
clear=AESGCM(base64.b64decode(key['key_b64'])).decrypt(base64.b64decode(ec['nonce_b64']),base64.b64decode(ec['ciphertext_b64']),ec['aad_utf8'].encode())
ok(sha(clear)==key['plaintext_mapping_sha256']==ec['plaintext_sha256'],'AES_GCM_AUTH_ORIGINAL')
source_index={(r['prompt_id'],r['arm_owner_only']):r for r in src['records']}
prompt_index={r['id']:r for r in eval_doc['prompts']}
mapping=json.loads(clear)['pairs']
ok(len(source_index)==72 and len(prompt_index)==36 and len(mapping)==24,'INPUT_GRID')
counts=collections.Counter();groupcounts=collections.defaultdict(collections.Counter)
for idx,(pair,m) in enumerate(zip(packet['pairs'],mapping),1):
 rid=f'R{idx:02}'
 ok(pair['pair_id']==m['pair_id']==rid,'PAIR_ID_'+rid)
 pid=m['prompt_id'];p=prompt_index[pid]
 ok(p['cohort']=='BLIND_FINAL' and pair['prompt']==p['prompt'],'PROMPT_VALUE_'+rid)
 ok(sha(pair['prompt'].encode())==p['prompt_utf8_sha256'],'PROMPT_SHA_'+rid)
 ok(set(pair.keys())=={'pair_id','prompt','LEFT','RIGHT'},'PAIR_FIELDS_'+rid)
 for side,arm in [('LEFT',m['left_arm']),('RIGHT',m['right_arm'])]:
  rec=source_index[(pid,arm)]
  ok(pair[side]==rec['continuation'],'RAW_CONTINUATION_'+rid+'_'+side)
  ok(sha(pair[side].encode())==rec['continuation_utf8_sha256'],'RAW_CONT_SHA_'+rid+'_'+side)
 counts[m['left_arm']]+=1;groupcounts[m['stratum']][m['left_arm']]+=1
ok(counts=={'D0':12,'D1':12},'ORIGINAL_12_12_BALANCE')
ok(len(groupcounts)==4 and all(x=={'D0':3,'D1':3} for x in groupcounts.values()),'ORIGINAL_3_3_BALANCE')
ok(template['unblind']=='NOT_EXECUTED' and receipt['unblind']=='NOT_EXECUTED','UNBLIND_NONE')
report={'schema':'ttm.small4m.hdec_r1.next24.independent_blind_packet_check.v1','date':'2026-11-12','source_72_sha256':digest(P/'HDEC_R1_V1_OWNER_ONLY_72_D0_D1_RAW_GENERATIONS.json'),'generation_receipt_sha256':digest(P/'HDEC_R1_V1_OWNER_GENERATION_NONSECRET_RECEIPT.json'),'rater_zip_sha256':expected_zip,'rater_packet_json_sha256':expected_packet,'checks_passed':len(checks),'checks_failed':0,'pairs':24,'texts':48,'original_AES_mapping_reused':True,'all_48_texts_exact_match':True,'all_prompts_exact_match':True,'no_arm_labels_or_key_in_bundle':True,'source_TEST_Q1_Q2_OOD_not_accessed':True,'model_forward':0,'scores':0,'unblind':'NOT_EXECUTED','verdict':'PASS_INDEPENDENT_PACKET_READBACK_READY_FOR_BLIND_RATING'}
out=P/'HDEC_R1_NEXT24_INDEPENDENT_PACKET_READBACK_20261112.json'
out.write_text(json.dumps(report,ensure_ascii=False,indent=2,sort_keys=True)+'\n',encoding='utf8')
print(json.dumps({'checks':len(checks),'verdict':report['verdict'],'sha256':digest(out),'raw_source_hash':report['source_72_sha256'],'packet_sha256':expected_packet,'zip_sha256':expected_zip},indent=2))
