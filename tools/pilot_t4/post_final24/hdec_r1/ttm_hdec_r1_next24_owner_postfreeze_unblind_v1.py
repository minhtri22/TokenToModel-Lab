#!/usr/bin/env python3
"""Read-only owner unblind, exact previously committed AES escrow + frozen metric.
Owner-only per-pair mapped data never published to GitHub. No model inference.
"""
import pathlib,hashlib,json,base64,importlib.util,collections,sys,datetime
import numpy as np
from cryptography.hazmat.primitives.ciphers.aead import AESGCM
P=pathlib.Path('/mnt/data');sh=lambda b:hashlib.sha256(b).hexdigest()
checks=[]
def require(b,n):
 if not b:raise RuntimeError('HDEC_POSTFREEZE_QA_HOLD:'+n)
 checks.append(n)
expected={
 'scores':('TTM_NEXT24_BLIND_SCORES_FROZEN(1).json','6ba3420b8863c435ef1fc71d9706826221455d5254c87ea4e789b852b908a682'),
 'receipt':('TTM_NEXT24_BLIND_RATER_RECEIPT(1).json','27b759413e4aae07d90ddd84aa7f84b6253be93547ed1cbf03e5a198f46d16cc'),
 'packet':('TTM_NEXT24_BLIND_PACKET.json','e28049bf770ddab879fdd10ac5805b9b5bf2e60fa0f8f9264ba641abab82dd22'),
 'raw':('HDEC_R1_V1_OWNER_ONLY_72_D0_D1_RAW_GENERATIONS.json','e09572c29993af8379a57cfc26c905912525e6238510f2803af5c9a81cc2f208'),
 'generation_receipt':('HDEC_R1_V1_OWNER_GENERATION_NONSECRET_RECEIPT.json','bdd1a513fef9de45fc66873795b6a04551ebde9b08f9b1b7a37d4d028d51735a'),
 'eval':('TTM_SMALL4M_NEXT_EVAL_OWNER_PRIVATE_DEV12_FINAL24_20261112.json','9480ba73cbbe425fc9b61cc3253df81b32d52b0c35127d6e4392e5b5d6b0d54f'),
 'escrow':('HDEC_R1_PUBLIC_SAFE_ENCRYPTED_MAPPING.json','812e7e23cdc3eba4735bfb0b8ff43b2a7420fbaac4fa0edfc2fe4a944cb8c3b7'),
 'key':('HDEC_R1_OWNER_PRIVATE_AES_KEY_DO_NOT_SHARE.json','3e2b381fce29753621baec956b993b8c01e951925717c1730feb7aca0a548911'),
 'frozen_metrics':('ttm_hdec_r1_frozen_metrics_v1.py','1c5cecf97cc86da1d833c9c4959d4532c989d5c0e604a1490e88c684870828f1'),
}
data={}
for k,(fn,hash_) in expected.items():
 b=(P/fn).read_bytes();require(sh(b)==hash_,'SOURCE_SHA_'+k)
 data[k]=b if k=='frozen_metrics' else json.loads(b)
s=data['scores'];r=data['receipt']
require(s['status']=='COMPLETE_FROZEN_PRE_UNBLIND' and s['unblind']=='NOT_EXECUTED','FROZEN_BEFORE_UNBLIND')
require(s['score_sha256_before_unblind']=='891225c539ffc46522e06a711fc1e8d60038d7dfba0195ac64c5d7754289543a','FROZEN_SCORE_ARRAY_SHA')
require(r['score_file_sha256']==expected['scores'][1],'RATER_RECEIPT_SCORE_BOND')
require(data['generation_receipt']['raw_owner_only_sha256']==expected['raw'][1],'OWNER_GENERATIONS_RECEIPT_SHA')
raw=data['raw'];eval_doc=data['eval'];esc=data['escrow'];key=data['key']
require(key['public_ciphertext_sha256']==expected['escrow'][1],'KEY_ORIGINAL_ESCROW_SHA')
clear=AESGCM(base64.b64decode(key['key_b64'])).decrypt(base64.b64decode(esc['nonce_b64']),base64.b64decode(esc['ciphertext_b64']),esc['aad_utf8'].encode('utf-8'))
require(sh(clear)==esc['plaintext_sha256']==key['plaintext_mapping_sha256']=='603bccaf0060f8a8a577302353ea6cac831281ad17596603ffa7eb6630ce20a3','AES_ORIGINAL_MAPPING_GCM_PLAINTEXT_SHA')
mapping=json.loads(clear)['pairs'];require(len(mapping)==24,'ORIGINAL_MAPPING_24')
require([p['pair_id'] for p in mapping]==[f'R{i:02d}' for i in range(1,25)],'MAPPING_ORDER')
require(len(s['scores'])==24,'24_SCORES')
require(len(data['packet']['pairs'])==24,'24_PACKET_PAIRS')
idx={(v['prompt_id'],v['arm_owner_only']):v for v in raw['records']}
require(len(idx)==72 and len(raw['records'])==72,'72_UNIQUE_GENERATIONS')
prompts={x['id']:x for x in eval_doc['prompts']}
require(len(prompts)==36,'36_PROMPTS')
require(np.__version__=='2.3.5','NUMPY_FROZEN_2_3_5')
sp=importlib.util.spec_from_file_location('ttm_hdec_locked_scoring',P/expected['frozen_metrics'][0]); metric=importlib.util.module_from_spec(sp);sys.modules[sp.name]=metric;sp.loader.exec_module(metric)
require(metric.BOOTSTRAP_SEED==20261112 and metric.BOOTSTRAP_RESAMPLES==20_000,'BOOTSTRAP_FROZEN')
rows=[];score_rows=[];stratum=collections.defaultdict(lambda:collections.Counter());audit=[]
for m,sc,pair in zip(mapping,s['scores'],data['packet']['pairs']):
 rid=m['pair_id'];pid=m['prompt_id'];require(rid==sc['pair_id']==pair['pair_id'],'PAIR_ID_'+rid)
 require(pid in prompts and pair['prompt']==prompts[pid]['prompt'],'PROMPT_VALUE_'+rid)
 require(sh(pair['prompt'].encode('utf8'))==prompts[pid]['prompt_utf8_sha256'],'PROMPT_SHA_'+rid)
 require({m['left_arm'],m['right_arm']}=={'D0','D1'},'ARMS_DISTINCT_'+rid)
 pair_arms={};scores_arms={}
 for side,arm in [('LEFT',m['left_arm']),('RIGHT',m['right_arm'])]:
  owner=idx[(pid,arm)];text=owner['continuation']
  require(text==pair[side],'TEXT_EQUALS_BLIND_PACKET_'+rid+'_'+side)
  require(sh(text.encode('utf8'))==owner['continuation_utf8_sha256'],'TEXT_HASH_'+rid+'_'+side)
  pair_arms[arm]=text
  values=sc[side.lower()]
  require(set(values)=={'coherence','consistency','prompt_adherence'},'AXES_'+rid+'_'+side)
  require(all(type(v) is int and 0<=v<=3 for v in values.values()),'SCORE_INT_'+rid+'_'+side)
  scores_arms[arm]=values
 require(isinstance(sc['note'],str) and sc['note'].strip(),'NOTE_'+rid)
 for side in ('left_arm','right_arm'):stratum[m['stratum']][m[side]]+=1
 rows.append({'pair_id':rid,**pair_arms})
 score_rows.append(scores_arms)
 audit.append({'pair_id':rid,'prompt_id':pid,'stratum':m['stratum'],
               'D0':{'output_sha256':idx[(pid,'D0')]['continuation_utf8_sha256'],
                     'scores':scores_arms['D0'],
                     'repeat_fraction':metric.repeat_fraction(pair_arms['D0']),
                     'tokens_bpe':idx[(pid,'D0')]['new_bpe_tokens'],
                     'stop_reason':idx[(pid,'D0')]['stop_reason']},
               'D1':{'output_sha256':idx[(pid,'D1')]['continuation_utf8_sha256'],
                     'scores':scores_arms['D1'],
                     'repeat_fraction':metric.repeat_fraction(pair_arms['D1']),
                     'tokens_bpe':idx[(pid,'D1')]['new_bpe_tokens'],
                     'stop_reason':idx[(pid,'D1')]['stop_reason']}})
require(len(stratum)==4 and all(x['D0']==6 and x['D1']==6 for x in stratum.values()),'STRATUM_ARMS_6_EACH')
require(sum(m['left_arm']=='D0' for m in mapping)==12 and sum(m['left_arm']=='D1' for m in mapping)==12,'MAPPING_LEFT_12_12')
result=metric.candidate_gate(rows,score_rows)
# Independent numerical cross-check against frozen implementation for deterministic metrics
rr0=[metric.repeat_fraction(row['D0']) for row in rows]
rr1=[metric.repeat_fraction(row['D1']) for row in rows]
diff=np.asarray(rr1)-np.asarray(rr0)
require(abs(np.mean(diff)-result['mean_repeat_delta'])<1e-12,'MEAN_DELTA_CHECK')
require(int(np.sum(diff<0))==result['wins_D1'] and int(np.sum(diff>0))==result['wins_D0'] and int(np.sum(diff==0))==result['ties'],'WIN_COUNTS_CHECK')
require(result['wins_D1']+result['wins_D0']+result['ties']==24,'WIN_SUM_24')
require(all(len(row[side])>0 for row in rows for side in ('D0','D1')),'NO_EMPTY_FINAL_TEXT')
# report token ceilings and EOS without mapping or raw strings
stats={}
for arm in ('D0','D1'):
 records=[idx[(f'NF{i:02d}',arm)] for i in range(1,25)]
 require(len(records)==24,'ARM_24_RECORDS_'+arm)
 stats[arm]={
  'mean_repetition_fraction':float(np.mean(rr0 if arm=='D0' else rr1)),
  'median_repetition_fraction':float(np.median(rr0 if arm=='D0' else rr1)),
  'eos_stops':sum(x['stop_reason']=='EOS' for x in records),
  'max_64_stops':sum(x['stop_reason']=='MAX_NEW_TOKENS' for x in records),
  'mean_new_bpe_tokens':sum(x['new_bpe_tokens'] for x in records)/24,
  'mean_word_count':sum(len(metric.words(idx[(f'NF{i:02d}',arm)]['continuation'])) for i in range(1,25))/24,
  'mean_axis':{axis:sum(x[arm][axis] for x in score_rows)/24 for axis in ('prompt_adherence','coherence','consistency')},
 }
# Score pair win/tie counts for descriptive reading; not posthoc candidate metric
axis_counts={}
for axis in ('prompt_adherence','coherence','consistency'):
 d=[x['D1'][axis]-x['D0'][axis] for x in score_rows]
 axis_counts[axis]={'mean_D1_minus_D0':sum(d)/24,'D1_win':sum(z>0 for z in d),'D0_win':sum(z<0 for z in d),'ties':sum(z==0 for z in d)}
private={'schema':'ttm.small4m.hdec_r1.next24.owner_private_postfreeze_unblind.v1','date':'2026-11-12','source_score_sha256':expected['scores'][1],
'original_AES_mapping_digest_only':sh(clear),'score_frozen_before_unblind':True,'scores_modified':False,
'run_id':data['generation_receipt']['run_id'],'mapped_pair_receipts_owner_only':audit,
'candidate_gate_result':result,'axis_descriptive':axis_counts,'stats_by_arm':stats,
'raw_AES_key_in_report':False,'actual_mapping_left_right_in_report':False,
'AI_rater_not_human_and_self_attested':True,'one_shot_generation_count':72,
'verdict':'PASS_UNBLIND_ORIGINAL_24_MAPPING_OWNER_PRIVATE__SCOPED_EXPLORATORY_ONLY'}
private_path=P/'TTM_HDEC_R1_NEXT24_OWNER_PRIVATE_POSTFREEZE_UNBLIND_20261112.json'
private_path.write_text(json.dumps(private,ensure_ascii=False,sort_keys=True,indent=2)+'\n',encoding='utf8')
public={'schema':'ttm.small4m.hdec_r1.next24.public_safe_unblind_aggregate.v1','date':'2026-11-12',
'run_id':data['generation_receipt']['run_id'],
'rater_review_classification':'EXPLORATORY_SCOPED_AI_REVIEW',
'AI_rater_independence':'SELF_ATTESTED_NOT_HUMAN_AND_NOT_PLATFORM_INDEPENDENTLY_VERIFIED',
'new_inference':'COMPLETED_72_ONCE_NO_RETRAIN',
'scores':{'sha256':expected['scores'][1],'canonical_scores_array_sha256':s['score_sha256_before_unblind'],'count':144,'notes':24,'original_sidecar_received':False},
'original_blind_packet_sha256':expected['packet'][1],
'original_generation_sha256':expected['raw'][1],
'original_escrow_sha256':expected['escrow'][1],
'original_mapping_plaintext_sha256_DIGEST_ONLY':sh(clear),
'frozen_metric_source_sha256':expected['frozen_metrics'][1],
'endpoint':'paired_mean_word_trigram_repeat_fraction_D1_minus_D0_on_NEW_FINAL24',
'metric':{'D0_mean':stats['D0']['mean_repetition_fraction'],'D1_mean':stats['D1']['mean_repetition_fraction'],'D1_minus_D0':result['mean_repeat_delta'],
'D1_strict_wins':result['wins_D1'],'D0_strict_wins':result['wins_D0'],'ties':result['ties'],'CI95_paired_bootstrap_descriptive':result['CI95_descriptive']},
'other_metrics':{'D0':stats['D0'],'D1':stats['D1'],'semantic_qualitative_axes':axis_counts},
'preregistered_candidate_thresholds':{'repetition_delta_le_minus_0_10':True,'D1_wins_ge_16_of_24':True,'bootstrap_CI_upper_lt_zero':True,'semantic_axis_no_drop_below_minus_0_25':True,'D1_under8words_not_more_than_D0':True},
'preregistered_gates':result['gates'],'candidate_pass':result['candidate_pass'],
'candidate_verdict':'H_DEC_R1_EXPLORATORY_CANDIDATE_PASS' if result['candidate_pass'] else 'H_DEC_R1_NO_DEMONSTRATED_SCOPED_BENEFIT',
'method_limitations':['One checkpoint/one generation run/24 new prompts/one AI-assisted blind rater','Not a human or institutionally independent scientific peer review','Bootstrap CI descriptive and not a confirmatory multi-seed estimate','Effects not proof of semantic prompt following or generalization'],
'AES_key_published':False,'per_pair_D0_D1_mapping_published':False,'TEST_Q1_Q2_OOD_accessed':False,'main_lineage_mutated':False,
'independent_science_QA_and_final_adjudication':'PENDING'}
public_path=P/'TTM_HDEC_R1_NEXT24_PUBLIC_SAFE_UNBLIND_AGGREGATE_20261112.json'
public_path.write_text(json.dumps(public,ensure_ascii=False,sort_keys=True,indent=2)+'\n',encoding='utf8')
print(json.dumps({'checks':len(checks),'metric':public['metric'],'prereg_gates':result['gates'],'candidate_verdict':public['candidate_verdict'],'axis':axis_counts,'D0':stats['D0'],'D1':stats['D1'],'private_report_SHA256':sh(private_path.read_bytes()),'public_report_SHA256':sh(public_path.read_bytes())},indent=2,ensure_ascii=False))
