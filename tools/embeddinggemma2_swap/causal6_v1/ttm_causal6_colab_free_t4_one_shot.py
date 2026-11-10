#!/usr/bin/env python3
"""TTM Gemma2 causal six arms, one-shot, exact checkpoint journal and sealed H512.
Free T4 ONLY. This source does NOT execute on import. `fixture` is synthetic CPU.
All scientific score files are private. Never touch historical 64 TEST or 320 holdout.
"""
from __future__ import annotations
import argparse, copy, hashlib, importlib.util, json, os, shutil, sys, time
from pathlib import Path
from collections import Counter
import numpy as np
import torch
from torch import nn
from torch.nn import functional as F

RUN_ID='ttm_small4m_gemma2_causal6_2048x4096_free_t4_20261109_v1'
STEPS=2048; TARGETS=4096; MICRO=8; CHECKPOINT_EVERY=256
ARMS=('RR-F','RP-F','RR-A','RP-A','OR-F','OP-F')
SEED=2026110912; PERM_SEED=2026110913; SCHEDULE_SEED=2026110914; BOOT_SEED=2026110915
H512_LABEL='ttm_causal6_h512_seal_v1_20261109'; H512_N=512
PINS={
 'checkpoint.pt':'cb985751795c8328ad65acf7ca4c1033ce35182c1bfbdb8c38550de629cb271b',
 'candidate_initialization.pt':'c9fc798d8880c7e76636258052e9885dbb086d7b462a5b6bee5cff8b582973c3',
 'T4_PRIVATE_TRAIN_VAL_WINDOWS.npz':'184f68b4c0c800ef3e98362c2e20e1cd35baa269e926489a475664526ecd9913',
 'T4_PRIVATE_PACK_MANIFEST.json':'ef2e6e67d49b1d5a921b1051df329f15574f1c10cece0ce49468acb53322d650',
 'p02_exact.py':'e0fcac285918b66b13c8f694e6d625a0691c9b59221b43043e63f46b25ddcc07',
 'ttm_embeddinggemma2_swap.py':'d11da61e9d7bb040f3263e680f026817a513553c186ab243e184ffaf6e68cd39',
 'ttm_directswap2048_gpu_once.py':'0994f0cd91cb504f2db8478f55963813a85469807f2921e38c196248f323759e'
}

def require(x,s):
 if not bool(x):raise RuntimeError('HOLD_'+s)

def hash_file(p):
 h=hashlib.sha256()
 with Path(p).open('rb') as fd:
  for chunk in iter(lambda:fd.read(1<<20),b''):h.update(chunk)
 return h.hexdigest()

def hash_bytes(b):return hashlib.sha256(b).hexdigest()

def canon(x):return json.dumps(x,sort_keys=True,separators=(',',':'),ensure_ascii=False,allow_nan=False).encode('utf-8')

def exclusive_json(path,data):
 with Path(path).open('x',encoding='utf8') as fd:
  json.dump(data,fd,ensure_ascii=False,sort_keys=True,indent=2,allow_nan=False)
  fd.write('\n');fd.flush();os.fsync(fd.fileno())

def read_json(p):return json.loads(Path(p).read_text('utf-8'))

def require_source(root):
 root=Path(root).resolve(strict=True)
 assert root.is_dir()
 def p(k):return root/k if k not in ('p02_exact.py','ttm_embeddinggemma2_swap.py','ttm_directswap2048_gpu_once.py') else root/'src'/k
 for k,exp in PINS.items():
  f=p(k);require(f.is_file() and not f.is_symlink() and hash_file(f)==exp,'SOURCE_SHA_'+k)
 return root,p

def load_module(name,path):
 spec=importlib.util.spec_from_file_location(name,str(path))
 require(spec is not None and spec.loader is not None,'DYNAMIC_IMPORT')
 mod=importlib.util.module_from_spec(spec);sys.modules[name]=mod;spec.loader.exec_module(mod)
 return mod

def model_context(root,p):
 sys.path.insert(0,str(root/'src'))
 import ttm_embeddinggemma2_swap as sw
 p02=sw.load_p02(p('p02_exact.py'))
 old=load_module('ttm_c2048_original_exact_ref',p('ttm_directswap2048_gpu_once.py'))
 ckpt=torch.load(p('checkpoint.pt'),map_location='cpu',weights_only=True)
 donor=torch.load(p('candidate_initialization.pt'),map_location='cpu',weights_only=True)
 require(ckpt.get('step')==1024 and ckpt.get('p02_git_blob')=='9762343e06cf800b50574c2871ae1ed58537fb18'
  and ckpt.get('train_pack_sha256')==PINS['T4_PRIVATE_TRAIN_VAL_WINDOWS.npz'],'BASE_CHECKPOINT_META')
 require(donor.get('schema')=='ttm.embeddinggemma2.token_swap.initialization.v1' and
  donor.get('source_checkpoint_sha256')==PINS['checkpoint.pt'] and donor.get('science_executed') is False,'DONOR_META')
 base=p02.GPT(sw.p02_config(p02)).float().eval()
 base.load_state_dict(ckpt['model'],strict=True)
 state=donor['model_state_dict'];src=state['tok.source.weight'].float();valid=state['tok.valid'].bool()
 e0=base.tok.weight.detach().float()
 require(src.shape==(2048,512) and valid.shape==(2048,) and valid.sum().item()==1917
  and not bool(valid[256]),'DONOR_MAPPING')
 require(state['tok.proj.weight'].shape==(256,512) and torch.equal(state['tok.fallback'],e0),'BASE_DONOR_FALLBACK')
 return sw,p02,old,ckpt,donor,src,valid,e0

def shared_init(src,valid,e0,donor):
 preal=donor['model_state_dict']['tok.proj.weight'].detach().float().clone()
 # Detect that original P was fitted by frozen ridge implementation.
 fromsys=src.detach().float()
 x=fromsys[valid].double();y=e0[valid].double()
 # Procrustes initializer, no labels used.
 u,_,vh=torch.linalg.svd(x.T@y,full_matrices=False)
 q=u@vh
 sc=float(((x@q)*y).sum()/((x@q)**2).sum())
 require(np.isfinite(sc) and sc>0 and q.shape==(512,256),'ORTH_SCALE')
 porth=(q*sc).T.float().contiguous()
 return preal,porth,sc

def permutation(src,valid):
 ids=torch.where(valid)[0]
 perm=np.random.default_rng(PERM_SEED).permutation(len(ids))
 out=src.clone();out[ids]=src[ids][torch.from_numpy(perm.copy()).long()]
 return out

def projected_multiset_hash(rows,p,valid):
 x=(rows[valid].double()@p.double().T).float().contiguous().numpy()
 return hash_bytes(b''.join(sorted([hash_bytes(row.tobytes()).encode() for row in x])))

def construct(arm,sw,p02,old,ckpt,donor,src,perm_src,valid,e0,pridge,porth):
 torch.manual_seed(SEED)
 base=p02.GPT(sw.p02_config(p02)).float();base.load_state_dict(ckpt['model'],strict=True)
 m=sw.control_untied(base)
 rows=perm_src if arm in ('RP-F','RP-A','OP-F') else src
 w=porth if arm in ('OR-F','OP-F') else pridge
 m.tok=sw.MappedGemmaInput(rows,valid,e0,w)
 if arm=='RR-F':
  m.load_state_dict(donor['model_state_dict'],strict=True)
 isadapter=arm.endswith('-A')
 for n,p in m.named_parameters():
  p.requires_grad_(n=='tok.proj.weight' if isadapter else n!='tok.source.weight')
 trainables=sum(p.numel() for p in m.parameters() if p.requires_grad)
 require(trainables==256*512 if isadapter else trainables>2000000,'ARM_TRAINABLES_'+arm)
 return m,trainables

def source_parity(sw,p02,old,ckpt,donor,src,perm_src,valid,e0,pridge,porth):
 reference=old.build_model('C',p02,sw,ckpt,donor).float().eval()
 test_model,params=construct('RR-F',sw,p02,old,ckpt,donor,src,perm_src,valid,e0,pridge,porth)
 test_model.eval()
 a=reference.state_dict();b=test_model.state_dict()
 require(a.keys()==b.keys() and all(torch.equal(a[k],b[k]) for k in a),'ORIGINAL_C2048_STATE_PARITY')
 probe=torch.tensor([[1,42,110,500,256,300]],dtype=torch.long)
 with torch.inference_mode():require(torch.equal(reference(probe)[0],test_model(probe)[0]),'ORIGINAL_C2048_LOGIT_PARITY')
 del reference,test_model
 return params

def load_t4(root,p):
 manifest=read_json(p('T4_PRIVATE_PACK_MANIFEST.json'))
 require(manifest.get('schema')=='ttm.t4.private.train_val.windowpack.v1' and manifest.get('contains_test') is False
  and manifest.get('npz_sha256')==PINS['T4_PRIVATE_TRAIN_VAL_WINDOWS.npz'],'PACK_MANIFEST')
 with np.load(p('T4_PRIVATE_TRAIN_VAL_WINDOWS.npz'),allow_pickle=False) as z:
  want={f'{s}_{t}' for s in ('train','val') for t in ('x','y','count','story_index')}
  require(set(z.files)==want,'T4_PACK_KEYS')
  data={k:z[k].astype(np.int64) for k in want}
 for s,w,story,num in [('train',2691,2048,498287),('val',328,256,61122)]:
  x,y,c,si=(data[f'{s}_{t}'] for t in ('x','y','count','story_index'))
  require(x.shape==(w,256) and y.shape==x.shape and c.shape==(w,) and si.shape==(w,),'T4_SHAPE_'+s)
  mask=np.arange(256)[None,:]<c[:,None]
  require((c>0).all() and (c<=256).all() and (x>=0).all() and (x<2048).all()
   and (y[~mask]==-100).all() and (y[mask]>=0).all() and (y[mask]<2048).all()
   and int(c.sum())==num and np.array_equal(np.unique(si),np.arange(story)),'T4_LABELS_'+s)
 return data

def load_h512(folder):
 folder=Path(folder).resolve(strict=True)
 public=read_json(folder/'H512_PUBLIC_SEAL.json')
 require(public.get('status')=='H512_SEALED_NOT_SCORED' and public.get('stories')==512 and
  public.get('near_train_pairs')==0 and public.get('near_val_pairs')==0 and public.get('near_internal_pairs')==0,'H512_PUBLIC_SEAL')
 for f,expected in [('H512_PRIVATE_MEMBERSHIP.json',public['membership_private_sha256']),('H512_PRIVATE_WINDOWS.npz',public['h512_window_pack_sha256'])]:
  require(hash_file(folder/f)==expected,'H512_PRIVATE_SHA_'+f)
 member=read_json(folder/'H512_PRIVATE_MEMBERSHIP.json')
 require(member['schema']=='ttm.causal6.h512.membership.private.v1' and member['selection_count']==512
  and member['source_hashes']['TinyStories-valid.txt']=='94e431816c4cce81ff71e4408ff8d3bda9a42e8d2663986697c3954288cb38b4'
  and member['split_sha256']=='9f2ebaca821bddf0a9d7ae30ccfcef34561b968b21159aa913794298235a2fa9'
  and member['bpe_file_sha256']=='cba18e60cee3d08a353ee6d4a451017289e45af7b4b1179c87171b9b78d7dfdc'
  and member['prior_l0017_sha256']=='bedc3671256a66f605fbeb9f98bbd27149b456019d3d8bc5bbc89ebca6d09b47','H512_MEMBERSHIP_BIND')
 with np.load(folder/'H512_PRIVATE_WINDOWS.npz',allow_pickle=False) as z:
  require(set(z.files)=={'x','y','count','story_index'},'H512_PACK_KEYS')
  d={k:z[k].astype(np.int64) for k in z.files}
 x,y,c,si=(d[k] for k in ('x','y','count','story_index'))
 mask=np.arange(256)[None,:]<c[:,None]
 require(x.ndim==2 and x.shape[1]==256 and y.shape==x.shape and c.shape==(len(x),)
  and si.shape==(len(x),) and np.array_equal(np.unique(si),np.arange(512)), 'H512_SHAPES')
 require((c>0).all() and (c<=256).all() and (x>=0).all() and (x<2048).all()
  and (y[~mask]==-100).all() and (y[mask]>=0).all() and (y[mask]<2048).all()
  and sum(member['story_target_counts'])==int(c.sum())==public['targets']
  and len(x)==public['windows'],'H512_BOUNDARY_MASK')
 counts=np.bincount(si,weights=c,minlength=512).astype(np.int64)
 require(counts.tolist()==member['story_target_counts'],'H512_STORY_COUNTS')
 return d,counts,public

def schedule(c):
 r=np.random.default_rng(SCHEDULE_SEED);packets=[]
 for _ in range(STEPS):
  remaining=TARGETS;idx=[];limits=[]
  while remaining:
   j=int(r.integers(0,len(c)));n=min(int(c[j]),remaining)
   require(n>0,'SAMPLE_ZERO');idx.append(j);limits.append(n);remaining-=n
  packets.append((idx,limits))
 return packets,hash_bytes(canon(packets))

def environment():return {'torch':str(torch.__version__),'numpy':str(np.__version__),'cuda':str(torch.version.cuda),
 'device':torch.cuda.get_device_name(0) if torch.cuda.is_available() else None,'device_count':torch.cuda.device_count()}

def gpu_preflight(free_drive_gib):
 require(os.environ.get('COLAB_RELEASE_TAG') is not None or Path('/content').is_dir(),'NOT_COLAB_RUNTIME')
 require(torch.cuda.is_available() and torch.cuda.device_count()==1,'NO_CUDA_SINGLE_GPU')
 require('T4' in torch.cuda.get_device_name(0),'NOT_TESLA_T4')
 total=torch.cuda.get_device_properties(0).total_memory
 require(total >= 14*1024**3,'T4_TOO_SMALL')
 require(free_drive_gib>=4,'OWNER_DRIVE_STORAGE_ATTEST_MISSING')
 require(os.environ.get('CUBLAS_WORKSPACE_CONFIG')==':4096:8','DETERMINISM_ENV_NOT_SET')
 torch.backends.cuda.matmul.allow_tf32=False
 torch.backends.cudnn.allow_tf32=False
 torch.set_float32_matmul_precision('highest')
 torch.use_deterministic_algorithms(True)
 torch.manual_seed(SEED);torch.cuda.manual_seed_all(SEED)
 return environment()

def gpu_smoke(model,device):
 # SYNTHETIC, never consuming holdout or real TRAIN/VAL.
 model=model.to(device=device,dtype=torch.float32).train()
 x=torch.randint(0,2048,(8,256),device=device,dtype=torch.long)
 y=torch.randint(0,2048,(8,256),device=device,dtype=torch.long)
 model.zero_grad(set_to_none=True)
 l,_=model(x,y)
 require(bool(torch.isfinite(l)),'SMOKE_LOSS_FINITE')
 l.backward()
 require(any(p.grad is not None for p in model.parameters() if p.requires_grad),'SMOKE_GRADIENT')
 model.zero_grad(set_to_none=True)
 torch.cuda.synchronize();peak=torch.cuda.max_memory_allocated()
 require(peak<12*1024**3,'GPU_SMOKE_PEAK_OVER_12_GIB')
 model=model.to('cpu');torch.cuda.empty_cache()
 return peak

def preflight(a,runpath_must_absent):
 root,p=require_source(a.input)
 out=Path(a.drive_output).resolve()
 require(out.name==RUN_ID and out.parent.is_dir(),'OUTPUT_PATH_RUN_ID')
 require(str(out).startswith('/content/drive/MyDrive/TTM/ttm-small-pilot/'),'OUTPUT_OUTSIDE_APPROVED_OWNER_DRIVE')
 require((not out.exists()) if runpath_must_absent else out.is_dir(),'OUTPUT_EXISTS_OR_NOT_EXISTS')
 require(a.free_only_confirmed,'FREE_COLAB_OWNER_CONFIRM_REQUIRED')
 env=gpu_preflight(a.owner_verified_drive_free_gib)
 sw,p02,old,ckpt,donor,src,valid,e0=model_context(root,p)
 pridge,porth,scale=shared_init(src,valid,e0,donor)
 perm_src=permutation(src,valid)
 projected={}
 for real,perm,p0 in [('RidgeReal','RidgePerm',pridge),('OrthReal','OrthPerm',porth)]:
  hreal=projected_multiset_hash(src,p0,valid)
  hperm=projected_multiset_hash(perm_src,p0,valid)
  require(hreal==hperm,'PROJECTED_MULTISET_MISMATCH')
  projected[real]=hreal;projected[perm]=hperm
 full_params=source_parity(sw,p02,old,ckpt,donor,src,perm_src,valid,e0,pridge,porth)
 data=load_t4(root,p)
 hd,hcnt,hpublic=load_h512(a.h512)
 draws,draw_sha=schedule(data['train_count'])
 model,_=construct('RP-F',sw,p02,old,ckpt,donor,src,perm_src,valid,e0,pridge,porth)
 peak=gpu_smoke(model,'cuda:0')
 log={'schema':'ttm.causal6.preclaim.v1','run_id':RUN_ID,'input_sha256':PINS,
  'runner_sha256':hash_file(Path(__file__)),'schedule_sha256':draw_sha,
  'source_parity_C2048':'PASS_EXACT_STATE_AND_SYNTHETIC_LOGITS','h512_public_seal_sha256':hash_file(Path(a.h512)/'H512_PUBLIC_SEAL.json'),
  'h512_membership_sha256':hpublic['membership_private_sha256'],'h512_pack_sha256':hpublic['h512_window_pack_sha256'],
  'six_arms':ARMS,'hyperparameters':{'steps':STEPS,'targets':TARGETS,'micro':MICRO,'lr':.0001,'betas':[.9,.95],'eps':1e-8,'wd':.1,'clip':1.},
  'seeds':{'model':SEED,'perm':PERM_SEED,'schedule':SCHEDULE_SEED,'bootstrap':BOOT_SEED},
  'env':env,'free_colab_owner_attested':True,'drive_gib_owner_attested':a.owner_verified_drive_free_gib,
  'gpu_synthetic_peak_bytes':peak,'init_projection_sha256':{'ridge':hash_bytes(pridge.numpy().tobytes()),'orth':hash_bytes(porth.numpy().tobytes())},
  'procrustes_scale':scale,'projected_multiset_sha256':projected,'full_trainable_parameters':full_params,'claimed':False}
 return (log,sw,p02,old,ckpt,donor,src,perm_src,valid,e0,pridge,porth,data,hd,hcnt,draws,draw_sha)

def train_chunk(m,opt,packets,data,start,stop):
 m.train();losses=[]
 device=torch.device('cuda:0')
 for step in range(start,stop):
  ids,limits=packets[step];require(sum(limits)==TARGETS,'TRAIN_PACKET_BUDGET')
  opt.zero_grad(set_to_none=True);total_loss=0.
  for offset in range(0,len(ids),MICRO):
   sel=ids[offset:offset+MICRO];lims=limits[offset:offset+MICRO]
   x=torch.from_numpy(data['train_x'][sel].copy()).to(device,dtype=torch.long)
   y=data['train_y'][sel].copy()
   for k,limit in enumerate(lims):y[k,limit:]=-100
   require(int((y!=-100).sum())==sum(lims),'TRAIN_MICRO_MASK')
   y=torch.from_numpy(y).to(device,dtype=torch.long)
   logits,_=m(x)
   l=F.cross_entropy(logits.float().reshape(-1,2048),y.reshape(-1),ignore_index=-100,reduction='sum')/TARGETS
   require(bool(torch.isfinite(l)),'NONFINITE_TRAIN_LOSS')
   l.backward();total_loss+=float(l.detach())
  params=[p for p in m.parameters() if p.requires_grad]
  require(all(p.grad is not None and torch.isfinite(p.grad).all() for p in params),'NONFINITE_GRADS')
  torch.nn.utils.clip_grad_norm_(params,1.)
  opt.step();losses.append(total_loss)
 return losses

def save_ready(out,arm,step,m,opt,losses,pre,env):
 folder=out/'checkpoints'/arm/f'step_{step:04d}'
 require(not folder.exists(),'READY_OVERWRITE_FORBIDDEN')
 folder.mkdir(parents=True,exist_ok=False)
 temp=folder/'checkpoint.pt'
 data={'schema':'ttm.causal6.checkpoint.ready_state.v1','run_id':RUN_ID,'arm':arm,'step':step,
  'source_sha256':pre['runner_sha256'],'schedule_sha256':pre['schedule_sha256'],
  'env':env,'model':m.state_dict(),'optimizer':opt.state_dict(),'train_losses':losses,
  'sampler_cursor':step,'cpu_rng':torch.get_rng_state(),'cuda_rng':torch.cuda.get_rng_state_all()}
 with temp.open('xb') as fd:torch.save(data,fd);fd.flush();os.fsync(fd.fileno())
 digest=hash_file(temp)
 exclusive_json(folder/'READY.json',{'schema':'ttm.causal6.ready.v1','run_id':RUN_ID,'arm':arm,
  'step':step,'checkpoint_sha256':digest,'bytes':temp.stat().st_size,
  'source_sha256':pre['runner_sha256'],'schedule_sha256':pre['schedule_sha256'],'env':env})
 return digest

def load_ready(out,arm,step,m,opt,pre,env):
 folder=out/'checkpoints'/arm/f'step_{step:04d}'
 r=read_json(folder/'READY.json')
 require(r['step']==step and r['arm']==arm and r['run_id']==RUN_ID and r['env']==env and
  r['source_sha256']==pre['runner_sha256'] and r['schedule_sha256']==pre['schedule_sha256'] and
  hash_file(folder/'checkpoint.pt')==r['checkpoint_sha256'],'RESTORE_READY_PIN')
 cp=torch.load(folder/'checkpoint.pt',map_location='cpu',weights_only=True)
 require(cp['step']==step and cp['sampler_cursor']==step and cp['run_id']==RUN_ID and
  len(cp['train_losses'])==step,'RESTORED_CURSOR_LOSSES')
 m.load_state_dict(cp['model'],strict=True);opt.load_state_dict(cp['optimizer'])
 torch.set_rng_state(cp['cpu_rng']);torch.cuda.set_rng_state_all(cp['cuda_rng'])
 return list(cp['train_losses'])

@torch.inference_mode()
def story_score(m,hd):
 m.eval();sums=np.zeros(512,dtype=np.float64)
 for start in range(0,len(hd['x']),MICRO):
  stop=min(start+MICRO,len(hd['x']))
  x=torch.from_numpy(hd['x'][start:stop].copy()).to('cuda:0',dtype=torch.long)
  y=torch.from_numpy(hd['y'][start:stop].copy()).to('cuda:0',dtype=torch.long)
  logits,_=m(x)
  require(bool(torch.isfinite(logits).all()),'SCORER_NONFINITE_LOGITS')
  losses=F.cross_entropy(logits.float().reshape(-1,2048),y.reshape(-1),ignore_index=-100,reduction='none')
  np.add.at(sums,hd['story_index'][start:stop],losses.reshape(stop-start,256).sum(dim=1).double().cpu().numpy())
 return sums

def contrasts(scores,counts):
 nll={k:float(v.sum()/counts.sum()) for k,v in scores.items()}
 pairs={'donor_real_vs_perm':(scores['RP-F']-scores['RR-F']),
 'donor_adapter_real_vs_perm':(scores['RP-A']-scores['RR-A']),
 'donor_orth_real_vs_perm':(scores['OP-F']-scores['OR-F'])}
 tauD=pairs['donor_real_vs_perm'];tauA=tauD-pairs['donor_adapter_real_vs_perm'];tauP=tauD-pairs['donor_orth_real_vs_perm']
 expr={'tau_D':tauD,'tau_A':tauA,'tau_P':tauP}
 rng=np.random.default_rng(BOOT_SEED);ix=rng.integers(0,512,size=(2000,512))
 out={}
 for name,arr in expr.items():
  d=arr[ix].sum(axis=1)/counts[ix].sum(axis=1)
  ci=[float(q) for q in np.quantile(d,[.025,.975])]
  out[name]={'delta_nll':float(arr.sum()/counts.sum()),'ci95_percentile':ci,'ci_lower_gt_zero':ci[0]>0}
 return nll,out

def post_train(out,pre,sw,p02,old,ckpt,donor,src,psrc,valid,e0,pridge,porth,hd,hcnt,env):
 require(all((out/'checkpoints'/arm/'step_2048'/'READY.json').is_file() for arm in ARMS),'SIX_FINAL_READY_MISSING')
 require(not (out/'SCORING_START.json').exists(),'SCORING_ONE_SHOT_ALREADY_STARTED')
 exclusive_json(out/'SCORING_START.json',{'run_id':RUN_ID,'source_sha256':pre['runner_sha256']})
 scores={}
 for arm in ARMS:
  m,_=construct(arm,sw,p02,old,ckpt,donor,src,psrc,valid,e0,pridge,porth)
  # only model weights needed for evaluation; latest checkpoint full restore not required here.
  c=read_json(out/'checkpoints'/arm/'step_2048'/'READY.json')
  cp=out/'checkpoints'/arm/'step_2048'/'checkpoint.pt'
  require(hash_file(cp)==c['checkpoint_sha256'],'FINAL_CHECKPOINT_INTEGRITY_'+arm)
  m.load_state_dict(torch.load(cp,map_location='cpu',weights_only=True)['model'],strict=True)
  m=m.to(device='cuda:0',dtype=torch.float32)
  scores[arm]=story_score(m,hd)
  del m;torch.cuda.empty_cache()
 per={'schema':'ttm.causal6.per_story.private.v1','run_id':RUN_ID,'target_counts':hcnt.tolist(),
      'loss_sum_by_arm':{k:v.tolist() for k,v in scores.items()},'h512_membership_sha256':pre['h512_membership_sha256']}
 exclusive_json(out/'PER_STORY_PRIVATE.json',per)
 nll,cis=contrasts(scores,hcnt)
 label='PASS_SCOPED_DONOR_MAPPING_ALIGNMENT' if cis['tau_D']['ci_lower_gt_zero'] else 'DONOR_MAPPING_EFFECT_NOT_ESTABLISHED'
 res={'schema':'ttm.causal6.result.public.v1','run_id':RUN_ID,'status':'COMPLETED_PENDING_INDEPENDENT_ADJUDICATION',
  'scientific_candidate_verdict':label,'nll_nats_per_target':nll,'contrasts':cis,'bootstrap_draws':2000,
  'bootstrap_seed':BOOT_SEED,'target_count':int(hcnt.sum()),'stories':512,'windows':len(hd['x']),
  'arm_count':len(ARMS),'steps_per_arm':STEPS,'targets_per_step':TARGETS,
  'per_story_sha256':hash_file(out/'PER_STORY_PRIVATE.json'),'claim_sha256':hash_file(out/'CLAIM.json'),
  'h512_membership_sha256':pre['h512_membership_sha256'],'source_runner_sha256':pre['runner_sha256'],
  'no_historical_TEST_read':True,'no_old_320_read':True,'gpu_name':env['device']}
 exclusive_json(out/'RESULT.json',res)
 print('CAUSAL6_SCIENCE_RESULT_SHA256='+hash_file(out/'RESULT.json'))
 print('CAUSAL6_CANDIDATE_VERDICT='+label)

def execute(a):
 out=Path(a.drive_output).resolve()
 resume=a.mode=='resume'
 pack=preflight(a,not resume)
 (pre,sw,p02,old,ckpt,donor,src,psrc,valid,e0,pridge,porth,data,hd,hcnt,draws,sched_sha)=pack
 env=pre['env']
 if not resume:
  out.mkdir(parents=True,exist_ok=False)
  pre['claimed']=True
  exclusive_json(out/'CLAIM.json',pre)
  print('CAUSAL6_ONE_SHOT_CLAIM=CONSUMED sha256='+hash_file(out/'CLAIM.json'),flush=True)
  exclusive_json(out/'SCHEDULE_PRIVATE.json',{'run_id':RUN_ID,'sha256':sched_sha,'ordered_packets':draws})
 else:
  claim=read_json(out/'CLAIM.json');pre['claimed']=True
  for key in ('source_parity_C2048','input_sha256','runner_sha256','schedule_sha256','h512_public_seal_sha256','h512_membership_sha256','h512_pack_sha256','init_projection_sha256','projected_multiset_sha256','env','six_arms','hyperparameters','seeds'):
   require(claim[key]==pre[key],'CLAIM_ENV_OR_SOURCE_CHANGED_'+key)
  require(not (out/'SCORING_START.json').exists() and not (out/'RESULT.json').exists(),'SCORING_OR_RESULT_CANNOT_RESUME')
 for arm in ARMS:
  m,_=construct(arm,sw,p02,old,ckpt,donor,src,psrc,valid,e0,pridge,porth)
  m=m.to(device='cuda:0',dtype=torch.float32)
  opt=torch.optim.AdamW([p for p in m.parameters() if p.requires_grad],lr=1e-4,betas=(.9,.95),eps=1e-8,weight_decay=.1)
  armfolder=out/'checkpoints'/arm;armfolder.mkdir(parents=True,exist_ok=True)
  completes=[k for k in range(256,STEPS+1,256) if (armfolder/f'step_{k:04d}'/'READY.json').is_file()]
  start=max(completes) if completes else 0
  require(completes==list(range(256,start+1,256)),'NONCONTIGUOUS_READY_'+arm)
  # durable chunk-start must be paired with DONE and READY; incomplete = HOLD, no replay.
  for j in range(256,STEPS+1,256):
   started=armfolder/f'CHUNK_{j:04d}_START.json';done=armfolder/f'CHUNK_{j:04d}_DONE.json'
   if started.exists():
    require(done.exists() and (armfolder/f'step_{j:04d}'/'READY.json').exists(),'UNFINISHED_CHUNK_NO_REPLAY_'+arm+str(j))
   if done.exists():require(started.exists(),'ORPHAN_DONE_'+arm+str(j))
  if start==0:
   require(not (armfolder/'ARM_START.json').exists(),'ARM_STARTED_NO_READY_'+arm)
   exclusive_json(armfolder/'ARM_START.json',{'run_id':RUN_ID,'arm':arm,'source_sha256':pre['runner_sha256']})
   losses=[]
  else:
   require((armfolder/'ARM_START.json').exists(),'MISSING_START_MARKER_'+arm)
   losses=load_ready(out,arm,start,m,opt,pre,env)
  for stop in range(start+256,STEPS+1,256):
   exclusive_json(armfolder/f'CHUNK_{stop:04d}_START.json',{'run_id':RUN_ID,'arm':arm,'after_step':stop-256,'target_step':stop})
   losses.extend(train_chunk(m,opt,draws,data,stop-256,stop))
   require(len(losses)==stop,'LOSS_HISTORY_STEP_COUNT')
   digest=save_ready(out,arm,stop,m,opt,losses,pre,env)
   exclusive_json(armfolder/f'CHUNK_{stop:04d}_DONE.json',{'run_id':RUN_ID,'arm':arm,'step':stop,'ready_sha256':digest})
   print('CAUSAL6_READY arm='+arm+' step='+str(stop)+' SHA256='+digest,flush=True)
  del m,opt;torch.cuda.empty_cache()
 post_train(out,pre,sw,p02,old,ckpt,donor,src,psrc,valid,e0,pridge,porth,hd,hcnt,env)

def fixture():
 c=np.arange(1,513,dtype=np.int64); a=np.linspace(0,1,512); b=a+.03; d=a+.01
 sums={'RR-F':a,'RP-F':b,'RR-A':d,'RP-A':d+.01,'OR-F':a+.02,'OP-F':a+.04}
 n,ci=contrasts(sums,c)
 assert len(n)==6 and ci['tau_D']['delta_nll']>0 and ci['tau_D']['ci_lower_gt_zero']
 assert all(np.isfinite(x['delta_nll']) for x in ci.values())
 s,h=schedule(np.ones(2691,dtype=np.int64)*256)
 assert len(s)==2048 and all(sum(n)==4096 for _,n in s)
 print(json.dumps({'status':'PASS_SYNTHETIC_ONLY','tests':5,'science_executed':False,'gpu_used':False,'schedule_sha256_fixture':h},sort_keys=True))

def cpu_source_qa(a):
 root,p=require_source(a.input)
 sw,p02,old,ckpt,donor,src,valid,e0=model_context(root,p)
 pridge,porth,scale=shared_init(src,valid,e0,donor)
 perm_src=permutation(src,valid)
 require(projected_multiset_hash(src,pridge,valid)==projected_multiset_hash(perm_src,pridge,valid),'CPU_RIDGE_MULTISET_PARITY')
 require(projected_multiset_hash(src,porth,valid)==projected_multiset_hash(perm_src,porth,valid),'CPU_ORTH_MULTISET_PARITY')
 source_parity(sw,p02,old,ckpt,donor,src,perm_src,valid,e0,pridge,porth)
 data=load_t4(root,p)
 h,counts,pub=load_h512(a.h512)
 draws,schedsha=schedule(data['train_count'])
 print(json.dumps({'status':'PASS_REAL_SOURCE_CPU_PARITY_NOT_SCIENCE','C2048_state_and_logits':'PASS_EXACT',
   'real_perm_projected_multiset':'PASS_TWO_METHODS','h512_stories':512,'h512_targets':int(counts.sum()),
   'h512_windows':len(h['x']),'schedule_sha256':schedsha,'gamma_free_no_claim':True,'gpu_used':False},sort_keys=True))

def main():
 a=argparse.ArgumentParser()
 a.add_argument('--mode',choices=('fixture','cpu-source-qa','preflight','execute','resume'),required=True)
 a.add_argument('--input',default='');a.add_argument('--h512',default='');a.add_argument('--drive-output',default='')
 a.add_argument('--owner-verified-drive-free-gib',type=float,default=0)
 a.add_argument('--free-only-confirmed',action='store_true')
 args=a.parse_args()
 if args.mode=='fixture':fixture();return
 if args.mode=='cpu-source-qa':cpu_source_qa(args);return
 if args.mode=='preflight':
  pre,*_=preflight(args,True)
  print(json.dumps({k:pre[k] for k in ('schema','run_id','env','source_parity_C2048','h512_public_seal_sha256','gpu_synthetic_peak_bytes')},sort_keys=True));return
 execute(args)

if __name__=='__main__':main()
