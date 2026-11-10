#!/usr/bin/env python3
"""One-batch CPU QA with adversarial negative mutations for R2A.
Does not access model, checkpoint, GPU, network, or private corpus.
"""
from __future__ import annotations
from copy import deepcopy
from pathlib import Path
import hashlib, json, sys, unittest
sys.path.insert(0,str(Path(__file__).resolve().parent))
import r2a_generator as g
import r2a_independent_checker as c

class TestR2A(unittest.TestCase):
 @classmethod
 def setUpClass(cls):
  cls.d,cls.m=g.build()
  cls.check=c.check(cls.d,cls.m)

 def test_01_256_records(self):self.assertEqual(len(self.d['pairs']),256)
 def test_02_128_pairs(self):self.assertEqual(len({x['pair_id'] for x in self.d['pairs']}),128)
 def test_03_128_query_switches(self):self.assertEqual(len(self.d['probes']),128)
 def test_04_safe_input(self):self.assertTrue(all(set(x)=={'story','question'} for x in self.m['records']))
 def test_05_deterministic_bytes(self):self.assertEqual(g.stable_json(self.d),g.stable_json(g.build()[0]))
 def test_06_independent_answer(self):self.assertEqual(self.check['ordered_update_interpreter_correct'],256)
 def test_07_query_switch(self):self.assertEqual(self.check['question_binding_probes_correct'],128)
 def test_08_bow_upper_bound(self):self.assertEqual(self.check['bag_of_words_upper_bound_correct_of_256'],128)
 def test_09_balanced_last_position(self):self.assertEqual(self.check['last_event_is_queried_key_fraction'],0.5)
 def test_10_third_sentence_shortcut_fails(self):self.assertLess(self.check['position_only_controls_correct_of_256']['third_sentence'],192)
 def test_11_last_sentence_shortcut_fails(self):self.assertLess(self.check['position_only_controls_correct_of_256']['last_sentence'],192)
 def test_12_last_relevant_is_trivial_rule(self):self.assertEqual(self.check['key_aware_last_relevant_control_correct_of_256'],256)
 def test_13_new_dev_challenge_templates(self):
  self.assertTrue(any(' belongs to ' in x['story'] for x in self.d['pairs']))
  self.assertTrue(any(' has the ' in x['story'] for x in self.d['pairs']))
 def test_14_model_input_is_strict_projection(self):self.assertEqual(self.m['records'][0],{k:self.d['pairs'][0][k] for k in ('story','question')})
 def test_15_no_TTM_dependency(self):
  import inspect
  self.assertNotIn('torch',inspect.getsource(g))
  self.assertNotIn('torch',inspect.getsource(c))

 # Separate checker is called directly on each mutation, not the generator oracle.
 def assert_bad(self,change):
  d=deepcopy(self.d);m=deepcopy(self.m);change(d,m)
  with self.assertRaises(c.Invalid):c.check(d,m)
 def test_16_wrong_answer(self):self.assert_bad(lambda d,m:d['pairs'][0].__setitem__('answer','impossible'))
 def test_17_wrong_counts(self):self.assert_bad(lambda d,m:d['counts'].__setitem__('paired_records',1))
 def test_18_missing_pair_row(self):self.assert_bad(lambda d,m:d['pairs'].pop())
 def test_19_missing_probe(self):self.assert_bad(lambda d,m:d['probes'].pop())
 def test_20_model_leaks_answer(self):self.assert_bad(lambda d,m:m['records'][0].__setitem__('answer','Lan'))
 def test_21_model_projection_tamper(self):self.assert_bad(lambda d,m:m['records'][0].__setitem__('question','Wrong?'))
 def test_22_source_event_tamper(self):self.assert_bad(lambda d,m:d['pairs'][0]['source_events'][0].__setitem__('value','BAD'))
 def test_23_invalid_story_grammar(self):self.assert_bad(lambda d,m:d['pairs'][0].__setitem__('story','The key belongs Lan.'))
 def test_24_invalid_question(self):self.assert_bad(lambda d,m:d['pairs'][0].__setitem__('question','What now?'))
 def test_25_wrong_split(self):self.assert_bad(lambda d,m:d['pairs'][0].__setitem__('split','CHALLENGE'))
 def test_26_bad_query_family(self):self.assert_bad(lambda d,m:d['pairs'][0].__setitem__('family','goal'))
 def test_27_duplicate_id(self):self.assert_bad(lambda d,m:d['pairs'][1].__setitem__('id',d['pairs'][0]['id']))
 def test_28_model_record_drop(self):self.assert_bad(lambda d,m:m['records'].pop())
 def test_29_bad_probe_question(self):self.assert_bad(lambda d,m:d['probes'][0].__setitem__('question',d['pairs'][0]['question']))
 def test_30_bad_probe_answer(self):self.assert_bad(lambda d,m:d['probes'][0].__setitem__('answer','not the answer'))
 def test_31_bad_seed(self):self.assert_bad(lambda d,m:d.__setitem__('seed',1))
 def test_32_counterfactual_wrong_variant(self):self.assert_bad(lambda d,m:d['pairs'][1].__setitem__('variant','A'))
 def test_33_modified_story_metadata_only(self):self.assert_bad(lambda d,m:d['pairs'][0].__setitem__('story',d['pairs'][0]['story'].replace('\n',' ')))
 def test_34_wrong_family_split_count(self):self.assert_bad(lambda d,m:d['counts']['by_family_split'].__setitem__('goal_DEV',0))
 def test_35_no_label_in_prediction(self):self.assertNotIn('source_events',g.stable_json(self.m))
 def test_36_public_holdout_not_sealed(self):self.assertIn('not sealed TEST',self.d['declaration'])

if __name__=='__main__':unittest.main(verbosity=2)
