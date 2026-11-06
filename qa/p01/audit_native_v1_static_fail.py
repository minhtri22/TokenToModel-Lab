"""Read-only independent AST audit for pinned V1 sources. No worker launch.

To reproduce, place byte-pinned native_win32_process_backend.py and
native_win32_handle_broker.py next to this script and run Python.
This audit detects missing controls; a zero exit is NOT a security PASS.
"""
import ast, hashlib, json, pathlib, sys
P = pathlib.Path(__file__).resolve().parent
files = [P / 'native_win32_process_backend.py', P / 'native_win32_handle_broker.py']
def methods(tree, class_name):
    for item in tree.body:
        if isinstance(item, ast.ClassDef) and item.name == class_name:
            return {n.name:n for n in item.body if isinstance(n,(ast.FunctionDef,ast.AsyncFunctionDef))}
    raise ValueError('MISSING_CLASS:'+class_name)
def call_names(fn):
    names=set()
    for n in ast.walk(fn):
        if isinstance(n,ast.Call):
            if isinstance(n.func,ast.Name): names.add(n.func.id)
            if isinstance(n.func,ast.Attribute): names.add(n.func.attr)
    return names
proc = ast.parse(files[0].read_text(encoding='utf8'))
brok = ast.parse(files[1].read_text(encoding='utf8'))
p=methods(proc,'Win32Backend'); b=methods(brok,'HandleRelativeBroker')
checks = {
 'V1_NO_ORCHESTRATED_ASSIGN_BEFORE_RESUME': not any('create_restricted_suspended' in call_names(n) and 'assign' in call_names(n) and 'resume' in call_names(n) for n in p.values()),
 'V1_NO_RESTRICTED_TOKEN_ACL_PROOF': not any('AccessCheck' in call_names(n) or 'GetEffectiveRightsFromAclW' in call_names(n) for n in p.values()),
 'V1_NO_BROKER_WORKER_PROCESS_SEPARATION': not any('CreateProcessAsUserW' in call_names(n) or 'CreateNamedPipeW' in call_names(n) for n in b.values()),
 'V1_NO_REPARSE_SAFE_ROOT_ATTESTATION': not any('GetFinalPathNameByHandleW' in call_names(n) or 'GetFileInformationByHandle' in call_names(n) for n in b.values()),
 'V1_NO_DELETE_PARTIAL_ON_WRITE_FAILURE': not any('SetFileInformationByHandle' in call_names(n) or 'DeleteFileW' in call_names(n) for n in b.values()),
 'V1_QUOTA_NOT_CROSS_PROCESS_DURABLE': '_reserved' in files[1].read_text() and 'threading.Lock()' in files[1].read_text(),
}
report = {'audit_type':'STATIC_SOURCE_ONLY','source_sha256':{f.name:hashlib.sha256(f.read_bytes()).hexdigest() for f in files},'critical_failures':checks,'all_six_confirmed':all(checks.values()),'native_windows_tests':'NOT_EXECUTED','permit':'NOT_GRANTED'}
print(json.dumps(report,indent=2))
if not all(checks.values()): sys.exit(2)
