"""Candidate Windows-only handle-relative atomic evidence publisher.

NOT security-qualified until effective DACL, directory identity and native W11/W12
are independently verified. Runs ONLY in a trusted broker process.
"""
from __future__ import annotations
import ctypes
from ctypes import wintypes
import hashlib
import os
import secrets

MAX_SINGLE_WRITE = 16 * 1024 * 1024  # bounded IPC; aggregate ledger limit remains 2GiB
ROOT_WORKTREE = r'D:\WORK\RESEARCH\TokenToModel-Lab\worktrees\p01-f0-static-i0a-20261105'
NT_FILE_CREATE = 2
FILE_NON_DIRECTORY_FILE = 0x40
FILE_SYNCHRONOUS_IO_NONALERT = 0x20
FILE_OPEN_REPARSE_POINT = 0x200000
OBJ_CASE_INSENSITIVE = 0x40
OBJ_DONT_REPARSE = 0x1000
GENERIC_READ = 0x80000000
GENERIC_WRITE = 0x40000000
DELETE = 0x10000
SYNCHRONIZE = 0x100000
FILE_SHARE_READ = 1
FILE_SHARE_WRITE = 2
FILE_SHARE_DELETE = 4
OPEN_EXISTING = 3
FILE_FLAG_BACKUP_SEMANTICS = 0x02000000
FILE_FLAG_OPEN_REPARSE_POINT = 0x00200000
FILE_ATTRIBUTE_REPARSE_POINT = 0x400
INVALID_HANDLE_VALUE = ctypes.c_void_p(-1).value

class AtomicWriteError(PermissionError): pass

class UNICODE_STRING(ctypes.Structure):
    _fields_ = [('Length', wintypes.USHORT), ('MaximumLength', wintypes.USHORT),
                ('Buffer', wintypes.LPWSTR)]
class OBJECT_ATTRIBUTES(ctypes.Structure):
    _fields_ = [('Length', wintypes.ULONG), ('RootDirectory', wintypes.HANDLE),
                ('ObjectName', ctypes.POINTER(UNICODE_STRING)), ('Attributes', wintypes.ULONG),
                ('SecurityDescriptor', ctypes.c_void_p), ('SecurityQualityOfService', ctypes.c_void_p)]
class IO_STATUS_BLOCK(ctypes.Structure):
    _fields_ = [('Status', ctypes.c_void_p), ('Information', ctypes.c_size_t)]
class FILE_RENAME_INFO(ctypes.Structure):
    _fields_ = [('ReplaceIfExists', ctypes.c_ubyte), ('RootDirectory', wintypes.HANDLE),
                ('FileNameLength', wintypes.DWORD), ('FileName', wintypes.WCHAR * 1)]
class FILE_DISPOSITION_INFO(ctypes.Structure):
    _fields_ = [('DeleteFile', wintypes.BOOL)]
class FILE_ATTRIBUTE_TAG_INFO(ctypes.Structure):
    _fields_ = [('FileAttributes', wintypes.DWORD), ('ReparseTag', wintypes.DWORD)]
class FILE_ID_INFO(ctypes.Structure):
    _fields_ = [('VolumeSerialNumber', ctypes.c_ulonglong), ('FileId', ctypes.c_ubyte * 16)]

class AtomicHandleWriter:
    def __init__(self, evidence_root: str):
        if os.name != 'nt' or ctypes.sizeof(ctypes.c_void_p) != 8:
            raise AtomicWriteError('WINDOWS_X64_REQUIRED')
        if not isinstance(evidence_root, str) or not os.path.isdir(evidence_root):
            raise AtomicWriteError('EXISTING_EVIDENCE_ROOT_REQUIRED')
        worktree = os.path.normcase(os.path.abspath(ROOT_WORKTREE))
        root = os.path.normcase(os.path.abspath(evidence_root))
        if os.path.commonpath([worktree, root]) != worktree or root == worktree:
            raise AtomicWriteError('EVIDENCE_ROOT_OUTSIDE_PINNED_WORKTREE')
        cur = root
        while cur and cur != os.path.dirname(cur):
            attrs = ctypes.windll.kernel32.GetFileAttributesW(cur)
            if attrs == 0xffffffff or attrs & FILE_ATTRIBUTE_REPARSE_POINT:
                raise AtomicWriteError('REPARSE_ANCESTOR_DENIED')
            cur = os.path.dirname(cur)
        self.k = ctypes.WinDLL('kernel32', use_last_error=True)
        self.nt = ctypes.WinDLL('ntdll', use_last_error=True)
        self._bind()
        self.root = self.open_root(evidence_root)
        self.root_identity = self._file_id(self.root)

    def _api(self, lib, name, args, ret):
        f = getattr(lib, name); f.argtypes = args; f.restype = ret; return f

    def _bind(self):
        H,D,B,P = wintypes.HANDLE,wintypes.DWORD,wintypes.BOOL,ctypes.c_void_p
        self.create_file = self._api(self.k, 'CreateFileW',
            [wintypes.LPCWSTR,D,D,P,D,D,H],H)
        self.close_file = self._api(self.k, 'CloseHandle',[H],B)
        self.get_info = self._api(self.k, 'GetFileInformationByHandleEx',[H,ctypes.c_int,P,D],B)
        self.set_info = self._api(self.k, 'SetFileInformationByHandle',[H,ctypes.c_int,P,D],B)
        self.write = self._api(self.k, 'WriteFile',[H,P,D,ctypes.POINTER(D),P],B)
        self.read = self._api(self.k, 'ReadFile',[H,P,D,ctypes.POINTER(D),P],B)
        self.seek = self._api(self.k, 'SetFilePointerEx',[H,ctypes.c_longlong,P,D],B)
        self.flush = self._api(self.k, 'FlushFileBuffers',[H],B)
        self.ntcreate = self._api(self.nt, 'NtCreateFile',
            [ctypes.POINTER(H),D,ctypes.POINTER(OBJECT_ATTRIBUTES),ctypes.POINTER(IO_STATUS_BLOCK),
             P,D,D,D,D,P,D],ctypes.c_long)

    def _file_id(self, handle: int):
        info=FILE_ID_INFO()
        if not self.get_info(handle,18,ctypes.byref(info),ctypes.sizeof(info)):
            raise AtomicWriteError('FILE_ID_QUERY_FAILED')
        return (info.VolumeSerialNumber,bytes(info.FileId))

    def open_root(self,path):
        h=self.create_file(path,GENERIC_READ,FILE_SHARE_READ, None,OPEN_EXISTING,
                           FILE_FLAG_BACKUP_SEMANTICS|FILE_FLAG_OPEN_REPARSE_POINT,None)
        if not h or int(h)==INVALID_HANDLE_VALUE:
            raise AtomicWriteError('ROOT_OPEN_FAILED')
        attrs=FILE_ATTRIBUTE_TAG_INFO()
        if not self.get_info(h,9,ctypes.byref(attrs),ctypes.sizeof(attrs)) or attrs.FileAttributes & FILE_ATTRIBUTE_REPARSE_POINT:
            self.close_file(h)
            raise AtomicWriteError('ROOT_REPARSE_OR_ATTRIBUTES_FAILED')
        return h

    def _create_relative(self,name):
        data=name.encode('utf-16-le')
        buf=ctypes.create_unicode_buffer(name)
        us=UNICODE_STRING(len(data),len(data)+2,ctypes.cast(buf,wintypes.LPWSTR))
        oa=OBJECT_ATTRIBUTES(ctypes.sizeof(OBJECT_ATTRIBUTES),self.root,ctypes.pointer(us),
                             OBJ_CASE_INSENSITIVE|OBJ_DONT_REPARSE,None,None)
        ios=IO_STATUS_BLOCK();h=wintypes.HANDLE()
        s=self.ntcreate(ctypes.byref(h),GENERIC_READ|GENERIC_WRITE|DELETE|SYNCHRONIZE,
                        ctypes.byref(oa),ctypes.byref(ios),None,0,0,NT_FILE_CREATE,
                        FILE_NON_DIRECTORY_FILE|FILE_SYNCHRONOUS_IO_NONALERT|FILE_OPEN_REPARSE_POINT,None,0)
        if s<0 or not h.value:
            raise AtomicWriteError('NT_CREATE_FAILED_%08X'%(s & 0xffffffff))
        return h.value

    def _rename_no_replace(self,handle,name):
        encoded=name.encode('utf-16-le')
        n=FILE_RENAME_INFO.FileName.offset+len(encoded)
        raw=ctypes.create_string_buffer(n)
        info=ctypes.cast(raw,ctypes.POINTER(FILE_RENAME_INFO)).contents
        info.ReplaceIfExists=0
        info.RootDirectory=self.root
        info.FileNameLength=len(encoded)
        ctypes.memmove(ctypes.addressof(raw)+FILE_RENAME_INFO.FileName.offset,encoded,len(encoded))
        if not self.set_info(handle,3,raw,n):
            raise AtomicWriteError('ATOMIC_RENAME_NO_REPLACE_FAILED_%d'%ctypes.get_last_error())

    def publish(self,name:str,content:bytes,expected_sha256:str):
        from durable_broker_quota_v1 import _name_key
        _name_key(name)
        if not isinstance(content,bytes) or len(content)>MAX_SINGLE_WRITE:
            raise AtomicWriteError('BOUNDED_BYTES_REQUIRED')
        digest=hashlib.sha256(content).hexdigest()
        if expected_sha256 != digest:
            raise AtomicWriteError('CONTENT_SHA256_MISMATCH')
        if self._file_id(self.root)!=self.root_identity:
            raise AtomicWriteError('ROOT_IDENTITY_CHANGED')
        stage='stage_'+secrets.token_hex(16)+'.tmp'
        h=self._create_relative(stage)
        committed=False
        try:
            offset=0
            while offset<len(content):
                chunk=content[offset:offset+1048576]
                b=ctypes.create_string_buffer(chunk)
                written=wintypes.DWORD()
                if not self.write(h,b,len(chunk),ctypes.byref(written),None) or written.value!=len(chunk):
                    raise AtomicWriteError('WRITE_FAILED_OR_PARTIAL')
                offset+=written.value
            if not self.flush(h) or not self.seek(h,0,None,0):
                raise AtomicWriteError('FLUSH_OR_REWIND_FAILED')
            sha=hashlib.sha256();read_total=0
            while read_total<len(content):
                n=min(1048576,len(content)-read_total)
                b=ctypes.create_string_buffer(n)
                got=wintypes.DWORD()
                if not self.read(h,b,n,ctypes.byref(got),None) or got.value==0:
                    raise AtomicWriteError('READBACK_FAILED')
                sha.update(b.raw[:got.value]);read_total+=got.value
            if sha.hexdigest()!=digest:
                raise AtomicWriteError('READBACK_HASH_MISMATCH')
            self._rename_no_replace(h,name)
            if not self.flush(h):
                raise AtomicWriteError('PUBLISHED_FLUSH_FAILED')
            committed=True
            return {'size':read_total,'sha256':digest,'file_id':self._file_id(h)[1].hex()}
        finally:
            if not committed:
                dispose=FILE_DISPOSITION_INFO(1)
                self.set_info(h,4,ctypes.byref(dispose),ctypes.sizeof(dispose))
            self.close_file(h)

    def close(self):
        if getattr(self,'root',None):
            if not self.close_file(self.root):
                raise AtomicWriteError('ROOT_CLOSE_FAILED')
            self.root=None
