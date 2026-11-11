#!/usr/bin/env python3
"""Read-only actual step-1024 checkpoint CPU fixture, NOT DEV/FINAL model evaluation.

The P02 class used here is an independently reconstructed algebraic-equivalent
smoke implementation from prior N1; exact Git blob source loader remains
available in cf1_teacher_forced_scorer.py for future official scoring.
"""
from __future__ import annotations
from pathlib import Path
import hashlib,importlib.util,json,sys,torch,math,argparse
from torch import nn
HERE=Path(__file__).resolve().parent
sys.path.insert(0,str(HERE))
from cf1_teacher_forced_scorer import sha_file,PARENT_SHA,validate_parent_checkpoint,score_pair
# The equivalent source is supplied explicitly; no external fixed machine path.

def main():
    ap=argparse.ArgumentParser();ap.add_argument('--checkpoint',required=True);ap.add_argument('--n1-equivalent-source',required=True);ap.add_argument('--out',required=True);cli=ap.parse_args()
    cpfile=Path(cli.checkpoint);P=Path(cli.n1_equivalent_source)
    torch.set_num_threads(2)
    orig_sha=sha_file(cpfile)
    assert orig_sha==PARENT_SHA
    cp=validate_parent_checkpoint(cpfile)
    sp=importlib.util.spec_from_file_location('p02_equivalent_smoke_n1',P)
    mod=importlib.util.module_from_spec(sp);sys.modules[sp.name]=mod;sp.loader.exec_module(mod)
    m=mod.GPT(mod.P02Config(**cp['config']))
    m.load_state_dict(cp['model'],strict=True)
    assert sum(p.numel() for p in m.parameters())==3749376
    m.to('cpu').eval()
    for p in m.parameters():p.requires_grad_(False)
    fingerprint=hashlib.sha256(b''.join(p.detach().cpu().numpy().tobytes() for p in m.parameters())).hexdigest()
    row={'context_a':'Ada was given the card.','context_b':'Bea was given the card.',
         'completion_x':' Ada won.','completion_y':' Bea won.'}
    def byte_encoder(s):return list(s.encode('ascii'))
    with torch.inference_mode():
        a=score_pair(m,byte_encoder,row)
        b=score_pair(m,byte_encoder,row)
    assert all(math.isfinite(a[k]) for k in ('L_a_x','L_a_y','L_b_x','L_b_y'))
    assert a==b
    assert not any(p.grad is not None for p in m.parameters())
    assert fingerprint==hashlib.sha256(b''.join(p.detach().cpu().numpy().tobytes() for p in m.parameters())).hexdigest()
    assert sha_file(cpfile)==orig_sha
    r={'schema':'ttm.cf1.frozen_parent_equivalent_cpu_fixture_source_qa.v1',
       'status':'PASS_8_OF_8_SOURCE_AND_SYNTHETIC_FIXTURE_ONLY',
       'checks':['checkpoint_SHA256','checkpoint_p02_step_config_pin','strict_state_dict','parameter_count_3749376',
                 'four_teacher_forced_scores_finite','repeat_deterministic','frozen_weights_unmodified','original_checkpoint_sha_unchanged'],
       'runtime':'CPU_PYTORCH_'+str(torch.__version__),
       'checkpoint_sha256':orig_sha,'checkpoint_step':1024,'model_params':3749376,
       'P02_source_for_fixture':'N1 algebraically equivalent CPU reconstruction, not exact src/p02/transformer_core.py blob',
       'future_official_scorer_requires_exact_P02_blob':True,
       'tokenizer_in_fixture':'ASCII_BYTES_ONLY_NOT_T1_BPE2048',
       'DEV_and_FINAL_neural_scores_executed':0,
       'new_training_steps':0,'gpu_calls':0,'Q1Q2_TEST_reads':0}
    out=Path(cli.out);out.write_text(json.dumps(r,indent=2,sort_keys=True)+'\n')
    print(r['status'])
if __name__=='__main__':main()
