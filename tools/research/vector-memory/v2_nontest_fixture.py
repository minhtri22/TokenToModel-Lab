#!/usr/bin/env python3
"""Generate one fresh synthetic NONTEST 192-case Vector Memory v2 fixture.

Source / schema only. No old probe access, no trained model, no TEST,
no inference. A separate science scorer must be approved before results exist.
"""
from __future__ import annotations
import argparse
import hashlib
import json
from pathlib import Path

VERSION = 'ttm.vm.v2.nontest192.id_alias_description.v1'
SEED = 'TTM_VM_V2_FRESH192_S0S1S2_20261112_PREREG_A1'
STRATA = ('S0_ID_LITERAL', 'S1_ALIAS_LOOKUP', 'S2_DESC_PARAPHRASE')
N_PER_STRATUM = 64
BANK = 32
ALPHABET = 'bcdfghjklmnpqrstvwxz'
LABELS = ('bivor', 'caxen', 'doral', 'fekum', 'gilen', 'havor', 'jekin', 'kofur',
          'lamet', 'mipor', 'navek', 'pizol', 'raqum', 'sivel', 'tobak', 'wexil')
# Closed-vocabulary attributes. Their synonyms are openly declared; a match
# under this dictionary is controlled matching, not a general semantics claim.
VOCAB = {
    'color': (
        ('amber', 'golden'), ('azure', 'blue'), ('crimson', 'red'),
        ('indigo', 'violet'), ('ivory', 'cream'), ('silver', 'gray'),
        ('copper', 'russet'), ('jade', 'green'), ('ochre', 'yellow'),
        ('pearl', 'white'), ('sable', 'black'), ('coral', 'salmon')),
    'shape': (
        ('round', 'circular'), ('square', 'quadrate'), ('triangular', 'three-sided'),
        ('spiral', 'coiled'), ('oval', 'elliptical'), ('rectangular', 'oblong'),
        ('conical', 'cone-shaped'), ('cubic', 'boxlike'), ('hexagonal', 'six-sided'),
        ('arched', 'curved'), ('tubular', 'pipe-shaped'), ('ridged', 'grooved')),
    'material': (
        ('ceramic', 'clay'), ('granite', 'stone'), ('cotton', 'fabric'),
        ('leather', 'hide'), ('timber', 'wood'), ('glass', 'crystal'),
        ('rubber', 'elastic'), ('bronze', 'metal'), ('paper', 'pulp'),
        ('linen', 'flax'), ('marble', 'limestone'), ('slate', 'shale')),
}
ATTRS = ('color', 'shape', 'material')


def digest(*parts: object) -> bytes:
    h = hashlib.sha256()
    h.update((SEED + '|' + '|'.join(map(str, parts))).encode('ascii'))
    return h.digest()


def random_int(limit: int, *parts: object) -> int:
    return int.from_bytes(digest(*parts)[:8], 'big') % limit


def object_key(stratum: str, case_index: int, slot: int) -> str:
    # 'a' cannot occur in any old 12-consonant obj key namespace;
    # disjoint by construction without reading former TRAIN/DEV/PROBE/TEST.
    b = digest('fresh-object-key', stratum, case_index, slot)
    return 'obja' + ''.join(ALPHABET[v % len(ALPHABET)] for v in b[:11])


def alias_key(stratum: str, case_index: int, slot: int) -> str:
    b = digest('fresh-alias', stratum, case_index, slot)
    return 'aka' + ''.join(ALPHABET[v % len(ALPHABET)] for v in b[:11])


def triple(stratum: str, case_index: int, slot: int) -> tuple[int, int, int]:
    return tuple(random_int(len(VOCAB[a]), 'triple', stratum, case_index, slot, a) for a in ATTRS)


def new_case(stratum: str, i: int) -> dict:
    if stratum not in STRATA or not (0 <= i < N_PER_STRATUM):
        raise ValueError('INVALID_STRATUM_INDEX')
    target = triple(stratum, i, 0)
    triples = [target]
    # Exactly four hard negatives: two attributes agree, one changes.
    # Use a deterministic repeated axis to cover all three attributes.
    for j, axis in enumerate((0, 1, 2, 0)):
        t = list(target)
        t[axis] = (t[axis] + 1 + j) % len(VOCAB[ATTRS[axis]])
        candidate = tuple(t)
        if candidate in triples:
            raise AssertionError('HARD_NEGATIVE_COLLISION')
        triples.append(candidate)
    slot = 1
    while len(triples) < BANK:
        candidate = triple(stratum, i, slot)
        slot += 1
        if candidate in triples:
            continue
        if sum(a == b for a, b in zip(candidate, target)) > 1:
            continue
        triples.append(candidate)
        if slot > 10000:
            raise RuntimeError('DISTRACTOR_GENERATION_BOUND_EXCEEDED')
    keys = [object_key(stratum, i, j) for j in range(BANK)]
    aliases = [alias_key(stratum, i, j) for j in range(BANK)]
    if len(set(keys)) != BANK or len(set(aliases)) != BANK:
        raise AssertionError('KEY_COLLISION')
    # Deterministic independent balanced answer labels, not based on attributes.
    # The 64 labels are permuted across four copies of the 16 labels.
    permutation = sorted(range(64), key=lambda j: (digest('label-permutation', stratum, j), j))
    answer_slot = permutation.index(i) % len(LABELS)
    answer = LABELS[answer_slot]
    values = [answer]
    for j in range(1, BANK):
        values.append(LABELS[(answer_slot + 1 + (j * 7) % 15) % len(LABELS)])
        if values[-1] == answer:
            raise AssertionError('GOLD_VALUE_LEAK')

    def description(t: tuple[int, int, int]) -> str:
        return ('archive item color ' + VOCAB['color'][t[0]][0] +
                '; shape ' + VOCAB['shape'][t[1]][0] +
                '; material ' + VOCAB['material'][t[2]][0])

    order = sorted(range(BANK), key=lambda j: (digest('card-order', stratum, i, j), j))
    cards = [{'key': keys[j], 'lookup_alias': aliases[j],
              'retrieval_text': description(triples[j]), 'value': values[j]}
             for j in order]
    wrong = [dict(card) for card in cards]
    for card in wrong:
        if card['key'] == keys[0]:
            card['value'] = LABELS[(answer_slot + 1) % len(LABELS)]

    if stratum == 'S0_ID_LITERAL':
        question = 'For archive object ' + keys[0] + ', what access tag was recorded? Answer:'
    elif stratum == 'S1_ALIAS_LOOKUP':
        question = 'What is the access tag for public alias ' + aliases[0] + '? Answer:'
    else:
        color, shape, material = (VOCAB[a][v][1] for a, v in zip(ATTRS, target))
        question = ('What access tag belongs to the ' + color + ' ' + shape +
                    ' ' + material + ' archive item? Answer:')
    if answer in question:
        raise AssertionError('ANSWER_IN_QUESTION')
    return {'schema': VERSION, 'split': 'non_test_probe_v2',
            'case_id': f'vm2-{stratum}-{i:04d}', 'stratum': stratum,
            'question': question, 'answer': answer, 'target_key': keys[0],
            'correct_memory': cards, 'wrong_memory': wrong, 'none_memory': [],
            'answer_only_scoring': True}


def build() -> list[dict]:
    cases = [new_case(stratum, i) for stratum in STRATA for i in range(N_PER_STRATUM)]
    keys = [card['key'] for case in cases for card in case['correct_memory']]
    aliases = [card['lookup_alias'] for case in cases for card in case['correct_memory']]
    if len(set(keys)) != 192 * BANK or len(set(aliases)) != 192 * BANK:
        raise AssertionError('NONTEST_GLOBAL_COLLISION')
    return cases


def serialized(cases: list[dict]) -> bytes:
    return (json.dumps({'schema': VERSION, 'split': 'non_test_probe_v2',
                        'cases': cases}, sort_keys=True, separators=(',', ':')) + '\n').encode('utf-8')


def main() -> None:
    p = argparse.ArgumentParser()
    p.add_argument('--project-root', type=Path, required=True)
    p.add_argument('--out', type=Path, required=True)
    p.add_argument('--write-once', action='store_true')
    args = p.parse_args()
    if not args.write_once:
        raise SystemExit('DENY_NO_EXPLICIT_FIXTURE_WRITE')
    root = args.project_root.resolve(strict=True)
    out = args.out.resolve()
    if not out.is_relative_to(root):
        raise SystemExit('DENY_OUTPUT_OUTSIDE_PROJECT_ROOT')
    if out.exists():
        raise SystemExit('DENY_FIXTURE_OVERWRITE')
    blob = serialized(build())
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_bytes(blob)
    print(json.dumps({'status':'FIXTURE_ONLY_NO_MODEL_EXECUTION','stories':192,
                      'banksize':BANK,'sha256':hashlib.sha256(blob).hexdigest(),
                      'test_opened':False,'training':False,'inference':False},sort_keys=True))

if __name__ == '__main__':
    main()
