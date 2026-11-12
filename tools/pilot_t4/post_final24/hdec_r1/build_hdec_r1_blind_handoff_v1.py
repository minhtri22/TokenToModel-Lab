#!/usr/bin/env python3
"""Build neutral reviewer packet from exact frozen owner data and original AES mapping.
No model load, no model forward, no scoring, no rekey, no unblind. Owner-only source paths.
"""
import base64, collections, hashlib, json, os, pathlib, re, zipfile
from cryptography.hazmat.primitives.ciphers.aead import AESGCM

P=pathlib.Path('/mnt/data')
O=P/'hdec_r1_blind_handoff'
O.mkdir(parents=True,exist_ok=True)

expected={
 'HDEC_R1_V1_OWNER_ONLY_72_D0_D1_RAW_GENERATIONS.json':'e09572c29993af8379a57cfc26c905912525e6238510f2803af5c9a81cc2f208',
 'HDEC_R1_V1_OWNER_GENERATION_NONSECRET_RECEIPT.json':'bdd1a513fef9de45fc66873795b6a04551ebde9b08f9b1b7a37d4d028d51735a',
 'TTM_SMALL4M_NEXT_EVAL_OWNER_PRIVATE_DEV12_FINAL24_20261112.json':'9480ba73cbbe425fc9b61cc3253df81b32d52b0c35127d6e4392e5b5d6b0d54f',
 'HDEC_R1_PUBLIC_SAFE_ENCRYPTED_MAPPING.json':'812e7e23cdc3eba4735bfb0b8ff43b2a7420fbaac4fa0edfc2fe4a944cb8c3b7',
 'HDEC_R1_OWNER_PRIVATE_AES_KEY_DO_NOT_SHARE.json':'3e2b381fce29753621baec956b993b8c01e951925717c1730feb7aca0a548911',
 'HDEC_R1_V1_ONE_SHOT_BEGIN.json':'c7354afd44df8b0c29fdf9ae2a4d0e400b3e77b09cb6eda26822ebdcee84973e',
}
sha=lambda b:hashlib.sha256(b).hexdigest()
raw={}
checks=[]

def require(condition,name):
 if not condition: raise AssertionError('HDEC_BLIND_HOLD:'+name)
 checks.append(name)

for name,h in expected.items():
 contents=(P/name).read_bytes()
 require(sha(contents)==h,'SHA_'+name)
 raw[name]=json.loads(contents)

owner=raw['HDEC_R1_V1_OWNER_ONLY_72_D0_D1_RAW_GENERATIONS.json']
receipt=raw['HDEC_R1_V1_OWNER_GENERATION_NONSECRET_RECEIPT.json']
eval_doc=raw['TTM_SMALL4M_NEXT_EVAL_OWNER_PRIVATE_DEV12_FINAL24_20261112.json']
e=raw['HDEC_R1_PUBLIC_SAFE_ENCRYPTED_MAPPING.json']
k=raw['HDEC_R1_OWNER_PRIVATE_AES_KEY_DO_NOT_SHARE.json']
begin=raw['HDEC_R1_V1_ONE_SHOT_BEGIN.json']
run_id='TTM_SMALL4M_POST_FINAL24_DECODING_REPETITION_DIAGNOSTIC_V1'
require(all(x['run_id']==run_id for x in (owner,receipt,eval_doc,e,k,begin)),'ALL_RUN_IDS')
require(receipt['raw_owner_only_sha256']==expected['HDEC_R1_V1_OWNER_ONLY_72_D0_D1_RAW_GENERATIONS.json'],'RAW_RECEIPT_BOND')
require(receipt['total_generations']==72 and receipt['dev_generations']==24 and receipt['final_generations']==48,'RECEIPT_COUNTS')
require(receipt['model_forward_calls']==4040 and receipt['optimizer_updates']==0,'FROZEN_FORWARD_AND_NO_TRAIN')
require(receipt['scoring']=='NOT_STARTED' and receipt['unblind']=='NOT_EXECUTED' and receipt['blind_packet']=='NOT_CREATED','RECEIPT_PRE_BLIND')
require(owner['status']=='OWNER_GENERATED_NOT_BLIND_SCORED_NOT_UNBLINDED','OWNER_STATUS')
require(owner['escrow_public_ciphertext_sha256']==expected['HDEC_R1_PUBLIC_SAFE_ENCRYPTED_MAPPING.json'],'OWNER_ESCROW_BOND')
require(begin['status']=='BEGIN_CLAIMED_ONE_SHOT_NO_REPLAY','ONE_SHOT_BEGIN')
require(owner['checkpoint_sha256']==receipt['checkpoint_sha256']=='ae9f05c5234ac98e3f9150e3f27501d217c1942a381650bec5aef91a1f56196b','CHECKPOINT_PIN')
require(owner['owner_eval_sha256']==expected['TTM_SMALL4M_NEXT_EVAL_OWNER_PRIVATE_DEV12_FINAL24_20261112.json'],'EVAL_PIN')
require(k['public_ciphertext_sha256']==expected['HDEC_R1_PUBLIC_SAFE_ENCRYPTED_MAPPING.json'],'ESCROW_KEY_BOND')
clear=AESGCM(base64.b64decode(k['key_b64'])).decrypt(base64.b64decode(e['nonce_b64']),base64.b64decode(e['ciphertext_b64']),e['aad_utf8'].encode('utf8'))
require(sha(clear)==e['plaintext_sha256']==k['plaintext_mapping_sha256']=='603bccaf0060f8a8a577302353ea6cac831281ad17596603ffa7eb6630ce20a3','ORIGINAL_AES_GCM_SHA')
mapdoc=json.loads(clear)
require(len(mapdoc['pairs'])==24 and [p['pair_id'] for p in mapdoc['pairs']]==[f'R{i:02}' for i in range(1,25)],'MAPPING_R01_R24')
require(len(eval_doc['prompts'])==36,'EVAL_36')
all_prompts={p['id']:p for p in eval_doc['prompts']}
require(len(all_prompts)==36 and [p['id'] for p in eval_doc['prompts']]==[f'ND{i:02}' for i in range(1,13)]+[f'NF{i:02}' for i in range(1,25)],'EVAL_ID_SEQUENCE')
records=owner['records']
require(len(records)==72,'OWNER_72_RECORDS')
by_key={}
for r in records:
 kk=(r['prompt_id'],r['arm_owner_only'])
 require(kk not in by_key,'NO_DUP_RECORD_'+r['prompt_id']+'_'+r['arm_owner_only'])
 require(r['arm_owner_only'] in ('D0','D1'),'ONLY_D0_D1')
 require(r['cohort']==all_prompts[r['prompt_id']]['cohort'],'COHORT_'+r['prompt_id']+'_'+r['arm_owner_only'])
 require(r['prompt_sha256']==all_prompts[r['prompt_id']]['prompt_utf8_sha256'],'PROMPT_BOND_'+r['prompt_id']+'_'+r['arm_owner_only'])
 require(sha(r['continuation'].encode('utf8'))==r['continuation_utf8_sha256'],'CONT_SHA_'+r['prompt_id']+'_'+r['arm_owner_only'])
 require(1<=r['new_bpe_tokens']<=64,'TOKEN_COUNT_'+r['prompt_id']+'_'+r['arm_owner_only'])
 require(r['stop_reason'] in ('EOS','MAX_NEW_TOKENS'),'STOP_'+r['prompt_id']+'_'+r['arm_owner_only'])
 require((r['stop_reason']!='MAX_NEW_TOKENS' or r['new_bpe_tokens']==64) and (r['new_bpe_tokens']==64 or r['stop_reason']=='EOS'),'STOP_COUNT_'+r['prompt_id']+'_'+r['arm_owner_only'])
 by_key[kk]=r
require(len(by_key)==72 and all((pid,arm) in by_key for pid in all_prompts for arm in ('D0','D1')),'COMPLETE_72_GRID')

pairs=[]; side_counts=collections.Counter(); strata=collections.defaultdict(collections.Counter)
for p in mapdoc['pairs']:
 rid=p['pair_id'];pid=p['prompt_id'];left=p['left_arm'];right=p['right_arm'];stratum=p['stratum']
 require(rid==pid.replace('NF','R',1),'PAIR_PROMPT_ID_'+rid)
 require({left,right}=={'D0','D1'},'PAIR_SIDES_'+rid)
 require(stratum==all_prompts[pid]['stratum'],'PAIR_STRATUM_'+rid)
 prompt=all_prompts[pid]['prompt']
 require(sha(prompt.encode('utf8'))==all_prompts[pid]['prompt_utf8_sha256'],'EVAL_PROMPT_SHA_'+rid)
 lo=by_key[(pid,left)]['continuation'];ro=by_key[(pid,right)]['continuation']
 pairs.append({'pair_id':rid,'prompt':prompt,'LEFT':lo,'RIGHT':ro})
 side_counts[left]+=1;strata[stratum][left]+=1
require(side_counts=={'D0':12,'D1':12},'LEFT_BALANCE_12_12')
require(len(strata)==4 and all(v=={'D0':3,'D1':3} for v in strata.values()),'STRATUM_BALANCE_3_3')
require(len(pairs)==24 and [x['pair_id'] for x in pairs]==[f'R{i:02}' for i in range(1,25)],'PACKET_24_ORDER')
# Reviewer artifacts must contain NO owner labels or arm metadata. Validation checks on structure, not rewriting passages.
packet={
 'schema':'ttm.small4m.next24.blind_rater_packet.v1',
 'blind_review':'AI_ASSISTED_EXPLORATORY_SCOPED_REVIEW',
 'status':'GENERATED_UNSCORED_PRE_UNBLIND',
 'pair_count':24,
 'text_count':48,
 'rules':{'review_only_input_prompt_and_left_right':True,'do_not_lookup_owner_context':True,'score_int_range':[0,3], 'axes':['prompt_adherence','coherence','consistency'],'notes':24,'freezing_required_before_owner_unblind':True},
 'pairs':pairs
}
score_rows=[{'pair_id':p['pair_id'], 'left':{'prompt_adherence':None,'coherence':None,'consistency':None},'right':{'prompt_adherence':None,'coherence':None,'consistency':None},'note':None} for p in pairs]
score_template={'schema':'ttm.small4m.next24.blind_rater_scores.v1', 'status':'SCORING_NOT_STARTED', 'rater_identity':None,'rater_session_reference':None,'packet_json_sha256':None,'scores':score_rows, 'score_sha256_before_unblind':None, 'unblind':'NOT_EXECUTED'}
# score template deliberately references packet hash; compute from the exact packet bytes first.
def write(path,obj):
 b=(json.dumps(obj,ensure_ascii=False,sort_keys=True,indent=2)+'\n').encode('utf8')
 path.write_bytes(b)
 return sha(b)
packet_path=P/'TTM_NEXT24_BLIND_PACKET.json'
packet_sha=write(packet_path,packet)
score_template['packet_json_sha256']=packet_sha
score_path=P/'TTM_NEXT24_SCORE_TEMPLATE.json'
score_sha=write(score_path,score_template)

# Standalone markdown human-readable packet with exact text and no metadata.
sections=['# NEXT24 — Independent Blind Rater Packet', '', '24 pairs × 2 texts. Review only these prompts and the raw continuations, without model attribution.', '']
for row in pairs:
 sections.extend([f"## {row['pair_id']}",'', '**PROMPT**','',row['prompt'],'','**LEFT**','',row['LEFT'] or '*(empty continuation)*','','**RIGHT**','',row['RIGHT'] or '*(empty continuation)*',''])
readable_path=P/'TTM_NEXT24_BLIND_PACKET.md'
readable_path.write_text('\n'.join(sections)+'\n',encoding='utf8')
readable_sha=sha(readable_path.read_bytes())

handoff=f'''# HANDOFF — NEXT24 Independent GPT-6 Blind Rater

**Operation:** `TTM_TTM_NEXT24_INDEPENDENT_GPT6_BLIND_SCORING_144_FREEZE`

**Reviewer classification:** `EXPLORATORY_SCOPED_AI_REVIEW` (AI self-attested, not a human scientific reviewer).

**State:** `SCORING_NOT_STARTED` · `UNBLIND=NOT_EXECUTED`.

## Inputs and cryptographic pins

Only use the three bundled input artifacts:

- `TTM_NEXT24_BLIND_PACKET.json` — SHA-256 `{packet_sha}`
- `TTM_NEXT24_BLIND_PACKET.md` — SHA-256 `{readable_sha}`
- `TTM_NEXT24_SCORE_TEMPLATE.json` — SHA-256 `{score_sha}`

Check the hashes before scoring. The JSON packet is authoritative; the Markdown is a reader-friendly representation. Exactly 24 pairs `R01–R24` with one PROMPT and exact raw LEFT/RIGHT continuation in each. Do not rewrite, normalize, edit, translate or repair any continuation. Do not request any owner private materials, keys, mapping, checkpoint, GitHub research history, prior reviewer results, memory or personal context. Do not attempt source/model attribution.

This is a **separate blind-rating session**. If you have seen a LEFT/RIGHT-to-model assignment, decline due to conflict of independence. You may accept the task by scoring; pre-acceptance before model generation was deliberately not required.

## Scope and scoring rubric (strict integers 0–3)

Judge **each text individually, conditional on its prompt**, along these three axes:

- **Prompt adherence:** 0 = unrelated; 1 = very weak relation; 2 = partially follows prompt's actors/objects/goal; 3 = clearly continues the specific prompt's actors/objects/goal.
- **Coherence:** 0 = unintelligible; 1 = largely broken/repetitive; 2 = partly intelligible; 3 = a coherent continuation.
- **Consistency:** 0 = direct contradiction with prompt; 1 = major contradictions; 2 = minor inconsistencies; 3 = consistent with the prompt's established facts and sequence.

Short or unfinished texts, repetitive prose, and EOS truncation must be assessed as written; never pad the output. Do not force a LEFT/RIGHT winner. If passages are byte-identical, give identical scores on each axis. Tie scores are allowed and normal.

For each R01–R24, provide three integer scores for LEFT and three for RIGHT, plus exactly one nonempty note grounded in observable text. This is **24 × 2 × 3 = 144 scores and 24 notes**. Use the supplied JSON score template preserving `pair_id` and schema field names.

## Deliverables — frozen before any unblinding

1. `TTM_NEXT24_BLIND_SCORES_FROZEN.json` — 24 score rows, 144 integers, 24 notes, honest rater identity/session and `unblind="NOT_EXECUTED"`.
2. `TTM_NEXT24_BLIND_SCORES_FROZEN.sha256` — SHA-256 on the exact UTF-8 file bytes, printed as `<64 hex>  TTM_NEXT24_BLIND_SCORES_FROZEN.json`.
3. `TTM_NEXT24_BLIND_RATER_RECEIPT.json` — verification counts, packet SHA, the frozen score file SHA, canonical score-array SHA, rater identity, own session reference (a self-generated reference, not a claimed platform-internal chat ID), UTC timestamp, method limitations, and `UNBLIND=NOT_EXECUTED`.

For canonical score-array hash, use `json.dumps(scores, ensure_ascii=False, sort_keys=True, separators=(',', ':')).encode('utf-8')` and SHA-256. For a score file containing its array hash, compute this canonical hash *first*, then serialize the complete final JSON file, and compute SHA-256 of that file's exact bytes. Do not modify a frozen score file afterward.

Return **all three deliverable files** and the succinct receipt:

`PACKET_SHA256=PASS`
`SCORES=144_INTEGERS_0_TO_3`
`NOTES=24`
`SCORE_FILE_SHA256=<actual 64-hex>`
`RATER_STATUS=COMPLETE_FROZEN_PRE_UNBLIND`
`REVIEW_CLASS=EXPLORATORY_SCOPED_AI_REVIEW`
`UNBLIND=NOT_EXECUTED`

If any input SHA/check/score is incomplete, return `SCORING_INCOMPLETE_HOLD` instead of inventing values. Do not unblind or conclude which generator is better. The owner will audit and only then privately unblind and adjudicate. No model retraining, text generation or use of source TEST/Q1/Q2/OOD.
'''
handoff_path=P/'TTM_NEXT24_INDEPENDENT_GPT6_HANDOFF.md'
handoff_path.write_text(handoff,encoding='utf8')
handoff_sha=sha(handoff_path.read_bytes())

# Strict exclusion of private terms in metadata (not natural language output spans).
for obj in (packet,score_template):
 require(not any(key in json.dumps(obj.get('rules',{}),ensure_ascii=False) for key in ('D0','D1','arm_owner_only','key_b64','left_arm','right_arm','checkpoint_sha256')),'RATER_METADATA_NO_ARM_LABELS')
 require(not any(key in obj for key in ('mapping','owner_only','escrow','key_b64','checkpoint_sha256')),'RATER_NO_SECRET_TOP_LEVEL')

manifest={
 'schema':'ttm.small4m.next24.blind_rater_bundle_manifest.v1',
 'scope':'BLIND_RATER_ONLY_NO_OWNER_MAPPING_OR_KEYS',
 'pair_count':24,'text_count':48,
 'files':[
 {'filename':packet_path.name,'sha256':packet_sha,'size':packet_path.stat().st_size},
 {'filename':readable_path.name,'sha256':readable_sha,'size':readable_path.stat().st_size},
 {'filename':score_path.name,'sha256':score_sha,'size':score_path.stat().st_size},
 {'filename':handoff_path.name,'sha256':handoff_sha,'size':handoff_path.stat().st_size}],
 'pre_scoring':True,'unblind':'NOT_EXECUTED'
}
manifest_path=P/'TTM_NEXT24_BLIND_PACKET_MANIFEST.json'
manifest_sha=write(manifest_path,manifest)
zip_path=P/'TTM_NEXT24_CHATGPT_BLIND_RATER.zip'
with zipfile.ZipFile(zip_path,'w',compression=zipfile.ZIP_DEFLATED) as z:
 for file in (packet_path,readable_path,score_path,handoff_path,manifest_path):
  z.write(file,arcname=file.name)
require(zipfile.ZipFile(zip_path).testzip() is None,'ZIP_INTEGRITY')
with zipfile.ZipFile(zip_path) as z:
 for entry in manifest['files']:
  require(sha(z.read(entry['filename']))==entry['sha256'],'ZIP_FILE_SHA_'+entry['filename'])
 require(len(z.namelist())==5,'ZIP_FIVE_FILES')

identical_pairs=sum(p['LEFT']==p['RIGHT'] for p in pairs)
public={
 'schema':'ttm.small4m.hdec_r1.owner_generation_to_blind_packet.public_safe_receipt.v1',
 'date':'2026-11-12',
 'operation':'TTM_HDEC_R1_OWNER_ONE_SHOT_72_READBACK_AND_ORIGINAL_AES_24_PAIR_BLIND_HANDOFF_FREEZE',
 'run_id':run_id,
 'source':{
  'owner_72_raw_sha256':expected['HDEC_R1_V1_OWNER_ONLY_72_D0_D1_RAW_GENERATIONS.json'],
  'owner_generation_receipt_sha256':expected['HDEC_R1_V1_OWNER_GENERATION_NONSECRET_RECEIPT.json'],
  'owner_begin_sha256':expected['HDEC_R1_V1_ONE_SHOT_BEGIN.json'],
  'owner_eval_sha256':expected['TTM_SMALL4M_NEXT_EVAL_OWNER_PRIVATE_DEV12_FINAL24_20261112.json'],
  'original_AES_escrow_sha256':expected['HDEC_R1_PUBLIC_SAFE_ENCRYPTED_MAPPING.json'],
  'original_mapping_plaintext_sha256_HASH_ONLY':e['plaintext_sha256'],
  'checkpoint_A_sha256':owner['checkpoint_sha256'],
  'model_source_commit':owner['source_commit'],
 },
 'generation':{'total':72,'DEV':24,'FINAL':48,'frozen_pairs':24,'model_forward_calls':receipt['model_forward_calls'],'optimizer_updates':0,'score_count':0,'rater_notes':0},
 'blind_custody':{'original_AES_mapping_reused':True,'AES_GCM_digest_and_authentication_verified':True,'left_right_balanced_12_12':True,'per_stratum_3_3':True,'all_prompt_and_continuation_SHA256_match':True,'all_72_grid_entries_unique':True,'identical_text_pairs':identical_pairs,'secret_mapping_published':False,'AES_key_published':False,'owner_raw_outputs_published':False,'no_new_random_mapping':True},
 'rater_bundle':{'filename':zip_path.name,'sha256':sha(zip_path.read_bytes()),'byte_length':zip_path.stat().st_size,'files':manifest['files'],'manifest_sha256':manifest_sha},
 'qa':{'checks_passed':len(checks),'checks_failed':0,'zip_testzip_pass':True,'raw_owner_bytes_independently_hashed':True,'no_training':True,'no_new_model_forward_for_packet':True},
 'verdict':'PASS_OWNER_GENERATIONS_72_AND_BLIND_PACKET_24_PAIRS_48_TEXTS_SHA_FROZEN_RATER_READY',
 'scoring':'NOT_STARTED','unblind':'NOT_EXECUTED','science_effect':'NOT_ESTIMABLE',
 'main_lineage_unchanged':True,
 'next':'Give ONLY neutral ZIP or its neutral contents to fresh ChatGPT blind rater; freeze 144 integer scores/24 notes with hashes before owner-only AES unblind.'
}
public_path=P/'HDEC_R1_OWNER_TO_RATER_PUBLIC_SAFE_READBACK_20261112.json'
public_sha=write(public_path,public)
# owner private receipt contains no per-pair mapping (only digest), kept separate anyway.
private={
 'schema':'ttm.small4m.hdec_r1.owner_private_handoff_custody.v1',
 'source_owner_raw_sha256':expected['HDEC_R1_V1_OWNER_ONLY_72_D0_D1_RAW_GENERATIONS.json'],
 'original_AES_escrow_sha256':expected['HDEC_R1_PUBLIC_SAFE_ENCRYPTED_MAPPING.json'],
 'original_mapping_plaintext_sha256':e['plaintext_sha256'],
 'rater_bundle_sha256':sha(zip_path.read_bytes()),
 'rater_json_sha256':packet_sha,
 'owner_source_not_modified':True,
 'original_mapping_not_rekeyed':True,
 'score_file_received':False,
 'unblind_executed':False,
 'scoring_started':False
}
private_path=P/'HDEC_R1_OWNER_PRIVATE_HANDOFF_CUSTODY_20261112.json'
private_sha=write(private_path,private)
for p in (packet_path,readable_path,score_path,handoff_path,manifest_path,zip_path,public_path,private_path):
 require(p.exists() and p.stat().st_size>0,'OUTPUT_EXISTS_'+p.name)
print(json.dumps({'status':'PASS_FROZEN_PRE_UNBLIND','source_hashes_verified':len(expected),'qa_checks':len(checks),'pairs':len(pairs),'texts':2*len(pairs),'dev_source_outputs':24,'private_input_records':len(records),'left_right_escrow_balanced':True,'identical_pairs':identical_pairs,'score_count':0,'zip':str(zip_path),'zip_bytes':zip_path.stat().st_size,'zip_sha256':sha(zip_path.read_bytes()),'packet_sha256':packet_sha,'manifest_sha256':manifest_sha,'handoff_sha256':handoff_sha,'owner_report_sha256':private_sha,'public_report_sha256':public_sha,'unblind':'NOT_EXECUTED'},indent=2))
