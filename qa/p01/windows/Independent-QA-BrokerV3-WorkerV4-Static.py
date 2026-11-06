#!/usr/bin/env python3
"""TTM P01 L1 independent, source-only V3/V4 static QA.

No service invocation, writes, network, imports of target source or scientific seeds.
The checker reads only the two named C# text files. Output is JSON on stdout.
Source checks do not establish .NET Framework compilability or runtime behavior.
"""
import argparse
import hashlib
import json
import pathlib
import re
import sys

def sha256(b: bytes) -> str:
    return hashlib.sha256(b).hexdigest()

def structural_scan(text: str) -> tuple[bool, str]:
    # Lexically ignore C# quoted literals and both comment forms when checking
    # brace/paren/bracket matching. No C# language-grammar claim.
    pairs = {"}": "{", ")": "(", "]": "["}
    stack: list[tuple[str, int]] = []
    state = "code"
    index = 0
    length = len(text)
    while index < length:
        char = text[index]
        nxt = text[index + 1] if index + 1 < length else ""
        if state == "line":
            if char == "\n":
                state = "code"
        elif state == "block":
            if char == "*" and nxt == "/":
                state = "code"
                index += 1
        elif state == "string":
            if char == "\\":
                index += 1
            elif char == '"':
                state = "code"
        elif state == "char":
            if char == "\\":
                index += 1
            elif char == "'":
                state = "code"
        elif state == "verbatim":
            if char == '"' and nxt == '"':
                index += 1
            elif char == '"':
                state = "code"
        else:
            if char == "/" and nxt == "/":
                state = "line"
                index += 1
            elif char == "/" and nxt == "*":
                state = "block"
                index += 1
            elif char == "@" and nxt == '"':
                state = "verbatim"
                index += 1
            elif char == '"':
                state = "string"
            elif char == "'":
                state = "char"
            elif char in "{([":
                stack.append((char, index))
            elif char in "})]":
                if not stack or stack[-1][0] != pairs[char]:
                    return False, f"unexpected {char} offset {index}"
                stack.pop()
        index += 1
    if state not in {"code", "line"}:
        return False, f"unterminated lexical state {state}"
    if stack:
        return False, f"unclosed {stack[-1][0]} offset {stack[-1][1]}"
    return True, "balanced_brace_paren_bracket_and_literals"

def evaluate(broker: str, worker: str) -> dict[str, bool]:
    b, w = broker, worker
    return {
        "broker_v3_class": "public sealed class BrokerAttestationServiceV3" in b,
        "broker_service_name_invariant": 'Service = "TTMP01Broker"' in b,
        "broker_pipe_name_invariant": 'PipeName = "TTM_P01_L1_BROKER_V1"' in b,
        "broker_localservice_sid_gate": 'identity.User.Value != "S-1-5-19"' in b,
        "broker_service_sid_token_gate": "TokenHasGroup(expectedService)" in b,
        "broker_explicit_protected_dacl": "SetAccessRuleProtection(true, false)" in b,
        "broker_dacl_exact_principals": all(x in b for x in
            ('new SecurityIdentifier("S-1-5-18")',
             'new SecurityIdentifier(service)',
             'new SecurityIdentifier(worker)')),
        "broker_worker_client_restricted_rights":
            'new SecurityIdentifier(worker),\n        PipeAccessRights.ReadWrite' in b,
        "broker_async_single_instance": "PipeOptions.Asynchronous" in b and
            "PipeDirection.InOut, 1," in b,
        "broker_accept_APM_balanced": b.count("pipe.BeginWaitForConnection(") == 1 and
            b.count("pipe.EndWaitForConnection(") == 1,
        "broker_read_APM_balanced": b.count("pipe.BeginRead(") == 1 and
            b.count("pipe.EndRead(") == 1,
        "broker_write_APM_balanced": b.count("pipe.BeginWrite(") == 1 and
            b.count("pipe.EndWrite(") == 1,
        "broker_overlapped_cancellation": "CancelIoEx(pipe.SafePipeHandle, IntPtr.Zero)" in b,
        "broker_cancellation_wake": "WaitHandle.WaitAny(wait)" in b and
            "stopSignal.Set()" in b,
        "broker_no_shared_active_pipe": "active.Dispose()" not in b and
            "NamedPipeServerStream active" not in b,
        "broker_service_thread_owns_disposal": "using (NamedPipeServerStream pipe" in b,
        "broker_onstop_bounded_join": "thread.Join(StopJoinMilliseconds)" in b and
            "StopJoinMilliseconds = 8000" in b,
        "broker_fail_closed_on_stop_timeout":
            "BROKER_V3_SERVER_THREAD_STOP_TIMEOUT" in b,
        "broker_read_before_impersonation": b.find("int n = ReadRequest(pipe, input)") <
            b.find("pipe.RunAsClient(") and
            b.find("int n = ReadRequest(pipe, input)") >= 0,
        "broker_peer_sid_gate": "if (peer != workerSid)" in b,
        "broker_auth_only_and_denies_operations":
            "AUTH_PEER_OK_NO_WRITE" in b and "DENY_UNSUPPORTED_OPERATION" in b and
            "DENY_PEER_SID" in b,
        "broker_no_fallback_pipe_default_dacl": b.count("new NamedPipeServerStream(") == 1 and
            "4096, 4096, acl" in b,
        "broker_no_evidence_writes": not any(x in b for x in
            ("File.WriteAll", "File.AppendAll", "FileStream(", "SqliteConnection",
             "SQLiteConnection", "git push", "sc.exe config")),
        "worker_v4_class": "public static class TTMWorkerNativeProbeV4" in w,
        "worker_token_real_logon": "LogonUser(user, domain, password, 2, 0, out token)" in w,
        "worker_identity_sid_gate": "identity.User.Value != expectedWorkerSid" in w,
        "worker_revert_token": "RevertToSelf()" in w and
            "WORKER_REVERT_TO_SELF_FAILED" in w,
        "worker_explicit_readwrite_connect": "PipeAccessRights.ReadWrite, PipeOptions.None" in w and
            "client.Connect(4000)" in w,
        "worker_no_create_instance": "PipeAccessRights.CreateNewInstance" in w and
            "BLOCK_CLIENT_RIGHTS_MASK" in w,
        "worker_DACL_on_existing_handle": "GetSecurityInfo(client.SafePipeHandle," not in w and
            "AuditConnectedPipe(client.SafePipeHandle," in w and
            "GetSecurityInfo(handle, 1u, 4u," in w,
        "worker_no_path_based_security_api": "GetFileSecurityW" not in
            re.sub(r"//[^\n]*", "", w) and "GetNamedSecurityInfo(" not in w,
        "worker_descriptor_memory_safety": all(x in w for x in
            ("GetSecurityDescriptorLength", "GetSecurityDescriptorControl",
             "Marshal.Copy(descriptor, raw", "LocalFree(descriptor)")),
        "worker_DACL_self_relative_protected": "control & 0x8000" in w and
            "control & 0x1000" in w and "control & 0x0004" in w,
        "worker_acl_three_principal_exact_masks": all(x in w for x in
            ("allowCount != 3", "PipeAccessRights.FullControl", "PipeAccessRights.ReadWrite",
             "BLOCK_BROAD_OR_UNKNOWN_PIPE_ALLOW_SID")),
        "worker_acl_no_owner_and_instance_rights": all(x in w for x in
            ("mask & 0x00000004", "mask & 0x00040000", "mask & 0x00080000")),
        "worker_separate_directory_denial": all(f"0x{x}u" in w for x in
            ("00000002", "00000004", "00000010", "00000100", "00010000",
             "00040000", "00080000")) and "foreach (uint right in forbidden)" in w,
        "worker_ledger_existing_write_denial": "FileGenericWrite" in w and
            "OpenExisting, 0u" in w and "BLOCK_WORKER_CAN_WRITE_LEDGER" in w,
        "worker_no_secret_or_descriptor_output": "return " + '"PASS_HANDLE_PIPE_DACL_EXACT_SHA256_" + Hex(raw)' in w and
            "RawSecurityDescriptor(raw, 0)" in w,
        "worker_auth_handshake": '"AUTH_PROBE\\n"' in w and
            '"AUTH_PEER_OK_NO_WRITE\\n"' in w,
        "worker_no_write_to_files": "File.WriteAll" not in w and
            "File.AppendAll" not in w and "new FileStream(" not in w,
        "both_pipe_name_equivalent": "TTM_P01_L1_BROKER_V1" in b and
            "TTM_P01_L1_BROKER_V1" in w,
    }

def run_mutants(b: str, w: str) -> dict[str, bool]:
    # Each mutation must be recognized as a violation by the independent checker.
    alterations = {
        "broker_sync_pipe": (b.replace("PipeOptions.Asynchronous", "PipeOptions.None", 1), w),
        "broker_missing_end_wait": (b.replace("pipe.EndWaitForConnection(pending)",
                                              "/* removed end */", 1), w),
        "broker_broad_client_rights": (b.replace(
            "new SecurityIdentifier(worker),\n        PipeAccessRights.ReadWrite",
            "new SecurityIdentifier(worker),\n        PipeAccessRights.FullControl", 1), w),
        "broker_missing_impersonation": (b.replace("if (peer != workerSid)",
                                                   "if (false)", 1), w),
        "worker_name_based_dacl": (b, w.replace(
            "AuditConnectedPipe(client.SafePipeHandle,",
            "AuditConnectedPipe(null,", 1)),
        "worker_leaks_descriptor": (b, w.replace("LocalFree(descriptor)",
                                                  "/* leaked descriptor */", 1)),
        "worker_omits_one_denied_right": (b, w.replace("0x00080000u", "0x00000000u", 1)),
        "worker_accepts_weak_mask": (b, w.replace(
            "mask != (int)PipeAccessRights.ReadWrite",
            "mask == (int)PipeAccessRights.ReadWrite", 1)),
    }
    result: dict[str, bool] = {}
    for name, (mb, mw) in alterations.items():
        result[name] = not all(evaluate(mb, mw).values())
    return result

def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--broker", required=True, type=pathlib.Path)
    ap.add_argument("--worker", required=True, type=pathlib.Path)
    ap.add_argument("--output", help="optional JSON output file; not used by default",
                    type=pathlib.Path)
    args = ap.parse_args()
    b_bytes = args.broker.read_bytes()
    w_bytes = args.worker.read_bytes()
    broker = b_bytes.decode("utf-8-sig")
    worker = w_bytes.decode("utf-8-sig")
    checks = evaluate(broker, worker)
    b_structure, b_reason = structural_scan(broker)
    w_structure, w_reason = structural_scan(worker)
    checks["broker_lexical_balance"] = b_structure
    checks["worker_lexical_balance"] = w_structure
    mutants = run_mutants(broker, worker)
    passed = sum(checks.values())
    output = {
        "schema": "ttm.p01.l1.broker_v3_worker_v4_independent_static_qa.v1",
        "source": {
            "broker_sha256": sha256(b_bytes),
            "worker_sha256": sha256(w_bytes),
        },
        "static_checks_passed": passed,
        "static_checks_total": len(checks),
        "static_failures": [name for name, ok in checks.items() if not ok],
        "structural_notes": {
            "broker": b_reason,
            "worker": w_reason,
        },
        "negative_fixture_passed": sum(mutants.values()),
        "negative_fixture_total": len(mutants),
        "negative_fixture_failures": [name for name, ok in mutants.items() if not ok],
        "scm_changed": False,
        "service_started": False,
        "windows_compilation": "NOT_EXECUTED",
        "native_security": "NOT_QUALIFIED",
        "W01_W12": "NOT_EXECUTED",
        "L1_grouped_QA": "NOT_AUTHORIZED",
        "verdict": ("PASS_SOURCE_ONLY_NO_WINDOWS_NATIVE" if
                    passed == len(checks) and all(mutants.values()) else
                    "FAIL_SOURCE_ONLY_STATIC_QA"),
    }
    encoded = json.dumps(output, ensure_ascii=False, indent=2) + "\n"
    print(encoded, end="")
    if args.output is not None:
        args.output.write_text(encoded, encoding="utf-8")
    return 0 if output["verdict"].startswith("PASS_") else 3

if __name__ == "__main__":
    sys.exit(main())
