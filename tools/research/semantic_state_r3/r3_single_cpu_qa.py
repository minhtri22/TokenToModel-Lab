#!/usr/bin/env python3
"""R3 single integrated source-only CPU QA, including deliberate negative mutations.
All tests are deterministic, no model import/training/TEST/GPU, no file writes.
"""
from __future__ import annotations
from copy import deepcopy
from collections import Counter
import hashlib,importlib.util,json,random,unittest
from pathlib import Path

HERE=Path(__file__).resolve().parent

def module(name,file):
 spec=importlib.util.spec_from_file_location(name,HERE/file)
 obj=importlib.util.module_from_spec(spec)
 spec.loader.exec_module(obj)
 return obj

gen=module('r3_source_generator','r3_generator.py')
chk=module('r3_source_independent_checker','r3_independent_checker.py')
ORACLE,INPUT=gen.build()
ORACLE_BYTES=gen.stable(ORACLE)
INPUT_BYTES=gen.stable(INPUT)

class R3QA(unittest.TestCase):
 def negative(self,why,oracle=None,model=None):
  with self.assertRaises(chk.Invalid,msg=why):chk.check(ORACLE if oracle is None else oracle, INPUT if model is None else model)

 def test_01_generated_dimensions(self):
  self.assertEqual(len(ORACLE['groups']),96);self.assertEqual(len(INPUT['records']),384)
 def test_02_exact_record_projection(self):
  expected=[{'story':c['story'],'question':c['question']} for g in ORACLE['groups'] for c in g['cells']]
  self.assertEqual(INPUT['records'],expected)
 def test_03_byte_determinism(self):
  a,b=gen.build();self.assertEqual(ORACLE_BYTES,gen.stable(a));self.assertEqual(INPUT_BYTES,gen.stable(b))
 def test_04_checker_pass(self):
  self.assertEqual(chk.check(ORACLE,INPUT)['independent_visible_text_rule_interpreter_correct'],384)
 def test_05_four_cells(self):
  self.assertTrue(all([c['cell'] for c in g['cells']]==['A_T','A_D','B_T','B_D'] for g in ORACLE['groups']))
 def test_06_all_counterfactuals_flip(self):
  self.assertTrue(all(g['cells'][0]['answer']!=g['cells'][2]['answer'] for g in ORACLE['groups']))
 def test_07_all_distractors_constant(self):
  self.assertTrue(all(g['cells'][1]['answer']==g['cells'][3]['answer'] for g in ORACLE['groups']))
 def test_08_input_only_exact_keys(self):
  self.assertEqual(set(INPUT),{'schema','records'})
  self.assertTrue(all(set(x)=={'story','question'} for x in INPUT['records']))
 def test_09_split_groups(self):
  self.assertEqual(Counter((g['family'],g['split']) for g in ORACLE['groups']),Counter({(f,s):16 for f in ('T1','T2','T3') for s in ('DEV','CHALLENGE')}))
 def test_10_motif_disjoint(self):
  self.assertEqual(chk.check(ORACLE,INPUT)['graph_motifs_cross_split'],0)
 def test_11_no_story_split_overlap(self):
  self.assertEqual(chk.check(ORACLE,INPUT)['story_overlap_cross_split'],0)
 def test_12_valid_preconditions_all(self):
  for group in ORACLE['groups']:
   for variant in (0,2):chk.run_visible(chk.parse_story(group['cells'][variant]['story']))
 def test_13_three_handoffs_T1(self):
  groups=[g for g in ORACLE['groups'] if g['family']=='T1']
  self.assertEqual(len(groups),32)
  for group in groups:
   e=group['cells'][0]['source_events']
   handoffs=Counter(x['item'] for x in e if x['op']=='HANDOFF')
   self.assertEqual(max(handoffs.values()),3)
   self.assertGreaterEqual(len({x['item'] for x in e if 'item' in x}),3)
 def test_14_goal_cancel_and_delegation_T2(self):
  self.assertTrue(all({'CANCEL_GOAL','DELEGATE_GOAL'}<=set(e['op'] for e in g['cells'][0]['source_events']) for g in ORACLE['groups'] if g['family']=='T2'))
 def test_15_indirect_alias_T3(self):
  self.assertTrue(all(sum(e['op']=='DEFINE_ALIAS' for e in g['cells'][0]['source_events'])==2 for g in ORACLE['groups'] if g['family']=='T3'))
 def test_16_alias_motifs_different_by_split(self):
  a={chk.motif(g['cells'][0]['source_events'],g['family'],'') for g in ORACLE['groups'] if g['family']=='T3' and g['split']=='DEV'}
  b={chk.motif(g['cells'][0]['source_events'],g['family'],'') for g in ORACLE['groups'] if g['family']=='T3' and g['split']=='CHALLENGE'}
  self.assertTrue(a.isdisjoint(b))
 def test_17_heuristic_not_100(self):
  r=chk.check(ORACLE,INPUT);self.assertLess(r['shallow_keyed_direct_baseline_correct'],384)
 def test_18_zero_gpu_neural(self):
  r=chk.check(ORACLE,INPUT);self.assertEqual((r['GPU_calls'],r['original_TTM_training_steps']),(0,0))
 def test_19_input_raw_roundtrip(self):
  self.assertEqual(chk.load_json(INPUT_BYTES),INPUT)
 def test_20_oracle_raw_roundtrip(self):
  self.assertEqual(chk.load_json(ORACLE_BYTES),ORACLE)
 def test_21_input_hash_pin(self):self.assertEqual(hashlib.sha256(INPUT_BYTES).hexdigest(),'4fa0ad45acdfecb2143a984127e6ad0c50126c203996148d60843eb1214cd50a')
 def test_22_oracle_hash_pin(self):self.assertEqual(hashlib.sha256(ORACLE_BYTES).hexdigest(),'bd9fb15d3f3850823e083269a61df90eaddaea3e61b8b73e9f40b4ec74c7ce47')
 def test_23_all_q_text_bound_to_two_keys(self):
  for group in ORACLE['groups']:
   self.assertNotEqual(group['cells'][0]['question'],group['cells'][1]['question'])
 def test_24_single_event_intervention(self):
  for group in ORACLE['groups']:
   a=group['cells'][0]['source_events'];b=group['cells'][2]['source_events']
   self.assertEqual(sum(x!=y for x,y in zip(a,b)),1)
 def test_25_no_metadata_leak_in_public_model(self):self.assertNotIn('source_events',INPUT_BYTES.decode())
 def test_26_public_not_final(self):self.assertTrue(ORACLE['labels_public'] and not ORACLE['sealed_final'])
 def test_27_parse_all_questions(self):
  self.assertTrue(all(chk.Q_HOLDER.fullmatch(x['question']) or chk.Q_GOAL.fullmatch(x['question']) for x in INPUT['records']))
 def test_28_parent_candidate_count(self):self.assertEqual(ORACLE['counts']['inputs'],96*4)

 def test_29_negative_model_root_answer_vector(self):
  m=deepcopy(INPUT);m['answer_vector']=[c['answer'] for g in ORACLE['groups'] for c in g['cells']];self.negative('ROOT_ANSWER_VECTOR',model=m)
 def test_30_negative_model_root_oracle(self):
  m=deepcopy(INPUT);m['oracle']=ORACLE;self.negative('ROOT_ORACLE',model=m)
 def test_31_negative_model_root_split(self):
  m=deepcopy(INPUT);m['split']='DEV';self.negative('ROOT_SPLIT',model=m)
 def test_32_negative_model_root_unexpected(self):
  m=deepcopy(INPUT);m['training']=True;self.negative('ROOT_UNEXPECTED',model=m)
 def test_33_negative_model_record_answer(self):
  m=deepcopy(INPUT);m['records'][0]['answer']='Lan';self.negative('RECORD_ANSWER',model=m)
 def test_34_negative_model_record_events(self):
  m=deepcopy(INPUT);m['records'][0]['source_events']=[];self.negative('RECORD_EVENTS',model=m)
 def test_35_negative_model_record_split(self):
  m=deepcopy(INPUT);m['records'][0]['split']='DEV';self.negative('RECORD_SPLIT',model=m)
 def test_36_negative_model_record_id(self):
  m=deepcopy(INPUT);m['records'][0]['id']='R2A';self.negative('RECORD_ID',model=m)
 def test_37_negative_model_row_type(self):
  m=deepcopy(INPUT);m['records'][0]='text';self.negative('RECORD_TYPE',model=m)
 def test_38_negative_model_short_question(self):
  m=deepcopy(INPUT);m['records'][0]['question']='';self.negative('EMPTY_Q',model=m)
 def test_39_negative_model_extra_record(self):
  m=deepcopy(INPUT);m['records'].append(m['records'][0]);self.negative('EXTRA_RECORD',model=m)
 def test_40_negative_model_reorder_projection(self):
  m=deepcopy(INPUT);m['records'][0],m['records'][1]=m['records'][1],m['records'][0];self.negative('WRONG_ORDER',model=m)
 def test_41_negative_oracle_false_sealed_claim(self):
  o=deepcopy(ORACLE);o['declaration']='Sealed FINAL TEST with hidden labels';self.negative('FALSE_FINAL',oracle=o)
 def test_42_negative_oracle_sealed_flag(self):
  o=deepcopy(ORACLE);o['sealed_final']=True;self.negative('SEALED_FLAG',oracle=o)
 def test_43_negative_oracle_labels_flag(self):
  o=deepcopy(ORACLE);o['labels_public']=False;self.negative('FALSE_LABELS',oracle=o)
 def test_44_negative_oracle_root_metadata(self):
  o=deepcopy(ORACLE);o['private']=True;self.negative('ORACLE_ROOT_UNEXPECTED',oracle=o)
 def test_45_negative_oracle_wrong_counts(self):
  o=deepcopy(ORACLE);o['counts']['inputs']=0;self.negative('WRONG_COUNTS',oracle=o)
 def test_46_negative_oracle_missing_cell(self):
  o=deepcopy(ORACLE);o['groups'][0]['cells'].pop();self.negative('MISSING_CELL',oracle=o)
 def test_47_negative_oracle_bad_answer(self):
  o=deepcopy(ORACLE);o['groups'][0]['cells'][0]['answer']='ZZZ';self.negative('ANSWER',oracle=o)
 def test_48_negative_oracle_tampered_source_events(self):
  o=deepcopy(ORACLE);o['groups'][0]['cells'][0]['source_events']=[];self.negative('SOURCE_EVENTS',oracle=o)
 def test_49_negative_oracle_intervention_not_changed(self):
  o=deepcopy(ORACLE);o['groups'][0]['cells'][2]=deepcopy(o['groups'][0]['cells'][0]);o['groups'][0]['cells'][2]['cell']='B_T';self.negative('NO_TARGET_FLIP',oracle=o)
 def test_50_negative_oracle_wrong_group_id(self):
  o=deepcopy(ORACLE);o['groups'][0]['group_id']='T1-DEV-999';self.negative('GROUP_ID',oracle=o)
 def test_51_negative_oracle_duplicate_group_id(self):
  o=deepcopy(ORACLE);o['groups'][1]['group_id']=o['groups'][0]['group_id'];self.negative('DUPLICATE_GROUP',oracle=o)
 def test_52_negative_oracle_split_group_mismatch(self):
  o=deepcopy(ORACLE);o['groups'][0]['split']='CHALLENGE';self.negative('SPLIT_GROUP',oracle=o)
 def test_53_negative_oracle_distractor_changed(self):
  o=deepcopy(ORACLE);o['groups'][0]['cells'][3]['answer']='ZZZ';self.negative('DISTRACTOR',oracle=o)
 def test_54_negative_oracle_changed_two_events(self):
  o=deepcopy(ORACLE);o['groups'][0]['cells'][2]['story']=o['groups'][1]['cells'][2]['story'];self.negative('CHANGED_TWO_EVENTS',oracle=o)
 def test_55_negative_illegal_handoff(self):
  o=deepcopy(ORACLE);c=o['groups'][0]['cells'][0];c['story']=c['story'].replace(' passes ',' makes ');self.negative('ILLEGAL_HANDOFF',oracle=o)
 def test_56_negative_illegal_cancel(self):
  o=deepcopy(ORACLE);g=next(g for g in o['groups'] if g['family']=='T2');c=g['cells'][0];c['story']=c['story'].replace(' cancels goal ',' cancels intent ');self.negative('ILLEGAL_CANCEL',oracle=o)
 def test_57_negative_ambiguous_alias(self):
  o=deepcopy(ORACLE);g=next(g for g in o['groups'] if g['family']=='T3');c=g['cells'][0];c['story']=c['story'].replace('The alias ','The alias Missing');self.negative('ALIAS_MALFORMED',oracle=o)
 def test_58_negative_oracle_duplicate_source_input(self):
  o=deepcopy(ORACLE);o['groups'][0]['cells'][1]['question']=o['groups'][0]['cells'][0]['question'];self.negative('DUPLICATE_SOURCE_INPUT',oracle=o)
 def test_59_negative_duplicate_model_json_key(self):
  raw=INPUT_BYTES.replace(b'"schema":',b'"schema":"Evil","schema":',1)
  with self.assertRaises(chk.Invalid):chk.verify_raw(ORACLE_BYTES,raw)
 def test_60_negative_duplicate_oracle_json_key(self):
  raw=ORACLE_BYTES.replace(b'"schema":',b'"schema":"Evil","schema":',1)
  with self.assertRaises(chk.Invalid):chk.verify_raw(raw,INPUT_BYTES)
 def test_61_negative_nonfinite_json(self):
  with self.assertRaises(chk.Invalid):chk.load_json(b'{"schema":NaN}')
 def test_62_negative_invalid_utf8(self):
  with self.assertRaises(chk.Invalid):chk.load_json(b'\xff')
 def test_63_negative_challenge_graph_relabel(self):
  o=deepcopy(ORACLE)
  a=next(g for g in o['groups'] if g['family']=='T1' and g['split']=='DEV' and g['group_id'].endswith('000'))
  b=next(g for g in o['groups'] if g['family']=='T1' and g['split']=='CHALLENGE' and g['group_id'].endswith('000'))
  # Exchange group membership, preserving valid IDs and counts; motif signature now overlaps splits.
  a['group_id'],b['group_id']=b['group_id'],a['group_id']
  a['split'],b['split']=b['split'],a['split']
  self.negative('CROSS_SPLIT_MOTIF_LEAK',oracle=o)
 def test_64_negative_event_wrong_precondition(self):
  o=deepcopy(ORACLE);g=next(g for g in o['groups'] if g['family']=='T1');c=g['cells'][0]
  lines=c['story'].split('\n');idx=next(i for i,line in enumerate(lines) if ' passes ' in line);lines[idx]='An passes key to Lan.'
  c['story']='\n'.join(lines);self.negative('BAD_CHAIN_STATE',oracle=o)
 def test_65_negative_oracle_wrong_cell_order(self):
  o=deepcopy(ORACLE);o['groups'][0]['cells'][0],o['groups'][0]['cells'][1]=o['groups'][0]['cells'][1],o['groups'][0]['cells'][0];self.negative('CELL_ORDER',oracle=o)
 def test_66_negative_oracle_nonexistent_query(self):
  o=deepcopy(ORACLE);o['groups'][0]['cells'][0]['question']='Who holds spaceship?';self.negative('UNKNOWN_QUERY',oracle=o)
 def test_67_alias_redefinition_precondition(self):
  g=next(g for g in ORACLE['groups'] if g['family']=='T3')
  events=deepcopy(g['cells'][0]['source_events'])
  names=[e['alias'] for e in events if e['op']=='DEFINE_ALIAS']
  self.assertEqual(len(names),2)
  second=next(i for i,e in enumerate(events) if e['op']=='DEFINE_ALIAS' and e['alias']==names[1])
  events[second]['alias']=names[0]
  with self.assertRaisesRegex(chk.Invalid,'ALIAS_AMBIGUOUS_OR_REDEFINED'):
   chk.run_visible(events)
 def test_68_illegal_handoff_precondition(self):
  g=next(g for g in ORACLE['groups'] if g['family']=='T1')
  events=deepcopy(g['cells'][0]['source_events'])
  first=next(i for i,e in enumerate(events) if e['op']=='HANDOFF')
  events[first]['p']='Thao' if events[first]['p']!='Thao' else 'Lan'
  with self.assertRaisesRegex(chk.Invalid,'HANDOFF_PRECONDITION'):
   chk.run_visible(events)
 def test_69_illegal_cancel_precondition(self):
  g=next(g for g in ORACLE['groups'] if g['family']=='T2')
  events=deepcopy(g['cells'][0]['source_events'])
  first=next(i for i,e in enumerate(events) if e['op']=='CANCEL_GOAL')
  events[first]['g']='count' if events[first]['g']!='count' else 'read'
  with self.assertRaisesRegex(chk.Invalid,'CANCEL_GOAL_PRECONDITION'):
   chk.run_visible(events)
 def test_70_nonexistent_alias_resolution(self):
  g=next(g for g in ORACLE['groups'] if g['family']=='T3')
  events=deepcopy(g['cells'][0]['source_events'])
  first=next(i for i,e in enumerate(events) if e['op']=='HANDOFF')
  events[first]['p']='UnknownAlias'
  with self.assertRaisesRegex(chk.Invalid,'UNRESOLVED_ALIAS_OR_UNKNOWN_PERSON'):
   chk.run_visible(events)


if __name__=='__main__':unittest.main(verbosity=2)
