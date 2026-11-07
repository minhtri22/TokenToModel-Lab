"""P03 synthetic CPU correctness QA, no external corpus or held-out TEST."""
import unittest
import torch
from src.p02.transformer_core import GPT, P02Config
from src.p03.train_loop import TrainConfig, scheduled_lr, train_fixed_batch

class P03TrainLoopTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        torch.set_num_threads(2)

    def make_model(self, seed=20261107):
        torch.manual_seed(seed)
        return GPT(P02Config())

    def setUp(self):
        self.x = torch.tensor([[10, 256, 2047, 12, 512, 1],
                               [10, 256, 2047, 12, 512, 1]], dtype=torch.long)
        self.y = torch.tensor([[256, 2047, 12, 512, 1, 13],
                               [256, 2047, 12, 512, 1, 13]], dtype=torch.long)

    def test_microbatch_overfit(self):
        model = self.make_model()
        result = train_fixed_batch(model, self.x, self.y, TrainConfig(steps=90))
        self.assertEqual(result['steps'], 90)
        self.assertLess(result['final_loss'], 0.15)
        self.assertLess(result['final_loss'], result['initial_loss'] * 0.1)

    def test_deterministic_two_runs(self):
        cfg = TrainConfig(steps=5)
        one = train_fixed_batch(self.make_model(), self.x, self.y, cfg)
        two = train_fixed_batch(self.make_model(), self.x, self.y, cfg)
        self.assertAlmostEqual(one['final_loss'], two['final_loss'], places=7)
        self.assertEqual(one['initial_loss'], two['initial_loss'])

    def test_gradient_accumulation_parity(self):
        torch.manual_seed(20261108)
        base = self.make_model()
        split = self.make_model()
        split.load_state_dict(base.state_dict())
        a = train_fixed_batch(base, self.x, self.y, TrainConfig(steps=1, warmup_steps=0, accumulation_steps=1))
        b = train_fixed_batch(split, self.x, self.y, TrainConfig(steps=1, warmup_steps=0, accumulation_steps=2))
        self.assertAlmostEqual(a['final_loss'], b['final_loss'], places=5)
        for (name, p), (_, q) in zip(base.named_parameters(), split.named_parameters()):
            torch.testing.assert_close(p, q, atol=1e-5, rtol=1e-5)

    def test_scheduler_bounds(self):
        cfg = TrainConfig(steps=20, warmup_steps=4, peak_lr=.003, min_lr_ratio=.2)
        lrs = [scheduled_lr(i, cfg) for i in range(cfg.steps)]
        self.assertAlmostEqual(lrs[3], cfg.peak_lr)
        self.assertAlmostEqual(lrs[-1], cfg.peak_lr*.2)
        self.assertTrue(all(0 < x <= cfg.peak_lr for x in lrs))

    def test_invalid_inputs_rejected_without_weight_changes(self):
        model = self.make_model()
        before = model.tok.weight.detach().clone()
        cfg = TrainConfig(steps=1, warmup_steps=0)
        with self.assertRaises(ValueError):
            train_fixed_batch(model, self.x, torch.full_like(self.y, 2048), cfg)
        with self.assertRaises(ValueError):
            train_fixed_batch(model, self.x, self.y, TrainConfig(steps=1, warmup_steps=0, accumulation_steps=3))
        with self.assertRaises(ValueError):
            train_fixed_batch(model, self.x.float(), self.y, cfg)
        torch.testing.assert_close(model.tok.weight, before, atol=0, rtol=0)

    def test_invalid_configs(self):
        for kwargs in (dict(steps=0), dict(peak_lr=float('nan')), dict(accumulation_steps=0),
                       dict(warmup_steps=6, steps=5), dict(min_lr_ratio=0)):
            with self.assertRaises(ValueError):
                TrainConfig(**kwargs)
        with self.assertRaises(ValueError):
            scheduled_lr(20, TrainConfig(steps=20))

if __name__ == '__main__':
    unittest.main()
