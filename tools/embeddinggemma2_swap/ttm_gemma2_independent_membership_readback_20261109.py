#!/usr/bin/env python3
"""Read-only independent audit of pinned NEW_HOLDOUT membership and public receipt.

Never reads TEST raw stories, checkpoint tensors, model inference or GPU. Never
prints private story IDs. Uses only Python standard library.
"""
from __future__ import annotations
import argparse
import hashlib
import json
import os
from pathlib import Path

PRIVATE_SHA = 'bedc3671256a66f605fbeb9f98bbd27149b456019d3d8bc5bbc89ebca6d09b47'
RAW_SHA = {
    'TinyStories-train.txt': 'c5cf5e22ff13614e830afbe61a99fbcbe8bcb7dd72252b989fa1117a368d401f',
    'TinyStories-valid.txt': '94e431816c4cce81ff71e4408ff8d3bda9a42e8d2663986697c3954288cb38b4',
}
SPLIT_SHA = '9f2ebaca821bddf0a9d7ae30ccfcef34561b968b21159aa913794298235a2fa9'
BPE_SHA = 'cba18e60cee3d08a353ee6d4a451017289e45af7b4b1179c87171b9b78d7dfdc'
DOMAIN = 'TTM_GEMMA2_2048_NEW_HOLDOUT_V1|'
OLD_TEST_BUCKET_DOMAIN = b'TTM_SMALL4M_20261108_STORY_HASH_V1|'
WORKSPACE = 'D:\\WORK\\RESEARCH\\TokenToModel-Lab'


def require(condition: bool, code: str) -> None:
    if not condition:
        raise RuntimeError('HOLD_' + code)


def digest(raw: bytes) -> str:
    return hashlib.sha256(raw).hexdigest()


def hex_id(x) -> bool:
    return isinstance(x, str) and len(x) == 64 and all(ch in '0123456789abcdef' for ch in x)


def audit(public: dict, private: dict, private_raw: bytes, old_split: dict, *, exact_sha: bool = True) -> dict:
    require(public.get('schema') == 'ttm.gemma2.new_holdout.seal_receipt.v1', 'PUBLIC_SCHEMA')
    require(public.get('status') == 'MEMBERSHIP_SEALED_NOT_EVALUATED', 'PUBLIC_STATUS')
    require(public.get('membership_private_sha256') == PRIVATE_SHA, 'PUBLIC_SHA_PIN')
    if exact_sha:
        require(digest(private_raw) == PRIVATE_SHA, 'PRIVATE_BYTES_SHA_MISMATCH')
    require(private.get('schema') == 'ttm.gemma2.new_holdout.private_membership.v1', 'PRIVATE_SCHEMA')
    require(private.get('source_raw_sha256') == RAW_SHA == public.get('source_sha256'), 'SOURCE_ORIGIN')
    require(private.get('prior_split_sha256') == SPLIT_SHA == public.get('split_sha256'), 'SPLIT_ORIGIN')
    require(private.get('bpe_file_sha256') == BPE_SHA == public.get('bpe_file_sha256'), 'TOKENIZER_PIN')
    require(private.get('selection_domain') == DOMAIN, 'SELECTION_DOMAIN')
    require(private.get('whole_train_stories_scanned') == public.get('whole_train_stories_scanned') == 2119489, 'FULL_TRAIN_STORY_SCAN')
    require(private.get('n_candidates') == 640, 'POOL_SIZE')
    ids = private.get('story_sha256_ordered')
    targets = private.get('target_counts_per_story')
    require(isinstance(ids, list) and len(ids) == 320 and all(hex_id(s) for s in ids), 'STORY_IDS')
    require(len(set(ids)) == len(ids), 'DUPLICATE_ID')
    require(isinstance(targets, list) and len(targets) == 320 and all(type(n) is int and n > 0 for n in targets), 'TARGETS_PER_STORY')
    require(sum(targets) == private.get('total_target_count') == public.get('target_count') == 75798, 'TARGET_COUNT')
    require(public.get('story_count') == 320, 'PUBLIC_STORY_COUNT')
    require(private.get('full_train_near_jaccard_threshold') == 0.85, 'NEAR_THRESHOLD')
    require(private.get('n_candidates_rejected_near_full_train') == public.get('rejected_near_full_train') == 0, 'NEAR_TRAIN_RECEIPT')
    require(private.get('n_candidates_rejected_within_new') == public.get('rejected_near_internal') == 0, 'NEAR_INTERNAL_RECEIPT')
    require(isinstance(private.get('exclusions'), dict), 'MISSING_EXCLUSION_COUNTS')
    for v in private['exclusions'].values():
        require(type(v) is int and v >= 0, 'BAD_EXCLUSION_COUNTS')
    ranks = [hashlib.sha256(DOMAIN.encode('ascii') + s.encode('ascii')).hexdigest() for s in ids]
    require(ranks == sorted(ranks), 'RANK_ORDER')
    olds = old_split.get('splits', {})
    require(all(k in olds for k in ('TRAIN', 'VAL', 'TEST')), 'OLD_SPLIT_KEYS')
    old_ids = set(olds['TRAIN'] + olds['VAL'] + olds['TEST'])
    require(len(old_ids) == 2368, 'OLD_SPLIT_SIZE_OR_DUPLICATES')
    require(not old_ids.intersection(ids), 'OLD_SPLIT_LEAK')
    for s in ids:
        old = hashlib.sha256(OLD_TEST_BUCKET_DOMAIN + s.encode('ascii')).hexdigest()
        require(int(old,16)%5 != 0, 'OLD_TEST_BUCKET_LEAK')
    require(public.get('science_executed') is False and private.get('model_forward') is False and
            public.get('gpu_used') is False and public.get('test_scored') is False and
            private.get('checkpoint_read') is False and private.get('prior_test_raw_text_exported') is False,
            'NO_SCIENCE_OR_OLD_TEST')
    return {
        'schema': 'ttm.gemma2.new_holdout.independent_membership_readback.v1',
        'status': 'PASS_SCOPED_MANIFEST_INDEPENDENT_READBACK',
        'membership_private_sha256': PRIVATE_SHA if exact_sha else 'FIXTURE_ONLY',
        'story_count': len(ids), 'target_count': sum(targets),
        'split_membership_exact_overlap': 0, 'old_test_bucket_membership': 0,
        'full_train_stories_scanned_reported': private['whole_train_stories_scanned'],
        'new_holdout_scored': False, 'gpu_used': False,
        'limitations': ['Checks frozen metadata and prior split exclusion, not independent full raw corpus near-duplicate rerun',
                        'No cross-near-duplicate audit against prior VALIDATION/TEST text',
                        'Does not authorize science or GPU']
    }


def run(args):
    repo = Path(args.repo).resolve(strict=True)
    if os.name == 'nt':
        require(str(repo).casefold() == WORKSPACE.casefold(), 'PROJECT_SCOPE')
    data = repo/'_tmp'/'ttm_gemma2_new_holdout_membership_v1_20261109'
    for f in (data/'MEMBERSHIP_PRIVATE.json', data/'SOURCE_SEAL_PUBLIC.json'):
        require(f.is_file() and not f.is_symlink(), 'INPUT_FILE_MISSING_OR_SYMLINK')
    p = data/'MEMBERSHIP_PRIVATE.json'
    raw = p.read_bytes()
    require(digest(raw) == PRIVATE_SHA, 'PRIVATE_SHA')
    public = json.loads((data/'SOURCE_SEAL_PUBLIC.json').read_text('utf-8'))
    private = json.loads(raw.decode('utf-8'))
    split_path = repo/'_tmp'/'ttm_t1_real_source_v1'/'T1_STORY_SPLIT_IDS_NO_RAW_TEXT.json'
    require(split_path.is_file(), 'SPLIT_FILE_MISSING')
    require(digest(split_path.read_bytes()) == SPLIT_SHA, 'SPLIT_BYTES_SHA')
    prior = json.loads(split_path.read_text('utf-8'))
    return audit(public, private, raw, prior)


def fixture():
    # Build metadata-only synthetic fixture; no raw story text and no old TEST IDs.
    ids = []
    i = 0
    while len(ids) < 320:
        s = digest(('fixture-%d' % i).encode())
        if int(digest(OLD_TEST_BUCKET_DOMAIN + s.encode()), 16) % 5 != 0:
            ids.append(s)
        i += 1
    ids.sort(key=lambda s: digest(DOMAIN.encode() + s.encode()))
    split = {'splits': {'TRAIN':[digest(('a%d' % i).encode()) for i in range(2048)],
                        'VAL':[digest(('b%d' % i).encode()) for i in range(256)],
                        'TEST':[digest(('c%d' % i).encode()) for i in range(64)]}}
    private = dict(schema='ttm.gemma2.new_holdout.private_membership.v1',
                   source_raw_sha256=RAW_SHA, prior_split_sha256=SPLIT_SHA,
                   bpe_file_sha256=BPE_SHA, selection_domain=DOMAIN,
                   whole_train_stories_scanned=2119489,n_candidates=640,
                   story_sha256_ordered=ids,target_counts_per_story=[237]*319+[195],
                   total_target_count=75798,full_train_near_jaccard_threshold=0.85,
                   n_candidates_rejected_near_full_train=0,
                   n_candidates_rejected_within_new=0,exclusions={},
                   model_forward=False,checkpoint_read=False,prior_test_raw_text_exported=False)
    public = dict(schema='ttm.gemma2.new_holdout.seal_receipt.v1',status='MEMBERSHIP_SEALED_NOT_EVALUATED',
                  membership_private_sha256=PRIVATE_SHA,source_sha256=RAW_SHA,split_sha256=SPLIT_SHA,
                  bpe_file_sha256=BPE_SHA,whole_train_stories_scanned=2119489,
                  story_count=320,target_count=75798,rejected_near_full_train=0,
                  rejected_near_internal=0,science_executed=False,gpu_used=False,test_scored=False)
    checks={}
    def pass_if(name, fn):
        try:
            fn();checks[name]='PASS'
        except Exception as e:
            raise AssertionError(name) from e
    pass_if('baseline_fixture', lambda: audit(public,private,b'',split,exact_sha=False))
    def reject(fn):
        try:fn()
        except RuntimeError:return
        raise AssertionError('FAIL_TO_REJECT')
    def test(name, updates):
        q={**private,**updates}
        pass_if(name,lambda:reject(lambda:audit(public,q,b'',split,exact_sha=False)))
    test('duplicate_id_rejected',{'story_sha256_ordered':ids[:-1]+ids[:1]})
    test('target_count_rejected',{'total_target_count':75797})
    test('bad_rank_rejected',{'story_sha256_ordered':list(reversed(ids))})
    test('bad_source_rejected',{'source_raw_sha256':{**RAW_SHA,'TinyStories-valid.txt':'0'*64}})
    test('old_split_leak_rejected',{'story_sha256_ordered':ids[:-1]+[split['splits']['VAL'][0]]})
    test('old_test_bucket_rejected',{'story_sha256_ordered':ids[:-1]+[next(s for s in (digest(('bad'+str(i)).encode()) for i in range(500)) if int(digest(OLD_TEST_BUCKET_DOMAIN + s.encode()),16)%5==0)]})
    test('old_test_scored_rejected',{'prior_test_raw_text_exported':True})
    return {'schema':'ttm.gemma2.holdout.readback.synthetic_qa.v1','status':'PASS','tests':len(checks),'checks':checks,
            'raw_data_read':False,'model_scored':False,'gpu_used':False}


def main():
    p=argparse.ArgumentParser()
    p.add_argument('--mode',choices=('fixture-qa','readback'),required=True)
    p.add_argument('--repo',default='')
    args=p.parse_args()
    report=fixture() if args.mode=='fixture-qa' else run(args)
    print(json.dumps(report,sort_keys=True,ensure_ascii=False))

if __name__=='__main__':
    main()
