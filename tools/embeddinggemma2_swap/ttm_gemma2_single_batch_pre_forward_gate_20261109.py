#!/usr/bin/env python3
"""TTM-Small-4M EmbeddingGemma2: pre-forward binding, test fixtures only.

NO evaluation mode. Never accesses corpus, model, GPU, historic TEST text,
new-holdout text, optimizer, or emits private IDs. Import as a library for a
future separately authorized one-shot evaluator. All windows are checked
BEFORE scoring_callback may be called. The real manifest SHA is immutable.
"""
from __future__ import annotations
import argparse
from dataclasses import dataclass
import hashlib
import json
from pathlib import Path
import importlib.util
import sys
import os
from typing import Callable, Sequence

CONTEXT = 256
VOCAB = 2048
EOS = 256
IGNORE = -100
SEALED_SHA = 'bedc3671256a66f605fbeb9f98bbd27149b456019d3d8bc5bbc89ebca6d09b47'
SPLIT_SHA = '9f2ebaca821bddf0a9d7ae30ccfcef34561b968b21159aa913794298235a2fa9'
BPE_FILE_SHA = 'cba18e60cee3d08a353ee6d4a451017289e45af7b4b1179c87171b9b78d7dfdc'
RAW_TRAIN_SHA = 'c5cf5e22ff13614e830afbe61a99fbcbe8bcb7dd72252b989fa1117a368d401f'
RAW_VALID_SHA = '94e431816c4cce81ff71e4408ff8d3bda9a42e8d2663986697c3954288cb38b4'
BPE_SOURCE_GIT_BLOB = 'fa5bd892941ba5aa6e6b2f0b2b0ae974efe297b6'
DOMAIN = b'TTM_GEMMA2_2048_NEW_HOLDOUT_V1|'
OLD_BUCKET = b'TTM_SMALL4M_20261108_STORY_HASH_V1|'
SEAL_COUNT = 320
SEAL_TARGETS = 75798
FROZEN_A_B_C_D = {
    'A':'ed7419f6421f4d82590c11ed8003b7df45aca9e86678ac2e1bdbeb62d8cd0081',
    'B':'a4bb239a4952f2670966e6aacf89b10374ecce9ac2f4b8ba22003ed1589c024c',
    'C':'ba04731f3d9f90a61e5d0819ca6f22a86775ff9784a94fe128128d205b7ca44d',
    'D':'db5bebe2182d4f479028b260e0f70497d67d6f6dfac845d95708cb9c9f78f41e',
}


def require(ok: bool, label: str) -> None:
    if not ok:
        raise RuntimeError('HOLD_PRE_FORWARD_' + label)


def digest(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def is_hex64(s: object) -> bool:
    return type(s) is str and len(s) == 64 and all(c in '0123456789abcdef' for c in s)


def pin_file(path: Path, sha: str) -> None:
    require(path.is_file() and not path.is_symlink(), 'PINNED_FILE_MISSING')
    require(digest(path.read_bytes()) == sha, 'PINNED_FILE_SHA')


def git_blob(data: bytes) -> str:
    header = b'blob ' + str(len(data)).encode('ascii') + b'\x00'
    return hashlib.sha1(header + data).hexdigest()


class RealEncoder:
    """Only factory build_pinned_encoder() may supply a real-science encoder."""
    def __init__(self, bpe, *, guard_token):
        require(guard_token is _ENCODER_GUARD, 'FORBID_MANUAL_ENCODER')
        self._bpe = bpe

    def __call__(self, text: str):
        return self._bpe.encode(text)


_ENCODER_GUARD = object()


def build_pinned_encoder(root: Path) -> RealEncoder:
    """At future authorized pre-forward: exact pinned source + BPE, no TEST read."""
    root = Path(root).resolve(strict=True)
    if os.name == 'nt':
        require(str(root).casefold() == r'd:\work\research\tokentomodel-lab', 'WORKSPACE_SCOPE')
    source = root/'tools'/'pilot_t1t3'/'source_t2'/'ttm_gpt2_bpe2048.py'
    raw_manifest = root/'_tmp'/'ttm_t1_real_source_v1'/'T1_BPE2048_REAL_TRAIN_MANIFEST.json'
    require(source.is_file() and not source.is_symlink(), 'BPE_SOURCE_MISSING')
    require(git_blob(source.read_bytes()) == BPE_SOURCE_GIT_BLOB, 'BPE_SOURCE_GIT_BLOB')
    pin_file(raw_manifest,BPE_FILE_SHA)
    spec = importlib.util.spec_from_file_location('_ttm_frozen_bpe_for_holdout',source)
    require(spec is not None and spec.loader is not None, 'BPE_MODULE')
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    bpe = module.BPE2048.from_manifest(json.loads(raw_manifest.read_text('utf-8')))
    require(bpe.source_kind == 'PINNED_TINYSTORIES_TRAIN', 'BPE_NOT_TRAIN_ONLY')
    return RealEncoder(bpe, guard_token=_ENCODER_GUARD)


@dataclass(frozen=True)
class Contract:
    story_ids: tuple[str, ...]
    label_counts: tuple[int, ...]
    membership_sha256: str
    kind: str
    witness: object | None = None


_SEAL_GUARD = object()


@dataclass(frozen=True)
class Window:
    story_id: str
    index: int
    x: tuple[int, ...]
    y: tuple[int, ...]


@dataclass(frozen=True)
class Material:
    story_id: str
    raw: bytes


def sealed_contract(private_raw: bytes, public: dict, split_raw: bytes) -> Contract:
    """Real-mode only. Never accepts a user-supplied 'fixture' flag."""
    require(digest(private_raw) == SEALED_SHA, 'MANIFEST_SHA')
    require(digest(split_raw) == SPLIT_SHA, 'HISTORICAL_SPLIT_SHA')
    private = json.loads(private_raw)
    split = json.loads(split_raw)
    require(private.get('schema') == 'ttm.gemma2.new_holdout.private_membership.v1', 'MANIFEST_SCHEMA')
    require(public.get('schema') == 'ttm.gemma2.new_holdout.seal_receipt.v1' and
            public.get('status') == 'MEMBERSHIP_SEALED_NOT_EVALUATED', 'RECEIPT_STATUS')
    require(public.get('membership_private_sha256') == SEALED_SHA, 'RECEIPT_MANIFEST_SHA')
    require(private.get('prior_split_sha256') == SPLIT_SHA and
            public.get('split_sha256') == SPLIT_SHA, 'SPLIT_PIN')
    require(private.get('bpe_file_sha256') == BPE_FILE_SHA and
            public.get('bpe_file_sha256') == BPE_FILE_SHA, 'TOKENIZER_PIN')
    source = {'TinyStories-train.txt': RAW_TRAIN_SHA, 'TinyStories-valid.txt': RAW_VALID_SHA}
    require(private.get('source_raw_sha256') == source == public.get('source_sha256'), 'SOURCE_PIN')
    require(private.get('selection_domain') == DOMAIN.decode('ascii'), 'MEMBERSHIP_DOMAIN')
    ids = private.get('story_sha256_ordered')
    counts = private.get('target_counts_per_story')
    require(type(ids) is list and len(ids) == SEAL_COUNT and all(is_hex64(z) for z in ids)
            and len(set(ids)) == SEAL_COUNT, 'STORY_IDS')
    require(type(counts) is list and len(counts) == SEAL_COUNT and
            all(type(n) is int and n > 0 for n in counts), 'LABEL_COUNTS')
    require(sum(counts) == private.get('total_target_count') == public.get('target_count') == SEAL_TARGETS
            and public.get('story_count') == SEAL_COUNT, 'TOTAL_LABELS')
    ranks = [digest(DOMAIN + s.encode('ascii')) for s in ids]
    require(ranks == sorted(ranks), 'RANK_ORDER')
    old = split.get('splits', {})
    require(all(k in old for k in ('TRAIN','VAL','TEST')), 'OLD_SPLIT_KEYS')
    previously_used = old['TRAIN'] + old['VAL'] + old['TEST']
    require(len(previously_used) == 2368 and len(set(previously_used)) == 2368, 'OLD_SPLIT_COUNTS')
    require(not set(ids).intersection(previously_used), 'OLD_EXACT_OVERLAP')
    require(all(int(digest(OLD_BUCKET + s.encode('ascii')), 16) % 5 != 0 for s in ids), 'OLD_TEST_BUCKET')
    require(public.get('test_scored') is False and public.get('science_executed') is False
            and public.get('gpu_used') is False, 'SEALED_NOT_SCORED')
    return Contract(tuple(ids), tuple(counts), SEALED_SHA, 'SEALED_REAL', _SEAL_GUARD)


def expected_windows(story_id: str, token_ids: Sequence[int]) -> tuple[Window, ...]:
    """Construct from all non-EOS BPE IDs of exactly one story."""
    require(is_hex64(story_id), 'STORY_HASH_FORMAT')
    require(bool(token_ids) and all(type(x) is int and 0 <= x < VOCAB and x != EOS
                                   for x in token_ids), 'BPE_TOKEN_IDS')
    ids = list(token_ids) + [EOS]
    out = []
    for j, offset in enumerate(range(0, len(ids)-1, CONTEXT)):
        n = min(CONTEXT, len(ids)-1-offset)
        x = tuple(ids[offset:offset+n] + [0]*(CONTEXT-n))
        y = tuple(ids[offset+1:offset+n+1] + [IGNORE]*(CONTEXT-n))
        out.append(Window(story_id, j, x, y))
    require(sum(sum(v != IGNORE for v in row.y) for row in out) == len(token_ids), 'INTERNAL_TARGETS')
    require(out[-1].y[len(token_ids)-CONTEXT*(len(out)-1)-1] == EOS, 'FINAL_EOS_TARGET')
    return tuple(out)


def validate_complete_plan(contract: Contract, stories: Sequence[Material], windows: Sequence[Window],
                           encode: Callable[[str], Sequence[int]]) -> dict:
    """Verify whole plan first; caller must not forward until this returns.

    For real use encode MUST come from SHA-pinned BPE2048.from_manifest(...).
    The future external orchestrator is responsible for obtaining exact raw
    bytes from the pinned VALID file without decoding historical TEST stories.
    """
    require(contract.kind in ('SEALED_REAL','SYNTHETIC_FIXTURE_ONLY'), 'CONTRACT_KIND')
    if contract.kind == 'SEALED_REAL':
        require(contract.witness is _SEAL_GUARD, 'REAL_SEAL_WITNESS')
        require(isinstance(encode, RealEncoder), 'REAL_REQUIRES_PINNED_BPE')
        require(len(contract.story_ids) == SEAL_COUNT and sum(contract.label_counts) == SEAL_TARGETS
                and contract.membership_sha256 == SEALED_SHA, 'REAL_CONTRACT_UNALTERED')
    require(len(stories) == len(contract.story_ids) and len(contract.story_ids) == len(contract.label_counts),
            'STORY_COUNT')
    require(all(isinstance(s, Material) for s in stories), 'MATERIAL_TYPE')
    require(tuple(s.story_id for s in stories) == contract.story_ids, 'STORY_MEMBERSHIP_AND_ORDER')
    require(len(windows) > 0, 'NO_WINDOWS')
    expected = []
    observed_targets = 0
    for s, targets in zip(stories, contract.label_counts):
        require(type(s.raw) is bytes and digest(s.raw) == s.story_id, 'RAW_STORY_ID_SHA')
        text = s.raw.decode('utf-8', 'strict')
        require(bool(text.strip()) and '\x00' not in text, 'STORY_BYTES_INVALID')
        encoded = encode(text)
        require(type(encoded) in (list,tuple) and len(encoded) == targets, 'BPE_COUNT_OR_TYPE')
        expected.extend(expected_windows(s.story_id, encoded))
        observed_targets += len(encoded)
    require(observed_targets == sum(contract.label_counts), 'TOTAL_TARGETS')
    require(len(windows) == len(expected), 'WINDOW_COUNT_DUPLICATE_OR_MISSING')
    for supplied, correct in zip(windows, expected):
        require(isinstance(supplied, Window), 'WINDOW_CLASS')
        require(supplied.story_id == correct.story_id and supplied.index == correct.index,
                'WINDOW_ORDER_OR_ID')
        require(type(supplied.x) is tuple and type(supplied.y) is tuple and
                len(supplied.x) == CONTEXT and len(supplied.y) == CONTEXT, 'WINDOW_TENSOR_SHAPE')
        require(all(type(v) is int for v in supplied.x+supplied.y), 'WINDOW_TENSOR_INT_TYPE')
        require(supplied.x == correct.x and supplied.y == correct.y,
                'WINDOW_CONTENT_EOS_PADDING_AND_NEXT_TOKEN')
    return {'status':'PASS_PRE_FORWARD_FULL_BINDING', 'contract_kind':contract.kind,
            'story_count':len(stories), 'target_count':observed_targets,
            'window_count':len(expected),
            'membership_sha256':contract.membership_sha256,
            'model_forward_calls':0}


def forward_only_after_guard(contract, stories, windows, encode, callback, *, synthetic_qa=False):
    """No execution on REAL holdout in this script. QA calls with fixture only."""
    require(contract.kind == 'SEALED_REAL' or
            (synthetic_qa is True and contract.kind == 'SYNTHETIC_FIXTURE_ONLY'), 'NO_UNAUTHORIZED_FIXTURE')
    witness = validate_complete_plan(contract, stories, windows, encode)
    # Do not provide partial input to callback: complete whole-plan preflight first.
    return callback(windows, witness)


def _synthetic_near_distinct_pair():
    """Two synthetic strings with distinct SHA and high 5-gram Jaccard.
    Purely demonstrates why exact hashes and TEST buckets don't imply near-disjointness.
    """
    a = [f'w{i:03d}' for i in range(100)]
    b = a.copy(); b[50] = 'changed_midpoint'
    A = ' '.join(a); B = ' '.join(b)
    def word5(txt):
        words = txt.casefold().split()
        return {tuple(words[i:i+5]) for i in range(len(words)-4)}
    x,y=word5(A),word5(B)
    return digest(A.encode())!=digest(B.encode()), len(x&y)/len(x|y)


def qa() -> dict:
    checks = {}
    def passed(name, predicate):
        if not predicate: raise AssertionError('FIXTURE_FAIL_'+name)
        checks[name] = 'PASS'
    def rejects(name, fn):
        try:fn()
        except (RuntimeError, UnicodeDecodeError):pass
        else:raise AssertionError('FAIL_OPEN_'+name)
        checks[name]='PASS'
    raws = [b'alpha beta gamma',b'foo bar baz qux',b'last sample of synthetic words']
    ids = tuple(digest(raw) for raw in raws)
    # synthetic independent tokenizer: one token per ASCII character; never EOS
    encoder = lambda text: [ord(ch) for ch in text]
    counts = tuple(len(encoder(raw.decode())) for raw in raws)
    spec = Contract(ids, counts, 'SYNTHETIC_NOT_SEALED', 'SYNTHETIC_FIXTURE_ONLY')
    stories = [Material(s,r) for s,r in zip(ids,raws)]
    win = [w for s,raw in zip(ids,raws) for w in expected_windows(s,encoder(raw.decode()))]
    witness = validate_complete_plan(spec,stories,win,encoder)
    passed('expected_good_fixture',witness['status']=='PASS_PRE_FORWARD_FULL_BINDING')
    passed('count_stories',witness['story_count']==3)
    passed('total_targets',witness['target_count']==sum(counts))
    passed('window_count',witness['window_count']==3)
    passed('caller_witness_no_forward',witness['model_forward_calls']==0)
    calls=[]
    def callback(w,witness):
        calls.append(len(w));return 'SYNTHETIC_OK'
    passed('synthetic_callback_success',forward_only_after_guard(spec,stories,win,encoder,callback,synthetic_qa=True)=='SYNTHETIC_OK')
    passed('synthetic_callback_once',calls==[len(win)])
    rejects('synthetic_callback_no_fixture_flag',lambda:forward_only_after_guard(spec,stories,win,encoder,callback))
    passed('no_callback_when_flag_wrong',len(calls)==1)
    def rejected_before(name, stories_input=stories, windows_input=win, encode=encoder, spec_input=spec):
        prior=len(calls)
        rejects(name,lambda:forward_only_after_guard(spec_input,stories_input,windows_input,encode,callback,synthetic_qa=True))
        passed(name+'_ZERO_FORWARDS',len(calls)==prior)
    rejected_before('extra_unknown_story',stories+[Material(digest(b'unknown'),b'unknown')])
    rejected_before('missing_story',stories[:-1])
    rejected_before('story_order_swap',[stories[1],stories[0],stories[2]])
    rejected_before('duplicate_story_id',[stories[0],stories[0],stories[2]])
    rejected_before('altered_story_raw',[Material(ids[0],b'other'),*stories[1:]])
    rejected_before('empty_raw',[Material(ids[0],b''),*stories[1:]])
    rejected_before('extra_window',windows_input=win+[win[-1]])
    rejected_before('missing_window',windows_input=win[:-1])
    rejected_before('duplicate_window',windows_input=[win[0],win[0],win[2]])
    rejected_before('reversed_window_order',windows_input=list(reversed(win)))
    def change_window(i, **changes):
        s=win[i]
        fields={'story_id':s.story_id,'index':s.index,'x':s.x,'y':s.y}
        fields.update(changes)
        z=win.copy();z[i]=Window(**fields)
        return z
    rejected_before('bad_window_index',windows_input=change_window(0,index=2))
    rejected_before('wrong_window_id',windows_input=change_window(1,story_id=ids[0]))
    rejected_before('wrong_window_x',windows_input=change_window(0,x=(999,)+win[0].x[1:]))
    rejected_before('wrong_window_y',windows_input=change_window(0,y=(999,)+win[0].y[1:]))
    old_y=list(win[0].y);old_y[counts[0]-1]=33
    rejected_before('wrong_eos_last',windows_input=change_window(0,y=tuple(old_y)))
    rejected_before('wrong_padding',windows_input=change_window(0,y=win[0].y[:70]+(0,)+win[0].y[71:]))
    rejected_before('wrong_window_length',windows_input=change_window(0,x=win[0].x[:-1]))
    rejected_before('wrong_tensor_type',windows_input=change_window(0,x=(True,)+win[0].x[1:]))
    rejected_before('encoder_wrong_length',encode=lambda s:encoder(s)[:-1])
    rejected_before('contract_wrong_count',spec_input=Contract(ids,(counts[0]+1,counts[1],counts[2]),spec.membership_sha256,spec.kind))
    rejected_before('wrong_legal_contract_kind',spec_input=Contract(ids,counts,spec.membership_sha256,'UNAUTHORIZED'))
    # Boundary lengths: each synthetic story's EOS is scored once, padding invisible.
    for n in (1,2,3,7,254,255,256,257,258,511,512,513,769,1025):
        tok=[(37*i+15)%255 for i in range(n)]
        wid=digest(('case'+str(n)).encode())
        w=expected_windows(wid,tok)
        passed(f'boundary_n{n}_targets',sum(sum(y != IGNORE for y in row.y) for row in w)==n)
        passed(f'boundary_n{n}_counts',len(w)==(n+CONTEXT-1)//CONTEXT)
        passed(f'boundary_n{n}_eos',w[-1].y[(n-1)%CONTEXT]==EOS)
        passed(f'boundary_n{n}_padding',all(all(y==IGNORE for y in row.y[min(CONTEXT,n-256*row.index):]) for row in w))
        passed(f'boundary_n{n}_no_cross', all(row.story_id==wid for row in w))
    # Run one complete 320-story/75,798-label *synthetic* plan: includes a
    # three-window long story and many distinct IDs. Does not read real corpus.
    n_per_story = [513,99,99] + [237]*316 + [195]
    require(len(n_per_story)==320 and sum(n_per_story)==75798,'INTERNAL_FIXTURE_COUNTS')
    large_raw=[]
    for i,n in enumerate(n_per_story):
        prefix=f'synthetic-{i:04d}-'.encode('ascii')
        require(len(prefix)<n, 'INTERNAL_PREFIX')
        large_raw.append(prefix + b'x'*(n-len(prefix)))
    large_stories = [Material(digest(raw),raw) for raw in large_raw]
    large_contract = Contract(tuple(s.story_id for s in large_stories),tuple(n_per_story),
                              'SYNTHETIC_320_STORIES_NO_REAL_MANIFEST','SYNTHETIC_FIXTURE_ONLY')
    large_windows = [w for s in large_stories for w in expected_windows(s.story_id,encoder(s.raw.decode()))]
    large_witness=validate_complete_plan(large_contract,large_stories,large_windows,encoder)
    passed('full_scale_320_synthetic_stories',large_witness['story_count']==320)
    passed('full_scale_75798_synthetic_targets',large_witness['target_count']==75798)
    passed('full_scale_multiwindow',len(large_windows)>320)
    passed('full_scale_still_no_forward',large_witness['model_forward_calls']==0)
    rejects('full_scale_extra_window',lambda:validate_complete_plan(
        large_contract,large_stories,large_windows+[large_windows[0]],encoder))
    rejects('full_scale_wrong_last_label',lambda:validate_complete_plan(
        large_contract,large_stories,large_windows[:-1],encoder))
    rejects('real_contract_fixture_encoder_rejected',lambda:validate_complete_plan(
        Contract(ids,counts,SEALED_SHA,'SEALED_REAL'),stories,win,encoder))
    rejects('manual_real_encoder_rejected',lambda:RealEncoder(None, guard_token=object()))
    rejects('no_tokens',lambda:expected_windows(ids[0],[]))
    rejects('eos_in_body',lambda:expected_windows(ids[0],[13,256]))
    rejects('bad_vocab',lambda:expected_windows(ids[0],[2048]))
    rejects('negative_token',lambda:expected_windows(ids[0],[-1]))
    rejects('bad_hash_id',lambda:expected_windows('x',[1]))
    # Pure mathematical counterexample of Jaccard overlap with non-identical hashes.
    is_diff, jac=_synthetic_near_distinct_pair()
    passed('distinct_sha_does_not_rule_out_near',is_diff and jac>=.85)
    return {'schema':'ttm.gemma2.pre_forward.single_batch.synthetic_qa.v1',
            'status':'PASS_SYNTHETIC_PRE_FORWARD_BINDING',
            'passed':len(checks),'total':len(checks),
            'synthetic_stories':len(stories),'synthetic_valid_targets':sum(counts),
            'negative_forward_calls_observed':0,'near_duplicate_counterexample_jaccard':jac,
            'only_synthetic_text':True,'actual_new_holdout_opened':False,
            'old_test_text_opened':False,'model_forward_on_real_data':False,
            'gpu_used':False,'science_executed':False,'check_names':list(checks)}


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--mode',required=True,choices=['fixture-qa'])
    args = ap.parse_args()
    result = qa()
    print(json.dumps(result,ensure_ascii=False,sort_keys=True))


if __name__ == '__main__':
    main()
