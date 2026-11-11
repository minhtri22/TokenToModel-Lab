import importlib.util
from pathlib import Path
import unittest

FILE=Path(__file__).with_name('ttm_fresh16_v2_e0.py')
spec=importlib.util.spec_from_file_location('fresh16_runner',FILE)
mod=importlib.util.module_from_spec(spec)
spec.loader.exec_module(mod)

class E0SourceOnlyTests(unittest.TestCase):
    def test_map_cardinality_and_blinding(self):
        ids=[{'id':f'CP{i:02d}-{v}'} for i in range(1,9) for v in 'AB']
        x=mod.make_map(ids)
        y=mod.map_validate(x)
        self.assertEqual(len(y),32)
        self.assertEqual(len({a['opaque_pair_id'] for a in y}),16)
        self.assertTrue(all(len(a['opaque_id'])==32 for a in y))
        self.assertEqual({a['checkpoint_step'] for a in y},{1024,1280})
    def test_random_map_is_not_repeated(self):
        ids=[{'id':f'CP{i:02d}-{v}'} for i in range(1,9) for v in 'AB']
        self.assertNotEqual(mod.make_map(ids)['secret_nonce'],mod.make_map(ids)['secret_nonce'])
    def test_bad_pair_rejected(self):
        ids=[{'id':f'CP{i:02d}-{v}'} for i in range(1,9) for v in 'AB']
        m=mod.make_map(ids)
        m['mapping'][0]['variant']='C'
        with self.assertRaises(RuntimeError):mod.map_validate(m)
    def test_map_missing_condition_is_rejected(self):
        ids=[{'id':f'CP{i:02d}-{v}'} for i in range(1,9) for v in 'AB']
        m=mod.make_map(ids)
        first=next(x for x in m['mapping'] if x['checkpoint_step']==1024 and x['prompt_id']=='CP01-A')
        second=next(x for x in m['mapping'] if x['checkpoint_step']==1280 and x['prompt_id']=='CP01-A')
        second['checkpoint_step']=1024
        with self.assertRaises(RuntimeError):mod.map_validate(m)
    def test_no_permit_is_fail_closed(self):
        import subprocess,sys
        p=subprocess.run([sys.executable,str(FILE),'--mode','run','--project-root','/tmp','--worktree','/tmp','--expected-head','0'*40,'--run-dir','/tmp/missing'],capture_output=True,text=True)
        self.assertNotEqual(p.returncode,0)
        self.assertIn('SCIENCE_GO_PERMIT_NOT_PROVIDED',p.stderr)
    def test_checkpoint_1280_metadata_without_forward(self):
        import torch,hashlib
        p=Path('/mnt/data/TTM_original_step1280_SHA256_ee723407.pt')
        if not p.exists():self.skipTest('Checkpoint unavailable')
        self.assertEqual(mod.sha(p),mod.CHECKPOINTS[1280][1])
        data=torch.load(p,map_location='cpu',weights_only=True)
        self.assertEqual(data['schema'],'ttm.t4.science.checkpoint.v1')
        self.assertEqual(data['step'],1280)
        self.assertEqual(data['config'],mod.CONFIG)
        self.assertEqual(data['model']['tok.weight'].shape,(2048,256))
        self.assertEqual(data['p02_git_blob'],mod.BLOBS[mod.P02])
if __name__=='__main__':unittest.main(verbosity=2)
