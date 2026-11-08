#!/usr/bin/env python3
"""TTM T1 source verification, story split and TRAIN-only BPE2048.

Pinned external TinyStories original ASCII txt only, no V2/Parquet.
Never uploads raw stories; artifacts are identifiers, counts, hashes and tokenizer manifest.
No scientific evaluation and no GPU. Local no-overwrite.
"""
from __future__ import annotations
import argparse, hashlib, heapq, json, os, sys, urllib.request
from collections import Counter
from pathlib import Path
from itertools import combinations
from typing import Iterator

from source_t2.ttm_gpt2_bpe2048 import BPE2048, Story, pretok, BYTE2CHAR, N_MERGES, EOS_ID, VOCAB_SIZE, canonical_bytes, sha, _bpe_merge

REV = 'f54c09fd23315a6f9c86f9dc80f725de7d8f9c64'
URL = 'https://huggingface.co/datasets/roneneldan/TinyStories/resolve/' + REV + '/'
SOURCES = {
    'TinyStories-train.txt': 'c5cf5e22ff13614e830afbe61a99fbcbe8bcb7dd72252b989fa1117a368d401f',
    'TinyStories-valid.txt': '94e431816c4cce81ff71e4408ff8d3bda9a42e8d2663986697c3954288cb38b4',
}
EOS = b'<|endoftext|>'
SEED = b'TTM_SMALL4M_20261108_STORY_HASH_V1'
NEAR_THRESHOLD = .85
TRAIN_MODEL_N=2048
TOKENIZER_FIT_N=768
VAL_EVAL_N=256
TEST_EVAL_N=64


def hash_file(path: Path):
    h=hashlib.sha256()
    with path.open('rb') as f:
        for c in iter(lambda:f.read(1<<20), b''):
            h.update(c)
    return h.hexdigest()


def pinned_download(name:str, rawdir:Path):
    """No resume/retry or overwrite. Existing correct file is reused."""
    target=rawdir/name
    if target.is_file():
        if hash_file(target)!=SOURCES[name]:
            raise RuntimeError('RAW_SHA_MISMATCH_DO_NOT_REPLACE:'+name)
        return
    partial=target.with_suffix(target.suffix+'.partial')
    if partial.exists():
        raise RuntimeError('PARTIAL_DOWNLOAD_EXISTS_NO_AUTO_RETRY:'+str(partial))
    # Redirect to Hugging Face content endpoint; write bytes only within project.
    req=urllib.request.Request(URL+name,headers={'User-Agent':'TTM-small4m-one-shot-source-pin/1.0'})
    with urllib.request.urlopen(req,timeout=120) as r, partial.open('xb') as fd:
        if r.status!=200: raise RuntimeError('HTTP_NOT_200:'+str(r.status))
        while True:
            chunk=r.read(1<<20)
            if not chunk: break
            fd.write(chunk)
        fd.flush()
        os.fsync(fd.fileno())
    if hash_file(partial)!=SOURCES[name]:
        raise RuntimeError('DOWNLOADED_SHA_MISMATCH_KEEP_PARTIAL:'+name)
    os.replace(partial,target)


def iter_story_bytes(path:Path, chunk_size=1<<20)->Iterator[bytes]:
    # Streaming parser of original EOS-delimited txt. No whole-corpus read.
    buf=b''
    with path.open('rb') as fd:
        while True:
            b=fd.read(chunk_size)
            if not b: break
            buf+=b
            while True:
                i=buf.find(EOS)
                if i<0: break
                story=buf[:i].strip(b' \t\r\n')
                buf=buf[i+len(EOS):]
                if story: yield story
            if len(buf)>1<<23: # larger than any expected single story; fail closed
                raise RuntimeError('UNEXPECTED_STORY_OVER_8MIB')
    tail=buf.strip(b' \t\r\n')
    if tail: yield tail


def eligible_raw(b:bytes)->str:
    if not b or b'\x00' in b or EOS in b:
        raise RuntimeError('BAD_STORY_BYTES')
    t=b.decode('utf-8','strict')
    if not t.strip():raise RuntimeError('EMPTY_STORY')
    return t


def key_for(raw_sha:str):
    return hashlib.sha256(SEED + b'|' + raw_sha.encode('ascii')).hexdigest()


def min_k_push(heap:list,limit:int,raw_sha:str,text:str,namespace:str):
    # Sort independent of input order, deterministic top-k by content hash + seed.
    # Heap stores largest of selected scores at root (negative integer).
    key=int(key_for(raw_sha),16)
    entry=(-key,raw_sha,text,namespace)
    if len(heap)<limit:heapq.heappush(heap,entry)
    elif key < -heap[0][0]:heapq.heapreplace(heap,entry)


def sorted_selection(heap):
    return sorted(heap,key=lambda x:-x[0])


def word5(text:str):
    # Case-fold only for near-duplicate screening, model uses untouched bytes.
    words=text.casefold().split()
    return frozenset(tuple(words[i:i+5]) for i in range(max(0,len(words)-4)))


def near(a,b):
    if not a or not b:return False
    an,bn=len(a),len(b)
    if min(an,bn)<NEAR_THRESHOLD*max(an,bn):return False
    k=len(a & b)
    return (k/(an+bn-k))>=NEAR_THRESHOLD


def near_dedupe(rows, existing, max_items):
    """Exhaustive pairwise Jaccard for model-facing limited pilot samples."""
    kept=[]
    signatures=[word5(x['text']) for x in existing]
    rejected=0
    for rec in rows:
        w=word5(rec['text'])
        if any(near(w,s) for s in signatures):
            rejected+=1;continue
        kept.append(rec);signatures.append(w)
        if len(kept)==max_items:break
    return kept,rejected


def scan(trainfile:Path,validfile:Path):
    selected_train=[]
    seen_train=set()
    count_train=0;duplicates_train=0
    for raw in iter_story_bytes(trainfile):
        count_train+=1
        text=eligible_raw(raw)
        digest=sha(text.encode('utf-8'))
        if digest in seen_train:
            duplicates_train+=1;continue
        seen_train.add(digest)
        min_k_push(selected_train,TRAIN_MODEL_N*2,digest,text,'TRAIN')
    if count_train<100_000:raise RuntimeError('TRAIN_TOO_SMALL_STORY_PARSER_OR_WRONG_SOURCE')
    # Use deterministic larger candidate pool then exhaustive near dedup locally.
    all_train=[{'sha256':t[1],'text':t[2],'split':'TRAIN'} for t in sorted_selection(selected_train)]
    chosen_train,_ = near_dedupe(all_train,[],TRAIN_MODEL_N)
    if len(chosen_train)<TRAIN_MODEL_N:raise RuntimeError('TRAIN_DEDUP_INSUFFICIENT_CANDIDATES')
    val_candidates=[];test_candidates=[];valid_count=0;cross_exact=0;valid_duplicates=0
    seen_valid=set()
    for raw in iter_story_bytes(validfile):
        valid_count+=1
        text=eligible_raw(raw)
        digest=sha(text.encode('utf-8'))
        if digest in seen_train:
            cross_exact+=1;continue
        if digest in seen_valid:
            valid_duplicates+=1;continue
        seen_valid.add(digest)
        bucket=int(key_for(digest),16)%5
        min_k_push(val_candidates if bucket else test_candidates,
                   (VAL_EVAL_N if bucket else TEST_EVAL_N)*4,
                   digest,text,'VAL' if bucket else 'TEST')
    if valid_count<1000:raise RuntimeError('VALID_TOO_SMALL_STORY_PARSER_OR_WRONG_SOURCE')
    trows=[{'sha256':r[1],'text':r[2],'split':'TEST'} for r in sorted_selection(test_candidates)]
    vrows=[{'sha256':r[1],'text':r[2],'split':'VAL'} for r in sorted_selection(val_candidates)]
    # Do not admit TEST near-duplicates vs TRAIN or admitted VAL.
    vfinal,vdropped=near_dedupe(vrows,chosen_train,VAL_EVAL_N)
    tfinal,tdropped=near_dedupe(trows,chosen_train+vfinal,TEST_EVAL_N)
    if len(vfinal)!=VAL_EVAL_N or len(tfinal)!=TEST_EVAL_N:
        raise RuntimeError('HELDOUT_NEAR_DUP_DEDUP_INSUFFICIENT_CANDIDATES')
    return chosen_train,vfinal,tfinal,{
        'train_stories_scanned':count_train,'train_exact_duplicates':duplicates_train,
        'valid_stories_scanned':valid_count,'valid_exact_duplicates':valid_duplicates,
        'valid_collision_with_full_raw_train':cross_exact,
        'near_dropped_candidates_val':vdropped,'near_dropped_candidates_test':tdropped,
        'selected_train':len(chosen_train),'selected_val':len(vfinal),'selected_test':len(tfinal),
        'near_threshold_word5_jaccard':NEAR_THRESHOLD}


def efficient_bpe(stories:list[Story])->BPE2048:
    """Exactly the same pair/rank algorithm as pinned T2, with unique segments weighted."""
    if not stories or len({s.story_id for s in stories})!=len(stories):raise RuntimeError('TRAIN_IDS_INVALID')
    if any(s.split!='TRAIN' or s.source!='TinyStories-train.txt' for s in stories):
        raise RuntimeError('TRAIN_ONLY_VIOLATION')
    inputs=[{'id':s.story_id,'text_sha256':sha(s.text.encode('utf-8')),'source':s.source} for s in stories]
    source_commitment=sha(canonical_bytes(inputs))
    segments=Counter(tuple(p.encode('utf-8')) for s in stories for p in pretok(s.text) if p)
    tokens=[BYTE2CHAR[i] for i in range(256)]+['<|endoftext|>']
    token_bytes=[bytes([i]) for i in range(256)]+[b'']
    seen_text=set(token_bytes[:256]);pairs=[]
    for rank in range(N_MERGES):
        pair_counts=Counter()
        for seg,weight in segments.items():
            for pair in zip(seg,seg[1:]):pair_counts[pair]+=weight
        viable=[(-cnt,a,b) for (a,b),cnt in pair_counts.items()
                if token_bytes[a]+token_bytes[b] not in seen_text]
        if not viable:raise RuntimeError(f'INSUFFICIENT_MERGES_AT_{rank}')
        _,a,b=min(viable)
        pair=(a,b);new_id=257+rank;new_bytes=token_bytes[a]+token_bytes[b]
        token_bytes.append(new_bytes);tokens.append(tokens[a]+tokens[b]);pairs.append(pair);seen_text.add(new_bytes)
        merged=Counter()
        for seg,w in segments.items():
            updated=tuple(_bpe_merge(list(seg),pair,new_id)) if a in seg else seg
            merged[updated]+=w
        segments=merged
    return BPE2048(tokens,pairs,source_commitment,'PINNED_TINYSTORIES_TRAIN')


def build_manifest(train, val,test,stats,rawdir,bpe):
    # Never include raw text or validation/test-token contents in public reports.
    ids=lambda xs:[r['sha256'] for r in xs]
    pieces={s:ids(rows) for s,rows in [('TRAIN',train),('VAL',val),('TEST',test)]}
    assert not (set(pieces['TRAIN'])&set(pieces['VAL']) or set(pieces['TRAIN'])&set(pieces['TEST']) or set(pieces['VAL'])&set(pieces['TEST']))
    return {'schema':'ttm.t1.real.stories.split.v1','repo':'roneneldan/TinyStories','revision':REV,
            'license':'CDLA-Sharing-1.0','source_sha256':{name:hash_file(rawdir/name) for name in SOURCES},
            'story_delimiter':'<|endoftext|>','seed':SEED.decode(),
            'train_select_n':TRAIN_MODEL_N,'tokenizer_fit_n':TOKENIZER_FIT_N,'val_n':VAL_EVAL_N,'test_n':TEST_EVAL_N,
            'splits':pieces,'stats':stats,'tokenizer_manifest_sha256':bpe.manifest()['manifest_sha256'],
            'negative_privileged_access':'NO_TEST_READ_FOR_TOKENIZER_FIT'}


def main():
    ap=argparse.ArgumentParser()
    ap.add_argument('--repo',required=True)
    ap.add_argument('--mode',choices=['preview','execute','fixture-qa'],default='preview')
    args=ap.parse_args()
    repo=Path(args.repo).resolve(strict=True)
    if os.name=='nt' and str(repo).lower()!=r'd:\work\research\tokentomodel-lab':raise RuntimeError('WRONG_REPO_SCOPE')
    rawdir=repo/'datasets'/'tinystories_v1_original_pinned'
    out=repo/'_tmp'/'ttm_t1_real_source_v1'
    if args.mode=='preview':
        print('T1_PINNED_REV='+REV)
        for name,h in SOURCES.items():
            print(f'T1_SOURCE={name} expected_sha256={h} status='+('present' if (rawdir/name).exists() else 'not_downloaded'))
        print('T1_EXACT_RAW_SOURCE=HOLD_UNTIL_DOWNLOAD_HASH');return
    if args.mode=='fixture-qa':
        a=[b'abc',b'def\r\nmore',b'\xe4\xbd\xa0\xe5\xa5\xbd']
        import tempfile
        with tempfile.TemporaryDirectory() as d:
            file=Path(d)/'fixture.txt'
            file.write_bytes(EOS.join(a)+EOS)
            assert list(iter_story_bytes(file,chunk_size=5))==a
        print('T1_STORY_PARSER_SYNTHETIC=PASS');return
    if out.exists():raise RuntimeError('T1_RESULT_EXISTS_NEVER_RERUN')
    if rawdir.is_symlink() or repo.is_symlink():raise RuntimeError('LINKED_DIR_REFUSED')
    rawdir.mkdir(parents=True,exist_ok=True)
    for name in ('TinyStories-valid.txt','TinyStories-train.txt'):
        pinned_download(name,rawdir)
    train,val,test,stats=scan(rawdir/'TinyStories-train.txt',rawdir/'TinyStories-valid.txt')
    selected_fit=[Story(story_id=f'TRAIN_{i:04d}_{r["sha256"][:16]}',text=r['text'],split='TRAIN',source='TinyStories-train.txt')
                  for i,r in enumerate(train[:TOKENIZER_FIT_N])]
    bpe=efficient_bpe(selected_fit)
    out.mkdir(parents=False,exist_ok=False)
    split=build_manifest(train,val,test,stats,rawdir,bpe)
    t_manifest=bpe.manifest()
    files={'T1_STORY_SPLIT_IDS_NO_RAW_TEXT.json':split,'T1_BPE2048_REAL_TRAIN_MANIFEST.json':t_manifest}
    for name,obj in files.items():
        (out/name).write_bytes(canonical_bytes(obj)+b'\n')
    check={name:hash_file(out/name) for name in files}
    (out/'T1_RESULT.json').write_text(json.dumps({'status':'READY_FOR_INDEPENDENT_NO_LEAKAGE_QA',
        'hashes':check,'stats':stats,'train_only':True,'science_executed':False},sort_keys=True,indent=2)+'\n',encoding='utf-8')
    print('T1_RESULT='+str(out/'T1_RESULT.json'))
    print('T1_SOURCE_SPLITS=EXECUTED_REQUIRES_INDEPENDENT_QA')

if __name__=='__main__':main()
