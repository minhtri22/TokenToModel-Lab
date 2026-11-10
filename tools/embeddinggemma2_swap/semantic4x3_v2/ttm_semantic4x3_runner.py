#!/usr/bin/env python3
"""TTM-Small-4M / EmbeddingGemma 2 SEMANTIC4X3 V2 one-shot scientific runner.

DOES NOT train on import, fixture, cpu-source-qa, or preflight.
Only the explicit --mode execute --owner-science-approved can create CLAIM or train.
H768 is scored only after all 12 final READY checkpoints, never in preflight.
"""
from __future__ import annotations
import argparse
import hashlib
import importlib.util
import json
import os
import sys
from pathlib import Path
import numpy as np
import torch
from torch.nn import functional as F

STUDY_ID = 'ttm_gemma2_semantic4x3_3seed_2048x4096_h768_20261110_v2'
STEPS, TARGETS, MICRO, EVERY = 2048, 4096, 8, 256
ARMS = ('PT-REAL', 'PT-PERM', 'NULL-REAL', 'NULL-PERM')
SEEDS = {
    'S1': {'model':2026111101,'null':2026111111,'perm':2026111112,'schedule':2026111113},
    'S2': {'model':2026111102,'null':2026111121,'perm':2026111122,'schedule':2026111123},
    'S3': {'model':2026111103,'null':2026111131,'perm':2026111132,'schedule':2026111133},
}
BOOT_SEED, BOOT_DRAWS = 2026111199, 2000
H768_PINS = {
    'H768_PUBLIC_SEAL.json':'9725b1254cde81b77e23b85ab479a08cafc14af0a7a536c7722ca87c7f2a5aa0',
    'H768_MEMBERSHIP_PRIVATE.json':'0ab671ae59ff4300d8257f2689261d6328afd7563c0aa66b363bc22348c1628f',
    'H768_WINDOWS_PRIVATE.npz':'1eb5b54b4bb7744e23fffd0fd755d5c91853a773dcc0d2219f777b47ba6a53df',
}
PINS = {
 'checkpoint.pt':'cb985751795c8328ad65acf7ca4c1033ce35182c1bfbdb8c38550de629cb271b',
 'candidate_initialization.pt':'c9fc798d8880c7e76636258052e9885dbb086d7b462a5b6bee5cff8b582973c3',
 'T4_PRIVATE_TRAIN_VAL_WINDOWS.npz':'184f68b4c0c800ef3e98362c2e20e1cd35baa269e926489a475664526ecd9913',
 'T4_PRIVATE_PACK_MANIFEST.json':'ef2e6e67d49b1d5a921b1051df329f15574f1c10cece0ce49468acb53322d650',
 'p02_exact.py':'e0fcac285918b66b13c8f694e6d625a0691c9b59221b43043e63f46b25ddcc07',
 'ttm_embeddinggemma2_swap.py':'d11da61e9d7bb040f3263e680f026817a513553c186ab243e184ffaf6e68cd39',
 'ttm_directswap2048_gpu_once.py':'0994f0cd91cb504f2db8478f55963813a85469807f2921e38c196248f323759e',
}
NULL_MODULE_SHA='0d71f38da356056be50a18d36f589774190178fd321e6d2e3970413d96238a2d'
MIN_DRIVE_FREE_BYTES=6*(1024**3)
EST_CHECKPOINT_BYTES=12*8*52947341
MIN_WITH_HEADROOM=max(MIN_DRIVE_FREE_BYTES,EST_CHECKPOINT_BYTES+1024**3)
DRIVE_BASE='/content/drive/MyDrive/TTM/ttm-small-pilot'


def require(cond, code):
    if not bool(cond):raise RuntimeError('HOLD_'+code)

def sha_bytes(b):return hashlib.sha256(b).hexdigest()

def sha_file(p):
    h=hashlib.sha256()
    with Path(p).open('rb') as f:
        for chunk in iter(lambda:f.read(1024*1024),b''):h.update(chunk)
    return h.hexdigest()

def canon(o):return (json.dumps(o,ensure_ascii=False,sort_keys=True,separators=(',',':'),allow_nan=False)).encode('utf-8')

def jsonread(p):return json.loads(Path(p).read_text('utf-8'))

def newjson(p,obj):
    with Path(p).open('x',encoding='utf-8') as f:
        json.dump(obj,f,ensure_ascii=False,sort_keys=True,indent=2,allow_nan=False)
        f.write('\n');f.flush();os.fsync(f.fileno())
    return sha_file(p)

def file_of(root,name):
    return root/'src'/name if name in ('p02_exact.py','ttm_embeddinggemma2_swap.py','ttm_directswap2048_gpu_once.py') else root/name

def require_sources(root,h768,code_dir):
    root=Path(root).resolve(strict=True)
    h768=Path(h768).resolve(strict=True)
    code_dir=Path(code_dir).resolve(strict=True)
    require(root.is_dir() and h768.is_dir() and code_dir.is_dir(),'SOURCE_DIRECTORY')
    for name,digest in PINS.items():
        p=file_of(root,name)
        require(p.is_file() and not p.is_symlink() and sha_file(p)==digest,'SOURCE_SHA_'+name)
    for name,digest in H768_PINS.items():
        p=h768/name
        require(p.is_file() and not p.is_symlink() and sha_file(p)==digest,'H768_SHA_'+name)
    helper=code_dir/'ttm_semantic4x3_balanced_null_cpu_qa.py'
    require(helper.is_file() and sha_file(helper)==NULL_MODULE_SHA,'NULL_SOURCE_SHA')
    return root,h768,helper

def import_file(name,file):
    spec=importlib.util.spec_from_file_location(name,str(file))
    require(spec is not None and spec.loader is not None,'MODULE_IMPORT_'+name)
    module=importlib.util.module_from_spec(spec)
    sys.modules[name]=module
    spec.loader.exec_module(module)
    return module

def model_context(root):
    sys.path.insert(0,str(root/'src'))
    import ttm_embeddinggemma2_swap as sw
    p02=sw.load_p02(file_of(root,'p02_exact.py'))
    old=import_file('ttm_sem4x3_original_c2048',file_of(root,'ttm_directswap2048_gpu_once.py'))
    ckpt=torch.load(root/'checkpoint.pt',map_location='cpu',weights_only=True)
    donor=torch.load(root/'candidate_initialization.pt',map_location='cpu',weights_only=True)
    require(ckpt.get('step')==1024 and ckpt.get('p02_git_blob')=='9762343e06cf800b50574c2871ae1ed58537fb18' and ckpt.get('train_pack_sha256')==PINS['T4_PRIVATE_TRAIN_VAL_WINDOWS.npz'],'CHECKPOINT_META')
    require(donor.get('schema')=='ttm.embeddinggemma2.token_swap.initialization.v1' and donor.get('source_checkpoint_sha256')==PINS['checkpoint.pt'] and donor.get('science_executed') is False,'DONOR_META')
    base=p02.GPT(sw.p02_config(p02)).float().eval()
    base.load_state_dict(ckpt['model'],strict=True)
    state=donor['model_state_dict'];src=state['tok.source.weight'].detach().float().clone()
    valid=state['tok.valid'].bool().clone();P=state['tok.proj.weight'].detach().float().clone()
    E0=base.tok.weight.detach().float().clone()
    require(src.shape==(2048,512) and valid.shape==(2048,) and int(valid.sum())==1917 and not bool(valid[256]),'DONOR_MAPPING')
    require(P.shape==(256,512) and E0.shape==(2048,256) and torch.equal(state['tok.fallback'],E0),'INIT_PINS')
    return sw,p02,old,ckpt,donor,src,valid,P,E0

def load_train(root):
    manifest=jsonread(root/'T4_PRIVATE_PACK_MANIFEST.json')
    require(manifest.get('schema')=='ttm.t4.private.train_val.windowpack.v1' and manifest.get('contains_test') is False and manifest.get('npz_sha256')==PINS['T4_PRIVATE_TRAIN_VAL_WINDOWS.npz'],'TRAIN_MANIFEST')
    with np.load(root/'T4_PRIVATE_TRAIN_VAL_WINDOWS.npz',allow_pickle=False) as f:
        keys={f'{prefix}_{suffix}' for prefix in ('train','val') for suffix in ('x','y','count','story_index')}
        require(set(f.files)==keys,'TRAIN_PACK_KEYS')
        d={k:f[k].astype(np.int64) for k in f.files}
    for key,n,story,total in [('train',2691,2048,498287),('val',328,256,61122)]:
        x,y,c,si=(d[f'{key}_{part}'] for part in ('x','y','count','story_index'))
        require(x.shape==(n,256) and y.shape==x.shape and c.shape==(n,) and si.shape==(n,),'TRAIN_SHAPE_'+key)
        mask=np.arange(256)[None,:]<c[:,None]
        require((c>0).all() and (c<=256).all() and (x>=0).all() and (x<2048).all() and (y[~mask]==-100).all() and (y[mask]>=0).all() and (y[mask]<2048).all() and int(c.sum())==total and np.array_equal(np.unique(si),np.arange(story)),'TRAIN_VALUES_'+key)
    return d

def load_h768_seal(hdir):
    """Hash/check frozen metadata only. Never parse H768 labels before all 12 READY."""
    pub=jsonread(hdir/'H768_PUBLIC_SEAL.json')
    member=jsonread(hdir/'H768_MEMBERSHIP_PRIVATE.json')
    require(pub['schema']=='ttm.semantic4x3.h768.public_seal.v1' and pub['status']=='H768_SEALED_NOT_SCORED' and pub['stories']==768 and pub['windows']==1000 and pub['targets']==186655,'H768_PUBLIC')
    require(pub['membership_private_sha256']==H768_PINS['H768_MEMBERSHIP_PRIVATE.json'] and pub['pack_private_sha256']==H768_PINS['H768_WINDOWS_PRIVATE.npz'],'H768_PUBLIC_HASH_BIND')
    require(pub['near_self_pairs']==pub['near_T1_TRAIN_pairs']==pub['near_T1_VALIDATION_pairs']==0 and pub['old_TEST_text_materialized'] is False and pub['old_H320_text_materialized'] is False and pub['old_H512_text_materialized'] is False and pub['claim_created'] is False and pub['model_forward_calls']==0,'H768_PROVENANCE')
    require(member['schema']=='ttm.semantic4x3.h768.private_membership.v1' and member['selection_count']==768 and len(member['story_sha256_ordered'])==768 and len(set(member['story_sha256_ordered']))==768 and len(member['story_target_counts'])==768 and sum(member['story_target_counts'])==186655,'H768_MEMBERSHIP')
    require(member['source_valid_sha256']=='94e431816c4cce81ff71e4408ff8d3bda9a42e8d2663986697c3954288cb38b4' and member['old_h512_membership_sha256']=='544c30b470f5e8718ba35fe016b0f52cac95e559020eae2806e1ff7291a03661','H768_SOURCE_MEMBER_PINS')
    return np.asarray(member['story_target_counts'],dtype=np.int64),pub

def load_h768_for_score(hdir,expected_counts):
    """Call ONLY inside post_train, AFTER 12 final READY and SCORING_START."""
    with np.load(hdir/'H768_WINDOWS_PRIVATE.npz',allow_pickle=False) as f:
        require(set(f.files)=={'x','y','count','story_index'},'H768_PACK_KEYS')
        d={k:f[k].astype(np.int64) for k in f.files}
    x,y,c,si=(d[k] for k in ('x','y','count','story_index'))
    require(x.shape==(1000,256) and y.shape==x.shape and c.shape==(1000,) and si.shape==(1000,),'H768_SHAPE')
    mask=np.arange(256)[None,:]<c[:,None]
    require((c>0).all() and (c<=256).all() and (x>=0).all() and (x<2048).all() and (y[~mask]==-100).all() and (y[mask]>=0).all() and (y[mask]<2048).all() and int(c.sum())==186655 and (si>=0).all() and (si<768).all() and np.array_equal(np.unique(si),np.arange(768)),'H768_LABELS')
    require(np.array_equal(np.bincount(si,weights=c,minlength=768).astype(np.int64),expected_counts),'H768_STORY_COUNTS')
    return d

def schedule(counts,seed,steps=STEPS,targets=TARGETS):
    rng=np.random.default_rng(seed);packets=[]
    require(len(counts)>0 and all(0<int(c)<=256 for c in counts),'SCHEDULE_INPUT')
    for _ in range(steps):
        remaining=targets;ids=[];limits=[]
        while remaining:
            j=int(rng.integers(0,len(counts)));n=min(int(counts[j]),remaining)
            require(n>0,'SCHEDULE_ZERO');ids.append(j);limits.append(n);remaining-=n
        packets.append((ids,limits))
    return packets,sha_bytes(canon(packets))

def projection_and_permutations(src,valid,P,helper,seed_label):
    ids=torch.where(valid)[0]
    seeds=SEEDS[seed_label]
    real=src.clone()
    X=real[valid].numpy().astype(np.float64)
    null_array,rank=helper.build_null(X,P.detach().numpy().astype(np.float64),seeds['null'])
    metrics=helper.metrics(X,null_array,P.detach().numpy().astype(np.float64))
    helper.check(metrics)
    require(rank==256 and np.isfinite(null_array).all(),'NULL_RANK_AND_FINITE')
    null=src.clone();null[ids]=torch.from_numpy(null_array.copy()).float()
    perm=np.random.default_rng(seeds['perm']).permutation(len(ids))
    require(not np.array_equal(perm,np.arange(len(ids))),'PERM_IDENTITY')
    pi=torch.from_numpy(perm.copy()).long()
    rperm=real.clone();rperm[ids]=real[ids][pi]
    nperm=null.clone();nperm[ids]=null[ids][pi]
    require(torch.equal(real[~valid],null[~valid]) and torch.equal(real[~valid],rperm[~valid]) and torch.equal(real[~valid],nperm[~valid]),'FALLBACK_DRIFT')
    require(torch.max(torch.abs(real[valid]@P.T-null[valid]@P.T)).item()<=1e-5,'PROJECTION_NULL_FP32')
    require(torch.max(torch.abs(rperm[valid]@P.T-nperm[valid]@P.T)).item()<=1e-5,'PROJECTION_PERM_FP32')
    rows={'PT-REAL':real,'PT-PERM':rperm,'NULL-REAL':null,'NULL-PERM':nperm}
    return rows,{'null_sha256':sha_bytes(null.numpy().tobytes()),'permutation_sha256':sha_bytes(np.asarray(perm,dtype=np.int64).tobytes()),'permuted_real_sha256':sha_bytes(rperm.numpy().tobytes()),'permuted_null_sha256':sha_bytes(nperm.numpy().tobytes()),'null_residual_rank':rank,'geometry':metrics}

def make_model(arm,model_seed,sw,p02,ckpt,donor,rows,valid,P,E0):
    require(arm in ARMS,'UNKNOWN_ARM')
    torch.manual_seed(model_seed)
    base=p02.GPT(sw.p02_config(p02)).float();base.load_state_dict(ckpt['model'],strict=True)
    m=sw.control_untied(base)
    m.tok=sw.MappedGemmaInput(rows,valid,E0,P)
    if arm=='PT-REAL':m.load_state_dict(donor['model_state_dict'],strict=True)
    for n,p in m.named_parameters():p.requires_grad_(n!='tok.source.weight')
    total=sum(p.numel() for p in m.parameters() if p.requires_grad)
    require(total==3880448,'TRAINABLE_PARAMS_'+arm)
    return m

def source_parity_and_null(sw,p02,old,ckpt,donor,src,valid,P,E0):
    torch.manual_seed(SEEDS['S1']['model'])
    ref=old.build_model('C',p02,sw,ckpt,donor).float().eval()
    m=make_model('PT-REAL',SEEDS['S1']['model'],sw,p02,ckpt,donor,src,valid,P,E0).eval()
    a=ref.state_dict();b=m.state_dict()
    require(a.keys()==b.keys() and all(torch.equal(a[k],b[k]) for k in a),'C2048_STATE_PARITY')
    probe=torch.tensor([[1,42,110,500,256,300]],dtype=torch.long)
    with torch.inference_mode():
        require(torch.equal(ref(probe)[0],m(probe)[0]),'C2048_LOGITS_PARITY')
    del ref,m
    return 'PASS_EXACT_STATE_AND_SYNTHETIC_LOGITS'

def deterministic_setup(seed):
    require(os.environ.get('CUBLAS_WORKSPACE_CONFIG')==':4096:8','CUBLAS_DETERMINISM_ENV')
    torch.backends.cuda.matmul.allow_tf32=False
    torch.backends.cudnn.allow_tf32=False
    torch.set_float32_matmul_precision('highest')
    torch.use_deterministic_algorithms(True)
    torch.manual_seed(seed);torch.cuda.manual_seed_all(seed)

def free_drive_quota_bytes():
    try:
        import google.auth
        from googleapiclient.discovery import build
        creds,_=google.auth.default(scopes=['https://www.googleapis.com/auth/drive.metadata.readonly'])
        q=build('drive','v3',credentials=creds,cache_discovery=False).about().get(fields='storageQuota(limit,usage,usageInDrive,usageInDriveTrash)').execute()['storageQuota']
        limit=int(q['limit']);used=int(q['usage'])
        require(limit>0 and 0<=used<=limit,'DRIVE_QUOTA_INVALID')
        return limit-used
    except Exception as exc:
        raise RuntimeError('HOLD_DRIVE_QUOTA_UNAVAILABLE_'+type(exc).__name__) from exc

def resource_preflight(a,out):
    require(Path('/content').is_dir() or os.environ.get('COLAB_RELEASE_TAG') is not None,'NOT_GOOGLE_COLAB')
    require(a.free_colab_confirmed,'OWNER_FREE_COLAB_NOT_CONFIRMED')
    require(torch.cuda.is_available() and torch.cuda.device_count()==1,'CUDA_COUNT')
    require('T4' in torch.cuda.get_device_name(0),'NOT_FREE_T4')
    mem=torch.cuda.get_device_properties(0).total_memory
    require(mem>=14*1024**3,'T4_REPORTED_VRAM_TOO_SMALL')
    require(a.owner_verified_free_gib>=6,'OWNER_STORAGE_ATTEST_LT6')
    quota=free_drive_quota_bytes()
    if a.mode=='resume':
        present=sum(int(checkpoint_path(out,s,arm,step).joinpath('READY.json').is_file())
            for s in SEEDS for arm in ARMS for step in range(EVERY,STEPS+1,EVERY))
        remaining=96-present
        require(quota>=max(1024**3,remaining*52947341+1024**3),'DRIVE_REMAINING_FREE_LT_BUDGET')
    else:
        require(quota>=MIN_WITH_HEADROOM,'DRIVE_FREE_LT_FROZEN_BUDGET')
    deterministic_setup(SEEDS['S1']['model'])
    return {'torch':str(torch.__version__),'numpy':str(np.__version__),'cuda':str(torch.version.cuda),
            'device':torch.cuda.get_device_name(0),'device_count':torch.cuda.device_count(),
            'visible_vram_bytes':mem}

def gpu_smoke(m):
    torch.cuda.empty_cache()
    torch.cuda.reset_peak_memory_stats()
    m=m.to('cuda:0',dtype=torch.float32).train()
    x=torch.randint(0,2048,(8,256),device='cuda:0',dtype=torch.long)
    y=torch.randint(0,2048,(8,256),device='cuda:0',dtype=torch.long)
    m.zero_grad(set_to_none=True)
    logits,_=m(x)
    loss=F.cross_entropy(logits.float().reshape(-1,2048),y.reshape(-1),reduction='mean')
    require(torch.isfinite(loss).item(),'SMOKE_SCALAR_FINITE')
    loss.backward()
    require(any(p.grad is not None for p in m.parameters() if p.requires_grad),'SMOKE_NO_GRAD')
    m.zero_grad(set_to_none=True)
    torch.cuda.synchronize()
    peak=torch.cuda.max_memory_allocated()
    require(peak<12*1024**3,'SMOKE_GPU_PEAK_GT12GIB')
    m=m.to('cpu');del m;torch.cuda.empty_cache()
    return peak

def inspect_output(a,require_absent):
    out=Path(a.drive_output).resolve()
    base=Path(DRIVE_BASE).resolve()
    require(out.name==STUDY_ID and out.parent==base and base.is_dir(),'OUTSIDE_STUDY_DRIVE_ROOT')
    if require_absent:require(not out.exists(),'STUDY_CLAIM_OR_OUTPUT_EXISTS')
    else:require(out.is_dir(),'STUDY_OUTPUT_MISSING')
    return out

def study_preflight(a,require_absent=True,gpu=True):
    root,hdir,helper_path=require_sources(a.input,a.h768,a.code_dir)
    out=inspect_output(a,require_absent) if gpu else None
    sw,p02,old,ckpt,donor,src,valid,P,E0=model_context(root)
    data=load_train(root)
    story_count,hpub=load_h768_seal(hdir)
    helper=import_file('ttm_sem4x3_frozen_null',helper_path)
    parity=source_parity_and_null(sw,p02,old,ckpt,donor,src,valid,P,E0)
    schedules={};rows_by_seed={};generated={}
    for s in SEEDS:
        rows,geo=projection_and_permutations(src,valid,P,helper,s)
        for arm in ARMS:
            require(rows[arm].shape==(2048,512),'ARM_ROW_SHAPE')
        schedule_packets,schedule_digest=schedule(data['train_count'],SEEDS[s]['schedule'])
        schedules[s]=(schedule_packets,schedule_digest)
        generated[s]=geo
        rows_by_seed[s]=rows
    env=resource_preflight(a,out) if gpu else {'gpu':'NOT_USED_CPU_QA'}
    peak=0
    if gpu:
        m=make_model('NULL-PERM',SEEDS['S1']['model'],sw,p02,ckpt,donor,rows_by_seed['S1']['NULL-PERM'],valid,P,E0)
        peak=gpu_smoke(m)
    log={'schema':'ttm.semantic4x3.study.preclaim.v1','study_id':STUDY_ID,
      'runner_sha256':sha_file(Path(__file__)),'null_module_sha256':NULL_MODULE_SHA,
      'input_pins':PINS,'h768_pins':H768_PINS,'h768_stories':768,'h768_windows':1000,'h768_targets':int(story_count.sum()),
      'h768_source_status':hpub['status'],'arm_count':12,'steps_per_arm':STEPS,'labels_per_step':TARGETS,
      'total_train_label_exposures':3*4*STEPS*TARGETS,'cpu_original_C2048_source_parity':parity,
      'generated_by_seed':generated,'schedules_sha256':{s:schedules[s][1] for s in SEEDS},
      'seeds':SEEDS,'bootstrap_seed':BOOT_SEED,'bootstrap_draws':BOOT_DRAWS,
      'env':env,'synthetic_gpu_peak_bytes':peak,'owner_science_approved':False,'claimed':False,
      'no_model_eval_on_h768_before_all_final_ready':True}
    ctx=(sw,p02,old,ckpt,donor,src,valid,P,E0,data,story_count,schedules,rows_by_seed,hdir)
    return out,log,ctx

def train_chunk(m,opt,packets,data,start,stop):
    m.train();losses=[]
    for step in range(start,stop):
        ids,limits=packets[step]
        require(sum(limits)==TARGETS,'TRAIN_BUDGET')
        opt.zero_grad(set_to_none=True);total=0.0
        for j in range(0,len(ids),MICRO):
            sel=ids[j:j+MICRO];lim=limits[j:j+MICRO]
            x=torch.from_numpy(data['train_x'][sel].copy()).to('cuda:0',dtype=torch.long)
            y=data['train_y'][sel].copy()
            for k,n in enumerate(lim):y[k,n:]=-100
            require(int((y!=-100).sum())==sum(lim),'TRAIN_MICRO_TARGET_COUNT')
            y=torch.from_numpy(y).to('cuda:0',dtype=torch.long)
            logits,_=m(x)
            loss=F.cross_entropy(logits.float().reshape(-1,2048),y.reshape(-1),ignore_index=-100,reduction='sum')/TARGETS
            require(torch.isfinite(loss).item(),'NONFINITE_TRAIN_LOSS')
            loss.backward();total+=float(loss.detach())
        params=[p for p in m.parameters() if p.requires_grad]
        require(all(p.grad is not None and torch.isfinite(p.grad).all().item() for p in params),'NONFINITE_TRAIN_GRAD')
        torch.nn.utils.clip_grad_norm_(params,1.0)
        opt.step();losses.append(total)
    return losses

def seed_run_id(s):return STUDY_ID+'_'+s.lower()

def checkpoint_path(out,s,arm,step):return out/s/'checkpoints'/arm/f'step_{step:04d}'

def save_ready(out,s,arm,step,m,opt,losses,pre,env):
    dest=checkpoint_path(out,s,arm,step)
    require(not dest.exists(),'NO_READY_OVERWRITE')
    dest.mkdir(parents=True,exist_ok=False)
    ck={'schema':'ttm.semantic4x3.checkpoint.v1','study_id':STUDY_ID,'run_id':seed_run_id(s),
        'seed':s,'arm':arm,'step':step,'source_sha256':pre['runner_sha256'],
        'schedule_sha256':pre['schedules_sha256'][s],
        'null_sha256':pre['generated_by_seed'][s]['null_sha256'],
        'env':env,'model':m.state_dict(),'optimizer':opt.state_dict(),'train_losses':losses,
        'sampler_cursor':step,'cpu_rng':torch.get_rng_state(),'cuda_rng':torch.cuda.get_rng_state_all()}
    cp=dest/'checkpoint.pt'
    with cp.open('xb') as f:torch.save(ck,f);f.flush();os.fsync(f.fileno())
    h=sha_file(cp)
    newjson(dest/'READY.json',{'schema':'ttm.semantic4x3.ready.v1','study_id':STUDY_ID,
      'run_id':seed_run_id(s),'seed':s,'arm':arm,'step':step,
      'source_sha256':pre['runner_sha256'],'schedule_sha256':pre['schedules_sha256'][s],
      'checkpoint_sha256':h,'checkpoint_bytes':cp.stat().st_size,
      'env':env})
    return h

def resume_state(out,s,arm,m,opt,pre,env):
    base=out/s/'checkpoints'/arm
    base.mkdir(parents=True,exist_ok=True)
    completed=[i for i in range(EVERY,STEPS+1,EVERY) if checkpoint_path(out,s,arm,i).joinpath('READY.json').exists()]
    last=max(completed) if completed else 0
    require(completed==list(range(EVERY,last+1,EVERY)),'NONCONTIGUOUS_READY_'+s+'_'+arm)
    for end in range(EVERY,STEPS+1,EVERY):
        mark=base/f'CHUNK_{end:04d}_START.json';done=base/f'CHUNK_{end:04d}_DONE.json'
        if mark.exists():require(done.exists() and checkpoint_path(out,s,arm,end).joinpath('READY.json').exists(),'UNFINISHED_CHUNK_NO_REPLAY_'+s+'_'+arm+str(end))
        if done.exists():require(mark.exists(),'CHUNK_ORPHAN_DONE_'+s+'_'+arm+str(end))
    if last==0:
        require(not (base/'ARM_START.json').exists(),'ARM_STARTED_NO_READY_'+s+'_'+arm)
        newjson(base/'ARM_START.json',{'study_id':STUDY_ID,'seed':s,'arm':arm,'run_id':seed_run_id(s)})
        return 0,[]
    require((base/'ARM_START.json').exists(),'ARM_START_MISSING_'+s+'_'+arm)
    p=checkpoint_path(out,s,arm,last)
    metadata=jsonread(p/'READY.json');cp=p/'checkpoint.pt'
    require(metadata['step']==last and metadata['seed']==s and metadata['arm']==arm and metadata['run_id']==seed_run_id(s)
       and metadata['env']==env and metadata['source_sha256']==pre['runner_sha256'] and metadata['schedule_sha256']==pre['schedules_sha256'][s]
       and sha_file(cp)==metadata['checkpoint_sha256'],'RESTORE_SHA_META_'+s+'_'+arm)
    data=torch.load(cp,map_location='cpu',weights_only=True)
    require(data['step']==last and data['sampler_cursor']==last and len(data['train_losses'])==last and data['null_sha256']==pre['generated_by_seed'][s]['null_sha256'],'RESTORE_CONTENT_'+s+'_'+arm)
    m.load_state_dict(data['model'],strict=True);opt.load_state_dict(data['optimizer'])
    torch.set_rng_state(data['cpu_rng']);torch.cuda.set_rng_state_all(data['cuda_rng'])
    return last,list(data['train_losses'])

@torch.inference_mode()
def story_score(m,h768):
    m.eval()
    sums=np.zeros(768,dtype=np.float64)
    for k in range(0,1000,MICRO):
        end=min(k+MICRO,1000)
        x=torch.from_numpy(h768['x'][k:end].copy()).to('cuda:0',dtype=torch.long)
        y=torch.from_numpy(h768['y'][k:end].copy()).to('cuda:0',dtype=torch.long)
        logits,_=m(x)
        require(torch.isfinite(logits).all().item(),'SCORER_NONFINITE_LOGITS')
        ll=F.cross_entropy(logits.float().reshape(-1,2048),y.reshape(-1),ignore_index=-100,reduction='none')
        np.add.at(sums,h768['story_index'][k:end],ll.reshape(end-k,256).sum(dim=1).double().cpu().numpy())
    return sums

def compute_science(losses,counts,seed=BOOT_SEED,draws=BOOT_DRAWS):
    require(counts.ndim==1 and counts.shape==(768,) and counts.sum()==186655,'SCIENCE_COUNT_SHAPE')
    require(set(losses)==set(SEEDS),'SCIENCE_SEEDS')
    for s in SEEDS:require(set(losses[s])==set(ARMS) and all(np.asarray(losses[s][a]).shape==(768,) for a in ARMS),'SCIENCE_ARMS_'+s)
    nll={s:{a:float(np.asarray(losses[s][a]).sum()/counts.sum()) for a in ARMS} for s in SEEDS}
    contrasts={}
    for s in SEEDS:
        a=losses[s]
        pre=np.asarray(a['PT-PERM'])-np.asarray(a['PT-REAL'])
        nul=np.asarray(a['NULL-PERM'])-np.asarray(a['NULL-REAL'])
        contrasts[s]={'tau_residual':float((pre-nul).sum()/counts.sum()),
                      'gamma_real':float((np.asarray(a['NULL-REAL'])-np.asarray(a['PT-REAL'])).sum()/counts.sum()),
                      'delta_PRE':float(pre.sum()/counts.sum()),'delta_NULL':float(nul.sum()/counts.sum())}
    rng=np.random.default_rng(seed)
    idx=rng.integers(0,768,size=(draws,768))
    den=counts[idx].sum(axis=1)
    bs={}
    for name in ('tau_residual','gamma_real'):
        total=np.zeros(768,dtype=np.float64)
        for s in SEEDS:
            z=losses[s]
            cur=(np.asarray(z['PT-PERM'])-np.asarray(z['PT-REAL'])
                 -np.asarray(z['NULL-PERM'])+np.asarray(z['NULL-REAL']) if name=='tau_residual'
                 else np.asarray(z['NULL-REAL'])-np.asarray(z['PT-REAL']))
            total+=cur
        total/=3
        v=total[idx].sum(axis=1)/den
        bs[name]={'mean_delta_nll':float(total.sum()/counts.sum()),
                  'ci95_percentile':[float(x) for x in np.quantile(v,[.025,.975])],
                  'seed_all_positive':all(contrasts[s][name]>0 for s in SEEDS)}
    verdict=('PASS_SCOPED_DONOR_RESIDUAL_STRUCTURE' if all(
        bs[k]['seed_all_positive'] and bs[k]['ci95_percentile'][0]>0
        for k in ('tau_residual','gamma_real')) else 'DONOR_RESIDUAL_SIGNAL_NOT_ESTABLISHED_SCOPED_FAIL')
    return nll,contrasts,bs,verdict

def post_train(out,pre,ctx):
    (sw,p02,old,ckpt,donor,src,valid,P,E0,data,counts,schedules,rows,hdir)=ctx
    for s in SEEDS:
        for arm in ARMS:
            dest=checkpoint_path(out,s,arm,STEPS)
            require((dest/'READY.json').is_file() and (dest/'checkpoint.pt').is_file(),'ALL_12_FINAL_READY_REQUIRED_'+s+'_'+arm)
    require(not (out/'SCORING_START.json').exists() and not (out/'RESULT.json').exists(),'SCORING_ALREADY_CONSUMED')
    # No H768 labels were parsed and no model.forward occurred before all final READY.
    newjson(out/'SCORING_START.json',{'schema':'ttm.semantic4x3.scoring_start.v1','study_id':STUDY_ID,'runner_sha256':pre['runner_sha256']})
    h=load_h768_for_score(hdir,counts)
    losses={}
    for s in SEEDS:
        losses[s]={}
        for arm in ARMS:
            cpdir=checkpoint_path(out,s,arm,STEPS)
            r=jsonread(cpdir/'READY.json')
            require(r['run_id']==seed_run_id(s) and r['arm']==arm and r['step']==STEPS and r['source_sha256']==pre['runner_sha256'] and r['schedule_sha256']==pre['schedules_sha256'][s] and sha_file(cpdir/'checkpoint.pt')==r['checkpoint_sha256'],'SCORER_CHECKPOINT_SHA_'+s+'_'+arm)
            m=make_model(arm,SEEDS[s]['model'],sw,p02,ckpt,donor,rows[s][arm],valid,P,E0)
            state=torch.load(cpdir/'checkpoint.pt',map_location='cpu',weights_only=True)
            require(state['run_id']==seed_run_id(s) and state['null_sha256']==pre['generated_by_seed'][s]['null_sha256'],'SCORER_META_'+s+'_'+arm)
            m.load_state_dict(state['model'],strict=True)
            m=m.to('cuda:0',dtype=torch.float32)
            losses[s][arm]=story_score(m,h)
            del m,state;torch.cuda.empty_cache()
    per={'schema':'ttm.semantic4x3.per_story.private.v1','study_id':STUDY_ID,'h768_membership_sha256':H768_PINS['H768_MEMBERSHIP_PRIVATE.json'],
         'target_counts':counts.tolist(),'loss_sum_by_seed_arm':{s:{a:losses[s][a].tolist() for a in ARMS} for s in SEEDS}}
    per_sha=newjson(out/'PER_STORY_PRIVATE.json',per)
    nll,delta,bs,verdict=compute_science(losses,counts)
    result={'schema':'ttm.semantic4x3.result.public.v1','study_id':STUDY_ID,
       'status':'COMPLETED_PENDING_INDEPENDENT_ADJUDICATION','candidate_verdict':verdict,
       'arms_per_seed':4,'seed_count':3,'steps_per_arm':STEPS,'targets_per_step':TARGETS,
       'h768_stories':768,'h768_windows':1000,'h768_targets':int(counts.sum()),
       'bootstrap_draws':BOOT_DRAWS,'bootstrap_seed':BOOT_SEED,'bootstrap_scope':'CONDITIONAL_ON_3_FIXED_TRAINING_SEEDS',
       'nll_nats_per_target':nll,'contrasts_by_seed':delta,'co_primary':bs,
       'claim_sha256':sha_file(out/'STUDY_CLAIM.json'),
       'private_per_story_sha256':per_sha,'source_runner_sha256':pre['runner_sha256'],
       'h768_membership_sha256':H768_PINS['H768_MEMBERSHIP_PRIVATE.json'],
       'historical_TEST_H320_H512_not_scored':True}
    res_sha=newjson(out/'RESULT.json',result)
    print('SEMANTIC4X3_RESULT_SHA256='+res_sha,flush=True)
    print('SEMANTIC4X3_PENDING_INDEPENDENT_ADJUDICATION='+verdict,flush=True)

def execute(a):
    resume=(a.mode=='resume')
    require(a.owner_science_approved,'OWNER_SCIENCE_APPROVAL_REQUIRED_NO_CLAIM')
    if resume:require(a.manual_resume_adjudicated,'EXPLICIT_MANUAL_RESUME_ADJUDICATION_REQUIRED')
    out,pre,ctx=study_preflight(a,require_absent=not resume,gpu=True)
    env=pre['env']
    if not resume:
        out.mkdir(parents=True,exist_ok=False)
        pre['claimed']=True;pre['owner_science_approved']=True
        claim_sha=newjson(out/'STUDY_CLAIM.json',pre)
        print('SEMANTIC4X3_STUDY_CLAIM_CONSUMED_SHA256='+claim_sha,flush=True)
        for s in SEEDS:
            (out/s).mkdir(parents=True,exist_ok=False)
            newjson(out/s/'CLAIM.json',{'study_id':STUDY_ID,'run_id':seed_run_id(s),'seed':s,'seeds':SEEDS[s],
                'source_sha256':pre['runner_sha256'],'h768_sha256':H768_PINS,'env':env,
                'parent_study_claim_sha256':claim_sha})
            newjson(out/s/'SCHEDULE_PRIVATE.json',{'run_id':seed_run_id(s),'schedule_sha256':pre['schedules_sha256'][s],
                'ordered_packets':ctx[-3][s][0]})
    else:
        claim=jsonread(out/'STUDY_CLAIM.json')
        require(claim.get('claimed') is True,'NO_CONSUMED_CLAIM')
        for key in ('study_id','runner_sha256','null_module_sha256','input_pins','h768_pins','generated_by_seed','schedules_sha256','seeds','env'):
            require(claim[key]==pre[key],'CLAIM_DRIFT_'+key)
        require(not (out/'SCORING_START.json').exists() and not (out/'RESULT.json').exists(),'SCORE_ALREADY_STARTED')
        for s in SEEDS:
            require((out/s/'CLAIM.json').is_file() and (out/s/'SCHEDULE_PRIVATE.json').is_file(),'SEED_CLAIM_MISSING_'+s)
            recorded=jsonread(out/s/'SCHEDULE_PRIVATE.json')
            require(recorded['schedule_sha256']==pre['schedules_sha256'][s] and sha_bytes(canon(recorded['ordered_packets']))==pre['schedules_sha256'][s],'SCHEDULE_DRIFT_'+s)
    (sw,p02,old,ckpt,donor,src,valid,P,E0,data,counts,schedules,rows_by_seed,hdir)=ctx
    for s in SEEDS:
        for arm in ARMS:
            m=make_model(arm,SEEDS[s]['model'],sw,p02,ckpt,donor,rows_by_seed[s][arm],valid,P,E0).to('cuda:0',dtype=torch.float32)
            opt=torch.optim.AdamW([p for p in m.parameters() if p.requires_grad],lr=1e-4,betas=(.9,.95),eps=1e-8,weight_decay=.1)
            start,history=resume_state(out,s,arm,m,opt,pre,env)
            for end in range(start+EVERY,STEPS+1,EVERY):
                base=out/s/'checkpoints'/arm
                newjson(base/f'CHUNK_{end:04d}_START.json',{'run_id':seed_run_id(s),'arm':arm,'start':end-EVERY,'end':end})
                history.extend(train_chunk(m,opt,schedules[s][0],data,end-EVERY,end))
                require(len(history)==end,'STEP_HISTORY_LENGTH')
                digest=save_ready(out,s,arm,end,m,opt,history,pre,env)
                newjson(base/f'CHUNK_{end:04d}_DONE.json',{'run_id':seed_run_id(s),'arm':arm,'step':end,'checkpoint_sha256':digest})
                print(f'SEMANTIC4X3_READY seed={s} arm={arm} step={end} sha256={digest}',flush=True)
            del m,opt;torch.cuda.empty_cache()
    post_train(out,pre,ctx)

def fixture():
    # Truly synthetic CPU: no private data, no GPU, and no science claims.
    import tempfile
    counts=np.ones(768,dtype=np.int64)*243
    counts[:31]+=1
    require(int(counts.sum())==186655,'FIXTURE_COUNT')
    packets,tag=schedule(np.array([256,100,128,16],dtype=np.int64),2026111113,steps=3,targets=1024)
    require(len(packets)==3 and all(sum(l)==1024 for _,l in packets),'FIXTURE_SCHEDULE')
    toy={}
    for s in SEEDS:
        arr=(np.linspace(.5,.6,768)+((int(s[-1])-1)*.0001))*counts
        toy[s]={'PT-REAL':arr,'PT-PERM':arr+.1*counts,'NULL-REAL':arr+.05*counts,'NULL-PERM':arr+.07*counts}
    n,contrasts,bs,verdict=compute_science(toy,counts,seed=BOOT_SEED,draws=2000)
    require(verdict=='PASS_SCOPED_DONOR_RESIDUAL_STRUCTURE' and bs['tau_residual']['mean_delta_nll']>.02 and bs['gamma_real']['mean_delta_nll']>.04,'FIXTURE_PASS_GATES')
    toy['S2']['NULL-REAL']=np.asarray(toy['S2']['PT-REAL'])-.01*counts
    _,_,_,verdict2=compute_science(toy,counts,seed=BOOT_SEED,draws=2000)
    require(verdict2=='DONOR_RESIDUAL_SIGNAL_NOT_ESTABLISHED_SCOPED_FAIL','FIXTURE_FAIL_GATE')
    with tempfile.TemporaryDirectory() as tmp:
        p=Path(tmp)/'CLAIM.json';require(not p.exists(),'FIXTURE_CLAIM')
        newjson(p,{'x':1})
        try:newjson(p,{'x':2})
        except FileExistsError:pass
        else:raise RuntimeError('FIXTURE_OVERWRITE_NOT_REJECTED')
    print(json.dumps({'schema':'ttm.semantic4x3.synthetic.fixture.v1','status':'PASS_8_CHECKS','science_training':False,'gpu_used':False,'h768_scored':False,'claim_created':False,'schedule_fixture_sha256':tag},sort_keys=True))

def cpu_source_qa(a):
    _,pre,_=study_preflight(a,require_absent=False,gpu=False)
    print(json.dumps({'status':'PASS_REAL_SOURCE_CPU_NO_SCIENCE','schema':'ttm.semantic4x3.cpu_source_qa.v1',
      'seed_count':3,'null_geometry_by_seed':{s:pre['generated_by_seed'][s]['geometry'] for s in SEEDS},
      'h768_stories':768,'h768_targets':186655,'source_parity':pre['cpu_original_C2048_source_parity'],
      'training_executed':False,'gpu_used':False,'claim_created':False},sort_keys=True))

def main():
    p=argparse.ArgumentParser()
    p.add_argument('--mode',required=True,choices=['fixture','cpu-source-qa','preflight','execute','resume'])
    p.add_argument('--input',default='');p.add_argument('--h768',default='');p.add_argument('--code-dir',default='')
    p.add_argument('--drive-output',default='');p.add_argument('--owner-verified-free-gib',type=float,default=0)
    p.add_argument('--free-colab-confirmed',action='store_true')
    p.add_argument('--owner-science-approved',action='store_true')
    p.add_argument('--manual-resume-adjudicated',action='store_true')
    a=p.parse_args()
    if a.mode=='fixture':fixture();return
    if a.mode=='cpu-source-qa':cpu_source_qa(a);return
    if a.mode=='preflight':
        _,pre,_=study_preflight(a,require_absent=True,gpu=True)
        print(json.dumps({k:pre[k] for k in ('schema','study_id','h768_stories','h768_targets','env','schedules_sha256','synthetic_gpu_peak_bytes','cpu_original_C2048_source_parity')},sort_keys=True))
        print('TTM_SEMANTIC4X3_PRECLAIM=PASS_NO_SCIENCE_CONSUMED');return
    execute(a)

if __name__=='__main__':main()
