"""Pure offline Q1/Q2 contract tests: no network/model/TEST access."""
import importlib.util
import json
import sys
from pathlib import Path
from unittest import TestCase, main
from unittest.mock import patch

P=Path(__file__).with_name('ttm_q1q2_single_batch.py')
spec=importlib.util.spec_from_file_location('ttm_q1q2_eval',P)
m=importlib.util.module_from_spec(spec)
spec.loader.exec_module(m)

class Tests(TestCase):
    def test_dynamic_dataclass_module_registration_before_execution(self):
        # Reproduce the exact pre-CLAIM failure class without model or network.
        from tempfile import TemporaryDirectory
        with TemporaryDirectory() as d:
            path=Path(d)/'synthetic_bpe.py'
            path.write_text('from dataclasses import dataclass\n'
                            '@dataclass(frozen=True)\n'
                            'class FakeBPE:\n'
                            '    vocab: int = 2048\n',encoding='utf-8')
            name='ttm_q1q2_offline_bpe_registration'
            self.assertNotIn(name,sys.modules)
            try:
                module=m.load_module(path,name)
                self.assertIs(sys.modules[name],module)
                self.assertEqual(module.FakeBPE().vocab,2048)
                with self.assertRaisesRegex(RuntimeError,'MODULE_ALREADY_REGISTERED'):
                    m.load_module(path,name)
                self.assertIs(sys.modules[name],module)
            finally:
                sys.modules.pop(name,None)

    def test_failed_dynamic_import_does_not_poison_sys_modules(self):
        from tempfile import TemporaryDirectory
        with TemporaryDirectory() as d:
            path=Path(d)/'failing_module.py'
            path.write_text('raise ValueError("synthetic import failure")\n',encoding='utf-8')
            name='ttm_q1q2_offline_bpe_failing'
            self.assertNotIn(name,sys.modules)
            with self.assertRaisesRegex(ValueError,'synthetic import failure'):
                m.load_module(path,name)
            self.assertNotIn(name,sys.modules)

    def test_dynamic_import_rejects_invalid_module_name(self):
        with self.assertRaisesRegex(RuntimeError,'INVALID_DYNAMIC_MODULE_NAME'):
            m.load_module(Path('ignored.py'),'../unsafe')

    def test_ollama_metadata_cache_allowed_for_exact_gpt2_only(self):
        from tempfile import TemporaryDirectory
        import hashlib
        with TemporaryDirectory() as d:
            root=Path(d)
            k='metadata/sha256-'+m.MODEL_SHA+'.json'
            sidecar=root/k
            sidecar.parent.mkdir(parents=True)
            good={'ollama_version':'0.40.14','kv':{
                'general.architecture':'gpt2','gpt2.block_count':4,
                'gpt2.context_length':256,'gpt2.embedding_length':256,
                'gpt2.attention.head_count':4,'tokenizer.ggml.bos_token_id':256,
                'tokenizer.ggml.eos_token_id':256}}
            sidecar.write_text(json.dumps(good),encoding='utf-8')
            baseline={'blobs/source':{'size':10,'sha256':'a'*64}}
            observed={**baseline,k:{'size':sidecar.stat().st_size,'sha256':m.digest(sidecar)}}
            result=m.verify_runtime_store_delta(root,baseline,observed)
            self.assertEqual(result['added_files'],[k])
            self.assertEqual(result['sidecar_sha256'],m.digest(sidecar))
            self.assertEqual(m.verify_runtime_store_delta(root,baseline,baseline)['added_files'],[])

    def test_runtime_store_rejects_immutable_blob_change(self):
        from tempfile import TemporaryDirectory
        with TemporaryDirectory() as d:
            baseline={'blobs/source':{'size':10,'sha256':'a'*64}}
            modified={'blobs/source':{'size':11,'sha256':'b'*64}}
            with self.assertRaisesRegex(RuntimeError,'MODEL_STORE_IMMUTABLE_FILE_CHANGED'):
                m.verify_runtime_store_delta(Path(d),baseline,modified)

    def test_runtime_store_rejects_arbitrary_added_file(self):
        from tempfile import TemporaryDirectory
        with TemporaryDirectory() as d:
            baseline={'blobs/source':{'size':10,'sha256':'a'*64}}
            with self.assertRaisesRegex(RuntimeError,'UNEXPECTED_MODEL_STORE_FILE_ADDED'):
                m.verify_runtime_store_delta(Path(d),baseline,{**baseline,'evil.bin':{'size':1,'sha256':'b'*64}})

    def test_runtime_store_rejects_tampered_metadata_architecture(self):
        from tempfile import TemporaryDirectory
        with TemporaryDirectory() as d:
            root=Path(d); key='metadata/sha256-'+m.MODEL_SHA+'.json'
            file=root/key;file.parent.mkdir(parents=True)
            file.write_text(json.dumps({'ollama_version':'0.40.14','kv':{
                'general.architecture':'other'}}),encoding='utf-8')
            baseline={'blobs/source':{'size':10,'sha256':'a'*64}}
            observed={**baseline,key:{'size':file.stat().st_size,'sha256':m.digest(file)}}
            with self.assertRaisesRegex(RuntimeError,'MODEL_METADATA_ARCHITECTURE_MISMATCH'):
                m.verify_runtime_store_delta(root,baseline,observed)

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
