#!/usr/bin/env python3
"""TTM P01 L1 S1: independent static check of host, runner, watchdog source.
Reads only text and hashes. No native compilation/run, SCM action, marker, file writes.
"""
import argparse
import hashlib
import json
import re
from pathlib import Path

def inspect(host, runner, engine):
    checks = {}
    def ck(name, value):
        checks[name] = bool(value)
    def at(src, *anchors):
        p = [src.find(a) for a in anchors]
        return all(v >= 0 for v in p) and p == sorted(p)
    ck("host_one_main", host.count("public static int Main(string[] args)") == 1)
    ck("host_limited_8_args", "args.Length==8" in host)
    ck("host_windows_x64", "Environment.Is64BitProcess" in host)
    ck("host_fixed_root", '@"D:\\WORK\\RESEARCH\\TokenToModel-Lab"' in host)
    ck("host_project_path", "full.StartsWith(Root+Path.DirectorySeparatorChar" in host)
    ck("host_reparse_guard", "BLOCK_PARENT_REPARSE" in host and "BLOCK_FILE_MISSING_OR_REPARSE" in host)
    ck("host_permit_hash", 'Pinned(permitFile,args[4])' in host)
    ck("host_marker_hash", 'Pinned(markerFile,args[6])' in host)
    ck("host_authorized_decision", "p.Decision==Decision" in host and
       'const string Decision="AUTHORIZED_ONCE_EXACT_SOURCE_S1_NATIVE"' in host)
    ck("host_permit_exact_id", "p.PermitId==PermitId" in host and
       'const string PermitId="TTM_P01_L1_S1_NATIVE_COMBINED_PERMIT_20261107"' in host)
    ck("host_permit_once", "p.AllowedNativeRuns==1" in host)
    ck("host_scm_forbidden", 'p.ScmActions=="FORBIDDEN"' in host)
    ck("host_source_hashes_fields", all(x in host for x in
       ["HashShape(p.HarnessSha)", "HashShape(p.WatchdogSha)",
        "HashShape(p.HostSha)", "HashShape(p.RunnerSha)"]))
    ck("host_marker_shape", "lines.Length==6" in host and "map.ContainsKey(key)" in host)
    ck("host_marker_run_id", 'Match(m,"run_id",runId)' in host)
    ck("host_marker_permit_sha", 'Match(m,"permit_sha256",args[4])' in host)
    ck("host_marker_one_shot", 'Match(m,"one_shot_id",OneShotId)' in host)
    ck("host_exact_child", '"TTMS1IsolatedCancellationHarness.exe"' in host)
    ck("host_no_direct_spawn", "CreateProcessW(" not in host and "Process.Start(" not in host)
    ck("host_one_delegate", host.count("IsolatedJobWatchdogV2.RunAfterExternalPermit(") == 1)
    ck("host_result_exit0", 'return result.Verdict=="PASS_ISOLATED_S1_ONLY"?0:3' in host)
    ck("host_failclosed", "TTM_S1_HOST_VERDICT=BLOCK_HOST_" in host)

    ck("runner_ps51", "#requires -Version 5.1" in runner)
    ck("runner_default_preflight", "Mode='Preflight'" in runner and
       "ValidateSet('Preflight','ExecuteOnce')" in runner)
    ck("runner_explicit_permit_ref", "PERMIT_COMMIT_SHA_REQUIRED" in runner)
    ck("runner_permit_remote", "S1_NATIVE_COMBINED_PERMIT_20261107.json" in runner)
    ck("runner_authorized_decision", "AUTHORIZED_ONCE_EXACT_SOURCE_S1_NATIVE" in runner)
    ck("runner_scope", "S1_ISOLATED_COMPILE_AND_SINGLE_NATIVE_SMOKE" in runner)
    ck("runner_one_native", "[int]$p.allowed_native_runs -ne 1" in runner)
    ck("runner_source_ref_locked", "e1ff28ca2808164dfbd51a902492a0218c345c54" in runner)
    ck("runner_host_blob", "7eedfab02ab995507e36a9beee25772393dc70ab" in runner)
    ck("runner_engine_blob", "5763ca10025bb928f161a0f33fa493d436107375" in runner)
    ck("runner_harness_blob", "872c67174c6fbbcea9941fe3bfa0acee3cddfb7c" in runner)
    ck("runner_compiler_pin", "eca02e6b15cde93009a59a3d129d5a77fb5008f2e1cf62cf573b6737c747ecc3" in runner)
    ck("runner_original_head", "f2e333df2f9ca24a8e483507c3cfc386ad9c76f0" in runner)
    ck("runner_scm_before_after", runner.count("ServiceSnapshot") >= 3 and
       "SCM_CHANGED" in runner)
    ck("runner_old_markers", all(x in runner for x in
       ["d39f4cd82c48c0401d48089c961f353663955671135c1e76ede06334b0b0f877",
        "506425d4fcd9e82fc0aa2d6c0056e0dda69f03a7ebbf270e43c97d3ddb2215d0",
        "c923fa283a3737bcdb2dcefed2c384899187cee532c8d580a589e0c7fda7d4ea"]))
    ck("runner_v3_receipt_reused", "V3_QA_RECEIPT_CONTRACT" in runner and
       "PASS_REUSED_NO_RERUN" in runner)
    ck("runner_no_replay", "NATIVE_MARKER_ALREADY_USED_NO_REPLAY" in runner)
    ck("runner_create_new_once", runner.count("[IO.FileMode]::CreateNew") == 1)
    ck("runner_marker_before_compiler", at(runner, "[IO.FileMode]::CreateNew",
       "Compile 'S1'"))
    ck("runner_exact_two_compiles", runner.count("Compile 'S1'") == 1 and
       runner.count("Compile 'HOST'") == 1)
    ck("runner_compiler_failure_preserved", at(runner,
       "$receipt.compile+=@($c1)", "Fail 'COMPILER_S1_FAILED'") and
       at(runner, "$receipt.compile+=@($c2)", "Fail 'COMPILER_HOST_FAILED'"))
    ck("runner_single_host_start", runner.count("Start-Process @sp") == 1)
    ck("runner_host_outer_timeout", "WaitForExit(30000)" in runner and
       "WaitForExit(3000)" in runner)
    ck("runner_host_own_kill", "$owned.Kill()" in runner and
       "Stop-Process" not in runner and "taskkill" not in runner)
    ck("runner_host_exit0",
       bool(re.search(r"(?m)^\s*TTM_S1_HOST_EXIT='0'\s*$", runner)) and
       "foreach($key in $fixed.Keys)" in runner and
       "$hostFields[$key] -cne $fixed[$key]" in runner and
       "Fail 'HOST_FIELD_CONTRACT'" in runner)
    ck("runner_child_hash_checked_independently",
       "HOST_CHILD_STDOUT_SHA256_NOT_EXPECTED" in runner and
       "$expectedOutputs" in runner)
    ck("runner_no_early_PASS", "LOCAL_S1_PASS_PENDING_GITHUB_READBACK" in runner and
       "$receipt.verdict='PASS_ISOLATED_S1_NATIVE_ONLY'" not in runner)
    ck("runner_fail_receipt", "if($markerCreated)" in runner and
       "New-Item -ItemType Directory -Path $dir -Force" in runner)
    ck("runner_github_readback", "GITHUB_SHA_READBACK" in runner and
       "if($passed -and $uploaded)" in runner)
    ck("runner_no_cleanup", "Remove-Item" not in runner)
    ck("runner_no_scm_mutation", all(x not in runner for x in
       ["Start-Service", "Stop-Service", "Set-Service", "sc.exe start", "sc.exe stop"]))
    ck("runner_no_F0", "science_execution='NOT_EXECUTED'" in runner)

    ck("engine_no_main", "public static int Main(" not in engine)
    ck("engine_job_list_creation", "PROC_THREAD_ATTRIBUTE_JOB_LIST = 0x0002000D" in engine and
       at(engine, "new IntPtr(PROC_THREAD_ATTRIBUTE_JOB_LIST)",
          "CreateProcessW(binaryPath, cmd"))
    ck("engine_member_checked_before_resume",
       at(engine, "CreateProcessW(binaryPath, cmd",
          "IsProcessInJob(child.hProcess, job, out insideJob) && insideJob",
          "ResumeThread(child.hThread)"))
    ck("engine_job_kill_on_close", "JOB_OBJECT_LIMIT_KILL_ON_JOB_CLOSE | JOB_OBJECT_LIMIT_ACTIVE_PROCESS" in engine)
    ck("engine_one_process", "ActiveProcessLimit = 1" in engine)
    ck("engine_memory_job_limit", "JOB_MEMORY_MAX_BYTES = 256 * 1024 * 1024" in engine)
    ck("engine_binary_locked", "FileShare.Read);" in engine and
       "LockBinaryAndCheck(binaryPath, exactBinarySha256)" in engine)
    ck("engine_pipe_capture", "new MemoryStream()" in engine and
       "Interlocked.Exchange(ref capture.OverflowFlag, 1)" in engine)
    ck("engine_timeout", "TIMEOUT_MS = 15000" in engine and
       "CONFIRM_MS = 3000" in engine)
    ck("engine_x64_abi_guard", "AssertMarshalLayoutsX64()" in engine and
       "Marshal.SizeOf(typeof(STARTUPINFOEX)) == 112" in engine)
    ck("engine_strict_output", "lines.Length == 3" in engine and
       "codeIsZero(result.ExitCode)" in engine and
       "stderr.SeenBytes == 0" in engine)
    ck("engine_no_scm", "Start-Service" not in engine and "ServiceController" not in engine)
    return checks

def negative_mutants(host, runner, engine):
    def change(src, before, after):
        if src.count(before) != 1:
            raise ValueError("nonunique anchor: "+before)
        return src.replace(before, after, 1)
    return {
       "host_forged_decision":(change(host, 'p.Decision==Decision',
                                     'p.Decision=="ANY"'),runner,engine),
       "host_permit_bypass":(change(host,'Pinned(permitFile,args[4])',
                                    'File.ReadAllBytes(permitFile)'),runner,engine),
       "host_marker_bypass":(change(host,'Pinned(markerFile,args[6])',
                                    'File.ReadAllBytes(markerFile)'),runner,engine),
       "host_unbounded_runs":(change(host,'p.AllowedNativeRuns==1',
                                     'p.AllowedNativeRuns>=1'),runner,engine),
       "host_marker_replay":(change(host,'Match(m,"run_id",runId)',
                                    'Need(true,"SKIP")'),runner,engine),
       "host_spawn_api":(host+"\nCreateProcessW();",runner,engine),
       "host_ignore_child_exit":(change(host,
                                    'return result.Verdict=="PASS_ISOLATED_S1_ONLY"?0:3',
                                    'return 0;'),runner,engine),
       "runner_default_execute":(host,change(runner,"Mode='Preflight'",
                                              "Mode='ExecuteOnce'"),engine),
       "runner_fake_permit":(host,change(runner,
                 "AUTHORIZED_ONCE_EXACT_SOURCE_S1_NATIVE","AUTHORIZED_ALWAYS"),engine),
       "runner_no_marker_atomic":(host,change(runner,
                 "[IO.FileMode]::CreateNew","[IO.FileMode]::OpenOrCreate"),engine),
       "runner_skip_markers":(host,change(runner,
                 "NATIVE_MARKER_ALREADY_USED_NO_REPLAY","ALLOW_REPLAY"),engine),
       "runner_compile_before_marker":(host,change(runner,
                 "Compile 'S1'","Compile_S1_Without_Bound"),engine),
       "runner_second_host":(host,runner+"\nStart-Process @sp\n",engine),
       "runner_remove_timeout":(host,change(runner,
                 "WaitForExit(30000)","WaitForExit()"),engine),
       "runner_skip_stdout_sha":(host,change(runner,
                 "HOST_CHILD_STDOUT_SHA256_NOT_EXPECTED","SHA_ACCEPTED_WITHOUT_PROOF"),engine),
       "runner_early_pass":(host,change(runner,
                 "LOCAL_S1_PASS_PENDING_GITHUB_READBACK","PASS_ISOLATED_S1_NATIVE_ONLY"),engine),
       "runner_skip_readback":(host,change(runner,
                 "GITHUB_SHA_READBACK","IGNORE_GH_READBACK"),engine),
       "runner_scm_start":(host,runner+"\nStart-Service TTMP01Broker\n",engine),
       "runner_delete_marker":(host,runner+"\nRemove-Item $marker\n",engine),
       "engine_no_job":(host,runner,change(engine,
                 "PROC_THREAD_ATTRIBUTE_JOB_LIST = 0x0002000D",
                 "PROC_THREAD_ATTRIBUTE_JOB_LIST = 0x0002000E")),
       "engine_no_output_cap":(host,runner,change(engine,
                 "Interlocked.Exchange(ref capture.OverflowFlag, 1)",
                 "capture.OverflowFlag=0")),
       "engine_remove_timeout":(host,runner,change(engine,
                 "TIMEOUT_MS = 15000","TIMEOUT_MS = 99999999")),
    }


MUTANT_EXPECTED_FAILURES = {
  "host_forged_decision": [
    "host_authorized_decision"
  ],
  "host_permit_bypass": [
    "host_permit_hash"
  ],
  "host_marker_bypass": [
    "host_marker_hash"
  ],
  "host_unbounded_runs": [
    "host_permit_once"
  ],
  "host_marker_replay": [
    "host_marker_run_id"
  ],
  "host_spawn_api": [
    "host_no_direct_spawn"
  ],
  "host_ignore_child_exit": [
    "host_result_exit0"
  ],
  "runner_default_execute": [
    "runner_default_preflight"
  ],
  "runner_fake_permit": [
    "runner_authorized_decision"
  ],
  "runner_no_marker_atomic": [
    "runner_create_new_once",
    "runner_marker_before_compiler"
  ],
  "runner_skip_markers": [
    "runner_no_replay"
  ],
  "runner_compile_before_marker": [
    "runner_marker_before_compiler",
    "runner_exact_two_compiles"
  ],
  "runner_second_host": [
    "runner_single_host_start"
  ],
  "runner_remove_timeout": [
    "runner_host_outer_timeout"
  ],
  "runner_skip_stdout_sha": [
    "runner_child_hash_checked_independently"
  ],
  "runner_early_pass": [
    "runner_no_early_PASS"
  ],
  "runner_skip_readback": [
    "runner_github_readback"
  ],
  "runner_scm_start": [
    "runner_no_scm_mutation"
  ],
  "runner_delete_marker": [
    "runner_no_cleanup"
  ],
  "engine_no_job": [
    "engine_job_list_creation"
  ],
  "engine_no_output_cap": [
    "engine_pipe_capture"
  ],
  "engine_remove_timeout": [
    "engine_timeout"
  ]
}

def main():
    p=argparse.ArgumentParser()
    for key in ("host","runner","engine"): p.add_argument("--"+key,required=True,type=Path)
    for key in ("host_sha256","runner_sha256","engine_sha256"):
        p.add_argument("--"+key.replace("_","-"),required=True)
    a=p.parse_args()
    bs={k:getattr(a,k).read_bytes() for k in ("host","runner","engine")}
    text={k:v.decode("utf-8-sig") for k,v in bs.items()}
    hashes={k:hashlib.sha256(v).hexdigest() for k,v in bs.items()}
    pins=all(hashes[k]==getattr(a,k+"_sha256") for k in bs)
    checks=inspect(text["host"],text["runner"],text["engine"])
    rejected,detail,errors={},{},{}
    baseline_clean=(len(checks)==66 and all(checks.values()))
    try: variants=negative_mutants(text["host"],text["runner"],text["engine"])
    except Exception as ex:
        variants={};errors["mutant_builder"]=type(ex).__name__
    if set(variants)!=set(MUTANT_EXPECTED_FAILURES):
        errors["mutant_inventory"]="EXPECTED_EXACT_22_CASES"
    for key,(h,r,e) in variants.items():
        try:
            failures=[name for name,ok in inspect(h,r,e).items() if not ok]
            expected=set(MUTANT_EXPECTED_FAILURES.get(key,[]))
            # The V1 bug counted all mutants as rejected because an unrelated
            # baseline predicate failed. A mutant now passes only after clean
            # baseline, and only if its own expected predicates are broken.
            rejected[key]=(baseline_clean and (h,r,e)!=(text["host"],text["runner"],text["engine"])
                           and bool(expected) and set(failures)==expected)
            detail[key]=failures
        except Exception as ex:
            rejected[key]=False;errors[key]=type(ex).__name__;detail[key]=["CHECKER_EXCEPTION"]
    passed=pins and baseline_clean and len(rejected)==22 and all(rejected.values()) and not errors
    print(json.dumps({"schema":"ttm.p01.l1.s1.host_runner_integrated_source_QA.v2",
        "hashes":hashes,"hashes_pinned":pins,
        "positive_passed":sum(checks.values()),"positive_total":len(checks),
        "positive_failed":[k for k,v in checks.items() if not v],
        "baseline_clean_before_mutations":baseline_clean,
        "mutant_target_isolation_required":True,
        "negative_rejected":sum(rejected.values()),"negative_total":len(rejected),
        "negative_failed":[k for k,v in rejected.items() if not v],
        "negative_failed_predicates":detail,"checker_errors":errors,
        "native_compilation":"NOT_EXECUTED","native_S1":"NOT_EXECUTED",
        "SCM_action":"NONE","verdict":"PASS_SOURCE_ONLY" if passed else "FAIL_SOURCE_ONLY"
        },indent=2,sort_keys=True))
    return 0 if passed else 3

if __name__=="__main__":raise SystemExit(main())
