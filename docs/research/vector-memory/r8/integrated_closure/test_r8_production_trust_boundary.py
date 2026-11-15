"""Only synthetic boundary/negative tests. All real R8 scientific gates remain sealed."""
from dataclasses import replace
from datetime import datetime, timezone, timedelta
import hashlib
import json
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch

import r8_production_trust_boundary as rb
from pre_g3_admission_guard import PrivateEnvelope, AdmissionDenied, SOURCE_COMMIT, SCHEMA, ALGORITHM


def canonical(v): return json.dumps(v, ensure_ascii=False, sort_keys=True, separators=(',', ':')).encode()
def sha(b): return hashlib.sha256(b).hexdigest()


class FakeRemote:
    def __init__(self):
        self.releases={}
        self.revoked=False
        self.failure=False
        self.calls=[]
    def verify(self, tag, asset):
        self.calls.append(('verify',tag,asset))
        if self.failure or self.revoked or (tag,asset) not in self.releases:
            raise AdmissionDenied('REMOTE_MISSING')
        return self.releases[tag,asset]
    def consume_once(self, tag, asset, exact):
        self.calls.append(('consume',tag,asset))
        if self.failure: raise AdmissionDenied('REMOTE_UNAVAILABLE')
        if (tag,asset) in self.releases: raise AdmissionDenied('REMOTE_ALREADY_CONSUMED')
        p=rb.ReleaseProof(tag,asset,sha(exact),datetime.now(timezone.utc),
            datetime.now(timezone.utc),datetime.now(timezone.utc),
            rb.strict_json(exact), 'custodian')
        self.releases[tag,asset]=p
        return p


class FakeKeyProvider:
    def __init__(self,key): self.key=key
    def read_key(self): return self.key


class FakeCustody:
    def __init__(self, fold):
        self.fold=fold
        self.called=0
    def verify(self, src,runtime):
        self.called+=1
        if src != '3'*64 or runtime != '4'*64:
            raise AdmissionDenied('SOURCE_OR_RUNTIME_UNVERIFIED')
        return self.fold


STUB_SOURCE=b'''import hashlib,hmac,json

def preassign_r8(blueprints, key):
    if len(blueprints)!=32 or len(key)<32:raise ValueError('bad blueprint')
    return {'algorithm_id':'R8_GPRE_CANONICAL_JSON_COMPONENT_RANKING_V2',
            'lock_schema':'TTM_VM_R8_GPRE_HMAC_V2',
            'preassignment_hmac':hmac.new(key,b'R8_GPRE_FOLDS_V2',hashlib.sha256).hexdigest(),
            'blueprint_hmac':hmac.new(key,b'R8_GPRE_BLUEPRINT_V1',hashlib.sha256).hexdigest(),
            'cv_status':'PREFOLD_READY_NOT_VALIDATED'}
'''

class ProductionBoundaryQA(unittest.TestCase):
    def setUp(self):
        self.key=b'fixture-only-do-not-use-for-real-gpre-0123456789'
        self.blueprints=[{'blueprint_id':f'fixture-{i:02d}'} for i in range(32)]
        self.blueprint_bytes=canonical(self.blueprints)
        self.lock=canonical({
          'algorithm_id':ALGORITHM,'lock_schema':SCHEMA,
          'preassignment_hmac':__import__('hmac').new(self.key,b'R8_GPRE_FOLDS_V2',hashlib.sha256).hexdigest(),
          'blueprint_hmac':__import__('hmac').new(self.key,b'R8_GPRE_BLUEPRINT_V1',hashlib.sha256).hexdigest(),
          'cv_status':'PREFOLD_READY_NOT_VALIDATED'})
        self.source_manifest='3'*64; self.runtime_manifest='4'*64
        self.session='synthetic-session-001'
        payload={'schema':SCHEMA,'algorithm_id':ALGORITHM,'session_id':self.session,
                 'source_commit':SOURCE_COMMIT,'source_manifest_sha256':self.source_manifest,
                 'runtime_manifest_sha256':self.runtime_manifest,
                 'blueprint_sha256':sha(self.blueprint_bytes),'lock_sha256':sha(self.lock)}
        self.envelope=PrivateEnvelope(canonical(payload),bytes(range(16)),self.blueprint_bytes,self.lock)
        self.remote=FakeRemote()
        self.custody=FakeCustody(STUB_SOURCE)
        self.keys=FakeKeyProvider(self.key)
        self.policy=rb.TrustPolicy('a'*40,'distinct-reviewer','implementation-agent',
                'ttm-vm-v4-r8-gpre-fixture','ttm-vm-v4-r8-review-fixture','f'*64,'e'*64)
        self.now=datetime.now(timezone.utc)
        def at(minutes): return self.now+timedelta(minutes=minutes)
        gpre={'commitment_digest':self.envelope.public_digest,'session_id':self.session,
             'source_commit':SOURCE_COMMIT,'source_manifest_sha256':self.source_manifest,
             'runtime_manifest_sha256':self.runtime_manifest}
        approval={'review_commit':'a'*40,'amendment_status':'PASS_SCOPED_R8_D',
                  'commitment_digest':self.envelope.public_digest,'session_id':self.session}
        self.remote.releases[self.policy.accepted_gpre_release_tag,'r8-gpre-commitment.json']=rb.ReleaseProof(
            self.policy.accepted_gpre_release_tag,'r8-gpre-commitment.json','a'*64,
            at(-60),at(-70),at(-55),gpre,'custodian')
        self.remote.releases[self.policy.acceptance_release_tag,'r8-gpre-review-acceptance.json']=rb.ReleaseProof(
            self.policy.acceptance_release_tag,'r8-gpre-review-acceptance.json','b'*64,
            at(-35),at(-45),at(-25),approval,'distinct-reviewer')
        self.boundary=rb.ProductionBoundaryCandidate(self.remote,self.custody,self.policy,
                                      rb.RemoteOneShotLedger(self.remote),self.keys)
        self.called=0
        self.stub_patch=patch.dict(rb.FROZEN_SHA,{'folds_raters.py':sha(STUB_SOURCE)})
        self.stub_patch.start()
        self.addCleanup(self.stub_patch.stop)
        self.registry_patch=patch.object(rb.ProductionBoundaryCandidate,
                                         '_registered_generator',self.harmless)

    def harmless(self):
        self.called+=1
        return 'INERT_CALLBACK_ONLY'
    def fixture(self):
        with self.registry_patch:
            return self.boundary.dispatch(self.envelope)
    def deny(self, reason):
        with self.assertRaises(AdmissionDenied) as x:self.fixture()
        self.assertEqual(str(x.exception),reason)
        self.assertEqual(self.called,0)

    def test_01_production_dispatch_is_denied_without_generator(self):
        with self.assertRaisesRegex(AdmissionDenied,'NO_APPROVED_G3_GENERATOR_REGISTERED'):
            self.boundary.dispatch(self.envelope)
        self.assertEqual(self.called,0)
    def test_02_valid_fixture_consumes_remote_before_callback(self):
        def check():
            tag='ttm-vm-v4-r8-consumed-'+self.envelope.public_digest
            self.assertIn((tag,'r8-gpre-consumed.json'),self.remote.releases)
            return self.harmless()
        with patch.object(rb.ProductionBoundaryCandidate,'_registered_generator',check):
            result=self.boundary.dispatch(self.envelope)
        self.assertEqual(result,'INERT_CALLBACK_ONLY')
        self.assertEqual(self.called,1)
    def test_03_remote_consumption_survives_reset_of_local_objects(self):
        self.fixture(); self.assertEqual(self.called,1)
        self.boundary=rb.ProductionBoundaryCandidate(self.remote,FakeCustody(STUB_SOURCE),
                        self.policy,rb.RemoteOneShotLedger(self.remote),self.keys)
        with self.assertRaisesRegex(AdmissionDenied,'REMOTE_ALREADY_CONSUMED'):
            self.fixture()
        self.assertEqual(self.called,1)
    def test_04_remote_consumption_failure_blocks_callback(self):
        self.remote.failure=True
        self.deny('REMOTE_MISSING')
    def test_05_missing_gpre_anchor_blocks(self):
        del self.remote.releases[(self.policy.accepted_gpre_release_tag,'r8-gpre-commitment.json')]
        self.deny('REMOTE_MISSING')
    def test_06_missing_independent_acceptance_blocks(self):
        del self.remote.releases[(self.policy.acceptance_release_tag,'r8-gpre-review-acceptance.json')]
        self.deny('REMOTE_MISSING')
    def test_07_reviewer_same_as_implementation_actor_denies(self):
        self.policy=replace(self.policy,distinct_reviewer_login='implementation-agent')
        self.boundary.policy=self.policy
        self.deny('DISTINCT_INDEPENDENT_REVIEW_NOT_VERIFIED')
    def test_08_reviewer_fake_review_commit_denies(self):
        obj=self.remote.releases[self.policy.acceptance_release_tag,'r8-gpre-review-acceptance.json']
        self.remote.releases[self.policy.acceptance_release_tag,'r8-gpre-review-acceptance.json']=replace(
            obj,body=dict(obj.body,review_commit='0'*40))
        self.deny('DISTINCT_INDEPENDENT_REVIEW_NOT_VERIFIED')
    def test_09_changed_digest_denies(self):
        obj=self.remote.releases[self.policy.accepted_gpre_release_tag,'r8-gpre-commitment.json']
        self.remote.releases[self.policy.accepted_gpre_release_tag,'r8-gpre-commitment.json']=replace(
            obj,body=dict(obj.body,commitment_digest='0'*64))
        self.deny('REMOTE_COMMITMENT_BINDING_MISMATCH')
    def test_10_wrong_custodian_key_blocks(self):
        with self.assertRaisesRegex(AdmissionDenied,'GPRE_LOCK_HMAC_OR_FOLD_MISMATCH'):
            with self.registry_patch:
                self.keys.key=b'c'*40
                self.boundary.dispatch(self.envelope)
        self.assertEqual(self.called,0)
    def test_11_tampered_lock_blocks(self):
        lock=rb.strict_json(self.lock)
        lock['blueprint_hmac']='0'*64
        bad=canonical(lock)
        raw=rb.strict_json(self.envelope.exact_bytes);raw['lock_sha256']=sha(bad)
        env=replace(self.envelope,lock_bytes=bad,exact_bytes=canonical(raw))
        with self.assertRaisesRegex(AdmissionDenied,'GPRE_LOCK_HMAC_OR_FOLD_MISMATCH'):
            with self.registry_patch:self.boundary.dispatch(env)
        self.assertEqual(self.called,0)
    def test_12_manifest_claim_without_custody_denies(self):
        self.custody.fold=STUB_SOURCE
        self.custody.verify=lambda src,runtime: (_ for _ in ()).throw(AdmissionDenied('SOURCE_NOT_FOUND'))
        self.deny('SOURCE_NOT_FOUND')
    def test_13_anchor_revoked_after_reviewer_check(self):
        first=self.remote.verify
        counter=[0]
        def verify(tag,asset):
            if tag==self.policy.accepted_gpre_release_tag:
                counter[0]+=1
                if counter[0]>1:raise AdmissionDenied('ANCHOR_REVOKED')
            return first(tag,asset)
        self.remote.verify=verify
        self.deny('ANCHOR_REVOKED')
    def test_14_remote_preexisting_consume_marker_denies(self):
        tag='ttm-vm-v4-r8-consumed-'+self.envelope.public_digest
        proof=rb.ReleaseProof(tag,'r8-gpre-consumed.json','e'*64,self.now,self.now,self.now,
                              {'fake':'previously consumed'},'custodian')
        self.remote.releases[tag,'r8-gpre-consumed.json']=proof
        self.deny('REMOTE_ALREADY_CONSUMED')
    def test_15_acceptance_timestamp_out_of_order_blocks(self):
        obj=self.remote.releases[self.policy.acceptance_release_tag,'r8-gpre-review-acceptance.json']
        self.remote.releases[self.policy.acceptance_release_tag,'r8-gpre-review-acceptance.json']=replace(
            obj,published_at=self.now-timedelta(minutes=80))
        self.deny('REVIEW_NOT_AFTER_PROSPECTIVE_COMMITMENT')
    def test_16_unverified_hmac_implementation_denies(self):
        self.custody.fold=STUB_SOURCE+b'#modified\n'
        with self.assertRaisesRegex(AdmissionDenied,'FROZEN_FOLD_IMPLEMENTATION_MISMATCH'):
            self.fixture()
    def test_17_production_denies_even_when_ready(self):
        self.boundary.verify_readiness(self.envelope)
        with self.assertRaises(AdmissionDenied):self.boundary.dispatch(self.envelope)
        self.assertEqual(self.called,0)


class GitHubClientParsingQA(unittest.TestCase):
    def test_18_nested_verified_timestamps_only(self):
        o={'some_user_field':{'verifiedTimestamps':[{'timestamp':'2026-11-15T08:16:25Z'}]}}
        self.assertEqual(rb.GitHubReleaseAuthority._signed_verified_times(o),[])
        verified={'verificationResult':{'verifiedTimestamps':[{'timestamp':'2026-11-15T08:16:25Z'}]}}
        self.assertEqual(len(rb.GitHubReleaseAuthority._signed_verified_times(verified)),1)
    def test_19_nan_json_denied(self):
        with self.assertRaisesRegex(AdmissionDenied,'UNTRUSTED_JSON_BYTES'):
            rb.strict_json(b'{"x":NaN}')
    def test_20_duplicate_json_denied(self):
        with self.assertRaisesRegex(AdmissionDenied,'UNTRUSTED_JSON_BYTES'):
            rb.strict_json(b'{"x":1,"x":2}')
    def test_21_missing_gh_digest_denied(self):
        with tempfile.TemporaryDirectory() as d:
            binary=Path(d)/'gh';binary.write_bytes(b'synthetic-gh-no-real-executable')
            with self.assertRaisesRegex(AdmissionDenied,'GH_EXECUTABLE_NOT_PINNED'):
                rb.GitHubReleaseAuthority(binary,'0'*64)
    def test_22_no_real_generator_registered(self):
        self.assertIsNone(rb.ProductionBoundaryCandidate._registered_generator)


if __name__=='__main__': unittest.main(verbosity=2)
