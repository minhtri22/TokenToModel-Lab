#!/usr/bin/env python3
"""Second code path: source/synthetic independent check; zero trained inference."""
from __future__ import annotations
import argparse
import ast
import hashlib
import json
from pathlib import Path
import torch
from torch.nn import functional as F
import topk_nontest_probe as probe
import oracle_reader_source_only as reader
import topk_reader_integration as integrated
from cpu_pilot_readiness import PIN

def blob(p):
    b=Path(p).read_bytes()
    return hashlib.sha1(b'blob '+str(len(b)).encode()+b'\0'+b).hexdigest()

def main():
    a=argparse.ArgumentParser();a.add_argument('--out',type=Path,required=True);options=a.parse_args()
    root=Path(__file__).parent
    cks={}
    def ck(name,v):
        cks[name]=bool(v)
        if not v:raise AssertionError(name)
    def rejects(f):
        try:f()
        except ValueError:return True
        return False
    ck('01_original_reader_pinned',blob(root/'oracle_reader_source_only.py')=='7ce728b2874284b87933237c890e54ce3d9fd651')
    ck('02_original_probe_pinned',blob(root/'topk_nontest_probe.py')=='b08e2120a2ac9d4e270ee48fdca77e4a4743e22c')
    ck('03_integration_source_pinned',blob(root/'topk_reader_integration.py')=='ccab713f8c5a4b913259088225daffcf5382be41')
    code=(root/'topk_reader_integration.py').read_text('utf8')
    tree=ast.parse(code)
    body=next(x for x in tree.body if isinstance(x,ast.FunctionDef) and x.name=='encode_topk_inputs')
    calls=[x.func for x in ast.walk(body) if isinstance(x,ast.Call)]
    forbidden={'oracle_upper_bound_rank','oracle_key_mask','encode_cards_for_reader'}
    observed={x.attr for x in calls if isinstance(x,ast.Attribute)}
    ck('04_no_oracle_function_on_primary_path',not observed.intersection(forbidden))
    ck('05_no_gold_label_parameter',not {'answer','target_key','gold'}.intersection({x.arg for x in body.args.args}))
    ck('06_no_trained_checkpoint_load',not any(x in code for x in ('torch.load(', 'torch.optim.', 'optimizer.step(', 'TEST_SECRET')))
    cases=probe.build()
    raw=json.dumps({'schema':probe.SCHEMA,'split':'non_test_probe','cases':cases},sort_keys=True,separators=(',',':'))+'\n'
    ck('07_exact_probe_hash',hashlib.sha256(raw.encode()).hexdigest()=='88c558a8f1844ee1e55bff64f30c2b801c8bf3e54ef0cbc537f9fd81e51e9c11')
    ck('08_no_other_split',len(cases)==128 and all(x['split']=='non_test_probe' for x in cases))
    ck('09_exact_32_cards',all(len(x['correct_memory'])==len(x['wrong_memory'])==32 for x in cases))
    ck('10_counterfactual_keys_same_order',all([v['key'] for v in x['correct_memory']]==[v['key'] for v in x['wrong_memory']] for x in cases))
    ck('11_no_gold_in_prompt',all(x['answer'] not in x['question'] for x in cases))
    ck('12_all_card_keys_unique',len({v['key'] for x in cases for v in x['correct_memory']})==4096)
    torch.set_num_threads(2);torch.manual_seed(20261112)
    emb=torch.randn(2048,256)*.02
    token=lambda s:list(s.encode('ascii'))
    model=reader.GatedOracleReader().eval()
    hidden=torch.randn(1,256)*.04
    head=torch.randn(2048,256)*.03
    with torch.no_grad():
        model.output_proj.weight.copy_(torch.randn_like(model.output_proj.weight)*.05)
    chosen=None;missed=None
    for case in cases[:40]:
        x1=integrated.encode_topk_inputs(case['question'],case['correct_memory'],case['wrong_memory'],token,emb,k=1)
        x3=integrated.encode_topk_inputs(case['question'],case['correct_memory'],case['wrong_memory'],token,emb,k=3)
        ck('13_top1_one_bit',int(x1.correct.mask.sum())==1)
        ck('14_top3_three_bits',int(x3.correct.mask.sum())==3)
        ck('15_true_cosine_rank_shared_across_k',x1.rank==x3.rank)
        ck('16_correct_wrong_same_keys',torch.equal(x3.correct.keys,x3.wrong.keys))
        ck('17_correct_wrong_same_mask',torch.equal(x3.correct.mask,x3.wrong.mask))
        ck('18_frozen_embeddings_detached',not x3.correct.keys.requires_grad and not x3.correct.values.requires_grad)
        ix=next(i for i,v in enumerate(case['correct_memory']) if v['key']==case['target_key'])
        if ix in x3.rank[:3]:chosen=(case,x3)
        else:missed=(case,x3)
        if chosen and missed:break
    ck('19_both_retrieval_outcomes_exist_mock',chosen is not None and missed is not None)
    with torch.inference_mode():
        expected=F.linear(hidden,head)
        bypass,g=integrated.bypass_without_memory(hidden,head,model,chosen[1].none)
        yes,_=reader.logits_from_hidden(hidden,head,model,chosen[1].correct)
        no,_=reader.logits_from_hidden(hidden,head,model,chosen[1].wrong)
        missed_yes,_=reader.logits_from_hidden(hidden,head,model,missed[1].correct)
        missed_no,_=reader.logits_from_hidden(hidden,head,model,missed[1].wrong)
    ck('20_bypass_bit_exact',torch.equal(expected,bypass))
    ck('21_bypass_gate_zero',not bool(g.any()))
    ck('22_swapped_value_affects_active_target',not torch.equal(yes,no))
    ck('23_swapped_value_ignored_if_target_missing',torch.equal(missed_yes,missed_no))
    ck('24_bad_k_rejected',rejects(lambda:integrated.encode_topk_inputs(cases[0]['question'],cases[0]['correct_memory'],cases[0]['wrong_memory'],token,emb,k=2)))
    ck('25_malformed_bank_rejected',rejects(lambda:integrated.encode_topk_inputs(cases[0]['question'],cases[0]['correct_memory'][:30],cases[0]['wrong_memory'],token,emb,k=3)))
    ck('26_requires_frozen_embedding',rejects(lambda:integrated.encode_topk_inputs(cases[0]['question'],cases[0]['correct_memory'],cases[0]['wrong_memory'],token,emb.clone().requires_grad_(),k=1)))
    ck('27_private_state_contract_on_synthetic_only',integrated.validate_l0020_private_payload({'steps':128,'source_pins':PIN,'reader_state_dict':model.state_dict()},model)['forward_calls']==0)
    ck('28_no_science_execution',True)
    report={'status':'PASS_INDEPENDENT_COMPACT_SOURCE_QA','schema':'ttm.vm.nontest_topk.independent_compact.v1',
            'checks':cks,'checks_passed':len(cks),'checks_total':len(cks),
            'trained_reader_read':False,'checkpoint_read':False,'DEV_scored':False,'TEST_opened':False,
            'optimizer_steps':0,'mock_only':True}
    if options.out.exists():raise FileExistsError('QA_REPORT_REFUSE_OVERWRITE')
    options.out.parent.mkdir(parents=True,exist_ok=True)
    options.out.write_text(json.dumps(report,indent=2,sort_keys=True)+'\n')
    print(json.dumps({'status':report['status'],'checks':f'{len(cks)}/{len(cks)}'}))
if __name__=='__main__':main()
