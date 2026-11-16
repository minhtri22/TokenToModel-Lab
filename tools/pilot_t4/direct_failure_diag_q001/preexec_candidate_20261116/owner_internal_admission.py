"""Scoped owner-only internal research admission for TTM-SM4M-DIAG-Q001.

This is an owner-policy alternative to three externally signed human roles.
It does not invent identities, certify upstream legal rights, grant arbitrary
model access, or authorize a run before I1 native/source/fixture review.
Current user has explicitly declared this one local internal research purpose;
the declaration is pinned to the actual GitHub governance document blob.
"""
from __future__ import annotations

from datetime import datetime, timezone
import hashlib
import json
import ntpath
from pathlib import Path
import platform
import re

QUESTION_ID = "TTM-SM4M-DIAG-Q001"
Q1_MAIN = "f7a0a5874e8fd895c8ea8d17ceff393a4d4917a3"
EXPECTED_CHECKPOINT_SHA256 = "cb985751795c8328ad65acf7ca4c1033ce35182c1bfbdb8c38550de629cb271b"
OWNER_GO = "GO_SMALL4M_DIAG_SINGLE_SCOPED_IMPLEMENT_AND_RUN_CONDITIONAL"
ROOT = r"D:\WORK\RESEARCH\TokenToModel-Lab"
HOST = "DESKTOP-4PSD0G2"
MODE = "OWNER_INTERNAL_NONCOMMERCIAL_Q001_V1"
OWNER_RECORD_BLOB = "aaf01f2cf0925f588ba38c0d4cd04e7c6578372b"
OWNER_RECORD_RELPATH = ("docs/governance/ttm-small4m-direct-diag/"
    "TTM_SM4M_DIAG_Q001_OWNER_INTERNAL_SCOPE_AND_LAST_MILE_AMENDMENT_20261116.md")
OWNER_ISSUE_RECORD = (
    "https://github.com/minhtri22/TokenToModel-Lab/issues/29#issuecomment-6916584568"
)

class OwnerInternalHold(RuntimeError):
    pass

def _hold(reason: str):
    raise OwnerInternalHold("HOLD_OWNER_INTERNAL_" + reason)

def _hex64(x):
    return isinstance(x, str) and bool(re.fullmatch("[0-9a-f]{64}", x))

def _git_blob_sha1(path: Path) -> str:
    raw = path.read_bytes()
    return hashlib.sha1(b"blob " + str(len(raw)).encode("ascii") + b"\x00" + raw).hexdigest()

def _verify_owner_scope_record() -> None:
    # The checked-in exact source is reviewed by Codex; the owner statement
    # remains represented truthfully as OWNER_DECLARED, not verified legal title.
    repo_root = Path(__file__).resolve().parents[4]
    declaration = repo_root / OWNER_RECORD_RELPATH
    if not declaration.is_file() or _git_blob_sha1(declaration) != OWNER_RECORD_BLOB:
        _hold("OWNER_SCOPE_GITHUB_DOCUMENT_BLOB_MISMATCH")

def _require_expiry(value) -> None:
    if not isinstance(value, str):
        _hold("EXPIRY_REQUIRED")
    try:
        expires = datetime.strptime(value, "%Y-%m-%dT%H:%M:%SZ").replace(tzinfo=timezone.utc)
    except ValueError:
        _hold("EXPIRY_INVALID")
    if expires.strftime("%Y-%m-%dT%H:%M:%SZ") != value:
        _hold("EXPIRY_INVALID")
    if datetime.now(timezone.utc) >= expires:
        _hold("EXPIRED")

def authenticate_owner_internal(
    permit_path: Path, *, phase: str, runner_sha256: str,
    tokenizer_sha256: str, underlying_sha256: str,
    frozen_fixture_sha256: str | None, project_root: Path
) -> dict:
    """Validate narrowed local owner scope; never pretends to verify 3 signers.

    Checkpoint, tokenizer, frozen fixture SHA/rights and one-shot claim are
    verified separately by the unchanged I1/I2 runner before model execution.
    This mode is a *policy amendment*, not a scientific parameter change.
    """
    from release_auth_v2 import trusted_execution_root
    trusted_execution_root(project_root)
    if not permit_path.is_file():
        _hold("PERMIT_MISSING")
    _verify_owner_scope_record()
    try:
        permit = json.loads(permit_path.read_text(encoding="utf-8"))
    except (ValueError, UnicodeError, OSError):
        _hold("PERMIT_INVALID")
    if not isinstance(permit, dict) or set(permit) != {"mode", "owner_scope_record", "payload"}:
        _hold("PERMIT_SCHEMA")
    if permit["mode"] != MODE or permit["owner_scope_record"] != OWNER_ISSUE_RECORD:
        _hold("MODE_OR_OWNER_RECORD_MISMATCH")
    payload = permit["payload"]
    if not isinstance(payload, dict):
        _hold("PAYLOAD_SCHEMA")
    exact = {
        "question_id": QUESTION_ID,
        "question_gate_main_sha": Q1_MAIN,
        "project_root": ROOT,
        "hostname": HOST,
        "owner_decision": OWNER_GO,
        "owner_research_scope": "LOCAL_INTERNAL_NONCOMMERCIAL_NO_REDISTRIBUTION",
        "owner_scope_document_git_blob": OWNER_RECORD_BLOB,
        "owner_declaration_status": "OWNER_DECLARED_INTERNAL_SCOPE",
        "phase": phase,
        "checkpoint_sha256": EXPECTED_CHECKPOINT_SHA256,
        "runner_sha256": runner_sha256,
        "token_inventory_sha256": tokenizer_sha256,
        "underlying_inventory_sha256": underlying_sha256,
        "train_count": 24,
        "nontrain_count": 56,
        "seed": 20261116,
        "max_steps": 256,
    }
    if any(payload.get(k) != v for k,v in exact.items()):
        _hold("PAYLOAD_EXACT_SCOPE_MISMATCH")
    if ntpath.normcase(ntpath.normpath(str(project_root.resolve(strict=False)))) != ntpath.normcase(ntpath.normpath(ROOT)):
        _hold("NONCANONICAL_ROOT")
    if platform.node().casefold() != HOST.casefold():
        _hold("FOREIGN_HOST")
    if not all(_hex64(x) for x in (runner_sha256,tokenizer_sha256,underlying_sha256)):
        _hold("SOURCE_SHA_FORMAT")
    if phase == "run":
        if not _hex64(payload.get("one_shot_nonce")):
            _hold("ONESHOT_NONCE_MISSING")
        if not _hex64(frozen_fixture_sha256) or payload.get("frozen_fixture_sha256") != frozen_fixture_sha256:
            _hold("FROZEN_FIXTURE_SHA_MISMATCH")
    elif phase != "fixture-freeze":
        _hold("PHASE_INVALID")
    _require_expiry(payload.get("expires_utc"))
    # Don't return invented rights approval; downstream only receives the
    # explicitly declared local-use scope and byte pins.
    return dict(payload)
