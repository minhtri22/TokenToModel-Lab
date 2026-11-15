"""G0-VERSION-01 targeted regression: no silent legacy G_pre lock acceptance.

Scope: NON-R8 synthetic manifest/cases only; no private key, reader or science.
This is implementation-agent QA, NOT independent review or protected custody.
"""
from __future__ import annotations

from copy import deepcopy
import unittest
import folds_raters as f
import r8_production_caller as caller
from test_g0_final_three_findings import production_blueprints, production_cases

PUBLIC_KEY = b"NONSECRET_G0_VERSION_FIXTURE_KEY_LENGTH_OVER_32"
LEGACY_SCHEMA = "TTM_VM_R8_GPRE_HMAC_V1"
LEGACY_DOMAIN = "R8_GPRE_FOLDS_V1"

def legacy_same_fold_lock(blueprints):
    """Recreate old V1 lock envelope using a V2-equivalent fold witness.

    The independent reviewer found a 32-row input where real V1 and V2 fold
    assignments matched. Here the fold, component/count/status are *identical*
    to current results, so only algorithm-version provenance can reject it.
    """
    new=f.preassign_r8(blueprints, PUBLIC_KEY)
    old={key:deepcopy(value) for key,value in new.items()
         if key!="algorithm_id"}
    old["lock_schema"]=LEGACY_SCHEMA
    fields=("lock_schema","blueprint_hmac","fold","component_id_pre",
            "component_count","case_count_by_fold","cv_status")
    old["preassignment_hmac"]=f._r8_hmac(
        PUBLIC_KEY,LEGACY_DOMAIN,{k:old[k] for k in fields})
    return new,old

class G0VersionBindingQA(unittest.TestCase):
    def setUp(self):
        self.bp=production_blueprints()
        self.cases=production_cases(self.bp)

    def test_v2_schema_and_algorithm_marker_are_explicit(self):
        self.assertEqual(f.R8_PREASSIGN_LOCK_SCHEMA,
                         "TTM_VM_R8_GPRE_HMAC_V2")
        self.assertEqual(f.R8_GPRE_ALGORITHM_ID,
                         "R8_GPRE_CANONICAL_JSON_COMPONENT_RANKING_V2")
        self.assertEqual(f.R8_GPRE_PREASSIGNMENT_MAC_DOMAIN,
                         "R8_GPRE_FOLDS_V2")

    def test_current_precommit_metadata_is_hmac_bound(self):
        lock=f.preassign_r8(self.bp,PUBLIC_KEY)
        self.assertEqual(lock["lock_schema"],f.R8_PREASSIGN_LOCK_SCHEMA)
        self.assertEqual(lock["algorithm_id"],f.R8_GPRE_ALGORITHM_ID)
        fields=("lock_schema","algorithm_id","blueprint_hmac","fold",
                "component_id_pre","component_count","case_count_by_fold",
                "cv_status")
        digest=f._r8_hmac(PUBLIC_KEY,f.R8_GPRE_PREASSIGNMENT_MAC_DOMAIN,
                          {k:lock[k] for k in fields})
        self.assertEqual(lock["preassignment_hmac"],digest)

    def test_previous_valid_v1_envelope_with_same_fold_is_rejected(self):
        v2,v1=legacy_same_fold_lock(self.bp)
        for field in ("fold","component_id_pre","component_count",
                      "case_count_by_fold","cv_status","blueprint_hmac"):
            self.assertEqual(v1[field],v2[field])
        with self.assertRaisesRegex(ValueError,"INVALID_R8_PREASSIGNMENT_SCHEMA"):
            f.postcheck_r8(self.cases,self.bp,v1,PUBLIC_KEY)

    def test_grafted_v2_schema_with_missing_algorithm_marker_is_rejected(self):
        _,old=legacy_same_fold_lock(self.bp)
        old["lock_schema"]=f.R8_PREASSIGN_LOCK_SCHEMA
        with self.assertRaisesRegex(ValueError,"INVALID_R8_GPRE_ALGORITHM_ID"):
            f.postcheck_r8(self.cases,self.bp,old,PUBLIC_KEY)

    def test_unknown_algorithm_marker_rejected(self):
        x=f.preassign_r8(self.bp,PUBLIC_KEY)
        x["algorithm_id"]="R8_GPRE_UNKNOWN_RANKING_VERSION"
        with self.assertRaisesRegex(ValueError,"INVALID_R8_GPRE_ALGORITHM_ID"):
            f.postcheck_r8(self.cases,self.bp,x,PUBLIC_KEY)

    def test_null_algorithm_marker_rejected(self):
        x=f.preassign_r8(self.bp,PUBLIC_KEY)
        x["algorithm_id"]=None
        with self.assertRaisesRegex(ValueError,"INVALID_R8_GPRE_ALGORITHM_ID"):
            f.postcheck_r8(self.cases,self.bp,x,PUBLIC_KEY)

    def test_v1_domain_hmac_rejected_even_with_v2_metadata(self):
        x=f.preassign_r8(self.bp,PUBLIC_KEY)
        fields=("lock_schema","algorithm_id","blueprint_hmac","fold",
                "component_id_pre","component_count","case_count_by_fold","cv_status")
        x["preassignment_hmac"]=f._r8_hmac(
            PUBLIC_KEY,LEGACY_DOMAIN,{k:x[k] for k in fields})
        with self.assertRaisesRegex(ValueError,"INVALID_R8_HMAC_PROVENANCE_PREASSIGNMENT_HMAC"):
            f.postcheck_r8(self.cases,self.bp,x,PUBLIC_KEY)

    def test_valid_v2_lock_accepted_only_by_strict_caller(self):
        lock=caller.precommit_before_G3(self.bp,PUBLIC_KEY)
        result=caller.verify_after_G3_before_CV(
            self.cases,self.bp,lock,PUBLIC_KEY)
        self.assertEqual(result["cv_status"],"POST_GRAPH_NO_CROSSFOLD_EDGE")
        self.assertEqual(result["post_case_count"],64)

    def test_realistic_four_component_same_fold_witness_rejects_v1(self):
        bp=production_blueprints()
        for index,row in enumerate(bp):
            row["event_graph_id"]=f"GROUP_{index//8}"
        current,legacy=legacy_same_fold_lock(bp)
        self.assertEqual(current["component_count"],4)
        self.assertEqual(sorted(current["case_count_by_fold"]),[8,8,8,8])
        self.assertEqual(current["fold"],legacy["fold"])
        with self.assertRaisesRegex(ValueError,"INVALID_R8_PREASSIGNMENT_SCHEMA"):
            caller.verify_after_G3_before_CV(
                production_cases(bp),bp,legacy,PUBLIC_KEY)

    def test_row_reordering_does_not_change_algorithm_hmac(self):
        a=f.preassign_r8(self.bp,PUBLIC_KEY)
        b=f.preassign_r8(list(reversed(self.bp)),PUBLIC_KEY)
        self.assertEqual(a["algorithm_id"],b["algorithm_id"])
        self.assertEqual(a["preassignment_hmac"],b["preassignment_hmac"])

if __name__=="__main__":
    unittest.main()
