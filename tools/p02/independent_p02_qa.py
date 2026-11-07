"""TTM P02 independent CPU checker: synthetic token IDs, no corpus access.

Compares causal Attention to PyTorch's SDPA, and P02 whole-model
logits/gradients to the frozen P00 reference under identical dimensions.
No optimizer steps, model checkpoint or P03/P04 run.
"""
from __future__ import annotations

import importlib.util
import json
from pathlib import Path
import sys
import traceback

import torch
from torch.nn import functional as F

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / 'src' / 'p02'))
sys.path.insert(0, str(ROOT / 'reference' / 'phase0'))
from transformer_core import GPT, P02Config  # noqa: E402


def check_attention_vs_sdpa() -> None:
    torch.manual_seed(6601)
    m = GPT(P02Config()).eval()
    attn = m.blocks[0].attn
    x = torch.randn(2, 7, 64)
    b, t, e = x.shape
    h = attn.heads
    d = attn.head_dim
    q, k, v = attn.qkv(x).reshape(b, t, 3, h, d).permute(2, 0, 3, 1, 4).unbind(0)
    expected = F.scaled_dot_product_attention(q, k, v, is_causal=True, dropout_p=0.0)
    expected = attn.proj(expected.transpose(1, 2).contiguous().reshape(b, t, e))
    actual = attn(x)
    torch.testing.assert_close(actual, expected, atol=2e-5, rtol=2e-5)


def check_end_to_end_p00_parity() -> None:
    torch.manual_seed(6602)
    cfg = P02Config()
    model = GPT(cfg).train()
    spec = importlib.util.spec_from_file_location('ttm_p00_independent_ref', ROOT / 'reference' / 'phase0' / 'model.py')
    if spec is None or spec.loader is None:
        raise RuntimeError('P00_REFERENCE_NOT_FOUND')
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    reference = mod.GPT(mod.GPTConfig(vocab_size=2048, max_seq_len=64, n_embd=64, n_layer=2, n_head=4)).train()
    reference.load_state_dict(model.state_dict(), strict=True)
    ids = torch.tensor([[0, 2047, 256, 87, 1048], [1535, 1, 1900, 44, 2046]], dtype=torch.long)
    target = ids.roll(-1, dims=1)
    a, la = model(ids, target)
    b, lb = reference(ids, target)
    torch.testing.assert_close(a, b, atol=1e-6, rtol=1e-6)
    torch.testing.assert_close(la, lb, atol=1e-6, rtol=1e-6)
    la.backward()
    lb.backward()
    for key in ('tok.weight', 'blocks.0.attn.qkv.weight', 'blocks.1.mlp.2.weight'):
        torch.testing.assert_close(dict(model.named_parameters())[key].grad,
                                   dict(reference.named_parameters())[key].grad,
                                   atol=1e-6, rtol=1e-6)


def check_causality_cross_batch() -> None:
    torch.manual_seed(6603)
    model = GPT(P02Config()).eval()
    a = torch.tensor([[2047, 256, 10, 1, 2], [777, 8, 900, 3, 4]])
    b = torch.tensor([[2047, 256, 10, 2000, 1999], [777, 8, 900, 1024, 2046]])
    with torch.no_grad():
        aa, _ = model(a)
        bb, _ = model(b)
    torch.testing.assert_close(aa[:, :3], bb[:, :3], atol=1e-6, rtol=1e-6)


def check_shapes_tie_and_boundaries() -> None:
    torch.manual_seed(6604)
    model = GPT(P02Config()).eval()
    if sum(p.numel() for p in model.parameters()) != 235264:
        raise AssertionError('INDEPENDENT_PARAMETER_COUNT_MISMATCH')
    if model.tok.weight.data_ptr() != model.head.weight.data_ptr():
        raise AssertionError('TIED_EMBEDDING_MISMATCH')
    tokens = torch.tensor([[0, 256, 1024, 2047]], dtype=torch.long)
    logits, loss = model(tokens)
    if tuple(logits.shape) != (1, 4, 2048) or loss is not None:
        raise AssertionError('OUTPUT_SHAPE_MISMATCH')
    for bad in (torch.tensor([[2048]]), torch.tensor([[-1]]), torch.zeros((1, 65), dtype=torch.long)):
        try:
            model(bad)
        except ValueError:
            continue
        raise AssertionError('INVALID_INPUT_NOT_REJECTED')


def main() -> int:
    torch.set_num_threads(2)
    checks = {
        'sdpa_attention_oracle': check_attention_vs_sdpa,
        'p00_logits_loss_gradient_parity': check_end_to_end_p00_parity,
        'cross_batch_future_token_isolation': check_causality_cross_batch,
        'shape_tied_weights_boundary_rejection': check_shapes_tie_and_boundaries,
    }
    results = {}
    for name, fn in checks.items():
        try:
            fn()
            results[name] = 'PASS'
        except Exception as exc:
            results[name] = 'FAIL: ' + repr(exc)
            traceback.print_exc(file=sys.stderr)
    verdict = 'PASS' if all(v == 'PASS' for v in results.values()) else 'FAIL'
    print(json.dumps({'schema': 'ttm.p02.independent.synthetic.qa.v1',
                      'status': verdict, 'device': 'cpu',
                      'torch': torch.__version__,
                      'tests': results, 'no_corpus_access': True,
                      'P03': 'NOT_EXECUTED'}, sort_keys=True))
    return 0 if verdict == 'PASS' else 1


if __name__ == '__main__':
    raise SystemExit(main())
