"""P01 security candidate: restricted write token and non-mutating DACL probes.

No worker launch, no ACL changes, and no execution authorization. A successful
probe covers ONLY the pinned directories, never the whole Windows filesystem.
"""
from __future__ import annotations
import ctypes
from ctypes import wintypes
import os

DISABLE_MAX_PRIVILEGE = 0x1
WRITE_RESTRICTED = 0x8
TOKEN_DUPLICATE = 0x2
TOKEN_QUERY = 0x8
TOKEN_ASSIGN_PRIMARY = 0x1
TOKEN_IMPERSONATE = 0x4
TOKEN_ADJUST_DEFAULT = 0x80
TOKEN_ADJUST_SESSIONID = 0x100
FILE_ADD_FILE = 0x2
FILE_ADD_SUBDIRECTORY = 0x4
DELETE = 0x10000
OPEN_EXISTING = 3
FILE_FLAG_BACKUP_SEMANTICS = 0x02000000
FILE_FLAG_OPEN_REPARSE_POINT = 0x00200000
ERROR_ACCESS_DENIED = 5
INVALID_HANDLE_VALUE = ctypes.c_void_p(-1).value
RESTRICTED_CODE_SID = 'S-1-5-12'

class WorkerIdentityFailure(PermissionError):
    pass

class SID_AND_ATTRIBUTES(ctypes.Structure):
    _fields_ = [('Sid', ctypes.c_void_p), ('Attributes', wintypes.DWORD)]

class RestrictedWorkerIdentity:
    def __init__(self):
        if os.name != 'nt' or ctypes.sizeof(ctypes.c_void_p) != 8:
            raise WorkerIdentityFailure('WINDOWS_X64_REQUIRED')
        self.k = ctypes.WinDLL('kernel32', use_last_error=True)
        self.a = ctypes.WinDLL('advapi32', use_last_error=True)
        self._setup()

    def _bind(self, lib, name, argtypes, restype):
        fun = getattr(lib, name)
        fun.argtypes, fun.restype = argtypes, restype
        return fun

    def _setup(self):
        H, D, B, P = wintypes.HANDLE, wintypes.DWORD, wintypes.BOOL, ctypes.c_void_p
        self.current = self._bind(self.k, 'GetCurrentProcess', [], H)
        self.close = self._bind(self.k, 'CloseHandle', [H], B)
        self.local_free = self._bind(self.k, 'LocalFree', [P], P)
        self.open_token = self._bind(self.a, 'OpenProcessToken', [H, D, ctypes.POINTER(H)], B)
        self.sid_from_string = self._bind(self.a, 'ConvertStringSidToSidW', [wintypes.LPCWSTR, ctypes.POINTER(P)], B)
        self.create_token = self._bind(self.a, 'CreateRestrictedToken',
            [H, D, D, P, D, P, D, ctypes.POINTER(SID_AND_ATTRIBUTES), ctypes.POINTER(H)], B)
        self.is_restricted = self._bind(self.a, 'IsTokenRestricted', [H], B)
        self.impersonate = self._bind(self.a, 'ImpersonateLoggedOnUser', [H], B)
        self.revert = self._bind(self.a, 'RevertToSelf', [], B)
        self.create_file = self._bind(self.k, 'CreateFileW',
            [wintypes.LPCWSTR, D, D, P, D, D, H], H)

    def restricted_primary_token(self) -> int:
        """Caller owns returned handle; MUST CloseHandle it on every path."""
        rights = (TOKEN_DUPLICATE | TOKEN_QUERY | TOKEN_ASSIGN_PRIMARY |
                  TOKEN_IMPERSONATE | TOKEN_ADJUST_DEFAULT | TOKEN_ADJUST_SESSIONID)
        original = wintypes.HANDLE()
        restricted = wintypes.HANDLE()
        sid = ctypes.c_void_p()
        if not self.open_token(self.current(), rights, ctypes.byref(original)):
            raise WorkerIdentityFailure('OPEN_PROCESS_TOKEN_FAILED')
        try:
            if not self.sid_from_string(RESTRICTED_CODE_SID, ctypes.byref(sid)):
                raise WorkerIdentityFailure('RESTRICTING_SID_INVALID')
            sid_item = SID_AND_ATTRIBUTES(sid, 0)
            if not self.create_token(original, DISABLE_MAX_PRIVILEGE | WRITE_RESTRICTED,
                                     0, None, 0, None, 1,
                                     ctypes.byref(sid_item), ctypes.byref(restricted)):
                raise WorkerIdentityFailure('CREATE_RESTRICTED_TOKEN_FAILED')
            if not self.is_restricted(restricted):
                raise WorkerIdentityFailure('TOKEN_RESTRICTING_SID_NOT_VERIFIED')
            value = int(restricted.value)
            restricted = wintypes.HANDLE()
            return value
        finally:
            if restricted.value:
                self.close(restricted)
            if sid.value:
                self.local_free(sid)
            self.close(original)

    def probe_denied_directory_write(self, token: int, path: str) -> dict:
        """OPEN_EXISTING only, so the probe never creates/changes a file.

        A denial on two directories is necessary but not sufficient to prove
        worker-wide filesystem confinement. Never accept a missing directory.
        """
        if type(token) is not int or token <= 0:
            raise WorkerIdentityFailure('INVALID_TOKEN')
        if type(path) is not str or not os.path.isabs(path) or not os.path.isdir(path):
            raise WorkerIdentityFailure('EXISTING_ABSOLUTE_DIRECTORY_REQUIRED')
        if os.path.islink(path):
            raise WorkerIdentityFailure('REPARSE_ROOT_NOT_ALLOWED')
        if not self.impersonate(wintypes.HANDLE(token)):
            raise WorkerIdentityFailure('IMPERSONATE_FAILED')
        handle = None
        try:
            handle = self.create_file(path, FILE_ADD_FILE | FILE_ADD_SUBDIRECTORY | DELETE,
                                      0x7, None, OPEN_EXISTING,
                                      FILE_FLAG_BACKUP_SEMANTICS | FILE_FLAG_OPEN_REPARSE_POINT,
                                      None)
            winerr = ctypes.get_last_error()
        finally:
            reverted = bool(self.revert())
        if handle and int(handle) != INVALID_HANDLE_VALUE:
            self.close(handle)
            raise WorkerIdentityFailure('UNBROKERED_WRITE_ACCESS_GRANTED')
        if not reverted:
            raise WorkerIdentityFailure('REVERT_TO_SELF_FAILED')
        if winerr != ERROR_ACCESS_DENIED:
            raise WorkerIdentityFailure('ACCESS_DENIAL_INCONCLUSIVE_WINERR_%s' % winerr)
        return {'path': path, 'denial_winerror': winerr,
                'access_test': 'WRITE_ON_EXISTING_DIRECTORY_ONLY',
                'scope': 'ONE_DIRECTORY_NOT_FILESYSTEM_PROOF'}
