#!/usr/bin/env python3
"""One-shot NON-TEST frozen Reader Top-k CPU evaluation. Never trains or opens TEST.

Called only with --execute-once after explicit owner GO. Frozen scientific
inputs and source are SHA-checked. One fixed 128-case PROBE, no retuning.
"""
from __future__ import annotations
import argparse
import hashlib
import json
from pathlib import Path
import numpy as np
import torch
from torch.nn import functional as F
import oracle_reader_source_only as vm
import topk_nontest_probe as probe
import topk_reader_integration as integr
from cpu_pilot_readiness import encode_target, frozen_hidden_at_answer_positions, module_from, gitblob, sha256

RUN_ID='TTM_VM_TOPK_NONTEST_FROZEN_READER_PROBE_ONCE_V1'
PIN={
 'p02':'9762343e06cf800b50574c2871ae1ed58537fb18',
 't1':'fa5bd892941ba5aa6e6b2f0b2b0ae974efe297b6',
 'reader_src':'7ce728b2874284b87933237c890e54ce3d9fd651',
 'probe_src':'b08e2120a2ac9d4e270ee48fdca77e4a4743e22c',
 'integration_src':'ccab713f8c5a4b913259088225daffcf5382be41',
 'backbone':'ee723407b2c25a18be20e26387a3dd8e4a18e2942d469279b6f0748ff86af0dc',
 't1_manifest':'cba18e60cee3d08a353ee6d4a451017289e45af7b4b1179c87171b9b78d7dfdc',
 'reader_binary':'c458de3afae87b3c381274b8edd698187df63ceac4dbbc0e6d8bd44b85c1632f',
 'probe_sha256':'88c558a8f1844ee1e55bff64f30c2b801c8bf3e54ef0cbc537f9fd81e51e9c11'
}
ARMS=('A','O1','B1','C1','B3','C3')
BOOTSTRAP_N=1000
READER_SHA='c458de3afae87b3c381274b8edd698187df63ceac4dbbc0e6d8bd44b85c1632f'

def strict_under(path:Path,root:Path)->Path:
    resolved=path.resolve(strict=True)
    if not resolved.is_relative_to(root):raise ValueError('INPUT_OUTSIDE_PROJECT_ROOT')
    return resolved

def stable_probe_bytes(cases):
    return (json.dumps({'schema':probe.SCHEMA,'split':'non_test_probe','cases':cases},sort_keys=True,separators=(',',':'))+'\n').encode('utf8')

def paired_ci(values,seed):
    x=np.asarray(values,dtype=np.float64)
    if x.shape!=(128,) or not np.isfinite(x).all():raise ValueError('BAD_PAIRED_BOOTSTRAP_VECTOR')
    index=np.random.default_rng(seed).integers(0,len(x),size=(BOOTSTRAP_N,len(x)))
    return np.quantile(x[index].mean(axis=1),[.025,.975]).tolist()

def expand_memory(memory,n):
    return vm.EncodedMemory(memory.keys.expand(n,-1,-1),memory.values.expand(n,-1,-1),memory.mask.expand(n,-1))

def score_from_memory(hidden,targets,memory,model,reader):
    if (hidden.ndim!=2 or targets.ndim!=1 or hidden.shape[0]!=targets.shape[0] or
        hidden.shape[1]!=256 or targets.shape[0]<1):raise ValueError('ANSWER_ONLY_SHAPE_MISMATCH')
    with torch.inference_mode():
        logits,gate=vm.logits_from_hidden(hidden,model.head.weight,reader,expand_memory(memory,len(targets)))
        loss=F.cross_entropy(logits,targets,reduction='none').mean().item()
    if not np.isfinite(loss):raise ValueError('NONFINITE_NLL')
    return float(loss),float(gate.mean().item())

def oracle_control_memory(case, mem):
    # Only arm O1 uses this gold-independent literal oracle from question.
    mask=probe.mask_from_rank(probe.oracle_upper_bound_rank(case['question'],case['correct_memory']),32,1)
    return vm.EncodedMemory(mem.correct.keys,mem.correct.values,torch.tensor([mask],dtype=torch.bool))

def evaluate_case(case,model,reader,t1):
    question=case['question']; answer=case['answer']
    x,positions,targets=encode_target(t1.encode,question,answer)
    with torch.no_grad():
        h=frozen_hidden_at_answer_positions(model,x,positions)
        r1=integr.encode_topk_inputs(question,case['correct_memory'],case['wrong_memory'],t1.encode,model.tok.weight,k=1)
        r3=integr.encode_topk_inputs(question,case['correct_memory'],case['wrong_memory'],t1.encode,model.tok.weight,k=3)
    if r1.rank!=r3.rank:raise AssertionError('TOP1_TOP3_RANK_CHANGED')
    if not torch.equal(r3.correct.keys,r3.wrong.keys) or not torch.equal(r3.correct.mask,r3.wrong.mask):
        raise AssertionError('CORRECT_WRONG_KEY_OR_MASK_DRIFT')
    if int(r1.correct.mask.sum())!=1 or int(r3.correct.mask.sum())!=3:
        raise AssertionError('RETRIEVAL_MASK_WRONG')
    key=case['target_key']
    index=next(i for i,v in enumerate(case['correct_memory']) if v['key']==key)
    rec1=index in r1.rank[:1];rec3=index in r3.rank[:3]
    oracle=oracle_control_memory(case,r1)
    memories={'A':r1.none,'O1':oracle,'B1':r1.correct,'C1':r1.wrong,'B3':r3.correct,'C3':r3.wrong}
    results={}
    for arm in ARMS:
        loss,gate=score_from_memory(h,targets,memories[arm],model,reader)
        results[arm]={'nll':loss,'gate':gate}
    if results['A']['gate']!=0:raise AssertionError('NO_MEMORY_GATE_NOT_ZERO')
    with torch.inference_mode():
        direct=F.cross_entropy(F.linear(h,model.head.weight),targets,reduction='none').mean().item()
    if results['A']['nll']!=direct:raise AssertionError('NO_MEMORY_NOT_EXACT_BACKBONE')
    # If the correct target did not get retrieved, value swap cannot impact logits.
    for k in (1,3):
        if (k==1 and not rec1) or (k==3 and not rec3):
            if results['B'+str(k)]['nll']!=results['C'+str(k)]['nll']:
                raise AssertionError('TARGET_MISSING_BUT_SWAP_CHANGED_NLL')
    lexical=probe.rank_lexical_full_question(question,case['correct_memory'])
    return {'case_id':case['case_id'],'r1':rec1,'r3':rec3,
            'lex1':index in lexical[:1],'lex3':index in lexical[:3],
            'answer_tokens':len(targets),'arm_nll':{a:results[a]['nll'] for a in ARMS},
            'arm_gate':{a:results[a]['gate'] for a in ARMS}}

def main():
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument('--execute-once',action='store_true')
    for name in ('project-root','checkout','checkpoint','reader','t1-manifest','output-dir'):
        p.add_argument('--'+name,type=Path,required=True)
    args=p.parse_args()
    if not args.execute_once:raise SystemExit('DENY_NO_EXECUTE_ONCE_OPTIN')
    root=args.project_root.resolve(strict=True)
    checkout=strict_under(args.checkout,root)
    private_reader=strict_under(args.reader,root)
    checkpoint=strict_under(args.checkpoint,root)
    manifest=strict_under(args.t1_manifest,root)
    destination=args.output_dir.resolve()
    if destination != (root/'_evidence'/'vector-memory'/RUN_ID).resolve():
        raise ValueError('WRONG_FROZEN_OUTPUT_RUN_ID')
    if destination.exists():raise FileExistsError('ONE_SHOT_ALREADY_STARTED_DO_NOT_RETRY')
    if torch.cuda.is_initialized():raise ValueError('CUDA_ALREADY_INITIALIZED_FAIL_CLOSED')
    if not destination.is_relative_to(root):raise ValueError('OUTPUT_OUTSIDE_ROOT')
    root_src=checkout/'tools/research/vector-memory'
    paths={'p02':checkout/'tools/pilot_t4/integrated/p02_source_exact.py',
           't1':checkout/'tools/pilot_t4/integrated/source_t2/ttm_gpt2_bpe2048.py',
           'reader_src':root_src/'oracle_reader_source_only.py',
           'probe_src':root_src/'topk_nontest_probe.py',
           'integration_src':root_src/'topk_reader_integration.py'}
    for name,path in paths.items():
        if gitblob(path)!=PIN[name]:raise ValueError('SOURCE_GIT_BLOB_MISMATCH:'+name)
    if sha256(checkpoint)!=PIN['backbone']:raise ValueError('BACKBONE_SHA_MISMATCH')
    if sha256(manifest)!=PIN['t1_manifest']:raise ValueError('T1_MANIFEST_SHA_MISMATCH')
    if sha256(private_reader)!=PIN['reader_binary']:raise ValueError('READER_SHA_MISMATCH')
    if PIN['reader_binary']!=READER_SHA:raise ValueError('READER_PIN_INCONSISTENT')
    torch.set_num_threads(2)
    torch.use_deterministic_algorithms(True)
    torch.manual_seed(20261112)
    ck=torch.load(checkpoint,map_location='cpu',weights_only=True)
    if ck['step']!=1280 or ck['p02_git_blob']!=PIN['p02']:raise ValueError('CHECKPOINT_METADATA_MISMATCH')
    p02=module_from('vm_topk_pinned_p02',paths['p02'])
    t1_source=module_from('vm_topk_pinned_t1',paths['t1'])
    t1=t1_source.BPE2048.from_manifest(json.loads(manifest.read_text(encoding='utf8')))
    if t1.source_kind!='PINNED_TINYSTORIES_TRAIN':raise ValueError('NOT_REAL_T1')
    model=p02.GPT(p02.P02Config(**ck['config'])).cpu().eval()
    model.load_state_dict(ck['model'],strict=True)
    model.requires_grad_(False)
    if model.tok.weight.data_ptr()!=model.head.weight.data_ptr():raise ValueError('BACKBONE_HEAD_NOT_TIED')
    orig={k:v.clone() for k,v in model.state_dict().items()}
    reader=vm.GatedOracleReader().cpu().eval()
    payload=torch.load(private_reader,map_location='cpu',weights_only=True)
    integr.validate_l0020_private_payload(payload,reader)
    reader.load_state_dict(payload['reader_state_dict'],strict=True)
    reader.requires_grad_(False)
    original_reader_state={k:v.clone() for k,v in reader.state_dict().items()}
    cases=probe.build()
    if hashlib.sha256(stable_probe_bytes(cases)).hexdigest()!=PIN['probe_sha256']:
        raise ValueError('PROBE_SHA256_MISMATCH')
    if len(cases)!=128 or any(len(c['correct_memory'])!=32 or c['split']!='non_test_probe' for c in cases):
        raise ValueError('PROBE_SCHEMA_ERROR')
    for c in cases:
        if c['answer'] in c['question'] or c['question'].count(c['target_key'])!=1:
            raise ValueError('PROBE_QUESTION_GOLD_LEAK_OR_TARGET_INVALID')
        good,bad=c['correct_memory'],c['wrong_memory']
        if ([x['key'] for x in good]!=[x['key'] for x in bad] or
            sum(x['key']==c['target_key'] for x in good)!=1 or
            any(x['value']!=y['value'] for x,y in zip(good,bad) if x['key']!=c['target_key'])):
            raise ValueError('PROBE_FOIL_NOT_TARGET_VALUE_ONLY')
        if next(x['value'] for x in good if x['key']==c['target_key'])!=c['answer'] or any(x['value']==c['answer'] for x in bad):
            raise ValueError('PROBE_TARGET_VALUE_NOT_COUNTERFACTUAL')
    destination.parent.mkdir(parents=True,exist_ok=True)
    destination.mkdir(exist_ok=False) # single-use marker, intentionally not cleaned on failure
    (destination/'ONE_SHOT_STARTED.json').write_text(json.dumps({'run_id':RUN_ID,'probe_cases':128,
            'reader_sha256':PIN['reader_binary'],'test_opened':False},sort_keys=True)+'\n')
    per_story=[]
    for case in cases:
        per_story.append(evaluate_case(case,model,reader,t1))
    if len(per_story)!=128:raise AssertionError('INCOMPLETE_PROBE')
    if not all(torch.equal(x,orig[k]) for k,x in model.state_dict().items()):
        raise AssertionError('FROZEN_BACKBONE_MUTATED')
    if any(p.grad is not None for p in list(reader.parameters())+list(model.parameters())):
        raise AssertionError('UNEXPECTED_GRADIENT')
    if not all(torch.equal(v,original_reader_state[k]) for k,v in reader.state_dict().items()):
        raise AssertionError('FROZEN_READER_STATE_MUTATED')
    results={a:float(np.mean([x['arm_nll'][a] for x in per_story])) for a in ARMS}
    recall={k:float(np.mean([x[k] for x in per_story])) for k in ('r1','r3','lex1','lex3')}
    dA=np.array([x['arm_nll']['A']-x['arm_nll']['B3'] for x in per_story])
    dC=np.array([x['arm_nll']['C3']-x['arm_nll']['B3'] for x in per_story])
    ciA=paired_ci(dA,20261114);ciC=paired_ci(dC,20261115)
    pass_recall=recall['r3']>=.95
    pass_nll=dA.mean()>=.05 and dC.mean()>=.05 and ciA[0]>0 and ciC[0]>0
    if results['A']-results['O1'] < .05:verdict='HOLD_ORACLE_READER_PROBE_DOMAIN_SHIFT'
    elif not pass_recall:verdict='FAIL_RETRIEVAL_SCOPED'
    elif not pass_nll:verdict='FAIL_TOP3_FROZEN_READER_SCOPED'
    else:verdict='GO_CANDIDATE_NONTEST_SCOPED'
    report={
        'schema':'ttm.vm.externalfacts.topk.nontest_frozen_reader_one_shot.v1',
        'run_id':RUN_ID,'verdict':verdict,'source_pins':PIN,
        'cases':128,'cards_per_case':32,'reader_training_steps':128,
        'reader_training_repeated':False,'optimizer_steps':0,'test_opened':False,
        'dev_rescored':False,'gpu_used':False,'backbone_unchanged':True,
        'reader_unchanged':True,'bootstrap_replicates':BOOTSTRAP_N,
        'nll_mean_story':results,'recall':recall,
        'mean_paired_delta':{'A_minus_B3':float(dA.mean()),'C3_minus_B3':float(dC.mean())},
        'bootstrap95':{'A_minus_B3':ciA,'C3_minus_B3':ciC},
        'answer_tokens_each_arm':sum(x['answer_tokens'] for x in per_story),
        'per_story_saved_private':True,
        'limit':'Non-TEST exploratory PROBE; Top3 outside singleton Oracle training distribution; no TEST release.'
    }
    (destination/'PER_STORY_QA_PRIVATE.json').write_text(json.dumps(per_story,sort_keys=True,indent=2)+'\n')
    (destination/'PROBE_AGGREGATE_PUBLIC.json').write_text(json.dumps(report,sort_keys=True,indent=2)+'\n')
    print(json.dumps({'status':verdict,'cases':128,'TEST_NOT_OPENED':True,'TRAINING':False},sort_keys=True))

if __name__=='__main__':main()
