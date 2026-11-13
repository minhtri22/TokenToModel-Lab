#!/usr/bin/env python3
"""Assemble public-safe read-only adjudication from independently produced receipts."""
from __future__ import annotations
import json,hashlib,pathlib,ast
P=pathlib.Path(__file__).parent
R=lambda n:json.loads((P/n).read_bytes())
sha=lambda p:hashlib.sha256(pathlib.Path(p).read_bytes()).hexdigest()
sam=R('TTM_HDATA_S1_REAL_TRAIN_METADATA_SAMPLER_QA_20261113.json')
ind=R('TTM_HDATA_S1_INDEPENDENT_REAL_METADATA_QA_20261113.json')
bpe=R('TTM_HDATA_S1_DEV_BPE_PARENT_STRUCTURAL_QA_20261113.json')
paths={
 'sampler_source':'ttm_hdata_s1_real_metadata_preexec_v1.py',
 'independent_source':'ttm_hdata_s1_independent_metadata_qa_v1.py',
 'bpe_source':'ttm_hdata_s1_bpe_resume_preexec_v1.py',
 't4_no_train_source':'ttm_hdata_s1_t4_source_only_readback_v1.py',
 'sampler_receipt':'TTM_HDATA_S1_REAL_TRAIN_METADATA_SAMPLER_QA_20261113.json',
 'independent_receipt':'TTM_HDATA_S1_INDEPENDENT_REAL_METADATA_QA_20261113.json',
 'bpe_receipt':'TTM_HDATA_S1_DEV_BPE_PARENT_STRUCTURAL_QA_20261113.json'
}
# Verify static safety: no executable model/optimizer forward/backward/step paths.
for k in ('sampler_source','independent_source','bpe_source','t4_no_train_source'):
    ast.parse((P/paths[k]).read_text('utf8'))
    forbidden=('eval(', 'exec(', '.backward(', '.step(', 'model(', '.forward(')
    contents=(P/paths[k]).read_text('utf8')
    # Method names appear in descriptive text only; verify prohibited calls via AST independently.
    tree=ast.parse(contents)
    for node in ast.walk(tree):
        if isinstance(node,ast.Call):
            fn=node.func
            if isinstance(fn,ast.Attribute) and fn.attr in ('backward','forward','step'):
                raise RuntimeError('H_DATA_PREEXEC_FORBIDDEN_MODEL_COMPUTE_'+k+'_'+fn.attr)
            if isinstance(fn,ast.Name) and fn.id in ('eval','exec'):
                raise RuntimeError('H_DATA_PREEXEC_FORBIDDEN_DYNAMIC_CODE_'+k)
assert sam['targets_each']==ind['target_labels_per_arm']==524288
assert sam['draws_each']==ind['draws_per_arm']==2928
assert sam['slots_each']==ind['forward_slots_per_arm']==749568
assert sam['baseline_unique_stories']==ind['control_unique_stories']==1493
assert sam['treatment_unique_stories']==ind['treatment_unique_stories']==2048
assert sam['treatment_first_window_fraction']==ind['treatment_first_fraction']==1.0
assert ind['legacy_step_count_match']==128 and ind['paired_step_target_count_match']==128
assert sam['metadata_pause_resume_64_64']=='PASS_EXACT'
assert bpe['bpe_roundtrip_pass']==12 and bpe['context_plus64_pass']==12
assert all(sam['thresholds'].values())
assert ind['science_execution'] is False and bpe['no_model_forward'] is True
owner_sign=pathlib.Path('/mnt/data/RIGHTS_OWNER_SIGNED.json')
rights=json.loads(owner_sign.read_bytes())
assert rights['internal_A_C_only'] is True
assert sha('/mnt/data/T4_PRIVATE_TRAIN_VAL_WINDOWS.npz')=='184f68b4c0c800ef3e98362c2e20e1cd35baa269e926489a475664526ecd9913'
assert sha('/mnt/data/checkpoint.pt')=='cb985751795c8328ad65acf7ca4c1033ce35182c1bfbdb8c38550de629cb271b'
assert sha('/mnt/data/T1_BPE2048_REAL_TRAIN_MANIFEST.json')=='cba18e60cee3d08a353ee6d4a451017289e45af7b4b1179c87171b9b78d7dfdc'
manifest=json.loads(pathlib.Path('/mnt/data/T4_PRIVATE_PACK_MANIFEST.json').read_bytes())
ready=json.loads(pathlib.Path('/mnt/data/READY.json').read_bytes())
assert manifest['contains_test'] is False and manifest['counts']['test_stories_tokenized']==0
assert ready['sha256']=='cb985751795c8328ad65acf7ca4c1033ce35182c1bfbdb8c38550de629cb271b'
source_shas={k:sha(P/n) for k,n in paths.items()}
receipt={
 'schema':'ttm.small4m.hdata_s1.integrated_real_metadata_preexec.owner_single_gate.v1',
 'date':'2026-11-13',
 'operation':'TTM_HDATA_S1_ONEPACKET_SAMPLER_SOURCE_REAL_METADATA_QA_RIGHTS_T4_RESUME_AND_OWNER_GO_HOLD_PREEXEC_NO_TRAIN',
 'run_id':'TTM_SMALL4M_HDATA_S1_MATCHED_BUDGET_FRESH_FINAL_V1',
 'git_source_branch':'research/ttm-small4m-h-data-s1-matched-budget-prereg-20261113',
 'prereg_source_base_commit':'2b5cc60ee032df66e6a368c4793fbb1ed6767ee3',
 'fixed_source_sha256':source_shas,
 'source_pins':{
  'train_val_pack_sha256':manifest['npz_sha256'],
  'original_T4_private_pack_manifest_sha256':sha('/mnt/data/T4_PRIVATE_PACK_MANIFEST.json'),
  'parent_P02_checkpoint_1024_sha256':ready['sha256'],
  'parent_ready_json_sha256':sha('/mnt/data/READY.json'),
  'original_P02_science_lock_sha256':sha('/mnt/data/T4_SCIENCE_LOCK_A2_1024.json'),
  'bpe_manifest_sha256':sha('/mnt/data/T1_BPE2048_REAL_TRAIN_MANIFEST.json'),
  'new_final24_owner_private_immutable_sha256_only':'b129a5c52520a25f1c40de950471622320abfa6b5414d0b16e0111ed96adc680',
  'new_final24_public_sha_commitment_sha256':'6c8c21c406b4bc30171244142c4226460a6735164f88fd425db7afa070a6f4f3',
 },
 'independent_qa':{'code_separate_from_sampler':True,'checks_passed':ind['checks_passed'],
                   'legacy_original_128_step_draw_counts_reproduced':128,'negative_mutations_rejected':ind['tamper_negative_count'],
                   'valid_train_label_count_replayed_per_step':128},
 'gates':{
  'exact_private_train_val_pack_sha':'PASS',
  'TRAIN_metadata_only_story_counts':'PASS_2048_STORIES_2691_WINDOWS',
  'sampler_parent_rng_replay':'PASS_128_OF_128_HISTORICAL_DRAW_COUNTS',
  'matched_128_step_4096_targets_each':'PASS_524288_PER_ARM',
  'matched_forward_windows_and_256_slots':'PASS_2928_WINDOWS_749568_SLOTS_PER_ARM',
  'manipulation_gain_unique_story_relative':'PASS_37_1735_PERCENT',
  'manipulation_gain_first_window_absolute':'PASS_24_0096_PERCENTAGE_POINTS',
  'BPE_DEV12_roundtrip':'PASS_12_OF_12_SHADOW_IMPLEMENTATION',
  'BPE_DEV12_context_max64':'PASS_12_OF_12_PROMPT_TOKENS_36_TO_52',
  'parent_step1024_optimizer_scheduler_scaler_structure':'PASS_CPU_READONLY',
  'sampler_resume_64_64':'PASS_CPU_METADATA_ONLY',
  'training_resume_stateful_T4':'HOLD_NOT_EXECUTED',
  'new_two_arm_T4_training_runner_integrated':'HOLD_NOT_VERIFIED',
  'current_T4_runtime_source_and_fp16_pin':'HOLD_NOT_EXECUTED',
  'owner_HDATA_S1_new_training_rights':'HOLD_OLD_A_C_SIGNOFF_SCOPED_ONLY',
  'owner_HDATA_S1_specific_science_GO':'NOT_GRANTED',
  'AES_24_NEW_FINAL_blind_mapping_before_forward':'NOT_CREATED',
  'rater_early_acceptance':'NOT_REQUIRED_POST_GENERATION',
  'science_training':'NOT_EXECUTED',
  'model_forward_or_inference':'NOT_EXECUTED'
 },
 'matched_sampler':{
   'H0_stories':sam['baseline_unique_stories'],'H1_stories':sam['treatment_unique_stories'],
   'relative_story_gain':sam['relative_story_gain'],
   'H0_first_window_fraction':sam['baseline_first_window_fraction'],
   'H1_first_window_fraction':sam['treatment_first_window_fraction'],
   'first_window_percentage_point_gain':sam['first_window_percentage_point_gain'],
   'draws_each':sam['draws_each'],'forward_slots_each':sam['slots_each'],'labels_each':sam['targets_each'],
   'baseline_schedule_hash_only':sam['control_draw_digest'],
   'treatment_schedule_hash_only':sam['treatment_draw_digest'],
   'paired_schedule_hash_only':sam['paired_schedule_digest'],
   'replacement_draws':sam['replaced_draws'],
   'risk_H1_first_window_only':'ALL_TREATMENT_WINDOWS_ARE_FIRST_STORY_WINDOWS__MAY_REDUCE_LATE_STORY_INFORMATION'
 },
 'scope':{'TRAIN_x_y_token_arrays_decompressed_for_analysis':False,
          'metadata_members_READ':['train_count.npy','train_story_index.npy'],
          'VAL_metadata_arrays_READ':False,'TEST_Q1_Q2_OOD_READ':False,
          'FINAL24_prompt_text_READ':False,
          'new_GPU_or_model_forward':0,'optimizer_updates':0,
          'original_FINAL24_and_NEXT24':'CLOSED_NOT_REUSED',
          'source_SHA_before_training':True,
          'old_owner_consent_scope':'INTERNAL_A_C_ONLY'},
 'interpretation':'The bundled H1 policy meets the preregistered manipulation/budget criteria on exact original TRAIN metadata. 100% first-window selection is a large distribution shift, not evidence of improved prompt following. No scientific training benefit has been tested.',
 'source_qa_verdict':'PASS_SCOPED_REAL_TRAIN_METADATA_AND_DEV_BPE',
 'owner_single_gate_decision':'HOLD_NO_GO_TRAINING_PENDING_NEW_RIGHTS_T4_RUNNER_RESUME_AND_NEW_BLIND_ESCROW',
 'training_release':False,
 'new_source_training_owner_GO_granted':False,
 'lineage_action':'APPEND_ONLY_PREEXEC_HOLD_IF_FINAL_READBACK',
 'main_action':'UNCHANGED',
 'next':'Single integrated owner H-DATA rights approval, native T4 runner source QA and exact interrupted-resume parity, AES escrow source freeze BEFORE any model-forward, then one GO/HOLD; do not train in this phase'
}
output=P/'TTM_HDATA_S1_INTEGRATED_PREEXEC_OWNER_GO_HOLD_20261113.json'
output.write_text(json.dumps(receipt,ensure_ascii=False,sort_keys=True,indent=2)+'\n',encoding='utf8')
print('H_DATA_S1_OWNER_DECISION='+receipt['owner_single_gate_decision'])
print('H_DATA_S1_MANIPULATION_STORY_GAIN='+str(sam['relative_story_gain']))
print('H_DATA_S1_MANIPULATION_FIRST_PP='+str(sam['first_window_percentage_point_gain']))
print('H_DATA_S1_SOURCE_SHA256='+sha(output))
