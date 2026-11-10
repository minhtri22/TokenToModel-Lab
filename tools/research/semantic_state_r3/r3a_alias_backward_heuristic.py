#!/usr/bin/env python3
"""R3A independent shallow reverse-regex baseline (Python 3.12).

Prediction uses ONLY story/question. No state simulation, precondition checks,
source_events, family/split labels, or oracle answers in predict().

The separately recorded 384/384 result was executed in JS against GitHub's
pinned JSONs on 2026-11-11. This Python port requires a local full replay;
do NOT label it Python PASS until the command actually executes.
"""
from __future__ import annotations
import argparse
from collections import defaultdict
import hashlib
import json
from pathlib import Path
import re
import subprocess
import sys

COMMIT = '81327724c08771682622bebb8648fefd55a4fa9a'
MODEL_PATH = 'artifacts/qa/ttm-r3-structural-design/r3a/R3A_MODEL_INPUT_ONLY.json'
ORACLE_PATH = 'artifacts/qa/ttm-r3-structural-design/r3a/R3A_PUBLIC_ORACLE.json'
MODEL_SHA256 = '2510866d82641bd27207082566d6b4dbb867e59516794e422dff8fb041646402'
ORACLE_SHA256 = 'b509fae3f63399c978d532c2686d147bd4ba41e44b2aa9135dcd38360e6ffb08'
ALIAS = re.compile(r'^The alias (\w+) names (\w+)\.$')
HOLDER_Q = re.compile(r'^Who holds (\w+)\?$')
GOAL_Q = re.compile(r'^What is (\w+) goal\?$')
PASS = re.compile(r'^\w+ passes (\w+) to (\w+)\.$')
INIT = re.compile(r'^(\w+) starts with (\w+)\.$')
CHANGE = re.compile(r'^(\w+) changes goal from \w+ to (\w+)\.$')
CANCEL = re.compile(r'^(\w+) cancels goal \w+\.$')
DELEGATE = re.compile(r'^(\w+) delegates goal (\w+) to (\w+)\.$')
SET = re.compile(r'^(\w+) begins goal (\w+)\.$')


def predict(row: dict[str, str]) -> str | None:
    lines = row['story'].split('\n')
    aliases = {}
    for line in lines:
        if m := ALIAS.fullmatch(line):
            aliases[m[1]] = m[2]

    def resolve(person: str) -> str:
        return aliases.get(person, person)

    if m := HOLDER_Q.fullmatch(row['question']):
        item = m[1]
        for line in reversed(lines):
            if (x := PASS.fullmatch(line)) and x[1] == item:
                return resolve(x[2])
            if (x := INIT.fullmatch(line)) and x[1] == item:
                return resolve(x[2])
        return None

    if m := GOAL_Q.fullmatch(row['question']):
        target = resolve(m[1])
        for line in reversed(lines):
            if (x := CHANGE.fullmatch(line)) and resolve(x[1]) == target:
                return x[2]
            if (x := CANCEL.fullmatch(line)) and resolve(x[1]) == target:
                return 'NONE'
            if x := DELEGATE.fullmatch(line):
                if resolve(x[3]) == target:
                    return x[2]
                if resolve(x[1]) == target:
                    return 'NONE'
            if (x := SET.fullmatch(line)) and resolve(x[1]) == target:
                return x[2]
        return 'NONE'
    return None


def pinned(raw: bytes, sha: str, name: str) -> dict:
    actual = hashlib.sha256(raw).hexdigest()
    if actual != sha:
        raise SystemExit(f'SOURCE_PIN_FAIL_{name}: {actual} != {sha}')
    return json.loads(raw)


def git_bytes(root: Path, path: str) -> bytes:
    result = subprocess.run(['git', '-C', str(root), 'show', f'{COMMIT}:{path}'], capture_output=True)
    if result.returncode:
        raise SystemExit(f'PINNED_COMMIT_NOT_AVAILABLE_OR_GIT_ERROR: {path}: '
                         + result.stderr.decode('utf-8', errors='replace'))
    return result.stdout


def assess(model: dict, oracle: dict) -> dict:
    if model.get('schema') != 'ttm.r3a.model_input_only.v1':
        raise SystemExit('MODEL_SCHEMA_FAIL')
    if len(model.get('records', [])) != 384 or len(oracle.get('groups', [])) != 96:
        raise SystemExit('UNEXPECTED_CORPUS_SIZE')
    if not (oracle.get('labels_public') is True and oracle.get('sealed_final') is False):
        raise SystemExit('ORACLE_PUBLIC_TOY_STATUS_MISMATCH')
    # Oracle is for scoring ONLY: it is not passed to predict().
    mapping = {}
    for group in oracle['groups']:
        for cell in group['cells']:
            k = (cell['story'], cell['question'])
            if k in mapping:
                raise SystemExit('DUPLICATE_ORACLE_PROJECTION')
            mapping[k] = (cell['answer'], group['family'], group['split'], cell['cell'])
    if len(mapping) != 384:
        raise SystemExit('BAD_ORACLE_PROJECTION_COUNT')
    by = defaultdict(lambda: {'correct': 0, 'total': 0})
    misses = []
    seen = set()
    for idx, row in enumerate(model['records']):
        if set(row) != {'story', 'question'}:
            raise SystemExit('MODEL_INPUT_FIELD_LEAK')
        key = (row['story'], row['question'])
        if key in seen or key not in mapping:
            raise SystemExit('MODEL_DUPLICATE_OR_UNMAPPED_ROW')
        seen.add(key)
        prediction = predict(row)
        answer, family, split, cell = mapping[key]
        bucket = by[f'{family}_{split}']
        bucket['total'] += 1
        bucket['correct'] += int(prediction == answer)
        if prediction != answer:
            misses.append({'row': idx, 'family': family, 'split': split,
                           'cell': cell, 'pred': prediction, 'answer': answer})
    if len(seen) != len(mapping):
        raise SystemExit('MISSING_MODEL_PROJECTION')
    return {
        'status': 'SHALLOW_HEURISTIC_384_384' if not misses else 'SHALLOW_HEURISTIC_PARTIAL',
        'review_type': 'INDEPENDENT_PYTHON_REPLAY_OF_JS_PREDICTOR',
        'pinned_commit': COMMIT, 'total': len(seen), 'correct': len(seen) - len(misses),
        'by_family_split': dict(sorted(by.items())), 'errors': misses[:10],
        'oracle_use': 'SCORING_ONLY_AFTER_PREDICTION',
        'uses_state_simulation': False, 'precondition_validation': False,
        'scientific_scope': 'PUBLIC_TOY_ONLY_NOT_BLINDED_FINAL'
    }


def smoke():
    cases = [
        ({'story': 'The alias Cloud names Hoa.\nbook starts with Minh.\nMinh passes book to Cloud.',
          'question': 'Who holds book?'}, 'Hoa'),
        ({'story': 'Lan begins goal read.\nLan delegates goal read to Minh.',
          'question': 'What is Minh goal?'}, 'read'),
        ({'story': 'Lan begins goal read.\nLan cancels goal read.',
          'question': 'What is Minh goal?'}, 'NONE'),
        ({'story': 'Minh begins goal plant.\nMinh changes goal from plant to repair.',
          'question': 'What is Minh goal?'}, 'repair'),
    ]
    for row, expected in cases:
        actual = predict(row)
        if actual != expected:
            raise SystemExit(f'SMOKE_FAIL: {actual} != {expected}')
    print('SMOKE_4_OF_4_PASS (not a full-corpus replay)')


def main():
    p = argparse.ArgumentParser()
    src = p.add_mutually_exclusive_group(required=False)
    src.add_argument('--repo-root', type=Path, help='local Git repo containing pinned commit')
    src.add_argument('--model', type=Path, help='model JSON (requires --oracle)')
    p.add_argument('--oracle', type=Path)
    p.add_argument('--out', type=Path, help='JSON receipt (default stdout only)')
    p.add_argument('--self-test', action='store_true')
    a = p.parse_args()
    if a.self_test:
        smoke()
        if a.repo_root is None and a.model is None:
            return
    if a.repo_root is None and a.model is None:
        p.error("--repo-root or --model is required unless --self-test is used")
    if a.repo_root is not None:
        if a.oracle is not None:
            p.error('--oracle may not be used with --repo-root')
        model_bytes = git_bytes(a.repo_root, MODEL_PATH)
        oracle_bytes = git_bytes(a.repo_root, ORACLE_PATH)
    else:
        if a.oracle is None:
            p.error('--oracle is required with --model')
        model_bytes = a.model.read_bytes()
        oracle_bytes = a.oracle.read_bytes()
    model = pinned(model_bytes, MODEL_SHA256, 'MODEL')
    oracle = pinned(oracle_bytes, ORACLE_SHA256, 'ORACLE')
    report = assess(model, oracle)
    report['source_sha256'] = {'model': MODEL_SHA256, 'oracle': ORACLE_SHA256}
    payload = json.dumps(report, ensure_ascii=False, indent=2, sort_keys=True) + '\n'
    if a.out:
        if a.out.exists():
            raise SystemExit('NO_OVERWRITE')
        # No implicit directories, accidental file creation, or repository writes.
        a.out.write_text(payload, encoding='utf-8')
    print(payload)
    if report['correct'] != 384:
        raise SystemExit(1)


if __name__ == '__main__':
    main()
