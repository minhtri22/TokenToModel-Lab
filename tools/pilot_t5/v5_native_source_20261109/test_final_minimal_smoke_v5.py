#!/usr/bin/env python3
"""Independent pure-fixture / mocked-transport QA for TTM dual attestation.

No real Windows native API, PowerShell, Ollama, socket connection, model import,
training data access or network call. On Windows fixtures stay inside project _tmp.
"""
from __future__ import annotations
import ast
import contextlib
import ctypes
import importlib
import json
from pathlib import Path
import socket
import struct
import subprocess
import sys
import tempfile
import unittest
from types import SimpleNamespace
from unittest.mock import patch, Mock

HERE=Path(__file__).resolve().parent
sys.path.insert(0,str(HERE))
m=importlib.import_module('t5_final_minimal_smoke_v5')
n=importlib.import_module('t5_native_tcp')
PID=24680
DATE='2026-11-09T01:00:00Z'

class Proc:
    def __init__(self,pid=PID,rc=None):self.pid=pid;self.rc=rc;self.returncode=rc
    def poll(self):return self.rc


def row(fam='IPv4',addr='127.0.0.1',state=0,pid=PID,port=None,remote=None,remote_port=0):
    if port is None:port=m.PORT
    if fam=='IPv6' and addr=='127.0.0.1':addr='::1'
    if remote is None: remote='0.0.0.0' if fam=='IPv4' else '::'
    return {'address_family':fam,'local_address':addr,'local_port':port,
            'remote_address':remote,'remote_port':remote_port,'pid':pid,
            'state_code':state,'state_verified_listen':state==2}

def identity(pid=PID,creation=DATE,path=None,name='ollama.exe'):
    return {'pid':pid,'name':name,'executable_path':str(m.EXE) if path is None else path,'creation_date':creation}

def snapshot(rows=None,processes=None,port=None,families=None):
    return {'schema':'ttm.t5.native.tcptable.dual.v1',
            'port':m.PORT if port is None else port,
            'rows':[row()] if rows is None else rows,
            'processes':[identity()] if processes is None else processes,
            'families_queried':['IPv4','IPv6'] if families is None else families}

def good_http(_):
    return {'attempted':True,'http_status':200,'api_version':m.VERSION,
            'error_type':None,'error_code':None}

class Sequence:
    def __init__(self,*items):self.items=list(items);self.i=0
    def __call__(self,p):
        if p!=m.PORT:raise AssertionError('WRONG_PORT')
        i=self.i;self.i+=1
        if i>=len(self.items):raise AssertionError('NO_MORE_SNAPSHOTS')
        item=self.items[i]
        if isinstance(item,Exception):raise item
        return item

@contextlib.contextmanager
def fixture_dir():
    if sys.platform=='win32':
        root=Path(r'D:\WORK\RESEARCH\TokenToModel-Lab\_tmp')
        if not root.is_dir():raise RuntimeError('QA_PROJECT_LOCAL_TMP_MISSING')
    else:root=HERE
    with tempfile.TemporaryDirectory(prefix='ttm_t5_final_qa_',dir=str(root)) as path:
        yield Path(path)

def packet4(state=0,addr='127.0.0.1',remote='0.0.0.0',port=None,pid=PID,remote_port=0):
    if port is None:port=m.PORT
    r=n.Tcp4Row();r.state=state;r.pid=pid
    r.local_addr=int.from_bytes(socket.inet_aton(addr),sys.byteorder)
    r.remote_addr=int.from_bytes(socket.inet_aton(remote),sys.byteorder)
    r.local_port=socket.htons(port);r.remote_port=socket.htons(remote_port)
    return bytes(r)

def packet6(state=0,addr='::1',remote='::',port=None,pid=PID,remote_port=0):
    if port is None:port=m.PORT
    r=n.Tcp6Row();r.state=state;r.pid=pid
    for i,b in enumerate(socket.inet_pton(socket.AF_INET6,addr)):r.local_addr[i]=b
    for i,b in enumerate(socket.inet_pton(socket.AF_INET6,remote)):r.remote_addr[i]=b
    r.local_port=socket.htons(port);r.remote_port=socket.htons(remote_port)
    return bytes(r)

def table(*rows):return struct.pack('<I',len(rows))+b''.join(rows)

class TestReleaseGuard(unittest.TestCase):
    def test_port_and_model_dedicated(self):
        self.assertEqual(m.PORT,12648)
        self.assertNotIn(m.PORT,(11434,12643,12644,12645,12646,12647))
        self.assertIn('v5final',str(m.OUT)); self.assertIn('v5final',m.MODEL)
    def test_exact_gguf_and_ollama_pins(self):
        self.assertEqual((m.GGUF_SHA,m.EXE_SHA),
            ('5bdc904e6c51af04a4223219f36e6bc2e687f60fd6e17dc24508f3eb7489e4e5',
             '14e0fff0449ce3c3a7fe9db8b8b32089274db5f835d4c99f5af7c32dcbf08981'))
        self.assertEqual((m.CONTEXT,m.MAX_TOKENS),(256,32))
    def test_cli_contract_does_not_start_server(self):
        with patch.object(m,'source_pins',side_effect=AssertionError('NO PRECLAIM')), \
             patch.object(m.subprocess,'Popen',side_effect=AssertionError('NO SERVE')):
            with patch('sys.argv',['runner','--mode','contract']):
                self.assertEqual(m.main(),0)
    def test_preview_uses_pin_but_never_create_claim(self):
        pins={'gguf':{'sha256':m.GGUF_SHA},'ollama_exe':{'sha256':m.EXE_SHA,'version':'ollama version is 0.40.14'}}
        with patch.object(m,'source_pins',return_value=pins),patch.object(m,'execute',side_effect=AssertionError('SHOULD_NOT_EXECUTE')):
            with patch('sys.argv',['runner','--mode','preview']): self.assertEqual(m.main(),0)
    def test_preview_fail_closed_on_bad_pin(self):
        with patch.object(m,'source_pins',side_effect=RuntimeError('BAD_SHA')), \
             patch.object(m,'execute',side_effect=AssertionError('EXECUTE_CALLED')):
            with patch('sys.argv',['runner','--mode','preview']): self.assertEqual(m.main(),3)
    def test_execute_calls_exactly_once(self):
        pins={'gguf':{'sha256':m.GGUF_SHA},'ollama_exe':{'sha256':m.EXE_SHA,'version':'ollama version is 0.40.14'}}
        with patch.object(m,'source_pins',return_value=pins),patch.object(m,'execute',return_value={'status':'PASS_COMPATIBILITY_ONLY_OLLAMA_IMPORT_AND_INFERENCE'}) as fake:
            with patch('sys.argv',['runner','--mode','execute']):self.assertEqual(m.main(),0)
            fake.assert_called_once_with(pins)
    def test_execute_hold_has_nonzero_exit(self):
        pins={'gguf':{'sha256':m.GGUF_SHA},'ollama_exe':{'sha256':m.EXE_SHA,'version':'ollama version is 0.40.14'}}
        with patch.object(m,'source_pins',return_value=pins),patch.object(m,'execute',return_value={'status':'FAIL_OR_HOLD_COMPATIBILITY_ONLY_NO_RERUN'}):
            with patch('sys.argv',['runner','--mode','execute']):self.assertEqual(m.main(),4)
    def test_no_global_service_commands(self):
        source=Path(m.__file__).read_text(encoding='utf-8')
        self.assertIn('OLLAMA_NO_CLOUD',source)
        self.assertNotIn('ollama stop',source);self.assertNotIn('ollama pull',source)
        self.assertNotIn('os.environ["PATH"]',source)
    def test_local_http_proxy_bypass(self):
        import inspect
        self.assertIn('ProxyHandler({})',inspect.getsource(m.api_json))
        self.assertIn('ProxyHandler({})',inspect.getsource(m.http_version_probe_direct))
    def test_unknown_tcp_state_not_claimed_listen(self):
        d=m.ownership_status(snapshot(),PID)
        self.assertEqual(d['decision'],'OWNED_LOOPBACK_CANDIDATE_ONLY')
        self.assertEqual(d['unknown_state_count'],1);self.assertEqual(d['confirmed_listen_count'],0)
    def test_loopback_wildcard_rejected(self):
        for a in ('0.0.0.0','192.168.1.2'):
            self.assertEqual(m.ownership_status(snapshot(rows=[row(addr=a)]),PID)['decision'],'HOLD_NON_LOOPBACK_OR_WILDCARD')
    def test_wrong_pid_rejected(self):
        self.assertEqual(m.ownership_status(snapshot(rows=[row(pid=PID+1)]),PID)['decision'],'HOLD_UNTRUSTED_PID')
    def test_changed_creation_rejected(self):
        self.assertEqual(m.ownership_status(snapshot(processes=[identity(creation='NEW')]),PID,expected_creation=DATE)['decision'],'HOLD_PROCESS_REPLACED')
    def test_state_zero_nonzero_remote_rejected(self):
        self.assertEqual(m.ownership_status(snapshot(rows=[row(remote_port=1)]),PID)['decision'],'HOLD_STATE_ZERO_WITH_NONZERO_REMOTE')
    def test_state_two_exact_loopback_ok(self):
        self.assertEqual(m.ownership_status(snapshot(rows=[row(state=2)]),PID)['confirmed_listen_count'],1)
    def test_native_parser_0_remains_unknown(self):
        s=n.parse_table(table(packet4()),n.AF_INET,m.PORT)
        self.assertEqual(s[0]['state_code'],0);self.assertFalse(s[0]['state_verified_listen'])
    def test_native_parser_bad_count_rejected(self):
        with self.assertRaises(ValueError):n.parse_table(struct.pack('<I',2)+packet4(),n.AF_INET,m.PORT)
    def test_native_parser_ipv6(self):
        self.assertEqual(n.parse_table(table(packet6()),n.AF_INET6,m.PORT)[0]['local_address'],'::1')
    def test_http_dual_attestation_success(self):
        sample=m.readiness_sample(Proc(),1,tcp_fn=Sequence(snapshot(),snapshot()),http_fn=good_http)
        self.assertEqual(sample['decision'],'READY_DUAL_ATTESTED_STATE_ZERO_UNKNOWN')
        self.assertFalse(sample['attestation']['native_listen_confirmed'])
    def test_http_200_alone_not_sufficient(self):
        sample=m.readiness_sample(Proc(),1,tcp_fn=Sequence(snapshot(rows=[],processes=[])),http_fn=good_http)
        self.assertNotIn('READY',sample['decision'])
    def test_http_wrong_version(self):
        sample=m.readiness_sample(Proc(),1,tcp_fn=Sequence(snapshot()),http_fn=lambda u:{**good_http(u),'api_version':'0.41.0'})
        self.assertEqual(sample['decision'],'WAIT_HTTP_INVALID_OR_WRONG_VERSION')
    def test_http_owner_changed(self):
        sample=m.readiness_sample(Proc(),1,tcp_fn=Sequence(snapshot(),snapshot(rows=[row(pid=12345)])),http_fn=good_http)
        self.assertEqual(sample['decision'],'HOLD_OWNER_CHANGED_AFTER_HTTP')
    def test_http_socket_state_changed(self):
        sample=m.readiness_sample(Proc(),1,tcp_fn=Sequence(snapshot(),snapshot(rows=[row(state=2)])),http_fn=good_http)
        self.assertEqual(sample['decision'],'HOLD_CANDIDATE_CHANGED_AFTER_HTTP')
    def test_trace_exclusive_no_overwrite(self):
        with fixture_dir() as d:
            (d/'READINESS_ATTEMPTS.jsonl').write_text('previous\n',encoding='utf-8')
            with self.assertRaises(FileExistsError):m.observe_readiness_with_trace(Proc(),d,max_samples=1)
            self.assertEqual((d/'READINESS_ATTEMPTS.jsonl').read_text(),'previous\n')
    def test_trace_ready_persisted(self):
        with fixture_dir() as d:
            x=m.observe_readiness_with_trace(Proc(),d,tcp_fn=Sequence(snapshot(),snapshot()),http_fn=good_http,max_samples=1)
            self.assertTrue(x['ready']);self.assertEqual(len((d/'READINESS_ATTEMPTS.jsonl').read_text().splitlines()),1)
    def test_failure_preserves_artifacts(self):
        with fixture_dir() as d:
            with self.assertRaisesRegex(RuntimeError,'READINESS_HOLD_UNTRUSTED_PID'):
                m.observe_readiness_with_trace(Proc(),d,tcp_fn=Sequence(snapshot(rows=[row(pid=111)])),http_fn=good_http,max_samples=1)
            self.assertTrue((d/'READINESS_ATTEMPTS.jsonl').is_file())
    def test_child_path_filter_never_mutates_parent(self):
        import os
        environ={'PATH':r'C:\Windows\System32;D:\WORK\RESEARCH\TokenToModel-Lab\_tmp\ttm_t2\build\bin\Release'}
        old=dict(environ)
        with patch.object(m.os,'environ',environ):
            env=m.isolated_env(Path(r'D:\WORK\RESEARCH\TokenToModel-Lab\_tmp\ttm_t5_ollama_compat_only_single_v5final'))
        self.assertEqual(environ,old)
        self.assertNotIn('ggml-base',env['PATH'])
        self.assertNotIn('ttm_t2',env['PATH'])
    def test_evidence_dir_creation_exclusive(self):
        with fixture_dir() as d:
            m.new_dir(d/'claim');
            with self.assertRaises(FileExistsError):m.new_dir(d/'claim')

class TestMockedFullSmoke(unittest.TestCase):
    def simulate(self,*,create_rc=0,manifest=True,visible=True,done=True,tokens=8,tag=True,shutdown_rows=None):
        with fixture_dir() as d:
            out=d/'one-shot-v5';events=[];proc=Proc(pid=PID)
            def fake_spawn(*args,**kwargs):events.append('serve');return proc
            def fake_run(*args,**kwargs):events.append('create');return SimpleNamespace(returncode=create_rc,stdout='mock',stderr='mock')
            def fake_api(url,body=None,timeout=4):
                if url.endswith('/api/tags'):
                    events.append('tags');return {'models':[{'name':m.MODEL}]} if visible else {'models':[]}
                if url.endswith('/api/generate'):
                    events.append('generate')
                    self.assertEqual(body['options']['num_ctx'],256)
                    self.assertEqual(body['options']['num_predict'],32)
                    self.assertTrue(body['raw']);self.assertFalse(body['stream'])
                    return {'model':m.MODEL if tag else 'other','done':done,'eval_count':tokens,'response':'MOCK_TEXT'}
                raise AssertionError('wrong endpoint')
            def fake_sha(p):return {m.GGUF.name:m.GGUF_SHA,m.EXE.name:m.EXE_SHA,m.ORIGINAL.name:m.ORIGINAL_SHA,m.V5B.name:m.V5B_SHA}[Path(p).name]
            def fake_store(p):
                if Path(p).name=='models' and 'create' in events and create_rc==0 and manifest:
                    return {'manifests/registry.ollama.ai/library/ttm':{'sha256':'f'*64,'size':16}}
                return {}
            def fake_env(r):
                return {**__import__('os').environ,'OLLAMA_HOST':m.HOST,'OLLAMA_NO_CLOUD':'1','OLLAMA_MODELS':str(r/'models'),
                        'OLLAMA_TMPDIR':str(r/'tmp'),'TEMP':str(r/'tmp'),'TMP':str(r/'tmp'),'HOME':str(r/'home'),
                        'USERPROFILE':str(r/'home'),'APPDATA':str(r/'home'/'AppData'),'LOCALAPPDATA':str(r/'home'/'LocalAppData'),
                        'HOMEDRIVE':'D:','HOMEPATH':r'\WORK\RESEARCH'}
            pins={'gguf':{'sha256':m.GGUF_SHA,'size':m.GGUF_BYTES,'path':str(m.GGUF)},
                  'original_fail':{'sha256':m.ORIGINAL_SHA},'v5b_fail':{'sha256':m.V5B_SHA},
                  'ollama_exe':{'sha256':m.EXE_SHA}}
            with patch.multiple(m,ROOT=d,OUT=out),patch.object(m,'isolated_env',side_effect=fake_env),\
                 patch.object(m.subprocess,'CREATE_NEW_PROCESS_GROUP',0,create=True),\
                 patch.object(m.subprocess,'Popen',side_effect=fake_spawn),\
                 patch.object(m.subprocess,'run',side_effect=fake_run),\
                 patch.object(m,'sha256',side_effect=fake_sha),\
                 patch.object(m,'folder_snapshot',side_effect=fake_store),\
                 patch.object(m,'tcp_table_observation',return_value={'rows':[] if shutdown_rows is None else shutdown_rows}),\
                 patch.object(m,'observe_readiness_with_trace',return_value={'identity_creation_date':DATE,'ready':True}),\
                 patch.object(m,'assert_owned_listener',return_value={'decision':'READY_DUAL_ATTESTED_STATE_ZERO_UNKNOWN'}),\
                 patch.object(m,'api_json',side_effect=fake_api),\
                 patch.object(m,'stop_owned_server',return_value={'stop_status':'STOPPED_OWNED_TREE','taskkill_exit_code':0}):
                result=m.execute(pins)
            self.assertTrue((out/'CLAIM.json').is_file())
            self.assertTrue((out/'RESULT.json').is_file())
            self.assertEqual(json.loads((out/'RESULT.json').read_text())['status'],result['status'])
            self.assertFalse(result['science_train_or_test_executed'])
            self.assertEqual(result['frozen_parity'],'FAIL_7_OF_8_PRESERVED')
            return result,events
    def test_positive_mock_full_pipeline(self):
        r,e=self.simulate();self.assertEqual(r['status'],'PASS_COMPATIBILITY_ONLY_OLLAMA_IMPORT_AND_INFERENCE');self.assertEqual(e,['serve','create','tags','generate'])
    def test_full_mock_pipeline_after_shutdown_pid0_timewait(self):
        r,e=self.simulate(shutdown_rows=[row(pid=0,state=11,remote='127.0.0.1',remote_port=53457)])
        self.assertEqual(r['status'],'PASS_COMPATIBILITY_ONLY_OLLAMA_IMPORT_AND_INFERENCE')
        self.assertEqual(r['shutdown_port_adjudication']['benign_timewait_count'],1)
        self.assertIn('generate',e)
    def test_create_fail_stops_before_generate(self):
        r,e=self.simulate(create_rc=1);self.assertIn('OLLAMA_CREATE_FAILED',r['failure']['message']);self.assertNotIn('generate',e)
    def test_missing_manifest_stops_before_generate(self):
        r,e=self.simulate(manifest=False);self.assertIn('MANIFEST',r['failure']['message']);self.assertNotIn('generate',e)
    def test_tag_not_visible_stops_before_generate(self):
        r,e=self.simulate(visible=False);self.assertIn('MODEL_TAG_NOT_VISIBLE',r['failure']['message']);self.assertNotIn('generate',e)
    def test_token_over_32_rejected(self):
        r,e=self.simulate(tokens=33);self.assertIn('GENERATION_NOT_CONFIRMED',r['failure']['message'])
    def test_no_done_rejected(self):
        r,e=self.simulate(done=False);self.assertIn('GENERATION_NOT_CONFIRMED',r['failure']['message'])
    def test_wrong_model_rejected(self):
        r,e=self.simulate(tag=False);self.assertIn('WRONG_RESPONSE_MODEL',r['failure']['message'])


class TestNativeTimeWaitRegression(unittest.TestCase):
    @staticmethod
    def extra_timewait(fam='IPv4', pid=0, state=11, local=None, remote=None, port=None):
        if local is None: local='127.0.0.1' if fam=='IPv4' else '::1'
        if remote is None: remote=local
        return row(fam=fam,addr=local,remote=remote,remote_port=53457,pid=pid,state=state,port=port)

    def test_timewait_pid_zero_keeps_owner(self):
        # Real V4 recorded this after /api/version: the actual listener PID
        # was still 34192; the incidental PID0 TIME_WAIT did not own it.
        s=snapshot(rows=[self.extra_timewait(),row()])
        result=m.ownership_status(s,PID)
        self.assertEqual(result['decision'],'OWNED_LOOPBACK_CANDIDATE_ONLY')
        self.assertEqual(result['owner_pids'],[PID])

    def test_pid_zero_non_timewait_rejected(self):
        s=snapshot(rows=[row(),self.extra_timewait(state=8)])
        self.assertEqual(m.ownership_status(s,PID)['decision'],'HOLD_UNTRUSTED_PID')

    def test_pid_zero_timewait_nonloopback_rejected(self):
        s=snapshot(rows=[row(),self.extra_timewait(local='0.0.0.0')])
        self.assertEqual(m.ownership_status(s,PID)['decision'],'HOLD_NON_LOOPBACK_OR_WILDCARD')

    def test_pid_zero_timewait_wrong_remote_rejected(self):
        s=snapshot(rows=[row(),self.extra_timewait(remote='192.168.1.7')])
        self.assertEqual(m.ownership_status(s,PID)['decision'],'HOLD_UNTRUSTED_PID')

    def test_pid_foreign_listener_never_ignored(self):
        s=snapshot(rows=[row(),row(pid=PID+2)])
        self.assertEqual(m.ownership_status(s,PID)['decision'],'HOLD_UNTRUSTED_PID')

    def test_timewait_after_http_with_stable_owner_readiness_passes(self):
        before=snapshot(rows=[row(state=8,remote='127.0.0.1',remote_port=53444),row()])
        after=snapshot(rows=[self.extra_timewait(),row()])
        result=m.readiness_sample(Proc(),4,tcp_fn=Sequence(before,after),http_fn=good_http)
        self.assertEqual(result['decision'],'READY_DUAL_ATTESTED_STATE_ZERO_UNKNOWN')
        self.assertEqual(result['http']['http_status'],200)

    def test_identity_query_ignores_timewait_pid_zero(self):
        stub={'schema':'ttm.t5.native.tcptable.dual.v1','port':m.PORT,
              'families_queried':['IPv4','IPv6'],'rows':[self.extra_timewait(),row()]}
        from unittest.mock import Mock
        identity_stub=Mock(return_value=identity())
        with patch.object(m.t5_native_tcp,'capture',return_value=stub):
            snap=m.tcp_table_observation(m.PORT,identity_fn=identity_stub)
        identity_stub.assert_called_once_with(PID)
        self.assertEqual(snap['processes'],[identity()])

    def test_shutdown_timewait_is_benign_not_server_running(self):
        rows=[self.extra_timewait()]
        result=m.classify_shutdown_port_rows(rows,m.PORT)
        self.assertEqual(result['decision'],'PASS_NO_ACTIVE_SOCKET_AFTER_SHUTDOWN')
        self.assertEqual(result['benign_timewait_count'],1)

    def test_shutdown_active_listener_still_holds(self):
        result=m.classify_shutdown_port_rows([row()],m.PORT)
        self.assertEqual(result['decision'],'HOLD_UNSAFE_PORT_ROW_AFTER_SHUTDOWN')

    def test_shutdown_pid_zero_non_timewait_holds(self):
        result=m.classify_shutdown_port_rows([self.extra_timewait(state=8)],m.PORT)
        self.assertEqual(result['decision'],'HOLD_UNSAFE_PORT_ROW_AFTER_SHUTDOWN')

    def test_listen_with_remote_endpoint_holds(self):
        s=snapshot(rows=[row(state=2,remote='127.0.0.1',remote_port=3)])
        self.assertEqual(m.ownership_status(s,PID)['decision'],'HOLD_LISTEN_WITH_REMOTE_ENDPOINT')


if __name__=='__main__':
    unittest.main(verbosity=2)
