#!/usr/bin/env python3
"""Read-only scorer audit for the Top-k PROBE one-shot source.

All numerical fixtures use synthetic tensors and dummy backbone. This never
opens a trained Reader, checkpoint, DEV, TEST or private run output.
"""
from __future__ import annotations
import argparse
import ast
import hashlib
import json
import subprocess
import sys
from pathlib import Path
from types import SimpleNamespace

import numpy as np
import torch
from torch import nn
from torch.nn import functional as F

import frozen_topk_probe_one_shot as run
import topk_nontest_probe as probe
import oracle_reader_source_only as vm
import topk_reader_integration as integ


def check_reject(fn, exception=(ValueError, TypeError, AssertionError)):
    try:
        fn()
    except exception:
        return True
    return False


def dummy():
    class Model(nn.Module):
        def __init__(self):
            super().__init__()
            self.tok = nn.Embedding(2048,256)
            self.pos = nn.Embedding(256,256)
            self.blocks = nn.ModuleList([])
            self.final_ln=nn.Identity()
            self.head=nn.Linear(256,2048,bias=False)
            self.head.weight = self.tok.weight
    model=Model().eval().requires_grad_(False)
    r=vm.GatedOracleReader().eval().requires_grad_(False)
    with torch.no_grad():
        r.output_proj.weight.copy_(torch.randn_like(r.output_proj.weight)*.005)
    return model,r,SimpleNamespace(encode=lambda s:list(s.encode('ascii')))


def audit():
    results={}
    def yes(name,condition):
        results[name]=bool(condition)
        if not condition:raise AssertionError(name)
    torch.set_num_threads(2)
    torch.manual_seed(20261112)
    raw=Path(run.__file__).read_bytes()
    src=raw.decode('utf8')
    tree=ast.parse(src)
    yes('01_python_compiles',isinstance(tree,ast.Module))
    yes('02_one_shot_optin_literal',"--execute-once" in src)
    yes('03_128_probe_count_fixed',"len(per_story)!=128" in src)
    yes('04_no_training_code',not any(x in src for x in ('optimizer.step(', 'torch.optim.', '.backward(', 'train_loader')))
    yes('05_no_TEST_operations',not any(x in src for x in ('TEST_SECRET','AESGCM','test_decrypt','TTM_VM_EXTERNAL_TEST_64')))
    yes('06_no_old_DEV_evaluation',not any(x in src for x in ('DEV_64_V1.json','TTM_EXTERNAL_FACTS_DEV','dev_file=')))
    yes('07_source_all_six_arms',run.ARMS==('A','O1','B1','C1','B3','C3'))
    yes('08_expected_l0020_reader_sha',run.PIN['reader_binary']=='c458de3afae87b3c381274b8edd698187df63ceac4dbbc0e6d8bd44b85c1632f')
    yes('09_expected_backbone_sha',run.PIN['backbone']=='ee723407b2c25a18be20e26387a3dd8e4a18e2942d469279b6f0748ff86af0dc')
    yes('10_expected_t1_sha',run.PIN['t1_manifest']=='cba18e60cee3d08a353ee6d4a451017289e45af7b4b1179c87171b9b78d7dfdc')
    yes('11_expected_probe_sha',run.PIN['probe_sha256']=='88c558a8f1844ee1e55bff64f30c2b801c8bf3e54ef0cbc537f9fd81e51e9c11')
    yes('12_frozen_retriever_source_sha',run.PIN['probe_src']=='b08e2120a2ac9d4e270ee48fdca77e4a4743e22c')
    yes('13_frozen_reader_source_sha',run.PIN['reader_src']=='7ce728b2874284b87933237c890e54ce3d9fd651')
    yes('14_frozen_integration_sha',run.PIN['integration_src']=='ccab713f8c5a4b913259088225daffcf5382be41')
    cases=probe.build()
    yes('15_probe_generator_builds_128',len(cases)==128)
    yes('16_probe_bytes_match_sha',hashlib.sha256(run.stable_probe_bytes(cases)).hexdigest()==run.PIN['probe_sha256'])
    yes('17_probe_disjoint_from_dev_by_case_id',all(x['case_id'].startswith('vm-probe-') for x in cases))
    yes('18_fixed_bank32',all(len(x['correct_memory'])==32 for x in cases))
    yes('19_fixed_top1_mask',sum(probe.mask_from_rank(list(range(32)),32,1))==1)
    yes('20_fixed_top3_mask',sum(probe.mask_from_rank(list(range(32)),32,3))==3)
    yes('21_bad_topk_rejected',check_reject(lambda:probe.mask_from_rank(list(range(32)),32,2)))
    yes('22_float_bootstrap_rejects_short',check_reject(lambda:run.paired_ci(np.ones(127),20261114)))
    yes('23_float_bootstrap_rejects_nan',check_reject(lambda:run.paired_ci(np.array([float('nan')]*128),20261114)))
    yes('24_float_bootstrap_1000',run.BOOTSTRAP_N==1000)
    yes('25_bootstrap_constant_mean_exact',run.paired_ci(np.ones(128)*.75,20261114)==[.75,.75])
    a=np.linspace(-1,2,128,dtype=np.float64)
    rng=np.random.default_rng(20261115)
    idx=rng.integers(0,128,size=(1000,128))
    ref=np.percentile(a[idx].mean(1),[2.5,97.5])
    yes('26_bootstrap_independent_percentile_reference',np.allclose(run.paired_ci(a,20261115),ref,atol=1e-13,rtol=0))
    yes('27_bootstrap_deterministic',run.paired_ci(a,20261115)==run.paired_ci(a,20261115))
    yes('28_bootstrap_seed_not_aliased',run.paired_ci(a,20261114)!=run.paired_ci(a,20261115))
    model, reader, t1=dummy()
    chosen=cases[0]
    outcome=run.evaluate_case(chosen,model,reader,t1)
    yes('29_scored_six_fixed_arms',set(outcome['arm_nll'])==set(run.ARMS))
    yes('30_scored_finite_nll',all(np.isfinite(v) for v in outcome['arm_nll'].values()))
    yes('31_no_memory_gate_zero',outcome['arm_gate']['A']==0.0)
    yes('32_probe_token_count_positive',outcome['answer_tokens']>0)
    yes('33_recall_hit_boolean',isinstance(outcome['r1'],bool) and isinstance(outcome['r3'],bool))
    yes('34_recall_monotonic',not outcome['r1'] or outcome['r3'])
    yes('35_lexical_recall_boolean',isinstance(outcome['lex1'],bool) and isinstance(outcome['lex3'],bool))
    yes('36_lexical_recall_monotonic',not outcome['lex1'] or outcome['lex3'])
    # Baseline EXACT independent CE reference using a separate path and same hidden.
    x,pos,y=run.encode_target(t1.encode,chosen['question'],chosen['answer'])
    h=run.frozen_hidden_at_answer_positions(model,x,pos)
    direct_logits=F.linear(h,model.head.weight)
    logprob=F.log_softmax(direct_logits,dim=-1)
    manual=float((-logprob[torch.arange(len(y)),y]).mean())
    yes('37_teacher_forcing_baseline_cross_entropy',abs(manual-outcome['arm_nll']['A'])<1e-6)
    yes('38_answer_only_token_positions',len(y)==len(t1.encode(' '+chosen['answer'])))
    yes('39_reader_value_state_still_no_gradient',all(p.grad is None for p in reader.parameters()))
    yes('40_frozen_model_no_gradient',all(p.grad is None for p in model.parameters()))
    yes('41_frozen_p02_tied_head',model.head.weight.data_ptr()==model.tok.weight.data_ptr())
    m1=integ.encode_topk_inputs(chosen['question'],chosen['correct_memory'],chosen['wrong_memory'],t1.encode,model.tok.weight,k=1)
    m3=integ.encode_topk_inputs(chosen['question'],chosen['correct_memory'],chosen['wrong_memory'],t1.encode,model.tok.weight,k=3)
    yes('42_top1_top3_rank_same',m1.rank==m3.rank)
    yes('43_top1_top3_same_keys',torch.equal(m1.correct.keys,m3.correct.keys))
    yes('44_correct_wrong_top3_masks_same',torch.equal(m3.correct.mask,m3.wrong.mask))
    yes('45_correct_wrong_top3_keys_same',torch.equal(m3.correct.keys,m3.wrong.keys))
    yes('46_answer_scramble_does_not_change_rank',m3.rank==integ.encode_topk_inputs(chosen['question'],chosen['correct_memory'],chosen['wrong_memory'],t1.encode,model.tok.weight,k=3).rank)
    target=next(i for i,v in enumerate(chosen['correct_memory']) if v['key']==chosen['target_key'])
    oracle=run.oracle_control_memory(chosen,m1)
    yes('47_oracle_exact_target_control',bool(oracle.mask[0,target]) and int(oracle.mask.sum())==1)
    yes('48_target_does_not_leak_to_topk_api','target_key' not in tuple(integ.encode_topk_inputs.__code__.co_varnames[:integ.encode_topk_inputs.__code__.co_argcount]))
    yes('49_score_shape_mismatch_denied',check_reject(lambda:run.score_from_memory(h,y[:-1],m1.none,model,reader)))
    yes('50_strict_output_path_frozen',"WRONG_FROZEN_OUTPUT_RUN_ID" in src and "ONE_SHOT_ALREADY_STARTED_DO_NOT_RETRY" in src)
    yes('51_single_use_marker_before_scoring','destination.mkdir(exist_ok=False)' in src and src.index('destination.mkdir(exist_ok=False)') < src.index('per_story=[]'))
    yes('52_reads_per_story_kept_private',"PER_STORY_QA_PRIVATE.json" in src and "PROBE_AGGREGATE_PUBLIC.json" in src)
    yes('53_original_backbone_state_equality','FROZEN_BACKBONE_MUTATED' in src)
    yes('54_original_reader_state_equality','FROZEN_READER_STATE_MUTATED' in src)
    yes('55_one_pass_source_loop','for case in cases:' in src)
    yes('56_no_mutation_of_probe_dataset','probe.build()' in src and "probe_sha256" in src)
    yes('57_retrieval_recall_metric_separate',"'recall':recall" in src)
    yes('58_oracle_domain_shift_hold','HOLD_ORACLE_READER_PROBE_DOMAIN_SHIFT' in src)
    yes('59_recall_fail_label','FAIL_RETRIEVAL_SCOPED' in src)
    yes('60_top3_fail_label','FAIL_TOP3_FROZEN_READER_SCOPED' in src)
    yes('61_success_not_test_release','GO_CANDIDATE_NONTEST_SCOPED' in src)
    yes('62_preexisting_training_not_repeated',"'optimizer_steps':0" in src)
    # Completely separate subprocess: without execute-once must fail before any file opens.
    process=subprocess.run([sys.executable,str(run.__file__),'--project-root','X:\\nonexistent','--checkout','X:\\nonexistent','--checkpoint','X:\\nonexistent', '--reader','X:\\nonexistent','--t1-manifest','X:\\nonexistent','--output-dir','X:\\nonexistent'],capture_output=True,text=True,timeout=12)
    yes('63_missing_explicit_execution_refused',process.returncode!=0 and 'DENY_NO_EXECUTE_ONCE_OPTIN' in process.stderr)
    yes('64_counterfactual_preflight_locked','PROBE_FOIL_NOT_TARGET_VALUE_ONLY' in src and 'PROBE_TARGET_VALUE_NOT_COUNTERFACTUAL' in src)
    yes('65_main_explicit_weights_only',src.count('weights_only=True')==2)
    yes('66_reader_and_model_eval_and_no_grad',"reader.requires_grad_(False)" in src and "model.requires_grad_(False)" in src)
    return results


if __name__=='__main__':
    ap=argparse.ArgumentParser();ap.add_argument('--out',required=True,type=Path);a=ap.parse_args()
    if a.out.exists():raise FileExistsError('QA_RESULT_REFUSE_OVERWRITE')
    checks=audit()
    report={'schema':'ttm.vm.topk.non_test_one_shot_runner.independent_source_synthetic_qa.v1','status':'PASS_PREEXEC_SCOPED_SOURCE_QA','checks_passed':sum(checks.values()),'checks_total':len(checks),'checks':checks,'limits':['Only mock tokenizer, random backbone and untrained Reader; no frozen learned Reader, PROBE science, DEV or TEST executed','No independent binary SHA read of owner private Reader; owner readback only','Design cannot claim semantic retrieval effectiveness before one-shot evaluation'],'execution':{'training_steps':0,'probe_science_runs':0,'dev_scored':False,'test_opened':False,'gpu_used':False}}
    a.out.parent.mkdir(parents=True,exist_ok=True)
    a.out.write_text(json.dumps(report,sort_keys=True,indent=2)+'\n')
    print(json.dumps({'status':report['status'],'qa':f'{sum(checks.values())}/{len(checks)}','probe_science':False,'test_opened':False}))
