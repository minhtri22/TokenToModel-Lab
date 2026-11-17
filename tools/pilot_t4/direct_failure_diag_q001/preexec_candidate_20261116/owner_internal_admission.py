"""Owner-internal Q001 admission anchored to the published I1 technical verdict."""
from __future__ import annotations

from datetime import datetime, timezone
import hashlib
import json
from pathlib import Path
import urllib.request

from release_auth_v2 import (
    CHECKPOINT_SHA, OWNER_DECISION, Q1_MAIN, QUESTION_ID,
    TRUSTED_HOSTNAME, TRUSTED_PROJECT_ROOT, trusted_execution_root,
)

OWNER_RECORD_BLOB = "aaf01f2cf0925f588ba38c0d4cd04e7c6578372b"
OWNER_RECORD_RELPATH = (
    "docs/governance/ttm-small4m-direct-diag/"
    "TTM_SM4M_DIAG_Q001_OWNER_INTERNAL_SCOPE_AND_LAST_MILE_AMENDMENT_20261116.md"
)
OWNER_ISSUE_RECORD = "https://github.com/minhtri22/TokenToModel-Lab/issues/29#issuecomment-6916584568"
VERDICT_PATH = "artifacts/governance/ttm-small4m-direct-diag/Q001_LAST_MILE_I1_20261116.json"
VERDICT_URL = (
    "https://raw.githubusercontent.com/minhtri22/TokenToModel-Lab/"
    "refs/heads/review/ttm-sm4m-diag-q001-preexec-source-candidate-20261116/"
    + VERDICT_PATH
)
BPE_SHA256 = "cba18e60cee3d08a353ee6d4a451017289e45af7b4b1179c87171b9b78d7dfdc"
BPE_MANIFEST_SHA256 = "6da22cf79c3a6cfd08d80a768eb1074125a753164ccf62a164e79545956e94c6"
# One claim shared by all owner-internal source revisions of this Q1.
ONE_SHOT_NONCE = hashlib.sha256(f"{QUESTION_ID}:{Q1_MAIN}:{CHECKPOINT_SHA}".encode()).hexdigest()
SCOPE = {
    "question_id": QUESTION_ID,
    "question_gate_main_sha": Q1_MAIN,
    "project_root": TRUSTED_PROJECT_ROOT,
    "hostname": TRUSTED_HOSTNAME,
    "owner_decision": OWNER_DECISION,
    "owner_scope_record": OWNER_ISSUE_RECORD,
    "owner_scope_document_git_blob": OWNER_RECORD_BLOB,
    "owner_declaration_status": "OWNER_DECLARED_INTERNAL_SCOPE",
    "checkpoint_sha256": CHECKPOINT_SHA,
    "checkpoint_bytes": 45074891,
    "tokenizer_source_sha256": BPE_SHA256,
    "seed": 20261116,
    "steps": 256,
    "train_count": 24,
    "nontrain_count": 56,
}
RUNTIME_FILES = (
    "ttm_sm4m_diag_q001.py", "owner_internal_admission.py",
    "release_auth_v2.py", "windows_rss_native.py", "windows_job_memory_limit.py",
    "Run-Approved-OneShot-PS51.ps1", "Watch-TTM-SM4M-ProcessTree-PS51.ps1",
)


class OwnerInternalHold(RuntimeError):
    pass


def require_scope(root: Path) -> None:
    trusted_execution_root(root)
    declaration = Path(__file__).resolve().parents[4] / OWNER_RECORD_RELPATH
    raw = declaration.read_bytes()
    blob = hashlib.sha1(f"blob {len(raw)}\0".encode("ascii") + raw).hexdigest()
    if blob != OWNER_RECORD_BLOB:
        raise OwnerInternalHold("HOLD_OWNER_INTERNAL_SCOPE_DOCUMENT_BLOB")


def original_token_ids(raw: bytes) -> list[int]:
    """Derive the ordered ID pool from the original TRAIN-only T1 BPE."""
    if hashlib.sha256(raw).hexdigest() != BPE_SHA256:
        raise OwnerInternalHold("HOLD_OWNER_INTERNAL_ORIGINAL_BPE_SHA256")
    bpe = json.loads(raw)
    if (bpe["manifest_sha256"] != BPE_MANIFEST_SHA256
            or bpe["source_kind"] != "PINNED_TINYSTORIES_TRAIN"
            or bpe["vocab_size"] != 2048 or bpe["eos_id"] != 256
            or bpe["tokens"][256] != "<|endoftext|>"
            or len(set(bpe["tokens"])) != 2048 or len(bpe["tokens"]) != 2048
            or len(bpe["pair_ids"]) != 1791):
        raise OwnerInternalHold("HOLD_OWNER_INTERNAL_ORIGINAL_BPE_TAXONOMY")
    return [token_id for token_id in range(2048) if token_id != 256]


def validate_verdict(verdict, *, runtime_sha256: dict) -> str:
    if not isinstance(verdict, dict) or verdict.get("I1") != "I1_PASS_SCOPED_INTERNAL_RESEARCH":
        raise OwnerInternalHold("HOLD_OWNER_INTERNAL_I1_NOT_PASS")
    if verdict.get("scope") != SCOPE:
        raise OwnerInternalHold("HOLD_OWNER_INTERNAL_I1_SCOPE")
    if verdict.get("runtime_sha256") != runtime_sha256:
        raise OwnerInternalHold("HOLD_OWNER_INTERNAL_I1_SOURCE_PINS")
    expires = verdict.get("expires_utc")
    try:
        deadline = datetime.strptime(expires, "%Y-%m-%dT%H:%M:%SZ").replace(tzinfo=timezone.utc)
    except (TypeError, ValueError) as exc:
        raise OwnerInternalHold("HOLD_OWNER_INTERNAL_I1_EXPIRY") from exc
    if deadline.strftime("%Y-%m-%dT%H:%M:%SZ") != expires or deadline <= datetime.now(timezone.utc):
        raise OwnerInternalHold("HOLD_OWNER_INTERNAL_I1_EXPIRY")
    fixture = verdict.get("fixture_sha256")
    if (not isinstance(fixture, str) or len(fixture) != 64
            or any(c not in "0123456789abcdef" for c in fixture)):
        raise OwnerInternalHold("HOLD_OWNER_INTERNAL_I1_FIXTURE_PIN")
    return fixture


def published_fixture_sha256(root: Path) -> str:
    require_scope(root)
    directory = Path(__file__).resolve().parent
    runtime = {name: hashlib.sha256((directory / name).read_bytes()).hexdigest()
               for name in RUNTIME_FILES}
    # Read only the project-controlled verdict destination. Local JSON never
    # supplies release facts or a nonce.
    opener = urllib.request.build_opener(urllib.request.ProxyHandler({}))
    request = urllib.request.Request(VERDICT_URL, headers={"Cache-Control": "no-cache"})
    try:
        with opener.open(request, timeout=10) as response:
            if response.geturl() != VERDICT_URL:
                raise OwnerInternalHold("HOLD_OWNER_INTERNAL_I1_UNEXPECTED_ORIGIN")
            verdict = json.loads(response.read(256 * 1024))
    except (OSError, ValueError) as exc:
        raise OwnerInternalHold("HOLD_OWNER_INTERNAL_I1_GITHUB_READBACK") from exc
    return validate_verdict(verdict, runtime_sha256=runtime)
