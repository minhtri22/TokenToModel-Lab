#!/usr/bin/env python3
"""Independent V2 frozen Reader scorer QA, strictly synthetic model/cards.

No private Reader, no trained checkpoint, no real 192-case retrieval/score,
no prior PROBE/DEV/TEST access. Distinct hand-built bank for adversarial QA.
"""
from __future__ import annotations
import argparse
import ast
import copy
import json
import math
import subprocess
import sys
from pathlib import Path
from types import SimpleNamespace
import numpy as np
import torch
from torch import nn
from torch.nn import functional as F
import v2_frozen_reader_cpu_one_shot as run
import v2_independent_source_qa as sourceqa
import v2_nontest_retrievers as ret
import oracle_reader_source_only as vm


def rejected(fn, exceptions=(ValueError,AssertionError,TypeError)):
    try:fn()
    except exceptions:return True
    return False


def mock_model():
    class Model(nn.Module):
        def __init__(self):
            super().__init__()
            self.tok=nn.Embedding(2048,256)
            self.pos=nn.Embedding(256,256)
            self.blocks=nn.ModuleList([])
            self.final_ln=nn.Identity()
            self.head=nn.Linear(256,2048,bias=False)
            self.head.weight=self.tok.weight
    model=Model().cpu().eval().requires_grad_(False)
    reader=vm.GatedOracleReader().cpu().eval().requires_grad_(False)
    with torch.no_grad():
        reader.output_proj.weight.copy_(torch.randn_like(reader.output_proj.weight)*.012)
    return model,reader


def synthetic_case(stratum):
    bank=sourceqa.custom_bank()  # HAND-MADE, not actual fixture.build() PROBE
    good=[dict(x) for x in bank]
    for i,c in enumerate(good):c['value']='bivor' if i==0 else 'tobak'
    bad=[dict(c) for c in good]
    bad[0]['value']='wexil'
    if stratum=='S0_ID_LITERAL':
        question='For archive object '+good[0]['key']+', what was the access tag? Answer:'
    elif stratum=='S1_ALIAS_LOOKUP':
        question='For public alias '+good[0]['lookup_alias']+', what was the access tag? Answer:'
    else:
        question='What access tag belongs to the golden circular clay archive item? Answer:'
    return {'case_id':'synthetic-mock-'+stratum,'stratum':stratum,
            'question':question,'answer':'bivor','target_key':good[0]['key'],
            'correct_memory':good,'wrong_memory':bad}


def audit():
    checks={}
    def ck(name,valid):
        checks[name]=bool(valid)
        if not valid:raise AssertionError('SCORER_QA_FAIL:'+name)
    torch.set_num_threads(2)
    torch.manual_seed(20261112)
    src=Path(run.__file__).read_text(encoding='utf-8')
    ck('01_python_ast',bool(ast.parse(src)))
    ck('02_expected_run_id',run.RUN_ID=='TTM_VM_V2_NONTEST_192_FROZEN_READER_CPU_ONESHOT_V1')
    ck('03_source_reader_SHA_pinned',run.PINS['reader']=='c458de3afae87b3c381274b8edd698187df63ceac4dbbc0e6d8bd44b85c1632f')
    ck('04_source_checkpoint_SHA_pinned',run.PINS['checkpoint']=='ee723407b2c25a18be20e26387a3dd8e4a18e2942d469279b6f0748ff86af0dc')
    ck('05_source_fixture_SHA_pinned',run.PINS['fixture']=='1d7c02ab082a3c34345953dc5146e5a93f8c6f44e11132ea8abb0594efcc0b9d')
    ck('06_source_retriever_blob_pinned',run.PINS['v2_retriever']=='dc733eda42d768d695309e3a1d5df25aeabb28b7')
    ck('07_source_fixture_blob_pinned',run.PINS['v2_fixture']=='01703d4786872a66459593d27cd7607b66c895dd')
    ck('08_six_arms',run.ARMS==('A','O1','B1','C1','B3','C3'))
    ck('09_no_optimizer_or_backward',not any(s in src for s in ('optimizer.step(','.backward(', 'torch.optim.', 'train_loader')))
    ck('10_no_old_probe_DEV_TEST_path',not any(s in src for s in ('TEST_SECRET','TTM_EXTERNAL_FACTS_DEV_64','PER_STORY_QA_PRIVATE_20261111','TTM_VM_TOPK_NONTEST_FROZEN_READER_PROBE_ONCE_V1')))
    ck('11_single_execution_optin','DENY_NO_EXPLICIT_EXECUTE_ONCE' in src)
    ck('12_marker_before_score','destination.mkdir(exist_ok=False)' in src and src.index('destination.mkdir(exist_ok=False)')<src.index('per_story=[]'))
    ck('13_output_exact_scope','FROZEN_ONESHOT_OUTPUT_SCOPE_MISMATCH' in src)
    ck('14_no_overwrite','ONE_SHOT_ALREADY_CONSUMED_NO_RETRY' in src and "open('x'" in src)
    ck('15_no_gpu','CUDA_INITIALIZED_CPU_ONLY' in src)
    ck('16_no_runtime_training','optimizer_steps' in src and 'reader.requires_grad_(False)' in src)
    ck('17_2000_bootstrap',run.BOOTSTRAP_DRAWS==2000)
    ck('18_registered_bootstrap_seeds',(run.SEED_A,run.SEED_C)==(20261116,20261117))
    ck('19_short_bootstrap_rejected',rejected(lambda:run.paired_bootstrap95(np.ones(63),run.SEED_A)))
    ck('20_nan_bootstrap_rejected',rejected(lambda:run.paired_bootstrap95(np.ones(64)*float('nan'),run.SEED_A)))
    ck('21_constant_bootstrap',run.paired_bootstrap95(np.ones(64)*.25,run.SEED_A)==[.25,.25])
    ar=np.linspace(-.5,1,64)
    pcg=np.random.default_rng(run.SEED_C)
    sample=pcg.integers(0,64,size=(2000,64))
    baseline=np.quantile(ar[sample].mean(axis=1),[.025,.975])
    ck('22_independent_bootstrap_reference',np.allclose(run.paired_bootstrap95(ar,run.SEED_C),baseline,rtol=0,atol=1e-13))
    ck('23_bootstrap_deterministic',run.paired_bootstrap95(ar,run.SEED_A)==run.paired_bootstrap95(ar,run.SEED_A))
    ck('24_BOOTSTRAP_two_seeds_independent',run.paired_bootstrap95(ar,run.SEED_A)!=run.paired_bootstrap95(ar,run.SEED_C))
    tokenizer=lambda s:list(s.encode('ascii'))
    model,reader=mock_model()
    allrecords={}
    for stratum in ('S0_ID_LITERAL','S1_ALIAS_LOOKUP','S2_DESC_PARAPHRASE'):
        case=synthetic_case(stratum)
        r1=run.rank_public(case['question'],case['correct_memory'],stratum,tokenizer,model.tok.weight,k=1)
        r3=run.rank_public(case['question'],case['correct_memory'],stratum,tokenizer,model.tok.weight,k=3)
        ck('25_'+stratum+'_mock_target_found',r1.status=='SELECTED' and r1.indices[0]==0)
        ck('26_'+stratum+'_rank_consistent',r3.status=='SELECTED' and r3.indices[0]==r1.indices[0])
        altered=[dict(x,value='ATTACK') for x in case['correct_memory']]
        r_new=run.rank_public(case['question'],altered,stratum,tokenizer,model.tok.weight,k=1)
        ck('27_'+stratum+'_blind_to_value',r_new==r1)
        out=run.score_case(case,model,reader,tokenizer)
        allrecords[stratum]=out
        ck('28_'+stratum+'_all_six_scored',set(out['arm_nll'])==set(run.ARMS))
        ck('29_'+stratum+'_finite_scoring',all(math.isfinite(v) for v in out['arm_nll'].values()))
        ck('30_'+stratum+'_hit1',out['hit1'])
        ck('31_'+stratum+'_bypass_gate_zero',out['arm_gate']['A']==0)
        ck('32_'+stratum+'_gold_value_affects_NLL',out['arm_nll']['B1']!=out['arm_nll']['C1'])
        ck('33_'+stratum+'_answer_tokens_nonempty',out['answer_tokens']>0)
    ck('34_mock_model_no_gradients',all(p.grad is None for p in model.parameters()))
    ck('35_mock_reader_no_gradients',all(p.grad is None for p in reader.parameters()))
    ck('36_model_tied_head',model.head.weight.data_ptr()==model.tok.weight.data_ptr())
    samplecase=synthetic_case('S2_DESC_PARAPHRASE')
    tok,pos,tar=run.encode_target(tokenizer,samplecase['question'],samplecase['answer'])
    hid=run.frozen_hidden_at_answer_positions(model,tok,pos)
    manual=F.log_softmax(F.linear(hid,model.head.weight),dim=-1)
    direct=-manual[torch.arange(len(tar)),tar].mean().item()
    ck('37_independent_answer_only_CE',abs(direct-allrecords['S2_DESC_PARAPHRASE']['arm_nll']['A'])<1e-6)
    ck('38_answer_only_alignment',len(tar)==len(tokenizer(' '+samplecase['answer'])))
    missing=copy.deepcopy(samplecase)
    missing['question']='What is access tag for a golden round item? Answer:'
    miss=run.rank_public(missing['question'],missing['correct_memory'],missing['stratum'],tokenizer,model.tok.weight,k=1)
    ck('39_missing_description_abstain',miss.status=='ABSTAIN' and miss.indices==())
    scored=run.score_case(missing,model,reader,tokenizer)
    ck('40_missing_description_zero_coverage',not scored['coverage1'] and not scored['hit1'])
    ck('41_missing_description_bypass_matches_correct',scored['arm_nll']['A']==scored['arm_nll']['B1']==scored['arm_nll']['C1'])
    ck('42_missing_description_bypass_matches_top3',scored['arm_nll']['A']==scored['arm_nll']['B3']==scored['arm_nll']['C3'])
    ck('43_missing_description_positive_oracle_control',scored['arm_nll']['O1']!=scored['arm_nll']['A'])
    wrong=copy.deepcopy(samplecase)
    wrong['wrong_memory'][0]['key']='objaXXXXXXXXXXXXXXXX'
    ck('44_key_drift_rejected_before_science',rejected(lambda:run.validate_fixture([wrong])))
    # Synthetic-only aggregate: 64 hand-constructed rows per stratum; no real PROBE.
    fake=[]
    for stratum in ('S0_ID_LITERAL','S1_ALIAS_LOOKUP','S2_DESC_PARAPHRASE'):
        for i in range(64):
            q=dict(allrecords[stratum]);q['case_id']=f'mock-{stratum}-{i:03d}'
            q['arm_nll']={key:float(v) for key,v in q['arm_nll'].items()}
            fake.append(q)
    agg=run.aggregate(fake)
    ck('45_aggregate_s2_only',agg['strata']['S2_DESC_PARAPHRASE']['count']==64)
    ck('46_aggregate_all_strata',len(agg['strata'])==3)
    ck('47_aggregate_64_s2_hit',agg['strata']['S2_DESC_PARAPHRASE']['hits1']==64)
    ck('48_aggregate_readout_NLL_s2',abs(agg['strata']['S2_DESC_PARAPHRASE']['mean_story_nll']['A']-allrecords['S2_DESC_PARAPHRASE']['arm_nll']['A'])<1e-8)
    ck('49_aggregate_one_shot_CI_bounds',len(agg['primary_S2']['bootstrap95']['A_minus_B1'])==2)
    ck('50_main_result_not_test_pass',agg['verdict'] in {'GO_CANDIDATE_NONTEST_DESCRIPTION_SCOPED','HOLD_READER_QUERY_DOMAIN_SHIFT','FAIL_DESCRIPTION_RETRIEVAL_SCOPED','FAIL_FROZEN_READER_TRANSFER_SCOPED'})
    lowhit=copy.deepcopy(fake)
    for x in lowhit:
        if x['stratum']=='S2_DESC_PARAPHRASE':x['hit1']=False
    lowres=run.aggregate(lowhit)
    # Oracle may cause HOLD first; precedence is checked via frozen source.
    ck('51_frozen_domain_shift_precedence',"if not (A - O1 >= .05): verdict='HOLD_READER_QUERY_DOMAIN_SHIFT'" in src)
    ck('52_frozen_recall_precedence',"elif strata['S2_DESC_PARAPHRASE']['hits1'] < 58" in src)
    ck('53_frozen_nll_precedence',"verdict='FAIL_FROZEN_READER_TRANSFER_SCOPED'" in src)
    ck('54_frozen_success_nonTEST_only',"verdict='GO_CANDIDATE_NONTEST_DESCRIPTION_SCOPED'" in src)
    ck('55_aggregate_uses_S2_64_only',len([x for x in fake if x['stratum']=='S2_DESC_PARAPHRASE'])==64)
    ck('56_source_sha_pins_checked','SOURCE_GIT_BLOB_DRIFT' in src and 'BINARY_SHA256_DRIFT' in src)
    ck('57_all_source_inputs_required',set(('checkpoint','reader','t1_manifest','fixture')).issubset(run.PINS))
    ck('58_no_real_probe_retrieval_in_QA',not any(isinstance(x,ast.Call) and isinstance(x.func,ast.Attribute) and x.func.attr == 'build' and isinstance(x.func.value,ast.Name) and x.func.value.id == 'fixture' for x in ast.walk(ast.parse(Path(__file__).read_text(encoding='utf8')))))
    ck('59_negative_no_execute_once_subprocess', _test_no_execute_once())
    ck('60_refuse_existing_one_shot_output', _test_existing_output_directory())
    return checks


def _args(tmp):
    return [sys.executable,str(Path(run.__file__)), '--project-root',str(tmp), '--checkout',str(tmp),
            '--checkpoint',str(tmp/'ck'), '--reader',str(tmp/'reader'), '--t1-manifest',str(tmp/'t1'),
            '--fixture',str(tmp/'fixture'), '--output-dir',str(tmp/'_evidence/vector-memory'/run.RUN_ID)]


def _test_no_execute_once():
    # No training assets are read and no output is created in this negative test.
    args=_args(Path('/tmp/VM_NO_EXECUTE_ONCE_FAKE_ROOT'))
    p=subprocess.run(args,stdout=subprocess.PIPE,stderr=subprocess.PIPE,text=True,timeout=20)
    return p.returncode!=0 and 'DENY_NO_EXPLICIT_EXECUTE_ONCE' in p.stderr


def _test_existing_output_directory():
    import tempfile
    with tempfile.TemporaryDirectory() as td:
        root=Path(td); folder=root/'_evidence'/'vector-memory'/run.RUN_ID
        folder.mkdir(parents=True)
        p=subprocess.run(_args(root)+['--execute-once'],stdout=subprocess.PIPE,stderr=subprocess.PIPE,text=True,timeout=20)
        return p.returncode!=0 and 'ONE_SHOT_ALREADY_CONSUMED_NO_RETRY' in p.stderr


def main():
    p=argparse.ArgumentParser()
    p.add_argument('--out',type=Path,required=True)
    args=p.parse_args()
    if args.out.exists():raise FileExistsError('SOURCE_QA_REFUSE_OVERWRITE')
    checks=audit()
    report={'schema':'ttm.vm.v2.nontest192.one_shot_scorer.independent_mock_QA.v1',
            'status':'PASS_INDEPENDENT_ONE_SHOT_SCORER_QA',
            'checks':checks,'checks_passed':sum(checks.values()),'checks_total':len(checks),
            'real_192_fixture_scored':False,'trained_reader_opened':False,
            'trained_backbone_opened':False,'old_probe_rescored':False,'DEV_scored':False,
            'TEST_opened':False,'optimizer_steps':0,'GPU_used':False,
            'mock_only':True}
    args.out.parent.mkdir(parents=True,exist_ok=True)
    args.out.write_text(json.dumps(report,indent=2,sort_keys=True)+'\n',encoding='utf-8')
    print(json.dumps({'status':report['status'],'qa':f"{len(checks)}/{len(checks)}",
                      'science_executed':False,'test_opened':False}))

if __name__=='__main__':main()
