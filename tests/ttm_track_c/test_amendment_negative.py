"""C-F01/02/03 adversarial acceptance and regression; stdlib only."""
import unittest
from synthetic_contract import (
    BOS, SYS, USER, ASSIST, EOT, EOS, IGNORE, PAD,
    serialize, shifted_padded_targets, build_sft_targets, audit_toy_records,
)

class AmendmentNegativeQA(unittest.TestCase):
    def _sample(self):
        return serialize([{"role": "user", "content": [77]},
                          {"role": "assistant", "content": [88]}], 12)

    def test_cf02_reject_forged_user_token_mask(self):
        ids, mask = self._sample()
        mask[2] = 1
        with self.assertRaisesRegex(ValueError, "mask provenance"):
            shifted_padded_targets(ids, mask, 12)

    def test_cf02_reject_forged_user_eot_mask(self):
        ids, mask = self._sample()
        mask[3] = 1
        with self.assertRaisesRegex(ValueError, "mask provenance"):
            shifted_padded_targets(ids, mask, 12)

    def test_cf02_reject_suppressed_assistant_target(self):
        ids, mask = self._sample()
        mask[5] = 0
        with self.assertRaisesRegex(ValueError, "mask provenance"):
            shifted_padded_targets(ids, mask, 12)

    def test_cf02_reject_forged_system_context(self):
        ids, mask = serialize([{"role": "system", "content": [44]},
            {"role": "user", "content": [77]}, {"role": "assistant", "content": [88]}], 16)
        mask[2] = 1
        with self.assertRaisesRegex(ValueError, "mask provenance"):
            shifted_padded_targets(ids, mask, 16)

    def test_cf02_reject_malformed_serialized_ids(self):
        ids, mask = self._sample()
        for bad in ([BOS, *ids[1:-1]], [BOS, ASSIST, *ids[2:]],
                    [BOS, USER, PAD, *ids[3:]], [BOS, USER, *ids[2:-1], EOT, EOS]):
            with self.subTest(bad=bad), self.assertRaises(ValueError):
                shifted_padded_targets(bad, mask[:len(bad)], 16)

    def test_cf02_reject_bool_flags_and_bool_max_len(self):
        ids, mask = self._sample()
        mask[2] = False
        with self.assertRaises(ValueError):
            shifted_padded_targets(ids, mask, 12)
        with self.assertRaises(ValueError):
            shifted_padded_targets(ids, [0, 0, 0, 0, 0, 1, 1, 1], True)

    def test_cf02_b_facing_wrapper_matches_valid_legacy(self):
        m = [{"role": "user", "content": [77]}, {"role": "assistant", "content": [88]}]
        ids, mask = serialize(m, 16)
        self.assertEqual(build_sft_targets(m, 16), shifted_padded_targets(ids, mask, 16))
        with self.assertRaises(ValueError):
            build_sft_targets([{"role": "user", "content": [77]}], 16)

    def test_cf01_zero_direct_prompt_ce_not_zero_context_gradient(self):
        m = [{"role": "system", "content": [19]}, {"role": "user", "content": [77]},
             {"role": "assistant", "content": [88]}]
        ids, _ = serialize(m, 16)
        _, y = build_sft_targets(m, 16)
        for i, label in enumerate(ids[1:]):
            if label in (19, 77, SYS, USER, ASSIST) or (label == EOT and i < 7):
                self.assertEqual(y[i], IGNORE)  # zero DIRECT target CE weight
        self.assertIn(88, y)
        self.assertEqual(y.count(EOS), 1)
        # Scalar chain-rule demonstration, not a neural-network run:
        # L=1/2*(p+a-target)^2 uses only the assistant target.
        prompt_feature, answer_feature, target = 2.0, 1.0, 0.0
        dL_dprompt = prompt_feature + answer_feature - target
        self.assertNotEqual(dL_dprompt, 0.0)  # context gradient IS allowed

    def test_cf03_unicode_canonical_equivalence(self):
        rows = [{"id": "nfc", "split": "train", "text": "é"},
                {"id": "nfd", "split": "val", "text": "e\u0301"}]
        summary = audit_toy_records(rows)
        self.assertEqual(summary["cross_split_exact_groups"], 0)
        self.assertEqual(summary["cross_split_normalized_groups"], 1)

    def test_randomized_role_boundaries(self):
        import random
        rng = random.Random(20261116)
        for _ in range(1000):
            messages = []
            if rng.randrange(2):
                messages.append({"role": "system", "content": [rng.randrange(100, 150)]})
            for _ in range(rng.randrange(1, 5)):
                messages.append({"role": "user", "content": [rng.randrange(150, 300)]})
                messages.append({"role": "assistant", "content": [rng.randrange(300, 450)]})
            ids, flags = serialize(messages, 100)
            x, y = shifted_padded_targets(ids, flags, 100)
            self.assertEqual((x, y), build_sft_targets(messages, 100))
            self.assertEqual(y.count(EOS), 1)
            self.assertEqual(y.count(EOT), len(messages)//2 if messages[0]["role"] != "system" else (len(messages)-1)//2)
            prompt_ix = [i for i,t in enumerate(ids) if t >= 7 and any(t in m["content"] and m["role"] != "assistant" for m in messages)]
            self.assertTrue(all(y[i-1] == IGNORE for i in prompt_ix if i > 0))

if __name__ == "__main__":
    unittest.main()
