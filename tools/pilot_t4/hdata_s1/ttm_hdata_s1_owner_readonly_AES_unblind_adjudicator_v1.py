#!/usr/bin/env python3
"""H-DATA-S1 FINAL24: one owner-authorized, read-only AES unblind.

CUSTODY BOUNDARY: Reads the *original* AES-256-GCM escrow ZIP only in RAM;
never writes key, decrypted mapping, pair-level arm labels, prompts, notes,
individual generations, or model weights to disk or stdout. Output is a
public-safe aggregate JSON, created exclusively (never overwritten).

No torch, GPU, training, prompt generation, rescoring, or packet edits.
"""
from __future__ import annotations
import base64
from collections import Counter, defaultdict
import hashlib
import json
import math
import os
from pathlib import Path
import sys
import zipfile
import numpy as np
from cryptography.hazmat.primitives.ciphers.aead import AESGCM

RUN_ID = 'TTM_SMALL4M_HDATA_S1_MATCHED_BUDGET_FRESH_FINAL_V1'
CONTRACT_SCHEMA = 'ttm.small4m.hdata_s1.scoring_protocol.v1'
EXPECTED = {
    'score': '81a680be56c7535a2a14137be69d121c76a43cb28f2b93995b020471609966f4',
    'array': 'fcbd93e8c2580566eb0414301a9afa5a13d07b2c179c8fe686bad3ccd68a167e',
    'freeze': 'fdf09445234fbf6d7a5d5092f685590720dfede88672d6229060768cc9cce449',
    'packet': '60be28c7bde777c61d984209fad31a049702b806ef3d015c2af8a9c64ad1ccd8',
    'generation': 'e2fca65f2d1571a8e61c365ea69d34dc4876af6c5741a55c25ec60aa6d17a4df',
    'ready': 'e30a2281580b1f6ea33856577f0a244cd02e226dc8a3db00d207a8fe13cce4b5',
    'zip': 'c5c5d6eae6ce38d892348878ae200d5bbcd42406b53f7b0c43e8876a145d48d4',
    'cipher': 'de0562cd4a9584ca8128e505b14e3d04ae35793b72f7d8a2b4d4f6eb0176cc7d',
    'commitment': '6c8c21c406b4bc30171244142c4226460a6735164f88fd425db7afa070a6f4f3',
    'source': '7953d33fa592a8890a185cedf490d7af2df9514e025395f00a1996c7bf784363',
    'gen_permit': '242a0925320e9c4aeb716fca4324cdce12d384f52322589f2e403ae464702581',
}
ROOT = Path('/mnt/data')
SCORED = ROOT/'hdata_blind240_drive_readback/TTM_HDATA_S1_FINAL24_INDEPENDENT_AI_BLIND240_SCORED_FROZEN_20261114.json'
ARRAY = ROOT/'hdata_blind240_drive_readback/TTM_HDATA_S1_FINAL24_CANONICAL_240_SCORE_ARRAY_20261114.json'
FREEZE = ROOT/'hdata_blind240_drive_readback/TTM_HDATA_S1_FINAL24_INDEPENDENT_AI_SCORE_SHA_FREEZE_RECEIPT_20261114.json'
PACKET = ROOT/'BLIND_FINAL24_RATER_PACKET.json'
GEN = ROOT/'OWNER_PRIVATE_GENERATION_RECEIPT.json'
READY = ROOT/'TTM_HDATA_S1_OWNER_READY_LAST_SCIENCE_READBACK_20261113.json'
ESCROW = ROOT/'TTM_HDATA_S1_OWNER_PRIVATE_ESCROW_BACKUP_DO_NOT_GITHUB.zip'
CONTRACT = ROOT/'hdata_s1_frozen_scoring_contract_20261113.json'
OUTPUT = ROOT/'TTM_HDATA_S1_FINAL24_READONLY_UNBLIND_PUBLIC_AGGREGATE_20261114.json'
KEY_NAME = 'TTM_HDATA_S1_OWNER_AES_KEY_PRIVATE_DO_NOT_GITHUB.json'
CIPHER_NAME = 'TTM_HDATA_S1_ENCRYPTED_BLIND_ESCROW_PUBLIC_SAFE.json'
AXES = ['actor_retention','object_relation_retention','goal_or_rule_progress','coherence','consistency']
STRATA = ['object_custody','social_relation','causal_obstacle','temporal_rule']

def need(condition, why):
    if not condition:
        raise RuntimeError('TTM_HDATA_S1_UNBLIND_HOLD:'+why)

def sha(b:bytes) -> str:
    return hashlib.sha256(b).hexdigest()

def get(name: str, path:Path):
    need(path.is_file() and not path.is_symlink(),'FILE_MISSING_OR_LINKED_'+name)
    raw=path.read_bytes()
    if name in EXPECTED:
        need(sha(raw)==EXPECTED[name],'SHA_DRIFT_'+name)
    return json.loads(raw),raw

def run():
    # Gate 0: fail closed on already consumed run; never overwrite/replay.
    need(not OUTPUT.exists(), 'AGGREGATE_ALREADY_EXISTS_ONE_SHOT_NO_REPLAY')
    score,score_raw = get('score',SCORED)
    arr,arr_raw = get('array',ARRAY)
    freeze,_ = get('freeze',FREEZE)
    packet,_ = get('packet',PACKET)
    gen,_ = get('generation',GEN)
    ready,_= get('ready',READY)
    contract,_=get('contract',CONTRACT)
    need(contract.get('schema') == CONTRACT_SCHEMA and contract['run_id']==RUN_ID,'LOCKED_CONTRACT')
    need(contract['primary_endpoint']=='delta_mean_anchor_preservation_score_H1_minus_H0_over_24_new_FINAL_prompt_pairs','PRIMARY_ENDPOINT_DRIFT')
    need([x['name'] for x in contract['primary_components']]==AXES[:3] and [x['range'] for x in contract['primary_components']]==[[0,1]]*3,'PRIMARY_AXES_DRIFT')
    need([x['name'] for x in contract['secondary_scored_axes']]==AXES[3:] and [x['range'] for x in contract['secondary_scored_axes']]==[[0,3]]*2,'SECONDARY_AXES_DRIFT')
    pg=contract['primary_gate'];sg=contract['secondary_guardrails'];cg=contract['components_guardrails']
    need(pg=={'H1_strict_pair_wins_at_least':16,'bootstrap_resamples':20000,'bootstrap_rng_seed':20261113,'bootstrap_unit':'24 prompt pairs, not tokens','mean_H1_minus_H0_at_least':0.5,'paired_bootstrap_CI95_lower_gt':0},'FROZEN_PRIMARY_GATES_DRIFT')
    need(cg=={'actor_mean_delta_min':-0.125,'goal_mean_delta_strictly_gt':0,'object_mean_delta_min':-0.125},'FROZEN_COMPONENT_GATES_DRIFT')
    need(sg=={'VAL_NLL_relative_regression_max':0.05,'coherence_mean_delta_min':-0.25,'consistency_mean_delta_min':-0.25,'report_EOS_and_cap64_counts':True,'under8_word_H1_count_lte_H0':True},'FROZEN_SECONDARY_GATES_DRIFT')
    need(score['schema']=='ttm.hdata_s1.blind240_score_template.source_only.v1' and score['score_status']=='SCORED_FROZEN_PENDING_UNBLIND' and score['rater_type']=='EXPLORATORY_SCOPED_AI_REVIEW' and score['blind']=='MODEL_IDENTITY_LEFT_RIGHT_UNKNOWN' and score['run_id']==RUN_ID,'SCORE_FROZEN_SCOPE')
    need(freeze['score_file']['sha256']==EXPECTED['score'] and freeze['canonical_score_array']['sha256']==EXPECTED['array'] and freeze['input_packet']['sha256']==EXPECTED['packet'] and freeze['unblind']=='NOT_EXECUTED','FREEZE_RECEIPT_CHAIN')
    need(freeze['canonical_score_array']['entries']==240 and freeze['score_status']=='SCORED_FROZEN_PENDING_UNBLIND','FREEZE_COUNTS')
    need(packet['schema']=='ttm.hdata_s1.neutral_blind_final24.rater_packet.v1' and packet['run_id']==RUN_ID and packet['blind'] is True and len(packet['records'])==24,'PACKET_SCOPE')
    need(gen['schema']=='ttm.hdata_s1.final24_owner_generation_receipt.v1' and gen['run_id']==RUN_ID and gen['status']=='GENERATED_PENDING_BLIND_RATER' and gen['rater_packet_sha256']==EXPECTED['packet'] and gen['generator_source_sha256']==EXPECTED['source'] and gen['permit_sha256']==EXPECTED['gen_permit'] and gen['NEW_FINAL_generation']=='EXECUTED_ONCE' and gen['unblind']=='NOT_EXECUTED','GENERATION_CHAIN')
    need(ready['status']=='PASS_TWO_ARM_128_STEP_READY_LAST_UNADJUDICATED' and ready['run_id']==RUN_ID,'READY_LAST_CHAIN')

    numerics=[]
    score_rows=score['records']; packet_rows=packet['records']
    need(len(score_rows)==24 and len(packet_rows)==24,'RATER_PAIR_COUNT')
    for i,(r,p) in enumerate(zip(score_rows,packet_rows),1):
        pid=f'R{i:02d}'
        need(r['pair_id']==p['pair_id']==pid,'PAIR_ID_ORDER')
        need(set(r)=={'pair_id','LEFT','RIGHT','note'} and isinstance(r['note'],str) and bool(r['note'].strip()),'PAIR_NOTE_SCOPE')
        need(set(p)=={'pair_id','LEFT','RIGHT','prompt_text'} and all(isinstance(p[k],str) for k in ('LEFT','RIGHT','prompt_text')),'PACKET_CONTENT_SCOPE')
        for side in ['LEFT','RIGHT']:
            row=r[side]
            need(set(row)==set(AXES),'RATER_AXIS_SET')
            for j,axis in enumerate(AXES):
                v=row[axis]
                need(type(v) is int and 0<=v<=(1 if j<3 else 3),'RATER_SCORE_RANGE')
                numerics.append({'pair_id':pid,'side':side,'axis':axis,'score':v})
    need(len(numerics)==240,'RATER_240')
    recomputed=json.dumps(numerics,ensure_ascii=False,sort_keys=True,separators=(',',':')).encode('utf-8')
    need(recomputed==arr_raw and sha(recomputed)==EXPECTED['array'] and arr==numerics,'CANONICAL_ARRAY_MATCH')

    # Gate 1: AES authentication; no plaintext mapping ever leaves process.
    need(ESCROW.is_file() and not ESCROW.is_symlink() and sha(ESCROW.read_bytes())==EXPECTED['zip'],'ESCROW_ZIP_SHA')
    with zipfile.ZipFile(ESCROW) as z:
        need(set(z.namelist())=={KEY_NAME,CIPHER_NAME,'README_OWNER_PRIVATE.txt'},'ESCROW_MEMBER_SCOPE')
        encrypted_bytes=z.read(CIPHER_NAME)
        key_bytes=z.read(KEY_NAME)
    need(sha(encrypted_bytes)==EXPECTED['cipher'],'AES_CIPHERTEXT_SHA')
    key=json.loads(key_bytes)
    encrypted=json.loads(encrypted_bytes)
    need(key['schema']=='ttm.hdata_s1.owner_private_aes_key.v1' and encrypted['schema']=='ttm.hdata_s1.encrypted_blind_escrow.v1','AES_SCHEMA')
    need(key['run_id']==encrypted['run_id']==RUN_ID and encrypted['commitment_sha256']==EXPECTED['commitment'] and key['public_escrow_sha256']==EXPECTED['cipher'],'AES_COMMITMENT_CHAIN')
    aad=('TTM_HDATA_S1_HF01_HF24_AES256GCM_V1|'+RUN_ID+'|'+EXPECTED['commitment']).encode('ascii')
    need(base64.b64decode(encrypted['aad_b64'])==aad,'AES_AAD_MATCH')
    key_value=base64.b64decode(key['key_b64']);nonce=base64.b64decode(encrypted['nonce_b64']);ciphertext=base64.b64decode(encrypted['ciphertext_b64'])
    need(len(key_value)==32 and len(nonce)==12,'AES_LENGTHS')
    decrypted=AESGCM(key_value).decrypt(nonce,ciphertext,aad)
    need(sha(decrypted)==key['mapping_sha256']==encrypted['plaintext_mapping_sha256'],'DECRYPTED_MAPPING_SHA')
    mapping=json.loads(decrypted)
    need(mapping.get('schema')=='ttm.hdata_s1.owner_private_blind_map.v1' and mapping.get('run_id')==RUN_ID,'AES_MAPPING_SCHEMA')
    pairs=mapping.get('pairs')
    need(isinstance(pairs,list) and len(pairs)==24,'AES_MAPPING_PAIR_COUNT')
    strata_counts=defaultdict(list)
    by_side=[]
    for i,(m,p) in enumerate(zip(pairs,packet_rows),1):
        name=f'R{i:02d}';hf=f'HF{i:02d}';stratum=STRATA[(i-1)//6]
        need(m['pair_id']==name and p['pair_id']==name and m['prompt_id']==hf and m['stratum']==stratum,'AES_PAIR_ID_STRATUM')
        need({m['left_arm'],m['right_arm']}=={'H0','H1'},'AES_TWO_ARMS')
        strata_counts[stratum].append(m['left_arm'])
        by_side.append(m['left_arm'])
    need(Counter(by_side)=={'H0':12,'H1':12},'AES_BALANCE_12_12')
    need(all(Counter(strata_counts[x])=={'H0':3,'H1':3} for x in STRATA),'AES_PER_STRATUM_BALANCE_3_3')

    # Gate 2: unblind in memory only; aggregate by arm, no per-pair publication.
    arm_rows={'H0':[],'H1':[]}
    pair_diffs=[]
    for scored, m in zip(score_rows, pairs):
        for side in ('LEFT','RIGHT'):
            arm_rows[m['left_arm'] if side=='LEFT' else m['right_arm']].append(scored[side])
        sides={m['left_arm']:scored['LEFT'],m['right_arm']:scored['RIGHT']}
        pair_diffs.append(sum(sides['H1'][k]-sides['H0'][k] for k in AXES[:3]))
    need(len(arm_rows['H0'])==len(arm_rows['H1'])==24 and len(pair_diffs)==24,'UNBLIND_PAIR_COUNT')

    def mean_by_arm(axis):return {arm:sum(r[axis] for r in rows)/24 for arm,rows in arm_rows.items()}
    means={axis:mean_by_arm(axis) for axis in AXES}
    delta={axis:means[axis]['H1']-means[axis]['H0'] for axis in AXES}
    primary={arm:sum(sum(r[k] for k in AXES[:3]) for r in rows)/24 for arm,rows in arm_rows.items()}
    dmean=primary['H1']-primary['H0']
    wins=sum(v>0 for v in pair_diffs); losses=sum(v<0 for v in pair_diffs);ties=sum(v==0 for v in pair_diffs)
    need(abs(sum(pair_diffs)/24-dmean)<1e-12,'PAIRED_MEAN_CONSISTENCY')
    rng=np.random.default_rng(int(pg['bootstrap_rng_seed']))
    ix=rng.integers(low=0,high=24,size=(int(pg['bootstrap_resamples']),24),endpoint=False)
    boot=np.asarray(pair_diffs,dtype=np.float64)[ix].mean(axis=1)
    ci=[float(np.quantile(boot,0.025)),float(np.quantile(boot,0.975))]
    need(math.isfinite(ci[0]) and math.isfinite(ci[1]),'BOOTSTRAP_FINITE')

    owner_counts=gen['arm_counts_OWNER_ONLY_NOT_FOR_RATER']
    for arm in ('H0','H1'):
        z=owner_counts[arm]
        need(set(z)=={'eos','cap64','under8_word'} and all(type(v) is int and v>=0 for v in z.values()) and z['eos']+z['cap64']==24,'OWNER_COUNTS_SUM_24')
    rarms={a['arm']:a for a in ready['arms']}
    need(set(rarms)=={'H0','H1'} and all(rarms[arm]['steps']==128 and rarms[arm]['end_step']==1152 for arm in ('H0','H1')),'SCIENCE_128_STEP_READY')
    v0=float(rarms['H0']['val_nll']);v1=float(rarms['H1']['val_nll']);vrel=(v1-v0)/v0
    verdict={
      'primary_mean_delta_ge_0p5':dmean>=float(pg['mean_H1_minus_H0_at_least']),
      'primary_strict_wins_ge_16':wins>=int(pg['H1_strict_pair_wins_at_least']),
      'primary_bootstrap_ci95_lower_gt_0':ci[0]>float(pg['paired_bootstrap_CI95_lower_gt']),
      'actor_delta_ge_neg0p125':delta['actor_retention']>=float(cg['actor_mean_delta_min']),
      'object_delta_ge_neg0p125':delta['object_relation_retention']>=float(cg['object_mean_delta_min']),
      'goal_delta_strict_gt_0':delta['goal_or_rule_progress']>float(cg['goal_mean_delta_strictly_gt']),
      'coherence_delta_ge_neg0p25':delta['coherence']>=float(sg['coherence_mean_delta_min']),
      'consistency_delta_ge_neg0p25':delta['consistency']>=float(sg['consistency_mean_delta_min']),
      'val_nll_relative_regression_le_5pct':vrel<=float(sg['VAL_NLL_relative_regression_max']),
      'under8_H1_le_H0':owner_counts['H1']['under8_word']<=owner_counts['H0']['under8_word'],
      'EOS_cap64_counts_reported':bool(sg['report_EOS_and_cap64_counts']),
    }
    allpass=all(verdict.values())
    outcome=contract['outcome_if_all_gates'] if allpass else contract['outcome_otherwise']

    result={
      'schema':'ttm.hdata_s1.final24.owner_authorized_readonly_AES_unblind_adjudication.v1',
      'date':'2026-11-14',
      'operation':'TTM_HDATA_S1_FINAL24_OWNER_UNBLIND_ON_FROZEN_AI_SCORE_SINGLE_GATE',
      'owner_approval':'GO_HDATA_S1_FINAL24_OWNER_UNBLIND_ON_FROZEN_AI_SCORE',
      'independence':'EXPLORATORY_SCOPED_AI_REVIEW_NOT_HUMAN_GOLD',
      'run_id':RUN_ID,
      'input_custody_SHA256':{k:EXPECTED[k] for k in ('score','array','freeze','packet','generation','ready','zip','cipher','commitment')},
      'AES_authenticated_decrypt':'PASS_AES256_GCM_AAD_KEY_NONCE_AND_PLAINTEXT_DIGEST',
      'AES_pair_balance':'PASS_12_12_OVERALL_AND_3_3_PER_STRATUM',
      'private_AES_key_or_plaintext_mapping_in_report':False,
      'rater_scores_240':'PASS_FROZEN_UNCHANGED',
      'rater_notes_24':'PASS_NONEMPTY_FROZEN_UNCHANGED',
      'unblind':'EXECUTED_ONCE_READ_ONLY',
      'training_or_generation_reexecution':False,
      'primary_anchor_score_0to3_arm_means':primary,
      'primary_paired_H1_minus_H0_mean_delta':dmean,
      'primary_paired_strict_wins_H1':wins,
      'primary_paired_strict_losses_H1':losses,
      'primary_paired_ties':ties,
      'paired_bootstrap_20k_seed_20261113':{'resamples':int(pg['bootstrap_resamples']),'seed':int(pg['bootstrap_rng_seed']),'method':'paired resample of 24 prompt-pair H1−H0 deltas, numpy.default_rng seed, 2.5/97.5 linear quantiles','CI95':ci},
      'component_secondary_arm_means':means,
      'component_secondary_H1_minus_H0_deltas':delta,
      'generation_guardrail_counts_owner_only_aggregated':owner_counts,
      'VAL_NLL':{'H0':v0,'H1':v1,'H1_minus_H0':v1-v0,'relative_regression':vrel},
      'frozen_preregistered_gate_pass':verdict,
      'ALL_GATES_PASS':allpass,
      'formal_adjudication':outcome,
      'status':'COMPLETE_READONLY_UNBLIND_NO_REDO',
      'scoping_note':'24 pairs, single AI blind rater, exploratory only; no human gold, multi-seed or general instruction following claim; unchanged primary/secondary cutoffs',
      'public_safe_guarantee':'No per-pair LEFT/RIGHT mapping, decrypted AES plaintext/key, private prompt, continuation, or reviewer note is emitted.',
      'follow_up':'Archive source+public safe aggregate evidence; do not rerun NEW FINAL or edit frozen scoring. Separate future design-only diagnostic can investigate mechanism, never revise this outcome.'
    }
    encoded=(json.dumps(result,ensure_ascii=False,sort_keys=True,indent=2)+'\n').encode('utf-8')
    fd=os.open(OUTPUT,os.O_CREAT|os.O_EXCL|os.O_WRONLY,0o600)
    with os.fdopen(fd,'wb') as f:f.write(encoded);f.flush();os.fsync(f.fileno())
    print(json.dumps({'status':result['status'],'formal_adjudication':outcome,'ALL_GATES_PASS':allpass,
          'pair_count':len(pair_diffs),'bootstrap_ci95':ci,'passed_gates':sum(verdict.values()),
          'total_gates':len(verdict),'public_report_sha256':sha(encoded),
          'public_report_path':str(OUTPUT)},sort_keys=True))

if __name__=='__main__':run()
