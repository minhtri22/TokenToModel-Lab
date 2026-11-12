#!/usr/bin/env python3
"""Synthetic string-only candidate metric test; no trained-model outputs or final prompts."""
from __future__ import annotations
import hashlib, importlib.util, json, numpy, pathlib
p=pathlib.Path(__file__).with_name('ttm_hdec_r1_frozen_metrics_v1.py')
spec=importlib.util.spec_from_file_location('hdec_metric',p)
m=importlib.util.module_from_spec(spec);spec.loader.exec_module(m)
checks=[]
def test(name,condition):
 if not condition:raise AssertionError(name)
 checks.append(name)
def fail(fn):
 try:fn()
 except (ValueError,RuntimeError,TypeError):return True
 return False

test('NUMPY_VERSION_FIXED',numpy.__version__=='2.3.5')
test('REPEAT_SHORT_ZERO',m.repeat_fraction('a b')==0.)
test('REPEAT_UNIQUE_ZERO',m.repeat_fraction('a b c d e f')==0.)
test('REPEAT_RECURRING_GT_ZERO',m.repeat_fraction('a b c a b c a b c')>0.5)
test('SINGLE_QUOTED_WORD',m.words("Don't move, Joy's toy!")==["don't",'move',"joy's",'toy'])
test('LOWERCASE',m.words('DOG Dog')==['dog','dog'])
test('CI_CONSTANT_NEGATIVE',m.ci_paired([-0.2]*24)[1]<0)
test('CI_CONSTANT_ZERO',m.ci_paired([0.]*24)==(0.,0.))
test('NEG_BAD_CI_SIZE',fail(lambda:m.ci_paired([0.]*23)))
test('NEG_NONFINITE',fail(lambda:m.ci_paired([float('nan')]*24)))
scores=[{'D0':{q:1 for q in ('prompt_adherence','coherence','consistency')},'D1':{q:1 for q in ('prompt_adherence','coherence','consistency')}} for _ in range(24)]
rows=[{'pair_id':f'R{i:02d}','D0':'one two three one two three one two three','D1':'one two three four five six seven eight nine'} for i in range(1,25)]
r=m.candidate_gate(rows,scores)
test('CANDIDATE_SYNTHETIC_ALL_PASS',r['candidate_pass'] and len(r['gates'])==7 and r['wins_D1']==24)
rows2=[dict(row) for row in rows];rows2[0]['pair_id']='R22'
test('NEG_PAIR_IDS',fail(lambda:m.candidate_gate(rows2,scores)))
rows3=[dict(row) for row in rows];rows3[0]['D0']=None
test('NEG_BAD_TEXT',fail(lambda:m.candidate_gate(rows3,scores)))
s2=[dict(q) for q in scores];s2[0]={'D0':dict(scores[0]['D0']),'D1':dict(scores[0]['D1'])};s2[0]['D1']['coherence']=1.2
test('NEG_INVALID_RATER',fail(lambda:m.candidate_gate(rows,s2)))
report={'operation':'TTM_SMALL4M_H_DEC_R1_PREEXEC_METRIC_SYNTHETIC_ONLY','checks':checks,'check_count':len(checks),'numPy_version':numpy.__version__,'metric_source_sha256':hashlib.sha256(p.read_bytes()).hexdigest(),'model_forward':0,'new_eval_final_prompt_read':False,'scientific_result':'NOT_EXECUTED','verdict':'PASS_SYNTHETIC_METRIC_QA'}
pathlib.Path(__file__).with_name('TTM_HDEC_R1_FROZEN_METRIC_SYNTHETIC_QA_20261112.json').write_text(json.dumps(report,indent=2,sort_keys=True)+'\n')
print(json.dumps({'checks':len(checks),'verdict':report['verdict'],'metric_source_sha256':report['metric_source_sha256']}))
