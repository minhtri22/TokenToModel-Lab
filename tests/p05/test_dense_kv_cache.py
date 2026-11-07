"""P05 synthetic CPU unit QA; no corpus reads or optimizer steps."""
import sys
from pathlib import Path
import unittest
import torch

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT))
from src.p02.transformer_core import GPT, P02Config
from src.p05.dense_kv_cache import DenseKVCache, dense_forward_tokens, benchmark_dense_vs_recompute


class TestDenseKV(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        torch.set_num_threads(2)

    def setUp(self):
        torch.manual_seed(20261107)
        self.m = GPT(P02Config()).eval()

    def cache(self, **overrides):
        opts = dict(n_layers=2, max_seq_len=64, n_heads=4, head_dim=16, max_requests=2)
        opts.update(overrides)
        return DenseKVCache(**opts)

    def test_each_decode_logits_matches_uncached_p02(self):
        c = self.cache()
        c.start("a")
        seq = [0, 256, 1024, 2047, 48, 25, 1701, 7, 23, 2018, 3]
        for t, token in enumerate(seq, 1):
            got = dense_forward_tokens(self.m, [token], c, "a")
            with torch.no_grad():
                ref, _ = self.m(torch.tensor([seq[:t]], dtype=torch.long))
            torch.testing.assert_close(got, ref[0, -1], atol=2e-5, rtol=2e-5)
        self.assertEqual(c.lengths["a"], len(seq))
        c.release("a")

    def test_interleaved_request_isolation_and_release(self):
        c = self.cache()
        c.start("a")
        c.start("b")
        seqs = {"a": [1, 2, 256, 2047, 4], "b": [66, 1024, 900, 800]}
        for i in range(5):
            for rid in ("a", "b"):
                if i >= len(seqs[rid]):
                    continue
                actual = dense_forward_tokens(self.m, [seqs[rid][i]], c, rid)
                with torch.no_grad():
                    expected, _ = self.m(torch.tensor([seqs[rid][:i + 1]]))
                torch.testing.assert_close(actual, expected[0, -1], atol=2e-5, rtol=2e-5)
        self.assertEqual(c.stats()["active_requests"], 2)
        c.release("a")
        self.assertEqual(c.stats()["active_requests"], 1)
        c.release("b")
        self.assertEqual(c.stats()["allocated_bytes"], 0)
        c.start("c")
        got = dense_forward_tokens(self.m, [2047, 256], c, "c")
        with torch.no_grad():
            ref, _ = self.m(torch.tensor([[2047, 256]]))
        torch.testing.assert_close(got, ref[0, -1], atol=2e-5, rtol=2e-5)
        c.release("c")

    def test_bounded_capacity_and_oom_without_state_change(self):
        c = self.cache(max_seq_len=3, max_requests=1)
        c.start("x")
        with self.assertRaises(MemoryError):
            c.start("y")
        for _ in range(3):
            c.allocate_token("x")
        with self.assertRaises(MemoryError):
            c.allocate_token("x")
        self.assertEqual(c.lengths["x"], 3)
        c.release("x")
        self.assertEqual(c.stats()["active_requests"], 0)
        with self.assertRaises(ValueError):
            self.cache(max_allocated_bytes=1)

    def test_input_validation_rejects_before_cache_mutation(self):
        c = self.cache()
        c.start("r")
        for bad in ([], [2048], [-1], [1.0], [True]):
            with self.assertRaises(ValueError):
                dense_forward_tokens(self.m, bad, c, "r")
            self.assertEqual(c.lengths["r"], 0)
        with self.assertRaises(ValueError):
            c.start("r")
        with self.assertRaises(KeyError):
            dense_forward_tokens(self.m, [1], c, "missing")
        self.m.train()
        with self.assertRaises(ValueError):
            dense_forward_tokens(self.m, [1], c, "r")
        self.assertEqual(c.lengths["r"], 0)
        c.release("r")

    def test_layernorm_and_rmsnorm_mode_parity(self):
        for norm in ("layernorm", "rmsnorm"):
            torch.manual_seed(11)
            m = GPT(P02Config(norm_type=norm)).eval()
            cache = self.cache()
            cache.start(norm)
            seq = [2047, 17, 1024, 9]
            got = dense_forward_tokens(m, seq, cache, norm)
            with torch.no_grad():
                ref, _ = m(torch.tensor([seq]))
            torch.testing.assert_close(got, ref[0, -1], atol=2e-5, rtol=2e-5)
            cache.release(norm)

    def test_wall_time_and_kv_byte_measurement(self):
        seq = [0, 256, 2047, 17, 23, 9]
        metrics = benchmark_dense_vs_recompute(self.m, seq, repeats=2)
        self.assertEqual(metrics["sequence_length"], len(seq))
        self.assertEqual(metrics["repeats"], 2)
        self.assertGreater(metrics["allocated_kv_bytes"], metrics["logical_kv_bytes"])
        self.assertTrue(all(v > 0 for v in metrics["recompute_ms"] + metrics["dense_ms"]))


if __name__ == "__main__":
    unittest.main()
