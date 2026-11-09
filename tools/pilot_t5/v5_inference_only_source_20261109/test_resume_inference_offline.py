#!/usr/bin/env python3
"""Independent lightweight QA for inference-only continuation (no Ollama, no Windows API)."""
import importlib.util, json, sys, tempfile, unittest
from pathlib import Path
from types import SimpleNamespace
from unittest import mock

source=Path(__file__).resolve().parent/'ttm_t5_v5_imported_resume_inference.py'
spec=importlib.util.spec_from_file_location('resume',source)
r=importlib.util.module_from_spec(spec)
spec.loader.exec_module(r)

MANIFEST={'schemaVersion':2,'format':'gguf','layers':[{'mediaType':'application/vnd.ollama.image.model','digest':'sha256:'+r.EXPECTED_GGUF_HASH,'size':r.GGUF_SIZE}]}

class TestResume(unittest.TestCase):
    def test_manifest_positive(self):self.assertTrue(r.validate_manifest(MANIFEST))
    def test_manifest_wrong_format(self):self.assertFalse(r.validate_manifest({**MANIFEST,'format':'safetensors'}))
    def test_manifest_wrong_digest(self):self.assertFalse(r.validate_manifest({**MANIFEST,'layers':[{'mediaType':'application/vnd.ollama.image.model','digest':'sha256:bad','size':r.GGUF_SIZE}]}))
    def test_manifest_wrong_size(self):self.assertFalse(r.validate_manifest({**MANIFEST,'layers':[{'mediaType':'application/vnd.ollama.image.model','digest':'sha256:'+r.EXPECTED_GGUF_HASH,'size':123}]}))
    def test_manifest_no_layers(self):self.assertFalse(r.validate_manifest({'schemaVersion':2,'format':'gguf','layers':[]}))
    def test_manifest_bad_shape(self):self.assertFalse(r.validate_manifest({'schemaVersion':2,'format':'gguf','layers':{}}))
    def test_frozen_model_tag(self):self.assertEqual(r.MODEL,'ttm-t5-f32-compat-only-v5final:latest')
    def test_new_port_distinct(self):self.assertEqual(r.PORT,12649)
    def test_new_evidence_dir_distinct(self):self.assertNotEqual(r.OUT,r.V5_RUN)
    def test_no_ollama_create_or_training(self):
        src=source.read_text(encoding='utf8')
        self.assertNotIn("'create',MODEL",src)
        self.assertNotIn('train(',src)
        self.assertIn("'/api/generate'",src)
    def test_claim_is_exclusive(self):
        with tempfile.TemporaryDirectory() as d:
            p=Path(d)/'CLAIM.json'
            r.write_x(p,{'status':'ONE_SHOT_CLAIMED'})
            with self.assertRaises(FileExistsError):r.write_x(p,{'status':'ONE_SHOT_CLAIMED'})
    def test_mock_generation_positive(self):
        with tempfile.TemporaryDirectory() as d:
            root=Path(d)/'resume'
            old_out=r.OUT
            r.OUT=root
            called=[]
            class Proc:
                pid=43210
            proc=Proc()
            def mock_copy(v5,evidence):
                called.append('copy')
                (root/'models'/r.MODEL_MANIFEST_REL).parent.mkdir(parents=True,exist_ok=True)
                r.write_x(root/'models'/r.MODEL_MANIFEST_REL,MANIFEST)
            def fake_api(url, body=None, timeout=0):
                called.append(url.rsplit('/',1)[-1])
                if body is None:return {'models':[{'name':r.MODEL}]}
                return {'done':True,'model':r.MODEL,'eval_count':13,'response':'robot text','done_reason':'stop'}
            v5=SimpleNamespace(
                isolated_env=lambda out:{},
                EXE=Path('ollama.exe'),
                observe_readiness_with_trace=lambda p,out:{'ready':True,'identity_creation_date':'t'},
                assert_owned_listener=lambda p,t:True,
                api_json=fake_api,
                stop_owned_server=lambda p:{'stop_status':'STOPPED_OWNED_TREE','pid':p.pid},
                tcp_table_observation=lambda port:{'rows':[]},
                classify_shutdown_port_rows=lambda rows,port:{'decision':'PASS_NO_ACTIVE_SOCKET_AFTER_SHUTDOWN'}
            )
            try:
                with mock.patch.object(r,'copy_store_and_verify',mock_copy),mock.patch.object(r.subprocess,'Popen',return_value=proc),mock.patch.object(r.subprocess,'CREATE_NEW_PROCESS_GROUP',0,create=True):
                    result=r.run_one_shot(v5,{'original_v5_result_sha256':'abc','source_store_snapshot':{}})
                self.assertEqual(result['status'],'PASS_COMPATIBILITY_IMPORT_REUSED_AND_INFERENCE_CONFIRMED')
                self.assertEqual(result['evaluation']['generated_tokens'],13)
                self.assertEqual(called,['copy','tags','generate'])
                self.assertTrue((root/'RESULT.json').is_file())
                with self.assertRaises(FileExistsError):r.run_one_shot(v5,{'original_v5_result_sha256':'abc','source_store_snapshot':{}})
            finally:r.OUT=old_out

if __name__=='__main__':unittest.main(verbosity=2)
