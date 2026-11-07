#!/usr/bin/env python3
"""Independent SOURCE-ONLY S1 cancellation harness audit.
Does not compile/execute C#, import target code, touch SCM or write files.
All negative fixtures mutate an in-memory source string.
"""
import argparse
import hashlib
import json
import re
from pathlib import Path


def structural_scan(src: str) -> bool:
    """Lexical bracket check outside C# comments and simple quoted literals."""
    stack = []
    pairs = {")": "(", "]": "[", "}": "{"}
    i = 0
    state = "code"
    while i < len(src):
        c = src[i]
        n = src[i + 1] if i + 1 < len(src) else ""
        if state == "line":
            if c == "\n":
                state = "code"
        elif state == "block":
            if c == "*" and n == "/":
                state = "code"
                i += 1
        elif state in ("string", "char"):
            if c == "\\":
                i += 1
            elif c == ('"' if state == "string" else "'"):
                state = "code"
        elif c == "/" and n == "/":
            state = "line"
            i += 1
        elif c == "/" and n == "*":
            state = "block"
            i += 1
        elif c == '"':
            state = "string"
        elif c == "'":
            state = "char"
        elif c in "([{":
            stack.append(c)
        elif c in ")]}":
            if not stack or stack.pop() != pairs[c]:
                return False
        i += 1
    return not stack and state in ("code", "line")


def code_without_comments(src: str) -> str:
    # For this purposely simple C# harness, reject verbatim/interpolated strings.
    # Only strip comments, preserving string literals and line endings.
    if '@"' in src or '$"' in src:
        return ""
    out = []
    i = 0
    state = "code"
    while i < len(src):
        c = src[i]
        n = src[i + 1] if i + 1 < len(src) else ""
        if state == "line":
            if c == "\n":
                out.append("\n")
                state = "code"
            else:
                out.append(" ")
        elif state == "block":
            if c == "*" and n == "/":
                out.extend("  ")
                i += 1
                state = "code"
            else:
                out.append("\n" if c == "\n" else " ")
        elif state == "string" or state == "char":
            out.append(c)
            if c == "\\" and i + 1 < len(src):
                i += 1
                out.append(src[i])
            elif c == ('"' if state == "string" else "'"):
                state = "code"
        elif c == "/" and n == "/":
            out.extend("  ")
            i += 1
            state = "line"
        elif c == "/" and n == "*":
            out.extend("  ")
            i += 1
            state = "block"
        elif c == '"':
            out.append(c)
            state = "string"
        elif c == "'":
            out.append(c)
            state = "char"
        else:
            out.append(c)
        i += 1
    return "".join(out) if state in ("code", "line") else ""


def inspect(source: str) -> dict[str, bool]:
    c = code_without_comments(source)
    tests = {}
    def check(label: str, ok: bool) -> None:
        tests[label] = bool(ok)

    check("structural_brackets", structural_scan(source))
    check("isolated_namespace", "namespace TTMP01S1 {" in c)
    check("single_main", c.count("public static int Main(string[] args)") == 1)
    check("no_runtime_arguments", "if (args.Length != 0)" in c)
    check("windows_required", "PlatformID.Win32NT" in c)
    check("unique_pipe_prefix", 'UniquePipePrefix = "TTM_P01_S1_ISOLATED_"' in c)
    check("unique_guid", 'Guid.NewGuid().ToString("N")' in c)
    check("server_name_generated", "string name = NewUniqueName();" in c and
          c.count("string name = NewUniqueName();") == 2)
    check("no_prod_pipe_name", '"TTM_P01_L1_BROKER_V1"' not in c)
    check("protected_dacl", "security.SetAccessRuleProtection(true, false)" in c)
    check("current_user_only", "identity.User, PipeAccessRights.FullControl" in c)
    check("no_dynamic_pipe_user_input", "NewServer(name)" in c and
          "args[0]" not in c)
    check("named_pipe_server_1_instance", "PipeDirection.InOut, 1, PipeTransmissionMode.Byte" in c)
    check("async_pipe", "PipeOptions.Asynchronous" in c)
    check("idle_accept_case", "static Outcome IdleAccept()" in c)
    check("silent_client_case", "static Outcome SilentClientRead()" in c)
    check("local_client_only", 'new NamedPipeClientStream(\n          ".", name' in c)
    check("no_client_payload", "client.Write(" not in c and "client.Flush(" not in c)
    check("accept_begin_twice", c.count("BeginWaitForConnection(null, null)") == 2)
    check("read_begin_once", c.count("BeginRead(buffer, 0, buffer.Length, null, null)") == 1)
    check("accept_end_once_per_case", c.count("EndWaitForConnection(") == 2)
    check("read_end_once", c.count("EndRead(ar)") == 1)
    check("cancel_dll", '[DllImport("kernel32.dll", SetLastError = true)]' in c)
    check("cancel_invocation_once", c.count("CancelIoEx(server.SafePipeHandle, IntPtr.Zero)") == 1)
    check("completion_bounded_4000", "CompletionTimeoutMs = 4000" in c and
          "pending.AsyncWaitHandle.WaitOne(CompletionTimeoutMs)" in c)
    check("connect_bounded_1500", "ConnectTimeoutMs = 1500" in c and
          "client.Connect(ConnectTimeoutMs)" in c)
    check("accept_complete_bounded", "accept.AsyncWaitHandle.WaitOne(ConnectTimeoutMs)" in c)
    check("cancel_request_not_pass", "BLOCK_CANCEL_REQUEST_" in c)
    check("not_found_race_handled", "error != ErrorNotFound" in c and
          "ErrorNotFound = 1168" in c)
    check("operation_aborted_995", "ErrorOperationAborted = 995" in c and
          "win32 == ErrorOperationAborted" in c)
    # Missing anchors in negative mutants are expected rejects, not exceptions.
    wait_anchor = "pending.AsyncWaitHandle.WaitOne(CompletionTimeoutMs)"
    end_anchor = "end(pending)"
    check("end_only_after_wait",
          wait_anchor in c and end_anchor in c and
          c.find(wait_anchor) < c.find(end_anchor))
    check("timeout_blocks", "BLOCK_CANCEL_COMPLETION_TIMEOUT" in c)
    check("normal_completion_blocks", "BLOCK_END_COMPLETED_NORMALLY" in c)
    check("uncompleted_not_disposed", c.count("pending == null || pending.IsCompleted") == 2 and
          "if (server != null && (pending == null || pending.IsCompleted))" in c and
          "read == null || read.IsCompleted" in c and
          "accept == null || accept.IsCompleted" in c)
    check("both_cases_mandatory", "if (!idle.Passed)" in c and
          "(silent.Passed ? 0 : 3)" in c)
    check("both_cases_actually_invoked",
          c.count("Outcome idle = IdleAccept();") == 1 and
          c.count("Outcome silent = SilentClientRead();") == 1)
    check("no_side_effect_api", not re.search(
        r"\b(?:File\.(?:Write|Append|Delete|Move)|Directory\.(?:Create|Delete)|"
        r"Process\.Start|Registry|ServiceController|ServiceBase|LogonUser|"
        r"ImpersonateLoggedOnUser|RevertToSelf|Environment\.Exit|"
        r"SetAccessControl|Thread\.Abort)\b", c))
    check("no_ps_or_scm", not re.search(
        r"(?:sc\.exe|powershell\.exe|Start-Service|Stop-Service|TTMP01Broker\.exe|"
        r"TTMP01Broker\.attestationV3\.exe|TTMWorkerNativeProbeV4\.dll)", c, re.I))
    check("no_unbounded_wait", "WaitOne()" not in c and "Thread.Sleep(" not in c)
    check("no_test_artifact_write", "FileStream(" not in c and
          "File.WriteAllText" not in c and "File.WriteAllBytes" not in c)
    check("no_test_result_file", "Console.WriteLine(" in c and
          '"TTM_S1_VERDICT=' in c)
    return tests


def replace_once(s: str, before: str, after: str) -> str:
    if s.count(before) != 1:
        raise ValueError(f"mutation anchor must be unique: {before}")
    return s.replace(before, after, 1)


def mutation_fixtures(src: str) -> dict[str, str]:
    return {
        "drop_guid": replace_once(src, 'Guid.NewGuid().ToString("N")', '"fixed"'),
        "use_production_pipe": replace_once(
            src, '"TTM_P01_S1_ISOLATED_"', '"TTM_P01_L1_BROKER_V1"'),
        "drop_protected_dacl": replace_once(
            src, "security.SetAccessRuleProtection(true, false)",
            "security.SetAccessRuleProtection(false, true)"),
        "drop_current_sid": replace_once(
            src, "identity.User, PipeAccessRights.FullControl",
            "new SecurityIdentifier(\"S-1-1-0\"), PipeAccessRights.FullControl"),
        "allow_args": replace_once(src, "if (args.Length != 0)", "if (args.Length < 0)"),
        "sync_pipe": replace_once(
            src, "PipeOptions.Asynchronous, 512, 512, security",
            "PipeOptions.None, 512, 512, security"),
        "remove_cancel": replace_once(
            src, "CancelIoEx(server.SafePipeHandle, IntPtr.Zero)",
            "AlwaysTrue(server.SafePipeHandle)"),
        "remove_abort_proof": replace_once(
            src, "win32 == ErrorOperationAborted", "win32 != ErrorOperationAborted"),
        "accept_normal_completion": replace_once(
            src, '"BLOCK_END_COMPLETED_NORMALLY"', '"PASS_COMPLETED_ABORTED"'),
        "remove_completion_bound": replace_once(
            src, "pending.AsyncWaitHandle.WaitOne(CompletionTimeoutMs)",
            "pending.AsyncWaitHandle.WaitOne()"),
        "ignore_timeout": replace_once(
            src, '"BLOCK_CANCEL_COMPLETION_TIMEOUT"', '"PASS_COMPLETED_ABORTED"'),
        "dispose_before_complete": replace_once(
            src, "if (server != null && (pending == null || pending.IsCompleted)) server.Dispose();",
            "if (server != null) server.Dispose();"),
        "skip_silent_case": replace_once(
            src, "Outcome silent = SilentClientRead();",
            "Outcome silent = new Outcome(\"SILENT_READ\", \"PASS_COMPLETED_ABORTED\");"),
        "inject_scm_start": src + "\n// fixture\nStart-Service TTMP01Broker\n",
        "inject_file_write": src + '\nFile.WriteAllText("broker_ledger.sqlite3","bad");\n',
        "inject_client_payload": src + "\nclient.Write(buffer, 0, 1);\n",
    }


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--source", required=True, type=Path)
    parser.add_argument("--expected-sha256", default="")
    args = parser.parse_args()
    data = args.source.read_bytes()
    text = data.decode("utf-8-sig")
    positive = inspect(text)
    negatives = {}
    negative_inspection_errors = {}
    for name, mutant in mutation_fixtures(text).items():
        try:
            negatives[name] = not all(inspect(mutant).values())
        except Exception as exc:
            # A checker crash must FAIL the QA, never masquerade as a
            # negative fixture being correctly rejected.
            negatives[name] = False
            negative_inspection_errors[name] = type(exc).__name__
    digest = hashlib.sha256(data).hexdigest()
    sha_match = not args.expected_sha256 or args.expected_sha256 == digest
    result = {
        "schema": "ttm.p01.l1.s1.isolated_cancel_independent_static.v2",
        "source_sha256": digest,
        "sha256_pinned": sha_match,
        "positive_passed": sum(positive.values()),
        "positive_total": len(positive),
        "positive_failed": [name for name, ok in positive.items() if not ok],
        "negative_rejected": sum(negatives.values()),
        "negative_total": len(negatives),
        "negative_failed": [name for name, ok in negatives.items() if not ok],
        "negative_inspection_errors": negative_inspection_errors,
        "native_csharp_compile": "NOT_EXECUTED",
        "native_harness_run": "NOT_EXECUTED",
        "SCM_action": "NONE",
        "verdict": "PASS_SOURCE_STATIC_NO_NATIVE" if
                   sha_match and all(positive.values()) and all(negatives.values())
                   else "FAIL_SOURCE_STATIC",
    }
    print(json.dumps(result, indent=2, sort_keys=True))
    return 0 if result["verdict"].startswith("PASS") else 3


if __name__ == "__main__":
    raise SystemExit(main())
