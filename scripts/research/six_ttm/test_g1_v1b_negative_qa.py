#!/usr/bin/env python3
"""CPU-only adversarial QA of G1 v1b. No TinyStories or Qwen model."""
from __future__ import annotations
import hashlib, io, json, os, sys, tempfile, time, zipfile
from pathlib import Path
import numpy as np
import g1_science_guard_v1b as guard
import g1_science_core_v1b as core
import g1_science_private_feature_extractor_v1b as extractor
from cryptography.hazmat.primitives.asymmetric.ed25519 import Ed25519PrivateKey
from cryptography.hazmat.primitives import serialization

PASS=[]
def ok(label):PASS.append(label)
def expect(code, fn):
    try:fn()
    except (RuntimeError, FileExistsError) as exc:
        assert code in str(exc) or (code=='FileExistsError' and isinstance(exc,FileExistsError)),(code,str(exc))
    else:raise AssertionError('NEGATIVE_TEST_NOT_REJECTED '+code)
    ok(code)

# Before any registration production must refuse all self-declared approvals.
expect('AUTHORITY_KEY_NOT_PROVISIONED',lambda:guard.verify_signed_permit({'payload':{'owner_authorized':True}},{}))
key=Ed25519PrivateKey.generate();pub=key.public_key().public_bytes(
    encoding=serialization.Encoding.Raw,format=serialization.PublicFormat.Raw)
pin=hashlib.sha256(pub).hexdigest()
base={'schema':'ttm.six.g1.owner_science_admission.v1b',
      'decision':'AUTHORIZE_G1_SCIENCE_ONE_SHOT','independent_review':'PASS_DISTINCT_REVIEWER',
      'manifest_sha256':guard.MANIFEST_SHA,'allow_private_numeric_feature_extraction':True,
      'private_source_staging_approved':True,'allow_one_shot_test':True,
      'run_id':'g1-synthetic','workspace':'synthetic-only','code_author_id':'author',
      'reviewer_id':'reviewer','reviewed_core_blob':'a'*40,'reviewed_extractor_blob':'b'*40,
      'reviewed_amendment_blob':'c'*40,'owner_id':'owner','expires_unix':int(time.time()+600)}
def envelope(body):
    return {'payload':body,'public_key_hex':pub.hex(),
            'signature_hex':key.sign(guard.canonical(body)).hex()}
signed=envelope(base)
assert guard.verify_signed_permit(signed,{'run_id':'g1-synthetic'},authority_pin=pin)['owner_id']=='owner';ok('VALID_TEST_AUTHORITY')
for field,val in [('owner_id','forged'),('code_author_id','reviewer'),('run_id','other')]:
    wrong=dict(base);wrong[field]=val
    if field=='code_author_id':
        expect('PERMIT_NOT_DISTINCT',lambda wrong=wrong:guard.verify_signed_permit(envelope(wrong),{},authority_pin=pin))
    elif field=='run_id':
        expect('PERMIT_FIELD_RUN_ID',lambda wrong=wrong:guard.verify_signed_permit(envelope(wrong),{'run_id':'g1-synthetic'},authority_pin=pin))
    else:
        altered=dict(signed);altered['payload']=wrong
        expect('PERMIT_SIGNATURE_INVALID',lambda altered=altered:guard.verify_signed_permit(altered,{},authority_pin=pin))
wrong=dict(base);wrong.pop('code_author_id')
expect('PERMIT_IDENTITY_OR_PIN_MISSING',lambda:guard.verify_signed_permit(envelope(wrong),{},authority_pin=pin))
wrong=dict(base);wrong['expires_unix']=1
expect('PERMIT_EXPIRED',lambda:guard.verify_signed_permit(envelope(wrong),{},authority_pin=pin))

with tempfile.TemporaryDirectory() as td:
    root=Path(td);split=root/'private_split_inputs';split.mkdir()
    # No raw global source in extract v1b; old 'reconstruct' takes split path only.
    assert 'TinyStories-train.txt' not in extractor.reconstruct.__code__.co_consts
    expect('TEST_PREMATURE_SOURCE_ACCESS',lambda:guard.open_split_payload('TEST',False,split))
    (split/'G1_PREFIX_TRAIN.json').write_text('{}')
    assert guard.open_split_payload('TRAIN',False,split)==b'{}';ok('TRAIN_SPLIT_ONLY')
    # A private TEST file must remain untouched by TRAIN/DEV routines.
    (split/'G1_PREFIX_TEST.json').write_bytes(b'test sentinel bytes')
    assert guard.open_split_payload('TRAIN',False,split)==b'{}';ok('TEST_BYTES_NOT_OPENED_IN_PREP')
    assert guard.open_split_payload('TEST',True,split)==b'test sentinel bytes';ok('TEST_RELEASED_ONLY_AFTER_FREEZE')
    (split/'G1_PREFIX_DEV.json').symlink_to(root/'G1_PREFIX_TEST.json')
    expect('PATH_SYMLINK',lambda:guard.open_split_payload('DEV',False,split))
    # Nested directory redirects must be checked, not just the leaf symlink.
    nested=split/'nested'; nested.symlink_to(root,target_is_directory=True)
    expect('PATH_SYMLINK',lambda:guard.ensure_regular_no_redirect(nested/'G1_PREFIX_TEST.json',split))
    expect('PATH_SYMLINK',lambda:guard.read_private_bytes(nested/'G1_PREFIX_TEST.json',split))
    marker=root/'G1_TEST_READ_ONE_SHOT_CONSUMED.marker'
    with marker.open('x') as fd:fd.write('CONSUMED')
    expect('FileExistsError',lambda:marker.open('x'))
    extractor_code=Path(extractor.__file__).read_text()
    marker_ix=extractor_code.index("with marker.open('x',encoding='utf-8')")
    prefix_ix=extractor_code.index('inputs=reconstruct(manifest,split,split_root')
    assert marker_ix < prefix_ix;ok('TEST_EXTRACT_MARKER_BEFORE_PREFIX_READ')
    committed=root/'unique-committed.bin'
    digest=guard.commit_immutable_bytes(committed,b'complete-content',root)
    assert digest==guard.sha_bytes(b'complete-content') and committed.read_bytes()==b'complete-content';ok('ATOMIC_COMMIT_FULL_BYTES')
    expect('COMMIT_TARGET_EXISTS',lambda:guard.commit_immutable_bytes(committed,b'substitution',root))
    assert committed.read_bytes()==b'complete-content';ok('ATOMIC_COMMIT_NO_OVERWRITE')
    # Freeze must contain structured selection, never a 0-byte presence-only gate.
    freeze={'schema':'ttm.six.g1.fit_dev_frozen_v1b',
            'manifest_sha256':guard.MANIFEST_SHA,'run_id':'g1-synthetic',
            'train_pack_sha256':'1'*64,'dev_pack_sha256':'2'*64,
            'test_touched':False,'null_count':1000,'primary_layer':28,'function_count':8,
            'aligned_alpha':10.,'direct_alpha':1.,'target_probe_alpha':100.,
            'null_alphas':[1.]*1000,'null_permutation_sha256':'3'*64}
    b=guard.canonical(freeze)
    assert guard.validate_frozen_dev(b,guard.sha_bytes(b),'1'*64,'2'*64,run_id='g1-synthetic')['null_count']==1000
    ok('VALID_FULL_FREEZE')
    expect('FIT_DEV_HASH_CHANGED',lambda:guard.validate_frozen_dev(b,'0'*64,'1'*64,'2'*64,run_id='g1-synthetic'))
    expect('FIT_DEV_JSON_INVALID',lambda:guard.validate_frozen_dev(b'',guard.sha_bytes(b''),'1'*64,'2'*64,run_id='g1-synthetic'))
    stale=dict(freeze);stale['run_id']='old'
    expect('FIT_DEV_FIELD_RUN_ID',lambda:guard.validate_frozen_dev(guard.canonical(stale),guard.sha_bytes(guard.canonical(stale)),'1'*64,'2'*64,run_id='g1-synthetic'))
    bad=dict(freeze);bad['null_alphas']=[1.]*999
    expect('FIT_DEV_NULL_GRID',lambda:guard.validate_frozen_dev(guard.canonical(bad),guard.sha_bytes(guard.canonical(bad)),'1'*64,'2'*64,run_id='g1-synthetic'))
    # Same IDs with different tensor bytes must be rejected: parse same bytes hashed.
    rng=np.random.default_rng(0);ids=[hashlib.sha256(f'id-{i}'.encode()).hexdigest() for i in range(128)]
    manifest={'splits':{'TRAIN':[{'source_story_sha256':z} for z in ids]}}
    s=rng.normal(size=(128,1024)).astype('float32');t=rng.normal(size=(128,2048)).astype('float32')
    r=rng.normal(size=(128,8)).astype('float64')
    def pack(tensor):
        out=io.BytesIO();np.savez_compressed(out,ids=np.array(ids,dtype='<U64'),s=s,t=tensor,r=r)
        return out.getvalue()
    raw=pack(t)
    rec={'schema':'ttm.six.g1.feature_pack_commit.v1b','status':'PACK_COMMITTED',
         'run_id':'g1-synthetic','split':'TRAIN','manifest_sha256':guard.MANIFEST_SHA,
         'sha256':guard.sha_bytes(raw)}
    got=guard.parse_authenticated_pack(raw,rec,split='TRAIN',manifest=manifest,run_id='g1-synthetic')
    assert got['t'].shape==(128,2048);ok('VALID_PRIVATE_PACK')
    modified=t.copy();modified[0,0]+=1.
    expect('PACK_RECEIPT_SHA256',lambda:guard.parse_authenticated_pack(pack(modified),rec,split='TRAIN',manifest=manifest,run_id='g1-synthetic'))
    bad=dict(rec);bad['run_id']='different'
    expect('PACK_RECEIPT_RUN_ID',lambda:guard.parse_authenticated_pack(raw,bad,split='TRAIN',manifest=manifest,run_id='g1-synthetic'))
    bad=dict(rec);bad['status']='IN_PROGRESS'
    expect('PACK_NOT_COMMITTED',lambda:guard.parse_authenticated_pack(raw,bad,split='TRAIN',manifest=manifest,run_id='g1-synthetic'))
    # Wrong content-ID order is rejected even when the pack receipt describes its exact bytes.
    reversed_manifest={'splits':{'TRAIN':list(reversed(manifest['splits']['TRAIN']))}}
    expect('PACK_MANIFEST_IDS_CHANGED',lambda:guard.parse_authenticated_pack(raw,rec,split='TRAIN',manifest=reversed_manifest,run_id='g1-synthetic'))
    corrupt=io.BytesIO()
    with zipfile.ZipFile(corrupt,'w',zipfile.ZIP_DEFLATED) as z:
        z.writestr('ids.npy',b'\x93NUMPY\x01\x00\x00\x00')
        for name in ['s.npy','t.npy','r.npy']:z.writestr(name,b'garbage')
    bogus=corrupt.getvalue();rec_corrupt={**rec,'sha256':guard.sha_bytes(bogus)}
    expect('PACK_HEADER_SIZE',lambda:guard.parse_authenticated_pack(bogus,rec_corrupt,split='TRAIN',manifest=manifest,run_id='g1-synthetic'))

# Exact Codex 63+1 problem: whole TEST denominator > threshold, bootstrap resamples
# that omit the only nonzero story must still be finite (no sample denominator).
pred=np.zeros((64,8));truth=np.zeros((64,8));truth[-1,:]=1.;mean=np.zeros(8)
bt=guard.stable_bootstrap_delta(pred,truth,mean,n=2000)
assert bt['status']=='PASS_STATISTICS_VALID' and np.isfinite(bt['bootstrap_lower'])
ok('BOOTSTRAP_63_PLUS_1_NONDEGENERATE')
assert guard.stable_bootstrap_delta(pred,np.zeros((64,8)),mean)['status']=='INCONCLUSIVE_DEGENERATE_TEST'
ok('FULL_TEST_SST_TERMINAL')
assert guard.safe_cka(np.ones((64,4)),np.ones((64,5)))['status']=='INCONCLUSIVE_GEOMETRY_DEGENERATE'
ok('ZERO_VARIANCE_CKA_TERMINAL')

class Clock:
    x=0.
    def now(self):return self.x
clock=Clock();budget=guard.Budget({'source':3590.,'target':0.},clock=clock.now)
began=clock.now();clock.x=11.
expect('MODEL_CUMULATIVE_TIMEOUT',lambda:budget.check('source',began))
clock.x=0.;budget=guard.Budget({'source':3600.,'target':3595.},clock=clock.now)
began=clock.now();clock.x=6.
expect('MODEL_CUMULATIVE_TIMEOUT',lambda:budget.check('target',began))
expect('BUDGET_PREVIOUS_OVERRUN',lambda:guard.Budget({'source':3601.,'target':3600.},clock=clock.now))
# Synthetic core QA is a separate check, not evidence of scientific inference.
ans=core.synthetic_qa();assert ans['status']=='PASS_SYNTHETIC_ONLY_NO_SCIENCE';ok('CORE_SYNTHETIC_NO_SCIENCE')
assert core.choose_alpha([(1,0.5),(10,0.5),(100,0.5)])==100.;ok('TIE_LARGER_ALPHA')
print(json.dumps({'status':'PASS_G1_V1B_ADVERSARIAL_CPU_ONLY','checks':len(PASS),
                  'checks_run':PASS,'private_TinyStories_read':False,
                  'qwen_download':False,'science_executed':False},sort_keys=True))
