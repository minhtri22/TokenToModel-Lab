#!/usr/bin/env python3
"""G1 trusted-boundary CONTRACT CANDIDATE, synthetic-only. Never authorizes science.

A conservative controller + *separately placed* filesystem witness prototype.
Witness and ledger must have independently controlled principals and a remote
monotonic trust anchor before any production data. Current key=None and real
admission is non-bypassably disabled.

This module does not import models, read a dataset or create scientific data.
"""
from __future__ import annotations

import hashlib
import json
import math
import os
from pathlib import Path
import re
import sqlite3
import stat
import subprocess
import sys
import time
import uuid

MANIFEST_SHA = "6451be0cd09a54378eda9e815b5c89ce8ce8301ddefef556476d94e3e31e42b6"
REVIEWED_V1C_HEAD = "d5d0c5346a595557a76349f900d09be50bce289c"
OWNER_PUBLIC_KEY_SHA256 = None  # Never insert a synthetic key here.
OWNER_SCIENCE_SCOPE_GRANTED = False
G1_SCIENCE_LOCK = "HOLD"
STATES = ("ADMITTED", "TRAIN_COMMITTED", "DEV_COMMITTED", "FIT_FROZEN",
          "TEST_EXTRACT_CONSUMED", "TEST_PACK_COMMITTED", "TEST_READ_CONSUMED", "TERMINAL")
SHA_RE = re.compile(r"^[0-9a-f]{64}$")
ID_RE = re.compile(r"^[A-Za-z0-9_-]{8,80}$")

class StopG1(RuntimeError):
    pass

def require(ok: bool, reason: str):
    if not ok:
        raise StopG1("STOP_G1_" + reason)

def canonical(value) -> bytes:
    return json.dumps(value, sort_keys=True, separators=(",", ":"),
                      ensure_ascii=True, allow_nan=False).encode("ascii")

def sha(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()

def root_proof(controller: Path, worker: Path, witness: Path):
    """Reject easy path alias; NOT evidence of distinct OS authority/ACL."""
    p = [Path(x).resolve(strict=True) for x in (controller, worker, witness)]
    for x in (controller, worker, witness):
        require(Path(x).is_dir() and not Path(x).is_symlink() and
                not getattr(os.path, "isjunction", lambda _: False)(x),
                "ROOT_REDIRECT")
    for i, a in enumerate(p):
        for b in p[i + 1:]:
            require(a != b and a not in b.parents and b not in a.parents,
                    "ROOTS_NOT_SEPARATE")
    return p

def read_no_alias(path: Path, root: Path, *, max_bytes=1024 * 1024) -> bytes:
    """Fail on known alias mechanisms, hash same opened bytes; no privileged ACL."""
    path = Path(path).absolute(); root = Path(root).absolute()
    require(path != root and root in path.parents and root.is_dir(), "READ_SCOPE")
    for p in (root, *(root.joinpath(*path.relative_to(root).parts[:i])
                      for i in range(1, len(path.relative_to(root).parts) + 1))):
        require(not p.is_symlink() and
                not getattr(os.path, "isjunction", lambda _: False)(p),
                "REDIRECTED_PATH")
    flags = os.O_RDONLY | getattr(os, "O_BINARY", 0) | getattr(os, "O_NOFOLLOW", 0)
    fd = os.open(str(path), flags)
    try:
        st = os.fstat(fd)
        check = path.stat(follow_symlinks=False)
        require(stat.S_ISREG(st.st_mode) and st.st_nlink == 1,
                "HARDLINK_OR_NONREGULAR")
        require((st.st_dev, st.st_ino) == (check.st_dev, check.st_ino),
                "OPEN_HANDLE_IDENTITY")
        require(0 <= st.st_size <= max_bytes, "FILE_SIZE")
        with os.fdopen(fd, "rb", closefd=False) as f:
            b = f.read(max_bytes + 1)
        require(len(b) <= max_bytes, "FILE_OVERSIZE")
        return b
    finally:
        os.close(fd)

class SyntheticFileWitness:
    """Independent *directory*, not independent credential/rollback domain.

    For each run an event is a distinct create-exclusive file. A real witness
    must be an authenticated append-only service operated by a distinct OS or
    remote principal. This candidate is never accepted as such.
    """
    def __init__(self, witness_root: Path):
        self.root = Path(witness_root).resolve(strict=True)
        require(self.root.is_dir(), "WITNESS_ROOT")

    def _run_dir(self, run_id):
        require(isinstance(run_id, str) and ID_RE.fullmatch(run_id), "RUN_ID")
        return self.root / run_id

    def _entry(self, run_id, seq):
        return self._run_dir(run_id) / ("%08d.json" % seq)

    def entries(self, run_id):
        rd = self._run_dir(run_id)
        if not rd.exists():
            return []
        require(rd.is_dir() and not rd.is_symlink(), "WITNESS_DIR_REDIRECT")
        out = []
        files = sorted(rd.iterdir())
        for idx, path in enumerate(files):
            require(path.name == "%08d.json" % idx, "WITNESS_SEQUENCE_GAP")
            record = json.loads(read_no_alias(path, rd, max_bytes=2048))
            require(type(record) is dict and record.get("run_id") == run_id and
                    record.get("seq") == idx and record.get("event_sha") and
                    isinstance(record.get("event_sha"), str) and
                    SHA_RE.fullmatch(record["event_sha"]), "WITNESS_RECORD_INVALID")
            out.append(record)
        return out

    def tip(self, run_id):
        arr = self.entries(run_id)
        return arr[-1] if arr else None

    def append(self, run_id, seq: int, event_sha: str):
        require(isinstance(event_sha, str) and SHA_RE.fullmatch(event_sha), "EVENT_SHA")
        require(type(seq) is int and seq >= 0, "EVENT_SEQ")
        rd = self._run_dir(run_id)
        if seq == 0:
            rd.mkdir(exist_ok=False)
        require(rd.is_dir() and not rd.is_symlink(), "WITNESS_ROOT_REDIRECT")
        previous = self.tip(run_id)
        require((previous is None and seq == 0) or
                (previous is not None and previous["seq"] + 1 == seq),
                "WITNESS_REPLAY_OR_GAP")
        payload = canonical({"run_id": run_id, "seq": seq, "event_sha": event_sha})
        target = self._entry(run_id, seq)
        with target.open("xb") as fd:
            fd.write(payload); fd.flush(); os.fsync(fd.fileno())
        require(read_no_alias(target, rd, max_bytes=2048) == payload,
                "WITNESS_POSTWRITE_HASH")
        return self.tip(run_id)

class WitnessedSimulationController:
    """SQLite/full-sync state + filesystem witness; synthetic only.

    Every state transition first commits locally, then asks the witness to
    confirm the same event hash. Loss of sync is terminal STOP, not a restart.
    A rollback of *only* the controller is detectable; simultaneous rollback
    of both domains is NOT protected by this simulated implementation.
    """
    def __init__(self, controller_root: Path, worker_root: Path, witness_root: Path):
        controller_root, worker_root, witness_root = root_proof(
            controller_root, worker_root, witness_root)
        self.root = controller_root; self.worker = worker_root
        self.witness = SyntheticFileWitness(witness_root)
        self.db_path = self.root / "ledger_sim_only.sqlite3"
        self.db = sqlite3.connect(self.db_path, isolation_level=None, timeout=2)
        self.db.execute("PRAGMA journal_mode=DELETE")
        self.db.execute("PRAGMA synchronous=FULL")
        self.db.execute("""CREATE TABLE IF NOT EXISTS runs (
            run_id TEXT PRIMARY KEY, seq INTEGER NOT NULL, state TEXT NOT NULL,
            event_sha TEXT NOT NULL, source_seconds REAL NOT NULL,
            target_seconds REAL NOT NULL, terminal INTEGER NOT NULL)""")
        self.db.execute("""CREATE TABLE IF NOT EXISTS events (
            run_id TEXT NOT NULL, seq INTEGER NOT NULL, state TEXT NOT NULL,
            payload_sha TEXT NOT NULL, event_sha TEXT NOT NULL,
            PRIMARY KEY(run_id,seq))""")

    def close(self):
        self.db.close()

    def state(self, run_id):
        row = self.db.execute("SELECT run_id,seq,state,event_sha,source_seconds,target_seconds,terminal FROM runs WHERE run_id=?", (run_id,)).fetchone()
        require(row is not None, "RUN_NOT_ADMITTED")
        return dict(zip(("run_id","seq","state","event_sha","source_seconds","target_seconds","terminal"), row))

    def verify_sync(self, run_id):
        state = self.state(run_id)
        tip = self.witness.tip(run_id)
        require(tip is not None and tip["seq"] == state["seq"] and
                tip["event_sha"] == state["event_sha"], "WITNESS_LEDGER_DIVERGED")
        ev = self.db.execute("SELECT seq,state,payload_sha,event_sha FROM events WHERE run_id=? ORDER BY seq", (run_id,)).fetchall()
        require(len(ev) == state["seq"] + 1 and
                all(x[0] == i for i, x in enumerate(ev)) and
                ev[-1][3] == tip["event_sha"], "EVENT_LOG_MISMATCH")
        for i, row in enumerate(ev):
            prior = "0" * 64 if i == 0 else ev[i-1][3]
            require(row[3] == sha(canonical({"run_id": run_id, "seq": i,
                         "prev": prior, "state": row[1], "payload_sha": row[2]})),
                    "EVENT_CHAIN_TAMPER")
        wit = self.witness.entries(run_id)
        require(len(wit) == len(ev) and all(wit[i]["event_sha"] == ev[i][3] for i in range(len(ev))),
                "WITNESS_EVENT_DIVERGENCE")
        return state

    def _record(self, run_id, seq, new_state, data_sha):
        previous = "0" * 64 if seq == 0 else self.state(run_id)["event_sha"]
        evsha = sha(canonical({"run_id": run_id, "seq": seq, "prev": previous,
                               "state": new_state, "payload_sha": data_sha}))
        self.db.execute("BEGIN IMMEDIATE")
        try:
            if seq == 0:
                self.db.execute("INSERT INTO runs VALUES (?,?,?,?,?,?,?)",
                                (run_id, 0, new_state, evsha, 0., 0., 0))
            else:
                self.db.execute("INSERT INTO events VALUES (?,?,?,?,?)",
                                (run_id,seq,new_state,data_sha,evsha))
                self.db.execute("UPDATE runs SET seq=?,state=?,event_sha=?,terminal=? WHERE run_id=?",
                                (seq,new_state,evsha,int(new_state=="TERMINAL"),run_id))
            if seq == 0:
                self.db.execute("INSERT INTO events VALUES (?,?,?,?,?)",
                                (run_id,0,new_state,data_sha,evsha))
            self.db.execute("COMMIT")
        except BaseException:
            self.db.execute("ROLLBACK")
            raise
        # The decision is not released to the caller until witness acknowledges.
        self.witness.append(run_id,seq,evsha)
        self.verify_sync(run_id)
        return evsha

    def admit(self, run_id, synthetic_payload: bytes):
        require(isinstance(run_id, str) and ID_RE.fullmatch(run_id), "RUN_ID")
        require(isinstance(synthetic_payload, bytes) and 1 <= len(synthetic_payload) <= 1024,
                "SYNTHETIC_ONLY_PAYLOAD")
        require(self.witness.tip(run_id) is None, "WITNESS_RUN_ALREADY_SEEN")
        require(self.db.execute("SELECT 1 FROM runs WHERE run_id=?", (run_id,)).fetchone() is None,
                "LEDGER_RUN_ALREADY_SEEN")
        return self._record(run_id,0,"ADMITTED",sha(synthetic_payload))

    def advance(self, run_id, to_state, payload_sha):
        require(isinstance(payload_sha,str) and SHA_RE.fullmatch(payload_sha), "PAYLOAD_SHA")
        before = self.verify_sync(run_id)
        require(before["terminal"] == 0, "RUN_TERMINAL")
        require(to_state in STATES and
                (to_state == "TERMINAL" or
                 STATES.index(to_state) == STATES.index(before["state"]) + 1),
                "STAGE_ORDER")
        return self._record(run_id,before["seq"]+1,to_state,payload_sha)

    def consume_test_before_open(self, run_id, test_source: Path, broker_root: Path):
        require(self.verify_sync(run_id)["state"] == "FIT_FROZEN", "TEST_NOT_RELEASED")
        # The witness acknowledgement MUST occur before any TEST handle is opened.
        self.advance(run_id, "TEST_EXTRACT_CONSUMED", sha(b"SYNTHETIC_TEST_INTENT"))
        try:
            return read_no_alias(test_source, broker_root, max_bytes=2*1024*1024)
        except BaseException:
            self.advance(run_id,"TERMINAL",sha(b"TEST_OPEN_STOP"))
            raise

    def commit_pack(self, run_id, split, payload: bytes):
        dest_state = {"TRAIN":"TRAIN_COMMITTED","DEV":"DEV_COMMITTED",
                      "TEST":"TEST_PACK_COMMITTED"}.get(split)
        require(dest_state is not None, "PACK_SPLIT")
        before = self.verify_sync(run_id)
        require(before["terminal"] == 0, "RUN_TERMINAL")
        if split == "TEST":
            require(before["state"] == "TEST_EXTRACT_CONSUMED", "PACK_STAGE")
        else:
            expected = "ADMITTED" if split == "TRAIN" else "TRAIN_COMMITTED"
            require(before["state"] == expected, "PACK_STAGE")
        require(isinstance(payload,bytes) and 0 < len(payload) <= 1024*1024, "PACK_SIZE_SYNTHETIC")
        path = self.root / ("SIM_PACK_"+split+".bin")
        # A crash before atomic publish may leave only a .staging file.  Never
        # mistake absence of final path for permission to rerun the stage.
        stale_stages = list(self.root.glob(path.name + ".staging.*"))
        require(not path.exists() and not path.is_symlink() and not stale_stages,
                "ORPHAN_OR_REPLAY_PACK")
        stage = self.root / (path.name+".staging."+uuid.uuid4().hex)
        try:
            with stage.open("xb") as fd:
                fd.write(payload);fd.flush();os.fsync(fd.fileno())
            os.link(stage,path,follow_symlinks=False)
            stage.unlink()
            require(read_no_alias(path,self.root,max_bytes=2*1024*1024)==payload,
                    "PACK_VERIFY")
            self.advance(run_id,dest_state,sha(payload))
        except BaseException:
            # If witness and ledger are in-sync we can adjudicate terminal,
            # otherwise record offline and deny further stage actions.
            try:
                if self.verify_sync(run_id)["terminal"] == 0:
                    self.advance(run_id,"TERMINAL",sha(b"PACK_FAILED"))
            except BaseException:
                pass
            raise
        return {"stage":dest_state,"sha256":sha(payload),"run_id":run_id}

    def terminal(self, run_id, reason):
        require(isinstance(reason,str) and 1<=len(reason)<=128,"TERMINAL_REASON")
        return self.advance(run_id,"TERMINAL",sha(reason.encode("ascii")))


def authorize_real_science(*, owner_key=None, ACL_verified=False,
                           independent_witness=False, watchdog_verified=False,
                           methods_approved=False):
    """NOT a permit issuing function. All flags are untrusted simulation input."""
    require(OWNER_PUBLIC_KEY_SHA256 is not None and OWNER_SCIENCE_SCOPE_GRANTED,
            "OWNER_PRODUCTION_SCOPE_NOT_GRANTED")
    raise StopG1("STOP_G1_REAL_PRODUCTION_RELEASE_NOT_IMPLEMENTED")


def supervised_synthetic_child(argv: list[str], timeout_seconds: float):
    """CPU-only subprocess kill demonstration. Not OS Job Object certification."""
    require(type(timeout_seconds) in (int,float) and math.isfinite(timeout_seconds)
            and 0 < timeout_seconds <= 20, "WATCHDOG_SYNTHETIC_TIMEOUT")
    require(isinstance(argv,list) and len(argv) >= 2 and all(isinstance(x,str) for x in argv),
            "WATCHDOG_ARGV")
    child = subprocess.Popen(argv, stdout=subprocess.PIPE, stderr=subprocess.PIPE,
              start_new_session=(os.name!="nt"),
              creationflags=(subprocess.CREATE_NEW_PROCESS_GROUP if os.name=="nt" else 0))
    try:
        out,err = child.communicate(timeout=timeout_seconds)
        return {"exit":child.returncode,"timeout":False,"stdout_bytes":len(out),"stderr_bytes":len(err)}
    except subprocess.TimeoutExpired:
        if os.name == "nt":
            subprocess.run(["taskkill","/T","/F","/PID",str(child.pid)],
                           stdout=subprocess.DEVNULL,stderr=subprocess.DEVNULL,check=False)
        else:
            import signal
            os.killpg(child.pid,signal.SIGKILL)
        child.communicate(timeout=5)
        return {"exit":child.returncode,"timeout":True,"stdout_bytes":0,"stderr_bytes":0}

if __name__ == "__main__":
    import argparse
    a=argparse.ArgumentParser()
    a.add_argument("--mode",choices=("status",),required=True)
    a.parse_args()
    print(json.dumps({"status":"SIMULATED_TRUST_BOUNDARY_ONLY",
                      "owner_authorized":False,"production_qualified":False,
                      "science_executed":False,"science_lock":G1_SCIENCE_LOCK},sort_keys=True))
