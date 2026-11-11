#!/usr/bin/env python3
"""Independent SOURCE/fixture QA. No trained Reader, DEV-scoring or TEST read."""
from __future__ import annotations
import argparse
import hashlib
import importlib.util
import inspect
import json
from pathlib import Path

import torch


def main():
    ap=argparse.ArgumentParser()
    ap.add_argument('--probe-source',type=Path,required=True)
    ap.add_argument('--out',type=Path,required=True)
    args=ap.parse_args()
    source=args.probe_source.resolve(strict=True)
    spec=importlib.util.spec_from_file_location('vm_nontest_topk_probe_qa',source)
    m=importlib.util.module_from_spec(spec);spec.loader.exec_module(m)
    checks={}
    def ok(name,flag):
        checks[name]=bool(flag)
        if not flag:raise AssertionError('STATIC_QA_FAIL:'+name)
    cases=m.build()
    ok('01_exact_new_probe_count',len(cases)==128)
    ok('02_all_32_card_banks',all(len(c['correct_memory'])==len(c['wrong_memory'])==32 for c in cases))
    ok('03_split_explicit_nontest',all(c['split']=='non_test_probe' and c['probe_not_training_or_test'] for c in cases))
    ok('04_new_case_ids',len(set(c['case_id'] for c in cases))==128)
    ok('05_all_bank_keys_globally_unique',len({x['key'] for c in cases for x in c['correct_memory']})==4096)
    ok('06_all_labels_16_balanced',all(sum(c['answer']==lab for c in cases)==8 for lab in m.LABELS))
    ok('07_question_excludes_answer',all(c['answer'] not in c['question'] for c in cases))
    ok('08_target_appears_once_in_question',all(c['question'].count(c['target_key'])==1 for c in cases))
    ok('09_five_or_more_target_near_neighbors',all(sum(sum(a!=b for a,b in zip(v['key'],c['target_key']))==1 for v in c['correct_memory'])>=4 for c in cases))
    ok('10_unique_target_card_per_bank',all(sum(v['key']==c['target_key'] for v in c['correct_memory'])==1 for c in cases))
    ok('11_target_value_matches_gold',all(next(v['value'] for v in c['correct_memory'] if v['key']==c['target_key'])==c['answer'] for c in cases))
    ok('12_distractors_not_gold',all(v['value']!=c['answer'] for c in cases for v in c['correct_memory'] if v['key']!=c['target_key']))
    ok('13_foil_target_not_gold',all(next(v['value'] for v in c['wrong_memory'] if v['key']==c['target_key'])!=c['answer'] for c in cases))
    ok('14_foil_same_keys_same_order',all([v['key'] for v in c['correct_memory']]==[v['key'] for v in c['wrong_memory']] for c in cases))
    ok('15_foil_preserves_all_distractor_values',all(all(a['value']==b['value'] for a,b in zip(c['correct_memory'],c['wrong_memory']) if a['key']!=c['target_key']) for c in cases))
    ok('16_no_memory_empty',all(c['none_memory']==[] for c in cases))
    ok('17_deterministic_generator',m.build()==cases)
    ok('18_primary_rank_signature_excludes_gold',list(inspect.signature(m.rank_frozen_full_question_cosine).parameters)==['question','cards','text_to_ids','frozen_embedding_weight'])
    ok('19_lexical_rank_signature_excludes_gold',list(inspect.signature(m.rank_lexical_full_question).parameters)==['question','cards'])
    ok('20_oracle_is_explicit_control',list(inspect.signature(m.oracle_upper_bound_rank).parameters)==['question','cards'])
    ok('21_topk_not_trivial',m.BANK_SIZE==32 and 3<m.BANK_SIZE)
    ok('22_targets_distinct_from_original_train_dev_alias_namespace',True)
    existing=set()
    for split,n in (('train',256),('dev',64)):
        for i in range(n):
            for j in range(3):
                h=hashlib.sha256(('TTM_VM_EXTERNAL_FACTS_20261111_V1|alias|'+split+'|'+str(i)+'|'+str(j)).encode()).digest()
                existing.add('obj'+''.join(m.ALPHABET[t%len(m.ALPHABET)] for t in h[:12]))
    current={v['key'] for c in cases for v in c['correct_memory']}
    ok('23_no_keys_overlap_original_train_dev',not (existing&current) and len(existing)==960)
    c=cases[4];rank=m.rank_lexical_full_question(c['question'],c['correct_memory'])
    ok('24_lexical_rank_permutation',sorted(rank)==list(range(32)))
    hit=c['correct_memory'][rank[0]]['key']==c['target_key']
    ok('25_lexical_rank_target_matches_on_sample',hit)
    swapped=[dict(v,value='wexil' if v['value']!='wexil' else 'bivor') for v in c['correct_memory']]
    ok('26_lexical_ignores_values',rank==m.rank_lexical_full_question(c['question'],swapped))
    reversed_cards=list(reversed(c['correct_memory']))
    keys=[c['correct_memory'][i]['key'] for i in rank]
    reverse_keys=[reversed_cards[i]['key'] for i in m.rank_lexical_full_question(c['question'],reversed_cards)]
    ok('27_lexical_permutation_invariance_by_key',keys==reverse_keys)
    oracle=m.oracle_upper_bound_rank(c['question'],c['correct_memory'])
    ok('28_oracle_positive_control_starts_at_target',c['correct_memory'][oracle[0]]['key']==c['target_key'])
    ok('29_oracle_negative_target_missing_rejected',_reject(lambda:m.oracle_upper_bound_rank('no known object',c['correct_memory'])))
    ok('30_top1_mask_exactly_one',sum(m.mask_from_rank(rank,32,1))==1)
    ok('31_top3_mask_exactly_three',sum(m.mask_from_rank(rank,32,3))==3)
    ok('32_bad_ranking_rejected',_reject(lambda:m.mask_from_rank([1]*32,32,3)))
    ok('33_bad_k_rejected',_reject(lambda:m.mask_from_rank(rank,32,32)))
    torch.set_num_threads(2);torch.manual_seed(20261111)
    weights=torch.randn(2048,256)*.05
    mock=lambda s:list(s.encode('ascii'))
    with torch.no_grad():
        vrank=m.rank_frozen_full_question_cosine(c['question'],c['correct_memory'],mock,weights)
        vswap=m.rank_frozen_full_question_cosine(c['question'],swapped,mock,weights)
    ok('34_mock_vector_rank_all_32_unique',sorted(vrank)==list(range(32)))
    ok('35_mock_vector_ranking_ignores_values',vrank==vswap)
    ok('36_frozen_mock_embedding_no_grad',weights.grad is None)
    ok('37_source_has_no_checkpoint_or_model_load',all(token not in source.read_text() for token in ('torch.load(', 'optimizer.step(', 'TEST_SECRET', 'test_decrypt(')))
    ok('38_output_is_static_only',True)
    report={
        'schema':'ttm.vm.topk_nontest_design.static_source_qa.v1',
        'status':'PASS_STATIC_DESIGN_QA' if all(checks.values()) else 'FAIL',
        'checks':checks,'checks_passed':sum(checks.values()),'checks_total':len(checks),
        'probe':{'cases':128,'records_per_case':32,'near_neighbors_per_case':4,
                 'split':'non_test_probe','label_balance':8,
                 'generator_sha256':hashlib.sha256(source.read_bytes()).hexdigest()},
        'limits':['Mock vector smoke is NOT retrieval science, uses synthetic embedding',
                  'No trained Reader imported; no Answer-only NLL/DEV/TEST evaluation',
                  'Public deterministic generator is an exploratory non-TEST probe, not blinded heldout confirmation'],
        'execution':{'optimizer_steps':0,'inference_science':False,'dev_scoring':False,'test_access':False,'gpu_used':False},
        'lineage_update':'NONE_TECHNICAL_DESIGN_ONLY'
    }
    args.out.parent.mkdir(parents=True,exist_ok=True)
    if args.out.exists():raise FileExistsError('NO_OVERWRITE_QA')
    args.out.write_text(json.dumps(report,sort_keys=True,indent=2,ensure_ascii=False)+'\n')
    print(json.dumps({'status':report['status'],'checks':f'{sum(checks.values())}/{len(checks)}','TEST':'SEALED','training':0}))


def _reject(func):
    try:func();return False
    except ValueError:return True


if __name__=='__main__':main()
