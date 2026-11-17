#!/usr/bin/env python3
"""Separate implementation of oracle/partition checks on MOCK fixtures ONLY.

Author-created cross-check, NOT an independent human/organizational reviewer.
Does NOT touch checkpoint, model, real tokenizer, original TEST, or FINAL24.
"""
from __future__ import annotations
import hashlib
import json
from collections import Counter
from pathlib import Path
import subprocess
import sys

import ttm_sm4m_diag_q001 as D


def check() -> dict:
    checks = {}
    allowed = list(range(100, 300))
    rows = D.fixture_generator(allowed)
    by_group = {g: [r for r in rows if r['group'] == g] for g in D.GROUPS}
    q_train = by_group['TRAIN']
    no_answer = by_group['HELDOUT_ABSENT'][0]['gold']
    roles = set([rows[0]['context'][0], rows[0]['context'][6], rows[0]['context'][8], no_answer])
    checks['count_exact_80'] = len(rows) == 80
    checks['groups_exact'] = dict(Counter(r['group'] for r in rows)) == D.GROUPS
    checks['one_token_next_position'] = all(len(r['context']) == 9 and r['gold'] != r['context'][-1] for r in rows)
    checks['oracle_recomputed_independently'] = all(
        (r['context'][2] if r['context'][7] == r['context'][1] else r['context'][5]
         if r['context'][7] == r['context'][4] else no_answer) == r['gold']
        for r in rows)
    checks['train_16_binding_8_absent'] = sum(r['gold'] != no_answer for r in q_train) == 16
    checks['train_8_first_8_second'] = sum(r['context'][7] == r['context'][1] for r in q_train) == 8 and sum(r['context'][7] == r['context'][4] for r in q_train) == 8
    checks['absent_key_is_absent'] = all(r['context'][7] not in (r['context'][1],r['context'][4]) for r in by_group['HELDOUT_ABSENT'])
    checks['all_binding_ids_disjoint_from_roles'] = all(
        not ({r['context'][1],r['context'][2],r['context'][4],r['context'][5]} & roles) for r in rows)
    checks['all_unique_contexts'] = len({tuple(r['context']) for r in rows}) == len(rows)
    train_content = {t for r in q_train for i,t in enumerate(r['context']) if i in (1,2,4,5,7)}
    checks['heldout_recomb_seen_symbol_set'] = all(
        r['context'][i] in train_content for r in by_group['HELDOUT_RECOMBINED'] for i in (1,2,4,5,7))
    checks['heldout_novel_unseen_symbol_set'] = all(
        r['context'][i] not in train_content for r in by_group['HELDOUT_NOVEL_IDS'] for i in (1,2,4,5,7))
    original = {r['id']: r for r in q_train}
    checks['counterfactual_swaps_change_gold'] = all(
        r['parent'] in original and
        r['context'][1] == original[r['parent']]['context'][1] and
        r['context'][4] == original[r['parent']]['context'][4] and
        r['context'][7] == original[r['parent']]['context'][7] and
        r['context'][2] == original[r['parent']]['context'][5] and
        r['context'][5] == original[r['parent']]['context'][2] and
        r['gold'] != original[r['parent']]['gold']
        for r in by_group['PAIRED_COUNTERFACTUAL'])
    checks['candidate_four_fixed_unique'] = all(len(r['choices']) == len(set(r['choices'])) == 4 and r['gold'] in r['choices'] for r in rows)
    checks['constant_no_answer_fails_bound'] = sum(r['gold'] != no_answer for r in rows) >= 40
    checks['last_binding_value_antioracle_fails'] = sum(r['gold'] != r['context'][5] for r in rows) >= 16
    checks['source_determinism'] = hashlib.sha256(D.json_bytes(rows)).digest() == hashlib.sha256(D.json_bytes(D.fixture_generator(allowed))).digest()
    for label, alter in [
        ('reject_duplicate', lambda x: x.__setitem__('context', rows[1]['context'])),
        ('reject_gold_tamper', lambda x: x.__setitem__('gold', -10)),
        ('reject_bad_length', lambda x: x.__setitem__('context', [1,2,3])),
    ]:
        mut = [{**r,'context':list(r['context']),'choices':list(r['choices'])} for r in rows]
        alter(mut[0]); bad = False
        try: D.validate_fixture(mut, no_answer)
        except RuntimeError: bad=True
        checks[label] = bad
    cmd=[sys.executable, str(Path(D.__file__).resolve()),'run']
    proc=subprocess.run(cmd,capture_output=True,text=True,timeout=10)
    checks['execution_without_permit_denied'] = proc.returncode == 2 and 'HOLD_MISSING_REQUIRED_RUN_FLAGS' in proc.stderr
    fixture_cmd=[sys.executable, str(Path(D.__file__).resolve()),'fixture-freeze']
    proc=subprocess.run(fixture_cmd,capture_output=True,text=True,timeout=10)
    checks['fixture_freeze_without_permit_denied'] = proc.returncode == 2 and 'HOLD_MISSING_FIXTURE_FREEZE_ARGUMENTS' in proc.stderr
    result={'scope':'MOCK_SOURCE_AND_ORACLE_QA_NOT_MODEL_RUN','checks':checks,
            'pass':sum(checks.values()),'total':len(checks),
            'model_executed':False,'checkpoint_read':False,'private_token_inventory_read':False,
            'independence':'SEPARATE_CHECKER_CODE_SAME_ASSISTANT_AUTHOR_NOT_DISTINCT_EXTERNAL_REVIEW'}
    return result

if __name__=='__main__':
    r=check()
    print(json.dumps(r,sort_keys=True))
    sys.exit(0 if r['pass']==r['total'] else 3)
