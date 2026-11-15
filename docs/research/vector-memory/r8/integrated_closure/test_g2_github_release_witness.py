"""Pure fake-GitHub API/CLI tests. Never calls GitHub or creates a real release."""
import hashlib
import json
from pathlib import Path
import tempfile
import threading
import unittest
from concurrent.futures import ThreadPoolExecutor
from g2_github_release_witness import GitHubReleaseWitness, ASSET, TAG_PREFIX
from g2_production_boundary import GateDenied, sha

class FakeProcess:
    def __init__(self, code=0, stdout=''):
        self.returncode=code
        self.stdout=stdout
        self.stderr=''

class FakeGh:
    def __init__(self):
        self.lock=threading.Lock()
        self.releases={}
        self.calls=[]
        self.next_id=100
        self.immutable=True
        self.missing=False
        self.bad_signature=False
        self.corrupt_asset=False
        self.clone_tag=False

    def __call__(self,cmd,**kwargs):
        assert kwargs['shell'] is False
        args=cmd[1:]
        with self.lock:
            self.calls.append(args)
            if args[:2]==['release','create']:
                tag=args[2]
                if tag in self.releases:
                    return FakeProcess(1)
                raw=Path(args[3]).read_bytes()
                self.next_id+=1
                self.releases[tag]={'id':self.next_id,'tag_name':tag,
                    'immutable':self.immutable,'published_at':'2026-11-15T09:00:00Z',
                    'assets':[{'name':ASSET,'digest':'sha256:'+sha(raw)}],
                    '_asset':raw}
                return FakeProcess()
            if args[0]=='api':
                tag=args[1].split('/')[-1]
                if self.missing or tag not in self.releases:
                    return FakeProcess(1)
                r=self.releases[tag]
                data={k:v for k,v in r.items() if k!='_asset'}
                return FakeProcess(stdout=json.dumps(data))
            if args[:2] in (['release','verify'],['release','verify-asset']):
                return FakeProcess(1 if self.bad_signature else 0)
            if args[:2]==['release','download']:
                tag=args[2]
                if self.missing or tag not in self.releases:
                    return FakeProcess(1)
                root=Path(args[args.index('--dir')+1])
                raw=self.releases[tag]['_asset']
                if self.corrupt_asset: raw+=b'BAD'
                (root/ASSET).write_bytes(raw)
                return FakeProcess()
            raise AssertionError('UNEXPECTED_CALL:'+repr(args))

class WitnessTests(unittest.TestCase):
    def setUp(self):
        t=tempfile.TemporaryDirectory()
        self.addCleanup(t.cleanup)
        self.root=Path(t.name)
        self.gh=FakeGh()
        self.w=GitHubReleaseWitness('/mock/gh',self.root,runner=self.gh)
        self.session='fixture-session-001'
        self.digest='a'*64

    def test_01_create_and_verify_release_asset(self):
        receipt=self.w.reserve_once(self.session,self.digest)
        self.assertTrue(receipt.signature_verified)
        self.assertEqual(receipt.commitment_digest,self.digest)
        self.assertTrue(receipt.witness_event_id.startswith('github-immutable-release:'))
        self.assertEqual(self.w.read_verified(self.session),receipt)
        self.assertTrue(any(c[:2]==['release','verify-asset'] for c in self.gh.calls))

    def test_02_replay_same_session_same_digest_denies(self):
        self.w.reserve_once(self.session,self.digest)
        with self.assertRaises(GateDenied):
            self.w.reserve_once(self.session,self.digest)

    def test_03_replay_same_session_different_digest_denies(self):
        self.w.reserve_once(self.session,self.digest)
        with self.assertRaises(GateDenied):
            self.w.reserve_once(self.session,'b'*64)
        with self.assertRaisesRegex(GateDenied,'EXTERNAL_WITNESS_DIGEST_IDENTITY_MISMATCH'):
            self.w.read_verified(self.session,'b'*64)

    def test_04_separate_instances_share_remote_witness(self):
        self.w.reserve_once(self.session,self.digest)
        second=GitHubReleaseWitness('/mock/gh',self.root,runner=self.gh)
        with self.assertRaises(GateDenied):
            second.reserve_once(self.session,self.digest)

    def test_05_two_threads_one_release(self):
        def task(_):
            try:
                return self.w.reserve_once(self.session,self.digest).witness_event_id
            except GateDenied:
                return 'DENIED'
        with ThreadPoolExecutor(max_workers=4) as pool:
            results=list(pool.map(task,range(4)))
        self.assertEqual(results.count('DENIED'),3)
        self.assertEqual(sum(x.startswith('github-immutable-release:') for x in results),1)

    def test_06_release_deleted_blocks_readback(self):
        self.w.reserve_once(self.session,self.digest)
        self.gh.missing=True
        with self.assertRaisesRegex(GateDenied,'EXTERNAL_GITHUB_WITNESS_OPERATION_FAILED'):
            self.w.read_verified(self.session)

    def test_07_mutable_release_denies(self):
        self.gh.immutable=False
        with self.assertRaisesRegex(GateDenied,'EXTERNAL_WITNESS_RELEASE_NOT_IMMUTABLE'):
            self.w.reserve_once(self.session,self.digest)

    def test_08_signature_verification_fails_closed(self):
        self.gh.bad_signature=True
        with self.assertRaisesRegex(GateDenied,'EXTERNAL_GITHUB_WITNESS_OPERATION_FAILED'):
            self.w.reserve_once(self.session,self.digest)

    def test_09_corrupt_download_denies(self):
        self.gh.corrupt_asset=True
        with self.assertRaisesRegex(GateDenied,'FILE_SHA256_PIN_MISMATCH'):
            self.w.reserve_once(self.session,self.digest)

    def test_10_bad_session_and_digest_rejected(self):
        with self.assertRaisesRegex(GateDenied,'EXTERNAL_WITNESS_SESSION_INVALID'):
            self.w.reserve_once('bad','a'*64)
        with self.assertRaisesRegex(GateDenied,'EXTERNAL_WITNESS_DIGEST_INVALID'):
            self.w.reserve_once(self.session,'bad')
        self.assertEqual(len(self.gh.calls),0)

    def test_11_deleted_release_can_be_recreated_is_known_risk(self):        # Explicit negative SECURITY LIMITATION: privileged deletion can reset
        # this witness. Retention amendment + invalidation are still mandatory.
        old=self.w.reserve_once(self.session,self.digest)
        self.gh.releases.clear() # admins can do this; fake emulates deletion
        new=self.w.reserve_once(self.session,self.digest)
        self.assertNotEqual(old.witness_event_id,new.witness_event_id)

if __name__=='__main__': unittest.main(verbosity=2)
