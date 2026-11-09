#!/usr/bin/env python3
"""Standalone CPU synthetic integration tests. Never opens TinyStories/G1 TEST."""
from pathlib import Path
from tempfile import TemporaryDirectory
import contextlib
import hashlib
import json
import os
import sys
from unittest.mock import patch
import g1_admission_controller_candidate as c

count=0
results=[]
def expect(label, f, code=None):
    global count
    try:
        value=f()
    except Exception as exc:
        if code is None:raise
        assert code in str(exc), f'{label} expected {code} got {type(exc).__name__} {exc}'
    else:
        assert code is None, f'{label} accepted when expected {code}: {value}'
    count+=1; results.append(label)

def run():
    with TemporaryDirectory() as root:
        root=Path(root)
        worker=root/'worker';worker.mkdir()
        controller=root/'controller';controller.mkdir()
        broker=root/'broker';broker.mkdir()
        path=broker/'G1_PREFIX_TEST.json'
        path.write_text('SYNTHETIC_TEST_ONLY',encoding='utf8')
        control=c.SimulatedControllerLedger(controller,worker)
        rid='synthetic-run-0001'
        expect('sim_admit',lambda:control.admit_simulated(rid,b'SIM_ONLY'))
        try:
            control.admit_simulated(rid,b'SIM_ONLY')
        except Exception as e:
            assert 'UNIQUE' in str(e)
            expect('admission_not_duplicated',lambda:control.state(rid)['seq'])
        else:raise AssertionError('duplicate run admitted')
        expect('test_denied_before_freeze',lambda:control.release_test_synthetic(rid,broker),'TEST_BEFORE_FIT_FREEZE')
        expect('out_of_order_denied',lambda:control.advance(rid,'FIT_FROZEN','a'*64),'NONMONOTONIC_TRANSITION')
        expect('wrong_digest_denied',lambda:control.advance(rid,'TRAIN_COMMITTED','BAD'),'BAD_PAYLOAD_HASH')
        expect('trainer_pack_commit',lambda:control.commit_pack_synthetic(rid,'ADMITTED','TRAIN_COMMITTED',b'FAKE_TRAIN','TRAIN.npz'))
        expect('second_pack_same_path_denied',lambda:control.commit_pack_synthetic(rid,'TRAIN_COMMITTED','DEV_COMMITTED',b'FAKE_DEV','TRAIN.npz'),'PACK_ALREADY_PRESENT')
        expect('dev_pack_commit',lambda:control.commit_pack_synthetic(rid,'TRAIN_COMMITTED','DEV_COMMITTED',b'FAKE_DEV','DEV.npz'))
        expect('freeze_ledger',lambda:control.advance(rid,'FIT_FROZEN',c.digest(b'SYNTHETIC_FREEZE')))
        expect('chain_pretest',lambda:control.check_chain(rid))
        # A hardlink of held-out bytes under a source alias is never acceptable.
        alias=broker/'holdout-alias.json'
        os.link(path,alias)
        expect('hardlink_alias_denied',lambda:c.guarded_regular(path,broker),'HARDLINK_OR_NOT_REGULAR')
        alias.unlink()
        # A symlink/junction is not an isolation mechanism.
        link=broker/'redirect.json';link.symlink_to(path)
        expect('symlink_denied',lambda:c.guarded_regular(link,broker),'REDIRECTED_PATH')
        link.unlink()
        expect('path_outside_root_denied',lambda:c.guarded_regular(controller/'TRAIN.npz',broker),'OUTSIDE_PRIVATE_ROOT')
        expect('test_open_once',lambda:control.release_test_synthetic(rid,broker))
        expect('test_open_again_denied',lambda:control.release_test_synthetic(rid,broker),'TEST_BEFORE_FIT_FREEZE')
        expect('test_pack_commit',lambda:control.commit_pack_synthetic(rid,'TEST_EXTRACT_CONSUMED','TEST_PACK_COMMITTED',b'FAKE_TEST','TEST.npz'))
        expect('test_read_consume',lambda:control.advance(rid,'TEST_READ_CONSUMED',c.digest(b'READ_INTENT')))
        expect('terminal',lambda:control.advance(rid,'TERMINAL',c.digest(b'DONE')))
        expect('terminal_restart_denied',lambda:control.advance(rid,'TRAIN_COMMITTED',c.digest(b'REPLAY')),'RUN_MISSING_OR_TERMINAL')
        expect('terminal_db_persists',lambda:control.state(rid)['terminal']==1)
        expect('chain_terminal',lambda:control.check_chain(rid))
        control.close()
        # Delete the worker contents, then open same trusted controller DB.
        for p in worker.iterdir():
            if p.is_file():p.unlink()
        control=c.SimulatedControllerLedger(controller,worker)
        expect('workspace_cleanup_does_not_reset_ledger',lambda:control.state(rid)['terminal']==1)
        try:control.admit_simulated(rid,b'FAKE')
        except Exception as e:
            assert 'UNIQUE' in str(e)
            expect('replay_after_worker_cleanup_denied',lambda:True)
        else:raise AssertionError('workspace rollback replay accepted')
        control.close()
        # Crash after ledger decision but before file commit; no retry.
        ctr2=root/'controller2';ctr2.mkdir()
        cr=c.SimulatedControllerLedger(ctr2,worker)
        cr.admit_simulated('synthetic-run-0002',b'DUMMY')
        with patch.object(c.os,'link',side_effect=OSError('simulated interrupted disk')):
            try:cr.commit_pack_synthetic('synthetic-run-0002','ADMITTED','TRAIN_COMMITTED',b'PACK','TRAIN.npz')
            except OSError:pass
            else:raise AssertionError('crash fixture did not crash')
        expect('pack_crash_terminal',lambda:cr.state('synthetic-run-0002')['status']=='TERMINAL')
        expect('crash_replay_denied',lambda:cr.commit_pack_synthetic('synthetic-run-0002','ADMITTED','TRAIN_COMMITTED',b'PACK','TRAIN.npz'),'PACK_WRONG_STAGE')
        cr.close()
        # Cumulative controller budget, not local worker clocks.
        ctr3=root/'controller3';ctr3.mkdir()
        cb=c.SimulatedControllerLedger(ctr3,worker)
        cb.admit_simulated('synthetic-run-0003',b'DUMMY')
        expect('source_budget',lambda:cb.record_budget('synthetic-run-0003','source',3500.0))
        expect('target_budget',lambda:cb.record_budget('synthetic-run-0003','target',3400.0))
        expect('source_overrun_denied',lambda:cb.record_budget('synthetic-run-0003','source',101.0),'CUMULATIVE_GPU_TIMEOUT')
        expect('target_overrun_denied',lambda:cb.record_budget('synthetic-run-0003','target',201.0),'CUMULATIVE_GPU_TIMEOUT')
        expect('boolean_budget_denied',lambda:cb.record_budget('synthetic-run-0003','target',True),'MODEL_TIMEOUT')
        cb.close()
        # Real owner key missing: cannot be bypassed via booleans.
        expect('science_permit_fail_closed',lambda:c.production_admission_gate(
            owner_public_sha256='f'*64,broker_acl_attested=True,
            trusted_writer_attested=True,remote_witness_attested=True,
            watchdog_attested=True,methods_approved=True), 'OWNER_TRUST_ROOT_NOT_PROVISIONED')
        # OS-level forced termination by controller, tested on CPU child only.
        ret=c.supervised_child_synthetic([sys.executable,'-c','import time;time.sleep(20)'],0.2)
        assert ret['timed_out'] and ret['exit']!=0
        expect('supervisor_force_killed_cpu_child',lambda:True)
        ok=c.supervised_child_synthetic([sys.executable,'-c','print(10+3)'],2.0)
        assert ok['exit']==0 and not ok['timed_out']
        expect('supervisor_allows_short_child',lambda:True)
    print(json.dumps({'status':'PASS_INTEGRATED_ADMISSION_SYNTHETIC_ONLY',
                      'checks':count,'tests':results,
                      'owner_production_authority':'NOT_PROVISIONED',
                      'external_rollback_witness':'NOT_ATTESTED',
                      'real_TEST_read':False,'science_executed':False},sort_keys=True))
if __name__=='__main__':run()
