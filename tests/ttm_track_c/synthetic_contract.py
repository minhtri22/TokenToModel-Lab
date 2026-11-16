"""Track-C source-only reference: toy SFT wire/mask and toy metadata QA.
NO model execution; token ids >=7 are arbitrary synthetic opaque symbols.
Not a substitute for tokenizer, independent gold or source-corpus audit.
"""
from __future__ import annotations
from collections import Counter, defaultdict
from hashlib import sha256
import json
import re

PAD, BOS, SYS, USER, ASSIST, EOT, EOS = range(7)
IGNORE = -100
ROLES = {"system": SYS, "user": USER, "assistant": ASSIST}
SPLITS = {"train", "val", "test"}

def serialize(messages: list[dict], max_len: int) -> tuple[list[int], list[int]]:
    """Return (ids, label_mask); assistant content + end/stop targets only."""
    if not isinstance(max_len, int) or isinstance(max_len, bool) or max_len < 5:
        raise ValueError("invalid max_len")
    if not isinstance(messages, list) or not messages:
        raise ValueError("empty conversation")
    ids, flags = [BOS], [0]
    expect = "user"
    for i, message in enumerate(messages):
        if not isinstance(message, dict) or set(message) != {"role", "content"}:
            raise ValueError("invalid message shape")
        role, content = message["role"], message["content"]
        if role == "system" and i == 0:
            pass
        elif role != expect:
            raise ValueError("invalid role alternation")
        else:
            expect = "assistant" if role == "user" else "user"
        if not isinstance(content, list) or not content or any(
            not isinstance(t, int) or isinstance(t, bool) or t < 7 for t in content
        ):
            raise ValueError("content must be nonempty synthetic token ids >=7")
        mark = int(role == "assistant")
        ids.extend([ROLES[role], *content, EOT])
        flags.extend([0, *([mark] * len(content)), mark])
    if messages[-1]["role"] != "assistant":
        raise ValueError("SFT conversation must end with assistant")
    ids.append(EOS)
    flags.append(1)
    if len(ids) > max_len:
        raise ValueError("no silent truncation allowed")
    return ids, flags

def shifted_padded_targets(ids: list[int], flags: list[int], max_len: int):
    """One-step target shift; pad all unused labels to IGNORE=-100."""
    if len(ids) != len(flags) or not ids or ids[0] != BOS:
        raise ValueError("invalid ids/mask")
    if len(ids) > max_len or max_len < 2 or flags[0] != 0:
        raise ValueError("invalid length")
    if any(t < 0 for t in ids) or any(f not in (0, 1) for f in flags):
        raise ValueError("invalid token or mask")
    padded = ids + [PAD] * (max_len - len(ids))
    mask = flags + [0] * (max_len - len(ids))
    x = padded[:-1]
    y = [padded[i] if mask[i] else IGNORE for i in range(1, max_len)]
    if not any(t != IGNORE for t in y):
        raise ValueError("no supervised targets")
    return x, y

def score_slot(gold: str | None, prediction: str) -> int | None:
    """Closed-world deterministic exact slot; absent gold is not 'unknown'."""
    if gold is None:
        return None
    if not isinstance(gold, str) or not gold.strip() or not isinstance(prediction, str):
        raise ValueError("invalid gold/prediction")
    return int(gold == prediction)

def floor_state(scores: list[int]) -> str:
    """Diagnostic only, never a significance test or a model score."""
    if not scores or any(s not in (0, 1) for s in scores):
        raise ValueError("binary controls only")
    if all(s == 0 for s in scores):
        return "FLOOR_HOLD"
    if all(s == 1 for s in scores):
        return "CEILING_HOLD"
    return "SEPARATING_TOY_CONTROLS_ONLY"

def audit_toy_records(records: list[dict]) -> dict:
    """Bounded synthetic manifest only; no raw content in result."""
    if not isinstance(records, list) or not records:
        raise ValueError("empty manifest")
    ids = set()
    split_counts = Counter()
    length_bins = Counter()
    exact = defaultdict(set)
    normalized = defaultdict(set)
    summary = []
    for r in records:
        if not isinstance(r, dict) or set(r) != {"id", "split", "text"}:
            raise ValueError("invalid record")
        item_id, split, value = r["id"], r["split"], r["text"]
        if not isinstance(item_id, str) or not item_id or item_id in ids:
            raise ValueError("duplicate or invalid id")
        if split not in SPLITS or not isinstance(value, str) or not value:
            raise ValueError("invalid split or text")
        ids.add(item_id)
        raw = value.encode("utf-8")
        h = sha256(raw).hexdigest()
        hn = sha256(re.sub(r"\s+", " ", value.casefold()).strip().encode("utf-8")).hexdigest()
        split_counts[split] += 1
        length_bins["lt32" if len(raw) < 32 else "32to127" if len(raw) < 128 else "ge128"] += 1
        exact[h].add(split)
        normalized[hn].add(split)
        summary.append([item_id, split, h])
    def collision_groups(groups):
        return sum(len(v) > 1 for v in groups.values())
    return {
        "scope": "SYNTHETIC_ONLY_NOT_PRODUCTION_DEDUP",
        "record_count": len(records),
        "split_counts": dict(sorted(split_counts.items())),
        "utf8_length_bins": dict(sorted(length_bins.items())),
        "cross_split_exact_groups": collision_groups(exact),
        "cross_split_normalized_groups": collision_groups(normalized),
        "manifest_sha256": sha256(json.dumps(sorted(summary), separators=(",", ":"), ensure_ascii=False).encode("utf-8")).hexdigest(),
        "near_duplicate_groups": "NOT_IMPLEMENTED_TOY_ONLY",
        "token_histogram": "NOT_AVAILABLE_NO_REAL_TOKENIZER",
    }
