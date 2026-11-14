"""Deterministic G_pre/G_post and proposed four-rater allocation. NO R8 generation.
Private HMAC key and real allocation must remain under authorized G2 custody.
"""
from __future__ import annotations
import hashlib,hmac,re,unicodedata
from collections import defaultdict

PATTERN=r"(?u)\b\w+\b"
THRESHOLD=0.80
ROSTER=("A","B","C","D")
SELECT=(("A","B"),("A","C"),("C","D"),("B","D"))
ABSTAIN=(("C","D"),("B","D"),("A","B"),("A","C"))

class DSU:
    def __init__(self,ids):self.parent={i:i for i in ids}
    def root(self,i):
        while self.parent[i]!=i:
            self.parent[i]=self.parent[self.parent[i]]
            i=self.parent[i]
        return i
    def union(self,a,b):
        x,y=self.root(a),self.root(b)
        if x!=y:self.parent[max(x,y)]=min(x,y)
    def components(self):
        out=defaultdict(list)
        for i in self.parent:out[self.root(i)].append(i)
        return [sorted(v) for v in sorted(out.values(),key=lambda v:min(v))]

def preassign(blueprints,private_hmac_key):
    """32 pair BLUEPRINT rows expected by design, never generated cases.
    The keyed order is private. Public results must suppress component membership.
    """
    ids=[b["blueprint_id"] for b in blueprints]
    if len(ids)!=len(set(ids)):raise ValueError("DUPLICATE_BLUEPRINT")
    if not private_hmac_key or not isinstance(private_hmac_key,bytes):
        raise ValueError("PRIVATE_KEY_REQUIRED")
    d=DSU(ids)
    for field in ("pair_id","event_graph_id","template_cluster_id"):
        seen={}
        for b in blueprints:
            val=b.get(field)
            if val is None:raise ValueError("MISSING_PRE_BLUEPRINT_FIELD_"+field)
            if val in seen:d.union(b["blueprint_id"],seen[val])
            else:seen[val]=b["blueprint_id"]
    comps=d.components()
    ranks=[]
    for comp in comps:
        signature="|".join(comp).encode("utf-8")
        digest=hmac.new(private_hmac_key,signature,hashlib.sha256).hexdigest()
        ranks.append((digest,comp))
    sizes=[0]*4; fold={}
    for _,comp in sorted(ranks):
        k=min(range(4),key=lambda j:(sizes[j],j))
        for item in comp:fold[item]=k
        sizes[k]+=len(comp)
    return {"component_id_pre":{i:d.root(i) for i in ids},
            "fold":fold,"component_count":len(comps),
            "case_count_by_fold":sizes,
            "cv_status":"NOT_ESTIMABLE" if len(comps)<4 or not all(sizes) else "PREFOLD_READY_NOT_VALIDATED"}

def tokens(text):
    return re.findall(PATTERN,unicodedata.normalize("NFKC",text).lower())

def fingerprint(case):
    # Card order cannot affect the normalized concatenation.
    chunks=[case["question"]]+sorted(c["text"] for c in case["cards"])
    words=tokens(" ".join(chunks))
    return set(tuple(words[i:i+5]) for i in range(len(words)-4))

def _jaccard(x,y):
    if not x and not y:return 0.0
    return len(x & y)/len(x | y)

def postcheck(cases, pre_folds, expected_twins_per_blueprint=2):
    """Build G_post on *case IDs*; map twins back to their locked G_pre fold.

    One blueprint contains two real R8 twin cases. Never cache fingerprints by
    blueprint_id or collapse twins before forming text-similarity edges.
    Source-only tests can explicitly request one twin per blueprint.
    """
    if expected_twins_per_blueprint not in (1, 2):
        raise ValueError("INVALID_EXPECTED_TWIN_COUNT")
    ids = [c["case_id"] for c in cases]
    if len(ids) != len(set(ids)):
        raise ValueError("DUPLICATE_POST_CASE_ID")
    if len(set(pre_folds)) != len(pre_folds) or not pre_folds:
        raise ValueError("INVALID_PRE_FOLD_MANIFEST")
    by_blueprint = defaultdict(list)
    for case in cases:
        bp = case["blueprint_id"]
        if bp not in pre_folds:
            raise ValueError("UNRECOGNIZED_POST_BLUEPRINT")
        by_blueprint[bp].append(case["case_id"])
    if set(by_blueprint) != set(pre_folds):
        raise ValueError("POST_CASES_MUST_MATCH_PRE_BLUEPRINT")
    if any(len(v) != expected_twins_per_blueprint for v in by_blueprint.values()):
        raise ValueError("POST_TWIN_COUNT_MISMATCH")
    d = DSU(ids)
    # Twins must be in one component even if their text differs.
    for twins in by_blueprint.values():
        for other in twins[1:]:
            d.union(twins[0], other)
    fps = {c["case_id"]: fingerprint(c) for c in cases}
    normalized_cards = {
        c["case_id"]: set(unicodedata.normalize("NFKC", x["text"]).lower()
                          for x in c["cards"])
        for c in cases
    }
    edges = []
    for i, a in enumerate(cases):
        for b in cases[i+1:]:
            aid, bid = a["case_id"], b["case_id"]
            identical_event = bool(
                a.get("event_signature") and
                a.get("event_signature") == b.get("event_signature")
            )
            same_card = bool(normalized_cards[aid] & normalized_cards[bid])
            similarity = _jaccard(fps[aid], fps[bid])
            if identical_event or same_card or similarity >= THRESHOLD:
                d.union(aid, bid)
                edges.append({
                    "a": aid, "b": bid,
                    "crossfold": pre_folds[a["blueprint_id"]] != pre_folds[b["blueprint_id"]],
                    "reasons": [tag for tag, yes in [
                        ("DUP_EVENT", identical_event),
                        ("DUP_CARD", same_card),
                        ("WORD5_JACCARD", similarity >= THRESHOLD)
                    ] if yes]
                })
    leaks = [e for e in edges if e["crossfold"]]
    return {
        "cv_status": "FOLD_LEAK_CV_INVALID" if leaks else "POST_GRAPH_NO_CROSSFOLD_EDGE",
        "crossfold_post_edges": len(leaks),
        "post_edges": len(edges),
        "post_case_count": len(ids),
        "expected_twins_per_blueprint": expected_twins_per_blueprint,
        "component_id_post": {i: d.root(i) for i in ids},
        "no_repartition": True
    }

def estimability(train_cases,component_ids):
    if len(set(component_ids.values()))<4:return "NOT_ESTIMABLE_FEWER_THAN_4_COMPONENTS"
    if {c["action"] for c in train_cases}!={"SELECT","ABSTAIN"}:
        return "NOT_ESTIMABLE_ONE_CLASS_TRAIN"
    return "ESTIMABLE_PRECONDITIONS_ONLY"

def rater_allocation_source_qa():
    """Only abstract slots. Do NOT materialize private pair IDs or packets."""
    rows=[];counts={r:{"SELECT":0,"ABSTAIN":0,"cases":0} for r in ROSTER}
    for family in range(8):
        for slot in range(4):
            sr,ar=SELECT[slot],ABSTAIN[slot]
            if len(set(sr+ar))!=4:raise AssertionError("RATER_TWIN_EXPOSURE")
            rows.append((family,slot,sr,ar))
            for r in sr:counts[r]["SELECT"]+=1;counts[r]["cases"]+=1
            for r in ar:counts[r]["ABSTAIN"]+=1;counts[r]["cases"]+=1
    assert len(rows)==32 and all(c=={"SELECT":16,"ABSTAIN":16,"cases":32}
                                 for c in counts.values())
    assert sum(c["cases"] for c in counts.values())==128
    return {"status":"PASS_SOURCE_ONLY_PROPOSAL_NOT_OWNER_APPROVED",
            "families":8,"pairs":32,"cases":64,"scores":128,"counts":counts,
            "private_assignment":"NOT_MATERIALIZED","owner_choice":"PENDING"}
