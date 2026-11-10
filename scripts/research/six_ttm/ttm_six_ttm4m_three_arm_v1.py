#!/usr/bin/env python3
"""TTM x SIX: source-verified, TEST-free three-arm TTM-Small-4M exploratory adaptation.

Never run with original TTM/G1 private TEST or original science lock. An explicit NEW
owner pilot approval file is necessary for the GPU path. This is an exploratory
48/16 DEV-only screen, NOT G1 confirmatory. No teacher model calls or downloads.
"""
from __future__ import annotations
import argparse
import hashlib
import importlib.util
import io
import json
import os
from pathlib import Path
import random
import shutil
import sys
import time
import zipfile

import numpy as np

# Exact original versions, not user-repointable mutable model/teacher aliases.
EXPERIMENT = 'TTM_SIX_TTM4M_FUNCTIONAL_TRANSFER_PUBLIC48_DEV16_V1'
OWNER_APPROVAL = 'APPROVE_TTM_SIX_TTM4M_FUNCTIONAL_PILOT_T4_V1'
RUN_ID = 'ttm_six_ttm4m_functional_transfer_public48_dev16_v1'
SOURCE_GIT_BLOB = 'c82ff40c0187677e6753db3beb56e7c93ea7d1b3'
SOURCE_SHA256 = '9688deb1d1157c93fb7090e5b1c12ea4bc56ed0dedadb0597d84ceb4e68e82eb'
QWEN_ZIP_SHA256 = '6f98560117219cf3cecc37fb87ff562a784fe82238d9b2d831cbda7634488d9f'
QWEN_MANIFEST_SHA = 'ae86b8e847e74c97b7f69d88a08f133902173bc4c4df104f413447c1cd6fa40d'
P02_GIT_BLOB = '9762343e06cf800b50574c2871ae1ed58537fb18'
BPE_GIT_BLOB = 'fa5bd892941ba5aa6e6b2f0b2b0ae974efe297b6'
BPE_MANIFEST_SHA = 'cba18e60cee3d08a353ee6d4a451017289e45af7b4b1179c87171b9b78d7dfdc'
CHECKPOINT_SHA = 'ee723407b2c25a18be20e26387a3dd8e4a18e2942d469279b6f0748ff86af0dc'
READY_SHA = 'eb89d0a797451187ed20956d1f0097e9a8b9539da8eeaa92960e2a8508c9095f'
CONFIG = {'vocab_size': 2048, 'max_seq_len': 256, 'n_embd': 256,
          'n_layer': 4, 'n_head': 4, 'norm_type': 'layernorm'}
TEACHER_FILES = {'g1_explore_public_qwen_dev_v1.py',
                 'results/manifest_receipt.json', 'results/result.json',
                 'results/source_features.npz', 'results/target_features.npz'}
EXPECTED_MODELS = {'source':'c1899de289a04d12100db370d81485cdf75e47ca',
                   'target':'70d244cc86ccca08cf5af4e1e306ecf908b1ad5e'}
TEMPLATE_BASELINE = 0.05202296104592581
TRAIN_N, DEV_N, SEED = 48, 16, 20261112
EPOCHS, BATCHES_PER_EPOCH, UPDATES = 12, 6, 72
WALL_CAP = 1200


def need(condition, code):
    if not condition:
        raise RuntimeError('TTM_SIX_STOP_' + code)


def sha_file(path):
    h = hashlib.sha256()
    with Path(path).open('rb') as f:
        for b in iter(lambda: f.read(4 << 20), b''):
            h.update(b)
    return h.hexdigest()


def sha_bytes(b):
    return hashlib.sha256(b).hexdigest()


def git_blob(path):
    b = Path(path).read_bytes()
    return hashlib.sha1(b'blob ' + str(len(b)).encode() + b'\0' + b).hexdigest()


def import_exact(path, blob, name):
    path = Path(path)
    need(path.is_file() and not path.is_symlink(), 'SOURCE_MISSING_OR_SYMLINK_'+name)
    need(git_blob(path) == blob, 'SOURCE_GIT_BLOB_CHANGED_'+name)
    spec = importlib.util.spec_from_file_location(name, path)
    obj = importlib.util.module_from_spec(spec)
    sys.modules[name] = obj
    spec.loader.exec_module(obj)
    return obj


def freeze_teacher(zip_path, source_module_path):
    """Only safe, expected cached data. Rebuild prompts from exact source; no Qwen calls."""
    need(sha_file(zip_path) == QWEN_ZIP_SHA256, 'QWEN_ZIP_SHA')
    mod = import_exact(source_module_path, SOURCE_GIT_BLOB, 'frozen_qwen_public_source')
    need(sha_file(source_module_path) == SOURCE_SHA256, 'QWEN_SOURCE_SHA')
    train, dev = mod.build_rows()
    need(len(train)==TRAIN_N and len(dev)==DEV_N, 'PROMPT_COUNTS')
    need(len({r['group'] for r in train})==12 and len({r['group'] for r in dev})==4, 'GROUP_COUNT')
    need(not ({r['group'] for r in train}&{r['group'] for r in dev}), 'GROUP_LEAK')
    rows = train+dev
    need(len({r['prompt_sha256'] for r in rows})==64, 'PROMPT_DUP')
    manifest = mod.manifest()
    calculated_manifest_sha = sha_bytes(json.dumps(manifest,sort_keys=True,separators=(',',':')).encode())
    need(calculated_manifest_sha == QWEN_MANIFEST_SHA, 'MANIFEST_RECONSTRUCTION')
    with zipfile.ZipFile(zip_path) as z:
        need(z.testzip() is None, 'ZIP_CRC')
        need(set(z.namelist())==TEACHER_FILES, 'ZIP_ALLOWLIST')
        need(not any(i.is_dir() for i in z.infolist()), 'ZIP_DIRECTORY')
        need(z.read('g1_explore_public_qwen_dev_v1.py') == Path(source_module_path).read_bytes(), 'SOURCE_IN_ZIP')
        meta = json.loads(z.read('results/manifest_receipt.json'))
        result = json.loads(z.read('results/result.json'))
        for k in ('manifest_sha256', 'source_code_sha256'):
            expect = QWEN_MANIFEST_SHA if k.startswith('manifest') else SOURCE_SHA256
            need(meta.get(k)==expect and result.get(k)==expect, 'CACHE_'+k)
        need(result.get('model_revisions')==EXPECTED_MODELS,'MODEL_REVISIONS')
        need(result.get('exploratory_qwen_inference_executed') is True and
             result.get('G1_original_science_executed') is False and
             result.get('G1_private_TEST_opened') is False, 'TEACHER_SCOPE')
        need(result.get('train_rows')==48 and result.get('dev_rows')==16, 'TEACHER_COUNTS')
        with np.load(io.BytesIO(z.read('results/target_features.npz')),allow_pickle=False) as d:
            need(d['manifest_sha256'].item()==QWEN_MANIFEST_SHA,'TEACHER_NPZ_MANIFEST')
            scores = np.array(d['probe'],dtype=np.float64,copy=True)
            need(d['hidden'].shape==(64,2048),'TARGET_HIDDEN_SHAPE')
            need(np.isfinite(d['hidden']).all(),'TARGET_HIDDEN_FINITE')
        with np.load(io.BytesIO(z.read('results/source_features.npz')),allow_pickle=False) as d:
            need(d['manifest_sha256'].item()==QWEN_MANIFEST_SHA and
                 d['hidden'].shape==(64,1024), 'SOURCE_NPZ_SHAPE_OR_MANIFEST')
            need(np.isfinite(d['hidden']).all(),'SOURCE_NPZ_FINITE')
    need(scores.shape==(64,2) and np.isfinite(scores).all(),'TEACHER_SCORE_SHAPE_FINITE')
    return rows, scores


def train_norms(train_rows, train_scores):
    need(len(train_rows)==TRAIN_N and train_scores.shape==(TRAIN_N,2),'TRAIN_NORMS_SCOPE')
    mean = train_scores.mean(0)
    std = train_scores.std(0)
    table = np.zeros((4,2),dtype=np.float64)
    for i in range(4):
        arr = train_scores[[k for k,r in enumerate(train_rows) if r['template']==i]]
        need(arr.shape==(12,2),'TEMPLATE_TRAIN_COUNT')
        table[i] = arr.mean(0)
    residual = train_scores - np.stack([table[r['template']] for r in train_rows])
    resid_std = residual.std(0)
    need(np.all(np.isfinite(mean)) and np.all(np.isfinite(table)) and
         np.all(std>1e-6) and np.all(resid_std>1e-6),'PROBE_NORM_DEGENERATE')
    direct = (train_scores-mean)/std
    controlled = residual/resid_std
    need(np.isfinite(direct).all() and np.isfinite(controlled).all(),'PROBE_NORM_NONFINITE')
    return {'mean':mean, 'std':std, 'template_table':table,
            'resid_std':resid_std, 'B':direct.astype(np.float32),
            'C':controlled.astype(np.float32)}


def template_mae(train_rows, dev_rows, train_scores, dev_scores):
    n = train_norms(train_rows, train_scores)
    p = np.stack([n['template_table'][x['template']] for x in dev_rows])
    return float(np.abs(p-dev_scores).mean())


def load_tokenizer(file_path, source_path, raw_prompts):
    need(sha_file(file_path)==BPE_MANIFEST_SHA,'BPE_FILE_SHA')
    bpe = import_exact(source_path, BPE_GIT_BLOB, 'frozen_ttm_bpe')
    m = json.loads(Path(file_path).read_text('utf-8'))
    need(m.get('source_kind')=='PINNED_TINYSTORIES_TRAIN','BPE_TRAIN_ONLY')
    encoder = bpe.BPE2048.from_manifest(m)
    tokens=[]
    for text in raw_prompts:
        ids = encoder.encode(text)
        need(2<=len(ids)<=256 and all(0<=x<2048 and x!=256 for x in ids),'PROMPT_TOKEN_LENGTH')
        need(encoder.decode(ids)==text, 'BPE_ROUNDTRIP')
        tokens.append(ids)
    return tokens, m['manifest_sha256']


def check_parent(checkpoint_dir):
    """Checkpoint data is trusted only after exact raw-byte digest and READY check."""
    import torch
    folder=Path(checkpoint_dir).resolve(strict=True)
    need(folder.is_dir() and folder.name=='step_1280','PARENT_DIRECTORY')
    cp=folder/'checkpoint.pt'; ready=folder/'READY.json'
    for f in [cp,ready]:
        need(f.is_file() and not f.is_symlink(),'PARENT_FILE_TYPE')
    need(sha_file(cp)==CHECKPOINT_SHA and sha_file(ready)==READY_SHA,'PARENT_HASH')
    m=json.loads(ready.read_text('utf-8'))
    need(m.get('schema')=='ttm.t4.ready.last.v1' and m.get('step')==1280 and
         m.get('checkpoint')=='checkpoint.pt' and m.get('sha256')==CHECKPOINT_SHA and
         m.get('bytes')==cp.stat().st_size, 'PARENT_READY')
    state=torch.load(cp,map_location='cpu',weights_only=True)
    need(state.get('schema')=='ttm.t4.science.checkpoint.v1' and
         state.get('step')==1280 and state.get('p02_git_blob')==P02_GIT_BLOB and
         state.get('config')==CONFIG and isinstance(state.get('model'),dict),'PARENT_PAYLOAD')
    need(len(state['model'])>10,'PARENT_WEIGHTS_EMPTY')
    return state['model']


def make_padded(examples, ids_list, device):
    import torch
    lengths=[len(ids_list[i]) for i in examples]
    need(all(2<=n<=256 for n in lengths),'PAD_LENGTH')
    L=max(lengths)
    x=torch.zeros((len(examples),L),dtype=torch.long,device=device)
    y=torch.full((len(examples),L),-100,dtype=torch.long,device=device)
    for bi,k in enumerate(examples):
        ids=ids_list[k]
        x[bi,:len(ids)]=torch.as_tensor(ids,dtype=torch.long,device=device)
        y[bi,:len(ids)-1]=torch.as_tensor(ids[1:],dtype=torch.long,device=device)
    need(int((y!=-100).sum().item())==sum(n-1 for n in lengths),'PAD_LABELS')
    return x,y,torch.as_tensor(np.array(lengths)-1,device=device,dtype=torch.long)


def forward_with_last_hidden(model, tokens, last_positions):
    import torch
    saved=[]
    def take_hidden(module, args, result):
        saved.append(result)
    hook=model.final_ln.register_forward_hook(take_hidden)
    try:
        logits,_=model(tokens)
    finally:
        hook.remove()
    need(len(saved)==1 and saved[0].ndim==3,'HOOK_EXPECTED_ONCE')
    hidden=saved[0][torch.arange(tokens.shape[0],device=tokens.device),last_positions]
    return logits,hidden


def schedule(train_rows):
    groups=list(dict.fromkeys(r['group'] for r in train_rows))
    need(len(groups)==12,'TRAIN_GROUPS')
    lookup={g:[i for i,r in enumerate(train_rows) if r['group']==g] for g in groups}
    need(all(len(v)==4 for v in lookup.values()),'TRAIN_GROUP_SIZE')
    items=[]
    for epoch in range(EPOCHS):
        for pair in range(BATCHES_PER_EPOCH):
            a=groups[2*pair:2*pair+2]
            items.append(lookup[a[0]]+lookup[a[1]])
    need(len(items)==UPDATES and all(len(a)==8 for a in items),'SCHEDULE_LENGTH')
    seen=np.bincount(np.concatenate(items),minlength=TRAIN_N)
    need(np.array_equal(seen,np.full(TRAIN_N,12)),'SCHEDULE_IMBALANCED')
    return items


def validate_approval(file_path):
    need(bool(file_path),'OWNER_NEW_PILOT_APPROVAL_REQUIRED')
    p=Path(file_path)
    need(p.is_file() and not p.is_symlink(),'OWNER_APPROVAL_FILE')
    a=json.loads(p.read_text('utf-8'))
    required={'experiment_id':EXPERIMENT,'decision':OWNER_APPROVAL,
              'new_pilot_only':True,'g1_original_TEST_opened':False,
              'source_zip_sha256':QWEN_ZIP_SHA256,
              'parent_checkpoint_sha256':CHECKPOINT_SHA,'model_training_permitted':True,
              'max_updates_each_arm':72, 'runner_sha256':sha_file(Path(__file__))}
    for k,v in required.items():
        need(a.get(k)==v,'OWNER_APPROVAL_'+k)
    need(a.get('owner_approved') is True,'OWNER_APPROVAL_EXPLICIT')
    need(a.get('owner_attestation') and len(str(a['owner_attestation']))>=8,'OWNER_ATTESTATION_MISSING')
    # This file prevents accidental execution. It is not a cryptographic signature.
    return a


def seed_all():
    import torch
    random.seed(SEED); np.random.seed(SEED); torch.manual_seed(SEED)
    torch.cuda.manual_seed_all(SEED)
    torch.use_deterministic_algorithms(True,warn_only=False)


def param_fingerprint(state):
    h=hashlib.sha256()
    for name,val in sorted(state.items()):
        h.update(name.encode('utf-8'))
        h.update(val.detach().cpu().contiguous().numpy().tobytes())
    return h.hexdigest()


def make_model(p02, parent, device, arm):
    import torch
    seed_all()
    model=p02.GPT(p02.P02Config(**CONFIG)).to(device)
    need(sum(p.numel() for p in model.parameters())==3749376,'TTM_MODEL_PARAM_COUNT')
    model.load_state_dict(parent,strict=True)
    fp=param_fingerprint(model.state_dict())
    head=torch.nn.Linear(256,2).to(device)
    optimizer=torch.optim.AdamW(list(model.parameters()) +
                                ([] if arm=='A' else list(head.parameters())),
                                lr=1e-4,betas=(.9,.95),weight_decay=.01)
    return model,head,optimizer,fp


def train_arm(p02, parent, arm, ids, train_rows, norms, device, start_time, tick=UPDATES):
    import torch
    from torch.nn import functional as F
    model,head,opt,fingerprint=make_model(p02,parent,device,arm)
    steps=schedule(train_rows)
    losses=[]
    target=norms.get(arm)
    if arm!='A':
        need(target is not None and target.shape==(TRAIN_N,2),'ARM_TARGET_TRAIN_ONLY')
        teacher=torch.as_tensor(target,dtype=torch.float32,device=device)
    for step,indices in enumerate(steps[:tick],1):
        need(time.monotonic()-start_time < WALL_CAP,'GPU_TIME_BUDGET')
        model.train(); head.train(); opt.zero_grad(set_to_none=True)
        x,y,pos=make_padded(indices,ids,device)
        logits,h=forward_with_last_hidden(model,x,pos)
        valid=(y!=-100).sum()
        loss_lm=F.cross_entropy(logits.float().flatten(0,1),y.flatten(),ignore_index=-100,reduction='sum')/valid
        loss=loss_lm
        if arm!='A':
            loss_aux=F.mse_loss(head(h).float(),teacher[indices])
            loss=loss+0.1*loss_aux
        need(bool(torch.isfinite(loss).item()),'TRAIN_NONFINITE')
        loss.backward()
        torch.nn.utils.clip_grad_norm_(list(model.parameters())+
                                      ([] if arm=='A' else list(head.parameters())),1.0,
                                      error_if_nonfinite=True)
        opt.step()
        if device.type=='cuda':
            need(torch.cuda.max_memory_reserved(device)/(1024**3)<12,'GPU_VRAM_LIMIT')
        losses.append(float(loss.detach().cpu()))
    return model,head,fingerprint,losses


def eval_arm(model,head,arm,ids,dev_rows,raw_dev,norms,device):
    import torch
    from torch.nn import functional as F
    model.eval();head.eval()
    by_group={};correct=[];outputs=[]
    with torch.inference_mode():
        for i,row in enumerate(dev_rows):
            x,y,pos=make_padded([TRAIN_N+i],ids,device)
            logits,h=forward_with_last_hidden(model,x,pos)
            numerator=float(F.cross_entropy(logits.float().flatten(0,1),y.flatten(),ignore_index=-100,reduction='sum'))
            count=int((y!=-100).sum())
            by_group.setdefault(row['group'],[0.0,0])
            by_group[row['group']][0]+=numerator
            by_group[row['group']][1]+=count
            if arm!='A':
                v=head(h).float().cpu().numpy()[0]
                if arm=='B': prediction=norms['mean']+norms['std']*v
                else: prediction=norms['template_table'][row['template']]+norms['resid_std']*v
                outputs.append(prediction)
    total_loss=sum(v[0] for v in by_group.values())
    total_labels=sum(v[1] for v in by_group.values())
    need(len(by_group)==4 and total_labels>0,'DEV_GROUPS_METRIC')
    result={'dev_nll':total_loss/total_labels,'dev_labels':total_labels,
            'dev_group_nll':{k:v[0]/v[1] for k,v in by_group.items()}}
    if arm!='A':
        need(len(outputs)==DEV_N,'DEV_PROBE_PRED_COUNT')
        result['dev_raw_probe_mae']=float(np.abs(np.asarray(outputs)-raw_dev).mean())
    return result


def verdict(metrics):
    a,b,c=(metrics[k] for k in 'ABC')
    needed={'dev_nll','dev_group_nll'}
    need(all(needed.issubset(metrics[k]) for k in 'ABC'),'VERDICT_METRIC_MISSING')
    gain_a=(a['dev_nll']-c['dev_nll'])/a['dev_nll']
    gain_b=(b['dev_nll']-c['dev_nll'])/b['dev_nll']
    base=min(b['dev_raw_probe_mae'],TEMPLATE_BASELINE)
    mae_gain=(base-c['dev_raw_probe_mae'])/base
    groups=sum(c['dev_group_nll'][g]<a['dev_group_nll'][g]
               for g in a['dev_group_nll'])
    status=('EXPLORATORY_FUNCTIONAL_GAIN_CANDIDATE'
            if gain_a>=.01 and gain_b>=.01 and mae_gain>=.01 and groups>=3
            else 'EXPLORATORY_NO_CLEAR_GAIN')
    return {'decision':status,'relative_dev_nll_C_vs_A':gain_a,
            'relative_dev_nll_C_vs_B':gain_b,
            'relative_probe_mae_C_vs_strongest_control':mae_gain,
            'DEV_groups_C_better_than_A':groups,
            'template_only_probe_mae':TEMPLATE_BASELINE,
            'no_formal_significance':True,'original_G1_science_lock':'HOLD'}


def atomic_copy_verified(source, destination):
    need(not destination.exists(),'OUTPUT_FILE_EXISTS_NO_OVERWRITE')
    with open(source,'rb') as s,open(destination,'xb') as d:
        shutil.copyfileobj(s,d,length=1<<20)
        d.flush();os.fsync(d.fileno())
    need(sha_file(source)==sha_file(destination),'OUTPUT_COPY_SHA')
    return sha_file(destination)


def valid_output_namespace(root):
    base=Path('/content/drive/MyDrive/TTM/ttm-six-functional-pilot-v1').resolve()
    root=Path(root).resolve()
    need(root.parent==base and root.name==RUN_ID, 'OUTPUT_NOT_UNDER_NEW_PILOT_NAMESPACE')
    need(not root.exists(), 'OUTPUT_FILE_EXISTS_NO_OVERWRITE')
    return root


def write_result_pack(out_root,metrics,model_states,info):
    """Write result.json and arm checkpoints, then READY.json last; never overwrite."""
    import torch
    root=valid_output_namespace(out_root)
    root.mkdir(parents=True,exist_ok=False)
    evidence={'schema':'ttm.six.ttm4m.three_arm_explore_result.v1',
              'experiment_id':EXPERIMENT,'source':info,'metrics':metrics,
              'decision':verdict(metrics),'g1_original_TEST_opened':False,
              'ttm_original_TEST_opened':False,'new_training_executed':True,
              'confirmatory_science':False}
    b=json.dumps(evidence,indent=2,sort_keys=True,allow_nan=False).encode()+b'\n'
    result=root/'result.json'
    with result.open('xb') as f:
        f.write(b);f.flush();os.fsync(f.fileno())
    hashes={'result.json':sha_file(result)}
    for arm in 'ABC':
        dst=root/f'arm_{arm}_weights_only.pt'
        with dst.open('xb') as f:
            torch.save(model_states[arm],f)
            f.flush();os.fsync(f.fileno())
        hashes[dst.name]=sha_file(dst)
    ready=root/'READY.json'
    with ready.open('x',encoding='utf-8') as f:
        json.dump({'schema':'ttm.six.ttm4m.three_arm_explore_ready.v1',
                   'experiment_id':EXPERIMENT,'files_sha256':hashes,
                   'decision':evidence['decision']['decision'],'TEST_used':False},f,indent=2,sort_keys=True)
        f.write('\n');f.flush();os.fsync(f.fileno())
    return evidence


def check_inputs(args):
    need(Path(args.qwen_zip).is_file() and not Path(args.qwen_zip).is_symlink(),'QWEN_ZIP_FILE')
    rows,scores=freeze_teacher(args.qwen_zip,args.qwen_source)
    norms=train_norms(rows[:TRAIN_N],scores[:TRAIN_N])
    ma=template_mae(rows[:TRAIN_N],rows[TRAIN_N:],scores[:TRAIN_N],scores[TRAIN_N:])
    need(abs(ma-TEMPLATE_BASELINE)<1e-8,'TEMPLATE_BASELINE_DRIFT')
    ids,tok_sha=load_tokenizer(args.tokenizer_manifest,args.bpe_source,[r['text'] for r in rows])
    need(len(ids)==64,'STUDENT_TOKEN_COUNTS')
    return rows,scores,norms,ids,tok_sha


def preflight(args, gpu=False):
    # All exact raw-byte checks precede owner execution and any output changes.
    rows,scores,norms,ids,tok_sha=check_inputs(args)
    import torch
    need(git_blob(args.p02_source)==P02_GIT_BLOB,'P02_GIT_BLOB')
    parent=check_parent(args.parent)
    if gpu:
        need(torch.cuda.is_available() and 'T4' in torch.cuda.get_device_name(0),'FREE_T4_REQUIRED')
        need(sys.platform.startswith('linux') and Path('/content').is_dir(),'COLAB_REQUIRED')
    return rows,scores,norms,ids,tok_sha,parent


def run(args):
    import torch
    validate_approval(args.owner_approval)
    rows,scores,norms,ids,toksha,parent=preflight(args,gpu=True)
    p02=import_exact(args.p02_source,P02_GIT_BLOB,'frozen_ttm_p02')
    out=valid_output_namespace(args.output)
    # No source/model teacher call and no original TTM train/val/test pack access.
    device=torch.device('cuda')
    start=time.monotonic();torch.cuda.reset_peak_memory_stats()
    all_metrics={};saved={};initial=None;train_last_losses={}
    # Complete ALL training arms before reading even one DEV score for evaluation.
    # This avoids adaptive tuning based on an earlier arm's DEV result.
    for arm in 'ABC':
        model,head,fp,losses=train_arm(p02,parent,arm,ids,rows[:TRAIN_N],norms,device,start)
        if initial is None:initial=fp
        need(fp==initial,'ARM_INITIAL_WEIGHTS_NOT_EQUAL')
        train_last_losses[arm]=losses[-1]
        saved[arm]={'model':{k:v.detach().cpu().clone() for k,v in model.state_dict().items()},
                    'aux_head':({k:v.detach().cpu().clone() for k,v in head.state_dict().items()} if arm!='A' else None),
                    'arm':arm,'parent_step':1280,'run_id':RUN_ID+'_'+arm.lower()}
        del model,head
        torch.cuda.empty_cache()
    for arm in 'ABC':
        model=p02.GPT(p02.P02Config(**CONFIG)).to(device)
        model.load_state_dict(saved[arm]['model'],strict=True)
        head=torch.nn.Linear(256,2).to(device)
        if arm!='A':head.load_state_dict(saved[arm]['aux_head'],strict=True)
        all_metrics[arm]=eval_arm(model,head,arm,ids,rows[TRAIN_N:],scores[TRAIN_N:],norms,device)
        all_metrics[arm]['train_loss_final']=train_last_losses[arm]
        all_metrics[arm]['updates']=UPDATES
        del model,head
        torch.cuda.empty_cache()
    # Parent is read-only diagnostic, evaluated only after all arms finish.
    model=p02.GPT(p02.P02Config(**CONFIG)).to(device)
    model.load_state_dict(parent,strict=True)
    head=torch.nn.Linear(256,2).to(device)
    all_metrics['PARENT_DIAGNOSTIC']=eval_arm(model,head,'A',ids,rows[TRAIN_N:],scores[TRAIN_N:],norms,device)
    del model,head
    torch.cuda.empty_cache()
    source={'checkpoint_sha256':CHECKPOINT_SHA, 'qwen_zip_sha256':QWEN_ZIP_SHA256,
            'qwen_model_rerun':False,'bpe_file_sha256':BPE_MANIFEST_SHA,
            'bpe_internal_sha256':toksha,'p02_git_blob':P02_GIT_BLOB,
            'initial_model_weights_sha256':initial,
            'elapsed_wall_seconds':time.monotonic()-start,
            'cuda_peak_reserved_gib':torch.cuda.max_memory_reserved()/(1024**3),
            'dev_reused_after_prior_qwen_screen':True,'original_ttm_optimizer_continued':False}
    need(source['elapsed_wall_seconds']<WALL_CAP,'CUMULATIVE_WALL_CAP')
    need(source['cuda_peak_reserved_gib']<12,'CUMULATIVE_VRAM_CAP')
    evidence=write_result_pack(out,all_metrics,saved,source)
    print(json.dumps({'STATUS':'OWNER_EXECUTED_NEW_EXPLORATORY_TTM_T4',
                      'RESULT':str(out/'result.json'),
                      'DECISION':evidence['decision'],'SCIENCE_G1_ORIGINAL':'HOLD'},indent=2))


def main():
    ap=argparse.ArgumentParser(description=__doc__)
    ap.add_argument('--mode',choices=['qa','preflight','run'],required=True)
    ap.add_argument('--qwen-zip')
    ap.add_argument('--qwen-source')
    ap.add_argument('--bpe-source')
    ap.add_argument('--tokenizer-manifest')
    ap.add_argument('--p02-source')
    ap.add_argument('--parent')
    ap.add_argument('--owner-approval')
    ap.add_argument('--output')
    args=ap.parse_args()
    if args.mode=='qa':
        print('QA_MODE_STATIC_ONLY_USE_SEPARATE_UNITTEST_FOR_CPU_VALIDATION')
        return
    for name in ('qwen_zip','qwen_source','bpe_source','tokenizer_manifest','p02_source','parent'):
        need(getattr(args,name) is not None,'MISSING_'+name)
    if args.mode=='preflight':
        rows,scores,norms,ids,tok,parent=preflight(args,gpu=False)
        print(json.dumps({'STATUS':'PRECLAIM_READONLY_OK','groups_train':12,'groups_dev':4,
                          'rows_train':48,'rows_dev':16,'checkpoint_sha256':CHECKPOINT_SHA,
                          'qwen_zip_sha256':QWEN_ZIP_SHA256,'tokenizer_sha256':BPE_MANIFEST_SHA,
                          'real_gpu_used':False,'G1_SCIENCE_LOCK':'HOLD'},indent=2))
        return
    for name in ('owner_approval','output'):
        need(getattr(args,name) is not None,'MISSING_'+name)
    run(args)


if __name__=='__main__':
    main()
