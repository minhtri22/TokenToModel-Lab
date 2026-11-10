#!/usr/bin/env python3
"""R2A: position-counterbalanced, query-key-binding symbolic toy fixture.

Research DESIGN ONLY. No TTM model, checkpoint, tokenizer or GPU is imported.
The complete oracle fixture and the input-only projection are intentionally separate.
"""
from __future__ import annotations
import argparse, hashlib, itertools, json, random, re
from collections import Counter
from pathlib import Path

SEED = 20261110
FAMILIES = ("ownership", "goal")
SPLITS = ("DEV", "CHALLENGE")
PEOPLE = ("Lan", "Minh", "An", "Binh", "Hoa", "Mai", "Nam", "Duy")
OBJECTS = ("key", "book", "ball", "cup", "map", "note")
GOALS = ("open the gate", "read the book", "visit the garden", "help a friend", "rest at home", "draw a map", "find the ball", "write a note")
PAIR_COUNT = 128


def stable_json(x):
    return json.dumps(x, sort_keys=True, ensure_ascii=False, separators=(",", ":")) + "\n"


def sha(b: bytes) -> str:
    return hashlib.sha256(b).hexdigest()


def manifest_shas(d: dict):
    return {k: sha(stable_json(d[k]).encode("utf-8")) for k in ("pairs", "probes", "counts")}


def render(event: dict, split: str) -> str:
    key, val, family = event["key"], event["value"], event["family"]
    if family == "ownership":
        return f"The {key} belongs to {val}." if split == "DEV" else f"{val} has the {key} now."
    return f"{key} plans to {val}." if split == "DEV" else f"{key} intends to {val}."


def question(family: str, key: str, split: str) -> str:
    if family == "ownership":
        return f"Who owns the {key}?" if split == "DEV" else f"Who has the {key} now?"
    return f"What does {key} plan to do?" if split == "DEV" else f"Which goal does {key} intend to pursue?"


def final_value(events: list[dict], key: str) -> str:
    values = [e["value"] for e in events if e["key"] == key]
    if len(values) != 2 or values[0] == values[1]:
        raise ValueError("MALFORMED_EVENT_KEY")
    return values[-1]


def patterns(seed_rng: random.Random) -> list[tuple[int,int]]:
    # Six position choices for the queried key's two updates. The last event is
    # queried for exactly 16/32 per family x split, never at a fixed position.
    candidate = list(itertools.combinations(range(4), 2))
    final = [p for p in candidate if 3 in p]
    nonfinal = [p for p in candidate if 3 not in p]
    result = [final[k % 3] for k in range(16)] + [nonfinal[k % 3] for k in range(16)]
    seed_rng.shuffle(result)
    return result


def build():
    rng = random.Random(SEED)
    pair_rows, probes = [], []
    used = set()
    for family in FAMILIES:
        for split in SPLITS:
            pos_plan = patterns(rng)
            target_side = [0] * 16 + [1] * 16
            rng.shuffle(target_side)
            for local_i in range(32):
                global_index = local_i + (0 if split == "DEV" else 32)
                pair_id = ("O" if family == "ownership" else "G") + f"{global_index+1:03d}"
                target_pos = pos_plan[local_i]
                other_pos = tuple(j for j in range(4) if j not in target_pos)
                # Use fresh lexical choices without replacement within a story.
                if family == "ownership":
                    keys = rng.sample(OBJECTS, 2)
                    vals = rng.sample(PEOPLE, 4)
                else:
                    keys = rng.sample(PEOPLE, 2)
                    vals = rng.sample(GOALS, 4)
                key = keys[target_side[local_i]]
                distract = keys[1-target_side[local_i]]
                # Two assignments to queried key and two conflicting assignments
                # to a second valid referent. This prevents question-free rules.
                primary = [dict(family=family, key=key, value=vals[0]),
                           dict(family=family, key=key, value=vals[1])]
                secondary = [dict(family=family, key=distract, value=vals[2]),
                             dict(family=family, key=distract, value=vals[3])]
                arr_a = [None] * 4
                for position, event in zip(target_pos, primary):
                    arr_a[position] = event
                for position, event in zip(other_pos, secondary):
                    arr_a[position] = event
                arr_b = [dict(e) for e in arr_a]
                arr_b[target_pos[0]], arr_b[target_pos[1]] = arr_b[target_pos[1]], arr_b[target_pos[0]]
                assert final_value(arr_a,key) != final_value(arr_b,key)
                assert final_value(arr_a,distract) == final_value(arr_b,distract)
                variants=[]
                for variant, events in (("A", arr_a),("B",arr_b)):
                    story="\n".join(render(e,split) for e in events)
                    q=question(family,key,split)
                    assert (story,q) not in used
                    used.add((story,q))
                    variants.append({"id":pair_id+variant,"pair_id":pair_id,"variant":variant,
                        "family":family,"split":split,"story":story,"question":q,
                        "answer":final_value(events,key),"source_events":events})
                pair_rows.extend(variants)
                # Exactly same story A, but question binds the OTHER valid key.
                # Answers differ: four owner/goal values are pairwise distinct.
                probe_story=variants[0]["story"]
                probe_question=question(family,distract,split)
                assert variants[0]["answer"]!=final_value(arr_a,distract)
                assert (probe_story,probe_question) not in used
                used.add((probe_story,probe_question))
                probes.append({"id":pair_id+"Q", "pair_id":pair_id,"family":family,
                    "split":split,"story":probe_story,"question":probe_question,
                    "answer":final_value(arr_a,distract),"source_events":arr_a})
    counts={"pairs":len(pair_rows)//2,"paired_records":len(pair_rows),"question_binding_probes":len(probes),
            "model_input_records":len(pair_rows)+len(probes),
            "by_family_split":{f"{f}_{s}":sum(1 for p in pair_rows if p["family"]==f and p["split"]==s) for f in FAMILIES for s in SPLITS}}
    dataset={"schema":"ttm.r2a.counterbalanced_key_binding.v1","seed":SEED,
        "declaration":"Public grammar toy; not sealed TEST, not TTM learning evidence",
        "counts":counts,"pairs":pair_rows,"probes":probes}
    # Never pass oracle-bearing rows to any model API. Two-field input view only.
    input_rows=[{"story":r["story"],"question":r["question"]} for r in pair_rows+probes]
    assert len(input_rows)==384 and all(set(r)=={"story","question"} for r in input_rows)
    return dataset,{"schema":"ttm.r2a.model_input_only.v1","records":input_rows}


def write_new(path, payload):
    p=Path(path)
    if p.exists(): raise SystemExit("REFUSE_OVERWRITE")
    p.parent.mkdir(parents=True,exist_ok=True)
    data=stable_json(payload).encode("utf-8")
    p.write_bytes(data)
    return {"path":str(p),"sha256":sha(data),"bytes":len(data)}


def main():
    ap=argparse.ArgumentParser()
    ap.add_argument("--oracle",required=True)
    ap.add_argument("--model-input",required=True)
    a=ap.parse_args()
    dataset,model=build()
    if Path(a.oracle).resolve()==Path(a.model_input).resolve():raise SystemExit("OUTPUT_COLLISION")
    print(json.dumps({"oracle":write_new(a.oracle,dataset),"model":write_new(a.model_input,model)},sort_keys=True))


if __name__=="__main__":main()
