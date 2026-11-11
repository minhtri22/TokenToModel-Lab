#!/usr/bin/env python3
"""CPU-only text-architecture parameter mirror of EmbeddingGemma2TextModel.

Source geometry: huggingface/transformers modeling_embedding_gemma2.py Git blob
c0fedeb4228fdab6020a78f6104fe05572996e1d (2026-11-11 main inspection).
HISTORICAL donor config SHA declared (not bytes read in this run):
b8f1e9931b57fbc054acdb445c41765d55b0074c58d145fa82839941ad1b5bb3
Do not mistake this for an instance of the official Transformers class or a
pretrained-semantic counterfactual. It does not implement forward/inference.
"""
from __future__ import annotations
import argparse, hashlib, json, sys
from pathlib import Path
import torch
from torch import nn
import safetensors.torch

SEED=2026111194
V,H,INTER,N_LAYER,DIM_OUT,PLE_DIM=262144,512,2048,24,768,512
FULL_LAYER={5,11,17,23}
MODEL_SOURCE_BLOB='c0fedeb4228fdab6020a78f6104fe05572996e1d'
CONFIG_SOURCE_SHA='b8f1e9931b57fbc054acdb445c41765d55b0074c58d145fa82839941ad1b5bb3'

class Norm(nn.Module):
 def __init__(self,n):
  super().__init__();self.weight=nn.Parameter(torch.ones(n))
class Attn(nn.Module):
 def __init__(self,i):
  super().__init__();heads=4;hd=512 if i in FULL_LAYER else 256
  nkv=1 if i in FULL_LAYER else 2
  self.q_proj=nn.Linear(H,heads*hd,bias=False)
  self.k_proj=nn.Linear(H,nkv*hd,bias=False)
  self.v_proj=nn.Linear(H,nkv*hd,bias=False)
  self.o_proj=nn.Linear(heads*hd,H,bias=False)
  self.q_norm=Norm(hd);self.k_norm=Norm(hd)
  # v_norm has with_scale=False and therefore no parameters
class MLP(nn.Module):
 def __init__(self):
  super().__init__();self.gate_proj=nn.Linear(H,INTER,bias=False)
  self.up_proj=nn.Linear(H,INTER,bias=False)
  self.down_proj=nn.Linear(INTER,H,bias=False)
class PLEBlock(nn.Module):
 def __init__(self):
  super().__init__();self.per_layer_input_gate=nn.Linear(H,PLE_DIM,bias=False)
  self.per_layer_projection=nn.Linear(PLE_DIM,H,bias=False)
  self.post_per_layer_input_norm=Norm(H)
class Layer(nn.Module):
 def __init__(self,i):
  super().__init__();self.self_attn=Attn(i);self.mlp=MLP()
  self.input_layernorm=Norm(H);self.post_attention_layernorm=Norm(H)
  self.pre_feedforward_layernorm=Norm(H);self.post_feedforward_layernorm=Norm(H)
  self.register_buffer('layer_scalar',torch.ones(1))
  self.ple_block=PLEBlock()
class PLE(nn.Module):
 def __init__(self):
  super().__init__();self.per_layer_model_projection=nn.Linear(H,N_LAYER*PLE_DIM,bias=False)
  self.per_layer_projection_norm=Norm(PLE_DIM)
class TextParameterMirror(nn.Module):
 def __init__(self):
  super().__init__();self.embed_tokens=nn.Embedding(V,H,padding_idx=0)
  self.layers=nn.ModuleList([Layer(i) for i in range(N_LAYER)])
  self.norm=Norm(H);self.ple=PLE();self.embedding_projection=nn.Linear(H,DIM_OUT,bias=False)
 # Intentionally no forward: prevents accidental inference under design-only gate

def initialize(model,seed):
 # Explicit independent generator; deterministic parameter-name order.
 generator=torch.Generator(device='cpu').manual_seed(seed)
 with torch.no_grad():
  for name,param in model.named_parameters():
   if name.endswith('.weight') and ('.norm.' in name or 'layernorm' in name or name.endswith('norm.weight') or name.endswith('q_norm.weight') or name.endswith('k_norm.weight')):
    param.fill_(1.0)
   else:
    torch.nn.init.trunc_normal_(param,mean=0,std=0.02,a=-0.04,b=0.04,generator=generator)
  model.embed_tokens.weight[0].zero_()

def fingerprint(model):
 # Stable name + dtype + shape + bytes SHA; no checkpoint tensors printed.
 h=hashlib.sha256(); stats=[]
 with torch.no_grad():
  for name,p in sorted(model.state_dict().items()):
   a=p.detach().contiguous().cpu().numpy()
   hh=hashlib.sha256(memoryview(a).cast('B')).hexdigest()
   line=json.dumps([name,list(p.shape),str(p.dtype),hh],separators=(',',':'))
   h.update(line.encode()+b'\n')
   stats.append([name,list(p.shape)])
 return h.hexdigest(),stats

def run(output,recheck=True):
 torch.set_num_threads(2)
 m=TextParameterMirror();initialize(m,SEED)
 digest,stats=fingerprint(m)
 assert len(m.layers)==24 and len(stats)>300
 assert all(m.layers[i].self_attn.q_proj.weight.shape[0]==(2048 if i in FULL_LAYER else 1024) for i in range(24))
 assert m.embed_tokens.weight.shape==(V,H)
 assert torch.count_nonzero(m.embed_tokens.weight[0]).item()==0
 if output:
  out=Path(output);assert not out.exists(),'REFUSE_OVERWRITE'
  # Hidden tensors stay locally private; write only on explicit output request.
  safetensors.torch.save_file({k:v.cpu().contiguous() for k,v in m.state_dict().items()},str(out),metadata={'scope':'NONPRETRAINED_TEXT_PARAMETER_MIRROR_NO_FORWARD','seed':str(SEED)})
  sha=hashlib.sha256(out.read_bytes()).hexdigest()
  saved_bytes=out.stat().st_size
 else:sha=None;saved_bytes=0
 del m
 if recheck:
  m2=TextParameterMirror();initialize(m2,SEED)
  digest2,_=fingerprint(m2)
  assert digest==digest2,'REGENERATION_SHA_MISMATCH'
  del m2
 else:digest2=None
 print(json.dumps({'status':'PASS_CPU_TEXT_PARAMETER_TOPOLOGY_AND_SEEDED_INIT_REGENERATED',
 'not_official_hf_class':True,'fully_executable_official_model':False,
 'seed':SEED,'source_architecture_git_blob':MODEL_SOURCE_BLOB,
 'pinned_donor_config_sha256_reference_only':CONFIG_SOURCE_SHA,
 'layers':N_LAYER,'full_attention_layers':sorted(FULL_LAYER),
 'vocab_size':V,'hidden_size':H,'out_embedding_dim':DIM_OUT,
 'total_state_tensors':len(stats),'parameter_count':sum(p.numel() for p in TextParameterMirror().parameters()),
 'name_shape_sha256':hashlib.sha256(json.dumps(stats,separators=(',',':')).encode()).hexdigest(),
 'initialized_state_merkle_sha256':digest,'repeat_merkle_sha256':digest2,
 'private_state_safetensors_sha256':sha,'private_state_bytes':saved_bytes,
 'torch_version':torch.__version__,'no_model_forward':True,'no_training':True,
 'exact_transformers_init_equivalence_proven':False,'donor_tokenizer_mapping_verified':False,
 'scientific_admission':'HOLD_UNTIL_ACTUAL_TRANSFORMERS_CLASS_AND_PINNED_TOKENIZER'},sort_keys=True))

if __name__=='__main__':
 ap=argparse.ArgumentParser();ap.add_argument('--output');ap.add_argument('--no-recheck',action='store_true');a=ap.parse_args()
 run(a.output,not a.no_recheck)
