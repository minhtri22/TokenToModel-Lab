"""Independent P06 CPU oracle: PyTorch SDPA, P05 and P00 reference fixtures.

Only synthetic token IDs; no corpus, optimizer, checkpoint, or GPU kernel.
"""
from __future__ import annotations

import json
import math
from pathlib import Path
import sys
import traceback

import torch
from torch.nn import functional as F

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT))
from src.p02.transformer_core import GPT, P02Config
from src.p05.dense_kv_cache import DenseKVCache, dense_forward_tokens
from src.p06.paged_kv_manager import PagedKVCache, paged_forward_tokens, benchmark_paged_vs_dense
sys.path.insert(0, str(ROOT / 'reference' / 'phase0'))
from paged_kv import PagedKVCache as P00PagedKVCache


def new_paged(block_size: int = 3, n_blocks: int = 14) -> PagedKVCache:
    return PagedKVCache(n_layers=2,n_blocks=n_blocks,block_size=block_size,
                        n_heads=4,head_dim=16,max_seq_len=32,max_requests=3)


@torch.inference_mode()
def full_prefix_sdpa_oracle(model: GPT, ids: list[int]) -> torch.Tensor:
    """Independent full-sequence attention via SDPA instead of cache gather."""
    inp=torch.tensor([ids],dtype=torch.long)
    pos=torch.arange(len(ids),dtype=torch.long)
    x=model.tok(inp)+model.pos(pos)[None,:,:]
    for block in model.blocks:
        attn=block.attn
        raw=attn.qkv(block.ln1(x))
        bs,t,emb3=raw.shape
        emb=emb3//3
        q,k,v=raw.chunk(3,dim=-1)
        def reshape(y):
            return y.reshape(bs,t,model.cfg.n_head,emb//model.cfg.n_head).transpose(1,2)
        y=F.scaled_dot_product_attention(reshape(q),reshape(k),reshape(v),
                                         is_causal=True,dropout_p=0.0)
        y=y.transpose(1,2).contiguous().reshape(bs,t,emb)
        x=x+attn.proj(y)
        x=x+block.mlp(block.ln2(x))
    return model.head(model.final_ln(x))[0,-1]


def check_sdpa_vs_dense_vs_paged_crossing_page_boundary() -> None:
    for norm in ('layernorm','rmsnorm'):
        torch.manual_seed(906)
        model=GPT(P02Config(norm_type=norm)).eval()
        paged=new_paged()
        dense=DenseKVCache(n_layers=2,max_seq_len=32,n_heads=4,head_dim=16,max_requests=1)
        paged.start('i');dense.start('i')
        ids=[2047,256,18,27,1034,40,1555,6,74,2047]
        for t,token in enumerate(ids,1):
            a=paged_forward_tokens(model,[token],paged,'i')
            b=dense_forward_tokens(model,[token],dense,'i')
            c=full_prefix_sdpa_oracle(model,ids[:t])
            torch.testing.assert_close(a,b,atol=2e-5,rtol=2e-5)
            torch.testing.assert_close(a,c,atol=2e-5,rtol=2e-5)
        assert len(paged.page_table('i'))==4
        dense.release('i');paged.release('i')


def check_interleaved_page_table_isolation_and_scrub_against_p00() -> None:
    torch.manual_seed(907)
    model=GPT(P02Config()).eval()
    cache=new_paged(block_size=2,n_blocks=10)
    reference=P00PagedKVCache(n_layers=2,n_blocks=10,block_size=2,n_heads=4,head_dim=16)
    cache.start('red');cache.start('blue')
    reference.start('red');reference.start('blue')
    seq={'red':[11,256,4,700,1900],'blue':[2047,19,23,3,101,12]}
    seen={'red':[],'blue':[]}
    for i in range(6):
        for rid in ('red','blue'):
            if i>=len(seq[rid]):continue
            tok=seq[rid][i]
            seen[rid].append(tok)
            out=paged_forward_tokens(model,[tok],cache,rid)
            o=full_prefix_sdpa_oracle(model,seen[rid])
            torch.testing.assert_close(out,o,atol=2e-5,rtol=2e-5)
            rpos=reference.allocate_token(rid)
            assert rpos==cache.lengths[rid]-1
            # Independent fixture checks the physical translation with P00.
            k=torch.full((4,16),float(i+1));v=k+0.25
            reference.write(0,rid,rpos,k,v)
            assert set(cache.page_table('red')).isdisjoint(cache.page_table('blue'))
    ids=cache.page_table('red')
    cache.release('red');reference.release('red')
    assert all(torch.count_nonzero(cache.storage[:,:,b]).item()==0 for b in ids)
    cache.start('green');reference.start('green')
    out=paged_forward_tokens(model,[1700,1901,3],cache,'green')
    oracle=full_prefix_sdpa_oracle(model,[1700,1901,3])
    torch.testing.assert_close(out,oracle,atol=2e-5,rtol=2e-5)
    assert set(cache.page_table('green')).isdisjoint(cache.page_table('blue'))
    cache.release('green');cache.release('blue')
    assert cache.stats()['used_blocks']==0
    assert torch.count_nonzero(cache.storage).item()==0


def check_fragments_pool_ownership_and_no_leaks() -> None:
    cache=new_paged(block_size=4,n_blocks=8)
    cache.start('a');cache.start('b');cache.start('c')
    for n,rid in ((1,'a'),(7,'b'),(3,'c')):
        for _ in range(n):cache.allocate_token(rid)
    st=cache.stats()
    actual_blocks=sum(len(cache.page_table(r)) for r in ('a','b','c'))
    live=sum(cache.lengths.values())
    assert (actual_blocks,live)==(4,11)
    assert st['fragmented_slots']==4*actual_blocks-live==5
    assert st['used_blocks']==4 and st['free_blocks']==4
    assert st['allocated_bytes']==cache.storage.numel()*cache.storage.element_size()
    assert st['reserved_bytes']-st['used_logical_bytes']==st['fragmented_bytes']
    assert len(set().union(*(cache.page_table(r) for r in ('a','b','c'))))==actual_blocks
    for r in ('a','b','c'):cache.release(r)
    assert cache.stats()['free_blocks']==cache.n_blocks
    assert cache.stats()['used_logical_bytes']==0


def check_oom_atomicity_and_invalid_write() -> None:
    cache=new_paged(block_size=2,n_blocks=1)
    cache.start('a');cache.start('b')
    cache.allocate_token('a')
    before=cache.stats().copy(),cache.storage.clone(),cache.page_table('a'),cache.page_table('b')
    try:
        # Needs another physical block, must reject before writing first new token.
        paged_forward_tokens(GPT(P02Config()).eval(),[11,12],cache,'b')
    except MemoryError:pass
    else:raise AssertionError('P06 out-of-block append not rejected')
    assert cache.stats()==before[0]
    assert cache.page_table('a')==before[2] and cache.page_table('b')==before[3]
    torch.testing.assert_close(cache.storage,before[1],atol=0,rtol=0)
    try:cache.write(0,'a',0,torch.ones(4,16,dtype=torch.float64),torch.zeros(4,16))
    except ValueError:pass
    else:raise AssertionError('wrong dtype not rejected')
    torch.testing.assert_close(cache.storage,before[1],atol=0,rtol=0)


def check_cpu_benchmark_bytes_and_no_speedup_claim() -> dict:
    torch.manual_seed(911)
    m=GPT(P02Config()).eval()
    result=benchmark_paged_vs_dense(m,[256,2047,1,1400,70,901,17],repeats=2,block_size=3)
    assert result['status']=='P06_CPU_MEASURED_NO_SPEEDUP_CLAIM'
    assert (result['sequence_length'],result['repeats'],result['block_size'])==(7,2,3)
    bytes_per_token=2*2*4*16*4
    assert result['used_logical_bytes']==7*bytes_per_token
    assert result['fragmented_bytes']==2*bytes_per_token
    assert result['paged_allocated_bytes']>=result['used_logical_bytes']
    for name in ('dense_ms','paged_ms','recompute_ms'):
        assert len(result[name])==2
        assert all(isinstance(t,float) and math.isfinite(t) and t>0 for t in result[name])
    return result


def main() -> int:
    torch.set_num_threads(2)
    checks={
        'explicit_sdpa_vs_p05_dense_vs_p06_paged_logits':check_sdpa_vs_dense_vs_paged_crossing_page_boundary,
        'interleaved_isolation_reuse_scrub_vs_p00':check_interleaved_page_table_isolation_and_scrub_against_p00,
        'independent_fragmentation_and_block_accounting':check_fragments_pool_ownership_and_no_leaks,
        'oom_and_invalid_write_atomicity':check_oom_atomicity_and_invalid_write,
        'cpu_repeated_benchmark_no_speedup_claim':check_cpu_benchmark_bytes_and_no_speedup_claim,
    }
    reports={}
    measured=None
    for name,fn in checks.items():
        try:
            r=fn()
            reports[name]=True
            if r is not None:measured=r
        except Exception:
            traceback.print_exc(file=sys.stderr)
            reports[name]=False
    ok=all(reports.values())
    result={'schema':'ttm.p06.independent.synthetic_cpu.qa.v1',
            'status':'PASS' if ok else 'FAIL',
            'checks':reports,'measurements':measured,
            'torch':torch.__version__, 'device':'cpu',
            'P01_TEST':'NOT_READ','P01_E0':'NOT_RERUN',
            'P03_TRAINING':'NOT_EXECUTED','P07_GPU':'NOT_OPENED',
            'no_external_corpus':True,'no_performance_claim':True}
    print(json.dumps(result,sort_keys=True))
    return 0 if ok else 1


if __name__=='__main__':
    raise SystemExit(main())
