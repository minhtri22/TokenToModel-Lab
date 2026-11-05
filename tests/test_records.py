import hashlib
import json
from pathlib import Path
import sys
import tempfile
import unittest
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'scripts'))
from record_run import register, validate
from compare_runs import compare

class RecordTests(unittest.TestCase):
    def test_reject_bad_hash(self):
        with tempfile.TemporaryDirectory() as tmp:
            root=Path(tmp); (root/'configs').mkdir()
            (root/'configs'/'a.json').write_text('{}')
            d=self.data();d['config_sha256']='invalid'
            with self.assertRaisesRegex(ValueError,'SHA256'):
                validate(d,root)
    def data(self):
        return dict(run_id='P00_TEST_00001',phase='P00',kind='QA',status='PASS',git_sha='0'*40,branch='feature/p00',config_path='configs/a.json',config_sha256='',dataset_id='toy',dataset_sha256='NA',seed=123,environment={'device':'cpu','torch':'x','os':'Windows'},workload_id='fixture-v1',metrics={'loss':1.1},qa_evidence='qa.json')
    def test_immutable_run(self):
        with tempfile.TemporaryDirectory() as tmp:
            root=Path(tmp); (root/'configs').mkdir()
            cfg=root/'configs'/'a.json';cfg.write_text('{}');d=self.data();d['config_sha256']=hashlib.sha256(cfg.read_bytes()).hexdigest()
            src=root/'receipt.json';src.write_text(json.dumps(d),encoding='utf-8')
            dest, ent=register(src,root)
            self.assertTrue(dest.exists())
            self.assertEqual(len((root/'experiments'/'registry.jsonl').read_text().splitlines()),1)
            with self.assertRaises(FileExistsError): register(src,root)
            self.assertEqual(len((root/'experiments'/'registry.jsonl').read_text().splitlines()),1)
    def test_comparability(self):
        a={'workload_id':'x','dataset_id':'a','dataset_sha256':'abc','environment':{'device':'cpu','torch':'x','os':'win'},'metrics':{'latency':10}}
        b=dict(a,workload_id='y',metrics={'latency':9})
        c,m,r=compare(a,b)
        self.assertFalse(c);self.assertIn('workload_id',m)
        self.assertEqual(r[0][3],-1)

if __name__=='__main__':unittest.main()
