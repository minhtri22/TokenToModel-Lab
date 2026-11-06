"""Independent fake-storage quota tests; no Windows worker / real corpus."""
import tempfile
import unittest
from pathlib import Path
from durable_broker_quota_v1 import DurableQuotaLedger, QuotaRefusal, MAX_BYTES

class DurableQuotaQA(unittest.TestCase):
    def setUp(self):
        self.temp=tempfile.TemporaryDirectory()
        self.db=str(Path(self.temp.name)/"ledger.sqlite")
        self.q=DurableQuotaLedger(self.db)
    def tearDown(self):
        self.temp.cleanup()
    def test_canonical_quota(self):
        with self.assertRaises(QuotaRefusal):
            DurableQuotaLedger(self.db,limit_bytes=1024)
    def test_aggregate_rejected(self):
        self.q.reserve("a","a.bin",MAX_BYTES)
        with self.assertRaisesRegex(QuotaRefusal,"AGGREGATE_QUOTA_EXCEEDED"):
            self.q.reserve("b","b.bin",1)
    def test_replay_identical(self):
        self.assertEqual(self.q.reserve("a","a.bin",3),self.q.reserve("a","a.bin",3))
        self.assertEqual(len(self.q.snapshot()),1)
    def test_replay_different_denied(self):
        self.q.reserve("a","a.bin",3)
        with self.assertRaises(QuotaRefusal):self.q.reserve("a","b.bin",3)
    def test_casefold_collision(self):
        self.q.reserve("a","ONE.dat",3)
        with self.assertRaises(QuotaRefusal):self.q.reserve("b","one.DAT",2)
    def test_path_traversal_and_device_name_denied(self):
        for name in ["../x","C:\\x","x/y","file:stream","CON.txt","", ".env"]:
            with self.subTest(name=name),self.assertRaises(QuotaRefusal):
                self.q.reserve("bad",name,1)
    def test_failure_is_held_across_restart(self):
        self.q.reserve("a","a.bin",MAX_BYTES)
        self.q.mark_failed_held("a")
        restarted=DurableQuotaLedger(self.db)
        self.assertEqual(restarted.snapshot()[0].state,"FAILED_HELD")
        with self.assertRaises(QuotaRefusal):restarted.reserve("b","b.bin",1)
    def test_commit_requires_readback_contract(self):
        self.q.reserve("a","a.bin",5)
        with self.assertRaises(QuotaRefusal):
            self.q.mark_committed("a",exact_size=4,verified_sha256="f"*64)
        with self.assertRaises(QuotaRefusal):
            self.q.mark_committed("a",exact_size=5,verified_sha256="bad")
        self.q.mark_committed("a",exact_size=5,verified_sha256="f"*64)
        self.assertEqual(self.q.snapshot()[0].state,"COMMITTED")
    def test_committed_quota_not_refunded(self):
        self.q.reserve("a","a.bin",MAX_BYTES)
        self.q.mark_committed("a",exact_size=MAX_BYTES,verified_sha256="f"*64)
        with self.assertRaises(QuotaRefusal):self.q.reserve("b","b.bin",1)
    def test_held_failure_cannot_be_committed(self):
        self.q.reserve("a","a.bin",10)
        self.q.mark_failed_held("a")
        with self.assertRaises(QuotaRefusal):
            self.q.mark_committed("a",exact_size=10,verified_sha256="f"*64)

if __name__=="__main__":unittest.main()
