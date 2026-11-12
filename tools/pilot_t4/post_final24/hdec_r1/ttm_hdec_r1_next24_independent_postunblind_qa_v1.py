#!/usr/bin/env python3
"""Independent source-only science readback after GPT-6 NEXT24 score SHA freeze.
No training, no inference, no raw text/key/arm mapping in public output.
Implementation separate from frozen metric adapter. One AI performing independent code check, not external peer review.
"""
from __future__ import annotations
import json,hashlib,re,base64,pathlib,collections
import numpy as np
from cryptography.hazmat.primitives.ciphers.aead import AESGCM
ROOT=pathlib.Path('/mnt/data')
expected={
 'score':'6ba3420b8863c435ef1fc71d9706826221455d5254c87ea4e789b852b908a682',
 'receipt':'27b759413e4aae07d90ddd84aa7f84b6253be93547ed1cbf03e5a198f46d16cc',
 'packet':'e28049bf770ddab879fdd10ac5805b9b5bf2e60fa0f8f9264ba641abab82dd22',
 'owner':'e09572c29993af8379a57cfc26c905912525e6238510f2803af5c9a81cc2f208',
 'generation_receipt':'bdd1a513fef9de45fc66873795b6a04551ebde9b08f9b1b7a37d4d028d51735a',
 'eval':'9480ba73cbbe425fc9b61cc3253df81b32d52b0c35127d6e4392e5b5d6b0d54f',
 'escrow':'812e7e23cdc3eba4735bfb0b8ff43b2a7420fbaac4fa0edfc2fe4a944cb8c3b7',
 'key':'3e2b381fce29753621baec956b993b8c01e951925717c1730feb7aca0a548911',
}
files={'score':'TTM_NEXT24_BLIND_SCORES_FROZEN(1).json','receipt':'TTM_NEXT24_BLIND_RATER_RECEIPT(1).json',
 'packet':'TTM_NEXT24_BLIND_PACKET.json','owner':'HDEC_R1_V1_OWNER_ONLY_72_D0_D1_RAW_GENERATIONS.json',
 'generation_receipt':'HDEC_R1_V1_OWNER_GENERATION_NONSECRET_RECEIPT.json','eval':'TTM_SMALL4M_NEXT_EVAL_OWNER_PRIVATE_DEV12_FINAL24_20261112.json',
 'escrow':'HDEC_R1_PUBLIC_SAFE_ENCRYPTED_MAPPING.json','key':'HDEC_R1_OWNER_PRIVATE_AES_KEY_DO_NOT_SHARE.json'}
sha=lambda b:hashlib.sha256(b).hexdigest()
checks=[]
def check(condition,name):
 if not condition:raise RuntimeError('HDEC_NEXT24_FINAL_QA_FAIL:'+name)
 checks.append(name)
objs={}
for name,path in files.items():
 raw=(ROOT/path).read_bytes()
 check(sha(raw)==expected[name],'PIN_'+name)
 objs[name]=json.loads(raw)
check(np.__version__=='2.3.5','FROZEN_NUMPY_VER')
score=objs['score'];owner=objs['owner'];packet=objs['packet'];receipt=objs['receipt']
check(score['status']=='COMPLETE_FROZEN_PRE_UNBLIND' and score['unblind']=='NOT_EXECUTED','SCORES_FROZEN')
check(receipt['score_file_sha256']==expected['score'],'SCORE_RECEIPT_BOND')
canonical=json.dumps(score['scores'],ensure_ascii=False,sort_keys=True,separators=(',',':')).encode('utf8')
check(sha(canonical)==score['score_sha256_before_unblind']==receipt['canonical_score_array_sha256'],'SCORE_ARRAY_DIGEST')
key=objs['key'];e=objs['escrow']
plain=AESGCM(base64.b64decode(key['key_b64'])).decrypt(base64.b64decode(e['nonce_b64']),base64.b64decode(e['ciphertext_b64']),e['aad_utf8'].encode())
check(sha(plain)==key['plaintext_mapping_sha256']==e['plaintext_sha256'],'ORIGINAL_AES_AUTH')
pairs=json.loads(plain)['pairs'];check(len(pairs)==24,'MAPPING_SIZE')
raw_index={(r['prompt_id'],r['arm_owner_only']):r for r in owner['records']}
check(len(raw_index)==72,'RAW_GRID_72')
prompt_lookup={p['id']:p for p in objs['eval']['prompts']};check(len(prompt_lookup)==36,'PROMPT_GRID_36')
wordrx=re.compile(r"[A-Za-z]+(?:'[A-Za-z]+)?")
def repeat(s):
 w=wordrx.findall(s.lower())
 if len(w)<3:return 0.0
 tri=[tuple(w[i:i+3]) for i in range(len(w)-2)]
 return 1.0-len(set(tri))/len(tri)
reps0=[];reps1=[];qdiff={k:[] for k in ('prompt_adherence','coherence','consistency')}
short={a:0 for a in ('D0','D1')}; caps={a:0 for a in ('D0','D1')};eos={a:0 for a in ('D0','D1')}
seen=set();strata=collections.defaultdict(collections.Counter)
for i in range(24):
 pair=pairs[i];blind=packet['pairs'][i];points=score['scores'][i];rid=f'R{i+1:02d}'
 check(pair['pair_id']==blind['pair_id']==points['pair_id']==rid,'PAIR_'+rid)
 check(pair['prompt_id']==f'NF{i+1:02d}','PROMPT_ID_'+rid)
 check(blind['prompt']==prompt_lookup[pair['prompt_id']]['prompt'],'PROMPT_EQUAL_'+rid)
 check(hashlib.sha256(blind['prompt'].encode()).hexdigest()==prompt_lookup[pair['prompt_id']]['prompt_utf8_sha256'],'PROMPT_HASH_'+rid)
 check({pair['left_arm'],pair['right_arm']}=={'D0','D1'},'D0_D1_PAIR_'+rid)
 check(pair['prompt_id'] not in seen,'PROMPT_UNIQUE_'+rid);seen.add(pair['prompt_id'])
 arms={};scores={}
 for side,arm in (('LEFT',pair['left_arm']),('RIGHT',pair['right_arm'])):
  record=raw_index[(pair['prompt_id'],arm)];output=blind[side]
  check(output==record['continuation'],'BLIND_EQUALS_RAW_'+rid+'_'+side)
  check(sha(output.encode('utf8'))==record['continuation_utf8_sha256'],'BLIND_OUTPUT_SHA_'+rid+'_'+side)
  arms[arm]=output
  scores[arm]=points[side.lower()]
  check(all(type(x) is int and 0<=x<=3 for x in scores[arm].values()) and len(scores[arm])==3,'RUBRIC_SCORE_'+rid+'_'+side)
  check(record['new_bpe_tokens'] in range(1,65),'TOKEN_RANGE_'+rid+'_'+side)
  if record['stop_reason']=='MAX_NEW_TOKENS':caps[arm]+=1
  elif record['stop_reason']=='EOS':eos[arm]+=1
  else:raise ValueError('STOP_REASON_CHANGED')
  short[arm]+=len(wordrx.findall(output.lower()))<8
 strata[pair['stratum']][pair['left_arm']]+=1
 for k in qdiff:qdiff[k].append(scores['D1'][k]-scores['D0'][k])
 reps0.append(repeat(arms['D0']));reps1.append(repeat(arms['D1']))
check(len(strata)==4 and all(sum(c.values())==6 and c['D0']==3 and c['D1']==3 for c in strata.values()),'MAPPING_STRATA_BALANCE')
check(len(reps0)==len(reps1)==24,'24_REPETITION_PAIRS')
arr=np.asarray(reps1,dtype=float)-np.asarray(reps0,dtype=float)
bootstrap=np.random.default_rng(20261112).choice(arr,size=(20_000,24),replace=True).mean(axis=1)
ci=[float(np.quantile(bootstrap,x,method='linear')) for x in (.025,.975)]
win1=int((arr<0).sum());win0=int((arr>0).sum());ties=int((arr==0).sum())
axis_mean={k:sum(v)/24 for k,v in qdiff.items()}
gates={
'repeat_delta_at_most_minus_0_10':float(arr.mean())<=-.10,
'D1_wins_at_least_16':win1>=16,
'bootstrap_upper_below_zero':ci[1]<0,
'D1_under8_not_more_than_D0':short['D1']<=short['D0'],
'prompt_adherence_D1_minus_D0_ge_minus_0_25':axis_mean['prompt_adherence']>=-.25,
'coherence_D1_minus_D0_ge_minus_0_25':axis_mean['coherence']>=-.25,
'consistency_D1_minus_D0_ge_minus_0_25':axis_mean['consistency']>=-.25}
check(all(gates.values()),'CANDIDATE_PASS_ALL_ORIGINAL_THRESHOLDS')
old=json.loads((ROOT/'TTM_HDEC_R1_NEXT24_PUBLIC_SAFE_UNBLIND_AGGREGATE_20261112.json').read_bytes())
check(abs(float(arr.mean())-old['metric']['D1_minus_D0'])<1e-12,'FIRST_OLD_MEAN_SAME')
check(win1==old['metric']['D1_strict_wins'] and win0==old['metric']['D0_strict_wins'] and ties==old['metric']['ties'],'FIRST_WINS_SAME')
check(all(abs(a-b)<1e-12 for a,b in zip(ci,old['metric']['CI95_paired_bootstrap_descriptive'])),'FIRST_CI_SAME')
check(all(abs(axis_mean[k]-old['other_metrics']['semantic_qualitative_axes'][k]['mean_D1_minus_D0'])<1e-12 for k in qdiff),'FIRST_QUALITY_SAME')
check(short=={'D0':0,'D1':0} and caps=={'D0':16,'D1':16} and eos=={'D0':8,'D1':8},'STOP_AND_SHORT_COUNTS')
result={
 'schema':'ttm.small4m.hdec_r1.next24.independent_implementation_scientific_QA.v1','date':'2026-11-12',
 'operation':'TTM_NEXT24_POST_FROZEN_SCORES_INDEPENDENT_IMPLEMENTATION_QA_AND_CANDIDATE_ADJUDICATION',
 'review_class':'EXPLORATORY_SCOPED_AI_REVIEW','QA_class':'INDEPENDENT_IMPLEMENTATION_READBACK_NOT_EXTERNAL_PEER_REVIEW',
 'rater_self_attested_AI':True,
 'source_sha256':{k:v for k,v in expected.items() if k!='key'},
 'private_key_sha256_ONLY':expected['key'],
 'mapping_plaintext_sha256_ONLY':sha(plain),
 'SCORE_FROZEN_SHA':expected['score'],'SCORES_COUNT':144,'NOTES_COUNT':24,
 'checker_checks_passed':len(checks),'checker_checks_failed':0,
 'independent_metric':{'D0_mean':float(np.mean(reps0)),'D1_mean':float(np.mean(reps1)),
    'delta':float(arr.mean()),'D1_wins':win1,'D0_wins':win0,'ties':ties,
    'CI95_bootstrap_paired_descriptive':ci},
 'guardrail_mean_D1_minus_D0':axis_mean,'under8_words':short,'stop_counts':{'EOS':eos,'CAP64':caps},
 'fixed_candidate_gates':gates,'pass_all_gates':all(gates.values()),
 'tech_candidate_verdict':'H_DEC_R1_EXPLORATORY_CANDIDATE_PASS',
 'semantic_quality_verdict':'PROMPT_ADHERENCE_REMAINS_NEAR_ZERO_NO_SEMANTIC_IMPROVEMENT_DEMONSTRATED',
 'scientific_interpretation':'Reduces word trigram repetition on 24 prompts with exact decoder settings; limited to one checkpoint, one one-shot generation, self-attested AI rater; not confirmatory improvement or equivalence.',
 'private_unblind_report_sha256':sha((ROOT/'TTM_HDEC_R1_NEXT24_OWNER_PRIVATE_POSTFREEZE_UNBLIND_20261112.json').read_bytes()),
 'public_safe_aggregate_sha256':sha((ROOT/'TTM_HDEC_R1_NEXT24_PUBLIC_SAFE_UNBLIND_AGGREGATE_20261112.json').read_bytes()),
 'AES_secret_in_report':False,'per_pair_mapping_in_report':False,'original_scorer_modified':False,
 'main_or_lineage_changed_during_QA':False,
 'verdict':'PASS_SCOPED_INDEPENDENT_IMPLEMENTATION_QA__TECHNICAL_CANDIDATE_PASS_SEMANTIC_BENEFIT_NOT_SHOWN',
}
out=ROOT/'TTM_HDEC_R1_NEXT24_INDEPENDENT_POSTUNBLIND_QA_20261112.json'
out.write_text(json.dumps(result,ensure_ascii=False,sort_keys=True,indent=2)+'\n',encoding='utf8')
print(json.dumps({'qa_count':len(checks),'delta':float(arr.mean()),'CI95':ci,'wins':[win1,win0,ties],'axis_deltas':axis_mean,'gates':gates,'sha256':sha(out.read_bytes())},ensure_ascii=False,indent=2))
