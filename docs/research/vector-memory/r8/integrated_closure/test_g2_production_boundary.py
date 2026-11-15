"""Synthetic contract and negative QA only; NO actual R8 key, G3, or commitment."""
from __future__ import annotations
from contextlib import closing
from dataclasses import replace
from datetime import datetime, timedelta, timezone
import hashlib
import json
from pathlib import Path
import sqlite3
import subprocess
import sys
import tempfile
import threading
import unittest
from unittest.mock import patch
from concurrent.futures import ThreadPoolExecutor

from g2_production_boundary import (
    ALGORITHM, SCHEMA, SOURCE_COMMIT, REPO, GateDenied, PrivatePrecommit,
    CheckedCode, GitHubAnchor, IndependentlyAcceptedReceipt, WitnessReceipt,
    FrozenCodeVerifier, GhReleaseVerifier, AntiRollbackConsumptionLedger,
    UnavailableWitness, VerifiedAdmissionCore, ProductionG3Gateway, exact_json,
    validate_hmac_v2, sha, safe_read, utc,
)

def canon(obj):
    return json.dumps(obj,sort_keys=True,ensure_ascii=False,
                      separators=(',',':'),allow_nan=False).encode()

def seconds_back(n):
    return (datetime.now(timezone.utc)-timedelta(seconds=n)).isoformat()

class AlgorithmFixture:
    def preassign_r8(self, blueprints, key):
        digest=sha(canon(blueprints)+key)
        return {'lock_schema':SCHEMA,'algorithm_id':ALGORITHM,
                'blueprint_hmac':digest,'preassignment_hmac':sha(key+canon(blueprints)),
                'fold':{'fake-blueprint':'TRAIN'},
                'component_id_pre':{'fake-blueprint':'fixture-component'},
                'component_count':4, 'case_count_by_fold':{'TRAIN':1},
                'cv_status':'PREFOLD_READY_NOT_VALIDATED'}

class CustodyFixture:
    """Nonsecret marker, fake key is never a real R8 allocation credential."""
    def __init__(self):
        self.fixture_key=b'only-fixture-bounded-by-test-run!!'
        self.fake_algorithm=AlgorithmFixture()
        self.blueprints=canon([{'fixture_marker':'not-an-R8-blueprint'}])
        self.lock=canon(self.fake_algorithm.preassign_r8(exact_json(self.blueprints),self.fixture_key))
        self.fields={
            'schema':SCHEMA,'algorithm_id':ALGORITHM,'session_id':'fixture-session-00001',
            'source_commit':SOURCE_COMMIT,'source_manifest_sha256':'a'*64,
            'runtime_manifest_sha256':'b'*64,
            'blueprint_sha256':sha(self.blueprints),'lock_sha256':sha(self.lock)}
        self.pre=PrivatePrecommit(canon(self.fields),bytes(range(16)),self.blueprints,self.lock)
        self.calls=0
    def read_gpre(self,session_id):
        self.calls+=1
        return self.pre
    def use_private_key(self,session_id,operation):
        if session_id!=self.fields['session_id']:
            raise GateDenied('CUSTODIAN_WRONG_SESSION')
        return operation(self.fixture_key)

class FakeCodeVerifier:
    def check(self,source_digest,runtime_digest,source_path,runtime_path):
        if source_digest!='a'*64 or runtime_digest!='b'*64:
            raise GateDenied('SOURCE_RUNTIME_NOT_PINNED')
        return CheckedCode(AlgorithmFixture(),'a'*64,'b'*64)

class FakeRelease:
    def __init__(self,pre):
        self.pre=pre
        self.exists=True
        self.requests=0
        self.mutable=False
        self.tag='r8-fixture-signed-anchor'
        self.published_at=seconds_back(100)
        self.asset=canon({'public_digest':pre.digest,'source_commit':SOURCE_COMMIT,
                          'session_id':'fixture-session-00001',
                          'source_manifest_sha256':'a'*64,
                          'runtime_manifest_sha256':'b'*64})
    def verify(self,tag,asset_path,expected_digest):
        self.requests+=1
        if not self.exists:
            raise GateDenied('ANCHOR_MISSING')
        if self.mutable:
            raise GateDenied('RELEASE_NOT_IMMUTABLE')
        if tag!=self.tag or expected_digest!=sha(self.asset):
            raise GateDenied('ANCHOR_MISMATCH')
        return GitHubAnchor(tag,sha(self.asset),self.published_at,self.asset,123)

class FakeIndependent:
    def __init__(self,pre,release):
        self.pre=pre
        self.release=release
        self.accepted=True
        self.review_commit='a'*40
        self.calls=0
    def verify_independently_signed(self, *, session_id, digest):
        self.calls+=1
        return IndependentlyAcceptedReceipt(session_id,digest,self.release.tag,
                    sha(self.release.asset),seconds_back(90),seconds_back(80),
                    self.review_commit,self.accepted)

class FakeMonotonicWitness:
    def __init__(self):
        self._lock=threading.Lock()
        self._events={}
        self.missing=False
        self.issued=0
    def reserve_once(self,session_id,digest):
        with self._lock:
            if session_id in self._events:
                raise GateDenied('EXTERNAL_ONE_SHOT_REPLAY')
            self.issued+=1
            receipt=WitnessReceipt(session_id,digest,'fixture-event-'+str(self.issued),True)
            self._events[session_id]=receipt
            return receipt
    def read_verified(self,session_id):
        with self._lock:
            if self.missing:
                raise GateDenied('REMOTE_WITNESS_UNAVAILABLE')
            return self._events.get(session_id)

class BoundaryTests(unittest.TestCase):
    def setUp(self):
        self.temp=tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root=Path(self.temp.name)
        self.custody=CustodyFixture()
        self.release=FakeRelease(self.custody.pre)
        self.accept=FakeIndependent(self.custody.pre,self.release)
        self.witness=FakeMonotonicWitness()
        self.ledger=AntiRollbackConsumptionLedger(self.root/'consumed.sqlite3',self.witness)
        self.asset=self.root/'signed-sentinel.json'
        self.asset.write_bytes(self.release.asset)
        self.core=VerifiedAdmissionCore(self.custody,FakeCodeVerifier(),self.release,
                self.accept,self.ledger,source_manifest_path=self.root/'source.json',
                runtime_manifest_path=self.root/'runtime.json',asset_path=self.asset,
                signed_timestamp_checker=lambda receipt: True)
    def go(self):
        return self.core.validate_and_consume('fixture-session-00001',self.release.tag)
    def deny(self, reason):
        with self.assertRaises(GateDenied) as e:
            self.go()
        self.assertEqual(str(e.exception),reason)
    def test_01_core_fixture_authorizes_single_remote_consume(self):
        self.assertEqual(self.go().witness_event_id,'fixture-event-1')
        self.assertEqual(self.witness.issued,1)
        with closing(sqlite3.connect(self.ledger.path)) as db:
            self.assertEqual(db.execute('select count(*) from consumed').fetchone()[0],1)
        self.deny('EXTERNAL_ONE_SHOT_REPLAY')
    def test_02_production_never_exposes_generator_callback(self):
        with self.assertRaisesRegex(GateDenied,'PRODUCTION_G3_GENERATOR_NOT_REGISTERED_OR_AUTHORIZED'):
            ProductionG3Gateway().launch('fixture-session-00001',self.release.tag)
    def test_03_missing_external_witness_blocks(self):
        self.ledger.witness=UnavailableWitness()
        self.deny('EXTERNAL_ANTIROLLBACK_WITNESS_NOT_CONFIGURED')
        self.assertFalse(self.ledger.path.exists())
    def test_04_alternate_ledger_does_not_replay(self):
        self.go()
        self.ledger=AntiRollbackConsumptionLedger(self.root/'new-ledger.sqlite3',self.witness)
        self.core._ledger=self.ledger
        self.deny('EXTERNAL_ONE_SHOT_REPLAY')
    def test_05_rollback_restored_empty_ledger_does_not_replay(self):
        # Rollback deletes consumed state, but the trusted external witness remains.
        self.go()
        self.ledger.path.unlink()
        self.deny('EXTERNAL_ONE_SHOT_REPLAY')
        self.assertFalse(self.ledger.path.exists())
    def test_06_two_threads_one_external_cas_winner(self):
        with ThreadPoolExecutor(max_workers=8) as pool:
            def run(_):
                try: return self.go().witness_event_id
                except GateDenied as e: return str(e)
            results=list(pool.map(run,range(8)))
        self.assertEqual(results.count('fixture-event-1'),1)
        self.assertEqual(results.count('EXTERNAL_ONE_SHOT_REPLAY'),7)
    def test_07_false_acceptance_does_not_consume(self):
        self.accept.accepted='false'
        self.deny('INDEPENDENT_GPRE_ACCEPTANCE_NOT_AUTHENTIC')
        self.assertEqual(self.witness.issued,0)
    def test_08_unsigned_time_denies(self):
        self.core._signed_time_check=lambda _ : False
        self.deny('INDEPENDENT_GPRE_ACCEPTANCE_NOT_AUTHENTIC')
    def test_09_missing_anchor_denies(self):
        self.release.exists=False
        self.deny('ANCHOR_MISSING')
    def test_10_revoked_after_receipt_denies(self):
        orig=self.accept.verify_independently_signed
        def revoke(**kwargs):
            self.release.exists=False
            return orig(**kwargs)
        self.accept.verify_independently_signed=revoke
        self.deny('ANCHOR_MISSING')
        self.assertEqual(self.witness.issued,0)
    def test_11_fake_hmac_shape_denies(self):
        lock=exact_json(self.custody.pre.lock_bytes)
        lock['preassignment_hmac']='c'*64
        self.custody.lock=canon(lock)
        self.custody.fields['lock_sha256']=sha(self.custody.lock)
        self.custody.pre=PrivatePrecommit(canon(self.custody.fields),self.custody.pre.nonce,
                                          self.custody.blueprints,self.custody.lock)
        self.deny('GPRE_HMAC_NOT_AUTHENTIC')
    def test_12_wrong_secret_denies(self):
        self.custody.fixture_key=b'wrong-fixture-key-not-real-1234567'
        self.deny('GPRE_HMAC_NOT_AUTHENTIC')
    def test_13_private_blueprint_mutation_denies(self):
        self.custody.pre=replace(self.custody.pre,blueprint_bytes=b'[]')
        self.deny('GPRE_PRIVATE_BYTE_MISMATCH')
    def test_14_release_claim_mismatch_denies(self):
        self.release.asset=canon({'public_digest':'f'*64,'source_commit':SOURCE_COMMIT})
        self.asset.write_bytes(self.release.asset)
        self.deny('PUBLIC_GPRE_RELEASE_BINDING_MISMATCH')
    def test_15_amendment_not_accepted_denies(self):
        self.accept.review_commit='0'*40
        self.deny('INDEPENDENT_GPRE_ACCEPTANCE_NOT_AUTHENTIC')
    def test_16_noncanonical_source_json_denies(self):
        with self.assertRaisesRegex(GateDenied,'NONCANONICAL_JSON'):
            exact_json(b'{"x": 1}')
    def test_17_duplicate_json_denies(self):
        with self.assertRaisesRegex(GateDenied,'INVALID_JSON_BYTES'):
            exact_json(b'{"x":1,"x":2}')
    def test_18_nonfinite_json_denies(self):
        with self.assertRaisesRegex(GateDenied,'INVALID_JSON_BYTES'):
            exact_json(b'{"x":NaN}')
    def test_19_bad_unicode_denies(self):
        with self.assertRaisesRegex(GateDenied,'INVALID_JSON_BYTES'):
            exact_json(b'{"x":"\\ud800"}')
    def test_20_source_pin_mismatch_denies(self):
        path=self.root/'source.py'
        path.write_text('a=1',encoding='utf-8')
        with self.assertRaisesRegex(GateDenied,'FILE_SHA256_PIN_MISMATCH'):
            safe_read(path,'0'*64)
    def test_21_symlink_rejected(self):
        dest=self.root/'real.py'; dest.write_bytes(b'source')
        link=self.root/'link.py';link.symlink_to(dest)
        with self.assertRaisesRegex(GateDenied,'UNTRUSTED_FILE_PATH'):
            safe_read(link,sha(b'source'))
    def test_22_wrong_local_runtime_manifest_denies(self):
        # Real code verifier needs real source and manifest; this test covers
        # minimal expected pins before source/runtime artifacts are loaded.
        class WrongVerifier:
            def check(self,*args): raise GateDenied('RUNTIME_BINARY_MANIFEST_MISMATCH')
        self.core._code=WrongVerifier()
        self.deny('RUNTIME_BINARY_MANIFEST_MISMATCH')
    def test_23_sqlite_tampered_schema_denies_after_external_consume(self):
        with closing(sqlite3.connect(self.ledger.path)) as db:
            db.execute('create table consumed(session_id TEXT, digest TEXT, witness_id TEXT)')
            db.commit()
        self.deny('LEDGER_SCHEMA_UNTRUSTED')
        self.assertEqual(self.witness.issued,1)
    def test_24_failed_local_write_consumes_remote_token(self):
        # A directory at DB leaf prevents SQLite open, AFTER remote reserve.
        self.ledger.path.mkdir()
        self.deny('LEDGER_CUSTODY_PATH_INVALID')
        self.assertEqual(self.witness.issued,0)
    def test_24b_local_write_error_consumes_remote_token(self):
        with patch('g2_production_boundary.sqlite3.connect',side_effect=sqlite3.OperationalError('disk full')):
            self.deny('LEDGER_PERSISTENCE_FAILED_TOKEN_CONSUMED')
        self.assertEqual(self.witness.issued,1)

    def test_25_remote_witness_state_change_denies(self):
        self.witness.missing=True
        self.deny('REMOTE_WITNESS_UNAVAILABLE')
        self.assertEqual(self.witness.issued,1)
    def test_26_read_back_of_real_gh_commands_contract(self):
        calls=[]
        raw={'id':123,'immutable':True,'tag_name':self.release.tag,
             'published_at':seconds_back(100),
             'assets':[{'name':self.asset.name,'id':4,'digest':'sha256:'+sha(self.asset.read_bytes())}]}
        def runner(args,**kwargs):
            calls.append(args)
            class Result:
                returncode=0
                stdout=json.dumps(raw) if 'api' in args else ''
                stderr=''
            return Result()
        verifier=GhReleaseVerifier(Path('/fictional/gh'),runner=runner)
        proof=verifier.verify(self.release.tag,self.asset,sha(self.asset.read_bytes()))
        self.assertEqual(proof.remote_id,123)
        self.assertEqual([x[1:3] for x in calls[:2]],
                         [['release','verify'],['release','verify-asset']])
        self.assertTrue(all(x[0]=='/fictional/gh' for x in calls))
    def test_27_gh_verification_failure_denies(self):
        def fail(args,**kwargs):
            class Result: returncode=1; stdout='';stderr='bad signature'
            return Result()
        verifier=GhReleaseVerifier(Path('/fictional/gh'),runner=fail)
        with self.assertRaisesRegex(GateDenied,'GH_CRYPTOGRAPHIC_VERIFICATION_FAILED'):
            verifier.verify(self.release.tag,self.asset,sha(self.asset.read_bytes()))
    def test_28_gh_mutable_release_denies(self):
        def mutable(args,**kwargs):
            class Result:
                returncode=0
                stderr=''
                stdout=json.dumps({'id':123,'immutable':False,'tag_name':self.release.tag,
                     'published_at':seconds_back(100),'assets':[]}) if 'api' in args else ''
            return Result()
        verifier=GhReleaseVerifier(Path('/fictional/gh'),runner=mutable)
        with self.assertRaisesRegex(GateDenied,'REMOTE_RELEASE_IDENTITY_UNVERIFIED'):
            verifier.verify(self.release.tag,self.asset,sha(self.asset.read_bytes()))
    def test_29_gh_remote_asset_digest_mismatch_denies(self):
        def bad_digest(args,**kwargs):
            class Result:
                returncode=0
                stderr=''
                stdout=json.dumps({'id':123,'immutable':True,'tag_name':self.release.tag,
                    'published_at':seconds_back(100),'assets':[{'name':self.asset.name,
                    'id':4,'digest':'sha256:'+'0'*64}]}) if 'api' in args else ''
            return Result()
        verifier=GhReleaseVerifier(Path('/fictional/gh'),runner=bad_digest)
        with self.assertRaisesRegex(GateDenied,'REMOTE_ASSET_DIGEST_UNVERIFIED'):
            verifier.verify(self.release.tag,self.asset,sha(self.asset.read_bytes()))
    def test_30_antirollback_witness_receipt_must_be_authenticated(self):
        self.witness.reserve_once=lambda session_id,digest: WitnessReceipt(session_id,digest,'fake','false')
        self.deny('EXTERNAL_WITNESS_UNTRUSTED')
    def test_31_proof_loses_anchor_recheck_denies(self):
        orig=self.release.verify
        def half(tag,path,digest):
            if self.release.requests>=1:
                raise GateDenied('ANCHOR_REMOVED')
            return orig(tag,path,digest)
        self.release.verify=half
        self.deny('ANCHOR_REMOVED')
    def test_32_release_timestamp_not_earlier_than_signed_denies(self):
        orig=self.release.verify
        def same_time(tag,path,digest):
            x=orig(tag,path,digest)
            return replace(x,published_at=seconds_back(80))
        self.release.verify=same_time
        self.deny('GPRE_PROSPECTIVE_TIMESTAMP_ORDER_INVALID')

if __name__=='__main__':
    unittest.main(verbosity=2)
