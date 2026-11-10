#!/usr/bin/env python3
"""Independent synthetic CPU QA. NEVER opens checkpoint, TTM/G1 private TEST, or GPU."""
from __future__ import annotations
import json
import tempfile
import time
import unittest
import sys
from pathlib import Path
from unittest.mock import patch
import zipfile
import numpy as np
import torch
from torch import nn
from torch.nn import functional as F
sys.path.insert(0,str(Path(__file__).resolve().parent))
import ttm_six_ttm4m_three_arm_v1 as m

SOURCE=Path('/mnt/data/g1_explore_public_qwen_dev_v1.py')
ZIP=Path('/mnt/data/TTM_SIX_G1_EXPLORE_REAL_QWEN_DEV_RESULTS.zip')

class SmallGPT(nn.Module):
    """Cheap synthetic model with the same forward/hook API, not TTM model itself."""
    def __init__(self):
        super().__init__()
        self.embedding=nn.Embedding(32,8)
        self.final_ln=nn.LayerNorm(8)
        self.head=nn.Linear(8,2048)
    def forward(self,x):
        h=self.final_ln(self.embedding(x))
        return self.head(h),None


def tiny_model_factory(p02,parent,device,arm):
    m.seed_all()
    model=SmallGPT().to(device)
    fp=m.param_fingerprint(model.state_dict())
    head=nn.Linear(8,2).to(device)
    opt=torch.optim.AdamW(list(model.parameters())+([] if arm=='A' else list(head.parameters())),lr=1e-4,betas=(.9,.95),weight_decay=.01)
    return model,head,opt,fp


class TestFrozenSource(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        torch.set_num_threads(1)
        cls.rows,cls.teacher=m.freeze_teacher(ZIP,SOURCE)
        cls.train=cls.rows[:48]
        cls.dev=cls.rows[48:]
        cls.norm=m.train_norms(cls.train,cls.teacher[:48])
        # Synthetic IDs: do not require ANY private tokenizer or corpus.
        cls.ids=[[3+((i+j)%20) for j in range(7+(i%4))] for i in range(64)]

    def test_01_positive_original_cached_tensor(self):
        self.assertEqual(self.teacher.shape,(64,2))
        self.assertEqual(len({r['group'] for r in self.train}),12)
        self.assertEqual(len({r['group'] for r in self.dev}),4)
        self.assertFalse({r['group'] for r in self.train}&{r['group'] for r in self.dev})
        self.assertAlmostEqual(m.template_mae(self.train,self.dev,self.teacher[:48],self.teacher[48:]),m.TEMPLATE_BASELINE,places=12)

    def test_02_qwen_wrong_sha_rejected(self):
        with tempfile.TemporaryDirectory() as t:
            q=Path(t)/'changed.zip'
            q.write_bytes(ZIP.read_bytes()+b'mismatch')
            with self.assertRaisesRegex(RuntimeError,'QWEN_ZIP_SHA'):
                m.freeze_teacher(q,SOURCE)

    def test_03_wrong_qwen_source_rejected(self):
        with tempfile.TemporaryDirectory() as t:
            q=Path(t)/'source.py';q.write_bytes(SOURCE.read_bytes()+b'\n')
            with self.assertRaisesRegex(RuntimeError,'SOURCE_GIT_BLOB_CHANGED'):
                m.freeze_teacher(ZIP,q)

    def test_04_nonfinite_teacher_rejected(self):
        with tempfile.TemporaryDirectory() as t:
            src=ZIP
            target=Path(t)/'bad.zip'
            import io
            with zipfile.ZipFile(src) as zi, zipfile.ZipFile(target,'w') as zo:
                for name in zi.namelist():
                    b=zi.read(name)
                    if name.endswith('target_features.npz'):
                        with np.load(io.BytesIO(b),allow_pickle=False) as f:
                            obj={k:f[k].copy() for k in f.files}
                        obj['probe'][0,0]=np.nan
                        out=io.BytesIO();np.savez_compressed(out,**obj);b=out.getvalue()
                    zo.writestr(name,b)
            with patch.object(m,'QWEN_ZIP_SHA256',m.sha_file(target)):
                with self.assertRaisesRegex(RuntimeError,'TEACHER_SCORE_SHAPE_FINITE'):
                    m.freeze_teacher(target,SOURCE)

    def test_05_group_duplicate_guard(self):
        old=list(self.train)
        wrong=old[:-1]+[dict(old[0],group='extra_group')]
        with self.assertRaisesRegex(RuntimeError,'TEMPLATE_TRAIN_COUNT'):
            m.train_norms(wrong,self.teacher[:48])

    def test_06_train_only_stats_isolated_from_DEV(self):
        mutate=self.teacher.copy();mutate[48:]+=1e7
        n=m.train_norms(self.train,mutate[:48])
        for k in ('mean','std','template_table','resid_std','B','C'):
            np.testing.assert_array_equal(n[k],self.norm[k])

    def test_07_normalization_failure(self):
        bad=self.teacher[:48].copy();bad[:,0]=1.
        with self.assertRaisesRegex(RuntimeError,'PROBE_NORM_DEGENERATE'):
            m.train_norms(self.train,bad)

    def test_08_schedule_balanced_exact_72(self):
        s=m.schedule(self.train)
        self.assertEqual(len(s),72)
        self.assertTrue(all(len(x)==8 for x in s))
        self.assertTrue(np.array_equal(np.bincount(np.concatenate(s),minlength=48),[12]*48))

    def test_09_rightpad_labels_and_hook(self):
        d=torch.device('cpu')
        x,y,p=m.make_padded([0,1],self.ids,d)
        self.assertEqual(x.shape,y.shape)
        self.assertEqual(int((y!=-100).sum()),len(self.ids[0])+len(self.ids[1])-2)
        self.assertEqual(y[0,0].item(),self.ids[0][1])
        self.assertEqual(y[0,len(self.ids[0])-1].item(),-100)
        self.assertEqual(p.tolist(),[len(self.ids[0])-1,len(self.ids[1])-1])
        tiny=SmallGPT()
        _,hidden=m.forward_with_last_hidden(tiny,x,p)
        actual=tiny.final_ln(tiny.embedding(x))
        torch.testing.assert_close(hidden[0],actual[0,p[0]])
        torch.testing.assert_close(hidden[1],actual[1,p[1]])

    def test_10_tampered_bpe_manifest_rejected(self):
        with tempfile.TemporaryDirectory() as t:
            p=Path(t)/'manifest.json';p.write_text('{}')
            with self.assertRaisesRegex(RuntimeError,'BPE_FILE_SHA'):
                m.load_tokenizer(p,'does-not-exist.py',['a sentence'])

    def test_11_broken_parent_hash_rejected_before_load(self):
        with tempfile.TemporaryDirectory() as t:
            p=Path(t)/'step_1280';p.mkdir()
            (p/'READY.json').write_text('{}')
            (p/'checkpoint.pt').write_bytes(b'fake')
            with self.assertRaisesRegex(RuntimeError,'PARENT_HASH'):
                m.check_parent(p)

    def test_12_no_authorization_rejected(self):
        with self.assertRaisesRegex(RuntimeError,'OWNER_NEW_PILOT_APPROVAL_REQUIRED'):
            m.validate_approval(None)
        with tempfile.TemporaryDirectory() as t:
            p=Path(t)/'permit.json';p.write_text(json.dumps({'decision':'AUTHORIZE_G1_SCIENCE_ONE_SHOT'}))
            with self.assertRaisesRegex(RuntimeError,'OWNER_APPROVAL_'):
                m.validate_approval(p)

    def test_13_output_scope_rejected(self):
        with tempfile.TemporaryDirectory() as t:
            path=Path(t)/'different'
            with self.assertRaisesRegex(RuntimeError,'OUTPUT_NOT_UNDER_NEW_PILOT_NAMESPACE'):
                m.write_result_pack(path,{}, {}, {})
        self.assertFalse(path.exists())

    def test_14_checkpoint_writes_not_on_parent(self):
        # Write operation uses a distinct required /content/drive/... namespace.
        self.assertNotEqual(m.RUN_ID,'ttm_small4m_step1024_to1280_exploratory_v1')
        self.assertNotIn('TEST',m.RUN_ID)

    def test_15_template_only_cheaper_than_both_previous_Qwen_baselines(self):
        self.assertLess(m.TEMPLATE_BASELINE,0.06182712847813694)
        self.assertLess(m.TEMPLATE_BASELINE,0.06755050653737271)

    def test_16_verdict_negative_strong_template_shortcut(self):
        a={'dev_nll':3.2,'dev_group_nll':{str(k):3.2 for k in range(4)}}
        b={'dev_nll':3.15,'dev_group_nll':{str(k):3.15 for k in range(4)},'dev_raw_probe_mae':.055}
        c={'dev_nll':3.11,'dev_group_nll':{str(k):3.11 for k in range(4)},'dev_raw_probe_mae':.053}
        self.assertEqual(m.verdict({'A':a,'B':b,'C':c})['decision'],'EXPLORATORY_NO_CLEAR_GAIN')

    def test_17_verdict_positive_synthetic_only(self):
        a={'dev_nll':3.2,'dev_group_nll':{str(k):3.2 for k in range(4)}}
        b={'dev_nll':3.18,'dev_group_nll':{str(k):3.18 for k in range(4)},'dev_raw_probe_mae':.055}
        c={'dev_nll':3.08,'dev_group_nll':{str(k):3.08 for k in range(4)},'dev_raw_probe_mae':.05}
        self.assertEqual(m.verdict({'A':a,'B':b,'C':c})['decision'],'EXPLORATORY_FUNCTIONAL_GAIN_CANDIDATE')

    def test_18_arms_same_initial_and_2steps_training_cpu(self):
        orig=m.make_model
        try:
            m.make_model=tiny_model_factory
            result=[]
            for arm in 'ABC':
                model,head,fp,loss=m.train_arm(None,{},arm,self.ids,self.train,self.norm,torch.device('cpu'),time.monotonic(),tick=2)
                self.assertEqual(len(loss),2)
                self.assertTrue(all(np.isfinite(loss)))
                result.append(fp)
            self.assertEqual(len(set(result)),1)
        finally:
            m.make_model=orig

    def test_19_test_must_remain_absent(self):
        self.assertEqual(TRAIN_N:=m.TRAIN_N,48)
        self.assertEqual(len(self.rows)-TRAIN_N,16)
        self.assertNotIn('TEST',m.EXPERIMENT)

    def test_20_oom_watch_and_timing_flags(self):
        self.assertEqual(m.WALL_CAP,1200)
        self.assertEqual(m.UPDATES,72)
        self.assertEqual(m.BATCHES_PER_EPOCH,6)


if __name__=='__main__':
    import time
    unittest.main(verbosity=2)
