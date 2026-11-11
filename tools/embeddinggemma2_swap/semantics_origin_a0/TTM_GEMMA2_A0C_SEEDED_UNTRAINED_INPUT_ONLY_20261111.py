#!/usr/bin/env python3
"""A0C controlled, source-pinned EmbeddingGemma2 INPUT-ONLY nonpretrained table.

NOT a full randomly initialized 24-layer model; NOT mapped to T1 tokens;
NOT a pretrained origin causal result. Never trains or runs LM inference.
"""
from __future__ import annotations
import argparse, hashlib, json, sys
from pathlib import Path
import numpy as np
import torch

PIN_CONFIG_SHA='b8f1e9931b57fbc054acdb445c41765d55b0074c58d145fa82839941ad1b5bb3'
PIN_REVISION='f9972ac22e696a105c482202646979e33e4b5a1e'
SEED=2026111173
V,H=262144,512
STD=0.02
PAD_ID=0

def check(ok,reason):
    if not bool(ok): raise RuntimeError('A0C_HOLD_'+reason)

def filehash(p):
    h=hashlib.sha256()
    with open(p,'rb') as f:
        for chunk in iter(lambda:f.read(8*1024*1024),b''):h.update(chunk)
    return h.hexdigest()

def make_table():
    g=torch.Generator(device='cpu').manual_seed(SEED)
    t=torch.empty((V,H),dtype=torch.float32,device='cpu')
    torch.nn.init.trunc_normal_(t,mean=0.0,std=STD,a=-2*STD,b=2*STD,generator=g)
    t[PAD_ID].zero_()
    check(t.shape==(V,H) and t[PAD_ID].abs().max().item()==0,'SHAPE_OR_PAD')
    check(torch.isfinite(t).all().item(),'FINITE')
    return t

def run(output):
    check(sys.byteorder=='little','ENDIAN')
    check(not output.exists(),'NO_OVERWRITE')
    t=make_table()
    arr=t.numpy()
    with output.open('wb') as f: np.save(f,arr,allow_pickle=False)
    digest=filehash(output)
    read=np.load(output,mmap_mode='r',allow_pickle=False)
    check(read.shape==(V,H) and read.dtype==np.float32 and read[0].max()==0 and read[0].min()==0,'READBACK')
    # Rerun the same initialization without using original table or file.
    del t,arr,read
    t2=make_table()
    h=hashlib.sha256()
    for row in t2.numpy():h.update(row.tobytes(order='C'))
    raw_digest=h.hexdigest()
    # Hash raw bytes independently from disk without loading all 512 MiB.
    read=np.load(output,mmap_mode='r',allow_pickle=False)
    h=hashlib.sha256()
    for i in range(0,V,2048):h.update(np.asarray(read[i:i+2048]).tobytes(order='C'))
    check(h.hexdigest()==raw_digest,'SECOND_SEED_REPRODUCTION')
    report={'schema':'ttm.embeddinggemma2.a0c.untrained_input_only.seeded_source.v1',
            'status':'INPUT_ONLY_SEEDED_SOURCE_REPRODUCED_FULL_MODEL_NOT_CLAIMED',
            'hf_repository':'google/embeddinggemma-2',
            'pinned_model_revision':PIN_REVISION,
            'pinned_original_config_sha256':PIN_CONFIG_SHA,
            'text_config_model_type':'embedding_gemma2_text',
            'text_config_num_hidden_layers':24,'vocab_size':V,'hidden_size':H,
            'initializer_range':STD,'padding_idx':PAD_ID,
            'init_operator':'torch.nn.init.trunc_normal_(mean=0, std=0.02, a=-0.04,b=0.04)',
            'seed':SEED,'torch_version':torch.__version__,'numpy_version':np.__version__,
            'dtype':'<f4','npy_bytes':output.stat().st_size,'npy_sha256':digest,
            'raw_f32le_sha256':raw_digest,'independent_regeneration_match':True,
            'complete_24_layer_untrained_backbone_constructed':False,
            'identical_to_transformers_post_init_not_established':True,
            'donor_tokenizer_mapping_constructed':False,
            'new_training':False,'model_forward':False,'evaluation_loss':False,
            'can_claim_pretrained_semantic_causality':False}
    print(json.dumps(report,ensure_ascii=False,sort_keys=True))
    return report

if __name__=='__main__':
    ap=argparse.ArgumentParser();ap.add_argument('--output',required=True)
    args=ap.parse_args()
    run(Path(args.output))
