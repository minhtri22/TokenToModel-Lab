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

def _proof_dependency_closure(chosen_claims, verified_by_card, present):
    """Enumerate minimal card closures for the *selected verified claims*.

    A card can carry multiple claims with different dependency sets. Only a
    claim chosen to establish a CORE predicate can make its dependencies
    mandatory. Unverified or unrelated assertions on the same card may never
    enlarge an otherwise sufficient proof. Dependent evidence cards may carry
    alternative verified supporting claims; choose the minimal alternatives.
    """
    roots = frozenset(c["card_key"] for c in chosen_claims)
    pending = frozenset(dep for c in chosen_claims
                        for dep in c.get("depends_on", ()))
    found = set()
    state_count = 0

    def search(cards, todo, expanded):
        nonlocal state_count
        state_count += 1
        if state_count > 4096:
            raise ValueError("PROOF_ENUMERATION_LIMIT")
        if not todo:
            found.add(cards)
            return
        key = min(todo)
        rest = todo - {key}
        if key not in present:
            raise ValueError("INVALID_FIXTURE_MISSING_PROOF_DEPENDENCY")
        if key in expanded:
            search(cards, rest, expanded)
            return
        alternatives = verified_by_card.get(key) or ({"depends_on": ()},)
        for c in alternatives:
            required = frozenset(c.get("depends_on", ()))
            search(cards | {key}, rest | required, expanded | {key})

    # The chosen claims have already contributed their own dependencies.
    search(roots, pending, roots)
    return found

def _validate_claim_dependencies(claims, present):
    """Reject malformed PRIVATE proof graphs as INVALID FIXTURE, never ABSTAIN."""
    dependencies = defaultdict(set)
    for claim in claims:
        refs = claim.get("depends_on", [])
        if not isinstance(refs, (list, tuple)) or any(
            not isinstance(k, str) or not k for k in refs
        ):
            raise ValueError("INVALID_FIXTURE_BAD_PROOF_DEPENDENCIES")
        for dep in refs:
            if dep not in present:
                raise ValueError("INVALID_FIXTURE_MISSING_PROOF_DEPENDENCY")
            dependencies[claim["card_key"]].add(dep)
    active, done = set(), set()

    def visit(key):
        if key in active:
            raise ValueError("INVALID_FIXTURE_CIRCULAR_PROOF")
        if key in done:
            return
        active.add(key)
        for nxt in sorted(dependencies[key]):
            visit(nxt)
        active.remove(key)
        done.add(key)

    for key in sorted(dependencies):
        visit(key)


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
    _validate_claim_dependencies(claims, present)
    valid_proofs={};missing=False;authority_conflict=False;explicit_negative=False
    for hid,h in byh.items():
        grouped=defaultdict(list)
        verified_by_card=defaultdict(list)
        for c in claims:
            if c["hypothesis_id"]==hid and c.get("verified") is True:
                verified_by_card[c["card_key"]].append(c)
                if c["predicate"] in CORE:
                    grouped[c["predicate"]].append(c)
        # Check equal-rank contradiction BEFORE missing CORE can mask invalid fixtures.
        contradict=[c for c in claims if c["hypothesis_id"]==hid and c.get("verified") is True
                    and c["predicate"] in ("DEFEATER","NEGATIVE_RECEIPT")]
        if contradict:
            equal=any(c.get("authority_rank")==h.get("authority_rank",0)
                      and c.get("time_valid") is True for c in contradict)
            if equal:
                raise ValueError("INVALID_FIXTURE_EQUAL_AUTHORITY_CONFLICT")
            explicit_negative |= any(c["predicate"]=="NEGATIVE_RECEIPT" for c in contradict)
        if any(not grouped[p] for p in CORE):
            missing=True
            continue
        if contradict:
            greater=any(c.get("authority_rank",-1)>h.get("authority_rank",0)
                        and c.get("time_valid") is True for c in contradict)
            if greater:
                continue
        # Bounded enumeration of minimal card evidence sets, never arbitrary first key.
        variants=1
        for p in CORE:variants*=len(grouped[p])
        if variants>4096:raise ValueError("PROOF_ENUMERATION_LIMIT")
        candidates=set()
        for combo in product(*(grouped[p] for p in CORE)):
            candidates.update(_proof_dependency_closure(combo,verified_by_card,present))
            if len(candidates)>4096:
                raise ValueError("PROOF_ENUMERATION_LIMIT")
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
        if (e.get("negates_accession")==h["accession"]
            and e.get("link_event")==h["event"]
            and e.get("authorized") is True):
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
