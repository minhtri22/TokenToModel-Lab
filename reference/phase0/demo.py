"""Deterministic dense-vs-paged comparison and sample greedy decode."""
import torch
from model import GPT, GPTConfig
from paged_kv import PagedKVCache


def main():
    torch.manual_seed(11)
    cfg = GPTConfig(n_layer=2, n_embd=64, n_head=4, max_seq_len=64)
    model = GPT(cfg).eval()
    prompt = list(b"Hello, paged attention!")
    cache = PagedKVCache(n_layers=cfg.n_layer, n_blocks=12, block_size=4,
                         n_heads=cfg.n_head, head_dim=cfg.n_embd // cfg.n_head)
    cache.start("demo")
    with torch.no_grad():
        paged_logits = model.paged_forward_tokens(prompt, cache, "demo")
        dense_logits = model(torch.tensor([prompt]))[0][0, -1]
        diff = (paged_logits - dense_logits).abs().max().item()
        assert torch.allclose(paged_logits, dense_logits, atol=2e-5, rtol=2e-5)
        print(f"DENSE_VS_PAGED=PASS max_abs_diff={diff:.3g}")
        generated = []
        for _ in range(8):
            next_tok = int(paged_logits.argmax())
            generated.append(next_tok)
            paged_logits = model.paged_forward_tokens([next_tok], cache, "demo")
    print("INPUT:", bytes(prompt).decode("utf-8"))
    print("OUTPUT BYTES:", bytes(generated))
    print("BLOCK_TABLE:", cache.tables["demo"])
    print("CACHE_STATS:", cache.stats())
    cache.release("demo")
    assert cache.stats()["used_blocks"] == 0
    print("RELEASE=PASS")
    print("NOTE: weights are random, output is not meaningful language")


if __name__ == "__main__":
    main()
