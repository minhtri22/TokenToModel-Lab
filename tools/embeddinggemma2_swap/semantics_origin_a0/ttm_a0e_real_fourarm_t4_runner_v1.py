#!/usr/bin/env python3
"""A0E executable 4x3 TTM-Small trainer: source-bound, one-shot, resumable.
Import/--fixture/--preflight never call model.forward, score VAL, train or touch GPU.
--execute requires exact owner GO receipt and a full passed integrated preexec dossier.
Never opens lexical gold, legacy TEST/H768/OOD256. All checkpoints/output are PRIVATE.
"""
from __future__ import annotations
import argparse,hashlib,importlib.util,json,os,sys
from pathlib import Path
from contextlib import nullcontext

ARMS=("P-A","P-C","N-A","N-C")
SEEDS=(41031,41032,41033)
NSEEDS=(61031,61032,61033)
STEPS=512;TARGET=4096;MICRO=8;SAVE_EVERY=128
INPUT_PINS={
 "checkpoint.pt":"cb985751795c8328ad65acf7ca4c1033ce35182c1bfbdb8c38550de629cb271b",
 "candidate_initialization.pt":"c9fc798d8880c7e76636258052e9885dbb086d7b462a5b6bee5cff8b582973c3",
 "T4_PRIVATE_TRAIN_VAL_WINDOWS.npz":"184f68b4c0c800ef3e98362c2e20e1cd35baa269e926489a475664526ecd9913",
 "p02_exact.py":"e0fcac285918b66b13c8f694e6d625a0691c9b59221b43043e63f46b25ddcc07",
 "ttm_embeddinggemma2_swap.py":"d11da61e9d7bb040f3263e680f026817a513553c186ab243e184ffaf6e68cd39",
}
PREREG_BLOB="d6e5d82709b2bc31458f73e7720cdae1e5f5e54e"
def need(ok,why):
    if not bool(ok):raise RuntimeError("A0E_RUN_HOLD_"+why)
def sha(path):
    h=hashlib.sha256()
    with Path(path).open('rb') as f:
        for b in iter(lambda:f.read(1048576),b''):h.update(b)
    return h.hexdigest()
def canonical(x):
    return json.dumps(x,sort_keys=True,ensure_ascii=False,separators=(',',':'),allow_nan=False).encode('utf-8')
def pinned_json(path):
    return json.loads(Path(path).read_text('utf8'))
def newjson(path,data):
    path=Path(path)
    path.parent.mkdir(parents=True,exist_ok=True)
    with path.open('x',encoding='utf8',newline='\n') as f:
        json.dump(data,f,sort_keys=True,indent=2,allow_nan=False);f.write('\n');f.flush();os.fsync(f.fileno())
    return sha(path)
def private_source(root):
    root=Path(root).resolve(strict=True)
    need(root.is_dir(),"PRIVATE_SOURCE_ROOT")
    for name,exp in INPUT_PINS.items():
        path=(root/'src'/name) if name.endswith('.py') else root/name
        need(path.is_file() and sha(path)==exp,"SOURCE_SHA_"+name)
    return root
def read_npz_source(path,receipt):
    import numpy as np
    path=Path(path).resolve(strict=True)
    need(sha(path)==receipt.get("normalized_private_npz_sha256"),"NORMALIZED_SHA")
    need(receipt.get('schema')=='ttm.gemma2.a0e.scaled_private_tensor_readback.v1'
         and receipt.get('status')=='PASS_REAL_TENSOR_TRANSFORM_SCOPED_HOLD_CROSS_ORIGIN_SHAPE'
         and receipt.get('gold_read') is False,"SCALAR_RECEIPT")
    with np.load(path,allow_pickle=False) as z:
        expected={f'{arm}-{n}' for n in NSEEDS for arm in ARMS}|{'valid','projector'}
        need(set(z.files)==expected,"NORMALIZED_KEYS")
        valid=z['valid'].astype(bool);proj=z['projector'].astype(np.float32)
        need(valid.shape==(2048,) and int(valid.sum())==1917 and proj.shape==(256,512),"NORMALIZED_GEOMETRY")
        rows={}
        for n in NSEEDS:
            r=next(x for x in receipt['seeds'] if x['seed']==n)
            for arm in ARMS:
                key=f'{arm}-{n}';v=z[key].astype(np.float32)
                need(v.shape==(2048,512) and np.isfinite(v).all(),"NORMALIZED_TENSOR_SHAPE_"+key)
                digest=hashlib.sha256(np.ascontiguousarray(v,dtype='<f4').tobytes()).hexdigest()
                need(digest==r['new_f32le_SHA'][key],"NORMALIZED_TENSOR_HASH_"+key)
                rows[key]=v
    return rows,valid,proj
def train_data(root):
    import numpy as np
    with np.load(root/'T4_PRIVATE_TRAIN_VAL_WINDOWS.npz',allow_pickle=False) as z:
        # deliberately NEVER access legacy VAL arrays
        x=z['train_x'].astype(np.int64);y=z['train_y'].astype(np.int64)
        count=z['train_count'].astype(np.int64)
        need(x.shape==(2691,256) and y.shape==x.shape and count.shape==(2691,),"TRAIN_SHAPE")
        mask=np.arange(256)[None,:]<count[:,None]
        need((count>0).all() and (count<=256).all() and count.sum()==498287,"TRAIN_COUNTS")
        need((x>=0).all() and (x<2048).all() and (y[~mask]==-100).all()
             and (y[mask]>=0).all() and (y[mask]<2048).all(),"TRAIN_MASK")
    return {'x':x,'y':y,'count':count}
def fresh_val_sources(npz,manifest):
    import numpy as np
    meta=pinned_json(manifest)
    need(meta.get('schema')=='ttm.gemma2.a0e.fresh_val_roster.v1'
         and meta.get('status')=='PASS_NEW_FRESH_VAL_ROSTER'
         and meta.get('original_prereg_blob')==PREREG_BLOB
         and meta.get('raw_rights_neardup_pass') is True,"FRESH_VAL_PROVENANCE")
    need(sha(npz)==meta['windows_npz_sha256'],"FRESH_VAL_SHA")
    need(sha(npz)!=INPUT_PINS['T4_PRIVATE_TRAIN_VAL_WINDOWS.npz'],"LEGACY_VAL_REUSE")
    # Called only after all 12 last checkpoints exist and are SHA verified.
    with np.load(npz,allow_pickle=False) as z:
        need(set(z.files)=={'x','y','count','story_index'},"VAL_KEYS")
        x=z['x'].astype(np.int64);y=z['y'].astype(np.int64)
        c=z['count'].astype(np.int64);ids=z['story_index'].astype(np.int64)
        need(x.ndim==2 and x.shape[1]==256 and y.shape==x.shape
             and c.shape==(len(x),) and ids.shape==(len(x),),"VAL_SHAPE")
        mask=np.arange(256)[None,:]<c[:,None]
        need((c>0).all() and (c<=256).all() and (x>=0).all() and (x<2048).all()
             and (y[~mask]==-100).all() and (y[mask]>=0).all() and (y[mask]<2048).all(),"VAL_MASK")
        need(len(set(ids.tolist()))==meta['document_count'],"VAL_DOCS")
        need(int(c.sum())==meta['target_tokens'],"VAL_TARGETS")
    return x,y,c,ids
def schedule(count,seed):
    import numpy as np
    rng=np.random.default_rng(seed)
    packets=[]
    for _ in range(STEPS):
        remain=TARGET;ids=[];limits=[]
        while remain:
            k=int(rng.integers(0,len(count)))
            n=min(int(count[k]),remain)
            need(n>0,"SCHEDULE_ZERO")
            ids.append(k);limits.append(n);remain-=n
        packets.append((ids,limits))
    return packets,hashlib.sha256(canonical(packets)).hexdigest()
def study_fixture():
    expected=[f'seed{s}__{arm}.json' for s in SEEDS for arm in ARMS]
    need(len(expected)==12 and len(set(expected))==12,"FIXTURE_ARMS")
    need(len(ARMS)*len(SEEDS)*STEPS*TARGET==25165824,"FIXTURE_BUDGET")
    need(len(INPUT_PINS)==5,"FIXTURE_SOURCE")
    print(json.dumps({"status":"PASS_A0E_TRAINER_STATIC_4X3_AND_25165824",
        "source_pins":len(INPUT_PINS),"gold_read":False,"model_forward":False,"GPU":False},sort_keys=True))
def import_module(name,path):
    spec=importlib.util.spec_from_file_location(name,str(path))
    need(spec and spec.loader,"IMPORT_SPEC")
    mod=importlib.util.module_from_spec(spec)
    sys.modules[name]=mod;spec.loader.exec_module(mod)
    return mod
def build_model(root,train_seed,rows,valid,proj):
    import torch
    sw=import_module('ttm_a0e_sw',root/'src'/'ttm_embeddinggemma2_swap.py')
    p02=sw.load_p02(root/'src'/'p02_exact.py')
    torch.manual_seed(train_seed)
    checkpoint=torch.load(root/'checkpoint.pt',map_location='cpu',weights_only=True)
    need(checkpoint.get('step')==1024 and checkpoint.get('train_pack_sha256')==INPUT_PINS['T4_PRIVATE_TRAIN_VAL_WINDOWS.npz'],"BASE_CKPT")
    base=p02.GPT(sw.p02_config(p02)).float()
    base.load_state_dict(checkpoint['model'],strict=True)
    model=sw.control_untied(base)
    donor=torch.load(root/'candidate_initialization.pt',map_location='cpu',weights_only=True)
    original=base.tok.weight.detach().float().clone()
    need(torch.equal(donor['model_state_dict']['tok.valid'].bool(),torch.from_numpy(valid)),"VALID_CANDIDATE")
    need(torch.equal(donor['model_state_dict']['tok.proj.weight'].float(),torch.from_numpy(proj)),"P0_CANDIDATE")
    model.tok=sw.MappedGemmaInput(torch.from_numpy(rows.copy()),
       torch.from_numpy(valid.copy()),original,torch.from_numpy(proj.copy()))
    for name,param in model.named_parameters():param.requires_grad_(name!='tok.source.weight')
    require_trainable=sum(p.numel() for p in model.parameters() if p.requires_grad)
    need(require_trainable==3880448,"TRAINABLE_PARAMS")
    return model
def restore_or_new(model,settings,root,seed,arm,expected_schedule_sha):
    import torch
    optimizer=torch.optim.AdamW((p for p in model.parameters() if p.requires_grad),
       lr=settings['lr'],betas=tuple(settings['betas']),weight_decay=settings['weight_decay'])
    folder=root/f'seed{seed}'/arm
    checkpoints=sorted(folder.glob('step_*.pt')) if folder.exists() else []
    if not checkpoints:return optimizer,0,[]
    last=checkpoints[-1];step=int(last.stem.split('_')[1])
    need(step in (128,256,384,512),"RESUME_STEP")
    marker=last.with_suffix('.ready.json')
    need(marker.is_file() and pinned_json(marker)['sha256']==sha(last),"RESUME_SHA")
    need(pinned_json(marker).get('schedule_sha256')==expected_schedule_sha,"RESUME_SCHEDULE_MARKER")
    state=torch.load(last,weights_only=True,map_location='cpu')
    need(state['seed']==seed and state['arm']==arm and state['step']==step
         and state['schedule_sha256']==expected_schedule_sha
         and state['schema']=='ttm.gemma2.a0e.checkpoint.v1',"RESUME_BIND")
    model.load_state_dict(state['model'],strict=True)
    optimizer.load_state_dict(state['optimizer'])
    need(len(state['losses'])==step,"RESUME_LENGTH")
    return optimizer,step,state['losses']
def save_state(model,opt,seed,arm,step,losses,folder,schedule_sha):
    import torch
    path=folder/f'step_{step:04d}.pt'
    need(not path.exists() and not path.with_suffix('.ready.json').exists(),"NO_OVERWRITE_CHECKPOINT")
    folder.mkdir(parents=True,exist_ok=True)
    state={'schema':'ttm.gemma2.a0e.checkpoint.v1','seed':seed,'arm':arm,'step':step,
      'schedule_sha256':schedule_sha,'losses':losses,
      'model':{k:v.detach().cpu() for k,v in model.state_dict().items()},
      'optimizer':opt.state_dict()}
    # No external writes: caller chooses private persistent output root.
    with path.open('xb') as f:
        torch.save(state,f);f.flush();os.fsync(f.fileno())
    newjson(path.with_suffix('.ready.json'),{'schema':'ttm.gemma2.a0e.ready.v1',
       'seed':seed,'arm':arm,'step':step,'schedule_sha256':schedule_sha,
       'sha256':sha(path)})
def train_arm(model,optimizer,seed,arm,packets,data,start,losses,out):
    import torch
    from torch.nn import functional as F
    model=model.to('cuda:0',dtype=torch.float32).train()
    # torch.load CPU optimizer state must be moved to the active parameter device on resume.
    for state in optimizer.state.values():
        for k,v in tuple(state.items()):
            if torch.is_tensor(v):state[k]=v.to('cuda:0')
    for step in range(start,STEPS):
        ids,limits=packets[step]
        need(sum(limits)==TARGET,"BUDGET_STEP")
        optimizer.zero_grad(set_to_none=True);loss_total=0.
        for i in range(0,len(ids),MICRO):
            ix=ids[i:i+MICRO];lim=limits[i:i+MICRO]
            x=torch.from_numpy(data['x'][ix].copy()).to('cuda:0')
            y=data['y'][ix].copy()
            for j,n in enumerate(lim):y[j,n:]=-100
            need(int((y!=-100).sum())==sum(lim),"MICRO_TARGETS")
            y=torch.from_numpy(y).to('cuda:0')
            logits,_=model(x)
            loss=F.cross_entropy(logits.float().reshape(-1,2048),y.reshape(-1),
                                 ignore_index=-100,reduction='sum')/TARGET
            need(bool(torch.isfinite(loss)),"TRAIN_LOSS")
            loss.backward()
            loss_total+=float(loss.detach())
        params=[p for p in model.parameters() if p.requires_grad]
        need(all(p.grad is not None and torch.isfinite(p.grad).all().item() for p in params),"GRAD")
        torch.nn.utils.clip_grad_norm_(params,1.)
        optimizer.step();losses.append(loss_total)
        if (step+1)%SAVE_EVERY==0:
            save_state(model,opt=optimizer,seed=seed,arm=arm,step=step+1,
                       losses=losses,folder=out/f'seed{seed}'/arm,
                       schedule_sha=hashlib.sha256(canonical(packets)).hexdigest())
    return model.to('cpu')
def evaluate_after_all(out,models,root,rows,valid,proj,settings,holdout):
    import numpy as np
    import torch
    from torch.nn import functional as F
    x,y,c,story=fresh_val_sources(*holdout)
    names=[f'seed{s}__{arm}.json' for s in SEEDS for arm in ARMS]
    need(all((out/f'seed{s}'/arm/'step_0512.pt').exists() for s in SEEDS for arm in ARMS),"ALL_FINAL_BEFORE_VAL")
    target=out/'outcomes'
    target.mkdir(exist_ok=True)
    need(not any((target/name).exists() for name in names),"NO_OVERWRITE_OUTCOME")
    for seed in SEEDS:
        init_seed=NSEEDS[SEEDS.index(seed)]
        for arm in ARMS:
            model=build_model(root,seed,rows[f'{arm}-{init_seed}'],valid,proj)
            checkpoint=torch.load(out/f'seed{seed}'/arm/'step_0512.pt',map_location='cpu',weights_only=True)
            model.load_state_dict(checkpoint['model'],strict=True)
            model=model.to('cuda:0').eval()
            sums={};counts={}
            with torch.inference_mode():
                for i in range(len(x)):
                    X=torch.from_numpy(x[i:i+1].copy()).to('cuda:0')
                    Y=torch.from_numpy(y[i:i+1].copy()).to('cuda:0')
                    logits,_=model(X)
                    token_loss=F.cross_entropy(logits.float().reshape(-1,2048),
                        Y.reshape(-1),ignore_index=-100,reduction='none').reshape(1,-1)
                    v=float(token_loss.sum().item())
                    d=str(int(story[i]))
                    sums[d]=sums.get(d,0.)+v
                    counts[d]=counts.get(d,0)+int(c[i])
            del model
            outcome={'schema':'ttm.gemma2.a0e.seed_arm_document_nll.v1',
                'seed':seed,'arm':arm,'checkpoint_sha256':sha(out/f'seed{seed}'/arm/'step_0512.pt'),
                'fresh_val_sha256':sha(holdout[0]),'document_sums':sums,'document_targets':counts,
                'total_targets':int(sum(counts.values())),
                'gold_read':False,'lexical_labels_read':False}
            newjson(target/f'seed{seed}__{arm}.json',outcome)
def preflight(a):
    import numpy as np
    root=private_source(a.input_root)
    receipt=pinned_json(a.scalar_receipt)
    rows,valid,proj=read_npz_source(a.scaled_npz,receipt)
    data=train_data(root)
    cfg=pinned_json(a.optimizer_config)
    need(cfg.get('schema')=='ttm.gemma2.a0e.frozen_optimizer.v1'
         and cfg.get('original_prereg_blob')==PREREG_BLOB,"OPTIMIZER_PIN")
    need(isinstance(cfg.get('lr'),(int,float)) and 0<cfg['lr']<.01
         and cfg.get('betas')==[.9,.999] and 0<=cfg.get('weight_decay',-1)<1,"OPTIMIZER_PARAMS")
    schedules={s:schedule(data['count'],s) for s in SEEDS}
    need(cfg.get('schedule_sha256_by_seed')=={str(s):schedules[s][1] for s in SEEDS},
         "SCHEDULE_NOT_PRE_FROZEN")
    need(cfg.get('source_checkpoint_sha256')==INPUT_PINS['checkpoint.pt']
         and cfg.get('private_train_pack_sha256')==INPUT_PINS['T4_PRIVATE_TRAIN_VAL_WINDOWS.npz'],
         "OPTIMIZER_SOURCE_NOT_PINNED")
    manifest_sha=sha(a.preexec_manifest)
    return root,rows,valid,proj,data,cfg,schedules,manifest_sha
def execute(a,ctx):
    import torch
    root,rows,valid,proj,data,cfg,schedules,manifest_sha=ctx
    # Recompute parsed, semantic per-artifact acceptance; owner "GO" cannot bypass v3.
    gate_module=import_module('ttm_a0e_content_guard_v3',
       Path(__file__).with_name('ttm_a0e_content_verified_preexec_guard_v3.py'))
    audited=gate_module.audit(pinned_json(a.preexec_manifest),a.evidence_root)
    need(audited['status']=='GO_CANDIDATE_OWNER_T4_APPROVAL_STILL_REQUIRED'
         and len(audited['missing'])==0,"INDEPENDENT_CONTENT_GATES_NOT_ALL_PASS")
    gate=pinned_json(a.authorization)
    need(gate.get('schema')=='ttm.gemma2.a0e.owner_t4_release.v1'
         and gate.get('status')=='GO_FOR_A0E_T4'
         and gate.get('owner_approved') is True
         and gate.get('preexec_manifest_sha256')==manifest_sha
         and gate.get('runner_sha256')==sha(__file__), "OWNER_RELEASE_NOT_VALID")
    need(a.owner_approve and os.environ.get('TTM_A0E_T4_GO')=='YES','OWNER_EXECUTION_MARKER')
    need(torch.cuda.is_available() and 'T4' in torch.cuda.get_device_name(0),"NOT_T4")
    out=Path(a.output).resolve()
    need(out.exists() and out.is_dir() and a.output_sha_manifest,"OUTPUT_ROOT_EXISTENCE")
    claim=out/'A0E_CLAIM.json'
    expected={'schema':'ttm.gemma2.a0e.claim.v1','prereg_git_blob':PREREG_BLOB,
       'preexec_sha256':manifest_sha,'runner_sha256':sha(__file__),
       'optimizer_sha256':sha(a.optimizer_config),'tensor_npz_sha256':sha(a.scaled_npz),
       'train_pack_sha256':INPUT_PINS['T4_PRIVATE_TRAIN_VAL_WINDOWS.npz'],
       'seeds':list(SEEDS),'arms':list(ARMS),'steps':STEPS,'tokens_per_step':TARGET}
    if claim.exists():need(pinned_json(claim)==expected,"RESUME_CLAIM_CHANGED")
    else:newjson(claim,expected)
    for seed in SEEDS:
        packets,_=schedules[seed];nseed=NSEEDS[SEEDS.index(seed)]
        for arm in ARMS:
            model=build_model(root,seed,rows[f'{arm}-{nseed}'],valid,proj)
            optimizer,start,losses=restore_or_new(model,cfg,out,seed,arm,schedules[seed][1])
            if start<STEPS:
                train_arm(model,optimizer,seed,arm,packets,data,start,losses,out)
            del model,optimizer
            torch.cuda.empty_cache()
    evaluate_after_all(out,None,root,rows,valid,proj,cfg,(a.fresh_val,a.fresh_val_manifest))
def main():
    p=argparse.ArgumentParser()
    g=p.add_mutually_exclusive_group(required=True)
    g.add_argument('--fixture',action='store_true')
    g.add_argument('--preflight',action='store_true')
    g.add_argument('--execute',action='store_true')
    for n in ('input-root','scaled-npz','scalar-receipt','preexec-manifest','optimizer-config',
              'authorization','output','output-sha-manifest','fresh-val','fresh-val-manifest',
              'evidence-root'):
        p.add_argument('--'+n)
    p.add_argument('--owner-approve',action='store_true')
    a=p.parse_args()
    try:
        if a.fixture:study_fixture();return
        need(all((a.input_root,a.scaled_npz,a.scalar_receipt,a.preexec_manifest,a.optimizer_config)),"ARGS")
        ctx=preflight(a)
        if a.preflight:
            print(json.dumps({"status":"SOURCE_PREFLIGHT_PASS_SCOPED_NOT_GPU_ADMITTED",
                              "training":False,"gold_read":False,"GPU":False}))
        else:
            need(all((a.authorization,a.output,a.output_sha_manifest,a.fresh_val,
                       a.fresh_val_manifest,a.evidence_root)),"EXEC_ARGS")
            execute(a,ctx)
    except Exception as e:
        print(json.dumps({"status":"NO_GO_HOLD","error":str(e),"T4_authorized":False},sort_keys=True))
        raise SystemExit(2)
if __name__=="__main__":main()
