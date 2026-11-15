"""R8-D pre-G3 production trust-boundary *candidate*, not an execution permit.

Require external proof, exact frozen source HMAC V2, executable package custody,
independent release approval, and a remote one-shot consumption anchor BEFORE
calling any registered generator. No G3 generator or production permit is
registered here. This source does not claim Windows ACL or retention attestation.
"""
from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timezone
import hashlib
import ctypes
import importlib.metadata
import importlib
import json
import os
from pathlib import Path
import subprocess
import sys
import tempfile
import types
from typing import Protocol

from pre_g3_admission_guard import (
    AdmissionDenied, PrivateEnvelope, SOURCE_COMMIT, SCHEMA, ALGORITHM,
    _digest, _utc, _reject_duplicate_keys,
)

REPO = "minhtri22/TokenToModel-Lab"
FROZEN_SHA = {
    "folds_raters.py": "02626f9f0def5af90b57c2930898e96dbc8f6206c441bb4aaa4c4278ce0dddae",
    "r8_production_caller.py": "3a9b249bced1b4ceaa5746d63367c017410ef82ded21ef386c3be2b1ee76b206",
    "test_g0_algorithm_version_binding.py": "2ce86fe549e1625790fcab72c076df2f12d648b048a350570d5c97a026431ae2",
    "gold_contract.py": "8e8b81ce2d0bc47cc60c29abc7156fe9d97613e67983e43b7f587615d68015a5",
    "restricted_oracles.py": "34ab74d36b822703e4d8cbdf281e142273d55d181243d904b55fd31a0e6382a1",
}
PACKAGES = {"numpy": "2.3.5", "scipy": "1.17.0", "scikit-learn": "1.8.0"}


def strict_json(raw: bytes):
    try:
        data = json.loads(raw.decode("utf-8", "strict"),
                          object_pairs_hook=_reject_duplicate_keys,
                          parse_constant=lambda x: (_ for _ in ()).throw(ValueError(x)))
    except (UnicodeError, TypeError, ValueError, OverflowError) as exc:
        raise AdmissionDenied("UNTRUSTED_JSON_BYTES") from exc
    return data


def canonical(data) -> bytes:
    try:
        return json.dumps(data, sort_keys=True, separators=(",", ":"),
                          ensure_ascii=False, allow_nan=False).encode("utf-8")
    except (TypeError, ValueError, UnicodeError, OverflowError) as exc:
        raise AdmissionDenied("INVALID_CANONICAL_CONTENT") from exc


def _sha_file(p: Path) -> str:
    try:
        if p.is_symlink() or not p.is_file() or p.stat().st_nlink != 1:
            raise AdmissionDenied("SOURCE_FILE_ALIAS_REJECTED")
        return _digest(p.read_bytes())
    except (OSError, PermissionError) as exc:
        raise AdmissionDenied("SOURCE_READBACK_FAILED") from exc


@dataclass(frozen=True)
class PinnedCustody:
    """The local protected source root/key supplied by authorized custodian.

    Source/path ACL verification belongs to Windows native attestation, not to
    pathlib (which cannot attest DACL, file handles, reparse and token identity).
    """

    source_root: Path
    runtime_manifest_path: Path
    python_exe_sha256: str

    def verify(self, expected_source_manifest_sha256: str, expected_runtime_sha256: str) -> bytes:
        root = self.source_root
        if not root.is_dir() or root.is_symlink():
            raise AdmissionDenied("PROTECTED_SOURCE_ROOT_UNVERIFIED")
        # Hash all five exact byte pins each admission; no public checkout fallback.
        hashes = {}
        for filename, expected in FROZEN_SHA.items():
            full = root / filename
            if not full.resolve().parent == root.resolve():
                raise AdmissionDenied("SOURCE_TRAVERSAL_OR_REPARSE")
            actual = _sha_file(full)
            if actual != expected:
                raise AdmissionDenied("FROZEN_SOURCE_HASH_MISMATCH")
            hashes[filename] = actual
        if _digest(canonical(hashes)) != expected_source_manifest_sha256:
            raise AdmissionDenied("SOURCE_MANIFEST_READBACK_MISMATCH")
        if not (sys.version_info.major == 3 and sys.version_info.minor == 12):
            raise AdmissionDenied("RUNTIME_PYTHON_VERSION_MISMATCH")
        if _sha_file(Path(sys.executable)) != self.python_exe_sha256:
            raise AdmissionDenied("RUNTIME_EXECUTABLE_ID_MISMATCH")
        for name, version in PACKAGES.items():
            if importlib.metadata.version(name) != version:
                raise AdmissionDenied("RUNTIME_DEPENDENCY_VERSION_MISMATCH")
        # Bind runtime manifest's exact bytes, not any claimed hash string.
        if _sha_file(self.runtime_manifest_path) != expected_runtime_sha256:
            raise AdmissionDenied("RUNTIME_MANIFEST_READBACK_MISMATCH")
        metadata = strict_json(self.runtime_manifest_path.read_bytes())
        if not isinstance(metadata, dict) or metadata.get("source_commit") != SOURCE_COMMIT:
            raise AdmissionDenied("RUNTIME_MANIFEST_INVALID")
        if metadata.get("python_exe_sha256") != self.python_exe_sha256:
            raise AdmissionDenied("RUNTIME_MANIFEST_EXECUTABLE_MISMATCH")
        if metadata.get("packages") != PACKAGES:
            raise AdmissionDenied("RUNTIME_MANIFEST_PACKAGE_MISMATCH")
        loaded = metadata.get("loaded_modules")
        if not isinstance(loaded, dict) or set(loaded) != set(PACKAGES):
            raise AdmissionDenied("RUNTIME_MODULE_PIN_SET_MISSING")
        for module_name in PACKAGES:
            # Runtime module is imported and checked against a private manifest;
            # package-name/version metadata alone is not an executable byte pin.
            name = module_name.replace("-", "_")
            module = importlib.import_module(name)
            full = Path(module.__file__).resolve(strict=True)
            if not full.is_relative_to(Path(sys.prefix).resolve(strict=True)):
                raise AdmissionDenied("RUNTIME_MODULE_OUTSIDE_PINNED_ENV")
            target = loaded[module_name]
            if (not isinstance(target, dict) or target.get("sha256") != _sha_file(full)
                    or target.get("path") != str(full)):
                raise AdmissionDenied("LOADED_MODULE_BYTE_IDENTITY_MISMATCH")
        # Module source used for HMAC executes exact pinned file, never sys.path.
        return (root / "folds_raters.py").read_bytes()


def authenticate_hmac_v2(envelope: PrivateEnvelope, custodian_key: bytes,
                         frozen_fold_source: bytes) -> None:
    """Recompute exact frozen V2 preassignment from the custodian key and blueprint.

    No new key/nonce/blueprint is created here, and no cases are generated.
    """
    envelope.parse_and_validate()
    if not isinstance(custodian_key, bytes) or len(custodian_key) < 32:
        raise AdmissionDenied("CUSTODIAN_HMAC_KEY_INVALID")
    if _digest(frozen_fold_source) != FROZEN_SHA["folds_raters.py"]:
        raise AdmissionDenied("FROZEN_FOLD_IMPLEMENTATION_MISMATCH")
    manifest = strict_json(envelope.blueprint_bytes)
    lock = strict_json(envelope.lock_bytes)
    if not isinstance(manifest, list) or not isinstance(lock, dict):
        raise AdmissionDenied("GPRE_BLUEPRINT_OR_LOCK_TYPE_INVALID")
    if canonical(manifest) != envelope.blueprint_bytes or canonical(lock) != envelope.lock_bytes:
        raise AdmissionDenied("GPRE_NONCANONICAL_BYTES")
    # Compile the pinned byte source without sys.path injection and call its
    # existing V2 validator/algorithm. Python bytecode caching disabled by design.
    module = types.ModuleType("_ttm_pinned_folds_raters_r8")
    module.__file__ = "<verified-frozen-folds_raters.py>"
    try:
        exec(compile(frozen_fold_source, module.__file__, "exec"), module.__dict__)
        expected = module.preassign_r8(manifest, custodian_key)
    except (ValueError, TypeError, KeyError, AssertionError) as exc:
        raise AdmissionDenied("FROZEN_HMAC_PREASSIGNMENT_REJECTED") from exc
    if expected.get("cv_status") != "PREFOLD_READY_NOT_VALIDATED":
        raise AdmissionDenied("R8_FOLD_NOT_READY")
    if canonical(expected) != envelope.lock_bytes:
        raise AdmissionDenied("GPRE_LOCK_HMAC_OR_FOLD_MISMATCH")
    # Do not expose the real fold map, key or blueprint in public receipts.


@dataclass(frozen=True)
class ReleaseProof:
    tag: str
    asset_name: str
    asset_sha256: str
    signed_at: datetime
    published_at: datetime
    checked_at: datetime
    body: dict
    release_author: str


class WindowsDPAPIKeyReader:
    """Read EXISTING custodian DPAPI CurrentUser ciphertext; never create a key.

    Windows profile and ACL/owner attestation must be checked out-of-process by
    the authorized custodian. This helper is not a substitute for DACL QA.
    """

    def __init__(self, private_root: Path, encrypted_key_path: Path):
        self.private_root = Path(private_root)
        self.encrypted_key_path = Path(encrypted_key_path)

    def read_key(self) -> bytes:
        if sys.platform != "win32":
            raise AdmissionDenied("DPAPI_CURRENTUSER_REQUIRES_WINDOWS")
        try:
            root = self.private_root.resolve(strict=True)
            full = self.encrypted_key_path.resolve(strict=True)
            if not full.is_relative_to(root) or self.encrypted_key_path.is_symlink():
                raise AdmissionDenied("DPAPI_CIPHERTEXT_NOT_IN_CUSTODY")
            encrypted = self.encrypted_key_path.read_bytes()
            if not encrypted or len(encrypted) > 16384:
                raise AdmissionDenied("DPAPI_CIPHERTEXT_INVALID")
            from ctypes import wintypes
            class BLOB(ctypes.Structure):
                _fields_ = [("cbData", wintypes.DWORD),
                            ("pbData", ctypes.POINTER(ctypes.c_ubyte))]
            input_buf = (ctypes.c_ubyte * len(encrypted)).from_buffer_copy(encrypted)
            inp = BLOB(len(encrypted), ctypes.cast(input_buf, ctypes.POINTER(ctypes.c_ubyte)))
            out = BLOB()
            crypt32 = ctypes.WinDLL("Crypt32.dll", use_last_error=True)
            kernel32 = ctypes.WinDLL("Kernel32.dll", use_last_error=True)
            crypt32.CryptUnprotectData.argtypes = [ctypes.POINTER(BLOB), ctypes.c_void_p,
                ctypes.c_void_p, ctypes.c_void_p, ctypes.c_void_p,
                wintypes.DWORD, ctypes.POINTER(BLOB)]
            crypt32.CryptUnprotectData.restype = wintypes.BOOL
            kernel32.LocalFree.argtypes = [ctypes.c_void_p]
            kernel32.LocalFree.restype = ctypes.c_void_p
            if not crypt32.CryptUnprotectData(ctypes.byref(inp), None, None,
                                                None, None, 0, ctypes.byref(out)):
                raise AdmissionDenied("DPAPI_CURRENTUSER_DECRYPT_DENIED")
            try:
                key = ctypes.string_at(out.pbData, out.cbData)
            finally:
                ctypes.memset(out.pbData, 0, out.cbData)
                kernel32.LocalFree(ctypes.cast(out.pbData, ctypes.c_void_p))
            if len(key) < 32:
                raise AdmissionDenied("CUSTODIAN_HMAC_KEY_INVALID")
            return key
        except AdmissionDenied:
            raise
        except (OSError, ValueError, PermissionError, AttributeError) as exc:
            raise AdmissionDenied("DPAPI_CUSTODY_READ_FAILED") from exc


class KeyProvider(Protocol):
    def read_key(self) -> bytes: ...


class ReleaseAuthority(Protocol):
    def verify(self, tag: str, asset_name: str) -> ReleaseProof: ...
    def consume_once(self, tag: str, asset_name: str, exact_asset: bytes) -> ReleaseProof: ...


class GitHubReleaseAuthority:
    """Github CLI backed verifier. Requires pinned gh.exe in protected Windows runtime.

    A failure of GitHub API, signature, or JSON timestamp extraction is a DENY.
    This is an implementation candidate: live remote/Windows attestation remains
    NOT_EXECUTED. Do not claim signed timestamp without verifiedTimestamps.
    """

    def __init__(self, gh_executable: Path, expected_gh_sha256: str):
        self.gh = Path(gh_executable)
        if _sha_file(self.gh) != expected_gh_sha256:
            raise AdmissionDenied("GH_EXECUTABLE_NOT_PINNED")

    def _run(self, *args: str) -> str:
        try:
            result = subprocess.run([str(self.gh), *args], check=False,
                                    capture_output=True, text=True, timeout=45,
                                    env={**os.environ, "GH_PROMPT_DISABLED": "1"})
        except (OSError, subprocess.TimeoutExpired) as exc:
            raise AdmissionDenied("GH_COMMAND_UNAVAILABLE") from exc
        if result.returncode != 0 or len(result.stdout) > 3_000_000:
            raise AdmissionDenied("GH_REMOTE_OR_SIGNATURE_VERIFY_FAILED")
        return result.stdout

    @staticmethod
    def _signed_verified_times(obj) -> list[datetime]:
        # Only verificationResult.verifiedTimestamps from GH verified output
        # counts. Do not accept timestamps in user-controlled predicate fields.
        entries = []
        def descend(node):
            if isinstance(node, dict):
                v = node.get("verificationResult")
                if isinstance(v, dict) and isinstance(v.get("verifiedTimestamps"), list):
                    for item in v["verifiedTimestamps"]:
                        if isinstance(item, dict) and isinstance(item.get("timestamp"), str):
                            entries.append(_utc(item["timestamp"]))
                for k, x in node.items():
                    if k != "verificationResult":
                        descend(x)
            elif isinstance(node, list):
                for item in node: descend(item)
        descend(obj)
        return entries

    def verify(self, tag: str, asset_name: str) -> ReleaseProof:
        if not isinstance(tag, str) or not tag.startswith("ttm-vm-v4-r8-") or not tag.replace("-", "").isalnum():
            raise AdmissionDenied("UNEXPECTED_RELEASE_TAG")
        if asset_name not in ("r8-gpre-commitment.json", "r8-gpre-review-acceptance.json",
                              "r8-gpre-consumed.json"):
            raise AdmissionDenied("UNEXPECTED_RELEASE_ASSET")
        record = strict_json(self._run("api", "repos/" + REPO + "/releases/tags/" + tag).encode())
        if not isinstance(record, dict) or record.get("tag_name") != tag or record.get("immutable") is not True:
            raise AdmissionDenied("GITHUB_IMMUTABLE_RELEASE_NOT_VERIFIED")
        assets = [a for a in record.get("assets", []) if a.get("name") == asset_name]
        if len(assets) != 1 or not isinstance(assets[0].get("digest"), str):
            raise AdmissionDenied("RELEASE_ASSET_NOT_UNIQUE")
        expected_digest = assets[0]["digest"]
        if not expected_digest.startswith("sha256:"):
            raise AdmissionDenied("GITHUB_RELEASE_SHA256_ABSENT")
        author = record.get("author") or {}
        if not isinstance(author.get("login"), str) or not author["login"]:
            raise AdmissionDenied("RELEASE_AUTHOR_UNVERIFIED")
        with tempfile.TemporaryDirectory(prefix="r8-verify-") as scratch:
            self._run("release", "download", tag, "-R", REPO,
                      "--pattern", asset_name, "--dir", scratch)
            asset = Path(scratch) / asset_name
            blob = asset.read_bytes()
            digest = _digest(blob)
            if expected_digest != "sha256:" + digest:
                raise AdmissionDenied("REMOTE_ASSET_BYTES_DIGEST_MISMATCH")
            # Cryptographic verification is done by GitHub CLI, not by our
            # own untrusted claim fields. A zero exit code is required.
            detail = strict_json(self._run("release", "verify-asset", tag,
                        str(asset), "-R", REPO, "--format", "json").encode())
            signed = self._signed_verified_times(detail)
            if not signed:
                raise AdmissionDenied("VERIFIED_SIGNATURE_TIMESTAMP_MISSING")
            metadata = strict_json(blob)
            if not isinstance(metadata, dict):
                raise AdmissionDenied("RELEASE_JSON_NOT_OBJECT")
            self._run("release", "verify", tag, "-R", REPO, "--format", "json")
        published = _utc(record.get("published_at"))
        checked = datetime.now(timezone.utc)
        signed_at = min(signed)
        if not published < signed_at <= checked:
            raise AdmissionDenied("REMOTE_TIMESTAMPS_NOT_PROSPECTIVE")
        return ReleaseProof(tag, asset_name, digest, signed_at, published,
                            checked, metadata, author["login"])

    def consume_once(self, tag: str, asset_name: str, exact_asset: bytes) -> ReleaseProof:
        if asset_name != "r8-gpre-consumed.json":
            raise AdmissionDenied("CONSUMPTION_ASSET_INVALID")
        with tempfile.TemporaryDirectory(prefix="r8-consume-") as scratch:
            full = Path(scratch) / asset_name
            full.write_bytes(exact_asset)
            # GitHub enforces uniqueness of tag/release creation. No --clobber.
            self._run("release", "create", tag, str(full), "-R", REPO,
                      "--target", SOURCE_COMMIT, "--prerelease",
                      "--title", "R8 one-shot G3 consumption", "--notes",
                      "Public-safe one-shot evidence; NOT a scientific result")
        proof = self.verify(tag, asset_name)
        if proof.body != strict_json(exact_asset):
            raise AdmissionDenied("REMOTE_CONSUMPTION_READBACK_MISMATCH")
        return proof


@dataclass(frozen=True)
class TrustPolicy:
    """Configuration pinned outside caller control; not a user-supplied receipt."""
    approved_review_commit: str
    distinct_reviewer_login: str
    implementation_actor_login: str
    accepted_gpre_release_tag: str
    acceptance_release_tag: str
    trusted_gh_sha256: str
    python_exe_sha256: str
    # Do not turn on this gate via a caller-supplied boolean; permission depends
    # on a separate trusted production process/launcher outside this candidate.


class RemoteOneShotLedger:
    """Remotely anchored consumption survives local SQLite rollback while tag exists."""

    def __init__(self, remote: ReleaseAuthority):
        self.remote = remote

    def consume(self, session: str, digest: str, review_commit: str) -> None:
        if not session or len(session) > 128 or not all(ch.isalnum() or ch in "_-" for ch in session):
            raise AdmissionDenied("CONSUME_SESSION_INVALID")
        # Tag uniquely determined by the prospective digest, never by a new seed.
        tag = "ttm-vm-v4-r8-consumed-" + digest
        message = {"schema": "TTM_VM_R8_CONSUMED_V1", "session_id": session,
                   "commitment_digest": digest, "review_commit": review_commit,
                   "source_commit": SOURCE_COMMIT}
        proof = self.remote.consume_once(tag, "r8-gpre-consumed.json", canonical(message))
        if proof.tag != tag or proof.body != message or proof.asset_name != "r8-gpre-consumed.json":
            raise AdmissionDenied("REMOTE_LEDGER_CONSUMPTION_PROOF_INVALID")


class ProductionBoundaryCandidate:
    """Trusted-path ordering. No actual G3 callback may be registered yet.

    The generator MUST be registered by a separately reviewed custodian-owned
    executable, not supplied to this class by a public API caller. In this source
    the registry is empty and production dispatch is *always denied*.
    """
    _registered_generator = None  # Explicitly unregistered: no real G3 is authorized.

    def __init__(self, authority: ReleaseAuthority, custodian: PinnedCustody,
                 policy: TrustPolicy, consumption: RemoteOneShotLedger,
                 key_provider: KeyProvider):
        self.authority = authority
        self.custodian = custodian
        self.policy = policy
        self.consumption = consumption
        self.key_provider = key_provider

    def verify_readiness(self, envelope: PrivateEnvelope) -> None:
        """Byte, HMAC, server-time, identity and amendment checks. No consumption."""
        value = envelope.parse_and_validate()
        fold_source = self.custodian.verify(value["source_manifest_sha256"],
                                            value["runtime_manifest_sha256"])
        authenticate_hmac_v2(envelope, self.key_provider.read_key(), fold_source)
        anchor = self.authority.verify(self.policy.accepted_gpre_release_tag,
                                       "r8-gpre-commitment.json")
        if (anchor.body.get("commitment_digest") != envelope.public_digest or
            anchor.body.get("session_id") != value["session_id"] or
            anchor.body.get("source_commit") != SOURCE_COMMIT or
            anchor.body.get("source_manifest_sha256") != value["source_manifest_sha256"] or
            anchor.body.get("runtime_manifest_sha256") != value["runtime_manifest_sha256"]):
            raise AdmissionDenied("REMOTE_COMMITMENT_BINDING_MISMATCH")
        accepted = self.authority.verify(self.policy.acceptance_release_tag,
                                         "r8-gpre-review-acceptance.json")
        review = self.policy.approved_review_commit
        if (len(review) != 40 or not all(c in "0123456789abcdef" for c in review) or
            review == "0" * 40 or
            accepted.release_author != self.policy.distinct_reviewer_login or
            accepted.release_author == self.policy.implementation_actor_login or
            accepted.body.get("review_commit") != review or
            accepted.body.get("amendment_status") != "PASS_SCOPED_R8_D" or
            accepted.body.get("commitment_digest") != envelope.public_digest or
            accepted.body.get("session_id") != value["session_id"]):
            raise AdmissionDenied("DISTINCT_INDEPENDENT_REVIEW_NOT_VERIFIED")
        if not anchor.signed_at < accepted.published_at < accepted.signed_at:
            raise AdmissionDenied("REVIEW_NOT_AFTER_PROSPECTIVE_COMMITMENT")
        # Second remote check after independent acceptance, fail if revoked.
        second = self.authority.verify(self.policy.accepted_gpre_release_tag,
                                       "r8-gpre-commitment.json")
        if second.asset_sha256 != anchor.asset_sha256 or second.body != anchor.body:
            raise AdmissionDenied("PROSPECTIVE_ANCHOR_CHANGED")

    def dispatch(self, envelope: PrivateEnvelope):
        """Single registered call path: verify, consume remotely, then generate.

        Registration remains None until a separately approved Windows launcher
        binds one exact generator under OS custody. Untrusted callers can always
        bypass in the same Python process; this is NOT an OS security boundary.
        """
        target = type(self)._registered_generator
        if target is None:
            raise AdmissionDenied("NO_APPROVED_G3_GENERATOR_REGISTERED")
        self.verify_readiness(envelope)
        value = envelope.parse_and_validate()
        self.consumption.consume(value["session_id"], envelope.public_digest,
                                 self.policy.approved_review_commit)
        # No exception/retry restores an already-consumed remote marker.
        return target()
