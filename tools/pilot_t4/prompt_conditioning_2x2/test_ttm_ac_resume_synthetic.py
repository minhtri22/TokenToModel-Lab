#!/usr/bin/env python3
"""No-LLM CPU fixture: A/C READY SHA, negative gates, toy optimizer/RNG resume parity.
Only synthetic 3->2 linear model; never loads TTM checkpoint, TRAIN, VAL or TEST.
Use TTM_AC_QA_ROOT pointing to a directory inside the project workspace.
"""
from __future__ import annotations
import copy, os, random, tempfile, unittest
from pathlib import Path
import numpy as np
import torch
import ttm_ac_resume_store as store

RUN='TTM_SMALL4M_AC_SYNTHETIC_QA_V1'
PIN='a'*64

class ResumeFixture(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        root=os.environ.get('TTM_AC_QA_ROOT')
        if not root or not Path(root).is_dir():
            raise RuntimeError('TTM_AC_QA_ROOT_REQUIRED_WITHIN_PROJECT')
        cls.workspace=Path(tempfile.mkdtemp(prefix='ttm_ac_preexec_synthetic_',dir=root))

    def test_01_scoped_roundtrip_and_no_overwrite(self):
        for arm in store.ARMS:
            p=self.workspace/f'roundtrip_{arm}';p.mkdir()
            for step in store.STEPS:
                state={'run_id':RUN,'arm':arm,'step':step,'history':[0]*(step-store.START),'model':{'toy':torch.arange(3)}}
                store.save_ready(p,step,state,RUN,arm,PIN,PIN,PIN)
                actual,restored,receipt=store.load_latest(p,RUN,arm,PIN,PIN,PIN)
                self.assertEqual((actual,len(restored['history'])),(step,step-store.START))
                self.assertEqual(receipt['checkpoint_sha256'],store.sha256_file(p/f'step_{step}.pt'))
                with self.assertRaisesRegex(RuntimeError,'NO_OVERWRITE'):
                    store.save_ready(p,step,state,RUN,arm,PIN,PIN,PIN)

    def test_02_orphan_rejected(self):
        p=self.workspace/'orphan';p.mkdir()
        (p/'step_1056.pt').write_bytes(b'synthetic broken payload')
        with self.assertRaisesRegex(RuntimeError,'ORPHAN'):
            store.load_latest(p,RUN,'A',PIN,PIN,PIN)

    def test_03_changed_pin_rejected(self):
        p=self.workspace/'wrong_pin';p.mkdir()
        state={'run_id':RUN,'arm':'A','step':1056,'history':[0]*32}
        store.save_ready(p,1056,state,RUN,'A',PIN,PIN,PIN)
        with self.assertRaisesRegex(RuntimeError,'READY_SCOPE_MISMATCH'):
            store.load_latest(p,RUN,'A','b'*64,PIN,PIN)

    def test_04_mutated_checkpoint_rejected(self):
        p=self.workspace/'mutated';p.mkdir()
        state={'run_id':RUN,'arm':'A','step':1056,'history':[0]*32}
        store.save_ready(p,1056,state,RUN,'A',PIN,PIN,PIN)
        with (p/'step_1056.pt').open('ab') as f:f.write(b'tamper')
        with self.assertRaisesRegex(RuntimeError,'READY_CHECKPOINT_SHA_MISMATCH'):
            store.load_latest(p,RUN,'A',PIN,PIN,PIN)

    def test_05_noncontiguous_rejected(self):
        p=self.workspace/'gap';p.mkdir()
        state={'run_id':RUN,'arm':'A','step':1088,'history':[0]*64}
        store.save_ready(p,1088,state,RUN,'A',PIN,PIN,PIN)
        with self.assertRaisesRegex(RuntimeError,'NONCONTIGUOUS'):
            store.load_latest(p,RUN,'A',PIN,PIN,PIN)

    @staticmethod
    def _new():
        torch.manual_seed(321);np.random.seed(654);random.seed(987)
        model=torch.nn.Linear(3,2)
        opt=torch.optim.AdamW(model.parameters(),lr=0.0003)
        sch=torch.optim.lr_scheduler.LambdaLR(opt,lr_lambda=lambda step:1.0)
        sampler=torch.Generator(device='cpu');sampler.manual_seed(999)
        return model,opt,sch,sampler

    @staticmethod
    def _advance(model,opt,sch,sampler,step):
        x=torch.randn(4,3)
        x=x+torch.from_numpy(np.random.normal(size=(4,3))).float()*0.01
        x=x+float(random.randint(0,30))/1000.0
        target=torch.randint(0,2,(4,),generator=sampler)
        loss=torch.nn.functional.cross_entropy(model(x),target)
        opt.zero_grad(set_to_none=True);loss.backward();opt.step();sch.step()
        return float(loss.item())

    def test_06_cpu_toy_adamw_rng_exact_resume(self):
        for arm in store.ARMS:
            p=self.workspace/f'toy_{arm}';p.mkdir()
            model,opt,sch,sampler=self._new()
            losses=[]
            for step in range(1025,1153):
                losses.append(self._advance(model,opt,sch,sampler,step))
                if step==1056:
                    q=np.random.get_state()
                    state={'run_id':RUN,'arm':arm,'step':step,'history':list(losses),
                           'model':copy.deepcopy(model.state_dict()),
                           'optimizer':copy.deepcopy(opt.state_dict()),'scheduler':sch.state_dict(),
                           'sampler_state':sampler.get_state(),
                           'torch_rng':torch.get_rng_state(),'python_rng':random.getstate(),
                           'numpy_rng':(q[0],q[1].tolist(),int(q[2]),int(q[3]),float(q[4]))}
                    store.save_ready(p,step,state,RUN,arm,PIN,PIN,PIN)
            uninterrupted={k:v.detach().clone() for k,v in model.state_dict().items()}
            expected_losses=list(losses)
            got,st,receipt=store.load_latest(p,RUN,arm,PIN,PIN,PIN)
            self.assertEqual(got,1056)
            model2,opt2,sch2,sampler2=self._new()
            model2.load_state_dict(st['model']);opt2.load_state_dict(st['optimizer'])
            sch2.load_state_dict(st['scheduler']);sampler2.set_state(st['sampler_state'])
            torch.set_rng_state(st['torch_rng']);random.setstate(st['python_rng'])
            q=st['numpy_rng'];np.random.set_state((q[0],np.array(q[1],dtype=np.uint32),q[2],q[3],q[4]))
            resumed_losses=list(st['history'])
            for step in range(got+1,1153):
                resumed_losses.append(self._advance(model2,opt2,sch2,sampler2,step))
            self.assertEqual(expected_losses,resumed_losses)
            for k,v in uninterrupted.items():self.assertTrue(torch.equal(v,model2.state_dict()[k]))
            self.assertEqual(sch.last_epoch,sch2.last_epoch)
            self.assertTrue(torch.equal(sampler.get_state(),sampler2.get_state()))

if __name__=='__main__':unittest.main(verbosity=2)
