"""R8-D G2 prospective production trust-boundary candidate (NO SCIENCE DISPATCH).

The sole G3 dispatch adapter is deliberately NOT_REGISTERED.  This module builds
verifiable source/receipt/witness primitives for an independently reviewed future
integration.  It never creates R8 cases, a real allocation key or a G_pre lock.

Security boundary: a custodian-controlled process + protected storage and an
external monotonic witness, not Python class privacy or plain SQLite.
"""
from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Callable, Protocol, TypeVar
import hashlib
import hmac
import importlib.util
import json
import os
import re
import sqlite3
import subprocess
import sys
from contextlib import closing

SOURCE_COMMIT = '84d9d5c95e9962ccfe294852570e261b145fe403'
FROZEN_GPRE_SHA256 = '02626f9f0def5af90b57c2930898e96dbc8f6206c441bb4aaa4c4278ce0dddae'
FROZEN_CALLER_SHA256 = '3a9b249bced1b4ceaa5746d63367c017410ef82ded21ef386c3be2b1ee76b206'
RUNTIME_EXEC_SHA256 = '0b471133e110cfb53a061cad528ce8e517d7b9ac41a0a396c39ad795a487fc14'
SCHEMA = 'TTM_VM_R8_GPRE_HMAC_V2'
ALGORITHM = 'R8_GPRE_CANONICAL_JSON_COMPONENT_RANKING_V2'
REPO = 'minhtri22/TokenToModel-Lab'
HEX = re.compile('[a-f0-9]{64}\\Z')
TAG_RE = re.compile('[a-zA-Z0-9._-]{8,150}\\Z')
T = TypeVar('T')

class GateDenied(RuntimeError):
    """Fail closed BEFORE any call into a future case generator."""

def sha(raw: bytes) -> str:
    return hashlib.sha256(raw).hexdigest()

def _unique(pairs):
    out={}
    for k,v in pairs:
        if k in out:
            raise ValueError('DUPLICATE_JSON_KEY')
        out[k]=v
    return out

def _reject_constant(name):
    raise ValueError('NONFINITE_JSON')

def exact_json(raw: bytes):
    if type(raw) is not bytes:
        raise GateDenied('INVALID_JSON_BYTES')
    try:
        data=json.loads(raw.decode('utf-8',errors='strict'),object_pairs_hook=_unique,
                        parse_constant=_reject_constant)
        canonical=json.dumps(data,sort_keys=True,ensure_ascii=False,
                             separators=(',',':'),allow_nan=False).encode('utf-8')
    except (ValueError, TypeError, UnicodeError, OverflowError, RecursionError) as exc:
        raise GateDenied('INVALID_JSON_BYTES') from exc
    if canonical!=raw:
        raise GateDenied('NONCANONICAL_JSON')
    return data

def utc(value):
    if type(value) is not str:
        raise GateDenied('UNTRUSTED_TIMESTAMP')
    try:
        t=datetime.fromisoformat(value.replace('Z','+00:00'))
    except ValueError as exc:
        raise GateDenied('UNTRUSTED_TIMESTAMP') from exc
    if t.tzinfo is None or t.utcoffset()!=timezone.utc.utcoffset(t):
        raise GateDenied('UNTRUSTED_TIMESTAMP')
    return t.astimezone(timezone.utc)

def safe_read(path: Path, expected_digest: str) -> bytes:
    """Read+hash same bytes; reject symlink leaf; not an OS custody ACL proof."""
    if type(expected_digest) is not str or not HEX.fullmatch(expected_digest):
        raise GateDenied('UNPINNED_CONTENT')
    path=Path(path)
    if path.is_symlink() or not path.is_file():
        raise GateDenied('UNTRUSTED_FILE_PATH')
    raw=path.read_bytes()
    if not hmac.compare_digest(sha(raw),expected_digest):
        raise GateDenied('FILE_SHA256_PIN_MISMATCH')
    return raw

@dataclass(frozen=True)
class PrivatePrecommit:
    exact_envelope: bytes
    nonce: bytes
    blueprint_bytes: bytes
    lock_bytes: bytes

    def fields(self):
        if type(self.nonce) is not bytes or len(self.nonce)!=16:
            raise GateDenied('INVALID_GPRE_NONCE')
        d=exact_json(self.exact_envelope)
        if not isinstance(d,dict) or set(d)!={
            'schema','algorithm_id','session_id','source_commit',
            'source_manifest_sha256','runtime_manifest_sha256',
            'blueprint_sha256','lock_sha256'}:
            raise GateDenied('GPRE_ENVELOPE_FIELDS_INVALID')
        if d['schema']!=SCHEMA or d['algorithm_id']!=ALGORITHM or d['source_commit']!=SOURCE_COMMIT:
            raise GateDenied('GPRE_ALGORITHM_PIN_MISMATCH')
        if type(d['session_id']) is not str or not re.fullmatch('[A-Za-z0-9_-]{12,128}',d['session_id']):
            raise GateDenied('GPRE_SESSION_INVALID')
        for field in ('source_manifest_sha256','runtime_manifest_sha256','blueprint_sha256','lock_sha256'):
            if type(d[field]) is not str or not HEX.fullmatch(d[field]):
                raise GateDenied('GPRE_DIGEST_FORMAT_INVALID')
        if not hmac.compare_digest(d['blueprint_sha256'],sha(self.blueprint_bytes)) or \
           not hmac.compare_digest(d['lock_sha256'],sha(self.lock_bytes)):
            raise GateDenied('GPRE_PRIVATE_BYTE_MISMATCH')
        return d

    @property
    def digest(self):
        return sha(self.nonce+self.exact_envelope)

class CustodianPort(Protocol):
    def read_gpre(self, session_id: str) -> PrivatePrecommit: ...
    def use_private_key(self, session_id: str, operation: Callable[[bytes], T]) -> T: ...

@dataclass(frozen=True)
class CheckedCode:
    module: object
    actual_source_manifest_digest: str
    actual_runtime_manifest_digest: str

class FrozenCodeVerifier:
    """Pin the frozen algorithm's bytes before loading it from approved custody."""
    def __init__(self, source_dir: Path, *, production: bool=True):
        self.source_dir=Path(source_dir)
        self.production=production

    def check(self, expected_source_manifest: str, expected_runtime_manifest: str,
              source_manifest_path: Path, runtime_manifest_path: Path) -> CheckedCode:
        if self.production:
            if sys.version_info[:2]!=(3,12):
                raise GateDenied('PYTHON_312_REQUIRED')
            if sha(Path(sys.executable).read_bytes())!=RUNTIME_EXEC_SHA256:
                raise GateDenied('PINNED_RUNTIME_EXECUTABLE_MISMATCH')
        frozen=self.source_dir/'folds_raters.py'
        caller=self.source_dir/'r8_production_caller.py'
        safe_read(frozen,FROZEN_GPRE_SHA256 if self.production else sha(frozen.read_bytes()))
        safe_read(caller,FROZEN_CALLER_SHA256 if self.production else sha(caller.read_bytes()))
        src=safe_read(source_manifest_path,expected_source_manifest)
        run=safe_read(runtime_manifest_path,expected_runtime_manifest)
        src_obj=exact_json(src)
        runtime_obj=exact_json(run)
        if not isinstance(src_obj,dict) or not isinstance(runtime_obj,dict):
            raise GateDenied('MANIFEST_STRUCTURE_INVALID')
        # Every manifest must cover the modules and executable that are actually used.
        if (src_obj.get('source_commit')!=SOURCE_COMMIT or
            src_obj.get('folds_raters_sha256')!=sha(frozen.read_bytes()) or
            src_obj.get('r8_production_caller_sha256')!=sha(caller.read_bytes())):
            raise GateDenied('SOURCE_MANIFEST_BINDING_INVALID')
        if runtime_obj.get('python_version')!=f'{sys.version_info.major}.{sys.version_info.minor}':
            raise GateDenied('RUNTIME_VERSION_MANIFEST_MISMATCH')
        if runtime_obj.get('executable_sha256')!=sha(Path(sys.executable).read_bytes()):
            raise GateDenied('RUNTIME_BINARY_MANIFEST_MISMATCH')
        if self.production:
            from importlib import metadata
            for package,expected in (('numpy','2.3.5'),('scipy','1.17.0'),('scikit-learn','1.8.0')):
                if metadata.version(package)!=expected:
                    raise GateDenied('RUNTIME_PACKAGE_PIN_MISMATCH')
        # Frozen source is hash-verified prior to executing it. Do not import from cwd.
        spec=importlib.util.spec_from_file_location('_r8_frozen_gpre_source_pin',frozen)
        if not spec or not spec.loader:
            raise GateDenied('FROZEN_MODULE_UNLOADABLE')
        mod=importlib.util.module_from_spec(spec)
        spec.loader.exec_module(mod)
        if Path(mod.__file__).resolve()!=frozen.resolve():
            raise GateDenied('FROZEN_MODULE_RESOLUTION_MISMATCH')
        return CheckedCode(mod,sha(src),sha(run))

def validate_hmac_v2(pre: PrivatePrecommit, code: CheckedCode, custodian: CustodianPort):
    """Recompute locked V2 preassignment with private key supplied by custodian.

    The key never appears in the public API, receipts or audit fields.  Caller
    cannot make a fake 64-hex HMAC pass this check.  Forbidden: regenerate lock.
    """
    fields=pre.fields()
    blueprints=exact_json(pre.blueprint_bytes)
    lock=exact_json(pre.lock_bytes)
    if not isinstance(blueprints,list) or not isinstance(lock,dict):
        raise GateDenied('INVALID_GPRE_LOCK_OR_BLUEPRINT')
    if lock.get('lock_schema')!=SCHEMA or lock.get('algorithm_id')!=ALGORITHM:
        raise GateDenied('INVALID_GPRE_LOCK_VERSION')
    def recompute(secret):
        if type(secret) is not bytes or len(secret)<32:
            raise GateDenied('CUSTODIAN_KEY_INVALID')
        return code.module.preassign_r8(blueprints,secret)
    try:
        expected=custodian.use_private_key(fields['session_id'],recompute)
    except GateDenied:
        raise
    except Exception as exc:
        raise GateDenied('CUSTODIAN_HMAC_VERIFICATION_FAILED') from exc
    if not isinstance(expected,dict) or set(lock)!=set(expected):
        raise GateDenied('GPRE_LOCK_MISMATCH')
    for key,value in expected.items():
        if key in ('preassignment_hmac','blueprint_hmac'):
            if type(value) is not str or type(lock.get(key)) is not str or not hmac.compare_digest(value,lock[key]):
                raise GateDenied('GPRE_HMAC_NOT_AUTHENTIC')
        elif lock.get(key)!=value:
            raise GateDenied('GPRE_FOLD_ASSIGNMENT_CHANGED')
    if lock.get('cv_status')!='PREFOLD_READY_NOT_VALIDATED':
        raise GateDenied('GPRE_NOT_ESTIMABLE')

@dataclass(frozen=True)
class GitHubAnchor:
    tag: str
    asset_digest: str
    published_at: str
    exact_asset_bytes: bytes
    remote_id: int

class GhReleaseVerifier:
    """Use GitHub's own signed release/asset verification, never caller flags.

    Required gh commands are documented at cli.github.com/manual/gh_release_verify
    and cli.github.com/manual/gh_release_verify-asset.  Server published time
    is not a trusted signed timestamp; verify signed time separately at admission.
    """
    def __init__(self, gh_binary: Path, *, runner=None):
        self.gh=str(gh_binary)
        self.runner=runner or subprocess.run

    def _run(self, args, *, max_stdout=100000):
        try:
            p=self.runner([self.gh,*args],shell=False,timeout=25,
                          capture_output=True,text=True,check=False)
        except (OSError,subprocess.TimeoutExpired) as exc:
            raise GateDenied('GH_VERIFICATION_UNAVAILABLE') from exc
        if p.returncode!=0 or len(p.stdout)>max_stdout:
            raise GateDenied('GH_CRYPTOGRAPHIC_VERIFICATION_FAILED')
        return p.stdout

    def verify(self,tag: str, asset_path: Path, expected_digest: str) -> GitHubAnchor:
        if type(tag) is not str or not TAG_RE.fullmatch(tag):
            raise GateDenied('RELEASE_TAG_INVALID')
        raw=safe_read(asset_path,expected_digest)
        self._run(['release','verify',tag,'-R',REPO])
        self._run(['release','verify-asset',tag,str(asset_path),'-R',REPO])
        remote=json.loads(self._run(['api',f'repos/{REPO}/releases/tags/{tag}']))
        if (type(remote) is not dict or remote.get('immutable') is not True or
            remote.get('tag_name')!=tag or type(remote.get('id')) is not int or
            not remote.get('published_at')):
            raise GateDenied('REMOTE_RELEASE_IDENTITY_UNVERIFIED')
        assets=[a for a in remote.get('assets',[]) if a.get('name')==asset_path.name]
        if len(assets)!=1 or assets[0].get('digest')!='sha256:'+sha(raw) or \
           type(assets[0].get('id')) is not int:
            raise GateDenied('REMOTE_ASSET_DIGEST_UNVERIFIED')
        return GitHubAnchor(tag,sha(raw),remote['published_at'],raw,remote['id'])

@dataclass(frozen=True)
class IndependentlyAcceptedReceipt:
    session_id: str
    commitment_digest: str
    release_tag: str
    release_asset_sha256: str
    signed_timestamp_utc: str
    acceptance_timestamp_utc: str
    amendment_review_commit: str
    accepted: bool

class IndependentAcceptanceVerifier(Protocol):
    def verify_independently_signed(self, *, session_id: str, digest: str) -> IndependentlyAcceptedReceipt: ...

@dataclass(frozen=True)
class WitnessReceipt:
    session_id: str
    commitment_digest: str
    witness_event_id: str
    signature_verified: bool

class MonotonicWitness(Protocol):
    """A remote CAS register that cannot be restored with the local SQLite DB."""
    def reserve_once(self,session_id: str,digest: str) -> WitnessReceipt: ...
    def read_verified(self,session_id: str) -> WitnessReceipt: ...

class UnavailableWitness:
    def reserve_once(self,session_id,digest):
        raise GateDenied('EXTERNAL_ANTIROLLBACK_WITNESS_NOT_CONFIGURED')
    def read_verified(self,session_id):
        raise GateDenied('EXTERNAL_ANTIROLLBACK_WITNESS_NOT_CONFIGURED')

class AntiRollbackConsumptionLedger:
    """Local audit + *external* monotonic reserve; SQLite is never authority.

    A filesystem rollback can erase SQLite, but the separate signed monotonic
    witness must reject a second reserve.  Production cannot pass a mock witness
    without a distinct custodian OS/process attestation (NOT provided here).
    """
    def __init__(self, local_db: Path, witness: MonotonicWitness):
        self.path=Path(local_db)
        self.witness=witness

    def consume(self,session_id: str,digest: str):
        if not self.path.parent.is_dir() or self.path.is_symlink():
            raise GateDenied('LEDGER_CUSTODY_PATH_INVALID')
        if self.path.exists() and not self.path.is_file():
            raise GateDenied('LEDGER_CUSTODY_PATH_INVALID')
        if self.path.exists() and self.path.stat().st_nlink!=1:
            raise GateDenied('LEDGER_MULTILINK_DENIED')
        # MUST occur first, before any local ledger write, and is globally atomic.
        external=self.witness.reserve_once(session_id,digest)
        if (not isinstance(external,WitnessReceipt) or external.signature_verified is not True or
            external.session_id!=session_id or external.commitment_digest!=digest or
            not external.witness_event_id):
            raise GateDenied('EXTERNAL_WITNESS_UNTRUSTED')
        try:
            with closing(sqlite3.connect(self.path,timeout=10,isolation_level=None)) as db:
                db.execute('PRAGMA synchronous=FULL')
                db.execute('PRAGMA journal_mode=DELETE')
                db.execute('BEGIN IMMEDIATE')
                db.execute('CREATE TABLE IF NOT EXISTS consumed ('
                           'session_id TEXT PRIMARY KEY, digest TEXT NOT NULL UNIQUE, '
                           'witness_id TEXT NOT NULL UNIQUE)')
                ddl=db.execute("SELECT sql FROM sqlite_master WHERE name='consumed'").fetchone()
                canonical='CREATE TABLE consumed (session_id TEXT PRIMARY KEY, digest TEXT NOT NULL UNIQUE, witness_id TEXT NOT NULL UNIQUE)'
                if not ddl or ' '.join(ddl[0].replace('IF NOT EXISTS','').split()).lower()!=canonical.lower():
                    raise GateDenied('LEDGER_SCHEMA_UNTRUSTED')
                if db.execute("SELECT count(*) FROM sqlite_master WHERE type='trigger'").fetchone()[0]:
                    raise GateDenied('LEDGER_TRIGGER_UNTRUSTED')
                db.execute('INSERT INTO consumed VALUES(?,?,?)',
                           (session_id,digest,external.witness_event_id))
                db.execute('COMMIT')
        except (sqlite3.Error,OSError) as exc:
            # Global witness token is ALREADY consumed; fail closed rather than
            # retry it.  Do not release/reissue the external commitment token.
            raise GateDenied('LEDGER_PERSISTENCE_FAILED_TOKEN_CONSUMED') from exc
        latest=self.witness.read_verified(session_id)
        if (not isinstance(latest,WitnessReceipt) or latest.signature_verified is not True or
            latest!=external):
            raise GateDenied('WITNESS_CHANGED_AFTER_CONSUME')
        return external

class VerifiedAdmissionCore:
    """Testable sequence, not an independently admitted production integration."""
    def __init__(self, custodian: CustodianPort, code: FrozenCodeVerifier,
                 release: GhReleaseVerifier, acceptor: IndependentAcceptanceVerifier,
                 ledger: AntiRollbackConsumptionLedger, *,
                 source_manifest_path: Path, runtime_manifest_path: Path, asset_path: Path,
                 signed_timestamp_checker: Callable[[IndependentlyAcceptedReceipt], bool]):
        self._custodian=custodian
        self._code=code
        self._release=release
        self._acceptor=acceptor
        self._ledger=ledger
        self._source_manifest_path=source_manifest_path
        self._runtime_manifest_path=runtime_manifest_path
        self._asset_path=asset_path
        self._signed_time_check=signed_timestamp_checker

    def validate_and_consume(self,session_id: str,tag: str):
        pre=self._custodian.read_gpre(session_id)
        if not isinstance(pre,PrivatePrecommit):
            raise GateDenied('PRIVATE_CUSTODY_ENVELOPE_MISSING')
        fields=pre.fields()
        if fields['session_id']!=session_id:
            raise GateDenied('CUSTODY_SESSION_MISMATCH')
        code=self._code.check(fields['source_manifest_sha256'],fields['runtime_manifest_sha256'],
                              self._source_manifest_path,self._runtime_manifest_path)
        validate_hmac_v2(pre,code,self._custodian)
        asset=self._release.verify(tag,self._asset_path,sha(self._asset_path.read_bytes()))
        claim=exact_json(asset.exact_asset_bytes)
        if not isinstance(claim,dict) or claim.get('public_digest')!=pre.digest or \
           claim.get('source_commit')!=SOURCE_COMMIT or \
           claim.get('session_id')!=session_id or \
           claim.get('source_manifest_sha256')!=fields['source_manifest_sha256'] or \
           claim.get('runtime_manifest_sha256')!=fields['runtime_manifest_sha256']:
            raise GateDenied('PUBLIC_GPRE_RELEASE_BINDING_MISMATCH')
        receipt=self._acceptor.verify_independently_signed(session_id=session_id,digest=pre.digest)
        if not isinstance(receipt,IndependentlyAcceptedReceipt) or receipt.accepted is not True or \
           receipt.session_id!=session_id or receipt.commitment_digest!=pre.digest or \
           receipt.release_tag!=tag or receipt.release_asset_sha256!=asset.asset_digest or \
           not re.fullmatch('[a-f0-9]{40}',receipt.amendment_review_commit) or \
           receipt.amendment_review_commit=='0'*40 or self._signed_time_check(receipt) is not True:
            raise GateDenied('INDEPENDENT_GPRE_ACCEPTANCE_NOT_AUTHENTIC')
        published=utc(asset.published_at)
        signed=utc(receipt.signed_timestamp_utc)
        accepted=utc(receipt.acceptance_timestamp_utc)
        if not published < signed < accepted <= datetime.now(timezone.utc):
            raise GateDenied('GPRE_PROSPECTIVE_TIMESTAMP_ORDER_INVALID')
        # Revalidate the signed release before consuming any authorization.
        refreshed=self._release.verify(tag,self._asset_path,asset.asset_digest)
        if refreshed!=asset:
            raise GateDenied('ANCHOR_DISAPPEARED_OR_CHANGED')
        return self._ledger.consume(session_id,pre.digest)

class ProductionG3Gateway:
    """Single public entrypoint: intentionally closed until audited generator.

    There is no registered G3 generator in the frozen scientific source tree.
    A caller must not supply a lambda, fake verifier or fixture_mode flag here.
    """
    def __init__(self):
        pass
    def launch(self, session_id: str, tag: str):
        raise GateDenied('PRODUCTION_G3_GENERATOR_NOT_REGISTERED_OR_AUTHORIZED')
