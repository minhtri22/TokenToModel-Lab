#!/usr/bin/env python3
"""TTM Vector Memory V2: exactly one CPU 192 NONTEST frozen-Reader evaluation.

No optimizer, no checkpoint mutation, no old PROBE/DEV or sealed TEST access.
This source cannot run without --execute-once and full input/source SHA pins.
The only primary readout is 64 S2 description cases, as preregistered.
"""
from __future__ import annotations
import argparse
from collections import Counter
import functools
import hashlib
import json
import subprocess
from pathlib import Path
import numpy as np
import torch
from torch.nn import functional as F
import oracle_reader_source_only as vm
import topk_reader_integration as old_adapter  # metadata-only validation; never ranks old PROBE
import v2_nontest_fixture as fixture
import v2_nontest_retrievers as retrieve
from cpu_pilot_readiness import encode_target, frozen_hidden_at_answer_positions, module_from, gitblob, sha256

RUN_ID = 'TTM_VM_V2_NONTEST_192_FROZEN_READER_CPU_ONESHOT_V1'
PINS = {
    'p02': '9762343e06cf800b50574c2871ae1ed58537fb18',
    't1': 'fa5bd892941ba5aa6e6b2f0b2b0ae974efe297b6',
    'reader_source': '7ce728b2874284b87933237c890e54ce3d9fd651',
    'adapter': 'ccab713f8c5a4b913259088225daffcf5382be41',
    'source_helpers': '6c43d2889f39a4ad537ace78ecbff40294089031',
    'v2_fixture': '01703d4786872a66459593d27cd7607b66c895dd',
    'v2_retriever': 'dc733eda42d768d695309e3a1d5df25aeabb28b7',
    'checkpoint': 'ee723407b2c25a18be20e26387a3dd8e4a18e2942d469279b6f0748ff86af0dc',
    'reader': 'c458de3afae87b3c381274b8edd698187df63ceac4dbbc0e6d8bd44b85c1632f',
    't1_manifest': 'cba18e60cee3d08a353ee6d4a451017289e45af7b4b1179c87171b9b78d7dfdc',
    'fixture': '1d7c02ab082a3c34345953dc5146e5a93f8c6f44e11132ea8abb0594efcc0b9d',
}
ARMS = ('A', 'O1', 'B1', 'C1', 'B3', 'C3')
BOOTSTRAP_DRAWS = 2000
SEED_A, SEED_C = 20261116, 20261117


def strict_path(path: Path, root: Path) -> Path:
    p = path.resolve(strict=True)
    if not p.is_relative_to(root):
        raise ValueError('INPUT_OUTSIDE_RESEARCH_ROOT')
    return p


def paired_bootstrap95(values: list[float] | np.ndarray, seed: int) -> list[float]:
    x = np.asarray(values, dtype=np.float64)
    if x.shape != (64,) or not np.isfinite(x).all():
        raise ValueError('PRIMARY_BOOTSTRAP_EXPECTS_64_FINITE_STORIES')
    rng = np.random.default_rng(seed)
    idx = rng.integers(0, 64, size=(BOOTSTRAP_DRAWS, 64))
    return [float(x) for x in np.quantile(x[idx].mean(axis=1), [.025, .975])]


def validate_fixture(cases: list[dict]) -> None:
    if len(cases) != 192 or len({x['case_id'] for x in cases}) != 192:
        raise ValueError('FIXTURE_NOT_EXACT_192_UNIQUE')
    if Counter(c['stratum'] for c in cases) != {s: 64 for s in fixture.STRATA}:
        raise ValueError('FIXTURE_STRATA_CHANGED')
    for stratum in fixture.STRATA:
        labels = Counter(c['answer'] for c in cases if c['stratum'] == stratum)
        if labels != {x: 4 for x in fixture.LABELS}:
            raise ValueError('FIXTURE_LABEL_BALANCE_CHANGED')
    keys, aliases = set(), set()
    for c in cases:
        if c['schema'] != fixture.VERSION or c['split'] != 'non_test_probe_v2':
            raise ValueError('FIXTURE_SCHEMA_CHANGED')
        question = c['question']
        if not question or c['answer'] in question or c['none_memory'] != []:
            raise ValueError('QUESTION_GOLD_LEAK_OR_NOT_NO_MEMORY')
        if c['stratum'] == 'S0_ID_LITERAL':
            if question.count(c['target_key']) != 1: raise ValueError('S0_QUERY_MISSING_LITERAL_ID')
        elif c['stratum'] == 'S1_ALIAS_LOOKUP':
            if 'obja' in question or 'aka' not in question: raise ValueError('S1_QUERY_LEAK')
        elif 'obja' in question or 'aka' in question:
            raise ValueError('S2_QUERY_IDENTITY_LEAK')
        good, bad = c['correct_memory'], c['wrong_memory']
        if len(good) != 32 or len(bad) != 32: raise ValueError('NOT_32_CARDS')
        if [v['key'] for v in good] != [v['key'] for v in bad]:
            raise ValueError('WRONG_MEMORY_KEY_ORDER_CHANGED')
        if len({v['key'] for v in good}) != 32 or len({v['lookup_alias'] for v in good}) != 32:
            raise ValueError('DUPLICATE_INDEX_KEY_OR_ALIAS')
        if sum(v['key'] == c['target_key'] for v in good) != 1:
            raise ValueError('TARGET_NOT_UNIQUE')
        if sum(a['value'] != b['value'] for a, b in zip(good, bad)) != 1:
            raise ValueError('COUNTERFACTUAL_MULTIPLE_VALUES')
        for a, b in zip(good, bad):
            if a['key'] != b['key'] or a['lookup_alias'] != b['lookup_alias'] or a['retrieval_text'] != b['retrieval_text']:
                raise ValueError('COUNTERFACTUAL_INDEX_DRIFT')
            if (a['value'] == c['answer']) != (a['key'] == c['target_key']):
                raise ValueError('CORRECT_MEMORY_GOLD_LEAK')
            if b['value'] == c['answer']:
                raise ValueError('WRONG_MEMORY_CONTAINS_GOLD')
            if a['key'] in keys or a['lookup_alias'] in aliases:
                raise ValueError('GLOBAL_DUPLICATE_KEY_OR_ALIAS')
            keys.add(a['key']); aliases.add(a['lookup_alias'])
    if len(keys) != 6144 or len(aliases) != 6144:
        raise ValueError('GLOBAL_CARD_COUNT_CHANGED')


def public_index(cards: list[dict]) -> list[dict]:
    """Strictly remove values and gold fields before any retrieval call."""
    return [{k: card[k] for k in ('key', 'lookup_alias', 'retrieval_text')} for card in cards]


def rank_public(question: str, cards: list[dict], stratum: str, text_to_ids, frozen_embedding, *, k: int):
    if k not in (1, 3): raise ValueError('K_NOT_FROZEN')
    index = public_index(cards)
    if stratum == 'S0_ID_LITERAL':
        return retrieve.exact_id(question, index)
    if stratum == 'S1_ALIAS_LOOKUP':
        return retrieve.exact_alias(question, index)
    if stratum != 'S2_DESC_PARAPHRASE':
        raise ValueError('STRATUM_UNKNOWN')
    cosine = functools.partial(retrieve.frozen_description_cosine,
                               text_to_ids=text_to_ids, frozen_embedding=frozen_embedding)
    return retrieve.hybrid_description(question, index, top_k=k, fallback_cosine=cosine)


def encode_memory(cards: list[dict], text_to_ids, embedding, indices: tuple[int, ...]):
    if len(cards) != 32 or not isinstance(indices, tuple) or len(indices) not in (0, 1, 3):
        raise ValueError('BAD_RETRIEVAL_SELECTION')
    if len(set(indices)) != len(indices) or any(type(i) is not int or i < 0 or i >= 32 for i in indices):
        raise ValueError('BAD_RETRIEVAL_INDICES')
    if embedding.shape != (2048, 256) or embedding.device.type != 'cpu' or embedding.requires_grad:
        raise ValueError('INVALID_FROZEN_EMBEDDING')
    # Preserve the exact L0020 key and value encoding, not descriptor embedding.
    with torch.inference_mode():
        keys = torch.stack([old_adapter._encode_frozen(c['key'], text_to_ids, embedding) for c in cards])[None]
        values = torch.stack([old_adapter._encode_frozen(' ' + c['value'], text_to_ids, embedding) for c in cards])[None]
    bits = [i in indices for i in range(32)]
    mask = torch.tensor([bits], dtype=torch.bool)
    return vm.EncodedMemory(keys, values, mask)


def no_memory(embedding):
    empty = embedding.detach().new_empty((1, 0, 256))
    return vm.EncodedMemory(empty, empty.clone(), torch.zeros((1, 0), dtype=torch.bool))


def score(hidden, targets, memory, model, reader):
    if hidden.ndim != 2 or hidden.shape != (len(targets), 256) or targets.ndim != 1 or len(targets) == 0:
        raise ValueError('INVALID_ANSWER_ONLY_SHAPES')
    expand = vm.EncodedMemory(memory.keys.expand(len(targets), -1, -1),
                              memory.values.expand(len(targets), -1, -1),
                              memory.mask.expand(len(targets), -1))
    with torch.inference_mode():
        logits, gate = vm.logits_from_hidden(hidden, model.head.weight, reader, expand)
        nll = F.cross_entropy(logits, targets, reduction='none').mean().item()
        avg_gate = gate.mean().item()
    if not np.isfinite(nll): raise ValueError('NONFINITE_ANSWER_ONLY_NLL')
    return float(nll), float(avg_gate)


def score_case(case, model, reader, text_to_ids):
    q, answer = case['question'], case['answer']
    tokens, positions, targets = encode_target(text_to_ids, q, answer)
    with torch.inference_mode():
        hidden = frozen_hidden_at_answer_positions(model, tokens, positions)
        r1 = rank_public(q, case['correct_memory'], case['stratum'], text_to_ids, model.tok.weight, k=1)
        r3 = rank_public(q, case['correct_memory'], case['stratum'], text_to_ids, model.tok.weight, k=3)
        if r1.status == 'SELECTED' and not r1.indices:
            raise ValueError('EMPTY_SELECTED_RETRIEVAL')
        if r1.status == 'ABSTAIN' and r1.indices:
            raise ValueError('ABSTAIN_WITH_INDICES')
        if r3.status == 'ABSTAIN' and r3.indices:
            raise ValueError('ABSTAIN_TOP3_WITH_INDICES')
        if r1.status == 'SELECTED' and r3.status == 'SELECTED' and r1.indices[0] != r3.indices[0]:
            raise AssertionError('K1_K3_PRIMARY_SELECTION_DRIFT')
        # Ground-truth target is accessed only *after* both ranks are formed.
        target_index = next(i for i, c in enumerate(case['correct_memory']) if c['key'] == case['target_key'])
        targets_mask = (target_index,)
        zero = no_memory(model.tok.weight)
        mem = {'A': zero,
               'O1': encode_memory(case['correct_memory'], text_to_ids, model.tok.weight, targets_mask),
               'B1': encode_memory(case['correct_memory'], text_to_ids, model.tok.weight, r1.indices),
               'C1': encode_memory(case['wrong_memory'], text_to_ids, model.tok.weight, r1.indices),
               'B3': encode_memory(case['correct_memory'], text_to_ids, model.tok.weight, r3.indices),
               'C3': encode_memory(case['wrong_memory'], text_to_ids, model.tok.weight, r3.indices)}
        nll, gates = {}, {}
        for arm in ARMS:
            nll[arm], gates[arm] = score(hidden, targets, mem[arm], model, reader)
        direct = F.cross_entropy(F.linear(hidden, model.head.weight), targets, reduction='none').mean().item()
        if nll['A'] != float(direct) or gates['A'] != 0.0:
            raise AssertionError('NO_MEMORY_NOT_EXACT_BYPASS')
        if not torch.equal(mem['B1'].mask, mem['C1'].mask) or not torch.equal(mem['B3'].mask, mem['C3'].mask):
            raise AssertionError('FOIL_MASK_CHANGED')
        if not torch.equal(mem['B1'].keys, mem['C1'].keys) or not torch.equal(mem['B3'].keys, mem['C3'].keys):
            raise AssertionError('FOIL_CARD_KEYS_CHANGED')
        hit1 = target_index in r1.indices
        hit3 = target_index in r3.indices
        if not hit1 and nll['B1'] != nll['C1']:
            raise AssertionError('MISSED_TARGET_K1_VALUE_AFFECTED_NLL')
        if not hit3 and nll['B3'] != nll['C3']:
            raise AssertionError('MISSED_TARGET_K3_VALUE_AFFECTED_NLL')
    return {'case_id': case['case_id'], 'stratum': case['stratum'],
            'hit1': bool(hit1), 'hit3': bool(hit3),
            'coverage1': r1.status == 'SELECTED', 'coverage3': r3.status == 'SELECTED',
            'status1': r1.status, 'status3': r3.status,
            'method1': r1.method, 'method3': r3.method,
            'cause1': r1.cause, 'cause3': r3.cause,
            'answer_tokens': int(len(targets)), 'arm_nll': nll, 'arm_gate': gates}


def mean(items):
    if len(items) == 0: raise ValueError('NO_STORIES')
    return float(np.mean(np.asarray(items, dtype=np.float64)))


def aggregate(per_story):
    if len(per_story) != 192: raise ValueError('INCOMPLETE_V2_EVALUATION')
    strata={}
    for stratum in fixture.STRATA:
        items=[x for x in per_story if x['stratum'] == stratum]
        if len(items) != 64: raise ValueError('INCOMPLETE_STRATUM')
        strata[stratum]={'count':64,
                         'hits1':sum(x['hit1'] for x in items), 'hits3':sum(x['hit3'] for x in items),
                         'coverage1':sum(x['coverage1'] for x in items),
                         'coverage3':sum(x['coverage3'] for x in items),
                         'recall1':mean([x['hit1'] for x in items]),
                         'recall3':mean([x['hit3'] for x in items]),
                         'mean_story_nll':{arm:mean([x['arm_nll'][arm] for x in items]) for arm in ARMS},
                         'answer_tokens_per_arm':sum(x['answer_tokens'] for x in items),
                         'fallback1_count':sum(x['cause1'] == 'FROZEN_COSINE_FALLBACK' for x in items)}
    s2=[x for x in per_story if x['stratum'] == 'S2_DESC_PARAPHRASE']
    dA=np.array([x['arm_nll']['A']-x['arm_nll']['B1'] for x in s2],dtype=np.float64)
    dC=np.array([x['arm_nll']['C1']-x['arm_nll']['B1'] for x in s2],dtype=np.float64)
    ciA=paired_bootstrap95(dA,SEED_A); ciC=paired_bootstrap95(dC,SEED_C)
    A,O1=strata['S2_DESC_PARAPHRASE']['mean_story_nll']['A'],strata['S2_DESC_PARAPHRASE']['mean_story_nll']['O1']
    # This order is frozen in v2 prereg. No success claim for S0/S1 or Top3.
    if not (A - O1 >= .05): verdict='HOLD_READER_QUERY_DOMAIN_SHIFT'
    elif strata['S2_DESC_PARAPHRASE']['hits1'] < 58: verdict='FAIL_DESCRIPTION_RETRIEVAL_SCOPED'
    elif not (mean(dA) >= .05 and mean(dC) >= .05 and ciA[0] > 0 and ciC[0] > 0):
        verdict='FAIL_FROZEN_READER_TRANSFER_SCOPED'
    else: verdict='GO_CANDIDATE_NONTEST_DESCRIPTION_SCOPED'
    return {'verdict':verdict,'strata':strata,
            'primary_S2':{'hits_min':58,'threshold_recall1':.90,
                          'paired_mean_delta':{'A_minus_B1':mean(dA),'C1_minus_B1':mean(dC)},
                          'bootstrap95':{'A_minus_B1':ciA,'C1_minus_B1':ciC},
                          'bootstrap_draws':BOOTSTRAP_DRAWS,
                          'bootstrap_seeds':{'A_minus_B1':SEED_A,'C1_minus_B1':SEED_C},
                          'oracle_min_gain':.05}}


def evaluate_pins(project_root: Path, checkout: Path, reader_path: Path, ckpt: Path, t1: Path, probe_path: Path):
    root = project_root.resolve(strict=True)
    wt = strict_path(checkout, root)
    reader = strict_path(reader_path, root)
    checkpoint = strict_path(ckpt, root)
    manifest = strict_path(t1, root)
    fixture_path = strict_path(probe_path, root)
    source=wt/'tools/research/vector-memory'
    sources={'p02':wt/'tools/pilot_t4/integrated/p02_source_exact.py',
             't1':wt/'tools/pilot_t4/integrated/source_t2/ttm_gpt2_bpe2048.py',
             'reader_source':source/'oracle_reader_source_only.py',
             'adapter':source/'topk_reader_integration.py',
             'source_helpers':source/'cpu_pilot_readiness.py',
             'v2_fixture':source/'v2_nontest_fixture.py',
             'v2_retriever':source/'v2_nontest_retrievers.py'}
    for key, path in sources.items():
        if gitblob(path) != PINS[key]:
            raise ValueError('SOURCE_GIT_BLOB_DRIFT:'+key)
    binary={'checkpoint':checkpoint,'reader':reader,'t1_manifest':manifest,'fixture':fixture_path}
    for key,path in binary.items():
        if sha256(path) != PINS[key]:
            raise ValueError('BINARY_SHA256_DRIFT:'+key)
    return sources


def main():
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument('--execute-once',action='store_true')
    for name in ('project-root','checkout','checkpoint','reader','t1-manifest','fixture','output-dir'):
        p.add_argument('--'+name,type=Path,required=True)
    args=p.parse_args()
    if not args.execute_once: raise SystemExit('DENY_NO_EXPLICIT_EXECUTE_ONCE')
    root=args.project_root.resolve(strict=True)
    destination=args.output_dir.resolve()
    expected=(root/'_evidence'/'vector-memory'/RUN_ID).resolve()
    if destination!=expected or not destination.is_relative_to(root):
        raise ValueError('FROZEN_ONESHOT_OUTPUT_SCOPE_MISMATCH')
    if destination.exists(): raise FileExistsError('ONE_SHOT_ALREADY_CONSUMED_NO_RETRY')
    sources=evaluate_pins(root,args.checkout,args.reader,args.checkpoint,args.t1_manifest,args.fixture)
    torch.set_num_threads(2)
    torch.use_deterministic_algorithms(True)
    torch.manual_seed(20261112)
    if torch.cuda.is_initialized(): raise RuntimeError('CUDA_INITIALIZED_CPU_ONLY')
    ck=torch.load(args.checkpoint,map_location='cpu',weights_only=True)
    if ck['step']!=1280 or ck['p02_git_blob']!=PINS['p02']:
        raise ValueError('ORIGINAL_CHECKPOINT_SOURCE_MISMATCH')
    p02mod=module_from('vm_v2_p02_source',sources['p02'])
    t1mod=module_from('vm_v2_t1_source',sources['t1'])
    manifest=json.loads(args.t1_manifest.read_text(encoding='utf8'))
    tokenizer=t1mod.BPE2048.from_manifest(manifest)
    if tokenizer.source_kind != 'PINNED_TINYSTORIES_TRAIN':
        raise ValueError('T1_SOURCE_NOT_REAL_TRAIN')
    model=p02mod.GPT(p02mod.P02Config(**ck['config'])).cpu().eval()
    model.load_state_dict(ck['model'],strict=True)
    model.requires_grad_(False)
    if model.head.weight.data_ptr()!=model.tok.weight.data_ptr():
        raise ValueError('BACKBONE_TIED_HEAD_BROKEN')
    reader=vm.GatedOracleReader().cpu().eval()
    payload=torch.load(args.reader,map_location='cpu',weights_only=True)
    old_adapter.validate_l0020_private_payload(payload,reader)
    reader.load_state_dict(payload['reader_state_dict'],strict=True)
    reader.requires_grad_(False)
    frozen_model={name:x.detach().clone() for name,x in model.state_dict().items()}
    frozen_reader={name:x.detach().clone() for name,x in reader.state_dict().items()}
    text=args.fixture.read_bytes()
    decoded=json.loads(text.decode('utf-8'))
    if decoded.get('schema')!=fixture.VERSION or decoded.get('split')!='non_test_probe_v2':
        raise ValueError('FIXTURE_SCHEMA_CHANGED')
    cases=decoded['cases']
    validate_fixture(cases)
    destination.parent.mkdir(parents=True,exist_ok=True)
    destination.mkdir(exist_ok=False)
    with (destination/'ONE_SHOT_STARTED.json').open('x',encoding='utf-8') as fh:
        json.dump({'run_id':RUN_ID,'cases':192,'source':'frozen_v2','reader_sha256':PINS['reader'],
                   'fixture_sha256':PINS['fixture'],'test_opened':False},fh,sort_keys=True)
        fh.write('\n')
    per_story=[]
    for case in cases:
        per_story.append(score_case(case,model,reader,tokenizer.encode))
    if len(per_story)!=192:
        raise RuntimeError('INCOMPLETE_V2_ONESHOT')
    if not all(torch.equal(x,frozen_model[k]) for k,x in model.state_dict().items()):
        raise AssertionError('BACKBONE_CHANGED_DURING_EVALUATION')
    if not all(torch.equal(x,frozen_reader[k]) for k,x in reader.state_dict().items()):
        raise AssertionError('READER_CHANGED_DURING_EVALUATION')
    if any(p.grad is not None for p in list(model.parameters())+list(reader.parameters())):
        raise AssertionError('UNEXPECTED_GRADIENT_FOR_FROZEN_EVAL')
    report=aggregate(per_story)
    report.update({'schema':'ttm.vm.v2.nontest192.frozen_reader_one_shot.v1',
                   'run_id':RUN_ID,'cases':192,'source_pins':PINS,
                   'reader_unchanged':True,'backbone_unchanged':True,'optimizer_steps':0,
                   'dev_rescored':False,'old_probe_rescored':False,'test_opened':False,
                   'gpu_used':False,'perstory_private':True,
                   'note':'S2 closed-vocabulary structured retrieval, not open semantic TEST. No heldout confirmatory claim.'})
    with (destination/'PER_STORY_QA_PRIVATE.json').open('x',encoding='utf-8') as fh:
        json.dump(per_story,fh,sort_keys=True,indent=2); fh.write('\n')
    with (destination/'PROBE_AGGREGATE_PUBLIC.json').open('x',encoding='utf-8') as fh:
        json.dump(report,fh,sort_keys=True,indent=2); fh.write('\n')
    print(json.dumps({'status':report['verdict'],'cases':192,'TRAINING':False,
                      'TEST_NOT_OPENED':True},sort_keys=True))

if __name__=='__main__':main()
