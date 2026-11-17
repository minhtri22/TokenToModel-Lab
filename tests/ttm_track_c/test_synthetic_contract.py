"""Known-answer controls for Track-C; unittest (stdlib), no model/science."""
import unittest
from synthetic_contract import (
    BOS, SYS, USER, ASSIST, EOT, EOS, IGNORE, PAD,
    serialize, shifted_padded_targets, score_slot, floor_state, audit_toy_records,
)

class ContractQA(unittest.TestCase):
    def test_one_turn_excludes_prompt_and_headers(self):
        ids, flags = serialize([{"role": "user", "content": [10, 11]},
                                {"role": "assistant", "content": [12, 13]}], 16)
        self.assertEqual(ids, [BOS, USER, 10, 11, EOT, ASSIST, 12, 13, EOT, EOS])
        self.assertEqual(flags, [0, 0, 0, 0, 0, 0, 1, 1, 1, 1])
        x, y = shifted_padded_targets(ids, flags, 16)
        self.assertEqual(x[:9], ids[:9])
        self.assertEqual(y[:9], [IGNORE]*5 + [12, 13, EOT, EOS])
        self.assertTrue(all(v == IGNORE for v in y[9:]))
        self.assertEqual(x[-1], PAD)

    def test_system_context_is_not_supervised(self):
        ids, flags = serialize([{"role":"system", "content":[20]},
            {"role":"user", "content":[21]}, {"role":"assistant", "content":[22]}], 16)
        x, y = shifted_padded_targets(ids, flags, 16)
        self.assertNotIn(20, y)
        self.assertNotIn(21, y)
        self.assertIn(22, y)

    def test_multiturn_termination_supervised_twice(self):
        dialogue = [{"role":"user", "content":[10]},
            {"role":"assistant", "content":[11]},
            {"role":"user", "content":[12]},
            {"role":"assistant", "content":[13]}]
        ids, flags = serialize(dialogue, 16)
        _, y = shifted_padded_targets(ids, flags, 16)
        self.assertEqual(y.count(EOT), 2)
        self.assertEqual(y.count(EOS), 1)
        self.assertNotIn(10, y)
        self.assertNotIn(12, y)

    def test_padding_no_leakage(self):
        ids, flags = serialize([{"role":"user","content":[11]},
            {"role":"assistant","content":[12]}], 25)
        _, y = shifted_padded_targets(ids, flags, 25)
        self.assertEqual(y.count(PAD), 0)
        self.assertEqual(y[-1], IGNORE)

    def test_reject_truncated_dialogue(self):
        with self.assertRaises(ValueError):
            serialize([{"role":"user","content":[7,8,9]},
                {"role":"assistant","content":[10]}], 5)

    def test_reject_nonassistant_final(self):
        with self.assertRaises(ValueError):
            serialize([{"role":"user","content":[7]}], 12)

    def test_reject_reordered_roles(self):
        with self.assertRaises(ValueError):
            serialize([{"role":"assistant","content":[7]}], 12)

    def test_reject_reserved_ids(self):
        with self.assertRaises(ValueError):
            serialize([{"role":"user","content":[USER]},
                {"role":"assistant","content":[7]}], 12)

    def test_reject_empty_completion(self):
        with self.assertRaises(ValueError):
            serialize([{"role":"user","content":[7]},
                {"role":"assistant","content":[]}], 12)

    def test_fluent_wrong_slot_does_not_pass(self):
        self.assertEqual(score_slot("lam", "lam"), 1)
        self.assertEqual(score_slot("lam", "minh"), 0)
        self.assertIsNone(score_slot(None, "lam"))

    def test_floor_and_ceiling_detected(self):
        self.assertEqual(floor_state([0,0,0]), "FLOOR_HOLD")
        self.assertEqual(floor_state([1,1,1]), "CEILING_HOLD")
        self.assertEqual(floor_state([0,1]), "SEPARATING_TOY_CONTROLS_ONLY")

    def test_toy_cross_split_exact_and_normalized(self):
        rows=[{"id":"a","split":"train","text":"Ngôi nhà X"},
              {"id":"b","split":"val","text":"Ngôi nhà X"},
              {"id":"c","split":"test","text":"  ngôi   nhà x  "}]
        report=audit_toy_records(rows)
        self.assertEqual(report["record_count"], 3)
        self.assertEqual(report["cross_split_exact_groups"], 1)
        self.assertEqual(report["cross_split_normalized_groups"], 1)
        self.assertEqual(report["token_histogram"], "NOT_AVAILABLE_NO_REAL_TOKENIZER")
        self.assertEqual(len(report["manifest_sha256"]),64)

    def test_reject_duplicate_ids(self):
        row={"id":"a", "split":"train", "text":"fake"}
        with self.assertRaises(ValueError):
            audit_toy_records([row,row])

    def test_reject_all_ignore_labels(self):
        with self.assertRaises(ValueError):
            shifted_padded_targets([BOS, USER], [0,0], 4)

if __name__ == "__main__":
    unittest.main()
