#!/usr/bin/env python3
"""One integrated R3A CPU-only QA. Does not train, evaluate or load TTM.
The latest-write baseline is the independently authored R3 comparator algorithm;
its original pinned-source script remains unchanged on the Codex review branch.
"""
from __future__ import annotations
import collections,copy,hashlib,importlib.util,json,pathlib,unittest
ROOT=pathlib.Path(__file__).resolve().parent

def load(modname,file):
    spec=importlib.util.spec_from_file_location(modname,ROOT/file)
    module=importlib.util.module_from_spec(spec);spec.loader.exec_module(module);return module
G=load('gen','r3a_generator.py')
C=load('check','r3a_independent_checker.py')
L=load('latest','ttm_r3_independent_latest_write_baseline.py')
ORACLE=ROOT/'R3A_ORACLE.json';MODEL=ROOT/'R3A_MODEL_INPUT_ONLY.json'
O=C.from_bytes(ORACLE.read_bytes());M=C.from_bytes(MODEL.read_bytes())

def baseline():
    counts=collections.defaultdict(lambda:{'correct':0,'total':0})
    kinds=collections.Counter()
    for g in O['groups']:
        for c in g['cells']:
            pred,typ=L.predict({'story':c['story'],'question':c['question']})
            k=g['family']+'_'+g['split'];counts[k]['total']+=1;counts[k]['correct']+=int(pred==c['answer']);kinds[typ]+=1
    return {'correct':sum(v['correct'] for v in counts.values()),'total':384,
            'by_family_split':dict(sorted(counts.items())),'prediction_types':dict(sorted(kinds.items()))}

class IntegratedQA(unittest.TestCase):
    @classmethod
    def setUpClass(cls):cls.verified=C.validate(O,M)
    def assertInvalid(self,o=None,m=None):
        with self.assertRaises((C.Fail,ValueError,TypeError,KeyError,IndexError)):
            C.validate(O if o is None else o,M if m is None else m)
    def test_01_visible_parser_384(self):self.assertEqual(self.verified['oracle_correct'],384)
    def test_02_group_count(self):self.assertEqual(self.verified['groups'],96)
    def test_03_four_cell(self):self.assertEqual(self.verified['four_cell_counterfactuals'],96)
    def test_04_motifs_nonoverlap(self):self.assertEqual(self.verified['query_dependent_motif_cross_split'],0)
    def test_05_none_target(self):self.assertEqual(self.verified['NONE_target_answers'],32)
    def test_06_no_sealed_final(self):self.assertFalse(O['sealed_final'])
    def test_07_model_only_two_fields(self):self.assertTrue(all(set(x)=={'story','question'} for x in M['records']))
    def test_08_shuffled_input(self):self.assertTrue(self.verified['model_input_shuffled'])
    def test_09_reproduces_bytes(self):
        o,m=G.build();self.assertEqual(G.stable(o),ORACLE.read_bytes());self.assertEqual(G.stable(m),MODEL.read_bytes())
    def test_10_latest_write_cannot_solve(self):self.assertLess(baseline()['correct'],300)
    def test_11_alias_answer_critical_t1(self):
        for g in O['groups']:
            if g['family']=='T1':
                a,b=g['cells'][0],g['cells'][2]
                self.assertNotEqual(a['answer'],b['answer'])
                aa,bb=a['story'].split('\n'),b['story'].split('\n')
                self.assertEqual([i for i,(x,y) in enumerate(zip(aa,bb)) if x!=y],
                                 [g['intervention_index']])
                self.assertTrue(any(' passes ' in x and ' to ' in x
                                    for x in aa[g['intervention_index']+1:]))
    def test_12_no_training(self):self.assertEqual(M['schema'],C.MODEL)
    def test_13_input_sha(self):self.assertEqual(hashlib.sha256(MODEL.read_bytes()).hexdigest(),'2510866d82641bd27207082566d6b4dbb867e59516794e422dff8fb041646402')
    def test_14_oracle_sha(self):self.assertEqual(hashlib.sha256(ORACLE.read_bytes()).hexdigest(),'b509fae3f63399c978d532c2686d147bd4ba41e44b2aa9135dcd38360e6ffb08')
    # All negative fixtures must fail closed.
    def test_N01_root_answer_vector(self):
        m=copy.deepcopy(M);m['answer_vector']=[0]*384;self.assertInvalid(m=m)
    def test_N02_root_oracle(self):
        m=copy.deepcopy(M);m['oracle']='LEAK';self.assertInvalid(m=m)
    def test_N03_root_split(self):
        m=copy.deepcopy(M);m['split']='FINAL';self.assertInvalid(m=m)
    def test_N04_row_answer(self):
        m=copy.deepcopy(M);m['records'][0]['answer']='Lan';self.assertInvalid(m=m)
    def test_N05_row_event(self):
        m=copy.deepcopy(M);m['records'][1]['source_events']=[];self.assertInvalid(m=m)
    def test_N06_row_id(self):
        m=copy.deepcopy(M);m['records'][1]['id']='T1-DEV-0-A';self.assertInvalid(m=m)
    def test_N07_duplicate_json_root(self):
        with self.assertRaises(C.Fail):C.from_bytes(b'{"schema":"x","schema":"y","records":[]}')
    def test_N08_duplicate_json_row(self):
        with self.assertRaises(C.Fail):C.from_bytes(b'{"schema":"x","records":[{"story":"a","story":"b"}]}')
    def test_N09_false_sealed(self):
        o=copy.deepcopy(O);o['sealed_final']=True;self.assertInvalid(o=o)
    def test_N10_false_declaration(self):
        o=copy.deepcopy(O);o['declaration']='Sealed FINAL TEST';self.assertInvalid(o=o)
    def test_N11_oracle_root_extra(self):
        o=copy.deepcopy(O);o['private_labels']=[1];self.assertInvalid(o=o)
    def test_N12_counts_tamper(self):
        o=copy.deepcopy(O);o['counts']['groups']=95;self.assertInvalid(o=o)
    def test_N13_answer_tamper(self):
        o=copy.deepcopy(O);o['groups'][0]['cells'][0]['answer']='FAKE';self.assertInvalid(o=o)
    def test_N14_source_events_tamper(self):
        o=copy.deepcopy(O);o['groups'][0]['cells'][0]['source_events'][0]['op']='FAKE';self.assertInvalid(o=o)
    def test_N15_omit_cell(self):
        o=copy.deepcopy(O);o['groups'][0]['cells'].pop();self.assertInvalid(o=o)
    def test_N16_repeat_model_row(self):
        m=copy.deepcopy(M);m['records'][1]=copy.deepcopy(m['records'][0]);self.assertInvalid(m=m)
    def test_N17_missing_model_row(self):
        m=copy.deepcopy(M);m['records'].pop();self.assertInvalid(m=m)
    def test_N18_null_story(self):
        m=copy.deepcopy(M);m['records'][0]['story']=None;self.assertInvalid(m=m)
    def test_N19_unknown_question(self):
        m=copy.deepcopy(M);m['records'][0]['question']='Who won?';self.assertInvalid(m=m)
    def test_N20_rewrite_event_grammar(self):
        o=copy.deepcopy(O);o['groups'][0]['cells'][0]['story']='XYZ';self.assertInvalid(o=o)
    def test_N21_undefined_alias_in_story(self):
        o=copy.deepcopy(O)
        for c in o['groups'][0]['cells']:
            c['story']=c['story'].replace('The alias ','The fake ')
        self.assertInvalid(o=o)
    def test_N22_bad_handoff_precondition(self):
        o=copy.deepcopy(O)
        for c in o['groups'][0]['cells']:
            c['story']=c['story'].replace(' passes ',' steals ')
        self.assertInvalid(o=o)
    def test_N23_bad_goal_cancel(self):
        o=copy.deepcopy(O);g=next(x for x in o['groups'] if x['family']=='T2' and x['split']=='CHALLENGE')
        for c in g['cells']:c['story']=c['story'].replace(' cancels goal ',' cancels goal fake')
        self.assertInvalid(o=o)
    def test_N24_swap_projection(self):
        m=copy.deepcopy(M);m['records'][0]['question']=m['records'][1]['question'];self.assertInvalid(m=m)
    def test_N25_split_mislabeled(self):
        o=copy.deepcopy(O);o['groups'][0]['split']='CHALLENGE';self.assertInvalid(o=o)
    def test_N26_intervention_idx(self):
        o=copy.deepcopy(O);o['groups'][0]['intervention_index']=-1;self.assertInvalid(o=o)
    def test_N27_one_variant_same_story(self):
        o=copy.deepcopy(O);g=o['groups'][0];g['cells'][2]['story']=g['cells'][0]['story'];self.assertInvalid(o=o)
    def test_N28_nan_json(self):
        with self.assertRaises(C.Fail):C.from_bytes(b'{"schema":NaN}')
    def test_N29_model_top_level_list(self):self.assertInvalid(m=M['records'])
    def test_N30_duplicate_group_id(self):
        o=copy.deepcopy(O);o['groups'][1]['group_id']=o['groups'][0]['group_id'];self.assertInvalid(o=o)

if __name__=='__main__':unittest.main(verbosity=2)
