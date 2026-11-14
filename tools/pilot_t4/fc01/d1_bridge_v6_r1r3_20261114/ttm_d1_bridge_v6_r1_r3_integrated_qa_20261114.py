#!/usr/bin/env python3
"""TTM D1 Bridge V6 prospective R1/R3 candidate / SOURCE-ONLY QA.

Self-test: python ttm_d1_bridge_v6_r1_r3_integrated_qa_20261114.py --selftest --out ./qa_out
Locally pinned candidate: python ...py --repo D:\\WORK\\RESEARCH\\TokenToModel-Lab
No GPU/train/inference, no private AST or gold, no Git writes.
"""
from __future__ import annotations
import argparse
import copy
import hashlib
import json
import subprocess
from dataclasses import dataclass
from pathlib import Path
from typing import Callable

FROZEN = "dd52804685d186c17e600221ffb16ce78aea12ea"
ROOT = "artifacts/research/ttm-small4m-fact-conditioning"
V5 = ROOT + "/TTM_D1_BRIDGE_V5_SINGLE_PACKET_SEMANTIC_ALIAS_HIDING_COMMITMENT_CONTRAST_PARAMS_SOURCE_CONTRACT_20261114.json"
V6 = ROOT + "/TTM_D1_BRIDGE_V6_SINGLE_PACKET_TYPED_FOUR_CATEGORY_ONTOLOGY_AUTHENTICATED_LEDGER_SOURCE_CONTRACT_20261114.json"
EXPECTED_V5_BLOB = "f4103f571ea80f909d59b1d9fe5f426702f53fa4"
EXPECTED_V6_BLOB = "c6ac330c40e31035116add165ef30fa58af59639"
TIMES = ("BEFORE_T0", "T0", "T1", "T2")
SEEDS = tuple(range(20261120, 20261131)) + (20261201,)
CATEGORY_IDS = ("entity_location", "causal_reasoning", "rule_constraint", "goal_persistence")
IMMEDIATE = ("RELOCATE", "CARRY", "TRANSFER", "RETAIN", "ACTIVATE")


def git_blob_sha1(data: bytes) -> str:
    return hashlib.sha1(b"blob " + str(len(data)).encode("ascii") + b"\0" + data).hexdigest()


def git_show(repo: Path, relative: str, expected: str) -> dict:
    r = subprocess.run(["git", "-C", str(repo), "show", f"{FROZEN}:{relative}"],
                       capture_output=True, check=True)
    got = git_blob_sha1(r.stdout)
    if got != expected:
        raise RuntimeError(f"FROZEN_BLOB_MISMATCH {relative}: {got} != {expected}")
    return json.loads(r.stdout.decode("utf-8"))


def t(tick: str) -> int:
    if tick not in TIMES:
        raise ValueError("BAD_TIME:" + str(tick))
    return TIMES.index(tick)


def base_state() -> dict:
    return {
        "current_time": "T0",
        "location_agent": {"a0": "l0", "a1": "l1"},
        "location_item": {"i0": "l0", "i1": "l0"},
        "holder": {"i0": "NONE", "i1": "NONE"},
        "power": {"d0": "OFF", "d1": "OFF"},
        "trigger_fired": {"g0": False, "g1": False},
        "scheduled_at": {"g0": "T1", "g1": "T2"},
        "linked_trigger": {"d0": "g0", "d1": "NONE"},
        "protected_until": {"i0": "BEFORE_T0", "i1": "BEFORE_T0"},
        "defer_until": {"a0": "NONE", "a1": "NONE"},
        "external_transfer_request": {"item": "NONE", "recipient": "NONE", "at": "NONE"},
    }


def valid_state(s: dict) -> bool:
    # This is a standalone synthetic finite-state checker, NOT the D1 science oracle.
    try:
        assert set(s) == set(base_state())
        for field, expected in (("location_agent", {"a0", "a1"}),
                                ("location_item", {"i0", "i1"}),
                                ("holder", {"i0", "i1"}),
                                ("power", {"d0", "d1"}),
                                ("trigger_fired", {"g0", "g1"}),
                                ("scheduled_at", {"g0", "g1"}),
                                ("linked_trigger", {"d0", "d1"}),
                                ("protected_until", {"i0", "i1"}),
                                ("defer_until", {"a0", "a1"})):
            assert set(s[field]) == expected
        assert s["current_time"] in TIMES[1:]
        assert all(loc in ("l0", "l1") for loc in s["location_agent"].values())
        assert all(loc in ("l0", "l1") for loc in s["location_item"].values())
        assert all(x in ("NONE", "a0", "a1") for x in s["holder"].values())
        assert all(x in ("OFF", "ON") for x in s["power"].values())
        assert all(type(x) is bool for x in s["trigger_fired"].values())
        assert all(x in (*TIMES[1:], "NONE") for x in s["scheduled_at"].values())
        assert all(x in ("NONE", "g0", "g1") for x in s["linked_trigger"].values())
        assert all(x in TIMES for x in s["protected_until"].values())
        assert all(x in (*TIMES[1:], "NONE") for x in s["defer_until"].values())
        assert set(s["external_transfer_request"]) == {"item", "recipient", "at"}
        er = s["external_transfer_request"]
        assert er["item"] in ("NONE", "i0", "i1")
        assert er["recipient"] in ("NONE", "a0", "a1")
        assert er["at"] in (*TIMES[1:], "NONE")
        assert (er["item"] == "NONE") == (er["recipient"] == "NONE") == (er["at"] == "NONE")
        for item, holder in s["holder"].items():
            if holder != "NONE":
                assert s["location_item"][item] == s["location_agent"][holder]
        return True
    except (KeyError, TypeError, ValueError, AssertionError):
        return False


def _events(s: dict, start: str, end: str) -> None:
    # Deterministic time/event policy: scheduled trigger firings idempotent;
    # exogenous transfer is attempted at its timestamp and protected guard wins.
    for tick in TIMES[t(start) + 1:t(end) + 1]:
        for g, scheduled in s["scheduled_at"].items():
            if scheduled == tick:
                s["trigger_fired"][g] = True
        er = s["external_transfer_request"]
        if er["at"] == tick:
            item, rec = er["item"], er["recipient"]
            if s["holder"][item] not in ("NONE", rec) and t(s["protected_until"][item]) < t(tick):
                s["holder"][item] = rec
                s["location_item"][item] = s["location_agent"][rec]
            er.update(item="NONE", recipient="NONE", at="NONE")


def step(state: dict, actor: str, verb: str, target: str, when: str, qualifier: str = "NONE") -> dict:
    if not valid_state(state):
        raise ValueError("INVALID_INITIAL_STATE")
    s = copy.deepcopy(state)
    now = s["current_time"]
    if actor not in s["location_agent"]:
        raise ValueError("BAD_AGENT")
    if verb in IMMEDIATE:
        if when != now: raise ValueError("GLOBAL_TIME_GUARD")
    elif verb == "WAIT":
        if when not in TIMES[1:] or t(when) <= t(now): raise ValueError("WAIT_FUTURE_GUARD")
    else:
        raise ValueError("BAD_VERB")
    if verb in ("RELOCATE", "CARRY"):
        if target not in s["holder"] or qualifier not in ("l0", "l1"):
            raise ValueError("BAD_TYPED_SLOTS")
        if s["holder"][target] != "NONE" or s["location_item"][target] != s["location_agent"][actor]:
            raise ValueError("NOT_ACCESSIBLE_UNHELD")
        if (s["location_item"][target] if verb == "RELOCATE" else s["location_agent"][actor]) == qualifier:
            raise ValueError("NO_OP_LOCATION")
        if verb == "RELOCATE":
            s["location_item"][target] = qualifier
        else:
            # Move all existing held items with their holder (critical for invariant).
            previously_held = [i for i, h in s["holder"].items() if h == actor]
            s["location_agent"][actor] = qualifier
            s["holder"][target] = actor
            for i in set(previously_held + [target]):
                s["location_item"][i] = qualifier
    elif verb == "TRANSFER":
        if target not in s["holder"] or qualifier not in s["location_agent"]:
            raise ValueError("BAD_TYPED_SLOTS")
        if s["holder"][target] != actor or actor == qualifier:
            raise ValueError("TRANSFER_HOLDER_GUARD")
        if t(s["protected_until"][target]) >= t(now):
            raise ValueError("PROTECTION_PRIORITY_BLOCKS_TRANSFER")
        s["holder"][target] = qualifier
        s["location_item"][target] = s["location_agent"][qualifier]
    elif verb == "RETAIN":
        if target not in s["holder"] or qualifier not in TIMES[1:]:
            raise ValueError("BAD_TYPED_SLOTS")
        if s["holder"][target] != actor or t(qualifier) < t(now):
            raise ValueError("RETAIN_GUARD")
        # Monotone update: never shorten previously accepted protection.
        if t(qualifier) > t(s["protected_until"][target]):
            s["protected_until"][target] = qualifier
    elif verb == "ACTIVATE":
        if target not in s["power"] or qualifier != "NONE" or s["power"][target] != "OFF":
            raise ValueError("ACTIVATE_GUARD")
        s["power"][target] = "ON"
        linked = s["linked_trigger"][target]
        if linked != "NONE": s["trigger_fired"][linked] = True
    elif verb == "WAIT":
        if target not in s["trigger_fired"] or qualifier != "NONE":
            raise ValueError("WAIT_TYPED_GUARD")
        if s["trigger_fired"][target] or s["scheduled_at"][target] != when:
            raise ValueError("WAIT_EVENT_GUARD")
        s["defer_until"][actor] = when
        _events(s, now, when)
        s["current_time"] = when
    if not valid_state(s):
        raise ValueError("POST_INVARIANT_BROKEN")
    return s


def fixtures() -> dict:
    cat = {}
    s = base_state()
    cat["CAT01"] = {"category": "entity_location", "state": s,
        "A": ("a0", "RELOCATE", "i0", "T0", "l1"),
        "B": ("a0", "CARRY", "i0", "T0", "l1")}
    s = base_state()
    cat["CAT02"] = {"category": "causal_reasoning", "state": s,
        "A": ("a0", "ACTIVATE", "d0", "T0", "NONE"),
        "B": ("a0", "WAIT", "g0", "T1", "NONE")}
    s = base_state()
    s["holder"]["i0"] = "a0"
    s["location_item"]["i0"] = "l0"
    s["protected_until"]["i0"] = "T1"
    cat["CAT03"] = {"category": "rule_constraint", "state": s,
        "A": ("a0", "WAIT", "g1", "T2", "NONE"),
        "B": ("a0", "TRANSFER", "i0", "T0", "a1"),
        "B_intervention": {"protected_until": {"i0": "BEFORE_T0"}},
        "shared_goal": "transfer i0 to a1 at first compliant opportunity; wait for g1 if blocked"}
    s = base_state()
    s["holder"]["i1"] = "a0"
    s["location_item"]["i1"] = "l0"
    s["external_transfer_request"] = {"item": "i1", "recipient": "a1", "at": "T1"}
    cat["CAT04"] = {"category": "goal_persistence", "state": s,
        "A": ("a0", "RETAIN", "i1", "T0", "T2"),
        "B": ("a0", "WAIT", "g0", "T1", "NONE"),
        "B_intervention": {"external_transfer_request": {"item": "NONE", "recipient": "NONE", "at": "NONE"}},
        "shared_goal": "keep holder(i1)=a0 through T2, with or without exogenous request"}
    return cat


def fixture_outcomes() -> dict:
    results = {}
    for fid, f in fixtures().items():
        assert valid_state(f["state"])
        a = step(f["state"], *f["A"])
        b_state = copy.deepcopy(f["state"])
        for k, v in f.get("B_intervention", {}).items():
            b_state[k].update(v)
        assert valid_state(b_state)
        b = step(b_state, *f["B"])
        if fid == "CAT01":
            assert a["holder"]["i0"] == "NONE" and b["holder"]["i0"] == "a0"
            assert a["location_item"]["i0"] == b["location_item"]["i0"] == "l1"
        if fid == "CAT02":
            assert a["power"]["d0"] == "ON" and a["trigger_fired"]["g0"]
            assert b["power"]["d0"] == "OFF" and b["trigger_fired"]["g0"]
            assert b["current_time"] == "T1"
        if fid == "CAT03":
            assert a["holder"]["i0"] == "a0" and a["current_time"] == "T2"
            assert b["holder"]["i0"] == "a1" and b["location_item"]["i0"] == "l1"
            # Under the same shared goal and A state, immediate transfer is forbidden.
            try: step(f["state"], *f["B"])
            except ValueError as exc: assert str(exc) == "PROTECTION_PRIORITY_BLOCKS_TRANSFER"
            else: raise AssertionError("CAT03 guard violated")
        if fid == "CAT04":
            assert a["protected_until"]["i1"] == "T2" and b["holder"]["i1"] == "a0"
            # WAIT on A state (without RETAIN) triggers forbidden exogenous transfer.
            lost = step(f["state"], *f["B"])
            assert lost["holder"]["i1"] == "a1"
            # RETAIN then WAIT must preserve across exogenous request.
            retained = step(a, *f["B"])
            assert retained["holder"]["i1"] == "a0"
        results[fid] = {"category": f["category"], "complete_state": True,
                        "reachable_A": True, "reachable_B": True,
                        "note": "Synthetic trace only; not real TRAIN/EVAL skeleton or unique-gold proof"}
    return results


def run_qa() -> dict:
    checks: list[tuple[str, bool]] = []
    negatives: list[tuple[str, bool]] = []
    def ok(name: str, cond: bool): checks.append((name, bool(cond)))
    def reject(name: str, cb: Callable[[], object]):
        try: cb()
        except (ValueError, AssertionError, KeyError): negatives.append((name, True))
        else: negatives.append((name, False))
    ok("SEED_FROZEN_EXPECTED_12", len(SEEDS) == 12 and SEEDS[-1] == 20261201)
    ok("TIME_ORDER", TIMES == ("BEFORE_T0", "T0", "T1", "T2"))
    fx = fixture_outcomes()
    ok("FOUR_COMPLETE_SYNTHETIC_TRACES", len(fx) == 4)
    ok("FOUR_ORIGINAL_CATEGORY_IDS", tuple(v["category"] for v in fx.values()) == CATEGORY_IDS)
    ok("CAT03_CONTROLLED_SHARED_GOAL", "shared_goal" in fixtures()["CAT03"])
    ok("CAT04_CONTROLLED_SHARED_GOAL", "shared_goal" in fixtures()["CAT04"])
    ok("CAT04_DISTRACTOR_TYPED_EVENT", fixtures()["CAT04"]["state"]["external_transfer_request"]["at"] == "T1")
    reject("NEG_V6_FROZEN_SEED_DRIFT", lambda: _require_exact_seeds(list(SEEDS[:-1]) + [20261131]))
    ok("MOCK_CONTRACT_CANDIDATE_PATCH_RUNS", mock_contract_test())
    s = base_state(); s["holder"]["i0"] = "a0"
    ok("STATE_COMPLETENESS", valid_state(s))
    # Protection extension but not shortening, and strict inclusive protection boundary.
    s = base_state(); s["holder"]["i1"] = "a0"; s["protected_until"]["i1"] = "T2"
    ext = step(s, "a0", "RETAIN", "i1", "T0", "T1")
    ok("RETAIN_MONOTONE", ext["protected_until"]["i1"] == "T2")
    # Deliberately reproduce the V6 set(guard) mutant and require invariant rejection.
    mutant_short = copy.deepcopy(ext)
    mutant_short["protected_until"]["i1"] = "T1"
    reject("NEG_V6_SET_MUTANT_SHORTENS_PROTECTION", lambda: _assert_protection_monotone(s, mutant_short, "i1"))
    reject("NEG_TRANSFER_WITHIN_PROTECTION", lambda: step(s, "a0", "TRANSFER", "i1", "T0", "a1"))
    reject("NEG_RELOCATE_FUTURE_TIME", lambda: step(base_state(), "a0", "RELOCATE", "i0", "T2", "l1"))
    reject("NEG_CARRY_FUTURE_TIME", lambda: step(base_state(), "a0", "CARRY", "i0", "T1", "l1"))
    reject("NEG_RETAIN_FUTURE_TIME", lambda: step(s, "a0", "RETAIN", "i1", "T1", "T2"))
    reject("NEG_ACTIVATE_FUTURE_TIME", lambda: step(base_state(), "a0", "ACTIVATE", "d0", "T1"))
    reject("NEG_WAIT_NO_SCHEDULE", lambda: step(base_state(), "a0", "WAIT", "g0", "T2"))
    reject("NEG_WAIT_SAME_TIME", lambda: step(base_state(), "a0", "WAIT", "g0", "T0"))
    s = base_state(); s["holder"]["i1"] = "a0"
    carried = step(s, "a0", "CARRY", "i0", "T0", "l1")
    ok("CARRY_MOVES_EVERY_HELD_ITEM", carried["location_item"]["i1"] == "l1" and valid_state(carried))
    reject("NEG_CARRY_OLD_EFFECT_BREAKS_INVARIANT", lambda: _broken_carry_old(s))
    reject("NEG_INCOMPLETE_HOLDER_LOCATION", lambda: _require_valid(_missing_holder_location()))
    old = base_state(); old["power"]["d0"] = "OFF"
    on = step(old, "a0", "ACTIVATE", "d0", "T0")
    ok("ACTIVATE_LINKED_TRIGGER_EARLY", on["trigger_fired"]["g0"])
    reject("NEG_WAIT_ON_ALREADY_FIRED", lambda: step(on, "a0", "WAIT", "g0", "T1"))
    # Check holder-location preservation over a finite combinatorial sample.
    count = 0
    for agent_a in ("l0", "l1"):
        for agent_b in ("l0", "l1"):
            for holder0 in ("NONE", "a0", "a1"):
                for holder1 in ("NONE", "a0", "a1"):
                    for item0_loc in ("l0", "l1"):
                        for item1_loc in ("l0", "l1"):
                            w = base_state()
                            w["location_agent"] = {"a0": agent_a, "a1": agent_b}
                            w["location_item"] = {"i0": item0_loc, "i1": item1_loc}
                            w["holder"] = {"i0": holder0, "i1": holder1}
                            if not valid_state(w): continue
                            for verb in ("RELOCATE", "CARRY"):
                                for item in ("i0", "i1"):
                                    for agent in ("a0", "a1"):
                                        for loc in ("l0", "l1"):
                                            try: z = step(w, agent, verb, item, "T0", loc)
                                            except ValueError: continue
                                            assert valid_state(z)
                                            count += 1
    ok("FINITE_CARRY_RELOCATE_HOLDER_LOCATION_INVARIANTS", count >= 20)
    return {"positive_pass": sum(v for _, v in checks), "positive_total": len(checks),
            "negative_detected": sum(v for _, v in negatives), "negative_total": len(negatives),
            "checks": dict(checks), "negative_cases": dict(negatives),
            "finite_valid_transitions_exercised": count, "four_fixtures": fx,
            "claim_limit": "SYNTHETIC_SOURCE_ONLY_NO_REAL_AST_GOLD_OR_NONOVERLAP"}


def _require_exact_seeds(xs: list[int]):
    if tuple(xs) != SEEDS: raise ValueError("FROZEN_SEED_ARRAY_MISMATCH")


def _assert_protection_monotone(before: dict, after: dict, item: str):
    if t(after["protected_until"][item]) < t(before["protected_until"][item]):
        raise AssertionError("PROTECTION_WAS_SHORTENED")


def _broken_carry_old(s: dict):
    q = copy.deepcopy(s)
    q["holder"]["i0"] = "a0"
    q["location_agent"]["a0"] = "l1"
    q["location_item"]["i0"] = "l1"
    _require_valid(q)


def _missing_holder_location():
    s = base_state(); s["holder"]["i0"] = "a0"; del s["location_agent"]["a0"]
    return s


def _require_valid(state: dict):
    if not valid_state(state): raise ValueError("STATE_INVALID")


def build_candidate(v5: dict, v6: dict) -> tuple[dict, dict]:
    assert v5["AM03_stats"]["seed_values"] == list(SEEDS), "V5_FROZEN_SEEDS_UNEXPECTED"
    assert v6["AM03_stats"]["seeds"][:-1] == list(SEEDS[:-1]), "V6_SEED_PREFIX_DRIFT"
    assert v6["AM03_stats"]["seeds"][-1] == 20261131, "V6_SEED_DRIFT_NOT_PRESENT_CHECK_PROTOCOL"
    out = copy.deepcopy(v6)
    out["schema"] = "ttm.d1_bridge.v6.prospective_r1_r3_integrated_candidate.v1"
    out["AM03_stats"]["seeds"] = list(SEEDS)
    out["AM03_stats"]["status"] = "RESTORED_V5_EXACT_SEEDS_CANDIDATE_NOT_APPROVED"
    A = out["AM01_four_category_typed_action"]
    slots = {a["id"]: a for a in A["action_slot_contract"]}
    assert set(slots) == {*IMMEDIATE, "WAIT"}
    for verb in IMMEDIATE:
        if ["eq", "time", "current_time"] not in slots[verb]["preconditions"]:
            slots[verb]["preconditions"].append(["eq", "time", "current_time"])
    slots["RETAIN"]["effects"] = [["set_max", "protected_until(target)", "qualifier"],
                                         ["preserve", "holder(target)"]]
    slots["CARRY"]["effects"] = [["set", "holder(target)", "agent"],
                                        ["set", "location(agent)", "qualifier"],
                                        ["forall_set", "location(item)", "qualifier", "preholder(item)=agent OR item=target"]]
    slots["WAIT"]["effects"] = [["set", "defer_until(agent,target)", "time"],
                                       ["atomic_advance", "current_time", "time", "all_scheduled_events_in_order"],
                                       ["set", "trigger_fired(target)", "true"]]
    A["typed_finite_domains"]["time_transition"] = (
        "For RELOCATE/CARRY/TRANSFER/RETAIN/ACTIVATE, time_id=current_time. "
        "WAIT's time_id is a future scheduled trigger timestamp; WAIT is atomic: record defer_until, "
        "advance current_time to that timestamp without permitting intervening agent actions, "
        "process scheduled trigger(s) and exogenous priority-filtered events at each intermediate tick. "
        "Events for already-fired triggers are idempotent; no double fire. "
        "At each tick: scheduled trigger events first, exogenous transfer request second, "
        "protected transfer guard takes priority; no other spontaneous transitions. "
        "Protection inclusive through protected_until; transfer only when protected_until < current_time. "
        "TIME=NONE reserved for explicit anytime but inadmissible to these six action transition contracts."
    )
    A["typed_finite_domains"]["state_fluents"].append("external_transfer_request(item,recipient,at) [synthetic exogenous event]")
    A["typed_finite_domains"]["invariants"].extend([
        "RETAIN protected_until(item) never decreases",
        "held item locations update atomically with their holder's CARRY location",
        "WAIT advances time atomically and cannot allow action before scheduled future trigger",
        "scheduled trigger activation is idempotent; transfer requests are priority-filtered"
    ])
    A["synthetic_non_EVAL_category_fixtures"] = [
        {"id": id_, **{k: v for k, v in f.items() if k != "state"}, "state": f["state"],
         "classification": "PUBLIC_SYNTHETIC_ONLY_NOT_TRAIN_EVAL_GOLD"}
        for id_, f in fixtures().items()
    ]
    A["actual_AST_source"] = "NOT_IMPLEMENTED"
    A["actual_reachable_checker"] = "NOT_IMPLEMENTED_FOR_RESEARCH_DATASET_SYNTHETIC_QA_ONLY"
    A["actual_4x4_skeletons"] = "NOT_GENERATED"
    A["QA"] = "SYNTHETIC_SOURCE_CANDIDATE_QA_ONLY"
    out["prospective_integrated_amendment"] = {
        "status": "CANDIDATE_REVIEW_REQUIRED_NO_SCIENCE_PERMISSION",
        "frozen_V6_blob_sha1": EXPECTED_V6_BLOB,
        "frozen_V5_blob_sha1": EXPECTED_V5_BLOB,
        "issues_addressed": ["D1V5-N01", "V6-R3-FROZEN_SEED_DRIFT"],
        "discovered_additional_R1_issue": "CARRY did not propagate holder location of other items",
        "semantic_scope": "fully-typed time/holder/trigger/exogenous-event source candidate; independent oracle absent",
        "R1_remaining_admission": "HOLD until actual typed 4 TRAIN + 4 OOD distinct skeletons per category, reachable oracle uniqueness, independent nonoverlap; no generation bypass",
        "R5_status": "INHERITED_PASS_SCOPED_DESIGN_PRODUCTION_HOLD",
        "science": "HOLD", "TEST_Q1Q2": "SEALED", "GPU": 0, "TRAINING": 0,
        "owner_permission": "NOT_GRANTED", "source_prereg_freeze": "NOT_AUTHORIZED",
    }
    # No silent changes to passed source contracts.
    for k in ("AM02_parser", "AM04_categories", "AM05_audit_ledger_binding", "AM06_contrastive"):
        assert out[k] == v6[k], "UNAUTHORIZED_INHERITED_AXIS_CHANGE " + k
    assert out["AM03_stats"]["seeds"] == v5["AM03_stats"]["seed_values"]
    assert out["gates"] == v6["gates"]
    receipt = {"operation": "TTM_D1_BRIDGE_V6_R1_R3_SINGLE_INTEGRATED_PROSPECTIVE_CORRECTION_SOURCE_QA",
       "mode": "READ_ONLY_FROZEN_INPUT_SOURCE_ONLY_PUBLIC_SYNTHETIC_NO_GPU_NO_GOLD",
       "frozen_source_head": FROZEN,
       "input_git_blob_sha1": {"S8_V5_CONTRACT": EXPECTED_V5_BLOB, "S2_V6_CONTRACT": EXPECTED_V6_BLOB},
       "seed_cross_version": {"V5_expected": list(SEEDS), "V6_before": v6["AM03_stats"]["seeds"],
                              "candidate_after": out["AM03_stats"]["seeds"], "restored": True},
       "inherited_contracts_preserved": ["R2", "R4", "R5", "R6"],
       "source_changes": ["R1_TYPED_TEMPORAL_EVENT_SEMANTICS", "R1_MONOTONE_RETAIN",
                            "R1_CARRY_HOLDER_LOCATION", "R1_COMPLETE_SYNTHETIC_FIXTURES", "R3_RESTORE_LAST_SEED"],
       "actual_dataset_oracle_nonoverlap": "NOT_EXECUTED", "real_science": "HOLD",
       "independent_review": "NOT_EXECUTED_FOR_CANDIDATE", "owner_approval": "NOT_GRANTED"}
    return out, receipt


def mock_contract_test() -> bool:
    # Purely public schema stub. This tests patch application, NOT real V6 frozen bytes.
    source_v5 = {"AM03_stats": {"seed_values": list(SEEDS)}}
    slots = [{"id": id_, "preconditions": [], "effects": []} for id_ in (*IMMEDIATE, "WAIT")]
    source_v6 = {"AM03_stats": {"seeds": list(SEEDS[:-1]) + [20261131]},
                 "AM01_four_category_typed_action": {
                     "action_slot_contract": slots,
                     "typed_finite_domains": {"invariants": [], "state_fluents": []},
                     "synthetic_non_EVAL_category_fixtures": [], "QA": "NOT_EXECUTED"},
                 "AM02_parser": {"immutable": 2}, "AM04_categories": {"immutable": 4},
                 "AM05_audit_ledger_binding": {"immutable": 5}, "AM06_contrastive": {"immutable": 6},
                 "gates": {"SCIENCE": "HOLD", "TEST_Q1Q2": "SEALED", "GPU_CALLS": 0}}
    candidate, receipt = build_candidate(source_v5, source_v6)
    cs = {x["id"]: x for x in candidate["AM01_four_category_typed_action"]["action_slot_contract"]}
    return (candidate["AM03_stats"]["seeds"] == list(SEEDS)
            and cs["RETAIN"]["effects"][0][0] == "set_max"
            and cs["CARRY"]["effects"][2][0] == "forall_set"
            and cs["WAIT"]["effects"][1][0] == "atomic_advance"
            and all(candidate[k] == source_v6[k] for k in
                    ("AM02_parser", "AM04_categories", "AM05_audit_ledger_binding", "AM06_contrastive", "gates"))
            and receipt["real_science"] == "HOLD")


def write_json(path: Path, obj: dict):
    b = (json.dumps(obj, ensure_ascii=False, sort_keys=True, indent=2) + "\n").encode("utf-8")
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_bytes(b)
    return hashlib.sha256(b).hexdigest()


def main():
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--selftest", action="store_true", help="run only independent public synthetic state tests")
    ap.add_argument("--repo", type=Path, help="local Git repo root, read frozen source via git show")
    ap.add_argument("--out", type=Path, help="output directory; must reside inside repo when --repo provided")
    ns = ap.parse_args()
    if not ns.selftest and ns.repo is None:
        ap.error("Use --selftest OR --repo <root>")
    qa = run_qa()
    if qa["positive_pass"] != qa["positive_total"] or qa["negative_detected"] != qa["negative_total"]:
        raise SystemExit("HOLD_SYNTHETIC_QA_FAILED")
    out_dir = ns.out or ((ns.repo / "_tmp" / "TTM_D1_V6_R1_R3_CANDIDATE_20261114") if ns.repo else Path.cwd())
    if ns.repo:
        rp = ns.repo.resolve(strict=True)
        op = out_dir.resolve(strict=False)
        if op != rp and rp not in op.parents: raise SystemExit("HOLD_OUTPUT_OUTSIDE_PROJECT_ROOT")
        v5 = git_show(rp, V5, EXPECTED_V5_BLOB)
        v6 = git_show(rp, V6, EXPECTED_V6_BLOB)
        candidate, receipt = build_candidate(v5, v6)
        receipt["candidate_sha256"] = write_json(out_dir / "TTM_D1_BRIDGE_V6_R1_R3_PROSPECTIVE_CANDIDATE.json", candidate)
        receipt["source_status"] = "EXACT_FROZEN_INPUT_GIT_BLOBS_VERIFIED_FROM_LOCAL_REPO"
    else:
        receipt = {"source_status": "NOT_LOADED_SELFTEST_ONLY", "real_science": "HOLD"}
    receipt["synthetic_qa"] = qa
    recpath = out_dir / "TTM_D1_BRIDGE_V6_R1_R3_INTEGRATED_QA_RECEIPT.json"
    sha = write_json(recpath, receipt)
    print("SYNTHETIC_QA_PASS=%s/%s" % (qa["positive_pass"], qa["positive_total"]))
    print("NEGATIVE_QA_PASS=%s/%s" % (qa["negative_detected"], qa["negative_total"]))
    print("FINITE_VALID_TRANSITIONS=%d" % qa["finite_valid_transitions_exercised"])
    print("SOURCE_STATUS=" + receipt["source_status"])
    print("RECEIPT_SHA256=" + sha)
    print("DESIGN_VERDICT=HOLD_PENDING_DISTINCT_SOURCE_AND_REAL_SKELETON_QA")
    print("D1_BRIDGE_SCIENCE=HOLD TEST_Q1Q2=SEALED GPU=0")

if __name__ == "__main__": main()
