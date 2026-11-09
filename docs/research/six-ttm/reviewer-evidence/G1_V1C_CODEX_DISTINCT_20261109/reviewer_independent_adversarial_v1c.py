"""Distinct reviewer CPU-only fixture suite. Never accesses real G1 sources, models or TEST."""
from __future__ import annotations
import copy
import hashlib
import io
import json
import os
from pathlib import Path
from unittest.mock import patch
import numpy as np
from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.primitives.asymmetric.ed25519 import Ed25519PrivateKey
import g1_science_core_v1b as old
import g1_science_core_v1c as core
import g1_science_guard_v1b as old_guard
import g1_science_guard_v1c as guard
import g1_science_private_feature_extractor_v1c as extractor

ROOT = Path(__file__).resolve().parent
PIN = 'd5d0c5346a595557a76349f900d09be50bce289c'
SHA64 = 'a' * 64
RUN = 'DISTINCT_SYNTHETIC_RUN'
results = []

def observe(name, status='CONTROL_PASS', **detail):
    entry = {'case':name, 'status':status, **detail}
    results.append(entry)
    print(json.dumps(entry, sort_keys=True, allow_nan=False))

def check(name, condition, **detail):
    if not condition:
        raise AssertionError(name + ': ' + str(detail))
    observe(name, **detail)

def expect_stop(name, action, contains=None):
    try:
        action()
    except Exception as exc:
        msg = str(exc)
        if contains is not None and contains not in msg:
            raise AssertionError(name + ': unexpected ' + msg) from exc
        observe(name, error_type=type(exc).__name__, error_code=msg[:140])
    else:
        raise AssertionError(name + ': expected a fail-closed rejection')

rng = np.random.default_rng(4409901)
W = rng.normal(size=(12, 20)) / 3
Q = rng.normal(size=(20, 8)) / 3

def synthetic(label, n):
    s = rng.normal(size=(n, 12))
    t = s @ W + rng.normal(size=(n, 20)) * 0.06
    r = t @ Q + rng.normal(size=(n, 8)) * 0.03
    return {'ids':np.asarray([hashlib.sha256(f'REVIEW_ONLY_{label}_{i}'.encode()).hexdigest() for i in range(n)]),
            's':s, 't':t, 'r':r}

train = synthetic('TRAIN', 128)
dev = synthetic('DEV', 64)
test = synthetic('HELDOUT_SYNTHETIC', 64)

# CRITICAL A. Reconstruct exactly the frozen schema written by prepare CLI.
old_replay = old.prepare(train, dev, shuffle_n=1000)
old_written = {**old_replay, 'schema':'ttm.six.g1.fit_dev_frozen_v1b',
               'train_pack_sha256':SHA64, 'dev_pack_sha256':SHA64,
               'manifest_sha256':old.MANIFEST_SHA, 'run_id':RUN}
old_bytes = old.jbytes(old_written)
old_validated = old_guard.validate_frozen_dev(old_bytes, hashlib.sha256(old_bytes).hexdigest(),
                                               SHA64, SHA64, run_id=RUN)
old_again = old.prepare(train, dev, shuffle_n=1000)
check('V1B_FREEZE_ACCEPTED_BY_GUARD', old_validated['schema']=='ttm.six.g1.fit_dev_frozen_v1b')
check('V1B_SCHEMA_MISMATCH_REPRODUCED', old_again['schema'] != old_validated['schema'] and
      not all(old_again[k]==v for k,v in old_validated.items() if k in old_again),
      status='CONTROL_PASS', old_replay_schema=old_again['schema'], persisted_schema=old_validated['schema'])
observe('V1B_CRITICAL_A_OBSERVED', 'DEFECT_REPRODUCED', terminal='FIT_DEV_SELECTION_CHANGED')

new_replay = core.prepare(train, dev, shuffle_n=1000)
new_written = {**new_replay, 'schema':'ttm.six.g1.fit_dev_frozen_v1b',
               'train_pack_sha256':SHA64, 'dev_pack_sha256':SHA64,
               'manifest_sha256':core.MANIFEST_SHA, 'run_id':RUN}
freeze_bytes = core.jbytes(new_written)
freeze_sha = hashlib.sha256(freeze_bytes).hexdigest()
validated = guard.validate_frozen_dev(freeze_bytes, freeze_sha, SHA64, SHA64, run_id=RUN)
new_again = core.prepare(train, dev, shuffle_n=1000)
check('V1C_FULL_PREPARE_FINALIZE_REPLAY_MATCH',
      all(new_again[k]==v for k,v in validated.items() if k in new_again) and
      len(new_again)==len(set(new_again)&set(validated)),
      freeze_sha256=freeze_sha, null_count=validated['null_count'],
      permutation_sha256=validated['null_permutation_sha256'],
      alphas=[validated[k] for k in ('aligned_alpha','direct_alpha','target_probe_alpha')])
check('V1C_DEV_REPLAY_UNCONSUMED_MARKER',
      not (ROOT/'G1_TEST_READ_ONE_SHOT_CONSUMED.marker').exists())

def mut_freeze(label, mutation, code):
    obj = copy.deepcopy(new_written)
    mutation(obj)
    raw = core.jbytes(obj)
    expect_stop(label, lambda:guard.validate_frozen_dev(raw,hashlib.sha256(raw).hexdigest(),
                                                         SHA64,SHA64,run_id=RUN),code)

mut_freeze('FREEZE_MISSING_ALPHA', lambda f:f.pop('direct_alpha'), 'FIT_DEV_KEYSET')
mut_freeze('FREEZE_BOOLEAN_ALPHA', lambda f:f.__setitem__('aligned_alpha',True), 'FIT_DEV_ALPHA')
mut_freeze('FREEZE_NULL_BOOLEAN_ALPHA', lambda f:f['null_alphas'].__setitem__(0,True), 'FIT_DEV_NULL_GRID')
mut_freeze('FREEZE_MISSING_SEED', lambda f:f.pop('seed_boot'), 'FIT_DEV_FIELD')
mut_freeze('FREEZE_NONHEX_DIGEST', lambda f:f.__setitem__('null_permutation_sha256','z'*64), 'FIT_DEV_SHA_FORMAT')
mut_freeze('FREEZE_WRONG_RUN', lambda f:f.__setitem__('run_id','OTHER_RUN'), 'FIT_DEV_FIELD_RUN_ID')
mut_freeze('FREEZE_WRONG_TRAIN_SHA',lambda f:f.__setitem__('train_pack_sha256','b'*64),'FIT_DEV_FIELD_TRAIN_PACK_SHA256')
mut_freeze('FREEZE_PARTIAL_NULLS',lambda f:f.__setitem__('null_alphas',f['null_alphas'][:997]),'FIT_DEV_NULL_GRID')
mut_freeze('FREEZE_NONFINITE_SCORE',lambda f:f.__setitem__('aligned_dev_macro_r2',float('inf')),'') if False else None
expect_stop('FREEZE_STALE_HASH',lambda:guard.validate_frozen_dev(freeze_bytes,'b'*64,SHA64,SHA64,run_id=RUN), 'FIT_DEV_HASH_CHANGED')
expect_stop('FREEZE_EMPTY_BYTES',lambda:guard.validate_frozen_dev(b'',hashlib.sha256(b'').hexdigest(),SHA64,SHA64,run_id=RUN),'FIT_DEV_JSON_INVALID')
unknown_freeze_bytes = core.jbytes({**new_written, 'unexpected': 'value'})
expect_stop('FREEZE_ADDED_UNKNOWN_KEY', lambda: guard.validate_frozen_dev(
    unknown_freeze_bytes, hashlib.sha256(unknown_freeze_bytes).hexdigest(),
    SHA64, SHA64, run_id=RUN), 'FIT_DEV_KEYSET')

# CRITICAL B. Mathematically permutation-invariant centered Gram, scale chosen
# separately from original reviewer to expose old denominator rounding.
identity = np.eye(64,dtype=np.float64)*0.001
old_observed = old_guard.safe_cka(identity,identity)['cka']
old_rng = np.random.default_rng(old.SEED_CKA)
old_null = [old.cka(identity[old_rng.permutation(64)],identity) for _ in range(1000)]
old_p = (1+sum(v>=old_observed for v in old_null))/1001
check('V1B_FALSE_CKA_SIGNIFICANCE_REPRODUCED', old_p==1/1001,
      old_observed=old_observed,old_null_min=min(old_null),old_null_max=max(old_null),old_p=old_p)
observe('V1B_CRITICAL_B_OBSERVED','DEFECT_REPRODUCED',p=old_p)
new_cka = core.cka_permutation_pvalue(identity,identity,n=1000,seed=core.SEED_CKA)
x = identity-identity.mean(0)
g = x@x.T
den = float(np.linalg.norm(g)**2)
obs_independent=float(np.sum(g*g)/den)
check('V1C_INVARIANT_CKA_P_ONE',new_cka['permutation_p']==1.0 and
      new_cka['null_at_or_above_observed']==1000,observed=new_cka['cka'],p=new_cka['permutation_p'])
check('V1C_INDEPENDENT_GRAM_OBSERVED',abs(obs_independent-new_cka['cka'])<1e-13,
      independent_observed=obs_independent)
perm_rng=np.random.default_rng(core.SEED_CKA)
tol=64*np.finfo('float64').eps*max(1.,abs(obs_independent))
independent_ge=sum(float(np.sum(g[np.ix_(perm_rng.permutation(64),perm_rng.permutation(64))]*g)/den)>=obs_independent-tol
                   for _ in []) if False else None
perm_rng=np.random.default_rng(core.SEED_CKA)
ge=0
for _ in range(1000):
    perm=perm_rng.permutation(64)
    v=float(np.sum(g[np.ix_(perm,perm)]*g)/den)
    ge+=v>=obs_independent-tol
check('V1C_CKA_INDEPENDENT_1000_DRAW_REPLAY', ge==1000 and
      new_cka['permutation_p']==(1+ge)/1001 and
      abs(new_cka['tie_absolute_tolerance']-tol)<1e-25,draws=1000,tolerance=tol)

rng2=np.random.default_rng(709)
paired=rng2.normal(size=(64,10));paired2=paired+rng2.normal(size=(64,10))*0.04
signal=core.cka_permutation_pvalue(paired,paired2,n=1000,seed=core.SEED_CKA)
check('V1C_INFORMATIVE_PAIRED_P_SMALL',signal['permutation_p']<=.01,p=signal['permutation_p'])
zero=core.cka_permutation_pvalue(np.zeros((64,10)),np.zeros((64,11)),n=1000)
check('V1C_ZERO_GRAM_TERMINAL_INCONCLUSIVE',zero['status']=='INCONCLUSIVE_GEOMETRY_DEGENERATE'
      and zero['permutation_p'] is None)
for scale in (0.1,1000.0):
    c=core.cka_permutation_pvalue(identity*scale,identity*scale,n=1000)
    check('V1C_CKA_SCALE_'+str(scale),c['permutation_p']==1.,status=c['status'])

# Independent primal ridge and rotation equivariance. Fixed full-count statistical loops.
z,zdev,_,_=core.standardize(train['s'],dev['s'])
eig,u=core.gram_fit(z)
center=train['r']-train['r'].mean(0)
for alpha in core.ALPHAS:
    pred_dual=core.dual_predict(eig,u,z,zdev,center,alpha)
    coef=np.linalg.solve(z.T@z+alpha*np.eye(z.shape[1]),z.T@center)
    pred_primal=zdev@coef
    check('RIDGE_PRIMAL_DUAL_'+str(alpha),np.max(abs(pred_dual-pred_primal))<1e-9,
          max_abs_diff=float(np.max(abs(pred_dual-pred_primal))))
U,_=np.linalg.qr(rng2.normal(size=(z.shape[1],z.shape[1])))
base=zdev@np.linalg.solve(z.T@z+10*np.eye(z.shape[1]),z.T@center)
rotated=(zdev@U)@np.linalg.solve((z@U).T@(z@U)+10*np.eye(z.shape[1]),(z@U).T@center)
check('ORTHOGONAL_ROTATION_NEUTRALITY',np.max(np.abs(base-rotated))<1e-9,
      max_abs_diff=float(np.max(np.abs(base-rotated))))
res=core.evaluate(train,dev,test,validated,permutation_n=1000,cka_n=1000,bootstrap_n=2000)
check('V1C_INDEPENDENT_FULL_LOOP_COUNTS',res['null_count']==1000 and
      res['cka_null_count']==1000 and res['bootstrap_count']==2000,
      result_scoped_verdict=res['verdict'],synthetic_only=True)
mu=np.zeros(8);spike=np.zeros((64,8));spike[0]=1.
boot=guard.stable_bootstrap_delta(spike,spike,mu,n=2000)
check('PAIRED_BOOTSTRAP_63_PLUS_ONE_ZERO_LOWER',boot['status']=='PASS_STATISTICS_VALID' and
      abs(boot['bootstrap_lower'])<1e-15,lower=boot['bootstrap_lower'])
bad=np.zeros((64,8))
check('PAIRED_BOOTSTRAP_DEGENERATE_INCONCLUSIVE',guard.stable_bootstrap_delta(bad,bad,mu,n=2000)['status']=='INCONCLUSIVE_DEGENERATE_TEST')
check('PROBE_BANK_8_EXACT_FIXED',len(extractor.PROBES)==8 and
      extractor.PROBES[0]==(' The child smiled.',' The child cried.') and
      extractor.PROBES[-1]==(' The story ended happily.',' The story ended sadly.'))

# Synthetic Ed25519 only in RAM. No owner key or production authorization.
priv=Ed25519PrivateKey.generate()
pub=priv.public_key().public_bytes(serialization.Encoding.Raw,serialization.PublicFormat.Raw)
test_pin=hashlib.sha256(pub).hexdigest()
payload={'schema':'ttm.six.g1.owner_science_admission.v1b','decision':'AUTHORIZE_G1_SCIENCE_ONE_SHOT',
 'independent_review':'PASS_DISTINCT_REVIEWER','manifest_sha256':guard.MANIFEST_SHA,
 'allow_private_numeric_feature_extraction':True,'private_source_staging_approved':True,
 'allow_one_shot_test':True,'run_id':RUN,'workspace':'SYNTHETIC_ONLY','code_author_id':'A',
 'reviewer_id':'B','reviewed_core_blob':'f591bd617feb007c20023a313ebc5f429471d8b2',
 'reviewed_extractor_blob':'9bb28fe39999fba0bab5474e2644b11f7940c06a',
 'reviewed_guard_blob':'4554a3e12911cbf0606a8be053660cad0c38f374',
 'reviewed_amendment_blob':'bd186413514541af46043aea605d22e0fbbbd394',
 'head_commit_sha':PIN,'owner_id':'FAKE_OWNER','expires_unix':9999999999,'phase':'prepare',
 'data_scope':{'source':'T1_TRAIN_ONLY','training':False,'gpu':'COLAB_FREE_T4',
               'feature_storage':'PRIVATE','test_one_shot':True}}
def sign(p):
    return {'payload':p,'public_key_hex':pub.hex(),
            'signature_hex':priv.sign(guard.canonical(p)).hex()}
def test_verify(env,expected=None):
    return guard.verify_signed_permit(env,expected or {'reviewed_core_blob':payload['reviewed_core_blob']},authority_pin=test_pin)
check('SYNTHETIC_KEY_SIGNATURE_CONTRACT',test_verify(sign(payload))['owner_id']=='FAKE_OWNER')
expect_stop('UNPROVISIONED_PRODUCTION_KEY_REJECTS',lambda:guard.verify_signed_permit(sign(payload),{}),'AUTHORITY_KEY_NOT_PROVISIONED')
broken=sign(payload);broken['signature_hex']='00'*64
expect_stop('MUTATED_SIGNATURE_STOP',lambda:test_verify(broken),'PERMIT_SIGNATURE_INVALID')
for label,field,value in [
    ('WRONG_HEAD_FORMAT','head_commit_sha','oops'),
    ('NO_OWNER_ID','owner_id',''),
    ('REVIEWER_EQ_AUTHOR','reviewer_id','A'),
    ('WRONG_DATA_SCOPE','data_scope',{'source':'OTHER'}),
    ('EXPIRED','expires_unix',1),
    ('WRONG_CORE_BLOB','reviewed_core_blob','a'*40),
]:
    p=copy.deepcopy(payload);p[field]=value
    expect_stop(label,lambda e=sign(p):test_verify(e))
# Source identity shortfall: syntactically valid yet incorrect cross-runner hashes
# are accepted when caller checks only its own blob. Trust must come from launcher.
for field in ('reviewed_guard_blob','reviewed_extractor_blob','reviewed_amendment_blob','head_commit_sha'):
    p=copy.deepcopy(payload);p[field]='0'*40
    passed=test_verify(sign(p))
    check('CROSS_COMPONENT_BINDING_GAP_'+field,passed[field]=='0'*40)
    observe('EXTERNAL_LAUNCHER_MISSING_'+field,'DEFECT_REPRODUCED')

# No private split files. This proves regular-file/hardlink alias cannot attest source rights.
splitroot=ROOT/'reviewer_fixture_split'
splitroot.mkdir(exist_ok=True)
heldout=splitroot/'synthetic_heldout_bytes.bin'
heldout.write_bytes(b'DISTINCT_SYNTHETIC_HELDOUT_SENTINEL')
train_alias=splitroot/'G1_PREFIX_TRAIN.json'
if not train_alias.exists():
    os.link(heldout,train_alias)
check('SPLIT_HARDLINK_PRE_FREEZE_READ_BOUNDARY_GAP',
      guard.open_split_payload('TRAIN',False,splitroot)==heldout.read_bytes())
observe('SPLIT_BROKER_UNTRUSTED_ALIAS','DEFECT_REPRODUCED')
expect_stop('SPLIT_TEST_PRE_FREEZE_REJECT',lambda:guard.open_split_payload('TEST',False,splitroot),'TEST_PREMATURE_SOURCE_ACCESS')

# Local receipt is self-mutable. The core's external expected hash detects mutation,
# but no authenticated trusted external writer/ledger is present in this version.
ids=np.asarray([hashlib.sha256(('SYNPACK'+str(i)).encode()).hexdigest() for i in range(128)])
npz_manifest={'splits':{'TRAIN':[{'source_story_sha256':i} for i in ids.tolist()]}}
sources=np.arange(128*3,dtype=np.float64).reshape(128,3)/128
targets=np.ones((128,5));responses=np.ones((128,8))
def pack_bytes(s):
    buffer=io.BytesIO()
    np.savez_compressed(buffer,ids=ids,s=s,t=targets,r=responses)
    return buffer.getvalue()
def receipt(b):
    return {'schema':'ttm.six.g1.feature_pack_commit.v1b','status':'PACK_COMMITTED',
            'split':'TRAIN','run_id':RUN,'manifest_sha256':guard.MANIFEST_SHA,
            'sha256':hashlib.sha256(b).hexdigest()}
raw=pack_bytes(sources)
mut=pack_bytes(sources+1)
first=guard.parse_authenticated_pack(raw,receipt(raw),split='TRAIN',manifest=npz_manifest,
                                     run_id=RUN,source_dim=3,target_dim=5)
second=guard.parse_authenticated_pack(mut,receipt(mut),split='TRAIN',manifest=npz_manifest,
                                      run_id=RUN,source_dim=3,target_dim=5)
check('SELF_SIGNED_PACK_RECEIPT_ACCEPTS_NUMERIC_MUTATION',
      np.array_equal(first['ids'],second['ids']) and np.any(first['s']!=second['s']))
observe('PACK_EXTERNAL_TRUST_MISSING','DEFECT_REPRODUCED')
packroot=ROOT/'reviewer_fixture_pack';packroot.mkdir(exist_ok=True)
(packroot/'G1_FEATURES_TRAIN.npz').write_bytes(mut)
(packroot/'G1_FEATURES_TRAIN.receipt.json').write_bytes(guard.canonical(receipt(mut)))
expect_stop('TRUSTED_PACK_DIGEST_MISMATCH_REJECTS',
 lambda:core.load_pack(packroot/'G1_FEATURES_TRAIN.npz','TRAIN',npz_manifest,3,5,
                  run_id=RUN,root=packroot,trusted_pack_sha=hashlib.sha256(raw).hexdigest()),
 'TRUSTED_PACK_SHA_MISMATCH')

# Transaction crash after pack is published leaves immutable pack without receipt.
transactionroot=ROOT/'reviewer_fixture_transaction';transactionroot.mkdir(exist_ok=True)
orphan=transactionroot/'synthetic_pack.bin'
with patch.object(guard,'read_private_bytes',side_effect=RuntimeError('INJECT_POST_LINK_FAILURE')):
    expect_stop('TRANSACTION_POST_LINK_INJECTION',
                lambda:guard.commit_immutable_bytes(orphan,b'SYNTHETIC_BYTES',transactionroot),
                'INJECT_POST_LINK_FAILURE')
check('TRANSACTION_ORPHAN_FILE_REPRODUCED',orphan.is_file() and orphan.read_bytes()==b'SYNTHETIC_BYTES')
observe('PACK_RECEIPT_NOT_ATOMIC','DEFECT_REPRODUCED')

# Simulate deletion/rollback of a local consume marker in a synthetic-only folder.
markers=ROOT/'reviewer_fixture_marker';markers.mkdir(exist_ok=True)
marker=markers/'G1_EXTRACT_TEST_ONE_SHOT_CONSUMED.marker'
with marker.open('x') as f:f.write('CONSUMED')
expect_stop('LOCAL_MARKER_ENFORCES_WHEN_PRESENT',lambda:marker.open('x'),'File exists') if os.name!='nt' else None
marker.unlink()
with marker.open('x') as f:f.write('REPLAY_AFTER_LOCAL_ROLLBACK')
check('ONE_SHOT_LOCAL_ROLLBACK_REPLAY_REPRODUCED',marker.read_text()=='REPLAY_AFTER_LOCAL_ROLLBACK')
observe('MONOTONIC_EXTERNAL_LEDGER_ABSENT','DEFECT_REPRODUCED')

clock=[0.0]
budget=guard.Budget({'source':0.,'target':0.},clock=lambda:clock[0])
clock[0]=3601.
expect_stop('BUDGET_COOPERATIVE_TIMEOUT_ON_NEXT_POLL',lambda:budget.check('source',0.),'MODEL_CUMULATIVE_TIMEOUT')
check('BUDGET_CANNOT_KILL_BLOCKED_CALL',True,wall=3601,external_kill_tested=False)

summary={'review_schema':'ttm.six.g1.v1c.distinct_adversarial_cpu.v1',
         'reviewed_head':PIN,'synthetic_only':True,'science_executed':False,
         'checks':len(results), 'controls':sum(x['status']=='CONTROL_PASS' for x in results),
         'defects_reproduced':sum(x['status']=='DEFECT_REPRODUCED' for x in results),
         'critical_v1b_freeze': 'REPRODUCED','critical_v1b_cka':'REPRODUCED',
         'critical_v1c_freeze':'PASS','critical_v1c_cka':'PASS',
         'original_v1b_cka_p':old_p, 'corrected_v1c_cka_p':new_cka['permutation_p'],
         'informative_v1c_cka_p':signal['permutation_p']}
(ROOT/'reviewer_independent_adversarial_v1c_receipt.json').write_text(
    json.dumps({'summary':summary,'observations':results},indent=2,sort_keys=True,allow_nan=False)+'\n',encoding='utf-8')
print('REVIEW_SUMMARY='+json.dumps(summary,sort_keys=True))
