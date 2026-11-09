#!/usr/bin/env python3
"""G1 pre-execution trust-boundary candidate; NOT a production science permit.

This module is deliberately fail-closed for real science. Its SQLite ledger,
private split broker and subprocess watchdog support synthetic integration QA.
Production requires owner-controlled signing root, distinct OS principals,
immutable off-worker witness and actual Windows/Colab security attestation.

No Qwen, TinyStories, private manifest or G1 TEST is accessed by this module.
"""
from __future__ import annotations
import hashlib
import json
import os
from pathlib import Path
import signal
import sqlite3
import stat
import subprocess
import sys
import time
import uuid

REVIEWED_HEAD = 'd5d0c5346a595557a76349f900d09be50bce289c'
MANIFEST_SHA = '6451be0cd09a54378eda9e815b5c89ce8ce8301ddefef556476d94e3e31e42b6'
OWNER_ED25519_PUBLIC_KEY_SHA256 = None  # EXPLICIT OWNER HOLD; do not provision artificially
STATES = ('ADMITTED', 'TRAIN_COMMITTED', 'DEV_COMMITTED', 'FIT_FROZEN',
          'TEST_EXTRACT_CONSUMED', 'TEST_PACK_COMMITTED',
          'TEST_READ_CONSUMED', 'TERMINAL')
BUDGET_SECONDS = {'source': 3600.0, 'target': 3600.0}
RUN_SECONDS = 7200.0

class StopG1(RuntimeError):
    pass

def require(ok: bool, code: str):
    if not ok:
        raise StopG1('STOP_G1_' + code)

def canonical(value) -> bytes:
    return json.dumps(value, sort_keys=True, separators=(',', ':'),
                      ensure_ascii=True, allow_nan=False).encode('ascii')

def digest(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()

def guarded_regular(path: Path, root: Path, *, max_bytes: int = 16*1024*1024) -> bytes:
    """Reject symlink/junctions/hardlinks and stat opened file identity.

    This cannot replace OS principal separation or deny an ACL-capable actor.
    """
    root = Path(root).absolute(); path = Path(path).absolute()
    require(path != root and root in path.parents, 'OUTSIDE_PRIVATE_ROOT')
    require(root.is_dir(), 'PRIVATE_ROOT_MISSING')
    cur = root
    for item in (root, *(root / Path(*path.relative_to(root).parts[:i])
                             for i in range(1, len(path.relative_to(root).parts)+1))):
        if item.exists() or item.is_symlink():
            require(not item.is_symlink() and
                    not getattr(os.path, 'isjunction', lambda p: False)(item),
                    'REDIRECTED_PATH')
    flags = os.O_RDONLY | getattr(os, 'O_BINARY', 0) | getattr(os, 'O_NOFOLLOW', 0)
    fd = os.open(str(path), flags)
    try:
        st = os.fstat(fd); pst = path.stat(follow_symlinks=False)
        require(stat.S_ISREG(st.st_mode) and st.st_nlink == 1, 'HARDLINK_OR_NOT_REGULAR')
        require((st.st_dev, st.st_ino) == (pst.st_dev, pst.st_ino), 'FD_PATH_IDENTITY_CHANGED')
        require(0 <= st.st_size <= max_bytes, 'PRIVATE_SOURCE_SIZE')
        data = bytearray()
        while len(data) <= max_bytes:
            block = os.read(fd, min(1024*1024, max_bytes+1-len(data)))
            if not block: break
            data.extend(block)
        require(len(data) <= max_bytes, 'PRIVATE_SOURCE_OVERSIZE')
        return bytes(data)
    finally:
        os.close(fd)

class SimulatedControllerLedger:
    """Transaction-safe local prototype; NOT rollback-proof against its operator.

    A real controller must keep this DB outside the worker security principal and
    anchor each receipt to an external append-only witness. Current gate HOLD.
    """
    def __init__(self, controller_root: Path, worker_root: Path):
        self.root = Path(controller_root).resolve(strict=True)
        self.worker = Path(worker_root).resolve(strict=True)
        require(self.root != self.worker and self.root not in self.worker.parents and
                self.worker not in self.root.parents, 'CONTROLLER_WORKER_NOT_SEPARATE')
        require(not self.root.is_symlink() and not self.worker.is_symlink(), 'ROOT_REDIRECT')
        self.db = self.root / 'g1_admission_state.sqlite3'
        self.connection = sqlite3.connect(self.db, isolation_level=None, timeout=5)
        self.connection.execute('PRAGMA journal_mode=DELETE')
        self.connection.execute('PRAGMA synchronous=FULL')
        self.connection.execute('''CREATE TABLE IF NOT EXISTS state (
            run_id TEXT PRIMARY KEY, status TEXT NOT NULL, seq INTEGER NOT NULL,
            chain_sha TEXT NOT NULL, source_seconds REAL NOT NULL,
            target_seconds REAL NOT NULL, terminal INTEGER NOT NULL)''')
        self.connection.execute('''CREATE TABLE IF NOT EXISTS transitions (
            run_id TEXT NOT NULL, seq INTEGER NOT NULL, previous TEXT NOT NULL,
            next_state TEXT NOT NULL, payload_sha TEXT NOT NULL,
            chain_sha TEXT NOT NULL, PRIMARY KEY(run_id,seq))''')

    def close(self):
        self.connection.close()

    def admit_simulated(self, run_id: str, admitted_data: bytes):
        require(len(run_id) > 5 and all(c.isalnum() or c in '-_' for c in run_id), 'RUN_ID_FORMAT')
        require(0 < len(admitted_data) < 1024*1024, 'SIMULATION_ADMISSION_SIZE')
        self.connection.execute('BEGIN IMMEDIATE')
        try:
            chain = digest(b'G1_SIM_ADMISSION|' + run_id.encode() + b'|' + admitted_data)
            self.connection.execute('INSERT INTO state VALUES(?,?,?,?,?,?,?)',
                                    (run_id, 'ADMITTED', 0, chain, 0., 0., 0))
            self.connection.execute('COMMIT')
        except Exception:
            self.connection.execute('ROLLBACK')
            raise
        return chain

    def state(self, run_id: str) -> dict:
        row = self.connection.execute('SELECT * FROM state WHERE run_id=?', (run_id,)).fetchone()
        require(row is not None, 'RUN_NOT_ADMITTED')
        return dict(zip(('run_id','status','seq','chain_sha','source_seconds','target_seconds','terminal'), row))

    def advance(self, run_id: str, destination: str, payload_sha: str):
        require(destination in STATES, 'UNSUPPORTED_STATE')
        require(isinstance(payload_sha,str) and len(payload_sha)==64 and
                all(c in '0123456789abcdef' for c in payload_sha), 'BAD_PAYLOAD_HASH')
        self.connection.execute('BEGIN IMMEDIATE')
        try:
            row = self.connection.execute('SELECT status,seq,chain_sha,terminal FROM state WHERE run_id=?', (run_id,)).fetchone()
            require(row is not None and row[3] == 0, 'RUN_MISSING_OR_TERMINAL')
            prior, seq, prev_hash, _ = row
            require(destination == 'TERMINAL' or
                    STATES.index(destination)==STATES.index(prior)+1, 'NONMONOTONIC_TRANSITION')
            chain = digest(canonical({'run_id':run_id,'seq':seq+1,'prev':prev_hash,
                                      'state':destination,'payload_sha':payload_sha}))
            self.connection.execute('INSERT INTO transitions VALUES(?,?,?,?,?,?)',
                                    (run_id,seq+1,prior,destination,payload_sha,chain))
            self.connection.execute('UPDATE state SET status=?,seq=?,chain_sha=?,terminal=? WHERE run_id=?',
                                    (destination,seq+1,chain,int(destination=='TERMINAL'),run_id))
            self.connection.execute('COMMIT')
            return chain
        except Exception:
            self.connection.execute('ROLLBACK')
            raise

    def record_budget(self, run_id: str, model: str, spent: float):
        require(model in BUDGET_SECONDS, 'UNKNOWN_MODEL')
        require(type(spent) in (int,float) and 0 <= spent <= BUDGET_SECONDS[model], 'MODEL_TIMEOUT')
        self.connection.execute('BEGIN IMMEDIATE')
        try:
            row = self.connection.execute('SELECT source_seconds,target_seconds,terminal FROM state WHERE run_id=?',(run_id,)).fetchone()
            require(row is not None and row[2]==0, 'TERMINAL_OR_NO_RUN')
            values = {'source':row[0], 'target':row[1]}
            values[model] += spent
            require(values[model] <= BUDGET_SECONDS[model] and sum(values.values()) <= RUN_SECONDS,
                    'CUMULATIVE_GPU_TIMEOUT')
            self.connection.execute('UPDATE state SET source_seconds=?,target_seconds=? WHERE run_id=?',
                                    (values['source'],values['target'],run_id))
            self.connection.execute('COMMIT')
            return values
        except Exception:
            self.connection.execute('ROLLBACK'); raise

    def check_chain(self, run_id: str) -> bool:
        s = self.state(run_id)
        items = self.connection.execute('SELECT seq,previous,next_state,payload_sha,chain_sha FROM transitions WHERE run_id=? ORDER BY seq',(run_id,)).fetchall()
        require(len(items)==s['seq'], 'LEDGER_TRANSITION_GAP')
        if items:
            require(items[-1][-1] == s['chain_sha'], 'LEDGER_CHAIN_LAST_MISMATCH')
        for index, (seq,old,new,h,chain) in enumerate(items):
            require(seq==index+1, 'LEDGER_SEQUENCE_GAP')
            if index: require(items[index-1][2]==old,'LEDGER_STATE_CHAIN')
            if index: require(digest(canonical({'run_id':run_id,'seq':seq,'prev':items[index-1][-1],
                        'state':new,'payload_sha':h}))==chain, 'LEDGER_TAMPER')
        return True

    def release_test_synthetic(self, run_id: str, broker_root: Path) -> bytes:
        require(self.state(run_id)['status']=='FIT_FROZEN', 'TEST_BEFORE_FIT_FREEZE')
        source = Path(broker_root) / 'G1_PREFIX_TEST.json'
        # An external broker/ACL MUST enforce this same decision at file-open time.
        self.advance(run_id, 'TEST_EXTRACT_CONSUMED', digest(b'TEST_READ_INTENT'))
        try:
            return guarded_regular(source, broker_root, max_bytes=2*1024*1024)
        except BaseException:
            self.advance(run_id, 'TERMINAL', digest(b'TEST_OPEN_FAILED'))
            raise

    def commit_pack_synthetic(self, run_id: str, expected_state: str,
                              next_state: str, pack: bytes, file_name: str):
        # No trusted writer, no authenticated origin: simulated only, never real science.
        require(self.state(run_id)['status']==expected_state,'PACK_WRONG_STAGE')
        require(file_name in ('TRAIN.npz','DEV.npz','TEST.npz'), 'PACK_NAME_DENIED')
        require(0 < len(pack) < 12*1024*1024, 'PACK_SIZE')
        path=self.root/file_name
        require(not path.exists(), 'PACK_ALREADY_PRESENT')
        # Transition FIRST. Crash before/while writing leaves a non-retryable
        # terminal/mismatched ledger state requiring external adjudication.
        self.advance(run_id,next_state,digest(pack))
        stage=self.root/(file_name+'.pending.'+uuid.uuid4().hex)
        try:
            with stage.open('xb') as fd:
                fd.write(pack);fd.flush();os.fsync(fd.fileno())
            os.link(stage,path,follow_symlinks=False)
            stage.unlink()
            require(digest(guarded_regular(path,self.root))==digest(pack),'PACK_POSTCOMMIT_SHA')
        except BaseException:
            try:self.advance(run_id,'TERMINAL',digest(b'PACK_COMMIT_FAILED'))
            except Exception:pass
            raise
        return {'run_id':run_id,'sha256':digest(pack),'stage':next_state}


def production_admission_gate(*, owner_public_sha256=None, broker_acl_attested=False,
                              trusted_writer_attested=False, remote_witness_attested=False,
                              watchdog_attested=False, methods_approved=False):
    """Deliberately NOT an authorization API; no production key is provisioned.

    Parameters are not accepted as substitutes for independent custody and
    cryptographic attestation. There is no route to science from this module.
    """
    require(OWNER_ED25519_PUBLIC_KEY_SHA256 is not None, 'OWNER_TRUST_ROOT_NOT_PROVISIONED')
    require(False, 'PRODUCTION_INTEGRATION_REQUIRES_DISTINCT_REVIEW')


def supervised_child_synthetic(command: list[str], seconds: float) -> dict:
    """Kill-capable *synthetic* subprocess supervisor, not qualified for T4."""
    require(isinstance(command,list) and len(command)>=2 and all(isinstance(x,str) for x in command),'BAD_COMMAND')
    require(type(seconds) in (int,float) and 0 < seconds <= 30, 'SYNTHETIC_TIMEOUT_ONLY')
    p = subprocess.Popen(command, stdout=subprocess.PIPE, stderr=subprocess.PIPE,
                         start_new_session=(os.name!='nt'),
                         creationflags=(subprocess.CREATE_NEW_PROCESS_GROUP if os.name=='nt' else 0))
    began=time.monotonic()
    try:
        out,err=p.communicate(timeout=seconds)
        return {'exit':p.returncode,'timed_out':False,'elapsed_seconds':time.monotonic()-began,
                'stdout_size':len(out),'stderr_size':len(err)}
    except subprocess.TimeoutExpired:
        if os.name=='nt':
            subprocess.run(['taskkill','/PID',str(p.pid),'/T','/F'],check=False,
                           stdout=subprocess.DEVNULL,stderr=subprocess.DEVNULL)
        else:
            os.killpg(p.pid,signal.SIGKILL)
        p.communicate(timeout=5)
        return {'exit':p.returncode,'timed_out':True,'elapsed_seconds':time.monotonic()-began,
                'stdout_size':0,'stderr_size':0}
