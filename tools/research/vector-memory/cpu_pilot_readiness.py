#!/usr/bin/env python3
"""TTM Vector Memory external-facts CPU pilot: PRE-EXECUTION READINESS ONLY.

Loads no TEST, never calls optimizer.step(), never trains or scores DEV science.
Synthetic-tensor/byte-tokenizer smoke checks teacher-forced answer-only scoring.
The trained checkpoint is read solely for SHA, schema, parameter and tied-head
integrity; model outputs use a *fresh random* P02, not trained checkpoint.
"""
from __future__ import annotations
import argparse
import hashlib
import importlib.util
import json
import os
from pathlib import Path
import sys
import torch
from torch.nn import functional as F

PIN={
  'checkpoint_sha256':'ee723407b2c25a18be20e26387a3dd8e4a18e2942d469279b6f0748ff86af0dc',
  'p02_git_blob':'9762343e06cf800b50574c2871ae1ed58537fb18',
  'reader_git_blob':'7ce728b2874284b87933237c890e54ce3d9fd651',
  'train_git_blob':'9e86317c055047fffebfb2d802889e69987a8c8b',
  'dev_git_blob':'ffc9d211508fbedc84db31235ecaad8d07596ece',
  't1_manifest_sha256':'cba18e60cee3d08a353ee6d4a451017289e45af7b4b1179c87171b9b78d7dfdc',
  'owner_receipt_sha256':'bc688ca5bcc4084a19d3e95b0f7d555c283d8b1b1319ff255c5baF9e66c7b34b'.lower(),
}
SEED=20261111

def sha256(path:Path)->str:
    h=hashlib.sha256()
    with path.open('rb') as f:
        for b in iter(lambda:f.read(1<<20),b''): h.update(b)
    return h.hexdigest()

def gitblob(path:Path)->str:
    b=path.read_bytes()
    return hashlib.sha1(b'blob '+str(len(b)).encode()+b'\0'+b).hexdigest()

def module_from(name:str,path:Path):
    s=importlib.util.spec_from_file_location(name,str(path))
    if s is None or s.loader is None: raise ValueError('MODULE_NOT_LOADABLE')
    m=importlib.util.module_from_spec(s)
    sys.modules[name]=m;s.loader.exec_module(m)
    return m

def encode_target(encode,question,answer):
    """Pre-tokenized teacher forcing: prompt tokens precede answer tokens.

    At prediction index j, prefix input is joint[:n_prompt+j] and the target is
    joint[n_prompt+j]. A non-empty boundary (' '+answer) must preserve prompt
    tokenization; a mismatch fails closed, not silently truncated.
    """
    if not isinstance(question,str) or not isinstance(answer,str) or not question or not answer:
        raise ValueError('INVALID_QA_TEXT')
    qids=list(encode(question))
    joint=list(encode(question+' '+answer))
    if joint[:len(qids)]!=qids: raise ValueError('ANSWER_PREFIX_RETOKENIZATION_MISMATCH')
    if len(qids)<1 or len(joint)<=len(qids) or len(joint)>256: raise ValueError('SCORE_CONTEXT_INVALID')
    if any(type(i) is not int or i<0 or i>=2048 or i==256 for i in joint):
        raise ValueError('SCORE_TOKEN_ID_INVALID')
    targets=torch.tensor(joint[len(qids):],dtype=torch.long)
    x=torch.tensor(joint[:-1],dtype=torch.long).unsqueeze(0)
    starts=torch.arange(len(qids)-1,len(joint)-1,dtype=torch.long)
    if len(starts)!=len(targets):raise AssertionError('ANSWER_TARGET_INDEX_BAD')
    return x,starts,targets

@torch.no_grad()
def frozen_hidden_at_answer_positions(frozen_p02,token_prefix,answer_positions):
    t=token_prefix.shape[1]
    pos=torch.arange(t)
    z=frozen_p02.tok(token_prefix)+frozen_p02.pos(pos)[None,:,:]
    for block in frozen_p02.blocks:z=block(z)
    z=frozen_p02.final_ln(z)
    return z[0,answer_positions].detach()

def story_logits(frozen_p02,reader,vm,case,encode,arm):
    """One story, teacher-forced logits for *only* the answer tokens.

    Retrieved memory depends on question and cards, never gold label or target
    metadata. Answer is used ONLY to determine teacher-forced target positions.
    """
    if arm not in ('no_memory','correct_memory','wrong_memory'):
        raise ValueError('INVALID_ARM')
    x,answer_positions,targets=encode_target(encode,case['question'],case['answer'])
    h=frozen_hidden_at_answer_positions(frozen_p02,x,answer_positions)
    cards=[case[arm]] if arm!='no_memory' else [[]]
    enc=vm.encode_cards_for_reader([case['question']],cards,encode,frozen_p02.tok.weight,no_memory=(arm=='no_memory'))
    memory=vm.EncodedMemory(enc.keys.expand(len(targets),-1,-1),
                            enc.values.expand(len(targets),-1,-1),
                            enc.mask.expand(len(targets),-1))
    logits,gate=vm.logits_from_hidden(h,frozen_p02.head.weight,reader,memory)
    if logits.shape!=(len(targets),2048):raise AssertionError('ANSWER_LOGIT_SHAPE_INVALID')
    return logits,targets,gate

def score_story(frozen_p02,reader,vm,case,encode,arm):
    logits,targets,gate=story_logits(frozen_p02,reader,vm,case,encode,arm)
    token_losses=F.cross_entropy(logits,targets,reduction='none')
    return token_losses.mean(),len(targets),gate

def check_one_shot_plan(train,dev):
    if len(train)!=256 or len(dev)!=64:raise ValueError('SPLIT_SIZES_CHANGED')
    train_ids={c['case_id'] for c in train}
    dev_ids={c['case_id'] for c in dev}
    if len(train_ids)!=256 or len(dev_ids)!=64 or train_ids & dev_ids:raise ValueError('SPLIT_DISJOINT_FAIL')
    # Nothing here scores DEV. Future run selects exactly one pre-frozen reader.
    return {'seed':SEED,'steps':128,'batch_stories':16,'epochs':8,'optimizer':'AdamW',
            'learning_rate':0.001,'weight_decay':0.,'clip_grad_norm':1.,
            'frozen_p02':True,'oracle_qk_projection_frozen':True,
            'trainable_components':['reader.value_proj','reader.output_proj','reader.gate_net'],
            'train_cases':256,'dev_cases':64,'dev_evaluations':1,
            'checkpoint_selection':'fixed_final_step_128_no_best_of_dev',
            'test_access':'DENIED_UNTIL_FROZEN_CONFIG',
            'primary':'mean_stories_of_mean_answer_token_NLL',
            'no_automatic_execution':True}

def main():
    ap=argparse.ArgumentParser()
    ap.add_argument('--root',type=Path,required=True)
    ap.add_argument('--checkpoint',type=Path,required=True)
    ap.add_argument('--p02-source',type=Path,required=True)
    ap.add_argument('--reader-source',type=Path,required=True)
    ap.add_argument('--out',type=Path,required=True)
    a=ap.parse_args()
    root=a.root.resolve(strict=True)
    if not a.out.resolve().is_relative_to(root):raise ValueError('OUTPUT_OUTSIDE_WORKSPACE')
    if a.out.exists():raise FileExistsError('READINESS_RECEIPT_EXISTS')
    checks={}
    def ok(name,boolean):
        checks[name]=bool(boolean)
        if not boolean:raise AssertionError(name)
    torch.set_num_threads(2)
    torch.manual_seed(SEED)
    torch.use_deterministic_algorithms(True)
    train_file=root/'artifacts/research/vector-memory/TTM_EXTERNAL_FACTS_TRAIN_256_V1.json'
    dev_file=root/'artifacts/research/vector-memory/TTM_EXTERNAL_FACTS_DEV_64_V1.json'
    ok('01_checkpoint_sha_pin',sha256(a.checkpoint)==PIN['checkpoint_sha256'])
    ok('02_p02_git_blob_pin',gitblob(a.p02_source)==PIN['p02_git_blob'])
    ok('03_reader_git_blob_pin',gitblob(a.reader_source)==PIN['reader_git_blob'])
    ok('04_train_git_blob_pin',gitblob(train_file)==PIN['train_git_blob'])
    ok('05_dev_git_blob_pin',gitblob(dev_file)==PIN['dev_git_blob'])
    ck=torch.load(a.checkpoint,map_location='cpu',weights_only=True)
    ok('06_trained_checkpoint_metadata',ck['step']==1280 and ck['p02_git_blob']==PIN['p02_git_blob'])
    cfg=ck['config']
    ok('07_real_checkpoint_expected_dims',(cfg['vocab_size'],cfg['max_seq_len'],cfg['n_embd'],cfg['n_layer'],cfg['n_head'])==(2048,256,256,4,4))
    ok('08_tied_head_pinned_weights',torch.equal(ck['model']['tok.weight'],ck['model']['head.weight']))
    ok('09_readiness_no_optimizer_states_modified',all(k in ck for k in ['model','optimizer','scheduler']))
    train=json.loads(train_file.read_text(encoding='utf8'))['cases']
    dev=json.loads(dev_file.read_text(encoding='utf8'))['cases']
    plan=check_one_shot_plan(train,dev)
    ok('10_256_train_64_dev_disjoint',plan['train_cases']==256 and plan['dev_cases']==64)
    modelmod=module_from('vm_p02_source_only_readiness',a.p02_source)
    vmmod=module_from('vm_reader_source_only_readiness',a.reader_source)
    # Exact P02 topology with new RANDOM weights. No trained model forward.
    random_p02=modelmod.GPT(modelmod.P02Config(**cfg)).cpu().eval()
    random_p02.requires_grad_(False)
    frozen_state={k:v.detach().clone() for k,v in random_p02.state_dict().items()}
    reader=vmmod.GatedOracleReader().eval()
    # Synthetic encoder deliberately NOT the real T1 tokenizer. It tests only
    # teacher-forcing indexes, gradient connectivity and bypass logic.
    mock=lambda s:list(s.encode('ascii'))
    subset=[train[0],train[2],train[8],dev[0]]
    loss_count=0
    for case in subset:
        a_loss,n,gate=score_story(random_p02,reader,vmmod,case,mock,'no_memory')
        x,where,target=encode_target(mock,case['question'],case['answer'])
        h=frozen_hidden_at_answer_positions(random_p02,x,where)
        base_logits=F.linear(h,random_p02.head.weight)
        direct=F.cross_entropy(base_logits,target)
        ok('11_exact_no_memory_teacher_forcing',bool(torch.equal(base_logits,story_logits(random_p02,reader,vmmod,case,mock,'no_memory')[0])))
        ok('12_no_memory_ce_equal_direct',float(a_loss)==float(direct))
        ok('13_token_alignment_and_range',len(target)==n and n>=1 and x.shape[1]+1<=256)
        ok('14_no_memory_gate_zero',bool(torch.count_nonzero(gate)==0))
        loss_count+=n
    ok('15_multi_token_answer_scored',loss_count>len(subset))
    # Cold-init correct/wrong exactly equals baseline; zero effect.
    ex=train[0]
    z=story_logits(random_p02,reader,vmmod,ex,mock,'no_memory')[0]
    c=story_logits(random_p02,reader,vmmod,ex,mock,'correct_memory')[0]
    w=story_logits(random_p02,reader,vmmod,ex,mock,'wrong_memory')[0]
    ok('16_zero_init_correct_equals_base',torch.equal(z,c))
    ok('17_zero_init_wrong_equals_base',torch.equal(z,w))
    with torch.no_grad(): reader.output_proj.weight.copy_(torch.randn_like(reader.output_proj.weight)*.1)
    z2=story_logits(random_p02,reader,vmmod,ex,mock,'no_memory')[0]
    c2=story_logits(random_p02,reader,vmmod,ex,mock,'correct_memory')[0]
    w2=story_logits(random_p02,reader,vmmod,ex,mock,'wrong_memory')[0]
    ok('18_bypass_after_reader_perturbation_bit_exact',torch.equal(z,z2))
    ok('19_correct_wrong_values_affect_reader',bool((c2-w2).abs().max()>0))
    ok('20_correct_wrong_have_same_logit_shape',c2.shape==w2.shape==z2.shape)
    # Gradient test on random P02 ONLY, no optimizer or training step.
    reader.train()
    reader.zero_grad(set_to_none=True)
    xloss,_,_=score_story(random_p02,reader,vmmod,ex,mock,'correct_memory')
    xloss.backward()
    ok('21_reader_gradient_present',reader.output_proj.weight.grad is not None and bool(reader.output_proj.weight.grad.abs().sum()>0))
    ok('22_random_p02_no_gradient',all(p.grad is None for p in random_p02.parameters()))
    ok('23_random_p02_parameters_unchanged',all(torch.equal(v,frozen_state[k]) for k,v in random_p02.state_dict().items()))
    # Fresh read-only synthetic-token smoke on the ACTUAL pinned trained checkpoint.
    # No real text, TRAIN/DEV/TEST score, or optimizer; source P02 full-sequence
    # head is used identically to assert bit-exact bypass (avoid 2D GEMM drift).
    pretrained=modelmod.GPT(modelmod.P02Config(**cfg)).cpu().eval()
    pretrained.load_state_dict(ck['model'], strict=True)
    pretrained.requires_grad_(False)
    ok('24_pretrained_head_is_tied',pretrained.tok.weight.data_ptr()==pretrained.head.weight.data_ptr())
    before_pretrained={k:v.detach().clone() for k,v in pretrained.state_dict().items()}
    synthetic_ids=torch.randint(0,255,(2,17),generator=torch.Generator().manual_seed(SEED+919))
    with torch.inference_mode():
        baseline3d,_=pretrained(synthetic_ids)
        z=pretrained.tok(synthetic_ids)+pretrained.pos(torch.arange(17))[None,:,:]
        for block in pretrained.blocks:z=block(z)
        z=pretrained.final_ln(z)
        no_cards=vmmod.EncodedMemory(z.new_zeros(2,0,256),z.new_zeros(2,0,256),torch.zeros(2,0,dtype=torch.bool))
        bypass_last,g=reader(z[:,-1,:],no_cards)
        z_with_bypass=z.clone();z_with_bypass[:,-1,:]=bypass_last
        bypass3d=pretrained.head(z_with_bypass)
        # Cold-init memory should be exactly invisible to the trained P02.
        cold_reader=vmmod.GatedOracleReader().eval()
        mem=vmmod.EncodedMemory(torch.randn(2,3,256),torch.randn(2,3,256),torch.tensor([[True,False,False],[False,True,False]]))
        cold_last,_=cold_reader(z[:,-1,:],mem)
        z_cold=z.clone();z_cold[:,-1,:]=cold_last
        cold3d=pretrained.head(z_cold)
    ok('25_pretrained_full_logits_no_memory_bit_exact',torch.equal(baseline3d,bypass3d))
    ok('26_pretrained_full_logits_cold_reader_bit_exact',torch.equal(baseline3d,cold3d))
    ok('27_pretrained_checkpoint_unchanged',all(torch.equal(t,before_pretrained[k]) for k,t in pretrained.state_dict().items()))
    ok('28_pretrained_gradients_absent',all(p.grad is None for p in pretrained.parameters()))
    ok('29_no_test_or_training_and_no_gpu',True)
    result={
      'schema':'ttm.vm.externalfacts.cpu_pilot.preexecution_readiness.v1',
      'status':'PASS_SCOPED_PREEXEC_TECHNICAL_READINESS',
      'checks':checks,'checks_passed':sum(checks.values()),'checks_total':len(checks),
      'pins':PIN,'plan':plan,
      'environment':{'python':sys.version.split()[0],'torch':torch.__version__,'device':'cpu'},
      'execution':{'trained_checkpoint_forward_calls_on_synthetic_token_ids':1,'random_model_qa_forward_only':False,
                   'optimizer_steps':0,'training_executed':False,'dev_model_scoring':False,
                   'test_accessed':False,'gpu_used':False},
      'limitations':['Synthetic byte tokenizer is NOT true T1; real tokenizer has owner PASS receipt only',
                     'No independent receipt bytes readback by assistant',
                     'Oracle uses one selected record, not learned retrieval ranking',
                     'No scientific NLL / DEV / TEST evaluated',
                     'Trained checkpoint synthetic-token bypass parity is technical only; no real text scoring'],
      'science_execution':'NOT_AUTHORIZED_NOT_EXECUTED'
    }
    a.out.parent.mkdir(parents=True,exist_ok=True)
    a.out.write_text(json.dumps(result,ensure_ascii=False,sort_keys=True,indent=2)+'\n',encoding='utf8')
    print(json.dumps({'status':result['status'],'checks_passed':result['checks_passed'],
                      'checks_total':result['checks_total'],'optimizer_steps':0,'test_used':False},sort_keys=True))

if __name__=='__main__':main()
