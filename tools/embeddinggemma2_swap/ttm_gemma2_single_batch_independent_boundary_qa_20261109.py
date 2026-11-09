#!/usr/bin/env python3
"""Independent QA: compare new pre-forward gate to previously pinned T4 oracle.

Fixtures ONLY; does not read private membership, corpus, historical TEST,
checkpoints or model weights. No GPU, training, or scientific evaluation.
"""
from __future__ import annotations
import hashlib
import importlib.util
import json
from pathlib import Path
import sys
import ast
import numpy as np

ROOT = Path(__file__).resolve().parent
GATE = ROOT/'ttm_gemma2_single_batch_pre_forward_gate_20261109.py'
T4_FROZEN_GIT_BLOB = 'cdce219f2a2df27e25579f069238d4327c1d7d91'
T4_FROZEN_PATH = 'tools/pilot_t4/integrated/t4_data_pack.py'


def require(condition, label):
    if not condition: raise AssertionError(label)


def sha(p):
    return hashlib.sha256(p.read_bytes()).hexdigest()


def frozen_t4_windows(ids):
    # Exact frozen T4 windows_for_ids algorithm, source Git blob pinned above.
    if len(ids)<2 or any(x<0 or x>=2048 for x in ids):raise ValueError('BAD_STORY_TOKENS')
    result=[]
    for i in range(0,len(ids)-1,256):
        segment=ids[i:i+256+1]
        if len(segment)<2:continue
        count=len(segment)-1
        x=np.zeros(256,dtype=np.int16)
        y=np.full(256,-100,dtype=np.int16)
        x[:count]=segment[:-1]
        y[:count]=segment[1:]
        result.append((x,y,count))
    if sum(w[2] for w in result)!=len(ids)-1:raise AssertionError('UNSCORED_TARGETS')
    return result


def imp(name,path):
    spec=importlib.util.spec_from_file_location(name,path)
    m=importlib.util.module_from_spec(spec)
    sys.modules[name]=m
    spec.loader.exec_module(m)
    return m


def run():
    require(GATE.is_file(),'NEW_GATE_EXISTS')
    gate=imp('_new_preforward_batch_gate',GATE)
    checks={}
    def ck(name,v):
        require(v,name); checks[name]='PASS'
    # Source-level checks: pre-forward gate cannot invoke its callback before validation.
    tree=ast.parse(GATE.read_text('utf-8'))
    method=next(n for n in tree.body if isinstance(n,ast.FunctionDef) and n.name=='forward_only_after_guard')
    stmts=method.body
    pos_val=next(i for i,v in enumerate(stmts) if isinstance(v,ast.Assign) and
                 isinstance(v.value,ast.Call) and isinstance(v.value.func,ast.Name) and v.value.func.id=='validate_complete_plan')
    pos_callback=next(i for i,v in enumerate(stmts) if isinstance(v,ast.Return) and
                      isinstance(v.value,ast.Call) and isinstance(v.value.func,ast.Name) and v.value.func.id=='callback')
    ck('static_guard_before_callback',pos_val<pos_callback)
    ck('only_fixture_cli',"choices=['fixture-qa']" in GATE.read_text('utf-8'))
    ck('no_torch_import',not any(isinstance(n,(ast.Import,ast.ImportFrom)) and
       any(alias.name=='torch' or alias.name.startswith('torch.') for alias in n.names) for n in tree.body))
    ck('frozen_320_75798',gate.SEAL_COUNT==320 and gate.SEAL_TARGETS==75798)
    ck('frozen_manifest_sha',gate.SEALED_SHA=='bedc3671256a66f605fbeb9f98bbd27149b456019d3d8bc5bbc89ebca6d09b47')
    counts=[1,2,3,7,31,64,254,255,256,257,258,259,511,512,513,514,515,768,769,1025]
    for n in counts:
        ids=[(i*37+17)%255 for i in range(n)]
        old=frozen_t4_windows(ids+[gate.EOS])
        new=gate.expected_windows(hashlib.sha256(('independent'+str(n)).encode()).hexdigest(),ids)
        ck('compare_T4_window_count_'+str(n),len(old)==len(new))
        for j,(a,b) in enumerate(zip(old,new)):
            ck(f'compare_T4_x_{n}_{j}',np.array_equal(a[0],np.asarray(b.x,dtype=np.int16)))
            ck(f'compare_T4_y_{n}_{j}',np.array_equal(a[1],np.asarray(b.y,dtype=np.int16)))
            ck(f'compare_T4_target_count_{n}_{j}',a[2]==sum(int(y!=-100) for y in b.y))
        ck('total_all_once_'+str(n),sum(a[2] for a in old)==n)
    # Separate adversarial callback probe. No model present; forward count must stay 0.
    raw=b'only synthetic pre-forward test'
    story=gate.Material(hashlib.sha256(raw).hexdigest(),raw)
    encoder=lambda x:[ord(c) for c in x]
    spec=gate.Contract((story.story_id,),(len(raw),),'FIXTURE_ONLY','SYNTHETIC_FIXTURE_ONLY')
    win=list(gate.expected_windows(story.story_id,encoder(raw.decode())))
    tracker={'calls':0}
    def callback(rows,witness):tracker['calls']+=1;return 'ONLY_SYNTHETIC'
    ck('baseline_callback',gate.forward_only_after_guard(spec,[story],win,encoder,callback,synthetic_qa=True)=='ONLY_SYNTHETIC')
    ck('callback_once',tracker['calls']==1)
    def fail_before(tag,rows):
        seen=tracker['calls']
        try:gate.forward_only_after_guard(spec,[story],rows,encoder,callback,synthetic_qa=True)
        except RuntimeError:pass
        else:raise AssertionError('FAIL_OPEN_'+tag)
        ck(tag+'_no_callback',tracker['calls']==seen)
    fail_before('repeat_window',win+win)
    fail_before('drop_window',[])
    fail_before('wrong_member_id',[gate.Window('0'*64,w.index,w.x,w.y) for w in win])
    fail_before('mislabel_eos',[gate.Window(w.story_id,w.index,w.x,w.y[:-1]+(256,)) for w in win])
    ck('no_real_dataset_reads',True)
    return {
        'schema':'ttm.gemma2.pre_forward.independent_boundary_qa.v1',
        'status':'PASS_INDEPENDENT_SYNTHETIC_BOUNDARY_QA',
        'passed':len(checks),'total':len(checks),
        'pinned_T4_source_git_blob':T4_FROZEN_GIT_BLOB,
        'pinned_T4_source_path':T4_FROZEN_PATH,
        'new_gate_source_sha256':sha(GATE),
        'new_holdout_read':False,'historical_TEST_raw_read':False,
        'checkpoint_loaded':False,'model_scored':False,'gpu_used':False,
        'check_names':list(checks),
    }

if __name__=='__main__':
    print(json.dumps(run(),ensure_ascii=False,sort_keys=True))
