#!/usr/bin/env python3
"""Read-only, independently implemented arithmetic and provenance receipt audit.
Runs on public-safe aggregate reports. Does not open TRAIN/VAL/TEST/checkpoints.
"""
from __future__ import annotations
import argparse, hashlib, json
from collections import Counter
from pathlib import Path

def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def main():
 a=argparse.ArgumentParser();a.add_argument('--metadata',required=True);a.add_argument('--eval',required=True)
 a.add_argument('--cpu',required=True);a.add_argument('--test-log',required=True);a.add_argument('--out',required=True);args=a.parse_args()
 m=json.loads(Path(args.metadata).read_text());e=json.loads(Path(args.eval).read_text());c=json.loads(Path(args.cpu).read_text())
 log=Path(args.test_log).read_text();checks=[]
 def check(label,condition):
  checks.append({'id':label,'pass':bool(condition)})
 check('real_metadata_status',m['status']=='PASS_REAL_METADATA_COUNT_MATCHED_128_STEPS_SOURCE_ONLY')
 check('input_pack_pin',m['private_inputs_sha256']['train_val_npz']=='184f68b4c0c800ef3e98362c2e20e1cd35baa269e926489a475664526ecd9913')
 check('original_checkpoint_pin',m['private_inputs_sha256']['step1024_checkpoint']=='cb985751795c8328ad65acf7ca4c1033ce35182c1bfbdb8c38550de629cb271b')
 z=m['public_safe_counts'];steps=m['per_step_public_summary']
 check('step_count',len(steps)==128)
 check('step_index_sequence',[x['step'] for x in steps]==list(range(1025,1153)))
 check('step_target_sum',sum(x['targets'] for x in steps)==524288)
 check('each_step_target_exact',all(x['targets']==4096 for x in steps))
 check('window_draws_match',sum(x['window_draws'] for x in steps)==z['forward_window_draws_per_arm'])
 check('all_forward_shapes_match',all(x['forward_slots']==x['window_draws']*256 for x in steps))
 check('slot_total',sum(x['forward_slots'] for x in steps)==z['forward_slots_per_arm'])
 check('first_window_metadata',z['first_story_windows']==z['train_stories']==2048)
 check('first_candidate_full',z['first_windows_with_256_targets']>0)
 check('all_real_candidates_satisfied',all(x['first_candidate_available_for_all'] for x in steps))
 check('counts_matched_each_step',all(x['counts_matched'] for x in steps))
 check('a_c_same',m['equality']['A_equals_C_exact_schedule'])
 check('b_d_same',m['equality']['B_equals_D_exact_schedule'])
 check('4arm_budget',4*z['target_exposures_per_arm']==2097152)
 check('new_eval_count',len(e['prompts'])==36)
 check('dev_size',sum(x['split']=='DEV' for x in e['prompts'])==12)
 check('final_size',sum(x['split']=='BLIND_FINAL' for x in e['prompts'])==24)
 check('ids_unique',len({x['id'] for x in e['prompts']})==36)
 check('texts_unique',len({x['prompt'] for x in e['prompts']})==36)
 check('prompt_hashes_all',all(hashlib.sha256(x['prompt'].encode()).hexdigest()==x['utf8_sha256'] for x in e['prompts']))
 check('prompt_length_under_context',all(x['bpe_token_count']<256 for x in e['prompts']))
 check('eval_not_test',e['source']=='authored_for_new_pilot_not_from_original_TINYSTORIES_TEST')
 check('cpu_parent_restored',c['status']=='PASS_FULL_PARENT_MODEL_ADAMW_SCHEDULER_SAMPLER_SCALER_CPU_RESTORE')
 check('cpu_no_updates',c['no_optimizer_step'])
 check('cpu_model_parameters',c['model_params']==3749376)
 check('cpu_scaler',c['scaler_state']['scale']==65536.0)
 check('cpu_gpu_not_claimed',c['gpu_fp16_not_executed'])
 check('test42','Ran 42 tests' in log and '\nOK\n' in log)
 check('no_private_token_records','train_x' not in str(m.keys()) and 'train_x' not in e)
 check('not_owner_approved',e['review']['human_independent_reviewer_assigned']==False)
 check('no_original_test',m['limitations'][0].startswith('PRIVATE raw'))
 if not all(x['pass'] for x in checks):raise RuntimeError('INDEPENDENT_PUBLIC_SAFE_ARITHMETIC_AUDIT_FAIL:'+','.join(x['id'] for x in checks if not x['pass']))
 rec={'schema':'ttm.2x2.real_metadata.readiness.second_pass_audit.v1','status':f'PASS_{len(checks)}_OF_{len(checks)}_INDEPENDENT_PUBLIC_SAFE_AUDIT',
 'checks':checks,'inputs_sha256':{k:sha(getattr(args,k)) for k in ('metadata','eval','cpu','test_log')},
 'limitations':['Separate arithmetic/source inspection only, no new semantic reviewer','No new training, no GPU','Pack metadata original sampled once with frozen original checkpoint RNG; no TEST/Q1Q2']}
 out=Path(args.out);out.write_text(json.dumps(rec,indent=2,sort_keys=True)+'\n',encoding='utf-8');print(rec['status'])
if __name__=='__main__':main()
