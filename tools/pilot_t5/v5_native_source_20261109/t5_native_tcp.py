#!/usr/bin/env python3
"""Pure parsing plus read-only IP Helper GetExtendedTcpTable for a pinned TCP port.

No CLI; all accesses fail closed. Does not infer LISTEN from state code zero.
"""
from __future__ import annotations
import ctypes
import ipaddress
import socket
import struct
import sys

DWORD = ctypes.c_uint32
BOOL = ctypes.c_int
AF_INET = socket.AF_INET
AF_INET6 = socket.AF_INET6
TCP_TABLE_OWNER_PID_ALL = 5
ERROR_INSUFFICIENT_BUFFER = 122
MAX_TABLE_BYTES = 16 * 1024 * 1024
MAX_ENTRIES = 200000
VALID_STATES = set(range(1, 13))

class Tcp4Row(ctypes.Structure):
    _fields_ = [("state", DWORD), ("local_addr", DWORD), ("local_port", DWORD),
                ("remote_addr", DWORD), ("remote_port", DWORD), ("pid", DWORD)]

class Tcp6Row(ctypes.Structure):
    _fields_ = [("local_addr", ctypes.c_ubyte * 16), ("local_scope_id", DWORD),
                ("local_port", DWORD), ("remote_addr", ctypes.c_ubyte * 16),
                ("remote_scope_id", DWORD), ("remote_port", DWORD),
                ("state", DWORD), ("pid", DWORD)]

def validate_layout():
    if (ctypes.sizeof(DWORD), ctypes.sizeof(Tcp4Row), ctypes.sizeof(Tcp6Row)) != (4, 24, 56):
        raise RuntimeError('IPHELPER_LAYOUT_INVALID')
    if (Tcp4Row.state.offset, Tcp4Row.pid.offset, Tcp6Row.state.offset, Tcp6Row.pid.offset) != (0, 20, 48, 52):
        raise RuntimeError('IPHELPER_OFFSETS_INVALID')

def parse_table(raw: bytes, family: int, port: int) -> list[dict]:
    validate_layout()
    if type(port) is not int or port < 1 or port > 65535:
        raise ValueError('PORT_OUT_OF_RANGE')
    if family not in (AF_INET, AF_INET6):
        raise ValueError('INVALID_AF')
    if type(raw) is not bytes or not 4 <= len(raw) <= MAX_TABLE_BYTES:
        raise ValueError('INVALID_BUFFER')
    cls = Tcp4Row if family == AF_INET else Tcp6Row
    count = struct.unpack_from('<I', raw, 0)[0]
    start = 4
    size = ctypes.sizeof(cls)
    if count > MAX_ENTRIES or start + count * size > len(raw):
        raise ValueError('COUNT_OUT_OF_BOUNDS')
    output = []
    for i in range(count):
        row = cls.from_buffer_copy(raw, start + i * size)
        local_port = socket.ntohs(int(row.local_port) & 0xFFFF)
        if local_port != port:
            continue
        remote_port = socket.ntohs(int(row.remote_port) & 0xFFFF)
        if family == AF_INET:
            la = str(ipaddress.IPv4Address(int(row.local_addr).to_bytes(4, sys.byteorder)))
            ra = str(ipaddress.IPv4Address(int(row.remote_addr).to_bytes(4, sys.byteorder)))
            family_name = 'IPv4'
        else:
            la = str(ipaddress.IPv6Address(bytes(row.local_addr)))
            ra = str(ipaddress.IPv6Address(bytes(row.remote_addr)))
            family_name = 'IPv6'
        output.append({'address_family':family_name,'local_address':la,'local_port':local_port,
                       'remote_address':ra,'remote_port':remote_port,'pid':int(row.pid),
                       'state_code':int(row.state),
                       'state_verified_listen':int(row.state)==2})
        if len(output) > 64:
            raise ValueError('TARGET_PORT_TOO_MANY_ROWS')
    return output

def native_table(family: int) -> bytes:
    if sys.platform != 'win32':
        raise RuntimeError('NATIVE_WINDOWS_ONLY')
    if family not in (AF_INET, AF_INET6):
        raise ValueError('INVALID_FAMILY')
    validate_layout()
    fn = ctypes.WinDLL('iphlpapi.dll').GetExtendedTcpTable
    fn.argtypes = (ctypes.c_void_p, ctypes.POINTER(DWORD), BOOL, DWORD, ctypes.c_int, DWORD)
    fn.restype = DWORD
    size = DWORD(0)
    rc = fn(None, ctypes.byref(size), False, family, TCP_TABLE_OWNER_PID_ALL, 0)
    if rc not in (0, ERROR_INSUFFICIENT_BUFFER) or not 4 <= size.value <= MAX_TABLE_BYTES:
        raise RuntimeError('IPHLPAPI_PREFLIGHT_FAILED')
    for _ in range(3):
        allocated = size.value
        buf = ctypes.create_string_buffer(allocated)
        rc = fn(buf, ctypes.byref(size), False, family, TCP_TABLE_OWNER_PID_ALL, 0)
        if rc == 0:
            if not 4 <= size.value <= allocated:
                raise RuntimeError('IPHLPAPI_RETURN_SIZE_INVALID')
            return bytes(buf.raw[:size.value])
        if rc != ERROR_INSUFFICIENT_BUFFER or not allocated < size.value <= MAX_TABLE_BYTES:
            raise RuntimeError('IPHLPAPI_ENUMERATION_FAILED')
    raise RuntimeError('IPHLPAPI_UNSTABLE_TABLE')

def capture(port: int, native_fn=None) -> dict:
    if type(port) is not int or not 1 <= port <= 65535:
        raise ValueError('PORT_OUT_OF_RANGE')
    if native_fn is None:
        native_fn = native_table
    # Both families are required; one family error makes entire snapshot unusable.
    ipv4 = parse_table(native_fn(AF_INET), AF_INET, port)
    ipv6 = parse_table(native_fn(AF_INET6), AF_INET6, port)
    return {'schema':'ttm.t5.native.tcptable.dual.v1','port':port,
            'rows':ipv4+ipv6,'families_queried':['IPv4','IPv6']}
