#!/usr/bin/env python3
"""Independent-style synthetic adversarial fixtures for G1 trusted-boundary candidate.

Author tests only. No real source, G1 manifest/TEST, models, owner key or GPU.
"""
import hashlib
import json
import os
from pathlib import Path
import shutil
import sqlite3
import sys
import tempfile
from unittest.mock import patch
import g1_trusted_runtime_witness_candidate as g

results=[]
def passes(name, fn):
    fn()
    results.append(name)

def rejected(name, code, fn):
    try:fn()
    except (g.StopG1, FileExistsError, sqlite3.IntegrityError) as ex:
        if code:assert code in str(ex),(name,str(ex))
        results.append(name)
    else:raise AssertionError('FALSE_ACCEPT_'+name)

def new_dirs(base, tag):
    cr=base/(tag+'_controller');cr.mkdir()
    wr=base/(tag+'_worker');wr.mkdir()
    wi=base/(tag+'_witness');wi.mkdir()
    return cr,wr,wi

def run():
    with tempfile.TemporaryDirectory(prefix='g1_witness_synthetic_') as d:
        root=Path(d)
        cr,wr,wi=new_dirs(root,'a')
        c=g.WitnessedSimulationController(cr,wr,wi)
        rid='synth-main-0001'
        passes('admit_exact_run',lambda:c.admit(rid,b'SYNTHETIC_ONLY'))
        passes('witness_ack_genesis',lambda:assert_sync(c,rid,0,'ADMITTED'))
        rejected('duplicate_admission_rejected','RUN_ALREADY_SEEN',lambda:c.admit(rid,b'REPLAY'))
        rejected('invalid_run_id_rejected','RUN_ID',lambda:c.admit('../x',b'SYNTHETIC_ONLY'))
        rejected('missing_test_freeze','TEST_NOT_RELEASED',lambda:c.consume_test_before_open(rid,wr/'TEST.bin',wr))
        rejected('invalid_state_jump','STAGE_ORDER',lambda:c.advance(rid,'FIT_FROZEN','0'*64))
        rejected('invalid_state_hash','PAYLOAD_SHA',lambda:c.advance(rid,'TRAIN_COMMITTED','XX'))
        rejected('invalid_split','PACK_SPLIT',lambda:c.commit_pack(rid,'BLAH',b'x'))
        rejected('empty_pack','PACK_SIZE_SYNTHETIC',lambda:c.commit_pack(rid,'TRAIN',b''))
        passes('train_pack_committed',lambda:c.commit_pack(rid,'TRAIN',b'SYNTHETIC_TRAIN'))
        passes('witness_ack_train',lambda:assert_sync(c,rid,1,'TRAIN_COMMITTED'))
        rejected('train_replay_denied','PACK_STAGE',lambda:c.commit_pack(rid,'TRAIN',b'SYNTHETIC_TRAIN'))
        rejected('out_of_order_test_pack_denied','PACK_STAGE',lambda:c.commit_pack(rid,'TEST',b'x'))
        passes('dev_pack_committed',lambda:c.commit_pack(rid,'DEV',b'SYNTHETIC_DEV'))
        passes('fit_dev_frozen',lambda:c.advance(rid,'FIT_FROZEN',g.sha(b'SYNTHETIC_FREEZE')))
        # Hardlink and symlink cannot be treated as split isolation.
        test_path=wr/'SYNTHETIC_TEST_ONLY.bin';test_path.write_bytes(b'HELD_OUT_FAKE')
        alias=wr/'alias';os.link(test_path,alias)
        rejected('TEST_hardlink_denied','HARDLINK_OR_NONREGULAR',lambda:g.read_no_alias(test_path,wr))
        alias.unlink()
        link=wr/'link';link.symlink_to(test_path)
        rejected('TEST_symlink_denied','REDIRECTED_PATH',lambda:g.read_no_alias(link,wr))
        link.unlink()
        rejected('source_scope_escape_denied','READ_SCOPE',lambda:g.read_no_alias(cr/'SIM_PACK_TRAIN.bin',wr))
        # Read source is allowed only AFTER witness acknowledged consumption.
        out=c.consume_test_before_open(rid,test_path,wr)
        assert out==b'HELD_OUT_FAKE'
        results.append('TEST_open_after_witness_ACK')
        passes('witness_TEST_consumed',lambda:assert_sync(c,rid,4,'TEST_EXTRACT_CONSUMED'))
        rejected('TEST_reopen_denied','TEST_NOT_RELEASED',lambda:c.consume_test_before_open(rid,test_path,wr))
        passes('test_pack_committed',lambda:c.commit_pack(rid,'TEST',b'SYNTHETIC_TEST'))
        passes('test_read_consumed',lambda:c.advance(rid,'TEST_READ_CONSUMED',g.sha(b'TEST_READ')))
        passes('terminal_transition',lambda:c.terminal(rid,'DONE'))
        passes('terminal_persisted',lambda:assert_sync(c,rid,7,'TERMINAL'))
        rejected('postterminal_transition_denied','RUN_TERMINAL',lambda:c.advance(rid,'TRAIN_COMMITTED','0'*64))
        c.close()
        # Worker workspace can be removed/rebuilt; controller + witness outside it persist.
        shutil.rmtree(wr);wr.mkdir()
        c=g.WitnessedSimulationController(cr,wr,wi)
        passes('worker_workspace_rollback_detected_as_terminal',lambda:assert_sync(c,rid,7,'TERMINAL'))
        rejected('postworker_replay_denied','RUN_TERMINAL',lambda:c.advance(rid,'TRAIN_COMMITTED','0'*64))
        c.close()
        # Controller-only DB rollback is detected using witness ahead-of-controller tip.
        cr,wr,wi=new_dirs(root,'rollback')
        c=g.WitnessedSimulationController(cr,wr,wi)
        rid='synth-rollback-0002';c.admit(rid,b'A')
        c.close()
        saved=(cr/'ledger_sim_only.sqlite3').read_bytes()
        c=g.WitnessedSimulationController(cr,wr,wi)
        c.advance(rid,'TRAIN_COMMITTED',g.sha(b'SYN'))
        c.close()
        (cr/'ledger_sim_only.sqlite3').write_bytes(saved)
        c=g.WitnessedSimulationController(cr,wr,wi)
        rejected('controller_DB_rollback_denied','WITNESS_LEDGER_DIVERGED',lambda:c.advance(rid,'TRAIN_COMMITTED',g.sha(b'REPLAY')))
        rejected('controller_DB_rollback_read_denied','WITNESS_LEDGER_DIVERGED',lambda:c.verify_sync(rid))
        c.close()
        # Witness-only partial rollback is also detected, never silently reconstructed.
        cr,wr,wi=new_dirs(root,'witnessloss')
        c=g.WitnessedSimulationController(cr,wr,wi);rid='synth-witness-0003'
        c.admit(rid,b'A');c.advance(rid,'TRAIN_COMMITTED',g.sha(b'TRAIN'))
        (wi/rid/'00000001.json').unlink()
        rejected('witness_rollback_denied','WITNESS_LEDGER_DIVERGED',lambda:c.advance(rid,'DEV_COMMITTED',g.sha(b'DEV')))
        c.close()
        # Interruption after ledger commit but before witness ack never exposes TEST.
        cr,wr,wi=new_dirs(root,'crash')
        c=g.WitnessedSimulationController(cr,wr,wi);rid='synth-crash-00004'
        c.admit(rid,b'A');c.commit_pack(rid,'TRAIN',b'TRAIN');c.commit_pack(rid,'DEV',b'DEV')
        c.advance(rid,'FIT_FROZEN',g.sha(b'FIT'))
        source=wr/'SYNTHETIC_TEST.bin';source.write_bytes(b'NEVER_OPEN')
        original=c.witness.append
        def deny_witness(*args,**kwargs):
            raise OSError('SIMULATED_WITNESS_OUTAGE')
        with patch.object(c.witness,'append',side_effect=deny_witness):
            with patch.object(g,'read_no_alias',wraps=g.read_no_alias) as reads:
                try:c.consume_test_before_open(rid,source,wr)
                except OSError:pass
                else:raise AssertionError('WITNESS_OUTAGE_ACCEPTED')
                assert not any(Path(call.args[0]) == source for call in reads.call_args_list), 'TEST read before witness acknowledgment'
        results.append('TEST_denied_on_witness_outage')
        rejected('witness_outage_terminal_fail_closed','WITNESS_LEDGER_DIVERGED',lambda:c.verify_sync(rid))
        c.close()
        # Orphan pack after crash must not be silently replayable.
        cr,wr,wi=new_dirs(root,'orphan')
        c=g.WitnessedSimulationController(cr,wr,wi);rid='synth-orphan-0005'
        c.admit(rid,b'A')
        with patch.object(c.witness,'append',side_effect=OSError('ACK LOST')):
            try:c.commit_pack(rid,'TRAIN',b'TRAIN')
            except OSError:pass
            else:raise AssertionError('WITNESS_FAILED_NO_STOP')
        rejected('post_orphan_event_untrusted','WITNESS_LEDGER_DIVERGED',lambda:c.commit_pack(rid,'TRAIN',b'B'))
        c.close()
        # Crash before final link: a pending staging file is an orphan, not
        # permission for another pack attempt.
        cr,wr,wi=new_dirs(root,'orphanstage')
        c=g.WitnessedSimulationController(cr,wr,wi);rid='synth-stage-00006'
        c.admit(rid,b'A')
        (cr/'SIM_PACK_TRAIN.bin.staging.INTERRUPTED').write_bytes(b'PARTIAL')
        rejected('precommit_staging_orphan_denied','ORPHAN_OR_REPLAY_PACK',
                 lambda:c.commit_pack(rid,'TRAIN',b'RETRY'))
        c.close()
        # No production authority can be simulated by flipping caller booleans.
        rejected('science_denied_owner_unprovisioned','OWNER_PRODUCTION_SCOPE_NOT_GRANTED',lambda:g.authorize_real_science(
            owner_key='f'*64,ACL_verified=True,independent_witness=True,watchdog_verified=True,methods_approved=True))
        rejected('science_denied_without_flags','OWNER_PRODUCTION_SCOPE_NOT_GRANTED',lambda:g.authorize_real_science())
        # Synthetic subprocess kill only; no GPU runtime touched.
        slow=g.supervised_synthetic_child([sys.executable,'-c','import time;time.sleep(5)'],0.1)
        assert slow['timeout'] and slow['exit']!=0
        results.append('CPU_child_forced_kill')
        fast=g.supervised_synthetic_child([sys.executable,'-c','print(13)'],2.)
        assert not fast['timeout'] and fast['exit']==0
        results.append('CPU_child_completed')
        rejected('watchdog_bad_timeout','WATCHDOG_SYNTHETIC_TIMEOUT',lambda:g.supervised_synthetic_child([sys.executable,'-c','pass'],0))
        rejected('watchdog_boolean_timeout','WATCHDOG_SYNTHETIC_TIMEOUT',lambda:g.supervised_synthetic_child([sys.executable,'-c','pass'],True))
        rejected('watchdog_bogus_argv','WATCHDOG_ARGV',lambda:g.supervised_synthetic_child(['one'],1))
        # Filesystem roots must not share owner chain or be symlink aliases.
        rejected('same_controller_and_worker_denied','ROOTS_NOT_SEPARATE',lambda:g.root_proof(cr,cr,wi))
        rejected('nested_controller_denied','ROOTS_NOT_SEPARATE',lambda:g.root_proof(root,wr,wi))
        sy=root/'root_symlink';sy.symlink_to(cr,target_is_directory=True)
        rejected('root_symlink_denied','ROOT_REDIRECT',lambda:g.root_proof(sy,wr,wi))
    # Note: cannot protect against a single attacker who can rollback BOTH
    # controller and simulated witness or fabricate an external owner key.
    print(json.dumps({'status':'PASS_G1_TRUSTED_BOUNDARY_SIMULATION_ONLY',
         'checks':len(results),'tests':results,'science_executed':False,
         'real_TEST_opened':False,'real_GPU_tested':False,
         'production_witness_qualified':False,'owner_key_provisioned':False},sort_keys=True))

def assert_sync(c,rid,seq,state):
    x=c.verify_sync(rid)
    assert x['seq']==seq and x['state']==state

if __name__=='__main__':run()
