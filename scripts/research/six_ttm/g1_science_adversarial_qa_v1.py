#!/usr/bin/env python3
"""Independent-style adversarial QA for G1 core. No private corpus/GPU/science."""
import hashlib, importlib.util, json, tempfile
from pathlib import Path
import numpy as np

SOURCE=Path(__file__).with_name('g1_science_core_v1.py')
spec=importlib.util.spec_from_file_location('g1_core',SOURCE)
core=importlib.util.module_from_spec(spec);spec.loader.exec_module(core)


def fail(code, func):
    try:func()
    except RuntimeError as e:
        if code not in str(e):raise AssertionError(f'Expected {code}, got {e}')
    else:raise AssertionError('MISSING_GATE_'+code)


def fixture(seed=9031):
    rng=np.random.default_rng(seed)
    w=rng.normal(size=(10,15))*0.25
    v=rng.normal(size=(15,8))*0.25
    def gen(name,n):
        s=rng.normal(size=(n,10))
        t=s@w+0.05*rng.normal(size=(n,15))
        r=t@v+0.05*rng.normal(size=(n,8))
        return {'ids':np.array([hashlib.sha256(f'{name}:{i}'.encode()).hexdigest() for i in range(n)]),'s':s,'t':t,'r':r}
    return gen('train',128),gen('dev',64),gen('test',64)


def main():
    tr,dev,te=fixture()
    result=core.synthetic_qa()
    assert result['status']=='PASS_SYNTHETIC_ONLY_NO_SCIENCE'
    frozen=core.prepare(tr,dev,shuffle_n=9)
    assert frozen['null_count']==9 and not frozen['test_touched']
    science=core.evaluate(tr,dev,te,frozen,permutation_n=9,cka_n=13,bootstrap_n=19)
    assert science['null_count']==9 and science['bootstrap_count']==19
    score=core.choose_alpha([(1,0.5),(10,0.5),(100,0.5)])
    assert score==100.
    fail('ALPHA_GRID_INCOMPLETE',lambda:core.choose_alpha([(1,0.4)]))
    duplicate={k:v.copy() for k,v in te.items()};duplicate['ids'][0]=dev['ids'][0]
    fail('SPLIT_ID_LEAKAGE',lambda:core.evaluate(tr,dev,duplicate,frozen,permutation_n=9,cka_n=13,bootstrap_n=19))
    changed={k:v.copy() for k,v in tr.items()};changed['r'][:,0]=1.
    fail('TRAIN_FUNCTION_STD_DEGENERATE',lambda:core.prepare(changed,dev,shuffle_n=9))
    bad={k:v.copy() for k,v in te.items()};bad['t'][1,2]=np.nan
    fail('PACK_NONFINITE_t',lambda:core.verify_arrays(bad,64,10,15))
    bad={k:v.copy() for k,v in te.items()};bad['r']=bad['r'][:,:7]
    fail('RESPONSES_SHAPE',lambda:core.verify_arrays(bad,64,10,15))
    mutated=dict(frozen);mutated['null_permutation_sha256']='0'*64
    fail('PERMUTATION_CHANGED',lambda:core.evaluate(tr,dev,te,mutated,permutation_n=9,cka_n=13,bootstrap_n=19))
    badtest={k:v.copy() for k,v in te.items()};badtest['r']=np.repeat(tr['r'].mean(0)[None,:],64,axis=0)
    fail('TEST_SST_DEGENERATE',lambda:core.evaluate(tr,dev,badtest,frozen,permutation_n=9,cka_n=13,bootstrap_n=19))
    fail('PERMIT_MISSING_OR_MISMATCH_schema',lambda:core.permit_check({},phase='prepare'))
    # The final stage's source code must consume TEST marker before any TEST pack read.
    code=SOURCE.read_text()
    marker=code.index("with (work/'G1_TEST_ONE_SHOT_CONSUMED.marker').open('x'")
    testopen=code.index("test=load_pack(test_path,'TEST',manifest)")
    assert marker<testopen and code.index('if args.mode==\'prepare\'')<marker
    # No path to TEST in fit-dev routine except comments/flags.
    source_prepare=code[code.index('def prepare('):code.index('def cka(')]
    assert "G1_FEATURES_TEST" not in source_prepare
    assert 'torch.' not in code and 'snapshot_download' not in code
    assert 'data_read' not in source_prepare
    print(json.dumps({'status':'PASS_ADVERSARIAL_SYNTHETIC_QA_NO_SCIENCE',
      'checks':14,'tiny_data_only':True,'test_marker_before_test_pack':True,
      'test_used_for_dev_selection':False,'actual_science_executed':False},sort_keys=True))


if __name__=='__main__':main()
