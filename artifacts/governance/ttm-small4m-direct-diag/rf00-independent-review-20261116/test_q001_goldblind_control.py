#!/usr/bin/env python3
"""TTM Q001: independent, NO-MODEL reproduction of a frozen scorer flaw.

This script does not import the Q001 runner, read a checkpoint/tokenizer,
contact the network, write fixtures, or consume the original one-shot nonce.
Token-ID pool is derived from reviewed owner-internal code: all IDs 0..2047
except EOS 256. Only Python standard library is used.
"""
from collections import Counter
import hashlib
import json
import random

EXPECTED_FIXTURE = "5f1234f583ccf719ca9f0e68de4f47d8b653af777271b8115c5f02307f764e5a"
SEED = 20261116
COUNTS = {
    "TRAIN": 24,
    "HELDOUT_RECOMBINED": 16,
    "HELDOUT_NOVEL_IDS": 16,
    "PAIRED_COUNTERFACTUAL": 16,
    "HELDOUT_ABSENT": 8,
}

def canonical(obj):
    return (json.dumps(obj, ensure_ascii=False, sort_keys=True,
                       separators=(",", ":")) + "\n").encode("utf-8")

def regenerate():
    allowed = [i for i in range(2048) if i != 256]
    rng = random.Random(SEED)
    pool = allowed[:]
    rng.shuffle(pool)
    bind, query, answer, no_answer = pool[:4]
    keys_seen, vals_seen = pool[4:20], pool[20:36]
    keys_novel, vals_novel = pool[36:52], pool[52:68]
    rows, seen = [], set()

    def put(group, k1, v1, k2, v2, kq, parent=None):
        if k1 == k2 or v1 == v2 or (k1 == kq and k2 == kq):
            raise AssertionError("BAD_CASE")
        ctx = (bind, k1, v1, bind, k2, v2, query, kq, answer)
        if ctx in seen:
            return False
        gold = v1 if kq == k1 else v2 if kq == k2 else no_answer
        row = dict(
            group=group,
            id=f"{group}_{sum(x['group'] == group for x in rows):02d}",
            context=list(ctx),
            gold=gold, first_value=v1, second_value=v2,
            query_position=1 if kq == k1 else 2 if kq == k2 else 0,
            parent=parent,
        )
        distractors = [no_answer] + sorted(set(vals_seen + vals_novel))
        opts = [gold]
        for x in distractors:
            if x != gold and x not in opts:
                opts.append(x)
            if len(opts) == 4:
                break
        assert len(opts) == 4
        row["choices"] = opts
        rows.append(row)
        seen.add(ctx)
        return True

    for i in range(16):
        assert put("TRAIN",
                   keys_seen[i], vals_seen[i],
                   keys_seen[(i + 5) % 16], vals_seen[(i + 7) % 16],
                   keys_seen[i] if i % 2 == 0 else keys_seen[(i + 5) % 16])
    for i in range(8):
        assert put("TRAIN",
                   keys_seen[i], vals_seen[i],
                   keys_seen[(i + 3) % 16], vals_seen[(i + 4) % 16],
                   keys_seen[(i + 8) % 16])
    trial = 0
    while sum(r["group"] == "HELDOUT_RECOMBINED" for r in rows) < 16:
        trial += 1
        assert trial <= 10000
        k1, k2 = rng.sample(keys_seen, 2)
        v1, v2 = rng.sample(vals_seen, 2)
        put("HELDOUT_RECOMBINED", k1, v1, k2, v2,
            k1 if trial % 2 else k2)
    for i in range(16):
        assert put("HELDOUT_NOVEL_IDS",
                   keys_novel[i], vals_novel[i],
                   keys_novel[(i + 1) % 16], vals_novel[(i + 5) % 16],
                   keys_novel[i] if i % 2 else keys_novel[(i + 1) % 16])
    for r in rows[:16]:
        z = r["context"]
        assert put("PAIRED_COUNTERFACTUAL",
                   z[1], z[5], z[4], z[2], z[7], r["id"])
    trial = 0
    while sum(r["group"] == "HELDOUT_ABSENT" for r in rows) < 8:
        trial += 1
        assert trial <= 10000
        k1, k2, kq = rng.sample(keys_seen, 3)
        v1, v2 = rng.sample(vals_seen, 2)
        put("HELDOUT_ABSENT", k1, v1, k2, v2, kq)
    return rows, no_answer, allowed

def main():
    rows, no_answer, allowed = regenerate()
    counts = dict(Counter(r["group"] for r in rows))
    fixture_sha = hashlib.sha256(canonical(rows)).hexdigest()
    assert counts == COUNTS
    assert fixture_sha == EXPECTED_FIXTURE, (
        f"Expected fixture bytes: {EXPECTED_FIXTURE}; got: {fixture_sha}"
    )
    # 1. Equal-logit restricted argmax chooses index zero, always the gold.
    assert all(r["choices"][0] == r["gold"] for r in rows)
    constant_restricted = sum(r["choices"][0] == r["gold"] for r in rows)
    assert constant_restricted == 80

    # 2. Context-blind logits: same scores on every example. Larger token IDs
    # score higher, except NO_ANSWER is last. Both modes use same vector.
    blind_score = lambda token_id: token_id if token_id != no_answer else -1
    blind_full_id = max(allowed, key=blind_score)
    blind = {}
    expected = {
        "TRAIN": (14, 0),
        "HELDOUT_RECOMBINED": (15, 0),
        "HELDOUT_NOVEL_IDS": (16, 0),
        "PAIRED_COUNTERFACTUAL": (16, 0),
        "HELDOUT_ABSENT": (0, 0),
    }
    for group in COUNTS:
        group_rows = [r for r in rows if r["group"] == group]
        restricted = sum(
            max(r["choices"], key=blind_score) == r["gold"]
            for r in group_rows
        )
        full = sum(blind_full_id == r["gold"] for r in group_rows)
        assert (restricted, full) == expected[group], (group, restricted, full)
        blind[group] = {"restricted": restricted, "full_vocab": full,
                        "n": len(group_rows)}

    train = [r for r in rows if r["group"] == "TRAIN"]
    tr_bindings = {
        (r["context"][key_index], r["context"][val_index])
        for r in train
        for key_index, val_index in ((1, 2), (4, 5))
    }
    tr_queried = {
        (r["context"][1], r["context"][2])
        if r["context"][7] == r["context"][1]
        else (r["context"][4], r["context"][5])
        for r in train if r["query_position"]
    }
    recombined = [r for r in rows if r["group"] == "HELDOUT_RECOMBINED"]
    any_repeat = sum(
        (r["context"][1], r["context"][2]) in tr_bindings
        or (r["context"][4], r["context"][5]) in tr_bindings
        for r in recombined
    )
    queried_repeat = sum(
        ((r["context"][1], r["context"][2]) if r["context"][7] == r["context"][1]
         else (r["context"][4], r["context"][5])) in tr_queried
        for r in recombined
    )
    assert (any_repeat, queried_repeat) == (6, 1)
    print(json.dumps({
        "status": "PASS_INDEPENDENT_NO_MODEL_REPRODUCTION",
        "fixture_sha256": fixture_sha, "cases": len(rows),
        "equal_logits_restricted_hits": constant_restricted,
        "context_blind": blind,
        "recombined_reused_any_train_binding": any_repeat,
        "recombined_reused_queried_train_binding": queried_repeat,
        "conclusion": "HOLD_I1_RESTRICTED_SCORER_LABEL_LEAKAGE",
        "model_forward": False, "optimizer_steps": 0,
        "tested_native_windows": False
    }, sort_keys=True, ensure_ascii=False, indent=2))

if __name__ == "__main__":
    main()
