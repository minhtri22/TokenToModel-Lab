#!/usr/bin/env python3
"""Independent guarded RC1 offline QA derived from TTM T5 TCP ownership V3.

No real Ollama/PowerShell invocation; mock process/TCP/HTTP and full create/generate path.
On Windows, any test temp files must stay within TTM project _tmp.
"""
from __future__ import annotations
import ast
import base64
import contextlib
import importlib.util
import json
import os
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest
from types import SimpleNamespace
from unittest.mock import Mock,patch

SRC=Path(__file__).with_name('t5_ollama_v3rc1.py')
spec=importlib.util.spec_from_file_location('ttm_t5_v3rc1_smoke_qa_only',SRC)
subject=importlib.util.module_from_spec(spec)
spec.loader.exec_module(subject)

class Proc:
    def __init__(self,pid=32177,rc=None):self.pid=pid;self.rc=rc;self.returncode=rc
    def poll(self):return self.rc


def snapshot(pid=32177,local='127.0.0.1',state='Listen',port=None,creation='2026-11-09T00:00:00Z',exe=None):
    port=port if port is not None else subject.PORT
    exe=exe if exe is not None else str(subject.EXE)
    rows=[{'local_address':local,'local_port':port,'state':state,'pid':pid}]
    procs=[{'pid':pid,'name':'ollama.exe','executable_path':exe,'creation_date':creation}] if state=='Listen' else []
    return {'schema':'ttm.t5.windows.tcptable.snapshot.v1','port':port,'rows':rows,'processes':procs}


def good_http(_):return {'attempted':True,'http_status':200,'api_version':subject.VERSION,'error_type':None,'error_code':None}


@contextlib.contextmanager
def qa_dir():
    if sys.platform=='win32':
        root=Path(r'D:\WORK\RESEARCH\TokenToModel-Lab\_tmp')
        assert root.is_dir(), 'QA_PROJECT_TMP_MISSING'
        with tempfile.TemporaryDirectory(prefix='ttm_t5_v3rc1_fake_',dir=root) as d:yield Path(d)
    else:
        with tempfile.TemporaryDirectory(prefix='ttm_t5_v3rc1_fake_',dir=Path(__file__).parent) as d:yield Path(d)


class TestPureGuard(unittest.TestCase):
    def check(self,raw,desired='OWNED_LOOPBACK_LISTEN',creation=None):
        out=subject.ownership_status(raw,32177,expected_creation=creation)
        self.assertEqual(out['decision'],desired)
        return out

    def test_ipv4_loopback_exact_pid(self):self.check(snapshot())
    def test_ipv6_loopback_exact_pid(self):self.check(snapshot(local='::1'))
    def test_wildcard_ipv6_rejected(self):self.check(snapshot(local='::'),'HOLD_NON_LOOPBACK_OR_WILDCARD_LISTENER')
    def test_wildcard_ipv4_rejected(self):self.check(snapshot(local='0.0.0.0'),'HOLD_NON_LOOPBACK_OR_WILDCARD_LISTENER')
    def test_other_ipv4_rejected(self):self.check(snapshot(local='192.168.1.17'),'HOLD_NON_LOOPBACK_OR_WILDCARD_LISTENER')
    def test_ipv4_mapped_loopback_is_not_silently_accepted(self):self.check(snapshot(local='::ffff:127.0.0.1'),'HOLD_NON_LOOPBACK_OR_WILDCARD_LISTENER')
    def test_wrong_pid_rejected(self):self.check(snapshot(pid=44444),'HOLD_UNTRUSTED_OR_MULTIPLE_PID')
    def test_two_owners_rejected(self):
        x=snapshot();x['rows']+=snapshot(pid=44444)['rows'];x['processes']+=snapshot(pid=44444)['processes']
        self.check(x,'HOLD_UNTRUSTED_OR_MULTIPLE_PID')
    def test_same_owner_ipv4_ipv6_loopback(self):
        x=snapshot();x['rows']+=snapshot(local='::1')['rows'];self.check(x)
    def test_no_listener_waits_not_pass(self):
        x=snapshot();x['rows']=[];x['processes']=[];self.check(x,'WAIT_NO_LISTEN_ROW')
    def test_bound_only_does_not_pass(self):self.check(snapshot(state='Bound'),'WAIT_NO_LISTEN_ROW')
    def test_established_only_does_not_pass(self):self.check(snapshot(state='Established'),'WAIT_NO_LISTEN_ROW')
    def test_missing_state_rejected(self):self.check(snapshot(state=''),'HOLD_TCP_ROW_INVALID_OR_MISSING_STATE')
    def test_missing_pid_rejected(self):
        x=snapshot();del x['rows'][0]['pid'];self.check(x,'HOLD_TCP_ROW_INVALID_OR_MISSING_STATE')
    def test_zero_pid_rejected(self):self.check(snapshot(pid=0),'HOLD_TCP_ROW_INVALID_OR_MISSING_STATE')
    def test_missing_port_rejected(self):
        x=snapshot();del x['rows'][0]['local_port'];self.check(x,'HOLD_TCP_ROW_INVALID_OR_MISSING_STATE')
    def test_wrong_port_rejected(self):self.check(snapshot(port=11434),'HOLD_TCP_TABLE_MALFORMED')
    def test_bad_schema_and_shape_rejected(self):
        self.check({'port':subject.PORT,'rows':None,'processes':[]},'HOLD_TCP_TABLE_MALFORMED')
    def test_missing_identity_rejected(self):
        x=snapshot();x['processes']=[];self.check(x,'HOLD_PROCESS_IDENTITY_MISSING_OR_MULTIPLE')
    def test_double_identity_rejected(self):
        x=snapshot();x['processes']*=2;self.check(x,'HOLD_PROCESS_IDENTITY_MISSING_OR_MULTIPLE')
    def test_wrong_executable_rejected(self):self.check(snapshot(exe=r'C:\Users\Public\fake_ollama.exe'),'HOLD_UNEXPECTED_EXECUTABLE_IDENTITY')
    def test_wrong_process_name_rejected(self):
        x=snapshot();x['processes'][0]['name']='cmd.exe';self.check(x,'HOLD_UNEXPECTED_EXECUTABLE_IDENTITY')
    def test_missing_creation_rejected(self):self.check(snapshot(creation=''),'HOLD_PROCESS_IDENTITY_INCOMPLETE')
    def test_creation_change_rejected(self):self.check(snapshot(), 'HOLD_PROCESS_CREATION_CHANGED',creation='other-instance')
    def test_creation_match_pass(self):self.check(snapshot(),creation='2026-11-09T00:00:00Z')
    def test_missing_listen_state_other_connection_blocked(self):
        x=snapshot();x['rows'].append({'local_address':'127.0.0.1','local_port':subject.PORT,'pid':32177,'state':''})
        self.check(x,'HOLD_TCP_ROW_INVALID_OR_MISSING_STATE')
    def test_nonlisten_same_pid_does_not_invalidate_good_listener(self):
        x=snapshot();x['rows'].append({'local_address':'127.0.0.1','local_port':subject.PORT,'pid':32177,'state':'Established'})
        self.check(x)
    def test_bool_pid_rejected(self):
        x=snapshot();x['rows'][0]['pid']=True;self.check(x,'HOLD_TCP_ROW_INVALID_OR_MISSING_STATE')


class TestReadiness(unittest.TestCase):
    def test_pass_requires_two_snapshots_and_http(self):
        tcp=Mock(return_value=snapshot());http=Mock(side_effect=good_http)
        x=subject.readiness_sample(Proc(),1,tcp_fn=tcp,http_fn=http)
        self.assertEqual(x['decision'],'READY_TCP_TABLE_PID_PATH_AND_EXACT_API_VERSION')
        self.assertEqual(tcp.call_count,2);http.assert_called_once()
        self.assertIsNotNone(x['ownership_after']['identity'])
    def test_wrong_pid_skips_http(self):
        http=Mock();x=subject.readiness_sample(Proc(),1,tcp_fn=lambda p:snapshot(pid=8),http_fn=http)
        self.assertEqual(x['decision'],'HOLD_UNTRUSTED_OR_MULTIPLE_PID');http.assert_not_called()
    def test_wildcard_skips_http(self):
        http=Mock();x=subject.readiness_sample(Proc(),1,tcp_fn=lambda p:snapshot(local='::'),http_fn=http)
        self.assertEqual(x['decision'],'HOLD_NON_LOOPBACK_OR_WILDCARD_LISTENER');http.assert_not_called()
    def test_empty_listener_skips_http(self):
        http=Mock();x=subject.readiness_sample(Proc(),1,tcp_fn=lambda p:{**snapshot(),'rows':[],'processes':[]},http_fn=http)
        self.assertEqual(x['decision'],'WAIT_NO_LISTEN_ROW');http.assert_not_called()
    def test_http_503_observed(self):
        x=subject.readiness_sample(Proc(),1,tcp_fn=lambda p:snapshot(),http_fn=lambda u:{'attempted':True,'http_status':503,'api_version':None,'error_code':'HTTP_NON_200'})
        self.assertEqual(x['decision'],'WAIT_HTTP_NON_200_OR_UNREACHABLE')
    def test_http_wrong_version_observed(self):
        x=subject.readiness_sample(Proc(),1,tcp_fn=lambda p:snapshot(),http_fn=lambda u:{'attempted':True,'http_status':200,'api_version':'0.40.13','error_code':None})
        self.assertEqual(x['decision'],'WAIT_HTTP_VERSION_MISMATCH')
    def test_http_invalid_json_observed(self):
        x=subject.readiness_sample(Proc(),1,tcp_fn=lambda p:snapshot(),http_fn=lambda u:{'attempted':True,'http_status':200,'api_version':None,'error_code':'INVALID_JSON'})
        self.assertEqual(x['decision'],'WAIT_HTTP_MALFORMED_PAYLOAD')
    def test_http_unexpected_exception_logged_without_detail(self):
        def raise_secret(_):raise RuntimeError('PRIVATE_SECRET_IGNORED')
        x=subject.readiness_sample(Proc(),1,tcp_fn=lambda p:snapshot(),http_fn=raise_secret)
        self.assertEqual(x['decision'],'WAIT_HTTP_PROBE_EXCEPTION');self.assertNotIn('PRIVATE_SECRET',str(x))
    def test_tcp_query_failure_holds_and_no_http(self):
        def bad(_):raise RuntimeError('ACCESS_DENIED_WITH_SECRET')
        http=Mock();x=subject.readiness_sample(Proc(),1,tcp_fn=bad,http_fn=http)
        self.assertEqual(x['decision'],'HOLD_TCP_TABLE_UNAVAILABLE');http.assert_not_called()
        self.assertNotIn('SECRET',str(x))
    def test_process_exit_no_probe(self):
        http=Mock();tcp=Mock();x=subject.readiness_sample(Proc(rc=5),1,tcp_fn=tcp,http_fn=http)
        self.assertEqual(x['decision'],'FAIL_SERVER_EXITED');tcp.assert_not_called();http.assert_not_called()
    def test_recheck_pid_replaced_after_http(self):
        values=[snapshot(),snapshot(pid=222)];tcp=Mock(side_effect=values)
        x=subject.readiness_sample(Proc(),1,tcp_fn=tcp,http_fn=good_http)
        self.assertEqual(x['decision'],'HOLD_OWNERSHIP_CHANGED_AFTER_HTTP')
    def test_recheck_process_creation_changed(self):
        values=[snapshot(),snapshot(creation='RECYCLED')]
        x=subject.readiness_sample(Proc(),1,tcp_fn=Mock(side_effect=values),http_fn=good_http)
        self.assertEqual(x['decision'],'HOLD_OWNERSHIP_CHANGED_AFTER_HTTP')
    def test_recheck_listener_set_changed(self):
        x=snapshot();y=snapshot();y['rows']+=snapshot(local='::1')['rows']
        z=subject.readiness_sample(Proc(),1,tcp_fn=Mock(side_effect=[x,y]),http_fn=good_http)
        self.assertEqual(z['decision'],'HOLD_LISTENER_SET_CHANGED_AFTER_HTTP')
    def test_recheck_fails_closed(self):
        def twice(_):
            twice.count+=1
            if twice.count==2:raise RuntimeError('CIM_FAILED')
            return snapshot()
        twice.count=0
        z=subject.readiness_sample(Proc(),1,tcp_fn=twice,http_fn=good_http)
        self.assertEqual(z['decision'],'HOLD_TCP_TABLE_RECHECK_UNAVAILABLE')
    def test_no_recheck_when_http_version_wrong(self):
        tcp=Mock(return_value=snapshot())
        subject.readiness_sample(Proc(),1,tcp_fn=tcp,http_fn=lambda u:{'attempted':True,'http_status':200,'api_version':'different','error_code':None})
        self.assertEqual(tcp.call_count,1)
    def test_trace_success_two_snapshots_and_fsnyc(self):
        with qa_dir() as d:
            x=subject.observe_readiness_with_trace(Proc(),d,max_samples=2,sleep_fn=lambda _:None,tcp_fn=lambda p:snapshot(),http_fn=good_http)
            self.assertTrue(x['ready']);self.assertEqual(x['identity_creation_date'],'2026-11-09T00:00:00Z')
            lines=(d/'READINESS_ATTEMPTS.jsonl').read_text().splitlines();self.assertEqual(len(lines),1)
            self.assertEqual(json.loads(lines[0])['decision'],'READY_TCP_TABLE_PID_PATH_AND_EXACT_API_VERSION')
    def test_trace_no_listener_timeout_without_http(self):
        with qa_dir() as d:
            http=Mock();z={**snapshot(),'rows':[],'processes':[]}
            with self.assertRaisesRegex(RuntimeError,'READINESS_TIMEOUT_WAIT_NO_LISTEN_ROW'):
                subject.observe_readiness_with_trace(Proc(),d,max_samples=3,sleep_fn=lambda _:None,tcp_fn=lambda p:z,http_fn=http)
            lines=(d/'READINESS_ATTEMPTS.jsonl').read_text().splitlines();self.assertEqual(len(lines),3);http.assert_not_called()
    def test_trace_exclusive_no_overwrite(self):
        with qa_dir() as d:
            p=d/'READINESS_ATTEMPTS.jsonl';p.write_text('immutable',encoding='utf8')
            with self.assertRaises(FileExistsError):
                subject.observe_readiness_with_trace(Proc(),d,max_samples=1,sleep_fn=lambda _:None,tcp_fn=lambda _:snapshot(),http_fn=good_http)
            self.assertEqual(p.read_text(),'immutable')
    def test_trace_holds_first_bad_pid(self):
        with qa_dir() as d:
            with self.assertRaisesRegex(RuntimeError,'READINESS_HOLD_UNTRUSTED_OR_MULTIPLE_PID'):
                subject.observe_readiness_with_trace(Proc(),d,max_samples=3,sleep_fn=lambda _:None,tcp_fn=lambda _:snapshot(pid=99),http_fn=good_http)
            self.assertEqual(len((d/'READINESS_ATTEMPTS.jsonl').read_text().splitlines()),1)


class TestAdapterAndStatic(unittest.TestCase):
    def test_encoded_command_is_powershell_5_1_and_get_tcp(self):
        raw=snapshot();raw['schema']='ttm.t5.windows.tcptable.snapshot.v1'
        fake=SimpleNamespace(returncode=0,stdout=json.dumps(raw))
        with patch.object(subject.subprocess,'run',return_value=fake) as call:
            obj=subject.tcp_table_observation(subject.PORT)
        self.assertEqual(obj['rows'][0]['pid'],32177)
        argv=call.call_args.args[0];self.assertIn('powershell.exe',argv[0].lower());self.assertIn('-EncodedCommand',argv)
        code=base64.b64decode(argv[-1]).decode('utf-16le')
        for required in ('Get-NetTCPConnection','Get-CimInstance Win32_Process','ConvertTo-Json','local_address','local_port','state','pid','-ErrorAction Stop'):
            self.assertIn(required,code)
        self.assertNotIn('netstat.exe',code)
        self.assertNotIn('Start-Process',code)
    def test_port_validation_before_subprocess(self):
        with patch.object(subject.subprocess,'run') as run:
            for v in (-1,0,65536,True,'12645'):
                with self.assertRaisesRegex(RuntimeError,'INVALID_TCP_PORT'):
                    subject.tcp_table_observation(v)
            run.assert_not_called()
    def test_wrong_schema_fails_closed(self):
        with patch.object(subject.subprocess,'run',return_value=SimpleNamespace(returncode=0,stdout='{}')):
            with self.assertRaisesRegex(RuntimeError,'SCHEMA_OR_PORT_MISMATCH'):
                subject.tcp_table_observation(subject.PORT)
    def test_nonzero_exit_fails_closed(self):
        with patch.object(subject.subprocess,'run',return_value=SimpleNamespace(returncode=1,stdout='ERROR',stderr='private')):
            with self.assertRaisesRegex(RuntimeError,'POWERSHELL_FAILED_RC_1'):
                subject.tcp_table_observation(subject.PORT)
    def test_invalid_json_fails_closed(self):
        with patch.object(subject.subprocess,'run',return_value=SimpleNamespace(returncode=0,stdout='NOT_JSON')):
            with self.assertRaisesRegex(RuntimeError,'INVALID_JSON'):
                subject.tcp_table_observation(subject.PORT)
    def test_too_big_response_fails_closed(self):
        with patch.object(subject.subprocess,'run',return_value=SimpleNamespace(returncode=0,stdout='A'*(65*1024))):
            with self.assertRaisesRegex(RuntimeError,'OUTPUT_TOO_LARGE'):
                subject.tcp_table_observation(subject.PORT)
    def test_no_accidental_v1v2_write_paths(self):
        self.assertTrue(str(subject.OUT).endswith('ttm_t5_ollama_compat_only_single_v3rc1'))
        self.assertEqual(subject.PORT,12645)
        self.assertNotIn('single_v2',str(subject.OUT))
        self.assertEqual(subject.MAX_TOKENS,32);self.assertEqual(subject.CONTEXT,256)
    def test_sourceonly_v3_remains_immutable_by_release(self):
        self.assertNotIn('V3_SOURCE_ONLY_EXECUTION_LOCK_NO_RUNTIME_PERMIT',SRC.read_text(encoding='utf-8'))
        self.assertEqual(subject.MODEL,'ttm-t5-f32-compat-only-v3rc1:latest')
        self.assertIn('single_v3rc1',str(subject.OUT))
        self.assertEqual(subject.EXE_SHA,'14e0fff0449ce3c3a7fe9db8b8b32089274db5f835d4c99f5af7c32dcbf08981')
    def test_contract_mode_does_not_touch_runtime(self):
        with patch.object(sys,'argv',['ignored','--mode','contract']),patch.object(subject,'source_pins',side_effect=AssertionError('no source PINs should execute')):
            self.assertEqual(subject.main(),0)
    def test_execute_argument_is_explicit_but_hardened(self):
        with patch.object(sys,'argv',['ignored','--mode','execute']), \
            patch.object(subject,'source_pins',side_effect=RuntimeError('PRECLAIM_PIN_FAILURE')), \
            patch.object(subject,'execute') as do_execute:
            self.assertEqual(subject.main(),3)
            do_execute.assert_not_called()

    def test_contract_preview_execute_only(self):
        with patch.object(sys,'argv',['ignored','--mode','unexpected']),self.assertRaises(SystemExit) as ctx:
            subject.main()
        self.assertEqual(ctx.exception.code,2)
    def test_independent_checker_no_real_ollama_or_ps(self):
        own=ast.parse(Path(__file__).read_text(encoding='utf8'))
        # Tests may patch subprocess.run but the checker itself does not call it.
        calls=[ast.unparse(x.func) for x in ast.walk(own) if isinstance(x,ast.Call)]
        self.assertNotIn('subprocess.run',calls)
        self.assertNotIn('subprocess.Popen',calls)
        self.assertNotIn('os.system',calls)
    def test_no_netstat_in_candidate(self):
        self.assertNotIn('netstat_listening_',SRC.read_text(encoding='utf8'))
    def test_proxy_explicitly_disabled_by_http(self):
        fn=subject.http_version_probe_direct
        self.assertIn('ProxyHandler({})',__import__('inspect').getsource(fn))




class FakeServer:
    def __init__(self,pid=87531): self.pid=pid; self.returncode=None
    def poll(self): return None


def fake_pins():
    return {'gguf':{'sha256':subject.GGUF_SHA,'size':subject.GGUF_BYTES,'path':str(subject.GGUF)},
            'original_fail':{'sha256':subject.ORIGINAL_SHA,'path':str(subject.ORIGINAL)},
            'v5b_fail':{'sha256':subject.V5B_SHA,'path':str(subject.V5B)},
            'ollama_exe':{'sha256':subject.EXE_SHA,'version':'ollama version is 0.40.14','path':str(subject.EXE)}}


class TestRC1FullPipeline(unittest.TestCase):
    """Mock end-to-end so the actual execute() path is verified without Ollama."""

    def simulate(self, *, create_rc=0, manifest=True, visible=True, done=True, tokens=8,
                 tag=True, force_server_exit=False):
        with qa_dir() as d:
            root=d
            out=d/'new-run'
            # Only mock transport and executable; actual result/trace files are written
            # in the isolated QA directory, never to a TTM science run directory.
            server=FakeServer()
            events=[]
            def fake_spawn(*a,**kw):
                events.append('serve')
                return server
            def fake_create(*a,**kw):
                events.append('create')
                return SimpleNamespace(returncode=create_rc,stdout='mock-create',stderr='mock-stderr')
            def fake_http(url,body=None,timeout=4):
                if url.endswith('/api/tags'):
                    events.append('tags')
                    return {'models':[{'name':subject.MODEL}]} if visible else {'models':[]}
                if url.endswith('/api/generate'):
                    events.append('generate')
                    self.assertEqual(body['options']['num_ctx'],256)
                    self.assertEqual(body['options']['num_predict'],32)
                    self.assertFalse(body['stream'])
                    self.assertTrue(body['raw'])
                    return {'model':subject.MODEL if tag else 'incorrect:latest','done':done,
                            'eval_count':tokens,'response':'hello'}
                raise AssertionError('unrecognized endpoint')
            def fake_hash(path):
                name=Path(path).name
                if name==subject.GGUF.name: return subject.GGUF_SHA
                if name==subject.EXE.name: return subject.EXE_SHA
                if name==subject.ORIGINAL.name: return subject.ORIGINAL_SHA
                if name==subject.V5B.name: return subject.V5B_SHA
                raise AssertionError('unknown pinned path: '+name)
            def fake_snapshot(path):
                if Path(path).name!='models':return {}
                if 'create' in events and create_rc==0:
                    return {'manifests/registry.ollama.ai/library/mock':{'sha256':'f'*64,'size':16}} if manifest else {}
                return {}
            def fake_env(root):
                env=subject.isolated_env_actual(root) if hasattr(subject,'isolated_env_actual') else None
                base={**__import__('os').environ,
                      'OLLAMA_HOST':subject.HOST,'OLLAMA_NO_CLOUD':'1','OLLAMA_MODELS':str(root/'models'),
                      'OLLAMA_TMPDIR':str(root/'tmp'),'TEMP':str(root/'tmp'),
                      'TMP':str(root/'tmp'),'HOME':str(root/'home'),
                      'USERPROFILE':str(root/'home'),
                      'APPDATA':str(root/'home'/'AppData'),
                      'LOCALAPPDATA':str(root/'home'/'LocalAppData'),
                      'PATH':'C:\\Windows\\System32','HOMEDRIVE':'D:', 'HOMEPATH':'\\WORK\\RESEARCH'}
                return base
            def fake_readiness(*a,**kw):
                events.append('ready')
                return {'identity_creation_date':'2026-11-09T00:00:00Z','ready':True}
            # All subprocesses and HTTP are mocks. No real TCP or Ollama call.
            with patch.multiple(subject,ROOT=root,OUT=out), \
                 patch.object(subject,'isolated_env',side_effect=fake_env), \
                 patch.object(subject.subprocess,'CREATE_NEW_PROCESS_GROUP',0,create=True), \
                 patch.object(subject.subprocess,'Popen',side_effect=fake_spawn), \
                 patch.object(subject.subprocess,'run',side_effect=fake_create), \
                 patch.object(subject,'sha256',side_effect=fake_hash), \
                 patch.object(subject,'folder_snapshot',side_effect=fake_snapshot), \
                 patch.object(subject,'tcp_table_observation',return_value={'rows':[]}), \
                 patch.object(subject,'observe_readiness_with_trace',side_effect=fake_readiness), \
                 patch.object(subject,'assert_owned_listener',return_value={'decision':'OWNED_LOOPBACK_LISTEN'}), \
                 patch.object(subject,'api_json',side_effect=fake_http), \
                 patch.object(subject,'stop_owned_server',return_value={'stop_status':'STOPPED_OWNED_TREE','taskkill_exit_code':0}):
                result=subject.execute(fake_pins())
            self.assertTrue((out/'CLAIM.json').is_file())
            self.assertTrue((out/'RESULT.json').is_file())
            self.assertEqual(json.loads((out/'RESULT.json').read_text())['status'],result['status'])
            self.assertTrue(result['science_train_or_test_executed'] is False)
            self.assertEqual(result['frozen_parity'],'FAIL_7_OF_8_PRESERVED')
            self.assertNotIn('status',fake_pins())
            self.assertIn('serve',events)
            return result,events

    def test_mocked_full_pipeline_positive(self):
        r,events=self.simulate()
        self.assertEqual(r['status'],'PASS_COMPATIBILITY_ONLY_OLLAMA_IMPORT_AND_INFERENCE')
        self.assertEqual(r['evaluation']['generated_tokens'],8)
        self.assertEqual(events,['serve','ready','create','tags','generate'])

    def test_mocked_full_pipeline_create_fail_preserves_result(self):
        r,events=self.simulate(create_rc=1)
        self.assertEqual(r['status'],'FAIL_OR_HOLD_COMPATIBILITY_ONLY_NO_RERUN')
        self.assertIn('OLLAMA_CREATE_FAILED',r['failure']['message'])
        self.assertNotIn('generate',events)

    def test_mocked_full_pipeline_no_local_manifest_never_generate(self):
        r,events=self.simulate(manifest=False)
        self.assertIn('CREATE_WITHOUT_PROJECT_LOCAL_MANIFEST',r['failure']['message'])
        self.assertNotIn('generate',events)

    def test_mocked_full_pipeline_model_not_visible_never_generate(self):
        r,events=self.simulate(visible=False)
        self.assertIn('PROJECT_LOCAL_SERVER_MODEL_TAG_NOT_VISIBLE',r['failure']['message'])
        self.assertNotIn('generate',events)

    def test_mocked_full_pipeline_no_done_is_fail(self):
        r,_=self.simulate(done=False)
        self.assertIn('GENERATION_NOT_CONFIRMED',r['failure']['message'])

    def test_mocked_full_pipeline_rejects_more_than_32_tokens(self):
        r,_=self.simulate(tokens=33)
        self.assertIn('GENERATION_NOT_CONFIRMED',r['failure']['message'])

    def test_mocked_full_pipeline_rejects_zero_generated_tokens(self):
        r,_=self.simulate(tokens=0)
        self.assertIn('GENERATION_NOT_CONFIRMED',r['failure']['message'])

    def test_mocked_full_pipeline_model_mismatch_is_fail(self):
        r,_=self.simulate(tag=False)
        self.assertIn('WRONG_RESPONSE_MODEL',r['failure']['message'])

    def test_child_env_scrubs_only_known_dll_directory(self):
        before='C:\\Windows\\System32;D:\\WORK\\RESEARCH\\TokenToModel-Lab\\_tmp\\ttm_t2\\build\\bin\\Release;C:\\other'
        with patch.dict(__import__('os').environ,{'PATH':before}):
            local=subject.isolated_env(subject.ROOT/'_tmp'/'fake')
            self.assertIn('C:\\Windows\\System32',local['PATH'])
            self.assertIn('C:\\other',local['PATH'])
            self.assertNotIn('ttm_t2',local['PATH'])
            self.assertIn('ttm_t2',__import__('os').environ['PATH'])

    def test_child_env_no_system_path_mutation(self):
        before=__import__('os').environ.get('PATH')
        subject.isolated_env(subject.ROOT/'_tmp'/'fake')
        self.assertEqual(__import__('os').environ.get('PATH'),before)

    def test_source_pins_has_exe_hash_pin(self):
        self.assertIn('EXE_SHA',''.join(__import__('inspect').getsource(subject.source_pins)))

    def test_source_pins_prior_claims_required(self):
        s=__import__('inspect').getsource(subject.source_pins)
        self.assertIn('V1_OUT',s);self.assertIn('V2_OUT',s)
        self.assertIn('CLAIM.json',s);self.assertIn('RESULT.json',s)

    def test_preview_no_claim_or_process(self):
        with patch.object(sys,'argv',['ignored','--mode','preview']), \
             patch.object(subject,'source_pins',return_value=fake_pins()), \
             patch.object(subject,'execute') as execute, \
             patch.object(subject.subprocess,'Popen') as popen:
            self.assertEqual(subject.main(),0)
            popen.assert_not_called();execute.assert_not_called()

    def test_execute_cli_invokes_exactly_once(self):
        outcome={'status':'FAIL_OR_HOLD_COMPATIBILITY_ONLY_NO_RERUN'}
        with patch.object(sys,'argv',['ignored','--mode','execute']), \
             patch.object(subject,'source_pins',return_value=fake_pins()), \
             patch.object(subject,'execute',return_value=outcome) as execute:
            self.assertEqual(subject.main(),4)
            execute.assert_called_once()

    def test_execute_stops_before_claim_if_pin_fails(self):
        with patch.object(sys,'argv',['ignored','--mode','execute']), \
             patch.object(subject,'source_pins',side_effect=RuntimeError('BAD_PIN')), \
             patch.object(subject,'execute') as execute:
            self.assertEqual(subject.main(),3)
            execute.assert_not_called()

    def test_anti_replay_directory_exists_is_not_overwritten(self):
        with qa_dir() as d:
            (d/'CLAIM.json').write_text('freeze',encoding='utf8')
            with self.assertRaisesRegex(RuntimeError,'EVIDENCE_ALREADY_EXISTS'):
                subject.write_json_x(d/'CLAIM.json',{'bad':True})
            self.assertEqual((d/'CLAIM.json').read_text(),'freeze')

    def test_anti_replay_output_already_exists(self):
        with qa_dir() as d:
            out=d/'run';out.mkdir()
            with self.assertRaises(FileExistsError):subject.new_dir(out)

    def test_windows_project_root_read_only_rules_present(self):
        s=__import__('inspect').getsource(subject.source_pins)
        self.assertIn('PYTHON312_WINDOWS_REQUIRED',s)
        self.assertIn('DISK_FREE_LT_1_GIB',s)
        self.assertIn('ONE_SHOT_EVIDENCE_DIR_ALREADY_EXISTS_NO_RERUN',s)
        self.assertIn('DEDICATED_IPV6_PORT_CONNECTABLE',s)

    def test_static_no_global_ollama_stop_or_pull(self):
        s=SRC.read_text('utf-8')
        self.assertNotIn('ollama pull',s)
        self.assertNotIn('ollama stop',s)
        self.assertNotIn('ollama run',s)
        self.assertNotIn('SetEnvironmentVariable(',s)

    def test_source_guard_version_v3rc1(self):
        self.assertEqual(subject.SCHEMA,'ttm.t5.ollama.compatibility.project-local.one-shot.v3rc1')
        self.assertEqual(subject.PORT,12645)
        self.assertEqual(subject.MAX_TOKENS,32)
        self.assertEqual(subject.CONTEXT,256)
        self.assertEqual(subject.API,'http://127.0.0.1:12645')

    def test_import_and_generate_endpoints_both_pinned_loopback(self):
        s=__import__('inspect').getsource(subject.api_json)
        self.assertIn('ProxyHandler({})',s)
        self.assertIn('url.startswith(API + "/")',s)

    def test_create_log_captured_no_unbounded_stdout(self):
        s=__import__('inspect').getsource(subject.execute)
        self.assertIn('create.stdout.log',s)
        self.assertIn('create.stderr.log',s)
        self.assertIn('timeout=180',s)

    def test_no_ollama_execution_in_unit_test_file(self):
        calls=[ast.unparse(x.func) for x in ast.walk(ast.parse(Path(__file__).read_text('utf-8'))) if isinstance(x,ast.Call)]
        self.assertNotIn('subprocess.run',calls)
        self.assertNotIn('subprocess.Popen',calls)
        self.assertNotIn('os.system',calls)


if __name__=='__main__':
    unittest.main(verbosity=2)
