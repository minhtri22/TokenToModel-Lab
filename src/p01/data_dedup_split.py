"""P01 H03 dedup/split *source-only* pure functions; NO IO and NO corpus admit."""
from __future__ import annotations
from dataclasses import dataclass
import hashlib
import unicodedata
import struct

SPLIT_SEED = 20261105
GROUP_PREFIX = b"TTM-P01-GROUP-V1\x00"
SPLIT_PREFIX = b"TTM-P01-SPLIT-V1\x00"


class SourceScopeError(ValueError):
    pass


@dataclass(frozen=True)
class Document:
    document_id: str
    raw: bytes
    approved: bool
    pii_reviewed: bool


def canonical_key(raw: bytes) -> str:
    if not isinstance(raw, bytes):
        raise SourceScopeError("RAW_BYTES_REQUIRED")
    text = raw.decode("utf-8", "strict")
    text = unicodedata.normalize("NFC", text)
    text = text.replace("\r\n", "\n").replace("\r", "\n").casefold()
    return " ".join(text.split())


def _edit_distance(a: str, b: str) -> int:
    if len(a) > len(b):
        a, b = b, a
    prev = list(range(len(a) + 1))
    for index, char_b in enumerate(b, 1):
        cur = [index]
        for j, char_a in enumerate(a, 1):
            cur.append(min(cur[-1] + 1, prev[j] + 1, prev[j - 1] + (char_a != char_b)))
        prev = cur
    return prev[-1]


def near_duplicate(a: str, b: str) -> bool:
    if a == b:
        return True
    la, lb = len(a), len(b)
    if min(la, lb) < 8:
        return False
    shorter, longer = min(la, lb), max(la, lb)
    if 5 * shorter < 4 * longer:
        return False
    if shorter < 40:
        return 10 * (longer - _edit_distance(a, b)) >= 9 * longer
    sa = {a[i:i + 5] for i in range(la - 4)}
    sb = {b[i:i + 5] for i in range(lb - 4)}
    overlap = len(sa & sb)
    union = len(sa | sb)
    return bool(union) and 20 * overlap >= 17 * union


def classify_f0_documents(docs: list[Document], *, admission: str) -> dict[str, str]:
    """QA0 synthetic only; human-approved F1/F2 sources are not admitted here."""
    if admission != "QA0_F0_SYNTHETIC_ONLY":
        raise PermissionError("F0_QA0_ADMISSION_REQUIRED")
    if not isinstance(docs, list) or len(docs) > 2000:
        raise SourceScopeError("DOCUMENT_LIMIT")
    if sum(len(d.raw) for d in docs) > 64 * 1024 * 1024:
        raise SourceScopeError("CORPUS_BYTES_LIMIT")
    ordered = sorted(docs, key=lambda d: d.document_id)
    ids: set[str] = set()
    raw_hash: list[bytes] = []
    keys: list[str] = []
    for doc in ordered:
        if not isinstance(doc, Document) or not doc.approved or not doc.pii_reviewed:
            raise SourceScopeError("QUARANTINE_OR_REJECT")
        if not doc.document_id or doc.document_id in ids:
            raise SourceScopeError("INVALID_OR_DUPLICATE_ID")
        ids.add(doc.document_id)
        key = canonical_key(doc.raw)
        if not key:
            raise SourceScopeError("EMPTY_CANONICAL")
        raw_hash.append(hashlib.sha256(doc.raw).digest())
        keys.append(key)
    parent = list(range(len(ordered)))

    def find(x: int) -> int:
        while parent[x] != x:
            parent[x] = parent[parent[x]]
            x = parent[x]
        return x

    for i in range(len(ordered)):
        for j in range(i + 1, len(ordered)):
            if raw_hash[i] == raw_hash[j] or near_duplicate(keys[i], keys[j]):
                pi, pj = find(i), find(j)
                if pi != pj:
                    parent[max(pi, pj)] = min(pi, pj)
    groups: dict[int, list[int]] = {}
    for i in range(len(ordered)):
        groups.setdefault(find(i), []).append(i)
    assignments = {}
    for members in groups.values():
        low = min(raw_hash[i] for i in members)
        group_id = hashlib.sha256(GROUP_PREFIX + low).hexdigest()
        for i in members:
            assignments[ordered[i].document_id] = group_id
    return assignments


def assign_splits(groups: dict[str, str], *, admission: str, seed: int = SPLIT_SEED) -> dict[str, str]:
    if admission != "QA0_F0_SYNTHETIC_ONLY":
        raise PermissionError("F0_QA0_ADMISSION_REQUIRED")
    ids = set(groups.values())
    if len(ids) < 30:
        raise SourceScopeError("INSUFFICIENT_GROUPS")
    if type(seed) is not int or not (0 <= seed < 2**64):
        raise SourceScopeError("INVALID_SEED")
    order = sorted(ids, key=lambda gid: (
        hashlib.sha256(SPLIT_PREFIX + struct.pack("<Q", seed) + bytes.fromhex(gid)).digest(), gid
    ))
    n_val = n_test = len(order) // 10
    labels = {gid: ("VALIDATION" if i < n_val else "TEST" if i < n_val + n_test else "TRAIN")
              for i, gid in enumerate(order)}
    return {doc_id: labels[gid] for doc_id, gid in groups.items()}
