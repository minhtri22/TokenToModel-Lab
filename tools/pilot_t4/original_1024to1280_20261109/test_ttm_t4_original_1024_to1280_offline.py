#!/usr/bin/env python3
"""Independent synthetic CPU verification; never touches real checkpoint or GPU."""
from __future__ import annotations
import copy
import importlib.util
import json
from pathlib import Path
import random
import tempfile
import unittest
from unittest.mock import patch

import numpy as np
import torch

FILE=Path(__file__).with_name('ttm_t4_original_1024_to1280.py')
spec=importlib.util.spec_from_file_location('ttm_t4_1024_1280_test_target',FILE)
m=importlib.util.module_from_spec(spec)
spec.loader.exec_module(m)


class ScalerFixture:
    def __init__(self): self.state={'scale': 2048, 'growth_tracker': 12}
    def state_dict(self): return copy.deepcopy(self.state)
    def load_state_dict(self, state): self.state=copy.deepcopy(state)


def fake_parent(root: Path):
    folder = root/'step_1024'
    folder.mkdir()
    model=torch.nn.Linear(2,2)
    opt=torch.optim.AdamW(model.parameters(),lr=3e-4,betas=(.9,.95),eps=1e-8,weight_decay=.1)
    sch=torch.optim.lr_scheduler.LambdaLR(opt,lr_lambda=lambda step:.1)
    opt.zero_grad()
    model(torch.ones(1,2)).sum().backward()
    opt.step()
    for item in opt.state.values(): item['step'].fill_(1024)
    opt.param_groups[0]['lr']=3e-5
    sch.last_epoch=1024
    sch._last_lr=[3e-5]
    sampler=torch.Generator().manual_seed(17)
    log=[{'step':i,'exact_scored_targets':4096,'train_loss':5.0} for i in range(1,1025)]
    prog={'schema':'ttm.t4.progress.v1','step':1024,'records':log}
    (folder/'progress.json').write_text(json.dumps(prog),encoding='utf-8')
    npst=np.random.get_state()
    payload={
      'schema':'ttm.t4.science.checkpoint.v1','step':1024,'science_seed':20261108,
      'science_lock_sha256':m.OLD_LOCK_SHA,'train_pack_sha256':m.PACK_SHA,
      'p02_git_blob':m.PINNED_GIT_BLOBS['p02'],'config':m.EXPECTED_CONFIG,
      'device_type':'cuda','grad_scaler_state':ScalerFixture().state_dict(),
      'model':model.state_dict(),'optimizer':opt.state_dict(),
      'scheduler':sch.state_dict(),'sampler_state':sampler.get_state(),
      'torch_cpu_rng':torch.get_rng_state(),'torch_cuda_rng':[torch.get_rng_state()],
      'python_rng':random.getstate(),
      'numpy_rng':(npst[0],npst[1].tolist(),npst[2],npst[3],npst[4])}
    torch.save(payload,folder/'checkpoint.pt')
    ready={'schema':'ttm.t4.ready.last.v1','step':1024,'checkpoint':'checkpoint.pt',
           'bytes':(folder/'checkpoint.pt').stat().st_size,
           'sha256':m.sha_file(folder/'checkpoint.pt'),
           'science_lock_sha256':m.OLD_LOCK_SHA,'train_pack_sha256':m.PACK_SHA,
           'progress_sha256':m.sha_file(folder/'progress.json')}
    (folder/'READY.json').write_text(json.dumps(ready),encoding='utf-8')
    return folder,payload,model,opt,sch,sampler


class T4OriginalContinuationOffline(unittest.TestCase):
    def setUp(self):
        self.temp=tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.folder,self.payload,self.model,self.opt,self.sch,self.sampler=fake_parent(Path(self.temp.name))
        self.patches=[patch.object(m,'PARENT_SHA',m.sha_file(self.folder/'checkpoint.pt')),
                      patch.object(m,'PARENT_PROGRESS_SHA',m.sha_file(self.folder/'progress.json'))]
        for item in self.patches:
            item.start();self.addCleanup(item.stop)

    def rewrite_payload(self):
        torch.save(self.payload,self.folder/'checkpoint.pt')
        digest=m.sha_file(self.folder/'checkpoint.pt')
        ready=json.loads((self.folder/'READY.json').read_text())
        ready['sha256']=digest;ready['bytes']=(self.folder/'checkpoint.pt').stat().st_size
        (self.folder/'READY.json').write_text(json.dumps(ready))
        p=patch.object(m,'PARENT_SHA',digest);p.start();self.addCleanup(p.stop)

    def test_valid_synthetic_ready_and_1024_step_prefix(self):
        ready,log,payload=m.checked_parent(self.folder)
        self.assertEqual(payload['step'],1024)
        self.assertEqual(len(log),1024)
        self.assertEqual(ready['sha256'],m.PARENT_SHA)

    def test_sha_mismatch_fails_closed(self):
        with (self.folder/'checkpoint.pt').open('ab') as f:f.write(b'corruption')
        with self.assertRaisesRegex(RuntimeError,'PARENT_CHECKPOINT_SHA_MISMATCH'):
            m.checked_parent(self.folder)

    def test_progress_sha_mismatch(self):
        with (self.folder/'progress.json').open('ab') as f:f.write(b' ')
        with self.assertRaisesRegex(RuntimeError,'PARENT_PROGRESS_SHA_MISMATCH'):
            m.checked_parent(self.folder)

    def test_parent_lock_mismatch(self):
        r=json.loads((self.folder/'READY.json').read_text())
        r['science_lock_sha256']='0'*64
        (self.folder/'READY.json').write_text(json.dumps(r))
        with self.assertRaisesRegex(RuntimeError,'PARENT_SCIENCE_LOCK_MISMATCH'):
            m.checked_parent(self.folder)

    def test_missing_optimizer_parameter_state(self):
        self.payload['optimizer']['state'].pop(next(iter(self.payload['optimizer']['state'])))
        self.rewrite_payload()
        with self.assertRaisesRegex(RuntimeError,'ADAMW_STATE_MISSING_FOR_PARAMETER'):
            m.checked_parent(self.folder)

    def test_optimizer_state_step_must_equal_1024(self):
        next(iter(self.payload['optimizer']['state'].values()))['step'].fill_(1000)
        self.rewrite_payload()
        with self.assertRaisesRegex(RuntimeError,'ADAMW_STEP_OR_MOMENTS_MISSING'):
            m.checked_parent(self.folder)

    def test_scheduler_step_mismatch(self):
        self.payload['scheduler']['last_epoch']=0
        self.rewrite_payload()
        with self.assertRaisesRegex(RuntimeError,'LAMBDA_SCHEDULER_STEP_MISMATCH'):
            m.checked_parent(self.folder)

    def test_absent_rng_rejected(self):
        self.payload.pop('numpy_rng')
        self.rewrite_payload()
        with self.assertRaisesRegex(RuntimeError,'PARENT_MISSING_STATE:numpy_rng'):
            m.checked_parent(self.folder)

    def test_absent_scaler_rejected(self):
        self.payload['grad_scaler_state']=None
        self.rewrite_payload()
        with self.assertRaisesRegex(RuntimeError,'PARENT_FP16_CUDA_SCALER_MISSING'):
            m.checked_parent(self.folder)

    def test_wrong_data_pack_blocked(self):
        self.payload['train_pack_sha256']='1'*64
        self.rewrite_payload()
        with self.assertRaisesRegex(RuntimeError,'PARENT_PAYLOAD_SOURCE'):
            m.checked_parent(self.folder)

    def test_full_restore_cpu_fixture_no_optimizer_reset(self):
        old_cpu=torch.get_rng_state();old_python=random.getstate();old_np=np.random.get_state()
        self.addCleanup(torch.set_rng_state,old_cpu)
        self.addCleanup(random.setstate,old_python)
        self.addCleanup(np.random.set_state,old_np)
        model2=torch.nn.Linear(2,2)
        opt2=torch.optim.AdamW(model2.parameters(),lr=3e-4,betas=(.9,.95),eps=1e-8,weight_decay=.1)
        sch2=torch.optim.lr_scheduler.LambdaLR(opt2,lr_lambda=lambda step:.1)
        sampler2=torch.Generator().manual_seed(99)
        scaler=ScalerFixture()
        m.restore_full_state(model2,opt2,sch2,sampler2,scaler,self.payload,
                             torch.device('cpu'),allow_cpu_fixture=True)
        m.assert_same(opt2.state_dict(),self.payload['optimizer'],'INDEPENDENT_ADAMW_DIFFERENT')
        m.assert_same(sch2.state_dict(),self.payload['scheduler'],'INDEPENDENT_SCHED_DIFFERENT')
        m.assert_same(sampler2.get_state(),self.payload['sampler_state'],'INDEPENDENT_SAMPLER_DIFFERENT')
        self.assertEqual(float(next(iter(opt2.state.values()))['step']),1024)

    def test_restore_gpu_required_by_default(self):
        with self.assertRaisesRegex(RuntimeError,'RESTORE_REQUIRES_SINGLE_CUDA_GPU'):
            m.restore_full_state(self.model,self.opt,self.sch,self.sampler,ScalerFixture(),
                                 self.payload,torch.device('cpu'))

    def test_no_new_science_lock_no_permission(self):
        with self.assertRaisesRegex(RuntimeError,'NEW_SCIENCE_LOCK_NOT_ISSUED'):
            m.authorized_lock(None,None,FILE,m.PARENT_SHA)

    def test_modified_new_science_lock_rejected(self):
        path=Path(self.temp.name)/'LOCK.json'
        path.write_text('{}',encoding='utf-8')
        with self.assertRaisesRegex(RuntimeError,'NEW_SCIENCE_LOCK_SHA_MISMATCH'):
            m.authorized_lock(path,'a'*64,FILE,m.PARENT_SHA)

    def test_source_blob_rejects_untrusted_file(self):
        with self.assertRaisesRegex(RuntimeError,'SOURCE_GIT_BLOB_MISMATCH:p02'):
            m.checked_paths({'p02':FILE})

    def test_new_output_refuses_overwrite(self):
        p=Path(self.temp.name)/'NEW.json'
        m.json_new(p,{'status':'pass'})
        with self.assertRaises(FileExistsError):m.json_new(p,{'status':'overwrite'})

    def test_schedule_floor_1025_1152_1280(self):
        # Frozen source lambda clamps at t=1 after step 1024; no fresh scheduler.
        from math import cos,pi
        for step in (1024,1025,1152,1280):
            t=min((step-32)/(1024-32),1.0)
            lr=3e-4*(.1+.9*(.5+.5*cos(pi*t)))
            self.assertAlmostEqual(lr,3e-5,places=12)

    def test_val_rejects_non_frozen_cohort(self):
        with self.assertRaisesRegex(RuntimeError,'PAIRED_VAL_INPUT_INVALID'):
            m.paired_val_decision(np.ones(2),np.ones(2),np.ones(2))

    def test_val_rejects_wrong_target_count(self):
        with self.assertRaisesRegex(RuntimeError,'VAL_TARGET_COUNT_CHANGED'):
            m.paired_val_decision(np.ones(256),np.ones(256),np.ones(256))

    def test_paired_bootstrap_positive_signal(self):
        # Fixed synthetic 256-story target counts summing to 61122.
        counts=np.full(256,238,dtype=np.int64)
        counts[:194]+=1  # 256*238 +194 == 61122
        base=counts.astype(float)*3.5
        endpoint=counts.astype(float)*3.4
        r=m.paired_val_decision(base,endpoint,counts)
        self.assertEqual(r['verdict'],'TRAINING_HELPFUL_SIGNAL')
        self.assertGreater(r['ci95'][0],0)
        self.assertAlmostEqual(r['delta_nll'],0.1,places=12)

    def test_paired_bootstrap_no_gain(self):
        counts=np.full(256,238,dtype=np.int64);counts[:194]+=1
        a=counts.astype(float)*3.5
        r=m.paired_val_decision(a,a,counts)
        self.assertEqual(r['verdict'],'TRAINING_NOT_CLEARED')
        self.assertEqual(r['delta_nll'],0)

    def test_source_disallows_test_and_embedding_paths(self):
        src=FILE.read_text()
        self.assertNotIn('import embeddinggemma2',src.lower())
        self.assertNotIn('Q1Q2_ONCE_V3',src)
        self.assertIn("'test_access': False",src)
        self.assertIn("'q1q2_v3': False",src)
        self.assertIn("'NEW_RUN_ID_ALREADY_EXISTS_NO_RERUN'",src)
        self.assertNotIn('ollama create',src)


if __name__=='__main__':unittest.main(verbosity=2)
