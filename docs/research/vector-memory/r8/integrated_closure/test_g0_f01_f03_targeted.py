"""R8 V4 targeted G0-F01/F02/F03 regressions; NON-R8 symbolic fixtures ONLY.

Do not import or generate an R8 case. This is implementation-agent QA, not a
distinct independent G0 review. Retains the separately frozen 37/37 receipt.
"""
from __future__ import annotations

import unittest
from copy import deepcopy
import gold_contract as g
import restricted_oracles as o


def simple():
    h={"id":"h1","record":"R","accession":"X","event":"E",
       "location":"L","interval":"t0","authority_policy":"P-REC-V1",
       "authority_rank":2}
    proof={"key":"proof"}
    target={"key":"target","target_identity":g.hypothesis_identity(h)}
    claims=[{"hypothesis_id":"h1","card_key":"proof",
             "predicate":p,"verified":True} for p in g.CORE]
    return [h],claims,[proof,target]


def public_case():
    return {"public_row_position":1,"public_case_count":32,
            "cards":[{"key":"key"+str(i),"source_id":"src"+str(i),
                      "text":"signed record approved; location"+str(i),
                      "status":"signed","authority_role":"authorized"}
                     for i in range(32)]}


class TargetedSourceBoundaryQA(unittest.TestCase):
    def test_F01_O1_exact_order_only_allowlist(self):
        f=o._o1_features(public_case())
        self.assertEqual(set(f),{
            "row_position_decile","card_count",
            "first_card_position","last_card_position"})
        self.assertNotIn("first_key_length",f)
        self.assertEqual(f["last_card_position"],31)

    def test_F01_key_metadata_cannot_change_order_only_result(self):
        a=public_case()
        b=deepcopy(a)
        b["cards"][0]["key"]="secretly_long_key_which_would_leak_metadata"
        b["cards"][31]["key"]="z"
        self.assertEqual(o._o1_features(a),o._o1_features(b))

    def test_F01_row_decile_remains_observable(self):
        a,b=public_case(),public_case()
        b["public_row_position"]=31
        self.assertNotEqual(o._o1_features(a),o._o1_features(b))

    def test_F02_two_card_cycle_rejected_not_abstained(self):
        hs,claims,cards=simple()
        cards.append({"key":"aux"})
        claims[0]["depends_on"]=["aux"]
        claims.append({"hypothesis_id":"h1","card_key":"aux",
                       "predicate":"AUTHORIZED","verified":True,
                       "depends_on":["proof"]})
        with self.assertRaisesRegex(ValueError,"INVALID_FIXTURE_CIRCULAR_PROOF"):
            g.resolve(hs,claims,cards)

    def test_F02_self_cycle_rejected(self):
        hs,claims,cards=simple()
        claims[0]["depends_on"]=["proof"]
        with self.assertRaisesRegex(ValueError,"INVALID_FIXTURE_CIRCULAR_PROOF"):
            g.resolve(hs,claims,cards)

    def test_F02_bad_dependency_reference_rejected(self):
        hs,claims,cards=simple()
        claims[0]["depends_on"]=["absent-card"]
        with self.assertRaisesRegex(ValueError,"INVALID_FIXTURE_MISSING_PROOF_DEPENDENCY"):
            g.resolve(hs,claims,cards)

    def test_F02_equal_authority_conflict_rejected_not_abstained(self):
        hs,claims,cards=simple()
        claims.append({"hypothesis_id":"h1","card_key":"proof",
                       "predicate":"DEFEATER","verified":True,
                       "authority_rank":2,"time_valid":True})
        with self.assertRaisesRegex(ValueError,"INVALID_FIXTURE_EQUAL_AUTHORITY_CONFLICT"):
            g.resolve(hs,claims,cards)

    def test_F02_missing_authorization_remains_valid_abstention(self):
        hs,claims,cards=simple()
        claims=[c for c in claims if c["predicate"]!="AUTHORIZED"]
        result=g.resolve(hs,claims,cards)
        self.assertEqual(result["action"],"ABSTAIN")
        self.assertEqual(result["primary_abstain_reason"],"MISSING_PREMISE")

    def test_F02_superior_negative_receipt_remains_abstain(self):
        hs,claims,cards=simple()
        claims.append({"hypothesis_id":"h1","card_key":"proof",
                       "predicate":"NEGATIVE_RECEIPT","verified":True,
                       "authority_rank":3,"time_valid":True})
        self.assertEqual(g.resolve(hs,claims,cards)["action"],"ABSTAIN")

    def test_F03_marker_only_cannot_include_neighbor_accession(self):
        case={"cards":[{"key":"x","text":
             "signed accession_x authorized proof_42 approved special_location",
             "status":"signed","authority_role":"authorized",
             "source_format":"record"}]}
        f=o._o3_features(case)
        self.assertFalse(any("accession_x" in k or "proof_42" in k or
                             "special_location" in k for k in f))
        self.assertIn("marker=signed",f)

    def test_F03_known_marker_bigram_remains_allowed(self):
        case={"cards":[{"key":"x","text":"applicable signed record",
                        "status":"signed","authority_role":"authorized"}]}
        f=o._o3_features(case)
        self.assertIn("markergram=applicable signed",f)
        self.assertIn("markergram=signed record",f)
        self.assertNotIn("markergram=signed arbitrary",f)

    def test_F02_equal_authority_conflict_invalid_even_with_missing_CORE(self):
        hs,claims,cards=simple()
        claims=[c for c in claims if c["predicate"]!="AUTHORIZED"]
        claims.append({"hypothesis_id":"h1","card_key":"proof",
                       "predicate":"DEFEATER","verified":True,
                       "authority_rank":2,"time_valid":True})
        with self.assertRaisesRegex(ValueError,"INVALID_FIXTURE_EQUAL_AUTHORITY_CONFLICT"):
            g.resolve(hs,claims,cards)

    def test_F02_equal_rank_negative_invalid_even_with_missing_CORE(self):
        hs,claims,cards=simple()
        claims=[c for c in claims if c["predicate"]!="AUTHORIZED"]
        claims.append({"hypothesis_id":"h1","card_key":"proof",
                       "predicate":"NEGATIVE_RECEIPT","verified":True,
                       "authority_rank":2,"time_valid":True})
        with self.assertRaisesRegex(ValueError,"INVALID_FIXTURE_EQUAL_AUTHORITY_CONFLICT"):
            g.resolve(hs,claims,cards)

    def test_F02_superior_negative_plus_missing_CORE_still_abstains(self):
        hs,claims,cards=simple()
        claims=[c for c in claims if c["predicate"]!="AUTHORIZED"]
        claims.append({"hypothesis_id":"h1","card_key":"proof",
                       "predicate":"NEGATIVE_RECEIPT","verified":True,
                       "authority_rank":3,"time_valid":True})
        self.assertEqual(g.resolve(hs,claims,cards)["action"],"ABSTAIN")

    def test_F03_closed_enum_rejects_identifier_in_any_categorical_field(self):
        for field in ("status","authority_role","source_format"):
            with self.subTest(field=field):
                case=public_case()
                case["cards"][0][field]="signed accession_x"
                with self.assertRaisesRegex(ValueError,
                                            "INVALID_O3_CATEGORICAL_VALUE_"+field.upper()):
                    o._o3_features(case)

    def test_F03_valid_categorical_values_remain_observable(self):
        case=public_case()
        case["cards"][0]["source_format"]="record"
        f=o._o3_features(case)
        self.assertIn("status=signed",f)
        self.assertIn("authority_role=authorized",f)
        self.assertIn("source_format=record",f)
        self.assertFalse(any("accession_x" in key for key in f))

    def test_F03_invalid_enum_rejected_before_model_fitting(self):
        cases=[]
        for i in range(4):
            c=public_case()
            c.update({"id":"nonR8_"+str(i),"component_id_pre":"bp_"+str(i),
                      "public_row_position":i,"public_case_count":4,
                      "action":"SELECT" if i%2==0 else "ABSTAIN",
                      "target_key":c["cards"][0]["key"] if i%2==0 else None})
            cases.append(c)
        self.assertEqual(o.validate_split(cases[:2],cases[2:]),"VALID_SOURCE_ONLY_SPLIT")
        cases[2]["cards"][0]["source_format"]="record private_identifier_42"
        self.assertEqual(o.validate_split(cases[:2],cases[2:]),
                         "INVALID_O3_CATEGORICAL_VALUE_SOURCE_FORMAT")

    def test_F07_existing_toy_witness_unchanged(self):
        a,b=g.f07_symbolic_twins()
        self.assertEqual(g.receipt_f07(a)["action"],"SELECT")
        self.assertEqual(g.receipt_f07(b)["action"],"ABSTAIN")


    def test_F03_null_is_not_literal_none_role(self):
        case={"cards":[{"status":"signed","authority_role":None,
                        "source_format":"record","text":"signed"}]}
        with self.assertRaisesRegex(ValueError,"INVALID_O3_CATEGORICAL_TYPE_AUTHORITY_ROLE"):
            o._o3_features(case)

    def test_F03_string_none_role_remains_allowed(self):
        case={"cards":[{"status":"signed","authority_role":"none",
                        "source_format":"record","text":"signed"}]}
        self.assertIn("authority_role=none",o._o3_features(case))

    def test_F03_null_and_non_string_rejected_for_all_fields(self):
        for field in ("status","authority_role","source_format"):
            for bad in (None,17,True,["signed"],{"key":"signed"}):
                with self.subTest(field=field,bad_type=type(bad).__name__):
                    c={"status":"signed","authority_role":"none","source_format":"record"}
                    c[field]=bad
                    case={"cards":[{**c,"text":"signed"}]}
                    with self.assertRaisesRegex(ValueError,"INVALID_O3_CATEGORICAL_TYPE_"+field.upper()):
                        o._o3_features(case)

    def test_F03_missing_is_explicit_empty_bin(self):
        case={"cards":[{"text":"signed"}]}
        z=o._o3_features(case)
        for field in ("status","authority_role","source_format"):
            self.assertIn(field+"=",z)

    def test_F03_null_preflight_rejected_before_fit(self):
        import test_integrated_source_only as fixture
        cases=[fixture.oracle_case(i,"SELECT" if i%2==0 else "ABSTAIN")
               for i in range(8)]
        cases[0]["cards"][0]["authority_role"]=None
        self.assertEqual(o.validate_split(cases[:6],cases[6:]),
                         "INVALID_O3_CATEGORICAL_TYPE_AUTHORITY_ROLE")


if __name__=="__main__":
    unittest.main()
