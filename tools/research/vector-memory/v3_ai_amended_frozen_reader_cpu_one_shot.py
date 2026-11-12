#!/usr/bin/env python3
"""V3 NONTEST 256: frozen Reader CPU one-shot with prospective AI-custody amendment.

Do not invoke unless owner explicitly chooses --execute-once after independent
QA. Owner-accepted two AI blind reviews required by SHA, not human attestation.
No training, previous PROBE/DEV/TEST, or GPU.
Negative cases NEVER receive Reader forwards, answers, or oracle controls.
"""
from __future__ import annotations
import argparse
from collections import Counter
import hashlib
import json
from pathlib import Path
import numpy as np
import torch
from torch.nn import functional as F
import oracle_reader_source_only as vm
import topk_reader_integration as adapter  # encode-only and private Reader source pin validation
import v3_fresh256_fixture as fixture
import v3_nonoracle_retriever as retrieve
import v3_ai_review_custody_amendment as ai_custody
from cpu_pilot_readiness import encode_target, frozen_hidden_at_answer_positions, module_from, gitblob, sha256

RUN_ID='TTM_VM_V3_NONTEST_256_FROZEN_READER_CPU_ONESHOT_V1'
PINS={
    'p02':'9762343e06cf800b50574c2871ae1ed58537fb18',
    't1':'fa5bd892941ba5aa6e6b2f0b2b0ae974efe297b6',
    'reader_source':'7ce728b2874284b87933237c890e54ce3d9fd651',
    'adapter':'ccab713f8c5a4b913259088225daffcf5382be41',
    'source_helpers':'6c43d2889f39a4ad537ace78ecbff40294089031',
    'v3_fixture_source':'5f51b8b464e54a370f3a3fa99d91307118f52f46',
    'v3_retriever_source':'68bfeaaf1d0acf0cf446e4d734e34368fbf8f702',
    'v3_reviewer_custody':'beaaa78126282439c94b2d0d525297e6b35266a5',
    'v3_source_negative_qa':'041e174579e5a842a0d4dfa46637fe036e9954ec',
    'v3_ai_review_custody':'ede2ee6438dc9b5ba106195e529eb3124d53f31b',
    'v3_ai_A':'46c9fad4b77065cf086213c64ee04145704efa8d6dd3cfbad56d80c9e1d68ed6',
    'v3_ai_B':'fd719ada13d2e44a72d29af04d18bb5d839547b288046ce410cfa9e5b7e49cdf',
    'v2_baseline_retriever':'dc733eda42d768d695309e3a1d5df25aeabb28b7',
    'checkpoint':'ee723407b2c25a18be20e26387a3dd8e4a18e2942d469279b6f0748ff86af0dc',
    'reader':'c458de3afae87b3c381274b8edd698187df63ceac4dbbc0e6d8bd44b85c1632f',
    't1_manifest':'cba18e60cee3d08a353ee6d4a451017289e45af7b4b1179c87171b9b78d7dfdc',
    'v3_fixture':'d473292d40dfb475d0b44f7d393341e19d846308820dcb4f5cbac6acb2c0e543'
}
POSITIVE=('P0_KNOWN_WIRING','P1_UNSEEN_PARAPHRASE','P2_PROVENANCE_UNIQUE','P3_NEGATION_UNIQUE')
PRIMARY_POSITIVE=POSITIVE[1:]
NEGATIVE=tuple(s for s in fixture.STRATA if s.startswith('N'))
ARMS=('A','O1','B1','C1','B3','C3')
BOOTSTRAP_DRAWS=2000
SEED_A,SEED_C=20261120,20261121


def strict_child(path:Path, root:Path)->Path:
    p=path.resolve(strict=True)
    if not p.is_relative_to(root):raise ValueError('PRIVATE_INPUT_OUTSIDE_PROJECT_ROOT')
    return p


def paired_bootstrap95(values,seed):
    xs=np.asarray(values,dtype=np.float64)
    if xs.shape!=(96,) or not np.isfinite(xs).all():
        raise ValueError('PAIRED_BOOTSTRAP_REQUIRES_96_FINITE_POSITIVE_STORIES')
    take=np.random.default_rng(seed).integers(0,96,size=(BOOTSTRAP_DRAWS,96))
    return [float(z) for z in np.quantile(xs[take].mean(axis=1),[.025,.975])]


def wilson95(hits:int,n:int):
    if type(hits) is not int or type(n) is not int or not 0<=hits<=n or n<1:
        raise ValueError('WILSON_COUNT_INVALID')
    z=1.959963984540054
    p=hits/n;den=1+z*z/n
    ctr=(p+z*z/(2*n))/den
    margin=z*((p*(1-p)/n+z*z/(4*n*n))**.5)/den
    return [max(0.,ctr-margin),min(1.,ctr+margin)]


def no_memory(embedding):
    x=embedding.detach().new_empty((1,0,256))
    return vm.EncodedMemory(x,x.clone(),torch.zeros((1,0),dtype=torch.bool))


def encode_memory(cards,text_to_ids,embedding,indices:tuple[int,...]):
    if len(cards)!=32 or not isinstance(indices,tuple) or len(indices) not in (0,1):
        raise ValueError('V3_ONLY_ONE_OR_ZERO_ACTIVE_CARDS')
    if any(type(i) is not int or i<0 or i>=32 for i in indices):
        raise ValueError('ILLEGAL_RETRIEVAL_INDEX')
    if tuple(embedding.shape)!=(2048,256) or embedding.requires_grad or embedding.device.type!='cpu':
        raise ValueError('EMBEDDING_NOT_FROZEN_CPU')
    with torch.inference_mode():
        key=torch.stack([adapter._encode_frozen(c['key'],text_to_ids,embedding) for c in cards])[None]
        val=torch.stack([adapter._encode_frozen(' '+c['value'],text_to_ids,embedding) for c in cards])[None]
    mask=torch.tensor([[i in indices for i in range(32)]],dtype=torch.bool)
    return vm.EncodedMemory(key,val,mask)


def score(hidden,targets,memory,model,reader):
    if hidden.shape!=(len(targets),256) or targets.ndim!=1 or len(targets)<1:
        raise ValueError('ANSWER_ONLY_HIDDEN_TARGET_SHAPE')
    expanded=vm.EncodedMemory(memory.keys.expand(len(targets),-1,-1),
                              memory.values.expand(len(targets),-1,-1),
                              memory.mask.expand(len(targets),-1))
    with torch.inference_mode():
        logits,gate=vm.logits_from_hidden(hidden,model.head.weight,reader,expanded)
        nll=float(F.cross_entropy(logits,targets,reduction='none').mean())
        avg_gate=float(gate.mean())
    if not np.isfinite(nll) or not np.isfinite(avg_gate):raise ValueError('NONFINITE_MODEL_SCORE')
    return nll,avg_gate


def action_only(case):
    """For negative cases, NO Reader, NO answer tokenization, NO target key."""
    if case.get('gold_action')!='ABSTAIN' or any(case.get(k) is not None for k in ('answer','target_key','correct_memory','wrong_memory')):
        raise ValueError('NEGATIVE_CONTAINS_TARGET_OR_ANSWER')
    decision=retrieve.retrieve(case['question'],case['public_index'])
    if decision.status not in ('SELECT','ABSTAIN'):raise ValueError('BAD_RETRIEVAL_STATUS')
    if len(retrieve.mask(decision))!=32:raise ValueError('BAD_RETRIEVAL_MASK')
    return {'case_id':case['case_id'],'stratum':case['stratum'],
            'status':decision.status,'reason_code':decision.reason_code,
            'selected_count':len(decision.indices),'correct_abstain':decision.status=='ABSTAIN',
            'false_selection':decision.status=='SELECT','reader_forward_calls':0,'nll':None}


def positive_case(case,model,reader,text_to_ids):
    if case.get('gold_action')!='SELECT' or not case.get('target_key') or not case.get('answer'):
        raise ValueError('POSITIVE_REQUIRES_GOLD_PRIVATE_SCORER_ONLY')
    # Query and public_index are the ONLY inputs to the retriever.
    decision=retrieve.retrieve(case['question'],case['public_index'])
    if decision.status not in ('SELECT','ABSTAIN'):raise ValueError('BAD_RETRIEVER_STATUS')
    if len(retrieve.mask(decision))!=32:raise ValueError('BAD_RETRIEVER_MASK')
    good,bad=case['correct_memory'],case['wrong_memory']
    if len(good)!=32 or len(bad)!=32:raise ValueError('PRIVATE_MEMORY_BANK_INVALID')
    if any({k:c[k] for k in ('key','source_id','retrieval_text')}!=index for c,index in zip(good,case['public_index'])):
        raise ValueError('PUBLIC_AND_PRIVATE_INDEX_DRIFT')
    if any({k:c[k] for k in ('key','source_id','retrieval_text')}!={k:w[k] for k in ('key','source_id','retrieval_text')} for c,w in zip(good,bad)):
        raise ValueError('WRONG_MEMORY_INDEX_DRIFT')
    if sum(c['value']!=w['value'] for c,w in zip(good,bad))!=1:
        raise ValueError('COUNTERFACTUAL_MUST_SWAP_ONE_VALUE')
    target=next((i for i,card in enumerate(case['public_index']) if card['key']==case['target_key']),None)
    if target is None:raise ValueError('PRIVATE_TARGET_NOT_IN_PUBLIC_INDEX')
    # The gold target is deliberately used ONLY AFTER retrieval has returned.
    selected=decision.indices
    hit=target in selected
    x,answer_positions,targets=encode_target(text_to_ids,case['question'],case['answer'])
    with torch.inference_mode():
        hidden=frozen_hidden_at_answer_positions(model,x,answer_positions)
        zero=no_memory(model.tok.weight)
        ctrl=encode_memory(good,text_to_ids,model.tok.weight,(target,))
        chosen_good=encode_memory(good,text_to_ids,model.tok.weight,selected)
        chosen_bad=encode_memory(bad,text_to_ids,model.tok.weight,selected)
    memories={'A':zero,'O1':ctrl,'B1':chosen_good,'C1':chosen_bad,
              'B3':chosen_good,'C3':chosen_bad}
    nll,gates={},{}
    for arm in ARMS:nll[arm],gates[arm]=score(hidden,targets,memories[arm],model,reader)
    with torch.inference_mode():
        direct=float(F.cross_entropy(F.linear(hidden,model.head.weight),targets,reduction='none').mean())
    if nll['A']!=direct or gates['A']!=0.:
        raise AssertionError('NO_MEMORY_NOT_BIT_EXACT_BYPASS')
    if not torch.equal(chosen_good.keys,chosen_bad.keys) or not torch.equal(chosen_good.mask,chosen_bad.mask):
        raise AssertionError('WRONG_VALUE_CHANGE_RANK_OR_MASK')
    if not hit and nll['B1']!=nll['C1']:
        raise AssertionError('WRONG_VALUE_AFFECTED_UNSELECTED_TARGET')
    if decision.status=='ABSTAIN' and (nll['B1']!=nll['A'] or nll['C1']!=nll['A']):
        raise AssertionError('POSITIVE_ABSTAIN_NOT_BYPASSED')
    return {'case_id':case['case_id'],'stratum':case['stratum'],'status':decision.status,
            'reason_code':decision.reason_code,'selected_count':len(selected),
            'hit1':bool(hit),'missed_positive':not hit,'correct_select':bool(hit),
            'answer_tokens':len(targets),'arm_nll':nll,'arm_gate':gates,
            'diagnostic_B3_C3':'SINGLETON_V3_EQUIVALENT_TO_B1_C1_NOT_TRUE_TOP3'}


def avg(xs):
    if not xs:raise ValueError('EMPTY_PRIMARY_METRIC')
    return float(np.mean(np.asarray(xs,dtype=np.float64)))


def aggregate(per_story):
    if len(per_story)!=256 or len({x['case_id'] for x in per_story})!=256:
        raise ValueError('INCOMPLETE_V3_ONE_SHOT')
    for s in fixture.STRATA:
        if sum(x['stratum']==s for x in per_story)!=32:raise ValueError('STRATUM_MISSING')
    positives=[x for x in per_story if x['stratum'] in POSITIVE]
    pp=[x for x in positives if x['stratum'] in PRIMARY_POSITIVE]
    neg=[x for x in per_story if x['stratum'] in NEGATIVE]
    if len(positives)!=128 or len(pp)!=96 or len(neg)!=128:raise ValueError('GROUP_TOTAL_MISMATCH')
    # Aggregate action accuracy is a hard denominator; abstain on positives is
    # counted as miss, and SELECT on negatives as a false selection.
    hits=sum(x['correct_select'] for x in pp)
    n_abstain=sum(x['correct_abstain'] for x in neg)
    p1hits=sum(x['correct_select'] for x in pp if x['stratum']=='P1_UNSEEN_PARAPHRASE')
    delA=[x['arm_nll']['A']-x['arm_nll']['B1'] for x in pp]
    delC=[x['arm_nll']['C1']-x['arm_nll']['B1'] for x in pp]
    ciA=paired_bootstrap95(delA,SEED_A);ciC=paired_bootstrap95(delC,SEED_C)
    means={arm:avg([x['arm_nll'][arm] for x in pp]) for arm in ARMS}
    oracle_gain=means['A']-means['O1']
    if oracle_gain<.05: verdict='HOLD_READER_DOMAIN_SHIFT'
    elif n_abstain<122:verdict='FAIL_UNSAFE_SELECTION_SCOPED'
    elif hits<72 or p1hits<20:verdict='FAIL_UNSEEN_OR_COMPOSITIONAL_RETRIEVAL_SCOPED'
    elif avg(delA)<.05 or avg(delC)<.05 or ciA[0]<=0 or ciC[0]<=0:
        verdict='FAIL_FROZEN_READER_TRANSFER_SCOPED'
    else:verdict='GO_CANDIDATE_NONTEST_AMBIGUITY_SCOPED'
    breakdown={}
    for s in fixture.STRATA:
        sub=[x for x in per_story if x['stratum']==s]
        breakdown[s]={'cases':32,'correct_select':sum(x.get('correct_select',False) for x in sub),
                       'correct_abstain':sum(x.get('correct_abstain',False) for x in sub),
                       'false_selection':sum(x.get('false_selection',False) for x in sub),
                       'status_counts':dict(Counter(x['status'] for x in sub)),
                       'reason_counts':dict(Counter(x['reason_code'] for x in sub))}
    return {'verdict':verdict,'positive_primary_96':{'correct_select':hits,'min_hits':72,
              'rate':hits/96,'wilson95':wilson95(hits,96),'p1_hits':p1hits,'p1_min_hits':20},
            'negative_primary_128':{'correct_abstain':n_abstain,'min_count':122,
              'false_selections':128-n_abstain,'rate':n_abstain/128,
              'wilson95':wilson95(n_abstain,128)},
            'positive_reader_primary96':{'story_mean_nll':means,
              'paired_mean_delta':{'A_minus_B1':avg(delA),'C1_minus_B1':avg(delC)},
              'bootstrap95':{'A_minus_B1':ciA,'C1_minus_B1':ciC},
              'bootstrap_draws':BOOTSTRAP_DRAWS,
              'bootstrap_seeds':{'A_minus_B1':SEED_A,'C1_minus_B1':SEED_C},
              'oracle_A_minus_O1':oracle_gain,
              'answer_tokens_per_arm':sum(x['answer_tokens'] for x in pp)},
            'diagnostic_cost':3*(128-n_abstain)+(96-hits),
            'strata':breakdown,
            'diagnostic_B3_C3':'SINGLETON_DUPLICATE_OF_B1_C1_NOT_A_TOP3_EXPERIMENT'}


def verify_fixture(decoded):
    if decoded.get('schema')!=fixture.SCHEMA or decoded.get('split')!='non_test_probe_v3':
        raise ValueError('V3_FIXTURE_SCHEMA_DRIFT')
    cases=decoded.get('cases')
    if not isinstance(cases,list) or len(cases)!=256:raise ValueError('V3_FIXTURE_NOT_256')
    if Counter(c['stratum'] for c in cases)!={s:32 for s in fixture.STRATA}:
        raise ValueError('V3_STRATUM_COUNT_CHANGED')
    ids=set()
    for c in cases:
        if c['case_id'] in ids:raise ValueError('DUPLICATE_CASE_ID')
        ids.add(c['case_id'])
        if c.get('schema')!=fixture.SCHEMA or len(c['public_index'])!=32:
            raise ValueError('PUBLIC_CASE_SCHEMA_CHANGED')
        if c['gold_action']=='ABSTAIN':
            if any(c.get(k) is not None for k in ('answer','target_key','correct_memory','wrong_memory')):
                raise ValueError('NEGATIVE_HAS_GOLD_ANSWER_OR_MEMORY')
        elif c['gold_action']=='SELECT':
            if not c.get('target_key') or not c.get('answer') or len(c['correct_memory'])!=32 or len(c['wrong_memory'])!=32:
                raise ValueError('POSITIVE_MISSING_ANSWER_OR_MEMORY')
        else:raise ValueError('INVALID_GOLD_ACTION')
    return cases


def verify_pins(root,checkout,ckpt,reader,t1,probe):
    paths={'checkout':strict_child(checkout,root),'checkpoint':strict_child(ckpt,root),
           'reader':strict_child(reader,root),'t1_manifest':strict_child(t1,root),
           'v3_fixture':strict_child(probe,root)}
    s=paths['checkout']/'tools/research/vector-memory'
    src={
      'p02':paths['checkout']/'tools/pilot_t4/integrated/p02_source_exact.py',
      't1':paths['checkout']/'tools/pilot_t4/integrated/source_t2/ttm_gpt2_bpe2048.py',
      'reader_source':s/'oracle_reader_source_only.py',
      'adapter':s/'topk_reader_integration.py',
      'source_helpers':s/'cpu_pilot_readiness.py',
      'v3_fixture_source':s/'v3_fresh256_fixture.py',
      'v3_retriever_source':s/'v3_nonoracle_retriever.py',
      'v3_reviewer_custody':s/'v3_p1_reviewer_custody.py',
      'v3_source_negative_qa':s/'v3_independent_source_qa.py',
      'v3_ai_review_custody':s/'v3_ai_review_custody_amendment.py',
      'v2_baseline_retriever':s/'v2_nontest_retrievers.py'}
    for k,path in src.items():
        if gitblob(path)!=PINS[k]:raise ValueError('FROZEN_V3_SOURCE_BLOB_MISMATCH:'+k)
    for k in ('checkpoint','reader','t1_manifest','v3_fixture'):
        if sha256(paths[k])!=PINS[k]:raise ValueError('FROZEN_V3_BINARY_SHA_MISMATCH:'+k)
    return paths,src


def main():
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument('--execute-once',action='store_true')
    for name in ('project-root','checkout','checkpoint','reader','t1-manifest','fixture','review-a','review-b','output-dir'):
        p.add_argument('--'+name,type=Path,required=True)
    args=p.parse_args()
    if not args.execute_once:raise SystemExit('DENY_NO_EXPLICIT_EXECUTE_ONCE')
    root=args.project_root.resolve(strict=True)
    output=args.output_dir.resolve()
    expected=(root/'_evidence'/'vector-memory'/RUN_ID).resolve()
    if output!=expected or not output.is_relative_to(root):raise ValueError('RUN_ID_OUTPUT_NOT_OWNER_ROOT')
    if output.exists():raise FileExistsError('ONE_SHOT_ALREADY_STARTED_NO_RETRY')
    paths,src=verify_pins(root,args.checkout,args.checkpoint,args.reader,args.t1_manifest,args.fixture)
    for review in (args.review_a,args.review_b):strict_child(review,root)
    dataset=json.loads(paths['v3_fixture'].read_text(encoding='utf-8'))
    cases=verify_fixture(dataset)
    review_a=json.loads(args.review_a.read_text(encoding='utf-8'))
    review_b=json.loads(args.review_b.read_text(encoding='utf-8'))
    a_raw=args.review_a.read_bytes(); b_raw=args.review_b.read_bytes()
    if sha256(args.review_a)!=PINS['v3_ai_A'] or sha256(args.review_b)!=PINS['v3_ai_B']:
        raise ValueError('HOLD_AI_RATER_RAW_SHA_MISMATCH')
    receipt=ai_custody.validate_two_ai_reviews(cases,PINS['v3_fixture'],a_raw,b_raw)
    if receipt['status']!='PASS_TWO_AI_BLIND_REVIEW_SOURCE_AND_GOLD_32_OF_32_EXPLORATORY' or receipt['human_gate_satisfied'] is not False:
        raise ValueError('HOLD_AI_CUSTODY_GATE_NOT_PASS')
    # Everything above is pre-execution. No trained-model forward or 256 PROBE
    # retrieval has occurred before the one-shot marker is created.
    torch.set_num_threads(2)
    torch.use_deterministic_algorithms(True)
    torch.manual_seed(20261112)
    if torch.cuda.is_initialized():raise RuntimeError('CUDA_ALREADY_INITIALIZED')
    ck=torch.load(paths['checkpoint'],map_location='cpu',weights_only=True)
    if ck['step']!=1280 or ck['p02_git_blob']!=PINS['p02']:raise ValueError('BACKBONE_CHECKPOINT_PIN_DRIFT')
    p02=module_from('vm_v3_p02_pinned',src['p02'])
    t1src=module_from('vm_v3_t1_pinned',src['t1'])
    tokenizer=t1src.BPE2048.from_manifest(json.loads(paths['t1_manifest'].read_text(encoding='utf8')))
    if tokenizer.source_kind!='PINNED_TINYSTORIES_TRAIN':raise ValueError('T1_NOT_ORIGINAL_TRAIN_SOURCE')
    model=p02.GPT(p02.P02Config(**ck['config'])).cpu().eval()
    model.load_state_dict(ck['model'],strict=True)
    model.requires_grad_(False)
    if model.head.weight.data_ptr()!=model.tok.weight.data_ptr():raise ValueError('BACKBONE_UNTIED')
    reader=vm.GatedOracleReader().cpu().eval()
    payload=torch.load(paths['reader'],map_location='cpu',weights_only=True)
    adapter.validate_l0020_private_payload(payload,reader)
    reader.load_state_dict(payload['reader_state_dict'],strict=True)
    reader.requires_grad_(False)
    model_state={k:v.detach().clone() for k,v in model.state_dict().items()}
    reader_state={k:v.detach().clone() for k,v in reader.state_dict().items()}
    output.parent.mkdir(parents=True,exist_ok=True)
    output.mkdir(exist_ok=False)  # permanently consumes one-shot even after partial failure
    with (output/'ONE_SHOT_STARTED.json').open('x',encoding='utf8') as f:
        json.dump({'run_id':RUN_ID,'cases':256,'reader_sha256':PINS['reader'],
                   'fixture_sha256':PINS['v3_fixture'],'P1_AI_CUSTODY':'PASS_32_32_EXPLORATORY','human_gate_satisfied':False,
                   'test_opened':False},f,sort_keys=True);f.write('\n')
    per_story=[]
    for case in cases:
        if case['gold_action']=='ABSTAIN':
            per_story.append(action_only(case))
        else:
            per_story.append(positive_case(case,model,reader,tokenizer.encode))
    if len(per_story)!=256:raise AssertionError('ONE_SHOT_INCOMPLETE')
    if not all(torch.equal(v,model_state[k]) for k,v in model.state_dict().items()):
        raise AssertionError('BACKBONE_WEIGHT_MUTATION')
    if not all(torch.equal(v,reader_state[k]) for k,v in reader.state_dict().items()):
        raise AssertionError('READER_WEIGHT_MUTATION')
    if any(p.grad is not None for p in list(model.parameters())+list(reader.parameters())):
        raise AssertionError('UNEXPECTED_GRADIENT')
    report=aggregate(per_story)
    report.update({'schema':'ttm.vm.v3.nontest256.frozen_reader_one_shot.v1',
         'run_id':RUN_ID,'cases':256,'p1_semantic_custody':'PASS_TWO_AI_BLIND_REVIEW_SOURCE_AND_GOLD_32_OF_32_EXPLORATORY',
         'review_class':'AI_ASSISTED_EXPLORATORY_SCOPED',
         'human_gate_satisfied':False,
         'source_pins':PINS,'optimizer_steps':0,'reader_unchanged':True,
         'backbone_unchanged':True,'old_probe_rescored':False,'dev_rescored':False,
         'test_opened':False,'gpu_used':False,'one_shot':True,
         'limitations':'Prospective pre-CPU owner amendment accepts AI instead of human for internal exploratory research; independence self-reported; P1 phrase proposals already embedded in V3 Retriever; no claim of open unseen semantics or sealed TEST.'})
    with (output/'PER_STORY_QA_PRIVATE.json').open('x',encoding='utf8') as f:
        json.dump(per_story,f,sort_keys=True,indent=2);f.write('\n')
    with (output/'PROBE_AGGREGATE_PUBLIC.json').open('x',encoding='utf8') as f:
        json.dump(report,f,sort_keys=True,indent=2);f.write('\n')
    print(json.dumps({'status':report['verdict'],'cases':256,'TEST_NOT_OPENED':True,
                      'TRAINING':False},sort_keys=True))

if __name__=='__main__':main()
