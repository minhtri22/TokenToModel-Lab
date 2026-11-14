"""R8 V4 answer-hypothesis proof checker. NON-R8 CONTRACT ONLY; no gold input.
AI-authored same-agent implementation; NOT independently validated/owner-approved.
"""
from __future__ import annotations
from collections import defaultdict
from itertools import product

CORE = ("IDENTITY","SCOPE","EVENT","LOCATION","TIME_VALID","AUTHORIZED")
MANDATORY = CORE + ("NOT_DEFEATED",)
PRIORITY = ("UNRESOLVED_AUTHORITY","MULTIPLE_SUPPORTED_HYPOTHESES",
            "MISSING_PREMISE","NO_SUPPORTED_HYPOTHESIS")

def hypothesis_identity(h):
    """Identity is record, accession, event, location, interval and authority version."""
    keys = ("record","accession","event","location","interval","authority_policy")
    if any(not isinstance(h.get(k),str) or not h[k] for k in keys):
        raise ValueError("INVALID_HYPOTHESIS_FIELDS")
    return tuple(h[k] for k in keys)

def _has_cycle(claims, chosen):
    # Dependency cycles must not become circular proofs.
    adj = {k:set() for k in chosen}
    for c in claims:
        if c["card_key"] in chosen:
            adj[c["card_key"]].update(k for k in c.get("depends_on",[]) if k in chosen)
    active, done = set(),set()
    def visit(n):
        if n in active:return True
        if n in done:return False
        active.add(n)
        if any(visit(m) for m in adj[n]):return True
        active.remove(n);done.add(n)
        return False
    return any(visit(x) for x in adj if x not in done)

def resolve(hypotheses, claims, cards, question_kind="RECORD_SELECTION"):
    """Reconstruct hypotheses from typed claims rather than reading generator gold.
    Input is PRIVATE proof schema. Caller must ensure claims came from reviewed records.
    NOT_DEFEATED is computed, never accepted as an unsupported affirmative marker.
    """
    if question_kind!="RECORD_SELECTION":raise ValueError("UNSUPPORTED_QUESTION")
    cardkeys=[c["key"] for c in cards]
    if len(cardkeys)!=len(set(cardkeys)):raise ValueError("DUPLICATE_CARD_KEY")
    present=set(cardkeys)
    byh={}; ids=set()
    for h in hypotheses:
        hid=h["id"]
        if hid in ids:raise ValueError("DUPLICATE_HYPOTHESIS")
        ids.add(hid);hypothesis_identity(h)
        byh[hid]=h
    for c in claims:
        if c["hypothesis_id"] not in ids or c["card_key"] not in present:
            raise ValueError("CLAIM_REFERENCE_INVALID")
        if c["predicate"] not in CORE+("DEFEATER","NEGATIVE_RECEIPT","NOT_DEFEATED"):
            raise ValueError("UNKNOWN_TYPED_CLAIM")
    valid_proofs={};missing=False;authority_conflict=False;explicit_negative=False
    for hid,h in byh.items():
        grouped=defaultdict(set)
        for c in claims:
            if c["hypothesis_id"]==hid and c["predicate"] in CORE and c.get("verified") is True:
                grouped[c["predicate"]].add(c["card_key"])
        if any(not grouped[p] for p in CORE):
            missing=True
            continue
        contradict=[c for c in claims if c["hypothesis_id"]==hid and c.get("verified") is True
                    and c["predicate"] in ("DEFEATER","NEGATIVE_RECEIPT")]
        if contradict:
            explicit_negative |= any(c["predicate"]=="NEGATIVE_RECEIPT" for c in contradict)
            equal=any(c.get("authority_rank")==h.get("authority_rank",0)
                      and c.get("time_valid") is True for c in contradict)
            greater=any(c.get("authority_rank",-1)>h.get("authority_rank",0)
                        and c.get("time_valid") is True for c in contradict)
            if equal:authority_conflict=True
            if greater or equal:continue
        # Bounded enumeration of minimal card evidence sets, never arbitrary first key.
        variants=1
        for p in CORE:variants*=len(grouped[p])
        if variants>4096:raise ValueError("PROOF_ENUMERATION_LIMIT")
        candidates=set()
        for combo in product(*(sorted(grouped[p]) for p in CORE)):
            s=frozenset(combo)
            if not _has_cycle(claims,s):candidates.add(s)
        minimal=sorted((s for s in candidates if not any(t<s for t in candidates)),
                       key=lambda s:(len(s),tuple(sorted(s))))
        if not minimal:
            missing=True;continue
        valid_proofs[hid]=[sorted(x) for x in minimal]
    supported=list(valid_proofs)
    reasons=[]
    if authority_conflict:reasons.append("UNRESOLVED_AUTHORITY")
    if len(supported)>1:reasons.append("MULTIPLE_SUPPORTED_HYPOTHESES")
    if missing or explicit_negative:reasons.append("MISSING_PREMISE")
    if not supported:reasons.append("NO_SUPPORTED_HYPOTHESIS")
    # A key is not selected by hash/order; target is a separate designated record card.
    if len(supported)==1 and not authority_conflict:
        h=byh[supported[0]]
        matches=[c["key"] for c in cards if c.get("target_identity")==hypothesis_identity(h)]
        if len(matches)!=1:raise ValueError("ONE_KEY_CONTRACT_INVALID")
        return {"action":"SELECT","target_key":matches[0],"supported_hypotheses":supported,
                "proof_sets":valid_proofs,"primary_abstain_reason":None,
                "all_applicable_reasons":[],"required_predicates":MANDATORY}
    reasons=sorted(set(reasons),key=PRIORITY.index)
    return {"action":"ABSTAIN","target_key":None,"supported_hypotheses":supported,
            "proof_sets":valid_proofs,"primary_abstain_reason":reasons[0],
            "all_applicable_reasons":reasons,"required_predicates":MANDATORY}

def receipt_f07(case):
    """Toy P-REC-V1: actual authoritative ACCESSION graph edge is decisive.
    No gold label, 'signed' keyword, or presence of an audit card is inspected.
    """
    if case.get("policy")!="P-REC-V1":raise ValueError("POLICY_NOT_P_REC_V1")
    target=case["target"]
    h={"id":"hX","record":target["record"],"accession":target["accession"],
       "event":target["event"],"location":target["location"],
       "interval":target["interval"],"authority_policy":"P-REC-V1",
       "authority_rank":2}
    evidence=case["evidence"]
    cards=[dict(key=target["key"],target_identity=hypothesis_identity(h))]
    cards.extend({"key":e["key"]} for e in evidence)
    claims=[dict(hypothesis_id="hX",card_key=target["key"],
                 predicate=p,verified=True)
            for p in ("IDENTITY","SCOPE","EVENT","LOCATION","TIME_VALID")]
    for e in evidence:
        if (e.get("authorized") is True and e.get("link_accession")==h["accession"]
            and e.get("link_event")==h["event"] and e.get("time_valid") is True
            and e.get("type") in ("ACKNOWLEDGEMENT","AUDIT_RECONCILIATION")):
            claims.append(dict(hypothesis_id="hX",card_key=e["key"],
                               predicate="AUTHORIZED",verified=True))
        if e.get("negates_accession")==h["accession"] and e.get("authorized") is True:
            claims.append(dict(hypothesis_id="hX",card_key=e["key"],
                 predicate="NEGATIVE_RECEIPT",verified=True,
                 authority_rank=e.get("authority_rank",3),time_valid=e.get("time_valid",False)))
    return resolve([h],claims,cards)

def f07_symbolic_twins():
    """Same categories and marker vocabulary; no R8 pairs or private maps."""
    common={"policy":"P-REC-V1","target":{"key":"receipt-card","record":"R",
             "accession":"X","event":"E","location":"L1","interval":"t0"}}
    def twin(authority_link):
        audit=[{"key":"audit-authoritative","type":"AUDIT_RECONCILIATION",
                "authorized":True,"link_accession":authority_link,
                "link_event":"E","time_valid":True,"text":"signed audit received X Y"},
               {"key":"audit-copy","type":"AUDIT_RECONCILIATION",
                "authorized":False,"link_accession":"Y" if authority_link=="X" else "X",
                "link_event":"E","time_valid":True,"text":"signed audit received X Y"},
               {"key":"forecast","type":"FORECAST","authorized":False,
                "link_accession":"X","link_event":"E","time_valid":True,
                "text":"signed audit received X Y"}]
        return {**common,"evidence":audit}
    return twin("X"),twin("Y")
