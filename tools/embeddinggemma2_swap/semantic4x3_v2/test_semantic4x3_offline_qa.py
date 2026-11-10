"""Synthetic offline negative/positive QA. Never reads user holdout or executes science."""
from __future__ import annotations
import importlib.util
from argparse import Namespace
from pathlib import Path
import tempfile
import json
import numpy as np
import pytest

ROOT=Path(__file__).resolve().parent

def load(file,name):
    spec=importlib.util.spec_from_file_location(name,ROOT/file)
    mod=importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod

r=load('ttm_semantic4x3_runner.py','semantic4x3_runner_qa')
i=load('ttm_semantic4x3_independent_readback.py','semantic4x3_reviewer_qa')

def samples():
    counts=np.full(768,243,dtype=np.int64);counts[:31]+=1
    arrays={}
    for seed in r.SEEDS:
        base=np.linspace(1,2,768)*counts
        arrays[seed]={'PT-REAL':base,'PT-PERM':base+.1*counts,'NULL-REAL':base+.05*counts,'NULL-PERM':base+.07*counts}
    return counts,arrays

def test_contract_dimensions_and_budget():
    assert 4*3*r.STEPS*r.TARGETS==100663296
    assert len(r.SEEDS)==3 and len(r.ARMS)==4 and r.EVERY==256
    assert len(r.H768_PINS)==3 and len(r.PINS)==7
    assert r.MIN_WITH_HEADROOM>=6*(1024**3)

def test_3_seed_schedule_deterministic_and_distinct():
    counts=np.array([32,43,256,10],dtype=np.int64)
    shas=[]
    for s,settings in r.SEEDS.items():
        a,h=r.schedule(counts,settings['schedule'],steps=6,targets=4096)
        b,j=r.schedule(counts,settings['schedule'],steps=6,targets=4096)
        assert a==b and h==j and all(sum(x[1])==4096 for x in a)
        shas.append(h)
    assert len(set(shas))==3

def test_cross_implementation_scientific_metrics():
    c,loss=samples()
    n,d,b,v=r.compute_science(loss,c)
    per={'loss_sum_by_seed_arm':{s:{a:x.tolist() for a,x in loss[s].items()} for s in loss}}
    n2,d2,b2,v2=i.delta_verify(per,c)
    assert v==v2=='PASS_SCOPED_DONOR_RESIDUAL_STRUCTURE'
    i.check_result({'candidate_verdict':v,'nll_nats_per_target':n,'contrasts_by_seed':d,'co_primary':b},n2,d2,b2,v2)
    assert b['tau_residual']['mean_delta_nll']>.07 and b['gamma_real']['mean_delta_nll']>.04

def test_scientific_failure_is_not_hold():
    c,loss=samples()
    loss['S3']['NULL-REAL']=loss['S3']['PT-REAL']-.1*c
    assert r.compute_science(loss,c)[-1]=='DONOR_RESIDUAL_SIGNAL_NOT_ESTABLISHED_SCOPED_FAIL'

def test_manual_execution_not_authorized_cannot_claim():
    with tempfile.TemporaryDirectory() as tmp:
        a=Namespace(mode='execute',owner_science_approved=False)
        with pytest.raises(RuntimeError,match='HOLD_OWNER_SCIENCE_APPROVAL'):
            r.execute(a)
        assert list(Path(tmp).iterdir())==[]

def test_exclusive_claim_no_overwrite():
    with tempfile.TemporaryDirectory() as tmp:
        p=Path(tmp)/'CLAIM.json'
        orig=r.newjson(p,{'schema':'fixture','claimed':True})
        with pytest.raises(FileExistsError):r.newjson(p,{'schema':'changed'})
        assert r.sha_file(p)==orig

def test_post_training_h768_forbidden_without_12_final_ready():
    with tempfile.TemporaryDirectory() as tmp:
        ctx=tuple([None]*14)
        with pytest.raises(RuntimeError,match='HOLD_ALL_12_FINAL_READY_REQUIRED'):
            r.post_train(Path(tmp),{'runner_sha256':'synthetic'},ctx)
        assert not (Path(tmp)/'SCORING_START.json').exists()

def test_unfinished_chunk_fail_closed_no_replay():
    with tempfile.TemporaryDirectory() as tmp:
        root=Path(tmp)
        folder=root/'S1'/'checkpoints'/'PT-REAL'
        folder.mkdir(parents=True)
        (folder/'CHUNK_0256_START.json').write_text('{}')
        with pytest.raises(RuntimeError,match='HOLD_UNFINISHED_CHUNK_NO_REPLAY'):
            r.resume_state(root,'S1','PT-REAL',None,None,{},{} )

def test_missing_private_h768_fails_source_pin():
    with tempfile.TemporaryDirectory() as tmp:
        root=Path(tmp)
        for k in r.H768_PINS: (root/k).write_bytes(b'invalid')
        with pytest.raises(Exception):r.load_h768_seal(root)

def test_review_detects_tampered_confidence_interval():
    c,loss=samples()
    n,d,b,v=r.compute_science(loss,c)
    result={'candidate_verdict':v,'nll_nats_per_target':n,'contrasts_by_seed':d,
        'co_primary':json.loads(json.dumps(b))}
    result['co_primary']['tau_residual']['ci95_percentile'][1]+=0.1
    with pytest.raises(RuntimeError,match='HOLD_INDEPENDENT_NUMERIC'):
        i.check_result(result,n,d,b,v)

def test_h768_score_not_invoked_in_preflight_source():
    import ast
    src=(ROOT/'ttm_semantic4x3_runner.py').read_text()
    tree=ast.parse(src)
    funcs={n.name:n for n in tree.body if isinstance(n,ast.FunctionDef)}
    calls=lambda fn:[n.func.id for n in ast.walk(funcs[fn]) if isinstance(n,ast.Call) and isinstance(n.func,ast.Name)]
    assert 'load_h768_for_score' in calls('post_train')
    assert 'load_h768_for_score' not in calls('study_preflight')
    assert 'load_h768_seal' in calls('study_preflight')
    assert 'post_train' not in calls('fixture')
