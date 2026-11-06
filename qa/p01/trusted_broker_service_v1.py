"""P01 separate-process trusted broker candidate with authenticated local IPC.

No worker is started. The service refuses to run unless its Windows service
account SID, permitted broker root, and secret material are explicitly pinned.
Separate *process* does NOT imply separate *Windows identity*; SCM provisioning,
pipe DACL, secret ACL and worker denial need independent native attestation.
"""
from __future__ import annotations
import base64
import binascii
import ctypes
from ctypes import wintypes
import hashlib
import json
from multiprocessing.connection import Listener
import os
import sys

from durable_broker_quota_v1 import DurableQuotaLedger, QuotaRefusal

MAX_MESSAGE=24*1024*1024   # 16MiB content + base64 overhead
MAX_FILE=16*1024*1024
ROOT_WORKTREE=r'D:\WORK\RESEARCH\TokenToModel-Lab\worktrees\p01-f0-static-i0a-20261105'

class BrokerSecurityError(PermissionError):pass

class SID_AND_ATTRIBUTES(ctypes.Structure):
    _fields_=[('Sid',ctypes.c_void_p),('Attributes',wintypes.DWORD)]
class TOKEN_USER(ctypes.Structure):
    _fields_=[('User',SID_AND_ATTRIBUTES)]

def current_user_sid_win32():
    if os.name!='nt':raise BrokerSecurityError('WINDOWS_SERVICE_SID_REQUIRED')
    k=ctypes.WinDLL('kernel32',use_last_error=True)
    a=ctypes.WinDLL('advapi32',use_last_error=True)
    H=wintypes.HANDLE;D=wintypes.DWORD;B=wintypes.BOOL
    k.GetCurrentProcess.restype=H
    a.OpenProcessToken.argtypes=[H,D,ctypes.POINTER(H)];a.OpenProcessToken.restype=B
    a.GetTokenInformation.argtypes=[H,D,ctypes.c_void_p,D,ctypes.POINTER(D)]
    a.GetTokenInformation.restype=B
    a.ConvertSidToStringSidW.argtypes=[ctypes.c_void_p,ctypes.POINTER(wintypes.LPWSTR)]
    a.ConvertSidToStringSidW.restype=B
    k.CloseHandle.argtypes=[H];k.CloseHandle.restype=B
    k.LocalFree.argtypes=[ctypes.c_void_p];k.LocalFree.restype=ctypes.c_void_p
    h=H()
    if not a.OpenProcessToken(k.GetCurrentProcess(),8,ctypes.byref(h)):
        raise BrokerSecurityError('BROKER_TOKEN_OPEN_FAILED')
    try:
        needed=D()
        a.GetTokenInformation(h,1,None,0,ctypes.byref(needed))
        if needed.value<ctypes.sizeof(TOKEN_USER) or needed.value>65536:
            raise BrokerSecurityError('TOKEN_USER_LENGTH_INVALID')
        raw=ctypes.create_string_buffer(needed.value)
        if not a.GetTokenInformation(h,1,raw,needed,ctypes.byref(needed)):
            raise BrokerSecurityError('BROKER_TOKEN_QUERY_FAILED')
        user=ctypes.cast(raw,ctypes.POINTER(TOKEN_USER)).contents
        sidptr=wintypes.LPWSTR()
        if not a.ConvertSidToStringSidW(user.User.Sid,ctypes.byref(sidptr)):
            raise BrokerSecurityError('BROKER_SID_CONVERSION_FAILED')
        try:return sidptr.value
        finally:k.LocalFree(ctypes.cast(sidptr,ctypes.c_void_p))
    finally:k.CloseHandle(h)

def parse_request(packet:bytes):
    if type(packet) is not bytes or len(packet)>MAX_MESSAGE:
        raise BrokerSecurityError('IPC_FRAME_TOO_LARGE')
    try:
        request=json.loads(packet.decode('utf-8'))
    except (UnicodeError,ValueError) as e:
        raise BrokerSecurityError('INVALID_JSON_FRAME') from e
    if type(request) is not dict or set(request)!=set(('op','request_id','filename','size','sha256','data_b64')):
        raise BrokerSecurityError('UNKNOWN_OR_MISSING_PROTOCOL_FIELDS')
    if request['op']!='WRITE_NEW':
        raise BrokerSecurityError('OPERATION_NOT_ALLOWED')
    if type(request['size']) is not int or not 0<=request['size']<=MAX_FILE:
        raise BrokerSecurityError('WRITE_SIZE_NOT_ALLOWED')
    if type(request['data_b64']) is not str or len(request['data_b64'])>4*((MAX_FILE+2)//3):
        raise BrokerSecurityError('B64_FRAME_TOO_LARGE')
    try:payload=base64.b64decode(request['data_b64'],validate=True)
    except (binascii.Error,ValueError) as e:
        raise BrokerSecurityError('B64_INVALID') from e
    if len(payload)!=request['size']:
        raise BrokerSecurityError('SIZE_MISMATCH')
    if type(request['sha256']) is not str or hashlib.sha256(payload).hexdigest()!=request['sha256']:
        raise BrokerSecurityError('SHA256_MISMATCH')
    return request,payload

class BrokerHandler:
    """Can be unit-tested with a fake writer; never interprets worker paths."""
    def __init__(self,ledger,writer):self.ledger,self.writer=ledger,writer
    def apply(self,packet):
        request,payload=parse_request(packet)
        rid=request['request_id']
        if any(row.request_id == rid for row in self.ledger.snapshot()):
            raise BrokerSecurityError('REPLAY_EXISTING_REQUEST_DENIED')
        reservation=self.ledger.reserve(rid,request['filename'],len(payload))
        if reservation.state!='PENDING':
            raise BrokerSecurityError('REPLAY_NOT_REEXECUTED')
        try:
            receipt=self.writer.publish(request['filename'],payload,request['sha256'])
            if receipt['size']!=len(payload) or receipt['sha256']!=request['sha256']:
                raise BrokerSecurityError('WRITE_RECEIPT_MISMATCH')
            self.ledger.mark_committed(rid,exact_size=receipt['size'],verified_sha256=receipt['sha256'])
        except BaseException:
            try:self.ledger.mark_failed_held(rid)
            except Exception:pass  # never refund uncertainty
            raise
        return {'ok':True,'request_id':rid,'sha256':receipt['sha256'],'size':receipt['size']}

def serve_one_connection(*, pipe_name, authkey, expected_broker_sid, worker_sid,
                         evidence_root, ledger_path):
    """Provisioned trusted broker *entrypoint*, not a worker-launch path.

    Must be invoked under an independently provisioned distinct service identity.
    SCM, SDDL and secret permissions are external mandatory native QA gates.
    """
    if os.name!='nt':raise BrokerSecurityError('WINDOWS_ONLY')
    if (type(expected_broker_sid) is not str or not expected_broker_sid.startswith('S-1-') or
        type(worker_sid) is not str or not worker_sid.startswith('S-1-') or
        expected_broker_sid==worker_sid):
        raise BrokerSecurityError('DISTINCT_PINNED_WINDOWS_SIDS_REQUIRED')
    if current_user_sid_win32()!=expected_broker_sid:
        raise BrokerSecurityError('BROKER_PROCESS_IDENTITY_MISMATCH')
    if type(authkey) is not bytes or len(authkey)<32:
        raise BrokerSecurityError('AUTHENTICATED_CHANNEL_KEY_REQUIRED')
    if (type(pipe_name) is not str or not pipe_name.startswith(r'\\.\pipe\TTM_P01_L1_') or
        len(pipe_name)>200):
        raise BrokerSecurityError('PINNED_PIPE_NAMESPACE_REQUIRED')
    work=os.path.normcase(os.path.abspath(ROOT_WORKTREE))
    root=os.path.normcase(os.path.abspath(evidence_root))
    if os.path.commonpath([work,root])!=work or root==work:
        raise BrokerSecurityError('EVIDENCE_ROOT_OUT_OF_WORKTREE')
    if os.path.normcase(os.path.dirname(os.path.abspath(ledger_path)))!=root:
        raise BrokerSecurityError('LEDGER_MUST_SHARE_EVIDENCE_ROOT')
    from atomic_handle_writer_win32_v1 import AtomicHandleWriter
    writer=AtomicHandleWriter(root)
    handler=BrokerHandler(DurableQuotaLedger(ledger_path),writer)
    try:
        # Multiprocessing Listener authkey authenticates request channel using
        # HMAC. Native pipe DACL and service identity remain separate QA gates.
        with Listener(address=pipe_name,family='AF_PIPE',authkey=authkey) as listener:
            with listener.accept() as conn:
                packet=conn.recv_bytes(maxlength=MAX_MESSAGE)
                try:
                    result=handler.apply(packet)
                    conn.send_bytes(json.dumps(result,sort_keys=True).encode('utf-8'))
                except (BrokerSecurityError,QuotaRefusal) as e:
                    conn.send_bytes(json.dumps({'ok':False,'error':str(e)}).encode('utf-8'))
                    raise
    finally:writer.close()

if __name__=='__main__':
    raise SystemExit('NO_CLI_EXECUTION_WITHOUT_PINNED_NATIVE_SUPERVISOR')
