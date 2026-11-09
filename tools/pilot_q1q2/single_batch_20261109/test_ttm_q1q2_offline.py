"""Pure offline Q1/Q2 contract tests: no network/model/TEST access."""
import importlib.util
import json
from pathlib import Path
from unittest import TestCase, main
from unittest.mock import patch

P=Path(__file__).with_name('ttm_q1q2_single_batch.py')
spec=importlib.util.spec_from_file_location('ttm_q1q2_eval',P)
m=importlib.util.module_from_spec(spec)
spec.loader.exec_module(m)

class Tests(TestCase):
    def test_ids_and_capacity(self):
        self.assertEqual(m.MAX_REQUESTS,74)
        self.assertEqual(m.MAX_OUTPUT_TOKENS,3904)
        self.assertNotEqual(m.PORT,12648)
        self.assertNotEqual(m.PORT,12649)

    def test_response_positive(self):
        obj={'done':True,'model':m.TAG,'response':'A story.','eval_count':4,
             'eval_duration':100000000,'total_duration':120000000,
             'prompt_eval_count':8,'prompt_eval_duration':6000000,
             'load_duration':3000000,'done_reason':'stop'}
        self.assertEqual(m.valid_response(obj,m.TAG,64),4)

    def test_response_negative_boundaries(self):
        obj={'done':True,'model':m.TAG,'response':'A story.','eval_count':4,
             'eval_duration':100000000,'total_duration':120000000,
             'prompt_eval_count':8,'prompt_eval_duration':6000000,
             'load_duration':3000000,'done_reason':'stop'}
        for k,v in [('done',False),('model','evil'),('eval_count',65),('eval_count',True),
                    ('eval_duration',0),('done_reason','bad'),('response',None),('total_duration',-1)]:
            with self.subTest(k=k,v=v),self.assertRaises(RuntimeError):
                m.valid_response({**obj,k:v},m.TAG,64)

    def test_request_greedy_sampling(self):
        g={'num_ctx':256,'num_predict':64,'temperature':0,'top_p':1.,'seed':None}
        a=m.request_body(g,'Synthetic prompt')
        self.assertEqual(a['options']['temperature'],0)
        self.assertNotIn('seed',a['options'])
        self.assertEqual(a['keep_alive'],'10m')
        self.assertTrue(a['raw'])
        self.assertFalse(a['stream'])
        s=m.request_body({**g,'seed':101,'temperature':0.8,'top_p':0.9},'Prompt')
        self.assertEqual(s['options']['seed'],101)

    def test_metric_measures_repetition(self):
        a=m.ngram_metrics([1,2,3,1,2,3])
        self.assertAlmostEqual(a['distinct_3'],0.75)
        self.assertAlmostEqual(a['repeat_3gram_ratio'],0.25)
        self.assertEqual(m.ngram_metrics([1,2])['distinct_3'],None)

    def test_write_new_refuses_overwrite(self):
        from tempfile import TemporaryDirectory
        with TemporaryDirectory() as d:
            p=Path(d)/'a.json'; m.write_new(p,{'ok':True})
            with self.assertRaises(FileExistsError):m.write_new(p,{'ok':False})
            self.assertEqual(json.loads(p.read_text())['ok'],True)

    def test_reparse_guard_regular_path(self):
        from tempfile import TemporaryDirectory
        with TemporaryDirectory() as d:m.reject_reparse(Path(d)/'not-created')

    def test_main_has_no_ollama_create(self):
        txt=P.read_text()
        self.assertNotIn("'/api/create'",txt)
        self.assertNotIn('drive.mount',txt)
        self.assertNotIn('TinyStories-test',txt)
        self.assertNotIn('torch.save',txt)
        self.assertNotIn('train_loop(',txt)

    def test_fixture_rejects_modified_sha(self):
        from tempfile import TemporaryDirectory
        with TemporaryDirectory() as d:
            root=Path(d)
            (root/'Q1Q2_LOCK_MANIFEST.json').write_text(json.dumps({'schema':'ttm.q1q2.frozen.inputs.manifest.v1',
                'files_sha256':{'Q1.json':'0'*64}}))
            (root/'Q1.json').write_text('{}')
            with patch.object(m,'INPUTS',root),self.assertRaises(RuntimeError):m.load_fixture()

    def test_fixture_rejects_path_escape(self):
        from tempfile import TemporaryDirectory
        with TemporaryDirectory() as d:
            root=Path(d)
            (root/'Q1Q2_LOCK_MANIFEST.json').write_text(json.dumps({'schema':'ttm.q1q2.frozen.inputs.manifest.v1',
                'files_sha256':{'../../secret':'0'*64}}))
            with patch.object(m,'INPUTS',root),self.assertRaises(RuntimeError):m.load_fixture()

if __name__=='__main__':main(verbosity=2)
