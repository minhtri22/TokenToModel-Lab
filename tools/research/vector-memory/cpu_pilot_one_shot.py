#!/usr/bin/env python3
"""SEALED CPU science runner: external facts, fixed 128-step TRAIN + one DEV.

NOT launched by prereg/readiness. Running requires explicit --execute-once.
TEST decryption, TEST paths, GPU, checkpoint updates, auto-resume and hyperparam
search are not implemented. Results are written only under owner project root.
"""
from __future__ import annotations
import argparse, hashlib, importlib.util, json, math, os, sys
from pathlib import Path
import numpy as np
import torch
from torch import nn
from torch.nn import functional as F

from cpu_pilot_readiness import PIN, SEED, sha256, gitblob, module_from, encode_target, frozen_hidden_at_answer_positions

STEPS, BATCH, LR = 128, 16, .001
RUN_ID='TTM_VM_EXTERNAL_FACTS_CPU_ORACLE_TRAIN_DEV_20261111_V1'

def read_fixture(path:Path, expected_blob:str, expected_split:str, n:int):
    if gitblob(path)!=expected_blob:raise ValueError('FIXTURE_SOURCE_PIN_MISMATCH')
    obj=json.loads(path.read_text('utf8'))
    if obj['split']!=expected_split or len(obj['cases'])!=n:raise ValueError('FIXTURE_SPLIT_COUNT_MISMATCH')
    return obj['cases']

def prepare_case(model,vm,case,encode):
    from cpu_pilot_readiness import encode_target, frozen_hidden_at_answer_positions
    x,starts,targets=encode_target(encode,case['question'],case['answer'])
    h=frozen_hidden_at_answer_positions(model,x,starts)
    good=vm.encode_cards_for_reader([case['question']],[case['correct_memory']],encode,model.tok.weight)
    bad=vm.encode_cards_for_reader([case['question']],[case['wrong_memory']],encode,model.tok.weight)
    if not torch.equal(good.keys,bad.keys) or not torch.equal(good.mask,bad.mask):
        raise ValueError('FACT_CONTROL_DIFFERENT_KEYS')
    if good.mask.sum().item()!=1 or torch.equal(good.values[good.mask],bad.values[bad.mask]):
        raise ValueError('ORACLE_OR_VALUE_FOIL_MISMATCH')
    return {'h':h,'targets':targets,'good':good,'bad':bad,'case_id':case['case_id']}

def collate(batch,vm,arm:str):
    if arm not in ('correct','wrong','none'):raise ValueError('UNKNOWN_ARM')
    hidden, targets, keys, vals, masks, owners=[],[],[],[],[],[]
    for j,item in enumerate(batch):
        n=len(item['targets']);hidden.append(item['h']);targets.append(item['targets']);owners.extend([j]*n)
        if arm=='none':
            # No-memory is a true bypass. No memory key/value extraction.
            continue
        m=item['good'] if arm=='correct' else item['bad']
        keys.append(m.keys.expand(n,-1,-1))
        vals.append(m.values.expand(n,-1,-1))
        masks.append(m.mask.expand(n,-1))
    h=torch.cat(hidden); y=torch.cat(targets)
    if arm=='none':
        mem=vm.EncodedMemory(h.new_zeros((len(y),0,256)),h.new_zeros((len(y),0,256)),torch.zeros((len(y),0),dtype=torch.bool))
    else:
        mem=vm.EncodedMemory(torch.cat(keys),torch.cat(vals),torch.cat(masks))
    return h,y,mem,torch.tensor(owners,dtype=torch.long)

def losses_and_gates(reader,vm,model,batch,arm):
    hidden, targets, mem, owners=collate(batch,vm,arm)
    logits, gates=vm.logits_from_hidden(hidden,model.head.weight,reader,mem)
    losses=F.cross_entropy(logits,targets,reduction='none')
    sums=losses.new_zeros(len(batch)).index_add(0,owners,losses)
    counts=torch.bincount(owners,minlength=len(batch)).to(losses.dtype)
    story_losses=sums/counts
    return story_losses, len(targets), float(gates.detach().mean())

def bootstrap_delta(values,seed=20261112):
    rng=np.random.default_rng(seed)
    v=np.asarray(values,dtype=np.float64)
    ix=rng.integers(0,len(v),size=(1000,len(v)))
    return np.quantile(v[ix].mean(axis=1),[.025,.975]).tolist()

def main():
    ap=argparse.ArgumentParser()
    ap.add_argument('--execute-once',action='store_true',help='Explicit science execution, never used by preflight')
    ap.add_argument('--project-root',type=Path,required=True)
    ap.add_argument('--checkout',type=Path,required=True)
    ap.add_argument('--checkpoint',type=Path,required=True)
    ap.add_argument('--t1-manifest',type=Path,required=True)
    ap.add_argument('--t1-owner-receipt',type=Path,required=True)
    ap.add_argument('--output-dir',type=Path,required=True)
    args=ap.parse_args()
    if not args.execute_once:raise SystemExit('NOT_AUTHORIZED_EXECUTION: --execute-once required')
    root=args.project_root.resolve(strict=True)
    checkout=args.checkout.resolve(strict=True)
    if not checkout.is_relative_to(root):raise ValueError('CHECKOUT_MUST_BE_INSIDE_PROJECT_ROOT')
    dest=args.output_dir.resolve()
    expected_dest=(root/'_evidence'/'vector-memory'/RUN_ID).resolve()
    if dest!=expected_dest:raise ValueError('ONE_SHOT_OUTPUT_PATH_NOT_FROZEN')
    if not dest.is_relative_to(root) or dest==root:raise ValueError('OUTPUT_OUTSIDE_PROJECT_ROOT')
    for source_file in (args.checkpoint,args.t1_manifest,args.t1_owner_receipt):
        if not source_file.resolve().is_relative_to(root):raise ValueError('PRIVATE_INPUT_OUTSIDE_PROJECT_ROOT')
    if dest.exists():raise FileExistsError('ONE_SHOT_CONSUMED_OR_PARTIAL_NO_OVERWRITE')
    source=checkout/'tools/pilot_t4/integrated/p02_source_exact.py'
    t1src=checkout/'tools/pilot_t4/integrated/source_t2/ttm_gpt2_bpe2048.py'
    reader_src=checkout/'tools/research/vector-memory/oracle_reader_source_only.py'
    train_file=checkout/'artifacts/research/vector-memory/TTM_EXTERNAL_FACTS_TRAIN_256_V1.json'
    dev_file=checkout/'artifacts/research/vector-memory/TTM_EXTERNAL_FACTS_DEV_64_V1.json'
    if sha256(args.checkpoint)!=PIN['checkpoint_sha256']:raise ValueError('CHECKPOINT_MISMATCH')
    if sha256(args.t1_manifest)!=PIN['t1_manifest_sha256']:raise ValueError('T1_MANIFEST_MISMATCH')
    if sha256(args.t1_owner_receipt)!=PIN['owner_receipt_sha256']:raise ValueError('T1_RECEIPT_SHA_MISMATCH')
    owner=json.loads(args.t1_owner_receipt.read_text('utf8'))
    if owner['status']!='PASS_REAL_T1_TOKENIZER' or owner['test_status']!='NOT_READ_OR_DECRYPTED' or owner['answer_boundary_prefix_mismatches']!=0 or owner['input_cases']!=320:
        raise ValueError('T1_RECEIPT_NOT_PASS')
    if gitblob(source)!=PIN['p02_git_blob'] or gitblob(reader_src)!=PIN['reader_git_blob']:
        raise ValueError('PINNED_P02_OR_READER_SOURCE_MISMATCH')
    torch.set_num_threads(2)
    torch.manual_seed(SEED)
    torch.use_deterministic_algorithms(True)
    p02=module_from('vm_science_original_p02',source)
    vm=module_from('vm_science_oracle_reader',reader_src)
    t1=module_from('vm_science_pinned_t1',t1src)
    manifest=json.loads(args.t1_manifest.read_text('utf8'))
    tok=t1.BPE2048.from_manifest(manifest)
    if tok.source_kind!='PINNED_TINYSTORIES_TRAIN':raise ValueError('NOT_REAL_T1')
    data_train=read_fixture(train_file,PIN['train_git_blob'],'train',256)
    data_dev=read_fixture(dev_file,PIN['dev_git_blob'],'dev',64)
    if {c['case_id'] for c in data_train}&{c['case_id'] for c in data_dev}:
        raise ValueError('SPLIT_OVERLAP')
    ck=torch.load(args.checkpoint,map_location='cpu',weights_only=True)
    if ck['step']!=1280 or ck['p02_git_blob']!=PIN['p02_git_blob']:
        raise ValueError('TRAINED_P02_METADATA_BAD')
    model=p02.GPT(p02.P02Config(**ck['config'])).cpu().eval()
    model.load_state_dict(ck['model'],strict=True)
    model.requires_grad_(False)
    before={k:v.detach().clone() for k,v in model.state_dict().items()}
    if model.head.weight.data_ptr()!=model.tok.weight.data_ptr():raise ValueError('NOT_TIED_HEAD')
    with torch.no_grad():
        train=[prepare_case(model,vm,c,tok.encode) for c in data_train]
        dev=[prepare_case(model,vm,c,tok.encode) for c in data_dev]
    reader=vm.GatedOracleReader().cpu().train()
    # Oracle masks exactly one key, so q/key projections cannot learn selection.
    # Freeze them deliberately; train only value projection, residual and gate.
    reader.query_proj.requires_grad_(False)
    reader.key_proj.requires_grad_(False)
    learned=[p for p in reader.parameters() if p.requires_grad]
    optimizer=torch.optim.AdamW(learned,lr=LR,weight_decay=0.)
    # One-shot marker created BEFORE optimizer starts, retained even on failure.
    dest.parent.mkdir(parents=True,exist_ok=True)
    dest.mkdir(exist_ok=False)
    (dest/'ONE_SHOT_STARTED.json').write_text(json.dumps({'run_id':RUN_ID,'steps_planned':STEPS,'test_opened':False},sort_keys=True)+'\n',encoding='utf8')
    losses=[]
    for epoch in range(8):
        order=torch.randperm(256,generator=torch.Generator().manual_seed(SEED+epoch)).tolist()
        for i in range(0,256,BATCH):
            mini=[train[j] for j in order[i:i+BATCH]]
            optimizer.zero_grad(set_to_none=True)
            story_losses,_,_=losses_and_gates(reader,vm,model,mini,'correct')
            loss=story_losses.mean();loss.backward()
            torch.nn.utils.clip_grad_norm_(learned,1.0)
            optimizer.step()
            losses.append(float(loss.detach()))
    if len(losses)!=STEPS:raise AssertionError('BUDGET_STEPS_MISMATCH')
    reader.eval()
    # ONE DEV pass, fixed final checkpoint. No candidate/seed search.
    with torch.no_grad():
        results={}
        for arm in ['none','correct','wrong']:
            stories=[];count=0;gates=[]
            for item in dev:
                ll,n,g=losses_and_gates(reader,vm,model,[item],arm)
                stories.append(float(ll.item()));count+=n;gates.append(g)
            results[arm]={'mean_story_nll':float(np.mean(stories)),
                          'answer_tokens':count,'gate_mean':float(np.mean(gates)),
                          '_losses_private':stories}
    A=np.asarray(results['none']['_losses_private']);B=np.asarray(results['correct']['_losses_private']);C=np.asarray(results['wrong']['_losses_private'])
    a_minus_b=A-B;c_minus_b=C-B
    ci_a=bootstrap_delta(a_minus_b);ci_c=bootstrap_delta(c_minus_b,seed=20261113)
    pass_dev=bool(a_minus_b.mean()>=.05 and c_minus_b.mean()>=.05 and ci_a[0]>0 and ci_c[0]>0)
    for arm in results:results[arm].pop('_losses_private')
    if not all(torch.equal(t,before[k]) for k,t in model.state_dict().items()):
        raise AssertionError('CHECKPOINT_MUTATED')
    torch.save({'reader_state_dict':reader.state_dict(),'source_pins':PIN,'steps':STEPS},dest/'reader_private.pt')
    public={'schema':'ttm.vm.externalfacts.cpu_oracle_train_dev.one_shot.v1',
            'status':'DEV_SCREEN_GO_CANDIDATE' if pass_dev else 'DEV_SCREEN_NO_GO',
            'run_id':RUN_ID,'sources':PIN,'steps':STEPS,'batch':BATCH,'seed':SEED,
            'train_stories':256,'dev_stories':64,'test_opened':False,
            'checkpoint_unchanged':True,'reader_trainable_count':sum(p.numel() for p in learned),
            'dev_arms':results,'paired_mean_deltas':{'no_minus_correct':float(a_minus_b.mean()),'wrong_minus_correct':float(c_minus_b.mean())},
            'bootstrap95':{'no_minus_correct':ci_a,'wrong_minus_correct':ci_c},
            'oracle_only':True,'retriever_topk_not_tested':True,'science_limit':'DEV only; no TEST, no tuning'}
    (dest/'DEV_AGGREGATE_PUBLIC.json').write_text(json.dumps(public,ensure_ascii=False,sort_keys=True,indent=2)+'\n',encoding='utf8')
    print(json.dumps({'status':public['status'],'steps':STEPS,'TEST_NOT_OPENED':True},sort_keys=True))

if __name__=='__main__':main()
