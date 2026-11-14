"""Source-only negative QA for 3 G0 reviewer defects, never R8 data.

These are implementation-agent tests, NOT an independent reviewer signoff.
No access to private custody, GPU, Reader, or PROBE256.
"""
from __future__ import annotations

import unittest
from copy import deepcopy
import gold_contract as g
import folds_raters as f


def simple_proof():
    h={"id":"h1","record":"R","accession":"X","event":"E",
       "location":"L","interval":"t0","authority_policy":"P-REC-V1",
       "authority_rank":2}
    cards=[{"key":"S"},{"key":"target","target_identity":g.hypothesis_identity(h)}]
    claims=[{"hypothesis_id":"h1","card_key":"S","predicate":p,
             "verified":True} for p in g.CORE]
    return [h],claims,cards


def production_blueprints():
    return [{"blueprint_id":f"bp_{family}_{slot}",
             "pair_id":f"pair_{family}_{slot}",
             "event_graph_id":f"ev_{family}_{slot}",
             "template_cluster_id":f"tmpl_{family}_{slot}",
             "relation_family":f"F{family+1:02d}"}
            for family in range(8) for slot in range(4)]


def production_cases(blueprints):
    cases=[]
    for bp in blueprints:
        for action in ("SELECT","ABSTAIN"):
            cid=bp["blueprint_id"]+"_"+action
            cards=[{"key":cid+f"_card{i:02d}","text":cid+f" token{i} evidence"}
                   for i in range(32)]
            cases.append({"case_id":cid,"blueprint_id":bp["blueprint_id"],
                          "question":"event relation "+cid,"event_signature":cid,
                          "action":action,"cards":cards,
                          "target_key":cards[0]["key"] if action=="SELECT" else None})
    return cases


class G0ThreeFindingsNegativeQA(unittest.TestCase):
    def test_minimal_proof_does_not_include_unverified_claim_dependency(self):
        hs,claims,cards=simple_proof()
        cards.append({"key":"U"})
        claims.append({"hypothesis_id":"h1","card_key":"S",
                       "predicate":"AUTHORIZED","verified":False,
                       "depends_on":["U"]})
        r=g.resolve(hs,claims,cards)
        self.assertEqual(r["action"],"SELECT")
        self.assertEqual(r["proof_sets"]["h1"],[["S"]])

    def test_minimal_proof_tracks_selected_verified_dependency(self):
        hs,claims,cards=simple_proof()
        cards.append({"key":"U"})
        next(x for x in claims if x["predicate"]=="AUTHORIZED")["depends_on"]=["U"]
        r=g.resolve(hs,claims,cards)
        self.assertEqual(r["proof_sets"]["h1"],[["S","U"]])

    def test_alternate_verified_support_prefers_minimal_proof(self):
        hs,claims,cards=simple_proof()
        cards.append({"key":"U"})
        claims.append({"hypothesis_id":"h1","card_key":"S",
                       "predicate":"AUTHORIZED","verified":True,
                       "depends_on":["U"]})
        r=g.resolve(hs,claims,cards)
        self.assertEqual(r["proof_sets"]["h1"],[["S"]])

    def test_transitive_verified_dependency_included(self):
        hs,claims,cards=simple_proof()
        cards.extend([{"key":"U"},{"key":"V"}])
        next(x for x in claims if x["predicate"]=="AUTHORIZED")["depends_on"]=["U"]
        claims.append({"hypothesis_id":"h1","card_key":"U",
                       "predicate":"SCOPE","verified":True,
                       "depends_on":["V"]})
        r=g.resolve(hs,claims,cards)
        self.assertEqual(r["proof_sets"]["h1"],[["S","U","V"]])

    def test_f07_unrelated_event_negative_cannot_defeat(self):
        source,_=g.f07_symbolic_twins()
        altered=deepcopy(source)
        altered["evidence"].append({"key":"neg-other-event",
            "negates_accession":"X","link_event":"UNRELATED_EVENT",
            "authorized":True,"authority_rank":3,"time_valid":True})
        self.assertEqual(g.receipt_f07(altered)["action"],"SELECT")

    def test_f07_matching_event_negative_defeats(self):
        source,_=g.f07_symbolic_twins()
        altered=deepcopy(source)
        altered["evidence"].append({"key":"neg-same-event",
            "negates_accession":"X","link_event":"E","authorized":True,
            "authority_rank":3,"time_valid":True})
        self.assertEqual(g.receipt_f07(altered)["action"],"ABSTAIN")

    def test_f07_missing_event_negative_fails_closed_as_unlinked(self):
        source,_=g.f07_symbolic_twins()
        altered=deepcopy(source)
        altered["evidence"].append({"key":"neg-no-event",
            "negates_accession":"X","authorized":True,
            "authority_rank":3,"time_valid":True})
        self.assertEqual(g.receipt_f07(altered)["action"],"SELECT")

    def test_r8_rejects_truncated_blueprint_before_hmac(self):
        with self.assertRaisesRegex(ValueError,"INVALID_R8_BLUEPRINT_COUNT"):
            f.preassign_r8(production_blueprints()[:2],b"non_secret_fixture_only")

    def test_r8_rejects_wrong_family_balance(self):
        bp=production_blueprints()
        bp[0]["relation_family"]="F02"
        with self.assertRaisesRegex(ValueError,"INVALID_R8_FAMILY_BALANCE"):
            f.validate_r8_blueprint_manifest(bp)

    def test_r8_rejects_truncated_cases_even_with_valid_pre(self):
        bp=production_blueprints()
        with self.assertRaisesRegex(ValueError,"INVALID_R8_CASE_COUNT"):
            f.postcheck_r8(production_cases(bp)[:4],bp,{"fold":{b["blueprint_id"]:i%4
                                  for i,b in enumerate(bp)},"cv_status":"PREFOLD_READY_NOT_VALIDATED"})

    def test_r8_rejects_missing_twin_action(self):
        bp=production_blueprints()
        cases=production_cases(bp)
        cases[0]["action"]="ABSTAIN"
        cases[0]["target_key"]=None
        with self.assertRaisesRegex(ValueError,"INVALID_R8_TWIN_ACTION_BALANCE"):
            f.validate_r8_case_manifest(cases,bp)

    def test_r8_rejects_wrong_card_count(self):
        bp=production_blueprints()
        cases=production_cases(bp)
        cases[0]["cards"].pop()
        with self.assertRaisesRegex(ValueError,"INVALID_R8_CARD_COUNT"):
            f.validate_r8_case_manifest(cases,bp)

    def test_r8_rejects_duplicate_case_id(self):
        bp=production_blueprints()
        cases=production_cases(bp)
        cases[0]["case_id"]=cases[1]["case_id"]
        with self.assertRaisesRegex(ValueError,"INVALID_R8_DUPLICATE_CASE_ID"):
            f.validate_r8_case_manifest(cases,bp)

    def test_r8_rejects_unlocked_fold_instead_of_repartition(self):
        bp=production_blueprints()
        cases=production_cases(bp)
        with self.assertRaisesRegex(ValueError,"INVALID_R8_LOCKED_FOLD_MANIFEST"):
            f.postcheck_r8(cases,bp,None)

    def test_r8_production_blueprints_and_cases_validate_symbolically(self):
        bp=production_blueprints()
        cases=production_cases(bp)
        self.assertEqual(len(f.validate_r8_blueprint_manifest(bp)),32)
        self.assertIs(f.validate_r8_case_manifest(cases,bp),True)
        pre=f.preassign_r8(bp,b"non_secret_source_only_fixture_key_32_bytes")
        self.assertEqual(set(pre["fold"]),{b["blueprint_id"] for b in bp})
        self.assertNotEqual(pre["cv_status"],"NOT_ESTIMABLE")
        result=f.postcheck_r8(cases,bp,pre,b"non_secret_source_only_fixture_key_32_bytes")
        self.assertEqual(result["post_case_count"],64)
        self.assertEqual(result["expected_twins_per_blueprint"],2)
        self.assertTrue(result["no_repartition"])


if __name__=="__main__":
    unittest.main()
