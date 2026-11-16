"""Reviewer-introduced acceptance checks; failures identify missing contract guards, not model results."""
import unittest
from synthetic_contract import serialize, shifted_padded_targets, audit_toy_records

class ReviewerRedChecks(unittest.TestCase):
    def test_reject_forged_user_supervision(self):
        ids, flags = serialize([{"role":"user","content":[77]}, {"role":"assistant","content":[88]}], 12)
        flags[2] = 1   # mutate user target mask at a known user-token index
        with self.assertRaises(ValueError):
            shifted_padded_targets(ids, flags, 12)

    def test_cross_split_unicode_canonical_forms_alert(self):
        rows = [{"id":"a","split":"train","text":"é"},
                {"id":"b","split":"val","text":"e\u0301"}]
        report = audit_toy_records(rows)
        self.assertEqual(report["cross_split_normalized_groups"], 1)

if __name__ == '__main__':
    unittest.main()
