"""Targeted G0-B03 QA only, using NON-R8 synthetic in-memory fixtures.

These same-agent tests do not attest a real G2 key, future caller, or R8 run.
"""
import unittest
from copy import deepcopy
from unittest.mock import patch
import folds_raters as f
import r8_production_caller as production
from test_g0_final_three_findings import production_blueprints,production_cases

FIXTURE_KEY=b"NON_SECRET_SYNTHETIC_32_BYTE_HMAC_FIXTURE_KEY"
OTHER_KEY=b"ANOTHER_FAKE_NON_SECRET_32_BYTE_TEST_KEY"

class B03FinalNegativeQA(unittest.TestCase):
    def setUp(self):
        self.bp=production_blueprints()
        self.cases=production_cases(self.bp)

    def test_closed_f01_f08_enum_rejects_unregistered_balanced_names(self):
        for row in self.bp:
            row["relation_family"]="UNREGISTERED_"+row["relation_family"]
        with self.assertRaisesRegex(ValueError,"INVALID_R8_FAMILY_ENUM"):
            f.validate_r8_blueprint_manifest(self.bp)

    def test_closed_family_enum_rejects_case_spelling(self):
        self.bp[0]["relation_family"]="f01"
        with self.assertRaisesRegex(ValueError,"INVALID_R8_FAMILY_ENUM"):
            f.validate_r8_blueprint_manifest(self.bp)

    def test_closed_family_balance_enforced(self):
        self.bp[0]["relation_family"]="F02"
        with self.assertRaisesRegex(ValueError,"INVALID_R8_FAMILY_BALANCE"):
            f.validate_r8_blueprint_manifest(self.bp)

    def test_unsourced_fold_dict_fails_even_with_valid_fields(self):
        forged={"fold":{x["blueprint_id"]:i%4 for i,x in enumerate(self.bp)},
                "cv_status":"PREFOLD_READY_NOT_VALIDATED"}
        with self.assertRaisesRegex(ValueError,"INVALID_R8_PREASSIGNMENT_SCHEMA"):
            f.postcheck_r8(self.cases,self.bp,forged,FIXTURE_KEY)

    def test_false_status_with_copied_hmac_rejected(self):
        assigned=f.preassign_r8(self.bp,FIXTURE_KEY)
        bad=deepcopy(assigned);bad["cv_status"]="PREFOLD_READY_NOT_VALIDATED_fake"
        with self.assertRaisesRegex(ValueError,"INVALID_R8_PREASSIGNMENT_MISMATCH_CV_STATUS"):
            f.postcheck_r8(self.cases,self.bp,bad,FIXTURE_KEY)

    def test_tampered_fold_with_copied_hmac_rejected(self):
        assigned=f.preassign_r8(self.bp,FIXTURE_KEY)
        bad=deepcopy(assigned);first=next(iter(bad["fold"]))
        bad["fold"][first]=(bad["fold"][first]+1)%4
        with self.assertRaisesRegex(ValueError,"INVALID_R8_PREASSIGNMENT_MISMATCH_FOLD"):
            f.postcheck_r8(self.cases,self.bp,bad,FIXTURE_KEY)

    def test_fake_mac_rejected(self):
        assigned=f.preassign_r8(self.bp,FIXTURE_KEY)
        bad=deepcopy(assigned);bad["preassignment_hmac"]="0"*64
        with self.assertRaisesRegex(ValueError,"INVALID_R8_HMAC_PROVENANCE_PREASSIGNMENT_HMAC"):
            f.postcheck_r8(self.cases,self.bp,bad,FIXTURE_KEY)

    def test_wrong_key_rejected(self):
        assigned=f.preassign_r8(self.bp,FIXTURE_KEY)
        with self.assertRaisesRegex(ValueError,"INVALID_R8_HMAC_PROVENANCE_BLUEPRINT_HMAC"):
            f.postcheck_r8(self.cases,self.bp,assigned,OTHER_KEY)

    def test_blueprint_mutation_invalidates_commitment(self):
        assigned=f.preassign_r8(self.bp,FIXTURE_KEY)
        changed=deepcopy(self.bp);changed[0]["event_graph_id"]="changed_event_graph"
        with self.assertRaisesRegex(ValueError,"INVALID_R8_HMAC_PROVENANCE_BLUEPRINT_HMAC"):
            f.postcheck_r8(self.cases,changed,assigned,FIXTURE_KEY)

    def test_private_key_must_have_32_bytes(self):
        with self.assertRaisesRegex(ValueError,"INVALID_R8_PRIVATE_HMAC_KEY"):
            f.preassign_r8(self.bp,b"weak")

    def test_valid_canonical_preassignment_is_order_independent(self):
        original=f.preassign_r8(self.bp,FIXTURE_KEY)
        reversed_bp=list(reversed(self.bp))
        again=f.preassign_r8(reversed_bp,FIXTURE_KEY)
        self.assertEqual(original["blueprint_hmac"],again["blueprint_hmac"])
        self.assertEqual(original["preassignment_hmac"],again["preassignment_hmac"])

    def test_actual_caller_uses_strict_gateways(self):
        with patch.object(f,"preassign_r8",wraps=f.preassign_r8) as pre:
            assigned=production.precommit_before_G3(self.bp,FIXTURE_KEY)
            self.assertEqual(pre.call_count,1)
        with patch.object(f,"postcheck_r8",wraps=f.postcheck_r8) as post:
            checked=production.verify_after_G3_before_CV(
                self.cases,self.bp,assigned,FIXTURE_KEY)
            self.assertEqual(post.call_count,1)
        self.assertEqual(checked["post_case_count"],64)
        self.assertEqual(checked["crossfold_post_edges"],0)

    def test_caller_fails_closed_on_forged_preassignment(self):
        bad={"fold":{x["blueprint_id"]:i%4 for i,x in enumerate(self.bp)},
             "cv_status":"PREFOLD_READY_NOT_VALIDATED"}
        with self.assertRaisesRegex(ValueError,"INVALID_R8_PREASSIGNMENT_SCHEMA"):
            production.verify_after_G3_before_CV(self.cases,self.bp,bad,FIXTURE_KEY)

    def test_caller_refuses_crossfold_edge_no_repartition(self):
        assigned=production.precommit_before_G3(self.bp,FIXTURE_KEY)
        by_fold={}
        for bp in self.bp:
            by_fold.setdefault(assigned["fold"][bp["blueprint_id"]],bp["blueprint_id"])
        a,b=list(by_fold.values())[:2]
        ca=next(x for x in self.cases if x["blueprint_id"]==a)
        cb=next(x for x in self.cases if x["blueprint_id"]==b)
        cb["cards"][0]["text"]=ca["cards"][0]["text"]
        with self.assertRaisesRegex(ValueError,"FOLD_LEAK_CV_INVALID"):
            production.verify_after_G3_before_CV(self.cases,self.bp,assigned,FIXTURE_KEY)

    def test_caller_rejects_missing_key(self):
        assigned=production.precommit_before_G3(self.bp,FIXTURE_KEY)
        with self.assertRaisesRegex(ValueError,"INVALID_R8_PRIVATE_HMAC_KEY"):
            production.verify_after_G3_before_CV(self.cases,self.bp,assigned,None)

if __name__=="__main__":
    unittest.main()
