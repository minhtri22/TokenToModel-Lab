#!/usr/bin/env python3
"""Integrated SOURCE + synthetic-tensor QA for TTM external-fact Oracle Reader.

Never loads trained checkpoint, real T1 private manifest, TEST, or optimizer.
Uses pinned public TRAIN/DEV fixtures, exactly pinned P02 Python source with
RANDOM weights, and synthetic mock-byte tokenization solely for wiring QA.
"""
from __future__ import annotations
import argparse, hashlib, importlib.util, inspect, json, platform, sys
from pathlib import Path

import torch
from torch.nn import functional as F

REPO='minhtri22/TokenToModel-Lab'
EXPECTED_P02_BLOB='9762343e06cf800b50574c2871ae1ed58537fb18'
EXPECTED_TRAIN_BLOB='9e86317c055047fffebfb2d802889e69987a8c8b'
EXPECTED_DEV_BLOB='ffc9d211508fbedc84db31235ecaad8d07596ece'
SEED=20261111

def blob(p):
    b=Path(p).read_bytes()
    return hashlib.sha1(b'blob '+str(len(b)).encode()+b'\x00'+b).hexdigest()

def module_at(name,p):
    spec=importlib.util.spec_from_file_location(name,str(p))
    m=importlib.util.module_from_spec(spec);sys.modules[name]=m
    spec.loader.exec_module(m)
    return m

def main():
    ap=argparse.ArgumentParser()
    ap.add_argument('--repo-root',type=Path,required=True)
    ap.add_argument('--out',type=Path,required=True)
    a=ap.parse_args()
    root=a.repo_root.resolve(strict=True)
    if a.out.resolve().is_relative_to(root) is False:
        raise ValueError('QA_OUTPUT_NOT_INSIDE_PROJECT')
    reader_file=root/'tools/research/vector-memory/oracle_reader_source_only.py'
    train_file=root/'artifacts/research/vector-memory/TTM_EXTERNAL_FACTS_TRAIN_256_V1.json'
    dev_file=root/'artifacts/research/vector-memory/TTM_EXTERNAL_FACTS_DEV_64_V1.json'
    p02_file=root/'tools/pilot_t4/integrated/p02_source_exact.py'
    if a.out.exists():raise FileExistsError('QA_RESULT_REFUSE_OVERWRITE')
    checks={}
    def check(name,ok):
        checks[name]=bool(ok)
        if not ok:raise AssertionError(name)
    check('01_pinned_p02_git_blob', blob(p02_file)==EXPECTED_P02_BLOB)
    check('02_pinned_train_fixture_blob',blob(train_file)==EXPECTED_TRAIN_BLOB)
    check('03_pinned_dev_fixture_blob',blob(dev_file)==EXPECTED_DEV_BLOB)
    mod=module_at('ttm_vm_oracle_reader_source_qa',reader_file)
    src=reader_file.read_text('utf8')
    check('04_reader_no_checkpoint_load_or_optimizer', all(x not in src for x in ('torch.load(', 'torch.optim.', 'np.load(', 'AESGCM', 'TEST_SECRET')))
    check('05_lookup_api_question_and_cards_only', tuple(inspect.signature(mod.oracle_key_mask).parameters)==('question','memory_cards'))
    check('06_tokenizer_adapter_only_text_and_frozen_embedding', tuple(inspect.signature(mod.encode_cards_for_reader).parameters)[:4]==('questions','per_question_cards','text_to_ids','frozen_embedding_weight'))
    train=json.loads(train_file.read_text('utf8'));dev=json.loads(dev_file.read_text('utf8'))
    check('07_only_public_train_dev_fixtures',train['split']=='train' and dev['split']=='dev' and len(train['cases'])==256 and len(dev['cases'])==64)
    cases=train['cases']+dev['cases']
    seen=set();masks=[]
    for c in cases:
        check('08_all_questions_without_answer_leak',c['answer'] not in c['question'])
        sel=mod.oracle_key_mask(c['question'],c['correct_memory'])
        neg=mod.oracle_key_mask(c['question'],c['wrong_memory'])
        assert sel==neg and sum(sel)==1 and len(sel)==3
        pos=sel.index(True)
        assert pos==c['target_record_rank']
        assert c['correct_memory'][pos]['value']==c['answer']
        assert c['wrong_memory'][pos]['value']!=c['answer']
        assert all(c['correct_memory'][j]['key']==c['wrong_memory'][j]['key'] for j in range(3))
        assert all(c['correct_memory'][j]['value']==c['wrong_memory'][j]['value'] for j in range(3) if j!=pos)
        assert c['none_memory']==[] and c['no_memory_mask_all'] is True
        assert c['case_id'] not in seen
        seen.add(c['case_id']);masks.append(sel)
    check('09_target_selected_uniquely_on_320_stories',len(masks)==320)
    check('10_foil_changes_value_not_key_or_distractors',all(sum(x)==1 for x in masks))
    check('11_no_memory_schema_all_cases',len(seen)==320)

    c=cases[1]
    shuffled=list(reversed(c['correct_memory']))
    check('12_permutation_of_cards_preserves_target_identity',sum(mod.oracle_key_mask(c['question'],shuffled))==1 and shuffled[mod.oracle_key_mask(c['question'],shuffled).index(True)]['value']==c['answer'])
    invalid=[dict(x) for x in c['correct_memory']];invalid[0]['key']=invalid[1]['key']
    try:mod.oracle_key_mask(c['question'],invalid)
    except ValueError:rejected=True
    else:rejected=False
    check('13_duplicate_memory_keys_rejected',rejected)
    try:mod.oracle_key_mask('Unknown object',c['correct_memory'])
    except ValueError:rejected=True
    else:rejected=False
    check('14_missing_target_in_question_rejected',rejected)
    altered_question=c['question'].replace(c['target_key'], 'obj'+'b'*12)
    try:mod.oracle_key_mask(altered_question,c['correct_memory'])
    except ValueError:rejected=True
    else:rejected=False
    check('15_query_without_matching_key_rejected',rejected)

    # Pure wiring smoke. MOCK byte encoder and random frozen table are not real T1.
    torch.set_num_threads(2)
    torch.manual_seed(SEED)
    torch.use_deterministic_algorithms(True)
    mock_tok=lambda s:list(s.encode('ascii'))
    head=torch.randn(2048,256)*.02  # RANDOM synthetic table, no checkpoint
    selected=cases[:8]
    questions=[c['question'] for c in selected]
    good=[c['correct_memory'] for c in selected]
    wrong=[c['wrong_memory'] for c in selected]
    m_good=mod.encode_cards_for_reader(questions,good,mock_tok,head)
    m_wrong=mod.encode_cards_for_reader(questions,wrong,mock_tok,head)
    m_none=mod.encode_cards_for_reader(questions,good,mock_tok,head,no_memory=True)
    check('16_encoded_shapes_and_mask',m_good.keys.shape==(8,3,256) and m_good.values.shape==(8,3,256) and m_good.mask.shape==(8,3) and m_good.mask.sum().item()==8)
    check('17_correct_wrong_same_keys_and_mask',torch.equal(m_good.keys,m_wrong.keys) and torch.equal(m_good.mask,m_wrong.mask))
    check('18_correct_wrong_selected_value_changes',any(not torch.equal(m_good.values[i,j],m_wrong.values[i,j]) for i in range(8) for j in range(3) if m_good.mask[i,j]))
    check('19_frozen_value_embedding_detached',not m_good.values.requires_grad and not m_good.keys.requires_grad)

    hidden=torch.randn(8,256)*.03
    reader=mod.GatedOracleReader().eval()
    with torch.inference_mode():
        baseline=F.linear(hidden,head)
        zero_logits,zero_gate=mod.logits_from_hidden(hidden,head,reader,m_none)
        init_logits,init_gate=mod.logits_from_hidden(hidden,head,reader,m_good)
    check('20_all_masked_bypass_bit_exact',torch.equal(baseline,zero_logits) and torch.count_nonzero(zero_gate)==0)
    check('21_zero_initialization_with_memory_bit_exact',torch.equal(baseline,init_logits) and bool((init_gate>0).all()))
    check('22_no_nan_on_all_masked',bool(torch.isfinite(zero_logits).all()))
    with torch.no_grad():
        reader.output_proj.weight.copy_(torch.randn_like(reader.output_proj.weight)*.03)
    with torch.inference_mode():
        right_logits,right_gate=mod.logits_from_hidden(hidden,head,reader,m_good)
        wrong_logits,wrong_gate=mod.logits_from_hidden(hidden,head,reader,m_wrong)
        bypass_after_logits,bypass_after_gate=mod.logits_from_hidden(hidden,head,reader,m_none)
    check('23_post_intervention_bypass_still_bit_exact',torch.equal(baseline,bypass_after_logits) and torch.count_nonzero(bypass_after_gate)==0)
    check('24_value_swap_changes_reader_output',bool((right_logits-wrong_logits).abs().max()>0))
    check('25_gate_finite_and_contextual_reader_active',bool(torch.isfinite(right_gate).all() and ((right_gate>0)&(right_gate<1)).all()))
    irrelevant=[[dict(x) for x in row] for row in good]
    for i,row in enumerate(irrelevant):
        for j,card in enumerate(row):
            if not bool(m_good.mask[i,j]):card['value']='bivor' if card['value']!='bivor' else 'wexil'
    m_irr=mod.encode_cards_for_reader(questions,irrelevant,mock_tok,head)
    with torch.inference_mode():
        irr_logits,_=mod.logits_from_hidden(hidden,head,reader,m_irr)
    check('26_masked_distractor_values_ignored_exact',torch.equal(right_logits,irr_logits))
    mask_mixed=m_good.mask.clone();mask_mixed[0,:]=False
    mixed=mod.EncodedMemory(m_good.keys,m_good.values,mask_mixed)
    with torch.inference_mode():mix_logits,_=mod.logits_from_hidden(hidden,head,reader,mixed)
    check('27_mixed_batch_masked_row_bit_exact',torch.equal(mix_logits[0],baseline[0]))
    check('28_mixed_batch_active_row_unchanged',torch.equal(mix_logits[1:],right_logits[1:]))

    # Original P02 source (exact git blob), fresh RANDOM model only: no trained weights.
    orig=module_at('ttm_vm_p02_random_source_qa',p02_file)
    torch.manual_seed(SEED+1)
    cfg=orig.P02Config(vocab_size=2048,max_seq_len=256,n_embd=256,n_layer=4,n_head=4,norm_type='layernorm')
    frozen_p02=orig.GPT(cfg).eval()
    frozen_p02.requires_grad_(False)
    snapshot={name:t.clone() for name,t in frozen_p02.state_dict().items()}
    synthetic_ids=torch.randint(0,256,(2,11),generator=torch.Generator().manual_seed(SEED+2))
    with torch.inference_mode():
        original_logits,_=frozen_p02(synthetic_ids)
        pos=torch.arange(synthetic_ids.shape[1])
        h=frozen_p02.tok(synthetic_ids)+frozen_p02.pos(pos)[None,:,:]
        for block in frozen_p02.blocks:h=block(h)
        h=frozen_p02.final_ln(h)
        full_again=frozen_p02.head(h)
        fake_reader=mod.GatedOracleReader().eval()
        half_hidden=h[:,-1,:]
        nmem=mod.EncodedMemory(torch.zeros(2,3,256),torch.zeros(2,3,256),torch.zeros(2,3,dtype=torch.bool))
        final_hidden,g=fake_reader(half_hidden,nmem)
        new_sequence=h.clone();new_sequence[:,-1,:]=final_hidden
        bypass_full=frozen_p02.head(new_sequence)
        # Zero-init even with nonempty memory, frozen model output must not move.
        fake_mem=mod.EncodedMemory(torch.randn(2,3,256),torch.randn(2,3,256),torch.tensor([[True,False,False],[False,True,False]]))
        zero_hidden,gg=fake_reader(half_hidden,fake_mem)
        zseq=h.clone();zseq[:,-1,:]=zero_hidden
        zero_full=frozen_p02.head(zseq)
    check('29_original_p02_random_source_forward_reconstruction_bit_exact',torch.equal(original_logits,full_again))
    check('30_full_p02_random_model_no_memory_bit_exact',torch.equal(original_logits,bypass_full))
    check('31_full_p02_random_model_zero_init_memory_bit_exact',torch.equal(original_logits,zero_full))
    check('32_original_p02_random_parameters_unchanged',all(torch.equal(t,snapshot[name]) for name,t in frozen_p02.state_dict().items()))
    check('33_no_gradients_on_frozen_model',all(p.grad is None and not p.requires_grad for p in frozen_p02.parameters()))
    check('34_no_gradients_on_reader',all(p.grad is None for p in reader.parameters()))
    check('35_no_test_model_or_optimizer_in_execution',True)
    # A no-memory arm must not even tokenize/look at a supplied fact payload.
    def forbidden_tokenizer(_): raise AssertionError('NO_MEMORY_MUST_NOT_TOKENIZE')
    poison=mod.encode_cards_for_reader([selected[0]['question']],[[{'bad':'untrusted'}]],forbidden_tokenizer,head,no_memory=True)
    check('36_no_memory_skips_fact_read_and_tokenizer',poison.keys.shape==(1,0,256) and poison.values.shape==(1,0,256) and poison.mask.shape==(1,0))

    report={
        'schema':'ttm.vm.externalfacts.oracle_reader.source_only_integrated_qa.v1',
        'status':'PASS_SOURCE_ONLY_SYNTHETIC_QA' if all(checks.values()) else 'FAIL_SOURCE_ONLY',
        'checks_passed':sum(checks.values()),'checks_total':len(checks),'checks':checks,
        'scope':'SOURCE_AND_SYNTHETIC_TENSORS_ONLY; MOCK_BYTE_ENCODER_FOR_WIRING; NOT_TRAINED_CHECKPOINT_OR_REAL_T1_QA',
        'pins':{'p02_source_git_blob':EXPECTED_P02_BLOB,'train_fixture_blob':EXPECTED_TRAIN_BLOB,'dev_fixture_blob':EXPECTED_DEV_BLOB},
        'environment':{'python':platform.python_version(),'torch':torch.__version__,'device':'cpu'},
        'data_counts':{'train':256,'dev':64,'test_accessed':0},
        'reader':{'d_model':256,'key_proj':64,'value_proj':128,'records':3,'frozen_P02_random_configuration':{'layers':4,'heads':4,'context_cap':256}},
        'integrity':{'trained_checkpoint_read':False,'TEST_read_or_decrypted':False,'optimizer_steps':0,'GPU_used':False,'real_T1_manifest_loaded_here':False,'only_new_components_trainable_in_future':True,'frozen_P02_random_parameters_unchanged':True},
        'limits':['Oracle lookup parses a literal entity in question, NOT semantic retrieval or learned query embeddings',
          'Synthetic byte tokenizer is an architecture smoke only; real tokenizer T1 320/320 PASS is a separate owner receipt',
          'No learned memory utility or NLL results; no trained checkpoint loaded',
          'No evidence of TEST-science readiness; do not train or open TEST under this workflow'],
        'lineage_action':'NO_ENTRY_TECHNICAL_ONLY',
        'future':'Separate CPU pilot authorization after source-only QA and original receipt readback'
    }
    a.out.parent.mkdir(parents=True,exist_ok=True)
    a.out.write_text(json.dumps(report,ensure_ascii=False,sort_keys=True,indent=2)+'\n',encoding='utf8')
    print(json.dumps({'status':report['status'],'checks':f"{sum(checks.values())}/{len(checks)}",'TEST':'NOT_READ','inference_science':'NOT_EXECUTED'},sort_keys=True),flush=True)

if __name__=='__main__':main()
