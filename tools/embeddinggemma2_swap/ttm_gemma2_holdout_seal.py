#!/usr/bin/env python3
"""TTM EmbeddingGemma2: source membership seal, WITHOUT model evaluation or training.

Requires original pinned local T1 sources. Writes only membership SHA and metadata
under the project's private _tmp; does not read raw historical TEST via its ID list.
"""
from __future__ import annotations
import argparse
from collections import Counter
import hashlib
import heapq
import json
import math
import os
from pathlib import Path
import sys

RAW = {
    'TinyStories-train.txt': 'c5cf5e22ff13614e830afbe61a99fbcbe8bcb7dd72252b989fa1117a368d401f',
    'TinyStories-valid.txt': '94e431816c4cce81ff71e4408ff8d3bda9a42e8d2663986697c3954288cb38b4',
}
T1_SPLIT_SHA = '9f2ebaca821bddf0a9d7ae30ccfcef34561b968b21159aa913794298235a2fa9'
T1_BPE_SHA = 'cba18e60cee3d08a353ee6d4a451017289e45af7b4b1179c87171b9b78d7dfdc'
T1_PARSER_BLOB = '3ef500ddd8259153e7e3d4602915a51b7060a40f'
T1_BPE_BLOB = 'fa5bd892941ba5aa6e6b2f0b2b0ae974efe297b6'
DOMAIN = b'TTM_GEMMA2_2048_NEW_HOLDOUT_V1|'
OLD_BUCKET_SEED = b'TTM_SMALL4M_20261108_STORY_HASH_V1|'
NEAR = 0.85
CANDIDATE_POOL = 640
STORY_COUNT = 320
MIN_TARGETS = 50_000
PRIVATE_SUBDIR = 'ttm_gemma2_new_holdout_membership_v1_20261109'


def file_sha(path):
    h = hashlib.sha256()
    with Path(path).open('rb') as f:
        for part in iter(lambda: f.read(1 << 20), b''):
            h.update(part)
    return h.hexdigest()


def git_blob(path):
    b = Path(path).read_bytes()
    return hashlib.sha1(b'blob ' + str(len(b)).encode() + b'\0' + b).hexdigest()


def insist(condition, reason):
    if not condition:
        raise RuntimeError('HOLD_' + reason)


def word5(text):
    w = text.casefold().split()
    return frozenset(tuple(w[i:i + 5]) for i in range(max(0, len(w) - 4)))


def near(a, b):
    if not a or not b or min(len(a), len(b)) < NEAR * max(len(a), len(b)):
        return False
    k = len(a & b)
    return k / (len(a) + len(b) - k) >= NEAR


def rank_sha(digest):
    return hashlib.sha256(DOMAIN + digest.encode('ascii')).hexdigest()


def old_is_test_bucket(digest):
    score = hashlib.sha256(OLD_BUCKET_SEED + digest.encode('ascii')).hexdigest()
    return int(score, 16) % 5 == 0


def compute_candidates(iter_valid, seen_train, previously_used):
    """Hash first, then decode only new eligible stories; never decode old TEST."""
    heap, seen_valid = [], set()
    excluded = Counter()
    for raw in iter_valid:
        digest = hashlib.sha256(raw).hexdigest()
        if digest in seen_train:
            excluded['EXACT_FULL_TRAIN'] += 1
            continue
        if digest in previously_used:
            excluded['EXISTING_TRAIN_VAL_TEST'] += 1
            continue
        if old_is_test_bucket(digest):
            excluded['ORIGINAL_TEST_BUCKET'] += 1
            continue
        if digest in seen_valid:
            excluded['DUP_VALID'] += 1
            continue
        seen_valid.add(digest)
        text = raw.decode('utf-8', 'strict')
        insist(bool(text.strip()) and '\x00' not in text, 'INVALID_STORY')
        if not word5(text):
            excluded['TOO_SHORT_FOR_NEAR_AUDIT'] += 1
            continue
        key = int(rank_sha(digest), 16)
        item = (-key, digest, text)
        if len(heap) < CANDIDATE_POOL:
            heapq.heappush(heap, item)
        elif key < -heap[0][0]:
            heapq.heapreplace(heap, item)
    ordered = sorted(heap, key=lambda a: -a[0])
    return [(d, t, word5(t)) for _, d, t in ordered], dict(excluded)


def full_train_near_audit(iter_train, candidates):
    """Exact all-TRAIN word-5 shingles; inverted index covers every candidate word-5.

    Every Jaccard>=0.85 pair shares shingles and is considered; no LSH recall gap.
    CPU-only full scan is intentionally more costly than a sampling audit.
    """
    inverse = {}
    for j, (_, _, shingles) in enumerate(candidates):
        for shingle in shingles:
            inverse.setdefault(shingle, []).append(j)
    rejected = set()
    checked = 0
    for raw in iter_train:
        checked += 1
        text = raw.decode('utf-8', 'strict')
        shingles = word5(text)
        if not shingles:
            continue
        overlaps = Counter()
        for shingle in shingles:
            for j in inverse.get(shingle, ()):
                if j not in rejected:
                    overlaps[j] += 1
        for j, count in overlaps.items():
            other = candidates[j][2]
            if min(len(shingles), len(other)) < NEAR * max(len(shingles), len(other)):
                continue
            if count / (len(shingles) + len(other) - count) >= NEAR:
                rejected.add(j)
        if len(rejected) == len(candidates):
            break
    return rejected, checked


def select_non_near(candidates, near_train):
    chosen, chosen_shingles = [], []
    reject_inter = 0
    for j, (digest, text, words) in enumerate(candidates):
        if j in near_train:
            continue
        if any(near(words, old) for old in chosen_shingles):
            reject_inter += 1
            continue
        chosen.append((digest, text))
        chosen_shingles.append(words)
        if len(chosen) == STORY_COUNT:
            break
    return chosen, reject_inter


def nll_for_logits(logits, label):
    """Independent, standard-library logsumexp reference for one synthetic token."""
    insist(0 <= label < len(logits), 'LOGIT_LABEL_RANGE')
    insist(all(math.isfinite(v) for v in logits), 'NONFINITE_LOGITS')
    peak = max(logits)
    return peak + math.log(sum(math.exp(v - peak) for v in logits)) - logits[label]


def score_masked_story(rows):
    total, targets = 0.0, 0
    for logits, label in rows:
        if label == -100:
            continue
        total += nll_for_logits(logits, label)
        targets += 1
    insist(targets > 0, 'NO_VALID_STORY_TARGETS')
    return total, targets


def fixture_qa():
    checks = {}
    def ck(name, value):
        assert value, name
        checks[name] = 'PASS'
    ck('score_rank_deterministic', rank_sha('abc') == rank_sha('abc'))
    ck('exclude_old_test_bucket', old_is_test_bucket('abc') == old_is_test_bucket('abc'))
    ck('near_true', near(word5('once a blue bird flew home'), word5('once a blue bird flew home')))
    ck('near_false', not near(word5('one two three four five six'), word5('seven eight nine ten eleven twelve')))
    ck('no_shingle_safe', not near(word5('abc'), word5('abc')))
    new_story = 'new safe story with five words'
    # Pick a fixture whose actual SHA isn't part of the old TEST bucket.
    while old_is_test_bucket(hashlib.sha256(new_story.encode()).hexdigest()):
        new_story += ' unique'
    c, ex = compute_candidates((s.encode() for s in ('old story', new_story)), {hashlib.sha256(b'old story').hexdigest()}, set())
    ck('full_train_exact_exclusion', ex.get('EXACT_FULL_TRAIN') == 1)
    ck('candidate_kept', len(c) == 1)
    rej, count = full_train_near_audit([new_story.encode()], c)
    ck('near_train_reject', rej == {0} and count == 1)
    chosen, _ = select_non_near(c, rej)
    ck('near_train_not_selected', not chosen)
    ck('masked_loss', abs(score_masked_story([([0.0, 0.0], 1), ([1.0, 2.0], -100)])[0] - math.log(2)) < 1e-12)
    ck('target_count', score_masked_story([([0.0, 0.0], 0), ([0.0, 0.0], -100)])[1] == 1)
    ck('finite_rejection', _raises(lambda: nll_for_logits([float('nan'), 0.0], 0)))
    ck('missing_target_rejection', _raises(lambda: score_masked_story([([0.0, 0.0], -100)])))
    ck('other_candidate_far', not near(word5('these words never appear together'), word5('the cat sat upon chair')))
    return {'schema': 'ttm.gemma2.holdout.synthetic_qa.v1', 'status': 'PASS', 'test_count': len(checks), 'checks': checks, 'raw_data_read': False, 'model_scored': False, 'gpu_used': False}


def _raises(fn):
    try:
        fn()
        return False
    except RuntimeError:
        return True


def check_pins(repo):
    root = Path(repo).resolve(strict=True)
    if os.name == 'nt':
        insist(str(root).casefold() == r'd:\work\research\tokentomodel-lab', 'ROOT_SCOPE')
    insist(not root.is_symlink(), 'SYMLINK_ROOT')
    t1 = root / 'tools' / 'pilot_t1t3'
    insist(git_blob(t1 / 't1_source_split_tokenizer.py') == T1_PARSER_BLOB, 'T1_PARSER_SOURCE_CHANGED')
    insist(git_blob(t1 / 'source_t2' / 'ttm_gpt2_bpe2048.py') == T1_BPE_BLOB, 'BPE_SOURCE_CHANGED')
    data = root / 'datasets' / 'tinystories_v1_original_pinned'
    for name, expected in RAW.items():
        p = data / name
        insist(p.is_file() and not p.is_symlink(), 'RAW_SOURCE_MISSING_' + name)
        insist(file_sha(p) == expected, 'RAW_SHA_' + name)
    split = root / '_tmp' / 'ttm_t1_real_source_v1' / 'T1_STORY_SPLIT_IDS_NO_RAW_TEXT.json'
    bpe_file = root / '_tmp' / 'ttm_t1_real_source_v1' / 'T1_BPE2048_REAL_TRAIN_MANIFEST.json'
    insist(file_sha(split) == T1_SPLIT_SHA, 'T1_SPLIT_SHA')
    insist(file_sha(bpe_file) == T1_BPE_SHA, 'T1_BPE_SHA')
    obj = json.loads(split.read_text('utf-8'))
    groups = obj['splits']
    insist({k: len(groups[k]) for k in ('TRAIN', 'VAL', 'TEST')} == {'TRAIN': 2048, 'VAL': 256, 'TEST': 64}, 'ORIGINAL_SPLIT_SIZE')
    insist(len(set(groups['TRAIN'] + groups['VAL'] + groups['TEST'])) == 2368, 'ORIGINAL_SPLIT_DISJOINT')
    return root, t1, data, obj, bpe_file


def seal(repo):
    root, t1, data, original, bpe_file = check_pins(repo)
    out = root / '_tmp' / PRIVATE_SUBDIR
    insist(not out.exists(), 'ONE_SHOT_OUTPUT_ALREADY_EXISTS')
    sys.path.insert(0, str(t1))
    from t1_source_split_tokenizer import iter_story_bytes
    from source_t2.ttm_gpt2_bpe2048 import BPE2048
    seen_train = set()
    train_count = 0
    for raw in iter_story_bytes(data / 'TinyStories-train.txt'):
        train_count += 1
        seen_train.add(hashlib.sha256(raw).hexdigest())
    insist(train_count == 2119489, 'TRAIN_STORY_COUNT_CHANGED')
    groups = original['splits']
    old = set(groups['TRAIN'] + groups['VAL'] + groups['TEST'])
    candidates, excluded = compute_candidates(iter_story_bytes(data / 'TinyStories-valid.txt'), seen_train, old)
    insist(len(candidates) == CANDIDATE_POOL, 'INSUFFICIENT_VALID_CANDIDATES')
    rejected, scanned = full_train_near_audit(iter_story_bytes(data / 'TinyStories-train.txt'), candidates)
    insist(scanned == train_count, 'NEAR_AUDIT_NOT_FULL_TRAIN')
    chosen, within_rej = select_non_near(candidates, rejected)
    insist(len(chosen) == STORY_COUNT, 'INSUFFICIENT_NONNEAR_STORIES')
    bpe = BPE2048.from_manifest(json.loads(bpe_file.read_text('utf-8')))
    insist(bpe.source_kind == 'PINNED_TINYSTORIES_TRAIN', 'WRONG_BPE_ORIGIN')
    # Mirrors T4: inputs = bpe.encode(text)+[EOS], score len(inputs)-1 targets.
    target_counts = [len(bpe.encode(text)) for _, text in chosen]
    insist(all(n > 0 for n in target_counts), 'EMPTY_ENCODED_STORY')
    insist(sum(target_counts) >= MIN_TARGETS, 'HOLD_TARGET_CAPACITY')
    rec = {'schema':'ttm.gemma2.new_holdout.private_membership.v1',
           'source_raw_sha256': RAW, 'prior_split_sha256': T1_SPLIT_SHA,
           'bpe_file_sha256': T1_BPE_SHA, 'selection_domain': DOMAIN.decode(),
           'selection_rule':'rank unique eligible non-TEST-bucket valid stories; top 640; exclude near TRAIN and earlier selections; keep first 320',
           'story_sha256_ordered':[d for d, _ in chosen],
           'target_counts_per_story':target_counts, 'total_target_count':sum(target_counts),
           'whole_train_stories_scanned':train_count,
           'full_train_near_jaccard_threshold':NEAR,
           'n_candidates':len(candidates), 'n_candidates_rejected_near_full_train':len(rejected),
           'n_candidates_rejected_within_new':within_rej,
           'exclusions':excluded, 'prior_test_raw_text_exported':False,
           'checkpoint_read':False, 'model_forward':False, 'gpu_used':False}
    content = json.dumps(rec, sort_keys=True, ensure_ascii=False, separators=(',', ':')).encode() + b'\n'
    digest = hashlib.sha256(content).hexdigest()
    out.mkdir(parents=True, exist_ok=False)
    (out / 'MEMBERSHIP_PRIVATE.json').write_bytes(content)
    public = {'schema': 'ttm.gemma2.new_holdout.seal_receipt.v1',
              'status': 'MEMBERSHIP_SEALED_NOT_EVALUATED', 'membership_private_sha256': digest,
              'source_sha256': RAW, 'split_sha256': T1_SPLIT_SHA,
              'bpe_file_sha256': T1_BPE_SHA, 'story_count': STORY_COUNT,
              'target_count':sum(target_counts), 'whole_train_stories_scanned':train_count,
              'rejected_near_full_train':len(rejected), 'rejected_near_internal':within_rej,
              'science_executed':False, 'test_scored':False, 'gpu_used':False}
    (out / 'SOURCE_SEAL_PUBLIC.json').write_text(json.dumps(public, sort_keys=True, ensure_ascii=False, indent=2)+'\n', encoding='utf-8')
    return public


def main():
    ap=argparse.ArgumentParser()
    ap.add_argument('--mode',choices=['fixture-qa', 'preflight', 'seal-membership'],required=True)
    ap.add_argument('--repo',default='')
    args=ap.parse_args()
    if args.mode == 'fixture-qa':
        print(json.dumps(fixture_qa(), ensure_ascii=False, sort_keys=True))
    elif args.mode == 'preflight':
        root, *_ = check_pins(args.repo)
        print('TTM_GEMMA2_NEW_HOLDOUT_SOURCE_PREFLIGHT=PASS_RAW_SPLIT_BPE_PINS')
        print('TTM_GEMMA2_NEW_HOLDOUT_MEMBERSHIP=NOT_SEALED')
    else:
        print(json.dumps(seal(args.repo),ensure_ascii=False,sort_keys=True))

if __name__ == '__main__':
    main()
