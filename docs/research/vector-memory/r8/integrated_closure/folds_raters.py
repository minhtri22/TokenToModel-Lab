"""Deterministic G_pre/G_post and proposed four-rater allocation. NO R8 generation.
Private HMAC key and real allocation must remain under authorized G2 custody.
"""
from __future__ import annotations
import hashlib,hmac,json,re,unicodedata
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

# Production-facing gates are separate from small symbolic source fixtures.
# All real R8 consumers MUST call these gateways, never the raw fold primitives.
R8_BLUEPRINTS=32
R8_CASES=64
R8_FAMILIES=8
R8_PAIRS_PER_FAMILY=4
R8_CARDS_PER_CASE=32
R8_FAMILY_IDS=tuple(f"F{i:02d}" for i in range(1,9))
R8_PREASSIGN_LOCK_SCHEMA="TTM_VM_R8_GPRE_HMAC_V1"


def validate_r8_blueprint_manifest(blueprints):
    """Fail closed on the frozen 8-family / 32-pair production manifest."""
    if len(blueprints)!=R8_BLUEPRINTS:
        raise ValueError("INVALID_R8_BLUEPRINT_COUNT")
    bpids=[b.get("blueprint_id") for b in blueprints]
    if any(not isinstance(k,str) or not k for k in bpids):
        raise ValueError("INVALID_R8_BLUEPRINT_ID")
    if len(set(bpids))!=R8_BLUEPRINTS:
        raise ValueError("INVALID_R8_DUPLICATE_BLUEPRINT")
    pairids=[b.get("pair_id") for b in blueprints]
    if any(not isinstance(k,str) or not k for k in pairids):
        raise ValueError("INVALID_R8_PAIR_ID")
    if len(set(pairids))!=R8_BLUEPRINTS:
        raise ValueError("INVALID_R8_DUPLICATE_PAIR_ID")
    for field in ("event_graph_id","template_cluster_id"):
        if any(not isinstance(b.get(field),str) or not b[field] for b in blueprints):
            raise ValueError("INVALID_R8_BLUEPRINT_FIELD_"+field.upper())
    counts=defaultdict(int)
    for b in blueprints:
        family=b.get("relation_family")
        if not isinstance(family,str) or not family:
            raise ValueError("INVALID_R8_RELATION_FAMILY")
        counts[family]+=1
    # Family labels are preregistered *identities*, not just eight buckets.
    if set(counts)!=set(R8_FAMILY_IDS):
        raise ValueError("INVALID_R8_FAMILY_ENUM")
    if any(counts[family]!=R8_PAIRS_PER_FAMILY for family in R8_FAMILY_IDS):
        raise ValueError("INVALID_R8_FAMILY_BALANCE")
    return tuple(bpids)


def validate_r8_case_manifest(cases,blueprints):
    """Enforce 64 distinct cases, 2 action twins and 32 cards per case."""
    ids=set(validate_r8_blueprint_manifest(blueprints))
    if len(cases)!=R8_CASES:
        raise ValueError("INVALID_R8_CASE_COUNT")
    caseids=[c.get("case_id") for c in cases]
    if any(not isinstance(k,str) or not k for k in caseids):
        raise ValueError("INVALID_R8_CASE_ID")
    if len(set(caseids))!=R8_CASES:
        raise ValueError("INVALID_R8_DUPLICATE_CASE_ID")
    by_blueprint=defaultdict(list)
    for c in cases:
        bp=c.get("blueprint_id")
        if bp not in ids:
            raise ValueError("INVALID_R8_UNKNOWN_BLUEPRINT")
        by_blueprint[bp].append(c.get("action"))
        cards=c.get("cards")
        if not isinstance(cards,list) or len(cards)!=R8_CARDS_PER_CASE:
            raise ValueError("INVALID_R8_CARD_COUNT")
        keys=[card.get("key") for card in cards]
        if any(not isinstance(k,str) or not k for k in keys) or len(set(keys))!=R8_CARDS_PER_CASE:
            raise ValueError("INVALID_R8_CARD_KEYS")
        if not isinstance(c.get("question"),str):
            raise ValueError("INVALID_R8_QUESTION")
        action=c.get("action")
        if action not in ("SELECT","ABSTAIN"):
            raise ValueError("INVALID_R8_ACTION")
        target=c.get("target_key")
        if action=="SELECT" and target not in keys:
            raise ValueError("INVALID_R8_SELECT_TARGET")
        if action=="ABSTAIN" and target is not None:
            raise ValueError("INVALID_R8_ABSTAIN_TARGET")
    if set(by_blueprint)!=ids or any(sorted(a)!=["ABSTAIN","SELECT"] for a in by_blueprint.values()):
        raise ValueError("INVALID_R8_TWIN_ACTION_BALANCE")
    return True


def _r8_private_key(private_hmac_key):
    """Only the authorized private custodian may supply the REAL G2 key."""
    if type(private_hmac_key) is not bytes or len(private_hmac_key)<32:
        raise ValueError("INVALID_R8_PRIVATE_HMAC_KEY")
    return private_hmac_key


def _r8_hmac(private_hmac_key,purpose,document):
    raw=json.dumps(document,sort_keys=True,ensure_ascii=False,
                   separators=(",",":"),allow_nan=False).encode("utf-8")
    return hmac.new(private_hmac_key,purpose.encode("ascii")+b"\0"+raw,
                    hashlib.sha256).hexdigest()


def _r8_blueprint_lock(blueprints,private_hmac_key):
    # All JSON blueprint fields are bound; no reinterpretation after G_pre.
    ordered=sorted(blueprints,key=lambda b:b["blueprint_id"])
    try:
        return _r8_hmac(private_hmac_key,"R8_GPRE_BLUEPRINT_V1",ordered)
    except (TypeError,ValueError,OverflowError) as exc:
        raise ValueError("INVALID_R8_BLUEPRINT_CANONICAL_JSON") from exc


def preassign_r8(blueprints,private_hmac_key):
    """Pre-G3 production gate. Result MUST be sealed by actual G2 custodian.

    This does not generate R8, prove the custody timestamp, or publish the fold.
    """
    validate_r8_blueprint_manifest(blueprints)
    key=_r8_private_key(private_hmac_key)
    blueprint_lock=_r8_blueprint_lock(blueprints,key)
    assignment=preassign(blueprints,key)
    # Freeze blueprint bytes, actual fold + graph components and readiness status.
    result={**assignment,
            "lock_schema":R8_PREASSIGN_LOCK_SCHEMA,
            "blueprint_hmac":blueprint_lock}
    result["preassignment_hmac"]=_r8_hmac(key,"R8_GPRE_FOLDS_V1",
        {k:result[k] for k in ("lock_schema","blueprint_hmac","fold",
                                "component_id_pre","component_count",
                                "case_count_by_fold","cv_status")})
    return result


def postcheck_r8(cases,blueprints,locked_preassignment,private_hmac_key):
    """Verify G2 HMAC/source-bound G_pre before G_post, never trust a dict status.

    The private key MUST originate in protected custody. Recomputing here checks
    exact fold/blueprint integrity; custody timestamps are separate evidence.
    """
    validate_r8_case_manifest(cases,blueprints)
    key=_r8_private_key(private_hmac_key)
    if not isinstance(locked_preassignment,dict):
        raise ValueError("INVALID_R8_LOCKED_FOLD_MANIFEST")
    if locked_preassignment.get("lock_schema")!=R8_PREASSIGN_LOCK_SCHEMA:
        raise ValueError("INVALID_R8_PREASSIGNMENT_SCHEMA")
    expected=preassign_r8(blueprints,key)
    for field in ("blueprint_hmac","preassignment_hmac"):
        supplied=locked_preassignment.get(field)
        if not isinstance(supplied,str) or not hmac.compare_digest(
            supplied,expected[field]
        ):
            raise ValueError("INVALID_R8_HMAC_PROVENANCE_"+field.upper())
    for field in ("fold","component_id_pre","component_count",
                  "case_count_by_fold","cv_status"):
        if locked_preassignment.get(field)!=expected[field]:
            raise ValueError("INVALID_R8_PREASSIGNMENT_MISMATCH_"+field.upper())
    folds=expected["fold"]
    if len(set(folds.values()))!=4 or expected["cv_status"]!="PREFOLD_READY_NOT_VALIDATED":
        raise ValueError("R8_CV_NOT_ESTIMABLE_PREASSIGNMENT")
    return postcheck(cases,folds,expected_twins_per_blueprint=2)

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
