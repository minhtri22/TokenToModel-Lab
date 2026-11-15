"""Scoped B03-C component-signature negative tests; NON-R8 fixture only.

Independent reviewer found delimiter-joined component IDs noninjective.
This suite is implementation-agent QA, NOT independent review or G2 custody.
"""
from __future__ import annotations
import hashlib
import hmac
import unittest
from unittest.mock import patch
import folds_raters as f
import r8_production_caller as caller
from test_g0_final_three_findings import production_blueprints,production_cases

FAKE_KEY=b"FAKE_G0_B03_C_NON_SECRET_HMAC_TEST_KEY_2026"

def ambiguous_manifest():
    bp=production_blueprints()
    for row,member in zip(bp[:4],("a","b|c","a|b","c")):
        row["blueprint_id"]=member
    bp[0]["event_graph_id"]=bp[1]["event_graph_id"]="GROUP_0"
    bp[2]["event_graph_id"]=bp[3]["event_graph_id"]="GROUP_1"
    return bp

class ComponentRankSignatureQA(unittest.TestCase):
    def test_original_reviewer_witness_distinct_after_json_encoding(self):
        a=["a","b|c"];b=["a|b","c"]
        self.assertEqual("|".join(a),"|".join(b))
        self.assertNotEqual(a,b)
        self.assertNotEqual(f._component_signature(a),f._component_signature(b))

    def test_membership_canonical_order_and_domain_separator(self):
        a=f._component_signature(["a","b|c"])
        self.assertEqual(a,f._component_signature(["b|c","a"]))
        self.assertTrue(a.startswith(b"R8_GPRE_COMPONENT_V1\\x00"))
        self.assertNotEqual(a,f._component_signature(["a|b","c"]))

    def test_special_characters_cannot_alias_member_boundaries(self):
        pairs=[
            (["a","b|c"],["a|b","c"]),
            (["a","b,c"],["a,b","c"]),
            (["a","b\\nc"],["a\\nb","c"]),
            (["a","b\\\"c"],["a\\\"b","c"]),
            (["a","b]c"],["a]b","c"]),
            (["x","y\\\\z"],["x\\\\y","z"]),
        ]
        for left,right in pairs:
            with self.subTest(left=left,right=right):
                self.assertNotEqual(f._component_signature(left),
                                    f._component_signature(right))

    def test_rejects_nonstring_or_repeated_component_member(self):
        for comp in (["a",None],["a",1],["a","a"]):
            with self.subTest(comp=comp),self.assertRaises(ValueError):
                f._component_signature(comp)

    def test_preassign_hmac_receives_two_distinct_rank_messages(self):
        bp=ambiguous_manifest()
        f.validate_r8_blueprint_manifest(bp)
        with patch.object(f.hmac,"new",wraps=hmac.new) as spy:
            lock=f.preassign_r8(bp,FAKE_KEY)
        self.assertEqual(lock["component_count"],30)
        self.assertNotEqual(lock["component_id_pre"]["a"],
                            lock["component_id_pre"]["a|b"])
        msgs=[c.args[1] for c in spy.call_args_list if len(c.args)>1]
        sig0=f._component_signature(["a","b|c"])
        sig1=f._component_signature(["a|b","c"])
        self.assertIn(sig0,msgs)
        self.assertIn(sig1,msgs)
        self.assertNotEqual(hmac.new(FAKE_KEY,sig0,hashlib.sha256).digest(),
                            hmac.new(FAKE_KEY,sig1,hashlib.sha256).digest())

    def test_adversarial_32_blueprint_caller_roundtrip_no_r8_data(self):
        bp=ambiguous_manifest()
        pre=caller.precommit_before_G3(bp,FAKE_KEY)
        cases=production_cases(bp)
        result=caller.verify_after_G3_before_CV(cases,bp,pre,FAKE_KEY)
        self.assertEqual(result["cv_status"],"POST_GRAPH_NO_CROSSFOLD_EDGE")
        self.assertEqual(result["post_case_count"],64)

    def test_source_hmac_is_sensitive_to_component_membership(self):
        bp=ambiguous_manifest()
        baseline=f.preassign_r8(bp,FAKE_KEY)
        changed=[dict(row) for row in bp]
        # Valid alternate graph: remove both repeated event IDs, changing G_pre.
        changed[1]["event_graph_id"]="CHANGED_GROUP_0"
        changed[3]["event_graph_id"]="CHANGED_GROUP_1"
        revised=f.preassign_r8(changed,FAKE_KEY)
        self.assertNotEqual(baseline["blueprint_hmac"],revised["blueprint_hmac"])
        with self.assertRaisesRegex(ValueError,"INVALID_R8_HMAC_PROVENANCE"):
            f.postcheck_r8(production_cases(changed),changed,baseline,FAKE_KEY)

if __name__=="__main__":
    unittest.main()
