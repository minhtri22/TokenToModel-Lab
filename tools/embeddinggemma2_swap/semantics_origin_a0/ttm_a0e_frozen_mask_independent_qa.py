#!/usr/bin/env python3
"""Read-only independent score-blind A0E mask checker; no labels or model calls."""
import argparse
import hashlib
import io
import json
import zipfile
from pathlib import Path

import networkx as nx

ZIP_SHA = '5680a2e8b39b04eba85629a0851c50f3da18387305221bdfa4a2aa2ab3b7c710'
FULL_SHA = '8ba5b07bea73cfc6784de940378d5726be9cc8dab2ecc32daa4a5a3555bf91b1'
CORE_SHA = 'b280478feb9f7359c261944e5c54c7808c96e05bd14558657044fe6f35a2ee2c'
EXPECTED = {'README_PRIVATE_MASK.txt', 'fresh138_pairs_private.tsv',
            'fresh37_maxmatching_core_private.tsv', 'A0E_LEXICAL_STATIC_COVERAGE_RECEIPT_PUBLIC.json'}


def pinned(ok, code):
    if not ok:
        raise RuntimeError('A0E_HOLD_' + code)


def read_pairs(data, count):
    pinned(data.endswith(b'\n'), 'NO_FINAL_LF')
    lines = data.decode('ascii').splitlines()
    pairs = [tuple(s.split('\t')) for s in lines]
    pinned(len(pairs) == count and len(set(pairs)) == count, 'COUNT_OR_DUPLICATES')
    pinned(all(len(a) == 2 and all(w.isascii() and w.isalpha() and w.islower() for w in a) for a in pairs), 'FORMAT')
    pinned(pairs == sorted(pairs), 'NON_CANONICAL_ORDER')
    return pairs


def run(archive):
    data = Path(archive).read_bytes()
    pinned(hashlib.sha256(data).hexdigest() == ZIP_SHA, 'ARCHIVE_SHA')
    with zipfile.ZipFile(io.BytesIO(data)) as z:
        pinned(set(z.namelist()) == EXPECTED and len(z.namelist()) == len(EXPECTED), 'ARCHIVE_MEMBERS')
        full_bytes = z.read('fresh138_pairs_private.tsv')
        core_bytes = z.read('fresh37_maxmatching_core_private.tsv')
        receipt = json.loads(z.read('A0E_LEXICAL_STATIC_COVERAGE_RECEIPT_PUBLIC.json'))
    pinned(hashlib.sha256(full_bytes).hexdigest() == FULL_SHA, 'FULL_MASK_SHA')
    pinned(hashlib.sha256(core_bytes).hexdigest() == CORE_SHA, 'CORE_MASK_SHA')
    full = read_pairs(full_bytes, 138)
    core = read_pairs(core_bytes, 37)
    pinned(set(core).issubset(set(full)), 'CORE_NOT_SUBSET')
    pinned(len(set(w for a in core for w in a)) == 74, 'CORE_SHARED_WORD')
    graph = nx.Graph()
    for a, b in full:
        tag = 'TTM_GEMMA2_A0E_LEXICAL_V1|' + a + '\t' + b
        weight = int(hashlib.sha256(tag.encode('ascii')).hexdigest()[:14], 16)
        graph.add_edge(a, b, weight=weight)
    selected = {frozenset(e) for e in nx.max_weight_matching(graph, maxcardinality=True)}
    pinned(selected == {frozenset(e) for e in core}, 'MAXIMUM_MATCH_DIFFERENCE')
    pinned(graph.number_of_nodes() == 78 and graph.number_of_edges() == 138, 'GRAPH_TOPOLOGY')
    pinned(sorted((len(comp) for comp in nx.connected_components(graph)), reverse=True) == [76, 2], 'COMPONENTS')
    pinned(receipt['private_commitments']['full_roster_pair_file_sha256'] == FULL_SHA, 'RECEIPT_FULL')
    pinned(receipt['private_commitments']['word_disjoint_core_file_sha256'] == CORE_SHA, 'RECEIPT_CORE')
    pinned(receipt['counts']['remaining_after_excluding_all_SimLex_and_WordSim_words'] == 138, 'RECEIPT_COUNT')
    return {
        'schema': 'ttm.gemma2.a0e.frozen_mask_independent_qa.v1',
        'status': 'PASS_FROZEN_MASK_HASH_AND_GRAPH_12_GATES',
        'source': 'SCORE_BLIND_PAIR_MASK_ONLY',
        'full_mask_sha256': FULL_SHA, 'core_sha256': CORE_SHA,
        'full_pairs': 138, 'full_word_types': 78,
        'word_disjoint_core_pairs': 37, 'core_word_types': 74,
        'components': [76, 2], 'networkx': nx.__version__,
        'human_gold_ratings_read': False, 'LM_forward': False,
        'training': False, 'gpu': False, 'T4_admitted': False,
    }


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--archive', required=True)
    args = parser.parse_args()
    try:
        print(json.dumps(run(args.archive), sort_keys=True))
    except Exception as e:
        print(json.dumps({'status': 'HOLD_FAIL_CLOSED', 'error': str(e), 'LM_forward': False, 'training': False}))
        raise SystemExit(2)
