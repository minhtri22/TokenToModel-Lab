"""Synthetic P04 functional QA: no P01 corpus access, no model-quality claims."""
import hashlib
from pathlib import Path
import sys
from tempfile import TemporaryDirectory
import unittest

import torch

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT))
from src.p02.transformer_core import GPT, P02Config
from src.p04.eval_checkpoints import (save_checkpoint_new, load_checkpoint_verified,
                                      generate_tokens, evaluate_synthetic_heldout)

BPE_SHA = "53aabcb8ac3a3c16c7cbd915b76eb82653a334c98381fad95a05eba0a9353f60"


class P04Tests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        torch.set_num_threads(2)

    def setUp(self):
        torch.manual_seed(44)
        self.model = GPT(P02Config()).eval()

    def test_checkpoint_weights_only_strict_roundtrip(self):
        with TemporaryDirectory() as folder:
            path = Path(folder) / "model.pt"
            sha = save_checkpoint_new(path, self.model, BPE_SHA)
            self.assertEqual(sha, hashlib.sha256(path.read_bytes()).hexdigest())
            restored = load_checkpoint_verified(path, sha, BPE_SHA)
            inputs = torch.tensor([[0, 256, 2047, 5]])
            a, _ = self.model(inputs)
            b, _ = restored(inputs)
            torch.testing.assert_close(a, b, atol=0, rtol=0)
            with self.assertRaises(FileExistsError):
                save_checkpoint_new(path, self.model, BPE_SHA)

    def test_tamper_checkpoint_rejected(self):
        with TemporaryDirectory() as folder:
            path = Path(folder) / "model.pt"
            sha = save_checkpoint_new(path, self.model, BPE_SHA)
            with self.assertRaises(ValueError):
                load_checkpoint_verified(path, sha, "0"*64)
            with path.open("ab") as out:
                out.write(b"tamper")
            with self.assertRaisesRegex(ValueError, "CHECKPOINT_SHA256_MISMATCH"):
                load_checkpoint_verified(path, sha, BPE_SHA)

    def test_sampling_is_deterministic_and_greedy(self):
        prefix = [0, 256, 2047]
        a = generate_tokens(self.model, prefix, 3, top_k=1, seed=777)
        b = generate_tokens(self.model, prefix, 3, top_k=1, seed=3)
        self.assertEqual(a, b)
        self.assertEqual(a[:3], prefix)
        self.assertTrue(all(0 <= i < 2048 for i in a))
        with torch.inference_mode():
            logits, _ = self.model(torch.tensor([prefix]))
        self.assertEqual(a[3], int(logits[0, -1].argmax().item()))

    def test_seeded_stochastic_generation(self):
        prefix = [5, 2047]
        a = generate_tokens(self.model, prefix, 4, top_k=32, seed=77)
        b = generate_tokens(self.model, prefix, 4, top_k=32, seed=77)
        self.assertEqual(a, b)

    def test_sealed_split_and_nonmutation(self):
        before = [p.detach().clone() for p in self.model.parameters()]
        heldout = [([1800, 1801, 1802], [1801, 1802, 1803]), ([2001, 2002], [2002, 2003])]
        r = evaluate_synthetic_heldout(self.model, heldout)
        self.assertEqual(r["token_count"], 5)
        self.assertEqual(r["split"], "SYNTHETIC_HELDOUT")
        self.assertGreater(r["perplexity"], 0)
        self.assertFalse(r["training_performed"])
        for p, x in zip(self.model.parameters(), before):
            torch.testing.assert_close(p, x, atol=0, rtol=0)
        with self.assertRaises(ValueError):
            evaluate_synthetic_heldout(self.model, heldout, split="WP30_TEST")

    def test_invalid_parameters_fail_closed(self):
        for prefix,n in [([],1),([2048],1),([0],65),([-1],1)]:
            with self.assertRaises(ValueError):
                generate_tokens(self.model, prefix, n)
        with self.assertRaises(ValueError):
            generate_tokens(self.model, [0], 1, temperature=float("nan"))
        with self.assertRaises(ValueError):
            generate_tokens(self.model, [0], 1, top_k=0)
        with self.assertRaises(ValueError):
            save_checkpoint_new(Path("unused.pt"), self.model, "bad sha")
        with self.assertRaises(ValueError):
            evaluate_synthetic_heldout(self.model, [([2048], [1])])


if __name__ == "__main__":
    unittest.main()
