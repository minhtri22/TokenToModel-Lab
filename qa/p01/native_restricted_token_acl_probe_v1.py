"""Windows native *read-only* restricted token probe. No worker is launched.

Uses OPEN_EXISTING requests against two pre-existing directories and returns
redacted receipts. Passing these probes does NOT prove actual broker/worker
identity, effective filesystem confinement, or W10 native end-to-end.
"""
from __future__ import annotations
import argparse, ctypes, hashlib, json, os
from worker_identity_acl_win32_v1 import RestrictedWorkerIdentity, WorkerIdentityFailure

def path_hash(path: str):
    return hashlib.sha256(os.path.normcase(os.path.abspath(path)).encode("utf-8")).hexdigest()

def main():
    p=argparse.ArgumentParser()
    p.add_argument("--evidence-root",required=True)
    p.add_argument("--outside-dir",required=True)
    args=p.parse_args()
    receipt={"verdict":"BLOCK","scope":"CURRENT_USER_RESTRICTED_TOKEN_ONLY",
             "native_worker_process":False,"W10_end_to_end":False,
             "paths": [path_hash(args.evidence_root),path_hash(args.outside_dir)]}
    identity=None
    token=None
    try:
        identity=RestrictedWorkerIdentity()
        token=identity.restricted_primary_token()
        for path in (args.evidence_root,args.outside_dir):
            identity.probe_denied_directory_write(token,path)
        receipt["verdict"]="PASS_TWO_READONLY_ACCESS_DENIALS_ONLY"
        receipt["observed_winerror"] = 5
    except Exception as err:
        receipt["reason"]="NATIVE_PROBE_FAILURE"
        receipt["exception_type"]=type(err).__name__
    finally:
        if token:
            try:
                if not identity.close(ctypes.c_void_p(token)):
                    receipt["verdict"]="BLOCK"
                    receipt["reason"]="TOKEN_CLOSE_FAILED"
            except Exception:
                receipt["verdict"]="BLOCK"
                receipt["reason"]="TOKEN_CLOSE_EXCEPTION"
    print(json.dumps(receipt,sort_keys=True))
    return 0 if receipt["verdict"]=="PASS_TWO_READONLY_ACCESS_DENIALS_ONLY" else 3

if __name__=="__main__":
    raise SystemExit(main())
