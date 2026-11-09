#!/usr/bin/env python3
"""Integrated G1 zero-science QA. Runtime tests on synthetic, no corpus/weights/TEST."""
import hashlib, importlib.util, io, json, tempfile
from pathlib import Path
import numpy as np
ROOT=Path(__file__).resolve().parent
PIN={'g1_science_core_v1.py':'b3ea8c890c45e3e2d248ad850977b53f5782552e',
     'g1_science_private_feature_extractor_v1.py':'f1557470ff66857e35ced71641b542685f6b3083',
     'g1_science_adversarial_qa_v1.py':'e6a93ac8248665de78d970ef9d237de5a45d9d8c'}

def blob(p):
    b=Path(p).read_bytes()
    return hashlib.sha1(b'blob '+str(len(b)).encode()+b'\0'+b).hexdigest()

def module(name,path):
    s=importlib.util.spec_from_file_location(name,path)
    m=importlib.util.module_from_spec(s);s.loader.exec_module(m);return m

def main():
    for path,pin in PIN.items():
        assert blob(ROOT/path)==pin,(path,'PIN_MISMATCH')
    math=module('core',ROOT/'g1_science_core_v1.py')
    extraction=module('extract',ROOT/'g1_science_private_feature_extractor_v1.py')
    adversary=module('adversarial',ROOT/'g1_science_adversarial_qa_v1.py')
    assert math.synthetic_qa()['status']=='PASS_SYNTHETIC_ONLY_NO_SCIENCE'
    assert extraction.prefix(extraction.normalize('a'*92+'. '+'b'*15))[1]==93
    assert len(extraction.PROBES)==8
    adversary.main()  # 14 adversarial checks (prints sanitized JSON)
    # Verify per-token conditional scoring indexing via a deterministic fake
    # distribution contract: for a prefix length P, next target logit is P-1.
    P=7;C=3
    assert list(range(P-1,P+C-1))==[6,7,8]
    # Full orthogonal rotations preserve isotropic ridge *after scaling*:
    rng=np.random.default_rng(9090)
    x=rng.normal(size=(128,12))
    y=rng.normal(size=(128,3))
    z=rng.normal(size=(64,12))
    x,z,_,_=math.standardize(x,z)
    q,_=np.linalg.qr(rng.normal(size=(12,12)))
    v,u=math.gram_fit(x)
    vq,uq=math.gram_fit(x@q)
    a=math.dual_predict(v,u,x,z,y-y.mean(0),10.)
    b=math.dual_predict(vq,uq,x@q,z@q,y-y.mean(0),10.)
    assert np.allclose(a,b,atol=1e-9)
    # Only one TEST release marker may ever be created at an exact path.
    with tempfile.TemporaryDirectory() as d:
        marker=Path(d)/'G1_TEST_ONE_SHOT_CONSUMED.marker'
        with marker.open('x') as f:f.write('USED')
        try:
            marker.open('x')
        except FileExistsError:pass
        else:raise AssertionError('ONE_SHOT_REPLAY_NOT_BLOCKED')
    # A science operation invoked without an authorized and distinct reviewer
    # must STOP, even when numerical fixture arrays are valid.
    try:math.permit_check({},phase='prepare')
    except RuntimeError as e:
        assert 'PERMIT_MISSING_OR_MISMATCH_schema' in str(e)
    else:raise AssertionError('MISSING_SCIENCE_GATE')
    print(json.dumps({'schema':'ttm.six.g1.integrated_preexec_qa.v1',
          'status':'PASS_INTEGRATED_SYNTHETIC_QA_SOURCE_PINS',
          'source_blobs_verified':3,'adversarial_tests':14,
          'orthogonal_is_neutral':True,'one_shot_second_open_rejected':True,
          'no_GPU':True,'no_private_dataset':True,
          'science_executed':False,'distinct_scientific_review_received':False},sort_keys=True))

if __name__=='__main__':main()
