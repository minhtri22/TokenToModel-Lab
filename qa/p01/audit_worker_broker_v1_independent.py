"""Read-only independent source-contract audit, NOT native Windows W01-W12."""
from __future__ import annotations
import ast
import hashlib
import json
import pathlib
import sys

ROOT=pathlib.Path(__file__).resolve().parent
PIN={
 'durable_broker_quota_v1.py':'352a59ab21c3f7f197fb95bd65f25f3d30f456ed93eabea044f962447ae52251',
 'worker_identity_acl_win32_v1.py':'15d6ef048144036b4a998f031ed67b1d6894172aee24f2ee385b44cd6073adf3',
 'atomic_handle_writer_win32_v1.py':'e5636f89ea0be005a373f808f2e3e59196e962d5bb6caf989f8c3e3fc1f557b5',
 'trusted_broker_service_v1.py':'8f9756fb6827561b8341558e08d79e16726f011124d94ad5d75d6f9d2dd01a31',
 'test_trusted_broker_protocol_v1.py':'02f40d119623665886c24e6ebf7b7091d4e2825f13f59557881d7c7eaabc4557',
}

def audit():
    contents={name:(ROOT/name).read_text(encoding='utf-8') for name in PIN}
    pins={name:hashlib.sha256((ROOT/name).read_bytes()).hexdigest()==sha for name,sha in PIN.items()}
    for name,content in contents.items():ast.parse(content,filename=name)
    w=contents['worker_identity_acl_win32_v1.py'];b=contents['trusted_broker_service_v1.py']
    a=contents['atomic_handle_writer_win32_v1.py'];q=contents['durable_broker_quota_v1.py']
    controls={
        'restricted_sid_and_write_restricted':all(x in w for x in ('RESTRICTED_CODE_SID','WRITE_RESTRICTED','IsTokenRestricted')),
        'nonmutating_acl_probe_and_restore':all(x in w for x in ('OPEN_EXISTING','ImpersonateLoggedOnUser','RevertToSelf','UNBROKERED_WRITE_ACCESS_GRANTED')),
        'broker_requires_distinct_service_sid':all(x in b for x in ('expected_broker_sid==worker_sid','current_user_sid_win32()!=expected_broker_sid')),
        'broker_authenticated_bounded_json_ipc':all(x in b for x in ('authkey=authkey','recv_bytes(maxlength=MAX_MESSAGE)','json.loads','B64_FRAME_TOO_LARGE')),
        'broker_does_not_expose_cli_worker_launch':'NO_CLI_EXECUTION_WITHOUT_PINNED_NATIVE_SUPERVISOR' in b,
        'atomic_handle_root_pinning':all(x in a for x in ('NtCreateFile','OBJ_DONT_REPARSE','FILE_OPEN_REPARSE_POINT','self.root_identity')),
        'atomic_rename_no_replace_and_readback':all(x in a for x in ('info.ReplaceIfExists=0','_rename_no_replace','READBACK_HASH_MISMATCH','FlushFileBuffers')),
        'durable_sqlite_quota_and_fail_held':all(x in q for x in ('BEGIN IMMEDIATE','FAILED_HELD','MAX_BYTES = 2 * 1024**3')),
        'no_python_pickle_ipc':'.recv(' not in b and 'pickle.loads' not in b,
    }
    unsatisfied=[
        'Windows-specific token/ACL effective access probe not executed',
        'Dedicated Windows SCM broker service SID not provisioned; distinct process identity not attested',
        'Named pipe SDDL/DACL, per-connection peer SID and secret ACL not native-qualified',
        'Evidence root/parent ACL immutability not independently proven',
        'NT atomic handle writer and quota/rename crash cases not run on Windows',
        'W01-W12 native negative QA not executed',
    ]
    return {
      'schema':'ttm.p01.l1.worker_broker_independent_static_source_audit.v1',
      'all_pins_match':all(pins.values()),'source_sha256_match':pins,
      'positive_source_contracts':controls,'all_positive_source_contracts':all(controls.values()),
      'remaining_native_security_gates':unsatisfied,
      'source_contract_verdict':'PASS_STATIC_ONLY' if all(pins.values()) and all(controls.values()) else 'FAIL_STATIC_SOURCE',
      'native_security_verdict':'NOT_QUALIFIED','W01_W12_native':'NOT_EXECUTED',
      'grouped_L1_permit':'NOT_GRANTED',
    }
if __name__=='__main__':
    result=audit()
    print(json.dumps(result,indent=2,ensure_ascii=False))
    sys.exit(0 if result['source_contract_verdict']=='PASS_STATIC_ONLY' else 2)
