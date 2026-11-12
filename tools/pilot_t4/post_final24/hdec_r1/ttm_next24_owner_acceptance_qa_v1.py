#!/usr/bin/env python3
"""Independent owner-side NEXT24 rater score pre-unblind validation.
No mapping/key access, no model inference, no score editing; sidecar rebuilt only from score file exact bytes.
"""
import hashlib,json,zipfile,pathlib,collections,datetime
ROOT=pathlib.Path('/mnt/data')
SC=ROOT/'TTM_NEXT24_BLIND_SCORES_FROZEN(1).json'
REC=ROOT/'TTM_NEXT24_BLIND_RATER_RECEIPT(1).json'
PACK=ROOT/'TTM_NEXT24_CHATGPT_BLIND_RATER.zip'
EXPECTED={
 'score':'6ba3420b8863c435ef1fc71d9706826221455d5254c87ea4e789b852b908a682',
 'scores_array':'891225c539ffc46522e06a711fc1e8d60038d7dfba0195ac64c5d7754289543a',
 'rater_json':'e28049bf770ddab879fdd10ac5805b9b5bf2e60fa0f8f9264ba641abab82dd22',
 'zip':'9ec48639974575e1cdebb28fcf9b2a0393a3318fb954dc9c5824e2f8bace927a',
 'packet_md':'6841c2b4e1029d5b2a4a8dc18dfec75c7fa0e7416761e9b02e44f0d502d68a14',
 'template':'c4263874e84e47ad613905531991e058e1f8481d1f3b7468153493abcbdb1b7b',
}
def sha(b):return hashlib.sha256(b).hexdigest()
checks=[]
def chk(x,name):
 if not x: raise RuntimeError('SCORE_ADMISSION_HOLD:'+name)
 checks.append(name)
b=SC.read_bytes(); rb=REC.read_bytes(); j=json.loads(b); r=json.loads(rb)
chk(len(b)==10248,'SCORE_FILE_EXACT_BYTES')
chk(sha(b)==EXPECTED['score'],'SCORE_EXACT_SHA256')
chk(r.get('score_file_bytes')==len(b) and r.get('score_file_sha256')==sha(b),'RECEIPT_SCORE_BOND')
chk(j.get('schema')=='ttm.small4m.next24.blind_rater_scores.v1','SCORE_SCHEMA')
chk(j.get('packet_json_sha256')==EXPECTED['rater_json']==r.get('packet_json_sha256'),'SCORE_PACKET_BOND')
chk(j.get('status')=='COMPLETE_FROZEN_PRE_UNBLIND'==r.get('status'),'SCORE_FROZEN_STATUS')
chk(j.get('unblind')=='NOT_EXECUTED'==r.get('UNBLIND'),'UNBLIND_DECLARATION')
chk(j.get('rater_identity')==r.get('rater_identity') and bool(j.get('rater_identity')),'RATER_ID_CONSISTENT')
chk(j.get('rater_session_reference')==r.get('rater_session_reference') and bool(j.get('rater_session_reference')),'SESSION_CONSISTENT')
chk(len(j.get('scores',[]))==24,'SCORES_24_ROWS')
chk([x['pair_id'] for x in j['scores']]==[f'R{i:02d}' for i in range(1,25)],'SCORE_IDS_IN_ORDER')
chk(len(set(x['pair_id'] for x in j['scores']))==24,'SCORE_IDS_UNIQUE')
chk(all(set(x.keys())=={'left','right','note','pair_id'} for x in j['scores']),'SCORE_FIELDS_EXACT')
chk(all(set(x[side])=={'prompt_adherence','coherence','consistency'} for x in j['scores'] for side in ('left','right')),'ALL_3_AXES')
values=[x[side][axis] for x in j['scores'] for side in ('left','right') for axis in ('prompt_adherence','coherence','consistency')]
chk(len(values)==144,'144_SCORES')
chk(all(type(n) is int and 0<=n<=3 for n in values),'SCORES_INT_NO_BOOL_0_TO_3')
chk(all(isinstance(x['note'],str) and x['note'].strip() for x in j['scores']),'24_NONEMPTY_NOTES')
canon=json.dumps(j['scores'],ensure_ascii=False,sort_keys=True,separators=(',',':')).encode('utf-8')
chk(sha(canon)==EXPECTED['scores_array']==j['score_sha256_before_unblind']==r['canonical_score_array_sha256'],'CANONICAL_SCORES_FROZEN_SHA')
chk(r['verification_counts']['integer_scores_count']==144 and r['verification_counts']['notes_count']==24 and r['verification_counts']['pair_count']==24 and r['verification_counts']['text_count']==48,'RECEIPT_COUNTS')
chk(r.get('review_class')=='EXPLORATORY_SCOPED_AI_REVIEW','AI_REVIEW_SCOPE')
chk(r.get('input_sha256_checks',{}).keys()>={'TTM_NEXT24_BLIND_PACKET.json','TTM_NEXT24_BLIND_PACKET.md','TTM_NEXT24_SCORE_TEMPLATE.json'},'RATER_INPUT_HASH_FIELDS')
with zipfile.ZipFile(PACK) as z:
 chk(z.testzip() is None,'ZIP_CRC')
 chk(sha(PACK.read_bytes())==EXPECTED['zip'],'ZIP_EXACT_SHA')
 chk(len(z.namelist())==5 and len(set(z.namelist()))==5,'ZIP_5_UNIQUE')
 hashes={'TTM_NEXT24_BLIND_PACKET.json':'rater_json','TTM_NEXT24_BLIND_PACKET.md':'packet_md','TTM_NEXT24_SCORE_TEMPLATE.json':'template'}
 for name,key in hashes.items():
  data=z.read(name)
  chk(sha(data)==EXPECTED[key],'ZIP_MEMBER_'+name+'_HASH')
  record=r['input_sha256_checks'][name]
  chk(record['expected_sha256']==record['actual_sha256']==sha(data) and record['status']=='PASS','RATER_RECEIPT_'+name+'_BOND')
 packet=json.loads(z.read('TTM_NEXT24_BLIND_PACKET.json'))
 chk(len(packet['pairs'])==24 and packet['text_count']==48,'PACKET_COUNTS')
 chk([x['pair_id'] for x in packet['pairs']]==[x['pair_id'] for x in j['scores']],'SCORE_PAIR_ORDER_PACKET_BOND')
 chk(all(set(x)=={'pair_id','prompt','LEFT','RIGHT'} for x in packet['pairs']),'PACKET_BLIND_FIELDS_ONLY')
 chk(all(isinstance(x['prompt'],str) and x['prompt'] and isinstance(x['LEFT'],str) and isinstance(x['RIGHT'],str) for x in packet['pairs']),'PACKET_TEXTS_PRESENT')
chk(r['score_file_sha256_sidecar']=='TTM_NEXT24_BLIND_SCORES_FROZEN.sha256','SIDECAR_REPORTED_NOT_UPLOADED')
side=ROOT/'TTM_NEXT24_BLIND_SCORES_FROZEN_OWNER_RECONSTRUCTED_20261112.sha256'
side.write_text(f"{sha(b)}  TTM_NEXT24_BLIND_SCORES_FROZEN.json\n",encoding='utf8')
receipt={
 'schema':'ttm.small4m.next24.owner_frozen_score_admission.v1',
 'date':'2026-11-12',
 'operation':'TTM_NEXT24_INDEPENDENT_GPT6_FROZEN_SCORE_OWNER_ACCEPTANCE_AND_POST_FREEZE_UNBLIND',
 'review_class':'EXPLORATORY_SCOPED_AI_REVIEW',
 'AI_rater_identity_self_attested':r['rater_identity'],
 'AI_rater_session_reference_self_generated':r['rater_session_reference'],
 'rater_receipt_original_sha256':sha(rb),
 'score_original_filename':SC.name,'score_original_sha256':sha(b),
 'score_original_bytes':len(b),'canonical_score_array_sha256':sha(canon),
 'blind_packet_json_sha256':EXPECTED['rater_json'],
 'blind_zip_sha256':EXPECTED['zip'],
 'checks_passed':len(checks),'checks_failed':0,'checks':checks,
 'score_count':144,'notes_count':24,'score_range':[min(values),max(values)],
 'original_sidecar_received':False,
 'reconstructed_sidecar_filename':side.name,'reconstructed_sidecar_sha256':sha(side.read_bytes()),
 'original_rater_scores_changed':False,
 'owner_unblind_allowed_after_this_check':True,
 'scores_qualitative_subjective':True,
 'rater_independence':'SELF_ATTESTED_AI_NOT_PLATFORM_OR_HUMAN_VERIFIED',
 'verdict':'PASS_OWNER_ADMITTED_AI_BLIND_SCORES_FROZEN_PRE_UNBLIND',
}
out=ROOT/'TTM_NEXT24_OWNER_SCORE_FREEZE_ACCEPTANCE_20261112.json'
out.write_text(json.dumps(receipt,ensure_ascii=False,sort_keys=True,indent=2)+'\n',encoding='utf-8')
print(json.dumps({k:receipt[k] for k in ('verdict','checks_passed','checks_failed','score_count','notes_count','score_range','score_original_sha256','canonical_score_array_sha256','rater_receipt_original_sha256','original_sidecar_received','reconstructed_sidecar_sha256')},indent=2))
