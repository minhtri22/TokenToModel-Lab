#!/usr/bin/env python3
"""Independent contract/negative QA for the CPU pilot prereg (NO training)."""
from __future__ import annotations
import argparse,ast,hashlib,importlib.util,json,subprocess,sys
from pathlib import Path
import torch

def main():
    ap=argparse.ArgumentParser()
    ap.add_argument('--root',type=Path,required=True)
    ap.add_argument('--report',type=Path,required=True)
    ap.add_argument('--out',type=Path,required=True)
    a=ap.parse_args();root=a.root.resolve(strict=True)
    if not a.out.resolve().is_relative_to(root) or a.out.exists():raise ValueError('BAD_OR_EXISTING_OUTPUT')
    result=json.loads(a.report.read_text('utf8'))
    scripts=(root/'tools/research/vector-memory' if (root/'tools/research/vector-memory/cpu_pilot_one_shot.py').exists() else root)
    src=(scripts/'cpu_pilot_one_shot.py').read_text('utf8')
    prep=(scripts/'cpu_pilot_readiness.py').read_text('utf8')
    execmod=ast.parse(src);checks={}
    def check(name,value):
        checks[name]=bool(value)
        if not value:raise AssertionError(name)
    check('01_primary_report_29_of_29',result['checks_passed']==29 and all(result['checks'].values()))
    check('02_checkpoint_step1280_pin',result['pins']['checkpoint_sha256']=='ee723407b2c25a18be20e26387a3dd8e4a18e2942d469279b6f0748ff86af0dc')
    check('03_source_blobs_pinned',len(result['pins']['p02_git_blob'])==40 and len(result['pins']['reader_git_blob'])==40)
    check('04_trained_checkpoint_bypass_exact',result['checks']['25_pretrained_full_logits_no_memory_bit_exact'])
    check('05_trained_checkpoint_cold_reader_exact',result['checks']['26_pretrained_full_logits_cold_reader_bit_exact'])
    check('06_trained_checkpoint_unchanged',result['checks']['27_pretrained_checkpoint_unchanged'])
    check('07_gradients_reader_only',result['checks']['21_reader_gradient_present'] and result['checks']['22_random_p02_no_gradient'])
    check('08_token_positions_and_boundaries',result['checks']['11_exact_no_memory_teacher_forcing'] and result['checks']['15_multi_token_answer_scored'])
    check('09_no_training_at_preflight',result['execution']['optimizer_steps']==0 and not result['execution']['training_executed'])
    check('10_test_and_dev_not_scored',not result['execution']['test_accessed'] and not result['execution']['dev_model_scoring'])
    check('11_fixed_128_steps_16_batch',result['plan']['steps']==128 and result['plan']['batch_stories']==16)
    check('12_fixed_final_only',result['plan']['dev_evaluations']==1 and result['plan']['checkpoint_selection']=='fixed_final_step_128_no_best_of_dev')
    check('13_one_shot_opt_in',"if not args.execute_once:raise SystemExit('NOT_AUTHORIZED_EXECUTION" in src)
    check('14_refuse_existing_output',"ONE_SHOT_CONSUMED_OR_PARTIAL_NO_OVERWRITE" in src)
    check('15_frozen_output_path',"ONE_SHOT_OUTPUT_PATH_NOT_FROZEN" in src)
    check('16_forbid_private_inputs_outside_project',"PRIVATE_INPUT_OUTSIDE_PROJECT_ROOT" in src)
    check('17_test_path_not_used',"TEST_64" not in src and "aesgcm" not in src.lower())
    check('18_no_automatic_resume',"resume" not in src.lower() or "auto-resume" in src)
    check('19_reader_qk_frozen_in_oracle_mode',"reader.query_proj.requires_grad_(False)" in src and "reader.key_proj.requires_grad_(False)" in src)
    check('20_optimizer_only_learned',"learned=[p for p in reader.parameters() if p.requires_grad]" in src and "AdamW(learned" in src)
    check('21_mean_per_story_training_metric',"story_losses.mean()" in src)
    check('22_wrong_and_no_controls',"for arm in ['none','correct','wrong']" in src)
    check('23_bootstrap_1000_fixed',"size=(1000,len(v))" in src)
    check('24_DEV_once_after_train',src.index("if len(losses)!=STEPS")<src.index("for arm in ['none','correct','wrong']"))
    check('25_no_early_best_of_DEV',"best_dev" not in src and "early_stop" not in src)
    check('26_prompt_gold_not_oracle_argument',"encode_cards_for_reader([case['question']],[case['correct_memory']]" in src and "c['target_key']" not in src)
    check('27_P02_orig_unmodified_in_runner',"model.requires_grad_(False)" in src and "model.load_state_dict(ck['model'],strict=True)" in src)
    check('28_owner_receipt_accepted_only_by_real_SHA',"sha256(args.t1_owner_receipt)!=PIN['owner_receipt_sha256']" in src)
    check('29_T1_real_manifest_required',"t1.BPE2048.from_manifest" in src and "PINNED_TINYSTORIES_TRAIN" in src)
    check('30_no_science_output_exists_in_this_run',not (root/'_evidence'/'vector-memory'/'TTM_VM_EXTERNAL_FACTS_CPU_ORACLE_TRAIN_DEV_20261111_V1').exists())
    # Negative controls for the scorer's prefix and context rules.
    spec=importlib.util.spec_from_file_location('vm_prep_negative',str(scripts/'cpu_pilot_readiness.py'))
    m=importlib.util.module_from_spec(spec);sys.modules[spec.name]=m;spec.loader.exec_module(m)
    bad=lambda s:[1] if ' ' not in s else [2,3]
    try:m.encode_target(bad,'Hello','bad')
    except ValueError as e:bad_ok='ANSWER_PREFIX_RETOKENIZATION_MISMATCH' in str(e)
    else:bad_ok=False
    check('31_boundary_retokenization_rejected',bad_ok)
    long_q='x'*257
    try:m.encode_target(lambda s:list(s.encode('ascii')),long_q,'z')
    except ValueError:long_ok=True
    else:long_ok=False
    check('32_context_overflow_rejected',long_ok)
    # Refuse running pilot without explicit permission, before opening inputs.
    child=subprocess.run([sys.executable,str(scripts/'cpu_pilot_one_shot.py'),
        '--project-root',str(root),'--checkout',str(root),
        '--checkpoint','missing','--t1-manifest','missing','--t1-owner-receipt','missing',
        '--output-dir',str(root/'_evidence'/'vector-memory'/'TTM_VM_EXTERNAL_FACTS_CPU_ORACLE_TRAIN_DEV_20261111_V1')],
        capture_output=True,text=True,timeout=10)
    check('33_opt_in_required_before_any_io',child.returncode!=0 and 'NOT_AUTHORIZED_EXECUTION' in child.stderr)
    check('34_only_source_qa_in_audit',not (root/'_evidence'/'vector-memory'/'TTM_VM_EXTERNAL_FACTS_CPU_ORACLE_TRAIN_DEV_20261111_V1').exists())
    ret={'schema':'ttm.vm.externalfacts.cpu_pilot.independent_preexecution_qa.v1',
       'status':'PASS_INDEPENDENT_SOURCE_PREEXEC_QA',
       'checks':checks,'checks_passed':sum(checks.values()),'checks_total':len(checks),
       'science_execution':'NOT_EXECUTED','optimizer_steps':0,'test_opened':False,
       'real_T1_receipt_readback':'OWNER_ONLY_NOT_INDEPENDENTLY_ACQUIRED',
       'limits':'Static runner review + synthetic-only negative QA + verification of primary checkpoint synthetic parity. Does not claim DEV or TEST science.'}
    a.out.parent.mkdir(parents=True,exist_ok=True)
    a.out.write_text(json.dumps(ret,ensure_ascii=False,sort_keys=True,indent=2)+'\n',encoding='utf8')
    print(json.dumps({'status':ret['status'],'checks_passed':ret['checks_passed'],'total':ret['checks_total'],'TEST':False,'TRAIN':False},sort_keys=True))

if __name__=='__main__':main()
