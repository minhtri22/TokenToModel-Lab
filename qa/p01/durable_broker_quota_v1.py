"""Durable broker quota ledger candidate. Not a broker service or security boundary.

Must be hosted by a separately authenticated, ACL-isolated trusted process.
No evidence-file write, Windows spawn, or QA execution permit is offered here.
"""
import sqlite3
import time
from contextlib import contextmanager
from dataclasses import dataclass

MAX_BYTES = 2 * 1024**3
SCHEMA = """CREATE TABLE IF NOT EXISTS requests (
 request_id TEXT PRIMARY KEY COLLATE BINARY,
 name_key TEXT NOT NULL UNIQUE COLLATE BINARY,
 requested_bytes INTEGER NOT NULL CHECK(requested_bytes>=0),
 state TEXT NOT NULL CHECK(state IN ('PENDING','COMMITTED','FAILED_HELD')),
 created_epoch_ns INTEGER NOT NULL
);"""

class QuotaRefusal(PermissionError): pass

def _identifier(value, label):
    if type(value) is not str or not 1<=len(value)<=120:
        raise QuotaRefusal("INVALID_"+label)
    if not value.isascii() or not all(c.isalnum() or c in "._-" for c in value):
        raise QuotaRefusal("INVALID_"+label)
    if value.startswith(".") or value.endswith((".", " ")):
        raise QuotaRefusal("INVALID_"+label)
    return value

def _name_key(value):
    value=_identifier(value, "NAME")
    stem=value.split(".",1)[0].upper()
    if stem in ("CON","PRN","AUX","NUL") or (
        len(stem)==4 and stem[:3] in ("COM","LPT") and stem[3] in "123456789"
    ):
        raise QuotaRefusal("WINDOWS_DEVICE_NAME")
    return value.casefold()

@dataclass(frozen=True)
class Reservation:
    request_id: str
    name_key: str
    requested_bytes: int
    state: str

class DurableQuotaLedger:
    def __init__(self, db_path, *, limit_bytes=MAX_BYTES):
        # The trusted broker must separately pin DB identity, ACL and storage root.
        if type(db_path) is not str or not db_path or db_path==":memory:":
            raise QuotaRefusal("PERSISTENT_DB_REQUIRED")
        if type(limit_bytes) is not int or limit_bytes!=MAX_BYTES:
            raise QuotaRefusal("CANONICAL_QUOTA_REQUIRED")
        self.db_path=db_path
        self.limit_bytes=limit_bytes

    @contextmanager
    def connect(self):
        c=sqlite3.connect(self.db_path,timeout=10,isolation_level=None)
        try:
            c.execute("PRAGMA busy_timeout=10000")
            c.execute("PRAGMA synchronous=FULL")
            c.executescript(SCHEMA)
            yield c
        finally:
            c.close()

    def reserve(self, request_id, filename, size):
        request_id=_identifier(request_id,"REQUEST_ID")
        name_key=_name_key(filename)
        if type(size) is not int or not 0<=size<=self.limit_bytes:
            raise QuotaRefusal("INVALID_RESERVATION_SIZE")
        with self.connect() as db:
            try:
                db.execute("BEGIN IMMEDIATE")
                old=db.execute("SELECT name_key,requested_bytes,state FROM requests WHERE request_id=?",
                               (request_id,)).fetchone()
                if old is not None:
                    if old[0]!=name_key or old[1]!=size:
                        raise QuotaRefusal("REQUEST_ID_REPLAY_DIFFERENT_INTENT")
                    db.execute("COMMIT")
                    return Reservation(request_id,*old)
                held=db.execute("SELECT COALESCE(SUM(requested_bytes),0) FROM requests").fetchone()[0]
                if size>self.limit_bytes-held:
                    raise QuotaRefusal("AGGREGATE_QUOTA_EXCEEDED")
                if db.execute("SELECT 1 FROM requests WHERE name_key=?",(name_key,)).fetchone():
                    raise QuotaRefusal("CREATE_NEW_COLLISION")
                db.execute("INSERT INTO requests VALUES (?,?,?,?,?)",
                           (request_id,name_key,size,"PENDING",time.time_ns()))
                db.execute("COMMIT")
                return Reservation(request_id,name_key,size,"PENDING")
            except BaseException:
                if db.in_transaction: db.execute("ROLLBACK")
                raise

    def mark_committed(self,request_id,*,exact_size,verified_sha256):
        # Caller must independently verify file readback, not merely supply a hash.
        _identifier(request_id,"REQUEST_ID")
        if type(verified_sha256) is not str or len(verified_sha256)!=64 or any(
            c not in "0123456789abcdef" for c in verified_sha256):
            raise QuotaRefusal("UNVERIFIED_READBACK")
        with self.connect() as db:
            try:
                db.execute("BEGIN IMMEDIATE")
                old=db.execute("SELECT requested_bytes,state FROM requests WHERE request_id=?",
                               (request_id,)).fetchone()
                if old is None or old[1]!="PENDING" or type(exact_size) is not int or exact_size!=old[0]:
                    raise QuotaRefusal("INVALID_COMMIT_TRANSITION")
                db.execute("UPDATE requests SET state='COMMITTED' WHERE request_id=?",(request_id,))
                db.execute("COMMIT")
            except BaseException:
                if db.in_transaction: db.execute("ROLLBACK")
                raise

    def mark_failed_held(self,request_id):
        _identifier(request_id,"REQUEST_ID")
        with self.connect() as db:
            try:
                db.execute("BEGIN IMMEDIATE")
                changed=db.execute("UPDATE requests SET state='FAILED_HELD' WHERE request_id=? AND state='PENDING'",
                                   (request_id,)).rowcount
                if changed!=1: raise QuotaRefusal("INVALID_FAILURE_TRANSITION")
                db.execute("COMMIT")
            except BaseException:
                if db.in_transaction: db.execute("ROLLBACK")
                raise

    def snapshot(self):
        with self.connect() as db:
            return tuple(Reservation(*row) for row in db.execute(
                "SELECT request_id,name_key,requested_bytes,state FROM requests ORDER BY request_id"))
