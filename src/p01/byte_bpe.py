"""P01 F0 Byte-BPE reference source. SOURCE-ONLY; not QA0-approved.

No IO on import. The only learning entry point rejects non-F0 QA0 admissions;
this file must not be used as authorization for real TRAIN, TEST, or GPT.
"""
from __future__ import annotations
from dataclasses import dataclass
from collections import Counter
import struct
from runtime.p01.source_scope_guard import require_f0_literal_bytes

MAGIC = b"TTM_BPE_V1\x00"


class BPEContractError(ValueError):
    pass


@dataclass(frozen=True)
class Merge:
    left: int
    right: int
    new_id: int


def _valid_id(value: object, maximum: int) -> int:
    if type(value) is not int or not (0 <= value < maximum):
        raise BPEContractError("INVALID_TOKEN_ID")
    return value


def _validate_merges(merges: tuple[Merge, ...], target: int) -> None:
    if type(target) is not int or not (256 <= target <= 2**32 - 1):
        raise BPEContractError("INVALID_TARGET_VOCAB")
    if len(merges) > target - 256:
        raise BPEContractError("TOO_MANY_MERGES")
    seen: set[tuple[int, int]] = set()
    for rank, merge in enumerate(merges):
        if not isinstance(merge, Merge) or merge.new_id != 256 + rank:
            raise BPEContractError("MERGE_RANK_NONCANONICAL")
        _valid_id(merge.left, merge.new_id)
        _valid_id(merge.right, merge.new_id)
        key = (merge.left, merge.right)
        if key in seen:
            raise BPEContractError("DUPLICATE_MERGE")
        seen.add(key)


def encode_merges(merges: tuple[Merge, ...], target_vocab_size: int) -> bytes:
    _validate_merges(merges, target_vocab_size)
    result = bytearray(MAGIC)
    result.extend(struct.pack("<III", target_vocab_size, 256 + len(merges), len(merges)))
    for item in merges:
        result.extend(struct.pack("<III", item.left, item.right, item.new_id))
    return bytes(result)


def decode_merges(blob: bytes) -> tuple[int, tuple[Merge, ...]]:
    if not isinstance(blob, bytes) or len(blob) < len(MAGIC) + 12 or blob[:11] != MAGIC:
        raise BPEContractError("MERGES_BAD_MAGIC_OR_SIZE")
    target, actual, count = struct.unpack_from("<III", blob, 11)
    if len(blob) != 23 + count * 12 or actual != 256 + count:
        raise BPEContractError("MERGES_LENGTH_OR_COUNT")
    merges = tuple(Merge(*struct.unpack_from("<III", blob, 23 + 12 * i)) for i in range(count))
    _validate_merges(merges, target)
    return target, merges


def _replace_pair(seq: list[int], a: int, b: int, new_id: int) -> list[int]:
    out: list[int] = []
    i = 0
    while i < len(seq):
        if i + 1 < len(seq) and seq[i] == a and seq[i + 1] == b:
            out.append(new_id)
            i += 2
        else:
            out.append(seq[i])
            i += 1
    return out


def learn_merges_f0_qa0_only(
    docs: list[bytes], target_vocab_size: int, *, admission: str
) -> tuple[Merge, ...]:
    """Synthetic QA0 only. No real source admission; no execution in I0A-S."""
    if admission != "QA0_F0_SYNTHETIC_ONLY":
        raise PermissionError("F0_QA0_ADMISSION_REQUIRED")
    if type(target_vocab_size) is not int or target_vocab_size < 256 or target_vocab_size > 65536:
        raise BPEContractError("INVALID_TARGET_VOCAB")
    if not isinstance(docs, list) or not all(isinstance(x, bytes) for x in docs):
        raise BPEContractError("INVALID_DOCS")
    # The caller's admission string is NOT a security capability.
    # Reject every non-pinned byte payload, even when it supplies that string.
    for document in docs:
        require_f0_literal_bytes(document)
    corpus = [list(document) for document in docs]
    merges: list[Merge] = []
    while len(merges) + 256 < target_vocab_size:
        counts: Counter[tuple[int, int]] = Counter()
        for doc in corpus:
            counts.update(zip(doc, doc[1:]))
        eligible = [pair for pair, frequency in counts.items() if frequency >= 2]
        if not eligible:
            break
        chosen = min(eligible, key=lambda p: (-counts[p], p))
        new_id = 256 + len(merges)
        merges.append(Merge(chosen[0], chosen[1], new_id))
        corpus = [_replace_pair(doc, *chosen, new_id) for doc in corpus]
    return tuple(merges)


class ByteBPE:
    def __init__(self, merges: tuple[Merge, ...] = (), target_vocab_size: int = 256):
        _validate_merges(merges, target_vocab_size)
        self.merges = merges
        self.target_vocab_size = target_vocab_size
        self._vocab = {i: bytes([i]) for i in range(256)}
        for item in merges:
            self._vocab[item.new_id] = self._vocab[item.left] + self._vocab[item.right]

    def encode_bytes(self, raw: bytes) -> list[int]:
        if not isinstance(raw, bytes):
            raise BPEContractError("INVALID_RAW_BYTES")
        ids = list(raw)
        for item in self.merges:
            ids = _replace_pair(ids, item.left, item.right, item.new_id)
        return ids

    def decode_bytes(self, ids: list[int]) -> bytes:
        if not isinstance(ids, list):
            raise BPEContractError("INVALID_IDS_CONTAINER")
        return b"".join(self._vocab[_valid_id(i, 256 + len(self.merges))] for i in ids)

    def encode_text(self, text: str) -> list[int]:
        if not isinstance(text, str):
            raise BPEContractError("INVALID_TEXT")
        return self.encode_bytes(text.encode("utf-8", "strict"))

    def decode_text(self, ids: list[int]) -> str:
        return self.decode_bytes(ids).decode("utf-8", "strict")
