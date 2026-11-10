#!/usr/bin/env python3
"""R2A author-side adversarial proxy audit; separate from generator and checker.

Scans exact public artifacts only. A 100% key-aware last update is still
trivial recency retrieval, NOT proof of learned semantic state or neural gain.
No model checkpoint, training, corpus or GPU is used.
"""
from __future__ import annotations
import argparse
from collections import Counter, defaultdict
import hashlib
import json
from pathlib import Path
import re


def top_level_qa(oracle, model):
    pairs, probes = oracle['pairs'], oracle['probes']
    ins = model['records']
    assert len(pairs) == 256 and len(probes) == 128 and len(ins) == 384
    assert all(set(x) == {'story', 'question'} for x in ins)
    assert [{'story': r['story'], 'question': r['question']} for r in pairs + probes] == ins
    return pairs, probes


def parse_visible_event(line):
    """Extract final value for a visible statement without asking which key matters."""
    pats = [
        r'^The ([a-z]+) belongs to ([A-Z][a-z]+)\.$',
        r'^([A-Z][a-z]+) has the ([a-z]+) now\.$',
        r'^([A-Z][a-z]+) plans to ([a-z ]+)\.$',
        r'^([A-Z][a-z]+) intends to ([a-z ]+)\.$',
    ]
    for i, p in enumerate(pats):
        m = re.fullmatch(p, line)
        if m:
            a, b = m.groups()
            if i == 0: return a, b
            if i == 1: return b, a
            return a, b
    raise AssertionError('UNRECOGNIZED_VISIBLE_SENTENCE')


def extract_query_key(question):
    pats = [r'^Who owns the ([a-z]+)\?$', r'^Who has the ([a-z]+) now\?$',
            r'^What does ([A-Z][a-z]+) plan to do\?$',
            r'^Which goal does ([A-Z][a-z]+) intend to pursue\?$']
    for p in pats:
        m = re.fullmatch(p, question)
        if m: return m.group(1)
    raise AssertionError('UNRECOGNIZED_QUESTION')


def analyze(oracle, model):
    pairs, probes = top_level_qa(oracle, model)
    positional = {f'sentence_{i+1}': 0 for i in range(4)}
    positional['first_in_query_key'] = 0
    positional['last_in_query_key'] = 0
    positional['first_in_story'] = 0
    seen = defaultdict(dict)
    for r in pairs:
        items = [parse_visible_event(x) for x in r['story'].split('\n')]
        assert len(items) == 4
        key = extract_query_key(r['question'])
        relevant = [value for k, value in items if k == key]
        assert len(relevant) == 2
        for i, (k, v) in enumerate(items):
            positional[f'sentence_{i+1}'] += int(v == r['answer'])
        positional['first_in_query_key'] += int(relevant[0] == r['answer'])
        positional['last_in_query_key'] += int(relevant[-1] == r['answer'])
        positional['first_in_story'] += int(items[0][1] == r['answer'])
        seen[r['pair_id']][r['variant']] = r
    assert len(seen) == 128 and all(set(x) == {'A', 'B'} for x in seen.values())
    questionless_bound = 0
    bag_bound = 0
    for ident, pair in seen.items():
        a, b = pair['A'], pair['B']
        assert a['answer'] != b['answer']
        assert a['question'] == b['question']
        assert Counter(re.findall(r'[a-z]+', a['story'].lower())) == Counter(re.findall(r'[a-z]+', b['story'].lower()))
        bag_bound += 1
        pa = next(x for x in probes if x['pair_id'] == ident)
        assert pa['story'] == a['story']
        assert pa['question'] != a['question']
        assert pa['answer'] != a['answer']
        questionless_bound += 1
    assert positional['last_in_query_key'] == 256
    assert max(positional[f'sentence_{i+1}'] for i in range(4)) < 256
    assert bag_bound == 128 and questionless_bound == 128
    return {
        'status': 'PASS_SCOPED_AUTHOR_AUDIT_NOT_CODEX',
        'model_input_records': 384,
        'counterfactual_records': 256,
        'query_swap_probes': 128,
        'positional_value_only_correct_of_256': positional,
        'bag_only_best_possible_paired_correct': 128,
        'no_question_best_possible_query_swap_correct': 128,
        'mechanical_key_aware_last_update_correct_of_256': 256,
        'limitations': [
            'The trivial key-aware recency algorithm solves R2A without persistent latent state.',
            'The public oracle dataset permits exact input-to-label lookup and cannot be a blinded heldout set.',
            'Only author-side visible-text audit; no Codex reviewer actually executed.',
            'No neural model tested; no extrapolation to unseen event transition types.',
        ],
        'scientific_disposition': 'O1_DEFER_KEEP_O0_HOLD; REQUIRE_CODEX_ADVERSARIAL_REVIEW',
    }


def main():
    p = argparse.ArgumentParser()
    p.add_argument('--oracle', required=True)
    p.add_argument('--model-input', required=True)
    p.add_argument('--out', required=True)
    a = p.parse_args()
    target = Path(a.out)
    if target.exists(): raise SystemExit('REFUSE_OVERWRITE')
    ob, ib = Path(a.oracle).read_bytes(), Path(a.model_input).read_bytes()
    result = analyze(json.loads(ob), json.loads(ib))
    result['oracle_sha256'] = hashlib.sha256(ob).hexdigest()
    result['model_input_sha256'] = hashlib.sha256(ib).hexdigest()
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_bytes((json.dumps(result, ensure_ascii=False, indent=2, sort_keys=True) + '\n').encode())
    print(json.dumps(result, ensure_ascii=False, sort_keys=True))

if __name__ == '__main__': main()
