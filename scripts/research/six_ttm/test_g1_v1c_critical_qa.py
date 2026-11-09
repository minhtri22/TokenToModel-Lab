#!/usr/bin/env python3
"""V1c two critical reviewer defects: CPU-only, no TinyStories or GPU."""
import hashlib
import json
import numpy as np
import g1_science_core_v1c as c
import g1_science_guard_v1b as g

rng=np.random.default_rng(420)
W=rng.normal(size=(9,14))/4
Q=rng.normal(size=(14,8))/4

def fixture(label,n):
    s=rng.normal(size=(n,9))
    t=s@W+0.1*rng.normal(size=(n,14))
    r=t@Q+0.1*rng.normal(size=(n,8))
    return {'ids':np.array([hashlib.sha256(f'{label}-{i}'.encode()).hexdigest() for i in range(n)]),
            's':s,'t':t,'r':r}

train,dev,test=fixture('train',128),fixture('dev',64),fixture('test',64)
fit=c.prepare(train,dev)
assert fit['schema']=='ttm.six.g1.fit_dev_frozen_v1b'
fit.update({'manifest_sha256':g.MANIFEST_SHA,'run_id':'synthetic-v1c',
            'train_pack_sha256':'1'*64,'dev_pack_sha256':'2'*64})
freeze_bytes=c.jbytes(fit)
freeze=g.validate_frozen_dev(freeze_bytes,g.sha_bytes(freeze_bytes),'1'*64,'2'*64,run_id='synthetic-v1c')
replay=c.prepare(train,dev)
assert all(replay[k]==v for k,v in freeze.items() if k in replay), 'TEST 1 PREPARE_TO_FINALIZE_REPLAY_FAILED'

# Invariant centered Gram: exact mathematical null under all 1,000 permutations.
# Detect the reviewer false-significant p=1/1001 regression.
one=np.ones((64,64),dtype='float64')/64
s=np.eye(64,dtype='float64')-one
t=np.eye(64,dtype='float64')-one
permtest=c.cka_permutation_pvalue(s,t,n=1000)
assert permtest['status']=='PASS_CKA'
assert abs(permtest['cka']-1.)<1e-12
assert permtest['permutation_p']==1.,f"FALSE_SIGNIFICANCE {permtest}"
assert permtest['null_at_or_above_observed']==1000

# Less structured null should be significant when 64 paired rows carry signal.
sig=c.cka_permutation_pvalue(train['s'][:64],train['s'][:64],n=1000)
assert sig['permutation_p']<=.01, sig

# Degenerate centered Gram has an explicit terminal indicator.
no=c.cka_permutation_pvalue(np.zeros((64,5)), np.ones((64,4)),n=1000)
assert no['status']=='INCONCLUSIVE_GEOMETRY_DEGENERATE'

# Numeric protocol STILL executes with real full null counts only synthetic data.
result=c.evaluate(train,dev,test,fit)
assert result['null_count']==1000 and result['cka_null_count']==1000 and result['bootstrap_count']==2000
assert np.isfinite(result['cka_permutation_p'])
print(json.dumps({'status':'PASS_V1C_CRITICAL_SYNTHETIC_QA_NO_SCIENCE',
 'checks':7,
 'freeze_replay':'PASS',
 'cka_invariant_null_p':permtest['permutation_p'],
 'cka_significant_fixture_p':sig['permutation_p'],
 'zero_gram':'INCONCLUSIVE',
 'full_loops':'1000_SHUFFLE_1000_CKA_2000_BOOTSTRAP',
 'science_executed':False},sort_keys=True))
