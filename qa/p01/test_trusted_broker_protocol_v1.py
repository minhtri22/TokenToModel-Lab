"""Independent pure protocol and failure-atomicity tests, NOT native W01-W12."""
import base64
import hashlib
import json
import pathlib
import unittest
import tempfile
import sys
sys.path.insert(0,str(pathlib.Path(__file__).parent))
from trusted_broker_service_v1 import BrokerHandler, BrokerSecurityError, parse_request,MAX_FILE
from durable_broker_quota_v1 import DurableQuotaLedger, QuotaRefusal, MAX_BYTES

def packet(payload=b'hello',name='evidence.dat',rid='case01',**delta):
    obj={'op':'WRITE_NEW','request_id':rid,'filename':name,'size':len(payload),
         'sha256':hashlib.sha256(payload).hexdigest(),
         'data_b64':base64.b64encode(payload).decode('ascii')}
    obj.update(delta)
    return json.dumps(obj).encode()
class FakeWriter:
    def __init__(self,fail=False,mismatch=False):
        self.fail,self.mismatch=fail,mismatch
        self.files={}
    def publish(self,name,payload,expected_sha256):
        if name in self.files:raise RuntimeError('DUPLICATE_WRITE')
        if self.fail:raise OSError('INJECTED_WRITE_FAILURE')
        self.files[name]=payload
        return {'size':len(payload)+int(self.mismatch),'sha256':hashlib.sha256(payload).hexdigest()}
class ProtocolQA(unittest.TestCase):
    def setUp(self):
        self.temp=tempfile.TemporaryDirectory()
        self.ledger=DurableQuotaLedger(str(pathlib.Path(self.temp.name)/'ledger.sqlite'))
        self.writer=FakeWriter()
        self.handler=BrokerHandler(self.ledger,self.writer)
    def tearDown(self):self.temp.cleanup()
    def test_happy_path_marks_committed(self):
        r=self.handler.apply(packet())
        self.assertTrue(r['ok'])
        self.assertEqual(self.ledger.snapshot()[0].state,'COMMITTED')
    def test_replay_exact_rejected_no_second_write(self):
        self.handler.apply(packet())
        with self.assertRaisesRegex(BrokerSecurityError,'REPLAY_EXISTING'):
            self.handler.apply(packet())
        self.assertEqual(self.writer.files,{'evidence.dat':b'hello'})
    def test_bad_sha_rejected_before_reservation(self):
        with self.assertRaisesRegex(BrokerSecurityError,'SHA256_MISMATCH'):
            self.handler.apply(packet(sha256='0'*64))
        self.assertEqual(len(self.ledger.snapshot()),0)
    def test_bad_size_rejected_before_reservation(self):
        with self.assertRaisesRegex(BrokerSecurityError,'SIZE_MISMATCH'):
            self.handler.apply(packet(size=19))
        self.assertEqual(len(self.ledger.snapshot()),0)
    def test_unknown_operation_rejected(self):
        with self.assertRaisesRegex(BrokerSecurityError,'OPERATION_NOT_ALLOWED'):
            self.handler.apply(packet(op='READ'))
    def test_unknown_fields_rejected(self):
        with self.assertRaisesRegex(BrokerSecurityError,'UNKNOWN_OR_MISSING'):
            self.handler.apply(packet(extra='no'))
    def test_invalid_json_rejected(self):
        with self.assertRaisesRegex(BrokerSecurityError,'INVALID_JSON_FRAME'):
            self.handler.apply(b'{')
    def test_invalid_base64_rejected(self):
        with self.assertRaisesRegex(BrokerSecurityError,'B64_INVALID'):
            self.handler.apply(packet(data_b64='???'))
    def test_request_traversal_rejected(self):
        with self.assertRaises(QuotaRefusal):
            self.handler.apply(packet(name='../escape'))
    def test_duplicate_casefold_rejected(self):
        self.handler.apply(packet(name='NAME.dat',rid='a'))
        with self.assertRaises(QuotaRefusal):
            self.handler.apply(packet(name='name.DAT',rid='b'))
    def test_partial_writer_failure_is_held(self):
        self.writer.fail=True
        with self.assertRaises(OSError):self.handler.apply(packet())
        self.assertEqual(self.ledger.snapshot()[0].state,'FAILED_HELD')
    def test_receipt_mismatch_is_held(self):
        self.writer.mismatch=True
        with self.assertRaisesRegex(BrokerSecurityError,'RECEIPT_MISMATCH'):
            self.handler.apply(packet())
        self.assertEqual(self.ledger.snapshot()[0].state,'FAILED_HELD')
    def test_held_capacity_not_refunded_on_restart(self):
        self.ledger.reserve('full','full.dat',MAX_BYTES)
        self.ledger.mark_failed_held('full')
        restarted=DurableQuotaLedger(self.ledger.db_path)
        with self.assertRaisesRegex(QuotaRefusal,'AGGREGATE_QUOTA_EXCEEDED'):
            restarted.reserve('new','new.dat',1)
    def test_non_windows_service_always_refuses(self):
        from trusted_broker_service_v1 import serve_one_connection
        with self.assertRaisesRegex(BrokerSecurityError,'WINDOWS_ONLY'):
            serve_one_connection(pipe_name='x',authkey=b'a'*32,expected_broker_sid='S-1-5-1',worker_sid='S-1-5-2',evidence_root='x',ledger_path='x')
    def test_windows_backend_untested_static_import_only(self):
        from worker_identity_acl_win32_v1 import RestrictedWorkerIdentity,WorkerIdentityFailure
        from atomic_handle_writer_win32_v1 import AtomicHandleWriter,AtomicWriteError
        if sys.platform == 'win32':
            # Native checks require their own W01-W12 permit, never run here.
            self.assertTrue(callable(RestrictedWorkerIdentity))
            self.assertTrue(callable(AtomicHandleWriter))
        else:
            with self.assertRaises(WorkerIdentityFailure):RestrictedWorkerIdentity()
            with self.assertRaises(AtomicWriteError):AtomicHandleWriter('fake')
if __name__=='__main__':unittest.main(verbosity=2)
