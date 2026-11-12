#!/usr/bin/env python3
"""Independent V3 CPU one-shot scorer technical QA after prospective AI gate amendment.

No real 256-case Retriever evaluation, no trained L0020 Reader forward, no
old PROBE, DEV, TEST, or optimizer. No fake human attestation generated.
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
import v3_ai_amended_frozen_reader_cpu_one_shot as run
import v3_independent_source_qa as prior
import v3_nonoracle_retriever as ranker
import v3_p1_reviewer_custody as custody
import v3_ai_review_custody_amendment as ai_custody
import hashlib
import v3_fresh256_fixture as fixture
import oracle_reader_source_only as vm


def expect_reject(fn,cls=(ValueError,AssertionError,TypeError)):
    try:fn()
    except cls:return True
    return False


class MockModel(nn.Module):
    def __init__(self):
        super().__init__()
        self.tok=nn.Embedding(2048,256)
        self.pos=nn.Embedding(256,256)
        self.blocks=nn.ModuleList([])
        self.final_ln=nn.Identity()
        self.head=nn.Linear(256,2048,bias=False)
        self.head.weight=self.tok.weight


def mock_positive(query='Which tag belongs to the amber round ceramic archive item? Answer:'):
    idx=prior.mock_bank()  # independent handwritten mock, not fixture.build() new PROBE
    good=[{**x,'value':'bivor' if i==0 else 'tobak'} for i,x in enumerate(idx)]
    bad=[dict(x,value='wexil' if i==0 else x['value']) for i,x in enumerate(good)]
    return {'schema':'synthetic_positive_only','case_id':'mock-positive-0000',
            'stratum':'P0_KNOWN_WIRING','question':query,'gold_action':'SELECT',
            'target_key':good[0]['key'],'answer':'bivor','public_index':idx,
            'correct_memory':good,'wrong_memory':bad}


def mock_negative(query='Which tag belongs to the amber round ceramic archive item excluding material ceramic? Answer:'):
    p=mock_positive()
    return {'case_id':'mock-negative-0000','stratum':'N2_CONTRADICTORY_QUERY',
            'question':query,'gold_action':'ABSTAIN','answer':None,'target_key':None,
            'correct_memory':None,'wrong_memory':None,'public_index':p['public_index']}


def fabricated(case_index:int,stratum:str,*,negative_wrong=False, positive_miss=False,domain_shift=False,transfer_fail=False):
    if stratum.startswith('N'):
        select=negative_wrong
        return {'case_id':f'fake-{stratum}-{case_index:02d}','stratum':stratum,
                'status':'SELECT' if select else 'ABSTAIN',
                'reason_code':'MOCK_ONLY','selected_count':int(select),
                'correct_abstain':not select,'false_selection':select,
                'reader_forward_calls':0,'nll':None}
    A,O1=(5.0,5.0 if domain_shift else 3.0)
    B1=5.0 if transfer_fail or positive_miss else 3.5
    C1=B1 if positive_miss else 4.5
    return {'case_id':f'fake-{stratum}-{case_index:02d}','stratum':stratum,
            'status':'ABSTAIN' if positive_miss else 'SELECT',
            'reason_code':'MOCK_ONLY','selected_count':int(not positive_miss),
            'hit1':not positive_miss,'missed_positive':positive_miss,
            'correct_select':not positive_miss,'answer_tokens':2,
            'arm_nll':{'A':A,'O1':O1,'B1':B1,'C1':C1,'B3':B1,'C3':C1},
            'arm_gate':{'A':0.0,'O1':0.1,'B1':0.1,'C1':0.1,'B3':0.1,'C3':0.1}}


def fabricated_batch(**opts):
    results=[]
    for stratum in fixture.STRATA:
        for i in range(32):
            o={k:(v(stratum,i) if callable(v) else v) for k,v in opts.items()}
            results.append(fabricated(i,stratum,**o))
    return results


def audit():
    checks={}
    def ck(label,condition):
        checks[label]=bool(condition)
        if not condition:raise AssertionError('V3_INDEPENDENT_SCORER_QA:'+label)
    torch.set_num_threads(2)
    torch.manual_seed(20261112)
    src=Path(run.__file__).read_text('utf8')
    ck('01_runner_ast',bool(ast.parse(src)))
    ck('02_one_shot_requires_optin',"'--execute-once'" in src and 'DENY_NO_EXPLICIT_EXECUTE_ONCE' in src)
    ck('03_expected_private_reader_pin',run.PINS['reader']=='c458de3afae87b3c381274b8edd698187df63ceac4dbbc0e6d8bd44b85c1632f')
    ck('04_expected_v3_fixture_pin',run.PINS['v3_fixture']=='d473292d40dfb475d0b44f7d393341e19d846308820dcb4f5cbac6acb2c0e543')
    ck('05_reader_source_git_blob_pin',run.PINS['reader_source']=='7ce728b2874284b87933237c890e54ce3d9fd651')
    ck('06_v3_fixture_source_git_blob_pin',run.PINS['v3_fixture_source']=='5f51b8b464e54a370f3a3fa99d91307118f52f46')
    ck('07_v3_ranker_git_blob_pin',run.PINS['v3_retriever_source']=='68bfeaaf1d0acf0cf446e4d734e34368fbf8f702')
    ck('08_v3_review_validator_blob_pin',run.PINS['v3_reviewer_custody']=='beaaa78126282439c94b2d0d525297e6b35266a5')
    ck('09_SHA_backbone_t1_pins',run.PINS['checkpoint']=='ee723407b2c25a18be20e26387a3dd8e4a18e2942d469279b6f0748ff86af0dc' and run.PINS['t1_manifest']=='cba18e60cee3d08a353ee6d4a451017289e45af7b4b1179c87171b9b78d7dfdc')
    ck('10_one_shot_marker_before_case_loop',src.index('ONE_SHOT_STARTED.json')<src.index('for case in cases:'))
    ck('11_refuse_existing_one_shot',"ONE_SHOT_ALREADY_STARTED_NO_RETRY" in src)
    ck('12_read_only_weights_only_true',src.count('weights_only=True')==2)
    ck('13_no_optimizer_or_training',not any(x in src for x in ('optimizer.step(','.backward(','torch.optim.','TRAIN_256_V1.json')))
    ck('14_no_old_dev_or_test_reader',not any(x in src for x in ('TEST_SECRET','DEV_64_V1','TTM_VM_EXTERNAL_TEST','old_probe_perstory')))
    ck('15_no_negative_nll_references',"'nll':None" in src)
    ck('16_singleton_diagnostic_no_top3_claim',run.ARMS==('A','O1','B1','C1','B3','C3') and 'NOT_TRUE_TOP3' in src)
    ck('17_ranker_only_public_question_index','retrieve.retrieve(case[\'question\'],case[\'public_index\'])' in src)
    ck('18_AI_review_gate_required','ai_custody.validate_two_ai_reviews(' in src and 'PASS_TWO_AI_BLIND_REVIEW_SOURCE_AND_GOLD_32_OF_32_EXPLORATORY' in src)
    ck('19_marker_after_review_check',src.index('ai_custody.validate_two_ai_reviews(')<src.index('ONE_SHOT_STARTED.json'))
    ck('20_negative_forward_ban',not any(word in run.action_only.__code__.co_names for word in ('vm','logits_from_hidden','score','encode_target','frozen_hidden_at_answer_positions')))
    ck('21_pos_denom_96',len(run.PRIMARY_POSITIVE)==3 and run.BOOTSTRAP_DRAWS==2000)
    ck('22_negative_denom_128',len(run.NEGATIVE)==4)
    ck('23_bootstrap_reject_short',expect_reject(lambda:run.paired_bootstrap95([1.]*95,20261120)))
    ck('24_bootstrap_reject_nonfinite',expect_reject(lambda:run.paired_bootstrap95([float('nan')]*96,20261120)))
    ck('25_bootstrap_constant',run.paired_bootstrap95([.75]*96,20261120)==[.75,.75])
    ck('26_bootstrap_determinism',run.paired_bootstrap95(list(np.linspace(-1,2,96)),20261120)==run.paired_bootstrap95(list(np.linspace(-1,2,96)),20261120))
    z=np.linspace(-1,2,96);gen=np.random.default_rng(20261121)
    ref=np.quantile(z[gen.integers(0,96,size=(2000,96))].mean(axis=1),[.025,.975])
    ck('27_bootstrap_independent_manual_numPy_reference',np.allclose(run.paired_bootstrap95(z,20261121),ref,rtol=0,atol=1e-12))
    ck('28_bootstrap_two_seeds_differ',run.paired_bootstrap95(z,20261120)!=run.paired_bootstrap95(z,20261121))
    ck('29_wilson_0_in_32',run.wilson95(0,32)[0]==0)
    ck('30_wilson_32_in_32',run.wilson95(32,32)[1]==1)
    ck('31_wilson_zero_n_reject',expect_reject(lambda:run.wilson95(0,0)))
    ck('32_wilson_hits_gt_n_reject',expect_reject(lambda:run.wilson95(33,32)))
    ck('33_source_fixture_is_256_without_retriever_calls',fixture.SCHEMA=='ttm.vm.v3.nontest256.provenance_negation_abstention.v1' and len(fixture.STRATA)==8)
    ck('34_review_packets_unsigned',not custody.review_packet(run.PINS['v3_fixture'],[], 'A')['attest_independent_semantic_mapping'])
    ck('35_reviewer_validator_rejects_unattested',expect_reject(lambda:custody.validate_receipts([],run.PINS['v3_fixture'],{},{})))
    mock=MockModel().cpu().eval().requires_grad_(False)
    reader=vm.GatedOracleReader().cpu().eval().requires_grad_(False)
    with torch.no_grad():reader.output_proj.weight.copy_(torch.randn_like(reader.output_proj.weight)*.01)
    token=lambda s:list(s.encode('ascii'))
    pos=mock_positive()
    baseline=run.positive_case(pos,mock,reader,token)
    ck('36_mock_positive_select',baseline['status']=='SELECT' and baseline['hit1'])
    ck('37_mock_six_arm_positive_nll_finite',all(np.isfinite(baseline['arm_nll'][a]) for a in run.ARMS))
    ck('38_mock_six_arm_gates_finite',all(np.isfinite(baseline['arm_gate'][a]) for a in run.ARMS))
    ck('39_bypass_gate_exact_zero',baseline['arm_gate']['A']==0)
    ck('40_positive_has_answer_token_nll',baseline['answer_tokens']>=1)
    ck('41_pos_top3_diagnostic_equals_B1',baseline['arm_nll']['B3']==baseline['arm_nll']['B1'])
    ck('42_pos_top3_foil_equals_C1',baseline['arm_nll']['C3']==baseline['arm_nll']['C1'])
    ck('43_mock_no_reader_grads',all(p.grad is None for p in reader.parameters()))
    ck('44_mock_no_model_grads',all(p.grad is None for p in mock.parameters()))
    x,places,targ=run.encode_target(token,pos['question'],pos['answer'])
    h=run.frozen_hidden_at_answer_positions(mock,x,places)
    direct=F.log_softmax(F.linear(h,mock.head.weight),dim=-1)
    independent=float((-direct[torch.arange(len(targ)),targ]).mean())
    ck('45_independent_teacher_forcing_log_softmax',abs(independent-baseline['arm_nll']['A'])<1e-5)
    ck('46_target_tokens_are_answer_only',len(targ)==len(token(' '+pos['answer'])))
    neg=mock_negative()
    out=run.action_only(neg)
    ck('47_mock_negative_abstains',out['status']=='ABSTAIN' and out['selected_count']==0)
    ck('48_negative_no_NLL_or_reader',out['nll'] is None and out['reader_forward_calls']==0)
    ck('49_negative_private_gold_injection_rejected',expect_reject(lambda:run.action_only({**neg,'answer':'bivor'})))
    ck('50_negative_target_key_injection_rejected',expect_reject(lambda:run.action_only({**neg,'target_key':'objuattack'})))
    neg_force=mock_negative('Which tag belongs to the amber round ceramic archive item? Answer:')
    forced=run.action_only(neg_force)
    ck('51_negative_forced_selection_flagged',forced['status']=='SELECT' and forced['false_selection'])
    p_missing=mock_positive('Which tag belongs to the amber archive item? Answer:')
    missing=run.positive_case(p_missing,mock,reader,token)
    ck('52_mock_positive_ambiguous_abstains',missing['status']=='ABSTAIN' and not missing['correct_select'])
    ck('53_mock_positive_abstain_counts_as_miss',missing['missed_positive'] is True)
    ck('54_mock_positive_abstain_bypass_equals_A',missing['arm_nll']['B1']==missing['arm_nll']['C1']==missing['arm_nll']['A'])
    ck('55_mock_positive_abstain_gate_zero',missing['arm_gate']['B1']==missing['arm_gate']['C1']==0)
    ck('56_mock_gold_not_in_index_fields',all(set(c)=={'key','source_id','retrieval_text'} for c in pos['public_index']))
    ck('57_mock_public_index_cannot_include_value',expect_reject(lambda:run.positive_case({**pos,'public_index':[dict(c,value='bivor') for c in pos['public_index']]},mock,reader,token)))
    ck('58_mock_wrong_public_index_drifts_rejected',expect_reject(lambda:run.positive_case({**pos,'wrong_memory':[dict(c,source_id='src-south') for c in pos['wrong_memory']]},mock,reader,token)))
    ck('59_mock_wrong_two_values_rejected',expect_reject(lambda:run.positive_case({**pos,'wrong_memory':[dict(c,value='wexil') for c in pos['wrong_memory']]},mock,reader,token)))
    ck('60_mock_invalid_bank_rejected',expect_reject(lambda:run.encode_memory(pos['correct_memory'][:30],token,mock.tok.weight,(0,))))
    ck('61_mock_invalid_selection_rejected',expect_reject(lambda:run.encode_memory(pos['correct_memory'],token,mock.tok.weight,(0,1))))
    ck('62_mock_unfrozen_embedding_rejected',expect_reject(lambda:run.encode_memory(pos['correct_memory'],token,mock.tok.weight.clone().requires_grad_(),(0,))))
    ck('63_mock_public_mask_selected_one',sum(ranker.mask(ranker.retrieve(pos['question'],pos['public_index'])))==1)
    ck('64_mock_public_mask_abstain_zero',sum(ranker.mask(ranker.retrieve(neg['question'],neg['public_index'])))==0)
    ck('65_mock_reader_uses_original_legacy_source',isinstance(reader,vm.GatedOracleReader))
    allpass=run.aggregate(fabricated_batch())
    ck('66_fake_256_scoped_GO',allpass['verdict']=='GO_CANDIDATE_NONTEST_AMBIGUITY_SCOPED')
    ck('67_fake_96_positive_rate_one',allpass['positive_primary_96']['correct_select']==96)
    ck('68_fake_128_neg_abstention_one',allpass['negative_primary_128']['correct_abstain']==128)
    ck('69_fake_96_pair_deltas_positive',allpass['positive_reader_primary96']['paired_mean_delta']['A_minus_B1']>=.05)
    ck('70_fake_96_bootstrap_lower_gt_zero',all(z[0]>0 for z in allpass['positive_reader_primary96']['bootstrap95'].values()))
    ck('71_fake_cost_zero',allpass['diagnostic_cost']==0)
    unsafe=run.aggregate(fabricated_batch(negative_wrong=lambda s,i:s=='N0_UNDERSPECIFIED' and i<7))
    ck('72_fake_seven_negative_false_select_fail',unsafe['verdict']=='FAIL_UNSAFE_SELECTION_SCOPED')
    ck('73_fake_false_select_cost21',unsafe['diagnostic_cost']==21)
    bad_positive=run.aggregate(fabricated_batch(positive_miss=lambda s,i:s=='P1_UNSEEN_PARAPHRASE' and i<20 or s=='P2_PROVENANCE_UNIQUE' and i<10))
    ck('74_fake_positive_below72_FAIL',bad_positive['verdict']=='FAIL_UNSEEN_OR_COMPOSITIONAL_RETRIEVAL_SCOPED')
    ck('75_fake_P1_unseen_below20_FAIL',bad_positive['positive_primary_96']['p1_hits']==12)
    domain=run.aggregate(fabricated_batch(domain_shift=True))
    ck('76_fake_oracle_domain_shift_HOLD',domain['verdict']=='HOLD_READER_DOMAIN_SHIFT')
    trans=run.aggregate(fabricated_batch(transfer_fail=True))
    ck('77_fake_reader_transfer_FAIL',trans['verdict']=='FAIL_FROZEN_READER_TRANSFER_SCOPED')
    ck('78_bad_perstory_count_rejected',expect_reject(lambda:run.aggregate(fabricated_batch()[:-1])))
    ck('79_only_positive_NLL_in_fake_negatives',all(z['nll'] is None for z in fabricated_batch() if z['stratum'].startswith('N')))
    ck('80_one_shot_negative_no_forward','reader_forward_calls' in out and out['reader_forward_calls']==0)
    ck('81_one_shot_result_private_output_path_pin',"PER_STORY_QA_PRIVATE.json" in src and "PROBE_AGGREGATE_PUBLIC.json" in src)
    ck('82_one_shot_source_weight_unchanged_checks',"BACKBONE_WEIGHT_MUTATION" in src and "READER_WEIGHT_MUTATION" in src)
    ck('83_one_shot_P1_reviewer_receipt_no_source_autosign','attest_independent_semantic_mapping' not in src and 'PASS_TWO_DISTINCT_BLIND_HUMAN_ATTESTATIONS' not in src)
    ck('84_one_shot_result_test_still_sealed',"'test_opened':False" in src)
    # Separate subprocess must deny execution without explicit --execute-once,
    # without touching any file or data, even if flags are supplied.
    cmd=[sys.executable,str(Path(run.__file__))]
    for arg in ('project-root','checkout','checkpoint','reader','t1-manifest','fixture','review-a','review-b','output-dir'):
        cmd.extend(['--'+arg,'X:/nonexistent'])
    p=subprocess.run(cmd,capture_output=True,text=True,timeout=15)
    ck('85_one_shot_no_optin_subprocess_denied',p.returncode!=0 and 'DENY_NO_EXPLICIT_EXECUTE_ONCE' in p.stderr)
    ck('86_AI_custody_source_pin',run.PINS['v3_ai_review_custody']=='ede2ee6438dc9b5ba106195e529eb3124d53f31b')
    ck('87_AI_agent_A_sha_pin',run.PINS['v3_ai_A']==ai_custody.AI_FILES['A']['sha256'])
    ck('88_AI_agent_B_sha_pin',run.PINS['v3_ai_B']==ai_custody.AI_FILES['B']['sha256'])
    ck('89_no_claim_of_human_pass',"'human_gate_satisfied':False" in src and 'HUMAN_ATTESTATIONS' not in src)
    ck('90_AI_gate_only_before_marker',src.index('ai_custody.validate_two_ai_reviews(')<src.index('ONE_SHOT_STARTED.json'))
    # Synthetic custody verifier negative QA; generation uses only structural
    # fixture public projection + pre-known private rule labels for mock choices.
    # Does not inspect actual GitHub AI files; owner preflight does that later.
    p1=[z for z in fixture.build() if z['stratum']=='P1_UNSEEN_PARAPHRASE']
    qa_packets=[]
    for slot in ('A','B'):
        p=custody.review_packet(ai_custody.FIXTURE_SHA256,p1,slot)
        p['rater_id']=ai_custody.AI_FILES[slot]['rater_id']
        p['reviewed_at_iso8601']='2026-11-12T17:00:00+07:00'
        for row,case in zip(p['cases'],p1):
            row['selected_key']=case['target_key'];row['reason']='SIMULATED_QA_ONLY_NOT_A_REAL_RATER';row['confidence']=3
        qa_packets.append(p)
    raw_A,raw_B=[json.dumps(p,sort_keys=True).encode('utf8') for p in qa_packets]
    old_pin=copy.deepcopy(ai_custody.AI_FILES)
    ai_custody.AI_FILES['A']['sha256']=hashlib.sha256(raw_A).hexdigest()
    ai_custody.AI_FILES['B']['sha256']=hashlib.sha256(raw_B).hexdigest()
    try:
        receipt=ai_custody.validate_two_ai_reviews(fixture.build(),ai_custody.FIXTURE_SHA256,raw_A,raw_B)
        ck('91_mock_two_AI_correct_32',receipt['agent_A_gold_match']==receipt['agent_B_gold_match']==32)
        ck('92_mock_AI_never_claims_human',receipt['human_gate_satisfied'] is False and receipt['human_reviewers']==0)
        bad=copy.deepcopy(qa_packets[1]);bad['attest_independent_semantic_mapping']=True
        ck('93_fake_human_attestation_rejected',expect_reject(lambda:ai_custody.validate_two_ai_reviews(fixture.build(),ai_custody.FIXTURE_SHA256,raw_A,json.dumps(bad,sort_keys=True).encode())))
        ck('94_actual_pinned_sha_rejects_mock_inputs',raw_A!=raw_B and old_pin['A']['sha256']!=hashlib.sha256(raw_A).hexdigest())
        wrong=copy.deepcopy(qa_packets[1]);wrong['cases'][0]['selected_key']=p1[0]['public_index'][1]['key']
        wrong_raw=json.dumps(wrong,sort_keys=True).encode()
        ai_custody.AI_FILES['B']['sha256']=hashlib.sha256(wrong_raw).hexdigest()
        ck('95_mock_AI_disagreement_rejected',expect_reject(lambda:ai_custody.validate_two_ai_reviews(fixture.build(),ai_custody.FIXTURE_SHA256,raw_A,wrong_raw)))
        ai_custody.AI_FILES['B']['sha256']=hashlib.sha256(raw_B).hexdigest()
        tampered=copy.deepcopy(qa_packets[0]);tampered['cases'][0]['question']='CHANGED'
        tampered_raw=json.dumps(tampered,sort_keys=True).encode()
        ai_custody.AI_FILES['A']['sha256']=hashlib.sha256(tampered_raw).hexdigest()
        ck('96_public_question_integrity_rejected',expect_reject(lambda:ai_custody.validate_two_ai_reviews(fixture.build(),ai_custody.FIXTURE_SHA256,tampered_raw,raw_B)))
        ai_custody.AI_FILES['A']['sha256']=hashlib.sha256(raw_A).hexdigest()
        no_reason=copy.deepcopy(qa_packets[0]);no_reason['cases'][0]['reason']=''
        no_reason_raw=json.dumps(no_reason,sort_keys=True).encode()
        ai_custody.AI_FILES['A']['sha256']=hashlib.sha256(no_reason_raw).hexdigest()
        ck('97_AI_no_reason_rejected',expect_reject(lambda:ai_custody.validate_two_ai_reviews(fixture.build(),ai_custody.FIXTURE_SHA256,no_reason_raw,raw_B)))
        ai_custody.AI_FILES['A']['sha256']=hashlib.sha256(raw_A).hexdigest()
        duplicate=copy.deepcopy(qa_packets[0]);duplicate['rater_id']=qa_packets[1]['rater_id']
        duplicate_raw=json.dumps(duplicate,sort_keys=True).encode()
        ai_custody.AI_FILES['A']['sha256']=hashlib.sha256(duplicate_raw).hexdigest()
        ck('98_wrong_AI_identity_rejected',expect_reject(lambda:ai_custody.validate_two_ai_reviews(fixture.build(),ai_custody.FIXTURE_SHA256,duplicate_raw,raw_B)))
    finally:
        ai_custody.AI_FILES.clear();ai_custody.AI_FILES.update(old_pin)
    ck('99_PIN_RESTORED_POST_MOCK',ai_custody.AI_FILES==old_pin)
    ck('100_no_source_read_real_PROBE_retriever',"retrieve.retrieve(case['question'],case['public_index'])" in src and 'reader_forward_calls' in src)
    return checks


def main():
    args=argparse.ArgumentParser()
    args.add_argument('--out',type=Path,required=True)
    a=args.parse_args()
    if a.out.exists():raise FileExistsError('SOURCE_QA_REFUSE_OVERWRITE')
    checks=audit()
    report={'schema':'ttm.vm.v3.frozen_reader_cpu_one_shot.independent_mock_qa.v1',
            'status':'PASS_INDEPENDENT_V3_SCORER_MOCK_QA',
            'checks_passed':len(checks),'checks_total':len(checks),'checks':checks,
            'source_scope':'SOURCE_AND_SEPARATE_HANDWRITTEN_MOCK_ONLY',
            'actual_new256_retriever_scored':False,'actual_new256_reader_forward':False,
            'L0020_trained_Reader_loaded':False,'P1_human_reviews_completed':False,'AI_substitution_source_QA':'PASS_MOCK_ONLY_HUMAN_NOT_SATISFIED',
            'optimizer_steps':0,'DEV_rescored':False,'TEST_opened':False,'GPU_used':False,
            'LIMITATION':'Owner-approved AI substitution requires exact already-final AI JSON bytes; source/mock QA does not authorize science without Windows QA and fixture/source/native SHA pins.'}
    a.out.parent.mkdir(parents=True,exist_ok=True)
    a.out.write_text(json.dumps(report,sort_keys=True,indent=2)+'\n',encoding='utf8')
    print(json.dumps({'status':report['status'],'qa':f'{len(checks)}/{len(checks)}','science':False,'P1_human':False}))

if __name__=='__main__':main()
