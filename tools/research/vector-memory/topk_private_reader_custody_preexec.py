#!/usr/bin/env python3
"""Owner-local READ-ONLY SHA lock and structure QA for L0020 Reader private.pt.

Never evaluates Reader, scores PROBE/DEV/TEST, trains, or opens checkpoint P02.
Original Reader source (Git blob pinned) is imported solely for state shapes.
"""
from __future__ import annotations
import argparse
import hashlib
import json
from pathlib import Path
import torch
import oracle_reader_source_only as base
import topk_reader_integration as new

EXPECTED_ORIGINAL_READER='7ce728b2874284b87933237c890e54ce3d9fd651'
EXPECTED_INTEGRATION='ccab713f8c5a4b913259088225daffcf5382be41'
EXPECTED_PROBE='b08e2120a2ac9d4e270ee48fdca77e4a4743e22c'
RUN_ID='TTM_VM_EXTERNAL_FACTS_CPU_ORACLE_TRAIN_DEV_20261111_V1'

def hash_file(p:Path):
    h=hashlib.sha256()
    with p.open('rb') as f:
        for part in iter(lambda:f.read(1024*1024),b''):h.update(part)
    return h.hexdigest()

def gitblob(p:Path):
    b=p.read_bytes()
    return hashlib.sha1(b'blob '+str(len(b)).encode()+b'\0'+b).hexdigest()

def main():
    ap=argparse.ArgumentParser(description=__doc__)
    ap.add_argument('--project-root',type=Path,required=True)
    ap.add_argument('--checkout',type=Path,required=True)
    ap.add_argument('--out',type=Path,required=True)
    args=ap.parse_args()
    root=args.project_root.resolve(strict=True)
    checkout=args.checkout.resolve(strict=True)
    if not checkout.is_relative_to(root):raise ValueError('RESEARCH_CHECKOUT_OUTSIDE_ROOT')
    src_dir=checkout/'tools/research/vector-memory'
    expected={'oracle_reader_source_only.py':EXPECTED_ORIGINAL_READER,
              'topk_reader_integration.py':EXPECTED_INTEGRATION,
              'topk_nontest_probe.py':EXPECTED_PROBE}
    for filename,sha in expected.items():
        if gitblob(src_dir/filename)!=sha:raise ValueError('SOURCE_BLOB_NOT_PINNED:'+filename)
    private=root/'_evidence'/'vector-memory'/RUN_ID/'reader_private.pt'
    private=private.resolve(strict=True)
    if not private.is_relative_to(root):raise ValueError('PRIVATE_READER_OUTSIDE_ROOT')
    source_sha=hash_file(private)
    # This is metadata readback, not a Reader forward or a science evaluation.
    payload=torch.load(str(private),map_location='cpu',weights_only=True)
    fresh=base.GatedOracleReader().cpu().eval()
    identity=new.validate_l0020_private_payload(payload,fresh)
    out=args.out.resolve()
    if not out.is_relative_to(root):raise ValueError('RECEIPT_OUTSIDE_ROOT')
    if out.exists():raise FileExistsError('REFUSE_CUSTODY_RECEIPT_OVERWRITE')
    output={
      'schema':'ttm.vm.topk.l0020_reader.private_readonly_custody.v1',
      'status':'PASS_PRIVATE_READER_SHA_AND_STRUCTURE_READBACK',
      'reader_sha256':source_sha,
      'source_state':'L0020_FROZEN_READER_FINAL_STEP128',
      'source_run_id':RUN_ID,
      'private_reader_size_bytes':private.stat().st_size,
      'metadata':identity,
      'input_source_git_blobs':expected,
      'forward_calls':0,'optimizer_steps':0,'dev_scored':False,
      'probe_scored':False,'test_opened':False,'gpu_used':False,
      'owner_local_private_weights_not_exported':True,
      'subsequent_state':'HOLD_UNTIL_FROZEN_TOPK_PROBE_SCIENCE_EXECUTION_SEPARATE_RELEASE',
      'lineage_change':'NONE_TECHNICAL_READBACK_ONLY'
    }
    out.parent.mkdir(parents=True,exist_ok=True)
    out.write_text(json.dumps(output,sort_keys=True,indent=2)+'\n',encoding='utf-8')
    print('PRIVATE_READER_SHA256='+source_sha)
    print('PRIVATE_READER_TENSORS='+str(identity['tensor_count']))
    print('PRIVATE_READER_SOURCE_STRUCTURE=PASS')
    print('TRAINING_INFERENCE_TEST=NOT_EXECUTED')
    print('QA_RECEIPT='+str(out))

if __name__=='__main__':main()
