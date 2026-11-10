#!/usr/bin/env python3
"""Independent CPU-only OOD256 integrity readback. No model, no inference."""
import argparse, hashlib, json
from pathlib import Path
import numpy as np

WIKI='49280f3dd993cbdfd322186194133d5d1935f81e1c91064c239f2a70ebb02701'
BPE='cba18e60cee3d08a353ee6d4a451017289e45af7b4b1179c87171b9b78d7dfdc'
SUB='_tmp/ttm_gemma2_ood_wikitext2_cpu_v1_20261111'

def sha(path):
    h=hashlib.sha256()
    with path.open('rb') as f:
        for b in iter(lambda:f.read(1<<20),b''): h.update(b)
    return h.hexdigest()
def need(ok,msg):
    if not ok:raise RuntimeError('HOLD_INDEPENDENT_'+msg)
def main(root):
    root=Path(root).resolve(strict=True);need(root.name.lower()=='tokentomodel-lab','PROJECT_ROOT')
    d=root/SUB
    pp=d/'OOD256_PUBLIC_SEAL.json';mp=d/'OOD256_PRIVATE_MEMBERSHIP.json'
    wp=d/'OOD256_PRIVATE_WINDOWS.npz';raw=d/'wikitext2_raw_train_pinned.parquet'
    for p in (pp,mp,wp,raw):need(p.is_file() and not p.is_symlink(),'MISSING_OR_LINK_'+p.name)
    pub=json.loads(pp.read_text('utf-8'));man=json.loads(mp.read_text('utf-8'))
    need(sha(raw)==WIKI and pub['parquet_sha256']==WIKI and man['parquet_sha256']==WIKI,'CORPUS_SHA')
    need(pub['t1_bpe_manifest_sha256']==BPE and man['t1_bpe_manifest_sha256']==BPE,'BPE_SHA')
    need(pub['private_membership_sha256']==sha(mp),'MEMBERSHIP_SHA')
    need(pub['private_windows_sha256']==sha(wp),'WINDOWS_SHA')
    need(pub['status']=='SEALED_SOURCE_ONLY_NOT_SCORED' and pub['science_executed'] is False and pub['model_forward_calls']==0,'NO_SCIENCE')
    need(pub['selected_articles']==man['selected_count']==256 and pub['selected_windows']==512 and pub['scored_targets_total']==man['scored_targets_total']==131072,'COUNTS')
    records=man['selected'];need(len(records)==256,'RECORDS')
    keys=[r['text_sha256'] for r in records];need(len(set(keys))==256,'DUPLICATE_MEMBERSHIP')
    ranks=[(r['rank_sha256'],r['text_sha256']) for r in records];need(ranks==sorted(ranks),'RANK_ORDER')
    need(all(r['bpe_total_tokens']>=513 for r in records),'TOKENS_TOO_SHORT')
    with np.load(wp,allow_pickle=False) as data:
        need(set(data.files)=={'x','y','story_index','count'},'PACK_KEYS')
        x=data['x'];y=data['y'];si=data['story_index'];counts=data['count']
    need(x.shape==y.shape==(512,256) and si.shape==counts.shape==(512,),'PACK_SHAPE')
    need((x>=0).all() and (x<2048).all() and (y>=0).all() and (y<2048).all(),'IDS_RANGE')
    need((counts==256).all() and int(counts.sum())==131072,'TARGET_COUNT')
    need(np.array_equal(si,np.repeat(np.arange(256,dtype=np.int32),2)),'DOCUMENT_SEQUENCE')
    need(np.array_equal(x[:,1:],y[:,:-1]),'SHIFTED_LABELS')
    need(np.array_equal(y[::2,-1],x[1::2,0]),'CONTIGUOUS_WINDOWS')
    need(pub['median_bpe_tokens_per_whitespace_word']<=4.0,'FRAGMENTATION_GATE')
    print('TTM_GEMMA2_OOD_INDEPENDENT_CPU_QA=PASS_SCOPED_NO_FORWARD')
    print('TTM_GEMMA2_OOD_DOCS=256; WINDOWS=512; LABELS=131072')
    print('TTM_GEMMA2_OOD_PUBLIC_SEAL_SHA256='+sha(pp))
    print('TTM_GEMMA2_OOD_SCIENCE=NOT_EXECUTED; GPU=0; TRAINING=0')
if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('--repo',required=True)
    a=p.parse_args();main(a.repo)
