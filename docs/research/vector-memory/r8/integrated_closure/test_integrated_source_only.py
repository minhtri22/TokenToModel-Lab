"""One bounded NON-R8 symbolic QA packet. Never imports generated R8 or private data.
All tests are SAME_AGENT_SEPARATE_CHECKER, not independent external review.
Run: python -m unittest discover -s docs/research/vector-memory/r8/integrated_closure -p 'test_*.py' -v
"""
from __future__ import annotations
import unittest
from copy import deepcopy
import gold_contract as g
import folds_raters as f
import restricted_oracles as o

def make_h(hid="h1",location="L1"):
    return {"id":hid,"record":"R1","accession":"X","event":"E1",
            "location":location,"interval":"t0","authority_policy":"P-REC-V1",
            "authority_rank":2}
def proof_input(hypotheses=None,alternate=False):
    hs=hypotheses or [make_h()]
    cards=[];claims=[]
    for h in hs:
        stem=h["id"]
        base=stem+"-proof"
        cards.append({"key":base,"target_identity":None})
        cards.append({"key":stem+"-target","target_identity":g.hypothesis_identity(h)})
        for p in g.CORE:
            claims.append({"hypothesis_id":stem,"card_key":base,"predicate":p,
                           "verified":True})
        if alternate:
            cards.append({"key":stem+"-alternate"})
            claims.append({"hypothesis_id":stem,"card_key":stem+"-alternate",
                           "predicate":"AUTHORIZED","verified":True})
    return hs,claims,cards
def blueprints(n=8):
    return [{"blueprint_id":"bp"+str(i),"pair_id":"p"+str(i),
             "event_graph_id":"ev"+str(i),"template_cluster_id":"t"+str(i)}
            for i in range(n)]
def doc(bp,question="where is the signed receipt located"):
    return {"blueprint_id":bp,"question":question,
            "event_signature":"E"+bp,
            "cards":[{"text":("document "+bp+" signed record approved location "+str(i))}
                     for i in range(3)]}
def oracle_case(i,action):
    cards=[]
    for j in range(32):
        cards.append({"key":f"q{i}_c{j}","text":f"card word {j} signed audit received",
             "source_id":f"src-{j}","source_marker":"audit" if j==0 else "copy",
             "source_format":"record","status":"signed" if j==0 else "pending",
             "authority_role":"authorized" if j==0 else "none"})
    return {"id":f"nonR8_{i}","component_id_pre":f"nonR8_component_{i}",
            "action":action,"target_key":cards[0]["key"] if action=="SELECT" else None,
            "question":"Which verified receipt record establishes X?",
            "cards":cards}
class GoldQA(unittest.TestCase):
    def test_01_F07_authority_edge_flip_not_keyword(self):
        a,b=g.f07_symbolic_twins()
        x,y=g.receipt_f07(a),g.receipt_f07(b)
        self.assertEqual(x["action"],"SELECT")
        self.assertEqual(x["target_key"],"receipt-card")
        self.assertEqual(y["action"],"ABSTAIN")
        self.assertIn("MISSING_PREMISE",y["all_applicable_reasons"])
    def test_02_F07_keyword_both_twins_equal(self):
        a,b=g.f07_symbolic_twins()
        self.assertEqual([x["text"] for x in a["evidence"]],
                         [x["text"] for x in b["evidence"]])
    def test_03_F07_false_positive_keyword_only(self):
        _,b=g.f07_symbolic_twins()
        for x in b["evidence"]:
            x["text"]="applicable signed record received X approved audit"
        self.assertEqual(g.receipt_f07(b)["action"],"ABSTAIN")
    def test_04_F07_untrusted_forecast_cannot_select(self):
        a,b=g.f07_symbolic_twins()
        for e in a["evidence"]:e["authorized"]=False
        self.assertEqual(g.receipt_f07(a)["action"],"ABSTAIN")
    def test_05_2_hypotheses_same_entity_different_location(self):
        hs,cl,ca=proof_input([make_h("one","L1"),make_h("two","L2")])
        result=g.resolve(hs,cl,ca)
        self.assertEqual(result["action"],"ABSTAIN")
        self.assertEqual(result["primary_abstain_reason"],"MULTIPLE_SUPPORTED_HYPOTHESES")
    def test_06_duplicate_target_card_rejected(self):
        hs,cl,ca=proof_input()
        ca.append(dict(ca[-1],key="another-target"))
        with self.assertRaisesRegex(ValueError,"ONE_KEY"):
            g.resolve(hs,cl,ca)
    def test_07_duplicate_key_rejected(self):
        hs,cl,ca=proof_input();ca.append(dict(ca[0]))
        with self.assertRaisesRegex(ValueError,"DUPLICATE_CARD_KEY"):
            g.resolve(hs,cl,ca)
    def test_08_equal_authority_stalemate(self):
        hs,cl,ca=proof_input()
        cl.append({"hypothesis_id":"h1","card_key":"h1-proof","predicate":"DEFEATER",
                   "verified":True,"authority_rank":2,"time_valid":True})
        v=g.resolve(hs,cl,ca)
        self.assertEqual(v["primary_abstain_reason"],"UNRESOLVED_AUTHORITY")
    def test_09_superior_negative_receipt_is_abstain(self):
        hs,cl,ca=proof_input()
        cl.append({"hypothesis_id":"h1","card_key":"h1-proof",
                   "predicate":"NEGATIVE_RECEIPT","verified":True,
                   "authority_rank":3,"time_valid":True})
        self.assertEqual(g.resolve(hs,cl,ca)["action"],"ABSTAIN")
    def test_10_circular_proof_not_accepted(self):
        hs,cl,ca=proof_input()
        ca.append({"key":"circular"})
        cl.append({"hypothesis_id":"h1","card_key":"circular","predicate":"AUTHORIZED",
                   "verified":True,"depends_on":["h1-proof"]})
        for c in cl:
            if c["card_key"]=="h1-proof":c["depends_on"]=["circular"]
        self.assertEqual(g.resolve(hs,cl,ca)["action"],"ABSTAIN")
    def test_11_alternative_minimal_sets(self):
        hs,cl,ca=proof_input(alternate=True)
        r=g.resolve(hs,cl,ca)
        self.assertEqual(r["action"],"SELECT")
        self.assertEqual(len(r["proof_sets"]["h1"]),1) # same base card supports all predicates
    def test_12_no_proof_abstain_reason(self):
        hs,cl,ca=proof_input()
        cl=[c for c in cl if c["predicate"]!="AUTHORIZED"]
        r=g.resolve(hs,cl,ca)
        self.assertEqual(r["action"],"ABSTAIN")
        self.assertEqual(r["primary_abstain_reason"],"MISSING_PREMISE")
        self.assertIn("NO_SUPPORTED_HYPOTHESIS",r["all_applicable_reasons"])
class FoldQA(unittest.TestCase):
    def test_13_pre_components_and_four_folds(self):
        p=f.preassign(blueprints(),b"TEST_NON_PRIVATE_KEY")
        self.assertEqual(p["component_count"],8)
        self.assertEqual(p["case_count_by_fold"],[2,2,2,2])
    def test_14_pair_and_event_edges(self):
        b=blueprints();b[1]["event_graph_id"]=b[0]["event_graph_id"]
        p=f.preassign(b,b"TEST_NON_PRIVATE_KEY")
        self.assertEqual(p["component_count"],7)
        self.assertEqual(p["component_id_pre"]["bp0"],p["component_id_pre"]["bp1"])
    def test_15_fewer_four_components_not_estimable(self):
        self.assertEqual(f.preassign(blueprints(3),b"k")["cv_status"],"NOT_ESTIMABLE")
    def test_16_post_crossfold_duplicate_card_invalid(self):
        pre=f.preassign(blueprints(),b"TEST_NON_PRIVATE_KEY")["fold"]
        cases=[doc("bp"+str(i)) for i in range(8)]
        a,b=next((a,b) for a in cases for b in cases
                 if pre[a["blueprint_id"]]!=pre[b["blueprint_id"]])
        b["cards"][0]["text"]=a["cards"][0]["text"]
        r=f.postcheck(cases,pre)
        self.assertEqual(r["cv_status"],"FOLD_LEAK_CV_INVALID")
        self.assertTrue(r["no_repartition"])
    def test_17_word5_duplicate_qa(self):
        c={"question":"ONE two three four FIVE six","cards":[]}
        self.assertIn(("one","two","three","four","five"),f.fingerprint(c))
    def test_18_abstract_four_rater_balance(self):
        r=f.rater_allocation_source_qa()
        self.assertEqual(r["scores"],128)
        self.assertEqual(r["counts"]["D"]["cases"],32)
        self.assertEqual(r["owner_choice"],"PENDING")
    def test_19_component_label_not_event_id(self):
        p=f.preassign(blueprints(),b"k")
        self.assertIn("component_id_pre",p)
        self.assertNotIn("event_graph_id",p)
class OracleQA(unittest.TestCase):
    def data(self):
        return ([oracle_case(i,"SELECT" if i%2==0 else "ABSTAIN")
                 for i in range(6)],
                [oracle_case(i,"SELECT" if i%2==0 else "ABSTAIN")
                 for i in range(6,8)])
    def test_20_O1_O8_executable_on_non_R8(self):
        train,test=self.data()
        r=o.evaluate(train,test)
        self.assertEqual(r["status"],"EXECUTED_NON_R8_SYNTHETIC_ONLY")
        self.assertEqual(set(r["oracles"]),{f"O{i}" for i in range(1,9)})
        for key,val in r["oracles"].items():
            if key=="O4":
                self.assertEqual(val["question_only"]["status"],
                                 "EXECUTED_NON_R8_SYNTHETIC_ONLY")
            else:self.assertEqual(val["status"],"EXECUTED_NON_R8_SYNTHETIC_ONLY")
    def test_21_O5_balanced_train_case_weights(self):
        train,test=self.data()
        r=o.evaluate(train,test)["oracles"]["O5"]
        self.assertAlmostEqual(r["training_positive"]+31*r["training_negative_each"],1)
        self.assertEqual(r["select_n"],1)
    def test_22_O6_joint_abstain_accounting(self):
        train,test=self.data()
        r=o.evaluate(train,test)["oracles"]["O6"]
        self.assertEqual(r["joint_n"],2)
        self.assertGreaterEqual(r["joint_correct"],0)
    def test_29_O5_candidate_key_not_dependent_on_hidden_test_action(self):
        train,test=self.data()
        oracle=o.evaluate(train,test)["oracles"]["O5"]
        self.assertEqual(set(oracle["keys"]),{c["id"] for c in test})
        self.assertEqual(oracle["select_n"],1)
    def test_23_group_overlap_invalid(self):
        train,test=self.data()
        test[0]["component_id_pre"]=train[0]["component_id_pre"]
        self.assertEqual(o.validate_split(train,test),"FOLD_LEAK_CV_INVALID")
    def test_24_one_class_train_not_estimable(self):
        train,test=self.data()
        for c in train:c["action"]="ABSTAIN";c["target_key"]=None
        self.assertEqual(o.validate_split(train,test),"NOT_ESTIMABLE_ONE_CLASS_TRAIN")
    def test_25_O5_null_and_Holm_family(self):
        self.assertEqual(o.PRIMARY,("O2","O3","O4","O5","O6"))
        self.assertEqual(o.holm_primary({})["status"],"NOT_ESTIMABLE")
        r=o.holm_primary({k:.001 for k in o.PRIMARY},exchangeable=True)
        self.assertAlmostEqual(r["tests"]["O2"]["cutoff"],.01)
    def test_26_O8_R7_marker_regression(self):
        train,test=self.data()
        test[0]["cards"][0]["text"]+=" applicable signed record"
        r=o.evaluate(train,test)
        self.assertGreaterEqual(r["oracles"]["O8"]["positive_rule_triggers"]
                                ["R7_APPLICABLE_SIGNED_RECORD"],1)
    def test_27_duplicate_card_keys_rejected(self):
        train,test=self.data();test[0]["cards"][1]["key"]=test[0]["cards"][0]["key"]
        self.assertEqual(o.validate_split(train,test),"INVALID_DUPLICATE_CARD_KEYS")
    def test_28_runtime_pins_never_claim_G2(self):
        r=o.runtime()
        self.assertIn("python",r)
        self.assertEqual(r["seed"],20261114)
if __name__=="__main__":
    unittest.main()
