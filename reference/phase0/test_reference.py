import unittest
import torch
from model import GPT, GPTConfig
from paged_kv import PagedKVCache


class GPTPagedTests(unittest.TestCase):
    def setUp(self):
        torch.manual_seed(123)
        self.cfg = GPTConfig(n_layer=2, n_head=4, n_embd=64, max_seq_len=64)
        self.model = GPT(self.cfg).eval()
        self.cache = PagedKVCache(n_layers=2, n_blocks=20, block_size=4,
                                  n_heads=4, head_dim=16)

    def test_trainable_loss_backward(self):
        self.model.train()
        x = torch.randint(0, 256, (2, 8))
        logits, loss = self.model(x, x)
        self.assertEqual(tuple(logits.shape), (2, 8, 256))
        self.assertTrue(torch.isfinite(loss))
        loss.backward()
        self.assertIsNotNone(self.model.tok.weight.grad)

    def test_causality(self):
        a = torch.tensor([[1, 2, 3, 4, 5]])
        b = torch.tensor([[1, 2, 3, 99, 100]])
        with torch.no_grad():
            outa, _ = self.model(a)
            outb, _ = self.model(b)
        torch.testing.assert_close(outa[:, :3], outb[:, :3], atol=1e-5, rtol=1e-5)

    def test_all_decode_positions_match_dense(self):
        self.cache.start("a")
        seq = [11, 7, 8, 5, 2, 13, 17, 20, 22, 4, 1, 0, 9]
        with torch.no_grad():
            for i, token in enumerate(seq):
                got = self.model.paged_forward_tokens([token], self.cache, "a")
                expected, _ = self.model(torch.tensor([seq[:i + 1]]))
                torch.testing.assert_close(got, expected[0, -1], atol=2e-5, rtol=2e-5)
        self.assertEqual(len(self.cache.tables["a"]), 4)

    def test_interleaved_requests(self):
        self.cache.start("a")
        self.cache.start("b")
        seqs = {"a": [4, 6, 9, 1, 2, 3], "b": [10, 2, 3, 3, 9]}
        with torch.no_grad():
            for i in range(6):
                for rid in ("a", "b"):
                    if i >= len(seqs[rid]):
                        continue
                    got = self.model.paged_forward_tokens([seqs[rid][i]], self.cache, rid)
                    expected, _ = self.model(torch.tensor([seqs[rid][:i + 1]]))
                    torch.testing.assert_close(got, expected[0, -1], atol=2e-5, rtol=2e-5)
        a_blocks = set(self.cache.tables["a"])
        b_blocks = set(self.cache.tables["b"])
        self.assertFalse(a_blocks.intersection(b_blocks))
        self.cache.release("a")
        self.cache.release("b")
        self.assertEqual(self.cache.stats()["used_blocks"], 0)

    def test_oom_and_reuse(self):
        tiny = PagedKVCache(n_layers=1, n_blocks=1, block_size=2,
                            n_heads=1, head_dim=2)
        tiny.start("one")
        tiny.allocate_token("one")
        tiny.allocate_token("one")
        with self.assertRaises(MemoryError):
            tiny.allocate_token("one")
        self.assertEqual(tiny.lengths["one"], 2)
        tiny.release("one")
        tiny.start("two")
        tiny.allocate_token("two")
        self.assertEqual(tiny.stats()["used_blocks"], 1)


if __name__ == "__main__":
    unittest.main()
