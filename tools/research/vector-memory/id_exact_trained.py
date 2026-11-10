#!/usr/bin/env python3
"""TTM trained checkpoint CPU test: externalize tied token embedding/output head.

Source architecture: original P02 git blob 9762343e06cf800b50574c2871ae1ed58537fb18
from minhtri22/TokenToModel-Lab, inspected on 2026-11-11.

A original P02 GPT (tok.weight tied to head.weight).
B external full-precision vector table used for BOTH embedding retrieval and
  output-head linear projection; no tied table inside model core.
C external FP16 vector table used for BOTH roles, restored to FP32 at execution.
D external row-wise INT8 vector table used for BOTH roles, restored to FP32.
E negative control: one wrong second-nearest vector at first token per sequence;
  same shared core and head computation.

Key query is nonlearned deterministic 8D Fourier encoding of token ID, not the
original embedding, so retrieval is not a circular self-query.

NOT evaluated: semantic knowledge retrieval, replacement of attention/MLP,
real-world language quality, or multi-step LLM inference quality.
"""
import argparse
import hashlib
import json
import math
from pathlib import Path
import torch
from torch import nn
from torch.nn import functional as F

EXPECTED_SHA256 = 'ee723407b2c25a18be20e26387a3dd8e4a18e2942d469279b6f0748ff86af0dc'
SOURCE_GIT_BLOB = '9762343e06cf800b50574c2871ae1ed58537fb18'

class CausalSelfAttention(nn.Module):
    # Exact math and operator order from original P02 blob.
    def __init__(self, dim, heads):
        super().__init__()
        self.heads=heads
        self.head_dim=dim//heads
        self.qkv=nn.Linear(dim,3*dim)
        self.proj=nn.Linear(dim,dim)
    def _split(self,t):
        batch,time,channels=t.shape
        return t.reshape(batch,time,self.heads,self.head_dim).transpose(1,2)
    def forward(self,x):
        batch,time,channels=x.shape
        q,k,v=[self._split(a) for a in self.qkv(x).chunk(3,dim=-1)]
        scores=q@k.transpose(-2,-1)/math.sqrt(self.head_dim)
        mask=torch.ones(time,time,dtype=torch.bool,device=x.device).tril()
        weights=scores.masked_fill(~mask,-torch.inf).softmax(dim=-1)
        y=weights@v
        y=y.transpose(1,2).contiguous().reshape(batch,time,channels)
        return self.proj(y)

class Block(nn.Module):
    def __init__(self, dim, heads):
        super().__init__()
        self.ln1=nn.LayerNorm(dim)
        self.attn=CausalSelfAttention(dim,heads)
        self.ln2=nn.LayerNorm(dim)
        self.mlp=nn.Sequential(nn.Linear(dim,4*dim),nn.GELU(),nn.Linear(4*dim,dim))
    def forward(self,x):
        x=x+self.attn(self.ln1(x))
        return x+self.mlp(self.ln2(x))

class OriginalP02GPT(nn.Module):
    # Original P02 topology, including tied input/output weights.
    def __init__(self,cfg):
        super().__init__()
        d=cfg['n_embd'];v=cfg['vocab_size']
        self.tok=nn.Embedding(v,d)
        self.pos=nn.Embedding(cfg['max_seq_len'],d)
        self.blocks=nn.ModuleList([Block(d,cfg['n_head']) for _ in range(cfg['n_layer'])])
        self.final_ln=nn.LayerNorm(d)
        self.head=nn.Linear(d,v,bias=False)
        self.head.weight=self.tok.weight
    def forward(self,tokens):
        positions=torch.arange(tokens.shape[1],device=tokens.device)
        x=self.tok(tokens)+self.pos(positions)[None,:,:]
        for block in self.blocks: x=block(x)
        return self.head(self.final_ln(x))

class BackboneNoTiedTable(nn.Module):
    # Identical position+attention+MLP+norm computation; no tok or head params.
    def __init__(self,cfg):
        super().__init__()
        d=cfg['n_embd']
        self.pos=nn.Embedding(cfg['max_seq_len'],d)
        self.blocks=nn.ModuleList([Block(d,cfg['n_head']) for _ in range(cfg['n_layer'])])
        self.final_ln=nn.LayerNorm(d)
    def forward(self,token_vectors):
        positions=torch.arange(token_vectors.shape[1],device=token_vectors.device)
        x=token_vectors+self.pos(positions)[None,:,:]
        for block in self.blocks: x=block(x)
        return self.final_ln(x)


def deterministic_id_query(ids,vocab):
    t=ids.to(torch.float64)
    theta=t.unsqueeze(-1)*(2*math.pi/vocab)*torch.tensor([1,3,13,47],dtype=torch.float64)
    code=torch.stack([theta.cos(),theta.sin()],dim=-1).reshape(*t.shape,8).float()
    return F.normalize(code,dim=-1)


def compare_logits(ref,trial):
    d=(ref-trial).abs()
    p=F.log_softmax(ref.float(),dim=-1)
    q=F.log_softmax(trial.float(),dim=-1)
    kl=F.kl_div(q,p.exp(),reduction='none').sum(-1).mean()
    return {'bit_exact_logits':bool(torch.equal(ref,trial)),
            'max_abs_logit_error':float(d.max()),
            'mean_abs_logit_error':float(d.mean()),
            'top1_agreement':float((ref.argmax(-1)==trial.argmax(-1)).float().mean()),
            'mean_kl_ref_to_arm_nats':max(0.0,float(kl))}


def main():
    parser=argparse.ArgumentParser()
    parser.add_argument('--checkpoint',type=Path,default=Path(__file__).resolve().parent / 'checkpoint.pt')
    parser.add_argument('--output',type=Path,default=Path(__file__).resolve().parent / 'ttm_trained_shared_backbone_vector_retrieval_results.json')
    args=parser.parse_args()
    torch.set_num_threads(2)
    torch.manual_seed(20261111)
    torch.use_deterministic_algorithms(True)
    actual_sha=hashlib.sha256(args.checkpoint.read_bytes()).hexdigest()
    if actual_sha != EXPECTED_SHA256: raise ValueError('CHECKPOINT_SHA256_MISMATCH: '+actual_sha)
    ckpt=torch.load(args.checkpoint,map_location='cpu',weights_only=True)
    assert ckpt['step']==1280 and ckpt['config']['vocab_size']==2048
    cfg=ckpt['config'];state=ckpt['model']
    assert state['tok.weight'].data_ptr()==state['head.weight'].data_ptr()
    assert torch.equal(state['tok.weight'],state['head.weight'])
    original=OriginalP02GPT(cfg).cpu().eval()
    original.load_state_dict(state,strict=True)
    assert original.tok.weight.data_ptr()==original.head.weight.data_ptr()

    core=BackboneNoTiedTable(cfg).cpu().eval()
    core.load_state_dict({k:v for k,v in state.items() if k not in ('tok.weight','head.weight')},strict=True)
    assert not any(k.startswith('tok.') or k.startswith('head.') for k in core.state_dict())
    original_unique=sum(p.numel() for p in original.parameters())
    external_unique=state['tok.weight'].numel()
    core_count=sum(p.numel() for p in core.parameters())
    assert original_unique==core_count+external_unique
    assert original_unique==3749376 and external_unique==524288
    assert all(a.data_ptr()!=original.tok.weight.data_ptr() for a in core.parameters())

    values=state['tok.weight'].clone().detach().contiguous()  # EXTERNAL store
    vocab=cfg['vocab_size']
    keys=deterministic_id_query(torch.arange(vocab,dtype=torch.long),vocab)
    with torch.inference_mode():
        similarities=keys@keys.T
        all_nearest=similarities.argmax(-1)
        accuracy=float((all_nearest==torch.arange(vocab)).float().mean())
        assert accuracy==1.0
        margin=float((similarities.diagonal()-similarities.topk(2,dim=-1).values[:,1]).min())
        gen=torch.Generator().manual_seed(314159)
        probes=torch.randint(vocab,(64,32),generator=gen)
        probes[0,:8]=torch.tensor([1,2,3,4,5,6,7,8]);probes[1,:8]=torch.tensor([8,7,6,5,4,3,2,1])
        query=deterministic_id_query(probes,vocab)
        candidate_similarity=query@keys.T
        nearest_ids=candidate_similarity.argmax(-1)
        assert torch.equal(probes,nearest_ids)
        # Verified reproduction of original P02 model using only shared no-table backbone.
        logits_a=original(probes)
        logits_a_split=F.linear(core(state['tok.weight'][probes]),state['tok.weight'])
        assert torch.equal(logits_a,logits_a_split), 'SOURCE_MODEL_RECONSTRUCTION_MISMATCH'

        # B: learned table is absent from model core and fetched from external memory
        logits_b=F.linear(core(values[nearest_ids]),values)
        assert torch.equal(logits_a,logits_b)

        # C: compress tied table once, use for both input and output, no separate copy
        half_table=values.half()
        external_c=half_table.float()
        logits_c=F.linear(core(external_c[nearest_ids]),external_c)

        # D: symmetric int8 per-row, reconstruct tied table for input + output
        scales=values.abs().amax(-1,keepdim=True).clamp_min(1e-12)/127.0
        q8=(values/scales).round().clamp(-127,127).to(torch.int8)
        external_d=q8.float()*scales
        logits_d=F.linear(core(external_d[nearest_ids]),external_d)

        # E: bad retrieval is not equivalent even if attention/MLP unchanged
        wrong=nearest_ids.clone()
        wrong[:,0]=candidate_similarity[:,0].topk(2,dim=-1).indices[:,1]
        assert bool(torch.all(wrong[:,0]!=probes[:,0]))
        logits_e=F.linear(core(values[wrong]),values)

    n_tokens=int(probes.numel())
    original_embedding_bytes=values.numel()*4
    key_bytes=keys.numel()*4
    half_bytes=values.numel()*2
    int8_bytes=q8.numel()+scales.numel()*4
    result={
      'experiment':'TTM_TRAINED_MODEL_SHARED_BACKBONE_VECTOR_RETRIEVAL_TEST',
      'checkpoint':{'source':'Google Drive TTM-Small-4M step_1280/checkpoint.pt',
                    'sha256':actual_sha,'step':ckpt['step'],'schema':ckpt['schema'],
                    'source_p02_git_blob':SOURCE_GIT_BLOB,'config':cfg,
                    'distinct_learned_parameters_total':original_unique,
                    'state_dict_entries_including_tied_duplicate':sum(v.numel() for v in state.values()),
                    'tied_tok_and_head':True,
                    'tied_table_parameters':external_unique,
                    'shared_core_parameters_without_tied_table':core_count,
                    'fraction_unique_parameters_moved_outside_model':external_unique/original_unique},
      'method':{'torch':torch.__version__,'device':'cpu','dtype':'fp32 for compute',
                'probe_sequences':int(probes.shape[0]),'token_positions':n_tokens,
                'probe_source':'synthetic token IDs, not real-language held-out set',
                'original_p02_forward_matches_refactored_backbone_bit_exact':bool(torch.equal(logits_a,logits_a_split)),
                'same_weights_attention_mlp':'All arms use exact same BackboneNoTiedTable module and initial weights from checkpoint; A also checked against full original GPT',
                'shared_head_operation':'F.linear on output using same table (externalized tied table for B/C/D); no head.weight in externalized core',
                'external_keys':'8D deterministic Fourier code from IDs, no learned embedding values as query',
                'external_search':'cosine nearest neighbor',
                'full_vocab_nn_accuracy':accuracy,'min_top1_top2_cosine_margin':margin},
      'arms':{'A_original_p02_trained_fp32':{'baseline':True},
              'B_external_fp32_exact':compare_logits(logits_a,logits_b),
              'C_external_fp16_tied_table':compare_logits(logits_a,logits_c),
              'D_external_int8_tied_table':compare_logits(logits_a,logits_d),
              'E_wrong_nearest_first_token':compare_logits(logits_a,logits_e)},
      'storage_bytes':{'original_tied_table_fp32':original_embedding_bytes,
                       'keys_8d_fp32':key_bytes,
                       'external_fp32_values_plus_keys':original_embedding_bytes+key_bytes,
                       'external_fp16_values_plus_keys':half_bytes+key_bytes,
                       'external_int8_values_scales_plus_keys':int8_bytes+key_bytes,
                       'excludes':'IDs, ANN index structures, runtime and other bookkeeping'},
      'conclusion':{'externalizing_trained_tied_table_with_same_transformer':'YES',
                    'bit_exact_external_fp32':'YES',
                    'eliminating_learned_table_from_model_parameter_storage':'YES',
                    'eliminating_learned_table_from_all_storage':'NO',
                    'compress_fp16_int8_bit_exact':'NO',
                    'replace_attention_or_mlp':'NOT_TESTED',
                    'preserve_language_quality_on_real_text':'NOT_TESTED',
                    'scope':'Toy-sized real trained checkpoint, ID-keyed exact retrieval, NOT semantic retrieval.'}
    }
    assert result['arms']['E_wrong_nearest_first_token']['top1_agreement']<0.999
    args.output.parent.mkdir(parents=True,exist_ok=True)
    args.output.write_text(json.dumps(result,indent=2,ensure_ascii=False)+'\n',encoding='utf-8')
    print(json.dumps(result,indent=2,ensure_ascii=False))

if __name__=='__main__':main()
