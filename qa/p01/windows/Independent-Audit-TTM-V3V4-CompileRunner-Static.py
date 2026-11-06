#!/usr/bin/env python3
"""Independent static QA of TTM P01 L1 V3/V4 compile-only PowerShell runner.
Source text inspection + intentional negative mutations ONLY. No exec, network,
PowerShell, csc, service change, filesystem write or scientific jobs.
PowerShell 5.1 native Parser.ParseFile is a SEPARATE mandatory gate.
"""
import argparse
import hashlib
import json
from pathlib import Path


def sha(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def evaluate(s: str) -> dict[str, bool]:
    check = {}
    def add(k: str, test: bool) -> None:
        check[k] = bool(test)

    add("powerShell51_requires", s.count("#requires -Version 5.1") == 1)
    add("explicit_optin", "param([switch]$CompileOnce)" in s)
    add("readonly_default", "if(-not $CompileOnce){" in s)
    add("readonly_verdict", "PREFLIGHT_PASS_NO_COMPILATION" in s)
    add("authorization_warning", "separate operator authorization" in s)
    add("frozen_root", "D:\\WORK\\RESEARCH\\TokenToModel-Lab" in s)
    add("frozen_head", "f2e333df2f9ca24a8e483507c3cfc386ad9c76f0" in s)
    add("frozen_branch", "implementation/p01-i0a-s-f0-static-20261106" in s)
    add("frozen_origin", "https://github.com/minhtri22/TokenToModel-Lab.git" in s)
    add("original_read_only", "GitRead @('rev-parse','HEAD')" in s)
    add("reparse_reject", "REPARSE_POINT" in s)
    add("scm_stopped_pid0", "SCM_CHANGED_OR_NOT_STOPPED_PID0" in s)
    add("scm_manual_localservice", "NT AUTHORITY\\LocalService" in s and
        "$svc.StartMode -ne 'Manual'" in s)
    add("scm_v2_sha", "a9dbc179b668559a0a5d6fe0bf979c9a6339d4977cb47f6a0c30d66fb289106a" in s)
    add("qa_receipt_sha", "619bd23aee3d901418a41e638597718929baed6caeb7e5db5e5078fd96cbed3c" in s)
    add("qa_receipt_commit", "3860d08601ee77402d44926776f69208da103157" in s)
    add("qa_receipt_blob", "c5d1ae4eb6a154161638710d8c4ec2b3f82c82d1" in s)
    add("qa_marker_pin", "515fc6c37370cb0080af05b87f837bff2e4f564f693cf49d7c1e5840d1f44e38" in s)
    add("old_markers_all4", all(x in s for x in (
        "29f1a8836da83d34d233b165698dc20bb2fb6022941a93b840ae528b2ae4a8d1",
        "f0d895e68c30b8c3845336ea8aee40d2e1ca84f96816906a952ae70ad81587c7",
        "f1ca3d0899fe6637a512e44dd073b449d4805ca8f8a8afa1e8a3989599143502",
        "59823e4cd684195692dc5988a4af3eb484b05c4f7e5597e34140c1e21ac01dc9",
    )))
    add("all_source_pins", all(x in s for x in (
        "8bbcb2bb7b9f0d69e20ebd8ac04fa6216b20c986207b4215617bac8ffb782ca4",
        "0e81e2a2ae9914daff20956d3d85f54b98dfa921ddd1764c771b8e9bae5cef04",
        "f75ce6ecf16fc5a3d00807dc958f4421027578f1aab7a587144c5ca2ab32642d",
    )))
    add("QA_46_9", all(x in s for x in (
        "static_checks_total -ne 46", "static_checks_passed -ne 46",
        "negative_fixture_total -ne 9", "negative_fixture_passed -ne 9"
    )))
    add("QA_checker_exit", "$qa.python_checker_exit -ne 0" in s)
    add("QA_JSON_readback", "GITHUB_QA_BLOB_MISMATCH" in s and
        "GITHUB_QA_BYTES_MISMATCH" in s)
    add("source_receipt_commit", "782f101f001973f8c23f23b22ae2b0896232d722" in s)
    add("csc_SHA", "eca02e6b15cde93009a59a3d129d5a77fb5008f2e1cf62cf573b6737c747ecc3" in s)
    add("compiler_only_new_exe", "TTMP01Broker.attestationV3.exe" in s)
    add("compiler_only_new_dll", "TTMWorkerNativeProbeV4.dll" in s)
    add("no_clobber", "OUTPUT_OR_MARKER_ALREADY_EXISTS" in s)
    add("RAM_D_guard", "RESOURCE_GUARD" in s and "2147483648" in s and
        "2097152" in s)
    add("atomic_compile_marker", s.count("[IO.FileMode]::CreateNew") == 1)
    add("marker_before_compiler", s.find("[IO.FileMode]::CreateNew") <
        s.find("RunCompiler 'BROKER_V3'"))
    add("broker_target_exe", "'/target:exe'" in s)
    add("worker_target_library", "'/target:library'" in s)
    add("only_2_compile_calls", s.count("RunCompiler 'BROKER_V3'") == 1 and
        s.count("RunCompiler 'WORKER_V4'") == 1)
    add("stop_on_broker_fail", "Block ('COMPILER_FAILED_'+$name)" in s)
    add("local_compiler_temp", "$env:TEMP=$temp;$env:TMP=$temp" in s and
        "$env:TEMP=$oldTemp;$env:TMP=$oldTmp" in s)
    add("output_sha_size", "sha256=(Hash $destination)" in s and
        "size=(Get-Item -LiteralPath $destination).Length" in s)
    add("bounded_csc_diagnostics", "$diagnostics.Substring(0,16384)" in s)
    add("sha_receipt_readback", "GITHUB_SHA256_MISMATCH" in s)
    add("evidence_fail_closed", "BLOCK_EVIDENCE_PUBLICATION_NOT_QUALIFIED" in s and
        "$CompileOnce -and $evidenceOk" in s)
    add("no_service_mutations", all(x not in s for x in (
        "Start-Service", "Stop-Service", "Set-Service", "sc.exe start",
        "sc.exe stop", "sc.exe config", "taskkill", "Stop-Process")))
    add("no_acl_user_mutations", all(x not in s for x in (
        "Set-Acl", "icacls ", "New-LocalUser", "Set-LocalUser")))
    add("no_marker_cleanup", "Remove-Item" not in s)
    add("no_science", "L1_grouped_QA='NOT_AUTHORIZED'" in s and
        "W01_W12='NOT_EXECUTED'" in s and "P02='NOT_OPENED'" in s)
    add("only_one_terminal_exit", s.count("exit 3") == 1)
    return check


def mutate_cases(source: str) -> dict[str, str]:
    return {
        "strip_explicit_switch": source.replace("param([switch]$CompileOnce)", "param()", 1),
        "drop_frozen_HEAD": source.replace("f2e333df2f9ca24a8e483507c3cfc386ad9c76f0",
                                           "0" * 40, 1),
        "drop_SCM_stop_guard": source.replace("SCM_CHANGED_OR_NOT_STOPPED_PID0",
                                              "ANY_SCM_STATE_ALLOWED", 1),
        "accept_unqualified_QA": source.replace("static_checks_total -ne 46",
                                                 "static_checks_total -ne 0", 1),
        "drop_atomic_marker": source.replace("[IO.FileMode]::CreateNew",
                                             "[IO.FileMode]::OpenOrCreate", 1),
        "overwrite_V2_exe": source.replace("TTMP01Broker.attestationV3.exe",
                                            "TTMP01Broker.attestationV2.exe", 1),
        "drop_QA_readback": source.replace("GITHUB_QA_BYTES_MISMATCH",
                                            "IGNORE_GITHUB_QA_SHA", 1),
        "drop_evidence_failclosed": source.replace(
            "BLOCK_EVIDENCE_PUBLICATION_NOT_QUALIFIED", "IGNORE_PUBLICATION", 1),
        "drop_worker_compile": source.replace("RunCompiler 'WORKER_V4'",
                                                "NoCompile 'WORKER_V4'", 1),
        "allow_force_kill": source + "\nStop-Process -Id 26200\n",
        "allow_cleanup": source + "\nRemove-Item $marker\n",
        "allow_service_start": source + "\nStart-Service TTMP01Broker\n",
    }


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--runner", type=Path, required=True)
    args = ap.parse_args()
    data = args.runner.read_bytes()
    source = data.decode("utf-8-sig")
    tests = evaluate(source)
    negative = {}
    for name, mutant in mutate_cases(source).items():
        negative[name] = not all(evaluate(mutant).values())
    out = {
        "schema": "ttm.p01.l1.compile_runner_independent_source_static.v1",
        "runner_sha256": sha(data),
        "positive_total": len(tests),
        "positive_pass": sum(tests.values()),
        "failed": [k for k, v in tests.items() if not v],
        "negative_total": len(negative),
        "negative_rejected": sum(negative.values()),
        "negative_fail": [k for k, v in negative.items() if not v],
        "powershell51_native_parse": "NOT_EXECUTED_BY_PYTHON_CHECKER",
        "compiler_invocation": "NOT_EXECUTED",
        "verdict": "PASS_SOURCE_ONLY_NO_NATIVE_PARSE" if
            all(tests.values()) and all(negative.values()) else "FAIL_SOURCE_STATIC",
    }
    print(json.dumps(out, indent=2))
    return 0 if out["verdict"].startswith("PASS_") else 3


if __name__ == "__main__":
    raise SystemExit(main())
