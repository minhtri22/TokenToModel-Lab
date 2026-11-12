#!/usr/bin/env python3
"""Independent-implementation readback of TTM Small4M A/C FINAL24 frozen scores.

Reads immutable sources and owner-only AES escrow; publishes ONLY aggregate metrics.
Never writes secret, plaintext mapping, per-pair labels, original texts or scores.
This is a separate checking *implementation*, not independent human/organization review.
"""
import argparse
import base64
import collections
import hashlib
import json
from pathlib import Path
import zipfile

import numpy as np
from cryptography.hazmat.primitives.ciphers.aead import AESGCM

PIN = {
    'blind_zip': '577f58ef101645febee25e959497d9d883400565ec65d4b8902516d8059daf00',
    'blind_json': 'b325567addf4a4498c7384309281c53525e8548fc18fa35221140bbdd0901be9',
    'raw_48': '9d158c9e8a7d590ebc9315d716e3b072f5bf94e06cf5061d63ab15e014c36570',
    'frozen_scores': '386d455bc3768c81b0728f4b3903ecd7e73fed6d8adabf8eaf934316bd8a91be',
    'score_array': 'f4cd13c915d2a423e21fcd74ea3fa2127ada45023292d84782614a54624f3369',
    'rater_receipt': 'a0ae78a805f102a4086f7e36a81f85d95e28716589cca0192ca501a1df7a4935',
    'public_escrow': '519f3185d6202052ce1e5c98a7e7fa58a813d87ce9d9e2d173eb25f6a05f9f1c',
    'mapping_plaintext': '68d4e303efd2c5809bf0e89f5564f70e1114349b463b5458174c1407e8deda1d',
    'key_file': 'c216ec0e9b815eb231e58c80cbb2d5ccc956cf4c66d481c7b3aa4488e19a897e',
    'owner_private_analysis': '10d1c71d46d7aa70b24ee66c304b3258b63ed0af6f73ba8be994a08da064c523',
    'owner_public_aggregate': '9c3e47121ef70b20d6483968bdef35015d09e2c98aaf8b47e4436937906879a9',
    'owner_report': 'b045877c04b299d9c8cb71404e2ae40c23d303ac7cb6e729bfade489e4ad30bd',
}
FILES = {
    'blind_zip':'TTM_SMALL4M_AC_FINAL24_RATER_HANDOFF_20261112.zip',
    'blind_json':'TTM_SMALL4M_AC_FINAL24_BLIND_RATER_PACKET_20261112.json',
    'raw_48':'OWNER_ONLY_AC_FINAL24_48_RAW_GENERATIONS.json',
    'frozen_scores':'TTM_SMALL4M_AC_FINAL24_BLIND_SCORES_FROZEN.json',
    'rater_receipt':'TTM_SMALL4M_AC_FINAL24_RATER_RECEIPT.json',
    'public_escrow':'TTM_SMALL4M_AC_BLIND24_ENCRYPTED_ESCROW_PUBLIC_20261111.json',
    'owner_private_analysis':'TTM_AC_FINAL24_OWNER_PRIVATE_UNBLIND_20261112.json',
    'owner_public_aggregate':'TTM_AC_FINAL24_OWNER_UNBLIND_PUBLIC_SAFE_AGGREGATE_20261112.json',
}
METRICS = ('prompt_adherence','coherence','consistency')
PREREG = {
    'primary':'mean_over_24_prompt_pairs(score_C_adherence-score_A_adherence)',
    'candidate_min_delta': 0.5,
    'candidate_min_strict_wins_C': 16,
    'paired_prompt_bootstrap_CI95_lower_gt_zero': True,
    'guardrail_max_val_nll_relative_regression': .05,
    'guardrail_max_coherence_mean_drop': .25,
    'guardrail_max_consistency_mean_drop': .25,
}

def sha(b):
    return hashlib.sha256(b).hexdigest()

def require(condition, label):
    if not condition:
        raise AssertionError('INDEPENDENT_QA_HOLD:'+label)

def load_json(data, name, expected_hash=None):
    p=data / name
    b=p.read_bytes()
    if expected_hash: require(sha(b)==expected_hash, 'hash:'+name)
    return json.loads(b)

def main():
    ap=argparse.ArgumentParser()
    ap.add_argument('--input-root',type=Path,required=True)
    ap.add_argument('--owner-key',type=Path,required=True)
    ap.add_argument('--output',type=Path,required=True)
    args=ap.parse_args()
    inp=args.input_root
    checks=[]
    def test(name,ok):
        require(ok,name);checks.append(name)
    for role,filename in FILES.items():
        test('source_exact_sha256_'+role,sha((inp/filename).read_bytes())==PIN[role])
    test('source_exact_sha256_key_file',sha(args.owner_key.read_bytes())==PIN['key_file'])
    with zipfile.ZipFile(inp/FILES['blind_zip']) as z:
        test('zip_internal_crc',z.testzip() is None)
        test('zip_exact_members',sorted(z.namelist())==sorted([
            'TTM_SMALL4M_AC_FINAL24_BLIND_RATER_PACKET_20261112.json',
            'TTM_SMALL4M_AC_FINAL24_BLIND_RATER_PACKET_20261112.md',
            'TTM_SMALL4M_AC_FINAL24_BLIND_SCORE_TEMPLATE_20261112.json',
        ]))
        test('zip_json_equals_frozen_packet',z.read('TTM_SMALL4M_AC_FINAL24_BLIND_RATER_PACKET_20261112.json')==(inp/FILES['blind_json']).read_bytes())
    blind=load_json(inp,FILES['blind_json'])
    frozen=load_json(inp,FILES['frozen_scores'])
    receipt=load_json(inp,FILES['rater_receipt'])
    raw=load_json(inp,FILES['raw_48'])
    prior_private=load_json(inp,FILES['owner_private_analysis'])
    prior_public=load_json(inp,FILES['owner_public_aggregate'])
    test('frozen_packet_ids_24',len(blind['pairs'])==24 and [x['pair_id'] for x in blind['pairs']]==[f'R{k:02d}' for k in range(1,25)])
    test('frozen_raw_48_unique',len(raw['outputs'])==48 and len({(x['prompt_id'],x['arm']) for x in raw['outputs']})==48)
    test('score_rubric_144_and_24_notes',len(frozen['scores'])==24 and all(x['pair_id']==f'R{i:02d}' and isinstance(x['note'],str) and x['note'].strip() and all(type(x[side][metric]) is int and 0<=x[side][metric]<=3 for side in ('left','right') for metric in METRICS) for i,x in enumerate(frozen['scores'],1)))
    canonical=json.dumps(frozen['scores'],sort_keys=True,ensure_ascii=False,separators=(',',':')).encode('utf-8')
    test('canonical_pre_unblind_score_sha256',sha(canonical)==PIN['score_array']==frozen['score_sha256_before_unblind']==receipt['score_sha256_before_unblind'])
    test('reviewer_receipt_binding',receipt['score_file_sha256']==PIN['frozen_scores'] and receipt['source_packet_json_sha256']==frozen['packet_sha256']==PIN['blind_json'] and receipt['source_zip_sha256']==PIN['blind_zip'] and receipt['score_count']==144 and receipt['notes_count']==24)
    test('reviewer_pre_unblind_and_scoped',receipt['unblind']=='NOT_EXECUTED' and not receipt['reviewer_mapping_seen'] and not receipt['reviewer_is_human'] and frozen['status']=='SCORING_COMPLETE_FROZEN_PRE_UNBLIND')
    escrow=load_json(inp,FILES['public_escrow'])
    key=load_json(args.owner_key.parent,args.owner_key.name)
    test('escrow_pin_metadata',escrow['plaintext_sha256']==PIN['mapping_plaintext'] and key['ciphertext_sha256']==PIN['public_escrow'] and key['plaintext_sha256']==PIN['mapping_plaintext'] and escrow['cipher']=='AES-256-GCM')
    plaintext=AESGCM(base64.b64decode(key['key_b64'])).decrypt(base64.b64decode(escrow['nonce_b64']),base64.b64decode(escrow['ciphertext_b64']),escrow['aad_utf8'].encode('utf-8'))
    test('original_AES_GCM_decrypt_and_plaintext_pin',sha(plaintext)==PIN['mapping_plaintext'])
    original=json.loads(plaintext)
    require(len(original['pairs'])==24, 'original_mapping_pair_count')
    lefts=collections.Counter(x['left_arm'] for x in original['pairs'])
    test('original_balanced_left_12_12',lefts=={'A':12,'C':12})
    mapby={x['pair_id']:x for x in original['pairs']}
    test('mapping_pair_ids_exact',len(mapby)==24 and set(mapby)=={f'R{i:02d}' for i in range(1,25)})
    byraw={(x['prompt_id'],x['arm']):x for x in raw['outputs']}
    byblind={x['pair_id']:x for x in blind['pairs']}
    byscore={x['pair_id']:x for x in frozen['scores']}
    deltas={k:[] for k in METRICS}; byarm={k:{'A':[],'C':[]} for k in METRICS}
    records=[]
    for pair_id in sorted(mapby):
        mapitem=mapby[pair_id]
        prompt=mapitem['prompt_id']
        bl=byblind[pair_id]
        score=byscore[pair_id]
        test('pair_'+pair_id+'_id_mapping',prompt==f'Q{int(pair_id[1:]):02d}' and {mapitem['left_arm'],mapitem['right_arm']}=={'A','C'})
        for side in ('left','right'):
            arm=mapitem[side+'_arm']; body=bl[side+'_continuation']; expected=byraw[(prompt,arm)]
            test('pair_'+pair_id+'_'+side+'_raw_binding',body==expected['output'] and sha(body.encode('utf-8'))==expected['output_utf8_sha256'])
        origident=bl['left_continuation']==bl['right_continuation']
        if origident: test('pair_'+pair_id+'_identical_content_equal_scores',score['left']==score['right'])
        arms={mapitem['left_arm']:score['left'],mapitem['right_arm']:score['right']}
        records.append((pair_id,prompt,arms['A'],arms['C'],origident))
        for metric in METRICS:
            a=arms['A'][metric];c=arms['C'][metric]
            byarm[metric]['A'].append(a);byarm[metric]['C'].append(c)
            deltas[metric].append(c-a)
    test('exact_48_texts_bound_original_order',len(records)==24)
    test('prior_private_perpair_agreement',all(
        p['pair_id']==pair_id and p['prompt_id']==prompt and p['A']==scoreA and p['C']==scoreC and p['raw_text_identical']==identical and
        all(p['delta_C_minus_A'][k]==scoreC[k]-scoreA[k] for k in METRICS)
        for p,(pair_id,prompt,scoreA,scoreC,identical) in zip(prior_private['records_owner_private'],records)
    ))
    val_A=3.511285912623514;val_C=3.512388891872789
    val_regression=(val_C-val_A)/val_A
    test('val_nll_agrees_original_owner_readback',prior_public['VAL_NLL']['A']==val_A and prior_public['VAL_NLL']['C']==val_C)
    metrics={}
    for metric in METRICS:
        arr=np.asarray(deltas[metric],dtype=np.int64)
        rng=np.random.default_rng(20261112)
        sims=np.mean(rng.choice(arr,size=(50_000,len(arr)),replace=True),axis=1)
        desc_ci=[float(np.quantile(sims,.025)),float(np.quantile(sims,.975))]
        stats={'A_mean':float(np.mean(byarm[metric]['A'])),'C_mean':float(np.mean(byarm[metric]['C'])),
               'C_minus_A_mean':float(np.mean(arr)),'wins_C':int(sum(v>0 for v in arr)),
               'wins_A':int(sum(v<0 for v in arr)),'ties':int(sum(v==0 for v in arr)),
               'bootstrap_95_descriptive_not_confirmatory':desc_ci}
        prior=prior_public['aggregate_metrics'][metric]
        test('prior_aggregate_'+metric+'_exact',stats['A_mean']==prior['A_mean'] and stats['C_mean']==prior['C_mean'] and stats['C_minus_A_mean']==prior['delta_C_minus_A_mean'] and stats['wins_C']==prior['C_strict_wins'] and stats['wins_A']==prior['A_strict_wins'] and stats['ties']==prior['ties'] and desc_ci==prior['bootstrap_95_percentile_exploratory'])
        metrics[metric]=stats
    p=metrics['prompt_adherence']
    checks_pre={
      'mean_adherence_delta_ge_0_5':p['C_minus_A_mean']>=PREREG['candidate_min_delta'],
      'C_strict_adherence_wins_ge_16':p['wins_C']>=PREREG['candidate_min_strict_wins_C'],
      'bootstrap95_lower_gt_0_descriptive_only':p['bootstrap_95_descriptive_not_confirmatory'][0]>0,
      'VAL_NLL_relative_regression_le_5pct':val_regression<=PREREG['guardrail_max_val_nll_relative_regression'],
      'coherence_mean_drop_le_0_25':metrics['coherence']['C_minus_A_mean']>=-PREREG['guardrail_max_coherence_mean_drop'],
      'consistency_mean_drop_le_0_25':metrics['consistency']['C_minus_A_mean']>=-PREREG['guardrail_max_consistency_mean_drop']
    }
    test('original_pre_reg_candidate_fail_consistent',not all(checks_pre.values()) and prior_public['preregistered_candidate_gate']['candidate_status']=='NO_PASS_SCOPED_CANDIDATE_GATE')
    test('expected_signed_delta_zero',p['C_minus_A_mean']==0 and p['wins_C']==1 and p['wins_A']==1 and p['ties']==22)
    test('original_prereg_thresholds_not_posthoc_changed',PREREG['candidate_min_delta']==.5 and PREREG['candidate_min_strict_wins_C']==16 and PREREG['paired_prompt_bootstrap_CI95_lower_gt_zero'])
    report={
      'schema':'ttm.small4m.ac.final24.independent_implementation.postunblind_qa.v1',
      'operation':'TTM_AC_FINAL24_INDEPENDENT_POST_UNBLIND_SCIENCE_QA_AND_FINAL_ADJUDICATION',
      'date':'2026-11-12',
      'verdict':'PASS_INDEPENDENT_RECOMPUTATION_SCOPED',
      'independence_scope':'Separate readback code path; assistant previously involved in owner workflow; NOT a second independent person or organization',
      'input_hash_pins':{k:v for k,v in PIN.items() if k!='key_file'},
      'encrypted_mapping_verified':True,
      'original_12_12_left_balance_verified':True,
      'owner_key_bytes_and_private_per_pair_labels_published':False,
      'frozen_source_and_rater_score_not_modified':True,
      'checks_count':len(checks), 'all_checks_pass':True,
      'checks':checks,
      'rater_scores_count':144,'rater_notes_count':24, 'pairs_count':24,'raw_generation_count':48,
      'identical_text_pairs':sum(x[-1] for x in records),
      'prereg_source_path':'docs/research/TTM_SMALL4M_AC_FINAL24_BLIND_EVAL_AND_RIGHTS_PREEXEC_FREEZE_20261111.json',
      'prereg_source_git_blob':'ce7e3ff7297157f1f852eadd2da72e97f91ec7ff',
      'frozen_primary':PREREG['primary'],'frozen_candidate_thresholds':PREREG,
      'metric_results':metrics,'val_nll':{'A':val_A,'C':val_C,'C_relative_regression':val_regression},
      'threshold_tests':checks_pre,
      'candidate_gate_result':'FAIL_CANDIDATE_EFFICACY_GATE_NO_DEMONSTRATED_C_GAIN',
      'scientific_result':'NO_DEMONSTRATED_SCOPED_PROMPT_ADHERENCE_GAIN; not equivalence proof',
      'bootstrap_note':'50,000 resamples with seed=20261112 checked for computational agreement, but algorithm/seed/count not fully pre-registered; CI is descriptive only',
      'scope_limitations':['single training run','GPT-6 AI self-attested blindness not human independence','no secondary rater','no external generalization','TEST/Q1/Q2/OOD not accessed by this checker'],
      'training_executed_by_this_checker':False,'score_changes':False,'lineage_changed_by_this_checker':False
    }
    args.output.parent.mkdir(parents=True,exist_ok=True)
    args.output.write_bytes((json.dumps(report,indent=2,ensure_ascii=False,sort_keys=True)+'\n').encode('utf-8'))
    print(json.dumps({'QA':report['verdict'],'checks':len(checks),'C_minus_A':p['C_minus_A_mean'],'C_wins':p['wins_C'],'A_wins':p['wins_A'],'ties':p['ties'],'candidate_gate':report['candidate_gate_result'],'public_report_sha256':sha(args.output.read_bytes())},sort_keys=True))

if __name__=='__main__': main()
