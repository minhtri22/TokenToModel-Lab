#!/usr/bin/env python3
"""Fail-closed READY-last checkpoint store for TTM A/C candidate; no model forward.

A READY marker is written only after the full checkpoint bytes have been fsynced.
Never overwrites an existing checkpoint or READY marker. Orphan/corrupt files HOLD.
"""
from __future__ import annotations
import hashlib, json, os, re
from pathlib import Path

START=1024
END=1152
INTERVAL=32
STEPS=tuple(range(START+INTERVAL, END+1, INTERVAL))
ARMS=('A','C')

def sha256_file(p):
    h=hashlib.sha256()
    with Path(p).open('rb') as f:
        for chunk in iter(lambda:f.read(1024*1024),b''):
            h.update(chunk)
    return h.hexdigest()

def ensure(ok, code):
    if not ok:
        raise RuntimeError(code)

def _names(root, step):
    return root/f'step_{step}.pt',root/f'READY_{step}.json'

def _scope(run_id,arm,source_sha,parent_sha,lock_sha):
    ensure(arm in ARMS,'INVALID_ARM')
    ensure(isinstance(run_id,str) and run_id.startswith('TTM_SMALL4M_AC_'),'INVALID_RUN_ID')
    pins={'source_sha256':source_sha,'parent_sha256':parent_sha,'owner_lock_sha256':lock_sha}
    ensure(all(isinstance(v,str) and re.fullmatch('[0-9a-f]{64}',v) for v in pins.values()),'INVALID_SHA_PIN')
    return {'run_id':run_id,'arm':arm,**pins}

def save_ready(root,step,state,run_id,arm,source_sha,parent_sha,lock_sha):
    """Durable checkpoint + READY only at an exact 32-step boundary."""
    import torch
    root=Path(root)
    scope=_scope(run_id,arm,source_sha,parent_sha,lock_sha)
    ensure(root.is_dir() and not root.is_symlink(),'NOT_AN_EXISTING_ARM_DIRECTORY')
    ensure(step in STEPS and isinstance(state,dict) and state.get('step')==step,'BAD_READY_STEP')
    ensure(state.get('run_id')==run_id and state.get('arm')==arm,'BAD_READY_STATE_IDENTITY')
    ck,ready=_names(root,step)
    ensure(not ck.exists() and not ready.exists(),'READY_ALREADY_EXISTS_NO_OVERWRITE')
    with ck.open('xb') as fp:
        torch.save(state,fp)
        fp.flush();os.fsync(fp.fileno())
    cksha=sha256_file(ck)
    record={**scope,'step':step,'checkpoint_sha256':cksha,'checkpoint_bytes':ck.stat().st_size,
            'history_length':len(state.get('history',[])),'schema':'ttm.small4m.ac.ready_last.v1'}
    ensure(record['history_length']==step-START,'READY_HISTORY_LENGTH_INVALID')
    with ready.open('x',encoding='utf-8') as fp:
        json.dump(record,fp,sort_keys=True,separators=(',',':'))
        fp.write('\n');fp.flush();os.fsync(fp.fileno())
    return record

def load_latest(root,run_id,arm,source_sha,parent_sha,lock_sha):
    """Verify all previous markers, reject orphan step files or interrupted markers.

    Returns (last_step, state, receipt); 1024/None/None on an untouched empty arm.
    """
    import torch
    root=Path(root)
    scope=_scope(run_id,arm,source_sha,parent_sha,lock_sha)
    ensure(root.is_dir() and not root.is_symlink(),'MISSING_ARM_DIRECTORY')
    known={f'step_{step}.pt' for step in STEPS}|{f'READY_{step}.json' for step in STEPS}
    seen={p.name for p in root.iterdir()}
    ensure(not any(x.startswith(('step_','READY_')) and x not in known for x in seen),'UNKNOWN_CHECKPOINT_OR_MARKER')
    last=START;state=None;receipt=None;gap=False
    for step in STEPS:
        ck,ready=_names(root,step)
        a,b=ck.exists(),ready.exists()
        ensure(a==b,'ORPHAN_CHECKPOINT_OR_READY_MARKER')
        ensure(not (gap and a),'NONCONTIGUOUS_READY_HISTORY')
        if not a:
            gap=True;continue
        ensure(ck.is_file() and ready.is_file() and not ck.is_symlink() and not ready.is_symlink(),'UNTRUSTED_READY_PATH')
        record=json.loads(ready.read_text('utf-8'))
        ensure(all(record.get(k)==v for k,v in scope.items()),'READY_SCOPE_MISMATCH')
        ensure(record.get('step')==step and record.get('schema')=='ttm.small4m.ac.ready_last.v1','READY_SCHEMA_OR_STEP_INVALID')
        ensure(ck.stat().st_size==record.get('checkpoint_bytes') and sha256_file(ck)==record.get('checkpoint_sha256'),'READY_CHECKPOINT_SHA_MISMATCH')
        st=torch.load(ck,map_location='cpu',weights_only=True)
        ensure(isinstance(st,dict) and st.get('step')==step and st.get('run_id')==run_id and st.get('arm')==arm,'READY_STATE_MISMATCH')
        ensure(len(st.get('history',[]))==step-START==record.get('history_length'),'READY_HISTORY_MISMATCH')
        last=step;state=st;receipt=record
    return last,state,receipt
