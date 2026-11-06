"""Independent mock-only negative tests. No Win32 API or subprocess."""
import unittest
from native_guard_lifecycle_v2 import GuardFailure, inspect_mock_only

class MockBackend:
    def __init__(self, fail=None):
        self.fail=fail
        self.events=[]
    def make_job(self):
        self.events.append('job')
        return 10
    def job_limits_confirmed(self, job):
        self.events.append('limits')
        return self.fail!='limits'
    def create_suspended(self):
        self.events.append('spawn_suspended')
        return 20,30
    def is_suspended(self,p,t):
        self.events.append('suspended_confirmed')
        return self.fail!='suspended'
    def assign(self,j,p):
        self.events.append('assign')
        return self.fail!='assign'
    def is_member(self,j,p):
        self.events.append('member')
        return self.fail!='member'
    def resume(self,t):
        self.events.append('resume')
        return self.fail!='resume'
    def terminate_job(self,j):
        self.events.append('killjob')
        return self.fail!='killjob'
    def wait(self,p,t):
        self.events.append('wait')
        return self.fail!='wait'
    def terminate_process(self,p):
        self.events.append('killproc')
        return self.fail!='killproc'
    def close(self,h):
        self.events.append('close'+str(h))
        if self.fail=='close':raise OSError('fake close error')

MockBackend.__module__='test_native_guard_lifecycle_v2'

class NegativeLifecycle(unittest.TestCase):
    def test_no_authority(self):
        with self.assertRaisesRegex(GuardFailure,'NO_NATIVE_EXECUTION_AUTHORITY'):
            inspect_mock_only(MockBackend(),fake_authority=None)
    def test_outsider_refused(self):
        class Outsider(MockBackend): pass
        Outsider.__module__='outside'
        with self.assertRaisesRegex(GuardFailure,'TEST_BACKEND_REQUIRED'):
            inspect_mock_only(Outsider(),fake_authority='MOCK_ONLY_NO_WIN32')
    def test_positive_fake_never_returns_worker(self):
        b=MockBackend()
        with self.assertRaisesRegex(GuardFailure,'MOCK_ONLY_SIMULATION_COMPLETE'):
            inspect_mock_only(b,fake_authority='MOCK_ONLY_NO_WIN32')
        self.assertLess(b.events.index('assign'),b.events.index('member'))
        self.assertLess(b.events.index('member'),b.events.index('resume'))
        self.assertIn('killjob',b.events)
    def test_limits_rejection_before_spawn(self):
        b=MockBackend('limits')
        with self.assertRaisesRegex(GuardFailure,'JOB_LIMIT_MISMATCH'):
            inspect_mock_only(b,fake_authority='MOCK_ONLY_NO_WIN32')
        self.assertNotIn('spawn_suspended',b.events)
    def test_assign_failure_kills_without_resume(self):
        b=MockBackend('assign')
        with self.assertRaisesRegex(GuardFailure,'JOB_ASSIGN_FAILED'):
            inspect_mock_only(b,fake_authority='MOCK_ONLY_NO_WIN32')
        self.assertNotIn('resume',b.events)
        self.assertIn('killjob',b.events)
    def test_membership_failure_kills_without_resume(self):
        b=MockBackend('member')
        with self.assertRaisesRegex(GuardFailure,'JOB_MEMBERSHIP_FAILED'):
            inspect_mock_only(b,fake_authority='MOCK_ONLY_NO_WIN32')
        self.assertNotIn('resume',b.events)
    def test_unverified_stop_is_failure(self):
        b=MockBackend('wait')
        with self.assertRaisesRegex(GuardFailure,'PROCESS_TERMINATION_UNVERIFIED'):
            inspect_mock_only(b,fake_authority='MOCK_ONLY_NO_WIN32')
    def test_close_failure_is_failure(self):
        b=MockBackend('close')
        with self.assertRaisesRegex(GuardFailure,'CLOSE_THREAD_FAILED'):
            inspect_mock_only(b,fake_authority='MOCK_ONLY_NO_WIN32')

if __name__=='__main__': unittest.main()
