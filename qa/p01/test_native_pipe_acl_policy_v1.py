"""Independent source-only negatives for the proposed pipe DACL policy.

Does not create a native pipe, spawn any worker, or run W01-W12.
"""
import unittest
from native_pipe_acl_policy_v1 import (
    CLIENT_ACCESS_MASK, FILE_CREATE_PIPE_INSTANCE,
    PipePolicyRefusal, propose_pipe_sddl, forbid_default_pipe_acl
)
SERVICE="S-1-5-80-123456789-987654321-123456789-987654321-123456789"
WORKER="S-1-5-21-123456789-987654321-123456789-1002"

class PipePolicyNegativeQA(unittest.TestCase):
    def test_exact_protected_dacl(self):
        s=propose_pipe_sddl(service_sid=SERVICE,worker_sid=WORKER)
        self.assertTrue(s.startswith("D:P"))
        self.assertIn(SERVICE,s)
        self.assertIn(WORKER,s)
        self.assertNotIn(";;;WD",s)
        self.assertNotIn(";;;AU",s)
    def test_client_cannot_create_pipe_instance(self):
        self.assertEqual(CLIENT_ACCESS_MASK & FILE_CREATE_PIPE_INSTANCE,0)
    def test_service_sid_must_be_service_namespace(self):
        with self.assertRaisesRegex(PipePolicyRefusal,"SERVICE_SID_REQUIRED"):
            propose_pipe_sddl(service_sid=WORKER,worker_sid=SERVICE)
    def test_reject_same_identity(self):
        with self.assertRaises(PipePolicyRefusal):
            propose_pipe_sddl(service_sid=SERVICE,worker_sid=SERVICE)
    def test_reject_builtin_users(self):
        for sid in ("S-1-1-0","S-1-5-7","S-1-5-11","S-1-5-32-545",
                    "S-1-5-18","S-1-5-32-544"):
            with self.subTest(sid=sid),self.assertRaises(PipePolicyRefusal):
                propose_pipe_sddl(service_sid=SERVICE,worker_sid=sid)
    def test_reject_sddl_injection(self):
        with self.assertRaises(PipePolicyRefusal):
            propose_pipe_sddl(service_sid=SERVICE,worker_sid=WORKER+")(")
    def test_reject_empty_or_non_string_sid(self):
        for val in ("",None,{},17):
            with self.subTest(val=val),self.assertRaises(PipePolicyRefusal):
                propose_pipe_sddl(service_sid=SERVICE,worker_sid=val)
    def test_default_dacl_is_rejected(self):
        with self.assertRaisesRegex(PipePolicyRefusal,"DEFAULT_PIPE_DACL_BLOCKED"):
            forbid_default_pipe_acl(security_attributes_explicit=False,
                                    native_dacl_readback=True,client_sid_attested=True)
    def test_readback_missing_is_rejected(self):
        with self.assertRaisesRegex(PipePolicyRefusal,"NATIVE_DACL_READBACK_REQUIRED"):
            forbid_default_pipe_acl(security_attributes_explicit=True,
                                    native_dacl_readback=False,client_sid_attested=True)
    def test_peer_sid_missing_is_rejected(self):
        with self.assertRaisesRegex(PipePolicyRefusal,"CLIENT_TOKEN_SID_ATTESTATION_REQUIRED"):
            forbid_default_pipe_acl(security_attributes_explicit=True,
                                    native_dacl_readback=True,client_sid_attested=False)

if __name__=="__main__":
    unittest.main(verbosity=2)
