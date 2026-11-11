#!/usr/bin/env python3
"""Optional future CPU DEV-only frozen-O0 scorer, not invoked by this readiness task.

Hard fences: exact public DEV input SHA, exact P02 blob, 1024 weights SHA,
exact T1 BPE, no optimizer, no FINAL and no TEST/Q1Q2.
"""
from __future__ import annotations
import argparse,hashlib,json,os,sys
from pathlib import Path
HERE=Path(__file__).resolve().parent
sys.path.insert(0,str(HERE))
from cf1_teacher_forced_scorer import load_model_inputs,load_frozen_p02,score_pair,sha_file
from cf1_exact_t1_bpe import PinnedT1BPE
DEV_SHA='81e9849226029a1cb017c87da4202347be42dc92039db8c0d430d7115b68b4ed'

def new_json(path,obj):
    path=Path(path)
    with path.open('x',encoding='utf8') as f:
        json.dump(obj,f,sort_keys=True,indent=2);f.write('\n');f.flush();os.fsync(f.fileno())

def main():
    ap=argparse.ArgumentParser()
    ap.add_argument('--p02',required=True)
    ap.add_argument('--checkpoint',required=True)
    ap.add_argument('--t1-manifest',required=True)
    ap.add_argument('--dev-model-input',required=True)
    ap.add_argument('--out',required=True)
    ap.add_argument('--allow-frozen-o0-dev-only',action='store_true',help='Explicit read-only DEV evaluation request; not FINAL')
    args=ap.parse_args()
    out=Path(args.out)
    if out.exists():raise FileExistsError('REFUSE_EXISTING_RESULT_ONE_SHOT')
    if not args.allow_frozen_o0_dev_only:
        print('CF1_O0_NEURAL_EVAL=HOLD_ONLY_SOURCE_PREFLIGHT');return
    src=Path(args.dev_model_input)
    if sha_file(src)!=DEV_SHA:raise RuntimeError('DEV_SHA256_DIFFERS_FROM_PINNED')
    data=load_model_inputs(src.read_bytes())
    if len(data)!=36:raise RuntimeError('EXPECTED_36_DEV_PAIRS')
    tok=PinnedT1BPE(args.t1_manifest)
    model=load_frozen_p02(Path(args.p02),Path(args.checkpoint))
    r=[]
    for row in data:r.append(score_pair(model,tok.encode,row))
    output={'schema':'ttm.cf1.readonly_frozen_o0_dev_scores.v1',
            'status':'DEV_SCORES_ONLY_REQUIRES_OWNER_ADJUDICATION',
            'dataset_sha256':DEV_SHA,'checkpoint_sha256':sha_file(args.checkpoint),
            'scored_pairs':len(r),'scores':r,
            'oracle_labels_used_in_prediction':False,
            'FINAL_opened':False,'TTM_Q1Q2_TEST_read':False,'optimizer_updates':0,'GPU_calls':0}
    new_json(out,output)
    print('CF1_READONLY_DEV_SCORES_READY=36; NO_FINAL_OR_TRAINING')

if __name__=='__main__':main()
