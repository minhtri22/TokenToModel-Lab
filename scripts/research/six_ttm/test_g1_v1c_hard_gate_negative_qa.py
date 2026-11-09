#!/usr/bin/env python3
"""Synthetic-only hard-gate negatives for v1c: no model, corpus, or science."""
from __future__ import annotations
import hashlib, json, os, tempfile, time
from pathlib import Path
from unittest.mock import patch
from cryptography.hazmat.primitives.asymmetric.ed25519 import Ed25519PrivateKey
from cryptography.hazmat.primitives import serialization
import g1_science_guard_v1c as g

passed=[]
def rejected(code, fn):
    try:fn()
    except RuntimeError as exc:
        assert code in str(exc), (code,str(exc))
        passed.append(code)
    else:raise AssertionError('FALSE_ACCEPT '+code)

# Complete owner envelope (synthetic key in RAM only); production key remains None.
key=Ed25519PrivateKey.generate()
pub=key.public_key().public_bytes(serialization.Encoding.Raw,serialization.PublicFormat.Raw)
pin=hashlib.sha256(pub).hexdigest()
payload={
 'schema':'ttm.six.g1.owner_science_admission.v1b',
 'decision':'AUTHORIZE_G1_SCIENCE_ONE_SHOT',
 'independent_review':'PASS_DISTINCT_REVIEWER',
 'manifest_sha256':g.MANIFEST_SHA,
 'allow_private_numeric_feature_extraction':True,
 'private_source_staging_approved':True,
 'allow_one_shot_test':True,
 'run_id':'fake-case', 'workspace':'fake-private-root',
 'phase':'prepare','code_author_id':'a','reviewer_id':'r',
 'reviewed_core_blob':'a'*40,
 'reviewed_extractor_blob':'b'*40,
 'reviewed_guard_blob':'c'*40,
 'reviewed_amendment_blob':'d'*40,
 'head_commit_sha':'e'*40,
 'data_scope':{'source':'T1_TRAIN_ONLY','training':False,'gpu':'COLAB_FREE_T4',
               'feature_storage':'PRIVATE','test_one_shot':True},
 'owner_id':'owner','expires_unix':int(time.time()+1800)
}
def envelope(value):
    return {'payload':value,'public_key_hex':pub.hex(),
            'signature_hex':key.sign(g.canonical(value)).hex()}
require={'run_id':'fake-case','phase':'prepare','reviewed_guard_blob':'c'*40}
assert g.verify_signed_permit(envelope(payload),require,authority_pin=pin)['owner_id']=='owner'
passed.append('TEST_KEY_ONLY_PROVES_SIGNATURE_CONTRACT')
rejected('AUTHORITY_KEY_NOT_PROVISIONED',lambda:g.verify_signed_permit(envelope(payload),require))
for dropped in ('head_commit_sha','reviewed_guard_blob','data_scope','reviewed_amendment_blob'):
    changed=dict(payload);changed.pop(dropped)
    reason=('PERMIT_FIELD_REVIEWED_GUARD_BLOB' if dropped=='reviewed_guard_blob' else 'PERMIT_IDENTITY_OR_PIN_MISSING')
    rejected(reason,lambda changed=changed:g.verify_signed_permit(envelope(changed),require,authority_pin=pin))
changed=dict(payload);changed['data_scope']=dict(payload['data_scope'],test_one_shot=False)
rejected('PERMIT_DATA_SCOPE',lambda:g.verify_signed_permit(envelope(changed),require,authority_pin=pin))

# Construct the exact core's freeze schema with full seed/scores.
freeze={
 'schema':'ttm.six.g1.fit_dev_frozen_v1b','manifest_sha256':g.MANIFEST_SHA,
 'run_id':'fake-case','train_pack_sha256':'1'*64,'dev_pack_sha256':'2'*64,
 'test_touched':False,'null_count':1000,'primary_layer':28,'function_count':8,
 'seed_shuffle':20261110,'seed_cka':20261110,'seed_boot':20261111,
 'aligned_alpha':10.0,'direct_alpha':10.0,'target_probe_alpha':10.0,
 'null_alphas':[10.0]*1000,'null_permutation_sha256':'f'*64,
 'control_oracle_dev_macro_r2':0.11,'direct_dev_macro_r2':0.12,
 'aligned_dev_macro_r2':0.13
}
def check(v):
    data=g.canonical(v)
    return g.validate_frozen_dev(data,g.sha_bytes(data),'1'*64,'2'*64,run_id='fake-case')
assert check(freeze)==freeze
passed.append('COMPLETE_FREEZE_PASS')
for drop in ('seed_shuffle','seed_cka','seed_boot','control_oracle_dev_macro_r2'):
    changed=dict(freeze);changed.pop(drop)
    rejected('FIT_DEV_FIELD_',lambda changed=changed:check(changed)) if drop.startswith('seed') else rejected('FIT_DEV_KEYSET_',lambda changed=changed:check(changed))
changed=dict(freeze);changed['null_alphas']=[True]*1000
rejected('FIT_DEV_NULL_GRID',lambda:check(changed))
changed=dict(freeze);changed['null_permutation_sha256']='?'*64
rejected('FIT_DEV_SHA_FORMAT_',lambda:check(changed))
changed=dict(freeze);changed['direct_dev_macro_r2']=float('nan')
try:check(changed)
except (RuntimeError,ValueError) as e:
    assert ('FIT_DEV_DEV_SCORE_INVALID' in str(e) or 'nan' in str(e).lower())
    passed.append('NONFINITE_SCORE_STOP')
else:raise AssertionError('NONFINITE_ACCEPTED')

rejected('BUDGET_LEDGER_REQUIRED',lambda:g.Budget({}))
rejected('BUDGET_LEDGER_REQUIRED',lambda:g.Budget({'source':0}))
rejected('BUDGET_BAD_LEDGER',lambda:g.Budget({'source':False,'target':0}))
assert g.Budget({'source':0,'target':0})
passed.append('BUDGET_FULL_LEDGER_PASS')

with tempfile.TemporaryDirectory() as td:
    root=Path(td);target=root/'target';target.mkdir()
    (target/'data').write_bytes(b'sentinel')
    link=root/'redirect';link.symlink_to(target,target_is_directory=True)
    rejected('COMMIT_ROOT_REDIRECT',lambda:g.commit_immutable_bytes(link/'new',b'x',link))
    assert not (target/'new').exists()
    passed.append('NO_WRITE_BEFORE_ROOT_REDIRECT_STOP')
    # Race: path looked safe, but returned file handle targets a different inode.
    valid=root/'valid';valid.write_bytes(b'expected')
    alternate=root/'alternate';alternate.write_bytes(b'wrong')
    saved_open=os.open
    def hostile_open(path,flags):
        return saved_open(str(alternate),flags)
    with patch.object(g.os,'open',hostile_open):
        rejected('PACK_OPEN_IDENTITY_CHANGED',lambda:g.read_private_bytes(valid,root))

print(json.dumps({'status':'PASS_V1C_HARD_GATE_NEGATIVE_QA_NO_SCIENCE',
    'checks':len(passed),'items':passed,'science_executed':False},sort_keys=True))
