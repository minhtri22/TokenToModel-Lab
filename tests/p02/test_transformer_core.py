"""P02 deterministic synthetic QA; never accesses Wikipedia/held-out TEST."""
import importlib.util
from pathlib import Path
import sys
import unittest

import torch

REPO = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(REPO / 'src' / 'p02'))
from transformer_core import GPT, P02Config


class P02CoreTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        torch.set_num_threads(2)

    def setUp(self):
        torch.manual_seed(20261107)
        self.cfg = P02Config()
        self.model = GPT(self.cfg).eval()

    def test_bpe2048_shape_and_tied_head(self):
        tokens = torch.randint(0, 2048, (2, 9), dtype=torch.long)
        logits, loss = self.model(tokens)
        self.assertEqual(tuple(logits.shape), (2, 9, 2048))
        self.assertIsNone(loss)
        self.assertEqual(self.model.head.weight.data_ptr(), self.model.tok.weight.data_ptr())
        self.assertTrue(torch.isfinite(logits).all().item())

    def test_finite_gradients_with_high_bpe_token_ids(self):
        self.model.train()
        x = torch.tensor([[0, 256, 1024, 2047, 55], [2047, 700, 5, 0, 1024]])
        y = x.roll(-1, dims=1)
        _, loss = self.model(x, y)
        self.assertTrue(torch.isfinite(loss).item())
        loss.backward()
        for key in ('tok.weight', 'pos.weight', 'blocks.0.attn.qkv.weight', 'blocks.0.mlp.0.weight'):
            p = dict(self.model.named_parameters())[key]
            self.assertIsNotNone(p.grad, key)
            self.assertTrue(torch.isfinite(p.grad).all().item(), key)
            self.assertGreater(float(p.grad.abs().sum()), 0, key)

    def test_future_token_cannot_change_prefix_logits(self):
        a = torch.tensor([[5, 256, 1090, 2047, 7, 8, 9]])
        b = torch.tensor([[5, 256, 1090, 1024, 1900, 21, 33]])
        with torch.no_grad():
            y_a, _ = self.model(a)
            y_b, _ = self.model(b)
        torch.testing.assert_close(y_a[:, :3], y_b[:, :3], atol=1e-6, rtol=1e-6)

    def test_exact_reference_p00_layernorm_parity(self):
        refdir = REPO / 'reference' / 'phase0'
        sys.path.insert(0, str(refdir))
        try:
            spec = importlib.util.spec_from_file_location('ttm_p00_ref_model_p02qa', refdir / 'model.py')
            mod = importlib.util.module_from_spec(spec)
            spec.loader.exec_module(mod)
            ref = mod.GPT(mod.GPTConfig(vocab_size=2048, max_seq_len=64,
                                        n_embd=64, n_layer=2, n_head=4)).eval()
            self.model.load_state_dict(ref.state_dict(), strict=True)
            x = torch.tensor([[0, 256, 2047, 1024, 5, 700]])
            target = x.roll(-1, dims=1)
            got, loss_got = self.model(x, target)
            want, loss_want = ref(x, target)
            torch.testing.assert_close(got, want, atol=1e-6, rtol=1e-6)
            torch.testing.assert_close(loss_got, loss_want, atol=1e-7, rtol=1e-7)
            loss_got.backward()
            loss_want.backward()
            for name in ('tok.weight', 'blocks.0.attn.qkv.weight', 'blocks.1.mlp.2.weight'):
                torch.testing.assert_close(dict(self.model.named_parameters())[name].grad,
                                           dict(ref.named_parameters())[name].grad,
                                           atol=1e-6, rtol=1e-6)
        finally:
            sys.path.remove(str(refdir))

    def test_rmsnorm_mode_finite_shape_and_backward(self):
        m = GPT(P02Config(norm_type='rmsnorm'))
        x = torch.tensor([[0, 256, 2047, 17]])
        logits, loss = m(x, x)
        self.assertEqual(tuple(logits.shape), (1, 4, 2048))
        self.assertTrue(torch.isfinite(loss).item())
        loss.backward()
        self.assertTrue(torch.isfinite(m.blocks[0].ln1.weight.grad).all().item())

    def test_invalid_inputs_and_configs_fail_closed(self):
        with self.assertRaises(ValueError):
            P02Config(n_head=3)
        with self.assertRaises(ValueError):
            P02Config(norm_type='unknown')
        for bad in (torch.tensor([[2048]]), torch.tensor([[-1]]),
                    torch.empty((1, 0), dtype=torch.long), torch.zeros((1, 65), dtype=torch.long),
                    torch.zeros((1, 1), dtype=torch.float32)):
            with self.assertRaises(ValueError):
                self.model(bad)
        with self.assertRaises(ValueError):
            self.model(torch.tensor([[1, 2]]), torch.tensor([[1]]))


if __name__ == '__main__':
    unittest.main()
